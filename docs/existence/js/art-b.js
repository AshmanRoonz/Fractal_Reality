// Plates, part two: koch, dragon, phyllotaxis, newton, rings, lightning, rose, pythagoras.
(function () {
  'use strict';
  const ART = window.ART, TAU = Math.PI * 2;
  const escape = window.PlateKit.escape, escapeShaded = window.PlateKit.escapeShaded, gauss = window.PlateKit.gauss;

  // ---------- koch: a boundary drawn with its whole history ----------
  ART.koch = function* (g) {
    const ctx = g.ctx, S = g.S;
    g.clear();
    ctx.globalCompositeOperation = 'lighter';
    ctx.lineJoin = 'round';
    const n = g.pick([3, 3, 4, 5, 6]), deg = g.pick([60, 60, 66, 72, 80]), th = deg * Math.PI / 180;
    const out = g.chance(0.7) ? 1 : -1, D = n <= 4 ? 6 : 5;
    const L = 1 / (2 + 2 * Math.cos(th)), cs = Math.cos(th), sn = Math.sin(th) * out;
    const R0 = S * (out > 0 ? 0.3 : 0.42), rot = g.rr(0, TAU);
    let pts = [];
    for (let i = 0; i < n; i++) {
      const a = rot + i / n * TAU;
      pts.push([g.cx + Math.cos(a) * R0, g.cy + Math.sin(a) * R0]);
    }
    g.name = deg === 60 ? (out > 0 ? 'Koch snowflake' : 'Koch anti-snowflake') : 'Cesàro boundary';
    g.caption = n + '-gon seed, ' + deg + '° bumps, ' + D + ' generations, ' + (n * Math.pow(4, D)).toLocaleString('en-US') + ' edges';

    const trace = function (P) {
      ctx.beginPath();
      ctx.moveTo(P[0][0], P[0][1]);
      for (let i = 1; i < P.length; i++) ctx.lineTo(P[i][0], P[i][1]);
      ctx.closePath();
    };
    for (let d = 0; d <= D; d++) {
      const u = d / D;
      trace(pts);
      if (d === D) { ctx.fillStyle = g.pal.css(0.5, 0.07); ctx.fill(); }
      ctx.strokeStyle = g.pal.css(0.35 + 0.6 * u, 0.14 + 0.76 * u * u);
      ctx.lineWidth = Math.max(0.8, S * (0.006 - 0.0045 * u));
      ctx.stroke();
      yield;
      if (d < D) {
        const Q = [];
        for (let i = 0; i < pts.length; i++) {
          const p = pts[i], q = pts[(i + 1) % pts.length], vx = q[0] - p[0], vy = q[1] - p[1];
          const ax = p[0] + vx * L, ay = p[1] + vy * L;
          Q.push(p, [ax, ay], [ax + L * (vx * cs + vy * sn), ay + L * (vy * cs - vx * sn)], [q[0] - vx * L, q[1] - vy * L]);
        }
        pts = Q;
      }
    }
  };

  // ---------- dragon: a path folded on itself ----------
  ART.dragon = function* (g) {
    const ctx = g.ctx, S = g.S;
    g.clear();
    ctx.globalCompositeOperation = 'lighter';
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    const folds = g.ri(11, 14), copies = g.pick([1, 2, 4]), N = 1 << folds;
    const turn = new Int8Array(N);
    for (let i = 1; i < N; i++) turn[i] = (((i & -i) << 1) & i) ? 1 : 3;
    const DX = [1, 0, -1, 0], DY = [0, 1, 0, -1];
    let minX = 0, maxX = 0, minY = 0, maxY = 0;
    for (let c = 0; c < copies; c++) {
      let x = 0, y = 0, dir = c;
      for (let i = 0; i < N; i++) {
        dir = (dir + turn[i]) & 3; x += DX[dir]; y += DY[dir];
        if (x < minX) minX = x; if (x > maxX) maxX = x; if (y < minY) minY = y; if (y > maxY) maxY = y;
      }
    }
    const s = S * 0.84 / Math.max(maxX - minX, maxY - minY, 1);
    const ox = g.cx - (minX + maxX) / 2 * s, oy = g.cy - (minY + maxY) / 2 * s;
    g.name = 'Heighway dragon';
    g.caption = folds + ' folds, ' + (copies > 1 ? copies + ' interlocking copies, ' : '') + (N * copies).toLocaleString('en-US') + ' segments';
    ctx.lineWidth = Math.max(1, s * 0.42);
    const state = [];
    for (let c = 0; c < copies; c++) state.push({ x: ox, y: oy, dir: c });
    const chunk = 256;
    for (let i0 = 0; i0 < N; i0 += chunk) {
      for (let c = 0; c < copies; c++) {
        const st = state[c];
        ctx.strokeStyle = g.pal.css(0.3 + 0.7 * i0 / N, 0.9);
        ctx.beginPath(); ctx.moveTo(st.x, st.y);
        for (let i = i0; i < Math.min(N, i0 + chunk); i++) {
          st.dir = (st.dir + turn[i]) & 3; st.x += DX[st.dir] * s; st.y += DY[st.dir] * s;
          ctx.lineTo(st.x, st.y);
        }
        ctx.stroke();
      }
      yield;
    }
  };

  // ---------- phyllotaxis: many seeds around one center ----------
  ART.phyllotaxis = function* (g) {
    const ctx = g.ctx, S = g.S, cx = g.cx, cy = g.cy;
    g.clear();
    ctx.globalCompositeOperation = 'lighter';
    const GOLD = 137.50776405, v = g.pick([0, 0, 0, 1, 2]);
    const deg = v === 0 ? GOLD : v === 1 ? GOLD + g.pick([-0.32, -0.14, 0.14, 0.32]) : 99.5025;
    const N = g.ri(1300, 2600), fib = g.pick([13, 21, 34]), c = S * 0.45 / Math.sqrt(N), step = deg * Math.PI / 180;
    g.name = 'Phyllotaxis';
    g.caption = deg.toFixed(3) + '° divergence, ' + N.toLocaleString('en-US') + ' seeds, shaded mod ' + fib;
    for (let i = 0; i < N; i++) {
      const r = c * Math.sqrt(i + 0.5), a = i * step;
      const t = 0.32 + 0.64 * (0.6 * (i % fib) / fib + 0.4 * i / N);
      ctx.fillStyle = g.pal.css(t, 0.85);
      ctx.beginPath(); ctx.arc(cx + Math.cos(a) * r, cy + Math.sin(a) * r, c * (0.2 + 0.24 * Math.sqrt(i / N)), 0, TAU); ctx.fill();
      if (i % 60 === 59) yield;
    }
    g.glow(cx, cy, S * 0.07, 1, 0.5);
  };

  // ---------- newton: basins that converge to a root ----------
  const SUP = ['', '', '²', '³', '⁴', '⁵', '⁶', '⁷'];

  ART.newton = function* (g) {
    const n = g.ri(3, 7), relaxed = g.chance(0.5);
    const ar = relaxed ? g.rr(1.1, 1.6) : 1, ai = relaxed ? g.rr(-0.3, 0.3) : 0;
    const span = g.rr(1.2, 2.1), rot = g.rr(0, TAU), cs = Math.cos(rot), sn = Math.sin(rot);
    const buf = g.buffer(Math.min(1, 720 / g.w)), W = buf.W, H = buf.H, L = g.pal.lut(256), maxIt = 48;
    g.name = 'Newton basins';
    g.caption = 'z' + SUP[n] + ' − 1, ' + n + ' roots' + (relaxed ? ', relaxation ' + g.f(ar) + (ai < 0 ? ' − ' : ' + ') + Math.abs(ai).toFixed(2) + 'i' : '');
    g.clear();
    let root = 0;
    yield* escapeShaded(g, buf, function (px, py) {
      const u = (px / W - 0.5) * 2 * span, w = (py / H - 0.5) * 2 * span * H / W;
      let zr = u * cs - w * sn, zi = u * sn + w * cs, it = 0;
      for (; it < maxIt; it++) {
        let pr = 1, pi = 0;
        for (let k = 0; k < n - 1; k++) { const t = pr * zr - pi * zi; pi = pr * zi + pi * zr; pr = t; }
        const fr = pr * zr - pi * zi - 1, fi = pr * zi + pi * zr, dr = n * pr, di = n * pi, den = dr * dr + di * di;
        if (den < 1e-14) break;
        const qr = (fr * dr + fi * di) / den, qi = (fi * dr - fr * di) / den;
        const sr = ar * qr - ai * qi, si = ar * qi + ai * qr;
        zr -= sr; zi -= si;
        if (sr * sr + si * si < 1e-9) break;
      }
      root = ((Math.round(Math.atan2(zi, zr) / (TAU / n)) % n) + n) % n;
      return it;
    }, 1.3, function (t) { return t * (0.55 + 0.45 * root / (n - 1)); });
  };

  // ---------- rings: centers sharing one field ----------
  ART.rings = function* (g) {
    const ctx = g.ctx, S = g.S, pair = !!g.o.pair;
    const m = pair ? 2 : g.ri(2, 4), C = [];
    for (let i = 0; i < m; i++) {
      const a = pair ? Math.PI * i + g.rr(-0.25, 0.25) : g.rr(0, TAU), r = pair ? 0.17 : g.rr(0.06, 0.3);
      C.push(0.5 + Math.cos(a) * r, 0.5 + Math.sin(a) * r, g.rr(0, TAU));
    }
    const k = g.rr(34, 62) * TAU, decay = g.rr(2.4, 3.8);
    const buf = g.buffer(Math.min(1, 720 / g.w)), W = buf.W, H = buf.H, L = g.pal.lut(256);
    g.name = 'Interference';
    g.caption = (pair ? 'two centers' : m + ' centers') + ', one shared field, ' + Math.round(k / TAU) + ' waves across';
    g.clear();
    yield* escape(buf, function (px, py, d, j) {
      const x = px / W, y = py / H;
      let s = 0;
      for (let i = 0; i < C.length; i += 3) {
        const dist = Math.hypot(x - C[i], y - C[i + 1]);
        s += Math.cos(dist * k + C[i + 2]) * Math.exp(-dist * decay);
      }
      let t = (s / m) * 0.5 + 0.5;
      t = t * t * t * t;
      const q = (Math.min(1, t * 1.6) * 255) | 0;
      d[j] = L[q * 3]; d[j + 1] = L[q * 3 + 1]; d[j + 2] = L[q * 3 + 2]; d[j + 3] = 255;
    });
    ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < C.length; i += 3) {
      const x = C[i] * g.w, y = C[i + 1] * g.h;
      ctx.strokeStyle = g.pal.css(0.95, 0.7);
      ctx.lineWidth = Math.max(1, S * 0.0025);
      ctx.beginPath(); ctx.arc(x, y, S * 0.05, 0, TAU); ctx.stroke();
      g.glow(x, y, S * 0.035, 1, 0.9);
    }
  };

  // ---------- lightning: many paths converging on one center ----------
  ART.lightning = function* (g) {
    const ctx = g.ctx, S = g.S, cx = g.cx, cy = g.cy;
    g.clear();
    ctx.globalCompositeOperation = 'lighter';
    ctx.lineJoin = 'round'; ctx.lineCap = 'round';
    const n = g.ri(6, 13), R = S * 0.47, rough = g.rr(0.12, 0.2), branchP = g.rr(0.04, 0.09), rot = g.rr(0, TAU);
    let branches = 0;
    g.name = 'Convergence';

    const bolt = function (x1, y1, x2, y2, levels) {
      let cur = [[x1, y1], [x2, y2]];
      for (let l = 0; l < levels; l++) {
        const next = [cur[0]];
        for (let i = 1; i < cur.length; i++) {
          const a = cur[i - 1], b = cur[i], dx = b[0] - a[0], dy = b[1] - a[1], len = Math.hypot(dx, dy) || 1;
          const off = gauss(g) * rough * len;
          next.push([(a[0] + b[0]) / 2 - dy / len * off, (a[1] + b[1]) / 2 + dx / len * off], b);
        }
        cur = next;
      }
      return cur;
    };
    const stroke = function (P, wide, thin, t, alpha) {
      ctx.beginPath(); ctx.moveTo(P[0][0], P[0][1]);
      for (let i = 1; i < P.length; i++) ctx.lineTo(P[i][0], P[i][1]);
      ctx.strokeStyle = g.pal.css(t, alpha * 0.12); ctx.lineWidth = wide; ctx.stroke();
      ctx.strokeStyle = g.pal.css(Math.min(1, t + 0.1), alpha); ctx.lineWidth = thin; ctx.stroke();
    };

    ctx.strokeStyle = g.pal.css(0.6, 0.25); ctx.lineWidth = Math.max(1, S * 0.0015);
    ctx.beginPath(); ctx.arc(cx, cy, R, 0, TAU); ctx.stroke();
    for (let b = 0; b < n; b++) {
      const a = rot + (b + g.rr(-0.3, 0.3)) / n * TAU;
      const P = bolt(cx + Math.cos(a) * R, cy + Math.sin(a) * R, cx, cy, 7);
      stroke(P, S * 0.014, Math.max(1, S * 0.0024), 0.82, 0.9);
      for (let i = 8; i < P.length - 24; i++) {
        if (!g.chance(branchP)) continue;
        const p = P[i], q = P[i + 4], dir = Math.atan2(q[1] - p[1], q[0] - p[0]) + g.pick([-1, 1]) * g.rr(0.35, 0.9);
        const len = Math.hypot(p[0] - cx, p[1] - cy) * g.rr(0.18, 0.45);
        stroke(bolt(p[0], p[1], p[0] + Math.cos(dir) * len, p[1] + Math.sin(dir) * len, 5), S * 0.008, Math.max(0.7, S * 0.0013), 0.6, 0.6);
        branches++;
      }
      g.caption = n + ' paths, ' + branches + ' branches, one center';
      yield;
    }
    g.glow(cx, cy, S * 0.12, 0.9, 0.45);
    g.glow(cx, cy, S * 0.03, 1, 1);
  };

  // ---------- rose: relationships drawn across a circle ----------
  ART.rose = function* (g) {
    const ctx = g.ctx, S = g.S, cx = g.cx, cy = g.cy, R = S * 0.43;
    g.clear();
    ctx.globalCompositeOperation = 'lighter';
    const lw = Math.max(0.8, S * 0.0012);
    ctx.strokeStyle = g.pal.css(0.6, 0.4); ctx.lineWidth = lw * 1.4;
    ctx.beginPath(); ctx.arc(cx, cy, R, 0, TAU); ctx.stroke();
    const P = function (a, r) { return [cx + Math.cos(a - Math.PI / 2) * r, cy + Math.sin(a - Math.PI / 2) * r]; };

    if (g.chance(0.55)) {
      const N = g.pick([200, 240, 300, 360]), m = g.pick([2, 3, 4, 5, 7, 10, 13, 21, 34, 51, 68, 99]);
      g.name = 'Times table on a circle';
      g.caption = N + ' points, each joined to its ×' + m;
      ctx.fillStyle = g.pal.css(0.9, 0.9);
      for (let i = 0; i < N; i++) { const p = P(i / N * TAU, R); ctx.fillRect(p[0] - lw, p[1] - lw, lw * 2, lw * 2); }
      ctx.lineWidth = lw;
      for (let i = 0; i < N; i++) {
        const a = P(i / N * TAU, R), b = P(((i * m) % N) / N * TAU, R);
        ctx.strokeStyle = g.pal.css(0.4 + 0.6 * i / N, 0.38);
        ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke();
        if (i % 8 === 7) yield;
      }
    } else {
      const n = g.ri(2, 7), d = g.pick([29, 31, 37, 39, 43, 47, 59, 71, 79, 97]);
      g.name = 'Maurer rose';
      g.caption = 'n = ' + n + ', d = ' + d + '°, 361 chords';
      ctx.lineWidth = lw;
      let prev = P(0, 0);
      for (let k = 1; k <= 360; k++) {
        const th = k * d * Math.PI / 180, p = P(th, R * Math.sin(n * th));
        ctx.strokeStyle = g.pal.css(0.4 + 0.55 * k / 360, 0.5);
        ctx.beginPath(); ctx.moveTo(prev[0], prev[1]); ctx.lineTo(p[0], p[1]); ctx.stroke();
        prev = p;
        if (k % 8 === 0) yield;
      }
      ctx.strokeStyle = g.pal.css(1, 0.85); ctx.lineWidth = lw * 1.8;
      ctx.beginPath();
      for (let k = 0; k <= 720; k++) {
        const th = k / 2 * Math.PI / 180, p = P(th, R * Math.sin(n * th));
        if (k) ctx.lineTo(p[0], p[1]); else ctx.moveTo(p[0], p[1]);
      }
      ctx.stroke();
    }
    g.glow(cx, cy, S * 0.025, 1, 0.9);
  };

  // ---------- pythagoras: every square carries two more ----------
  ART.pythagoras = function* (g) {
    const ctx = g.ctx, S = g.S;
    g.clear();
    ctx.globalCompositeOperation = 'lighter';
    ctx.lineJoin = 'round';
    const deg = g.ri(28, 62), al = deg * Math.PI / 180, ca = Math.cos(al), sa = Math.sin(al), depth = g.ri(10, 12);
    let level = [[-0.5, 0, 0.5, 0]], minX = -0.5, maxX = 0.5, minY = -1, maxY = 0;
    const levels = [];
    for (let d = 0; d <= depth; d++) {
      const sq = [], next = [];
      for (const b of level) {
        const x0 = b[0], y0 = b[1], x1 = b[2], y1 = b[3], vx = x1 - x0, vy = y1 - y0;
        const x2 = x1 + vy, y2 = y1 - vx, x3 = x0 + vy, y3 = y0 - vx;
        sq.push([x0, y0, x1, y1, x2, y2, x3, y3]);
        const ax = x3 + (vx * ca + vy * sa) * ca, ay = y3 + (-vx * sa + vy * ca) * ca;
        next.push([x3, y3, ax, ay], [ax, ay, x2, y2]);
        minX = Math.min(minX, x2, x3); maxX = Math.max(maxX, x2, x3);
        minY = Math.min(minY, y2, y3); maxY = Math.max(maxY, y2, y3);
      }
      levels.push(sq);
      level = next;
    }
    const s = S * 0.88 / Math.max(maxX - minX, maxY - minY);
    const ox = g.cx - (minX + maxX) / 2 * s, oy = g.cy - (minY + maxY) / 2 * s;
    const total = Math.pow(2, depth + 1) - 1;
    g.name = 'Pythagoras tree';
    g.caption = deg + '°, ' + (depth + 1) + ' generations, ' + total.toLocaleString('en-US') + ' squares';
    ctx.lineWidth = Math.max(0.7, S * 0.001);
    for (let d = 0; d < levels.length; d++) {
      const t = 0.25 + 0.72 * d / depth;
      ctx.beginPath();
      for (const q of levels[d]) {
        ctx.moveTo(ox + q[0] * s, oy + q[1] * s);
        ctx.lineTo(ox + q[2] * s, oy + q[3] * s);
        ctx.lineTo(ox + q[4] * s, oy + q[5] * s);
        ctx.lineTo(ox + q[6] * s, oy + q[7] * s);
        ctx.closePath();
      }
      ctx.fillStyle = g.pal.css(t, 0.16); ctx.fill();
      ctx.strokeStyle = g.pal.css(t, 0.6); ctx.stroke();
      yield;
    }
  };
})();
