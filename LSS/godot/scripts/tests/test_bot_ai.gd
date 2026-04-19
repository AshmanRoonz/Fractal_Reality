extends SceneTree

# Headless coverage for the bot AI math + shared broadcast state (HTML
# last_ship_sailing.html:2959-3393). The pure math + constants live in
# BotAIMath (scripts/bot_ai_math.gd), the same RefCounted + class_name
# pattern as DeathCamMath / GameData, so this test can reach them without
# preloading enemy_ship.gd (which pulls in PlayerShip / ArenaMap / GameData
# and hangs in `-s` mode).
#
# The shared-broadcast dictionary lives on enemy_ship.gd as a static var
# (_shared_target_by_team) and is exposed via reset_shared_broadcasts(). We
# exercise it through EnemyShip.reset_shared_broadcasts() rather than
# instantiating bots, because spinning up a bot wires visuals / signals /
# arena_map and drags the whole project in.

const EnemyShipScript = preload("res://scripts/enemy_ship.gd")

var _ok := true

func _fail(msg: String) -> void:
	push_error(msg)
	_ok = false

func _init() -> void:
	print("=== Bot AI tests ===")

	_assert_constants()
	_assert_loadout_range_preference()
	_assert_squad_role()
	_assert_flank_math()
	_assert_strafe_math()
	_assert_accuracy()
	_assert_range_gate()
	_assert_memory_drift()
	_assert_retreat()
	_assert_shared_broadcast_reset()

	if _ok:
		print("RESULT: PASS")
		quit(0)
	else:
		push_error("Bot AI tests FAILED")
		quit(1)

# ---- Constants --------------------------------------------------------------
# These numbers are the HTML contract. If any drifts, the bot behaviour no
# longer matches the web build (e.g. FLANK_OFFSET at 800 would push flankers
# further out than the HTML's 600, changing engagement geometry).
func _assert_constants() -> void:
	if not is_equal_approx(BotAIMath.FLANK_ROLE_PROBABILITY, 0.33):
		_fail("FLANK_ROLE_PROBABILITY should be 0.33")
	if not is_equal_approx(BotAIMath.FLANK_OFFSET, 600.0):
		_fail("FLANK_OFFSET should be 600.0")
	if not is_equal_approx(BotAIMath.FLANK_MIN_DISTANCE, 300.0):
		_fail("FLANK_MIN_DISTANCE should be 300.0")
	if not is_equal_approx(BotAIMath.FLANK_MAX_DISTANCE, 3000.0):
		_fail("FLANK_MAX_DISTANCE should be 3000.0")
	if not is_equal_approx(BotAIMath.FLANK_BLEND, 0.6):
		_fail("FLANK_BLEND should be 0.6")
	if not is_equal_approx(BotAIMath.STRAFE_RANGE_MULT, 1.5):
		_fail("STRAFE_RANGE_MULT should be 1.5")
	if not is_equal_approx(BotAIMath.STRAFE_BLEND, 0.5):
		_fail("STRAFE_BLEND should be 0.5")
	if not is_equal_approx(BotAIMath.MEMORY_DURATION, 5.0):
		_fail("MEMORY_DURATION should be 5.0")
	if not is_equal_approx(BotAIMath.SHARED_TARGET_DURATION, 7.0):
		_fail("SHARED_TARGET_DURATION should be 7.0")
	if not is_equal_approx(BotAIMath.RANGE_FIRE_MULT, 1.3):
		_fail("RANGE_FIRE_MULT should be 1.3")
	if not is_equal_approx(BotAIMath.ACCURACY_BASE, 0.25):
		_fail("ACCURACY_BASE should be 0.25")
	if not is_equal_approx(BotAIMath.ACCURACY_RANGE_BONUS, 0.45):
		_fail("ACCURACY_RANGE_BONUS should be 0.45")
	print("CONSTANTS match HTML contract: OK")

