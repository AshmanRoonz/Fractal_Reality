"""Parts with their own 0: circumpuncts all the way down. Predictions frozen before any noisy run of this script.

Created: 2026-11-05
Last updated: 2026-11-05
Version: 1.0
History: 2026-11-05 v1.0: initial, after Ashman said: "Yes, parts have their own center. Circumpuncts all the way down." The theory is a Claude Doc, https://claude.ai/artifact/58ahYtFyKbQtDHEggdvEte

Results: U1, U2, U3, U4 passed; U5, U6 missed. U1: all 11 cells in every seed, three levels included. U2: N = 5 held in every seed and N = 4 in none, at both gains. U4: smallest port amplitude .877 and .805 at G = 2, against .601 plain. U5: slope .024, .128, .040, .203. U6: lit .051, .609, .271; net -3 at spacing 12.
After the follow-ups: F1, F2, F4 passed; F3 missed. F1: rank .929. F2: 3 opposite zeros in every seed at t = 20, net 1 throughout, 3 zeros at t = 500. F3: 13 alike fell to 5 at G = 4 and 3 at G = 2. F4: 1 of 5 fed centres kept its own turn.
Totals: 10 frozen, 7 passed, 3 missed. The gain in a part is only read as power through its own centre, since the law has no term for where gain comes from. No real system was measured.

Needs numpy. All data are synthetic.
Run: python -I wholeness_nested_v1.py OUTDIR [solve hold floor depend disk flow plane f1 f2 f3 f4]
"solve" finds noise-free fixed points and reads their linear stability. It uses no noise and scores nothing, and was run before the predictions were written.

WHY. wholeness_input_v1.py found that a whole fed only through its centre stays its centre's size, and left open whether power through each part's own centre does better. Canon: "From scale Lambda, the part appears as a point of convergence in the greater whole", and the part's boundary is the whole's field at contact.

HAND DERIVATIONS.
(a) A part cannot be read by its mean. The mean of a wound part is 0 (F3 in wholeness_zero_v1.py). So what a part gives the whole is its rotation: turn the whole part by psi and its own turn is unchanged. The whole can reach psi only at a contact. So the rule of wholeness_flow_v1.py recurs one level up: the parts' rotations exp(i psi) add to 0, and their steps add to one turn.
(b) In one shared field charges add. A loop round many zeros winds by their sum. So parts all turning alike, in one field, force a boundary of N turns, and that field has no single greater 0. A boundary turning once round K centres turning alike forces at least K - 1 opposite zeros between them.
(c) Parts with their own interior, joined at one contact. Give each part its own ring, and let the whole's ring pass through one site of each. Every tie then lies on exactly one loop, so every loop has its own whole number. So each part can have 1 and the whole can have 1, or any pair of numbers. Noise-free fixed points agree: q, Q = (1, 1), (1, 0), (0, 1), (1, 2), (1, -1), (-1, 1), (0, 0) are all stable at G = 4, n = 8, N = 16. The same recurses to three levels. Canon's "Bodies are shared; centres are not" fits, as a reading.
(d) The floor comes down. Rigid parts rotating against each other need only cos(2 pi / N) > 0, so N >= 5 at any gain, since the amplitude belongs to the parts. Noise-free: stable from N = 5 at G = 2 and G = 4, against 9 and 6 for a plain ring. At G = 2, t = .95 it fails, and t up to .9 is stable.
(e) Reach. Whole ties carry no power, so a whole of many parts needs nothing extra. In a plane, fed centres with halos of about 8 sites should light a disk at spacing 12, and leave gaps at 24. I read the gain in a part as power through that part's own centre. That is a reading: the law has no term that says where a part's gain comes from.
(f) Nesting is allowed and not required. The whole's 1 does not need its parts to have 1s: (q, Q) = (0, 1) is stable. So this test cannot show circumpuncts all the way down have to be so, only that they can be.
(g) Dependence runs one way. Cut the whole's ties and the parts go on. Remove one part from a ring and the whole's loop opens, so its turn unwinds, while the others keep theirs. A disk of parts should stand that as the plain disk did.
(h) Nesting may quench flow. Flow came from an amplitude deficit at the core. A part with its own hold has less deficit, so at small t the whole's slope should be near 0, and it should rise with t. So parts with their own centres may stop the whole's flow, as a rich core did.

PREDICTIONS. Noise .02, input spread .05. Rings at G = 4, n = 8 or G = 2, n = 12. t is the port's share through the whole.
U1. Ring of rings, run 1500, 8 seeds, every ring and the whole at their numbers in at least 90%: (G, n, N, t, q, Q) = (2, 12, 8, .2, 1, 1), (4, 8, 8, .2, 1, 1), (4, 8, 16, .2, 1, 1), (2, 12, 16, .2, 1, 1), (4, 8, 64, .2, 1, 1), (4, 8, 16, .2, 1, 0), (4, 8, 16, .2, 0, 1), (4, 8, 16, .2, 1, 2), (4, 8, 16, .2, 1, -1), (4, 8, 16, .2, -1, 1). Three levels, G = 4, 8 by 8 by 8, t = .2, run 3000: all at 1 in at least 90%.
U2. Floor, t = .2, run 3000, 16 seeds. N = 6, 8: held in at least 75%. N = 3: at most 25%. N = 4, 5 reported.
U3. Dependence, G = 4, n = 8, N = 16, t = .2. Whole's ties cut, run 1000: every part keeps its turn in at least 90%. One part removed, run 4000: the others keep theirs in at least 90%, and the ports have come together, |mean| / mean amplitude >= .5, in at least 75%. One part unwound: it stays at 0, the others at 1, the whole at 1, in at least 90%.
U4. Disk of rings, radius 8. G = 4, n = 8 and G = 2, n = 12, t = .2, .5, run 500: whole's charge 1 in at least 75%, every part keeps its turn in at least 90%. G = 4, n = 8, t = .5: clamp one port opposite for 60, core or random: at most 10% of ports turned past pi / 2, charge 1 after 100 more in at least 90%.
U5. Flow, disk of rings, radius 16, G = 2, n = 12, c = 1, run 700. Slope over r = 5 to 13: at t = .2 at most .05 in size, and rising with t = .2, .5, .8, .95, each within .01. Plain disk reported.
U6. Plane, radius 32, parts at G = .95, each fed centre r < 4 at gain 4, noise a tenth. Lit, |z| >= .095: one centre at most .2 of the disk; spacing 12 at least .9; spacing 24 at most .6. Net charge, counting squares with amplitude >= .02, equals the number of centres in at least 75%. Boundary turning once with 4 centres turning alike, counting squares with amplitude >= .01: net 1 in every seed, at least 3 opposite zeros in at least 75%.

ADDED AFTER SEEING THE RESULTS ABOVE, predictions frozen before these ran. Seen so far: U1, U2, U3, U4 passed; U5, U6 missed. U2: N = 5 held in every seed and N = 4 in none, at both gains. U5: slope .024, .128, .040, .203 at t = .2, .5, .8, .95, so not rising, while core and far port amplitude were .893, .927; .883, .935; .955, .953; .801, .957. U6: lit .051, .609, .271 for 1, 13, 5 centres. My .9 was impossible, since 13 halos of about 8 sites cover at most .81 of the disk. Net charge -3 at spacing 12 and 1, 2 at spacing 24, not the number of centres; and the pinned case read neither, since my amplitude filter drops zeros in dark ground.
F1. U5's slope follows the core's deficit, not t. t = .1, .2, .35, .5, .65, .8, .9, .95: Spearman rank between slope and far minus core amplitude at least .7.
F2. Charges add, with no filter. Self-powered plane, G = 2, no fed centres, boundary held turning once, 4 centres seeded turning alike, noise a tenth. Net 1 at t = 20 and t = 500 in every seed. At t = 20 at least 3 opposite zeros in at least 75%. At t = 500 exactly one zero reported.
F3. Free edge, self-powered, no fed centres, 13 zeros alike at spacing 12, run 500, noise a tenth. G = 4: net 13 in at least 75%, held by the grid. G = 2: net below 13 in at least 75%.
F4. Why fed centres lost their own turn: each other's turning strains them, and a zero can leave for the dark ground. Fed plane, spacing 24, 5 centres, no noise, run 1000. Loop at half-side 5 round each centre: at most 3 of 5 still wind once.
"""
import json
import os
import sys
import time
from math import cos, pi, sqrt, tanh
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


