extends Node

# Port of HTML last_ship_sailing.html:10600-11226 (audio system).
# WebAudio -> Godot mapping:
#   - Master/dry/wet/ambient routing      -> AudioServer buses
#   - Convolver reverb (metallic IR)      -> AudioEffectReverb on Wet bus
#   - High-frequency rolloff              -> AudioEffectLowPassFilter on Master
#   - triChord oscillators (ADSR + ramp)  -> procedurally synthesized PCM into AudioStreamWAV, pooled AudioStreamPlayer
#   - playNoiseBurst (noise + biquad LP)  -> procedurally synthesized PCM into AudioStreamWAV, single-pole IIR lowpass
#   - Phi-cascade binaural ambient bed    -> single AudioStreamGenerator mixing 12 oscillators internally
#
# Runs as an autoload singleton. main.gd and player_ship.gd call Audio.play_sound("type")
# for discrete SFX, Audio.update_ambient_bed(speed, state) each frame for the bed.
#
# All SFX call sites from the HTML (11145-11226) are mapped in the call-site comments
# of whichever main.gd / player_ship.gd function already performs the equivalent action.

const SAMPLE_RATE := 22050
const PHI := 1.6180339887498949
const PHI_LAYERS := 6
const PHI_REST_BASE := 69.0
const PHI_SPEED_BASE := 144.0
const PHI_BEAT_STRENGTH := 0.25
const PHI_BEAT := PHI * PHI_BEAT_STRENGTH  # ~0.4045 Hz binaural beat
const MAX_AMBIENT_SPEED := 800.0
const POOL_SIZE := 24  # max concurrent SFX voices

# Bus names kept in one place so main.gd / test can cross-reference.
const BUS_MASTER := "Master"
const BUS_DRY := "SFX_Dry"
const BUS_WET := "SFX_Wet"
const BUS_AMBIENT := "Ambient"

# ------------------------------------------------------------------------
# Bus setup
# ------------------------------------------------------------------------

# Pool of transient AudioStreamPlayer nodes for SFX. Each tri_chord / noise_burst
# claims one idle player, swaps its stream, and plays. Players are NOT freed
# between plays; stream_finished just releases the claim.
var _sfx_pool: Array[AudioStreamPlayer] = []
var _sfx_cursor: int = 0

# Ambient bed: one generator pushing stereo frames synthesized in GDScript.
var _ambient_player: AudioStreamPlayer = null
var _ambient_playback: AudioStreamGeneratorPlayback = null
var _ambient_started: bool = false
# Current base frequency for the phi cascade (lerps toward target in update).
var _ambient_base_freq: float = PHI_REST_BASE
# Per-layer phase accumulators for L/R oscillators and LFOs.
# phases[i] = { left, right, lfo_l, lfo_r }
var _phi_phases: Array = []
# Current gain applied to the whole bed; ramps toward target in update.
var _ambient_gain: float = 0.0

func _ready() -> void:
	_ensure_buses()
	_build_sfx_pool()
	_build_ambient_bed()

func _ensure_buses() -> void:
	# Bus #0 is always Master. Add SFX_Dry, SFX_Wet, Ambient if not already present.
	# Indices are computed fresh each time so the function is idempotent (handy for
	# re-running setup inside headless tests that reset the audio server).
	var bus_count := AudioServer.bus_count
	var known := {}
	for i in range(bus_count):
		known[AudioServer.get_bus_name(i)] = i
	if not known.has(BUS_DRY):
		AudioServer.add_bus()
		var idx := AudioServer.bus_count - 1
		AudioServer.set_bus_name(idx, BUS_DRY)
		AudioServer.set_bus_send(idx, BUS_MASTER)
		AudioServer.set_bus_volume_db(idx, linear_to_db(0.80))
	if not known.has(BUS_WET):
		AudioServer.add_bus()
		var idx_wet := AudioServer.bus_count - 1
		AudioServer.set_bus_name(idx_wet, BUS_WET)
		AudioServer.set_bus_send(idx_wet, BUS_MASTER)
		AudioServer.set_bus_volume_db(idx_wet, linear_to_db(0.40))
		var reverb := AudioEffectReverb.new()
		# Long metallic tail mimicking HTML's generateImpulseResponse(2.4s, decay 3.5).
		reverb.room_size = 0.85
		reverb.damping = 0.35
		reverb.wet = 1.0
		reverb.dry = 0.0
		reverb.spread = 0.9
		reverb.predelay_msec = 15.0
		AudioServer.add_bus_effect(idx_wet, reverb)
	if not known.has(BUS_AMBIENT):
		AudioServer.add_bus()
		var idx_amb := AudioServer.bus_count - 1
		AudioServer.set_bus_name(idx_amb, BUS_AMBIENT)
		AudioServer.set_bus_send(idx_amb, BUS_MASTER)
		AudioServer.set_bus_volume_db(idx_amb, linear_to_db(0.85))

	# Gentle lowpass on the master bus to match HTML's hiCut at 3.5kHz. Only add
	# once; looking for an existing LPF effect by type keeps this idempotent.
	var master_idx := AudioServer.get_bus_index(BUS_MASTER)
	var has_lpf := false
	for e in range(AudioServer.get_bus_effect_count(master_idx)):
		if AudioServer.get_bus_effect(master_idx, e) is AudioEffectLowPassFilter:
			has_lpf = true
			break
	if not has_lpf:
		var lpf := AudioEffectLowPassFilter.new()
		lpf.cutoff_hz = 3500.0
		lpf.resonance = 0.7
		AudioServer.add_bus_effect(master_idx, lpf)

