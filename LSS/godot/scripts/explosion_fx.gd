extends Node3D
class_name ExplosionFX

# Port of HTML last_ship_sailing.html:3836-4032 (spawnExplosion +
# spawnDynamicLight + updateDynamicLights) and 5113-5215 (updateEffects, the
# subset that animates explosion-spawned meshes: explosionFlash, explosionFire,
# shockwave, smoke, debris, shieldHit). One self-contained child of main that
# handles the full visual cascade.
#
# Design notes:
#   - HTML uses pooled THREE.PointLights (MAX_LIGHTS = 8) plus an "active"
#     queue that steals the oldest entry when the pool runs dry. We mirror that
#     with OmniLight3D.
#   - The five-phase explosion (flash core, billboarded disc, fireball + dark
#     core, shockwave rings, smoke, embers + debris) creates short-lived
#     MeshInstance3D nodes parented under this node and animates them in
#     _process. A small per-effect record array drives the animation; meshes
#     are queue_freed when the lifetime expires.
#   - Headless safety: this module deliberately AVOIDS `if not is_inside_tree():`
#     guards because Godot's `-s scene_tree.gd` mode reports is_inside_tree() ==
#     false even after get_root().add_child(node) (the SceneTree itself is
#     "inactive" from the node's perspective). Instead we guard on the actual
#     preconditions: spawn_dynamic_light returns early when both the pool and
#     active list are empty (i.e. _ready never built the pool), and ember
#     particle cleanup uses GPUParticles3D.finished rather than
#     get_tree().create_timer so we don't depend on a live tree.
#   - We do NOT recreate THREE.js's lookAt(camera) per frame for "billboard"
#     effects. Godot has BaseMaterial3D.BILLBOARD_ENABLED which gives the same
#     visual without per-frame work; we use it for the lens-flare disc and the
#     shockwave flat ring.

const MAX_LIGHTS := 8
const MAX_EFFECTS := 200  # HTML cap is 350; we trim because Godot effects are
                         # heavier than the THREE.js JS-record approach.
const MAX_EMBERS := 18
const MAX_CHUNKS := 6
const MAX_IMPACT_SPARKS := 12
# HTML spawnDamageSmoke thresholds (5238, 5257): smoke below 50% health, fire
# added below 25%. Per-frame probabilities in the HTML are intensity*0.4 for
# smoke and intensity*0.3 for fire where intensity = 1 - hp/0.5.
const DAMAGE_SMOKE_THRESHOLD := 0.5
const DAMAGE_FIRE_THRESHOLD := 0.25
const DAMAGE_SMOKE_PROB_MAX := 0.4
const DAMAGE_FIRE_PROB_MAX := 0.3

# Colors used at multiple sites in this module.
const FLASH_COLOR := Color(1.0, 1.0, 1.0, 1.0)
const FLARE_COLOR := Color(1.0, 0.93, 0.75, 0.95)
const FIRE_COLOR := Color(1.0, 0.4, 0.0, 0.85)
const CORE_COLOR := Color(1.0, 0.13, 0.0, 0.6)
const SHOCKWAVE_FLAT_COLOR := Color(1.0, 0.82, 0.5, 0.95)
const SHOCKWAVE_TORUS_COLOR := Color(1.0, 0.67, 0.27, 0.8)
const SHOCKWAVE_TORUS2_COLOR := Color(1.0, 0.53, 0.2, 0.6)
const SMOKE_COLOR := Color(0.13, 0.07, 0.0, 0.4)
const EMBER_COLORS := [
	Color8(0xff, 0x88, 0x00),
	Color8(0xff, 0x44, 0x00),
	Color8(0xff, 0xcc, 0x00),
	Color8(0xff, 0x66, 0x00),
	Color8(0xff, 0xaa, 0x22),
]

# Effect-record fields:
#   node           - MeshInstance3D
#   material       - StandardMaterial3D (for opacity/color tweens)
#   type           - one of "flash", "fire", "shockwave_flat", "shockwave_torus",
#                    "smoke", "debris"
#   lifetime, age  - float seconds
#   max_size       - float (target scale for shockwave/smoke)
#   base_opacity   - float starting alpha
#   velocity       - Vector3 (debris)
#   rot_velocity   - Vector3 (smoke + debris)
var _effects: Array = []

# Light pool: each entry is { light: OmniLight3D, intensity: float,
#                              duration: float, age: float, active: bool }
var _light_pool: Array = []
var _active_lights: Array = []

# Camera reference for player-distance shake decisions; main.gd may set this.
var _player_ref: Node3D = null

