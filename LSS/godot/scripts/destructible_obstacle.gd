class_name DestructibleObstacle
extends Node3D

# Port of HTML last_ship_sailing.html:4043-4321 (DestructibleObstacle).
# Destructible props live either standalone (self-respawn in 25s) or as
# children of a ClusterObstacle (the cluster manages rebirth). Ships bounce
# off intact pieces; heavy impacts shatter a cluster into drifting debris,
# and those fragments detonate on contact (40-120 dmg) before expiring after
# 10-16s. Weapon damage also shatters the cluster immediately.
#
# Per-frame ticking, ship-collision resolution, and fragment-impact checks
# are driven by main.gd; the obstacle only owns its own state, mesh, motion,
# and the damage/respawn state machine.

const SHAPE_TYPES := ["box", "diamond", "cross", "wedge", "ring"]
const OBSTACLE_COLORS: Array[int] = [0xaa4433, 0xccaa22, 0x885522, 0x447788, 0x778844]

var original_pos: Vector3
var shape_type: String = "box"
var scale_val: float = 60.0
var hp: float = 250.0
var max_hp: float = 250.0
var is_alive: bool = true
var respawn_timer: float = 0.0
var respawn_time: float = 25.0
var collision_radius: float = 42.0

# Set by ClusterObstacle when this piece is a child. localOffset is the
# body-frame offset (pre-rotation) the cluster uses each frame to keep the
# child glued to its slot while the cluster rotates as a rigid group.
var cluster: Node = null
var local_offset: Vector3 = Vector3.ZERO

var broken: bool = false
var fragment_vel: Vector3 = Vector3.ZERO
var fragment_life: float = 0.0
var fragment_max_life: float = 14.0

var rot_speed: Vector3 = Vector3.ZERO
var base_color: int = 0xaa4433

var mesh_instance: MeshInstance3D
var _material: StandardMaterial3D

func configure(pos: Vector3, shape: String = "", scale_override: float = 0.0, color_override: int = -1) -> void:
	original_pos = pos
	position = pos
	if shape == "":
		shape_type = SHAPE_TYPES[randi() % SHAPE_TYPES.size()]
	else:
		shape_type = shape
	if scale_override > 0.0:
		scale_val = scale_override
	else:
		scale_val = 40.0 + randf() * 60.0
	hp = 250.0 + scale_val * 3.0
	max_hp = hp
	collision_radius = scale_val * 0.7
	rot_speed = Vector3(
		(randf() - 0.5) * 0.3,
		(randf() - 0.5) * 0.5,
		(randf() - 0.5) * 0.3
	)
	rotation = Vector3(
		randf() * TAU,
		randf() * TAU,
		randf() * TAU
	)
	if color_override >= 0:
		base_color = color_override
	else:
		base_color = OBSTACLE_COLORS[randi() % OBSTACLE_COLORS.size()]
	if is_inside_tree():
		_build_mesh()

func _ready() -> void:
	if mesh_instance == null:
		_build_mesh()

func _build_mesh() -> void:
	if mesh_instance != null and is_instance_valid(mesh_instance):
		mesh_instance.queue_free()
	mesh_instance = MeshInstance3D.new()
	var s := scale_val
	var mesh: Mesh
	match shape_type:
		"diamond":
			# Octahedron stand-in: 4-segment sphere with 2 rings collapses to a
			# diamond in Godot's primitive set.
			var sphere := SphereMesh.new()
			sphere.radius = s
			sphere.height = s * 2.0
			sphere.radial_segments = 4
			sphere.rings = 2
			mesh = sphere
		"cross":
			# HTML uses a dodecahedron here; a 6-segment sphere is a close-enough
			# angular proxy without a custom mesh.
			var sphere := SphereMesh.new()
			sphere.radius = s * 0.85
			sphere.height = s * 1.7
			sphere.radial_segments = 6
			sphere.rings = 3
			mesh = sphere
		"wedge":
			# Cone (cylinder with top_radius == 0).
			var cone := CylinderMesh.new()
			cone.top_radius = 0.0
			cone.bottom_radius = s * 0.7
			cone.height = s * 1.4
			cone.radial_segments = 5
			mesh = cone
		"ring":
			var torus := TorusMesh.new()
			torus.inner_radius = s * 0.35
			torus.outer_radius = s * 0.85
			mesh = torus
		_:
			# Irregular box (HTML's default).
			var box := BoxMesh.new()
			box.size = Vector3(
				s * (0.6 + randf() * 0.8),
				s * (0.6 + randf() * 0.8),
				s * (0.6 + randf() * 0.8)
			)
			mesh = box
	mesh_instance.mesh = mesh
	_material = StandardMaterial3D.new()
	var col := _color_from_hex(base_color)
	_material.albedo_color = col
	_material.metallic = 0.7
	_material.roughness = 0.3
	_material.emission_enabled = true
	_material.emission = col
	_material.emission_energy_multiplier = 0.15
	mesh_instance.material_override = _material
	add_child(mesh_instance)

func _color_from_hex(hex: int) -> Color:
	var r := float((hex >> 16) & 0xff) / 255.0
	var g := float((hex >> 8) & 0xff) / 255.0
	var b := float(hex & 0xff) / 255.0
	return Color(r, g, b, 1.0)

