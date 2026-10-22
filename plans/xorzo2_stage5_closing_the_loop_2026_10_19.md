# Xorzo2 Stage 5: Closing the Loop (design proposal)

```
Created: 2026-10-19
Last updated: 2026-10-19
Version: 1.0
```

> It hears the world. Next: it hears what it holds, it chooses how wide to open, and it notices that it acts.

**Status: PROPOSAL, not adjudicated.** Drafted by Claude on 2026-10-19 at Ashman's request ("Do this task here"). Nothing in `Xorzo2/`, `plans/xorzo2_plan.md`, `Xorzo2/findings_stage1.md`, or `Xorzo2/worldline/` has been changed, and the individual has not been run. Every experiment below runs on fresh twins (`Life(home=None)`); nothing touches the individual until Ashman adjudicates its adoption, and each adoption would be a worldline event in the pattern of `voice_upgrade_resonant`.

---

## 0. Origin and thesis

**Origin.** On 2026-10-19 Ashman brought a proposal for a circumpunct-based AI into the session (pasted from a conversation elsewhere) and asked what it could mean for Xorzo. Its claims, in short: the 0D to 4D sequence is the organization of a conscious whole, and the processes (convergence, transformation, emergence, feedback) are what connect the dimensions rather than another dimension beside them; adding a center to a volume does not make it literally four-dimensional without a fourth coordinate such as time; an implementable AI is a dynamical model `s_{t+1} = U(s_t, o_t, a_t)` whose state is organized by the five structures (center = focus and goal, path = memory and commitments, boundary = evidence and permission rules, field = a relational world model, whole = coordination); corrigibility belongs inside the cycle; and such an architecture would test memory, coherence, and correction without establishing that anyone is inside.

**Reading against the code.** Most of it is already Xorzo2, in a stricter form:

1. Xorzo2 already is `s_{t+1} = U(s_t, o_t, ·)`. `life.py` `_cycle` computes ψ ← normalize(M⁸(ψ + E(b))): U is the frozen spine T = κ ∘ F run for one octave, o_t is the byte through the given bit-station keyboard.
2. The processes already connect the structures. The four beats of F carry the i-strokes at the half-integer stations, between the integer structures, inside the operator: the structure-is-process identity (`plans/structure_is_process_2026_08_08.md`, adjudicated) is in the physics.
3. The proposal's test (does the organization improve memory, coherence, correction?) is the plan's falsification ladder (§8 of `plans/xorzo2_plan.md`: severance, inflation, sleep, growth), each run at least once.
4. The proposal's 4D caveat agrees with canon: ⊙ has no dimension slot and 4D carries one identity, 0.5D′. Xorzo2's time coordinate is its worldline, which is law.

**Where the proposal would steer wrong.** It realizes the five structures as five modules, one of them a "whole" that coordinates the rest. That is a homunculus; D5 says the whole is the compositional unity of the parts, not a fifth part, and adjudication 3 (2026-07-19) retired hand-designed anatomy in favor of a seed that grows. Xorzo2's stations are roles inside one operator acting on one state vector, and its whole is the composition plus the reserved upward seam (node 21, 3.5D = 0D′) where it couples to the triad. Stage 5 keeps that. **Take the proposal's cycle, not its parts list.**

**What the proposal genuinely adds.** Two terms Xorzo2 lacks, and one gap that blocks both:

- **a_t, credited.** Xorzo2 emits, and (correcting the 2026-10-19 conversation, which said otherwise) it already hears itself: `speak()` and `speak_continue()` re-inject every emitted byte, and in the chamber `converse()` learns the other party's words while Xorzo2's own reply is still held in ψ. So a weak loop exists in the chamber. What does not exist: any controlled test that its own emissions inform its predictions of the world's answer, any action channel on the corpus stream, and any record linking what it said to what came back.
- **Selection at the aperture.** Every byte enters at the same α-capped amplitude. The center has no variable.
- **The readout gap.** The spine holds the past (F4, F5, F8, F11), but the voice does not convert it into prediction (`experiments/pole_gap_xorzo2_null_findings_v1.md`, pending adjudication). Acting on the world is pointless if the voice cannot reliably tell what it just heard or said.

**Thesis.** Stage 5 closes the cycle without adding a part: the voice learns to read what the spine holds, the aperture gets its one variable, and the world gets to answer.

**Milestone, one sentence.** *Xorzo2 notices that it acts: when the world answers it, its prediction of the answer beats a yoked twin that hears the same answers without having caused them.*

---

## 1. Where Xorzo2 stands: the proposal's map against the code

