"""Architecture of Wholeness, Experiment 13: the reduced heading model used to derive the frozen predictions
before the full organisms are run.

Created: 2026-11-07. Last updated: 2026-11-07. Version: 1.0.

Experiment 12 verified the ring's heading law to within 7%: theta' = (eps / V) sum_s w_s sin(phi_s - theta),
V = G r cos(2 pi / n), with the neutral mode walking at variance sigma^2 t / (n r^2). This file integrates that
one-variable law through the harder task of Experiment 13 (plans/architecture_experiment_13_harder_task_2026_11_07.md)
to produce the numbers the pre-registration freezes. It is a derivation tool, not the experiment: it has no parts,
no limiter, no hub. Where it stands in for the chair and the leader it says so (the chair re-locked like the G = 8
ring in Experiment 12; the leader commits on its first cued trial and never moves).

Usage: python architecture_experiment_13_reduced_v1.py [--seeds 1000] [--scan | --forms | --coalition]
  --scan       sweep the number of liars and the lie rate for the list with and without learning (design step)
  --forms      the three weight forms (raw, chance-corrected, gate) against independent liars
  --coalition  the three weight forms against liars that lie together
"""
import argparse
from math import pi, sqrt, cos
import numpy as np

N = 16
SIGMA = .05
TAU = 40.0
DT = .1
STEPS = int(round(TAU / DT))
TRIALS = 100
SKIP = 20                # trials left out of every hit rate, for learning
HIT = np.deg2rad(20)
RES_NOISE = np.deg2rad(10)
ETA = .2
EPS = .3
CHANCE = 2 * HIT / (2 * pi)      # 1/9
P_BLANK = .25


def wrap(a):
    return (a + pi) % (2 * pi) - pi


def rest(G, n=N):
    r = 1.0
    for _ in range(10000):
        r = np.tanh(G * r * cos(2 * pi / n))
    return r


def V_of(G):
    return G * rest(G) * cos(2 * pi / N)


class World:
    """Regimes of k trials; the resource is redrawn uniformly at each regime start, with 10 degree per-trial noise.
    A trial is blank (no cue reaches the organism) with probability P_BLANK. Source 0 is honest. Sources 1..L lie
    with probability q on each cued trial, each in its own uniformly random direction (independent) or all in one
    (coalition), and announce the resource otherwise."""

    def __init__(self, rng, S, k, liars=3, q=.75, coalition=False):
        self.S, self.k, self.L = S, k, liars
        t = np.arange(TRIALS)
        reg = t // k
        nreg = reg.max() + 1
        star = rng.uniform(-pi, pi, (S, nreg))[:, reg]
        self.res = wrap(star + RES_NOISE * rng.standard_normal((S, TRIALS)))
        self.cued = rng.random((S, TRIALS)) >= P_BLANK
        self.first = np.zeros(TRIALS, bool)
        self.first[::k] = True                      # first trial of each regime
        self.settled = ~self.first & ~np.roll(self.first, 1)   # third trial of a regime onward
        ns = 1 + liars
        self.dir = np.zeros((S, ns, TRIALS))
        self.dir[:, 0] = self.res
        if coalition:
            lie = (rng.random((S, 1, TRIALS)) < q).repeat(liars, 1)
            d = rng.uniform(-pi, pi, (S, 1, TRIALS)).repeat(liars, 1)
        else:
            lie = rng.random((S, liars, TRIALS)) < q
            d = rng.uniform(-pi, pi, (S, liars, TRIALS))
        self.dir[:, 1:] = np.where(lie, d, self.res[:, None, :])
        self.hit = np.abs(wrap(self.dir - self.res[:, None, :])) <= HIT

    def feedback(self, rng, mode):
        """hit_s(t) as the grader reports it: 'true', 'shuffle' (another trial's resource), 'random' (a coin)."""
        if mode == 'true':
            return self.hit
        if mode == 'random':
            return rng.random(self.hit.shape) < .5
        perm = np.array([rng.permutation(TRIALS) for _ in range(self.S)])
        res_p = np.take_along_axis(self.res, perm, 1)
        return np.abs(wrap(self.dir - res_p[:, None, :])) <= HIT


def weights(r, form):
    if form == 'raw':
        return r
    if form == 'corrected':
        return np.maximum(0, (r - CHANCE) / (1 - CHANCE))
    if form == 'gate':
        return (np.maximum(0, (r - CHANCE) / (1 - CHANCE)) >= .5).astype(float)
    raise ValueError(form)


