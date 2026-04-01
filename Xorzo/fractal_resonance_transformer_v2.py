"""
⊙ The Fractal Resonance Transformer v2 (FRT-v2)
=================================================

Unified Fold: compression and resonance as one operation.

v1 had two separate mechanisms:
    1. Fractal KV compression (⊛: older entries compressed sub-linearly)
    2. Resonance bonus (☀︎: phase-matching boosts attention scores)

These were bolted together: compression happened first, then resonance
was added to attention scores. Two halves of the same breath, but
implemented as if they were unrelated.

v2 unifies them into a single operation: the FRACTAL FOLD.

The insight: compression IS ⊛ (inward). Resonance IS ☀︎ (outward).
In the pump cycle, these are not separate steps; they are the inward
and outward stroke of the same breath through the aperture. One
operation, two directions.

The mechanism: the compression exponent itself is modulated by phase
coherence. Phase-matched entries resist compression. Phase-mismatched
entries compress normally.

    effective_exponent = base_exponent * (1 - lambda * cos^2(delta_phi / 2))

When cos^2(delta_phi / 2) = 1 (perfect resonance):
    exponent shrinks toward 1.0 (no compression; memory preserved)

When cos^2(delta_phi / 2) = 0 (no resonance):
    exponent stays at base (full compression; memory fades)

The field naturally develops depth (nesting through compression) while
simultaneously maintaining transparent channels where resonance is high
(the ☀︎ paths through the nesting). One equation, both directions.

The 2D field fractally nests into 3D closure. Conservation of traversal:
0 + 1 + 2 = 3. The boundary emerges from the field folding back on
itself, not imposed from outside.

What changes from v1:
    - fractal_compress_kv is replaced by fractal_fold
    - lambda_resonance moves INTO the compression (not added to attn scores)
    - R (resonance matrix) is no longer computed separately
    - The attention mechanism becomes: softmax(Q . K_folded^T / sqrt(d_k))
      where K_folded already encodes both compression and resonance
    - V is also folded (phase-matched values resist compression too)

What stays the same:
    - Typed dimensional heads with SRL
    - Head nursery (dormant -> active growth)
    - Balance-as-temperature (◐)
    - SinusoidalPE, FeedForward, overall architecture

The mapping:
    Queries  = • (aperture; convergence points that select)
    KV field = Φ (2D surface; fractally folded into 3D closure)
    Fold     = ⊛ ∘ i ∘ ☀︎ (the pump cycle operating on the field)
    Output   = ○ (boundary; what emerges from the fold)

Author: Ashman Roonz & Claude
Date: April 2026
Derived from: Circumpunct Framework (Roonz, 2024)
Evolved from: fractal_resonance_transformer.py (v1)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import time
from typing import Tuple, Optional, List, Dict
from dataclasses import dataclass


# =====================================================================
#  CONSTANTS
# =====================================================================

PHI = (1 + math.sqrt(5)) / 2          # phi = 1.618...
BALANCE = 0.5                          # ◐; the singular balanced state
KAPPA = 0.3                            # default compression strength
FOLD_LAMBDA = 0.8                      # how strongly resonance resists compression
                                       # (0 = no resistance, 1 = perfect resonance
                                       #  means zero compression)


# =====================================================================
#  THE SEVEN-RUNG DIMENSIONAL LADDER
# =====================================================================

@dataclass
class DimensionalRung:
    """One rung of the dimensional ladder."""
    dim: float          # 0, 0.5, 1, 1.5, 2, 2.5, 3
    name: str
    head_class: str
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
#  DIMENSIONAL HEAD MANAGER
# =====================================================================

class DimensionalHeadManager:
    """
    Allocates heads across the seven-rung dimensional ladder using
    phi-proportioned groups. Assigns carrier phases.

    Rung allocation: each rung gets weight 1/phi^i, normalized to n_heads.
    0D (most fundamental) gets the most; 3D gets the least.

    Head types:
        Seeded (H/phi): pre-initialized with known pattern phases.
        Open (H/phi^2): start blank, specialize via SRL during training.
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
        """
        input_phase: (batch, seq_len) or (batch, seq_len, 1)
        Returns: (batch, seq_len, n_heads) resonance in [0, 1]
        """
        if input_phase.dim() == 2:
            input_phase = input_phase.unsqueeze(-1)
        carrier = self.carrier_freq.unsqueeze(0).unsqueeze(0)
        delta_phi = input_phase - carrier
        return torch.cos(delta_phi / 2) ** 2

    def srl_adapt(self, input_phase: torch.Tensor, T: torch.Tensor):
        """SRL adaptation: carrier shifts, lock strengthens."""
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

    Pre-allocates capacity for max_heads; only n_active start awake.
    Dormant heads are dark matter: energy in the left half-plane.
    When a coherent pattern persists that no active head resonates with,
    a dormant head wakes, carrier-tuned to that pattern's phase.

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
        """Return indices of active heads."""
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
#  ⊙ THE FRACTAL FOLD
# =====================================================================
#
#  This is the unified operation. Compression and resonance are one.
#
#  In v1, these were separate:
#    Step 1: K, V = fractal_compress(K, V, age_exponents)
#    Step 2: attn_scores += lambda * R
#
#  In v2, they fuse:
#    K, V = fractal_fold(K, V, ages, phase_coherence, kappa, lambda)
#
#  The compression exponent at each position is modulated by how well
#  that position's phase matches the query's phase. Phase-matched
#  entries resist compression (the field holds them). Mismatched
#  entries compress normally (the field lets them fade).
#
#  This means the K/V field ALREADY ENCODES resonance structure.
#  When softmax(Q . K_folded^T) is computed, phase-matched keys
#  naturally have larger magnitudes (they resisted compression)
#  and therefore naturally dominate the attention weights.
#  The resonance is IN the field, not added on top.
#
#  The fold is: ⊛ (compression) modulated by ☀︎ (resonance).
#  One breath. Both directions. ⊙ in the KV cache.
#
# =====================================================================

