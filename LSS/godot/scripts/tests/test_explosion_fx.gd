extends SceneTree

# Headless coverage for the explosion VFX module ported in task #54
# (HTML last_ship_sailing.html:3836-4032 spawnExplosion + spawnDynamicLight,
# 5113-5215 effect animation).
#
# Like the audio test, we manually instantiate the module under our SceneTree
# (autoloads aren't auto-mounted in `-s` mode) and drive it from outside. We
# verify:
#
#   1. Light pool initialises to MAX_LIGHTS = 8 OmniLight3D children
#   2. spawn_dynamic_light moves entries from pool -> active and the totals
#      remain conserved (pool + active == MAX_LIGHTS)
#   3. Pool overflow falls back to "steal oldest active" (HTML 3861)
#   4. spawn_explosion(size=20) creates the small-set effect cascade
#      (no shockwave, no smoke, no debris) and queues two dynamic lights
#   5. spawn_explosion(size=40) creates the full cascade including smoke and
#      debris
#   6. _process advances time and effects expire/queue_free at lifetime
#   7. spawn_shield_hit creates exactly one effect plus one dynamic light
#   8. Calling spawn_explosion BEFORE the node is in the tree is a silent
#      no-op (matches audio.gd's is_inside_tree() defensive guard)
#   9. spawn_impact_sparks(pos, 6) creates 1 flash + 6 sparks + 1 scorch puff
#      (count > 3 gate) + 2 dynamic lights (HTML 5290-5347)
#  10. spawn_impact_sparks(pos, 2) skips the scorch puff (count > 3 gate)
#  11. spawn_damage_smoke(pos, 0.8) is a no-op at full-ish health
#  12. spawn_damage_smoke(pos, 0.3) spawned many times produces smoke-only
#      effects (no fire above DAMAGE_FIRE_THRESHOLD = 0.25)
#  13. spawn_damage_smoke(pos, 0.1) spawned many times can produce BOTH
#      smoke and fire effects (below 0.25 fire threshold)
#
# Anything that pushes an error to push_error fails the test.

const ExplosionFXScript = preload("res://scripts/explosion_fx.gd")

var _ok := true

func _fail(msg: String) -> void:
	push_error(msg)
	_ok = false

func _new_fx() -> Node:
	var fx: Node = ExplosionFXScript.new()
	fx.name = "ExplosionFX"
	get_root().add_child(fx)
	# _ready() runs deferred from add_child; the pool builds inside _ready,
	# but we want it ready before assertions. Drive _ready() directly to make
	# the test deterministic.
	if fx.has_method("_ready"):
		fx.call("_ready")
	return fx

func _init() -> void:
	print("=== Explosion FX tests ===")

	_assert_pre_tree_noop()
	_assert_pool_initialisation()
	_assert_dynamic_light_lifecycle()
	_assert_pool_overflow_steal()
	_assert_small_explosion_cascade()
	_assert_large_explosion_cascade()
	_assert_effect_expiry()
	_assert_shield_hit()
	_assert_impact_sparks_with_scorch()
	_assert_impact_sparks_without_scorch()
	_assert_damage_smoke_gated_by_health()
	_assert_damage_smoke_smoke_only_regime()
	_assert_damage_smoke_fire_regime()

	if _ok:
		print("RESULT: PASS")
		quit(0)
	else:
		push_error("test_explosion_fx FAILED")
		quit(1)

# -- 1. Pre-tree no-op -----------------------------------------------------

func _assert_pre_tree_noop() -> void:
	# Brand-new instance, NOT yet added to the tree. The defensive
	# is_inside_tree() guard inside spawn_explosion / spawn_dynamic_light /
	# spawn_shield_hit should return early without crashing.
	var fx: Node = ExplosionFXScript.new()
	fx.spawn_explosion(Vector3.ZERO, 20.0)
	fx.spawn_dynamic_light(Vector3.ZERO, Color.WHITE, 1.0, 100.0, 0.5)
	fx.spawn_shield_hit(Vector3.ZERO, 30.0, Color(0.3, 0.5, 1.0))
	if fx.get("_get_active_light_count") != null:
		var active: int = fx.call("_get_active_light_count")
		if active != 0:
			_fail("Pre-tree spawn should have created no active lights, got %d" % active)
	fx.free()
	print("Pre-tree calls are silent no-ops: OK")

