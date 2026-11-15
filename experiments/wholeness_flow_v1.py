"""Flow through the 0, and the 1 it is the centre of. Predictions frozen before any site-level run of this script.

Created: 2026-11-05
Last updated: 2026-11-05
Version: 1.0
History: 2026-11-05 v1.0: initial, after Ashman said yes to testing flow and added: "Also thinking that the 0 is a center of a 1. But not just any 1, it has to be 1 that is whole with parts." The theory is a Claude Doc, https://claude.ai/artifact/58ahYtFyKbQtDHEggdvEte

Results: W4 passed; W1, W2, W3, W5, W6 missed. W2: only (3, 2) passed whole. W3: outward in all 6 cells, .03 to .16, with (2, -2) at .45 of radial. W4: core .57 to .60 and .06 to .07 of the shift; ring .20 to .22 and .03.
After the follow-ups: E1, E3 passed; E2 missed. E1: the W1 miss is Euler on a fast rotation. E2: at G = 8, n = 5, noise a tenth held only in .41; first n holding at normal noise 9, 7, 7, 6, 5 at G = 2, 3, 4, 8, 32. E3: single 0 up to c = .5, 1, 1, 2, 2 at G = 1.5, 2, 2.5, 3, 4, breaking at the next c into 16, 63, 36, 178, 140 zeros; inward in every seed in all 16 cells where it held.
Totals: 9 frozen, 3 passed, 6 missed. Spiral waves in chemical and living media share this physics, so it does not single out a person. No real system was measured.

Needs numpy. All data are synthetic.
Run: python -I wholeness_flow_v1.py OUTDIR [solve idle waves signal clock strokes parts e1 e2 e3]
"solve" prints numbers from a radial reduction and from linear algebra, and was run before the predictions were written. It simulates no lattice sites.

WHY. wholeness_zero_v1.py ended with nothing flowing through the 0. And Ashman says the 0 is the centre of a 1, and only of a 1 that is whole with parts. Canon: "The dot is 0... The circle is 1", "The future converges. The past emerges.", and the pump: convergence, the turn, emergence.

HAND DERIVATIONS.
(a) The same parts make the 0 and the 1. Parts round a loop with phases theta_j: the sum of their values is 0, and the sum of their steps is one whole turn. So the 0 is the centre of a 1 in an exact sense: the 1 is the winding and the 0 is what the parts add to. A 1 with no parts has no steps. A consensus is a 1 as a value, with steps of 0, values that add to n m, and no 0 at all (Y3 in wholeness_zero_v1.py). So not just any 1.
(b) How few parts. Two cannot turn: their steps are pi and -pi, which wrap to 0. The smallest definite turn is 3, each step under pi. To hold on plain nearest ties a part reads cos(2 pi / n), so by hand G cos(2 pi / n) > 1, n_min 7, 6, 5, 5 at G = 2, 3, 4, 8. The solver is stricter, since the phase pattern fails before the amplitude does: 9, 7, 6, 5, and still 5 at G = 32. So a plain whole with a 0 has a floor of 5 parts, and more at lower gain.
(c) A turn in each tie. Each part reads the one before it, turned by beta = 2 pi / n. Then y_j = exp(-i j beta) z_j reads y_(j-1), so it is a consensus on a directed chain, relabelled, as a stored pattern was. So any n >= 3 holds at full strength from noise, with mean 0, and the sign of beta sets the sign of the turn. At n = 4, beta = pi / 2: z = m i^j, so 1 + i - 1 - i = 0 and one whole turn, which is the four strokes in arithmetic. It is a relabelled consensus, so this is a reading and not a discovery. n = 2, beta = pi: mean 0 and no turn. Two parts can balance on a 0 without having a centre.
(d) Two turns that do not flow. A uniform turn is only a rotating frame. A lag alpha in reading gives m = cos(alpha) tanh(G D m) at rate tan(alpha), whatever the gradient, so everything rotates rigidly and is weaker, and a quarter turn on every undirected read (alpha = pi / 2) ends it.
(e) A turn from energy. A part turns at a rate c |z|^2: its rate is its energy. Canon has "energy and frequency are the same thing", which is why I chose this, and it is my choice. At the 0 there is no energy, so no turning. Amplitude falls as phase gradient rises, m(k), so rate falls too: a wave exp(i(k r + w t)) has w = c m(k)^2. From memory, Hagan 1982: spirals send signal outward. Signal speed -dw/dk is outward only if k has the sign of c. Then w / k > 0, so phase lines move inward, for either sign of c. So phase lines converge on the 0 and signal emerges from it, with nothing tuned. Radial solver, R = 32, |c| = 1, 2, 4: G 2: k .262, .204, .132, rate .911, 1.777, 2.254, inward. G 1.5, |c| = 1, 2: k .647, .239, rate .625, .842, inward, but at |c| = 4 it turns outward, k .057, rate 1.281. G 3, c 2: k .087, rate 1.979. G 4, c 2: k .008, rate 1.997. Drift above c = 0: G 2: .043, .18 to .24 at |c| = 1, 2. G 1.5, |c| = 1: .155, .175. G 4: at most .0008. So flow needs soft parts. A stiff amplitude does not change with gradient, so it carries no wave.
(f) Numerics, caught in the solver before any site ran: plain Euler on the rotation blew up at |c| >= 2 and overstated k at c = 1. The rotation is now integrated exactly.
(g) Does the core set the clock? I expected so. Solver, G 2, c 1: a shift of -.05 at r < 3 moves the rate everywhere by .68 of the shift, and the same on a ring at r = 14 to 18 by .26, though the ring has far more sites. A shift of +.05: .09 and .02. So the core weighs most per site, and slowing counts where speeding barely does. It does not simply set the clock.
Reading to test, not a result. Nothing crosses the 0 here. Phase lines arrive and end at it, and signal leaves from it. That is the shape of convergence, a turn and emergence, and "through" would still be a stretch.

PREDICTIONS. Noise .02, input spread .05. Disk radius 32, except 16 in W1. Charge from plaquettes. k is the slope of the phase along the radius from .3 R to .8 R, and rate the far-field turning.
W1. Uniform turn .3, no noise: amplitudes agree within 1e-6. Lag alpha = .3, 1/G limit - .1, limit + .15, pi / 2, G = 2, 4: far amplitude within .05 of derived, and |k| <= .01.
W2. Energy turn, run 700, cells (G, c): (2, +-1), (2, +-2), (2, +-4), (1.5, +-1), (1.5, +-2), (3, 2), (4, 2). Charge 1 in at least 75%. Where radial |k| >= .02: k within 25%, rate within 10%, phase inward in at least 90%. Elsewhere |k| <= .02.
W3. Signal. A ring of phase at r = 14 pushed by .2, no noise. Centroid drift above c = 0 is positive and within a factor of 2 of the radial number, at (2, +-1), (2, +-2), (1.5, +-1). At (2, +-1) what reaches r = 22 over what reaches r = 6 at t = 40 is at least 1.5 times its value at c = 0.
W4. Clock, G = 2, c = 1, run 1500. Rates at r = 8 and r = 24 move, as a share of the shift, within 50% or .15 of: core -.05: .68, .69; core +.05: .09, .09; ring -.05: .26, .27; ring +.05: .02, .02.
W5. A turn in each tie, directed ring, from noise, 32 seeds, G = 2, 4, both signs. n = 3, 4, 5, 8: winding equal to the sign in at least 90%, amplitude within 3% of rest(G), |mean| <= .05. n = 2: |mean| <= .05, winding reported.
W6. Plain nearest ties, started wound, run 400, 32 seeds: holds one turn in at least 75% at n_min = 9, 7, 6, 5 for G = 2, 3, 4, 8, and in at most 25% at n_min - 1.

ADDED AFTER SEEING THE RESULTS ABOVE, predictions frozen before these ran. Seen so far: W4 passed; W1, W2, W3, W5, W6 missed. W1: just inside the lag limit, far amplitude .416 and .357 against .361 and .278. W2: only (3, 2) passed; (2, +-1) held in every seed, inward in every seed, k .18 against .26; at (2, +-2), (2, +-4) and all G = 1.5 cells charge 1 was lost in most seeds. W3: drift outward in every cell, but (2, -2) was .45 of radial. W5: n = 3, 4, 5 clean; at G = 4, n = 8, 2 of 32 seeds went elsewhere with |mean| .72. W6: G = 2, 3 clean; G = 4, n = 6 and G = 8, n = 5 held in none.
E1. W1's miss is Euler on a fast rotation. Single site, same law: at step .05 within .02 of the .416 and .357 measured; at step .005 within .02 of the .361 and .278 derived.
E2. W6's miss is noise on a small basin. With noise and spread a tenth as large: holds in at least 75% at G = 4, n = 6 and G = 8, n = 5. Also reported: the first n holding in at least 75% at normal noise, G = 2, 3, 4, 8, 32.
E3. What the energy turn does to a single 0. Map of G = 1.5, 2, 2.5, 3, 4 against |c| = .25, .5, 1, 2, 4, run 700. (1.5, .5) and (2, .5): charge 1 in at least 75% and 1 zero in at least 75%. (2, 4) and (1.5, 2): median zero count at least 3, so the 0 breaks up rather than leaving. The rest reported.
"""
import json
import os
import sys
import time
from math import acos, atanh, cos, pi, sqrt, tan, tanh
from multiprocessing import Pool
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np

