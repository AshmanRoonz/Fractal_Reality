class_name SettingsOverlay
extends CanvasLayer

# ---------------------------------------------------------------------------
# Settings overlay
# Mirrors buildSettingsPage() at line 9141 of last_ship_sailing.html.
# Opened by MainMenu or by main.gd on ESC during gameplay. When this layer is
# mounted the game pauses (process_mode = WHEN_PAUSED) so gameplay freezes
# but the overlay remains interactive.
# ---------------------------------------------------------------------------

const Settings = preload("res://scripts/settings.gd")

signal closed

const BG_COLOR := Color(0.02, 0.02, 0.06, 0.95)
const ACCENT_COLOR := Color(1.0, 0.6667, 0.0, 1.0)      # #ffaa00
const SUBTITLE_COLOR := Color(0.533, 0.533, 0.533, 1.0) # #888
const LABEL_COLOR := Color(0.8, 0.8, 0.8, 1.0)
const ROW_SEP_COLOR := Color(0.23, 0.23, 0.31, 0.3)
const CARD_BORDER := Color(0.39, 0.39, 0.47, 0.5)

var _previous_pause_state: bool = false
var _was_mouse_captured: bool = false

var _root: Control
var _content_vbox: VBoxContainer
var _reopen_after_rebuild: bool = false

# Slider refs, keyed by setting name, for the reset pass.
var _sliders: Dictionary = {}
var _value_labels: Dictionary = {}
var _checkboxes: Dictionary = {}
var _bind_buttons: Dictionary = {}  # action -> OptionButton

func _ready() -> void:
	layer = 100
	process_mode = Node.PROCESS_MODE_WHEN_PAUSED

	_was_mouse_captured = Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)

	_previous_pause_state = get_tree().paused
	get_tree().paused = true

	_root = Control.new()
	_root.anchor_right = 1.0
	_root.anchor_bottom = 1.0
	_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(_root)

	# Opaque background panel.
	var bg := ColorRect.new()
	bg.color = BG_COLOR
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.mouse_filter = Control.MOUSE_FILTER_STOP
	_root.add_child(bg)

	# Scroll container for long content.
	var scroll := ScrollContainer.new()
	scroll.set_anchors_preset(Control.PRESET_FULL_RECT)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	_root.add_child(scroll)

	var outer_margin := MarginContainer.new()
	outer_margin.add_theme_constant_override("margin_top", 30)
	outer_margin.add_theme_constant_override("margin_bottom", 40)
	outer_margin.add_theme_constant_override("margin_left", 20)
	outer_margin.add_theme_constant_override("margin_right", 20)
	outer_margin.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(outer_margin)

	var center := CenterContainer.new()
	center.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	outer_margin.add_child(center)

	_content_vbox = VBoxContainer.new()
	_content_vbox.custom_minimum_size = Vector2(700, 0)
	_content_vbox.add_theme_constant_override("separation", 18)
	center.add_child(_content_vbox)

	_build_content()

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.physical_keycode == KEY_ESCAPE:
			_close()
			get_viewport().set_input_as_handled()
	elif event is InputEventJoypadButton and event.pressed:
		if event.button_index == JOY_BUTTON_B or event.button_index == JOY_BUTTON_BACK:
			_close()
			get_viewport().set_input_as_handled()

