# Experiment: A Cross-Domain Transfer Test of the Pole Gap Schema

```
Created: 2026-07-27
Last updated: 2026-07-27
Version: 1.0
```

*Section draft for "The Pole Gap" (the parent essay and its attack document are still chat-side). Companion code: `pole_gap_transfer_v1.py` (deterministic seeds; all numbers below reproduce exactly; re-verified 2026-07-27 under Python 3.11 / NumPy 2.4.0). Interactive companion: `../docs/the_pole_gap_live.html`, which runs the same two poles live on a Rule 30 ring and separates the floor's existence from its discovery. Method and burden of proof per the attack document: one piece of reasoning must move between fields because the schema identifies them, or the unification claim downgrades honestly.*

---

## 1. The claim under test

The schema asserts that randomness is never a property of a process but of a projection: a gap between an inclusion-pole (the full state) and an integration-pole (an observer of a many-to-one image of it), measured per observer class. If that is right, then Yao's equivalence (cryptography's foundational result that *next-bit unpredictability* and *indistinguishability from uniform noise* are the same property of a bitstream relative to an observer class) cannot be a fact about cryptography. It must be a law of pole gaps as such, holding for physical and dynamical projections exactly as it holds for pseudorandom generators, with the entropy chain rule playing the role that the hybrid argument plays in the computational setting.

Stated as a correspondence:

| Cryptography | Pole-gap schema | Statistical physics / dynamics |
|---|---|---|
| distinguisher | test within an observer class | k-local experiment on a source |
| next-bit advantage | per-step prediction deficit | conditional-entropy deficit of the projected process |
| hybrid argument | chain rule of the gap | block-KL decomposition |
| security parameter | pole gap magnitude | opacity of the projection |
| "secure PRG" | maximal gap for the class | source indistinguishable from noise by any k-local test |

For the *statistical* observer class (all order-k tests), the equivalence is exact mathematics: for an empirical k-block distribution P_k, KL(P_k‖U_k) = k − H(P_k), which by the chain rule equals the sum of per-step conditional-entropy deficits; Pinsker then bounds any test's advantage, TV ≤ √(KL · ln 2 / 2). This is the "classical shadow" of Yao's theorem. The schema's prediction is therefore two-sided: in the statistical class the coupling must hold *with the specific quantitative constants*, across domains and at finite sample, where estimator pathologies can and do break naive analyses; and in computational classes (where chain rules for pseudoentropy are known to be subtle) the equivalence carries irreducible content, marking the schema's frontier rather than its failure.

## 2. Design

Five bitstreams of N = 300,000 from four fields, evaluated by one observer class (order k = 12 statistics): a fair coin (control; OS-grade RNG), the center column of Rule 30 on a 101-cell ring (deterministic physics-flavored substrate; the projection is the convergence stroke π, a 101→1 map), the logistic map at r = 3.8 thresholded at 1/2 (chaos), a two-state Markov chain with stay-probability 0.55 (subtle statistical structure), and an 8-bit LFSR (a deliberately broken pseudorandom generator).

Two instruments per stream. The prediction side is a prequential Krichevsky-Trofimov estimator: it prices every bit before that bit arrives and pays the log-loss, so sparse contexts cannot counterfeit certainty; its per-step loss is the observer's honest conditional entropy plus a learning tax, calibrated by the control. The distinguishing side is the full k-block statistics: KL from uniform, total variation, and chi-square per degree of freedom.

Falsifiable predictions. P1 (coupling): the two alarms ("prediction beats chance" and "a k-block test separates the stream from noise") fire together or not at all; a single decoupled cell falsifies the transfer at finite sample. P2 (constants): measured TV obeys the Pinsker bound computed from measured KL on every stream, crypto or physical. P3 (audit power): the coupling requirement must be strong enough to detect an inconsistent entropy estimate if one exists in our own prior work.

## 3. Results

| stream | KT H(b\|ctx₁₂) | acc % | KL₁₂ (bits) | TV bound | TV meas. | χ²/df | coupling |
|---|---|---|---|---|---|---|---|
| fair coin (control) | 1.0368 | 49.94 | 0.0098 | 0.0583 | 0.0464 | 0.99 | neither |
| Rule 30 center | 1.0369 | 49.89 | 0.0101 | 0.0591 | 0.0469 | 1.02 | neither |
| logistic r = 3.8 | 0.6377 | 74.25 | 3.8983 | 1.1624 | 0.9160 | 1348.3 | both |
| Markov p = 0.55 | 1.0293 | 52.12 | 0.0854 | 0.1721 | 0.1375 | 9.03 | both |
| LFSR-8 | 0.0008 | 99.99 | 7.0457 | 1.5626 | 0.9924 | 9606.0 | both |

