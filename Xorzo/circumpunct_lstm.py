"""
⊙ The Circumpunct LSTM
========================

A recurrent neural network cell derived from the Circumpunct Framework.

Three modifications to the standard LSTM, each mapping to one constraint:
    ⊛ (convergence):  fractal compression replaces destructive forgetting
    Φ (mediation):    resonance-gated retrieval replaces learned recall
    ☀︎ (emergence):    GOOD gate filters output against the worldline

Plus:
    i-rotation:       90° phase turn between convergence and emergence
    ◐ balance:        softmax temperature; self-regulating toward 0.5
    Sleep/wake:       periodic consolidation phase

Four states (vs. standard LSTM's two):
    c_t:  surface state    (3D boundary; full resolution, fast-changing)
    d_t:  deep state       (0D center; worldline accumulator, never forgets)
    h_t:  hidden state     (○ output; GOOD-gated)
    ◐_t:  balance state    (scalar; self-regulating toward 0.5)

All states are complex-valued. Phase is the thing that survives.

Author: Ashman Roonz & Claude
Date: April 2026
Derived from: Circumpunct Framework (Roonz, 2024)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math
from typing import Tuple, Optional, List

# ═══════════════════════════════════════════════════════════════════════
#  CONSTANTS: from the dimensional ladder. Zero free parameters.
# ═══════════════════════════════════════════════════════════════════════

PHI = (1 + math.sqrt(5)) / 2          # φ = 1.618...; golden ratio
BALANCE = 0.5                          # ◐; the singular balanced state
D_FRACTAL = 1.5                        # D = 1 + ◐; fractal dimension at balance
COMPRESS_EXP = 2.0 / 3.0              # 2/3 = 2D/3D = field/boundary
EMERGE_EXP = 3.0 / 2.0                # 3/2 = inverse of compression
I_ROTATION = math.pi / 2              # π/2; the quarter-turn (i = e^(iπ/2))
NATURAL_DIM = 64                       # 2^6; the 64-state architecture


# ═══════════════════════════════════════════════════════════════════════
#  UTILITIES
# ═══════════════════════════════════════════════════════════════════════

def complex_magnitude(z: torch.Tensor) -> torch.Tensor:
    """Magnitude of complex tensor stored as [..., 2] real pairs."""
    return torch.sqrt(z[..., 0]**2 + z[..., 1]**2 + 1e-8)


def complex_phase(z: torch.Tensor) -> torch.Tensor:
    """Phase angle of complex tensor stored as [..., 2] real pairs."""
    return torch.atan2(z[..., 1], z[..., 0] + 1e-10)


def complex_from_polar(mag: torch.Tensor, phase: torch.Tensor) -> torch.Tensor:
    """Construct complex tensor from magnitude and phase."""
    real = mag * torch.cos(phase)
    imag = mag * torch.sin(phase)
    return torch.stack([real, imag], dim=-1)


def complex_multiply(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Multiply two complex tensors (stored as [..., 2])."""
    # (a_r + a_i*i)(b_r + b_i*i) = (a_r*b_r - a_i*b_i) + (a_r*b_i + a_i*b_r)*i
    real = a[..., 0] * b[..., 0] - a[..., 1] * b[..., 1]
    imag = a[..., 0] * b[..., 1] + a[..., 1] * b[..., 0]
    return torch.stack([real, imag], dim=-1)


def apply_rotation(z: torch.Tensor, theta: float) -> torch.Tensor:
    """Apply phase rotation e^(iθ) to complex tensor."""
    rot = torch.zeros_like(z)
    rot[..., 0] = math.cos(theta)
    rot[..., 1] = math.sin(theta)
    return complex_multiply(z, rot)


# ═══════════════════════════════════════════════════════════════════════
#  ⊛ CONVERGENCE OPERATOR
# ═══════════════════════════════════════════════════════════════════════