# ---------- Graphs: lists of neighbours and weights ----------
class Net:
    def __init__(self, S):
        self.S = S
        self.nb = [[] for _ in range(S)]

    def tie(self, i, j, w):
        self.nb[i].append((j, w))

    def finish(self, alive=None):
        K = max(max((len(x) for x in self.nb), default=1), 1)
        self.idx = np.zeros((self.S, K), dtype=int)
        self.wt = np.zeros((self.S, K))
        for i, x in enumerate(self.nb):
            for k, (j, w) in enumerate(x):
                self.idx[i, k] = j
                self.wt[i, k] = w
        return self

    def reading(self, z):
        return (z[..., self.idx] * self.wt).sum(-1)

    def dense(self):
        W = np.zeros((self.S, self.S))
        for i, x in enumerate(self.nb):
            for j, w in x:
                W[i, j] += w
        return W


def ring_of_rings(N, n, t, drop_whole=False):
    """N rings of n sites. Site 0 of each ring is its port, which reads a share t through the whole's ring."""
    g = Net(N * n)
    rings = np.arange(N * n).reshape(N, n)
    ports = rings[:, 0]
    for P in range(N):
        for j in range(n):
            s = rings[P, j]
            share = (1 - t) if (j == 0 and not drop_whole) else 1.0
            g.tie(s, rings[P, (j + 1) % n], share / 2)
            g.tie(s, rings[P, (j - 1) % n], share / 2)
            if j == 0 and not drop_whole:
                g.tie(s, ports[(P + 1) % N], t / 2)
                g.tie(s, ports[(P - 1) % N], t / 2)
    return g.finish(), rings, ports


