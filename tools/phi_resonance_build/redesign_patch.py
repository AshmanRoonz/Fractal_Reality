"""Give docs/phi_resonance.html the Last Ship Sailing interface."""
import io, os, sys

p = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
s = io.open(p, encoding='utf-8', newline='').read()

def piece(name):
    return io.open(os.path.join(here, name), encoding='utf-8').read()

def rep(a, b, count=1):
    global s
    n = s.count(a)
    assert n == count, 'anchor matched %d times (wanted %d): %r' % (n, count, a[:90])
    s = s.replace(a, b)

# ---- head: theme colour and the game's fonts ----
rep('<meta name="theme-color" content="#0a0a1a">',
    '<meta name="theme-color" content="#05050f">\n'
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;600;700;900&family=Rajdhani:wght@400;500;600;700&display=swap" rel="stylesheet">')

# ---- the stylesheet ----
a = s.index('<style>') + len('<style>')
b = s.index('</style>')
s = s[:a] + '\n' + piece('shell.css') + s[b:]

# ---- the page ----
a = s.index('<body>')
b = s.index('<script>')
s = s[:a] + piece('shell_body.html') + s[b:]

# ---- the shell's code, before the click-to-edit section ----
rep('  // ============= CLICK-TO-EDIT SLIDER VALUES =============',
    piece('shell.js') + '  // ============= CLICK-TO-EDIT SLIDER VALUES =============')

# the main screen's preset picker follows every preset change
rep("""      btn.addEventListener('click', () => applyPreset(pr.id));
      grid.appendChild(btn);
    });
  }""", """      btn.addEventListener('click', () => applyPreset(pr.id));
      grid.appendChild(btn);
    });
    updatePresetPicker();
  }""")

# ---- the field radiates from the centre of the stage ----
rep("""  function drawBG() {
    const t = Date.now() / 1000;
    const cx = bg.width / 2, cy = bg.height / 2;""", """  function drawBG() {
    const t = Date.now() / 1000;
    // the field radiates from the centre of the stage (the screen centre if it
    // is not laid out); the canvas is fixed, so the rings follow a scroll
    const orbEl = document.getElementById('stageOrb');
    const orbBox = orbEl ? orbEl.getBoundingClientRect() : null;
    const cx = orbBox && orbBox.width ? orbBox.left + orbBox.width / 2 : bg.width / 2;
    const cy = orbBox && orbBox.height ? orbBox.top + orbBox.height / 2 : bg.height / 2;""")

# ---- the waveform strip at rest: a slow, faint swell along the strip (the
# field's spiral now turns around the stage's circumpunct, so a second small
# spiral under it read as a stray glyph) ----
rep("""    } else {
      vctx.strokeStyle = 'rgba(255,215,0,0.25)';
      vctx.lineWidth = 1;
      vctx.beginPath();
      for (let a = 0; a < 8*Math.PI; a += 0.05) {
        const r = 3 * Math.pow(PHI, a / TWO_PI);
        const x = w/2 + r * Math.cos(a + t/3);
        const y = cy + r * Math.sin(a + t/3);
        if (a === 0) vctx.moveTo(x,y); else vctx.lineTo(x,y);
        if (r > Math.max(w, h)) break;
      }
      vctx.stroke();
    }""", """    } else {
      // at rest: the waveform breathes slowly along the strip, fading at the ends
      vctx.strokeStyle = 'rgba(255,170,0,0.28)';
      vctx.lineWidth = 1;
      vctx.beginPath();
      for (let x = 0; x <= w; x += 2) {
        const env = Math.sin(Math.PI * x / w);
        const y = cy + Math.sin(x / w * TWO_PI * PHI + t * 0.5) * h * 0.08 * env;
        if (x === 0) vctx.moveTo(x, y); else vctx.lineTo(x, y);
      }
      vctx.stroke();
    }""")

# ---- trails fade toward transparent, not toward black, so the deep-space
# backdrop behind both canvases stays visible ----
rep("""    bctx.fillStyle = 'rgba(0,0,0,0.05)';
    bctx.fillRect(0, 0, bg.width, bg.height);""", """    // trails fade toward transparent (not black) so the backdrop shows through
    bctx.save();
    bctx.globalCompositeOperation = 'destination-out';
    bctx.fillStyle = 'rgba(0,0,0,0.05)';
    bctx.fillRect(0, 0, bg.width, bg.height);
    bctx.restore();""")
rep("""    vctx.fillStyle = 'rgba(0,0,0,0.12)';
    vctx.fillRect(0, 0, w, h);""", """    vctx.save();
    vctx.globalCompositeOperation = 'destination-out';
    vctx.fillStyle = 'rgba(0,0,0,0.12)';
    vctx.fillRect(0, 0, w, h);
    vctx.restore();""")

# ---- while playing: thin rings around the circumpunct instead of filled
# discs (the discs' trails flooded the whole screen with amber) ----
rep("""    } else {
      // gentle pulsing rings per layer
      state.nodes.forEach((n, idx) => {
        if (!n) return;
        const phase = n.beat ? (t * n.beat * 0.5) : (t * 0.2 + idx*0.4);
        const intensity = 0.5 + 0.5 * Math.sin(phase * TWO_PI);
        const r = 60 + idx * 70 + intensity * 30;
        const g = bctx.createRadialGradient(cx, cy, r*0.2, cx, cy, r);
        g.addColorStop(0, 'rgba(255,215,0,' + (0.12 * intensity) + ')');
        g.addColorStop(1, 'rgba(255,215,0,0)');
        bctx.fillStyle = g;
        bctx.beginPath();
        bctx.arc(cx, cy, r, 0, TWO_PI);
        bctx.fill();
      });
    }""", """    } else {
      // one ring per layer around the stage's centre, swelling at its beat
      // (folded by octaves into 0.5 to 2 Hz); thin lines whose trails fade,
      // so the field glows without flooding the screen
      const gr = orbBox && orbBox.height ? Math.min(orbBox.width, orbBox.height) * 0.18 : 60;
      const r0 = Math.max(50, gr * 1.15), step = Math.max(46, gr * 0.75);
      state.nodes.forEach((n, idx) => {
        if (!n) return;
        let rate = n.beat || 0;
        if (rate > 0) { while (rate > 2) rate /= 2; while (rate < 0.5) rate *= 2; }
        const phase = rate ? t * rate : (t * 0.2 + idx * 0.4);
        const intensity = 0.5 + 0.5 * Math.sin(phase * TWO_PI);
        const r = r0 + idx * step + intensity * step * 0.4;
        bctx.strokeStyle = 'rgba(255,170,0,' + (0.04 + 0.1 * intensity).toFixed(3) + ')';
        bctx.lineWidth = 1.5;
        bctx.beginPath();
        bctx.arc(cx, cy, r, 0, TWO_PI);
        bctx.stroke();
      });
    }""")

# the stop glyph as text, like the play triangle (the emoji square drew a dark box)
rep("$('playBtn').textContent = '⬛ STOP SESSION';", "$('playBtn').textContent = '■ STOP SESSION';")

# ---- the breath guide pairs with the flashing visuals (owner, 2026-10-18:
# "the breathing bar should be able to be paired with flashing visuals ...
# able to put in the main visual window as well") ----
a = s.index('  // ============= BREATH LEAD (dot on a half sine; 3 - 12 bpm) =============')
b = s.index('  // ============= THE SHELL: tabs, breath guide, preset picker, stage =============')
assert a < b and s.count('// ============= BREATH LEAD') == 1
s = s[:a] + piece('breath.js') + s[b:]

rep("""    phaseOffset: 0,       // degrees
    baseDivisor: 1000
  };""", """    phaseOffset: 0,       // degrees
    baseDivisor: 1000,
    where: 'full'         // 'full' screen, or 'stage': inside the main window
  };""")
rep("""    const offsetPhase = ((state.vbeat.phaseOffset || 0) / 360);
    const phase = ((elapsed * rate) + offsetPhase) % 1;  // 0..1 per flash cycle
""", """    const offsetPhase = ((state.vbeat.phaseOffset || 0) / 360);
    let phase = ((elapsed * rate) + offsetPhase) % 1;  // 0..1 per flash cycle
    // Following the breath guide while it breathes: one flash per breath,
    // locked to it, brightest at the top of the inhale, darkest when empty
    if (state.vbeat.sync === 'breath' && state.breath && state.breath.playing) {
      phase = (breathU(now) + 0.5 + offsetPhase) % 1;
    }
""")
rep("""    // Render
    const panel = $('flashPanel');
    const canvas = $('flashCanvas');
    if (state.vbeat.shape === 'radial' || state.vbeat.shape === 'ring' || state.vbeat.shape === 'split') {
      panel.style.background = '#000';
      canvas.style.display = 'block';
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const w = canvas.width = Math.floor(window.innerWidth * dpr);
      const h = canvas.height = Math.floor(window.innerHeight * dpr);
""", """    // Render: full screen, or behind everything on the main window's stage
    const inStage = state.vbeat.where === 'stage';
    const panel = inStage ? $('stageFlash') : $('flashPanel');
    const canvas = inStage ? $('stageFlashCanvas') : $('flashCanvas');
    if (state.vbeat.shape === 'radial' || state.vbeat.shape === 'ring' || state.vbeat.shape === 'split') {
      panel.style.background = '#000';
      canvas.style.display = 'block';
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const box = inStage ? panel.getBoundingClientRect() : { width: window.innerWidth, height: window.innerHeight };
      const w = Math.floor(box.width * dpr), h = Math.floor(box.height * dpr);
      if (canvas.width !== w) canvas.width = w;
      if (canvas.height !== h) canvas.height = h;
""")
rep("""  function openFlash() {
    const overlay = $('flashOverlay');
    overlay.classList.add('active');
    state.vbeat.active = true;
    state.vbeat.t0 = 0;
    state.vbeat.shape = $('vbeatShape').value;
    state.vbeat.intensity = parseInt($('vbeatInt').value, 10) / 100;
    state.vbeat.src = $('vbeatSrc').value;
    // Request fullscreen (best effort; silently falls back to fixed overlay)
    if (overlay.requestFullscreen) {
      overlay.requestFullscreen().catch(() => {});
    } else if (overlay.webkitRequestFullscreen) {
      overlay.webkitRequestFullscreen();
    }
    cancelAnimationFrame(state.vbeat.raf);
    state.vbeat.raf = requestAnimationFrame(flashLoop);
  }

  function closeFlash() {
    state.vbeat.active = false;
    cancelAnimationFrame(state.vbeat.raf);
    $('flashOverlay').classList.remove('active');
    if (document.fullscreenElement) {
      document.exitFullscreen().catch(() => {});
    } else if (document.webkitFullscreenElement && document.webkitExitFullscreen) {
      document.webkitExitFullscreen();
    }
  }""", """  function openFlash() {
    const overlay = $('flashOverlay');
    state.vbeat.active = true;
    state.vbeat.t0 = 0;
    state.vbeat.shape = $('vbeatShape').value;
    state.vbeat.intensity = parseInt($('vbeatInt').value, 10) / 100;
    state.vbeat.src = $('vbeatSrc').value;
    // the breath guide rides over the flashes when asked to, breathing
    if (state.breath.onFlash && !state.breath.playing) startBreath();
    if (state.vbeat.where === 'stage') {
      // in the main window the stage flashes behind the circumpunct
      revealStage();
      $('stage').classList.add('flashing');
      $('stageFlashStop').hidden = false;
    } else {
      overlay.classList.add('active');
      // Request fullscreen (best effort; silently falls back to fixed overlay)
      if (overlay.requestFullscreen) {
        overlay.requestFullscreen().catch(() => {});
      } else if (overlay.webkitRequestFullscreen) {
        overlay.webkitRequestFullscreen();
      }
    }
    syncFlashControls();
    cancelAnimationFrame(state.vbeat.raf);
    state.vbeat.raf = requestAnimationFrame(flashLoop);
  }

  function closeFlash() {
    state.vbeat.active = false;
    cancelAnimationFrame(state.vbeat.raf);
    const overlay = $('flashOverlay');
    overlay.classList.remove('active');
    $('stage').classList.remove('flashing');
    $('stageFlashStop').hidden = true;
    $('stageFlash').style.background = '';
    // leave the app's own full screen alone; only the flash view's ends here
    if (document.fullscreenElement === overlay) {
      document.exitFullscreen().catch(() => {});
    } else if (document.webkitFullscreenElement === overlay && document.webkitExitFullscreen) {
      document.webkitExitFullscreen();
    }
    syncFlashControls();
  }""")
rep("""  $('vbeatLaunch').addEventListener('click', openFlash);""",
    """  $('vbeatLaunch').addEventListener('click', () => { if (state.vbeat.active) closeFlash(); else openFlash(); });""")
rep("""    if (!document.fullscreenElement && state.vbeat.active) closeFlash();""",
    """    if (!document.fullscreenElement && state.vbeat.active && state.vbeat.where !== 'stage') closeFlash();""")

# ---- the Export tab became File (save and load settings): the Serum 2
# wavetable export goes, with its helpers (nothing else uses them) ----
a = s.index('  // ============= SERUM 2 EXPORT =============')
z = s.index('  // Chips: solfeggio, chakras, brainwaves, ratios, freq sets')
assert a < z and s.count('// ============= SERUM 2 EXPORT') == 1
s = s[:a] + s[z:]
rep("empty.textContent = 'No saved states yet. Dial in your settings, give them a name, save.';",
    "empty.textContent = 'Nothing saved yet. Set things the way you like, give them a name, and save.';")
rep("loadB.title = 'Load this state';", "loadB.title = 'Load these settings';")

# ---- Ashman1, the starting sound (owner, 2026-10-19), first in the preset list ----
rep("""  const PRESETS = [
""", """  const PRESETS = [
    { id: 'ashman1',     name: 'ASHMAN1',         desc: '144 base, 2.1 Hz binaural, triangle, octave layers', base: 144, beat: 2.1, beta: 0.25, mode: 'binaural', wave: 'triangle', spacing: 'octave' },
""")
rep("""    currentPreset: 'phibeat',
""", """    currentPreset: 'ashman1',   // the starting sound
""")
rep("""      base: 432, beat: PHI, vol: 25, wave: 'sine', detune: 0,
      spacing: 'phi', stereo: 100, beatStr: 100,
""", """      base: 144, beat: 2.1, vol: 25, wave: 'triangle', detune: 0,
      spacing: 'octave', stereo: 100, beatStr: 100,
""")
rep("""  updateStatsFromParams();
  drawBG();
  drawViz();
""", """  updateStatsFromParams();
  // the controls start on the starting preset: sliders, waveform, spacing, mode, readouts
  applyPreset(state.currentPreset);
  drawBG();
  drawViz();
""")

# ---- canvases in the game's amber ----
rep("rgba(255,215,0,", "rgba(255,170,0,", count=2)

# ---- one reverb across setting changes (owner, 2026-10-19: changing settings stuttered on a phone) ----
rep("""  function spacingRatio(kind, i) {""", """  // ----- one reverb across setting changes -----
  // Most setting changes rebuild the field and crossfade to the new one. The
  // reverb is the heaviest part, so it is no longer rebuilt with them (owner,
  // 2026-10-19: in the phone app, changing settings stuttered; each change
  // ran a second reverb, made from fresh noise, beside the first). Each audio
  // context keeps one reverb; every graph feeds it through its own fade, and
  // it is replaced only when Reverb size changes. It lives while the live
  // engine sounds: a stop, or the lock loop taking over, fades it out and
  // lets it go.
  function sharedReverb(ctx, dest, size) {
    const v = ctx.phiVerb;
    if (v && v.size === size && v.dest === dest) {
      reverbLevel(v, state.params.rev / 100, 0.05);   // back up if a stop was fading it
      return v;
    }
    if (v) dropReverb(ctx, FADE_CHANGE + v.size + 0.5);   // the old one rings out first
    const input = ctx.createGain();
    const convolver = ctx.createConvolver();
    convolver.buffer = createReverbImpulse(size, 2.5);
    const wet = ctx.createGain();
    wet.gain.value = state.params.rev / 100;
    input.connect(convolver);
    convolver.connect(wet);
    wet.connect(dest);
    [input, convolver, wet].forEach(n => { n.phiShared = true; });   // teardownGraph leaves these
    ctx.phiVerb = { size, dest, input, convolver, wet };
    return ctx.phiVerb;
  }

  // Ramp the shared reverb's output (it follows the live sound out)
  function reverbLevel(v, level, sec) {
    if (!v) return;
    const g = v.wet.gain, now = v.wet.context.currentTime;
    g.cancelScheduledValues(now);
    g.setValueAtTime(g.value, now);
    g.linearRampToValueAtTime(level, now + Math.max(0.01, sec));
  }

  // Let a context's reverb go, after afterSec (0: now)
  function dropReverb(ctx, afterSec) {
    const v = ctx && ctx.phiVerb;
    if (!v) return;
    ctx.phiVerb = null;
    const off = () => [v.input, v.convolver, v.wet].forEach(n => { try { n.disconnect(); } catch (e) {} });
    if (afterSec > 0) setTimeout(off, afterSec * 1000); else off();
  }

  function spacingRatio(kind, i) {""")
rep("""    // Per-graph fade stage: dry + wet -> fade -> destination
""", """    // Per-graph fade stage: the dry sound -> fade -> destination, and on into the shared reverb
""")
rep("""    // master + effects chain: [sources] -> filter? -> master -> (dry + wet via convolver) -> destination
""", """    // master + effects chain: [sources] -> filter? -> master -> dry -> fade -> destination (+ the shared reverb)
""")
rep("""    // Reverb
    state.convolver = ctx.createConvolver();
    state.convolver.buffer = createReverbImpulse(p.revSz, 2.5);
    state.wetGain = ctx.createGain();
    state.dryGain = ctx.createGain();
    state.wetGain.gain.value = p.rev / 100;
    state.dryGain.gain.value = 1;
    state.masterGain.connect(state.dryGain);
    state.masterGain.connect(state.convolver);
    state.convolver.connect(state.wetGain);
    state.dryGain.connect(state.fade);
    state.wetGain.connect(state.fade);
""", """    // Reverb: the context's one reverb (sharedReverb), fed after this graph's
    // fade, so a crossfade or a fade-out moves this graph out of the reverb as
    // well as out of the dry sound
    const verb = sharedReverb(ctx, dest || ctx.destination, p.revSz);
    state.convolver = verb.convolver;
    state.wetGain = verb.wet;
    state.dryGain = ctx.createGain();
    state.dryGain.gain.value = 1;
    state.masterGain.connect(state.dryGain);
    state.dryGain.connect(state.fade);
    state.fade.connect(verb.input);
""")
rep("""    ['masterGain','filter','convolver','wetGain','dryGain','fade'].forEach(k => {
      if (g[k]) { try { g[k].disconnect(); } catch(e){} }""", """    // the shared reverb outlives the graphs (sharedReverb)
    ['masterGain','filter','convolver','wetGain','dryGain','fade'].forEach(k => {
      if (g[k] && !g[k].phiShared) { try { g[k].disconnect(); } catch(e){} }""")
rep("""      } else {
        fadeOutGraph(detachGraph(), fadeSec);
      }
    }
    state.playing = false;""", """      } else {
        fadeOutGraph(detachGraph(), fadeSec);
      }
      reverbLevel(state.ctx.phiVerb, 0, fadeSec);   // the shared reverb fades with the sound
    }
    state.playing = false;""")
rep("""      // Nothing left to render; let the engine sleep (start resumes it)
      if (state.ctx && state.ctx.state === 'running') state.ctx.suspend();""", """      // Nothing left to render; let the engine sleep (start resumes it)
      dropReverb(state.ctx, 0);
      if (state.ctx && state.ctx.state === 'running') state.ctx.suspend();""")
rep("""    if (fadeSec > 0) fadeOutGraph(g, fadeSec); else teardownGraph(g);
""", """    if (fadeSec > 0) fadeOutGraph(g, fadeSec); else teardownGraph(g);
    reverbLevel(state.ctx && state.ctx.phiVerb, 0, fadeSec);   // the shared reverb goes with it
""")
rep("""      if (loopState.active && state.ctx && state.ctx.state === 'running') state.ctx.suspend();""",
    """      if (loopState.active && state.ctx && state.ctx.state === 'running') { dropReverb(state.ctx, 0); state.ctx.suspend(); }""")

# ---- lighter setting changes (owner, 2026-10-19: after a while of changing settings, the phone app got really hitchy) ----
# a) every source can be told when to stop, so a fading graph stops on the audio clock
a = s.index('  function makeOscillator(freq, waveType) {')
b = s.index('  function startNoiseBed() {')
sec = s[a:b]
counts = (sec.count('stopAll: () =>'), sec.count('.stop();'), sec.count('.stopAll();'))
assert counts[0] >= 10 and counts[1] >= 10 and counts[2] >= 5, counts
sec = sec.replace('stopAll: () =>', 'stopAll: (t) =>').replace('.stop();', '.stop(t);').replace('.stopAll();', '.stopAll(t);')
s = s[:a] + sec + s[b:]
rep("""  function fadeOutGraph(g, sec) {
    if (!g.fade) { teardownGraph(g); return; }
    rampGain(g.fade.gain, 0, sec);
    setTimeout(() => teardownGraph(g), sec * 1000 + 80);
  }""", """  function fadeOutGraph(g, sec) {
    if (!g.fade) { teardownGraph(g); return; }
    rampGain(g.fade.gain, 0, sec);
    // Its sources stop on the audio clock the moment the fade ends, so the old
    // sound costs nothing once it is silent, however late the timer below runs
    // on a busy phone (owner, 2026-10-19: changing settings got hitchy)
    stopGraphAt(g, g.fade.context.currentTime + sec);
    setTimeout(() => teardownGraph(g), sec * 1000 + 80);
  }

  // Schedule every source of a detached graph to stop at context time t
  function stopGraphAt(g, t) {
    (g.nodes || []).forEach(n => { if (n && n.stopAll) { try { n.stopAll(t); } catch (e) {} } });
    if (g.noiseNodes) {
      try { g.noiseNodes.source && g.noiseNodes.source.stop(t); } catch (e) {}
      (g.noiseNodes.extras || []).forEach(n => { try { n.stop && n.stop(t); } catch (e) {} });
    }
  }""")
# b) a shorter crossfade: the old and the new sound run together only this long
rep("""  // Fade times (seconds): sessions breathe in and out; parameter changes crossfade
  const FADE_IN = 3, FADE_OUT = 1.5, FADE_TIMER_END = 8, FADE_CHANGE = 0.35;""",
    """  // Fade times (seconds): sessions breathe in and out; parameter changes crossfade.
  // A change's crossfade is 0.25 s (it was 0.35): for that long the old and the
  // new sound both play, the heaviest moment for a phone.
  const FADE_IN = 3, FADE_OUT = 1.5, FADE_TIMER_END = 8, FADE_CHANGE = 0.25;""")
# c) noise is made once per audio context, type and length
rep("""  function createNoise(type, durationSec = 4) {
    const ctx = state.ctx;""", """  // Noise is made once per audio context, type and length, then reused: every
  // setting change used to make it again (megabytes of fresh noise each time)
  const noiseCache = new WeakMap();
  function createNoise(type, durationSec = 4) {
    const ctx = state.ctx;
    let kept = noiseCache.get(ctx);
    if (!kept) noiseCache.set(ctx, kept = new Map());
    const key = type + '|' + durationSec;
    if (!kept.has(key)) kept.set(key, makeNoise(type, durationSec));
    return kept.get(key);
  }

  function makeNoise(type, durationSec) {
    const ctx = state.ctx;""")

# ---- cheap flashes (owner, 2026-10-19: the app's sound was good until the visuals started) ----
rep("""  function flashLoop(now) {""", """  // While the full-screen flashes cover the page, nothing under them is drawn
  function coveredByFlash() {
    return !!(state.vbeat && state.vbeat.active && state.vbeat.where !== 'stage');
  }

  // The flash colour without a repaint per frame: the panel stays black, a
  // layer of the hue at 50% lightness and a white layer sit on it (shell
  // markup), and only their opacities move. Below 50% HSL lightness is a
  // straight blend toward black, above it toward white, so this shows exactly
  // hsl(hue, sat, light). Each frame used to repaint the panel in a new colour.
  function paintTint(panel, hue, sat, light) {
    const t = panel.querySelectorAll('.flash-tint');
    if (t.length < 2) { panel.style.background = hslCss(hue, sat, light); return; }
    const col = hslCss(hue, sat, 50);
    if (t[0].phiCol !== col) { t[0].style.background = col; t[0].phiCol = col; }
    setOpacity(t[0], Math.min(1, light / 50));
    setOpacity(t[1], Math.max(0, (light - 50) / 50));
  }
  function setOpacity(el, v) {
    const s = v.toFixed(3);
    if (el.phiOp !== s) { el.style.opacity = s; el.phiOp = s; }
  }
  function hideTint(panel) {
    panel.querySelectorAll('.flash-tint').forEach(el => setOpacity(el, 0));
  }
  // Text is written only when it changes (rewriting it every frame forced a layout)
  function setText(el, s) {
    if (el && el.textContent !== s) el.textContent = s;
  }

  function flashLoop(now) {""")
rep("""      panel.style.background = '#000';
      canvas.style.display = 'block';
""", """      panel.style.background = '#000';
      canvas.style.display = 'block';
      hideTint(panel);
""")
rep("""      canvas.style.display = 'none';
      panel.style.background = hslCss(hue, sat, 10 + 45 * I);
""", """      canvas.style.display = 'none';
      paintTint(panel, hue, sat, 10 + 45 * I);
""")
rep("""    $('flashHUDNote').textContent = note + ' · ' + colorName;
    $('flashHUDRate').textContent = rate.toFixed(3) + ' Hz · ' + state.vbeat.shape + ' · ' + state.vbeat.sync;
""", """    setText($('flashHUDNote'), note + ' · ' + colorName);
    setText($('flashHUDRate'), rate.toFixed(3) + ' Hz · ' + state.vbeat.shape + ' · ' + state.vbeat.sync);
""")
rep("""    $('stageFlash').style.background = '';
""", """    $('stageFlash').style.background = '';
    hideTint($('stageFlash'));
    hideTint($('flashPanel'));
""")
rep("""  function drawBG() {
    const t = Date.now() / 1000;
""", """  function drawBG() {
    if (coveredByFlash()) { requestAnimationFrame(drawBG); return; }
    const t = Date.now() / 1000;
""")
rep("""  function drawViz() {
    const w = viz.width, h = viz.height;
""", """  function drawViz() {
    if (coveredByFlash()) { requestAnimationFrame(drawViz); return; }
    const w = viz.width, h = viz.height;
""")

# ---- a frame cap (owner, 2026-10-19: measured on the owner's Pixel 9, the page's drawing took about three cores) ----
rep("""  const $ = (id) => document.getElementById(id);
""", """  const $ = (id) => document.getElementById(id);

  // Animation is capped: phones draw at most 30 frames a second, other screens 60
  // (owner, 2026-10-19: measured on a Pixel 9, whose screen runs at 120 Hz, the
  // page's drawing took about three CPU cores, the phone throttled, and the
  // audio broke up). Each loop asks frameDue before it draws, and fades scale
  // with the time since its last frame, so trails last as long at any rate.
  const FRAME_MS = (/Android|iPhone|iPad|iPod/i.test(navigator.userAgent) ||
    (navigator.maxTouchPoints > 1 && /Macintosh/.test(navigator.userAgent)) ? 1000 / 30 : 1000 / 60) - 2;
  const frameLast = {};
  // ms since this loop last drew, or 0 when it is not yet due
  function frameDue(key, now, ms) {
    now = now || performance.now();
    const last = frameLast[key] || 0;
    if (now - last < (ms || FRAME_MS)) return 0;
    frameLast[key] = now;
    return last ? Math.min(now - last, 250) : 1000 / 60;
  }
  // a fade of `alpha` per 60th of a second, over a frame of `dt` ms
  function fadeFor(alpha, dt) {
    return 1 - Math.pow(1 - alpha, dt / (1000 / 60));
  }
  // Phones also rest the title tag's never-ending CSS animation, which kept the
  // screen redrawing at its full rate: the jitter stops, and the glitch fires as a
  // one-off every 4.7 s, its old period (see .lite-motion in the style)
  if (FRAME_MS > 1000 / 60) {
    document.documentElement.classList.add('lite-motion');
    const still = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!still) setInterval(() => {
      if (document.hidden) return;
      document.querySelectorAll('.lss-tag').forEach(t => {
        t.classList.add('glitch-shot');
        setTimeout(() => t.classList.remove('glitch-shot'), 140);
      });
    }, 4700);
  }
""")
rep("""  function drawBG() {
    if (coveredByFlash()) { requestAnimationFrame(drawBG); return; }
    const t = Date.now() / 1000;
""", """  function drawBG(now) {
    const dt = coveredByFlash() ? 0 : frameDue('bg', now);
    if (!dt) { requestAnimationFrame(drawBG); return; }
    const t = Date.now() / 1000;
""")
rep("""    bctx.fillStyle = 'rgba(0,0,0,0.05)';""", """    bctx.fillStyle = 'rgba(0,0,0,' + fadeFor(0.05, dt).toFixed(4) + ')';""")
rep("""  function drawViz() {
    if (coveredByFlash()) { requestAnimationFrame(drawViz); return; }
    const w = viz.width, h = viz.height;
""", """  function drawViz(now) {
    const dt = coveredByFlash() ? 0 : frameDue('viz', now);
    if (!dt) { requestAnimationFrame(drawViz); return; }
    const w = viz.width, h = viz.height;
""")
rep("""    vctx.fillStyle = 'rgba(0,0,0,0.12)';""", """    vctx.fillStyle = 'rgba(0,0,0,' + fadeFor(0.12, dt).toFixed(4) + ')';""")
# the flashes: at most 60 frames a second everywhere (what a 60 Hz screen always showed)
rep("""  function flashLoop(now) {
    if (!state.vbeat.active) return;
""", """  function flashLoop(now) {
    if (!state.vbeat.active) return;
    if (!frameDue('flash', now, 1000 / 60 - 2)) { state.vbeat.raf = requestAnimationFrame(flashLoop); return; }
""")

# ---- a preset is a whole sound, and Reset all settings (owner, 2026-10-28: after playing with
# the sliders and tabs, going back to Ashman1 "sounded completely different"; a built-in preset
# set only base, beat, wave, spacing and mode, so every other setting stayed as it was left) ----
rep("""  function applyPreset(id) {
    const pr = PRESETS.find(p => p.id === id);
    if (!pr) return;
    state.currentPreset = id;
""", """  function applyPreset(id) {
    const pr = PRESETS.find(p => p.id === id);
    if (!pr) return;
    // A preset is a whole sound: every setting starts from the starting sound, then the
    // preset sets its own. The volume and the session timer stay as they are.
    if (FACTORY) {
      const vol = state.params.vol;
      restoreSettings(FACTORY, { keepTimer: true, quiet: true });
      state.params.vol = vol;
      $('vol').value = vol;
      updateVolumeCaution(vol);
    }
    state.currentPreset = id;
""")
# saved settings and the starting sound go in place through one function
rep("""  function loadSaved(name) {
    const all = getSaved();
    const s = all[name];
    if (!s) return;
    state.mode = s.mode || state.mode;""", """  // The starting sound, whole, taken once the page has set itself up: presets start from it,
  // and Reset all settings goes back to it
  let FACTORY = null;

  // Put a whole set of settings in place: saved settings, or the starting sound under a preset
  function restoreSettings(s, opts) {
    opts = opts || {};
    state.mode = s.mode || state.mode;""")
rep("""    state.currentPreset = s.currentPreset || state.currentPreset;
    state.timerTarget = s.timerTarget || 0;
""", """    state.currentPreset = s.currentPreset || state.currentPreset;
    if (!opts.keepTimer) state.timerTarget = s.timerTarget || 0;
""")
rep("""    if (state.playing) debouncedRestart();
  }

  function deleteSaved(name) {""", """    if (state.playing && !opts.quiet) debouncedRestart();
  }

  function loadSaved(name) {
    const s = getSaved()[name];
    if (s) restoreSettings(s);
  }

  function deleteSaved(name) {""")
rep("""  // the controls start on the starting preset: sliders, waveform, spacing, mode, readouts
  applyPreset(state.currentPreset);
""", """  // the starting sound, whole, before anyone touches a control
  FACTORY = JSON.parse(JSON.stringify(serializeState()));
  // the controls start on the starting preset: sliders, waveform, spacing, mode, readouts
  applyPreset(state.currentPreset);
""")
# the File tab: Start over
rep("""        <input type="file" id="importFile" accept="application/json,.json" style="display:none;">
      </div>
    </div>
""", """        <input type="file" id="importFile" accept="application/json,.json" style="display:none;">
      </div>
    </div>
    <div class="settings-section">
      <h3>Start over</h3>
      <div class="row-note" style="padding-top:0;">Puts every setting back the way it starts, with the Ashman1 sound: the layers, texture and tuning, the breath guide, the visuals and the rest. Your saved settings stay.</div>
      <div class="io-row" style="grid-template-columns:1fr;">
        <button id="resetAllBtn" type="button">Reset all settings</button>
      </div>
    </div>
""")
rep("""  $('exportBtn').addEventListener('click', exportStates);
""", """  $('exportBtn').addEventListener('click', exportStates);
  // Reset all settings: saved settings and the safety notice's answer stay; everything else
  // this page keeps on the device goes, and the page starts again (a playing session stops
  // first, so a phone's playback service ends with it)
  $('resetAllBtn').addEventListener('click', () => {
    if (!confirm('Reset all settings?\\n\\nEverything goes back to how it starts, with the Ashman1 sound. Your saved settings stay.')) return;
    const startOver = () => {
      try {
        for (let i = localStorage.length - 1; i >= 0; i--) {
          const k = localStorage.key(i);
          if (k && k.indexOf('phi_resonance_') === 0 && k !== STORAGE_KEY && k !== SAFETY_KEY) localStorage.removeItem(k);
        }
      } catch (e) {}
      location.reload();
    };
    if (state.playing) { stopSession(0.4); setTimeout(startOver, 900); } else startOver();
  });
""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('redesigned', p, len(s), 'chars')
