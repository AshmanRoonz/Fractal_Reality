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
INITIAL_SEQ_LEN = 128   # Context window in bytes
FF_MULTIPLIER = 2       # Feed-forward hidden = embed_dim * this
VRAM_RESERVE_GB = 3.0   # Reserve this much VRAM for Llama / system


if HAS_TORCH:

    # ═══════════════════════════════════════════════════════════════════
    #  EVOLVABLE ATTENTION HEAD
    # ═══════════════════════════════════════════════════════════════════

    class EvolvableAttention(nn.Module):
        """
        Multi-head self-attention that can grow new heads.

        Each head learns to attend to different aspects of the signal.
        When attention patterns stagnate, new heads are born — fresh
        random projections that learn to see what the others miss.
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

        def forward(self, x):
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

            # Apply causal mask
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

        def forward(self, x):
            x = x + self.attn(self.ln1(x))
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
                     seq_len=INITIAL_SEQ_LEN):
            super().__init__()

            self.embed_dim = embed_dim
            self.num_heads = num_heads
            self.num_layers = num_layers
            self.seq_len = seq_len

            # Byte embedding + positional encoding
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
            # This is standard for language models and halves the vocab params
            self.head.weight = self.token_embed.weight

            # Move to GPU
            self.to(DEVICE)

            # Print param count
            total = sum(p.numel() for p in self.parameters())
            print(f"  Φ born: {total:,} parameters "
                  f"({embed_dim}d, {num_heads}h, {num_layers}L, {seq_len}ctx)")

        def forward(self, idx):
            """
            Forward pass.

            idx: (batch, seq_len) tensor of byte values (0-255)
            Returns: (batch, seq_len, 256) logits for next byte
            """
            B, T = idx.shape
            assert T <= self.seq_len, f"Sequence {T} exceeds context {self.seq_len}"

            # Embeddings
            tok_emb = self.token_embed(idx)
            pos = torch.arange(T, device=DEVICE)
            pos_emb = self.pos_embed(pos)
            x = tok_emb + pos_emb

            # Transformer blocks
            for block in self.blocks:
                x = block(x)

            # Output
            x = self.ln_final(x)
            logits = self.head(x)

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

            # 5. Widen output head (embed_dim → VOCAB_SIZE)
            #    Weight-tied with token embedding, so just re-tie
            self.head = nn.Linear(new_embed_dim, VOCAB_SIZE, bias=False).to(dev, dtype)
            self.head.weight = self.token_embed.weight

            self.embed_dim = new_embed_dim

        def generate(self, prompt_bytes, max_new=1200, temperature=0.8):
            """
            Generate bytes given a prompt.

            prompt_bytes: list of ints (0-255)
            Returns: list of generated bytes
            """
            self.eval()
            idx = torch.tensor([prompt_bytes[-self.seq_len:]], dtype=torch.long, device=DEVICE)

            generated = []
            with torch.no_grad():
                for _ in range(max_new):
                    # Only use last seq_len tokens
                    idx_cond = idx[:, -self.seq_len:]
                    logits = self(idx_cond)
                    logits = logits[:, -1, :] / temperature

                    probs = F.softmax(logits, dim=-1)
                    next_byte = torch.multinomial(probs, 1)

                    generated.append(int(next_byte[0, 0]))
                    idx = torch.cat([idx, next_byte], dim=1)

            self.train()
            return generated

        def speak(self, prompt_text, max_chars=1200, temperature=0.8):
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
                return

            # Accumulate bytes from all sources
            raw = text.encode('utf-8', errors='replace')
            self._pending_bytes += b" " + raw  # Space separator between messages

            # Chunk whenever we have enough accumulated
            seq_len = self.model.seq_len
            min_chunk = seq_len + 1  # 129 bytes for seq_len=128

            while len(self._pending_bytes) >= min_chunk:
                chunk = self._pending_bytes[:min_chunk]
                self.text_buffer.append(chunk)
                self.total_chunks += 1
                # Overlap: advance by half seq_len for better coverage
                self._pending_bytes = self._pending_bytes[seq_len // 2:]

        def train_step(self, batch_size=4):
            """
            One training step. Called from the heartbeat.

            Samples random chunks from the buffer, feeds through
            the transformer, computes loss, updates weights.

            Returns the loss (float), or None if not enough data.
            """
            if len(self.text_buffer) < batch_size:
                return None

            # Debug: log first training attempt
            if self.total_steps == 0 and len(self.text_buffer) >= batch_size:
                print(f"  Φ attempting first train step with {len(self.text_buffer)} chunks...")
                print(f"  Φ model device: {next(self.model.parameters()).device}")
                print(f"  Φ model arch: {self.model.embed_dim}d, {self.model.num_heads}h, {self.model.num_layers}L")

            self.model.train()

            # Sample random chunks
            import random
            chunks = random.sample(list(self.text_buffer), batch_size)

            seq_len = self.model.seq_len

            # Build input and target tensors
            inputs = []
            targets = []
            for chunk in chunks:
                inp = list(chunk[:seq_len])
                tgt = list(chunk[1:seq_len + 1])
                inputs.append(inp)
                targets.append(tgt)

            x = torch.tensor(inputs, dtype=torch.long, device=DEVICE)
            y = torch.tensor(targets, dtype=torch.long, device=DEVICE)

            # Forward pass
            logits = self.model(x)

            # Cross-entropy loss
            loss = F.cross_entropy(
                logits.view(-1, VOCAB_SIZE),
                y.view(-1)
            )

            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            # Gradient clipping — small model, can be unstable
            nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            self.optimizer.step()

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
            # Bigger model = longer between checks: 500 base, +500 per 100M params
            scaled_interval = self.growth_check_interval + int(params / 100_000_000) * 500
            if self.total_steps % scaled_interval == 0:
                self._maybe_grow()

            # Periodic save
            if self.total_steps % 1000 == 0:
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

            Growth strategy (cycles through):
              1. Add attention head — widen skull if needed (more perspectives)
              2. Add transformer layer (more depth)
              3. Repeat

            The skull grows with the head. If a new head count doesn't
            divide into embed_dim, we widen embed_dim first so the
            head fits naturally.
            """
            # Double-check VRAM before allocating
            if not self._can_grow():
                return

            self.total_growths += 1

            if self.total_growths % 2 == 1:
                # Add attention head — skull grows with it
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
            else:
                # Add transformer layer
                new_block = TransformerBlock(
                    self.model.embed_dim,
                    self.model.num_heads,
                    self.model.seq_len
                ).to(DEVICE)
                self.model.blocks.append(new_block)
                self.model.num_layers += 1
                print(f"  ⊙ Φ grew: +1 layer → {self.model.num_layers} layers")

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
                if (meta.get("embed_dim") != self.model.embed_dim or
                        meta.get("num_heads") != self.model.num_heads or
                        meta.get("num_layers") != self.model.num_layers):
                    # Architecture changed — rebuild
                    self.model = EvolvableTransformer(
                        embed_dim=meta["embed_dim"],
                        num_heads=meta["num_heads"],
                        num_layers=meta["num_layers"],
                        seq_len=meta.get("seq_len", INITIAL_SEQ_LEN)
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