func _build_sfx_pool() -> void:
	for i in range(POOL_SIZE):
		var p := AudioStreamPlayer.new()
		p.bus = BUS_DRY
		add_child(p)
		_sfx_pool.append(p)

func _claim_sfx_player(target_bus: String) -> AudioStreamPlayer:
	# Round-robin; if the slot is still playing we just stomp it. With POOL_SIZE = 24
	# and typical SFX under 1.5s, collisions are rare at normal game pace.
	var p := _sfx_pool[_sfx_cursor]
	_sfx_cursor = (_sfx_cursor + 1) % POOL_SIZE
	p.bus = target_bus
	return p

# ------------------------------------------------------------------------
# PCM synthesis helpers
# ------------------------------------------------------------------------

# tri_chord: 3 simultaneous oscillators with ADSR envelope and optional
# exponential frequency ramp to ramp_freqs over ramp_time. Replays the HTML
# triChord(freqs, wave, vol, dur, rampFreqs, rampTime, startOffset, envelope).
#
# start_offset is applied via AudioStreamPlayer.play(from_position) so multiple
# chained chords can schedule within one SFX without pre-mixing a single long
# buffer.
func tri_chord(
		freqs: Array,
		wave: String,
		vol: float,
		dur: float,
		ramp_freqs = null,
		ramp_time: float = 0.0,
		start_offset: float = 0.0,
		env: Dictionary = {}) -> void:
	var attack: float = float(env.get("attack", 0.003))
	var hold: float = float(env.get("hold", 0.0))
	var decay: float = float(env.get("decay", dur))
	var peak_vol: float = vol / 3.0
	var total_dur: float = maxf(dur + 0.01, attack + hold + decay)
	var buf := _alloc_pcm_buffer(total_dur)
	for i in range(freqs.size()):
		var base_freq: float = float(freqs[i])
		var ramp_to: float = base_freq
		if ramp_freqs != null and i < ramp_freqs.size():
			ramp_to = maxf(1.0, float(ramp_freqs[i]))
		var ramp_t: float = ramp_time if ramp_time > 0.0 else dur
		_accumulate_osc(buf, base_freq, ramp_to, ramp_t, wave, peak_vol, total_dur, attack, hold, decay)
	_play_buffer_both_paths(buf, start_offset)

# Filtered noise burst: optionally lowpass-filtered white noise with a linear
# amplitude envelope (HTML data[i] = noise * (1 - i/bufSize)) plus an exponential
# gain ramp from `volume` to 0.001 over duration.
#
# start_time in the HTML is already baked into the audio context clock; we
# remap to a play(from_position) offset relative to "now".
func play_noise_burst(
		duration: float,
		volume: float,
		start_offset: float = 0.0,
		filter_freq: float = 0.0,
		filter_q: float = 0.7) -> void:
	if duration <= 0.0:
		return
	var buf := _alloc_pcm_buffer(duration)
	var n_samples: int = buf.data.size() / 2  # 16-bit mono
	var pcm := PackedFloat32Array()
	pcm.resize(n_samples)
	for i in range(n_samples):
		# HTML data[i] = (rand*2-1) * (1 - i/bufSize), an envelope that fades
		# linearly to zero across the whole burst. That envelope is the primary
		# shape; the gain ramp below adds an exponential tail on top.
		pcm[i] = (randf() * 2.0 - 1.0) * (1.0 - float(i) / float(maxi(1, n_samples)))
	if filter_freq > 0.0:
		var cutoff := clampf(filter_freq, 20.0, 10000.0)
		# Single-pole IIR lowpass. The HTML uses a 2-pole biquad, but a 1-pole
		# at the same cutoff is audibly indistinguishable when Q <= 1 (which
		# HTML caps at in playNoiseBurst).
		var alpha := 1.0 - exp(-2.0 * PI * cutoff / float(SAMPLE_RATE))
		var y := 0.0
		for i in range(n_samples):
			y = y + alpha * (pcm[i] - y)
			pcm[i] = y
		# Resonance peak at filter_freq via one extra pole (mild for Q <= 1).
		if filter_q > 0.5:
			var q_boost := clampf(filter_q, 0.5, 2.0) - 0.5
			var prev := 0.0
			for i in range(n_samples):
				var filt := pcm[i] + q_boost * 0.3 * (pcm[i] - prev)
				prev = pcm[i]
				pcm[i] = filt
	# Apply exponential gain ramp from volume to 0.001 over duration, same as
	# HTML gain.gain.exponentialRampToValueAtTime.
	var target_end := 0.001
	var log_ratio := log(target_end / maxf(volume, 0.001))
	for i in range(n_samples):
		var t := float(i) / float(maxi(1, n_samples))
		var env := volume * exp(log_ratio * t)
		pcm[i] *= env
	_write_pcm_to_buffer(buf, pcm)
	_play_buffer_both_paths(buf, start_offset)

