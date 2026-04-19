class_name PlayerShip
extends Node3D

const GameData = preload("res://scripts/game_data.gd")
const ShipVisuals = preload("res://scripts/ship_visuals.gd")
const ArenaMap = preload("res://scripts/arena_map.gd")
const Settings = preload("res://scripts/settings.gd")

const FIRST_PERSON_VIEW := true

# Doomed state: when hull drops to or below 15% of max, the ship enters a
# countdown (DOOMED_TIMER seconds). Reaching zero on the timer is fatal even
# if external damage stops. Matches HTML LSS.DOOMED_HEALTH_PCT = 0.15 and
# LSS.DOOMED_TIMER = 10 (last_ship_sailing.html line 701).
const DOOMED_HEALTH_PCT := 0.15
const DOOMED_TIMER := 10.0

signal primary_fired(origin: Vector3, direction: Vector3, loadout_key: String, weapon_data: Dictionary, source: Node3D, team: int)
signal ability_triggered(ability_id: String, loadout_key: String, source: Node3D, origin: Vector3, direction: Vector3, team: int)
# Emitted for every ability activation regardless of routing (local `_set_state`
# paths don't fire `ability_triggered`, which only covers networked abilities).
# `ability_name` is the human-readable loadout name; the HUD uses this for the
# cinematic edge-glow label.
signal ability_activated(ability_id: String, ability_name: String, slot: int)
signal core_triggered(core_id: String, loadout_key: String, source: Node3D, origin: Vector3, direction: Vector3, team: int)
signal loadout_changed(loadout_key: String)
# killer_loadout_key = attacker's loadout (or "" if environmental / unknown);
# victim_loadout_key = this ship's loadout. Emitted once per death.
signal destroyed(killer_loadout_key: String, victim_loadout_key: String)
# Emitted AFTER health/shield deduction but regardless of whether it killed the
# ship. `amount` is the raw damage pre-absorption; `ratio` is amount/max_health
# already clamped to [0, 1] (so listeners don't need player config). Use for
# HUD effects (damage vignette, hit-marker audio). Fires even on fatal hits.
signal damage_taken(amount: float, ratio: float, hit_point: Vector3)

const TEAM_PLAYER := 0

var loadout_key := "ION"
var loadout_keys: PackedStringArray = GameData.get_loadout_keys()
var loadout_index := 0

var loadout: Dictionary = {}
var chassis: Dictionary = {}
var signature: Dictionary = {}
var velocity := Vector3.ZERO
var pitch := 0.0
var yaw := 0.0

var fire_cooldown := 0.0
var reload_timer := 0.0
var clip_ammo := 0
var max_clip := 0
var dash_charges := 0
var dash_recharge_timer := 0.0
var mouse_sensitivity := 0.0024
var max_health := 0.0
var health := 0.0
var max_shield := 0.0
var shield := 0.0
var alive := true
# Doomed state: entered when hull/max_health ≤ DOOMED_HEALTH_PCT. A
# persistent red vignette + "HULL CRITICAL" banner appear; shield no longer
# regenerates; doom_timer counts down to fatal. Reset on respawn.
var doomed := false
var doom_timer := 0.0
var respawn_timer := 0.0
var spawn_point := Vector3(0, 0, 720)
var ability_cooldowns := [0.0, 0.0, 0.0]
var state_timers: Dictionary = {}
var core_meter := 0.0
var monarch_tier := 0
var monarch_damage_mult := 1.0
var monarch_cooldown_mult := 1.0
var monarch_bonus_shield := 0.0
var monarch_arc_rounds := false
var monarch_missile_racks := false
var monarch_xo16_accel := false
var legion_mode := "close"
# LEGION Mode Switch: 1s transition delay before the pending mode activates
# (HTML last_ship_sailing.html:7699-7724). During the window the ship keeps
# firing the previous weapon profile and the HUD shows "SWITCHING".
var legion_switch_timer := 0.0
var legion_pending_mode := ""
# LEGION Power Shot: 1s charge window before firing; the charged shot's
# behaviour depends on legion_mode at the moment it releases.
var power_shot_charging := false
var power_shot_charge := 0.0
# TONE lock-on: player-side dictionary keyed by EnemyShip instance id, max 3
# per target. Tracker Rockets consume only full (>=3) locks; partial locks
# persist across volleys. enemy_tone_locks tracks the reverse (TONE bots
# building locks on the player from hits).
var tone_locks: Dictionary = {}
var tone_locked_target: EnemyShip = null
var enemy_tone_locks: Dictionary = {}
var enemy_tone_lock_max := 0
# Stasis state: set by main.gd when the player walks into a stasis pickup.
# While in_stasis, velocity is zeroed every frame and shield recharges linearly
# from its current level to max_shield over stasis_timer's full duration.
# pre_stasis_velocity is captured at entry so a future design pass could
# restore it on exit; HTML last_ship_sailing.html:9524-9558 zeroes and leaves
# the player at rest, which this port matches.
var in_stasis := false
var stasis_timer := 0.0
var stasis_duration := 0.0
var pre_stasis_velocity := Vector3.ZERO
var match_state := "warmup"
var arena_map: ArenaMap
var look_input := Vector2.ZERO
var camera_base_offset := Vector3(0, 9, 0)
var camera_recoil := 0.0
var camera_shake := 0.0
var camera_shake_offset := Vector2.ZERO
var dash_feedback := 0.0
var muzzle_flash_timer := 0.0
var muzzle_flash_side := 0
var gun_recoil_l := 0.0
var gun_recoil_r := 0.0
var shot_toggle := 0

