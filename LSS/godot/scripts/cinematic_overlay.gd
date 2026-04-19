class_name CinematicOverlay
extends Control

# Bundles the eight cinematic overlays from last_ship_sailing.html that sit
# above the base HUD but below the banner / scoreboard:
#   1. hit marker     ; 0.25s white cross flash when the player deals damage
#   2. kill marker    ; 0.5s red X flash when the player scores a kill
#   3. killstreak     ; "DOUBLE KILL" through "GODLIKE" announcement (2s)
#   4. medal          ; stacked medal popups (first blood / longshot / ...)
#   5. countdown      ; 3, 2, 1, FIGHT at round start (0.9s / 1.2s)
#   6. ability flash  ; edge glow + "X ACTIVE" label (0.8s)
#   7. respawn        ; persistent destroyed overlay until hide_respawn()
#   8. exec prompt    ; "RAM TO EXECUTE" banner for doomed-enemy finisher
#
# All animations are driven by `_timer += delta` counters so the overlays
# work headless (no Tween / AnimationPlayer required); _draw() reads the
# timers and paints the current frame. This matches the structure of
# banner_overlay.gd and damage_overlay.gd.

# ---------------------------------------------------------------------------
# Hit / kill marker constants

const HIT_MARKER_DURATION := 0.25
const KILL_MARKER_DURATION := 0.5
const HIT_COLOR := Color(1.0, 1.0, 1.0, 1.0)
const KILL_COLOR := Color(1.0, 0.2, 0.1, 1.0)
const HIT_SIZE := 30.0
const KILL_SIZE := 40.0
const MARKER_LINE_THICKNESS := 2.0

# ---------------------------------------------------------------------------
# Killstreak constants. Index by min(count, STREAK_DATA.size() - 1); entries
# 0 and 1 are null (no popup for a solo kill). Ported from HTML lines
# 10148-10156.

const KILLSTREAK_DURATION := 2.0
const KILLSTREAK_Y_RATIO := 0.28   # top: 28% (HTML)
const KILLSTREAK_LABEL_SIZE := 42
const KILLSTREAK_COUNT_SIZE := 14
const KILLSTREAK_LETTER_SPACING := 6.0

const STREAK_DATA := [
	{},
	{},
	{"label": "DOUBLE KILL",  "color": Color(1.0, 0.8, 0.0, 1.0),   "scale": 1.10, "glow": false},
	{"label": "TRIPLE KILL",  "color": Color(1.0, 0.53, 0.0, 1.0),  "scale": 1.20, "glow": false},
	{"label": "QUAD KILL",    "color": Color(1.0, 0.27, 0.0, 1.0),  "scale": 1.35, "glow": false},
	{"label": "RAMPAGE",      "color": Color(1.0, 0.0, 0.27, 1.0),  "scale": 1.50, "glow": false},
	{"label": "UNSTOPPABLE",  "color": Color(0.8, 0.0, 1.0, 1.0),   "scale": 1.60, "glow": false},
	{"label": "GODLIKE",      "color": Color(1.0, 0.0, 1.0, 1.0),   "scale": 1.70, "glow": true},
]

# ---------------------------------------------------------------------------
# Medals. Each medal row lives independently with its own timer; when the
# timer expires the row is removed from _medals.

const MEDAL_DURATION := 2.2
const MEDAL_Y_RATIO := 0.62
const MEDAL_ROW_HEIGHT := 24.0
const MEDAL_ICON_SIZE := 18
const MEDAL_LABEL_SIZE := 11
const MEDAL_LABEL_SPACING := 2.0
const MEDAL_PADDING_X := 14.0
const MEDAL_PADDING_Y := 4.0
const MEDAL_ICON_GAP := 8.0

const MEDAL_DATA := {
	"firstBlood": {"icon": "◉", "label": "FIRST BLOOD", "color": Color(1.0, 0.0, 0.27, 1.0)},
	"revenge":    {"icon": "⟳", "label": "REVENGE",     "color": Color(0.8, 0.27, 1.0, 1.0)},
	"shutdown":   {"icon": "✹", "label": "SHUTDOWN",    "color": Color(1.0, 0.67, 0.0, 1.0)},
	"longshot":   {"icon": "—", "label": "LONGSHOT",    "color": Color(0.27, 0.8, 1.0, 1.0)},
	"assist":     {"icon": "Φ", "label": "ASSIST",      "color": Color(0.4, 1.0, 0.4, 1.0)},
	"savior":     {"icon": "○", "label": "SAVIOR",      "color": Color(0.27, 0.67, 1.0, 1.0)},
	"execution":  {"icon": "•", "label": "EXECUTION",   "color": Color(1.0, 0.13, 0.0, 1.0)},
}

