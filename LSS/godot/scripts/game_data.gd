class_name GameData
extends RefCounted

const ARENA_EXTENTS := Vector3(1400.0, 700.0, 1400.0)
const MAP_UNIT := 150.0

# ---- Menu-to-match selection state ----
# MainMenu writes these; Main reads them on load. Defaults let Main stand
# alone in an editor run without going through the menu.
static var selected_loadout_key: String = "ION"
static var selected_map_key: String = "hourglass"

const CHASSIS := {
	"FRIGATE": {
		"name": "Frigate",
		"max_health": 7500.0,
		"max_shield": 2500.0,
		"flight_speed": 450.0,
		"strafe_speed": 350.0,
		"vertical_speed": 300.0,
		"acceleration": 1200.0,
		"deceleration": 800.0,
		"max_dashes": 3,
		"dash_speed": 900.0,
		"dash_duration": 0.4,
		"dash_cooldown": 4.0,
		"hull_width": 60.0,
		"hull_height": 25.0,
		"hull_length": 80.0,
		"color": 0x44aaff,
		"health_segments": 3
	},
	"CORVETTE": {
		"name": "Corvette",
		"max_health": 10000.0,
		"max_shield": 3500.0,
		"flight_speed": 350.0,
		"strafe_speed": 280.0,
		"vertical_speed": 250.0,
		"acceleration": 800.0,
		"deceleration": 600.0,
		"max_dashes": 2,
		"dash_speed": 750.0,
		"dash_duration": 0.5,
		"dash_cooldown": 5.0,
		"hull_width": 80.0,
		"hull_height": 30.0,
		"hull_length": 100.0,
		"color": 0x44cc44,
		"health_segments": 4
	},
	"DREADNOUGHT": {
		"name": "Dreadnought",
		"max_health": 12500.0,
		"max_shield": 5000.0,
		"flight_speed": 250.0,
		"strafe_speed": 180.0,
		"vertical_speed": 160.0,
		"acceleration": 500.0,
		"deceleration": 400.0,
		"max_dashes": 1,
		"dash_speed": 550.0,
		"dash_duration": 0.6,
		"dash_cooldown": 7.0,
		"hull_width": 110.0,
		"hull_height": 45.0,
		"hull_length": 140.0,
		"color": 0xff6644,
		"health_segments": 5
	}
}

const LOADOUT_KEYS := ["ION", "SCORCH", "NORTHSTAR", "RONIN", "TONE", "LEGION", "MONARCH"]