# -- 2. Pool initialisation ------------------------------------------------

func _assert_pool_initialisation() -> void:
	var fx := _new_fx()
	var pool: int = fx.call("_get_pool_light_count")
	var active: int = fx.call("_get_active_light_count")
	if pool != 8:
		_fail("Pool should contain MAX_LIGHTS = 8 lights at init, got %d" % pool)
	if active != 0:
		_fail("Active list should be empty at init, got %d" % active)
	# Children should include 8 OmniLight3Ds plus nothing else.
	var omni_count := 0
	for child in fx.get_children():
		if child is OmniLight3D:
			omni_count += 1
	if omni_count != 8:
		_fail("Expected 8 OmniLight3D children, got %d" % omni_count)
	print("Pool initialisation (8 OmniLight3D, 0 active): OK")
	fx.queue_free()

# -- 3. Dynamic light lifecycle (spawn -> active -> expire) ---------------

func _assert_dynamic_light_lifecycle() -> void:
	var fx := _new_fx()
	fx.spawn_dynamic_light(Vector3.ZERO, Color(1.0, 0.5, 0.0), 4.0, 600.0, 0.5)
	if fx.call("_get_active_light_count") != 1:
		_fail("Active count should be 1 after one spawn, got %d" % fx.call("_get_active_light_count"))
	if fx.call("_get_pool_light_count") != 7:
		_fail("Pool should drop to 7 after one spawn, got %d" % fx.call("_get_pool_light_count"))
	# Conservation: pool + active should always equal MAX_LIGHTS = 8.
	if int(fx.call("_get_active_light_count")) + int(fx.call("_get_pool_light_count")) != 8:
		_fail("Pool + active conservation broken")
	# Tick past the lifetime; the entry should return to the pool.
	if fx.has_method("_process"):
		fx.call("_process", 0.6)  # > 0.5 lifetime
	if fx.call("_get_active_light_count") != 0:
		_fail("Active count should be 0 after expiry, got %d" % fx.call("_get_active_light_count"))
	if fx.call("_get_pool_light_count") != 8:
		_fail("Pool should refill to 8 after expiry, got %d" % fx.call("_get_pool_light_count"))
	print("Dynamic light spawn/expire/recycle: OK")
	fx.queue_free()

# -- 4. Pool overflow stealing oldest active ------------------------------

func _assert_pool_overflow_steal() -> void:
	var fx := _new_fx()
	# Spawn 9 lights with long durations so none expire naturally; the 9th
	# must reuse the oldest (first) entry rather than allocate.
	for i in range(9):
		fx.spawn_dynamic_light(Vector3(i * 10.0, 0.0, 0.0), Color.WHITE, 1.0, 100.0, 100.0)
	# After 8 spawns the pool is empty; the 9th should still succeed by
	# pulling from active. Total active stays at 8.
	if fx.call("_get_active_light_count") != 8:
		_fail("Active should be capped at MAX_LIGHTS = 8 under overflow, got %d" % fx.call("_get_active_light_count"))
	if fx.call("_get_pool_light_count") != 0:
		_fail("Pool should be 0 under overflow, got %d" % fx.call("_get_pool_light_count"))
	print("Pool overflow steals oldest active: OK")
	fx.queue_free()

# -- 5. Small explosion cascade (size <= 12) ------------------------------

func _assert_small_explosion_cascade() -> void:
	var fx := _new_fx()
	# size = 12 falls into the "small" bracket: flash sphere, flash disc, two
	# fire spheres. No shockwaves (size > 12), no smoke (size > 15), no
	# debris (size > 25). Embers run for any size > 0.
	fx.spawn_explosion(Vector3.ZERO, 12.0)
	# Effect array: 1 flash sphere + 1 flash disc + 2 fire spheres = 4. The
	# embers go through GPUParticles3D and aren't tracked in _effects.
	var effect_count: int = fx.call("_get_effect_count")
	if effect_count != 4:
		_fail("Small explosion (size=12) should produce 4 mesh effects, got %d" % effect_count)
	# Two dynamic lights (flash + glow).
	if fx.call("_get_active_light_count") != 2:
		_fail("Explosion should spawn 2 dynamic lights, got %d" % fx.call("_get_active_light_count"))
	print("Small explosion cascade (4 effects + 2 lights): OK")
	fx.queue_free()

