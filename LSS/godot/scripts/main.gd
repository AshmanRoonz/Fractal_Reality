extends Node3D

const GameData = preload("res://scripts/game_data.gd")
const PlayerShip = preload("res://scripts/player_ship.gd")
const SandboxHUD = preload("res://scripts/hud.gd")
const CinematicOverlay = preload("res://scripts/cinematic_overlay.gd")
const TracerPool = preload("res://scripts/tracer_pool.gd")
const EnemyShip = preload("res://scripts/enemy_ship.gd")
const ArenaMap = preload("res://scripts/arena_map.gd")
const Settings = preload("res://scripts/settings.gd")
const DestructibleObstacle = preload("res://scripts/destructible_obstacle.gd")
const ClusterObstacle = preload("res://scripts/cluster_obstacle.gd")
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
var hazard_root: Node3D
var arena_map: ArenaMap

# Environmental hazards (HTML last_ship_sailing.html:4043-4525). Clusters
# hold their own child pack; standalone_obstacles is a flat list of any
# pieces that were NOT spawned as part of a cluster. main.gd iterates
# clusters + each cluster's children + standalones each frame; cluster
# respawn rebuilds its own children in place, so no array sync is needed.
var clusters: Array[ClusterObstacle] = []
var standalone_obstacles: Array[DestructibleObstacle] = []

var tracer_glow: TracerPool
var tracer_beam: TracerPool
var tracer_core: TracerPool
var explosion_fx: ExplosionFX

var enemies: Array[EnemyShip] = []
var projectiles: Array = []
var world_effects: Array = []
# HTML last_ship_sailing.html:840-849, 9425-9522. Shield-recharge pickups.
# First batch (three at once) spawns 30s into the round; afterward one
# respawns every 30s while fewer than three remain. Kept as plain Arrays
# so tests can inspect them without poking inside world_effects dicts.
var stasis_spawn_timer: float = 30.0
var stasis_first_batch: bool = true
const STASIS_INTERVAL := 30.0
const STASIS_MAX := 3
const STASIS_PICKUP_RADIUS := 120.0
const STASIS_DURATION := 3.0
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

# --- Cinematic overlay state ---------------------------------------------
# Kill streak: _streak_count chains while consecutive kills land within
# MULTIKILL_WINDOW seconds; resets on first kill after the window expires.
const MULTIKILL_WINDOW := 4.0
const LONGSHOT_RANGE_SQ := 1800.0 * 1800.0
var _streak_count := 0
var _last_kill_time := -1000.0
var _match_time := 0.0
# True once the first kill of the round has been scored. Reset in _begin_round.
var _first_blood_claimed := false
# Tracks the enemy that last killed the player (for revenge medals). Stored
# as the enemy's EnemyShip reference; cleared on consumption / respawn.
var _last_killed_by: EnemyShip = null
# Per-bot kill streak tallies (EnemyShip -> int). Used for shutdown medals.
# Cleared on _begin_round.
var _bot_streaks: Dictionary = {}
# Last integer value passed to the 3-2-1 countdown; used so we don't re-fire
# the overlay every frame while warmup_timer is still above the threshold.
var _last_countdown_n := -1
# One-shot flags used to tag the kill-feed suffix " [EXEC]" on finisher kills.
# Set by _execute_enemy / _execute_player before the lethal apply_damage call;
# consumed by _on_enemy_destroyed / _on_player_destroyed when they stamp the
# kill feed entry. Cleared unconditionally so a non-execution kill in the same
# frame cannot inherit the suffix.
var _pending_exec_victim: EnemyShip = null
var _pending_player_exec := false

# --- Death camera (orbit spectator) --------------------------------------
# Mirrors last_ship_sailing.html:11309-11347. When the player dies we swap
# the current Camera3D over to a dedicated orbit cam that circles the
# death location at a slow angular rate; on respawn we flip the player's
# own camera back to current. The player's camera stays parented to the
# ship (so it snaps back cleanly once the ship reparents on respawn), but
# current = false keeps it from rendering while _death_cam_active is true.
# Death-cam constants + pure math live in DeathCamMath (scripts/death_cam_math.gd)
# so the headless test can call the helpers via a class_name without preloading
# this whole file (which pulls in class_name types that `-s` mode can't resolve).
var _death_cam: Camera3D = null
var _death_cam_active := false
var _death_cam_target := Vector3.ZERO
var _death_cam_angle := 0.0
var _death_cam_radius := DeathCamMath.DEATH_CAM_DEFAULT_RADIUS

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

	# Explosion + dynamic-light cascade. Mirrors HTML last_ship_sailing.html
	# 3836-4032 (spawnExplosion + spawnDynamicLight pool). Lives under
	# effect_root so it shares the cleanup path other VFX use; the pool of 8
	# OmniLight3D children is built in its _ready.
	explosion_fx = ExplosionFX.new()
	explosion_fx.name = "ExplosionFX"
	effect_root.add_child(explosion_fx)

	projectile_root = Node3D.new()
	projectile_root.name = "Projectiles"
	add_child(projectile_root)

	hazard_root = Node3D.new()
	hazard_root.name = "Hazards"
	add_child(hazard_root)

	player = PlayerShip.new()
	add_child(player)
	player.global_position = arena_map.get_spawn_point("A", 30.0)
	player.set_arena_map(arena_map)
	player.primary_fired.connect(_on_primary_fired)
	player.ability_triggered.connect(_on_ability_triggered)
	player.core_triggered.connect(_on_core_triggered)
	player.destroyed.connect(_on_player_destroyed)
	player.damage_taken.connect(_on_player_damage_taken)
	# Cinematic ability flash fires for every successful activation, local or
	# networked; wired to the HUD's forwarder which picks a color by id.
	player.ability_activated.connect(_on_player_ability_activated)

	# Hand the explosion module a player ref so distance-based shake decisions
	# can run inside it if we later move that logic out of _shake_from_event.
	if explosion_fx != null:
		explosion_fx.set_player_ref(player)

	# Death camera lives on main so it is not reparented when the player
	# respawns. Starts non-current so the player's cockpit camera owns the
	# viewport until _start_death_cam flips it.
	_death_cam = Camera3D.new()
	_death_cam.name = "DeathCam"
	_death_cam.fov = 62.0
	_death_cam.near = 0.1
	_death_cam.current = false
	add_child(_death_cam)

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

	# Ambient bed: phi-cascade binaural drone that rides the player's speed.
	# HTML line 10845 starts it at init; we defer to after _start_match so the
	# match_state is already "warmup" when update_ambient_bed() first reads it.
	_start_ambient_bed()

# --- Audio autoload plumbing --------------------------------------------
# All three helpers below null-check the autoload before calling it so the
# headless test harnesses (scripts/tests/*) can spin up a bare SceneTree
# without Audio registered and still exercise the gameplay paths.
func _play_audio(type: String) -> void:
	# Engine.get_main_loop() returns the MainLoop base class, which doesn't
	# expose .root; the Godot 4.6 typed-inference check rejects a bare
	# `var root := loop.root` assignment. Cast to SceneTree first so `root` is
	# typed as Window and the script parses cleanly in the editor AND in `-s`.
	var loop := Engine.get_main_loop() as SceneTree
	if loop == null:
		return
	var root: Window = loop.root
	if root != null and root.has_node("Audio"):
		root.get_node("Audio").play_sound(type)

func _start_ambient_bed() -> void:
	var loop := Engine.get_main_loop() as SceneTree
	if loop == null:
		return
	var root: Window = loop.root
	if root != null and root.has_node("Audio"):
		root.get_node("Audio").start_ambient_bed()

func _update_ambient_bed() -> void:
	var loop := Engine.get_main_loop() as SceneTree
	if loop == null:
		return
	var root: Window = loop.root
	if root == null or not root.has_node("Audio"):
		return
	var speed := 0.0
	if player != null and player.is_alive():
		speed = player.velocity.length()
	root.get_node("Audio").update_ambient_bed(speed, match_state)

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
	# Drive the phi-cascade ambient bed every frame. Internally the Audio
	# autoload lerps the current base frequency toward the speed-derived target,
	# so per-frame calls produce a smooth morph instead of zipper noise.
	_update_ambient_bed()
	hud.update_from_player(player, _count_alive_enemies(), _get_match_info())
	# Drive the persistent doomed vignette + "HULL CRITICAL" banner from the
	# ship's latched flag. Cheap no-op when state hasn't changed (DoomedOverlay
	# early-returns when set_active is called with the same value).
	hud.set_doomed_state(player.is_doomed())
	# Execution prompt: show "RAM TO EXECUTE" only when there is a doomed
	# enemy within roughly hull_length*3 AND the player is looking at it
	# (HTML lines 9573-9630). The HUD overlay no-ops when the state doesn't
	# change, so re-evaluating every frame is cheap.
	hud.set_execution_prompt(_any_doomed_enemy_in_sight())
	# Keep the scoreboard's stats fresh while it's on screen so health/shield
	# values follow combat in real time (mirrors HTML updateScoreboard being
	# called every keydown; we poll at frame rate while visible).
	if hud.is_scoreboard_visible():
		_refresh_scoreboard_contents()

# HTML's execution prompt gate: the player is within ~3x hull lengths of a
# doomed enemy AND is looking towards it. Returns true if any enemy qualifies.
# We use player.get_forward() and a dot > 0.3 threshold to match line 9578.
const EXEC_PROMPT_RANGE_MULT := 3.0
const EXEC_PROMPT_DOT_THRESHOLD := 0.3

# Ship-ship collision + finisher constants (HTML 2233-2328, 9563-9631).
# SHIP_REPULSE_RANGE multiplies combined hull radii to set the soft-push field;
# SHIP_REPULSE_STRENGTH is the per-second peak force inside that field; hard
# contact (dist < min_dist) swaps to a reflect-and-penetrate bounce governed by
# RAM_BOUNCE_COEFF. Ram damage kicks in only when relative closing speed along
# the contact normal exceeds RAM_IMPACT_THRESHOLD, scaled by RAM_DAMAGE_MULT.
# Execution radius is 1.2x the player's hull length (HTML line 9566); a
# successful exec grants +20 core meter, refills shields, and adds 4.0 of the
# 0..4 screen-shake budget.
const SHIP_REPULSE_RANGE := 2.2
const SHIP_REPULSE_STRENGTH := 10000.0
const RAM_DAMAGE_MULT := 0.3
const RAM_IMPACT_THRESHOLD := 80.0
const RAM_BOUNCE_COEFF := 0.6
const SHIP_HULL_RADIUS_MULT := 0.45
const EXEC_RADIUS_MULT := 1.2
const EXEC_CORE_GAIN := 20.0
const EXEC_SCREEN_SHAKE := 4.0
func _any_doomed_enemy_in_sight() -> bool:
	if player == null or not player.is_alive():
		return false
	var forward := player.get_forward()
	if forward == Vector3.ZERO:
		return false
	var hull_length := float(player.chassis.get("hull_length", 100.0))
	var prompt_range := hull_length * EXEC_PROMPT_RANGE_MULT
	var prompt_range_sq := prompt_range * prompt_range
	for enemy in enemies:
		if not enemy.is_alive() or not enemy.doomed:
			continue
		var offset := enemy.global_position - player.global_position
		if offset.length_squared() > prompt_range_sq:
			continue
		var to_enemy := offset.normalized()
		if forward.dot(to_enemy) > EXEC_PROMPT_DOT_THRESHOLD:
			return true
	return false