var pitch_pivot: Node3D
var camera_mount: Node3D
var camera: Camera3D
var visuals: ShipVisuals

func _ready() -> void:
	name = "PlayerShip"

	pitch_pivot = Node3D.new()
	pitch_pivot.name = "PitchPivot"
	add_child(pitch_pivot)

	camera_mount = Node3D.new()
	camera_mount.position = camera_base_offset
	pitch_pivot.add_child(camera_mount)

	camera = Camera3D.new()
	camera.current = true
	camera.fov = 76.0
	camera.near = 0.1
	camera_mount.add_child(camera)

	visuals = ShipVisuals.new()
	visuals.name = "Visuals"
	add_child(visuals)

	set_loadout_by_index(0)

func _unhandled_input(event: InputEvent) -> void:
	if Input.get_mouse_mode() != Input.MOUSE_MODE_CAPTURED:
		return

	if event is InputEventMouseMotion:
		# Read mouse sensitivity from Settings every frame so the settings
		# overlay's slider takes effect without a scene reload.
		var sens := Settings.mouse_sensitivity
		yaw -= event.relative.x * sens
		pitch = clampf(pitch - event.relative.y * sens, deg_to_rad(-50.0), deg_to_rad(28.0))
		look_input = Vector2(event.relative.x, event.relative.y)
		rotation.y = yaw
		pitch_pivot.rotation.x = pitch

