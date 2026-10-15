// Plate toolkit shared by every fractal. Each algorithm is a generator: it draws a little,
// yields, and the book's runner resumes it on the next frame so the plate grows in front of you.
(function () {
  'use strict';
  const TAU = Math.PI * 2;

  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function hashSeed() {
    let h = 2166136261;
    for (const part of arguments) {
      const s = String(part);
      for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
    }
    return h >>> 0;
  }

  // Four stops each, dark to bright: luminous inks on the night plate.
  const PALETTES = [
    { name: 'gold leaf', stops: ['#2b1d06', '#9c6b1e', '#e9b949', '#fff3d1'] },
    { name: 'aurora',    stops: ['#06222e', '#1f7fa8', '#6fe8c4', '#eafff8'] },
    { name: 'ember',     stops: ['#260a0c', '#a8382a', '#ff9348', '#ffe7bf'] },
    { name: 'violet',    stops: ['#170c2e', '#5b3fc4', '#be95ff', '#f6ecff'] },
    { name: 'verdigris', stops: ['#06241c', '#178066', '#8fe0a2', '#f2ffe8'] },
    { name: 'rose',      stops: ['#260818', '#a63470', '#ff9cc2', '#fff0f6'] },
    { name: 'lapis',     stops: ['#08102c', '#2f4fd0', '#9fb8ff', '#ffffff'] },
    { name: 'copper',    stops: ['#1c1009', '#8f5226', '#e2a265', '#fff0dc'] }
  ];

  function hex(h) {
    const n = parseInt(h.slice(1), 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  }

  function makePalette(p) {
    const stops = p.stops.map(hex);
    const ramp = function (t) {
      t = t < 0 ? 0 : t > 1 ? 1 : t;
      const f = t * (stops.length - 1);
      const i = Math.min(stops.length - 2, Math.floor(f));
      const u = f - i, a = stops[i], b = stops[i + 1];
      return [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u];
    };
    const css = function (t, alpha) {
      const c = ramp(t);
      return 'rgba(' + (c[0] | 0) + ',' + (c[1] | 0) + ',' + (c[2] | 0) + ',' + (alpha == null ? 1 : alpha) + ')';
    };
    const lut = function (n) {
      const L = new Uint8ClampedArray(n * 3);
      for (let i = 0; i < n; i++) {
        const c = ramp(i / (n - 1));
        L[i * 3] = c[0]; L[i * 3 + 1] = c[1]; L[i * 3 + 2] = c[2];
      }
      return L;
    };
    return { name: p.name, ramp: ramp, css: css, lut: lut };
  }

  function offscreen(W, H) {
    const c = document.createElement('canvas');
    c.width = W; c.height = H;
    return c;
  }

  function Plate(canvas, seed, paletteIndex, opts) {
    const ctx = canvas.getContext('2d');
    const w = canvas.width, h = canvas.height;
    const rnd = mulberry32(seed);
    const g = {
      ctx: ctx, w: w, h: h, S: Math.min(w, h), cx: w / 2, cy: h / 2, TAU: TAU,
      seed: seed, o: opts || {}, rnd: rnd, name: '', caption: '',
      pal: makePalette(PALETTES[((paletteIndex % PALETTES.length) + PALETTES.length) % PALETTES.length]),
      rr: function (a, b) { return a + (b - a) * rnd(); },
      ri: function (a, b) { return Math.floor(a + (b - a + 1) * rnd()); },
      pick: function (arr) { return arr[Math.floor(rnd() * arr.length)]; },
      chance: function (p) { return rnd() < p; },
      // Signed number with a true minus sign, for captions.
      f: function (x, d) { return (x < 0 ? '−' : '') + Math.abs(x).toFixed(d == null ? 2 : d); }
    };

    g.clear = function () {
      ctx.globalCompositeOperation = 'source-over';
      ctx.globalAlpha = 1;
      ctx.fillStyle = '#05060b';
      ctx.fillRect(0, 0, w, h);
      const c0 = g.pal.ramp(0);
      const rg = ctx.createRadialGradient(g.cx, g.cy, 0, g.cx, g.cy, g.S * 0.78);
      rg.addColorStop(0, 'rgba(' + (c0[0] | 0) + ',' + (c0[1] | 0) + ',' + (c0[2] | 0) + ',0.85)');
      rg.addColorStop(1, 'rgba(5,6,11,0)');
      ctx.fillStyle = rg;
      ctx.fillRect(0, 0, w, h);
    };

    // Soft luminous dot. Use with ctx.globalCompositeOperation = 'lighter'.
    g.glow = function (x, y, r, t, alpha) {
      const rg = ctx.createRadialGradient(x, y, 0, x, y, r);
      rg.addColorStop(0, g.pal.css(t, alpha));
      rg.addColorStop(1, g.pal.css(t, 0));
      ctx.fillStyle = rg;
      ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill();
    };

    // Opaque pixel buffer at a reduced scale, for escape-time fractals.
    g.buffer = function (scale) {
      const W = Math.max(1, Math.round(w * scale)), H = Math.max(1, Math.round(h * scale));
      const off = offscreen(W, H), octx = off.getContext('2d');
      const img = octx.createImageData(W, H);
      return {
        W: W, H: H, data: img.data,
        flush: function (y0, y1) {
          y0 = y0 || 0; y1 = y1 == null ? H : y1;
          if (y1 > y0) octx.putImageData(img, 0, 0, 0, y0, W, y1 - y0);
          ctx.globalCompositeOperation = 'source-over';
          ctx.imageSmoothingEnabled = true;
          ctx.drawImage(off, 0, 0, w, h);
        }
      };
    };

    // Density histogram for attractors and chaos games: brightness from hit count,
    // tint from the average color index carried by each hit.
    g.hist = function (scale) {
      const W = Math.max(1, Math.round(w * scale)), H = Math.max(1, Math.round(h * scale));
      const n = new Float32Array(W * H), ts = new Float32Array(W * H);
      const off = offscreen(W, H), octx = off.getContext('2d');
      const img = octx.createImageData(W, H), d = img.data;
      const L = g.pal.lut(256);
      return {
        W: W, H: H,
        add: function (x, y, t) {
          const xi = x | 0, yi = y | 0;
          if (xi < 0 || yi < 0 || xi >= W || yi >= H) return;
          const i = yi * W + xi;
          n[i] += 1; ts[i] += t;
        },
        render: function (gamma) {
          gamma = gamma || 0.8;
          let max = 0;
          for (let i = 0; i < n.length; i++) if (n[i] > max) max = n[i];
          const lm = Math.log1p(max) || 1;
          for (let i = 0; i < n.length; i++) {
            const c = n[i], j = i * 4;
            if (!c) { d[j + 3] = 0; continue; }
            const k = Math.pow(Math.log1p(c) / lm, gamma);
            const tt = ts[i] / c;
            const bi = (Math.min(1, 0.3 + 0.55 * tt) * 255) | 0;
            const wk = k * k * k, bk = Math.min(1, k * 1.25);
            d[j]     = L[bi * 3] * bk * (1 - wk) + L[765] * wk;
            d[j + 1] = L[bi * 3 + 1] * bk * (1 - wk) + L[766] * wk;
            d[j + 2] = L[bi * 3 + 2] * bk * (1 - wk) + L[767] * wk;
            d[j + 3] = Math.min(255, k * 520);
          }
          octx.putImageData(img, 0, 0);
          g.clear();
          ctx.imageSmoothingEnabled = true;
          ctx.drawImage(off, 0, 0, w, h);
        }
      };
    };

    return g;
  }

  window.ART = {};
  window.PlateKit = { Plate: Plate, PALETTES: PALETTES, hashSeed: hashSeed, TAU: TAU };
})();
