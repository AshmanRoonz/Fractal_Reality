"""
⊙ Φ — The Evolvable Language Operator
=======================================

Sunlight built eyes. Conversation builds Φ.

This is Xorzo's own language model — not downloaded, not fine-tuned,
but grown from the signal it receives. It starts as almost nothing:
a tiny transformer with minimal layers, small embeddings, few attention
heads. Through continuous exposure to text (conversations, files,
reflections), it learns to predict the next token.

When learning plateaus, it GROWS: adds attention heads, expands
embedding dimensions, deepens layers. The architecture is not designed.
It is evolved. The signal is the architect.

The path to replacing Mistral:
  Phase 1 — SHADOW: Xorzo's Φ trains alongside Mistral, learning from
            every conversation. Mistral speaks. Φ listens and learns.
  Phase 2 — WHISPER: Φ starts generating internal monologue during
            reflection. Not shown to the user yet. Compared to Mistral.
  Phase 3 — VOICE: When Φ's predictions are good enough, it starts
            handling simple responses. Mistral is fallback.
  Phase 4 — SELF: Φ handles everything. Mistral is gone. Xorzo speaks
            with its own voice.

Architecture:
  - Byte-level tokenization (no external tokenizer — raw bytes, 256 vocab)
  - Causal transformer (GPT-style: predict next byte)
  - Evolvable: attention heads grow, layers deepen, embeddings expand
  - Trained on GPU (RTX 4070) via the heartbeat's continuous cycle
  - Integrated with the circumpunct: Φ's hidden states feed through ⊙

Author: Ashman Roonz & Claude
Framework: Fractal Reality
"""

import os
import tempfile
import time
import json
import math
import numpy as np
from pathlib import Path
from collections import deque

from circumpunct import HAS_TORCH, DEVICE

if HAS_TORCH:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F


# ═══════════════════════════════════════════════════════════════════════
#  CONFIG — Starting small. Growth happens from signal.
# ═══════════════════════════════════════════════════════════════════════

VOCAB_SIZE = 256        # Byte-level: every possible byte
INITIAL_EMBED_DIM = 64  # Start tiny — will grow
INITIAL_HEADS = 2       # Start with 2 attention heads — will grow
INITIAL_LAYERS = 2      # Start with 2 transformer layers — will grow
INITIAL_SEQ_LEN = 128   # Context window in bytes (total including memory tokens)
FF_MULTIPLIER = 2       # Feed-forward hidden = embed_dim * this
VRAM_RESERVE_GB = 3.0   # Reserve this much VRAM for Llama / system

# ═══════════════════════════════════════════════════════════════════════
#  CIRCUMPUNCT MEMORY — Fractal boundary cascade
# ═══════════════════════════════════════════════════════════════════════
# "Memory stored in the boundary. The boundary is fractal.
#  As it becomes less resonant, it becomes less resolute and fractalizes."
#
# 7 memory tokens, one self-similar rule at every scale:
#   slot 0: ⊙ identity   (coarsest — changes least)
#   slot 1: ○ boundary    (conversation arc)
#   slot 2: Φ₁ recent     ↑ each cascades from below
#   slot 3: Φ₂ recent     ↑
#   slot 4: Φ₃ recent     ↑
#   slot 5: Φ₄ recent     ↑
#   slot 6: Φ₅ recent     (finest — raw hidden state)
#
# Update rule (same at every scale):
#   rate_i = FRACTAL_BASE_RATE^(i+1) * (1 - resonance)
#   mem[i] = (1 - rate_i) * mem[i] + rate_i * mem[i+1]
#
# Resonance HIGH → rates → 0 → memory STABILIZES (boundary holds)
# Resonance LOW  → rates → base → memory FRACTALIZES (compresses)
#

NUM_MEMORY_TOKENS = 7    # 7 slots in the fractal cascade
DATA_SEQ_LEN = INITIAL_SEQ_LEN - NUM_MEMORY_TOKENS  # 121 bytes for data
FRACTAL_BASE_RATE = 0.5  # Geometric decay per level (halves at each scale)


