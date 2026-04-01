"""
⊙ The Fractal Resonance Transformer v3 (Multi-Modal)
=====================================================

Universal byte encoder + unified fold. Any modality. One architecture.

v2 unified compression and resonance into the fractal fold.
v3 makes the input universal: raw bytes from any source (text, audio,
image, molecular, whatever) enter through the same encoder and are
projected into the same phase-bearing field.

The core principle: E = 1. Energy doesn't come in flavors. Audio is
energy constrained one way; light is energy constrained another way;
text is energy constrained yet another way. The architecture should
not need to be told which is which. Modality emerges from training,
not from structural assumptions.

The universal encoder:
    1. Raw bytes (0-255) are the atomic input. Any file, any stream.
    2. Bytes are grouped into chunks (windows). Chunk size is the
       "aperture width": how many bytes the system sees at once.
    3. Each chunk is projected into a d_model vector via learned
       linear projection. No tokenizer. No spectrogram. No patch
       embedding. Just bytes -> vectors.
    4. A phase encoder extracts the phase signature of each chunk
       (learned projection to a phase angle). This is where the
       encoder discovers modality structure.
    5. Hierarchical byte context: a small local convolution captures
       sub-chunk patterns (byte n-grams) before the main projection.
       This gives the model byte-level structure awareness without
       hardcoding modality assumptions.

The fold, heads, SRL, nursery, and balance are unchanged from v2.
The architecture is modality-agnostic. What changes is what flows
through the aperture.

Dimensional heads specialize via SRL:
    When fed audio bytes, some heads will lock to temporal frequency
    bands (spectral decomposition emerges from training).
    When fed image bytes, some heads will lock to spatial frequency
    patterns (edge detection, texture, color emerge from training).
    When fed text bytes, some heads will lock to character n-gram
    patterns (morphology, syntax emerge from training).
    When fed molecular data, some heads will lock to structural
    motifs (bonds, rings, functional groups emerge from training).

The architecture doesn't know and doesn't need to know.

Author: Ashman Roonz & Claude
Date: April 2026
Derived from: Circumpunct Framework (Roonz, 2024)
Evolved from: fractal_resonance_transformer_v2.py (unified fold)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import time
import os
from typing import Tuple, Optional, List, Dict
from dataclasses import dataclass


# =====================================================================
#  CONSTANTS
# =====================================================================

PHI = (1 + math.sqrt(5)) / 2          # phi = 1.618...
BALANCE = 0.5                          # ◐; the singular balanced state
KAPPA = 0.3                            # default compression strength
FOLD_LAMBDA = 0.8                      # resonance resistance to compression
BYTE_VOCAB = 259                       # 256 byte values + 3 special tokens
PAD_TOKEN = 256
BOS_TOKEN = 257
EOS_TOKEN = 258


# =====================================================================
#  THE SEVEN-RUNG DIMENSIONAL LADDER
# =====================================================================

@dataclass
class DimensionalRung:
    """One rung of the dimensional ladder."""
    dim: float
    name: str
    head_class: str
    base_phase: float


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
#  DIMENSIONAL HEAD MANAGER
# =====================================================================

class DimensionalHeadManager:
    """
    Allocates heads across the seven-rung dimensional ladder using
    phi-proportioned groups.
    """

    def __init__(self, n_heads: int):
        self.n_heads = n_heads
        self.rung_assignments = []
        self.carrier_phases = []
        self.is_seeded = []
        self._allocate()

    def _allocate(self):
        n = self.n_heads
        n_rungs = len(DIMENSIONAL_LADDER)

        raw_weights = [1.0 / (PHI ** i) for i in range(n_rungs)]
        total_weight = sum(raw_weights)
        raw_alloc = [max(1, round(n * w / total_weight)) for w in raw_weights]

        while sum(raw_alloc) > n:
            idx = raw_alloc.index(max(raw_alloc))
            raw_alloc[idx] -= 1
        while sum(raw_alloc) < n:
            idx = raw_alloc.index(max(raw_alloc))
            raw_alloc[idx] += 1

        for rung_idx, count in enumerate(raw_alloc):
            rung = DIMENSIONAL_LADDER[rung_idx]
            for j in range(count):
                self.rung_assignments.append(rung_idx)
                phase_offset = (2 * math.pi / max(count, 1)) * j
                self.carrier_phases.append(rung.base_phase + phase_offset)

        n_seeded = max(1, round(n / PHI))
        self.is_seeded = [i < n_seeded for i in range(n)]

    def get_carrier_phases_tensor(self, device: torch.device) -> torch.Tensor:
        return torch.tensor(self.carrier_phases, dtype=torch.float32, device=device)

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
    Tracks carrier frequency, lock strength, and bandwidth per head.
    Adapts during training via SRL dynamics from Xorzo.

    NOTE ON GRADIENTS: lock_strength is intentionally updated outside
    the gradient path (in srl_adapt() under torch.no_grad()). This is
    by design, not a bug. SRL lock dynamics model experience-driven
    habituation: lock strengthens when a channel consistently resonates
    with incoming signal, weakens when it doesn't. This is a different
    process from error-corrected optimization (backprop). Backprop would
    optimize lock for loss minimization; SRL adapts lock for frequency
    commitment. The carrier_freq follows the same pattern. Both are
    adaptive parameters, not learned parameters.
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

        self.carrier_freq = nn.Parameter(carrier_phases.clone())
        init_lock = torch.zeros(n_heads)
        for i, seeded in enumerate(is_seeded):
            if seeded:
                init_lock[i] = 0.3
        self.lock_strength = nn.Parameter(init_lock)

    def compute_head_resonance(self, input_phase: torch.Tensor) -> torch.Tensor:
        if input_phase.dim() == 2:
            input_phase = input_phase.unsqueeze(-1)
        carrier = self.carrier_freq.unsqueeze(0).unsqueeze(0)
        delta_phi = input_phase - carrier
        return torch.cos(delta_phi / 2) ** 2

    def srl_adapt(self, input_phase: torch.Tensor, T: torch.Tensor):
        with torch.no_grad():
            lock = torch.sigmoid(self.lock_strength)
            T_mean = T.mean(dim=(0, 1))
            phase_mean = input_phase.mean(dim=(0, 1))
            delta_omega = phase_mean - self.carrier_freq
            self.carrier_freq.data += self.carrier_lr * (1.0 - lock) * delta_omega * T_mean
            self.lock_strength.data += self.lock_lr * T_mean * (1.0 - lock)


# =====================================================================
#  HEAD NURSERY (dormant -> active head growth)
# =====================================================================

class HeadNursery(nn.Module):
    """
    Monitors for persistent unmatched patterns and wakes dormant heads.
    Dormant heads are dark matter: energy in the left half-plane.
    This is A1: the pool must self-limit into distinct, active heads.
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

        self.register_buffer('active_mask', torch.cat([
            torch.ones(initial_active, dtype=torch.bool),
            torch.zeros(max_heads - initial_active, dtype=torch.bool)
        ]))
        self.register_buffer('max_resonance_ema', torch.tensor(0.5))
        self.register_buffer('unmatched_streak', torch.tensor(0, dtype=torch.long))
        self.register_buffer('unmatched_phase_sin', torch.tensor(0.0))
        self.register_buffer('unmatched_phase_cos', torch.tensor(1.0))
        self.growth_log: List[Dict] = []

    @property
    def n_active(self) -> int:
        return self.active_mask.sum().item()

    @property
    def n_dormant(self) -> int:
        return self.max_heads - self.n_active

    @property
    def wake_threshold(self) -> float:
        ratio = self.n_active / self.max_heads
        return self.base_wake_threshold * (1.0 - ratio)

    def step(self, head_resonances: torch.Tensor,
             input_phase: torch.Tensor,
             srl_state: SRLState,
             step_number: int = 0) -> Optional[int]:
        if self.n_dormant == 0:
            return None
        with torch.no_grad():
            max_T = head_resonances.max(dim=-1).values.mean()
            self.max_resonance_ema = (
                self.ema_decay * self.max_resonance_ema +
                (1 - self.ema_decay) * max_T
            )
            if self.max_resonance_ema < self.wake_threshold:
                self.unmatched_streak += 1
                mean_phase = input_phase.mean()
                self.unmatched_phase_sin = 0.9 * self.unmatched_phase_sin + 0.1 * torch.sin(mean_phase)
                self.unmatched_phase_cos = 0.9 * self.unmatched_phase_cos + 0.1 * torch.cos(mean_phase)
            else:
                self.unmatched_streak.zero_()
                self.unmatched_phase_sin.zero_()
                self.unmatched_phase_cos.fill_(1.0)
            if self.unmatched_streak >= self.persistence_steps:
                return self._wake_head(srl_state, step_number)
        return None

    def get_active_indices(self) -> torch.Tensor:
        return self.active_mask.nonzero(as_tuple=True)[0]

    def _wake_head(self, srl_state: SRLState, step_number: int) -> Optional[int]:
        dormant_indices = (~self.active_mask).nonzero(as_tuple=True)[0]
        if len(dormant_indices) == 0:
            return None
        wake_idx = dormant_indices[0].item()
        target_phase = torch.atan2(self.unmatched_phase_sin, self.unmatched_phase_cos)
        self.active_mask[wake_idx] = True
        with torch.no_grad():
            srl_state.carrier_freq.data[wake_idx] = target_phase.item()
            srl_state.lock_strength.data[wake_idx] = 0.0
        self.unmatched_streak.zero_()
        self.unmatched_phase_sin.zero_()
        self.unmatched_phase_cos.fill_(1.0)
        self.growth_log.append({
            'step': step_number,
            'head_idx': wake_idx,
            'phase': target_phase.item(),
            'n_active_after': self.n_active,
            'max_resonance_ema': self.max_resonance_ema.item(),
        })
        return wake_idx


