"""One 0 at the centre: what cannot be divided, and what it does. Predictions frozen before any site-level run of this script.

Created: 2026-11-05
Last updated: 2026-11-05
Version: 1.0
History: 2026-11-05 v1.0: initial, after Ashman asked: "What cannot be divided in your system? A 0. If there could be one 0 at the center of your system...." The theory is a Claude Doc, https://claude.ai/artifact/58ahYtFyKbQtDHEggdvEte

Results: Y1, Y3, Y4, Y5, Y6, Y7, Y8, Y10 passed; Y2, Y9 missed. Y1: last range 26, 32, 36, 40. Y3: exactly |q| zeros in every seed; smallest amplitude .437 at G = 2, .906 at G = 4. Y4: at most .5% of sites turned. Y6, reported: at G = 2 the zero left its piece in every seed. Y7: separation 18.2 and 14.4. Y10: ring wound .70, .58, 0 at r = 2, 4, 30; disk any zero .56 and exactly one .31 at G = 4, .44 and .38 at G = 2. Y2: last c .061, .084, .094, .114 against .051 to .054. Y9: .316, below the bracket.
After the follow-ups: F2 passed; F1, F3, F4 missed. F1: my run-length account was wrong. F2: .324, .316, .293; ratios .60, .62, .53. F3: .09 against .054, still far below s_hold .31. F4: balance went at .060 in all three, as predicted; the pull at the last c was .048, .213, .594 against .082, .316, .754, outside the bar at G = 2, 4.
Totals: 14 frozen, 9 passed, 5 missed, all five on how it ends. Nothing flows through the 0 in these runs, the phase is assumed, and no real system was measured.

Needs numpy. All data are synthetic.
Run: python -I wholeness_zero_v1.py OUTDIR [solve ring hub boundary node free cut two connect pull birth f1 f2 f4]
"solve" prints linear-algebra numbers used below, and was run before the predictions were written. It simulates no sites.

WHY. wholeness_point_v1.py had to assume that a node cannot be split, and its centre was a node that others read. Ashman points at what cannot be divided: a 0. Canon has this already: "The dot is 0 (total convergence of the field to a point). The circle is 1", "phase requires exactly 2D to exist", and "Information = the topology of 0s in the 1" (CLAUDE.md).

HAND DERIVATIONS.
(a) Only 0 is unchanged by dividing. x / k = x for every k holds only at x = 0. So a centre that holds 0 cannot be halved: cutting it gives 0 and 0, each the whole of it. Two 0s also cannot be told apart by what they hold, only by where they are.
(b) A 0 cannot work by being read. Parts that read 0 receive nothing; that is E3 in wholeness_point_v1.py, the aperture shut. In the real-valued law, then, a 0 at the centre does nothing but cost. So its work has to be something other than a value passed on.
(c) Give the law a phase. z' = -z + lim(G W z), lim(w) = tanh(|w|) w / |w|, the same leak and limit, with the limit on amplitude and the phase free. Real z gives back the old law. This is a new assumption of mine, though canon's i and its "rotation needs a plane" point the same way.
(d) A closed loop can turn. Add the phase steps round any closed loop and the sum is 2 pi q with q a whole number. Winding-number theorem: if a continuous z is nonzero on a closed curve bounding a disk and q is not 0, then z has a zero inside, and the charges of the zeros sum to q. So the boundary forces a centre. Nobody places it, it is not a site, and there is no half of it. That gives indivisibility from closing a loop, where I had to assume it for a node.
(e) A full turn averages to 0. The sum of exp(2 pi i j / n) is 0, and 1 + i - 1 - i = 0 for the four strokes. So parts spread round a circle are all different, and what they converge on is 0. A node reading all of them reads 0 with no clamp, and leaves 0 only as they fall out of balance.
(f) Neither a list nor a star can hold it. Under all pairs a wound part reads about 0, so it fades and a consensus takes over. Under a star parts read only the hub, which reads 0, so the same. So the point of the last test is not this 0. The ring holds only for short range. Solver, largest r / n at q = 1: .203, .250, .281, .328 at G = 2, 3, 4, 8, with r = 26, 32, 36, 42 of n = 128. From memory, Wiley, Strogatz and Girvan 2006 have about .34 for oscillators.
(g) A node that all read breaks it. Let parts read a share c through a node. By hand I estimated the wound state fails near c = .5. The solver refuted that before any site ran: c limit .051, .054, .054, .054 at G = 2, 3, 4, 8, for r = 8, far below the amplitude limit .484 to .871, since long waves of phase have little stiffness. So very little reading through a node undoes the 0, and the node then carries one consensus.
(h) It is not a node. Clamp any site or remove any site and the charge stays, since a loop further out does not change. So my earlier count of nodes that can move the whole reads this as a list, and only a loop reads it. A chair has no winding, so this separates a chair from a 0, which the last test could not.
(i) Cutting gives no fractions. Cut off the core and the pieces carry 1 and 0. Cut through the core and they carry 0 and 0. The pieces go on as lists, so the parts do not die, unlike a star.
(j) A 2 divides and a 1 does not. Two turns of boundary give two zeros that move apart. From memory, the cost goes as q squared. Reading, not result: a whole has one 0, and a group has several, "a group has n centres". Lattice caveat: one square cannot hold charge 2, so the first split is by construction, and only their moving apart is a test.
(k) Distinct under connection. The solver has the wound state stable up to s = 1, no own share at all, at every G. So parts stay all different under full connection, with no s_hold limit, which is the plane's healthy corner. Caveat: a part's place is given by the whole, since push it and it goes back. That is a position, not a hold, so this may not be what "a" meant.
(l) What ends it: an opposite charge, a cut through it, or a common pull strong enough to take a site through 0. I have no derived number for the pull, only a bracket.
This is known physics under other names: vortices and phase singularities, from memory Onsager 1949 and Kosterlitz and Thouless 1973. What is mine is using it as the centre of a whole. None of it shows that any real whole has one.

PREDICTIONS. Noise .02, input spread .05. Disk: radius 16, square grid, each site reading the mean of its neighbours. Charges come from plaquettes. The zero is placed on a plaquette except where it grows.
Y1. Ring, q = 1. Last range holding within 10% or 2 sites of 26, 32, 36, 42. All pairs and star, wound at the start: end with winding 0 in every seed.
Y2. A node reading a wound ring, read by nobody: |h| <= .05, G = 2, 3, 4, 8. Read by the parts at share c: last c holding the winding within .02 of .051, .054, .054, .054. At limit + .1: winding 0 and |h| >= .5 in at least 75%.
Y3. Boundary held turning q, interior random phases, run 500. Net charge equals q in every seed, G = 2, 4, q = 0, 1. Exactly |q| zeros in at least 50%.
Y4. Not a node. Placed zero, G = 2, 4. Clamp any one site opposite for 60, core sites included: at most 10% of sites turned past pi / 2; charge 1 after release in at least 90%. Core sites removed: loop winding 1 in at least 90%. 5% of sites removed at random: same.
Y5. Free edge, G = 4, run 1000: charge 1 stays in at least 75%. G = 2 reported only.
Y6. Cut, G = 4, run 800. Off the core at x = 8: core piece 1 in at least 75%, other piece 0 in at least 90%, other piece holds together, |mean| >= .5, in at least 75%. Through the core at x = 1: both 0 in at least 75%, each holding in at least 75%. G = 2 reported only.
Y7. Boundary held turning twice, G = 2, run 500: 2 zeros at least 3 sites apart in at least 75%. G = 4 reported only.
Y8. Ring n = 128, r = 8, s = .1, .2, .4, .6, .8, 1, G = 2, 3, 4, 8: winding 1 and spread 1 - |mean z| / mean |z| >= .9 in at least 90%. G = 4: one part pushed opposite for 20 returns to its place within .1 rad in at least 90%.
Y9. Common pull, G = 4: the pull that ends the winding lies between .25 and 1.1 of u_c = 2.147; at 1.1 times it, a site's amplitude has passed .3 or lower in at least 75% of the seeds lost.
Y10. From noise, nothing placed, G = 4. Ring r = 2: wound in .1 to .8 of 64 seeds; r = 30: at most .1. Disk free edge, run 500: any zero in at least 50%. Exactly one, and G = 2, reported only.

ADDED AFTER SEEING THE RESULTS ABOVE, predictions frozen before these ran. Seen so far: Y1, Y3 to Y8, Y10 passed; Y2, Y9 missed. Y2: last c holding .061, .084, .094, .114 against .051, .054, .054, .054. Y9: the pull that ends the winding is .316 at G = 4, below my bracket, .15 of u_c.
F1. Y2's miss is run length. Just past the limit the growth is very slow and that run lasted 1500. With a run of 8000, G = 2, 4, 8: last c holding within .02 of the solver.
F2. After the fact, Y9 is the range limit again. A common pull bunches the turn into a kink, until its steepest step reaches the same limit as Y1, 2 pi sigma_c per r sites. Phase stiffness r^2 / 6 and pull u / (G m) give a kink of width r sqrt(G / (6 u)) with steepest step 2 / width, so u_end = G (2 pi sigma_c)^2 / 24, which does not depend on r: .137, .308, .520, 1.41 at G = 2, 3, 4, 8. Measured .316 at G = 4 is .61 of that. So: u_end at r = 4, 8, 16, G = 4, within 25% of each other; and its ratio to that formula within 30% of .61 at G = 2, 3, 8.
F3. Connection through a mean is not neighbour connection. Two wound rings, each reading the other's mean at share s and its own neighbours at the rest. Each mean is 0, so at first nothing passes. But the shared mode is the same as Y2's. G = 4, run 8000: last s holding within .02 of .054, far below s_hold(4) = .310 for real-valued blocks.
Results of those: F2 passed: u_end .324, .316, .293 at r = 4, 8, 16; ratios .60, .62, .53. F1 and F3 missed. F1: last c holding .061, .094, .104 or more at G = 2, 4, 8. F3: last s holding .09. My explanation was wrong: at Y2's last c the solver's growth rate gives 9 to 55 e-folds in 1500, so run length was not the cause.
F4. So the solver's limit may be where the balance goes, not where the winding goes. Past it the node's reading |h| leaves 0, and it then acts on its own parts as a common pull of c G |h|. The winding goes only when that reaches u_end. G = 2, 4, 8, run 2000, c = .02 to .2: first c with median |h| >= .1 within .02 of .051, .054, .054. At the last c holding the winding, c G |h| within 30% of u_end .082, .316, .754.
"""
import json
import os
import sys
import time
from math import atanh, pi, sqrt, tanh
from multiprocessing import Pool
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np

