class_name EnemyShip
extends Node3D

const GameData = preload("res://scripts/game_data.gd")
const ShipVisuals = preload("res://scripts/ship_visuals.gd")
const PlayerShip = preload("res://scripts/player_ship.gd")
const ArenaMap = preload("res://scripts/arena_map.gd")

signal primary_fired(origin: Vector3, direction: Vector3, loadout_key: String, weapon_data: Dictionary, source: Node3D, team: int)
signal ability_triggered(ability_id: String, loadout_key: String, source: Node3D, origin: Vector3, direction: Vector3, team: int)
signal core_triggered(core_id: String, loadout_key: String, source: Node3D, origin: Vector3, direction: Vector3, team: int)
# killer_loadout_key = attacker's loadout (or "" if environmental / unknown);
# victim_loadout_key = this ship's loadout. Emitted once per death.
signal destroyed(killer_loadout_key: String, victim_loadout_key: String)

const TEAM_ENEMY := 1

# Doomed state thresholds (HTML LSS.DOOMED_HEALTH_PCT = 0.15, DOOMED_TIMER = 10
# at last_ship_sailing.html line 701). Enemies enter doomed at the same
# thresholds as the player so the scoreboard / execute mechanic treat them
# symmetrically.
const DOOMED_HEALTH_PCT := 0.15
const DOOMED_TIMER := 10.0

var loadout_key := "SCORCH"
var loadout: Dictionary = {}
var chassis: Dictionary = {}
var signature: Dictionary = {}
var target: PlayerShip
var spawn_point := Vector3.ZERO
var velocity := Vector3.ZERO
var health := 0.0
var max_health := 0.0
var shield := 0.0
var max_shield := 0.0
var alive := true
# Doomed state: entered when hull/max_health ≤ DOOMED_HEALTH_PCT. Latches
# until death or respawn; doom_timer counts down to fatal when the last 15%
# is reached.
var doomed := false
var doom_timer := 0.0
var respawn_timer := 0.0
var fire_cooldown := 0.0
var reload_timer := 0.0
var clip_ammo := 0
var max_clip := 0
var orbit_sign := 1.0
var orbit_phase := 0.0
var ability_cooldowns := [0.0, 0.0, 0.0]
var state_timers: Dictionary = {}
var core_meter := 0.0
var legion_mode := "close"
# LEGION 1s switch transition (mirror of PlayerShip.legion_switch_timer);
# enemy_ship ticks it in _physics_process so bots honor the same delay
# humans do rather than flipping instantly.
var legion_switch_timer := 0.0
var legion_pending_mode := ""
var monarch_tier := 0
var monarch_damage_mult := 1.0
var monarch_cooldown_mult := 1.0
var monarch_arc_rounds := false
var monarch_missile_racks := false
var monarch_xo16_accel := false
var decision_timer := 0.0
var match_state := "warmup"
var arena_map: ArenaMap

# ---- Bot AI enhancements (HTML last_ship_sailing.html:2959-3393) ----
# Squad coordination + memory / share + LOS-gated firing + retreat on doom.
# Pure math lives in BotAIMath (scripts/bot_ai_math.gd); state + cadence
# lives here. See the SLICE A block in _physics_process for the tick order.

# Role: "engage" (charge in) or "flank" (offset 600u perpendicular to the
# player axis). Set once at configure time from an RNG draw.
var ai_role := "engage"

# Preferred engagement distance; set from loadout_key in apply_loadout.
# Replaces the hard 900 / 360 thresholds with loadout-aware bands.
var ai_range_preference := 800.0

# Retreat mode: latches on doom; bots move away from the live player at
# full speed and stop strafing / firing (HTML lines 3057-3059, 3082-3084,
# 3156). Reset in respawn() so the bot re-engages on its next life.
var ai_retreating := false

# Strafe state rolls every 1-3 seconds: on/off flag + alternating direction.
# When active and in range, adds a lateral offset to the movement target.
var ai_strafe_active := false
var ai_strafe_dir := 1.0
var ai_strafe_timer := 0.0

# findTarget cadence (1-3s); separate from combat decision_timer (0.35-0.6s).
# On elapse, the bot rechecks LOS to the player and updates its movement
# target (live LOS > squad shared > own drifting memory > no target).
var ai_find_target_timer := 0.0

# Memory of the last-seen live player position. ai_memory_age ticks each
# frame while valid; cleared when age reaches MEMORY_DURATION.
var ai_memory_valid := false
var ai_memory_pos := Vector3.ZERO
var ai_memory_age := 0.0

