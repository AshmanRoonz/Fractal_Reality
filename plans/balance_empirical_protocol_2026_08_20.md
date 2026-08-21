# Balance-Attractor Empirical Protocol

**Status:** executable pre-registration scaffold, 2026-08-20, v1.1. No natural-system data have yet been collected. Passing synthetic controls validates the analyzer, not the framework's physical claim. **Framework integration COUNTERSIGNED (Ashman, 2026-08-21, "Do it. Signed"; disposition 9 in `plans/countersign_batch_2026_08_21.md`). Run 1 (the Xorzo2 spine, instrument validation): `plans/balance_xorzo2_run_2026_08_21.md`.**

## 0. Purpose

This protocol turns the statement

> Stable systems should have balanced input and output, convergence and emergence.

into three claims that can fail independently:

1. **Accounting closure:** the measured flows explain the change of stored quantity inside the stated boundary.
2. **Complete-cycle balance:** a bounded persistent system has equal total convergence and emergence over a sufficiently long record or a closed cycle.
3. **Restoring attraction:** an imbalance changes later flow in the opposite direction, with the recovery point at \(b=1/2\).

The companion analyzer is

`experiments/balance_empirical_test_v1.py`.

The protocol deliberately does not treat a mean near \(1/2\) as evidence of an attractor. Conservation, centering, and attraction are different propositions.

## 1. Variables and Accounting Boundary

Choose one conserved or approximately conserved quantity and one explicit system boundary before looking at the result. All rates must describe that same quantity in compatible units.

Let

\[
C(t)=I(t)+G(t)
\]

be total convergence, where \(I\) is boundary inflow and \(G\) is internal generation. Let

\[
E(t)=O(t)+L(t)
\]

be total emergence, where \(O\) is boundary outflow and \(L\) is internal loss. Let \(X(t)\) be the quantity stored inside the boundary. The accounting equation is

\[
\dot X=C-E.
\]

Define

\[
b(t)=\frac{C(t)}{C(t)+E(t)}.
\]

Then

\[
2b-1=\frac{C-E}{C+E}.
\]

If \(G\) and \(L\) do not exist in the chosen application, record them as zero. If they exist but are not measured, the experiment does not test total convergence against total emergence.

## 2. Exact Finite-Window Identity

For any observed interval with total throughput

\[
Q=\int(C+E)\,dt>0,
\]

the throughput-weighted balance is exactly

\[
\bar b_Q
=
\frac{\int(C+E)b\,dt}{Q}
=
\frac12
+
\frac{\int(C-E)\,dt}{2Q}.
\]

When the accounting closes,

\[
\bar b_Q
=
\frac12
+
\frac{X(T)-X(0)}{2Q}.
\]

This is an identity, not a fitted prediction. Its empirical content lies in whether the chosen flows close the independently measured stock and whether stock change becomes negligible relative to cumulative throughput.

## 3. Data Contract

Use a CSV with one observation per row. Column names are case-insensitive.

| Column | Required | Meaning |
|---|---:|---|
| `time` | yes | Time within a trial; it must increase strictly |
| `convergence` | yes | Measured boundary input rate \(I\) |
| `emergence` | yes | Measured boundary output rate \(O\) |
| `stock` | strongly recommended | Independently measured stored quantity \(X\) |
| `external_convergence` | no | Internal generation \(G\); zero if absent |
| `external_emergence` | no | Internal loss \(L\); zero if absent |
| `trial` | recommended | Independent run or perturbation episode; time may reset between trials |
| `cycle` | optional | Cycle owning the interval that begins at this row |

Accepted aliases include `input` for `convergence`, `output` for `emergence`, `generation` for `external_convergence`, `loss` for `external_emergence`, and `storage` for `stock`.

Rates must be nonnegative. Total convergence plus total emergence must be positive at every observation. Missing values are rejected rather than silently imputed.

### Minimum record

Ten rows are accepted for mechanical testing, but they are not a scientifically adequate sample by themselves. Trial duration must be long enough to observe recovery or a complete cycle. Sampling must be fast enough that the smallest tested lag resolves the proposed feedback time.

## 4. Measurement Sequence

### Stage A: boundary and sensor audit