const LOADOUTS := {
	"ION": {
		"name": "ION",
		"class_name": "Corvette MkII",
		"chassis": "CORVETTE",
		"weapon": {
			"name": "Splitter Rifle",
			"mode": "hitscan",
			"damage": 380.0,
			"fire_rate": 0.25,
			"clip_size": 30,
			"range": 3000.0,
			"pellets": 1,
			"spinup": 0.0,
			"spread": 0.0
		},
		"abilities": [
			{"id": "laser_shot", "name": "Laser Shot", "cooldown": 10.0, "desc": "Heavy beam burst"},
			{"id": "vortex_shield", "name": "Vortex Shield", "cooldown": 12.0, "duration": 3.0, "desc": "Defensive front shield"},
			{"id": "trip_wire", "name": "Trip Wire", "cooldown": 12.0, "desc": "Deploy proximity mine"}
		],
		"core": {"id": "laser_core", "name": "Laser Core", "duration": 4.0, "desc": "Continuous high-power beam"}
	},
	"SCORCH": {
		"name": "SCORCH",
		"class_name": "Dreadnought Incinerator",
		"chassis": "DREADNOUGHT",
		"weapon": {
			"name": "T-203 Thermite",
			"mode": "projectile",
			"damage": 900.0,
			"fire_rate": 1.2,
			"clip_size": 12,
			"range": 2500.0,
			"projectile_speed": 600.0,
			"pellets": 1,
			"spinup": 0.0,
			"spread": 0.02
		},
		"abilities": [
			{"id": "firewall", "name": "Firewall", "cooldown": 10.0, "desc": "Moving fire wave"},
			{"id": "thermal_shield", "name": "Thermal Shield", "cooldown": 14.0, "duration": 4.0, "desc": "Absorb damage and burn nearby"},
			{"id": "incendiary_trap", "name": "Incendiary Trap", "cooldown": 15.0, "desc": "Deploy burning gas trap"}
		],
		"core": {"id": "flame_core", "name": "Flame Core", "duration": 0.4, "desc": "Massive local blast"}
	},
	"NORTHSTAR": {
		"name": "NORTHSTAR",
		"class_name": "Frigate Starcaster",
		"chassis": "FRIGATE",
		"weapon": {
			"name": "Plasma Railgun",
			"mode": "hitscan",
			"damage": 1000.0,
			"fire_rate": 1.5,
			"clip_size": 6,
			"range": 4500.0,
			"pellets": 1,
			"spinup": 0.0,
			"spread": 0.0
		},
		"abilities": [
			{"id": "cluster_missile", "name": "Cluster Missile", "cooldown": 8.0, "desc": "Explodes into bursts"},
			{"id": "afterburner", "name": "Afterburner", "cooldown": 10.0, "duration": 3.0, "desc": "Speed boost"},
			{"id": "tether_trap", "name": "Tether Trap", "cooldown": 12.0, "desc": "Deploy slow field"}
		],
		"core": {"id": "afterburner_core", "name": "Afterburner Core", "duration": 5.0, "desc": "Empowered speed and volleys"}
	},
	"RONIN": {
		"name": "RONIN",
		"class_name": "Frigate Blade",
		"chassis": "FRIGATE",
		"weapon": {
			"name": "Leadwall",
			"mode": "spread",
			"damage": 200.0,
			"fire_rate": 0.85,
			"clip_size": 4,
			"range": 900.0,
			"pellets": 8,
			"spinup": 0.0,
			"spread": 0.06
		},
		"abilities": [
			{"id": "arc_wave", "name": "Arc Wave", "cooldown": 8.0, "desc": "Electric shockwave"},
			{"id": "sword_block", "name": "Sword Block", "cooldown": 8.0, "duration": 3.0, "desc": "Reduce incoming damage"},
			{"id": "phase_dash", "name": "Phase Dash", "cooldown": 6.0, "desc": "Burst invulnerable dash"}
		],
		"core": {"id": "sword_core", "name": "Sword Core", "duration": 6.0, "desc": "Empowered close-range combat"}
	},
	"TONE": {
		"name": "TONE",
		"class_name": "Corvette Tracker",
		"chassis": "CORVETTE",
		"weapon": {
			"name": "40mm Tracker",
			"mode": "projectile",
			"damage": 660.0,
			"fire_rate": 0.6,
			"clip_size": 20,
			"range": 3500.0,
			"projectile_speed": 900.0,
			"pellets": 1,
			"spinup": 0.0,
			"spread": 0.01
		},
		"abilities": [
			{"id": "tracker_rockets", "name": "Tracker Rockets", "cooldown": 6.0, "desc": "Homing missile burst"},
			{"id": "particle_wall", "name": "Particle Wall", "cooldown": 14.0, "duration": 6.0, "desc": "Temporary blocking wall"},
			{"id": "sonar_lock", "name": "Sonar Lock", "cooldown": 12.0, "duration": 5.0, "desc": "Mark a target"}
		],
		"core": {"id": "salvo_core", "name": "Salvo Core", "duration": 4.0, "desc": "Sustained missile barrage"}
	},
	"LEGION": {
		"name": "LEGION",
		"class_name": "Dreadnought Siege",
		"chassis": "DREADNOUGHT",
		"weapon": {
			"name": "Predator Cannon",
			"mode": "hitscan",
			"damage": 85.0,
			"fire_rate": 0.05,
			"clip_size": 150,
			"range": 1500.0,
			"pellets": 1,
			"spinup": 1.2,
			"spread": 0.04
		},
		"abilities": [
			{"id": "power_shot", "name": "Power Shot", "cooldown": 8.0, "desc": "Heavy precision blast"},
			{"id": "gun_shield", "name": "Gun Shield", "cooldown": 12.0, "duration": 4.0, "desc": "Frontal shield"},
			{"id": "mode_switch", "name": "Mode Switch", "cooldown": 2.0, "desc": "Toggle long-range mode"}
		],
		"core": {"id": "smart_core", "name": "Smart Core", "duration": 8.0, "desc": "Auto-assisted barrage"}
	},
	"MONARCH": {
		"name": "MONARCH",
		"class_name": "Corvette Sovereign",
		"chassis": "CORVETTE",
		"weapon": {
			"name": "XO-16 Chaingun",
			"mode": "hitscan",
			"damage": 240.0,
			"fire_rate": 0.09,
			"clip_size": 40,
			"range": 3000.0,
			"pellets": 1,
			"spinup": 0.4,
			"spread": 0.02
		},
		"abilities": [
			{"id": "rocket_salvo", "name": "Rocket Salvo", "cooldown": 6.0, "desc": "Rapid rocket burst"},
			{"id": "energy_siphon", "name": "Energy Siphon", "cooldown": 8.0, "desc": "Drain shield and heal"},
			{"id": "rearm", "name": "Rearm", "cooldown": 12.0, "desc": "Reset cooldowns and reload"}
		],
		"core": {"id": "upgrade_core", "name": "Upgrade Core", "duration": 0.2, "desc": "Permanent upgrade tier"}
	}
}

