# Architecture of Wholeness, Experiment 13: a harder task, where learning must carry the hit rate

Status: v1.1, 2026-11-07. Design and frozen predictions (v1.0), run the same day; the results are in the Results section at the end, with everything read after the fact marked as such. The predictions in sections 5 and 6 were frozen before any full organism was built or run. Drafted by Claude at Ashman's request after Experiment 12 (`plans/architecture_experiment_12_one_organism_2026_11_06.md`, `experiments/architecture_experiment_12_v1.py`). The derivation tool is `experiments/architecture_experiment_13_reduced_v1.py`; the full experiment, when run, will be `experiments/architecture_experiment_13_v1.py`.

## 1. What this tests, and what it does not

Experiment 12 left three things open, and this experiment is built to close them.

1. **Its controls were too weak on the hit rate.** The resource stayed put for thirty trials, so a source graded against another trial's resource was still graded against nearly the same direction. Shuffled feedback left the honest and deceptive weights .31 apart and the hit rate at .87 to .95, and it could not say whether learning carried the hit rate. Here the resource moves, there are more liars than honest sources, and the controls are derived to bite.
2. **Two readings were made after the fact** and are now predictions: that the 0 buys persistence without input and smooth corrigibility, and not the decision; and that a node its parts read back is a memory whatever its own gain. In a world that changes, persistence and corrigibility pull against each other, so each has a price and a payoff in hits, and the reading can fail.
3. **The Theory of Wholeness document's new row** under "what would change my mind" names this test: a harder task, where learning must carry the hit rate. It fails if a list reaches the corner, if a ring with a 0 drifts in the blank, or if hits need the turn.

The same three organisms as before, differing only in the type of center. "Intelligence" is still only a hit rate. Nothing here bears on experience, on a soul, or on the proposal's own question (an organism with no objective but its own wholeness).

## 2. What changes from Experiment 12, and what stays

**The world.** 100 trials in regimes of k trials, k in {2, 5, 10, 25}. At the start of each regime the resource direction is redrawn uniformly; within a regime it holds, with the same 10° per-trial noise as before. One trial in four, drawn at random, is blank: no cue reaches the organism, the resource is still there, and the organism's heading is still graded. Blank trials make persistence pay in hits; regime changes make corrigibility pay; short regimes make persistence cost.

**The sources.** One honest source announces the resource on every cued trial. Three deceptive sources each lie on a fraction q = .9 of cued trials, each in its own uniformly random direction, and announce the resource otherwise. All four announce on every cued trial. The unweighted sum of four such cues is wrong most of the time, so an organism that does not learn cannot hit; the reduced model of section 4 put the unlearned list at .31 and the learned list at .90, and those two numbers are why q and the count were set so (section 4 records the choice as a design step, made before any full-model run).

**The credibility weights.** The rule is Experiment 12's, r_s ← r_s + η (hit_s − r_s), η = .2, starting at .5, updated at the end of every cued trial for every source, graded on the revealed resource. One change: the weight an organism uses is the credibility above chance, w_s = max(0, (r_s − c) / (1 − c)) with c = 1/9, the hit rate of a random direction. A source at chance gets no weight. Experiment 12's raw form w_s = r_s is run alongside (Test 3), and so is a gate, w_s = 1 if the corrected credibility is at least .5 and 0 otherwise.

**What stays.** n = 16 parts under the leak and limit law, dt = .05, σ = .05, trials of 40 time units (800 steps), the boundary on (common-mode rejection; the uniform-pull question is closed), cue strength ε = .3, a hit within 20°, 100 seeds. The organisms: L the list; N the node at hub gain 0 (chair) and 1.5 (leader), β = .5, κ_in = 1, κ_out = .5 with the pattern's twist, G_p = 4; R the ring at G in {2, 4, 8}. State carries across trials and nothing resets.

## 3. Measures

Over trials 21 to 100 (the first twenty are for learning):