func _physics_process(delta: float) -> void:
	if not alive:
		_update_feedback(delta, 0.0, Vector3.ZERO)
		return

	# Doomed countdown: ticks regardless of match_state so holding the round-end
	# banner past your critical window still kills you (matches HTML line 5896
	# which runs inside the main update, unconditional on playing state).
	if doomed:
		doom_timer = maxf(0.0, doom_timer - delta)
		if doom_timer <= 0.0:
			_apply_doomed_death()
			_update_feedback(delta, 0.0, Vector3.ZERO)
			return

	for index in range(ability_cooldowns.size()):
		ability_cooldowns[index] = maxf(0.0, float(ability_cooldowns[index]) - delta)
	_tick_state_timers(delta)
	_tick_legion_switch(delta)
	_tick_power_shot(delta)
	_tick_stasis(delta)

	# Gamepad right-stick look (applied only while playing and while mouse is
	# captured, so the settings overlay can't fight the stick for the camera).
	if Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED and match_state == "playing":
		var stick := Settings.read_look_stick(delta)
		if stick.length_squared() > 0.00001:
			yaw -= stick.x
			pitch = clampf(pitch - stick.y, deg_to_rad(-50.0), deg_to_rad(28.0))
			look_input = Vector2(stick.x, stick.y) * 60.0
			rotation.y = yaw
			pitch_pivot.rotation.x = pitch

	if Input.is_action_just_pressed("next_loadout"):
		set_loadout_by_index((loadout_index + 1) % loadout_keys.size())
	if Input.is_action_just_pressed("prev_loadout"):
		set_loadout_by_index(posmod(loadout_index - 1, loadout_keys.size()))
	if match_state != "playing":
		velocity = velocity.move_toward(Vector3.ZERO, float(chassis.get("deceleration", 600.0)) * delta)
		_update_feedback(delta, 0.0, Vector3.ZERO)
		visuals.update_ship_visuals(delta, 0.0, Vector3.ZERO, look_input, 0.0)
		return
	# Stasis lockout: velocity is pinned to zero inside _tick_stasis, and
	# movement / fire / ability input are ignored for the duration. The camera,
	# look axes, and state timers keep running so the player can still observe
	# and react visually (HTML last_ship_sailing.html:9535-9558).
	if in_stasis:
		velocity = Vector3.ZERO
		_update_feedback(delta, 0.0, Vector3.ZERO)
		visuals.update_ship_visuals(delta, 0.0, Vector3.ZERO, look_input, 0.0)
		return
	if Input.is_action_just_pressed("ability_1"):
		_try_activate_ability(0)
	if Input.is_action_just_pressed("ability_2"):
		_try_activate_ability(1)
	if Input.is_action_just_pressed("ability_3"):
		_try_activate_ability(2)
	if Input.is_action_just_pressed("core_ability"):
		_try_activate_core()

	fire_cooldown = maxf(0.0, fire_cooldown - delta)
	if reload_timer > 0.0:
		reload_timer = maxf(0.0, reload_timer - delta)
		if reload_timer == 0.0:
			clip_ammo = max_clip

	if dash_recharge_timer > 0.0:
		dash_recharge_timer = maxf(0.0, dash_recharge_timer - delta)
		if dash_recharge_timer == 0.0 and dash_charges < int(chassis.get("max_dashes", 1)):
			dash_charges += 1
			if dash_charges < int(chassis.get("max_dashes", 1)):
				dash_recharge_timer = float(chassis.get("dash_cooldown", 4.0))

	if Input.is_action_just_pressed("reload") and clip_ammo < max_clip and reload_timer == 0.0:
		reload_timer = 1.1

	var forward: Vector3 = -pitch_pivot.global_basis.z
	var right: Vector3 = global_basis.x
	var up := Vector3.UP
	var move_speed_multiplier := 1.0
	if is_state_active("afterburner"):
		move_speed_multiplier *= 1.4
	if is_state_active("afterburner_core"):
		move_speed_multiplier *= 1.75
	if is_state_active("sword_core"):
		move_speed_multiplier *= 1.15

	var desired_velocity := Vector3.ZERO
	if Input.is_action_pressed("move_forward"):
		desired_velocity += forward * float(chassis.get("flight_speed", 350.0)) * move_speed_multiplier
	if Input.is_action_pressed("move_backward"):
		desired_velocity -= forward * float(chassis.get("flight_speed", 350.0)) * 0.6 * move_speed_multiplier
	if Input.is_action_pressed("move_left"):
		desired_velocity -= right * float(chassis.get("strafe_speed", 280.0)) * move_speed_multiplier
	if Input.is_action_pressed("move_right"):
		desired_velocity += right * float(chassis.get("strafe_speed", 280.0)) * move_speed_multiplier
	if Input.is_action_pressed("move_up"):
		desired_velocity += up * float(chassis.get("vertical_speed", 250.0)) * move_speed_multiplier
	if Input.is_action_pressed("move_down"):
		desired_velocity -= up * float(chassis.get("vertical_speed", 250.0)) * move_speed_multiplier

	if desired_velocity.length_squared() > 0.001:
		velocity = velocity.move_toward(desired_velocity, float(chassis.get("acceleration", 800.0)) * delta)
	else:
		velocity = velocity.move_toward(Vector3.ZERO, float(chassis.get("deceleration", 600.0)) * delta)

	var max_speed := float(chassis.get("flight_speed", 350.0)) * move_speed_multiplier
	if velocity.length() > max_speed:
		velocity = velocity.normalized() * max_speed

	if Input.is_action_just_pressed("dash") and dash_charges > 0:
		velocity += forward * float(chassis.get("dash_speed", 700.0))
		dash_charges -= 1
		dash_feedback = 1.0
		_add_screen_shake(0.9)
		if dash_recharge_timer == 0.0:
			dash_recharge_timer = float(chassis.get("dash_cooldown", 4.0))
		# HTML line 11189-11194: dash SFX fires only when a charge was actually
		# consumed. The `hadCharges` guard there is equivalent to the dash_charges > 0
		# check we already gate the whole block on.
		_play_audio("dash")

	global_position += velocity * delta
	if arena_map:
		global_position = arena_map.constrain_point(global_position, get_collision_radius() * 0.6)
	else:
		_apply_bounds()

	if Input.is_action_pressed("fire_primary"):
		_attempt_fire(forward)

	var local_velocity: Vector3 = global_basis.inverse() * velocity
	var speed_ratio := clampf(velocity.length() / maxf(1.0, float(chassis.get("flight_speed", 350.0))), 0.0, 1.6)
	_update_feedback(delta, speed_ratio, local_velocity)
	var boost_amount := dash_feedback
	if is_state_active("afterburner") or is_state_active("afterburner_core"):
		boost_amount = maxf(boost_amount, 0.45)
	visuals.update_ship_visuals(delta, speed_ratio, local_velocity, look_input, boost_amount)

