class_name ShipVisuals
extends Node3D

const GameData = preload("res://scripts/game_data.gd")

var loadout_key := "ION"
var chassis: Dictionary = {}
var signature: Dictionary = {}

var hull_root: Node3D
var engine_glows: Array[MeshInstance3D] = []
var engine_bases: Array[Vector3] = []
var engine_particles: Array[GPUParticles3D] = []
var shield_mesh: MeshInstance3D
var muzzle_particles: GPUParticles3D
var muzzle_anchor: Node3D
var muzzle_light: OmniLight3D

var _pulse_time := 0.0
var _muzzle_flash := 0.0

func configure_ship(new_loadout_key: String, new_chassis: Dictionary, new_signature: Dictionary) -> void:
	loadout_key = new_loadout_key
	chassis = new_chassis.duplicate(true)
	signature = new_signature.duplicate(true)
	_rebuild_ship()

func trigger_muzzle_flash() -> void:
	_muzzle_flash = 1.0
	if muzzle_particles:
		muzzle_particles.restart()
		muzzle_particles.emitting = true
	if muzzle_light:
		muzzle_light.light_energy = 4.4

func pulse_shield() -> void:
	if shield_mesh and shield_mesh.material_override is StandardMaterial3D:
		var shield_material: StandardMaterial3D = shield_mesh.material_override
		shield_material.albedo_color.a = 0.32
		shield_material.emission_energy_multiplier = 2.4

func set_ship_enabled(is_enabled: bool) -> void:
	process_mode = Node.PROCESS_MODE_INHERIT if is_enabled else Node.PROCESS_MODE_DISABLED
	for child in get_children():
		_toggle_visual_recursive(child, is_enabled)

func update_ship_visuals(delta: float, speed_ratio: float, local_velocity: Vector3 = Vector3.ZERO, look_input: Vector2 = Vector2.ZERO, boost_amount: float = 0.0) -> void:
	_pulse_time += delta
	_muzzle_flash = maxf(0.0, _muzzle_flash - delta * 7.0)

	var pulse_rate := float(signature.get("engine_pulse_rate", 12.0))
	var pulse := 0.82 + (sin(_pulse_time * pulse_rate) * 0.08)
	var glow_scale := pulse + (speed_ratio * 0.32) + (_muzzle_flash * 0.15) + boost_amount * 0.12

	for index in range(engine_glows.size()):
		var glow := engine_glows[index]
		var base_scale := engine_bases[index]
		glow.scale = base_scale * glow_scale
		if glow.material_override is StandardMaterial3D:
			var glow_material: StandardMaterial3D = glow.material_override
			glow_material.emission_energy_multiplier = 1.8 + speed_ratio * 1.8 + _muzzle_flash * 1.2 + boost_amount * 1.4

	for plume in engine_particles:
		plume.amount_ratio = clampf(0.35 + speed_ratio * 0.75 + _muzzle_flash * 0.08 + boost_amount * 0.18, 0.2, 1.0)
		plume.speed_scale = 0.9 + speed_ratio * 0.65 + boost_amount * 0.45

	if hull_root:
		var strafe_speed := maxf(1.0, float(chassis.get("strafe_speed", 280.0)))
		var vertical_speed := maxf(1.0, float(chassis.get("vertical_speed", 250.0)))
		var forward_speed := maxf(1.0, float(chassis.get("flight_speed", 350.0)))
		var target_roll := clampf(-local_velocity.x / strafe_speed, -1.0, 1.0) * 0.28 - clampf(look_input.x * 0.0025, -0.10, 0.10)
		var target_pitch := clampf(local_velocity.y / vertical_speed, -1.0, 1.0) * 0.12 + clampf(-local_velocity.z / forward_speed, -1.0, 1.0) * 0.05 - clampf(look_input.y * 0.0018, -0.08, 0.08)
		var target_push := _muzzle_flash * 1.8 + boost_amount * 2.4
		hull_root.rotation.z = lerpf(hull_root.rotation.z, target_roll, delta * 6.0)
		hull_root.rotation.x = lerpf(hull_root.rotation.x, target_pitch, delta * 6.0)
		hull_root.position = hull_root.position.lerp(Vector3(0.0, boost_amount * 0.35, target_push), delta * 9.0)

	if muzzle_light:
		muzzle_light.light_energy = lerpf(muzzle_light.light_energy, _muzzle_flash * 4.4, delta * 15.0)

	if shield_mesh and shield_mesh.material_override is StandardMaterial3D:
		var shield_material: StandardMaterial3D = shield_mesh.material_override
		shield_material.albedo_color.a = lerpf(shield_material.albedo_color.a, 0.08, delta * 4.0)
		shield_material.emission_energy_multiplier = lerpf(shield_material.emission_energy_multiplier, 1.0, delta * 4.0)

