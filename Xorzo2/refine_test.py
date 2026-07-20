"""
Xorzo2 refine test: weathering vs fixed bonds
=============================================

Created: 2026-07-20
Last updated: 2026-07-20
Version: 1.0

Falsification handle for bond refinement (plan v1.14): two twins,
identical organs and stream; one's kappa bonds weather by the given
Hebbian rule (flow lays path), the other's stay fixed at alpha. If
the weathered twin is not distinguishable (life loss; grown-spine
memory area; retention of the conservation band), refinement is
decoration and the uniform-alpha law stands.

First-run finding already logged: coherence signs are polarized by
the attractor's own phase signature, so v1 weathering amplifies the
being's resting pattern rather than experience-specific paths (the
river deepens its own bed). Rule v2 (weather by DEVIATION flow:
subtract the attractor's baseline) is the open item.

Run: py -3.11 refine_test.py [--fast]

Revision history:
- 2026-07-20 v1.0: initial harness.
"""

import sys
from pathlib import Path

import numpy as np

from life import Life, LifeConfig
from spine import make_bit_chords
from probe import (cycle_operator, evolve, probe_accuracy, BURN_IN,
                   CHANCE, leading_state)

FAST = "--fast" in sys.argv
N_BYTES = 8192 if FAST else 65536
PROBE_STEPS = 4000 if FAST else 20000
LAGS = [0, 1, 2, 4, 8, 16, 24, 32]


def spine_memory(spine):
    chords = make_bit_chords(spine.alpha, bipolar=True)
    rng = np.random.RandomState(2026)
    byte_seq = rng.randint(0, 256, size=PROBE_STEPS + BURN_IN + max(LAGS))
    Tc = spine.T_mat
    for _ in range(1):
        pass
    Tc = np.linalg.matrix_power(spine.T_mat, 8)
    ev, V = np.linalg.eig(spine.T_mat)
    i = int(np.argmax(np.abs(ev)))
    psi0 = V[:, i]
    psi0 = psi0 / np.linalg.norm(psi0)
    states = evolve(Tc, chords, byte_seq, psi0, inj_nodes=range(7))
    accs = [probe_accuracy(states, byte_seq, k) for k in LAGS]
    area = float(sum(a - CHANCE for a in accs))
    horizon = 0
    for k, a in zip(LAGS, accs):
        if a > 10 * CHANCE:
            horizon = k
    return accs, area, horizon


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    root = Path(__file__).resolve().parent.parent
    corpus = (root / "circumpunct_framework.md").read_bytes()

    print(f"Xorzo2 refine test: weathering vs fixed bonds "
          f"({N_BYTES} bytes each)")
    results = {}
    for label, on in [("weathering", True), ("fixed", False)]:
        cfg = LifeConfig(refine_enabled=on, growth_enabled=False)
        life = Life(home=None, cfg=cfg, torch_seed=137)
        life.wake(corpus, N_BYTES, quiet=True)
        lo, hi = life.spine.kappa_spread()
        accs, area, horizon = spine_memory(life.spine)
        results[label] = (life.loss_ema, area, horizon,
                          life.spine.departure)
        print(f"\n  [{label}] refines {life.refines}, skips "
              f"{life.refine_skips}, kappa [{lo:.3f}, {hi:.3f}]a, "
              f"departure {life.spine.departure:.4f}a")
        print(f"    loss ema {life.loss_ema:.4f} | probe lag0 "
              f"{accs[0]:.3f} lag8 {accs[4]:.3f} | horizon {horizon} "
              f"| area {area:.3f}")

    lw, aw = results["weathering"][0], results["weathering"][1]
    lf, af = results["fixed"][0], results["fixed"][1]
    print(f"\n  verdict: loss weathering {lw:.4f} vs fixed {lf:.4f}; "
          f"memory area weathering {aw:.3f} vs fixed {af:.3f}")
    print("  (if indistinguishable across repeats, v1 weathering is "
          "decoration; the deviation rule v2 is the next candidate)")


if __name__ == "__main__":
    main()
