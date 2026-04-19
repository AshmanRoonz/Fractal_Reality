class_name ArenaMap
extends Node3D

const GameData = preload("res://scripts/game_data.gd")
const PlayerShip = preload("res://scripts/player_ship.gd")

const DEFAULT_TUNNEL_RADIUS := GameData.MAP_UNIT * 1.2
const NEXUS_WALL_SHADER := preload("res://scripts/shaders/nexus_wall.gdshader")

# Zone palette mirrored from last_ship_sailing.html createMeshFromPositions() roomPalette.
# Hex order: 0x1a3050, 0x3a1010, 0x103a10, 0x351828, 0x183520, 0x2a2040, 0x1a4030, 0x402020.
const NEXUS_ROOM_PALETTE: Array[Color] = [
	Color(0.102, 0.188, 0.314, 1.0),
	Color(0.227, 0.063, 0.063, 1.0),
	Color(0.063, 0.227, 0.063, 1.0),
	Color(0.208, 0.094, 0.157, 1.0),
	Color(0.094, 0.208, 0.125, 1.0),
	Color(0.165, 0.125, 0.251, 1.0),
	Color(0.102, 0.251, 0.188, 1.0),
	Color(0.251, 0.125, 0.125, 1.0),
]

var map_key := "hourglass"
var map_data: Dictionary = {}
var rooms: Array = []
var tunnel_segments: Array = []
var corridor_points: Array = []
var spawn_points := {"A": [], "B": []}
var bounds_min := Vector3.ZERO
var bounds_max := Vector3.ZERO

var _rng := RandomNumberGenerator.new()
var _nexus_wall_material: ShaderMaterial

func build_map(new_map_key: String = "hourglass") -> void:
	for child in get_children():
		child.queue_free()

	map_key = new_map_key
	map_data = GameData.get_map_data(map_key)
	rooms = map_data.get("rooms", []).duplicate(true)
	tunnel_segments.clear()
	corridor_points.clear()
	spawn_points = {"A": [], "B": []}
	_rng.seed = int(hash(map_key))

	_build_tunnel_segments(map_data.get("tunnels", []))
	_compute_bounds()
	_build_visuals()
	_generate_corridor_points()

func get_map_name() -> String:
	return str(map_data.get("name", "Arena"))

func get_bounds_extents() -> Vector3:
	return (bounds_max - bounds_min) * 0.5

func get_spawn_point(team: String, spread: float = 80.0, clearance: float = 38.0) -> Vector3:
	var pool: Array = spawn_points.get(team, [])
	if pool.is_empty():
		pool = corridor_points
	if pool.is_empty():
		return Vector3.ZERO

	var base: Dictionary = pool[_rng.randi_range(0, pool.size() - 1)]
	var offset := Vector3(
		_rng.randf_range(-spread * 0.5, spread * 0.5),
		_rng.randf_range(-spread * 0.35, spread * 0.35),
		_rng.randf_range(-spread * 0.5, spread * 0.5)
	)
	return constrain_point(Vector3(base["position"]) + offset, clearance)

func contains_point(point: Vector3, clearance: float = 0.0) -> bool:
	for room in rooms:
		var radius := maxf(18.0, float(room.get("radius", 0.0)) - clearance)
		if point.distance_to(Vector3(room.get("position", Vector3.ZERO))) <= radius:
			return true

	for segment in tunnel_segments:
		var seg_radius := maxf(18.0, float(segment.get("radius", DEFAULT_TUNNEL_RADIUS)) - clearance)
		if _distance_to_segment(point, Vector3(segment["a"]), Vector3(segment["b"])) <= seg_radius:
			return true

	return false

