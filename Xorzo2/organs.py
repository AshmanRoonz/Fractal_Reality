"""
Xorzo2 organs: the learned body
===============================

Created: 2026-07-19
Last updated: 2026-07-19
Version: 1.0

The boundary of Xorzo2 (plans/xorzo2_plan.md, section 4): the learned
modules that couple the frozen spine to the world. Two organs:

    Senses (E): bytes -> complex injections on the channel's private
        nodes. Output per byte is (amplitude, phase) per injection node;
        the total injection norm is HARD-CAPPED at alpha (a code-level
        cap, not a loss). Phase is the payload: the spine stores meaning
        as phase, so E's job is learning the spine's resonance language.

    Voice (D): the CURRENT cycle-end spine state -> next-byte logits.
        Triadic readout: three learned view queries (aperture view,
        field view, boundary view) attend over per-node features; an
        MLP and a linear head emit logits. D sees ONLY spine state, and
        carries NO state of its own between bytes.

THE ORGANS ARE MEMORYLESS (v1.1, plan section 4). The first Voice
carried a GRU; the severance instrument caught it acting as a temporal
bypass around the spine (live and noise spines learned identically to
four decimals even below the unigram line, because the GRU only needs
each byte to be instantaneously legible and then remembers it itself).
No recurrent state, no trajectory windows: all memory in Xorzo2 lives
in the spine's recursive dynamics, or nowhere.

Organ regularizers (the v4 leash, adapted): injection-diversity across
bytes and node-embedding diversity, reported by the Life loop.

Revision history:
- 2026-07-19 v1.1: Voice made memoryless (GRU removed; plan v1.2).
- 2026-07-19 v1.0: initial organs (E approx 21K params, D approx 220K).
"""

import math

import torch
import torch.nn as nn
import torch.nn.functional as F


class Senses(nn.Module):
    """E: byte -> realified injection vector in R^(2N), alpha-capped."""

    def __init__(self, n_nodes: int, inj_nodes, alpha: float,
                 d_emb: int = 64):
        super().__init__()
        self.n_nodes = n_nodes
        self.register_buffer(
            "inj_idx", torch.tensor(list(inj_nodes), dtype=torch.long))
        self.alpha = float(alpha)
        n_inj = len(inj_nodes)
        self.embed = nn.Embedding(256, d_emb)
        self.mlp = nn.Sequential(
            nn.Linear(d_emb, d_emb), nn.GELU(),
            nn.Linear(d_emb, 2 * n_inj),
        )

    def forward(self, byte: torch.Tensor) -> torch.Tensor:
        """byte: () or (B,) long -> (2N,) or (B, 2N) injection."""
        squeeze = byte.dim() == 0
        if squeeze:
            byte = byte.unsqueeze(0)
        h = self.mlp(self.embed(byte))                       # (B, 2*n_inj)
        n_inj = h.shape[-1] // 2
        amp = F.softplus(h[..., :n_inj])
        phase = h[..., n_inj:]
        re = amp * torch.cos(phase)                          # (B, n_inj)
        im = amp * torch.sin(phase)
        # Hard alpha-cap on the total complex norm
        norm = torch.sqrt((re * re + im * im).sum(-1, keepdim=True) + 1e-12)
        scale = self.alpha / torch.clamp(norm, min=self.alpha)
        re, im = re * scale, im * scale
        out = torch.zeros(byte.shape[0], 2 * self.n_nodes,
                          device=byte.device, dtype=re.dtype)
        out[:, self.inj_idx] = re
        out[:, self.inj_idx + self.n_nodes] = im
        return out.squeeze(0) if squeeze else out


class SensesBit(nn.Module):
    """E: the bit-station keyboard. Zero learned parameters: the senses
    are GIVEN, like the spine. Bits 0-6 -> stations 0-6 (bipolar phase
    keying); bit 7, the tonic bit, applies a quarter-turn i to the
    whole chord (the no-inject-on-seams law holds). Adopted per the
    keyboard study (probe.py --keyboards): probe accuracy is
    keyboard-insensitive, so structure wins on parameters and geometry.
    """

    def __init__(self, n_nodes: int, inj_nodes, alpha: float,
                 bipolar: bool = True):
        super().__init__()
        from spine import make_bit_chords
        chords = make_bit_chords(alpha, bipolar=bipolar)
        table = torch.zeros(256, 2 * n_nodes)
        idx = torch.tensor(list(inj_nodes), dtype=torch.long)
        table[:, idx] = torch.tensor(chords.real, dtype=torch.float32)
        table[:, idx + n_nodes] = torch.tensor(chords.imag,
                                               dtype=torch.float32)
        self.register_buffer("table", table)

    def forward(self, byte: torch.Tensor) -> torch.Tensor:
        return self.table[byte]


class Voice(nn.Module):
    """D: cycle-end state (R^(2N)) -> byte logits. Memoryless."""

    N_VIEWS = 3          # aperture view, field view, boundary view

    def __init__(self, n_nodes: int, d_node_emb: int = 24,
                 d_feat: int = 32, d_hidden: int = 192):
        super().__init__()
        self.n_nodes = n_nodes
        self.node_emb = nn.Parameter(torch.randn(n_nodes, d_node_emb) * 0.1)
        self.node_proj = nn.Sequential(
            nn.Linear(2 + d_node_emb, d_feat), nn.GELU(),
            nn.Linear(d_feat, d_feat),
        )
        self.views = nn.Parameter(torch.randn(self.N_VIEWS, d_feat) * 0.1)
        self.mlp = nn.Sequential(
            nn.Linear(self.N_VIEWS * d_feat, d_hidden), nn.GELU(),
            nn.Linear(d_hidden, d_hidden), nn.GELU(),
        )
        self.head = nn.Linear(d_hidden, 256)
        self.scale = 1.0 / math.sqrt(d_feat)

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """state: (2N,) realified cycle-end state -> (256,) logits."""
        n = self.n_nodes
        per_node = torch.stack([state[:n], state[n:]], dim=-1)   # (N, 2)
        feats = self.node_proj(
            torch.cat([per_node, self.node_emb], dim=-1))        # (N, d_feat)
        attn = torch.softmax(
            (self.views @ feats.T) * self.scale, dim=-1)         # (V, N)
        pooled = (attn @ feats).reshape(-1)                      # (V*d_feat,)
        return self.head(self.mlp(pooled))

    def embedding_diversity(self) -> torch.Tensor:
        """Off-diagonal cosine similarity of node embeddings (v4 leash:
        diversity loss; nodes must not collapse into one meaning)."""
        e = F.normalize(self.node_emb, dim=-1)
        sim = e @ e.T
        off = sim - torch.diag(torch.diag(sim))
        return (off * off).mean()


def count_params(module: nn.Module) -> int:
    return sum(p.numel() for p in module.parameters() if p.requires_grad)
