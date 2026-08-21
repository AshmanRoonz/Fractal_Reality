"""
Pre-registered candidate search for the JUNO pair.

Created: 2026-08-21
Last updated: 2026-08-21
Version: 1.1
History:
  - 2026-08-21 v1.1: removed a value cap (fractions < 1) that v1.0 imposed but
    the frozen spec never stated; the cap emptied F2 for Target 1 (the Cabibbo
    precedent's own prefactor is 8/3 > 1). Fractions now range freely; the
    band filters do the selecting. No other change; incident noted in Part II.
  - 2026-08-21 v1.0: initial; implements the frozen spec of
    plans/preregistration_juno_computation_2026_08_21.md Part I (sections 5-6).

This script is Part II's instrument. It enumerates the FROZEN candidate space
(atom list, families F1/F2/F3, Tier 1 fractions, caps) against the two picked
targets, and calibrates every count against matched-magnitude null windows per
the binding section 27.7n bar. It reports everything: totals, in-band lists,
null quantiles, economy tiers. It selects nothing; the decision procedure
(filters A/B/C and the verdict rules) is applied in the record, in the frozen
order, from this output.

Implementation readings of the frozen text (declared, not silent):
  1. F1's parenthetical "correction well under 1%" is implemented as
     |n*alpha/K| <= 1% of the target (window center for nulls).
  2. Null-window "filtered survivor" statistics use the mechanical economy
     tier only (the address filter is semantic and target-specific, so it
     cannot run on null windows); Part II says so when comparing.
  3. Economy count = distinct atoms used + 1 if alpha appears + 1 if the
     half-power base appears; a value reachable by several expressions
     carries the minimum.
"""

import bisect
import math
import random

# ---------------------------------------------------------------- frozen pool
ATOMS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 20, 21, 24, 27,
         28, 32, 35, 39, 56, 58, 59, 64, 72, 81, 84, 91, 126, 169, 247]
ALPHA = 1.0 / 137.035999177          # CODATA 2022, as frozen
PHI = (1.0 + math.sqrt(5.0)) / 2.0   # carrier, available to the space; the
                                     # frozen families do not use phi in a
                                     # slot, so it appears nowhere below.

# ------------------------------------------------------------- frozen targets
T1_C, T1_S = 0.3092, 0.0087                      # sin^2 theta_12 (JUNO 2026)
DM21_C, DM21_S = 7.50e-5, 0.12e-5                # JUNO 2026
DM31_C, DM31_S = 2.534e-3, 0.024e-3              # NuFIT 6.0 NO, symmetrized
T2_C = DM21_C / DM31_C
T2_S = T2_C * math.sqrt((DM21_S / DM21_C) ** 2 + (DM31_S / DM31_C) ** 2)

NULL_RANGE = {"T1": (0.15, 0.50), "T2": (0.010, 0.090)}
N_NULL = 2000
random.seed(27)

KEY = lambda v: round(v, 14)  # dedupe key at 1e-14 absolute on rounded value


def econ(atoms_used, uses_alpha, uses_half):
    return len(set(atoms_used)) + (1 if uses_alpha else 0) + (1 if uses_half else 0)


# ------------------------------------------------- Tier 1 fractions p/q (F3)
frac1 = {}   # value -> list of (expr, econ); no magnitude cap (frozen spec has none)
for p in ATOMS:
    for q in ATOMS:
        v = p / q
        if 1e-4 < v < 300.0:
            frac1.setdefault(KEY(v), []).append((f"{p}/{q}", econ([p, q], False, False)))

# --------------------------------------------- Tier 2 fractions (sensitivity)
prods = {}
for i, a in enumerate(ATOMS):
    prods.setdefault(a, f"{a}")
    for b in ATOMS[i:]:
        prods.setdefault(a * b, f"{a}*{b}")
tier2_vals = set()
for pn in prods:
    for pd in prods:
        v = pn / pd
        if 1e-4 < v < 1.0:
            tier2_vals.add(KEY(v))
tier2_sorted = sorted(tier2_vals)

# ------------------------------------------------------- F2 value families
half_vals = {}  # c-key -> (c_expr, c_econ_atoms)
half_vals[0.0] = ("0", [])
for a in ATOMS:
    for b in ATOMS:
        c = a / b
        if c <= 13.0:
            k = KEY(c)
            if k not in half_vals:
                half_vals[k] = (f"{a}/{b}", [a, b])

