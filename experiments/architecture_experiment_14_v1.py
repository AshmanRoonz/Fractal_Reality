"""Architecture of Wholeness, Experiment 14: attention as resonance, a ring whose turn keeps time.

Created: 2026-11-08. Last updated: 2026-11-08. Version: 1.0 (results appended 2026-11-08).
Pre-registration, frozen before this file was written:
    plans/architecture_experiment_14_resonant_attention_2026_11_08.md (v1.1)
Derivation tool: architecture_experiment_14_reduced_v1.py (the heading law with a clock, 500 seeds).
Run:    python -I architecture_experiment_14_v1.py [t1a t1b t2 t2c t3a t3b t3c] [--seeds 100] [--out DIR]
Needs numpy and architecture_experiment_12_v1.py beside it. Writes one trials CSV and one summary CSV per
test to --out (default: architecture_experiment_14_results beside this file).

WHAT IS BUILT. Experiment 12's three organisms from the same 16 parts (L list, N node as chair G_h 0 and leader
G_h 1.5, R ring at G 2, 4, 8), with a clock. The ring reads its two neighbours unequally, weights 1/2 - b on the
left and 1/2 + b on the right (b is the plan's beta; E12's hub constant is also named BETA, so the code calls
the ring's asymmetry `asym`). For a first-mode pattern that reading is the pattern rotated by chi = atan(2 b tan
(2 pi/n)), so the turn rotates at omega0 = tan chi = 2 b tan(2 pi/n), exact and independent of G, with the
heading law's stiffness V unchanged. The node's clock is the hub broadcast rotated by chi_h, omega_h = tan(chi_h/2)
(a reduced-model derivation, band 25%). The list has no coupling and no clock. Cues rotate, phi_c(t) = Omega_c t
+ alpha_c, continuous in time across trials, entering as I_j = sum_c eps w_c exp(i(psi_j + phi_c(t))), eps .3.
Self-tuning (Tests 3b, 3c): asym <- asym + dt eta_b pull, chi_h <- chi_h + dt eta_chi pull, pull = Im(conj(P^) I^)/V,
P^ the normalized population vector, I^ the input's first mode, V = V(G) for the ring and 5.9 for the chair;
eta_b = .004/(2 tan(2 pi/n)), eta_chi = .008, so the clock rate moves at .004 times the pull. Boundary on, dt .05,
sigma .05, trials of 40 time units (800 steps), heading sampled every 5 steps, 100 seeds, nothing resets.

ONE CLARIFICATION, made before any run. Test 1a has no cue, and a node has no pattern until a cue forms one, so
every organism gets one priming trial with a static cue at a random direction (w 1) before its five blank
trials; the blank trials 2 to 5 are scored as planned. The ring's pattern exists from the start and is unaffected.

MEASURES (per seed and trial). rate: slope of the unwrapped heading samples. F_c: fraction of samples within 45
degrees of cue c. LOCK_c: |mean exp(i(theta - phi_c))| over the samples (no heading counts 0); locked = LOCK >= .97
(one cue); follows = seed mean LOCK over the scored trials > .8 (two cues). hit_c: within 20 degrees at the end.
clock: omega0 or omega_h. winding of every ring.

FROZEN PREDICTIONS (D closed form, Dr reduced model, C carried, G guess; bands +-.05 rings and list, +-.10 chair).
Test 1a, no cue, clocks 0, .05, .10, .20.
  P1.1 (D) rings rotate at 2 b tan(2 pi/n) within 5%: .000, .050, .100, .200; (Dr) chair at tan(chi_h/2) within 25%
       (.100 +- .025); (G) leader does not rotate; the list has no heading.
Test 1b, one cue at Omega in {-.3, -.2, -.1, -.05, 0, .05, .1, .15, .2, .3}, clocks .10, trials 3-10.
  P1.2 (D) locked (LOCK >= .97) exactly where |Omega - .10| <= K (K .173, .081, .041; chair .051): G 2 at -.05..
       .20; G 4 at .05, .10, .15; G 8 at .10; chair at .05, .10, .15; outside LOCK <= .93. The list locked at all
       ten; the leader only at 0.
  P1.3 (D) hits follow the lag: all rings and the chair >= .95 at .10; G 2 >= .95 at .05, <= .15 at .15, 0 at 0 and
       -.05; G 4 and G 8 <= .10 away from .10; the list >= .95 everywhere.
Test 2, target +.10 and distractor -.10, w 1 each, clocks +.10 / 0 / -.10, trials 3-20.
  P2.1 (Dr) tuned to the target: rings and chair follow it in >= .95 of seeds, none the distractor; F_target 1.00
       (G 4, G 8, chair), .75 (G 2); hits .48, .57, .82, .70 (G 2, 4, 8, chair).
  P2.2 (D) the list follows neither in any seed: F .50 both, LOCK .65 both, hits .23; the leader F .24, hits .13.
  P2.3 (Dr) clocks 0: no ring and not the chair follows either (0 seeds), F <= .25 both, G 2 F .18.
  P2.4 (Dr) tuned to the distractor: the mirror image of P2.1.
  P2.5 (D) Test 2c, w (1, 0), clocks 0: the list F 1.00 hits 1.00; G 2 F 1.00 hits 0; G 4, G 8, chair F <= .25,
       hits <= .10.
Test 3a, clocks -.10 moved to +.10 at trial 21.
  P3.1 (D, Dr) F_target .99 by trial 22 (G 2, G 4) and by 23 (G 8, chair); within trial 21: .81, .69, .50, .56;
       at trial 22: .99, .99, .87, .92.
Test 3b, self-tuning from clock .02, 30 trials.
  P3.2 (Dr) G 2 and G 4 tuned to the target by trial 20 in >= .95 of seeds, clock .10 +- .01 at trial 30, F_target
       21-30 .83 and 1.00; chair .6 to .8 of seeds by 30 (clock .094); G 8 <= .10 (clock .04 to .07, F .19);
       none to the distractor (<= .05).
Test 3c, clocks .10, target absent on trials 31-40, back 41-50, rule on and off.
  P3.3 (Dr) F_target on trials 31 / 32 / 33-35 / 36-40 and F_distractor 31-40, bands +-.10:
       G 8 on 1.00 1.00 .98 .45 (.25); chair on 1.00 .99 .75 .06 (.25); G 4 on .88 .46 .02 .25 (.24);
       G 2 on .28 .24 .25 .25 (.60, clock near -.04 at 40); G 8 off 1.00 .96 .53 .03; chair off .99 .74 .16 .00;
       G 4 off .61 .10 .00 .42; G 2 off .29 .54 .37 .32 (.17); the list .25 throughout and F_distractor 1.00.
  P3.4 (Dr) return: F_target 42-50 >= .95 (G 8), .90 (G 4), .95 (chair) with the rule on; G 2 on stays with the
       distractor (.30), G 2 off returns (.75).
  P3.5 (C) every ring at G >= 4 keeps winding 1 at every trial; G 2 may lose and remake its turn in <= 5% of
       trials under two cues.
Kill conditions. Against the readings: K1 the list follows exactly one cue in >= .3 of seeds (Test 2); K2 a
tuned ring follows the target in < .8 of seeds; K3 the G 2 ring at clock 0 follows one cue in >= .3 of seeds;
K4 self-tuning sends any organism to the distractor in > .2 of seeds; K5 with the rule on G 8 holds less than
G 4 (F_target 33-35); K6 the chair with its measured clock within .02 of .10 follows the target in < .5 of
seeds. Against the design: K7 the ring's measured rate off 2 b tan(2 pi/n) by > 10% at any b (then b is reset
from the measured rate for the later tests and P1.1's ring clause is a MISS); K8 the chair's rate at chi_h .1993
outside [.075, .125] (then chi_h is reset from the measured ratio; P1.1's chair clause a MISS); K9 the full ring
at clock .10 with one cue at .10 and .30 (G 2, 4) off the reduced model by > .05 in F or LOCK (the bands are
reported as failed and the run continues).
RESULTS (run 2026-11-08, 100 seeds, 497 s; grading in architecture_experiment_14_results/grading_2026_11_08.txt).
Tally: 5 PASS (P1.1, P2.2, P2.5, P3.4, P3.5), 8 MISS (P1.2, P1.3, P2.1, P2.3, P2.4, P3.1, P3.2, P3.3), every miss
with clauses that pass; no kill condition against the readings fired (K1 to K5 not fired; K6 not applicable, the
chair's clock sat at .077); K7 and K8 not fired; K9 fired on one of its four cells.
Test 1a. Rings rotate at .000/.050/.100/.200 for clocks 0/.05/.10/.20 at every G (sd .002): the clock law is exact.
  Leader 0. Chair .038/.077/.156: .77 of tan(chi_h/2), inside the pre-registered 25% band, so not reset. Every
  chair clause that depends on its lag (hits, 45 degree reach, hold) misses below; every chair clause about
  selection passes.
Test 1b. Locked sets exactly as derived: G 2 {-.05, 0, .05, .10, .15, .20}, G 4 {.05, .10, .15}, G 8 {.10}, list all
  ten, leader {0}; chair {.05, .10} (predicted .15 too; its tongue is centred at .077). Max LOCK outside .86/.74/
  .93/.74. Hits at .10: rings 1.00/1.00/1.00, chair .00; G 2 at .05/.15/0/-.05: 1.00/.00/.00/.00; list 1.00
  everywhere. New: at Omega .3 the G 2 ring lost its turn (winding 1 kept in 36.5% of seed-trials; 99.6% at -.1);
  K9 fired on that cell (F .056 vs .136, LOCK .862 vs .620), the other three within .003.
Test 2. Follows (per-seed LOCK > .8): every coupled organism 1.00 on the target at clock +.10, 0 on either cue at
  clock 0, 1.00 on the distractor at -.10; the list 0/0 (F .50/.50, LOCK .65, hits .22); the leader 0 (F .24,
  hits .12). F_target tuned: G 2 .825 (pred .75), G 4 1.000, G 8 .993, chair .519 (pred 1.00: lag). Hits tuned
  .527/.602/.842 (pred .48/.57/.82), chair .000 (pred .70). Clock 0: F .28/.16/.21/.19 (G 2 pred .18).
Test 2c. List F 1.00 hit 1.00; G 2 F .99 hit .00; G 4 .17/.07; G 8 .24/.10; chair .21/.04: as derived.
Test 3a. F_target at trials 21/22/23: G 2 .70/.82/.82 (pred .81/.99), G 4 .65/.97/.99 (pred .69/.99), G 8 .48/.84/
  .96 (pred .50/.87), chair .48/.52/.52 (pred .56/.92). G 2's ceiling is its two-cue reach; the frozen .99 came
  from the reduced model with the lag angle left at its pre-retune sign (found after the fact: with the lag
  negative the reduced model gives .99, at zero .85, with the correct sign .75). The chair's ceiling is its lag.
Test 3b. G 2 tuned to the target by trial 20 in 1.00 of seeds, clock .108, measured rate .100, F 21-30 .88 (pred
  .83); G 4 1.00, clock .106, rate .100, F 1.00. G 8: clock .054 (pred .04 to .07), F .19 (pred .19); by the
  frozen lock criterion .56 of seeds "follow" over trials 21-30, because slow slipping inflates LOCK; by the reach
  criterion the reduced model used it is not tuned, as predicted. Chair: locked to the target by trial 30 in 1.00
  of seeds (pred .6 to .8), rate .104, clock .096, F .10 (locked out of reach). None to the distractor.
Test 3c. F_target on trials 31 / 32 / 33-35 / 36-40, F_distractor 31-40, clock at 40:
  G 8 on 1.00 1.00 .96 .35 (.25) .098 | chair on .99 .71 .15 .00 (.25) .124 | G 4 on .83 .36 .01 .24 (.24) .084 |
  G 2 on .33 .25 .25 .25 (.55; .97 on 36-40) -.040 | G 8 off 1.00 .97 .57 .05 | chair off .12 .00 .39 .24 |
  G 4 off .62 .11 .00 .40 | G 2 off .31 .52 .33 .30 (.15) | list .25 and F_distractor 1.00.
  29 of 30 ring cells within .10 (G 8 on, 36-40, at the band's edge: .35 vs .45); the chair's six cells miss.
  Return, trials 42-50: G 8 on 1.00, G 4 on .91, chair on .99, G 2 on .33 (clock -.089: it stays with the
  distractor), G 2 off .82.
Windings. G 4 and G 8 at winding 1 in 100% of seed-trials in every test; G 2 98.0% over all tests, 97.7% in Test 2.
After the fact. (1) With the rule on, the chair corrected its own clock (variable .133, measured .103) and reached
  F 1.00 before the blank: the self-tuning rule compensates a mis-derived loop clock. (2) The fast ring's turn
  breaks under a cue that slips fast past it (one cue at Omega .3, 36% kept), which the reduced model cannot show:
  the fast ring is the most distractible and the most fragile. (3) The hold ordering is exact, stiff > middle >
  fast, the fast ring captured by what remains and staying captured; the rule lengthens the stiff ring's hold
  (.96 against .57 on trials 33-35). (4) Two defects of the derivation tool: the lag angle was not updated at
  retune, and the plan's "follows" criterion (LOCK > .8) is not the tuned criterion the reduced model used
  (reach > .6); the second matters only for slow slipping.
"""
import argparse
import os
import sys
import time
import warnings
from math import pi, sqrt, tan, atan

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from architecture_experiment_12_v1 import (N, DT, STEPS, SIGMA, HIT, PSI, EPSI, CEPSI, BETA, K_IN, K_OUT, G_P,
                                           wrap, lim, cnoise, rest, V_of, Organism, write_csv)

