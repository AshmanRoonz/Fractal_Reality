extends SceneTree

# Smoke test for environmental hazards (Task #49 validation).
# Covers: DestructibleObstacle configure/collide/take_damage flow, ClusterObstacle
# spawn + break_apart + tick. Ships-vs-obstacle driving is smoke-tested in
# main.gd's _tick_obstacle wiring (parse-only coverage here; full integration
# is Task #50).

const DestructibleObstacle = preload("res://scripts/destructible_obstacle.gd")
const ClusterObstacle = preload("res://scripts/cluster_obstacle.gd")
const MainScript = preload("res://scripts/main.gd")

var _ok := true

func _fail(msg: String) -> void:
	push_error(msg)
	_ok = false

func _init() -> void:
	print("=== Hazard smoke test ===")

	# Standalone destructible: configure, collide at center, collide off-center,
	# destroy via take_damage.
	var d := DestructibleObstacle.new()
	get_root().add_child(d)
	d.configure(Vector3.ZERO, "", 60.0, 0xaa4433)
	if not d.is_alive:
		_fail("destructible should be alive after configure")
	if d.collision_radius < 1.0:
		_fail("collision_radius should be populated (%f)" % d.collision_radius)
	if d.hp <= 0.0 or d.hp != d.max_hp:
		_fail("hp should be seeded to max (hp=%f, max=%f)" % [d.hp, d.max_hp])
	print("Destructible configure: OK (hp=%.0f radius=%.1f shape=%s)" % [d.hp, d.collision_radius, d.shape_type])

	var result: Dictionary = d.collide_entity(Vector3.ZERO, Vector3.ZERO, 10.0)
	if not result.get("collided", false):
		_fail("center-overlap collision should register")
	var pos_out: Vector3 = result.get("position", Vector3.ZERO)
	if pos_out.y < 1.0:
		_fail("center overlap should nudge entity up (got %s)" % str(pos_out))
	print("Collide center (center overlap → up nudge): OK")

	var result2: Dictionary = d.collide_entity(Vector3(30.0, 0.0, 0.0), Vector3(-100.0, 0.0, 0.0), 10.0)
	if not result2.get("collided", false):
		_fail("side-on collision should register")
	var vel_out: Vector3 = result2.get("velocity", Vector3.ZERO)
	# Incoming v_dot_n = -100; bounce gives new_vel.x = -100 - (-100)*1.3 = +30.
	if absf(vel_out.x - 30.0) > 0.01:
		_fail("bounce should flip + amplify 1.3x (expected 30.0, got %s)" % str(vel_out))
	var ram: float = result2.get("ram_damage", -1.0)
	# impact_speed = 100, above threshold 50 → ram = 100 * 0.4 = 40.
	if absf(ram - 40.0) > 0.01:
		_fail("ram damage at impact 100 should be 40.0 (got %f)" % ram)
	print("Collide bounce (1.3x reflection + ram): OK")

	d.take_damage(99999.0, Vector3(1.0, 0.0, 0.0))
	if d.is_alive:
		_fail("destructible should be dead after massive damage")
	print("Destroy via take_damage: OK")

	# Cluster: spawn, verify child count and cluster linkage, trigger break_apart,
	# advance ticks to move fragments.
	var hazard_root := Node3D.new()
	get_root().add_child(hazard_root)
	var c := ClusterObstacle.new()
	hazard_root.add_child(c)
	c.configure(Vector3(100.0, 0.0, 0.0), 60.0, hazard_root)
	if c.children.size() < 5 or c.children.size() > 10:
		_fail("cluster child count should be 5-10 (got %d)" % c.children.size())
	for child in c.children:
		if child == null or not is_instance_valid(child):
			_fail("cluster child should be valid")
			continue
		if child.cluster != c:
			_fail("child.cluster back-reference should point at parent cluster")
	print("Cluster spawn: OK (count=%d)" % c.children.size())

	c.break_apart(c.original_pos, Vector3(1.0, 0.0, 0.0))
	if not c.broken:
		_fail("cluster should be marked broken")
	var broken_count := 0
	for child in c.children:
		if child.broken:
			broken_count += 1
	if broken_count == 0:
		_fail("at least one child should be in fragment mode")
	print("Cluster break_apart: OK (%d/%d children in fragment mode)" % [broken_count, c.children.size()])

	# Damaging a still-intact cluster child should trigger cluster shatter.
	var c2 := ClusterObstacle.new()
	hazard_root.add_child(c2)
	c2.configure(Vector3(-100.0, 0.0, 0.0), 60.0, hazard_root)
	var first_child: DestructibleObstacle = c2.children[0]
	first_child.take_damage(10.0, Vector3(1.0, 0.0, 0.0))
	if not c2.broken:
		_fail("cluster should shatter when a child takes damage while intact")
	print("Child-hit cluster shatter: OK")

	if _ok:
		print("=== RESULT: PASS ===")
		quit(0)
	else:
		push_error("test_hazards FAILED")
		quit(1)
