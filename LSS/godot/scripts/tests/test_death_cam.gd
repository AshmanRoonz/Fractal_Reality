extends SceneTree

# Headless coverage for the death camera helpers (HTML last_ship_sailing.html:
# 11309-11347). The orchestration code (_start_death_cam, _stop_death_cam,
# _tick_death_cam) lives on main.gd and requires arena_map/HUD/environment
# bootstrap to exercise, which cannot run in `-s` mode (several class_name
# types aren't registered by the single-script runner, so preloading main.gd
# hangs).
#
# The pure math + constants live in DeathCamMath (scripts/death_cam_math.gd),
# a small RefCounted with a class_name so it's reachable without preloading
# main.gd. Same pattern as GameData; test_game_mechanics.gd only reads
# MainScript CONSTANTS for the same reason (direct static-func dispatch
# through a preloaded script doesn't resolve because main.gd has no
# class_name).

var _ok := true

func _fail(msg: String) -> void:
	push_error(msg)
	_ok = false

func _init() -> void:
	print("=== Death camera tests ===")

	_assert_constants()
	_assert_position_math()
	_assert_radius_math()
	_assert_angle_advance()

	if _ok:
		print("RESULT: PASS")
		quit(0)
	else:
		push_error("Death camera tests FAILED")
		quit(1)

# ---- Constants ---------------------------------------------------------------
# HTML references:
#   startDeathCam: radius = hullLength * 4  (line 11312)
#   updateDeathCam: angle += dt * 0.4       (line 11337)
#   cam.position.y = target.y + 150          (line 11343)
#
# These three numbers are the whole contract; if they drift, the orbit changes
# pace or height and the HTML behaviour is no longer matched.
func _assert_constants() -> void:
	if not is_equal_approx(DeathCamMath.DEATH_CAM_HEIGHT, 150.0):
		_fail("DEATH_CAM_HEIGHT should be 150.0, got %f" % DeathCamMath.DEATH_CAM_HEIGHT)
	if not is_equal_approx(DeathCamMath.DEATH_CAM_ANGULAR_SPEED, 0.4):
		_fail("DEATH_CAM_ANGULAR_SPEED should be 0.4, got %f" % DeathCamMath.DEATH_CAM_ANGULAR_SPEED)
	if not is_equal_approx(DeathCamMath.DEATH_CAM_DEFAULT_RADIUS, 400.0):
		_fail("DEATH_CAM_DEFAULT_RADIUS should be 400.0, got %f" % DeathCamMath.DEATH_CAM_DEFAULT_RADIUS)
	print("CONSTANTS height=150 speed=0.4 default_radius=400: OK")

# ---- Position math -----------------------------------------------------------
# Polar coordinates around the target, with a fixed +150 height offset. At
# angle 0 the cam sits at +X of the target; at pi/2 at +Z; at pi at -X; at
# 3pi/2 at -Z. All three components need to line up with the HTML cos/sin
# wiring.
func _assert_position_math() -> void:
	# Quarter-turn sweep around origin at radius 400.
	_check_pos(Vector3.ZERO, 0.0, 400.0, Vector3(400.0, 150.0, 0.0), "angle=0")
	_check_pos(Vector3.ZERO, PI / 2.0, 400.0, Vector3(0.0, 150.0, 400.0), "angle=pi/2")
	_check_pos(Vector3.ZERO, PI, 400.0, Vector3(-400.0, 150.0, 0.0), "angle=pi")
	_check_pos(Vector3.ZERO, 3.0 * PI / 2.0, 400.0, Vector3(0.0, 150.0, -400.0), "angle=3pi/2")

	# Non-origin target: height adds to target.y, polar offset adds to x/z.
	_check_pos(Vector3(123.0, 45.0, -67.0), 1.25, 320.0,
		Vector3(123.0 + cos(1.25) * 320.0, 45.0 + 150.0, -67.0 + sin(1.25) * 320.0),
		"target(123,45,-67) angle=1.25 radius=320")

	# Negative yaw seed (matches a player.rotation.y below the horizon).
	_check_pos(Vector3(-500.0, 10.0, 800.0), -2.1, 400.0,
		Vector3(-500.0 + cos(-2.1) * 400.0, 10.0 + 150.0, 800.0 + sin(-2.1) * 400.0),
		"target(-500,10,800) angle=-2.1")

	# Zero radius: cam sits exactly at the target plus the 150 height offset.
	_check_pos(Vector3(1.0, 2.0, 3.0), 0.75, 0.0,
		Vector3(1.0, 2.0 + 150.0, 3.0),
		"radius=0 (degenerate)")

	print("POSITION polar math (+150 height): OK")

