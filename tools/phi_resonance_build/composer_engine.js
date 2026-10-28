  // ============= φ COMPOSER: generative music from the field =============
  // Music grown from the field's own numbers.
  //   tonic  = the base frequency folded into one octave (196 to 392 Hz)
  //   tempo  = the beat frequency shifted by octaves into 64-128 BPM, so one
  //            grid unit of the music IS the entrainment beat (a 1.618 Hz
  //            beat is 97.1 BPM: one beat per quarter note)
  //   form   = Fibonacci sections, F(k) + 3·F(k+1) + F(k) bars (34 bars is
  //            5 + 8 + 8 + 8 + 5); the Peak starts at bar F(k+3), the golden
  //            section of the whole, then the piece breathes back to bar 0
  //   rhythm = Euclidean patterns, with hats and bells on the Fibonacci word
  //            (quasi-periodic: structured, never exactly repeating)
  //   bells  = FM with a golden-ratio modulator (inharmonic and glassy)
  //   pads   = with binaural pads on, each right-ear voice sits one beat
  //            higher, so every chord carries the entrainment beat itself
  // The voices are adapted from Last Ship Sailing's band (lss.js
  // _musicSynthDrum / Bass / Pad / Lead), softened for listening.
  // A piece is a deterministic cycle (seed + settings), so it can loop
  // seamlessly, render for background playback, and export to WAV.

  const MUSIC_DEFAULTS = JSON.parse(JSON.stringify(state.music));
  const MUSIC_TRIM = 1.2;     // music master vs the field (measured: matches the field-only loudness at the peak)
  const IS_MOBILE = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent) ||
    (navigator.maxTouchPoints > 1 && /Macintosh/.test(navigator.userAgent));

  // The field's own pitch classes: φ^k for k = -3..2 folded into one octave.
  // With the default six φ-spaced layers, every layer of the field is a note
  // of this scale, so the music plays the field's own notes.
  const PHI_CHAIN = [-3, -2, -1, 0, 1, 2].map(k => {
    let r = Math.pow(PHI, k);
    while (r >= 2) r /= 2;
    while (r < 1) r *= 2;
    return r;
  }).sort((a, b) => a - b);

  const SCALES = {
    pent_minor: { label: 'Pentatonic minor (just)', words: 'just-intonation minor pentatonic', ratios: [1, 6/5, 4/3, 3/2, 9/5] },
    pent_major: { label: 'Pentatonic major (just)', words: 'just-intonation major pentatonic', ratios: [1, 9/8, 5/4, 3/2, 5/3] },
    dorian:     { label: 'Dorian (just)', words: 'just-intonation dorian mode', ratios: [1, 9/8, 6/5, 4/3, 3/2, 5/3, 9/5] },
    aeolian:    { label: 'Natural minor (just)', words: 'just-intonation natural minor', ratios: [1, 9/8, 6/5, 4/3, 3/2, 8/5, 9/5] },
    lydian:     { label: 'Lydian (just, bright)', words: 'bright just-intonation lydian mode', ratios: [1, 9/8, 5/4, 45/32, 3/2, 5/3, 15/8] },
    harmonic:   { label: 'Harmonic series (8 to 15)', words: 'harmonic-series scale (partials 8 to 15, natural 7th and 11th)', ratios: [1, 9/8, 5/4, 11/8, 3/2, 13/8, 7/4, 15/8] },
    phi:        { label: 'φ-chain (the field’s own notes)', words: 'golden-ratio scale of stacked golden ratios folded into one octave (xenharmonic, otherworldly)', ratios: PHI_CHAIN }
  };

  // Each style: which parts play in which sections, and how they play.
  // Section ids: intro, A (Rise), B (Build), C (Peak), outro (Return).
  const STYLES = {
    ambient: {
      label: 'Ambient Field',
      words: 'ambient meditation, evolving warm pads, glassy golden-ratio FM bells, soft sine sub bass, a slow sparse melody at the peak, no drums',
      chordBars: 2, sevenths: true,
      padWave: 'triangle', padAttack: 1.8, padRelease: 2.8,
      bassWave: 'sine', bass: 'held', bassIn: ['A', 'B', 'C', 'outro'],
      drums: 'none', drumsIn: [],
      bells: 'sparse', bellsIn: ['B', 'C', 'outro'],
      lead: 'slow', leadIn: ['C'], leadAttack: 0.25,
      progressions: [['T', 'Sub', 'S', 'T'], ['T', 'S', 'Sub', 'D'], ['T', 'Med', 'Sub', 'T']]
    },
    pulse: {
      label: 'Heartbeat Pulse',
      words: 'slow heartbeat kick (lub-dub), soft shaker, warm pads, round bass on the one, gentle bells',
      chordBars: 2, sevenths: false,
      padWave: 'triangle', padAttack: 1.2, padRelease: 2.2,
      bassWave: 'triangle', bass: 'bar', bassIn: ['A', 'B', 'C', 'outro'],
      drums: 'heart', drumsIn: ['intro', 'A', 'B', 'C', 'outro'],
      bells: 'sparse', bellsIn: ['A', 'C'],
      lead: 'slow', leadIn: ['C'], leadAttack: 0.2,
      progressions: [['T', 'Sub', 'T', 'S'], ['T', 'Med', 'S', 'T']]
    },
    downtempo: {
      label: 'Downtempo',
      words: 'downtempo chill groove, laid-back kick and snare, Fibonacci-rhythm hi-hats, syncopated bass, warm pads, singing triangle-wave lead melody, golden bells',
      chordBars: 1, sevenths: true,
      padWave: 'triangle', padAttack: 0.6, padRelease: 1.4,
      bassWave: 'triangle', bass: 'synco', bassIn: ['A', 'B', 'C', 'outro'],
      drums: 'down', drumsIn: ['A', 'B', 'C', 'outro'],
      bells: 'arp', bellsIn: ['B', 'outro'],
      lead: 'motif', leadIn: ['A', 'C'], leadAttack: 0.03,
      progressions: [['T', 'Sub', 'S', 'D'], ['T', 'Med', 'Sub', 'S'], ['T', 'S', 'T', 'D']]
    },
    drive: {
      label: 'Cosmic Drive',
      words: 'cosmic synthwave drive, driving eighth-note bass, punchy kick and snare, sixteenth-note hats, sawtooth pads, bright triangle lead riffs',
      chordBars: 2, sevenths: false,
      padWave: 'sawtooth', padAttack: 0.4, padRelease: 1.0,
      bassWave: 'sawtooth', bass: 'eighths', bassIn: ['A', 'B', 'C', 'outro'], bassDrive: true,
      drums: 'drive', drumsIn: ['intro', 'A', 'B', 'C', 'outro'],
      bells: 'arp', bellsIn: ['B'],
      lead: 'riff', leadIn: ['A', 'C'], leadAttack: 0.015,
      progressions: [['T', 'Sub', 'S', 'T'], ['T', 'D', 'Sub', 'S']]
    },
    bells: {
      label: 'Golden Bells',
      words: 'golden-ratio FM bell arpeggios on a Fibonacci rhythm, soft pads, deep held bass, music-box shimmer, no drums',
      chordBars: 2, sevenths: false,
      padWave: 'sine', padAttack: 1.4, padRelease: 2.4,
      bassWave: 'sine', bass: 'held', bassIn: ['A', 'B', 'C', 'outro'],
      drums: 'none', drumsIn: [],
      bells: 'fib', bellsIn: ['intro', 'A', 'B', 'C', 'outro'],
      lead: 'none', leadIn: [],
      progressions: [['T', 'Sub', 'S', 'T'], ['T', 'Med', 'Sub', 'D']]
    }
  };

  const SECTION_DEFS = [
    { id: 'intro', label: 'Intro',  energy: 0.25 },
    { id: 'A',     label: 'Rise',   energy: 0.5 },
    { id: 'B',     label: 'Build',  energy: 0.72 },
    { id: 'C',     label: 'Peak',   energy: 1.0 },
    { id: 'outro', label: 'Return', energy: 0.35 }
  ];
  // bars = F(k+4) = F(k) + 3·F(k+1) + F(k); the Peak starts at F(k+3)
  const FORM_SIZES = { 13: [2, 3], 21: [3, 5], 34: [5, 8], 55: [8, 13] };

  // LSS riff tables ('driving' rhythm; riff_minor, pentatonic_a, zigzag and
  // rising contours), contours in 7-note degrees, rescaled to each scale
  const RIFF_RHYTHM = [2,0,1,0, 1,0,2,0, 0,1,1,0, 2,0,1,1];
  const RIFF_CONTOURS = [[0,0,2,4,7,4,2,0], [0,2,4,7,9,7,4,2], [0,4,2,5,4,7,5,9], [0,2,4,5,7,9,11,12]];

  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function hashStr(s) {
    let h = 2166136261;
    for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
    return h >>> 0;
  }
  function modi(a, n) { return ((a % n) + n) % n; }

  // Euclidean rhythm: k pulses spread as evenly as possible over n steps,
  // first pulse on step 0, then rotated
  function euclid(k, n, rot) {
    const p = [];
    for (let i = 0; i < n; i++) p.push(Math.floor((i + 1) * k / n) - Math.floor(i * k / n));
    const r = modi(p.indexOf(1) + (rot || 0), n);
    return p.slice(r).concat(p.slice(0, r));
  }
  // The Fibonacci word, the rhythm of the golden ratio itself: 1 is the
  // rarer symbol (density 2 - φ = 0.382), and the pattern never repeats
  function fibBit(i) { return 2 + Math.floor(i * PHI) - Math.floor((i + 1) * PHI); }

  function ratioOfDeg(R, deg) {
    return R[modi(deg, R.length)] * Math.pow(2, Math.floor(deg / R.length));
  }

  // Harmonic functions as the scale degrees nearest the classic ratios
  function functionDegrees(R) {
    const near = (target) => {
      let best = 0, bd = 1e9;
      R.forEach((r, i) => { const d = Math.abs(Math.log2(r / target)); if (d < bd) { bd = d; best = i; } });
      return best;
    };
    return { T: 0, S: near(4/3), D: near(3/2), Sub: near(8/5), Med: near(6/5) };
  }

  function nearestChordTone(deg, tones, n) {
    let best = deg, bd = 1e9;
    for (const t of tones) {
      for (let o = -3; o <= 3; o++) {
        const c = t + o * n, d = Math.abs(c - deg);
        if (d < bd) { bd = d; best = c; }
      }
    }
    return best;
  }

  // Keep each chord tone near the previous chord's voices (LSS
  // _musicVoicePad), inside a warm register around half the tonic
  function voiceLead(target, prev) {
    return target.map((r, i) => {
      if (!prev) return r;
      const ref = prev[Math.min(i, prev.length - 1)];
      let best = r, bd = 1e9;
      for (let k = -2; k <= 2; k++) {
        const c = r * Math.pow(2, k);
        if (c < 0.45 || c > 1.3) continue;
        const d = Math.abs(Math.log2(c / ref));
        if (d < bd) { bd = d; best = c; }
      }
      return best;
    });
  }

  // A melodic line: a random walk in scale degrees, mostly steps, sometimes
  // leaps, with durations drawn from the given (Fibonacci-flavoured) list
  function genLine(rnd, lenSteps, durs, restP, lo, hi) {
    const out = [];
    let t = 0, deg = [0, 2, 4][Math.floor(rnd() * 3)];
    while (t < lenSteps) {
      let d = durs[Math.floor(rnd() * durs.length)];
      d = Math.min(d, lenSteps - t);
      if (t > 0 && rnd() < restP) { t += d; continue; }
      out.push({ s: t, d, deg });
      const r = rnd();
      const mv = r < 0.32 ? 1 : r < 0.64 ? -1 : r < 0.76 ? 2 : r < 0.88 ? -2 : r < 0.94 ? 0 : (rnd() < 0.5 ? 3 : -3);
      deg = Math.max(lo, Math.min(hi, deg + mv));
      t += d;
    }
    return out;
  }

  function fibForm(bars) {
    const [s, l] = FORM_SIZES[bars] || FORM_SIZES[34];
    const lens = [s, l, l, l, s];
    let start = 0;
    return SECTION_DEFS.map((d, i) => {
      const sec = Object.assign({}, d, { start, len: lens[i] });
      start += lens[i];
      return sec;
    });
  }

  // Compose one piece: a deterministic score of 16th-note steps. Pitches are
  // ratios of the tonic, so a new base frequency retunes it without
  // recomposing, and a new beat retimes it.
  function composePiece(m) {
    const R = (SCALES[m.scale] || SCALES.pent_minor).ratios;
    const n = R.length;
    const st = STYLES[m.style] || STYLES.ambient;
    const bars = FORM_SIZES[m.bars] ? +m.bars : 34;
    const rnd = mulberry32(((m.seed >>> 0) ^ hashStr(m.style + '|' + m.scale + '|' + bars)) >>> 0);
    const dens = Math.max(0, Math.min(1, m.density / 100));
    const steps = bars * 16;
    const events = Array.from({ length: steps }, () => []);
    let maxSpan = 1;
    const put = (step, e) => {
      if (step < 0 || step >= steps) return;
      if (!e.d) e.d = 1;
      events[step].push(e);
      if (e.d > maxSpan) maxSpan = e.d;
    };

    const sections = fibForm(bars);
    const secOfBar = new Array(bars);
    sections.forEach(s => { for (let b = s.start; b < s.start + s.len; b++) secOfBar[b] = s; });

    // Harmony: a functional progression mapped onto this scale's degrees,
    // restarting on the tonic at each section; the cycle closes on the tonic
    const fd = functionDegrees(R);
    const prog = st.progressions[Math.floor(rnd() * st.progressions.length)].map(f => fd[f]);
    const chords = new Array(bars), chordStart = new Array(bars).fill(false);
    sections.forEach(s => {
      for (let b = s.start; b < s.start + s.len; b++) {
        chords[b] = prog[Math.floor((b - s.start) / st.chordBars) % prog.length];
        chordStart[b] = (b - s.start) % st.chordBars === 0;
      }
    });
    if (chords[bars - 1] !== fd.T) { chords[bars - 1] = fd.T; chordStart[bars - 1] = true; }
    const toneSets = new Array(bars);
    let cur = null;
    for (let b = 0; b < bars; b++) {
      if (chordStart[b] || !cur) {
        cur = [chords[b], chords[b] + 2, chords[b] + 4];
        if (st.sevenths && rnd() < 0.5) cur.push(chords[b] + 6);
      }
      toneSets[b] = cur;
    }
    const chordLen = (b, limit) => { let len = 1; while (b + len < limit && !chordStart[b + len]) len++; return len; };

    // Pads: every chord, voice-led
    let prev = null;
    for (let b = 0; b < bars; b++) {
      if (!chordStart[b] && b !== 0) continue;
      const len = chordLen(b, bars);
      const voiced = voiceLead(toneSets[b].map(d => ratioOfDeg(R, d) * 0.5), prev);
      prev = voiced;
      const v = 0.5 + 0.5 * secOfBar[b].energy;
      put(b * 16, { i: 'pad', rs: voiced, d: len * 16 - 1, v });
    }

    // Bass: chord roots two octaves under the tonic reference
    sections.forEach(sec => {
      if (!st.bassIn.includes(sec.id)) return;
      const end = sec.start + sec.len;
      for (let b = sec.start; b < end; b++) {
        const root = chords[b], s0 = b * 16;
        const rr = (d) => ratioOfDeg(R, d) * 0.25;
        const v = 0.55 + 0.4 * sec.energy;
        if (st.bass === 'held') {
          if (chordStart[b] || b === sec.start) put(s0, { i: 'bass', r: rr(root), d: chordLen(b, end) * 16 - 2, v });
        } else if (st.bass === 'bar') {
          put(s0, { i: 'bass', r: rr(root), d: 12, v });
          if (sec.energy >= 0.72) put(s0 + 10, { i: 'bass', r: rr(root), d: 4, v: v * 0.6 });
        } else if (st.bass === 'synco') {
          // E(5,16): x..x..x..x..x... over root, root, octave, root, third
          const degs = [root, root, root + n, root, root + 2];
          let h = 0;
          euclid(5, 16, 0).forEach((x, s) => {
            if (!x) return;
            put(s0 + s, { i: 'bass', r: rr(degs[h % degs.length]), d: 2, v: h % 2 ? v * 0.75 : v });
            h++;
          });
        } else if (st.bass === 'eighths') {
          // LSS combat bass: driving eighths, a scale walk down to close each section
          const lastBar = b === end - 1;
          for (let s = 0; s < 16; s += 2) {
            const d = lastBar ? root - Math.floor(s / 4) : (s === 8 || s === 12) ? root + n : root;
            put(s0 + s, { i: 'bass', r: rr(d), d: 2, v: s % 4 === 0 ? v : v * 0.7 });
          }
        }
      }
    });

    // Drums
    if (st.drums !== 'none') sections.forEach(sec => {
      if (!st.drumsIn.includes(sec.id)) return;
      const e = sec.energy, end = sec.start + sec.len;
      for (let b = sec.start; b < end; b++) {
        const s0 = b * 16, lastBar = b === end - 1;
        if (st.drums === 'heart') {
          // lub-dub on the half bar, a resting heart under the music
          put(s0, { i: 'kick', v: 0.85 }); put(s0 + 1, { i: 'kick', v: 0.45 });
          if (e >= 0.5) { put(s0 + 8, { i: 'kick', v: 0.75 }); put(s0 + 9, { i: 'kick', v: 0.4 }); }
          if (e >= 0.72) [2, 6, 10, 14].forEach(s => put(s0 + s, { i: 'shaker', v: s % 8 === 6 ? 0.55 : 0.4 }));
        } else if (st.drums === 'down') {
          if (e >= 0.35) {
            put(s0, { i: 'kick', v: 0.95 }); put(s0 + 10, { i: 'kick', v: 0.7 });
            if (e >= 0.72 && b % 2 === 1) put(s0 + 7, { i: 'kick', v: 0.5 });
          }
          if (e >= 0.5) { put(s0 + 4, { i: 'snare', v: 0.75 }); put(s0 + 12, { i: 'snare', v: 0.8 }); }
          if (e >= 0.72) {
            for (let s = 0; s < 16; s++) if (fibBit(s0 + s) === 0) put(s0 + s, { i: 'hat', v: s % 4 === 2 ? 0.6 : 0.38 });
          } else if (e >= 0.35) {
            for (let s = 0; s < 16; s += 2) put(s0 + s, { i: 'hat', v: 0.4 });
          }
          if (e >= 1 && lastBar) put(s0 + 15, { i: 'snare', v: 0.35 });
        } else if (st.drums === 'drive') {
          if (e >= 0.5) {
            put(s0, { i: 'kick', v: 1 }); put(s0 + 8, { i: 'kick', v: 0.95 });
            if (e >= 1) put(s0 + 14, { i: 'kick', v: 0.55 });
            put(s0 + 4, { i: 'snare', v: 0.85 }); put(s0 + 12, { i: 'snare', v: 0.9 });
          } else if (e >= 0.35) {
            put(s0, { i: 'kick', v: 0.8 });
          }
          if (e >= 0.72) for (let s = 0; s < 16; s++) put(s0 + s, { i: 'hat', v: s % 2 ? 0.3 : 0.55 });
          else for (let s = 0; s < 16; s += 2) put(s0 + s, { i: 'hat', v: 0.45 });
          if (b === sec.start && (sec.id === 'A' || sec.id === 'C')) put(s0, { i: 'crash', v: 0.7 });
          // LSS transition fill into the next section
          if (lastBar && e >= 0.72) [12, 13, 14, 15].forEach((s, j) => put(s0 + s, { i: 'snare', v: 0.35 + j * 0.12 }));
        }
      }
    });

    // Bells: golden FM bells over the chord tones
    sections.forEach(sec => {
      if (!st.bellsIn.includes(sec.id)) return;
      const e = sec.energy;
      for (let b = sec.start; b < sec.start + sec.len; b++) {
        const s0 = b * 16, tones = toneSets[b];
        if (st.bells === 'sparse') {
          euclid(2 + Math.round(dens * 2), 16, (b * 5) % 16).forEach((x, s) => {
            if (!x) return;
            const deg = tones[Math.floor(rnd() * tones.length)] + (rnd() < 0.3 ? n : 0);
            put(s0 + s, { i: 'bell', r: ratioOfDeg(R, deg) * 2, d: 16, v: 0.45 + 0.35 * rnd(), p: rnd() * 1.2 - 0.6 });
          });
        } else if (st.bells === 'arp') {
          let idx = 0;
          euclid(5 + Math.round(dens * 3), 16, b % 2 ? 2 : 0).forEach((x, s) => {
            if (!x) return;
            const deg = tones[idx % tones.length] + n * (Math.floor(idx / tones.length) % 2);
            idx++;
            put(s0 + s, { i: 'bell', r: ratioOfDeg(R, deg) * 2, d: 8, v: 0.4 + 0.25 * e, p: idx % 2 ? -0.4 : 0.4 });
          });
        } else if (st.bells === 'fib') {
          for (let s = 0; s < 16; s += 2) {
            const k = (s0 + s) / 2;                      // global eighth-note index
            if ((e >= 0.72 ? fibBit(k) === 0 : fibBit(k) === 1) === false) continue;
            const j = Math.floor(k * PHI) % tones.length; // a golden walk through the chord
            const deg = tones[j] + (k % 3 === 0 ? n : 0);
            // pan steps by the golden angle (137.5°), a sunflower spiral in stereo
            put(s0 + s, { i: 'bell', r: ratioOfDeg(R, deg) * 2, d: 8, v: 0.4 + 0.3 * e, p: Math.sin(k * 2.39996) * 0.6 });
          }
        }
      }
    });

    // Lead
    if (st.lead !== 'none') sections.forEach(sec => {
      if (!st.leadIn.includes(sec.id)) return;
      const end = sec.start + sec.len, endStep = end * 16;
      if (st.lead === 'riff') {
        const contour = RIFF_CONTOURS[Math.floor(rnd() * RIFF_CONTOURS.length)];
        let ci = 0;
        for (let b = sec.start; b < end; b++) {
          if ((b - sec.start) % 2 === 0) ci = 0;     // the riff restarts every two bars
          RIFF_RHYTHM.forEach((x, s) => {
            if (!x) return;
            const deg = chords[b] + Math.round(contour[ci % contour.length] * n / 7);
            ci++;
            put(b * 16 + s, { i: 'lead', r: ratioOfDeg(R, deg), d: 2, v: x === 2 ? 0.85 : 0.55 });
          });
        }
        return;
      }
      // Motif melody: statement, statement over the new chord, statement,
      // answer; the answer ends on the tonic, held
      const slow = st.lead === 'slow';
      const mBars = slow ? 4 : 2;
      const durs = slow ? [5, 8, 8, 13] : [2, 2, 3, 3, 4, 5, 1];
      const restP = slow ? 0.3 : 0.32 - 0.18 * dens;
      const motif = genLine(rnd, mBars * 16, durs, restP, -1, n + 1);
      const answer = genLine(rnd, mBars * 16, durs, restP * 0.7, -1, n + 1);
      if (answer.length) {
        const last = answer[answer.length - 1];
        last.deg = last.deg > n / 2 ? n : 0;
        last.d = mBars * 16 - last.s;
      }
      for (let b = sec.start, j = 0; b < end; b += mBars, j++) {
        const isLast = b + mBars >= end;
        const line = (isLast || j % 4 === 3) ? answer : motif;
        const anchor = (j % 2 === 1) ? chords[b] : 0;
        for (const nt of line) {
          const step = b * 16 + nt.s;
          if (step >= endStep) continue;
          let deg = nt.deg + anchor;
          if (nt.s % 4 === 0) deg = nearestChordTone(deg, toneSets[Math.floor(step / 16)], n);
          put(step, { i: 'lead', r: ratioOfDeg(R, deg), d: Math.min(nt.d, endStep - step), v: (nt.s % 8 === 0 ? 0.9 : 0.7) * (0.75 + 0.25 * sec.energy) });
        }
      }
    });

    return { seed: m.seed >>> 0, style: m.style, scale: m.scale, bars, steps, events, sections, chords: toneSets, maxSpan, R };
  }

  // ----- tempo and tonic -----
  function composerTempo() {
    if (state.music.tempo === 'free') return { bpm: Math.max(40, +state.music.bpm || 90), k: null };
    const b = Math.max(0.01, +state.params.beat || 1);
    const k = Math.floor(Math.log2(60 * b / 64));
    return { bpm: 60 * b / Math.pow(2, k), k };
  }
  function stepDur() { return 60 / composerTempo().bpm / 4; }
  function tonicRef() {
    let f = Math.max(1, +state.params.base || 432);
    while (f >= 392) f /= 2;
    while (f < 196) f *= 2;
    return f;
  }
  function beatUnitName(k) {
    const names = { '-4': '4 bars', '-3': '2 bars', '-2': 'whole bar', '-1': 'half note', '0': 'quarter note',
                    '1': 'eighth note', '2': '16th note', '3': '32nd note', '4': '64th note', '5': '128th note' };
    if (names[k] != null) return names[k];
    return k < 0 ? Math.pow(2, -k - 2) + ' bars' : '1/' + (4 * Math.pow(2, k)) + ' note';
  }
  function bedLevel() { return state.music.on ? levelGain(state.music.levels.field) : 1; }
  function levelGain(v) { return Math.pow(Math.max(0, +v || 0) / 100, 1.5); }

  // ----- voices -----
  const _musicNoise = new WeakMap();
  function noiseSrc(ctx, t, len) {
    let b = _musicNoise.get(ctx);
    if (!b) {
      b = ctx.createBuffer(1, ctx.sampleRate, ctx.sampleRate);
      const d = b.getChannelData(0);
      for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
      _musicNoise.set(ctx, b);
    }
    const src = ctx.createBufferSource();
    src.buffer = b;
    src.loop = true;
    src.start(t, Math.random() * 0.5);
    src.stop(t + len);
    return src;
  }

  // Envelopes are the expensive part of rendering (an oscillator under a
  // moving gain costs about ten times a steady one), so slow envelopes run
  // at block rate where the browser allows it
  // A block-rate envelope takes one value per 128-sample block, read at the
  // block's start; a note starting mid-block would get the param's resting
  // value for its first samples, so the resting value is set first (the
  // gain default of 1 there was an audible click)
  function kRate(param, rest) {
    try { param.automationRate = 'k-rate'; } catch (e) {}
    if (rest != null) param.value = rest;
  }

  // A pad chord: every tone shares one envelope and one filter
  function vPad(ch, t, freqs, dur, vel, st, beatHz) {
    const ctx = ch.ctx;
    const a = st.padAttack, rel = st.padRelease;
    const bin = beatHz > 0;
    // binaural: one oscillator per ear per tone; otherwise two detuned
    // oscillators per tone summed in the centre, so a little quieter
    const peak = (bin ? 0.06 : 0.04) * vel;
    const end = t + Math.max(dur, a + 0.05);
    const amp = ctx.createGain();
    kRate(amp.gain, 0);
    amp.gain.setValueAtTime(0, t);
    amp.gain.linearRampToValueAtTime(peak, t + a);
    amp.gain.setValueAtTime(peak, end);
    amp.gain.linearRampToValueAtTime(0, end + rel);
    const f0 = Math.min.apply(null, freqs);
    const lp = ctx.createBiquadFilter();
    lp.type = 'lowpass';
    lp.Q.value = 0.6;
    kRate(lp.frequency);
    lp.frequency.setValueAtTime(Math.min(f0 * 3, 2000), t);
    lp.frequency.linearRampToValueAtTime(Math.min(f0 * 6, 4200), t + a + 0.6);
    lp.connect(amp);
    amp.connect(ch.buses.pad);
    const stopAt = end + rel + 0.05;
    // Binaural pads: left ear on the note, right ear one beat higher, each
    // ear hearing only its own tone (a channel merger, no panners)
    const merger = bin ? ctx.createChannelMerger(2) : null;
    if (merger) merger.connect(lp);
    freqs.forEach(f => {
      const oL = ctx.createOscillator(), oR = ctx.createOscillator();
      oL.type = st.padWave;
      oR.type = st.padWave;
      if (merger) {
        oL.frequency.value = f;
        oR.frequency.value = f + beatHz;
        oL.connect(merger, 0, 0);
        oR.connect(merger, 0, 1);
      } else {
        oL.frequency.value = f * 0.998;
        oR.frequency.value = f * 1.002;
        oL.connect(lp);
        oR.connect(lp);
      }
      oL.start(t); oR.start(t);
      oL.stop(stopAt); oR.stop(stopAt);
    });
    // a faint golden overtone above the root: the field's own interval
    const og = ctx.createOscillator();
    og.type = 'sine';
    og.frequency.value = f0 * PHI * 2;
    const gg = ctx.createGain();
    gg.gain.value = 0.12;
    og.connect(gg); gg.connect(lp);
    og.start(t); og.stop(stopAt);
  }

  const _bassSat = (() => {
    const c = new Float32Array(512);
    for (let i = 0; i < 512; i++) c[i] = Math.tanh((i / 255.5 - 1) * 1.7);
    return c;
  })();
  // Fast notes start straight at their peak on a block-rate envelope. That
  // is click-free because these waveforms (sine, triangle, sawtooth) all
  // begin at zero; the resting value is the peak, so the first partial
  // block is already right.
  function vBass(ch, t, f, dur, vel, st) {
    const ctx = ch.ctx;
    const held = st.bass === 'held';
    const atk = held ? 0.35 : 0, rel = held ? 0.9 : 0.06;
    const peak = (held ? 0.2 : 0.26) * vel;
    const end = t + Math.max(dur, held ? atk + 0.02 : 0.16);
    const o = ctx.createOscillator();
    o.type = st.bassWave;
    o.frequency.value = f;
    const body = ctx.createOscillator();
    body.type = 'sine';
    body.frequency.value = f;
    const lp = ctx.createBiquadFilter();
    lp.type = 'lowpass';
    lp.Q.value = held ? 0.7 : 2.2;
    kRate(lp.frequency);
    if (held) lp.frequency.value = Math.min(f * 4, 600);
    else {
      lp.frequency.setValueAtTime(Math.min(f * 10, 1600), t);
      lp.frequency.exponentialRampToValueAtTime(Math.max(f * 2.5, 120), t + 0.12);
    }
    const amp = ctx.createGain();
    if (held) {
      kRate(amp.gain, 0);
      amp.gain.setValueAtTime(0, t);
      amp.gain.linearRampToValueAtTime(peak, t + atk);
      amp.gain.setValueAtTime(peak, end);
    } else {
      kRate(amp.gain, peak);
      amp.gain.setValueAtTime(peak, t);
      amp.gain.linearRampToValueAtTime(peak * 0.7, t + 0.15);
      amp.gain.setValueAtTime(peak * 0.7, end);
    }
    amp.gain.linearRampToValueAtTime(0, end + rel);
    let src = o;
    if (st.bassDrive) {
      const sat = ctx.createWaveShaper();
      sat.curve = _bassSat;
      o.connect(sat);
      src = sat;
    }
    src.connect(lp);
    const bg = ctx.createGain();
    bg.gain.value = 0.6;
    body.connect(bg); bg.connect(lp);
    lp.connect(amp); amp.connect(ch.buses.bass);
    o.start(t); body.start(t);
    o.stop(end + rel + 0.05); body.stop(end + rel + 0.05);
  }

  function vLead(ch, t, f, dur, vel, st) {
    const ctx = ch.ctx;
    const atk = st.leadAttack || 0.03;
    const slow = atk >= 0.05;
    const rel = atk > 0.1 ? 0.7 : 0.12;
    const peak = 0.1 * vel;
    const end = t + Math.max(dur, atk + 0.17);
    const o = ctx.createOscillator();
    o.type = 'triangle';
    o.frequency.value = f;
    const oct = ctx.createOscillator();
    oct.type = 'sine';
    oct.frequency.value = f * 2;
    const og = ctx.createGain();
    og.gain.value = 0.15;
    // Vibrato blooms in after the attack (LSS lead)
    const lfo = ctx.createOscillator();
    lfo.type = 'sine';
    lfo.frequency.value = 5.2;
    const lg = ctx.createGain();
    kRate(lg.gain, 0);
    lg.gain.setValueAtTime(0, t);
    lg.gain.linearRampToValueAtTime(f * 0.0045, t + atk + 0.25);
    lfo.connect(lg); lg.connect(o.frequency);
    const amp = ctx.createGain();
    if (slow) {
      kRate(amp.gain, 0);
      amp.gain.setValueAtTime(0, t);
      amp.gain.linearRampToValueAtTime(peak, t + atk);
    } else {
      kRate(amp.gain, peak);
      amp.gain.setValueAtTime(peak, t);
    }
    amp.gain.linearRampToValueAtTime(peak * 0.6, t + atk + 0.15);
    amp.gain.setValueAtTime(peak * 0.6, end);
    amp.gain.linearRampToValueAtTime(0, end + rel);
    o.connect(amp); oct.connect(og); og.connect(amp); amp.connect(ch.buses.lead);
    const stopAt = end + rel + 0.05;
    o.start(t); oct.start(t); lfo.start(t);
    o.stop(stopAt); oct.stop(stopAt); lfo.stop(stopAt);
  }

  // Golden bell: FM with the modulator at φ times the carrier, so its
  // overtones are inharmonic (glassy) and soften as the index falls
  function vBell(ch, t, f, vel, pan, decay) {
    const ctx = ch.ctx;
    const dec = decay || 2.6;
    const car = ctx.createOscillator();
    car.type = 'sine';
    car.frequency.value = f;
    const mod = ctx.createOscillator();
    mod.type = 'sine';
    mod.frequency.value = f * PHI;
    const idx = ctx.createGain();
    kRate(idx.gain, f * 2.2);
    idx.gain.setValueAtTime(f * 2.2, t);
    idx.gain.exponentialRampToValueAtTime(f * 0.05, t + dec * 0.6);
    mod.connect(idx); idx.connect(car.frequency);
    const amp = ctx.createGain();
    kRate(amp.gain, 0.08 * vel);
    amp.gain.setValueAtTime(0.08 * vel, t);
    amp.gain.exponentialRampToValueAtTime(0.0001, t + dec);
    const pn = ctx.createStereoPanner();
    pn.pan.value = pan || 0;
    car.connect(amp); amp.connect(pn); pn.connect(ch.buses.bells);
    car.start(t); mod.start(t);
    car.stop(t + dec + 0.05); mod.stop(t + dec + 0.05);
  }

  function vKick(ch, t, vel) {
    const ctx = ch.ctx;
    const o = ctx.createOscillator();
    o.type = 'sine';
    kRate(o.frequency);
    o.frequency.setValueAtTime(140, t);
    o.frequency.exponentialRampToValueAtTime(44, t + 0.12);
    const a = ctx.createGain();
    kRate(a.gain, 0.75 * vel);
    a.gain.setValueAtTime(0.75 * vel, t);
    a.gain.exponentialRampToValueAtTime(0.001, t + 0.42);
    o.connect(a); a.connect(ch.buses.drums);
    o.start(t); o.stop(t + 0.45);
  }
  function noiseHit(ch, t, len, filterType, freq, q, peak) {
    const ctx = ch.ctx;
    const src = noiseSrc(ctx, t, len + 0.02);
    const f = ctx.createBiquadFilter();
    f.type = filterType;
    f.frequency.value = freq;
    if (q) f.Q.value = q;
    const a = ctx.createGain();
    kRate(a.gain, peak);
    a.gain.setValueAtTime(peak, t);
    a.gain.exponentialRampToValueAtTime(peak * 0.01, t + len);
    src.connect(f); f.connect(a); a.connect(ch.buses.drums);
    return f;
  }
  function vSnare(ch, t, vel) {
    const ctx = ch.ctx;
    const body = ctx.createOscillator();
    body.type = 'triangle';
    body.frequency.value = 190;
    const ba = ctx.createGain();
    kRate(ba.gain, 0.25 * vel);
    ba.gain.setValueAtTime(0.25 * vel, t);
    ba.gain.exponentialRampToValueAtTime(0.001, t + 0.07);
    body.connect(ba); ba.connect(ch.buses.drums);
    body.start(t); body.stop(t + 0.08);
    noiseHit(ch, t, 0.18, 'bandpass', 1900, 0.8, 0.4 * vel);
  }
  function vHat(ch, t, vel) { noiseHit(ch, t, 0.045, 'highpass', 7500, 0, 0.16 * vel); }
  function vShaker(ch, t, vel) { noiseHit(ch, t, 0.1, 'bandpass', 5200, 1.4, 0.1 * vel); }
  function vCrash(ch, t, vel) {
    const f = noiseHit(ch, t, 1.5, 'highpass', 6500, 0, 0.16 * vel);
    kRate(f.frequency);
    f.frequency.setValueAtTime(6500, t);
    f.frequency.exponentialRampToValueAtTime(2600, t + 0.9);
  }

  // ----- the music chain -----
  // Its own master, fade and reverb, separate from the field's graph, so a
  // field rebuild (any field setting change) never cuts a sustaining chord.
  function musicImpulse(ctx, seconds, decay) {
    const len = Math.max(1, Math.floor(ctx.sampleRate * seconds));
    const buf = ctx.createBuffer(2, len, ctx.sampleRate);
    for (let c = 0; c < 2; c++) {
      const d = buf.getChannelData(c);
      for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, decay);
    }
    return buf;
  }

  function makeMusicChain(ctx, dest, startLevel) {
    const m = state.music;
    const lvl = startLevel || 0;
    const master = ctx.createGain();
    master.gain.value = state.params.vol / 100 * MUSIC_TRIM;
    const fade = ctx.createGain();
    fade.gain.value = lvl;
    master.connect(fade);
    fade.connect(dest || ctx.destination);
    const verb = ctx.createConvolver();
    verb.buffer = musicImpulse(ctx, 3.2, 2.2);
    const wet = ctx.createGain();
    wet.gain.value = m.verb / 100;
    verb.connect(wet); wet.connect(master);
    const SENDS = { pad: 0.7, bass: 0.05, lead: 0.6, bells: 0.8, drums: 0.18 };
    const buses = {};
    Object.keys(SENDS).forEach(k => {
      const g = ctx.createGain();
      g.gain.value = levelGain(m.levels[k]);
      g.connect(master);
      const s = ctx.createGain();
      s.gain.value = SENDS[k];
      g.connect(s); s.connect(verb);
      buses[k] = g;
    });
    return { ctx, master, fade, verb, wet, buses, lvl: { from: lvl, to: lvl, t0: 0, t1: 0 } };
  }

  // The fade level is tracked in JS: AudioParam.value lags scheduled ramps,
  // and a fade that starts from a stale value starts from silence
  function chainLevel(ch) {
    if (!ch) return 0;
    const L = ch.lvl, now = ch.ctx.currentTime;
    if (now >= L.t1) return L.to;
    if (now <= L.t0) return L.from;
    return L.from + (L.to - L.from) * (now - L.t0) / (L.t1 - L.t0);
  }
  function chainFade(ch, to, sec) {
    const now = ch.ctx.currentTime, s = Math.max(0.01, sec);
    const from = chainLevel(ch);
    const g = ch.fade.gain;
    g.cancelScheduledValues(now);
    g.setValueAtTime(from, now);
    g.linearRampToValueAtTime(to, now + s);
    ch.lvl = { from, to, t0: now, t1: now + s };
  }
  function chainRetire(ch, sec) {
    if (!ch) return;
    chainFade(ch, 0, sec);
    setTimeout(() => { try { ch.fade.disconnect(); } catch (e) {} }, sec * 1000 + 300);
  }

  // ----- the live clock -----
  const composer = {
    piece: null, pending: null, key: '',
    restart: false, // the pending piece starts from its top (new seed or length)
    running: false, timer: null, stopAt: 0,
    origin: 0,      // context time of step 0 of the current cycle
    n: 0,           // next 16th step to schedule, counted from origin
    sd: 0.15,       // seconds per 16th step
    chain: null,
    lookahead: IS_MOBILE ? 0.6 : 0.3
  };

  function composerKey(m) { return [m.seed, m.style, m.scale, m.bars, m.density].join('|'); }

  function composerEnsurePiece() {
    const key = composerKey(state.music);
    if (!composer.piece || (composer.key !== key && !composer.running)) {
      composer.piece = composePiece(state.music);
      composer.key = key;
      composer.pending = null;
    }
    return composer.piece;
  }

  // New settings: compose the new piece; while playing it enters at the
  // next bar line, so the music never breaks off mid-phrase. A new style,
  // scale or density keeps its place in the form; a new seed (a new piece)
  // or a new length starts again from the top.
  function composerRecompose() {
    const key = composerKey(state.music);
    if (composer.key === key && composer.piece) return;
    const p = composePiece(state.music);
    composer.key = key;
    if (composer.running) {
      const cur = composer.piece;
      composer.restart = !cur || cur.seed !== p.seed || cur.bars !== p.bars;
      composer.pending = p;
    } else {
      composer.piece = p;
      composer.pending = null;
    }
  }

  function playStep(ch, piece, step, t, sd) {
    const evs = piece.events[step];
    if (!evs || !evs.length) return;
    const T = tonicRef();
    const st = STYLES[piece.style] || STYLES.ambient;
    const leadMul = T < 300 ? 2 : 1;
    const b = +state.params.beat;
    const beatHz = (state.music.binPads && b > 0 && b <= 12) ? b : 0;
    for (const e of evs) {
      const dur = e.d * sd;
      switch (e.i) {
        case 'pad':    vPad(ch, t, e.rs.map(r => T * r), dur, e.v, st, beatHz); break;
        case 'bass':   vBass(ch, t, T * e.r, dur, e.v, st); break;
        case 'lead':   vLead(ch, t, T * e.r * leadMul, dur, e.v, st); break;
        case 'bell':   vBell(ch, t, T * e.r, e.v, e.p, e.d <= 8 ? 1.3 : 2.6); break;
        case 'kick':   vKick(ch, t, e.v); break;
        case 'snare':  vSnare(ch, t, e.v); break;
        case 'hat':    vHat(ch, t, e.v); break;
        case 'shaker': vShaker(ch, t, e.v); break;
        case 'crash':  vCrash(ch, t, e.v); break;
      }
    }
  }

  function composerStart(fadeIn) {
    const ctx = ensureAudio();
    if (composer.pending) { composer.piece = composer.pending; composer.pending = null; }
    composerEnsurePiece();
    if (composer.chain) chainRetire(composer.chain, 0.3);
    composer.chain = makeMusicChain(ctx, ctx.destination, 0);
    chainFade(composer.chain, 1, fadeIn);
    composer.sd = stepDur();
    composer.origin = ctx.currentTime + 0.12;
    composer.n = 0;
    composer.stopAt = 0;
    composer.running = true;
    clearInterval(composer.timer);
    composer.timer = setInterval(composerTick, 40);
  }

  function composerStop(fadeSec) {
    if (!composer.running) return;
    if (composer.chain) chainFade(composer.chain, 0, fadeSec);
    composer.stopAt = state.ctx ? state.ctx.currentTime + fadeSec : 0;
    // Notes keep coming through the fade; the clock stops once it is silent
    setTimeout(() => {
      if (state.playing && state.music.on) return;   // restarted meanwhile
      composer.running = false;
      clearInterval(composer.timer);
      composer.timer = null;
    }, fadeSec * 1000 + 100);
  }

  function composerTick() {
    if (!composer.running || !composer.chain || !state.ctx) return;
    if (loopState.active || state.ctx.state !== 'running') return;
    const now = state.ctx.currentTime;
    if (composer.stopAt && now > composer.stopAt) return;
    // The tempo follows the beat live: keep the musical position, respace the grid
    const sd = stepDur();
    if (Math.abs(sd - composer.sd) > 1e-9) {
      composer.origin = composer.origin + composer.n * composer.sd - composer.n * sd;
      composer.sd = sd;
    }
    // A throttled tab or a paused engine: rejoin the timeline at "now"
    // instead of firing the whole backlog at once
    if (composer.origin + composer.n * sd < now - 0.15) {
      composer.n = Math.ceil((now + 0.05 - composer.origin) / sd);
    }
    const horizon = now + composer.lookahead;
    let guard = 0;
    while (composer.origin + composer.n * sd < horizon && guard++ < 256) {
      if (composer.pending && composer.n % 16 === 0) {
        if (composer.restart) {
          composer.origin += composer.n * sd;
          composer.n = 0;
        }
        composer.piece = composer.pending;
        composer.pending = null;
        renderComposerForm();
      }
      const p = composer.piece;
      playStep(composer.chain, p, composer.n % p.steps, composer.origin + composer.n * sd, sd);
      composer.n++;
    }
  }

  // Seconds into the current cycle, or null when the clock is not running
  function composerPos() {
    if (!composer.running || !composer.piece || !state.ctx) return null;
    const C = composer.piece.steps * composer.sd;
    // Just after a new piece is scheduled its start can still lie ahead
    // (the clock works a lookahead in advance): count that as its first moment
    const d = state.ctx.currentTime - composer.origin;
    return d < 0 ? 0 : d % C;
  }

  // The loop element played the music while the engine slept: pick the live
  // timeline up at the element's position, so the music simply carries on
  function composerResumeFromLoop(posSec, fadeIn) {
    if (!composer.running || !state.music.on || !composer.piece) return;
    const ctx = ensureAudio();
    if (composer.chain) chainRetire(composer.chain, 0.02);
    // a crossfade back (Android, desktop) fades the live music in under the
    // fading loop; otherwise it takes over at full level
    composer.chain = makeMusicChain(ctx, ctx.destination, fadeIn > 0 ? 0 : 1);
    if (fadeIn > 0) chainFade(composer.chain, 1, fadeIn);
    composer.sd = stepDur();
    const C = composer.piece.steps * composer.sd;
    const pos = ((posSec % C) + C) % C;
    composer.origin = ctx.currentTime + 0.06 - pos;
    composer.n = Math.ceil(pos / composer.sd);
  }

  function composerRetireChain(sec) {
    if (composer.chain) { chainRetire(composer.chain, sec); composer.chain = null; }
  }

  // ----- offline scheduling -----
  // An offline render that is handed every note up front holds thousands of
  // idle future nodes in the graph and walks all of them on every block
  // (measured: a 90 s Downtempo piece took 19.6 s). The live clock never
  // holds more than its lookahead, so offline renders do the same: pause
  // every 2 s, add the next window of notes, resume (where the browser can
  // pause an offline render: offlineSuspendWorks, in the background code).
  function scheduleOffline(off, ch, piece, t0, fromStep, toStep, sd, progressive, onProgress) {
    const WIN = 2;
    let next = fromStep;
    const fill = (until) => {
      while (next < toStep) {
        const t = t0 + next * sd;
        if (t >= until) break;
        if (t >= 0) playStep(ch, piece, modi(next, piece.steps), t, sd);
        next++;
      }
    };
    if (!progressive) { fill(Infinity); return; }
    const endT = Math.min(t0 + toStep * sd, off.length / off.sampleRate - 0.05);
    fill(WIN + 0.5);
    for (let w = WIN; w < endT; w += WIN) {
      off.suspend(w).then(() => {
        fill(w + WIN + 0.5);
        if (onProgress) onProgress(w);
        off.resume();
      });
    }
  }

  // Line an oscillator's cycles up with the music grid (the isochronic
  // pulse lands on the beat of the music)
  function gridStartFor(period) {
    const ctx = state.ctx;
    if (!state.music.on || state.music.tempo !== 'locked') return ctx.currentTime;
    if (state.rendering) {
      const o = state.renderOrigin || 0;
      return o - Math.floor(o / period) * period;
    }
    if (!composer.running) return ctx.currentTime;
    const now = ctx.currentTime, o = composer.origin;
    return o + Math.ceil((now - o) / period) * period;
  }

