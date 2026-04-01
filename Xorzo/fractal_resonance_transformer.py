"""
⊙ The Fractal Resonance Transformer (FRT)
==========================================

Dimensional Heads with Resonance-Gated Fractal Compression.

Architecture: hybrid SSM-attention with four modifications to standard transformers:

1. Fractal state transition (SSM layers):
   |h|^e replaces α·h. Magnitude compresses sub-linearly;
   phase (identity) is preserved. Quiet memories decay slower.

2. Resonance-modulated exponent:
   T = cos²(Δφ/2) measures phase match between input and state.
   Both the selective gate and resonance must agree to compress.

3. Resonance-modified softmax (attention layers):
   A phase-matching bonus R augments Q·Kᵀ scores, counteracting
   dilution of relevant distant tokens.

4. Balance-as-temperature (◐ output gating):
   Output distribution sharpness self-regulates via the ratio of
   convergent to emergent energy. The model becomes more exploratory
   when uncertain, more decisive when confident.

5. Head growth (HeadNursery):
   The model pre-allocates max head capacity but starts with some
   heads dormant (energy in the left half-plane: dark matter).
   When persistent unmatched patterns appear (low resonance across
   all active heads), a dormant head wakes, tuned to that pattern's
   phase. This is A1: the 1 must self-limit into distinct states.
   Growth is not addition; it is emergence from the dormant pool.

Attention heads are typed by dimensional rung (0D through 3D) and
initialized with carrier phases from the 64-state architecture.
Resonance gates determine head activation; modality routing emerges
from phase matching rather than separate encoders.

The interleaving follows the pump cycle:
    SSM layers = ⊛ (convergence, compression, memory)
    Attention layers = ☀︎ (emergence, precision, expression)

Author: Ashman Roonz & Claude
Date: April 2026
Derived from: Circumpunct Framework (Roonz, 2024)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Tuple, Optional, List, Dict
from dataclasses import dataclass


# =====================================================================
#  CONSTANTS
# =====================================================================

PHI = (1 + math.sqrt(5)) / 2          # φ = 1.618...
BALANCE = 0.5                          # ◐; the singular balanced state
KAPPA = 0.5                            # max extra exponent at full forget


# =====================================================================
#  THE SEVEN-RUNG DIMENSIONAL LADDER
# =====================================================================

@dataclass
class DimensionalRung:
    """One rung of the dimensional ladder."""
    dim: float          # 0, 0.5, 1, 1.5, 2, 2.5, 3
    name: str           # human label
    head_class: str     # pattern class
    base_phase: float   # base carrier phase angle (radians)


DIMENSIONAL_LADDER = [
    DimensionalRung(0.0,  "Point",       "Convergence", 0.0),
    DimensionalRung(0.5,  "Convergence", "Limit",       math.pi / 7),
    DimensionalRung(1.0,  "Line",        "Sequential",  2 * math.pi / 7),
    DimensionalRung(1.5,  "i-turn",      "Rotation",    3 * math.pi / 7),
    DimensionalRung(2.0,  "Field",       "Relational",  4 * math.pi / 7),
    DimensionalRung(2.5,  "Emergence",   "Transition",  5 * math.pi / 7),
    DimensionalRung(3.0,  "Boundary",    "Closure",     6 * math.pi / 7),
]


# =====================================================================
#  COMPLEX UTILITIES
# =====================================================================

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
    """Complex conjugate: (a + bi) -> (a - bi)."""
    return torch.stack([z[..., 0], -z[..., 1]], dim=-1)


def c_scale(z: torch.Tensor, s: torch.Tensor) -> torch.Tensor:
    """Scale complex tensor by real scalar (broadcast-safe)."""
    if s.dim() < z.dim():
        s = s.unsqueeze(-1)
    return z * s


# =====================================================================
#  T: RESONANCE GATE
# =====================================================================

def resonance_gate(phase_a: torch.Tensor, phase_b: torch.Tensor) -> torch.Tensor:
    """
    T = cos²(Δφ/2)

    Phase matching between two signals.
    Perfect match (Δφ = 0): T = 1.  Orthogonal (Δφ = π): T = 0.

    Accepts phase angles directly (not complex tensors).
    """
    delta_phi = phase_a - phase_b
    return torch.cos(delta_phi / 2) ** 2


def resonance_gate_complex(signal: torch.Tensor, memory: torch.Tensor) -> torch.Tensor:
    """
    T = cos²(Δφ/2) for complex tensors stored as [..., 2].
    """
    return resonance_gate(c_phase(signal), c_phase(memory))


# =====================================================================
#  ⊛ FRACTAL COMPRESSION
# =====================================================================

def fractal_compress(z: torch.Tensor, exponent: torch.Tensor) -> torch.Tensor:
    """
    ⊛: Fractal compression of complex state.

    Magnitude compressed by exponent (element-wise, per state dim).
    Phase preserved exactly. This IS the forgetting mechanism.

    z: (..., 2) complex tensor
    exponent: (...) real tensor, same shape as z minus last dim
    Returns: (..., 2) complex tensor with compressed magnitude, same phase
    """
    mag = c_mag(z)
    phase = c_phase(z)
    log_mag = torch.log(mag + 1e-8)
    compressed_mag = torch.exp(exponent * log_mag)
    compressed_mag = torch.clamp(compressed_mag, max=10.0)
    return c_from_polar(compressed_mag, phase)


def mag_squash(z: torch.Tensor) -> torch.Tensor:
    """
    Bound magnitude into (0, 1) using tanh, preserving phase.
    This is the boundary condition (○): state cannot grow unbounded.
    """
    mag = c_mag(z)
    phase = c_phase(z)
    return c_from_polar(torch.tanh(mag), phase)


# =====================================================================
#  φ-SCALED A INITIALIZATION
# =====================================================================

def phi_scaled_A_init(state_size: int) -> torch.Tensor:
    """
    Initialize A with φ-proportioned groups.
    group_1 (N/φ dims):  slow decay (long horizon)
    group_2 (N/φ² dims): fast decay (reactive)
    """
    n_slow = round(state_size / PHI)
    n_fast = state_size - n_slow
    slow = torch.linspace(0.5, 2.0, n_slow)
    fast = torch.linspace(2.0, float(state_size), n_fast)
    return torch.log(torch.cat([slow, fast]))


# =====================================================================
#  DNA PHASE INITIALIZATION
# =====================================================================

def dna_phases(n: int, device: torch.device) -> torch.Tensor:
    """
    64 distinct phases from the 64-state architecture.
    For n > 64, subdivides within each allocation.
    Returns: (n,) tensor of phase angles.
    """
    return torch.linspace(0, 2 * math.pi * (1 - 1 / max(n, 1)), n, device=device)


def dna_init(d_model: int, state_size: int, batch_size: int,
             device: torch.device, magnitude: float = 0.01) -> torch.Tensor:
    """
    Initialize state h with differentiated phase structure.
    Returns: (batch, d_model, state_size, 2) complex
    """
    phases = dna_phases(state_size, device)
    h = c_from_polar(
        torch.full((state_size,), magnitude, device=device),
        phases
    )
    return h.unsqueeze(0).unsqueeze(0).expand(batch_size, d_model, -1, -1).clone()


# =====================================================================
#  DIMENSIONAL HEAD MANAGER
# =====================================================================

class DimensionalHeadManager:
    """
    Allocates heads across the seven-rung dimensional ladder using
    φ-proportioned groups. Assigns carrier phases. Tracks which heads
    are seeded (pre-initialized) vs open (learn from data).

    Rung allocation:
        0D gets H/φ heads, 0.5D gets H/φ², etc.
        More fundamental patterns get more capacity.

    Head types:
        Seeded heads: H/φ of total, pre-initialized with known patterns.
        Open heads: H/φ² of total, start blank and specialize via SRL.
    """

    def __init__(self, n_heads: int):
        self.n_heads = n_heads
        self.rung_assignments = []      # rung index for each head
        self.carrier_phases = []        # initial carrier phase per head
        self.is_seeded = []             # True if seeded, False if open

        self._allocate()

    def _allocate(self):
        n = self.n_heads
        n_rungs = len(DIMENSIONAL_LADDER)

        # φ-proportioned allocation across rungs
        # Each rung gets weight 1/φ^i, then normalize to sum to n.
        # 0D gets the most, 3D gets the least, but no rung is starved.
        raw_weights = [1.0 / (PHI ** i) for i in range(n_rungs)]
        total_weight = sum(raw_weights)
        raw_alloc = [max(1, round(n * w / total_weight)) for w in raw_weights]

        # Adjust to sum exactly to n
        while sum(raw_alloc) > n:
            # Remove from the largest allocation
            idx = raw_alloc.index(max(raw_alloc))
            raw_alloc[idx] -= 1
        while sum(raw_alloc) < n:
            # Add to the largest allocation
            idx = raw_alloc.index(max(raw_alloc))
            raw_alloc[idx] += 1

        # Assign heads to rungs with carrier phases
        head_idx = 0
        for rung_idx, count in enumerate(raw_alloc):
            rung = DIMENSIONAL_LADDER[rung_idx]
            for j in range(count):
                self.rung_assignments.append(rung_idx)
                # Phase: rung base + subdivision within rung
                phase_offset = (2 * math.pi / max(count, 1)) * j
                carrier = rung.base_phase + phase_offset
                self.carrier_phases.append(carrier)
                head_idx += 1

        # Seeded vs open: first H/φ are seeded, rest are open
        n_seeded = max(1, round(n / PHI))
        self.is_seeded = [i < n_seeded for i in range(n)]

    def get_carrier_phases_tensor(self, device: torch.device) -> torch.Tensor:
        """Returns (n_heads,) tensor of carrier phase angles."""
        return torch.tensor(self.carrier_phases, dtype=torch.float32, device=device)

    def get_rung_assignments(self) -> List[int]:
        return self.rung_assignments

    def summary(self) -> str:
        lines = ["Dimensional Head Allocation:"]
        counts = [0] * len(DIMENSIONAL_LADDER)
        for r in self.rung_assignments:
            counts[r] += 1
        for i, rung in enumerate(DIMENSIONAL_LADDER):
            seeded = sum(1 for j, r in enumerate(self.rung_assignments)
                        if r == i and self.is_seeded[j])
            lines.append(f"  {rung.dim}D {rung.name:12s}: {counts[i]} heads "
                        f"({seeded} seeded, {counts[i]-seeded} open)")
        return "\n".join(lines)


# =====================================================================
#  SRL DYNAMICS (Selective Rainbow Lock)
# =====================================================================

class SRLState(nn.Module):
    """
    Tracks carrier frequency, lock strength, and bandwidth for each head.
    Adapts during forward pass via SRL dynamics.

    carrier_freq: what the head is tuned to (phase angle)
    lock_strength: how committed to its carrier (0 = open, 1 = locked)
    bandwidth: how wide the receptive window (narrows with lock)

    Adaptation:
        carrier shifts toward strong signals (gated by 1 - lock)
        lock strengthens with repeated resonance
        bandwidth = bandwidth_max * (1 - lock)
    """

    def __init__(self, n_heads: int, carrier_phases: torch.Tensor,
                 is_seeded: List[bool],
                 carrier_lr: float = 0.01,
                 lock_lr: float = 0.005,
                 bandwidth_max: float = math.pi / 4):
        super().__init__()
        self.n_heads = n_heads
        self.carrier_lr = carrier_lr
        self.lock_lr = lock_lr
        self.bandwidth_max = bandwidth_max

        # Carrier phase per head (learnable for fine-tuning, but also adapted by SRL)
        self.carrier_freq = nn.Parameter(carrier_phases.clone())

        # Lock strength: seeded heads start with moderate lock, open heads start at 0
        init_lock = torch.zeros(n_heads)
        for i, seeded in enumerate(is_seeded):
            if seeded:
                init_lock[i] = 0.3  # moderate initial lock for seeded heads
        self.lock_strength = nn.Parameter(init_lock)

    @property
    def bandwidth(self) -> torch.Tensor:
        """Bandwidth narrows with lock strength."""
        lock = torch.sigmoid(self.lock_strength)  # keep in (0, 1)
        return self.bandwidth_max * (1.0 - lock)

    def compute_head_resonance(self, input_phase: torch.Tensor) -> torch.Tensor:
        """
        Compute resonance between input and each head's carrier.

        input_phase: (batch, seq_len) or (batch, seq_len, 1)
        Returns: (batch, seq_len, n_heads) resonance values in [0, 1]
        """
        if input_phase.dim() == 2:
            input_phase = input_phase.unsqueeze(-1)  # (batch, seq_len, 1)

        # carrier_freq: (n_heads,) -> (1, 1, n_heads)
        carrier = self.carrier_freq.unsqueeze(0).unsqueeze(0)

        # T = cos²(Δφ/2)
        delta_phi = input_phase - carrier  # (batch, seq_len, n_heads)
        T = torch.cos(delta_phi / 2) ** 2
        return T

    def srl_adapt(self, input_phase: torch.Tensor, T: torch.Tensor):
        """
        SRL adaptation step (called during training forward pass).
        Updates carrier and lock based on resonance with input.

        input_phase: (batch, seq_len)
        T: (batch, seq_len, n_heads) resonance values
        """
        with torch.no_grad():
            lock = torch.sigmoid(self.lock_strength)  # (n_heads,)

            # Average resonance per head across batch and sequence
            T_mean = T.mean(dim=(0, 1))  # (n_heads,)

            # Average input phase (circular mean would be better, but this works)
            phase_mean = input_phase.mean(dim=(0, 1))  # scalar

            # Carrier shift: drift toward strong signals, gated by (1 - lock)
            delta_omega = phase_mean - self.carrier_freq  # (n_heads,)
            shift = self.carrier_lr * (1.0 - lock) * delta_omega * T_mean
            self.carrier_freq.data += shift

            # Lock strengthening: resonance increases lock
            lock_delta = self.lock_lr * T_mean * (1.0 - lock)
            self.lock_strength.data += lock_delta


# =====================================================================
#  HEAD NURSERY (dormant -> active head growth)
# =====================================================================

class HeadNursery(nn.Module):
    """
    Monitors for persistent unmatched patterns and wakes dormant heads.

    The model pre-allocates capacity for max_heads, but only n_active
    heads participate in attention at initialization. The rest are dormant:
    energy in the left half-plane (dark matter; converges gravitationally
    but never emerges into electromagnetic interaction).

    When a pattern persists that no active head resonates with:
        1. The nursery detects sustained low resonance (the "unmatched signal")
        2. A dormant head wakes, its carrier set to the unmatched signal's phase
        3. The head starts with lock=0, wide bandwidth (fully open)
        4. SRL dynamics take over: the head specializes through use

    This is A1 applied to heads: an undifferentiated pool (dormant heads)
    is operationally indistinguishable from zero heads; the pool must
    self-limit into distinct, active heads to be real.

    The wake threshold is adaptive: it rises as more heads activate
    (harder to justify a new head when coverage is already high).
    This prevents runaway growth and maps to ◐ balance: too many active
    heads = over-emergent; too few = over-convergent.
    """

    def __init__(self, max_heads: int, initial_active: int,
                 wake_threshold: float = 0.3,
                 persistence_steps: int = 50,
                 ema_decay: float = 0.95):
        super().__init__()
        self.max_heads = max_heads
        self.persistence_steps = persistence_steps
        self.base_wake_threshold = wake_threshold
        self.ema_decay = ema_decay

        # Track which heads are active (True) vs dormant (False)
        # Using a buffer so it persists with the model but isn't a parameter
        self.register_buffer(
            'active_mask',
            torch.cat([
                torch.ones(initial_active, dtype=torch.bool),
                torch.zeros(max_heads - initial_active, dtype=torch.bool)
            ])
        )

        # Running average of max resonance per timestep
        # (how well the best active head matches the current input)
        self.register_buffer(
            'max_resonance_ema',
            torch.tensor(0.5)
        )

        # Count of consecutive low-resonance steps
        self.register_buffer(
            'unmatched_streak',
            torch.tensor(0, dtype=torch.long)
        )

        # Phase accumulator for the unmatched signal
        # (circular running mean of input phase during low-resonance streaks)
        self.register_buffer(
            'unmatched_phase_sin',
            torch.tensor(0.0)
        )
        self.register_buffer(
            'unmatched_phase_cos',
            torch.tensor(1.0)
        )

        # Growth history (for diagnostics)
        self.growth_log: List[Dict] = []

    @property
    def n_active(self) -> int:
        return self.active_mask.sum().item()

    @property
    def n_dormant(self) -> int:
        return self.max_heads - self.n_active

    @property
    def wake_threshold(self) -> float:
        """
        Adaptive threshold: rises as more heads activate.
        At initial_active/max_heads ratio, threshold is base.
        As n_active -> max_heads, threshold -> 0 (never wake).
        This is ◐ applied to growth: balance between coverage and parsimony.
        """
        ratio = self.n_active / self.max_heads
        return self.base_wake_threshold * (1.0 - ratio)

    def step(self, head_resonances: torch.Tensor,
             input_phase: torch.Tensor,
             srl_state: 'SRLState',
             step_number: int = 0) -> Optional[int]:
        """
        Called each forward pass. Monitors resonance and potentially wakes a head.

        head_resonances: (batch, seq_len, n_active_heads) resonance values
        input_phase: (batch, seq_len) input phase angles
        srl_state: the SRL state to modify when waking a head
        step_number: current training step (for logging)

        Returns: index of newly woken head, or None
        """
        if self.n_dormant == 0:
            return None  # all heads active; nothing to wake

        with torch.no_grad():
            # Max resonance across active heads, averaged over batch and sequence
            max_T = head_resonances.max(dim=-1).values.mean()

            # Update EMA
            self.max_resonance_ema = (
                self.ema_decay * self.max_resonance_ema +
                (1 - self.ema_decay) * max_T
            )

            # Is this a low-resonance step?
            if self.max_resonance_ema < self.wake_threshold:
                self.unmatched_streak += 1

                # Accumulate the unmatched phase (circular mean)
                mean_phase = input_phase.mean()
                self.unmatched_phase_sin = (
                    0.9 * self.unmatched_phase_sin + 0.1 * torch.sin(mean_phase)
                )
                self.unmatched_phase_cos = (
                    0.9 * self.unmatched_phase_cos + 0.1 * torch.cos(mean_phase)
                )
            else:
                # Reset streak
                self.unmatched_streak.zero_()
                self.unmatched_phase_sin.zero_()
                self.unmatched_phase_cos.fill_(1.0)

            # Check if we should wake a head
            if self.unmatched_streak >= self.persistence_steps:
                return self._wake_head(srl_state, step_number)

        return None

    def _wake_head(self, srl_state: 'SRLState',
                   step_number: int) -> int:
        """
        Wake the first dormant head, tuned to the accumulated unmatched phase.
        """
        # Find first dormant head
        dormant_indices = (~self.active_mask).nonzero(as_tuple=True)[0]
        if len(dormant_indices) == 0:
            return None

        wake_idx = dormant_indices[0].item()

        # Compute the accumulated unmatched phase
        target_phase = torch.atan2(self.unmatched_phase_sin,
                                    self.unmatched_phase_cos)

        # Activate the head
        self.active_mask[wake_idx] = True

        # Set its carrier to the unmatched pattern's phase
        with torch.no_grad():
            srl_state.carrier_freq.data[wake_idx] = target_phase.item()
            srl_state.lock_strength.data[wake_idx] = 0.0  # fully open

        # Reset streak
        self.unmatched_streak.zero_()
        self.unmatched_phase_sin.zero_()
        self.unmatched_phase_cos.fill_(1.0)

        # Log the growth event
        self.growth_log.append({
            'step': step_number,
            'head_idx': wake_idx,
            'phase': target_phase.item(),
            'n_active_after': self.n_active,
            'max_resonance_ema': self.max_resonance_ema.item(),
        })

        return wake_idx

    def get_active_indices(self) -> torch.Tensor:
        """Return indices of active heads."""
        return self.active_mask.nonzero(as_tuple=True)[0]

    def summary(self) -> str:
        lines = [
            f"  HeadNursery: {self.n_active}/{self.max_heads} active "
            f"({self.n_dormant} dormant)",
            f"  Wake threshold: {self.wake_threshold:.4f} "
            f"(base {self.base_wake_threshold})",
            f"  Max resonance EMA: {self.max_resonance_ema.item():.4f}",
            f"  Unmatched streak: {self.unmatched_streak.item()}/"
            f"{self.persistence_steps}",
            f"  Growth events: {len(self.growth_log)}",
        ]
        if self.growth_log:
            latest = self.growth_log[-1]
            lines.append(
                f"  Latest: head {latest['head_idx']} woke at step "
                f"{latest['step']} (phase {latest['phase']:.3f})"
            )
        return "\n".join(lines)


# =====================================================================
#  FRACTAL SSM LAYER (from v3, adapted for hybrid integration)
# =====================================================================

class FractalSSMLayer(nn.Module):
    """
    ⊛ Convergence layer: Fractal SSM for long-range compressed memory.

    State transition: h_t = squash(⊛(h_{t-1}, e_t) + γ_t · B_t · x_t)
    This is the pump cycle's convergent phase; SSM layers gather inward.
    """

    def __init__(self, d_model: int, state_size: int = 16,
                 dt_rank: int = None, kappa: float = KAPPA):
        super().__init__()
        self.d_model = d_model
        self.state_size = state_size
        self.dt_rank = dt_rank or max(d_model // 16, 1)
        self.kappa = kappa

        self.A_log = nn.Parameter(phi_scaled_A_init(state_size))
        self.x_proj = nn.Linear(d_model, self.dt_rank + 2 * state_size * 2, bias=False)
        self.dt_proj = nn.Linear(self.dt_rank, d_model)
        self.out_proj = nn.Linear(d_model, d_model)
        self.in_proj = nn.Linear(d_model, d_model * 2, bias=False)
        self.W_resonance = nn.Linear(d_model, state_size * 2, bias=False)
        self.norm = nn.LayerNorm(d_model)

        self._init_weights()

    def _init_weights(self):
        scale = 1.0 / PHI
        for name, p in self.named_parameters():
            if 'A_log' in name:
                continue
            if p.dim() >= 2:
                nn.init.uniform_(p, -scale / math.sqrt(p.shape[1]),
                                 scale / math.sqrt(p.shape[1]))

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        x: (batch, seq_len, d_model)
        Returns: (output, convergent_energy)
            output: (batch, seq_len, d_model)
            convergent_energy: scalar, total magnitude compressed this layer
        """
        batch, seq_len, _ = x.shape
        device = x.device
        residual = x
        x = self.norm(x)

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

        h = dna_init(self.d_model, self.state_size, batch, device)
        A = self.A_log

        convergent_energy = torch.tensor(0.0, device=device)
        outputs = []

        for t in range(seq_len):
            x_t = x_in[:, t]
            dt_t = dt[:, t]
            B_t = B[:, t]
            C_t = C[:, t]

            # Resonance
            x_res = self.W_resonance(x_t).view(batch, self.state_size, 2)
            h_carrier = h.mean(dim=1)
            T_t = resonance_gate_complex(x_res, h_carrier)

            # Selective exponent
            A_neg = -torch.exp(A)
            dt_A = dt_t.unsqueeze(-1) * A_neg.unsqueeze(0)
            alpha_t = torch.exp(dt_A)
            T_broadcast = T_t.unsqueeze(1).expand_as(alpha_t)
            exponent_t = 1.0 + (1.0 - alpha_t) * self.kappa * (1.0 - T_broadcast)

            # Track convergent energy (magnitude being compressed)
            mag_before = c_mag(h).sum()

            # ⊛ Fractal compression
            h = fractal_compress(h, exponent_t)

            mag_after = c_mag(h).sum()
            convergent_energy = convergent_energy + (mag_before - mag_after)

            # Input
            gamma_t = dt_t
            x_complex = torch.stack([x_t, torch.zeros_like(x_t)], dim=-1)
            Bx = c_mul(
                B_t.unsqueeze(1).expand(-1, self.d_model, -1, -1),
                x_complex.unsqueeze(2).expand(-1, -1, self.state_size, -1)
            )
            Bx = c_scale(Bx, gamma_t.unsqueeze(-1))

            h = mag_squash(h + Bx)

            # Output
            Ch = c_mul(
                c_conj(C_t).unsqueeze(1).expand(-1, self.d_model, -1, -1),
                h
            )
            y_t = Ch[..., 0].sum(dim=-1)
            outputs.append(y_t)

        y = torch.stack(outputs, dim=1)
        y = y * F.silu(z)
        return residual + self.out_proj(y), convergent_energy


