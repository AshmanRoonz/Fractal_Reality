class_name BotAIMath
extends RefCounted

# Pure math + constants for the bot AI (HTML last_ship_sailing.html:2959-3393).
# Lives in its own file with a class_name so headless tests can call the
# helpers without preloading enemy_ship.gd (which pulls in PlayerShip /
# ArenaMap / GameData via preload). The orchestration (state, timers, fire
# signals, RNG seeding) lives in enemy_ship.gd; only the deterministic
# pieces belong here.
#
# HTML line references are intentionally dense so the grammar of the port is
# inspectable without opening the browser bundle.

# ---- Squad coordination -----------------------------------------------------
# this.aiRole = Math.random() < 0.33 ? 'flank' : 'engage';   (HTML line 3000)
const FLANK_ROLE_PROBABILITY := 0.33

# Flank offset: 600 units perpendicular to the player axis, blended 60% into
# the movement direction (HTML lines 3092-3099). Bot only flanks when the
# live player distance is in the (300, 3000) band: too close and the offset
# is useless; too far and the bot wastes time.
const FLANK_OFFSET := 600.0
const FLANK_MIN_DISTANCE := 300.0
const FLANK_MAX_DISTANCE := 3000.0
const FLANK_BLEND := 0.6

# ---- Strafing ---------------------------------------------------------------
# aiStrafeTimer = 1 + random*2; strafe on if dist < aiRangePreference * 1.5;
# perp * dir * 0.5 (HTML lines 3069-3108).
const STRAFE_TIMER_MIN := 1.0
const STRAFE_TIMER_MAX := 3.0
const STRAFE_RANGE_MULT := 1.5
const STRAFE_BLEND := 0.5

# ---- Memory / squad share ---------------------------------------------------
# Own memory expires after 5 seconds; squad shared target after 7 seconds
# (HTML lines 3207, 3216). A 2-second gap on purpose: stale squad info beats
# staler solo memory.
const MEMORY_DURATION := 5.0
const SHARED_TARGET_DURATION := 7.0

# Memory drift grows linearly with age (HTML lines 3218-3223). Each axis is
# uniform in [-1, 1] * age * coefficient; XZ drifts at 80 u/s, Y at 40 u/s
# (ships drift faster laterally than vertically, matching HTML spatial bias).
const MEMORY_DRIFT_XZ := 80.0
const MEMORY_DRIFT_Y := 40.0

# ---- Firing -----------------------------------------------------------------
# withinRange = distToPlayer <= preferredDist * 1.3 (HTML line 3162).
const RANGE_FIRE_MULT := 1.3

# accuracy = 0.25 + rangeRatio * 0.45 where rangeRatio = max(0, 1 -
# dist/weapon.range) (HTML lines 3295-3296). Floor 25% so bots still
# occasionally land shots at the edge of range; ceiling 70% so point-blank
# isn't a guaranteed kill.
const ACCURACY_BASE := 0.25
const ACCURACY_RANGE_BONUS := 0.45

# ---- findTarget cadence -----------------------------------------------------
# aiTimer = 1 + random*2 (HTML line 3064). Separate from the combat decision
# timer (0.35-0.6s in enemy_ship.gd) which governs ability activation.
const FIND_TARGET_INTERVAL_MIN := 1.0
const FIND_TARGET_INTERVAL_MAX := 3.0

# Range preferences per loadout. Mirrors HTML getLoadoutRangePreference
# (lines 3017-3028): SCORCH / RONIN close (500 units); NORTHSTAR long
# (1500); TONE / LEGION / ION medium (1000-1200); MONARCH medium-close (800).
static func get_loadout_range_preference(loadout_key: String) -> float:
	match loadout_key:
		"SCORCH", "RONIN":
			return 500.0
		"NORTHSTAR":
			return 1500.0
		"TONE":
			return 1200.0
		"LEGION":
			return 1000.0
		"MONARCH":
			return 800.0
		"ION":
			return 1000.0
	return 800.0

# Squad role from an RNG draw in [0, 1). Kept as a pure function so tests
# can sweep the boundary without tying to RandomNumberGenerator state.
static func assign_squad_role(rng_value: float) -> String:
	return "flank" if rng_value < FLANK_ROLE_PROBABILITY else "engage"

