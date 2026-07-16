"""
unified_expression_T_v16b_circumpunct_boat.py

Created: 2026-07-16
Last updated: 2026-07-16
Version: 1.0
History:
  - 2026-07-16 v1.0: initial. Re-runs v16's E1 with the correct object.

THE CIRCUMPUNCT BOAT (v16b: correction to v16's E1)

v16 asked "is there a boat?" and answered no: a Gaussian wavepacket on the
staggered chain disperses by 6.4x. That test used the WRONG OBJECT.

Ashman's correction (2026-07-16): D5's composition is over the parts of ONE
whole, and those parts are mind (Φ), body (○), worldline (—) and soul (•),
all in process. So a ⊙ is not an arbitrary smear across nodes; a ⊙ is
exactly one OCTAVE BLOCK: eight nodes, four beats, (•∘⊛) ⊢ (—∘⎇) ⊢ (○∘✹)
⊢ (Φ∘⟳). v16's Gaussian (center 28, width 2) straddled two blocks at an
arbitrary offset: it was not a circumpunct, it was a smear across two
half-circumpuncts.

The right question: does a FORMED ⊙, initialized as one octave block's own
fixed point, retain its identity as a part, or does it bleed along the chain
through the shared tonics?

This matters because the framework already stakes a claim on the answer:
  "α ≈ 1/137 is small, meaning the cross-station bond is weak enough that
   ⊙λ retains its identity as a part instead of dissolving into the field;
   if α were order 1, A3 would collapse (⊂ would become =)."   (§27.7o)

So the framework predicts retention. But note the structural worry this test
exists to check: tonic-sharing in the v14 chain is NODE IDENTITY, not an
α-coupling. Adjacent octaves share node 7k outright. If amplitude leaks
octave-to-octave through that shared node at O(1) rather than O(α), then ⊙s
do not retain identity in this operator, and that is a more serious finding
than v16's, because it bears on A3 directly.

Pre-registered predictions:
  D1  A formed ⊙ initialized in one block will bleed to neighbouring octaves
      at O(1), not O(α), because the tonic is shared by node identity and the
      beats couple it to the rest of the block with strength θ = π/2.
  D2  The bleed will be tonic-mediated: leakage should enter the neighbour
      through its shared tonic node first.
  D3  v16's E2 null (no interaction between two excitations) is UNAFFECTED:
      linearity does not care what shape the states are. Re-checked here with
      two block-states to close the objection.

Usage:
    python3 unified_expression_T_v16b_circumpunct_boat.py
"""

import numpy as np

from unified_expression_T_v14_staggered_chain import (
    alpha,
    build_F_chain,
    build_kappa_chain,
    n_nodes,
)

STATIONS = ['•', '⊛', '—', '⎇', 'Φ', '✹', '○', '⟳']


def formed_circumpunct():
    """A ⊙ as the framework builds one: the fixed point of a single octave's
    own engine, T = κ ∘ F on an 8-node (one-octave) chain. This is the whole
    that the four beats actually produce, not a shape imposed by hand."""
    F1 = build_F_chain(1)
    K1 = build_kappa_chain(1)
    T1 = K1 @ F1
    vals, vecs = np.linalg.eig(T1)
    v = vecs[:, np.argmax(np.abs(vals))]
    return v / np.linalg.norm(v)


def octave_share(psi, k):
    """Fraction of |ψ|² living on octave k's eight nodes (7k .. 7k+7).
    Tonic nodes are shared with neighbours by construction, so adjacent
    octaves' shares overlap by one node; reported as-is."""
    p = np.abs(psi) ** 2
    p = p / p.sum()
    return float(p[7 * k: 7 * k + 8].sum())