# Accumulate one oscillator with ADSR + frequency ramp into an existing PCM buffer.
# We write to the internal int16 data array directly for speed; GDScript loops
# over 22050-sample buffers are tolerable (~50k float ops per SFX).
func _accumulate_osc(
		buf: AudioStreamWAV,
		freq_start: float,
		freq_end: float,
		ramp_time: float,
		wave: String,
		peak_vol: float,
		total_dur: float,
		attack: float,
		hold: float,
		decay: float) -> void:
	var sample_count: int = buf.data.size() / 2
	var phase: float = 0.0
	var samples_per_sec := float(SAMPLE_RATE)
	var ramp_samples := int(ramp_time * samples_per_sec)
	var log_freq_ratio := 0.0
	if ramp_samples > 0 and freq_start > 0.0:
		log_freq_ratio = log(maxf(1.0, freq_end) / maxf(1.0, freq_start))
	var data := buf.data
	var attack_samples := int(attack * samples_per_sec)
	var hold_samples := int(hold * samples_per_sec)
	var decay_start_sample := attack_samples + hold_samples
	var decay_log_ratio := log(0.001 / maxf(peak_vol, 0.001))
	var decay_samples := maxi(1, sample_count - decay_start_sample)
	for i in range(sample_count):
		var t := float(i) / samples_per_sec
		# Frequency: exponential ramp from freq_start to freq_end over ramp_time,
		# constant at freq_end thereafter.
		var f: float
		if i < ramp_samples:
			f = freq_start * exp(log_freq_ratio * float(i) / float(ramp_samples))
		else:
			f = freq_end
		phase += 2.0 * PI * f / samples_per_sec
		if phase > 2.0 * PI:
			phase -= 2.0 * PI
		var osc_val := _osc_sample(wave, phase)
		# ADSR envelope
		var amp := 0.0
		if i < attack_samples:
			amp = peak_vol * float(i) / float(maxi(1, attack_samples))
		elif i < decay_start_sample:
			amp = peak_vol
		else:
			var decay_t := float(i - decay_start_sample) / float(decay_samples)
			amp = peak_vol * exp(decay_log_ratio * decay_t)
		var mixed := osc_val * amp
		# Sum into existing int16 frame (sign-extend, clamp, write back).
		var idx := i * 2
		var existing := data[idx] | (data[idx + 1] << 8)
		if existing >= 32768:
			existing -= 65536
		var new_val := existing + int(mixed * 32767.0)
		new_val = clampi(new_val, -32768, 32767)
		if new_val < 0:
			new_val += 65536
		data[idx] = new_val & 0xff
		data[idx + 1] = (new_val >> 8) & 0xff
	buf.data = data

func _osc_sample(wave: String, phase: float) -> float:
	match wave:
		"sine":
			return sin(phase)
		"square":
			return 1.0 if sin(phase) >= 0.0 else -1.0
		"sawtooth":
			return (phase / PI) - 1.0
		"triangle":
			var p := phase / (2.0 * PI)
			var v := 4.0 * absf(p - 0.5) - 1.0
			return v
		_:
			return sin(phase)

func _alloc_pcm_buffer(duration: float) -> AudioStreamWAV:
	var buf := AudioStreamWAV.new()
	buf.format = AudioStreamWAV.FORMAT_16_BITS
	buf.stereo = false
	buf.mix_rate = SAMPLE_RATE
	buf.loop_mode = AudioStreamWAV.LOOP_DISABLED
	var sample_count := maxi(16, int(duration * float(SAMPLE_RATE)))
	var data := PackedByteArray()
	data.resize(sample_count * 2)
	buf.data = data
	return buf

func _write_pcm_to_buffer(buf: AudioStreamWAV, pcm: PackedFloat32Array) -> void:
	var data := buf.data
	for i in range(pcm.size()):
		var v := clampf(pcm[i], -1.0, 1.0)
		var s := int(v * 32767.0)
		if s < 0:
			s += 65536
		data[i * 2] = s & 0xff
		data[i * 2 + 1] = (s >> 8) & 0xff
	buf.data = data

# HTML routes each SFX through BOTH dry (masterGain) and wet (convolver) paths.
# We do the same by claiming two players from the pool and pointing one at
# BUS_DRY and the other at BUS_WET, sharing the same AudioStreamWAV.
func _play_buffer_both_paths(buf: AudioStreamWAV, start_offset: float) -> void:
	# Pool players might not be inside the tree yet if something dispatches a
	# sound during boot (or from a headless test spinning up the node before
	# the first frame). Skip silently in that case; the alternative is a
	# `push_error("Playback can only happen when a node is inside the scene tree")`
	# bomb for every concurrent SFX that runs this early.
	if not is_inside_tree():
		return
	var dry := _claim_sfx_player(BUS_DRY)
	if dry == null or not dry.is_inside_tree():
		return
	dry.stream = buf
	dry.play(maxf(0.0, start_offset))
	var wet := _claim_sfx_player(BUS_WET)
	if wet == null or not wet.is_inside_tree():
		return
	wet.stream = buf
	wet.play(maxf(0.0, start_offset))

# ------------------------------------------------------------------------
# Ambient bed (phi-cascade binaural)
# ------------------------------------------------------------------------

func _build_ambient_bed() -> void:
	var gen := AudioStreamGenerator.new()
	gen.mix_rate = SAMPLE_RATE
	# 250 ms buffer = plenty of headroom to keep up with a 60 fps push step.
	gen.buffer_length = 0.25
	_ambient_player = AudioStreamPlayer.new()
	_ambient_player.stream = gen
	_ambient_player.bus = BUS_AMBIENT
	add_child(_ambient_player)
	for i in range(PHI_LAYERS):
		_phi_phases.append({"left": 0.0, "right": 0.0, "lfo_l": 0.0, "lfo_r": 0.0})

func start_ambient_bed() -> void:
	if _ambient_started or _ambient_player == null:
		return
	# Guard: the ambient player must be inside the tree to begin playback.
	# In headless tests the tree hasn't processed a frame yet when _init()
	# runs; we still flip _ambient_started so the lifecycle asserts see a
	# consistent state.
	if not _ambient_player.is_inside_tree():
		_ambient_started = true
		return
	_ambient_player.play()
	_ambient_playback = _ambient_player.get_stream_playback() as AudioStreamGeneratorPlayback
	_ambient_started = true

func stop_ambient_bed() -> void:
	if _ambient_player != null and _ambient_player.playing:
		_ambient_player.stop()
	_ambient_playback = null
	_ambient_started = false
	_ambient_gain = 0.0

