class_name ClusterObstacle
extends Node3D

# Port of HTML last_ship_sailing.html:4326-4471 (ClusterObstacle).
# A cluster spawns 5-10 DestructibleObstacle children orbiting in a rigid
# group around a shared center. Ships bouncing off the pack at >80 u/s
# impact speed OR any weapon damage to any child triggers break_apart(),
# which scatters every child as a drifting, self-detonating fragment.
# Once all children are dead the cluster queues a 30s full respawn of the
# whole pack.
#
# Per-frame ticking, ship-collision resolution, and weapon hits against
# individual children are driven by main.gd, which walks the children list
# directly (kept authoritative here so respawn doesn't have to sync a
# parallel array).

const DestructibleObstacle = preload("res://scripts/destructible_obstacle.gd")

const OBSTACLE_COLORS: Array[int] = [0xaa4433, 0xccaa22, 0x885522, 0x447788, 0x778844]

var original_pos: Vector3
var cluster_scale: float = 60.0
var is_alive: bool = true
var broken: bool = false
var respawn_timer: float = 0.0
var respawn_time: float = 30.0
var rot_speed: Vector3 = Vector3.ZERO
# Stored explicitly instead of using Node3D.rotation so the rotation chain is
# independent of any parent transform and matches the HTML's scene-space
# Euler tracking (HTML doesn't parent children under the cluster mesh).
var cluster_rotation: Vector3 = Vector3.ZERO
var base_color: int = 0xaa4433
var children: Array[DestructibleObstacle] = []

# Parent node the DestructibleObstacle children are attached to. Set by main
# when the cluster is spawned so child respawns can re-add themselves to the
# same scene-graph slot. Kept as a weak-ish ref: if the parent has been freed
# the respawn is skipped.
var _hazard_root: Node3D = null

func configure(pos: Vector3, cluster_size: float, hazard_root: Node3D) -> void:
	original_pos = pos
	position = pos
	cluster_scale = cluster_size
	_hazard_root = hazard_root
	rot_speed = Vector3(
		(randf() - 0.5) * 0.15,
		(randf() - 0.5) * 0.20,
		(randf() - 0.5) * 0.15
	)
	cluster_rotation = Vector3(
		randf() * TAU,
		randf() * TAU,
		randf() * TAU
	)
	base_color = OBSTACLE_COLORS[randi() % OBSTACLE_COLORS.size()]
	_build_children()

func _build_children() -> void:
	# Clear any stragglers before rebuilding (used by respawn).
	for child in children:
		if child != null and is_instance_valid(child):
			child.queue_free()
	children.clear()

	var count := 5 + (randi() % 6)  # 5-10 pieces
	var pack_r := cluster_scale * 0.70
	var avg_child_scale := cluster_scale * (0.22 + randf() * 0.10)
	var q := Quaternion.from_euler(cluster_rotation)

	for i in range(count):
		# Rejection-sample an offset inside the packing sphere.
		var offset := Vector3.ZERO
		var tries := 0
		while true:
			offset = Vector3(
				(randf() - 0.5) * 2.0 * pack_r,
				(randf() - 0.5) * 2.0 * pack_r,
				(randf() - 0.5) * 2.0 * pack_r
			)
			tries += 1
			if offset.length() <= pack_r or tries >= 12:
				break

		var rotated_offset := q * offset
		var child_pos := original_pos + rotated_offset
		var child_scale_val := avg_child_scale * (0.75 + randf() * 0.55)

		var child := DestructibleObstacle.new()
		child.configure(child_pos, "", child_scale_val, base_color)
		child.cluster = self
		child.local_offset = offset  # body-frame offset, pre-rotation
		# Cluster children are weaker than standalone pieces so a single
		# weapon hit can start the shatter cascade.
		child.max_hp = 80.0 + child_scale_val * 2.0
		child.hp = child.max_hp
		child.fragment_max_life = 10.0 + randf() * 6.0

		if _hazard_root != null and is_instance_valid(_hazard_root):
			_hazard_root.add_child(child)
		children.append(child)

func update(delta: float) -> void:
	if not is_alive:
		respawn_timer -= delta
		if respawn_timer <= 0.0:
			respawn()
		return

	if not broken:
		cluster_rotation.x += rot_speed.x * delta
		cluster_rotation.y += rot_speed.y * delta
		cluster_rotation.z += rot_speed.z * delta
		var q := Quaternion.from_euler(cluster_rotation)
		# Pin intact children to their rotated body-frame slots before main
		# does anything else with them this frame.
		for child in children:
			if child == null or not is_instance_valid(child):
				continue
			if not child.is_alive or child.broken:
				continue
			var rotated := q * child.local_offset
			child.position = original_pos + rotated

	# Once every child is gone, schedule the full respawn.
	var any_alive := false
	for child in children:
		if child != null and is_instance_valid(child) and child.is_alive:
			any_alive = true
			break
	if not any_alive:
		is_alive = false
		respawn_timer = respawn_time

func break_apart(hit_pos: Vector3, hit_dir: Vector3) -> void:
	if broken:
		return
	broken = true
	var src := hit_pos if hit_pos != Vector3.ZERO else original_pos
	for child in children:
		if child == null or not is_instance_valid(child):
			continue
		if not child.is_alive:
			continue
		var outward := child.position - src
		if outward.length_squared() < 0.001:
			outward = Vector3(randf() - 0.5, randf() - 0.5, randf() - 0.5)
		outward = outward.normalized()
		var scatter := Vector3(
			randf() - 0.5,
			randf() - 0.5,
			randf() - 0.5
		).normalized()
		var speed := 45.0 + randf() * 65.0
		var vel := outward * (speed * 0.7) + scatter * (speed * 0.4)
		if hit_dir.length_squared() > 0.0001:
			vel += hit_dir * 25.0
		child.begin_fragment(vel, 10.0 + randf() * 6.0)

func respawn() -> void:
	# Fully tear down the old pack and rebuild at the original position.
	for child in children:
		if child != null and is_instance_valid(child):
			child.queue_free()
	children.clear()
	broken = false
	is_alive = true
	position = original_pos
	cluster_rotation = Vector3(
		randf() * TAU,
		randf() * TAU,
		randf() * TAU
	)
	_build_children()