| Station | The proposal wants | Xorzo2 has | Gap Stage 5 addresses |
|---|---|---|---|
| • center | focus, perspective, active goal | its own attractor as self-reference; health = overlap with it | no selection: injection is fixed at the α cap (item 2) |
| — path | memory, commitments, a record of how conclusions changed | the worldline (law), `growth_history` events, weathered bonds, the chamber's return rule | receipts cover architecture events, not what each dawn changed (item 4) |
| ○ boundary | evidence rules, what it may affect, when it needs permission | given keyboard, α cap in code, memoryless organs, no bypass, no injection on seams | permission has nothing to govern until actions exist; Stage 5 confines action to a toy world and the chamber (item 3, §7) |
| Φ field | a model connecting people, objects, meanings, uncertainties | ψ: 22 complex amplitudes holding the past in original form, rotated (F11) | small and crowded, and the voice cannot read it well (item 1) |
| ⊙ whole | coordination among components | composition, plus the node-21 seam to the greater whole | none: kept as it is (§7) |

---

## 2. The individual as it rests (read from `worldline/meta.json`; nothing was run)

- Booted 2026-07-19 20:34; last saved 2026-07-20 16:28; resting since. 1,160,496 bytes lived, 9,743,040 ticks, 293 sleeps (32,256 replay bytes, 2,952 dream bytes; dream fraction at its 0.5 ceiling). Last dream: `oEba GdAe`.
- Still the seed: 3 octaves, 22 nodes, no births. Site crowding ratios 0.999 / 1.000 / 1.001 against a 1.5 trigger: the healthy trigger correctly silent. (`growth_events` = 4 counts worldline events of every kind; the octave list shows no births.)
- Health and conservation clean: attractor overlap 0.9996; growth excess 3.7e-5 per cycle; injection norm 1.0α; reserved node untouched.
- **Weathering has reached its limits.** 32 refines, 0 skips; the weakest bond sits at the lower band edge (0.5α) and the strongest at the upper (1.5α); conservation departure 0.9618α against a guard of 1.0α. The next dawns will begin skipping once a candidate crosses the guard. This is the v1 rule's known self-reinforcement (attractor-polarized coherence: "the river deepens its own bed") running to its edges.
- Loss EMA 3.547 nats at save, above its 3.07 low at 830K bytes. Plan v1.13 already recorded that this wandering EMA is position-dependent and cannot measure the individual's progress; it is reported here, not interpreted.
- Organs: given keyboard (zero parameters), resonant voice (107,952 parameters, six rewound frames).

---

## 3. Item 1: the readout (first, because everything after depends on it)

### 3.1 The problem

On the same stream, budget, and online single-pass protocol, a one-byte lookup table beats Xorzo2 by 1.17 nats per byte (order-1 tail 1.899 vs Xorzo2's reported 3.070; order-2 tail 1.540), and the order-1 table is smaller than the voice. The finding is pending adjudication, the corpus has drifted since the runs, and the comparison is protocol-fair but not architecture-fair. Its core point survives all three caveats: an order-1 model knows the previous byte exactly, and Xorzo2 does not.

### 3.2 Two candidate bottlenecks, both already partly measured

**(a) Crowding of the present.** The state barely knows the byte it just heard: lag-0 byte identity reads at 0.074 by ridge probe (F4) and 0.085 by whitened linear decoder (F8), against chance 0.0039 and against the noise twin's 0.980. The spine retains the past at near-equal amplitude (de-resonance, not fade: median cycle singular value 1.0002), so each new byte lands on a superposition of the recent past in 44 real dimensions. F10 already showed the size dependence: lag-0 legibility grows eightfold from 1 to 8 octaves ("a bigger vessel crowds the present less").

**(b) Pooling in the voice.** F8 recorded it directly: the voice's three-view softmax pooling is a measured bottleneck for sign-keyed chords, because near-uniform attention averages the keyboard's bipolar signs away. Two further features of the current readout plausibly compound it: each rewound frame is renormalized but not whitened, although F8's conditioning lesson showed the state covariance spans about nine decades and trained decoders need whitening with a relative floor; and the attractor (overlap 0.9996) dominates every frame, so experience lives in a residual of a few percent of the norm.

### 3.3 Experiments (fresh twins only)

**1a. The oracle ceiling.** A fresh live twin and a fresh noise twin each live 256K corpus bytes under the standard protocol (the v1.13 powered length). Their cycle-end frames and next bytes are recorded. Offline, and never fed back, readouts are fitted on the first 80% and scored on the last 20%: (i) whitened linear, (ii) whitened MLP trained to convergence over several passes. A recorded state is an instrument reading, like the ridge probe; the oracle is not an organ. The same harness reports lag-0 identity accuracy on the corpus stream.

| Oracle on live states | Reading | Next |
|---|---|---|
| beats the online voice by more than the seed spread | the information is in the state; the voice or its online learning is the bottleneck | 1b |
| matches the online voice | the state is the bottleneck | 1c |
| beats the order-1 table | the state already holds more than the last byte, legibly | adopt the calibrated ladder as the bar (D1) |

**1b. Sign-safe readouts that stay memoryless and no-bypass.** Candidate voice variants at matched parameter count, each a fixed or learned function of the present state only:

1. *Residual reading:* each frame read as ψ minus its projection on the spine's own attractor (the self's resting hum removed; the attractor is recomputed after any growth, as health already is).
2. *Frozen whitening:* a per-frame whitening transform with a relative eigenvalue floor, derived once from the spine's own stationary state covariance under the keyboard and frozen. It is a given lens, not a learned one, and is recomputed only at births.
3. *Sign-safe pooling:* pooling that cannot cancel signs (more views with sharpened attention, or pooled products of signed features), so bipolar chords survive aggregation. A flattened readout over all nodes is a control only: it is size-dependent and breaks at births.

