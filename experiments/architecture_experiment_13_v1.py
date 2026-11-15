"""Architecture of Wholeness, Experiment 13: a harder task, where learning must carry the hit rate.

Created: 2026-11-07. Last updated: 2026-11-07. Version: 1.0 (results appended 2026-11-07, same day).

Pre-registration: plans/architecture_experiment_13_harder_task_2026_11_07.md (v1.0), frozen before this file was
written. Derivation tool: architecture_experiment_13_reduced_v1.py (the verified heading law integrated as one angle).
Built on Experiment 12's organisms (architecture_experiment_12_v1.py: parts, leak and limit law, boundary, list, node,
ring), imported unchanged. Everything below the RESULTS marker was written after the run.

WHAT IS BUILT. The same three organisms as Experiment 12, from the same 16 parts under the leak and limit law
(dt .05, sigma .05, 800 steps per trial of 40 time units), the boundary on (common-mode rejection), cue strength
eps .3, a hit within 20 degrees, 100 seeds: L the list; N the node at hub gain 0 (chair) and 1.5 (leader); R the
ring at G 2, 4, 8. The world: 100 trials in regimes of k trials, k in {2, 5, 10, 25}; the resource direction is
redrawn uniformly at each regime start and holds within the regime with 10 degree per-trial noise; one trial in four
is blank (no cue reaches the organism, the heading is still graded). Four sources announce on every cued trial: one
honest, three liars that lie on 9 of 10 trials each in its own random direction (or, in the coalition world, all in
one). Credibility r_s <- r_s + .2 (hit_s - r_s) at the end of every cued trial, graded on the revealed resource;
the weight used is the credibility above chance, w_s = max(0, (r_s - 1/9) / (8/9)) (corrected), with Experiment
12's raw form w_s = r_s and a gate (w_s = 1 if corrected credibility >= .5 else 0) in Test 3. Learning conditions:
true, none (weights fixed at .5), shuffle (each source graded against a uniformly random other trial's resource),
random (a coin flip per source and trial). Measures over trials 21 to 100: S_all (no heading = miss), S_cued,
S_blank, S_first (first cued trial of each regime), S_settled (cued trials from a regime's third trial on), the
credibilities at trial 100, and the ring's winding at every trial.

FROZEN PREDICTIONS (copied from the pre-registration; the reduced-model table is its section 5).
 P1.1 Derived (reduced model). Learned, L and R(2) hit .90 +- .05 of cued trials at every k; with weights fixed at .5,
      .31 +- .05; under random feedback within .03 of that. r_honest 1.00, r_liar .20 +- .03 in every organism alike.
 P1.2 Derived (closed form, reduced). Shuffle: r_honest .13, .16, .20, .33 (+-.03) at k 2, 5, 10, 25; L's cued hits
      .26, .30, .36, .51 (+-.05): at or below the unlearned level for k <= 5, about half the learned level at k 25.
 P1.3 Derived (reduced). The leader hits .11 to .13 at every k.
 P2.1 Derived (reduced). S_all per the table, +-.05: k 2: R(2) > L ~ R(4) > R(8); k 10: every ring > L, R(2) >= R(4)
      > R(8); k 25: the rings within .01 of each other, all above L by about .17.
      Table (S_all / S_cued / S_blank / S_first / S_settled):
        k 2 : L .68/.90/0/.90/-   R2 .76/.90/.33/.90/-   R4 .69/.82/.30/.76/-   R8 .49/.58/.22/.44/-
        k 5 : L .68/.90/0/.90/.90 R2 .82/.90/.55/.89/.91 R4 .79/.88/.53/.76/.91 R8 .69/.76/.46/.45/.89
        k 10: L .68/.90/0/.90/.90 R2 .84/.90/.64/.89/.90 R4 .83/.89/.63/.77/.91 R8 .79/.85/.61/.46/.92
        k 25: L .68/.90/0/.90/.90 R2 .85/.90/.68/.90/.90 R4 .85/.91/.69/.76/.91 R8 .85/.90/.70/.44/.93
        leader .11 to .13 at every k; chair = the R8 row within .10.
 P2.2 Derived (closed form). S_first = S_settled x P, P = 1.00, .86, .46 at G 2, 4, 8: rings .90, .77, .42 (+-.05)
      on the first cued trial of a regime at every k; L .90.
 P2.3 Derived (reduced). L hits no blank trial. Rings' S_blank .33/.30/.22 (k 2), .55/.53/.46 (k 5), .64/.63/.61
      (k 10), .68/.69/.70 (k 25) for G 2/4/8, +-.07.
 P2.4 Derived (reduced). Settled cued trials: R(2) within .01 of L; R(8) above L by .02 to .03.
 P2.5 Carried (Guess on the band). The chair follows the R(8) row within .10 on S_all, S_blank, S_first.
 P2.6 Carried. Every ring keeps winding 1 at every trial in every condition, 100 of 100.
 P3.1 Derived (reduced). Independent liars, k 10, cued hits for L and R(2): raw .80, corrected .90, gate .98 (+-.05);
      R(8) .79, .85, .89.
 P3.2 Derived (closed form, reduced). Coalition, k 10, cued hits for L and R(2): raw .59, corrected .76 (+-.05), gate
      .99 (+-.02); R(8) .62, .74, .90. The gate beats corrected weighting by >= .20 under the coalition and by <= .10
      against independent liars.
AGAINST THE READINGS: K1 R(2) beats L on settled cued trials by > .05 at any k. K2 any ring's S_blank < .40 at k 10.
 K3 R(8)'s S_first > .65 or R(2)'s < .80 at k 10. K4 the chair differs from R(8) by > .15 on S_first or S_blank at
 k 10. K5 under the coalition the gate beats corrected weighting by < .15. K6 the leader > .30 at any k.
AGAINST THE DESIGN: K7 the learned L within .10 of the unlearned L on cued trials. K8 random feedback leaves hits
 > .10 above the unlearned level.

Usage: python architecture_experiment_13_v1.py [smoke] [t1] [t3] [--seeds 100] [--seed 13] [--out DIR]

RESULTS (run 2026-11-07, 100 seeds, --seed 13; CSVs and run_2026_11_07.log in architecture_experiment_13_results/).
Correspondence check first: the list and the G 2 ring at k 10, learned, against the reduced model's row: all ten
measures within .015 (largest difference S_first of L, +.015). The reduced model stands for the full organisms here.
Tally: 11 frozen predictions, 7 PASS, 4 MISS, of which 3 are partial (one number, one clause, one measure); none
of the eight conditions listed against the readings or the design occurred.

Test 1, learned (S_all / S_cued / S_blank / S_first / S_settled):
  k 2 : L .680/.903/.000/.902/-   chair .580/.685/.258/.571/-   leader .116   R2 .765/.903/.345/.898/-
        R4 .692/.821/.298/.766/-   R8 .477/.561/.220/.431/-
  k 5 : L .678/.905/.000/.898/.904 chair .744/.821/.522/.538/.918 leader .120 R2 .818/.907/.553/.898/.909
        R4 .789/.872/.543/.742/.914 R8 .682/.753/.473/.419/.886
  k 10: L .676/.907/.000/.915/.907 chair .821/.879/.655/.562/.927 leader .116 R2 .837/.906/.635/.900/.905
        R4 .829/.896/.634/.767/.913 R8 .786/.845/.614/.433/.918
  k 25: L .681/.903/.000/.900/.904 chair .863/.915/.701/.557/.932 leader .127 R2 .843/.903/.653/.897/.904
        R4 .847/.906/.664/.761/.913 R8 .852/.904/.694/.407/.930
  credibilities at trial 100: honest 1.000 everywhere; liars .193 to .209.
Controls, S_cued of L at k 2, 5, 10, 25: none .309 .305 .297 .318; random .309 .302 .300 .313; shuffle .293 .294
  .359 .535 (honest credibility .130 .140 .192 .294, liars .10 to .13). Rings under shuffle: G 2 .207 .267 .399 .580,
  G 8 .139 .161 .280 .538.
Test 3, S_cued at k 10 (L, R2, R4, R8): independent liars, raw .805 .805 .805 .792; corrected .907 .906 .896 .845;
  gate .981 .982 .967 .890. Coalition: raw .606 .608 .616 .631; corrected .774 .775 .773 .749; gate .989 .989 .968 .888.

P1.1 PASS: learned L and R2 .903 to .907 at every k; unlearned .297 to .331; random within .013 of unlearned;
  credibilities as derived. P1.2 MISS on one number: shuffled honest credibility .294 at k 25 against .33 +- .03
  (the other three within .02; L's cued hits .293 .294 .359 .535 all within .05 of .26 .30 .36 .51, and at or below
  the unlearned level at k 2 and 5). After the fact: the closed form ignored the 10 degree per-trial noise; two
  resources of one regime agree within 20 degrees with probability .843, so honest credibility goes to
  .843 k/100 + (1 - k/100)/9 = .126 .148 .184 .294, each within .01 of the run. The reduced model had .300; I froze
  the closed form instead. P1.3 PASS: leader .116 to .127.
P2.1 PASS: all 16 S_all cells within .05 of the table (largest gap .013); k 2: R2 .765 > L .680 ~ R4 .692 > R8 .477;
  k 10: every ring above L .676, R2 .837 >= R4 .829 > R8 .786; k 25: rings .843 to .852, within .009, each .16 to
  .17 above L .681. P2.2 PASS: S_first .898 to .900 / .742 to .767 / .407 to .433 at G 2 / 4 / 8; first over
  settled .99, .81 to .84, .44 to .47 against P 1.00, .86, .46. P2.3 PASS: L hit no blank trial anywhere; rings
  within .07 of the table (largest gap .035). P2.4 MISS in part: R2 - L on settled trials +.004, -.001, -.000 at
  k 5, 10, 25 (the main clause); R8 - L -.019, +.011, +.025: the slow ring's averaging advantage held at k 25 only,
  and the frozen table itself had R8 .89 against L .90 at k 5; the prose generalized from k 10 and 25. P2.5 MISS
  on one measure: the chair matched the G 8 ring on blank hits within .05 at every k and on S_all within .10 except
  k 2 (+.102), but followed changes faster: S_first .538 to .571 against .407 to .431, +.12 to +.15 at every k. By
  the re-lock law that is a ring at V 5.8 to 6.0, between gains 4 (3.69) and 8 (7.39). K4 did not fire (.129 at
  k 10, threshold .15). P2.6 MISS: the G 2 ring did not keep its turn at every trial. In 1 to 11% of seeds per
  condition it left winding 1 for about .2% of trials on average (mostly one trial, then back); in two shuffle
  seeds (k 5 and k 10) it lost it for most of the run; the G 4 ring lost it in 2 seeds of 1600, the G 8 ring never;
  98.3% of ring seeds in Test 1 and 98.7% in Test 3 kept winding 1 at every trial. After the fact: the cues are
  patterned, so a net cue opposed to the heading lowers the pattern's amplitude at every part at once; at G 2 the
  standing amplitude is .94 and an opposing patterned input of 0.43 or more leaves no positive fixed point
  (1.89 at G 4, above 3 at G 8), so the pattern collapses and re-forms along the cue, and the turn
  passes through 0 on the way. The unlearned net cue reaches .53 and the learned one .39, so the learned losses
  are transients of the same kind. A remaking along the cue, not a capture; the heading law still says where it
  lands, and the hit rates were as predicted.
P3.1 PASS: independent liars, L and R2: raw .805, corrected .907 and .906, gate .981 and .982; R8 .792 .845 .890;
  the gate's advantage over corrected weighting .074 to .076. P3.2 PASS: coalition, L and R2: raw .606 and .608,
  corrected .774 and .775, gate .989; R8 .631 .749 .888; the gate's advantage +.214 and +.215.
Kill conditions: K1 R2 - L settled at most +.004; K2 smallest ring S_blank at k 10 .614; K3 R8 S_first .433, R2
  .900; K4 .129; K5 +.214; K6 leader at most .127; K7 learned minus unlearned L at least +.585; K8 random minus
  unlearned at most +.003. None fired.

WHAT THE RUN SHOWS, read after the fact.
1. Learning carries the hit rate here, and the controls bite: unlearned .31, random .30, learned .90. The shuffle
   collapsed hits where the world is fast (.29 at k 2 and 5) and not where it is slow (.54 at k 25), as derived once
   the per-trial noise is in the formula.
2. The type of center sets the tempo at which persistence pays. The fast ring beats the list at every regime
   length (+.085 at k 2, +.16 at k 25); the slow ring loses to the list in a fast world (.477 against .680 at k 2)
   and draws level with the fast ring in a slow one. First-trial hits follow S_settled x P(Delta_0 <= Delta_max) at
   every gain and k. On settled trials the fast ring and the list decide alike within .005 at every k; what the slow
   ring adds there is averaging, .025 at k 25 and nothing at k 5. "The 0 buys persistence and smooth corrigibility,
   not the decision" held in a task where both have a price.
3. The chair is in effect a ring of intermediate gain: blank hits as G 8, re-lock as V about 5.9. Its memory loop
   has its own rate, so the Experiment 12 reading (a node its parts read back is a memory) holds and the band
   "like the G 8 ring" did not.
4. Dropping sources at chance is worth .07 against independent liars and .21 against a coalition; Experiment 12's
   raw credibility loses .10 and .17 against the corrected form. A coalition of liars is answered by a gate, not by
   weights: a boundary job, not a path job.
5. The weak ring's turn is not kept at every trial under patterned cues that oppose it, by a collapse and
   re-forming that the one-variable heading law cannot see. Experiment 12's winding claim was made with at most
   two sources and holds there; with four it needs the amplitude margin, which G 4 and 8 have and G 2 barely has.
"""
import argparse
import os
import sys
import time
import warnings
from math import pi
import numpy as np