# ---------------------------------------------------------------------------
# Countdown constants. "FIGHT" uses a longer animation (1.2s) than numeric
# ticks (0.9s).

const COUNTDOWN_NUMBER_DURATION := 0.9
const COUNTDOWN_FIGHT_DURATION := 1.2
const COUNTDOWN_Y_RATIO := 0.40
const COUNTDOWN_LABEL_SIZE := 12
const COUNTDOWN_NUMBER_SIZE := 96
const COUNTDOWN_FIGHT_SIZE := 64
const COUNTDOWN_RING_START_RADIUS := 40.0
const COUNTDOWN_RING_END_RADIUS := 140.0
const COUNTDOWN_LABEL_COLOR := Color(1.0, 0.67, 0.0, 0.67)
const COUNTDOWN_NUMBER_COLOR := Color(1.0, 1.0, 1.0, 1.0)
const COUNTDOWN_FIGHT_COLOR := Color(1.0, 0.27, 0.0, 1.0)
const COUNTDOWN_RING_COLOR := Color(1.0, 0.67, 0.0, 0.4)

# ---------------------------------------------------------------------------
# Ability flash constants.

const ABILITY_FLASH_DURATION := 0.8
const ABILITY_LABEL_SIZE := 14
const ABILITY_LABEL_SPACING := 4.0
const ABILITY_Y_RATIO := 0.52
const ABILITY_EDGE_GLOW_WIDTH := 60.0   # Inner shadow approximation thickness

# Keyed by ability_id (not name) so main.gd can look up without the name
# string. Any unknown id falls back to the default color.
const ABILITY_COLORS := {
	"phase_dash":      Color(0.0,  0.8,  1.0, 1.0),   # dash
	"afterburner":     Color(1.0,  0.67, 0.0, 1.0),   # overclock
	"vortex_shield":   Color(0.27, 0.53, 1.0, 1.0),   # shield
	"thermal_shield":  Color(0.27, 0.53, 1.0, 1.0),
	"sword_block":     Color(0.27, 0.53, 1.0, 1.0),
	"gun_shield":      Color(0.27, 0.53, 1.0, 1.0),
	"emp_burst":       Color(1.0,  0.27, 0.0, 1.0),
	"firewall":        Color(1.0,  0.27, 0.0, 1.0),
	"arc_wave":        Color(1.0,  0.27, 0.0, 1.0),
	"laser_shot":      Color(1.0,  0.27, 0.0, 1.0),
	"power_shot":      Color(1.0,  0.67, 0.0, 1.0),
	"heal":            Color(0.27, 1.0,  0.53, 1.0),
	"rearm":           Color(0.27, 1.0,  0.53, 1.0),
	"energy_siphon":   Color(0.27, 1.0,  0.53, 1.0),
	"stasis_field":    Color(0.0,  1.0,  0.8, 1.0),
	"trip_wire":       Color(0.0,  1.0,  0.8, 1.0),
	"tether_trap":     Color(0.0,  1.0,  0.8, 1.0),
	"cluster_missile": Color(1.0,  0.4,  0.0, 1.0),
	"tracker_rockets": Color(1.0,  0.4,  0.0, 1.0),
	"rocket_salvo":    Color(1.0,  0.4,  0.0, 1.0),
	"mode_switch":     Color(1.0,  1.0,  1.0, 1.0),
	"particle_wall":   Color(0.27, 0.53, 1.0, 1.0),
	"incendiary_trap": Color(1.0,  0.27, 0.0, 1.0),
}
const ABILITY_DEFAULT_COLOR := Color(1.0, 1.0, 1.0, 1.0)

# ---------------------------------------------------------------------------
# Respawn / execution prompt. Respawn persists until hide_respawn() (one
# life per round). Execution prompt is purely driven by set_execution_prompt()
# from main.gd's doomed-enemy proximity check.

