extends Node3D

const GameData = preload("res://scripts/game_data.gd")
const PlayerShip = preload("res://scripts/player_ship.gd")
const SandboxHUD = preload("res://scripts/hud.gd")
const TracerPool = preload("res://scripts/tracer_pool.gd")
const EnemyShip = preload("res://scripts/enemy_ship.gd")
const ArenaMap = preload("res://scripts/arena_map.gd")
const Settings = preload("res://scripts/settings.gd")
const SETTINGS_OVERLAY_SCENE := preload("res://scenes/SettingsOverlay.tscn")

const ROUND_TIME := 180.0
const WARMUP_TIME := 5.0
const ROUND_END_TIME := 5.0
const ROUNDS_TO_WIN := 4
const PLAYER_SPAWN := Vector3(0, 0, 720)

var player: PlayerShip
var hud: SandboxHUD
var projectile_root: Node3D
var effect_root: Node3D
var arena_map: ArenaMap

var tracer_glow: TracerPool
var tracer_beam: TracerPool
var tracer_core: TracerPool

var enemies: Array[EnemyShip] = []
var projectiles: Array = []
var world_effects: Array = []
var tracked_enemy: EnemyShip = null
var enemy_spawn_positions: Array[Vector3] = []
var player_spawn_point := PLAYER_SPAWN
var match_state := "warmup"
var round_timer := ROUND_TIME
var warmup_timer := WARMUP_TIME
var round_end_timer := ROUND_END_TIME
var score_a := 0
var score_b := 0
var current_round := 1

# Scoreboard / match summary tallies. Player-side only; damage tracking is
# coarse (sum of amounts the player dealt to enemies, ignoring shield-vs-hull).
var player_kills := 0
var player_deaths := 0
var player_damage_dealt := 0.0
# True while Tab / gamepad Back is held during a round, OR permanently after
# match_end (so the final standings stay visible under the VICTORY banner).
var _scoreboard_held := false
var _scoreboard_pinned := false

const MAIN_MENU_SCENE := "res://scenes/MainMenu.tscn"

var _settings_overlay: SettingsOverlay = null

func _ready() -> void:
	GameData.ensure_input_map()
	# Load persisted settings and push their bindings into the live InputMap.
	# ensure_input_map() must run first so every action exists before
	# Settings.apply_to_input_map() rewires the JoyButton events.
	Settings.load_from_disk()
	randomize()
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

	_build_environment()

	arena_map = ArenaMap.new()
	arena_map.name = "ArenaMap"
	add_child(arena_map)
	# Read selected_map_key (set by MainMenu); default "hourglass" keeps direct
	# scene runs working when Main.tscn is launched without the menu flow.
	arena_map.build_map(String(GameData.selected_map_key))

	effect_root = Node3D.new()
	effect_root.name = "Effects"
	add_child(effect_root)

	tracer_glow = TracerPool.new()
	tracer_glow.name = "TracerGlow"
	effect_root.add_child(tracer_glow)
	tracer_glow.configure(180, 0.24)

	tracer_beam = TracerPool.new()
	tracer_beam.name = "TracerBeam"
	effect_root.add_child(tracer_beam)
	tracer_beam.configure(180, 0.88)

	tracer_core = TracerPool.new()
	tracer_core.name = "TracerCore"
	effect_root.add_child(tracer_core)
	tracer_core.configure(180, 1.0)

	projectile_root = Node3D.new()
	projectile_root.name = "Projectiles"
	add_child(projectile_root)

	player = PlayerShip.new()
	add_child(player)
	player.global_position = arena_map.get_spawn_point("A", 30.0)
	player.set_arena_map(arena_map)
	player.primary_fired.connect(_on_primary_fired)
	player.ability_triggered.connect(_on_ability_triggered)
	player.core_triggered.connect(_on_core_triggered)
	player.destroyed.connect(_on_player_destroyed)
	player.damage_taken.connect(_on_player_damage_taken)

	# Apply the loadout chosen in MainMenu (defaults to "ION" when launched
	# directly without the menu).
	var selected_key := String(GameData.selected_loadout_key)
	var loadout_keys := GameData.get_loadout_keys()
	var selected_idx := loadout_keys.find(selected_key)
	if selected_idx >= 0:
		player.set_loadout_by_index(selected_idx)

	hud = SandboxHUD.new()
	add_child(hud)

	_spawn_enemies()
	hud.configure_context(arena_map, enemies)
	_start_match()

func _unhandled_input(event: InputEvent) -> void:
	# ESC opens the settings overlay (which pauses the tree and releases
	# the pointer); closing the overlay restores mouse capture.
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode == KEY_ESCAPE:
		_open_settings_overlay()
		return
	elif event is InputEventJoypadButton and event.pressed and event.button_index == JOY_BUTTON_START:
		_open_settings_overlay()
		return
	elif event is InputEventMouseButton and event.pressed and Input.get_mouse_mode() != Input.MOUSE_MODE_CAPTURED:
		# Click anywhere to re-capture if the user tabbed out.
		Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

	# Tab (keyboard) / Back (gamepad) holds the scoreboard (HTML lines
	# 11296-11307). Hold-to-show: keyup hides it unless pinned by match_end.
	if event is InputEventKey and event.physical_keycode == KEY_TAB and not event.echo:
		_scoreboard_held = event.pressed
		_refresh_scoreboard_visibility()
	elif event is InputEventJoypadButton and event.button_index == JOY_BUTTON_BACK:
		_scoreboard_held = event.pressed
		_refresh_scoreboard_visibility()

	# After match_end: Enter / gamepad A returns to the main menu.
	if match_state == "match_end":
		var return_pressed := false
		if event is InputEventKey and event.pressed and not event.echo:
			if event.physical_keycode == KEY_ENTER or event.physical_keycode == KEY_KP_ENTER:
				return_pressed = true
		elif event is InputEventJoypadButton and event.pressed and event.button_index == JOY_BUTTON_A:
			return_pressed = true
		if return_pressed:
			_return_to_main_menu()
			return

func _refresh_scoreboard_visibility() -> void:
	if hud == null:
		return
	if _scoreboard_held or _scoreboard_pinned:
		_refresh_scoreboard_contents()
	else:
		hud.hide_scoreboard()

func _refresh_scoreboard_contents() -> void:
	if hud == null or player == null:
		return
	var rows := _collect_scoreboard_rows()
	var match_info := {
		"score_a": score_a,
		"score_b": score_b,
		"kills": player_kills,
		"deaths": player_deaths,
		"damage": int(player_damage_dealt),
	}
	var prompt := ""
	if match_state == "match_end":
		prompt = "Press ENTER / A to return to main menu"
	hud.show_scoreboard(rows, match_info, prompt)