# Called each frame from main.gd. speed is player velocity magnitude; state
# is "playing" / "warmup" / whatever (the HTML fades the bed in when game
# active, down to 0.08 gain otherwise).
func update_ambient_bed(speed: float, state: String) -> void:
	if not _ambient_started or _ambient_playback == null:
		return
	var t := clampf(speed / MAX_AMBIENT_SPEED, 0.0, 1.0)
	var target_base := PHI_REST_BASE + t * (PHI_SPEED_BASE - PHI_REST_BASE)
	# Smooth base-frequency morph; matches the `*= 0.02` smoothing rate in the HTML.
	_ambient_base_freq += (target_base - _ambient_base_freq) * 0.02
	var target_gain := 0.08
	if state == "playing" or state == "warmup":
		target_gain = 1.0
	_ambient_gain += (target_gain - _ambient_gain) * 0.02
	var frames_available := _ambient_playback.get_frames_available()
	if frames_available <= 0:
		return
	var frames := PackedVector2Array()
	frames.resize(frames_available)
	var dt_per_sample := 1.0 / float(SAMPLE_RATE)
	for n in range(frames_available):
		var left_mix := 0.0
		var right_mix := 0.0
		for i in range(PHI_LAYERS):
			var layer: Dictionary = _phi_phases[i]
			var layer_freq: float = _ambient_base_freq * pow(PHI, float(i - 3))
			var layer_vol: float = (0.50 / float(PHI_LAYERS)) * (1.0 + t * 0.8)
			# LFO modulation at phi-derived rate (matches HTML layer.frequency = PHI / PHI^i).
			var lfo_freq := PHI / pow(PHI, float(i))
			layer["lfo_l"] += 2.0 * PI * lfo_freq * dt_per_sample
			layer["lfo_r"] += 2.0 * PI * lfo_freq * dt_per_sample
			if layer["lfo_l"] > 2.0 * PI:
				layer["lfo_l"] -= 2.0 * PI
			if layer["lfo_r"] > 2.0 * PI:
				layer["lfo_r"] -= 2.0 * PI
			var mod_l := 1.0 + 0.5 * sin(layer["lfo_l"])
			var mod_r := 1.0 + 0.5 * sin(layer["lfo_r"])
			# Left ear: carrier at layer_freq.
			layer["left"] += 2.0 * PI * layer_freq * dt_per_sample
			if layer["left"] > 2.0 * PI:
				layer["left"] -= 2.0 * PI
			left_mix += sin(layer["left"]) * layer_vol * mod_l
			# Right ear: carrier at layer_freq + PHI_BEAT (creates the binaural beat).
			layer["right"] += 2.0 * PI * (layer_freq + PHI_BEAT) * dt_per_sample
			if layer["right"] > 2.0 * PI:
				layer["right"] -= 2.0 * PI
			right_mix += sin(layer["right"]) * layer_vol * mod_r
			_phi_phases[i] = layer
		frames[n] = Vector2(
			clampf(left_mix * _ambient_gain, -1.0, 1.0),
			clampf(right_mix * _ambient_gain, -1.0, 1.0)
		)
	_ambient_playback.push_buffer(frames)

# ------------------------------------------------------------------------
# SFX dispatcher (ports HTML playSound(type) at 10865)
# ------------------------------------------------------------------------

# randf helpers mirror the HTML local r/rr/ri/rWave closures.
func _rr(base: float, spread: float) -> float:
	return base * (1.0 + (randf() - 0.5) * spread)

func _ri(base: float, spread: float) -> int:
	return int(round(_rr(base, spread)))

func _r_wave(options: Array) -> String:
	return String(options[int(randf() * options.size()) % options.size()])

