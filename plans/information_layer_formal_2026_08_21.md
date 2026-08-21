# The Information Layer: Formal Note

**Status: formal note, 2026-08-21, v1.1. The countersigned information layer (disposition 11, `plans/countersign_batch_2026_08_21.md`) written up as a self-contained statement with its precisions, witnesses, and grades baked in; amended per the countersigned first amendment (disposition 12, `plans/information_layer_amendment_2026_08_21.md`): the accessibility rewording, the matter-capacity rewording, the measure-declaration rule, the formal spine with its five theorems, the Boundary-Record Loss Theorem, and the free-energy bridge as primary anchor. Companion to the audit record `plans/information_layer_2026_08_21.md`; this note carries the positions. Atlas-registered.**

## 1. The canonical statements

**The quadruple (canon):**

> Energy is potential distinction. Information is realized distinction. Structure is retained distinction. Dynamics is distinction flowing.

Seated in the master isomorphism table as the Information row (Potential / Realized / Retained distinction across Reality / point of view / result, i.e. future / present / past), with the fourth term carried by the present's process rows. Identification joining the temporal mechanics: **actuality = realized distinction** (what "possibility moves through inherited constraint and becomes actuality" yields, said in information dress).

**The boundary principle (canon; A3's Shannon form):** for a possibility space Ω and a partition π: Ω → {1, ..., N} induced by a boundary, N = 1 gives H = log₂1 = 0 no matter how rich Ω is; a boundary distinguishing N equiprobable classes gives H = log₂N; a realized outcome carries surprisal i(x) = −log₂p(x). Information does not exist merely because possibilities exist; **information becomes accessible relative to a boundary when that boundary makes alternatives distinguishable** (amended v1.1, disposition 12; the v1.0 wording "information appears when a boundary makes possibilities distinguishable" is superseded as insufficiently observer-relative). This is the corrected card's boundary axiom made computable, not a new axiom.

**Whose boundary (adjudicated):** the partition belongs to the OBSERVING whole's ○ (the filter with a passband); the information cycle (possibilities → partition → selection → encoding → transmission → integration → new possibilities) is therefore the validation channel of an observer meeting the world, not the constitutive genesis of a whole. Two wholes are always in play in a measurement: the observed • is realized against the observer's π. This dissolves the apparent order tension with the primary sequence.

**The station dictionary (canon, class X with the §2 anchors of the audit record):** ∞ = undifferentiated possibility space; convergence = conditioning, selection, compression, measurement; • = a realized outcome from a point of view; — = channel and causal history (the worldline as receipts); ○ = the partition (the filter); Φ = the distribution and relations among states; ⊙ = an integrated information-processing whole; ⟳ = output becoming the next scale's input or prior.

## 1b. The formal spine and its theorems (v1.1, disposition 12)

With possibilities X, the observer's partition Y = π(X), realized outcome y with surprisal i(y) = −log₂p(y), and retained record R, the rigorous cycle is p(X) → π → Y → y → R → p(X′): possibility → boundary → distinction → centered actuality → retained structure → new possibility. Theorems (imports, class S at P4; framework readings class I/X at P2):

1. π constant ⇒ H(Y) = 0.
2. Refining π cannot reduce H(Y) (a refinement Y′ determines Y, so H(Y′) = H(Y) + H(Y′|Y) ≥ H(Y)).
3. Coarsening π cannot increase H(Y).
4. I(Y;R) ≤ H(Y), with the exact scope: **a record cannot retain more information about Y than the boundary made accessible through Y; the record may contain information about other variables.**
5. Perfect retention gives I(Y;R) = H(Y).

**The Boundary-Record Loss Theorem.** With Y = π(X) deterministic and the record generated from Y (X → Y → R Markov), the data-processing chain gives I(X;R) ≤ I(X;Y) = H(Y) ≤ H(X), and the unavailable information decomposes exactly:

    H(X) − I(X;R) = H(X|Y) + H(Y|R).

Proof: I(X;R) = H(X) − H(X|R); by the chain rule H(X|R) = H(Y|R) + H(X|Y,R), determinism removing H(Y|X,R); the Markov property gives H(X|Y,R) = H(X|Y). Equality conditions: H(X|Y) = 0 when the boundary loses nothing present in X; H(Y|R) = 0 when the record keeps everything the boundary passed; I(X;R) = H(X) only when both vanish. Framework reading: **what the whole cannot know decomposes into what its boundary could not distinguish (boundary loss) and what its memory could not retain (retention loss).** This is the information-theoretic form of the pole gap: the program's observer class is π, its predictor state is R.

## 2. Information balance (the standing four-channel form)

Information is not conserved, and (v1.1, disposition 12) **every information ledger must declare which measure it tracks** before its channels mean anything: marginal entropy of a named subsystem, joint entropy of the whole, total correlation, or a mutual information with a named reference. Copying does not generally create Shannon information; it creates correlation (a perfect copy leaves joint entropy unchanged and raises mutual information), so whether copying counts as generation depends entirely on the declared measure. With the measure declared, the standing accounting is

    Ṁ = C_I − E_I + G_I − L_I,

with C_I converging (acquired) and E_I emerging (expressed, transmitted) information, G_I internal generation, and L_I internal loss (erasure). The countersigned balance canon applies to the totals, per the empirical protocol's accounting guard: bounded memory with diverging total throughput forces the throughput-weighted long-run balance of total convergence against total emergence to 1/2; stability requires the homeostatic feedback (M − M*)(total in − total out) < 0. Too much stored information must increase expression or erasure; too little must increase acquisition. The two-channel form (G_I = L_I = 0) is a special case; using it where computation or forgetting exist would pathologize every computing system, which is why the four-channel form is the standing one. The amended protocol (clamp check included) applies verbatim to information ledgers.

## 3. The energy bridge (import, stated with scope)

There is no universal equation E = I. The primary bridge (v1.1, disposition 12) is the state-level identity of nonequilibrium statistical mechanics: for a system at temperature T with distribution p and equilibrium p_eq,

    F(p) − F(p_eq) = k_B·T·D(p‖p_eq),

exactly. Anchor line: **information relative to equilibrium is available free energy expressed in units of k_B·T** (per bit, k_B·T·ln2), with the conditions named (fixed T, a named equilibrium reference). Landauer's bound is the erasure corollary: erasing one classical bit dissipates at least k_B·T·ln2, so E_dissipated ≥ k_B·T·ln2 × I_erased, experimentally confirmed at the single-bit scale; it prices exactly the L channel of §2. The canonical paragraph (amended, superseding the v1.0 closing formulation whose clause "matter is information retained as stable structure" is revised to the capacity claim):

> Energy supplies the physical capacity for transformation. A boundary makes alternatives distinguishable. Convergence realizes an alternative at a center, information quantifies that distinction relative to the boundary, and structure retains its consequences. Dynamics transports and transforms distinctions, while recursion makes retained results part of the next field of possibility. Matter is stable physical structure capable of retaining distinctions, correlations and constraints. Under fixed thermodynamic conditions, information relative to equilibrium corresponds exactly to available free energy through F − F_eq = k_B·T·D(p‖p_eq).

## 4. The experimental face: the pole gap

The corpus's pole-gap program is this layer operational: the inclusion-pole (∞: everything present, nothing distinguished by a predictor that already contains it) against the integration-pole (⊙: an observer pricing each bit before it lands), with randomness as the projection gap between them per observer class. The layer's ∞ and ⊙ rows are the program's two poles; the observer-class relativity the program measured is the "whose partition" adjudication with receipts. Cross-note recorded in `plans/pole_gap_boundary.md`.

## 5. Witnesses (differences stated)

Shannon (entropy, surprisal, the data-processing inequality: imported unmodified). Esposito and Van den Broeck, and the Parrondo, Horowitz, Sagawa review (the nonequilibrium free-energy identity of §3; stochastic thermodynamics as the bridge's home field). Bateson ("a difference that makes a difference": the ancestor of the distinction vocabulary; the quadruple extends his line into a four-tense grammar). Wheeler (it from bit: the ontological neighbor of "matter is information retained"; the framework grounds distinction in boundary-and-center anatomy rather than participatory acts alone). Landauer (information is physical; the erasure bound). Jaynes (probability as information, at the Φ row). Friston's free-energy principle (the near neighbor of information homeostasis; FEP minimizes surprise, the balance canon balances acquisition against release under bounded memory: distinct, comparable claims). IIT (the nearest neighbor of the ⊙ row and of "consciousness is wholeness"; IIT posits a measure with phenomenological axioms, the framework posits structural wholeness; **standing disambiguation: the framework's Φ is the field, IIT's Φ is a scalar integration measure, and the two must never be conflated in any write-up**).

## 6. Grades

Imports (Shannon, Landauer): S at P4. Boundary principle: I at P2 (one-line derivation from the card's A3). Dictionary: X, with the temporal-triple identification, the A3-Shannon form, and the filter-partition formalization as its three firm anchors. Balance transfer: I, conditional on the four-channel form. The closing formulation of §3: countersigned canonical wording. Empirical standing: none yet beyond the pole-gap program's existing receipts; any new empirical claim goes through the amended protocol.

## Revision history

- 2026-08-21 v1.1: first amendment executed (disposition 12): accessibility rewording, matter-capacity rewording, measure-declaration rule, the formal spine with five theorems, the Boundary-Record Loss Theorem, the free-energy identity as primary bridge with Landauer as corollary; originals retained visibly at each superseded clause.
- 2026-08-21 v1.0: initial; the countersigned layer stated with precisions, witnesses, grades, and the pole-gap face.