func _physics_process(delta: float) -> void:
	_update_round_system(delta)
	_update_projectiles(delta)
	_update_world_effects(delta)
	_update_stasis_spawner(delta)
	# Hazards tick after world-effects / projectiles so a projectile that just
	# detonated on a cluster child already logged its damage to this frame's
	# take_damage call; the hazard update then advances fragment drift, runs
	# ship-vs-obstacle collision, and ticks respawn countdowns.
	_update_hazards(delta)
	# HTML order (lines 10503, 10534): checkExecutions first so a finisher that
	# lands on the same frame as a ram gets the execution bonuses; the collision
	# pass then handles any surviving ships with its own ram-damage path.
	_check_executions()
	_resolve_ship_ship_collisions(delta)
	_tick_damage_fx()
	# Orbit the death cam each frame while the player is waiting to respawn.
	# HTML updateDeathCam runs every tick (line 11326); we key off the local
	# active flag so the call is a cheap no-op the rest of the time.
	_tick_death_cam(delta)

	if tracked_enemy and (not is_instance_valid(tracked_enemy) or not tracked_enemy.is_alive()):
		tracked_enemy = null

# Mirrors HTML ship.update() lines 3043-3046: every ship below 50% hull emits
# a damage-smoke roll per frame. The module self-gates on the threshold and
# rolls intensity*probability dice internally, so we just feed it every ship
# every tick. No extra throttling: matches the HTML cadence.
func _tick_damage_fx() -> void:
	if explosion_fx == null or not is_instance_valid(explosion_fx):
		return
	if player != null and player.is_alive() and player.max_health > 0.0 \
			and player.health < player.max_health * 0.5:
		explosion_fx.spawn_damage_smoke(player.global_position, player.health / player.max_health)
	for enemy in enemies:
		if enemy == null or not is_instance_valid(enemy) or not enemy.is_alive():
			continue
		if enemy.max_health <= 0.0:
			continue
		if enemy.health < enemy.max_health * 0.5:
			explosion_fx.spawn_damage_smoke(enemy.global_position, enemy.health / enemy.max_health)

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
	# Reset the stasis spawner so the new round gets a fresh 30s countdown to the
	# first batch (HTML last_ship_sailing.html:9464-9484). _clear_transient_combat
	# below wipes any existing fields from the previous round.
	stasis_spawn_timer = STASIS_INTERVAL
	stasis_first_batch = true
	# Clear the team-level bot broadcast dictionary so a stale player position
	# from the previous round doesn't lead bots back to where round-2 player
	# has already left (HTML game.botSharedTarget is per-round in practice).
	EnemyShip.reset_shared_broadcasts()
	_clear_transient_combat()
	# Hazards are rebuilt per round (HTML spawnDynamicObjects at lines 4473-4510
	# runs whenever a new round starts). _clear_transient_combat above strips
	# projectiles and world_effects but leaves the obstacles untouched so this
	# call owns their lifecycle independently.
	_spawn_hazards()
	player_spawn_point = arena_map.get_spawn_point("A", 120.0)
	player.reset_for_round(player_spawn_point)
	# HTML 11343-11347: respawnPlayer() wrapper flips deathCam.active = false.
	# _begin_round is the single entry point for a fresh round in this port, so
	# deactivation lives here rather than on a per-ship respawn hook.
	_stop_death_cam()
	enemy_spawn_positions.clear()
	for enemy in enemies:
		var enemy_spawn := arena_map.get_spawn_point("B", 220.0)
		enemy_spawn_positions.append(enemy_spawn)
		enemy.spawn_point = enemy_spawn
		enemy.reset_for_round()
	# Reset per-round cinematic tallies. _first_blood_claimed flips false so
	# the first kill of the new round qualifies for the medal; bot streaks
	# start from zero; the persistent respawn overlay clears (1 life per
	# round in Last Ship Sailing).
	_first_blood_claimed = false
	_bot_streaks.clear()
	_streak_count = 0
	_last_killed_by = null
	_last_countdown_n = -1
	if hud != null:
		hud.hide_respawn()
		hud.set_execution_prompt(false)
	_set_match_state("warmup")

func _update_round_system(delta: float) -> void:
	_match_time += delta
	match match_state:
		"warmup":
			warmup_timer = maxf(0.0, warmup_timer - delta)
			# 3-2-1 countdown in the last 3 seconds of warmup (HTML lines
			# 7763-7778). We fire the overlay once per integer transition;
			# the "FIGHT" beat plays on the warmup->playing transition below.
			var n := int(ceil(warmup_timer))
			if n >= 1 and n <= 3 and n != _last_countdown_n:
				_last_countdown_n = n
				if hud != null:
					hud.show_countdown(n, "ROUND %d" % current_round)
			if warmup_timer <= 0.0:
				round_timer = ROUND_TIME
				_set_match_state("playing")
				# Round-start chord on the warmup->playing flip (HTML fires the
				# FIGHT SFX at this transition).
				_play_audio("round_start")
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
				# HTML uses the dedicated countdown element for FIGHT (line
				# 7777); the banner stays reserved for ROUND OVER / VICTORY /
				# ROUND N text. Passing 0 marks this as the fight beat.
				hud.show_countdown(0, "")
				_last_countdown_n = -1
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
	# Death explosion at the player's last known position. HTML spawnExplosion
	# fires from playerDie (line 5707) with size ~45-55 depending on chassis.
	# We spawn before resolving names because player.global_position becomes
	# stale once the ship reparents during respawn handling.
	if player != null and is_instance_valid(player):
		_spawn_explosion(player.global_position, 50.0)
	# Orbit spectator camera (HTML 11336-11341: startDeathCam hooked after the
	# original playerDie). Captured here before any further state mutates so
	# the target position matches the visible death location.
	_start_death_cam()
	var killer_name := _resolve_ship_name(killer_loadout_key)
	# Execution finisher by an enemy on a doomed player (HTML line 9615).
	# _pending_player_exec is set in _execute_player right before the lethal
	# apply_damage call so the suffix lands on exactly one kill feed entry.
	if _pending_player_exec:
		killer_name += " [EXEC]"
	_pending_player_exec = false
	player_deaths += 1
	if hud != null:
		hud.add_kill_feed_entry(killer_name, "You")
		# Persistent "DESTROYED" overlay until the next round begins. HTML
		# uses Overlays.respawn(killer) at line 5713; we mirror by stashing
		# the display name.
		hud.show_respawn(killer_name)
	# Remember who killed us so a retaliatory kill inside this round can
	# claim the revenge medal. Match the HTML by resolving to the specific
	# enemy ship rather than just the loadout key (several bots can share a
	# key if loadouts are duplicated; the revenge logic wants the instance).
	_last_killed_by = null
	for enemy in enemies:
		if enemy.loadout_key == killer_loadout_key:
			_last_killed_by = enemy
			break

# Cinematic damage feedback: red radial vignette + chromatic aberration pulse,
# intensity scaled by how hard we were hit relative to max health. Matches
# HTML Overlays.damageVignette(amount/player.maxHealth) (line 5682).
# hit_point is the attacker/projectile world position so the HUD overlay can
# light the matching directional indicator (HTML showDamageIndicator 10294).
func _on_player_damage_taken(_amount: float, ratio: float, hit_point: Vector3) -> void:
	if hud != null:
		hud.flash_damage(ratio)
		# Directional damage arrows: forwarded to HUDOverlay via the SandboxHUD
		# wrapper. Uses the player's own camera for the screen-space basis so
		# the indicators point at the attacker regardless of roll/look-around.
		if player != null and player.is_alive() and player.camera != null:
			hud.show_damage_indicator(hit_point, player.global_position, player.camera)

# ---- Death camera helpers (HTML last_ship_sailing.html:11309-11347) ----
# startDeathCam captures the death location, angle, and orbit radius from the
# player's chassis. updateDeathCam advances the angle at 0.4 rad/sec and
# positions the camera at polar coordinates around the target with a fixed
# height of 150. _stop_death_cam is the respawnPlayer counterpart: flips
# current back to the player's own camera and clears the state so a subsequent
# death starts from a fresh angle instead of wherever the previous orbit left
# off (the HTML implementation reassigns player.euler.y each death, matching
# this behaviour).

# Pure math + constants live in DeathCamMath (scripts/death_cam_math.gd). This
# file only owns the Node3D glue: captures player state, flips cam.current,
# advances the angle every physics tick.

func _start_death_cam() -> void:
	if _death_cam == null or not is_instance_valid(_death_cam):
		return
	if player == null or not is_instance_valid(player):
		return
	_death_cam_active = true
	_death_cam_target = player.global_position
	_death_cam_angle = player.rotation.y
	_death_cam_radius = DeathCamMath.compute_death_cam_radius(player.chassis)
	_death_cam.current = true
	# Snap to the initial orbit position so the first rendered frame doesn't
	# flash from wherever the cam was last parked.
	_apply_death_cam_transform()

func _stop_death_cam() -> void:
	_death_cam_active = false
	if _death_cam != null and is_instance_valid(_death_cam):
		_death_cam.current = false
	# Restore the player's camera as current if it is still around. The player
	# camera is a child of the ship; on the respawn path reset_for_round has
	# already run by the time _stop_death_cam fires, so the camera is at the
	# correct offset when we flip it back on.
	if player != null and is_instance_valid(player) and player.camera != null:
		player.camera.current = true

func _tick_death_cam(delta: float) -> void:
	if not _death_cam_active:
		return
	if _death_cam == null or not is_instance_valid(_death_cam):
		return
	_death_cam_angle += delta * DeathCamMath.DEATH_CAM_ANGULAR_SPEED
	_apply_death_cam_transform()