const RESPAWN_FADE := 0.6
const RESPAWN_TITLE_COLOR := Color(1.0, 0.13, 0.0, 1.0)
const RESPAWN_KILLER_COLOR := Color(0.67, 0.67, 0.67, 1.0)
const RESPAWN_KILLER_NAME_COLOR := Color(1.0, 0.4, 0.4, 1.0)
const RESPAWN_WAIT_COLOR := Color(1.0, 0.67, 0.0, 0.8)
const RESPAWN_TITLE_SIZE := 36
const RESPAWN_KILLER_SIZE := 13
const RESPAWN_WAIT_SIZE := 14

const EXEC_PROMPT_Y_RATIO := 0.55
const EXEC_PROMPT_COLOR := Color(1.0, 0.27, 0.0, 1.0)
const EXEC_PROMPT_SIZE := 13
const EXEC_PROMPT_SPACING := 2.0
const EXEC_PROMPT_TEXT := "RAM TO EXECUTE"

# ---------------------------------------------------------------------------
# Runtime state

var _hit_marker_timer: float = -1.0
var _kill_marker_timer: float = -1.0

var _streak_timer: float = -1.0
var _streak_data: Dictionary = {}
var _streak_count: int = 0

# _medals is an array of {timer, data}; each row ages independently.
var _medals: Array = []

var _countdown_timer: float = -1.0
var _countdown_duration: float = 0.9
var _countdown_number: String = ""
var _countdown_label: String = ""
var _countdown_is_fight: bool = false

var _ability_timer: float = -1.0
var _ability_label: String = ""
var _ability_color: Color = ABILITY_DEFAULT_COLOR

var _respawn_visible: bool = false
var _respawn_fade: float = 0.0   # 0 = hidden, 1 = fully shown
var _respawn_killer: String = ""

var _exec_prompt_visible: bool = false

func _ready() -> void:
	mouse_filter = MOUSE_FILTER_IGNORE
	focus_mode = FOCUS_NONE
	set_anchors_preset(PRESET_FULL_RECT)

# ---------------------------------------------------------------------------
# Public API (called by hud.gd / main.gd)

func show_hit_marker() -> void:
	_hit_marker_timer = 0.0
	queue_redraw()

func show_kill_marker() -> void:
	_kill_marker_timer = 0.0
	queue_redraw()

# count < 2 is a no-op (solo kills don't announce); values past the top tier
# clamp to GODLIKE, matching the HTML's STREAK_DATA indexing.
func show_killstreak(count: int) -> void:
	if count < 2:
		return
	var index: int = min(count, STREAK_DATA.size() - 1)
	_streak_data = STREAK_DATA[index]
	_streak_count = count
	_streak_timer = 0.0
	queue_redraw()

# Unknown medal types are silently ignored (matches HTML's `if (!m) return`).
func show_medal(type_id: String) -> void:
	if not MEDAL_DATA.has(type_id):
		return
	_medals.append({
		"timer": 0.0,
		"data": MEDAL_DATA[type_id],
	})
	queue_redraw()

# n is int or "FIGHT"; use 0 / "FIGHT" for the fight beat. `label` is the
# small caption above the number (e.g. "ROUND 1").
func show_countdown(n: Variant, label: String = "") -> void:
	var is_fight: bool = (typeof(n) == TYPE_STRING and String(n) == "FIGHT") \
			or (typeof(n) == TYPE_INT and int(n) == 0)
	_countdown_is_fight = is_fight
	_countdown_label = label
	_countdown_number = "FIGHT" if is_fight else str(n)
	_countdown_duration = COUNTDOWN_FIGHT_DURATION if is_fight else COUNTDOWN_NUMBER_DURATION
	_countdown_timer = 0.0
	queue_redraw()

# Prefer passing an explicit color from main.gd (looked up via ABILITY_COLORS
# by ability_id); pass Color(0,0,0,0) to request the default white.
func show_ability_flash(ability_name: String, color: Color = Color(0, 0, 0, 0)) -> void:
	_ability_label = ability_name.to_upper() + " ACTIVE"
	_ability_color = ABILITY_DEFAULT_COLOR if color.a <= 0.0 else color
	_ability_timer = 0.0
	queue_redraw()

# Respawn stays visible until hide_respawn() is called. The killer name is
# optional; pass "" to hide the "KILLED BY X" line.
func show_respawn(killer_name: String = "") -> void:
	_respawn_visible = true
	_respawn_killer = killer_name
	queue_redraw()

func hide_respawn() -> void:
	_respawn_visible = false
	queue_redraw()

