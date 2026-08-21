# One Narrow Chain: Ontology to Experiment

**Status: session record, 2026-08-21. Commissioned by Ashman's directive: "What we need now is one narrow chain that begins with our ontology, passes through standard mathematics, produces a dynamical theorem, and ends in an experiment that could fail." This file IS that chain. Part I (the chain, the theorem with proofs, the Stage 0 declarations, the frozen Stage A design) is committed before any Stage 0 computation runs, per the standing pre-registration discipline. Part II (Stage 0 results) is appended after. Stage A awaits recorded data and Ashman's countersign.**

## 0. The chain in four sentences

1. **Ontology.** A bounded persistent whole must balance total convergence and emergence over its complete cycle, and it becomes dynamically stable when accumulated excess in either direction changes the next flow in the opposite direction (the constitutive principle, countersigned 2026-08-21, disposition 8); the pump is instantaneously off balance through the cycle and exactly balanced over it (the periodic corollary, same countersign); erasing accumulated seam displacement requires integral feedback (same countersign, third result).
2. **Standard mathematics.** Formalize the whole as a conserved-stock ledger with feedback: linear systems theory, the final-value theorem, and conditional expectations of linear stochastic systems; every mathematical step is a class S import with a textbook name.
3. **Dynamical theorem.** The Response Theorem: a whole that erases accumulated seam displacement must, on release from a held displacement, cross its baseline (overshoot), repay the accumulated displacement-time integral exactly, scale the repaid area linearly with hold duration with sign opposite to the hold side, and exhibit a perturbation response predictable from its resting fluctuations alone; a whole with only proportional feedback does none of these.
4. **Experiment.** Breath-hold trials against a respiration-belt volume ledger (the same instrument as Run 2), with four pre-registered predictions, each carrying a kill condition; Stage 0 (this date) characterizes the instrument on matched synthetic nulls with expectations declared below before running; Stage A (awaiting data) is the decisive perturbation study.

The experimental system is the corpus's own canonical pump instance: inhale the future, exhale the past (§4.11a). The chain tests whether the pump's closure discipline is physically real at a declared ledger.

## 1. Link one: the ontology (exact sentences used, and nothing else)

The chain draws on five countersigned commitments and no others:

- **A0 (conservation):** E = 1; all else is constraints. Operationally: the declared ledger closes; the stock changes only by the difference of its flows.
- **A2 (persistence) with ○ (boundedness):** the whole persists as a whole; its stock neither empties (Severance) nor inflates without bound (Inflation); throughput continues while it lives.
- **◐ = 0.5:** balance of the two channels (⊛ convergence as inflow, ✹ emergence as outflow) is the healthy operating point.
- **The constitutive principle (disposition 8, canonical wording):** "A bounded persistent whole must balance total convergence and emergence over its complete cycle. It becomes dynamically stable when accumulated excess in either direction changes the next flow in the opposite direction."
- **The periodic corollary and the integral-feedback result (disposition 8):** the pump is exactly balanced over its complete cycle, and erasing accumulated seam displacement requires integral feedback (memory of cumulative error).

Not used: the dimensional ladder, the constants grammar, T = 3, the octave arithmetic, the information layer. The chain is deliberately narrow; if it dies, it dies alone (§5 states the kill scope precisely).

## 2. Link two: the standard mathematics (class S imports, named)