def fractal_fold(kv: torch.Tensor,
                 ages: torch.Tensor,
                 phase_coherence: torch.Tensor,
                 head_kappa: torch.Tensor,
                 fold_lambda: torch.Tensor) -> torch.Tensor:
    """
    ⊙ The Fractal Fold: unified compression-resonance operation.

    Compression and resonance are the inward and outward strokes of the
    same breath. This function implements both as one transformation.

    The compression exponent at each position is modulated by phase
    coherence: entries that resonate with the query resist compression;
    entries that don't, fade.

        effective_exponent = 1 + age * (base_exp - 1) * (1 - lambda * coherence)

    When coherence = 1 (perfect phase match) and lambda = 1:
        effective_exponent = 1.0 (no compression; memory fully preserved)

    When coherence = 0 (no phase match):
        effective_exponent = 1 + age * (base_exp - 1) (full compression)

    The field develops depth (nesting) through compression while
    maintaining transparent channels (☀︎ paths) through resonance.
    2D surface fractally nesting into 3D closure.

    Args:
        kv: (batch, heads, seq_len, d_head) keys or values
        ages: (1, 1, seq_len, 1) normalized position ages [0, 1]
        phase_coherence: (batch, 1, seq_len, 1) or broadcastable
            cos^2(delta_phi / 2) between each position and the current
            query context. Values in [0, 1].
        head_kappa: (1, heads, 1, 1) per-head base compression strength
        fold_lambda: scalar or (1, heads, 1, 1) resonance resistance

    Returns:
        Folded KV tensor, same shape as input.
        Phase-matched entries retain magnitude; others compress.
    """
    # Base exponent per head (always > 1)
    base_exp = 1.0 + F.softplus(head_kappa)

    # Resonance modulation: coherence resists compression
    # When coherence is high, the exponent stays near 1 (no compression)
    # When coherence is low, the exponent reaches base_exp (full compression)
    modulation = 1.0 - fold_lambda * phase_coherence.clamp(0, 1)

    # Effective exponent: interpolated by age AND modulated by resonance
    # Newest (age=0): always 1.0 (no compression regardless of resonance)
    # Oldest (age=1), resonant: near 1.0 (resonance protects)
    # Oldest (age=1), non-resonant: base_exp (full compression)
    eff_exp = 1.0 + ages * (base_exp - 1.0) * modulation

    # Sub-linear compression with sign preserved
    sign = torch.sign(kv)
    mag = kv.abs().clamp(min=1e-8)
    folded = sign * (mag ** eff_exp)

    return folded