func is_respawn_visible() -> bool:
	return _respawn_visible

func set_execution_prompt(visible: bool) -> void:
	if _exec_prompt_visible == visible:
		return
	_exec_prompt_visible = visible
	queue_redraw()

# ---------------------------------------------------------------------------
# Lookup helpers (exposed for main.gd's wiring logic)

static func color_for_ability(ability_id: String) -> Color:
	return ABILITY_COLORS.get(ability_id, ABILITY_DEFAULT_COLOR)

# ---------------------------------------------------------------------------
# Frame update. Each overlay has its own timer; expired timers flip back to
# -1 (idle) so _draw() can early-out cheaply.

func _process(delta: float) -> void:
	var dirty := false

	if _hit_marker_timer >= 0.0:
		_hit_marker_timer += delta
		if _hit_marker_timer >= HIT_MARKER_DURATION:
			_hit_marker_timer = -1.0
		dirty = true

	if _kill_marker_timer >= 0.0:
		_kill_marker_timer += delta
		if _kill_marker_timer >= KILL_MARKER_DURATION:
			_kill_marker_timer = -1.0
		dirty = true

	if _streak_timer >= 0.0:
		_streak_timer += delta
		if _streak_timer >= KILLSTREAK_DURATION:
			_streak_timer = -1.0
			_streak_data = {}
			_streak_count = 0
		dirty = true

	if _medals.size() > 0:
		var kept: Array = []
		for row in _medals:
			row["timer"] = float(row["timer"]) + delta
			if float(row["timer"]) < MEDAL_DURATION:
				kept.append(row)
		_medals = kept
		dirty = true

	if _countdown_timer >= 0.0:
		_countdown_timer += delta
		if _countdown_timer >= _countdown_duration:
			_countdown_timer = -1.0
		dirty = true

	if _ability_timer >= 0.0:
		_ability_timer += delta
		if _ability_timer >= ABILITY_FLASH_DURATION:
			_ability_timer = -1.0
		dirty = true

	# Respawn fade: animate _respawn_fade 0->1 while visible, 1->0 when hidden.
	var target_fade: float = 1.0 if _respawn_visible else 0.0
	if not is_equal_approx(_respawn_fade, target_fade):
		var step: float = delta / RESPAWN_FADE
		if _respawn_fade < target_fade:
			_respawn_fade = min(target_fade, _respawn_fade + step)
		else:
			_respawn_fade = max(target_fade, _respawn_fade - step)
		dirty = true

	if dirty:
		queue_redraw()

# ---------------------------------------------------------------------------
# Rendering

func _draw() -> void:
	var viewport_size := get_viewport_rect().size

	_draw_hit_marker(viewport_size)
	_draw_kill_marker(viewport_size)
	_draw_killstreak(viewport_size)
	_draw_medals(viewport_size)
	_draw_countdown(viewport_size)
	_draw_ability_flash(viewport_size)
	_draw_respawn(viewport_size)
	_draw_execution_prompt(viewport_size)

func _draw_hit_marker(viewport_size: Vector2) -> void:
	if _hit_marker_timer < 0.0:
		return
	# Approximate hitFlash keyframes (1.3x scale, fading alpha).
	var progress := _hit_marker_timer / HIT_MARKER_DURATION
	var scale: float
	var alpha: float
	if progress < 0.5:
		scale = lerp(1.3, 1.0, progress * 2.0)
		alpha = lerp(1.0, 0.9, progress * 2.0)
	else:
		scale = lerp(1.0, 0.8, (progress - 0.5) * 2.0)
		alpha = lerp(0.9, 0.0, (progress - 0.5) * 2.0)
	var size := HIT_SIZE * scale
	var center := viewport_size * 0.5
	var color := Color(HIT_COLOR.r, HIT_COLOR.g, HIT_COLOR.b, alpha)
	# Cross shape: two perpendicular rectangles.
	var half := size * 0.5
	draw_rect(Rect2(center.x - half, center.y - MARKER_LINE_THICKNESS * 0.5, size, MARKER_LINE_THICKNESS), color)
	draw_rect(Rect2(center.x - MARKER_LINE_THICKNESS * 0.5, center.y - half, MARKER_LINE_THICKNESS, size), color)