# ---------------------------------------------------------------------------
# Content construction
# ---------------------------------------------------------------------------
func _build_content() -> void:
	# Clear (used by Reset to re-render with default values).
	for child in _content_vbox.get_children():
		child.queue_free()
	_sliders.clear()
	_value_labels.clear()
	_checkboxes.clear()
	_bind_buttons.clear()

	# Title row.
	var title := Label.new()
	title.text = "SETTINGS"
	title.add_theme_color_override("font_color", ACCENT_COLOR)
	title.add_theme_font_size_override("font_size", 28)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_content_vbox.add_child(title)

	var subtitle := Label.new()
	subtitle.text = "CONTROLS & INPUT"
	subtitle.add_theme_color_override("font_color", SUBTITLE_COLOR)
	subtitle.add_theme_font_size_override("font_size", 13)
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_content_vbox.add_child(subtitle)

	# Sections.
	_add_section("MOUSE", [
		["mouse_sensitivity", "Mouse Sensitivity", 0.0005, 0.01, 0.0005, 4, Settings.mouse_sensitivity],
	])

	_add_section("GAMEPAD - SENSITIVITY", [
		["gp_look_sensitivity", "Look Sensitivity", 1.0, 15.0, 0.5, 1, Settings.gp_look_sensitivity],
		["gp_move_sensitivity", "Move Sensitivity", 1.0, 15.0, 0.5, 1, Settings.gp_move_sensitivity],
		["gp_look_curve", "Look Response Curve", 1.0, 3.0, 0.1, 1, Settings.gp_look_curve],
		["gp_move_curve", "Move Response Curve", 1.0, 3.0, 0.1, 1, Settings.gp_move_curve],
	])

	_add_section("GAMEPAD - DEADZONE", [
		["gp_deadzone", "Stick Deadzone", 0.0, 0.5, 0.01, 2, Settings.gp_deadzone],
		["trigger_threshold", "Trigger Threshold", 0.05, 0.9, 0.05, 2, Settings.trigger_threshold],
	])

	_add_toggle_section("GAMEPAD - OPTIONS", [
		["invert_look_y", "Invert Look Y", Settings.invert_look_y],
		["swap_sticks", "Swap Sticks (Southpaw)", Settings.swap_sticks],
	])

	_add_bindings_section()

	# Buttons row.
	var button_row := VBoxContainer.new()
	button_row.alignment = BoxContainer.ALIGNMENT_CENTER
	button_row.add_theme_constant_override("separation", 8)
	_content_vbox.add_child(button_row)

	var close_btn := Button.new()
	close_btn.text = "CLOSE"
	close_btn.custom_minimum_size = Vector2(240, 44)
	_style_accent_button(close_btn)
	close_btn.pressed.connect(_close)
	var close_center := CenterContainer.new()
	close_center.add_child(close_btn)
	button_row.add_child(close_center)

	var reset_btn := Button.new()
	reset_btn.text = "RESET TO DEFAULTS"
	reset_btn.custom_minimum_size = Vector2(240, 32)
	_style_reset_button(reset_btn)
	reset_btn.pressed.connect(_on_reset_pressed)
	var reset_center := CenterContainer.new()
	reset_center.add_child(reset_btn)
	button_row.add_child(reset_center)

func _add_section(title_text: String, rows: Array) -> void:
	var section := VBoxContainer.new()
	section.add_theme_constant_override("separation", 6)
	_content_vbox.add_child(section)

	var header := Label.new()
	header.text = title_text
	header.add_theme_color_override("font_color", ACCENT_COLOR)
	header.add_theme_font_size_override("font_size", 14)
	section.add_child(header)

	var rule := ColorRect.new()
	rule.color = Color(ACCENT_COLOR, 0.3)
	rule.custom_minimum_size = Vector2(0, 1)
	section.add_child(rule)

	for row_spec in rows:
		var key: String = row_spec[0]
		var label_text: String = row_spec[1]
		var min_v: float = row_spec[2]
		var max_v: float = row_spec[3]
		var step_v: float = row_spec[4]
		var decimals: int = row_spec[5]
		var current: float = row_spec[6]
		section.add_child(_build_slider_row(key, label_text, min_v, max_v, step_v, decimals, current))

func _add_toggle_section(title_text: String, rows: Array) -> void:
	var section := VBoxContainer.new()
	section.add_theme_constant_override("separation", 6)
	_content_vbox.add_child(section)

	var header := Label.new()
	header.text = title_text
	header.add_theme_color_override("font_color", ACCENT_COLOR)
	header.add_theme_font_size_override("font_size", 14)
	section.add_child(header)

	var rule := ColorRect.new()
	rule.color = Color(ACCENT_COLOR, 0.3)
	rule.custom_minimum_size = Vector2(0, 1)
	section.add_child(rule)

	for row_spec in rows:
		var key: String = row_spec[0]
		var label_text: String = row_spec[1]
		var current: bool = row_spec[2]
		section.add_child(_build_toggle_row(key, label_text, current))

