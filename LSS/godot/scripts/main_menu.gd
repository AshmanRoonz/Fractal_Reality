class_name MainMenu
extends Control

# Godot port of the HTML ship-select + lobby flow (last_ship_sailing.html lines
# 627-682). Multiplayer (WebTorrent P2P) is not ported; the Godot build is
# solo + bots, so lobby collapses into a single Start button.
#
# Layout mirrors #ship-select: title, subtitle, loadout grid, map grid,
# control hints, big Start button. Palette matches the HTML #ffaa00 accent on
# rgba(5,5,15,0.97) background.

const GameData := preload("res://scripts/game_data.gd")
const Settings := preload("res://scripts/settings.gd")
const SETTINGS_OVERLAY_SCENE := preload("res://scenes/SettingsOverlay.tscn")

const ACCENT_COLOR := Color(1.0, 0.667, 0.0, 1.0)       # #ffaa00
const ACCENT_DIM := Color(0.533, 0.533, 0.533, 1.0)     # #888888
const CARD_BG := Color(0.078, 0.078, 0.157, 0.90)       # rgba(20,20,40,0.9)
const CARD_BORDER := Color(0.314, 0.314, 0.471, 0.4)    # rgba(80,80,120,0.4)
const CARD_BORDER_HOVER := ACCENT_COLOR
const BG_COLOR := Color(0.020, 0.020, 0.059, 0.97)      # rgba(5,5,15,0.97)
const STAT_COLOR := Color(0.667, 0.667, 0.667, 1.0)     # #aaa
const WEAPON_COLOR := Color(0.4, 0.733, 0.4, 1.0)       # #66bb66
const ABILITY_COLOR := Color(0.4, 0.8, 0.4, 1.0)        # #66cc66
const SUBTLE_COLOR := Color(0.333, 0.333, 0.333, 1.0)   # #555

const MAIN_SCENE_PATH := "res://scenes/Main.tscn"

var _selected_loadout_key: String = GameData.selected_loadout_key
var _selected_map_key: String = GameData.selected_map_key

var _loadout_cards: Dictionary = {}
var _map_cards: Dictionary = {}
var _start_button: Button
var _settings_overlay: SettingsOverlay = null

func _ready() -> void:
	# Make sure input map is ready so hotkeys (e.g. mouse click, ENTER) work in
	# case the user navigates from the menu back to gameplay via shortcut.
	GameData.ensure_input_map()
	# Load persisted settings before any input is read so the menu honours the
	# user's sensitivity/deadzone/button remaps immediately.
	Settings.load_from_disk()
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)

	anchor_right = 1.0
	anchor_bottom = 1.0
	mouse_filter = Control.MOUSE_FILTER_STOP

	_build_background()
	_build_layout()
	_refresh_start_button()
	# Grab focus on the currently-selected loadout card so gamepad D-pad / stick
	# has somewhere to land on first press (otherwise the first directional
	# input is swallowed because no Control owns focus).
	call_deferred("_grab_initial_focus")

func _grab_initial_focus() -> void:
	var target: Button = _loadout_cards.get(_selected_loadout_key, null)
	if target == null and _loadout_cards.size() > 0:
		target = _loadout_cards.values()[0]
	if target:
		target.grab_focus()

func _build_background() -> void:
	var bg := ColorRect.new()
	bg.color = BG_COLOR
	bg.anchor_right = 1.0
	bg.anchor_bottom = 1.0
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg)