# Right-of-direction in the XZ plane (up × direction). When the input is
# ~vertical the cross collapses, so fall back to Vector3.RIGHT so flank /
# strafe vectors are well-defined for edge cases (bot directly above / below
# the player).
static func compute_horizontal_right(direction: Vector3) -> Vector3:
	var right := Vector3.UP.cross(direction)
	if right.length_squared() < 0.0001:
		return Vector3.RIGHT
	return right.normalized()

# Flank position: 600 units to the player's right along the bot-to-player
# axis. Bot moves toward this instead of the player's exact position when
# playing the flanker role.
static func compute_flank_target(player_pos: Vector3, bot_pos: Vector3) -> Vector3:
	var to_player := player_pos - bot_pos
	if to_player.length_squared() < 0.0001:
		return player_pos
	var dir := to_player.normalized()
	return player_pos + compute_horizontal_right(dir) * FLANK_OFFSET

# Gate for the flank blend (HTML line 3092). Role check is included so
# callers can pass the bot's role directly without an outer conditional.
static func should_flank(distance_to_player: float, role: String) -> bool:
	return role == "flank" \
		and distance_to_player > FLANK_MIN_DISTANCE \
		and distance_to_player < FLANK_MAX_DISTANCE

# Strafe perpendicular with the HTML blend factor baked in (line 3106:
# perpendicular * dir * 0.5). Returns a signed unit vector scaled by the
# blend factor; callers multiply by strafe_speed before adding to velocity.
static func compute_strafe_offset(aim_dir: Vector3, strafe_sign: float) -> Vector3:
	var perp := Vector3.UP.cross(aim_dir)
	if perp.length_squared() < 0.0001:
		return Vector3.ZERO
	return perp.normalized() * strafe_sign * STRAFE_BLEND

# Strafe engagement gate: active flag + within 1.5x range preference + not
# doomed (HTML lines 3103-3108). Doom override mirrors the retreat-overrides-
# strafe semantics where a fleeing bot commits to the escape.
static func should_strafe(strafe_active: bool, distance_to_player: float,
		range_preference: float, is_doomed: bool) -> bool:
	return strafe_active \
		and not is_doomed \
		and distance_to_player < range_preference * STRAFE_RANGE_MULT

# Accuracy as hit-probability for a fire attempt (HTML lines 3295-3297).
# Range ratio is clamped to [0, 1] so shots at or beyond weapon.range stay at
# the 0.25 floor rather than going negative.
static func compute_accuracy(distance: float, weapon_range: float) -> float:
	var range_ratio := clampf(1.0 - distance / maxf(1.0, weapon_range), 0.0, 1.0)
	return ACCURACY_BASE + range_ratio * ACCURACY_RANGE_BONUS

# Range gate for firing (HTML line 3162). Combines with the weapon.range cap
# upstream: a bot only fires if both constraints are satisfied.
static func is_within_firing_range(distance: float, range_preference: float) -> bool:
	return distance <= range_preference * RANGE_FIRE_MULT

# Memory drift vector: position fuzz grows with age so stale last-known
# positions slowly wander. Uses the supplied RNG so tests can seed and get
# deterministic output; each axis is independent U(-1, 1) * age * coef.
static func compute_memory_drift(age: float, rng: RandomNumberGenerator) -> Vector3:
	return Vector3(
		(rng.randf() - 0.5) * age * MEMORY_DRIFT_XZ,
		(rng.randf() - 0.5) * age * MEMORY_DRIFT_Y,
		(rng.randf() - 0.5) * age * MEMORY_DRIFT_XZ,
	)

static func is_memory_valid(age: float) -> bool:
	return age < MEMORY_DURATION

static func is_shared_target_valid(age: float) -> bool:
	return age < SHARED_TARGET_DURATION

# Retreat direction: away from the player, normalized (HTML lines 3083-3084:
# this.position - player.position, normalized). Degenerate input (co-located
# bot and player) falls back to Vector3.BACK so velocity doesn't NaN.
static func compute_retreat_direction(bot_pos: Vector3, player_pos: Vector3) -> Vector3:
	var away := bot_pos - player_pos
	if away.length_squared() < 0.0001:
		return Vector3.BACK
	return away.normalized()