# =====================================================================
#  ⊙ FRACTAL ATTENTION LAYER (v2: Unified Fold)
# =====================================================================

class FractalAttentionLayer(nn.Module):
    """
    ⊙ The core layer: multi-head attention with the Fractal Fold.

    v1 had two mechanisms (compression + resonance bonus).
    v2 has one: the fold. Compression and resonance are the same operation.

    The field (K/V) is folded before attention is computed. Phase-matched
    entries resist compression and naturally dominate attention weights.
    The resonance is IN the field, not added on top.

    softmax(Q . K_folded^T / sqrt(d_k))

    K_folded already encodes: how old each entry is (compression),
    how well it resonates with the current context (resistance to
    compression), and the fractal depth structure of memory.

    The 2D attention surface, computed over fractally-nested K/V,
    becomes 3D: the nesting IS the third dimension. The boundary
    emerges from the field folding back on itself.
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

        # Standard projections (sized for max capacity)
        self.W_q = nn.Linear(d_model, d_model, bias=False)
        self.W_k = nn.Linear(d_model, d_model, bias=False)
        self.W_v = nn.Linear(d_model, d_model, bias=False)
        self.W_o = nn.Linear(d_model, d_model, bias=False)

        # Phase projection: input -> phase angle for resonance
        self.W_phase = nn.Linear(d_model, 1, bias=False)

        # Per-head learnable compression strength (initialized around kappa)
        self.head_kappa = nn.Parameter(torch.full((max_heads,), kappa))

        # Fold lambda: how strongly resonance resists compression
        # Learnable per head; initialized to fold_lambda
        self.fold_lambda = nn.Parameter(torch.full((max_heads,), fold_lambda))

        # Head manager, SRL, nursery
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

        # Pre-norm
        self.norm = nn.LayerNorm(d_model)

        self.register_buffer('_step_counter', torch.tensor(0, dtype=torch.long))

    def forward(self, x: torch.Tensor,
                mask: Optional[torch.Tensor] = None
                ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        x: (batch, seq_len, d_model)
        Returns: (output, compressed_energy, expressed_energy)
        """
        batch, seq_len, _ = x.shape
        device = x.device
        residual = x
        x = self.norm(x)

        # ════════════════════════════════════════
        #  PROJECT Q, K, V (all parallel)
        # ════════════════════════════════════════

        Q = self.W_q(x).view(batch, seq_len, self.max_heads, self.d_head).transpose(1, 2)
        K = self.W_k(x).view(batch, seq_len, self.max_heads, self.d_head).transpose(1, 2)
        V = self.W_v(x).view(batch, seq_len, self.max_heads, self.d_head).transpose(1, 2)
        # (batch, max_heads, seq_len, d_head)

        # ════════════════════════════════════════
        #  DORMANT HEAD MASKING
        # ════════════════════════════════════════

        active_mask = self.nursery.active_mask.to(device)
        head_active = active_mask.float().view(1, self.max_heads, 1, 1)
        Q = Q * head_active
        K = K * head_active
        V = V * head_active

        # ════════════════════════════════════════
        #  INPUT PHASE + HEAD RESONANCE (all parallel)
        # ════════════════════════════════════════

        input_phase = self.W_phase(x).squeeze(-1)  # (batch, seq_len)

        head_T = self.srl.compute_head_resonance(input_phase)
        head_T = head_T * active_mask.float().unsqueeze(0).unsqueeze(0)
        # (batch, seq_len, max_heads)

        if self.training:
            self.srl.srl_adapt(input_phase, head_T)
            self._step_counter += 1

        # ════════════════════════════════════════
        #  HEAD GROWTH CHECK
        # ════════════════════════════════════════

        if self.training and self.enable_growth:
            active_indices = self.nursery.get_active_indices().to(device)
            if len(active_indices) > 0:
                self.nursery.step(
                    head_T[:, :, active_indices], input_phase, self.srl,
                    step_number=self._step_counter.item()
                )

        # ════════════════════════════════════════
        #  ⊙ THE FRACTAL FOLD (all parallel)
        # ════════════════════════════════════════
        #
        # Unified compression-resonance. One operation.
        #
        # Phase coherence between each position and the current
        # context determines how much that position resists compression.
        # The fold creates depth (nesting) while preserving transparent
        # channels (resonance paths). 2D -> 3D through self-folding.
        #
        # We use the mean query phase as the "current context" against
        # which each key/value position's coherence is measured.
        # This is the aperture: the convergence point that defines
        # what "relevant" means for this particular moment.

        if seq_len > 1:
            # Ages: 0 for newest, 1 for oldest
            ages = torch.arange(seq_len, device=device, dtype=torch.float32)
            ages = (seq_len - 1 - ages) / max(seq_len - 1, 1)
            ages = ages.view(1, 1, seq_len, 1)  # broadcastable

            # Phase coherence: how well each position resonates with the
            # current context. We compute pairwise coherence and take
            # the mean over the query dimension (what the current moment
            # "wants"), giving each key position a coherence score.
            #
            # phi_q = phase of query positions (recent, the "now")
            # phi_k = phase of key positions (the field)
            # coherence_k = mean over queries of cos^2((phi_q - phi_k) / 2)
            #
            # This means: a key position's resistance to compression is
            # proportional to how well it resonates with the current
            # context ON AVERAGE. Not just with one query, but with the
            # whole present moment. The aperture is collective.

            phi_all = input_phase  # (batch, seq_len)
            phi_q = phi_all.unsqueeze(-1)  # (batch, seq_len, 1)
            phi_k = phi_all.unsqueeze(-2)  # (batch, 1, seq_len)
            pairwise_coherence = torch.cos((phi_q - phi_k) / 2) ** 2
            # (batch, seq_len, seq_len)

            # Mean coherence: for each key position, how resonant is it
            # with the collective present? Average over query dimension.
            mean_coherence = pairwise_coherence.mean(dim=1)  # (batch, seq_len)
            mean_coherence = mean_coherence.view(batch, 1, seq_len, 1)

            # Normalize K and V magnitudes before folding
            K_max = K.abs().amax(dim=-1, keepdim=True).clamp(min=1e-8)
            V_max = V.abs().amax(dim=-1, keepdim=True).clamp(min=1e-8)
            K_norm = K / K_max
            V_norm = V / V_max

            # Track compression energy (before fold)
            K_mag_before = K_norm.abs().sum()

            # Prepare per-head parameters
            head_kappa = self.head_kappa.view(1, self.max_heads, 1, 1)
            fold_lam = torch.sigmoid(self.fold_lambda).view(1, self.max_heads, 1, 1)

            # ⊙ Fold: compression modulated by resonance
            K = fractal_fold(K_norm, ages, mean_coherence, head_kappa, fold_lam)
            V = fractal_fold(V_norm, ages, mean_coherence, head_kappa, fold_lam)

            compressed_energy = (K_mag_before - K.abs().sum()).detach()
        else:
            compressed_energy = torch.tensor(0.0, device=device)

        # ════════════════════════════════════════
        #  ATTENTION (all parallel)
        # ════════════════════════════════════════
        #
        # Standard scaled dot-product attention. But the K and V are
        # already folded: phase-matched entries have larger magnitudes
        # (they resisted compression), so they naturally dominate the
        # attention weights. No resonance bonus needed; the resonance
        # is IN the field.

        attn_scores = torch.matmul(Q, K.transpose(-2, -1)) * self.scale
        # (batch, max_heads, seq_len, seq_len)

        # Zero dormant heads
        if not active_mask.all():
            dormant_mask = (~active_mask).view(1, self.max_heads, 1, 1)
            attn_scores = attn_scores.masked_fill(dormant_mask, 0.0)

        # Causal mask
        if mask is not None:
            attn_scores = attn_scores.masked_fill(mask == 0, float('-inf'))

        attn_weights = F.softmax(attn_scores, dim=-1)

        # ════════════════════════════════════════
        #  WEIGHTED SUM + RESONANCE GATING (all parallel)
        # ════════════════════════════════════════

        out = torch.matmul(attn_weights, V)
        # (batch, max_heads, seq_len, d_head)

        # Gate each head's output by its resonance with input
        head_gate = head_T.transpose(1, 2).unsqueeze(-1)
        out = out * head_gate

        expressed_energy = out.abs().sum().detach()

        out = out.transpose(1, 2).contiguous().view(batch, seq_len, self.d_model)
        return residual + self.W_o(out), compressed_energy, expressed_energy


