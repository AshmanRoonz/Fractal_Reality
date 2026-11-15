"""An input at the 0 from beyond the whole. Predictions frozen before any lattice run of this script.

Created: 2026-11-05
Last updated: 2026-11-05
Version: 1.0
History: 2026-11-05 v1.0: initial, after Ashman said yes to testing an input at the 0 from beyond the whole. The theory is a Claude Doc, https://claude.ai/artifact/58ahYtFyKbQtDHEggdvEte

Results: V1, V3, V6 passed; V2, V4, V5, V7, V8 missed. V1: amplitude at the zero site about 1e-19, with gain times 10 too. V3: fed whole out, .008; back with the input in 0 of 8 seeds with winding 1; self-powered .957. V4: slope .401, .491, .631, .722, .718, .221, -.015, -.039, -.041 at Gc = 0, .5, 1, 1.25, 1.5, 2, 2.5, 4, 8, G = 2, winding 1 in every seed. V5: drift above no turn bare .0334, depleted .1744, rich -.0110. V6: core to r = 24 at t = 230, share .572; edge to r = 8 at t = 492, share .458. V7: far rate moved .01 to .07 of the difference for input above the whole's rate, .16 to .53 below; at size 3 the zero sat at r about 3.8 with winding 1 in every seed.
After the follow-ups: F1, F2 passed. F1: extent 8 at Gc = 2.5, 3, 3.5, 4, 6, peak .981 to 1.002, so the threshold is between 2 and 2.5. F2: winding 0 in every seed.
Totals: 10 frozen, 5 passed, 5 missed. No real system was measured, and from beyond the whole only means a term with no source among the parts.

Needs numpy. All data are synthetic.
Run: python -I wholeness_input_v1.py OUTDIR [solve deficit zero fed cutoff direction signal arrival phased birth f1 f2]
"solve" prints numbers from a radial reduction, and was run before the predictions were written. It simulates no lattice sites.

WHY. wholeness_flow_v1.py found phase lines going in and signal coming out round a single 0, with every part powering itself. Canon opens the aperture directly onto infinity: "The future arrives at the center directly from infinity, through no channel at all", and "its only variable is how open it is". So what can come in there, and what does it do?

HAND DERIVATIONS.
(a) Nothing without a phase can enter at the 0 itself. Input with no phase of its own acts as a gain, and gain times 0 is 0. Input with a phase is additive, and it moves the zero off that spot; the charge stays, so it does not fill the 0. So what is undifferentiated cannot land exactly there. It can only act on the parts right around it. Canon's "a meeting has no width" fits, as a reading.
(b) A point input cannot make a 0. Charge is a loop's property, and a source at one place has no turn round it. So no seed, no 0. Only a closed turn gives one, as in wholeness_zero_v1.py.
(c) A whole fed only through its centre. Parts below their own hold, G < 1, with a core r < 4 at gain Gc. Parts then answer linearly and fall off over xi = .5 sqrt(G / (1 - G)). Radial solver: extent to 10% of peak 6, 6, 7, 9 at G = .8, .9, .95, .99, Gc = 4, with xi 1.0, 1.5, 2.2, 5.0. So such a whole stays about the size of its centre. Openness, G = .95: below Gc about 1.15 nothing holds. Above it the extent stays 7 and only the peak rises, .24, .53, .76, .93, .999, 1.0 at Gc = 1.2, 1.3, 1.5, 2, 4, 8. So opening the aperture wider makes this whole brighter and not larger. With the energy turn on, a fed whole is smaller still, since the turning field falls off in under a site: lambda^2 = (4 / G)(1 - G + i rate).
(d) Stop the input. A fed whole goes out. A whole with parts that hold itself does not notice.
(e) I expected an input at the core to drive flow. The solver says the opposite, G = 2, c = 1. Slope of the phase at r = 10 to 25, and drift above no turn: Gc = 0: .30, .048. Gc = .5: .35, .057. Gc = 1: .49, .089. Gc = 1.25: .59, .12. Gc = 1.5: .74, .18. Gc = 2, the bare 0: .27, .043. Gc = 2.2: .04, .007. Gc = 2.5: 0, 0. Gc = 4: -.03, -.008. So a core with more than its field stops the flow, within 25% extra gain, and a core with less carries more of it. The reason, after the fact: a part's rate is its energy and waves here can only run below the bulk rate, so a bare or depleted core has a slower rate to pull phase lines in, and a rich core is only screened. The small negative slope is a tail, not a wave. Some cells between Gc = 1.75 and 2 and at G = 3 are jumpy or not locked, so I do not lean on those. G = 3, c = 2: Gc = 3: .088; Gc = 8: -.011.
(f) Arrival. Radial, G = 2, c = 1: a step of -.05 in rate at r < 3 reaches r = 24 half way at t = 239, share .694. The same step at r >= 28 reaches r = 8 at t = 497, share .560.
(g) An input with a phase and a clock of its own. No solver, since it breaks the symmetry. From the derivation above: a small one moves the zero a little and leaves the far rate alone, since a zero circling inside a far loop does not change the far winding.
Reading to test, not a result. A centre carries flow by having less, not more. This is one law I chose, and "from beyond the whole" here only means a term with no source among the parts.

PREDICTIONS. Noise .02, input spread .05. Disk radius 32 except where stated. Core r < 4.
V1. Radius 16, zero on a site, no noise, c = 1, G = 2. Gain at that site times 1 and 10: its amplitude <= 1e-9. An input with a phase there, size .2: amplitude >= .05, winding round it still 1.
V2. Fed whole, no turn, run 1000. Extent within 25% or 1.5 sites of the radial number, cells (G, Gc): (.8, 4), (.9, 4), (.95, 4), (.99, 4), (.95, 1.5), (.95, 2), (.95, 8); winding 1 at r = 5 in at least 75%. (.95, 1.1): peak <= .15.
V3. Stop the input, G = .95: reading at r = 3 <= .05. G = 2: reading at r = 8 >= .5, winding 1 in at least 90%. Input back after fading: reported.
V4. Flow against the core's gain, run 1500. Cells (G, Gc, c): (2, 0, 1), (2, .5, 1), (2, 1, 1), (2, 1.25, 1), (2, 2, 1), (2, 2.5, 1), (2, 4, 1), (2, 8, 1), (2, 4, -1), (3, 3, 2), (3, 8, 2). Winding 1 at r = 8 in at least 75%. Slope over r = 10 to 25 within 30% or .03 of radial. (2, 1.5, 1) reported only. Fed, (.95, 4, 1), no noise: slope over r = 4 to 7 within 30% of radial, rate within 5%, phase outward.
V5. Signal, no noise, drift above no turn: (2, 1.25, 1) at least 1.5 times the bare (2, 2, 1); (2, 4, 1) at most .01 in size.
V6. Arrival, as (f): core sooner than edge; each time and share within 50% of radial.
V7. Input with a phase, G = 2, c = 1, rate .05 either side of the whole's. Size .1, .3: far rate moves at most .25 of the difference, zero within 4 of the centre, winding 1 at r = 16 in at least 75%. Size 1, 3 reported.
V8. No seed, radius 16, G = .95. Input with a phase at r < 2: winding 0 at r = 5 in at least 90%. Active core from noise: wound in .1 to .7 of 64 seeds.

ADDED AFTER SEEING THE RESULTS ABOVE, predictions frozen before these ran. Seen so far: V1, V3, V6 passed; V2, V4, V5, V7, V8 missed. V2: at G = .95 the wound core went out at Gc = 1.5 and 2, peak about .01, where radial had .76 and .93. V4: slope .401 and .491 at Gc = 0, .5 against radial .301 and .354, the other cells within the bar. V5: rich core -.0110 against a bar of .01. V7: size .3, rate below the whole's: .44 of the difference against .25. V8: first clause .27 against .9; second .03 against .1 to .7.
F1. V2's miss is the radial solver's small core, which has only three radial points. On the lattice the wound core needs more gain. G = .95, Gc = 2.5, 3, 3.5, 4, 6: a threshold lies between 2 and 4; above it the extent stays within 1.5 sites of 8, and the peak does not fall as Gc rises.
F2. V8's first clause read noise, since at r = 5 the input has faded to the noise floor. Noise a tenth as large, reading at r = 3: winding 0 in at least 90%.
"""
import json
import os
import sys
import time
from math import pi, sqrt, tanh
from multiprocessing import Pool
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np