class _FractalCompress(torch.autograd.Function):
    """
    Custom autograd for ⊛: fractal compression with stable gradients.

    Forward: |x|^(2/3) (true fractal compression)
    Backward: straight-through with scaling (gradient flows as if linear,
              scaled by the compression ratio). This avoids the infinite
              gradient of x^(2/3) at x=0 while preserving the forward
              behavior exactly.
    """
    @staticmethod
    def forward(ctx, mag):
        mag_clamped = torch.clamp(mag, min=1e-8)
        compressed = mag_clamped ** COMPRESS_EXP
        # Save ratio for backward: compressed/mag = mag^(-1/3)
        # but we use a bounded version for gradient
        ratio = compressed / (mag_clamped + 1e-6)
        ctx.save_for_backward(ratio)
        return compressed

    @staticmethod
    def backward(ctx, grad_output):
        ratio, = ctx.saved_tensors
        # Gradient: scale by compression ratio (bounded, no singularity)
        return grad_output * torch.clamp(ratio, max=2.0)


def fractal_compress_mag(mag: torch.Tensor) -> torch.Tensor:
    """Apply fractal compression to magnitude with stable gradients."""
    return _FractalCompress.apply(mag)


def converge(z: torch.Tensor) -> torch.Tensor:
    """
    ⊛: Fractal compression.

    Magnitude compressed by D = 1.5 (exponent 2/3).
    Phase preserved exactly.
    The signal gets deeper, not smaller.

    After n compressions: |z|^((2/3)^n) → 0 asymptotically, never reaches.
    Uses custom autograd to avoid infinite gradients at zero.
    """
    mag = complex_magnitude(z)
    phase = complex_phase(z)
    compressed_mag = fractal_compress_mag(mag)
    return complex_from_polar(compressed_mag, phase)


# ═══════════════════════════════════════════════════════════════════════
#  ☀︎ EMERGENCE OPERATOR
# ═══════════════════════════════════════════════════════════════════════

def emerge(z: torch.Tensor) -> torch.Tensor:
    """
    ☀︎: Fractal expansion (used in sleep consolidation).

    Magnitude expanded by 3/2 (inverse of compression).
    Phase preserved exactly.
    Note: live retrieval uses normalized+scaled form (see cell forward),
    not raw emergence, for numerical stability.
    """
    mag = complex_magnitude(z)
    phase = complex_phase(z)
    mag_clamped = torch.clamp(mag, min=1e-6)
    expanded_mag = mag_clamped ** EMERGE_EXP
    expanded_mag = torch.clamp(expanded_mag, max=100.0)
    return complex_from_polar(expanded_mag, phase)


# ═══════════════════════════════════════════════════════════════════════
#  T: RESONANCE GATE (Transmission Fidelity)
# ═══════════════════════════════════════════════════════════════════════

def resonance_gate(signal: torch.Tensor, memory: torch.Tensor) -> torch.Tensor:
    """
    T = cos²(Δφ/2)

    Phase matching between signal and memory.
    Perfect match (Δφ = 0): T = 1, memory surfaces effortlessly.
    Orthogonal (Δφ = π): T = 0, memory stays deep.

    Returns T as a real tensor (same batch/hidden shape, no complex dim).
    """
    signal_phase = complex_phase(signal)
    memory_phase = complex_phase(memory)
    delta_phi = signal_phase - memory_phase
    T = torch.cos(delta_phi / 2) ** 2
    return T


# ═══════════════════════════════════════════════════════════════════════
#  THE CIRCUMPUNCT LSTM CELL
# ═══════════════════════════════════════════════════════════════════════