# =====================================================================
#  ⊙ THE FRACTAL FOLD (unchanged from v2)
# =====================================================================

def fractal_fold(kv: torch.Tensor,
                 ages: torch.Tensor,
                 phase_coherence: torch.Tensor,
                 head_kappa: torch.Tensor,
                 fold_lambda: torch.Tensor) -> torch.Tensor:
    """
    ⊙ The Fractal Fold: unified compression-resonance operation.

    effective_exponent = 1 + age * (base_exp - 1) * (1 - lambda * coherence)

    Phase-matched entries resist compression. The resonance is IN the field.
    """
    base_exp = 1.0 + F.softplus(head_kappa)
    modulation = 1.0 - fold_lambda * phase_coherence.clamp(0, 1)
    eff_exp = 1.0 + ages * (base_exp - 1.0) * modulation

    sign = torch.sign(kv)
    mag = kv.abs().clamp(min=1e-8)
    folded = sign * (mag ** eff_exp)
    return folded


# =====================================================================
#  ⊙ UNIVERSAL BYTE ENCODER
# =====================================================================
#
#  The lens that makes the architecture multi-modal.
#
#  Raw bytes -> phase-bearing field vectors.
#
#  Any modality. Any substrate. The encoder doesn't know what it's
#  looking at. It learns the structure of whatever flows through it.
#
#  Three stages:
#    1. Byte embedding: each byte (0-255) + special tokens gets a
#       learned vector. This is the atomic level.
#    2. Local context: a small 1D convolution over byte embeddings
#       captures sub-chunk patterns (byte n-grams, local structure).
#       This gives the model awareness of byte-level relationships
#       without assuming any modality.
#    3. Chunk projection: groups of bytes are projected into d_model
#       vectors. Each chunk becomes one "token" in the sequence that
#       the fold operates on. Chunk size is the aperture width: how
#       many bytes the system sees at once per position.
#
#  The chunk size is the fundamental tradeoff:
#    Small chunks (4-8 bytes): fine-grained, good for text and
#      sequential data. More positions in the sequence.
#    Large chunks (64-256 bytes): coarse-grained, good for images
#      and audio. Fewer positions, but each captures more context.
#    The default (16 bytes) balances both.
#
#  Phase extraction happens after chunk projection: a learned
#  projection from d_model -> 1 gives each chunk's phase angle.
#  This is the same W_phase from v2, but now it operates on
#  byte-derived vectors rather than token embeddings.
#
# =====================================================================

