"""
⊙ The Circumpunct Mamba v2
============================

v1 proved the concept: fractal compression instead of destructive forgetting.
v2 applies three more structural predictions from the dimensional ladder.

Upgrade 1: Hierarchical Worldlines (A2)
    Three nested worldlines at different compression depths, matching the
    framework's three-scale structure (past/present/future = parts/self/whole).
    Each level has its own absorption rate and compression exponent:

        d_fast:  recent, mild compression     (working memory)
        d_mid:   medium, deeper compression    (episodic memory)
        d_deep:  ancient, heaviest compression (identity/semantic)

    Overflow cascades downward: fast → mid → deep.
    Retrieval searches all three, weighted by resonance quality.

Upgrade 2: Adaptive Compression via ◐
    The compression exponent is no longer fixed at 2/3.
    ◐ tracks the ratio of convergent to emergent energy and
    self-regulates toward 0.5. The compression exponent becomes:

        exponent = (1 + ◐) / (2 + ◐)

    At balance (◐ = 0.5): exponent ≈ 0.6
    Over-convergence (◐ → 1): exponent → 0.667 (gentle, preserve detail)
    Over-emergence (◐ → 0): exponent → 0.5 (hard, prevent saturation)

    The worldline absorption rate is also ◐-modulated:
    fastest at balance, slows when imbalanced.

Upgrade 3: φ-Scaled State Partitioning
    The state dimensions are partitioned into two groups in golden ratio:
        group_1 ≈ N/φ   (slow forgetting, long horizon)
        group_2 ≈ N/φ²  (fast forgetting, reactive)

    A_init values are scaled so group_1 decays slowly and group_2 decays fast.
    Gives the SSM built-in multi-timescale structure within a single layer,
    zero extra parameters.

Author: Ashman Roonz & Claude
Date: April 2026
Derived from: Circumpunct Framework (Roonz, 2024) + Mamba (Gu & Dao, 2024)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Tuple, Optional


# ═══════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════════════════

PHI = (1 + math.sqrt(5)) / 2          # φ = 1.618...
BALANCE = 0.5                          # ◐; the singular balanced state


# ═══════════════════════════════════════════════════════════════════════
#  COMPLEX UTILITIES
# ═══════════════════════════════════════════════════════════════════════

def c_mag(z: torch.Tensor) -> torch.Tensor:
    """Magnitude of complex tensor stored as [..., 2]."""
    return torch.sqrt(z[..., 0]**2 + z[..., 1]**2 + 1e-8)


def c_phase(z: torch.Tensor) -> torch.Tensor:
    """Phase angle of complex tensor stored as [..., 2]."""
    return torch.atan2(z[..., 1], z[..., 0] + 1e-10)


def c_from_polar(mag: torch.Tensor, phase: torch.Tensor) -> torch.Tensor:
    """Construct complex tensor from magnitude and phase."""
    return torch.stack([mag * torch.cos(phase), mag * torch.sin(phase)], dim=-1)


def c_mul(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Multiply two complex tensors (stored as [..., 2])."""
    real = a[..., 0] * b[..., 0] - a[..., 1] * b[..., 1]
    imag = a[..., 0] * b[..., 1] + a[..., 1] * b[..., 0]
    return torch.stack([real, imag], dim=-1)


def c_conj(z: torch.Tensor) -> torch.Tensor:
    """Complex conjugate: (a + bi) → (a - bi)."""
    return torch.stack([z[..., 0], -z[..., 1]], dim=-1)


def c_scale(z: torch.Tensor, s: torch.Tensor) -> torch.Tensor:
    """Scale complex tensor by real scalar (broadcast-safe)."""
    if s.dim() < z.dim():
        s = s.unsqueeze(-1)
    return z * s


# ═══════════════════════════════════════════════════════════════════════
#  ⊛ FRACTAL COMPRESSION (with adaptive exponent)
# ═══════════════════════════════════════════════════════════════════════

