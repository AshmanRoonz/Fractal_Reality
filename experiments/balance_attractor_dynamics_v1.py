#!/usr/bin/env python3
"""Verify candidate dynamics that make balance a stable attractor.

Created: 2026-08-20
Last updated: 2026-08-20
Version: 1.0

Revision history:
- 2026-08-20 v1.0: conservative input-output exchange, boundary-preserving
  homeostasis, gap-defect gradient flow, continuous and discrete seam
  correction, and bounded-storage averaging checks.

Companion proof note:
plans/balance_attractor_dynamics_2026_08_20.md
"""

from __future__ import annotations

import math
from collections.abc import Callable

import numpy as np


Vector = np.ndarray


def rk4(
    rhs: Callable[[float, Vector], Vector],
    initial: Vector,
    t_final: float,
    step: float,
) -> tuple[np.ndarray, np.ndarray]:
    count = int(round(t_final / step))
    times = np.linspace(0.0, t_final, count + 1)
    states = np.empty((count + 1, len(initial)), dtype=float)
    states[0] = initial
    for index, time in enumerate(times[:-1]):
        value = states[index]
        k1 = rhs(time, value)
        k2 = rhs(time + step / 2, value + step * k1 / 2)
        k3 = rhs(time + step / 2, value + step * k2 / 2)
        k4 = rhs(time + step, value + step * k3)
        states[index + 1] = value + step * (k1 + 2 * k2 + 2 * k3 + k4) / 6
    return times, states


def exchange_exact(b0: float, kappa: float, time: np.ndarray) -> np.ndarray:
    return 0.5 + (b0 - 0.5) * np.exp(-2 * kappa * time)


def replicator_exact(b0: float, gamma: float, time: np.ndarray) -> np.ndarray:
    delta0 = b0 - 0.5
    if delta0 == 0:
        return np.full_like(time, 0.5)
    y0 = delta0 * delta0
    y = y0 * np.exp(-gamma * time) / (
        1 - 4 * y0 + 4 * y0 * np.exp(-gamma * time)
    )
    return 0.5 + math.copysign(1.0, delta0) * np.sqrt(y)


def check_conservative_exchange() -> tuple[float, float]:
    kappa = 0.3
    initial = np.array([8.0, 2.0])

    def rhs(_time: float, state: Vector) -> Vector:
        input_flow, output_flow = state
        mismatch = input_flow - output_flow
        return np.array([-kappa * mismatch, kappa * mismatch])

    times, states = rk4(rhs, initial, t_final=10.0, step=0.002)
    totals = states.sum(axis=1)
    balances = states[:, 0] / totals
    expected = exchange_exact(initial[0] / initial.sum(), kappa, times)

    assert np.max(np.abs(totals - initial.sum())) < 2e-12
    assert np.min(states) > 0
    assert np.max(np.abs(balances - expected)) < 2e-12
    assert np.all(np.diff(np.abs(balances - 0.5)) <= 2e-14)
    return float(balances[0]), float(balances[-1])


def check_boundary_preserving_homeostasis() -> list[tuple[float, float]]:
    gamma = 1.0
    results: list[tuple[float, float]] = []

    def rhs(_time: float, state: Vector) -> Vector:
        balance = state[0]
        return np.array([gamma * balance * (1 - balance) * (1 - 2 * balance)])

    for b0 in (0.01, 0.1, 0.25, 0.75, 0.9, 0.99):
        times, states = rk4(rhs, np.array([b0]), t_final=30.0, step=0.002)
        expected = replicator_exact(b0, gamma, times)
        balance = states[:, 0]
        assert np.max(np.abs(balance - expected)) < 2e-12
        assert np.min(balance) > 0
        assert np.max(balance) < 1
        assert np.all(np.diff(np.abs(balance - 0.5)) <= 2e-14)
        results.append((b0, float(balance[-1])))

    return results


def check_gap_gradient_flow() -> tuple[float, float]:
    m = 3
    count = 2 * m + 1
    coefficient = m * (m + 1) / count**2
    mobility = 0.7

    def variance(balance: np.ndarray) -> np.ndarray:
        return coefficient * (2 * balance - 1) ** 2

    def rhs(_time: float, state: Vector) -> Vector:
        balance = state[0]
        derivative = 4 * coefficient * (2 * balance - 1)
        return np.array([-mobility * derivative])

    _times, states = rk4(rhs, np.array([0.9]), t_final=10.0, step=0.002)
    energies = variance(states[:, 0])
    assert np.all(np.diff(energies) <= 2e-14)
    assert abs(states[-1, 0] - 0.5) < 2e-6
    return float(energies[0]), float(energies[-1])