func _ready() -> void:
	# Build the light pool eagerly so spawn_explosion never has to allocate
	# a PointLight at firing time. HTML does the same (MAX_LIGHTS = 8 created
	# at module load).
	for i in range(MAX_LIGHTS):
		var light := OmniLight3D.new()
		light.light_color = Color(1.0, 0.53, 0.0, 1.0)
		light.light_energy = 0.0
		light.omni_range = 30.0
		light.visible = false
		add_child(light)
		_light_pool.append({
			"light": light,
			"intensity": 0.0,
			"duration": 0.0,
			"age": 0.0,
			"active": false,
		})

func set_player_ref(p: Node3D) -> void:
	_player_ref = p

func _process(delta: float) -> void:
	_update_lights(delta)
	_update_effects(delta)

# -- Public API ------------------------------------------------------------

# spawn_explosion mirrors HTML 3893-4032. `size` defaults to 20 (matches HTML).
# Distance-based screen shake is left to the caller (main.gd already runs its
# own _shake_from_event in _blast_area); we focus on the visual cascade plus
# the dynamic-light flash/glow pair. World units in Godot are 1 to 1 with the
# HTML's three.js units; the original arena is on the same scale.
func spawn_explosion(position: Vector3, size: float = 20.0) -> void:
	# Defensive guard: if _ready never ran, the pool is empty, so all the
	# spawn_* calls below would either allocate meshes into a detached node
	# tree (add_child fails silently in -s mode) or steal a non-existent
	# light. Early-out keeps the pre-tree call a true no-op.
	if _light_pool.is_empty() and _active_lights.is_empty():
		return
	# Phase 1: white-hot flash core (sphere, no billboard)
	_spawn_flash_sphere(position, size * 0.55, 0.12, false)
	# Phase 1b: lens-flare disc (billboarded, slightly bigger and longer)
	_spawn_flash_disc(position, size * 1.6, 0.22)
	# Phase 2: fireball (orange) + inner red core
	_spawn_fire_sphere(position, size, 0.5, size * 2.5, FIRE_COLOR)
	_spawn_fire_sphere(position, size * 0.7, 0.35, size * 1.8, CORE_COLOR)
	# Phase 3: shockwave rings (only for size > 12)
	if size > 12.0:
		_spawn_shockwave_flat(position, size, 0.55, size * 6.0)
		_spawn_shockwave_torus(position, size, 0.45, size * 5.0, SHOCKWAVE_TORUS_COLOR)
		# Bigger explosions get a second perpendicular torus.
		if size > 30.0:
			_spawn_shockwave_torus(position, size, 0.55, size * 6.0, SHOCKWAVE_TORUS2_COLOR, true)
	# Phase 4: smoke cloud (size > 15 only)
	if size > 15.0:
		_spawn_smoke(position, size, 1.2, size * 4.0)
	# Phase 5: ember and debris particles. Embers use GPUParticles3D with a
	# one-shot burst; debris use individual tetrahedron MeshInstance3D so we
	# can spin them per HTML rotVel.
	var ember_count: int = mini(int(ceil(size * 0.6)), MAX_EMBERS)
	if ember_count > 0:
		_spawn_embers(position, ember_count)
	if size > 25.0:
		var chunk_count: int = mini(int(ceil(size * 0.1)), MAX_CHUNKS)
		_spawn_debris_chunks(position, chunk_count)
	# Dynamic lights: bright short flash + warm slower glow (HTML 4030-4031).
	var light_intensity: float = minf(8.0, size * 0.2)
	var light_range: float = minf(1500.0, size * 18.0)
	spawn_dynamic_light(position, Color8(0xff, 0xcc, 0x88), light_intensity * 1.5, light_range * 0.6, 0.1)
	spawn_dynamic_light(position, Color8(0xff, 0x55, 0x00), light_intensity, light_range, 0.45)

# Direct equivalent of HTML spawnDynamicLight (3855). Pulls from the pool;
# steals the oldest active light when the pool is empty.
func spawn_dynamic_light(position: Vector3, color: Color, intensity: float, range_: float, duration: float) -> void:
	# Pre-_ready guard: if the pool was never populated AND nothing is active,
	# there's nothing to take or steal. Early-out so pre-tree callers are a
	# true no-op without depending on is_inside_tree() (which returns false
	# under `-s` SceneTree mode even after add_child).
	if _light_pool.is_empty() and _active_lights.is_empty():
		return
	var slot: Dictionary
	if _light_pool.size() > 0:
		slot = _light_pool.pop_back()
	elif _active_lights.size() > 0:
		# Steal the oldest active light (HTML does pool.pop()/active.shift()).
		slot = _active_lights.pop_front()
	else:
		return
	var light: OmniLight3D = slot["light"]
	light.light_color = color
	light.light_energy = intensity
	light.omni_range = range_
	_place(light, position)
	light.visible = true
	slot["intensity"] = intensity
	slot["duration"] = maxf(0.001, duration)
	slot["age"] = 0.0
	slot["active"] = true
	_active_lights.append(slot)