DT = .05
SIGMA = .02
SPREAD = .05


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
    m = 1.0
    for _ in range(20000):
        m = tanh(G * m)
    return m


def winding(z):
    a = np.angle(z)
    return np.rint(wrap(np.roll(a, -1, axis=-1) - a).sum(-1) / (2 * pi)).astype(int)


# ---------- Radial reduction: no lattice sites ----------
def radial(G, c, R=32, T=1500.0, dw=None, f0=None):
    r = np.arange(1, R + 1, dtype=float)
    f = rest(G) * np.tanh(r / 2) + 0j if f0 is None else f0.copy()
    d = np.zeros(R) if dw is None else dw(r)
    for _ in range(int(T / DT)):
        g = np.r_[0, f, f[-1]]
        lap = g[2:] - 2 * f + g[:-2] + (g[2:] - g[:-2]) / (2 * r) - f / r ** 2
        w = G * (f + .25 * lap)
        f = f + DT * (-f + lim(w))
        f = f * np.exp(1j * DT * (c * np.abs(f) ** 2 + d))
    return r, f


def rad_measure(G, c, R=32, T=1500.0, dw=None):
    r, f = radial(G, c, R, T, dw)
    i0, i1 = int(.3 * R), int(.8 * R)
    k = float(np.polyfit(r[i0:i1], np.unwrap(np.angle(f[i0:i1])), 1)[0])
    g = f.copy()
    a0 = np.angle(g[int(.6 * R)])
    tot = 0.0
    for _ in range(int(20 / DT)):
        r, g = radial(G, c, R, DT, dw, g)
        a1 = np.angle(g[int(.6 * R)])
        tot += wrap(a1 - a0)
        a0 = a1
    return k, tot / 20, f


