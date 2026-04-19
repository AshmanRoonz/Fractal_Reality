extends SceneTree

const BannerOverlayScript = preload("res://scripts/banner_overlay.gd")
const KillFeedOverlayScript = preload("res://scripts/kill_feed_overlay.gd")
const SandboxHUD = preload("res://scripts/hud.gd")

func _init() -> void:
	var ok := true

	# --- Kill feed basic behaviour ---
	var feed := KillFeedOverlayScript.new()
	get_root().add_child(feed)
	feed.add_entry("You", "SCORCH")
	feed.add_entry("RONIN", "You")
	feed.add_entry("TONE", "SCORCH")
	if feed._entries.size() != 3:
		push_error("Kill feed did not accumulate entries: got %d" % feed._entries.size())
		ok = false

	# Feed cap: push 10 entries, expect at most 5 (the HTML cap)
	for i in range(10):
		feed.add_entry("A%d" % i, "B%d" % i)
	if feed._entries.size() != KillFeedOverlayScript.MAX_ENTRIES:
		push_error("Kill feed cap broken: got %d expected %d" % [feed._entries.size(), KillFeedOverlayScript.MAX_ENTRIES])
		ok = false

	# Simulate a long delta to expire everything (9 seconds > 8s lifetime)
	feed._process(9.0)
	if feed._entries.size() != 0:
		push_error("Kill feed did not expire all entries after 9s: got %d" % feed._entries.size())
		ok = false
	print("KILL FEED expire + cap: OK (final size %d)" % feed._entries.size())

	# --- Banner basic behaviour ---
	var banner := BannerOverlayScript.new()
	get_root().add_child(banner)
	banner.show_banner("FIGHT", "")
	if banner._timer < 0.0:
		push_error("Banner did not enter active state after show_banner")
		ok = false
	# Tick past the full 3s animation
	banner._process(BannerOverlayScript.TOTAL_DURATION + 0.1)
	if banner._timer >= 0.0:
		push_error("Banner did not return to idle after animation: timer=%f" % banner._timer)
		ok = false
	print("BANNER animate + idle-after: OK")

	# --- SandboxHUD wiring ---
	var hud := SandboxHUD.new()
	get_root().add_child(hud)
	# In a SceneTree-based test, _ready() does not auto-fire; invoke it
	# manually so the HUD installs its banner / kill_feed children.
	hud._ready()
	if hud.banner == null or hud.kill_feed == null:
		push_error("SandboxHUD missing banner/kill_feed children")
		ok = false
	hud.show_banner("ROUND OVER", "FLEET A: 1  FLEET B: 0")
	hud.add_kill_feed_entry("You", "SCORCH")
	if hud.banner._timer < 0.0:
		push_error("SandboxHUD.show_banner did not activate banner")
		ok = false
	if hud.kill_feed._entries.size() != 1:
		push_error("SandboxHUD.add_kill_feed_entry did not push into feed")
		ok = false
	print("SANDBOX_HUD forwarding: OK (banner active, feed size %d)" % hud.kill_feed._entries.size())

	# --- Signal wiring: PlayerShip / EnemyShip emit destroyed on death ---
	# Use global class names registered via class_name (avoids load-inference issues).
	# InputMap needs to exist before PlayerShip / EnemyShip _ready()
	var GameData := load("res://scripts/game_data.gd")
	GameData.ensure_input_map()
	var player: PlayerShip = PlayerShip.new()
	get_root().add_child(player)
	# Force _ready so visuals child is created (apply_damage calls into it on death).
	player._ready()
	var saw_player_death := [false]
	var captured_killer := [""]
	player.destroyed.connect(func(killer: String, _victim: String) -> void:
		saw_player_death[0] = true
		captured_killer[0] = killer
	)
	# Force-kill by dumping massive damage; shields absorb first, then health
	player.apply_damage(99999.0, Vector3.ZERO, "SCORCH")
	if not saw_player_death[0]:
		push_error("PlayerShip destroyed signal did not fire")
		ok = false
	if captured_killer[0] != "SCORCH":
		push_error("PlayerShip destroyed signal carried wrong killer: '%s'" % captured_killer[0])
		ok = false
	print("PLAYER_SHIP destroyed signal: OK (killer='%s')" % captured_killer[0])

	var enemy: EnemyShip = EnemyShip.new()
	get_root().add_child(enemy)
	enemy._ready()
	enemy.configure("SCORCH", player, Vector3.ZERO, 0.0)
	var saw_enemy_death := [false]
	var enemy_killer := [""]
	var enemy_victim := [""]
	enemy.destroyed.connect(func(killer: String, victim: String) -> void:
		saw_enemy_death[0] = true
		enemy_killer[0] = killer
		enemy_victim[0] = victim
	)
	enemy.apply_damage(99999.0, Vector3.ZERO, "ION")
	if not saw_enemy_death[0]:
		push_error("EnemyShip destroyed signal did not fire")
		ok = false
	if enemy_killer[0] != "ION" or enemy_victim[0] != "SCORCH":
		push_error("EnemyShip destroyed signal wrong args: killer='%s' victim='%s'" % [enemy_killer[0], enemy_victim[0]])
		ok = false
	print("ENEMY_SHIP destroyed signal: OK (killer='%s' victim='%s')" % [enemy_killer[0], enemy_victim[0]])

	if ok:
		print("RESULT: PASS")
		quit(0)
	else:
		push_error("Overlay tests FAILED")
		quit(1)
