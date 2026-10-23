"""
alpha_resonance_numbers_v1.py

Created: 2026-10-22
Last updated: 2026-10-22
Version: 1.0
History:
- 2026-10-22 v1.0: initial. Numbers and figure for the staged proposal
  plans/alpha_resonance_reframing_2026_10_22.md (not canon until countersign).

Recomputes every number the alpha resonance proposal cites:
  1. the three stages of 1/alpha = 360/phi^2 - 2/phi^3 + (third term), with
     both known third terms (ours: +alpha*3/59; Pellis 2021: +(3*phi)^-5);
  2. look-elsewhere counts for each stage within declared families, and a
     matched null for stage 2;
  3. both closures against the two best direct measurements (Cs 2018, Rb 2020),
     which disagree with each other;
  4. the phyllotaxis comparison: continued fractions of the golden angle and of
     the "alpha angle" 137.036 deg as divergence angles, and an SVG figure.

Plain Python, no dependencies. Run from anywhere:
    python experiments/alpha_resonance_numbers_v1.py
The figure is written to plans/alpha_resonance_phyllotaxis_2026_10_22.svg.
"""
import math
import os
import random
from fractions import Fraction

PHI = (1 + math.sqrt(5)) / 2
CODATA = 137.035999177        # CODATA 2022 1/alpha
U_CODATA = 0.000000021
CS_2018 = (137.035999046, 0.000000027)   # Parker et al., Science 2018 (Berkeley, Cs recoil)
RB_2020 = (137.035999206, 0.000000011)   # Morel et al., Nature 2020 (LKB Paris, Rb recoil)
ALPHA = 1 / CODATA

GOLDEN_DEG = 360 / PHI**2
BASE = GOLDEN_DEG - 2 / PHI**3
OURS = (BASE + math.sqrt(BASE * BASE + 4 * 3 / 59)) / 2   # positive root of x^2 - BASE x - 3/59 = 0
PELLIS = BASE + (3 * PHI) ** -5


def ppb(v, ref):
    return (v - ref) / ref * 1e9


def stages():
    print("== stages ==")
    print(f"golden angle 360/phi^2 = {GOLDEN_DEG:.9f}  rel to 1/alpha {(GOLDEN_DEG - CODATA) / CODATA:+.4%}")
    n = min(range(300, 420), key=lambda k: abs(k / PHI**2 - CODATA))
    print(f"best n in n/phi^2: {n} -> {n / PHI**2:.6f}  rel {(n / PHI**2 - CODATA) / CODATA:+.4%}")
    gap = GOLDEN_DEG - CODATA
    print(f"gap {gap:.9f}  2/phi^3 {2 / PHI**3:.9f}  rel miss {(2 / PHI**3 - gap) / gap:+.4%}")
    need = CODATA - BASE
    print(f"remainder after base {need:.9e}  (CODATA unc / remainder = {U_CODATA / need:.2e})")
    for name, v in (("ours  +alpha*3/59", OURS), ("Pellis +(3phi)^-5", PELLIS)):
        t = v - BASE
        print(f"  {name}: term {t:.9e} rel miss {(t - need) / need:+.2e} -> {v:.9f} "
              f"{ppb(v, CODATA):+.3f} ppb {(v - CODATA) / U_CODATA:+.2f} sigma")
    d1 = -math.log10(abs(GOLDEN_DEG - CODATA) / CODATA)
    d2 = -math.log10(abs(2 / PHI**3 - gap) / gap)
    d3 = -math.log10(abs((OURS - BASE) - need) / need)
    print(f"digits gained: stage1 {d1:.2f}  stage2 {d2:.2f}  stage3 {d3:.2f}")
    return gap, need


