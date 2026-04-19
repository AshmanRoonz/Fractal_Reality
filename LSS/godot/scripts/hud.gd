class_name SandboxHUD
extends CanvasLayer

const PlayerShip = preload("res://scripts/player_ship.gd")
const HUDOverlay = preload("res://scripts/hud_overlay.gd")
const BannerOverlayScript = preload("res://scripts/banner_overlay.gd")
const KillFeedOverlayScript = preload("res://scripts/kill_feed_overlay.gd")
const ScoreboardOverlayScript = preload("res://scripts/scoreboard_overlay.gd")
const DamageOverlayScript = preload("res://scripts/damage_overlay.gd")
const DoomedOverlayScript = preload("res://scripts/doomed_overlay.gd")
const CinematicOverlayScript = preload("res://scripts/cinematic_overlay.gd")

var overlay: Control
var banner: BannerOverlay
var kill_feed: KillFeedOverlay
var scoreboard: ScoreboardOverlay
var damage_overlay: DamageOverlay
var doomed_overlay: DoomedOverlay
var cinematic: CinematicOverlay

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
	# Cinematic overlay bundles the eight transient widgets (hit marker, kill
	# marker, killstreak, medals, countdown, ability flash, respawn, exec
	# prompt). Drawn above the damage overlay so flashes don't tint the
	# player's feedback, but below the kill feed so stacked medals never
	# obscure who killed whom.
	cinematic = CinematicOverlayScript.new()
	add_child(cinematic)
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

# Light the edge-of-screen directional damage arrow closest to the attacker.
# Thin pass-through to HUDOverlay.show_damage_indicator; see HTML 10294-10325.
# Safe to call with any combination of nulls; HUDOverlay guards internally.
func show_damage_indicator(attacker_pos: Vector3, player_pos: Vector3, cam: Camera3D) -> void:
	if overlay != null and overlay.has_method("show_damage_indicator"):
		overlay.call("show_damage_indicator", attacker_pos, player_pos, cam)

# Show / hide the persistent doomed vignette + "HULL CRITICAL" banner.
# Called every frame from main.gd with player.is_doomed(); DoomedOverlay
# internally no-ops when the state hasn't changed.
func set_doomed_state(active: bool) -> void:
	if doomed_overlay != null:
		doomed_overlay.set_active(active)

# --- Cinematic overlay forwarding -----------------------------------------
# main.gd wires these into the game loop; thin wrappers keep consumers from
# reaching into `cinematic` directly (so we can swap the implementation
# without touching the call sites).

func show_hit_marker() -> void:
	if cinematic != null:
		cinematic.show_hit_marker()

func show_kill_marker() -> void:
	if cinematic != null:
		cinematic.show_kill_marker()

func show_killstreak(count: int) -> void:
	if cinematic != null:
		cinematic.show_killstreak(count)

func show_medal(type_id: String) -> void:
	if cinematic != null:
		cinematic.show_medal(type_id)

func show_countdown(n: Variant, label: String = "") -> void:
	if cinematic != null:
		cinematic.show_countdown(n, label)

func show_ability_flash(ability_name: String, color: Color = Color(0, 0, 0, 0)) -> void:
	if cinematic != null:
		cinematic.show_ability_flash(ability_name, color)

func show_respawn(killer_name: String = "") -> void:
	if cinematic != null:
		cinematic.show_respawn(killer_name)

func hide_respawn() -> void:
	if cinematic != null:
		cinematic.hide_respawn()

func set_execution_prompt(visible: bool) -> void:
	if cinematic != null:
		cinematic.set_execution_prompt(visible)
