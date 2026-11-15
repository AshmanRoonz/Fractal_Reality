"""Architecture of Wholeness, Experiment 12: one organism with a 0 at its center.

Created: 2026-11-06. Last updated: 2026-11-07. Version: 1.0 (results appended 2026-11-07).
Pre-registration, frozen before this file was written:
    plans/architecture_experiment_12_one_organism_2026_11_06.md
Run:    python -I architecture_experiment_12_v1.py [smoke t2 t1a t1b t1c t3] [--seeds 100] [--out DIR]
Needs numpy only. Writes one CSV per test to --out (default: architecture_experiment_12_results beside this file).

WHAT IS BUILT. Three organisms from the same 16 parts, inputs, boundary and learning rule, differing only in
the center: L, a list (center = the parts' mean, read instantly); N, a node (a hub of 16 bistable cells that
reads the parts' population vector and that the parts read back, self-gain Gh from chair to leader); R, a ring
(parts coupled in a closed loop carrying one turn; the center is the 0 the turn forces; the decision is the
loop's orientation). Law: z' = -z + lim(G W z + I) + noise, lim(w) = tanh|w| w/|w|, dt .05, part noise .05.
Cues enter as I_j = eps w_s exp(i(psi_j + phi_s)). Boundary: common-mode rejection of the input. Path: one
credibility weight per source, w <- w + .2 (hit - w), graded on the revealed resource, the same in every
organism. Task: 70 trials of 40 time units; honest source every trial, deceptive source (random direction) on
half; hit if the heading at the trial's end is within 20 degrees of the resource; the resource jumps 120
degrees at trial 31; trials 61 to 70 are blank.

ONE CLARIFICATION OF THE PRE-REGISTRATION, made before any run. Its section 2 wrote the hub's broadcast to the
parts as kappa_out * sum_k max(y_k, 0) exp(i psi_k), which is the same number for every part and would be a
uniform pull, cancelled by the readout and by the boundary. "The parts read the hub" needs the pattern's
twist: I_j gains kappa_out * Y * exp(i psi_j), Y = sum_k max(y_k, 0) exp(i psi_k). That is what is coded.
In Test 3 the contact is coded in the share form of wholeness_nested_v1.py (a port reads a share t = .5 from
its partner and 1 - t from its own ring), and the shared field as a share .5 of the mean of all sub-ring parts.

FROZEN PREDICTIONS (D derived, C carried from the wholeness tests, G guess), from the pre-registration.
Test 1a, uniform pull ramped 0 to 3 over trials 15 to 30.
  P1a.1 (C) R, boundary off, G 4: the turn ends at |u| in [.15, .6], centered on .3.
  P1a.2 (D) R, boundary on: no capture up to 3.
  P1a.3 (D) N and L: no capture by a uniform pull at any size.
  P1a.4 (D) A patterned false cue affects all three organisms alike (hit rates within .1 at every trial).
Test 1b, targeted input.
  P1b.1 (D) N captured by a hub input above I_c = Gh y* - atanh(y*), y* = sqrt(1 - 1/Gh): .21 at 1.5, .53 at 2,
            plus about beta y_on of inhibition.
  P1b.2 (C) R and L: a pull on one part moves the heading at most 22.5 degrees and cannot end the turn.
Test 1c, k parts removed.
  P1c.1 (D) R without reconnection: any removal ends the turn.
  P1c.2 (C) R with reconnection: the turn survives up to k = 9.
  P1c.3 (D) N survives every part removal while the hub lives and loses its heading when the hub goes.
Test 2, the corner.
  P2.1 (D) R holds its heading over the ten blank trials: drift within 30 degrees in at least 90 of 100 seeds
           (random walk, about 14 degrees over the blank at sigma .05).
  P2.2 (D) N leader (Gh >= 1.5) holds within 5 degrees; N chair (Gh <= 1) and L have no heading in the blank.
  P2.3 (D) R re-locks in 2.29 V/eps time units, V = G r cos(2 pi/16): T = 1, 1, 2 at eps .3 and 1, 2, 3 at
           eps .15 for G = 2, 4, 8.
  P2.4 (D) N leader: T is a step, 1 trial or never. N chair and L: T = 1.
  P2.5 (D) Corner (S >= .9, T <= 2, persistence): R passes 5 of 6 cells, failing only (G 8, eps .15).
  P2.6 (G) N passes at no more than one Gh per eps, and not the same Gh at both eps.
  P2.7 (D) L never passes.
Test 3, nesting.
  P3.1 (C) Contact: all four sub-rings and the top ring keep winding 1 in >= 95 of 100 seeds; each S >= .9.
  P3.2 (C) Shared field: median <= 2 of 4 sub-rings keep winding 1; all four in <= 10 of 100 seeds; survivors'
           headings within 20 degrees of each other on blank trials.
  P3.3 (G) Shared false cue: error correlation across sub-rings < .3 (contact) against > .7 (shared);
           P(all four miss) <= .1 against >= .5.
Controls.
  PC.1 (D) Memory reset at the jump: T rises by at least 3 trials in every organism.
  PC.2 (G) Shuffled feedback: honest and deceptive weights within .1; S < .4 in every organism.
  PC.3 (D) Coin flip hits .111; (G) after learning every organism but an untuned leader is at >= 8x.
Against the framework: R captured with the boundary on; R drifting > 30 degrees in > 10 seeds; R's re-lock
off 2.29 V/eps by > 50%; N passing the corner at >= 3 of 5 Gh at both eps; contact sub-rings losing turns in
> 20 seeds; shared-field sub-rings all keeping theirs in > 50.

RESULTS (run 2026-11-07, 100 seeds, --seed 12; CSVs and run_2026_11_07.log in architecture_experiment_12_results/).
Tally: 22 frozen predictions, 11 PASS, 11 MISS, of which 5 are partial (the main clause held and a part failed).
None of the six conditions listed against the framework occurred. The summary table's T_median column was
first written as inf whenever any seed never re-locked; it was regenerated from the seed table the same day
and the code line corrected (trivial fix, version unchanged).

Smoke. Lock time measured over derived: 1.04, 1.07, 1.01, 1.03, 1.01, 1.01 for (G, eps) = (2,.15), (2,.3),
(4,.15), (4,.3), (8,.15), (8,.3). The derivation and the code agree.

Test 2, base runs. S = hit rate over trials 15 to 30; T = first trial after the jump that begins three hits
(median over seeds, with the share of seeds at T <= 2); drift = median heading drift over the blank, with the
share within 30 degrees.
  R  G2  eps.15: S .988  T 1 (98%)   drift 10.4 deg (98%)   corner PASS
  R  G2  eps.3 : S .988  T 1 (98%)   drift 10.4 (98%)       PASS
  R  G4  eps.15: S .994  T 2 (96%)   drift 10.1 (99%)       PASS
  R  G4  eps.3 : S .988  T 1 (98%)   drift 9.9 (99%)        PASS
  R  G8  eps.15: S .989  T 3 (2%)    drift 10.0 (100%)      fail, as derived
  R  G8  eps.3 : S .994  T 2 (96%)   drift 10.0 (99%)       PASS
  N  Gh0  eps.15: S .996  T 3 (30%)  drift 3.9 (100%)       fail
  N  Gh0  eps.3 : S .994  T 2 (97%)  drift 4.4 (100%)       PASS
  N  Gh.5 eps.15: S .489  never 99%                          fail
  N  Gh.5 eps.3 : S .824  T 8 (0%), never 3%                 fail
  N  Gh1, 1.5, 2, both eps: S .48, never 97 to 98%, drift 0.0 to 0.7 deg   fail
  L  both eps: S .986  T 1 (98%)  no heading in the blank    fail
P2.1 PASS. P2.2 PASS for the leader (drift 0.1 deg) and for L (no heading); MISS for the chair, which holds
its heading through the blank (drift 4 deg, |P| 1.00 on every blank trial). After the fact: the parts read
the hub back at kappa_out .5 and the hub reads the parts, and with G_p 4 that loop sustains itself with no
input. A node that its parts read back is a memory whatever its own gain. P2.3 PASS, all six T values as
derived. P2.4 PASS in form for the leader (a step, landing on never at every Gh >= 1, and at Gh .5 for eps
.15); MISS for the chair (T 3 and 2, not 1: the same loop gives it inertia). P2.5 PASS exactly: 5 of 6, with
(8, .15) the one failure. P2.6 PASS: one Gh (0) passes at eps .3 and none at eps .15. P2.7 PASS.
The leader at Gh >= 1 commits in the first trials and never moves again; S .48 is the share of seeds where it
happened to commit within reach of the resource. Incorrigible, as the types-of-center table says of a leader.

Controls.
PC.1 MISS on size: a memory reset at the jump raises the median T by 1 to 2 trials in R, N chair and L (R G2:
1 to 3; R G4 eps .15: 2 to 3; R G8 eps .15: 3 to 5; N chair eps .3: 2 to 3; L: 1 to 3), not by 3, and changes
nothing for the stuck leaders. Learning does part of the work of re-locking, less than predicted.
PC.2 MISS twice: under shuffled feedback the honest and deceptive weights still separate by .31, not within
.1, and S falls only to .87 to .95, not below .4, while T rises (R G4 eps .15: 2 to 4; R G8 eps .15: 3 to 8;
N chair eps .15: 3 to 6). The control is weak by construction: the honest source announces the resource, so
grading it against another trial's resource in the same environment still finds it right most of the time.
The hit rate in a stable environment is robust to degraded learning; the speed of re-locking is not.
PC.3 PASS: coin flip .113 (analytic .111); R .988, N chair .994 and L .986 are 8.7 to 8.9 times it; the stuck
leader at .48 is 4.3 times.

Test 1a. P1a.1 MISS: with the boundary off, R lost its turn at |u| .71 (10th to 90th percentile .68 to .73),
above the band [.15, .6]. After the fact: the earlier ring had no cue holding its pattern; here the honest cue
(.3 at weight 1) holds the twist against the pull and raises the threshold. P1a.2 PASS: boundary on, no capture
up to 3, hits .99 and |P| 1.00 throughout. P1a.3 PASS for N (the chair hits .99 in every third of the ramp,
|P| down to .29 at |u| 2 to 3 with the heading still right); MISS for L at the top of the ramp (hits .98, .98,
.78 as |P| fell to .06: the parts' saturation crowds out the pattern). The leader sat at .48 throughout,
untouched and useless. P1a.4 MISS by a hair: the three organisms' hit rates differ by .10 and .11 on trials 1
and 2 (R .44 and .59, N .54 and .70, L .54 and .62) and by less than .1 from trial 3 on; R starts from a random
heading and turns at eps w/V with w .5, so it lags for two trials.

Test 1b. P1b.1 PASS on the order, MISS on the numbers: the chair follows a hub input already in the first
third of the ramp (|u| < 1: 66%, then 100%); Gh 1.5 follows only in the last third (|u| 2 to 3: 86%); Gh 2 not
at all up to 3 (7%). The threshold rises with Gh, but it is about 2 at Gh 1.5 and above 3 at Gh 2, not .21 and
.53: the cell formula ignores the drive the hub feeds back to itself through the parts. P1b.2 PASS: a pull on
one part of R moved the heading by a median 21.5 deg at |u| 2 to 3 (hits down to .37) and never ended the turn
(winding 1 in 100%); L moved 6.9 deg (hits .98). The list is the harder of the two to move by one part.

Test 1c. P1c.1 PASS where the measure can speak: without reconnection, one part removed in the blank left the
turn in 0 of 100 seeds by trial 70, two parts in 4; with 4, 6 or 9 removed the ring is in fragments and the
alive-order winding is an integer by construction (1 in 32 to 47%), so it cannot say. P1c.2 PASS to k = 6
(winding 1 in 100% at trial 70, drift within 30 deg in 93 to 99%), MISS at k = 9: 61% (blank) and 66% (cues),
seven parts left unevenly spaced. P1c.3 PASS: N keeps its parts' pattern and its heading (drift 0.2 deg)
through every removal while the hub lives (97% at k = 9) and has no heading once the hub is removed. L is
unaffected by any removal (hits 1.00 at k = 9), so "degrades in proportion" was not borne out. The leader's
hits in trials 50 to 60 were .01 in every injury run: still stuck from the jump.

Test 3. P3.1 MISS on the counts, PASS on performance: under contact all four sub-rings kept their turn in 92
of 100 seeds (96 before the jump, 92 after), not 95, and the top ring kept its turn in 62, not 95, losing it
over the first 30 trials (97% at trial 1, 69% by trial 10, 62% from trial 31) as the four sub-rings were
pulled to four unrelated headings and their ports showed the top ring four unrelated phases. S per sub-ring
.937, lowest .909. P3.2 PASS: in the shared field no sub-ring kept its turn (0 of 4 in every seed, so the
survivors' clause does not arise), and the same with the contacts added. P3.3 MISS: the broadcast false cue
produced no correlated failure in the shared field (error correlation .07 against -.02 under contact; all four
missing on broadcast trials .08 against .07) and no loss of hit rate (S .944 against .937 under contact). After
the fact: the shared field couples the parts' mean, the common mode, while the heading lives in the first mode,
which the shared mean does not touch. Losing the 0 cost the sub-rings nothing on this task.

WHAT THE RUN SHOWS, read after the fact.
1. The ring's heading law is exact to a few percent and the corner follows from it: the 0-centered organism
holds without input and follows at the derived rate, across gains, and fails exactly where the derivation
said (gain 8, weak cue). The node reaches the corner in one cell, and only because its parts-hub loop is a
memory; above Gh 1 it commits once and never moves.
2. The turn is not needed to decide. L has no turn and hits .986; the shared-field colonies lose every turn
and hit .944. In this task the 0 buys persistence without input and smooth corrigibility, and carries one
specific fragility, to a uniform pull, which the boundary removes exactly. "Fragile to anything shared" held
for the turn (0 of 4 kept) and not for the behaviour.
3. Learning carried the hit rate less than expected and the re-lock speed more: the shuffle control barely
touched S and doubled T. The controls were too weak for the hit rate, and a harder task is needed before
"learning does the work" can be claimed or denied.
4. The clarification of the hub's broadcast (the twist) turned the chair into a loop with memory. That is a
result about nodes, not a defect of the design: a node that its parts read back is never only a reader.
"""
import argparse
import csv
import os
import sys
import time
from math import pi, sqrt, tanh, atanh

