# Architecture of Wholeness, Experiment 15: the line that rings

Status: v1.1, 2026-11-08. Design and frozen predictions (v1.0), written before the full chain was run; run the same day, results in the Results section at the end with everything read after the fact marked as such. Drafted by Claude at Ashman's "try it", after Ashman's reading of 2026-11-08 that the 1D line is a string that can resonate and that attention is its mode. Builds on Experiment 14 (`plans/architecture_experiment_14_resonant_attention_2026_11_08.md`), which put the frequency in the whole's turn and left the line static. The derivation tool is `experiments/architecture_experiment_15_reduced_v1.py` (closed-form modal model); the full experiment is `experiments/architecture_experiment_15_v1.py`.

## 1. What this tests, and what it does not

Canon has the string already, for nesting (§27.7m: a string fixed at both ends, modes f_n = n f_1, nodes as points admitted within one fixed length). Ashman's reading moves the same string to the attention axis: the line between the soul and what it reaches is a string, attending is ringing it at a mode, and the node of the mode is the 0 in the 1 of §1.2. Neither programme has tested a line that rings: the Life author's Experiment 4 had a string whose outputs were constants, and our Experiment 14 put the clock in the ring's turn with static couplings between parts.

This experiment builds the smallest line that can ring, a chain of parts fixed at two ends, and asks five questions the reading answers in advance: does a cue at a mode frequency excite the line and a cue between modes not; do two cues at two modes coexist on one line (the ring of Experiment 14 followed one or neither); does a 0 imposed in the line select and concentrate, by removing the modes that have no node there and doubling what remains; does a second line sharing a mode take up the first's vibration, and lose it when detuned (canon's lateral transparency); and how long does the line hold a mode after the cue stops. It does not test selection by the whole (Experiment 14 did), saturating parts (left out, section 8), or anything about consciousness. The linear chain is textbook physics; the point of building it is to state canon's claim as a mechanism with numbers, so that the next steps (a saturating line, a line inside a ring) have a measured baseline.

## 2. The model

A chain of N = 15 parts between two fixed ends (16 segments), unit wave speed, damping γ = .02, a point force A cos(Ω t) at part 5 (A = .01), white force noise of .002 per part, RK4 at dt = .05, settling until t = 400 and measurement over t = 400 to 600. Modes φ_n(k) = sin(nπk/16), ω_n = 2 sin(nπ/32): .1960, .3902, .5806, .7654 for n = 1 to 4 (ratios 1, 1.99, 2.96, 3.90; nearly harmonic). Quality ω_1/γ = 9.8; period of mode 1 32 time units; settling time 2/γ = 100. A 0 imposed in the line is a part held at zero displacement. Two lines are coupled by a spring κ = .04 between their parts 8 (the midpoint, which couples the odd modes only).

## 3. Measures

Displacement RMS at the driven part over the window; modal amplitudes a_n = (2/16) Σ_k x_k φ_n(k) and their RMS; the share of modal energy in the cued mode; for the hold, the envelope of mode 1 after the cue stops, in windows of one period.

## 4. Derivations (closed form, section 2 of the tool)

Steady state: a_n = F_n / √((ω_n² − Ω²)² + (γΩ)²), F_n = (2/16) A sin(5nπ/16). On a mode a_n = F_n/(γω_n); between modes 1 and 2 the response is the sum of two off-resonant tails. A part held at zero splits the chain: with the node at 8 the driven half has 8 segments and modes ω_2, ω_4, ω_6, ..., and the drive's energy no longer leaves for the other half, so the response at part 5 to ω_2 doubles (the modal force of the half is (2/8) against (2/16) with the same shape at part 5); with the node at 4 the driven chain is the right one of 12 segments, whose modes are 2 sin(nπ/24) = .261, .518, .765, so only ω_4 of the free modes survives, and it rises by 16/12. Two lines coupled at their midpoints share each odd mode through κ_n = (2/16) κ, which for mode 1 is .005 against the damping term γω_1 = .0039; the ratio of B's to A's mode-1 amplitude is the 2 by 2 solution per mode. Free decay of a mode is e^(−γt/2), half-life 2 ln 2/γ.

## 5. Tests and frozen predictions

Labels: Derived (follows from section 4), Guess (no derivation; noise and discretisation only).

