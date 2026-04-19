extends Control

const GameData = preload("res://scripts/game_data.gd")
const PlayerShip = preload("res://scripts/player_ship.gd")
const ArenaMap = preload("res://scripts/arena_map.gd")

var player_ref: PlayerShip
var arena_map: ArenaMap
var enemies: Array = []
var alive_targets := 0
var match_info: Dictionary = {}
var status: Dictionary = {}
var tracked_enemy: Node3D

func _ready() -> void:
	set_anchors_preset(PRESET_FULL_RECT)
	offset_left = 0.0
	offset_top = 0.0
	offset_right = 0.0
	offset_bottom = 0.0
	mouse_filter = MOUSE_FILTER_IGNORE
	focus_mode = FOCUS_NONE

func configure_context(new_arena_map: ArenaMap, enemy_list: Array) -> void:
	arena_map = new_arena_map
	enemies = enemy_list
	queue_redraw()

func set_state(player: PlayerShip, new_alive_targets: int, new_match_info: Dictionary) -> void:
	player_ref = player
	alive_targets = new_alive_targets
	match_info = new_match_info.duplicate(false)
	tracked_enemy = match_info.get("tracked_enemy", null) as Node3D
	status = player.get_status() if player != null else {}
	queue_redraw()

func _process(_delta: float) -> void:
	if player_ref != null:
		queue_redraw()

func _draw() -> void:
	if player_ref == null or status.is_empty():
		return

	var viewport_size := get_viewport_rect().size
	var hud_scale := clampf(minf(viewport_size.x / 1600.0, viewport_size.y / 900.0), 0.72, 1.0)
	var t := Time.get_ticks_msec() * 0.001
	var panel_color := GameData.color_from_hex(int(player_ref.signature.get("panel_color", 0x66ccff)))
	var accent_color := _with_alpha(panel_color.lightened(0.12), 1.0)

	_draw_damage_vignette(viewport_size, t)
	_draw_round_banner(viewport_size, hud_scale, t, accent_color)
	_draw_enemy_markers(viewport_size, hud_scale, t)
	_draw_center_hud(viewport_size, hud_scale, t, accent_color)
	_draw_minimap(viewport_size, hud_scale, t)
	_draw_corner_panels(viewport_size, hud_scale, accent_color)

func _draw_damage_vignette(viewport_size: Vector2, t: float) -> void:
	var health_ratio := float(status.get("health", 0.0)) / maxf(1.0, float(status.get("max_health", 1.0)))
	if health_ratio >= 0.45:
		return

	var pulse := 0.12 + (1.0 - health_ratio) * 0.20 + absf(sin(t * 4.4)) * 0.08
	var edge := minf(viewport_size.x, viewport_size.y) * 0.08
	var vignette_color := Color(1.0, 0.10, 0.05, clampf(pulse, 0.0, 0.33))
	draw_rect(Rect2(0.0, 0.0, viewport_size.x, edge), vignette_color)
	draw_rect(Rect2(0.0, viewport_size.y - edge, viewport_size.x, edge), vignette_color)
	draw_rect(Rect2(0.0, 0.0, edge, viewport_size.y), vignette_color)
	draw_rect(Rect2(viewport_size.x - edge, 0.0, edge, viewport_size.y), vignette_color)

