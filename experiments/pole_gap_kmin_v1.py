"""k_min and the discovery lag on ring 15: testing the pole-gap calculus.

Created: 2026-07-27
Last updated: 2026-07-27
Version: 1.0
History:
- 2026-07-27 v1.0: initial. Tests the floor theorem's k_min and the proposed
  discovery lag Lambda_k against the live page's own substrate and observer
  constants. Result: the page's FLOOR FOUND indicator is a false positive at
  its default setting (see companion findings).

Floor theorem:  the observer can predict perfectly exactly when every repeated
context has a unique successor, i.e. H(Y_{t+1} | C_t^(k)) = 0.
  k_min    = min{k : H = 0}                 minimum integration depth
  Lambda_k = tau_found - tau_cycle          discovery lag

The page's FOUND light uses an ABSOLUTE threshold (ema < 0.3 bits/step), which
is not the floor theorem's condition. This sweep separates them.

Companion findings: pole_gap_kmin_findings_v1.md
Run: py -3.11 experiments/pole_gap_kmin_v1.py
"""
import math
from collections import defaultdict

W, N = 15, 400_000
# live-page observer constants, so the lag is comparable to the demo's numbers
EMA_A, FOUND_EMA, FOUND_RUN, MIN_SCORED = 1/400, 0.3, 1500, 3000
REL_MARGIN = 0.05          # "reached its own floor" = ema < H_k + 0.05


def rule30_center(n, w=W):
    row = [0]*w; row[w//2] = 1
    out = []
    for _ in range(n):
        out.append(row[w//2])
        nxt = [0]*w
        for i in range(w):
            l, c, r = row[(i-1) % w], row[i], row[(i+1) % w]
            nxt[i] = l ^ (c | r)
        row = nxt
    return out


def substrate_cycle(w=W, cap=200_000):
    """Exact revisit of the FULL row: when the floor comes to exist."""
    row = [0]*w; row[w//2] = 1
    seen = {}
    for t in range(1, cap+1):
        nxt = [0]*w
        for i in range(w):
            l, c, r = row[(i-1) % w], row[i], row[(i+1) % w]
            nxt[i] = l ^ (c | r)
        row = nxt
        key = tuple(row)
        if key in seen:
            return t, t - seen[key], seen[key]
        seen[key] = t
    return None, None, None


def structural(bits, k, start, period):
    """H(Y|C_k) on the periodic orbit, S_k, and the ambiguous-context count."""
    counts = defaultdict(lambda: [0, 0])
    orbit = bits[start:start+period]
    for i in range(period):
        ctx = tuple(orbit[(i - k + j) % period] for j in range(k))
        counts[ctx][orbit[i]] += 1
    H, amb = 0.0, 0
    for c in counts.values():
        n = c[0] + c[1]
        if c[0] and c[1]:
            amb += 1
        for y in (0, 1):
            if c[y]:
                p = c[y]/n
                H -= (n/period) * p * math.log2(p)
    return H, len(counts), amb


def kt_run(bits, k, abs_thresh, rel_thresh):
    """Prequential KT. Returns crossing times for the absolute (page) bar and
    for the observer's own floor, plus final EMA and accuracy."""
    counts = {}
    ctx = []
    ema, below_abs, below_rel = 1.0, 0, 0
    scored, hits = 0, 0
    t_abs, t_rel = None, None
    for t, b in enumerate(bits):
        if len(ctx) == k:
            key = tuple(ctx)
            cell = counts.get(key)
            if cell is None:
                cell = [0, 0]; counts[key] = cell
            tot = cell[0] + cell[1]
            p1 = (cell[1] + 0.5) / (tot + 1)
            p = p1 if b else 1 - p1
            ema += (-math.log2(max(p, 1e-12)) - ema) * EMA_A
            scored += 1
            hits += (1 if p1 > 0.5 else 0) == b
            below_abs = below_abs + 1 if (scored > MIN_SCORED and ema < abs_thresh) else 0
            below_rel = below_rel + 1 if (scored > MIN_SCORED and ema < rel_thresh) else 0
            if t_abs is None and below_abs >= FOUND_RUN:
                t_abs = t + 1
            if t_rel is None and below_rel >= FOUND_RUN:
                t_rel = t + 1
            cell[b] += 1
        ctx.append(b)
        if len(ctx) > k:
            ctx.pop(0)
    return t_abs, t_rel, ema, hits/max(scored, 1)


def main():
    tau_cycle, period, first = substrate_cycle()
    print(f"ring {W}: substrate revisits at {tau_cycle:,}, period {period:,}\n")
    bits = rule30_center(N)

    print(f"{'k':>4}{'H(Y|C_k)':>11}{'S_k':>7}{'amb':>6}{'acc %':>8}"
          f"{'FOUND(abs)':>12}{'Lam_abs':>9}{'own floor':>11}{'Lam_rel':>9}")
    print("-" * 78)
    kmin, rows = None, []
    for k in range(8, 25):
        H, S, amb = structural(bits, k, first, period)
        if H == 0.0 and kmin is None:
            kmin = k
        ta, tr, ema, acc = kt_run(bits, k, FOUND_EMA, H + REL_MARGIN)
        rows.append((k, H, S, amb, ta, tr, acc))
        print(f"{k:>4}{H:>11.4f}{S:>7}{amb:>6}{acc*100:>8.2f}"
              f"{(f'{ta:,}' if ta else 'never'):>12}"
              f"{(f'{ta-tau_cycle:,}' if ta else '-'):>9}"
              f"{(f'{tr:,}' if tr else 'never'):>11}"
              f"{(f'{tr-tau_cycle:,}' if tr else '-'):>9}")

    print(f"\nk_min (first k with H = 0 exactly) = {kmin}")
    print(f"H reaches 0 when every phase of the period has a distinct "
          f"k-context (S_k = period = {period:,})\n")

    print("THE CATCH: rows where the page says FOUND but H(Y|C_k) > 0")
    caught = [(k, H, acc) for k, H, S, amb, ta, tr, acc in rows
              if ta is not None and H > 1e-12]
    for k, H, acc in caught:
        print(f"  k={k:>2}: FOUND fires, but H={H:.4f} bits/step is a permanent "
              f"floor; accuracy plateaus at {acc*100:.1f}%, not 100%")
    if not caught:
        print("  none")


if __name__ == "__main__":
    main()