# Impact spark cascade (HTML 5290-5347). Called on every bullet/projectile
# connect: bright white flash + `count` spark streaks + smaller ember burst +
# optional dark scorch puff + two dynamic lights. `spark_color` lets callers
# tint the streaks to their loadout signature; pass Color.TRANSPARENT to fall
# back to the HTML default warm palette (white-orange).
func spawn_impact_sparks(position: Vector3, count: int = 6, spark_color: Color = Color(0, 0, 0, 0)) -> void:
	# Pre-_ready guard: see spawn_dynamic_light.
	if _light_pool.is_empty() and _active_lights.is_empty():
		return
	count = clampi(count, 1, MAX_IMPACT_SPARKS)
	# White-hot impact flash (sphere, very brief).
	_spawn_flash_sphere(position, 3.0, 0.06, false)
	# Spark streaks: small bright spheres with outward velocity. HTML uses
	# speed 300-800 per axis; we match that.
	for i in range(count):
		var brightness: float = 0.8 + randf() * 0.2
		var streak_color: Color
		if spark_color.a > 0.0:
			# Loadout-tinted sparks: use the provided color directly (matches
			# main.gd's old _spawn_impact_burst behaviour for signature tint).
			streak_color = Color(spark_color.r, spark_color.g, spark_color.b, 1.0)
		else:
			# HTML default: warm white-orange with randomised green/blue.
			streak_color = Color(
				brightness,
				brightness * 0.6 + randf() * 0.2,
				brightness * 0.15,
				1.0
			)
		var mesh := SphereMesh.new()
		var radius: float = 1.2 + randf() * 0.8
		mesh.radius = radius
		mesh.height = radius * 2.0
		mesh.radial_segments = 4
		mesh.rings = 3
		var node := MeshInstance3D.new()
		node.mesh = mesh
		var mat := _make_additive_mat(streak_color, 1.0, false)
		node.material_override = mat
		add_child(node)
		_place(node, position)
		var speed: float = 300.0 + randf() * 500.0
		var vel := Vector3(
			(randf() - 0.5) * speed,
			(randf() - 0.5) * speed,
			(randf() - 0.5) * speed,
		)
		_effects.append({
			"node": node,
			"material": mat,
			"type": "spark",
			"lifetime": 0.2 + randf() * 0.3,
			"age": 0.0,
			"max_size": 0.0,
			"base_opacity": 1.0,
			"velocity": vel,
			"rot_velocity": Vector3.ZERO,
		})
	# Secondary ember burst via GPUParticles3D (HTML's secondary batched
	# particles). Uses the same one-shot infrastructure as spawn_explosion
	# embers but smaller, faster, and warmer.
	var secondary_count: int = int(ceil(float(count) * 0.6))
	if secondary_count > 0:
		_spawn_impact_embers(position, secondary_count)
	# Scorch puff (only for bigger hits, same gate as HTML).
	if count > 3:
		_spawn_scorch_puff(position)
	# Dynamic lights: white flash + warm afterglow (HTML 5345-5346).
	spawn_dynamic_light(position, Color.WHITE, 3.0, 200.0, 0.05)
	spawn_dynamic_light(position, Color8(0xff, 0xcc, 0x44), 2.0, 300.0, 0.2)

# Damage smoke/fire trickle driven by ship health (HTML 5236-5273). Callers
# feed this once per ship tick; the module gates internally on the health
# threshold and rolls the HTML's intensity*probability dice. When health is at
# or above 50% this is a silent no-op, matching HTML line 5238.
func spawn_damage_smoke(position: Vector3, health_pct: float) -> void:
	if health_pct >= DAMAGE_SMOKE_THRESHOLD:
		return
	if _light_pool.is_empty() and _active_lights.is_empty():
		return
	# intensity = 1 at 0% health, 0 at 50% health (matches HTML 5239).
	var intensity: float = 1.0 - (health_pct / DAMAGE_SMOKE_THRESHOLD)
	# Smoke puff probability scales with intensity.
	if randf() < intensity * DAMAGE_SMOKE_PROB_MAX:
		_spawn_damage_smoke_puff(position)
	# Fire only when critically low.
	if health_pct < DAMAGE_FIRE_THRESHOLD and randf() < intensity * DAMAGE_FIRE_PROB_MAX:
		_spawn_damage_fire_spark(position)

