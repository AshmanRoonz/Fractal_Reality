// Plate: an open hand, palm toward you. Outline, skin of cells, veins that branch like a tree,
// palm lines, joint creases and fingertip whorls. "One hand. Several fingers. Skin, joints, cells."
(function () {
  'use strict';
  const ART = window.ART, TAU = Math.PI * 2;

  function chaikin(pts, iters, closed) {
    for (let k = 0; k < iters; k++) {
      const out = closed ? [] : [pts[0]], n = closed ? pts.length : pts.length - 1;
      for (let i = 0; i < n; i++) {
        const p = pts[i], q = pts[(i + 1) % pts.length];
        out.push([p[0] * 0.75 + q[0] * 0.25, p[1] * 0.75 + q[1] * 0.25], [p[0] * 0.25 + q[0] * 0.75, p[1] * 0.25 + q[1] * 0.75]);
      }
      if (!closed) out.push(pts[pts.length - 1]);
      pts = out;
    }
    return pts;
  }

  function lerp(a, b, t) { return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]; }

  // Right hand in palm-width units: origin on the middle knuckle line, y down, thumb toward +x.
  function model(g) {
    const spread = g.rr(0.55, 1.45), curl = g.rr(0.01, 0.06), open = g.rr(-0.1, 0.16);
    const F = [ // knuckle x, knuckle y, angle from vertical (+ toward thumb), length, width
      [0.35, 0.03, 0.13, 0.92, 0.215],    // index
      [0.115, -0.01, 0.03, 1.0, 0.225],   // middle
      [-0.13, 0.025, -0.07, 0.94, 0.21],  // ring
      [-0.355, 0.11, -0.19, 0.74, 0.18]   // little
    ];
    const SEG = [0.48, 0.29, 0.23], LEAN = [-1, -0.2, 0.5, 1];
    const digits = F.map(function (f, i) {
      let x = f[0], y = f[1], a = f[2] * spread + g.rr(-0.025, 0.025);
      const len = f[3] * g.rr(0.97, 1.03), pts = [[x, y]];
      for (let s = 0; s < 3; s++) {
        x += Math.sin(a) * len * SEG[s]; y -= Math.cos(a) * len * SEG[s];
        pts.push([x, y]);
        a += LEAN[i] * curl;
      }
      return { pts: pts, w: [f[4], f[4] * 0.93, f[4] * 0.86] };
    });
    // Thumb: the first segment is the fleshy ball of the thumb over its metacarpal.
    let x = 0.33, y = 0.78, a = 0.78 + open;
    const tp = [[x, y]], TL = [0.4, 0.32, 0.27], TB = [-0.22, -0.18, 0];
    for (let s = 0; s < 3; s++) { x += Math.sin(a) * TL[s]; y -= Math.cos(a) * TL[s]; tp.push([x, y]); a += TB[s]; }
    digits.push({ pts: tp, w: [0.4, 0.25, 0.235], thumb: true });
    const palm = chaikin([[-0.37, 1.8], [-0.4, 1.0], [-0.47, 0.62], [-0.49, 0.3], [-0.45, 0.1], [-0.3, -0.02],
      [-0.02, -0.08], [0.24, -0.06], [0.44, 0], [0.5, 0.22], [0.52, 0.42], [0.47, 0.72], [0.4, 1.0], [0.36, 1.8]], 3, true);
    return { digits: digits, palm: palm };
  }

  ART.hand = function* (g) {
    const ctx = g.ctx, S = g.S, w = g.w, h = g.h, m = model(g);
    const left = g.o.variant ? g.chance(0.5) : !!g.o.left, mirror = left ? -1 : 1, tilt = g.rr(-0.09, 0.09);

    // Fit the hand above the wrist into the plate; the forearm runs off the bottom edge.
    let x0 = Infinity, x1 = -Infinity, y0 = Infinity;
    m.digits.forEach(function (d) {
      d.pts.forEach(function (p, i) {
        const r = d.w[Math.min(i, 2)] / 2;
        x0 = Math.min(x0, p[0] - r); x1 = Math.max(x1, p[0] + r); y0 = Math.min(y0, p[1] - r);
      });
    });
    m.palm.forEach(function (p) { if (p[1] < 1.05) { x0 = Math.min(x0, p[0]); x1 = Math.max(x1, p[0]); } });
    const y1 = 1.05, cxL = (x0 + x1) / 2, cyL = (y0 + y1) / 2;
    const sc = Math.min(h * 0.92 / (y1 - y0), w * 0.86 / (x1 - x0));
    const pcx = g.cx, pcy = h * 0.055 + (y1 - y0) * sc / 2, cs = Math.cos(tilt), sn = Math.sin(tilt);
    const T = function (p) {
      const x = (p[0] - cxL) * mirror, y = p[1] - cyL;
      return [pcx + (x * cs - y * sn) * sc, pcy + (x * sn + y * cs) * sc];
    };
    const digits = m.digits.map(function (d) {
      return { pts: d.pts.map(T), w: d.w.map(function (v) { return v * sc; }), thumb: !!d.thumb };
    });
    const palm = m.palm.map(T);

    const shapes = function (c, grow) {
      c.lineCap = 'round'; c.lineJoin = 'round';
      c.beginPath();
      palm.forEach(function (p, i) { if (i) c.lineTo(p[0], p[1]); else c.moveTo(p[0], p[1]); });
      c.closePath(); c.fill();
      if (grow > 0) { c.lineWidth = grow * 2; c.stroke(); }
      digits.forEach(function (d) {
        for (let s = 0; s < 3; s++) {
          c.lineWidth = d.w[s] + grow * 2;
          c.beginPath(); c.moveTo(d.pts[s][0], d.pts[s][1]); c.lineTo(d.pts[s + 1][0], d.pts[s + 1][1]); c.stroke();
        }
      });
    };
    const layer = function () { const c = document.createElement('canvas'); c.width = w; c.height = h; return c.getContext('2d'); };

    // Body: the union of palm and digits, drawn opaque once so overlaps never double up.
    const body = layer();
    const grad = body.createRadialGradient(pcx, pcy + h * 0.12, 0, pcx, pcy, S * 0.62);
    grad.addColorStop(0, g.pal.css(0.62, 1)); grad.addColorStop(1, g.pal.css(0.3, 1));
    body.fillStyle = body.strokeStyle = grad;
    shapes(body, 0);

    // Outline: the body grown by the rim width, with the body cut out of it.
    const rim = Math.max(1, S * 0.0032), outline = layer();
    outline.fillStyle = outline.strokeStyle = g.pal.css(0.95, 1);
    shapes(outline, rim);
    outline.globalCompositeOperation = 'destination-out';
    outline.fillStyle = outline.strokeStyle = '#000';
    shapes(outline, 0);

    // Low-resolution mask for keeping cells and veins inside the hand.
    const ms = Math.min(1, 420 / w), MW = Math.max(1, Math.round(w * ms)), MH = Math.max(1, Math.round(h * ms));
    const mc = document.createElement('canvas'); mc.width = MW; mc.height = MH;
    const mx = mc.getContext('2d');
    mx.drawImage(body.canvas, 0, 0, MW, MH);
    const md = mx.getImageData(0, 0, MW, MH).data;
    const inside = function (x, y) {
      if (x < 0 || y < 0 || x >= w || y >= h) return false;
      return md[(((y * ms) | 0) * MW + ((x * ms) | 0)) * 4 + 3] > 127;
    };

    // Veins: one trunk from the wrist into each digit, with branches that branch again.
    const trunks = m.digits.map(function (d) {
      const p = d.pts;
      const local = d.thumb
        ? [[0.18, 1.02], [0.3, 0.82], p[1], p[2], lerp(p[2], p[3], 0.7)]
        : [[p[0][0] * 0.3, 1.02], [p[0][0] * 0.75, 0.5], [p[0][0], p[0][1] + 0.05], p[1], p[2], lerp(p[2], p[3], 0.72)];
      return chaikin(local.map(T), 3, false);
    });
    const gens = [[], [], [], []];
    let branches = 0;
    const grow = function (x, y, a, len, d) {
      const x2 = x + Math.cos(a) * len, y2 = y + Math.sin(a) * len;
      if (!inside(x2, y2)) return;
      gens[d].push(x, y, x2, y2); branches++;
      if (d < 3) {
        grow(x2, y2, a - g.rr(0.28, 0.6), len * 0.68, d + 1);
        if (g.chance(0.75)) grow(x2, y2, a + g.rr(0.28, 0.6), len * 0.68, d + 1);
      }
    };
    trunks.forEach(function (tr) {
      let acc = 0, side = g.chance(0.5) ? 1 : -1;
      for (let i = 1; i < tr.length; i++) {
        const ax = tr[i - 1][0], ay = tr[i - 1][1], bx = tr[i][0], by = tr[i][1];
        acc += Math.hypot(bx - ax, by - ay);
        if (acc < S * 0.028) continue;
        acc = 0;
        if (!g.chance(0.7)) continue;
        grow(bx, by, Math.atan2(by - ay, bx - ax) + side * g.rr(0.5, 1.0), S * g.rr(0.028, 0.055), 1);
        side = -side;
      }
    });

    const cells = 5200;
    g.name = 'Open hand';
    g.caption = (left ? 'left' : 'right') + ' palm, 27 bones, ' + branches + ' vein branches, ' + cells.toLocaleString('en-US') + ' cells';

    // 1. Body and outline.
    g.clear();
    ctx.globalCompositeOperation = 'lighter';
    ctx.globalAlpha = 0.13; ctx.drawImage(body.canvas, 0, 0); ctx.globalAlpha = 1;
    ctx.save();
    ctx.shadowColor = g.pal.css(0.85, 0.9); ctx.shadowBlur = S * 0.018;
    ctx.drawImage(outline.canvas, 0, 0);
    ctx.restore();
    yield;

    // 2. Skin: a stipple of cells.
    const dot = Math.max(1, S / 560);
    let made = 0, tries = 0;
    while (made < cells && tries < cells * 14) {
      tries++;
      const x = g.rnd() * w, y = g.rnd() * h;
      if (!inside(x, y)) continue;
      if (made % 200 === 0) ctx.fillStyle = g.pal.css(0.55 + g.rnd() * 0.4, 0.3);
      ctx.fillRect(x, y, dot, dot);
      made++;
      if (made % 650 === 0) yield;
    }

    // 3. Veins, one generation at a time.
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.strokeStyle = g.pal.css(0.8, 0.55);
    ctx.lineWidth = Math.max(1, S * 0.0034);
    trunks.forEach(function (tr) {
      ctx.beginPath();
      tr.forEach(function (p, i) { if (i) ctx.lineTo(p[0], p[1]); else ctx.moveTo(p[0], p[1]); });
      ctx.stroke();
    });
    yield;
    for (let d = 1; d <= 3; d++) {
      const s = gens[d];
      ctx.strokeStyle = g.pal.css(0.78 - d * 0.08, 0.5 - d * 0.09);
      ctx.lineWidth = Math.max(0.6, S * 0.0034 * Math.pow(0.68, d));
      ctx.beginPath();
      for (let i = 0; i < s.length; i += 4) { ctx.moveTo(s[i], s[i + 1]); ctx.lineTo(s[i + 2], s[i + 3]); }
      ctx.stroke();
      yield;
    }

    // 4. Palm lines: heart, head, life.
    const lw = Math.max(1, S * 0.0028);
    const curve = function (P) {
      const q = P.map(T);
      ctx.beginPath(); ctx.moveTo(q[0][0], q[0][1]);
      ctx.bezierCurveTo(q[1][0], q[1][1], q[2][0], q[2][1], q[3][0], q[3][1]);
      ctx.strokeStyle = g.pal.css(0.95, 0.18); ctx.lineWidth = lw * 3.2; ctx.stroke();
      ctx.strokeStyle = g.pal.css(0.95, 0.72); ctx.lineWidth = lw; ctx.stroke();
    };
    curve([[-0.49, 0.27], [-0.12, 0.31], [0.1, 0.14], [0.27, 0.05]]);
    curve([[0.47, 0.35], [0.2, 0.41], [-0.06, 0.47], [-0.36, 0.6]]);
    curve([[0.46, 0.38], [0.16, 0.52], [0.1, 0.86], [0.2, 1.03]]);
    yield;

    // 5. Joint creases and fingertip whorls.
    ctx.strokeStyle = g.pal.css(0.9, 0.55);
    ctx.lineWidth = Math.max(0.8, S * 0.0018);
    const crease = function (p, ux, uy, half, double) {
      const nx = -uy, ny = ux, offs = double ? [-0.012 * sc, 0.012 * sc] : [0];
      offs.forEach(function (o) {
        ctx.beginPath();
        ctx.moveTo(p[0] - nx * half + ux * o, p[1] - ny * half + uy * o);
        ctx.quadraticCurveTo(p[0] + ux * (o + half * 0.2), p[1] + uy * (o + half * 0.2), p[0] + nx * half + ux * o, p[1] + ny * half + uy * o);
        ctx.stroke();
      });
    };
    digits.forEach(function (d) {
      const p = d.pts;
      for (let s = d.thumb ? 1 : 0; s < 3; s++) {
        const dx = p[s + 1][0] - p[s][0], dy = p[s + 1][1] - p[s][1], L = Math.hypot(dx, dy) || 1;
        const at = s === 0 ? lerp(p[0], p[1], 0.2) : p[s];
        crease(at, dx / L, dy / L, d.w[s] * 0.34, s > 0);
      }
    });
    ctx.strokeStyle = g.pal.css(0.9, 0.3);
    ctx.lineWidth = Math.max(0.6, S * 0.0011);
    digits.forEach(function (d) {
      const a = d.pts[2], b = d.pts[3], c = lerp(a, b, 0.55), phi = Math.atan2(b[1] - a[1], b[0] - a[0]), R = d.w[2] * 0.34;
      for (let k = 1; k <= 5; k++) {
        ctx.beginPath(); ctx.ellipse(c[0], c[1], R * k / 5 * 1.3, R * k / 5, phi, 0, TAU); ctx.stroke();
      }
    });
  };
})();