func _draw_round_banner(viewport_size: Vector2, hud_scale: float, t: float, accent_color: Color) -> void:
	var timer_seconds := int(round(float(match_info.get("timer", 0.0))))
	var minutes: int = maxi(timer_seconds, 0) / 60
	var seconds: int = maxi(timer_seconds, 0) % 60
	var timer_text := "%d:%02d" % [minutes, seconds]
	var round_text := "ROUND %d" % int(match_info.get("current_round", 1))
	var score_text := "FLEET A %d  |  FLEET B %d" % [int(match_info.get("score_a", 0)), int(match_info.get("score_b", 0))]
	var state_text := String(match_info.get("state_label", "Warmup")).to_upper()
	var map_name := String(match_info.get("map_name", "The Nexus")).to_upper()

	var panel_width := 360.0 * hud_scale
	var panel_height := 58.0 * hud_scale
	var panel_rect := Rect2(
		Vector2(viewport_size.x * 0.5 - panel_width * 0.5, 24.0 * hud_scale),
		Vector2(panel_width, panel_height)
	)
	_draw_panel(panel_rect, Color(0.03, 0.05, 0.09, 0.54), _with_alpha(accent_color, 0.35))
	_draw_text(Vector2(panel_rect.position.x + 16.0 * hud_scale, panel_rect.position.y + 22.0 * hud_scale), round_text, int(round(16.0 * hud_scale)), _with_alpha(Color(0.90, 0.96, 1.0, 1.0), 0.88))
	_draw_text_centered(Vector2(panel_rect.get_center().x, panel_rect.position.y + 22.0 * hud_scale), timer_text, int(round(18.0 * hud_scale)), _with_alpha(Color(1.0, 1.0, 1.0, 1.0), 0.96))
	_draw_text_right(Vector2(panel_rect.end.x - 16.0 * hud_scale, panel_rect.position.y + 22.0 * hud_scale), state_text, int(round(16.0 * hud_scale)), _with_alpha(accent_color, 0.90))
	_draw_text_centered(Vector2(panel_rect.get_center().x, panel_rect.end.y - 10.0 * hud_scale), "%s  |  %s" % [score_text, map_name], int(round(12.0 * hud_scale)), Color(0.66, 0.80, 0.94, 0.82))

	var match_state := String(match_info.get("state", "warmup"))
	if match_state == "playing":
		return

	var pulse := 0.36 + absf(sin(t * 3.2)) * 0.24
	var headline_color := _with_alpha(accent_color.lightened(0.15), pulse)
	var subtitle_color := Color(0.86, 0.92, 0.98, pulse * 0.86)
	var headline_y := viewport_size.y * 0.24
	_draw_text_centered(Vector2(viewport_size.x * 0.5, headline_y), state_text, int(round(36.0 * hud_scale)), headline_color)
	_draw_text_centered(Vector2(viewport_size.x * 0.5, headline_y + 28.0 * hud_scale), "%s  |  %s" % [round_text, score_text], int(round(15.0 * hud_scale)), subtitle_color)