func _collect_scoreboard_rows() -> Array:
	var rows: Array = []
	# Player always appears as the first row of Team A.
	var player_loadout := GameData.get_loadout(player.loadout_key)
	var player_name := "YOU (%s)" % String(player_loadout.get("name", player.loadout_key))
	rows.append({
		"name": player_name,
		"status": _ship_status_label(player.is_alive(), player.is_doomed()),
		"health": player.health,
		"shield": player.shield,
		"team": 0,
		"is_player": true,
	})
	# Enemies: HTML runs solo+bots with all bots on Team B; mirror that here.
	for enemy in enemies:
		if not is_instance_valid(enemy):
			continue
		var enemy_loadout := GameData.get_loadout(enemy.loadout_key)
		rows.append({
			"name": String(enemy_loadout.get("name", enemy.loadout_key)),
			"status": _ship_status_label(enemy.is_alive(), enemy.is_doomed()),
			"health": max(0.0, enemy.health),
			"shield": max(0.0, enemy.shield),
			"team": 1,
			"is_player": false,
		})
	return rows

# Three-way status matching HTML lines 11271-11286: DEAD takes precedence over
# DOOMED, and DOOMED over ALIVE. is_doomed() already AND's with alive on the
# ship side, so this just enforces the priority explicitly.
func _ship_status_label(is_alive: bool, is_doomed: bool) -> String:
	if not is_alive:
		return "DEAD"
	if is_doomed:
		return "DOOMED"
	return "ALIVE"

func _return_to_main_menu() -> void:
	# Unpin the scoreboard so it doesn't flash for a frame on MainMenu.
	_scoreboard_pinned = false
	_scoreboard_held = false
	if hud != null:
		hud.hide_scoreboard()
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	get_tree().change_scene_to_file(MAIN_MENU_SCENE)

func _open_settings_overlay() -> void:
	if is_instance_valid(_settings_overlay):
		return
	_settings_overlay = SETTINGS_OVERLAY_SCENE.instantiate() as SettingsOverlay
	add_child(_settings_overlay)
	_settings_overlay.closed.connect(_on_settings_overlay_closed)

func _on_settings_overlay_closed() -> void:
	_settings_overlay = null

func _process(_delta: float) -> void:
	hud.update_from_player(player, _count_alive_enemies(), _get_match_info())
	# Drive the persistent doomed vignette + "HULL CRITICAL" banner from the
	# ship's latched flag. Cheap no-op when state hasn't changed (DoomedOverlay
	# early-returns when set_active is called with the same value).
	hud.set_doomed_state(player.is_doomed())
	# Keep the scoreboard's stats fresh while it's on screen so health/shield
	# values follow combat in real time (mirrors HTML updateScoreboard being
	# called every keydown; we poll at frame rate while visible).
	if hud.is_scoreboard_visible():
		_refresh_scoreboard_contents()

func _physics_process(delta: float) -> void:
	_update_round_system(delta)
	_update_projectiles(delta)
	_update_world_effects(delta)

	if tracked_enemy and (not is_instance_valid(tracked_enemy) or not tracked_enemy.is_alive()):
		tracked_enemy = null

func _build_environment() -> void:
	# Mirrors last_ship_sailing.html lines 1553-1847:
	# scene.fog = FogExp2(0x0a0520, 0.000015), renderer clear 0x0a0520,
	# AmbientLight(0x445577, 0.8), DirectionalLight(0xffeedd, 1.2) key,
	# DirectionalLight(0x8888ff, 0.4) fill, PointLight(0x6699ff, 0.5, 12000) origin,
	# HemisphereLight(0x6688cc, 0x224466, 0.6), bloom 0.85, ACES tonemap, exposure 1.05.
	var fog_tint := Color(0.039, 0.020, 0.125, 1.0)  # 0x0a0520 deep purple-black
	var environment := Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = fog_tint
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color(0.267, 0.333, 0.467, 1.0)  # 0x445577
	environment.ambient_light_energy = 0.8
	environment.ambient_light_sky_contribution = 0.0

	# Volumetric-style exponential fog tuned to Godot's world scale (MAP_UNIT=150)
	environment.fog_enabled = true
	environment.fog_light_color = fog_tint
	environment.fog_light_energy = 1.0
	environment.fog_density = 0.0009
	environment.fog_sky_affect = 1.0
	environment.fog_aerial_perspective = 0.25

	# ACES filmic tonemap + matching exposure
	environment.tonemap_mode = Environment.TONE_MAPPER_ACES
	environment.tonemap_exposure = 1.05
	environment.tonemap_white = 6.0

	# Bloom matches the HTML post-FX (strength 0.85, threshold 0.55, soft knee 0.35)
	environment.glow_enabled = true
	environment.glow_intensity = 0.85
	environment.glow_strength = 1.1
	environment.glow_bloom = 0.22
	environment.glow_blend_mode = Environment.GLOW_BLEND_MODE_ADDITIVE
	environment.glow_hdr_threshold = 0.55
	environment.glow_hdr_scale = 2.0

	# Subtle grade matching the HTML shadow-cool / highlight-warm mix
	environment.adjustment_enabled = true
	environment.adjustment_brightness = 1.0
	environment.adjustment_contrast = 1.04
	environment.adjustment_saturation = 1.05

	var world_environment := WorldEnvironment.new()
	world_environment.name = "WorldEnvironment"
	world_environment.environment = environment
	add_child(world_environment)

	# Key sun light; warm (0xffeedd), strong
	var sun := DirectionalLight3D.new()
	sun.name = "KeyLight"
	sun.light_color = Color(1.0, 0.933, 0.867, 1.0)
	sun.light_energy = 1.2
	sun.shadow_enabled = false
	sun.look_at_from_position(Vector3(1000, 3000, 1500), Vector3.ZERO, Vector3.UP)
	add_child(sun)

	# Cool fill from below (0x8888ff, 0.4), casting upward
	var fill_directional := DirectionalLight3D.new()
	fill_directional.name = "FillLight"
	fill_directional.light_color = Color(0.533, 0.533, 1.0, 1.0)
	fill_directional.light_energy = 0.4
	fill_directional.shadow_enabled = false
	fill_directional.look_at_from_position(Vector3(-500, -1000, -500), Vector3.ZERO, Vector3.UP)
	add_child(fill_directional)

	# Hemisphere stand-in: warm top-down + cool bottom-up omni pair (0.6 mix)
	var hemi_up := OmniLight3D.new()
	hemi_up.name = "HemiUp"
	hemi_up.light_color = Color(0.400, 0.533, 0.800, 1.0)  # 0x6688cc sky color
	hemi_up.light_energy = 0.45
	hemi_up.omni_range = 14000.0
	hemi_up.omni_attenuation = 0.6
	hemi_up.position = Vector3(0, 4000, 0)
	add_child(hemi_up)

	var hemi_down := OmniLight3D.new()
	hemi_down.name = "HemiDown"
	hemi_down.light_color = Color(0.133, 0.267, 0.400, 1.0)  # 0x224466 ground color
	hemi_down.light_energy = 0.35
	hemi_down.omni_range = 14000.0
	hemi_down.omni_attenuation = 0.6
	hemi_down.position = Vector3(0, -4000, 0)
	add_child(hemi_down)

	# Origin accent point light (0x6699ff, 0.5 intensity, range 12000)
	var core_point := OmniLight3D.new()
	core_point.name = "CoreAccent"
	core_point.light_color = Color(0.400, 0.600, 1.0, 1.0)
	core_point.light_energy = 0.5
	core_point.omni_range = 12000.0
	core_point.omni_attenuation = 0.8
	core_point.position = Vector3(0, 500, 0)
	add_child(core_point)

	_build_starfield()