class _FractalCompress(torch.autograd.Function):
    """
    Custom autograd for ⊛: |x|^exponent with stable gradients.
    Exponent is passed per-call (not fixed at 2/3).
    """
    @staticmethod
    def forward(ctx, mag, exponent):
        mag_safe = torch.clamp(mag, min=1e-8)
        compressed = mag_safe ** exponent
        ratio = compressed / (mag_safe + 1e-6)
        ctx.save_for_backward(ratio)
        return compressed

    @staticmethod
    def backward(ctx, grad_output):
        ratio, = ctx.saved_tensors
        return grad_output * torch.clamp(ratio, max=2.0), None  # no grad for exponent


def converge(z: torch.Tensor, exponent: float = 2.0 / 3.0) -> torch.Tensor:
    """
    ⊛: Fractal compression.
    Magnitude compressed by given exponent. Phase preserved exactly.
    """
    mag = c_mag(z)
    phase = c_phase(z)
    compressed_mag = _FractalCompress.apply(mag, exponent)
    return c_from_polar(compressed_mag, phase)


# ═══════════════════════════════════════════════════════════════════════
#  T: RESONANCE GATE
# ═══════════════════════════════════════════════════════════════════════

def resonance_gate(signal: torch.Tensor, memory: torch.Tensor) -> torch.Tensor:
    """
    T = cos²(Δφ/2)

    Phase matching between signal and memory.
    Perfect match (Δφ = 0): T = 1.  Orthogonal (Δφ = π): T = 0.
    """
    delta_phi = c_phase(signal) - c_phase(memory)
    return torch.cos(delta_phi / 2) ** 2


# ═══════════════════════════════════════════════════════════════════════
#  DNA INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════

def dna_init(state_size: int, batch_size: int, device: torch.device,
             magnitude: float = 0.01) -> torch.Tensor:
    """
    Initialize worldline with differentiated phase structure.
    A1: the 1 must self-limit into distinct states.
    """
    phases = torch.linspace(0, 2 * math.pi * (1 - 1 / state_size),
                            state_size, device=device)
    d = c_from_polar(
        torch.full((state_size,), magnitude, device=device),
        phases
    )
    return d.unsqueeze(0).expand(batch_size, -1, -1).clone()


# ═══════════════════════════════════════════════════════════════════════
#  φ-SCALED A INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════

def phi_scaled_A_init(state_size: int) -> torch.Tensor:
    """
    Initialize A with φ-proportioned groups.

    group_1 (≈ N/φ dims):  slow decay (low A values, long horizon)
    group_2 (≈ N/φ² dims): fast decay (high A values, reactive)

    The golden ratio sets the proportion between timescales.
    """
    n_slow = round(state_size / PHI)
    n_fast = state_size - n_slow

    # Slow group: A values from 0.5 to 2 (gentle decay)
    slow = torch.linspace(0.5, 2.0, n_slow)
    # Fast group: A values from 2 to state_size (aggressive decay)
    fast = torch.linspace(2.0, float(state_size), n_fast)

    A_init = torch.cat([slow, fast])
    return torch.log(A_init)  # stored as log for exp() parameterization


# ═══════════════════════════════════════════════════════════════════════
#  HIERARCHICAL WORLDLINE
# ═══════════════════════════════════════════════════════════════════════

