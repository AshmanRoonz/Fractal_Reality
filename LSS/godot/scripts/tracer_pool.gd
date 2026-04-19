class_name TracerPool
extends MultiMeshInstance3D

var max_segments := 128
var segments: Array = []

func configure(segment_capacity: int, opacity: float) -> void:
	max_segments = segment_capacity
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_colors = true
	mm.instance_count = max_segments

	var beam_mesh := BoxMesh.new()
	beam_mesh.size = Vector3.ONE
	mm.mesh = beam_mesh
	multimesh = mm

	var beam_material := StandardMaterial3D.new()
	beam_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	beam_material.vertex_color_use_as_albedo = true
	beam_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	beam_material.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	beam_material.no_depth_test = true
	beam_material.cull_mode = BaseMaterial3D.CULL_DISABLED
	beam_material.albedo_color = Color(1, 1, 1, opacity)
	material_override = beam_material

	for i in range(max_segments):
		multimesh.set_instance_color(i, Color(0, 0, 0, 0))
		multimesh.set_instance_transform(i, Transform3D.IDENTITY)

func spawn_segment(from: Vector3, to: Vector3, color: Color, width: float, lifetime: float) -> void:
	if segments.size() >= max_segments:
		segments.pop_front()
	segments.append({
		"from": from,
		"to": to,
		"color": color,
		"width": width,
		"lifetime": maxf(0.03, lifetime),
		"age": 0.0
	})

func _process(delta: float) -> void:
	if multimesh == null:
		return

	for index in range(segments.size() - 1, -1, -1):
		var segment: Dictionary = segments[index]
		segment["age"] = float(segment["age"]) + delta
		if float(segment["age"]) >= float(segment["lifetime"]):
			segments.remove_at(index)
			continue
		segments[index] = segment

	var instance_index := 0
	for segment in segments:
		var from: Vector3 = segment["from"]
		var to: Vector3 = segment["to"]
		var direction := to - from
		var length := direction.length()
		if length < 0.01:
			continue

		var up := Vector3.UP
		var dir_normalized := direction / length
		if absf(dir_normalized.dot(up)) > 0.98:
			up = Vector3.RIGHT

		var basis := Transform3D.IDENTITY.looking_at(dir_normalized, up).basis
		var width := float(segment["width"])
		basis = basis.scaled(Vector3(width, width, length))
		var midpoint := from.lerp(to, 0.5)
		multimesh.set_instance_transform(instance_index, Transform3D(basis, midpoint))

		var life_t := 1.0 - (float(segment["age"]) / float(segment["lifetime"]))
		var color: Color = segment["color"]
		multimesh.set_instance_color(instance_index, Color(color.r, color.g, color.b, life_t * life_t))
		instance_index += 1
		if instance_index >= max_segments:
			break

	for clear_index in range(instance_index, max_segments):
		multimesh.set_instance_color(clear_index, Color(0, 0, 0, 0))
