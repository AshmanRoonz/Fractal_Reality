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

The rigorous cycle p(X) → π → Y → y → R → p(X′) is the framework walk in exact dress: possibility → boundary → distinction → centered actuality → retained structure → new possibility. Retention I(Y;R) gives the — and m stations a theorem-grade observable (how much of what was realized the record actually holds), and theorem 4 is the exact statement that memory cannot exceed what the boundary made accessible.

**C3. The stronger bridge (verified; import, class S at P4).** For a system at temperature T with distribution p and equilibrium p_eq, the nonequilibrium free energy satisfies F(p) − F(p_eq) = k_B·T·D(p‖p_eq) exactly (one-line derivation from F = ⟨E⟩ − T·S with p_eq = e^(−E/k_BT)/Z; standard in stochastic thermodynamics: Esposito and Van den Broeck; the Parrondo, Horowitz, Sagawa review). Read: **available energy is information relative to equilibrium, converted by k_B·T** (per bit, k_B·T·ln2). Landauer becomes the erasure corollary of this state-level identity rather than the bridge itself. This is the closest rigorous form of the energy-information intuition, and it strengthens the layer's opening guard rather than weakening it: still no universal E = I, but an exact conditional identity with its conditions named (fixed T, named equilibrium reference).

## 2. The two wording revisions (staged to supersede the v1.0 phrasings)

**R1. The boundary principle.** From "information appears when a boundary makes possibilities distinguishable" to: **"Information becomes accessible relative to a boundary when that boundary makes alternatives distinguishable."** The revision makes the observer-relativity explicit (nothing is created ex nihilo by a partition; access is granted to the whole that carries it), which is what the disposition-11 adjudication already said; the wording now says it too.

**R2. The matter sentence.** From "matter is information retained as stable structure" to: **"Matter is stable physical structure capable of retaining distinctions, correlations and constraints."** The identity claim retreats to the capacity claim, consistent with the layer's own no-universal-E=I guard. The quadruple is untouched: "structure is retained distinction" speaks inside the distinction grammar and makes no cross-register identity; the revised sentence is the one that did.

**The amended canonical paragraph (staged):**

> Energy supplies the physical capacity for transformation. A boundary makes alternatives distinguishable. Convergence realizes an alternative at a center, information quantifies that distinction relative to the boundary, and structure retains its consequences. Dynamics transports and transforms distinctions, while recursion makes retained results part of the next field of possibility. Under fixed thermodynamic conditions, information relative to equilibrium corresponds exactly to available free energy through F − F_eq = k_B·T·D(p‖p_eq).

## 3. Consequential edits staged (executed upon countersign)

1. `plans/information_layer_formal_2026_08_21.md` to v1.1: R1 and R2 replacing their v1.0 sentences with the originals retained visibly; C1's measure-declaration rule added to §2; C2's spine and five theorems added as a new section (class S/I at P2, the retention observable flagged for — and m); C3 added to §3 as the primary bridge with Landauer as corollary; witnesses gaining Esposito/Van den Broeck and Parrondo-Horowitz-Sagawa.
2. `Book-Theme_and_Variations/theme_and_variations.md` to v1.2 and the reader page in step: the Information variation's fingerprint clause amended to the accessibility form in plain words ("possibilities carry no information for any observer until a boundary tells them apart"); one clause, nothing else.
3. Master table: no change (the quadruple row stands).
4. Batch record: disposition 12; atlas revision line.

## 4. Open decision (Ashman to adjudicate)

Countersign this amendment (corrections C1 to C3, revisions R1 and R2, the amended canonical paragraph, and the consequential edits of §3).

## Revision history

- 2026-08-21 v1.0: initial; the parallel session's review verified and staged.