# Shield-hit shimmer (HTML 5219-5233): wireframe sphere + blue flash light.
func spawn_shield_hit(position: Vector3, radius: float = 40.0, color: Color = Color8(0x44, 0x88, 0xff)) -> void:
	# Pre-_ready guard: same reasoning as spawn_explosion/spawn_dynamic_light.
	if _light_pool.is_empty() and _active_lights.is_empty():
		return
	var mesh := SphereMesh.new()
	mesh.radius = radius
	mesh.height = radius * 2.0
	mesh.radial_segments = 12
	mesh.rings = 8
	var node := MeshInstance3D.new()
	node.mesh = mesh
	var mat := _make_additive_mat(color, 0.6, true)
	node.material_override = mat
	add_child(node)
	_place(node, position)
	_effects.append({
		"node": node,
		"material": mat,
		"type": "shield_hit",
		"lifetime": 0.3,
		"age": 0.0,
		"max_size": radius,
		"base_opacity": 0.6,
		"velocity": Vector3.ZERO,
		"rot_velocity": Vector3.ZERO,
	})
	spawn_dynamic_light(position, color, 2.5, 400.0, 0.15)

# -- Phase spawners -------------------------------------------------------

func _spawn_flash_sphere(position: Vector3, radius: float, lifetime: float, billboard: bool) -> void:
	var mesh := SphereMesh.new()
	mesh.radius = radius
	mesh.height = radius * 2.0
	mesh.radial_segments = 8
	mesh.rings = 6
	var node := MeshInstance3D.new()
	node.mesh = mesh
	var mat := _make_additive_mat(FLASH_COLOR, 1.0, false)
	if billboard:
		mat.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	node.material_override = mat
	add_child(node)
	_place(node, position)
	_push_effect(node, mat, "flash", lifetime, radius * 1.5, 1.0)

func _spawn_flash_disc(position: Vector3, size: float, lifetime: float) -> void:
	# Lens-flare disc: a billboarded plane (QuadMesh) that grows over time.
	var mesh := QuadMesh.new()
	mesh.size = Vector2(size, size)
	var node := MeshInstance3D.new()
	node.mesh = mesh
	var mat := _make_additive_mat(FLARE_COLOR, 0.95, true)
	node.material_override = mat
	add_child(node)
	_place(node, position)
	_push_effect(node, mat, "flash", lifetime, size * 2.5, 0.95)

func _spawn_fire_sphere(position: Vector3, radius: float, lifetime: float, max_size: float, color: Color) -> void:
	var mesh := SphereMesh.new()
	mesh.radius = radius
	mesh.height = radius * 2.0
	mesh.radial_segments = 8
	mesh.rings = 6
	var node := MeshInstance3D.new()
	node.mesh = mesh
	var mat := _make_additive_mat(color, color.a, false)
	node.material_override = mat
	add_child(node)
	_place(node, position)
	_push_effect(node, mat, "fire", lifetime, max_size, color.a)

func _spawn_shockwave_flat(position: Vector3, size: float, lifetime: float, max_size: float) -> void:
	# Use a flat ring approximated as a thin cylinder face: TorusMesh with
	# tiny tube + huge ring works, but Godot's QuadMesh + billboarding gives a
	# cleaner cinematic disc that "rapidly expands toward the camera". We pick
	# the QuadMesh route to mirror HTML's billboarded RingGeometry.
	var mesh := QuadMesh.new()
	mesh.size = Vector2(size, size)
	var node := MeshInstance3D.new()
	node.mesh = mesh
	var mat := _make_additive_mat(SHOCKWAVE_FLAT_COLOR, 0.95, true)
	node.material_override = mat
	add_child(node)
	_place(node, position)
	_push_effect(node, mat, "shockwave_flat", lifetime, max_size, 0.95)

func _spawn_shockwave_torus(position: Vector3, size: float, lifetime: float, max_size: float, color: Color, perpendicular: bool = false) -> void:
	var mesh := TorusMesh.new()
	mesh.inner_radius = size * 0.4
	mesh.outer_radius = size * 0.5
	mesh.ring_segments = 32
	mesh.rings = 8
	var node := MeshInstance3D.new()
	node.mesh = mesh
	var mat := _make_additive_mat(color, color.a, false)
	node.material_override = mat
	add_child(node)
	_place(node, position)
	# Random orientation per HTML: rotation.set(Math.random()*PI, ...).
	var basis := Basis()
	basis = basis.rotated(Vector3.RIGHT, randf() * PI + (1.5 if perpendicular else 0.0))
	basis = basis.rotated(Vector3.UP, randf() * PI)
	node.basis = basis
	_push_effect(node, mat, "shockwave_torus", lifetime, max_size, color.a)