def look_elsewhere(gap, need):
    print("\n== look-elsewhere ==")
    tol2 = abs(2 / PHI**3 - gap)
    fam2 = [(b, k, b * PHI**k) for b in range(1, 13) for k in range(-6, 7)]
    hits2 = [(b, k) for b, k, v in fam2 if abs(v - gap) <= tol2]
    print(f"stage 2, b*phi^k (b=1..12, k=-6..6, {len(fam2)} forms): hits {hits2}")
    random.seed(1)
    rel2 = tol2 / gap
    vals2 = [v for _, _, v in fam2]
    trials, hit = 200000, 0
    for _ in range(trials):
        g = GOLDEN_DEG - random.uniform(130.0, 137.4)
        if any(abs(v - g) <= rel2 * g for v in vals2):
            hit += 1
    print(f"  matched null (target ~ U[130,137.4], same anchor/family/tolerance): P(hit) = {hit / trials:.4f}")

    tol3 = 1.05 * abs(OURS - CODATA)   # the precision our closure achieves, with float slack
    for q_max in (100, 200):
        hits = [f"{p}/{q}" for q in range(1, q_max + 1) for p in range(1, q)
                if Fraction(p, q).denominator == q and abs(ALPHA * p / q - need) <= tol3]
        local = sum(1 for q in range(1, q_max + 1) for p in range(1, q)
                    if Fraction(p, q).denominator == q and abs(p / q - 3 / 59) < 0.01)
        print(f"stage 3, alpha*p/q (q<={q_max}): hits {hits}, expected by local density "
              f"{local * (2 * tol3 / ALPHA) / 0.02:.3f}")
    fam3 = [(c, a, k, c * (a * PHI) ** -k) for c in range(1, 7) for a in range(1, 7) for k in range(1, 9)]
    hits3 = [(c, a, k) for c, a, k, v in fam3 if abs(v - need) <= tol3]
    local3 = sum(1 for *_, v in fam3 if need / 2 <= v <= need * 2)
    print(f"stage 3, c*(a*phi)^-k (c,a=1..6, k=1..8, {len(fam3)} forms): hits {hits3}, "
          f"expected by local density {local3 * 2 * tol3 / (1.5 * need):.3f}")


def measurements():
    print("\n== against the direct measurements ==")
    (cs, ucs), (rb, urb) = CS_2018, RB_2020
    print(f"Rb 2020 - Cs 2018 = {(rb - cs) * 1e9:.0f}e-9 ({ppb(rb, cs):.2f} ppb, "
          f"{(rb - cs) / math.hypot(ucs, urb):.1f} sigma combined)")
    print(f"ours - Pellis = {(OURS - PELLIS) * 1e9:+.1f}e-9 ({ppb(OURS, PELLIS):+.3f} ppb)")
    for name, v in (("ours", OURS), ("Pellis", PELLIS)):
        print(f"  {name}: vs Cs {ppb(v, cs):+.2f} ppb ({(v - cs) / ucs:+.1f} sigma); "
              f"vs Rb {ppb(v, rb):+.2f} ppb ({(v - rb) / urb:+.1f} sigma)")


def continued_fraction(x, n):
    out = []
    for _ in range(n):
        a = int(x)
        out.append(a)
        x -= a
        if x < 1e-12:
            break
        x = 1 / x
    return out


def convergents(cf):
    h0, h1, k0, k1 = 0, 1, 1, 0
    out = []
    for a in cf:
        h0, h1 = h1, a * h1 + h0
        k0, k1 = k1, a * k1 + k0
        out.append((h1, k1))
    return out


def phyllotaxis():
    print("\n== phyllotaxis (divergence as a fraction of a turn) ==")
    for name, deg in (("golden", GOLDEN_DEG), ("alpha ", CODATA)):
        d = deg / 360
        cf = continued_fraction(d, 10)
        conv = convergents(cf)
        print(f"{name} {deg:.4f} deg  d={d:.9f}  cf={cf}")
        print(f"   convergents {[f'{p}/{q}' for p, q in conv]}")
    d = CODATA / 360
    step = (21 * d - 8) * 360
    print(f"alpha angle: seeds n and n+21 differ by {step:+.2f} deg (21-arm drift per step)")
    print(f"   intermediate fractions 8/21 -> 59/155: {[f'{3 + j * 8}/{8 + j * 21}' for j in range(1, 8)]}")


def figure(path, seeds=1000):
    w, h, radius = 760, 440, 168
    c = radius / math.sqrt(seeds)
    panels = (
        (190, "Golden angle 137.508°", "fills evenly; spirals 13, 21, 34, 55, 89", GOLDEN_DEG),
        (570, "α angle 137.036° (1/α in degrees)", "locks into 21 curving arms with empty lanes", CODATA),
    )
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
           'font-family="Georgia, serif" role="img">',
           f'<title>Sunflower seed placement at the golden angle and at 1/alpha degrees ({seeds} seeds each)</title>']
    for cx, top, bottom, deg in panels:
        cy = 215
        out.append(f'<text x="{cx}" y="24" text-anchor="middle" font-size="15" fill="#8A8272">{top}</text>')
        for n in range(1, seeds + 1):
            r = c * math.sqrt(n)
            t = math.radians(n * deg)
            out.append(f'<circle cx="{cx + r * math.cos(t):.2f}" cy="{cy + r * math.sin(t):.2f}" r="2.1" fill="#B8A060"/>')
        out.append(f'<text x="{cx}" y="{h - 12}" text-anchor="middle" font-size="13" fill="#8A8272">{bottom}</text>')
    out.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"\nfigure written: {path}")


if __name__ == "__main__":
    g, r = stages()
    look_elsewhere(g, r)
    measurements()
    phyllotaxis()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    figure(os.path.join(root, "plans", "alpha_resonance_phyllotaxis_2026_10_22.svg"))
