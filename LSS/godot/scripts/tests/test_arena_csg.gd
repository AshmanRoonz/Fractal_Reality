extends SceneTree

const ArenaMap = preload("res://scripts/arena_map.gd")

func _init() -> void:
	var arena := ArenaMap.new()
	root.add_child(arena)
	arena.build_map("hourglass")

	var hull: CSGCombiner3D = arena.get_node_or_null("Hull")
	assert(hull != null, "Hull CSGCombiner3D not found")
	var sphere_count := 0
	var cylinder_count := 0
	for child in hull.get_children():
		if child is CSGSphere3D:
			sphere_count += 1
		elif child is CSGCylinder3D:
			cylinder_count += 1
	print("HULL: OK (spheres=", sphere_count, " cylinders=", cylinder_count, ")")
	assert(sphere_count == arena.rooms.size(), "Sphere count mismatch")
	assert(cylinder_count == arena.tunnel_segments.size(), "Cylinder count mismatch")

	# Process a couple of frames to let CSGCombiner3D bake.
	await process_frame
	await process_frame
	await process_frame

	var meshes := hull.get_meshes()
	print("BAKE: meshes returned ", meshes.size(), " entries")

	# Logical union sanity: each room center lies inside, a point far outside does not.
	var first_room := arena.rooms[0] as Dictionary
	var center := Vector3(first_room.get("position", Vector3.ZERO))
	assert(arena.contains_point(center, 0.0), "Room center should be inside union")
	assert(not arena.contains_point(center + Vector3(10000.0, 0.0, 0.0), 0.0), "Faraway point should be outside")
	print("CONTAINS_POINT: OK (center inside, 10km away outside)")

	# constrain_point should snap a wildly-outside point back into the hull.
	var far := center + Vector3(5000.0, 0.0, 0.0)
	var snapped := arena.constrain_point(far, 0.0)
	assert(arena.contains_point(snapped, 0.0), "constrain_point should land inside the union")
	print("CONSTRAIN_POINT: OK")

	# Raycast regression: bullet fired from inside the room toward +Y (straight
	# up through the room ceiling). Use Y so we don't clip into neighbouring
	# rooms at the "ne"/"se" corners.
	print("RAYCAST inside->outside: starting")
	var room_radius := float(first_room.get("radius", 0.0))
	var inside_target := center + Vector3(0.0, room_radius * 4.0, 0.0)
	var inside_ray := arena.raycast_wall(center, inside_target, 12.0)
	print("RAYCAST inside->outside: hit=", inside_ray)
	assert(not inside_ray.is_empty(), "Ray from inside to far outside should hit the wall")
	var inside_hit_dist := float(inside_ray.get("distance", 0.0))
	assert(inside_hit_dist > 0.0 and inside_hit_dist <= room_radius * 4.0, "Inside->outside hit distance should land inside the segment")
	print("RAYCAST inside->outside: OK (distance=", inside_hit_dist, ")")

	# Raycast regression #2: bullet whose ORIGIN is outside the hull must still
	# register a wall (match HTML sdfRaycast t=4 behaviour). Before the fix
	# raycast_wall returned {} and the bullet travelled unchecked.
	print("RAYCAST outside-origin: starting")
	var outside_origin := center + Vector3(0.0, room_radius * 3.0, 0.0)
	var contains := arena.contains_point(outside_origin, 12.0)
	print("RAYCAST outside-origin: contains_point(outside)=", contains)
	assert(not contains, "Test origin should be outside the hull")
	var outside_ray := arena.raycast_wall(outside_origin, outside_origin + Vector3(0.0, 1000.0, 0.0), 12.0)
	print("RAYCAST outside-origin: hit=", outside_ray)
	assert(not outside_ray.is_empty(), "Ray originating outside must report an immediate hit")
	var outside_hit_dist := float(outside_ray.get("distance", -1.0))
	assert(outside_hit_dist >= 0.0 and outside_hit_dist <= 4.0001, "Outside-origin hit should land within 4-unit grace: got " + str(outside_hit_dist))
	print("RAYCAST outside-origin: OK (distance=", outside_hit_dist, ")")

	print("RESULT: PASS")
	quit()
