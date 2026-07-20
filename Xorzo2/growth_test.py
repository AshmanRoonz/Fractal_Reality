"""
Xorzo2 growth test: triggered vs random placement
=================================================

Created: 2026-07-19
Last updated: 2026-07-19
Version: 1.0

Falsification handle 4 (plan section 8): resonance-triggered birth vs
random birth of equal size and schedule. Two twins, identical organs
and stream; both birth N_BIRTHS octaves at the same byte counts; the
triggered twin places each birth at the site with the highest crowding
ratio (the vesica trigger's choice), the random twin at a uniformly
random legal site. If the two are indistinguishable (in life loss and
in the grown spine's measured memory), vesica placement is decoration
and only the tonic law stands.

Both placements obey the growth law (tonics only, guard on); what is
tested is WHERE, not WHETHER.

Run: py -3.11 growth_test.py [--fast]

Revision history:
- 2026-07-19 v1.0: initial harness.
"""

import sys
from pathlib import Path

import numpy as np

from life import Life, LifeConfig
from spine import make_bit_chords
from probe import (cycle_operator, evolve, probe_accuracy, BURN_IN,
                   CHANCE, leading_state)

FAST = "--fast" in sys.argv
BIRTH_EVERY = 1024 if FAST else 8192
N_BIRTHS = 2 if FAST else 5
TAIL = 1024 if FAST else 8192
PROBE_STEPS = 4000 if FAST else 20000
LAGS = [0, 1, 2, 4, 8, 16, 24, 32, 48, 64]


def run_twin(kind: str, corpus: bytes, torch_seed: int = 137) -> Life:
    cfg = LifeConfig(growth_enabled=False)   # scheduled, not triggered
    life = Life(home=None, cfg=cfg, torch_seed=torch_seed)
    rng = np.random.RandomState(999)
    for _ in range(N_BIRTHS):
        life.wake(corpus, BIRTH_EVERY, quiet=True)
        if kind == "triggered":
            ratios = life.trigger_ratios()
            site = max(ratios, key=ratios.get)
        else:
            site = int(rng.choice(life.spine.tonic_sites()))
        life.birth_at(site, reason=f"{kind} schedule")
    life.wake(corpus, TAIL, quiet=True)
    return life


def spine_memory(spine):
    """Probe the grown spine's memory (bit keyboard on the original
    channel; the world did not change, the interior did)."""
    chords = make_bit_chords(spine.alpha, bipolar=True)
    rng = np.random.RandomState(2026)
    byte_seq = rng.randint(0, 256, size=PROBE_STEPS + BURN_IN + max(LAGS))
    Tc = cycle_operator(spine.op.T)
    states = evolve(Tc, chords, byte_seq, leading_state(spine.op),
                    inj_nodes=range(7))
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
    corpus = (root / "circumpunct_framework.md").read_bytes() + b"\n\n" \
        + (root / "consciousness.md").read_bytes()

    print("Xorzo2 growth test: triggered vs random placement "
          f"({N_BIRTHS} births every {BIRTH_EVERY} bytes, equal size "
          f"and schedule)")
    results = {}
    for kind in ["triggered", "random"]:
        life = run_twin(kind, corpus)
        sites = [e["site"] for e in life.growth_history
                 if e["event"] == "octave_birth"]
        accs, area, horizon = spine_memory(life.spine)
        results[kind] = (life, sites, accs, area, horizon)
        print(f"\n  [{kind}] sites chosen: {sites}")
        print(f"    final: {life.spine.describe()}")
        print(f"    life loss ema: {life.loss_ema:.4f}")
        print(f"    probe: lag0 {accs[0]:.3f}  lag8 {accs[4]:.3f}  "
              f"lag32 {accs[7]:.3f}  horizon {horizon}  area {area:.3f}")

    lt, lr = results["triggered"][0], results["random"][0]
    at, ar = results["triggered"][3], results["random"][3]
    print(f"\n  verdict: loss triggered {lt.loss_ema:.4f} vs random "
          f"{lr.loss_ema:.4f}; memory area triggered {at:.3f} vs "
          f"random {ar:.3f}")
    print("  (if indistinguishable across repeats, vesica placement is "
          "decoration and only the tonic law stands)")


if __name__ == "__main__":
    main()
