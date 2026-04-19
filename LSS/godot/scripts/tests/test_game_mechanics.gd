extends SceneTree

# Coverage for the four game-mechanics slices ported in tasks #43, #45, #47, #49:
#
#   1. ramming + execution  -> ram constants, doomed flag, execution gate math
#   2. chassis-specific      -> LEGION mode_switch with the 1s pending-delay tick
#   3. stasis + trap fields  -> enter_stasis, shield recharge over duration,
#                               re-entry immunity, set_velocity/scale_velocity
#                               hooks used by tether_trap + incendiary_gas
#   4. environmental hazards -> covered by scripts/tests/test_hazards.gd
#                               (the cluster/destructible smoke test).
#
# main.gd's per-frame collision resolver and execution sweep are not exercised
# directly here because _ready() requires arena_map/HUD/environment. We cover
# the ship-side state each slice depends on, plus the constants the resolver
# reads.

const PlayerShipScript = preload("res://scripts/player_ship.gd")
const EnemyShipScript = preload("res://scripts/enemy_ship.gd")
const MainScript = preload("res://scripts/main.gd")
const GameData = preload("res://scripts/game_data.gd")

var _ok := true

func _fail(msg: String) -> void:
	push_error(msg)
	_ok = false

func _new_player() -> PlayerShip:
	var ship: PlayerShip = PlayerShipScript.new()
	get_root().add_child(ship)
	return ship

func _new_enemy() -> EnemyShip:
	var ship: EnemyShip = EnemyShipScript.new()
	get_root().add_child(ship)
	return ship

func _find_ability_slot(loadout_key: String, ability_id: String) -> int:
	var loadout := GameData.get_loadout(loadout_key)
	var abilities: Array = loadout.get("abilities", [])
	for i in range(abilities.size()):
		if String(abilities[i].get("id", "")) == ability_id:
			return i
	return -1

func _select_loadout(ship: Object, loadout_key: String) -> void:
	var keys := GameData.get_loadout_keys()
	var idx := keys.find(loadout_key)
	if idx < 0:
		_fail("loadout key %s not found" % loadout_key)
		return
	# PlayerShip exposes set_loadout_by_index; EnemyShip uses apply_loadout(key).
	if ship.has_method("set_loadout_by_index"):
		ship.set_loadout_by_index(idx)
	elif ship.has_method("apply_loadout"):
		ship.apply_loadout(loadout_key)
	else:
		_fail("ship has no loadout setter method")

func _init() -> void:
	GameData.ensure_input_map()
	print("=== Game-mechanics slice tests ===")

	_assert_ram_constants()
	_assert_stasis_enter_tick_exit()
	_assert_stasis_reentry_blocked()
	_assert_trap_velocity_hooks()
	_assert_doomed_and_exec_gate()
	_assert_legion_mode_switch_delay()

	if _ok:
		print("RESULT: PASS")
		quit(0)
	else:
		push_error("test_game_mechanics FAILED")
		quit(1)

# -- Slice 1: ramming + execution ------------------------------------------

func _assert_ram_constants() -> void:
	# RAM_IMPACT_THRESHOLD = 80.0, RAM_DAMAGE_MULT = 0.3, RAM_BOUNCE_COEFF = 0.6
	# These constants are read by _resolve_ship_ship_collisions; they must be
	# the exact values ported from the HTML so collision arithmetic matches.
	if absf(MainScript.RAM_IMPACT_THRESHOLD - 80.0) > 0.0001:
		_fail("RAM_IMPACT_THRESHOLD should be 80.0, got %f" % MainScript.RAM_IMPACT_THRESHOLD)
	if absf(MainScript.RAM_DAMAGE_MULT - 0.3) > 0.0001:
		_fail("RAM_DAMAGE_MULT should be 0.3, got %f" % MainScript.RAM_DAMAGE_MULT)
	if absf(MainScript.RAM_BOUNCE_COEFF - 0.6) > 0.0001:
		_fail("RAM_BOUNCE_COEFF should be 0.6, got %f" % MainScript.RAM_BOUNCE_COEFF)
	# Execution radius multiplier should be > 0; the HTML uses ~3x hull length.
	if MainScript.EXEC_RADIUS_MULT <= 0.0:
		_fail("EXEC_RADIUS_MULT must be positive")
	print("Ram/exec constants (80/0.3/0.6): OK")

func _assert_doomed_and_exec_gate() -> void:
	# is_doomed() flips based on the `doomed` flag; once true, the main.gd
	# _check_executions sweep gates on exec_radius distance. We simulate the
	# gate math here on two ships.
	var enemy := _new_enemy()
	_select_loadout(enemy, "ION")
	enemy.global_position = Vector3.ZERO
	if enemy.is_doomed():
		_fail("fresh enemy should not start doomed")
	enemy.doomed = true
	if not enemy.is_doomed():
		_fail("enemy.doomed = true should flip is_doomed()")

	var hull_length := float(enemy.chassis.get("hull_length", 100.0))
	var exec_radius := hull_length * MainScript.EXEC_RADIUS_MULT
	var exec_radius_sq := exec_radius * exec_radius
	# Inside radius: gate triggers.
	var inside_pos := Vector3(exec_radius * 0.5, 0.0, 0.0)
	if inside_pos.distance_squared_to(enemy.global_position) >= exec_radius_sq:
		_fail("exec gate should trigger inside radius")
	# Outside radius: gate does not trigger.
	var outside_pos := Vector3(exec_radius * 1.5, 0.0, 0.0)
	if outside_pos.distance_squared_to(enemy.global_position) < exec_radius_sq:
		_fail("exec gate should not trigger outside radius")
	print("Doomed + exec-gate math: OK (exec_radius=%.1f)" % exec_radius)