func constrain_point(point: Vector3, clearance: float = 0.0) -> Vector3:
	if contains_point(point, clearance):
		return point

	var best_point := point
	var best_distance := INF

	for room in rooms:
		var center := Vector3(room.get("position", Vector3.ZERO))
		var radius := maxf(18.0, float(room.get("radius", 0.0)) - clearance)
		var to_point := point - center
		var dist := to_point.length()
		var candidate := center
		if dist > 0.001:
			candidate = center + to_point / dist * minf(dist, radius)
		var outside := maxf(0.0, dist - radius)
		if outside < best_distance:
			best_distance = outside
			best_point = candidate

	for segment in tunnel_segments:
		var seg_radius := maxf(18.0, float(segment.get("radius", DEFAULT_TUNNEL_RADIUS)) - clearance)
		var closest := _closest_point_on_segment(point, Vector3(segment["a"]), Vector3(segment["b"]))
		var to_point := point - closest
		var dist := to_point.length()
		var candidate := closest
		if dist > 0.001:
			candidate = closest + to_point / dist * minf(dist, seg_radius)
		var outside := maxf(0.0, dist - seg_radius)
		if outside < best_distance:
			best_distance = outside
			best_point = candidate

	return best_point

func raycast_wall(from: Vector3, to: Vector3, clearance: float = 0.0) -> Dictionary:
	var segment := to - from
	var length := segment.length()
	if length <= 0.01:
		return {}

	var direction := segment / length

	# Mirrors HTML sdfRaycast (last_ship_sailing.html:2076-2095): if the origin
	# is already outside the playable cavity, the bullet / ray has been in a
	# wall since before this frame, so report an immediate hit 4 units ahead
	# (capped to the segment). Previously this branch returned {} and let the
	# shot pass through every subsequent wall, which is the "shoots through
	# walls" bug: a ship clipping the hull for one frame would fire bullets
	# that ignored every wall for the rest of their lifetime because the
	# origin kept testing as outside.
	if not contains_point(from, clearance):
		var hit_dist := minf(4.0, length)
		return {"point": from + direction * hit_dist, "distance": hit_dist}

	# Tighter sampling (<= 16 units per step, vs HTML's 8-unit sphere-trace
	# minimum) so fast projectiles or hitscans cannot skip thin sections of
	# the hull between samples. Bisection refinement stays at 8 rounds.
	var prev := from
	var prev_inside := true
	var steps := maxi(6, int(ceil(length / 16.0)))
	for index in range(1, steps + 1):
		var t := float(index) / float(steps)
		var sample := from.lerp(to, t)
		var inside := contains_point(sample, clearance)
		if prev_inside and not inside:
			var low := prev
			var high := sample
			for _refine in range(8):
				var mid := low.lerp(high, 0.5)
				if contains_point(mid, clearance):
					low = mid
				else:
					high = mid
			return {"point": low, "distance": from.distance_to(low)}
		prev = sample
		prev_inside = inside

	return {}

func segment_is_clear(from: Vector3, to: Vector3, clearance: float = 0.0) -> bool:
	return raycast_wall(from, to, clearance).is_empty()

func get_navigation_target(from: Vector3, target: Vector3, source_team: int) -> Vector3:
	if segment_is_clear(from, target, 24.0):
		return target

	if corridor_points.is_empty():
		return constrain_point(target, 24.0)

	var desired_team := "B" if source_team == PlayerShip.TEAM_PLAYER else "A"
	var best_point := target
	var best_score := INF

	for point_data in corridor_points:
		var point := Vector3(point_data["position"])
		var score := from.distance_to(point) * 1.15 + point.distance_to(target) * 0.85
		if str(point_data.get("team", "")) == desired_team:
			score -= 160.0
		if str(point_data.get("room_type", "")) == "tunnel":
			score -= 22.0
		if score < best_score:
			best_score = score
			best_point = point

	return best_point

func _build_tunnel_segments(raw_tunnels: Array) -> void:
	for tunnel_data in raw_tunnels:
		var tunnel: Dictionary = tunnel_data
		var path: Array = tunnel.get("path", [])
		var radius := float(tunnel.get("radius", DEFAULT_TUNNEL_RADIUS))
		for index in range(path.size() - 1):
			var a := Vector3(path[index])
			var b := Vector3(path[index + 1])
			var length := a.distance_to(b)
			if length <= 10.0:
				continue
			tunnel_segments.append({
				"a": a,
				"b": b,
				"radius": radius,
				"length": length
			})

