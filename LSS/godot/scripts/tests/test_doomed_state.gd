extends SceneTree

# Covers the doomed state port (task #27):
#   - player_ship.gd & enemy_ship.gd: DOOMED_HEALTH_PCT / DOOMED_TIMER
#     constants, doomed latch on crossing threshold, doom_timer countdown,
#     is_doomed() accessor, _apply_doomed_death() fatal path.
#   - doomed_overlay.gd: vignette + banner visibility toggle, pulse animation.
#   - hud.gd: set_doomed_state() forwarding, layer order (doomed_overlay below
#     damage_overlay so damage flashes still pulse on top).
#   - Scoreboard STATUS column: three-way DEAD > DOOMED > ALIVE priority via
#     the main.gd _ship_status_label helper is not run here (it requires the
#     full Main scene); we verify the inputs feeding it (is_doomed values).

const PlayerShipScript = preload("res://scripts/player_ship.gd")
const EnemyShipScript = preload("res://scripts/enemy_ship.gd")
const DoomedOverlayScript = preload("res://scripts/doomed_overlay.gd")
const SandboxHUD = preload("res://scripts/hud.gd")

func _init() -> void:
	var ok := true

	# Ensure input map actions exist for PlayerShip._ready() / settings reads.
	var GameData := load("res://scripts/game_data.gd")
	GameData.ensure_input_map()

	# --- PlayerShip: doomed entry threshold ---
	var player: PlayerShip = PlayerShipScript.new()
	get_root().add_child(player)
	player._ready()

	if player.is_doomed():
		push_error("Fresh player should not be doomed")
		ok = false
	if player.doom_timer != 0.0:
		push_error("Fresh player doom_timer should be 0 (got %f)" % player.doom_timer)
		ok = false

	# Damage just below the threshold: shield-only hit, should NOT doom.
	# ION chassis has max_shield large enough that a 200-damage hit stays in
	# shield; hull is untouched, so doomed must remain false.
	player.apply_damage(200.0, Vector3.ZERO, "SCORCH")
	if player.is_doomed():
		push_error("Shield-absorbed hit should not enter doomed state")
		ok = false

	# Drain shield, then hit hull down to 14% → expect doomed = true.
	# Use a huge single hit (health stays > 0 due to max_health headroom only
	# if we pick a shape; simpler to set shield/health directly and poke a
	# tiny damage to run the threshold check).
	player.shield = 0.0
	player.health = player.max_health * 0.16   # just above threshold
	player.apply_damage(player.max_health * 0.02, Vector3.ZERO, "SCORCH")
	# Now health ≈ 14% of max, doomed should latch.
	if not player.is_doomed():
		push_error("Player should be doomed below 15%% hull (health=%f max=%f)" % [player.health, player.max_health])
		ok = false
	var latched_timer := player.doom_timer
	if absf(latched_timer - PlayerShipScript.DOOMED_TIMER) > 0.01:
		push_error("doom_timer should start at DOOMED_TIMER (got %f expected %f)" % [latched_timer, PlayerShipScript.DOOMED_TIMER])
		ok = false

	# Further hits must NOT reset the timer; latch-on-entry only.
	player.apply_damage(10.0, Vector3.ZERO, "SCORCH")
	if player.doom_timer > latched_timer + 0.01:
		push_error("doom_timer should not reset on subsequent hits (got %f latched %f)" % [player.doom_timer, latched_timer])
		ok = false
	print("PLAYER_SHIP doomed entry + latch: OK (timer %.2f)" % player.doom_timer)

	# --- Countdown → fatal ---
	var destroyed_fired := [false]
	var killer_key := [""]
	player.destroyed.connect(func(killer: String, _victim: String) -> void:
		destroyed_fired[0] = true
		killer_key[0] = killer
	)
	# Simulate DOOMED_TIMER + epsilon of physics ticks. _physics_process runs
	# the countdown at the top when doomed = true, so we can invoke it
	# directly with a single large delta.
	player._physics_process(PlayerShipScript.DOOMED_TIMER + 0.1)
	if player.is_alive():
		push_error("Player should be dead after doom timer expires")
		ok = false
	if player.is_doomed():
		push_error("Player should clear doomed flag on death (is_doomed=%s)" % player.is_doomed())
		ok = false
	if not destroyed_fired[0]:
		push_error("destroyed signal must fire on doom-timer death")
		ok = false
	if killer_key[0] != "":
		push_error("doom-timer death should emit empty killer key (got %s)" % killer_key[0])
		ok = false
	print("PLAYER_SHIP doomed countdown → death: OK")

	# --- Respawn clears doomed ---
	player.reset_for_round(Vector3(0, 0, 720))
	if player.is_doomed() or player.doom_timer != 0.0 or not player.is_alive():
		push_error("reset_for_round should clear doomed state (doomed=%s timer=%f alive=%s)" % [player.is_doomed(), player.doom_timer, player.is_alive()])
		ok = false
	print("PLAYER_SHIP respawn clears doomed: OK")

	# --- EnemyShip symmetric behaviour ---
	var enemy: EnemyShip = EnemyShipScript.new()
	get_root().add_child(enemy)
	enemy._ready()
	enemy.apply_loadout("SCORCH")
	enemy.shield = 0.0
	enemy.health = enemy.max_health * 0.16
	enemy.apply_damage(enemy.max_health * 0.02, Vector3.ZERO, "ION")
	if not enemy.is_doomed():
		push_error("Enemy should be doomed below 15%% hull")
		ok = false

	# Enemy countdown path. Set match_state so the early-return for
	# non-playing state doesn't swallow the tick.
	enemy.set_match_state("playing")
	# Avoid the full physics path (which requires a target); invoke the
	# doomed countdown section by reaching into _physics_process behaviour
	# via direct timer decrement + _apply_doomed_death reflection.
	enemy.doom_timer = 0.0
	# Trigger the private death path via a near-zero timer plus _physics_process.
	# EnemyShip._physics_process guards on `target`, so we need to assign one.
	enemy.target = player   # doesn't matter that player is freshly respawned
	enemy._physics_process(0.1)
	if enemy.is_alive():
		push_error("Enemy should be dead after doom-timer expiry")
		ok = false
	print("ENEMY_SHIP doomed countdown: OK")

	# --- DoomedOverlay behaviour ---
	var overlay: DoomedOverlay = DoomedOverlayScript.new()
	get_root().add_child(overlay)
	overlay._ready()
	if overlay.visible:
		push_error("DoomedOverlay should start hidden")
		ok = false
	if overlay.is_active():
		push_error("DoomedOverlay should start inactive")
		ok = false

	overlay.set_active(true)
	if not overlay.visible:
		push_error("set_active(true) should make overlay visible")
		ok = false
	if not overlay.is_active():
		push_error("is_active() should report true after activation")
		ok = false

	# Pulse animation: alpha should oscillate between 0.5 and 1.0 over time.
	overlay._process(0.0)
	var min_alpha := overlay._warning_label.modulate.a
	overlay._process(0.2)   # halfway through first ramp
	var mid_alpha := overlay._warning_label.modulate.a
	if mid_alpha <= min_alpha:
		push_error("DoomedOverlay pulse should rise over time (start=%f mid=%f)" % [min_alpha, mid_alpha])
		ok = false
	if mid_alpha > 1.001 or mid_alpha < 0.4:
		push_error("DoomedOverlay pulse alpha out of [0.5,1.0] range: %f" % mid_alpha)
		ok = false

	overlay.set_active(false)
	if overlay.visible or overlay.is_active():
		push_error("set_active(false) should hide and deactivate overlay")
		ok = false
	print("DOOMED_OVERLAY visibility + pulse: OK")

	# --- HUD forwarding + layer order ---
	var hud := SandboxHUD.new()
	get_root().add_child(hud)
	hud._ready()
	if hud.doomed_overlay == null:
		push_error("HUD did not create doomed_overlay child")
		ok = false
	# Ensure _ready fired for all children (SceneTree test quirk).
	if hud.doomed_overlay != null:
		hud.doomed_overlay._ready()
	if hud.damage_overlay != null:
		hud.damage_overlay._ready()
	if hud.banner != null:
		hud.banner._ready()

	if hud.doomed_overlay != null and hud.doomed_overlay.is_active():
		push_error("HUD doomed_overlay should start inactive")
		ok = false

	hud.set_doomed_state(true)
	if hud.doomed_overlay != null and not hud.doomed_overlay.is_active():
		push_error("HUD.set_doomed_state did not activate overlay")
		ok = false
	hud.set_doomed_state(false)
	if hud.doomed_overlay != null and hud.doomed_overlay.is_active():
		push_error("HUD.set_doomed_state(false) did not deactivate overlay")
		ok = false

	# Layer order: doomed_overlay below damage_overlay below banner.
	if hud.doomed_overlay != null and hud.damage_overlay != null:
		var doomed_idx := hud.doomed_overlay.get_index()
		var damage_idx := hud.damage_overlay.get_index()
		if doomed_idx >= damage_idx:
			push_error("Doomed overlay should draw below damage overlay (doomed=%d damage=%d)" % [doomed_idx, damage_idx])
			ok = false
		if hud.banner != null and damage_idx >= hud.banner.get_index():
			push_error("Damage overlay should draw below banner (damage=%d banner=%d)" % [damage_idx, hud.banner.get_index()])
			ok = false
		print("HUD layer order (doomed<damage<banner): OK (doomed=%d damage=%d banner=%d)" % [doomed_idx, damage_idx, hud.banner.get_index()])

	print("SANDBOX_HUD doomed forwarding: OK")

	if ok:
		print("RESULT: PASS")
		quit(0)
	else:
		push_error("Doomed-state tests FAILED")
		quit(1)
