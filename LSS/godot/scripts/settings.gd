class_name Settings
extends RefCounted

# ---------------------------------------------------------------------------
# Settings (gamepad + mouse)
#
# Mirrors the HTML settings-overlay data in buildSettingsPage() at line 9141
# of last_ship_sailing.html. Values persist to user://settings.cfg via
# ConfigFile. Call Settings.load_from_disk() once at startup; call
# Settings.save_to_disk() after any mutation. Settings.apply_to_input_map()
# is invoked by load/reset/rebind to keep the live InputMap in sync.
# ---------------------------------------------------------------------------

const CONFIG_PATH := "user://settings.cfg"

# ---- Mouse ----
static var mouse_sensitivity: float = 0.0024  # HTML input.sensitivity = 0.002 (radians per pixel)

# ---- Gamepad sensitivity / curves ----
static var gp_look_sensitivity: float = 6.0    # radians/sec scaler
static var gp_move_sensitivity: float = 10.0   # stick -> movement scaler
static var gp_look_curve: float = 1.6          # exponent applied to |stick|
static var gp_move_curve: float = 1.2

# ---- Gamepad deadzone / trigger ----
static var gp_deadzone: float = 0.15
static var trigger_threshold: float = 0.3

# ---- Gamepad options ----
static var invert_look_y: bool = false
static var swap_sticks: bool = false

# ---- Gamepad button bindings (Godot JoyButton indices or BIND_TRIGGER_* ;
# ----  -1 = unbound). Keyed by InputMap action names. Defaults mirror HTML
# ---- gpBindings at last_ship_sailing.html lines 963-971; fire_primary maps
# ---- to RT (synthetic trigger index), everything else is a standard button.
static var gp_bindings: Dictionary = {
	"fire_primary":  BIND_TRIGGER_RIGHT,
	"dash":          JOY_BUTTON_A,
	"reload":        JOY_BUTTON_X,
	"ability_1":     JOY_BUTTON_LEFT_SHOULDER,
	"ability_2":     JOY_BUTTON_RIGHT_SHOULDER,
	"ability_3":     JOY_BUTTON_Y,
	"core_ability":  JOY_BUTTON_DPAD_UP,
	"move_up":       JOY_BUTTON_LEFT_STICK,
	"move_down":     JOY_BUTTON_RIGHT_STICK,
	"next_loadout":  JOY_BUTTON_DPAD_RIGHT,
	"prev_loadout":  JOY_BUTTON_DPAD_LEFT,
}

# Action -> human label for the settings UI.
const ACTION_LABELS := {
	"fire_primary":  "Fire Weapon",
	"dash":          "Dash",
	"reload":        "Reload",
	"ability_1":     "Ability 1 (Offensive)",
	"ability_2":     "Ability 2 (Defensive)",
	"ability_3":     "Ability 3 (Utility)",
	"core_ability":  "Core Ability",
	"move_up":       "Move Up",
	"move_down":     "Move Down",
	"next_loadout":  "Next Loadout",
	"prev_loadout":  "Previous Loadout",
}

# Synthetic binding indices for trigger axes. Godot exposes triggers as axes
# (JOY_AXIS_TRIGGER_LEFT / JOY_AXIS_TRIGGER_RIGHT), not JoyButton constants, so
# they are invisible to a button-only rebind UI. These high values let the UI
# and apply_to_input_map() treat a trigger pull like any other button binding
# while generating the correct InputEventJoypadMotion event under the hood.
const BIND_TRIGGER_LEFT := 100
const BIND_TRIGGER_RIGHT := 101

# Binding index -> human label. Standard JoyButton indices 0-14 plus the two
# synthetic trigger entries above.
const BUTTON_NAMES := {
	-1: "None",
	 0: "A",                      # JOY_BUTTON_A
	 1: "B",                      # JOY_BUTTON_B
	 2: "X",                      # JOY_BUTTON_X
	 3: "Y",                      # JOY_BUTTON_Y
	 4: "Back",                   # JOY_BUTTON_BACK
	 5: "Guide",                  # JOY_BUTTON_GUIDE
	 6: "Start",                  # JOY_BUTTON_START
	 7: "L3",                     # JOY_BUTTON_LEFT_STICK
	 8: "R3",                     # JOY_BUTTON_RIGHT_STICK
	 9: "LB",                     # JOY_BUTTON_LEFT_SHOULDER
	10: "RB",                     # JOY_BUTTON_RIGHT_SHOULDER
	11: "D-Up",                   # JOY_BUTTON_DPAD_UP
	12: "D-Down",                 # JOY_BUTTON_DPAD_DOWN
	13: "D-Left",                 # JOY_BUTTON_DPAD_LEFT
	14: "D-Right",                # JOY_BUTTON_DPAD_RIGHT
	BIND_TRIGGER_LEFT:  "LT",     # JOY_AXIS_TRIGGER_LEFT (synthetic)
	BIND_TRIGGER_RIGHT: "RT",     # JOY_AXIS_TRIGGER_RIGHT (synthetic)
}