DT = .05
SIGMA = .02
SPREAD = .05
RC = 4


def seed_of(*v):
    return np.random.default_rng([abs(int(round(a * 1000))) for a in v])


def verdict(ok):
    return "PASS" if ok else "MISS"


def wrap(a):
    return (a + pi) % (2 * pi) - pi


def lim(w):
    a = np.abs(w)
    return np.tanh(a) * w / np.maximum(a, 1e-12)


def cnoise(rng, shape):
    return rng.standard_normal(shape) + 1j * rng.standard_normal(shape)


def rest(G):
    if G <= 1:
        return 0.0
    m = 1.0
    for _ in range(20000):
        m = tanh(G * m)
    return m


def winding(z):
    a = np.angle(z)
    return np.rint(wrap(np.roll(a, -1, axis=-1) - a).sum(-1) / (2 * pi)).astype(int)


# ---------- Radial reduction: no lattice sites ----------
def radial(gmap, c, R=32, T=1500.0, dw=None, f0=None):
    r = np.arange(1, R + 1, dtype=float)
    f = (.9 * np.tanh(r / 2) * np.exp(-np.maximum(r - RC, 0) / 8) + 0j) if f0 is None else f0.copy()
    g = gmap(r)
    d = np.zeros(R) if dw is None else dw(r)
    for _ in range(int(T / DT)):
        h = np.r_[0, f, f[-1]]
        lap = h[2:] - 2 * f + h[:-2] + (h[2:] - h[:-2]) / (2 * r) - f / r ** 2
        f = f + DT * (-f + lim(g * (f + .25 * lap)))
        f = f * np.exp(1j * DT * (c * np.abs(f) ** 2 + d))
    return r, f