func _rebuild_ship() -> void:
	for child in get_children():
		child.queue_free()

	engine_glows.clear()
	engine_bases.clear()
	engine_particles.clear()
	shield_mesh = null
	muzzle_particles = null
	muzzle_anchor = null
	muzzle_light = null

	hull_root = Node3D.new()
	hull_root.name = "HullRoot"
	add_child(hull_root)

	var hull_color := Color(0.70, 0.75, 0.84, 1.0)
	var dark_color := Color(0.14, 0.17, 0.24, 1.0)
	var panel_color := GameData.color_from_hex(int(signature.get("panel_color", 0x66ccff)))
	var engine_color := GameData.color_from_hex(int(signature.get("engine_color", 0x66eeff)))
	var plume_color := GameData.color_from_hex(int(signature.get("plume_color", 0xaaeeff)))
	var shield_color := GameData.color_from_hex(int(signature.get("shield_color", 0x44ccff)))
	var muzzle_color := GameData.color_from_hex(int(signature.get("muzzle_color", 0xffcc66)))

	var hull_material := _make_surface_material(hull_color, Color(0.18, 0.25, 0.36, 1.0), 0.35)
	var dark_material := _make_surface_material(dark_color, Color(0.05, 0.05, 0.08, 1.0), 0.0)
	var panel_material := _make_surface_material(panel_color.darkened(0.2), panel_color, 1.4)
	var engine_material := _make_glow_material(engine_color, 2.2)

	var hull_width := float(chassis.get("hull_width", 80.0))
	var hull_height := float(chassis.get("hull_height", 30.0))
	var hull_length := float(chassis.get("hull_length", 100.0))
	# Match HTML: chassis hullWidth/hullHeight/hullLength are world-unit
	# dimensions (last_ship_sailing.html:2522-2527 uses them directly via
	# `w = hullWidth*0.5` etc). The previous 0.25 scale_factor made ships
	# ~25 units long against a 750-unit-diameter spawn room, so they read as
	# specks. Drawing at full chassis dimensions matches the HTML reference
	# and the room/tunnel scale (MAP_UNIT = 150 = HTML SU = 150).
	var scale_factor := 1.0
	var w := hull_width * scale_factor
	var h := hull_height * scale_factor
	var l := hull_length * scale_factor
	var imported_model_added := _try_add_imported_model(hull_root, l)

	if not imported_model_added:
		match String(chassis.get("name", "Corvette")):
			"Frigate":
				_add_box(hull_root, Vector3(w * 0.55, h * 0.55, l * 1.2), Vector3(0, 0, 0), hull_material)
				_add_box(hull_root, Vector3(w * 0.18, h * 0.22, l * 0.55), Vector3(0, h * 0.42, -l * 0.20), panel_material)
				_add_box(hull_root, Vector3(w * 1.6, h * 0.08, l * 0.58), Vector3(0, -h * 0.05, l * 0.10), dark_material, Vector3(0, 0, deg_to_rad(10)))
				_add_box(hull_root, Vector3(w * 0.22, h * 0.5, l * 0.3), Vector3(-w * 0.82, h * 0.18, l * 0.32), dark_material)
				_add_box(hull_root, Vector3(w * 0.22, h * 0.5, l * 0.3), Vector3(w * 0.82, h * 0.18, l * 0.32), dark_material)
			"Corvette":
				_add_box(hull_root, Vector3(w * 0.82, h * 0.78, l * 1.42), Vector3(0, 0, 0), hull_material)
				_add_box(hull_root, Vector3(w * 0.42, h * 0.32, l * 0.62), Vector3(0, h * 0.42, -l * 0.18), panel_material)
				_add_box(hull_root, Vector3(w * 1.05, h * 0.10, l * 0.28), Vector3(0, 0, -l * 0.45), dark_material)
				_add_box(hull_root, Vector3(w * 0.16, h * 0.36, l * 1.0), Vector3(-w * 0.62, -h * 0.05, 0), dark_material)
				_add_box(hull_root, Vector3(w * 0.16, h * 0.36, l * 1.0), Vector3(w * 0.62, -h * 0.05, 0), dark_material)
			_:
				_add_box(hull_root, Vector3(w * 0.96, h * 0.82, l * 1.56), Vector3(0, 0, 0), hull_material)
				_add_box(hull_root, Vector3(w * 0.6, h * 0.36, l * 0.7), Vector3(0, h * 0.45, -l * 0.15), panel_material)
				_add_box(hull_root, Vector3(w * 1.2, h * 0.12, l * 0.42), Vector3(0, 0, -l * 0.45), dark_material)
				_add_box(hull_root, Vector3(w * 0.18, h * 0.5, l * 1.2), Vector3(-w * 0.62, 0, 0), dark_material)
				_add_box(hull_root, Vector3(w * 0.18, h * 0.5, l * 1.2), Vector3(w * 0.62, 0, 0), dark_material)

	match String(chassis.get("name", "Corvette")):
		"Frigate":
			_add_engine_bank(hull_root, Vector3(-w * 0.34, -h * 0.08, l * 0.72), Vector3(h * 0.22, h * 0.22, h * 0.06), engine_material, plume_color, l * 0.95)
			_add_engine_bank(hull_root, Vector3(w * 0.34, -h * 0.08, l * 0.72), Vector3(h * 0.22, h * 0.22, h * 0.06), engine_material, plume_color, l * 0.95)
			muzzle_anchor = _add_marker(hull_root, Vector3(0, 0, -l * 0.82))
		"Corvette":
			_add_engine_bank(hull_root, Vector3(0, 0, l * 0.88), Vector3(h * 0.42, h * 0.42, h * 0.08), engine_material, plume_color, l * 1.15)
			_add_engine_bank(hull_root, Vector3(-w * 0.55, h * 0.08, l * 0.74), Vector3(h * 0.10, h * 0.10, h * 0.05), engine_material, plume_color, l * 0.42)
			_add_engine_bank(hull_root, Vector3(w * 0.55, h * 0.08, l * 0.74), Vector3(h * 0.10, h * 0.10, h * 0.05), engine_material, plume_color, l * 0.42)
			muzzle_anchor = _add_marker(hull_root, Vector3(0, 0, -l * 0.96))
		_:
			_add_engine_bank(hull_root, Vector3(-w * 0.32, 0, l * 0.94), Vector3(h * 0.24, h * 0.24, h * 0.06), engine_material, plume_color, l * 1.0)
			_add_engine_bank(hull_root, Vector3(0, 0, l * 0.94), Vector3(h * 0.24, h * 0.24, h * 0.06), engine_material, plume_color, l * 1.0)
			_add_engine_bank(hull_root, Vector3(w * 0.32, 0, l * 0.94), Vector3(h * 0.24, h * 0.24, h * 0.06), engine_material, plume_color, l * 1.0)
			muzzle_anchor = _add_marker(hull_root, Vector3(0, 0, -l * 0.98))

	shield_mesh = _add_sphere(hull_root, maxf(w, l) * 0.85, Vector3.ZERO, _make_shield_material(shield_color))
	shield_mesh.scale = Vector3(1.3, 0.78, 1.3)
	muzzle_particles = _create_muzzle_particles(muzzle_color)
	muzzle_anchor.add_child(muzzle_particles)
	muzzle_light = OmniLight3D.new()
	muzzle_light.light_color = muzzle_color
	muzzle_light.light_energy = 0.0
	muzzle_light.omni_range = 220.0
	muzzle_light.shadow_enabled = false
	muzzle_anchor.add_child(muzzle_light)

