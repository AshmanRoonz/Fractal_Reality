"""
⊙ The Circumpunct Mamba
========================

A selective state space model where forgetting becomes fractal compression.

Based on Mamba-2/3 (Gu, Dao et al. 2024-2026), modified with one structural
change from the Circumpunct Framework:

    What the selective mechanism discards does not vanish.
    It gets fractally compressed into a deep state (the worldline),
    preserving phase while reducing magnitude.
    Resonance retrieval surfaces it when the input phase-matches.

The standard Mamba state update:
    h_t = α_t · h_{t-1} + γ_t · B_t · x_t          (destroyed: (1-α_t)·h_{t-1})

The Circumpunct Mamba state update:
    released_t = (1 - α_t) · h_{t-1}                 (what Mamba would destroy)
    d_t = d_{t-1} + α_d · ⊛(released_t)              (fractal compress into worldline)
    surfaced_t = T(x_t, d_t) · d_t                    (resonance retrieval)
    h_t = α_t · h_{t-1} + γ_t · B_t · (x_t + surfaced_t)   (state update)
    y_t = C_tᵀ · h_t

Where:
    ⊛(z) = |z|^(2/3) · e^(iφ)     fractal compression (magnitude shrinks, phase preserved)
    T = cos²(Δφ/2)                  resonance gate (phase matching)

All states are complex-valued (following Mamba-3's direction).
The worldline is detached from the gradient graph.
Phase is the thing that survives.

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

PHI = (1 + math.sqrt(5)) / 2          # φ = 1.618...; golden ratio
COMPRESS_EXP = 2.0 / 3.0              # 2/3 = 2D/3D; fractal compression


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


def c_scale(z: torch.Tensor, s: torch.Tensor) -> torch.Tensor:
    """Scale complex tensor by real scalar (broadcast-safe)."""
    if s.dim() < z.dim():
        s = s.unsqueeze(-1)
    return z * s


# ═══════════════════════════════════════════════════════════════════════
#  ⊛ FRACTAL COMPRESSION
# ═══════════════════════════════════════════════════════════════════════

class _FractalCompress(torch.autograd.Function):
    """
    Custom autograd for ⊛: |x|^(2/3) with stable gradients.

    Forward: true fractal compression (2/3 power on magnitude).
    Backward: straight-through scaled by compression ratio.
    Avoids the infinite gradient of x^(2/3) at x=0.
    """
    @staticmethod
    def forward(ctx, mag):
        mag_safe = torch.clamp(mag, min=1e-8)
        compressed = mag_safe ** COMPRESS_EXP
        ratio = compressed / (mag_safe + 1e-6)
        ctx.save_for_backward(ratio)
        return compressed

    @staticmethod
    def backward(ctx, grad_output):
        ratio, = ctx.saved_tensors
        return grad_output * torch.clamp(ratio, max=2.0)


def converge(z: torch.Tensor) -> torch.Tensor:
    """
    ⊛: Fractal compression.

    Magnitude compressed by exponent 2/3.
    Phase preserved exactly.
    The signal gets deeper, not smaller.
    """
    mag = c_mag(z)
    phase = c_phase(z)
    compressed_mag = _FractalCompress.apply(mag)
    return c_from_polar(compressed_mag, phase)


# ═══════════════════════════════════════════════════════════════════════
#  T: RESONANCE GATE
# ═══════════════════════════════════════════════════════════════════════

def resonance_gate(signal: torch.Tensor, memory: torch.Tensor) -> torch.Tensor:
    """
    T = cos²(Δφ/2)

    Phase matching between signal and memory.
    Perfect match (Δφ = 0): T = 1, memory surfaces.
    Orthogonal (Δφ = π): T = 0, memory stays deep.
    """
    delta_phi = c_phase(signal) - c_phase(memory)
    return torch.cos(delta_phi / 2) ** 2


# ═══════════════════════════════════════════════════════════════════════
#  DNA INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════

def dna_init(state_size: int, batch_size: int, device: torch.device,
             magnitude: float = 0.01) -> torch.Tensor:
    """
    Initialize the worldline with differentiated phase structure.

    64 distinct phases from the 64-state architecture (2^6 = 64).
    If state_size != 64, evenly space phases across the circle.
    Magnitude is tiny (embryonic identity, not yet developed).
    Phase is differentiated from step zero (A1: the 1 must self-limit).
    """
    phases = torch.linspace(0, 2 * math.pi * (1 - 1 / state_size),
                            state_size, device=device)
    d = c_from_polar(
        torch.full((state_size,), magnitude, device=device),
        phases
    )
    return d.unsqueeze(0).expand(batch_size, -1, -1).clone()


# ═══════════════════════════════════════════════════════════════════════
#  SELECTIVE SSM LAYER (Standard Mamba-2 style)
# ═══════════════════════════════════════════════════════════════════════

class SelectiveSSM(nn.Module):
    """
    Standard selective SSM (Mamba-2 style) for baseline comparison.

    h_t = α_t · h_{t-1} + γ_t · B_t · x_t
    y_t = C_tᵀ · h_t

    All states complex-valued (following Mamba-3).
    α_t = exp(Δ_t · A) where A < 0 (learned, data-independent).
    Δ_t, B_t, C_t are input-dependent (projected from x_t).
    """

    def __init__(self, d_model: int, state_size: int = 16, dt_rank: int = None):
        super().__init__()
        self.d_model = d_model
        self.state_size = state_size
        self.dt_rank = dt_rank or max(d_model // 16, 1)

        # A: learnable negative log (ensures A < 0 after -exp)
        self.A_log = nn.Parameter(torch.log(torch.linspace(1, state_size, state_size)))

        # Projections from input to SSM parameters
        # x → (Δ_raw, B, C) all at once for efficiency
        self.x_proj = nn.Linear(d_model, self.dt_rank + 2 * state_size * 2, bias=False)

        # Δ projection: dt_rank → d_model (one Δ per channel)
        self.dt_proj = nn.Linear(self.dt_rank, d_model)

        # Output projection
        self.out_proj = nn.Linear(d_model, d_model)

        # Input/output gates (SiLU gating, standard in Mamba)
        self.in_proj = nn.Linear(d_model, d_model * 2, bias=False)

        self._init_weights()

    def _init_weights(self):
        scale = 1.0 / PHI
        for name, p in self.named_parameters():
            if p.dim() >= 2:
                nn.init.uniform_(p, -scale / math.sqrt(p.shape[1]),
                                 scale / math.sqrt(p.shape[1]))

    def _ssm_step(self, x_t, h_prev, A, dt_t, B_t, C_t):
        """One SSM recurrence step. Returns y_t, h_t."""
        # x_t: (batch, d_model)
        # h_prev: (batch, d_model, state_size, 2) complex
        # dt_t: (batch, d_model)
        # B_t: (batch, state_size, 2) complex
        # C_t: (batch, state_size, 2) complex

        batch = x_t.shape[0]

        # α_t = exp(Δ_t · A) per (d_model, state_size)
        # A is negative, so α ∈ (0, 1)
        A_neg = -torch.exp(A)  # (state_size,)
        dt_A = dt_t.unsqueeze(-1) * A_neg.unsqueeze(0)  # (batch, d_model, state_size)
        alpha_t = torch.exp(dt_A)  # (batch, d_model, state_size)

        # γ_t = Δ_t
        gamma_t = dt_t  # (batch, d_model)

        # State update: h_t = α_t · h_{t-1} + γ_t · B_t · x_t
        # B_t · x_t: outer product, complex
        # x_t is real, broadcast into complex: (x_t, 0)
        x_complex = torch.stack([x_t, torch.zeros_like(x_t)], dim=-1)  # (batch, d_model, 2)
        # B_t: (batch, state_size, 2), x_complex: (batch, d_model, 2)
        # We want (batch, d_model, state_size, 2)
        Bx = c_mul(
            B_t.unsqueeze(1).expand(-1, self.d_model, -1, -1),
            x_complex.unsqueeze(2).expand(-1, -1, self.state_size, -1)
        )  # (batch, d_model, state_size, 2)

        # Scale by γ_t
        Bx = c_scale(Bx, gamma_t.unsqueeze(-1))  # gamma broadcasts over state_size

        # Decay previous state
        h_decayed = c_scale(h_prev, alpha_t)  # (batch, d_model, state_size, 2)

        # New state
        h_t = h_decayed + Bx

        # Output: y_t = Re(C_tᵀ · h_t) summed over state dimension
        # C_t: (batch, state_size, 2), h_t: (batch, d_model, state_size, 2)
        # Conjugate multiply and sum over state_size
        Ch = c_mul(
            C_t.unsqueeze(1).expand(-1, self.d_model, -1, -1),
            h_t
        )  # (batch, d_model, state_size, 2)
        y_t = Ch[..., 0].sum(dim=-1)  # real part, summed over state: (batch, d_model)

        return y_t, h_t, alpha_t

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (batch, seq_len, d_model)
        Returns: (batch, seq_len, d_model)
        """
        batch, seq_len, _ = x.shape
        device = x.device

        # SiLU gating
        xz = self.in_proj(x)  # (batch, seq, d_model*2)
        x_in, z = xz.chunk(2, dim=-1)
        x_in = F.silu(x_in)

        # Project to SSM params
        xp = self.x_proj(x_in)  # (batch, seq, dt_rank + 2*state*2)
        dt_raw = xp[..., :self.dt_rank]
        bc_raw = xp[..., self.dt_rank:]

        # Δ: softplus ensures positive
        dt = F.softplus(self.dt_proj(dt_raw))  # (batch, seq, d_model)

        # B, C: split and reshape into complex
        bc = bc_raw.view(batch, seq_len, 2, self.state_size, 2)
        B = bc[:, :, 0]  # (batch, seq, state_size, 2)
        C = bc[:, :, 1]  # (batch, seq, state_size, 2)

        # Initialize state
        h = torch.zeros(batch, self.d_model, self.state_size, 2, device=device)

        A = self.A_log  # will be negated and exp'd inside step

        outputs = []
        for t in range(seq_len):
            y_t, h, _ = self._ssm_step(
                x_in[:, t], h, A, dt[:, t], B[:, t], C[:, t])
            outputs.append(y_t)

        y = torch.stack(outputs, dim=1)  # (batch, seq, d_model)

        # Output gate and projection
        y = y * F.silu(z)
        return self.out_proj(y)