func _add_bindings_section() -> void:
	var section := VBoxContainer.new()
	section.add_theme_constant_override("separation", 6)
	_content_vbox.add_child(section)

	var header := Label.new()
	header.text = "GAMEPAD - BUTTON MAPPING"
	header.add_theme_color_override("font_color", ACCENT_COLOR)
	header.add_theme_font_size_override("font_size", 14)
	section.add_child(header)

	var rule := ColorRect.new()
	rule.color = Color(ACCENT_COLOR, 0.3)
	rule.custom_minimum_size = Vector2(0, 1)
	section.add_child(rule)

	# Build a row per action in a predictable order.
	var action_order: Array = [
		"fire_primary", "dash", "reload",
		"ability_1", "ability_2", "ability_3",
		"core_ability", "move_up", "move_down",
		"next_loadout", "prev_loadout"
	]
	for action in action_order:
		if not Settings.gp_bindings.has(action):
			continue
		var label_text: String = String(Settings.ACTION_LABELS.get(action, action))
		var current_btn: int = int(Settings.gp_bindings[action])
		section.add_child(_build_bind_row(action, label_text, current_btn))

# ---------------------------------------------------------------------------
# Row builders
# ---------------------------------------------------------------------------
func _build_slider_row(key: String, label_text: String, min_v: float, max_v: float, step_v: float, decimals: int, current: float) -> Control:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 12)
	row.custom_minimum_size = Vector2(0, 26)

	var label := Label.new()
	label.text = label_text
	label.add_theme_color_override("font_color", LABEL_COLOR)
	label.add_theme_font_size_override("font_size", 12)
	label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(label)

	var slider := HSlider.new()
	slider.min_value = min_v
	slider.max_value = max_v
	slider.step = step_v
	slider.value = current
	slider.custom_minimum_size = Vector2(220, 20)
	row.add_child(slider)

	var value_label := Label.new()
	value_label.text = "%.*f" % [decimals, current]
	value_label.add_theme_color_override("font_color", ACCENT_COLOR)
	value_label.add_theme_font_size_override("font_size", 11)
	value_label.custom_minimum_size = Vector2(60, 0)
	value_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	row.add_child(value_label)

	_sliders[key] = slider
	_value_labels[key] = value_label

	slider.value_changed.connect(func(v: float) -> void:
		_apply_slider_value(key, v)
		value_label.text = "%.*f" % [decimals, v]
		Settings.save_to_disk()
	)
	return row

func _build_toggle_row(key: String, label_text: String, current: bool) -> Control:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 12)
	row.custom_minimum_size = Vector2(0, 26)

	var label := Label.new()
	label.text = label_text
	label.add_theme_color_override("font_color", LABEL_COLOR)
	label.add_theme_font_size_override("font_size", 12)
	label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(label)

	var checkbox := CheckBox.new()
	checkbox.button_pressed = current
	row.add_child(checkbox)

	_checkboxes[key] = checkbox

	checkbox.toggled.connect(func(pressed: bool) -> void:
		_apply_toggle_value(key, pressed)
		Settings.save_to_disk()
	)
	return row

func _build_bind_row(action: String, label_text: String, current_btn: int) -> Control:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 12)
	row.custom_minimum_size = Vector2(0, 26)

	var label := Label.new()
	label.text = label_text
	label.add_theme_color_override("font_color", LABEL_COLOR)
	label.add_theme_font_size_override("font_size", 12)
	label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(label)

	var option := OptionButton.new()
	option.custom_minimum_size = Vector2(140, 0)
	var selected_idx := 0
	var i := 0
	for btn_idx in Settings.BUTTON_ORDER:
		var name_str: String = String(Settings.BUTTON_NAMES.get(btn_idx, "Btn %d" % btn_idx))
		option.add_item(name_str, btn_idx)
		if btn_idx == current_btn:
			selected_idx = i
		i += 1
	option.select(selected_idx)
	row.add_child(option)

	_bind_buttons[action] = option

	option.item_selected.connect(func(index: int) -> void:
		var button_id := option.get_item_id(index)
		Settings.gp_bindings[action] = button_id
		Settings.apply_to_input_map()
		Settings.save_to_disk()
	)
	return row

