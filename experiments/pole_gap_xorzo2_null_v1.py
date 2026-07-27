"""Point the pole-gap ledger at Xorzo2's own stream, at Xorzo2's own budget.

Created: 2026-07-27
Last updated: 2026-07-27
Version: 1.0
History:
- 2026-07-27 v1.0: initial. Applies the prequential instrument from
  pole_gap_transfer_v1.py to the corpus Xorzo2 lives on, to ask whether the
  unigram line is the right null for the severance verdict (Xorzo2 F2).

READ-ONLY BY CONSTRUCTION. This module never imports Xorzo2, never runs it,
and never touches Xorzo2/worldline/. It reads the same corpus bytes that
run_xorzo2.py streams and prices them with its own estimator. Xorzo2's
reported figures below are quoted from Xorzo2/findings_stage1.md for
comparison only; nothing here re-measures Xorzo2 itself.

Companion findings: pole_gap_xorzo2_null_findings_v1.md
Run: py -3.11 experiments/pole_gap_xorzo2_null_v1.py
"""
import math, random
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CORPUS_FILES = [REPO / "circumpunct_framework.md", REPO / "consciousness.md"]
BUDGET = 830_000          # bytes Xorzo2 had lived at its reported 3.07
A = 256                   # alphabet
HALF_A = A / 2.0          # Dirichlet(1/2) normalizer: KT generalized to A symbols
TAIL = 100_000            # trailing window, to compare against a late-life EMA

# Xorzo2's reported figures (findings_stage1.md), for comparison only.
XORZO_UNIGRAM = 3.517
XORZO_RANDOM = 5.545
XORZO_VOICE_RECURRENT = 3.44
XORZO_VOICE_MEMORYLESS = 3.18
XORZO_VOICE_BEST = 3.07


def load_corpus():
    blobs = []
    for p in CORPUS_FILES:
        if p.exists():
            blobs.append(p.read_bytes())
        else:
            print(f"  (missing, skipped: {p})")
    return b"".join(blobs)


def prequential(stream, k):
    """Price each byte BEFORE it lands, pay the log-loss. Returns nats/byte.

    Dirichlet(1/2) per context (KT generalized to a 256-symbol alphabet).
    A context seen once cannot fake certainty; fresh contexts cost ln(256).

    Returns (lifetime mean, trailing-window mean, distinct contexts). The
    trailing figure is the apples-to-apples comparison with a late-life
    running loss; the lifetime mean carries all the early ignorance.
    """
    counts = {}
    loss = 0.0
    scored = 0
    tail_loss = 0.0
    tail_scored = 0
    n = len(stream)
    tail_start = n - TAIL
    for t in range(k, n):
        ctx = stream[t - k:t] if k else b""
        b = stream[t]
        cell = counts.get(ctx)
        if cell is None:
            cell = [0, {}]
            counts[ctx] = cell
        tot, tab = cell
        p = (tab.get(b, 0) + 0.5) / (tot + HALF_A)
        l = -math.log(p)
        loss += l
        scored += 1
        if t >= tail_start:
            tail_loss += l
            tail_scored += 1
        tab[b] = tab.get(b, 0) + 1
        cell[0] = tot + 1
    return loss / scored, tail_loss / max(tail_scored, 1), len(counts)


def main():
    corpus = load_corpus()
    print(f"corpus: {len(corpus):,} bytes ({', '.join(p.name for p in CORPUS_FILES)})")

    # Xorzo2 reads cyclically from position 0; at 830K against a 1.44M corpus
    # it had not yet wrapped, so a prefix matches its reading exactly.
    stream = corpus[:BUDGET] if len(corpus) >= BUDGET else (
        (corpus * (BUDGET // len(corpus) + 1))[:BUDGET])
    print(f"stream:  {len(stream):,} bytes (Xorzo2's lived budget)\n")

    freq = {}
    for b in stream:
        freq[b] = freq.get(b, 0) + 1
    H0 = -sum((c / len(stream)) * math.log(c / len(stream)) for c in freq.values())
    print(f"static unigram entropy of this stream: {H0:.3f} nats "
          f"(Xorzo2 reports {XORZO_UNIGRAM}; the corpus has been edited since "
          f"2026-07-19, so small drift is expected)")
    print(f"uniform-random reference: {math.log(A):.3f} nats "
          f"(Xorzo2 reports {XORZO_RANDOM})\n")

    # Matched-entropy control: identical byte histogram, all higher-order
    # structure destroyed. This is the CALIBRATED null the pole-gap control
    # argues for, in place of a static entropy number.
    shuffled = list(stream)
    random.Random(30).shuffle(shuffled)
    shuffled = bytes(shuffled)

    print(f"{'order':>6}{'real life':>11}{'real tail':>11}{'null life':>11}"
          f"{'null tail':>11}{'structure':>11}{'contexts':>12}")
    print("-" * 78)
    results = {}
    for k in (0, 1, 2, 3, 4):
        real, real_tail, nctx = prequential(stream, k)
        null, null_tail, _ = prequential(shuffled, k)
        results[k] = (real, real_tail, null, null_tail)
        print(f"{k:>6}{real:>11.3f}{real_tail:>11.3f}{null:>11.3f}"
              f"{null_tail:>11.3f}{null - real:>11.3f}{nctx:>12,}")

    print("\n(life = mean over all 830K bytes; tail = mean over the last "
          f"{TAIL:,}, the fair\n comparison against a late-life running loss)\n")
    best_k = min(results, key=lambda k: results[k][1])
    best_life, best_tail = results[best_k][0], results[best_k][1]
    print(f"best context model: order {best_k} at {best_tail:.3f} nats/byte "
          f"(tail), {best_life:.3f} (lifetime)")
    print(f"Xorzo2 reported:    {XORZO_VOICE_BEST:.3f} nats/byte at 830K "
          f"(memoryless voice, spine as sole memory channel)")
    print(f"  vs unigram line     {XORZO_UNIGRAM:.3f}: Xorzo2 "
          f"{XORZO_UNIGRAM - XORZO_VOICE_BEST:+.3f} nats")
    print(f"  vs order-1 tail     {results[1][1]:.3f}: Xorzo2 "
          f"{results[1][1] - XORZO_VOICE_BEST:+.3f} nats "
          f"({'BEATS' if XORZO_VOICE_BEST < results[1][1] else 'LOSES TO'} "
          f"a one-byte lookup)")
    print(f"  vs order-{best_k} tail     {best_tail:.3f}: Xorzo2 "
          f"{best_tail - XORZO_VOICE_BEST:+.3f} nats "
          f"({'BEATS' if XORZO_VOICE_BEST < best_tail else 'LOSES TO'} "
          f"the best ledger)")


if __name__ == "__main__":
    main()