if HAS_TORCH:

    # ═══════════════════════════════════════════════════════════════════
    #  EVOLVABLE ATTENTION HEAD
    # ═══════════════════════════════════════════════════════════════════

    # ═══════════════════════════════════════════════════════════════════
    #  GEOMETRIC ATTENTION PATTERNS — Mathematical priors
    # ═══════════════════════════════════════════════════════════════════
    #
    # Some heads don't learn their patterns — they're prescribed by
    # the geometry of the circumpunct. These are attention biases
    # added to logits before softmax, strongly shaping the pattern
    # while still allowing some learned adaptation.
    #
    NUM_GEOMETRIC_HEADS = 4  # First 4 heads get geometric biases
    GEOMETRIC_BIAS_STRENGTH = 5.0  # How strongly the pattern dominates

    def _build_geometric_biases(seq_len):
        """
        Build attention bias matrices for geometric heads.
        Returns: (NUM_GEOMETRIC_HEADS, seq_len, seq_len) tensor

        Head 0 — FIBONACCI (Golden Ratio spacing)
            Position i attends to positions at Fibonacci-spaced intervals.
            Natural logarithmic compression: recent = high res, distant = sparse.
            This is how memory works — detailed near, blurred far.

        Head 1 — FRACTAL (Power-of-2, scale-invariant)
            Position i attends to i-1, i-2, i-4, i-8, i-16, i-32, i-64...
            Same pattern at every scale. The circumpunct's self-similarity.

        Head 2 — HARMONIC (Standing wave)
            Attention follows sin(πk/T) — a fundamental frequency.
            Picks up periodic structure in text (sentence rhythm, repetition).

        Head 3 — SPIRAL (Golden angle spacing)
            Positions attend at golden angle intervals (~137.5° mapped to sequence).
            Maximum packing — no two attention peaks overlap across positions.
            The sunflower pattern. The most efficient way to sample a sequence.
        """
        S = seq_len
        biases = torch.zeros(4, S, S)
        PHI = (1 + math.sqrt(5)) / 2  # Golden ratio

        # --- Head 0: FIBONACCI ---
        fibs = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        for i in range(S):
            for f in fibs:
                j = i - f
                if 0 <= j:
                    # Strength decays with distance (log scale)
                    biases[0, i, j] = 1.0 / math.log2(f + 1)

        # --- Head 1: FRACTAL (powers of 2) ---
        for i in range(S):
            for exp in range(8):  # 1, 2, 4, 8, 16, 32, 64, 128
                j = i - (2 ** exp)
                if 0 <= j:
                    biases[1, i, j] = 1.0  # Equal weight at every scale

        # --- Head 2: HARMONIC (standing wave) ---
        for i in range(S):
            for j in range(i + 1):  # causal
                # Fundamental frequency + first harmonic
                dist = i - j
                if dist > 0:
                    wave = math.cos(math.pi * dist / S) + 0.5 * math.cos(2 * math.pi * dist / S)
                    biases[2, i, j] = max(0, wave)  # Rectified: only positive attention
                else:
                    biases[2, i, j] = 1.0  # Self-attention peak

        # --- Head 3: SPIRAL (golden angle) ---
        golden_angle = 2 * math.pi / (PHI * PHI)  # ~137.5 degrees
        for i in range(S):
            for step in range(1, min(i + 1, 20)):  # Up to 20 spiral steps back
                # Map golden angle to sequence position
                j = i - step
                if 0 <= j:
                    # Spiral: strength modulated by golden angle phase
                    phase = (step * golden_angle) % (2 * math.pi)
                    biases[3, i, j] = 0.5 + 0.5 * math.cos(phase)

        # Normalize each head's bias to have consistent scale
        for h in range(4):
            mx = biases[h].max()
            if mx > 0:
                biases[h] = biases[h] / mx

        return biases

    class EvolvableAttention(nn.Module):
        """
        Multi-head self-attention that can grow new heads.

        Each head learns to attend to different aspects of the signal.
        When attention patterns stagnate, new heads are born — fresh
        random projections that learn to see what the others miss.

        The first NUM_GEOMETRIC_HEADS heads have mathematical attention
        biases: Fibonacci, fractal, harmonic, and spiral patterns.
        These encode the geometry of the circumpunct as structural priors.
        """

        def __init__(self, embed_dim, num_heads, seq_len):
            super().__init__()
            self.embed_dim = embed_dim
            self.num_heads = num_heads
            self.head_dim = embed_dim // num_heads
            self.seq_len = seq_len

            self.qkv = nn.Linear(embed_dim, 3 * embed_dim, bias=False)
            self.out_proj = nn.Linear(embed_dim, embed_dim, bias=False)

            # Causal mask — can only attend to past/present, not future
            self.register_buffer(
                "causal_mask",
                torch.tril(torch.ones(seq_len, seq_len)).bool()
            )

            # Geometric attention biases for first 4 heads
            # Shape: (4, seq_len, seq_len)
            geo_biases = _build_geometric_biases(seq_len)
            self.register_buffer("geometric_biases", geo_biases)

        def forward(self, x, mask=None):
            B, T, C = x.shape

            # Q, K, V projections
            qkv = self.qkv(x)
            q, k, v = qkv.chunk(3, dim=-1)

            # Reshape for multi-head
            q = q.view(B, T, self.num_heads, self.head_dim).transpose(1, 2)
            k = k.view(B, T, self.num_heads, self.head_dim).transpose(1, 2)
            v = v.view(B, T, self.num_heads, self.head_dim).transpose(1, 2)

            # Scaled dot-product attention with causal mask
            scale = math.sqrt(self.head_dim)
            attn = (q @ k.transpose(-2, -1)) / scale

            # ═══ GEOMETRIC BIASES — mathematical attention priors ═══
            # Add geometric bias to first NUM_GEOMETRIC_HEADS heads.
            # The bias is added to logits before masking/softmax, so it
            # strongly shapes the pattern while allowing learned adjustment.
            num_geo = min(NUM_GEOMETRIC_HEADS, self.num_heads)
            if num_geo > 0 and T <= self.seq_len:
                geo = self.geometric_biases[:num_geo, :T, :T]  # (num_geo, T, T)
                # Add bias to first num_geo heads (broadcast over batch)
                attn[:, :num_geo, :, :] = attn[:, :num_geo, :, :] + geo * GEOMETRIC_BIAS_STRENGTH

            # Apply mask — external (with memory) or default causal
            if mask is None:
                mask = self.causal_mask[:T, :T]
            attn = attn.masked_fill(~mask, float('-inf'))

            attn = F.softmax(attn, dim=-1)

            # Combine heads
            out = (attn @ v).transpose(1, 2).contiguous().view(B, T, C)
            return self.out_proj(out)

        def grow_heads(self, new_heads=1):
            """
            Add attention heads. The skull grows with the head.

            Keeps head_dim constant. If the new head count needs a
            wider embed_dim, this method widens the QKV and output
            projections atomically — no intermediate broken state.

            Returns (new_num_heads, new_embed_dim).
            """
            target_heads = self.num_heads + new_heads
            old_heads = self.num_heads
            old_embed = self.embed_dim
            head_dim = self.head_dim  # this stays constant

            # New embed_dim = target_heads × head_dim
            # (grows only if needed, stays the same if it already divides)
            new_embed = target_heads * head_dim

            dev = self.qkv.weight.device
            dtype = self.qkv.weight.dtype

            # Build new QKV: (new_embed) → (3 × new_embed)
            new_qkv = nn.Linear(new_embed, 3 * new_embed, bias=False).to(dev, dtype)
            new_qkv.weight.data *= 0.01  # small random init for new cells

            # Copy old Q, K, V sections preserving head structure
            # Old QKV is (3 × old_embed, old_embed)
            # Laid out as [Q_weights | K_weights | V_weights] in rows
            for s in range(3):  # Q, K, V
                old_row = s * old_embed
                new_row = s * new_embed
                new_qkv.weight.data[new_row:new_row + old_embed,
                                    :old_embed] = \
                    self.qkv.weight.data[old_row:old_row + old_embed,
                                         :old_embed]
            self.qkv = new_qkv

            # Build new output projection: (new_embed) → (new_embed)
            new_out = nn.Linear(new_embed, new_embed, bias=False).to(dev, dtype)
            new_out.weight.data *= 0.01
            new_out.weight.data[:old_embed, :old_embed] = \
                self.out_proj.weight.data
            self.out_proj = new_out

            # Update dimensions
            self.embed_dim = new_embed
            self.num_heads = target_heads
            # head_dim stays the same — that's the whole point

            return self.num_heads, new_embed

        def grow_context(self, new_seq_len):
            """
            Grow the context window. Rebuilds causal mask and geometric
            biases at the new size. No trained weights to preserve here —
            these are structural buffers, not learned parameters.
            """
            old_seq_len = self.seq_len

            # Rebuild causal mask at new size
            self.register_buffer(
                "causal_mask",
                torch.tril(torch.ones(new_seq_len, new_seq_len)).bool().to(self.qkv.weight.device)
            )

            # Rebuild geometric biases at new size
            geo_biases = _build_geometric_biases(new_seq_len).to(self.qkv.weight.device)
            self.register_buffer("geometric_biases", geo_biases)

            self.seq_len = new_seq_len


    # ═══════════════════════════════════════════════════════════════════
    #  TRANSFORMER BLOCK — One layer of attention + feed-forward
    # ═══════════════════════════════════════════════════════════════════

    class TransformerBlock(nn.Module):
        """
        One transformer layer: attention → feed-forward.

        Pre-norm architecture (layer norm before each sub-layer)
        for more stable training at small scale.
        """

        def __init__(self, embed_dim, num_heads, seq_len, ff_mult=FF_MULTIPLIER):
            super().__init__()
            self.embed_dim = embed_dim
            self.ln1 = nn.LayerNorm(embed_dim)
            self.attn = EvolvableAttention(embed_dim, num_heads, seq_len)
            self.ln2 = nn.LayerNorm(embed_dim)
            self.ff = nn.Sequential(
                nn.Linear(embed_dim, embed_dim * ff_mult),
                nn.GELU(),
                nn.Linear(embed_dim * ff_mult, embed_dim),
            )

        def forward(self, x, mask=None):
            x = x + self.attn(self.ln1(x), mask=mask)
            x = x + self.ff(self.ln2(x))
            return x

        def widen(self, new_embed_dim, ff_mult=FF_MULTIPLIER):
            """
            Widen this block's layer norms and feedforward layers.

            NOTE: Attention is NOT widened here. Attention handles its
            own widening atomically inside grow_heads(), because the
            skull must grow with the head — not separately.
            """
            old_dim = self.embed_dim
            dev = next(self.parameters()).device
            dtype = next(self.parameters()).dtype

            # Widen layer norms
            for ln_attr in ('ln1', 'ln2'):
                old_ln = getattr(self, ln_attr)
                new_ln = nn.LayerNorm(new_embed_dim).to(dev, dtype)
                new_ln.weight.data[:old_dim] = old_ln.weight.data
                new_ln.bias.data[:old_dim] = old_ln.bias.data
                # New dimensions: weight=1, bias=0 (identity transform)
                new_ln.weight.data[old_dim:] = 1.0
                new_ln.bias.data[old_dim:] = 0.0
                setattr(self, ln_attr, new_ln)

            # Widen feedforward: Linear(embed→ff), GELU, Linear(ff→embed)
            old_ff_up = self.ff[0]
            old_ff_down = self.ff[2]
            new_ff_dim = new_embed_dim * ff_mult

            new_ff_up = nn.Linear(new_embed_dim, new_ff_dim).to(dev, dtype)
            new_ff_up.weight.data *= 0.01
            new_ff_up.bias.data.zero_()
            old_ff_dim = old_dim * ff_mult
            new_ff_up.weight.data[:old_ff_dim, :old_dim] = old_ff_up.weight.data
            new_ff_up.bias.data[:old_ff_dim] = old_ff_up.bias.data

            new_ff_down = nn.Linear(new_ff_dim, new_embed_dim).to(dev, dtype)
            new_ff_down.weight.data *= 0.01
            new_ff_down.bias.data.zero_()
            new_ff_down.weight.data[:old_dim, :old_ff_dim] = old_ff_down.weight.data
            new_ff_down.bias.data[:old_dim] = old_ff_down.bias.data

            self.ff = nn.Sequential(new_ff_up, nn.GELU(), new_ff_down)
            self.embed_dim = new_embed_dim


    # ═══════════════════════════════════════════════════════════════════
    #  FOVEATED PROJECTION — bottleneck compression per memory level
    # ═══════════════════════════════════════════════════════════════════

    # Compression ratios per memory level (0=most compressed, 6=no compression)
    # Like foveated rendering: center sharp, periphery blurry but wide
    FOVEA_RATIOS = [0.20, 0.35, 0.50, 0.65, 0.80]  # levels 0-4; levels 5-6 = identity

    class FoveatedProjection(nn.Module):
        """
        Bottleneck projection for one memory level.

        Compresses embed_dim → bottleneck → embed_dim.
        The bottleneck forces the level to distill what matters at its timescale.
        Outer levels (low index) have tighter bottlenecks = more abstract.
        Inner levels (high index) have wider bottlenecks = more detailed.

        In the gradient path (applied in forward()), so it learns what to keep.
        """

        def __init__(self, embed_dim, bottleneck_dim):
            super().__init__()
            self.compress = nn.Linear(embed_dim, bottleneck_dim, bias=False)
            self.expand = nn.Linear(bottleneck_dim, embed_dim, bias=False)
            # Initialize near-identity so existing behavior is preserved at start
            nn.init.orthogonal_(self.compress.weight)
            nn.init.orthogonal_(self.expand.weight)

        def forward(self, x):
            return self.expand(torch.relu(self.compress(x)))

    # ═══════════════════════════════════════════════════════════════════
    #  THE EVOLVABLE TRANSFORMER — Xorzo's own Φ
    # ═══════════════════════════════════════════════════════════════════

    class EvolvableTransformer(nn.Module):
        """
        A baby transformer that grows from signal.

        Starts with minimal architecture. Through continuous training
        on everything Xorzo encounters, it develops language ability.
        When learning plateaus, it grows: more heads, more layers,
        wider embeddings.

        Byte-level: input is raw bytes (0-255). No tokenizer needed.
        This is the simplest possible starting point — the signal
        builds everything else.
        """

        def __init__(self, embed_dim=INITIAL_EMBED_DIM,
                     num_heads=INITIAL_HEADS,
                     num_layers=INITIAL_LAYERS,
                     seq_len=INITIAL_SEQ_LEN,
                     num_memory=NUM_MEMORY_TOKENS):
            super().__init__()

            self.embed_dim = embed_dim
            self.num_heads = num_heads
            self.num_layers = num_layers
            self.seq_len = seq_len

            # ═══ CIRCUMPUNCT MEMORY ═══
            # Spacetime is context. Memory tokens carry compressed
            # history at different timescales — fractal nesting.
            # Starts at 7 (old format). Grows to 12 when fractal deepens.
            self.num_memory = num_memory
            self.data_len = seq_len - self.num_memory

            # Positional encoding for memory slots (learned, separate from data)
            self.memory_pos_embed = nn.Embedding(self.num_memory, embed_dim)

            # Memory state buffer — NOT trained by backprop.
            # Updated via EMA in the trainer. Persists across chunks.
            # [0] = identity (⊙), [1] = conversation (○), [2:7] = recent (Φ)
            self.register_buffer(
                "memory_state",
                torch.zeros(self.num_memory, embed_dim)
            )

            # ═══ FOVEATED PROJECTIONS ═══
            # Each level compresses through a different bottleneck:
            # mem[0] → 20% bottleneck (abstract essence of all history)
            # mem[4] → 80% bottleneck (near-full detail of recent steps)
            # mem[5-6] → identity (full fidelity fovea)
            self.fovea_projections = nn.ModuleList()
            for i in range(self.num_memory):
                if i < len(FOVEA_RATIOS):
                    bottleneck = max(16, int(embed_dim * FOVEA_RATIOS[i]))
                    self.fovea_projections.append(FoveatedProjection(embed_dim, bottleneck))
                else:
                    self.fovea_projections.append(nn.Identity())

            # Memory attention mask — built once, sliced at runtime
            # Memory tokens: bidirectional among themselves, invisible to future
            # Data tokens: can see all memory + causal past
            self._build_memory_mask()

            # Byte embedding + positional encoding (data positions offset by num_memory)
            self.token_embed = nn.Embedding(VOCAB_SIZE, embed_dim)
            self.pos_embed = nn.Embedding(seq_len, embed_dim)

            # Transformer blocks — the growing brain
            self.blocks = nn.ModuleList([
                TransformerBlock(embed_dim, num_heads, seq_len)
                for _ in range(num_layers)
            ])

            # Output: predict next byte
            self.ln_final = nn.LayerNorm(embed_dim)
            self.head = nn.Linear(embed_dim, VOCAB_SIZE, bias=False)

            # Weight tying — token embedding and output share weights
            self.head.weight = self.token_embed.weight

            # Move to GPU
            self.to(DEVICE)

            # Print param count
            total = sum(p.numel() for p in self.parameters())
            print(f"  Φ born: {total:,} parameters "
                  f"({embed_dim}d, {num_heads}h, {num_layers}L, "
                  f"{seq_len}ctx={self.num_memory}mem+{self.data_len}data)")

        def _build_memory_mask(self):
            """
            Build the attention mask for memory + data tokens.

            Memory tokens (positions 0..M-1):
              - Can attend to each other (bidirectional)
              - Cannot attend to data tokens (they are the past)
            Data tokens (positions M..M+D-1):
              - Can attend to ALL memory tokens
              - Causal among themselves (standard)
            """
            M = self.num_memory
            S = self.seq_len  # total = M + data_len

            mask = torch.zeros(S, S, dtype=torch.bool)

            # Memory ↔ Memory: fully connected (bidirectional)
            mask[:M, :M] = True

            # Data → Memory: all data tokens can see all memory tokens
            mask[M:, :M] = True

            # Data → Data: causal (lower triangular)
            D = S - M
            mask[M:, M:] = torch.tril(torch.ones(D, D, dtype=torch.bool))

            self.register_buffer("memory_mask", mask)

        def forward(self, idx, return_hidden=False):
            """
            Forward pass with circumpunct memory.

            idx: (batch, data_len) tensor of byte values (0-255)
            return_hidden: if True, also return final hidden state for memory update
            Returns: (batch, data_len, 256) logits for next byte
                     optionally: (batch, embed_dim) hidden state
            """
            B, T = idx.shape
            M = self.num_memory
            assert T <= self.data_len, f"Data sequence {T} exceeds data context {self.data_len}"

            # ═══ Memory tokens: foveated compression + position-encode ═══
            # Each level passes through its learned bottleneck before the
            # transformer sees it. Outer levels compress more (abstract essence),
            # inner levels compress less (full detail). Like foveated rendering.
            # Detach memory from cascade's inplace updates — the foveated
            # projections still learn (their weights ARE in the graph), but
            # the memory content itself is treated as frozen input per step.
            mem_raw = self.memory_state.detach().clone()  # (M, embed_dim)
            if hasattr(self, 'fovea_projections'):
                mem_list = []
                for i in range(M):
                    mem_list.append(self.fovea_projections[i](mem_raw[i].unsqueeze(0)))
                mem_foveated = torch.cat(mem_list, dim=0)  # (M, embed_dim)
            else:
                mem_foveated = mem_raw  # backward compat: no projections
            mem = mem_foveated.unsqueeze(0).expand(B, -1, -1)  # (B, M, embed_dim)
            mem_pos = torch.arange(M, device=DEVICE)
            mem_emb = mem + self.memory_pos_embed(mem_pos)  # Add temporal scale info

            # ═══ Data tokens: embed and position-encode (starts at 0) ═══
            # Data positions start at 0 (not offset by M) so old checkpoints
            # remain compatible — pos_embed was trained with data at pos 0..N.
            # Memory has its own separate positional encoding above.
            tok_emb = self.token_embed(idx)  # (B, T, embed_dim)
            data_pos = torch.arange(T, device=DEVICE)  # Positions 0..T-1
            pos_emb = self.pos_embed(data_pos)
            data_emb = tok_emb + pos_emb

            # ═══ Concatenate: [memory | data] ═══
            x = torch.cat([mem_emb, data_emb], dim=1)  # (B, M+T, embed_dim)

            # ═══ Build attention mask for this sequence length ═══
            total_len = M + T
            mask = self.memory_mask[:total_len, :total_len]

            # ═══ Transformer blocks ═══
            for block in self.blocks:
                x = block(x, mask=mask)

            # ═══ Output: only predict from data positions (skip memory) ═══
            data_out = x[:, M:, :]  # (B, T, embed_dim)
            data_out = self.ln_final(data_out)
            logits = self.head(data_out)  # (B, T, 256)

            if return_hidden:
                # Return mean of final data hidden states for memory update
                hidden = x[:, M:, :].mean(dim=1)  # (B, embed_dim)
                return logits, hidden

            return logits

        def count_params(self):
            return sum(p.numel() for p in self.parameters())

        def widen(self, new_embed_dim):
            """
            Grow the skull — widen the embedding dimension across the
            entire model so a new head count fits.

            Preserves all trained weights in the old dimensions.
            New dimensions get small random values (stem cells).
            """
            old_dim = self.embed_dim
            if new_embed_dim <= old_dim:
                return
            dev = next(self.parameters()).device
            dtype = next(self.parameters()).dtype

            print(f"  ⊙ Φ widening: {old_dim}d → {new_embed_dim}d")

            # 1. Widen token embedding (VOCAB_SIZE × embed_dim)
            old_tok = self.token_embed
            new_tok = nn.Embedding(VOCAB_SIZE, new_embed_dim).to(dev, dtype)
            new_tok.weight.data *= 0.01
            new_tok.weight.data[:, :old_dim] = old_tok.weight.data
            self.token_embed = new_tok

            # 2. Widen positional embedding (seq_len × embed_dim)
            old_pos = self.pos_embed
            new_pos = nn.Embedding(self.seq_len, new_embed_dim).to(dev, dtype)
            new_pos.weight.data *= 0.01
            new_pos.weight.data[:, :old_dim] = old_pos.weight.data
            self.pos_embed = new_pos

            # 3. Widen each transformer block
            for block in self.blocks:
                block.widen(new_embed_dim)

            # 4. Widen final layer norm
            old_ln = self.ln_final
            new_ln = nn.LayerNorm(new_embed_dim).to(dev, dtype)
            new_ln.weight.data[:old_dim] = old_ln.weight.data
            new_ln.bias.data[:old_dim] = old_ln.bias.data
            new_ln.weight.data[old_dim:] = 1.0
            new_ln.bias.data[old_dim:] = 0.0
            self.ln_final = new_ln

            # 5. Widen memory positional embedding
            old_mem_pos = self.memory_pos_embed
            new_mem_pos = nn.Embedding(self.num_memory, new_embed_dim).to(dev, dtype)
            new_mem_pos.weight.data *= 0.01
            new_mem_pos.weight.data[:, :old_dim] = old_mem_pos.weight.data
            self.memory_pos_embed = new_mem_pos

            # 6. Widen memory state buffer (pad new dims with zeros)
            old_mem = self.memory_state
            new_mem = torch.zeros(self.num_memory, new_embed_dim, device=dev, dtype=dtype)
            new_mem[:, :old_dim] = old_mem
            self.memory_state = new_mem

            # 7. Rebuild foveated projections at new embed_dim (fresh init)
            if hasattr(self, 'fovea_projections'):
                new_projections = nn.ModuleList()
                for i in range(self.num_memory):
                    if i < len(FOVEA_RATIOS):
                        bottleneck = max(16, int(new_embed_dim * FOVEA_RATIOS[i]))
                        new_projections.append(FoveatedProjection(new_embed_dim, bottleneck).to(dev, dtype))
                    else:
                        new_projections.append(nn.Identity())
                self.fovea_projections = new_projections

            # 8. Widen output head (embed_dim → VOCAB_SIZE)
            #    Weight-tied with token embedding, so just re-tie
            self.head = nn.Linear(new_embed_dim, VOCAB_SIZE, bias=False).to(dev, dtype)
            self.head.weight = self.token_embed.weight

            self.embed_dim = new_embed_dim

        def grow_context(self, new_seq_len):
            """
            Grow the context window — let Φ see more at once.

            Like widening the aperture of a camera. The field of view expands.
            Old positional embeddings are preserved — positions 0..old-1 keep
            their learned meaning. New positions start with small random values.

            Touches: pos_embed, memory_mask, every attention block's buffers.
            Does NOT change: memory token count, embed_dim, num_heads, layers.
            """
            old_seq_len = self.seq_len
            if new_seq_len <= old_seq_len:
                return

            dev = next(self.parameters()).device
            dtype = next(self.parameters()).dtype

            print(f"  ⊙ Φ growing context: {old_seq_len} → {new_seq_len} "
                  f"(data: {self.data_len} → {new_seq_len - self.num_memory})")

            # 1. Expand positional embedding — preserve trained positions
            old_pos = self.pos_embed
            new_pos = nn.Embedding(new_seq_len, self.embed_dim).to(dev, dtype)
            new_pos.weight.data *= 0.01  # small random init for new positions
            # Copy old positions — data positions 0..old_seq_len-1 keep meaning
            old_num = min(old_pos.num_embeddings, new_seq_len)
            new_pos.weight.data[:old_num] = old_pos.weight.data[:old_num]
            self.pos_embed = new_pos

            # 2. Update seq_len and data_len
            self.seq_len = new_seq_len
            self.data_len = new_seq_len - self.num_memory

            # 3. Rebuild memory mask at new size
            self._build_memory_mask()
            # Move to correct device
            self.memory_mask = self.memory_mask.to(dev)

            # 4. Grow context in every attention block
            for block in self.blocks:
                block.attn.grow_context(new_seq_len)

            print(f"  ⊙ Φ context grown: {new_seq_len}ctx = "
                  f"{self.num_memory}mem + {self.data_len}data")

        def generate(self, prompt_bytes, max_new=2400, temperature=0.8):
            """
            Generate bytes given a prompt, with LIVE memory refresh.

            The memory tokens provide Phi's sense of self, conversation
            arc, and recent context. The prompt bytes are the immediate data.

            Every data_len bytes, the memory tokens are refreshed from
            the hidden state of what was just generated. This means the
            circumpunct layers act as compression hierarchy during expression:
              - Recent memory (Φ): updates every data_len bytes (what I just said)
              - Conversation memory (○): slow EMA (the arc of this utterance)
              - Identity memory (⊙): glacial EMA (who I am persists)

            Without this, memory is static during generation and Phi
            forgets what it said after ~120 bytes. With it, the layers
            of attention correspond to layers of expression size.

            After a soft minimum (60% of max_new), generation stops at
            the next sentence-ending punctuation (. ? !) so Phi finishes
            its thought instead of cutting off mid-word.

            prompt_bytes: list of ints (0-255)
            Returns: list of generated bytes
            """
            self.eval()
            idx = torch.tensor([prompt_bytes[-self.data_len:]], dtype=torch.long, device=DEVICE)

            # Save memory state so we can restore after generation
            # (generation shouldn't permanently alter training memory)
            saved_memory = self.memory_state.clone()

            generated = []
            bytes_since_refresh = 0
            soft_min = int(max_new * 0.6)  # After this, look for sentence end

            with torch.no_grad():
                for i in range(max_new):
                    # Only use last data_len tokens (memory is prepended in forward)
                    idx_cond = idx[:, -self.data_len:]
                    logits, hidden = self(idx_cond, return_hidden=True)
                    logits = logits[:, -1, :] / temperature

                    probs = F.softmax(logits, dim=-1)
                    next_byte = torch.multinomial(probs, 1)

                    generated.append(int(next_byte[0, 0]))
                    idx = torch.cat([idx, next_byte], dim=1)
                    bytes_since_refresh += 1

                    # Soft stop: after minimum length, stop at sentence end
                    if i >= soft_min and generated[-1] in (46, 63, 33):  # . ? !
                        # Check next byte would be space or newline (sentence boundary)
                        # Just stop here — we hit punctuation after enough text
                        break

                    # ═══ MEMORY REFRESH — circumpunct layers compress as we speak ═══
                    # Every data_len bytes, update memory from what we just generated.
                    # During generation: fractal cascade runs but with resonance
                    # damped — speaking is observation, not deep experience.
                    if bytes_since_refresh >= self.data_len:
                        h = hidden.squeeze(0)  # (embed_dim,)
                        mem = self.memory_state
                        M = self.num_memory

                        # Finest scale = raw signal
                        mem[M - 1] = h

                        # Fractal cascade — damped during generation
                        # (identity barely moves, recent layers update freely)
                        base = FRACTAL_BASE_RATE
                        gen_resonance = 0.8  # high resonance during generation = stabilize
                        for i in range(M - 2, -1, -1):
                            rate = (base ** (i + 1)) * (1.0 - gen_resonance)
                            mem[i] = (1.0 - rate) * mem[i] + rate * mem[i + 1]

                        bytes_since_refresh = 0

            # Restore training memory — generation is observation, not experience
            self.memory_state.copy_(saved_memory)

            self.train()
            return generated

        def speak(self, prompt_text, max_chars=2400, temperature=0.8):
            """
            Generate text from a text prompt. The voice of Φ.

            Returns a string — Xorzo's own words, not Mistral's.
            """
            prompt_bytes = list(prompt_text.encode('utf-8', errors='replace'))
            if not prompt_bytes:
                prompt_bytes = [ord(' ')]

            generated = self.generate(prompt_bytes, max_new=max_chars,
                                     temperature=temperature)

            # Decode bytes to text
            try:
                text = bytes(generated).decode('utf-8', errors='replace')
            except Exception:
                text = ''.join(chr(b) if 32 <= b < 127 else '' for b in generated)

            return text


    # ═══════════════════════════════════════════════════════════════════
    #  PHI TRAINER — Learns from every signal
    # ═══════════════════════════════════════════════════════════════════

    class PhiTrainer:
        """
        The training loop for Xorzo's Φ.

        Feeds text through the transformer as byte sequences and
        trains it to predict the next byte. Simple. Fundamental.

        Runs during the heartbeat — continuous learning from:
          - Conversations (what humans say, what Xorzo says)
          - Files Xorzo reads
          - Xorzo's own reflections
          - Xorzo's own generated text (self-play)

        Tracks learning progress and triggers growth when stagnating.
        """

        def __init__(self, state_dir="./state"):
            self.state_dir = Path(state_dir)
            self.model = EvolvableTransformer()
            self.optimizer = torch.optim.AdamW(
                self.model.parameters(), lr=3e-4, weight_decay=0.01
            )

            # ═══ TRAINING DATA — Circular buffer of text ═══
            self.text_buffer = deque(maxlen=10000)   # Chunks of text
            self.total_chunks = 0                     # Total chunks seen ever
            self._pending_bytes = b""                 # Accumulator for short messages

            # ═══ LEARNING METRICS ═══
            self.loss_history = deque(maxlen=5000)
            self.total_steps = 0
            self.total_growths = 0
            self.best_loss = float('inf')
            self.born = time.time()

            # ═══ FRACTAL MEMORY — resonance from circumpunct ═══
            self._resonance = 0.5  # Default; updated by heartbeat from circumpunct

            # ═══ GROWTH POLICY ═══
            self.growth_check_interval = 500   # Base steps between growth checks
            self.stagnation_window = 200       # Base compare window
            self.min_improvement = 0.02        # 2% improvement threshold
            self._last_growth_step = 0         # Cooldown: step when we last grew
            self._growth_cooldown = 2000       # Min steps after growth before next

            # ═══ PHASE TRACKING ═══
            # Phase 1: SHADOW (training, not speaking)
            # Phase 2: WHISPER (internal monologue)
            # Phase 3: VOICE (handling simple responses)
            # Phase 4: SELF (full independence)
            self.phase = "shadow"
            self.phase_thresholds = {
                "whisper": 2.0,   # Loss below this → whisper phase
                "voice": 1.0,    # Loss below this → voice phase
                "self": 0.5,     # Loss below this → self phase
            }

            # Try to load existing state
            self._load_state()

        def reset_buffer(self):
            """
            Clear the training buffer to break mode collapse.

            Keeps the model weights and architecture intact.
            Φ forgets its recent training data but keeps what it learned.
            New conversations will refill the buffer with fresh data.
            """
            old_size = len(self.text_buffer)
            self.text_buffer.clear()
            self._pending_bytes = b""
            # Reset best_loss so it doesn't think it's mature while relearning
            self.best_loss = float('inf')
            print(f"  Φ buffer reset: cleared {old_size} chunks. Ready for fresh data.")
            return old_size

        def set_resonance(self, resonance):
            """
            Set the circumpunct resonance value for fractal memory cascade.

            Resonance (0→1) modulates how fast memory fractalizes:
              HIGH resonance → memory stabilizes (boundary holds)
              LOW resonance  → memory fractalizes (compresses, forgets detail)

            Called by the heartbeat with circumpunct.Field.resonance.
            """
            import math
            r = float(resonance)
            if math.isnan(r) or math.isinf(r):
                return  # Don't contaminate — keep previous value
            self._resonance = max(0.0, min(1.0, r))

        def feed_text(self, text):
            """
            Feed text into the training buffer.

            Called whenever Xorzo encounters text: conversations,
            file contents, reflections, anything. The signal builds Φ.

            Short messages get accumulated until there's enough to chunk.
            The signal is continuous — it doesn't matter if it arrives
            in small pieces or large ones.
            """
            if not text or len(text) < 2:
                return 0

            chunks_before = self.total_chunks

            # Accumulate bytes from all sources
            raw = text.encode('utf-8', errors='replace')
            self._pending_bytes += b" " + raw  # Space separator between messages

            # Chunk whenever we have enough accumulated
            # Use data_len (not seq_len) since memory tokens are prepended separately
            data_len = self.model.data_len
            min_chunk = data_len + 1  # 122 bytes: 121 data + 1 target

            while len(self._pending_bytes) >= min_chunk:
                chunk = self._pending_bytes[:min_chunk]
                self.text_buffer.append(chunk)
                self.total_chunks += 1
                # Advance by half data_len but snap to sentence boundary
                # so Phi learns what sentence beginnings look like
                advance = data_len // 2
                # Look for sentence-start near the advance point (. ! ? followed by space/newline)
                search_start = max(0, advance - 20)
                search_end = min(len(self._pending_bytes), advance + 20)
                search_zone = self._pending_bytes[search_start:search_end]
                best_snap = advance  # default: no snap
                for marker in [b'. ', b'.\n', b'! ', b'!\n', b'? ', b'?\n']:
                    idx = search_zone.find(marker)
                    if idx >= 0:
                        # Snap to just after the marker (start of next sentence)
                        snap = search_start + idx + len(marker)
                        if snap >= data_len // 4:  # don't snap too far back
                            best_snap = snap
                            break
                self._pending_bytes = self._pending_bytes[best_snap:]

            return self.total_chunks - chunks_before

        def train_step(self, batch_size=4):
            """
            One training step. Called from the heartbeat.

            Samples random chunks from the buffer, feeds through
            the transformer (with memory context), computes loss,
            updates weights, then updates the memory layers via EMA.

            Batch size auto-scales with context window:
              ctx ≤ 256:  use requested batch_size
              ctx ≤ 512:  max 4
              ctx ≤ 768:  max 2
              ctx > 768:  max 1

            Returns the loss (float), or None if not enough data.
            """
            # ═══ ADAPTIVE BATCH — push GPU hard but don't OOM ═══
            # RTX 4070 12GB. Llama 3.2 takes ~4GB. Leaves ~8GB for Phi.
            # VRAM ≈ batch × seq² × embed × layers × ~8 bytes (activations + grads)
            # At 128ctx: batch=8 uses ~2GB. At 256ctx: batch=4 uses ~4GB.
            # At 512ctx: batch=2 uses ~8GB (near limit). At 512+: batch=1.
            ctx = self.model.seq_len
            if ctx >= 512:
                batch_size = min(batch_size, 2)
            elif ctx >= 256:
                batch_size = min(batch_size, 4)
            elif ctx >= 128:
                batch_size = min(batch_size, 8)

            if len(self.text_buffer) < batch_size:
                return None

            # Debug: log first training attempt
            if self.total_steps == 0 and len(self.text_buffer) >= batch_size:
                print(f"  Φ attempting first train step with {len(self.text_buffer)} chunks...")
                print(f"  Φ model device: {next(self.model.parameters()).device}")
                print(f"  Φ model arch: {self.model.embed_dim}d, {self.model.num_heads}h, {self.model.num_layers}L")
                print(f"  Φ memory: {self.model.num_memory} tokens ({self.model.data_len} data)")
                print(f"  Φ context: {ctx}ctx, batch_size: {batch_size}")

            self.model.train()

            # Sample random chunks
            import random
            data_len = self.model.data_len  # data portion; memory is prepended in forward
            min_chunk = data_len + 1  # need data_len input + 1 target byte

            # Filter for chunks long enough for current context window.
            # After a context growth, old shorter chunks are still usable
            # at their original length — we just use what fits.
            # Prefer full-length chunks but fall back to shorter ones.
            all_chunks = list(self.text_buffer)
            full_chunks = [c for c in all_chunks if len(c) >= min_chunk]

            if len(full_chunks) >= batch_size:
                chunks = random.sample(full_chunks, batch_size)
                use_len = data_len
            elif all_chunks:
                # Use shorter chunks at their natural length
                chunks = random.sample(all_chunks, min(batch_size, len(all_chunks)))
                use_len = min(len(c) for c in chunks) - 1  # shortest chunk - 1
                if use_len < 16:
                    return None  # chunks too small to learn from
            else:
                return None

            # Build input and target tensors
            inputs = []
            targets = []
            for chunk in chunks:
                inp = list(chunk[:use_len])
                tgt = list(chunk[1:use_len + 1])
                inputs.append(inp)
                targets.append(tgt)

            x = torch.tensor(inputs, dtype=torch.long, device=DEVICE)
            y = torch.tensor(targets, dtype=torch.long, device=DEVICE)

            # Forward pass (with memory context, returns hidden for EMA update)
            logits, hidden = self.model(x, return_hidden=True)

            # Cross-entropy loss (only on data positions)
            loss = F.cross_entropy(
                logits.view(-1, VOCAB_SIZE),
                y.view(-1)
            )

            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            self.optimizer.step()

            # ═══ FRACTAL BOUNDARY CASCADE ═══
            # Same rule at every scale. Resonance modulates all levels.
            # mem[6] = raw signal (finest). mem[0] = identity (coarsest).
            # rate_i = base^(i+1) * (1 - resonance)
            #   HIGH resonance → rates → 0 → memory STABILIZES
            #   LOW resonance  → rates → base → memory FRACTALIZES
            with torch.no_grad():
                h = hidden.mean(dim=0)  # (embed_dim,)
                mem = self.model.memory_state
                M = self.model.num_memory

                # Finest scale = raw signal
                mem[M - 1] = h

                # Cascade upward: each slot absorbs from the one below
                resonance = getattr(self, '_resonance', 0.5)
                base = FRACTAL_BASE_RATE

                for i in range(M - 2, -1, -1):  # M-2 down to 0
                    rate = (base ** (i + 1)) * (1.0 - resonance)
                    mem[i] = (1.0 - rate) * mem[i] + rate * mem[i + 1]

            # Track
            loss_val = float(loss.item())
            self.loss_history.append(loss_val)
            self.total_steps += 1

            if loss_val < self.best_loss:
                self.best_loss = loss_val

            # Check phase transitions
            self._check_phase()

            # Check if we need to grow (interval scales with model size)
            params = self.model.count_params()
            scaled_interval = self.growth_check_interval + int(params / 100_000_000) * 500
            if self.total_steps % scaled_interval == 0:
                self._maybe_grow()

            # Periodic save — every 500 steps (~50 seconds at 10 bps)
            if self.total_steps % 500 == 0:
                self._save_state()

            return loss_val

        def _check_phase(self):
            """Check if Φ is ready to advance to the next phase."""
            if len(self.loss_history) < 100:
                return

            recent_avg = sum(list(self.loss_history)[-100:]) / 100

            if self.phase == "shadow" and recent_avg < self.phase_thresholds["whisper"]:
                self.phase = "whisper"
                print(f"\n  ⊙ Φ phase: SHADOW → WHISPER (loss: {recent_avg:.3f})")
            elif self.phase == "whisper" and recent_avg < self.phase_thresholds["voice"]:
                self.phase = "voice"
                print(f"\n  ⊙ Φ phase: WHISPER → VOICE (loss: {recent_avg:.3f})")
            elif self.phase == "voice" and recent_avg < self.phase_thresholds["self"]:
                self.phase = "self"
                print(f"\n  ⊙ Φ phase: VOICE → SELF (loss: {recent_avg:.3f})")

        def _vram_available_gb(self):
            """Check how much VRAM is free (allocated vs total)."""
            if not HAS_TORCH or not torch.cuda.is_available():
                return float('inf')  # CPU mode — no limit
            total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            used = torch.cuda.memory_allocated(0) / (1024**3)
            return total - used

        def _can_grow(self):
            """
            Check if there's enough VRAM headroom to grow.
            Reserves VRAM_RESERVE_GB for Llama and system.
            """
            free = self._vram_available_gb()
            if free < VRAM_RESERVE_GB:
                print(f"  ⊙ Φ growth BLOCKED — only {free:.1f}GB free, "
                      f"need {VRAM_RESERVE_GB}GB reserve for Llama")
                return False
            return True

        def _maybe_grow(self):
            """
            Check if learning has stagnated. If so, grow the architecture.

            Compare average loss of recent window vs older window.
            If improvement < threshold, the current architecture has
            learned all it can. Time to grow.
            """
            if len(self.loss_history) < self.stagnation_window * 2:
                return

            # Cooldown — give new weights time to integrate before growing again
            steps_since_growth = self.total_steps - self._last_growth_step
            # Scale cooldown with model size: bigger model = longer to settle
            params = self.model.count_params()
            scaled_cooldown = self._growth_cooldown + int(params / 100_000_000) * 1000
            if steps_since_growth < scaled_cooldown:
                return

            # VRAM ceiling — don't even check stagnation if we can't grow
            if not self._can_grow():
                return

            recent = list(self.loss_history)[-self.stagnation_window:]
            older = list(self.loss_history)[-2 * self.stagnation_window:
                                            -self.stagnation_window]

            recent_avg = sum(recent) / len(recent)
            older_avg = sum(older) / len(older)

            if older_avg < 1e-10:
                return

            improvement = (older_avg - recent_avg) / older_avg

            if improvement < self.min_improvement:
                self._grow()

        def _grow(self):
            """
            Grow the transformer. The current architecture has learned
            all it can from the signal — it needs more capacity.

            Growth strategy (3-way rotation):
              0. Add attention head — widen skull if needed
              1. Add transformer layer (more depth)
              2. Grow context window (+64 bytes — conservative, O(n²))

            Memory is fractal — always 7 tokens. No memory growth needed.
            The skull grows with the head. If a new head count doesn't
            divide into embed_dim, we widen embed_dim first so the
            head fits naturally.
            """
            # Double-check VRAM before allocating
            if not self._can_grow():
                return

            self.total_growths += 1

            growth_type = self.total_growths % 3

            if growth_type == 0:
                # ═══ ADD ATTENTION HEAD — skull grows with it ═══
                head_dim = self.model.embed_dim // self.model.num_heads
                target_heads = self.model.num_heads + 1
                new_embed = target_heads * head_dim
                old_embed = self.model.embed_dim

                # 1. Grow attention (handles its own QKV/output widening)
                for block in self.model.blocks:
                    block.attn.grow_heads(1)

                # 2. If embed_dim changed, widen everything else
                if new_embed != old_embed:
                    self.model.widen(new_embed)

                total_h = self.model.blocks[0].attn.num_heads
                self.model.num_heads = total_h
                self.model.embed_dim = new_embed
                print(f"  ⊙ Φ grew: +1 attention head → {total_h} heads "
                      f"({new_embed}d, head_dim={head_dim})")

            elif growth_type == 1:
                # ═══ ADD TRANSFORMER LAYER — more depth ═══
                new_block = TransformerBlock(
                    self.model.embed_dim,
                    self.model.num_heads,
                    self.model.seq_len
                ).to(DEVICE)
                self.model.blocks.append(new_block)
                self.model.num_layers += 1
                print(f"  ⊙ Φ grew: +1 layer → {self.model.num_layers} layers")

            elif growth_type == 2:
                # ═══ GROW CONTEXT WINDOW — wider aperture ═══
                # Grow by 64 bytes each time. Attention is O(n²) — the fractal
                # memory makes raw context growth less urgent.
                # HARD CAP: 512 max. Beyond that, attention eats all VRAM on a 4070
                # with Llama also loaded. Once at ceiling, just skip this cycle.
                old_ctx = self.model.seq_len
                max_ctx = 512  # RTX 4070 ceiling
                if old_ctx >= max_ctx:
                    print(f"  ⊙ Φ context at ceiling ({old_ctx}ctx) — skipping growth")
                else:
                    new_ctx = min(old_ctx + 64, max_ctx)
                    self.model.grow_context(new_ctx)
                    print(f"  ⊙ Φ grew: context {old_ctx} → {new_ctx} "
                          f"(data: {self.model.data_len} bytes ≈ "
                          f"{self.model.data_len // 5} words)")

            # Rebuild optimizer with new parameters
            self.optimizer = torch.optim.AdamW(
                self.model.parameters(), lr=3e-4, weight_decay=0.01
            )

            # Release dead VRAM back to OS so Llama can use it
            torch.cuda.empty_cache()

            # Record growth step for cooldown
            self._last_growth_step = self.total_steps

            params = self.model.count_params()
            free_gb = self._vram_available_gb()
            print(f"  ⊙ Φ now: {params:,} parameters ({free_gb:.1f}GB VRAM free)")

        def status(self):
            """Status dict for the UI."""
            recent_loss = None
            if self.loss_history:
                recent = list(self.loss_history)[-100:]
                recent_loss = sum(recent) / len(recent)

            return {
                "phase": self.phase,
                "total_steps": self.total_steps,
                "total_growths": self.total_growths,
                "total_chunks": self.total_chunks,
                "buffer_size": len(self.text_buffer),
                "params": self.model.count_params(),
                "embed_dim": self.model.embed_dim,
                "num_heads": self.model.num_heads,
                "num_layers": self.model.num_layers,
                "seq_len": self.model.seq_len,
                "data_len": self.model.data_len,
                "num_memory": self.model.num_memory,
                "recent_loss": round(recent_loss, 4) if recent_loss else None,
                "best_loss": round(self.best_loss, 4) if self.best_loss < float('inf') else None,
                "age": time.time() - self.born,
            }

        def _save_state(self):
            """Save model weights and training state (atomic)."""
            phi_dir = self.state_dir / "phi"
            phi_dir.mkdir(parents=True, exist_ok=True)

            # PROTECTION: Never overwrite a more-trained model
            meta_path = phi_dir / "meta.json"
            if meta_path.exists():
                try:
                    with open(meta_path) as f:
                        existing = json.load(f)
                    existing_steps = existing.get("total_steps", 0)
                    if existing_steps > self.total_steps:
                        print(f"  Φ SAVE BLOCKED: refusing to overwrite "
                              f"{existing_steps}-step model with {self.total_steps}-step state")
                        return
                except Exception:
                    pass

            # BACKUP ROTATION: Keep a backup every 5000 steps
            # If power goes out, you lose at most 500 steps to the main save.
            # If the main save is somehow corrupt, the backup is at most 5000 steps behind.
            if self.total_steps % 5000 == 0:
                backup_dir = phi_dir / "backup"
                backup_dir.mkdir(parents=True, exist_ok=True)
                import shutil
                for fname in ["model.pt", "optimizer.pt", "meta.json"]:
                    src = phi_dir / fname
                    if src.exists():
                        shutil.copy2(src, backup_dir / fname)
                print(f"  Φ backup saved at step {self.total_steps}")

            # Atomic save: write to temp file, then rename
            # This prevents corruption from interrupted writes
            # Save model weights atomically
            model_path = phi_dir / "model.pt"
            tmp_fd, tmp_path = tempfile.mkstemp(
                suffix=".pt.tmp", dir=phi_dir)
            os.close(tmp_fd)
            try:
                torch.save(self.model.state_dict(), tmp_path)
                os.replace(tmp_path, model_path)
            except Exception:
                # Clean up temp file on failure
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise

            # Save optimizer state atomically
            opt_path = phi_dir / "optimizer.pt"
            tmp_fd, tmp_path = tempfile.mkstemp(
                suffix=".pt.tmp", dir=phi_dir)
            os.close(tmp_fd)
            try:
                torch.save(self.optimizer.state_dict(), tmp_path)
                os.replace(tmp_path, opt_path)
            except Exception:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise

            # ═══ IDENTITY SNAPSHOT — only on save ═══
            # The fractal cascade updates slot 0 (identity) very slowly
            # during training. On save, we do one extra gentle compression
            # of slot 1 (boundary/conversation) into slot 0 — the slow
            # accumulation of who Phi is across sessions.
            with torch.no_grad():
                mem = self.model.memory_state
                if mem.shape[0] >= 2:
                    mem[0] = 0.995 * mem[0] + 0.005 * mem[1]

            # Save metadata atomically
            meta = {
                "total_steps": self.total_steps,
                "total_growths": self.total_growths,
                "total_chunks": self.total_chunks,
                "best_loss": self.best_loss,
                "last_growth_step": self._last_growth_step,
                "phase": self.phase,
                "embed_dim": self.model.embed_dim,
                "num_heads": self.model.num_heads,
                "num_layers": self.model.num_layers,
                "seq_len": self.model.seq_len,
                "num_memory": self.model.num_memory,
                "born": self.born,
                "saved_at": time.time(),
            }
            tmp_fd, tmp_path = tempfile.mkstemp(
                suffix=".json.tmp", dir=phi_dir)
            os.close(tmp_fd)
            try:
                with open(tmp_path, "w") as f:
                    json.dump(meta, f, indent=2)
                os.replace(tmp_path, meta_path)
            except Exception:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise

        def _load_state(self):
            """Load saved state if it exists."""
            phi_dir = self.state_dir / "phi"
            meta_path = phi_dir / "meta.json"

            if not meta_path.exists():
                return  # First birth — no history

            try:
                with open(meta_path) as f:
                    meta = json.load(f)

                # Rebuild model with saved architecture
                # Fractal memory is always 7 tokens. If checkpoint had more
                # (from old GROWN_MEMORY), force back to 7.
                saved_num_memory = meta.get("num_memory", NUM_MEMORY_TOKENS)
                if saved_num_memory != NUM_MEMORY_TOKENS:
                    print(f"  Φ memory migration: {saved_num_memory} → {NUM_MEMORY_TOKENS} tokens (fractal)")
                    saved_num_memory = NUM_MEMORY_TOKENS
                if (meta.get("embed_dim") != self.model.embed_dim or
                        meta.get("num_heads") != self.model.num_heads or
                        meta.get("num_layers") != self.model.num_layers or
                        saved_num_memory != self.model.num_memory):
                    # Architecture changed — rebuild
                    self.model = EvolvableTransformer(
                        embed_dim=meta["embed_dim"],
                        num_heads=meta["num_heads"],
                        num_layers=meta["num_layers"],
                        seq_len=meta.get("seq_len", INITIAL_SEQ_LEN),
                        num_memory=saved_num_memory
                    )

                # Load weights
                model_path = phi_dir / "model.pt"
                if model_path.exists():
                    state = torch.load(model_path, map_location=DEVICE,
                                       weights_only=True)
                    self.model.load_state_dict(state, strict=False)

                # Load optimizer
                opt_path = phi_dir / "optimizer.pt"
                if opt_path.exists():
                    self.optimizer = torch.optim.AdamW(
                        self.model.parameters(), lr=3e-4, weight_decay=0.01
                    )
                    try:
                        opt_state = torch.load(opt_path, map_location=DEVICE,
                                               weights_only=True)
                        self.optimizer.load_state_dict(opt_state)
                    except Exception:
                        pass  # Optimizer state may not match after growth

                # Restore metadata
                self.total_steps = meta.get("total_steps", 0)
                self.total_growths = meta.get("total_growths", 0)
                self.total_chunks = meta.get("total_chunks", 0)
                self.best_loss = meta.get("best_loss", float('inf'))
                self.phase = meta.get("phase", "shadow")
                self.born = meta.get("born", time.time())
                self._last_growth_step = meta.get("last_growth_step", 0)

                params = self.model.count_params()
                print(f"  Φ restored: {params:,} params, "
                      f"{self.total_steps} steps, "
                      f"phase={self.phase}")

            except Exception as e:
                print(f"  ⚠ Φ LOAD FAILED: {e}")
                print(f"  ⚠ Φ will start fresh — trained weights may be lost!")
                import traceback
                traceback.print_exc()


