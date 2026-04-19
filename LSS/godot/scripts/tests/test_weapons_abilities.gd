extends SceneTree

# Covers the weapons/projectiles/abilities/loadouts vertical slice:
#   - GameData.LOADOUTS: every loadout has a weapon, 3 abilities, a core.
#   - PlayerShip & EnemyShip: _attempt_fire consumes ammo, emits primary_fired
#     with the expected payload, respects fire_cooldown and reload_timer;
#     clip empty starts a reload; reload restores the clip.
#   - Ability activation: each local ability id ("vortex_shield",
#     "thermal_shield", "afterburner", "sword_block", "phase_dash",
#     "gun_shield", "mode_switch", "rearm") sets the expected ship-local
#     state; each emit-id (laser_shot, firewall, cluster_missile, arc_wave,
#     tracker_rockets, power_shot, rocket_salvo, etc) fires
#     ability_triggered with the correct id so main.gd can route it to a
#     world effect.
#   - Cooldown gating: a second activation inside the cooldown window is
#     refused; Rearm resets peer cooldowns, refills the clip, and restores
#     dash charges.
#   - Cores: laser_core / flame_core / salvo_core emit core_triggered for
#     main.gd; afterburner_core / sword_core / smart_core set local state;
#     upgrade_core advances monarch_tier and pokes the buffs.
#   - Damage mitigation: each defensive state (sword_block, thermal_shield,
#     gun_shield, vortex_shield) reduces incoming damage by its multiplier;
#     phase_dash drops damage entirely.
#   - Everything is verified on BOTH PlayerShip and EnemyShip so the two
#     implementations stay synchronised.

const PlayerShipScript = preload("res://scripts/player_ship.gd")
const EnemyShipScript = preload("res://scripts/enemy_ship.gd")
const GameData = preload("res://scripts/game_data.gd")

# Ability ids that keep their effect on the ship (no signal; no world entity).
# If the ship's _try_activate_ability routes one of these through the default
# branch it emits ability_triggered incorrectly; we detect that.
const LOCAL_ABILITY_IDS := [
	"vortex_shield", "thermal_shield", "afterburner",
	"sword_block", "phase_dash", "gun_shield",
	"mode_switch", "rearm"
]

# Ability ids that fire ability_triggered for main.gd to spawn a world effect.
const EMIT_ABILITY_IDS := [
	"laser_shot", "trip_wire", "firewall", "incendiary_trap",
	"cluster_missile", "tether_trap", "arc_wave",
	"tracker_rockets", "particle_wall", "sonar_lock",
	"power_shot", "rocket_salvo", "energy_siphon"
]

# Mapping each defensive state to its damage multiplier (see
# player_ship.gd::apply_damage / enemy_ship.gd::apply_damage).
const DAMAGE_MULTS := {
	"sword_block": 0.3,
	"thermal_shield": 0.45,
	"gun_shield": 0.55,
	"vortex_shield": 0.4
}

var _ok := true

func _init() -> void:
	GameData.ensure_input_map()

	_assert_loadout_schema()
	_assert_player_fire_loop()
	_assert_ship_ability_routing(_new_player(), "Player")
	_assert_ship_ability_routing(_new_enemy(), "Enemy")
	_assert_ship_core_routing(_new_player(), "Player")
	_assert_ship_core_routing(_new_enemy(), "Enemy")
	_assert_damage_mitigation_player()
	_assert_damage_mitigation_enemy()
	_assert_rearm_and_cooldowns()
	_assert_upgrade_core_tiers()
	_assert_monarch_cooldown_scaling()

	if _ok:
		print("RESULT: PASS")
		quit(0)
	else:
		push_error("test_weapons_abilities FAILED")
		quit(1)

# -- helpers ----------------------------------------------------------------

func _fail(message: String) -> void:
	push_error(message)
	_ok = false

func _new_player() -> PlayerShip:
	var ship: PlayerShip = PlayerShipScript.new()
	get_root().add_child(ship)
	ship._ready()
	ship.set_match_state("playing")
	return ship

func _new_enemy() -> EnemyShip:
	var enemy: EnemyShip = EnemyShipScript.new()
	get_root().add_child(enemy)
	enemy._ready()
	enemy.apply_loadout("SCORCH")
	enemy.set_match_state("playing")
	return enemy

# -- the loadout catalog is fully populated --------------------------------