func set_loadout_by_index(index: int) -> void:
	loadout_index = index
	loadout_key = String(loadout_keys[index])
	loadout = GameData.get_loadout(loadout_key)
	chassis = GameData.get_chassis_for_loadout(loadout_key)
	signature = GameData.get_signature(loadout_key)

	var weapon: Dictionary = loadout.get("weapon", {})
	max_clip = int(weapon.get("clip_size", 12))
	clip_ammo = max_clip
	max_health = float(chassis.get("max_health", 10000.0))
	health = max_health
	max_shield = float(chassis.get("max_shield", 3000.0))
	shield = max_shield
	alive = true
	doomed = false
	doom_timer = 0.0
	respawn_timer = 0.0
	reload_timer = 0.0
	fire_cooldown = 0.0
	velocity = Vector3.ZERO
	ability_cooldowns = [0.0, 0.0, 0.0]
	state_timers.clear()
	core_meter = 0.0
	dash_charges = int(chassis.get("max_dashes", 1))
	dash_recharge_timer = 0.0
	monarch_tier = 0
	monarch_damage_mult = 1.0
	monarch_cooldown_mult = 1.0
	monarch_bonus_shield = 0.0
	monarch_arc_rounds = false
	monarch_missile_racks = false
	monarch_xo16_accel = false
	legion_mode = "close"
	legion_switch_timer = 0.0
	legion_pending_mode = ""
	power_shot_charging = false
	power_shot_charge = 0.0
	tone_locks.clear()
	tone_locked_target = null
	enemy_tone_locks.clear()
	enemy_tone_lock_max = 0
	in_stasis = false
	stasis_timer = 0.0
	stasis_duration = 0.0
	pre_stasis_velocity = Vector3.ZERO
	_update_camera_base_offset()

	visuals.configure_ship(loadout_key, chassis, signature)
	_sync_local_view_mode()
	loadout_changed.emit(loadout_key)

func get_status() -> Dictionary:
	return {
		"loadout_name": String(loadout.get("name", loadout_key)),
		"class_name": String(loadout.get("class_name", "Prototype")),
		"weapon_name": String(loadout.get("weapon", {}).get("name", "Weapon")),
		"weapon_mode": legion_mode if loadout_key == "LEGION" else String(loadout.get("weapon", {}).get("mode", "hitscan")),
		"chassis_name": String(chassis.get("name", "Chassis")),
		"clip_ammo": clip_ammo,
		"max_clip": max_clip,
		"speed": velocity.length(),
		"dash_charges": dash_charges,
		"health": health,
		"max_health": max_health,
		"shield": shield,
		"max_shield": max_shield,
		"alive": alive,
		"doomed": doomed,
		"doom_timer": doom_timer,
		"in_stasis": in_stasis,
		"stasis_timer": stasis_timer,
		"stasis_duration": stasis_duration,
		"ability_names": _get_ability_names(),
		"ability_cooldowns": ability_cooldowns.duplicate(),
		"core_name": String(loadout.get("core", {}).get("name", "Core")),
		"core_meter": core_meter,
		"match_state": match_state
	}

func apply_damage(amount: float, hit_point: Vector3, source_loadout_key: String) -> void:
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

	# Capture post-mitigation, pre-shield damage for HUD listeners. Shield is
	# part of the ship's wholeness (it's consumed either way), so we report the
	# full amount that landed on the ship, not just what leaked through.
	var inflicted := amount

	if shield > 0.0:
		visuals.pulse_shield()
		var shield_damage := minf(shield, amount)
		shield -= shield_damage
		amount -= shield_damage

	if amount > 0.0:
		health -= amount

	# Enter doomed state when hull crosses the 15% threshold (HTML line 5699).
	# Guarded by !doomed so the timer isn't reset by further hits; latches until
	# death or respawn.
	if not doomed and health > 0.0 and health / maxf(1.0, max_health) <= DOOMED_HEALTH_PCT:
		doomed = true
		doom_timer = DOOMED_TIMER

	if health <= 0.0:
		alive = false
		doomed = false
		doom_timer = 0.0
		respawn_timer = 2.5
		velocity = Vector3.ZERO
		visuals.set_ship_enabled(false)
		# Death SFX before destroyed.emit so listeners (kill feed, revenge
		# tracking) don't race the sound. HTML 11198 fires death on playerDie().
		_play_audio("death")
		destroyed.emit(source_loadout_key, loadout_key)
	else:
		camera_recoil = minf(camera_recoil + amount / maxf(1.0, max_health) * 5.0, 0.45)
		_add_screen_shake(minf(1.8, 0.35 + amount / 1600.0))
		# Damage SFX fires only on non-fatal hits; fatal hits play "death"
		# instead (HTML 11197 gates damage SFX on survival). `inflicted` is the
		# post-mitigation amount that landed on the ship (shield + hull).
		if inflicted > 0.0:
			_play_audio("damage")

	var ratio := clampf(inflicted / maxf(1.0, max_health), 0.0, 1.0)
	# hit_point = attacker's world position (or projectile impact). HUD listeners
	# use it to drive the directional damage overlay (HTML 10292-10337).
	damage_taken.emit(inflicted, ratio, hit_point)

