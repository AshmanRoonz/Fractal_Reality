# The Pole Gap and the Circumpunct Octave

```
Created: 2026-07-28
Last updated: 2026-07-28
Version: 1.0
```

*The conceptual bridge between the two arms of the 2026-07-27/28 session. Ashman's synthesis, with one refinement added at §7 and verified. Reference document for the experimental programme: `pole_gap_boundary.md`. Session record and open adjudications: `pole_gap_thread_notes.md`.*

---

## The relationship, stated once

The octave supplies the structural cycle. The Pole Gap work supplies measurements for what is gained, lost, preserved, or invented while moving through it.

> ∞ →[π] local observation →[integration] ⊙

∞ is the whole state available by inclusion; π is the aperture through which the whole becomes locally accessible; ⊙ is the whole reconstructed by integration. The Pole Gap is the distance between the two kinds of oneness:

> **Pole Gap = what the whole contains − what the observer has integrated.**

The work does not prove the octave. It asks whether the octave's distinctions correspond to separable mathematical quantities. Some do. At least one proposed correspondence did not, and killing it was the point.

## 1. ∞: one by inclusion

The full Rule 30 row X_t determines X_{t+1}. From this view there is no intrinsic randomness: every relevant distinction is contained in the whole. The observer never has this access.

## 2. The aperture: projection makes a local reality

The observer receives O_t = π_o(X_t) and predicts Y_{t+1} = π_y(X_{t+1}). The projection does two things at once: it makes observation possible, and it destroys distinctions, since X¹ ≠ X² may still give π(X¹) = π(X²).

The centre column is not fake. It is genuinely part of the system, and it is not the whole row. **Local truth ≠ complete inclusion.**

## 3. The line: the observer receives a sequence

The spatial whole becomes a temporal path O₁, O₂, O₃, … The observer must infer hidden structure from that line, which is why memory depth mattered: C_t^(k) = (O_{t−k+1}, …, O_t) is how much of the line is integrated into the present.

## 4. The interface: where two realities meet

X_t ↔ M_t. Neither is the other; contact happens through the projection. A × B preserves both coordinates, and GOOD(A,B) = R(A,B) ∧ ¬(A alone ∨ B alone) is the admissibility condition: no severance in either direction, no absorption in either direction. Conservative rather than generative. **The boundary does not guarantee a new whole; it guarantees the contact does not erase either side.**

## 5. ⊙: one by integration

M_t = 𝓜(O_≤t) is oneness by organising observations into a coherent predictive state, not by containing the substrate. Ring 15 forced three stages apart:

| stage | ring 15 |
|---|---|
| substrate closed | step 1,502, period 1,455 |
| floor representable, H(Y\|C^(k)) = 0 | k_min = 21 |
| model learned | ≈ 20,000-30,000 observations |

So ⊙ is not "the pattern exists." It is **the pattern has been integrated into an observer capable of carrying it.**

## 6. Convergence and emergence

Convergence happens twice: X_t →[π] O_t, and O_≤t →[𝓜] M_t. Emergence is the integrated state producing q(Y_{t+1}|M_t), a prediction or action that re-enters the field.

> whole state → projection → temporal observations → integration → prediction, and recurse.

## 7. The Pole Gap measures incomplete traversal, in three terms

The two-term decomposition, verified:

> Γ = I(Y_{t+1}; X_t | M_t) + E[ D_KL( P(Y_{t+1}|M_t) ‖ q(Y_{t+1}|M_t) ) ]

**Refinement (2026-07-28).** Both convergence steps are many-to-one, so the first term contains two different losses and they should not be lumped:

> **Γ_q = Γ_π + Γ_⊙ + Γ_learn**
> = I(Y;X|O_≤t) + I(Y;O_≤t|M) + E[D_KL(P(Y|M) ‖ q(Y|M))]

holding under two conditions: M = f(O), and the full state screens the observation history from the target, Y ⊥ O | X.

| term | what it is | who can recover it |
|---|---|---|
| **Γ_π** = I(Y;X\|O_≤t) | never passed the external aperture | **nobody** observing through π |
| **Γ_⊙** = I(Y;O_≤t\|M) | passed, but not retained by integration | a better-memoried observer |
| **Γ_learn** = E[D_KL] | retained, not yet correctly expressed | more data, **conditionally** (see below) |

So "the observer cannot access it" was hiding two different claims: *it was never given*, and *it was given and discarded*.