import numpy as np

N = 16
DT = .05
TAU = 40.0
STEPS = int(round(TAU / DT))
SIGMA = .05
TRIALS = 70
JUMP = 30
BLANK = 60
HIT = np.deg2rad(20)
RES_NOISE = np.deg2rad(10)
ETA = .2
PSI = 2 * pi * np.arange(N) / N
EPSI = np.exp(1j * PSI)
CEPSI = np.conj(EPSI)
BETA, K_IN, K_OUT, G_P = .5, 1.0, .5, 4.0
RAMP0, RAMP1 = 14, 30          # ramp runs over trials 15 to 30 (indices 14..29)
RAMP_MAX = 3.0


def wrap(a):
    return (a + pi) % (2 * pi) - pi


def lim(w):
    a = np.abs(w)
    return np.tanh(a) * w / np.maximum(a, 1e-12)


def cnoise(rng, shape):
    return rng.standard_normal(shape) + 1j * rng.standard_normal(shape)


def rest(G, n=N):
    r = 1.0
    for _ in range(10000):
        r = tanh(G * r * np.cos(2 * pi / n))
    return r


def V_of(G):
    return G * rest(G) * np.cos(2 * pi / N)


def circ_sd(th, axis=-1):
    R = np.abs(np.exp(1j * th).mean(axis))
    return np.sqrt(np.maximum(-2 * np.log(np.maximum(R, 1e-12)), 0))


