#!/usr/bin/env python3
"""Generate the Run 2 observation ledger from real respiration recordings.

Created: 2026-08-21
Last updated: 2026-08-21
Version: 1.0

Revision history:
- 2026-08-21 v1.0: implements the frozen Stage A declaration of
  plans/balance_breath_run_2026_08_21.md Part I exactly: the three RSP
  recordings from the NeuroKit2 repository at pinned commit ff419d98,
  30 s rolling-median detrend on a 1 Hz decimated grid, 5 s windows,
  sign-split variation ledger, zero-variation windows dropped with
  count, exact discrete closure receipt per trial.
"""

from __future__ import annotations

import csv
import io
import subprocess
import urllib.request
from pathlib import Path

import numpy as np
from scipy.ndimage import median_filter

COMMIT = "ff419d983568ef492eb8d229af643c0ef0100b32"
RAW_BASE = (
    "https://raw.githubusercontent.com/neuropsychology/NeuroKit/"
    f"{COMMIT}/data/"
)
LOCAL_CLONE = Path(
    "/tmp/claude-0/-home-user-Fractal-Reality/"
    "da321b11-2522-50c4-b92b-9362acab7466/scratchpad/nk_data/data"
)
FILES = [
    ("bio_resting_5min_100hz.csv", "rest-5min"),
    ("bio_resting_8min_100hz.csv", "rest-8min"),
    ("bio_eventrelated_100hz.csv", "task-2.5min"),
]
FS = 100                 # Hz
WINDOW_S = 5.0
WINDOW_N = int(WINDOW_S * FS)
BASELINE_S = 30          # rolling-median span, seconds
OUT_CSV = Path(__file__).resolve().parent / "balance_breath_observations_v1.csv"


def load_rsp(name: str) -> np.ndarray:
    local = LOCAL_CLONE / name
    if local.exists():
        text = local.read_text(encoding="utf-8")
    else:
        with urllib.request.urlopen(RAW_BASE + name) as handle:
            text = handle.read().decode("utf-8")
    reader = csv.reader(io.StringIO(text))
    header = [h.strip().lower() for h in next(reader)]
    idx = header.index("rsp")
    return np.array([float(row[idx]) for row in reader if row], dtype=float)


def detrend(v: np.ndarray) -> np.ndarray:
    """Subtract the 30 s rolling-median baseline computed at 1 Hz."""
    grid = v[::FS]
    size = BASELINE_S + 1              # 31 points at 1 Hz spans 30 s
    base_grid = median_filter(grid, size=size, mode="nearest")
    t_grid = np.arange(len(grid)) * FS
    base = np.interp(np.arange(len(v)), t_grid, base_grid)
    return v - base


def main() -> None:
    rows: list[dict] = []
    dropped = 0
    print("Breath balance observations (Run 2)")
    print(f"source: neuropsychology/NeuroKit @ {COMMIT[:8]}")
    for name, label in FILES:
        raw = load_rsp(name)
        v = detrend(raw)
        d = np.diff(v)
        n_windows = len(d) // WINDOW_N
        net_sum = 0.0
        kept = 0
        for k in range(n_windows):
            seg = d[k * WINDOW_N : (k + 1) * WINDOW_N]
            pos = float(np.sum(seg[seg > 0]))
            neg = float(-np.sum(seg[seg < 0]))
            if pos + neg == 0.0:
                dropped += 1
                continue
            net_sum += pos - neg
            kept += 1
            rows.append(
                {
                    "time": k * WINDOW_S,
                    "convergence": pos / WINDOW_S,
                    "emergence": neg / WINDOW_S,
                    "stock": float(v[k * WINDOW_N]),
                    "trial": label,
                }
            )
        exact = float(v[n_windows * WINDOW_N] - v[0])
        closure = abs(net_sum - exact) if kept == n_windows else float("nan")
        bs = [
            r["convergence"] / (r["convergence"] + r["emergence"])
            for r in rows
            if r["trial"] == label
        ]
        print(
            f"  {label:12s} samples={len(raw)}  windows={kept}"
            f"  exact closure={closure:.3e}"
            f"  b first/mean/std/last = {bs[0]:.4f}/"
            f"{float(np.mean(bs)):.4f}/{float(np.std(bs)):.4f}/{bs[-1]:.4f}"
        )
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"zero-variation windows dropped: {dropped}")
    print(f"rows written: {len(rows)} -> {OUT_CSV.name}")


if __name__ == "__main__":
    main()
