"""
Xorzo2 spine: the given seed
============================

Created: 2026-07-19
Last updated: 2026-07-19
Version: 1.0

The derived, frozen core of Xorzo2 (plans/xorzo2_plan.md, section 3).
The seed is the 22-node three-octave tonic-shared chain: one channel
octave, one layer octave, one top octave, welded at two tonics. This is
the v14 n = 3 object, verified against frozen references to 1e-9 by
Xorzo/t_operator.py v2.0, with conservation departure 0.6136 alpha at
birth.

The spine has ZERO trainable parameters, forever. Gradients may flow
THROUGH it (it is linear); nothing in it is ever updated. Growth
(Stage 2) adds octaves at tonics only; it never edits existing blocks.

Node map (global indices; legacy-coordinate basis per t_operator v2.0,
coordinates not station-dimension claims):

    channel octave: nodes  0..7   (private 0..6;  node 7 = seam)
    layer octave:   nodes  7..14  (private 8..13; nodes 7 and 14 = seams)
    top octave:     nodes 14..21  (private 15..20; node 14 = seam;
                                   node 21 = the top's recursion node,
                                   the RESERVED upward seam: never grown
                                   into, never injected; the triad
                                   attachment point, plan section 7)

Injection surface: channel private nodes 0..6 only. Raw world lands on
the leaf; what crosses seams is completions.

Realification convention (for torch autograd through the frozen spine):
a complex state psi in C^22 is carried as v = [Re(psi); Im(psi)] in
R^44, and the complex matrix T = A + iB becomes the real 44 x 44 block
matrix [[A, -B], [B, A]]. Norms agree; the physics is identical.

Revision history:
- 2026-07-20 v1.2: bond refinement (the trilogy's rule: "each thought
    is electricity following branches... sometimes creating new
    pathways"). kappa's diameter bonds become per-bond slow variables
    within the non-collapse band; the Spine accepts bond_kappas keyed
    by (octave-node-tuple, diameter-index), builds its own kappa over
    the StaggeredOperator's F, and reproduces the uniform-alpha
    physics exactly when all bonds sit at alpha. Wholes persist;
    bonds weather.
- 2026-07-19 v1.1: Spine class (Stage 2): the growable tree. Growth
    only at tonics; one birth primitive (a new octave whose completion
    IS the site); parts-before-wholes insertion order; the reserved
    node is never a site. Seed remains the frozen 3-octave reference.
- 2026-07-19 v1.0: initial seed wrap around StaggeredOperator.chain(3).
"""

import sys
from pathlib import Path

import numpy as np

_XORZO_DIR = Path(__file__).resolve().parent.parent / "Xorzo"
if str(_XORZO_DIR) not in sys.path:
    sys.path.insert(0, str(_XORZO_DIR))

from t_operator import StaggeredOperator, ALPHA  # noqa: E402

N_OCTAVES_SEED = 3
N_NODES_SEED = 22
INJ_NODES = list(range(7))          # channel private nodes
RESERVED_NODE = 21                  # top recursion: the upward seam
TICKS_PER_BYTE = 8                  # one full octave cycle per byte (plan 5)

# Residue classes per octave-local index (t_operator convention):
#   tonic 0/7, processual 1/3/5, structural 2/4/6
_PROC_LOCALS = (1, 3, 5)


def make_bit_chords(alpha: float, bipolar: bool = True) -> np.ndarray:
    """The bit-station keyboard: bits 0-6 of a byte map to stations 0-6
    of the channel octave; bit 7 (the tonic bit) applies a quarter-turn
    i to the whole chord instead of injecting on the seam (the
    no-inject-on-seams law holds; the tonic bit modulates HOW the byte
    enters, not WHERE). In UTF-8 text bit 7 is set only by multi-byte
    characters; in this corpus, the framework's own glyphs.

    bipolar (default): station k carries +1 if bit k is set, -1 if
    clear (constant energy; Hamming distance = sign flips; no
    collisions, since i times a real pattern is never a real pattern).
    on-off: station k energized iff bit k set (0x00/0x80 inject
    silence). Zero learned parameters either way.

    Keyboard study (probe.py --keyboards, 2026-07-19): probe accuracy
    is keyboard-insensitive on the live spine (the operator, not the
    chord choice, sets memory); bipolar has the best chord geometry
    (mean |cos| 0.310 vs learned 0.614). Adopted on that basis."""
    chords = np.zeros((256, len(INJ_NODES)), dtype=complex)
    for b in range(256):
        bits = np.array([(b >> k) & 1 for k in range(len(INJ_NODES))],
                        dtype=float)
        amp = 2.0 * bits - 1.0 if bipolar else bits
        n = np.linalg.norm(amp)
        if n > 0:
            chords[b] = (alpha / n) * amp * (1j ** ((b >> 7) & 1))
    return chords