func _draw_center_hud(viewport_size: Vector2, hud_scale: float, t: float, accent_color: Color) -> void:
	var center := viewport_size * 0.5
	var white := Color(0.98, 0.99, 1.0, 1.0)
	var cyan := Color(0.42, 0.82, 1.0, 1.0)
	var amber := Color(1.0, 0.70, 0.22, 1.0)
	var green := Color(0.46, 1.0, 0.66, 1.0)
	var red := Color(1.0, 0.24, 0.18, 1.0)

	var health_pct := float(status.get("health", 0.0)) / maxf(1.0, float(status.get("max_health", 1.0)))
	var shield_pct := float(status.get("shield", 0.0)) / maxf(1.0, float(status.get("max_shield", 1.0)))
	var core_pct := clampf(float(status.get("core_meter", 0.0)) / 100.0, 0.0, 1.0)
	var speed_pct := clampf(float(status.get("speed", 0.0)) / maxf(1.0, float(player_ref.chassis.get("flight_speed", 350.0)) * 1.5), 0.0, 1.0)
	var smart_core_ammo := player_ref.is_state_active("smart_core") and player_ref.loadout_key == "LEGION"
	var ammo_pct := 1.0 if smart_core_ammo or player_ref.max_clip >= 999 else float(player_ref.clip_ammo) / maxf(1.0, float(player_ref.max_clip))
	var health_segments := int(player_ref.chassis.get("health_segments", 4))
	var dash_max := int(player_ref.chassis.get("max_dashes", 1))

	var h_color := green
	if health_pct < 0.6:
		h_color = Color(1.0, 0.72, 0.24, 1.0)
	if health_pct < 0.3:
		h_color = red

	var r1 := 126.0 * hud_scale
	var r2 := 160.0 * hud_scale
	var r3 := 204.0 * hud_scale
	var r4 := 248.0 * hud_scale
	var r5 := 292.0 * hud_scale
	var r6 := 334.0 * hud_scale

	_draw_cockpit_guns(viewport_size, hud_scale, t, accent_color)

	if player_ref.loadout_key == "LEGION" and player_ref.legion_mode == "close":
		draw_arc(center, 22.0 * hud_scale, 0.0, TAU, 48, _with_alpha(white, 0.62), 2.0, true)
		draw_circle(center, 2.5 * hud_scale, _with_alpha(white, 0.78))
	else:
		draw_circle(center, 3.2 * hud_scale, _with_alpha(white, 0.92))
		var cross_gap := 10.0 * hud_scale
		var cross_len := 28.0 * hud_scale
		_draw_line(center + Vector2(-cross_gap - cross_len, 0.0), center + Vector2(-cross_gap, 0.0), _with_alpha(white, 0.44), 1.5)
		_draw_line(center + Vector2(cross_gap, 0.0), center + Vector2(cross_gap + cross_len, 0.0), _with_alpha(white, 0.44), 1.5)
		_draw_line(center + Vector2(0.0, -cross_gap - cross_len), center + Vector2(0.0, -cross_gap), _with_alpha(white, 0.44), 1.5)
		_draw_line(center + Vector2(0.0, cross_gap), center + Vector2(0.0, cross_gap + cross_len), _with_alpha(white, 0.44), 1.5)

	if player_ref.loadout_key == "LEGION":
		_draw_text_centered(center + Vector2(0.0, 34.0 * hud_scale), String(player_ref.legion_mode).to_upper(), int(round(11.0 * hud_scale)), _with_alpha(amber if player_ref.legion_mode == "long" else white, 0.56))

	var health_arc_start := PI * 0.65
	var health_arc_end := PI * 2.35
	_draw_arc(center, r1, health_arc_start, health_arc_end, _with_alpha(white, 0.10), 8.0)
	var seg_gap := 0.04
	var span := health_arc_end - health_arc_start
	for index in range(health_segments):
		var seg_start := health_arc_start + (span / health_segments) * index + seg_gap * 0.5
		var seg_end := health_arc_start + (span / health_segments) * (index + 1) - seg_gap * 0.5
		var seg_start_pct := float(index) / float(health_segments)
		if health_pct > seg_start_pct:
			var fill_pct := minf(1.0, (health_pct - seg_start_pct) / (1.0 / float(health_segments)))
			var fill_end := lerpf(seg_start, seg_end, fill_pct)
			_draw_arc(center, r1, seg_start, fill_end, _with_alpha(h_color, 0.84), 8.0)
			_draw_arc(center, r1 - 5.0 * hud_scale, seg_start, fill_end, _with_alpha(white, 0.14), 1.4)
		if index > 0:
			var tick_angle := health_arc_start + (span / health_segments) * index
			_draw_radial_tick(center, r1, tick_angle, 14.0 * hud_scale, 14.0 * hud_scale, _with_alpha(white, 0.12), 1.3)
	_draw_text_centered(center + Vector2(0.0, r1 + 22.0 * hud_scale), str(int(round(float(status.get("health", 0.0))))), int(round(13.0 * hud_scale)), _with_alpha(white, 0.68))

	var shield_arc_start := -PI * 0.85
	var shield_arc_end := -PI * 0.15
	_draw_arc(center, r2, shield_arc_start, shield_arc_end, _with_alpha(cyan, 0.11), 5.0)
	if shield_pct > 0.0:
		_draw_arc(center, r2, shield_arc_start, lerpf(shield_arc_start, shield_arc_end, shield_pct), _with_alpha(cyan, 0.64), 5.0)
	for tick in range(11):
		var tick_angle2 := lerpf(shield_arc_start, shield_arc_end, float(tick) / 10.0)
		var tick_len := 12.0 * hud_scale if tick % 5 == 0 else 7.0 * hud_scale
		_draw_radial_tick(center, r2, tick_angle2, tick_len, tick_len, _with_alpha(cyan, 0.14 if tick % 5 == 0 else 0.08), 1.2)

	var speed_arc_start := PI * 0.55
	var speed_arc_end := PI * 0.95
	_draw_arc(center, r3, speed_arc_start, speed_arc_end, _with_alpha(white, 0.08), 3.0)
	if speed_pct > 0.0:
		_draw_arc(center, r3, speed_arc_start, lerpf(speed_arc_start, speed_arc_end, speed_pct), _with_alpha(white, 0.46), 3.0)
	var speed_angle := (speed_arc_start + speed_arc_end) * 0.5
	_draw_text_centered(center + Vector2(cos(speed_angle), sin(speed_angle)) * (r3 + 22.0 * hud_scale), str(int(round(float(status.get("speed", 0.0))))), int(round(11.0 * hud_scale)), _with_alpha(white, 0.52))

	var ammo_arc_start := PI * 0.05
	var ammo_arc_end := PI * 0.45
	_draw_arc(center, r3, ammo_arc_start, ammo_arc_end, _with_alpha(white, 0.08), 3.0)
	if ammo_pct > 0.0:
		var ammo_color := amber if player_ref.reload_timer > 0.0 else white
		_draw_arc(center, r3, ammo_arc_start, lerpf(ammo_arc_start, ammo_arc_end, ammo_pct), _with_alpha(ammo_color, 0.54), 3.0)
	var ammo_angle := (ammo_arc_start + ammo_arc_end) * 0.5
	var ammo_text := "INF" if smart_core_ammo or player_ref.max_clip >= 999 else str(player_ref.clip_ammo)
	_draw_text_centered(center + Vector2(cos(ammo_angle), sin(ammo_angle)) * (r3 + 22.0 * hud_scale), ammo_text, int(round(11.0 * hud_scale)), _with_alpha(white, 0.52))

	for index_dash in range(64):
		var dash_angle_start := (TAU / 64.0) * index_dash + t * 0.08
		var dash_angle_end := dash_angle_start + (TAU / 64.0) * 0.28
		if index_dash % 2 == 0:
			_draw_arc(center, r4, dash_angle_start, dash_angle_end, _with_alpha(white, 0.06), 1.4)
	if core_pct > 0.0:
		var core_start := -PI * 0.5
		var core_end := core_start + TAU * core_pct
		var core_color := amber if core_pct >= 1.0 else accent_color
		_draw_arc(center, r4, core_start, core_end, _with_alpha(core_color, 0.34 if core_pct < 1.0 else 0.70), 4.0)
		if core_pct >= 1.0:
			_draw_arc(center, r4 + 3.0 * hud_scale, 0.0, TAU, _with_alpha(amber, 0.12 + absf(sin(t * 3.0)) * 0.18), 7.0)

	var ability_angles := [
		-PI * 0.5 - 0.8,
		-PI * 0.5,
		-PI * 0.5 + 0.8
	]
	var ability_keys := ["1", "2", "3"]
	var abilities: Array = player_ref.loadout.get("abilities", [])
	for ability_index in range(min(3, abilities.size())):
		var ability: Dictionary = abilities[ability_index]
		var ability_angle := float(ability_angles[ability_index])
		var bracket_width := 0.22
		var b_start := ability_angle - bracket_width * 0.5
		var b_end := ability_angle + bracket_width * 0.5
		var cooldown := float(player_ref.ability_cooldowns[ability_index])
		var ready := cooldown <= 0.05
		var active := _ability_is_active(String(ability.get("id", "")))
		_draw_arc(center, r5, b_start, b_end, _with_alpha(white, 0.12), 3.0)
		_draw_radial_tick(center, r5, b_start, 12.0 * hud_scale, 12.0 * hud_scale, _with_alpha(white, 0.16), 1.3)
		_draw_radial_tick(center, r5, b_end, 12.0 * hud_scale, 12.0 * hud_scale, _with_alpha(white, 0.16), 1.3)
		if ready:
			var ready_color := amber if active else cyan
			_draw_arc(center, r5, b_start, b_end, _with_alpha(ready_color, 0.84 if active else 0.42), 3.0)
		else:
			var max_cooldown := maxf(0.25, float(ability.get("cooldown", 8.0)))
			var fill_pct2 := clampf(1.0 - cooldown / max_cooldown, 0.0, 1.0)
			_draw_arc(center, r5, b_start, lerpf(b_start, b_end, fill_pct2), _with_alpha(white, 0.36), 3.0)
		_draw_text_centered(center + Vector2(cos(ability_angle), sin(ability_angle)) * (r5 + 23.0 * hud_scale), ability_keys[ability_index], int(round(11.0 * hud_scale)), _with_alpha(white if ready else Color(0.74, 0.78, 0.84, 1.0), 0.68))

	for tick_ring in range(80):
		var tick_angle3 := (TAU / 80.0) * tick_ring + t * 0.04
		var major := tick_ring % 10 == 0
		var mid := tick_ring % 5 == 0
		var tick_len2 := 16.0 * hud_scale if major else (9.0 * hud_scale if mid else 5.0 * hud_scale)
		var tick_color := _with_alpha(white, 0.18 if major else (0.10 if mid else 0.05))
		_draw_radial_tick(center, r6, tick_angle3, tick_len2, 4.0 * hud_scale, tick_color, 1.4 if major else 1.0)

	var corner_radius := 366.0 * hud_scale
	for base_angle in [PI * 0.25, PI * 0.75, PI * 1.25, PI * 1.75]:
		var a := float(base_angle) - t * 0.05
		var bracket_center := center + Vector2(cos(a), sin(a)) * corner_radius
		var radial := Vector2(cos(a), sin(a))
		var tangent := Vector2(-radial.y, radial.x)
		var bracket_size := 28.0 * hud_scale
		_draw_line(bracket_center - radial * bracket_size * 0.55, bracket_center + radial * bracket_size * 0.4, _with_alpha(white, 0.13), 1.8)
		_draw_line(bracket_center + radial * bracket_size * 0.4, bracket_center + radial * bracket_size * 0.4 + tangent * bracket_size * 0.35, _with_alpha(white, 0.13), 1.8)

	var dash_y := center.y + r1 + 35.0 * hud_scale
	var pip_radius := 5.0 * hud_scale
	var pip_gap := 14.0 * hud_scale
	var total_width := dash_max * ((pip_radius * 2.0) + pip_gap) - pip_gap
	var start_x := center.x - total_width * 0.5
	for dash_index in range(dash_max):
		var pip_center := Vector2(start_x + dash_index * ((pip_radius * 2.0) + pip_gap) + pip_radius, dash_y)
		if dash_index < player_ref.dash_charges:
			draw_circle(pip_center, pip_radius, _with_alpha(cyan, 0.86))
		else:
			draw_arc(pip_center, pip_radius, 0.0, TAU, 24, _with_alpha(white, 0.18), 1.2, true)

