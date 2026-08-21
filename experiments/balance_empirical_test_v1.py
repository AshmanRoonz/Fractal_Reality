#!/usr/bin/env python3
"""Test balance, accounting closure, and restoring drift in flow data.

Created: 2026-08-20
Last updated: 2026-08-20
Version: 1.0

Revision history:
- 2026-08-20 v1.0: data contract, finite-window balance identity, stock
  accounting audit, conditional-drift lag sweep, block-bootstrap intervals,
  repeated-trial contraction test, cycle audit, and synthetic controls.

Companion protocol:
plans/balance_empirical_protocol_2026_08_20.md

This program does not prove that a system is stable from a finite passive
record. It separates three questions that require different evidence:

1. Were all flows counted consistently with the observed stock?
2. Was convergence balanced by emergence over the observed window or cycle?
3. Did imbalance generate restoring dynamics toward one half?
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np


Vector = np.ndarray


ALIASES: dict[str, tuple[str, ...]] = {
    "time": ("time", "t"),
    "convergence": ("convergence", "input", "inflow", "i"),
    "emergence": ("emergence", "output", "outflow", "o"),
    "external_convergence": (
        "external_convergence",
        "generation",
        "external_gain",
        "gain",
        "g",
    ),
    "external_emergence": (
        "external_emergence",
        "loss",
        "external_loss",
        "l",
    ),
    "stock": ("stock", "storage", "x"),
    "trial": ("trial", "episode", "run"),
    "cycle": ("cycle", "period"),
}


@dataclass(frozen=True)
class Observations:
    time: Vector
    convergence: Vector
    emergence: Vector
    external_convergence: Vector
    external_emergence: Vector
    stock: Vector | None
    trial: np.ndarray
    cycle: np.ndarray | None
    explicit_trials: bool

    @property
    def total_convergence(self) -> Vector:
        return self.convergence + self.external_convergence

    @property
    def total_emergence(self) -> Vector:
        return self.emergence + self.external_emergence


@dataclass(frozen=True)
class LinearDriftFit:
    lag_samples: int
    transition_count: int
    lag_time_median: float
    intercept_at_half: float
    intercept_ci95: tuple[float, float]
    slope: float
    slope_ci95: tuple[float, float]
    restoring_rate: float
    equilibrium_balance: float | None
    equilibrium_ci95: tuple[float, float] | None
    r_squared: float
    half_fixed_slope: float
    bic_half_fixed: float
    bic_free_equilibrium: float
    bic_difference_half_minus_free: float
    restoring_fraction: float
    mean_lyapunov_drift: float


def _resolve_columns(fieldnames: list[str]) -> dict[str, str | None]:
    normalized = {name.strip().lower(): name for name in fieldnames}
    resolved: dict[str, str | None] = {}
    for canonical, aliases in ALIASES.items():
        found = [normalized[name] for name in aliases if name in normalized]
        if len(found) > 1:
            raise ValueError(
                f"multiple columns map to {canonical!r}: {', '.join(found)}"
            )
        resolved[canonical] = found[0] if found else None
    for required in ("time", "convergence", "emergence"):
        if resolved[required] is None:
            options = ", ".join(ALIASES[required])
            raise ValueError(f"missing {required!r} column; accepted names: {options}")
    return resolved


def _parse_float(row: dict[str, str], column: str, row_number: int) -> float:
    raw = row.get(column, "").strip()
    if not raw:
        raise ValueError(f"row {row_number}: missing value in {column!r}")
    try:
        value = float(raw)
    except ValueError as error:
        raise ValueError(
            f"row {row_number}: {column!r} is not numeric: {raw!r}"
        ) from error
    if not math.isfinite(value):
        raise ValueError(f"row {row_number}: {column!r} must be finite")
    return value


def load_csv(path: Path) -> Observations:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header")
        columns = _resolve_columns(reader.fieldnames)
        rows = list(reader)

    if len(rows) < 10:
        raise ValueError("at least 10 observations are required")

    def numeric(canonical: str, default: float | None = None) -> Vector | None:
        column = columns[canonical]
        if column is None:
            if default is None:
                return None
            return np.full(len(rows), default, dtype=float)
        return np.array(
            [_parse_float(row, column, index + 2) for index, row in enumerate(rows)],
            dtype=float,
        )

    time = numeric("time")
    convergence = numeric("convergence")
    emergence = numeric("emergence")
    external_convergence = numeric("external_convergence", 0.0)
    external_emergence = numeric("external_emergence", 0.0)
    stock = numeric("stock")
    assert time is not None
    assert convergence is not None
    assert emergence is not None
    assert external_convergence is not None
    assert external_emergence is not None

    trial_column = columns["trial"]
    explicit_trials = trial_column is not None
    if trial_column is None:
        trial = np.full(len(rows), "record", dtype=object)
    else:
        trial = np.array(
            [row.get(trial_column, "").strip() for row in rows], dtype=object
        )
        if any(not label for label in trial):
            raise ValueError("trial labels may not be blank")

    cycle_column = columns["cycle"]
    cycle: np.ndarray | None
    if cycle_column is None:
        cycle = None
    else:
        cycle = np.array(
            [row.get(cycle_column, "").strip() for row in rows], dtype=object
        )
        if any(not label for label in cycle):
            raise ValueError("cycle labels may not be blank")

    observations = Observations(
        time=time,
        convergence=convergence,
        emergence=emergence,
        external_convergence=external_convergence,
        external_emergence=external_emergence,
        stock=stock,
        trial=trial,
        cycle=cycle,
        explicit_trials=explicit_trials,
    )
    validate_observations(observations)
    return observations


def validate_observations(data: Observations) -> None:
    size = len(data.time)
    arrays = (
        data.convergence,
        data.emergence,
        data.external_convergence,
        data.external_emergence,
        data.trial,
    )
    if any(len(array) != size for array in arrays):
        raise ValueError("all columns must have the same length")
    if data.stock is not None and len(data.stock) != size:
        raise ValueError("stock column has the wrong length")
    if data.cycle is not None and len(data.cycle) != size:
        raise ValueError("cycle column has the wrong length")
    if size < 10:
        raise ValueError("at least 10 observations are required")

    rates = (
        data.convergence,
        data.emergence,
        data.external_convergence,
        data.external_emergence,
    )
    if any(np.any(~np.isfinite(rate)) for rate in rates):
        raise ValueError("flow columns must be finite")
    if any(np.any(rate < 0) for rate in rates):
        raise ValueError("throughput rates must be nonnegative")

    throughput = data.total_convergence + data.total_emergence
    if np.any(throughput <= 0):
        raise ValueError("total convergence plus emergence must be positive")

    if np.any(~np.isfinite(data.time)):
        raise ValueError("time values must be finite")
    if data.stock is not None and np.any(~np.isfinite(data.stock)):
        raise ValueError("stock values must be finite")

    for label, indices in trial_groups(data):
        if len(indices) < 3:
            raise ValueError(f"trial {label!r} needs at least 3 observations")
        if np.any(np.diff(data.time[indices]) <= 0):
            raise ValueError(
                f"time must be strictly increasing within trial {label!r}"
            )


def trial_groups(data: Observations) -> list[tuple[str, Vector]]:
    labels: list[str] = []
    seen: set[str] = set()
    for raw in data.trial:
        label = str(raw)
        if label not in seen:
            labels.append(label)
            seen.add(label)
    return [(label, np.flatnonzero(data.trial == label)) for label in labels]


def cumulative_trapezoid(values: Vector, time: Vector) -> Vector:
    areas = 0.5 * (values[1:] + values[:-1]) * np.diff(time)
    return np.concatenate((np.array([0.0]), np.cumsum(areas)))


def integrate_trials(data: Observations, values: Vector) -> float:
    return float(
        sum(
            np.trapezoid(values[indices], data.time[indices])
            for _label, indices in trial_groups(data)
        )
    )


def finite_window_audit(
    data: Observations,
    balance_tolerance: float,
    accounting_tolerance: float,
) -> dict[str, Any]:
    total_in = data.total_convergence
    total_out = data.total_emergence
    throughput = total_in + total_out
    mismatch = total_in - total_out
    balance = total_in / throughput

    integrated_in = integrate_trials(data, total_in)
    integrated_out = integrate_trials(data, total_out)
    integrated_throughput = integrated_in + integrated_out
    integrated_mismatch = integrated_in - integrated_out
    weighted_balance = integrated_in / integrated_throughput
    normalized_mismatch = integrated_mismatch / integrated_throughput
    identity_target = 0.5 + normalized_mismatch / 2

    audit: dict[str, Any] = {
        "sample_count": len(data.time),
        "trial_count": len(trial_groups(data)),
        "integrated_convergence": integrated_in,
        "integrated_emergence": integrated_out,
        "integrated_throughput": integrated_throughput,
        "integrated_mismatch": integrated_mismatch,
        "normalized_mismatch": normalized_mismatch,
        "throughput_weighted_balance": weighted_balance,
        "balance_identity_error": weighted_balance - identity_target,
        "balance_tolerance": balance_tolerance,
        "finite_window_balance_verdict": (
            "within_tolerance"
            if abs(normalized_mismatch) <= balance_tolerance
            else "outside_tolerance"
        ),
        "instantaneous_balance_mean": float(np.mean(balance)),
        "instantaneous_balance_std": float(np.std(balance, ddof=1)),
    }

    if data.stock is None:
        audit.update(
            {
                "stock_accounting_verdict": "not_tested",
                "stock_note": (
                    "No stock column was supplied. Flow balance can be described, "
                    "but bounded persistence and boundary completeness cannot be "
                    "checked."
                ),
            }
        )
        return audit

    observed_change = 0.0
    predicted_change = 0.0
    squared_errors: list[float] = []
    squared_stock_scale: list[float] = []
    for _label, indices in trial_groups(data):
        local_time = data.time[indices]
        local_stock = data.stock[indices]
        local_mismatch = mismatch[indices]
        predicted_path = local_stock[0] + cumulative_trapezoid(
            local_mismatch, local_time
        )
        observed_change += float(local_stock[-1] - local_stock[0])
        predicted_change += float(np.trapezoid(local_mismatch, local_time))
        squared_errors.extend(((local_stock - predicted_path) ** 2).tolist())
        centered_stock = local_stock - np.mean(local_stock)
        squared_stock_scale.extend((centered_stock**2).tolist())

    closure_error = observed_change - predicted_change
    closure_relative_to_throughput = closure_error / integrated_throughput
    stock_rmse = float(math.sqrt(np.mean(squared_errors)))
    stock_scale = float(math.sqrt(np.mean(squared_stock_scale)))
    normalized_path_rmse = stock_rmse / max(stock_scale, 1e-15)
    observed_change_over_throughput = observed_change / integrated_throughput

    audit.update(
        {
            "observed_stock_change": observed_change,
            "predicted_stock_change": predicted_change,
            "stock_closure_error": closure_error,
            "stock_closure_error_over_throughput": (
                closure_relative_to_throughput
            ),
            "stock_path_rmse": stock_rmse,
            "stock_path_rmse_over_stock_variation": normalized_path_rmse,
            "observed_stock_change_over_throughput": (
                observed_change_over_throughput
            ),
            "accounting_tolerance": accounting_tolerance,
            "stock_accounting_verdict": (
                "within_tolerance"
                if abs(closure_relative_to_throughput) <= accounting_tolerance
                else "outside_tolerance"
            ),
            "boundedness_note": (
                "A finite trace cannot prove boundedness. The reported stock "
                "change and trajectory closure are necessary diagnostics only."
            ),
        }
    )
    return audit


def transition_groups(
    data: Observations, balance: Vector, lag: int
) -> list[tuple[Vector, Vector, Vector]]:
    groups: list[tuple[Vector, Vector, Vector]] = []
    for _label, indices in trial_groups(data):
        if len(indices) <= lag:
            continue
        local_time = data.time[indices]
        local_balance = balance[indices]
        elapsed = local_time[lag:] - local_time[:-lag]
        delta = local_balance[:-lag] - 0.5
        drift = (local_balance[lag:] - local_balance[:-lag]) / elapsed
        groups.append((delta, drift, elapsed))
    return groups


def linear_fit(delta: Vector, drift: Vector) -> tuple[float, float, float]:
    if len(delta) < 4 or float(np.std(delta)) < 1e-12:
        raise ValueError("not enough balance variation for a drift fit")
    design = np.column_stack((np.ones(len(delta)), delta))
    coefficients, _residuals, _rank, _singular = np.linalg.lstsq(
        design, drift, rcond=None
    )
    intercept, slope = (float(value) for value in coefficients)
    fitted = design @ coefficients
    residual_sum = float(np.sum((drift - fitted) ** 2))
    total_sum = float(np.sum((drift - np.mean(drift)) ** 2))
    r_squared = 1.0 - residual_sum / total_sum if total_sum > 0 else 1.0
    return intercept, slope, r_squared


def bootstrap_drift_fit(
    groups: list[tuple[Vector, Vector, Vector]],
    samples: int,
    seed: int,
    lag: int,
) -> tuple[Vector, Vector, Vector]:
    rng = np.random.default_rng(seed + 7919 * lag)
    lengths = [len(group[0]) for group in groups]
    total = sum(lengths)
    if total < 8:
        raise ValueError("at least 8 transitions are needed for bootstrap intervals")
    block_length = max(lag + 1, int(round(total ** (1 / 3))))

    blocks: list[tuple[Vector, Vector]] = []
    for delta, drift, _elapsed in groups:
        local_block = min(block_length, len(delta))
        for start in range(len(delta) - local_block + 1):
            blocks.append(
                (
                    delta[start : start + local_block],
                    drift[start : start + local_block],
                )
            )
    if not blocks:
        raise ValueError("trials are too short for block bootstrap intervals")

    intercepts: list[float] = []
    slopes: list[float] = []
    equilibria: list[float] = []
    attempts = 0
    max_attempts = max(samples * 5, 100)
    while len(slopes) < samples and attempts < max_attempts:
        attempts += 1
        chosen_delta: list[float] = []
        chosen_drift: list[float] = []
        while len(chosen_delta) < total:
            block_delta, block_drift = blocks[int(rng.integers(len(blocks)))]
            chosen_delta.extend(block_delta.tolist())
            chosen_drift.extend(block_drift.tolist())
        delta_sample = np.array(chosen_delta[:total])
        drift_sample = np.array(chosen_drift[:total])
        try:
            intercept, slope, _r_squared = linear_fit(delta_sample, drift_sample)
        except ValueError:
            continue
        intercepts.append(intercept)
        slopes.append(slope)
        if abs(slope) > 1e-12:
            equilibria.append(0.5 - intercept / slope)

    if len(slopes) < max(50, samples // 2):
        raise ValueError("bootstrap could not produce enough nondegenerate fits")
    return (
        np.array(intercepts),
        np.array(slopes),
        np.array(equilibria),
    )


def percentile_interval(values: Vector) -> tuple[float, float]:
    low, high = np.percentile(values, [2.5, 97.5])
    return float(low), float(high)


def fit_conditional_drift(
    data: Observations,
    lag: int,
    bootstrap_samples: int,
    seed: int,
) -> LinearDriftFit:
    total_in = data.total_convergence
    total_out = data.total_emergence
    balance = total_in / (total_in + total_out)
    groups = transition_groups(data, balance, lag)
    if not groups:
        raise ValueError(f"lag {lag} leaves no within-trial transitions")

    delta = np.concatenate([group[0] for group in groups])
    drift = np.concatenate([group[1] for group in groups])
    elapsed = np.concatenate([group[2] for group in groups])
    intercept, slope, r_squared = linear_fit(delta, drift)
    bootstrap_intercepts, bootstrap_slopes, bootstrap_equilibria = (
        bootstrap_drift_fit(groups, bootstrap_samples, seed, lag)
    )

    active = np.abs(delta) > max(1e-12, 0.01 * float(np.std(delta)))
    restoring_fraction = float(np.mean(delta[active] * drift[active] < 0))
    mean_lyapunov_drift = float(np.mean(2 * delta * drift))
    equilibrium = 0.5 - intercept / slope if abs(slope) > 1e-12 else None
    equilibrium_ci = (
        percentile_interval(bootstrap_equilibria)
        if len(bootstrap_equilibria) >= 50
        else None
    )

    delta_energy = float(np.dot(delta, delta))
    half_fixed_slope = (
        float(np.dot(delta, drift) / delta_energy)
        if delta_energy > 1e-24
        else 0.0
    )
    half_residual = drift - half_fixed_slope * delta
    free_residual = drift - (intercept + slope * delta)
    half_sse = float(np.dot(half_residual, half_residual))
    free_sse = float(np.dot(free_residual, free_residual))
    scale = max(float(np.dot(drift, drift)), 1.0)
    floor = np.finfo(float).eps**2 * scale
    count = len(delta)
    bic_half = count * math.log(max(half_sse, floor) / count) + math.log(count)
    bic_free = count * math.log(max(free_sse, floor) / count) + 2 * math.log(
        count
    )

    return LinearDriftFit(
        lag_samples=lag,
        transition_count=len(delta),
        lag_time_median=float(np.median(elapsed)),
        intercept_at_half=intercept,
        intercept_ci95=percentile_interval(bootstrap_intercepts),
        slope=slope,
        slope_ci95=percentile_interval(bootstrap_slopes),
        restoring_rate=-slope,
        equilibrium_balance=equilibrium,
        equilibrium_ci95=equilibrium_ci,
        r_squared=r_squared,
        half_fixed_slope=half_fixed_slope,
        bic_half_fixed=bic_half,
        bic_free_equilibrium=bic_free,
        bic_difference_half_minus_free=bic_half - bic_free,
        restoring_fraction=restoring_fraction,
        mean_lyapunov_drift=mean_lyapunov_drift,
    )


def binned_conditional_drift(
    data: Observations, lag: int, requested_bins: int = 8
) -> list[dict[str, Any]]:
    total_in = data.total_convergence
    total_out = data.total_emergence
    balance = total_in / (total_in + total_out)
    groups = transition_groups(data, balance, lag)
    if not groups:
        return []
    delta = np.concatenate([group[0] for group in groups])
    drift = np.concatenate([group[1] for group in groups])
    bin_count = min(requested_bins, max(2, len(delta) // 20))
    edges = np.unique(np.quantile(delta, np.linspace(0.0, 1.0, bin_count + 1)))
    if len(edges) < 3:
        return []

    rows: list[dict[str, Any]] = []
    for index, (left, right) in enumerate(zip(edges[:-1], edges[1:])):
        if index == len(edges) - 2:
            selected = (delta >= left) & (delta <= right)
        else:
            selected = (delta >= left) & (delta < right)
        count = int(np.sum(selected))
        if count < 2:
            continue
        local_delta = delta[selected]
        local_drift = drift[selected]
        mean_delta = float(np.mean(local_delta))
        mean_drift = float(np.mean(local_drift))
        standard_error = float(np.std(local_drift, ddof=1) / math.sqrt(count))
        product = mean_delta * mean_drift
        if abs(mean_delta) < 1e-12 or abs(mean_drift) < 1e-12:
            direction = "neutral_or_at_balance"
        elif product < 0:
            direction = "toward_half"
        else:
            direction = "away_from_half"
        rows.append(
            {
                "count": count,
                "mean_balance": mean_delta + 0.5,
                "mean_drift": mean_drift,
                "drift_standard_error": standard_error,
                "direction": direction,
            }
        )
    return rows


def trial_contraction(data: Observations) -> dict[str, Any]:
    total_in = data.total_convergence
    total_out = data.total_emergence
    balance = total_in / (total_in + total_out)
    ratios: list[float] = []
    trials: list[dict[str, Any]] = []
    for label, indices in trial_groups(data):
        start = float(balance[indices[0]] - 0.5)
        end = float(balance[indices[-1]] - 0.5)
        ratio = abs(end) / abs(start) if abs(start) > 1e-12 else None
        if ratio is not None:
            ratios.append(ratio)
        trials.append(
            {
                "trial": label,
                "start_balance": start + 0.5,
                "end_balance": end + 0.5,
                "absolute_imbalance_ratio": ratio,
            }
        )
    return {
        "explicit_trial_labels": data.explicit_trials,
        "trial_count": len(trials),
        "median_absolute_imbalance_ratio": (
            float(np.median(ratios)) if ratios else None
        ),
        "contracting_trial_fraction": (
            float(np.mean(np.array(ratios) < 1.0)) if ratios else None
        ),
        "trials": trials,
    }


def lag_pattern(fits: list[LinearDriftFit]) -> dict[str, Any]:
    ordered = sorted(fits, key=lambda fit: fit.lag_time_median)
    if any(fit.slope < 0 for fit in ordered) and any(
        fit.slope >= 0 for fit in ordered
    ):
        return {
            "pattern": "changes_sign_with_lag",
            "magnitude_ratio_last_to_first": None,
            "note": (
                "Warning: drift direction changes across sampling lags. The "
                "one-state local model is not resolved; test hidden states, "
                "delays, cycles, and finer sampling."
            ),
        }
    negative = [fit for fit in ordered if fit.slope < 0]
    if len(negative) < 2:
        return {
            "pattern": "unresolved",
            "magnitude_ratio_last_to_first": None,
            "note": "At least two negative-slope lag fits are required.",
        }
    first = abs(negative[0].slope)
    last = abs(negative[-1].slope)
    ratio = last / first if first > 1e-15 else math.inf
    if ratio >= 1.5:
        pattern = "strengthens_with_lag"
        note = (
            "Warning: finite-lag restoration strengthens as the lag grows. A "
            "hidden neutral oscillator can produce this pattern without an "
            "attractor. Use smaller sampling intervals and perturbation trials."
        )
    elif ratio <= 0.8:
        pattern = "weakens_with_lag"
        note = (
            "Consistent with dissipative relaxation, whose finite-lag slope "
            "usually weakens in magnitude as lag grows. This is not causal proof."
        )
    else:
        pattern = "approximately_flat"
        note = (
            "The restoring estimate is fairly stable across the tested lags. "
            "This is compatible with local relaxation but is not causal proof."
        )
    return {
        "pattern": pattern,
        "magnitude_ratio_last_to_first": ratio,
        "note": note,
    }


def cycle_audit(
    data: Observations, balance_tolerance: float
) -> dict[str, Any]:
    if data.cycle is None:
        return {
            "cycle_count": 0,
            "cycle_balance_verdict": "not_tested",
            "note": "No cycle column was supplied.",
            "cycles": [],
        }

    total_in = data.total_convergence
    total_out = data.total_emergence
    accumulated: dict[tuple[str, str], dict[str, float]] = {}
    for trial_label, trial_indices in trial_groups(data):
        for local_index in range(len(trial_indices) - 1):
            left = trial_indices[local_index]
            right = trial_indices[local_index + 1]
            elapsed = float(data.time[right] - data.time[left])
            cycle_label = str(data.cycle[left])
            key = (trial_label, cycle_label)
            bucket = accumulated.setdefault(
                key, {"convergence": 0.0, "emergence": 0.0, "duration": 0.0}
            )
            bucket["convergence"] += (
                0.5 * float(total_in[left] + total_in[right]) * elapsed
            )
            bucket["emergence"] += (
                0.5 * float(total_out[left] + total_out[right]) * elapsed
            )
            bucket["duration"] += elapsed

    if not accumulated:
        return {
            "cycle_count": 0,
            "cycle_balance_verdict": "not_tested",
            "note": "Cycle labels did not contain any complete sample interval.",
            "cycles": [],
        }

    rows: list[dict[str, Any]] = []
    for (trial_label, cycle_label), bucket in accumulated.items():
        incoming = bucket["convergence"]
        outgoing = bucket["emergence"]
        throughput = incoming + outgoing
        mismatch = (incoming - outgoing) / throughput
        rows.append(
            {
                "trial": trial_label,
                "cycle": cycle_label,
                "duration": bucket["duration"],
                "integrated_convergence": incoming,
                "integrated_emergence": outgoing,
                "normalized_mismatch": mismatch,
                "throughput_weighted_balance": incoming / throughput,
                "balance_verdict": (
                    "within_tolerance"
                    if abs(mismatch) <= balance_tolerance
                    else "outside_tolerance"
                ),
            }
        )
    within = [row["balance_verdict"] == "within_tolerance" for row in rows]
    return {
        "cycle_count": len(rows),
        "balance_tolerance": balance_tolerance,
        "balanced_cycle_fraction": float(np.mean(within)),
        "cycle_balance_verdict": (
            "all_within_tolerance" if all(within) else "some_outside_tolerance"
        ),
        "median_absolute_cycle_mismatch": float(
            np.median([abs(row["normalized_mismatch"]) for row in rows])
        ),
        "cycles": rows,
    }


def attractor_assessment(
    fits: list[LinearDriftFit],
    pattern: dict[str, Any],
    contraction: dict[str, Any],
) -> dict[str, str]:
    if not fits:
        return {
            "drift_direction": "not_tested",
            "half_centering": "not_tested",
            "overall": "not_tested",
        }
    shortest = min(fits, key=lambda fit: fit.lag_time_median)
    slope_low, slope_high = shortest.slope_ci95
    if slope_high < 0:
        direction = "restoring"
    elif slope_low > 0:
        direction = "repelling"
    else:
        direction = "inconclusive"

    equilibrium_ci = shortest.equilibrium_ci95
    if direction != "restoring" or equilibrium_ci is None:
        centering = "unresolved"
    elif equilibrium_ci[0] <= 0.5 <= equilibrium_ci[1]:
        centering = "compatible_with_half"
    else:
        centering = "detectably_biased_from_half"

    ratio = contraction["median_absolute_imbalance_ratio"]
    repeated_contraction = (
        contraction["explicit_trial_labels"]
        and contraction["trial_count"] >= 3
        and ratio is not None
        and ratio < 0.8
    )

    if direction == "repelling":
        overall = "evidence_against_a_half_attractor"
    elif pattern["pattern"] in {
        "strengthens_with_lag",
        "changes_sign_with_lag",
    } and any(fit.slope < 0 for fit in fits):
        overall = "possible_hidden_state_or_oscillator"
    elif direction != "restoring":
        overall = "inconclusive"
    elif centering == "detectably_biased_from_half":
        overall = "restoring_but_not_to_half"
    elif repeated_contraction and centering == "compatible_with_half":
        overall = "half_attractor_candidate_under_repeated_trials"
    else:
        overall = "observationally_restoring; perturbation_test_needed"

    return {
        "drift_direction": direction,
        "half_centering": centering,
        "overall": overall,
        "epistemic_limit": (
            "A finite observational record can support or reject signatures of "
            "restoration. Causal attraction requires controlled perturbations, "
            "independent trials, adequate time resolution, and a complete state."
        ),
    }


def analyze(
    data: Observations,
    lags: list[int],
    bootstrap_samples: int,
    seed: int,
    balance_tolerance: float,
    accounting_tolerance: float,
) -> dict[str, Any]:
    finite = finite_window_audit(data, balance_tolerance, accounting_tolerance)
    fits: list[LinearDriftFit] = []
    skipped: dict[str, str] = {}
    for lag in sorted(set(lags)):
        if lag < 1:
            raise ValueError("lags must be positive integers")
        try:
            fits.append(
                fit_conditional_drift(data, lag, bootstrap_samples, seed)
            )
        except ValueError as error:
            skipped[str(lag)] = str(error)
    pattern = lag_pattern(fits)
    contraction = trial_contraction(data)
    cycles = cycle_audit(data, balance_tolerance)
    assessment = attractor_assessment(fits, pattern, contraction)
    return {
        "schema_version": "balance-empirical-v1.0",
        "finite_window": finite,
        "conditional_drift": {
            "model": "db/dt = intercept_at_half + slope * (b - 1/2)",
            "fits": [asdict(fit) for fit in fits],
            "binned_drift_by_lag": {
                str(fit.lag_samples): binned_conditional_drift(
                    data, fit.lag_samples
                )
                for fit in fits
            },
            "skipped_lags": skipped,
            "lag_pattern": pattern,
        },
        "trial_contraction": contraction,
        "cycle_audit": cycles,
        "attractor_assessment": assessment,
    }


def make_relaxation_data(
    target: float,
    rate: float,
    starts: tuple[float, ...],
    duration: float = 8.0,
    samples: int = 401,
) -> Observations:
    times: list[Vector] = []
    convergence: list[Vector] = []
    emergence: list[Vector] = []
    stocks: list[Vector] = []
    trials: list[np.ndarray] = []
    for index, start in enumerate(starts):
        time = np.linspace(0.0, duration, samples)
        balance = target + (start - target) * np.exp(-rate * time)
        throughput = np.full(samples, 4.0)
        incoming = throughput * balance
        outgoing = throughput * (1 - balance)
        stock = 10.0 + cumulative_trapezoid(incoming - outgoing, time)
        times.append(time)
        convergence.append(incoming)
        emergence.append(outgoing)
        stocks.append(stock)
        trials.append(np.full(samples, f"trial-{index + 1}", dtype=object))
    data = Observations(
        time=np.concatenate(times),
        convergence=np.concatenate(convergence),
        emergence=np.concatenate(emergence),
        external_convergence=np.zeros(samples * len(starts)),
        external_emergence=np.zeros(samples * len(starts)),
        stock=np.concatenate(stocks),
        trial=np.concatenate(trials),
        cycle=None,
        explicit_trials=True,
    )
    validate_observations(data)
    return data


def make_repeller_data() -> Observations:
    starts = (0.47, 0.48, 0.52, 0.53)
    rate = 0.7
    duration = 3.0
    samples = 301
    times: list[Vector] = []
    convergence: list[Vector] = []
    emergence: list[Vector] = []
    trials: list[np.ndarray] = []
    for index, start in enumerate(starts):
        time = np.linspace(0.0, duration, samples)
        balance = 0.5 + (start - 0.5) * np.exp(rate * time)
        assert np.min(balance) > 0 and np.max(balance) < 1
        times.append(time)
        convergence.append(4 * balance)
        emergence.append(4 * (1 - balance))
        trials.append(np.full(samples, f"trial-{index + 1}", dtype=object))
    data = Observations(
        time=np.concatenate(times),
        convergence=np.concatenate(convergence),
        emergence=np.concatenate(emergence),
        external_convergence=np.zeros(samples * len(starts)),
        external_emergence=np.zeros(samples * len(starts)),
        stock=None,
        trial=np.concatenate(trials),
        cycle=None,
        explicit_trials=True,
    )
    validate_observations(data)
    return data


def make_neutral_oscillator_data() -> Observations:
    samples = 1601
    cycles = 8
    duration = cycles * 2 * math.pi
    time = np.linspace(0.0, duration, samples)
    balance = 0.5 + 0.2 * np.cos(time)
    throughput = np.full(samples, 4.0)
    stock = 10.0 + cumulative_trapezoid(
        throughput * (2 * balance - 1), time
    )
    cycle_labels = np.minimum(
        (time / (2 * math.pi)).astype(int), cycles - 1
    ).astype(str)
    data = Observations(
        time=time,
        convergence=throughput * balance,
        emergence=throughput * (1 - balance),
        external_convergence=np.zeros(samples),
        external_emergence=np.zeros(samples),
        stock=stock,
        trial=np.full(samples, "record", dtype=object),
        cycle=cycle_labels.astype(object),
        explicit_trials=False,
    )
    validate_observations(data)
    return data


def run_self_test() -> None:
    common = {
        "lags": [1, 2, 4, 8],
        "bootstrap_samples": 300,
        "seed": 20260820,
        "balance_tolerance": 0.01,
        "accounting_tolerance": 1e-8,
    }

    stable = analyze(
        make_relaxation_data(0.5, 0.8, (0.2, 0.3, 0.7, 0.8)), **common
    )
    assert stable["finite_window"]["stock_accounting_verdict"] == (
        "within_tolerance"
    )
    assert stable["attractor_assessment"]["overall"] == (
        "half_attractor_candidate_under_repeated_trials"
    )

    biased = analyze(
        make_relaxation_data(0.62, 0.8, (0.25, 0.4, 0.8, 0.95)), **common
    )
    assert biased["attractor_assessment"]["overall"] == (
        "restoring_but_not_to_half"
    )

    repeller = analyze(make_repeller_data(), **common)
    assert repeller["attractor_assessment"]["overall"] == (
        "evidence_against_a_half_attractor"
    )

    oscillator = analyze(make_neutral_oscillator_data(), **common)
    assert oscillator["finite_window"]["finite_window_balance_verdict"] == (
        "within_tolerance"
    )
    assert oscillator["conditional_drift"]["lag_pattern"]["pattern"] == (
        "strengthens_with_lag"
    )
    assert oscillator["attractor_assessment"]["overall"] == (
        "possible_hidden_state_or_oscillator"
    )

    identity_error = max(
        abs(result["finite_window"]["balance_identity_error"])
        for result in (stable, biased, repeller, oscillator)
    )
    assert identity_error < 5e-15

    print("Balance empirical analyzer self-test")
    print(
        "stable centered control:    ",
        stable["attractor_assessment"]["overall"],
    )
    print(
        "stable biased control:      ",
        biased["attractor_assessment"]["overall"],
    )
    print(
        "repelling control:          ",
        repeller["attractor_assessment"]["overall"],
    )
    print(
        "neutral oscillator control: ",
        oscillator["attractor_assessment"]["overall"],
    )
    print(f"maximum balance identity error: {identity_error:.3e}")


def parse_lags(raw: str) -> list[int]:
    try:
        values = [int(part.strip()) for part in raw.split(",") if part.strip()]
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "lags must be comma-separated integers"
        ) from error
    if not values or any(value < 1 for value in values):
        raise argparse.ArgumentTypeError("lags must contain positive integers")
    return values


def print_summary(report: dict[str, Any]) -> None:
    finite = report["finite_window"]
    assessment = report["attractor_assessment"]
    print("Balance empirical test")
    print(
        "finite-window normalized mismatch: "
        f"{finite['normalized_mismatch']:+.6g} "
        f"({finite['finite_window_balance_verdict']})"
    )
    print(
        "throughput-weighted balance: "
        f"{finite['throughput_weighted_balance']:.9f}"
    )
    print(f"stock accounting: {finite['stock_accounting_verdict']}")
    fits = report["conditional_drift"]["fits"]
    if fits:
        shortest = min(fits, key=lambda fit: fit["lag_time_median"])
        low, high = shortest["slope_ci95"]
        print(
            "shortest-lag drift slope: "
            f"{shortest['slope']:+.6g} (95% block interval {low:+.6g}, "
            f"{high:+.6g})"
        )
        print(
            "estimated restoring equilibrium: "
            f"{shortest['equilibrium_balance']}"
        )
    print(
        "lag diagnostic: "
        f"{report['conditional_drift']['lag_pattern']['pattern']}"
    )
    print(f"attractor assessment: {assessment['overall']}")
    print("Interpret the JSON report with the protocol's epistemic limits.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Audit convergence/emergence balance and test restoring drift toward "
            "one half."
        )
    )
    parser.add_argument("csv", nargs="?", type=Path, help="observation CSV")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run stable, biased, repelling, and oscillator controls",
    )
    parser.add_argument(
        "--lags",
        type=parse_lags,
        default=[1, 2, 4, 8],
        help="comma-separated forward lags in samples (default: 1,2,4,8)",
    )
    parser.add_argument(
        "--bootstrap-samples",
        type=int,
        default=1000,
        help="moving-block bootstrap replicates (default: 1000)",
    )
    parser.add_argument("--seed", type=int, default=20260820)
    parser.add_argument(
        "--balance-tolerance",
        type=float,
        default=0.01,
        help="allowed absolute integrated mismatch / throughput (default: 0.01)",
    )
    parser.add_argument(
        "--accounting-tolerance",
        type=float,
        default=0.01,
        help="allowed absolute stock closure error / throughput (default: 0.01)",
    )
    parser.add_argument(
        "--json",
        type=Path,
        help="optional path for the complete machine-readable report",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return
    if args.csv is None:
        parser.error("provide a CSV path or use --self-test")
    if args.bootstrap_samples < 100:
        parser.error("--bootstrap-samples must be at least 100")
    if args.balance_tolerance < 0 or args.accounting_tolerance < 0:
        parser.error("tolerances must be nonnegative")

    observations = load_csv(args.csv)
    report = analyze(
        observations,
        lags=args.lags,
        bootstrap_samples=args.bootstrap_samples,
        seed=args.seed,
        balance_tolerance=args.balance_tolerance,
        accounting_tolerance=args.accounting_tolerance,
    )
    print_summary(report)
    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        with args.json.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write("\n")
        print(f"complete report: {args.json}")


if __name__ == "__main__":
    main()
