# Next Frontier Plan (2026-04-22)

> With the α closed form pinned at the factor level and the three-term shape resolved by station-content, the auxiliary-claim layer is closed modulo one bookkeeping convention. This plan walks the six genuine open pieces of the framework as of 2026-04-22. The order is concrete-to-speculative: easy local wins first, then computational infrastructure, then the big "does it actually predict" question, then axiomatic derivations, then empirical tests, ending at the hardest open question (absolute masses).

## Status of prior frontier (closed)

- Seven routes force T = 3 (Routes 1-5 plus Route 6 from P! = G·Φ and Route 7 from P·V + R + Φ + T = (T+1)³ = P³)
- α closed form: 1/α = 360/φ² − 2/φ³ + α/(59/3) = 137.035999147 (0.22 ppb); every factor pool-native
- φ-exponent rule: closed by A3 + dimensional analysis (φ as scaling ratio, φ^d at dimension d by what dimension means)
- 59/3 dual reading: closed by Route 7 (one identity, two sides)
- Three-term shape: pinned by station-content argument (scalar κ_{0,0} with 2D mediator; content at 2D/3D/0D; no 1D by scalarity; no α² by QED-loop argument)
- Residual: one bookkeeping convention ("one term per station with content"), consistent with A(d) bookkeeping throughout

## Six open pieces

### 1. Bond energy outliers (O=O, S-F, H-F)

Smallest, most independent. §16.4e-f gives sub-percent on 23 bonds; three outliers remain. Each is a local fix; none depend on the others.

**O=O (paramagnetic, 2.3% error).** Two unpaired electrons in pi* antibonding orbitals. The current double-bond model treats the second pi as filled; for O=O it is not. Predict: add a paramagnetic exchange term proportional to the unpaired-electron count; test against O=O, N=O, NO₂ radical bonds.

**S-F (39% error, H-F 26% error).** Extreme ΔEN where the power law D(A-B) = √(D_AA · D_BB) · [1 + 5·ΔEN²] compresses or over-extends. The 5 = Φ+○ coupling is correct at moderate ΔEN; at the extremes a higher-order term matters. Candidate: add a −(Φ+○)²·ΔEN⁴ correction at fourth order (same coupling family, next shell); test against all ΔEN > 2.5 bonds.

**Deliverables.** Short HTML page `docs/bond_outliers.html` with the three corrections, accuracy tables, and the specific bonds each fixes. Update §16.4e-f in circumpunct_framework.md with the extended model. Keep the original 23-bond baseline; the extensions should not degrade existing fits.

**Edge.** Three small wins, independent, each directly testable against CODATA bond-energy tables.
**Risk.** The corrections might over-fit; need to check they do not degrade the baseline 23 bonds.

### 2. ℂ⁵¹² three-scale octave (F₅₁₂ = F₈ ⊗ F₈ ⊗ F₈) ✓ DONE 2026-04-22

**Status: complete.** See `experiments/unified_expression_T_v14_C512.py` and `experiments/T_operator_findings_v14_C512.md`.

Headline results (six of seven predictions held):
- Phase sum = 0 exactly (Σarg(λ) mod 2π = 0.000000π) ✓
- 69/31 split: 68.75 / 31.25 per scale (structural vs processual); 0.52% from cosmological DE/matter ✓
- A3 outer/inner identical to L2 = 4.39e-16 (machine precision); middle α-enriched by 2.47e-3 ✓
- Leading |λ| = 1 + 2α exactly (same as ℂ⁶⁴) ✓
- Spectral gap ≈ α/P (ratio 1.056; O(α) correction open) ≈
- Leading-eigenvalue angle: −128.26° (not tetrahedral 109.47°; representation-dependent) ✗
- Sector split 244/268 (not 35/29 as at ℂ⁶⁴; representation-dependent) ✗

**What this confirms.** 69/31 is representation-invariant (now three independent representations produce it); phase closure at three-scale holds at both ℂ⁴ and ℂ⁸ single-scale resolutions; A3 is a scale symmetry at the operator level. What it leaves open: precise coefficient of the spectral-gap α/P scaling, meaning of the −128.26° angle, and the 244/268 sector ratio.