func _apply_death_cam_transform() -> void:
	if _death_cam == null or not is_instance_valid(_death_cam):
		return
	var cam_pos := DeathCamMath.compute_death_cam_position(_death_cam_target, _death_cam_angle, _death_cam_radius)
	_death_cam.global_position = cam_pos
	# Guard against look_at with a degenerate up vector (cam directly above
	# target). 150-unit height with a few-hundred-unit radius keeps us safe,
	# but cheap defensive check keeps the fallback for zero-radius tests.
	if (cam_pos - _death_cam_target).length_squared() > 0.0001:
		_death_cam.look_at(_death_cam_target, Vector3.UP)

func is_death_cam_active() -> bool:
	return _death_cam_active

func get_death_cam_angle() -> float:
	return _death_cam_angle

func get_death_cam_target() -> Vector3:
	return _death_cam_target

func get_death_cam_radius() -> float:
	return _death_cam_radius

func _on_enemy_destroyed(killer_loadout_key: String, victim_loadout_key: String) -> void:
	# If the player scored this kill, attribute to "You" rather than the
	# player's ship name (matches HTML line 3435).
	var player_scored := (killer_loadout_key == player.loadout_key)
	if player_scored:
		player_kills += 1
	var killer_name := "You" if player_scored else _resolve_ship_name(killer_loadout_key)
	var victim_name := _resolve_ship_name(victim_loadout_key)
	# Locate the victim EnemyShip so we can compare against _last_killed_by
	# (revenge), read its world position for the longshot range check, and
	# match the " [EXEC]" suffix against _pending_exec_victim by ship
	# reference (duplicate loadout keys otherwise could mis-fire).
	var victim_ship: EnemyShip = null
	for enemy in enemies:
		if enemy.loadout_key == victim_loadout_key and not enemy.is_alive():
			victim_ship = enemy
			break
	# Death explosion at the enemy's last position. HTML fires this from the
	# enemy death branch (around line 5703 in the web build); size mirrors the
	# player death scale so chassis destruction reads similarly regardless of
	# team. _handle_player_kill_cinematics also calls _play_audio("kill"), but
	# the kill SFX is a separate HUD cue from the explosion boom already
	# covered by the dynamic lights + shockwave here.
	if victim_ship != null and is_instance_valid(victim_ship):
		_spawn_explosion(victim_ship.global_position, 45.0)
	# Execution finisher suffix (HTML line 9600). _pending_exec_victim is set
	# in _execute_enemy; we clear it unconditionally so an unrelated kill in
	# the same frame can't inherit the " [EXEC]" tag.
	if _pending_exec_victim != null and victim_ship != null and _pending_exec_victim == victim_ship:
		victim_name += " [EXEC]"
	_pending_exec_victim = null
	if hud != null:
		hud.add_kill_feed_entry(killer_name, victim_name)
	if player_scored:
		_handle_player_kill_cinematics(victim_ship)
	else:
		_handle_bot_kill_cinematics(killer_loadout_key)

# HTML lines 3432-3466: tick the multikill streak, stamp firstBlood on the
# first player kill of the round, award longshot / revenge / shutdown medals
# where applicable, and flash the red X kill marker.
func _handle_player_kill_cinematics(victim_ship: EnemyShip) -> void:
	if hud == null:
		return
	hud.show_kill_marker()
	# Kill SFX paired with the red X marker (HTML 11178). Only fires for
	# player-scored kills; bot-vs-bot kills go through _handle_bot_kill_cinematics
	# which has its own audio hooks.
	_play_audio("kill")
	# Multikill window: chain if within MULTIKILL_WINDOW seconds of the last
	# kill, reset otherwise. _match_time is a monotonic counter driven by
	# _physics_process.
	if _last_kill_time > -100.0 and (_match_time - _last_kill_time) <= MULTIKILL_WINDOW:
		_streak_count += 1
	else:
		_streak_count = 1
	_last_kill_time = _match_time
	if _streak_count >= 2:
		hud.show_killstreak(_streak_count)
	# First blood: first kill of the round.
	if not _first_blood_claimed:
		_first_blood_claimed = true
		hud.show_medal("firstBlood")
	# Longshot: kill at > 1800 units.
	if victim_ship != null and player != null:
		var d2 := player.global_position.distance_squared_to(victim_ship.global_position)
		if d2 > LONGSHOT_RANGE_SQ:
			hud.show_medal("longshot")
	# Revenge: finished off the bot that last killed us.
	if victim_ship != null and _last_killed_by != null and victim_ship == _last_killed_by:
		hud.show_medal("revenge")
		_last_killed_by = null
	# Shutdown: the bot was on a streak of 3 or more when the player ended
	# them. Bot streaks are tracked in _bot_streaks.
	if victim_ship != null:
		var bot_streak: int = int(_bot_streaks.get(victim_ship, 0))
		if bot_streak >= 3:
			hud.show_medal("shutdown")

# Bot-on-bot or bot-on-player kill: extend the attacker's shutdown streak.
# Only the *killer* bot's streak ticks; the player's streak lives in
# _streak_count and is handled above. Multiple bots can share a loadout key,
# so we resolve by the first alive enemy that matches.
func _handle_bot_kill_cinematics(killer_loadout_key: String) -> void:
	var killer_ship: EnemyShip = null
	for enemy in enemies:
		if enemy.loadout_key == killer_loadout_key and enemy.is_alive():
			killer_ship = enemy
			break
	if killer_ship == null:
		return
	var current: int = int(_bot_streaks.get(killer_ship, 0))
	_bot_streaks[killer_ship] = current + 1

func _on_player_ability_activated(ability_id: String, ability_name: String, _slot: int) -> void:
	if hud == null:
		return
	var color: Color = CinematicOverlay.color_for_ability(ability_id)
	hud.show_ability_flash(ability_name, color)

func _resolve_ship_name(loadout_key: String) -> String:
	if loadout_key.is_empty():
		return "UNKNOWN"
	var loadout := GameData.get_loadout(loadout_key)
	return String(loadout.get("name", loadout_key))

# HTML last_ship_sailing.html:4473-4510 (spawnDynamicObjects). 2-3 clusters
# per non-spawn room (rooms where team == null) plus 3-6 clusters seeded in
# tunnel corridor points. Cluster scale 35-90 in rooms, 25-60 in tunnels.
func _spawn_hazards() -> void:
	_clear_hazards()
	if arena_map == null:
		return

	# Clusters in non-spawn rooms (center, flanking, etc.).
	for room_data in arena_map.rooms:
		var room: Dictionary = room_data
		if room.get("team", null) != null:
			continue
		var room_center := Vector3(room.get("position", Vector3.ZERO))
		var room_radius := float(room.get("radius", 0.0))
		var cluster_count := 2 + (randi() % 2)  # 2-3 clusters per room
		for i in range(cluster_count):
			var angle := randf() * TAU
			var dist := room_radius * (0.15 + randf() * 0.45)
			var y_offset := (randf() - 0.5) * room_radius * 0.6
			var pos := Vector3(
				room_center.x + cos(angle) * dist,
				room_center.y + y_offset,
				room_center.z + sin(angle) * dist
			)
			var cluster_scale_val := 35.0 + randf() * 55.0
			_spawn_cluster(pos, cluster_scale_val)

	# A few clusters in tunnels. The HTML filters corridor_points to tunnel
	# entries and picks a few at random, splicing them out of the pool so the
	# same slot isn't reused for a second cluster in the same round.
	var tunnel_points: Array = []
	for point_data in arena_map.corridor_points:
		var pt: Dictionary = point_data
		if String(pt.get("room_type", "")) == "tunnel":
			tunnel_points.append(pt)
	var tunnel_count := mini(6, maxi(3, int(float(tunnel_points.size()) / 5.0)))
	for c in range(tunnel_count):
		if tunnel_points.is_empty():
			break
		var idx := randi() % tunnel_points.size()
		var pt: Dictionary = tunnel_points[idx]
		tunnel_points.remove_at(idx)
		var pos := Vector3(pt.get("position", Vector3.ZERO))
		var cluster_scale_val := 25.0 + randf() * 35.0
		_spawn_cluster(pos, cluster_scale_val)

func _spawn_cluster(pos: Vector3, cluster_scale_val: float) -> void:
	var cluster := ClusterObstacle.new()
	hazard_root.add_child(cluster)
	cluster.configure(pos, cluster_scale_val, hazard_root)
	clusters.append(cluster)

func _clear_hazards() -> void:
	for cluster in clusters:
		if cluster != null and is_instance_valid(cluster):
			for child in cluster.children:
				if child != null and is_instance_valid(child):
					child.queue_free()
			cluster.children.clear()
			cluster.queue_free()
	clusters.clear()
	for obstacle in standalone_obstacles:
		if obstacle != null and is_instance_valid(obstacle):
			obstacle.queue_free()
	standalone_obstacles.clear()

# Per-frame tick: advance cluster rotations, fragment drift, damage flashes,
# and respawns; resolve ship-vs-obstacle collisions and fragment impacts.
# Ordering inside this function mirrors HTML updateDynamicObjects at lines
# 4512-4524: clusters first (so intact children follow the cluster spin this
# frame), then individual pieces.
func _update_hazards(delta: float) -> void:
	for cluster in clusters:
		if cluster == null or not is_instance_valid(cluster):
			continue
		cluster.update(delta)

	# Collect the list of targets once per frame. Bouncing off an obstacle can
	# mutate a ship's velocity; the caller applies those updates in place via
	# ship.velocity / global_position so subsequent obstacles in the same
	# frame see the corrected pose.
	var ships: Array = []
	if player != null and is_instance_valid(player) and player.is_alive() and not player.chassis.is_empty():
		ships.append({
			"node": player,
			"radius": float(player.chassis.get("hull_length", 100.0)) * SHIP_HULL_RADIUS_MULT,
			"team": PlayerShip.TEAM_PLAYER,
		})
	for enemy in enemies:
		if enemy != null and is_instance_valid(enemy) and enemy.is_alive() and not enemy.chassis.is_empty():
			ships.append({
				"node": enemy,
				"radius": float(enemy.chassis.get("hull_length", 100.0)) * SHIP_HULL_RADIUS_MULT,
				"team": EnemyShip.TEAM_ENEMY,
			})

	# Children of every cluster, plus the flat standalones list.
	for cluster in clusters:
		if cluster == null or not is_instance_valid(cluster):
			continue
		for child in cluster.children:
			_tick_obstacle(child, delta, ships)
	for obstacle in standalone_obstacles:
		_tick_obstacle(obstacle, delta, ships)

