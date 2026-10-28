"""Build docs/phi_resonance_composer.html from docs/phi_resonance.html.

Usage: python build_composer.py <src.html> <dst.html> [pieces_dir]
The Composer's pieces (composer_*.js/.css/.html) are read from pieces_dir, by default this
script's own folder. Every anchor must match exactly once, or the build stops.
"""
import io, os, sys

src, dst = sys.argv[1], sys.argv[2]
scratch = sys.argv[3] if len(sys.argv) > 3 else os.path.dirname(os.path.abspath(__file__))
s = io.open(src, encoding='utf-8', newline='').read()

def piece(name):
    return io.open(os.path.join(scratch, name), encoding='utf-8').read()

def rep(a, b):
    global s
    n = s.count(a)
    assert n == 1, 'anchor matched %d times: %r' % (n, a[:80])
    s = s.replace(a, b)

def between(start, end, new):
    """Replace from `start` (inclusive) up to `end` (exclusive)."""
    global s
    i = s.index(start)
    j = s.index(end, i)
    assert s.count(start) == 1, start[:60]
    s = s[:i] + new + s[j:]

# ---- head ----
rep('<meta charset="UTF-8">',
    '<meta charset="UTF-8">\n'
    '<!--\n'
    '  φ-Entrainment Composer: the full sound lab plus generative music.\n'
    '  Created: 2026-10-18\n'
    '  Last updated: 2026-10-28\n'
    '  Version: 1.8\n'
    '  Revision history:\n'
    '  - 2026-10-28 v1.8: a preset is a whole sound: every setting, the Composer\'s too,\n'
    '    starts from the starting sound and the preset then sets its own, so Ashman1 always\n'
    '    sounds like Ashman1 (the owner heard it come back different after other changes);\n'
    '    the volume and the session timer stay. The File tab gains Reset all settings,\n'
    '    which keeps saved settings.\n'
    '  - 2026-10-19 v1.7: a frame cap: phones draw at most 30 frames a second, other\n'
    '    screens 60, with fades scaled to the frame time, and on phones the title tag\'s\n'
    '    glitch fires as a one-off instead of a never-ending animation (measured on the\n'
    '    owner\'s Pixel 9, a 120 Hz screen: the page\'s drawing took about three cores, the\n'
    '    phone throttled, and Android counted over 1,000 audio underruns a minute)\n'
    '  - 2026-10-19 v1.6: cheap flashes: the flash colour moves by opacity alone (no\n'
    '    repaint per frame), the HUD text is written only when it changes, and the page\n'
    '    under the full-screen flashes is not drawn (the phone app hitched with visuals)\n'
    '  - 2026-10-19 v1.5: lighter setting changes: the old sound stops on the audio clock\n'
    '    when its fade ends, the crossfade is 0.25 s (was 0.35), and noise is made once\n'
    '    and reused (the phone app got hitchy after a while of changing settings)\n'
    '  - 2026-10-19 v1.4: one reverb runs across setting changes (it was rebuilt beside\n'
    '    the old one on every change, which stuttered in the phone app)\n'
    '  - 2026-10-19 v1.3: the breath guide\'s lane is on the main screen by default; since\n'
    '    v1.2 also: Base, Beat and Mode as buttons with editors, the File tab, the session\n'
    '    card that folds to a bar, and the Ashman1 starting setting\n'
    '  - 2026-10-18 v1.2: the settings tabs sit along the top of the main screen (no\n'
    '    separate settings screen, no full-screen button); the generated part is called\n'
    '    the Composer, not music\n'
    '  - 2026-10-18 v1.1: the Last Ship Sailing interface (a player screen and a tabbed\n'
    '    settings menu, the composer in its own tab); the breath guide pairs with\n'
    '    the flashes, on the main screen or full screen\n'
    '  - 2026-10-18 v1.0: forked from phi_resonance.html; φ Composer (Fibonacci form,\n'
    '    beat-locked tempo, golden bells, binaural pads), WAV download, AI music prompt\n'
    '-->')
rep('<title>φ-Entrainment | Sound Laboratory</title>',
    '<title>φ-Entrainment Composer | Sound Laboratory</title>')
rep('</style>', piece('composer_shell.css') + '</style>')

# ---- html ----
rep('<span class="lt-text">φ-ENTRAINMENT</span>', '<span class="lt-text">φ-COMPOSER</span>')
# the composer gets its own tab, first in the row
rep('      <button class="settings-tab" data-tab="sound" type="button" role="tab" aria-selected="false">Sound</button>',
    '      <button class="settings-tab" data-tab="composer" type="button" role="tab" aria-selected="false">Composer</button>\n'
    '      <button class="settings-tab" data-tab="sound" type="button" role="tab" aria-selected="false">Sound</button>')
rep('  <!-- SOUND -->\n  <div class="settings-panel" data-panel="sound">',
    piece('composer_tab.html') + '  <!-- SOUND -->\n  <div class="settings-panel" data-panel="sound">')