func _build_starfield() -> void:
	# 4000 stars, ±10000 per axis, six-color palette (HTML lines 1851-1876).
	var palette := [
		Color(1.00, 0.90, 0.70, 1.0),
		Color(0.70, 0.80, 1.00, 1.0),
		Color(1.00, 0.60, 0.80, 1.0),
		Color(0.60, 1.00, 0.80, 1.0),
		Color(1.00, 1.00, 0.50, 1.0),
		Color(0.80, 0.70, 1.00, 1.0)
	]

	var quad := QuadMesh.new()
	quad.size = Vector2(12.0, 12.0)

	var star_material := StandardMaterial3D.new()
	star_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	star_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	star_material.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	star_material.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	star_material.billboard_keep_scale = true
	star_material.albedo_color = Color(1, 1, 1, 0.9)
	star_material.vertex_color_use_as_albedo = true
	star_material.disable_receive_shadows = true
	star_material.disable_fog = true
	star_material.no_depth_test = false
	star_material.cull_mode = BaseMaterial3D.CULL_DISABLED
	quad.material = star_material

	var multimesh := MultiMesh.new()
	multimesh.transform_format = MultiMesh.TRANSFORM_3D
	multimesh.use_colors = true
	multimesh.mesh = quad

	var star_count := 4000
	multimesh.instance_count = star_count

	var star_rng := RandomNumberGenerator.new()
	star_rng.seed = 0xA5701F7
	for index in range(star_count):
		var position := Vector3(
			star_rng.randf_range(-10000.0, 10000.0),
			star_rng.randf_range(-10000.0, 10000.0),
			star_rng.randf_range(-10000.0, 10000.0)
		)
		# Keep stars out of the playable volume so the HUD stays readable
		if position.length() < 3500.0:
			position = position.normalized() * 3500.0
		var transform := Transform3D(Basis.IDENTITY, position)
		# Random brightness variance for subtle twinkle-friendly appearance
		var brightness := star_rng.randf_range(0.55, 1.0)
		var palette_pick: Color = palette[star_rng.randi_range(0, palette.size() - 1)]
		var color := Color(palette_pick.r * brightness, palette_pick.g * brightness, palette_pick.b * brightness, 0.95)
		multimesh.set_instance_transform(index, transform)
		multimesh.set_instance_color(index, color)

	var star_node := MultiMeshInstance3D.new()
	star_node.name = "Starfield"
	star_node.multimesh = multimesh
	star_node.extra_cull_margin = 20000.0
	add_child(star_node)

func _spawn_enemies() -> void:
	var loadouts := ["SCORCH", "RONIN", "TONE"]

	for index in range(loadouts.size()):
		var enemy := EnemyShip.new()
		add_child(enemy)
		enemy.set_arena_map(arena_map)
		var spawn_position := arena_map.get_spawn_point("B", 180.0)
		enemy.configure(loadouts[index], player, spawn_position, float(index) * 0.75)
		enemy.primary_fired.connect(_on_primary_fired)
		enemy.ability_triggered.connect(_on_ability_triggered)
		enemy.core_triggered.connect(_on_core_triggered)
		enemy.destroyed.connect(_on_enemy_destroyed)
		enemies.append(enemy)

func _start_match() -> void:
	score_a = 0
	score_b = 0
	current_round = 1
	player_kills = 0
	player_deaths = 0
	player_damage_dealt = 0.0
	_scoreboard_pinned = false
	_scoreboard_held = false
	_begin_round()

func _begin_round() -> void:
	tracked_enemy = null
	round_timer = ROUND_TIME
	warmup_timer = WARMUP_TIME
	round_end_timer = ROUND_END_TIME
	_clear_transient_combat()
	player_spawn_point = arena_map.get_spawn_point("A", 120.0)
	player.reset_for_round(player_spawn_point)
	enemy_spawn_positions.clear()
	for enemy in enemies:
		var enemy_spawn := arena_map.get_spawn_point("B", 220.0)
		enemy_spawn_positions.append(enemy_spawn)
		enemy.spawn_point = enemy_spawn
		enemy.reset_for_round()
	_set_match_state("warmup")

func _update_round_system(delta: float) -> void:
	match match_state:
		"warmup":
			warmup_timer = maxf(0.0, warmup_timer - delta)
			if warmup_timer <= 0.0:
				round_timer = ROUND_TIME
				_set_match_state("playing")
		"playing":
			round_timer = maxf(0.0, round_timer - delta)
			var alive_a := 1 if player.is_alive() else 0
			var alive_b := _count_alive_enemies()
			if alive_b == 0 or round_timer <= 0.0:
				score_a += 1
				round_end_timer = ROUND_END_TIME
				_set_match_state("round_end")
			elif alive_a == 0:
				score_b += 1
				round_end_timer = ROUND_END_TIME
				_set_match_state("round_end")
		"round_end":
			round_end_timer = maxf(0.0, round_end_timer - delta)
			if round_end_timer <= 0.0:
				if score_a >= ROUNDS_TO_WIN or score_b >= ROUNDS_TO_WIN:
					_set_match_state("match_end")
				else:
					current_round += 1
					_begin_round()

func _set_match_state(new_state: String) -> void:
	var previous_state := match_state
	match_state = new_state
	if new_state != "playing":
		tracked_enemy = null
		_clear_transient_combat()
	player.set_match_state(new_state)
	for enemy in enemies:
		enemy.set_match_state(new_state)
	_fire_state_banner(previous_state, new_state)

