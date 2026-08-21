# Theorem Atlas and Dependency Audit

**Status:** working research index, 2026-08-20, landed and extended 2026-08-21, v1.11. This atlas inventories theorem-like claims across the active repository, separates proved mathematics from internal consequences, computation, conjecture, and interpretation, and records a first new derivation pass. It does not itself change canon. **Its staged judgments are COUNTERSIGNED (Ashman, 2026-08-21; disposition 2 in `plans/countersign_batch_2026_08_21.md`): the claim taxonomy, the quarantine register, the authority order, and the section 12 maintenance protocol are now editorial law for theorem-like claims.**

## 1. Executive result

The repository contains a large theorem-bearing corpus, but the number of theorem labels is much larger than the number of independent proved results.

The lexical harvest found:

| Measure | Count | Meaning |
|---|---:|---|
| Theorem-like occurrences | 764 | Every extracted theorem, lemma, proposition, corollary, conjecture, axiom, identity, or derivation label |
| Normalized candidate titles | 590 | Case and punctuation-normalized labels, still not semantic deduplication |
| Theorem labels | 316 | Includes complete proofs, sketches, repetitions, and unsupported theorem headings |
| Identity labels | 95 | Includes mathematical identities and ordinary prose uses of the word identity |
| Derivation labels | 94 | Includes proofs, calculations, and headings about derivation status |
| Axiom labels | 60 | Premises rather than derived conclusions |
| Conjecture labels | 60 | Explicitly open or speculative claims |
| Proposition labels | 55 | Mixed proof status |
| Lemma labels | 42 | Mixed proof status |
| Corollary labels | 42 | Often repeated downstream consequences |

The raw inventory is `plans/theorem_inventory_2026_08_20.tsv`. It includes the new formal pass but excludes this generated atlas so the count cannot inflate recursively. It is a discovery index, not a proof certificate. Its false positives are useful because they expose overloaded words and duplicated claims, but no raw count should be advertised as a count of proved theorems.

The strongest currently auditable mathematical clusters are:

1. The shell-trident and balance-pole results in zeta coordinates.
2. The finite-window reconstruction theorem with its corrected v2 certificate.
3. The exact finite harmonic analysis of the balanced seven-residue octave.
4. The single-period and residue arithmetic conditional on the adopted half-step lattice.
5. The finite T-operator perturbation and scale experiments.
6. Elementary internal consequences of the countersigned ontology, including the new group-only-at-balance theorem.

The Clay-problem documents, universal physics claims, and several older geometric theorems are not in that class. They contain programs, conjectural links, or missing major steps and must not be represented as established solutions.

## 2. Reading rule and authority order

When two documents disagree, use this order:

1. Latest dated and countersigned adjudication record.
2. `CLAUDE.md` as working memory, except where a later countersigned record supersedes it.
3. Current formal or experimental note with an explicit status and revision history.
4. Long-form framework exposition.
5. Older or undated documents.
6. `Path_of_Learning/`, which is historical archive and excluded from the active harvest.

The present meaning-layer sequence is:

\[
\text{Infinity}
\to
\text{convergence}
\to
\text{singularity}
\to
\text{emergence as 1D, 2D, 3D}
\to
\text{wholeness},
\]

with every whole converging again. The corrected geometric ladder is point at 0D, line at 1D, boundary at 2D, and field at 3D. Documents that use field at 2D or boundary at 3D carry migration debt even when a separate algebraic argument inside them is sound.

The two-layer rule is essential:

- Meaning layer: the primary sequence is coordinate-free.
- Arithmetic layer: half-step addresses are retained for the octave calculations.

A formula using an address does not by itself prove that the associated process has a fractional spatial dimension.

## 3. Claim classes

Every serious entry should receive both a claim class and an evidence grade.

### 3.1 Claim class

| Code | Class | Test |
|---|---|---|
| S | Standard mathematics | Imported theorem, identity, or method with ordinary mathematical meaning |
| I | Internal theorem | Follows from explicitly stated framework premises but does not establish a physical instantiation |
| R | Research candidate | Complete or nearly complete mathematical result whose literature novelty is not yet established |
| C | Computational result | Established for a stated finite model, parameter range, or numerical certificate |
| E | Empirical claim | Requires independent observation, data, or prospective testing |
| X | Interpretive bridge | Maps mathematics into framework language without adding a mathematical implication |

### 3.2 Evidence grade

