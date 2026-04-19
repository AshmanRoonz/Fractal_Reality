class_name BannerOverlay
extends Control

# Round transition banner. Ported from last_ship_sailing.html #ov-banner
# (lines 466-493, 606-611, 10255-10266). The HTML animation is 3 seconds:
# 0-10% fade-in, 10-80% hold, 80-100% fade-out; the two horizontal lines
# expand from 0 to 300px over the first 10% and then hold.

const TOTAL_DURATION := 3.0
const LINE_GROW_FRACTION := 0.10   # Fraction of total where lines finish expanding
const FADE_IN_FRACTION := 0.10
const FADE_OUT_FRACTION := 0.20    # Fade covers the last 20%
const LINE_MAX_WIDTH := 300.0
const LINE_HEIGHT := 1.0
const TEXT_SIZE := 28
const SUBTEXT_SIZE := 12
const TEXT_COLOR := Color(1.0, 0.667, 0.0, 1.0)          # #ffaa00
const SUBTEXT_COLOR := Color(0.533, 0.533, 0.533, 1.0)   # #888
const GLOW_COLOR := Color(1.0, 0.667, 0.0, 0.25)
const LETTER_SPACING_TEXT := 8.0
const LETTER_SPACING_SUBTEXT := 3.0
const LINE_TEXT_GAP := 12.0

var _text: String = ""
var _subtext: String = ""
var _timer: float = -1.0   # Negative = idle (nothing to draw)

func _ready() -> void:
	mouse_filter = MOUSE_FILTER_IGNORE
	focus_mode = FOCUS_NONE
	set_anchors_preset(PRESET_FULL_RECT)

func show_banner(text: String, subtext: String = "") -> void:
	_text = text
	_subtext = subtext
	_timer = 0.0
	queue_redraw()

func _process(delta: float) -> void:
	if _timer < 0.0:
		return
	_timer += delta
	if _timer >= TOTAL_DURATION:
		_timer = -1.0
	queue_redraw()

func _draw() -> void:
	if _timer < 0.0:
		return
	var progress := clampf(_timer / TOTAL_DURATION, 0.0, 1.0)
	var alpha: float
	if progress < FADE_IN_FRACTION:
		alpha = progress / FADE_IN_FRACTION
	elif progress > 1.0 - FADE_OUT_FRACTION:
		alpha = maxf(0.0, (1.0 - progress) / FADE_OUT_FRACTION)
	else:
		alpha = 1.0

	# Line width expands for the first 10% then holds
	var line_width := LINE_MAX_WIDTH * clampf(progress / LINE_GROW_FRACTION, 0.0, 1.0)

	var viewport_size := get_viewport_rect().size
	var center_x := viewport_size.x * 0.5
	# HTML anchors at top:38% translate(-50%,-50%), so the banner's centre sits at ~38% of height
	var center_y := viewport_size.y * 0.38

	var font := get_theme_default_font()
	var main_font_size := TEXT_SIZE
	var sub_font_size := SUBTEXT_SIZE

	# Measure text with letter spacing so the lines/subtitle centre properly
	var text_upper := _text.to_upper()
	var main_width := _measure_spaced(font, text_upper, main_font_size, LETTER_SPACING_TEXT)
	var main_height := float(main_font_size)

	# Layout: top line (gap) main text (gap) sub text (gap) bot line
	var sub_height := 0.0
	var has_sub := not _subtext.is_empty()
	if has_sub:
		sub_height = float(sub_font_size)

	var top_line_y := center_y - main_height * 0.5 - LINE_TEXT_GAP
	var bot_line_y := center_y + main_height * 0.5 + (6.0 + sub_height + 6.0 if has_sub else LINE_TEXT_GAP)

	# Draw top + bottom horizontal lines with gradient-style fall-off via two halves
	_draw_gradient_line(Vector2(center_x - line_width * 0.5, top_line_y), line_width, alpha)
	_draw_gradient_line(Vector2(center_x - line_width * 0.5, bot_line_y), line_width, alpha)

	# Main text with subtle glow (simulates HTML text-shadow 0 0 20px rgba(255,170,0,0.4))
	var main_baseline_y := center_y + main_height * 0.35
	var glow_color := Color(GLOW_COLOR.r, GLOW_COLOR.g, GLOW_COLOR.b, GLOW_COLOR.a * alpha)
	var main_color := Color(TEXT_COLOR.r, TEXT_COLOR.g, TEXT_COLOR.b, TEXT_COLOR.a * alpha)

	var main_x_start := center_x - main_width * 0.5
	for offset in [Vector2(-2, 0), Vector2(2, 0), Vector2(0, -2), Vector2(0, 2)]:
		_draw_spaced(font, Vector2(main_x_start, main_baseline_y) + offset, text_upper, main_font_size, LETTER_SPACING_TEXT, glow_color)
	_draw_spaced(font, Vector2(main_x_start, main_baseline_y), text_upper, main_font_size, LETTER_SPACING_TEXT, main_color)

	if has_sub:
		var sub_upper := _subtext.to_upper()
		var sub_width := _measure_spaced(font, sub_upper, sub_font_size, LETTER_SPACING_SUBTEXT)
		var sub_color := Color(SUBTEXT_COLOR.r, SUBTEXT_COLOR.g, SUBTEXT_COLOR.b, SUBTEXT_COLOR.a * alpha)
		var sub_baseline := center_y + main_height * 0.5 + 6.0 + float(sub_font_size)
		_draw_spaced(font, Vector2(center_x - sub_width * 0.5, sub_baseline), sub_upper, sub_font_size, LETTER_SPACING_SUBTEXT, sub_color)

func _draw_gradient_line(start: Vector2, total_width: float, alpha: float) -> void:
	# Approximates the HTML linear-gradient(90deg, transparent, #ffaa00, transparent)
	# via three stacked rectangles of decreasing alpha from the edges inward.
	if total_width <= 0.0:
		return
	var segments := 12
	var seg_w := total_width / float(segments)
	for i in range(segments):
		var normalized := (float(i) + 0.5) / float(segments)
		# Triangle envelope: 0 at edges, 1 at centre
		var envelope := 1.0 - absf(normalized - 0.5) * 2.0
		var segment_color := Color(TEXT_COLOR.r, TEXT_COLOR.g, TEXT_COLOR.b, TEXT_COLOR.a * alpha * envelope)
		draw_rect(Rect2(start.x + float(i) * seg_w, start.y, seg_w + 1.0, LINE_HEIGHT), segment_color)

func _measure_spaced(font: Font, text: String, font_size: int, spacing: float) -> float:
	if text.is_empty():
		return 0.0
	var total := 0.0
	for ch in text:
		total += font.get_string_size(ch, HORIZONTAL_ALIGNMENT_LEFT, -1.0, font_size).x + spacing
	# Trailing spacing not part of the visible glyph run
	return maxf(0.0, total - spacing)

func _draw_spaced(font: Font, pos: Vector2, text: String, font_size: int, spacing: float, color: Color) -> void:
	var cursor_x := pos.x
	for ch in text:
		font.draw_string(get_canvas_item(), Vector2(cursor_x, pos.y), ch, HORIZONTAL_ALIGNMENT_LEFT, -1.0, font_size, color)
		cursor_x += font.get_string_size(ch, HORIZONTAL_ALIGNMENT_LEFT, -1.0, font_size).x + spacing