# ---------------------------------------------------------------------------
# Value application
# ---------------------------------------------------------------------------
func _apply_slider_value(key: String, value: float) -> void:
	match key:
		"mouse_sensitivity":
			Settings.mouse_sensitivity = value
		"gp_look_sensitivity":
			Settings.gp_look_sensitivity = value
		"gp_move_sensitivity":
			Settings.gp_move_sensitivity = value
		"gp_look_curve":
			Settings.gp_look_curve = value
		"gp_move_curve":
			Settings.gp_move_curve = value
		"gp_deadzone":
			Settings.gp_deadzone = value
			Settings.apply_to_input_map()
		"trigger_threshold":
			Settings.trigger_threshold = value
			Settings.apply_to_input_map()

func _apply_toggle_value(key: String, value: bool) -> void:
	match key:
		"invert_look_y":
			Settings.invert_look_y = value
		"swap_sticks":
			Settings.swap_sticks = value

# ---------------------------------------------------------------------------
# Reset / close
# ---------------------------------------------------------------------------
func _on_reset_pressed() -> void:
	Settings.reset_to_defaults()
	_build_content()

func _close() -> void:
	get_tree().paused = _previous_pause_state
	if _was_mouse_captured:
		Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
	closed.emit()
	queue_free()

# ---------------------------------------------------------------------------
# Styling helpers
# ---------------------------------------------------------------------------
func _style_accent_button(btn: Button) -> void:
	btn.add_theme_color_override("font_color", ACCENT_COLOR)
	btn.add_theme_color_override("font_hover_color", Color(1, 0.9, 0.4))
	btn.add_theme_color_override("font_focus_color", ACCENT_COLOR)
	btn.add_theme_font_size_override("font_size", 14)
	var normal := StyleBoxFlat.new()
	normal.bg_color = Color(ACCENT_COLOR, 0.15)
	normal.border_width_left = 1
	normal.border_width_top = 1
	normal.border_width_right = 1
	normal.border_width_bottom = 1
	normal.border_color = ACCENT_COLOR
	var hover := normal.duplicate() as StyleBoxFlat
	hover.bg_color = Color(ACCENT_COLOR, 0.3)
	var pressed := normal.duplicate() as StyleBoxFlat
	pressed.bg_color = Color(ACCENT_COLOR, 0.45)
	btn.add_theme_stylebox_override("normal", normal)
	btn.add_theme_stylebox_override("hover", hover)
	btn.add_theme_stylebox_override("pressed", pressed)
	btn.add_theme_stylebox_override("focus", hover)

func _style_reset_button(btn: Button) -> void:
	var danger := Color(1.0, 0.4, 0.4, 1.0)
	btn.add_theme_color_override("font_color", danger)
	btn.add_theme_color_override("font_hover_color", Color(1, 0.6, 0.6))
	btn.add_theme_font_size_override("font_size", 11)
	var normal := StyleBoxFlat.new()
	normal.bg_color = Color(0, 0, 0, 0)
	normal.border_width_left = 1
	normal.border_width_top = 1
	normal.border_width_right = 1
	normal.border_width_bottom = 1
	normal.border_color = Color(danger, 0.4)
	var hover := normal.duplicate() as StyleBoxFlat
	hover.bg_color = Color(danger, 0.15)
	btn.add_theme_stylebox_override("normal", normal)
	btn.add_theme_stylebox_override("hover", hover)
	btn.add_theme_stylebox_override("pressed", hover)
	btn.add_theme_stylebox_override("focus", hover)