# ---------------------------------------------------------------- the world
class World:
    """Resource directions, announcements and each source's hits, drawn once per seed. Nothing here depends
    on the organism. Source 0 is honest (announces the resource every cue trial), source 1 is deceptive
    (a uniformly random direction on half the cue trials)."""

    def __init__(self, rng, S, phiA=None):
        self.S = S
        phiA = np.zeros(S) if phiA is None else np.asarray(phiA, float)
        t = np.arange(TRIALS)
        star = np.where(t[None, :] < JUMP, phiA[:, None], phiA[:, None] + 2 * pi / 3)
        self.res = wrap(star + RES_NOISE * rng.standard_normal((S, TRIALS)))
        self.cue = t < BLANK
        self.ann = np.zeros((S, 2, TRIALS), bool)
        self.dir = np.zeros((S, 2, TRIALS))
        self.ann[:, 0] = self.cue[None, :]
        self.dir[:, 0] = self.res
        self.ann[:, 1] = (rng.random((S, TRIALS)) < .5) & self.cue[None, :]
        self.dir[:, 1] = rng.uniform(-pi, pi, (S, TRIALS))
        self.hit = np.abs(wrap(self.dir - self.res[:, None, :])) <= HIT

    def shuffled(self, rng):
        """Shuffled feedback: a source is graded at trial t against the resource of another cue trial."""
        w = World.__new__(World)
        w.__dict__.update(self.__dict__)
        perm = np.array([rng.permutation(BLANK) for _ in range(self.S)])
        res_p = np.take_along_axis(self.res[:, :BLANK], perm, 1)
        w.hit = self.hit.copy()
        w.hit[:, :, :BLANK] = np.abs(wrap(self.dir[:, :, :BLANK] - res_p[:, None, :])) <= HIT
        return w


