#!/usr/bin/env python3
"""Generate the Run 1 observation ledger from the Xorzo2 spine's physics.

Created: 2026-08-21
Last updated: 2026-08-21
Version: 1.0

Revision history:
- 2026-08-21 v1.0: implements the frozen Stage A declaration of
  plans/balance_xorzo2_run_2026_08_21.md Part I exactly: the engine's
  per-byte cycle (psi + inj, M^8, scale-only normalization) in float64,
  the given bit-station keyboard, the framework corpus, the exact
  sign-split flow decomposition, nine 400-byte trials (three shams as
  one continuous segmented run; three random-direction and three
  top-singular-direction perturbations on the shared segment), seed
  20260821. Prints the exact discrete closure receipt per trial.

The learned Voice plays no role in the state update, so this reproduces
the living state dynamics, not a model of them. No torch, no training,
no worldline touched.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "Xorzo2"))

from spine import Seed, make_bit_chords, INJ_NODES  # noqa: E402

SEED = 20260821
WARMUP_BYTES = 2000
TRIAL_BYTES = 400
SHARED_SEGMENT = (2000, 2400)
SHAM_SEGMENTS = [(2000, 2400), (2400, 2800), (2800, 3200)]
BLEND_WEIGHTS = (0.25, 0.5, 1.0)
CORPUS_PATH = _ROOT / "circumpunct_framework.md"
OUT_CSV = _ROOT / "experiments" / "balance_xorzo2_observations_v1.csv"


def realify_chord(chord: np.ndarray, n_nodes: int) -> np.ndarray:
    v = np.zeros(2 * n_nodes, dtype=np.float64)
    v[: len(INJ_NODES)] = np.real(chord)
    v[n_nodes : n_nodes + len(INJ_NODES)] = np.imag(chord)
    return v


def unit(v: np.ndarray) -> np.ndarray:
    return v / np.linalg.norm(v)


def run_trial(
    label: str,
    psi0: np.ndarray,
    corpus: bytes,
    segment: tuple[int, int],
    m8: np.ndarray,
    chords44: np.ndarray,
    rows: list[dict],
) -> tuple[np.ndarray, float]:
    """Run one trial; append per-byte ledger rows; return (final psi,
    exact discrete closure |sum(C-E) - (X_end - X_start)|)."""
    psi = unit(psi0.copy())
    x_start = float(psi @ psi)
    net = 0.0
    for t, pos in enumerate(range(*segment)):
        byte = corpus[pos]
        inj = chords44[byte]
        s_prime = psi + inj
        s = m8 @ s_prime
        n_psi = float(psi @ psi)
        n_prime = float(s_prime @ s_prime)
        n_s = float(s @ s)
        dx_inj = n_prime - n_psi
        dx_op = n_s - n_prime
        dx_norm = 1.0 - n_s
        psi = s / np.sqrt(n_s)

        convergence = max(dx_inj, 0.0)
        external_convergence = max(dx_op, 0.0) + max(dx_norm, 0.0)
        emergence = max(-dx_norm, 0.0)
        external_emergence = max(-dx_op, 0.0) + max(-dx_inj, 0.0)
        net += (convergence + external_convergence) - (
            emergence + external_emergence
        )
        rows.append(
            {
                "time": float(t),
                "convergence": convergence,
                "emergence": emergence,
                "external_convergence": external_convergence,
                "external_emergence": external_emergence,
                "stock": n_psi,
                "trial": label,
            }
        )
    x_end = float(psi @ psi)
    return psi, abs(net - (x_end - x_start))


def main() -> None:
    seed_obj = Seed()
    n = seed_obj.op.N
    m_real = seed_obj.M_real
    m8 = np.linalg.matrix_power(m_real, 8)
    chords = make_bit_chords(seed_obj.alpha)
    chords44 = np.array([realify_chord(chords[b], n) for b in range(256)])

    corpus = CORPUS_PATH.read_bytes()
    assert len(corpus) >= SHAM_SEGMENTS[-1][1], "corpus too short"

    # Warmup from the realified attractor
    psi = np.concatenate(
        [np.real(seed_obj.attractor), np.imag(seed_obj.attractor)]
    )
    psi = unit(psi)
    for pos in range(WARMUP_BYTES):
        s = m8 @ (psi + chords44[corpus[pos]])
        psi = s / np.linalg.norm(s)
    psi_warm = psi.copy()

    # Perturbation directions (frozen): seeded random; top right-singular
    rng = np.random.default_rng(SEED)
    d_random = unit(rng.standard_normal(2 * n))
    _u, _sv, vt = np.linalg.svd(m8)
    d_singular = vt[0]

    rows: list[dict] = []
    closures: list[tuple[str, float]] = []

    # Shams: one continuous run segmented into three trials
    state = psi_warm.copy()
    for k, segment in enumerate(SHAM_SEGMENTS):
        label = f"sham-{'ABC'[k]}"
        state, closure = run_trial(
            label, state, corpus, segment, m8, chords44, rows
        )
        closures.append((label, closure))

    # Perturbed trials, all on the shared segment against sham-A
    for name, direction in (("rand", d_random), ("sing", d_singular)):
        for w in BLEND_WEIGHTS:
            label = f"pert-{name}-{w:g}"
            psi0 = unit((1.0 - w) * psi_warm + w * direction)
            _final, closure = run_trial(
                label, psi0, corpus, SHARED_SEGMENT, m8, chords44, rows
            )
            closures.append((label, closure))

    OUT_CSV.parent.mkdir(exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print("Xorzo2 balance observations (Run 1)")
    print(seed_obj.describe())
    print(f"corpus: {CORPUS_PATH.name} ({len(corpus)} bytes)")
    print(f"rows written: {len(rows)} -> {OUT_CSV.name}")
    print("exact discrete closure |sum(C-E) - dX| per trial:")
    for label, closure in closures:
        print(f"  {label:16s} {closure:.3e}")
    by_trial: dict[str, list[float]] = {}
    for row in rows:
        c = row["convergence"] + row["external_convergence"]
        e = row["emergence"] + row["external_emergence"]
        by_trial.setdefault(row["trial"], []).append(c / (c + e))
    print("per-trial balance b (first, mean, last):")
    for label, bs in by_trial.items():
        print(
            f"  {label:16s} {bs[0]:.4f}  {float(np.mean(bs)):.4f}  "
            f"{bs[-1]:.4f}"
        )


if __name__ == "__main__":
    main()