# Fired when the doom_timer reaches zero. Equivalent to a fatal apply_damage
# with no attributed killer; the ship dies, destroyed.emit() fires so
# kill-feed / scoreboard updates still run, and the respawn timer starts.
func _apply_doomed_death() -> void:
	if not alive:
		return
	health = 0.0
	alive = false
	doomed = false
	doom_timer = 0.0
	respawn_timer = 2.5
	velocity = Vector3.ZERO
	visuals.set_ship_enabled(false)
	# Death SFX on the environmental-kill path too; the sound is the same
	# regardless of attribution.
	_play_audio("death")
	# Empty killer key matches the HTML playerDie(null) path for environmental
	# / timer kills (no attacker to credit, no revenge target recorded).
	destroyed.emit("", loadout_key)

func is_alive() -> bool:
	return alive

func is_doomed() -> bool:
	return doomed and alive

func get_doom_timer() -> float:
	return doom_timer

func get_team() -> int:
	return TEAM_PLAYER

func get_collision_radius() -> float:
	# Match HTML wall-collision sphere (last_ship_sailing.html:5904):
	# `collRadius = ch.hullLength * 0.4`.
	return float(chassis.get("hull_length", 100.0)) * 0.4

func set_arena_map(new_arena_map: ArenaMap) -> void:
	arena_map = new_arena_map

func set_match_state(new_state: String) -> void:
	match_state = new_state

func reset_for_round(position: Vector3 = spawn_point) -> void:
	spawn_point = position
	_respawn()

func get_forward() -> Vector3:
	return -pitch_pivot.global_basis.z

func get_muzzle_origin() -> Vector3:
	return global_position + get_forward() * 36.0

func is_state_active(state_id: String) -> bool:
	return float(state_timers.get(state_id, 0.0)) > 0.0

func add_core_charge(amount: float) -> void:
	core_meter = clampf(core_meter + amount / 100.0, 0.0, 100.0)

func restore_shield(amount: float) -> void:
	shield = minf(max_shield, shield + amount)

# Called by main.gd when the player walks into a stasis pickup. Locks the ship
# immobile for `duration` seconds and slowly refills shield over that window
# (HTML last_ship_sailing.html:9524-9558). Re-entering while already in stasis
# is a no-op so overlapping pickups don't double-stack the timer.
func enter_stasis(duration: float) -> void:
	if not alive or in_stasis or duration <= 0.0:
		return
	in_stasis = true
	stasis_duration = duration
	stasis_timer = duration
	pre_stasis_velocity = velocity
	velocity = Vector3.ZERO
	# Stasis lock-in SFX (HTML 11207). Only fires on genuine entry; the
	# re-entry guard above ensures overlapping pickups don't restack the sound.
	_play_audio("stasis")

# Clear the stasis lock early. Used by respawn / round reset; exits the state
# without forcing shield to full (the natural timer path guarantees full; this
# path is for involuntary exits).
func exit_stasis() -> void:
	in_stasis = false
	stasis_timer = 0.0
	stasis_duration = 0.0
	pre_stasis_velocity = Vector3.ZERO

func _tick_stasis(delta: float) -> void:
	if not in_stasis:
		return
	# Linear shield recharge: maxShield / duration per second, matching HTML
	# line 9542-9543. The final `shield = maxShield` at exit (below) guarantees
	# a full top-off even if the player started with partial shield.
	var recharge_per_sec := max_shield / maxf(0.0001, stasis_duration)
	shield = minf(max_shield, shield + recharge_per_sec * delta)
	# Force immobility every frame; any _physics_process movement above this
	# tick was already gated, but this guards against external force sources
	# (ramming, knockback) still landing on the frozen ship.
	velocity = Vector3.ZERO
	stasis_timer = maxf(0.0, stasis_timer - delta)
	if stasis_timer <= 0.0:
		in_stasis = false
		stasis_duration = 0.0
		shield = max_shield
		pre_stasis_velocity = Vector3.ZERO

# Velocity helpers used by main.gd's trap-field ticks: scale_velocity is called
# by the incendiary_gas slow effect (multiplicative drag per frame), set_velocity
# is called by the tether_trap root (hard zero each frame while rooted).
func set_velocity(new_velocity: Vector3) -> void:
	velocity = new_velocity

func scale_velocity(factor: float) -> void:
	velocity *= factor