def rad_rate(gmap, c, f, R=32, at=(8, 24), dw=None):
    a0 = np.angle(f[[x - 1 for x in at]])
    tot = np.zeros(len(at))
    g = f.copy()
    for _ in range(int(20 / DT)):
        _r, g = radial(gmap, c, R, DT, dw, g)
        a1 = np.angle(g[[x - 1 for x in at]])
        tot = tot + wrap(a1 - a0)
        a0 = a1
    return tot / 20


def rad_slope(r, f, lo, hi):
    sel = (r >= lo) & (r <= hi)
    return float(np.polyfit(r[sel], np.unwrap(np.angle(f[sel])), 1)[0])


def rad_extent(r, f):
    a = np.abs(f)
    pk = a.max()
    i = int(np.argmax(a))
    below = np.where(a[i:] <= .1 * pk)[0]
    return float(r[i + below[0]]) if len(below) else float(r[-1])


def patch(Gp, Gc):
    return lambda r, a=Gp, b=Gc: np.where(r < RC, b, a)


def rad_arrival(where, c=1.0, G=2.0, dw0=-.05, R=32, at=24):
    """A step shift in rate at the core, or at the edge. Time for the far rate to go half way to its final shift."""
    gm = lambda r, g=G: np.full_like(r, g)
    r, f = radial(gm, c, R, 1500)
    if where == "core":
        dw = lambda r, d=dw0: d * (r < 3)
    else:
        dw = lambda r, d=dw0: d * (r >= 28)
    idx = at - 1
    a0 = np.angle(f[idx])
    rates = []
    g = f.copy()
    for t in range(3000):
        _r, g = radial(gm, c, R, 1.0, dw, g)
        a1 = np.angle(g[idx])
        rates.append(wrap(a1 - a0))
        a0 = a1
    rates = np.array(rates)
    base = rad_rate(gm, c, f, R, (at,))[0]
    final = rates[-100:].mean()
    change = final - base
    if abs(change) < 1e-4:
        return float("inf"), float(change / dw0)
    frac = (rates - base) / change
    w = np.convolve(frac, np.ones(20) / 20, mode="valid")
    idxs = np.where(w >= .5)[0]
    return float(idxs[0]) if len(idxs) else float("inf"), float(change / dw0)


def rad_pulse(gmap, c, R=32, T=2000.0, r0=14, delta=.2):
    r, f = radial(gmap, c, R, T)
    p = f * np.exp(1j * delta * (np.abs(r - r0) <= 1))
    fa, fb = f.copy(), p.copy()
    cen = {}
    for tt in range(1, 61):
        r, fa = radial(gmap, c, R, 1.0, None, fa)
        r, fb = radial(gmap, c, R, 1.0, None, fb)
        d = np.abs(wrap(np.angle(fb) - np.angle(fa)))
        cen[tt] = float((r * r * d).sum() / (r * d).sum())
    ts = np.arange(20, 61)
    return float(np.polyfit(ts, [cen[t] for t in ts], 1)[0])


def solve_deficit():
    print("Deficit: core r < 4 at Gc, parts at G, c. Slope over 10 to 25, rates at r = 8, 24, drift above no turn")
    for G, c in ((2.0, 1.0), (3.0, 2.0)):
        base = rad_pulse(lambda r, g=G: np.full_like(r, g), 0.0)
        for Gc in (0.0, .5, 1.0, 1.25, 1.5, 1.75, 1.9, 2.0, 2.2, 2.5, 3.0, 4.0, 8.0):
            gm = patch(G, Gc)
            r, f = radial(gm, c, T=2500)
            rt = rad_rate(gm, c, f)
            k = rad_slope(r, f, 10, 25)
            k2 = rad_slope(r, f, 18, 28)
            v = rad_pulse(gm, c)
            print(f"  G {G:g}, c {c:g}, Gc {Gc:g}: slope {k:.4f}, further out {k2:.4f}; rates {rt[0]:.4f}, {rt[1]:.4f}; drift above no turn {v-base:.4f}", flush=True)