const SHIP_MODELS := {
	"NORTHSTAR": {"path": "res://assets/ships/northstar.glb", "face_flip": true, "scale_mult": 1.10},
	"RONIN": {"path": "res://assets/ships/ronin.glb", "face_flip": true, "scale_mult": 1.10},
	"ION": {"path": "res://assets/ships/ion.glb", "face_flip": true, "scale_mult": 1.15},
	"TONE": {"path": "res://assets/ships/tone.glb", "face_flip": true, "scale_mult": 1.00},
	"MONARCH": {"path": "res://assets/ships/monarch.glb", "face_flip": true, "scale_mult": 1.10},
	"SCORCH": {"path": "res://assets/ships/scorch.glb", "face_flip": true, "scale_mult": 1.05},
	"LEGION": {"path": "res://assets/ships/legion.glb", "face_flip": true, "scale_mult": 1.05}
}

const MAPS := {
	"hourglass": {
		"name": "The Nexus",
		"description": "Ring layout with six chambers and a central hub.",
		"rooms": [
			{"id": "center", "team": null, "position": Vector3(0.0, 0.0, 0.0), "radius": MAP_UNIT * 2.5},
			{"id": "spawn_a", "team": "A", "position": Vector3(0.0, 0.0, -MAP_UNIT * 8.0), "radius": MAP_UNIT * 2.2},
			{"id": "ne", "team": null, "position": Vector3(MAP_UNIT * 7.0, MAP_UNIT * 2.0, -MAP_UNIT * 4.0), "radius": MAP_UNIT * 1.8},
			{"id": "se", "team": null, "position": Vector3(MAP_UNIT * 7.0, -MAP_UNIT * 2.0, MAP_UNIT * 4.0), "radius": MAP_UNIT * 1.8},
			{"id": "spawn_b", "team": "B", "position": Vector3(0.0, 0.0, MAP_UNIT * 8.0), "radius": MAP_UNIT * 2.2},
			{"id": "sw", "team": null, "position": Vector3(-MAP_UNIT * 7.0, -MAP_UNIT * 2.0, MAP_UNIT * 4.0), "radius": MAP_UNIT * 1.8},
			{"id": "nw", "team": null, "position": Vector3(-MAP_UNIT * 7.0, MAP_UNIT * 2.0, -MAP_UNIT * 4.0), "radius": MAP_UNIT * 1.8}
		],
		"tunnels": [
			{"path": [Vector3(0.0, 0.0, -MAP_UNIT * 8.0), Vector3(MAP_UNIT * 7.0, MAP_UNIT * 2.0, -MAP_UNIT * 4.0)]},
			{"path": [Vector3(MAP_UNIT * 7.0, MAP_UNIT * 2.0, -MAP_UNIT * 4.0), Vector3(MAP_UNIT * 7.0, -MAP_UNIT * 2.0, MAP_UNIT * 4.0)]},
			{"path": [Vector3(MAP_UNIT * 7.0, -MAP_UNIT * 2.0, MAP_UNIT * 4.0), Vector3(0.0, 0.0, MAP_UNIT * 8.0)]},
			{"path": [Vector3(0.0, 0.0, MAP_UNIT * 8.0), Vector3(-MAP_UNIT * 7.0, -MAP_UNIT * 2.0, MAP_UNIT * 4.0)]},
			{"path": [Vector3(-MAP_UNIT * 7.0, -MAP_UNIT * 2.0, MAP_UNIT * 4.0), Vector3(-MAP_UNIT * 7.0, MAP_UNIT * 2.0, -MAP_UNIT * 4.0)]},
			{"path": [Vector3(-MAP_UNIT * 7.0, MAP_UNIT * 2.0, -MAP_UNIT * 4.0), Vector3(0.0, 0.0, -MAP_UNIT * 8.0)]},
			{"path": [Vector3(0.0, 0.0, -MAP_UNIT * 8.0), Vector3(0.0, 0.0, 0.0)]},
			{"path": [Vector3(MAP_UNIT * 7.0, MAP_UNIT * 2.0, -MAP_UNIT * 4.0), Vector3(0.0, 0.0, 0.0)]},
			{"path": [Vector3(MAP_UNIT * 7.0, -MAP_UNIT * 2.0, MAP_UNIT * 4.0), Vector3(0.0, 0.0, 0.0)]},
			{"path": [Vector3(0.0, 0.0, MAP_UNIT * 8.0), Vector3(0.0, 0.0, 0.0)]},
			{"path": [Vector3(-MAP_UNIT * 7.0, -MAP_UNIT * 2.0, MAP_UNIT * 4.0), Vector3(0.0, 0.0, 0.0)]},
			{"path": [Vector3(-MAP_UNIT * 7.0, MAP_UNIT * 2.0, -MAP_UNIT * 4.0), Vector3(0.0, 0.0, 0.0)]}
		]
	}
}