func _fire_state_banner(previous_state: String, new_state: String) -> void:
	# Mirrors last_ship_sailing.html transitions at lines 7774-7808. We use
	# the HUD's banner overlay for every transition (HTML uses countdown()
	# for FIGHT and banner() for the others; here a single animated banner
	# handles all three cases).
	if hud == null:
		return
	match new_state:
		"playing":
			if previous_state == "warmup":
				hud.show_banner("FIGHT", "")
		"round_end":
			hud.show_banner("ROUND OVER", "FLEET A: %d  FLEET B: %d" % [score_a, score_b])
		"match_end":
			var winner := "FLEET A" if score_a >= ROUNDS_TO_WIN else "FLEET B"
			hud.show_banner("VICTORY", "%s WINS" % winner)
			# Pin the scoreboard so the final standings stay on screen after
			# the banner fades. Player hits ENTER / A to bounce back to
			# MainMenu (see _unhandled_input + _return_to_main_menu).
			_scoreboard_pinned = true
			_refresh_scoreboard_visibility()
		"warmup":
			# Only show round banner on subsequent rounds; the initial warmup
			# after match start is silent (matches HTML behaviour).
			if previous_state == "round_end":
				hud.show_banner("ROUND %d" % current_round, "")

func _on_player_destroyed(killer_loadout_key: String, _victim_loadout_key: String) -> void:
	var killer_name := _resolve_ship_name(killer_loadout_key)
	player_deaths += 1
	if hud != null:
		hud.add_kill_feed_entry(killer_name, "You")

# Cinematic damage feedback: red radial vignette + chromatic aberration pulse,
# intensity scaled by how hard we were hit relative to max health. Matches
# HTML Overlays.damageVignette(amount/player.maxHealth) (line 5682).
func _on_player_damage_taken(_amount: float, ratio: float) -> void:
	if hud != null:
		hud.flash_damage(ratio)

func _on_enemy_destroyed(killer_loadout_key: String, victim_loadout_key: String) -> void:
	# If the player scored this kill, attribute to "You" rather than the
	# player's ship name (matches HTML line 3435).
	var player_scored := (killer_loadout_key == player.loadout_key)
	if player_scored:
		player_kills += 1
	var killer_name := "You" if player_scored else _resolve_ship_name(killer_loadout_key)
	var victim_name := _resolve_ship_name(victim_loadout_key)
	if hud != null:
		hud.add_kill_feed_entry(killer_name, victim_name)

func _resolve_ship_name(loadout_key: String) -> String:
	if loadout_key.is_empty():
		return "UNKNOWN"
	var loadout := GameData.get_loadout(loadout_key)
	return String(loadout.get("name", loadout_key))

func _clear_transient_combat() -> void:
	for projectile in projectiles:
		var projectile_node: MeshInstance3D = projectile.get("node", null) as MeshInstance3D
		if projectile_node != null and is_instance_valid(projectile_node):
			projectile_node.queue_free()
	projectiles.clear()

	for effect in world_effects:
		var effect_node: Node = effect.get("node", null) as Node
		if effect_node != null and is_instance_valid(effect_node):
			effect_node.queue_free()
	world_effects.clear()

func _count_alive_enemies() -> int:
	var alive_enemies := 0
	for enemy in enemies:
		if enemy.is_alive():
			alive_enemies += 1
	return alive_enemies

func _get_match_info() -> Dictionary:
	var timer := round_timer
	if match_state == "warmup":
		timer = warmup_timer
	elif match_state == "round_end":
		timer = round_end_timer

	var state_label := "Warmup"
	if match_state == "playing":
		state_label = "Playing"
	elif match_state == "round_end":
		state_label = "Round Over"
	elif match_state == "match_end":
		state_label = "Match End"

	return {
		"state": match_state,
		"state_label": state_label,
		"timer": timer,
		"score_a": score_a,
		"score_b": score_b,
		"current_round": current_round,
		"map_name": arena_map.get_map_name() if arena_map else "Arena",
		"tracked_enemy": tracked_enemy
	}

func _on_primary_fired(origin: Vector3, direction: Vector3, loadout_key: String, weapon_data: Dictionary, source: Node3D, team: int) -> void:
	var signature: Dictionary = GameData.get_signature(loadout_key)
	var damage_scale := _get_actor_damage_multiplier(source)

	match String(weapon_data.get("mode", "hitscan")):
		"hitscan":
			_fire_hitscan(origin, direction, weapon_data, signature, loadout_key, team, damage_scale, source)
		"spread":
			var pellets := int(weapon_data.get("pellets", 8))
			var spread := float(weapon_data.get("spread", 0.06))
			for pellet in range(pellets):
				var shot_direction := (
					direction +
					Vector3(
						randf_range(-spread, spread),
						randf_range(-spread, spread),
						randf_range(-spread * 0.35, spread * 0.35)
					)
				).normalized()
				var pellet_scale := damage_scale * (1.0 if pellet == 0 else 0.55)
				_fire_hitscan(origin, shot_direction, weapon_data, signature, loadout_key, team, pellet_scale, source)
		"projectile":
			_spawn_projectile(origin, direction, weapon_data, signature, loadout_key, team, source, {})