# Movement target produced by findTarget. When ai_has_target is false the
# movement code falls back to target.global_position (live player) so the
# bot keeps moving even before its first findTarget tick.
var ai_target_pos := Vector3.ZERO
var ai_has_target := false

# Per-bot RNG; seeded from configure()'s seed_value so bots stay
# deterministic given the same seed but still vary between instances.
var ai_rng := RandomNumberGenerator.new()

# Team-level shared target broadcast. Mirrors `game.botSharedTarget` (HTML
# lines 3194-3211); a bot with LOS writes the player position here so
# squadmates without LOS can read it as their movement target. Static so
# all instances share; main.gd calls reset_shared_broadcasts() in
# _begin_round so stale positions don't leak between rounds.
static var _shared_target_by_team: Dictionary = {}

var visuals: ShipVisuals

func _ready() -> void:
	visuals = ShipVisuals.new()
	visuals.name = "Visuals"
	add_child(visuals)
	if loadout.is_empty():
		apply_loadout(loadout_key)

func configure(new_loadout_key: String, new_target: PlayerShip, start_position: Vector3, seed_value: float) -> void:
	loadout_key = new_loadout_key
	target = new_target
	spawn_point = start_position
	orbit_phase = seed_value
	orbit_sign = -1.0 if int(floor(seed_value * 10.0)) % 2 == 0 else 1.0
	# Seed the per-bot RNG from seed_value so role / strafe / drift stay
	# deterministic given a seed but vary across bots in the same squad.
	# +1 avoids a zero seed (Godot's RNG dislikes seed 0).
	ai_rng.seed = int(seed_value * 100000.0) + 1
	ai_role = BotAIMath.assign_squad_role(ai_rng.randf())
	if visuals:
		apply_loadout(loadout_key)
		respawn(true)

