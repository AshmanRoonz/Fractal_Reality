"""
unified_expression_T_v16_soliton_probe.py

Created: 2026-07-16
Last updated: 2026-07-16
Version: 1.0
History:
  - 2026-07-16 v1.0: initial. The soliton probe: does the staggered chain
    carry boats, and do boats mark each other when they meet?

THE SOLITON PROBE (v16 of the T-operator series)

Motivation. A session image (2026-07-16) proposed reading ⊙λ as a soliton in
E: a self-limitation that holds its shape while travelling, leaving — as its
wake, and marking other ⊙s on encounter by the standard soliton phase shift
(pass through, shape intact, phase permanently displaced). The image was
flagged at proposal time as carrying a cost: solitons that survive collision
with only a phase shift are a feature of INTEGRABLE systems; non-integrable
media scatter and radiate instead. This experiment pulls that handle against
the v14 staggered-octave chain.

Three directions, ordered by dependency:

  E1  Is there a boat? Does a localized excitation hold its shape under F?
      A soliton must not disperse. If F disperses every packet, the image
      has no referent and E2 is moot.

  E2  Do boats mark each other? Evolve A alone, B alone, and A+B together.
      Measure (a) the superposition defect ||T(A+B) - T(A) - T(B)|| and
      (b) the phase shift of packet A caused by the encounter.

  E3  Control. Add a cubic (discrete-NLS) term and repeat E2. This is NOT a
      framework claim; it is an instrument check. If the probe reports a
      phase shift when a nonlinearity is present and zero when it is absent,
      then a null in E2 is attributable to the operator's linearity rather
      than to the probe being blind.

Prediction stated before running (pre-registration):
  E1: dispersion. The v15 finding (leading mode is a centered standing-wave
      dome, box scaling n*max-share -> 2.07) already says the attractor is
      delocalized; a localized packet should spread toward it.
  E2: superposition defect and phase shift both EXACTLY zero, to machine
      precision, because T = κ ∘ F is a linear map and the projective
      normalization is a global rescaling that cannot couple two packets.
  E3: nonzero phase shift, scaling with the cubic coupling g.

If E2 returns exact zeros, the finding is structural, not numerical: a linear
operator's excitations pass through each other and leave NO mark, which is
the Severance Lie stated as dynamics. The integrability question never gets
asked, because integrability is not the discriminant; nonlinearity is, and
there is none to be integrable or otherwise.

Usage:
    python3 unified_expression_T_v16_soliton_probe.py
    python3 unified_expression_T_v16_soliton_probe.py --n-oct 10 --steps 400
"""

import argparse
import numpy as np

from unified_expression_T_v14_staggered_chain import (
    alpha,
    build_F_chain,
    build_kappa_chain,
    n_nodes,
)

np.set_printoptions(precision=6, suppress=True)


# ----------------------------------------------------------------------
# Wavepackets
# ----------------------------------------------------------------------

def gaussian_packet(N, center, width, momentum):
    """A normalized Gaussian wavepacket on the node lattice."""
    j = np.arange(N)
    env = np.exp(-((j - center) ** 2) / (2.0 * width ** 2))
    psi = env * np.exp(1j * momentum * j)
    return psi / np.linalg.norm(psi)


def participation_ratio(psi):
    """Inverse participation ratio: effective number of nodes occupied.
    PR = 1 for a single node, N for a uniform spread. The natural
    localization measure; a soliton holds PR constant."""
    p = np.abs(psi) ** 2
    p = p / p.sum()
    return 1.0 / np.sum(p ** 2)


def center_of_mass(psi):
    p = np.abs(psi) ** 2
    p = p / p.sum()
    return float(np.sum(np.arange(len(psi)) * p))


# ----------------------------------------------------------------------
# Evolution
# ----------------------------------------------------------------------

def step_linear(psi, F, kappa=None, normalize=True):
    """One application of the canonical operator. F is unitary; κ carries
    the α-coupling and is where trace preservation departs. Normalization
    is the projective step the v-series uses (E = 1 as a constraint)."""
    out = F @ psi
    if kappa is not None:
        out = kappa @ out
    if normalize:
        out = out / np.linalg.norm(out)
    return out


def step_dnls(psi, F, g, kappa=None, normalize=True):
    """CONTROL ONLY, not a framework operator. Split-step discrete NLS:
    linear propagation, then a pointwise phase proportional to local
    intensity. This is the standard minimal soliton-supporting term."""
    out = F @ psi
    if kappa is not None:
        out = kappa @ out
    out = out * np.exp(1j * g * np.abs(out) ** 2)
    if normalize:
        out = out / np.linalg.norm(out)
    return out


