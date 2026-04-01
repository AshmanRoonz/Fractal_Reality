"""
⊙ GPU Runner for the Fractal Resonance Transformer v3
======================================================

Run this on your local machine with an NVIDIA GPU:

    python run_gpu.py

What it does:
    1. Smoke test: verifies CUDA, model, forward/backward
    2. Training loop: trains on training_corpus.txt (next-byte prediction)
    3. Balance regulation: homeostatic ◐ correction prevents drift
    4. Reports: SRL head specialization, balance, growth events
    5. Generation: chunk-aligned sliding window, proper text output

Requirements:
    pip install torch  (with CUDA support)

Author: Ashman Roonz & Claude
Date: April 2026
"""

import torch
import torch.nn.functional as F
import time
import os
import math
import sys

# Import from the same directory
from fractal_resonance_transformer_v3 import (
    FractalResonanceTransformerV3, frt_v3_small, frt_v3_medium,
    BYTE_VOCAB, PAD_TOKEN, BOS_TOKEN, EOS_TOKEN, KAPPA,
    file_to_bytes, text_to_bytes, bytes_to_text,
)
from sensory_modules import LanguageModule, SensoryModuleManager


# =====================================================================
#  CONFIG
# =====================================================================

# Training
EPOCHS = 10
BATCH_SIZE = 8
SEQ_LEN = 512          # bytes per sample
LEARNING_RATE = 3e-4
WEIGHT_DECAY = 0.01
GRAD_CLIP = 1.0
LOG_EVERY = 25         # steps between status prints
SAVE_EVERY = 2         # epochs between checkpoints

# Balance regulation
KAPPA_REG_WEIGHT = 0.01         # soft L2 pull on kappa toward initial value
BALANCE_RESTORE_INTERVAL = 10   # steps between homeostatic checks
BALANCE_LOW = 0.35              # below this: too much compression
BALANCE_HIGH = 0.65             # above this: too little compression
BALANCE_NUDGE = 0.995           # multiplicative correction per check

# Model: use 'small' for RTX 5050 (8GB VRAM fits this comfortably)
MODEL_SIZE = 'small'   # 'small' (~1.8M), 'medium' (~30M), 'large' (~100M)

# Data
CORPUS_PATH = os.path.join(os.path.dirname(__file__), 'training_corpus.txt')
CHECKPOINT_DIR = os.path.join(os.path.dirname(__file__), 'checkpoints')


# =====================================================================
#  DATA: BYTE-LEVEL DATASET
# =====================================================================