func _physics_process(delta: float) -> void:
	if not target:
		return

	if not alive:
		return

	# Doomed countdown. Ticks regardless of match_state so bots that enter
	# doomed during warmup still resolve naturally when play resumes.
	# Matches HTML line 3051-3053 (inside bot update, unconditional).
	if doomed:
		doom_timer = maxf(0.0, doom_timer - delta)
		if doom_timer <= 0.0:
			_apply_doomed_death()
			return

	for index in range(ability_cooldowns.size()):
		ability_cooldowns[index] = maxf(0.0, float(ability_cooldowns[index]) - delta)
	_tick_state_timers(delta)
	_tick_legion_switch(delta)
	core_meter = minf(100.0, core_meter + delta * 4.5)

	fire_cooldown = maxf(0.0, fire_cooldown - delta)
	if reload_timer > 0.0:
		reload_timer = maxf(0.0, reload_timer - delta)
		if reload_timer == 0.0:
			clip_ammo = max_clip

	if match_state != "playing":
		velocity = velocity.move_toward(Vector3.ZERO, float(chassis.get("deceleration", 600.0)) * delta)
		visuals.update_ship_visuals(delta, 0.0, Vector3.ZERO, Vector2.ZERO, 0.0)
		return

	# ---- SLICE A: bot AI cadence ticks ----
	# Retreat latches on doom (HTML lines 3057-3059). Bots that dropped below
	# 15% hull commit to the escape until death / respawn.
	if doomed:
		ai_retreating = true

	# findTarget: every 1-3s re-evaluate LOS and produce ai_target_pos (HTML
	# lines 3062-3067). Between ticks, ai_target_pos stays fixed, giving the
	# "I last saw you over there" feel when a bot loses sight of the player.
	ai_find_target_timer -= delta
	if ai_find_target_timer <= 0.0:
		ai_find_target_timer = ai_rng.randf_range(
			BotAIMath.FIND_TARGET_INTERVAL_MIN,
			BotAIMath.FIND_TARGET_INTERVAL_MAX,
		)
		_run_find_target()

	# Memory ages whether or not findTarget fired; it's a wall-clock decay.
	if ai_memory_valid:
		ai_memory_age += delta
		if not BotAIMath.is_memory_valid(ai_memory_age):
			ai_memory_valid = false
			ai_memory_age = 0.0

	# Strafe roll: 1-3s intervals with 50/50 on/off and 50/50 direction
	# (HTML lines 3069-3075). The roll runs independently of LOS so bots
	# keep juking even when they've lost the player.
	ai_strafe_timer -= delta
	if ai_strafe_timer <= 0.0:
		ai_strafe_active = ai_rng.randf() < 0.5
		ai_strafe_dir = 1.0 if ai_rng.randf() < 0.5 else -1.0
		ai_strafe_timer = ai_rng.randf_range(
			BotAIMath.STRAFE_TIMER_MIN, BotAIMath.STRAFE_TIMER_MAX,
		)

	orbit_phase += delta

	# Movement anchor: retreat overrides everything and points away from the
	# live player; otherwise follow findTarget's result (possibly stale or
	# drifting); otherwise the live player as a last resort.
	var desired_anchor: Vector3 = target.global_position
	if ai_retreating:
		var away_dir := BotAIMath.compute_retreat_direction(global_position, target.global_position)
		desired_anchor = global_position + away_dir * 2000.0
	elif ai_has_target:
		desired_anchor = ai_target_pos

	var move_target := desired_anchor
	if arena_map:
		move_target = arena_map.get_navigation_target(global_position, desired_anchor, TEAM_ENEMY)
	# Live player distance drives aim, firing gates, flank / strafe gates.
	# Movement direction uses the (possibly stale) move_target so memory
	# decay actually shows up as "moving toward a wrong spot".
	var to_target := target.global_position - global_position
	var to_move_target := move_target - global_position
	var distance := to_target.length()
	var move_distance := to_move_target.length()
	var aim_dir := to_target.normalized() if distance > 0.01 else -global_basis.z
	var move_dir := to_move_target.normalized() if move_distance > 0.01 else aim_dir

	# Flank blend: if we're a flanker and the live player distance is in the
	# flank band, blend move_dir toward a position 600u to the player's
	# right (HTML lines 3092-3099). Skipped while retreating.
	if not ai_retreating and BotAIMath.should_flank(distance, ai_role):
		var flank_target := BotAIMath.compute_flank_target(target.global_position, global_position)
		var to_flank := flank_target - global_position
		if to_flank.length_squared() > 0.001:
			move_dir = move_dir.lerp(to_flank.normalized(), BotAIMath.FLANK_BLEND).normalized()

	var orbit_right := aim_dir.cross(Vector3.UP).normalized()
	if orbit_right.length_squared() < 0.001:
		orbit_right = Vector3.RIGHT

	var move_speed_multiplier := 1.0
	if is_state_active("afterburner"):
		move_speed_multiplier *= 1.35
	if is_state_active("afterburner_core"):
		move_speed_multiplier *= 1.65
	if is_state_active("sword_core"):
		move_speed_multiplier *= 1.12

	# vertical_delta stays hoisted because the visuals call below consumes it
	# regardless of retreat state (it drives the pitch/roll animation).
	var vertical_delta := clampf(target.global_position.y - global_position.y, -220.0, 220.0) / 220.0

	# Range-preference bands replace the hard 900 / 360 thresholds so SCORCH
	# (500) closes hard while NORTHSTAR (1500) holds distance. Retreat
	# overrides the bands with full-speed escape.
	var desired_velocity := Vector3.ZERO
	if ai_retreating:
		desired_velocity = move_dir * float(chassis.get("flight_speed", 350.0)) * move_speed_multiplier
	else:
		var far_threshold := ai_range_preference * 1.2
		var close_threshold := ai_range_preference * 0.7
		if distance > far_threshold:
			desired_velocity += move_dir * float(chassis.get("flight_speed", 350.0)) * 0.72 * move_speed_multiplier
		elif distance < close_threshold:
			desired_velocity -= move_dir * float(chassis.get("flight_speed", 350.0)) * 0.45 * move_speed_multiplier
		else:
			desired_velocity += move_dir * float(chassis.get("flight_speed", 350.0)) * 0.18 * move_speed_multiplier

		# Active strafe (HTML lines 3103-3108) replaces the steady orbit
		# with a rolled-direction perpendicular offset. When the roll is
		# cold, fall back to the existing steady orbit so bots never look
		# frozen mid-engagement.
		if BotAIMath.should_strafe(ai_strafe_active, distance, ai_range_preference, doomed):
			var strafe_perp := BotAIMath.compute_strafe_offset(aim_dir, ai_strafe_dir)
			desired_velocity += strafe_perp * float(chassis.get("strafe_speed", 280.0)) * move_speed_multiplier
		else:
			desired_velocity += orbit_right * orbit_sign * float(chassis.get("strafe_speed", 280.0)) * 0.45 * move_speed_multiplier

		desired_velocity += Vector3.UP * vertical_delta * float(chassis.get("vertical_speed", 250.0)) * 0.55 * move_speed_multiplier

	velocity = velocity.move_toward(desired_velocity, float(chassis.get("acceleration", 800.0)) * delta)
	var max_speed := float(chassis.get("flight_speed", 350.0)) * 0.95 * move_speed_multiplier
	if velocity.length() > max_speed:
		velocity = velocity.normalized() * max_speed

	global_position += velocity * delta
	if arena_map:
		global_position = arena_map.constrain_point(global_position, get_collision_radius() * 0.6)
	else:
		_apply_bounds()

	look_at(global_position + aim_dir, Vector3.UP)
	var forward := -global_basis.z

	decision_timer -= delta
	if decision_timer <= 0.0:
		decision_timer = 0.35 + randf() * 0.25
		_run_combat_decisions(distance, aim_dir, forward)

	_maybe_fire(distance, aim_dir, forward)

	var local_velocity: Vector3 = global_basis.inverse() * velocity
	var speed_ratio := clampf(velocity.length() / maxf(1.0, float(chassis.get("flight_speed", 350.0))), 0.0, 1.4)
	var boost_amount := 0.0
	if is_state_active("afterburner") or is_state_active("afterburner_core"):
		boost_amount = 0.45
	elif is_state_active("phase_dash"):
		boost_amount = 0.8
	visuals.update_ship_visuals(delta, speed_ratio, local_velocity, Vector2(orbit_sign * 8.0, vertical_delta * -6.0), boost_amount)