warnings.filterwarnings('ignore', 'Mean of empty slice')   # wind1 is nan for the list and the node

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from architecture_experiment_12_v1 import N, STEPS, SIGMA, HIT, RES_NOISE, ETA, PSI, wrap, Organism, write_csv  # noqa: E402

TRIALS = 100
SKIP = 20
EPS = .3
P_BLANK = .25
Q = .9
LIARS = 3
CHANCE = 2 * HIT / (2 * pi)
KS = (2, 5, 10, 25)
ORGS = (('L', 0.0), ('C', 0.0), ('D', 1.5), ('R', 2.0), ('R', 4.0), ('R', 8.0))
LEARNS = ('true', 'none', 'shuffle', 'random')
FORMS = ('raw', 'corrected', 'gate')


def label(kind, p):
    return {'L': 'L', 'C': 'N chair', 'D': 'N leader'}.get(kind, f'R G{p:g}')


# ------------------------------------------------------------------ the world
class World13:
    """Regimes of k trials with the resource redrawn at each start; blank trials; one honest source and LIARS
    deceptive ones. Nothing here depends on the organism."""

    def __init__(self, rng, S, k, liars=LIARS, q=Q, coalition=False):
        self.S, self.k = S, k
        t = np.arange(TRIALS)
        reg = t // k
        star = rng.uniform(-pi, pi, (S, reg.max() + 1))[:, reg]
        self.res = wrap(star + RES_NOISE * rng.standard_normal((S, TRIALS)))
        self.cued = rng.random((S, TRIALS)) >= P_BLANK
        self.first = np.zeros(TRIALS, bool)
        self.first[::k] = True
        self.settled = ~self.first & ~np.roll(self.first, 1)
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
    corrected = np.maximum(0, (r - CHANCE) / (1 - CHANCE))
    if form == 'corrected':
        return corrected
    if form == 'gate':
        return (corrected >= .5).astype(float)
    raise ValueError(form)


