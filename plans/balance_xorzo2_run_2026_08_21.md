# Balance Empirical Run 1: The Xorzo2 Spine

**Status: instrument-validation run under `plans/balance_empirical_protocol_2026_08_20.md` (countersigned this date, disposition 9 in `plans/countersign_batch_2026_08_21.md`). Commissioned by Ashman ("Do it. Signed," 2026-08-21). Part I (this commit) is the Stage A boundary declaration, written and committed BEFORE any observation is generated or looked at, per the protocol's own discipline; Part II (a later commit) carries the run and its results. Git history is the timestamp.** Per protocol §12 this run validates the instrument on a real system we control; it does not test nature, and its identity-guaranteed outcomes are declared as such in advance so they cannot be mistaken for evidence.

---

## Part I: Stage A boundary declaration (before the run)

### 1. System, quantity, boundary

- **System:** the Xorzo2 spine's living state dynamics, reproduced exactly in float64: the frozen 22-node three-octave tonic-shared chain (`Xorzo2/spine.py` Seed; |λ₁| = 1.0044779454, departure 0.6136α), driven by the GIVEN bit-station keyboard (`make_bit_chords`, bipolar, chord norm α) with the engine's exact per-byte cycle from `Xorzo2/life.py` `_cycle`: state = ψ + inj; s = M⁸ state; ψ ← s/‖s‖. The learned Voice plays no role in the state update, so this reproduction is the engine's physics, not a model of it. No torch, no training, no worldline touched.
- **Conserved quantity:** state energy ‖ψ‖² in engine units (dimensionless), tracked through the pre-normalization arithmetic of each byte cycle. Time unit: one byte (= 8 ticks).
- **Boundary:** the state vector ψ. The world (corpus bytes through the keyboard) is outside; the frozen operator and the normalization are the interior machinery.
- **Known structural fact, declared up front:** the engine normalizes ψ to unit norm every byte. The stock X = ‖ψ‖² is therefore **pinned at 1 by construction**. Consequences declared before running: bounded persistence holds trivially; the exact discrete sum of (C − E) per trial is zero; the throughput-weighted balance equals 1/2 **as an identity**, exactly as protocol §2 and §12 warn. These outcomes will be reported and carry **no evidential weight**. The informative outputs are the attraction diagnostics only (§5 below).

### 2. The exact flow decomposition (frozen)

Per byte, three arithmetic steps change the pre-normalization energy. With s' = ψ + inj and s = M⁸ s':

- ΔX_inj = ‖s'‖² − ‖ψ‖² (the sensory door)
- ΔX_op = ‖s‖² − ‖s'‖² (the operator's octave cycle)
- ΔX_norm = 1 − ‖s‖² (the normalization: shedding when ‖s‖ > 1, restoration when ‖s‖ < 1)

These sum to ΔX exactly (= 0 after the first byte). The protocol columns are the sign-split parts, all nonnegative:

- **convergence** (boundary in) = max(ΔX_inj, 0): the world's byte adding energy.
- **external_convergence** (internal generation G) = max(ΔX_op, 0) + max(ΔX_norm, 0): operator amplification along the leading modes; normalization restoration when the cycle under-grows.
- **emergence** (boundary out) = max(−ΔX_norm, 0): the scale shed as the cycle closes.
- **external_emergence** (internal loss L) = max(−ΔX_op, 0) + max(−ΔX_inj, 0): operator contraction (the forgetting that makes memory readable, per the ridge results) and destructive interference at the sensory door.