# -- Slice 2: chassis-specific (LEGION mode_switch) ------------------------

func _assert_legion_mode_switch_delay() -> void:
	# LEGION mode_switch queues a pending mode and starts a 1s transition
	# timer; the flip happens only after _tick_legion_switch counts down.
	var legion_key := "LEGION"
	var slot := _find_ability_slot(legion_key, "mode_switch")
	if slot < 0:
		_fail("LEGION loadout has no mode_switch ability")
		return

	var ship := _new_player()
	_select_loadout(ship, legion_key)
	var initial_mode: String = ship.legion_mode
	if initial_mode != "close":
		_fail("LEGION should start in close mode, got %s" % initial_mode)

	# Fire the ability. legion_mode stays "close" until the delay elapses.
	ship._try_activate_ability(slot)
	if ship.legion_mode != "close":
		_fail("LEGION mode_switch should NOT flip immediately (got %s)" % ship.legion_mode)
	if ship.legion_pending_mode != "long":
		_fail("LEGION pending mode should be 'long' after mode_switch, got %s" % ship.legion_pending_mode)
	if absf(ship.legion_switch_timer - 1.0) > 0.0001:
		_fail("LEGION switch timer should be 1.0s, got %f" % ship.legion_switch_timer)

	# Tick 1.1s worth; the flip should have happened.
	for i in range(11):
		ship._tick_legion_switch(0.1)
	if ship.legion_mode != "long":
		_fail("LEGION should flip close->long after 1s tick, got %s" % ship.legion_mode)
	if not ship.legion_pending_mode.is_empty():
		_fail("LEGION pending mode should clear after flip, got %s" % ship.legion_pending_mode)
	if ship.legion_switch_timer > 0.0:
		_fail("LEGION switch timer should be 0 after flip, got %f" % ship.legion_switch_timer)
	print("LEGION mode_switch 1s delay: OK (close -> long after tick)")

# -- Slice 3: stasis + trap fields -----------------------------------------

func _assert_stasis_enter_tick_exit() -> void:
	# Stasis locks the ship for N seconds, zeroes velocity, linearly refills
	# shield to max, and guarantees a full shield at exit.
	var ship := _new_player()
	_select_loadout(ship, "ION")
	ship.velocity = Vector3(100.0, 0.0, 0.0)
	ship.shield = 0.0
	var duration := 3.0

	ship.enter_stasis(duration)
	if not ship.in_stasis:
		_fail("enter_stasis should flip in_stasis true")
	if absf(ship.stasis_timer - duration) > 0.0001:
		_fail("stasis_timer should initialize to duration")
	if ship.velocity != Vector3.ZERO:
		_fail("enter_stasis should zero velocity (got %s)" % str(ship.velocity))
	if ship.pre_stasis_velocity != Vector3(100.0, 0.0, 0.0):
		_fail("pre_stasis_velocity should cache incoming velocity")

	# Tick half the duration; shield should be ~50% of max.
	var half_ticks := int(duration * 0.5 / 0.1)
	for i in range(half_ticks):
		ship._tick_stasis(0.1)
	var expected_shield := ship.max_shield * 0.5
	# Allow 5% slack; linear recharge accumulates small float drift.
	if absf(ship.shield - expected_shield) > ship.max_shield * 0.05:
		_fail("stasis halfway shield should be ~%.1f, got %.1f" % [expected_shield, ship.shield])

	# Tick the remainder; stasis should auto-exit and shield should be max.
	for i in range(int(duration / 0.1) + 2):
		ship._tick_stasis(0.1)
	if ship.in_stasis:
		_fail("stasis should auto-exit after timer")
	if absf(ship.shield - ship.max_shield) > 0.1:
		_fail("stasis should finish with full shield, got %.1f / %.1f" % [ship.shield, ship.max_shield])
	print("Stasis enter/tick/auto-exit + shield recharge: OK")

func _assert_stasis_reentry_blocked() -> void:
	# enter_stasis while already in stasis must be a no-op; overlapping field
	# pickups shouldn't double-extend the lock or zero velocity a second time.
	var ship := _new_player()
	_select_loadout(ship, "ION")
	ship.enter_stasis(3.0)
	var first_timer := ship.stasis_timer
	ship.enter_stasis(10.0)  # Should NOT overwrite.
	if absf(ship.stasis_timer - first_timer) > 0.0001:
		_fail("second enter_stasis should be a no-op (timer became %f, was %f)" % [ship.stasis_timer, first_timer])
	print("Stasis re-entry blocked: OK")

func _assert_trap_velocity_hooks() -> void:
	# Tether-trap root uses set_velocity(Vector3.ZERO) every frame while rooted;
	# incendiary-gas slow uses scale_velocity(factor) every frame. Both must
	# actually mutate velocity on the ship.
	var ship := _new_player()
	_select_loadout(ship, "ION")
	ship.velocity = Vector3(100.0, 50.0, -30.0)

	ship.set_velocity(Vector3.ZERO)
	if ship.velocity != Vector3.ZERO:
		_fail("set_velocity(ZERO) should hard-zero velocity (tether root)")

	ship.velocity = Vector3(100.0, 0.0, 0.0)
	ship.scale_velocity(0.5)
	if absf(ship.velocity.x - 50.0) > 0.0001:
		_fail("scale_velocity(0.5) should halve velocity (incendiary slow)")
	print("Trap velocity hooks (tether root + gas slow): OK")