def make13(kind, S, rng, p):
    if kind == 'R':
        return Organism('R', S, rng, G=p)
    if kind in ('C', 'D'):
        return Organism('N', S, rng, Gh=p)
    return Organism('L', S, rng)


def cue_input13(world, w, eps, t):
    """I_j = sum_s cued_t eps w_s exp(i(psi_j + phi_s,t)); zero on a blank trial."""
    amp = eps * w * world.cued[:, t][:, None]                                  # (S, ns)
    ph = np.exp(1j * (PSI[None, None, :] + world.dir[:, :, t][:, :, None]))   # (S, ns, N)
    return (amp[:, :, None] * ph).sum(1)


def run13(org, world, rng, eps=EPS, learn='true', form='corrected'):
    S = org.S
    ns = world.dir.shape[1]
    r = np.full((S, ns), .5)
    fb = world.feedback(rng, 'true' if learn == 'none' else learn)
    theta = np.full((S, TRIALS), np.nan)
    hit = np.zeros((S, TRIALS), bool)
    wind = np.zeros((S, TRIALS), int)
    absP = np.zeros((S, TRIALS))
    for t in range(TRIALS):
        w = weights(r, form)
        I = cue_input13(world, w, eps, t)
        for _ in range(STEPS):
            org.step(I, rng, sigma=SIGMA)
        th = org.heading()
        theta[:, t] = th
        hit[:, t] = np.abs(wrap(th - world.res[:, t])) <= HIT
        wind[:, t] = org.winding()
        absP[:, t] = org.absP()
        if learn != 'none':
            upd = world.cued[:, t][:, None]
            r = np.where(upd, r + ETA * (fb[:, :, t] - r), r)
    return dict(theta=theta, hit=hit, wind=wind, absP=absP, r=r)


