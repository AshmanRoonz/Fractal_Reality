class_name DoomedOverlay
extends Control

# Persistent red ellipse vignette + flashing "HULL CRITICAL" banner while the
# player ship is doomed (hull ≤ 15%). Ported from:
#   last_ship_sailing.html #doomed-vignette (CSS 170-175): radial-gradient
#     ellipse at center, transparent inner 50%, rgba(255,0,0,0.3) at edge.
#   last_ship_sailing.html #doomed-warning (CSS 134-141): "! HULL CRITICAL !"
#     text pulsing alpha between 0.5 and 1.0 at 0.4s interval, color #ff2200,
#     letter-spacing 3px, positioned ~80px above screen center.
#   HTML visibility toggle at lines 8752-8754 (isDoomed = player.doomed &&
#     shipState !== 'dead').
#
# This overlay is a sibling of DamageOverlay inside SandboxHUD; damage flashes
# layer on top of the doomed vignette (so a hit while doomed still produces
# the chromatic aberration pulse visibly).

const FLASH_INTERVAL := 0.4   # full period for the banner alpha pulse
const WARNING_OFFSET := -80.0  # pixels above screen vertical center
const VIGNETTE_ALPHA := 0.3   # matches rgba(255,0,0,0.3) in HTML CSS
const WARNING_COLOR := Color(1.0, 0.133, 0.0, 1.0)   # #ff2200

var _vignette: TextureRect
var _warning_label: Label
var _pulse_time: float = 0.0
var _active: bool = false

func _ready() -> void:
	mouse_filter = MOUSE_FILTER_IGNORE
	set_anchors_preset(PRESET_FULL_RECT)
	visible = false

	# Radial red vignette. Same GradientTexture2D pattern used by
	# DamageOverlay, but tuned to the doomed-state palette: transparent up to
	# 50% radius (matches HTML "transparent 50%"), then ramping to ~0.3 alpha
	# red at the edges. Less intense than the damage flash so it can sit on
	# screen for 10 seconds without overwhelming.
	_vignette = TextureRect.new()
	_vignette.set_anchors_preset(PRESET_FULL_RECT)
	_vignette.mouse_filter = MOUSE_FILTER_IGNORE
	_vignette.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_vignette.stretch_mode = TextureRect.STRETCH_SCALE
	_vignette.texture = _build_gradient_texture()
	add_child(_vignette)

	# "! HULL CRITICAL !" banner. Centered horizontally, positioned 80px above
	# screen vertical center. Alpha pulses between 0.5 and 1.0 via _process.
	_warning_label = Label.new()
	_warning_label.text = "! HULL CRITICAL !"
	_warning_label.add_theme_font_size_override("font_size", 18)
	_warning_label.add_theme_color_override("font_color", WARNING_COLOR)
	_warning_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_warning_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_warning_label.mouse_filter = MOUSE_FILTER_IGNORE
	_warning_label.anchor_left = 0.0
	_warning_label.anchor_right = 1.0
	_warning_label.anchor_top = 0.5
	_warning_label.anchor_bottom = 0.5
	_warning_label.offset_top = WARNING_OFFSET
	_warning_label.offset_bottom = WARNING_OFFSET + 22.0
	add_child(_warning_label)

func _build_gradient_texture() -> GradientTexture2D:
	var gradient := Gradient.new()
	# HTML: "transparent 50%, rgba(255,0,0,0.3) 100%"
	gradient.set_color(0, Color(1.0, 0.0, 0.0, 0.0))
	gradient.set_color(1, Color(1.0, 0.0, 0.0, VIGNETTE_ALPHA))
	gradient.set_offset(0, 0.50)
	gradient.set_offset(1, 1.00)

	var tex := GradientTexture2D.new()
	tex.gradient = gradient
	tex.fill = GradientTexture2D.FILL_RADIAL
	tex.fill_from = Vector2(0.5, 0.5)
	tex.fill_to = Vector2(1.0, 0.5)
	tex.width = 256
	tex.height = 256
	return tex

# Public API -------------------------------------------------------------

# Mirrors HTML isDoomed check. Call every frame from SandboxHUD; cheap.
func set_active(active: bool) -> void:
	if active == _active:
		return
	_active = active
	visible = active
	if not active:
		# Reset pulse so re-activation starts from the dim phase, keeping the
		# animation in sync with the banner's "flash on entry" feel.
		_pulse_time = 0.0
		_warning_label.modulate.a = 0.5

func is_active() -> bool:
	return _active

# Internal ---------------------------------------------------------------

func _process(delta: float) -> void:
	if not _active:
		return
	# Triangle wave between 0.5 and 1.0 over FLASH_INTERVAL seconds (matches
	# "alternate" animation-direction in the HTML keyframes: dim → bright →
	# dim → bright …). Half the period for the ramp, so one full cycle is
	# 2 × FLASH_INTERVAL = 0.8 s.
	_pulse_time = fmod(_pulse_time + delta, FLASH_INTERVAL * 2.0)
	var t := _pulse_time / FLASH_INTERVAL
	var alpha := 0.5 + 0.5 * (1.0 - absf(t - 1.0))
	_warning_label.modulate.a = alpha