func _spawn_smoke(position: Vector3, size: float, lifetime: float, max_size: float) -> void:
	# HTML uses IcosahedronGeometry; SphereMesh with low subdivision is the
	# closest Godot built-in (visually indistinguishable for an additive blob).
	var mesh := SphereMesh.new()
	mesh.radius = size * 0.6
	mesh.height = size * 1.2
	mesh.radial_segments = 6
	mesh.rings = 4
	var node := MeshInstance3D.new()
	node.mesh = mesh
	# Smoke is NOT additive; it's a dark transparent puff that occludes light
	# behind it (HTML uses default blending here, not AdditiveBlending).
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.albedo_color = SMOKE_COLOR
	node.material_override = mat
	add_child(node)
	_place(node, position)
	var rot := Vector3(randf() * 6.0, randf() * 6.0, randf() * 6.0)
	var basis := Basis()
	basis = basis.rotated(Vector3.RIGHT, rot.x)
	basis = basis.rotated(Vector3.UP, rot.y)
	basis = basis.rotated(Vector3.FORWARD, rot.z)
	node.basis = basis
	var rot_vel := Vector3((randf() - 0.5) * 2.0, (randf() - 0.5) * 2.0, (randf() - 0.5) * 2.0)
	_effects.append({
		"node": node,
		"material": mat,
		"type": "smoke",
		"lifetime": lifetime,
		"age": 0.0,
		"max_size": max_size,
		"base_opacity": 0.4,
		"velocity": Vector3.ZERO,
		"rot_velocity": rot_vel,
	})

func _spawn_embers(position: Vector3, count: int) -> void:
	# Single GPUParticles3D burst per explosion is much cheaper than N nodes
	# and matches HTML's batched-particle aesthetic. Color is the warm orange
	# range from EMBER_COLORS (we sample one at random for the whole burst;
	# HTML samples per-particle but the visual difference is minor here and
	# Godot's ParticleProcessMaterial color_ramp would be the next step if we
	# want strict parity).
	var particles := GPUParticles3D.new()
	particles.amount = count
	particles.lifetime = 0.8
	particles.one_shot = true
	particles.explosiveness = 1.0

	var quad := QuadMesh.new()
	quad.size = Vector2(3.0, 3.0)
	var color: Color = EMBER_COLORS[randi() % EMBER_COLORS.size()]
	var mat := _make_additive_mat(color, 0.95, true)
	mat.emission_enabled = true
	mat.emission = color
	mat.emission_energy_multiplier = 2.5
	quad.material = mat
	particles.draw_pass_1 = quad

	var process := ParticleProcessMaterial.new()
	process.direction = Vector3.ZERO
	process.spread = 180.0
	process.gravity = Vector3.ZERO
	process.initial_velocity_min = 200.0
	process.initial_velocity_max = 600.0
	process.scale_min = 0.6
	process.scale_max = 1.4
	process.color = color
	process.damping_min = 50.0
	process.damping_max = 50.0
	particles.process_material = process

	add_child(particles)
	_place(particles, position)
	particles.emitting = true
	# Auto-cleanup once the burst completes. GPUParticles3D.finished fires once
	# after one_shot emission completes (amount * lifetime seconds later); this
	# avoids depending on SceneTree (get_tree() is null under `-s` mode).
	particles.finished.connect(particles.queue_free)

# Smaller, faster ember burst used by spawn_impact_sparks. Cheaper than the
# explosion ember burst because impact events happen 10-20x more often.
func _spawn_impact_embers(position: Vector3, count: int) -> void:
	var particles := GPUParticles3D.new()
	particles.amount = count
	particles.lifetime = 0.35
	particles.one_shot = true
	particles.explosiveness = 1.0

	var quad := QuadMesh.new()
	quad.size = Vector2(1.5, 1.5)
	var color: Color = (EMBER_COLORS[randi() % EMBER_COLORS.size()] if randf() > 0.5 else Color8(0xff, 0x88, 0x00))
	var mat := _make_additive_mat(color, 0.95, true)
	mat.emission_enabled = true
	mat.emission = color
	mat.emission_energy_multiplier = 1.8
	quad.material = mat
	particles.draw_pass_1 = quad

	var process := ParticleProcessMaterial.new()
	process.direction = Vector3.ZERO
	process.spread = 180.0
	process.gravity = Vector3.ZERO
	process.initial_velocity_min = 100.0
	process.initial_velocity_max = 300.0
	process.scale_min = 0.5
	process.scale_max = 1.2
	process.color = color
	process.damping_min = 80.0
	process.damping_max = 80.0
	particles.process_material = process

	add_child(particles)
	_place(particles, position)
	particles.emitting = true
	particles.finished.connect(particles.queue_free)