func apply_loadout(new_loadout_key: String) -> void:
	loadout_key = new_loadout_key
	loadout = GameData.get_loadout(loadout_key)
	chassis = GameData.get_chassis_for_loadout(loadout_key)
	signature = GameData.get_signature(loadout_key)
	max_health = float(chassis.get("max_health", 10000.0))
	max_shield = float(chassis.get("max_shield", 3000.0))
	health = max_health
	shield = max_shield
	var weapon: Dictionary = loadout.get("weapon", {})
	max_clip = int(weapon.get("clip_size", 12))
	clip_ammo = max_clip
	fire_cooldown = 0.0
	reload_timer = 0.0
	ability_cooldowns = [0.0, 0.0, 0.0]
	state_timers.clear()
	core_meter = 0.0
	legion_mode = "close"
	legion_switch_timer = 0.0
	legion_pending_mode = ""
	monarch_tier = 0
	monarch_damage_mult = 1.0
	monarch_cooldown_mult = 1.0
	monarch_arc_rounds = false
	monarch_missile_racks = false
	monarch_xo16_accel = false
	decision_timer = 0.0
	# Loadout-derived AI bits: range preference comes straight from the
	# loadout key (HTML lines 3017-3028). Fire-cadence / memory state resets
	# happen in respawn() so round boundaries clear stale target info.
	ai_range_preference = BotAIMath.get_loadout_range_preference(loadout_key)
	if visuals:
		visuals.configure_ship(loadout_key, chassis, signature)
		visuals.set_ship_enabled(true)

func apply_damage(amount: float, _hit_point: Vector3, source_loadout_key: String) -> void:
	if not alive:
		return
	if is_state_active("phase_dash"):
		return

	if is_state_active("sword_block"):
		amount *= 0.3
	if is_state_active("thermal_shield"):
		amount *= 0.45
	if is_state_active("gun_shield"):
		amount *= 0.55
	if is_state_active("vortex_shield"):
		amount *= 0.4

	if shield > 0.0:
		visuals.pulse_shield()
		var shield_damage := minf(shield, amount)
		shield -= shield_damage
		amount -= shield_damage

	if amount > 0.0:
		health -= amount

	# Enter doomed state at the 15% threshold (HTML line 3413).
	if not doomed and health > 0.0 and health / maxf(1.0, max_health) <= DOOMED_HEALTH_PCT:
		doomed = true
		doom_timer = DOOMED_TIMER

	if health <= 0.0:
		alive = false
		doomed = false
		doom_timer = 0.0
		respawn_timer = 3.2
		velocity = Vector3.ZERO
		visuals.set_ship_enabled(false)
		global_position = Vector3(0, -4000, 0)
		destroyed.emit(source_loadout_key, loadout_key)

# Fatal when doom_timer reaches zero with no finishing blow. destroyed.emit()
# still fires with an empty killer key so kill-feed / scoring paths run, but
# no attacker is credited (matches HTML die(null) for timer kills).
func _apply_doomed_death() -> void:
	if not alive:
		return
	health = 0.0
	alive = false
	doomed = false
	doom_timer = 0.0
	respawn_timer = 3.2
	velocity = Vector3.ZERO
	visuals.set_ship_enabled(false)
	global_position = Vector3(0, -4000, 0)
	destroyed.emit("", loadout_key)

