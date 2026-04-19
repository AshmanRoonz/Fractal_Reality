class_name TargetDrone
extends StaticBody3D

const GameData = preload("res://scripts/game_data.gd")

var max_health := 2400.0
var health := 2400.0
var base_position := Vector3.ZERO
var phase := 0.0
var spin_rate := 0.45
var respawn_timer := 0.0
var active := true

var shell_mesh: MeshInstance3D
var core_mesh: MeshInstance3D
var collision_shape: CollisionShape3D

func _ready() -> void:
	collision_layer = 1
	collision_mask = 1

	var shell := SphereMesh.new()
	shell.radius = 18.0
	shell.height = 36.0
	shell_mesh = MeshInstance3D.new()
	shell_mesh.mesh = shell
	shell_mesh.material_override = _make_shell_material(Color(0.22, 0.30, 0.42, 1.0), Color(0.28, 0.45, 0.75, 1.0), 1.0)
	add_child(shell_mesh)

	var core := SphereMesh.new()
	core.radius = 8.0
	core.height = 16.0
	core_mesh = MeshInstance3D.new()
	core_mesh.mesh = core
	core_mesh.material_override = _make_shell_material(Color(0.82, 0.90, 1.0, 1.0), Color(0.55, 0.78, 1.0, 1.0), 3.0)
	add_child(core_mesh)

	collision_shape = CollisionShape3D.new()
	var shape := SphereShape3D.new()
	shape.radius = 20.0
	collision_shape.shape = shape
	add_child(collision_shape)

func configure(position_in_space: Vector3, seed_offset: float) -> void:
	base_position = position_in_space
	global_position = position_in_space
	phase = seed_offset

func _process(delta: float) -> void:
	if active:
		phase += delta
		global_position = base_position + Vector3(
			sin(phase * 0.8) * 18.0,
			cos(phase * 1.3) * 14.0,
			sin(phase * 0.5) * 22.0
		)
		rotate_y(delta * spin_rate)
		_update_flash(delta)
	else:
		respawn_timer -= delta
		if respawn_timer <= 0.0:
			_respawn()

func apply_damage(amount: float, _hit_point: Vector3, source_loadout_key: String) -> void:
	if not active:
		return

	health -= amount
	var tint := GameData.color_from_hex(int(GameData.get_signature(source_loadout_key).get("impact_light_color", 0xffcc66)))
	if core_mesh.material_override is StandardMaterial3D:
		var core_material: StandardMaterial3D = core_mesh.material_override
		core_material.emission = tint
		core_material.emission_energy_multiplier = 5.0

	if shell_mesh.material_override is StandardMaterial3D:
		var shell_material: StandardMaterial3D = shell_mesh.material_override
		shell_material.emission = tint
		shell_material.emission_energy_multiplier = 2.0

	if health <= 0.0:
		active = false
		respawn_timer = 2.2
		visible = false
		collision_shape.disabled = true

func is_active() -> bool:
	return active

func _respawn() -> void:
	active = true
	health = max_health
	visible = true
	collision_shape.disabled = false
	global_position = base_position
	if core_mesh.material_override is StandardMaterial3D:
		var core_material: StandardMaterial3D = core_mesh.material_override
		core_material.emission = Color(0.55, 0.78, 1.0, 1.0)
		core_material.emission_energy_multiplier = 3.0
	if shell_mesh.material_override is StandardMaterial3D:
		var shell_material: StandardMaterial3D = shell_mesh.material_override
		shell_material.emission = Color(0.28, 0.45, 0.75, 1.0)
		shell_material.emission_energy_multiplier = 1.0

func _update_flash(delta: float) -> void:
	if core_mesh.material_override is StandardMaterial3D:
		var core_material: StandardMaterial3D = core_mesh.material_override
		core_material.emission_energy_multiplier = lerpf(core_material.emission_energy_multiplier, 3.0, delta * 5.0)
	if shell_mesh.material_override is StandardMaterial3D:
		var shell_material: StandardMaterial3D = shell_mesh.material_override
		shell_material.emission_energy_multiplier = lerpf(shell_material.emission_energy_multiplier, 1.0, delta * 5.0)

func _make_shell_material(albedo: Color, emission: Color, energy: float) -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.albedo_color = albedo
	material.metallic = 0.15
	material.roughness = 0.35
	material.emission_enabled = true
	material.emission = emission
	material.emission_energy_multiplier = energy
	return material