def rad_rates(G, c, dw=None, R=32, T=1500.0, at=(8, 24)):
    r, g = radial(G, c, R, T, dw)
    a0 = np.angle(g[[x - 1 for x in at]])
    tot = np.zeros(len(at))
    for _ in range(int(20 / DT)):
        r, g = radial(G, c, R, DT, dw, g)
        a1 = np.angle(g[[x - 1 for x in at]])
        tot = tot + wrap(a1 - a0)
        a0 = a1
    return tot / 20


def rad_pulse(G, c, R=32, T=1500.0, r0=14, delta=.2):
    r, f = radial(G, c, R, T)
    p = f * np.exp(1j * delta * (np.abs(r - r0) <= 1))
    fa, fb = f.copy(), p.copy()
    out = {}
    for tt in range(1, 81):
        r, fa = radial(G, c, R, 1.0, None, fa)
        r, fb = radial(G, c, R, 1.0, None, fb)
        d = np.abs(wrap(np.angle(fb) - np.angle(fa)))
        out[tt] = (float((r * r * d).sum() / (r * d).sum()), float(d[r0 + 8 - 1]), float(d[r0 - 8 - 1]))
    ts = np.arange(20, 61)
    v = float(np.polyfit(ts, [out[t][0] for t in ts], 1)[0])
    return v, out[40][1] / max(out[40][2], 1e-12)


# ---------- Ring, linear algebra ----------
def ring1(n):
    W = np.zeros((n, n))
    for j in range(n):
        W[j, (j + 1) % n] += .5
        W[j, (j - 1) % n] += .5
    return W