func _draw_cockpit_guns(viewport_size: Vector2, hud_scale: float, t: float, accent_color: Color) -> void:
	var gun_len := viewport_size.y * 0.35
	var gun_base_width := viewport_size.x * 0.16
	var gun_tip_width := viewport_size.x * 0.034
	var tip_inset := viewport_size.x * 0.22
	var flash_timer := player_ref.muzzle_flash_timer
	var gun_color := Color(0.16, 0.18, 0.24, 0.92)
	var barrel_color := Color(0.08, 0.10, 0.14, 0.96)

	for side in range(2):
		var recoil := player_ref.gun_recoil_l if side == 0 else player_ref.gun_recoil_r
		var flash_active := flash_timer > 0.0 and player_ref.muzzle_flash_side == side
		var sway := sin(t * 1.2 + float(side) * PI) * 2.0 * hud_scale
		var recoil_amt := recoil * 18.0 * hud_scale
		var base_y := viewport_size.y + 20.0 * hud_scale + recoil_amt + sway
		var tip_y := viewport_size.y - gun_len + recoil_amt + sway
		var slide := gun_base_width * 0.66

		var base_outer_x := 0.0
		var base_inner_x := 0.0
		var tip_outer_x := 0.0
		var tip_inner_x := 0.0
		if side == 0:
			base_outer_x = -12.0 * hud_scale - slide
			base_inner_x = gun_base_width - 12.0 * hud_scale - slide
			tip_outer_x = tip_inset - gun_tip_width - slide * 0.35
			tip_inner_x = tip_inset - slide * 0.35
		else:
			base_outer_x = viewport_size.x + 12.0 * hud_scale + slide
			base_inner_x = viewport_size.x - gun_base_width + 12.0 * hud_scale + slide
			tip_outer_x = viewport_size.x - tip_inset + gun_tip_width + slide * 0.35
			tip_inner_x = viewport_size.x - tip_inset + slide * 0.35

		var hull_points := PackedVector2Array([
			Vector2(base_outer_x, base_y),
			Vector2(base_inner_x, base_y),
			Vector2(tip_inner_x, tip_y),
			Vector2(tip_outer_x, tip_y)
		])
		draw_colored_polygon(hull_points, gun_color)
		_draw_line(hull_points[0], hull_points[3], _with_alpha(accent_color, 0.12), 2.0)
		_draw_line(hull_points[1], hull_points[2], _with_alpha(Color(1.0, 1.0, 1.0, 1.0), 0.08), 1.6)

		var barrel_points: PackedVector2Array
		if side == 0:
			barrel_points = PackedVector2Array([
				Vector2(lerpf(base_outer_x, base_inner_x, 0.34), base_y),
				Vector2(lerpf(base_outer_x, base_inner_x, 0.66), base_y),
				Vector2(lerpf(tip_outer_x, tip_inner_x, 0.74), tip_y),
				Vector2(lerpf(tip_outer_x, tip_inner_x, 0.24), tip_y)
			])
		else:
			barrel_points = PackedVector2Array([
				Vector2(lerpf(base_outer_x, base_inner_x, 0.66), base_y),
				Vector2(lerpf(base_outer_x, base_inner_x, 0.34), base_y),
				Vector2(lerpf(tip_outer_x, tip_inner_x, 0.26), tip_y),
				Vector2(lerpf(tip_outer_x, tip_inner_x, 0.76), tip_y)
			])
		draw_colored_polygon(barrel_points, barrel_color)

		if flash_active:
			var flash_pos := Vector2((tip_outer_x + tip_inner_x) * 0.5, tip_y)
			var flash_intensity := clampf(flash_timer / 0.08, 0.0, 1.0)
			draw_circle(flash_pos, 15.0 * hud_scale * flash_intensity, _with_alpha(Color(1.0, 0.86, 0.46, 1.0), 0.20 * flash_intensity))
			draw_circle(flash_pos, 9.0 * hud_scale * flash_intensity, _with_alpha(Color(1.0, 0.94, 0.72, 1.0), 0.54 * flash_intensity))