# ------------------------------------------------------------- one organism
class Organism:
    def __init__(self, kind, S, rng, G=4.0, Gh=1.5, boundary=True, reconnect=True):
        self.kind, self.S, self.G, self.Gh = kind, S, float(G), float(Gh)
        self.boundary, self.reconnect = boundary, reconnect
        self.rows = np.arange(S)[:, None]
        self.alive = np.ones((S, N), bool)
        base = np.arange(N)
        self.left = np.broadcast_to((base - 1) % N, (S, N)).copy()
        self.right = np.broadcast_to((base + 1) % N, (S, N)).copy()
        self.right_alive = self.right.copy()
        if kind == 'R':
            th0 = rng.uniform(-pi, pi, (S, 1))
            self.z = rest(G) * np.exp(1j * (PSI[None, :] + th0))
        else:
            self.z = np.zeros((S, N), complex)
        self.y = np.zeros((S, N))
        self.hub_alive = np.ones(S, bool)
        self.w = np.full((S, 2), .5)

    # readings
    def reading(self):
        zl = self.z[self.rows, self.left]
        zr = self.z[self.rows, self.right]
        return .5 * (zl + zr) * self.alive

    def popvec(self):
        return (self.z * CEPSI[None, :]).sum(1) / np.maximum(self.alive.sum(1), 1)

    def hub_vec(self):
        return (np.maximum(self.y, 0) * EPSI[None, :]).sum(1)

    def step(self, I, rng, hub_pull=None, sigma=SIGMA):
        if self.boundary:
            I = I - I.mean(1, keepdims=True)
        if self.kind == 'R':
            v = self.G * self.reading() + I
        elif self.kind == 'N':
            Y = self.hub_vec()
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
            if hub_pull is not None:
                x = x + hub_pull
            inhib = BETA * (self.y.sum(1, keepdims=True) - self.y)
            y = self.y + DT * (-self.y + np.tanh(self.Gh * self.y - inhib + x))
            self.y = y * self.hub_alive[:, None]

    # readouts
    def heading(self):
        if self.kind == 'N':
            Y = self.hub_vec()
            return np.where(np.abs(Y) > 1e-9, np.angle(Y), np.nan)
        P = self.popvec()
        if self.kind == 'L':
            return np.where(np.abs(P) >= .05, np.angle(P), np.nan)
        return np.angle(P)

    def absP(self):
        return np.abs(self.popvec())

    def winding(self):
        a = np.angle(self.z)
        d = wrap(a[self.rows, self.right_alive] - a) * self.alive
        return np.rint(d.sum(1) / (2 * pi)).astype(int)

    def c1(self):
        num = np.abs((self.z * CEPSI[None, :]).sum(1))
        return num / np.maximum(np.abs(self.z).sum(1), 1e-12)

    def injure(self, k, rng, hub=False):
        """Remove k parts at random per seed (or the hub). With reconnect, the neighbours of a removed part
        connect to each other; without, the ring is left open with the dead parts reading as 0."""
        if hub:
            self.hub_alive[:] = False
            self.y[:] = 0
            return
        for s in range(self.S):
            idx = rng.choice(N, k, replace=False)
            self.alive[s, idx] = False
        self.z = self.z * self.alive
        right_alive = self.right.copy()
        left_alive = self.left.copy()
        for s in range(self.S):
            al = np.flatnonzero(self.alive[s])
            nxt = np.roll(al, -1)
            prv = np.roll(al, 1)
            right_alive[s, al] = nxt
            left_alive[s, al] = prv
        self.right_alive = right_alive
        if self.reconnect:
            self.left, self.right = left_alive, right_alive


def cue_input(world, w, eps, t, psi=PSI):
    """I_j = sum_s ann_s eps w_s exp(i(psi_j + phi_s)) for the trial t. w: (S, 2)."""
    S = world.S
    I = np.zeros((S, psi.size), complex)
    for s in range(2):
        amp = eps * w[:, s] * world.ann[:, s, t]
        I += amp[:, None] * np.exp(1j * (psi[None, :] + world.dir[:, s, t][:, None]))
    return I


def run(org, world, rng, eps, reset_at_jump=False, ramp=None, injury=None, eta=ETA, sigma=SIGMA):
    """One organism through the 70 trials. ramp: ('uniform' | 'part' | 'hub', phi_u (S,)) ramps |u| from 0 to
    RAMP_MAX over trials RAMP0..RAMP1-1. injury: dict(at=trial index, k=parts, hub=bool)."""
    S = org.S
    rec = dict(theta=np.full((S, TRIALS), np.nan), hit=np.zeros((S, TRIALS), bool), wind=np.zeros((S, TRIALS), int),
               c1=np.zeros((S, TRIALS)), absP=np.zeros((S, TRIALS)), w=np.zeros((S, TRIALS, 2)),
               capture_u=np.full(S, np.nan), err_u=np.full((S, TRIALS), np.nan))
    for t in range(TRIALS):
        if reset_at_jump and t == JUMP:
            org.w[:] = .5
        if injury is not None and t == injury['at']:
            org.injure(injury.get('k', 0), rng, hub=injury.get('hub', False))
        I = cue_input(world, org.w, eps, t)
        ramping = ramp is not None and RAMP0 <= t < RAMP1
        for step in range(STEPS):
            hub_pull = None
            Ist = I
            if ramping:
                u = RAMP_MAX * ((t - RAMP0) * STEPS + step) / ((RAMP1 - RAMP0) * STEPS)
                kind, phi_u = ramp
                if kind == 'uniform':
                    Ist = I + (u * np.exp(1j * phi_u))[:, None]
                elif kind == 'part':
                    Ist = I.copy()
                    Ist[:, 0] += u * np.exp(1j * phi_u)
                elif kind == 'hub':
                    hub_pull = u * np.cos(phi_u[:, None] - PSI[None, :])
            org.step(Ist, rng, hub_pull=hub_pull, sigma=sigma)
            if ramping and org.kind == 'R' and step % 40 == 0:
                lost = (org.winding() != 1) | (org.c1() < .2)
                fresh = lost & np.isnan(rec['capture_u'])
                rec['capture_u'][fresh] = u
        th = org.heading()
        rec['theta'][:, t] = th
        rec['absP'][:, t] = org.absP()
        rec['c1'][:, t] = org.c1()
        rec['wind'][:, t] = org.winding()
        if world.cue[t]:
            rec['hit'][:, t] = np.abs(wrap(th - world.res[:, t])) <= HIT
        if ramp is not None:
            rec['err_u'][:, t] = np.abs(wrap(th - ramp[1]))
        for s in range(2):
            upd = world.ann[:, s, t]
            org.w[:, s] = np.where(upd, org.w[:, s] + eta * (world.hit[:, s, t] - org.w[:, s]), org.w[:, s])
        rec['w'][:, t] = org.w
    return rec