func respawn(force_position := false) -> void:
	alive = true
	doomed = false
	doom_timer = 0.0
	respawn_timer = 0.0
	health = max_health
	shield = max_shield
	clip_ammo = max_clip
	fire_cooldown = 0.0
	reload_timer = 0.0
	velocity = Vector3.ZERO
	ability_cooldowns = [0.0, 0.0, 0.0]
	state_timers.clear()
	core_meter = 0.0
	legion_mode = "close"
	legion_switch_timer = 0.0
	legion_pending_mode = ""
	monarch_tier = 0
	monarch_damage_mult = 1.0
	monarch_cooldown_mult = 1.0
	monarch_arc_rounds = false
	monarch_missile_racks = false
	monarch_xo16_accel = false
	decision_timer = 0.35 + randf() * 0.2
	# Reset bot AI cadence + transient state for the new life. Role is set
	# once at configure and carries across respawns (a bot's tactical
	# preference shouldn't flip mid-match).
	ai_retreating = false
	ai_strafe_active = false
	ai_strafe_dir = 1.0 if ai_rng.randf() < 0.5 else -1.0
	ai_strafe_timer = ai_rng.randf_range(
		BotAIMath.STRAFE_TIMER_MIN, BotAIMath.STRAFE_TIMER_MAX,
	)
	# Small randomized offset on the find-target timer so a squad of bots
	# staggers its LOS checks rather than all pulsing on the same frame.
	ai_find_target_timer = ai_rng.randf_range(
		BotAIMath.FIND_TARGET_INTERVAL_MIN * 0.25,
		BotAIMath.FIND_TARGET_INTERVAL_MAX * 0.5,
	)
	ai_memory_valid = false
	ai_memory_age = 0.0
	ai_has_target = false
	visuals.set_ship_enabled(true)
	if force_position or global_position.distance_to(spawn_point) > 10.0:
		global_position = spawn_point

func is_alive() -> bool:
	return alive

func is_doomed() -> bool:
	return doomed and alive

func get_doom_timer() -> float:
	return doom_timer

func get_team() -> int:
	return TEAM_ENEMY

func get_collision_radius() -> float:
	# Match HTML wall-collision sphere (last_ship_sailing.html:5904):
	# `collRadius = ch.hullLength * 0.4`. The earlier 0.14 multiplier was
	# tuned for the old 0.25 visual scale factor and let bullets brush past
	# ship hulls at point-blank range.
	return float(chassis.get("hull_length", 100.0)) * 0.4

func set_arena_map(new_arena_map: ArenaMap) -> void:
	arena_map = new_arena_map

func get_health_ratio() -> float:
	return health / maxf(1.0, max_health)

func get_shield_ratio() -> float:
	return shield / maxf(1.0, max_shield)

func is_state_active(state_id: String) -> bool:
	return float(state_timers.get(state_id, 0.0)) > 0.0

func add_core_charge(amount: float) -> void:
	core_meter = clampf(core_meter + amount / 120.0, 0.0, 100.0)

func restore_shield(amount: float) -> void:
	shield = minf(max_shield, shield + amount)

# Velocity helpers used by main.gd's trap-field ticks: scale_velocity is the
# per-frame multiplicative drag applied by incendiary_gas once it ignites, and
# set_velocity is the hard zero applied by tether_trap while rooting the ship.
# Duck-typed from main.gd so bots and the player can share a single code path.
func set_velocity(new_velocity: Vector3) -> void:
	velocity = new_velocity

func scale_velocity(factor: float) -> void:
	velocity *= factor

func get_damage_multiplier() -> float:
	var multiplier := monarch_damage_mult
	if is_state_active("sword_core"):
		multiplier *= 1.2
	return multiplier

func set_match_state(new_state: String) -> void:
	match_state = new_state

func reset_for_round() -> void:
	respawn(true)

func _attempt_fire(forward: Vector3) -> void:
	if fire_cooldown > 0.0 or reload_timer > 0.0:
		return

	if clip_ammo <= 0:
		reload_timer = 1.3
		return

	var weapon: Dictionary = loadout.get("weapon", {})
	clip_ammo -= 1
	fire_cooldown = float(weapon.get("fire_rate", 0.25))
	if is_state_active("smart_core"):
		fire_cooldown *= 0.55
	if clip_ammo == 0:
		reload_timer = 1.3

	visuals.trigger_muzzle_flash()
	var muzzle_origin := global_position + forward * 36.0
	primary_fired.emit(muzzle_origin, forward, loadout_key, weapon.duplicate(true), self, TEAM_ENEMY)