func _compute_bounds() -> void:
	var min_corner := Vector3(INF, INF, INF)
	var max_corner := Vector3(-INF, -INF, -INF)
	var padding := 60.0

	for room_data in rooms:
		var room: Dictionary = room_data
		var center := Vector3(room.get("position", Vector3.ZERO))
		var radius := float(room.get("radius", 0.0)) + padding
		min_corner = min_corner.min(center - Vector3.ONE * radius)
		max_corner = max_corner.max(center + Vector3.ONE * radius)

	for segment_data in tunnel_segments:
		var segment: Dictionary = segment_data
		var radius := float(segment.get("radius", DEFAULT_TUNNEL_RADIUS)) + padding
		var expansion := Vector3.ONE * radius
		min_corner = min_corner.min(Vector3(segment["a"]) - expansion)
		min_corner = min_corner.min(Vector3(segment["b"]) - expansion)
		max_corner = max_corner.max(Vector3(segment["a"]) + expansion)
		max_corner = max_corner.max(Vector3(segment["b"]) + expansion)

	bounds_min = min_corner
	bounds_max = max_corner

func _build_visuals() -> void:
	_nexus_wall_material = _build_nexus_wall_material()

	# Hull root: CSGCombiner3D baked as a UNION of every room sphere and every
	# tunnel cylinder. One continuous hull mesh; tunnel end caps dissolve inside
	# the rooms they connect, overlapping spheres merge into a single cavity, and
	# the resulting surface matches the logical union used by contains_point /
	# constrain_point / raycast_wall. What the player sees is what they collide
	# with, which is what the HTML build got from worldSDF + Marching Cubes but
	# without a custom MC port (last_ship_sailing.html:1960-2006, 2048-2095).
	# cull_disabled on nexus_wall.gdshader keeps the interior view correct.
	var hull_root := CSGCombiner3D.new()
	hull_root.name = "Hull"
	hull_root.operation = CSGShape3D.OPERATION_UNION
	hull_root.use_collision = false
	hull_root.material_override = _nexus_wall_material
	add_child(hull_root)

	var room_root := Node3D.new()
	room_root.name = "Rooms"
	add_child(room_root)

	var marker_root := Node3D.new()
	marker_root.name = "Markers"
	add_child(marker_root)

	var detail_root := Node3D.new()
	detail_root.name = "Detail"
	add_child(detail_root)

	for room_data in rooms:
		var room: Dictionary = room_data
		var center := Vector3(room.get("position", Vector3.ZERO))
		var radius := float(room.get("radius", 0.0))

		var room_csg := CSGSphere3D.new()
		room_csg.radius = radius
		room_csg.radial_segments = 32
		room_csg.rings = 16
		room_csg.position = center
		room_csg.operation = CSGShape3D.OPERATION_UNION
		hull_root.add_child(room_csg)

		var room_light := OmniLight3D.new()
		room_light.position = center
		room_light.light_color = _team_color(str(room.get("team", ""))).lerp(Color(0.45, 0.62, 0.95, 1.0), 0.4)
		room_light.light_energy = 0.85
		room_light.omni_range = radius * 1.45
		room_root.add_child(room_light)

		var marker := MeshInstance3D.new()
		var marker_mesh := CylinderMesh.new()
		marker_mesh.top_radius = radius * 0.16
		marker_mesh.bottom_radius = radius * 0.16
		marker_mesh.height = radius * 0.14
		marker.mesh = marker_mesh
		marker.position = center
		marker.material_override = _make_marker_material(str(room.get("team", "")))
		marker_root.add_child(marker)

		_add_room_detail(detail_root, center, radius, str(room.get("team", "")), str(room.get("id", "")))

	for segment_data in tunnel_segments:
		var segment: Dictionary = segment_data
		var a := Vector3(segment["a"])
		var b := Vector3(segment["b"])
		var radius := float(segment.get("radius", DEFAULT_TUNNEL_RADIUS))

		var tunnel_csg := CSGCylinder3D.new()
		tunnel_csg.radius = radius
		tunnel_csg.height = a.distance_to(b)
		tunnel_csg.sides = 32
		tunnel_csg.transform = _segment_transform(a, b)
		tunnel_csg.operation = CSGShape3D.OPERATION_UNION
		hull_root.add_child(tunnel_csg)

		_add_tunnel_beacons(detail_root, a, b, radius)