def scores13(world, rec, kind):
    """Per-seed scores over trials SKIP..TRIALS-1."""
    sl = slice(SKIP, TRIALS)
    h = rec['hit'][:, sl]
    cued = world.cued[:, sl]
    first = np.broadcast_to(world.first[sl], h.shape)
    settled = np.broadcast_to(world.settled[sl], h.shape)

    def rate(mask):
        n = mask.sum(1)
        with np.errstate(invalid='ignore', divide='ignore'):
            return np.where(n > 0, (h & mask).sum(1) / np.maximum(n, 1), np.nan)

    return dict(S_all=h.mean(1), S_cued=rate(cued), S_blank=rate(~cued), S_first=rate(cued & first),
                S_settled=rate(cued & settled),
                wind1=(rec['wind'] == 1).mean(1) if kind == 'R' else np.full(h.shape[0], np.nan),
                r_honest=rec['r'][:, 0], r_liar=rec['r'][:, 1:].mean(1))


def one(S, seed, k, learn, kind, p, form='corrected', coalition=False, tag=()):
    world = World13(np.random.default_rng([seed, k, 1, int(coalition)]), S, k, coalition=coalition)
    rng = np.random.default_rng([seed, k, 2, LEARNS.index(learn), ORGS.index((kind, p)), FORMS.index(form), int(coalition)])
    org = make13(kind, S, rng, p)
    t0 = time.time()
    rec = run13(org, world, rng, learn=learn, form=form)
    sc = scores13(world, rec, kind)
    base = dict(k=k, learn=learn, org=label(kind, p), form=form, world='coalition' if coalition else 'independent')
    seeds = [dict(seed=i, **base, **{m: float(v[i]) for m, v in sc.items()}) for i in range(S)]
    summary = dict(**base, **{m: float(np.nanmean(v)) for m, v in sc.items()})
    curve = dict(**base, **{f't{t + 1}': float(rec['hit'][:, t].mean()) for t in range(TRIALS)})
    print(f"  k {k:>2} {learn:>7} {label(kind, p):>8} {form:>9} {'coal' if coalition else 'indep'}: "
          + " ".join(f"{m} {summary[m]:.3f}" for m in ('S_all', 'S_cued', 'S_blank', 'S_first', 'S_settled', 'r_honest', 'r_liar'))
          + f"  [{time.time() - t0:.0f} s]", flush=True)
    return seeds, summary, curve