warnings.filterwarnings('ignore', 'Mean of empty slice')
warnings.filterwarnings('ignore', 'invalid value encountered')
warnings.filterwarnings('ignore', 'Degrees of freedom')

TAU = STEPS * DT                 # 40 time units
EPS = .3
SAMPLE = 5
NSAMP = STEPS // SAMPLE
FOLLOW = np.deg2rad(45)
TAN_A = tan(2 * pi / N)
V_CHAIR = 5.9
ETA_OMEGA = .004
CLOCK_TUNED = .10
OMEGAS_1B = (-.3, -.2, -.1, -.05, 0.0, .05, .1, .15, .2, .3)
ORGS = (('L', 0.0), ('N', 0.0), ('N', 1.5), ('R', 2.0), ('R', 4.0), ('R', 8.0))


def label(kind, p):
    return {'L': 'L', 'N': 'chair' if p == 0.0 else 'leader'}.get(kind, f'R G{p:g}')


def asym_for(omega):
    return omega / (2 * TAN_A)


def chi_for(omega):
    return 2 * atan(omega)


# ------------------------------------------------------------------- cues
class Cues:
    """Rotating cues phi_c(t) = Omega_c t + alpha_c (alpha_c uniform per seed), weight w_c, present on trials
    where on[c, t] holds. Cue 0 is the target."""

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

    def inputs(self, t, t_abs):
        """I (S, N) and its first mode I^ (S,) at absolute time t_abs within trial t."""
        Ihat = np.zeros(self.S, complex)
        for c in range(len(self.omega)):
            if self.on[c, t] and self.w[c] != 0:
                Ihat += EPS * self.w[c] * np.exp(1j * self.phase(c, t_abs))
        return Ihat[:, None] * EPSI[None, :], Ihat