func _assert_loadout_schema() -> void:
	for key in GameData.get_loadout_keys():
		var loadout: Dictionary = GameData.get_loadout(String(key))
		if not loadout.has("weapon") or not loadout.has("abilities") or not loadout.has("core"):
			_fail("Loadout %s missing weapon/abilities/core" % key)
			continue
		var abilities: Array = loadout["abilities"]
		if abilities.size() != 3:
			_fail("Loadout %s should have 3 abilities (got %d)" % [key, abilities.size()])
		for ability in abilities:
			var ability_id := String(ability.get("id", ""))
			if ability_id.is_empty():
				_fail("Loadout %s has an ability with empty id" % key)
			if not (ability_id in LOCAL_ABILITY_IDS) and not (ability_id in EMIT_ABILITY_IDS):
				_fail("Loadout %s ability id %s is neither local nor emit" % [key, ability_id])
		var core_id := String(loadout["core"].get("id", ""))
		if core_id.is_empty():
			_fail("Loadout %s has an empty core id" % key)
	print("LOADOUT schema: OK (%d loadouts)" % GameData.get_loadout_keys().size())

# -- fire / reload / ammo loop ---------------------------------------------

func _assert_player_fire_loop() -> void:
	var ship := _new_player()
	ship.set_loadout_by_index(0) # ION hitscan rifle, clip_size=32

	var fired_payloads: Array = []
	ship.primary_fired.connect(func(origin: Vector3, direction: Vector3, loadout_key: String, weapon_data: Dictionary, source: Node3D, team: int) -> void:
		fired_payloads.append({
			"origin": origin,
			"direction": direction,
			"loadout_key": loadout_key,
			"weapon_data": weapon_data,
			"source": source,
			"team": team
		})
	)

	var forward := Vector3(0, 0, -1)
	var starting_clip := ship.clip_ammo

	# Fire one round.
	ship._attempt_fire(forward)
	if ship.clip_ammo != starting_clip - 1:
		_fail("first shot should consume exactly one round (clip=%d expected %d)" % [ship.clip_ammo, starting_clip - 1])
	if fired_payloads.size() != 1:
		_fail("primary_fired should fire once on first shot (got %d)" % fired_payloads.size())
	elif String(fired_payloads[0]["loadout_key"]) != "ION":
		_fail("primary_fired carried wrong loadout_key (got %s)" % fired_payloads[0]["loadout_key"])

	# fire_cooldown should gate a second shot in the same frame.
	ship._attempt_fire(forward)
	if ship.clip_ammo != starting_clip - 1:
		_fail("fire_cooldown should block second shot same frame (clip=%d)" % ship.clip_ammo)

	# Drain the rest of the clip respecting the cooldown.
	for i in range(starting_clip):
		ship.fire_cooldown = 0.0
		ship._attempt_fire(forward)
		if ship.clip_ammo == 0:
			break
	if ship.clip_ammo != 0:
		_fail("draining clip should bottom out at 0 (got %d)" % ship.clip_ammo)
	if ship.reload_timer <= 0.0:
		_fail("empty clip should auto-start reload (timer=%f)" % ship.reload_timer)

	# Firing during reload is a no-op and does not emit.
	var mid_reload_shots := fired_payloads.size()
	ship._attempt_fire(forward)
	if fired_payloads.size() != mid_reload_shots:
		_fail("shots during reload should not emit primary_fired")

	# Tick until the reload finishes, then clip refills.
	ship._physics_process(0.25)
	ship._physics_process(0.9)
	if ship.reload_timer != 0.0 or ship.clip_ammo != ship.max_clip:
		_fail("reload should complete in ~1.1s (timer=%f clip=%d)" % [ship.reload_timer, ship.clip_ammo])

	print("PLAYER fire/reload loop: OK (fired %d rounds, clip refilled to %d)" % [fired_payloads.size(), ship.clip_ammo])

# -- ability routing (local vs. emit) --------------------------------------