def ring_stable(n, G):
    W = ring1(n)
    th = 2 * pi * np.arange(n) / n
    D = float(np.real((W[0] * np.exp(1j * (th - th[0]))).sum()))
    gain = G * D
    if gain <= 1:
        return False
    m = 1.0
    for _ in range(40000):
        m = tanh(gain * m)
    z = m * np.exp(1j * th)
    w = G * W @ z
    a = np.abs(w)
    ux, uy = np.real(w) / a, np.imag(w) / a
    rho, tau = 1 / np.cosh(a) ** 2, np.tanh(a) / a
    J = -np.eye(2 * n)
    for j in range(n):
        Dj = np.array([[rho[j] * ux[j] ** 2 + tau[j] * uy[j] ** 2, (rho[j] - tau[j]) * ux[j] * uy[j]], [(rho[j] - tau[j]) * ux[j] * uy[j], rho[j] * uy[j] ** 2 + tau[j] * ux[j] ** 2]])
        J[2 * j:2 * j + 2, ::2] += G * Dj[:, [0]] * W[j]
        J[2 * j:2 * j + 2, 1::2] += G * Dj[:, [1]] * W[j]
    return float(np.linalg.eigvals(J).real.max()) < 1e-7


def n_min(G):
    for n in range(3, 40):
        if ring_stable(n, G):
            return n
    return None


def solve():
    print("Smallest ring, nearest neighbours, that holds one turn")
    for G in (1.5, 2.0, 3.0, 4.0, 8.0, 32.0):
        print(f"  G {G:g}: n_min {n_min(G)}")
    print("Energy turn, radial reduction, R = 32: k, spiral rate, c m^2, phase direction, drift above c = 0, out over in, against c = 0")
    for G in (1.5, 2.0, 3.0, 4.0):
        v0, ra0 = rad_pulse(G, 0.0)
        print(f"  G {G:g}, c 0: drift {v0:.4f}; out over in {ra0:.2f}")
        for c in (-4.0, -2.0, -1.0, 1.0, 2.0, 4.0):
            k, om, _f = rad_measure(G, c)
            v, ra = rad_pulse(G, c)
            print(f"  G {G:g}, c {c:g}: k {k:.4f}; rate {om:.4f}; c m^2 {c*rest(G)**2:.4f}; phase {'inward' if om*k>0 else 'outward'}; drift above c=0 {v-v0:.4f}; out over in {ra:.2f}", flush=True)
    print("Clock, G 2, c 1: rates at r = 8 and r = 24 with a shift dw in sites at r < 3, or at r 14 to 18")
    base = rad_rates(2.0, 1.0)
    print(f"  no shift: {base[0]:.4f}, {base[1]:.4f}")
    for dw in (-.05, .05):
        a = rad_rates(2.0, 1.0, lambda r, d=dw: d * (r < 3))
        b = rad_rates(2.0, 1.0, lambda r, d=dw: d * ((r >= 14) & (r <= 18)))
        print(f"  dw {dw:g}: core moves them by {(a[0]-base[0])/dw:.3f}, {(a[1]-base[1])/dw:.3f} of dw; ring by {(b[0]-base[0])/dw:.3f}, {(b[1]-base[1])/dw:.3f} of dw", flush=True)


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

    def placed(self, B, m, rng):
        z = m * np.tanh(self.rad / 2) * np.exp(1j * self.phi)
        return (z[None] + SPREAD * cnoise(rng, (B, *self.x.shape))) * self.mask

    def reading(self, z):
        s = 0
        for ax, sh, a in self.adj:
            s = s + np.roll(z, sh, axis=ax + 1) * a
        return s / np.maximum(self.cnt, 1)

    def run(self, z, G, T, rng, c=0.0, dw=None, alpha=0.0, omega=0.0, sigma=SIGMA):
        turn = np.exp(1j * alpha)
        d = 0 if dw is None else dw
        for _ in range(int(T / DT)):
            z = z + DT * (-z + turn * lim(G * self.reading(z)))
            z = z * np.exp(1j * DT * (c * np.abs(z) ** 2 + d + omega))
            if sigma:
                z = z + sqrt(DT) * sigma * cnoise(rng, z.shape)
            z = z * self.mask
        return z

    def net(self, z):
        a = np.angle(z)
        d1 = wrap(np.roll(a, -1, axis=2) - a)
        d2 = wrap(np.roll(np.roll(a, -1, axis=2), -1, axis=1) - np.roll(a, -1, axis=2))
        d3 = wrap(np.roll(a, -1, axis=1) - np.roll(np.roll(a, -1, axis=2), -1, axis=1))
        d4 = wrap(a - np.roll(a, -1, axis=1))
        ch = np.rint((d1 + d2 + d3 + d4) / (2 * pi)).astype(int)
        m = self.mask
        ok = m & np.roll(m, -1, 1) & np.roll(m, -1, 0) & np.roll(np.roll(m, -1, 1), -1, 0)
        return (ch * ok).sum((1, 2))

    def annulus(self, z, r):
        sel = self.mask & (np.abs(self.rad - r) <= .5)
        return (z * np.exp(-1j * self.phi) * sel).sum((1, 2)) / sel.sum()

    def measure_k(self, z):
        rs = np.arange(int(.3 * self.R), int(.8 * self.R))
        a = np.stack([self.annulus(z, r) for r in rs], axis=1)
        return np.array([np.polyfit(rs, np.unwrap(np.angle(a[b])), 1)[0] for b in range(z.shape[0])])

    def measure_rate(self, z, G, rng, c=0.0, dw=None, r=None):
        r = int(.6 * self.R) if r is None else r
        a0 = np.angle(self.annulus(z, r))
        tot = 0.0
        for _ in range(int(20 / DT)):
            z = self.run(z, G, DT, rng, c, dw)
            a1 = np.angle(self.annulus(z, r))
            tot = tot + wrap(a1 - a0)
            a0 = a1
        return tot / 20, z


