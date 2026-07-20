"""
Xorzo2 sleep test: does learning without external input matter?
===============================================================

Created: 2026-07-19
Last updated: 2026-07-19
Version: 1.0

Falsification handle 3 (plan section 8): wake-only learning vs
wake+sleep learning. Two twins on an identical wake schedule; twin A's
sleeps learn (replay + dreams per the maturation schedule), twin B's
sleeps only rest (cfg.sleep_learning = False). The classic prediction
from continual learning: online streaming forgets; internal replay is
the cure. Measured as RETENTION:

    live chunk 1  ->  eval on a probe slice of chunk 1 (baseline)
    live chunk 2  ->  eval the same probe again (retention) and a
                      probe of chunk 2 (recency)

If the sleeping twin does not retain chunk 1 better, sleep learning
adds nothing and the claim retracts (the spine's wake/sleep operator
distinction is untouched: it is derived, not claimed from this test).

Honesty note: the sleeping twin takes MORE gradient steps (its sleep
steps), but on NO new external data: the extra internal steps ARE the
treatment under test. A strictly step-matched variant (extra wake
passes for the rest-only twin) is future work and noted in the plan.

Run: py -3.11 sleep_test.py [--fast]

Revision history:
- 2026-07-19 v1.0: initial retention harness.
"""

import sys
from pathlib import Path

from life import Life, LifeConfig

FAST = "--fast" in sys.argv
CHUNK = 8192 if FAST else 65536
PROBE = 2048 if FAST else 4096


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    root = Path(__file__).resolve().parent.parent
    corpus = (root / "circumpunct_framework.md").read_bytes()
    chunk1 = corpus[:CHUNK]
    chunk2 = corpus[CHUNK:2 * CHUNK]
    probe1 = chunk1[:PROBE + 1]
    probe2 = chunk2[:PROBE + 1]

    print("Xorzo2 sleep test: wake+sleep learning vs wake-only "
          f"(chunks {CHUNK}, probe {PROBE})")
    results = {}
    for label, sleep_on in [("sleeps-learn", True), ("rest-only", False)]:
        cfg = LifeConfig(sleep_learning=sleep_on, growth_enabled=False)
        life = Life(home=None, cfg=cfg, torch_seed=137)
        life.wake(chunk1, CHUNK, quiet=True)
        base1 = life.eval_loss(probe1, PROBE)
        life.wake(chunk2, CHUNK, quiet=True)
        ret1 = life.eval_loss(probe1, PROBE)
        rec2 = life.eval_loss(probe2, PROBE)
        forgetting = ret1 - base1
        results[label] = (base1, ret1, rec2, forgetting)
        print(f"\n  [{label}] sleeps {life.sleeps}, replay "
              f"{life.replay_bytes} bytes, dreams {life.dream_bytes} "
              f"bytes")
        print(f"    chunk1 baseline {base1:.4f} -> after chunk2 "
              f"{ret1:.4f}  (forgetting {forgetting:+.4f})")
        print(f"    chunk2 recency  {rec2:.4f}")
        if sleep_on and life.last_dream:
            printable = "".join(chr(b) if 32 <= b < 127 else "?"
                                for b in life.last_dream[:60])
            print(f"    last dream: {printable}")

    fa = results["sleeps-learn"][3]
    fb = results["rest-only"][3]
    print(f"\n  verdict: forgetting with sleep learning {fa:+.4f} vs "
          f"rest-only {fb:+.4f} "
          f"({'sleep retains better' if fa < fb else 'NO retention benefit'})")


if __name__ == "__main__":
    main()