def three_levels(M, N, n, t):
    """M rings of N rings of n sites. The third level passes through site n // 2 of ring 0 of each second-level ring."""
    S = M * N * n
    g = Net(S)
    site = np.arange(S).reshape(M, N, n)
    for A in range(M):
        for P in range(N):
            for j in range(n):
                s = site[A, P, j]
                l2 = j == 0
                l3 = (P == 0 and j == n // 2)
                share = (1 - t) if (l2 or l3) else 1.0
                g.tie(s, site[A, P, (j + 1) % n], share / 2)
                g.tie(s, site[A, P, (j - 1) % n], share / 2)
                if l2:
                    g.tie(s, site[A, (P + 1) % N, 0], t / 2)
                    g.tie(s, site[A, (P - 1) % N, 0], t / 2)
                if l3:
                    g.tie(s, site[(A + 1) % M, 0, n // 2], t / 2)
                    g.tie(s, site[(A - 1) % M, 0, n // 2], t / 2)
    return g.finish(), site


def state_rr(N, n, q, Q, m=.9):
    z = np.zeros(N * n, complex)
    for P in range(N):
        for j in range(n):
            z[P * n + j] = m * np.exp(1j * (2 * pi * q * j / n + 2 * pi * Q * P / N))
    return z


def run(g, z, G, T, rng, c=0.0, sigma=SIGMA, pin=None, pinval=None):
    for _ in range(int(T / DT)):
        z = z + DT * (-z + lim(G * g.reading(z)))
        if c:
            z = z * np.exp(1j * DT * c * np.abs(z) ** 2)
        if sigma:
            z = z + sqrt(DT) * sigma * cnoise(rng, z.shape)
        if pin is not None:
            z[pin] = pinval
    return z


def max_eig(g, z, G):
    W = g.dense()
    w = G * W @ z
    a = np.abs(w)
    a = np.maximum(a, 1e-12)
    ux, uy = np.real(w) / a, np.imag(w) / a
    rho, tau = 1 / np.cosh(a) ** 2, np.tanh(a) / a
    S = g.S
    J = -np.eye(2 * S)
    for j in range(S):
        Dj = np.array([[rho[j] * ux[j] ** 2 + tau[j] * uy[j] ** 2, (rho[j] - tau[j]) * ux[j] * uy[j]], [(rho[j] - tau[j]) * ux[j] * uy[j], rho[j] * uy[j] ** 2 + tau[j] * ux[j] ** 2]])
        J[2 * j:2 * j + 2, ::2] += G * Dj[:, [0]] * W[j]
        J[2 * j:2 * j + 2, 1::2] += G * Dj[:, [1]] * W[j]
    return float(np.linalg.eigvals(J).real.max())


def rr_stable(G, n, N, t, q=1, Q=1):
    g, rings, ports = ring_of_rings(N, n, t)
    z = state_rr(N, n, q, Q)[None]
    z = run(g, z, G, 4000, None, sigma=0.0)
    qq = winding(z[:, rings])[0]
    QQ = winding(z[:, ports])[0]
    amp = float(np.abs(z).min())
    if amp < .02 or not (qq == q).all() or QQ != Q:
        return False, amp, float("nan")
    e = max_eig(g, z[0], G)
    return e < 1e-6, amp, e


def plain_floor(G):
    for n in range(3, 40):
        W = np.zeros((n, n))
        for j in range(n):
            W[j, (j + 1) % n] += .5
            W[j, (j - 1) % n] += .5
        g = Net(n)
        for j in range(n):
            g.tie(j, (j + 1) % n, .5)
            g.tie(j, (j - 1) % n, .5)
        g.finish()
        z = (.9 * np.exp(2j * pi * np.arange(n) / n))[None]
        z = run(g, z, G, 4000, None, sigma=0.0)
        if winding(z)[0] == 1 and np.abs(z).min() > .02 and max_eig(g, z[0], G) < 1e-6:
            return n
    return None


def solve():
    print("Plain ring floors, noise-free:")
    for G in (2.0, 4.0):
        print(f"  G {G:g}: {plain_floor(G)}")
    print("Ring of rings, q = Q = 1. Floor in N, t = .2, and whether it is stable; smallest amplitude; largest growth rate")
    for G, n in ((2.0, 12), (4.0, 8)):
        for N in (3, 4, 5, 6, 8, 12):
            st, amp, e = rr_stable(G, n, N, .2)
            print(f"  G {G:g}, n {n}, N {N}: stable {st}; amplitude {amp:.3f}; growth {e:.2e}", flush=True)
    print("Share t through the whole's ring, N = 8")
    for G, n in ((2.0, 12), (4.0, 8)):
        for t in (.05, .1, .2, .4, .6, .8, .9, .95):
            st, amp, e = rr_stable(G, n, 8, t)
            print(f"  G {G:g}, n {n}, t {t:g}: stable {st}; amplitude {amp:.3f}; growth {e:.2e}", flush=True)
    print("Independent integers, G 4, n 8, N 16, t .2")
    for q, Q in ((1, 0), (0, 1), (1, 2), (1, -1), (-1, 1), (0, 0)):
        st, amp, e = rr_stable(4.0, 8, 16, .2, q, Q)
        print(f"  q {q}, Q {Q}: stable {st}; amplitude {amp:.3f}; growth {e:.2e}", flush=True)


def hold_cell(job):
    G, n, N, t, q, Q = job
    g, rings, ports = ring_of_rings(N, n, t)
    rng = seed_of(1, G, n, N, t, q + 3, Q + 3)
    z = state_rr(N, n, q, Q, m=.9)[None] + SPREAD * cnoise(rng, (8, N * n))
    z = run(g, z, G, 1500, rng)
    a = (winding(z[:, rings]) == q).all(1) & (winding(z[:, ports]) == Q)
    return job, float(a.mean())


def job_hold(_o):
    """U1."""
    ok = True
    cells = [(2.0, 12, 8, .2, 1, 1), (4.0, 8, 8, .2, 1, 1), (4.0, 8, 16, .2, 1, 1), (2.0, 12, 16, .2, 1, 1), (4.0, 8, 64, .2, 1, 1), (4.0, 8, 16, .2, 1, 0), (4.0, 8, 16, .2, 0, 1), (4.0, 8, 16, .2, 1, 2), (4.0, 8, 16, .2, 1, -1), (4.0, 8, 16, .2, -1, 1)]
    with Pool(8) as p:
        res = p.map(hold_cell, cells)
    for job, fr in res:
        good = fr >= .9
        ok &= good
        print(f"  G {job[0]:g}, n {job[1]}, N {job[2]}, t {job[3]:g}, q {job[4]}, Q {job[5]}: held in {fr:.2f}; {verdict(good)}", flush=True)
    G, M, N, n, t = 4.0, 8, 8, 8, .2
    g, site = three_levels(M, N, n, t)
    rng = seed_of(1, 3)
    z0 = np.zeros(M * N * n, complex)
    for A in range(M):
        for P in range(N):
            for j in range(n):
                z0[site[A, P, j]] = .9 * np.exp(1j * (2 * pi * j / n + 2 * pi * P / N + 2 * pi * A / M))
    z = z0[None] + SPREAD * cnoise(rng, (8, M * N * n))
    z = run(g, z, G, 3000, rng)
    q1 = (winding(z[:, site]) == 1).all((1, 2))
    q2 = (winding(z[:, site[:, :, 0]]) == 1).all(1)
    q3 = winding(z[:, site[:, 0, n // 2]]) == 1
    fr = float((q1 & q2 & q3).mean())
    good = fr >= .9
    ok &= good
    print(f"  Three levels, G 4, 8 by 8 by 8, t .2: all held in {fr:.2f}; level 1 {float(q1.mean()):.2f}, level 2 {float(q2.mean()):.2f}, level 3 {float(q3.mean()):.2f}; {verdict(good)}", flush=True)
    return ok


def floor_cell(job):
    G, n, N, t = job
    g, rings, ports = ring_of_rings(N, n, t)
    rng = seed_of(2, G, n, N, t)
    z = state_rr(N, n, 1, 1)[None] + SPREAD * cnoise(rng, (16, N * n))
    z = run(g, z, G, 3000, rng)
    return job, float(((winding(z[:, rings]) == 1).all(1) & (winding(z[:, ports]) == 1)).mean())


def job_floor(_o):
    """U2."""
    ok = True
    cells = [(G, n, N, .2) for G, n in ((2.0, 12), (4.0, 8)) for N in (3, 4, 5, 6, 8)]
    with Pool(8) as p:
        res = p.map(floor_cell, cells)
    for job, fr in res:
        G, n, N, t = job
        if N >= 6:
            good = fr >= .75
        elif N == 3:
            good = fr <= .25
        else:
            good = True
        ok &= good
        print(f"  G {G:g}, n {n}, N {N}: held in {fr:.2f}; {verdict(good)}{' (reported)' if N in (4, 5) else ''}", flush=True)
    return ok


def job_depend(_o):
    """U3."""
    ok = True
    G, n, N, t = 4.0, 8, 16, .2
    g, rings, ports = ring_of_rings(N, n, t)
    rng = seed_of(3, 1)
    z0 = state_rr(N, n, 1, 1)[None] + SPREAD * cnoise(rng, (8, N * n))
    z0 = run(g, z0, G, 500, rng)
    # The whole's ties cut: the parts carry on.
    gd, _r, _p = ring_of_rings(N, n, t, drop_whole=True)
    z = run(gd, z0.copy(), G, 1000, rng)
    a = float((winding(z[:, rings]) == 1).all(1).mean())
    ok &= a >= .9
    print(f"  The whole's ties cut: every part keeps its turn in {a:.2f}", flush=True)
    # One part removed: its port stops reading and being read. The whole's loop opens.
    g2 = Net(N * n)
    dead = 0
    for P in range(N):
        for j in range(n):
            s = rings[P, j]
            if P == dead:
                continue
            nbrs = []
            if j == 0:
                nx, pv = (P + 1) % N, (P - 1) % N
                ws = [(rings[P, 1], (1 - t) / 2), (rings[P, n - 1], (1 - t) / 2)]
                tot = 0
                for o in (nx, pv):
                    if o != dead:
                        ws.append((ports[o], t / 2))
                        tot += t / 2
                sc = 1 / ((1 - t) + tot)
                for x, w in ws:
                    g2.tie(s, x, w * sc)
            else:
                g2.tie(s, rings[P, (j + 1) % n], .5)
                g2.tie(s, rings[P, (j - 1) % n], .5)
    g2.finish()
    z = z0.copy()
    z[:, rings[dead]] = 0
    alive = np.delete(np.arange(N), dead)
    for _ in range(int(4000 / DT)):
        z = z + DT * (-z + lim(G * g2.reading(z))) + sqrt(DT) * SIGMA * cnoise(rng, z.shape)
        z[:, rings[dead]] = 0
    keep = float((winding(z[:, rings[alive]]) == 1).all(1).mean())
    together = np.abs(z[:, ports[alive]].mean(1)) / np.abs(z[:, ports[alive]]).mean(1)
    b = float(np.mean(together >= .5))
    ok &= keep >= .9 and b >= .75
    print(f"  One part removed: other parts keep their turn in {keep:.2f}; the whole's turn has unwound, ports together, in {b:.2f}; median {float(np.median(together)):.3f}", flush=True)
    # One part loses its own turn: the whole's turn stays.
    z = z0.copy()
    amp = np.abs(z[:, rings[3]])
    pa = np.angle(z[:, ports[3]])[:, None]
    z[:, rings[3]] = amp * np.exp(1j * pa)
    z = run(g, z, G, 1000, rng)
    w = winding(z[:, rings])
    c1 = float(((w[:, 3] == 0) & (np.delete(w, 3, axis=1) == 1).all(1) & (winding(z[:, ports]) == 1)).mean())
    ok &= c1 >= .9
    print(f"  One part loses its own turn: it stays without one, the others keep theirs, and the whole keeps its turn in {c1:.2f}", flush=True)
    return ok


def disk_net(R, n, t, cx=.5, cy=.5):
    L = 2 * R + 2
    y, x = np.mgrid[0:L, 0:L]
    X, Y = x - R + 0.0, y - R + 0.0
    mask = (X - cx) ** 2 + (Y - cy) ** 2 < R * R
    ids = -np.ones_like(x)
    pos = np.argwhere(mask)
    ids[mask] = np.arange(len(pos))
    Np = len(pos)
    g = Net(Np * n)
    for P, (i, j) in enumerate(pos):
        nbrs = []
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            a, b = i + di, j + dj
            if 0 <= a < L and 0 <= b < L and mask[a, b]:
                nbrs.append(ids[a, b])
        share = t if n > 1 else 1.0
        for o in nbrs:
            g.tie(P * n, o * n, share / max(len(nbrs), 1))
        if n > 1:
            g.tie(P * n, P * n + 1, (1 - t) / 2)
            g.tie(P * n, P * n + n - 1, (1 - t) / 2)
            for j2 in range(1, n):
                g.tie(P * n + j2, P * n + (j2 + 1) % n, .5)
                g.tie(P * n + j2, P * n + (j2 - 1) % n, .5)
    g.finish()
    info = dict(L=L, X=X, Y=Y, mask=mask, ids=ids, pos=pos, Np=Np, n=n, phi=np.arctan2(Y - cy, X - cx), rad=np.hypot(X - cx, Y - cy))
    return g, info


def disk_state(info, B, m, rng, spread=SPREAD):
    n, Np, pos = info["n"], info["Np"], info["pos"]
    z = np.zeros(Np * n, complex)
    for P, (i, j) in enumerate(pos):
        ph = info["phi"][i, j]
        amp = m * np.tanh(info["rad"][i, j] / 2) if n == 1 else m
        for k in range(n):
            z[P * n + k] = amp * np.exp(1j * (ph + 2 * pi * k / n))
    return z[None] + spread * cnoise(rng, (B, Np * n))


def disk_charges(z, info):
    n, ids, mask, L = info["n"], info["ids"], info["mask"], info["L"]
    B = z.shape[0]
    a = np.zeros((B, L, L))
    a[:, mask] = np.angle(z[:, ids[mask] * n])
    d1 = wrap(np.roll(a, -1, axis=2) - a)
    d2 = wrap(np.roll(np.roll(a, -1, axis=2), -1, axis=1) - np.roll(a, -1, axis=2))
    d3 = wrap(np.roll(a, -1, axis=1) - np.roll(np.roll(a, -1, axis=2), -1, axis=1))
    d4 = wrap(a - np.roll(a, -1, axis=1))
    ch = np.rint((d1 + d2 + d3 + d4) / (2 * pi)).astype(int)
    ok = mask & np.roll(mask, -1, 1) & np.roll(mask, -1, 0) & np.roll(np.roll(mask, -1, 1), -1, 0)
    return ch * ok


def job_disk(_o):
    """U4."""
    ok = True
    for G, n in ((4.0, 8), (2.0, 12)):
        for t in (.2, .5):
            g, info = disk_net(8, n, t)
            rng = seed_of(4, G, t)
            rings = np.arange(info["Np"] * n).reshape(info["Np"], n)
            z = disk_state(info, 8, .9, rng)
            z = run(g, z, G, 500, rng)
            ch = disk_charges(z, info)
            net = ch.sum((1, 2))
            cnt = np.abs(ch).sum((1, 2))
            q = (winding(z[:, rings]) == 1).all(1)
            portamp = np.abs(z[:, rings[:, 0]])
            good = float(np.mean(net == 1)) >= .75 and float(q.mean()) >= .9
            ok &= good
            print(f"  G {G:g}, n {n}, t {t:g}: whole's charge 1 in {float(np.mean(net==1)):.2f}; every part keeps its turn in {float(q.mean()):.2f}; zeros {sorted(set(cnt.tolist()))}; smallest port amplitude {float(np.median(portamp.min(1))):.3f}; {verdict(good)}", flush=True)
    # A plain disk at the same size, for the amplitude.
    for G in (2.0, 4.0):
        g, info = disk_net(8, 1, 1.0)
        rng = seed_of(4, G, 9)
        z = disk_state(info, 8, .9, rng)
        z = run(g, z, G, 500, rng)
        print(f"  Plain disk, G {G:g}: smallest amplitude {float(np.median(np.abs(z).min(1))):.3f}; charge 1 in {float(np.mean(disk_charges(z, info).sum((1,2))==1)):.2f}", flush=True)
    # Clamp and remove one part.
    G, n, t = 4.0, 8, .5
    g, info = disk_net(8, n, t)
    rng = seed_of(4, 11)
    rings = np.arange(info["Np"] * n).reshape(info["Np"], n)
    z0 = disk_state(info, 8, .9, rng)
    z0 = run(g, z0, G, 300, rng)
    worst = 0.0
    for trial in range(6):
        P = int(np.argmin(info["rad"][info["mask"]])) if trial < 2 else int(rng.integers(info["Np"]))
        val = -z0[:, rings[P, 0]]
        z = z0.copy()
        for _ in range(int(60 / DT)):
            z = z + DT * (-z + lim(G * g.reading(z))) + sqrt(DT) * SIGMA * cnoise(rng, z.shape)
            z[:, rings[P, 0]] = val
        turned = np.abs(wrap(np.angle(z[:, rings[:, 0]]) - np.angle(z0[:, rings[:, 0]]))) > pi / 2
        worst = max(worst, float(turned.mean(1).max()))
        z = run(g, z, G, 100, rng)
        net = disk_charges(z, info).sum((1, 2))
        a = float(np.mean(net == 1))
        ok &= a >= .9
    ok &= worst <= .1
    print(f"  Clamp one part opposite: largest share of parts turned {worst:.3f}; charge stayed, last trial {a:.2f}", flush=True)
    return ok


def flow_cell(job):
    n, t, G, c = job
    g, info = disk_net(16, n, t)
    rng = seed_of(5, n, t, G, c)
    z = disk_state(info, 4, .9, rng)
    z = run(g, z, G, 700, rng, c=c)
    ports = np.arange(info["Np"]) * n
    pos = info["pos"]
    rad = info["rad"][pos[:, 0], pos[:, 1]]
    phi = info["phi"][pos[:, 0], pos[:, 1]]
    rs = np.arange(5, 14)

    def ann(y, r):
        sel = np.abs(rad - r) <= .5
        return (y[:, ports[sel]] * np.exp(-1j * phi[sel])).mean(1)
    a = np.stack([ann(z, r) for r in rs], axis=1)
    k = np.array([np.polyfit(rs, np.unwrap(np.angle(a[b])), 1)[0] for b in range(4)])
    a0 = np.angle(ann(z, 10))
    tot = 0.0
    y = z
    for _ in range(int(20 / DT)):
        y = run(g, y, G, DT, rng, c=c)
        a1 = np.angle(ann(y, 10))
        tot = tot + wrap(a1 - a0)
        a0 = a1
    rate = tot / 20
    net = disk_charges(y, info).sum((1, 2))
    amp = np.abs(y[:, ports])
    core = amp[:, rad < 2].mean(1)
    far = amp[:, rad > 8].mean(1)
    return job, k.tolist(), rate.tolist(), net.tolist(), float(core.mean()), float(far.mean())


def job_flow(_o):
    """U5."""
    ok = True
    cells = [(1, 1.0, 2.0, 1.0), (12, .2, 2.0, 1.0), (12, .5, 2.0, 1.0), (12, .8, 2.0, 1.0), (12, .95, 2.0, 1.0)]
    with Pool(5) as p:
        res = {x[0]: x[1:] for x in p.map(flow_cell, cells)}
    plain = float(np.median(np.abs(res[(1, 1.0, 2.0, 1.0)][0])))
    prev = None
    for job in cells:
        k, rate, net, core, far = res[job]
        mk = float(np.median(k))
        inward = float(np.mean(np.array(k) * np.array(rate) > 0))
        print(f"  n {job[0]}, t {job[1]:g}: slope {mk:.4f}; rate {float(np.median(rate)):.4f}; inward in {inward:.2f}; charge 1 in {float(np.mean(np.array(net)==1)):.2f}; port amplitude core {core:.3f}, far {far:.3f}", flush=True)
    sl = [abs(float(np.median(res[(12, x, 2.0, 1.0)][0]))) for x in (.2, .5, .8, .95)]
    good = sl[0] <= .05 and sl[0] <= sl[1] + .01 and sl[1] <= sl[2] + .01 and sl[2] <= sl[3] + .01
    ok &= good
    print(f"  Slope rises with t, and at t = .2 is at most .05: {verdict(good)}", flush=True)
    return ok


class Plane:
    def __init__(self, R=32):
        self.R = R
        L = 2 * R + 2
        y, x = np.mgrid[0:L, 0:L]
        self.x, self.y = x - R + 0.0, y - R + 0.0
        self.mask = self.x ** 2 + self.y ** 2 < R * R
        self.adj = []
        for ax, sh in ((0, 1), (0, -1), (1, 1), (1, -1)):
            self.adj.append((ax, sh, self.mask & np.roll(self.mask, sh, axis=ax)))
        self.cnt = sum(a.astype(float) for _x, _s, a in self.adj)

    def run(self, z, G, T, rng, sigma, pin=None, pinval=None):
        for _ in range(int(T / DT)):
            s = 0
            for ax, sh, a in self.adj:
                s = s + np.roll(z, sh, axis=ax + 1) * a
            z = z + DT * (-z + lim(G * s / np.maximum(self.cnt, 1)))
            if sigma:
                z = z + sqrt(DT) * sigma * cnoise(rng, z.shape)
            z = z * self.mask
            if pin is not None:
                z[:, pin] = pinval
        return z

    def charges(self, z, amin=0.0):
        a = np.angle(z)
        amp = np.abs(z)
        d1 = wrap(np.roll(a, -1, axis=2) - a)
        d2 = wrap(np.roll(np.roll(a, -1, axis=2), -1, axis=1) - np.roll(a, -1, axis=2))
        d3 = wrap(np.roll(a, -1, axis=1) - np.roll(np.roll(a, -1, axis=2), -1, axis=1))
        d4 = wrap(a - np.roll(a, -1, axis=1))
        ch = np.rint((d1 + d2 + d3 + d4) / (2 * pi)).astype(int)
        m = self.mask
        ok = m & np.roll(m, -1, 1) & np.roll(m, -1, 0) & np.roll(np.roll(m, -1, 1), -1, 0)
        low = np.minimum(np.minimum(amp, np.roll(amp, -1, axis=2)), np.minimum(np.roll(amp, -1, axis=1), np.roll(np.roll(amp, -1, axis=2), -1, axis=1)))
        return ch * ok * (low >= amin)

    def cores(self, L):
        out = []
        k = int(self.R / L) + 1
        for i in range(-k, k + 1):
            for j in range(-k, k + 1):
                x, y = i * L + .5, j * L + .5
                if x * x + y * y < (self.R - 6) ** 2:
                    out.append((x, y))
        return out

    def seeded(self, B, cores, rng, spread):
        ph = np.zeros_like(self.x)
        amp = np.zeros_like(self.x)
        for cx, cy in cores:
            ph = ph + np.arctan2(self.y - cy, self.x - cx)
            r = np.hypot(self.x - cx, self.y - cy)
            amp = np.maximum(amp, .9 * np.tanh(r / 2) * np.exp(-np.maximum(r - 4, 0) / 6))
        for cx, cy in cores:
            r = np.hypot(self.x - cx, self.y - cy)
            amp = amp * np.tanh(r / 2 + .01) ** 1
        return (amp * np.exp(1j * ph))[None] * self.mask + spread * cnoise(rng, (B, *self.x.shape)) * self.mask

    def gainmap(self, cores, G, Gc):
        g = np.full_like(self.x, G)
        for cx, cy in cores:
            g = np.where(np.hypot(self.x - cx, self.y - cy) < 4, Gc, g)
        return g


def plane_cell(job):
    L = job
    p = Plane(32)
    rng = seed_of(6, L)
    cores = [(.5, .5)] if L == 0 else p.cores(L)
    gm = p.gainmap(cores, .95, 4.0)
    z = p.seeded(4, cores, rng, SPREAD * .1)
    z = p.run(z, gm, 1000, rng, SIGMA * .1)
    a = np.abs(z)
    lit = ((a >= .1 * .95) & p.mask).sum((1, 2)) / p.mask.sum()
    ch = p.charges(z, .02)
    net = ch.sum((1, 2))
    cnt = np.abs(ch).sum((1, 2))
    return L, len(cores), float(np.median(lit)), net.tolist(), cnt.tolist()


def job_plane(_o):
    """U6."""
    ok = True
    with Pool(3) as q:
        res = q.map(plane_cell, [0, 12, 24])
    for L, K, lit, net, cnt in res:
        if L == 0:
            good = lit <= .2
        elif L == 12:
            good = lit >= .9
        else:
            good = lit <= .6
        same = float(np.mean(np.array(net) == K))
        good2 = same >= .75
        ok &= good and good2
        print(f"  Spacing {L}, {K} fed centres: lit {lit:.3f}, {verdict(good)}; net charge {sorted(set(net))}, equal to the number of centres in {same:.2f}, {verdict(good2)}; zeros {sorted(set(cnt))}", flush=True)
    # Boundary held turning once, four centres all turning the same way.
    p = Plane(32)
    rng = seed_of(6, 99)
    cores = [(12.5, 12.5), (-11.5, 12.5), (12.5, -11.5), (-11.5, -11.5)]
    gm = p.gainmap(cores, .95, 4.0)
    z = p.seeded(8, cores, rng, SPREAD * .1)
    shell = p.mask & (np.hypot(p.x, p.y) >= 30.5)
    pinval = .9 * np.exp(1j * np.arctan2(p.y[shell], p.x[shell]))
    z[:, shell] = pinval
    z = p.run(z, gm, 500, rng, SIGMA * .1, shell, pinval)
    ch = p.charges(z, .01)
    net = ch.sum((1, 2))
    neg = (ch < 0).sum((1, 2))
    a = float(np.mean(net == 1))
    b = float(np.mean(neg >= 3))
    ok &= a == 1.0 and b >= .75
    print(f"  Boundary turning once, 4 centres turning alike: net charge 1 in {a:.2f}; at least 3 opposite zeros in {b:.2f}; opposite zeros {sorted(set(neg.tolist()))}", flush=True)
    return ok


def job_f1(_o):
    ts = (.1, .2, .35, .5, .65, .8, .9, .95)
    cells = [(12, t, 2.0, 1.0) for t in ts]
    with Pool(8) as p:
        res = p.map(flow_cell, cells)
    sl, de = [], []
    for job, k, rate, net, core, far in res:
        mk = float(np.median(k))
        sl.append(abs(mk))
        de.append(far - core)
        print(f"  t {job[1]:g}: slope {mk:.4f}; far minus core {far-core:.4f}; rate {float(np.median(rate)):.4f}; charge 1 in {float(np.mean(np.array(net)==1)):.2f}", flush=True)
    ra = np.argsort(np.argsort(sl))
    rb = np.argsort(np.argsort(de))
    rho = float(np.corrcoef(ra, rb)[0, 1])
    print(f"  Spearman rank {rho:.3f}", flush=True)
    return rho >= .7


def job_f2(_o):
    p = Plane(32)
    rng = seed_of(7, 1)
    cores = [(12.5, 12.5), (-11.5, 12.5), (12.5, -11.5), (-11.5, -11.5)]
    gm = np.full_like(p.x, 2.0)
    z = p.seeded(8, cores, rng, SPREAD * .1)
    shell = p.mask & (np.hypot(p.x, p.y) >= 30.5)
    pinval = rest(2.0) * np.exp(1j * np.arctan2(p.y[shell], p.x[shell]))
    z[:, shell] = pinval
    z = p.run(z, gm, 20, rng, SIGMA * .1, shell, pinval)
    ch = p.charges(z)
    net1, neg1 = ch.sum((1, 2)), (ch < 0).sum((1, 2))
    z = p.run(z, gm, 480, rng, SIGMA * .1, shell, pinval)
    ch = p.charges(z)
    net2, cnt2 = ch.sum((1, 2)), np.abs(ch).sum((1, 2))
    a = float(np.mean(net1 == 1)), float(np.mean(net2 == 1))
    b = float(np.mean(neg1 >= 3))
    print(f"  t 20: net 1 in {a[0]:.2f}; at least 3 opposite zeros in {b:.2f}; opposite zeros {sorted(set(neg1.tolist()))}", flush=True)
    print(f"  t 500: net 1 in {a[1]:.2f}; zeros {sorted(set(cnt2.tolist()))}; exactly one in {float(np.mean(cnt2==1)):.2f}", flush=True)
    return a[0] == 1.0 and a[1] == 1.0 and b >= .75


def job_f3(_o):
    ok = True
    p = Plane(32)
    cores = p.cores(12)
    K = len(cores)
    for G in (4.0, 2.0):
        rng = seed_of(7, 2, G)
        ph = np.zeros_like(p.x)
        for cx, cy in cores:
            ph = ph + np.arctan2(p.y - cy, p.x - cx)
        z = (rest(G) * np.exp(1j * ph))[None] * p.mask + SPREAD * .1 * cnoise(rng, (8, *p.x.shape)) * p.mask
        z = p.run(z, np.full_like(p.x, G), 500, rng, SIGMA * .1)
        ch = p.charges(z)
        net, cnt = ch.sum((1, 2)), np.abs(ch).sum((1, 2))
        fr = float(np.mean(net == K)) if G == 4.0 else float(np.mean(net < K))
        good = fr >= .75
        ok &= good
        print(f"  G {G:g}, {K} zeros alike: net {sorted(set(net.tolist()))}; zeros {sorted(set(cnt.tolist()))}; {'net unchanged' if G == 4.0 else 'net below'} in {fr:.2f}; {verdict(good)}", flush=True)
    return ok


def job_f4(_o):
    p = Plane(32)
    rng = seed_of(7, 3)
    cores = p.cores(24)
    gm = p.gainmap(cores, .95, 4.0)
    z = p.seeded(1, cores, rng, 0.0)
    z = p.run(z, gm, 1000, rng, 0.0)
    kept = 0
    rows = []
    for cx, cy in cores:
        i0, j0 = int(round(cy - .5)) + p.R, int(round(cx - .5)) + p.R
        h = 5
        pts = [(i0 - h, j0 + d) for d in range(-h, h)] + [(i0 + d, j0 + h) for d in range(-h, h)] + [(i0 + h, j0 - d) for d in range(-h, h)] + [(i0 - d, j0 - h) for d in range(-h, h)]
        w = int(winding(np.stack([z[:, a, b] for a, b in pts], axis=1))[0])
        rows.append(((cx, cy), w))
        kept += w == 1
    print(f"  Windings at half-side 5: {rows}; kept {kept} of {len(cores)}", flush=True)
    return kept <= 3


JOBS = {"hold": ("U1", job_hold), "floor": ("U2", job_floor), "depend": ("U3", job_depend), "disk": ("U4", job_disk), "flow": ("U5", job_flow), "plane": ("U6", job_plane), "f1": ("F1", job_f1), "f2": ("F2", job_f2), "f3": ("F3", job_f3), "f4": ("F4", job_f4)}


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
