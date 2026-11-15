"""Architecture of Wholeness, Experiment 14: the reduced heading model used to derive the frozen predictions
before the full organisms are run. Attention as resonance: a ring whose turn keeps time.

Created: 2026-11-08. Last updated: 2026-11-08. Version: 1.0.

Experiment 12 verified the ring's heading law to within 7%: theta' = (eps / V) sum_c w_c sin(phi_c - theta),
V = G r cos(2 pi / n). Experiment 14 gives the ring a clock by reading its two neighbours unequally, weights
1/2 - beta on the left and 1/2 + beta on the right. For a first-mode pattern that reading is the pattern rotated
by chi = atan(2 beta tan(2 pi / n)), and the exact first-mode law becomes

    theta' = omega0 + (eps / V_b) sum_c w_c sin(phi_c(t) - theta - chi),   omega0 = tan chi = 2 beta tan(2 pi / n),

with V_b = G |C| r*, |C| = sqrt(cos^2(2 pi/n) + 4 beta^2 sin^2(2 pi/n)) (within 0.5% of V for |beta| <= .25).
Cues rotate: phi_c(t) = Omega_c t + alpha_c. One cue is the Adler equation, psi' = Omega - omega0 - K sin(psi - chi),
K = eps w / V, locked iff |Omega - omega0| <= K: the organism's tongue. Here the law is integrated through the
world of plans/architecture_experiment_14_resonant_attention_2026_11_08.md to produce the numbers the
pre-registration freezes. It is a derivation tool: no parts, no limiter, no hub. The list is the angle of the
leaky-filtered cue sum (each cue attenuated by 1/sqrt(1 + Omega^2) and lagged by atan Omega). The chair stands in
as the ring law at V(5.9), the effective gain Experiment 13 measured for it, with its own clock omega_h =
tan(chi_h / 2) from the rotated hub broadcast. The leader commits to the list's first heading and never moves.

Usage: python architecture_experiment_14_reduced_v1.py [--seeds 500] [tongue two weight retune selftune hold]
"""
import argparse
from math import pi, sqrt, cos, tan, atan
import numpy as np

N = 16
SIGMA = .05
TAU = 40.0
DT = .1
STEPS = int(round(TAU / DT))
SAMPLE = 5                      # heading sampled every SAMPLE steps for the follow fraction
HIT = np.deg2rad(20)
FOLLOW = np.deg2rad(45)
EPS = .3
TAN_A = tan(2 * pi / N)         # tan 22.5 deg = .4142
V_CHAIR = 5.9                   # Experiment 13: the chair turned like a ring at V about 5.9


def wrap(a):
    return (a + pi) % (2 * pi) - pi


def rest(G, n=N):
    r = 1.0
    for _ in range(10000):
        r = np.tanh(G * r * cos(2 * pi / n))
    return r


def V_of(G):
    return G * rest(G) * cos(2 * pi / N)


def omega_ring(beta):
    return 2 * beta * TAN_A


def chi_ring(beta):
    return atan(2 * beta * TAN_A)


def beta_for(omega):
    return omega / (2 * TAN_A)


def omega_node(chi_h):
    return tan(chi_h / 2)


class Cues:
    """Rotating cues phi_c(t) = Omega_c t + alpha_c, alpha_c uniform per seed, weight w_c, present on the trials
    where on[c, t] is True. Cue 0 is the target (the resource)."""

    def __init__(self, rng, S, omegas, weights, trials, off=None):
        self.S, self.T = S, trials
        self.omega = np.asarray(omegas, float)
        self.w = np.asarray(weights, float)
        self.alpha = rng.uniform(-pi, pi, (S, len(omegas)))
        self.on = np.ones((len(omegas), trials), bool)
        if off:
            for c, (a, b) in off.items():
                self.on[c, a:b] = False

    def phase(self, c, t_abs):
        return self.alpha[:, c] + self.omega[c] * t_abs