FROZEN_SMOKE = {'L': dict(S_all=.68, S_cued=.90, S_blank=0.0, S_first=.90, S_settled=.90),
                'R G2': dict(S_all=.84, S_cued=.90, S_blank=.64, S_first=.89, S_settled=.90)}


def smoke(S, out, seed):
    """Correspondence check: the list and the G = 2 ring at k = 10, learned, against the reduced model's row."""
    print("smoke: full organisms against the reduced model, k 10, learned, corrected weights", flush=True)
    rows = []
    for kind, p in (('L', 0.0), ('R', 2.0)):
        seeds, summary, _ = one(S, seed, 10, 'true', kind, p)
        fr = FROZEN_SMOKE[label(kind, p)]
        for m, v in fr.items():
            d = summary[m] - v
            flag = 'ok' if abs(d) <= .05 else 'OFF'
            print(f"    {label(kind, p):>5} {m:>9}: full {summary[m]:.3f} reduced {v:.2f} diff {d:+.3f} {flag}", flush=True)
            rows.append(dict(org=label(kind, p), measure=m, full=summary[m], reduced=v, diff=d))
    write_csv(out, 'smoke', rows)


def t1(S, out, seed):
    print("Test 1: six organisms x four regime lengths x four learning conditions, corrected weights", flush=True)
    seeds_all, summ, curves = [], [], []
    for k in KS:
        for learn in LEARNS:
            for kind, p in ORGS:
                seeds, summary, curve = one(S, seed, k, learn, kind, p)
                seeds_all += seeds
                summ.append(summary)
                curves.append(curve)
        write_csv(out, 't1_seeds', seeds_all)
        write_csv(out, 't1_summary', summ)
        write_csv(out, 't1_curves', curves)