func get_damage_multiplier() -> float:
	var multiplier := monarch_damage_mult
	if is_state_active("sword_core"):
		multiplier *= 1.2
	return multiplier

func _update_camera_base_offset() -> void:
	match String(chassis.get("name", "Corvette")):
		"Frigate":
			camera_base_offset = Vector3(0, 7, 0)
		"Dreadnought":
			camera_base_offset = Vector3(0, 12, 2)
		_:
			camera_base_offset = Vector3(0, 9, 0)

func _sync_local_view_mode() -> void:
	visuals.set_ship_enabled(true)
	visuals.visible = not FIRST_PERSON_VIEW
	camera_mount.position = camera_base_offset

func _add_screen_shake(amount: float) -> void:
	camera_shake = minf(camera_shake + amount, 4.0)

# Public shake trigger for external events (explosions, nearby blasts,
# projectile detonations). Mirrors HTML triggerScreenShake() (line 10276).
# Amount is in the same 0..4 scale as _add_screen_shake, where 4.0 is cap.
func add_screen_shake(amount: float) -> void:
	if not alive:
		return
	_add_screen_shake(amount)

# Null-safe dispatcher into the Audio autoload. In headless tests the autoload
# may not be installed (scripts/tests/ spin up a bare SceneTree); we skip the
# call silently so physics/gameplay paths keep working.
func _play_audio(type: String) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	if tree == null:
		return
	var root: Window = tree.root
	if root != null and root.has_node("Audio"):
		root.get_node("Audio").play_sound(type)

# Weapon-fire routing. The Audio autoload classifies the active weapon by mode,
# fire-rate, and flags (homing/salvo) to pick one of 5 fire SFX (hitscan,
# railgun, minigun, projectile, spread).
func _play_weapon_fire_audio(weapon: Dictionary) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	if tree == null:
		return
	var root: Window = tree.root
	if root != null and root.has_node("Audio"):
		root.get_node("Audio").play_weapon_fire(
			String(weapon.get("mode", "hitscan")),
			float(weapon.get("fire_rate", 0.25)),
			bool(weapon.get("homing", false)),
			bool(weapon.get("salvo", false))
		)

func _apply_fire_feedback(weapon: Dictionary) -> void:
	var weapon_mode := String(weapon.get("mode", "hitscan"))
	var fire_rate := float(weapon.get("fire_rate", 0.25))
	var recoil_amount := 0.005
	var shake_amount := 0.3
	if weapon_mode == "spread":
		recoil_amount = 0.015
		shake_amount = 1.5
	elif fire_rate > 0.5:
		recoil_amount = 0.025
		shake_amount = 1.0

	pitch = clampf(pitch - recoil_amount, deg_to_rad(-50.0), deg_to_rad(28.0))
	pitch_pivot.rotation.x = pitch
	camera_recoil = minf(camera_recoil + recoil_amount * 18.0, 0.55)
	_add_screen_shake(shake_amount)

func _update_feedback(delta: float, speed_ratio: float, local_velocity: Vector3) -> void:
	look_input = look_input.lerp(Vector2.ZERO, clampf(delta * 10.0, 0.0, 1.0))
	camera_recoil = lerpf(camera_recoil, 0.0, delta * 10.0)
	dash_feedback = lerpf(dash_feedback, 0.0, delta * 4.0)
	muzzle_flash_timer = maxf(0.0, muzzle_flash_timer - delta * 12.5)
	gun_recoil_l = maxf(0.0, gun_recoil_l - delta * 12.0)
	gun_recoil_r = maxf(0.0, gun_recoil_r - delta * 12.0)

	if camera_shake > 0.02:
		camera_shake_offset = Vector2(
			randf_range(-1.0, 1.0) * camera_shake,
			randf_range(-1.0, 1.0) * camera_shake
		)
		camera_shake = lerpf(camera_shake, 0.0, delta * 12.0)
	else:
		camera_shake = 0.0
		camera_shake_offset = Vector2.ZERO

	var target_fov := 76.0 + speed_ratio * 6.0 + dash_feedback * 4.0
	if is_state_active("afterburner") or is_state_active("afterburner_core"):
		target_fov += 2.5
	camera.fov = lerpf(camera.fov, target_fov, delta * 5.0)

	var strafe_speed := maxf(1.0, float(chassis.get("strafe_speed", 280.0)))
	var strafe_ratio := clampf(local_velocity.x / strafe_speed, -1.0, 1.0)
	var target_roll := strafe_ratio * -deg_to_rad(4.5) - clampf(look_input.x * 0.0022, -deg_to_rad(1.8), deg_to_rad(1.8))
	camera.rotation.z = lerpf(camera.rotation.z, target_roll + camera_shake_offset.x * 0.01, delta * 8.0)

	var target_offset := camera_base_offset + Vector3(
		camera_shake_offset.x * 0.35 - local_velocity.x * 0.01,
		camera_shake_offset.y * 0.25 - local_velocity.y * 0.01 + dash_feedback * 0.5,
		camera_recoil * 24.0 + dash_feedback * 8.0 + speed_ratio * 1.5
	)
	camera_mount.position = camera_mount.position.lerp(target_offset, delta * 10.0)