1. Name the conserved quantity, system boundary, units, and every known source and sink.
2. Calibrate convergence, emergence, and stock instruments independently.
3. Synchronize their clocks.
4. Estimate measurement error before testing balance.
5. Set balance and accounting tolerances from that error budget, not from the observed answer.
6. **Clamp check (added 2026-08-21, from Run 1's finding):** identify every normalization, homeostatic clamp, or per-sample closure in the system or measurement chain BEFORE selecting the boundary. A boundary whose stock closes at every sample pins b at 1/2 identically and makes every attraction diagnostic undefined; a single-signal derivation of both flows makes accounting closure a construction that carries no evidential weight. Declare both conditions where present.

If the stock trajectory is not explained by integrated \(C-E\), stop. A failed accounting boundary cannot adjudicate the balance hypothesis.

### Stage B: passive bounded record

Observe the unperturbed system for many characteristic response times or many complete cycles. Record:

\[
R(T)=\frac{\int_0^T(C-E)\,dt}{\int_0^T(C+E)\,dt}.
\]

The bounded-persistence prediction is \(R(T)\to0\). A finite experiment can show convergence toward zero within uncertainty; it cannot prove the infinite-time limit.

### Stage C: controlled perturbation

Passive stationarity is not enough. Begin independent trials on both sides of balance:

1. Create a measured convergence surplus, \(b>1/2\).
2. Create a matched emergence surplus, \(b<1/2\).
3. Release the intervention without changing the accounting boundary.
4. Measure recovery in randomized trial order across several perturbation magnitudes.
5. Include sham perturbations and a deliberately non-restoring control.

Use a pilot only to estimate noise and response time. Then choose the number of independent trials with a prospective power calculation. The analyzer's minimum of three labeled trials is a software guardrail, not an evidential standard.

## 5. Dynamic Predictions

The local model tested by the analyzer is

\[
\frac{db}{dt}
=
a+s\left(b-\frac12\right).
\]

The half-attractor prediction is

\[
a=0,
\qquad
s<0.
\]

The restoring rate is

\[
\lambda=-s>0,
\]

and the freely fitted equilibrium is

\[
b_*
=
\frac12-\frac{a}{s}.
\]

The nonlinear sign prediction is

\[
\left(b-\frac12\right)A(b)<0,
\]

where \(A(b)\) is conditional drift. The analyzer reports both a linear fit and quantile-binned conditional drift, so curvature cannot be hidden by one slope.

For explicit perturbation trials it also reports

\[
r_j
=
\frac{|b_j(T)-1/2|}{|b_j(0)-1/2|}.
\]

A recovering trial has \(r_j<1\). A convincing attractor study should show contraction from both sides over independent trials, not merely one favorable trajectory.

## 6. Half Versus a Freely Fitted Equilibrium

The analyzer fits two local models:

1. half fixed: \(db/dt=s(b-1/2)\);
2. equilibrium free: \(db/dt=a+s(b-1/2)\).

It reports

`bic_difference_half_minus_free`.

A positive value favors the freely centered model; a negative value favors the half-fixed model after accounting for the extra parameter. The bootstrap interval for \(b_*\) is the primary centering diagnostic. If it excludes \(1/2\), the observed dynamics are restoring but detectably centered elsewhere.

No finite experiment verifies exact equality. The correct conclusion is "compatible with one half at the stated resolution," not "proved equal to one half."

## 7. The Oscillator Trap

A neutral oscillator

\[
b(t)=\frac12+A\cos(\omega t)
\]

is balanced over every complete period and repeatedly returns to \(1/2\), but its amplitude does not decay. It has no stable attractor.

At finite forward lag \(\tau\), regressing the increment on the present imbalance gives

\[
\frac{\mathbb E[b(t+\tau)-b(t)\mid b(t)]}{\tau}
=
\frac{\cos(\omega\tau)-1}{\tau}
\left(b(t)-\frac12\right),
\]

which has a negative slope. A one-lag analysis would falsely call this restoring.

The distinction appears as \(\tau\to0\):

\[
\frac{\cos(\omega\tau)-1}{\tau}
\sim
-\frac{\omega^2\tau}{2}
\to0
\]

for the neutral oscillator, while a dissipative relaxer has a nonzero negative infinitesimal slope. Therefore the analyzer sweeps several lags. A restoring magnitude that strengthens with lag triggers a hidden-state or oscillator warning. Independent perturbation trials and amplitude contraction remain the decisive test.

## 8. Cycle Test

When cycle labels are supplied, the label on a row applies to the sample interval beginning at that row. The analyzer integrates every interval exactly once and reports each cycle's

\[
R_k
=
\frac{\int_{\text{cycle }k}(C-E)\,dt}
{\int_{\text{cycle }k}(C+E)\,dt}.
\]

A closed stock cycle predicts \(R_k=0\) within measurement uncertainty. Instantaneous \(b(t)\) may remain far from \(1/2\) through much of the cycle.

## 9. Commands

First verify the analyzer against its controls:

```bash
python3 experiments/balance_empirical_test_v1.py --self-test
```

Analyze observations and retain the complete report:

```bash
python3 experiments/balance_empirical_test_v1.py observations.csv \
  --lags 1,2,4,8 \
  --balance-tolerance 0.01 \
  --accounting-tolerance 0.01 \
  --json balance_report.json
```

The tolerances above are examples only. Replace them with values justified by the instrument error budget.

## 10. Verdict Meanings

| Analyzer result | Meaning |
|---|---|
| `half_attractor_candidate_under_repeated_trials` | Restoring drift, half-compatible equilibrium, no oscillator warning, and repeated endpoint contraction |
| `observationally_restoring; perturbation_test_needed` | Passive drift is compatible with restoration, but causal attraction has not been tested |
| `restoring_but_not_to_half` | The system returns toward a detectably biased equilibrium |
| `evidence_against_a_half_attractor` | The shortest-lag conditional drift points away from half |
| `possible_hidden_state_or_oscillator` | Finite-lag mean reversion may be caused by projected cyclic dynamics |
| `inconclusive` | Sampling, variation, or uncertainty does not resolve drift direction |
| `balance_constrained_by_construction` (added 2026-08-21) | The balance observable has zero variance because a clamp or per-sample normalization pins it; attraction is undefined at this boundary, and the analyzer's per-lag "not enough balance variation" skips plus a not_tested assessment are the signature (Run 1, the Xorzo2 spine, is the worked case) |

These are disciplined triage labels, not automatic publication claims.

## 11. Disconfirmation Logic

The claims fail at different levels:

1. **Accounting failure:** observed stock change is not explained by counted flows. This rejects the measurement boundary, not the balance dynamics.
2. **Bounded-persistence failure:** accounting closes, stock is independently shown to remain bounded, throughput grows, but normalized cumulative mismatch does not approach zero. This contradicts at least one stated premise or conservation itself.
3. **Half-centering failure:** controlled, well-resolved recovery repeatedly favors \(b_*\ne1/2\) after complete accounting. This rejects the half-centered dynamic law in that domain.
4. **Attraction failure:** perturbations do not contract, conditional drift is neutral or repelling, or apparent restoration vanishes as sampling lag decreases. This rejects attraction even if cycle balance holds.
5. **Predictive failure:** an alternative equilibrium or feedback law predicts held-out recovery better than the half-attractor model.

## 12. What Would Be Novel

For a conserved stock, equality of total inflow and outflow at steady state is standard conservation. Renaming that equality convergence and emergence does not by itself create a new physical prediction.

The framework can add scientific content by predicting, before measurement:

1. the non-obvious physical variables that instantiate convergence and emergence;
2. the correct system boundary and missing channels;
3. why the recovery point is \(1/2\) rather than a fitted \(b_*\);
4. the feedback law or relaxation-rate scaling;
5. a cross-domain invariant that standard conservation alone does not imply.

The first physical study should therefore serve as instrument validation. A later study must pre-register at least one framework-specific result beyond the accounting identity.

## 13. Current Verification Record

The synthetic suite contains four adversarial cases:

1. a dissipative relaxer centered exactly at \(1/2\);
2. a dissipative relaxer centered at \(0.62\);
3. a repeller centered at \(1/2\);
4. a neutral oscillator centered at \(1/2\) and exactly balanced over complete cycles.

The analyzer classifies them respectively as:

1. `half_attractor_candidate_under_repeated_trials`;
2. `restoring_but_not_to_half`;
3. `evidence_against_a_half_attractor`;
4. `possible_hidden_state_or_oscillator`.

Across all four controls, the finite-window balance identity holds to machine precision.

## Revision History

- 2026-08-21 v1.2: the constraint case added (Stage A clamp check; the balance_constrained_by_construction verdict), from Run 1's finding; countersigned as batch disposition 10.
- 2026-08-21 v1.1: countersigned (batch disposition 9); Run 1 commissioned; status updated, content unchanged.
- 2026-08-20 v1.0: data contract, exact finite-window audit, perturbation protocol, free-equilibrium comparison, lag identifiability safeguard, cycle test, falsifiers, and synthetic controls.