func _generate_corridor_points() -> void:
	for room_data in rooms:
		var room: Dictionary = room_data
		var center := Vector3(room.get("position", Vector3.ZERO))
		var radius := float(room.get("radius", 0.0))
		var count := maxi(8, int(radius / 30.0))
		for _index in range(count):
			var point := center + _random_point_in_sphere(radius * 0.7)
			var entry := {
				"position": point,
				"team": room.get("team", null),
				"room_type": "room",
				"room_id": str(room.get("id", "room"))
			}
			corridor_points.append(entry)
			var team_key := str(room.get("team", ""))
			if spawn_points.has(team_key):
				spawn_points[team_key].append(entry)

	for segment_data in tunnel_segments:
		var segment: Dictionary = segment_data
		var a := Vector3(segment["a"])
		var b := Vector3(segment["b"])
		var length := a.distance_to(b)
		var steps := maxi(3, int(length / 80.0))
		var radius := float(segment.get("radius", DEFAULT_TUNNEL_RADIUS))
		for step_index in range(steps + 1):
			var t := float(step_index) / float(steps)
			var center := a.lerp(b, t)
			var point := center + Vector3(
				_rng.randf_range(-radius * 0.35, radius * 0.35),
				_rng.randf_range(-radius * 0.25, radius * 0.25),
				_rng.randf_range(-radius * 0.35, radius * 0.35)
			)
			corridor_points.append({
				"position": point,
				"team": null,
				"room_type": "tunnel"
			})

func _segment_transform(a: Vector3, b: Vector3) -> Transform3D:
	var axis := (b - a).normalized()
	var side := axis.cross(Vector3.FORWARD)
	if side.length_squared() < 0.001:
		side = axis.cross(Vector3.RIGHT)
	side = side.normalized()
	var forward := side.cross(axis).normalized()
	var basis := Basis(side, axis, forward).orthonormalized()
	return Transform3D(basis, (a + b) * 0.5)

func _team_color(team: String) -> Color:
	if team == "A":
		return Color(1.0, 0.42, 0.42, 1.0)
	if team == "B":
		return Color(0.38, 0.92, 0.58, 1.0)
	return Color(0.42, 0.62, 1.0, 1.0)

func _build_nexus_wall_material() -> ShaderMaterial:
	# Mirrors the HTML ShaderMaterial in createMeshFromPositions(): pad to 8 entries,
	# cycle the palette, and park unused slots far below the map so nearest-room
	# lookups never pick them.
	var mat := ShaderMaterial.new()
	mat.shader = NEXUS_WALL_SHADER

	var centers: Array[Vector3] = []
	var colors: Array[Color] = []
	var radii: Array[float] = []
	var room_count := mini(rooms.size(), 8)
	centers.resize(8)
	colors.resize(8)
	radii.resize(8)

	for i in range(8):
		if i < room_count:
			var room: Dictionary = rooms[i]
			centers[i] = Vector3(room.get("position", Vector3.ZERO))
			colors[i] = NEXUS_ROOM_PALETTE[i % NEXUS_ROOM_PALETTE.size()]
			radii[i] = float(room.get("radius", 0.0))
		else:
			centers[i] = Vector3(0.0, 99999.0, 0.0)
			colors[i] = Color(0.0, 0.0, 0.0, 1.0)
			radii[i] = 0.0

	# Godot shader uniform arrays accept PackedVector3Array / PackedColorArray /
	# PackedFloat32Array directly for vec3[]/vec3[]:source_color/float[] slots.
	var centers_packed := PackedVector3Array(centers)
	var colors_packed := PackedColorArray(colors)
	var radii_packed := PackedFloat32Array(radii)

	mat.set_shader_parameter("room_centers", centers_packed)
	mat.set_shader_parameter("room_colors", colors_packed)
	mat.set_shader_parameter("room_radii", radii_packed)
	mat.set_shader_parameter("room_count", room_count)
	mat.set_shader_parameter("time_scale", 1.0)
	mat.set_shader_parameter("fractal_gain", 3.4)
	return mat