class ByteCorpus:
    """
    Loads a text file as raw bytes and serves fixed-length windows.
    Each window is a training sample for next-byte prediction.

    The target for each chunk position is the first byte that follows
    the chunk: given chunk i (bytes[i*cs : (i+1)*cs]), predict
    bytes[(i+1)*cs]. This is next-byte prediction at chunk granularity.
    """

    def __init__(self, filepath: str, seq_len: int = 512, chunk_size: int = 16):
        with open(filepath, 'rb') as f:
            self.data = f.read()
        self.seq_len = seq_len
        self.chunk_size = chunk_size
        self.n_samples = max(1, (len(self.data) - seq_len - chunk_size) // (seq_len // 2))
        print(f"  Corpus: {len(self.data):,} bytes from {filepath}")
        print(f"  Samples per epoch: ~{self.n_samples} (stride {seq_len // 2})")

    def get_batch(self, batch_size: int, device: torch.device):
        """
        Returns (input_bytes, target_ids) for next-byte prediction.

        input_bytes: (batch, seq_len) raw byte windows
        target_ids:  (batch, n_chunks) the byte immediately following
                     each chunk; target[i] = data[start + (i+1)*chunk_size]
        """
        cs = self.chunk_size
        max_start = len(self.data) - self.seq_len - cs
        starts = torch.randint(0, max(1, max_start), (batch_size,))

        input_batch = []
        target_batch = []

        n_chunks = self.seq_len // cs

        for s in starts:
            s = s.item()
            window = self.data[s : s + self.seq_len]
            input_batch.append(list(window))

            # Target: for chunk i, predict the first byte of chunk i+1
            # That byte lives at offset (i+1)*cs in the window
            targets = []
            for i in range(n_chunks):
                target_pos = s + (i + 1) * cs
                if target_pos < len(self.data):
                    targets.append(self.data[target_pos])
                else:
                    targets.append(0)  # padding
            target_batch.append(targets)

        input_tensor = torch.tensor(input_batch, dtype=torch.long, device=device)
        target_tensor = torch.tensor(target_batch, dtype=torch.long, device=device)

        return input_tensor, target_tensor


# =====================================================================
#  BALANCE REGULATION
# =====================================================================
#
#  Two mechanisms keep ◐ near 0.5:
#
#  1. Differentiable kappa regularization: a soft L2 penalty on the
#     fold's compression exponent (head_kappa). Prevents kappa from
#     growing unbounded, which is what drives ◐ toward 0.
#
#  2. Homeostatic correction: a non-gradient nudge applied every N
#     steps. If ◐ drifts below 0.35, scale kappa down slightly;
#     if it drifts above 0.65, scale up. This is analogous to
#     biological homeostasis: the system self-corrects without
#     needing the loss to encode it.
#
#  Together these keep the system in the balanced regime (◐ ~ 0.5)
#  where the fold compresses old information but preserves resonant
#  patterns: the breath of ⊛ and ☀︎ in equilibrium.
#
# =====================================================================

def compute_kappa_regularization(model):
    """
    Soft L2 pull on head_kappa toward its initial value.
    Prevents compression from growing unbounded.
    """
    kappa_init = F.softplus(torch.tensor(KAPPA))
    reg = 0.0
    for layer in model.attn_layers:
        kappa_vals = F.softplus(layer.head_kappa)
        reg = reg + (kappa_vals - kappa_init).pow(2).mean()
    return reg


def homeostatic_balance_check(model, step):
    """
    Non-gradient correction: nudge kappa if ◐ drifts too far from 0.5.
    Applied every BALANCE_RESTORE_INTERVAL steps.
    """
    if step % BALANCE_RESTORE_INTERVAL != 0:
        return

    bal = model.get_balance()
    with torch.no_grad():
        if bal < BALANCE_LOW:
            # Over-compressing (too much ⊛): reduce kappa
            for layer in model.attn_layers:
                layer.head_kappa.data *= BALANCE_NUDGE
        elif bal > BALANCE_HIGH:
            # Under-compressing (too little ⊛): increase kappa
            for layer in model.attn_layers:
                layer.head_kappa.data *= (2.0 - BALANCE_NUDGE)


# =====================================================================
#  TRAINING LOOP
# =====================================================================

def train(model, corpus, device, epochs=EPOCHS, batch_size=BATCH_SIZE,
          lr=LEARNING_RATE):

    optimizer = torch.optim.AdamW(
        model.parameters(), lr=lr, weight_decay=WEIGHT_DECAY,
        betas=(0.9, 0.95),
    )

    # Cosine annealing over total steps
    steps_per_epoch = corpus.n_samples // batch_size
    total_steps = epochs * steps_per_epoch
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=total_steps, eta_min=lr / 10,
    )

    chunk_size = model.chunk_size
    global_step = 0
    best_loss = float('inf')

    print(f"\n{'='*60}")
    print(f"  TRAINING: {epochs} epochs, {steps_per_epoch} steps/epoch")
    print(f"  Batch: {batch_size}, Seq: {corpus.seq_len} bytes")
    print(f"  LR: {lr}, Grad clip: {GRAD_CLIP}")
    print(f"  Balance regulation: kappa_reg={KAPPA_REG_WEIGHT}, "
          f"homeostatic every {BALANCE_RESTORE_INTERVAL} steps")
    print(f"{'='*60}\n")

    for epoch in range(1, epochs + 1):
        model.train()
        epoch_loss = 0.0
        epoch_steps = 0
        t_epoch = time.time()

        for step in range(1, steps_per_epoch + 1):
            global_step += 1

            input_bytes, target_ids = corpus.get_batch(batch_size, device)

            # Forward
            logits = model(input_bytes, causal=True)
            # logits: (batch, n_chunks, BYTE_VOCAB)
            n_chunks = logits.size(1)
            # Trim target to match (in case of rounding)
            target = target_ids[:, :n_chunks]

            main_loss = F.cross_entropy(
                logits.reshape(-1, BYTE_VOCAB),
                target.reshape(-1),
                ignore_index=0,  # ignore padding
            )

            # Balance regulation: soft kappa regularization
            kappa_reg = compute_kappa_regularization(model)
            loss = main_loss + KAPPA_REG_WEIGHT * kappa_reg

            # Backward
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
            optimizer.step()
            scheduler.step()

            # Homeostatic balance correction (non-gradient)
            homeostatic_balance_check(model, global_step)

            epoch_loss += main_loss.item()
            epoch_steps += 1

            if step % LOG_EVERY == 0 or step == 1:
                avg = epoch_loss / epoch_steps
                lr_now = scheduler.get_last_lr()[0]
                active = model.total_active_heads()
                dormant = model.total_dormant_heads()
                bal = model.get_balance()
                print(f"  [{epoch}/{epochs}] step {step:4d}/{steps_per_epoch}  "
                      f"loss {main_loss.item():.4f}  avg {avg:.4f}  "
                      f"lr {lr_now:.2e}  "
                      f"heads {active}+{dormant}d  "
                      f"◐ {bal:.3f}")

        epoch_time = time.time() - t_epoch
        avg_loss = epoch_loss / max(epoch_steps, 1)

        print(f"\n  Epoch {epoch} complete: avg loss {avg_loss:.4f}, "
              f"time {epoch_time:.1f}s")

        # Report SRL state
        report_srl(model, epoch)

        # Report any head growth
        growth = model.get_growth_summary()
        if growth.strip():
            print(f"\n  Head growth events:\n{growth}")

        # Save checkpoint
        if epoch % SAVE_EVERY == 0 or avg_loss < best_loss:
            if avg_loss < best_loss:
                best_loss = avg_loss
            save_checkpoint(model, optimizer, epoch, avg_loss)

        print()

    return model


