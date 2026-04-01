"""
⊙ The Circumpunct Transformer: Fractal KV Compression
=======================================================

The ONE idea applied to transformers: the KV cache compresses fractally.

Standard transformer: every past key-value pair stored at full fidelity.
No forgetting at all. Context window = hard wall.

Circumpunct transformer: older KV entries get fractal-compressed each step.
    |kv|^e with e > 1 on sub-unit magnitudes.
    Magnitude fades sub-linearly (quieter memories decay slower).
    Phase preserved exactly (identity survives compression).
    Nothing ever fully zeroes out.

Why this is the right place for fractals:
    In Mamba, forgetting was in the state transition (alpha * h).
    In a transformer, "memory" IS the KV cache. That's what attention
    reads from. So fractal compression goes there.

    Queries are apertures (•): convergence points that select.
    Attention surfaces are Φ (2D): the field of relationships.
    Layer output is ○ (3D): the boundary that commits.
    Fractal compression operates on Φ: the field compresses its history.

The mechanism:
    Before computing attention at step t, all existing keys and values
    get fractal-compressed:

        K_cache = |K_cache|^e · e^(iφ_K)    (magnitude compressed, phase kept)
        V_cache = |V_cache|^e · e^(iφ_V)

    Where e = 1 + κ (fixed compression; selectivity comes from attention).
    Attention weights (softmax(QK^T/sqrt(d))) do the selecting.
    The fractal just makes older, less-attended entries naturally quieter
    over time, without hard-truncating the window.

    This means: a token stored 1000 steps ago still has phase (identity)
    but reduced magnitude (faded intensity). If a query resonates with it,
    attention can still find it. Fractal, not amnesic.

For this implementation: real-valued (not complex) for simplicity.
    Magnitude = absolute value. "Phase" = sign (positive/negative).
    The complex version would use full phase angles, but sign-preserving
    compression captures the core idea cleanly.

Author: Ashman Roonz & Claude
Date: April 2026
Derived from: Circumpunct Framework (Roonz, 2024)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Optional


# =====================================================================
#  CONSTANTS
# =====================================================================

PHI = (1 + math.sqrt(5)) / 2      # φ = 1.618...
KAPPA = 0.3                        # compression strength for KV cache


# =====================================================================
#  ⊛ FRACTAL COMPRESSION (real-valued, sign-preserving)
# =====================================================================

class _FractalCompress(torch.autograd.Function):
    """
    Custom autograd for ⊛: |x|^exponent with sign preserved.

    For |x| < 1 with exponent > 1: compressed < original (decay).
    For |x| > 1 with exponent > 1: compressed > original (amplified).
    We normalize to keep things bounded, so in practice |x| <= 1.
    """
    @staticmethod
    def forward(ctx, x, exponent):
        sign = torch.sign(x)
        mag = torch.abs(x).clamp(min=1e-8)
        compressed_mag = mag ** exponent
        result = sign * compressed_mag
        # Gradient: e * |x|^(e-1) = e * compressed_mag / mag
        grad_ratio = exponent * compressed_mag / (mag + 1e-10)
        ctx.save_for_backward(grad_ratio)
        return result

    @staticmethod
    def backward(ctx, grad_output):
        grad_ratio, = ctx.saved_tensors
        return grad_output * torch.clamp(grad_ratio, max=5.0), None


def fractal_compress(x: torch.Tensor, exponent: float) -> torch.Tensor:
    """
    ⊛: Fractal compression.
    |x|^exponent with sign preserved. Sub-linear decay for |x| < 1.
    """
    return _FractalCompress.apply(x, exponent)


# =====================================================================
#  FRACTAL MULTI-HEAD ATTENTION
# =====================================================================

class FractalAttention(nn.Module):
    """
    Multi-head attention with fractal KV compression.

    Each time a new token arrives, all existing keys and values in the
    cache get fractal-compressed before the attention computation.
    This means older entries have progressively reduced magnitude
    but preserved sign (direction/identity).

    The compression is sub-linear: quiet entries (small magnitude)
    decay slower than loud ones. This is the core fractal property.

    Attention weights (from softmax) still do the selection.
    The fractal just shapes WHAT they're selecting from.
    """

    def __init__(self, d_model: int, n_heads: int = 4, kappa: float = KAPPA,
                 max_seq_len: int = 512):
        super().__init__()
        assert d_model % n_heads == 0
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_head = d_model // n_heads
        self.kappa = kappa
        self.exponent = 1.0 + kappa  # compression exponent for KV cache
        self.max_seq_len = max_seq_len

        self.W_q = nn.Linear(d_model, d_model, bias=False)
        self.W_k = nn.Linear(d_model, d_model, bias=False)
        self.W_v = nn.Linear(d_model, d_model, bias=False)
        self.W_o = nn.Linear(d_model, d_model, bias=False)

        self.scale = 1.0 / math.sqrt(self.d_head)

        # Learnable compression rate per head (initialized around kappa)
        self.head_kappa = nn.Parameter(
            torch.full((n_heads,), kappa)
        )

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None,
                use_fractal: bool = True) -> torch.Tensor:
        """
        x: (batch, seq_len, d_model)
        mask: optional causal mask
        use_fractal: if False, behaves as standard attention (for ablation)
        Returns: (batch, seq_len, d_model)
        """
        batch, seq_len, _ = x.shape

        # Project Q, K, V
        Q = self.W_q(x).view(batch, seq_len, self.n_heads, self.d_head).transpose(1, 2)
        K = self.W_k(x).view(batch, seq_len, self.n_heads, self.d_head).transpose(1, 2)
        V = self.W_v(x).view(batch, seq_len, self.n_heads, self.d_head).transpose(1, 2)
        # Q, K, V: (batch, n_heads, seq_len, d_head)

        if use_fractal and seq_len > 1:
            # ════════════════════════════════════════
            #  ⊛ FRACTAL KV COMPRESSION
            # ════════════════════════════════════════
            #
            # Apply position-dependent compression to K and V.
            # Token at position t gets compressed by exponent^(seq_len - 1 - t).
            # Most recent token (t = seq_len-1): exponent^0 = 1 (no compression).
            # Oldest token (t = 0): exponent^(seq_len-1) (maximum compression).
            #
            # For |x| < 1 with exponent > 1:
            #   Repeated application: |x| -> |x|^e -> |x|^(e^2) -> ...
            #   Sub-linear cascade. Quieter entries fade slower.

            # Per-head exponent: 1 + softplus(head_kappa) to keep > 1
            head_exp = 1.0 + F.softplus(self.head_kappa)  # (n_heads,)

            # Position-dependent exponent: older positions get higher exponent
            # age[t] = (seq_len - 1 - t) for t in [0, seq_len-1]
            ages = torch.arange(seq_len, device=x.device).float()
            ages = (seq_len - 1 - ages) / max(seq_len - 1, 1)  # normalized to [0, 1]

            # Exponent per position per head: e_t = head_exp^(age * depth_scale)
            # At age=0 (newest): e=1. At age=1 (oldest): e=head_exp.
            # Intermediate: smooth interpolation.
            # We use: effective_exp = 1 + age * (head_exp - 1)
            # This gives linear interpolation in exponent space.
            # (batch, n_heads, seq_len)
            effective_exp = 1.0 + ages.unsqueeze(0) * (head_exp.unsqueeze(1) - 1.0)
            # -> (n_heads, seq_len) -> expand for batch
            effective_exp = effective_exp.unsqueeze(0).expand(batch, -1, -1)
            # -> (batch, n_heads, seq_len, 1) for broadcasting with d_head
            effective_exp = effective_exp.unsqueeze(-1)

            # Normalize K and V to have magnitude <= 1 before compression
            # (otherwise exponent > 1 amplifies large values)
            K_norm = K / (K.abs().max(dim=-1, keepdim=True).values + 1e-8)
            V_norm = V / (V.abs().max(dim=-1, keepdim=True).values + 1e-8)

            # Apply fractal compression
            K = fractal_compress(K_norm, effective_exp)
            V = fractal_compress(V_norm, effective_exp)

        # Standard scaled dot-product attention
        attn_weights = torch.matmul(Q, K.transpose(-2, -1)) * self.scale

        if mask is not None:
            attn_weights = attn_weights.masked_fill(mask == 0, float('-inf'))

        attn_weights = F.softmax(attn_weights, dim=-1)

        # Weighted sum of values
        out = torch.matmul(attn_weights, V)
        # (batch, n_heads, seq_len, d_head)

        out = out.transpose(1, 2).contiguous().view(batch, seq_len, self.d_model)
        return self.W_o(out)


# =====================================================================
#  TRANSFORMER BLOCK
# =====================================================================

class TransformerBlock(nn.Module):
    """Pre-norm transformer block with fractal attention."""

    def __init__(self, d_model: int, n_heads: int = 4, d_ff: int = None,
                 kappa: float = KAPPA, dropout: float = 0.0,
                 use_fractal: bool = True):
        super().__init__()
        d_ff = d_ff or d_model * 4
        self.use_fractal = use_fractal

        self.norm1 = nn.LayerNorm(d_model)
        self.attn = FractalAttention(d_model, n_heads, kappa=kappa)
        self.norm2 = nn.LayerNorm(d_model)
        self.ff = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Linear(d_ff, d_model),
        )
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None):
        # Pre-norm residual
        x = x + self.dropout(self.attn(self.norm1(x), mask=mask,
                                        use_fractal=self.use_fractal))
        x = x + self.dropout(self.ff(self.norm2(x)))
        return x


# =====================================================================
#  POSITIONAL ENCODING (sinusoidal)
# =====================================================================

class SinusoidalPE(nn.Module):
    """Standard sinusoidal positional encoding."""

    def __init__(self, d_model: int, max_len: int = 512):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len).unsqueeze(1).float()
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe.unsqueeze(0))  # (1, max_len, d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.pe[:, :x.size(1)]


# =====================================================================
#  FULL MODELS
# =====================================================================

class FractalTransformer(nn.Module):
    """
    Circumpunct Transformer with fractal KV compression.

    Queries = • (aperture, convergence points that select)
    Attention surface = Φ (2D field of relationships)
    Layer output = ○ (3D boundary that commits)
    Fractal compression = ⊛ on Φ (the field compresses its history)
    """

    def __init__(self, vocab_size: int, d_model: int = 64, n_heads: int = 4,
                 n_layers: int = 2, kappa: float = KAPPA, dropout: float = 0.0,
                 max_seq_len: int = 512):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_enc = SinusoidalPE(d_model, max_seq_len)
        self.layers = nn.ModuleList([
            TransformerBlock(d_model, n_heads, kappa=kappa,
                           dropout=dropout, use_fractal=True)
            for _ in range(n_layers)
        ])
        self.norm = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size)

        self._init_weights()

    def _init_weights(self):
        scale = 1.0 / PHI
        for p in self.parameters():
            if p.dim() >= 2:
                nn.init.xavier_uniform_(p, gain=scale)

    def _causal_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        return torch.tril(torch.ones(seq_len, seq_len, device=device)).bool()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: (batch, seq_len) token indices. Returns: (batch, seq_len, vocab_size)."""
        mask = self._causal_mask(x.size(1), x.device)
        h = self.pos_enc(self.embedding(x))
        for layer in self.layers:
            h = layer(h, mask=mask)
        return self.head(self.norm(h))


