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
signal core_triggered(core_id: String, loadout_key: String, source: Node3D, origin: Vector3, direction: Vector3, team: int)
signal loadout_changed(loadout_key: String)
# killer_loadout_key = attacker's loadout (or "" if environmental / unknown);
# victim_loadout_key = this ship's loadout. Emitted once per death.
signal destroyed(killer_loadout_key: String, victim_loadout_key: String)
# Emitted AFTER health/shield deduction but regardless of whether it killed the
# ship. `amount` is the raw damage pre-absorption; `ratio` is amount/max_health
# already clamped to [0, 1] (so listeners don't need player config). Use for
# HUD effects (damage vignette, hit-marker audio). Fires even on fatal hits.
signal damage_taken(amount: float, ratio: float)

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
var legion_mode := "close"
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
	legion_mode = "close"
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
		"ability_names": _get_ability_names(),
		"ability_cooldowns": ability_cooldowns.duplicate(),
		"core_name": String(loadout.get("core", {}).get("name", "Core")),
		"core_meter": core_meter,
		"match_state": match_state
	}

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
		destroyed.emit(source_loadout_key, loadout_key)
	else:
		camera_recoil = minf(camera_recoil + amount / maxf(1.0, max_health) * 5.0, 0.45)
		_add_screen_shake(minf(1.8, 0.35 + amount / 1600.0))

	var ratio := clampf(inflicted / maxf(1.0, max_health), 0.0, 1.0)
	damage_taken.emit(inflicted, ratio)

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
	return maxf(float(chassis.get("hull_width", 80.0)), float(chassis.get("hull_length", 100.0))) * 0.14

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
		return

	var weapon: Dictionary = loadout.get("weapon", {})
	clip_ammo -= 1
	fire_cooldown = float(weapon.get("fire_rate", 0.25))
	if is_state_active("smart_core"):
		fire_cooldown *= 0.55

	if clip_ammo == 0:
		reload_timer = 1.1

	var muzzle_origin := global_position + forward * 36.0
	_apply_fire_feedback(weapon)
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

func _try_activate_core() -> void:
	var core: Dictionary = loadout.get("core", {})
	var core_id := String(core.get("id", ""))
	if core_id.is_empty() or core_meter < 100.0:
		return

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
	var weapon: Dictionary = loadout.get("weapon", {})
	if legion_mode == "close":
		legion_mode = "long"
		weapon["range"] = 3200.0
		weapon["spread"] = 0.012
		weapon["fire_rate"] = 0.08
	else:
		legion_mode = "close"
		weapon["range"] = 1500.0
		weapon["spread"] = 0.04
		weapon["fire_rate"] = 0.05
	loadout["weapon"] = weapon

func _apply_monarch_upgrade() -> void:
	monarch_tier = min(monarch_tier + 1, 3)
	var weapon: Dictionary = loadout.get("weapon", {})
	match monarch_tier:
		1:
			max_clip = max(max_clip, 50)
			clip_ammo = min(max_clip, clip_ammo + 10)
			weapon["clip_size"] = max_clip
		2:
			monarch_bonus_shield = 500.0
			max_shield = float(chassis.get("max_shield", 3500.0)) + monarch_bonus_shield
			shield = minf(max_shield, shield + 500.0)
			monarch_cooldown_mult = 0.7
		3:
			monarch_damage_mult = 1.25
			weapon["fire_rate"] = maxf(0.06, float(weapon.get("fire_rate", 0.09)) * 0.75)
	loadout["weapon"] = weapon

func _get_ability_names() -> Array:
	var names: Array = []
	for ability in loadout.get("abilities", []):
		names.append(String(ability.get("name", "Ability")))
	return names