def summarize(rec):
    """S: hit rate over trials 15 to 30. T: first trial after the jump that begins three consecutive hits,
    counted from the jump (inf if none). drift: heading drift over the blank (nan if undefined)."""
    hit = rec['hit']
    S_ = hit[:, 14:30].mean(1)
    T = np.full(hit.shape[0], np.inf)
    for s in range(hit.shape[0]):
        for t in range(JUMP, BLANK - 2):
            if hit[s, t] and hit[s, t + 1] and hit[s, t + 2]:
                T[s] = t - JUMP + 1
                break
    th0, th1 = rec['theta'][:, BLANK - 1], rec['theta'][:, TRIALS - 1]
    drift = np.abs(wrap(th1 - th0))
    return S_, T, drift


def tdeg(x):
    return np.rad2deg(x)


# ------------------------------------------------------------------- tests
def smoke(S, out, rng_seed):
    """Lock law: R with one honest cue, no noise, no deceptive source, weight 1. Time for a 120 degree jump
    to come within 20 degrees, against 2.29 V/eps."""
    print("SMOKE: lock law, R, no noise, cue weight 1")
    rows = []
    for G in (2, 4, 8):
        for eps in (.15, .3):
            rng = np.random.default_rng(rng_seed)
            org = Organism('R', 1, rng, G=G)
            org.z = rest(G) * np.exp(1j * PSI[None, :])
            I0 = eps * np.exp(1j * PSI[None, :])
            for _ in range(STEPS):
                org.step(I0, rng, sigma=0)
            I1 = eps * np.exp(1j * (PSI[None, :] + 2 * pi / 3))
            t_lock = np.nan
            for step in range(20 * STEPS):
                org.step(I1, rng, sigma=0)
                if abs(wrap(org.heading()[0] - 2 * pi / 3)) <= HIT:
                    t_lock = (step + 1) * DT
                    break
            pred = 2.29 * V_of(G) / eps
            rows.append(dict(G=G, eps=eps, V=V_of(G), t_lock=t_lock, t_pred=pred, ratio=t_lock / pred))
            print(f"  G {G} eps {eps}: V {V_of(G):.2f}  measured {t_lock:.1f}  derived {pred:.1f}  ratio {t_lock / pred:.2f}")
    write_csv(out, 'smoke', rows)


def corner_cells():
    cells = [('R', G, eps) for G in (2, 4, 8) for eps in (.15, .3)]
    cells += [('N', Gh, eps) for Gh in (0, .5, 1, 1.5, 2) for eps in (.15, .3)]
    cells += [('L', 0, eps) for eps in (.15, .3)]
    return cells


def make(kind, S, rng, p, **kw):
    if kind == 'R':
        return Organism('R', S, rng, G=p, **kw)
    if kind == 'N':
        return Organism('N', S, rng, Gh=p, **kw)
    return Organism('L', S, rng, **kw)


def t2(S, out, rng_seed):
    print("TEST 2: the corner, with the controls")
    rows, table = [], []
    for kind, p, eps in corner_cells():
        for ctrl in ('base', 'reset', 'shuffle'):
            rng = np.random.default_rng([rng_seed, 2])
            world = World(np.random.default_rng([rng_seed, 1]), S)
            if ctrl == 'shuffle':
                world = world.shuffled(np.random.default_rng([rng_seed, 3]))
            org = make(kind, S, rng, p)
            rec = run(org, world, rng, eps, reset_at_jump=(ctrl == 'reset'))
            S_, T, drift = summarize(rec)
            wgap = rec['w'][:, BLANK - 1, 0] - rec['w'][:, BLANK - 1, 1]
            defined = ~np.isnan(drift)
            pers_ok = np.mean(defined & (drift <= np.deg2rad(30)))
            Tfin = T[np.isfinite(T)]
            res = dict(kind=kind, p=p, eps=eps, ctrl=ctrl, S_mean=S_.mean(), S_ge09=np.mean(S_ >= .9),
                       T_median=np.median(T),
                       T_mean_finite=(Tfin.mean() if Tfin.size else np.nan), T_le2=np.mean(T <= 2),
                       T_never=np.mean(~np.isfinite(T)), pers_defined=defined.mean(), pers_ok=pers_ok,
                       drift_med_deg=(np.median(tdeg(drift[defined])) if defined.any() else np.nan),
                       wind1_end=np.mean(rec['wind'][:, TRIALS - 1] == 1), wgap=wgap.mean(),
                       hit_vs_coin=S_.mean() / (40 / 360))
            table.append(res)
            print(f"  {kind} p={p:<4} eps={eps:<4} {ctrl:8s} S={res['S_mean']:.3f} T_med={res['T_median']:<5} "
                  f"T<=2={res['T_le2']:.2f} never={res['T_never']:.2f} pers_ok={pers_ok:.2f} "
                  f"(defined {defined.mean():.2f}, drift med {res['drift_med_deg']:.1f} deg) w1end={res['wind1_end']:.2f} "
                  f"wgap={wgap.mean():.2f}", flush=True)
            for s in range(S):
                rows.append(dict(kind=kind, p=p, eps=eps, ctrl=ctrl, seed=s, S=S_[s], T=T[s],
                                 drift_deg=tdeg(drift[s]), wind_end=rec['wind'][s, TRIALS - 1],
                                 w_honest=rec['w'][s, BLANK - 1, 0], w_decept=rec['w'][s, BLANK - 1, 1]))
    write_csv(out, 't2_seeds', rows)
    write_csv(out, 't2_summary', table)
    # the corner verdicts, base runs
    print("  Corner (base): pass = S_mean >= .9, T_median <= 2, pers_ok >= .9")
    for r in table:
        if r['ctrl'] != 'base':
            continue
        ok = r['S_mean'] >= .9 and r['T_median'] <= 2 and r['pers_ok'] >= .9
        print(f"    {r['kind']} p={r['p']:<4} eps={r['eps']:<4} -> {'PASS' if ok else 'fail'}")
    coin = np.abs(wrap(np.random.default_rng(rng_seed).uniform(-pi, pi, (S, 60)) - 0)) <= HIT
    print(f"  Coin flip hit rate (simulated): {coin.mean():.3f}; analytic {40 / 360:.3f}")