func _draw_kill_marker(viewport_size: Vector2) -> void:
	if _kill_marker_timer < 0.0:
		return
	# Approximate killFlash keyframes (1.5x scale, shrinking + fading).
	var progress := _kill_marker_timer / KILL_MARKER_DURATION
	var scale: float
	var alpha: float
	if progress < 0.3:
		scale = lerp(1.5, 1.0, progress / 0.3)
		alpha = 1.0
	else:
		scale = lerp(1.0, 0.6, (progress - 0.3) / 0.7)
		alpha = lerp(1.0, 0.0, (progress - 0.3) / 0.7)
	var size := KILL_SIZE * scale
	var center := viewport_size * 0.5
	var color := Color(KILL_COLOR.r, KILL_COLOR.g, KILL_COLOR.b, alpha)
	# X shape: two diagonals.
	var half := size * 0.5
	draw_line(
		Vector2(center.x - half, center.y - half),
		Vector2(center.x + half, center.y + half),
		color, MARKER_LINE_THICKNESS,
	)
	draw_line(
		Vector2(center.x - half, center.y + half),
		Vector2(center.x + half, center.y - half),
		color, MARKER_LINE_THICKNESS,
	)

func _draw_killstreak(viewport_size: Vector2) -> void:
	if _streak_timer < 0.0 or _streak_data.is_empty():
		return
	var progress := _streak_timer / KILLSTREAK_DURATION
	var alpha: float
	if progress < 0.08:
		alpha = progress / 0.08
	elif progress < 0.70:
		alpha = 1.0
	else:
		alpha = maxf(0.0, 1.0 - (progress - 0.70) / 0.30)

	var base_scale := float(_streak_data.get("scale", 1.0))
	var label_color: Color = _streak_data.get("color", Color(1, 1, 1, 1))
	label_color.a = alpha
	var label_text := String(_streak_data.get("label", ""))

	var font := get_theme_default_font()
	var label_size_px := int(round(KILLSTREAK_LABEL_SIZE * base_scale))
	var label_width := _measure_spaced(font, label_text, label_size_px, KILLSTREAK_LETTER_SPACING)
	var center_x := viewport_size.x * 0.5
	var center_y := viewport_size.y * KILLSTREAK_Y_RATIO

	# Glow: four offset draws around the main text.
	var glow_color := Color(label_color.r, label_color.g, label_color.b, alpha * 0.35)
	for offset in [Vector2(-2, 0), Vector2(2, 0), Vector2(0, -2), Vector2(0, 2)]:
		_draw_spaced(font, Vector2(center_x - label_width * 0.5, center_y) + offset,
				label_text, label_size_px, KILLSTREAK_LETTER_SPACING, glow_color)
	_draw_spaced(font, Vector2(center_x - label_width * 0.5, center_y),
			label_text, label_size_px, KILLSTREAK_LETTER_SPACING, label_color)

	# Kill count line below.
	var count_text := "%d KILLS" % _streak_count
	var count_color := Color(label_color.r, label_color.g, label_color.b, alpha * 0.67)
	var count_width := font.get_string_size(count_text, HORIZONTAL_ALIGNMENT_LEFT, -1.0, KILLSTREAK_COUNT_SIZE).x
	font.draw_string(get_canvas_item(), Vector2(center_x - count_width * 0.5, center_y + label_size_px * 0.6),
			count_text, HORIZONTAL_ALIGNMENT_LEFT, -1.0, KILLSTREAK_COUNT_SIZE, count_color)

	# Under-bar (width scales with count, like --ks-bar-w).
	var bar_w := (60.0 + float(_streak_count) * 12.0) * base_scale
	draw_rect(Rect2(center_x - bar_w * 0.5, center_y + label_size_px * 0.7 + 10.0, bar_w, 2.0),
			Color(label_color.r, label_color.g, label_color.b, alpha))

