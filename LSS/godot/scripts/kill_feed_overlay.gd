class_name KillFeedOverlay
extends Control

# Rolling kill feed, ported from last_ship_sailing.html (lines 105-110,
# 548, 8899-8913, 10583-10586). Each entry shows "<killer> destroyed
# <victim>" in the top-right; keep at most 5 entries, expire at 8 seconds,
# with a short fade-out over the final 0.5 s (matches the HTML CSS
# transition: opacity 0.5s).

const MAX_ENTRIES := 5
const ENTRY_LIFETIME := 8.0
const ENTRY_FADE := 0.5
const ENTRY_SIZE := 11
const ENTRY_LINE_HEIGHT := 16.0
const PADDING_RIGHT := 20.0
const PADDING_TOP := 60.0
const KILLER_COLOR := Color(1.0, 0.4, 0.4, 1.0)          # #ff6666
const VICTIM_COLOR := Color(0.4, 0.733, 0.4, 1.0)        # #66bb66
const TEXT_COLOR := Color(1.0, 1.0, 1.0, 1.0)

var _entries: Array = []   # [{killer: String, victim: String, age: float}]

func _ready() -> void:
	mouse_filter = MOUSE_FILTER_IGNORE
	focus_mode = FOCUS_NONE
	set_anchors_preset(PRESET_FULL_RECT)

func add_entry(killer: String, victim: String) -> void:
	_entries.push_front({"killer": killer, "victim": victim, "age": 0.0})
	while _entries.size() > MAX_ENTRIES:
		_entries.pop_back()
	queue_redraw()

func _process(delta: float) -> void:
	if _entries.is_empty():
		return
	var dirty := false
	for i in range(_entries.size() - 1, -1, -1):
		_entries[i]["age"] = float(_entries[i]["age"]) + delta
		if _entries[i]["age"] >= ENTRY_LIFETIME:
			_entries.remove_at(i)
			dirty = true
	if dirty or not _entries.is_empty():
		queue_redraw()

func _draw() -> void:
	if _entries.is_empty():
		return
	var font := get_theme_default_font()
	var viewport_size := get_viewport_rect().size
	var right_edge := viewport_size.x - PADDING_RIGHT
	var y := PADDING_TOP

	for entry in _entries:
		var age := float(entry["age"])
		var alpha := 1.0
		if age > ENTRY_LIFETIME - ENTRY_FADE:
			alpha = maxf(0.0, (ENTRY_LIFETIME - age) / ENTRY_FADE)
		var killer := String(entry["killer"])
		var victim := String(entry["victim"])
		var mid := " destroyed "
		var killer_w := font.get_string_size(killer, HORIZONTAL_ALIGNMENT_LEFT, -1.0, ENTRY_SIZE).x
		var mid_w := font.get_string_size(mid, HORIZONTAL_ALIGNMENT_LEFT, -1.0, ENTRY_SIZE).x
		var victim_w := font.get_string_size(victim, HORIZONTAL_ALIGNMENT_LEFT, -1.0, ENTRY_SIZE).x
		var total_w := killer_w + mid_w + victim_w
		var x := right_edge - total_w
		var baseline := y + float(ENTRY_SIZE)

		font.draw_string(get_canvas_item(), Vector2(x, baseline), killer, HORIZONTAL_ALIGNMENT_LEFT, -1.0, ENTRY_SIZE, Color(KILLER_COLOR.r, KILLER_COLOR.g, KILLER_COLOR.b, alpha))
		font.draw_string(get_canvas_item(), Vector2(x + killer_w, baseline), mid, HORIZONTAL_ALIGNMENT_LEFT, -1.0, ENTRY_SIZE, Color(TEXT_COLOR.r, TEXT_COLOR.g, TEXT_COLOR.b, alpha))
		font.draw_string(get_canvas_item(), Vector2(x + killer_w + mid_w, baseline), victim, HORIZONTAL_ALIGNMENT_LEFT, -1.0, ENTRY_SIZE, Color(VICTIM_COLOR.r, VICTIM_COLOR.g, VICTIM_COLOR.b, alpha))
		y += ENTRY_LINE_HEIGHT
