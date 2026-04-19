class_name SandboxHUD
extends CanvasLayer

const PlayerShip = preload("res://scripts/player_ship.gd")
const HUDOverlay = preload("res://scripts/hud_overlay.gd")
const BannerOverlayScript = preload("res://scripts/banner_overlay.gd")
const KillFeedOverlayScript = preload("res://scripts/kill_feed_overlay.gd")
const ScoreboardOverlayScript = preload("res://scripts/scoreboard_overlay.gd")
const DamageOverlayScript = preload("res://scripts/damage_overlay.gd")
const DoomedOverlayScript = preload("res://scripts/doomed_overlay.gd")

var overlay: Control
var banner: BannerOverlay
var kill_feed: KillFeedOverlay
var scoreboard: ScoreboardOverlay
var damage_overlay: DamageOverlay
var doomed_overlay: DoomedOverlay

func _ready() -> void:
	layer = 1
	overlay = HUDOverlay.new()
	add_child(overlay)
	# Doomed vignette sits between the base HUD and the damage overlay: it
	# needs to colour the base readouts red while letting a hit flash pulse
	# on top (damage_overlay draws the CA on a higher child index).
	doomed_overlay = DoomedOverlayScript.new()
	add_child(doomed_overlay)
	# Damage overlay draws above the base HUD + doomed vignette but below
	# everything else, so the red flash + CA pulse don't tint the kill feed /
	# banner / scoreboard.
	damage_overlay = DamageOverlayScript.new()
	add_child(damage_overlay)
	# Kill feed draws above the base HUD (top-right rolling list).
	kill_feed = KillFeedOverlayScript.new()
	add_child(kill_feed)
	# Scoreboard sits above the kill feed but below the banner; it anchors
	# center-screen and is hidden until the player holds Tab / Back or the
	# match ends.
	scoreboard = ScoreboardOverlayScript.new()
	add_child(scoreboard)
	# Banner draws above all (round-transition text with fade animation).
	banner = BannerOverlayScript.new()
	add_child(banner)

func configure_context(arena_map: Node, enemies: Array) -> void:
	if overlay != null and overlay.has_method("configure_context"):
		overlay.call("configure_context", arena_map, enemies)

func update_from_player(player: PlayerShip, alive_targets: int, match_info: Dictionary = {}) -> void:
	if overlay != null and overlay.has_method("set_state"):
		overlay.call("set_state", player, alive_targets, match_info)

func show_banner(text: String, subtext: String = "") -> void:
	if banner != null:
		banner.show_banner(text, subtext)

func add_kill_feed_entry(killer: String, victim: String) -> void:
	if kill_feed != null:
		kill_feed.add_entry(killer, victim)

func show_scoreboard(rows: Array, match_info: Dictionary, prompt: String = "") -> void:
	if scoreboard == null:
		return
	scoreboard.update_rows(rows, match_info, prompt)
	scoreboard.show_board()

func hide_scoreboard() -> void:
	if scoreboard != null:
		scoreboard.hide_board()

func is_scoreboard_visible() -> bool:
	return scoreboard != null and scoreboard.visible

# Intensity 0..1; typically `amount / max_health`. Triggers a 0.45s red
# radial vignette + chromatic aberration pulse above the base HUD.
func flash_damage(intensity: float) -> void:
	if damage_overlay != null:
		damage_overlay.flash(intensity)

# Show / hide the persistent doomed vignette + "HULL CRITICAL" banner.
# Called every frame from main.gd with player.is_doomed(); DoomedOverlay
# internally no-ops when the state hasn't changed.
func set_doomed_state(active: bool) -> void:
	if doomed_overlay != null:
		doomed_overlay.set_active(active)