# Dark scorch puff that lingers after an impact (HTML 5333-5342). Non-additive,
# semi-transparent, rotates gently.
func _spawn_scorch_puff(position: Vector3) -> void:
	var mesh := SphereMesh.new()
	mesh.radius = 4.0
	mesh.height = 8.0
	mesh.radial_segments = 6
	mesh.rings = 4
	var node := MeshInstance3D.new()
	node.mesh = mesh
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.albedo_color = Color(0.07, 0.07, 0.07, 0.3)
	node.material_override = mat
	add_child(node)
	_place(node, position)
	var rot_vel := Vector3((randf() - 0.5) * 3.0, (randf() - 0.5) * 3.0, (randf() - 0.5) * 3.0)
	_effects.append({
		"node": node,
		"material": mat,
		"type": "smoke",
		"lifetime": 0.6,
		"age": 0.0,
		"max_size": 12.0,
		"base_opacity": 0.3,
		"velocity": Vector3.ZERO,
		"rot_velocity": rot_vel,
	})

# Small smoke puff spawned by spawn_damage_smoke (HTML 5241-5255). Rises and
# drifts laterally, fades over <= 0.8s. We model it as a tiny smoke effect
# reusing the "smoke" type so _update_effects handles expand + fade + spin.
func _spawn_damage_smoke_puff(position: Vector3) -> void:
	var offset := Vector3(
		(randf() - 0.5) * 20.0,
		(randf() - 0.5) * 10.0,
		(randf() - 0.5) * 20.0,
	)
	var size: float = 4.0 + randf() * 4.0
	var mesh := SphereMesh.new()
	mesh.radius = size * 0.5
	mesh.height = size
	mesh.radial_segments = 6
	mesh.rings = 4
	var node := MeshInstance3D.new()
	node.mesh = mesh
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.albedo_color = Color(0.13, 0.13, 0.13, 0.4)
	node.material_override = mat
	add_child(node)
	_place(node, position + offset)
	# Rises upward (HTML 5244: 20 + random*30 on y) with lateral drift.
	var vel := Vector3(
		(randf() - 0.5) * 30.0,
		20.0 + randf() * 30.0,
		(randf() - 0.5) * 30.0,
	)
	var rot_vel := Vector3((randf() - 0.5) * 2.0, (randf() - 0.5) * 2.0, (randf() - 0.5) * 2.0)
	_effects.append({
		"node": node,
		"material": mat,
		"type": "damage_smoke",
		"lifetime": 0.4 + randf() * 0.4,
		"age": 0.0,
		"max_size": size * 2.0,
		"base_opacity": 0.4,
		"velocity": vel,
		"rot_velocity": rot_vel,
	})

# Fire spark emitted only when hull < 25%. Quick hot flicker, additive.
func _spawn_damage_fire_spark(position: Vector3) -> void:
	var offset := Vector3(
		(randf() - 0.5) * 15.0,
		(randf() - 0.5) * 8.0,
		(randf() - 0.5) * 15.0,
	)
	var size: float = 2.0 + randf() * 3.0
	var fire_colors := [
		Color8(0xff, 0x44, 0x00),
		Color8(0xff, 0x66, 0x00),
		Color8(0xff, 0x88, 0x00),
	]
	var color: Color = fire_colors[randi() % fire_colors.size()]
	var mesh := SphereMesh.new()
	mesh.radius = size * 0.5
	mesh.height = size
	mesh.radial_segments = 4
	mesh.rings = 3
	var node := MeshInstance3D.new()
	node.mesh = mesh
	var mat := _make_additive_mat(color, 0.9, false)
	node.material_override = mat
	add_child(node)
	_place(node, position + offset)
	var vel := Vector3(
		(randf() - 0.5) * 40.0,
		30.0 + randf() * 40.0,
		(randf() - 0.5) * 40.0,
	)
	_effects.append({
		"node": node,
		"material": mat,
		"type": "spark",
		"lifetime": 0.15 + randf() * 0.15,
		"age": 0.0,
		"max_size": 0.0,
		"base_opacity": 0.9,
		"velocity": vel,
		"rot_velocity": Vector3.ZERO,
	})