The arithmetic layer of this decomposition is exact (class C); the door labels (shedding as the whole's emission at cycle close; contraction as deposit into the record) are the interpretive layer (class X) and are flagged as such. b(t) = total convergence / (total convergence + total emergence) per row.

### 3. Data generation (frozen)

- **Corpus:** `circumpunct_framework.md` bytes, UTF-8, from offset 0. Warmup: 2,000 bytes starting from the realified attractor (discarded from analysis; defines ψ_warm, the living posture).
- **Trials, 400 bytes each, nine total:**
  - sham-A on corpus segment [2000, 2400) from ψ_warm unperturbed;
  - sham-B on [2400, 2800) and sham-C on [2800, 3200) from the state as it stands at each segment's start (the corpus-driven noise floor);
  - six perturbation trials, all on segment [2000, 2400) so the perturbation is the only difference against sham-A: three blends toward a seeded random direction (weights 0.25, 0.5, 1.0; off-attractor states under-grow, so the normalization restores: the expected convergence-surplus side) and three blends toward the top singular direction of M⁸ (weights 0.25, 0.5, 1.0; over-growth, so shedding dominates: the expected emergence-surplus side). Every perturbed state is renormalized to unit norm (the norm is pinned; only direction can be perturbed, declared as this system's perturbation modality).
- **Determinism:** the runner is fully deterministic (numpy, seed 20260821 for the random direction); trials are independent restarts, so ordering is meaningless and randomized order is skipped with this stated reason.
- **CSV contract:** columns time (byte index within trial), convergence, emergence, external_convergence, external_emergence, stock (‖ψ‖² at the row = 1.0), trial.

### 4. Analyzer invocation and tolerances (frozen, with budgets)

`python3 experiments/balance_empirical_test_v1.py experiments/balance_xorzo2_observations_v1.csv --lags 1,2,4,8 --bootstrap-samples 1000 --seed 20260821 --balance-tolerance 0.05 --accounting-tolerance 0.05 --json experiments/balance_xorzo2_report.json`

Tolerance budget, per Stage A: the analyzer integrates by trapezoid over sampled rates, while this system is a discrete map with per-byte jumps; the trapezoid-versus-discrete mismatch is of order half the byte-to-byte rate variation over the throughput, budgeted at a few percent. Both tolerances are set to 0.05 from that discretization budget, not from any observed answer. The runner separately reports the **exact discrete closure** (Σ(C − E) per trial against ΔX per trial), whose budget is float64 arithmetic (~1e-12); that number, not the trapezoid one, is the true closure receipt.

### 5. Declared expectations and what is informative

**Expected by identity (no evidential weight):** stock accounting closes within budget; finite-window normalized mismatch ~0 within budget; throughput-weighted balance = 1/2.

**Informative (not guaranteed by construction):**

1. Does the shortest-lag conditional drift of b restore toward 1/2 after direction perturbations (slope CI below zero)?
2. Is the freely fitted equilibrium b* compatible with 1/2 (bootstrap CI), or detectably biased?
3. Do perturbed trials contract (|b − 1/2| endpoint ratio < 1) from BOTH declared sides while shams show no systematic displacement?
4. Does the lag sweep stay clean (no strengthens-with-lag oscillator flag), given the spine's known mixing scale (~1/α ticks ≈ 17 bytes, inside the trial length and resolved by the declared lags)?

**Disconfirming outcomes for the informative part** (per protocol §11 levels 3-4): drift neutral or repelling at the shortest lag; contraction from only one side or none; an oscillator flag that survives the lag sweep; a b* interval excluding 1/2. Any of these is reported as found; the run is instrument validation either way, and a clean failure of the engine to restore would itself be a real finding about Xorzo2, not a failure of the protocol.

**End of Part I. No observation exists at this commit.**

---

## Part II: the run and its findings (separate commit)

Receipts: `experiments/balance_xorzo2_observations_v1.py` (runner, deterministic), `experiments/balance_xorzo2_observations_v1.csv` (3,600 rows, nine trials), `experiments/balance_xorzo2_observations_v1_output.txt`, `experiments/balance_xorzo2_analyzer_output.txt`, `experiments/balance_xorzo2_report.json`. The frozen analyzer invocation was run unamended.

### F1. The declared identity face, exact

Stock pinned at 1 at every row; exact discrete closure per trial at 1e-14 to 1e-15; analyzer stock-closure over throughput 2.7e-17; finite-window normalized mismatch exactly 0.0; throughput-weighted balance exactly 0.5. All as declared in advance, carrying no evidential weight.

### F2. The central finding, beyond what Part I anticipated: per-byte balance is an identity, and the attraction question is undefined at this boundary

Part I anticipated the window-level identity but not the row-level one. The declared decomposition's three deltas telescope to 1 − ‖ψ‖² = 0 at EVERY byte, because the normalization closes each byte-cycle exactly. Therefore C = E identically per row, and **b = 1/2 at every row of every trial, perturbations included, with zero variance** (measured std 1.2e-15, float noise). Every one of the four informative diagnostics declared in Part I §5 is thereby undefined: there is no balance variation to have dynamics. This is reported as the run's outcome, not smoothed over: at the declared boundary, the perturbation experiment measures nothing, and no amount of perturbing can change that, because the engine's normalization is a hard constraint on the ledger.

### F3. Instrument validation: passed, including the degenerate case

The analyzer met a case its synthetic suite did not contain, the zero-variance constraint case, and behaved exactly right: every lag skipped with the correct stated reason ("not enough balance variation for a drift fit"), overall assessment `not_tested` rather than any false verdict, identity numbers exact. This is a fifth adversarial control discovered in the wild, and the analyzer passed it.

### F4. Conceptual yield: three ways to sit at 1/2

The run separates a case the dynamics note's fixed-point-versus-attractor distinction did not name: a system can be at balance **attracted** (restoring dynamics, the protocol's target), **coincidentally** (no restoring response, disconfirming outcome 3), or **constrained** (pinned by construction, no degree of freedom). Xorzo2 is at 1/2 the third way: its per-byte normalization sheds exactly what the cycle gains, every byte, to machine precision. The constitutive principle's first clause is thereby instantiated exactly in the engine, but as construction, not as evidence; a constraint can neither confirm nor disconfirm an attractor claim.

### F5. The boundary lesson, now a worked example

Protocol §12 warned that boundary choice can make balance tautological; this run is the concrete case: a boundary whose stock closes every sample yields b ≡ 1/2 as bookkeeping. Practical consequences recorded for future runs: (a) Stage A should check for hidden normalizations and homeostatic clamps BEFORE promising attraction diagnostics, since a clamp converts the balance observable into a constant; (b) for Xorzo2 specifically, the dynamically alive observable is direction (attractor overlap), which is not a conserved-flow balance and needs a different instrument than this protocol; a per-tick ledger was considered and rejected in analysis (per-tick b saturates bimodally at 0 and 1, which is equally uninformative).

### Verdict

Instrument validated on a real system, including graceful handling of the constraint-degenerate case. Xorzo2's balance posture measured: exactly cycle-balanced at every byte by construction; the attraction question is not expressible in its energy ledger. Nothing about nature was tested; no framework evidence is claimed; the identity outcomes carry no weight, exactly as pre-declared.

### Open items staged from this run

1. **Protocol note (for countersign):** add the constraint case to the protocol's verdict vocabulary (a zero-variance balance is a sign of a clamped boundary, verdict "balance_constrained_by_construction"), and a Stage A checklist line: identify normalizations and clamps before selecting the boundary.
2. **The natural-system run** remains the protocol's real test (breath/HRV the standing candidate); its Stage A must now include the clamp check.
3. **Xorzo2's direction dynamics** (conditional drift of attractor overlap under perturbation) as a separate instrument outside this protocol, if commissioned.