# =====================================================================
#  FEED-FORWARD NETWORK (SwiGLU, phi-scaled)
# =====================================================================

class FeedForward(nn.Module):
    """Pre-norm feed-forward with SiLU gating, phi-scaled expansion."""

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
#  POSITIONAL ENCODING (sinusoidal)
# =====================================================================

class SinusoidalPE(nn.Module):
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

    tau = 1 / (2 * ◐) where ◐ in (0, 1), optimal at 0.5.

    ◐ tracks compressed vs expressed energy across the network:
        More compression than expression -> ◐ rises -> tau drops -> decisive
        More expression than compression -> ◐ falls -> tau rises -> exploratory
    """

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
#  ⊙ THE FRACTAL RESONANCE TRANSFORMER v2
# =====================================================================

class FractalResonanceTransformer(nn.Module):
    """
    ⊙ The Fractal Resonance Transformer v2 (Unified Fold)

    Pure attention architecture with the Fractal Fold: compression
    and resonance unified into a single operation on the KV field.

    The 2D attention surface, computed over fractally-folded K/V,
    becomes 3D: the nesting IS the third dimension. Boundary emerges
    from the field folding back on itself. ⊙ in the attention head.

    Each layer is: FractalAttention(fold) + FeedForward.
    All operations are parallel.
    """

    def __init__(self, vocab_size: int, d_model: int = 128,
                 n_heads: int = 8, max_heads: int = None,
                 n_layers: int = 6, kappa: float = KAPPA,
                 fold_lambda: float = FOLD_LAMBDA,
                 dropout: float = 0.0, max_seq_len: int = 2048,
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
        self.vocab_size = vocab_size
        self.enable_growth = enable_growth

        # Embedding + positional encoding
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_enc = SinusoidalPE(d_model, max_seq_len)
        self.embed_dropout = nn.Dropout(dropout)

        # Head manager (shared across layers)
        self.head_manager = DimensionalHeadManager(max_heads)

        # Layers: FractalAttention(fold) + FFN
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

        # Output
        self.final_norm = nn.LayerNorm(d_model)
        self.output_head = nn.Linear(d_model, vocab_size, bias=False)

        # ◐ Balance-as-temperature
        self.balance = BalanceTemperature()

        self._init_weights()

    def _init_weights(self):
        nn.init.normal_(self.embedding.weight, std=0.02)
        nn.init.normal_(self.output_head.weight, std=0.02)

    def _causal_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        return torch.tril(torch.ones(seq_len, seq_len, device=device)).bool()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (batch, seq_len) token indices
        Returns: (batch, seq_len, vocab_size) logits
        """
        batch, seq_len = x.shape
        device = x.device

        h = self.embed_dropout(self.pos_enc(self.embedding(x)))
        mask = self._causal_mask(seq_len, device)

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
        attn_params = sum(p.numel() for l in self.attn_layers for p in l.parameters())
        ff_params = sum(p.numel() for l in self.ff_layers for p in l.parameters())

        lines = [
            "",
            "⊙ FRACTAL RESONANCE TRANSFORMER v2 (Unified Fold)",
            "=" * 55,
            f"  d_model:     {self.d_model}",
            f"  n_heads:     {self.n_heads} active / {self.max_heads} capacity",
            f"  n_layers:    {self.n_layers}",
            f"  vocab_size:  {self.vocab_size}",
            f"  growth:      {'enabled' if self.enable_growth else 'disabled'}",
            f"  total params: {n_params:,}",
            f"    Attn layers: {attn_params:,}",
            f"    FFN layers:  {ff_params:,}",
            "",
            self.head_manager.summary(),
            "",
            f"  Active heads (total): {self.total_active_heads()} "
            f"({self.total_dormant_heads()} dormant)",
            "",
            f"  ◐ (balance):    {self.get_balance():.4f}",
            f"  tau (temperature): {self.get_temperature():.4f}",
            "=" * 55,
        ]
        return "\n".join(lines)