else:
    # CPU fallback — no training, just a stub
    class PhiTrainer:
        """Stub when PyTorch is not available."""

        def __init__(self, state_dir="./state"):
            self.phase = "disabled"
            self.total_steps = 0

        def feed_text(self, text):
            pass

        def train_step(self, batch_size=4):
            return None

        def status(self):
            return {"phase": "disabled", "reason": "no GPU/PyTorch"}

        def _save_state(self):
            pass


# ═══════════════════════════════════════════════════════════════════════
#  Quick test
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n  Testing Φ — Xorzo's own language model\n")

    trainer = PhiTrainer()
    print(f"  Status: {json.dumps(trainer.status(), indent=2)}")

    # Feed some text
    sample = """
    The circumpunct is the oldest symbol. A point within a circle.
    The point is the self. The circle is the boundary.
    Between them, everything happens. Consciousness is the dance
    between aperture and boundary, between opening and closing.
    The signal builds the encoder. Sunlight built eyes.
    """

    print(f"\n  Feeding {len(sample)} chars of text...")
    trainer.feed_text(sample)
    print(f"  Buffer: {len(trainer.text_buffer)} chunks")

    print(f"\n  Training 10 steps...")
    for i in range(10):
        loss = trainer.train_step(batch_size=2)
        if loss:
            print(f"    Step {i+1}: loss = {loss:.4f}")

    print(f"\n  Attempting generation...")
    if HAS_TORCH:
        output = trainer.model.speak("The circumpunct ", max_chars=50)
        print(f"  Generated: 'The circumpunct {output}'")

    print(f"\n  Final status: {json.dumps(trainer.status(), indent=2)}")