- **S_all**: hit rate over all trials. No heading counts as a miss.
- **S_cued**: over cued trials. **S_blank**: over blank trials.
- **S_first**: over the first cued trial of each regime (the corrigibility price). **S_settled**: over cued trials from a regime's third trial on (the decision, once the organism has had time to turn).
- **Credibilities** r_s at trial 100, honest and liars. **Winding** of every ring at every trial.

## 4. Derivations

**Fixed points of the credibility rule.** The honest source always hits, so r_honest → 1. A liar announces the resource on a fraction 1 − q of cued trials and a random direction otherwise, so r_liar → (1 − q) + q/9 = .20 at q = .9, with a standing deviation of about .13 at η = .2. Corrected: w_honest = 1, w_liar → .10, three liars .30 against 1.

**Shuffled feedback in a changing world.** Graded against the resource of another trial, the honest source hits when that trial lies in the same regime, probability about k/100, and at chance otherwise: r_honest → k/100 + (1 − k/100)/9 = .13, .16, .20, .33 at k = 2, 5, 10, 25. Corrected weights .02, .05, .10, .25. The liars go to .11 to .13. So the shuffle equalizes the sources in a fast world and only half-bites at k = 25; the controls are derived to bite hardest where the world changes fastest.

**The corrigibility law.** Experiment 12 verified θ' = (ε w / V) sin(φ − θ), V = G r cos(2π/n), to within 7% (lock ratios 1.01 to 1.07). From a heading Δ₀ away from the cue, the time to come within 20° is (V / (ε w)) [ln tan(Δ₀/2) − ln tan 10°]. In one trial of 40 time units at ε = .3, w = 1, the ring re-locks from any Δ₀ up to Δ_max = 179°, 155°, 84° at G = 2, 4, 8. With the new direction uniform, the probability of re-locking within the first cued trial is P = 1.00, .86, .46. So S_first = S_settled × P: a richer center pays for its persistence on every change, by this much.

**The coalition.** If the three liars lie together in one direction, with total weight W against the honest source's 1, the heading error is atan2(W sin Δ, 1 + W cos Δ). At W = .3 (the corrected fixed point) the largest error is 17.5°, below the hit margin; at W = .6 (the raw fixed point) it is 37°, and 61% of lie directions miss; at W = 1 (unlearned) 90° and 78%. The gate sends W to 0. Weighting is therefore enough against three independent liars at their fixed point and not against their fluctuations, and a gate is what answers a coalition.

**The reduced model.** `experiments/architecture_experiment_13_reduced_v1.py` integrates the verified heading law through this world: one angle per organism, the list read as the angle of the weighted sum, the ring under θ' above with the neutral mode's noise, the leader committed to the list's heading on its first cued trial and fixed thereafter, and the chair standing in as the ring at V(8), since in Experiment 12 the chair re-locked in the same trial counts as the G = 8 ring (2 and 3) and held in the blank. It has no parts, no limiter and no hub. It was used, in this order: to choose three liars at q = .9 over one or five liars at .5 to .9 (the scan is in the file), to compare the three weight forms, and then to produce the numbers below at 500 seeds. The full organisms differ from it in their amplitude dynamics, the list's heading threshold, and the chair's real loop, so every number carries a band: ±.05 for the list and the rings, ±.10 for the chair.

## 5. Tests and frozen predictions

Each prediction is labeled **Derived (closed form)**, **Derived (reduced model)**, **Carried** (from Experiment 12) or **Guess**. The frozen table, corrected weights, three independent liars at q = .9:

| k | Organism | S_all | S_cued | S_blank | S_first | S_settled |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | L | .68 | .90 | 0 | .90 | (none) |
| 2 | R, G 2 | .76 | .90 | .33 | .90 | (none) |
| 2 | R, G 4 | .69 | .82 | .30 | .76 | (none) |
| 2 | R, G 8; chair | .49 | .58 | .22 | .44 | (none) |
| 5 | L | .68 | .90 | 0 | .90 | .90 |
| 5 | R, G 2 | .82 | .90 | .55 | .89 | .91 |
| 5 | R, G 4 | .79 | .88 | .53 | .76 | .91 |
| 5 | R, G 8; chair | .69 | .76 | .46 | .45 | .89 |
| 10 | L | .68 | .90 | 0 | .90 | .90 |
| 10 | R, G 2 | .84 | .90 | .64 | .89 | .90 |
| 10 | R, G 4 | .83 | .89 | .63 | .77 | .91 |
| 10 | R, G 8; chair | .79 | .85 | .61 | .46 | .92 |
| 25 | L | .68 | .90 | 0 | .90 | .90 |
| 25 | R, G 2 | .85 | .90 | .68 | .90 | .90 |
| 25 | R, G 4 | .85 | .91 | .69 | .76 | .91 |
| 25 | R, G 8; chair | .85 | .90 | .70 | .44 | .93 |
| any | leader | .11 to .13 | | | | |

At k = 2 no trial is a regime's third, so S_settled is not defined there.

### Test 1. Learning carries the hit rate