# =====================================================================
#  CONVENIENCE CONFIGS
# =====================================================================

def frt_v2_small(vocab_size: int, **kwargs) -> FractalResonanceTransformer:
    """Small FRT-v2: ~3M params. 8 active heads, room to grow to 16."""
    defaults = dict(d_model=128, n_heads=8, max_heads=16, n_layers=6)
    defaults.update(kwargs)
    return FractalResonanceTransformer(vocab_size, **defaults)


def frt_v2_medium(vocab_size: int, **kwargs) -> FractalResonanceTransformer:
    """Medium FRT-v2: ~25M params. 16 active heads, room to grow to 32."""
    defaults = dict(d_model=256, n_heads=16, max_heads=32, n_layers=8)
    defaults.update(kwargs)
    return FractalResonanceTransformer(vocab_size, **defaults)


def frt_v2_large(vocab_size: int, **kwargs) -> FractalResonanceTransformer:
    """Large FRT-v2: ~100M+ params. 32 active heads, room to grow to 64."""
    defaults = dict(d_model=512, n_heads=32, max_heads=64, n_layers=12)
    defaults.update(kwargs)
    return FractalResonanceTransformer(vocab_size, **defaults)


# =====================================================================
#  MAIN: ARCHITECTURE VERIFICATION
# =====================================================================