func _draw_medals(viewport_size: Vector2) -> void:
	if _medals.is_empty():
		return
	var font := get_theme_default_font()
	var center_x := viewport_size.x * 0.5
	var base_y := viewport_size.y * MEDAL_Y_RATIO
	var y := base_y
	for row in _medals:
		var progress := float(row["timer"]) / MEDAL_DURATION
		var alpha: float
		var x_offset: float
		if progress < 0.08:
			alpha = progress / 0.08
			x_offset = lerp(-40.0, 4.0, progress / 0.08)
		elif progress < 0.12:
			alpha = 1.0
			x_offset = lerp(4.0, 0.0, (progress - 0.08) / 0.04)
		elif progress < 0.75:
			alpha = 1.0
			x_offset = 0.0
		else:
			alpha = maxf(0.0, 1.0 - (progress - 0.75) / 0.25)
			x_offset = lerp(0.0, 20.0, (progress - 0.75) / 0.25)

		var data: Dictionary = row["data"]
		var icon_text := String(data.get("icon", "•"))
		var label_text := String(data.get("label", ""))
		var color: Color = data.get("color", Color(1, 0.27, 0.0, 1.0))

		var icon_w := font.get_string_size(icon_text, HORIZONTAL_ALIGNMENT_LEFT, -1.0, MEDAL_ICON_SIZE).x
		var label_w := _measure_spaced(font, label_text, MEDAL_LABEL_SIZE, MEDAL_LABEL_SPACING)
		var row_w := MEDAL_PADDING_X * 2.0 + icon_w + MEDAL_ICON_GAP + label_w
		var row_x := center_x - row_w * 0.5 + x_offset
		var bg := Color(0, 0, 0, 0.6 * alpha)
		var border := Color(color.r, color.g, color.b, 0.27 * alpha)
		var icon_color := Color(color.r, color.g, color.b, alpha)
		var label_color := Color(color.r, color.g, color.b, alpha)

		draw_rect(Rect2(row_x, y, row_w, MEDAL_ROW_HEIGHT), bg)
		draw_rect(Rect2(row_x, y, row_w, MEDAL_ROW_HEIGHT), border, false, 1.0)

		var icon_x := row_x + MEDAL_PADDING_X
		var icon_y := y + MEDAL_ROW_HEIGHT * 0.5 + MEDAL_ICON_SIZE * 0.35
		font.draw_string(get_canvas_item(), Vector2(icon_x, icon_y), icon_text,
				HORIZONTAL_ALIGNMENT_LEFT, -1.0, MEDAL_ICON_SIZE, icon_color)

		var label_x := icon_x + icon_w + MEDAL_ICON_GAP
		var label_y := y + MEDAL_ROW_HEIGHT * 0.5 + MEDAL_LABEL_SIZE * 0.35
		_draw_spaced(font, Vector2(label_x, label_y), label_text, MEDAL_LABEL_SIZE,
				MEDAL_LABEL_SPACING, label_color)

		y += MEDAL_ROW_HEIGHT + 4.0

func _draw_countdown(viewport_size: Vector2) -> void:
	if _countdown_timer < 0.0:
		return
	var progress := _countdown_timer / _countdown_duration
	# ovCountdown keyframes: 0% opacity, 10% full, 70% full, 100% faded.
	var alpha: float
	if progress < 0.10:
		alpha = progress / 0.10
	elif progress < 0.70:
		alpha = 1.0
	else:
		alpha = maxf(0.0, 1.0 - (progress - 0.70) / 0.30)

	var center := Vector2(viewport_size.x * 0.5, viewport_size.y * COUNTDOWN_Y_RATIO)
	var font := get_theme_default_font()

	# Expanding ring.
	var ring_radius: float = lerp(COUNTDOWN_RING_START_RADIUS, COUNTDOWN_RING_END_RADIUS, progress)
	var ring_alpha := maxf(0.0, COUNTDOWN_RING_COLOR.a * (1.0 - progress)) * (1.0 if alpha > 0.0 else 0.0)
	draw_arc(center, ring_radius, 0.0, TAU, 64,
			Color(COUNTDOWN_RING_COLOR.r, COUNTDOWN_RING_COLOR.g, COUNTDOWN_RING_COLOR.b, ring_alpha), 2.0)

	# Label above the number (only for numeric ticks; hidden during FIGHT).
	if not _countdown_is_fight and not _countdown_label.is_empty():
		var label_upper := _countdown_label.to_upper()
		var label_w := _measure_spaced(font, label_upper, COUNTDOWN_LABEL_SIZE, 4.0)
		var label_color := Color(COUNTDOWN_LABEL_COLOR.r, COUNTDOWN_LABEL_COLOR.g, COUNTDOWN_LABEL_COLOR.b,
				COUNTDOWN_LABEL_COLOR.a * alpha)
		_draw_spaced(font, Vector2(center.x - label_w * 0.5, center.y - 50.0),
				label_upper, COUNTDOWN_LABEL_SIZE, 4.0, label_color)

	# Number / FIGHT text.
	var number_size := COUNTDOWN_FIGHT_SIZE if _countdown_is_fight else COUNTDOWN_NUMBER_SIZE
	var number_color := COUNTDOWN_FIGHT_COLOR if _countdown_is_fight else COUNTDOWN_NUMBER_COLOR
	number_color.a = alpha
	var number_letter_spacing: float = 8.0 if _countdown_is_fight else 0.0
	var number_w := _measure_spaced(font, _countdown_number, number_size, number_letter_spacing)
	_draw_spaced(font, Vector2(center.x - number_w * 0.5, center.y + number_size * 0.35),
			_countdown_number, number_size, number_letter_spacing, number_color)