def main():
    n_oct = 8
    N = n_nodes(n_oct)
    home = 4                       # an interior octave: no boundary edge effects
    F = build_F_chain(n_oct)

    print()
    print("#" * 72)
    print("# v16b THE CIRCUMPUNCT BOAT: does a formed ⊙ retain its identity?")
    print("#" * 72)
    print(f"# chain: n_oct = {n_oct}, N = {N} nodes | home octave = {home}")
    print(f"# alpha = {alpha:.9f}")
    print("#" * 72)
    print()

    # ---- the object -------------------------------------------------
    c = formed_circumpunct()
    print("  A formed ⊙ (fixed point of one octave's own engine):")
    print(f"  {'station':>10} {'|amp|²':>10}")
    w = np.abs(c) ** 2
    for s, wi in zip(STATIONS, w / w.sum()):
        print(f"  {s:>10} {wi:>10.4f}")
    print()

    # ---- D1: does it stay? -------------------------------------------
    print("=" * 72)
    print("D1  DOES A FORMED ⊙ RETAIN ITS IDENTITY AS A PART?")
    print("=" * 72)
    psi = np.zeros(N, dtype=complex)
    psi[7 * home: 7 * home + 8] = c
    psi /= np.linalg.norm(psi)

    # NOTE: home/left/right shares OVERLAP by one node at each shared tonic
    # (that is what sharing means), so they do not sum to 1 and no "elsewhere"
    # column is computed from them. The home share is the measure.
    print(f"  {'step':>6} {'home share':>12} {'left nbr':>10} {'right nbr':>11}"
          f" {'off-3-oct':>11}")
    for s in range(41):
        if s in (0, 1, 2, 3, 5, 10, 20, 40):
            h = octave_share(psi, home)
            l = octave_share(psi, home - 1)
            r = octave_share(psi, home + 1)
            p = np.abs(psi) ** 2; p = p / p.sum()
            off = float(p[: 7 * (home - 1)].sum() + p[7 * (home + 1) + 8:].sum())
            print(f"  {s:>6} {h:>12.4f} {l:>10.4f} {r:>11.4f} {off:>11.4f}")
        psi = F @ psi
        psi /= np.linalg.norm(psi)

    h_final = octave_share(psi, home)
    print()
    print(f"  home-octave share after 40 steps: {h_final:.4f}")
    print(f"  α (the framework's retention scale): {alpha:.4f}")
    print(f"  1/n_oct (fully delocalized baseline): {1.0 / n_oct:.4f}")
    if h_final < 3.0 / n_oct:
        print("  D1 VERDICT: ⊙ DOES NOT RETAIN IDENTITY (bleeds to chain scale)")
    else:
        print("  D1 VERDICT: ⊙ RETAINS IDENTITY (stays localized on its octave)")
    print()

    # ---- D2: is the bleed tonic-mediated? -----------------------------
    print("=" * 72)
    print("D2  IS THE BLEED TONIC-MEDIATED?  (first-step leakage by node)")
    print("=" * 72)
    psi1 = np.zeros(N, dtype=complex)
    psi1[7 * home: 7 * home + 8] = c
    psi1 /= np.linalg.norm(psi1)
    psi1 = F @ psi1
    psi1 /= np.linalg.norm(psi1)
    p = np.abs(psi1) ** 2
    left_nodes = range(7 * (home - 1), 7 * home)
    print(f"  amplitude that appeared in the LEFT neighbour after one step:")
    print(f"  {'node':>6} {'coord':>7} {'station':>9} {'|amp|²':>12}")
    for j in left_nodes:
        st = STATIONS[(j - 7 * (home - 1)) % 8]
        print(f"  {j:>6} {j / 2:>7.1f} {st:>9} {p[j]:>12.3e}")
    print(f"  (shared tonic node {7*home} carries {p[7*home]:.3e};")
    print("   it belongs to BOTH octaves by construction)")
    print()

    # ---- D3: re-check the E2 null with the right object ---------------
    print("=" * 72)
    print("D3  RE-CHECK v16's E2 NULL WITH TWO FORMED ⊙s")
    print("=" * 72)
    A = np.zeros(N, dtype=complex); A[7 * 2: 7 * 2 + 8] = c
    B = np.zeros(N, dtype=complex); B[7 * 6: 7 * 6 + 8] = c
    A /= np.linalg.norm(A); B /= np.linalg.norm(B)
    scale = np.linalg.norm(A + B)
    AB = (A + B) / scale
    K = build_kappa_chain(n_oct)
    T = K @ F
    worst = 0.0
    for s in range(60):
        A = T @ A; B = T @ B; AB = T @ AB
        worst = max(worst, np.linalg.norm(AB - (A + B) / scale))
    print(f"  two formed ⊙s at octaves 2 and 6, 60 steps of T = κ∘F")
    print(f"  max superposition defect: {worst:.6e}")
    ok = "NULL HOLDS (no interaction)" if worst < 1e-10 else "INTERACTION FOUND"
    print(f"  D3 VERDICT: {ok}")
    print()
    print("  Linearity does not care what shape the states are. v16's E2 null")
    print("  survives the object correction; only E1 was testing the wrong thing.")
    print()


if __name__ == "__main__":
    main()