func _build_layout() -> void:
	var margin := MarginContainer.new()
	margin.anchor_right = 1.0
	margin.anchor_bottom = 1.0
	margin.add_theme_constant_override("margin_left", 60)
	margin.add_theme_constant_override("margin_right", 60)
	margin.add_theme_constant_override("margin_top", 40)
	margin.add_theme_constant_override("margin_bottom", 40)
	add_child(margin)

	var root := VBoxContainer.new()
	root.alignment = BoxContainer.ALIGNMENT_BEGIN
	root.add_theme_constant_override("separation", 14)
	margin.add_child(root)

	# Title block.
	var title := _make_label("LAST SHIP SAILING", 36, ACCENT_COLOR, 4)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	root.add_child(title)

	var subtitle := _make_label("CHOOSE YOUR SHIP", 14, ACCENT_DIM, 2)
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	root.add_child(subtitle)

	var spacer1 := Control.new()
	spacer1.custom_minimum_size = Vector2(0, 12)
	root.add_child(spacer1)

	# Loadout grid (4 columns, mirrors HTML .ship-grid).
	var loadout_grid_wrap := CenterContainer.new()
	loadout_grid_wrap.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	root.add_child(loadout_grid_wrap)

	var loadout_grid := GridContainer.new()
	loadout_grid.columns = 4
	loadout_grid.add_theme_constant_override("h_separation", 12)
	loadout_grid.add_theme_constant_override("v_separation", 12)
	loadout_grid_wrap.add_child(loadout_grid)

	for key in GameData.get_loadout_keys():
		var card := _build_loadout_card(String(key))
		_loadout_cards[String(key)] = card
		loadout_grid.add_child(card)

	_highlight_loadout(_selected_loadout_key)

	# Map selector.
	var spacer2 := Control.new()
	spacer2.custom_minimum_size = Vector2(0, 18)
	root.add_child(spacer2)

	var map_heading := _make_label("SELECT MAP", 16, ACCENT_COLOR, 2)
	map_heading.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	map_heading.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	root.add_child(map_heading)

	var map_wrap := CenterContainer.new()
	map_wrap.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	root.add_child(map_wrap)

	var map_row := HBoxContainer.new()
	map_row.add_theme_constant_override("separation", 12)
	map_wrap.add_child(map_row)

	for map_key in GameData.MAPS.keys():
		var map_card := _build_map_card(String(map_key))
		_map_cards[String(map_key)] = map_card
		map_row.add_child(map_card)

	_highlight_map(_selected_map_key)

	# Control hint row (mirrors HTML lines 680-681).
	var spacer3 := Control.new()
	spacer3.custom_minimum_size = Vector2(0, 18)
	root.add_child(spacer3)

	var controls_hint := _make_label(
		"WASD: Move | SPACE/CTRL: Up/Down | MOUSE: Aim | SHIFT: Dash | 1/2/3: Abilities | F: Core | ESC: Pause",
		10, SUBTLE_COLOR, 1
	)
	controls_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	controls_hint.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	root.add_child(controls_hint)

	var gamepad_hint := _make_label(
		"GAMEPAD: Left stick move | Right stick aim | RT fire | LT dash | A/D-Up up | Dpad-Down down | B core",
		9, Color(0.267, 0.267, 0.267, 1.0), 1
	)
	gamepad_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	gamepad_hint.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	root.add_child(gamepad_hint)

	# Start button.
	var spacer4 := Control.new()
	spacer4.custom_minimum_size = Vector2(0, 16)
	root.add_child(spacer4)

	var button_row := HBoxContainer.new()
	button_row.alignment = BoxContainer.ALIGNMENT_CENTER
	button_row.add_theme_constant_override("separation", 16)
	button_row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	root.add_child(button_row)

	_start_button = Button.new()
	_start_button.text = "START SOLO + BOTS"
	_start_button.custom_minimum_size = Vector2(320, 56)
	_style_start_button(_start_button)
	_start_button.pressed.connect(_on_start_pressed)
	button_row.add_child(_start_button)

	var settings_button := Button.new()
	settings_button.text = "SETTINGS"
	settings_button.custom_minimum_size = Vector2(180, 56)
	_style_start_button(settings_button)
	settings_button.pressed.connect(_open_settings_overlay)
	button_row.add_child(settings_button)

func _make_label(text: String, font_size: int, color: Color, letter_spacing: int = 0) -> Label:
	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	# Godot's default Label doesn't support letter-spacing directly; approximate by
	# inserting thin spaces for the large title, leave smaller labels plain.
	if letter_spacing >= 3 and font_size >= 20:
		var spaced := ""
		for ch in text:
			spaced += ch + " "
		label.text = spaced.strip_edges()
	return label