def check_local_balance_leaves_seam_residual() -> tuple[float, float]:
    rho = 0.6
    delta0 = 0.2
    seam0 = -0.1
    steps = 200
    deltas = delta0 * rho ** np.arange(steps)
    seam = seam0 + np.sum(deltas)
    expected = seam0 + delta0 / (1 - rho)
    assert abs(seam - expected) < 1e-14
    assert abs(deltas[-1]) < 1e-40
    assert abs(seam) > 0.1
    return float(deltas[-1]), float(seam)


def check_continuous_seam_controller() -> tuple[float, float, float]:
    k_p = 1.2
    k_i = 0.5
    initial = np.array([0.25, 0.8])  # delta, accumulated seam

    def rhs(_time: float, state: Vector) -> Vector:
        delta, seam = state
        return np.array([-k_p * delta - k_i * seam, delta])

    _times, states = rk4(rhs, initial, t_final=35.0, step=0.002)
    energies = 0.5 * states[:, 0] ** 2 + 0.5 * k_i * states[:, 1] ** 2
    assert np.all(np.diff(energies) <= 2e-12)
    assert np.linalg.norm(states[-1]) < 2e-8
    return float(energies[0]), float(energies[-1]), float(np.linalg.norm(states[-1]))


def discrete_pi_is_stable(k_p: float, k_i: float) -> bool:
    return k_i > 0 and k_p > k_i and 2 * k_p - k_i < 4


def check_discrete_seam_controller() -> tuple[int, int]:
    checked = 0
    stable = 0
    for k_p in np.linspace(0.025, 2.5, 100):
        for k_i in np.linspace(0.025, 2.0, 80):
            matrix = np.array([[1.0, 1.0], [-k_i, 1.0 - k_p]])
            radius = float(np.max(np.abs(np.linalg.eigvals(matrix))))
            predicted = discrete_pi_is_stable(float(k_p), float(k_i))
            margin = min(
                abs(k_i),
                abs(k_p - k_i),
                abs(4 - 2 * k_p + k_i),
            )
            if margin < 1e-10:
                continue
            assert (radius < 1.0) == predicted
            checked += 1
            stable += int(predicted)
    return checked, stable


def check_bounded_storage_average() -> tuple[float, float]:
    baseline = 2.0
    amplitude = 0.6
    omega = 1.3
    periods = 40
    duration = periods * 2 * math.pi / omega
    time = np.linspace(0.0, duration, 200_001)
    storage_rate = amplitude * omega * np.cos(omega * time)
    input_flow = baseline + storage_rate / 2
    output_flow = baseline - storage_rate / 2
    throughput = input_flow + output_flow
    balance = input_flow / throughput
    weighted_mean = np.trapezoid(throughput * balance, time) / np.trapezoid(
        throughput, time
    )
    storage_change = np.trapezoid(input_flow - output_flow, time)
    assert np.min(input_flow) > 0 and np.min(output_flow) > 0
    assert abs(storage_change) < 2e-13
    assert abs(weighted_mean - 0.5) < 2e-14
    return float(storage_change), float(weighted_mean)


def main() -> None:
    exchange_start, exchange_final = check_conservative_exchange()
    homeostatic_results = check_boundary_preserving_homeostasis()
    energy_start, energy_final = check_gap_gradient_flow()
    local_delta, residual_seam = check_local_balance_leaves_seam_residual()
    pi_energy_start, pi_energy_final, pi_final_norm = (
        check_continuous_seam_controller()
    )
    discrete_checked, discrete_stable = check_discrete_seam_controller()
    storage_change, weighted_mean = check_bounded_storage_average()

    print("Balance-attractor dynamics verification")
    print(
        f"conservative exchange: b {exchange_start:.6f} -> "
        f"{exchange_final:.6f}"
    )
    for start, final in homeostatic_results:
        print(f"boundary-preserving flow: b {start:.2f} -> {final:.9f}")
    print(
        f"gap-defect energy: {energy_start:.9f} -> {energy_final:.3e}"
    )
    print(
        f"local balance only: final delta {local_delta:.3e}, "
        f"residual seam {residual_seam:.6f}"
    )
    print(
        f"continuous seam controller energy: {pi_energy_start:.6f} -> "
        f"{pi_energy_final:.3e}; final state norm {pi_final_norm:.3e}"
    )
    print(
        f"discrete PI Jury test: {discrete_checked} parameter pairs, "
        f"{discrete_stable} stable"
    )
    print(
        f"bounded periodic storage: net change {storage_change:.3e}, "
        f"throughput-weighted b {weighted_mean:.15f}"
    )


if __name__ == "__main__":
    main()