def job_idle(_o):
    """W1."""
    ok = True
    for G in (2.0, 4.0):
        d = Disk(16)
        rng = seed_of(1, G)
        z0 = d.placed(2, rest(G), rng)
        a = d.run(z0, G, 100, rng, sigma=0.0)
        b = d.run(z0, G, 100, rng, omega=.3, sigma=0.0)
        diff = float(np.abs(np.abs(a) - np.abs(b)).max())
        ok &= diff <= 1e-6
        print(f"  G {G:g}: uniform turn .3: largest difference in amplitude {diff:.2e}")
        for al in (.3, acos(1 / G) - .1, acos(1 / G) + .15, pi / 2):
            z = d.run(z0, G, 300, rng, alpha=al, sigma=0.0)
            m = float(np.abs(z)[:, d.mask & (d.rad > 8)].mean())
            want = 0.0
            if G * cos(al) > 1:
                want = .9
                for _ in range(40000):
                    want = cos(al) * tanh(G * want)
            good = abs(m - want) <= .05
            kk = float(np.abs(d.measure_k(z)).max()) if want > .01 else 0.0
            good &= kk <= .01
            ok &= good
            print(f"  G {G:g}, lag {al:.3f} ({'tan %.3f' % tan(al)}): far amplitude {m:.3f}, derived {want:.3f}; |k| {kk:.4f}")
    return ok


def wave_cell(job):
    G, c = job
    d = Disk(32)
    rng = seed_of(2, G, c)
    z = d.placed(4, rest(G), rng)
    z = d.run(z, G, 700, rng, c)
    net = d.net(z)
    k = d.measure_k(z)
    om, z = d.measure_rate(z, G, rng, c)
    return G, c, net.tolist(), k.tolist(), om.tolist()


def job_waves(_o):
    """W2."""
    ok = True
    cells = [(2.0, x) for x in (-4.0, -2.0, -1.0, 1.0, 2.0, 4.0)] + [(1.5, 1.0), (1.5, -1.0), (1.5, 2.0), (1.5, -2.0), (3.0, 2.0), (4.0, 2.0)]
    with Pool(8) as p:
        res = p.map(wave_cell, cells)
    for G, c, net, k, om in res:
        rk, rom, _f = rad_measure(G, c)
        net, k, om = np.array(net), np.array(k), np.array(om)
        keep = net == 1
        fr = float(keep.mean())
        mk, mo = float(np.median(k)), float(np.median(om))
        inward = float(np.mean(om * k > 0))
        strong = abs(rk) >= .02
        good = fr >= .75
        if strong:
            good &= abs(mk - rk) <= .25 * abs(rk) and abs(mo - rom) <= .1 * abs(rom) and inward >= .9
        else:
            good &= abs(mk) <= max(.25 * abs(rk), .02)
        ok &= good
        print(f"  G {G:g}, c {c:g}: charge 1 in {fr:.2f}; k {mk:.4f} (radial {rk:.4f}); rate {mo:.4f} (radial {rom:.4f}); inward in {inward:.2f}; {verdict(good)}", flush=True)
    return ok