func _add_box(parent: Node3D, size: Vector3, position: Vector3, material: Material, rotation: Vector3 = Vector3.ZERO) -> MeshInstance3D:
	var mesh := BoxMesh.new()
	mesh.size = size
	var instance := MeshInstance3D.new()
	instance.mesh = mesh
	instance.material_override = material
	instance.position = position
	instance.rotation = rotation
	parent.add_child(instance)
	return instance

func _add_sphere(parent: Node3D, radius: float, position: Vector3, material: Material) -> MeshInstance3D:
	var mesh := SphereMesh.new()
	mesh.radius = radius
	mesh.height = radius * 2.0
	var instance := MeshInstance3D.new()
	instance.mesh = mesh
	instance.material_override = material
	instance.position = position
	parent.add_child(instance)
	return instance

func _add_engine_bank(parent: Node3D, position: Vector3, base_scale: Vector3, engine_material: Material, plume_color: Color, plume_length: float) -> void:
	var glow := _add_sphere(parent, 1.0, position, engine_material)
	glow.scale = base_scale
	engine_glows.append(glow)
	engine_bases.append(base_scale)

	var plume := _create_plume_particles(plume_color, plume_length)
	plume.position = position
	parent.add_child(plume)
	engine_particles.append(plume)

func _add_marker(parent: Node3D, position: Vector3) -> Node3D:
	var marker := Node3D.new()
	marker.position = position
	parent.add_child(marker)
	return marker