func _draw_minimap(viewport_size: Vector2, hud_scale: float, _t: float) -> void:
	if arena_map == null:
		return

	var map_size := 162.0 * hud_scale
	var panel_rect := Rect2(
		Vector2(viewport_size.x - map_size - 26.0 * hud_scale, 100.0 * hud_scale),
		Vector2(map_size, map_size)
	)
	_draw_panel(panel_rect, Color(0.02, 0.04, 0.08, 0.70), Color(0.30, 0.38, 0.52, 0.75))
	var inner := panel_rect.grow(-8.0 * hud_scale)
	draw_rect(inner, Color(0.02, 0.04, 0.07, 0.92))

	var map_center := (arena_map.bounds_min + arena_map.bounds_max) * 0.5
	var extent_x := maxf(absf(arena_map.bounds_min.x - map_center.x), absf(arena_map.bounds_max.x - map_center.x))
	var extent_z := maxf(absf(arena_map.bounds_min.z - map_center.z), absf(arena_map.bounds_max.z - map_center.z))
	var extent := maxf(420.0, maxf(extent_x, extent_z) * 1.12)
	var scale := minf(inner.size.x, inner.size.y) / (extent * 2.0)

	for segment_data in arena_map.tunnel_segments:
		var segment: Dictionary = segment_data
		var a := _world_to_minimap(Vector3(segment["a"]), inner, map_center, scale)
		var b := _world_to_minimap(Vector3(segment["b"]), inner, map_center, scale)
		_draw_line(a, b, Color(0.26, 0.30, 0.44, 0.54), 2.4)

	for room_data in arena_map.rooms:
		var room: Dictionary = room_data
		var team := str(room.get("team", ""))
		var fill_color := Color(0.16, 0.20, 0.30, 0.56)
		var border_color := Color(0.34, 0.40, 0.54, 0.78)
		if team == "A":
			fill_color = Color(0.48, 0.18, 0.18, 0.26)
			border_color = Color(0.90, 0.36, 0.30, 0.80)
		elif team == "B":
			fill_color = Color(0.16, 0.30, 0.20, 0.28)
			border_color = Color(0.34, 0.88, 0.56, 0.84)
		var room_center := _world_to_minimap(Vector3(room.get("position", Vector3.ZERO)), inner, map_center, scale)
		var room_radius := float(room.get("radius", 120.0)) * scale
		draw_circle(room_center, room_radius, fill_color)
		draw_arc(room_center, room_radius, 0.0, TAU, 40, border_color, 1.0, true)

	var player_pos := _world_to_minimap(player_ref.global_position, inner, map_center, scale)
	draw_rect(Rect2(player_pos - Vector2.ONE * 2.0, Vector2.ONE * 4.0), Color(0.98, 0.99, 1.0, 0.96))
	var forward := player_ref.get_forward()
	# Forward arrow must use the same axis convention as _world_to_minimap
	# (both world.x and world.z negated; HTML last_ship_sailing.html:8850-8855).
	_draw_line(player_pos, player_pos + Vector2(-forward.x, -forward.z).normalized() * (16.0 * hud_scale), Color(0.98, 0.99, 1.0, 0.65), 1.4)

	for enemy in enemies:
		if not is_instance_valid(enemy) or not enemy.has_method("is_alive") or not enemy.is_alive():
			continue
		var enemy_pos := _world_to_minimap(enemy.global_position, inner, map_center, scale)
		var enemy_color := Color(0.28, 0.84, 0.42, 0.92)
		draw_rect(Rect2(enemy_pos - Vector2.ONE * 1.5, Vector2.ONE * 3.0), enemy_color)
		if tracked_enemy != null and enemy == tracked_enemy:
			draw_arc(enemy_pos, 5.0 * hud_scale, 0.0, TAU, 24, Color(1.0, 0.76, 0.26, 0.86), 1.2, true)

	_draw_text_centered(Vector2(panel_rect.get_center().x, panel_rect.end.y + 16.0 * hud_scale), String(match_info.get("map_name", "The Nexus")).to_upper(), int(round(10.0 * hud_scale)), Color(0.72, 0.82, 0.94, 0.74))

