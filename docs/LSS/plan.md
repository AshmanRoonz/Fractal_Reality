# Last Ship Sailing: Visual & Audio Polish Plan

Target file: `last_ship_sailing.html`

Priorities are roughly ordered by impact-per-line. Items within a section are independent unless noted.

## Visual

### V1. Depth and space (indoor arena context)
- **V1a. Cool-tinted second fog layer.** Add atmospheric perspective so distant silhouettes read; keep current low-density fog for walls, layer a subtle second pass tint for open volumes.
- **V1b. One-shot radial screen-space distortion on shockwave.** ~300 ms refraction warp around explosion center; sells concussion harder than more particles.
- **V1c. Cheap god-rays / radial blur near strong bloom sources.** Sampled toward a bright-emitter direction (sun light or big explosion) during its lifetime.

### V2. Ship readability and life
- **V2a. Fresnel rim-light on hull material.** Team-colored silhouette glow at glancing angles; instant target ID at distance.
- **V2b. Cockpit heartbeat pulse.** Slow 1 Hz emissive modulation (±10%) so the ship reads as alive when idle.
- **V2c. Plume length/intensity modulated by thrust.** `animateShipMesh` already knows speed; drive plume length and opacity from it.
- **V2d. Heat-haze quad behind plume tip.** Stretched billboard with a faint refraction texture.
- **V2e. Distance-scaled outline width.** Swap static `EdgesGeometry` lines for distance-aware outline (or simple LineBasicMaterial with dynamic opacity fallback).

### V3. Damage and feedback
- **V3a. Inverse-bloom shutter flash on kills.** One-frame negative exposure pulse through composite shader.
- **V3b. Screen-warp on damage (low-freq sin).** Subtle UV distortion when `damagePulse` > 0.
- **V3c. Doomed-state world warp.** Stronger, slower version of V3b while doomed.
- **V3d. Chromatic split on hit-marker / kill-marker.** Brief cyan/magenta separation confirms hit vs kill without text.

### V4. Particles and effects
- **V4a. Ember billboard with soft radial falloff.** Replace shared sphere geometry with camera-facing quad; procedural additive radial falloff texture (generated once).
- **V4b. Projectile ribbon trails.** 6-8 history positions per projectile rendered as line-strips, especially for railgun / missile / salvo.
- **V4c. Soft-particle smoke.** Depth-aware fade where billboards meet ship hulls; no more hard clip lines.
- **V4d. Explosion afterglow point light.** Third low-intensity warm point, ~1.5 s, so smoke is still lit after flash dies.

### V5. Lighting
- **V5a. Team-color rim PointLight child on each ship.** Very short range (~150 u), attached to ship root; tint player's own ship with team color.
- **V5b. (folded into V4d)** afterglow.

### V6. HUD polish
- **V6a. shadowBlur on active arcs.** Health/shield/core ring segments participate in the cinematic look.
- **V6b. Parallax HUD vs camera shake.** Translate ring positions inversely to shake so HUD feels cockpit-anchored.

## Audio

### A1. Spatialization (biggest wins)
- **A1a. HRTF PannerNode per-SFX.** Route explosions, gunfire, enemy thrusters through 3D panners positioned in world space.
- **A1b. Ambient bed stays unspatialized.** Binaural beats need direct-to-ears; only SFX bus becomes 3D.
- **A1c. Occlusion lowpass.** Raycast against level geometry (few frames per source); attenuate high freqs through walls.

### A2. Dynamics and mix
- **A2a. Master DynamicsCompressorNode.** threshold ~-18 dB, ratio ~4:1, attack 5 ms, release 100 ms; between `masterGain` and `hiCut`.
- **A2b. Side-chain duck on ambient.** Drop ambient 8-12 dB during loud SFX, restore over ~400 ms.
- **A2c. High-shelf boost on dry bus.** +2 dB @ 6 kHz before the 3.5 kHz cut so transients crack cleanly.

### A3. Reverb and space
- **A3a. Two convolvers, crossfaded by environment.** Tight ~0.5 s slap for tunnels; existing 2.4 s tail for open volumes.
- **A3b. Long lush send for explosions.** Separate ~5 s IR at low wet level for distant explosion tails.

### A4. Source material
- **A4a. Detune-chorus on triChord.** One detuned copy per oscillator (±5 cents, 30% mix); procedural sounds gain thickness.
- **A4b. Minigun sub-bed granular layer.** Stochastic noise grains at 30-50 ms; replaces many per-tick `triChord` calls, meatier and cheaper.
- **A4c. Sub-bass impulse at death onset.** 35 Hz sine, ADSR 5/100/600 ms; lands physically.
- **A4d. Shield-hit vs armor-hit differentiation.** Shield damage: high-pass + bell filter ("crystalline crack"). Armor damage: existing dissonance.

### A5. Gameplay-linked modulation
- **A5a. Ambient tremor by health.** Low-freq gain wobble scales with (1 - health%); peaks when doomed.
- **A5b. Round-start resolve up a fifth + reverse-cymbal swell.** Third chord resolves; noise burst with reversed envelope.
- **A5c. Lock-on sonar ping.** Rising pitch + rate as lock builds; 2 pip cycles at half-lock, 4 at full-lock.

### A6. Quality of life
- **A6a. Volume sliders in settings overlay.** Master / SFX / Music(ambient) / UI; expose existing gain nodes.
- **A6b. Headphones recommendation note.** One-line notice in settings about binaural bed.

## Execution order (decided after writing)

Start with low-risk, high-impact changes:
1. **A2a** compressor (mix glue, protects everything downstream)
2. **A6a + A6b** settings sliders + headphones note (user-visible, zero gameplay risk)
3. **A4a** detune-chorus (wider sound across all SFX)
4. **A4c** sub-bass impulse on death
5. **A4d** shield vs armor differentiation
6. **A2b** ambient side-chain duck
7. **A5a** health-tremor ambient
8. **A5c** lock-on sonar ping
9. **V2b** cockpit heartbeat pulse
10. **V2c** thrust-modulated plumes
11. **V2a** fresnel rim-light
12. **V4a** ember soft billboard
13. **V4d** explosion afterglow light
14. **V3b + V3c** damage/doomed warp
15. **V3a** kill shutter flash
16. **V3d** hit/kill chromatic split
17. **V6a** HUD shadowBlur
18. **V6b** HUD parallax
19. **V4b** projectile ribbon trails
20. **V1b** shockwave screen warp
21. **A1a + A1b** HRTF panner migration
22. **A1c** occlusion lowpass
23. **A3a** dual convolver crossfade
24. **A3b** explosion long send
25. **V1a** cool fog tint
26. **V1c** god-rays radial blur
27. **A4b** minigun granular bed
28. **A5b** round-start resolve
29. **V2d** heat haze
30. **V2e** distance outline
31. **V5a** team rim light

## Notes
- Match the file's existing style: shader uniforms, ShaderMaterial passes, procedural Web Audio with no external assets.
- Prefer adding toggles in the settings overlay for visually disruptive effects (warp, chromatic split) so users can dial them.
- Respect the file's cap on particles / effects (`MAX_PARTICLES`, `MAX_EFFECTS`); any new spawners should cost budget.
- Keep audio CPU conservative; reuse buffers where possible (impulse responses, noise buffers).