func _draw_ability_flash(viewport_size: Vector2) -> void:
	if _ability_timer < 0.0:
		return
	var progress := _ability_timer / ABILITY_FLASH_DURATION
	var alpha: float
	if progress < 0.20:
		alpha = progress / 0.20
	else:
		alpha = maxf(0.0, 1.0 - (progress - 0.20) / 0.80)

	# Edge glow: draw a thick inset border approximating the HTML's
	# `box-shadow: inset 0 0 100px color`. We fake it with a ring of four
	# rectangles at the screen edges, fading outward via a gradient strip.
	var edge_color := Color(_ability_color.r, _ability_color.g, _ability_color.b, alpha * 0.5)
	var soft_color := Color(_ability_color.r, _ability_color.g, _ability_color.b, alpha * 0.25)

	# Three bands per edge for a crude gradient.
	var bands := 3
	for i in range(bands):
		var thickness := ABILITY_EDGE_GLOW_WIDTH / float(bands)
		var falloff := 1.0 - float(i) / float(bands)
		var color := edge_color.lerp(soft_color, float(i) / float(bands))
		color.a *= falloff
		var y_top := float(i) * thickness
		var y_bot := viewport_size.y - float(i + 1) * thickness
		var x_l := float(i) * thickness
		var x_r := viewport_size.x - float(i + 1) * thickness
		# Top band
		draw_rect(Rect2(0.0, y_top, viewport_size.x, thickness), color)
		# Bottom band
		draw_rect(Rect2(0.0, y_bot, viewport_size.x, thickness), color)
		# Left band
		draw_rect(Rect2(x_l, thickness * float(i), thickness, viewport_size.y - thickness * float(i * 2)), color)
		# Right band
		draw_rect(Rect2(x_r, thickness * float(i), thickness, viewport_size.y - thickness * float(i * 2)), color)

	# Center label.
	var label_alpha := alpha
	var label_color := Color(_ability_color.r, _ability_color.g, _ability_color.b, label_alpha)
	var font := get_theme_default_font()
	var label_w := _measure_spaced(font, _ability_label, ABILITY_LABEL_SIZE, ABILITY_LABEL_SPACING)
	var label_pos := Vector2(viewport_size.x * 0.5 - label_w * 0.5, viewport_size.y * ABILITY_Y_RATIO)
	# Glow under-pass.
	var glow := Color(label_color.r, label_color.g, label_color.b, label_alpha * 0.35)
	for offset in [Vector2(-1, 0), Vector2(1, 0), Vector2(0, -1), Vector2(0, 1)]:
		_draw_spaced(font, label_pos + offset, _ability_label, ABILITY_LABEL_SIZE, ABILITY_LABEL_SPACING, glow)
	_draw_spaced(font, label_pos, _ability_label, ABILITY_LABEL_SIZE, ABILITY_LABEL_SPACING, label_color)