func _try_add_imported_model(parent: Node3D, target_length: float) -> bool:
	var spec := GameData.get_model_spec(loadout_key)
	if spec.is_empty():
		return false

	var model_path := String(spec.get("path", ""))
	if model_path.is_empty() or not ResourceLoader.exists(model_path):
		return false

	var model_scene: Resource = load(model_path)
	if model_scene == null or not (model_scene is PackedScene):
		return false

	var model_root := (model_scene as PackedScene).instantiate()
	if not (model_root is Node3D):
		if model_root:
			model_root.queue_free()
		return false

	parent.add_child(model_root)
	var bbox := _compute_local_bounds(model_root)
	var longest := maxf(maxf(bbox.size.x, bbox.size.y), bbox.size.z)
	if longest <= 0.001:
		longest = 1.0

	var desired_length := target_length * float(spec.get("scale_mult", 1.0))
	var fit_scale := desired_length / longest
	model_root.scale = Vector3.ONE * fit_scale

	bbox = _compute_local_bounds(model_root)
	model_root.position -= bbox.get_center()
	if bool(spec.get("face_flip", false)):
		model_root.rotate_y(PI)
	_apply_model_materials(model_root)
	return true

func _compute_local_bounds(root: Node3D) -> AABB:
	var has_bounds := false
	var min_corner := Vector3.ZERO
	var max_corner := Vector3.ZERO
	var state: Array = _accumulate_bounds_recursive(root, Transform3D.IDENTITY, has_bounds, min_corner, max_corner)
	has_bounds = state[0]
	min_corner = state[1]
	max_corner = state[2]
	if not has_bounds:
		return AABB(Vector3.ZERO, Vector3.ONE)
	return AABB(min_corner, max_corner - min_corner)

func _accumulate_bounds_recursive(node: Node, parent_transform: Transform3D, has_bounds: bool, min_corner: Vector3, max_corner: Vector3) -> Array:
	var current_transform := parent_transform
	if node is Node3D:
		current_transform = parent_transform * (node as Node3D).transform

	if node is MeshInstance3D:
		var mesh_instance := node as MeshInstance3D
		if mesh_instance.mesh:
			var aabb := mesh_instance.get_aabb()
			for corner in _aabb_corners(aabb):
				var transformed_corner := current_transform * corner
				if not has_bounds:
					min_corner = transformed_corner
					max_corner = transformed_corner
					has_bounds = true
				else:
					min_corner = min_corner.min(transformed_corner)
					max_corner = max_corner.max(transformed_corner)

	for child in node.get_children():
		var state: Array = _accumulate_bounds_recursive(child, current_transform, has_bounds, min_corner, max_corner)
		has_bounds = state[0]
		min_corner = state[1]
		max_corner = state[2]

	return [has_bounds, min_corner, max_corner]

func _aabb_corners(aabb: AABB) -> Array[Vector3]:
	var p := aabb.position
	var s := aabb.size
	return [
		p,
		p + Vector3(s.x, 0, 0),
		p + Vector3(0, s.y, 0),
		p + Vector3(0, 0, s.z),
		p + Vector3(s.x, s.y, 0),
		p + Vector3(s.x, 0, s.z),
		p + Vector3(0, s.y, s.z),
		p + s
	]