const DEFAULT_SIGNATURE := {
	"muzzle_color": 0xffcc66,
	"tracer_color": 0xffff66,
	"impact_light_color": 0xffcc66,
	"engine_color": 0x66eeff,
	"plume_color": 0xaaeeff,
	"shield_color": 0x44ccff,
	"panel_color": 0x66ccff,
	"tracer_core_radius": 1.2,
	"tracer_beam_radius": 2.0,
	"tracer_glow_radius": 6.0,
	"beam_lifetime": 0.08,
	"glow_lifetime": 0.15,
	"flash_scale": 1.0,
	"engine_pulse_rate": 12.0,
	"plume_length_scale": 1.0
}

const SHIP_SIGNATURES := {
	"ION": {
		"muzzle_color": 0x66eaff,
		"tracer_color": 0x66f2ff,
		"impact_light_color": 0x88eeff,
		"engine_color": 0x4fdcff,
		"plume_color": 0x9ff8ff,
		"shield_color": 0x55d8ff,
		"panel_color": 0x44bbff,
		"tracer_core_radius": 1.0,
		"tracer_beam_radius": 1.7,
		"tracer_glow_radius": 5.0,
		"beam_lifetime": 0.09,
		"glow_lifetime": 0.18,
		"flash_scale": 0.95,
		"engine_pulse_rate": 16.0,
		"plume_length_scale": 1.05
	},
	"SCORCH": {
		"muzzle_color": 0xff6622,
		"tracer_color": 0xff8a3a,
		"impact_light_color": 0xff9944,
		"engine_color": 0xff9955,
		"plume_color": 0xffc080,
		"shield_color": 0xff8844,
		"panel_color": 0xff7744,
		"tracer_core_radius": 1.4,
		"tracer_beam_radius": 2.2,
		"tracer_glow_radius": 6.8,
		"beam_lifetime": 0.08,
		"glow_lifetime": 0.16,
		"flash_scale": 1.15,
		"engine_pulse_rate": 9.0,
		"plume_length_scale": 1.2
	},
	"NORTHSTAR": {
		"muzzle_color": 0xb9c8ff,
		"tracer_color": 0xaed0ff,
		"impact_light_color": 0xdde8ff,
		"engine_color": 0x9fb8ff,
		"plume_color": 0xe0f0ff,
		"shield_color": 0xa9beff,
		"panel_color": 0x7d95ff,
		"tracer_core_radius": 0.85,
		"tracer_beam_radius": 1.35,
		"tracer_glow_radius": 4.4,
		"beam_lifetime": 0.11,
		"glow_lifetime": 0.22,
		"flash_scale": 0.9,
		"engine_pulse_rate": 18.0,
		"plume_length_scale": 1.15
	},
	"RONIN": {
		"muzzle_color": 0xffc27a,
		"tracer_color": 0xffb15a,
		"impact_light_color": 0xffc67a,
		"engine_color": 0xffbb66,
		"plume_color": 0xffe2ad,
		"shield_color": 0xffaa66,
		"panel_color": 0xff9955,
		"tracer_core_radius": 1.35,
		"tracer_beam_radius": 2.4,
		"tracer_glow_radius": 5.8,
		"beam_lifetime": 0.06,
		"glow_lifetime": 0.12,
		"flash_scale": 1.08,
		"engine_pulse_rate": 20.0,
		"plume_length_scale": 0.95
	},
	"TONE": {
		"muzzle_color": 0xffc44a,
		"tracer_color": 0xffbf4a,
		"impact_light_color": 0xffcf66,
		"engine_color": 0xffc155,
		"plume_color": 0xffefb0,
		"shield_color": 0xffbb55,
		"panel_color": 0xffaa33,
		"tracer_core_radius": 1.0,
		"tracer_beam_radius": 1.8,
		"tracer_glow_radius": 5.2,
		"beam_lifetime": 0.09,
		"glow_lifetime": 0.18,
		"flash_scale": 1.0,
		"engine_pulse_rate": 11.0,
		"plume_length_scale": 1.0
	},
	"LEGION": {
		"muzzle_color": 0xffdd55,
		"tracer_color": 0xffdd55,
		"impact_light_color": 0xffdd77,
		"engine_color": 0xffc966,
		"plume_color": 0xffebaa,
		"shield_color": 0xffcc66,
		"panel_color": 0xffbb55,
		"tracer_core_radius": 1.5,
		"tracer_beam_radius": 2.6,
		"tracer_glow_radius": 7.2,
		"beam_lifetime": 0.05,
		"glow_lifetime": 0.10,
		"flash_scale": 1.18,
		"engine_pulse_rate": 8.0,
		"plume_length_scale": 1.08
	},
	"MONARCH": {
		"muzzle_color": 0xb9ff66,
		"tracer_color": 0xd9ff66,
		"impact_light_color": 0xdfff88,
		"engine_color": 0x8dff99,
		"plume_color": 0xd8ffd0,
		"shield_color": 0x88ff99,
		"panel_color": 0x66dd88,
		"tracer_core_radius": 1.1,
		"tracer_beam_radius": 1.9,
		"tracer_glow_radius": 5.6,
		"beam_lifetime": 0.07,
		"glow_lifetime": 0.14,
		"flash_scale": 1.0,
		"engine_pulse_rate": 13.0,
		"plume_length_scale": 1.06
	}
}