func _on_ability_triggered(ability_id: String, loadout_key: String, source: Node3D, origin: Vector3, direction: Vector3, team: int) -> void:
	var signature := GameData.get_signature(loadout_key)
	var source_position := source.global_position if source else origin
	var damage_scale := _get_actor_damage_multiplier(source)
	match ability_id:
		"laser_shot":
			var weapon := {"damage": 2400.0, "range": 3600.0}
			_fire_hitscan(origin, direction, weapon, signature, loadout_key, team, damage_scale, source)
		"trip_wire":
			_spawn_mine(source_position + direction * 180.0, 210.0, 1.0, 12.0, 350.0 * damage_scale, team, loadout_key, signature, source)
		"firewall":
			_spawn_zone(source_position + direction * 170.0, 180.0, 4.5, 320.0 * damage_scale, team, signature, direction * 260.0, loadout_key, source)
		"incendiary_trap":
			_spawn_zone(source_position + direction * 260.0, 210.0, 8.0, 220.0 * damage_scale, team, signature, Vector3.ZERO, loadout_key, source)
		"cluster_missile":
			_spawn_projectile(origin, direction, {"damage": 800.0 * damage_scale, "range": 2600.0, "projectile_speed": 900.0}, signature, loadout_key, team, source, {
				"explode_radius": 130.0,
				"blast_damage": 520.0 * damage_scale,
				"cluster_count": 5,
				"cluster_damage": 180.0 * damage_scale
			})
		"tether_trap":
			_spawn_zone(source_position + direction * 220.0, 175.0, 5.0, 100.0 * damage_scale, team, signature, Vector3.ZERO, loadout_key, source)
		"arc_wave":
			_spawn_projectile(origin, direction, {"damage": 2000.0 * damage_scale, "range": 1800.0, "projectile_speed": 1200.0}, signature, loadout_key, team, source, {
				"explode_radius": 90.0,
				"blast_damage": 700.0 * damage_scale,
				"projectile_radius": 36.0
			})
		"tracker_rockets":
			_spawn_homing_volley(origin, direction, 5, 640.0 * damage_scale, team, loadout_key, signature, source)
		"particle_wall":
			_spawn_particle_wall(source_position + direction * 220.0, direction, 260.0, 160.0, 6.0, team, signature)
		"sonar_lock":
			var marked_target := _find_priority_target(source_position, direction, 2200.0, team)
			if team == PlayerShip.TEAM_PLAYER:
				tracked_enemy = marked_target as EnemyShip
			if marked_target != null and is_instance_valid(marked_target):
				_spawn_impact_burst(marked_target.global_position, signature)
		"power_shot":
			var heavy_weapon := {"damage": 3200.0, "range": 3400.0}
			_fire_hitscan(origin, direction, heavy_weapon, signature, loadout_key, team, damage_scale, source)
		"rocket_salvo":
			_spawn_homing_volley(origin, direction, 5, 720.0 * damage_scale, team, loadout_key, signature, source)
		"energy_siphon":
			var siphon_target := _find_nearest_target(source_position, direction, 1800.0, team)
			if siphon_target != null:
				var siphon_damage := 800.0 * damage_scale
				siphon_target.apply_damage(siphon_damage, siphon_target.global_position, loadout_key)
				_track_player_damage(source, siphon_target, siphon_damage)
				if source != null and source.has_method("restore_shield"):
					source.restore_shield(800.0)
				_award_core_charge(source, 400.0)
				_spawn_tracer(source_position, siphon_target.global_position, signature)
				_spawn_impact_burst(siphon_target.global_position, signature)

func _on_core_triggered(core_id: String, loadout_key: String, source: Node3D, origin: Vector3, direction: Vector3, team: int) -> void:
	var signature := GameData.get_signature(loadout_key)
	var damage_scale := _get_actor_damage_multiplier(source)
	match core_id:
		"laser_core":
			var core_weapon := {"damage": 4500.0, "range": 4000.0}
			_fire_hitscan(origin, direction, core_weapon, signature, loadout_key, team, damage_scale, source)
		"flame_core":
			var blast_position := source.global_position if source else origin
			_blast_area(blast_position, 340.0, 3200.0 * damage_scale, team, loadout_key, signature, source)
		"salvo_core":
			_spawn_homing_volley(origin, direction, 12, 420.0 * damage_scale, team, loadout_key, signature, source)

func _fire_hitscan(origin: Vector3, direction: Vector3, weapon_data: Dictionary, signature: Dictionary, loadout_key: String, team: int, damage_scale: float, source: Node3D) -> void:
	var aim_direction := direction.normalized()
	var ray_length := float(weapon_data.get("range", 2400.0))
	var target_point := origin + aim_direction * ray_length
	var best_distance := ray_length

	var wall_hit := _find_blocking_wall_hit(origin, target_point, team)
	if not wall_hit.is_empty():
		best_distance = minf(best_distance, float(wall_hit["distance"]))
		target_point = wall_hit["point"]

	var best_hit := _find_hitscan_target(origin, aim_direction, ray_length, team)
	if not best_hit.is_empty() and float(best_hit["distance"]) < best_distance:
		best_distance = float(best_hit["distance"])
		target_point = best_hit["point"]
		var target: Object = best_hit["target"]
		var dealt := float(weapon_data.get("damage", 100.0)) * damage_scale
		target.apply_damage(dealt, target_point, loadout_key)
		_track_player_damage(source, target, dealt)
		_award_core_charge(source, dealt)
		_spawn_impact_burst(target_point, signature)
	elif not wall_hit.is_empty():
		_spawn_impact_burst(target_point, signature)

	_spawn_tracer(origin, target_point, signature)

func _spawn_projectile(origin: Vector3, direction: Vector3, weapon_data: Dictionary, signature: Dictionary, loadout_key: String, team: int, source: Node3D, extra: Dictionary) -> void:
	var projectile_mesh := SphereMesh.new()
	projectile_mesh.radius = 6.0
	projectile_mesh.height = 12.0

	var projectile_node := MeshInstance3D.new()
	projectile_node.mesh = projectile_mesh
	var projectile_color: Color = GameData.color_from_hex(int(signature.get("muzzle_color", 0xffaa33)))
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.albedo_color = projectile_color
	material.emission_enabled = true
	material.emission = projectile_color
	material.emission_energy_multiplier = 2.8
	projectile_node.material_override = material
	projectile_root.add_child(projectile_node)
	projectile_node.global_position = origin

	var projectile_speed := float(weapon_data.get("projectile_speed", 800.0))
	var velocity := direction.normalized() * projectile_speed
	var projectile_radius := float(extra.get("projectile_radius", 24.0))
	var projectile_data := {
		"node": projectile_node,
		"position": origin,
		"velocity": velocity,
		"ttl": float(weapon_data.get("range", 2500.0)) / maxf(1.0, projectile_speed),
		"radius": projectile_radius,
		"damage": float(weapon_data.get("damage", 500.0)),
		"loadout_key": loadout_key,
		"team": team,
		"source": source,
		"signature": signature,
		"explode_radius": float(extra.get("explode_radius", 0.0)),
		"blast_damage": float(extra.get("blast_damage", 0.0)),
		"cluster_count": int(extra.get("cluster_count", 0)),
		"cluster_damage": float(extra.get("cluster_damage", 0.0)),
		"homing_target": extra.get("homing_target", null),
		"turn_rate": float(extra.get("turn_rate", 4.2))
	}
	projectiles.append(projectile_data)

	_spawn_tracer(origin, origin + direction.normalized() * 120.0, signature)

func _spawn_homing_volley(origin: Vector3, direction: Vector3, count: int, damage: float, team: int, loadout_key: String, signature: Dictionary, source: Node3D) -> void:
	for index in range(count):
		var spread_amount := 0.12 + (float(index % 3) * 0.02)
		var volley_direction := (
			direction +
			Vector3(
				randf_range(-spread_amount, spread_amount),
				randf_range(-spread_amount, spread_amount),
				randf_range(-spread_amount * 0.2, spread_amount * 0.2)
			)
		).normalized()
		var target := _find_priority_target(origin, direction, 2600.0, team)
		_spawn_projectile(origin, volley_direction, {
			"damage": damage,
			"range": 3800.0,
			"projectile_speed": 760.0
		}, signature, loadout_key, team, source, {
			"explode_radius": 120.0,
			"blast_damage": damage * 0.65,
			"homing_target": target,
			"turn_rate": 4.8
		})