func _build_loadout_card(key: String) -> Button:
	var loadout := GameData.get_loadout(key)
	var chassis := GameData.get_chassis_for_loadout(key)
	var weapon: Dictionary = loadout.get("weapon", {})
	var abilities: Array = loadout.get("abilities", [])

	var card := Button.new()
	card.custom_minimum_size = Vector2(200, 150)
	card.focus_mode = Control.FOCUS_ALL
	card.mouse_filter = Control.MOUSE_FILTER_STOP
	card.toggle_mode = true
	_style_card_button(card)

	var vbox := VBoxContainer.new()
	vbox.anchor_right = 1.0
	vbox.anchor_bottom = 1.0
	vbox.offset_left = 14.0
	vbox.offset_top = 12.0
	vbox.offset_right = -14.0
	vbox.offset_bottom = -12.0
	vbox.add_theme_constant_override("separation", 2)
	vbox.mouse_filter = Control.MOUSE_FILTER_IGNORE
	card.add_child(vbox)

	var name_label := _make_label(String(loadout.get("name", key)), 18, ACCENT_COLOR)
	vbox.add_child(name_label)

	var class_label := _make_label(
		"%s (%s)" % [String(loadout.get("class_name", "Prototype")), String(chassis.get("name", "Frame"))],
		11, ACCENT_DIM
	)
	vbox.add_child(class_label)

	var spacer := Control.new()
	spacer.custom_minimum_size = Vector2(0, 4)
	vbox.add_child(spacer)

	vbox.add_child(_make_label("Hull: %d" % int(chassis.get("max_health", 0.0)), 10, STAT_COLOR))
	vbox.add_child(_make_label("Shield: %d" % int(chassis.get("max_shield", 0.0)), 10, STAT_COLOR))
	vbox.add_child(_make_label("Speed: %d" % int(chassis.get("flight_speed", 0.0)), 10, STAT_COLOR))
	vbox.add_child(_make_label("Dashes: %d" % int(chassis.get("max_dashes", 0)), 10, STAT_COLOR))

	var weapon_label := _make_label(
		"%s (%d dmg)" % [String(weapon.get("name", "Weapon")), int(weapon.get("damage", 0.0))],
		10, WEAPON_COLOR
	)
	vbox.add_child(weapon_label)

	var ability_names: Array = []
	for ability in abilities:
		ability_names.append(String(ability.get("name", "-")))
	var ability_label := _make_label(" / ".join(ability_names), 9, ABILITY_COLOR)
	ability_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	vbox.add_child(ability_label)

	card.pressed.connect(func(): _select_loadout(key))
	return card

func _build_map_card(map_key: String) -> Button:
	var map_data: Dictionary = GameData.MAPS.get(map_key, {})

	var card := Button.new()
	card.custom_minimum_size = Vector2(220, 72)
	card.toggle_mode = true
	_style_card_button(card)

	var vbox := VBoxContainer.new()
	vbox.anchor_right = 1.0
	vbox.anchor_bottom = 1.0
	vbox.offset_left = 12.0
	vbox.offset_top = 10.0
	vbox.offset_right = -12.0
	vbox.offset_bottom = -10.0
	vbox.mouse_filter = Control.MOUSE_FILTER_IGNORE
	card.add_child(vbox)

	var name_label := _make_label(String(map_data.get("name", map_key)), 14, ACCENT_COLOR)
	vbox.add_child(name_label)

	var desc_label := _make_label(String(map_data.get("description", "")), 10, ACCENT_DIM)
	desc_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	vbox.add_child(desc_label)

	card.pressed.connect(func(): _select_map(map_key))
	return card

func _select_loadout(key: String) -> void:
	_selected_loadout_key = key
	_highlight_loadout(key)
	_refresh_start_button()

func _select_map(key: String) -> void:
	_selected_map_key = key
	_highlight_map(key)
	_refresh_start_button()

func _highlight_loadout(active_key: String) -> void:
	for key in _loadout_cards.keys():
		var card: Button = _loadout_cards[key]
		card.set_pressed_no_signal(key == active_key)

func _highlight_map(active_key: String) -> void:
	for key in _map_cards.keys():
		var card: Button = _map_cards[key]
		card.set_pressed_no_signal(key == active_key)

func _refresh_start_button() -> void:
	if _start_button:
		var loadout_name := String(GameData.get_loadout(_selected_loadout_key).get("name", _selected_loadout_key))
		var map_name := String(GameData.MAPS.get(_selected_map_key, {}).get("name", _selected_map_key))
		_start_button.text = "LAUNCH %s ON %s" % [loadout_name, map_name.to_upper()]