func _tick_obstacle(obstacle: DestructibleObstacle, delta: float, ships: Array) -> void:
	if obstacle == null or not is_instance_valid(obstacle):
		return
	obstacle.update(delta)
	if not obstacle.is_alive:
		return
	# Resolve each ship against this piece in turn. Broken fragments detonate
	# on the first contact; intact pieces bounce the ship and optionally take
	# ram damage back.
	if match_state != "playing":
		return
	for ship_data in ships:
		var ship: Node3D = ship_data["node"]
		if ship == null or not is_instance_valid(ship) or not ship.is_alive():
			continue
		var result := obstacle.collide_entity(ship.global_position, ship.velocity, float(ship_data["radius"]))
		if not bool(result.get("collided", false)):
			continue
		if bool(result.get("exploded", false)):
			# Broken fragment contact: damage the ship and retire the piece.
			var dmg := float(result.get("fragment_damage", 0.0))
			if dmg > 0.0:
				ship.apply_damage(dmg, obstacle.global_position, "debris")
			# The piece has already set is_alive=false inside collide_entity;
			# no further work for this obstacle against other ships.
			return
		ship.global_position = result.get("position", ship.global_position)
		ship.velocity = result.get("velocity", ship.velocity)
		var ram_damage := float(result.get("ram_damage", 0.0))
		if ram_damage > 0.0:
			obstacle.take_damage(ram_damage, result.get("normal", Vector3.ZERO))
			if not obstacle.is_alive:
				return

# Ray-vs-obstacles check for hitscan weapons and the projectile frame step.
# Walks every intact piece (cluster children + standalones) and returns the
# closest hit along [origin..origin+direction*max_range]. Broken fragments
# are skipped so hitscan lasers don't lock onto drifting debris.
func _find_obstacle_hit(origin: Vector3, direction: Vector3, max_range: float) -> Dictionary:
	var best: Dictionary = {}
	var best_distance := max_range
	for cluster in clusters:
		if cluster == null or not is_instance_valid(cluster):
			continue
		for child in cluster.children:
			var hit := _obstacle_ray_hit(child, origin, direction, best_distance)
			if not hit.is_empty():
				best = hit
				best_distance = float(hit["distance"])
	for obstacle in standalone_obstacles:
		var hit := _obstacle_ray_hit(obstacle, origin, direction, best_distance)
		if not hit.is_empty():
			best = hit
			best_distance = float(hit["distance"])
	return best

func _obstacle_ray_hit(obstacle: DestructibleObstacle, origin: Vector3, direction: Vector3, max_range: float) -> Dictionary:
	if obstacle == null or not is_instance_valid(obstacle):
		return {}
	if not obstacle.is_alive or obstacle.broken:
		return {}
	var hit := _ray_sphere_hit(origin, direction, obstacle.global_position, obstacle.collision_radius, max_range)
	if hit.is_empty():
		return {}
	hit["obstacle"] = obstacle
	return hit