DT = .05
SIGMA = .02
SPREAD = .05
GS = (2.0, 3.0, 4.0, 8.0)


def flip_u(G):
    if G <= 1:
        return 0.0
    m = sqrt(1 - 1 / G)
    return abs(atanh(m) - G * m)


def seed_of(*v):
    return np.random.default_rng([abs(int(round(a * 1000))) for a in v])


def verdict(ok):
    return "PASS" if ok else "MISS"


def wrap(a):
    return (a + pi) % (2 * pi) - pi


def lim(w):
    """Leak and limit with a phase: the limit acts on the amplitude, the phase is free. lim(0) = 0."""
    a = np.abs(w)
    return np.tanh(a) * w / np.maximum(a, 1e-12)


def cnoise(rng, shape):
    return rng.standard_normal(shape) + 1j * rng.standard_normal(shape)


# ---------- Ring ----------
def ring_w(n, r):
    if 2 * r >= n - 1:
        return (1 - np.eye(n)) / (n - 1)
    W = np.zeros((n, n))
    for j in range(n):
        for k in range(1, r + 1):
            W[j, (j + k) % n] = W[j, (j - k) % n] = 1 / (2 * r)
    return W


def ring_rest(n, q, G, W, c=0.0, s=1.0):
    th = 2 * pi * q * np.arange(n) / n
    D = float(np.real((W[0] * np.exp(1j * (th - th[0]))).sum()))
    gain = G * (1 - c) * ((1 - s) + s * D)
    m = 1.0
    for _ in range(40000):
        m = tanh(gain * m)
    return m, th


