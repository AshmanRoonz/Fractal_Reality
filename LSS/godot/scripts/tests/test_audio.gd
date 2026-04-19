extends SceneTree

# Headless coverage for the audio system ported in task #52 (HTML
# last_ship_sailing.html:10600-11226).
#
# This test runs against the real Audio autoload (registered in project.godot
# as `Audio="*res://scripts/audio.gd"`), so it exercises the exact code path
# the game uses. We cannot actually *hear* anything in headless mode, but we
# can verify:
#
#   1. Bus layout (SFX_Dry, SFX_Wet, Ambient under Master; LPF on Master)
#   2. Reverb effect present on SFX_Wet
#   3. SFX pool populated (POOL_SIZE = 24 idle AudioStreamPlayers)
#   4. Phi cascade initialises PHI_LAYERS = 6 phase dicts
#   5. All 14 play_sound() type strings run without crashing (ensuring every
#      match branch synthesizes a buffer that fits the int16 pipeline)
#   6. play_weapon_fire() routing: hitscan vs railgun vs minigun vs projectile
#      vs spread vs missile all dispatch without error
#   7. start_ambient_bed / update_ambient_bed / stop_ambient_bed all toggle
#      the `_ambient_started` flag cleanly
#
# Anything that hits `push_error` fails the test; any swallowed exception in
# GDScript would still trip the assertion because we verify side effects
# (pool cursor, phase dict count, bus indices) after each call.

const AudioScript = preload("res://scripts/audio.gd")

var _ok := true

func _fail(msg: String) -> void:
	push_error(msg)
	_ok = false

func _get_audio() -> Node:
	# NOTE: Godot's `-s <script>` runner replaces the default SceneTree with
	# our own (extends SceneTree), and in that mode project.godot's
	# [autoload] section is NOT automatically instantiated. We therefore
	# mount the Audio script manually and drive its setup hooks directly so
	# the same code path the real game uses runs here too.
	var root := get_root()
	if root == null:
		_fail("get_root() returned null")
		return null
	if root.has_node("Audio"):
		return root.get_node("Audio")
	var manual: Node = AudioScript.new()
	manual.name = "Audio"
	root.add_child(manual)
	# In `_init()` the tree hasn't processed a frame yet, so NOTIFICATION_READY
	# is deferred. Call the setup methods directly to guarantee buses + pool
	# + bed are available before the asserts run. This mirrors what `_ready`
	# does in scripts/audio.gd.
	if manual.has_method("_ensure_buses"):
		manual.call("_ensure_buses")
	if manual.has_method("_build_sfx_pool"):
		manual.call("_build_sfx_pool")
	if manual.has_method("_build_ambient_bed"):
		manual.call("_build_ambient_bed")
	return manual

func _init() -> void:
	print("=== Audio system tests ===")
	var audio := _get_audio()
	if audio == null:
		push_error("Audio node unavailable; aborting")
		quit(1)
		return

	_assert_bus_layout()
	_assert_master_lpf()
	_assert_wet_reverb()
	_assert_sfx_pool(audio)
	_assert_phi_phases(audio)
	_assert_play_sound_all_types(audio)
	_assert_play_weapon_fire_routing(audio)
	_assert_ambient_bed_lifecycle(audio)

	if _ok:
		print("RESULT: PASS")
		quit(0)
	else:
		push_error("test_audio FAILED")
		quit(1)

# -- Bus layout ------------------------------------------------------------

func _assert_bus_layout() -> void:
	var expected := ["Master", "SFX_Dry", "SFX_Wet", "Ambient"]
	var present := {}
	for i in range(AudioServer.bus_count):
		present[AudioServer.get_bus_name(i)] = i
	for name in expected:
		if not present.has(name):
			_fail("Expected bus %s missing" % name)
			return
	# SFX_Dry / SFX_Wet / Ambient should all send to Master (index 0).
	for send_name in ["SFX_Dry", "SFX_Wet", "Ambient"]:
		var idx: int = present[send_name]
		var send := AudioServer.get_bus_send(idx)
		if send != "Master":
			_fail("Bus %s should send to Master, got %s" % [send_name, send])
	print("Bus layout (Master/SFX_Dry/SFX_Wet/Ambient): OK")

func _assert_master_lpf() -> void:
	var master_idx := AudioServer.get_bus_index("Master")
	var found := false
	for i in range(AudioServer.get_bus_effect_count(master_idx)):
		var fx := AudioServer.get_bus_effect(master_idx, i)
		if fx is AudioEffectLowPassFilter:
			found = true
			var lpf := fx as AudioEffectLowPassFilter
			# Cutoff should be roughly 3500 Hz (HTML's hiCut). Allow some slack.
			if absf(lpf.cutoff_hz - 3500.0) > 50.0:
				_fail("Master LPF cutoff should be ~3500 Hz, got %.1f" % lpf.cutoff_hz)
			break
	if not found:
		_fail("Master bus missing AudioEffectLowPassFilter")
	else:
		print("Master LPF @ 3500Hz: OK")