def signal_cell(job):
    G, c = job
    d = Disk(32)
    rng = seed_of(3, G, c)
    z = d.placed(1, rest(G), rng)
    z = d.run(z, G, 700, rng, c, sigma=0.0)
    r0 = 14
    p = z * np.exp(.2j * (np.abs(d.rad - r0) <= 1))
    a, b = z.copy(), p.copy()
    cen, far, near = {}, {}, {}
    for t in range(1, 81):
        a = d.run(a, G, 1.0, rng, c, sigma=0.0)
        b = d.run(b, G, 1.0, rng, c, sigma=0.0)
        e = np.abs(wrap(np.angle(b) - np.angle(a)))[0] * d.mask
        cen[t] = float((d.rad * e).sum() / e.sum())
        far[t] = float(e[np.abs(d.rad - (r0 + 8)) <= .5].mean())
        near[t] = float(e[np.abs(d.rad - (r0 - 8)) <= .5].mean())
    ts = np.arange(20, 61)
    v = float(np.polyfit(ts, [cen[t] for t in ts], 1)[0])
    return G, c, v, far[40] / max(near[40], 1e-12)


def job_signal(_o):
    """W3."""
    ok = True
    cells = [(2.0, 0.0), (2.0, 1.0), (2.0, -1.0), (2.0, 2.0), (2.0, -2.0), (1.5, 0.0), (1.5, 1.0), (1.5, -1.0)]
    with Pool(8) as p:
        res = {(g, c): (v, ra) for g, c, v, ra in p.map(signal_cell, cells)}
    for (G, c), (v, ra) in res.items():
        if c == 0:
            print(f"  G {G:g}, c 0: drift {v:.4f}; out over in {ra:.2f}", flush=True)
            continue
        v0, ra0 = res[(G, 0.0)]
        rv0, rra0 = rad_pulse(G, 0.0)
        rv, rra = rad_pulse(G, c)
        dv, rd = v - v0, rv - rv0
        good = dv > 0 and .5 * rd <= dv <= 2 * rd
        if G == 2.0 and abs(c) == 1.0:
            good &= ra >= 1.5 * ra0
        ok &= good
        print(f"  G {G:g}, c {c:g}: drift above c = 0 {dv:.4f} (radial {rd:.4f}); out over in {ra:.2f} against {ra0:.2f}; {verdict(good)}", flush=True)
    return ok


def clock_cell(job):
    where, dw = job
    G, c = 2.0, 1.0
    d = Disk(32)
    rng = seed_of(4, abs(dw), dw > 0, len(where))
    if where == "none":
        patch = None
    elif where == "core":
        patch = dw * (d.rad < 3)
    else:
        patch = dw * ((d.rad >= 14) & (d.rad <= 18))
    z = d.placed(4, rest(G), rng)
    z = d.run(z, G, 1500, rng, c, patch)
    a0 = np.stack([np.angle(d.annulus(z, x)) for x in (8, 24)])
    tot = np.zeros_like(a0)
    for _ in range(int(20 / DT)):
        z = d.run(z, G, DT, rng, c, patch)
        a1 = np.stack([np.angle(d.annulus(z, x)) for x in (8, 24)])
        tot = tot + wrap(a1 - a0)
        a0 = a1
    r = np.median(tot / 20, axis=1)
    return where, dw, float(r[0]), float(r[1]), d.net(z).tolist()


def job_clock(_o):
    """W4."""
    ok = True
    cells = [("none", 0.0), ("core", -.05), ("core", .05), ("ring", -.05), ("ring", .05)]
    with Pool(5) as p:
        res = {(w, x): (a, b, n) for w, x, a, b, n in p.map(clock_cell, cells)}
    a0, b0, _n = res[("none", 0.0)]
    ra0 = rad_rates(2.0, 1.0)
    print(f"  No shift: rates {a0:.4f}, {b0:.4f}; radial {ra0[0]:.4f}, {ra0[1]:.4f}", flush=True)
    for (w, x), (a, b, n) in res.items():
        if w == "none":
            continue
        if w == "core":
            ra = rad_rates(2.0, 1.0, lambda r, d=x: d * (r < 3))
        else:
            ra = rad_rates(2.0, 1.0, lambda r, d=x: d * ((r >= 14) & (r <= 18)))
        f1, f2 = (a - a0) / x, (b - b0) / x
        w1, w2 = (ra[0] - ra0[0]) / x, (ra[1] - ra0[1]) / x
        good = abs(f1 - w1) <= max(.5 * abs(w1), .15) and abs(f2 - w2) <= max(.5 * abs(w2), .15)
        ok &= good
        print(f"  {w}, shift {x:g}: rates at r = 8, 24 moved by {f1:.3f}, {f2:.3f} of the shift; radial {w1:.3f}, {w2:.3f}; charges {sorted(set(n))}; {verdict(good)}", flush=True)
    return ok