def t3(S, out, seed):
    print("Test 3: weight forms against independent liars and a coalition, k 10, learned", flush=True)
    seeds_all, summ, curves = [], [], []
    for coalition in (False, True):
        for form in FORMS:
            for kind, p in (('L', 0.0), ('R', 2.0), ('R', 4.0), ('R', 8.0)):
                seeds, summary, curve = one(S, seed, 10, 'true', kind, p, form=form, coalition=coalition)
                seeds_all += seeds
                summ.append(summary)
                curves.append(curve)
            write_csv(out, 't3_seeds', seeds_all)
            write_csv(out, 't3_summary', summ)
            write_csv(out, 't3_curves', curves)


TESTS = dict(smoke=smoke, t1=t1, t3=t3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tests', nargs='*', default=['smoke', 't1', 't3'])
    ap.add_argument('--seeds', type=int, default=100)
    ap.add_argument('--seed', type=int, default=13)
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    out = a.out or os.path.join(HERE, 'architecture_experiment_13_results')
    os.makedirs(out, exist_ok=True)
    for name in a.tests:
        t0 = time.time()
        TESTS[name](a.seeds, out, a.seed)
        print(f"  [{name} done in {time.time() - t0:.0f} s]", flush=True)


if __name__ == '__main__':
    main()