| | Prediction | Label | Pass if |
| --- | --- | --- | --- |
| P1.1 | The sweep (step .01) peaks at .20, .39, .58, .77 | Derived | each peak within .01 of ω_n |
| P1.2 | RMS at part 5 on the modes over the mid-gap (Ω = .293): 44 at ω_1, 28 at ω_2 | Derived | within a factor 1.5 of each |
| P1.3 | Peak heights relative to ω_1: 1.00, .62, .02, .19 | Derived | each within .05 |
| P1.4 | Energy share of the cued mode: .998, .996, .863, .991 | Derived | each within .04 |
| P2.1 | Two cues at ω_1 and ω_2 together: each mode carries its single-cue amplitude | Derived | both ratios within .97 to 1.03 |
| P2.2 | Cross-talk: mode 2 under the ω_1 cue .069 of its own; mode 1 under the ω_2 cue .034 | Derived | each within .02 |
| P3.1 | Node at part 8: response at part 5 relative to free: .107 (ω_1), 1.99 (ω_2), 1.98 (ω_4); the sweep's first peak moves to .39 | Derived | ratios within 10%, peak within .01 |
| P3.2 | Node at part 4: .053 (ω_1), .067 (ω_2), 1.33 (ω_4) | Derived | within 10% (absolute .02 for the two small ones) |
| P4.1 | Lateral transparency, mode-1 amplitude of B over A: .787 at equal speed, .512 at 1.05, .366 at 1.10, .225 at 1.20 | Derived | each within .05 |
| P5.1 | Hold: mode-1 envelope halves 69 time units after the cue stops (2.2 periods); decay rate .010 | Derived | half-life within 10, rate within .002 |
| P5.2 | The decaying mode keeps its shape: mode 1 stays the largest mode until the envelope reaches the noise floor | Guess | argmax mode 1 throughout the fitted range |

Reading the table before the run. If the Derived rows pass, the reading is a mechanism with these properties: a line rings at its modes and not between them (P1), carries two modes at once (P2), is selected and concentrated by a 0 placed in it (P3), passes its vibration to a line tuned alike and not to one detuned (P4), and holds a mode for about two periods at this damping (P5). What the mechanism then lacks, against Experiment 14's ring: it does not choose. A linear line carries every mode its cues excite; choosing needs either a 0 placed in it (P3, which is the §1.2 reading made literal) or a whole with a clock (Experiment 14). Holding is the quality factor, not a turn's inertia.

## 6. What would count against the reading, and what against the design

Against the reading:
- K1. The RMS at ω_2 is under 3 times the mid-gap RMS: the line does not resonate at its modes in any sense that selects.
- K2. With the node at 8 the response to ω_1 stays above .3 of the free chain's: a 0 in the line does not remove the modes without a node there.
- K3. Two cues at once give either mode a ratio outside .8 to 1.2 of its single-cue amplitude, or cross-talk above .25: the line does not carry two modes at once.
- K4. Equal lines transfer under .5, or the line detuned 20% transfers as much as the equal one: sharing a frequency does not make the path between lines transparent.

Against the design:
- K5. The measured mid-gap RMS exceeds the derived .0035 by more than 2 times: the noise floor, not the line, sets the ratios of P1.2, and they are read against the floor after the fact.
- K6. The free chain's energy without drive grows or oscillates in the mean (RK4 at dt .05 against ω_15 = 1.99): the integrator, not the model, is being measured.

## 7. Run plan

`python experiments/architecture_experiment_15_v1.py 100`: 100 noise seeds; Test 1 a sweep of 81 frequencies plus the four modes and the mid-gap; Test 2 three conditions; Test 3 the two node positions with three cues and a sweep with the node at 8; Test 4 four speeds of chain B; Test 5 one run with the cue off at t = 400. CSVs to `experiments/architecture_experiment_15_results/`. Grading by the table above, written into the Results section with everything read after the fact marked.

## 8. What is left out

Saturating parts (a line whose restoring force is tanh), which is where superposition would fail and where the comparison with Experiment 14's ring belongs; a line inside a ring (the crossing of the two programmes); a moving cue frequency (the tongue of a line is γ and was not swept); the dependence of the fundamental on length other than through the imposed node; noise other than white force noise.

## 9. Prior art the result will be read against

