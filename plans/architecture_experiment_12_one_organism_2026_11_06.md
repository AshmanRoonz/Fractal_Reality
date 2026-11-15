# Architecture of Wholeness, Experiment 12: one organism with a 0 at its center

Status: v1.1, 2026-11-07. The predictions in sections 4 and 6 were frozen on 2026-11-06 before any code was written or run, and are unchanged. The run's results are in the Results section at the end, dated, with everything read after the fact marked as such. Code and data: `experiments/architecture_experiment_12_v1.py` and `experiments/architecture_experiment_12_results/`. Drafted by Claude at Ashman's request, after the audit of the Architecture of Wholeness series, Experiments 1 to 11 (`experiments/architecture_study_audit_v1.py`), and the wholeness tests (`experiments/wholeness_*.py`). This is Experiment 12 of that series, not of the physics series, which has an Experiment 12 of its own.

## 1. What this tests, and what it does not

The proposal that prompted it (the study author's note of 2026-11-06) asks whether intelligence can emerge from a system organized around maintaining its own wholeness, and suggests building one organism from the eleven experiments' parts, with "an individual decision-making center". This experiment does not answer that question, and it is designed so that nobody can mistake its result for an answer. The learning in it is one standard rule, a credibility weight per cue source updated by outcomes, and it does the same work in every organism. What the design isolates is the one thing the framework has an input on and the proposal gets wrong: the type of center.

Three organisms are built from the same parts, the same inputs, the same boundary and the same learning rule, and differ only in what sits at the center:

- **L, a list.** The center is the mean of the parts (a barycenter). Nothing is at the center, and nothing holds there.
- **N, a node.** A hub that reads all the parts and that all the parts read, with a self-gain G_h that runs it from a chair (it follows the parts) to a leader (it holds its own state).
- **R, a ring.** Parts coupled in a closed loop carrying one turn of phase. The center is the 0 that the turn forces: none of the parts, nothing to occupy, nothing to remove. The organism's decision is the orientation of the whole loop around that 0.

The framework's claims under test, each carried from the wholeness tests into an organism with inputs, a task and learning:

1. A 0 is fragile to anything shared and robust to ties; so a 0-centered organism needs a boundary that filters what is shared, and with that boundary it is not captured.
2. Health is a corner, not a middle: a 0-centered organism holds its state when unpushed (as a leader does) and moves at the rate of its input (as a chair does), while a node trades the one for the other through a single tuned threshold.
3. Parts with their own 0 keep it only if joined at a contact; in one shared field they push each other out.

"Intelligence" is measured narrowly: hit rate in a foraging task under noise, deception and change; persistence without cues; re-lock after a change; survival of the turn under injury and under nesting. The three controls that caught the overstatements in Experiments 3, 7 and 10 are built in (section 6). Nothing here bears on experience or on a soul.

## 2. The organisms

**Common parts.** n = 16 parts with preferred directions ψ_j = 2πj/n. Each part has a complex state z_j (a strength and a phase) under the leak-and-limit law of the wholeness tests:

    z_j' = −z_j + lim(G · (W z)_j + I_j) + noise,    lim(w) = tanh(|w|) · w/|w|

with complex white part noise of intensity σ = .05 added to z, and dt = .05.

- **Field (Φ): the coupling W.** In R, W is the ring: W_jk = 1/2 for k = j ± 1 (mod n), otherwise 0. In N, W = 0 and the parts read the hub instead. In L, W = 0.
- **Path (—): credibility weights** w_s in [0, 1], one per cue source s, starting at .5 and updated at the end of each trial by w_s ← w_s + η (hit_s − w_s), η = .2, where hit_s = 1 if the source's announced direction was within 20° of where the resource turned out to be. The same rule in every organism, and it does not depend on what the organism did. The path is also the carry of state from one trial to the next.
- **Boundary (○): common-mode rejection.** I_j ← I_j − mean_k I_k before the input enters. It removes any pull shared by all the parts and passes anything patterned. Switchable, for Test 1.
- **Inputs.** A cue from source s in direction φ_s with strength ε enters as I_j = ε · w_s · exp(i(ψ_j + φ_s)): a patterned input with the ring's own twist and a global phase equal to the cue's direction. Several cues add.
- **The center, and how the decision is read.**
  - R: heading θ = arg Σ_j z_j exp(−iψ_j), the phase of the first spatial mode. The turn is w = (1/2π) Σ_j wrap(arg z_{j+1} − arg z_j), expected 1. Coherence c₁ = |Σ_j z_j exp(−iψ_j)| / Σ_j |z_j|.
  - N: a hub of K = n real cells y_k with y_k' = −y_k + tanh(G_h y_k − β Σ_{l≠k} y_l + x_k), driven by x_k = κ_in |P| cos(arg P − ψ_k), where P = (1/n) Σ_j z_j exp(−iψ_j) is the parts' population vector. The parts read the hub back: I_j gains κ_out Σ_k max(y_k, 0) exp(iψ_k). [Clarified 2026-11-07, before the run: as written this is one number for every part, a uniform pull that the readout and the boundary cancel; "the parts read the hub" needs the pattern's twist, so the code gives part j κ_out · Y · exp(iψ_j) with Y = Σ_k max(y_k, 0) exp(iψ_k). The predictions were not changed.] Heading = arg Σ_k max(y_k, 0) exp(iψ_k). At G_h = 0 the hub is a chair; above 1 its cells are bistable and the hub is a leader that keeps its choice until the drive for another cell crosses a threshold. With κ_out = 0 the hub is only a reader and N reduces to L with a decider on top.
  - L: heading = arg P, read instantly; no state at the center.

**Why N has discrete cells and R does not.** Under the complex law a hub with self-gain has a soft phase, because the limiter keeps phase and only caps strength; a complex hub would be a chair at any gain. A leader that stops following needs a stiff state, which is a bistable cell. R's heading is a neutral mode of the loop (the law is unchanged by a global phase shift), so it is soft by construction: it moves at the rate it is pushed and stays where it is left. That is the mechanical content of the corner claim, and Test 2 checks it.

The energy turn of the flow tests (phase advancing at a rate set by |z|²) is left out. With uniform amplitude it rotates the heading at a constant rate, which is a separate question.

## 3. Environment and task

Trials of τ = 40 time units (800 steps). In each trial a resource lies in direction φ*, drawn once per environment, with per-trial noise of 10°. An honest source announces φ* every trial. A deceptive source announces a uniformly random direction on half the trials. At the end of the trial the organism's heading is read: a hit if |θ − φ*| ≤ 20°. The resource's true direction is then revealed to the credibility rule (as in Experiment 4's evidence and Experiment 9's credibility), whatever the organism did.

Schedule: trials 1 to 30, environment A (φ* = 0°); at trial 31, φ* jumps to 120°; trials 31 to 60, environment B; trials 61 to 70, blank (no cues at all).

Measures: S, the hit rate over trials 15 to 30 (after learning); T, the first trial after the jump that begins three consecutive hits, counted from the jump (T = 1 is trial 31); Pers, the heading's drift from the start to the end of the ten blank trials, for organisms that have a heading there; and w, c₁ and |P| throughout.

Parameters swept: ε in {.15, .3}; R: G in {2, 4, 8}, boundary on and off; N: G_h in {0, .5, 1, 1.5, 2}, with β = .5, κ_in = 1, κ_out = .5 and the parts' gain G_p = 4; 100 seeds per cell.

## 4. Tests and frozen predictions

Each prediction is labeled **Derived** (from the equations above), **Carried** (a number from the wholeness tests, with the band expected when the setting changes) or **Guess**.

### Test 1. Capture, injury and the boundary

**1a. A uniform pull.** The same complex number u is added to every part's input (no pattern), ramped from 0 to 3 in environment A after learning (trials 15 to 30).

- R, boundary off, G = 4: the turn ends (w falls to 0, c₁ below .2) at |u| between .15 and .6, centered on .3. Carried: .316 on the 128-part ring; 16 parts may differ.
- R, boundary on: no capture at any |u| up to 3. Derived: the rejection is exact.
- N and L: no capture by a uniform pull at any size. Derived: Σ_j exp(−iψ_j) = 0, so a uniform input cancels in the readout. On this test the 0 is the only center that can be captured this way, and the boundary is what answers it. That is recorded as such.
- A patterned false cue (a twisted input) passes every boundary; what happens next depends on the credibility weights, equally in all three organisms (hit rates within 10% of each other at every trial). Derived: the weight rule is shared.

**1b. A targeted input.** The same u applied to the hub's cells (N only), or to any one part (all three).

- N: captured by a hub input above the cell threshold, which rises with G_h. Derived: for a bistable cell the switching input is I_c = G_h y* − atanh(y*) with y* = √(1 − 1/G_h), so .21 at G_h = 1.5 and .53 at G_h = 2, plus the inhibition from the cell that is on, about β y_on.
- R and L: an input to any one part moves the heading by at most 1/n of its angle (at most 22.5° at the largest input), and no part can end the turn. Carried: holding one part opposite turned at most .5% of the others.

**1c. Injury** (Experiment 3's removal): k parts removed at random, k = 1 to 9.

- R without reconnection: any removal ends the turn. Derived: an open chain has no winding number.
- R with Experiment 3's repair rule (the neighbors of a removed part connect to each other): the turn survives up to k = 9, which is n minus the measured floor of 7 parts at G = 4. Carried.
- N: survives every part removal while the hub lives, and loses its heading when the hub is removed. L: degrades in proportion. Derived, and trivial: this is the "its center cut away" column of the types-of-center table.

### Test 2. The corner: persistence and corrigibility

**Persistence** (blank trials 61 to 70).

- R: holds its heading. Derived: the neutral mode performs a random walk with variance σ² t / (n r²), a standard deviation of about 4.5° per trial and 14° over the ten blank trials. Frozen: the drift over the blank is within 30° in at least 90 of 100 seeds.
- N leader (G_h ≥ 1.5): holds within 5°. Derived: bistable.
- N chair (G_h ≤ 1) and L: no heading in the blank (|P| → 0); persistence fails. Derived.

**Corrigibility** (T, after the jump at trial 31).

- R: the heading follows the honest cue at the rate θ' = (ε w / V) sin(φ − θ), with V = G r cos(2π/n) and r the standing amplitude, because the limiter passes a perpendicular (phase) input with gain tanh(V)/V = r/V. A 120° jump reaches 20° in 2.29 V/ε time units. With w = 1 the values of V are 1.74, 3.69 and 7.39 at G = 2, 4, 8. Derived: at ε = .3 the re-lock takes 13, 28 and 56 time units, so T = 1, 1, 2; at ε = .15 it takes 27, 56 and 113 time units, so T = 1, 2, 3. A richer center is a slower one, and the prediction says by how much.
- N leader: T is a step. One trial when the honest drive clears the cell threshold, never otherwise. Derived. Which side of the step it lands on depends on G_h, β, ε and the learned weight together.
- N chair and L: T = 1. Derived.

**The corner.** Pass = S ≥ .9, T ≤ 2 and persistence within 30°, all together.

- R passes in 5 of its 6 (G, ε) cells; the cell (8, .15) is predicted to fail on T. Derived.
- N passes at no more than one G_h value for a given ε, and the passing value is not the same at ε = .15 as at ε = .3. Guess, grounded in the threshold formula: the leader's working range is one tuned window.
- L never passes: no persistence. Derived.

**What would count against the framework:** R captured with the boundary on (1a); R drifting more than 30° in the blank in more than 10 seeds; R's re-lock times off the 2.29 V/ε law by more than 50%; N passing the corner at three or more of its five G_h values at both ε (then the window is not tuned, and the corner is not special to the 0).

### Test 3. Nesting at a contact

m = 4 sub-rings of 16 parts, each with its own environment (its own φ*, honest source and deceptive source), under a top ring of 16 parts with no environment of its own, in two constructions:

- Contact: one part of the top ring couples, both ways with weight κ_c = .5, to one part of each sub-ring; nothing else connects them.
- Shared field: every part of every sub-ring also reads the mean state of all 64 parts, with weight κ_f = .5.

Each sub-ring runs the schedule of section 3 in its own environment. Before learning (trials 1 to 10), on three chosen trials, one patterned false cue is broadcast to every sub-ring at once, with weight .5.

- Contact: all four sub-rings keep w = 1 and the top ring keeps w = 1 in at least 95 of 100 seeds; each sub-ring's heading tracks its own cue (S ≥ .9 each). Carried: every level kept its own 1 through 64 parts and three levels.
- Shared field: at most two of the four sub-rings keep w = 1 (median over seeds), and all four keep it in no more than 10 of 100 seeds; the sub-rings that keep a heading sit within 20° of each other on cue-free trials. Carried: 13 centers placed in one field fell to 5 or 3.
- Under the shared false cue: contact sub-rings respond each on their own (correlation of heading errors across sub-rings below .3); shared-field sub-rings respond together (above .7), so all four miss together far more often (P(all four miss) ≥ .5 against ≤ .1). Guess, from "fragile to anything shared" read one level up.

**Against the framework:** contact sub-rings losing their turns in more than 20 of 100 seeds; shared-field sub-rings all keeping theirs in more than 50.

## 5. The roles, as inputs rather than labels

- • Center: the 0 (R), the hub (N), the mean (L). The type is the independent variable.
- — Path: the credibility weights, and the carry of heading from trial to trial.
- ○ Boundary: common-mode rejection, and the reconnection rule under injury. Its reason to exist is Test 1a.
- Φ Field: the ring coupling W; the field interpolated inside the ring is what holds the 0.
- ⊙ Whole: the heading, a property of the loop that no part has.

## 6. Controls, run on every organism

- **Memory reset.** Set every w_s back to .5 at the jump. Prediction: T rises by at least 3 trials in every organism alike (Derived: the false source has to be re-learned, about 1/η trials). If T does not rise, the learning was not doing the work, as in Experiment 3's repair.
- **Shuffled feedback.** Assign each trial's hit_s from a shuffled trial order. Prediction: the honest and deceptive weights stay within .1 of each other, and S falls below .4 in every organism (Guess). If S survives, the credibility learning was not learning, as in Experiment 7.
- **Coin flip.** An organism that heads in a uniformly random direction each trial. Hit rate 40/360 = .111 (Derived). Every claim of performance is stated as a multiple of this; after learning, every organism except an untuned leader is predicted at 8× or better (Guess).

What the controls are expected to show, stated now: that the learning carries the hit rate, and that the type of center carries persistence, corrigibility, capture and nesting. If the center turns out to carry the hit rate as well, that is a finding against this design's reading, and it will be recorded as one.

## 7. Run plan

- Code: `experiments/architecture_experiment_12_v1.py`, numpy, vectorized over seeds; the predictions above copied into its docstring before the first run, and the results appended below them. Outputs: one CSV per test (per seed and condition) and a summary table.
- Compute: 16 parts × 56,000 steps × 100 seeds × about 30 conditions; minutes.
- Order: Test 2 first (it carries the most derived numbers and the most risk), then Test 1, then Test 3, with the controls alongside each.
- Reporting: every prediction above gets PASS, MISS or INCONCLUSIVE with its number. Misses are not relabeled.

## 8. What is reused from Experiments 1 to 11, and what is left out

Reused: removal and repair (3), evidence as a revealed outcome (4), a gate on input (7, here fixed as common-mode rejection), a change in the environment (8), credibility per source (9), a broadcast that deceives (11). Left out of this draft: the commons (10), which would be the natural extension of Test 3 (four sub-organisms drawing on one habitat), and the learned gate (5 to 7). Both are left out so that the three structural claims are tested with as little else moving as possible.

Also left out, and named so it is not read into the result: the proposal's own question. A test of it would give an organism no objective but keeping its turn (w = 1) and ask whether foraging, or anything else, arises from that. Nothing here does that.

## 9. Prior art the result will be read against

Continuous attractors for heading: Zhang (1996), and the fly's ring attractor (Seelig and Jayaraman 2015; Kim and colleagues 2017), where the bump of activity on a ring is the heading and no cell is it. Discrete attractors for decisions: Wang (2002). The soft-mode account of R and the stiff account of N are both standard results for those two classes. What is tested here is the framework's use of them, as the difference between a 0 and a node, and the three claims that follow from it.

## Results (run 2026-11-07, 100 seeds; everything after "After the fact" was written after seeing the numbers)

**Tally: 22 frozen predictions, 11 PASS, 11 MISS, of which 5 are partial (the main clause held and a part failed). None of the six conditions listed against the framework occurred.** The lock law checked out first: measured over derived re-lock times 1.01 to 1.07 across the six (G, ε) cells.

| Prediction | Result |
| --- | --- |
| P1a.1 (C) R without boundary captured at .15 to .6 | MISS: .71 (.68 to .73). After the fact: the honest cue holds the twist against the pull, which the earlier ring did not have |
| P1a.2 (D) R with boundary not captured up to 3 | PASS: hits .99, |P| 1.00 throughout |
| P1a.3 (D) N and L not captured at any size | PASS for N (hits .99 in every third of the ramp); MISS for L at |u| 2 to 3 (hits .78, |P| .06: saturation crowds out the pattern) |
| P1a.4 (D) a patterned false cue affects all alike, within .1 at every trial | MISS by a hair: spread .10 and .11 on trials 1 and 2 (R lags from its random start), under .1 from trial 3 |
| P1b.1 (D) N captured above I_c rising with G_h; .21 at 1.5, .53 at 2 | PASS on the order (chair below 1, G_h 1.5 at about 2, G_h 2 above 3), MISS on the numbers: the formula ignores the drive the hub feeds back to itself |
| P1b.2 (C) one part moves R and L at most 22.5°, never ends the turn | PASS: R 21.5° median (hits .37), turn kept in 100%; L 6.9° |
| P1c.1 (D) no reconnection: any removal ends the turn | PASS where the measure can speak: k = 1 leaves the turn in 0 of 100, k = 2 in 4; at k ≥ 4 the ring is in fragments and the alive-order winding is an integer by construction |
| P1c.2 (C) reconnection: the turn survives to k = 9 | PASS to k = 6 (100%), MISS at k = 9 (61% blank, 66% with cues) |
| P1c.3 (D) N survives any part removal while the hub lives; no heading without the hub | PASS (97% at k = 9; drift 0.2°; no heading once the hub goes). L unaffected by any removal, so "degrades in proportion" was not borne out |
| P2.1 (D) R holds in the blank, drift within 30° in ≥ 90 seeds | PASS: median 10°, within 30° in 98 to 100% |
| P2.2 (D) leader holds within 5°; chair and L have no heading in the blank | PASS leader (0.1°) and L; MISS chair: it holds (4°, |P| 1.00). After the fact: the parts-hub loop sustains itself with no input; a node its parts read back is a memory whatever its own gain |
| P2.3 (D) T = 1, 1, 2 (ε .3) and 1, 2, 3 (ε .15) for G = 2, 4, 8 | PASS, all six |
| P2.4 (D) leader: a step, 1 or never; chair and L: T = 1 | PASS leader in form (never, at every G_h ≥ 1); PASS L; MISS chair (T 3 and 2: the same loop gives it inertia) |
| P2.5 (D) corner: R passes 5 of 6, failing (8, .15) | PASS exactly |
| P2.6 (G) N passes at most one G_h per ε, not the same at both | PASS: G_h 0 at ε .3, none at ε .15 |
| P2.7 (D) L never passes | PASS |
| P3.1 (C) contact: all four sub-rings and the top ring keep their turn in ≥ 95; S ≥ .9 | MISS on the counts (sub-rings 92, top ring 62, lost over the first 30 trials as four unrelated headings strained it); PASS on S (.937, lowest .909) |
| P3.2 (C) shared field: median ≤ 2 keep; all four in ≤ 10 | PASS: 0 of 4 in every seed |
| P3.3 (G) shared false cue: correlation < .3 against > .7; all miss ≤ .1 against ≥ .5 | MISS: .07 against −.02, and .08 against .07; S .944. After the fact: the shared field couples the common mode and the heading lives in the first mode |
| PC.1 (D) memory reset raises T by ≥ 3 | MISS: by 1 to 2 in R, chair and L; 0 for stuck leaders |
| PC.2 (G) shuffled feedback: weights within .1; S < .4 | MISS twice: gap .31; S .87 to .95, while T doubles. The honest source stays mostly right under the shuffle, so the control cannot bite on S |
| PC.3 (D) coin flip .111; (G) organisms at ≥ 8× | PASS: .113; R, chair and L at 8.7 to 8.9×; the stuck leader at 4.3× |

**Read after the fact.**

1. The ring's heading law is exact to a few percent and the corner follows from it. The 0-centered organism holds without input and follows at the derived rate across gains, and fails exactly where the derivation said. The node reaches the corner in one cell, and only because its parts-hub loop is a memory; above G_h 1 it commits in the first trials and never moves again (S .48 is the share of seeds where it happened to commit within reach).
2. The turn is not needed to decide. L has no turn and hits .986; the shared-field colonies lose every turn and hit .944. In this task the 0 buys persistence without input and smooth corrigibility, and carries one fragility, to a uniform pull, which the boundary removes exactly. "Fragile to anything shared" held for the turn (0 of 4 kept) and not for the behaviour.
3. Learning carried the hit rate less than predicted and the re-lock speed more: the shuffle control barely touched S and doubled T. The controls were too weak on the hit rate; a harder task is needed before "learning does the work" can be claimed or denied.
4. The clarification of the hub's broadcast turned the chair into a loop with memory. That is a result about nodes, not a defect: a node that its parts read back is never only a reader.

## Revision history

- 2026-11-07 v1.1: results of the run appended, predictions unchanged; the hub-broadcast clarification recorded in section 2.
- 2026-11-06 v1.0: design and frozen predictions; nothing run.
