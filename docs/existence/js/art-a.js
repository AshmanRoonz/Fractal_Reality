// Plates, part one: circumpunct, tree, julia, mandel, ifs, nested, attractor, flow.
(function () {
  'use strict';
  const ART = window.ART, TAU = Math.PI * 2;

  // ---------- shared helpers ----------

  // Rows in center-out order, so escape-time plates open from the middle.
  function rowAt(k, H) { const mid = H >> 1; return k % 2 ? mid - ((k + 1) >> 1) : mid + (k >> 1); }

  function* escape(buf, pixel) {
    const W = buf.W, H = buf.H, d = buf.data;
    for (let k = 0; k < H; k++) {
      const y = rowAt(k, H);
      for (let x = 0; x < W; x++) pixel(x, y, d, (y * W + x) * 4);
      if ((k & 7) === 7) { buf.flush(); yield; }
    }
    buf.flush();
  }

  // Escape-time plates: iter(x, y) returns a smooth count, or -1 inside the set.
  // A coarse pre-pass finds the range of counts in view, so every zoom gets a dark
  // ground and a bright edge. mod(t) may tint the final value.
  function* escapeShaded(g, buf, iter, gamma, mod) {
    const W = buf.W, H = buf.H, L = g.pal.lut(256), logs = [];
    for (let y = 0; y < 40; y++) {
      for (let x = 0; x < 40; x++) {
        const v = iter((x + 0.5) / 40 * W, (y + 0.5) / 40 * H);
        if (v >= 0) logs.push(Math.log(v + 1));
      }
    }
    logs.sort(function (p, q) { return p - q; });
    const lo = logs.length ? logs[Math.floor(logs.length * 0.02)] : 0;
    const hi = logs.length ? logs[Math.floor(logs.length * 0.995)] : 1;
    const span = Math.max(1e-6, hi - lo);
    yield;
    yield* escape(buf, function (px, py, d, j) {
      const v = iter(px, py);
      if (v < 0) { inside(d, j, L); return; }
      let t = (Math.log(v + 1) - lo) / span;
      t = Math.pow(t < 0 ? 0 : t > 1 ? 1 : t, gamma);
      if (mod) t = mod(t);
      const k = (t * 255) | 0;
      d[j] = L[k * 3]; d[j + 1] = L[k * 3 + 1]; d[j + 2] = L[k * 3 + 2]; d[j + 3] = 255;
    });
  }

  function inside(d, j, L) {
    d[j] = L[30] * 0.35; d[j + 1] = L[31] * 0.35; d[j + 2] = L[32] * 0.35 + 4; d[j + 3] = 255;
  }

  function* dust(g, n, place, tBase, tVar, alpha, size) {
    const ctx = g.ctx;
    for (let i = 0; i < n; i++) {
      if (i % 240 === 0) ctx.fillStyle = g.pal.css(tBase + (g.rnd() - 0.5) * tVar, alpha);
      const p = place(i);
      ctx.fillRect(p[0], p[1], size, size);
      if (i % 3000 === 2999) yield;
    }
  }

  function gauss(g) { return g.rnd() + g.rnd() + g.rnd() - 1.5; }

  // ---------- circumpunct: center, field, boundary ----------
  ART.circumpunct = function* (g) {
    const ctx = g.ctx, cx = g.cx, cy = g.cy, S = g.S;
    const lone = !!g.o.lone, aperture = !!g.o.aperture;
    const dpr = Math.max(1, S / 700);
    g.clear();
    ctx.globalCompositeOperation = 'lighter';
    const rot = g.rr(0, TAU);

    if (lone) {
      g.name = 'A single point';
      g.caption = 'no boundary, no parts';
      for (let k = 1; k <= 5; k++) {
        ctx.strokeStyle = g.pal.css(0.7, 0.16 / k);
        ctx.lineWidth = dpr;
        ctx.beginPath(); ctx.arc(cx, cy, S * 0.07 * k * k * 0.5, 0, TAU); ctx.stroke();
      }
      yield* dust(g, 2200, function () { return [g.rnd() * g.w, g.rnd() * g.h]; }, 0.6, 0.4, 0.22, dpr);
      g.glow(cx, cy, S * 0.12, 0.85, 0.35);
      g.glow(cx, cy, S * 0.03, 1, 0.9);
      return;
    }

    const R = S * g.rr(0.33, 0.38);
    const rings = g.ri(4, 9), rays = g.ri(5, 12) * 2, p = g.rr(0.75, 1.5);
    g.name = aperture ? 'Aperture' : 'Circumpunct';

    if (aperture) {
      const blades = g.ri(6, 11), hole = R * g.rr(0.22, 0.34), sweep = g.rr(0.9, 1.6) * (g.chance(0.5) ? 1 : -1);
      g.caption = blades + ' blades, open center';
      ctx.lineWidth = 1.1 * dpr;
      for (let b = 0; b < blades; b++) {
        const th0 = rot + b / blades * TAU;
        for (let s = 0; s < 46; s++) {
          const off = s / 46 * (TAU / blades);
          ctx.strokeStyle = g.pal.css(0.45 + 0.5 * s / 46, 0.11);
          ctx.beginPath();
          for (let q = 0; q <= 40; q++) {
            const u = q / 40, r = R - (R - hole) * u, a = th0 + off + sweep * u * u;
            if (q) ctx.lineTo(cx + Math.cos(a) * r, cy + Math.sin(a) * r);
            else ctx.moveTo(cx + Math.cos(a) * r, cy + Math.sin(a) * r);
          }
          ctx.stroke();
        }
        yield;
      }
    } else {
      g.caption = rings + ' rings, ' + rays + ' rays';
      // Field: dust gathered along rays, densest at the center.
      yield* dust(g, rays * 700, function (i) {
        const a = rot + (i % rays) / rays * TAU + gauss(g) * 0.025;
        const r = R * Math.pow(g.rnd(), 1.8);
        return [cx + Math.cos(a) * r, cy + Math.sin(a) * r];
      }, 0.7, 0.4, 0.28, dpr);
    }

    // Rings of stippled light.
    for (let k = 1; k <= rings; k++) {
      const rk = R * Math.pow(k / (rings + 1), p);
      if (aperture && rk < R * 0.36) continue;
      const n = Math.round(1800 + rk / S * 9000);
      yield* dust(g, n, function () {
        const a = g.rnd() * TAU, r = rk + gauss(g) * S * 0.004;
        return [cx + Math.cos(a) * r, cy + Math.sin(a) * r];
      }, 0.5 + 0.4 * k / rings, 0.2, 0.35, dpr);
    }

    // Boundary.
    ctx.save();
    ctx.shadowColor = g.pal.css(0.85, 0.9);
    ctx.shadowBlur = S * 0.02;
    ctx.strokeStyle = g.pal.css(0.9, 0.9);
    ctx.lineWidth = S * 0.006;
    ctx.beginPath(); ctx.arc(cx, cy, R, 0, TAU); ctx.stroke();
    ctx.restore();
    yield;

    // Center.
    g.glow(cx, cy, S * 0.1, 0.8, 0.4);
    g.glow(cx, cy, S * 0.028, 1, 0.95);
    ctx.fillStyle = g.pal.css(1, 1);
    ctx.beginPath(); ctx.arc(cx, cy, S * 0.008, 0, TAU); ctx.fill();
  };

  // ---------- tree: branching generations ----------
  ART.tree = function* (g) {
    const ctx = g.ctx, S = g.S;
    g.clear();
    ctx.globalCompositeOperation = 'lighter';
    ctx.lineCap = 'round';
    const kids = g.pick([2, 2, 3]);
    const depth = kids === 3 ? g.ri(7, 8) : g.ri(10, 12);
    const spread = g.rr(0.32, 0.62), decay = kids === 3 ? g.rr(0.6, 0.66) : g.rr(0.7, 0.78);
    const jitter = g.rr(0.04, 0.22), lean = g.rr(-0.06, 0.06);
    const len0 = S * 0.74 * (1 - decay);
    let width = S * 0.02;
    let level = [{ x: g.cx, y: g.h * 0.97, a: -Math.PI / 2 + lean, len: len0 }];
    g.name = 'Fractal tree';
    g.caption = kids + '-fold, ' + depth + ' generations, ' + Math.round(spread * 2 * 180 / Math.PI) + '° spread';

    for (let d = 0; d < depth; d++) {
      const next = [], u = d / (depth - 1);
      ctx.strokeStyle = g.pal.css(0.3 + 0.65 * u, 0.5 + 0.35 * u);
      ctx.lineWidth = Math.max(0.6, width);
      ctx.beginPath();
      for (const b of level) {
        const x2 = b.x + Math.cos(b.a) * b.len, y2 = b.y + Math.sin(b.a) * b.len;
        ctx.moveTo(b.x, b.y); ctx.lineTo(x2, y2);
        if (d < depth - 1) {
          for (let k = 0; k < kids; k++) {
            const off = (k / (kids - 1) - 0.5) * 2 * spread;
            next.push({ x: x2, y: y2, a: b.a + off + (g.rnd() - 0.5) * jitter, len: b.len * decay * (0.88 + 0.24 * g.rnd()) });
          }
        } else {
          next.push({ x: x2, y: y2 });
        }
      }
      ctx.stroke();
      width *= 0.72;
      level = next;
      yield;
    }
    // Blossoms at the tips.
    for (let i = 0; i < level.length; i++) {
      const b = level[i];
      ctx.fillStyle = g.pal.css(0.85 + 0.15 * g.rnd(), 0.5);
      ctx.beginPath(); ctx.arc(b.x, b.y, S * 0.0022 * (1 + g.rnd()), 0, TAU); ctx.fill();
      if (i % 2000 === 1999) yield;
    }
  };

  // ---------- julia: escape-time boundary ----------
  const JULIA_C = [[-0.8, 0.156], [-0.7269, 0.1889], [0.285, 0.01], [-0.4, 0.6], [0.355, 0.355],
    [-0.70176, -0.3842], [-0.835, -0.2321], [-0.1, 0.651], [0.45, 0.1428], [-0.54, 0.54], [-0.12, -0.77], [0.37, 0.1]];

  ART.julia = function* (g) {
    const b = g.pick(JULIA_C);
    const cr = b[0] + g.rr(-0.006, 0.006), ci = b[1] + g.rr(-0.006, 0.006);
    const rot = g.rr(0, TAU), cs = Math.cos(rot), sn = Math.sin(rot), span = g.rr(1.25, 1.55);
    const buf = g.buffer(Math.min(1, 720 / g.w)), W = buf.W, H = buf.H;
    const maxIt = 280, L = g.pal.lut(256);
    g.name = 'Julia set';
    g.caption = 'c = ' + g.f(cr, 4) + (ci < 0 ? ' − ' : ' + ') + Math.abs(ci).toFixed(4) + 'i';
    g.clear();
    yield* escapeShaded(g, buf, function (px, py) {
      const u = (px / W - 0.5) * 2 * span, v = (py / H - 0.5) * 2 * span * H / W;
      let zr = u * cs - v * sn, zi = u * sn + v * cs, zr2 = zr * zr, zi2 = zi * zi, i = 0;
      while (i < maxIt && zr2 + zi2 < 256) { zi = 2 * zr * zi + ci; zr = zr2 - zi2 + cr; zr2 = zr * zr; zi2 = zi * zi; i++; }
      if (i >= maxIt) return -1;
      return i + 1 - Math.log(0.5 * Math.log(zr2 + zi2)) / Math.LN2;
    }, 1.5);
  };

  // ---------- mandel: the set that includes its own copies ----------
  const SPOTS = [
    { n: 'the whole set', x: -0.62, y: 0, r: 1.35 },
    { n: 'Seahorse Valley', x: -0.7435, y: 0.1314, r: 0.004 },
    { n: 'Seahorse Valley', x: -0.748, y: 0.1, r: 0.03 },
    { n: 'Elephant Valley', x: 0.2849, y: 0.0123, r: 0.012 },
    { n: 'a double spiral', x: -0.761574, y: -0.0847596, r: 0.0035 },
    { n: 'a minibrot on the needle', x: -1.7549, y: 0, r: 0.035 },
    { n: 'spiral arm', x: -1.25066, y: 0.02012, r: 0.0025 },
    { n: 'northern bulb', x: -0.1011, y: 0.9563, r: 0.006 }
  ];

  ART.mandel = function* (g) {
    const s = g.o.spot != null && !g.o.variant ? SPOTS[g.o.spot] : g.pick(SPOTS), span = s.r * g.rr(0.9, 1.15);
    const rot = s.r > 1 ? g.pick([0, -Math.PI / 2]) : g.rr(0, TAU), cs = Math.cos(rot), sn = Math.sin(rot);
    const buf = g.buffer(Math.min(1, 720 / g.w)), W = buf.W, H = buf.H;
    const maxIt = Math.min(1500, Math.floor(180 + 75 * Math.log2(1.5 / span))), L = g.pal.lut(256);
    g.name = 'Mandelbrot set';
    g.caption = s.n + ', width ' + (span * 2).toPrecision(2);
    g.clear();
    yield* escapeShaded(g, buf, function (px, py) {
      const u = (px / W - 0.5) * 2 * span, v = (py / H - 0.5) * 2 * span * H / W;
      const x0 = s.x + u * cs - v * sn, y0 = s.y + u * sn + v * cs;
      const q = (x0 - 0.25) * (x0 - 0.25) + y0 * y0;
      if (q * (q + (x0 - 0.25)) <= 0.25 * y0 * y0 || (x0 + 1) * (x0 + 1) + y0 * y0 <= 0.0625) return -1;
      let zr = 0, zi = 0, zr2 = 0, zi2 = 0, i = 0;
      while (i < maxIt && zr2 + zi2 < 256) { zi = 2 * zr * zi + y0; zr = zr2 - zi2 + x0; zr2 = zr * zr; zi2 = zi * zi; i++; }
      if (i >= maxIt) return -1;
      return i + 1 - Math.log(0.5 * Math.log(zr2 + zi2)) / Math.LN2;
    }, 1.5);
  };

  // ---------- ifs: parts that are copies of the whole ----------
  function ngonMaps(n, twist, core) {
    let sum = 0;
    for (let k = 1; k <= Math.floor(n / 4); k++) sum += Math.cos(TAU * k / n);
    const r = 1 / (2 + 2 * sum), a = r * Math.cos(twist), c = r * Math.sin(twist), maps = [];
    for (let i = 0; i < n; i++) {
      const vx = Math.cos(TAU * i / n - Math.PI / 2), vy = Math.sin(TAU * i / n - Math.PI / 2);
      maps.push([a, -c, c, a, vx - (a * vx - c * vy), vy - (c * vx + a * vy), 1]);
    }
    if (core) maps.push([a, -c, c, a, 0, 0, 1]);
    return maps;
  }

  ART.ifs = function* (g) {
    const kind = g.o.kind && !g.o.variant ? g.o.kind : g.pick(['fern', 'polygon', 'polygon', 'levy', 'spiral']);
    let maps, label;
    if (kind === 'fern') {
      const curl = g.rr(-0.035, 0.035);
      maps = [[0, 0, 0, 0.16, 0, 0, 0.01], [0.85, 0.04 + curl, -0.04 - curl, 0.85, 0, 1.6, 0.85],
        [0.2, -0.26, 0.23, 0.22, 0, 1.6, 0.07], [-0.15, 0.28, 0.26, 0.24, 0, 0.44, 0.07]];
      label = 'Barnsley fern, 4 maps';
    } else if (kind === 'polygon') {
      const n = g.pick([3, 5, 6, 7, 8]), twist = g.chance(0.5) ? g.rr(0.08, 0.32) * (g.chance(0.5) ? 1 : -1) : 0;
      const core = n >= 5 && g.chance(0.5);
      maps = ngonMaps(n, twist, core);
      label = n + '-gon flake' + (core ? ' with core' : '') + (twist ? ', twist ' + g.f(twist * 180 / Math.PI, 0) + '°' : '');
    } else if (kind === 'levy') {
      maps = [[0.5, 0.5, -0.5, 0.5, 0, 0, 1], [0.5, -0.5, 0.5, 0.5, 0.5, -0.5, 1]];
      label = 'Lévy C curve, 2 maps';
    } else {
      maps = [[0.787879, -0.424242, 0.242424, 0.859848, 1.758647, 1.408065, 0.9],
        [-0.121212, 0.257576, 0.151515, 0.05303, -6.721654, 1.377236, 0.05],
        [0.181818, -0.136364, 0.090909, 0.181818, 6.086107, 1.568035, 0.05]];
      label = 'spiral, 3 maps';
    }
    g.name = 'Iterated function system';
    g.caption = label;

    const m = maps.length, cum = [];
    let tot = 0;
    for (const mp of maps) tot += mp[6];
    let acc = 0;
    for (const mp of maps) { acc += mp[6] / tot; cum.push(acc); }
    const pickMap = function () { const r = g.rnd(); for (let i = 0; i < m; i++) if (r <= cum[i]) return i; return m - 1; };

    let x = 0, y = 0, t = 0.5, minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    for (let i = 0; i < 40000; i++) {
      const mp = maps[pickMap()], nx = mp[0] * x + mp[1] * y + mp[4];
      y = mp[2] * x + mp[3] * y + mp[5]; x = nx;
      if (i > 50) { if (x < minX) minX = x; if (x > maxX) maxX = x; if (y < minY) minY = y; if (y > maxY) maxY = y; }
    }
    const hist = g.hist(Math.min(1, 900 / g.w)), W = hist.W, H = hist.H;
    const span = Math.max(maxX - minX, maxY - minY) * 1.12, sc = Math.min(W, H) / span;
    const ox = W / 2 - (minX + maxX) / 2 * sc, oy = H / 2 + (minY + maxY) / 2 * sc;
    g.clear();
    for (let pass = 0; pass < 28; pass++) {
      for (let i = 0; i < 60000; i++) {
        const k = pickMap(), mp = maps[k], nx = mp[0] * x + mp[1] * y + mp[4];
        y = mp[2] * x + mp[3] * y + mp[5]; x = nx;
        t = (t + (m > 1 ? k / (m - 1) : 0.5)) * 0.5;
        hist.add(ox + x * sc, oy - y * sc, t);
      }
      if (pass % 4 === 3) hist.render(0.72);
      yield;
    }
    hist.render(0.72);
  };

  // ---------- nested: circumpuncts all the way down ----------
  ART.nested = function* (g) {
    const ctx = g.ctx, S = g.S;
    g.clear();
    ctx.globalCompositeOperation = 'lighter';
    const k = g.ri(5, 8), depthMax = g.ri(4, 5), twist = g.rr(-0.7, 0.7), core = g.chance(0.65);
    const sA = Math.sin(Math.PI / k), rho = sA / (1 + sA) * 0.94, coreR = (1 - 2 * sA / (1 + sA)) * 0.9;
    g.name = 'Nested circumpuncts';
    g.caption = k + ' wholes around ' + (core ? 'a core' : 'an open center') + ', ' + depthMax + ' levels';
    const minR = Math.max(2, S / 500);
    let queue = [{ x: g.cx, y: g.cy, r: S * 0.44, d: 0, a: g.rr(0, TAU) }], count = 0;
    while (queue.length) {
      const next = [];
      for (const c of queue) {
        const u = c.d / depthMax;
        ctx.strokeStyle = g.pal.css(0.95 - u * 0.55, 0.85 - u * 0.4);
        ctx.lineWidth = Math.max(0.7, c.r * 0.014);
        ctx.beginPath(); ctx.arc(c.x, c.y, c.r, 0, TAU); ctx.stroke();
        if (c.d < 2) g.glow(c.x, c.y, c.r * 0.22, 0.85, 0.22);
        ctx.fillStyle = g.pal.css(1, 0.9);
        ctx.beginPath(); ctx.arc(c.x, c.y, Math.max(0.8, c.r * 0.035), 0, TAU); ctx.fill();
        if (c.d < depthMax && c.r * rho > minR) {
          const dist = c.r * (1 - sA / (1 + sA));
          for (let i = 0; i < k; i++) {
            const a = c.a + i / k * TAU;
            next.push({ x: c.x + Math.cos(a) * dist, y: c.y + Math.sin(a) * dist, r: c.r * rho, d: c.d + 1, a: a + twist });
          }
          if (core && c.r * coreR > minR) next.push({ x: c.x, y: c.y, r: c.r * coreR, d: c.d + 1, a: c.a + twist * 0.5 });
        }
        if (++count % 180 === 0) yield;
      }
      queue = next;
      yield;
    }
  };

  // ---------- attractor: a path that never repeats ----------
  const CLIFFORD = [[-1.4, 1.6, 1.0, 0.7], [1.7, 1.7, 0.6, 1.2], [1.5, -1.8, 1.6, 0.9], [-1.7, 1.3, -0.1, -1.21],
    [-1.8, -2.0, -0.5, -0.9], [1.6, -0.6, -1.2, 1.6], [-1.3, -1.3, -1.8, -1.9]];
  const DEJONG = [[1.4, -2.3, 2.4, -2.1], [2.01, -2.53, 1.61, -0.33], [-2.7, -0.09, -0.86, -2.2],
    [-2.24, 0.43, -0.65, -2.43], [-2.0, -2.0, -1.2, 2.0]];

  ART.attractor = function* (g) {
    const clifford = g.chance(0.55);
    const p = g.pick(clifford ? CLIFFORD : DEJONG).map(function (v) { return v + g.rr(-0.025, 0.025); });
    const a = p[0], b = p[1], c = p[2], d = p[3];
    g.name = clifford ? 'Clifford attractor' : 'Peter de Jong attractor';
    g.caption = 'a ' + g.f(a) + ', b ' + g.f(b) + ', c ' + g.f(c) + ', d ' + g.f(d);
    let x = 0.1, y = 0.1, minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    const stepOnce = clifford
      ? function () { const nx = Math.sin(a * y) + c * Math.cos(a * x); y = Math.sin(b * x) + d * Math.cos(b * y); x = nx; }
      : function () { const nx = Math.sin(a * y) - Math.cos(b * x); y = Math.sin(c * x) - Math.cos(d * y); x = nx; };
    for (let i = 0; i < 60000; i++) {
      stepOnce();
      if (i > 100) { if (x < minX) minX = x; if (x > maxX) maxX = x; if (y < minY) minY = y; if (y > maxY) maxY = y; }
    }
    const hist = g.hist(Math.min(1, 900 / g.w)), W = hist.W, H = hist.H;
    const span = Math.max(maxX - minX, maxY - minY) * 1.1, sc = Math.min(W, H) / span;
    const ox = W / 2 - (minX + maxX) / 2 * sc, oy = H / 2 - (minY + maxY) / 2 * sc;
    const vmax = span * 0.6;
    g.clear();
    for (let pass = 0; pass < 30; pass++) {
      for (let i = 0; i < 100000; i++) {
        const px = x, py = y;
        stepOnce();
        const v = Math.hypot(x - px, y - py) / vmax;
        hist.add(ox + x * sc, oy + y * sc, v > 1 ? 1 : v);
      }
      if (pass % 4 === 3) hist.render(0.78);
      yield;
    }
    hist.render(0.78);
  };

  // ---------- flow: a field of relationships ----------
  ART.flow = function* (g) {
    const ctx = g.ctx, S = g.S, w = g.w, h = g.h;
    g.clear();
    ctx.globalCompositeOperation = 'lighter';
    ctx.lineCap = 'round';
    const k1 = g.rr(1.2, 3.2) / S, k2 = g.rr(1.2, 3.2) / S, k3 = g.rr(0.8, 2.4) / S;
    const p1 = g.rr(0, TAU), p2 = g.rr(0, TAU), p3 = g.rr(0, TAU), amp = g.rr(0.9, 1.9);
    const vortex = g.chance(0.6) ? g.rr(0.7, 1) * (g.chance(0.5) ? 1 : -1) : 0;
    const N = g.ri(1800, 2600), steps = 80, stepLen = S * 0.0045;
    g.name = 'Flow field';
    g.caption = N.toLocaleString('en-US') + ' streamlines, ' + (vortex ? 'centered vortex' : 'open field');
    const angle = function (x, y) {
      const a = amp * (Math.sin(x * k1 * TAU + p1) + Math.cos(y * k2 * TAU + p2) + Math.sin((x + y) * k3 * TAU + p3));
      if (!vortex) return a;
      const dx = x - g.cx, dy = y - g.cy, r = Math.hypot(dx, dy) / S;
      const wv = Math.min(0.95, Math.exp(-r * r * 5) * Math.abs(vortex));
      const tang = Math.atan2(dy, dx) + Math.sign(vortex) * Math.PI / 2;
      return Math.atan2(Math.sin(a) * (1 - wv) + Math.sin(tang) * wv, Math.cos(a) * (1 - wv) + Math.cos(tang) * wv);
    };
    ctx.lineWidth = Math.max(0.6, S * 0.0016);
    for (let n = 0; n < N; n++) {
      let x = g.rnd() * w, y = g.rnd() * h;
      const t = 0.35 + 0.65 * (1 - Math.min(1, Math.hypot(x - g.cx, y - g.cy) / (S * 0.7)));
      ctx.strokeStyle = g.pal.css(t, 0.13);
      ctx.beginPath(); ctx.moveTo(x, y);
      for (let s = 0; s < steps; s++) {
        const a = angle(x, y);
        x += Math.cos(a) * stepLen; y += Math.sin(a) * stepLen;
        if (x < 0 || y < 0 || x > w || y > h) break;
        ctx.lineTo(x, y);
      }
      ctx.stroke();
      if (n % 40 === 39) yield;
    }
  };

  // Shared with part two.
  window.PlateKit.escape = escape;
  window.PlateKit.escapeShaded = escapeShaded;
  window.PlateKit.gauss = gauss;
})();