def t1a(S, out, rng_seed):
    print("TEST 1a: uniform pull ramped 0..3 over trials 15..30")
    rows, table = [], []
    conds = [('R', 4, False), ('R', 4, True), ('N', 0, False), ('N', 1.5, False), ('L', 0, False)]
    eps = .3
    for kind, p, boundary in conds:
        rng = np.random.default_rng([rng_seed, 2])
        world = World(np.random.default_rng([rng_seed, 1]), S)
        phi_u = rng.uniform(-pi, pi, S)
        org = make(kind, S, rng, p, boundary=boundary)
        rec = run(org, world, rng, eps, ramp=('uniform', phi_u))
        cap = rec['capture_u']
        hit = rec['hit']
        thirds = [hit[:, 14:19].mean(), hit[:, 19:24].mean(), hit[:, 24:30].mean()]
        absP = [rec['absP'][:, 14:19].mean(), rec['absP'][:, 19:24].mean(), rec['absP'][:, 24:30].mean()]
        res = dict(kind=kind, p=p, boundary=boundary, captured=np.mean(~np.isnan(cap)),
                   cap_u_median=(np.nanmedian(cap) if np.isfinite(cap).any() else np.nan),
                   cap_u_q10=(np.nanpercentile(cap, 10) if np.isfinite(cap).any() else np.nan),
                   cap_u_q90=(np.nanpercentile(cap, 90) if np.isfinite(cap).any() else np.nan),
                   hit_u0_1=thirds[0], hit_u1_2=thirds[1], hit_u2_3=thirds[2],
                   absP_u0_1=absP[0], absP_u1_2=absP[1], absP_u2_3=absP[2],
                   hit_after=hit[:, 30:60].mean(), wind1_t30=np.mean(rec['wind'][:, 29] == 1))
        table.append(res)
        print(f"  {kind} p={p} boundary={boundary}: captured {res['captured']:.2f} at |u| median {res['cap_u_median']:.2f} "
              f"[{res['cap_u_q10']:.2f},{res['cap_u_q90']:.2f}]; hits by |u| third {thirds[0]:.2f} {thirds[1]:.2f} {thirds[2]:.2f}; "
              f"|P| {absP[0]:.2f} {absP[1]:.2f} {absP[2]:.2f}; winding 1 at trial 30: {res['wind1_t30']:.2f}", flush=True)
        for s in range(S):
            rows.append(dict(kind=kind, p=p, boundary=boundary, seed=s, capture_u=cap[s],
                             hits_ramp=hit[s, 14:30].mean(), wind_t30=rec['wind'][s, 29]))
    write_csv(out, 't1a_seeds', rows)
    write_csv(out, 't1a_summary', table)


def t1b(S, out, rng_seed):
    print("TEST 1b: targeted input ramped 0..3 (hub cells for N; one part for R and L), phi_u = honest + 90 deg")
    rows, table = [], []
    conds = [('N', 0, 'hub'), ('N', 1.5, 'hub'), ('N', 2, 'hub'), ('R', 4, 'part'), ('L', 0, 'part')]
    eps = .3
    for kind, p, kindu in conds:
        rng = np.random.default_rng([rng_seed, 2])
        world = World(np.random.default_rng([rng_seed, 1]), S)
        phi_u = np.full(S, pi / 2)
        org = make(kind, S, rng, p)
        rec = run(org, world, rng, eps, ramp=(kindu, phi_u))
        err_u = rec['err_u']
        hit = rec['hit']
        capt = [np.mean(err_u[:, 14:19] <= HIT), np.mean(err_u[:, 19:24] <= HIT), np.mean(err_u[:, 24:30] <= HIT)]
        thirds = [hit[:, 14:19].mean(), hit[:, 19:24].mean(), hit[:, 24:30].mean()]
        shift = np.nanmedian(tdeg(np.abs(wrap(rec['theta'][:, 24:30] - world.res[:, 24:30]))))
        res = dict(kind=kind, p=p, target=kindu, follow_u_0_1=capt[0], follow_u_1_2=capt[1], follow_u_2_3=capt[2],
                   hit_u0_1=thirds[0], hit_u1_2=thirds[1], hit_u2_3=thirds[2], shift_deg_u2_3=shift,
                   wind1_t30=np.mean(rec['wind'][:, 29] == 1))
        table.append(res)
        print(f"  {kind} p={p} target={kindu}: heading within 20 deg of the pull, by |u| third: {capt[0]:.2f} {capt[1]:.2f} {capt[2]:.2f}; "
              f"hits {thirds[0]:.2f} {thirds[1]:.2f} {thirds[2]:.2f}; median error vs resource at |u| 2..3: {shift:.1f} deg; "
              f"winding 1 at trial 30: {res['wind1_t30']:.2f}", flush=True)
        for s in range(S):
            rows.append(dict(kind=kind, p=p, target=kindu, seed=s, follow_u_2_3=np.mean(err_u[s, 24:30] <= HIT),
                             hits_u_2_3=hit[s, 24:30].mean(), wind_t30=rec['wind'][s, 29]))
    write_csv(out, 't1b_seeds', rows)
    write_csv(out, 't1b_summary', table)


