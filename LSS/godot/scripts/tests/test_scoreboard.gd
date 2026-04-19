extends SceneTree

# Covers the scoreboard overlay (scripts/scoreboard_overlay.gd) and its
# wiring through SandboxHUD (scripts/hud.gd). Mirrors the shape of
# test_overlays.gd; does not exercise the full Main scene.

const ScoreboardOverlayScript = preload("res://scripts/scoreboard_overlay.gd")
const SandboxHUD = preload("res://scripts/hud.gd")

func _init() -> void:
	var ok := true

	# --- Direct scoreboard overlay behaviour ---
	var board := ScoreboardOverlayScript.new()
	get_root().add_child(board)
	# SceneTree tests don't auto-fire _ready(); panel + rows_vbox are built
	# there, so we invoke it manually to match in-tree behaviour.
	board._ready()
	if board.visible:
		push_error("Scoreboard should be hidden by default")
		ok = false

	var rows := [
		{"name": "YOU (ION)", "status": "ALIVE", "health": 7350, "shield": 2460, "team": 0, "is_player": true},
		{"name": "SCORCH", "status": "DEAD", "health": 0, "shield": 0, "team": 0, "is_player": false},
		{"name": "RONIN", "status": "ALIVE", "health": 1100, "shield": 0, "team": 1, "is_player": false},
		{"name": "TONE", "status": "ALIVE", "health": 8200, "shield": 4100, "team": 1, "is_player": false},
	]
	var match_info := {"score_a": 3, "score_b": 1, "kills": 4, "deaths": 1, "damage": 18432}
	board.update_rows(rows, match_info, "HOLD TAB / BACK")
	board.show_board()
	if not board.visible:
		push_error("show_board() did not flip visible to true")
		ok = false

	# Expect one team header per team (2) plus one row per ship (4) = 6 rows_vbox children.
	var row_count := board._rows_vbox.get_child_count()
	if row_count != 6:
		push_error("Scoreboard row count wrong: got %d expected 6" % row_count)
		ok = false

	# Footer label should carry K/D/DMG formatted.
	if board._footer_label.text.find("K: 4") == -1 or board._footer_label.text.find("DMG: 18432") == -1:
		push_error("Footer label missing K/D/DMG: '%s'" % board._footer_label.text)
		ok = false

	if not board._prompt_label.visible or board._prompt_label.text.find("TAB") == -1:
		push_error("Prompt label not shown or wrong text: visible=%s text='%s'" % [str(board._prompt_label.visible), board._prompt_label.text])
		ok = false

	# Update with empty prompt should hide prompt row.
	board.update_rows(rows, match_info, "")
	if board._prompt_label.visible:
		push_error("Empty prompt should hide prompt label")
		ok = false

	board.hide_board()
	if board.visible:
		push_error("hide_board() did not flip visible to false")
		ok = false
	print("SCOREBOARD_OVERLAY direct: OK (rows=%d)" % row_count)

	# --- SandboxHUD forwarding ---
	var hud := SandboxHUD.new()
	get_root().add_child(hud)
	hud._ready()
	# hud._ready() creates scoreboard/banner/kill_feed as children, but their
	# own _ready() methods do not auto-fire in a SceneTree test. Call them
	# explicitly so panels + internal labels exist before we poke at them.
	if hud.scoreboard != null:
		hud.scoreboard._ready()
	if hud.banner != null:
		hud.banner._ready()
	if hud.kill_feed != null:
		hud.kill_feed._ready()
	if hud.scoreboard == null:
		push_error("SandboxHUD missing scoreboard child")
		ok = false
	if hud.is_scoreboard_visible():
		push_error("Scoreboard should start hidden via HUD API")
		ok = false

	hud.show_scoreboard(rows, match_info, "HOLD TAB")
	if not hud.is_scoreboard_visible():
		push_error("HUD.show_scoreboard did not make scoreboard visible")
		ok = false
	if hud.scoreboard._rows_vbox.get_child_count() != 6:
		push_error("HUD.show_scoreboard did not forward rows")
		ok = false

	hud.hide_scoreboard()
	if hud.is_scoreboard_visible():
		push_error("HUD.hide_scoreboard did not hide scoreboard")
		ok = false
	print("SANDBOX_HUD scoreboard forwarding: OK")

	# --- Layer order: scoreboard must sit below banner so VICTORY text draws on top ---
	var scoreboard_index := hud.scoreboard.get_index()
	var banner_index := hud.banner.get_index()
	if scoreboard_index >= banner_index:
		push_error("Scoreboard draws over banner (scoreboard idx=%d banner idx=%d)" % [scoreboard_index, banner_index])
		ok = false
	print("HUD layer order (scoreboard below banner): OK (scoreboard=%d banner=%d)" % [scoreboard_index, banner_index])

	if ok:
		print("RESULT: PASS")
		quit(0)
	else:
		push_error("Scoreboard tests FAILED")
		quit(1)
