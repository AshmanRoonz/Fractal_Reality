"""
⊙ Language Modeling Benchmark: Fractal Mamba v3 vs Standard Mamba
=================================================================

Character-level language modeling on tiny Shakespeare.
The real test: does fractal compression help with actual language?

Metrics:
    - Loss (cross-entropy, nats)
    - Perplexity (exp(loss); lower is better)
    - Bits per character (loss / ln(2))

Usage:
    python lm_benchmark.py                          # default settings
    python lm_benchmark.py --epochs 50 --d_model 128  # custom
    python lm_benchmark.py --fractal-only           # skip baseline

On GPU (RTX 5050): try d_model=128 or 256, n_layers=4, seq_len=256
On CPU: d_model=64, n_layers=2, seq_len=128 (slow but works)

Author: Ashman Roonz & Claude
Date: April 2026
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import os
import time
import argparse
from pathlib import Path

from circumpunct_mamba_v3 import FractalSSM, SelectiveSSM, PHI


# =====================================================================
#  DATASET: Character-level text
# =====================================================================

class CharDataset:
    """
    Character-level dataset. Maps chars to ints and back.
    Produces random chunks of (input, target) for next-char prediction.
    """
    def __init__(self, text: str, seq_len: int = 128):
        self.seq_len = seq_len
        chars = sorted(set(text))
        self.vocab_size = len(chars)
        self.char_to_idx = {c: i for i, c in enumerate(chars)}
        self.idx_to_char = {i: c for i, c in enumerate(chars)}
        self.data = torch.tensor([self.char_to_idx[c] for c in text], dtype=torch.long)
        self.n_chars = len(self.data)

    def get_batch(self, batch_size: int, device: torch.device):
        """Random batch of (input, target) sequences."""
        max_start = self.n_chars - self.seq_len - 1
        starts = torch.randint(0, max_start, (batch_size,))
        x = torch.stack([self.data[s:s+self.seq_len] for s in starts]).to(device)
        y = torch.stack([self.data[s+1:s+self.seq_len+1] for s in starts]).to(device)
        return x, y

    def decode(self, indices):
        """Convert tensor of indices back to string."""
        return ''.join(self.idx_to_char[i.item()] for i in indices)


# =====================================================================
#  LANGUAGE MODELS
# =====================================================================

class FractalLM(nn.Module):
    """Fractal Mamba v3 language model (character-level)."""
    def __init__(self, vocab_size: int, d_model: int = 64, state_size: int = 16,
                 n_layers: int = 2, kappa: float = 0.5, dropout: float = 0.1):
        super().__init__()
        self.d_model = d_model
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.drop = nn.Dropout(dropout)
        self.layers = nn.ModuleList([
            FractalSSM(d_model, state_size, kappa=kappa) for _ in range(n_layers)
        ])
        self.norms = nn.ModuleList([
            nn.LayerNorm(d_model) for _ in range(n_layers)
        ])
        self.final_norm = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size)

        # Weight tying: share embedding and output weights
        self.head.weight = self.embedding.weight

    def forward(self, x):
        h = self.drop(self.embedding(x))
        for layer, norm in zip(self.layers, self.norms):
            h = h + self.drop(layer(norm(h)))   # pre-norm residual
        return self.head(self.final_norm(h))

    def generate(self, start_tokens: torch.Tensor, max_new: int = 200,
                 temperature: float = 0.8):
        """Autoregressive generation."""
        self.eval()
        tokens = start_tokens.clone()
        with torch.no_grad():
            for _ in range(max_new):
                logits = self(tokens)
                logits = logits[:, -1, :] / temperature
                probs = F.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, 1)
                tokens = torch.cat([tokens, next_token], dim=1)
        return tokens


class StandardLM(nn.Module):
    """Standard Mamba language model (matched architecture)."""
    def __init__(self, vocab_size: int, d_model: int = 64, state_size: int = 16,
                 n_layers: int = 2, dropout: float = 0.1):
        super().__init__()
        self.d_model = d_model
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.drop = nn.Dropout(dropout)
        self.layers = nn.ModuleList([
            SelectiveSSM(d_model, state_size) for _ in range(n_layers)
        ])
        self.norms = nn.ModuleList([
            nn.LayerNorm(d_model) for _ in range(n_layers)
        ])
        self.final_norm = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size)

        self.head.weight = self.embedding.weight

    def forward(self, x):
        h = self.drop(self.embedding(x))
        for layer, norm in zip(self.layers, self.norms):
            h = h + self.drop(layer(norm(h)))
        return self.head(self.final_norm(h))

    def generate(self, start_tokens: torch.Tensor, max_new: int = 200,
                 temperature: float = 0.8):
        self.eval()
        tokens = start_tokens.clone()
        with torch.no_grad():
            for _ in range(max_new):
                logits = self(tokens)
                logits = logits[:, -1, :] / temperature
                probs = F.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, 1)
                tokens = torch.cat([tokens, next_token], dim=1)
        return tokens


# =====================================================================
#  TRAINING
# =====================================================================

def count_params(model):
    return sum(p.numel() for p in model.parameters())


def train_lm(model, dataset, n_epochs, batch_size, lr, device,
             label="Model", eval_interval=10, eval_batches=5,
             seq_len=128, verbose=True):
    """
    Train a language model and track loss/perplexity.
    Returns history list of dicts.
    """
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, n_epochs, eta_min=lr/10)

    n_params = count_params(model)
    if verbose:
        print(f"\n{'=' * 65}")
        print(f"  {label}")
        print(f"  Params: {n_params:,}  |  d={model.d_model}  |  {device}")
        print(f"  epochs={n_epochs}  batch={batch_size}  seq={seq_len}  lr={lr}")
        print(f"{'=' * 65}\n")

    history = []
    best_val_loss = float('inf')
    nan_skips = 0
    t0 = time.time()

    for epoch in range(n_epochs):
        model.train()
        x, y = dataset.get_batch(batch_size, device)
        logits = model(x)
        loss = F.cross_entropy(logits.view(-1, dataset.vocab_size), y.view(-1))

        if torch.isnan(loss) or torch.isinf(loss):
            optimizer.zero_grad()
            nan_skips += 1
            continue

        optimizer.zero_grad()
        loss.backward()

        # Check for NaN gradients
        if any(p.grad is not None and (torch.isnan(p.grad).any() or torch.isinf(p.grad).any())
               for p in model.parameters()):
            nan_skips += 1
            optimizer.zero_grad()
            continue

        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()

        # Evaluate
        if epoch % eval_interval == 0 or epoch == n_epochs - 1:
            model.eval()
            with torch.no_grad():
                val_losses = []
                for _ in range(eval_batches):
                    vx, vy = dataset.get_batch(batch_size, device)
                    vlogits = model(vx)
                    vloss = F.cross_entropy(vlogits.view(-1, dataset.vocab_size), vy.view(-1))
                    val_losses.append(vloss.item())
                val_loss = sum(val_losses) / len(val_losses)
                perplexity = math.exp(val_loss)
                bpc = val_loss / math.log(2)
                best_val_loss = min(best_val_loss, val_loss)
                best_ppl = math.exp(best_val_loss)
                best_bpc = best_val_loss / math.log(2)

            history.append({
                'epoch': epoch,
                'train_loss': loss.item(),
                'val_loss': val_loss,
                'perplexity': perplexity,
                'bpc': bpc,
                'best_val_loss': best_val_loss,
            })

            if verbose and (epoch % (eval_interval * 5) == 0 or epoch == n_epochs - 1):
                elapsed = time.time() - t0
                skip = f"  skip={nan_skips}" if nan_skips else ""
                print(f"  E{epoch:4d}  loss={val_loss:.4f}  ppl={perplexity:.1f}"
                      f"  bpc={bpc:.3f}  best_bpc={best_bpc:.3f}"
                      f"  [{elapsed:.0f}s]{skip}")

    best_ppl = math.exp(best_val_loss)
    best_bpc = best_val_loss / math.log(2)
    return history, best_val_loss, best_ppl, best_bpc


# =====================================================================
#  MAIN
# =====================================================================

def main():
    parser = argparse.ArgumentParser(description='⊙ Fractal Mamba v3 Language Modeling')
    parser.add_argument('--data', type=str, default=None,
                        help='Path to text file (default: data/shakespeare.txt)')
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--seq_len', type=int, default=128)
    parser.add_argument('--d_model', type=int, default=64)
    parser.add_argument('--state_size', type=int, default=16)
    parser.add_argument('--n_layers', type=int, default=2)
    parser.add_argument('--lr', type=float, default=0.001)
    parser.add_argument('--kappa', type=float, default=0.5)
    parser.add_argument('--dropout', type=float, default=0.1)
    parser.add_argument('--fractal-only', action='store_true',
                        help='Skip standard baseline')
    parser.add_argument('--generate', action='store_true',
                        help='Generate sample text after training')
    parser.add_argument('--gen_len', type=int, default=300,
                        help='Length of generated text')
    args = parser.parse_args()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Load data
    data_path = args.data
    if data_path is None:
        # Look for shakespeare.txt relative to this script
        script_dir = Path(__file__).parent
        data_path = script_dir / 'data' / 'shakespeare.txt'
        if not data_path.exists():
            print("No data file found. Downloading tiny Shakespeare...")
            import urllib.request
            data_path.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(
                'https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt',
                str(data_path))

    with open(data_path, 'r') as f:
        text = f.read()

    dataset = CharDataset(text, seq_len=args.seq_len)

    print(f"\n⊙ FRACTAL MAMBA v3: Language Modeling Benchmark")
    print(f"  Data: {len(text):,} chars, {dataset.vocab_size} unique, seq_len={args.seq_len}")
    print(f"  Device: {device}")
    print(f"  Architecture: d={args.d_model}, N={args.state_size}, "
          f"layers={args.n_layers}, kappa={args.kappa}")

    # ── Standard Mamba ──
    if not args.fractal_only:
        std_model = StandardLM(
            dataset.vocab_size, d_model=args.d_model, state_size=args.state_size,
            n_layers=args.n_layers, dropout=args.dropout
        ).to(device)

        std_h, std_loss, std_ppl, std_bpc = train_lm(
            std_model, dataset, args.epochs, args.batch_size, args.lr, device,
            label="STANDARD MAMBA (baseline)", seq_len=args.seq_len)

    # ── Fractal Mamba v3 ──
    frac_model = FractalLM(
        dataset.vocab_size, d_model=args.d_model, state_size=args.state_size,
        n_layers=args.n_layers, kappa=args.kappa, dropout=args.dropout
    ).to(device)

    frac_h, frac_loss, frac_ppl, frac_bpc = train_lm(
        frac_model, dataset, args.epochs, args.batch_size, args.lr, device,
        label="FRACTAL MAMBA v3", seq_len=args.seq_len)

    # ── Results ──
    print(f"\n{'=' * 65}")
    print(f"  RESULTS: Character-Level Language Modeling")
    print(f"  Dataset: {Path(data_path).name} ({len(text):,} chars)")
    if not args.fractal_only:
        std_params = count_params(std_model)
        print(f"\n  Standard Mamba:  bpc={std_bpc:.3f}  ppl={std_ppl:.1f}"
              f"  ({std_params:,} params)")
    frac_params = count_params(frac_model)
    print(f"  Fractal v3:      bpc={frac_bpc:.3f}  ppl={frac_ppl:.1f}"
          f"  ({frac_params:,} params)")
    if not args.fractal_only:
        delta_bpc = frac_bpc - std_bpc
        arrow = "+" if delta_bpc > 0 else ""
        print(f"\n  Delta bpc:       {arrow}{delta_bpc:.3f}"
              f"  ({'worse' if delta_bpc > 0 else 'BETTER'})")
        print(f"  Param ratio:     {frac_params/std_params:.2f}x")
    print(f"{'=' * 65}")

    # ── Generate sample ──
    if args.generate:
        print(f"\n{'~' * 65}")
        print("  GENERATED TEXT (Fractal Mamba v3)")
        print(f"{'~' * 65}\n")
        prompt = "ROMEO:\n"
        prompt_ids = torch.tensor(
            [[dataset.char_to_idx[c] for c in prompt]], dtype=torch.long
        ).to(device)
        generated = frac_model.generate(prompt_ids, max_new=args.gen_len, temperature=0.8)
        print(dataset.decode(generated[0]))

        if not args.fractal_only:
            print(f"\n{'~' * 65}")
            print("  GENERATED TEXT (Standard Mamba)")
            print(f"{'~' * 65}\n")
            generated_std = std_model.generate(prompt_ids, max_new=args.gen_len, temperature=0.8)
            print(dataset.decode(generated_std[0]))


if __name__ == '__main__':
    main()