func _apply_model_materials(root: Node) -> void:
	var accent_color := GameData.color_from_hex(int(signature.get("panel_color", 0x66ccff)))
	for child in root.get_children():
		_apply_model_materials(child)
	if root is MeshInstance3D:
		var mesh_instance := root as MeshInstance3D
		var surface_count := mesh_instance.mesh.get_surface_count() if mesh_instance.mesh else 0
		for surface_index in range(surface_count):
			var base_material := mesh_instance.get_active_material(surface_index)
			var material: Material = base_material if base_material != null else mesh_instance.mesh.surface_get_material(surface_index)
			if material is StandardMaterial3D:
				var dupe := (material as StandardMaterial3D).duplicate()
				dupe.emission_enabled = true
				dupe.emission = accent_color * 0.25
				dupe.emission_energy_multiplier = maxf(dupe.emission_energy_multiplier, 0.45)
				mesh_instance.set_surface_override_material(surface_index, dupe)

func _make_surface_material(albedo: Color, emission: Color, emission_energy: float) -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.albedo_color = albedo
	material.metallic = 0.22
	material.roughness = 0.35
	material.emission_enabled = emission_energy > 0.0
	material.emission = emission
	material.emission_energy_multiplier = emission_energy
	return material

func _make_glow_material(color: Color, energy: float) -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	material.cull_mode = BaseMaterial3D.CULL_DISABLED
	material.no_depth_test = true
	material.albedo_color = Color(color.r, color.g, color.b, 0.85)
	material.emission_enabled = true
	material.emission = color
	material.emission_energy_multiplier = energy
	return material

func _make_shield_material(color: Color) -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	material.cull_mode = BaseMaterial3D.CULL_DISABLED
	material.albedo_color = Color(color.r, color.g, color.b, 0.08)
	material.emission_enabled = true
	material.emission = color
	material.emission_energy_multiplier = 1.0
	return material

func _create_plume_particles(color: Color, plume_length: float) -> GPUParticles3D:
	var particles := GPUParticles3D.new()
	particles.amount = 28
	particles.lifetime = 0.38
	particles.local_coords = true
	particles.position = Vector3.ZERO
	particles.amount_ratio = 0.7
	particles.speed_scale = 1.0

	var quad := QuadMesh.new()
	quad.size = Vector2(1.4, 1.4)
	var quad_material := StandardMaterial3D.new()
	quad_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	quad_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	quad_material.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	quad_material.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	quad_material.albedo_color = Color(color.r, color.g, color.b, 0.65)
	quad_material.emission_enabled = true
	quad_material.emission = color
	quad_material.emission_energy_multiplier = 2.0
	quad.material = quad_material
	particles.draw_pass_1 = quad

	var process := ParticleProcessMaterial.new()
	process.direction = Vector3(0, 0, 1)
	process.spread = 12.0
	process.gravity = Vector3.ZERO
	process.initial_velocity_min = plume_length * 0.22
	process.initial_velocity_max = plume_length * 0.34
	process.scale_min = 0.6
	process.scale_max = 1.2
	process.color = color
	particles.process_material = process
	particles.emitting = true
	return particles

func _create_muzzle_particles(color: Color) -> GPUParticles3D:
	var particles := GPUParticles3D.new()
	particles.amount = 18
	particles.lifetime = 0.12
	particles.one_shot = true
	particles.explosiveness = 0.95
	particles.local_coords = true

	var quad := QuadMesh.new()
	quad.size = Vector2(1.0, 1.0)
	var quad_material := StandardMaterial3D.new()
	quad_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	quad_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	quad_material.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	quad_material.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	quad_material.albedo_color = Color(color.r, color.g, color.b, 0.85)
	quad_material.emission_enabled = true
	quad_material.emission = color
	quad_material.emission_energy_multiplier = 3.0
	quad.material = quad_material
	particles.draw_pass_1 = quad

	var process := ParticleProcessMaterial.new()
	process.direction = Vector3(0, 0, -1)
	process.spread = 18.0
	process.gravity = Vector3.ZERO
	process.initial_velocity_min = 10.0
	process.initial_velocity_max = 24.0
	process.scale_min = 0.8
	process.scale_max = 1.6
	process.color = color
	particles.process_material = process
	return particles

func _toggle_visual_recursive(node: Node, is_enabled: bool) -> void:
	if node is VisualInstance3D:
		var visual := node as VisualInstance3D
		visual.visible = is_enabled
	if node is GPUParticles3D:
		var particles := node as GPUParticles3D
		particles.emitting = is_enabled and not particles.one_shot
	for child in node.get_children():
		_toggle_visual_recursive(child, is_enabled)