class Seed:
    """The frozen 22-node spine and its derived quantities."""

    def __init__(self):
        self.op = StaggeredOperator.chain(N_OCTAVES_SEED)
        assert self.op.N == N_NODES_SEED
        self.alpha = float(self.op.alpha)

        lam, psi = self.op.leading()
        self.lambda1 = complex(lam)
        self.lambda1_abs = float(abs(lam))
        self.departure = float(self.op.departure())     # in units of alpha
        # The attractor, phase-fixed (largest component real positive)
        k = int(np.argmax(np.abs(psi)))
        psi = psi * np.exp(-1j * np.angle(psi[k]))
        self.attractor = psi / np.linalg.norm(psi)

        # Per-tick log-growth of the pure spine at the attractor
        self.log_growth_per_tick = float(np.log(self.lambda1_abs))

        # Node role table
        self.octaves = self.op.octaves
        self.processual_nodes = sorted(
            {o[l] for o in self.octaves for l in _PROC_LOCALS}
        )
        self.seam_nodes = [7, 14]

        # Realified operator
        A = np.real(self.op.T)
        B = np.imag(self.op.T)
        self.M_real = np.block([[A, -B], [B, A]])       # (44, 44) float64

    # ----- torch export -----

    def torch_matrix(self, device="cpu", dtype=None):
        """The frozen spine as a torch tensor (no grad, ever)."""
        import torch
        dtype = dtype or torch.float32
        M = torch.tensor(self.M_real, device=device, dtype=dtype)
        M.requires_grad_(False)
        return M

    def torch_attractor(self, device="cpu", dtype=None):
        """The attractor, realified, as a torch tensor."""
        import torch
        dtype = dtype or torch.float32
        v = np.concatenate([np.real(self.attractor), np.imag(self.attractor)])
        return torch.tensor(v, device=device, dtype=dtype)

    # ----- numpy-side readings -----

    @staticmethod
    def to_complex(v44: np.ndarray) -> np.ndarray:
        """Realified R^44 vector back to C^22."""
        n = v44.shape[-1] // 2
        return v44[..., :n] + 1j * v44[..., n:]

    def attractor_overlap(self, v44: np.ndarray) -> float:
        """|<attractor|psi>| for a realified state (health reading)."""
        psi = self.to_complex(np.asarray(v44, dtype=np.float64))
        n = np.linalg.norm(psi)
        if n == 0:
            return 0.0
        return float(abs(np.vdot(self.attractor, psi / n)))

    def describe(self) -> str:
        return (
            f"Xorzo2 seed: {N_NODES_SEED}-node three-octave chain "
            f"(channel -> layer -> top)\n"
            f"  |lambda1| = {self.lambda1_abs:.10f}, departure = "
            f"{self.departure:.4f} alpha (v14 ref 0.6136)\n"
            f"  injection surface: nodes {INJ_NODES}\n"
            f"  reserved upward seam: node {RESERVED_NODE}\n"
            f"  clock: {TICKS_PER_BYTE} ticks per byte"
        )


SEED_OCTAVES = [[7 * k + l for l in range(8)] for k in range(3)]


