extends SceneTree

# Headless coverage for the directional damage indicator subsystem on
# hud_overlay.gd, plus the forwarding wrapper on hud.gd. The indicators map
# an attacker's world-space position onto one of four edge overlays (top,
# bottom, left, right) so the player gets a directional cue for where the
# hit came from; HTML reference: last_ship_sailing.html:10294-10360.
#
# In `extends SceneTree -s` mode Camera3D.is_inside_tree() returns false and
# Camera3D.global_basis always resolves to identity (forward = -Z, right =
# +X, up = +Y) regardless of any rotation we set. We therefore place the
# player and attacker in world space and rely on the identity-basis
# direction math; rotating the camera in the test would be silently
# ignored.

const HUDOverlay = preload("res://scripts/hud_overlay.gd")
const SandboxHUD = preload("res://scripts/hud.gd")

func _init() -> void:
	var ok := true

	# --- Initial state: all four indicators start at 0.0 ---
	var overlay: Control = HUDOverlay.new()
	get_root().add_child(overlay)
	for dir in ["top", "bottom", "left", "right"]:
		if float(overlay.damage_indicators.get(dir, -1.0)) != 0.0:
			push_error("damage_indicators[%s] should start at 0.0" % dir)
			ok = false
	print("INIT damage_indicators all 0.0: OK")

	# Camera at origin with identity basis. forward = -Z, right = +X.
	var cam := Camera3D.new()
	get_root().add_child(cam)

	# --- Attacker straight ahead (player at origin, attacker at -Z) ---
	# to_attacker_norm = (0, 0, -1); forward.dot = 1.0 > 0.3 → top lit.
	# |f_dot| = 1.0 > 0.7 triggers the secondary lateral ping; r_dot = 0.0
	# so the ">= 0.0" branch lights right at 0.5 (not left).
	_reset_indicators(overlay)
	overlay.show_damage_indicator(Vector3(0, 0, -10), Vector3.ZERO, cam)
	if float(overlay.damage_indicators["top"]) != 1.0:
		push_error("attacker ahead should light top to 1.0; got %f" % float(overlay.damage_indicators["top"]))
		ok = false
	if float(overlay.damage_indicators["bottom"]) != 0.0:
		push_error("attacker ahead should not light bottom; got %f" % float(overlay.damage_indicators["bottom"]))
		ok = false
	if float(overlay.damage_indicators["right"]) != 0.5:
		push_error("attacker directly ahead should secondary-ping right at 0.5; got %f" % float(overlay.damage_indicators["right"]))
		ok = false
	if float(overlay.damage_indicators["left"]) != 0.0:
		push_error("attacker directly ahead should not ping left; got %f" % float(overlay.damage_indicators["left"]))
		ok = false
	print("Attacker ahead lights top + secondary right: OK")

	# --- Attacker directly behind ---
	# to_attacker_norm = (0, 0, 1); f_dot = -1.0 < -0.3 → bottom lit.
	# |f_dot| = 1.0 > 0.7 and r_dot = 0.0 → secondary right at 0.5.
	_reset_indicators(overlay)
	overlay.show_damage_indicator(Vector3(0, 0, 10), Vector3.ZERO, cam)
	if float(overlay.damage_indicators["bottom"]) != 1.0:
		push_error("attacker behind should light bottom; got %f" % float(overlay.damage_indicators["bottom"]))
		ok = false
	if float(overlay.damage_indicators["top"]) != 0.0:
		push_error("attacker behind should not light top; got %f" % float(overlay.damage_indicators["top"]))
		ok = false
	print("Attacker behind lights bottom: OK")

	# --- Attacker to the right (pure +X) ---
	# to_attacker_norm = (1, 0, 0); f_dot = 0.0, r_dot = 1.0 > 0.3 → right
	# lit, nothing else. |f_dot| = 0 so no secondary ping.
	_reset_indicators(overlay)
	overlay.show_damage_indicator(Vector3(10, 0, 0), Vector3.ZERO, cam)
	if float(overlay.damage_indicators["right"]) != 1.0:
		push_error("attacker right should light right; got %f" % float(overlay.damage_indicators["right"]))
		ok = false
	if float(overlay.damage_indicators["top"]) != 0.0 or float(overlay.damage_indicators["bottom"]) != 0.0 or float(overlay.damage_indicators["left"]) != 0.0:
		push_error("pure right should only light right; got top=%f bot=%f left=%f" % [float(overlay.damage_indicators["top"]), float(overlay.damage_indicators["bottom"]), float(overlay.damage_indicators["left"])])
		ok = false
	print("Attacker on right lights right only: OK")

	# --- Attacker to the left (pure -X) ---
	_reset_indicators(overlay)
	overlay.show_damage_indicator(Vector3(-10, 0, 0), Vector3.ZERO, cam)
	if float(overlay.damage_indicators["left"]) != 1.0:
		push_error("attacker left should light left; got %f" % float(overlay.damage_indicators["left"]))
		ok = false
	if float(overlay.damage_indicators["top"]) != 0.0 or float(overlay.damage_indicators["bottom"]) != 0.0 or float(overlay.damage_indicators["right"]) != 0.0:
		push_error("pure left should only light left; got top=%f bot=%f right=%f" % [float(overlay.damage_indicators["top"]), float(overlay.damage_indicators["bottom"]), float(overlay.damage_indicators["right"])])
		ok = false
	print("Attacker on left lights left only: OK")

	# --- Secondary ping flips to left when r_dot < 0 and |f_dot| > 0.7 ---
	# Attacker at (-0.1, 0, -1): to_attacker_norm ~ (-0.0995, 0, -0.995).
	# f_dot ~ 0.995 > 0.7 → top lit; r_dot ~ -0.0995 so the primary right /
	# left thresholds (|r_dot| > 0.3) fail, but the secondary ping uses
	# sign(r_dot): r_dot < 0 → left at 0.5.
	_reset_indicators(overlay)
	overlay.show_damage_indicator(Vector3(-0.1, 0, -1), Vector3.ZERO, cam)
	if float(overlay.damage_indicators["top"]) != 1.0:
		push_error("near-forward attacker should light top; got %f" % float(overlay.damage_indicators["top"]))
		ok = false
	if float(overlay.damage_indicators["left"]) != 0.5:
		push_error("near-forward attacker slightly-left should secondary-ping left at 0.5; got %f" % float(overlay.damage_indicators["left"]))
		ok = false
	if float(overlay.damage_indicators["right"]) != 0.0:
		push_error("near-forward attacker slightly-left should NOT ping right; got %f" % float(overlay.damage_indicators["right"]))
		ok = false
	print("Secondary lateral ping flips to left when r_dot < 0: OK")

	# --- Front-right diagonal lights both top and right at 1.0 ---
	# Attacker at (1, 0, -1): to_attacker_norm = (0.707, 0, -0.707).
	# f_dot = 0.707 > 0.3 → top at 1.0. r_dot = 0.707 > 0.3 → right at 1.0.
	# |f_dot| = 0.707 > 0.7, r_dot >= 0 → secondary right 0.5, but right is
	# already 1.0 so maxf() keeps it at 1.0 (no regression).
	_reset_indicators(overlay)
	overlay.show_damage_indicator(Vector3(1, 0, -1), Vector3.ZERO, cam)
	if float(overlay.damage_indicators["top"]) != 1.0:
		push_error("front-right diagonal should light top; got %f" % float(overlay.damage_indicators["top"]))
		ok = false
	if float(overlay.damage_indicators["right"]) != 1.0:
		push_error("front-right diagonal should light right at 1.0 (not regressed by secondary ping); got %f" % float(overlay.damage_indicators["right"]))
		ok = false
	if float(overlay.damage_indicators["bottom"]) != 0.0 or float(overlay.damage_indicators["left"]) != 0.0:
		push_error("front-right diagonal should leave bottom/left at 0; got bot=%f left=%f" % [float(overlay.damage_indicators["bottom"]), float(overlay.damage_indicators["left"])])
		ok = false
	print("Front-right diagonal lights both channels: OK")

	# --- Dead zone: |dot| below 0.3 does not light primary channels ---
	# Attacker at (0.1, 0, -0.1): both dots are ~0.707 after normalization
	# (same as above) so we can't use this — instead pick an attacker with
	# both |dots| < 0.3. Attacker at (0.2, 1.0, -0.2): the Y component
	# drags both normalized XZ components below 0.3.
	# to_attacker = (0.2, 1.0, -0.2), length ~ 1.04, so normalized
	# ~= (0.192, 0.962, -0.192). f_dot = 0.192, r_dot = 0.192. Both below
	# the 0.3 threshold. |f_dot| = 0.192 < 0.7 so no secondary ping either.
	_reset_indicators(overlay)
	overlay.show_damage_indicator(Vector3(0.2, 1.0, -0.2), Vector3.ZERO, cam)
	for dir in ["top", "bottom", "left", "right"]:
		if float(overlay.damage_indicators[dir]) != 0.0:
			push_error("dead-zone attacker should not light any indicator, but %s = %f" % [dir, float(overlay.damage_indicators[dir])])
			ok = false
	print("Dead-zone attacker (|dots| < 0.3) lights nothing: OK")

	# --- Player at non-origin position subtracts correctly ---
	# Player at (10, 0, 0), attacker at (0, 0, 0): to_attacker = (-10, 0, 0)
	# → normalized (-1, 0, 0), r_dot = -1.0 → left lit.
	_reset_indicators(overlay)
	overlay.show_damage_indicator(Vector3.ZERO, Vector3(10, 0, 0), cam)
	if float(overlay.damage_indicators["left"]) != 1.0:
		push_error("attacker at origin with player at +X should light left; got %f" % float(overlay.damage_indicators["left"]))
		ok = false
	print("Player offset subtracts correctly: OK")

	# --- Decay at 2.5/sec in _process ---
	# 0.1s tick should subtract 0.25 from each indicator; floor at 0.
	overlay.damage_indicators = {"top": 1.0, "bottom": 0.5, "left": 0.0, "right": 0.25}
	overlay._process(0.1)
	if not is_equal_approx(float(overlay.damage_indicators["top"]), 0.75):
		push_error("0.1s decay should drop top 1.0 -> 0.75; got %f" % float(overlay.damage_indicators["top"]))
		ok = false
	if not is_equal_approx(float(overlay.damage_indicators["bottom"]), 0.25):
		push_error("0.1s decay should drop bottom 0.5 -> 0.25; got %f" % float(overlay.damage_indicators["bottom"]))
		ok = false
	if float(overlay.damage_indicators["left"]) != 0.0:
		push_error("zero indicator should stay zero; got %f" % float(overlay.damage_indicators["left"]))
		ok = false
	if float(overlay.damage_indicators["right"]) != 0.0:
		push_error("right 0.25 with 0.25 decay should clamp to 0.0; got %f" % float(overlay.damage_indicators["right"]))
		ok = false
	print("Decay at 2.5/sec + clamp at 0.0: OK")

	# --- Full decay duration: 0.4s is enough to fully decay a 1.0 indicator ---
	overlay.damage_indicators = {"top": 1.0, "bottom": 0.0, "left": 0.0, "right": 0.0}
	overlay._process(0.41)
	if float(overlay.damage_indicators["top"]) != 0.0:
		push_error("after 0.41s decay, top should clamp to 0; got %f" % float(overlay.damage_indicators["top"]))
		ok = false
	print("Full decay clamps to 0.0: OK")

	# --- Null camera is a no-op ---
	_reset_indicators(overlay)
	overlay.show_damage_indicator(Vector3(0, 0, -10), Vector3.ZERO, null)
	for dir in ["top", "bottom", "left", "right"]:
		if float(overlay.damage_indicators[dir]) != 0.0:
			push_error("null camera should be no-op, but %s = %f" % [dir, float(overlay.damage_indicators[dir])])
			ok = false
	print("Null camera no-op: OK")

	# --- Zero-distance (attacker = player) is a no-op; prevents NaN ---
	_reset_indicators(overlay)
	overlay.show_damage_indicator(Vector3.ZERO, Vector3.ZERO, cam)
	for dir in ["top", "bottom", "left", "right"]:
		if float(overlay.damage_indicators[dir]) != 0.0:
			push_error("zero-distance attacker should be no-op, but %s = %f" % [dir, float(overlay.damage_indicators[dir])])
			ok = false
	print("Zero-distance attacker no-op: OK")

	overlay.queue_free()

	# --- SandboxHUD forwarding: hud.show_damage_indicator -> overlay ---
	# Hit marker style: the HUD's own show_damage_indicator must reach the
	# inner HUDOverlay and set its indicators. No independent state on HUD.
	var hud: SandboxHUD = SandboxHUD.new()
	get_root().add_child(hud)
	hud._ready()
	if hud.overlay == null:
		push_error("SandboxHUD missing overlay child")
		ok = false
	else:
		hud.show_damage_indicator(Vector3(0, 0, -10), Vector3.ZERO, cam)
		if float(hud.overlay.damage_indicators["top"]) != 1.0:
			push_error("hud.show_damage_indicator did not forward: top=%f" % float(hud.overlay.damage_indicators["top"]))
			ok = false
		hud.show_damage_indicator(Vector3(-10, 0, 0), Vector3.ZERO, cam)
		if float(hud.overlay.damage_indicators["left"]) != 1.0:
			push_error("hud.show_damage_indicator did not forward left: %f" % float(hud.overlay.damage_indicators["left"]))
			ok = false
		print("SandboxHUD show_damage_indicator forwarding: OK")
	hud.queue_free()
	cam.queue_free()

	if ok:
		print("RESULT: PASS")
		quit(0)
	else:
		push_error("Damage indicator tests FAILED")
		quit(1)

func _reset_indicators(overlay: Control) -> void:
	overlay.damage_indicators = {"top": 0.0, "bottom": 0.0, "left": 0.0, "right": 0.0}