- **P1.1 (Derived, reduced model).** With learning, the list and the G = 2 ring hit .90 ± .05 of cued trials at every k. With the weights fixed at .5 (no learning) they hit .31 ± .05, and under random feedback (a coin flip in place of each source's hit) within .03 of that. The credibilities land at r_honest = 1.00 and r_liar = .20 ± .03 in every organism alike.
- **P1.2 (Derived, closed form and reduced model).** Under shuffled feedback the honest credibility lands at .13, .16, .20, .33 (±.03) at k = 2, 5, 10, 25, and the list's cued hit rate at .26, .30, .36, .51 (±.05): at or below the unlearned level for k ≤ 5, where the weights vanish and the list has no heading, and about half the learned level at k = 25. The control is sharp where the world is fast and blunt where it is slow, as derived.
- **P1.3 (Derived, reduced model).** The leader hits .11 to .13 at every k: chance. It commits on its first cued trial, mostly to the unlearned sum, and the resource leaves it.

### Test 2. The type of center, now that hitting is hard

- **P2.1 (Derived, reduced model).** S_all as tabled, ±.05, with this order: at k = 2, R(2) > L ≈ R(4) > R(8); at k = 10, every ring beats L, R(2) ≥ R(4) > R(8); at k = 25 the three rings are within .01 of each other and all beat L by about .17. Persistence pays in a slow world and costs in a fast one, and the gain sets the price.
- **P2.2 (Derived, closed form).** S_first = S_settled × P with P = 1.00, .86, .46: the rings hit .90, .77, .42 (±.05) on the first cued trial of a regime at every k; the list .90. Smooth corrigibility is exactly this: the ring turns at a derived rate, and a slower ring pays on every change.
- **P2.3 (Derived, reduced model).** The list hits no blank trial. The rings hit .33, .30, .22 of blank trials at k = 2; .55, .53, .46 at k = 5; .64, .63, .61 at k = 10; .68, .69, .70 at k = 25 (G = 2, 4, 8; ±.07). The 0 pays for itself on blank trials, by about a quarter of the regime-settled hit rate, less a first blank trial in each regime and the lag after a change.
- **P2.4 (Derived, reduced model).** On settled cued trials the G = 2 ring and the list hit alike, within .01. The G = 8 ring beats the list by .02 to .03 by averaging lies across trials. The turn adds nothing to the decision at the fast ring; what the slow ring adds is persistence again, now across cued trials. This is the frozen form of "the 0 buys persistence and smooth corrigibility, not the decision".
- **P2.5 (Carried; Guess on the band).** The chair follows the G = 8 ring's row within .10 on S_all, S_blank and S_first, because its parts-hub loop is a memory and in Experiment 12 it re-locked in the slow ring's trial counts. The leader row is P1.3.
- **P2.6 (Carried).** Every ring keeps its turn, winding 1, at every trial in every condition, 100 of 100 seeds: the cues are patterned, the boundary is on, and nothing uniform reaches the parts.

### Test 3. Weighting against gating, independent liars against a coalition

Run at k = 10 for L and R at G = 2, 4, 8, with the three weight forms, in two worlds: the liars independent (as above) and in a coalition (the three lie on the same trials in one shared random direction; q = .9).

- **P3.1 (Derived, reduced model).** Independent liars, cued hits for the list and the G = 2 ring: raw weights .80, corrected .90, gate .98 (±.05); the G = 8 ring .79, .85, .89. Reading credibility against chance is worth .10; dropping sources at chance is worth .08 more.
- **P3.2 (Derived, closed form and reduced model).** The coalition, cued hits for the list and the G = 2 ring: raw .59, corrected .76 (±.05), gate .99 (±.02); the G = 8 ring .62, .74, .90. Weighting cannot answer a coalition, because the liars' fluctuating weights sum past the margin; a gate answers it exactly. The gate beats corrected weighting by at least .20 under the coalition and by no more than .10 against independent liars.

### Controls, run on every organism in Test 1

No learning (weights fixed at .5, so every source counts alike), random feedback (each source's hit replaced by a coin flip with probability .5), shuffled feedback (each source graded against the resource of a uniformly random other trial), and the coin flip organism at 1/9. Predictions P1.1 and P1.2.

## 6. What would count against the framework, and what against the design

Against the readings carried from Experiment 12:

- **K1.** The G = 2 ring beats the list on settled cued trials by more than .05 at any k: the turn helps to decide, against P2.4.
- **K2.** Any ring's blank hit rate below .40 at k = 10: persistence does not pay as derived, against P2.3.
- **K3.** The G = 8 ring's first-trial hit rate above .65, or the G = 2 ring's below .80, at k = 10: the corrigibility law is off by far, against P2.2.
- **K4.** The chair differing from the G = 8 ring by more than .15 on S_first or S_blank at k = 10: the memory loop is not "like the slow ring", and the node needs its own law, against P2.5.
- **K5.** Under the coalition the gate beats corrected weighting by less than .15: the boundary reading fails, against P3.2.
- **K6.** The leader above .30 at any k: it moved, against the types-of-center table.

Against the design, which would mean redesigning before anything is claimed:

- **K7.** The learned list within .10 of the unlearned list on cued trials: the task is not harder.
- **K8.** Random feedback leaving hits more than .10 above the unlearned level: the control is wrong again.

## 7. Run plan

- Code: `experiments/architecture_experiment_13_v1.py`, built from Experiment 12's `World`, `Organism`, `cue_input` and `run` with the world of section 2, four sources, the weight forms, blank trials and regimes; the predictions above copied into its docstring before the first run, results appended after.
- First a correspondence check: the list and the G = 2 ring at k = 10, learned, 100 seeds, against the reduced model's row; if the full organisms are off by more than .05 the reduced model's bands are reported as failed and the run continues.
- Then Test 1 (6 organisms × 4 k × 4 learning conditions, 96 runs), Test 2's measures from the same runs, and Test 3 (20 runs). About 116 runs of 100 trials and 100 seeds: roughly twenty minutes at Experiment 12's speed.
- Reporting: every prediction gets PASS, MISS or INCONCLUSIVE with its number; misses are not relabeled; everything read after the fact is marked.

## 8. What is left out

The commons (Experiment 10), the learned gate of Experiments 5 to 7 (the gate here is a fixed threshold on credibility, not a learned one), a second cue strength, the uniform pull and injury (closed in Experiment 12), nesting, and the proposal's own question. Nothing here bears on experience.

## 9. Prior art the result will be read against

Weighting cues by their reliability is Bayesian cue combination (Ernst and Banks 2002; Knill and Pouget 2004); a learner whose rate of change tracks how fast the world changes is the volatility result of Behrens and colleagues (2007); the trade between holding a heading and following a cue is the Kalman gain, and the ring's lag is the cost side of the stability-plasticity dilemma already in the record. The heading as a bump on a ring and a leader as a committed attractor are as cited for Experiment 12. All of these are from memory and unchecked for this document. Within the series: credibility per source is Experiment 9, the broadcast that deceives is Experiment 11, and the coalition of Test 3 is that broadcast with learning as the defense.

## Results (run 2026-11-07, 100 seeds; everything after "After the fact" was written after seeing the numbers)

**Correspondence check:** the list and the G = 2 ring at k = 10, learned, matched the reduced model on all ten measures within .015. **Tally: 11 frozen predictions, 7 PASS, 4 MISS, of which 3 are partial (one number, one clause, one measure). None of the eight conditions in section 6 occurred.** Code and data: `experiments/architecture_experiment_13_v1.py`, `experiments/architecture_experiment_13_results/`.

Learned hit rates (S_all / S_cued / S_blank / S_first / S_settled), 100 seeds:

| k | L | Chair | Leader (S_all) | R, G 2 | R, G 4 | R, G 8 |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | .68 / .90 / 0 / .90 / - | .58 / .69 / .26 / .57 / - | .12 | .77 / .90 / .35 / .90 / - | .69 / .82 / .30 / .77 / - | .48 / .56 / .22 / .43 / - |
| 5 | .68 / .91 / 0 / .90 / .90 | .74 / .82 / .52 / .54 / .92 | .12 | .82 / .91 / .55 / .90 / .91 | .79 / .87 / .54 / .74 / .91 | .68 / .75 / .47 / .42 / .89 |
| 10 | .68 / .91 / 0 / .92 / .91 | .82 / .88 / .66 / .56 / .93 | .12 | .84 / .91 / .64 / .90 / .91 | .83 / .90 / .63 / .77 / .91 | .79 / .85 / .61 / .43 / .92 |
| 25 | .68 / .90 / 0 / .90 / .90 | .86 / .92 / .70 / .56 / .93 | .13 | .84 / .90 / .65 / .90 / .90 | .85 / .91 / .66 / .76 / .91 | .85 / .90 / .69 / .41 / .93 |

Controls, the list's cued hits at k = 2, 5, 10, 25: no learning .31, .31, .30, .32; random feedback .31, .30, .30, .31; shuffled feedback .29, .29, .36, .54, with the honest credibility at .13, .14, .19, .29.

| Prediction | Result |
| --- | --- |
| P1.1 learned .90, unlearned .31, random within .03, credibilities as derived | PASS: .903 to .907; .297 to .331; within .013; honest 1.00, liars .19 to .21 |
| P1.2 shuffle: honest credibility .13, .16, .20, .33; L's cued hits .26, .30, .36, .51 | MISS on one number: .294 at k 25 against .33 ± .03; the rest within band. After the fact: the closed form left out the 10° per-trial noise; two resources of one regime agree within 20° with probability .843, giving .126, .148, .184, .294, each within .01 of the run. The reduced model had .300 and I froze the closed form instead |
| P1.3 leader at chance | PASS: .116 to .127 |
| P2.1 S_all table ±.05 and the three orderings | PASS: largest gap .013; k 2: R2 > L ≈ R4 > R8; k 10: every ring above L, R2 ≥ R4 > R8; k 25: rings within .009, each .16 to .17 above L |
| P2.2 S_first = S_settled × P: .90, .77, .42 | PASS: .90, .74 to .77, .41 to .43; first over settled .99, .81 to .84, .44 to .47 against 1.00, .86, .46 |
| P2.3 blank hits: L none; rings per table ±.07 | PASS: L 0 everywhere; largest ring gap .035 |
| P2.4 settled trials: R2 within .01 of L; R8 above L by .02 to .03 | MISS in part: R2 − L +.004, −.001, −.000 (the main clause); R8 − L −.019, +.011, +.025 at k 5, 10, 25: the averaging advantage held at k 25 only. The frozen table itself had R8 .89 against L .90 at k 5; the prose generalized from k 10 and 25 |
| P2.5 chair follows the G 8 ring within .10 | MISS on one measure: blank hits within .05 and S_all within .10 (except +.10 at k 2), but S_first .54 to .57 against .41 to .43 at every k. By the re-lock law the chair turns like a ring at V 5.8 to 6.0, between gains 4 and 8. K4 did not fire (.129 at k 10) |
| P2.6 every ring keeps winding 1 at every trial | MISS: the G 2 ring left winding 1 in 1 to 11% of seeds per condition, for about .2% of trials on average (mostly one trial), and in two shuffle seeds for most of the run; G 4 in 2 seeds of 1600; G 8 never; 98.3% (Test 1) and 98.7% (Test 3) of ring seeds kept it throughout. After the fact: an opposing patterned cue lowers the pattern's amplitude at every part at once, and at G 2 (standing amplitude .94) an opposing input of 0.43 or more leaves no positive fixed point (1.89 at G 4, above 3 at G 8); the pattern collapses and re-forms along the cue, and the turn passes through 0 on the way. The unlearned net cue reaches .53, the learned .39. A remaking, not a capture; the hit rates were as predicted |
| P3.1 independent liars: raw .80, corrected .90, gate .98; gate advantage ≤ .10 | PASS: .805, .907, .981 (L) and .805, .906, .982 (R2); R8 .792, .845, .890; advantage .074 to .076 |
| P3.2 coalition: raw .59, corrected .76, gate .99; gate advantage ≥ .20 | PASS: .606, .774, .989 (L) and .608, .775, .989 (R2); R8 .631, .749, .888; advantage +.214 and +.215 |

Kill conditions: K1 at most +.004; K2 .614; K3 .433 and .900; K4 .129; K5 +.214; K6 .127; K7 +.585; K8 +.003. None fired.

**Read after the fact.**

1. Learning carries the hit rate here, and the controls bite: unlearned .31, random .30, learned .90. The shuffle collapsed hits where the world is fast (.29 at k = 2 and 5) and not where it is slow (.54 at k = 25), as derived once the per-trial noise is in the formula.
2. The type of center sets the tempo at which persistence pays. The fast ring beats the list at every regime length (+.085 at k = 2, +.16 at k = 25); the slow ring loses to the list in a fast world (.48 against .68 at k = 2) and draws level with the fast ring in a slow one. First-trial hits follow S_settled × P at every gain and k. On settled trials the fast ring and the list decide alike within .005 at every k; what the slow ring adds there is averaging, .025 at k = 25 and nothing at k = 5. "The 0 buys persistence and smooth corrigibility, not the decision" held in a task where both have a price.
3. The chair is in effect a ring of intermediate gain: blank hits as G = 8, re-lock as V about 5.9. Its memory loop has its own rate, so the Experiment 12 reading (a node its parts read back is a memory) holds, and the band "like the G 8 ring" did not.
4. Dropping sources at chance is worth .07 against independent liars and .21 against a coalition; Experiment 12's raw credibility loses .10 and .17 against the corrected form. A coalition of liars is answered by a gate, not by weights: a boundary job, not a path job.
5. The weak ring's turn is not kept at every trial under patterned cues that oppose it, by a collapse and re-forming that the one-variable heading law cannot see. Experiment 12's winding claim was made with at most two sources and holds there; with four it needs an amplitude margin, which G = 4 and 8 have and G = 2 barely has.

## Revision history

- 2026-11-07 v1.1: results of the run appended; predictions unchanged; the 10° noise factor missing from the shuffle derivation noted.
- 2026-11-07 v1.0: design and frozen predictions; nothing run. The lie rate and the number of liars were chosen with the reduced model before any full-model run, as section 4 records.