func _spawn_tracer(origin: Vector3, target_point: Vector3, signature: Dictionary) -> void:
	var tracer_color: Color = GameData.color_from_hex(int(signature.get("tracer_color", 0xffff66)))
	var beam_lifetime := float(signature.get("beam_lifetime", 0.08))
	var glow_lifetime := float(signature.get("glow_lifetime", 0.15))

	tracer_core.spawn_segment(origin, target_point, Color(1, 1, 1, 1), float(signature.get("tracer_core_radius", 1.2)) * 0.12, minf(beam_lifetime, 0.06))
	tracer_beam.spawn_segment(origin, target_point, tracer_color, float(signature.get("tracer_beam_radius", 2.0)) * 0.14, beam_lifetime)
	tracer_glow.spawn_segment(origin, target_point, tracer_color, float(signature.get("tracer_glow_radius", 6.0)) * 0.18, glow_lifetime)

func _spawn_impact_burst(position: Vector3, signature: Dictionary) -> void:
	var particles := GPUParticles3D.new()
	particles.amount = 24
	particles.lifetime = 0.18
	particles.one_shot = true
	particles.explosiveness = 1.0

	var quad := QuadMesh.new()
	quad.size = Vector2(9.0, 9.0)
	var impact_color: Color = GameData.color_from_hex(int(signature.get("impact_light_color", 0xffcc66)))
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	material.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	material.albedo_color = Color(impact_color.r, impact_color.g, impact_color.b, 0.9)
	material.emission_enabled = true
	material.emission = impact_color
	material.emission_energy_multiplier = 2.8
	quad.material = material
	particles.draw_pass_1 = quad

	var process := ParticleProcessMaterial.new()
	process.direction = Vector3.ZERO
	process.spread = 180.0
	process.gravity = Vector3.ZERO
	process.initial_velocity_min = 20.0
	process.initial_velocity_max = 90.0
	process.scale_min = 0.6
	process.scale_max = 1.6
	process.color = impact_color
	particles.process_material = process

	effect_root.add_child(particles)
	particles.global_position = position
	particles.emitting = true
	get_tree().create_timer(0.5).timeout.connect(particles.queue_free)

func _spawn_zone(position: Vector3, radius: float, duration: float, damage_per_second: float, team: int, signature: Dictionary, velocity: Vector3, loadout_key: String, source: Node3D) -> void:
	var mesh := SphereMesh.new()
	mesh.radius = 1.0
	mesh.height = 2.0
	var node := MeshInstance3D.new()
	node.mesh = mesh
	var color := GameData.color_from_hex(int(signature.get("impact_light_color", 0xffcc66)))
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	material.albedo_color = Color(color.r, color.g, color.b, 0.14)
	material.emission_enabled = true
	material.emission = color
	material.emission_energy_multiplier = 1.1
	node.material_override = material
	node.scale = Vector3.ONE * radius
	node.global_position = position
	effect_root.add_child(node)

	world_effects.append({
		"type": "zone",
		"node": node,
		"position": position,
		"radius": radius,
		"timer": duration,
		"dps": damage_per_second,
		"team": team,
		"source": source,
		"velocity": velocity,
		"loadout_key": loadout_key,
		"signature": signature
	})

func _spawn_mine(position: Vector3, radius: float, arm_time: float, duration: float, damage: float, team: int, loadout_key: String, signature: Dictionary, source: Node3D) -> void:
	var mesh := SphereMesh.new()
	mesh.radius = 12.0
	mesh.height = 24.0
	var node := MeshInstance3D.new()
	node.mesh = mesh
	var color := GameData.color_from_hex(int(signature.get("impact_light_color", 0xffcc66)))
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	material.albedo_color = Color(color.r, color.g, color.b, 0.85)
	material.emission_enabled = true
	material.emission = color
	material.emission_energy_multiplier = 2.0
	node.material_override = material
	node.global_position = position
	effect_root.add_child(node)

	world_effects.append({
		"type": "mine",
		"node": node,
		"position": position,
		"radius": radius,
		"timer": duration,
		"arm_time": arm_time,
		"damage": damage,
		"team": team,
		"source": source,
		"loadout_key": loadout_key,
		"signature": signature
	})

func _spawn_particle_wall(position: Vector3, normal: Vector3, width: float, height: float, duration: float, team: int, signature: Dictionary) -> void:
	var mesh := QuadMesh.new()
	mesh.size = Vector2(width, height)
	var node := MeshInstance3D.new()
	node.mesh = mesh
	var color := GameData.color_from_hex(int(signature.get("shield_color", signature.get("impact_light_color", 0x88ccff))))
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	material.billboard_mode = BaseMaterial3D.BILLBOARD_DISABLED
	material.cull_mode = BaseMaterial3D.CULL_DISABLED
	material.albedo_color = Color(color.r, color.g, color.b, 0.18)
	material.emission_enabled = true
	material.emission = color
	material.emission_energy_multiplier = 1.8
	node.material_override = material
	node.global_position = position
	node.look_at(position + normal, Vector3.UP)
	effect_root.add_child(node)

	var right := normal.cross(Vector3.UP).normalized()
	if right.length_squared() < 0.001:
		right = Vector3.RIGHT

	world_effects.append({
		"type": "wall",
		"node": node,
		"position": position,
		"normal": normal.normalized(),
		"right": right,
		"width": width,
		"height": height,
		"timer": duration,
		"team": team,
		"signature": signature
	})

func _update_projectiles(delta: float) -> void:
	for index in range(projectiles.size() - 1, -1, -1):
		var projectile: Dictionary = projectiles[index]
		projectile["ttl"] = float(projectile["ttl"]) - delta
		var current_position: Vector3 = projectile["position"]
		var velocity: Vector3 = projectile["velocity"]

		var homing_target: Node3D = projectile.get("homing_target", null) as Node3D
		if homing_target != null and is_instance_valid(homing_target) and homing_target.has_method("is_alive") and homing_target.is_alive():
			var target_direction: Vector3 = (homing_target.global_position - current_position).normalized()
			var turn_rate := float(projectile.get("turn_rate", 4.0))
			velocity = velocity.normalized().slerp(target_direction, clampf(turn_rate * delta, 0.0, 1.0)) * velocity.length()
			projectile["velocity"] = velocity

		var next_position := current_position + velocity * delta

		var wall_hit := _find_blocking_wall_hit(current_position, next_position, int(projectile["team"]))
		if not wall_hit.is_empty():
			_detonate_projectile(index, wall_hit["point"], null)
			continue

		var node: MeshInstance3D = projectile["node"]
		node.global_position = next_position
		if velocity.length_squared() > 0.01:
			node.look_at(next_position + velocity, Vector3.UP)

		projectile["position"] = next_position
		if float(projectile["ttl"]) <= 0.0:
			_detonate_projectile(index, next_position, null)
			continue

		var hit_ship := _find_projectile_hit(next_position, float(projectile["radius"]), int(projectile["team"]))
		if hit_ship != null:
			_detonate_projectile(index, next_position, hit_ship)
			continue

		if _outside_bounds(next_position):
			_free_projectile(index)
			continue

		projectiles[index] = projectile