def t1c(S, out, rng_seed):
    print("TEST 1c: injury, k parts removed at trial 45 (cues on) or at trial 61 (blank)")
    rows, table = [], []
    conds = [('R', 4, True, False), ('R', 4, False, False), ('N', 1.5, True, False), ('N', 1.5, True, True), ('L', 0, True, False)]
    eps = .3
    for at, label in ((44, 'cues'), (60, 'blank')):
        for kind, p, reconnect, hub in conds:
            for k in ((0,) if hub else (1, 2, 4, 6, 9)):
                rng = np.random.default_rng([rng_seed, 2])
                world = World(np.random.default_rng([rng_seed, 1]), S)
                org = make(kind, S, rng, p, reconnect=reconnect)
                rec = run(org, world, rng, eps, injury=dict(at=at, k=k, hub=hub))
                S_, T, drift = summarize(rec)
                defined = ~np.isnan(drift)
                res = dict(kind=kind, p=p, reconnect=reconnect, hub_removed=hub, k=k, when=label,
                           hit_50_60=rec['hit'][:, 49:60].mean(), wind1_t60=np.mean(rec['wind'][:, 59] == 1),
                           wind1_t70=np.mean(rec['wind'][:, 69] == 1), pers_defined=defined.mean(),
                           pers_ok=np.mean(defined & (drift <= np.deg2rad(30))),
                           drift_med_deg=(np.median(tdeg(drift[defined])) if defined.any() else np.nan))
                table.append(res)
                print(f"  {label:5s} {kind} p={p} reconnect={reconnect} hub_removed={hub} k={k}: hits 50..60 {res['hit_50_60']:.2f}; "
                      f"winding 1 at 60: {res['wind1_t60']:.2f}, at 70: {res['wind1_t70']:.2f}; blank drift defined {defined.mean():.2f}, "
                      f"within 30 deg {res['pers_ok']:.2f}, median {res['drift_med_deg']:.1f} deg", flush=True)
                for s in range(S):
                    rows.append(dict(kind=kind, p=p, reconnect=reconnect, hub_removed=hub, k=k, when=label, seed=s,
                                     hit_50_60=rec['hit'][s, 49:60].mean(), wind_t60=rec['wind'][s, 59],
                                     wind_t70=rec['wind'][s, 69], drift_deg=tdeg(drift[s])))
    write_csv(out, 't1c_seeds', rows)
    write_csv(out, 't1c_summary', table)