# Sphere-based overlap check for projectile frame ticks. Called from inside
# _update_projectiles before the ship-hit check so a rocket that grazes a
# cluster child detonates on the obstacle instead of overshooting into a
# ship behind it.
func _find_obstacle_projectile_hit(position: Vector3, hit_radius: float) -> DestructibleObstacle:
	for cluster in clusters:
		if cluster == null or not is_instance_valid(cluster):
			continue
		for child in cluster.children:
			if child == null or not is_instance_valid(child):
				continue
			if not child.is_alive or child.broken:
				continue
			if child.global_position.distance_to(position) <= hit_radius + child.collision_radius:
				return child
	for obstacle in standalone_obstacles:
		if obstacle == null or not is_instance_valid(obstacle):
			continue
		if not obstacle.is_alive or obstacle.broken:
			continue
		if obstacle.global_position.distance_to(position) <= hit_radius + obstacle.collision_radius:
			return obstacle
	return null

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
			# HTML last_ship_sailing.html:6714-6732 deploys THREE proximity mines in
			# a lateral spread (±180 on the right vector, plus the centerline) so
			# one ability covers a wide area. 250u forward to match HTML line 6720.
			var tripwire_right := direction.cross(Vector3.UP).normalized()
			if tripwire_right.length_squared() < 0.001:
				tripwire_right = Vector3.RIGHT
			var tripwire_center := source_position + direction * 250.0
			for lateral_offset in [-180.0, 0.0, 180.0]:
				_spawn_mine(
					tripwire_center + tripwire_right * lateral_offset,
					220.0, 1.0, 12.0, 350.0 * damage_scale,
					team, loadout_key, signature, source
				)
		"firewall":
			# HTML last_ship_sailing.html:6450-6488 lays a STATIC 800u linear path
			# of fire starting 100u forward. 400 DPS, 5s duration. Not a moving
			# blob: the damage tick sweeps along the line each frame. Fire sources
			# (firewall/flame_core/thermite splash) also ignite nearby incendiary
			# gas clouds (handled in _update_world_effects below).
			_spawn_firewall(source_position + direction * 100.0, direction, 800.0, 5.0, 400.0 * damage_scale, team, loadout_key, signature, source)
		"incendiary_trap":
			# HTML last_ship_sailing.html:6739-6763 drops an inert 350u gas cloud
			# that does NOTHING until a fire source contacts it; once ignited it
			# burns for 10s at 450 DPS with a 50% slow applied every frame.
			_spawn_incendiary_gas(source_position + direction * 400.0, 350.0, 15.0, 450.0 * damage_scale, 10.0, 0.5, team, loadout_key, signature, source)
		"cluster_missile":
			_spawn_projectile(origin, direction, {"damage": 800.0 * damage_scale, "range": 2600.0, "projectile_speed": 900.0}, signature, loadout_key, team, source, {
				"explode_radius": 130.0,
				"blast_damage": 520.0 * damage_scale,
				"cluster_count": 5,
				"cluster_damage": 180.0 * damage_scale
			})
		"tether_trap":
			# HTML last_ship_sailing.html:6765-6777 deploys a proximity tether that
			# roots the first enemy to enter its 250u radius for 4s (velocity
			# zeroed per frame). Not a damage zone: the HTML only sets rootTarget
			# and forces velocity.set(0,0,0) during the rootDuration.
			_spawn_tether_trap(source_position + direction * 300.0, 250.0, 15.0, 4.0, team, loadout_key, signature, source)
		"arc_wave":
			_spawn_projectile(origin, direction, {"damage": 2000.0 * damage_scale, "range": 1800.0, "projectile_speed": 1200.0}, signature, loadout_key, team, source, {
				"explode_radius": 90.0,
				"blast_damage": 700.0 * damage_scale,
				"projectile_radius": 36.0,
				"is_arc_wave": true,
			})
		"tracker_rockets":
			_fire_tracker_rockets(source, origin, direction, loadout_key, team, signature, damage_scale)
		"particle_wall":
			_spawn_particle_wall(source_position + direction * 220.0, direction, 260.0, 160.0, 6.0, team, signature)
		"sonar_lock":
			_apply_sonar_lock(source, source_position, direction, team, signature)
		"power_shot":
			# Player starts a 1s charge (mode-aware release below). Bots don't
			# charge (their AI routes aren't wired for it), so they fire the
			# original hitscan immediately.
			if source is PlayerShip:
				(source as PlayerShip).start_power_shot_charge()
			else:
				var heavy_weapon := {"damage": 3200.0, "range": 3400.0}
				_fire_hitscan(origin, direction, heavy_weapon, signature, loadout_key, team, damage_scale, source)
		"power_shot_release":
			_fire_power_shot_release(source, origin, direction, loadout_key, team, signature, damage_scale)
		"rocket_salvo":
			var salvo_count := 10 if _source_has_missile_racks(source) else 5
			_spawn_homing_volley(origin, direction, salvo_count, 720.0 * damage_scale, team, loadout_key, signature, source)
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

	# Cluster children and standalone destructibles block hitscan too. An
	# obstacle hit ahead of any ship absorbs the shot entirely; a ship ahead
	# of the nearest obstacle still wins. The HTML does this implicitly via
	# game.dynamicObjects in the same ray loop (last_ship_sailing.html:4236).
	var obstacle_hit := _find_obstacle_hit(origin, aim_direction, best_distance)
	var obstacle_blocking := false
	if not obstacle_hit.is_empty():
		best_distance = float(obstacle_hit["distance"])
		target_point = obstacle_hit["point"]
		obstacle_blocking = true

	var best_hit := _find_hitscan_target(origin, aim_direction, ray_length, team)
	if not best_hit.is_empty() and float(best_hit["distance"]) < best_distance:
		best_distance = float(best_hit["distance"])
		target_point = best_hit["point"]
		var target: Object = best_hit["target"]
		var dealt := float(weapon_data.get("damage", 100.0)) * damage_scale
		# Hitscan range falloff (HTML last_ship_sailing.html:6207-6210 for player,
		# 3309-3312 for bots): full damage up close, 70% at the weapon's max
		# range. range_ratio is clamped to [0, 1] so shots that somehow travel
		# past the weapon's nominal range don't invert the falloff sign.
		var weapon_range := float(weapon_data.get("range", 2400.0))
		var range_ratio := clampf(1.0 - best_distance / maxf(1.0, weapon_range), 0.0, 1.0)
		dealt *= 0.7 + 0.3 * range_ratio
		# Bot damage scaling (HTML line 3306-3307): bots deal 60% of base damage
		# across the board. Applied after the falloff so both multipliers stack
		# as they do in the HTML (the HTML applies 0.6 first then falloff, but
		# the two are commutative so the order doesn't affect the product).
		if team == EnemyShip.TEAM_ENEMY:
			dealt *= 0.6
		dealt = _apply_arc_rounds_bonus(source, target, dealt)
		target.apply_damage(dealt, target_point, loadout_key)
		_register_tone_lock_on_hit(source, target)
		_register_enemy_tone_lock_on_hit(source, target)
		_track_player_damage(source, target, dealt)
		_award_core_charge(source, dealt)
		_spawn_impact_burst(target_point, signature)
	elif obstacle_blocking:
		# Obstacle was the closest thing in line: deal the full hit damage to
		# the piece (any hit shatters a cluster via take_damage) and spark at
		# the contact point. No tone-lock / damage-tally paths; obstacles
		# aren't ships.
		var obstacle: DestructibleObstacle = obstacle_hit["obstacle"]
		var dealt := float(weapon_data.get("damage", 100.0)) * damage_scale
		var hit_dir := -aim_direction
		obstacle.take_damage(dealt, hit_dir)
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
	# Bot damage scaling (HTML last_ship_sailing.html:3306-3307): pre-scale at
	# spawn time so the stored damage already carries the 0.6 multiplier.
	# Mirror-applies to the blast / cluster children so bot rockets don't get
	# scaled impact damage with unscaled splash.
	var bot_scale := 0.6 if team == EnemyShip.TEAM_ENEMY else 1.0
	var base_damage := float(weapon_data.get("damage", 500.0)) * bot_scale
	var blast_damage := float(extra.get("blast_damage", 0.0)) * bot_scale
	var cluster_damage := float(extra.get("cluster_damage", 0.0)) * bot_scale
	var projectile_data := {
		"node": projectile_node,
		"position": origin,
		"velocity": velocity,
		"ttl": float(weapon_data.get("range", 2500.0)) / maxf(1.0, projectile_speed),
		"radius": projectile_radius,
		"damage": base_damage,
		"loadout_key": loadout_key,
		"team": team,
		"source": source,
		"signature": signature,
		"explode_radius": float(extra.get("explode_radius", 0.0)),
		"blast_damage": blast_damage,
		"cluster_count": int(extra.get("cluster_count", 0)),
		"cluster_damage": cluster_damage,
		"homing_target": extra.get("homing_target", null),
		"turn_rate": float(extra.get("turn_rate", 4.2)),
		# Arc-wave projectiles (HTML 3622-3640) emit forward-ahead lightning
		# bolts on a 4-7 Hz cadence. The timer is seeded to 0 so the first
		# update() tick fires immediately; spawn-site passes the flag.
		"is_arc_wave": bool(extra.get("is_arc_wave", false)),
		"arc_light_timer": 0.0,
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

# Short arc-wave bolt (HTML last_ship_sailing.html:3631 spawnLightningBolt):
# split start->end into 3 segments with perpendicular jitter on the middle
# joints, render in blue-white via the existing tracer pools, 0.10s lifetime.
# Reuses tracer_core for the bright inner thread and tracer_glow for the
# outer halo so we don't add a dedicated lightning renderer for a secondary
# visual effect.
func _spawn_arc_wave_bolt(from: Vector3, to: Vector3) -> void:
	if tracer_core == null or tracer_glow == null:
		return
	var segment := to - from
	var length := segment.length()
	if length < 0.001:
		return
	var axis := segment / length
	# Pick any perpendicular for the jitter plane. UP.cross(axis) collapses
	# when axis is ~vertical, so fall back to FORWARD in that case.
	var perp := Vector3.UP.cross(axis)
	if perp.length_squared() < 0.0001:
		perp = Vector3.FORWARD.cross(axis)
	perp = perp.normalized()
	var perp2 := axis.cross(perp).normalized()

	var jitter_amp := length * 0.08
	var p1 := from + axis * (length * 0.33) + perp * randf_range(-jitter_amp, jitter_amp) + perp2 * randf_range(-jitter_amp, jitter_amp)
	var p2 := from + axis * (length * 0.66) + perp * randf_range(-jitter_amp, jitter_amp) + perp2 * randf_range(-jitter_amp, jitter_amp)

	# 0x44aaff (HTML line 3631) = near-cyan; tracer_core carries the white-hot
	# core thread for 0.10s, tracer_glow carries the cyan halo slightly longer
	# so the bolt fades out with a soft glow instead of popping off.
	var core_color := Color(0.85, 0.95, 1.0, 1.0)
	var glow_color := Color(0.27, 0.67, 1.0, 1.0)
	var core_lifetime := 0.10
	var glow_lifetime := 0.14
	var core_width := 0.22
	var glow_width := 0.55

	tracer_core.spawn_segment(from, p1, core_color, core_width, core_lifetime)
	tracer_core.spawn_segment(p1, p2, core_color, core_width, core_lifetime)
	tracer_core.spawn_segment(p2, to, core_color, core_width, core_lifetime)
	tracer_glow.spawn_segment(from, p1, glow_color, glow_width, glow_lifetime)
	tracer_glow.spawn_segment(p1, p2, glow_color, glow_width, glow_lifetime)
	tracer_glow.spawn_segment(p2, to, glow_color, glow_width, glow_lifetime)

# Thin dispatcher for the impact-spark cascade (HTML 5290-5347). The whole
# effect lives on ExplosionFX now: flash sphere, streaks, ember burst, optional
# scorch puff, two dynamic lights. We keep this signature so existing callers
# (projectile hits, beam impacts) keep working.
func _spawn_impact_burst(position: Vector3, signature: Dictionary) -> void:
	if explosion_fx == null or not is_instance_valid(explosion_fx):
		return
	var impact_color: Color = GameData.color_from_hex(int(signature.get("impact_light_color", 0xffcc66)))
	explosion_fx.spawn_impact_sparks(position, 6, impact_color)

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

func _spawn_firewall(position: Vector3, direction: Vector3, length: float, duration: float, damage_per_second: float, team: int, loadout_key: String, signature: Dictionary, source: Node3D) -> void:
	# Ports HTML last_ship_sailing.html:6450-6488. Static 800u linear fire path
	# rendered as a chain of 8 additive planes along the direction vector. Unlike
	# _spawn_zone (moving sphere), this applies damage to anything whose closest
	# point on the line is within 150u perpendicular.
	var normalized_direction := direction.normalized()
	if normalized_direction.length_squared() < 0.001:
		normalized_direction = Vector3.FORWARD
	var segment_count := 8
	var segment_length := length / float(segment_count)
	var container := Node3D.new()
	container.global_position = position
	effect_root.add_child(container)
	var fire_color := GameData.color_from_hex(0xff5500)
	for segment_index in range(segment_count):
		var segment_mid := normalized_direction * (segment_length * (float(segment_index) + 0.5))
		var plane_mesh := QuadMesh.new()
		plane_mesh.size = Vector2(segment_length, 120.0)
		var plane_node := MeshInstance3D.new()
		plane_node.mesh = plane_mesh
		var plane_material := StandardMaterial3D.new()
		plane_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		plane_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		plane_material.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
		plane_material.cull_mode = BaseMaterial3D.CULL_DISABLED
		plane_material.albedo_color = Color(fire_color.r, fire_color.g, fire_color.b, 0.25)
		plane_material.emission_enabled = true
		plane_material.emission = fire_color
		plane_material.emission_energy_multiplier = 2.0
		plane_node.material_override = plane_material
		plane_node.position = segment_mid
		# Orient the quad perpendicular to the firewall so the flame ribbon is
		# visible from the side (matches HTML line 6477 which does the same
		# `planeMesh.lookAt(mid + perpendicular)` trick).
		var perpendicular := Vector3(-normalized_direction.z, 0.0, normalized_direction.x)
		if perpendicular.length_squared() < 0.001:
			perpendicular = Vector3.RIGHT
		plane_node.look_at(plane_node.global_position + perpendicular, Vector3.UP)
		container.add_child(plane_node)

	world_effects.append({
		"type": "firewall",
		"node": container,
		"position": position,
		"direction": normalized_direction,
		"length": length,
		"timer": duration,
		"dps": damage_per_second,
		"team": team,
		"source": source,
		"loadout_key": loadout_key,
		"signature": signature,
		# Firewalls are a fire source for incendiary gas ignition. The gas
		# handler looks for any world effect flagged is_fire_source == true in
		# its proximity check. flame_core blasts set the same flag on the short
		# _spawn_zone they emit.
		"is_fire_source": true
	})

func _spawn_incendiary_gas(position: Vector3, radius: float, duration: float, ignite_dps: float, ignite_duration: float, slow_factor: float, team: int, loadout_key: String, signature: Dictionary, source: Node3D) -> void:
	# Ports HTML last_ship_sailing.html:6739-6763. Spawns an INERT gas cloud. The
	# cloud only ignites when a fire source (firewall, flame_core, thermite
	# splash) touches its proximity; the update tick watches world_effects for
	# any effect with is_fire_source == true and flips "ignited" on when the
	# sphere overlaps the source. Once lit, the cloud burns for ignite_duration
	# dealing ignite_dps + a per-frame slow_factor velocity scale.
	var gas_mesh := SphereMesh.new()
	gas_mesh.radius = radius
	gas_mesh.height = radius * 2.0
	var node := MeshInstance3D.new()
	node.mesh = gas_mesh
	var gas_color := GameData.color_from_hex(0x88aa33)
	var gas_material := StandardMaterial3D.new()
	gas_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	gas_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	gas_material.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	gas_material.albedo_color = Color(gas_color.r, gas_color.g, gas_color.b, 0.12)
	gas_material.emission_enabled = true
	gas_material.emission = gas_color
	gas_material.emission_energy_multiplier = 0.8
	node.material_override = gas_material
	node.global_position = position
	effect_root.add_child(node)

	world_effects.append({
		"type": "incendiary_gas",
		"node": node,
		"material": gas_material,
		"position": position,
		"radius": radius,
		"timer": duration,
		"ignited": false,
		"ignite_dps": ignite_dps,
		"ignite_timer": 0.0,
		"ignite_duration": ignite_duration,
		"slow_factor": slow_factor,
		"team": team,
		"source": source,
		"loadout_key": loadout_key,
		"signature": signature
	})

func _spawn_tether_trap(position: Vector3, radius: float, duration: float, root_duration: float, team: int, loadout_key: String, signature: Dictionary, source: Node3D) -> void:
	# Ports HTML last_ship_sailing.html:6765-6777. Octahedron anchor that sits
	# idle until an enemy enters its radius; on first contact, latches that
	# enemy and zeroes their velocity every frame for root_duration seconds.
	# Pure crowd-control, no damage (the HTML only calls velocity.set(0,0,0)).
	var tether_mesh := SphereMesh.new()
	tether_mesh.radius = 14.0
	tether_mesh.height = 28.0
	var node := MeshInstance3D.new()
	node.mesh = tether_mesh
	var tether_color := GameData.color_from_hex(0x44aaff)
	var tether_material := StandardMaterial3D.new()
	tether_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	tether_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	tether_material.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	tether_material.albedo_color = Color(tether_color.r, tether_color.g, tether_color.b, 0.8)
	tether_material.emission_enabled = true
	tether_material.emission = tether_color
	tether_material.emission_energy_multiplier = 2.4
	node.material_override = tether_material
	node.global_position = position
	effect_root.add_child(node)

	world_effects.append({
		"type": "tether",
		"node": node,
		"position": position,
		"radius": radius,
		"timer": duration,
		"triggered": false,
		"root_target": null,
		"root_timer": 0.0,
		"root_duration": root_duration,
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
			# Descent-3 two-tier tracking (HTML last_ship_sailing.html:3528-3563):
			# close range tracks aggressively with a loose FOV (can chase slightly
			# behind); far range softens the turn rate and tightens the FOV so a
			# target that dodges off-axis can outmaneuver the missile. Outside the
			# FOV cone the missile coasts straight; the dodge is what makes
			# distance matter at all.
			var to_target := homing_target.global_position - current_position
			var distance := to_target.length()
			if distance > 0.001 and velocity.length_squared() > 0.0001:
				var to_target_dir := to_target / distance
				var velocity_dir := velocity.normalized()
				var fov := ProjectileMath.compute_homing_fov(distance)
				if ProjectileMath.should_steer_homing(velocity_dir, to_target_dir, fov):
					var turn_rate := ProjectileMath.compute_homing_turn_rate(distance)
					velocity = velocity_dir.slerp(to_target_dir, clampf(turn_rate * delta, 0.0, 1.0)) * velocity.length()
					projectile["velocity"] = velocity

		# Arc-wave bolt emission (HTML last_ship_sailing.html:3622-3640). Ticks
		# an internal timer; when it fires, spawn a forward-ahead lightning
		# bolt, reset to a 4-7 Hz interval. The bolt itself is 3 jittered
		# tracer-glow segments in blue (color 0x44aaff); cheap, reuses the
		# existing tracer pool, gives the "arcing lightning" look without a
		# dedicated lightning renderer.
		if bool(projectile.get("is_arc_wave", false)) and velocity.length_squared() > 0.0001:
			var arc_timer := float(projectile.get("arc_light_timer", 0.0)) - delta
			if arc_timer <= 0.0:
				var ahead_dist := ProjectileMath.ARC_WAVE_AHEAD_MIN + randf() * ProjectileMath.ARC_WAVE_AHEAD_RANGE
				var bolt_end := current_position + velocity.normalized() * ahead_dist + Vector3(
					(randf() - 0.5) * ProjectileMath.ARC_WAVE_JITTER,
					(randf() - 0.5) * ProjectileMath.ARC_WAVE_JITTER,
					(randf() - 0.5) * ProjectileMath.ARC_WAVE_JITTER,
				)
				_spawn_arc_wave_bolt(current_position, bolt_end)
				arc_timer = ProjectileMath.ARC_WAVE_BOLT_MIN + randf() * (ProjectileMath.ARC_WAVE_BOLT_MAX - ProjectileMath.ARC_WAVE_BOLT_MIN)
			projectile["arc_light_timer"] = arc_timer

		var next_position := current_position + velocity * delta

		# Look 5 units past the bullet's frame-end position to match HTML
		# `raycastLevel(prevPos, moveDir, moveDist + 5)` in last_ship_sailing.html:3658,
		# so projectiles whose edge grazes a wall stop against it instead of
		# visually overshooting.
		var wall_probe_end := next_position
		if velocity.length_squared() > 0.0:
			wall_probe_end = next_position + velocity.normalized() * 5.0
		var wall_hit := _find_blocking_wall_hit(current_position, wall_probe_end, int(projectile["team"]))
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

		# Cluster children and standalone destructibles block projectiles the
		# same as walls: an obstacle in the projectile's path detonates the
		# round on the obstacle and deals the warhead damage through
		# take_damage so cluster shatter cascades fire (HTML 4286-4302).
		var hit_obstacle := _find_obstacle_projectile_hit(next_position, float(projectile["radius"]))
		if hit_obstacle != null:
			var hit_dir := Vector3.ZERO
			if velocity.length_squared() > 0.0:
				hit_dir = -velocity.normalized()
			hit_obstacle.take_damage(float(projectile["damage"]), hit_dir)
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
			"firewall":
				# HTML last_ship_sailing.html:7408-7458. Damages any target whose
				# closest-point-on-line is within 150u. Applied per-frame (dps *
				# dt) to match the HTML's `eff.dmgPerSec * dt`.
				var fw_direction: Vector3 = effect["direction"]
				var fw_length: float = float(effect["length"])
				var fw_dps: float = float(effect["dps"])
				var fw_team: int = int(effect["team"])
				var fw_source: Node3D = effect.get("source", null) as Node3D
				var fw_radius := 150.0
				var fw_targets := _find_ships_along_line(effect["position"], fw_direction, fw_length, fw_radius, fw_team)
				for fw_target in fw_targets:
					var fw_damage := fw_dps * delta
					fw_target.apply_damage(fw_damage, fw_target.global_position, String(effect["loadout_key"]))
					_track_player_damage(fw_source, fw_target, fw_damage)
			"incendiary_gas":
				# HTML last_ship_sailing.html:7480-7611. Two-phase effect.
				var gas_material: StandardMaterial3D = effect.get("material", null) as StandardMaterial3D
				if bool(effect.get("ignited", false)):
					effect["ignite_timer"] = maxf(0.0, float(effect["ignite_timer"]) - delta)
					var gas_targets := _get_targets_in_radius(effect["position"], float(effect["radius"]), int(effect["team"]))
					var gas_source: Node3D = effect.get("source", null) as Node3D
					var tick_damage := float(effect["ignite_dps"]) * delta
					var slow_scale := 1.0 - float(effect["slow_factor"]) * delta
					for gas_target in gas_targets:
						gas_target.apply_damage(tick_damage, gas_target.global_position, String(effect["loadout_key"]))
						_track_player_damage(gas_source, gas_target, tick_damage)
						if gas_target.has_method("scale_velocity"):
							gas_target.scale_velocity(slow_scale)
					if float(effect["ignite_timer"]) <= 0.0:
						effect["timer"] = 0.0
				else:
					# Inert gas cloud. Look for any active fire source nearby
					# and ignite on contact. Fire sources are tagged with
					# is_fire_source == true; only firewalls do this today but
					# flame_core blasts and thermite splashes can adopt the
					# same flag later without touching this code.
					for other in world_effects:
						if other == effect:
							continue
						if not bool(other.get("is_fire_source", false)):
							continue
						var other_pos: Vector3 = other.get("position", Vector3.ZERO)
						var ignite_radius := float(effect["radius"]) + 150.0
						if other_pos.distance_to(effect["position"]) < ignite_radius:
							effect["ignited"] = true
							effect["ignite_timer"] = float(effect["ignite_duration"])
							if gas_material != null:
								gas_material.albedo_color = Color(1.0, 0.27, 0.0, 0.22)
								gas_material.emission = Color(1.0, 0.4, 0.0)
								gas_material.emission_energy_multiplier = 2.4
							break
			"tether":
				# HTML last_ship_sailing.html:7614-7632. First enemy in radius
				# latches; velocity zeroed every frame until root_timer expires.
				if not bool(effect["triggered"]):
					var tether_targets := _get_targets_in_radius(effect["position"], float(effect["radius"]), int(effect["team"]))
					if not tether_targets.is_empty():
						effect["triggered"] = true
						effect["root_target"] = tether_targets[0]
						effect["root_timer"] = float(effect["root_duration"])
				else:
					var rooted: Node3D = effect.get("root_target", null) as Node3D
					if rooted != null and is_instance_valid(rooted) and rooted.has_method("is_alive") and rooted.is_alive():
						effect["root_timer"] = maxf(0.0, float(effect["root_timer"]) - delta)
						if rooted.has_method("set_velocity"):
							rooted.set_velocity(Vector3.ZERO)
						elif "velocity" in rooted:
							rooted.set("velocity", Vector3.ZERO)
						if float(effect["root_timer"]) <= 0.0:
							effect["timer"] = 0.0
					else:
						effect["timer"] = 0.0
			"stasis":
				# HTML last_ship_sailing.html:9464-9533. Static pickup zone.
				# Pulsing visuals plus a 120u pickup check against the player
				# and any alive bot (bots instantly grab it if they're below
				# max shield; player entry triggers the 3s immobilize/recharge
				# via PlayerShip.enter_stasis).
				var stasis_visual: Node3D = effect["node"]
				if stasis_visual != null and is_instance_valid(stasis_visual):
					var stasis_pulse := 1.0 + sin(Time.get_ticks_msec() * 0.003) * 0.12
					stasis_visual.scale = Vector3.ONE * stasis_pulse
				_check_stasis_pickup(effect, index)
				# Pickup callbacks may have already removed the effect; the
				# early-continue keeps us from writing back to a dead slot.
				if index >= world_effects.size() or world_effects[index] != effect:
					continue

		world_effects[index] = effect

func _apply_arc_rounds_bonus(source: Node3D, target: Object, damage: float) -> float:
	# MONARCH Tier 1 Arc Rounds (HTML last_ship_sailing.html:6222-6223):
	# +50% damage against any target that still has shield. The bonus applies
	# before apply_damage, so partial-shield hits get the boost on the part
	# that lands on shield (the HTML matches by reading bestHit.shield > 0
	# from the outside before calling takeDamage).
	if source == null or not is_instance_valid(source):
		return damage
	if target == null or not is_instance_valid(target):
		return damage
	if not source.get("monarch_arc_rounds"):
		return damage
	var shield_value := 0.0
	if target.has_method("get"):
		shield_value = float(target.get("shield"))
	if shield_value > 0.0:
		return damage * 1.5
	return damage

func _register_tone_lock_on_hit(source: Node3D, target: Object) -> void:
	# Any TONE hit on an enemy adds +1 lock on the player's tone_locks dict
	# (HTML last_ship_sailing.html:3387-3389 mirrors this for the reverse
	# direction). Only the player side builds lock stacks for Tracker Rockets;
	# bots don't consume stacks so we skip the reverse indirection.
	if source == null or not is_instance_valid(source):
		return
	if not (source is PlayerShip):
		return
	if String(source.get("loadout_key")) != "TONE":
		return
	var enemy := target as EnemyShip
	if enemy == null or not is_instance_valid(enemy):
		return
	(source as PlayerShip).add_tone_lock(enemy, 1)

func _register_enemy_tone_lock_on_hit(source: Node3D, target: Object) -> void:
	# Inverse of the above: when a TONE bot hits the player, the player's
	# enemy_tone_locks dict builds up per-bot (max 3) so the HUD / audio
	# can react to being painted (HTML 3386-3390).
	if source == null or not is_instance_valid(source):
		return
	if not (source is EnemyShip):
		return
	if String(source.get("loadout_key")) != "TONE":
		return
	if target == null or not (target is PlayerShip):
		return
	(target as PlayerShip).register_enemy_tone_lock(source as EnemyShip)

func _source_has_missile_racks(source: Node3D) -> bool:
	if source == null or not is_instance_valid(source):
		return false
	return bool(source.get("monarch_missile_racks"))

func _apply_sonar_lock(source: Node3D, source_position: Vector3, direction: Vector3, team: int, signature: Dictionary) -> void:
	# Pulse over a wide cone; every enemy inside 2000 units with forward·to ≥ 0.3
	# accrues +1 lock on player.tone_locks (max 3). Matches HTML 6779-6796.
	if source == null or not is_instance_valid(source):
		return
	var is_player_source := source is PlayerShip
	var lock_range := 2000.0
	var aim := direction.normalized()
	var marked_any := false
	if is_player_source and player != null:
		for enemy in enemies:
			if enemy == null or not enemy.is_alive():
				continue
			var to_enemy := enemy.global_position - source_position
			var dist := to_enemy.length()
			if dist > lock_range:
				continue
			if aim.dot(to_enemy.normalized()) < 0.3:
				continue
			var locks := player.add_tone_lock(enemy, 1)
			if locks > 0:
				marked_any = true
				_spawn_tracer(source_position, enemy.global_position, signature)
		if marked_any and is_instance_valid(player.tone_locked_target):
			tracked_enemy = player.tone_locked_target
	else:
		# Enemy-source branch: single-target marker (original behaviour).
		var marked := _find_priority_target(source_position, direction, lock_range, team)
		if marked != null and is_instance_valid(marked):
			_spawn_impact_burst(marked.global_position, signature)

func _fire_tracker_rockets(source: Node3D, origin: Vector3, direction: Vector3, loadout_key: String, team: int, signature: Dictionary, damage_scale: float) -> void:
	# If player has any fully-locked targets, fire 5 homing rockets at each
	# (consuming those full locks). Otherwise fire an unguided 5-rocket volley.
	# Partial locks on other enemies survive the volley (HTML 6507-6540).
	if source is PlayerShip:
		var locked_ids: Array = (source as PlayerShip).consume_full_tone_locks()
		if not locked_ids.is_empty():
			for locked_id in locked_ids:
				var enemy := instance_from_id(int(locked_id)) as EnemyShip
				if enemy == null or not enemy.is_alive():
					continue
				var to_enemy := (enemy.global_position - origin).normalized()
				_spawn_homing_volley(origin, to_enemy, 5, 1000.0 * damage_scale, team, loadout_key, signature, source)
			return
	# Fallback: unguided salvo (bots always take this path; players with only
	# partial locks also fall through here).
	_spawn_homing_volley(origin, direction, 5, 640.0 * damage_scale, team, loadout_key, signature, source)

func _fire_power_shot_release(source: Node3D, origin: Vector3, direction: Vector3, loadout_key: String, team: int, signature: Dictionary, damage_scale: float) -> void:
	# Charge has completed; the mode at release time determines payload.
	# Close mode: shotgun (12 pellets, wide spread, per-pellet knockback).
	# Long mode: high-damage piercing hitscan (HTML firePowerShot 6809-6862).
	var mode := "close"
	if source != null and is_instance_valid(source):
		mode = String(source.get("legion_mode"))
	if mode == "close":
		var pellet_weapon := {"damage": 270.0, "range": 1200.0}
		var spread := 0.12
		for pellet in range(12):
			var pellet_dir := (
				direction +
				Vector3(
					randf_range(-spread, spread),
					randf_range(-spread, spread),
					randf_range(-spread, spread)
				)
			).normalized()
			_fire_hitscan(origin, pellet_dir, pellet_weapon, signature, loadout_key, team, damage_scale, source)
	else:
		# Long-mode Power Shot: 3200 dmg, 3500 range hitscan
		var heavy_weapon := {"damage": 3200.0, "range": 3500.0}
		_fire_hitscan(origin, direction, heavy_weapon, signature, loadout_key, team, damage_scale, source)

func _apply_zone_damage(effect: Dictionary, delta: float) -> void:
	var damage := float(effect["dps"]) * delta
	var zone_source: Node3D = effect.get("source", null) as Node3D
	for target in _get_targets_in_radius(effect["position"], float(effect["radius"]), int(effect["team"])):
		target.apply_damage(damage, effect["position"], String(effect["loadout_key"]))
		_track_player_damage(zone_source, target, damage)
		_award_core_charge(zone_source, damage)

# Ship-ship soft repulsion + hard ram pass (HTML resolveShipShipCollisions,
# lines 2233-2328). Runs every physics frame during active rounds; no-ops
# during warmup/round_end so respawn positioning can't kick ships around
# before play resumes. The immunity for a dashing attacker is handled
# inside apply_damage on each ship (phase_dash early-returns), so we just
# apply ram damage to both parties and let state gating sort it out.
func _resolve_ship_ship_collisions(delta: float) -> void:
	if match_state != "playing":
		return
	var ships: Array = []
	if player != null and player.is_alive() and not player.chassis.is_empty():
		ships.append({
			"node": player,
			"is_player": true,
			"radius": float(player.chassis.get("hull_length", 100.0)) * SHIP_HULL_RADIUS_MULT,
		})
	for enemy in enemies:
		if not enemy.is_alive() or enemy.chassis.is_empty():
			continue
		ships.append({
			"node": enemy,
			"is_player": false,
			"radius": float(enemy.chassis.get("hull_length", 100.0)) * SHIP_HULL_RADIUS_MULT,
		})

	for i in range(ships.size()):
		for j in range(i + 1, ships.size()):
			var a: Dictionary = ships[i]
			var b: Dictionary = ships[j]
			var a_node: Node3D = a["node"]
			var b_node: Node3D = b["node"]
			var diff := a_node.global_position - b_node.global_position
			var min_dist := float(a["radius"]) + float(b["radius"])
			var repulse_dist := min_dist * SHIP_REPULSE_RANGE
			var dist_sq := diff.length_squared()
			if dist_sq >= repulse_dist * repulse_dist:
				continue
			var dist := sqrt(dist_sq)
			if dist < 0.1:
				# Degenerate overlap: split on world Y so both ships unstick.
				a_node.global_position = a_node.global_position + Vector3(0.0, min_dist * 0.5, 0.0)
				b_node.global_position = b_node.global_position + Vector3(0.0, -min_dist * 0.5, 0.0)
				continue
			var normal := diff / dist
			if dist < min_dist:
				# Hard contact: separate, reflect, potentially deal ram damage.
				# The +1.0 pad on half-penetration matches the HTML's extra
				# unit of slack so floating-point jitter can't keep ships
				# wedged on the next frame.
				var penetration := min_dist - dist
				var half_pen := penetration * 0.5 + 1.0
				a_node.global_position = a_node.global_position + normal * half_pen
				b_node.global_position = b_node.global_position + normal * (-half_pen)
				var rel_velocity: Vector3 = a_node.velocity - b_node.velocity
				var rel_vn := rel_velocity.dot(normal)
				if rel_vn < 0.0:
					var impulse := rel_vn * RAM_BOUNCE_COEFF
					a_node.velocity -= normal * impulse
					b_node.velocity += normal * impulse
					var impact_speed := absf(rel_vn)
					if impact_speed > RAM_IMPACT_THRESHOLD:
						_apply_ram_damage(a_node, b_node, impact_speed * RAM_DAMAGE_MULT, bool(a["is_player"]), bool(b["is_player"]))
			else:
				# Soft push zone: gentle ratio-squared repulse before contact.
				var ratio := 1.0 - (dist / repulse_dist)
				var force := SHIP_REPULSE_STRENGTH * ratio * ratio * delta
				a_node.velocity += normal * (force * 0.5)
				b_node.velocity -= normal * (force * 0.5)

# Ram-damage dispatcher. Both parties receive `damage`; the dasher (if any)
# eats their blow via phase_dash's early-return inside apply_damage. Player
# damage tallies only increment when the player actually hurt an enemy;
# bot-vs-bot and bot-vs-player contributions are ignored so the scoreboard
# doesn't inflate from ambient chaos.
func _apply_ram_damage(a_node: Node3D, b_node: Node3D, damage: float, a_is_player: bool, b_is_player: bool) -> void:
	if damage <= 0.0:
		return
	var contact: Vector3 = (a_node.global_position + b_node.global_position) * 0.5
	var a_key: String = player.loadout_key if a_is_player else (a_node as EnemyShip).loadout_key
	var b_key: String = player.loadout_key if b_is_player else (b_node as EnemyShip).loadout_key
	var player_hit_enemy_a: bool = (not a_is_player) and b_is_player and a_node.is_alive()
	var player_hit_enemy_b: bool = (not b_is_player) and a_is_player and b_node.is_alive()
	a_node.apply_damage(damage, contact, b_key)
	b_node.apply_damage(damage, contact, a_key)
	if player_hit_enemy_a:
		player_damage_dealt += damage
		if hud != null:
			hud.show_hit_marker()
		_play_audio("hit")
	if player_hit_enemy_b:
		player_damage_dealt += damage
		if hud != null:
			hud.show_hit_marker()
		_play_audio("hit")

# Execution finisher pass (HTML checkExecutions, lines 9563-9631). Runs before
# ship-ship collisions so a doomed enemy inside the exec radius gets credited
# to the player's finisher rather than whatever ram happens on the same frame.
# Bidirectional: a doomed player in enemy range gets executed too, with the
# attacking enemy's shields refilled.
func _check_executions() -> void:
	if match_state != "playing":
		return
	if player == null or not player.is_alive() or player.chassis.is_empty():
		return
	var hull_length := float(player.chassis.get("hull_length", 100.0))
	var exec_radius := hull_length * EXEC_RADIUS_MULT
	var exec_radius_sq := exec_radius * exec_radius
	# Player finisher on a doomed enemy. First match wins; return after one
	# execution so shield/core gains can't stack from overlapping doomed
	# enemies on the same frame.
	for enemy in enemies:
		if not enemy.is_alive() or not enemy.doomed:
			continue
		if player.global_position.distance_squared_to(enemy.global_position) < exec_radius_sq:
			_execute_enemy(enemy)
			return
	# Enemy finisher on a doomed player. The HTML runs this as an else branch
	# inside the same function; order doesn't matter because only one of the
	# two sides can be doomed at a time in practice.
	if player.is_doomed():
		for enemy in enemies:
			if not enemy.is_alive():
				continue
			if player.global_position.distance_squared_to(enemy.global_position) < exec_radius_sq:
				_execute_player(enemy)
				return

# Player's finisher hook. The dealt-damage credit captures the pre-kill pool
# (health + shield) so the scoreboard records the full pool the finisher
# consumed, not just the overkill amount. apply_damage is given +1.0 over
# the pool so any residual mitigation on the target still lands a kill.
func _execute_enemy(enemy: EnemyShip) -> void:
	if not enemy.is_alive():
		return
	var dealt: float = enemy.health + enemy.shield
	_pending_exec_victim = enemy
	enemy.apply_damage(dealt + 1.0, enemy.global_position, player.loadout_key)
	player.core_meter = clampf(player.core_meter + EXEC_CORE_GAIN, 0.0, 100.0)
	player.shield = player.max_shield
	player_damage_dealt += maxf(0.0, dealt)
	if hud != null:
		hud.show_medal("execution")
		hud.show_kill_marker()
	# Execution kill SFX. Doubles the regular kill audio through the same
	# pool, which the HTML also does (both sounds fire at executeEnemy).
	_play_audio("kill")
	player.add_screen_shake(EXEC_SCREEN_SHAKE)
	_spawn_impact_burst(enemy.global_position, GameData.get_signature(enemy.loadout_key))

# Enemy's finisher on the doomed player. The attacking bot's shield is
# refilled before the lethal damage lands (HTML line 9613) so the visible
# result matches: the player falls, the ramming bot walks away healthy.
func _execute_player(killer: EnemyShip) -> void:
	if not player.is_alive():
		return
	_pending_player_exec = true
	killer.shield = killer.max_shield
	var lethal: float = player.health + player.shield + 1.0
	player.apply_damage(lethal, player.global_position, killer.loadout_key)
	_spawn_impact_burst(player.global_position, GameData.get_signature(killer.loadout_key))

func _detonate_projectile(index: int, position: Vector3, hit_target: Object) -> void:
	var projectile: Dictionary = projectiles[index]
	var loadout_key := String(projectile["loadout_key"])
	var source: Node3D = projectile.get("source", null) as Node3D
	var signature: Dictionary = projectile["signature"]
	var base_damage := float(projectile["damage"])

	if hit_target != null:
		var direct_damage := _apply_arc_rounds_bonus(source, hit_target, base_damage)
		hit_target.apply_damage(direct_damage, position, loadout_key)
		_register_tone_lock_on_hit(source, hit_target)
		_register_enemy_tone_lock_on_hit(source, hit_target)
		_track_player_damage(source, hit_target, direct_damage)
		_award_core_charge(source, direct_damage)

	var explode_radius := float(projectile.get("explode_radius", 0.0))
	var blast_damage := float(projectile.get("blast_damage", 0.0))
	if explode_radius > 0.0 and blast_damage > 0.0:
		_blast_area(position, explode_radius, blast_damage, int(projectile["team"]), loadout_key, signature, source)
		# Explosion SFX keyed off actual blast detonation (HTML 11180). Missiles
		# without explode_radius stay silent on impact; the hit SFX still fires
		# from _track_player_damage above.
		_play_audio("explosion")

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
	# Visible fireball + embers + dynamic lights. Size scales with the blast
	# radius; HTML uses a similar `size` parameter directly in world units.
	# Small clusters (~75 radius) get a size ~24; heavy core blasts (~340) get
	# size ~70, triggering all 5 explosion phases including the perpendicular
	# torus shockwave.
	_spawn_explosion(position, clampf(radius * 0.18 + 8.0, 12.0, 80.0))
	# AOE contribution to shake: small kick with the blast radius's own falloff.
	_shake_from_event(position, minf(1.5, 0.25 + damage / 1800.0), maxf(radius * 4.0, 1500.0))

# Thin dispatcher: the explosion cascade lives on ExplosionFX. Guarded so that
# callers firing off a blast before _ready (e.g. tests) don't crash.
func _spawn_explosion(position: Vector3, size: float = 20.0) -> void:
	if explosion_fx == null or not is_instance_valid(explosion_fx):
		return
	explosion_fx.spawn_explosion(position, size)

# Shield-hit shimmer dispatcher. Kept next to _spawn_explosion for symmetry.
func _spawn_shield_hit(position: Vector3, radius: float = 40.0, color: Color = Color8(0x44, 0x88, 0xff)) -> void:
	if explosion_fx == null or not is_instance_valid(explosion_fx):
		return
	explosion_fx.spawn_shield_hit(position, radius, color)

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
	# Cinematic hit marker: 0.25s white cross flash when the player lands any
	# damage on an enemy (shields or hull). Matches HTML showHitMarker() at
	# line 5275, fired from every projectile / hitscan hit path.
	if amount > 0.0 and hud != null:
		hud.show_hit_marker()
		# Hit SFX paired with the visual marker. Gated on amount > 0 so a
		# zero-damage hit (e.g., fully absorbed by an immunity state) stays
		# silent.
		_play_audio("hit")

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

func _find_ships_along_line(origin: Vector3, direction: Vector3, length: float, perpendicular_radius: float, source_team: int) -> Array:
	# Equivalent to HTML last_ship_sailing.html:7411-7421. Returns any enemy
	# ship whose closest-point on the segment is within perpendicular_radius,
	# and whose projection onto the direction is inside [-50, length+50] so
	# ships touching either end of the firewall still count (HTML slack).
	var hits: Array = []
	var axis := direction.normalized()
	if axis.length_squared() < 0.001:
		return hits
	var candidates: Array = []
	if source_team == PlayerShip.TEAM_PLAYER:
		for enemy in enemies:
			if enemy.is_alive():
				candidates.append(enemy)
	else:
		if player.is_alive():
			candidates.append(player)
	for candidate in candidates:
		var offset: Vector3 = candidate.global_position - origin
		var along := offset.dot(axis)
		if along < -50.0 or along > length + 50.0:
			continue
		var perp := offset - axis * along
		if perp.length() <= perpendicular_radius + candidate.get_collision_radius():
			hits.append(candidate)
	return hits

func _update_stasis_spawner(delta: float) -> void:
	# Port of HTML last_ship_sailing.html:9464-9484 spawn cadence. Only ticks
	# during the "playing" phase so warmup does not pre-seed pickups.
	if match_state != "playing":
		return
	var alive := _count_stasis_fields()
	if alive >= STASIS_MAX:
		return
	stasis_spawn_timer = maxf(0.0, stasis_spawn_timer - delta)
	if stasis_spawn_timer > 0.0:
		return
	if stasis_first_batch:
		for _i in range(STASIS_MAX):
			_try_spawn_stasis_field()
		stasis_first_batch = false
	else:
		_try_spawn_stasis_field()
	stasis_spawn_timer = STASIS_INTERVAL

func _count_stasis_fields() -> int:
	var count := 0
	for effect in world_effects:
		if String(effect.get("type", "")) == "stasis":
			count += 1
	return count

func _pick_stasis_spawn_position() -> Vector3:
	# Matches HTML last_ship_sailing.html:9438-9454: keep trying random valid
	# spawn points until we find one at least 300u from every other stasis
	# field, giving up after 50 attempts so the spawner never stalls the
	# physics frame. Reuses arena_map.get_spawn_point() which already walks
	# the hourglass / circumpunct room pools.
	var min_distance := 300.0
	for attempt in range(50):
		var team_key := "A" if randi() % 2 == 0 else "B"
		var candidate := arena_map.get_spawn_point(team_key, 320.0, 120.0)
		var too_close := false
		for effect in world_effects:
			if String(effect.get("type", "")) != "stasis":
				continue
			var other_pos: Vector3 = effect.get("position", Vector3.ZERO)
			if other_pos.distance_to(candidate) < min_distance:
				too_close = true
				break
		if not too_close:
			return candidate
	return Vector3.INF

func _try_spawn_stasis_field() -> void:
	var position := _pick_stasis_spawn_position()
	if position == Vector3.INF:
		return
	_spawn_stasis_field(position)

func _spawn_stasis_field(position: Vector3) -> void:
	# Visual: translucent cyan sphere (the HTML uses a sphere + two rotating
	# torus rings; a single emissive sphere is a close-enough proxy until art
	# time). Pickup logic lives on the world_effects tick in _check_stasis_pickup.
	var core_mesh := SphereMesh.new()
	core_mesh.radius = 26.0
	core_mesh.height = 52.0
	var node := MeshInstance3D.new()
	node.mesh = core_mesh
	var stasis_color := GameData.color_from_hex(0x00ccff)
	var stasis_material := StandardMaterial3D.new()
	stasis_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	stasis_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	stasis_material.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	stasis_material.albedo_color = Color(stasis_color.r, stasis_color.g, stasis_color.b, 0.8)
	stasis_material.emission_enabled = true
	stasis_material.emission = stasis_color
	stasis_material.emission_energy_multiplier = 2.4
	node.material_override = stasis_material
	node.global_position = position
	effect_root.add_child(node)

	world_effects.append({
		"type": "stasis",
		"node": node,
		"position": position,
		"radius": STASIS_PICKUP_RADIUS,
		# Stasis fields persist until consumed; this big duration keeps the
		# generic timer-expiry path from culling them. _check_stasis_pickup
		# flips timer=0 on the frame a ship walks into them.
		"timer": 9999.0,
		"team": -1,
		"signature": {}
	})

func _check_stasis_pickup(effect: Dictionary, index: int) -> void:
	var field_position: Vector3 = effect["position"]
	var radius: float = float(effect["radius"])
	# Player pickup: the ship itself gates on "not already in stasis" and
	# "not dead" so we don't have to replicate the checks here.
	if player != null and is_instance_valid(player) and player.is_alive() and not player.get("in_stasis"):
		if player.global_position.distance_to(field_position) < radius:
			if player.has_method("enter_stasis"):
				player.enter_stasis(STASIS_DURATION)
			_remove_world_effect(index)
			return
	# Bot pickup: any bot under full shield grabs the pickup instantly and
	# refills to max. HTML last_ship_sailing.html:9500-9510 matches this
	# simplified behaviour (bots don't have the 3s immobilize, they just top
	# off their shield so the player isn't racing against a bot's 3s delay).
	for enemy in enemies:
		if not enemy.is_alive():
			continue
		if enemy.global_position.distance_to(field_position) >= radius:
			continue
		if enemy.get("shield") >= enemy.get("max_shield"):
			continue
		if enemy.has_method("restore_shield"):
			enemy.restore_shield(float(enemy.get("max_shield")))
		_remove_world_effect(index)
		return

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
