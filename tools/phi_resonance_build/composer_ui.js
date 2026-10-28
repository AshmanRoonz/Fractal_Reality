  // ============= COMPOSER UI =============
  let _uiKey = '', _lastBarShown = -1;
  function seedHex(s) { return ((s >>> 0) & 0xFFFFFF).toString(16).toUpperCase().padStart(6, '0'); }
  function newSeed() { return 1 + Math.floor(Math.random() * 0xFFFFFE); }
  function fmtTime(sec) {
    const s = Math.round(sec);
    return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0');
  }
  const COMPOSER_NOTES = ['C', 'C♯', 'D', 'E♭', 'E', 'F', 'F♯', 'G', 'A♭', 'A', 'B♭', 'B'];
  function noteName(f) {
    const midi = 69 + 12 * Math.log2(f / 440);
    const r = Math.round(midi), cents = Math.round((midi - r) * 100);
    return COMPOSER_NOTES[modi(r, 12)] + (Math.floor(r / 12) - 1) +
      (cents ? ' ' + (cents > 0 ? '+' : '−') + Math.abs(cents) + '¢' : '');
  }

  function updateMusicButtons() {
    ['musicToggle', 'musicToggleQuick'].forEach(id => {
      const b = $(id);
      if (!b) return;
      b.textContent = state.music.on ? '♫ COMPOSER: ON' : '♫ COMPOSER: OFF';
      b.classList.toggle('on', state.music.on);
      b.setAttribute('aria-pressed', String(state.music.on));
    });
  }

  // Music settings that change the score: recompose (enters at the next bar)
  function onMusicSettingChanged() {
    composerRecompose();
    renderComposerForm();
    renderPieceInfo();
    if (state.playing && state.music.on) {
      if (loopState.active) debouncedRestart(); else maybePrepare();
    }
  }

  // Mix changes glide live; a rendered loop has the old mix baked in, so
  // hand back to the live synth (or re-render behind it)
  function onMusicMixChanged() {
    const ch = composer.chain;
    if (ch) {
      Object.keys(ch.buses).forEach(k => glide(ch.buses[k].gain, levelGain(state.music.levels[k])));
      glide(ch.wet.gain, state.music.verb / 100);
    }
    if (state.bedBus) glide(state.bedBus.gain, bedLevel());
    if (state.playing && state.music.on) {
      if (loopState.active) debouncedRestart(); else maybePrepare();
    }
  }

  function setMusicOn(on) {
    state.music.on = !!on;
    updateMusicButtons();
    if (state.playing) {
      if (state.music.on) composerStart(2); else composerStop(1.5);
      // the field level only applies under music, and the loop must re-render
      debouncedRestart();
    }
    renderPieceInfo();
    updateMediaSession();
  }

  function renderStyleTabs() {
    const box = $('styleTabs');
    box.innerHTML = '';
    Object.keys(STYLES).forEach(id => {
      const b = document.createElement('button');
      // its own class: the field's mode code resets every .mode-tab
      b.className = 'style-tab' + (state.music.style === id ? ' active' : '');
      b.type = 'button';
      b.textContent = STYLES[id].label;
      b.addEventListener('click', () => {
        state.music.style = id;
        renderStyleTabs();
        onMusicSettingChanged();
      });
      box.appendChild(b);
    });
  }

  function renderComposerForm() {
    const piece = composer.pending || composer.piece || composerEnsurePiece();
    const bar = $('formBar');
    if (!bar) return;
    bar.innerHTML = '';
    piece.sections.forEach(s => {
      const d = document.createElement('div');
      d.className = 'form-seg';
      d.style.flex = String(s.len);
      d.style.background = 'rgba(255, 170, 0, ' + (0.1 + 0.55 * s.energy).toFixed(2) + ')';
      d.style.color = s.energy >= 0.6 ? '#111' : 'var(--amber-hi)';
      d.textContent = s.label;
      d.title = s.label + ': ' + s.len + ' bars';
      bar.appendChild(d);
    });
    const peak = piece.sections.find(s => s.id === 'C');
    const gm = document.createElement('div');
    gm.className = 'golden-mark';
    gm.style.left = (peak.start / piece.bars * 100).toFixed(3) + '%';
    gm.title = 'Golden section: bar ' + (peak.start + 1) + ' of ' + piece.bars;
    bar.appendChild(gm);
    const ph = document.createElement('div');
    ph.className = 'form-playhead';
    ph.id = 'formPlayhead';
    bar.appendChild(ph);
    _lastBarShown = -1;
  }

  function renderPieceInfo() {
    const m = state.music;
    const piece = composer.pending || composer.piece || composerEnsurePiece();
    const tempo = composerTempo(), T = tonicRef();
    const unit = tempo.k == null
      ? 'free tempo'
      : '1 ' + beatUnitName(tempo.k) + ' = 1 beat (' + (+state.params.beat).toFixed(3) + ' Hz)';
    const C = piece.steps * stepDur();
    $('pieceInfo').innerHTML =
      'Tonic <b>' + T.toFixed(1) + ' Hz</b> (' + noteName(T) + ') · <b>' + tempo.bpm.toFixed(1) + ' BPM</b>, ' + unit +
      ' · ' + piece.bars + ' bars, ' + fmtTime(C) + ' per cycle · golden peak at bar ' +
      (piece.sections.find(s => s.id === 'C').start + 1) + ' · seed <b>' + seedHex(m.seed) + '</b>';
    $('pieceLineQuick').textContent = m.on
      ? (STYLES[m.style] || STYLES.ambient).label + ' · ' + tempo.bpm.toFixed(1) + ' BPM · tonic ' + T.toFixed(1) + ' Hz'
      : 'Composer off: the field plays alone';
    if (document.activeElement !== $('seedInput')) $('seedInput').value = seedHex(m.seed);
    $('bpmRow').style.display = m.tempo === 'free' ? '' : 'none';
  }

  // Playhead, bar and chord readout; cheap enough to run every frame
  function composerUiFrame(now) {
    requestAnimationFrame(composerUiFrame);
    // nothing to show under the full-screen flashes; otherwise the frame cap (see frameDue)
    if (coveredByFlash() || !frameDue('composerUi', now)) return;
    const m = state.music;
    const key = [state.params.base, state.params.beat, m.tempo, m.bpm, m.seed, m.bars, m.style, m.scale, m.on].join('|');
    if (key !== _uiKey) { _uiKey = key; renderPieceInfo(); }
    const ph = $('formPlayhead');
    if (!ph) return;
    const piece = composer.piece;
    let pos = null;
    if (piece && state.playing && m.on) {
      if (loopState.active && loopState.musicLoop && loopState.el) pos = loopState.el.currentTime;
      else pos = composerPos();
    }
    if (pos == null || !piece) {
      if (ph.style.display !== 'none') {
        ph.style.display = 'none';
        $('formPos').textContent = m.on ? 'Press begin session to hear the piece' : 'Composer is off';
        $('formChord').textContent = '';
        _lastBarShown = -1;
      }
      return;
    }
    const C = piece.steps * composer.sd;
    ph.style.display = 'block';
    ph.style.left = (Math.min(1, pos / C) * 100).toFixed(3) + '%';
    const barIdx = Math.floor(pos / (16 * composer.sd)) % piece.bars;
    if (barIdx !== _lastBarShown) {
      _lastBarShown = barIdx;
      const sec = piece.sections.find(s => barIdx >= s.start && barIdx < s.start + s.len);
      $('formPos').textContent = 'Bar ' + (barIdx + 1) + ' / ' + piece.bars + (sec ? ' · ' + sec.label : '');
      const T = tonicRef();
      $('formChord').textContent = 'Chord ' + piece.chords[barIdx]
        .map(d => (T * piece.R[modi(d, piece.R.length)]).toFixed(0)).join(' · ') + ' Hz';
    }
  }

  function bindMusicSlider(id, fmt, apply) {
    const el = $(id);
    el.addEventListener('input', () => {
      const v = parseFloat(el.value);
      $(id + 'Val').textContent = fmt(v);
      apply(v);
    });
  }

  function pushMusicUI() {
    const m = state.music;
    updateMusicButtons();
    renderStyleTabs();
    $('mScale').value = m.scale;
    $('mBars').value = String(m.bars);
    $('mTempo').value = m.tempo;
    $('mBpm').value = m.bpm; $('mBpmVal').textContent = Math.round(m.bpm) + ' BPM';
    $('mDensity').value = m.density; $('mDensityVal').textContent = Math.round(m.density) + '%';
    $('binPads').checked = !!m.binPads;
    [['mField', 'field'], ['mPad', 'pad'], ['mBass', 'bass'], ['mLead', 'lead'], ['mBells', 'bells'], ['mDrums', 'drums']]
      .forEach(([id, k]) => { $(id).value = m.levels[k]; $(id + 'Val').textContent = Math.round(m.levels[k]) + '%'; });
    $('mVerb').value = m.verb; $('mVerbVal').textContent = Math.round(m.verb) + '%';
    renderComposerForm();
    renderPieceInfo();
  }

  // Saved states carry the music settings too (older states simply lack them)
  function loadMusicSettings(sm) {
    const wasOn = state.music.on;
    state.music = Object.assign({}, MUSIC_DEFAULTS, sm, {
      levels: Object.assign({}, MUSIC_DEFAULTS.levels, (sm && sm.levels) || {})
    });
    composerRecompose();
    pushMusicUI();
    if (state.playing && wasOn !== state.music.on) {
      if (state.music.on) composerStart(2); else composerStop(1.5);
    }
    onMusicMixChanged();
  }

  // Populate selects
  Object.keys(SCALES).forEach(id => {
    const o = document.createElement('option');
    o.value = id;
    o.textContent = SCALES[id].label;
    $('mScale').appendChild(o);
  });

  $('musicToggle').addEventListener('click', () => setMusicOn(!state.music.on));
  $('musicToggleQuick').addEventListener('click', () => setMusicOn(!state.music.on));
  const newPiece = () => {
    state.music.seed = newSeed();
    if (!state.music.on) setMusicOn(true);
    onMusicSettingChanged();
  };
  $('newPiece').addEventListener('click', newPiece);
  $('newPieceQuick').addEventListener('click', newPiece);

  $('mScale').addEventListener('change', e => { state.music.scale = e.target.value; onMusicSettingChanged(); });
  $('mBars').addEventListener('change', e => { state.music.bars = parseInt(e.target.value, 10); onMusicSettingChanged(); });
  $('mTempo').addEventListener('change', e => {
    state.music.tempo = e.target.value;
    renderPieceInfo();
    // the isochronic pulse re-aligns to the grid in a rebuilt field
    if (state.playing) debouncedRestart();
  });
  bindMusicSlider('mBpm', v => Math.round(v) + ' BPM', v => {
    state.music.bpm = v;
    if (state.playing && state.music.on) { if (loopState.active) debouncedRestart(); else maybePrepare(); }
  });
  let _densityTimer = null;
  bindMusicSlider('mDensity', v => Math.round(v) + '%', v => {
    state.music.density = v;
    clearTimeout(_densityTimer);
    _densityTimer = setTimeout(onMusicSettingChanged, 250);
  });
  $('binPads').addEventListener('change', e => {
    state.music.binPads = e.target.checked;
    if (state.playing && state.music.on) { if (loopState.active) debouncedRestart(); else maybePrepare(); }
  });
  $('seedInput').addEventListener('change', e => {
    const v = parseInt(String(e.target.value).trim(), 16);
    if (isFinite(v) && v > 0) {
      state.music.seed = v & 0xFFFFFF;
      onMusicSettingChanged();
    } else {
      e.target.value = seedHex(state.music.seed);
    }
  });
  [['mField', 'field'], ['mPad', 'pad'], ['mBass', 'bass'], ['mLead', 'lead'], ['mBells', 'bells'], ['mDrums', 'drums']]
    .forEach(([id, k]) => bindMusicSlider(id, v => Math.round(v) + '%', v => { state.music.levels[k] = v; onMusicMixChanged(); }));
  bindMusicSlider('mVerb', v => Math.round(v) + '%', v => { state.music.verb = v; onMusicMixChanged(); });

  // ----- download audio (.wav) -----
  // Renders the current sound (the field, plus the music when it is on)
  // offline, faster than real time, to a 44.1 kHz 16-bit stereo WAV.
  let _exportBusy = false;
  function setExportStatus(t) { $('exportStatus').textContent = t; }
  function downloadWav(blob, name) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 4000);
  }

  async function exportAudio() {
    if (_exportBusy) return;
    if (!window.OfflineAudioContext) { setExportStatus('This browser cannot render audio files.'); return; }
    _exportBusy = true;
    const btn = $('exportAudioBtn');
    btn.disabled = true;
    const finish = () => { _exportBusy = false; btn.disabled = false; };
    const piece = state.music.on ? composePiece(state.music) : null;
    const sd = stepDur();
    const rate = 44100, TAIL = 6, START = 0.05;
    const sel = $('exportLen').value;
    let total, musicSteps = 0;
    if (sel === 'cycle') {
      if (piece) { musicSteps = piece.steps; total = START + musicSteps * sd + TAIL; }
      else total = 60;
    } else {
      total = Number(sel);
      if (piece) musicSteps = Math.max(16, Math.floor((total - TAIL - START) / sd / 16) * 16);
    }
    const fadeOutAt = piece ? START + musicSteps * sd : total - TAIL;
    const progressive = await offlineSuspendWorks();
    const progress = (t) => setExportStatus('Rendering… ' + Math.round(t / total * 100) + '%');
    let off;
    try { off = new OfflineAudioContext(2, Math.ceil(rate * total), rate); }
    catch (e) { setExportStatus('Could not start rendering: ' + e.message); finish(); return; }
    setExportStatus('Rendering ' + fmtTime(total) + ' of audio…');

    const live = state.ctx;
    const liveGraph = detachGraph();
    state.ctx = off;
    state.rendering = true;
    state.renderOrigin = START;
    try {
      buildGraph(2.5, off.destination);
      const g = state.fade.gain;
      g.setValueAtTime(1, fadeOutAt);
      g.linearRampToValueAtTime(0, total - 0.3);
      if (piece) {
        const ch = makeMusicChain(off, off.destination, 1);
        scheduleOffline(off, ch, piece, START, 0, musicSteps, sd, progressive, progress);
        ch.fade.gain.setValueAtTime(1, fadeOutAt);
        ch.fade.gain.linearRampToValueAtTime(0, total - 0.3);
      }
    } catch (e) {
      setExportStatus('Rendering failed: ' + e.message);
    } finally {
      detachGraph();
      state.ctx = live;
      state.rendering = false;
      restoreGraph(liveGraph);
    }

    // Progress for a field-only render (with music, the scheduler reports it)
    if (!piece && progressive) {
      for (let t = 10; t < total - 1; t += 10) {
        off.suspend(t).then(() => { progress(t); off.resume(); });
      }
    }

    let buf;
    try { buf = await off.startRendering(); }
    catch (e) { setExportStatus('Rendering failed: ' + e.message); finish(); return; }
    setExportStatus('Encoding…');
    const blob = await encodeWavAsync([buf.getChannelData(0), buf.getChannelData(1)], rate);
    const name = 'phi-' + (piece
      ? 'composer-' + piece.style + '-' + seedHex(piece.seed)
      : 'field-' + state.mode) + '-' + Math.round(state.params.base) + 'hz.wav';
    downloadWav(blob, name);
    setExportStatus('Saved ' + name + ' (' + fmtTime(total) + ', ' + (blob.size / 1048576).toFixed(1) + ' MB)');
    finish();
  }
  $('exportAudioBtn').addEventListener('click', exportAudio);

  // ----- AI music prompt (Suno, Udio, Stable Audio, ElevenLabs Music) -----
  const SPACING_WORDS = {
    phi: 'golden-ratio intervals, each 1.618 times the last', octave: 'octaves', fifth: 'perfect fifths',
    fourth: 'perfect fourths', major3: 'major thirds', minor3: 'minor thirds', semitone: 'semitones',
    harmonic: 'the harmonic series', subharmonic: 'the subharmonic series', prime: 'prime-number ratios'
  };
  const WAVE_WORDS = {
    sine: 'pure sine', triangle: 'soft triangle', square: 'hollow square', sawtooth: 'bright sawtooth',
    fm: 'FM bell', am: 'pulsing AM', organ: 'organ-like', vocal: 'vocal formant', bowed: 'bowed'
  };
  function fieldFreqs() {
    const p = state.params, N = state.layerCount, half = Math.floor(N / 2), out = [];
    for (let i = 0; i < N; i++) {
      if (state.layerMute[i]) continue;
      out.push(Math.max(20, Math.min(12000, p.base * spacingRatio(p.spacing, i - half))));
    }
    return out.sort((a, b) => a - b);
  }
  function modeWords(beat) {
    switch (state.mode) {
      case 'binaural':   return 'binaural beat at ' + beat + ' Hz (each tone slightly higher in the right ear than the left)';
      case 'isochronic': return 'isochronic pulses at ' + beat + ' Hz (the tones switch on and off rhythmically)';
      case 'monaural':   return 'monaural beat at ' + beat + ' Hz (pairs of close tones beating together)';
      case 'cascade':    return 'cascading binaural beats from ' + beat + ' Hz, each layer slower by the golden ratio';
      case 'harmonic':   return 'a stack of harmonic overtones';
      case 'noise':      return 'bands of filtered noise';
      case 'chord':      return 'a sustained chord';
      default:           return 'a steady drone';
    }
  }

  function aiPromptTexts() {
    const p = state.params, m = state.music;
    const beat = +(+p.beat).toFixed(3);
    const freqs = fieldFreqs().map(f => Math.round(f));
    const wave = WAVE_WORDS[p.wave] || 'pure sine';
    const spacing = SPACING_WORDS[p.spacing] || 'golden-ratio intervals';
    const tempo = composerTempo();
    const bpm = Math.round(tempo.bpm * 10) / 10;
    const swell = p.lfoDepth > 0
      ? (p.lfoRate <= 1 ? 'gentle ' + Math.round(1 / p.lfoRate) + '-second breathing swell' : 'tremolo at ' + (+p.lfoRate).toFixed(2) + ' Hz')
      : null;
    const fieldLine = freqs.length + ' ' + wave + ' tones (' + freqs.join(', ') + ' Hz) stacked in ' + spacing;

    if (!m.on) {
      const style = [
        'instrumental ambient drone', 'meditation', Math.round(p.base) + ' Hz tuning',
        tempo.k === 0 ? bpm + ' BPM pulse' : null,
        fieldLine,
        p.spacing === 'phi' ? 'glassy, inharmonic, otherworldly shimmer' : null,
        modeWords(beat), swell,
        p.noiseType !== 'none' ? p.noiseType + ' noise bed' : null,
        p.rev >= 40 ? 'deep reverb' : 'soft room reverb',
        'wide stereo', 'still and hypnotic', 'no drums', 'no melody', 'no vocals', 'headphones'
      ].filter(Boolean).join(', ');
      const structure = [
        '[Instrumental]',
        '[Intro: a single ' + Math.round(p.base) + ' Hz tone fades in]',
        '[Build: the other tones enter one by one, low to high]',
        '[Main: the full shimmering chord, pulsing gently between the ears]',
        '[Breakdown: the highest tones fade, the low drone breathes]',
        '[Outro: everything dissolves into reverb]'
      ].join('\n');
      const description =
        'Create an instrumental meditation drone built the way the φ-Entrainment app builds sound. ' +
        'Tune everything to ' + Math.round(p.base) + ' Hz. Play ' + fieldLine + '. ' +
        (p.spacing === 'phi' ? 'Because the intervals are golden ratios, the chord is glassy and otherworldly rather than major or minor. ' : '') +
        'The sound carries a ' + modeWords(beat) + (tempo.k === 0 ? ', which pulses about ' + bpm + ' times per minute' : '') + '. ' +
        (swell ? 'The whole chord has a ' + swell + '. ' : '') +
        'Add ' + (p.rev >= 40 ? 'a deep' : 'a soft') + ' reverb and wide stereo. No drums, no melody, no vocals: ' +
        'a still, hypnotic, shimmering drone that fades in at the start and dissolves into reverb at the end.';
      return { style, structure, description };
    }

    const st = STYLES[m.style] || STYLES.ambient, sc = SCALES[m.scale] || SCALES.pent_minor;
    const piece = composer.pending || composer.piece || composerEnsurePiece();
    const T = tonicRef();
    const binPads = m.binPads && beat > 0 && beat <= 12;
    const style = [
      'instrumental', st.words, bpm + ' BPM',
      'tuned to ' + Math.round(p.base) + ' Hz (home note ' + T.toFixed(1) + ' Hz)',
      sc.words,
      tempo.k != null ? 'a ' + beat + ' Hz binaural beat locked to the tempo (one beat per ' + beatUnitName(tempo.k) + ')' : null,
      binPads ? 'chords that pulse gently between the ears' : null,
      'a soft drone of ' + wave + ' tones in ' + (p.spacing === 'phi' ? 'golden-ratio intervals' : spacing) + ' underneath',
      'song form in Fibonacci-length sections with the climax at the golden section',
      'wide stereo', 'lush reverb', 'calm and hypnotic', 'no vocals', 'headphones'
    ].filter(Boolean).join(', ');

    const partsIn = (id) => {
      const parts = ['pads'];
      if (st.bassIn.includes(id)) parts.push('bass');
      if (st.drumsIn.includes(id)) parts.push(st.drums === 'heart' ? 'heartbeat kick' : 'drums');
      if (st.bellsIn.includes(id)) parts.push('golden bells');
      if (st.leadIn.includes(id)) parts.push('melody');
      return parts.join(' + ');
    };
    const structure = ['[Instrumental]'].concat(piece.sections.map(s =>
      '[' + s.label + ': ' + partsIn(s.id) + ', ' + s.len + ' bars' + (s.id === 'C' ? ', the climax' : '') + ']'
    )).join('\n');

    const peak = piece.sections.find(s => s.id === 'C');
    const description =
      'Create an instrumental ' + st.label.toLowerCase() + ' track built the way the φ-Entrainment Composer builds music. ' +
      'Everything is tuned to a ' + Math.round(p.base) + ' Hz reference and the home note is ' + T.toFixed(1) + ' Hz. ' +
      'The tempo is ' + bpm + ' BPM' +
      (tempo.k != null ? ', chosen so that one ' + beatUnitName(tempo.k) + ' lasts exactly one cycle of a ' + beat + ' Hz brainwave beat' : '') + '. ' +
      'Underneath plays a quiet drone of ' + fieldLine + ', carrying a ' + modeWords(beat) + '. ' +
      'On top: ' + st.words + '. ' +
      'Melody and chords use a ' + sc.words + '. ' +
      (binPads ? 'The chords themselves are binaural: each right-ear note sits ' + beat + ' Hz above the left, so the harmony pulses between the ears. ' : '') +
      'The piece is ' + piece.bars + ' bars in Fibonacci-sized sections (' + piece.sections.map(s => s.len).join(' + ') + '), ' +
      'builds gradually, peaks at the golden section (bar ' + (peak.start + 1) + ', 61.8% of the way through), ' +
      'then breathes back down to where it began so it can loop. Calm, spacious and hypnotic, wide stereo, no vocals.';
    return { style, structure, description };
  }

  let _aiTexts = null;
  function renderAiPrompt() {
    _aiTexts = aiPromptTexts();
    $('aiPrompt').value =
      'STYLE (paste into Suno\'s "Style of Music"; ' + _aiTexts.style.length + ' characters)\n' + _aiTexts.style +
      '\n\nSTRUCTURE (paste into the lyrics box, with Instrumental on)\n' + _aiTexts.structure +
      '\n\nDESCRIPTION (for generators that take a full sentence)\n' + _aiTexts.description;
  }
  async function copyText(txt, btn) {
    let ok = false;
    try { await navigator.clipboard.writeText(txt); ok = true; }
    catch (e) {
      const ta = document.createElement('textarea');
      ta.value = txt;
      ta.setAttribute('readonly', '');
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      try { ok = document.execCommand('copy'); } catch (e2) {}
      document.body.removeChild(ta);
    }
    const old = btn.textContent;
    btn.textContent = ok ? 'Copied ✓' : 'Copy failed';
    setTimeout(() => { btn.textContent = old; }, 1400);
  }
  $('aiDetails').addEventListener('toggle', () => { if ($('aiDetails').open) renderAiPrompt(); });
  $('aiRefreshBtn').addEventListener('click', renderAiPrompt);
  $('copyStyleBtn').addEventListener('click', e => { renderAiPrompt(); copyText(_aiTexts.style, e.currentTarget); });
  $('copyStructBtn').addEventListener('click', e => { renderAiPrompt(); copyText(_aiTexts.structure, e.currentTarget); });
  $('copyDescBtn').addEventListener('click', e => { renderAiPrompt(); copyText(_aiTexts.description, e.currentTarget); });

  pushMusicUI();
  requestAnimationFrame(composerUiFrame);

