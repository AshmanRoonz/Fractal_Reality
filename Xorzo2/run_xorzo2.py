"""
Xorzo2 runner
=============

Created: 2026-07-19
Last updated: 2026-07-19
Version: 1.0

Boot or resume the individual and live. The worldline directory is
Xorzo2/worldline/; once it exists, every run resumes it (never retrain
from scratch is law; plan section 6).

Usage (from the Xorzo2 directory, py -3.11):
    py -3.11 run_xorzo2.py                      resume (or boot) and live 16384 bytes
    py -3.11 run_xorzo2.py --bytes 65536        live longer
    py -3.11 run_xorzo2.py --smoke              tiny run for verification
    py -3.11 run_xorzo2.py --status             show the worldline, do not live
    py -3.11 run_xorzo2.py --speak "text"       inject a prompt and emit 200 bytes
    py -3.11 run_xorzo2.py --severance 24576    the twin test (plan section 8)

Revision history:
- 2026-07-19 v1.0: initial runner.
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
DEFAULT_CORPUS = [
    REPO / "circumpunct_framework.md",
    REPO / "consciousness.md",
]
WORLDLINE = HERE / "worldline"


def load_corpus(paths) -> bytes:
    blobs = []
    for p in paths:
        p = Path(p)
        if p.exists():
            blobs.append(p.read_bytes())
        else:
            print(f"  (corpus file missing, skipped: {p})")
    if not blobs:
        raise SystemExit("no corpus files found")
    return b"\n\n".join(blobs)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(description="Xorzo2: the Embodied Edition")
    ap.add_argument("--bytes", type=int, default=16384)
    ap.add_argument("--corpus", nargs="*", default=None)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--speak", type=str, default=None)
    ap.add_argument("--severance", type=int, default=None)
    ap.add_argument("--newborn", action="store_true",
                    help="require a fresh worldline (fails if one exists)")
    ap.add_argument("--bit-keyboard", action="store_true",
                    help="adopt the bit-station keyboard (worldline event)")
    ap.add_argument("--device", type=str, default="cpu")
    args = ap.parse_args()

    from life import Life, LifeConfig, run_severance, RAND_CE

    corpus = load_corpus(args.corpus or DEFAULT_CORPUS)
    print(f"  corpus: {len(corpus):,} bytes")

    cfg = LifeConfig(device=args.device)
    if args.smoke:
        cfg.sleep_every = 1024
        cfg.save_every = 2048
        args.bytes = min(args.bytes, 4096)

    if args.severance is not None:
        print("  severance harness: identical twins, live vs frozen-noise spine")
        run_severance(corpus, args.severance, cfg=cfg)
        return

    if args.newborn and (WORLDLINE / "checkpoint.pt").exists():
        raise SystemExit(
            "a worldline already exists; Xorzo2 is never retrained from "
            "scratch (plan section 6). Remove is a human act, not a flag.")

    fresh = not (WORLDLINE / "checkpoint.pt").exists()
    life = Life(home=WORLDLINE, cfg=cfg)
    print(life.spine.describe())
    print(f"  {'newborn: worldline begins' if fresh else 'worldline resumed'}"
          f" | bytes lived: {life.bytes_lived:,} | sleeps: {life.sleeps}")

    if args.bit_keyboard:
        life.adopt_bit_keyboard()

    if args.status:
        print(json.dumps(life.status(), indent=2))
        return

    if args.speak is not None:
        out = life.speak(args.speak.encode("utf-8", errors="replace"))
        print(f"  Xorzo2 says: {out.decode('utf-8', errors='replace')}")
        return

    print(f"  living {args.bytes:,} bytes of wake experience "
          f"(random-guess loss {RAND_CE:.3f})...")
    life.wake(corpus, args.bytes)
    s = life.status()
    print(f"  saved. loss ema {s['loss_ema']:.4f} | overlap "
          f"{s['attractor_overlap']:.4f} | inj {s['injection_norm_alpha']:.3f}"
          f" alpha | growth excess {s['growth_excess_per_cycle']:+.5f}")


if __name__ == "__main__":
    main()