def job_strokes(_o):
    """W5."""
    ok = True
    for G in (2.0, 4.0):
        for n in (2, 3, 4, 5, 8):
            for sgn in (1, -1):
                beta = sgn * 2 * pi / n
                rng = seed_of(5, G, n, sgn + 2)
                z = .05 * cnoise(rng, (32, n))
                for _ in range(int(200 / DT)):
                    w = G * np.exp(1j * beta) * np.roll(z, 1, axis=1)
                    z = z + DT * (-z + lim(w)) + sqrt(DT) * SIGMA * cnoise(rng, z.shape)
                q = winding(z)
                am = float(np.abs(z).mean())
                mean = float(np.abs(z.mean(1)).max())
                if n == 2:
                    print(f"  G {G:g}, n 2, sign {sgn}: windings {sorted(set(q.tolist()))}; amplitude {am:.3f}; largest |mean| {mean:.3f}", flush=True)
                    ok &= mean <= .05
                    continue
                fr = float(np.mean(q == sgn))
                good = fr >= .9 and abs(am - rest(G)) <= .03 * rest(G) and mean <= .05
                ok &= good
                print(f"  G {G:g}, n {n}, sign {sgn}: winding {sgn} in {fr:.2f}; amplitude {am:.3f} (rest {rest(G):.3f}); largest |mean| {mean:.3f}; {verdict(good)}", flush=True)
    return ok


def job_parts(_o):
    """W6."""
    ok = True
    for G in (2.0, 3.0, 4.0, 8.0):
        nm = n_min(G)
        for n in (nm - 1, nm):
            if n < 3:
                continue
            rng = seed_of(6, G, n)
            W = ring1(n)
            th = 2 * pi * np.arange(n) / n
            z = .9 * np.exp(1j * th)[None, :] + SPREAD * cnoise(rng, (32, n))
            for _ in range(int(400 / DT)):
                z = z + DT * (-z + lim(G * z @ W.T)) + sqrt(DT) * SIGMA * cnoise(rng, z.shape)
            fr = float(np.mean((winding(z) == 1) & (np.abs(z).mean(1) >= .2)))
            good = fr >= .75 if n == nm else fr <= .25
            ok &= good
            print(f"  G {G:g}, n {n}: holds one turn in {fr:.2f}; {verdict(good)}", flush=True)
    return ok


def job_e1(_o):
    ok = True
    for G, al, meas, want in ((2.0, .9472, .416, .361), (4.0, 1.2181, .357, .278)):
        res = []
        for dt in (.05, .005):
            z = .9 + 0j
            for _ in range(int(400 / dt)):
                z = z + dt * (-z + np.exp(1j * al) * tanh(G * abs(z)) * z / abs(z))
            res.append(abs(z))
        good = abs(res[0] - meas) <= .02 and abs(res[1] - want) <= .02
        ok &= good
        print(f"  G {G:g}, lag {al:.3f}: step .05 gives {res[0]:.3f} (measured {meas}); step .005 gives {res[1]:.3f} (derived {want}); {verdict(good)}", flush=True)
    return ok


def ring_hold(G, n, scale, seeds=32, T=400.0):
    rng = seed_of(21, G, n, scale)
    W = ring1(n)
    th = 2 * pi * np.arange(n) / n
    z = .9 * np.exp(1j * th)[None, :] + scale * SPREAD * cnoise(rng, (seeds, n))
    for _ in range(int(T / DT)):
        z = z + DT * (-z + lim(G * z @ W.T)) + sqrt(DT) * scale * SIGMA * cnoise(rng, z.shape)
    return float(np.mean((winding(z) == 1) & (np.abs(z).mean(1) >= .2)))