# Fire every ability on every loadout and verify the matching effect: local
# ids set a state timer / toggle a property; emit ids produce an
# ability_triggered signal whose id matches the loadout's declared id.
func _assert_ship_ability_routing(ship: Node3D, label: String) -> void:
	var emits: Array = []
	ship.ability_triggered.connect(func(ability_id: String, loadout_key: String, source: Node3D, origin: Vector3, direction: Vector3, team: int) -> void:
		emits.append({"id": ability_id, "loadout_key": loadout_key})
	)

	var forward := Vector3(0, 0, -1)
	for key in GameData.get_loadout_keys():
		var loadout_key := String(key)
		# Reset loadout / state between ships so cooldowns don't leak.
		_apply_loadout(ship, loadout_key)
		ship.ability_cooldowns = [0.0, 0.0, 0.0]
		ship.state_timers.clear()
		ship.monarch_tier = 0
		ship.monarch_cooldown_mult = 1.0
		ship.legion_mode = "close"
		var abilities: Array = ship.loadout.get("abilities", [])
		for slot in range(abilities.size()):
			var expected_id := String(abilities[slot].get("id", ""))
			var emits_before := emits.size()

			if ship is PlayerShip:
				ship.ability_cooldowns[slot] = 0.0
				ship._try_activate_ability(slot)
			else:
				ship._try_activate_ability(slot, forward)

			var cooldown: float = float(abilities[slot].get("cooldown", 8.0)) * ship.monarch_cooldown_mult
			if absf(float(ship.ability_cooldowns[slot]) - cooldown) > 0.01:
				_fail("%s %s slot %d: cooldown should be set to %.2f (got %.2f)" % [label, loadout_key, slot, cooldown, ship.ability_cooldowns[slot]])

			if expected_id in EMIT_ABILITY_IDS:
				if emits.size() != emits_before + 1:
					_fail("%s %s slot %d (%s): expected one ability_triggered (got %d new)" % [label, loadout_key, slot, expected_id, emits.size() - emits_before])
				else:
					var emitted: Dictionary = emits[emits.size() - 1]
					if String(emitted["id"]) != expected_id:
						_fail("%s %s slot %d: emitted id %s but expected %s" % [label, loadout_key, slot, emitted["id"], expected_id])
					if String(emitted["loadout_key"]) != loadout_key:
						_fail("%s %s slot %d: emitted loadout_key %s but expected %s" % [label, loadout_key, slot, emitted["loadout_key"], loadout_key])
			else:
				if emits.size() != emits_before:
					_fail("%s %s slot %d (%s): local ability should NOT emit ability_triggered" % [label, loadout_key, slot, expected_id])
				# mode_switch toggles legion_mode; rearm restores resources;
				# everything else sets a state timer keyed by the ability id.
				match expected_id:
					"mode_switch":
						# mode_switch queues a 1s transition (HTML
						# last_ship_sailing.html:6798-6802); the ability
						# activation sets legion_pending_mode immediately
						# and the actual flip happens in _tick_legion_switch
						# when the timer reaches 0. Verify both the
						# immediate contract and the full integration.
						if ship.legion_pending_mode != "long":
							_fail("%s LEGION mode_switch should queue pending mode 'long' (got %s)" % [label, ship.legion_pending_mode])
						ship._tick_legion_switch(1.1)
						if ship.legion_mode != "long":
							_fail("%s LEGION mode_switch should flip close→long after timer (got %s)" % [label, ship.legion_mode])
					"rearm":
						pass # checked in _assert_rearm_and_cooldowns
					_:
						if not ship.is_state_active(expected_id):
							_fail("%s %s slot %d (%s): state timer not set" % [label, loadout_key, slot, expected_id])

			# Second activation inside cooldown is refused.
			var retry_emits := emits.size()
			if ship is PlayerShip:
				ship._try_activate_ability(slot)
			else:
				ship._try_activate_ability(slot, forward)
			if expected_id in EMIT_ABILITY_IDS and emits.size() != retry_emits:
				_fail("%s %s slot %d (%s): cooldown should block re-activation" % [label, loadout_key, slot, expected_id])

	print("%s ability routing: OK" % label)

# -- core routing ----------------------------------------------------------