static func color_from_hex(value: int) -> Color:
	return Color(
		float((value >> 16) & 255) / 255.0,
		float((value >> 8) & 255) / 255.0,
		float(value & 255) / 255.0,
		1.0
	)

static func get_loadout_keys() -> PackedStringArray:
	return PackedStringArray(LOADOUT_KEYS)

static func get_loadout(loadout_key: String) -> Dictionary:
	return LOADOUTS.get(loadout_key, LOADOUTS["ION"]).duplicate(true)

static func get_chassis_for_loadout(loadout_key: String) -> Dictionary:
	var loadout := get_loadout(loadout_key)
	return CHASSIS.get(loadout.get("chassis", "CORVETTE"), CHASSIS["CORVETTE"]).duplicate(true)

static func get_signature(loadout_key: String) -> Dictionary:
	var signature := DEFAULT_SIGNATURE.duplicate(true)
	signature.merge(SHIP_SIGNATURES.get(loadout_key, {}), true)
	return signature

static func get_model_spec(loadout_key: String) -> Dictionary:
	return SHIP_MODELS.get(loadout_key, {}).duplicate(true)

static func get_map_data(map_key: String) -> Dictionary:
	return MAPS.get(map_key, MAPS["hourglass"]).duplicate(true)

static func ensure_input_map() -> void:
	# Keyboard + mouse (mirrors HTML lines 680-681 and 9070-9073 keybinds:
	# Q/E/F trigger activateAbility(0/1/2), V triggers activateCore(),
	# R reloads, Shift dashes, Space/Ctrl move up/down, L-click fires).
	_ensure_key_action("move_forward", KEY_W)
	_ensure_key_action("move_backward", KEY_S)
	_ensure_key_action("move_left", KEY_A)
	_ensure_key_action("move_right", KEY_D)
	_ensure_key_action("move_up", KEY_SPACE)
	_ensure_key_action("move_down", KEY_CTRL)
	_ensure_key_action("dash", KEY_SHIFT)
	_ensure_key_action("reload", KEY_R)
	# Ability keys: Q / E / F match the HTML loadout activateAbility() calls.
	# Numeric 1 / 2 / 3 stay as convenience aliases (no HTML collision).
	_ensure_key_action("ability_1", KEY_Q)
	_ensure_key_action("ability_1", KEY_1)
	_ensure_key_action("ability_2", KEY_E)
	_ensure_key_action("ability_2", KEY_2)
	_ensure_key_action("ability_3", KEY_F)
	_ensure_key_action("ability_3", KEY_3)
	# Core ability: V matches HTML `keys['v'] -> activateCore()` (line 9073).
	_ensure_key_action("core_ability", KEY_V)
	# Mid-match loadout cycling is a Godot-only convenience (HTML only lets
	# you pick at the select screen). Parked on the bracket keys so they do
	# not collide with Q/E abilities.
	_ensure_key_action("prev_loadout", KEY_BRACKETLEFT)
	_ensure_key_action("next_loadout", KEY_BRACKETRIGHT)
	_ensure_mouse_action("fire_primary", MOUSE_BUTTON_LEFT)

	# Gamepad bindings (mirrors HTML gpBindings defaults at lines 963-971 of
	# last_ship_sailing.html). HTML mapping uses W3C gamepad API indices which
	# translate as follows to Godot JoyButton constants:
	#   HTML 7 (RT)       -> trigger axis JOY_AXIS_TRIGGER_RIGHT (fire)
	#   HTML 0 (A)        -> JOY_BUTTON_A (dash)
	#   HTML 2 (X)        -> JOY_BUTTON_X (reload)
	#   HTML 4 (LB)       -> JOY_BUTTON_LEFT_SHOULDER (ability 1, offensive)
	#   HTML 5 (RB)       -> JOY_BUTTON_RIGHT_SHOULDER (ability 2, defensive)
	#   HTML 3 (Y)        -> JOY_BUTTON_Y (ability 3, utility)
	#   HTML 12 (DPadUp)  -> JOY_BUTTON_DPAD_UP (core ability)
	#   HTML 10 (L3)      -> JOY_BUTTON_LEFT_STICK (move up / ascend)
	#   HTML 11 (R3)      -> JOY_BUTTON_RIGHT_STICK (move down / descend)
	# Loadout cycling is a Godot-only convenience (HTML only lets you pick at
	# the select screen); parked on D-Pad left/right so they don't collide.
	# Trigger axes remain for fire because HTML's RT-button-index is actually
	# a Godot axis. Settings.apply_to_input_map() can override any button
	# assignment but leaves axis events untouched, so the RT trigger still
	# works as a fallback even if a user clears the button binding.
	_ensure_joy_axis_action("fire_primary", JOY_AXIS_TRIGGER_RIGHT, 1.0, 0.5)
	_ensure_joy_button("dash", JOY_BUTTON_A)
	_ensure_joy_button("reload", JOY_BUTTON_X)
	_ensure_joy_button("ability_1", JOY_BUTTON_LEFT_SHOULDER)
	_ensure_joy_button("ability_2", JOY_BUTTON_RIGHT_SHOULDER)
	_ensure_joy_button("ability_3", JOY_BUTTON_Y)
	_ensure_joy_button("core_ability", JOY_BUTTON_DPAD_UP)
	_ensure_joy_button("move_up", JOY_BUTTON_LEFT_STICK)
	_ensure_joy_button("move_down", JOY_BUTTON_RIGHT_STICK)
	_ensure_joy_button("prev_loadout", JOY_BUTTON_DPAD_LEFT)
	_ensure_joy_button("next_loadout", JOY_BUTTON_DPAD_RIGHT)

	# Left-stick movement with dead-zone (applyDeadzone equivalent in HTML line 7862)
	_ensure_joy_axis_action("move_forward", JOY_AXIS_LEFT_Y, -1.0, 0.2)
	_ensure_joy_axis_action("move_backward", JOY_AXIS_LEFT_Y, 1.0, 0.2)
	_ensure_joy_axis_action("move_left", JOY_AXIS_LEFT_X, -1.0, 0.2)
	_ensure_joy_axis_action("move_right", JOY_AXIS_LEFT_X, 1.0, 0.2)

	# Right-stick look axes; player_ship reads them directly via Input.get_joy_axis
	_ensure_action("look_x_positive")
	_ensure_action("look_x_negative")
	_ensure_action("look_y_positive")
	_ensure_action("look_y_negative")
	_ensure_joy_axis_action("look_x_positive", JOY_AXIS_RIGHT_X, 1.0, 0.2)
	_ensure_joy_axis_action("look_x_negative", JOY_AXIS_RIGHT_X, -1.0, 0.2)
	_ensure_joy_axis_action("look_y_positive", JOY_AXIS_RIGHT_Y, 1.0, 0.2)
	_ensure_joy_axis_action("look_y_negative", JOY_AXIS_RIGHT_Y, -1.0, 0.2)