def solve():
    print("Fed whole: parts at G, core r < 4 at Gc = 4, no turn. Extent to 10% of peak; xi = .5 sqrt(G / (1 - G))")
    for G in (.8, .9, .95, .99):
        xi = .5 * sqrt(G / (1 - G))
        r, f = radial(patch(G, 4.0), 0.0)
        print(f"  G {G:g}: extent {rad_extent(r, f):.1f}; xi {xi:.2f}; peak {np.abs(f).max():.3f}; amplitude at r = 8: {np.abs(f[7]):.4f}", flush=True)
    print("Openness: parts at G .95, core Gc. Extent and peak")
    for Gc in (1.0, 1.1, 1.2, 1.3, 1.5, 2.0, 4.0, 8.0):
        r, f = radial(patch(.95, Gc), 0.0)
        print(f"  Gc {Gc:g}: extent {rad_extent(r, f):.1f}; peak {np.abs(f).max():.4f}", flush=True)
    print("Direction: core r < 4 at Gc, parts at G, c. Slope over 5 to 12 (fed) or 10 to 25 (self-powered), rate at r = 8, 24, direction")
    for G, Gc, c in ((.9, 4.0, 1.0), (.95, 4.0, 1.0), (.99, 4.0, 1.0), (.95, 4.0, 2.0), (.95, 4.0, -1.0), (2.0, 2.0, 1.0), (2.0, 2.2, 1.0), (2.0, 2.5, 1.0), (2.0, 3.0, 1.0), (2.0, 4.0, 1.0), (2.0, 8.0, 1.0), (2.0, 4.0, -1.0), (2.0, 1.8, 1.0), (2.0, 1.5, 1.0), (3.0, 3.0, 2.0), (3.0, 8.0, 2.0), (3.0, 1.5, 2.0)):
        gm = patch(G, Gc)
        r, f = radial(gm, c, T=2500)
        rt = rad_rate(gm, c, f)
        lo, hi = (5, 12) if G < 1 else (10, 25)
        k = rad_slope(r, f, lo, hi)
        print(f"  G {G:g}, Gc {Gc:g}, c {c:g}: slope {k:.4f}; rates {rt[0]:.4f}, {rt[1]:.4f}; phase {'inward' if rt[0]*k>0 else 'outward'}; amplitude at 8, 24: {np.abs(f[7]):.3f}, {np.abs(f[23]):.3f}", flush=True)
    print("Arrival: step of -.05 in rate at r < 3 read at r = 24; or at r >= 28 read at r = 8; G 2, c 1")
    t1, s1 = rad_arrival("core", at=24)
    print(f"  core to r 24: half way at t = {t1:.0f}; final share {s1:.3f}", flush=True)
    t2, s2 = rad_arrival("edge", at=8)
    print(f"  edge to r 8: half way at t = {t2:.0f}; final share {s2:.3f}", flush=True)


# ---------- Disk ----------
class Disk:
    def __init__(self, R=32, cx=.5, cy=.5):
        self.R = R
        L = 2 * R + 2
        y, x = np.mgrid[0:L, 0:L]
        self.x, self.y = x - R + 0.0, y - R + 0.0
        self.mask = (self.x - cx) ** 2 + (self.y - cy) ** 2 < R * R
        self.phi = np.arctan2(self.y - cy, self.x - cx)
        self.rad = np.hypot(self.x - cx, self.y - cy)
        self.adj = []
        for ax, sh in ((0, 1), (0, -1), (1, 1), (1, -1)):
            self.adj.append((ax, sh, self.mask & np.roll(self.mask, sh, axis=ax)))
        self.cnt = sum(a.astype(float) for _x, _s, a in self.adj)

    def placed(self, B, rng, fall=8.0, spread=SPREAD):
        amp = .9 * np.tanh(self.rad / 2) * np.exp(-np.maximum(self.rad - RC, 0) / fall)
        z = amp * np.exp(1j * self.phi)
        return (z[None] + spread * cnoise(rng, (B, *self.x.shape))) * self.mask

    def reading(self, z):
        s = 0
        for ax, sh, a in self.adj:
            s = s + np.roll(z, sh, axis=ax + 1) * a
        return s / np.maximum(self.cnt, 1)

    def run(self, z, G, T, rng, c=0.0, dw=None, src=None, srcrate=0.0, t0=0.0, sigma=SIGMA):
        d = 0 if dw is None else dw
        for i in range(int(T / DT)):
            z = z + DT * (-z + lim(G * self.reading(z)))
            z = z * np.exp(1j * DT * (c * np.abs(z) ** 2 + d))
            if src is not None:
                z = z + DT * src * np.exp(1j * srcrate * (t0 + i * DT))
            if sigma:
                z = z + sqrt(DT) * sigma * cnoise(rng, z.shape)
            z = z * self.mask
        return z

    def annulus(self, z, r):
        sel = self.mask & (np.abs(self.rad - r) <= .5)
        return (z * np.exp(-1j * self.phi) * sel).sum((1, 2)) / sel.sum()

    def profile(self, z, rmax=None):
        rs = np.arange(1, (rmax or self.R - 1))
        return rs, np.stack([self.annulus(z, r) for r in rs], axis=1)

    def loop(self, z, h):
        pts = []
        cx, cy = self.R, self.R
        for i in range(-h, h):
            pts.append((cy - h, cx + i))
        for i in range(-h, h):
            pts.append((cy + i, cx + h))
        for i in range(-h, h):
            pts.append((cy + h, cx - i))
        for i in range(-h, h):
            pts.append((cy - i, cx - h))
        return winding(np.stack([z[:, p[0], p[1]] for p in pts], axis=1))

    def zero_pos(self, z):
        """Plaquette with a nonzero charge and the largest amplitude around it, nearest the centre."""
        a = np.angle(z)
        d1 = wrap(np.roll(a, -1, axis=2) - a)
        d2 = wrap(np.roll(np.roll(a, -1, axis=2), -1, axis=1) - np.roll(a, -1, axis=2))
        d3 = wrap(np.roll(a, -1, axis=1) - np.roll(np.roll(a, -1, axis=2), -1, axis=1))
        d4 = wrap(a - np.roll(a, -1, axis=1))
        ch = np.rint((d1 + d2 + d3 + d4) / (2 * pi)).astype(int)
        m = self.mask
        ok = m & np.roll(m, -1, 1) & np.roll(m, -1, 0) & np.roll(np.roll(m, -1, 1), -1, 0)
        ch = ch * ok
        out = []
        for b in range(z.shape[0]):
            pos = np.argwhere(ch[b] != 0)
            if len(pos) == 0:
                out.append((float("inf"), 0))
            else:
                ds = [float(self.rad[p[0], p[1]]) for p in pos]
                out.append((min(ds), len(pos)))
        return out

    def measure(self, z, G, rng, c, lo, hi, r0=8, r1=24, dw=None, sigma=SIGMA):
        rs = np.arange(lo, hi + 1)
        a = np.stack([self.annulus(z, r) for r in rs], axis=1)
        k = np.array([np.polyfit(rs, np.unwrap(np.angle(a[b])), 1)[0] for b in range(z.shape[0])])
        a0 = np.stack([np.angle(self.annulus(z, r)) for r in (r0, r1)])
        tot = np.zeros_like(a0)
        y = z
        for _ in range(int(20 / DT)):
            y = self.run(y, G, DT, rng, c, dw, sigma=sigma)
            a1 = np.stack([np.angle(self.annulus(y, r)) for r in (r0, r1)])
            tot = tot + wrap(a1 - a0)
            a0 = a1
        return k, tot / 20