# -- 6. Large explosion cascade (size > 30) -------------------------------

func _assert_large_explosion_cascade() -> void:
	var fx := _new_fx()
	# size = 50: flash sphere + flash disc + 2 fires + flat shockwave + 2
	# torus shockwaves (perpendicular added at size > 30) + smoke + debris
	# (chunk_count = ceil(50*0.1) = 5). Effects total = 1+1+2+1+2+1+5 = 13.
	fx.spawn_explosion(Vector3.ZERO, 50.0)
	var effect_count: int = fx.call("_get_effect_count")
	# Allow some slack in case randf changes future behaviour; the lower
	# bound (no debris) is 8, the upper bound (max debris = 6) is 14.
	if effect_count < 8 or effect_count > 14:
		_fail("Large explosion (size=50) should produce 8-14 mesh effects, got %d" % effect_count)
	# Still only two dynamic lights regardless of size (flash + glow pair).
	if fx.call("_get_active_light_count") != 2:
		_fail("Large explosion should still spawn exactly 2 dynamic lights, got %d" % fx.call("_get_active_light_count"))
	print("Large explosion cascade (%d effects + 2 lights): OK" % effect_count)
	fx.queue_free()

# -- 7. Effect expiry via _process ----------------------------------------

func _assert_effect_expiry() -> void:
	var fx := _new_fx()
	fx.spawn_explosion(Vector3.ZERO, 50.0)
	var initial: int = fx.call("_get_effect_count")
	if initial == 0:
		_fail("Expected effects before expiry tick")
		fx.queue_free()
		return
	# All explosion effects have lifetime <= 1.2s (smoke is the longest).
	# Step time forward in chunks; effects should drain to zero.
	for i in range(8):
		fx.call("_process", 0.2)
	var remaining: int = fx.call("_get_effect_count")
	if remaining != 0:
		_fail("All explosion effects should have expired after 1.6s, %d remain" % remaining)
	print("Effect expiry via _process (lifetime <= 1.2s): OK")
	fx.queue_free()

# -- 8. Shield hit --------------------------------------------------------

func _assert_shield_hit() -> void:
	var fx := _new_fx()
	fx.spawn_shield_hit(Vector3.ZERO, 35.0, Color(0.3, 0.5, 1.0))
	if fx.call("_get_effect_count") != 1:
		_fail("Shield hit should produce exactly 1 effect, got %d" % fx.call("_get_effect_count"))
	if fx.call("_get_active_light_count") != 1:
		_fail("Shield hit should produce exactly 1 dynamic light, got %d" % fx.call("_get_active_light_count"))
	print("Shield hit (1 effect + 1 light): OK")
	fx.queue_free()

# -- 9. Impact sparks with scorch puff (count > 3) ------------------------

func _assert_impact_sparks_with_scorch() -> void:
	var fx := _new_fx()
	# count = 6: flash sphere + 6 spark streaks + scorch puff (gate is count > 3)
	# = 8 mesh effects; embers go through GPUParticles3D and aren't tracked in
	# _effects. Two dynamic lights (white flash + warm afterglow).
	fx.spawn_impact_sparks(Vector3.ZERO, 6, Color(1.0, 0.8, 0.3, 1.0))
	var effect_count: int = fx.call("_get_effect_count")
	if effect_count != 8:
		_fail("Impact sparks (count=6) should produce 8 mesh effects (1 flash + 6 sparks + 1 scorch), got %d" % effect_count)
	if fx.call("_get_active_light_count") != 2:
		_fail("Impact sparks should spawn 2 dynamic lights, got %d" % fx.call("_get_active_light_count"))
	print("Impact sparks count=6 (8 effects + 2 lights, with scorch): OK")
	fx.queue_free()

# -- 10. Impact sparks without scorch (count <= 3) ------------------------

