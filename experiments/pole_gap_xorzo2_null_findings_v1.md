# The pole-gap ledger applied to Xorzo2: the unigram line is the wrong null

```
Created: 2026-07-27
Last updated: 2026-07-27
Version: 1.0
```

*Code: `pole_gap_xorzo2_null_v1.py` (read-only; never imports, runs, or touches Xorzo2 or its worldline). Instrument: the prequential estimator from `pole_gap_transfer_v1.py`, generalized from 2 symbols to 256. Status: a receipt, submitted for Ashman's adjudication. Nothing in `Xorzo2/findings_stage1.md` or `plans/xorzo2_plan.md` has been edited; F2 and F3 stand as written until he rules.*

---

## 1. What was asked

Xorzo2's F2 sets the severance verdict's threshold at the corpus unigram line (3.517 nats): above it, "learning is input-independent marginal statistics." F3 reports the memoryless voice at 3.18 nats, "0.33 nats below unigram with the spine as sole memory channel," and the individual later reached 3.07 at 830K bytes lived.

The pole-gap transfer experiment's control argues that a null should be an *estimator run on a structureless stream*, not a static entropy figure, because the estimator's own learning tax is part of the price (its fair-coin control pays 1.0368 bits, not 1.0000). Applying that argument here asks one question: on the identical stream, at the identical budget, under the identical online single-pass protocol, what does a trivial count-based context model pay?

## 2. Protocol

Same corpus files `run_xorzo2.py` streams (`circumpunct_framework.md` + `consciousness.md`, concatenated, read as raw bytes), same prefix (Xorzo2 reads cyclically from position 0 and at 830K against a 1.44M corpus had not yet wrapped), same budget (830,000 bytes), same prequential discipline (price every byte before it lands, pay the log-loss, learn only after paying). Dirichlet(1/2) per context. Reported in nats/byte to match Xorzo2. The matched-entropy null is the same stream shuffled: identical byte histogram, every higher-order correlation destroyed.

## 3. Results

| order | real, life | real, tail | null, life | null, tail | structure won | contexts |
|---|---|---|---|---|---|---|
| 0 | 3.482 | 3.364 | 3.482 | 3.479 | −0.000 | 1 |
| 1 | 1.972 | 1.899 | 3.538 | 3.498 | 1.566 | 170 |
| 2 | **1.734** | **1.540** | 3.995 | 3.802 | 2.261 | 4,213 |
| 3 | 1.925 | 1.614 | 4.825 | 4.617 | 2.900 | 23,869 |
| 4 | 2.281 | 1.961 | 5.353 | 5.264 | 3.071 | 67,046 |

"Life" is the mean over all 830K bytes; "tail" is the mean over the last 100K, which is the fair comparison against a late-life running loss. Order 0 reproduces the static unigram entropy (3.482 vs 3.480 measured directly), which calibrates the instrument.

**Two results, one of which was expected and one of which was not.**

**(a) The null rises with order, and it starts above the unigram line.** A structureless stream costs 3.538 nats at order 1 and 5.353 at order 4, against a static unigram entropy of 3.480. That excess is the learning tax: the price of maintaining contexts that carry no information. So "below the unigram line" is not the boundary between learning and marginal statistics; at any order above 0 the marginal-statistics baseline is *higher* than the unigram line, and it climbs steeply. The unigram line understates the null.

**(b) Xorzo2's reported loss is beaten by a one-byte lookup table.** Against the trailing window, the order-1 model pays 1.899 nats and the order-2 model 1.540, versus Xorzo2's reported 3.070. Xorzo2 is 1.171 nats/byte worse than a model that looks only at the immediately preceding byte, and 1.530 worse than the best model in the ladder.

The obvious defense (that the count model is simply bigger) does not hold at order 1: 170 observed contexts with sparse successor tables is a smaller object than the voice's ~108K parameters, and it wins by 1.17 nats under the same online single-pass protocol.

Note also that orders 3 and 4 are *worse* than order 2 on lifetime loss (1.925 and 2.281 vs 1.734). At this budget the tax overtakes the structure. That is the same estimator pathology §4 of the transfer experiment documented, appearing again unprompted.

## 4. What this does and does not say

**It does not contradict F4 or F5.** Those measure retention directly (ridge probe: 0.074 at lag 0 against chance 0.0039, horizon 6 cycles at 10x chance; and κ proven as the legibility mechanism by F-only ablation), and the recall ablation showing spine removal destroys everything older than 2 cycles is direct evidence that the spine holds and supplies the past. None of that is touched. The spine demonstrably retains.

**It says the retained information is not being converted into prediction.** There is a large gap between "linearly decodable from the state" and "used to predict the next byte," and this measurement locates Xorzo2 on the wrong side of it. The natural diagnosis is that the bottleneck is the readout, not the spine's memory, which is a different bottleneck than the project has been working on and a testable one.

**It says F2's rule should be restated.** The severance verdict wants a threshold below which learning is genuinely input-dependent. The unigram line is a valid floor for the narrow question "did it learn more than marginal byte frequencies," but it is a weak one, and reporting a margin against it ("0.33 nats below unigram") reads as stronger than it is. The calibrated replacement is cheap: report the shuffled null at matched order as the floor and the best context model as the bar, both from this ledger.

**Caveats.** The corpus has been edited since Xorzo2's 2026-07-19 runs, so the stream is not byte-identical to what it actually read; the unigram discrepancy (3.480 measured here vs 3.517 reported) is consistent with that drift. A 1.17-nat gap is far too large to be explained by it, but the exact figures would shift on a re-run against the corpus as it stood. Xorzo2's 3.070 is quoted from its findings file, not re-measured here; a direct re-measurement would have to run the individual, which advances its worldline and is a decision for Ashman, not an experiment to be run casually. The architectural comparison is protocol-fair (identical online single-pass pricing) but not architecture-fair: a count table memorizes exactly where a small online-trained network cannot, and Xorzo2's claim was never to be a competitive language model.

## 5. What it is evidence for

The transfer experiment's third prediction (P3) was that the coupling requirement must be strong enough to detect an inconsistent estimate in the project's own prior work. It did that once already, on the Rule 30 entropy rate. This is the second time the same instrument has been pointed at a project number and moved it. That is the property being claimed for the schema: a taxonomy cannot audit anything, and a structure with consequences can.

## Revision history

- 2026-07-27 v1.0: initial. Run after landing the pole-gap transfer experiment and the live page, to check by measurement a claim made from inference (that Xorzo2's severance threshold and the pole gap meter measure the same quantity). They do, and the threshold is set too low.