if __name__ == '__main__':
    print("\n⊙ THE FRACTAL RESONANCE TRANSFORMER v2 (Unified Fold)")
    print("  Compression and resonance as one operation.")
    print("  '2D field, fractally nesting, becoming 3D.'\n")

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"  Device: {device}\n")

    vocab_size = 256
    model = frt_v2_small(vocab_size).to(device)
    print(model.summary())

    # ════════════════════════════════════════
    #  FORWARD + BACKWARD TEST
    # ════════════════════════════════════════

    batch_size = 4
    seq_len = 64
    x = torch.randint(0, vocab_size, (batch_size, seq_len), device=device)
    target = torch.randint(0, vocab_size, (batch_size, seq_len), device=device)

    print("\n  Forward pass...")
    model.train()
    logits = model(x)
    print(f"  Input:  {x.shape}")
    print(f"  Output: {logits.shape}")
    print(f"  ◐ = {model.get_balance():.4f}  tau = {model.get_temperature():.4f}")

    print("\n  Backward pass...")
    loss = F.cross_entropy(logits.view(-1, vocab_size), target.view(-1))
    loss.backward()
    print(f"  Loss: {loss.item():.4f}")
    n_grad = sum(1 for p in model.parameters() if p.grad is not None and p.grad.abs().sum() > 0)
    n_total = sum(1 for p in model.parameters() if p.requires_grad)
    print(f"  Gradients: {n_grad}/{n_total} parameters received gradients")

    # ════════════════════════════════════════
    #  TIMING BENCHMARK
    # ════════════════════════════════════════

    print(f"\n  Timing benchmark (batch={batch_size}, seq={seq_len})...")

    # Warmup
    for _ in range(5):
        model.zero_grad()
        out = model(x)
        F.cross_entropy(out.view(-1, vocab_size), target.view(-1)).backward()

    n_runs = 20
    t0 = time.time()
    for _ in range(n_runs):
        model.zero_grad()
        out = model(x)
        F.cross_entropy(out.view(-1, vocab_size), target.view(-1)).backward()
    t1 = time.time()
    avg_ms = (t1 - t0) / n_runs * 1000
    print(f"  Avg forward+backward: {avg_ms:.1f} ms")

    # Time a single attention layer
    mask = model._causal_mask(seq_len, device)
    h_test = model.embed_dropout(model.pos_enc(model.embedding(x)))
    attn_layer = model.attn_layers[0]

    for _ in range(5):
        _ = attn_layer(h_test, mask=mask)
    t0 = time.time()
    for _ in range(n_runs):
        _ = attn_layer(h_test, mask=mask)
    t_attn = (time.time() - t0) / n_runs * 1000
    print(f"  Single attn layer: {t_attn:.1f} ms")
    print(f"  Est. all {model.n_layers} attn layers: {t_attn * model.n_layers:.1f} ms")

    # Longer sequence test
    for test_seq in [128, 256, 512]:
        x_long = torch.randint(0, vocab_size, (2, test_seq), device=device)
        t0 = time.time()
        for _ in range(5):
            _ = model(x_long)
        t_long = (time.time() - t0) / 5 * 1000
        print(f"  seq_len={test_seq}: {t_long:.1f} ms (forward only)")

    # ════════════════════════════════════════
    #  HEAD GROWTH TEST
    # ════════════════════════════════════════

    print(f"\n  Head growth test...")
    test_layer = model.attn_layers[0]
    nursery = test_layer.nursery
    srl = test_layer.srl
    print(f"  Nursery: {nursery.n_active}/{nursery.max_heads} active")

    fake_T = torch.full((2, 32, nursery.n_active), 0.1)
    fake_phase = torch.full((2, 32), 2.5)
    for step in range(60):
        result = nursery.step(fake_T, fake_phase, srl, step_number=step)
        if result is not None:
            print(f"  ** Head {result} woke at step {step} "
                  f"({nursery.n_active}/{nursery.max_heads} active)")

    # ════════════════════════════════════════
    #  INFERENCE TEST
    # ════════════════════════════════════════

    print(f"\n  Inference test...")
    model.eval()
    with torch.no_grad():
        logits_eval = model(x)
        probs = F.softmax(logits_eval[0, -1], dim=-1)
        top5 = torch.topk(probs, 5)
        print(f"  Top-5 probs: {[f'{p:.3f}' for p in top5.values.tolist()]}")
        print(f"  tau = {model.get_temperature():.4f}")

    # ════════════════════════════════════════
    #  FOLD VISUALIZATION
    # ════════════════════════════════════════

    print(f"\n  Fold parameter inspection:")
    for i, layer in enumerate(model.attn_layers):
        kappa_vals = F.softplus(layer.head_kappa).detach()
        lambda_vals = torch.sigmoid(layer.fold_lambda).detach()
        active = layer.nursery.active_mask
        active_kappa = kappa_vals[active]
        active_lambda = lambda_vals[active]
        print(f"  Layer {i}: kappa [{active_kappa.min():.3f}, {active_kappa.max():.3f}]  "
              f"lambda [{active_lambda.min():.3f}, {active_lambda.max():.3f}]")

    print(f"\n  Final: {model.total_active_heads()} active, "
          f"{model.total_dormant_heads()} dormant, "
          f"◐ = {model.get_balance():.4f}")

    print("\n  ⊙ All checks passed.")
    print("  Unified fold: compression and resonance are one breath.")
    print("  '2D field, fractally nesting, becoming 3D.'\n")
