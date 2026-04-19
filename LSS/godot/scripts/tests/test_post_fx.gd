extends SceneTree

# Covers the post-FX polish pass (task #25):
#   - damage_overlay.gd: red vignette + chromatic aberration pulse with
#     0.45s ease-out animation, alpha 0->1 over first 15% then back to 0.
#   - hud.gd flash_damage() forwarding
#   - player_ship.gd damage_taken signal (fires on both non-fatal and fatal
#     hits; carries pre-shield inflicted amount and clamped ratio)
#   - player_ship.gd add_screen_shake() public trigger

const DamageOverlayScript = preload("res://scripts/damage_overlay.gd")
const SandboxHUD = preload("res://scripts/hud.gd")

func _init() -> void:
	var ok := true

	# --- Damage overlay: animation curve ---
	var overlay := DamageOverlayScript.new()
	get_root().add_child(overlay)
	overlay._ready()
	if overlay.is_flashing():
		push_error("Damage overlay should not be flashing on spawn")
		ok = false
	if overlay._vignette == null or overlay._ca_material == null:
		push_error("Damage overlay missing vignette or CA material")
		ok = false

	overlay.flash(0.5)
	if not overlay.is_flashing():
		push_error("flash() did not start the timer")
		ok = false

	# Tick just past fade-in (15% of 0.45 = 0.0675s). Expect peak alpha ~0.5.
	overlay._process(0.07)
	var peak_alpha := overlay._vignette.modulate.a
	if peak_alpha < 0.40 or peak_alpha > 0.55:
		push_error("Peak vignette alpha out of range at fade-in end: got %f expected ~0.5" % peak_alpha)
		ok = false
	var peak_ca: float = overlay._ca_material.get_shader_parameter("ca_strength")
	if peak_ca <= 0.0:
		push_error("CA strength should be >0 at fade-in end: got %f" % peak_ca)
		ok = false

	# Tick past the end of the animation. Expect everything zeroed and timer idle.
	overlay._process(0.5)
	if overlay.is_flashing():
		push_error("Damage overlay timer should be idle after full duration")
		ok = false
	if overlay._vignette.modulate.a > 0.001:
		push_error("Vignette alpha should be ~0 after animation: got %f" % overlay._vignette.modulate.a)
		ok = false
	var end_ca: float = overlay._ca_material.get_shader_parameter("ca_strength")
	if end_ca > 0.0001:
		push_error("CA strength should be ~0 after animation: got %f" % end_ca)
		ok = false

	# MIN_INTENSITY clamp: tiny hits still flash visibly.
	overlay.flash(0.01)
	overlay._process(0.07)
	if overlay._vignette.modulate.a < DamageOverlayScript.MIN_INTENSITY * 0.9:
		push_error("MIN_INTENSITY clamp broken: tiny hit produced alpha %f" % overlay._vignette.modulate.a)
		ok = false
	overlay._process(0.5)  # reset for next phase
	print("DAMAGE_OVERLAY animation: OK (peak alpha %.3f, CA %.5f)" % [peak_alpha, peak_ca])

	# --- HUD forwarding ---
	var hud := SandboxHUD.new()
	get_root().add_child(hud)
	hud._ready()
	if hud.damage_overlay != null:
		hud.damage_overlay._ready()
	if hud.banner != null:
		hud.banner._ready()
	if hud.kill_feed != null:
		hud.kill_feed._ready()
	if hud.scoreboard != null:
		hud.scoreboard._ready()

	if hud.damage_overlay == null:
		push_error("HUD did not create damage_overlay child")
		ok = false
	if hud.damage_overlay != null and hud.damage_overlay.is_flashing():
		push_error("HUD damage_overlay should not start in flashing state")
		ok = false

	hud.flash_damage(0.4)
	if hud.damage_overlay != null and not hud.damage_overlay.is_flashing():
		push_error("HUD.flash_damage did not start the overlay animation")
		ok = false
	print("SANDBOX_HUD damage flash forwarding: OK")

	# --- Layer order: damage overlay below banner/scoreboard/killfeed ---
	if hud.damage_overlay != null and hud.banner != null:
		var dmg_idx := hud.damage_overlay.get_index()
		var banner_idx := hud.banner.get_index()
		if dmg_idx >= banner_idx:
			push_error("Damage overlay draws over banner (damage=%d banner=%d)" % [dmg_idx, banner_idx])
			ok = false
		print("HUD layer order (damage overlay below banner): OK (damage=%d banner=%d)" % [dmg_idx, banner_idx])

	# --- PlayerShip damage_taken signal ---
	var GameData := load("res://scripts/game_data.gd")
	GameData.ensure_input_map()
	var player: PlayerShip = PlayerShip.new()
	get_root().add_child(player)
	player._ready()

	var captured_amount := [0.0]
	var captured_ratio := [0.0]
	var captured_count := [0]
	player.damage_taken.connect(func(amount: float, ratio: float) -> void:
		captured_amount[0] = amount
		captured_ratio[0] = ratio
		captured_count[0] += 1
	)

	# Sub-fatal hit; shields should soak it. Signal must still fire.
	player.apply_damage(200.0, Vector3.ZERO, "SCORCH")
	if captured_count[0] != 1:
		push_error("damage_taken should fire once per sub-fatal hit (got %d)" % captured_count[0])
		ok = false
	if captured_amount[0] <= 0.0:
		push_error("damage_taken amount should be >0 on a 200-damage hit (got %f)" % captured_amount[0])
		ok = false
	if captured_ratio[0] < 0.0 or captured_ratio[0] > 1.0:
		push_error("damage_taken ratio out of [0,1]: got %f" % captured_ratio[0])
		ok = false

	# Fatal hit; signal should still fire exactly once more.
	player.apply_damage(99999.0, Vector3.ZERO, "SCORCH")
	if captured_count[0] != 2:
		push_error("damage_taken should fire on fatal hit too (count=%d)" % captured_count[0])
		ok = false
	if captured_ratio[0] < 0.99:
		push_error("damage_taken ratio should clamp to ~1.0 on huge hit (got %f)" % captured_ratio[0])
		ok = false
	print("PLAYER_SHIP damage_taken signal: OK (count=%d last ratio=%.3f)" % [captured_count[0], captured_ratio[0]])

	# --- add_screen_shake() public trigger: no-ops when dead ---
	var prev_shake := player.camera_shake
	player.add_screen_shake(0.5)
	if player.camera_shake != prev_shake:
		push_error("add_screen_shake should no-op after player death")
		ok = false

	# Fresh player for the alive-path check
	var player2: PlayerShip = PlayerShip.new()
	get_root().add_child(player2)
	player2._ready()
	player2.add_screen_shake(1.5)
	if player2.camera_shake < 1.4:
		push_error("add_screen_shake did not raise camera_shake while alive: got %f" % player2.camera_shake)
		ok = false
	# Cap check: stacking shakes past 4.0 should clamp.
	player2.add_screen_shake(10.0)
	if player2.camera_shake > 4.0:
		push_error("add_screen_shake did not respect 4.0 cap: got %f" % player2.camera_shake)
		ok = false
	print("PLAYER_SHIP add_screen_shake: OK (cap held at %.2f)" % player2.camera_shake)

	if ok:
		print("RESULT: PASS")
		quit(0)
	else:
		push_error("Post-FX tests FAILED")
		quit(1)