# ═══════════════════════════════════════════════════════════════════════
#  CIRCUMPUNCT SSM LAYER (Mamba + Fractal Worldline)
# ═══════════════════════════════════════════════════════════════════════

class CircumpunctSSM(nn.Module):
    """
    Selective SSM with fractal worldline.

    Same as SelectiveSSM but with one structural addition:
    what α_t destroys gets fractally compressed into a deep state (d),
    retrievable by phase-matching resonance.

    h_t = α_t · h_{t-1} + γ_t · B_t · (x_t + surfaced_t)
    d_t = d_{t-1} + α_d · ⊛(released_t)
    surfaced_t = T(x_t, d_t) · emerged(d_t)
    """

    def __init__(self, d_model: int, state_size: int = 16, dt_rank: int = None,
                 alpha_d: float = 0.01):
        super().__init__()
        self.d_model = d_model
        self.state_size = state_size
        self.dt_rank = dt_rank or max(d_model // 16, 1)
        self.alpha_d = alpha_d

        # A: learnable negative log
        self.A_log = nn.Parameter(torch.log(torch.linspace(1, state_size, state_size)))

        # Projections from input to SSM parameters
        self.x_proj = nn.Linear(d_model, self.dt_rank + 2 * state_size * 2, bias=False)
        self.dt_proj = nn.Linear(self.dt_rank, d_model)

        # Output projection
        self.out_proj = nn.Linear(d_model, d_model)

        # Input/output gates
        self.in_proj = nn.Linear(d_model, d_model * 2, bias=False)

        # ── Circumpunct addition: resonance projection ──
        # Projects real input into complex space for phase matching
        # against the worldline. This IS the boundary (○): where
        # real signal meets complex memory.
        self.W_resonance = nn.Linear(d_model, state_size * 2, bias=False)

        self._init_weights()

    def _init_weights(self):
        scale = 1.0 / PHI
        for name, p in self.named_parameters():
            if p.dim() >= 2:
                nn.init.uniform_(p, -scale / math.sqrt(p.shape[1]),
                                 scale / math.sqrt(p.shape[1]))

    def _ssm_step(self, x_t, h_prev, d_prev, A, dt_t, B_t, C_t):
        """
        One SSM recurrence step with fractal worldline.
        Returns y_t, h_t, d_t.
        """
        batch = x_t.shape[0]

        # ════════════════════════════════════════════════
        #  RESONANCE RETRIEVAL from worldline
        # ════════════════════════════════════════════════

        # Project input into complex space for phase matching
        x_proj = self.W_resonance(x_t)  # (batch, state_size * 2)
        x_complex = x_proj.view(batch, self.state_size, 2)  # (batch, state_size, 2)

        # Read worldline (detached: you cannot backprop through the soul)
        d_read = d_prev.detach()

        # T = cos²(Δφ/2): resonance between input and worldline
        T = resonance_gate(x_complex, d_read)  # (batch, state_size)

        # Surface: normalize worldline, scale gently, gate by resonance
        d_mag = c_mag(d_read).unsqueeze(-1)  # (batch, state_size, 1)
        d_normed = d_read / (d_mag + 1e-8)
        d_scale = torch.sqrt(torch.clamp(d_mag, min=1e-6, max=20.0))
        surfaced = d_normed * d_scale * T.unsqueeze(-1)  # (batch, state_size, 2)

        # ════════════════════════════════════════════════
        #  STANDARD SSM UPDATE (with augmented input)
        # ════════════════════════════════════════════════

        A_neg = -torch.exp(A)
        dt_A = dt_t.unsqueeze(-1) * A_neg.unsqueeze(0)
        alpha_t = torch.exp(dt_A)  # (batch, d_model, state_size)

        gamma_t = dt_t  # (batch, d_model)

        # x_t + surfaced contribution: surfaced is (batch, state_size, 2)
        # We need to add surfaced into the Bx computation.
        # The surfaced memory augments the B projection:
        # Instead of B_t · x_t, we compute B_t · x_t + surfaced
        x_complex_full = torch.stack([x_t, torch.zeros_like(x_t)], dim=-1)
        Bx = c_mul(
            B_t.unsqueeze(1).expand(-1, self.d_model, -1, -1),
            x_complex_full.unsqueeze(2).expand(-1, -1, self.state_size, -1)
        )
        # Add surfaced memory (broadcast across d_model)
        Bx = Bx + surfaced.unsqueeze(1).expand(-1, self.d_model, -1, -1)
        Bx = c_scale(Bx, gamma_t.unsqueeze(-1))

        # Decay previous state
        h_decayed = c_scale(h_prev, alpha_t)

        # ════════════════════════════════════════════════
        #  ⊛ FRACTAL COMPRESSION of released state
        # ════════════════════════════════════════════════

        # What Mamba would destroy
        released = c_scale(h_prev, 1.0 - alpha_t)  # (batch, d_model, state_size, 2)

        # Compress: magnitude^(2/3), phase preserved
        compressed = converge(released)
        compressed = torch.clamp(compressed, min=-10.0, max=10.0)

        # Average over d_model channels to get (batch, state_size, 2)
        # Each state dimension accumulates the mean release across channels
        compressed_avg = compressed.mean(dim=1)  # (batch, state_size, 2)

        # Accumulate into worldline (detached history + current contribution)
        d_t = d_prev.detach() + self.alpha_d * compressed_avg
        # Clamp magnitude
        d_mag_new = c_mag(d_t).unsqueeze(-1)
        d_t = torch.where(d_mag_new > 20.0, d_t * (20.0 / d_mag_new), d_t)

        # ════════════════════════════════════════════════
        #  STATE UPDATE AND OUTPUT
        # ════════════════════════════════════════════════

        h_t = h_decayed + Bx

        # Output: y_t = Re(C_tᵀ · h_t) summed over state
        Ch = c_mul(
            C_t.unsqueeze(1).expand(-1, self.d_model, -1, -1),
            h_t
        )
        y_t = Ch[..., 0].sum(dim=-1)  # (batch, d_model)

        return y_t, h_t, d_t

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
        d = dna_init(self.state_size, batch, device)  # DNA-initialized worldline

        A = self.A_log

        outputs = []
        for t in range(seq_len):
            y_t, h, d = self._ssm_step(
                x_in[:, t], h, d, A, dt[:, t], B[:, t], C[:, t])
            outputs.append(y_t)

        y = torch.stack(outputs, dim=1)
        y = y * F.silu(z)
        return self.out_proj(y)


# ═══════════════════════════════════════════════════════════════════════
#  SEQUENCE MODELS (for benchmarking)
# ═══════════════════════════════════════════════════════════════════════

class MambaModel(nn.Module):
    """Standard Mamba model for benchmark."""

    def __init__(self, vocab_size: int, d_model: int = 64, state_size: int = 16,
                 n_layers: int = 2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.layers = nn.ModuleList([
            SelectiveSSM(d_model, state_size) for _ in range(n_layers)
        ])
        self.norm = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.embedding(x)
        for layer in self.layers:
            h = h + layer(h)  # residual
        h = self.norm(h)
        return self.head(h)


class CircumpunctMambaModel(nn.Module):
    """Circumpunct Mamba model for benchmark."""

    def __init__(self, vocab_size: int, d_model: int = 64, state_size: int = 16,
                 n_layers: int = 2, alpha_d: float = 0.01):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.layers = nn.ModuleList([
            CircumpunctSSM(d_model, state_size, alpha_d=alpha_d)
            for _ in range(n_layers)
        ])
        self.norm = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.embedding(x)
        for layer in self.layers:
            h = h + layer(h)  # residual
        h = self.norm(h)
        return self.head(h)


# ═══════════════════════════════════════════════════════════════════════
#  BENCHMARK: COPYING PROBLEM
# ═══════════════════════════════════════════════════════════════════════

class CopyingProblem:
    """
    Classic long-range dependency benchmark.

    Input:  [marker] [8 random digits] [T blank tokens] [trigger] [8 blanks]
    Target: [blanks...] [the original 8 digits]

    The network must remember 8 digits across T blank timesteps.
    """

    def __init__(self, T: int = 100, n_digits: int = 8,
                 vocab_size: int = 10, batch_size: int = 32):
        self.T = T
        self.n_digits = n_digits
        self.vocab_size = vocab_size
        self.batch_size = batch_size
        self.seq_len = 1 + n_digits + T + 1 + n_digits
        self.BLANK = vocab_size
        self.MARKER = vocab_size + 1
        self.TRIGGER = vocab_size + 2
        self.total_tokens = vocab_size + 3

    def generate_batch(self, device=None):
        batch = self.batch_size
        seq = torch.full((batch, self.seq_len), self.BLANK,
                         dtype=torch.long, device=device)
        target = torch.full((batch, self.seq_len), self.BLANK,
                            dtype=torch.long, device=device)

        seq[:, 0] = self.MARKER
        digits = torch.randint(0, self.vocab_size,
                               (batch, self.n_digits), device=device)
        seq[:, 1:1 + self.n_digits] = digits

        trigger_pos = 1 + self.n_digits + self.T
        seq[:, trigger_pos] = self.TRIGGER
        target[:, trigger_pos + 1:trigger_pos + 1 + self.n_digits] = digits

        return seq, target


# ═══════════════════════════════════════════════════════════════════════
#  BENCHMARK: SELECTIVE COPYING
# ═══════════════════════════════════════════════════════════════════════

class SelectiveCopyingProblem:
    """
    Selective copying: remember WHICH items to recall, not just THAT there were items.

    Input:  [16 tokens, 8 marked with * prefix] [T blanks] [trigger] [8 blanks]
    Target: [blanks...] [the 8 marked tokens in order]

    Harder than basic copying: the network must attend to markers
    AND remember content across the gap.
    """

    def __init__(self, T: int = 100, n_total: int = 16, n_marked: int = 8,
                 vocab_size: int = 10, batch_size: int = 32):
        self.T = T
        self.n_total = n_total
        self.n_marked = n_marked
        self.vocab_size = vocab_size
        self.batch_size = batch_size
        self.seq_len = n_total + T + 1 + n_marked
        self.BLANK = vocab_size
        self.MARKER = vocab_size + 1  # prefixed to marked tokens
        self.TRIGGER = vocab_size + 2
        self.total_tokens = vocab_size + 3

    def generate_batch(self, device=None):
        batch = self.batch_size
        seq = torch.full((batch, self.seq_len), self.BLANK,
                         dtype=torch.long, device=device)
        target = torch.full((batch, self.seq_len), self.BLANK,
                            dtype=torch.long, device=device)

        for b in range(batch):
            # Generate n_total random tokens
            all_tokens = torch.randint(0, self.vocab_size, (self.n_total,), device=device)
            # Randomly mark n_marked of them
            marked_idx = torch.randperm(self.n_total, device=device)[:self.n_marked].sort().values

            for i in range(self.n_total):
                if i in marked_idx:
                    seq[b, i] = self.MARKER  # marker token
                else:
                    seq[b, i] = all_tokens[i]

            # Place actual marked values right after their markers
            # (Simplified: use markers as positional, values interleaved)
            # Actually, simpler approach: marked positions get MARKER token,
            # the target is the original values at those positions
            marked_values = all_tokens[marked_idx]

            trigger_pos = self.n_total + self.T
            seq[b, trigger_pos] = self.TRIGGER
            target[b, trigger_pos + 1:trigger_pos + 1 + self.n_marked] = marked_values

        return seq, target


# ═══════════════════════════════════════════════════════════════════════
#  TRAINING
# ═══════════════════════════════════════════════════════════════════════

def train_benchmark(model_type: str = 'circumpunct',
                    problem_type: str = 'copying',
                    T: int = 100, n_epochs: int = 300,
                    lr: float = 0.001, batch_size: int = 32,
                    d_model: int = 64, state_size: int = 16,
                    n_layers: int = 2,
                    verbose: bool = True):
    """
    Train on a benchmark and report accuracy.

    model_type: 'circumpunct' or 'standard'
    problem_type: 'copying' or 'selective'
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    if problem_type == 'copying':
        problem = CopyingProblem(T=T, batch_size=batch_size)
    else:
        problem = SelectiveCopyingProblem(T=T, batch_size=batch_size)

    if model_type == 'circumpunct':
        model = CircumpunctMambaModel(
            vocab_size=problem.total_tokens,
            d_model=d_model, state_size=state_size, n_layers=n_layers)
    else:
        model = MambaModel(
            vocab_size=problem.total_tokens,
            d_model=d_model, state_size=state_size, n_layers=n_layers)

    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    n_params = sum(p.numel() for p in model.parameters())

    if verbose:
        print(f"\n{'=' * 60}")
        print(f"  ⊙ {problem_type.title()} Problem Benchmark")
        print(f"  Model:      {model_type}")
        print(f"  Parameters: {n_params:,}")
        print(f"  T (gap):    {T}")
        print(f"  Seq length: {problem.seq_len}")
        print(f"  d_model:    {d_model}  state_size: {state_size}  layers: {n_layers}")
        print(f"  Device:     {device}")
        print(f"{'=' * 60}\n")

    if problem_type == 'copying':
        trigger_pos = 1 + problem.n_digits + T
        output_len = problem.n_digits
    else:
        trigger_pos = problem.n_total + T
        output_len = problem.n_marked

    best_acc = 0.0
    history = []
    nan_skips = 0

    for epoch in range(n_epochs):
        model.train()
        seq, target = problem.generate_batch(device)

        logits = model(seq)

        output_logits = logits[:, trigger_pos + 1:trigger_pos + 1 + output_len]
        output_target = target[:, trigger_pos + 1:trigger_pos + 1 + output_len]

        loss = F.cross_entropy(
            output_logits.reshape(-1, problem.total_tokens),
            output_target.reshape(-1))

        if torch.isnan(loss).item() or torch.isinf(loss).item():
            optimizer.zero_grad()
            nan_skips += 1
            continue

        optimizer.zero_grad()
        loss.backward()

        # NaN gradient guard
        has_nan = any(
            p.grad is not None and (torch.isnan(p.grad).any() or torch.isinf(p.grad).any())
            for p in model.parameters()
        )
        if has_nan:
            nan_skips += 1
            optimizer.zero_grad()
            continue

        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        # Evaluate
        model.eval()
        with torch.no_grad():
            eval_seq, eval_target = problem.generate_batch(device)
            eval_logits = model(eval_seq)
            eval_output = eval_logits[:, trigger_pos + 1:trigger_pos + 1 + output_len]
            eval_tgt = eval_target[:, trigger_pos + 1:trigger_pos + 1 + output_len]
            preds = eval_output.argmax(dim=-1)
            acc = (preds == eval_tgt).float().mean().item()
            if acc > best_acc:
                best_acc = acc

        history.append({'epoch': epoch, 'loss': loss.item(), 'acc': acc})

        if verbose and (epoch % 25 == 0 or epoch == n_epochs - 1):
            skip_str = f"  skip={nan_skips}" if nan_skips > 0 else ""
            print(f"  Epoch {epoch:4d}  loss={loss.item():.4f}"
                  f"  acc={acc:.3f}  best={best_acc:.3f}{skip_str}")

    return history, best_acc


# ═══════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import sys

    T = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    n_epochs = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    problem = sys.argv[3] if len(sys.argv) > 3 else 'copying'

    print("\n⊙ THE CIRCUMPUNCT MAMBA")
    print("  What is forgotten is not destroyed. It is compressed.\n")

    # Run both models
    print("\n" + "─" * 60)
    print("  STANDARD MAMBA (baseline)")
    print("─" * 60)
    std_history, std_best = train_benchmark(
        'standard', problem_type=problem, T=T, n_epochs=n_epochs)

    print("\n" + "─" * 60)
    print("  CIRCUMPUNCT MAMBA")
    print("─" * 60)
    circ_history, circ_best = train_benchmark(
        'circumpunct', problem_type=problem, T=T, n_epochs=n_epochs)

    print("\n" + "=" * 60)
    print(f"  RESULTS (T = {T}, problem = {problem})")
    print(f"  Standard Mamba best accuracy:    {std_best:.3f}")
    print(f"  Circumpunct Mamba best accuracy: {circ_best:.3f}")
    param_std = sum(p.numel() for p in MambaModel(13, 64, 16, 2).parameters())
    param_circ = sum(p.numel() for p in CircumpunctMambaModel(13, 64, 16, 2).parameters())
    print(f"  Parameter ratio:                 {param_circ/param_std:.2f}x")
    print("=" * 60)