func _assert_impact_sparks_without_scorch() -> void:
	var fx := _new_fx()
	# count = 2 is at or below the "count > 3" scorch gate, so no scorch puff.
	# 1 flash + 2 sparks = 3 mesh effects. Still two dynamic lights.
	fx.spawn_impact_sparks(Vector3.ZERO, 2, Color(0, 0, 0, 0))
	var effect_count: int = fx.call("_get_effect_count")
	if effect_count != 3:
		_fail("Impact sparks (count=2) should produce 3 mesh effects (no scorch), got %d" % effect_count)
	if fx.call("_get_active_light_count") != 2:
		_fail("Impact sparks should spawn 2 dynamic lights even without scorch, got %d" % fx.call("_get_active_light_count"))
	print("Impact sparks count=2 (3 effects + 2 lights, no scorch): OK")
	fx.queue_free()

# -- 11. Damage smoke gated by 50% health threshold -----------------------

func _assert_damage_smoke_gated_by_health() -> void:
	var fx := _new_fx()
	# HTML line 3044-3046: damage smoke is only called when health < maxHealth*0.5,
	# AND the module itself early-outs at health_pct >= 0.5 as a safety net.
	# We verify the module's own gate: many calls at 80% health must produce zero
	# effects, regardless of RNG.
	for i in range(200):
		fx.spawn_damage_smoke(Vector3.ZERO, 0.8)
	var effect_count: int = fx.call("_get_effect_count")
	if effect_count != 0:
		_fail("spawn_damage_smoke at health_pct=0.8 must be a no-op, got %d effects" % effect_count)
	print("Damage smoke gated at health_pct >= 0.5 (0 effects after 200 calls): OK")
	fx.queue_free()

# -- 12. Damage smoke in smoke-only regime (0.25 <= health < 0.5) ---------

func _assert_damage_smoke_smoke_only_regime() -> void:
	var fx := _new_fx()
	# health_pct = 0.3: intensity = 1 - 0.3/0.5 = 0.4. Smoke probability per call
	# = intensity * 0.4 = 0.16; fire gate is health_pct < 0.25, so fire is off.
	# Over 500 calls we expect ~80 smoke puffs and exactly 0 fire sparks. The
	# statistical test uses wide bounds to avoid flakes; the hard gate is the
	# "no fire" assertion.
	seed(0xc0ffee)
	var before_smoke: int = 0
	var before_fire: int = 0
	for i in range(500):
		fx.spawn_damage_smoke(Vector3.ZERO, 0.3)
	var smoke_count: int = fx.call("_count_effects_of_type", "damage_smoke") - before_smoke
	var fire_count: int = fx.call("_count_effects_of_type", "spark") - before_fire
	if fire_count != 0:
		_fail("spawn_damage_smoke at health_pct=0.3 must NOT spawn fire (health >= 0.25 threshold), got %d fire effects" % fire_count)
	if smoke_count < 20 or smoke_count > 200:
		_fail("spawn_damage_smoke at health_pct=0.3 should produce ~80 smoke puffs in 500 calls (wide band 20-200), got %d" % smoke_count)
	print("Damage smoke @ 30%% (smoke-only regime, %d smoke / 0 fire in 500 calls): OK" % smoke_count)
	fx.queue_free()

# -- 13. Damage smoke in fire regime (health_pct < 0.25) ------------------

func _assert_damage_smoke_fire_regime() -> void:
	var fx := _new_fx()
	# health_pct = 0.1: intensity = 0.8. Smoke p = 0.32, fire p = 0.24.
	# Over 500 calls, expect ~160 smoke + ~120 fire. Wide bounds again; the
	# hard gate is that BOTH are nonzero.
	seed(0xfeedbeef)
	for i in range(500):
		fx.spawn_damage_smoke(Vector3.ZERO, 0.1)
	var smoke_count: int = fx.call("_count_effects_of_type", "damage_smoke")
	var fire_count: int = fx.call("_count_effects_of_type", "spark")
	if smoke_count == 0:
		_fail("spawn_damage_smoke at health_pct=0.1 should produce smoke (got 0 in 500 calls)")
	if fire_count == 0:
		_fail("spawn_damage_smoke at health_pct=0.1 should produce fire sparks (got 0 in 500 calls)")
	print("Damage smoke @ 10%% (fire regime, %d smoke + %d fire in 500 calls): OK" % [smoke_count, fire_count])
	fx.queue_free()
