class_name ScoreboardOverlay
extends Control

# Godot port of the HTML #scoreboard overlay (last_ship_sailing.html lines
# 11228-11307). Shown while the player holds Tab / gamepad Back; auto-shown
# when the match ends so the final standings stay visible under the VICTORY
# banner. Layout mirrors the HTML:
#
#   SCOREBOARD
#   SHIP           STATUS   HEALTH   SHIELD
#   FLEET A (3 rounds)
#     YOU (ION)    ALIVE     7350      2460
#     SCORCH       DEAD         0         0
#   FLEET B (1 rounds)
#     RONIN        DOOMED    1100         0
#     TONE         ALIVE     8200      4100
#   K: 4 / D: 1 / DMG: 18432
#
# Rebuilds labels on each update_rows() call (small list, low frequency).

const ACCENT_COLOR := Color(1.0, 0.667, 0.0, 1.0)        # #ffaa00
const TEAM_A_COLOR := Color(1.0, 0.4, 0.4, 1.0)          # #ff6666
const TEAM_B_COLOR := Color(0.4, 0.733, 0.4, 1.0)        # #66bb66
const HEADER_DIM := Color(0.4, 0.4, 0.4, 1.0)            # #666
const STAT_COLOR := Color(0.667, 0.667, 0.667, 1.0)      # #aaa
const PLAYER_ROW_COLOR := Color(1.0, 0.8, 0.0, 1.0)      # #ffcc00
const ROW_COLOR := Color(1.0, 1.0, 1.0, 1.0)
const PANEL_BG := Color(0.020, 0.031, 0.071, 0.92)       # rgba(5,8,18,0.92)
const PANEL_BORDER := Color(0.392, 0.706, 1.0, 0.2)      # rgba(100,180,255,0.2)
const PROMPT_COLOR := Color(0.4, 0.9, 0.4, 1.0)
const SUBTLE_COLOR := Color(0.333, 0.333, 0.333, 1.0)    # #555

const PANEL_WIDTH := 600.0
const ROW_HEIGHT := 18.0
const PADDING := 20.0

var _panel: PanelContainer
var _rows_vbox: VBoxContainer
var _title_label: Label
var _footer_label: Label
var _prompt_label: Label

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	anchor_right = 1.0
	anchor_bottom = 1.0
	visible = false

	_panel = PanelContainer.new()
	_panel.custom_minimum_size = Vector2(PANEL_WIDTH, 0)
	_panel.anchor_left = 0.5
	_panel.anchor_right = 0.5
	_panel.anchor_top = 0.5
	_panel.anchor_bottom = 0.5
	_panel.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_panel.grow_vertical = Control.GROW_DIRECTION_BOTH
	_panel.offset_left = -PANEL_WIDTH * 0.5
	_panel.offset_right = PANEL_WIDTH * 0.5
	_panel.offset_top = -240.0
	_panel.offset_bottom = 240.0

	var style := StyleBoxFlat.new()
	style.bg_color = PANEL_BG
	style.border_color = PANEL_BORDER
	style.set_border_width_all(1)
	style.content_margin_left = PADDING
	style.content_margin_right = PADDING
	style.content_margin_top = PADDING
	style.content_margin_bottom = PADDING
	_panel.add_theme_stylebox_override("panel", style)
	add_child(_panel)

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 4)
	_panel.add_child(vbox)

	_title_label = _make_label("SCOREBOARD", 16, ACCENT_COLOR)
	_title_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_title_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	vbox.add_child(_title_label)

	var header := HBoxContainer.new()
	header.add_theme_constant_override("separation", 0)
	vbox.add_child(header)
	_add_header_cell(header, "SHIP", 2.0, HORIZONTAL_ALIGNMENT_LEFT)
	_add_header_cell(header, "STATUS", 1.0, HORIZONTAL_ALIGNMENT_CENTER)
	_add_header_cell(header, "HEALTH", 1.0, HORIZONTAL_ALIGNMENT_CENTER)
	_add_header_cell(header, "SHIELD", 1.0, HORIZONTAL_ALIGNMENT_CENTER)

	_rows_vbox = VBoxContainer.new()
	_rows_vbox.add_theme_constant_override("separation", 2)
	_rows_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	vbox.add_child(_rows_vbox)

	_footer_label = _make_label("", 10, SUBTLE_COLOR)
	_footer_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_footer_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	vbox.add_child(_footer_label)

	_prompt_label = _make_label("", 11, PROMPT_COLOR)
	_prompt_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_prompt_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_prompt_label.visible = false
	vbox.add_child(_prompt_label)