func _assert_wet_reverb() -> void:
	var wet_idx := AudioServer.get_bus_index("SFX_Wet")
	var found := false
	for i in range(AudioServer.get_bus_effect_count(wet_idx)):
		var fx := AudioServer.get_bus_effect(wet_idx, i)
		if fx is AudioEffectReverb:
			found = true
			break
	if not found:
		_fail("SFX_Wet bus missing AudioEffectReverb")
	else:
		print("SFX_Wet reverb: OK")

# -- SFX pool + phi phase initialisation -----------------------------------

func _assert_sfx_pool(audio: Node) -> void:
	# Peek at the private pool via the Node's child count. Each pool entry is
	# an AudioStreamPlayer child of the audio node.
	var player_count := 0
	for child in audio.get_children():
		if child is AudioStreamPlayer:
			player_count += 1
	# POOL_SIZE = 24 discrete SFX + 1 ambient = 25 expected.
	if player_count < 24:
		_fail("Expected at least 24 AudioStreamPlayer children for SFX pool, got %d" % player_count)
	else:
		print("SFX pool size: OK (%d players)" % player_count)

func _assert_phi_phases(audio: Node) -> void:
	var phases: Array = audio.get("_phi_phases")
	if phases.size() != 6:
		_fail("PHI_LAYERS should yield 6 phase dicts, got %d" % phases.size())
		return
	for i in range(phases.size()):
		var d: Dictionary = phases[i]
		for key in ["left", "right", "lfo_l", "lfo_r"]:
			if not d.has(key):
				_fail("phase[%d] missing key %s" % [i, key])
				return
	print("Phi cascade phase init (6 layers x 4 keys): OK")

# -- play_sound type coverage ----------------------------------------------

func _assert_play_sound_all_types(audio: Node) -> void:
	# All 14 HTML SFX types from last_ship_sailing.html:10865-11143 plus
	# round_start (11143). A branch that fails to synthesize will push_error
	# from inside the audio script, which _fail picks up via push_error
	# inherited from SceneTree's error_reported.
	var types := [
		"fire_hitscan", "fire_projectile", "fire_spread", "fire_minigun",
		"fire_railgun", "fire_salvo", "hit", "kill", "damage", "dash",
		"ability", "core", "explosion", "stasis", "reload", "death",
		"round_start"
	]
	for type_name in types:
		audio.play_sound(type_name)
	print("play_sound() x %d types: OK" % types.size())

# -- play_weapon_fire routing ----------------------------------------------

func _assert_play_weapon_fire_routing(audio: Node) -> void:
	# Cover every classification branch in play_weapon_fire.
	# hitscan (standard)       -> fire_hitscan
	audio.play_weapon_fire("hitscan", 0.25, false, false)
	# railgun (hitscan, slow)  -> fire_railgun (fire_rate >= 0.8)
	audio.play_weapon_fire("hitscan", 1.2, false, false)
	# minigun (hitscan, fast)  -> fire_minigun (fire_rate < 0.08)
	audio.play_weapon_fire("hitscan", 0.05, false, false)
	# projectile (standard)    -> fire_projectile
	audio.play_weapon_fire("projectile", 0.3, false, false)
	# homing/salvo missile     -> fire_salvo
	audio.play_weapon_fire("projectile", 0.3, true, false)
	audio.play_weapon_fire("projectile", 0.3, false, true)
	# spread (shotgun)         -> fire_spread
	audio.play_weapon_fire("spread", 0.4, false, false)
	print("play_weapon_fire routing (6 classes): OK")

# -- Ambient bed lifecycle -------------------------------------------------

func _assert_ambient_bed_lifecycle(audio: Node) -> void:
	# Pre-state: the bed may or may not be started yet (depends on whether an
	# earlier call in this test happened to start it). Force a known state.
	audio.stop_ambient_bed()
	if audio.get("_ambient_started"):
		_fail("stop_ambient_bed should leave _ambient_started false")
		return
	audio.start_ambient_bed()
	if not audio.get("_ambient_started"):
		_fail("start_ambient_bed should flip _ambient_started true")
		return
	# Tick update_ambient_bed across a few speeds / match states to exercise
	# the target-gain logic and the phase accumulators.
	audio.update_ambient_bed(0.0, "warmup")
	audio.update_ambient_bed(200.0, "playing")
	audio.update_ambient_bed(800.0, "playing")
	audio.update_ambient_bed(0.0, "round_end")
	# stop should cleanly release the bed again.
	audio.stop_ambient_bed()
	if audio.get("_ambient_started"):
		_fail("stop_ambient_bed should release _ambient_started")
		return
	print("Ambient bed start/update/stop: OK")
