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
var monarch_tier := 0
var monarch_damage_mult := 1.0
var monarch_cooldown_mult := 1.0
var decision_timer := 0.0
var match_state := "warmup"
var arena_map: ArenaMap

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
	if visuals:
		apply_loadout(loadout_key)
		respawn(true)

func _physics_process(delta: float) -> void:
	if not target:
		return

	if not alive:
		return

	for index in range(ability_cooldowns.size()):
		ability_cooldowns[index] = maxf(0.0, float(ability_cooldowns[index]) - delta)
	_tick_state_timers(delta)
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

	orbit_phase += delta
	var move_target := target.global_position
	if arena_map:
		move_target = arena_map.get_navigation_target(global_position, target.global_position, TEAM_ENEMY)
	var to_target := target.global_position - global_position
	var to_move_target := move_target - global_position
	var distance := to_target.length()
	var move_distance := to_move_target.length()
	var aim_dir := to_target.normalized() if distance > 0.01 else -global_basis.z
	var move_dir := to_move_target.normalized() if move_distance > 0.01 else aim_dir
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

	var desired_velocity := Vector3.ZERO
	if distance > 900.0:
		desired_velocity += move_dir * float(chassis.get("flight_speed", 350.0)) * 0.72 * move_speed_multiplier
	elif distance < 360.0:
		desired_velocity -= move_dir * float(chassis.get("flight_speed", 350.0)) * 0.45 * move_speed_multiplier
	else:
		desired_velocity += move_dir * float(chassis.get("flight_speed", 350.0)) * 0.18 * move_speed_multiplier

	desired_velocity += orbit_right * orbit_sign * float(chassis.get("strafe_speed", 280.0)) * 0.45 * move_speed_multiplier
	var vertical_delta := clampf(target.global_position.y - global_position.y, -220.0, 220.0) / 220.0
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

	if distance < float(loadout.get("weapon", {}).get("range", 2200.0)) * 0.92 and forward.dot(aim_dir) > 0.94:
		_attempt_fire(forward)

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
	monarch_tier = 0
	monarch_damage_mult = 1.0
	monarch_cooldown_mult = 1.0
	decision_timer = 0.0
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

	if health <= 0.0:
		alive = false
		respawn_timer = 3.2
		velocity = Vector3.ZERO
		visuals.set_ship_enabled(false)
		global_position = Vector3(0, -4000, 0)
		destroyed.emit(source_loadout_key, loadout_key)

func respawn(force_position := false) -> void:
	alive = true
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
	monarch_tier = 0
	monarch_damage_mult = 1.0
	monarch_cooldown_mult = 1.0
	decision_timer = 0.35 + randf() * 0.2
	visuals.set_ship_enabled(true)
	if force_position or global_position.distance_to(spawn_point) > 10.0:
		global_position = spawn_point

func is_alive() -> bool:
	return alive

func get_team() -> int:
	return TEAM_ENEMY

func get_collision_radius() -> float:
	return maxf(float(chassis.get("hull_width", 80.0)), float(chassis.get("hull_length", 100.0))) * 0.14

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
			max_shield = float(chassis.get("max_shield", 3500.0)) + 500.0
			shield = minf(max_shield, shield + 500.0)
			monarch_cooldown_mult = 0.7
		3:
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