# --------------------------------------------------------------- organism
class Organism14(Organism):
    """Experiment 12's organism with a clock: unequal neighbour reading (ring), rotated hub broadcast (node),
    and the self-tuning rule on either."""

    def __init__(self, kind, S, rng, G=4.0, Gh=1.5, clock=0.0):
        super().__init__(kind, S, rng, G=G, Gh=Gh, boundary=True, reconnect=True)
        self.asym = np.zeros(S)
        self.chi_h = np.zeros(S)
        self.set_clock(clock)
        self.V = V_of(G) if kind == 'R' else V_CHAIR

    def set_clock(self, omega):
        if self.kind == 'R':
            self.asym[:] = asym_for(omega)
        elif self.kind == 'N':
            self.chi_h[:] = chi_for(omega)

    def clock(self):
        if self.kind == 'R':
            return 2 * self.asym * TAN_A
        if self.kind == 'N':
            return np.tan(self.chi_h / 2)
        return np.zeros(self.S)

    def reading(self):
        zl = self.z[self.rows, self.left]
        zr = self.z[self.rows, self.right]
        return ((.5 - self.asym)[:, None] * zl + (.5 + self.asym)[:, None] * zr) * self.alive

    def step(self, I, rng, hub_pull=None, sigma=SIGMA):
        if self.boundary:
            I = I - I.mean(1, keepdims=True)
        if self.kind == 'R':
            v = self.G * self.reading() + I
        elif self.kind == 'N':
            Y = self.hub_vec() * np.exp(1j * self.chi_h)
            v = G_P * (I + K_OUT * Y[:, None] * EPSI[None, :])
        else:
            v = G_P * I
        z = self.z + DT * (-self.z + lim(v))
        if sigma:
            z = z + sqrt(DT) * sigma * cnoise(rng, z.shape)
        self.z = z * self.alive
        if self.kind == 'N':
            P = self.popvec()
            x = K_IN * np.real(P[:, None] * CEPSI[None, :])
            inhib = BETA * (self.y.sum(1, keepdims=True) - self.y)
            y = self.y + DT * (-self.y + np.tanh(self.Gh * self.y - inhib + x))
            self.y = y * self.hub_alive[:, None]

    def adapt(self, Ihat, eta_omega):
        P = self.popvec()
        Phat = P / np.maximum(np.abs(P), 1e-9)
        pull = np.imag(np.conj(Phat) * Ihat) / self.V
        if self.kind == 'R':
            self.asym = np.clip(self.asym + DT * (eta_omega / (2 * TAN_A)) * pull, -.5, .5)
        elif self.kind == 'N':
            self.chi_h = np.clip(self.chi_h + DT * (2 * eta_omega) * pull, -pi / 2, pi / 2)


