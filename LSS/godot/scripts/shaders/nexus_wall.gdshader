// Nexus Wall shader (Godot port of the HTML Kali IFS cosmic fractal wall).
// - Dark base tinted by nearest room's zone color.
// - Full-surface dancing Kali IFS (Apollonian-style fold/scale/offset fractal)
//   with three phi-scaled rings, hue steered by the zone.
// - One-way upper-half transparency: interior (front-facing) faces fade above
//   heightFrac 0.5 so the starfield shows through; exterior faces stay opaque.
// - Fresnel rim in the zone color for readable edges.
shader_type spatial;
render_mode unshaded, blend_mix, depth_draw_always, cull_disabled;

uniform vec3 room_centers[8];
uniform vec3 room_colors[8] : source_color;
uniform float room_radii[8];
uniform int room_count : hint_range(0, 8) = 0;
uniform float time_scale : hint_range(0.0, 4.0) = 1.0;
uniform float fractal_gain : hint_range(0.0, 8.0) = 3.4;

varying vec3 v_world_pos;
varying vec3 v_world_normal;
varying float v_ao;

void vertex() {
	vec4 wp = MODEL_MATRIX * vec4(VERTEX, 1.0);
	v_world_pos = wp.xyz;
	v_world_normal = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
	float normal_up_dot = dot(v_world_normal, vec3(0.0, 1.0, 0.0));
	float ao_from_normal = 0.85 + normal_up_dot * 0.15;
	v_ao = clamp(ao_from_normal, 0.7, 1.0);
}

// HSV -> RGB (same formulation as the HTML dancing cosmos shader).
vec3 hsv(float h, float s, float v) {
	vec3 k = mod(vec3(5.0, 3.0, 1.0) + h * 6.0, 6.0);
	return vec3(
		v - v * s * clamp(min(k.x, 4.0 - k.x), 0.0, 1.0),
		v - v * s * clamp(min(k.y, 4.0 - k.y), 0.0, 1.0),
		v - v * s * clamp(min(k.z, 4.0 - k.z), 0.0, 1.0)
	);
}

// Rough RGB -> hue for steering the palette off the zone color.
float rgb_hue(vec3 c) {
	float mx = max(c.r, max(c.g, c.b));
	float mn = min(c.r, min(c.g, c.b));
	float d = mx - mn;
	if (d < 0.001) {
		return 0.0;
	}
	float h;
	if (mx == c.r) {
		h = mod((c.g - c.b) / d + 6.0, 6.0) / 6.0;
	} else if (mx == c.g) {
		h = ((c.b - c.r) / d + 2.0) / 6.0;
	} else {
		h = ((c.r - c.g) / d + 4.0) / 6.0;
	}
	return h;
}

// Kali IFS (Apollonian-style fold/scale/offset fractal).
float kali_ifs(vec3 p, vec3 off, float inv) {
	float s = 1.0;
	for (int k = 0; k < 8; k++) {
		if (p.x + p.y < 0.0) {
			p.xy = -p.yx;
		}
		if (p.x + p.z < 0.0) {
			p.xz = -p.zx;
		}
		if (p.y + p.z < 0.0) {
			p.yz = -p.zy;
		}
		float e = max(0.95, inv / dot(p, p));
		s *= e;
		p = p * e - off;
	}
	return s;
}

// Cosmic fractal field evaluated at a world position, steered by the zone color.
vec3 cosmic_field(vec3 wp, vec3 zone_c, float tt) {
	vec3 off = vec3(1.5, 1.618, 1.0);
	vec3 p = wp * 0.0028;
	float ca = cos(tt * 0.12);
	float sa = sin(tt * 0.12);
	p = vec3(ca * p.x - sa * p.z, p.y, sa * p.x + ca * p.z);
	float base_hue = rgb_hue(zone_c);
	vec3 accum = vec3(0.0);
	for (int ring = 0; ring < 3; ring++) {
		float rf = float(ring);
		float s_mul = pow(1.618, 1.4 - rf * 0.7);
		vec3 pp = p * s_mul;
		float s = kali_ifs(pp, off, 9.0 + rf * 0.4);
		float phase = atan(pp.x, pp.y);
		float q = 0.5 + 0.5 * sin(phase * 3.0 + tt * 0.3 + rf * 1.7);
		float band = q < 0.5 ? 0.65 : 1.0;
		float val = clamp(s / 380.0 * (0.35 + 0.80 * band), 0.0, 4.5);
		float hue = fract(base_hue + rf * 0.12 + phase * 0.05 + tt * 0.02);
		float sat = 0.55 + rf * 0.10;
		accum += hsv(hue, sat, val) * pow(0.75, rf);
	}
	return accum;
}

void fragment() {
	// Nearest-room lookup (up to 8 rooms).
	vec3 zone_color = vec3(0.06, 0.08, 0.12);
	vec3 near_c = vec3(0.0);
	float near_r = 500.0;
	float min_d = 99999.0;
	for (int i = 0; i < 8; i++) {
		if (i >= room_count) {
			break;
		}
		float d = length(v_world_pos - room_centers[i]);
		if (d < min_d) {
			min_d = d;
			zone_color = room_colors[i];
			near_c = room_centers[i];
			near_r = room_radii[i];
		}
	}

	// Normalize zone color so dark palette entries still tint vividly.
	float z_max = max(zone_color.r, max(zone_color.g, zone_color.b));
	vec3 zone_tint = zone_color / max(0.04, z_max);

	// Height along the nearest room's vertical extent (0 at floor, 1 at ceiling).
	float height_frac = clamp(
		(v_world_pos.y - (near_c.y - near_r)) / (2.0 * near_r),
		0.0, 1.0
	);

	// Dark base + slight zone tint.
	vec3 dark = vec3(0.010, 0.012, 0.022) + zone_tint * 0.08;
	vec3 c = dark;

	// Kali IFS cosmic fractal (full surface).
	float tt = TIME * time_scale;
	float frac_pulse = 0.92 + 0.12 * sin(tt * 0.35);
	float shimmer = 0.90 + 0.18 * sin(tt * 1.10 + v_world_pos.x * 0.003 + v_world_pos.z * 0.003);
	vec3 cosmic = cosmic_field(v_world_pos, zone_tint, tt);
	c += cosmic * frac_pulse * shimmer * fractal_gain;

	// Soft diffuse + fresnel rim for 3D readability.
	vec3 vd = normalize(CAMERA_POSITION_WORLD - v_world_pos);
	float diff = max(dot(v_world_normal, vd), 0.0) * 0.35 + 0.65;
	float fresnel_factor = pow(1.0 - abs(dot(v_world_normal, vd)), 3.0);
	c += zone_tint * 1.6 * fresnel_factor * 0.5;
	c *= diff * v_ao;

	// One-way upper fade: interior (front-facing on outward-normal meshes) fades
	// above height_frac ~0.5 so the starfield shows through the ceiling.
	// Godot's FRONT_FACING is true for faces whose normal points toward the camera;
	// for outward-normal SphereMesh/CylinderMesh this is the EXTERIOR view. The
	// interior (inside the sphere/tunnel) is the back face -> FRONT_FACING is false.
	// So we fade when NOT FRONT_FACING (i.e. when we are seeing the wall from inside).
	float upper_mask = smoothstep(0.50, 0.80, height_frac);
	float alpha = 1.0;
	if (!FRONT_FACING) {
		alpha = mix(1.0, 0.08, upper_mask);
	}

	ALBEDO = c;
	ALPHA = alpha;
}