func _draw_enemy_markers(viewport_size: Vector2, hud_scale: float, _t: float) -> void:
	if player_ref.camera == null:
		return

	for enemy in enemies:
		if not is_instance_valid(enemy) or not enemy.has_method("is_alive") or not enemy.is_alive():
			continue

		var radius := float(enemy.get_collision_radius())
		var world_pos: Vector3 = enemy.global_position + Vector3.UP * radius * 0.55
		if player_ref.camera.is_position_behind(world_pos):
			continue

		var screen_pos: Vector2 = player_ref.camera.unproject_position(world_pos)
		if screen_pos.x < -60.0 or screen_pos.x > viewport_size.x + 60.0 or screen_pos.y < -60.0 or screen_pos.y > viewport_size.y + 60.0:
			continue

		var health_ratio: float = enemy.get_health_ratio() if enemy.has_method("get_health_ratio") else 1.0
		var shield_ratio: float = enemy.get_shield_ratio() if enemy.has_method("get_shield_ratio") else 0.0
		var base_color := Color(0.28, 0.84, 0.42, 0.92)
		if health_ratio < 0.35:
			base_color = Color(1.0, 0.44, 0.28, 0.96)
		if tracked_enemy != null and enemy == tracked_enemy:
			base_color = Color(1.0, 0.76, 0.26, 0.98)

		var bracket_w := 16.0 * hud_scale
		var bracket_h := 10.0 * hud_scale
		_draw_bracket_box(screen_pos, bracket_w, bracket_h, base_color, 1.6)

		var health_rect := Rect2(screen_pos + Vector2(-20.0 * hud_scale, -24.0 * hud_scale), Vector2(40.0 * hud_scale, 3.0 * hud_scale))
		draw_rect(health_rect, Color(0.04, 0.06, 0.09, 0.75))
		draw_rect(Rect2(health_rect.position, Vector2(health_rect.size.x * health_ratio, health_rect.size.y)), _with_alpha(base_color, 0.88))
		if shield_ratio > 0.0:
			var shield_rect := Rect2(health_rect.position + Vector2(0.0, -5.0 * hud_scale), Vector2(health_rect.size.x * shield_ratio, 2.0 * hud_scale))
			draw_rect(Rect2(shield_rect.position, Vector2(health_rect.size.x, shield_rect.size.y)), Color(0.05, 0.08, 0.12, 0.58))
			draw_rect(shield_rect, Color(0.42, 0.84, 1.0, 0.72))

		_draw_text_centered(screen_pos + Vector2(0.0, -31.0 * hud_scale), String(enemy.loadout_key), int(round(10.0 * hud_scale)), _with_alpha(Color(0.92, 0.98, 1.0, 1.0), 0.82))