func _spawn_debris_chunks(position: Vector3, count: int) -> void:
	for i in range(count):
		var chunk_size := 2.0 + randf() * 4.0
		# Godot has no TetrahedronMesh; PrismMesh is the closest built-in.
		# (BoxMesh would also work, but the spinning prism reads like a chunk
		# of hull more clearly.)
		var mesh := PrismMesh.new()
		mesh.size = Vector3(chunk_size, chunk_size, chunk_size)
		var node := MeshInstance3D.new()
		node.mesh = mesh
		var mat := StandardMaterial3D.new()
		mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		mat.albedo_color = Color(0.27, 0.2, 0.13, 0.8)
		node.material_override = mat
		add_child(node)
		_place(node, position)
		var vel := Vector3(
			(randf() - 0.5) * 350.0,
			(randf() - 0.5) * 350.0,
			(randf() - 0.5) * 350.0,
		)
		var rot_vel := Vector3(
			(randf() - 0.5) * 10.0,
			(randf() - 0.5) * 10.0,
			(randf() - 0.5) * 10.0,
		)
		_effects.append({
			"node": node,
			"material": mat,
			"type": "debris",
			"lifetime": 0.8 + randf() * 0.6,
			"age": 0.0,
			"max_size": 0.0,
			"base_opacity": 0.8,
			"velocity": vel,
			"rot_velocity": rot_vel,
		})

# -- Update loop ----------------------------------------------------------

func _update_lights(delta: float) -> void:
	# Walk in reverse so we can pop expired entries safely.
	for i in range(_active_lights.size() - 1, -1, -1):
		var entry: Dictionary = _active_lights[i]
		entry["age"] += delta
		var age: float = entry["age"]
		var dur: float = entry["duration"]
		if age >= dur:
			var light: OmniLight3D = entry["light"]
			light.visible = false
			light.light_energy = 0.0
			entry["active"] = false
			_active_lights.remove_at(i)
			_light_pool.append(entry)
		else:
			# Quadratic falloff for "punch" (HTML 3886).
			var t: float = age / dur
			var light2: OmniLight3D = entry["light"]
			light2.light_energy = float(entry["intensity"]) * (1.0 - t * t)

func _update_effects(delta: float) -> void:
	# Cap effects: cull the oldest (front of array) when over budget. HTML
	# 5114-5120 disposes geometry/material; queue_free does both for us.
	while _effects.size() > MAX_EFFECTS:
		var stale: Dictionary = _effects.pop_front()
		var stale_node: Node3D = stale["node"]
		if is_instance_valid(stale_node):
			stale_node.queue_free()

	for i in range(_effects.size() - 1, -1, -1):
		var e: Dictionary = _effects[i]
		e["age"] += delta
		var age: float = e["age"]
		var lifetime: float = e["lifetime"]
		if age >= lifetime:
			var n: Node3D = e["node"]
			if is_instance_valid(n):
				n.queue_free()
			_effects.remove_at(i)
			continue
		var t: float = age / lifetime
		var node: MeshInstance3D = e["node"]
		var mat: StandardMaterial3D = e["material"]
		if not is_instance_valid(node):
			_effects.remove_at(i)
			continue
		match e["type"]:
			"flash":
				# Billboard plane expands faster than the sphere; HTML uses
				# `1 + t*2.5` for billboard and `1 + t*0.5` for the sphere.
				var s: float = 1.0 + t * (2.5 if mat.billboard_mode == BaseMaterial3D.BILLBOARD_ENABLED else 0.5)
				node.scale = Vector3(s, s, s)
				_set_alpha(mat, e["base_opacity"] * (1.0 - t * t))
			"fire":
				var expand: float = 1.0 + t * 2.2
				node.scale = Vector3(expand, expand, expand)
				# Color shift: orange -> red -> dark.
				var g: float = maxf(0.0, 0.4 * (1.0 - t * 1.5))
				mat.albedo_color = Color(1.0, g, 0.0, e["base_opacity"] * (1.0 - t * t))
			"shockwave_flat":
				var ring_scale: float = 1.0 + t * float(e["max_size"])
				node.scale = Vector3(ring_scale, ring_scale, 1.0)
				_set_alpha(mat, 0.95 * (1.0 - t * t))
			"shockwave_torus":
				var rs: float = 1.0 + t * float(e["max_size"])
				node.scale = Vector3(rs, rs, rs)
				_set_alpha(mat, 0.8 * (1.0 - t))
			"smoke":
				var smoke_expand: float = 1.0 + t * (float(e["max_size"]) - 1.0)
				node.scale = Vector3(smoke_expand, smoke_expand, smoke_expand)
				_set_alpha(mat, e["base_opacity"] * (1.0 - t) * (1.0 - t))
				var rv: Vector3 = e["rot_velocity"]
				node.rotate(Vector3.RIGHT, rv.x * delta)
				node.rotate(Vector3.UP, rv.y * delta)
				node.rotate(Vector3.FORWARD, rv.z * delta)
			"debris":
				var v: Vector3 = e["velocity"]
				# Use `position` (local) to avoid is_inside_tree() reads inside
				# get_global_transform; ExplosionFX is stationary relative to
				# its parent, so per-frame offsets are equivalent.
				node.position += v * delta
				e["velocity"] = v * 0.97  # drag
				var rv2: Vector3 = e["rot_velocity"]
				node.rotate(Vector3.RIGHT, rv2.x * delta)
				node.rotate(Vector3.UP, rv2.y * delta)
				node.rotate(Vector3.FORWARD, rv2.z * delta)
				_set_alpha(mat, e["base_opacity"] * (1.0 - t))
				var shrink: float = 1.0 - t * 0.3
				node.scale = Vector3(shrink, shrink, shrink)
			"shield_hit":
				var shimmer: float = 1.0 + t * 0.3
				node.scale = Vector3(shimmer, shimmer, shimmer)
				_set_alpha(mat, e["base_opacity"] * (1.0 - t))
			"spark":
				# Same kinematics as debris but without the shrink; sparks
				# stay bright until they fade. Inherits _place()'s local-
				# space movement trick for `-s` headless safety.
				var sv: Vector3 = e["velocity"]
				node.position += sv * delta
				e["velocity"] = sv * 0.92
				_set_alpha(mat, e["base_opacity"] * (1.0 - t * t))
			"damage_smoke":
				var dv: Vector3 = e["velocity"]
				node.position += dv * delta
				# Smoke slows vertically less than horizontally; keep the rise
				# readable. HTML applies uniform 0.95 damping; we match.
				e["velocity"] = dv * 0.95
				var smoke_expand: float = 1.0 + t * 1.2
				node.scale = Vector3(smoke_expand, smoke_expand, smoke_expand)
				_set_alpha(mat, e["base_opacity"] * (1.0 - t) * (1.0 - t))
				var rv3: Vector3 = e["rot_velocity"]
				node.rotate(Vector3.RIGHT, rv3.x * delta)
				node.rotate(Vector3.UP, rv3.y * delta)
				node.rotate(Vector3.FORWARD, rv3.z * delta)
			_:
				pass

