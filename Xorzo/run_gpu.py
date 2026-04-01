"""
⊙ GPU Runner for the Fractal Resonance Transformer v3
======================================================

Run this on your local machine with an NVIDIA GPU:

    python run_gpu.py

What it does:
    1. Smoke test: verifies CUDA, model, forward/backward
    2. Training loop: trains on training_corpus.txt (next-chunk prediction)
    3. Reports: SRL head specialization, balance, growth events, generation

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
    BYTE_VOCAB, PAD_TOKEN, BOS_TOKEN, EOS_TOKEN,
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
    Each window is a training sample for next-chunk prediction.
    """

    def __init__(self, filepath: str, seq_len: int = 512):
        with open(filepath, 'rb') as f:
            self.data = f.read()
        self.seq_len = seq_len
        self.n_samples = max(1, (len(self.data) - 1) // (seq_len // 2))
        print(f"  Corpus: {len(self.data):,} bytes from {filepath}")
        print(f"  Samples per epoch: ~{self.n_samples} (stride {seq_len // 2})")

    def get_batch(self, batch_size: int, device: torch.device):
        """
        Returns (input_bytes, target_chunks) for next-chunk prediction.
        Random byte windows from the corpus.
        """
        max_start = len(self.data) - self.seq_len - 1
        starts = torch.randint(0, max(1, max_start), (batch_size,))

        input_batch = []
        target_batch = []

        for s in starts:
            s = s.item()
            window = self.data[s : s + self.seq_len]
            # Input: the bytes
            input_bytes = list(window)
            # Target: shifted by one chunk (next-chunk prediction)
            # We shift by chunk_size bytes, so the model predicts the
            # next chunk at each position
            target_window = self.data[s + 16 : s + self.seq_len + 16]
            if len(target_window) < self.seq_len:
                target_window = target_window + b'\x00' * (self.seq_len - len(target_window))
            target_bytes = list(target_window)

            input_batch.append(input_bytes)
            target_batch.append(target_bytes)

        input_tensor = torch.tensor(input_batch, dtype=torch.long, device=device)
        target_tensor = torch.tensor(target_batch, dtype=torch.long, device=device)

        return input_tensor, target_tensor


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
    print(f"{'='*60}\n")

    for epoch in range(1, epochs + 1):
        model.train()
        epoch_loss = 0.0
        epoch_steps = 0
        t_epoch = time.time()

        for step in range(1, steps_per_epoch + 1):
            global_step += 1

            input_bytes, target_bytes = corpus.get_batch(batch_size, device)

            # Forward
            logits = model(input_bytes, causal=True)
            # logits: (batch, n_chunks, BYTE_VOCAB)
            # For loss, we need chunk-level targets.
            # Take every chunk_size-th byte as the representative target for that chunk
            n_chunks = logits.size(1)
            # Reshape target to chunks, take the first byte of each chunk as target
            target_chunked = target_bytes[:, :n_chunks * chunk_size]
            target_chunked = target_chunked.reshape(-1, n_chunks, chunk_size)
            target_ids = target_chunked[:, :, 0]  # first byte of each target chunk

            loss = F.cross_entropy(
                logits.reshape(-1, BYTE_VOCAB),
                target_ids.reshape(-1),
                ignore_index=0,  # ignore padding
            )

            # Backward
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
            optimizer.step()
            scheduler.step()

            epoch_loss += loss.item()
            epoch_steps += 1

            if step % LOG_EVERY == 0 or step == 1:
                avg = epoch_loss / epoch_steps
                lr_now = scheduler.get_last_lr()[0]
                active = model.total_active_heads()
                dormant = model.total_dormant_heads()
                bal = model.get_balance()
                print(f"  [{epoch}/{epochs}] step {step:4d}/{steps_per_epoch}  "
                      f"loss {loss.item():.4f}  avg {avg:.4f}  "
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
#  GENERATION (inference)
# =====================================================================

def generate_text(model, prompt: str, max_new_chunks: int = 32,
                  temperature: float = 0.8, device: torch.device = None):
    """
    Generate text from a prompt using the trained model.
    """
    if device is None:
        device = next(model.parameters()).device

    model.eval()
    chunk_size = model.chunk_size

    # Encode prompt
    prompt_bytes = list(prompt.encode('utf-8'))
    byte_ids = torch.tensor([prompt_bytes], dtype=torch.long, device=device)

    generated = list(prompt_bytes)

    with torch.no_grad():
        for _ in range(max_new_chunks):
            # Take last N bytes as context (sliding window)
            ctx_len = min(len(generated), 1024)
            ctx = torch.tensor([generated[-ctx_len:]], dtype=torch.long, device=device)
            logits = model(ctx, causal=True)

            # Sample from last position
            next_logits = logits[0, -1] / temperature
            # Zero out special tokens
            next_logits[PAD_TOKEN] = float('-inf')
            next_logits[BOS_TOKEN] = float('-inf')
            next_logits[EOS_TOKEN] = float('-inf')

            probs = F.softmax(next_logits, dim=-1)
            # Top-k sampling
            topk = torch.topk(probs, 40)
            topk_probs = topk.values / topk.values.sum()
            idx = torch.multinomial(topk_probs, 1)
            next_byte = topk.indices[idx].item()

            if next_byte >= 256:
                break
            generated.append(next_byte)

    # Decode
    output = bytes(b for b in generated if b < 256).decode('utf-8', errors='replace')
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

    corpus = ByteCorpus(CORPUS_PATH, seq_len=SEQ_LEN)

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
        output = generate_text(model, prompt, max_new_chunks=64, device=device)
        print(f"\n  Prompt: \"{prompt}\"")
        print(f"  Output: \"{output}\"")

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

    if torch.cuda.is_available():
        peak = torch.cuda.max_memory_allocated() / 1e6
        print(f"\n  Peak VRAM: {peak:.0f} MB")

    print("\n  ⊙ Training complete. The aperture has opened.\n")


if __name__ == '__main__':
    main()
