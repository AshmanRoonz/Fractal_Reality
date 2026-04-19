class_name DeathCamMath
extends RefCounted

# Pure math + constants for the death-camera orbit (HTML last_ship_sailing.html:
# 11309-11347). Lives in its own file with a class_name so headless tests can
# call the static helpers without preloading main.gd (which pulls in ArenaMap,
# TracerPool, SettingsOverlay, and other class_name types that `-s` mode
# doesn't resolve). main.gd just references DeathCamMath.* so behavior stays
# in one place.
#
# HTML references:
#   startDeathCam: radius = hullLength * 4  (line 11312)
#   updateDeathCam: angle += dt * 0.4       (line 11337)
#   cam.position.y = target.y + 150          (line 11343)

const DEATH_CAM_HEIGHT := 150.0
const DEATH_CAM_ANGULAR_SPEED := 0.4
const DEATH_CAM_DEFAULT_RADIUS := 400.0

# Polar position around the target with a fixed +150 height. At angle 0 the cam
# sits at +X of the target; at pi/2 at +Z; at pi at -X; at 3pi/2 at -Z.
static func compute_death_cam_position(target: Vector3, angle: float, radius: float) -> Vector3:
	return Vector3(
		target.x + cos(angle) * radius,
		target.y + DEATH_CAM_HEIGHT,
		target.z + sin(angle) * radius
	)

# Orbit radius from the chassis dictionary. 80-unit floor keeps tiny craft
# outside their own explosion; the 100-unit hull_length fallback matches the
# HTML behaviour when a ship is mid-transition between chassis.
static func compute_death_cam_radius(chassis: Dictionary) -> float:
	var hull_length := float(chassis.get("hull_length", 100.0)) if chassis != null else 100.0
	return maxf(80.0, hull_length * 4.0)