# Per-frame tick. Handles fragment drift, spin, damage-flash emission, and
# self-respawn for standalone pieces. ClusterObstacle keeps intact children
# pinned to its rotation before this runs (main.gd order of operations).
func update(delta: float) -> void:
	if not is_alive:
		if cluster == null:
			respawn_timer -= delta
			if respawn_timer <= 0.0:
				_self_respawn()
		return

	if broken:
		position += fragment_vel * delta
		# Gentle drag so debris eventually coasts rather than flying forever.
		fragment_vel *= maxf(0.0, 1.0 - 0.35 * delta)
		fragment_life += delta
		if fragment_life > fragment_max_life:
			is_alive = false
			_hide_mesh()
			return

	# Self-rotation (intact or broken both tumble).
	rotation.x += rot_speed.x * delta
	rotation.y += rot_speed.y * delta
	rotation.z += rot_speed.z * delta

	if _material != null:
		if broken:
			_material.emission_energy_multiplier = 0.55
		else:
			var hp_ratio := hp / max_hp
			if hp_ratio < 0.5:
				_material.emission_energy_multiplier = 0.15 + (1.0 - hp_ratio) * 0.4
			else:
				_material.emission_energy_multiplier = 0.15

# Sphere collision: pushes the entity out of overlap and reflects its
# velocity with a 1.3x bounce coefficient (HTML 4236-4283). Returns a
# dictionary with whether we bounced, the corrected pos/vel, a ram-damage
# amount to apply back to this obstacle (if any), and an "exploded" flag
# if this was a broken fragment that detonated on contact.
#
# Caller is responsible for applying ram damage to the ship, writing
# back the corrected pos/vel, and calling take_damage(ram_damage, normal)
# on this obstacle when ram_damage > 0.
func collide_entity(entity_pos: Vector3, entity_vel: Vector3, entity_radius: float) -> Dictionary:
	if not is_alive:
		return {"collided": false}
	var delta_vec := entity_pos - global_position
	var dist_sq := delta_vec.length_squared()
	var min_dist := collision_radius + entity_radius
	if dist_sq >= min_dist * min_dist:
		return {"collided": false}

	var dist := sqrt(dist_sq)
	if dist < 0.1:
		# Entity is sitting on the center; nudge it up a full min_dist so it
		# escapes in a deterministic direction.
		return {
			"collided": true,
			"position": entity_pos + Vector3(0.0, min_dist, 0.0),
			"velocity": entity_vel,
			"ram_damage": 0.0,
			"normal": Vector3.UP,
			"exploded": false,
		}

	var normal := delta_vec / dist

	# Broken fragment: no solid bounce. It detonates on contact; main.gd is
	# expected to apply ram-impact damage to the entity based on fragment_vel
	# and call _fragment_explode on this piece. Tell caller "exploded" so it
	# skips the ship-vs-obstacle bounce update for this pair.
	if broken:
		var impact_speed_frag := entity_vel.length()
		var damage_frag := 40.0 + minf(80.0, impact_speed_frag * 0.3)
		_fragment_explode()
		return {
			"collided": true,
			"position": entity_pos,
			"velocity": entity_vel,
			"ram_damage": 0.0,
			"normal": normal,
			"exploded": true,
			"fragment_damage": damage_frag,
		}

	var pen := min_dist - dist
	var new_pos := entity_pos + normal * (pen + 1.0)
	var new_vel := entity_vel
	var ram_damage := 0.0
	var v_dot_n := entity_vel.dot(normal)
	if v_dot_n < 0.0:
		var impact_speed := absf(v_dot_n)
		if impact_speed > 50.0:
			ram_damage = impact_speed * 0.4
		new_vel = entity_vel - normal * v_dot_n * 1.3
		# Significant bump on an intact cluster child triggers a full cluster
		# shatter (HTML 4279-4281). We only flag the shatter here; take_damage
		# below handles the damage/destroy side.
		if cluster != null and impact_speed > 80.0 and cluster.has_method("break_apart"):
			if not bool(cluster.get("broken")):
				cluster.break_apart(global_position, -normal)
	return {
		"collided": true,
		"position": new_pos,
		"velocity": new_vel,
		"ram_damage": ram_damage,
		"normal": -normal,
		"exploded": false,
	}

# Any damage against a still-intact cluster child shatters the whole cluster
# (HTML 4286-4302). Returns the damage actually absorbed so main.gd can
# score it for the attacker.
func take_damage(dmg: float, hit_dir: Vector3 = Vector3.ZERO) -> float:
	if not is_alive:
		return 0.0
	if cluster != null and cluster.has_method("break_apart") and not bool(cluster.get("broken")):
		cluster.break_apart(global_position, hit_dir)
	hp -= dmg
	if hp <= 0.0:
		if broken:
			_fragment_explode()
		else:
			destroy()
	return dmg

func destroy() -> void:
	is_alive = false
	_hide_mesh()
	# Cluster children don't self-respawn; the parent ClusterObstacle rebuilds
	# them via its own respawn path once all children are dead.
	if cluster == null:
		respawn_timer = respawn_time

func _fragment_explode() -> void:
	if not is_alive:
		return
	is_alive = false
	_hide_mesh()

func _hide_mesh() -> void:
	if mesh_instance != null and is_instance_valid(mesh_instance):
		mesh_instance.visible = false

func _self_respawn() -> void:
	is_alive = true
	broken = false
	fragment_life = 0.0
	fragment_vel = Vector3.ZERO
	hp = max_hp
	position = original_pos
	if mesh_instance != null and is_instance_valid(mesh_instance):
		mesh_instance.visible = true
	else:
		_build_mesh()

# Called by ClusterObstacle.break_apart. Sets the fragment kinematics; main's
# update tick then drifts and ages the piece until fragment_max_life expires
# or it touches a ship.
func begin_fragment(vel: Vector3, life_max: float) -> void:
	broken = true
	fragment_vel = vel
	fragment_life = 0.0
	fragment_max_life = life_max
	collision_radius = scale_val * 0.55
	rot_speed = Vector3(
		(randf() - 0.5) * 2.2,
		(randf() - 0.5) * 2.2,
		(randf() - 0.5) * 2.2
	)
	if _material != null:
		_material.emission_energy_multiplier = 0.55
