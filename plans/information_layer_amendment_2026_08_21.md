# The Information Layer: First Amendment (Staged)

**Status: amendment record, 2026-08-21, staged for countersign. The parallel session reviewed the countersigned layer (disposition 11) and returned three technical corrections and two wording revisions; this record verifies them and stages the amendment. The countersigned v1.0 positions stand until Ashman signs; nothing is silently revised.** The correction flow itself is worth one line: the audit caught two errors in the proposal, and the proposal's author then caught a third error in the audit's repair. That loop running in both directions is the metacognitive culture working.

## 1. The three corrections, verified

**C1. Copying creates correlation, not entropy (verified, and it corrects this corpus's own repair).** If Y copies X, the joint entropy is H(X,Y) = H(X), not H(X) + H(Y); what grows is the mutual information I(X;Y). The countersigned four-channel accounting attributed "internal generation G_I" to copying and computation; that is ill-typed until the ledger names its measure. **Standing repair: every information ledger must declare which measure it tracks** (marginal entropy of a named subsystem, joint entropy of the whole, total correlation, or a mutual information with a named reference), and G_I and L_I are defined relative to that declaration. Under joint entropy, copying is not generation; under a subsystem's marginal, it can be. The four-channel FORM survives; its semantics acquire a required declaration, exactly parallel to the empirical protocol's accounting-boundary guard.

**C2. The formal spine (verified line by line).** With possibilities X, the observer's partition Y = π(X), realized outcome y, surprisal i(y) = −log₂p(y), and retained record R:

1. π constant ⇒ H(Y) = 0. (Immediate.)
2. Refining π cannot reduce H(Y): a refinement Y′ determines Y, so H(Y′) = H(Y) + H(Y′|Y) ≥ H(Y). (Verified.)
3. Coarsening cannot increase it. (Same identity, read the other way.)
4. I(Y;R) ≤ H(Y). (Mutual information is bounded by the marginal entropy.)
5. Perfect retention gives I(Y;R) = H(Y). (R determining Y saturates the bound.)

The rigorous cycle p(X) → π → Y → y → R → p(X′) is the framework walk in exact dress: possibility → boundary → distinction → centered actuality → retained structure → new possibility. Retention I(Y;R) gives the — and m stations a theorem-grade observable (how much of what was realized the record actually holds), and theorem 4 states precisely that **a record cannot retain more information about Y than the boundary made accessible through Y; the record may contain information about other variables** (the bound governs I(Y;R), not R's total capacity or content; micro-edit of 2026-08-21 replacing an earlier overstatement).

**C4. The Boundary-Record Loss Theorem (verified; the review's addition).** With Y = π(X) deterministic and the record generated from Y (so X → Y → R is a Markov chain), the data-processing chain gives I(X;R) ≤ I(X;Y) = H(Y) ≤ H(X), and the unavailable information decomposes exactly:

    H(X) − I(X;R) = H(X|Y) + H(Y|R).

Proof, two lines: I(X;R) = H(X) − H(X|R); by the chain rule H(X|R) = H(Y|R) + H(X|Y,R) (determinism removes H(Y|X,R)); Markov makes H(X|Y,R) = H(X|Y). Equality conditions: H(X|Y) = 0 when the boundary loses nothing; H(Y|R) = 0 when the record keeps everything the boundary passed; I(X;R) = H(X) only when both vanish. Framework reading: **what the whole cannot know decomposes into what its boundary could not distinguish (boundary loss) and what its memory could not retain (retention loss).** This is the information-theoretic form of the pole gap: the program's observer class is π, its predictor state is R, and the class-relative randomness gap it measures is exactly this two-term decomposition with receipts. Imported identities class S at P4; the boundary-loss and retention-loss reading class I/X at P2.

**C3. The stronger bridge (verified; import, class S at P4).** For a system at temperature T with distribution p and equilibrium p_eq, the nonequilibrium free energy satisfies F(p) − F(p_eq) = k_B·T·D(p‖p_eq) exactly (one-line derivation from F = ⟨E⟩ − T·S with p_eq = e^(−E/k_BT)/Z; standard in stochastic thermodynamics: Esposito and Van den Broeck; the Parrondo, Horowitz, Sagawa review). Read: **available energy is information relative to equilibrium, converted by k_B·T** (per bit, k_B·T·ln2). Landauer becomes the erasure corollary of this state-level identity rather than the bridge itself. This is the closest rigorous form of the energy-information intuition, and it strengthens the layer's opening guard rather than weakening it: still no universal E = I, but an exact conditional identity with its conditions named (fixed T, named equilibrium reference).

## 2. The two wording revisions (staged to supersede the v1.0 phrasings)

**R1. The boundary principle.** From "information appears when a boundary makes possibilities distinguishable" to: **"Information becomes accessible relative to a boundary when that boundary makes alternatives distinguishable."** The revision makes the observer-relativity explicit (nothing is created ex nihilo by a partition; access is granted to the whole that carries it), which is what the disposition-11 adjudication already said; the wording now says it too.

**R2. The matter sentence.** From "matter is information retained as stable structure" to: **"Matter is stable physical structure capable of retaining distinctions, correlations and constraints."** The identity claim retreats to the capacity claim, consistent with the layer's own no-universal-E=I guard. The quadruple is untouched: "structure is retained distinction" speaks inside the distinction grammar and makes no cross-register identity; the revised sentence is the one that did.

**The amended canonical paragraph (staged):**

> Energy supplies the physical capacity for transformation. A boundary makes alternatives distinguishable. Convergence realizes an alternative at a center, information quantifies that distinction relative to the boundary, and structure retains its consequences. Dynamics transports and transforms distinctions, while recursion makes retained results part of the next field of possibility. Under fixed thermodynamic conditions, information relative to equilibrium corresponds exactly to available free energy through F − F_eq = k_B·T·D(p‖p_eq).

## 3. Consequential edits staged (executed upon countersign)

1. `plans/information_layer_formal_2026_08_21.md` to v1.1: R1 and R2 replacing their v1.0 sentences with the originals retained visibly; C1's measure-declaration rule added to §2; C2's spine and five theorems added as a new section (class S/I at P2, with theorem 4 in the corrected about-Y wording); C4's loss-decomposition theorem added with its pole-gap identification; C3 added to §3 as the primary bridge with Landauer as corollary and the anchor line "information relative to equilibrium is available free energy expressed in units of k_B·T"; witnesses gaining Esposito/Van den Broeck and Parrondo-Horowitz-Sagawa.
2. `Book-Theme_and_Variations/theme_and_variations.md` to v1.2 and the reader page in step: the Information variation's fingerprint clause amended to the properly relativized form (micro-edit of 2026-08-21, replacing an earlier draft that quantified over all observers): "possibilities that a boundary does not distinguish carry no accessible information for its observer," with the full formal wording ("Possibilities that a given observer's boundary does not distinguish carry no accessible information for that observer") carried in the formal note; one clause, nothing else.
3. Master table: no change (the quadruple row stands).
4. `plans/pole_gap_boundary.md`: one added line under the cross-connection, naming the loss decomposition as the gap's exact information-theoretic form.
5. Batch record: disposition 12; atlas revision line.

## 4. Open decision (Ashman to adjudicate)

Countersign this amendment (corrections C1 to C3, revisions R1 and R2, the amended canonical paragraph, and the consequential edits of §3).

## Revision history

- 2026-08-21 v1.1: the review's two micro-edits incorporated (theorem 4's about-Y precision; the book clause properly relativized) and the Boundary-Record Loss Theorem added as C4, verified (chain rule plus Markov, two lines); the reviewer assesses the package ready to countersign.
- 2026-08-21 v1.0: initial; the parallel session's review verified and staged.
