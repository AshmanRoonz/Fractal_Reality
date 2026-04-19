extends SceneTree

# Headless coverage for cinematic_overlay.gd and hud.gd's forwarding layer.
# Runs in the SceneTree so we can install widgets as real children and tick
# their timers via _process(delta) the way the game loop would. No rendering
# happens (we never call _draw manually); the tests assert on the internal
# timer / visibility state the renderer reads.

const CinematicOverlayScript = preload("res://scripts/cinematic_overlay.gd")
const SandboxHUD = preload("res://scripts/hud.gd")

func _init() -> void:
	var ok := true

	# --- Hit marker + kill marker timers ---
	var overlay := CinematicOverlayScript.new()
	get_root().add_child(overlay)

	overlay.show_hit_marker()
	if overlay._hit_marker_timer != 0.0:
		push_error("show_hit_marker did not reset timer: got %f" % overlay._hit_marker_timer)
		ok = false
	overlay._process(CinematicOverlayScript.HIT_MARKER_DURATION + 0.01)
	if overlay._hit_marker_timer != -1.0:
		push_error("hit marker did not expire: got %f" % overlay._hit_marker_timer)
		ok = false
	print("HIT_MARKER expire: OK")

	overlay.show_kill_marker()
	overlay._process(CinematicOverlayScript.KILL_MARKER_DURATION + 0.01)
	if overlay._kill_marker_timer != -1.0:
		push_error("kill marker did not expire: got %f" % overlay._kill_marker_timer)
		ok = false
	print("KILL_MARKER expire: OK")

	# --- Killstreak (count < 2 is a no-op) ---
	overlay.show_killstreak(1)
	if overlay._streak_timer >= 0.0 or overlay._streak_count != 0:
		push_error("killstreak(1) should no-op: timer=%f count=%d" % [overlay._streak_timer, overlay._streak_count])
		ok = false
	overlay.show_killstreak(2)
	if overlay._streak_timer != 0.0 or overlay._streak_count != 2:
		push_error("killstreak(2) did not activate: timer=%f count=%d" % [overlay._streak_timer, overlay._streak_count])
		ok = false
	if String(overlay._streak_data.get("label", "")) != "DOUBLE KILL":
		push_error("killstreak(2) wrong label: %s" % String(overlay._streak_data.get("label", "")))
		ok = false
	# Clamp past GODLIKE: count=100 should still resolve to the last STREAK_DATA entry.
	overlay.show_killstreak(100)
	if String(overlay._streak_data.get("label", "")) != "GODLIKE":
		push_error("killstreak(100) did not clamp to GODLIKE: %s" % String(overlay._streak_data.get("label", "")))
		ok = false
	overlay._process(CinematicOverlayScript.KILLSTREAK_DURATION + 0.01)
	if overlay._streak_timer != -1.0 or overlay._streak_count != 0:
		push_error("killstreak did not expire: timer=%f count=%d" % [overlay._streak_timer, overlay._streak_count])
		ok = false
	print("KILLSTREAK activate + clamp + expire: OK")

	# --- Medals: each MEDAL_DATA key, unknown key, stacking, independent expiry ---
	for medal_id in ["firstBlood", "revenge", "shutdown", "longshot", "assist", "savior", "execution"]:
		overlay._medals.clear()
		overlay.show_medal(medal_id)
		if overlay._medals.size() != 1:
			push_error("medal '%s' did not push: size=%d" % [medal_id, overlay._medals.size()])
			ok = false
			continue
		var data: Dictionary = overlay._medals[0]["data"]
		var expected_label: String = String(CinematicOverlayScript.MEDAL_DATA[medal_id]["label"])
		if String(data.get("label", "")) != expected_label:
			push_error("medal '%s' carried wrong data: got label='%s'" % [medal_id, String(data.get("label", ""))])
			ok = false
	overlay._medals.clear()
	overlay.show_medal("not_a_real_medal")
	if overlay._medals.size() != 0:
		push_error("unknown medal id was accepted")
		ok = false
	# Stack two medals, tick halfway: both should still be present.
	overlay.show_medal("firstBlood")
	overlay.show_medal("longshot")
	if overlay._medals.size() != 2:
		push_error("medal stacking failed: size=%d" % overlay._medals.size())
		ok = false
	overlay._process(CinematicOverlayScript.MEDAL_DURATION * 0.5)
	if overlay._medals.size() != 2:
		push_error("medals expired prematurely: size=%d" % overlay._medals.size())
		ok = false
	overlay._process(CinematicOverlayScript.MEDAL_DURATION + 0.01)
	if overlay._medals.size() != 0:
		push_error("medals did not expire: size=%d" % overlay._medals.size())
		ok = false
	print("MEDALS all-ids + unknown + stacking + expire: OK")

	# --- Countdown: numeric uses NUMBER duration, "FIGHT" uses FIGHT duration ---
	overlay.show_countdown(3, "ROUND 1")
	if overlay._countdown_is_fight:
		push_error("numeric countdown should not be fight mode")
		ok = false
	if overlay._countdown_number != "3":
		push_error("countdown number wrong: got '%s'" % overlay._countdown_number)
		ok = false
	if not is_equal_approx(overlay._countdown_duration, CinematicOverlayScript.COUNTDOWN_NUMBER_DURATION):
		push_error("numeric countdown wrong duration: got %f" % overlay._countdown_duration)
		ok = false
	overlay.show_countdown(0, "")
	if not overlay._countdown_is_fight or overlay._countdown_number != "FIGHT":
		push_error("countdown(0) did not enter fight mode: number='%s'" % overlay._countdown_number)
		ok = false
	if not is_equal_approx(overlay._countdown_duration, CinematicOverlayScript.COUNTDOWN_FIGHT_DURATION):
		push_error("fight countdown wrong duration: got %f" % overlay._countdown_duration)
		ok = false
	overlay.show_countdown("FIGHT", "")
	if not overlay._countdown_is_fight or overlay._countdown_number != "FIGHT":
		push_error("countdown(\"FIGHT\") did not enter fight mode")
		ok = false
	overlay._process(CinematicOverlayScript.COUNTDOWN_FIGHT_DURATION + 0.01)
	if overlay._countdown_timer != -1.0:
		push_error("countdown did not expire: got %f" % overlay._countdown_timer)
		ok = false
	print("COUNTDOWN numeric + 0 + FIGHT + expire: OK")

	# --- Ability flash: with explicit color, with default sentinel, with unknown id ---
	overlay.show_ability_flash("phase_dash", CinematicOverlayScript.color_for_ability("phase_dash"))
	if overlay._ability_timer != 0.0:
		push_error("ability flash did not activate")
		ok = false
	if overlay._ability_label != "PHASE_DASH ACTIVE":
		push_error("ability flash wrong label: '%s'" % overlay._ability_label)
		ok = false
	# Color should be the phase_dash color (0, 0.8, 1.0).
	var dash_color: Color = CinematicOverlayScript.ABILITY_COLORS["phase_dash"]
	if not is_equal_approx(overlay._ability_color.r, dash_color.r) or not is_equal_approx(overlay._ability_color.g, dash_color.g) or not is_equal_approx(overlay._ability_color.b, dash_color.b):
		push_error("ability flash wrong color")
		ok = false
	# Passing Color(0,0,0,0) should fall back to the default (white).
	overlay.show_ability_flash("made_up_ability", Color(0, 0, 0, 0))
	if not is_equal_approx(overlay._ability_color.r, CinematicOverlayScript.ABILITY_DEFAULT_COLOR.r):
		push_error("ability flash sentinel did not fall back to default")
		ok = false
	# color_for_ability on unknown id returns default.
	var unknown_color := CinematicOverlayScript.color_for_ability("does_not_exist")
	if not is_equal_approx(unknown_color.r, CinematicOverlayScript.ABILITY_DEFAULT_COLOR.r):
		push_error("color_for_ability fallback failed")
		ok = false
	overlay._process(CinematicOverlayScript.ABILITY_FLASH_DURATION + 0.01)
	if overlay._ability_timer != -1.0:
		push_error("ability flash did not expire: got %f" % overlay._ability_timer)
		ok = false
	print("ABILITY_FLASH explicit + sentinel + unknown-id + expire: OK")

	# --- Respawn fade: show ramps 0 -> 1, hide ramps 1 -> 0 ---
	overlay._respawn_fade = 0.0
	overlay.show_respawn("SCORCH")
	if not overlay.is_respawn_visible():
		push_error("respawn not visible after show_respawn")
		ok = false
	if overlay._respawn_killer != "SCORCH":
		push_error("respawn killer not captured: '%s'" % overlay._respawn_killer)
		ok = false
	# After one full fade duration the fade should be saturated at 1.
	overlay._process(CinematicOverlayScript.RESPAWN_FADE + 0.01)
	if not is_equal_approx(overlay._respawn_fade, 1.0):
		push_error("respawn fade did not saturate at 1.0: got %f" % overlay._respawn_fade)
		ok = false
	overlay.hide_respawn()
	if overlay.is_respawn_visible():
		push_error("respawn still visible after hide_respawn")
		ok = false
	# After one fade duration the fade should be saturated at 0.
	overlay._process(CinematicOverlayScript.RESPAWN_FADE + 0.01)
	if not is_equal_approx(overlay._respawn_fade, 0.0):
		push_error("respawn fade did not return to 0.0: got %f" % overlay._respawn_fade)
		ok = false
	print("RESPAWN fade-up + fade-down: OK")

	# --- Execution prompt toggle ---
	overlay.set_execution_prompt(true)
	if not overlay._exec_prompt_visible:
		push_error("exec prompt not visible after set_execution_prompt(true)")
		ok = false
	overlay.set_execution_prompt(false)
	if overlay._exec_prompt_visible:
		push_error("exec prompt visible after set_execution_prompt(false)")
		ok = false
	print("EXEC_PROMPT toggle: OK")

	overlay.queue_free()

	# --- SandboxHUD forwarding ---
	var hud := SandboxHUD.new()
	get_root().add_child(hud)
	hud._ready()
	if hud.cinematic == null:
		push_error("SandboxHUD missing cinematic child")
		ok = false
	else:
		hud.show_hit_marker()
		if hud.cinematic._hit_marker_timer < 0.0:
			push_error("hud.show_hit_marker did not forward")
			ok = false
		hud.show_kill_marker()
		if hud.cinematic._kill_marker_timer < 0.0:
			push_error("hud.show_kill_marker did not forward")
			ok = false
		hud.show_killstreak(3)
		if hud.cinematic._streak_count != 3:
			push_error("hud.show_killstreak did not forward: count=%d" % hud.cinematic._streak_count)
			ok = false
		hud.show_medal("firstBlood")
		if hud.cinematic._medals.size() != 1:
			push_error("hud.show_medal did not forward: size=%d" % hud.cinematic._medals.size())
			ok = false
		hud.show_countdown(2, "ROUND 2")
		if hud.cinematic._countdown_number != "2":
			push_error("hud.show_countdown did not forward: '%s'" % hud.cinematic._countdown_number)
			ok = false
		hud.show_ability_flash("vortex_shield")
		if hud.cinematic._ability_label != "VORTEX_SHIELD ACTIVE":
			push_error("hud.show_ability_flash did not forward: '%s'" % hud.cinematic._ability_label)
			ok = false
		hud.show_respawn("TONE")
		if not hud.cinematic.is_respawn_visible():
			push_error("hud.show_respawn did not forward")
			ok = false
		hud.hide_respawn()
		if hud.cinematic.is_respawn_visible():
			push_error("hud.hide_respawn did not forward")
			ok = false
		hud.set_execution_prompt(true)
		if not hud.cinematic._exec_prompt_visible:
			push_error("hud.set_execution_prompt did not forward")
			ok = false
		print("SANDBOX_HUD cinematic forwarding: OK")

	# --- player_ship ability_activated signal fires from _try_activate_ability ---
	var GameData := load("res://scripts/game_data.gd")
	GameData.ensure_input_map()
	var player: PlayerShip = PlayerShip.new()
	get_root().add_child(player)
	player._ready()
	var saw_ability := [false]
	var captured_id := [""]
	var captured_slot := [-1]
	player.ability_activated.connect(func(ability_id: String, _name: String, slot: int) -> void:
		saw_ability[0] = true
		captured_id[0] = ability_id
		captured_slot[0] = slot
	)
	# Force cooldown to 0 so the activation path runs, then fire slot 0.
	player.ability_cooldowns[0] = 0.0
	player._try_activate_ability(0)
	if not saw_ability[0]:
		push_error("player.ability_activated did not fire for slot 0")
		ok = false
	if captured_slot[0] != 0:
		push_error("ability_activated captured wrong slot: %d" % captured_slot[0])
		ok = false
	if captured_id[0].is_empty():
		push_error("ability_activated captured empty id")
		ok = false
	print("PLAYER_SHIP ability_activated signal: OK (id='%s' slot=%d)" % [captured_id[0], captured_slot[0]])

	# Cooldown blocks re-activation: the signal should NOT fire the second time.
	saw_ability[0] = false
	player._try_activate_ability(0)
	if saw_ability[0]:
		push_error("ability_activated fired while cooldown > 0")
		ok = false
	print("PLAYER_SHIP cooldown gating: OK")

	if ok:
		print("RESULT: PASS")
		quit(0)
	else:
		push_error("HUD overlay tests FAILED")
		quit(1)