func _check_pos(target: Vector3, angle: float, radius: float, want: Vector3, label: String) -> void:
	var got: Vector3 = DeathCamMath.compute_death_cam_position(target, angle, radius)
	if not is_equal_approx(got.x, want.x) or not is_equal_approx(got.y, want.y) or not is_equal_approx(got.z, want.z):
		_fail("compute_death_cam_position[%s] got %s expected %s" % [label, str(got), str(want)])

# ---- Radius math -------------------------------------------------------------
# radius = max(80, hull_length * 4). The 80-unit floor keeps tiny craft from
# being inside their own explosion; the 100-unit default catches chassis
# dictionaries with no hull_length key.
func _assert_radius_math() -> void:
	# Default chassis: hull_length = 100 -> radius = 400.
	if not is_equal_approx(DeathCamMath.compute_death_cam_radius({"hull_length": 100.0}), 400.0):
		_fail("hull_length=100 should give radius 400")

	# Large chassis: hull_length = 250 -> radius = 1000.
	if not is_equal_approx(DeathCamMath.compute_death_cam_radius({"hull_length": 250.0}), 1000.0):
		_fail("hull_length=250 should give radius 1000")

	# Tiny chassis: hull_length = 10 -> 40, floored to 80.
	if not is_equal_approx(DeathCamMath.compute_death_cam_radius({"hull_length": 10.0}), 80.0):
		_fail("hull_length=10 should floor to 80")

	# Exactly at floor: hull_length = 20 -> 80 (no change).
	if not is_equal_approx(DeathCamMath.compute_death_cam_radius({"hull_length": 20.0}), 80.0):
		_fail("hull_length=20 should give exactly the floor 80")

	# Just above floor: hull_length = 21 -> 84 (above the floor).
	if not is_equal_approx(DeathCamMath.compute_death_cam_radius({"hull_length": 21.0}), 84.0):
		_fail("hull_length=21 should give 84 (just above the floor)")

	# Empty chassis: hull_length key missing -> fallback to 100.0 -> radius 400.
	if not is_equal_approx(DeathCamMath.compute_death_cam_radius({}), 400.0):
		_fail("empty chassis should fall back to hull_length=100 and give radius 400")

	# Extra keys are ignored; only hull_length drives the radius.
	if not is_equal_approx(DeathCamMath.compute_death_cam_radius({"hull_length": 150.0, "mass": 999.0}), 600.0):
		_fail("extra chassis keys should be ignored")

	print("RADIUS floor=80, fallback=400 on empty: OK")

# ---- Angle advancement -------------------------------------------------------
# _tick_death_cam does `_death_cam_angle += delta * DEATH_CAM_ANGULAR_SPEED`.
# Encodes the rate the constant lives to serve; if someone edits the tick
# formula to scale differently, these expected deltas change.
func _assert_angle_advance() -> void:
	var rate: float = DeathCamMath.DEATH_CAM_ANGULAR_SPEED
	# 1 second of ticking should advance by exactly 0.4 rad.
	if not is_equal_approx(1.0 * rate, 0.4):
		_fail("1.0s tick should advance 0.4 rad, got %f" % (1.0 * rate))
	# 2.5 seconds -> 1.0 rad.
	if not is_equal_approx(2.5 * rate, 1.0):
		_fail("2.5s tick should advance 1.0 rad, got %f" % (2.5 * rate))
	# Full loop: 2*pi / 0.4 ~ 15.708 seconds per revolution.
	var period := (2.0 * PI) / rate
	if period < 15.0 or period > 16.0:
		_fail("full orbit period should land near 15.71s, got %f" % period)
	print("ANGLE 0.4 rad/sec -> ~15.71s period: OK")
