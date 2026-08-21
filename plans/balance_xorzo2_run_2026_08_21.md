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