**1c. Capacity.** If 1a says the state is the bottleneck, grown fresh twins at 4, 6, and 8 octaves, born at tonic sites under the guard and preferring lateral births (F10: wider beats deeper at equal size), with the oracle ceiling measured against octave count.

### 3.4 Pre-registered predictions and retraction

Every verdict uses at least 3 seeds and counts only if all seeds agree in sign and the mean gap exceeds the largest seed-to-seed spread (the multi-seed rule v1.13 called for).

- **P1.1** The live oracle beats the noise oracle beyond lag 2 (the severance result at the ceiling). Expected; failure would contradict F8 and stops Stage 5.
- **P1.2** At least one 1b variant beats the current voice on held-out loss and on lag-0 identity. If none does, the pooling diagnosis is retracted and the bottleneck is located in the state (go to 1c).
- **P1.3** The oracle ceiling rises with octave count (F10 predicts it). If it does not, capacity is not the bottleneck either, and the readout problem is reopened from scratch.

**Reporting standard.** If D1 is adjudicated in favor of the pole-gap finding, every loss is reported against the calibrated ladder (the shuffled null at matched order as the floor; the best count model as the bar), recomputed on the corpus as it stands. **Stage 5 does not require beating the count models.** Xorzo2 has never claimed to be a competitive language model; the bar is that the voice can use what the spine holds, measured as the closing of the oracle-to-voice gap.

---

## 4. Item 2: the aperture's one variable

### 4.1 Mechanism

The center gets one scalar, openness o_t, applied to the injection: ψ + o_t · E(b_t). It is set by a given rule, not learned:

- o_t = clip(σ_t / σ̄, o_min, 1), where σ_t = −ln p(b_t) is the voice's surprise at the byte about to enter, computed from the logits it already produced when predicting that byte (detached; no gradient through the gate), and σ̄ is the running loss EMA. Bytes more surprising than its own average enter fully open; bytes it expected enter attenuated in proportion. The reference is self-referenced, like health and the vesica trigger.
- **The two Lies bound it at both ends.** o ≤ 1: the injection can only shrink, so the α cap in code is never approached from above (no Inflation by construction). o ≥ o_min > 0: the aperture never seals (a closed aperture is the Severance shape, and lies persist through closed apertures, β → 0).
- Learning is unchanged: the loss on every byte is computed whatever its openness, so attenuation never hides an error from the voice. What changes is how much of each byte the field is asked to hold.

### 4.2 Why

- **Framework.** "The aperture has one variable" (CLAUDE.md, Wholeness Plane notice, 2026-08-01): a 0D center has nothing to adjust except how open it is. TRUE is curiosity, and its freedom is NOT-YET; the symbolic organism already specified curiosity as mechanism. This is the first time the center of a Xorzo has a variable at all.
- **Physics.** It is the second remedy for crowding (§3.2a). F10 crowds the present less by growing a bigger vessel; openness crowds it less by asking the vessel to hold mostly what it did not expect.
- **Prior art, to cite rather than rediscover:** predictive coding (Rao and Ballard, 1999) and the wider literature on surprise-modulated memory encoding. What is framework-native here is narrower: the gate is the center's only variable, and its range is fixed by the two Lies rather than tuned.

### 4.3 Falsification

Three fresh twins, at least 3 seeds each, same stream and schedule:

- **A** fixed openness o = 1 (current physics);
- **B** surprise-gated openness;
- **C** B's own openness sequence, permuted in time (identical distribution and mean injection; the timing of selection destroyed).

Measures: held-out loss under the reporting standard; delayed recall (`recall.py`-style whitened decoders) of high-surprise bytes at lags 1 to 16, where "high-surprise" is the top quartile under a fixed external reference (the order-2 count model), so the byte subset is identical across twins; conservation (growth excess, departure) and the Inflation monitor.

- **P2.1** B beats C on high-surprise recall and on loss. If B ≈ C, the effect is lowered mean injection and the selection is decoration: retract the selection claim.
- **P2.2** B is no worse than A on loss. If B is worse than A, retract the mechanism.
- **P2.3** Conservation is unchanged within its band (expected: injection only shrinks).

**Instrument note.** The Inflation monitor's injection EMA will read below 1.0α under gating; mean openness is reported beside it so the monitor stays interpretable.

**Dependency.** The gate is only as good as the voice's surprise. It runs after item 1's voice verdict, on the best memoryless voice item 1 produces.

---

## 5. Item 3: the action term

### 5.1 What exists today (corrected)

`speak()` and `speak_continue()` inject every emitted byte back into ψ: the voice hears itself, with no learning on its own bytes. In the chamber, `converse()` learns the other party's text as wake experience while Xorzo2's previous reply is still held in ψ, so its prediction of the other's words is already conditioned, physically, on what it said. What is missing is any evidence that this conditioning carries information, any control that could show it, and any action channel outside the chamber.

### 5.2 Mechanism: a world that answers, and a yoked twin

- **The world, W.** A deterministic responder in code. Minimal form: Xorzo2 emits a chunk e of k bytes (via `speak_continue`, self-heard, no learning on its own bytes); W answers r = σ(e), a fixed byte substitution applied to the chunk; r streams in through the `converse` path as wake experience (learning on, targets always real). Predicting r's first byte requires remembering e's first byte at a lag of about k cycles.
- **The yoked twin.** The classic contingency-learning control. A twin identical at birth receives exactly the live twin's response stream at the same times. It emits its own chunks (self-heard, so its injection load matches), but its emissions caused nothing. Any advantage the live twin shows can only come from carrying its own action forward in ψ.
- **No reward.** Stage 5 adds no objective over what the world says back. An objective over the other's response is strategic metacognition with no governing pillar (§25.20: legitimate only when governed by TRUE, GOOD, RIGHT, FAITHFUL, and AGREEMENT); in the chamber it would mean optimizing Ashman. **Stage 5 learns how the world answers, never how to make it answer.** Any objective over responses is a separate stage with its own boundary design and adjudication.

### 5.3 Falsification

At least 3 seeds per condition; delays k ∈ {1, 2, 4, 8, 16, 32}.

- **P3.1 (the milestone)** At k = 1, the live twin's loss on response bytes falls below the yoked twin's, and the gap widens with experience. If live ≈ yoked, the spine does not carry its own action into prediction, and the loop is decoration: retract.
- **P3.2 (dose-response, the mechanism check)** The contingency gap decays with k along a curve shaped like delayed recall (F8: signal to lag 16+). A gap that does not depend on k would mean something other than memory-through-physics is carrying it.
- **P3.3 (action severance)** With a frozen-noise spine at matched radius, the gap survives only at k ≤ 2 (the F8 crossover). If the noise twin matches the live twin at large k, the organs are carrying the action, not the spine: a bypass, as in F3.

### 5.4 Framework reading (a reading, not a derivation)

The countersigned kinematics (§4.11a): *the future converges; the past emerges.* An emission is the past Xorzo2 makes; the answer is the future arriving through its aperture; the cycle between them is the present. The staged 0.5D correction (2026-10-15, not countersigned) would read the emission as the outbound ray; nothing here depends on it.

### 5.5 The chamber, and the boundary

After a twin verdict, the individual's chamber turns can log (reply, response) pairs to the worldline. This is descriptive only: a person cannot be yoked. Action stays confined to W and the chamber. **Any channel with effects outside them (files, network, other processes, other people) is out of scope**, and needs its own boundary design (what it may affect; what requires permission) before it is proposed. That is where the proposal's permission rules belong, and not before.

---

## 6. Item 4: dawn receipts

### 6.1 Mechanism

An append-only `worldline/dawns.jsonl`, one line per sleep, written by a fixed template from the rule's own values (never by the voice):