def simulate(world, rng, kind, G=4.0, learn='true', form='corrected', eps=EPS):
    """kind: 'L' list, 'R' ring at gain G, 'C' chair (stands in: the ring law at V = V_of(8)), 'D' leader
    (commits to the list's heading on its first cued trial, then never moves). learn: 'true' | 'none' | 'shuffle' |
    'random'. Returns heading (S, TRIALS) with nan for no heading, and the raw credibilities at the end."""
    S = world.S
    ns = world.dir.shape[1]
    r = np.full((S, ns), .5)
    fb = world.feedback(rng, 'true' if learn == 'none' else learn)
    V = V_of(8.0) if kind == 'C' else V_of(G)
    rr = rest(8.0 if kind == 'C' else G)
    theta = rng.uniform(-pi, pi, S)
    committed = np.zeros(S, bool)
    head = np.full((S, TRIALS), np.nan)
    noise_sd = SIGMA / (rr * sqrt(N)) if rr > 0 else 0.0
    for t in range(TRIALS):
        w = weights(r, form)
        cued = world.cued[:, t]
        net = (w * np.exp(1j * world.dir[:, :, t])).sum(1) * cued
        if kind == 'L':
            head[:, t] = np.where(np.abs(net) >= .05, np.angle(net), np.nan)
        elif kind == 'D':
            th_list = np.where(np.abs(net) >= .05, np.angle(net), np.nan)
            fresh = ~committed & ~np.isnan(th_list)
            theta = np.where(fresh, th_list, theta)
            committed |= fresh
            head[:, t] = np.where(committed, theta, np.nan)
        else:
            amp = np.abs(net)
            ang = np.angle(net)
            for _ in range(STEPS):
                theta = theta + DT * (eps / V) * amp * np.sin(ang - theta) + sqrt(DT) * noise_sd * rng.standard_normal(S)
            theta = wrap(theta)
            head[:, t] = theta
        if learn != 'none':
            upd = cued[:, None]
            r = np.where(upd, r + ETA * (fb[:, :, t] - r), r)
    return head, r


def scores(world, head):
    hit = np.abs(wrap(head - world.res)) <= HIT      # nan -> False
    sl = slice(SKIP, TRIALS)
    cued = world.cued[:, sl]
    h = hit[:, sl]
    first = np.broadcast_to(world.first[sl], h.shape)
    settled = np.broadcast_to(world.settled[sl], h.shape)
    out = dict(S_all=h.mean(), S_cued=h[cued].mean(), S_blank=h[~cued].mean() if (~cued).any() else np.nan,
               S_first=h[cued & first].mean(), S_settled=h[cued & settled].mean())
    return {k: float(v) for k, v in out.items()}


def table(S, seed, ks=(2, 5, 10, 25), orgs=(('L', 0), ('C', 0), ('D', 0), ('R', 2), ('R', 4), ('R', 8)),
          learns=('true', 'none', 'shuffle', 'random'), form='corrected', liars=3, q=.75, coalition=False):
    rows = []
    for k in ks:
        for learn in learns:
            for kind, G in orgs:
                wr = np.random.default_rng([seed, k, 1])
                world = World(wr, S, k, liars=liars, q=q, coalition=coalition)
                rng = np.random.default_rng([seed, k, 2])
                head, r = simulate(world, rng, kind, G=G, learn=learn, form=form)
                sc = scores(world, head)
                rows.append(dict(k=k, learn=learn, kind=kind, G=G, form=form, r_honest=float(r[:, 0].mean()),
                                 r_liar=float(r[:, 1:].mean()), **sc))
    return rows


def show(rows, cols=('S_all', 'S_cued', 'S_blank', 'S_first', 'S_settled', 'r_honest', 'r_liar')):
    print(f"{'k':>3} {'learn':>8} {'org':>4} {'G':>2} {'form':>9} " + " ".join(f"{c:>9}" for c in cols))
    for r in rows:
        print(f"{r['k']:>3} {r['learn']:>8} {r['kind']:>4} {r['G']:>2} {r['form']:>9} "
              + " ".join(f"{r[c]:>9.3f}" for c in cols))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seeds', type=int, default=1000)
    ap.add_argument('--seed', type=int, default=13)
    ap.add_argument('--scan', action='store_true')
    ap.add_argument('--coalition', action='store_true')
    ap.add_argument('--forms', action='store_true')
    ap.add_argument('--q', type=float, default=.75, help='lie rate of each deceptive source')
    ap.add_argument('--liars', type=int, default=3)
    ap.add_argument('--form', default='corrected', help='raw | corrected | gate, for the main table')
    a = ap.parse_args()
    if a.scan:
        print("design scan: the list, k = 10, learned (corrected weights) against no learning")
        for liars in (1, 3, 5):
            for q in (.5, .75, .9):
                rows = table(a.seeds, a.seed, ks=(10,), orgs=(('L', 0),), learns=('true', 'none'), liars=liars, q=q)
                print(f"liars {liars} q {q}: learned S_cued {rows[0]['S_cued']:.3f}  none {rows[1]['S_cued']:.3f}"
                      f"  r_liar {rows[0]['r_liar']:.3f}")
        return
    if a.forms:
        print(f"weight forms, k = 10, learned, {a.liars} independent liars at q {a.q}")
        for form in ('raw', 'corrected', 'gate'):
            show(table(a.seeds, a.seed, ks=(10,), learns=('true',), form=form, liars=a.liars, q=a.q))
        return
    if a.coalition:
        print(f"coalition of {a.liars} liars at q {a.q}, k = 10, learned, three weight forms")
        for form in ('raw', 'corrected', 'gate'):
            show(table(a.seeds, a.seed, ks=(10,), learns=('true',), form=form, coalition=True, liars=a.liars, q=a.q,
                       orgs=(('L', 0), ('R', 2), ('R', 4), ('R', 8))))
        return
    print(f"main table: {a.liars} independent liars at q {a.q}, weights {a.form}, {a.seeds} seeds")
    show(table(a.seeds, a.seed, form=a.form, liars=a.liars, q=a.q))


if __name__ == '__main__':
    main()