# Fire gate (HTML last_ship_sailing.html:3156-3175 + 3287-3313). Combines:
# retreat suppression, weapon range cap (0.92x so bots don't fire at the very
# edge and miss for free), alignment floor, range-preference gate, LOS ray
# against ArenaMap walls, and an accuracy roll. On accuracy fail, the shot
# still burns cooldown + muzzle flash so the animation reads as a miss rather
# than a frozen bot.
func _maybe_fire(distance: float, aim_dir: Vector3, forward: Vector3) -> void:
	if ai_retreating:
		return
	if not target or not target.is_alive():
		return
	var weapon: Dictionary = loadout.get("weapon", {})
	var weapon_range := float(weapon.get("range", 2200.0))
	if distance >= weapon_range * 0.92:
		return
	if forward.dot(aim_dir) <= 0.94:
		return
	if not BotAIMath.is_within_firing_range(distance, ai_range_preference):
		return
	if arena_map and not arena_map.segment_is_clear(global_position, target.global_position, 12.0):
		return
	var accuracy := BotAIMath.compute_accuracy(distance, weapon_range)
	if ai_rng.randf() > accuracy:
		_burn_shot()
		return
	_attempt_fire(forward)

# Mirrors _attempt_fire's cooldown / clip / reload bookkeeping without emitting
# the projectile signal. Used by _maybe_fire when the accuracy roll fails; the
# bot commits to the miss rather than dry-firing infinitely.
func _burn_shot() -> void:
	if fire_cooldown > 0.0 or reload_timer > 0.0:
		return
	if clip_ammo <= 0:
		reload_timer = 1.3
		return
	var weapon: Dictionary = loadout.get("weapon", {})
	clip_ammo -= 1
	fire_cooldown = float(weapon.get("fire_rate", 0.25))
	if is_state_active("smart_core"):
		fire_cooldown *= 0.55
	if clip_ammo == 0:
		reload_timer = 1.3
	visuals.trigger_muzzle_flash()

# findTarget (HTML lines 3180-3234). Priority: live LOS > squad shared > own
# drifting memory > no target (fall through to the live player as the anchor
# caller-side). When LOS is acquired, update memory + broadcast so squadmates
# without LOS can piggyback. Memory drift grows with age so stale positions
# wander slightly (the "I thought I saw them over there" feel).
func _run_find_target() -> void:
	if not target or not target.is_alive():
		ai_has_target = false
		return
	var to_player := target.global_position - global_position
	var distance := to_player.length()
	var has_los := true
	if arena_map:
		has_los = arena_map.segment_is_clear(global_position, target.global_position, 12.0)

	if has_los:
		ai_memory_valid = true
		ai_memory_pos = target.global_position
		ai_memory_age = 0.0
		ai_target_pos = target.global_position
		ai_has_target = true
		_broadcast_shared_target(target.global_position)
		return

	# No LOS: try squadmate's broadcast first (7s window), then own memory
	# (5s window, with drift). If both miss, clear the target so the movement
	# code falls back to the live player as a last resort. _has_shared_target
	# gates the read so the subsequent assignment is typed Vector3.
	if _has_shared_target():
		ai_target_pos = _get_shared_target_pos()
		ai_has_target = true
		return

	if ai_memory_valid and BotAIMath.is_memory_valid(ai_memory_age):
		ai_target_pos = ai_memory_pos + BotAIMath.compute_memory_drift(ai_memory_age, ai_rng)
		ai_has_target = true
		return

	ai_has_target = false

# Write to the team's shared broadcast. The dictionary holds {pos, time_msec};
# time is monotonic msec so age checks don't wobble across frame-delta jitter.
func _broadcast_shared_target(pos: Vector3) -> void:
	_shared_target_by_team[TEAM_ENEMY] = {
		"pos": pos,
		"time_msec": Time.get_ticks_msec(),
	}

# True if a squadmate's broadcast exists AND is still within the 7s age window.
# Split from _get_shared_target_pos so the caller can sequence the check and
# the typed Vector3 read without a Variant-typed intermediate.
func _has_shared_target() -> bool:
	if not _shared_target_by_team.has(TEAM_ENEMY):
		return false
	var entry: Dictionary = _shared_target_by_team[TEAM_ENEMY]
	if not entry.has("pos"):
		return false
	var age_sec := float(Time.get_ticks_msec() - int(entry.get("time_msec", 0))) / 1000.0
	return BotAIMath.is_shared_target_valid(age_sec)

# Returns the broadcast position. Only valid when _has_shared_target() is
# true; on failure returns Vector3.ZERO, which should never reach the caller
# because the call is gated by _has_shared_target.
func _get_shared_target_pos() -> Vector3:
	if not _shared_target_by_team.has(TEAM_ENEMY):
		return Vector3.ZERO
	var entry: Dictionary = _shared_target_by_team[TEAM_ENEMY]
	return entry.get("pos", Vector3.ZERO)

# Clears the team-level broadcast dictionary. main.gd calls this from
# _begin_round so a stale player position from the previous round doesn't
# lead bots back to where the round-2 player has already left.
static func reset_shared_broadcasts() -> void:
	_shared_target_by_team.clear()