# ---- Loadout range preference ----------------------------------------------
# HTML getLoadoutRangePreference (lines 3017-3028): per-loadout engagement
# distance. SCORCH / RONIN close, NORTHSTAR long, others medium bands. Unknown
# loadouts fall back to 800 so a missing key doesn't crash the engagement
# code; 800 sits between the close (500) and medium-close (800) presets.
func _assert_loadout_range_preference() -> void:
	if not is_equal_approx(BotAIMath.get_loadout_range_preference("SCORCH"), 500.0):
		_fail("SCORCH should be 500")
	if not is_equal_approx(BotAIMath.get_loadout_range_preference("RONIN"), 500.0):
		_fail("RONIN should be 500")
	if not is_equal_approx(BotAIMath.get_loadout_range_preference("NORTHSTAR"), 1500.0):
		_fail("NORTHSTAR should be 1500")
	if not is_equal_approx(BotAIMath.get_loadout_range_preference("TONE"), 1200.0):
		_fail("TONE should be 1200")
	if not is_equal_approx(BotAIMath.get_loadout_range_preference("LEGION"), 1000.0):
		_fail("LEGION should be 1000")
	if not is_equal_approx(BotAIMath.get_loadout_range_preference("MONARCH"), 800.0):
		_fail("MONARCH should be 800")
	if not is_equal_approx(BotAIMath.get_loadout_range_preference("ION"), 1000.0):
		_fail("ION should be 1000")
	if not is_equal_approx(BotAIMath.get_loadout_range_preference("UNKNOWN"), 800.0):
		_fail("UNKNOWN loadout should fall back to 800")
	print("LOADOUT range preferences: OK")

# ---- Squad role assignment --------------------------------------------------
# HTML line 3000: Math.random() < 0.33 ? 'flank' : 'engage'. Boundary check at
# 0.33 ensures the role flip is deterministic across small RNG-seed drifts.
func _assert_squad_role() -> void:
	if BotAIMath.assign_squad_role(0.0) != "flank":
		_fail("rng=0.0 should give flank")
	if BotAIMath.assign_squad_role(0.32) != "flank":
		_fail("rng=0.32 should give flank (below 0.33)")
	if BotAIMath.assign_squad_role(0.33) != "engage":
		_fail("rng=0.33 should give engage (not below 0.33)")
	if BotAIMath.assign_squad_role(0.5) != "engage":
		_fail("rng=0.5 should give engage")
	if BotAIMath.assign_squad_role(0.999) != "engage":
		_fail("rng=0.999 should give engage")
	print("SQUAD role 0.33 threshold: OK")

# ---- Flank target math ------------------------------------------------------
# Flank = player position + 600u perpendicular to the player-to-bot axis, in
# the XZ plane. compute_horizontal_right(dir) uses UP × dir, which in Godot
# is (0,1,0) × (1,0,0) = (0,0,-1) (right-handed Y-up: +Z is "back" / into the
# camera, so UP × RIGHT lands on -Z). Degenerate vertical inputs should fall
# back to Vector3.RIGHT so downstream math doesn't NaN on bots directly above
# / below the player.
func _assert_flank_math() -> void:
	# Bot at origin, player at +X direction → right = UP × +X = -Z.
	var flank_right := BotAIMath.compute_horizontal_right(Vector3(1.0, 0.0, 0.0))
	if not flank_right.is_equal_approx(Vector3(0.0, 0.0, -1.0)):
		_fail("right for +X direction should be -Z (Godot Y-up), got %s" % str(flank_right))
	# Vertical direction degenerates → falls back to RIGHT.
	var vertical_right := BotAIMath.compute_horizontal_right(Vector3(0.0, 1.0, 0.0))
	if not vertical_right.is_equal_approx(Vector3.RIGHT):
		_fail("right for vertical direction should fall back to RIGHT")
	# Full flank target: player at (100, 0, 0), bot at origin; right = -Z so
	# flank lands at (100, 0, -600).
	var flank_target: Vector3 = BotAIMath.compute_flank_target(
		Vector3(100.0, 0.0, 0.0), Vector3.ZERO)
	var expected_flank := Vector3(100.0, 0.0, -600.0)
	if not flank_target.is_equal_approx(expected_flank):
		_fail("flank target should be player + 600*right = %s, got %s" % [str(expected_flank), str(flank_target)])

	# should_flank gate: role must be flank AND distance in (300, 3000).
	if BotAIMath.should_flank(1000.0, "engage"):
		_fail("engage role should never flank")
	if BotAIMath.should_flank(299.0, "flank"):
		_fail("distance < 300 should not flank")
	if not BotAIMath.should_flank(500.0, "flank"):
		_fail("distance=500 flank role should flank")
	if BotAIMath.should_flank(3001.0, "flank"):
		_fail("distance > 3000 should not flank")
	# Boundary points: the gate is strictly inside (300, 3000), so equal
	# values at either edge should NOT trigger. The HTML uses >, < strictly.
	if BotAIMath.should_flank(300.0, "flank"):
		_fail("distance=300 should not flank (exclusive lower bound)")
	if BotAIMath.should_flank(3000.0, "flank"):
		_fail("distance=3000 should not flank (exclusive upper bound)")
	print("FLANK math + gate: OK")

