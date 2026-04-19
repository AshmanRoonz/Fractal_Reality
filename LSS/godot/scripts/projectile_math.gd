class_name ProjectileMath
extends RefCounted

# Pure math + constants for projectile flight tuning (HTML
# last_ship_sailing.html:3528-3572). Lives in its own file with a class_name
# so headless tests can call the helpers without preloading main.gd (which
# pulls in ArenaMap, TracerPool, SettingsOverlay, and other class_name types
# that `-s` mode doesn't resolve). The orchestration (spawn, despawn, hit
# detection) lives in main.gd; only the deterministic pieces belong here.

# ---- Two-tier homing (HTML lines 3539-3555) --------------------------------
# Descent-3-style: close range gets aggressive tracking (loose FOV, almost
# 180deg including slightly-behind targets); mid range moderate; far range
# gentle with tight FOV so missiles can be outmaneuvered at distance.
const HOMING_CLOSE_DIST := 800.0
const HOMING_MAX_DIST := 3000.0

const HOMING_TURN_RATE_CLOSE := 5.0
const HOMING_TURN_RATE_MID := 3.0
const HOMING_TURN_RATE_FAR := 1.5

# fov_threshold is a dot-product cutoff between current velocity direction and
# direction-to-target. Below the threshold the missile flies straight.
# -0.3 = can track targets slightly behind (>108deg off-axis); 0.2 = within
# ~78deg cone; 0.5 = within 60deg cone.
const HOMING_FOV_CLOSE := -0.3
const HOMING_FOV_MID := 0.2
const HOMING_FOV_FAR := 0.5

# Salvo-core remote guidance: aggressive turn rate with no FOV gate (player
# has full crosshair control). HTML line 3570.
const SALVO_GUIDED_TURN_RATE := 6.0

# Arc-wave bolt cadence: spawn a forward-ahead lightning bolt every
# 0.14-0.22s (HTML line 3639). ~4-7 bolts/sec.
const ARC_WAVE_BOLT_MIN := 0.14
const ARC_WAVE_BOLT_MAX := 0.22

# Forward offset of each bolt from the projectile: 120 + U(0,80) (HTML 3627).
const ARC_WAVE_AHEAD_MIN := 120.0
const ARC_WAVE_AHEAD_RANGE := 80.0

# End-point jitter cube for the bolt tip (HTML 3628-3630). Uniform in
# [-40, 40] per axis (the HTML uses (rand-0.5)*80).
const ARC_WAVE_JITTER := 80.0

# Turn-rate for the current homing regime.
static func compute_homing_turn_rate(distance: float) -> float:
	if distance < HOMING_CLOSE_DIST:
		return HOMING_TURN_RATE_CLOSE
	if distance < HOMING_MAX_DIST:
		return HOMING_TURN_RATE_MID
	return HOMING_TURN_RATE_FAR

# FOV cutoff (dot-product) for the current homing regime. Caller compares
# dot(velocity_dir, to_target_dir) > fov_threshold to decide whether to steer.
static func compute_homing_fov(distance: float) -> float:
	if distance < HOMING_CLOSE_DIST:
		return HOMING_FOV_CLOSE
	if distance < HOMING_MAX_DIST:
		return HOMING_FOV_MID
	return HOMING_FOV_FAR

# Combined lookup so callers can get both values in one branch. Dictionary
# keeps the return typed-safe at the call site (float get with default).
static func get_homing_params(distance: float) -> Dictionary:
	if distance < HOMING_CLOSE_DIST:
		return {"turn_rate": HOMING_TURN_RATE_CLOSE, "fov": HOMING_FOV_CLOSE}
	if distance < HOMING_MAX_DIST:
		return {"turn_rate": HOMING_TURN_RATE_MID, "fov": HOMING_FOV_MID}
	return {"turn_rate": HOMING_TURN_RATE_FAR, "fov": HOMING_FOV_FAR}

# FOV gate: true if the missile should actively steer this frame, false if it
# should fly straight (target is too far off-axis for current tracking regime).
# velocity_dir and to_target_dir should already be normalized; caller verifies
# both are non-zero before calling.
static func should_steer_homing(velocity_dir: Vector3, to_target_dir: Vector3,
		fov_threshold: float) -> bool:
	return velocity_dir.dot(to_target_dir) > fov_threshold