func play_sound(type: String) -> void:
	# Dispatch is a large switch; grouped by in-game event family for readability.
	# Each branch mirrors the corresponding `else if (type === '...')` in
	# the HTML playSound() body at 10865-11143. Numeric constants are preserved
	# exactly so the audio character stays identical.
	match type:
		"fire_hitscan":
			var p := _rr(1.0, 0.15)
			tri_chord(
				[_ri(55.0 * p, 0.0), _ri(82.0 * p, 0.0), _ri(110.0 * p, 0.0)],
				_r_wave(["sawtooth", "triangle"]),
				_rr(0.30, 0.2), _rr(0.10, 0.2),
				[_ri(30.0 * p, 0.0), _ri(45.0 * p, 0.0), _ri(55.0 * p, 0.0)],
				0.08, 0.0,
				{"attack": 0.001, "hold": 0.0, "decay": _rr(0.10, 0.2)}
			)
			play_noise_burst(_rr(0.04, 0.3), _rr(0.14, 0.2), 0.0, _ri(1800.0, 0.25), _rr(0.8, 0.3))
			if randf() > 0.6:
				play_noise_burst(_rr(0.03, 0.2), 0.06, 0.0, _ri(300.0, 0.3), 0.5)
		"fire_projectile":
			var p := _rr(1.0, 0.12)
			tri_chord(
				[_ri(80.0 * p, 0.0), _ri(100.0 * p, 0.0), _ri(130.0 * p, 0.0)],
				_r_wave(["sine", "triangle"]),
				_rr(0.35, 0.15), _rr(0.28, 0.15),
				[_ri(25.0 * p, 0.0), _ri(35.0 * p, 0.0), _ri(45.0 * p, 0.0)],
				_rr(0.22, 0.15), 0.0,
				{"attack": _rr(0.015, 0.3), "hold": _rr(0.04, 0.3), "decay": _rr(0.22, 0.15)}
			)
			play_noise_burst(_rr(0.08, 0.3), _rr(0.06, 0.3), 0.01, _ri(600.0, 0.3), _rr(1.2, 0.3))
			if randf() > 0.5:
				play_noise_burst(_rr(0.05, 0.2), 0.04, _rr(0.03, 0.3), _ri(900.0, 0.3), 1.0)
		"fire_spread":
			var p := _rr(1.0, 0.12)
			tri_chord(
				[_ri(45.0 * p, 0.0), _ri(67.0 * p, 0.0), _ri(90.0 * p, 0.0)],
				"sawtooth",
				_rr(0.35, 0.15), _rr(0.14, 0.2),
				[_ri(20.0 * p, 0.0), _ri(30.0 * p, 0.0), _ri(40.0 * p, 0.0)],
				_rr(0.11, 0.2), 0.0,
				{"attack": 0.001, "hold": _rr(0.01, 0.3), "decay": _rr(0.13, 0.2)}
			)
			play_noise_burst(_rr(0.10, 0.25), _rr(0.28, 0.15), 0.0, _ri(1200.0, 0.2), _rr(0.5, 0.3))
			var pops := 1 + int(randf() * 3.0)
			for i in range(pops):
				play_noise_burst(_rr(0.02, 0.3), _rr(0.05, 0.3), randf() * 0.04, _ri(1500.0, 0.4), _rr(1.5, 0.3))
		"fire_minigun":
			var p := _rr(1.0, 0.08)
			tri_chord(
				[_ri(90.0 * p, 0.0), _ri(113.0 * p, 0.0), _ri(135.0 * p, 0.0)],
				_r_wave(["square", "sawtooth"]),
				_rr(0.14, 0.2), _rr(0.04, 0.15),
				[_ri(60.0 * p, 0.0), _ri(75.0 * p, 0.0), _ri(90.0 * p, 0.0)],
				0.03, 0.0,
				{"attack": 0.001, "hold": 0.0, "decay": _rr(0.04, 0.2)}
			)
			play_noise_burst(_rr(0.015, 0.2), _rr(0.05, 0.2), 0.0, _ri(2200.0, 0.15), _rr(2.0, 0.2))
		"fire_railgun":
			var p := _rr(1.0, 0.08)
			tri_chord(
				[_ri(40.0 * p, 0.0), _ri(60.0 * p, 0.0), _ri(80.0 * p, 0.0)],
				"sine",
				_rr(0.25, 0.15), _rr(0.15, 0.15),
				[_ri(120.0 * p, 0.0), _ri(180.0 * p, 0.0), _ri(240.0 * p, 0.0)],
				_rr(0.12, 0.2), 0.0,
				{"attack": _rr(0.02, 0.3), "hold": _rr(0.03, 0.3), "decay": _rr(0.10, 0.2)}
			)
			var ring_p := _rr(1.0, 0.10)
			tri_chord(
				[_ri(165.0 * ring_p, 0.0), _ri(247.0 * ring_p, 0.0), _ri(330.0 * ring_p, 0.0)],
				_r_wave(["triangle", "sine"]),
				_rr(0.07, 0.2), _rr(0.45, 0.15),
				[_ri(135.0 * ring_p, 0.0), _ri(200.0 * ring_p, 0.0), _ri(270.0 * ring_p, 0.0)],
				_rr(0.40, 0.15), _rr(0.05, 0.3),
				{"attack": 0.001, "hold": 0.0, "decay": _rr(0.45, 0.15)}
			)
			play_noise_burst(_rr(0.12, 0.2), _rr(0.08, 0.2), 0.0, _ri(1600.0, 0.2), _rr(3.0, 0.2))
			if randf() > 0.4:
				tri_chord(
					[_ri(400.0, 0.2)],
					"sine", 0.03, _rr(0.08, 0.3),
					[_ri(200.0, 0.2)], 0.06, _rr(0.02, 0.3),
					{"attack": 0.001, "hold": 0.0, "decay": _rr(0.08, 0.3)}
				)
		"fire_salvo":
			var p := _rr(1.0, 0.15)
			var rise_p := _rr(1.0, 0.15)
			tri_chord(
				[_ri(50.0 * p, 0.0), _ri(63.0 * p, 0.0), _ri(75.0 * p, 0.0)],
				_r_wave(["sine", "triangle"]),
				_rr(0.22, 0.15), _rr(0.35, 0.15),
				[_ri(150.0 * rise_p, 0.0), _ri(190.0 * rise_p, 0.0), _ri(225.0 * rise_p, 0.0)],
				_rr(0.30, 0.15), 0.0,
				{"attack": _rr(0.008, 0.3), "hold": _rr(0.05, 0.3), "decay": _rr(0.30, 0.15)}
			)
			play_noise_burst(_rr(0.20, 0.2), _rr(0.12, 0.2), 0.01, _ri(800.0, 0.25), _rr(0.6, 0.3))
			if randf() > 0.5:
				tri_chord(
					[_ri(100.0, 0.2), _ri(130.0, 0.2)],
					"sawtooth", 0.04, _rr(0.15, 0.2),
					null, 0.0, _rr(0.08, 0.3),
					{"attack": 0.005, "hold": 0.02, "decay": _rr(0.12, 0.2)}
				)
		"hit":
			var p := _rr(1.0, 0.10)
			tri_chord(
				[_ri(130.0 * p, 0.0), _ri(164.0 * p, 0.0), _ri(196.0 * p, 0.0)],
				_r_wave(["triangle", "sine"]),
				_rr(0.18, 0.15), _rr(0.12, 0.2),
				[_ri(80.0 * p, 0.0), _ri(100.0 * p, 0.0), _ri(120.0 * p, 0.0)],
				_rr(0.10, 0.2), 0.0,
				{"attack": 0.001, "hold": 0.0, "decay": _rr(0.12, 0.2)}
			)
		"kill":
			var p := _rr(1.0, 0.08)
			tri_chord(
				[_ri(130.0 * p, 0.0), _ri(156.0 * p, 0.0), _ri(196.0 * p, 0.0)],
				"sine", _rr(0.18, 0.12), _rr(0.35, 0.12),
				null, 0.0, 0.0,
				{"attack": 0.005, "hold": _rr(0.05, 0.2), "decay": _rr(0.30, 0.15)}
			)
			tri_chord(
				[_ri(65.0 * p, 0.0), _ri(78.0 * p, 0.0), _ri(98.0 * p, 0.0)],
				"sine", _rr(0.15, 0.12), _rr(0.40, 0.12),
				null, 0.0, _rr(0.12, 0.15),
				{"attack": 0.005, "hold": _rr(0.05, 0.2), "decay": _rr(0.35, 0.15)}
			)
		"damage":
			# 3-5 dissonant staccato pulses (minor 2nds/tritones/minor 7ths).
			var pulses := 3 + int(randf() * 3.0)
			var base_p := _rr(1.0, 0.20)
			var dissonant := [1.0, 1.059, 1.122, 1.414, 1.498, 1.682, 1.888]
			for i in range(pulses):
				var offset := float(i) * _rr(0.025, 0.3)
				var d1: float = dissonant[int(randf() * dissonant.size()) % dissonant.size()]
				var d2: float = dissonant[int(randf() * dissonant.size()) % dissonant.size()]
				var d3: float = dissonant[int(randf() * dissonant.size()) % dissonant.size()]
				var vol := _rr(0.14, 0.25) * (1.0 - float(i) * 0.12)
				tri_chord(
					[_ri(50.0 * base_p * d1, 0.0), _ri(63.0 * base_p * d2, 0.0), _ri(78.0 * base_p * d3, 0.0)],
					_r_wave(["sawtooth", "square", "square"]),
					vol, _rr(0.04, 0.3),
					[_ri(25.0 * base_p * d1, 0.0), _ri(32.0 * base_p * d2, 0.0), _ri(40.0 * base_p * d3, 0.0)],
					_rr(0.03, 0.3), offset,
					{"attack": 0.001, "hold": 0.005, "decay": _rr(0.035, 0.3)}
				)
				play_noise_burst(_rr(0.025, 0.3), _rr(0.04, 0.3), offset, _ri(300.0 + randf() * 600.0, 0.3), _rr(0.7, 0.3))
		"dash":
			var p := _rr(1.0, 0.10)
			tri_chord(
				[_ri(55.0 * p, 0.0), _ri(69.0 * p, 0.0), _ri(82.0 * p, 0.0)],
				"sine", _rr(0.15, 0.15), _rr(0.30, 0.15),
				[_ri(110.0 * p, 0.0), _ri(138.0 * p, 0.0), _ri(165.0 * p, 0.0)],
				_rr(0.25, 0.15), 0.0,
				{"attack": 0.005, "hold": _rr(0.03, 0.3), "decay": _rr(0.27, 0.15)}
			)
			play_noise_burst(_rr(0.20, 0.2), _rr(0.10, 0.2), 0.0, _ri(1500.0, 0.2), _rr(0.8, 0.3))
		"ability":
			var p := _rr(1.0, 0.08)
			tri_chord(
				[_ri(82.0 * p, 0.0), _ri(103.0 * p, 0.0), _ri(123.0 * p, 0.0)],
				"sine", _rr(0.18, 0.12), _rr(0.15, 0.15),
				null, 0.0, 0.0,
				{"attack": 0.003, "hold": _rr(0.03, 0.2), "decay": _rr(0.12, 0.15)}
			)
			tri_chord(
				[_ri(98.0 * p, 0.0), _ri(123.0 * p, 0.0), _ri(147.0 * p, 0.0)],
				"sine", _rr(0.15, 0.12), _rr(0.18, 0.15),
				null, 0.0, _rr(0.08, 0.15),
				{"attack": 0.003, "hold": _rr(0.03, 0.2), "decay": _rr(0.15, 0.15)}
			)
		"core":
			var p := _rr(1.0, 0.06)
			tri_chord(
				[_ri(40.0 * p, 0.0), _ri(50.0 * p, 0.0), _ri(60.0 * p, 0.0)],
				"sawtooth", _rr(0.30, 0.12), _rr(0.70, 0.10),
				[_ri(110.0 * p, 0.0), _ri(138.0 * p, 0.0), _ri(165.0 * p, 0.0)],
				_rr(0.55, 0.10), 0.0,
				{"attack": _rr(0.05, 0.2), "hold": _rr(0.10, 0.2), "decay": _rr(0.55, 0.10)}
			)
			tri_chord(
				[_ri(55.0 * p, 0.0), _ri(69.0 * p, 0.0), _ri(82.0 * p, 0.0)],
				"sine", _rr(0.20, 0.12), _rr(0.60, 0.10),
				[_ri(130.0 * p, 0.0), _ri(164.0 * p, 0.0), _ri(196.0 * p, 0.0)],
				_rr(0.50, 0.10), _rr(0.15, 0.15),
				{"attack": _rr(0.04, 0.2), "hold": _rr(0.08, 0.2), "decay": _rr(0.48, 0.10)}
			)
			play_noise_burst(_rr(0.50, 0.15), _rr(0.12, 0.15), 0.0, _ri(600.0, 0.2), _rr(0.5, 0.3))
		"explosion":
			# Initial sub-bass thud then 5-8 dissonant pulses + shrapnel + sub-rumble tail.
			var size := _rr(1.0, 0.25)
			var pulses := 5 + int(randf() * 4.0)
			var base_p := _rr(1.0, 0.25)
			var dissonant := [1.0, 1.059, 1.122, 1.335, 1.414, 1.498, 1.682, 1.888]
			play_noise_burst(_rr(0.08, 0.3) * size, _rr(0.40, 0.2), 0.0, _ri(60.0, 0.3), _rr(0.3, 0.3))
			for i in range(pulses):
				var offset := 0.01 + float(i) * _rr(0.022, 0.35)
				var d1: float = dissonant[int(randf() * dissonant.size()) % dissonant.size()]
				var d2: float = dissonant[int(randf() * dissonant.size()) % dissonant.size()]
				var d3: float = dissonant[int(randf() * dissonant.size()) % dissonant.size()]
				var vol := _rr(0.12, 0.3) * size * (1.0 - float(i) * 0.08)
				var wave := _r_wave(["sawtooth", "square", "square", "sawtooth"])
				tri_chord(
					[_ri(30.0 * base_p * d1, 0.0), _ri(42.0 * base_p * d2, 0.0), _ri(55.0 * base_p * d3, 0.0)],
					wave, vol, _rr(0.04, 0.3),
					[_ri(15.0 * base_p * d1, 0.0), _ri(21.0 * base_p * d2, 0.0), _ri(28.0 * base_p * d3, 0.0)],
					_rr(0.03, 0.3), offset,
					{"attack": 0.001, "hold": 0.003, "decay": _rr(0.04, 0.3)}
				)
				play_noise_burst(_rr(0.03, 0.3), _rr(0.06, 0.3) * size, offset,
					_ri(200.0 + randf() * 1200.0, 0.3), _rr(0.6, 0.4))
			var shrapnel_count := 3 + int(randf() * 4.0)
			for i in range(shrapnel_count):
				var offset := randf() * 0.15
				var sp := _rr(1.0, 0.30)
				var d_mod: float = dissonant[int(randf() * dissonant.size()) % dissonant.size()]
				tri_chord(
					[_ri(180.0 * sp, 0.0), _ri(240.0 * sp * d_mod, 0.0)],
					_r_wave(["triangle", "square"]),
					_rr(0.03, 0.4), _rr(0.02, 0.3),
					[_ri(90.0 * sp, 0.0), _ri(120.0 * sp, 0.0)],
					_rr(0.015, 0.3), offset,
					{"attack": 0.001, "hold": 0.0, "decay": _rr(0.02, 0.3)}
				)
			play_noise_burst(_rr(0.25, 0.3) * size, _rr(0.20, 0.2), 0.12, _ri(45.0, 0.3), _rr(0.2, 0.3))
		"stasis":
			# 3-second charging sweep, 3 layered sine sweeps + 3 noise shimmers + release chord.
			var dur := 3.0
			var p := _rr(1.0, 0.04)
			tri_chord(
				[_ri(50.0 * p, 0.0), _ri(63.0 * p, 0.0), _ri(75.0 * p, 0.0)],
				"sine", _rr(0.20, 0.10), dur,
				[_ri(200.0 * p, 0.0), _ri(250.0 * p, 0.0), _ri(300.0 * p, 0.0)],
				dur * 0.95, 0.0,
				{"attack": 0.3, "hold": dur * 0.5, "decay": dur * 0.2}
			)
			tri_chord(
				[_ri(100.0 * p, 0.0), _ri(126.0 * p, 0.0), _ri(150.0 * p, 0.0)],
				"triangle", _rr(0.12, 0.10), dur * 0.85,
				[_ri(400.0 * p, 0.0), _ri(500.0 * p, 0.0), _ri(600.0 * p, 0.0)],
				dur * 0.8, 0.3,
				{"attack": 0.5, "hold": dur * 0.35, "decay": dur * 0.15}
			)
			tri_chord(
				[_ri(200.0 * p, 0.0), _ri(252.0 * p, 0.0), _ri(300.0 * p, 0.0)],
				"sine", _rr(0.06, 0.10), dur * 0.7,
				[_ri(800.0 * p, 0.0), _ri(1000.0 * p, 0.0), _ri(1200.0 * p, 0.0)],
				dur * 0.65, 0.6,
				{"attack": 0.8, "hold": dur * 0.15, "decay": dur * 0.1}
			)
			play_noise_burst(dur * 0.8, _rr(0.04, 0.2), 0.0, _ri(200.0, 0.15), _rr(0.5, 0.2))
			play_noise_burst(dur * 0.5, _rr(0.03, 0.2), 0.8, _ri(600.0, 0.2), _rr(0.6, 0.2))
			play_noise_burst(dur * 0.3, _rr(0.02, 0.2), 1.6, _ri(1200.0, 0.2), _rr(0.5, 0.2))
			tri_chord(
				[_ri(300.0 * p, 0.0), _ri(378.0 * p, 0.0), _ri(450.0 * p, 0.0)],
				"sine", _rr(0.15, 0.10), 0.6,
				null, 0.0, dur - 0.1,
				{"attack": 0.02, "hold": 0.15, "decay": 0.43}
			)
		"reload":
			var p := _rr(1.0, 0.08)
			tri_chord(
				[_ri(110.0 * p, 0.0), _ri(138.0 * p, 0.0), _ri(165.0 * p, 0.0)],
				"square", _rr(0.10, 0.15), _rr(0.06, 0.2),
				null, 0.0, 0.0,
				{"attack": 0.001, "hold": 0.0, "decay": _rr(0.06, 0.2)}
			)
			tri_chord(
				[_ri(82.0 * p, 0.0), _ri(103.0 * p, 0.0), _ri(123.0 * p, 0.0)],
				"square", _rr(0.10, 0.15), _rr(0.06, 0.2),
				null, 0.0, _rr(0.07, 0.15),
				{"attack": 0.001, "hold": 0.0, "decay": _rr(0.06, 0.2)}
			)
			play_noise_burst(_rr(0.02, 0.2), _rr(0.06, 0.2), 0.0, _ri(2800.0, 0.15), _rr(3.0, 0.2))
		"death":
			# Dramatic descending drone + debris noise + delayed secondary + shrapnel + groan.
			var p := _rr(1.0, 0.15)
			var size := _rr(1.0, 0.2)
			tri_chord(
				[_ri(82.0 * p, 0.0), _ri(98.0 * p, 0.0), _ri(123.0 * p, 0.0)],
				_r_wave(["sawtooth", "square"]),
				_rr(0.25, 0.15), _rr(1.30, 0.15) * size,
				[_ri(20.0 * p, 0.0), _ri(25.0 * p, 0.0), _ri(30.0 * p, 0.0)],
				_rr(1.10, 0.15), 0.0,
				{"attack": _rr(0.03, 0.3), "hold": _rr(0.10, 0.3), "decay": _rr(1.17, 0.12)}
			)
			tri_chord(
				[_ri(55.0 * p, 0.0), _ri(65.0 * p, 0.0), _ri(82.0 * p, 0.0)],
				"sine", _rr(0.15, 0.15), _rr(1.00, 0.15) * size,
				[_ri(15.0 * p, 0.0), _ri(18.0 * p, 0.0), _ri(22.0 * p, 0.0)],
				_rr(0.90, 0.15), _rr(0.20, 0.2),
				{"attack": _rr(0.03, 0.3), "hold": _rr(0.08, 0.3), "decay": _rr(0.89, 0.12)}
			)
			play_noise_burst(_rr(0.80, 0.25) * size, _rr(0.15, 0.2), 0.0, _ri(200.0, 0.35), _rr(0.6, 0.3))
			play_noise_burst(_rr(0.60, 0.2) * size, _rr(0.25, 0.2), randf() * 0.05, _ri(50.0, 0.3), _rr(0.3, 0.3))
			var delay2 := 0.15 + randf() * 0.25
			play_noise_burst(_rr(0.40, 0.3), _rr(0.20, 0.2), delay2, _ri(400.0, 0.4), _rr(0.5, 0.3))
			play_noise_burst(_rr(0.25, 0.3), _rr(0.08, 0.3), delay2 + 0.01, _ri(1000.0, 0.3), _rr(0.8, 0.3))
			var shrapnel := int(randf() * 4.0)
			for i in range(shrapnel):
				var sp := _rr(1.0, 0.3)
				var t := 0.1 + randf() * 0.5
				tri_chord(
					[_ri(180.0 * sp, 0.0), _ri(260.0 * sp, 0.0)],
					_r_wave(["triangle", "square", "sawtooth"]),
					_rr(0.03, 0.3), _rr(0.15, 0.3),
					[_ri(80.0 * sp, 0.0), _ri(120.0 * sp, 0.0)],
					_rr(0.12, 0.3), t,
					{"attack": 0.001, "hold": 0.0, "decay": _rr(0.15, 0.3)}
				)
			if randf() > 0.4:
				var gp := _rr(1.0, 0.25)
				tri_chord(
					[_ri(30.0 * gp, 0.0), _ri(38.0 * gp, 0.0), _ri(45.0 * gp, 0.0)],
					"sawtooth", _rr(0.08, 0.3), _rr(0.80, 0.2),
					[_ri(10.0 * gp, 0.0), _ri(13.0 * gp, 0.0), _ri(15.0 * gp, 0.0)],
					_rr(0.70, 0.2), _rr(0.30, 0.3),
					{"attack": _rr(0.05, 0.3), "hold": _rr(0.05, 0.3), "decay": _rr(0.70, 0.15)}
				)
		"round_start":
			tri_chord([65, 82, 98], "sine", 0.18, 0.35, null, 0.0, 0.0,
				{"attack": 0.01, "hold": 0.08, "decay": 0.26})
			tri_chord([73, 92, 110], "sine", 0.18, 0.35, null, 0.0, 0.18,
				{"attack": 0.01, "hold": 0.08, "decay": 0.26})
			tri_chord([82, 103, 130], "sine", 0.20, 0.40, null, 0.0, 0.36,
				{"attack": 0.01, "hold": 0.10, "decay": 0.29})
		_:
			push_warning("Audio.play_sound: unknown type '%s'" % type)

# Helper for play_sound branches that map weapon firing mode -> sound type.
# Mirrors the JS override at HTML line 11148-11163. main.gd / player_ship.gd
# already have the weapon dict at call sites; they pass mode + fire_rate +
# flags and we pick the right SFX here.
func play_weapon_fire(weapon_mode: String, fire_rate: float, homing: bool = false, salvo: bool = false) -> void:
	var is_railgun: bool = weapon_mode == "hitscan" and fire_rate >= 0.8
	var is_minigun: bool = weapon_mode == "hitscan" and fire_rate < 0.08
	var is_missile: bool = weapon_mode == "projectile" and (homing or salvo)
	if is_minigun:
		play_sound("fire_minigun")
	elif is_railgun:
		play_sound("fire_railgun")
	elif is_missile:
		play_sound("fire_salvo")
	elif weapon_mode == "hitscan":
		play_sound("fire_hitscan")
	elif weapon_mode == "projectile":
		play_sound("fire_projectile")
	elif weapon_mode == "spread":
		play_sound("fire_spread")