class HierarchicalWorldline(nn.Module):
    """
    Three nested worldlines at different compression depths.

    d_fast:  ⊛^1 compression, high α_d   (parts = ☀︎ = past, recent)
    d_mid:   ⊛^2 compression, medium α_d  (self = i = present)
    d_deep:  ⊛^3 compression, low α_d     (whole = ⊛ = future, identity)

    Overflow: when a level's magnitude exceeds its capacity,
    the excess cascades downward to the next level.

    Retrieval: resonance gate searches all three levels.
    The level with the best phase match contributes most.
    """

    def __init__(self, state_size: int, d_model: int,
                 alpha_fast: float = 0.05,
                 alpha_mid: float = 0.01,
                 alpha_deep: float = 0.002,
                 capacity_fast: float = 10.0,
                 capacity_mid: float = 15.0,
                 capacity_deep: float = 20.0):
        super().__init__()
        self.state_size = state_size
        self.d_model = d_model

        self.alpha_fast = alpha_fast
        self.alpha_mid = alpha_mid
        self.alpha_deep = alpha_deep

        self.capacity_fast = capacity_fast
        self.capacity_mid = capacity_mid
        self.capacity_deep = capacity_deep

        # Compression exponents: (2/3)^1, (2/3)^2, (2/3)^3
        self.exp_fast = 2.0 / 3.0
        self.exp_mid = (2.0 / 3.0) ** 2   # ≈ 0.444
        self.exp_deep = (2.0 / 3.0) ** 3  # ≈ 0.296

        # Resonance projection: real input → complex for phase matching
        self.W_resonance = nn.Linear(d_model, state_size * 2, bias=False)

        # Per-level output scaling (learnable, initialized to equal weight)
        self.level_weight = nn.Parameter(torch.ones(3) / 3.0)

    def init_state(self, batch_size: int, device: torch.device):
        """Initialize all three worldlines with DNA phases."""
        d_fast = dna_init(self.state_size, batch_size, device, magnitude=0.01)
        d_mid = dna_init(self.state_size, batch_size, device, magnitude=0.005)
        d_deep = dna_init(self.state_size, batch_size, device, magnitude=0.001)
        balance = torch.full((batch_size, 1), BALANCE, device=device)
        return d_fast, d_mid, d_deep, balance

    def _clamp_and_overflow(self, d: torch.Tensor, capacity: float):
        """
        Clamp magnitude to capacity. Return (clamped, overflow).
        Overflow preserves phase; it's what exceeds the capacity.
        """
        mag = c_mag(d).unsqueeze(-1)           # (batch, state, 1)
        excess_mask = (mag > capacity).float()
        overflow_mag = (mag - capacity) * excess_mask
        overflow_phase = c_phase(d)
        overflow = c_from_polar(overflow_mag.squeeze(-1), overflow_phase)

        # Clamp d
        d_clamped = torch.where(
            mag > capacity,
            d * (capacity / mag),
            d
        )
        return d_clamped, overflow

    def absorb(self, released: torch.Tensor, balance: torch.Tensor,
               d_fast: torch.Tensor, d_mid: torch.Tensor, d_deep: torch.Tensor):
        """
        Absorb released state into the hierarchical worldline.

        released: (batch, state_size, 2) complex; averaged release from SSM state.
        Returns: updated (d_fast, d_mid, d_deep, balance)
        """
        # ── Adaptive compression exponent via ◐ ──
        # exponent = (1 + ◐) / (2 + ◐)
        bal = balance.squeeze(-1).mean()  # scalar for exponent calc
        bal_clamped = torch.clamp(bal, min=0.01, max=0.99)
        adaptive_exp = (1.0 + bal_clamped) / (2.0 + bal_clamped)

        # ── Adaptive α via ◐ ──
        # Fastest absorption at balance (◐=0.5), slows when imbalanced
        balance_quality = 1.0 - 2.0 * torch.abs(bal_clamped - BALANCE)  # 1 at balance, 0 at extremes
        balance_quality = torch.clamp(balance_quality, min=0.1)  # floor at 10%

        a_fast = self.alpha_fast * balance_quality
        a_mid = self.alpha_mid * balance_quality
        a_deep = self.alpha_deep * balance_quality

        # ── Level 1: Fast (working memory) ──
        # Use adaptive exponent (mild compression)
        compressed_fast = converge(released, exponent=adaptive_exp.item())
        compressed_fast = torch.clamp(compressed_fast, min=-10.0, max=10.0)
        d_fast = d_fast.detach() + a_fast * compressed_fast

        # Overflow from fast → mid
        d_fast, overflow_1 = self._clamp_and_overflow(d_fast, self.capacity_fast)

        # ── Level 2: Mid (episodic memory) ──
        # Deeper compression on overflow
        compressed_mid = converge(overflow_1, exponent=self.exp_mid)
        d_mid = d_mid.detach() + a_mid * compressed_mid

        # Overflow from mid → deep
        d_mid, overflow_2 = self._clamp_and_overflow(d_mid, self.capacity_mid)

        # ── Level 3: Deep (identity / semantic) ──
        # Heaviest compression
        compressed_deep = converge(overflow_2, exponent=self.exp_deep)
        d_deep = d_deep.detach() + a_deep * compressed_deep

        # Clamp deep (final boundary)
        d_mag = c_mag(d_deep).unsqueeze(-1)
        d_deep = torch.where(
            d_mag > self.capacity_deep,
            d_deep * (self.capacity_deep / d_mag),
            d_deep
        )

        # ── Update ◐ ──
        convergent_energy = (c_mag(released) ** 2).sum(dim=-1, keepdim=True)
        # emergent energy will be computed in the main cell and passed back
        # For now, track convergent side
        self._last_convergent = convergent_energy

        return d_fast, d_mid, d_deep

    def retrieve(self, x_t: torch.Tensor,
                 d_fast: torch.Tensor, d_mid: torch.Tensor, d_deep: torch.Tensor):
        """
        Resonance retrieval across all three worldline levels.

        x_t: (batch, d_model) real input
        Returns: surfaced (batch, state_size, 2) complex
        """
        batch = x_t.shape[0]

        # Project input into complex space for phase matching
        x_proj = self.W_resonance(x_t)
        x_complex = x_proj.view(batch, self.state_size, 2)

        # Normalize level weights
        w = F.softmax(self.level_weight, dim=0)

        surfaced = torch.zeros(batch, self.state_size, 2, device=x_t.device)

        for i, (d_level, cap) in enumerate([
            (d_fast.detach(), self.capacity_fast),
            (d_mid.detach(), self.capacity_mid),
            (d_deep.detach(), self.capacity_deep),
        ]):
            # Resonance: T = cos²(Δφ/2)
            T = resonance_gate(x_complex, d_level)  # (batch, state_size)

            # Normalize and scale (gentle emergence)
            d_mag = c_mag(d_level).unsqueeze(-1)
            d_normed = d_level / (d_mag + 1e-8)
            d_scale = torch.sqrt(torch.clamp(d_mag, min=1e-6, max=cap))

            level_surfaced = d_normed * d_scale * T.unsqueeze(-1)
            surfaced = surfaced + w[i] * level_surfaced

        return surfaced

    def update_balance(self, balance: torch.Tensor,
                       emergent_energy: torch.Tensor) -> torch.Tensor:
        """Update ◐ with both convergent and emergent energy."""
        convergent = self._last_convergent if hasattr(self, '_last_convergent') \
            else torch.ones_like(emergent_energy)
        total = convergent + emergent_energy + 1e-8
        b_measured = convergent / total
        return 0.99 * balance + 0.01 * b_measured