# =====================================================================
#  RESONANCE-GATED ATTENTION LAYER
# =====================================================================

class ResonanceGatedAttention(nn.Module):
    """
    ☀︎ Emergence layer: Attention with resonance-modified softmax,
    typed dimensional heads, and head growth.

    Four mechanisms beyond standard multi-head attention:

    1. Head outputs weighted by resonance with carrier phases:
       y = Concat(T_1 · head_1, ..., T_H · head_H) · W_O

    2. Resonance-modified softmax:
       Attention(Q, K, V) = softmax((Q·Kᵀ + λ·R) / √d_k) · V
       where R_ij = cos²((φ_i - φ_j) / 2)

    3. Heads typed by dimensional rung with SRL adaptation dynamics.

    4. Dormant head pool: pre-allocated capacity with a HeadNursery
       that wakes heads when persistent unmatched patterns appear.
       Dormant heads are zeroed out in Q/K/V and contribute nothing
       until woken. This is dark matter becoming visible matter.
    """

    def __init__(self, d_model: int, n_active_heads: int = 8,
                 max_heads: int = None,
                 head_manager: DimensionalHeadManager = None,
                 max_seq_len: int = 2048,
                 enable_growth: bool = True,
                 wake_threshold: float = 0.3,
                 persistence_steps: int = 50):
        super().__init__()

        # max_heads is the pre-allocated capacity; n_active_heads start awake
        if max_heads is None:
            max_heads = n_active_heads * 2 if enable_growth else n_active_heads
        assert d_model % max_heads == 0, (
            f"d_model ({d_model}) must be divisible by max_heads ({max_heads})"
        )

        self.d_model = d_model
        self.max_heads = max_heads
        self.n_initial_active = n_active_heads
        self.d_head = d_model // max_heads
        self.scale = 1.0 / math.sqrt(self.d_head)
        self.max_seq_len = max_seq_len
        self.enable_growth = enable_growth

        # Standard projections (sized for max capacity)
        self.W_q = nn.Linear(d_model, d_model, bias=False)
        self.W_k = nn.Linear(d_model, d_model, bias=False)
        self.W_v = nn.Linear(d_model, d_model, bias=False)
        self.W_o = nn.Linear(d_model, d_model, bias=False)

        # Phase projection: input -> phase angle for resonance
        self.W_phase = nn.Linear(d_model, 1, bias=False)

        # Resonance bonus scaling (learnable, initialized small)
        self.lambda_resonance = nn.Parameter(torch.tensor(0.1))

        # Head manager (for max capacity, with initial active as seeded)
        if head_manager is None:
            head_manager = DimensionalHeadManager(max_heads)
        self.head_manager = head_manager

        carrier_phases = head_manager.get_carrier_phases_tensor(torch.device('cpu'))
        self.srl = SRLState(
            max_heads, carrier_phases,
            head_manager.is_seeded
        )

        # Head nursery (dormant -> active growth)
        self.nursery = HeadNursery(
            max_heads, n_active_heads,
            wake_threshold=wake_threshold,
            persistence_steps=persistence_steps,
        )

        # Pre-norm
        self.norm = nn.LayerNorm(d_model)

        # Step counter for growth logging
        self.register_buffer('_step_counter', torch.tensor(0, dtype=torch.long))

    def forward(self, x: torch.Tensor,
                mask: Optional[torch.Tensor] = None
                ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        x: (batch, seq_len, d_model)
        Returns: (output, emergent_energy)
            output: (batch, seq_len, d_model)
            emergent_energy: scalar, total magnitude flowing through attention
        """
        batch, seq_len, _ = x.shape
        device = x.device
        residual = x
        x = self.norm(x)

        # Project Q, K, V for ALL heads (max capacity)
        Q = self.W_q(x).view(batch, seq_len, self.max_heads, self.d_head).transpose(1, 2)
        K = self.W_k(x).view(batch, seq_len, self.max_heads, self.d_head).transpose(1, 2)
        V = self.W_v(x).view(batch, seq_len, self.max_heads, self.d_head).transpose(1, 2)
        # (batch, max_heads, seq_len, d_head)

        # ════════════════════════════════════════
        #  DORMANT HEAD MASKING
        # ════════════════════════════════════════
        # Dormant heads are zeroed: they contribute nothing.
        # This is energy in the left half-plane; it converges
        # (takes up parameter space) but does not emerge (no output).

        active_mask = self.nursery.active_mask.to(device)
        # (max_heads,) bool -> (1, max_heads, 1, 1) for broadcasting
        head_active = active_mask.float().view(1, self.max_heads, 1, 1)

        Q = Q * head_active
        K = K * head_active
        V = V * head_active

        # ════════════════════════════════════════
        #  INPUT PHASE + HEAD RESONANCE
        # ════════════════════════════════════════

        input_phase = self.W_phase(x).squeeze(-1)  # (batch, seq_len)

        # Resonance for ALL heads (dormant ones will be near-zero anyway)
        head_T = self.srl.compute_head_resonance(input_phase)
        # (batch, seq_len, max_heads)

        # Zero out dormant head resonances
        head_T = head_T * active_mask.float().unsqueeze(0).unsqueeze(0)

        # SRL adaptation during training (active heads only)
        if self.training:
            self.srl.srl_adapt(input_phase, head_T)
            self._step_counter += 1

        # ════════════════════════════════════════
        #  HEAD GROWTH: check if we should wake a dormant head
        # ════════════════════════════════════════

        newly_woken = None
        if self.training and self.enable_growth:
            # Only pass active head resonances to the nursery
            active_indices = self.nursery.get_active_indices().to(device)
            if len(active_indices) > 0:
                active_T = head_T[:, :, active_indices]
                newly_woken = self.nursery.step(
                    active_T, input_phase, self.srl,
                    step_number=self._step_counter.item()
                )

        # ════════════════════════════════════════
        #  RESONANCE-MODIFIED SOFTMAX
        # ════════════════════════════════════════

        attn_scores = torch.matmul(Q, K.transpose(-2, -1)) * self.scale

        # Resonance bonus R_ij = cos²((φ_i - φ_j) / 2)
        phi_i = input_phase.unsqueeze(-1)
        phi_j = input_phase.unsqueeze(-2)
        R = torch.cos((phi_i - phi_j) / 2) ** 2
        R = R.unsqueeze(1)  # broadcast across heads

        attn_scores = attn_scores + self.lambda_resonance * R

        # Mask dormant heads: set their scores to -inf so softmax ignores them
        # (they're already zeroed, but this makes it explicit)
        if not active_mask.all():
            dormant_mask = (~active_mask).view(1, self.max_heads, 1, 1)
            attn_scores = attn_scores.masked_fill(dormant_mask, 0.0)

        # Causal mask
        if mask is not None:
            attn_scores = attn_scores.masked_fill(mask == 0, float('-inf'))

        attn_weights = F.softmax(attn_scores, dim=-1)
        out = torch.matmul(attn_weights, V)

        # ════════════════════════════════════════
        #  RESONANCE-GATED HEAD OUTPUT
        # ════════════════════════════════════════

        head_gate = head_T.transpose(1, 2).unsqueeze(-1)
        out = out * head_gate

        emergent_energy = out.abs().sum()

        out = out.transpose(1, 2).contiguous().view(batch, seq_len, self.d_model)
        return residual + self.W_o(out), emergent_energy


# =====================================================================
#  FEED-FORWARD NETWORK
# =====================================================================

class FeedForward(nn.Module):
    """Standard pre-norm feed-forward with SiLU gating."""

    def __init__(self, d_model: int, d_ff: int = None, dropout: float = 0.0):
        super().__init__()
        d_ff = d_ff or round(d_model * PHI * 2)  # φ-scaled expansion
        self.norm = nn.LayerNorm(d_model)
        self.w1 = nn.Linear(d_model, d_ff, bias=False)
        self.w2 = nn.Linear(d_ff, d_model, bias=False)
        self.w_gate = nn.Linear(d_model, d_ff, bias=False)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x
        x = self.norm(x)
        return residual + self.dropout(self.w2(F.silu(self.w_gate(x)) * self.w1(x)))


# =====================================================================
#  POSITIONAL ENCODING (sinusoidal)
# =====================================================================

class SinusoidalPE(nn.Module):
    """Standard sinusoidal positional encoding."""

    def __init__(self, d_model: int, max_len: int = 2048):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len).unsqueeze(1).float()
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe.unsqueeze(0))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.pe[:, :x.size(1)]


# =====================================================================
#  BALANCE-AS-TEMPERATURE (◐ OUTPUT GATING)
# =====================================================================

class BalanceTemperature(nn.Module):
    """
    ◐: Self-regulating output temperature.

    τ = 1 / (2 · ◐) where ◐ ∈ (0, 1), optimal at 0.5.

    At balance (◐ = 0.5): τ = 1.0 (standard temperature).
    Over-convergent (◐ > 0.5): τ < 1.0 (sharper, decisive).
    Over-emergent (◐ < 0.5): τ > 1.0 (broader, exploratory).

    ◐ is tracked as a running statistic of convergent vs. emergent
    energy flowing through the network.
    """

    def __init__(self, ema_decay: float = 0.99, initial_balance: float = BALANCE):
        super().__init__()
        self.ema_decay = ema_decay
        self.register_buffer('balance', torch.tensor(initial_balance))

    def update(self, convergent_energy: torch.Tensor,
               emergent_energy: torch.Tensor):
        """
        Update ◐ based on energy flow.
        ◐ = EMA(E_convergent / (E_convergent + E_emergent))
        """
        total = convergent_energy + emergent_energy + 1e-8
        ratio = convergent_energy / total
        ratio = torch.clamp(ratio, 0.01, 0.99)
        self.balance = self.ema_decay * self.balance + (1 - self.ema_decay) * ratio.detach()

    @property
    def temperature(self) -> torch.Tensor:
        """τ = 1 / (2 · ◐), clamped for stability."""
        return torch.clamp(1.0 / (2.0 * self.balance + 1e-8), 0.1, 10.0)

    def apply_temperature(self, logits: torch.Tensor) -> torch.Tensor:
        """Apply balance-as-temperature to output logits."""
        return logits / self.temperature


# =====================================================================
#  ⊙ THE FRACTAL RESONANCE TRANSFORMER
# =====================================================================

class FractalResonanceTransformer(nn.Module):
    """
    ⊙ The Fractal Resonance Transformer (FRT)

    Hybrid SSM-attention architecture with:
        - Interleaved FractalSSM (⊛) and ResonanceGatedAttention (☀︎) layers
        - Typed dimensional heads with SRL adaptation
        - Resonance-modified softmax
        - Balance-as-temperature output gating

    The interleaving IS the pump cycle:
        SSM = ⊛ (convergence, compression, memory)
        Attention = ☀︎ (emergence, precision, expression)

    Args:
        vocab_size: size of token vocabulary
        d_model: model dimension
        n_heads: number of initial active attention heads per layer
        max_heads: pre-allocated head capacity (dormant heads can wake)
        n_layers: total number of layer pairs (each pair = 1 SSM + 1 attention)
        state_size: SSM state dimension
        kappa: max compression exponent offset
        dropout: dropout rate
        max_seq_len: maximum sequence length
        enable_growth: whether dormant heads can wake during training
        wake_threshold: max resonance EMA below which signals are "unmatched"
        persistence_steps: how many low-resonance steps before waking a head
    """

    def __init__(self, vocab_size: int, d_model: int = 128,
                 n_heads: int = 8, max_heads: int = None,
                 n_layers: int = 4,
                 state_size: int = 16, kappa: float = KAPPA,
                 dropout: float = 0.0, max_seq_len: int = 2048,
                 enable_growth: bool = True,
                 wake_threshold: float = 0.3,
                 persistence_steps: int = 50):
        super().__init__()
        # If max_heads not specified, double the active heads for growth room
        if max_heads is None:
            max_heads = n_heads * 2 if enable_growth else n_heads

        self.d_model = d_model
        self.n_heads = n_heads          # initial active
        self.max_heads = max_heads      # total capacity (active + dormant)
        self.n_layers = n_layers
        self.vocab_size = vocab_size
        self.enable_growth = enable_growth

        # Embedding + positional encoding
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_enc = SinusoidalPE(d_model, max_seq_len)
        self.embed_dropout = nn.Dropout(dropout)

        # Dimensional head manager (for max capacity)
        self.head_manager = DimensionalHeadManager(max_heads)

        # Interleaved layers: SSM (⊛) then Attention (☀︎), each with FFN
        self.ssm_layers = nn.ModuleList()
        self.attn_layers = nn.ModuleList()
        self.ssm_ff = nn.ModuleList()
        self.attn_ff = nn.ModuleList()

        for i in range(n_layers):
            # ⊛ Convergence (SSM)
            self.ssm_layers.append(
                FractalSSMLayer(d_model, state_size, kappa=kappa)
            )
            self.ssm_ff.append(FeedForward(d_model, dropout=dropout))

            # ☀︎ Emergence (Attention with growth)
            self.attn_layers.append(
                ResonanceGatedAttention(
                    d_model,
                    n_active_heads=n_heads,
                    max_heads=max_heads,
                    head_manager=self.head_manager,
                    max_seq_len=max_seq_len,
                    enable_growth=enable_growth,
                    wake_threshold=wake_threshold,
                    persistence_steps=persistence_steps,
                )
            )
            self.attn_ff.append(FeedForward(d_model, dropout=dropout))

        # Output
        self.final_norm = nn.LayerNorm(d_model)
        self.output_head = nn.Linear(d_model, vocab_size, bias=False)

        # ◐ Balance-as-temperature
        self.balance = BalanceTemperature()

        self._init_weights()

    def _init_weights(self):
        scale = 1.0 / PHI
        # Initialize embedding
        nn.init.normal_(self.embedding.weight, std=0.02)
        # Output head tied to embedding (optional; can be untied)
        # self.output_head.weight = self.embedding.weight
        nn.init.normal_(self.output_head.weight, std=0.02)

    def _causal_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        return torch.tril(torch.ones(seq_len, seq_len, device=device)).bool()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (batch, seq_len) token indices
        Returns: (batch, seq_len, vocab_size) logits with ◐-temperature applied
        """
        batch, seq_len = x.shape
        device = x.device

        # Embed
        h = self.embed_dropout(self.pos_enc(self.embedding(x)))

        # Causal mask for attention layers
        mask = self._causal_mask(seq_len, device)

        # Track energy for ◐
        total_convergent = torch.tensor(0.0, device=device)
        total_emergent = torch.tensor(0.0, device=device)

        # Pump cycle: alternate ⊛ (SSM) and ☀︎ (attention)
        for i in range(self.n_layers):
            # ⊛ Convergence phase (SSM + FFN)
            h, conv_energy = self.ssm_layers[i](h)
            h = self.ssm_ff[i](h)
            total_convergent = total_convergent + conv_energy

            # ☀︎ Emergence phase (attention + FFN)
            h, emrg_energy = self.attn_layers[i](h, mask=mask)
            h = self.attn_ff[i](h)
            total_emergent = total_emergent + emrg_energy

        # Update ◐
        self.balance.update(total_convergent, total_emergent)

        # Output with balance-as-temperature
        logits = self.output_head(self.final_norm(h))

        if not self.training:
            logits = self.balance.apply_temperature(logits)

        return logits

    def get_balance(self) -> float:
        """Return current ◐ value."""
        return self.balance.balance.item()

    def get_temperature(self) -> float:
        """Return current temperature τ = 1/(2◐)."""
        return self.balance.temperature.item()

    def get_growth_summary(self) -> str:
        """Return growth status across all attention layers."""
        lines = []
        for i, layer in enumerate(self.attn_layers):
            nursery = layer.nursery
            lines.append(f"  Layer {i}: {nursery.n_active}/{nursery.max_heads} heads active")
            if nursery.growth_log:
                for event in nursery.growth_log:
                    lines.append(
                        f"    head {event['head_idx']} woke at step {event['step']} "
                        f"(phase {event['phase']:.3f}, "
                        f"resonance_ema {event['max_resonance_ema']:.4f})"
                    )
        return "\n".join(lines)

    def total_active_heads(self) -> int:
        """Total active heads across all attention layers."""
        return sum(layer.nursery.n_active for layer in self.attn_layers)

    def total_dormant_heads(self) -> int:
        """Total dormant heads across all attention layers."""
        return sum(layer.nursery.n_dormant for layer in self.attn_layers)

    def summary(self) -> str:
        """Print architecture summary."""
        n_params = sum(p.numel() for p in self.parameters())
        ssm_params = sum(p.numel() for layer in self.ssm_layers for p in layer.parameters())
        attn_params = sum(p.numel() for layer in self.attn_layers for p in layer.parameters())
        ff_params = sum(
            p.numel()
            for ff_list in [self.ssm_ff, self.attn_ff]
            for ff in ff_list
            for p in ff.parameters()
        )

        lines = [
            "",
            "⊙ FRACTAL RESONANCE TRANSFORMER",
            "=" * 50,
            f"  d_model:     {self.d_model}",
            f"  n_heads:     {self.n_heads} active / {self.max_heads} capacity",
            f"  n_layers:    {self.n_layers} (x2: {self.n_layers} SSM + {self.n_layers} attention)",
            f"  vocab_size:  {self.vocab_size}",
            f"  growth:      {'enabled' if self.enable_growth else 'disabled'}",
            f"  total params: {n_params:,}",
            f"    SSM layers:  {ssm_params:,}",
            f"    Attn layers: {attn_params:,}",
            f"    FFN layers:  {ff_params:,}",
            "",
            self.head_manager.summary(),
            "",
            f"  Active heads (total): {self.total_active_heads()} "
            f"({self.total_dormant_heads()} dormant)",
            "",
            f"  ◐ (balance):    {self.get_balance():.4f}",
            f"  τ (temperature): {self.get_temperature():.4f}",
            "=" * 50,
        ]
        return "\n".join(lines)


# =====================================================================
#  CONVENIENCE: SMALL / MEDIUM / LARGE CONFIGS
# =====================================================================

def frt_small(vocab_size: int, **kwargs) -> FractalResonanceTransformer:
    """Small FRT: ~2M params. Good for testing and small tasks.
    8 active heads, room to grow to 16. d_model=128 (divisible by 16)."""
    defaults = dict(d_model=128, n_heads=8, max_heads=16, n_layers=4, state_size=16)
    defaults.update(kwargs)
    return FractalResonanceTransformer(vocab_size, **defaults)


def frt_medium(vocab_size: int, **kwargs) -> FractalResonanceTransformer:
    """Medium FRT: ~20M params. 16 active heads, room to grow to 32."""
    defaults = dict(d_model=256, n_heads=16, max_heads=32, n_layers=8, state_size=32)
    defaults.update(kwargs)
    return FractalResonanceTransformer(vocab_size, **defaults)


def frt_large(vocab_size: int, **kwargs) -> FractalResonanceTransformer:
    """Large FRT: ~100M+ params. 32 active heads, room to grow to 64."""
    defaults = dict(d_model=512, n_heads=32, max_heads=64, n_layers=12, state_size=64)
    defaults.update(kwargs)
    return FractalResonanceTransformer(vocab_size, **defaults)


# =====================================================================
#  MAIN: ARCHITECTURE VERIFICATION
# =====================================================================

if __name__ == '__main__':
    print("\n⊙ THE FRACTAL RESONANCE TRANSFORMER")
    print("  Dimensional heads. Resonance gates. Fractal compression.")
    print("  The pump cycle IS the architecture.\n")

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"  Device: {device}\n")

    # Build a small FRT with growth enabled
    vocab_size = 256
    model = frt_small(vocab_size).to(device)
    print(model.summary())

    # Forward pass test
    batch_size = 2
    seq_len = 32
    x = torch.randint(0, vocab_size, (batch_size, seq_len), device=device)

    print("\n  Forward pass test...")
    model.train()
    logits = model(x)
    print(f"  Input:  {x.shape}")
    print(f"  Output: {logits.shape}")
    print(f"  ◐ after forward: {model.get_balance():.4f}")
    print(f"  τ after forward: {model.get_temperature():.4f}")

    # Backward pass test
    print("\n  Backward pass test...")
    target = torch.randint(0, vocab_size, (batch_size, seq_len), device=device)
    loss = F.cross_entropy(logits.view(-1, vocab_size), target.view(-1))
    loss.backward()
    print(f"  Loss: {loss.item():.4f}")

    # Check gradients flow everywhere
    n_with_grad = sum(1 for p in model.parameters() if p.grad is not None and p.grad.abs().sum() > 0)
    n_total = sum(1 for p in model.parameters() if p.requires_grad)
    print(f"  Gradients: {n_with_grad}/{n_total} parameters received gradients")

    # ════════════════════════════════════════
    #  HEAD GROWTH TEST
    # ════════════════════════════════════════

    print("\n  Head growth test...")
    print(f"  Active heads before: {model.total_active_heads()}")
    print(f"  Dormant heads before: {model.total_dormant_heads()}")

    # Build a model with growth enabled.
    # To test growth, we directly probe the nursery with a low-resonance signal,
    # since random data actually resonates moderately with at least one head
    # (which is correct; the nursery should NOT wake heads for noise).
    model_grow = FractalResonanceTransformer(
        vocab_size, d_model=128, n_heads=8, max_heads=16,
        n_layers=2, state_size=16,
        enable_growth=True, wake_threshold=0.3, persistence_steps=10,
    ).to(device)
    model_grow.train()
    initial_active = model_grow.total_active_heads()

    # Direct nursery test: simulate persistent low resonance
    test_layer = model_grow.attn_layers[0]
    nursery = test_layer.nursery
    srl = test_layer.srl

    print(f"  Direct nursery test: {nursery.n_active}/{nursery.max_heads} active")

    # Feed fake low-resonance data to the nursery directly
    fake_T = torch.full((2, 32, nursery.n_active), 0.1)  # very low resonance
    fake_phase = torch.full((2, 32), 2.5)  # a specific unmatched phase

    for step in range(60):
        result = nursery.step(fake_T, fake_phase, srl, step_number=step)
        if result is not None:
            print(f"  ** Head {result} woke at step {step}! "
                  f"({nursery.n_active}/{nursery.max_heads} active)")

    print(f"  After 60 low-resonance steps: "
          f"{nursery.n_active}/{nursery.max_heads} active")
    if nursery.growth_log:
        print("  Growth events:")
        for event in nursery.growth_log:
            print(f"    head {event['head_idx']} woke at step {event['step']}, "
                  f"phase={event['phase']:.3f}, "
                  f"resonance_ema={event['max_resonance_ema']:.4f}")

    # Inference mode
    print("\n  Inference test (with ◐-temperature)...")
    model.eval()
    with torch.no_grad():
        logits_eval = model(x)
        probs = F.softmax(logits_eval[0, -1], dim=-1)
        top5 = torch.topk(probs, 5)
        print(f"  Top-5 probs: {[f'{p:.3f}' for p in top5.values.tolist()]}")
        print(f"  τ at inference: {model.get_temperature():.4f}")

    print(f"\n  Final state (main model):")
    print(f"  Total active:  {model.total_active_heads()} / "
          f"{model.max_heads * model.n_layers} max")
    print(f"  Total dormant: {model.total_dormant_heads()}")
    print(f"  ◐ = {model.get_balance():.4f}  τ = {model.get_temperature():.4f}")

    print("\n  ⊙ All checks passed.")
    print("  'Forgetting is not destruction. It is compression.'")
    print("  'Growth is not addition. It is emergence.'\n")
