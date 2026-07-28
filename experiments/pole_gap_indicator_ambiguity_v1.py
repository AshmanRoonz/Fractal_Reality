"""Instrument Pole Gap: IPG_mu(C;T) = H_mu(C|T), and its prior-free companion.

Created: 2026-07-27
Last updated: 2026-07-27
Version: 1.1
History:
- 2026-07-27 v1.1: added IPG_max (prior-free worst-fiber ambiguity) and an
  explicit refinement check. The period marker turns out to be a REPLACEMENT
  for the threshold light, not a refinement of it.
- 2026-07-27 v1.0: initial. Measures the residual ambiguity of the live page's
  threshold indicator about the claim it was labelled with, and shows the
  prior-dependence of the average measure.

See plans/pole_gap_boundary.md section 2a.
Run: py -3.11 experiments/pole_gap_indicator_ambiguity_v1.py
"""
import math

# ring-15 k-sweep, measured (pole_gap_kmin_findings_v1.md)
DATA = [  # k, H(Y|C_k), FOUND light fired, S_k
    (8, 0.8636, 0, 254), (9, 0.6676, 0, 488), (10, 0.4499, 0, 782),
    (11, 0.2902, 0, 1036), (12, 0.1569, 1, 1219), (13, 0.0910, 1, 1323),
    (14, 0.0418, 1, 1386), (15, 0.0239, 1, 1416), (16, 0.0143, 1, 1433),
    (17, 0.0096, 1, 1443), (18, 0.0027, 1, 1450), (19, 0.0027, 1, 1452),
    (20, 0.0014, 1, 1454), (21, 0.0, 1, 1455), (22, 0.0, 1, 1455),
    (23, 0.0, 1, 1455), (24, 0.0, 1, 1455)]
P = 1455

LIGHT = lambda k, H, f, S: f                       # the page's threshold light
PERIOD = lambda k, H, f, S: S == P                 # marker from the same data
CLAIM = lambda k, H, f, S: 1 if H == 0.0 else 0    # "the floor is found"


def h2(p):
    return 0.0 if p <= 0 or p >= 1 else -(p*math.log2(p) + (1-p)*math.log2(1-p))


def IPG_mu(rows, T):
    """H_mu(C | T) under the uniform prior on the supplied rows."""
    groups = {}
    for r in rows:
        groups.setdefault(T(*r), []).append(CLAIM(*r))
    tot = len(rows)
    return sum((len(cs)/tot)*h2(sum(cs)/len(cs)) for cs in groups.values())


def IPG_max(rows, T):
    """max over fibers of log2 |distinct claim values compatible with it|."""
    groups = {}
    for r in rows:
        groups.setdefault(T(*r), set()).add(CLAIM(*r))
    return max(math.log2(len(v)) for v in groups.values())


def is_refinement(rows, T_coarse, T_fine):
    """Is T_coarse = f(T_fine)? Each fine fiber must carry one coarse value."""
    m = {}
    for r in rows:
        f, c = T_fine(*r), T_coarse(*r)
        if f in m and m[f] != c:
            return False
        m[f] = c
    return True


def main():
    print("claim C = 'the floor is found', i.e. H(Y|C_k) = 0\n")
    for name, T in (("threshold light (EMA < 0.3 sustained)", LIGHT),
                    ("S_k == period", PERIOD)):
        print(f"indicator T = {name}:")
        for lo, hi, lab in ((8, 24, "k in 8..24"), (10, 22, "k in 10..22"),
                            (12, 24, "k in 12..24")):
            rows = [r for r in DATA if lo <= r[0] <= hi]
            print(f"  IPG_mu   prior {lab:<12} = {IPG_mu(rows, T):.4f} bits")
        print(f"  IPG_max  (prior-free)      = {IPG_max(DATA, T):.4f} bits\n")

    print("REFINEMENT CHECK. Refinement requires the old reading to be")
    print("recoverable from the new one; only then is improvement guaranteed")
    print("under EVERY prior.")
    print(f"  light  = f(period)?  {is_refinement(DATA, LIGHT, PERIOD)}")
    print(f"  period = f(light)?   {is_refinement(DATA, PERIOD, LIGHT)}")
    print("  -> neither. The period marker REPLACES the light rather than")
    print("     refining it. It is still universally at least as good, but")
    print("     because it attains IPG_max = 0, not by the refinement order.")


if __name__ == "__main__":
    main()