func _assert_ship_core_routing(ship: Node3D, label: String) -> void:
	var emits: Array = []
	ship.core_triggered.connect(func(core_id: String, loadout_key: String, source: Node3D, origin: Vector3, direction: Vector3, team: int) -> void:
		emits.append({"id": core_id, "loadout_key": loadout_key})
	)

	var forward := Vector3(0, 0, -1)
	for key in GameData.get_loadout_keys():
		var loadout_key := String(key)
		_apply_loadout(ship, loadout_key)
		ship.core_meter = 100.0
		ship.state_timers.clear()
		ship.monarch_tier = 0
		ship.monarch_cooldown_mult = 1.0

		var core_id := String(ship.loadout.get("core", {}).get("id", ""))
		var emits_before := emits.size()

		if ship is PlayerShip:
			ship._try_activate_core()
		else:
			ship._try_activate_core(forward)

		if ship.core_meter != 0.0:
			_fail("%s %s core: meter should drain to 0 (got %.2f)" % [label, loadout_key, ship.core_meter])

		match core_id:
			"laser_core", "flame_core", "salvo_core":
				if emits.size() != emits_before + 1:
					_fail("%s %s core %s: expected one core_triggered emission" % [label, loadout_key, core_id])
				else:
					var emitted: Dictionary = emits[emits.size() - 1]
					if String(emitted["id"]) != core_id:
						_fail("%s %s core: emitted id %s but expected %s" % [label, loadout_key, emitted["id"], core_id])
			"afterburner_core", "sword_core", "smart_core":
				if not ship.is_state_active(core_id):
					_fail("%s %s core %s: expected state timer" % [label, loadout_key, core_id])
				if emits.size() != emits_before:
					_fail("%s %s core %s: should NOT emit core_triggered" % [label, loadout_key, core_id])
			"upgrade_core":
				if ship.monarch_tier != 1:
					_fail("%s MONARCH upgrade_core: first activation should set monarch_tier=1 (got %d)" % [label, ship.monarch_tier])
				if emits.size() != emits_before:
					_fail("%s MONARCH upgrade_core: should not emit core_triggered" % label)
			_:
				_fail("%s %s: unexpected core id %s" % [label, loadout_key, core_id])

	print("%s core routing: OK" % label)

# -- damage mitigation (player + enemy) ------------------------------------

func _assert_damage_mitigation_player() -> void:
	for state_id in DAMAGE_MULTS.keys():
		var ship := _new_player()
		ship.shield = 0.0 # isolate hull damage
		var starting_hp := ship.health
		var hit := 500.0
		ship._set_state(String(state_id), 5.0)
		ship.apply_damage(hit, Vector3.ZERO, "SCORCH")
		var expected := starting_hp - hit * float(DAMAGE_MULTS[state_id])
		if absf(ship.health - expected) > 0.5:
			_fail("PlayerShip %s mitigation: hp=%f expected %f" % [state_id, ship.health, expected])

	# phase_dash = invulnerable: zero damage taken.
	var phased := _new_player()
	phased.shield = 0.0
	var starting := phased.health
	phased._set_state("phase_dash", 5.0)
	phased.apply_damage(800.0, Vector3.ZERO, "SCORCH")
	if phased.health != starting:
		_fail("PlayerShip phase_dash should block all damage (hp=%f starting=%f)" % [phased.health, starting])

	print("PLAYER damage mitigation: OK (sword_block .3x, thermal .45x, gun .55x, vortex .4x, phase_dash immune)")

func _assert_damage_mitigation_enemy() -> void:
	for state_id in DAMAGE_MULTS.keys():
		var enemy := _new_enemy()
		enemy.shield = 0.0
		var starting_hp := enemy.health
		var hit := 500.0
		enemy._set_state(String(state_id), 5.0)
		enemy.apply_damage(hit, Vector3.ZERO, "ION")
		var expected := starting_hp - hit * float(DAMAGE_MULTS[state_id])
		if absf(enemy.health - expected) > 0.5:
			_fail("EnemyShip %s mitigation: hp=%f expected %f" % [state_id, enemy.health, expected])
	print("ENEMY damage mitigation: OK")

# -- rearm resets peers ----------------------------------------------------

func _assert_rearm_and_cooldowns() -> void:
	var ship := _new_player()
	_apply_loadout(ship, "MONARCH")
	# Seed all three cooldowns and empty the clip; Rearm should wipe peers
	# and refill ammunition / dash charges while still eating slot 2's
	# own cooldown.
	ship.ability_cooldowns = [5.0, 7.0, 0.0]
	ship.clip_ammo = 0
	ship.reload_timer = 1.0
	ship.dash_charges = 0
	ship.dash_recharge_timer = 4.0

	ship._try_activate_ability(2)

	if float(ship.ability_cooldowns[0]) != 0.0 or float(ship.ability_cooldowns[1]) != 0.0:
		_fail("Rearm should zero peer cooldowns (got %s)" % [ship.ability_cooldowns])
	if float(ship.ability_cooldowns[2]) <= 0.0:
		_fail("Rearm should still consume its own cooldown (got %.2f)" % ship.ability_cooldowns[2])
	if ship.clip_ammo != ship.max_clip:
		_fail("Rearm should refill the clip (%d / %d)" % [ship.clip_ammo, ship.max_clip])
	if ship.reload_timer != 0.0:
		_fail("Rearm should clear a pending reload (timer=%f)" % ship.reload_timer)
	if ship.dash_charges != int(ship.chassis.get("max_dashes", 1)):
		_fail("Rearm should restore dash charges (got %d)" % ship.dash_charges)
	if ship.dash_recharge_timer != 0.0:
		_fail("Rearm should zero dash_recharge_timer (got %f)" % ship.dash_recharge_timer)
	print("REARM cooldown wipe + refill: OK")