# Ordered list of selectable binding indices for the rebind dropdowns. The
# triggers sit at the end so they read as "less standard" fallbacks.
const BUTTON_ORDER: Array = [-1, 0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, BIND_TRIGGER_LEFT, BIND_TRIGGER_RIGHT]

static var _loaded: bool = false

# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------
static func load_from_disk() -> void:
	var cfg := ConfigFile.new()
	var err := cfg.load(CONFIG_PATH)
	if err == OK:
		mouse_sensitivity   = float(cfg.get_value("mouse", "sensitivity", mouse_sensitivity))
		gp_look_sensitivity = float(cfg.get_value("gamepad", "look_sensitivity", gp_look_sensitivity))
		gp_move_sensitivity = float(cfg.get_value("gamepad", "move_sensitivity", gp_move_sensitivity))
		gp_look_curve       = float(cfg.get_value("gamepad", "look_curve", gp_look_curve))
		gp_move_curve       = float(cfg.get_value("gamepad", "move_curve", gp_move_curve))
		gp_deadzone         = float(cfg.get_value("gamepad", "deadzone", gp_deadzone))
		trigger_threshold   = float(cfg.get_value("gamepad", "trigger_threshold", trigger_threshold))
		invert_look_y       = bool(cfg.get_value("gamepad", "invert_look_y", invert_look_y))
		swap_sticks         = bool(cfg.get_value("gamepad", "swap_sticks", swap_sticks))
		var saved_bindings: Dictionary = cfg.get_value("gamepad", "bindings", {})
		# Merge saved bindings over defaults so new actions keep working.
		for key in saved_bindings.keys():
			gp_bindings[key] = int(saved_bindings[key])
	_loaded = true
	apply_to_input_map()

static func save_to_disk() -> void:
	var cfg := ConfigFile.new()
	cfg.set_value("mouse", "sensitivity", mouse_sensitivity)
	cfg.set_value("gamepad", "look_sensitivity", gp_look_sensitivity)
	cfg.set_value("gamepad", "move_sensitivity", gp_move_sensitivity)
	cfg.set_value("gamepad", "look_curve", gp_look_curve)
	cfg.set_value("gamepad", "move_curve", gp_move_curve)
	cfg.set_value("gamepad", "deadzone", gp_deadzone)
	cfg.set_value("gamepad", "trigger_threshold", trigger_threshold)
	cfg.set_value("gamepad", "invert_look_y", invert_look_y)
	cfg.set_value("gamepad", "swap_sticks", swap_sticks)
	cfg.set_value("gamepad", "bindings", gp_bindings)
	cfg.save(CONFIG_PATH)

static func reset_to_defaults() -> void:
	mouse_sensitivity = 0.0024
	gp_look_sensitivity = 6.0
	gp_move_sensitivity = 10.0
	gp_look_curve = 1.6
	gp_move_curve = 1.2
	gp_deadzone = 0.15
	trigger_threshold = 0.3
	invert_look_y = false
	swap_sticks = false
	gp_bindings = {
		"fire_primary":  BIND_TRIGGER_RIGHT,
		"dash":          JOY_BUTTON_A,
		"reload":        JOY_BUTTON_X,
		"ability_1":     JOY_BUTTON_LEFT_SHOULDER,
		"ability_2":     JOY_BUTTON_RIGHT_SHOULDER,
		"ability_3":     JOY_BUTTON_Y,
		"core_ability":  JOY_BUTTON_DPAD_UP,
		"move_up":       JOY_BUTTON_LEFT_STICK,
		"move_down":     JOY_BUTTON_RIGHT_STICK,
		"next_loadout":  JOY_BUTTON_DPAD_RIGHT,
		"prev_loadout":  JOY_BUTTON_DPAD_LEFT,
	}
	apply_to_input_map()
	save_to_disk()