rep('      <div class="bg-status" id="bgStatus" aria-live="polite"></div>\n',
    '      <div class="bg-status" id="bgStatus" aria-live="polite"></div>\n'
    '      <div class="composer-quick">\n'
    '        <button class="quick-btn" id="musicToggleQuick" type="button" aria-pressed="false">♫ COMPOSER: OFF</button>\n'
    '        <button class="quick-btn" id="newPieceQuick" type="button">⟳ NEW PIECE</button>\n'
    '      </div>\n'
    '      <div class="piece-line" id="pieceLineQuick"></div>\n')

# ---- state ----
rep('    layerMute: new Array(9).fill(false),\n',
    '    layerMute: new Array(9).fill(false),\n'
    '    renderOrigin: 0,      // where the music grid starts inside an offline render\n'
    '    bedBus: null,         // the field\'s level under the music\n'
    '    // φ Composer settings (saved with states)\n'
    '    music: {\n'
    '      on: true, seed: 0x75C2C6, style: \'ambient\', scale: \'pent_minor\', bars: 34,   // Ashman1\'s piece\n'
    '      tempo: \'locked\', bpm: 90, density: 50, binPads: true, verb: 40,\n'
    '      levels: { field: 55, pad: 70, bass: 65, lead: 60, bells: 60, drums: 60 }\n'
    '    },\n')

# ---- composer engine, before the sound engine ----
rep('  // ============= SOUND ENGINE =============',
    piece('composer_engine.js') + '  // ============= SOUND ENGINE =============')

# ---- the field graph gets a level stage under the music ----
rep('    const filterInput = state.filter || state.masterGain;\n',
    '    const filterInput = state.filter || state.masterGain;\n'
    '\n'
    '    // Field level: under the composer\'s music the field sits back in the mix\n'
    '    state.bedBus = ctx.createGain();\n'
    '    state.bedBus.gain.value = bedLevel();\n'
    '    state.bedBus.connect(filterInput);\n')
rep('      layerGain.connect(filterInput);', '      layerGain.connect(state.bedBus);')
rep('      dryGain: state.dryGain, fade: state.fade\n',
    '      dryGain: state.dryGain, fade: state.fade, bedBus: state.bedBus\n')
rep('state.convolver = null; state.wetGain = null; state.dryGain = null; state.fade = null;',
    'state.convolver = null; state.wetGain = null; state.dryGain = null; state.fade = null;\n'
    '    state.bedBus = null;')
rep("['masterGain','filter','convolver','wetGain','dryGain','fade']",
    "['masterGain','filter','convolver','wetGain','dryGain','fade','bedBus']")
rep('    state.dryGain = g.dryGain; state.fade = g.fade;',
    '    state.dryGain = g.dryGain; state.fade = g.fade; state.bedBus = g.bedBus;')

# ---- the isochronic pulse lands on the music's beat ----
rep('    pulse.start();', '    pulse.start(gridStartFor(1 / Math.max(0.01, beat)));')

# ---- session start / stop ----
rep('    buildGraph(FADE_IN);\n',
    '    if (state.music.on) composerStart(FADE_IN);\n'
    '    buildGraph(FADE_IN);\n')
rep("    state.playing = false;\n    $('playBtn').textContent = '▶ BEGIN SESSION';",
    "    composerStop(fadeSec);\n"
    "    state.playing = false;\n    $('playBtn').textContent = '▶ BEGIN SESSION';")