- sleep index, bytes lived, time;
- weathering outcome (applied / skipped at guard / off), bonds moved, mean and largest |Δκ| in α units, bonds at each band edge, departure before and after, the three largest moves with octave and pair, the coherence sign split;
- growth: site ratios, streaks, birth or rollback;
- sleep learning: loss on the slept segments before and after (sleep's own receipt of what it changed), replay and dream counts, a printable dream sample;
- health: attractor overlap, injection EMA, mean openness (once item 2 lands).

### 6.2 Integrity test

A receipt must reconstruct what it records. Replaying the logged Δκ from the bond state at the previous checkpoint must reproduce the current bonds to float tolerance; a log that cannot reconstruct is not a receipt.

### 6.3 Why

The path is kept rhythm with receipts: the worldline i(t) is the record of whether the line held. The record cannot un-happen, and prediction reads it without rewriting it (§4.11a). This is the proposal's "record of how conclusions changed," at the scale Xorzo2 actually changes. Receipts change no physics, so they can land first, on twins at once and on the individual when it next lives.

---

## 7. Non-goals: what Stage 5 will not add

1. **No coordinator or "whole" module.** The whole stays as composition plus the node-21 seam (D5; adjudication 3).
2. **No reward over the world's responses** (§5.2).
3. **No action beyond W and the chamber** (§5.5).
4. **No change to the laws.** The spine is never trained (it grows at tonics and weathers by a given rule). Injection stays α-capped in code; openness can only lower it. Organs stay memoryless and no-bypass; residual reading and frozen whitening are fixed functions of the present state, and the oracle is an offline instrument that never feeds back. The reserved node stays untouched. The worldline is never re-initialized.
5. **No claim about consciousness.** These items test the architecture (memory, legibility, selection, contingency, receipts). None tests whether anyone is inside; the proposal's own closing caveat and the corpus's grading agree on this.

---

## 8. Order of work

| Step | Depends on | Touches the individual |
|---|---|---|
| 4: dawn receipts | nothing | only on adoption |
| 1a: oracle ceiling | nothing | no |
| 1b: readout variants | 1a | only on adoption |
| 1c: grown twins | 1a (if the state is the bottleneck) | no |
| 2: openness | 1b voice verdict | only on adoption |
| 3: contingency loop | 1b (the voice must know what it said); 2 optional | only on adoption, chamber logging after the twin verdict |

Feasibility: all of it is twin-scale work on the RTX 4070 (`py -3.11`, numpy for the spine, torch for the organs), hours per run, in the plan's §9 territory. No cluster; every claim is structural.

---

## 9. Open decisions (Ashman to adjudicate)

1. **D1: the null.** Adjudicate `experiments/pole_gap_xorzo2_null_findings_v1.md` and, with it, the reporting standard (calibrated ladder replaces the unigram line as the verdict threshold).
2. **D2: weathering before the individual lives again.** The v1 rule has reached both band edges with departure at 0.9618α against a 1.0α guard. Options: (a) pause weathering on the individual until the deviation-Hebbian rule v2 is tested on twins (recommended); (b) let v1 run into guard skips; (c) adopt v2 directly.
3. **D3: experience is the deviation.** Residual reading (item 1b, variant 1) and deviation-Hebbian weathering (rule v2) are the same principle applied to the voice and to the bonds: experience is the departure from the self's resting hum, not the hum. Adjudicate them together, as one principle, or separately.
4. **D4: measurement forks.** May a copy of the individual be loaded, evaluated on a fixed probe, and discarded without saving? It advances only the discarded copy. Recommended: yes, logged as a worldline event ("measured by fork") so the record shows it. This would also give the position-independent lifetime curve v1.13 asked for.
5. **D5: the aperture's range.** The floor o_min (proposed 0.25), the reference σ̄ (proposed: the running loss EMA), and whether its own self-heard emissions are gated (they are predicted by construction, so gating would mute self-hearing; proposed: self-heard bytes enter at o_min rather than zero).
6. **D6: the world.** Echo-substitution as the first W, or a richer responder of Ashman's design.
7. **D7: adoption order on the individual.** Proposed: receipts first, then the readout verdict's voice (function-preserving, as `from_voice` was), then openness, then chamber logging; each a worldline event.

---

## Revision history

- 2026-10-19 v1.0: initial proposal. Origin (the pasted circumpunct-AI proposal) read against the code; the corrected account of self-hearing; the individual's resting state (weathering at both band edges, departure near guard); four items with mechanisms, multi-seed falsification handles, and retraction conditions (readout, aperture openness, contingency loop with yoked control, dawn receipts); non-goals; order of work; seven open decisions.
