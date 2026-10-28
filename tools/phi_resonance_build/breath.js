  // ============= BREATH GUIDE (dot on a half sine; 3 - 12 bpm) =============
  // One full traversal left-to-right = one breath (inhale on rise, exhale on
  // fall); at the breath's end the dot snaps back to the left. One clock drives
  // every view of it (owner: "the breathing bar should be able to be paired
  // with flashing visuals"): its own popup, a lane on the main screen, and a
  // layer over the flashes, wherever they run.
  // The lane on the main screen is on by default (owner: "we should also have
  // the breathing on the main screen by default"). The key is v2 because a
  // choice saved under the old default (off) should start over once.
  const BREATH_WHERE_KEY = 'phi_resonance_breath_where_v2';

  state.breath = {
    playing: false,
    raf: 0,
    t0: 0,           // timestamp (ms) of the current breath's start
    rate: 6.0,       // breaths per minute
    onStage: true,   // shown on the main screen
    onFlash: false   // shown over the flashes
  };
  try {
    const saved = JSON.parse(localStorage.getItem(BREATH_WHERE_KEY) || 'null');
    if (saved) {
      state.breath.onStage = !!saved.stage;
      state.breath.onFlash = !!saved.flash;
    }
  } catch (e) {}

  const breathPlay = $('breathPlay');
  const breathRate = $('breathRate');
  const breathRateVal = $('breathRateVal');
  const stageEl = $('stage');

  // Are the flashes running, and in which place ('full' or 'stage')?
  function flashIn(where) {
    if (!state.vbeat || !state.vbeat.active) return false;
    return (state.vbeat.where === 'stage') === (where === 'stage');
  }

  // The views. Over flashing colour the lines carry a dark edge so they read.
  const breathViews = [
    { canvas: $('breathCanvas'), label: $('breathPhase'), cls: 'breath-phase', idle: 'READY',
      padX: 26, padTop: 28, padBot: 24, dot: 9 },
    { canvas: $('stageBreathCanvas'), label: $('stageBreathPhase'), cls: 'stage-breath-phase', idle: 'TAP TO BREATHE',
      padX: 24, padTop: 14, padBot: 18, dot: 7,
      edge: () => flashIn('stage'), show: () => stageEl.classList.contains('breath-on') && !coveredByFlash() },
    { canvas: $('flashBreathCanvas'), label: $('flashBreathPhase'), cls: 'flash-breath-phase', idle: 'READY',
      padX: 36, padTop: 20, padBot: 20, dot: 11,
      edge: () => true, show: () => state.breath.onFlash && flashIn('full') }
  ];

  // Where the breath is: u in [0, 1), 0 at the start of the inhale
  function breathU(tNow) {
    if (!state.breath.playing) return 0;
    if (!state.breath.t0) state.breath.t0 = tNow;
    const periodSec = 60 / state.breath.rate;   // seconds per breath
    const elapsed = Math.max(0, (tNow - state.breath.t0) / 1000);
    return (elapsed / periodSec) % 1;
  }

  function paintBreath(view, u) {
    const c = view.canvas;
    const W = c.clientWidth, H = c.clientHeight;
    if (!W || !H) return;   // its view is closed
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const cw = Math.round(W * dpr), ch = Math.round(H * dpr);
    if (c.width !== cw || c.height !== ch) { c.width = cw; c.height = ch; }
    const ctx = c.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);
    const edge = view.edge ? view.edge() : false;

    // Layout: the arch spans the view inside its margins
    const x0 = view.padX, x1 = W - view.padX;
    const yBase = H - view.padBot, yTop = view.padTop;
    const archW = x1 - x0, archH = yBase - yTop;
    const at = (tu) => [x0 + tu * archW, yBase - Math.sin(tu * Math.PI) * archH];
    function trace(n) {                   // the arch from its start to step n of 64
      ctx.beginPath();
      for (let i = 0; i <= n; i++) {
        const p = at(i / 64);
        if (i === 0) ctx.moveTo(p[0], p[1]); else ctx.lineTo(p[0], p[1]);
      }
    }
    function line(color, width) {         // over flashing colour, a dark edge first
      if (edge) { ctx.strokeStyle = 'rgba(0, 0, 0, 0.55)'; ctx.lineWidth = width + 4; ctx.stroke(); }
      ctx.strokeStyle = color;
      ctx.lineWidth = width;
      ctx.stroke();
    }

    // The arch (half sine from (x0, yBase) to (x1, yBase), peak at mid-top)
    trace(64);
    line(edge ? 'rgba(255, 255, 255, 0.5)' : 'rgba(255, 170, 0, 0.35)', 2);

    // Baseline (ground)
    ctx.beginPath();
    ctx.moveTo(x0 - 8, yBase);
    ctx.lineTo(x1 + 8, yBase);
    line(edge ? 'rgba(255, 255, 255, 0.35)' : 'rgba(255, 255, 255, 0.12)', 1);

    // Trail (the arch from the start to the dot)
    trace(Math.max(2, Math.floor(u * 64)));
    line(edge ? 'rgba(255, 255, 255, 0.92)' : 'rgba(255, 170, 0, 0.75)', 3);

    // The dot and its halo
    const [dx, dy] = at(u);
    const dotColor = u < 0.5 ? '#8fd3ff' : '#ffb08f';
    const halo = view.dot * 2.4;
    if (edge) {
      ctx.beginPath();
      ctx.arc(dx, dy, view.dot + 3, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
      ctx.fill();
    }
    ctx.beginPath();
    ctx.arc(dx, dy, halo, 0, Math.PI * 2);
    const grad = ctx.createRadialGradient(dx, dy, 0, dx, dy, halo);
    grad.addColorStop(0, dotColor + 'cc');
    grad.addColorStop(1, dotColor + '00');
    ctx.fillStyle = grad;
    ctx.fill();
    ctx.beginPath();
    ctx.arc(dx, dy, view.dot, 0, Math.PI * 2);
    ctx.fillStyle = dotColor;
    ctx.shadowColor = dotColor;
    ctx.shadowBlur = 16;
    ctx.fill();
    ctx.shadowBlur = 0;

    // Tick markers for the in, turn and out positions
    [0, 0.5, 1].forEach(pos => {
      const tx = x0 + pos * archW;
      ctx.beginPath();
      ctx.moveTo(tx, yBase);
      ctx.lineTo(tx, yBase + 6);
      line(edge ? 'rgba(255, 255, 255, 0.6)' : 'rgba(255, 255, 255, 0.35)', 1);
    });
  }

  function labelBreath(view, u) {
    let text = view.idle, cls = view.cls;
    if (state.breath.playing) {
      const isInhale = u < 0.5;
      text = isInhale ? 'INHALE' : 'EXHALE';
      cls += isInhale ? ' inhale' : ' exhale';
    }
    if (view.label.textContent !== text) view.label.textContent = text;
    if (view.label.className !== cls) view.label.className = cls;
  }

  // One loop paints every open view, so they all share one breath
  function breathLoop(now) {
    state.breath.raf = requestAnimationFrame(breathLoop);
    if (!frameDue('breath', now)) return;   // the frame cap (see frameDue)
    const u = breathU(now);
    breathViews.forEach(v => {
      if (v.show && !v.show()) return;
      paintBreath(v, u);
      labelBreath(v, u);
    });
  }

  // Every control and view follows the breath's state
  function syncBreathControls() {
    breathPlay.textContent = state.breath.playing ? '■ STOP' : '▶ START';
    breathPlay.classList.toggle('playing', state.breath.playing);
    document.querySelectorAll('[data-breath-where]').forEach(b => {
      const on = b.dataset.breathWhere === 'stage' ? state.breath.onStage : state.breath.onFlash;
      b.setAttribute('aria-pressed', String(on));
      b.textContent = on ? 'ON' : 'OFF';
    });
    // The lane shows when it is asked for on the main screen, or when the
    // flashes run there with the breath riding over them
    stageEl.classList.toggle('breath-on', state.breath.onStage || (state.breath.onFlash && flashIn('stage')));
    $('flashOverlay').classList.toggle('with-breath', state.breath.onFlash);
    $('stageBreath').setAttribute('aria-pressed', String(state.breath.playing));
  }
  function startBreath() {
    state.breath.playing = true;
    state.breath.t0 = 0;
    syncBreathControls();
  }
  function stopBreath() {
    state.breath.playing = false;
    syncBreathControls();
  }
  function toggleBreath() {
    if (state.breath.playing) stopBreath(); else startBreath();
  }
  breathPlay.addEventListener('click', toggleBreath);
  $('stageBreath').addEventListener('click', toggleBreath);
  document.querySelectorAll('[data-breath-where]').forEach(b => {
    b.addEventListener('click', () => {
      const key = b.dataset.breathWhere === 'stage' ? 'onStage' : 'onFlash';
      state.breath[key] = !state.breath[key];
      // putting the guide somewhere new starts it breathing
      if (state.breath[key] && !state.breath.playing) startBreath();
      try {
        localStorage.setItem(BREATH_WHERE_KEY, JSON.stringify({ stage: state.breath.onStage, flash: state.breath.onFlash }));
      } catch (e) {}
      syncBreathControls();
    });
  });
  breathRate.addEventListener('input', (e) => {
    const v = parseFloat(e.target.value);
    state.breath.rate = v;
    breathRateVal.textContent = v.toFixed(1) + ' bpm';
    // Reset phase so the new rate starts cleanly (no mid-breath jump)
    state.breath.t0 = 0;
  });
  syncBreathControls();
  state.breath.raf = requestAnimationFrame(breathLoop);