def job_e2(_o):
    ok = True
    for G, n in ((4.0, 6), (8.0, 5)):
        fr = ring_hold(G, n, .1)
        good = fr >= .75
        ok &= good
        print(f"  G {G:g}, n {n}, noise a tenth: holds in {fr:.2f}; {verdict(good)}", flush=True)
    for G in (2.0, 3.0, 4.0, 8.0, 32.0):
        row = [(n, ring_hold(G, n, 1.0)) for n in range(5, 15)]
        first = next((n for n, f in row if f >= .75), None)
        print(f"  G {G:g}, normal noise: first n holding {first}; " + ", ".join(f"{n}: {f:.2f}" for n, f in row), flush=True)
    return ok


def map_cell(job):
    G, c = job
    d = Disk(32)
    rng = seed_of(23, G, c)
    z = d.placed(4, rest(G), rng)
    z = d.run(z, G, 700, rng, c)
    a = np.angle(z)
    d1 = wrap(np.roll(a, -1, axis=2) - a)
    d2 = wrap(np.roll(np.roll(a, -1, axis=2), -1, axis=1) - np.roll(a, -1, axis=2))
    d3 = wrap(np.roll(a, -1, axis=1) - np.roll(np.roll(a, -1, axis=2), -1, axis=1))
    d4 = wrap(a - np.roll(a, -1, axis=1))
    ch = np.rint((d1 + d2 + d3 + d4) / (2 * pi)).astype(int)
    m = d.mask
    ok = m & np.roll(m, -1, 1) & np.roll(m, -1, 0) & np.roll(np.roll(m, -1, 1), -1, 0)
    ch = ch * ok
    net = ch.sum((1, 2))
    cnt = np.abs(ch).sum((1, 2))
    k = d.measure_k(z)
    om, _z = d.measure_rate(z, G, rng, c)
    return G, c, float(np.mean(net == 1)), float(np.mean(cnt == 1)), float(np.median(cnt)), float(np.mean((om * k > 0)[cnt == 1])) if (cnt == 1).any() else float("nan"), float(np.median(np.abs(k[cnt == 1]))) if (cnt == 1).any() else float("nan")


def job_e3(_o):
    ok = True
    cells = [(G, c) for G in (1.5, 2.0, 2.5, 3.0, 4.0) for c in (.25, .5, 1.0, 2.0, 4.0)]
    with Pool(8) as p:
        res = {(g, c): r for g, c, *r in p.map(map_cell, cells)}
    for (G, c), (net, one, med, inw, k) in res.items():
        print(f"  G {G:g}, c {c:g}: charge 1 in {net:.2f}; exactly one zero in {one:.2f}; median zeros {med:.0f}; where one, inward in {inw:.2f}, |k| {k:.3f}", flush=True)
    for cell in ((1.5, .5), (2.0, .5)):
        net, one, med, inw, k = res[cell]
        ok &= net >= .75 and one >= .75
    for cell in ((2.0, 4.0), (1.5, 2.0)):
        ok &= res[cell][2] >= 3
    return ok


JOBS = {"idle": ("W1", job_idle), "waves": ("W2", job_waves), "signal": ("W3", job_signal), "clock": ("W4", job_clock), "strokes": ("W5", job_strokes), "parts": ("W6", job_parts), "e1": ("E1", job_e1), "e2": ("E2", job_e2), "e3": ("E3", job_e3)}


if __name__ == "__main__":
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    which = sys.argv[2:] or list(JOBS)
    res = {}
    for w in which:
        if w == "solve":
            solve()
            continue
        if w == "clocksolve":
            base = rad_rates(2.0, 1.0)
            print(f"  no shift: {base[0]:.4f}, {base[1]:.4f}")
            for dw in (-.05, .05):
                a = rad_rates(2.0, 1.0, lambda r, d=dw: d * (r < 3))
                b = rad_rates(2.0, 1.0, lambda r, d=dw: d * ((r >= 14) & (r <= 18)))
                print(f"  dw {dw:g}: core moves them by {(a[0]-base[0])/dw:.3f}, {(a[1]-base[1])/dw:.3f} of dw; ring by {(b[0]-base[0])/dw:.3f}, {(b[1]-base[1])/dw:.3f} of dw", flush=True)
            continue
        name, fn = JOBS[w]
        t0 = time.time()
        ok = fn(None)
        res[name] = bool(ok)
        print(f"{name} {verdict(ok)}; {time.time()-t0:.0f}s", flush=True)
    with open(os.path.join(outdir, "results_" + "_".join(which) + ".json"), "w") as f:
        json.dump(res, f)