func _draw_corner_panels(viewport_size: Vector2, hud_scale: float, accent_color: Color) -> void:
	var top_left := Rect2(Vector2(20.0 * hud_scale, 24.0 * hud_scale), Vector2(292.0 * hud_scale, 78.0 * hud_scale))
	var bottom_left := Rect2(Vector2(20.0 * hud_scale, viewport_size.y - 136.0 * hud_scale), Vector2(360.0 * hud_scale, 110.0 * hud_scale))
	_draw_panel(top_left, Color(0.03, 0.05, 0.08, 0.42), _with_alpha(accent_color, 0.24))
	_draw_panel(bottom_left, Color(0.03, 0.05, 0.08, 0.40), _with_alpha(accent_color, 0.22))

	var ship_title := "%s  |  %s" % [String(status.get("loadout_name", player_ref.loadout_key)), String(status.get("class_name", "Prototype"))]
	var weapon_line := "%s  |  %s" % [String(status.get("weapon_name", "Weapon")), String(player_ref.chassis.get("name", "Chassis"))]
	var stat_line := "HP %d/%d  SH %d/%d  SPD %d  ENEMIES %d" % [
		int(round(float(status.get("health", 0.0)))),
		int(round(float(status.get("max_health", 0.0)))),
		int(round(float(status.get("shield", 0.0)))),
		int(round(float(status.get("max_shield", 0.0)))),
		int(round(float(status.get("speed", 0.0)))),
		alive_targets
	]
	_draw_text(top_left.position + Vector2(14.0 * hud_scale, 18.0 * hud_scale), ship_title, int(round(16.0 * hud_scale)), Color(0.92, 0.98, 1.0, 0.94))
	_draw_text(top_left.position + Vector2(14.0 * hud_scale, 40.0 * hud_scale), weapon_line, int(round(13.0 * hud_scale)), _with_alpha(accent_color, 0.82))
	_draw_text(top_left.position + Vector2(14.0 * hud_scale, 60.0 * hud_scale), stat_line, int(round(12.0 * hud_scale)), Color(0.74, 0.84, 0.96, 0.78))

	var ability_y := bottom_left.position.y + 20.0 * hud_scale
	var abilities: Array = player_ref.loadout.get("abilities", [])
	for ability_index in range(min(3, abilities.size())):
		var ability: Dictionary = abilities[ability_index]
		var cooldown := float(player_ref.ability_cooldowns[ability_index])
		var ready := cooldown <= 0.05
		var state_text := "READY" if ready else "%.1fs" % cooldown
		var label := "%d  %s  %s" % [ability_index + 1, String(ability.get("name", "Ability")).to_upper(), state_text]
		var ability_color := Color(0.92, 0.98, 1.0, 0.88) if ready else Color(0.74, 0.80, 0.88, 0.62)
		if _ability_is_active(String(ability.get("id", ""))):
			ability_color = Color(1.0, 0.76, 0.26, 0.92)
		_draw_text(bottom_left.position + Vector2(14.0 * hud_scale, ability_y), label, int(round(12.0 * hud_scale)), ability_color)
		ability_y += 22.0 * hud_scale

	var core_text := "F  %s  %s" % [
		String(player_ref.loadout.get("core", {}).get("name", "Core")).to_upper(),
		"READY" if float(status.get("core_meter", 0.0)) >= 100.0 else "%.0f%%" % float(status.get("core_meter", 0.0))
	]
	_draw_text(bottom_left.position + Vector2(14.0 * hud_scale, bottom_left.end.y - 16.0 * hud_scale), core_text, int(round(12.0 * hud_scale)), Color(1.0, 0.80, 0.34, 0.80))