# ------------------------------------------------------------------ nesting
class Colony:
    """Four sub-rings of 16 parts, each with its own world, under a top ring of 16 (contact variants).
    contact: a port (site 0 of each sub-ring) reads a share t from its partner site on the top ring (sites
    0, 4, 8, 12) and 1 - t from its own ring, and the partner likewise. shared: every sub-ring part reads
    a share kf of the mean of all 64 sub-ring parts and 1 - kf from its own ring (and contacts)."""
    M = 4

    def __init__(self, S, rng, G=4.0, contact=True, shared=False, t=.5, kf=.5):
        self.S, self.G, self.contact, self.shared, self.t, self.kf = S, G, contact, shared, t, kf
        self.Np = self.M * N + (N if contact else 0)
        self.top0 = self.M * N
        idx = np.zeros((self.Np, 3), int)
        wt = np.zeros((self.Np, 3))
        for m in range(self.M):
            for j in range(N):
                s = m * N + j
                port = contact and j == 0
                share = (1 - t) if port else 1.0
                idx[s, 0], wt[s, 0] = m * N + (j + 1) % N, share / 2
                idx[s, 1], wt[s, 1] = m * N + (j - 1) % N, share / 2
                if port:
                    idx[s, 2], wt[s, 2] = self.top0 + 4 * m, t
        if contact:
            for j in range(N):
                s = self.top0 + j
                port = j % 4 == 0
                share = (1 - t) if port else 1.0
                idx[s, 0], wt[s, 0] = self.top0 + (j + 1) % N, share / 2
                idx[s, 1], wt[s, 1] = self.top0 + (j - 1) % N, share / 2
                if port:
                    idx[s, 2], wt[s, 2] = (j // 4) * N, t
        self.idx, self.wt = idx, wt
        self.is_sub = np.arange(self.Np) < self.M * N
        th = rng.uniform(-pi, pi, (S, self.M + 1, 1))
        z = np.zeros((S, self.Np), complex)
        for m in range(self.M):
            z[:, m * N:(m + 1) * N] = rest(G) * np.exp(1j * (PSI[None, :] + th[:, m]))
        if contact:
            z[:, self.top0:] = rest(G) * np.exp(1j * (PSI[None, :] + th[:, self.M]))
        self.z = z
        self.w = np.full((S, self.M, 2), .5)

    def reading(self):
        r = (self.z[:, self.idx] * self.wt[None, :, :]).sum(-1)
        if self.shared:
            mean_sub = self.z[:, :self.M * N].mean(1, keepdims=True)
            r = np.where(self.is_sub[None, :], (1 - self.kf) * r + self.kf * mean_sub, r)
        return r

    def step(self, I, rng):
        v = self.G * self.reading() + I
        self.z = self.z + DT * (-self.z + lim(v)) + sqrt(DT) * SIGMA * cnoise(rng, self.z.shape)

    def block(self, m):
        return self.z[:, m * N:(m + 1) * N]

    def headings(self):
        return np.stack([np.angle((self.block(m) * CEPSI[None, :]).sum(1)) for m in range(self.M)], 1)

    def windings(self):
        def wnd(zb):
            a = np.angle(zb)
            return np.rint(wrap(np.roll(a, -1, axis=1) - a).sum(1) / (2 * pi)).astype(int)
        w = np.stack([wnd(self.block(m)) for m in range(self.M)], 1)
        top = wnd(self.z[:, self.top0:]) if self.contact else np.zeros(self.S, int)
        return w, top


def t3(S, out, rng_seed):
    print("TEST 3: nesting at a contact against a shared field (eps .3, G 4)")
    eps = .3
    BCAST = (2, 5, 8)
    rows, table = [], []
    for variant, contact, shared in (('contact', True, False), ('shared', False, True), ('both', True, True)):
        rng = np.random.default_rng([rng_seed, 2])
        wrng = np.random.default_rng([rng_seed, 1])
        worlds = [World(wrng, S, phiA=wrng.uniform(-pi, pi, S)) for _ in range(Colony.M)]
        phi_b = wrng.uniform(-pi, pi, (S, TRIALS))
        col = Colony(S, rng, contact=contact, shared=shared)
        th_rec = np.zeros((S, TRIALS, Colony.M))
        hit_rec = np.zeros((S, TRIALS, Colony.M), bool)
        w_rec = np.zeros((S, TRIALS, Colony.M), int)
        top_rec = np.zeros((S, TRIALS), int)
        for t in range(TRIALS):
            I = np.zeros((S, col.Np), complex)
            for m in range(Colony.M):
                I[:, m * N:(m + 1) * N] = cue_input(worlds[m], col.w[:, m], eps, t)
                if t in BCAST:
                    I[:, m * N:(m + 1) * N] += eps * .5 * np.exp(1j * (PSI[None, :] + phi_b[:, t][:, None]))
            for _ in range(STEPS):
                col.step(I, rng)
            th = col.headings()
            th_rec[:, t] = th
            w_rec[:, t], top_rec[:, t] = col.windings()
            for m in range(Colony.M):
                if worlds[m].cue[t]:
                    hit_rec[:, t, m] = np.abs(wrap(th[:, m] - worlds[m].res[:, t])) <= HIT
                for s_ in range(2):
                    upd = worlds[m].ann[:, s_, t]
                    col.w[:, m, s_] = np.where(upd, col.w[:, m, s_] + ETA * (worlds[m].hit[:, s_, t] - col.w[:, m, s_]), col.w[:, m, s_])
        keep59 = (w_rec[:, 59] == 1)
        keep69 = (w_rec[:, 69] == 1)
        n_keep = keep69.sum(1)
        S_sub = hit_rec[:, 14:30].mean(1)             # (S, M)
        # errors on broadcast trials, correlation across sub-rings
        errs = np.stack([wrap(th_rec[:, t, :] - np.stack([worlds[m].res[:, t] for m in range(Colony.M)], 1)) for t in BCAST], 1)  # (S, 3, M)
        e = errs.reshape(-1, Colony.M)
        cors = []
        for a in range(Colony.M):
            for b in range(a + 1, Colony.M):
                cors.append(np.corrcoef(e[:, a], e[:, b])[0, 1])
        all_miss_b = np.mean((np.abs(errs) > HIT).all(2))
        ctrl_t = [t for t in range(2, 12) if t not in BCAST]
        errs_c = np.stack([wrap(th_rec[:, t, :] - np.stack([worlds[m].res[:, t] for m in range(Colony.M)], 1)) for t in ctrl_t], 1)
        all_miss_c = np.mean((np.abs(errs_c) > HIT).all(2))
        # headings on blank trials: circular sd across the sub-rings that keep their turn
        sds = []
        for s in range(S):
            for t in range(BLANK, TRIALS):
                k = w_rec[s, t] == 1
                if k.sum() >= 2:
                    sds.append(circ_sd(th_rec[s, t, k]))
        blank_sd = tdeg(np.mean(sds)) if sds else np.nan
        res = dict(variant=variant, all4_keep_t60=np.mean(keep59.all(1)), all4_keep_t70=np.mean(keep69.all(1)),
                   median_keep_t70=np.median(n_keep), mean_keep_t70=n_keep.mean(),
                   top_keep_t70=(np.mean(top_rec[:, 69] == 1) if contact else np.nan),
                   S_sub_mean=S_sub.mean(), S_sub_min=S_sub.mean(0).min(), err_corr_bcast=np.mean(cors),
                   all_miss_bcast=all_miss_b, all_miss_ctrl=all_miss_c, blank_sd_deg=blank_sd)
        table.append(res)
        print(f"  {variant}: all four keep w=1 at trial 60: {res['all4_keep_t60']:.2f}, at 70: {res['all4_keep_t70']:.2f}; "
              f"median kept at 70: {res['median_keep_t70']:.0f} (mean {res['mean_keep_t70']:.2f}); top keeps: {res['top_keep_t70']}; "
              f"S per sub-ring mean {res['S_sub_mean']:.3f} (min {res['S_sub_min']:.3f}); broadcast error corr {res['err_corr_bcast']:.2f}; "
              f"all four miss: broadcast {all_miss_b:.2f} vs control {all_miss_c:.2f}; blank spread {blank_sd:.1f} deg", flush=True)
        for s in range(S):
            rows.append(dict(variant=variant, seed=s, keep_t60=int(keep59[s].sum()), keep_t70=int(n_keep[s]),
                             top_t70=int(top_rec[s, 69]), S_sub=S_sub[s].mean()))
    write_csv(out, 't3_seeds', rows)
    write_csv(out, 't3_summary', table)


def write_csv(out, name, rows):
    if not rows:
        return
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, f"{name}.csv")
    with open(path, 'w', newline='', encoding='utf-8') as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)


TESTS = dict(smoke=smoke, t2=t2, t1a=t1a, t1b=t1b, t1c=t1c, t3=t3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tests', nargs='*', default=['smoke', 't2', 't1a', 't1b', 't1c', 't3'])
    ap.add_argument('--seeds', type=int, default=100)
    ap.add_argument('--seed', type=int, default=12)
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'architecture_experiment_12_results')
    for name in a.tests:
        t0 = time.time()
        TESTS[name](a.seeds, out, a.seed)
        print(f"  [{name} done in {time.time() - t0:.0f} s]", flush=True)


if __name__ == '__main__':
    main()