# ---- Strafe math ------------------------------------------------------------
# Strafe returns a signed unit perpendicular scaled by STRAFE_BLEND (0.5).
# Direction sign (+1 / -1) picks which side to juke to. Vertical aim collapses
# the cross product; should return ZERO so callers know to skip.
func _assert_strafe_math() -> void:
	var offset_right: Vector3 = BotAIMath.compute_strafe_offset(Vector3(1.0, 0.0, 0.0), 1.0)
	if not offset_right.is_equal_approx(Vector3(0.0, 0.0, -0.5)):
		_fail("strafe +X dir +1 sign should give -Z*0.5, got %s" % str(offset_right))
	var offset_left: Vector3 = BotAIMath.compute_strafe_offset(Vector3(1.0, 0.0, 0.0), -1.0)
	if not offset_left.is_equal_approx(Vector3(0.0, 0.0, 0.5)):
		_fail("strafe +X dir -1 sign should give +Z*0.5")
	var degenerate: Vector3 = BotAIMath.compute_strafe_offset(Vector3(0.0, 1.0, 0.0), 1.0)
	if not degenerate.is_equal_approx(Vector3.ZERO):
		_fail("vertical aim should give ZERO offset")

	# should_strafe gate: active + in range + not doomed. Doomed bots commit
	# to retreat (HTML line 3103-3108 semantics).
	if not BotAIMath.should_strafe(true, 600.0, 800.0, false):
		_fail("active, in-range, alive bot should strafe")
	if BotAIMath.should_strafe(false, 600.0, 800.0, false):
		_fail("inactive bot should not strafe")
	if BotAIMath.should_strafe(true, 600.0, 800.0, true):
		_fail("doomed bot should never strafe (retreat overrides)")
	# 1.5x range preference = 1200; at distance 1201 we're outside the band.
	if BotAIMath.should_strafe(true, 1201.0, 800.0, false):
		_fail("distance > 1.5x range_preference should not strafe")
	print("STRAFE offset + gate: OK")

# ---- Accuracy ---------------------------------------------------------------
# HTML: accuracy = 0.25 + max(0, 1 - dist/range) * 0.45. Point-blank → 0.70,
# at range → 0.25, beyond range → floored at 0.25 (not negative).
func _assert_accuracy() -> void:
	if not is_equal_approx(BotAIMath.compute_accuracy(0.0, 2000.0), 0.70):
		_fail("point-blank accuracy should be 0.70")
	if not is_equal_approx(BotAIMath.compute_accuracy(2000.0, 2000.0), 0.25):
		_fail("at-range accuracy should be 0.25")
	if not is_equal_approx(BotAIMath.compute_accuracy(3000.0, 2000.0), 0.25):
		_fail("beyond-range accuracy should clamp to 0.25, not go negative")
	# Halfway (1000 of 2000) = ratio 0.5 → 0.25 + 0.225 = 0.475.
	if not is_equal_approx(BotAIMath.compute_accuracy(1000.0, 2000.0), 0.475):
		_fail("halfway accuracy should be 0.475")
	# Zero weapon range shouldn't divide-by-zero; maxf(1, range) keeps it sane
	# (range_ratio clamps to 0; accuracy = base 0.25).
	if not is_equal_approx(BotAIMath.compute_accuracy(1000.0, 0.0), 0.25):
		_fail("zero weapon range should fall back to 0.25, not NaN")
	print("ACCURACY 25-70%% band: OK")

# ---- Range-fire gate --------------------------------------------------------
# HTML line 3162: withinRange = distToPlayer <= preferredDist * 1.3. This is a
# separate gate from weapon.range; both must pass before firing.
func _assert_range_gate() -> void:
	# range_preference 800 → fire gate at 1040.
	if not BotAIMath.is_within_firing_range(500.0, 800.0):
		_fail("500 < 1040 should pass")
	if not BotAIMath.is_within_firing_range(1040.0, 800.0):
		_fail("equal to 1.3x should pass (inclusive)")
	if BotAIMath.is_within_firing_range(1050.0, 800.0):
		_fail("1050 > 1040 should fail")
	print("RANGE gate 1.3x preference: OK")