# ---- background loop: one full cycle of the piece when the music is on ----
between('  async function renderLoop(v) {', '  function switchToLoop(v, url, musicLoop, key, immediate) {', '''  async function renderLoop(v) {
    // A new piece enters at the next bar line; render it once it is playing
    if (composer.pending) { scheduleLoopRender(400); return; }
    loopState.started = true;
    updateBgStatus();
    const progressive = await offlineSuspendWorks();
    if (v !== loopState.version || !state.playing) return;
    const key = loopKey();
    const c = loopState.cache;
    if (c && c.key === key) {
      loopState.progress = 1;
      updateBgStatus();
      queueSwitch(v, c.url, c.musicLoop, key);
      return;
    }
    const live = state.ctx;
    const piece = (state.music.on && composer.running && composer.piece) ? composer.piece : null;
    // Music loops render at 32 kHz: a third less work and a third smaller,
    // with everything the music holds still well under its 16 kHz ceiling
    const rate = Math.min(live.sampleRate, 32000);
    const sd = composer.sd;
    // With music the loop is exactly one cycle of the piece; without, 48 s of field
    const loopLen = piece ? piece.steps * sd : LOOP_SEC;
    // Render a lead-in long enough for the reverbs and the previous cycle's
    // ringing notes to reach steady state, then keep one period: it loops
    // without a seam
    const lead = Math.max(state.params.revSz + 0.25, piece ? piece.maxSpan * sd + 6.5 : 0);
    const total = loopLen + lead;
    let off;
    try { off = new OfflineAudioContext(2, Math.ceil(rate * total), rate); }
    catch (e) { loopFailed(); return; }
    snapOscillators(off, loopLen);
    const onProgress = (t) => {
      if (v === loopState.version) { loopState.progress = Math.min(1, t / total); updateBgStatus(); }
    };

    const liveGraph = detachGraph();
    state.ctx = off;
    state.rendering = true;
    state.renderOrigin = lead;
    try {
      buildGraph(0, off.destination);
      if (piece) {
        const ch = makeMusicChain(off, off.destination, 1);
        scheduleOffline(off, ch, piece, lead, -Math.ceil(lead / sd), piece.steps, sd, progressive, onProgress);
      }
    }
    finally {
      detachGraph();
      state.ctx = live;
      state.rendering = false;
      restoreGraph(liveGraph);
    }
    // the music's windowed scheduler reports progress itself
    if (progressive && !piece) watchProgress(off, v, total);

    let rendered;
    try { rendered = await off.startRendering(); }
    catch (e) { if (v === loopState.version) loopFailed(); return; }
    if (v !== loopState.version || !state.playing) return;
    const a = Math.round(lead * rate), n = Math.round(loopLen * rate);
    const wav = await encodeWavAsync([
      rendered.getChannelData(0).subarray(a, a + n),
      rendered.getChannelData(1).subarray(a, a + n)
    ], rate);
    if (v !== loopState.version || !state.playing) return;
    const url = URL.createObjectURL(wav);
    loopState.progress = 1;
    updateBgStatus();
    queueSwitch(v, url, !!piece, key);
  }

''')

rep('''    el.src = url;
    const played = el.play();''', '''    el.src = url;
    // A music loop starts where the live music is in the cycle, so the
    // handover is a continuation, not a restart
    const pos = musicLoop ? composerPos() : null;
    if (pos != null) { try { el.currentTime = pos; } catch (e) {} }
    const played = el.play();''')
rep('''  function adoptLoop(el, url, musicLoop, key, fadeSec, crossfade) {
    loopState.active = true;
''', '''  function adoptLoop(el, url, musicLoop, key, fadeSec, crossfade) {
    if (musicLoop) {
      const p2 = composerPos();
      if (p2 != null && Math.abs(el.currentTime - p2) > 0.06) { try { el.currentTime = p2; } catch (e) {} }
      composerRetireChain(fadeSec > 0 ? fadeSec : 0.02);
    }
    loopState.musicLoop = !!musicLoop;
    loopState.active = true;
''')

# The loop depends on the music too; while a new piece is waiting for its
# bar line, nothing kept can match
rep('    return JSON.stringify([state.mode, state.layerCount, state.layerMute, state.params]);',
    "    return JSON.stringify([state.mode, state.layerCount, state.layerMute, state.params, state.music, composer.pending ? 'pending' : '']);")

rep('''    } else {
      toSilence();
    }
  }''', '''    } else {
      toSilence();
    }
    if (loopState.musicLoop) composerResumeFromLoop(pos, fadeSec);
    loopState.musicLoop = false;
  }''')

# ---- lock-screen title ----
rep('''          title: state.mode.charAt(0).toUpperCase() + state.mode.slice(1) + ' · ' +
                 Math.round(state.params.base) + ' Hz',
          artist: 'φ-Entrainment',''', '''          title: state.music.on
            ? (STYLES[state.music.style] || STYLES.ambient).label + ' · ' + composerTempo().bpm.toFixed(1) + ' BPM'
            : state.mode.charAt(0).toUpperCase() + state.mode.slice(1) + ' · ' + Math.round(state.params.base) + ' Hz',
          artist: state.music.on ? 'φ-Entrainment Composer' : 'φ-Entrainment',''')

# ---- master volume moves the music too ----
rep('    if (state.masterGain) glide(state.masterGain.gain, v/100);',
    '    if (state.masterGain) glide(state.masterGain.gain, v/100);\n'
    '    if (composer.chain) glide(composer.chain.master.gain, v / 100 * MUSIC_TRIM);')

# ---- saved states carry the music ----
rep('      params: Object.assign({}, state.params),\n',
    '      params: Object.assign({}, state.params),\n'
    '      music: JSON.parse(JSON.stringify(state.music)),\n')
rep('    if (s.params) state.params = Object.assign({}, state.params, s.params);\n',
    '    if (s.params) state.params = Object.assign({}, state.params, s.params);\n'
    '    if (s.music && JSON.stringify(s.music) !== JSON.stringify(state.music)) loadMusicSettings(s.music);\n')

# ---- composer UI, before click-to-edit ----
rep('  // ============= CLICK-TO-EDIT SLIDER VALUES =============',
    piece('composer_ui.js') + '  // ============= CLICK-TO-EDIT SLIDER VALUES =============')

io.open(dst, 'w', encoding='utf-8', newline='').write(s)
print('built', dst, len(s), 'chars')
