class_name DamageOverlay
extends Control

# Red radial vignette + chromatic aberration pulse on player damage.
# Ported from last_ship_sailing.html:
#   #ov-damage-vignette (CSS lines 309-321, animation "ovDamageFlash")
#   damagePulse uniform in the composite pass (HTML lines 1681, 1762 for
#   vignette push, and the chromatic aberration block around lines 1735-1760)
#
# Animation: 0.45s ease-out. Alpha 0 -> 1 over first 15%, then 1 -> 0 over
# remaining 85%. Intensity clamped to [0.15, 1.0]; heavier hits get a
# stronger red + wider CA split.
#
# The vignette is a radial GradientTexture2D on a TextureRect (GPU friendly,
# no per-frame draw calls). The chromatic aberration is a fullscreen ColorRect
# with a shader that samples hint_screen_texture with RGB-offset UVs; the CA
# strength uniform is pulsed from the same timer as the vignette.

const FLASH_DURATION := 0.45
const FADE_IN_FRACTION := 0.15
const MIN_INTENSITY := 0.15
const MAX_CA_STRENGTH := 0.006   # UV offset at peak pulse (HTML pushes ~0.005-0.008)

const CA_SHADER_CODE := """
shader_type canvas_item;

uniform float ca_strength : hint_range(0.0, 0.02) = 0.0;
uniform sampler2D SCREEN_TEX : hint_screen_texture, filter_linear;

void fragment() {
	vec2 uv = SCREEN_UV;
	vec2 center = vec2(0.5, 0.5);
	vec2 dir = uv - center;
	// Radial CA: channels diverge more toward the edges (matches HTML behaviour).
	float radial = length(dir);
	vec2 offset = dir * ca_strength * radial * 4.0;
	float r = texture(SCREEN_TEX, uv + offset).r;
	float g = texture(SCREEN_TEX, uv).g;
	float b = texture(SCREEN_TEX, uv - offset).b;
	COLOR = vec4(r, g, b, ca_strength > 0.0001 ? 1.0 : 0.0);
}
"""

var _vignette: TextureRect
var _ca_rect: ColorRect
var _ca_material: ShaderMaterial
var _timer: float = -1.0
var _intensity: float = 0.0

func _ready() -> void:
	mouse_filter = MOUSE_FILTER_IGNORE
	set_anchors_preset(PRESET_FULL_RECT)

	# --- Chromatic aberration rect (drawn first, below the vignette) ---
	_ca_rect = ColorRect.new()
	_ca_rect.set_anchors_preset(PRESET_FULL_RECT)
	_ca_rect.mouse_filter = MOUSE_FILTER_IGNORE
	_ca_rect.color = Color(1, 1, 1, 1)   # shader writes fragment alpha from uniform
	var shader := Shader.new()
	shader.code = CA_SHADER_CODE
	_ca_material = ShaderMaterial.new()
	_ca_material.shader = shader
	_ca_material.set_shader_parameter("ca_strength", 0.0)
	_ca_rect.material = _ca_material
	add_child(_ca_rect)

	# --- Red radial vignette (drawn above CA so vignette colour wins at edges) ---
	_vignette = TextureRect.new()
	_vignette.set_anchors_preset(PRESET_FULL_RECT)
	_vignette.mouse_filter = MOUSE_FILTER_IGNORE
	_vignette.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_vignette.stretch_mode = TextureRect.STRETCH_SCALE
	_vignette.modulate = Color(1, 1, 1, 0)
	_vignette.texture = _build_gradient_texture()
	add_child(_vignette)

func _build_gradient_texture() -> GradientTexture2D:
	var gradient := Gradient.new()
	gradient.set_color(0, Color(1.0, 0.0, 0.0, 0.0))   # transparent red at center (first stop)
	gradient.set_color(1, Color(1.0, 0.0, 0.0, 0.85))  # opaque red at edge
	gradient.set_offset(0, 0.30)   # matches HTML "transparent 30%"
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

# intensity: 0..1, typically amount / max_health. Values below MIN_INTENSITY
# are clamped up so every hit registers. Re-triggering restarts the animation.
func flash(intensity: float) -> void:
	_intensity = clampf(intensity, MIN_INTENSITY, 1.0)
	_timer = 0.0

func is_flashing() -> bool:
	return _timer >= 0.0

# Internal ---------------------------------------------------------------

func _process(delta: float) -> void:
	if _timer < 0.0:
		return
	_timer += delta
	if _timer >= FLASH_DURATION:
		_timer = -1.0
		_apply_pulse(0.0)
		return
	var progress := _timer / FLASH_DURATION
	var alpha: float
	if progress < FADE_IN_FRACTION:
		alpha = progress / FADE_IN_FRACTION
	else:
		alpha = maxf(0.0, 1.0 - (progress - FADE_IN_FRACTION) / (1.0 - FADE_IN_FRACTION))
	_apply_pulse(alpha * _intensity)

func _apply_pulse(pulse: float) -> void:
	_vignette.modulate.a = pulse
	if _ca_material != null:
		_ca_material.set_shader_parameter("ca_strength", pulse * MAX_CA_STRENGTH)