def job_zero(_o):
    """V1."""
    ok = True
    d = Disk(16, 0.0, 0.0)
    c0 = (d.rad == 0)
    rng = seed_of(1, 1)
    for mult in (1.0, 10.0):
        G = np.where(c0, 2.0 * mult, 2.0)
        z = d.placed(1, rng, fall=1e9, spread=0.0)
        z = d.run(z, G, 100, rng, 1.0, sigma=0.0)
        v = float(np.abs(z[0][c0]).max())
        ok &= v <= 1e-9
        print(f"  Gain at the zero site times {mult:g}: amplitude there {v:.2e}", flush=True)
    src = .2 * c0
    z = d.placed(1, rng, fall=1e9, spread=0.0)
    z = d.run(z, np.full_like(d.rad, 2.0), 100, rng, 1.0, src=src, srcrate=.9, sigma=0.0)
    v = float(np.abs(z[0][c0]).max())
    h = d.loop(z, 8)
    good = v >= .05 and (h == 1).all()
    ok &= good
    print(f"  An input with a phase at the zero site: amplitude there {v:.3f}; winding round it {h.tolist()}; {verdict(good)}", flush=True)
    return ok


def fed_cell(job):
    G, Gc, c = job
    d = Disk(32)
    rng = seed_of(2, G, Gc, c)
    gm = np.where(d.rad < RC, Gc, G)
    z = d.placed(4, rng)
    z = d.run(z, gm, 1000, rng, c)
    rs, a = d.profile(z)
    amp = np.abs(a).mean(0)
    i = int(np.argmax(amp))
    below = np.where(amp[i:] <= .1 * amp[i])[0]
    ext = float(rs[i + below[0]]) if len(below) else float(rs[-1])
    w = d.loop(z, 5)
    return G, Gc, c, ext, float(amp[i]), float(np.mean(w == 1))


def job_fed(_o):
    """V2."""
    ok = True
    cells = [(.8, 4.0, 0.0), (.9, 4.0, 0.0), (.95, 4.0, 0.0), (.99, 4.0, 0.0), (.95, 1.5, 0.0), (.95, 2.0, 0.0), (.95, 8.0, 0.0), (.95, 1.1, 0.0)]
    with Pool(8) as p:
        res = p.map(fed_cell, cells)
    for G, Gc, c, ext, pk, w in res:
        r, f = radial(patch(G, Gc), c)
        re, rp = rad_extent(r, f), float(np.abs(f).max())
        if rp < .05:
            good = pk <= .15
        else:
            good = abs(ext - re) <= max(.25 * re, 1.5) and w >= .75
        ok &= good
        print(f"  G {G:g}, Gc {Gc:g}: extent {ext:.1f} (radial {re:.1f}); peak {pk:.3f} (radial {rp:.3f}); winding 1 at r = 5 in {w:.2f}; {verdict(good)}", flush=True)
    return ok