func _add_header_cell(parent: HBoxContainer, text: String, flex: float, alignment: int) -> void:
	var cell := _make_label(text, 9, HEADER_DIM)
	cell.horizontal_alignment = alignment
	cell.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	cell.size_flags_stretch_ratio = flex
	parent.add_child(cell)

# Public API -------------------------------------------------------------

# rows: Array of Dictionary entries. Each entry:
#   { "name": String, "status": String, "health": int, "shield": int,
#     "team": int (0=A, 1=B), "is_player": bool }
# match_info: Dictionary with { "score_a": int, "score_b": int,
#   "kills": int, "deaths": int, "damage": int }
# prompt: String (empty hides the prompt row)
func update_rows(rows: Array, match_info: Dictionary, prompt: String = "") -> void:
	# Clear existing rows without leaking nodes.
	for child in _rows_vbox.get_children():
		child.queue_free()

	var team_a: Array = []
	var team_b: Array = []
	for row in rows:
		if int(row.get("team", 0)) == 0:
			team_a.append(row)
		else:
			team_b.append(row)

	_rows_vbox.add_child(_make_team_header("FLEET A (%d rounds)" % int(match_info.get("score_a", 0)), TEAM_A_COLOR))
	for row in team_a:
		_rows_vbox.add_child(_make_ship_row(row))

	_rows_vbox.add_child(_make_team_header("FLEET B (%d rounds)" % int(match_info.get("score_b", 0)), TEAM_B_COLOR))
	for row in team_b:
		_rows_vbox.add_child(_make_ship_row(row))

	_footer_label.text = "K: %d / D: %d / DMG: %d" % [
		int(match_info.get("kills", 0)),
		int(match_info.get("deaths", 0)),
		int(match_info.get("damage", 0)),
	]

	if prompt.is_empty():
		_prompt_label.visible = false
	else:
		_prompt_label.text = prompt
		_prompt_label.visible = true

func _make_team_header(text: String, color: Color) -> Control:
	var row := Control.new()
	row.custom_minimum_size = Vector2(0, ROW_HEIGHT + 4)

	var bg := ColorRect.new()
	bg.color = Color(color.r, color.g, color.b, 0.08)
	bg.anchor_right = 1.0
	bg.anchor_bottom = 1.0
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(bg)

	var label := _make_label(text, 12, color)
	label.anchor_left = 0.0
	label.anchor_right = 1.0
	label.anchor_top = 0.0
	label.anchor_bottom = 1.0
	label.offset_left = 8.0
	label.offset_right = -8.0
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(label)
	return row

func _make_ship_row(data: Dictionary) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 0)

	var color := PLAYER_ROW_COLOR if bool(data.get("is_player", false)) else ROW_COLOR

	var name_label := _make_label(String(data.get("name", "?")), 11, color)
	name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	name_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	name_label.size_flags_stretch_ratio = 2.0
	row.add_child(name_label)

	var status_label := _make_label(String(data.get("status", "?")), 11, color)
	status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	status_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	status_label.size_flags_stretch_ratio = 1.0
	row.add_child(status_label)

	var health_text := "%d" % int(ceil(float(data.get("health", 0))))
	var health_label := _make_label(health_text, 11, STAT_COLOR if not bool(data.get("is_player", false)) else color)
	health_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	health_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	health_label.size_flags_stretch_ratio = 1.0
	row.add_child(health_label)

	var shield_text := "%d" % int(ceil(float(data.get("shield", 0))))
	var shield_label := _make_label(shield_text, 11, STAT_COLOR if not bool(data.get("is_player", false)) else color)
	shield_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	shield_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	shield_label.size_flags_stretch_ratio = 1.0
	row.add_child(shield_label)

	return row

func _make_label(text: String, font_size: int, color: Color) -> Label:
	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	return label

func show_board() -> void:
	visible = true

func hide_board() -> void:
	visible = false