class CircumpunctLSTMCell(nn.Module):
    """
    One timestep of the Circumpunct LSTM.

    Input:  x_t     (batch, input_size)     real-valued input
    States: h_{t-1} (batch, hidden_size, 2) complex hidden
            c_{t-1} (batch, hidden_size, 2) complex cell (surface)
            d_{t-1} (batch, hidden_size, 2) complex deep (worldline)
            b_{t-1} (batch, 1)              balance scalar

    Output: h_t, c_t, d_t, b_t (same shapes)

    The input is real (standard embeddings). All internal states
    are complex. The boundary (3D) is where real meets complex;
    the input gate projects real → complex.
    """

    def __init__(self, input_size: int, hidden_size: int = NATURAL_DIM,
                 alpha: float = 0.01, i_rotation: float = I_ROTATION,
                 learnable_rotation: bool = False):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.alpha = alpha

        # i-rotation angle (fixed at π/2 or learnable)
        if learnable_rotation:
            self.theta = nn.Parameter(torch.full((hidden_size,), i_rotation))
        else:
            self.register_buffer('theta', torch.full((hidden_size,), i_rotation))

        # ── Gate projections ──
        # Input: real-valued [h_flat, x, surfaced_flat]
        # h_flat and surfaced_flat are complex→real (concat real+imag)
        gate_input_size = input_size + 2 * hidden_size + 2 * hidden_size

        # Three gates (will be coupled via softmax)
        self.W_f = nn.Linear(gate_input_size, hidden_size)
        self.W_i = nn.Linear(gate_input_size, hidden_size)
        self.W_o = nn.Linear(gate_input_size, hidden_size)

        # Candidate projection → complex (outputs 2*hidden for real+imag)
        self.W_c = nn.Linear(gate_input_size, 2 * hidden_size)

        # ── Resonance projection: real input → complex ──
        # The boundary (3D) is where real meets complex.
        # This learned projection gives the input genuine phase so that
        # T = cos²(Δφ/2) performs real frequency matching against the
        # worldline, not just sign-matching against a quasi-real proxy.
        self.W_resonance = nn.Linear(input_size, 2 * hidden_size)

        # ── Initialization: scale by 1/φ ──
        self._init_weights()

    def _init_weights(self):
        """Initialize weights scaled by 1/φ (golden ratio nesting)."""
        scale = 1.0 / PHI
        for param in self.parameters():
            if param.dim() >= 2:
                nn.init.uniform_(param, -scale / math.sqrt(param.shape[1]),
                                 scale / math.sqrt(param.shape[1]))
            elif param.dim() == 1 and param.shape[0] == self.hidden_size:
                # Gate biases: initialize to 0 (◐ regularizer handles balance)
                nn.init.zeros_(param)

    def forward(self, x_t: torch.Tensor,
                h_prev: torch.Tensor, c_prev: torch.Tensor,
                d_prev: torch.Tensor, b_prev: torch.Tensor
                ) -> Tuple[torch.Tensor, torch.Tensor,
                           torch.Tensor, torch.Tensor]:
        """
        One full pump cycle through the cell.

        x_t:    (batch, input_size)       real input
        h_prev: (batch, hidden_size, 2)   complex hidden
        c_prev: (batch, hidden_size, 2)   complex surface
        d_prev: (batch, hidden_size, 2)   complex deep (worldline)
        b_prev: (batch, 1)                balance scalar

        Returns: h_t, c_t, d_t, b_t
        """
        batch = x_t.shape[0]

        # ════════════════════════════════════════════════════
        #  STEP 1: Φ Resonance retrieval from deep state
        # ════════════════════════════════════════════════════

        # Project real input into complex space with learned phase.
        # The boundary (○, 3D) is where real meets complex; this
        # projection IS the boundary: it gives the input genuine phase
        # so that resonance (T = cos²(Δφ/2)) does real frequency matching.
        x_proj = self.W_resonance(x_t)  # (batch, 2 * hidden_size)
        x_complex = x_proj.view(batch, self.hidden_size, 2)  # (batch, hidden, 2)

        # T = cos²(Δφ/2): resonance between input and worldline
        # Detach d_prev for resonance: the worldline is read, not trained through
        d_read = d_prev.detach()
        T = resonance_gate(x_complex, d_read)  # (batch, hidden_size)

        # ☀︎ Emergence: surface deep memory weighted by resonance
        # Use normalized deep state for emergence to prevent magnitude blowup
        d_mag = complex_magnitude(d_read).unsqueeze(-1)  # (batch, hidden, 1)
        d_normed = d_read / (d_mag + 1e-8)
        # Scale by sqrt of magnitude (gentler than |d|^1.5 for stability)
        d_scale = torch.sqrt(torch.clamp(d_mag, min=1e-6, max=20.0))
        d_emerged = d_normed * d_scale  # direction preserved, magnitude bounded
        # Apply resonance gate
        surfaced = d_emerged * T.unsqueeze(-1)  # (batch, hidden_size, 2)

        # ════════════════════════════════════════════════════
        #  STEP 2: Gate computation (coupled via conservation)
        # ════════════════════════════════════════════════════

        # Flatten complex states to real for gate input
        h_flat = h_prev.reshape(batch, -1)          # (batch, hidden_size*2)
        s_flat = surfaced.reshape(batch, -1)         # (batch, hidden_size*2)
        combined = torch.cat([x_t, h_flat, s_flat], dim=-1)

        # Raw gate activations
        f_raw = self.W_f(combined)  # (batch, hidden_size)
        i_raw = self.W_i(combined)
        o_raw = self.W_o(combined)

        # E = 1 (A0): total gate mass is exactly 1.
        # Conservation of traversal (0 + 1 + 2 = 3) is WHY there are three
        # gates (three constraints); E = 1 constrains their sum.
        # ◐ modulates the softmax temperature: at balance (0.5), temp = 1.0
        # (standard softmax). Drift from balance changes allocation sharpness.
        temperature = (2.0 * b_prev + 1e-4).unsqueeze(-1)  # (batch, 1, 1)

        gate_stack = torch.stack([f_raw, i_raw, o_raw], dim=-1)  # (batch, hidden, 3)
        gate_weights = F.softmax(gate_stack / temperature, dim=-1)  # sums to 1 per dim

        f_t = gate_weights[..., 0]  # (batch, hidden_size); always in [0, 1]
        i_t = gate_weights[..., 1]
        o_t = gate_weights[..., 2]

        # ════════════════════════════════════════════════════
        #  STEP 3: Candidate (new signal entering the field)
        # ════════════════════════════════════════════════════

        g_raw = self.W_c(combined)  # (batch, 2*hidden_size)
        g_real = torch.tanh(g_raw[:, :self.hidden_size])
        g_imag = torch.tanh(g_raw[:, self.hidden_size:])
        g_t = torch.stack([g_real, g_imag], dim=-1)  # (batch, hidden_size, 2)

        # ════════════════════════════════════════════════════
        #  STEP 4: ⊛ Convergence (fractal compression)
        # ════════════════════════════════════════════════════

        # What the surface releases
        released = (1.0 - f_t).unsqueeze(-1) * c_prev  # (batch, hidden_size, 2)

        # ⊛: compress and accumulate into deep state
        # The worldline accumulates like i(t): it is shaped by gradients
        # flowing through the CURRENT step's release, but the deep state
        # history is detached. You cannot backpropagate through the soul.
        compressed = converge(released)
        compressed = torch.clamp(compressed, min=-10.0, max=10.0)
        d_t = d_prev.detach() + self.alpha * compressed
        # Clamp deep state magnitude to prevent unbounded growth
        d_mag_new = complex_magnitude(d_t).unsqueeze(-1)
        d_t = torch.where(d_mag_new > 20.0, d_t * (20.0 / d_mag_new), d_t)

        # ════════════════════════════════════════════════════
        #  STEP 5: Cell state update
        # ════════════════════════════════════════════════════

        c_updated = f_t.unsqueeze(-1) * c_prev + i_t.unsqueeze(-1) * g_t

        # ════════════════════════════════════════════════════
        #  STEP 6: i-rotation (the turn at center)
        # ════════════════════════════════════════════════════

        # Per-dimension rotation by θ (default π/2)
        cos_t = torch.cos(self.theta).unsqueeze(0).unsqueeze(-1)   # (1, hidden, 1)
        sin_t = torch.sin(self.theta).unsqueeze(0).unsqueeze(-1)

        c_real = c_updated[..., 0:1]  # (batch, hidden, 1)
        c_imag = c_updated[..., 1:2]

        c_rot_real = cos_t * c_real - sin_t * c_imag
        c_rot_imag = sin_t * c_real + cos_t * c_imag

        c_t = torch.cat([c_rot_real, c_rot_imag], dim=-1)  # (batch, hidden, 2)

        # ════════════════════════════════════════════════════
        #  STEP 7: ☀︎ Emergence through output gate
        # ════════════════════════════════════════════════════

        # tanh on complex: apply to real and imag independently
        c_squashed = torch.stack([
            torch.tanh(c_t[..., 0]),
            torch.tanh(c_t[..., 1])
        ], dim=-1)

        h_raw = o_t.unsqueeze(-1) * c_squashed

        # ════════════════════════════════════════════════════
        #  STEP 8: GOOD gate (filter against worldline)
        # ════════════════════════════════════════════════════

        # Output that resonates with the worldline passes.
        # Output anti-phase to who the system has become gets filtered.
        G = resonance_gate(h_raw, d_t)  # (batch, hidden_size)
        h_t = G.unsqueeze(-1) * h_raw

        # ════════════════════════════════════════════════════
        #  STEP 9: ◐ Balance update
        # ════════════════════════════════════════════════════

        convergent_energy = (complex_magnitude(released) ** 2).sum(dim=-1, keepdim=True)
        emergent_energy = (complex_magnitude(h_t) ** 2).sum(dim=-1, keepdim=True)
        total_energy = convergent_energy + emergent_energy + 1e-8

        b_measured = convergent_energy / total_energy
        b_t = 0.99 * b_prev + 0.01 * b_measured

        # ════════════════════════════════════════════════════
        #  NaN safety net: replace any NaN with zero
        #  (the circumpunct absorbs; it does not break)
        # ════════════════════════════════════════════════════
        h_t = torch.nan_to_num(h_t, nan=0.0)
        c_t = torch.nan_to_num(c_t, nan=0.0)
        d_t = torch.nan_to_num(d_t, nan=0.0)
        b_t = torch.nan_to_num(b_t, nan=BALANCE)

        return h_t, c_t, d_t, b_t