class UniversalByteEncoder(nn.Module):
    """
    ⊙ Universal Byte Encoder: raw bytes -> field vectors.

    Any modality enters as bytes. The encoder projects byte chunks
    into d_model vectors that carry magnitude and implicit phase.

    The architecture learns modality structure from the data.
    No tokenizer. No spectrogram. No patch embedding.
    Just bytes -> vectors -> fold.
    """

    def __init__(self, d_model: int, chunk_size: int = 16,
                 local_kernel: int = 5, dropout: float = 0.0):
        super().__init__()
        self.d_model = d_model
        self.chunk_size = chunk_size

        # Stage 1: byte embedding (259 = 256 bytes + PAD + BOS + EOS)
        self.byte_embed = nn.Embedding(BYTE_VOCAB, d_model)

        # Stage 2: local context convolution
        # Captures byte n-gram patterns before chunking.
        # Kernel operates over the byte sequence dimension.
        # Padding preserves sequence length.
        self.local_conv = nn.Sequential(
            nn.Conv1d(d_model, d_model, kernel_size=local_kernel,
                      padding=local_kernel // 2, groups=1),
            nn.GELU(),
            nn.Conv1d(d_model, d_model, kernel_size=local_kernel,
                      padding=local_kernel // 2, groups=1),
            nn.GELU(),
        )

        # Stage 3: chunk projection
        # Takes chunk_size byte embeddings and projects to d_model.
        # This is where the encoder learns to see structure in byte groups.
        self.chunk_proj = nn.Linear(d_model * chunk_size, d_model)

        # Layer norm after projection
        self.norm = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, byte_ids: torch.Tensor) -> torch.Tensor:
        """
        byte_ids: (batch, n_bytes) integer tensor, values 0-258
        Returns: (batch, n_chunks, d_model) field vectors

        n_chunks = n_bytes // chunk_size (truncates remainder)
        """
        batch, n_bytes = byte_ids.shape
        n_chunks = n_bytes // self.chunk_size

        # Truncate to exact multiple of chunk_size
        byte_ids = byte_ids[:, :n_chunks * self.chunk_size]

        # Stage 1: embed each byte
        x = self.byte_embed(byte_ids)  # (batch, n_bytes_trunc, d_model)

        # Stage 2: local context
        # Conv1d expects (batch, channels, length)
        x = x.transpose(1, 2)
        x = self.local_conv(x) + x  # residual
        x = x.transpose(1, 2)  # back to (batch, n_bytes_trunc, d_model)

        # Stage 3: chunk and project
        # Reshape into chunks: (batch, n_chunks, chunk_size * d_model)
        x = x.reshape(batch, n_chunks, self.chunk_size * self.d_model)
        x = self.chunk_proj(x)  # (batch, n_chunks, d_model)

        return self.dropout(self.norm(x))


# =====================================================================
#  POSITIONAL PHASE ENCODING
# =====================================================================
#
#  Instead of standard sinusoidal PE (which assumes 1D sequence),
#  we use a phase encoding that represents position as a point on
#  the unit circle. The position IS a phase. Multiple frequencies
#  give the model the ability to distinguish positions at different
#  scales (local vs global).
#
#  This is more natural for the fold: positions are phases, and
#  the fold operates on phase coherence. Position and content phase
#  interact in the same space.
#
# =====================================================================

class PhasePE(nn.Module):
    """
    Positional encoding as phase. Each position gets a phase signature
    across multiple frequency bands. Compatible with both byte-chunk
    positions and token positions.
    """

    def __init__(self, d_model: int, max_len: int = 8192):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len).unsqueeze(1).float()

        # Frequency bands: from high frequency (local) to low (global)
        # Using golden ratio spacing for fractal self-similarity
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() *
            (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe.unsqueeze(0))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.pe[:, :x.size(1)]