func _run_combat_decisions(distance: float, aim_dir: Vector3, forward: Vector3) -> void:
	var alignment := forward.dot(aim_dir)
	if core_meter >= 100.0 and _should_use_core(distance, alignment):
		if _try_activate_core(forward):
			return

	match loadout_key:
		"ION":
			if shield < max_shield * 0.45:
				if _try_activate_ability(1, forward):
					return
			if distance < 420.0:
				if _try_activate_ability(2, forward):
					return
			if distance < 2600.0 and alignment > 0.96:
				_try_activate_ability(0, forward)
		"SCORCH":
			if distance < 550.0 or shield < max_shield * 0.4:
				if _try_activate_ability(1, forward):
					return
			if distance > 360.0 and distance < 1200.0:
				if _try_activate_ability(0, forward):
					return
			if distance < 1100.0:
				_try_activate_ability(2, forward)
		"NORTHSTAR":
			if distance > 1250.0 or distance < 520.0:
				if _try_activate_ability(1, forward):
					return
			if distance > 650.0 and alignment > 0.9:
				if _try_activate_ability(0, forward):
					return
			if distance > 450.0 and distance < 1400.0:
				_try_activate_ability(2, forward)
		"RONIN":
			if distance < 900.0 and shield < max_shield * 0.55:
				if _try_activate_ability(1, forward):
					return
			if distance < 750.0 and alignment > 0.84:
				if _try_activate_ability(0, forward):
					return
			if distance > 1050.0 or distance < 320.0:
				_try_activate_ability(2, forward)
		"TONE":
			if distance < 2000.0:
				if _try_activate_ability(2, forward):
					return
			if distance < 2200.0 and alignment > 0.88:
				if _try_activate_ability(0, forward):
					return
			if shield < max_shield * 0.5 or distance < 700.0:
				_try_activate_ability(1, forward)
		"LEGION":
			if (distance > 1600.0 and legion_mode == "close") or (distance < 900.0 and legion_mode == "long"):
				if _try_activate_ability(2, forward):
					return
			if shield < max_shield * 0.5 or distance < 700.0:
				if _try_activate_ability(1, forward):
					return
			if distance > 900.0 and alignment > 0.96:
				_try_activate_ability(0, forward)
		"MONARCH":
			if clip_ammo < int(max_clip * 0.35) and float(ability_cooldowns[0]) > 2.0 and float(ability_cooldowns[1]) > 2.0:
				if _try_activate_ability(2, forward):
					return
			if distance < 900.0:
				if _try_activate_ability(1, forward):
					return
			if distance < 2200.0 and alignment > 0.84:
				_try_activate_ability(0, forward)

func _should_use_core(distance: float, alignment: float) -> bool:
	match loadout_key:
		"ION":
			return distance < 3200.0 and alignment > 0.95
		"SCORCH":
			return distance < 520.0
		"NORTHSTAR":
			return distance > 900.0
		"RONIN":
			return distance < 820.0
		"TONE":
			return distance < 2600.0 and alignment > 0.82
		"LEGION":
			return distance < 2600.0 and alignment > 0.82
		"MONARCH":
			return true
	return false

func _try_activate_ability(slot: int, forward: Vector3) -> bool:
	var abilities: Array = loadout.get("abilities", [])
	if slot >= abilities.size() or float(ability_cooldowns[slot]) > 0.0:
		return false

	var ability: Dictionary = abilities[slot]
	var ability_id := String(ability.get("id", ""))
	if ability_id.is_empty():
		return false

	var cooldown := float(ability.get("cooldown", 8.0)) * monarch_cooldown_mult
	var origin := global_position + forward * 36.0
	var consumed := true

	match ability_id:
		"vortex_shield":
			_set_state("vortex_shield", float(ability.get("duration", 3.0)))
		"thermal_shield":
			_set_state("thermal_shield", float(ability.get("duration", 4.0)))
		"afterburner":
			_set_state("afterburner", float(ability.get("duration", 3.0)))
		"sword_block":
			_set_state("sword_block", float(ability.get("duration", 3.0)))
		"phase_dash":
			_set_state("phase_dash", 0.22)
			velocity += forward * float(chassis.get("dash_speed", 700.0)) * 1.35
		"gun_shield":
			_set_state("gun_shield", float(ability.get("duration", 4.0)))
		"mode_switch":
			_toggle_legion_mode()
		"rearm":
			for index in range(ability_cooldowns.size()):
				if index != slot:
					ability_cooldowns[index] = 0.0
			reload_timer = 0.0
			clip_ammo = max_clip
		_:
			ability_triggered.emit(ability_id, loadout_key, self, origin, forward, TEAM_ENEMY)

	if consumed:
		ability_cooldowns[slot] = cooldown
	return consumed