def job_cutoff(_o):
    """V3."""
    ok = True
    d = Disk(32)
    for G, lab in ((.95, "fed"), (2.0, "self-powered")):
        rng = seed_of(3, G)
        gm = np.where(d.rad < RC, 4.0, G)
        z = d.placed(8, rng, fall=8.0 if G < 1 else 1e9)
        z = d.run(z, gm, 600, rng, 0.0)
        z2 = d.run(z, np.full_like(d.rad, G), 300, rng, 0.0)
        amp = np.abs(d.annulus(z2, 3 if G < 1 else 8))
        w = d.loop(z2, 8)
        if G < 1:
            good = float(np.median(amp)) <= .05
            ok &= good
            print(f"  {lab}: input stopped: reading at r = 8 {float(np.median(amp)):.4f}; {verdict(good)}", flush=True)
            z3 = d.run(z2, gm, 600, rng, 0.0)
            ww = d.loop(z3, 5)
            print(f"  {lab}: input back after the whole faded: windings {sorted(set(ww.tolist()))}; winding 1 in {float(np.mean(ww==1)):.2f}", flush=True)
        else:
            good = float(np.mean(w == 1)) >= .9 and float(np.median(amp)) >= .5
            ok &= good
            print(f"  {lab}: input stopped: reading at r = 8 {float(np.median(amp)):.3f}; winding 1 in {float(np.mean(w==1)):.2f}; {verdict(good)}", flush=True)
    return ok


def dir_cell(job):
    G, Gc, c = job
    d = Disk(32)
    rng = seed_of(4, G, Gc, c)
    gm = np.where(d.rad < RC, Gc, G)
    z = d.placed(4, rng, fall=1e9)
    z = d.run(z, gm, 1500, rng, c)
    k, rt = d.measure(z, gm, rng, c, 10, 25)
    w = d.loop(z, 8)
    return G, Gc, c, k.tolist(), rt[0].tolist(), w.tolist()


def fed_dir():
    G, Gc, c = .95, 4.0, 1.0
    d = Disk(32)
    rng = seed_of(4, 77)
    gm = np.where(d.rad < RC, Gc, G)
    z = d.placed(1, rng, spread=0.0)
    z = d.run(z, gm, 1000, rng, c, sigma=0.0)
    k, rt = d.measure(z, gm, rng, c, 4, 7, r0=5, r1=6, sigma=0.0)
    return float(k[0]), float(rt[0][0])


def job_direction(_o):
    """V4."""
    ok = True
    cells = [(2.0, 0.0, 1.0), (2.0, .5, 1.0), (2.0, 1.0, 1.0), (2.0, 1.25, 1.0), (2.0, 1.5, 1.0), (2.0, 2.0, 1.0), (2.0, 2.5, 1.0), (2.0, 4.0, 1.0), (2.0, 8.0, 1.0), (2.0, 4.0, -1.0), (3.0, 3.0, 2.0), (3.0, 8.0, 2.0)]
    with Pool(8) as p:
        res = p.map(dir_cell, cells)
    for G, Gc, c, k, rt, w in res:
        gm = patch(G, Gc)
        r, f = radial(gm, c, T=2500)
        rk = rad_slope(r, f, 10, 25)
        k, rt, w = np.array(k), np.array(rt), np.array(w)
        mk = float(np.median(k))
        fr = float(np.mean(w == 1))
        good = fr >= .75 and abs(mk - rk) <= max(.3 * abs(rk), .03)
        if (G, Gc, c) == (2.0, 1.5, 1.0):
            print(f"  G {G:g}, Gc {Gc:g}, c {c:g}: slope {mk:.4f} (radial {rk:.4f}); winding 1 in {fr:.2f} (reported)", flush=True)
            continue
        ok &= good
        print(f"  G {G:g}, Gc {Gc:g}, c {c:g}: slope {mk:.4f} (radial {rk:.4f}); rate {float(np.median(rt)):.4f}; winding 1 in {fr:.2f}; {verdict(good)}", flush=True)
    k, rt = fed_dir()
    gm = patch(.95, 4.0)
    r, f = radial(gm, 1.0, T=2500)
    rk = rad_slope(r, f, 4, 7)
    rrt = rad_rate(gm, 1.0, f, at=(5, 6))[0]
    good = abs(k - rk) <= .3 * abs(rk) and abs(rt - rrt) <= .05 * abs(rrt) and rt * k < 0
    ok &= good
    print(f"  Fed, G .95, Gc 4, c 1: slope {k:.4f} (radial {rk:.4f}); rate {rt:.4f} (radial {rrt:.4f}); phase {'inward' if rt*k>0 else 'outward'}; {verdict(good)}", flush=True)
    return ok