func _attempt_fire(forward: Vector3) -> void:
	if fire_cooldown > 0.0 or reload_timer > 0.0:
		return

	if clip_ammo <= 0:
		reload_timer = 1.1
		# Empty-click reload trigger; matches HTML 11165-11170 where the dry
		# click launches the reload SFX from the same zero-ammo branch.
		_play_audio("reload")
		return

	var weapon: Dictionary = loadout.get("weapon", {})
	clip_ammo -= 1
	fire_cooldown = float(weapon.get("fire_rate", 0.25))
	if is_state_active("smart_core"):
		fire_cooldown *= 0.55

	if clip_ammo == 0:
		reload_timer = 1.1
		_play_audio("reload")

	var muzzle_origin := global_position + forward * 36.0
	_apply_fire_feedback(weapon)
	# Fire SFX after feedback so the routing dict matches the shot that was
	# actually committed (recoil/shake came from the same weapon record).
	_play_weapon_fire_audio(weapon)
	muzzle_flash_timer = 0.08
	muzzle_flash_side = shot_toggle % 2
	if muzzle_flash_side == 0:
		gun_recoil_l = 1.0
	else:
		gun_recoil_r = 1.0
	shot_toggle += 1
	visuals.trigger_muzzle_flash()
	primary_fired.emit(muzzle_origin, forward.normalized(), loadout_key, weapon.duplicate(true), self, TEAM_PLAYER)

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

func _respawn() -> void:
	alive = true
	doomed = false
	doom_timer = 0.0
	respawn_timer = 0.0
	health = max_health
	shield = max_shield
	clip_ammo = max_clip
	reload_timer = 0.0
	fire_cooldown = 0.0
	dash_charges = int(chassis.get("max_dashes", 1))
	dash_recharge_timer = 0.0
	velocity = Vector3.ZERO
	global_position = spawn_point
	camera_recoil = 0.0
	camera_shake = 0.0
	camera_shake_offset = Vector2.ZERO
	dash_feedback = 0.0
	muzzle_flash_timer = 0.0
	muzzle_flash_side = 0
	gun_recoil_l = 0.0
	gun_recoil_r = 0.0
	shot_toggle = 0
	camera.rotation.z = 0.0
	camera.fov = 76.0
	_sync_local_view_mode()
	state_timers.clear()
	ability_cooldowns = [0.0, 0.0, 0.0]
	in_stasis = false
	stasis_timer = 0.0
	stasis_duration = 0.0
	pre_stasis_velocity = Vector3.ZERO

func _try_activate_ability(slot: int) -> void:
	var abilities: Array = loadout.get("abilities", [])
	if slot >= abilities.size() or float(ability_cooldowns[slot]) > 0.0:
		return

	var ability: Dictionary = abilities[slot]
	var ability_id := String(ability.get("id", ""))
	if ability_id.is_empty():
		return

	var origin := get_muzzle_origin()
	var forward := get_forward()
	var cooldown := float(ability.get("cooldown", 8.0)) * monarch_cooldown_mult

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
			dash_charges = int(chassis.get("max_dashes", 1))
			dash_recharge_timer = 0.0
		_:
			ability_triggered.emit(ability_id, loadout_key, self, origin, forward, TEAM_PLAYER)

	ability_cooldowns[slot] = cooldown
	# Ability SFX after successful activation. Mirrors HTML 11186; the ability
	# triggered the match above, so cooldown has been committed.
	_play_audio("ability")
	# Fire the cinematic hook AFTER routing so the HUD only flashes for
	# abilities that actually activated (cooldown + empty-id checks above
	# early-return before we get here).
	var ability_name := String(ability.get("name", ability_id))
	ability_activated.emit(ability_id, ability_name, slot)

func _try_activate_core() -> void:
	var core: Dictionary = loadout.get("core", {})
	var core_id := String(core.get("id", ""))
	if core_id.is_empty() or core_meter < 100.0:
		return

	core_meter = 0.0
	# Core SFX after the meter-drain guard. HTML 11185 fires on discharge.
	_play_audio("core")
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
			core_triggered.emit(core_id, loadout_key, self, get_muzzle_origin(), get_forward(), TEAM_PLAYER)

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
	# instantly (HTML last_ship_sailing.html:6798-6802). The actual weapon profile
	# swap happens in _tick_legion_switch when the timer reaches zero.
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
	# Scale ammo proportionally between modes so a switch mid-clip doesn't
	# give a free reload (HTML last_ship_sailing.html:7705-7722).
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

