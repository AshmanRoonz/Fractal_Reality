extends SceneTree

const Settings = preload("res://scripts/settings.gd")
const GameData = preload("res://scripts/game_data.gd")

func _init() -> void:
	# Ensure InputMap has the actions Settings targets.
	GameData.ensure_input_map()

	# Default load (should succeed even with no file).
	Settings.load_from_disk()
	var default_mouse := Settings.mouse_sensitivity
	print("DEFAULT mouse_sensitivity = ", default_mouse)

	# Mutate + save.
	Settings.mouse_sensitivity = 0.005
	Settings.gp_look_sensitivity = 8.5
	Settings.gp_deadzone = 0.22
	Settings.invert_look_y = true
	Settings.swap_sticks = true
	Settings.trigger_threshold = 0.45
	Settings.gp_bindings["dash"] = JOY_BUTTON_RIGHT_SHOULDER  # rebind dash to RB
	Settings.save_to_disk()
	Settings.apply_to_input_map()

	# Reset static state and reload; values should round-trip.
	Settings.mouse_sensitivity = 0.0
	Settings.gp_look_sensitivity = 0.0
	Settings.gp_deadzone = 0.0
	Settings.invert_look_y = false
	Settings.swap_sticks = false
	Settings.trigger_threshold = 0.0
	Settings.load_from_disk()
	print("RELOAD mouse_sensitivity = ", Settings.mouse_sensitivity)
	print("RELOAD gp_look_sensitivity = ", Settings.gp_look_sensitivity)
	print("RELOAD gp_deadzone = ", Settings.gp_deadzone)
	print("RELOAD invert_look_y = ", Settings.invert_look_y)
	print("RELOAD swap_sticks = ", Settings.swap_sticks)
	print("RELOAD trigger_threshold = ", Settings.trigger_threshold)
	print("RELOAD dash binding = ", Settings.gp_bindings["dash"])

	var ok: bool = (
		abs(Settings.mouse_sensitivity - 0.005) < 0.0001
		and abs(Settings.gp_look_sensitivity - 8.5) < 0.01
		and abs(Settings.gp_deadzone - 0.22) < 0.001
		and Settings.invert_look_y == true
		and Settings.swap_sticks == true
		and abs(Settings.trigger_threshold - 0.45) < 0.001
		and int(Settings.gp_bindings["dash"]) == JOY_BUTTON_RIGHT_SHOULDER
	)

	# Also verify InputMap reflects the new dash binding (now RB).
	var dash_has_rb: bool = false
	for event in InputMap.action_get_events("dash"):
		if event is InputEventJoypadButton and event.button_index == JOY_BUTTON_RIGHT_SHOULDER:
			dash_has_rb = true
			break
	print("DASH action has RB event = ", dash_has_rb)
	ok = ok and dash_has_rb

	# Verify stick movement actions got the configured deadzone.
	var mf_dz := InputMap.action_get_deadzone("move_forward")
	print("move_forward deadzone = ", mf_dz)
	ok = ok and abs(mf_dz - 0.22) < 0.001

	# Verify triggers were tuned.
	var fp_dz := InputMap.action_get_deadzone("fire_primary")
	print("fire_primary deadzone = ", fp_dz)
	ok = ok and abs(fp_dz - 0.45) < 0.001

	# Restore defaults so we don't leave the user's next run with these values.
	Settings.reset_to_defaults()

	if ok:
		print("RESULT: PASS")
		quit(0)
	else:
		push_error("Settings roundtrip FAILED")
		quit(1)