f2_direct = {}  # value -> (expr, econ) best; sin-form values kept up to 1.2
for ck, (cexpr, catoms) in half_vals.items():
    base = ALPHA ** (0.5 + ck * ALPHA)
    for fk, exprs in frac1.items():
        v = base * fk
        if not (1e-4 < v < 1.2):
            continue
        pexpr, _ = exprs[0]
        patoms = [int(x) for x in exprs[0][0].split("/")]
        e = econ(patoms + catoms, True, True)
        expr = (f"alpha^(1/2)*({pexpr})" if ck == 0.0
                else f"alpha^(1/2+({cexpr})*alpha)*({pexpr})")
        kv = KEY(v)
        cur = f2_direct.get(kv)
        if cur is None or e < cur[1]:
            f2_direct[kv] = (expr, e)

f2_sin2 = {}    # squared values for Target 1
for kv, (expr, e) in f2_direct.items():
    v2 = KEY(kv * kv)
    cur = f2_sin2.get(v2)
    if cur is None or e < cur[1]:
        f2_sin2[v2] = (f"[{expr}]^2", e)

# ------------------------------------------------------- F1 correction terms
corr = {}   # value -> (expr, atoms)
for n in [a for a in ATOMS if a <= 13]:
    for Kd in ATOMS:
        cv = n * ALPHA / Kd
        k = KEY(cv)
        if k not in corr or econ([n, Kd], True, False) < corr[k][2]:
            corr[k] = (f"{n}*alpha/{Kd}", [n, Kd], econ([n, Kd], True, False))

frac1_sorted = sorted(frac1.keys())
frac1_econ = {k: min(e for _, e in v) for k, v in frac1.items()}
corr_sorted = sorted((ck, cexpr, catoms) for ck, (cexpr, catoms, _) in corr.items())


def f1_candidates(center, halfwidth):
    """Frozen F1: Tier 1 base within 2 percent of center, correction with
    magnitude <= 1 percent of center, total inside the band."""
    out = {}
    lo_b = bisect.bisect_left(frac1_sorted, center * 0.98)
    hi_b = bisect.bisect_right(frac1_sorted, center * 1.02)
    cap = 0.01 * center
    for bk in frac1_sorted[lo_b:hi_b]:
        bexpr, _ = frac1[bk][0]
        batoms = [int(x) for x in bexpr.split("/")]
        # n = 0 case (pure base) counts under F1 iff inside band
        if abs(bk - center) <= halfwidth:
            kv = KEY(bk)
            e = econ(batoms, False, False)
            if kv not in out or e < out[kv][1]:
                out[kv] = (f"{bexpr}", e)
        for ck, cexpr, catoms in corr_sorted:
            if ck > cap:
                break
            for sgn, s in ((+1, "+"), (-1, "-")):
                v = bk + sgn * ck
                if abs(v - center) <= halfwidth:
                    kv = KEY(v)
                    e = econ(batoms + catoms, True, False)
                    expr = f"{bexpr} {s} {cexpr}"
                    if kv not in out or e < out[kv][1]:
                        out[kv] = (expr, e)
    return out


def f1_count(center, halfwidth):
    """Counting-only variant of f1_candidates for the null loops."""
    seen = set()
    lo_b = bisect.bisect_left(frac1_sorted, center * 0.98)
    hi_b = bisect.bisect_right(frac1_sorted, center * 1.02)
    cap = 0.01 * center
    for bk in frac1_sorted[lo_b:hi_b]:
        if abs(bk - center) <= halfwidth:
            seen.add(KEY(bk))
        for ck, _, _ in corr_sorted:
            if ck > cap:
                break
            if abs(bk + ck - center) <= halfwidth:
                seen.add(KEY(bk + ck))
            if abs(bk - ck - center) <= halfwidth:
                seen.add(KEY(bk - ck))
    return len(seen)


def in_band(sorted_vals, lo, hi):
    return bisect.bisect_right(sorted_vals, hi) - bisect.bisect_left(sorted_vals, lo)


def econ_tier_count(sorted_vals, econs, lo, hi):
    i0, i1 = bisect.bisect_left(sorted_vals, lo), bisect.bisect_right(sorted_vals, hi)
    if i0 == i1:
        return 0, None
    es = econs[i0:i1]
    m = min(es)
    return sum(1 for e in es if e == m), m