| Grade | Evidence |
|---|---|
| P0 | Statement only |
| P1 | Sketch, heuristic, or proof with a material gap |
| P2 | Complete written proof at the stated scope |
| P3 | Complete proof plus reproducible computation or explicit certificate |
| P4 | Established external result, with attribution still required where absent |

These axes prevent four common category errors: treating an axiom as a theorem, treating a finite computation as a universal law, treating an internal implication as empirical validation, and treating an exact rearrangement of known mathematics as established literature novelty.

## 4. High-confidence mathematical register

| Result | Class / grade | What is established | Limit or action |
|---|---|---|---|
| Shell radius/weight law | R/S, P3 | Mellin Plancherel weight on radius \(R\) is \(x^{1/R-1}\); the critical circle is the unique flat shell | Arrangement appears original to this framework, but ingredients are classical; complete literature audit remains |
| Critical-circle measure pullback | S, P3 | On \(s=1/2+it\), \(dt=d\theta/|1-w|^2\) in absolute measure | Standard conformal calculation |
| Shell winding and Li-mode visibility | R/S, P3 | Prime-shell Cauchy pairings vanish outside the Euler shell and expose Li modes after the center is enclosed, subject to the stated zero-free region | Exact packaging may be new; ingredients are classical |
| Balance-pole Abel criterion | R, P3 | RH is equivalent to Abel summability of either stated alternating Li series; when it exists, parity fixes the unweighted sum at zero and the weighted sum at the displayed closed form | Proof is present; novelty remains uncensored by a full literature search |
| Finite-window pencil skeleton | S, P4 | A definite moment-matrix pencil recovers finitely many support points when the packet matrix has full column rank | Classical Prony, matrix-pencil, and ESPRIT territory |
| Prime-built finite reconstruction | R/C, P3 | Eight target ordinates are uniquely reconstructed from finite prime-built forms with corrected unconditional error below \(6.9676\times10^{-4}\) | Finite-window theorem only; no infinite-window or RH conclusion |
| Transversality lemma | S/R, P3 | Restriction to any transverse signal subspace preserves ideal generalized eigenvalues by congruence | Exact use in this certificate is valuable; underlying linear algebra is standard |
| Balanced octave residue group | I/S, P2 | Given the half-step lattice and wrap \(7/2\), the residues form \(\mathbb Z_7\) | Conditional on adopted coordinate lattice |
| Quadratic chirp character | S/C, P3 | The stated quadratic traversal is an exact CAZAC/Zadoff-Chu sequence on \(\mathbb Z_7\) | Standard finite harmonic analysis, exactly instantiated |
| Linear splitting character | S/C, P3 | The pure-tone route is a single Fourier character on \(\mathbb Z_7\) | Same scope |
| Octave single-period lemma | I, P2 | The half-step sequence has primitive period \(7/2\), one constant per residue, parity alternation, and traversal excess \(nR\) under its stated definitions | Do not transfer it to a deformed lattice without reproof |
| Odd-cycle balance rigidity | S/I, P3 | For the staggered family with \(m\) structural intervals (\(N=2m+1\) stations, wrap \(L=m+b\)): eleven conditions are equivalent to \(b=1/2\) (equal spacing, additive closure, nontrivial rotational symmetry, zero circular centroid, Fourier unitarity, optimal conditioning, and five more); closure explosion: rational \(b=a/q\) generates \(\mathbb Z_{mq+a}\), irrational \(b\) a dense orbit; exact gap-variance \(m(m+1)(2b-1)^2/N^2\), displacement, sumset-growth, and Dirichlet-kernel Fourier-defect formulas; verification rerun bit-identically on this branch | Generalizes and supersedes the \(m=3\) group-only-at-balance entry; elementary methods, literature novelty not claimed; framework instantiation unproved; interpretation countersigned 2026-08-21 (balance package) |
| Balance-attractor dynamics | S/I, P3 | Bounded persistence with diverging throughput forces the throughput-weighted long-run balance to \(1/2\) from conservation alone (Theorem 1); complement symmetry fixes the point but not stability, so a feedback law is required; four explicit laws (conservative exchange, storage homeostasis, boundary-preserving relative growth, defect-gradient descent on the rigidity theorem's \(V_{\rm gap}\)) each make balance globally attractive with exact solutions; integral feedback is required in the linear model to erase accumulated seam displacement (continuous Lyapunov and the exact discrete Jury region \(k_i>0\), \(k_p>k_i\), \(2k_p-k_i<4\)); delay boundary \(\lambda\tau=\pi/2\); OU fluctuation signatures; a conditional-drift empirical protocol with four disconfirming outcomes | Standard dynamical-systems and control mathematics, exactly instantiated; which law, if any, nature uses is unmeasured; the constitutive principle countersigned 2026-08-21 (balance package) |

Primary files:

- `plans/balance_pole_theorem_2026_08_15.md`
- `experiments/balance_pole_theorem_v1.py`
- `plans/finite_window_reconstruction_2026_08_15.md`
- `experiments/finite_window_certificate_v2.py`
- `experiments/finite_window_certificate_v2_findings.md`
- `docs/octave_wrap_lemma.html`
- `experiments/staggered_octave_z7_findings_v1.md`
- `plans/balance_rigidity_theorem_2026_08_20.md`
- `experiments/balance_rigidity_v1.py` (output receipt: `experiments/balance_rigidity_v1_output.txt`)
- `plans/balance_attractor_dynamics_2026_08_20.md`
- `experiments/balance_attractor_dynamics_v1.py` (output receipt: `experiments/balance_attractor_dynamics_v1_output.txt`)
- `plans/balance_empirical_protocol_2026_08_20.md`
- `experiments/balance_empirical_test_v1.py` (self-test receipt: `experiments/balance_empirical_test_v1_selftest_output.txt`)
- `plans/theorem_inventory_2026_08_21.tsv` (refreshed snapshot; the 2026-08-20 snapshot retained)

## 5. Internal framework theorems

These results can be rigorous while remaining conditional on framework definitions or countersigned premises.

| Result | Dependency | Class / grade | Audit note |
|---|---|---|---|
| Present indivisibility | Present is identified with the center; the center is indivisible | I, P2 | Direct substitution, not an external discovery |
| No greatest whole | Every whole embeds properly in a larger whole | I, P2 | If proper nesting is already an axiom, a separate no-greatest-whole axiom is redundant |
| Conjugacy transfer | \(F=\varphi\circ T\circ\varphi^{-1}\) with valid domains | S/I, P4 | Standard theorem; each claimed domain isomorphism still needs proof |
| Single-circumpunct identity | The substrate is one and every center is a localization of it | I, P1 to P2 | Exact strength depends on which identity and copula axioms survive the foundations audit |
| Every whole converges again | Countersigned primary sequence | I, canonical premise | Presently functions as a canonical cycle rule, not a theorem from weaker axioms |
| Line-boundary-field emergence ordering | Corrected ladder plus primary sequence | I, canonical premise | Supersedes the older field-boundary reversal |

The formal foundations file `circumpunct_foundations_formal_v0_1.md` is a useful start but is not yet a closed axiom system. Its current audit obligations are:

1. State the third copula relation between infinity and wholeness explicitly.
2. Decide whether \(R(\infty,\bullet)\) improperly treats one substrate as two relata.
3. Repair or replace the categorical identity-morphism construction.
4. Distinguish shared-tonic saturation from a genuine composition law.
5. Add downward or bidirectional nesting if the prose requires it.
6. Remove the older present-at-interface statement where the later indivisible-present correction supersedes it.

Until those decisions are closed, downstream results should cite their exact premises instead of saying they follow from "the framework" without qualification.

## 6. New formal pass completed on 2026-08-20

The commissioned pass is in `plans/half_balance_formal_pass_2026_08_20.md`. It contains eight proved statements.

Let \(b\in(0,1)\), let the wrap length be \(L_b=3+b\), and let

\[
S_b=\{0,b,1,1+b,2,2+b,3\}\subset\mathbb R/L_b\mathbb Z.
\]

| New result | Exact conclusion | Class / grade |
|---|---|---|
| Complement reflection | \(b^*=1-b\), with unique self-complementary value \(b=1/2\) | I/S, P2 |
| Group only at balance | \(S_b\) is a subgroup iff \(b=1/2\); then \(S_b\cong\mathbb Z_7\) | I/S, P2 |
| Equal spacing only at balance | The ordered octave is an arithmetic progression iff \(b=1/2\) | I/S, P2 |
| Exact gap variance | \(V_{\rm gap}=\frac{12}{49}(2b-1)^2\), uniquely zero at balance | I/S, P2 |
| Constant seam drift | \(\Delta_n=n(b-1/2)\) relative to the balanced lattice | I/S, P2 |
| Variable seam drift | \(\Delta_n=\sum_{j<n}(b_j-1/2)\) | I/S, P2 |
| fBm sign convention | If \(D=1+b\) and \(D=2-H\) describe the same graph, then \(b=1-H\) | S/X, P2 conditional |
| Three-beta underdetermination | The coincidence \(F(1/2,1/2,1/2)=1/2\) cannot select a beta or aggregation law | I/S, P2 |
| Stroke-to-arc classification | Current typings force convergence arc \(\{q=0,q=1\}\) and emergence arc \(\{q=2,q=3\}\) | I, P2 relative to canon |

Two deductions materially sharpen the earlier staging:

1. Local balance and final balance are different. Complementary off-balance octaves can cancel cumulative seam drift, but neither local station set gains \(\mathbb Z_7\) symmetry.
2. An off-balance octave does close at its own tonic \(3+b\). It closes early or late only relative to the canonical balanced tonic \(7/2\). The earlier absolute wording is corrected.

This formal pass is mathematically complete at its stated scope. (Countersigned 2026-08-21, batch disposition 1.)

**Extension (2026-08-20, landed and verified 2026-08-21).** The group-only-at-balance theorem opened into the odd-cycle balance-rigidity theorem (`plans/balance_rigidity_theorem_2026_08_20.md`, verification `experiments/balance_rigidity_v1.py`, rerun on this branch with output identical to the source session's). Eleven conditions are proved equivalent to \(b=1/2\) across the whole family \(N=2m+1\); the closure-explosion theorem classifies every imbalance (rational \(b=a/q\) embeds the \(N\) visible stations in \(\mathbb Z_{mq+a}\); irrational \(b\) generates a dense orbit; balance is uniquely the case where the visible stations already ARE the complete group they generate); and the two-register consequence protects the existing \(\mathbb Z_7\) harmonic results while bounding them: the label DFT (chirp and tone) survives at every \(b\), but only at balance does it coincide with the orthonormal harmonic analysis induced by coordinate translation. The mathematics is verified; the framework interpretation is countersigned (2026-08-21, the balance package).

**Second extension (2026-08-20, landed and verified 2026-08-21): balance-attractor dynamics.** This executes section 11 item 2 (`plans/balance_attractor_dynamics_2026_08_20.md`, verification `experiments/balance_attractor_dynamics_v1.py`, rerun clean on this branch). Three results carry the weight: the bounded-persistence theorem derives the throughput-weighted long-run balance \(1/2\) from conservation plus boundedness alone (a route to ◐ = 1/2 independent of the symmetry, entropy, and virial arguments, valid only over complete cycles with all channels counted, per its own accounting guard); the periodic corollary legitimizes oscillation (a system can be instantaneously off balance throughout its cycle while exactly balanced over it); and the seam-residual theorem proves local balance restoration cannot erase accumulated displacement, so a stable whole needs memory of cumulative error (the integral term), with the exact discrete stability region given by the Jury conditions. The empirical face is the conditional-drift protocol: measure \(I\), \(O\), and storage, perturb, and test whether the drift of \(b\) points toward \(1/2\); four disconfirming outcomes are pre-stated. Which law, if any, nature instantiates is open; the constitutive principle is countersigned (2026-08-21, the balance package, `plans/countersign_batch_2026_08_21.md` dispositions 7 and 8).

**Third extension (2026-08-20, landed and verified 2026-08-21): the empirical protocol and analyzer.** The balance-attractor claim is now an executable, falsifiable research program (`plans/balance_empirical_protocol_2026_08_20.md`, class E scaffold; `experiments/balance_empirical_test_v1.py`, class C at P3 for its validation). The protocol separates three claims that fail independently (accounting closure; complete-cycle balance; restoring attraction toward 1/2), fixes tolerances from the instrument error budget before looking, compares the half-fixed against a freely centered equilibrium by bootstrap interval and BIC, and defends against the oscillator trap: a neutral oscillator is balanced over every cycle and mean-reverting at any single finite lag, so the analyzer sweeps lags and flags restoration that strengthens with lag as a hidden-state warning; only repeated perturbation contraction from both sides is decisive. Self-test rerun on this branch: the four adversarial controls (relaxer at 1/2, relaxer at 0.62, repeller at 1/2, neutral oscillator) classify correctly, with the finite-window balance identity exact. Section 12 of the protocol states the novelty bar honestly: steady-state inflow-equals-outflow is standard conservation, and the framework adds content only by pre-registering variables, boundaries, the reason the recovery point is 1/2, rate scalings, or a cross-domain invariant. No natural-system dataset exists in the repository yet; this validates the method, not nature. The inventory was refreshed per protocol step 7 (`plans/theorem_inventory_2026_08_21.tsv`: 799 candidates, 607 normalized titles, matching the source session's counts on its own tree exactly; the 2026-08-20 snapshot is retained). Framework integration of the protocol awaits countersign.

## 7. Computational and finite-model register

| Program | Established finite result | Prohibited extrapolation |
|---|---|---|
| T-operator v14 | Tonic-sharing departure saturates rather than accumulating across tested scales; a forced second-period shift reduces distinguishability; the 69/31 split does not converge; tested parity observable is null | Universal scale law or physical validation |
| T-operator v15 | The apparent ground floor is a finite-size artifact in the studied construction | A privileged physical minimum scale |
| T-operator v17 | The observed maximizing \(q^*\) is alpha-independent under the specified perturbation; no simple closed form was found | Closed-form universality outside that model |
| T-operator v19 | The spectral gap opens linearly to first order under the specified whole-tone interpolation | The discarded \(2/7\) guess or an empirical law |
| Staggered octave v2 | Stated finite chain and spectral relations reproduce under the script's assumptions | Ontological necessity |
| Pole-gap transfer | Entropy, KL divergence, and Pinsker relations hold and the finite experiment matches them | New information theory or an experimental physics result |

Primary files include `experiments/T_operator_findings_v14_staggered_chain.md`, `experiments/T_operator_findings_v15_ground_floor.md`, `experiments/T_operator_findings_v17_qstar.md`, `experiments/T_operator_findings_v19_gap_scaling.md`, `experiments/staggered_octave_findings_v2.md`, and `experiments/weil_scale_operator_findings_v1.md`.

## 8. Prediction and empirical register

The predictions scoreboard is valuable but must be read from its corrected verification section, not its stale top summary.

Current corrected tally in `plans/predictions_scoreboard.md`:

- 42 known results or retrofits.
- 4 predictions still pending.
- 13 structural derivations.
- 1 open item.
- 60 unique entries total.

No pending prediction has yet landed. A structural identity that follows from chosen coordinates is not automatically a novel prediction, and a match to a known integer or natural-units convention is not independent empirical evidence. The framework's physical value will be established only by preregistered, discriminating predictions that outperform plausible alternatives.

## 9. Conditional, staged, and quarantined clusters

| Cluster | Current status | Required repair |
|---|---|---|
| Tier decomposition | Conditional set arithmetic under width-3 tiers, but noncanonical because the current octave wraps at \(7/2\) | Retype or preserve explicitly as an alternative model |
| Euler theorems E2 to E5 | Depend on the retracted surface theorem and older ladder; at least one boundary-to-\(S^2\) step is unsupported | Quarantine, then rewrite from corrected topology with explicit hypotheses |
| Analytic continuation gap | Conjectural triple closure and missing analytic estimates | Keep as research program, not an RH proof |
| Isomorphism apparatus | Standard conjugacy principle is sound, but six apparatus decisions and the February migration remain open | Close staged decisions; verify every domain map |
| Navier-Stokes chain | Major drain-stretch and regularity steps not proved | Treat as speculative program, not solution |
| Hodge chain | Main algebraicity step unsupported | Treat as speculative program, not solution |
| Yang-Mills chain | Mass-gap mechanism contains explicit proof obligations | Treat as speculative program, not solution |
| P versus NP chain | Framework-language separation does not prove a complexity lower bound | Supply a standard-model lower-bound argument or retract theorem wording |

Files with old ladder notation can still contain locally valid algebra. Migration debt is not automatic mathematical falsity. Each claim must be separated from its obsolete interpretation before reuse.

## 10. Dependency map

### 10.1 Ontology and balance chain

\[
\text{countersigned primary sequence}
\Rightarrow
\text{two-layer rule}
\Rightarrow
\text{deformed address family }S_b
\Rightarrow
\text{balance-only }\mathbb Z_7.
\]

The last implication is now proved. It does not run backward to prove the ontology.

### 10.2 Octave and operator chain

\[
\text{half-step lattice + wrap }7/2
\Rightarrow
\text{single-period lemma}
\Rightarrow
\mathbb Z_7\text{ characters}
\Rightarrow
\text{chirp and tone routes}
\Rightarrow
\text{finite T-operator studies}.
\]

Changing the lattice parameter breaks the group step unless \(b=1/2\), so downstream DFT results cannot be assumed off balance. Refined by the balance-rigidity theorem (2026-08-21): the label-register DFT results survive at every \(b\); what breaks off balance is their coincidence with the coordinate-induced harmonic analysis, whose matrix stays invertible but loses unitarity, with condition number minimized uniquely at balance.

### 10.3 Zeta chain

\[
\text{Li/Keiper disk coordinate + Mellin theory}
\Rightarrow
\text{shell trident and balance pole},
\]

and independently

\[
\text{explicit formula + Gaussian packets}
\Rightarrow
\text{finite Weil forms}
\Rightarrow
\text{definite pencil}
\Rightarrow
\text{finite certified ordinates}.
\]

The finite reconstruction chain stops before the window-to-infinity limit. That missing assembly is exactly where an RH-scale problem remains.

### 10.4 Isomorphism chain

\[
\text{proved bijection }\varphi
+
\text{proved conjugacy }F=\varphi T\varphi^{-1}
\Rightarrow
\text{transfer of invariants}.
\]

The transfer theorem is standard. The burden lies in proving each proposed \(\varphi\), its domains, and the exact conjugacy, not in naming two diagrams alike.

## 11. Highest-value next theorem work

1. **Foundations minimization.** Produce an independent axiom basis and prove which present axioms are redundant, inconsistent, or definitional.
2. **Balance dynamics.** Specify a law for \(b_j\), then prove conditions for bounded drift, zero mean drift, local restoration, or instability. The current seam theorem gives the exact observable.
3. **Deformed harmonic analysis.** Replace the lost off-balance group with a weighted frame or nonuniform Fourier system and quantify how chirp orthogonality degrades as a function of \(|b-1/2|\).
4. **Finite-window convergence.** Improve unconditional prime-tail and zero-tail bounds, enlarge certified windows, and isolate precisely what compactness or positivity would be needed for an infinite limit.
5. **Literature novelty audit.** Search Li/Keiper, Voros, Bombieri-Lagarias, Mellin-Plancherel, matrix-pencil, and finite-frame literature before making priority claims.
6. **Prediction conversion.** Turn one internal identity into a preregistered quantitative test with a null model, uncertainty budget, and disconfirming outcome.
7. **Topology rewrite.** Rebuild the older Euler and surface claims using the corrected line-boundary-field ladder and explicit manifold hypotheses.

## 12. Maintenance protocol

For every new theorem-like claim:

1. Give it a stable title and exact statement.
2. List definitions and dependencies immediately above it.
3. Assign a claim class and evidence grade.
4. Separate proof, computation, interpretation, and empirical consequence.
5. State the strongest conclusion the proof does not establish.
6. Record supersession or retraction visibly.
7. Add the result to the raw inventory and this curated atlas.
8. Require countersign only for canon changes, not for ordinary mathematical correctness checks.

This protocol turns the corpus from a collection of theorem-shaped passages into a dependency-tracked research program.

## Addendum (2026-08-21): landing receipt and post-dating events

This atlas, the raw inventory, the half-balance formal pass, and the harvester (v1.2) were produced in a 2026-08-20 working session and landed verbatim on branch `claude/infinity-scale-architecture-ruskx6` on 2026-08-21. Landing receipts and events postdating v1.0:

1. **Reference integrity:** every file cited in sections 4 through 7 exists on this branch; no dangling references. The harvester was rerun on the 2026-08-21 tree and reproduced the committed inventory bit-for-bit (764 candidates, 590 normalized titles), which also certifies that the day's five new records introduce zero theorem-labels.
2. **Section 11 item 6 (prediction conversion) was executed on 2026-08-21, independently and before this atlas landed.** A pre-registered blind test now exists under a binding protocol: targets scouted and picked before looking, rules and candidate space frozen and committed before the search, null calibration per the §27.7n bar, no silent drops, null a reportable outcome. Result: sin²θ₁₂ came out null-by-multiplicity (the frozen family space cannot individuate it: itself a finding about the grammar's density at that magnitude); Δm²₂₁/|Δm²₃₁| is pre-registered at 5/169 = 0.0295858 (grade ii, sharpening survival; kill at >3σ exclusion by JUNO's forthcoming releases). Files: `plans/preregistration_targets_2026_08_21.md`, `plans/preregistration_juno_computation_2026_08_21.md`, `experiments/preregistration_juno_search_v1.py`. Section 8's register therefore gains one pending prediction (4 becomes 5); the scoreboard row itself awaits countersign.
3. **Section 8's empirical caution acquired a live instance the same day:** the Λ-constancy audit (`plans/lambda_constancy_audit_2026_08_21.md`) found the corpus two-voiced on the dark-energy equation of state: a dated evolution prediction (framework §12.1 and the public predictions page, w(z) ≈ −1.033 + 0.017/(1+z), directionally tracking DESI while ~50x below its central amplitude) standing beside the constancy stratum (§12.2/§27.7g and the ladder-correction witness). A four-branch futures table with pre-assigned verdicts is staged for adjudication before Euclid DR1 (October 2026).
4. **Status unchanged where it matters:** the half-balance formal pass and this atlas's staged judgments remain awaiting Ashman's countersign. Landing is delivery, not signature.

## Revision history

- 2026-08-21 v1.11: the synthesis document countersigned with the ethics corner-and-middle repair and published (`docs/fractal_reality_with_the_information_layer.html`, disposition 13); conformance audit in `plans/fractal_reality_with_information_layer_2026_08_21.md`.
- 2026-08-21 v1.10: the layer's first amendment countersigned (disposition 12): the formal spine's five theorems and the Boundary-Record Loss Theorem (S at P4 imports; boundary-loss/retention-loss reading I/X at P2) registered; the free-energy identity F − F_eq = k_B·T·D(p‖p_eq) as primary bridge; measure-declaration rule standing.
- 2026-08-21 v1.9: the information layer countersigned and registered (`plans/information_layer_formal_2026_08_21.md`): the quadruple and boundary principle (A3's Shannon form, I/P2) canon; dictionary class X with three firm anchors; four-channel balance accounting standing; Landauer bridge S/P4 with scope; IIT disambiguation mandatory; pole-gap program identified as the layer's experimental face; master-table Information row (charter v2.19) and the eleventh Theme-and-Variations variation landed.
- 2026-08-21 v1.8: protocol amended to v1.2 (clamp check; constraint verdict; disposition 10) and Run 2 executed (breath, `plans/balance_breath_run_2026_08_21.md`): instrument validated on a natural oscillatory system (monotone 8/8-bin restoring profile, textbook weakens-with-lag, oscillator guard satisfied not tricked); breathing measured cycle-balanced to 0.1% with equilibrium 0.4915 (primary diagnostic detects the −0.9% offset, BIC discounts it); passive-data ceiling respected; class E evidence awaits a perturbed consented study.
- 2026-08-21 v1.7: Run 1 executed (Xorzo2 spine, `plans/balance_xorzo2_run_2026_08_21.md`): instrument validated including the newly identified zero-variance constraint case; Xorzo2 measured as exactly cycle-balanced by construction (b pinned at 1/2, attraction undefined at that boundary); "three ways to sit at 1/2" (attracted, coincidental, constrained) enters the register as the run's conceptual yield.
- 2026-08-21 v1.6: empirical protocol and analyzer landed with clean self-test (third section 6 extension); inventory refreshed to the 2026-08-21 snapshot (799/607, cross-tree match).
- 2026-08-21 v1.5: the balance package countersigned (rigidity interpretation and constitutive principle); status cells updated.
- 2026-08-21 v1.4: balance-attractor dynamics landed and verified (register row, second section 6 extension); section 11 item 2 executed.
- 2026-08-21 v1.3: odd-cycle balance-rigidity theorem landed and verified (new register row, section 6 extension, section 10.2 refinement); the section 6 countersign bracket added.
- 2026-08-21 v1.2: staged judgments countersigned (batch disposition 2); the section 12 protocol becomes editorial law.
- 2026-08-21 v1.1: landed in-repo; addendum with the landing receipt, the bit-identical harvest check, the executed section 11 item 6 (JUNO pre-registration), and the Λ two-voice cross-reference.
- 2026-08-20 v1.0: initial active-corpus harvest, claim taxonomy, dependency audit, quarantine register, and integration of the half-balance formal pass.