def sig_cell(job):
    G, Gc, c = job
    d = Disk(32)
    rng = seed_of(8, G, Gc, c)
    gm = np.where(d.rad < RC, Gc, G)
    z = d.placed(1, rng, fall=1e9)
    z = d.run(z, gm, 1000, rng, c, sigma=0.0)
    r0 = 14
    p = z * np.exp(.2j * (np.abs(d.rad - r0) <= 1))
    a, b = z.copy(), p.copy()
    cen = {}
    for t in range(1, 61):
        a = d.run(a, gm, 1.0, rng, c, sigma=0.0)
        b = d.run(b, gm, 1.0, rng, c, sigma=0.0)
        e = np.abs(wrap(np.angle(b) - np.angle(a)))[0] * d.mask
        cen[t] = float((d.rad * e).sum() / e.sum())
    ts = np.arange(20, 61)
    return G, Gc, c, float(np.polyfit(ts, [cen[t] for t in ts], 1)[0])


def job_signal(_o):
    """V5."""
    cells = [(2.0, 2.0, 0.0), (2.0, 2.0, 1.0), (2.0, 1.25, 1.0), (2.0, 4.0, 1.0)]
    with Pool(4) as p:
        res = {(g, gc, c): v for g, gc, c, v in p.map(sig_cell, cells)}
    v0 = res[(2.0, 2.0, 0.0)]
    bare, dep, rich = res[(2.0, 2.0, 1.0)] - v0, res[(2.0, 1.25, 1.0)] - v0, res[(2.0, 4.0, 1.0)] - v0
    ok = dep >= 1.5 * bare and abs(rich) <= .01
    print(f"  Drift above no turn: bare {bare:.4f}; depleted core {dep:.4f}; rich core {rich:.4f}; {verdict(ok)}", flush=True)
    return ok


def arr_cell(job):
    where, target = job
    G, c, shift = 2.0, 1.0, -.05
    d = Disk(32)
    rng = seed_of(5, len(where), target)
    gm = np.full_like(d.rad, G)
    z = d.placed(4, rng, fall=1e9)
    z = d.run(z, gm, 1000, rng, c)
    if where == "none":
        patchw = None
    elif where == "core":
        patchw = shift * (d.rad < 3)
    else:
        patchw = shift * (d.rad >= 28)
    a0 = np.angle(d.annulus(z, target))
    rates = []
    for _ in range(3000):
        z = d.run(z, gm, 1.0, rng, c, patchw)
        a1 = np.angle(d.annulus(z, target))
        rates.append(wrap(a1 - a0))
        a0 = a1
    return where, target, np.median(np.array(rates), axis=1).tolist()


def job_arrival(_o):
    """V6."""
    ok = True
    cells = [("none", 24), ("core", 24), ("none", 8), ("edge", 8)]
    with Pool(4) as p:
        res = {(w, t): np.array(r) for w, t, r in p.map(arr_cell, cells)}
    out = {}
    for where, target in (("core", 24), ("edge", 8)):
        base = res[("none", target)].mean()
        rr = res[(where, target)]
        final = rr[-300:].mean()
        change = final - base
        frac = (rr - base) / change if abs(change) > 1e-4 else rr * 0
        w = np.convolve(frac, np.ones(50) / 50, mode="valid")
        idx = np.where(w >= .5)[0]
        t = float(idx[0]) if len(idx) else float("inf")
        out[where] = (t, change / -.05)
    t1, s1 = rad_arrival("core", at=24)
    t2, s2 = rad_arrival("edge", at=8)
    print(f"  Core to r 24: half way at t = {out['core'][0]:.0f}, share {out['core'][1]:.3f}; radial {t1:.0f}, {s1:.3f}", flush=True)
    print(f"  Edge to r 8: half way at t = {out['edge'][0]:.0f}, share {out['edge'][1]:.3f}; radial {t2:.0f}, {s2:.3f}", flush=True)
    a = out["core"][0] < out["edge"][0]
    b = abs(out["core"][0] - t1) <= .5 * t1 and abs(out["edge"][0] - t2) <= .5 * t2
    c = abs(out["core"][1] - s1) <= .5 * abs(s1) and abs(out["edge"][1] - s2) <= .5 * abs(s2)
    return a and b and c


def phased_cell(job):
    eps, dO = job
    G, c = 2.0, 1.0
    d = Disk(32)
    rng = seed_of(6, eps, dO)
    gm = np.full_like(d.rad, G)
    z = d.placed(4, rng, fall=1e9)
    z = d.run(z, gm, 1000, rng, c)
    k0, r0 = d.measure(z, gm, rng, c, 10, 25)
    src = eps * (d.rad < 2)
    Om = float(np.median(r0[1])) + dO
    t = 0.0
    z1 = d.run(z, gm, 1500, rng, c, src=src, srcrate=Om, t0=t)
    t = 1500.0
    a0 = np.angle(d.annulus(z1, 24))
    tot = np.zeros_like(a0)
    y = z1
    for i in range(int(40 / DT)):
        y = d.run(y, gm, DT, rng, c, src=src, srcrate=Om, t0=t + i * DT)
        a1 = np.angle(d.annulus(y, 24))
        tot = tot + wrap(a1 - a0)
        a0 = a1
    rate = tot / 40
    pos = d.zero_pos(y)
    w = d.loop(y, 16)
    return eps, dO, float(np.median(r0[1])), float(np.median(rate)), [p[0] for p in pos], [p[1] for p in pos], w.tolist()