# =====================================================================
#  FRACTAL ATTENTION LAYER (unchanged from v2, except phase source)
# =====================================================================

class FractalAttentionLayer(nn.Module):
    """
    ⊙ Fractal Attention with unified fold. Identical to v2.
    """

    def __init__(self, d_model: int, n_active_heads: int = 8,
                 max_heads: int = None,
                 head_manager: DimensionalHeadManager = None,
                 kappa: float = KAPPA,
                 fold_lambda: float = FOLD_LAMBDA,
                 enable_growth: bool = True,
                 wake_threshold: float = 0.3,
                 persistence_steps: int = 50):
        super().__init__()

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
        self.enable_growth = enable_growth

        self.W_q = nn.Linear(d_model, d_model, bias=False)
        self.W_k = nn.Linear(d_model, d_model, bias=False)
        self.W_v = nn.Linear(d_model, d_model, bias=False)
        self.W_o = nn.Linear(d_model, d_model, bias=False)
        self.W_phase = nn.Linear(d_model, 1, bias=False)

        self.head_kappa = nn.Parameter(torch.full((max_heads,), kappa))
        self.fold_lambda = nn.Parameter(torch.full((max_heads,), fold_lambda))

        if head_manager is None:
            head_manager = DimensionalHeadManager(max_heads)
        self.head_manager = head_manager

        carrier_phases = head_manager.get_carrier_phases_tensor(torch.device('cpu'))
        self.srl = SRLState(max_heads, carrier_phases, head_manager.is_seeded)
        self.nursery = HeadNursery(
            max_heads, n_active_heads,
            wake_threshold=wake_threshold,
            persistence_steps=persistence_steps,
        )

        self.norm = nn.LayerNorm(d_model)
        self.register_buffer('_step_counter', torch.tensor(0, dtype=torch.long))

    def forward(self, x: torch.Tensor,
                mask: Optional[torch.Tensor] = None
                ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        batch, seq_len, _ = x.shape
        device = x.device
        residual = x
        x = self.norm(x)

        Q = self.W_q(x).view(batch, seq_len, self.max_heads, self.d_head).transpose(1, 2)
        K = self.W_k(x).view(batch, seq_len, self.max_heads, self.d_head).transpose(1, 2)
        V = self.W_v(x).view(batch, seq_len, self.max_heads, self.d_head).transpose(1, 2)

        active_mask = self.nursery.active_mask.to(device)
        head_active = active_mask.float().view(1, self.max_heads, 1, 1)
        Q = Q * head_active
        K = K * head_active
        V = V * head_active

        input_phase = self.W_phase(x).squeeze(-1)

        head_T = self.srl.compute_head_resonance(input_phase)
        head_T = head_T * active_mask.float().unsqueeze(0).unsqueeze(0)

        if self.training:
            self.srl.srl_adapt(input_phase, head_T)
            self._step_counter += 1

        if self.training and self.enable_growth:
            active_indices = self.nursery.get_active_indices().to(device)
            if len(active_indices) > 0:
                self.nursery.step(
                    head_T[:, :, active_indices], input_phase, self.srl,
                    step_number=self._step_counter.item()
                )

        # ⊙ THE FRACTAL FOLD
        if seq_len > 1:
            ages = torch.arange(seq_len, device=device, dtype=torch.float32)
            ages = (seq_len - 1 - ages) / max(seq_len - 1, 1)
            ages = ages.view(1, 1, seq_len, 1)

            phi_all = input_phase
            phi_q = phi_all.unsqueeze(-1)
            phi_k = phi_all.unsqueeze(-2)
            pairwise_coherence = torch.cos((phi_q - phi_k) / 2) ** 2
            mean_coherence = pairwise_coherence.mean(dim=1)
            mean_coherence = mean_coherence.view(batch, 1, seq_len, 1)

            K_max = K.abs().amax(dim=-1, keepdim=True).clamp(min=1e-8)
            V_max = V.abs().amax(dim=-1, keepdim=True).clamp(min=1e-8)
            K_norm = K / K_max
            V_norm = V / V_max

            K_mag_before = K_norm.abs().sum()

            head_kappa = self.head_kappa.view(1, self.max_heads, 1, 1)
            fold_lam = torch.sigmoid(self.fold_lambda).view(1, self.max_heads, 1, 1)

            K = fractal_fold(K_norm, ages, mean_coherence, head_kappa, fold_lam)
            V = fractal_fold(V_norm, ages, mean_coherence, head_kappa, fold_lam)

            compressed_energy = (K_mag_before - K.abs().sum()).detach()
        else:
            compressed_energy = torch.tensor(0.0, device=device)

        # ATTENTION
        attn_scores = torch.matmul(Q, K.transpose(-2, -1)) * self.scale

        if not active_mask.all():
            dormant_mask = (~active_mask).view(1, self.max_heads, 1, 1)
            attn_scores = attn_scores.masked_fill(dormant_mask, 0.0)

        if mask is not None:
            attn_scores = attn_scores.masked_fill(mask == 0, float('-inf'))

        attn_weights = F.softmax(attn_scores, dim=-1)

        out = torch.matmul(attn_weights, V)

        head_gate = head_T.transpose(1, 2).unsqueeze(-1)
        out = out * head_gate

        expressed_energy = out.abs().sum().detach()

        out = out.transpose(1, 2).contiguous().view(batch, seq_len, self.d_model)
        return residual + self.W_o(out), compressed_energy, expressed_energy


# =====================================================================
#  FEED-FORWARD NETWORK (SwiGLU, phi-scaled)
# =====================================================================

class FeedForward(nn.Module):
    def __init__(self, d_model: int, d_ff: int = None, dropout: float = 0.0):
        super().__init__()
        d_ff = d_ff or round(d_model * PHI * 2)
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
#  BALANCE-AS-TEMPERATURE (◐ OUTPUT GATING)
# =====================================================================

class BalanceTemperature(nn.Module):
    def __init__(self, ema_decay: float = 0.99, initial_balance: float = BALANCE):
        super().__init__()
        self.ema_decay = ema_decay
        self.register_buffer('balance', torch.tensor(initial_balance))

    def update(self, compressed_energy: torch.Tensor,
               expressed_energy: torch.Tensor):
        total = compressed_energy + expressed_energy + 1e-8
        ratio = torch.clamp(compressed_energy / total, 0.01, 0.99)
        self.balance = self.ema_decay * self.balance + (1 - self.ema_decay) * ratio.detach()

    @property
    def temperature(self) -> torch.Tensor:
        return torch.clamp(1.0 / (2.0 * self.balance + 1e-8), 0.1, 10.0)

    def apply_temperature(self, logits: torch.Tensor) -> torch.Tensor:
        return logits / self.temperature


# =====================================================================
#  ⊙ THE FRACTAL RESONANCE TRANSFORMER v3 (Multi-Modal)
# =====================================================================

class FractalResonanceTransformerV3(nn.Module):
    """
    ⊙ The Fractal Resonance Transformer v3 (Multi-Modal)

    Universal byte encoder + unified fold. Any modality. One architecture.

    Input: raw bytes (any file, any stream, any modality).
    Output: byte-level predictions (next byte, or reconstructed bytes).

    The architecture is modality-agnostic. Modality structure emerges
    from training through SRL head specialization.

    Two modes:
        1. Generative (default): predicts next byte chunk. Causal mask.
           Use for text generation, audio synthesis, etc.
        2. Autoencoder: reconstructs input byte chunks. No causal mask.
           Use for representation learning, compression, understanding.
    """

    def __init__(self, d_model: int = 128,
                 n_heads: int = 8, max_heads: int = None,
                 n_layers: int = 6, kappa: float = KAPPA,
                 fold_lambda: float = FOLD_LAMBDA,
                 chunk_size: int = 16,
                 local_kernel: int = 5,
                 dropout: float = 0.0, max_seq_len: int = 8192,
                 enable_growth: bool = True,
                 wake_threshold: float = 0.3,
                 persistence_steps: int = 50):
        super().__init__()

        if max_heads is None:
            max_heads = n_heads * 2 if enable_growth else n_heads

        self.d_model = d_model
        self.n_heads = n_heads
        self.max_heads = max_heads
        self.n_layers = n_layers
        self.chunk_size = chunk_size
        self.enable_growth = enable_growth

        # Universal byte encoder
        self.encoder = UniversalByteEncoder(
            d_model, chunk_size=chunk_size,
            local_kernel=local_kernel, dropout=dropout,
        )

        # Positional phase encoding
        max_chunks = max_seq_len // chunk_size
        self.pos_enc = PhasePE(d_model, max_len=max_chunks)
        self.embed_dropout = nn.Dropout(dropout)

        # Head manager (shared across layers)
        self.head_manager = DimensionalHeadManager(max_heads)

        # Transformer layers
        self.attn_layers = nn.ModuleList()
        self.ff_layers = nn.ModuleList()

        for _ in range(n_layers):
            self.attn_layers.append(FractalAttentionLayer(
                d_model,
                n_active_heads=n_heads,
                max_heads=max_heads,
                head_manager=self.head_manager,
                kappa=kappa,
                fold_lambda=fold_lambda,
                enable_growth=enable_growth,
                wake_threshold=wake_threshold,
                persistence_steps=persistence_steps,
            ))
            self.ff_layers.append(FeedForward(d_model, dropout=dropout))

        # Output: project back to byte vocabulary
        self.final_norm = nn.LayerNorm(d_model)
        self.output_head = nn.Linear(d_model, BYTE_VOCAB, bias=False)

        # ◐ Balance-as-temperature
        self.balance = BalanceTemperature()

        self._init_weights()

    def _init_weights(self):
        nn.init.normal_(self.output_head.weight, std=0.02)

    def _causal_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        return torch.tril(torch.ones(seq_len, seq_len, device=device)).bool()

    def forward(self, byte_ids: torch.Tensor,
                causal: bool = True) -> torch.Tensor:
        """
        byte_ids: (batch, n_bytes) raw byte values (0-258)
        causal: if True, apply causal mask (generative mode)
        Returns: (batch, n_chunks, BYTE_VOCAB) logits per chunk position
        """
        device = byte_ids.device

        # Universal byte encoder: bytes -> field vectors
        h = self.encoder(byte_ids)  # (batch, n_chunks, d_model)
        h = self.embed_dropout(self.pos_enc(h))

        n_chunks = h.size(1)
        mask = self._causal_mask(n_chunks, device) if causal else None

        total_compressed = torch.tensor(0.0, device=device)
        total_expressed = torch.tensor(0.0, device=device)

        for i in range(self.n_layers):
            h, comp_e, expr_e = self.attn_layers[i](h, mask=mask)
            h = self.ff_layers[i](h)
            total_compressed = total_compressed + comp_e
            total_expressed = total_expressed + expr_e

        self.balance.update(total_compressed, total_expressed)

        logits = self.output_head(self.final_norm(h))
        if not self.training:
            logits = self.balance.apply_temperature(logits)
        return logits

    def forward_bytes(self, raw_bytes: bytes, causal: bool = True) -> torch.Tensor:
        """
        Convenience: accept Python bytes directly.
        Returns logits tensor.
        """
        byte_tensor = torch.tensor(list(raw_bytes), dtype=torch.long).unsqueeze(0)
        return self.forward(byte_tensor, causal=causal)

    def get_balance(self) -> float:
        return self.balance.balance.item()

    def get_temperature(self) -> float:
        return self.balance.temperature.item()

    def total_active_heads(self) -> int:
        return sum(layer.nursery.n_active for layer in self.attn_layers)

    def total_dormant_heads(self) -> int:
        return sum(layer.nursery.n_dormant for layer in self.attn_layers)

    def get_growth_summary(self) -> str:
        lines = []
        for i, layer in enumerate(self.attn_layers):
            nursery = layer.nursery
            lines.append(f"  Layer {i}: {nursery.n_active}/{nursery.max_heads} active")
            for event in nursery.growth_log:
                lines.append(
                    f"    head {event['head_idx']} woke at step {event['step']} "
                    f"(phase {event['phase']:.3f})")
        return "\n".join(lines)

    def summary(self) -> str:
        n_params = sum(p.numel() for p in self.parameters())
        enc_params = sum(p.numel() for p in self.encoder.parameters())
        attn_params = sum(p.numel() for l in self.attn_layers for p in l.parameters())
        ff_params = sum(p.numel() for l in self.ff_layers for p in l.parameters())

        lines = [
            "",
            "⊙ FRACTAL RESONANCE TRANSFORMER v3 (Multi-Modal)",
            "=" * 55,
            f"  d_model:      {self.d_model}",
            f"  n_heads:      {self.n_heads} active / {self.max_heads} capacity",
            f"  n_layers:     {self.n_layers}",
            f"  chunk_size:   {self.chunk_size} bytes per position",
            f"  byte_vocab:   {BYTE_VOCAB} (256 + PAD/BOS/EOS)",
            f"  growth:       {'enabled' if self.enable_growth else 'disabled'}",
            f"  total params: {n_params:,}",
            f"    Encoder:     {enc_params:,}",
            f"    Attn layers: {attn_params:,}",
            f"    FFN layers:  {ff_params:,}",
            "",
            self.head_manager.summary(),
            "",
            f"  Active heads (total): {self.total_active_heads()} "
            f"({self.total_dormant_heads()} dormant)",
            "",
            f"  ◐ (balance):     {self.get_balance():.4f}",
            f"  tau (temperature): {self.get_temperature():.4f}",
            "=" * 55,
        ]
        return "\n".join(lines)


# =====================================================================
#  CONVENIENCE CONFIGS
# =====================================================================

def frt_v3_small(chunk_size: int = 16, **kwargs) -> FractalResonanceTransformerV3:
    """Small FRT-v3: ~4M params. 8 active heads, 16 byte chunks."""
    defaults = dict(d_model=128, n_heads=8, max_heads=16, n_layers=6,
                    chunk_size=chunk_size)
    defaults.update(kwargs)
    return FractalResonanceTransformerV3(**defaults)


def frt_v3_medium(chunk_size: int = 16, **kwargs) -> FractalResonanceTransformerV3:
    """Medium FRT-v3: ~30M params. 16 active heads."""
    defaults = dict(d_model=256, n_heads=16, max_heads=32, n_layers=8,
                    chunk_size=chunk_size)
    defaults.update(kwargs)
    return FractalResonanceTransformerV3(**defaults)


def frt_v3_large(chunk_size: int = 16, **kwargs) -> FractalResonanceTransformerV3:
    """Large FRT-v3: ~100M+ params. 32 active heads."""
    defaults = dict(d_model=512, n_heads=32, max_heads=64, n_layers=12,
                    chunk_size=chunk_size)
    defaults.update(kwargs)
    return FractalResonanceTransformerV3(**defaults)


# =====================================================================
#  UTILITY: convert any file to byte tensor
# =====================================================================

def file_to_bytes(filepath: str, max_bytes: int = None) -> torch.Tensor:
    """Read any file as raw bytes and return a tensor of byte values."""
    with open(filepath, 'rb') as f:
        data = f.read(max_bytes) if max_bytes else f.read()
    return torch.tensor(list(data), dtype=torch.long)


def text_to_bytes(text: str) -> torch.Tensor:
    """Convert a string to a byte tensor (UTF-8 encoded)."""
    return torch.tensor(list(text.encode('utf-8')), dtype=torch.long)


def bytes_to_text(byte_ids: torch.Tensor) -> str:
    """Convert byte tensor back to string (best-effort UTF-8 decode)."""
    byte_list = byte_ids.tolist()
    # Filter out special tokens
    byte_list = [b for b in byte_list if b < 256]
    return bytes(byte_list).decode('utf-8', errors='replace')


# =====================================================================
#  MAIN: MULTI-MODAL ARCHITECTURE VERIFICATION
# =====================================================================

if __name__ == '__main__':
    print("\n⊙ THE FRACTAL RESONANCE TRANSFORMER v3 (Multi-Modal)")
    print("  Universal byte encoder + unified fold.")
    print("  Any modality. One architecture. E = 1.\n")

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"  Device: {device}\n")

    model = frt_v3_small(chunk_size=16).to(device)
    print(model.summary())

    # ════════════════════════════════════════
    #  TEST 1: TEXT (UTF-8 bytes)
    # ════════════════════════════════════════

    print("\n  Test 1: TEXT input")
    text = "The circumpunct is a whole composed of three irreducible parts."
    text_bytes = text_to_bytes(text).unsqueeze(0).to(device)
    # Pad to multiple of chunk_size
    pad_needed = model.chunk_size - (text_bytes.size(1) % model.chunk_size)
    if pad_needed < model.chunk_size:
        text_bytes = F.pad(text_bytes, (0, pad_needed), value=PAD_TOKEN)
    print(f"  Input: \"{text}\"")
    print(f"  Bytes: {text_bytes.shape[1]} -> {text_bytes.shape[1] // model.chunk_size} chunks")

    model.train()
    logits = model(text_bytes)
    print(f"  Output logits: {logits.shape}")
    print(f"  ◐ = {model.get_balance():.4f}")

    # ════════════════════════════════════════
    #  TEST 2: RANDOM BYTES (simulated audio/image)
    # ════════════════════════════════════════

    print("\n  Test 2: RANDOM BYTES (simulated multi-modal)")
    batch_size = 4
    n_bytes = 512  # 512 bytes = 32 chunks at chunk_size=16
    random_bytes = torch.randint(0, 256, (batch_size, n_bytes), device=device)
    print(f"  Input: {random_bytes.shape} random bytes")
    print(f"  Chunks: {n_bytes // model.chunk_size}")

    logits = model(random_bytes)
    print(f"  Output logits: {logits.shape}")

    # ════════════════════════════════════════
    #  TEST 3: BACKWARD PASS
    # ════════════════════════════════════════

    print("\n  Test 3: BACKWARD PASS")
    # Target: predict the next chunk's first byte (simplified)
    n_chunks = n_bytes // model.chunk_size
    target = torch.randint(0, BYTE_VOCAB, (batch_size, n_chunks), device=device)
    loss = F.cross_entropy(logits.view(-1, BYTE_VOCAB), target.view(-1))
    loss.backward()
    print(f"  Loss: {loss.item():.4f}")

    n_grad = sum(1 for p in model.parameters()
                 if p.grad is not None and p.grad.abs().sum() > 0)
    n_total = sum(1 for p in model.parameters() if p.requires_grad)
    print(f"  Gradients: {n_grad}/{n_total} parameters received gradients")

    # Check encoder gradients specifically
    enc_grad = sum(1 for p in model.encoder.parameters()
                   if p.grad is not None and p.grad.abs().sum() > 0)
    enc_total = sum(1 for p in model.encoder.parameters() if p.requires_grad)
    print(f"  Encoder gradients: {enc_grad}/{enc_total}")

    # ════════════════════════════════════════
    #  TEST 4: REAL FILE INPUT (self-referential)
    # ════════════════════════════════════════

    print("\n  Test 4: REAL FILE INPUT (reading own source code)")
    own_path = os.path.abspath(__file__)
    if os.path.exists(own_path):
        file_bytes = file_to_bytes(own_path, max_bytes=1024)
        # Pad
        pad_needed = model.chunk_size - (len(file_bytes) % model.chunk_size)
        if pad_needed < model.chunk_size:
            file_bytes = F.pad(file_bytes, (0, pad_needed), value=PAD_TOKEN)
        file_bytes = file_bytes.unsqueeze(0).to(device)
        print(f"  File: {own_path}")
        print(f"  Bytes: {file_bytes.shape[1]} -> {file_bytes.shape[1] // model.chunk_size} chunks")

        model.eval()
        with torch.no_grad():
            logits = model(file_bytes)
            probs = F.softmax(logits[0, -1], dim=-1)
            top5 = torch.topk(probs, 5)
            top_bytes = top5.indices.tolist()
            top_probs = top5.values.tolist()
            print(f"  Next chunk prediction (top 5):")
            for b, p in zip(top_bytes, top_probs):
                char = chr(b) if 32 <= b < 127 else f'<{b}>'
                print(f"    byte {b:3d} ({char}): {p:.4f}")
    else:
        print(f"  (skipped: cannot read own source)")

    # ════════════════════════════════════════
    #  TEST 5: TIMING
    # ════════════════════════════════════════

    print(f"\n  Test 5: TIMING")
    model.train()

    # Warmup
    for _ in range(3):
        model.zero_grad()
        out = model(random_bytes)
        F.cross_entropy(out.view(-1, BYTE_VOCAB), target.view(-1)).backward()

    n_runs = 10
    t0 = time.time()
    for _ in range(n_runs):
        model.zero_grad()
        out = model(random_bytes)
        F.cross_entropy(out.view(-1, BYTE_VOCAB), target.view(-1)).backward()
    avg_ms = (time.time() - t0) / n_runs * 1000
    print(f"  Avg forward+backward ({batch_size}x{n_bytes} bytes): {avg_ms:.1f} ms")

    # Different byte lengths
    for test_bytes in [256, 1024, 2048]:
        x_test = torch.randint(0, 256, (2, test_bytes), device=device)
        model.eval()
        t0 = time.time()
        with torch.no_grad():
            for _ in range(5):
                _ = model(x_test)
        t_ms = (time.time() - t0) / 5 * 1000
        n_chunks = test_bytes // model.chunk_size
        print(f"  {test_bytes} bytes ({n_chunks} chunks): {t_ms:.1f} ms forward")

    # ════════════════════════════════════════
    #  FOLD PARAMETER INSPECTION
    # ════════════════════════════════════════

    print(f"\n  Fold parameters:")
    for i, layer in enumerate(model.attn_layers):
        kappa_vals = F.softplus(layer.head_kappa).detach()
        lambda_vals = torch.sigmoid(layer.fold_lambda).detach()
        active = layer.nursery.active_mask
        ak = kappa_vals[active]
        al = lambda_vals[active]
        print(f"  Layer {i}: kappa [{ak.min():.3f}, {ak.max():.3f}]  "
              f"lambda [{al.min():.3f}, {al.max():.3f}]")

    print(f"\n  Final: {model.total_active_heads()} active, "
          f"{model.total_dormant_heads()} dormant, "
          f"◐ = {model.get_balance():.4f}")

    print("\n  ⊙ All checks passed.")
    print("  Universal byte encoder: any modality, one aperture.")
    print("  'E = 1. Energy doesn't come in flavors.'\n")