The damped driven string and its Lorentzian modal response are elementary (Rayleigh's theory of sound; any text). The imposed node is the fretted or stopped string. Coupled strings sharing a mode are sympathetic resonance (the aliquot strings of a piano, the tanpura). All from memory and unchecked for this document. Within the series: the nesting string of §27.7m; Experiment 14's clock in the turn and its two-cue result (the coupled organism followed one cue in 100% of seeds, the list the bisector); the Life author's note of 2026-11-08 and their Experiment 4, whose string was a removable constant.

## Results (run 2026-11-08, 100 seeds; everything after "After the fact" was written after seeing the numbers)

Code `experiments/architecture_experiment_15_v1.py`; CSVs and logs in `experiments/architecture_experiment_15_results/`. Two runs died on indexing slips before any test printed. The third printed Tests 1 to 4 and crashed in Test 5 on a window-indexing slip (`run_2026_11_08.log`); Test 5, repaired, and a noise-floor measurement (Test 0, added) were then run alone at the frozen noise (`run_2026_11_08_tests_0_5.log`). Rule changes before the run: none. Tool changes after the first numbers: Test 5's windows repaired, Test 0 added, tests made selectable by argument.

**Tally at the frozen noise (.002): 3 PASS, 7 MISS, 1 not measured.** K5 fired: the noise floor at part 5 without drive is .0174 against the derived mid-gap signal of .0035, five times, not two. No kill condition against the reading fired: K1 (5.3 at ω_2 against 3), K2 (.140 against .3), K3 (ratios 1.013 and 1.003, cross-talk .11 against .25), K4 (.766 against .5, and .236 at 20% detuning). K6 was not tested.

| Prediction | Result | What held, what did not |
| --- | --- | --- |
| P1.1 | MISS (partial) | Peaks at .19, .39, .60, .76: three within .01, mode 3 off by .02 (its signal, .019, equals the floor). |
| P1.2 | MISS | 8.5 and 5.3 against 44 and 28: the mid gap (.0190) sits on the floor (.0174). |
| P1.3 | MISS (partial) | 1.00, .63, .12, .22: three within .05, the mode 3 height is the floor. |
| P1.4 | MISS (partial) | .993, .956, .305, .756: modes 1 and 2 within .04, modes 3 and 4 not. |
| P2.1 | PASS | Two cues at once: 1.013 and 1.003 of the single-cue amplitudes. |
| P2.2 | MISS | Cross-talk .111 and .104 against .069 and .034; with the floor removed in quadrature .072 and .055. |
| P3.1 | MISS (partial) | Node at 8: .140 (pred .107), 1.966 (1.99), 1.723 (1.98); the sweep's first peak at .39 as predicted. |
| P3.2 | MISS | Node at 4: .081, .119, 1.159 against .053, .067, 1.33. |
| P4.1 | PASS | B over A: .766, .502, .360, .236 against .787, .512, .366, .225. |
| P5.1 | PASS | Envelope by period after the cue stops .157, .115, .085, .062, .046, .035: decay rate .0094 per time unit (derived .010), half-life 74 (derived 69). The script's printed 112 is its one-period sampling grid. |
| P5.2 | not measured | Only mode 1 was stored during the hold (a defect of the tool). |

**Reading, before the fact (section 5), as it stands.** The large-signal claims all hold: the line carries two modes at once, passes its vibration to a line tuned alike and not to one detuned (.77 at equal speed, .24 at 20%), holds a mode for about two periods, and a 0 placed at its midpoint doubles the response at the mode that has a node there and moves the first peak to the second mode. The small-signal claims (what happens between modes, at the weak third mode, and to the modes a placed 0 removes) could not be read at this noise.

**After the fact.**
- The floor. Force noise .002 per part produced a displacement floor of .0174 at part 5 and modal floors of .016, .009, .006 and .004 for modes 1 to 4: five times the derived mid-gap signal and about the amplitude of mode 3 (.021). Every miss is a clause whose derived signal is at or below the floor; every clause with a signal above .05 passed. Tests 0, 1 and 3 were rerun at a quarter of the noise (floor .0044; `run_2026_11_08_after_the_fact_sig0005.log`, CSVs tagged `_sig0.0005`): peaks .19, .39, .58, .76 (all within .01); on-mode over mid-gap 27 and 16.7, which become 41 and 25 once the floor is removed from the mid gap in quadrature (derived 44 and 28); heights 1.00, .62, .04, .19; shares .998, .993, .761, .972; node at 8: .111, 1.991, 1.962; node at 4: .0559, .0725, 1.318; first pressed peak .39. Against the frozen bands that is every clause of P1.1, P1.3, P3.1 and P3.2 passing, P1.2 passing after the floor correction, and P1.4's mode 3 (.761 against .863) still floor-limited. The derivation was right; the frozen noise was set without computing the floor it would produce, which K5 was written to catch and did.
- Cross-talk at the frozen noise, floor-corrected: .072 (derived .069) and .055 (derived .034); the second is still off by .02, the mode-1 floor being the largest and not removed exactly.
- The hold is the quality factor: 2.2 periods to half amplitude, γ exactly. Experiment 14's stiff ring held a moving target for trials by the inertia of its phase; the line holds a mode for cycles, and the number is its damping.

**What this adds to the Theory of Wholeness, pending Ashman's reading.** Attention as the mode of the line and attention as a 0 in the 1 (§1.2) are one picture: the standing wave is nodes in the string, and a 0 placed in the line is at once the selection (it removes every mode without a node there) and the concentration (it doubles what remains). The line resonates but does not choose; choosing needs the placed 0 or the whole's clock of Experiment 14. Lateral transparency (canon's two souls at one frequency) is sympathetic resonance with the derived falloff. The 0.5D correction's ray and this string meet: the direction of focus is the ray, the held mode is the string.

## Revision history

- 2026-11-08 v1.1: results appended (100 seeds); Test 5 repaired and a noise-floor test added after the first run; the quarter-noise rerun recorded after the fact.
- 2026-11-08 v1.0: design and frozen predictions from the closed-form modal model; not yet run.