func _style_card_button(button: Button) -> void:
	var normal := StyleBoxFlat.new()
	normal.bg_color = CARD_BG
	normal.border_color = CARD_BORDER
	normal.set_border_width_all(1)
	normal.set_corner_radius_all(2)
	normal.content_margin_left = 14.0
	normal.content_margin_right = 14.0
	normal.content_margin_top = 12.0
	normal.content_margin_bottom = 12.0
	button.add_theme_stylebox_override("normal", normal)

	var hover := normal.duplicate() as StyleBoxFlat
	hover.border_color = ACCENT_COLOR
	hover.bg_color = Color(0.118, 0.118, 0.196, 0.9)  # rgba(30,30,50,0.9)
	button.add_theme_stylebox_override("hover", hover)

	var pressed := hover.duplicate() as StyleBoxFlat
	pressed.bg_color = Color(0.157, 0.118, 0.039, 0.95)
	pressed.border_color = ACCENT_COLOR
	pressed.set_border_width_all(2)
	button.add_theme_stylebox_override("pressed", pressed)

	var focus := pressed.duplicate() as StyleBoxFlat
	button.add_theme_stylebox_override("focus", focus)
	button.add_theme_color_override("font_color", Color(1, 1, 1, 1))
	button.add_theme_color_override("font_hover_color", Color(1, 1, 1, 1))
	button.add_theme_color_override("font_pressed_color", Color(1, 1, 1, 1))
	button.flat = false
	button.alignment = HORIZONTAL_ALIGNMENT_LEFT
	# Clear the text since we overlay a VBoxContainer of labels.
	button.text = ""

func _style_start_button(button: Button) -> void:
	var normal := StyleBoxFlat.new()
	normal.bg_color = Color(1.0, 0.667, 0.0, 0.15)
	normal.border_color = ACCENT_COLOR
	normal.set_border_width_all(1)
	normal.set_corner_radius_all(2)
	normal.content_margin_left = 40
	normal.content_margin_right = 40
	normal.content_margin_top = 14
	normal.content_margin_bottom = 14
	button.add_theme_stylebox_override("normal", normal)

	var hover := normal.duplicate() as StyleBoxFlat
	hover.bg_color = Color(1.0, 0.667, 0.0, 0.3)
	button.add_theme_stylebox_override("hover", hover)

	var pressed := hover.duplicate() as StyleBoxFlat
	pressed.bg_color = Color(1.0, 0.667, 0.0, 0.45)
	button.add_theme_stylebox_override("pressed", pressed)

	var focus := pressed.duplicate() as StyleBoxFlat
	button.add_theme_stylebox_override("focus", focus)
	button.add_theme_color_override("font_color", ACCENT_COLOR)
	button.add_theme_color_override("font_hover_color", ACCENT_COLOR)
	button.add_theme_color_override("font_pressed_color", Color(1, 1, 1, 1))
	button.add_theme_font_size_override("font_size", 16)

func _on_start_pressed() -> void:
	GameData.selected_loadout_key = _selected_loadout_key
	GameData.selected_map_key = _selected_map_key
	get_tree().change_scene_to_file(MAIN_SCENE_PATH)

func _open_settings_overlay() -> void:
	if is_instance_valid(_settings_overlay):
		return
	_settings_overlay = SETTINGS_OVERLAY_SCENE.instantiate() as SettingsOverlay
	add_child(_settings_overlay)
	_settings_overlay.closed.connect(_on_settings_overlay_closed)

func _on_settings_overlay_closed() -> void:
	_settings_overlay = null
	# The overlay captured the pointer while open; restore menu visibility.
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)

func _unhandled_input(event: InputEvent) -> void:
	# Quick launch with Enter / gamepad Start, back with Escape.
	if event is InputEventKey and event.pressed and not event.echo:
		match event.physical_keycode:
			KEY_ENTER:
				_on_start_pressed()
			KEY_ESCAPE:
				get_tree().quit()
	elif event is InputEventJoypadButton and event.pressed:
		if event.button_index == JOY_BUTTON_START:
			_on_start_pressed()
		elif event.button_index == JOY_BUTTON_BACK:
			get_tree().quit()