def simulate(cues, rng, kind, G=4.0, clock=0.0, adapt=0.0, retune=None, eps=EPS):
    """kind: 'L' list, 'R' ring at gain G with clock omega0, 'C' chair (ring law at V_CHAIR with clock omega_h),
    'D' leader (fixed heading). clock: omega0 (R) or omega_h (C) in rad per time unit. adapt: eta_omega for the
    self-tuning rule omega0' = eta sum_c (eps w_c / V) sin(phi_c - theta). retune: (trial, new clock).
    Returns heading samples (S, T, STEPS // SAMPLE) and the clock per trial (S, T)."""
    S, T = cues.S, cues.T
    nsamp = STEPS // SAMPLE
    head = np.full((S, T, nsamp), np.nan)
    clocks = np.zeros((S, T))
    if kind in ('R', 'C'):
        V = V_CHAIR if kind == 'C' else V_of(G)
        rr = rest(G) if kind == 'R' else rest(5.9)
        chi = chi_ring(beta_for(clock)) if kind == 'R' else clock          # node: the broadcast lag is chi_h
        if kind == 'C':
            chi = atan(clock)                                                # lag at lock for the node loop
        omega = np.full(S, float(clock))
        theta = rng.uniform(-pi, pi, S)
        noise_sd = SIGMA / (rr * sqrt(N))
    committed = np.zeros(S, bool)
    theta_fixed = np.zeros(S)
    for t in range(T):
        if retune is not None and t == retune[0] and kind in ('R', 'C'):
            omega[:] = retune[1]
        for s_ in range(STEPS):
            t_abs = t * TAU + s_ * DT
            if kind in ('L', 'D'):
                net = np.zeros(S, complex)
                for c in range(len(cues.omega)):
                    if cues.on[c, t]:
                        gain = cues.w[c] / sqrt(1 + cues.omega[c] ** 2)
                        net += gain * np.exp(1j * (cues.phase(c, t_abs) - atan(cues.omega[c])))
                th = np.where(np.abs(net) >= .05, np.angle(net), np.nan)
                if kind == 'D':
                    fresh = ~committed & ~np.isnan(th)
                    theta_fixed = np.where(fresh, th, theta_fixed)
                    committed |= fresh
                    th = np.where(committed, theta_fixed, np.nan)
            else:
                pull = np.zeros(S)
                pull_adapt = np.zeros(S)
                for c in range(len(cues.omega)):
                    if cues.on[c, t]:
                        ph = cues.phase(c, t_abs)
                        pull += (eps * cues.w[c] / V) * np.sin(ph - theta - chi)
                        pull_adapt += (eps * cues.w[c] / V) * np.sin(ph - theta)
                theta = theta + DT * (omega + pull) + sqrt(DT) * noise_sd * rng.standard_normal(S)
                if adapt:
                    omega = omega + DT * adapt * pull_adapt
                th = wrap(theta)
            if s_ % SAMPLE == 0:
                head[:, t, s_ // SAMPLE] = th
        if kind in ('R', 'C'):
            clocks[:, t] = omega
    return head, clocks


def follow(cues, head, c):
    """Fraction of samples within FOLLOW of cue c, per seed and trial (nan heading counts as not following)."""
    S, T, nsamp = head.shape
    t_abs = (np.arange(T)[:, None] * TAU + np.arange(nsamp)[None, :] * SAMPLE * DT)
    ph = cues.alpha[:, c][:, None, None] + cues.omega[c] * t_abs[None, :, :]
    d = np.abs(wrap(head - ph))
    return np.nanmean(np.where(np.isnan(d), 0.0, (d <= FOLLOW).astype(float)), axis=2)


def lock(cues, head, c):
    """Lock to cue c: the order parameter |mean exp(i(theta - phi_c))| over the trial's samples, per seed and
    trial. Locked (a bounded relative phase) gives about 1; slipping gives a small value; no heading gives 0."""
    S, T, nsamp = head.shape
    t_abs = (np.arange(T)[:, None] * TAU + np.arange(nsamp)[None, :] * SAMPLE * DT)
    ph = cues.alpha[:, c][:, None, None] + cues.omega[c] * t_abs[None, :, :]
    rel = np.exp(1j * (head - ph))
    rel = np.where(np.isnan(head), 0.0, rel)
    return np.abs(rel.mean(axis=2))


def hit(cues, head, c):
    """Hit at the trial's end: last sample within HIT of cue c."""
    S, T, nsamp = head.shape
    t_end = np.arange(T) * TAU + (nsamp - 1) * SAMPLE * DT
    ph = cues.alpha[:, c][:, None] + cues.omega[c] * t_end[None, :]
    d = np.abs(wrap(head[:, :, -1] - ph))
    return np.where(np.isnan(d), False, d <= HIT)


def rate(head):
    """Measured rotation rate per trial from the unwrapped heading samples (rad per time unit)."""
    th = np.unwrap(head, axis=2)
    dt = SAMPLE * DT
    return (th[:, :, -1] - th[:, :, 0]) / (dt * (th.shape[2] - 1))


ORGS = (('L', 0.0), ('C', 0.0), ('D', 0.0), ('R', 2.0), ('R', 4.0), ('R', 8.0))


def label(kind, G):
    return {'L': 'L', 'C': 'chair', 'D': 'leader'}.get(kind, f'R G{G:g}')


def line(name, *vals):
    print(f'{name:28s}' + ''.join(f'{v:>9}' if isinstance(v, str) else f'{v:9.3f}' for v in vals))


def tongue(S, seed):
    """Test 1b: one cue at Omega, organisms with their clocks at .10. Follow fraction over trials 3 to 10."""
    print('Test 1b, the tongue: one cue at Omega, clocks at .10 (ring beta .1207, chair chi_h .2); trials 3-10')
    omegas = (-.3, -.2, -.1, -.05, 0.0, .05, .1, .15, .2, .3)
    for measure, fn in (('F (within 45 deg)', follow), ('LOCK (order parameter)', lock), ('hit (20 deg, trial end)', hit)):
        print(f'  {measure}')
        line('Omega', *[f'{o:.2f}' for o in omegas])
        for kind, G in ORGS:
            row = []
            for om in omegas:
                rng = np.random.default_rng([seed, 1, int(om * 1000) % 100000, 7])
                cues = Cues(rng, S, [om], [1.0], 10)
                clock = .10 if kind in ('R', 'C') else 0.0
                h, _ = simulate(cues, rng, kind, G=G, clock=clock)
                row.append(fn(cues, h, 0)[:, 2:].mean())
            line(label(kind, G), *row)
    for G in (2.0, 4.0, 8.0):
        print(f'   K = eps/V at G {G:g}: {EPS / V_of(G):.3f}  (chair K {EPS / V_CHAIR:.3f})')


def two(S, seed):
    """Test 2: target at +.10, distractor at -.10, equal weights; clocks tuned to the target, zero, or to the
    distractor. F_target, F_distractor, hit_target over trials 3 to 20."""
    print('Test 2, two cues: target +.10, distractor -.10, equal weights .3; trials 3-20')
    line('organism, clock', 'F_targ', 'F_dist', 'L_targ', 'L_dist', 'hit_targ', 'hit_dist', 'seeds>t', 'seeds>d')
    for clock_name, om in (('tuned to target', .10), ('midway', 0.0), ('tuned to distractor', -.10)):
        for kind, G in ORGS:
            rng = np.random.default_rng([seed, 2, int(om * 100) % 1000, 11])
            cues = Cues(rng, S, [.10, -.10], [1.0, 1.0], 20)
            clock = om if kind in ('R', 'C') else 0.0
            h, _ = simulate(cues, rng, kind, G=G, clock=clock)
            ft, fd = follow(cues, h, 0)[:, 2:], follow(cues, h, 1)[:, 2:]
            lt, ld = lock(cues, h, 0)[:, 2:], lock(cues, h, 1)[:, 2:]
            ht, hd = hit(cues, h, 0)[:, 2:], hit(cues, h, 1)[:, 2:]
            line(f'{label(kind, G)}, {clock_name}', ft.mean(), fd.mean(), lt.mean(), ld.mean(), ht.mean(), hd.mean(),
                 (lt.mean(1) > .8).mean(), (ld.mean(1) > .8).mean())


def weight(S, seed):
    """Test 2c: selection by weight on a moving target (w 1 against 0), no clocks."""
    print('Test 2c, weight selection on a moving target: target +.10 at w 1, distractor at w 0, clocks 0; trials 3-20')
    line('organism', 'F_targ', 'hit_targ')
    for kind, G in ORGS:
        rng = np.random.default_rng([seed, 3, 5])
        cues = Cues(rng, S, [.10, -.10], [1.0, 0.0], 20)
        h, _ = simulate(cues, rng, kind, G=G, clock=0.0)
        line(label(kind, G), follow(cues, h, 0)[:, 2:].mean(), hit(cues, h, 0)[:, 2:].mean())


def retune(S, seed):
    """Test 3a: clock moved by the experimenter from -.10 to +.10 at trial 21 (index 20)."""
    print('Test 3a, external retune at trial 21: clock -.10 -> +.10; F_target by trial')
    trials = list(range(18, 26))
    line('organism', *[f't{t + 1}' for t in trials])
    for kind, G in ORGS:
        if kind not in ('R', 'C'):
            continue
        rng = np.random.default_rng([seed, 4, 3])
        cues = Cues(rng, S, [.10, -.10], [1.0, 1.0], 30)
        h, _ = simulate(cues, rng, kind, G=G, clock=-.10, retune=(20, .10))
        ft = follow(cues, h, 0)
        line(label(kind, G), *[ft[:, t].mean() for t in trials])


def selftune(S, seed, eta=.004, start=.02):
    """Test 3b: self-tuning clock from omega0 = start (nearer the target); 30 trials."""
    print(f'Test 3b, self-tuning (eta {eta}) from clock {start}: target +.10, distractor -.10')
    line('organism', 'F_t 1-10', 'F_t 11-20', 'F_t 21-30', 'frac->targ', 'frac->dist', 'clock@30', 'sd clock')
    for kind, G in ORGS:
        if kind not in ('R', 'C'):
            continue
        rng = np.random.default_rng([seed, 5, 9])
        cues = Cues(rng, S, [.10, -.10], [1.0, 1.0], 30)
        h, cl = simulate(cues, rng, kind, G=G, clock=start, adapt=eta)
        ft = follow(cues, h, 0)
        fd = follow(cues, h, 1)
        to_t = (ft[:, 20:].mean(1) > .6).mean()
        to_d = (fd[:, 20:].mean(1) > .6).mean()
        line(label(kind, G), ft[:, :10].mean(), ft[:, 10:20].mean(), ft[:, 20:].mean(), to_t, to_d,
             cl[:, 29].mean(), cl[:, 29].std())


def hold(S, seed, eta=.004):
    """Test 3c: clocks start tuned (.10); the target is absent on trials 31-40 and returns for 41-50. Run with the
    self-tuning rule on (the clock keeps adapting to what is present) and off (a frozen clock)."""
    print(f'Test 3c, hold: clock tuned to .10; target off on trials 31-40 (distractor stays), back 41-50')
    line('organism, rule', 'F_t 21-30', 'F_t 31', 'F_t 32', 'F_t 33-35', 'F_t 36-40', 'F_t 41', 'F_t 42-50',
         'clock@40', 'F_d 31-40')
    for rule_name, rule in (('rule on', eta), ('rule off', 0.0)):
        for kind, G in ORGS:
            if kind not in ('R', 'C') and rule_name == 'rule off':
                continue
            rng = np.random.default_rng([seed, 6, 13])
            cues = Cues(rng, S, [.10, -.10], [1.0, 1.0], 50, off={0: (30, 40)})
            clock = .10 if kind in ('R', 'C') else 0.0
            h, cl = simulate(cues, rng, kind, G=G, clock=clock, adapt=(rule if kind in ('R', 'C') else 0.0))
            ft = follow(cues, h, 0)
            fd = follow(cues, h, 1)
            line(f'{label(kind, G)}, {rule_name}', ft[:, 20:30].mean(), ft[:, 30].mean(), ft[:, 31].mean(),
                 ft[:, 32:35].mean(), ft[:, 35:40].mean(), ft[:, 40].mean(), ft[:, 41:].mean(),
                 cl[:, 39].mean(), fd[:, 30:40].mean())


def blank_rate(S, seed):
    """Test 1a: no cue; the measured rotation rate against the derived clock."""
    print('Test 1a, the clock: no cue, measured rotation rate (rad per time unit) over trials 2-5')
    line('organism', 'clock set', 'measured', 'sd')
    for kind, G in (('R', 2.0), ('R', 4.0), ('R', 8.0), ('C', 0.0)):
        for om in (0.0, .05, .10, .20):
            rng = np.random.default_rng([seed, 0, int(om * 100)])
            cues = Cues(rng, S, [0.0], [0.0], 5)
            h, _ = simulate(cues, rng, kind, G=G, clock=om)
            r = rate(h)[:, 1:]
            line(f'{label(kind, G)} clock {om:.2f}', om, r.mean(), r.std())


TESTS = dict(blank=blank_rate, tongue=tongue, two=two, weight=weight, retune=retune, selftune=selftune, hold=hold)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tests', nargs='*', default=list(TESTS))
    ap.add_argument('--seeds', type=int, default=500)
    ap.add_argument('--seed', type=int, default=14)
    ap.add_argument('--eta', type=float, default=.004)
    ap.add_argument('--start', type=float, default=.02)
    a = ap.parse_args()
    for t in a.tests:
        if t == 'selftune':
            selftune(a.seeds, a.seed, eta=a.eta, start=a.start)
        elif t == 'hold':
            hold(a.seeds, a.seed, eta=a.eta)
        else:
            TESTS[t](a.seeds, a.seed)
        print()


if __name__ == '__main__':
    main()