def job_phased(_o):
    """V7."""
    ok = True
    cells = [(.1, .05), (.1, -.05), (.3, .05), (.3, -.05), (1.0, .05), (1.0, -.05), (3.0, .05), (3.0, -.05)]
    with Pool(8) as p:
        res = p.map(phased_cell, cells)
    for eps, dO, r0, r1, dist, cnt, w in res:
        moved = (r1 - r0) / dO
        wfr = float(np.mean(np.array(w) == 1))
        if eps <= .3:
            good = abs(moved) <= .25 and wfr >= .75 and float(np.median(dist)) <= 4
            ok &= good
            print(f"  Input {eps:g}, its rate {dO:+g} from the whole's: far rate moved {moved:.3f} of the difference; zero at r {float(np.median(dist)):.1f}; winding 1 at r = 16 in {wfr:.2f}; {verdict(good)}", flush=True)
        else:
            print(f"  Input {eps:g}, its rate {dO:+g} from the whole's: far rate moved {moved:.3f} of the difference; zero at r {float(np.median(dist)):.1f}; zeros {sorted(set(cnt))}; winding 1 at r = 16 in {wfr:.2f} (reported)", flush=True)
    return ok


def job_birth(_o):
    """V8."""
    ok = True
    d = Disk(16)
    G = .95
    gm = np.where(d.rad < RC, 4.0, G)
    rng = seed_of(7, 1)
    z = .05 * cnoise(rng, (64, *d.x.shape)) * d.mask
    z = d.run(z, np.full_like(d.rad, G), 50, rng, 0.0, src=(.5 * (d.rad < 2)), srcrate=.5)
    w = d.loop(z, 5)
    fr = float(np.mean(w == 0))
    ok &= fr >= .9
    print(f"  Input with a phase, parts below hold, no seed: winding 0 at r = 5 in {fr:.2f}", flush=True)
    rng = seed_of(7, 2)
    z = .05 * cnoise(rng, (64, *d.x.shape)) * d.mask
    z = d.run(z, gm, 200, rng, 0.0)
    w = d.loop(z, 5)
    fr2 = float(np.mean(w != 0))
    good = .1 <= fr2 <= .7
    ok &= good
    print(f"  Active core from noise, parts below hold: wound at r = 5 in {fr2:.2f}; windings {sorted(set(w.tolist()))}; {verdict(good)}", flush=True)
    return ok


def job_f1(_o):
    ok = True
    cells = [(.95, x, 0.0) for x in (2.5, 3.0, 3.5, 4.0, 6.0)]
    with Pool(5) as p:
        res = p.map(fed_cell, cells)
    last = 0.0
    held = []
    for G, Gc, c, ext, pk, w in res:
        print(f"  G {G:g}, Gc {Gc:g}: extent {ext:.1f}; peak {pk:.3f}; winding 1 at r = 5 in {w:.2f}", flush=True)
        if pk >= .5 and w >= .75:
            held.append((Gc, ext, pk))
    good = bool(held) and held[0][0] <= 4.0
    good &= all(abs(e - 8) <= 1.5 for _g, e, _p in held)
    good &= all(held[i + 1][2] >= held[i][2] - .01 for i in range(len(held) - 1))
    return good


def job_f2(_o):
    d = Disk(16)
    rng = seed_of(9, 1)
    z = .005 * cnoise(rng, (64, *d.x.shape)) * d.mask
    z = d.run(z, np.full_like(d.rad, .95), 50, rng, 0.0, src=(.5 * (d.rad < 2)), srcrate=.5, sigma=SIGMA * .1)
    w = d.loop(z, 3)
    fr = float(np.mean(w == 0))
    print(f"  Input with a phase, noise a tenth, reading at r = 3: winding 0 in {fr:.2f}", flush=True)
    return fr >= .9


JOBS = {"zero": ("V1", job_zero), "fed": ("V2", job_fed), "cutoff": ("V3", job_cutoff), "direction": ("V4", job_direction), "signal": ("V5", job_signal), "arrival": ("V6", job_arrival), "phased": ("V7", job_phased), "birth": ("V8", job_birth), "f1": ("F1", job_f1), "f2": ("F2", job_f2)}


if __name__ == "__main__":
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    which = sys.argv[2:] or list(JOBS)
    res = {}
    for w in which:
        if w == "solve":
            solve()
            continue
        if w == "deficit":
            solve_deficit()
            continue
        name, fn = JOBS[w]
        t0 = time.time()
        ok = fn(None)
        res[name] = bool(ok)
        print(f"{name} {verdict(ok)}; {time.time()-t0:.0f}s", flush=True)
    with open(os.path.join(outdir, "results_" + "_".join(which) + ".json"), "w") as f:
        json.dump(res, f)
