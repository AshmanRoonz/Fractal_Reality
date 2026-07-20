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
