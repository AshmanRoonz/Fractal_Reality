# Balance Empirical Run 2: Breath

**Status: first natural-system run under `plans/balance_empirical_protocol_2026_08_20.md` v1.2 (the amended protocol, with the Stage A clamp check this run is the first to execute). Commissioned by Ashman ("Let's do it," 2026-08-21; disposition 10 in `plans/countersign_batch_2026_08_21.md`). Part I (this commit) is the Stage A declaration, written and committed BEFORE any signal is processed or any result looked at; Part II (a later commit) carries the run. Git history is the timestamp.** Ceiling declared up front: the data are passive public recordings with no perturbation trials, so the best reachable verdict is "observationally_restoring; perturbation_test_needed," and per protocol §12 this run is the second instrument-validation rung (the instrument meeting a genuinely oscillatory natural signal), not a framework-discriminating test.

---

## Part I: Stage A declaration (before processing)

### 1. System, quantity, boundary

- **System:** resting human breathing, recorded by respiration belt.
- **Conserved quantity:** lung air volume above baseline, measured through the belt signal as an uncalibrated linear proxy V(t) (arbitrary units). The balance observable b is a ratio of positive to total variation, hence scale-invariant, so calibration is unnecessary; this is declared as the reason an uncalibrated proxy is admissible.
- **Boundary:** the lungs. Convergence = inspiratory flow (air in), emergence = expiratory flow (air out). Known unmeasured channels, declared: gas exchange (O₂ uptake versus CO₂ output differ by the respiratory quotient, a sub-percent volume asymmetry), humidity and temperature volume changes, and belt nonlinearity. These enter the tolerance budget below.
- **Data (frozen):** the three respiration-bearing recordings in the NeuroKit2 repository (`neuropsychology/NeuroKit`, commit ff419d983568ef492eb8d229af643c0ef0100b32, dated 2026-03-01; example data recorded with BIOPAC, per that project's documentation), fetched by pinned raw URLs:
  - `bio_resting_5min_100hz.csv` (RSP column; 30,000 samples; resting) → trial `rest-5min`
  - `bio_resting_8min_100hz.csv` (RSP column; 50,682 samples; resting) → trial `rest-8min`
  - `bio_eventrelated_100hz.csv` (RSP column; 15,000 samples; picture-viewing task) → trial `task-2.5min`, its condition carried in the label
  - The 200 Hz JSON copy of the 8-minute session is excluded to avoid double-counting one session. Subject identity across files is not documented; trials are declared as recordings, not subjects. Raw files are cached in the session scratchpad and not committed; the derived ledger is.

### 2. Clamp check (protocol Stage A item 6, first execution)

- **Per-sample closure clamp:** none. The belt signal is free-running; no normalization pins the ledger, so b is not constrained (the Run 1 failure mode is absent).
- **Single-signal derivation:** PRESENT. Both flows derive from V(t) as its signed increments, so stock closure is a construction and the accounting verdicts carry **no evidential weight** in this run. Declared here per the amended protocol; the informative content is confined to the dynamics of b.

### 3. Preprocessing and ledger construction (frozen)

1. Read the RSP column at 100 Hz; time in seconds.
2. Detrend: subtract a 30-second rolling-median baseline, computed on a 1 Hz decimated grid and linearly interpolated back (removes belt baseline wander slower than ~30 s; preserves the 3-6 s breath cycle). V = the detrended signal.
3. Windows of **5 seconds** (500 samples), chosen at or above the typical adult breath period so each row averages roughly one full cycle, targeting multi-breath volume homeostasis rather than the intra-breath cycle; residual cyclicity is exactly what the analyzer's lag sweep exists to flag, and that behavior on a real oscillatory signal is this run's validation target.
4. Per window: convergence rate = (sum of positive sample-to-sample increments of V)/5 s; emergence rate = (sum of negative increments' magnitude)/5 s; stock = V at the window's first sample; time = window start in seconds; trial as labeled above. Windows with zero total variation (flatline or dropout) are dropped with the count reported.
5. Expected row count ~190 across the three trials (declared for the transition-count sanity check; lags 1, 2, 4, 8 windows = 5 to 40 s).

### 4. Tolerances (frozen, from the budget, before looking)

- **Balance tolerance 0.02:** net lung-volume drift over a resting record is bounded by roughly one tidal volume against a throughput of hundreds of tidal volumes (~0.5%), plus detrending leakage and the declared unmeasured channels (respiratory quotient ~1%, belt nonlinearity); budgeted at 2%.
- **Accounting tolerance 0.05:** trapezoid integration over 5 s windowed rates against point-sampled stock; same discretization class as Run 1, budgeted at 5%. Carries no weight regardless, per the clamp check.
- **Analyzer invocation (frozen):** `python3 experiments/balance_empirical_test_v1.py experiments/balance_breath_observations_v1.csv --lags 1,2,4,8 --bootstrap-samples 1000 --seed 20260821 --balance-tolerance 0.02 --accounting-tolerance 0.05 --json experiments/balance_breath_report.json`

### 5. Declared expectations, informative outputs, and disconfirmers

**Expected with no evidential weight:** cycle-complete records give near-zero normalized mismatch (breathing returns to baseline); stock closure within budget (construction).

**Informative:**

1. **The lag-sweep behavior on a real oscillatory system:** whether the analyzer's oscillator guard handles the breath cycle correctly (a `possible_hidden_state_or_oscillator` flag would be the instrument CORRECTLY detecting respiratory cyclicity, not a failure; a clean restoring pattern would indicate the 5 s window successfully averaged the cycle).
2. **Drift direction at the shortest lag** for windowed b: established physiology (volume homeostasis, chemoreflex drive) predicts restoration; a repelling verdict would be investigated as a preprocessing or windowing artifact first, and that order of suspicion is declared now.
3. **The freely fitted equilibrium b\* against 1/2:** the framework-relevant number. Resting breathing should be compatible with 1/2; a bootstrap interval excluding 1/2 would be reported as a detected bias (instrument nonlinearity being the leading suspect, declared).
4. **Verdict ceiling:** "observationally_restoring; perturbation_test_needed" at best; no perturbations exist in these data. Any stronger-sounding verdict would itself indicate an analyzer problem and be treated as such.

**Run-level disconfirmers:** none of these outcomes can disconfirm the framework's balance claims at this rung (declared); they validate or indict the instrument and the boundary choice. A future perturbation study (breath-holds, paced breathing, sighs, with consent and proper collection) is what could carry evidential weight, and its Stage A would build on this run's findings.

**End of Part I. No signal has been processed at this commit.**