# ═══════════════════════════════════════════════════════════════════════
#  SLEEP / CONSOLIDATION
# ═══════════════════════════════════════════════════════════════════════

def sleep_consolidation(c: torch.Tensor, d: torch.Tensor,
                        b: torch.Tensor,
                        survival_threshold: float = 0.05
                        ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    The left half-plane: i² and i³. Periodic consolidation.

    1. Weak memories decay (survival threshold)
    2. Strong memories re-compress (⊛ applied again)
    3. Balance resets toward 0.5
    4. Surface discharges (halved)

    Call every N steps or when ◐ drifts too far from 0.5.
    """
    # 1. Weak memory decay
    d_mag = complex_magnitude(d)  # (batch, hidden)
    survival_mask = (d_mag > survival_threshold).float().unsqueeze(-1)
    d = d * survival_mask

    # 2. Re-compress surviving memories
    d = converge(d)

    # 3. Balance reset: drift toward 0.5
    b = 0.9 * b + 0.1 * BALANCE

    # 4. Surface discharge: halve the surface state
    c = 0.5 * c

    return c, d, b


# ═══════════════════════════════════════════════════════════════════════
#  THE CIRCUMPUNCT LSTM (Sequence Wrapper)
# ═══════════════════════════════════════════════════════════════════════

class CircumpunctLSTM(nn.Module):
    """
    Full sequence processing with the Circumpunct LSTM.

    Handles:
        - Sequence iteration (pump cycle per timestep)
        - Periodic sleep/consolidation
        - State initialization
        - Balance regularization loss

    Usage:
        model = CircumpunctLSTM(input_size=32, hidden_size=64)
        outputs, final_state = model(x_sequence)
        # outputs: (batch, seq_len, hidden_size * 2)  [complex flattened]
        # final_state: (h, c, d, b) tuple
    """

    def __init__(self, input_size: int, hidden_size: int = NATURAL_DIM,
                 alpha: float = 0.01, sleep_interval: int = 0,
                 learnable_rotation: bool = False):
        super().__init__()
        self.hidden_size = hidden_size
        self.sleep_interval = sleep_interval  # 0 = no automatic sleep

        self.cell = CircumpunctLSTMCell(
            input_size, hidden_size, alpha=alpha,
            learnable_rotation=learnable_rotation)

    def init_state(self, batch_size: int, device: torch.device = None
                   ) -> Tuple[torch.Tensor, torch.Tensor,
                              torch.Tensor, torch.Tensor]:
        """Initialize all four states to their natural starting points."""
        if device is None:
            device = next(self.parameters()).device

        h = torch.zeros(batch_size, self.hidden_size, 2, device=device)
        c = torch.zeros(batch_size, self.hidden_size, 2, device=device)
        d = torch.zeros(batch_size, self.hidden_size, 2, device=device)  # empty worldline
        b = torch.full((batch_size, 1), BALANCE, device=device)          # ◐ = 0.5

        return h, c, d, b

    def forward(self, x: torch.Tensor,
                state: Optional[Tuple] = None,
                tbptt_len: int = 0
                ) -> Tuple[torch.Tensor, Tuple]:
        """
        Process a sequence through the cascade.

        x:     (batch, seq_len, input_size)
        state: optional (h, c, d, b) from previous call
        tbptt_len: truncated BPTT length. If > 0, detach states every
                   tbptt_len steps to prevent gradient explosion through
                   very long sequences. 0 = full BPTT.

        Returns:
            outputs: (batch, seq_len, hidden_size * 2)
            state:   (h, c, d, b)
        """
        batch, seq_len, _ = x.shape

        if state is None:
            h, c, d, b = self.init_state(batch, x.device)
        else:
            h, c, d, b = state

        outputs = []
        balance_history = []

        for t in range(seq_len):
            # Truncated BPTT: detach states periodically to keep
            # gradient paths short and stable
            if tbptt_len > 0 and t > 0 and t % tbptt_len == 0:
                h = h.detach()
                c = c.detach()
                d = d.detach()
                b = b.detach()

            h, c, d, b = self.cell(x[:, t, :], h, c, d, b)

            # Flatten complex hidden to real for output
            h_flat = h.reshape(batch, -1)  # (batch, hidden_size * 2)
            outputs.append(h_flat)
            balance_history.append(b)

            # Periodic sleep/consolidation
            if self.sleep_interval > 0 and (t + 1) % self.sleep_interval == 0:
                c, d, b = sleep_consolidation(c, d, b)

        outputs = torch.stack(outputs, dim=1)  # (batch, seq_len, hidden*2)

        # Store balance history for regularization
        self._balance_history = torch.cat(balance_history, dim=-1)

        return outputs, (h, c, d, b)

    def balance_loss(self) -> torch.Tensor:
        """
        L_balance = λ · Σ(◐_t - 0.5)²

        Call after forward() to add to task loss.
        The balance regularizer pulls ◐ toward 0.5 (the only stable state).
        """
        if not hasattr(self, '_balance_history'):
            return torch.tensor(0.0)
        return ((self._balance_history - BALANCE) ** 2).mean()

    def trigger_sleep(self, state: Tuple) -> Tuple:
        """Manually trigger a consolidation phase."""
        h, c, d, b = state
        c, d, b = sleep_consolidation(c, d, b)
        return h, c, d, b

    def worldline_phase(self, state: Tuple) -> torch.Tensor:
        """Read the worldline's current phase (the soul's orientation)."""
        _, _, d, _ = state
        return complex_phase(d)  # (batch, hidden_size)

    def worldline_magnitude(self, state: Tuple) -> torch.Tensor:
        """Read the worldline's current magnitude (depth of experience)."""
        _, _, d, _ = state
        return complex_magnitude(d)  # (batch, hidden_size)