func _make_chamber_material(team: String) -> StandardMaterial3D:
	var color := _team_color(team)
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.blend_mode = BaseMaterial3D.BLEND_MODE_MIX
	material.cull_mode = BaseMaterial3D.CULL_DISABLED
	material.albedo_color = Color(color.r * 0.45, color.g * 0.45, color.b * 0.55, 0.12)
	material.emission_enabled = true
	material.emission = color
	material.emission_energy_multiplier = 1.2
	return material

func _make_tunnel_material() -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.blend_mode = BaseMaterial3D.BLEND_MODE_MIX
	material.cull_mode = BaseMaterial3D.CULL_DISABLED
	material.albedo_color = Color(0.14, 0.20, 0.28, 0.10)
	material.emission_enabled = true
	material.emission = Color(0.30, 0.52, 0.90, 1.0)
	material.emission_energy_multiplier = 0.9
	return material

func _make_marker_material(team: String) -> StandardMaterial3D:
	var color := _team_color(team)
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	material.cull_mode = BaseMaterial3D.CULL_DISABLED
	material.albedo_color = Color(color.r, color.g, color.b, 0.75)
	material.emission_enabled = true
	material.emission = color
	material.emission_energy_multiplier = 2.2
	return material

func _make_emissive_material(color: Color, alpha: float, emission_energy: float, additive := true) -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.blend_mode = BaseMaterial3D.BLEND_MODE_ADD if additive else BaseMaterial3D.BLEND_MODE_MIX
	material.cull_mode = BaseMaterial3D.CULL_DISABLED
	material.albedo_color = Color(color.r, color.g, color.b, alpha)
	material.emission_enabled = true
	material.emission = color
	material.emission_energy_multiplier = emission_energy
	return material

func _add_room_detail(parent: Node3D, center: Vector3, radius: float, team: String, room_id: String) -> void:
	var detail_color := _team_color(team).lerp(Color(0.55, 0.72, 1.0, 1.0), 0.45)

	var shell := MeshInstance3D.new()
	var shell_mesh := SphereMesh.new()
	shell_mesh.radius = radius * 1.03
	shell_mesh.height = radius * 2.06
	shell.mesh = shell_mesh
	shell.position = center
	shell.material_override = _make_emissive_material(detail_color, 0.035, 0.7, false)
	parent.add_child(shell)

	var strut_material := _make_emissive_material(detail_color, 0.32, 1.5)
	var strut_radius := maxf(6.0, radius * 0.028)
	var strut_length := radius * 1.55
	_add_strut(parent, center, strut_length, strut_radius, strut_material, Vector3.ZERO)
	_add_strut(parent, center, strut_length, strut_radius, strut_material, Vector3(0.0, 0.0, deg_to_rad(90.0)))
	_add_strut(parent, center, strut_length, strut_radius, strut_material, Vector3(deg_to_rad(90.0), 0.0, 0.0))

	var beacon_count := maxi(4, int(radius / 90.0))
	for beacon_index in range(beacon_count):
		var angle := TAU * float(beacon_index) / float(beacon_count)
		var beacon_pos := center + Vector3(cos(angle), sin(angle * 0.5) * 0.35, sin(angle)) * radius * 0.68
		var beacon := MeshInstance3D.new()
		var beacon_mesh := SphereMesh.new()
		beacon_mesh.radius = maxf(4.0, radius * 0.025)
		beacon_mesh.height = beacon_mesh.radius * 2.0
		beacon.mesh = beacon_mesh
		beacon.position = beacon_pos
		beacon.material_override = _make_emissive_material(detail_color.lightened(0.18), 0.75, 2.1)
		parent.add_child(beacon)

	if room_id == "center":
		_add_reactor_core(parent, center, radius, detail_color)

