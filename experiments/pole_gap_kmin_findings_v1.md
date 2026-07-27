# k_min = 21, and the live page's FLOOR FOUND light is a false positive

```
Created: 2026-07-27
Last updated: 2026-07-27
Version: 1.0
```

*Code: `pole_gap_kmin_v1.py`. Tests the floor theorem and the proposed discovery lag from the Pole Gap Calculus draft (Ashman, 2026-07-27) against `docs/the_pole_gap_live.html`'s own substrate and observer constants.*

---

## 1. The identities check out

Verified by hand before running anything: the G_q decomposition (cross-entropy = entropy + KL, then the definition of conditional mutual information), the telescoping observer chain and its per-step conditional mutual information, A\* − ½ = TV(P_{M,Y}, P_M ⊗ U), D_KL(P_{M,Y} ‖ P_M ⊗ U) = 1 − H(Y|M), the Pinsker chain, the coherence dividend Ω = I(A';B'|M), and the deterministic specialization G(M) = H(Y_{t+1}|M_t) = I(Y_{t+1};X_t|M_t). All correct.

## 2. The measurement

Ring 15, Rule 30 centre column. The substrate revisits at step 1,502 with period 1,455. Observer constants taken from the live page (EMA 1/400, threshold 0.3 bits/step sustained 1,500 steps, 3,000 scored minimum).

| k | H(Y\|C_k) | S_k | ambiguous | acc % | FOUND (abs) | Λ_abs | own floor | Λ_rel |
|---|---|---|---|---|---|---|---|---|
| 8 | 0.8636 | 254 | 234 | 62.7 | never | - | 11,704 | 10,202 |
| 10 | 0.4499 | 782 | 254 | 76.5 | never | - | 20,135 | 18,633 |
| 11 | 0.2902 | 1036 | 183 | 81.9 | never | - | 25,914 | 24,412 |
| **12** | **0.1569** | 1219 | 104 | **89.6** | **8,252** | 6,750 | 25,712 | 24,210 |
| 14 | 0.0418 | 1386 | 30 | 97.2 | 5,926 | 4,424 | 31,437 | 29,935 |
| 16 | 0.0143 | 1433 | 10 | 98.9 | 5,299 | 3,797 | 27,070 | 25,568 |
| 20 | 0.0014 | 1454 | 1 | 99.8 | 5,098 | 3,596 | 22,638 | 21,136 |
| **21** | **0.0000** | **1455** | **0** | 99.8 | 5,077 | 3,575 | 22,418 | 20,916 |

**k_min = 21.** The condition H = 0 is reached exactly when S_k equals the period: every phase of the cycle acquires a distinct k-window. Below that, some window recurs with both successors and no amount of observation can resolve it.

## 3. The catch: the page's default cannot find the floor, and its light says it did

The live page ships at k = 12. At k = 12 the structural term is 0.1569 bits/step and is **permanent**: accuracy plateaus at 89.6%, not 100%, no matter the budget. The FLOOR FOUND indicator nevertheless fires at step 8,252.

It fires falsely at every k from 12 through 20. Only k ≥ 21 can find the floor at all.

The cause is that the indicator tests an absolute display threshold (EMA below 0.3 bits/step) while the floor theorem's condition is H(Y|C_k) = 0. Those coincide only when the observer's asymptote happens to sit under the bar. The light means "the gap dropped below 0.3," and the page says it means "discovered."

This is the second indicator fault in that page in one day, and the two are mirror images. This morning's was on the ∞ side: a hashed row claiming to be the full state, reporting a cycle that did not exist. This one is on the ⊙ side: a threshold claiming to be a floor, reporting a discovery that did not happen. Both are the Inflation shape, an indicator asserting more than its aperture admits, once at each pole.

## 4. The proposed lag Λ_k measures the wrong thing