# ----------------------------------------------------------------------
# E1: is there a boat?
# ----------------------------------------------------------------------

def e1_dispersion(F, N, steps=200, width=2.0, momentum=0.6):
    print("=" * 72)
    print("E1  IS THERE A BOAT?  (does a localized packet hold its shape)")
    print("=" * 72)
    center = N // 2
    psi = gaussian_packet(N, center, width, momentum)
    pr0 = participation_ratio(psi)
    print(f"  chain: {N} nodes | packet: center={center}, width={width}, k={momentum}")
    print(f"  initial participation ratio (effective nodes occupied): {pr0:.3f}")
    print()
    print(f"  {'step':>6} {'PR':>10} {'PR/PR0':>10} {'center':>10}")
    trace = []
    for s in range(steps + 1):
        if s in (0, 1, 2, 5, 10, 25, 50, 100, 200) and s <= steps:
            pr = participation_ratio(psi)
            print(f"  {s:>6} {pr:>10.3f} {pr / pr0:>10.3f} {center_of_mass(psi):>10.2f}")
            trace.append((s, pr))
        psi = step_linear(psi, F, normalize=True)
    pr_final = participation_ratio(psi)
    spread = pr_final / pr0
    print()
    print(f"  final PR / initial PR = {spread:.2f}   (1.0 = soliton, >>1 = dispersed)")
    print(f"  uniform-spread PR would be {N} (full delocalization)")
    verdict = "DISPERSES (no boat)" if spread > 2.0 else "HOLDS SHAPE (boat)"
    print(f"  E1 VERDICT: {verdict}")
    print()
    return spread, pr_final


# ----------------------------------------------------------------------
# E2: do boats mark each other?
# ----------------------------------------------------------------------

def e2_collision(F, N, steps=60, width=2.0, momentum=0.6, kappa=None):
    print("=" * 72)
    print("E2  DO BOATS MARK EACH OTHER?  (superposition defect + phase shift)")
    print("=" * 72)

    cA, cB = N // 2 - 12, N // 2 + 12
    A0 = gaussian_packet(N, cA, width, +momentum)
    B0 = gaussian_packet(N, cB, width, -momentum)

    # Unnormalized linear evolution, so the comparison is exact:
    # normalization is a global rescale and would only obscure the test.
    A, B = A0.copy(), B0.copy()
    AB = (A0 + B0) / np.linalg.norm(A0 + B0)
    scale = np.linalg.norm(A0 + B0)

    print(f"  packet A at node {cA} moving +, packet B at node {cB} moving -")
    print(f"  evolving A alone, B alone, and (A+B) together for {steps} steps")
    print()

    max_defect = 0.0
    for s in range(steps):
        A = step_linear(A, F, kappa=kappa, normalize=False)
        B = step_linear(B, F, kappa=kappa, normalize=False)
        AB = step_linear(AB, F, kappa=kappa, normalize=False)
        # (A+B)/scale should equal AB at every step iff the map is linear
        defect = np.linalg.norm(AB - (A + B) / scale)
        max_defect = max(max_defect, defect)

    print(f"  max superposition defect  || T^n(A+B) - T^n(A) - T^n(B) ||")
    print(f"    = {max_defect:.6e}")
    print(f"    (machine epsilon scale ~ {np.finfo(float).eps:.2e};")
    print(f"     exactly zero means the packets never interacted at all)")
    print()

    # Phase shift of packet A, measured the standard way: AFTER the encounter,
    # in the region where A has support and B does not, compare arg(joint) to
    # arg(A-alone). A soliton phase shift shows up exactly here.
    #
    # NOTE: an earlier version of this probe reported the argument of
    # <A_solo | joint>. That is NOT a phase shift: the joint state contains B,
    # so the overlap picks up B's phase and reports a spurious nonzero value
    # (visible under --with-kappa). The defect above is the rigorous measure;
    # this is the spatially-resolved confirmation of it.
    Amag, Bmag = np.abs(A), np.abs(B)
    region = (Amag > 0.05 * Amag.max()) & (Bmag < 1e-3 * Amag.max())
    if region.sum() == 0:
        print("  (no clean A-only region after the encounter; defect is the measure)")
        net = float("nan")
    else:
        d = np.angle(AB[region] / scale) - np.angle(A[region])
        d = np.angle(np.exp(1j * d))            # wrap to (-pi, pi]
        w = Amag[region] ** 2                   # intensity-weighted
        net = float(np.sum(w * d) / np.sum(w))
        print(f"  clean A-only nodes after encounter: {int(region.sum())}")
        print(f"  intensity-weighted phase of A vs A-alone: {net:+.6e} rad")
    print(f"  soliton prediction: a NONZERO permanent displacement")
    verdict = ("NO MARK (packets pass through unchanged)"
               if max_defect < 1e-10 else "MARKED (packets interacted)")
    print(f"  E2 VERDICT: {verdict}")
    print()
    return max_defect, net