def stable(n, q, G, W, c=0.0, s=1.0):
    """Linear stability of the wound state, relay eliminated. No sites simulated."""
    m, th = ring_rest(n, q, G, W, c, s)
    if m < 1e-3:
        return False
    Wt = (1 - c) * ((1 - s) * np.eye(n) + s * W) + c * np.ones((n, n)) / n
    z = m * np.exp(1j * th)
    w = G * Wt @ z
    a = np.abs(w)
    ux, uy = np.real(w) / a, np.imag(w) / a
    rho, tau = 1 / np.cosh(a) ** 2, np.tanh(a) / a
    J = -np.eye(2 * n)
    for j in range(n):
        Dj = np.array([[rho[j] * ux[j] ** 2 + tau[j] * uy[j] ** 2, (rho[j] - tau[j]) * ux[j] * uy[j]], [(rho[j] - tau[j]) * ux[j] * uy[j], rho[j] * uy[j] ** 2 + tau[j] * ux[j] ** 2]])
        J[2 * j:2 * j + 2, ::2] += G * Dj[:, [0]] * Wt[j]
        J[2 * j:2 * j + 2, 1::2] += G * Dj[:, [1]] * Wt[j]
    return float(np.linalg.eigvals(J).real.max()) < 1e-7


def r_limit(G, q, n=128):
    last = 0
    for r in range(1, n // 2):
        if stable(n, q, G, ring_w(n, r)):
            last = r
        elif last:
            break
    return last


def c_limit(G, q=1, n=128, r=8):
    W = ring_w(n, r)
    lo, hi = 0.0, 1.0
    for _ in range(12):
        mid = (lo + hi) / 2
        if stable(n, q, G, W, c=mid):
            lo = mid
        else:
            hi = mid
    return lo


def solve():
    print("Ring, n = 128. Largest neighbour range r at which the wound state is stable, and r / n")
    for G in GS:
        print(f"  G {G:g}: q 1: r {r_limit(G,1)} ({r_limit(G,1)/128:.3f}); q 2: r {r_limit(G,2)} ({r_limit(G,2)/128:.3f}); u_c {flip_u(G):.3f}")
    print("Ring with a hub, n = 128, r = 8. Largest share c through the hub, and 1 - 1/(G D)")
    W = ring_w(128, 8)
    th = 2 * pi * np.arange(128) / 128
    D = float(np.real((W[0] * np.exp(1j * (th - th[0]))).sum()))
    print(f"  D {D:.4f}")
    for G in GS:
        print(f"  G {G:g}: c limit {c_limit(G):.3f}; amplitude limit {1-1/(G*D):.3f}")
    print("Own share 1 - s, n = 128, r = 8: stable at s = .1 to 1")
    for G in GS:
        print(f"  G {G:g}: " + ", ".join(f"{s:g}:{stable(128,1,G,W,s=s)}" for s in (.1, .2, .4, .6, .8, 1.0)))


def winding(z):
    a = np.angle(z)
    return np.rint(wrap(np.roll(a, -1, axis=-1) - a).sum(-1) / (2 * pi)).astype(int)


def ring_run(z, W, G, T, rng, c=0.0, s=1.0, u=0.0, push=None, sigma=SIGMA):
    Wt = W.T
    minamp = np.full(z.shape[0], np.inf)
    for t in range(int(T / DT)):
        rd = z @ Wt
        if s < 1:
            rd = (1 - s) * z + s * rd
        if c:
            rd = (1 - c) * rd + c * z.mean(1, keepdims=True)
        w = G * rd + u
        if push is not None and t * DT < push[1]:
            w = w + push[0]
        z = z + DT * (-z + lim(w)) + sqrt(DT) * sigma * cnoise(rng, z.shape)
        minamp = np.minimum(minamp, np.abs(z).min(1))
    return z, minamp


def wound(n, B, q, m, rng, th=None):
    th = 2 * pi * q * np.arange(n) / n if th is None else th
    return m * np.exp(1j * th)[None, :] + SPREAD * cnoise(rng, (B, n))


def job_ring(_o):
    """Y1."""
    ok = True
    n = 128
    for G in GS:
        rc = r_limit(G, 1)
        rs = sorted(set(int(round(rc * f)) for f in (.5, .7, .85, .95, 1.0, 1.05, 1.15, 1.3, 1.6) if 1 <= round(rc * f) < n // 2))
        last = 0
        for r in rs:
            W = ring_w(n, r)
            rng = seed_of(1, G, r)
            m, _ = ring_rest(n, 1, G, W)
            z, _a = ring_run(wound(n, 8, 1, max(m, .2), rng), W, G, 400, rng)
            if np.mean(winding(z) == 1) >= .75:
                last = r
        good = abs(last - rc) <= max(.1 * rc, 2)
        ok &= good
        print(f"  G {G:g}: last range holding {last}; solver {rc}")
    for G in GS:
        rng = seed_of(1, G, 99)
        nn = 64
        W = ring_w(nn, nn)
        z, _a = ring_run(wound(nn, 8, 1, .9, rng), W, G, 300, rng)
        q1 = winding(z)
        amp1 = np.abs(z.mean(1))
        z2, _a = ring_run(wound(nn, 8, 1, .9, rng), np.zeros((nn, nn)), G, 300, rng, c=1.0)
        q2 = winding(z2)
        amp2 = np.abs(z2.mean(1))
        good = (q1 == 0).all() and (q2 == 0).all()
        ok &= good
        print(f"  G {G:g}: wound list ends q {sorted(set(q1.tolist()))}, mean amplitude {float(amp1.mean()):.3f}; wound star ends q {sorted(set(q2.tolist()))}, mean amplitude {float(amp2.mean()):.3f}")
    return ok


def hub_cell(job):
    G, c = job
    n, r = 128, 8
    W = ring_w(n, r)
    rng = seed_of(2, G, c)
    m2, _ = ring_rest(n, 1, G, W, c=float(c))
    z, _a = ring_run(wound(n, 8, 1, max(m2, .2), rng), W, G, 1500, rng, c=float(c))
    return G, float(c), float(np.mean(winding(z) == 1))


def job_hub(_o):
    """Y2."""
    ok = True
    n, r = 128, 8
    W = ring_w(n, r)
    tasks = []
    limits = {}
    for G in GS:
        rng = seed_of(2, G)
        m, _ = ring_rest(n, 1, G, W)
        z, _a = ring_run(wound(n, 8, 1, m, rng), W, G, 200, rng)
        h = float(np.abs(z.mean(1)).max())
        ok &= h <= .05
        print(f"  G {G:g}: centre reading the whole ring, largest |h| {h:.4f}; amplitude of parts {float(np.abs(z).mean()):.3f}", flush=True)
        cl = c_limit(G)
        limits[G] = cl
        tasks += [(G, round(float(c), 3)) for c in np.arange(max(cl - .04, 0), cl + .09, .01)]
    with Pool(8) as p:
        res = p.map(hub_cell, tasks)
    for G in GS:
        cl = limits[G]
        cells = sorted((c, f) for g, c, f in res if g == G)
        held = [c for c, f in cells if f >= .75]
        last = max(held) if held else 0.0
        good = abs(last - cl) <= .02
        ok &= good
        c2 = cl + .1
        rng = seed_of(2, G, 77)
        z, _a = ring_run(wound(n, 8, 1, .5, rng), W, G, 800, rng, c=c2)
        ends = float(np.mean((winding(z) == 0) & (np.abs(z.mean(1)) >= .5)))
        ok &= ends >= .75
        print(f"  G {G:g}: last c holding the winding {last:.3f}; solver {cl:.3f}; at c = {c2:.3f} ends in one consensus through the node in {ends:.2f}", flush=True)
    return ok


# ---------- Disk ----------
class Disk:
    def __init__(self, R=16, cx=.5, cy=.5):
        self.R = R
        L = 2 * R + 2
        y, x = np.mgrid[0:L, 0:L]
        self.x = x - R + 0.0
        self.y = y - R + 0.0
        self.cx, self.cy = cx, cy
        self.mask = (self.x - cx) ** 2 + (self.y - cy) ** 2 < R * R
        self.phi = np.arctan2(self.y - cy, self.x - cx)
        self.rad = np.hypot(self.x - cx, self.y - cy)
        self.label = np.ones_like(self.x, dtype=int)
        self.build()

    def build(self):
        self.adj = []
        for ax, sh in ((0, 1), (0, -1), (1, 1), (1, -1)):
            nb_m = np.roll(self.mask, sh, axis=ax)
            nb_l = np.roll(self.label, sh, axis=ax)
            self.adj.append((ax, sh, self.mask & nb_m & (nb_l == self.label)))
        self.cnt = sum(a.astype(float) for _x, _s, a in self.adj)

    def placed(self, B, q, m, rng):
        f = np.tanh(self.rad / 2)
        z = m * f * np.exp(1j * q * self.phi)
        z = z[None] + SPREAD * cnoise(rng, (B, *self.x.shape))
        return z * self.mask

    def reading(self, z):
        s = 0
        for ax, sh, a in self.adj:
            s = s + np.roll(z, sh, axis=ax + 1) * a
        return s / np.maximum(self.cnt, 1)

    def run(self, z, G, T, rng, pinned=None, pinval=None, clamp=None, clampval=None, sigma=SIGMA):
        for _ in range(int(T / DT)):
            z = z + DT * (-z + lim(G * self.reading(z))) + sqrt(DT) * sigma * cnoise(rng, z.shape)
            z = z * self.mask
            if pinned is not None:
                z[:, pinned] = pinval
            if clamp is not None:
                z[clamp] = clampval
        return z

    def charges(self, z):
        """Plaquette charges: integers by construction, since each is a sum of wrapped phase steps round a closed square."""
        a = np.angle(z)
        d1 = wrap(np.roll(a, -1, axis=2) - a)
        d2 = wrap(np.roll(np.roll(a, -1, axis=2), -1, axis=1) - np.roll(a, -1, axis=2))
        d3 = wrap(np.roll(a, -1, axis=1) - np.roll(np.roll(a, -1, axis=2), -1, axis=1))
        d4 = wrap(a - np.roll(a, -1, axis=1))
        ch = np.rint((d1 + d2 + d3 + d4) / (2 * pi)).astype(int)
        m = self.mask
        l = self.label
        ok = m & np.roll(m, -1, 1) & np.roll(m, -1, 0) & np.roll(np.roll(m, -1, 1), -1, 0)
        ok = ok & (l == np.roll(l, -1, 1)) & (l == np.roll(l, -1, 0)) & (l == np.roll(np.roll(l, -1, 1), -1, 0))
        return ch * ok

    def loop(self, z, h):
        """Winding along a square loop of half-side h round the centre, skipping missing sites."""
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
        pts = [p for p in pts if self.mask[p]]
        v = np.stack([z[:, p[0], p[1]] for p in pts], axis=1)
        return winding(v)


def rest(G):
    m = 1.0
    for _ in range(20000):
        m = tanh(G * m)
    return m


def job_boundary(_o):
    """Y3."""
    ok = True
    for G in (2.0, 4.0):
        for q in (0, 1):
            d = Disk()
            rng = seed_of(3, G, q)
            shell = d.mask & (d.rad >= d.R - 1.5)
            pinval = rest(G) * np.exp(1j * q * d.phi[shell])
            z = .5 * np.exp(2j * pi * rng.random((8, *d.x.shape))) * d.mask
            z[:, shell] = pinval
            z = d.run(z, G, 500, rng, shell, pinval)
            ch = d.charges(z)
            net = ch.sum((1, 2))
            cnt = np.abs(ch).sum((1, 2))
            fr = float(np.mean(cnt == abs(q)))
            good = (net == q).all() and fr >= .5
            ok &= good
            amin = float(np.median((np.abs(z) + (~d.mask) * 9).min((1, 2))))
            print(f"  G {G:g}, boundary turning {q}: net charge {sorted(set(net.tolist()))}; exactly |q| zeros in {fr:.2f}; counts {sorted(set(cnt.tolist()))}; smallest amplitude {amin:.3f}")
    return ok


def job_node(_o):
    """Y4."""
    ok = True
    for G in (2.0, 4.0):
        d = Disk()
        rng = seed_of(4, G)
        m = rest(G)
        idx = np.argwhere(d.mask)
        core = np.argwhere(d.mask & (d.rad < 1))
        pick = rng.choice(len(idx), 12, replace=False)
        sites = np.vstack([core, idx[pick]])
        B = len(sites)
        z0 = d.placed(B, 1, m, rng)
        z0 = d.run(z0, G, 100, rng)
        clamp = np.zeros_like(d.mask, shape=(B, *d.x.shape))
        val = np.zeros(B, complex)
        for b, (i, j) in enumerate(sites):
            clamp[b, i, j] = True
            val[b] = -z0[b, i, j]
        z1 = z0.copy()
        for _ in range(int(60 / DT)):
            z1 = z1 + DT * (-z1 + lim(G * d.reading(z1))) + sqrt(DT) * SIGMA * cnoise(rng, z1.shape)
            z1 = z1 * d.mask
            z1[clamp] = val
        turned = (np.abs(wrap(np.angle(z1) - np.angle(z0))) > pi / 2) & d.mask
        fr = turned.sum((1, 2)) / d.mask.sum()
        z2 = d.run(z1, G, 100, rng)
        net = d.charges(z2).sum((1, 2))
        a = float(np.mean(net == 1))
        good = a >= .9 and float(fr.max()) <= .10
        ok &= good
        print(f"  G {G:g}: clamp any site opposite: largest share of sites turned {float(fr.max()):.3f}, core sites {float(fr[:len(core)].max()):.3f}; charge 1 afterward in {a:.2f}")
        # Core removed.
        d2 = Disk()
        d2.mask = d2.mask & (d2.rad >= 1)
        d2.build()
        rng = seed_of(4, G, 5)
        z = d2.placed(8, 1, m, rng)
        z = d2.run(z, G, 200, rng)
        q2 = d2.loop(z, 6)
        a2 = float(np.mean(q2 == 1))
        ok &= a2 >= .9
        # 5% of sites removed at random.
        d3 = Disk()
        rng = seed_of(4, G, 6)
        d3.mask = d3.mask & (rng.random(d3.mask.shape) > .05)
        d3.build()
        z = d3.placed(8, 1, m, rng)
        z = d3.run(z, G, 200, rng)
        q3 = d3.loop(z, 10)
        a3 = float(np.mean(q3 == 1))
        ok &= a3 >= .9
        print(f"  G {G:g}: core sites removed, loop winding 1 in {a2:.2f}; 5% removed at random, loop winding 1 in {a3:.2f}")
    return ok


def job_free(_o):
    """Y5."""
    ok = True
    for G in (2.0, 4.0):
        d = Disk()
        rng = seed_of(5, G)
        z = d.placed(8, 1, rest(G), rng)
        z = d.run(z, G, 1000, rng)
        ch = d.charges(z)
        net = ch.sum((1, 2))
        a = float(np.mean(net == 1))
        if G == 4.0:
            ok &= a >= .75
        print(f"  G {G:g}: free edge, run 1000: charge 1 stays in {a:.2f}")
    return ok


def job_cut(_o):
    """Y6."""
    ok = True
    for G in (2.0, 4.0):
        m = rest(G)
        for lab, x0 in (("off the core, x = 8", 8), ("through the core, x = 1", 1)):
            d = Disk()
            rng = seed_of(6, G, x0)
            z = d.placed(8, 1, m, rng)
            z = d.run(z, G, 50, rng)
            d.label = (d.x >= x0).astype(int)
            d.build()
            z = d.run(z, G, 800, rng)
            ch = d.charges(z)
            left = (ch * (d.x < x0)).sum((1, 2))
            right = (ch * (d.x >= x0)).sum((1, 2))
            hl = np.abs((z * (d.mask & (d.x < x0))).sum((1, 2))) / (d.mask & (d.x < x0)).sum()
            hr = np.abs((z * (d.mask & (d.x >= x0))).sum((1, 2))) / (d.mask & (d.x >= x0)).sum()
            if x0 == 8:
                a, b, c = float(np.mean(left == 1)), float(np.mean(right == 0)), float(np.mean(hr >= .5))
                if G == 4.0:
                    ok &= a >= .75 and b >= .9 and c >= .75
                print(f"  G {G:g}, {lab}: core piece charge 1 in {a:.2f}; other piece charge 0 in {b:.2f}, holds together in {c:.2f}")
            else:
                a, b, c = float(np.mean((left == 0) & (right == 0))), float(np.mean(hl >= .5)), float(np.mean(hr >= .5))
                if G == 4.0:
                    ok &= a >= .75 and b >= .75 and c >= .75
                print(f"  G {G:g}, {lab}: both pieces charge 0 in {a:.2f}; each holds together in {b:.2f}, {c:.2f}; charges seen {sorted(set(left.tolist()+right.tolist()))}")
    return ok


def job_two(_o):
    """Y7."""
    ok = True
    for G in (2.0, 4.0):
        d = Disk()
        rng = seed_of(7, G)
        shell = d.mask & (d.rad >= d.R - 1.5)
        pinval = rest(G) * np.exp(2j * d.phi[shell])
        z = d.placed(8, 2, rest(G), rng)
        z[:, shell] = pinval
        z = d.run(z, G, 500, rng, shell, pinval)
        ch = d.charges(z)
        seps = []
        counts = []
        for b in range(8):
            pos = np.argwhere(ch[b] != 0)
            counts.append(len(pos))
            seps.append(float(np.hypot(*(pos[0] - pos[1]))) if len(pos) == 2 else 0.0)
        a = float(np.mean([(c == 2 and s >= 3) for c, s in zip(counts, seps)]))
        if G == 2.0:
            ok &= a >= .75
        print(f"  G {G:g}: two turns of boundary: zeros {sorted(set(counts))}; separation, median {float(np.median(seps)):.1f}; 2 zeros at least 3 apart in {a:.2f}")
    return ok


def job_connect(_o):
    """Y8."""
    ok = True
    n, r = 128, 8
    W = ring_w(n, r)
    for G in GS:
        row = []
        for s in (.1, .2, .4, .6, .8, 1.0):
            rng = seed_of(8, G, s)
            m, _ = ring_rest(n, 1, G, W, s=s)
            z, _a = ring_run(wound(n, 8, 1, m, rng), W, G, 300, rng, s=s)
            q = winding(z)
            spread = 1 - np.abs(z.mean(1)) / np.abs(z).mean(1)
            a = float(np.mean((q == 1) & (spread >= .9)))
            ok &= a >= .9
            row.append(f"s {s:g}: {a:.2f}")
        print(f"  G {G:g}: wound and spread: " + "; ".join(row))
    # One part pushed: it goes back to its place.
    G = 4.0
    rng = seed_of(8, 99)
    m, th = ring_rest(n, 1, G, W)
    z = wound(n, 8, 1, m, rng)
    z, _a = ring_run(z, W, G, 50, rng)
    ref = z.copy()
    p = np.zeros(n, complex)
    p[0] = -6 * np.exp(1j * th[0])
    z2, _a = ring_run(z, W, G, 200, rng, push=(p, 20))
    err = np.abs(wrap(np.angle(z2[:, 0]) - np.angle(z2[:, 1]) - (th[0] - th[1])))
    a = float(np.mean(err <= .1))
    ok &= a >= .9
    print(f"  G 4: one part pushed opposite then released: back in its place in {a:.2f}; largest error {float(err.max()):.3f}")
    return ok


def job_pull(_o):
    """Y9."""
    n, r, G = 128, 8, 4.0
    W = ring_w(n, r)
    lo, hi = 0.0, 8.0
    m, _ = ring_rest(n, 1, G, W)
    for _ in range(10):
        mid = (lo + hi) / 2
        rng = seed_of(9, mid)
        z, _a = ring_run(wound(n, 8, 1, m, rng), W, G, 300, rng, u=mid)
        if np.median(winding(z)) == 1:
            lo = mid
        else:
            hi = mid
    th = (lo + hi) / 2
    rng = seed_of(9, 99)
    z, a = ring_run(wound(n, 8, 1, m, rng), W, G, 300, rng, u=th * 1.1)
    lost = winding(z) != 1
    amp = float(np.mean(a[lost] <= .3)) if lost.any() else 0.0
    ok = (.25 * flip_u(G) <= th <= 1.1 * flip_u(G)) and amp >= .75
    print(f"  G 4: common pull that ends the winding {th:.3f}; u_c {flip_u(G):.3f}; a site passed near 0 in {amp:.2f} of those lost")
    return ok


def birth_ring(job):
    r, seed = job
    n, G = 128, 4.0
    W = ring_w(n, r)
    rng = seed_of(10, r, seed)
    z = .05 * cnoise(rng, (1, n))
    z, _a = ring_run(z, W, G, 400, rng)
    return int(winding(z)[0])


def job_birth(_o):
    """Y10."""
    ok = True
    with Pool(8) as p:
        for r, lo, hi in ((2, .1, .8), (4, None, None), (30, 0.0, .1)):
            q = p.map(birth_ring, [(r, s) for s in range(64)])
            fr = float(np.mean(np.array(q) != 0))
            if lo is not None:
                ok &= lo <= fr <= hi
            print(f"  Ring from noise, r {r}: wound in {fr:.2f}; windings {sorted(set(q))}")
    for G in (2.0, 4.0):
        d = Disk()
        rng = seed_of(10, G)
        z = .05 * cnoise(rng, (16, *d.x.shape)) * d.mask
        z = d.run(z, G, 500, rng)
        ch = d.charges(z)
        cnt = np.abs(ch).sum((1, 2))
        net = ch.sum((1, 2))
        a = float(np.mean(cnt >= 1))
        one = float(np.mean(cnt == 1))
        if G == 4.0:
            ok &= a >= .5
        print(f"  Disk from noise, G {G:g}: any zero in {a:.2f}; exactly one in {one:.2f}; counts {sorted(set(cnt.tolist()))}; net {sorted(set(net.tolist()))}")
    return ok


def max_eig(n, q, G, W, c=0.0):
    m, th = ring_rest(n, q, G, W, c)
    Wt = (1 - c) * W + c * np.ones((n, n)) / n
    z = m * np.exp(1j * th)
    w = G * Wt @ z
    a = np.abs(w)
    ux, uy = np.real(w) / a, np.imag(w) / a
    rho, tau = 1 / np.cosh(a) ** 2, np.tanh(a) / a
    J = -np.eye(2 * n)
    for j in range(n):
        Dj = np.array([[rho[j] * ux[j] ** 2 + tau[j] * uy[j] ** 2, (rho[j] - tau[j]) * ux[j] * uy[j]], [(rho[j] - tau[j]) * ux[j] * uy[j], rho[j] * uy[j] ** 2 + tau[j] * ux[j] ** 2]])
        J[2 * j:2 * j + 2, ::2] += G * Dj[:, [0]] * Wt[j]
        J[2 * j:2 * j + 2, 1::2] += G * Dj[:, [1]] * Wt[j]
    return float(np.linalg.eigvals(J).real.max())


def long_cell(job):
    G, c = job
    n, r = 128, 8
    W = ring_w(n, r)
    rng = seed_of(31, G, c)
    m2, _ = ring_rest(n, 1, G, W, c=float(c))
    z, _a = ring_run(wound(n, 4, 1, max(m2, .2), rng), W, G, 8000, rng, c=float(c))
    return "hub", G, float(c), float(np.mean(winding(z) == 1))


def pair_cell(job):
    G, sh = job
    n, r = 128, 8
    W = ring_w(n, r)
    Wt = W.T
    rng = seed_of(33, G, sh)
    m2, _ = ring_rest(n, 1, G, W, c=float(sh))
    B = 4
    a = wound(n, B, 1, max(m2, .2), rng)
    b = wound(n, B, 1, max(m2, .2), rng)
    for _ in range(int(8000 / DT)):
        ma, mb = a.mean(1, keepdims=True), b.mean(1, keepdims=True)
        ra = (1 - sh) * (a @ Wt) + sh * mb
        rb = (1 - sh) * (b @ Wt) + sh * ma
        a = a + DT * (-a + lim(G * ra)) + sqrt(DT) * SIGMA * cnoise(rng, a.shape)
        b = b + DT * (-b + lim(G * rb)) + sqrt(DT) * SIGMA * cnoise(rng, b.shape)
    return "pair", G, float(sh), float(np.mean((winding(a) == 1) & (winding(b) == 1)))


def run_cell(job):
    return long_cell(job[1:]) if job[0] == "hub" else pair_cell(job[1:])


def job_f1(_o):
    """F1 and F3."""
    ok = True
    n, r = 128, 8
    W = ring_w(n, r)
    tasks = []
    lims = {}
    for G in (2.0, 4.0, 8.0):
        cl = c_limit(G)
        lims[G] = cl
        for c, was in zip((.061, .084, .094, .114), (2.0, 3.0, 4.0, 8.0)):
            if was == G:
                print(f"  G {G:g}: solver growth rate at Y2's last c = {c}: {max_eig(n,1,G,W,c=c):.5f}; e-folds in a run of 1500: {1500*max_eig(n,1,G,W,c=c):.1f}", flush=True)
        tasks += [("hub", G, round(float(x), 3)) for x in np.arange(max(cl - .02, 0), cl + .05, .01)]
    tasks += [("pair", 4.0, x) for x in (.03, .05, .06, .07, .09, .12)]
    with Pool(8) as p:
        res = p.map(run_cell, tasks)
    for G in (2.0, 4.0, 8.0):
        cells = sorted((c, f) for k, g, c, f in res if k == "hub" and g == G)
        held = [c for c, f in cells if f >= .75]
        last = max(held) if held else 0.0
        ok1 = abs(last - lims[G]) <= .02
        print(f"  F1, G {G:g}, run 8000: last c holding {last:.3f}; solver {lims[G]:.3f}; {verdict(ok1)}; cells {[(c, round(f, 2)) for c, f in cells]}", flush=True)
        ok &= ok1
    cells = sorted((c, f) for k, g, c, f in res if k == "pair")
    held = [c for c, f in cells if f >= .75]
    last = max(held) if held else 0.0
    ok3 = abs(last - .054) <= .02
    print(f"  F3, G 4, two wound rings reading each other's mean: last s holding {last:.3f}; predicted .054; s_hold {.310}; {verdict(ok3)}; cells {[(c, round(f, 2)) for c, f in cells]}", flush=True)
    return ok and ok3


def pull_cell(job):
    G, r = job
    n = 128
    W = ring_w(n, r)
    m, _ = ring_rest(n, 1, G, W)
    lo, hi = 0.0, 8.0
    for _ in range(10):
        mid = (lo + hi) / 2
        rng = seed_of(32, G, r, mid)
        z, _a = ring_run(wound(n, 8, 1, m, rng), W, G, 300, rng, u=mid)
        if np.median(winding(z)) == 1:
            lo = mid
        else:
            hi = mid
    return G, r, (lo + hi) / 2


def job_f2(_o):
    """F2."""
    ok = True
    sig = {2.0: 26 / 128, 3.0: 32 / 128, 4.0: 36 / 128, 8.0: 42 / 128}
    with Pool(8) as p:
        res = p.map(pull_cell, [(4.0, 4), (4.0, 8), (4.0, 16), (2.0, 8), (3.0, 8), (8.0, 8)])
    rs = [u for G, r, u in res if G == 4.0]
    print(f"  G 4, r 4, 8, 16: u_end {[round(u, 3) for u in rs]}", flush=True)
    ok &= max(rs) / min(rs) <= 1.25
    for G, r, u in res:
        if G != 4.0:
            f = G * (2 * pi * sig[G]) ** 2 / 24
            ratio = u / f
            print(f"  G {G:g}, r 8: u_end {u:.3f}; formula {f:.3f}; ratio {ratio:.2f}; u_c {flip_u(G):.3f}", flush=True)
            ok &= abs(ratio - .61) <= .3 * .61
    return ok


def bal_cell(job):
    G, c = job
    n, r = 128, 8
    W = ring_w(n, r)
    rng = seed_of(34, G, c)
    m2, _ = ring_rest(n, 1, G, W, c=float(c))
    z, _a = ring_run(wound(n, 4, 1, max(m2, .2), rng), W, G, 2000, rng, c=float(c))
    return G, float(c), float(np.median(np.abs(z.mean(1)))), float(np.mean(winding(z) == 1))


def job_f4(_o):
    """F4."""
    ok = True
    ue = {2.0: .082, 4.0: .316, 8.0: .754}
    tasks = [(G, round(float(c), 3)) for G in ue for c in np.arange(.02, .205, .01)]
    with Pool(8) as p:
        res = p.map(bal_cell, tasks)
    for G in ue:
        cells = sorted((c, h, f) for g, c, h, f in res if g == G)
        first = next((c for c, h, f in cells if h >= .1), float("inf"))
        held = [(c, h) for c, h, f in cells if f >= .75]
        lc, lh = held[-1] if held else (0.0, 0.0)
        pull = lc * G * lh
        a = abs(first - c_limit(G)) <= .02
        b = abs(pull - ue[G]) <= .3 * ue[G]
        ok &= a and b
        print(f"  G {G:g}: balance goes at c = {first:.3f}, solver {c_limit(G):.3f}, {verdict(a)}; winding last at c = {lc:.3f}, |h| {lh:.3f}, pull {pull:.3f} against u_end {ue[G]:.3f}, {verdict(b)}", flush=True)
        print("    " + "; ".join(f"{c:.2f}: h {h:.2f}, q1 {f:.2f}" for c, h, f in cells), flush=True)
    return ok


JOBS = {"ring": ("Y1", job_ring), "hub": ("Y2", job_hub), "boundary": ("Y3", job_boundary), "node": ("Y4", job_node), "free": ("Y5", job_free), "cut": ("Y6", job_cut), "two": ("Y7", job_two), "connect": ("Y8", job_connect), "pull": ("Y9", job_pull), "birth": ("Y10", job_birth), "f1": ("F1, F3", job_f1), "f2": ("F2", job_f2), "f4": ("F4", job_f4)}


if __name__ == "__main__":
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    which = sys.argv[2:] or list(JOBS)
    res = {}
    for w in which:
        if w == "solve":
            solve()
            continue
        name, fn = JOBS[w]
        t0 = time.time()
        ok = fn(None)
        res[name] = bool(ok)
        print(f"{name} {verdict(ok)}; {time.time()-t0:.0f}s", flush=True)
    with open(os.path.join(outdir, "results_" + "_".join(which) + ".json"), "w") as f:
        json.dump(res, f)