The decoupled cell is empty. The Pinsker bound holds on all five streams. The coupling tracks magnitude, not merely presence: the Markov chain's whisper (52% accuracy, χ²/df = 9) and the LFSR's scream (99.99%, χ²/df = 9606) sit on the same curve. Rule 30 is indistinguishable from the control to four decimal places on the prediction side, and its measured KL₁₂ (0.0101 bits) matches the finite-sample floor exactly: the expected plug-in KL of a *truly uniform* source at this sample size is (2¹² − 1)/(2N ln 2) ≈ 0.0098 bits, which is where both the coin and Rule 30 sit. Within the order-12 class, Rule 30's deficit is consistent with zero and bounded above by ~0.001 bits/step.

## 4. The audit: the transfer's first casualty was our own number

An earlier session in this project reported the Rule 30 center column's entropy rate as ≈ 0.863 bits/symbol, from a naive block-entropy difference H(16) − H(15) at 200,000 samples. The coupling requirement executes that number. If the per-step deficit were really 0.137, the chain rule forces KL₁₂ ≈ 12 × 0.137 ≈ 1.65 bits and the chi-square must scream. Measured, under the original conditions: KL₁₂ = 0.0149 (implied deficit 0.00125 bits/step), χ²/df = 1.01: silence. The post-mortem is standard estimator pathology: at m = 16 the block coverage was 95.4%, and undersampling bias dragged the naive rate to 0.8644; the Miller-Madow correction recovers 0.9720; the prequential ledger, whose overhead is calibrated by the control, is consistent with a class-relative gap of 1.000 bits/step. Rule 30 pays full price to this observer class (it is maximally opaque, not 86% opaque), and the erroneous figure was published within this very project by its authors, then caught not by inspection but by the transferred consistency requirement. A taxonomy cannot catch errors; only a structure with consequences can. We report the mistake rather than silently correcting it because the catch *is* the result.

## 5. Exported corollary: a detection-cost bound for physical sources

Cryptography reasons about how much observation an adversary needs; experimental physics rarely states the mirror-image question (how long must one watch a source before claiming its randomness is or is not real) in those terms. The transfer supplies the bound: a G-test on the observer's statistics crosses a fixed significance threshold when accumulated evidence 2n·KL reaches it, so the detection step n* scales as the inverse per-step deficit, with predicted constant n*·δ ≤ 10.83/(2 ln 2) ≈ 7.8 (bits) at the p ≈ 0.001 level.

| p_stay | deficit (bits/step) | n* detected | n* × deficit |
|---|---|---|---|
| 0.51 | 0.000289 | 9,200 | 2.7 |
| 0.55 | 0.007226 | 400 | 2.9 |
| 0.60 | 0.029049 | 250 | 7.3 |

The product stays order-constant while the deficit varies a hundredfold, at or below the predicted ceiling as expected for a first-crossing statistic. The bound is usable as stated: the observation budget required to refute a source's apparent randomness is the reciprocal of its pole gap deficit, in bits.

## 6. Honest limits

No new mathematics was produced or claimed. The chain rule and Pinsker's inequality are classical; for the statistical observer class the equivalence is theorem-adjacent, and the experiment's contributions there are finite-sample behavior, audit power (§4), and the exported bound (§5). What the schema adds, and what this experiment tested, is the *identification*: that Yao's equivalence, Boltzmann-style coarse-grained entropy, and dynamical unpredictability are one structure measured per observer class (a claim with consequences, one of which corrected its own authors). The schema's genuine frontier is exactly where it predicts: computational observer classes, where pseudoentropy chain rules are known to fail in general and the equivalence carries content that classical information theory cannot supply. A second transfer candidate (crypticity as a lower bound on observer-synchronization lag, statable as a security parameter) remains open and is the natural next experiment.

---

*Prepared under the standing orders of the attack document: claim only what survived; put the objections first; one transfer demonstrated at the "reasoning, with teeth" level. Circumpunct Framework, Ashman Roonz, fractalreality.ca.*

## Revision history

- 2026-07-27 v1.0: initial. Imported from the claude.ai chat session (emergence-files.zip: pole-gap-experiment.md + transfer.py). Repo edits on import: house header and this history added; prose em dashes converted to house punctuation; en-dash name pairs hyphenated; companion-code reference renamed transfer.py → pole_gap_transfer_v1.py; all numbers re-verified by a local run (exact match, every row). Content otherwise unchanged from the chat draft.