---

### 2-original. ℂ⁵¹² three-scale octave (original spec)

The v11 findings note this as next. Infrastructure exists: `experiments/unified_expression_T_v11_C64.py` handles three-scale ℂ⁶⁴ = ℂ⁴ ⊗ ℂ⁴ ⊗ ℂ⁴. Upgrade to three-scale octave.

**Predictions to verify.**
- Phase sum = 0 exactly (tensor-product structure; 96·(−π/3) = −32π ≡ 0 mod 2π)
- Cosmological 69/31 split survives at three-scale higher resolution (and whether it tightens)
- Expanding/contracting sector split at 512 states (analogue of ℂ⁶⁴'s C(R,T)/(S−C(R,T)) = 35/29)
- Leading eigenvalue at tetrahedral angle 109.47° or a new angle
- Spectral gap scaling (ℂ⁴: α, ℂ⁸: α/P, ℂ⁶⁴: α/P, ℂ⁵¹²: ?)
- A3 consistency: outer/inner scales identical to machine precision, middle scale α-enriched
- Top states: does |•, Φ, •, Φ, •, Φ⟩ (full aperture-field alternation across three scales) dominate as |•, Φ, •⟩ did in ℂ⁶⁴?

**Deliverables.** `experiments/unified_expression_T_v14_C512.py` (three-scale octave); `experiments/T_operator_findings_v14_C512.md` with converged weights, phase clusters, eigenvalue spectrum, A3 verification; update `plans/unified_expression_unlock_plan.md` marking direction #15 extended.

**Edge.** Pure infrastructure extension; the v11 machinery generalizes cleanly.
**Risk.** Convergence time. ℂ⁸ needed ~300K iterations; ℂ⁵¹² may need millions. Budget accordingly or use sparse eigenvalue methods.

### 3. Grammar predictiveness scoreboard ✓ DONE 2026-04-22

**Status: complete.** See `plans/predictions_scoreboard.md`, `docs/circumpunct_predictions.html` (Scoring & Status section), and `docs/predictions_history.html`.

Headline results:
- Full audit of 52 entries across 10 domain buckets (α-ladder, cosmological, particle masses, mixing, molecular geometry, bond energies, periodic table, nuclear, biology, pre-registered)
- Classification: 44 K (known-fit), 4 P (pre-registered), 4 D (derived identity)
- Four P entries locked with pre-committed bands: P1 (1/α next decimal, ±5 ppb), P2 (Si≡Si/Si−Si length ratio, ±1%), P3 (mycelial Murray's Law exponent, ±0.15), P4 (five-virtue sequence Cohen's d ≥ 0.5)
- Retraction protocol defined: Revision Notice blocks in circumpunct_framework.md, history-page logging, no silent retraction, post-hoc refits flagged "re-fit after failure" in Brier score
- Flag threshold: if 2 of 4 P fail their bands, piece #3 reopens with new targets
- Honest framing: 44 K entries show the grammar is restrictive (sparse pool, forced integers, tight fits); no P has settled, so predictiveness is not yet on record

**Original task description (for reference):**

The biggest epistemic payoff. Every existing ladder formula is a fit given α. The open question: does the grammar reproduce a NOT-YET-measured constant without per-formula tuning? `docs/circumpunct_predictions.html` stakes pre-registered predictions on specific future measurements. Upgrade that page from narrative to scoreboard.

**What the scoreboard needs.**
- Pre-registered predictions table: constant, formula, framework integers used, predicted value, measurement uncertainty band, target timeline, data source, live/retracted/confirmed status
- Primary targets: three extended Higgs states (mass and couplings), muon g−2 anomalous contribution at higher precision, proton radius at next-generation precision, α drift across cosmic time (QSO spectra), neutrino masses and mixing angles, Δ_ν / Δ_atm mass splittings, electron EDM upper bound
- Secondary targets: dark matter phase identification (left-half-plane signature in direct-detection), HRV coherence ≈ 0.1 Hz in clinical populations, bond-angle predictions for unmeasured heavy-atom molecules
- Scoring rule: pass/fail thresholds in advance; Brier score tracked over time; retraction protocol if a prediction fails
- Falsification log: which predictions failed, what the failure mode said about the framework

**Deliverables.** Rewrite `docs/circumpunct_predictions.html` as a live scoreboard (each prediction a card with metadata). Add `plans/predictions_scoreboard.md` with the scoring rules, threshold definitions, and retraction protocol. Spin up a companion `docs/predictions_history.html` for the failure/success log that grows over time.

**Edge.** Converts "structural grammar" to "testable grammar"; anyone can check the framework against future data.
**Risk.** Pre-registration is only meaningful if the thresholds are set before data comes in; need honest thresholds, not wide-enough-to-always-pass.

### 4. Nuclear potential shape

§16.5 derives the seven nuclear magic numbers (2, 8, 20, 28, 50, 82, 126) and the single-intruder theorem from T = 3. The nuclear potential shape itself (Woods-Saxon, harmonic-oscillator-plus-spin-orbit) is currently empirical input.

**What to show.** The potential shape is forced by the same pump-cycle geometry that gives the magic numbers. Candidate routes:
- Potential = boundary (○) filter profile; Woods-Saxon edge = ○ filtration at nuclear scale
- Spin-orbit coupling magnitude from i² = −1 at the 1.5D station (already identified structurally; currently unfit in magnitude)
- Harmonic-oscillator well depth from the pump-cycle amplitude at nuclear Φ
- Deformation of heavy nuclei (quadrupole, octupole) as half-integer-station signatures

**Deliverables.** `docs/nuclear_potential.html` with the shape derivation, predictions for spin-orbit splitting magnitudes, and deformation signatures; update §16.5 in circumpunct_framework.md; verify predictions against measured single-particle energies in ²⁰⁸Pb and ¹³²Sn (cleanest doubly-magic nuclei).

**Edge.** Nuclear physics is where the framework has cleanest quantitative success on integer data; shape derivation would upgrade that from "magic numbers explained" to "full single-particle spectrum explained."
**Risk.** Nuclear potentials are historically sticky. The framework gets magic numbers for free; the shape might require more than T = 3.

### 5. Empirical tests catalog

Three clean falsification handles, each testable on existing data.

**β_•/β_○ vs cancer aggressiveness.** §18.11.5 predicts the ratio correlates with tumor grade. Existing pathology data (Ki-67 proliferation index / caspase-3 activation) already measures these in immunohistochemistry archives. Propose a meta-analysis across published tumor series; threshold: Pearson r > 0.6 across at least three independent cohorts.

**α drift across cosmic time.** Sensitivity: 10⁻⁶ over Hubble time. Current bound from QSO absorption spectra: |Δα/α| < 10⁻⁶ at z ≈ 4. The framework predicts α is fixed (κ_{0,0} is a coupling strength, not a variable field). Threshold: any measured Δα/α > 10⁻⁶ falsifies; below 10⁻⁶ consistent.

**Balance parameter ≈ 0.5 in equilibrium.** HRV coherence at 0.1 Hz (6 breaths/min) in resonance-trained subjects; molecular dynamics equilibrium configurations; steady-state turbulence energy-cascade distributions. The framework predicts ◐ = 0.5 in every equilibrium system. Threshold: |◐ − 0.5| < 0.05 across at least three independent equilibrium-type systems.

**Deliverables.** `docs/empirical_tests.html` with the three tests, pre-registered thresholds, data sources, and how to run each. Add each as a row in the predictions scoreboard (#3). Link to published datasets where available.

**Edge.** Each test can be run on existing published data; no new experiment needed.
**Risk.** Heart-rate-variability data is noisy; molecular dynamics has many definitions of "equilibrium"; need careful operational definitions before claiming pass/fail.

### 6. Absolute masses (Mount Everest)

m_μ/m_e is pinned at 5 ppm. m_τ/m_e at 1 ppm. m_p/m_e at 5.35 ppm. Every mass ratio is a fit given α. The base mass m_e in absolute units (or any one particle mass in absolute units) is input.

**Two routes, roughly equal hardness.**

**Route A: Electron mass from Planck units and α.** The Planck-to-electron ratio M_Pl/m_e = (1/α)^(21/2) × √2/φ is pinned at 0.008% (§27.7j). If M_Pl itself is pool-native (candidate: M_Pl is the ⊙Λ scale of the nesting chain for our universe, or something derivable from the Hubble volume), then m_e follows from the ratio. The open question: what sets M_Pl? Gravity's ladder (3D) should force it from G; check whether α_G, φ, and pool integers assemble it from first principles.

**Route B: Electron mass from the cosmological budget.** The universe's total energy is the sum across all ⊙s in the nesting chain; the electron's position on that chain fixes its mass. The 5%/27%/68% cosmological budget (§10.10a) already partitions E at our scale; whether the electron's share within the 5% visible matter follows from the 64-state architecture or the i-cycle quadrant decomposition is open.

**Deliverables.** `docs/absolute_masses.html` with both routes developed; pick the more tractable one for a first attempt. Target: predict m_e in kg (or equivalently m_e/M_Pl or m_e in eV) from framework integers and α to better than 1%. A successful derivation would be the single biggest upgrade the framework could receive.

**Edge.** Genuine Theory-of-Everything territory; nothing in the framework currently pins absolute scales.
**Risk.** The framework may be dimensionless by construction (A0 says E = 1; absolute units require a scale-fixing input that the framework may not contain). If so, the genuine answer is "absolute masses require an external scale choice; the framework pins all dimensionless ratios given α and any one mass."

---

## Walking order

1. **Bond energy outliers** (1-2 days; three independent small pieces; warm-up) — pending
2. **ℂ⁵¹² octave** (2-3 days; mostly infrastructure; v11 machinery generalizes) — ✓ DONE 2026-04-22
3. **Grammar predictiveness scoreboard** (1 week; rewrite predictions page; set up scoring rules and retraction protocol; lock pre-registered thresholds) — ✓ DONE 2026-04-22
4. **Empirical tests catalog** (3-4 days; documentation + existing-data analysis; slots into scoreboard) — pending
5. **Nuclear potential shape** (1-2 weeks; real derivation work; most likely to need course-correction) — pending
6. **Absolute masses** (open-ended; may end in "the framework is dimensionless"; that is itself a clean result) — pending

## Verification at each step

Every piece ships with:
- A testable quantitative prediction (threshold and data source pre-committed)
- A falsification path (what measurement or derivation failure retracts the claim)
- A cross-reference to its position in the ladder (which rung, which station)
- An accuracy audit (where the formula departs from measurement and by how much)

After each piece, verify against the rest of the framework:
- Does it preserve existing sub-percent fits? (bond-energy baseline must not degrade; mass ratios must still hold)
- Does it introduce new integers not in the pool? (if yes, flag for review)
- Does it shift the α closed form? (if yes, reopen §27.7a)
- Does it add a new Route for T = 3 self-determination? (current count: 7; a new route would be Route 8)

## What "done" looks like

All six pieces walked; every open flag in CLAUDE.md either closed or reclassified as out-of-scope; the predictions scoreboard populated with pre-registered thresholds and running against incoming measurements; three empirical tests with scored results; nuclear potential shape derived or the gap clearly named; absolute masses either pinned or the dimensionless-framework conclusion documented as the genuine answer.

## Cross-references

- `circumpunct_framework.md` §27.7a (α), §27.7b (T = 3 routes), §16.4-16.5 (bonds, nuclear)
- `docs/alpha_derivation.html` (factor-level audit; closed 2026-04-22)
- `docs/octave_wrap_lemma.html` (Routes 6 and 7 for T = 3)
- `docs/circumpunct_predictions.html` (current predictions; upgrade target in piece #3)
- `plans/unified_expression_unlock_plan.md` (the conservation-form investigation; piece #2 extends direction #15)
- `experiments/unified_expression_T_v11_C64.py` (three-scale ℂ⁶⁴; v14 extends to ℂ⁵¹²)