def null_stats(fn, rel_hw, rng_lo, rng_hi):
    counts = []
    for _ in range(N_NULL):
        c = random.uniform(rng_lo, rng_hi)
        counts.append(fn(c, rel_hw * c))
    counts.sort()
    return counts[N_NULL // 2], counts[int(N_NULL * 0.9)]


def report_family(name, cand_map, center, sigma):
    lo, hi = center - sigma, center + sigma
    hits = [(k, *cand_map[k]) for k in cand_map if lo <= k <= hi]
    hits.sort(key=lambda h: abs(h[0] - center))
    print(f"  {name}: {len(hits)} in-band value(s)")
    show = hits[:40]
    for v, expr, e in show:
        print(f"    {v:.6f}  ({(v - center) / sigma:+.2f} sigma)  econ={e}  {expr}")
    if len(hits) > 40:
        print(f"    ... {len(hits) - 40} more suppressed in print, counted above")
    if hits:
        m = min(h[2] for h in hits)
        tier = [h for h in hits if h[2] == m]
        print(f"    minimal economy tier: econ={m}, {len(tier)} member(s):")
        for v, expr, e in tier[:15]:
            print(f"      -> {v:.6f}  ({(v - center) / sigma:+.2f} sigma)  {expr}")
    return hits


def run_target(tag, center, sigma):
    rel_hw = sigma / center
    print(f"\n=== Target {tag}: {center:.6f} +/- {sigma:.6f} "
          f"(band [{center - sigma:.6f}, {center + sigma:.6f}], rel width {rel_hw:.4f}) ===")
    rng_lo, rng_hi = NULL_RANGE[tag]

    # F3
    f3_sorted = frac1_sorted
    f3_econs = [frac1_econ[k] for k in f3_sorted]
    hits3 = report_family("F3 (pure Tier 1 fraction)",
                          {k: (frac1[k][0][0], frac1_econ[k]) for k in frac1},
                          center, sigma)
    med, p90 = null_stats(lambda c, hw: in_band(f3_sorted, c - hw, c + hw), rel_hw, rng_lo, rng_hi)
    tmed, tp90 = null_stats(lambda c, hw: econ_tier_count(f3_sorted, f3_econs, c - hw, c + hw)[0],
                            rel_hw, rng_lo, rng_hi)
    print(f"    null (raw in-band): median={med}, p90={p90}; "
          f"null (econ-tier size): median={tmed}, p90={tp90}")

    # F1
    f1map = f1_candidates(center, sigma)
    hits1 = report_family("F1 (fraction + n*alpha/K)", f1map, center, sigma)
    med1, p901 = null_stats(f1_count, rel_hw, rng_lo, rng_hi)
    print(f"    null (raw in-band): median={med1}, p90={p901}")

    # F2
    fam = f2_sin2 if tag == "T1" else f2_direct
    f2_sorted = sorted(fam.keys())
    f2_econs = [fam[k][1] for k in f2_sorted]
    hits2 = report_family("F2 (alpha^(1/2+c*alpha) * p/q" + (", squared" if tag == "T1" else ")"),
                          {k: fam[k] for k in fam}, center, sigma)
    med2, p902 = null_stats(lambda c, hw: in_band(f2_sorted, c - hw, c + hw), rel_hw, rng_lo, rng_hi)
    tmed2, tp902 = null_stats(lambda c, hw: econ_tier_count(f2_sorted, f2_econs, c - hw, c + hw)[0],
                              rel_hw, rng_lo, rng_hi)
    print(f"    null (raw in-band): median={med2}, p90={p902}; "
          f"null (econ-tier size): median={tmed2}, p90={tp902}")

    # Tier 2 sensitivity (multiplicity picture only; not pre-registrable)
    n2 = in_band(tier2_sorted, center - sigma, center + sigma)
    med_t2, p90_t2 = null_stats(lambda c, hw: in_band(tier2_sorted, c - hw, c + hw),
                                rel_hw, rng_lo, rng_hi)
    print(f"  Tier 2 sensitivity: {n2} in-band of {len(tier2_sorted)} values "
          f"(null median={med_t2}, p90={p90_t2}) -> multiplicity context only")
    return hits3, hits1, hits2


print("Pre-registered JUNO-pair search v1.0 (frozen spec)")
print(f"alpha = 1/137.035999177; atoms = {ATOMS}")
print(f"Tier 1 distinct fraction values in (1e-4, 1): {len(frac1)}")
print(f"F2 distinct direct values: {len(f2_direct)}; squared: {len(f2_sin2)}")
print(f"Target 2 band from quoted inputs: {T2_C:.6f} +/- {T2_S:.6f}")

run_target("T1", T1_C, T1_S)
run_target("T2", T2_C, T2_S)
print("\nDone. Decision procedure (filters A/B/C, verdict rules) applies in the record.")