static func _ensure_action(action: StringName) -> void:
	if not InputMap.has_action(action):
		InputMap.add_action(action)

static func _ensure_key_action(action: StringName, keycode: Key) -> void:
	_ensure_action(action)
	for event in InputMap.action_get_events(action):
		if event is InputEventKey and event.physical_keycode == keycode:
			return
	var key_event := InputEventKey.new()
	key_event.physical_keycode = keycode
	InputMap.action_add_event(action, key_event)

static func _ensure_mouse_action(action: StringName, button: MouseButton) -> void:
	_ensure_action(action)
	for event in InputMap.action_get_events(action):
		if event is InputEventMouseButton and event.button_index == button:
			return
	var mouse_event := InputEventMouseButton.new()
	mouse_event.button_index = button
	InputMap.action_add_event(action, mouse_event)

static func _ensure_joy_button(action: StringName, button: JoyButton) -> void:
	_ensure_action(action)
	for event in InputMap.action_get_events(action):
		if event is InputEventJoypadButton and event.button_index == button:
			return
	var joy_event := InputEventJoypadButton.new()
	joy_event.button_index = button
	InputMap.action_add_event(action, joy_event)

static func _ensure_joy_axis_action(action: StringName, axis: JoyAxis, value: float, deadzone: float) -> void:
	_ensure_action(action)
	for event in InputMap.action_get_events(action):
		if event is InputEventJoypadMotion and event.axis == axis and signf(event.axis_value) == signf(value):
			return
	var axis_event := InputEventJoypadMotion.new()
	axis_event.axis = axis
	axis_event.axis_value = value
	InputMap.action_set_deadzone(action, deadzone)
	InputMap.action_add_event(action, axis_event)