# ═══════════════════════════════════════════════════════════════════════
#  CIRCUMPUNCT SSM v2 (Mamba + Hierarchical Fractal Worldline)
# ═══════════════════════════════════════════════════════════════════════

class CircumpunctSSMv2(nn.Module):
    """
    Selective SSM with hierarchical fractal worldline,
    adaptive compression, and φ-scaled state partitioning.

    The standard Mamba state update is augmented:
        released_t = (1 - α_t) · h_{t-1}
        worldline.absorb(released_t)
        surfaced_t = worldline.retrieve(x_t)
        h_t = α_t · h_{t-1} + γ_t · B_t · (x_t + surfaced_t)
    """

    def __init__(self, d_model: int, state_size: int = 16, dt_rank: int = None,
                 alpha_fast: float = 0.05, alpha_mid: float = 0.01,
                 alpha_deep: float = 0.002):
        super().__init__()
        self.d_model = d_model
        self.state_size = state_size
        self.dt_rank = dt_rank or max(d_model // 16, 1)

        # A: φ-scaled initialization (Upgrade 3)
        self.A_log = nn.Parameter(phi_scaled_A_init(state_size))

        # Projections
        self.x_proj = nn.Linear(d_model, self.dt_rank + 2 * state_size * 2, bias=False)
        self.dt_proj = nn.Linear(self.dt_rank, d_model)
        self.out_proj = nn.Linear(d_model, d_model)
        self.in_proj = nn.Linear(d_model, d_model * 2, bias=False)

        # Hierarchical worldline (Upgrade 1)
        self.worldline = HierarchicalWorldline(
            state_size, d_model,
            alpha_fast=alpha_fast, alpha_mid=alpha_mid, alpha_deep=alpha_deep)

        # Surface projection: maps surfaced memory (state_size*2) back to d_model
        # so it enters through B_t properly, not bypassing the state-input transform
        self.surface_proj = nn.Linear(state_size * 2, d_model, bias=False)

        self._init_weights()

    def _init_weights(self):
        scale = 1.0 / PHI
        for name, p in self.named_parameters():
            if 'A_log' in name:
                continue  # already initialized by phi_scaled_A_init
            if p.dim() >= 2:
                nn.init.uniform_(p, -scale / math.sqrt(p.shape[1]),
                                 scale / math.sqrt(p.shape[1]))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (batch, seq_len, d_model)
        Returns: (batch, seq_len, d_model)
        """
        batch, seq_len, _ = x.shape
        device = x.device

        # SiLU gating
        xz = self.in_proj(x)
        x_in, z = xz.chunk(2, dim=-1)
        x_in = F.silu(x_in)

        # Project to SSM params
        xp = self.x_proj(x_in)
        dt_raw = xp[..., :self.dt_rank]
        bc_raw = xp[..., self.dt_rank:]

        dt = F.softplus(self.dt_proj(dt_raw))

        bc = bc_raw.view(batch, seq_len, 2, self.state_size, 2)
        B = bc[:, :, 0]
        C = bc[:, :, 1]

        # Initialize states
        h = torch.zeros(batch, self.d_model, self.state_size, 2, device=device)
        d_fast, d_mid, d_deep, balance = self.worldline.init_state(batch, device)

        A = self.A_log

        outputs = []
        for t in range(seq_len):
            x_t = x_in[:, t]        # (batch, d_model)
            dt_t = dt[:, t]          # (batch, d_model)
            B_t = B[:, t]            # (batch, state_size, 2)
            C_t = C[:, t]            # (batch, state_size, 2)

            # ════════════════════════════════════════
            #  RESONANCE RETRIEVAL from worldline
            # ════════════════════════════════════════

            surfaced = self.worldline.retrieve(x_t, d_fast, d_mid, d_deep)
            # (batch, state_size, 2)

            # ════════════════════════════════════════
            #  SELECTIVE SSM UPDATE
            # ════════════════════════════════════════

            A_neg = -torch.exp(A)
            dt_A = dt_t.unsqueeze(-1) * A_neg.unsqueeze(0)
            alpha_t = torch.exp(dt_A)  # (batch, d_model, state_size)
            gamma_t = dt_t             # (batch, d_model)

            # Build input: γ_t · B_t · (x_t + surfaced_t)
            # Surfaced is (batch, state_size, 2) complex; project back to
            # (batch, d_model) real so it can be added to x_t BEFORE B_t.
            surfaced_flat = surfaced.reshape(batch, -1)  # (batch, state_size*2)
            surfaced_contribution = self.surface_proj(surfaced_flat)  # (batch, d_model)
            x_augmented = x_t + surfaced_contribution

            x_complex = torch.stack([x_augmented, torch.zeros_like(x_augmented)], dim=-1)
            Bx = c_mul(
                B_t.unsqueeze(1).expand(-1, self.d_model, -1, -1),
                x_complex.unsqueeze(2).expand(-1, -1, self.state_size, -1)
            )
            Bx = c_scale(Bx, gamma_t.unsqueeze(-1))

            # ════════════════════════════════════════
            #  ⊛ CAPTURE RELEASED STATE
            # ════════════════════════════════════════

            released = c_scale(h, 1.0 - alpha_t)  # (batch, d_model, state_size, 2)

            # Average over d_model for worldline absorption
            released_avg = released.mean(dim=1)  # (batch, state_size, 2)

            # Absorb into hierarchical worldline (with adaptive ◐)
            d_fast, d_mid, d_deep = self.worldline.absorb(
                released_avg, balance, d_fast, d_mid, d_deep)

            # ════════════════════════════════════════
            #  STATE UPDATE AND OUTPUT
            # ════════════════════════════════════════

            h = c_scale(h, alpha_t) + Bx

            # Output: y_t = Re(C_t^H · h_t), conjugate multiply
            Ch = c_mul(
                c_conj(C_t).unsqueeze(1).expand(-1, self.d_model, -1, -1),
                h
            )
            y_t = Ch[..., 0].sum(dim=-1)  # real part, summed over state
            outputs.append(y_t)

            # Update ◐
            emergent_energy = (y_t ** 2).sum(dim=-1, keepdim=True)
            balance = self.worldline.update_balance(balance, emergent_energy)

        y = torch.stack(outputs, dim=1)
        y = y * F.silu(z)
        return self.out_proj(y)


# ═══════════════════════════════════════════════════════════════════════
#  STANDARD SSM BASELINE (same as v1, for fair comparison)
# ═══════════════════════════════════════════════════════════════════════

class SelectiveSSM(nn.Module):
    """Standard selective SSM (Mamba-2 style) baseline."""

    def __init__(self, d_model: int, state_size: int = 16, dt_rank: int = None):
        super().__init__()
        self.d_model = d_model
        self.state_size = state_size
        self.dt_rank = dt_rank or max(d_model // 16, 1)

        self.A_log = nn.Parameter(torch.log(torch.linspace(1, state_size, state_size)))
        self.x_proj = nn.Linear(d_model, self.dt_rank + 2 * state_size * 2, bias=False)
        self.dt_proj = nn.Linear(self.dt_rank, d_model)
        self.out_proj = nn.Linear(d_model, d_model)
        self.in_proj = nn.Linear(d_model, d_model * 2, bias=False)

        self._init_weights()

    def _init_weights(self):
        scale = 1.0 / PHI
        for name, p in self.named_parameters():
            if p.dim() >= 2:
                nn.init.uniform_(p, -scale / math.sqrt(p.shape[1]),
                                 scale / math.sqrt(p.shape[1]))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch, seq_len, _ = x.shape
        device = x.device

        xz = self.in_proj(x)
        x_in, z = xz.chunk(2, dim=-1)
        x_in = F.silu(x_in)

        xp = self.x_proj(x_in)
        dt_raw = xp[..., :self.dt_rank]
        bc_raw = xp[..., self.dt_rank:]

        dt = F.softplus(self.dt_proj(dt_raw))
        bc = bc_raw.view(batch, seq_len, 2, self.state_size, 2)
        B = bc[:, :, 0]
        C = bc[:, :, 1]

        h = torch.zeros(batch, self.d_model, self.state_size, 2, device=device)
        A = self.A_log

        outputs = []
        for t in range(seq_len):
            A_neg = -torch.exp(A)
            dt_A = dt[:, t].unsqueeze(-1) * A_neg.unsqueeze(0)
            alpha_t = torch.exp(dt_A)
            gamma_t = dt[:, t]

            x_complex = torch.stack([x_in[:, t], torch.zeros_like(x_in[:, t])], dim=-1)
            Bx = c_mul(
                B[:, t].unsqueeze(1).expand(-1, self.d_model, -1, -1),
                x_complex.unsqueeze(2).expand(-1, -1, self.state_size, -1)
            )
            Bx = c_scale(Bx, gamma_t.unsqueeze(-1))

            h = c_scale(h, alpha_t) + Bx

            Ch = c_mul(
                C[:, t].unsqueeze(1).expand(-1, self.d_model, -1, -1),
                h
            )
            y_t = Ch[..., 0].sum(dim=-1)
            outputs.append(y_t)

        y = torch.stack(outputs, dim=1)
        y = y * F.silu(z)
        return self.out_proj(y)


# ═══════════════════════════════════════════════════════════════════════
#  SEQUENCE MODELS
# ═══════════════════════════════════════════════════════════════════════

class MambaModel(nn.Module):
    """Standard Mamba baseline."""
    def __init__(self, vocab_size: int, d_model: int = 64, state_size: int = 16,
                 n_layers: int = 2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.layers = nn.ModuleList([
            SelectiveSSM(d_model, state_size) for _ in range(n_layers)
        ])
        self.norm = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size)

    def forward(self, x):
        h = self.embedding(x)
        for layer in self.layers:
            h = h + layer(h)
        return self.head(self.norm(h))


class CircumpunctMambaModel(nn.Module):
    """Circumpunct Mamba v2."""
    def __init__(self, vocab_size: int, d_model: int = 64, state_size: int = 16,
                 n_layers: int = 2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.layers = nn.ModuleList([
            CircumpunctSSMv2(d_model, state_size) for _ in range(n_layers)
        ])
        self.norm = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size)

    def forward(self, x):
        h = self.embedding(x)
        for layer in self.layers:
            h = h + layer(h)
        return self.head(self.norm(h))


# ═══════════════════════════════════════════════════════════════════════
#  BENCHMARKS
# ═══════════════════════════════════════════════════════════════════════

class CopyingProblem:
    """Remember 8 digits across T blank timesteps."""
    def __init__(self, T=100, n_digits=8, vocab_size=10, batch_size=32):
        self.T, self.n_digits, self.vocab_size = T, n_digits, vocab_size
        self.batch_size = batch_size
        self.seq_len = 1 + n_digits + T + 1 + n_digits
        self.BLANK, self.MARKER, self.TRIGGER = vocab_size, vocab_size+1, vocab_size+2
        self.total_tokens = vocab_size + 3
        self.trigger_pos = 1 + n_digits + T
        self.output_len = n_digits

    def generate_batch(self, device=None):
        b = self.batch_size
        seq = torch.full((b, self.seq_len), self.BLANK, dtype=torch.long, device=device)
        tgt = torch.full((b, self.seq_len), self.BLANK, dtype=torch.long, device=device)
        seq[:, 0] = self.MARKER
        digits = torch.randint(0, self.vocab_size, (b, self.n_digits), device=device)
        seq[:, 1:1+self.n_digits] = digits
        seq[:, self.trigger_pos] = self.TRIGGER
        tgt[:, self.trigger_pos+1:self.trigger_pos+1+self.n_digits] = digits
        return seq, tgt


class SelectiveCopyingProblem:
    """
    Selective copying: remember only the marked tokens across T blanks.

    Input:  [MARKER digit BLANK digit MARKER digit ...] [T blanks] [trigger] [blanks]
    Target: [blanks...] [the digits that were preceded by MARKER, in order]

    Each of n_total positions is either (MARKER, digit) or (BLANK, digit).
    The model sees all digits but must recall only the marked ones.
    Sequence length = n_total * 2 + T + 1 + n_marked.
    """
    def __init__(self, T=100, n_total=16, n_marked=8, vocab_size=10, batch_size=32):
        self.T, self.n_total, self.n_marked = T, n_total, n_marked
        self.vocab_size, self.batch_size = vocab_size, batch_size
        # Each position takes 2 tokens: (marker_or_blank, digit)
        self.seq_len = n_total * 2 + T + 1 + n_marked
        self.BLANK, self.MARKER, self.TRIGGER = vocab_size, vocab_size+1, vocab_size+2
        self.total_tokens = vocab_size + 3
        self.trigger_pos = n_total * 2 + T
        self.output_len = n_marked

    def generate_batch(self, device=None):
        b = self.batch_size
        seq = torch.full((b, self.seq_len), self.BLANK, dtype=torch.long, device=device)
        tgt = torch.full((b, self.seq_len), self.BLANK, dtype=torch.long, device=device)
        for i in range(b):
            tokens = torch.randint(0, self.vocab_size, (self.n_total,), device=device)
            marked = torch.randperm(self.n_total, device=device)[:self.n_marked].sort().values
            marked_set = set(marked.tolist())
            for j in range(self.n_total):
                # Position j gets two slots: (flag, digit)
                flag = self.MARKER if j in marked_set else self.BLANK
                seq[i, j * 2] = flag
                seq[i, j * 2 + 1] = tokens[j]  # digit is ALWAYS visible
            tgt[i, self.trigger_pos+1:self.trigger_pos+1+self.n_marked] = tokens[marked]
        seq[:, self.trigger_pos] = self.TRIGGER
        return seq, tgt


# ═══════════════════════════════════════════════════════════════════════
#  TRAINING
# ═══════════════════════════════════════════════════════════════════════

def train_benchmark(model_type='circumpunct', problem_type='copying',
                    T=100, n_epochs=300, lr=0.001, batch_size=32,
                    d_model=64, state_size=16, n_layers=2, verbose=True):
    """Train on a benchmark. model_type: 'circumpunct' or 'standard'."""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    problem = CopyingProblem(T=T, batch_size=batch_size) if problem_type == 'copying' \
        else SelectiveCopyingProblem(T=T, batch_size=batch_size)

    model = (CircumpunctMambaModel if model_type == 'circumpunct' else MambaModel)(
        vocab_size=problem.total_tokens, d_model=d_model,
        state_size=state_size, n_layers=n_layers
    ).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    n_params = sum(p.numel() for p in model.parameters())

    if verbose:
        print(f"\n{'=' * 60}")
        print(f"  ⊙ {problem_type.title()} Benchmark  |  {model_type}")
        print(f"  Params: {n_params:,}  |  T={T}  |  seq={problem.seq_len}")
        print(f"  d={d_model}  N={state_size}  layers={n_layers}  |  {device}")
        print(f"{'=' * 60}\n")

    tp = problem.trigger_pos
    ol = problem.output_len
    best_acc = 0.0
    history = []
    nan_skips = 0

    for epoch in range(n_epochs):
        model.train()
        seq, target = problem.generate_batch(device)
        logits = model(seq)

        out_logits = logits[:, tp+1:tp+1+ol]
        out_target = target[:, tp+1:tp+1+ol]
        loss = F.cross_entropy(out_logits.reshape(-1, problem.total_tokens),
                               out_target.reshape(-1))

        if torch.isnan(loss).item() or torch.isinf(loss).item():
            optimizer.zero_grad()
            nan_skips += 1
            continue

        optimizer.zero_grad()
        loss.backward()

        if any(p.grad is not None and (torch.isnan(p.grad).any() or torch.isinf(p.grad).any())
               for p in model.parameters()):
            nan_skips += 1
            optimizer.zero_grad()
            continue

        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        model.eval()
        with torch.no_grad():
            e_seq, e_tgt = problem.generate_batch(device)
            e_log = model(e_seq)
            preds = e_log[:, tp+1:tp+1+ol].argmax(dim=-1)
            acc = (preds == e_tgt[:, tp+1:tp+1+ol]).float().mean().item()
            best_acc = max(best_acc, acc)

        history.append({'epoch': epoch, 'loss': loss.item(), 'acc': acc})

        if verbose and (epoch % 25 == 0 or epoch == n_epochs - 1):
            skip = f"  skip={nan_skips}" if nan_skips else ""
            print(f"  E{epoch:4d}  loss={loss.item():.4f}  acc={acc:.3f}"
                  f"  best={best_acc:.3f}{skip}")

    return history, best_acc


# ═══════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import sys

    T = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    n_epochs = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    problem = sys.argv[3] if len(sys.argv) > 3 else 'copying'

    print("\n⊙ THE CIRCUMPUNCT MAMBA v2")
    print("  Hierarchical memory. Adaptive compression. φ-scaled state.\n")

    print("\n" + "─" * 60)
    print("  STANDARD MAMBA (baseline)")
    print("─" * 60)
    std_h, std_best = train_benchmark('standard', problem, T=T, n_epochs=n_epochs)

    print("\n" + "─" * 60)
    print("  CIRCUMPUNCT MAMBA v2")
    print("─" * 60)
    circ_h, circ_best = train_benchmark('circumpunct', problem, T=T, n_epochs=n_epochs)

    # Parameter comparison
    std_p = sum(p.numel() for p in MambaModel(13, 64, 16, 2).parameters())
    circ_p = sum(p.numel() for p in CircumpunctMambaModel(13, 64, 16, 2).parameters())

    print(f"\n{'=' * 60}")
    print(f"  RESULTS (T={T}, {problem})")
    print(f"  Standard Mamba:    {std_best:.3f}  ({std_p:,} params)")
    print(f"  Circumpunct v2:    {circ_best:.3f}  ({circ_p:,} params)")
    print(f"  Param ratio:       {circ_p/std_p:.2f}x")
    print(f"{'=' * 60}")