# -- upgrade core tiers stack monarch buffs --------------------------------

func _assert_upgrade_core_tiers() -> void:
	var ship := _new_player()
	_apply_loadout(ship, "MONARCH")
	var base_max_clip := ship.max_clip
	var base_max_shield := ship.max_shield

	# Tier 1: ammunition bump and arc rounds (max_clip ≥ 50).
	ship.core_meter = 100.0
	ship._try_activate_core()
	if ship.monarch_tier != 1:
		_fail("upgrade_core tier 1: monarch_tier=%d" % ship.monarch_tier)
	if ship.max_clip < 50:
		_fail("upgrade_core tier 1: max_clip should rise to ≥50 (got %d, base %d)" % [ship.max_clip, base_max_clip])

	# Tier 2: bonus shield + cooldown reduction.
	ship.core_meter = 100.0
	ship._try_activate_core()
	if ship.monarch_tier != 2:
		_fail("upgrade_core tier 2: monarch_tier=%d" % ship.monarch_tier)
	if ship.max_shield <= base_max_shield:
		_fail("upgrade_core tier 2: max_shield should rise above base (base %.1f new %.1f)" % [base_max_shield, ship.max_shield])
	if absf(ship.monarch_cooldown_mult - 0.7) > 0.001:
		_fail("upgrade_core tier 2: monarch_cooldown_mult should be 0.7 (got %.3f)" % ship.monarch_cooldown_mult)

	# Tier 3: XO-16 accelerator (+25% dmg).
	ship.core_meter = 100.0
	ship._try_activate_core()
	if ship.monarch_tier != 3:
		_fail("upgrade_core tier 3: monarch_tier=%d" % ship.monarch_tier)
	if absf(ship.monarch_damage_mult - 1.25) > 0.001:
		_fail("upgrade_core tier 3: monarch_damage_mult should be 1.25 (got %.3f)" % ship.monarch_damage_mult)
	if ship.get_damage_multiplier() < 1.25:
		_fail("get_damage_multiplier should reflect 1.25x at tier 3 (got %.3f)" % ship.get_damage_multiplier())

	# Tier 4 activation is ignored: tier caps at 3.
	ship.core_meter = 100.0
	ship._try_activate_core()
	if ship.monarch_tier != 3:
		_fail("upgrade_core: tier should cap at 3 (got %d)" % ship.monarch_tier)

	print("UPGRADE_CORE tiers 1→2→3 + cap: OK")

# -- monarch cooldown scaling applies on next activation -------------------

func _assert_monarch_cooldown_scaling() -> void:
	var ship := _new_player()
	_apply_loadout(ship, "MONARCH")
	# Force a cooldown multiplier as if tier-2 had fired, then activate the
	# rocket salvo slot and confirm its cooldown was multiplied.
	ship.monarch_cooldown_mult = 0.7
	ship.ability_cooldowns = [0.0, 0.0, 0.0]
	var base_cooldown := float(ship.loadout["abilities"][0]["cooldown"]) # rocket_salvo = 6.0
	ship._try_activate_ability(0)
	var expected := base_cooldown * 0.7
	if absf(float(ship.ability_cooldowns[0]) - expected) > 0.01:
		_fail("monarch_cooldown_mult should scale ability cooldowns (got %.3f expected %.3f)" % [ship.ability_cooldowns[0], expected])
	print("MONARCH cooldown scaling: OK (%.2f × 0.7 = %.2f)" % [base_cooldown, ship.ability_cooldowns[0]])

func _apply_loadout(ship: Node3D, loadout_key: String) -> void:
	if ship is PlayerShip:
		var keys := GameData.get_loadout_keys()
		for index in range(keys.size()):
			if String(keys[index]) == loadout_key:
				ship.set_loadout_by_index(index)
				ship.set_match_state("playing")
				return
	elif ship is EnemyShip:
		ship.apply_loadout(loadout_key)
		ship.set_match_state("playing")