func _draw_respawn(viewport_size: Vector2) -> void:
	if _respawn_fade <= 0.0:
		return
	# Black backdrop.
	draw_rect(Rect2(Vector2.ZERO, viewport_size), Color(0, 0, 0, 0.6 * _respawn_fade))

	var font := get_theme_default_font()
	var center_x := viewport_size.x * 0.5
	var center_y := viewport_size.y * 0.5

	# "DESTROYED" title.
	var title := "DESTROYED"
	var title_color := Color(RESPAWN_TITLE_COLOR.r, RESPAWN_TITLE_COLOR.g, RESPAWN_TITLE_COLOR.b, _respawn_fade)
	var title_w := _measure_spaced(font, title, RESPAWN_TITLE_SIZE, 6.0)
	_draw_spaced(font, Vector2(center_x - title_w * 0.5, center_y - 30.0),
			title, RESPAWN_TITLE_SIZE, 6.0, title_color)

	# Optional killer line.
	if not _respawn_killer.is_empty():
		var prefix := "KILLED BY "
		var prefix_color := Color(RESPAWN_KILLER_COLOR.r, RESPAWN_KILLER_COLOR.g, RESPAWN_KILLER_COLOR.b, _respawn_fade)
		var killer_color := Color(RESPAWN_KILLER_NAME_COLOR.r, RESPAWN_KILLER_NAME_COLOR.g,
				RESPAWN_KILLER_NAME_COLOR.b, _respawn_fade)
		var prefix_w := font.get_string_size(prefix, HORIZONTAL_ALIGNMENT_LEFT, -1.0, RESPAWN_KILLER_SIZE).x
		var killer_w := font.get_string_size(_respawn_killer, HORIZONTAL_ALIGNMENT_LEFT, -1.0, RESPAWN_KILLER_SIZE).x
		var total_w := prefix_w + killer_w
		var line_x := center_x - total_w * 0.5
		var line_y := center_y + 12.0
		font.draw_string(get_canvas_item(), Vector2(line_x, line_y), prefix,
				HORIZONTAL_ALIGNMENT_LEFT, -1.0, RESPAWN_KILLER_SIZE, prefix_color)
		font.draw_string(get_canvas_item(), Vector2(line_x + prefix_w, line_y), _respawn_killer,
				HORIZONTAL_ALIGNMENT_LEFT, -1.0, RESPAWN_KILLER_SIZE, killer_color)

	# Waiting message.
	var wait_text := "WAITING FOR NEXT ROUND"
	var wait_color := Color(RESPAWN_WAIT_COLOR.r, RESPAWN_WAIT_COLOR.g, RESPAWN_WAIT_COLOR.b,
			RESPAWN_WAIT_COLOR.a * _respawn_fade)
	var wait_w := _measure_spaced(font, wait_text, RESPAWN_WAIT_SIZE, 4.0)
	_draw_spaced(font, Vector2(center_x - wait_w * 0.5, center_y + 44.0),
			wait_text, RESPAWN_WAIT_SIZE, 4.0, wait_color)

func _draw_execution_prompt(viewport_size: Vector2) -> void:
	if not _exec_prompt_visible:
		return
	var font := get_theme_default_font()
	var prompt_w := _measure_spaced(font, EXEC_PROMPT_TEXT, EXEC_PROMPT_SIZE, EXEC_PROMPT_SPACING)
	var pos := Vector2(viewport_size.x * 0.5 - prompt_w * 0.5,
			viewport_size.y * EXEC_PROMPT_Y_RATIO)
	# Subtle glow.
	var glow := Color(EXEC_PROMPT_COLOR.r, EXEC_PROMPT_COLOR.g, EXEC_PROMPT_COLOR.b, 0.4)
	for offset in [Vector2(-1, 0), Vector2(1, 0), Vector2(0, -1), Vector2(0, 1)]:
		_draw_spaced(font, pos + offset, EXEC_PROMPT_TEXT, EXEC_PROMPT_SIZE, EXEC_PROMPT_SPACING, glow)
	_draw_spaced(font, pos, EXEC_PROMPT_TEXT, EXEC_PROMPT_SIZE, EXEC_PROMPT_SPACING, EXEC_PROMPT_COLOR)

# ---------------------------------------------------------------------------
# Text helpers (kept local so this script has no sibling-class dependencies).

func _measure_spaced(font: Font, text: String, font_size: int, spacing: float) -> float:
	if text.is_empty():
		return 0.0
	var total := 0.0
	for ch in text:
		total += font.get_string_size(ch, HORIZONTAL_ALIGNMENT_LEFT, -1.0, font_size).x + spacing
	return maxf(0.0, total - spacing)

func _draw_spaced(font: Font, pos: Vector2, text: String, font_size: int, spacing: float, color: Color) -> void:
	var cursor_x := pos.x
	for ch in text:
		font.draw_string(get_canvas_item(), Vector2(cursor_x, pos.y), ch,
				HORIZONTAL_ALIGNMENT_LEFT, -1.0, font_size, color)
		cursor_x += font.get_string_size(ch, HORIZONTAL_ALIGNMENT_LEFT, -1.0, font_size).x + spacing