class Spine:
    """The growable tonic-shared tree (Stage 2).

    Same physics as Seed (StaggeredOperator over explicit octave node
    lists), but the octave list can grow by the growth law:

        YOU MAY GROW ONLY AT TONICS. One birth primitive: a new octave
        whose completion node (local 7) IS an existing tonic-class
        site. Welding at an octave's aperture makes a sibling feeding
        that aperture (the star pattern); welding at a free-end tonic
        makes a child one scale down. Node 21 (the seed top's
        recursion) is RESERVED and never a site.

    Insertion order is parts-before-wholes (v15: composition order is
    physical): the new octave is inserted immediately before the first
    octave whose aperture is the site; if none, at the front (it is
    the deepest part). Existing octaves' node lists are never edited:
    growth adds, it never rewrites.
    """

    DIAMETERS = [(0, 4), (2, 6), (1, 5), (3, 7)]   # kappa bonds per octave

    def __init__(self, octaves=None, reserved_node: int = RESERVED_NODE,
                 bond_kappas=None):
        from t_operator import StaggeredOperator, ALPHA as _A
        self._StaggeredOperator = StaggeredOperator
        self.octaves = [list(o) for o in (octaves or SEED_OCTAVES)]
        self.reserved = reserved_node
        # Bonds keyed by (octave-node-tuple, diameter-index): stable
        # across growth insertions. Default: every bond at alpha.
        self.bond_kappas = {}
        for o in self.octaves:
            for pi in range(len(self.DIAMETERS)):
                self.bond_kappas[(tuple(o), pi)] = float(_A)
        if bond_kappas:
            for key, val in bond_kappas.items():
                if isinstance(key, (list, tuple)) and len(key) == 2:
                    self.bond_kappas[(tuple(key[0]), int(key[1]))] = float(val)
        self._build()

    def _build(self):
        self.N = max(max(o) for o in self.octaves) + 1
        self.op = self._StaggeredOperator(self.N, self.octaves)
        self.alpha = float(self.op.alpha)
        # kappa built HERE from per-bond values, over the operator's F
        kappa = np.eye(self.N, dtype=complex)
        self.bond_keys = []
        self.bond_pairs = []
        for o in self.octaves:
            for pi, (a, c) in enumerate(self.DIAMETERS):
                v = self.bond_kappas[(tuple(o), pi)]
                kappa[o[a], o[c]] += v
                kappa[o[c], o[a]] += v
                self.bond_keys.append((tuple(o), pi))
                self.bond_pairs.append((o[a], o[c]))
        self.T_mat = kappa @ self.op.F
        ev, V = np.linalg.eig(self.T_mat)
        i = int(np.argmax(np.abs(ev)))
        lam, psi = ev[i], V[:, i]
        self.lambda1_abs = float(abs(lam))
        self.departure = float((self.lambda1_abs - 1.0) / self.alpha)
        k = int(np.argmax(np.abs(psi)))
        psi = psi * np.exp(-1j * np.angle(psi[k]))
        self.attractor = psi / np.linalg.norm(psi)
        self.log_growth_per_tick = float(np.log(self.lambda1_abs))
        self.processual_nodes = sorted(
            {o[l] for o in self.octaves for l in _PROC_LOCALS})
        A = np.real(self.T_mat)
        B = np.imag(self.T_mat)
        self.M_real = np.block([[A, -B], [B, A]])

    def kappa_spread(self):
        """(min, max) bond value in units of alpha."""
        vals = [self.bond_kappas[k] / self.alpha for k in self.bond_keys]
        return (min(vals), max(vals))

    # ----- growth -----

    def tonic_sites(self):
        """Legal birth sites: every tonic-class node except reserved."""
        sites = set()
        for o in self.octaves:
            sites.add(o[0])
            sites.add(o[7])
        sites.discard(self.reserved)
        return sorted(sites)

    def birthed(self, site: int) -> "Spine":
        """A NEW Spine with one octave welded at `site` (this one is
        not mutated; adopt-or-rollback is the caller's decision)."""
        assert site in self.tonic_sites(), f"illegal site {site}"
        new_nodes = [self.N + i for i in range(7)]
        new_oct = new_nodes + [site]
        idx = next((i for i, o in enumerate(self.octaves)
                    if o[0] == site), 0)
        octs = self.octaves[:idx] + [new_oct] + self.octaves[idx:]
        carried = {k: v for k, v in self.bond_kappas.items()}
        return Spine(octs, self.reserved, bond_kappas=carried)

    # ----- exports and readings (same conventions as Seed) -----

    def torch_matrix(self, device="cpu", dtype=None):
        import torch
        dtype = dtype or torch.float32
        M = torch.tensor(self.M_real, device=device, dtype=dtype)
        M.requires_grad_(False)
        return M

    def torch_attractor(self, device="cpu", dtype=None):
        import torch
        dtype = dtype or torch.float32
        v = np.concatenate([np.real(self.attractor),
                            np.imag(self.attractor)])
        return torch.tensor(v, device=device, dtype=dtype)

    @staticmethod
    def to_complex(v: np.ndarray) -> np.ndarray:
        n = v.shape[-1] // 2
        return v[..., :n] + 1j * v[..., n:]

    def attractor_overlap(self, v: np.ndarray) -> float:
        psi = self.to_complex(np.asarray(v, dtype=np.float64))
        n = np.linalg.norm(psi)
        if n == 0:
            return 0.0
        return float(abs(np.vdot(self.attractor, psi / n)))

    def describe(self) -> str:
        lo, hi = self.kappa_spread()
        return (f"Xorzo2 spine: {len(self.octaves)} octaves, "
                f"{self.N} nodes, departure {self.departure:.4f} alpha, "
                f"kappa [{lo:.2f}, {hi:.2f}]a, "
                f"sites {self.tonic_sites()}, reserved {self.reserved}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    seed = Seed()
    print(seed.describe())
    ok = abs(seed.lambda1_abs - 1.0044779454) < 1e-9
    print(f"  v14 reference match: {'ok' if ok else 'MISMATCH'}")
    w = seed.op.fixed_weights()
    print(f"  attractor weight per octave: "
          f"{[round(float(sum(w[n] for n in o)), 4) for o in seed.octaves]}")