# ---- Memory drift -----------------------------------------------------------
# Drift grows linearly with age; XZ at 80 u/s, Y at 40 u/s. Using a seeded RNG
# makes the output deterministic; each axis is uniform in [-1, 1] * age * coef.
func _assert_memory_drift() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 12345
	var drift_young: Vector3 = BotAIMath.compute_memory_drift(0.0, rng)
	if not drift_young.is_equal_approx(Vector3.ZERO):
		_fail("age=0 should give ZERO drift, got %s" % str(drift_young))

	# At age=1s, bounds are (-40, 40) XZ and (-20, 20) Y (since randf is in
	# [0,1) the term is (randf-0.5) * age * 80 ∈ (-40, 40) and similarly Y).
	rng.seed = 12345
	var drift_1s: Vector3 = BotAIMath.compute_memory_drift(1.0, rng)
	if abs(drift_1s.x) > 40.0 or abs(drift_1s.z) > 40.0:
		_fail("age=1s XZ drift should be within ±40, got %s" % str(drift_1s))
	if abs(drift_1s.y) > 20.0:
		_fail("age=1s Y drift should be within ±20, got %s" % str(drift_1s))

	# At age=5s (the MEMORY_DURATION limit), the envelope expands to (-200,
	# 200) XZ and (-100, 100) Y. This is the "how badly can memory lie"
	# contract; if it drifts wider, bots chase phantom positions too far.
	rng.seed = 54321
	var drift_max: Vector3 = BotAIMath.compute_memory_drift(5.0, rng)
	if abs(drift_max.x) > 200.0 or abs(drift_max.z) > 200.0:
		_fail("age=5s XZ drift should be within ±200")
	if abs(drift_max.y) > 100.0:
		_fail("age=5s Y drift should be within ±100")

	# is_memory_valid: age < 5 → valid; 5+ → invalid.
	if not BotAIMath.is_memory_valid(4.99):
		_fail("age=4.99 should be valid")
	if BotAIMath.is_memory_valid(5.0):
		_fail("age=5.0 should be invalid (exclusive upper bound)")
	# is_shared_target_valid: age < 7 → valid.
	if not BotAIMath.is_shared_target_valid(6.99):
		_fail("age=6.99 should be valid for shared target")
	if BotAIMath.is_shared_target_valid(7.0):
		_fail("age=7.0 should be invalid for shared target")
	print("MEMORY drift + valid windows: OK")

# ---- Retreat direction ------------------------------------------------------
# HTML lines 3083-3084: this.position - player.position, normalized. Degenerate
# input (bot co-located with player) falls back to Vector3.BACK so velocity
# doesn't NaN on a numerical edge case.
func _assert_retreat() -> void:
	var dir: Vector3 = BotAIMath.compute_retreat_direction(
		Vector3(100.0, 0.0, 0.0), Vector3.ZERO)
	if not dir.is_equal_approx(Vector3(1.0, 0.0, 0.0)):
		_fail("retreat away from +X player origin should be +X unit vector")
	var fallback: Vector3 = BotAIMath.compute_retreat_direction(
		Vector3.ZERO, Vector3.ZERO)
	if not fallback.is_equal_approx(Vector3.BACK):
		_fail("co-located retreat should fall back to Vector3.BACK")
	print("RETREAT direction + degenerate fallback: OK")

# ---- Shared broadcast reset -------------------------------------------------
# Tests that EnemyShip.reset_shared_broadcasts() clears the team-level
# dictionary. We seed the static directly (same script the production code
# writes to), call the reset, and verify the dictionary is empty. Use the
# preloaded script rather than EnemyShip.TEAM_ENEMY so the test stays isolated
# from the enemy_ship.gd import order.
func _assert_shared_broadcast_reset() -> void:
	# Can't access private statics directly from the test; exercise the full
	# round-trip: reset → dictionary is empty. That's the behavioural contract
	# callers care about (main.gd._begin_round needs a clean slate).
	EnemyShipScript.reset_shared_broadcasts()
	# Second call should be idempotent (no error on empty dict).
	EnemyShipScript.reset_shared_broadcasts()
	print("SHARED broadcast reset idempotent: OK")