# ---------------------------------------------------------------------------
# InputMap synchronisation
# ---------------------------------------------------------------------------
# Walks gp_bindings and replaces each action's single JoyButton event (leaving
# axis/key/mouse events untouched). Also pushes trigger_threshold into the
# trigger actions' deadzones and gp_deadzone into the stick actions.
static func apply_to_input_map() -> void:
	var trig_dz := clampf(trigger_threshold, 0.05, 0.95)
	for action_variant in gp_bindings.keys():
		var action := StringName(action_variant)
		if not InputMap.has_action(action):
			continue
		# Clear old JoyButton events and any prior trigger axis events for this
		# action. Stick axes (LEFT_X/Y, RIGHT_X/Y) are left alone because those
		# are hardcoded by game_data.ensure_input_map() for movement and look.
		for event in InputMap.action_get_events(action):
			if event is InputEventJoypadButton:
				InputMap.action_erase_event(action, event)
			elif event is InputEventJoypadMotion:
				if event.axis == JOY_AXIS_TRIGGER_LEFT or event.axis == JOY_AXIS_TRIGGER_RIGHT:
					InputMap.action_erase_event(action, event)
		var btn := int(gp_bindings[action_variant])
		if btn == BIND_TRIGGER_LEFT or btn == BIND_TRIGGER_RIGHT:
			var axis_event := InputEventJoypadMotion.new()
			axis_event.axis = JOY_AXIS_TRIGGER_LEFT if btn == BIND_TRIGGER_LEFT else JOY_AXIS_TRIGGER_RIGHT
			axis_event.axis_value = 1.0
			InputMap.action_set_deadzone(action, trig_dz)
			InputMap.action_add_event(action, axis_event)
		elif btn >= 0:
			var new_event := InputEventJoypadButton.new()
			new_event.button_index = btn
			InputMap.action_add_event(action, new_event)

	# Re-tune the trigger-driven actions' deadzones whenever the
	# trigger_threshold slider moves. fire_primary and dash may carry a
	# trigger axis event if their gp_bindings map to BIND_TRIGGER_LEFT /
	# BIND_TRIGGER_RIGHT; setting the deadzone even when they don't is
	# harmless because Godot only reads it for axis events.
	if InputMap.has_action("fire_primary"):
		InputMap.action_set_deadzone("fire_primary", trig_dz)
	if InputMap.has_action("dash"):
		InputMap.action_set_deadzone("dash", trig_dz)

	# Movement stick deadzone. The look stick is read raw in player_ship.gd
	# and applies gp_deadzone directly, so we only update the movement
	# actions here.
	var stick_dz := clampf(gp_deadzone, 0.0, 0.9)
	for action_name in ["move_forward", "move_backward", "move_left", "move_right"]:
		if InputMap.has_action(action_name):
			InputMap.action_set_deadzone(action_name, stick_dz)

# ---------------------------------------------------------------------------
# Look-stick helper (used by player_ship.gd)
# ---------------------------------------------------------------------------
# Returns a cooked (dx, dy) pair scaled by delta. dx steers yaw (positive =
# look right); dy steers pitch (positive = camera pitches up after the
# caller's own sign convention is applied). Applies radial deadzone, curve,
# sensitivity, invertY, and swap-sticks.
static func read_look_stick(delta: float) -> Vector2:
	var look_x_axis := JOY_AXIS_RIGHT_X
	var look_y_axis := JOY_AXIS_RIGHT_Y
	if swap_sticks:
		look_x_axis = JOY_AXIS_LEFT_X
		look_y_axis = JOY_AXIS_LEFT_Y
	var raw := Vector2(
		Input.get_joy_axis(0, look_x_axis),
		Input.get_joy_axis(0, look_y_axis)
	)
	var cooked := _apply_radial_deadzone(raw, gp_deadzone)
	# Per-axis curve (pow preserves sign via signf) then sensitivity + delta.
	var cx := signf(cooked.x) * pow(absf(cooked.x), gp_look_curve) * gp_look_sensitivity * delta
	var cy := signf(cooked.y) * pow(absf(cooked.y), gp_look_curve) * gp_look_sensitivity * delta
	if invert_look_y:
		cy = -cy
	return Vector2(cx, cy)

# Returns a (forward/right/up)-friendly triple in stick-space units in
# [-1, 1] after deadzone + curve. The caller multiplies these by chassis
# speeds. Stick Y is inverted so +z means forward.
static func read_move_stick() -> Vector3:
	var move_x_axis := JOY_AXIS_LEFT_X
	var move_y_axis := JOY_AXIS_LEFT_Y
	if swap_sticks:
		move_x_axis = JOY_AXIS_RIGHT_X
		move_y_axis = JOY_AXIS_RIGHT_Y
	var raw := Vector2(
		Input.get_joy_axis(0, move_x_axis),
		Input.get_joy_axis(0, move_y_axis)
	)
	var cooked := _apply_radial_deadzone(raw, gp_deadzone)
	var cx := signf(cooked.x) * pow(absf(cooked.x), gp_move_curve)
	var cy := signf(cooked.y) * pow(absf(cooked.y), gp_move_curve)
	return Vector3(cx, 0.0, -cy)

# Radial deadzone: zero inside the dead circle, rescaled linearly outside.
static func _apply_radial_deadzone(v: Vector2, dz: float) -> Vector2:
	var mag := v.length()
	if mag <= dz:
		return Vector2.ZERO
	var scaled := (mag - dz) / maxf(0.0001, 1.0 - dz)
	return v * (scaled / mag)