# =====================================================================
#  SRL REPORTING
# =====================================================================

def report_srl(model, epoch):
    """Show how heads have specialized after training."""
    print(f"\n  SRL State (epoch {epoch}):")
    for i, layer in enumerate(model.attn_layers):
        srl = layer.srl
        lock = torch.sigmoid(srl.lock_strength).detach()
        carrier = srl.carrier_freq.detach()
        active = layer.nursery.active_mask

        active_locks = lock[active]
        active_carriers = carrier[active]

        if len(active_locks) > 0:
            locked = (active_locks > 0.5).sum().item()
            total = len(active_locks)
            max_lock = active_locks.max().item()
            print(f"    Layer {i}: {locked}/{total} heads locked (max lock {max_lock:.3f}), "
                  f"carrier range [{active_carriers.min():.2f}, {active_carriers.max():.2f}]")


# =====================================================================
#  GENERATION (chunk-aligned sliding window)
# =====================================================================
#
#  The model operates on chunks: every chunk_size bytes are projected
#  into one d_model vector. At each chunk position, it predicts the
#  first byte after that chunk.
#
#  Generation strategy:
#    1. Maintain a fixed-size context buffer (multiple of chunk_size).
#    2. Forward pass: get prediction at last chunk position.
#    3. Sample a byte: this is the next byte in the stream.
#    4. Slide the window right by 1 byte (drop first byte, append new).
#    5. Repeat.
#
#  The context is always exactly ctx_size bytes (a multiple of
#  chunk_size), so the encoder never needs to pad. Chunk boundaries
#  shift by 1 byte each step, which the model handles because
#  training uses random start positions (different chunk alignments).
#
#  This produces one byte per forward pass, which is expensive but
#  correct. On GPU it's fast enough for short generations.
#
# =====================================================================