# -- Helpers --------------------------------------------------------------

func _push_effect(node: MeshInstance3D, mat: StandardMaterial3D, type_name: String, lifetime: float, max_size: float, base_opacity: float) -> void:
	_effects.append({
		"node": node,
		"material": mat,
		"type": type_name,
		"lifetime": lifetime,
		"age": 0.0,
		"max_size": max_size,
		"base_opacity": base_opacity,
		"velocity": Vector3.ZERO,
		"rot_velocity": Vector3.ZERO,
	})

func _make_additive_mat(color: Color, opacity: float, billboard: bool) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	mat.depth_draw_mode = BaseMaterial3D.DEPTH_DRAW_DISABLED
	mat.albedo_color = Color(color.r, color.g, color.b, opacity)
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	if billboard:
		mat.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	return mat

func _set_alpha(mat: StandardMaterial3D, alpha: float) -> void:
	var c := mat.albedo_color
	mat.albedo_color = Color(c.r, c.g, c.b, clampf(alpha, 0.0, 1.0))

# _place sets a child node's world position. Uses global_position when the
# scene tree is live; falls back to the local-space `position` property under
# `-s` test mode (where is_inside_tree() reports false even after add_child,
# so touching global_position triggers "Condition !is_inside_tree() is true").
# In the test harness ExplosionFX is attached directly to root with no offset,
# so local == global and the fallback is visually/structurally correct.
func _place(node: Node3D, world_pos: Vector3) -> void:
	if is_inside_tree():
		node.global_position = world_pos
	else:
		node.position = world_pos

# -- Test hooks -----------------------------------------------------------

# Used by test_explosion_fx.gd to verify pool/queue counts without poking
# private members directly.
func _get_active_light_count() -> int:
	return _active_lights.size()

func _get_pool_light_count() -> int:
	return _light_pool.size()

func _get_effect_count() -> int:
	return _effects.size()

# Count entries in the active effect queue whose "type" field matches. Used
# by test_explosion_fx.gd to verify damage-smoke vs fire-spark counts without
# reaching into the private array.
func _count_effects_of_type(type_name: String) -> int:
	var n: int = 0
	for e in _effects:
		if String(e.get("type", "")) == type_name:
			n += 1
	return n