def make14(kind, S, rng, p, clock=0.0):
    if kind == 'R':
        return Organism14('R', S, rng, G=p, clock=clock)
    if kind == 'N':
        return Organism14('N', S, rng, Gh=p, clock=clock)
    return Organism14('L', S, rng)


# -------------------------------------------------------------------- run
def run14(org, cues, rng, eta=0.0, retune=None, prime=None):
    """One organism through the cues' trials. eta: self-tuning rate on the clock (0 = off). retune: (trial, new
    clock). prime: a Cues object with one static cue, run for one unscored trial before the main trials.
    Returns heading samples (S, T, NSAMP), clock (S, T), winding (S, T)."""
    S, T = cues.S, cues.T
    head = np.full((S, T, NSAMP), np.nan)
    clock = np.zeros((S, T))
    wind = np.zeros((S, T), int)
    if prime is not None:
        for s in range(STEPS):
            I, _ = prime.inputs(0, s * DT)
            org.step(I, rng)
    for t in range(T):
        if retune is not None and t == retune[0]:
            org.set_clock(retune[1])
        for s in range(STEPS):
            t_abs = t * TAU + s * DT
            I, Ihat = cues.inputs(t, t_abs)
            org.step(I, rng)
            if eta:
                org.adapt(Ihat, eta)
            if s % SAMPLE == SAMPLE - 1:
                head[:, t, s // SAMPLE] = org.heading()
        clock[:, t] = org.clock()
        wind[:, t] = org.winding() if org.kind == 'R' else 0
    return head, clock, wind


def sample_times(T):
    s = (np.arange(NSAMP) + 1) * SAMPLE * DT - DT
    return np.arange(T)[:, None] * TAU + s[None, :]


def measures(cues, head):
    """Per seed and trial: F_c, LOCK_c, hit_c for each cue, and the rotation rate."""
    S, T, _ = head.shape
    tt = sample_times(T)
    out = {}
    for c in range(len(cues.omega)):
        ph = cues.alpha[:, c][:, None, None] + cues.omega[c] * tt[None, :, :]
        d = wrap(head - ph)
        out[f'F{c}'] = np.where(np.isnan(d), 0.0, (np.abs(d) <= FOLLOW).astype(float)).mean(2)
        rel = np.where(np.isnan(d), 0.0, np.exp(1j * np.nan_to_num(d)))
        out[f'LOCK{c}'] = np.abs(rel.mean(2))
        dend = d[:, :, -1]
        out[f'hit{c}'] = np.where(np.isnan(dend), False, np.abs(dend) <= HIT)
    th = np.unwrap(head, axis=2)
    out['rate'] = (th[:, :, -1] - th[:, :, 0]) / (SAMPLE * DT * (NSAMP - 1))
    return out


def rows_from(meta, cues, head, clock, wind):
    m = measures(cues, head)
    S, T = clock.shape
    rows = []
    for s in range(S):
        for t in range(T):
            r = dict(meta, seed=s, trial=t + 1, clock=float(clock[s, t]), winding=int(wind[s, t]),
                     rate=float(m['rate'][s, t]))
            for c in range(len(cues.omega)):
                r[f'F{c}'] = float(m[f'F{c}'][s, t])
                r[f'LOCK{c}'] = float(m[f'LOCK{c}'][s, t])
                r[f'hit{c}'] = int(m[f'hit{c}'][s, t])
            rows.append(r)
    return rows


def summarize(rows, keys, window, extra=()):
    """Means over the trials in window (1-based, inclusive) grouped by keys; plus seed-level 'follows' fractions
    (seed mean LOCK over the window > .8) for each cue present."""
    import collections
    groups = collections.OrderedDict()
    for r in rows:
        if window[0] <= r['trial'] <= window[1]:
            groups.setdefault(tuple(r[k] for k in keys), []).append(r)
    out = []
    for g, rs in groups.items():
        rec = dict(zip(keys, g))
        rec['n_trials'] = len(rs)
        for col in ('F0', 'F1', 'LOCK0', 'LOCK1', 'hit0', 'hit1', 'rate', 'clock'):
            if col in rs[0]:
                vals = np.array([r[col] for r in rs], float)
                rec[col] = float(np.nanmean(vals))
                if col == 'rate':
                    rec['rate_sd'] = float(np.nanstd(vals))
                if col == 'clock':
                    rec['clock_sd'] = float(np.nanstd(vals))
        if 'winding' in rs[0]:
            rec['winding1'] = float(np.mean([r['winding'] == 1 for r in rs]))
        seeds = sorted(set(r['seed'] for r in rs))
        for c in (0, 1):
            if f'LOCK{c}' in rs[0]:
                per = [np.mean([r[f'LOCK{c}'] for r in rs if r['seed'] == s]) for s in seeds]
                rec[f'follows{c}'] = float(np.mean([p > .8 for p in per]))
                rec[f'locked{c}'] = float(np.mean([r[f'LOCK{c}'] >= .97 for r in rs]))
        for k, fn in extra:
            rec[k] = fn(rs)
        out.append(rec)
    return out


def show(summary, cols):
    keys = [k for k in ('organism', 'clock_set', 'Omega', 'rule') if k in summary[0]]
    print('  ' + ' '.join(f'{k:>12}' for k in keys) + ' ' + ' '.join(f'{c:>9}' for c in cols))
    for rec in summary:
        print('  ' + ' '.join(f'{str(rec[k]):>12}' for k in keys) + ' '
              + ' '.join(f'{rec.get(c, float("nan")):9.3f}' for c in cols))


def progress(msg, t0):
    print(f'[{time.time() - t0:7.1f}s] {msg}', flush=True)


# ------------------------------------------------------------------ tests
def t1a(S, out, seed, t0):
    rows = []
    for oi, (kind, p) in enumerate(ORGS):
        clocks = (0.0,) if kind == 'L' else (0.0, .05, .10, .20)
        for ci, om in enumerate(clocks):
            wr = np.random.default_rng([seed, 1, ci])
            prime = Cues(wr, S, [0.0], [1.0], 1)
            cues = Cues(wr, S, [0.0], [0.0], 5)
            org = make14(kind, S, np.random.default_rng([seed, 1, 2, oi, ci]), p, clock=om)
            head, clock, wind = run14(org, cues, np.random.default_rng([seed, 1, 3, oi, ci]), prime=prime)
            rows += rows_from(dict(test='t1a', organism=label(kind, p), clock_set=om), cues, head, clock, wind)
            progress(f't1a {label(kind, p)} clock {om}', t0)
    write_csv(out, 't1a_trials', rows)
    summ = summarize(rows, ('organism', 'clock_set'), (2, 5))
    write_csv(out, 't1a_summary', summ)
    print('Test 1a: measured rotation rate over blank trials 2-5 (rate), against the clock set')
    show(summ, ('rate', 'rate_sd', 'clock'))
    return summ


def t1b(S, out, seed, t0, clock=CLOCK_TUNED, chair_clock=CLOCK_TUNED):
    rows = []
    for wi, om in enumerate(OMEGAS_1B):
        wr = np.random.default_rng([seed, 2, wi])
        cues = Cues(wr, S, [om], [1.0], 10)
        for oi, (kind, p) in enumerate(ORGS):
            ck = chair_clock if kind == 'N' else clock
            org = make14(kind, S, np.random.default_rng([seed, 2, 2, oi, wi]), p, clock=ck)
            head, ck_, wind = run14(org, cues, np.random.default_rng([seed, 2, 3, oi, wi]))
            rows += rows_from(dict(test='t1b', organism=label(kind, p), Omega=om), cues, head, ck_, wind)
        progress(f't1b Omega {om}', t0)
    write_csv(out, 't1b_trials', rows)
    summ = summarize(rows, ('organism', 'Omega'), (3, 10))
    write_csv(out, 't1b_summary', summ)
    print('Test 1b: one cue at Omega, clocks .10, trials 3-10')
    show(summ, ('F0', 'LOCK0', 'locked0', 'hit0', 'winding1'))
    return summ


def t2(S, out, seed, t0, clock=CLOCK_TUNED):
    rows = []
    wr = np.random.default_rng([seed, 3, 1])
    cues = Cues(wr, S, [.10, -.10], [1.0, 1.0], 20)
    for ci, om in enumerate((clock, 0.0, -clock)):
        for oi, (kind, p) in enumerate(ORGS):
            if kind == 'L' and ci > 0:
                continue
            org = make14(kind, S, np.random.default_rng([seed, 3, 2, oi, ci]), p, clock=om)
            head, ck, wind = run14(org, cues, np.random.default_rng([seed, 3, 3, oi, ci]))
            rows += rows_from(dict(test='t2', organism=label(kind, p), clock_set=om), cues, head, ck, wind)
            progress(f't2 {label(kind, p)} clock {om}', t0)
    write_csv(out, 't2_trials', rows)
    summ = summarize(rows, ('organism', 'clock_set'), (3, 20))
    write_csv(out, 't2_summary', summ)
    print('Test 2: target +.10, distractor -.10, trials 3-20')
    show(summ, ('F0', 'F1', 'LOCK0', 'LOCK1', 'hit0', 'hit1', 'follows0', 'follows1', 'winding1'))
    return summ


def t2c(S, out, seed, t0):
    rows = []
    wr = np.random.default_rng([seed, 4, 1])
    cues = Cues(wr, S, [.10, -.10], [1.0, 0.0], 20)
    for oi, (kind, p) in enumerate(ORGS):
        org = make14(kind, S, np.random.default_rng([seed, 4, 2, oi]), p, clock=0.0)
        head, ck, wind = run14(org, cues, np.random.default_rng([seed, 4, 3, oi]))
        rows += rows_from(dict(test='t2c', organism=label(kind, p)), cues, head, ck, wind)
        progress(f't2c {label(kind, p)}', t0)
    write_csv(out, 't2c_trials', rows)
    summ = summarize(rows, ('organism',), (3, 20))
    write_csv(out, 't2c_summary', summ)
    print('Test 2c: weight selection on a moving target, clocks 0, trials 3-20')
    show(summ, ('F0', 'LOCK0', 'hit0', 'follows0', 'winding1'))
    return summ


def t3a(S, out, seed, t0, clock=CLOCK_TUNED):
    rows = []
    wr = np.random.default_rng([seed, 5, 1])
    cues = Cues(wr, S, [.10, -.10], [1.0, 1.0], 30)
    for oi, (kind, p) in enumerate(ORGS):
        if kind == 'L' or (kind == 'N' and p != 0.0):
            continue
        org = make14(kind, S, np.random.default_rng([seed, 5, 2, oi]), p, clock=-clock)
        head, ck, wind = run14(org, cues, np.random.default_rng([seed, 5, 3, oi]), retune=(20, clock))
        rows += rows_from(dict(test='t3a', organism=label(kind, p)), cues, head, ck, wind)
        progress(f't3a {label(kind, p)}', t0)
    write_csv(out, 't3a_trials', rows)
    print('Test 3a: retune at trial 21, F_target by trial')
    for kind, p in ORGS:
        if kind == 'L' or (kind == 'N' and p != 0.0):
            continue
        lab = label(kind, p)
        vals = [np.mean([r['F0'] for r in rows if r['organism'] == lab and r['trial'] == t]) for t in range(19, 27)]
        print(f'  {lab:8s} ' + ' '.join(f't{t}:{v:.3f}' for t, v in zip(range(19, 27), vals)))
    return rows


def t3b(S, out, seed, t0, start=.02):
    rows = []
    wr = np.random.default_rng([seed, 6, 1])
    cues = Cues(wr, S, [.10, -.10], [1.0, 1.0], 30)
    for oi, (kind, p) in enumerate(ORGS):
        if kind == 'L' or (kind == 'N' and p != 0.0):
            continue
        org = make14(kind, S, np.random.default_rng([seed, 6, 2, oi]), p, clock=start)
        head, ck, wind = run14(org, cues, np.random.default_rng([seed, 6, 3, oi]), eta=ETA_OMEGA)
        rows += rows_from(dict(test='t3b', organism=label(kind, p)), cues, head, ck, wind)
        progress(f't3b {label(kind, p)}', t0)
    write_csv(out, 't3b_trials', rows)
    print('Test 3b: self-tuning from clock .02')
    for w0, w1 in ((1, 10), (11, 20), (21, 30)):
        summ = summarize(rows, ('organism',), (w0, w1))
        print(f'  trials {w0}-{w1}')
        show(summ, ('F0', 'F1', 'follows0', 'follows1', 'clock', 'clock_sd', 'winding1'))
    return rows


def t3c(S, out, seed, t0, clock=CLOCK_TUNED):
    rows = []
    wr = np.random.default_rng([seed, 7, 1])
    cues = Cues(wr, S, [.10, -.10], [1.0, 1.0], 50, off={0: (30, 40)})
    for rule_name, eta in (('on', ETA_OMEGA), ('off', 0.0)):
        for oi, (kind, p) in enumerate(ORGS):
            if (kind == 'L' or (kind == 'N' and p != 0.0)) and rule_name == 'off':
                continue
            org = make14(kind, S, np.random.default_rng([seed, 7, 2, oi]), p, clock=clock)
            use_eta = eta if (kind == 'R' or (kind == 'N' and p == 0.0)) else 0.0
            head, ck, wind = run14(org, cues, np.random.default_rng([seed, 7, 3, oi]), eta=use_eta)
            rows += rows_from(dict(test='t3c', organism=label(kind, p), rule=rule_name), cues, head, ck, wind)
            progress(f't3c {label(kind, p)} rule {rule_name}', t0)
    write_csv(out, 't3c_trials', rows)
    print('Test 3c: hold; target absent on trials 31-40')
    for w0, w1 in ((21, 30), (31, 31), (32, 32), (33, 35), (36, 40), (41, 41), (42, 50)):
        summ = summarize(rows, ('organism', 'rule'), (w0, w1))
        print(f'  trials {w0}-{w1}')
        show(summ, ('F0', 'F1', 'LOCK0', 'clock', 'winding1'))
    return rows


TESTS = dict(t1a=t1a, t1b=t1b, t2=t2, t2c=t2c, t3a=t3a, t3b=t3b, t3c=t3c)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tests', nargs='*', default=list(TESTS))
    ap.add_argument('--seeds', type=int, default=100)
    ap.add_argument('--seed', type=int, default=14)
    ap.add_argument('--out', default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                  'architecture_experiment_14_results'))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    for t in a.tests:
        TESTS[t](a.seeds, a.out, a.seed, t0)
        print()
    progress('done', t0)


if __name__ == '__main__':
    main()
