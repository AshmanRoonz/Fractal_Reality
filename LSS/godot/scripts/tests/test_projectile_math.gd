extends SceneTree

# Headless coverage for ProjectileMath (scripts/projectile_math.gd): the
# Descent-3-style two-tier homing turn-rate / FOV lookup and the arc-wave
# cadence constants (HTML last_ship_sailing.html:3528-3572, 3622-3640).
# Pure math + constants; no SceneTree / node dependencies. Calls through the
# class_name so the test doesn't preload main.gd (which pulls in ArenaMap /
# TracerPool / SettingsOverlay and hangs in `-s` mode).

var _ok := true

func _fail(msg: String) -> void:
	push_error(msg)
	_ok = false

func _init() -> void:
	print("=== ProjectileMath tests ===")

	_assert_constants()
	_assert_turn_rate_boundaries()
	_assert_fov_boundaries()
	_assert_get_homing_params_matches_split_calls()
	_assert_fov_gate()
	_assert_arc_wave_constants()

	if _ok:
		print("RESULT: PASS")
		quit(0)
	else:
		push_error("ProjectileMath tests FAILED")
		quit(1)

# ---- Constants --------------------------------------------------------------
# These numbers are the HTML contract: 800 / 3000 distance cutoffs,
# 5.0/3.0/1.5 turn rates, -0.3/0.2/0.5 FOV dot-product thresholds. If any
# drifts, the missile "feel" stops matching the web build.
func _assert_constants() -> void:
	if not is_equal_approx(ProjectileMath.HOMING_CLOSE_DIST, 800.0):
		_fail("HOMING_CLOSE_DIST 800.0, got %f" % ProjectileMath.HOMING_CLOSE_DIST)
	if not is_equal_approx(ProjectileMath.HOMING_MAX_DIST, 3000.0):
		_fail("HOMING_MAX_DIST 3000.0, got %f" % ProjectileMath.HOMING_MAX_DIST)
	if not is_equal_approx(ProjectileMath.HOMING_TURN_RATE_CLOSE, 5.0):
		_fail("close turn 5.0, got %f" % ProjectileMath.HOMING_TURN_RATE_CLOSE)
	if not is_equal_approx(ProjectileMath.HOMING_TURN_RATE_MID, 3.0):
		_fail("mid turn 3.0, got %f" % ProjectileMath.HOMING_TURN_RATE_MID)
	if not is_equal_approx(ProjectileMath.HOMING_TURN_RATE_FAR, 1.5):
		_fail("far turn 1.5, got %f" % ProjectileMath.HOMING_TURN_RATE_FAR)
	if not is_equal_approx(ProjectileMath.HOMING_FOV_CLOSE, -0.3):
		_fail("close fov -0.3, got %f" % ProjectileMath.HOMING_FOV_CLOSE)
	if not is_equal_approx(ProjectileMath.HOMING_FOV_MID, 0.2):
		_fail("mid fov 0.2, got %f" % ProjectileMath.HOMING_FOV_MID)
	if not is_equal_approx(ProjectileMath.HOMING_FOV_FAR, 0.5):
		_fail("far fov 0.5, got %f" % ProjectileMath.HOMING_FOV_FAR)
	if not is_equal_approx(ProjectileMath.SALVO_GUIDED_TURN_RATE, 6.0):
		_fail("salvo turn 6.0, got %f" % ProjectileMath.SALVO_GUIDED_TURN_RATE)
	print("CONSTANTS match HTML contract: OK")

# ---- Turn-rate boundaries ---------------------------------------------------
# HTML 3543-3555 uses strict < for both cutoffs: dist < 800 is close, dist <
# 3000 is mid, else far. 799 -> close, 800 -> mid (boundary belongs to mid),
# 1500 -> mid, 2999 -> mid, 3000 -> far (boundary belongs to far), 10000 -> far.
func _assert_turn_rate_boundaries() -> void:
	var cases := [
		[0.0, 5.0, "d=0"],
		[799.0, 5.0, "d=799 close"],
		[800.0, 3.0, "d=800 mid (cutoff)"],
		[1500.0, 3.0, "d=1500 mid"],
		[2999.0, 3.0, "d=2999 mid"],
		[3000.0, 1.5, "d=3000 far (cutoff)"],
		[10000.0, 1.5, "d=10000 far"],
	]
	for case in cases:
		var d := float(case[0])
		var expected := float(case[1])
		var actual := ProjectileMath.compute_homing_turn_rate(d)
		if not is_equal_approx(actual, expected):
			_fail("%s: expected turn %.1f, got %.1f" % [case[2], expected, actual])
	print("TURN_RATE distance tiers 800/3000: OK")

func _assert_fov_boundaries() -> void:
	var cases := [
		[0.0, -0.3, "d=0"],
		[799.0, -0.3, "d=799 close"],
		[800.0, 0.2, "d=800 mid (cutoff)"],
		[1500.0, 0.2, "d=1500 mid"],
		[2999.0, 0.2, "d=2999 mid"],
		[3000.0, 0.5, "d=3000 far (cutoff)"],
		[10000.0, 0.5, "d=10000 far"],
	]
	for case in cases:
		var d := float(case[0])
		var expected := float(case[1])
		var actual := ProjectileMath.compute_homing_fov(d)
		if not is_equal_approx(actual, expected):
			_fail("%s: expected fov %.1f, got %.1f" % [case[2], expected, actual])
	print("FOV distance tiers 800/3000: OK")