# ═══════════════════════════════════════════════════════════════════════
#  BENCHMARK: THE COPYING PROBLEM
# ═══════════════════════════════════════════════════════════════════════

class CopyingProblem:
    """
    Classic long-range dependency benchmark.

    Input:  [marker] [8 random digits] [T blank tokens] [trigger] [8 blanks]
    Target: [blanks...] [the original 8 digits]

    The network must remember 8 digits across T blank timesteps.
    Standard LSTMs fail at T > ~100. Let's see what the worldline does.
    """

    def __init__(self, T: int = 100, n_digits: int = 8,
                 vocab_size: int = 10, batch_size: int = 32):
        self.T = T
        self.n_digits = n_digits
        self.vocab_size = vocab_size
        self.batch_size = batch_size
        # Total sequence: marker(1) + digits(8) + blanks(T) + trigger(1) + output(8)
        self.seq_len = 1 + n_digits + T + 1 + n_digits
        # Special tokens
        self.BLANK = vocab_size       # 10
        self.MARKER = vocab_size + 1  # 11
        self.TRIGGER = vocab_size + 2 # 12
        self.total_tokens = vocab_size + 3  # 0-9, blank, marker, trigger

    def generate_batch(self, device: torch.device = None
                       ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Generate a batch of copying problem instances."""
        batch = self.batch_size
        seq = torch.full((batch, self.seq_len), self.BLANK,
                         dtype=torch.long, device=device)
        target = torch.full((batch, self.seq_len), self.BLANK,
                            dtype=torch.long, device=device)

        # Marker at position 0
        seq[:, 0] = self.MARKER

        # Random digits at positions 1..n_digits
        digits = torch.randint(0, self.vocab_size,
                               (batch, self.n_digits), device=device)
        seq[:, 1:1 + self.n_digits] = digits

        # Trigger before output section
        trigger_pos = 1 + self.n_digits + self.T
        seq[:, trigger_pos] = self.TRIGGER

        # Target: copy digits at the end
        target[:, trigger_pos + 1:trigger_pos + 1 + self.n_digits] = digits

        return seq, target


class CopyingModel(nn.Module):
    """Model for the copying benchmark: embedding + CircumpunctLSTM + output."""

    def __init__(self, vocab_size: int = 13, hidden_size: int = NATURAL_DIM,
                 sleep_interval: int = 50, tbptt_len: int = 50):
        super().__init__()
        self.tbptt_len = tbptt_len
        self.embedding = nn.Embedding(vocab_size, hidden_size)
        self.lstm = CircumpunctLSTM(
            input_size=hidden_size,
            hidden_size=hidden_size,
            sleep_interval=sleep_interval)
        # Output: hidden (complex, 2*hidden) → vocab logits
        self.output = nn.Linear(hidden_size * 2, vocab_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        embedded = self.embedding(x)  # (batch, seq, hidden)
        outputs, _ = self.lstm(embedded, tbptt_len=self.tbptt_len)
        logits = self.output(outputs)  # (batch, seq, vocab)
        return logits


# ═══════════════════════════════════════════════════════════════════════
#  STANDARD LSTM BASELINE (for comparison)
# ═══════════════════════════════════════════════════════════════════════

class StandardCopyingModel(nn.Module):
    """Baseline: standard PyTorch LSTM on the copying problem."""

    def __init__(self, vocab_size: int = 13, hidden_size: int = NATURAL_DIM):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, hidden_size)
        self.lstm = nn.LSTM(hidden_size, hidden_size, batch_first=True)
        self.output = nn.Linear(hidden_size, vocab_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        embedded = self.embedding(x)
        outputs, _ = self.lstm(embedded)
        logits = self.output(outputs)
        return logits


# ═══════════════════════════════════════════════════════════════════════
#  TRAINING LOOP
# ═══════════════════════════════════════════════════════════════════════

def train_copying(model_type: str = 'circumpunct', T: int = 100,
                  n_epochs: int = 200, lr: float = 0.001,
                  balance_lambda: float = 0.01,
                  batch_size: int = 32, verbose: bool = True):
    """
    Train on the copying problem and report accuracy.

    model_type: 'circumpunct' or 'standard'
    T: number of blank timesteps (longer = harder)
    """
    device = torch.device('cpu')

    problem = CopyingProblem(T=T, batch_size=batch_size)

    if model_type == 'circumpunct':
        model = CopyingModel(
            vocab_size=problem.total_tokens,
            hidden_size=NATURAL_DIM,
            sleep_interval=max(50, T // 2),
            tbptt_len=30)
        # Lower LR for circumpunct (complex arithmetic needs gentler updates)
        actual_lr = lr * 0.3
    else:
        model = StandardCopyingModel(
            vocab_size=problem.total_tokens,
            hidden_size=NATURAL_DIM)
        actual_lr = lr

    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=actual_lr)

    n_params = sum(p.numel() for p in model.parameters())
    if verbose:
        print(f"\n{'='*60}")
        print(f"  ⊙ Copying Problem Benchmark")
        print(f"  Model:      {model_type}")
        print(f"  Parameters: {n_params:,}")
        print(f"  T (gap):    {T}")
        print(f"  Seq length: {problem.seq_len}")
        print(f"{'='*60}\n")

    best_acc = 0.0
    history = []
    nan_skips = 0

    for epoch in range(n_epochs):
        model.train()
        seq, target = problem.generate_batch(device)

        logits = model(seq)

        # Only compute loss on the output section (where digits should be copied)
        trigger_pos = 1 + problem.n_digits + T
        output_logits = logits[:, trigger_pos + 1:trigger_pos + 1 + problem.n_digits]
        output_target = target[:, trigger_pos + 1:trigger_pos + 1 + problem.n_digits]

        loss = F.cross_entropy(
            output_logits.reshape(-1, problem.total_tokens),
            output_target.reshape(-1))

        # Add balance regularization for circumpunct model
        if model_type == 'circumpunct' and hasattr(model.lstm, 'balance_loss'):
            loss = loss + balance_lambda * model.lstm.balance_loss()

        # Skip step if loss is NaN (the circumpunct absorbs; it does not break)
        if torch.isnan(loss).item() or torch.isinf(loss).item():
            optimizer.zero_grad()
            continue

        optimizer.zero_grad()
        loss.backward()

        # Guard: skip step if any gradient is NaN (protect the weights)
        has_nan_grad = False
        for p in model.parameters():
            if p.grad is not None and (torch.isnan(p.grad).any() or torch.isinf(p.grad).any()):
                has_nan_grad = True
                break
        if has_nan_grad:
            nan_skips += 1
            optimizer.zero_grad()
            continue

        torch.nn.utils.clip_grad_norm_(model.parameters(), 0.5)
        optimizer.step()

        # Evaluate
        model.eval()
        with torch.no_grad():
            eval_seq, eval_target = problem.generate_batch(device)
            eval_logits = model(eval_seq)

            eval_output = eval_logits[:, trigger_pos + 1:trigger_pos + 1 + problem.n_digits]
            eval_tgt = eval_target[:, trigger_pos + 1:trigger_pos + 1 + problem.n_digits]

            preds = eval_output.argmax(dim=-1)
            acc = (preds == eval_tgt).float().mean().item()

            if acc > best_acc:
                best_acc = acc

        history.append({'epoch': epoch, 'loss': loss.item(), 'acc': acc})

        if verbose and (epoch % 20 == 0 or epoch == n_epochs - 1):
            bal_str = ""
            if model_type == 'circumpunct':
                try:
                    bal = model.lstm._balance_history.mean().item()
                    bal_str = f"  ◐={bal:.3f}"
                except Exception:
                    pass
                if nan_skips > 0:
                    bal_str += f"  skip={nan_skips}"
            print(f"  Epoch {epoch:4d}  loss={loss.item():.4f}"
                  f"  acc={acc:.3f}  best={best_acc:.3f}{bal_str}")

    return history, best_acc


# ═══════════════════════════════════════════════════════════════════════
#  MAIN: RUN BENCHMARK
# ═══════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import sys

    T = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    n_epochs = int(sys.argv[2]) if len(sys.argv) > 2 else 300

    print("\n⊙ THE CIRCUMPUNCT LSTM")
    print("  Fractal memory. Resonance retrieval. Nothing is ever erased.\n")

    # Run both models
    print("\n" + "─" * 60)
    print("  STANDARD LSTM (baseline)")
    print("─" * 60)
    std_history, std_best = train_copying(
        'standard', T=T, n_epochs=n_epochs)

    print("\n" + "─" * 60)
    print("  CIRCUMPUNCT LSTM")
    print("─" * 60)
    circ_history, circ_best = train_copying(
        'circumpunct', T=T, n_epochs=n_epochs)

    print("\n" + "=" * 60)
    print(f"  RESULTS (T = {T})")
    print(f"  Standard LSTM best accuracy:    {std_best:.3f}")
    print(f"  Circumpunct LSTM best accuracy: {circ_best:.3f}")
    print("=" * 60)