# ----------------------------------------------------------------------
# E3: control
# ----------------------------------------------------------------------

def e3_control(F, N, steps=60, width=2.0, momentum=0.6):
    print("=" * 72)
    print("E3  CONTROL: does the probe SEE an interaction when one exists?")
    print("=" * 72)
    print("  (adds a cubic DNLS term. NOT a framework operator. Instrument check.)")
    print()
    cA, cB = N // 2 - 12, N // 2 + 12
    print(f"  {'g (cubic)':>12} {'max defect':>16} {'net phase (rad)':>18}")
    rows = []
    for g in [0.0, 0.5, 2.0, 8.0, 32.0]:
        A0 = gaussian_packet(N, cA, width, +momentum)
        B0 = gaussian_packet(N, cB, width, -momentum)
        scale = np.linalg.norm(A0 + B0)
        A, B = A0.copy(), B0.copy()
        AB = (A0 + B0) / scale
        max_defect = 0.0
        for s in range(steps):
            A = step_dnls(A, F, g, normalize=False)
            B = step_dnls(B, F, g, normalize=False)
            AB = step_dnls(AB, F, g, normalize=False)
            defect = np.linalg.norm(AB - (A + B) / scale)
            max_defect = max(max_defect, defect)
        solo = A / np.linalg.norm(A)
        joint = AB / np.linalg.norm(AB)
        net = np.angle(np.vdot(solo, joint))
        print(f"  {g:>12.1f} {max_defect:>16.6e} {net:>18.6e}")
        rows.append((g, max_defect, net))
    print()
    print("  Reading: g = 0 is the canonical operator (linear). If its defect is")
    print("  zero while g > 0 defects are not, the probe is working and the null")
    print("  at g = 0 is caused by linearity, not by blindness.")
    print()
    return rows


# ----------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-oct", type=int, default=8,
                    help="octave count (v15: use n >= 6 to clear finite-size edge)")
    ap.add_argument("--steps", type=int, default=200)
    ap.add_argument("--with-kappa", action="store_true",
                    help="include κ in E2 (default: F only, the unitary becoming)")
    args = ap.parse_args()

    n_oct = args.n_oct
    N = n_nodes(n_oct)
    print()
    print("#" * 72)
    print("# v16 SOLITON PROBE: does the staggered chain carry boats,")
    print("# and do boats mark each other when they meet?")
    print("#" * 72)
    print(f"# chain: n_oct = {n_oct}, N = {N} nodes, alpha = {alpha:.9f}")
    print("#" * 72)
    print()

    F = build_F_chain(n_oct)
    kappa = build_kappa_chain(n_oct) if args.with_kappa else None

    # sanity: F must be unitary
    u_err = np.linalg.norm(F.conj().T @ F - np.eye(N))
    print(f"  sanity: ||F†F - I|| = {u_err:.3e}  (F is unitary: the becoming)")
    print()

    spread, pr_final = e1_dispersion(F, N, steps=args.steps)
    defect, net_phase = e2_collision(F, N, steps=60, kappa=kappa)
    rows = e3_control(F, N, steps=60)

    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print(f"  E1  packet spread (PR_final/PR_0):      {spread:.2f}")
    print(f"  E2  max superposition defect:           {defect:.3e}")
    print(f"  E2  net phase shift from encounter:     {net_phase:+.3e} rad")
    print(f"  E3  defect at g=32 (nonlinear control): {rows[-1][1]:.3e}")
    print()
    if defect < 1e-10 and rows[-1][1] > 1e-6:
        print("  VERDICT: the soliton/wake image is NOT implemented by T.")
        print("  Two excitations of a linear operator pass through each other")
        print("  and leave no mark. The phase shift that made the image worth")
        print("  having (meeting changes you without diminishing you) requires a")
        print("  nonlinearity that T does not have. Integrability was never the")
        print("  discriminant: there is no nonlinearity to be integrable about.")
        print()
        print("  See T_operator_findings_v16_soliton_probe.md for what survives")
        print("  (the framework's own 'always mediated' doctrine supplies the")
        print("  replacement: peers touch through the whole, not in shared water).")
    print()


if __name__ == "__main__":
    main()