func _update_world_effects(delta: float) -> void:
	for index in range(world_effects.size() - 1, -1, -1):
		var effect: Dictionary = world_effects[index]
		effect["timer"] = float(effect["timer"]) - delta
		if float(effect["timer"]) <= 0.0:
			_remove_world_effect(index)
			continue

		match String(effect["type"]):
			"zone":
				var pos: Vector3 = effect["position"] + effect["velocity"] * delta
				effect["position"] = pos
				var zone_node: MeshInstance3D = effect["node"]
				zone_node.global_position = pos
				zone_node.scale = Vector3.ONE * float(effect["radius"]) * (0.92 + sin(Time.get_ticks_msec() * 0.004) * 0.08)
				_apply_zone_damage(effect, delta)
			"mine":
				var mine_node: MeshInstance3D = effect["node"]
				mine_node.scale = Vector3.ONE * (1.0 + sin(Time.get_ticks_msec() * 0.006) * 0.12)
				effect["arm_time"] = maxf(0.0, float(effect["arm_time"]) - delta)
				if float(effect["arm_time"]) <= 0.0:
					var targets := _get_targets_in_radius(effect["position"], float(effect["radius"]), int(effect["team"]))
					if not targets.is_empty():
						var mine_source: Node3D = effect.get("source", null) as Node3D
						for target in targets:
							target.apply_damage(float(effect["damage"]), effect["position"], String(effect["loadout_key"]))
							_track_player_damage(mine_source, target, float(effect["damage"]))
							_award_core_charge(mine_source, float(effect["damage"]))
						_spawn_impact_burst(effect["position"], effect["signature"])
						_blast_area(effect["position"], 120.0, float(effect["damage"]) * 0.6, int(effect["team"]), String(effect["loadout_key"]), effect["signature"], effect.get("source", null) as Node3D)
						_remove_world_effect(index)
						continue
			"wall":
				var wall_node: MeshInstance3D = effect["node"]
				wall_node.scale = Vector3.ONE * (0.96 + sin(Time.get_ticks_msec() * 0.005) * 0.04)

		world_effects[index] = effect

func _apply_zone_damage(effect: Dictionary, delta: float) -> void:
	var damage := float(effect["dps"]) * delta
	var zone_source: Node3D = effect.get("source", null) as Node3D
	for target in _get_targets_in_radius(effect["position"], float(effect["radius"]), int(effect["team"])):
		target.apply_damage(damage, effect["position"], String(effect["loadout_key"]))
		_track_player_damage(zone_source, target, damage)
		_award_core_charge(zone_source, damage)

func _detonate_projectile(index: int, position: Vector3, hit_target: Object) -> void:
	var projectile: Dictionary = projectiles[index]
	var loadout_key := String(projectile["loadout_key"])
	var source: Node3D = projectile.get("source", null) as Node3D
	var signature: Dictionary = projectile["signature"]
	var base_damage := float(projectile["damage"])

	if hit_target != null:
		hit_target.apply_damage(base_damage, position, loadout_key)
		_track_player_damage(source, hit_target, base_damage)
		_award_core_charge(source, base_damage)

	var explode_radius := float(projectile.get("explode_radius", 0.0))
	var blast_damage := float(projectile.get("blast_damage", 0.0))
	if explode_radius > 0.0 and blast_damage > 0.0:
		_blast_area(position, explode_radius, blast_damage, int(projectile["team"]), loadout_key, signature, source)

	# Concussive shake: blast radius and damage drive the kick size; distance
	# attenuates quadratically so distant detonations barely register.
	var kick := 0.8 + (blast_damage + base_damage) / 2400.0
	_shake_from_event(position, minf(3.0, kick), 3000.0)

	var cluster_count := int(projectile.get("cluster_count", 0))
	if cluster_count > 0:
		var cluster_damage := float(projectile.get("cluster_damage", base_damage * 0.3))
		for cluster_index in range(cluster_count):
			var cluster_pos := position + Vector3(
				randf_range(-90.0, 90.0),
				randf_range(-60.0, 60.0),
				randf_range(-90.0, 90.0)
			)
			_spawn_impact_burst(cluster_pos, signature)
			_blast_area(cluster_pos, 75.0, cluster_damage, int(projectile["team"]), loadout_key, signature, source)

	_spawn_impact_burst(position, signature)
	_free_projectile(index)

func _blast_area(position: Vector3, radius: float, damage: float, team: int, loadout_key: String, signature: Dictionary, source: Node3D) -> void:
	for target in _get_targets_in_radius(position, radius, team):
		target.apply_damage(damage, position, loadout_key)
		_track_player_damage(source, target, damage)
		_award_core_charge(source, damage)
	_spawn_impact_burst(position, signature)
	# AOE contribution to shake: small kick with the blast radius's own falloff.
	_shake_from_event(position, minf(1.5, 0.25 + damage / 1800.0), maxf(radius * 4.0, 1500.0))

# Distance-attenuated screen-shake trigger for explosions. Mirrors the HTML
# "distance-based camera shake" block (lines 3896-3904). amount is the peak
# intensity at distance 0; falloff is quadratic out to max_distance, at which
# point the contribution is zero. Skips when player is null/dead or mounted
# on a camera that isn't following the event space (headless tests).
func _shake_from_event(position: Vector3, amount: float, max_distance: float) -> void:
	if player == null or not player.is_alive():
		return
	if amount <= 0.0:
		return
	var distance := player.global_position.distance_to(position)
	var falloff := clampf(1.0 - distance / maxf(1.0, max_distance), 0.0, 1.0)
	var shake := amount * falloff * falloff
	if shake > 0.05:
		player.add_screen_shake(shake)

# Record damage the local player dealt to enemy ships for the scoreboard
# stats. Source is the attacking Node3D; target is whatever took the hit.
# We count damage only when the source is the player AND the target is NOT
# the player (so self-damage from e.g. own blast radius doesn't inflate the
# tally). The scoreboard column is integer MeV-style total; rounding is done
# at display time.
func _track_player_damage(source: Node3D, target: Object, amount: float) -> void:
	if source == null or source != player:
		return
	if target == null or target == player:
		return
	player_damage_dealt += maxf(0.0, amount)