Verified (`pole_gap_three_term_v1.py`) on a stochastic 2-bit substrate with a lossy projection and a depth-1 observer: 0.46709 + 0.53284 = 0.99993 against Γ_rep = 0.99993, residual 1e-16, with the screening condition checked rather than assumed. The aperture floor is analytically h₂(p) for the fresh noise bit; against the run's *realised* p = 0.09940 that is 0.46710 against a measured 0.46709, so the 0.0019 offset from the nominal h₂(0.1) = 0.46900 is sampling variation in the noise rate, not estimator bias (dh₂/dp = log₂9 = 3.17).

**Caveat on the "nobody" column.** The experiment uses a three-observation window as O, not the literal infinite history. Here that window is provably sufficient, since Y_t = a_t ⊕ a_{t−1} ⊕ N_{t−1} and the fresh noise bit is in no earlier observation. In a different testbed the sufficiency of the window is an assumption requiring its own argument, and without it Γ_π and Γ_⊙ are not cleanly separated.

The algebra is telescoping; the content is that it separates **irrecoverable** from **recoverable** loss.

**Where the experimental arm lives.** Define the internal-aperture loss at memory depth k:

> J_k = I(Y; O_≤t | M_t^{(k)}), with M_t^{(k)} = (O_{t−k+1}, …, O_t).

Then **k_min = min{k : J_k = 0}** is the general predictive Markov order: the first depth at which finite memory retains everything in the *accessible* history that matters. On ring 15 the full observable history predicts perfectly, H(Y|O_≤t) = 0, so J_k collapses to H(Y|C_t^{(k)}) and k_min = 21 is exactly where the **internal** aperture loss vanishes, not where the external aperture disappears.

And since Γ_π is fixed by the projection and constant across observers,

> **k\*(n) = argmin_k [ J_k + R_k(n) ]**,

which is sharper than "entropy against complexity": it trades information discarded by the internal aperture against information not yet learned because that aperture is more complex.

**Placement correction (2026-07-28).** I first wrote that the CTW-versus-fixed-order pilot was aimed at J_k. It is not, under the fair common-D protocol. Both observers receive the same observations at the same maximum depth D, and both families *contain the complete depth-D model*: the fixed-order mixture as its deepest component, CTW as one tree in its mixture. So neither discards anything the other retains,

> J_D^FO = J_D^CTW,

and their difference is the learning term, L_FO − L_CTW ≈ Γ_learn^FO − Γ_learn^CTW, up to finite-sample noise. CTW's proposed advantage is not that it preserves information a uniform-depth mixture must discard. It is that a prior over tree structures encodes heterogeneous dependency more economically: short contexts where short suffice, deep only where needed. So **V_π predicts an architecture-dependent difference in learning cost, not in retention.**

Verified (`pole_gap_same_floor_v1.py`) on a known-order source with exactly computable H_D at D = 8:

| n | L_FO − H_D | L_CTW − H_D | L_FO − L_CTW |
|---|---|---|---|
| 2,000 | +0.01341 | +0.01634 | −0.00293 |
| 50,000 | −0.00234 | −0.00175 | −0.00060 |
| 299,000 | −0.00033 | −0.00025 | −0.00008 |

Both realized prequential losses approach the *same* theoretical floor H_D = 0.24429, while the between-observer difference shrinks by a factor of ~35. Shared J_D; the architectures differ in how fast they pay it down.

**These are realized deviations, not "excess" terms.** The middle columns go negative at the larger budgets, which is not a defect: an individual generated sequence can be easier than its own source's entropy rate. Only the expectation is bounded below, E[L̂(n)] − H_D ≥ 0. The evidence is not that each displayed difference stays positive; it is that L_FO(n) → H_D and L_CTW(n) → H_D while L_FO(n) − L_CTW(n) → 0. The theoretical reason for the common asymptote is representability plus consistency; the table is a finite-run illustration of it, not the proof.

A genuinely lossy architecture comparison *could* move the middle term, for instance if one architecture permanently pooled contexts the other kept. That is not this design.

**The hypothesis, stated precisely.** V_π predicts

> R_FO,π(n) − R_CTW,π(n),  **not**  J_FO,π − J_CTW,π.

CTW is hypothesised to pay less for learning heterogeneous context structure, not to perceive or retain more. Falsification condition: *after matching projection difficulty and using a common sufficient depth D, context-depth heterogeneity does not predict the finite-budget prequential advantage of CTW over the fixed-order mixture.*