Let M(t) be the declared stock, I(t) ≥ 0 and O(t) ≥ 0 its inflow and outflow, x = M − M* the displacement from the operating point, u = I − O the net flow. The ledger is ẋ = u (A0). Define the seam displacement z(t) = ∫ x dt (accumulated displacement-time; disposition 8's "cumulative error"). The constitutive principle's second sentence, read at its two accumulation registers, gives the minimal linear feedback architecture

    u = −k_p·x − k_i·z + w(t),    k_p > 0, k_i ≥ 0,

with w exogenous drive and noise. k_p is the principle's first register (excess accumulated in the stock changes the next flow oppositely); k_i is the second register (excess-time accumulated at the seam), which disposition 8 proved necessary for erasing seam displacement. The imports:

- **Linear ODE theory and the final-value theorem** (any control text; class S): stability regions, steady-state error. In particular: under a sustained load d, the proportional-only loop settles at x_∞ = d/k_p (offset), while any loop with k_i > 0 settles at x_∞ = 0 (no offset). Exact complete-cycle balance in the presence of sustained disturbance therefore REQUIRES k_i > 0; this is the periodic corollary's "exactly balanced" converted into an architecture claim by one standard theorem.
- **Conditional expectations of linear stochastic systems** (Doob; any SDE text; class S): for a linear system driven by stationary noise, E[state(t+s) | state(t)] follows the noise-free flow from state(t); the deterministic semigroup is identifiable from resting fluctuations.
- **The Jury/Routh stability conditions** (already verified in `plans/balance_attractor_dynamics_2026_08_20.md`): the discrete-time PI region, previously confirmed over 7900 gain pairs.

## 3. Link three: the Response Theorem

**Theorem (Response).** For the balance-regulated stock ẋ = −k_p·x − k_i·z + w, ż = x, k_p > 0, with equilibrium (x, z) = (0, 0):

**(a) Return.** With w = 0 the origin is asymptotically stable for all k_p > 0, k_i > 0 (continuous time); with k_i = 0 the x-dynamics is a first-order lag.

**(b) Crossing and exact repayment.** Take w = 0, an impulse displacement x(0) = A ≠ 0 with no prior seam debt, z(0) = 0. If k_i > 0, then ∫₀^∞ x dt = z(∞) − z(0) = 0: the total displacement-time integral vanishes exactly, so the trajectory must cross zero at least once, and the area repaid beyond the crossing equals the initial-side area exactly. If k_i = 0, then ∫₀^∞ x dt = A/k_p ≠ 0 and x never crosses zero.

*Proof.* ż = x gives ∫₀^T x dt = z(T) − z(0). For k_i > 0 the unique attracting equilibrium is (0, 0), so z(∞) = 0 and the integral is −z(0) = 0; a continuous x with x(0) = A ≠ 0 and zero total integral must take values of the opposite sign. For k_i = 0, x(t) = A·e^(−k_p·t), which is single-signed with integral A/k_p. ∎

**(c) Held-debt repayment scaling.** Clamp the flows for t ∈ [0, T_h] with the stock held displaced at x = A (a breath-hold: I = O = 0, so ẋ = 0), z(0) = 0. At release, z(T_h) = A·T_h. If k_i > 0, the post-release trajectory satisfies

    ∫_{T_h}^∞ x dt = z(∞) − z(T_h) = −A·T_h :

the repaid area is exactly the accumulated displacement-time, linear in hold duration, with sign opposite to the hold side. If k_i = 0 the post-release integral is A/k_p, independent of T_h. ∎ (same one-line argument)

**(d) Regression: rest predicts response.** With stationary noise w, the conditional mean of the future state given the present state follows the noise-free flow (class S import above). Hence a linear model identified from resting fluctuations alone predicts the ensemble-mean post-perturbation trajectory with no parameters fit to perturbation data.

**Generality note.** Parts (b) and (c) do not require linearity. For ANY feedback u = −f(x, z) whose closed loop makes (0, 0) globally attracting (any whole that erases seam displacement), ż = x forces ∫ x dt over the recovery to equal −z(release). The repayment identity is an architecture-level signature, not a linearity artifact; linearity sharpens only part (d).

**Corollary (the framework's committed side).** Canon's periodic corollary says the pump is EXACTLY balanced over its complete cycle; by the final-value theorem, exact balance under sustained disturbance requires k_i > 0. Therefore the framework predicts, for a healthy breathing whole at the ledger it actually regulates: the crossing (K1), full repayment ρ = 1 (K2), linear scaling in T_h with sign anti-symmetry by hold side (K2s), and rest-predicts-response (K3). A proportional-only whole (monotone return, no repayment, offset under load) is the rival the experiment can select.

Verification script: `experiments/narrow_chain_response_theorem_v1.py` (checks V1 to V4 below; results in Part II).

## 4. Link four: the experiment

The declared system-measure pair: **human resting breathing at the respiration-belt volume ledger**, the identical instrument to Run 2 (`plans/balance_breath_run_2026_08_21.md`): belt signal detrended, differenced, 5 s sign-split windows; convergence = inhaled volume rate, emergence = exhaled volume rate; b = C/(C+E).

### 4a. Stage 0 (this date): instrument characterization on matched synthetic nulls

Run 2 left one anomaly (freely fitted equilibrium 0.4915, shortest-lag CI (0.4854, 0.4972) excluding 1/2, with BIC preferring half-fixed at every lag) and one open vulnerability (a cyclic process can mimic restoration through windowed estimators; the lag-sweep guard passed, but no matched null was run). Stage 0 runs four synthetic breathers through the EXACT Run 2 pipeline (100 Hz synthesis; 30 s rolling-median detrend at 1 Hz; diff; 5 s sign-split windows; trials of 5, 8, 2.5 min; analyzer invocation frozen at lags 1,2,4,8, bootstrap 1000, seed 20260821, tolerances 0.02/0.05):

- **N1 (mechanical, duty-asymmetric):** raised-cosine breaths, per-breath closure exact (each exhale returns the inhaled amplitude), inhale ~1.6 s, exhale/inhale ratio ~1.5, amplitude cv 20 percent, timing cv 15 percent, all draws independent; NO feedback of any kind.
- **N1s (mechanical, duty-symmetric):** same with exhale/inhale ratio 1.0; isolates duty asymmetry.
- **N2 (mechanical + drifting stock):** N1 plus an independent Gaussian step of the end-expiratory level each breath (sd 10 percent of mean amplitude): the stock random-walks with no restoring feedback; the pipeline's detrend then does whatever it does.
- **N3 (PI breather, the framework's model):** N1 plus end-expiratory level actively corrected by proportional-plus-integral feedback on the volume displacement, gains inside the verified stability region, plus the same per-breath noise as N2.

**Pre-declared expectations (committed before running; a failed expectation is itself a finding):**

- **E1:** all four nulls pass finite-window accounting and balance (the pipeline near-guarantees closure).
- **E2:** N1, N1s, and N2 (no feedback) are classified restoring at the shortest lag (negative slope with CI). If so, "restoring" through this instrument does NOT discriminate homeostatic feedback from mechanical cyclicity, and Run 2's claim-3 evidence downgrades from "restoring signature detected" to "signature reproduced by a feedback-free null"; the downgrade will be recorded as an addendum pointer in the Run 2 record. If the nulls are NOT classified restoring, Run 2's signature carries content beyond cyclicity, and the chain says so.
- **E3 (the 0.4915 mechanism test):** the duty-asymmetric N1 fits an equilibrium below 1/2 and the symmetric N1s fits an equilibrium consistent with 1/2. If so, the Run 2 sub-half anomaly is instrumental (duty-cycle sampling bias), direction confirmed at the instrument level. If N1 sits at 1/2, the anomaly is not duty-mechanical and stands as physiological.
- **E4:** N2 (random-walking stock) is ALSO classified restoring after the pipeline's detrend: if so, the passive pipeline cannot certify boundedness either, and the honest statement is that detrending manufactures local closure.
- **E5:** N3 (with feedback) is nearly indistinguishable from N2 (without) through the passive analyzer at these lags. If so, the passive-data ceiling is confirmed from below, and perturbation (Stage A) is established as the only decisive discriminator; that is the chain's central methodological claim.

Stage 0 has no kill condition for the chain; it characterizes the instrument. Its results bind Stage A's interpretation.

### 4b. Stage A (frozen design; awaiting recorded data and countersign)

**Subject and equipment.** Ashman (self-experiment) or any consenting healthy adult. A respiration belt at ≥ 20 Hz (chest strap, Go Direct/Vernier, BioHarness, or a phone accelerometer lying flat on the sternum as a tilt proxy; the pipeline decimates to the Run 2 grid). Safety: seated, no prior hyperventilation, holds released at any discomfort, contraindicated for cardiovascular or respiratory conditions; all holds are everyday submaximal holds of at most 30 s.

**Session (one sitting, ~40 min).** 10 min quiet rest (baseline identification); then hold trials in pre-randomized order (seed committed with the data-collection script before the session): end-inhalation holds of 10, 20, 30 s (3 each) and end-exhalation holds of 10, 20 s (3 each), 15 trials, separated by ≥ 90 s recovery; then 5 min rest.

**Instrument decision frozen now (the detrend trap).** The Run 2 rolling 30 s median would subtract the very recovery under test. For perturbation trials, the baseline is the median of the 60 s immediately preceding the hold, held CONSTANT through the hold and 90 s of recovery. Rest segments keep the Run 2 detrend for comparability of resting estimates.

**Estimators.** Per trial: displacement x(t) (baseline-subtracted volume); hold side and amplitude A (mean displacement during hold); held area A·T_h; post-release signed area ∫ x dt over 90 s; repayment fraction ρ = −(post-release area)/(held area); crossing indicator (does x cross zero within 90 s). From rest alone: linear model identification (discrete second-order fit on the 1 Hz displacement) yielding a predicted mean recovery trajectory; conditional-drift slope and equilibrium exactly as in Run 2.

**Pre-registered predictions and kill conditions** (the framework's side is the corollary of §3; the rival is proportional-only):

- **K1 (crossing).** The trial-averaged recovery crosses baseline. Kill: the mean trajectory's bootstrap band stays on the hold side throughout 90 s AND fewer than half of trials individually cross.
- **K2 (repayment).** ρ > 0 with the pre-named bands: ρ CI entirely above 0.25 = integral feedback confirmed at this ledger; CI containing 0 = the integral claim is DEAD at the volume ledger; between = partial, declared underpowered, more trials required before any verdict. (Power for the band widths is rehearsed in Stage 0's V6 on the N3 breather.)
- **K2s (sign anti-symmetry, the sharpest edge).** The volume-ledger model predicts post-release areas of OPPOSITE sign for end-inhale vs end-exhale holds (repaying the displacement each side accumulated); the rival gas-debt-only model (CO2 chemoreflex with volume as mere actuator) predicts side-independent hyperpnea. Kill for the declared ledger: same-signed recovery areas on both hold sides with CIs excluding anti-symmetry.
- **K3 (rest predicts response).** The rest-identified model's predicted mean recovery matches the observed mean: declared statistics are the time-to-first-crossing ratio (must lie in [1/2, 2]) and normalized RMSE within twice the rest-model bootstrap band; kill requires BOTH to fail (guards against killing on noise).

**Honest risk table.** Post-hold ventilatory overshoot (hyperpnea) is established physiology, so SOME response is guaranteed; K1 alone passing is weak evidence. The genuine risks: K2's ρ at the VOLUME ledger is unknown and may be near zero (volume has no obvious debt memory; the physiological integrator is chemical); K2s may come out same-signed (gas debt dominating), which kills the volume-ledger reading specifically; K3 may fail on two-timescale grounds (mechanical vs chemoreflex dynamics). Failure of the expectations is the experiment working.

**The escape-hatch clause (binding).** If K2 or K2s or K3 kills the one-loop PI reading at the volume ledger, the constitutive principle survives only by retreating to a different declared ledger (e.g., blood-gas via capnometry) or a declared nested two-loop architecture. Either retreat is a NEW claim requiring a new Stage A; it may not be offered as a reinterpretation of this one. Nesting is not a rescue; it is a different experiment.

## 5. What failure kills, and what it does not

A Stage A kill at the declared ledger kills: the one-loop integral-feedback reading of the constitutive principle for breath-at-volume, which is the framework's first dynamical-mechanism claim placed at risk on a real system; and, if K2s selects the gas-debt rival, the identification of the belt-visible pump with the whole's regulated stock. It does not kill: A0 (an accounting convention), the boundedness-forces-balance theorem (mathematics), the rigidity and attractor theorems (proven), or the totals form of complete-cycle balance (near-tautological given boundedness, as the protocol already records). The chain is narrow by construction: one system, one ledger, one theorem, four numbered ways to lose.

## Part II: Stage 0 results

*(appended after the committed declarations above; nothing in Part I was edited in response to what follows; full receipt: `experiments/narrow_chain_response_theorem_v1_output.txt`, run this date at commit acec88b3)*

**Theorem verification: all four parts PASS.** V1: proportional-only never crosses, area A/k_p and load offset d/k_p to 1e-3. V2: PI crosses in underdamped, critical, and overdamped regimes with total area zero to machine precision (1e-15) and load rejected. V3: post-release area equals −A·T_h at all four hold durations, linear-fit slope −1.0000. V4: conditional means of the noisy system match the deterministic propagator across 36 state bins, worst deviation 1.49 crude standard errors.

**Stage 0 against the pre-declared expectations:**

- **E1 CONFIRMED.** All four nulls pass accounting and balance within tolerance.
- **E2 CONFIRMED, with force.** All three feedback-free nulls are classified restoring at the shortest lag with confident negative slopes (N1 −0.278, N1s −0.337, N2 −0.268; every CI below zero), AND all show the monotone weakens-with-lag pattern (ratios 0.067 to 0.090) that Run 2's §7 guard treated as the dissipative-relaxer signature. Run 2's real numbers (slope −0.322, ratio 0.080) sit inside the null range. The declared consequence executes: Run 2's claim-3 evidence downgrades from "restoring signature detected" to "signature reproduced by feedback-free mechanical cyclicity through this instrument"; addendum recorded in `plans/balance_breath_run_2026_08_21.md`.
- **E3 FAILED (the run's one surprise, and a finding).** The duty-asymmetric N1 fits equilibrium CI (0.4911, 0.5022), CONTAINING one half; the symmetric N1s also contains it. Duty-duration asymmetry at ratio 1.5 does not reproduce the Run 2 sub-half equilibrium. The candidate mechanism named in Run 2's Part II (duty-cycle sampling bias, duration form) is disconfirmed at the instrument level; the 0.4915 anomaly stands. Sharpening: of the five datasets now run through this instrument (three feedback-free nulls, one PI breather, one real), ONLY the real breathing triggered the sub-half detection. Remaining untested instrument-level candidate: within-phase flow-shape asymmetry (real inspiratory flow is shaped differently from expiratory); a declared variant could test it, and Stage A's own data will bear on it either way.
- **E4 CONFIRMED.** N2, whose stock random-walks with no restoration at all, is classified restoring after the pipeline's detrend. The passive pipeline cannot certify boundedness; detrending manufactures local closure. This binds all passive runs, Run 2 included.
- **E5 CONFIRMED.** N3 (PI feedback) and N2 (none) return identical verdict strings and overlapping slope CIs; the analyzer's own verdict for both is "observationally_restoring; perturbation_test_needed". Feedback presence or absence is invisible to the passive instrument at these lags. The chain's central methodological claim is established from below: **Stage A's perturbation protocol is the only decisive discriminator, and every kill condition of this chain lives there.**

**V6 rehearsal (rehearsal, not calibration).** The Stage A estimator suite works end-to-end on ground truth: rest-only identification recovers the gains (k̂_p 0.253 vs 0.30, k̂_i 0.0212 vs 0.03); crossing fraction 1.00; repayment ρ̂ = +1.09 ± 0.19 (end-inhale) and +1.08 ± 0.13 (end-exhale) against true 1, a small positive bias from noise and the finite 90 s integration, well inside the K2 band scale; se(ρ) with 9 end-inhale trials ≈ 0.065, so the K2 bands separate full repayment from zero by an order of magnitude if breath resembles the model at all; K3 crossing-time ratios 1.36 and 1.40, inside the declared [1/2, 2] band.

**Net position of the chain after Stage 0.** The theorem is verified; the instrument is characterized; the passive ceiling is now demonstrated rather than assumed (E2, E4, E5); the one standing empirical anomaly (0.4915) survived its leading deflationary explanation (E3) and waits on Stage A data. The chain is complete on paper and armed: what remains is a recording session and the four kills.

## Open decisions (Ashman to adjudicate)

1. Countersign the chain (the corollary's commitment that canon's side is k_i > 0 at the regulated ledger; the frozen Stage A design; the escape-hatch clause as binding).
2. Schedule the Stage A recording session (equipment on hand vs to acquire; self-experiment vs other subject).
3. Whether the Stage 0 findings (Part II) warrant the Run 2 addendum immediately or wait for Stage A.

## Files consulted

`plans/balance_attractor_dynamics_2026_08_20.md` (the constitutive principle, the integral-feedback necessity, the Jury region); `plans/balance_empirical_protocol_2026_08_20.md` v1.2 (three-claim separation, oscillator trap, clamp check); `plans/balance_breath_run_2026_08_21.md` and `experiments/balance_breath_report.json` (Run 2 numbers); `experiments/balance_breath_observations_v1.py` (the pipeline reproduced exactly); `experiments/balance_empirical_test_v1.py` (the analyzer, imported unmodified); CLAUDE.md §4.11a (the kinematics canon).