The draft predicts Λ_k should grow with S_k, since KT redundancy is O(S_k log n / n). Measured, Λ_abs *falls* with k: 6,750 at k = 12 down to 3,575 at k = 21, while S_k rises from 1,219 to 1,455.

That is not a falsification of the redundancy law; it is a defect in the observable. Λ_abs is the time to cross a fixed bar, and a larger k has a lower asymptote, so it crosses sooner. The measurement conflates learning speed with floor depth.

Measuring instead the time to come within 0.05 bits of the observer's *own* floor (Λ_rel) gives 10,202 at k = 8 rising to roughly 20,000-30,000 for k ≥ 11, with no clean monotone trend and considerable scatter. The relative lag is the meaningful quantity and it is an order of magnitude larger than the absolute one. Any future claim about learning-time scaling should use it, and should expect noise.

## 5. A caveat on the monotonicity theorem

G(B) ≤ G(A) when M_A = f(M_B) is correct for the **ideal** observer, since it is conditioning reducing entropy. It does not transfer to the realized gap G_q at finite budget, because the KL term carries a learning tax that grows with observer size.

We already have the counterexample in this repo. On Xorzo2's corpus at 830K bytes, the realized prequential loss is 1.734 nats at order 2, 1.925 at order 3, and 2.281 at order 4 (`pole_gap_xorzo2_null_findings_v1.md`). A strictly more informed observer performed strictly worse. The ordering O_0 ⪯ O_1 ⪯ ... holds for the structural term and not for what an actual observer pays.

## 6. Prior art: this program has a 35-year-old name

The setup (an observer that cannot see the internal state, receives only a projection, and must infer the state from the output stream) is **computational mechanics**, developed by Crutchfield and collaborators since the late 1980s. The correspondences are close to exact:

- **Synchronization time** is Λ_k. There is a paper specifically on the periodic case: "Synchronizing to Periodicity: The Transient Information and Synchronization Time of Periodic Sequences," which is the ring-15 experiment's exact subject.
- **Markov order** is k_min.
- **Crypticity** measures the inaccessibility of internal state information, with a hierarchy of k-cryptic processes. It is already named in `pole_gap_transfer_findings_v1.md` §6 as the next transfer candidate, which means the thread had already arrived at this literature's doorstep without going in.
- **The ε-machine** is the minimal model of the hidden state the observer is synchronizing to; **excess entropy** and **transient information** are the standard measures of what the projection costs.

This does not sink the program, but it relocates it. A "Pole Gap Calculus" presented without this literature would be dismissed by anyone in the field, and rightly. Presented as an extension it has one genuinely distinctive move: **computational mechanics generally takes the observable as given and studies the process, whereas the pole-gap framing makes the projection π a swept variable alongside the observer.** G(π, M, n) with π varying is the part that is less explored. The three-stage instrument (ontic closure, representability, learnedness displayed separately on a live substrate) is instrumentation rather than theory, and is useful on those terms.

## 7. Two further cautions

**Emergence curvature.** The draft's own telescoping result already gives the first difference: G_j − G_{j+1} = I(Y'; M_{j+1}|M_j). So the natural object is the sequence of conditional-mutual-information increments, and emergence should be defined on those rather than on second differences of G. Note also that the prose ("a small increase in integration produces a disproportionate increase in predictability") describes a first-difference criterion while κ_j is a second difference; those identify different scales and the intended one should be pinned down.

**The coherence dividend beyond two parts.** Ω = I(A';B'|M) is correct and is conditional mutual information under a new name, and it is non-negative, so it cannot detect anti-coherence. For three or more parts the analogous decomposition is the partial information decomposition problem (Williams and Beer, and the unresolved synergy/redundancy debate), and integrated information theory has spent two decades on the same difficulty. Worth noting that IIT's symbol for it is Φ, which in this corpus already means the field.

## Revision history

- 2026-07-27 v1.0: initial. Run to test the Pole Gap Calculus draft's two measurable quantities; found k_min = 21 against a shipped default of 12, and a false-positive indicator in the live page.