If that happens the hypothesis fails without touching the three-term decomposition, the aperture/integration distinction, k_min, or k\*(n). The live claim is now independently falsifiable from the established structure, which it was not while it sat on the middle term.

**Experimental map.**

| experiment | term it addresses |
|---|---|
| projection sweep | Γ_π |
| memory-depth sweep | J_k = Γ_⊙(k) |
| k\*(n) | J_k + R_k(n) |
| CTW vs fixed-order at common D | R_CTW(n) vs R_FO(n) |
| Instrument Pole Gap | Γ_π applied recursively to measurement |

**Wording on the third term.** Γ_learn is not emergence itself. It measures the inaccuracy of the emergent output relative to what the current integrated state could already support.

**And "more data" carries two conditions**, without which the third column is false. Γ_learn itself splits:

> Γ_learn = inf_{q ∈ 𝒬} E[D_KL(P ‖ q)] + finite-data excess loss
> = model-class approximation + what more data actually fixes

Only the second part is recoverable by observation. The first vanishes when the predictor family can represent P(Y|M) and the learning procedure is consistent. For KT conditionals over a fixed finite context set that holds asymptotically, and for both bounded-depth mixtures used here it holds provided D is sufficient, since both contain the full depth-D model. Outside those conditions, an irreducible approximation term sits inside Γ_learn and no amount of data removes it.

The three terms land on three octave transitions: what reality made observable, what the observer retained, what it learned to express.

## 8. The Instrument Pole Gap: the octave recursing onto itself

An instrument observes through a marker, Z →[T] T(Z), which is another aperture, and then makes a claim C(Z). If T(Z₁) = T(Z₂) while C(Z₁) ≠ C(Z₂), the instrument has confused its local projection with the included whole. That is exactly what happened with the hash for the state, the threshold for the floor, the sentinel for a measurement, a name for a function, and two examples for a general relation.

**The observer's aperture is itself observed through another aperture.** The framework did not merely describe the Rule 30 observer; it described the research apparatus and the reasoning about it.

## 9. Scope inflation is a failed emergence

A local truth expanded to a general one without testing the boundary crossed. The local finding is real; the larger whole is invented. In octave terms an invalid emergence: a part claiming wholeness without carrying the relations that would support it. The Inflation Lie at the level of reasoning.

## 10. GOOD and synergy are different octave moments

GOOD establishes that both sides survive the relation. It does not establish that the resulting whole has a new capacity. Synergy requires a named target and a chosen decomposition: S(A,B→Y) > 0 means the pair carries information about Y that neither carries alone.

> **GOOD preserves the possibility of emergence; synergy demonstrates that emergence occurred.**

## 11. What the experiments do and do not establish

They do not prove the octave as a metaphysical structure. They show that several of its distinctions become operational: inclusion vs integration; whole state vs projection; existence vs representability vs learnedness; boundary preservation vs emergent synergy; local truth vs scope-inflated whole; observer error vs distributed correction; indicator vs condition indicated.

Some correspondences survived: Γ_rep ≠ Γ_learn is real and now three-way. One failed: I(A;B) ≠ synergy. The failure is productive, because the octave must not let symbolic resemblance substitute for mathematical identity.

## The mapping

| octave | operational |
|---|---|
| ∞ | X_t, the included whole |
| π_outer | X_t → O_t, the observation aperture |
| — (line) | O_≤t, observations through time |
| π_inner | O_≤t → M_t, the integration aperture |
| A × B | interface preserving both coordinates |
| GOOD | neither severance nor absorption |
| ⊙ | M_t, one by integration |
| emergence | q(Y_{t+1}|M_t), outward prediction or action |
| S(A,B→Y) | measurable whole-only emergence |
| recursion | apply the same structure to the instrument itself |

The two poles are no longer joined by one undifferentiated distance. There is a path, and every transition fails differently:

> ∞ → what reality makes observable → what the observer retains → what the observer learns to express

> **Pole Gap = not transmitted + not retained + not learned.**

That also says why the two arms are one project. The Instrument Pole Gap concerns failures at the first transition, where a marker destroys distinctions a claim requires. Memory depth governs the second. KT and CTW compete on the third.

Three operational levers, fully separated:

> projection choice → what is transmitted
> memory depth → what is retained
> learning architecture → how efficiently it is learned

The octave generated the distinctions; the Pole Gap translated some into information theory; the failed experiments showed which symbolic correspondences were real enough to survive measurement.

## Revision history

- 2026-07-28 v1.0: initial. Ashman's synthesis, with the three-term refinement at §7 added and verified.