func _find_hitscan_target(origin: Vector3, direction: Vector3, max_range: float, source_team: int) -> Dictionary:
	var best_distance := max_range
	var best_target: Object = null
	var best_point := origin + direction * max_range

	if source_team == PlayerShip.TEAM_PLAYER:
		for enemy in enemies:
			if not enemy.is_alive():
				continue
			var hit := _ray_sphere_hit(origin, direction, enemy.global_position, enemy.get_collision_radius(), best_distance)
			if not hit.is_empty():
				best_distance = float(hit["distance"])
				best_point = hit["point"]
				best_target = enemy
	else:
		if player.is_alive():
			var player_hit := _ray_sphere_hit(origin, direction, player.global_position, player.get_collision_radius(), best_distance)
			if not player_hit.is_empty():
				best_distance = float(player_hit["distance"])
				best_point = player_hit["point"]
				best_target = player

	if best_target:
		return {"target": best_target, "point": best_point, "distance": best_distance}
	return {}

func _find_projectile_hit(position: Vector3, hit_radius: float, source_team: int) -> Object:
	if source_team == PlayerShip.TEAM_PLAYER:
		for enemy in enemies:
			if not enemy.is_alive():
				continue
			if enemy.global_position.distance_to(position) <= hit_radius + enemy.get_collision_radius():
				return enemy
	else:
		if player.is_alive() and player.global_position.distance_to(position) <= hit_radius + player.get_collision_radius():
			return player
	return null

func _get_targets_in_radius(position: Vector3, radius: float, source_team: int) -> Array:
	var targets: Array = []
	if source_team == PlayerShip.TEAM_PLAYER:
		for enemy in enemies:
			if enemy.is_alive() and enemy.global_position.distance_to(position) <= radius + enemy.get_collision_radius():
				targets.append(enemy)
	else:
		if player.is_alive() and player.global_position.distance_to(position) <= radius + player.get_collision_radius():
			targets.append(player)
	return targets

func _find_nearest_enemy(origin: Vector3, forward: Vector3, max_distance: float) -> EnemyShip:
	var best_enemy: EnemyShip = null
	var best_distance := max_distance
	for enemy in enemies:
		if not enemy.is_alive():
			continue
		var to_enemy := enemy.global_position - origin
		var distance := to_enemy.length()
		if distance > best_distance:
			continue
		if forward.normalized().dot(to_enemy.normalized()) < 0.2:
			continue
		best_enemy = enemy
		best_distance = distance
	return best_enemy

func _find_nearest_target(origin: Vector3, forward: Vector3, max_distance: float, source_team: int) -> Node3D:
	if source_team == PlayerShip.TEAM_PLAYER:
		return _find_nearest_enemy(origin, forward, max_distance)
	if player.is_alive():
		var to_player := player.global_position - origin
		if to_player.length() <= max_distance and forward.normalized().dot(to_player.normalized()) >= -0.1:
			return player
	return null

func _find_priority_target(origin: Vector3, forward: Vector3, max_distance: float, source_team: int) -> Node3D:
	if source_team == PlayerShip.TEAM_PLAYER and tracked_enemy and tracked_enemy.is_alive() and tracked_enemy.global_position.distance_to(origin) <= max_distance:
		return tracked_enemy
	return _find_nearest_target(origin, forward, max_distance, source_team)

func _get_actor_damage_multiplier(source: Node3D) -> float:
	if source != null and source.has_method("get_damage_multiplier"):
		return float(source.call("get_damage_multiplier"))
	return 1.0

func _award_core_charge(source: Node3D, amount: float) -> void:
	if source != null and is_instance_valid(source) and source.has_method("add_core_charge"):
		source.call("add_core_charge", amount)

func _find_blocking_wall_hit(from: Vector3, to: Vector3, source_team: int) -> Dictionary:
	var best_distance := INF
	var best_point := Vector3.ZERO
	var found := false
	if arena_map:
		var map_hit := arena_map.raycast_wall(from, to, 12.0)
		if not map_hit.is_empty():
			best_distance = float(map_hit["distance"])
			best_point = map_hit["point"]
			found = true

	for effect in world_effects:
		if String(effect["type"]) != "wall":
			continue
		if int(effect["team"]) == source_team:
			continue

		var segment := to - from
		var normal: Vector3 = effect["normal"]
		var denominator := segment.dot(normal)
		if absf(denominator) < 0.0001:
			continue

		var t := (Vector3(effect["position"]) - from).dot(normal) / denominator
		if t < 0.0 or t > 1.0:
			continue

		var point := from + segment * t
		var local_offset := point - Vector3(effect["position"])
		var half_width := float(effect["width"]) * 0.5
		var half_height := float(effect["height"]) * 0.5
		var right: Vector3 = effect["right"]
		if absf(local_offset.dot(right)) > half_width:
			continue
		if absf(local_offset.y) > half_height:
			continue

		var hit_distance := from.distance_to(point)
		if hit_distance < best_distance:
			best_distance = hit_distance
			best_point = point
			found = true

	if found:
		return {"point": best_point, "distance": best_distance}
	return {}

func _ray_sphere_hit(origin: Vector3, direction: Vector3, center: Vector3, radius: float, max_range: float) -> Dictionary:
	var to_center := center - origin
	var projection := to_center.dot(direction)
	if projection < 0.0 or projection > max_range:
		return {}
	var closest := origin + direction * projection
	if closest.distance_to(center) > radius:
		return {}
	return {"distance": projection, "point": closest}

func _remove_world_effect(index: int) -> void:
	var effect: Dictionary = world_effects[index]
	var node: Node = effect.get("node", null) as Node
	if node != null and is_instance_valid(node):
		node.queue_free()
	world_effects.remove_at(index)

func _free_projectile(index: int) -> void:
	var projectile: Dictionary = projectiles[index]
	var node: MeshInstance3D = projectile["node"]
	if is_instance_valid(node):
		node.queue_free()
	projectiles.remove_at(index)

func _outside_bounds(position: Vector3) -> bool:
	if arena_map:
		var extents := arena_map.get_bounds_extents() + Vector3.ONE * 120.0
		return position.x < -extents.x or position.x > extents.x or position.y < -extents.y or position.y > extents.y or position.z < -extents.z or position.z > extents.z
	var bounds: Vector3 = GameData.ARENA_EXTENTS
	return position.x < -bounds.x or position.x > bounds.x or position.y < -bounds.y or position.y > bounds.y or position.z < -bounds.z or position.z > bounds.z