func start_power_shot_charge() -> void:
	# LEGION Power Shot begins a 1s charge; the charge completes in
	# _tick_power_shot which emits power_shot_released and resets the charge.
	power_shot_charging = true
	power_shot_charge = 0.0

func _tick_power_shot(delta: float) -> void:
	if not power_shot_charging:
		return
	power_shot_charge = minf(1.0, power_shot_charge + delta)
	if power_shot_charge >= 1.0:
		power_shot_charging = false
		power_shot_charge = 0.0
		ability_triggered.emit("power_shot_release", loadout_key, self, get_muzzle_origin(), get_forward(), TEAM_PLAYER)

func _apply_monarch_upgrade() -> void:
	monarch_tier = min(monarch_tier + 1, 3)
	var weapon: Dictionary = loadout.get("weapon", {})
	match monarch_tier:
		1:
			# Tier 1: Arc Rounds + extra clip capacity (HTML 6934-6938).
			# monarch_arc_rounds is consumed in main.gd when the attacker
			# resolves damage against a target that still has shield.
			monarch_arc_rounds = true
			max_clip = max(max_clip, 50)
			clip_ammo = min(max_clip, clip_ammo + 10)
			weapon["clip_size"] = max_clip
		2:
			monarch_bonus_shield = 500.0
			max_shield = float(chassis.get("max_shield", 3500.0)) + monarch_bonus_shield
			shield = minf(max_shield, shield + 500.0)
			monarch_cooldown_mult = 0.7
		3:
			# Tier 3: XO-16 Accelerator (HTML 6946-6950). The flag exposes the
			# tier state to HUD / analytics; damage and fire-rate effects are
			# applied below and consumed via get_damage_multiplier / weapon.
			monarch_xo16_accel = true
			monarch_damage_mult = 1.25
			weapon["fire_rate"] = maxf(0.06, float(weapon.get("fire_rate", 0.09)) * 0.75)
	loadout["weapon"] = weapon

func clear_tone_lock(enemy_id: int) -> void:
	# Called from main.gd when an enemy dies; purge both our locks on them and
	# locked_target refs that point to the dead enemy. Mirrors HTML 3427-3429.
	tone_locks.erase(enemy_id)
	if tone_locked_target != null and tone_locked_target.get_instance_id() == enemy_id:
		tone_locked_target = null
	enemy_tone_locks.erase(enemy_id)
	_recompute_enemy_tone_lock_max()

func add_tone_lock(enemy: EnemyShip, amount: int = 1) -> int:
	# Build up to 3 locks on a single enemy; return the new count. Called by
	# the Sonar Lock ability handler in main.gd for each enemy inside the cone.
	if enemy == null or not is_instance_valid(enemy):
		return 0
	var enemy_id := enemy.get_instance_id()
	var current := int(tone_locks.get(enemy_id, 0))
	var next := clampi(current + amount, 0, 3)
	tone_locks[enemy_id] = next
	if next >= 3:
		tone_locked_target = enemy
	return next

func consume_full_tone_locks() -> Array:
	# Return the list of enemies with 3+ locks and strip those entries so the
	# Tracker Rockets volley gets a clean shopping list. Partial locks survive.
	var locked_targets: Array = []
	for key in tone_locks.keys():
		if int(tone_locks[key]) >= 3:
			locked_targets.append(key)
	for key in locked_targets:
		tone_locks.erase(key)
	tone_locked_target = null
	return locked_targets

func register_enemy_tone_lock(enemy: EnemyShip) -> void:
	# TONE bots build lock stacks on the player with each hit (HTML 3386-3390).
	# We key by the attacker's instance id, not loadout_key, so each TONE bot
	# tracks its own lock independently.
	if enemy == null or not is_instance_valid(enemy):
		return
	var enemy_id := enemy.get_instance_id()
	var current := int(enemy_tone_locks.get(enemy_id, 0))
	enemy_tone_locks[enemy_id] = clampi(current + 1, 0, 3)
	_recompute_enemy_tone_lock_max()

func _recompute_enemy_tone_lock_max() -> void:
	var running_max := 0
	for key in enemy_tone_locks.keys():
		running_max = max(running_max, int(enemy_tone_locks[key]))
	enemy_tone_lock_max = running_max

func _get_ability_names() -> Array:
	var names: Array = []
	for ability in loadout.get("abilities", []):
		names.append(String(ability.get("name", "Ability")))
	return names