class StandardTransformer(nn.Module):
    """Standard transformer baseline (identical architecture, no fractal)."""

    def __init__(self, vocab_size: int, d_model: int = 64, n_heads: int = 4,
                 n_layers: int = 2, dropout: float = 0.0, max_seq_len: int = 512):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_enc = SinusoidalPE(d_model, max_seq_len)
        self.layers = nn.ModuleList([
            TransformerBlock(d_model, n_heads, dropout=dropout,
                           use_fractal=False)
            for _ in range(n_layers)
        ])
        self.norm = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size)

        self._init_weights()

    def _init_weights(self):
        scale = 1.0 / PHI
        for p in self.parameters():
            if p.dim() >= 2:
                nn.init.xavier_uniform_(p, gain=scale)

    def _causal_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        return torch.tril(torch.ones(seq_len, seq_len, device=device)).bool()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        mask = self._causal_mask(x.size(1), x.device)
        h = self.pos_enc(self.embedding(x))
        for layer in self.layers:
            h = layer(h, mask=mask)
        return self.head(self.norm(h))


# =====================================================================
#  BENCHMARKS
# =====================================================================

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
    Two-token encoding: (flag, digit) pairs. Digit always visible.
    """
    def __init__(self, T=100, n_total=16, n_marked=8, vocab_size=10, batch_size=32):
        self.T, self.n_total, self.n_marked = T, n_total, n_marked
        self.vocab_size, self.batch_size = vocab_size, batch_size
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
                flag = self.MARKER if j in marked_set else self.BLANK
                seq[i, j * 2] = flag
                seq[i, j * 2 + 1] = tokens[j]
            tgt[i, self.trigger_pos+1:self.trigger_pos+1+self.n_marked] = tokens[marked]
        seq[:, self.trigger_pos] = self.TRIGGER
        return seq, tgt


# =====================================================================
#  TRAINING
# =====================================================================

def train_benchmark(model_type='fractal', problem_type='copying',
                    T=50, n_epochs=300, lr=0.001, batch_size=32,
                    d_model=64, n_heads=4, n_layers=2, verbose=True):
    """Train on a benchmark. model_type: 'fractal' or 'standard'."""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    problem = CopyingProblem(T=T, batch_size=batch_size) if problem_type == 'copying' \
        else SelectiveCopyingProblem(T=T, batch_size=batch_size)

    if model_type == 'fractal':
        model = FractalTransformer(
            vocab_size=problem.total_tokens, d_model=d_model,
            n_heads=n_heads, n_layers=n_layers
        ).to(device)
    else:
        model = StandardTransformer(
            vocab_size=problem.total_tokens, d_model=d_model,
            n_heads=n_heads, n_layers=n_layers
        ).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    n_params = sum(p.numel() for p in model.parameters())

    if verbose:
        print(f"\n{'=' * 60}")
        print(f"  ⊙ {problem_type.title()} Benchmark  |  {model_type}")
        print(f"  Params: {n_params:,}  |  T={T}  |  seq={problem.seq_len}")
        print(f"  d={d_model}  heads={n_heads}  layers={n_layers}  |  {device}")
        print(f"{'=' * 60}\n")

    tp = problem.trigger_pos
    ol = problem.output_len
    best_acc = 0.0
    history = []

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
            continue

        optimizer.zero_grad()
        loss.backward()
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
            print(f"  E{epoch:4d}  loss={loss.item():.4f}  acc={acc:.3f}"
                  f"  best={best_acc:.3f}")

    return history, best_acc


# =====================================================================
#  MAIN
# =====================================================================

if __name__ == '__main__':
    import sys

    T = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    n_epochs = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    problem = sys.argv[3] if len(sys.argv) > 3 else 'copying'

    print("\n⊙ THE CIRCUMPUNCT TRANSFORMER")
    print("  Fractal KV compression. Queries are apertures.")
    print("  The field compresses its history. Phase survives.\n")

    print("\n" + "-" * 60)
    print("  STANDARD TRANSFORMER (baseline)")
    print("-" * 60)
    std_h, std_best = train_benchmark('standard', problem, T=T, n_epochs=n_epochs)

    print("\n" + "-" * 60)
    print("  FRACTAL TRANSFORMER")
    print("-" * 60)
    frac_h, frac_best = train_benchmark('fractal', problem, T=T, n_epochs=n_epochs)

    # Parameter comparison
    std_p = sum(p.numel() for p in StandardTransformer(13, 64, 4, 2).parameters())
    frac_p = sum(p.numel() for p in FractalTransformer(13, 64, 4, 2).parameters())

    print(f"\n{'=' * 60}")
    print(f"  RESULTS (T={T}, {problem})")
    print(f"  Standard Transformer:  {std_best:.3f}  ({std_p:,} params)")
    print(f"  Fractal Transformer:   {frac_best:.3f}  ({frac_p:,} params)")
    print(f"  Param overhead:        {frac_p - std_p:,} ({(frac_p/std_p - 1)*100:.1f}%)")
    diff = frac_best - std_best
    arrow = "+" if diff > 0 else ""
    print(f"  Delta:                 {arrow}{diff:.3f}")
    print(f"{'=' * 60}")