func _ability_is_active(ability_id: String) -> bool:
	match ability_id:
		"vortex_shield", "thermal_shield", "afterburner", "sword_block", "phase_dash", "gun_shield":
			return player_ref.is_state_active(ability_id)
		"mode_switch":
			return player_ref.legion_mode == "long"
		_:
			return false

func _world_to_minimap(world_pos: Vector3, rect: Rect2, map_center: Vector3, scale: float) -> Vector2:
	# Mirror the HTML convention (last_ship_sailing.html:8824-8825): both world.x
	# and world.z are negated on the radar so east/west on the minimap matches
	# the player's actual right/left in-world. Without the X negation the radar
	# is flipped across the vertical axis relative to ship movement.
	return Vector2(
		rect.get_center().x - (world_pos.x - map_center.x) * scale,
		rect.get_center().y - (world_pos.z - map_center.z) * scale
	)

func _draw_panel(rect: Rect2, fill_color: Color, border_color: Color) -> void:
	draw_rect(rect, fill_color)
	draw_rect(rect, border_color, false, 1.0, true)

func _draw_arc(center: Vector2, radius: float, start_angle: float, end_angle: float, color: Color, width: float) -> void:
	draw_arc(center, radius, start_angle, end_angle, 44, color, width, true)

func _draw_line(a: Vector2, b: Vector2, color: Color, width: float) -> void:
	draw_line(a, b, color, width, true)

func _draw_radial_tick(center: Vector2, radius: float, angle: float, inner_length: float, outer_length: float, color: Color, width: float) -> void:
	var dir := Vector2(cos(angle), sin(angle))
	_draw_line(center + dir * (radius - inner_length), center + dir * (radius + outer_length), color, width)

func _draw_bracket_box(center: Vector2, bracket_w: float, bracket_h: float, color: Color, width: float) -> void:
	var inset := Vector2(bracket_w, bracket_h)
	var line_len := 8.0
	_draw_line(center + Vector2(-inset.x, -inset.y), center + Vector2(-inset.x + line_len, -inset.y), color, width)
	_draw_line(center + Vector2(-inset.x, -inset.y), center + Vector2(-inset.x, -inset.y + line_len), color, width)
	_draw_line(center + Vector2(inset.x, -inset.y), center + Vector2(inset.x - line_len, -inset.y), color, width)
	_draw_line(center + Vector2(inset.x, -inset.y), center + Vector2(inset.x, -inset.y + line_len), color, width)
	_draw_line(center + Vector2(-inset.x, inset.y), center + Vector2(-inset.x + line_len, inset.y), color, width)
	_draw_line(center + Vector2(-inset.x, inset.y), center + Vector2(-inset.x, inset.y - line_len), color, width)
	_draw_line(center + Vector2(inset.x, inset.y), center + Vector2(inset.x - line_len, inset.y), color, width)
	_draw_line(center + Vector2(inset.x, inset.y), center + Vector2(inset.x, inset.y - line_len), color, width)

func _draw_text(position: Vector2, text: String, font_size: int, color: Color) -> void:
	var font := _get_font()
	if font == null:
		return
	draw_string(font, position, text, HORIZONTAL_ALIGNMENT_LEFT, -1.0, font_size, color)

func _draw_text_centered(position: Vector2, text: String, font_size: int, color: Color) -> void:
	var font := _get_font()
	if font == null:
		return
	var text_size := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1.0, font_size)
	draw_string(font, position - Vector2(text_size.x * 0.5, 0.0), text, HORIZONTAL_ALIGNMENT_LEFT, -1.0, font_size, color)

func _draw_text_right(position: Vector2, text: String, font_size: int, color: Color) -> void:
	var font := _get_font()
	if font == null:
		return
	var text_size := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1.0, font_size)
	draw_string(font, position - Vector2(text_size.x, 0.0), text, HORIZONTAL_ALIGNMENT_LEFT, -1.0, font_size, color)

func _get_font() -> Font:
	var font := get_theme_default_font()
	if font != null:
		return font
	return ThemeDB.fallback_font

func _with_alpha(color: Color, alpha: float) -> Color:
	return Color(color.r, color.g, color.b, alpha)