func _add_strut(parent: Node3D, position: Vector3, length: float, radius: float, material: Material, rotation: Vector3) -> void:
	var strut := MeshInstance3D.new()
	var mesh := CylinderMesh.new()
	mesh.top_radius = radius
	mesh.bottom_radius = radius
	mesh.height = length
	strut.mesh = mesh
	strut.position = position
	strut.rotation = rotation
	strut.material_override = material
	parent.add_child(strut)

func _add_reactor_core(parent: Node3D, center: Vector3, radius: float, base_color: Color) -> void:
	var reactor_root := Node3D.new()
	reactor_root.position = center
	parent.add_child(reactor_root)

	var reactor_material := _make_emissive_material(base_color.lightened(0.22), 0.48, 2.3)
	var core_column := MeshInstance3D.new()
	var core_mesh := CylinderMesh.new()
	core_mesh.top_radius = radius * 0.10
	core_mesh.bottom_radius = radius * 0.14
	core_mesh.height = radius * 1.15
	core_column.mesh = core_mesh
	core_column.material_override = reactor_material
	reactor_root.add_child(core_column)

	var core_orb := MeshInstance3D.new()
	var orb_mesh := SphereMesh.new()
	orb_mesh.radius = radius * 0.18
	orb_mesh.height = radius * 0.36
	core_orb.mesh = orb_mesh
	core_orb.position = Vector3(0.0, radius * 0.08, 0.0)
	core_orb.material_override = _make_emissive_material(base_color.lightened(0.35), 0.78, 3.2)
	reactor_root.add_child(core_orb)

	var reactor_light := OmniLight3D.new()
	reactor_light.light_color = base_color.lightened(0.25)
	reactor_light.light_energy = 1.6
	reactor_light.omni_range = radius * 1.7
	reactor_root.add_child(reactor_light)

func _add_tunnel_beacons(parent: Node3D, a: Vector3, b: Vector3, radius: float) -> void:
	var length := a.distance_to(b)
	var steps := maxi(2, int(length / 180.0))
	var beacon_color := Color(0.36, 0.58, 0.96, 1.0)
	var beacon_material := _make_emissive_material(beacon_color, 0.70, 1.9)
	for step in range(1, steps):
		var t := float(step) / float(steps)
		var pos := a.lerp(b, t)
		var offset_dir := (b - a).cross(Vector3.UP).normalized()
		if offset_dir.length_squared() < 0.001:
			offset_dir = Vector3.RIGHT
		var beacon := MeshInstance3D.new()
		var beacon_mesh := SphereMesh.new()
		beacon_mesh.radius = maxf(3.0, radius * 0.045)
		beacon_mesh.height = beacon_mesh.radius * 2.0
		beacon.mesh = beacon_mesh
		beacon.position = pos + offset_dir * radius * 0.62
		beacon.material_override = beacon_material
		parent.add_child(beacon)

func _random_point_in_sphere(radius: float) -> Vector3:
	var direction := Vector3(
		_rng.randf_range(-1.0, 1.0),
		_rng.randf_range(-1.0, 1.0),
		_rng.randf_range(-1.0, 1.0)
	)
	if direction.length_squared() < 0.001:
		direction = Vector3.FORWARD
	return direction.normalized() * radius * pow(_rng.randf(), 0.33333334)

func _distance_to_segment(point: Vector3, a: Vector3, b: Vector3) -> float:
	return point.distance_to(_closest_point_on_segment(point, a, b))

func _closest_point_on_segment(point: Vector3, a: Vector3, b: Vector3) -> Vector3:
	var ab := b - a
	var denom := ab.length_squared()
	if denom <= 0.0001:
		return a
	var t := clampf((point - a).dot(ab) / denom, 0.0, 1.0)
	return a + ab * t