func _try_activate_core(forward: Vector3) -> bool:
	var core: Dictionary = loadout.get("core", {})
	var core_id := String(core.get("id", ""))
	if core_id.is_empty() or core_meter < 100.0:
		return false

	core_meter = 0.0
	match core_id:
		"afterburner_core":
			_set_state("afterburner_core", float(core.get("duration", 5.0)))
		"sword_core":
			_set_state("sword_core", float(core.get("duration", 6.0)))
		"smart_core":
			_set_state("smart_core", float(core.get("duration", 8.0)))
		"upgrade_core":
			_apply_monarch_upgrade()
		_:
			core_triggered.emit(core_id, loadout_key, self, global_position + forward * 36.0, forward, TEAM_ENEMY)
	return true

func _tick_state_timers(delta: float) -> void:
	var to_clear: Array[String] = []
	for key in state_timers.keys():
		state_timers[key] = maxf(0.0, float(state_timers[key]) - delta)
		if float(state_timers[key]) <= 0.0:
			to_clear.append(String(key))
	for key in to_clear:
		state_timers.erase(key)

func _set_state(state_id: String, duration: float) -> void:
	state_timers[state_id] = maxf(float(state_timers.get(state_id, 0.0)), duration)

func _toggle_legion_mode() -> void:
	# Queue a pending mode and start the 1s transition timer instead of flipping
	# instantly (HTML last_ship_sailing.html:6798-6802). Matches the player-side
	# delay so bots spend the same vulnerable window humans do.
	legion_switch_timer = 1.0
	legion_pending_mode = "long" if legion_mode == "close" else "close"

func _tick_legion_switch(delta: float) -> void:
	if legion_switch_timer <= 0.0:
		return
	legion_switch_timer = maxf(0.0, legion_switch_timer - delta)
	if legion_switch_timer > 0.0:
		return
	if legion_pending_mode.is_empty():
		return
	var weapon: Dictionary = loadout.get("weapon", {})
	var ammo_pct := 1.0
	if max_clip > 0:
		ammo_pct = float(clip_ammo) / float(max_clip)
	if legion_pending_mode == "close":
		legion_mode = "close"
		weapon["range"] = 1500.0
		weapon["spread"] = 0.04
		weapon["fire_rate"] = 0.05
		weapon["damage"] = 85.0
		max_clip = 150
	else:
		legion_mode = "long"
		weapon["range"] = 3000.0
		weapon["spread"] = 0.005
		weapon["fire_rate"] = 0.08
		weapon["damage"] = 100.0
		max_clip = 100
	clip_ammo = int(round(ammo_pct * float(max_clip)))
	weapon["clip_size"] = max_clip
	loadout["weapon"] = weapon
	legion_pending_mode = ""

func _apply_monarch_upgrade() -> void:
	monarch_tier = min(monarch_tier + 1, 3)
	var weapon: Dictionary = loadout.get("weapon", {})
	match monarch_tier:
		1:
			monarch_arc_rounds = true
			max_clip = max(max_clip, 50)
			clip_ammo = min(max_clip, clip_ammo + 10)
			weapon["clip_size"] = max_clip
		2:
			max_shield = float(chassis.get("max_shield", 3500.0)) + 500.0
			shield = minf(max_shield, shield + 500.0)
			monarch_cooldown_mult = 0.7
		3:
			monarch_xo16_accel = true
			monarch_damage_mult = 1.25
			weapon["fire_rate"] = maxf(0.06, float(weapon.get("fire_rate", 0.09)) * 0.75)
	loadout["weapon"] = weapon

func _apply_bounds() -> void:
	var p := global_position
	var bounds: Vector3 = GameData.ARENA_EXTENTS

	if p.x < -bounds.x:
		p.x = -bounds.x
		velocity.x = maxf(0.0, velocity.x)
	elif p.x > bounds.x:
		p.x = bounds.x
		velocity.x = minf(0.0, velocity.x)

	if p.y < -bounds.y:
		p.y = -bounds.y
		velocity.y = maxf(0.0, velocity.y)
	elif p.y > bounds.y:
		p.y = bounds.y
		velocity.y = minf(0.0, velocity.y)

	if p.z < -bounds.z:
		p.z = -bounds.z
		velocity.z = maxf(0.0, velocity.z)
	elif p.z > bounds.z:
		p.z = bounds.z
		velocity.z = minf(0.0, velocity.z)

	global_position = p