def generate_text(model, prompt: str, max_new_bytes: int = 256,
                  temperature: float = 0.8, top_k: int = 40,
                  ctx_size: int = 512, device: torch.device = None):
    """
    Generate text from a prompt using chunk-aligned sliding window.

    Args:
        prompt: seed text
        max_new_bytes: how many bytes to generate
        temperature: sampling temperature (lower = more deterministic)
        top_k: top-k sampling width
        ctx_size: context window in bytes (must be multiple of chunk_size)
        device: torch device
    """
    if device is None:
        device = next(model.parameters()).device

    model.eval()
    cs = model.chunk_size

    # Ensure ctx_size is a multiple of chunk_size
    ctx_size = (ctx_size // cs) * cs
    if ctx_size < cs:
        ctx_size = cs

    # Encode prompt
    prompt_bytes = list(prompt.encode('utf-8'))

    # Build initial context buffer: left-pad with zeros to fill ctx_size
    if len(prompt_bytes) >= ctx_size:
        # Prompt fills or exceeds context: take the last ctx_size bytes
        ctx = prompt_bytes[-ctx_size:]
    else:
        # Left-pad with zeros so the prompt is right-aligned
        pad_len = ctx_size - len(prompt_bytes)
        ctx = [0] * pad_len + prompt_bytes

    generated_bytes = []

    with torch.no_grad():
        for _ in range(max_new_bytes):
            ctx_tensor = torch.tensor([ctx], dtype=torch.long, device=device)
            logits = model(ctx_tensor, causal=True)

            # Last chunk position predicts the next byte
            next_logits = logits[0, -1] / temperature

            # Suppress special tokens (not real bytes)
            next_logits[PAD_TOKEN] = float('-inf')
            next_logits[BOS_TOKEN] = float('-inf')
            next_logits[EOS_TOKEN] = float('-inf')

            probs = F.softmax(next_logits, dim=-1)

            # Top-k sampling
            topk = torch.topk(probs, min(top_k, probs.size(-1)))
            topk_probs = topk.values / topk.values.sum()
            idx = torch.multinomial(topk_probs, 1)
            next_byte = topk.indices[idx].item()

            if next_byte >= 256:
                break

            generated_bytes.append(next_byte)

            # Slide window: drop first byte, append new byte
            ctx = ctx[1:] + [next_byte]

    # Decode: prompt + generated
    all_bytes = prompt_bytes + generated_bytes
    output = bytes(b for b in all_bytes if b < 256).decode('utf-8', errors='replace')
    return output


# =====================================================================
#  CHECKPOINT
# =====================================================================

def save_checkpoint(model, optimizer, epoch, loss):
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    path = os.path.join(CHECKPOINT_DIR, f'frt_v3_epoch{epoch}.pt')
    torch.save({
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss,
        'balance': model.get_balance(),
        'active_heads': model.total_active_heads(),
    }, path)
    print(f"  Checkpoint saved: {path}")


# =====================================================================
#  MAIN
# =====================================================================

def main():
    print("\n⊙ FRACTAL RESONANCE TRANSFORMER v3: GPU RUNNER")
    print("=" * 55)

    # ── Device ──
    if torch.cuda.is_available():
        device = torch.device('cuda')
        gpu_name = torch.cuda.get_device_name(0)
        props = torch.cuda.get_device_properties(0)
        vram = (getattr(props, 'total_memory', None) or getattr(props, 'total_mem', 0)) / 1e9
        print(f"  GPU: {gpu_name}")
        print(f"  VRAM: {vram:.1f} GB")
    else:
        device = torch.device('cpu')
        print("  No CUDA GPU detected; running on CPU (will be slower).")

    # ── Model ──
    print(f"\n  Building model: {MODEL_SIZE}")

    if MODEL_SIZE == 'small':
        model = frt_v3_small(chunk_size=16)
    elif MODEL_SIZE == 'medium':
        model = frt_v3_medium(chunk_size=16)
    elif MODEL_SIZE == 'large':
        from fractal_resonance_transformer_v3 import frt_v3_large
        model = frt_v3_large(chunk_size=16)
    else:
        raise ValueError(f"Unknown model size: {MODEL_SIZE}")

    model = model.to(device)
    print(model.summary())

    # ── Apply language sensory module ──
    print("\n  Applying LanguageModule sensory profile...")
    lang = LanguageModule()
    manager = SensoryModuleManager(modules=[lang])
    manager.apply_all(model)
    print(manager.summary())

    # ── Smoke test ──
    print("\n  Smoke test: forward + backward...")
    test_bytes = torch.randint(0, 256, (2, 256), device=device)
    model.train()
    out = model(test_bytes)
    target = torch.randint(0, BYTE_VOCAB, out.shape[:2], device=device)
    loss = F.cross_entropy(out.reshape(-1, BYTE_VOCAB), target.reshape(-1))
    loss.backward()
    print(f"  Forward: {out.shape}, Loss: {loss.item():.4f}")
    print(f"  Backward: OK (gradients flow)")

    if torch.cuda.is_available():
        mem_mb = torch.cuda.max_memory_allocated() / 1e6
        print(f"  Peak VRAM usage: {mem_mb:.0f} MB")

    # ── Load corpus ──
    print(f"\n  Loading corpus...")
    if not os.path.exists(CORPUS_PATH):
        print(f"  ERROR: {CORPUS_PATH} not found.")
        print(f"  Place your training data there and re-run.")
        return

    corpus = ByteCorpus(CORPUS_PATH, seq_len=SEQ_LEN, chunk_size=model.chunk_size)

    # ── Train ──
    model = train(model, corpus, device)

    # ── Generate ──
    print("\n" + "=" * 55)
    print("  GENERATION (post-training)")
    print("=" * 55)

    prompts = [
        "The circumpunct ",
        "Energy is ",
        "The aperture ",
        "Consciousness ",
    ]

    for prompt in prompts:
        output = generate_text(
            model, prompt,
            max_new_bytes=256,
            temperature=0.7,
            top_k=30,
            ctx_size=512,
            device=device,
        )
        # Show just the generated part (trim prompt)
        generated_part = output[len(prompt):]
        print(f"\n  Prompt: \"{prompt}\"")
        print(f"  Output: \"{prompt}{generated_part[:200]}\"")

    # ── Final report ──
    print("\n" + "=" * 55)
    print("  FINAL STATE")
    print("=" * 55)
    print(f"  ◐ (balance):   {model.get_balance():.4f}")
    print(f"  tau (temp):     {model.get_temperature():.4f}")
    print(f"  Active heads:   {model.total_active_heads()}")
    print(f"  Dormant heads:  {model.total_dormant_heads()}")
    print(f"\n  Growth log:")
    print(model.get_growth_summary())

    # Fold parameter state
    print(f"\n  Fold parameters (post-regulation):")
    for i, layer in enumerate(model.attn_layers):
        kappa_vals = F.softplus(layer.head_kappa).detach()
        lambda_vals = torch.sigmoid(layer.fold_lambda).detach()
        active = layer.nursery.active_mask
        ak = kappa_vals[active]
        al = lambda_vals[active]
        print(f"    Layer {i}: kappa [{ak.min():.3f}, {ak.max():.3f}]  "
              f"lambda [{al.min():.3f}, {al.max():.3f}]")

    if torch.cuda.is_available():
        peak = torch.cuda.max_memory_allocated() / 1e6
        print(f"\n  Peak VRAM: {peak:.0f} MB")

    print("\n  ⊙ Training complete. The aperture has opened.\n")


if __name__ == '__main__':
    main()
