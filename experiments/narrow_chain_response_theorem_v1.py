#!/usr/bin/env python3
"""Verification and Stage 0 instrument characterization for the narrow chain.

Created: 2026-08-21
Last updated: 2026-08-21
Version: 1.0

Revision history:
- 2026-08-21 v1.0: initial. V1-V4 verify the Response Theorem of
  plans/one_narrow_chain_2026_08_21.md section 3 numerically. V5 runs the
  four pre-declared synthetic breathers (N1, N1s, N2, N3) through the exact
  Run 2 pipeline (100 Hz synthesis, 30 s rolling-median detrend at 1 Hz,
  diff, 5 s sign-split windows, three trials of 5/8/2.5 min) and the
  unmodified Run 2 analyzer invocation (lags 1,2,4,8; bootstrap 1000;
  seed 20260821; tolerances 0.02/0.05). V6 rehearses the Stage A estimator
  suite on the reduced PI model with known ground truth (labelled
  rehearsal, not calibration).

Part I of the plan file is committed before this script runs (the standing
pre-registration discipline); expectations E1-E5 are declared there.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import median_filter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import balance_empirical_test_v1 as bal  # noqa: E402  (the Run 2 analyzer, unmodified)

SCRATCH = Path(
    "/tmp/claude-0/-home-user-Fractal-Reality/"
    "da321b11-2522-50c4-b92b-9362acab7466/scratchpad"
)
FS = 100
WINDOW_S = 5.0
WINDOW_N = int(WINDOW_S * FS)
BASELINE_S = 30
TRIALS = [("n-5min", 300.0), ("n-8min", 480.0), ("n-2p5min", 150.0)]
ANALYZER_ARGS = dict(
    lags=[1, 2, 4, 8],
    bootstrap_samples=1000,
    seed=20260821,
    balance_tolerance=0.02,
    accounting_tolerance=0.05,
)


# ----------------------------------------------------------------------
# The reduced model: x' = -kp*x - ki*z + w,  z' = x
# ----------------------------------------------------------------------

def simulate(kp, ki, x0, z0, T, dt=0.001, load=0.0):
    n = int(T / dt)
    x, z = x0, z0
    xs = np.empty(n)
    for i in range(n):
        xdot = -kp * x - ki * z + load
        x += xdot * dt
        z += x * dt
        xs[i] = x
    return xs, z


def v1_proportional_only():
    print("\nV1  proportional-only (ki = 0): no crossing, area A/kp, offset under load")
    ok = True
    for kp in (0.3, 1.0, 3.0):
        xs, _ = simulate(kp, 0.0, 1.0, 0.0, 60.0 / kp)
        area = np.sum(xs) * 0.001
        crossed = bool(np.any(xs < -1e-9))
        offset_xs, _ = simulate(kp, 0.0, 0.0, 0.0, 200.0 / kp, load=0.5)
        offset = offset_xs[-1]
        good = (not crossed) and abs(area - 1.0 / kp) < 2e-3 and abs(offset - 0.5 / kp) < 2e-3
        ok &= good
        print(f"    kp={kp:4.1f}  crossed={crossed!s:5}  area={area:+.4f} (A/kp={1/kp:.4f})"
              f"  load offset={offset:+.4f} (d/kp={0.5/kp:.4f})  {'PASS' if good else 'FAIL'}")
    return ok


def v2_pi_crossing_and_repayment():
    print("\nV2  PI (ki > 0): crossing, total area = 0, load rejected")
    ok = True
    cases = [("underdamped", 0.4, 1.0), ("critical", 2.0, 1.0), ("overdamped", 4.0, 1.0)]
    for name, kp, ki in cases:
        xs, _ = simulate(kp, ki, 1.0, 0.0, 400.0)
        area = np.sum(xs) * 0.001
        crossed = bool(np.any(xs < -1e-9))
        load_xs, _ = simulate(kp, ki, 0.0, 0.0, 600.0, load=0.5)
        rejected = abs(load_xs[-1]) < 2e-3
        good = crossed and abs(area) < 2e-3 and rejected
        ok &= good
        print(f"    {name:11s} kp={kp:3.1f} ki={ki:3.1f}  crossed={crossed!s:5}"
              f"  total area={area:+.2e}  load x_inf={load_xs[-1]:+.2e}  {'PASS' if good else 'FAIL'}")
    return ok


def v3_held_debt_scaling():
    print("\nV3  held debt: post-release area = -A*Th, linear in Th")
    kp, ki, A = 1.0, 0.5, 1.0
    ok = True
    areas = []
    for Th in (5.0, 10.0, 20.0, 40.0):
        z_at_release = A * Th          # clamp: x = A, z accumulates A per second
        xs, _ = simulate(kp, ki, A, z_at_release, 600.0)
        area = np.sum(xs) * 0.001
        areas.append(area)
        good = abs(area + A * Th) < 0.05 * A * Th
        ok &= good
        print(f"    Th={Th:5.1f}  post-release area={area:+9.4f}  target={-A*Th:+9.4f}  "
              f"{'PASS' if good else 'FAIL'}")
    slope = np.polyfit([5.0, 10.0, 20.0, 40.0], areas, 1)[0]
    lin = abs(slope + A) < 0.02
    ok &= lin
    print(f"    linear-fit slope vs Th = {slope:+.4f}  (theorem: -A = {-A:.1f})  "
          f"{'PASS' if lin else 'FAIL'}")
    return ok


def v4_regression():
    print("\nV4  regression: conditional means of the noisy system follow the noise-free flow")
    rng = np.random.default_rng(20260821)
    kp, ki, sigma, dt, s = 1.0, 0.5, 0.4, 0.02, 1.0
    n = 1_000_000
    xs = np.empty(n)
    zs = np.empty(n)
    x, z = 0.0, 0.0
    sq = sigma * np.sqrt(dt)
    noise = rng.standard_normal(n)
    for i in range(n):
        x += (-kp * x - ki * z) * dt + sq * noise[i]
        z += x * dt
        xs[i] = x
        zs[i] = z
    lag = int(s / dt)
    # deterministic propagator over s
    Amat = np.array([[-kp, -ki], [1.0, 0.0]])
    from scipy.linalg import expm
    Phi = expm(Amat * s)
    # bin on (x, z), compare E[x(t+s)|bin] with propagated bin mean
    xe = np.quantile(xs[:-lag], np.linspace(0, 1, 7))
    ze = np.quantile(zs[:-lag], np.linspace(0, 1, 7))
    worst = 0.0
    count = 0
    for i in range(6):
        for j in range(6):
            m = ((xs[:-lag] >= xe[i]) & (xs[:-lag] < xe[i + 1])
                 & (zs[:-lag] >= ze[j]) & (zs[:-lag] < ze[j + 1]))
            if m.sum() < 5000:
                continue
            mean_state = np.array([xs[:-lag][m].mean(), zs[:-lag][m].mean()])
            pred = Phi @ mean_state
            obs = xs[lag:][m].mean()
            se = xs[lag:][m].std() / np.sqrt(m.sum() / 50)  # crude autocorr discount
            dev = abs(obs - pred[0])
            worst = max(worst, dev / max(se, 1e-9))
            count += 1
    ok = worst < 4.0 and count >= 20
    print(f"    bins used={count}  worst |obs - predicted| / se = {worst:.2f}  "
          f"(threshold 4)  {'PASS' if ok else 'FAIL'}")
    return ok


# ----------------------------------------------------------------------
# V5: the four synthetic breathers through the exact Run 2 pipeline
# ----------------------------------------------------------------------

def lognormal(rng, mean, cv, size=None):
    s2 = np.log(1.0 + cv * cv)
    mu = np.log(mean) - s2 / 2.0
    return rng.lognormal(mu, np.sqrt(s2), size)


def breather(rng, duration, ratio_mean, walk_sd, pi_gains):
    """One trial of synthetic belt signal at FS Hz.

    ratio_mean: exhale/inhale duration ratio (duty asymmetry).
    walk_sd: per-breath Gaussian step of the end-expiratory level (N2/N3).
    pi_gains: None, or (gp, gi) discrete PI correction of the EE level (N3).
    """
    t_total = 0.0
    ee = 0.0
    z = 0.0
    chunks = []
    while t_total < duration + 10.0:
        ti = float(lognormal(rng, 1.6, 0.15))
        te = float(lognormal(rng, ratio_mean, 0.10)) * ti
        amp = float(lognormal(rng, 1.0, 0.20))
        ni = max(2, int(ti * FS))
        ne = max(2, int(te * FS))
        up = ee + amp * 0.5 * (1.0 - np.cos(np.pi * np.arange(ni) / ni))
        dn = ee + amp * 0.5 * (1.0 + np.cos(np.pi * np.arange(ne) / ne))
        chunks.append(up)
        chunks.append(dn)
        t_total += ti + te
        step = rng.normal(0.0, walk_sd) if walk_sd > 0 else 0.0
        if pi_gains is not None:
            gp, gi = pi_gains
            z += ee
            ee = ee + step - gp * ee - gi * z
        else:
            ee = ee + step
    v = np.concatenate(chunks)
    return v[: int(duration * FS)]


def detrend(v):
    """The Run 2 detrend, reproduced exactly."""
    grid = v[::FS]
    base_grid = median_filter(grid, size=BASELINE_S + 1, mode="nearest")
    t_grid = np.arange(len(grid)) * FS
    base = np.interp(np.arange(len(v)), t_grid, base_grid)
    return v - base


def ledger_rows(v, label):
    """The Run 2 window ledger, reproduced exactly."""
    d = np.diff(v)
    rows = []
    n_windows = len(d) // WINDOW_N
    for k in range(n_windows):
        seg = d[k * WINDOW_N : (k + 1) * WINDOW_N]
        pos = float(np.sum(seg[seg > 0]))
        neg = float(-np.sum(seg[seg < 0]))
        if pos + neg == 0.0:
            continue
        rows.append({
            "time": k * WINDOW_S,
            "convergence": pos / WINDOW_S,
            "emergence": neg / WINDOW_S,
            "stock": float(v[k * WINDOW_N]),
            "trial": label,
        })
    return rows


def run_null(name, seed, ratio_mean, walk_sd, pi_gains):
    rng = np.random.default_rng(seed)
    rows = []
    for label, duration in TRIALS:
        v = breather(rng, duration, ratio_mean, walk_sd, pi_gains)
        rows.extend(ledger_rows(detrend(v), f"{name}-{label}"))
    path = SCRATCH / f"narrow_chain_{name}.csv"
    with path.open("w", newline="") as handle:
        w = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    data = bal.load_csv(path)
    report = bal.analyze(data, **ANALYZER_ARGS)
    return report


def summarize(name, report):
    fit1 = report["conditional_drift"]["fits"][0]
    pat = report["conditional_drift"]["lag_pattern"]
    fw = report["finite_window"]
    eq = fit1["equilibrium_balance"]
    eqci = fit1["equilibrium_ci95"]
    print(f"  {name:4s} verdict={report['attractor_assessment']['overall']:28s}"
          f" accounting={fw['stock_accounting_verdict']}/{fw['finite_window_balance_verdict']}")
    print(f"       lag1 slope={fit1['slope']:+.3f} CI({fit1['slope_ci95'][0]:+.3f},"
          f"{fit1['slope_ci95'][1]:+.3f})  eq={eq:.4f}"
          f" CI({eqci[0]:.4f},{eqci[1]:.4f})  BICdiff={fit1['bic_difference_half_minus_free']:+.1f}")
    print(f"       lag pattern={pat.get('pattern')} ratio={pat.get('magnitude_ratio_last_to_first', float('nan')):.3f}"
          f"  throughput-weighted b={fw['throughput_weighted_balance']:.4f}")
    return fit1, pat, fw


def v5_stage0():
    print("\nV5  Stage 0: four synthetic breathers through the exact Run 2 pipeline + analyzer")
    print("    (expectations E1-E5 pre-declared in plans/one_narrow_chain_2026_08_21.md 4a)")
    specs = [
        ("N1", 101, 1.5, 0.0, None),          # mechanical, duty-asymmetric, closed
        ("N1s", 102, 1.0, 0.0, None),         # mechanical, duty-symmetric, closed
        ("N2", 103, 1.5, 0.1, None),          # mechanical + random-walk EE level
        ("N3", 104, 1.5, 0.1, (0.5, 0.1)),    # PI-corrected EE level (Jury-stable gains)
    ]
    out = {}
    for name, seed, ratio, walk, gains in specs:
        out[name] = run_null(name, seed, ratio, walk, gains)
        summarize(name, out[name])
    # E-flag readouts
    def eq_ci(n):
        return out[n]["conditional_drift"]["fits"][0]["equilibrium_ci95"]
    def slope_ci(n):
        return out[n]["conditional_drift"]["fits"][0]["slope_ci95"]
    def verdict(n):
        return out[n]["attractor_assessment"]["overall"]
    print("\n    E-flag readout:")
    e1 = all(out[n]["finite_window"]["stock_accounting_verdict"] == "within_tolerance"
             and out[n]["finite_window"]["finite_window_balance_verdict"] == "within_tolerance"
             for n in out)
    print(f"    E1 (all pass accounting+balance): {e1}")
    e2 = all(slope_ci(n)[1] < 0 for n in ("N1", "N1s", "N2"))
    print(f"    E2 (feedback-free nulls classified restoring at lag 1): {e2}"
          f"  [verdicts: {verdict('N1')}, {verdict('N1s')}, {verdict('N2')}]")
    n1_lo, n1_hi = eq_ci("N1")
    n1s_lo, n1s_hi = eq_ci("N1s")
    e3a = n1_hi < 0.5
    e3b = n1s_lo <= 0.5 <= n1s_hi
    print(f"    E3 (duty mechanism): N1 eq CI ({n1_lo:.4f},{n1_hi:.4f}) below half: {e3a};"
          f" N1s eq CI ({n1s_lo:.4f},{n1s_hi:.4f}) contains half: {e3b}")
    e4 = slope_ci("N2")[1] < 0
    print(f"    E4 (random-walk stock still classified restoring after detrend): {e4}")
    s2, s3 = slope_ci("N2"), slope_ci("N3")
    overlap = not (s2[1] < s3[0] or s3[1] < s2[0])
    print(f"    E5 (N3 vs N2 indistinguishable): slope CIs overlap: {overlap};"
          f" verdict N2={verdict('N2')}, N3={verdict('N3')}")
    return out


# ----------------------------------------------------------------------
# V6: Stage A rehearsal on the reduced PI model (known ground truth)
# ----------------------------------------------------------------------

def v6_stage_a_rehearsal():
    print("\nV6  Stage A rehearsal on the reduced model (rehearsal, not calibration)")
    rng = np.random.default_rng(20260821)
    kp, ki, sigma = 0.30, 0.03, 0.25   # relaxation ~ seconds-to-tens-of-seconds
    dt = 0.05
    def step(x, z, drive):
        xn = x + (-kp * x - ki * z) * dt + drive
        return xn, z + xn * dt
    # rest segment for identification: 600 s
    n_rest = int(600 / dt)
    xs = np.empty(n_rest)
    x, z = 0.0, 0.0
    sq = sigma * np.sqrt(dt)
    for i in range(n_rest):
        x, z = step(x, z, sq * rng.standard_normal())
        xs[i] = x
    # identification at 1 Hz: regress dx on (x, z_integrated)
    grid = xs[:: int(1 / dt)]
    zg = np.cumsum(grid)  # 1 s steps
    dx = np.diff(grid)
    X = np.column_stack([grid[:-1], zg[:-1], np.ones(len(dx))])
    coef, *_ = np.linalg.lstsq(X, dx, rcond=None)
    kp_hat, ki_hat = -coef[0], -coef[1]
    print(f"    identified from rest: kp_hat={kp_hat:.3f} (true {kp}), "
          f"ki_hat={ki_hat:.4f} (true {ki})")
    # hold trials: end-inhale side A=+1 (Th 10,20,30 x3), end-exhale A=-1 (Th 10,20 x3)
    trials = [(+1.0, th) for th in (10, 20, 30) for _ in range(3)] + \
             [(-1.0, th) for th in (10, 20) for _ in range(3)]
    rhos, sides, ths, crossings = [], [], [], []
    for A, Th in trials:
        x, z = 0.0, 0.0
        for _ in range(int(120 / dt)):     # settle with noise
            x, z = step(x, z, sq * rng.standard_normal())
        z0 = z
        z = z + A * Th                     # clamp accumulates seam debt
        x = A
        n_rec = int(90 / dt)
        rec = np.empty(n_rec)
        for i in range(n_rec):
            x, z = step(x, z, sq * rng.standard_normal())
            rec[i] = x
        area = np.sum(rec) * dt
        rho = -(area) / (A * Th)
        crossed = bool(np.any(np.sign(rec) == -np.sign(A)))
        rhos.append(rho)
        sides.append(A)
        ths.append(Th)
        crossings.append(crossed)
    rhos = np.array(rhos)
    sides = np.array(sides)
    print(f"    crossing fraction: {np.mean(crossings):.2f}  "
          f"(theorem with ki>0: should approach 1)")
    for side, label in ((+1.0, "end-inhale"), (-1.0, "end-exhale")):
        m = sides == side
        print(f"    {label:10s} rho mean={rhos[m].mean():+.3f} sd={rhos[m].std(ddof=1):.3f}"
              f"  n={m.sum()}  (full repayment: +1)")
    se9 = rhos[sides == +1.0].std(ddof=1) / np.sqrt((sides == +1.0).sum())
    print(f"    power note: se(rho) with 9 end-inhale trials ~ {se9:.3f}; "
          f"K2 bands in the plan were set against this scale")
    # rest-predicts-response: deterministic recovery from identified gains
    from scipy.linalg import expm
    ok_pred = True
    A_true = np.array([[-kp, -ki], [1.0, 0.0]])
    A_hat = np.array([[-kp_hat, -ki_hat], [1.0, 0.0]])
    for Th in (10, 30):
        def crossing_time(Am):
            s = np.array([1.0, Th])
            t, dtau = 0.0, 0.1
            P = expm(Am * dtau)
            for _ in range(int(120 / dtau)):
                s = P @ s
                t += dtau
                if s[0] < 0:
                    return t
            return np.inf
        t_true, t_hat = crossing_time(A_true), crossing_time(A_hat)
        ratio = t_hat / t_true if np.isfinite(t_true) else np.nan
        ok_pred &= 0.5 < ratio < 2.0
        print(f"    Th={Th:2d}: predicted crossing time from rest fit {t_hat:.1f} s "
              f"vs true model {t_true:.1f} s (ratio {ratio:.2f}; K3 band [0.5, 2])")
    return ok_pred


def main():
    print("Narrow chain: Response Theorem verification + Stage 0")
    print("plan: plans/one_narrow_chain_2026_08_21.md (Part I committed before this run)")
    r1 = v1_proportional_only()
    r2 = v2_pi_crossing_and_repayment()
    r3 = v3_held_debt_scaling()
    r4 = v4_regression()
    v5_stage0()
    r6 = v6_stage_a_rehearsal()
    print(f"\ntheorem checks: V1={'PASS' if r1 else 'FAIL'} V2={'PASS' if r2 else 'FAIL'}"
          f" V3={'PASS' if r3 else 'FAIL'} V4={'PASS' if r4 else 'FAIL'}"
          f"  rehearsal K3 band: {'PASS' if r6 else 'FAIL'}")
    print("Stage 0 E-flags are findings, not pass/fail; see the plan's Part II.")


if __name__ == "__main__":
    main()