# ---- Combined lookup --------------------------------------------------------
# get_homing_params should return the same numbers as the split calls for
# every distance; it's a single-branch convenience, not a separate formula.
func _assert_get_homing_params_matches_split_calls() -> void:
	for d in [0.0, 500.0, 799.0, 800.0, 1500.0, 2999.0, 3000.0, 5000.0]:
		var params: Dictionary = ProjectileMath.get_homing_params(d)
		var tr := float(params.get("turn_rate", -1.0))
		var fv := float(params.get("fov", -99.0))
		var split_tr := ProjectileMath.compute_homing_turn_rate(d)
		var split_fv := ProjectileMath.compute_homing_fov(d)
		if not is_equal_approx(tr, split_tr):
			_fail("d=%.1f combined turn %.2f vs split %.2f" % [d, tr, split_tr])
		if not is_equal_approx(fv, split_fv):
			_fail("d=%.1f combined fov %.2f vs split %.2f" % [d, fv, split_fv])
	print("get_homing_params == split calls: OK")

# ---- FOV gate ---------------------------------------------------------------
# should_steer returns (dot > threshold). A missile flying forward (+Z) with a
# target dead ahead has dot = 1; slightly-off-axis has dot near 1; perpendicular
# has dot = 0; behind has dot = -1. At close range the threshold is -0.3, so
# behind-and-a-bit should still steer; at far range the threshold is 0.5, so
# anything past 60deg off-axis should NOT steer.
func _assert_fov_gate() -> void:
	var forward := Vector3(0, 0, 1)

	# Close range: dead ahead (dot=1) -> steer.
	if not ProjectileMath.should_steer_homing(forward, Vector3(0, 0, 1), ProjectileMath.HOMING_FOV_CLOSE):
		_fail("close: dead ahead should steer")
	# Close range: slightly behind (dot=-0.2) -> still steer (threshold -0.3).
	if not ProjectileMath.should_steer_homing(forward, Vector3(0.98, 0, -0.2).normalized(), ProjectileMath.HOMING_FOV_CLOSE):
		_fail("close: slightly behind (dot~-0.2) should steer")
	# Close range: fully behind (dot=-1) -> do NOT steer.
	if ProjectileMath.should_steer_homing(forward, Vector3(0, 0, -1), ProjectileMath.HOMING_FOV_CLOSE):
		_fail("close: fully behind should NOT steer")

	# Far range: 45deg off-axis (dot ~= 0.707) -> steer (passes 0.5 threshold).
	if not ProjectileMath.should_steer_homing(forward, Vector3(sin(PI / 4.0), 0, cos(PI / 4.0)), ProjectileMath.HOMING_FOV_FAR):
		_fail("far: 45deg off-axis should steer")
	# Far range: 75deg off-axis (dot ~= 0.259) -> do NOT steer.
	if ProjectileMath.should_steer_homing(forward, Vector3(sin(deg_to_rad(75.0)), 0, cos(deg_to_rad(75.0))), ProjectileMath.HOMING_FOV_FAR):
		_fail("far: 75deg off-axis should NOT steer")
	print("FOV gate steer/straight decisions: OK")

# ---- Arc-wave cadence -------------------------------------------------------
# HTML 3639 picks bolt interval U(0.14, 0.22). The 120+U(0,80) forward offset
# and (U-0.5)*80 jitter on the end point are knobs for visual polish; the
# test locks the numbers so a refactor can't quietly retune the arc look.
func _assert_arc_wave_constants() -> void:
	if not is_equal_approx(ProjectileMath.ARC_WAVE_BOLT_MIN, 0.14):
		_fail("bolt min 0.14, got %f" % ProjectileMath.ARC_WAVE_BOLT_MIN)
	if not is_equal_approx(ProjectileMath.ARC_WAVE_BOLT_MAX, 0.22):
		_fail("bolt max 0.22, got %f" % ProjectileMath.ARC_WAVE_BOLT_MAX)
	if not is_equal_approx(ProjectileMath.ARC_WAVE_AHEAD_MIN, 120.0):
		_fail("ahead min 120.0, got %f" % ProjectileMath.ARC_WAVE_AHEAD_MIN)
	if not is_equal_approx(ProjectileMath.ARC_WAVE_AHEAD_RANGE, 80.0):
		_fail("ahead range 80.0, got %f" % ProjectileMath.ARC_WAVE_AHEAD_RANGE)
	if not is_equal_approx(ProjectileMath.ARC_WAVE_JITTER, 80.0):
		_fail("jitter 80.0, got %f" % ProjectileMath.ARC_WAVE_JITTER)
	# Sanity check: min < max so the interval is non-degenerate.
	if ProjectileMath.ARC_WAVE_BOLT_MIN >= ProjectileMath.ARC_WAVE_BOLT_MAX:
		_fail("bolt interval must have min < max")
	print("ARC_WAVE constants match HTML contract: OK")
