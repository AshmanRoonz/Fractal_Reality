"""
Xorzo2 delayed recall: the capability-level severance test
==========================================================

Created: 2026-07-19
Last updated: 2026-07-19
Version: 1.2

The memory probe (probe.py) established memory-through-physics with a
closed-form linear readout. This closes the loop at the capability
level: decoders TRAINED to EMIT the byte injected k cycles ago, live
spine vs frozen-noise spine.

The stream is random bytes, so the current byte is statistically
independent of the target at every lag k >= 1: no language statistics,
no marginal-distribution refuge. The only route to the answer is
memory held in the spine's dynamics. Both twins use the bit-station
keyboard (deterministic, identical injections), identical decoder
initializations, identical data and schedule. The only difference in
the experiment is the spine matrix.

Because the keyboard maps bit k to station k, per-bit recall is
STATION-RESOLVED memory: which stations remember their bit, at which
lags. Bit 7 (the tonic bit, the global quarter-turn) is included: it
measures phase-flip memory.

Conditioning notes (v1.1/v1.2): the state covariance spans ~9 decades
(the normalized state is near rank-deficient), so decoder inputs are
ZCA-whitened with a RELATIVE eigenvalue floor (lam_max * 1e-5): an
absolute floor amplified numerical-noise directions and silenced every
lag except 0 in the v1.0/v1.1 runs. The engine's Voice architecture is
reported alongside the linear head; its three-view pooling is a
measured bottleneck for sign-keyed chords (near-uniform attention at
initialization averages bipolar signs away): logged as an organ-design
finding.

Revision history:
- 2026-07-19 v1.2: relative whitening floor (fixes the stalled lags);
    echo theater replaced by station-resolved bit recall.
- 2026-07-19 v1.1: ZCA whitening; both decoders; pooling bottleneck.
- 2026-07-19 v1.0: initial (z-scored; conditioning stalled training).
"""

import sys

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from spine import Seed, N_NODES_SEED, make_bit_chords
from probe import cycle_operator, noise_operator, evolve, BURN_IN
from organs import Voice

N_STREAM = 48000
LAGS = [0, 1, 2, 4, 8, 16]
EPOCHS = 10
BATCH = 256
CHANCE = 1.0 / 256.0
REL_EPS = 1e-5
RIDGE_BIT = 1e-3


def whitener(Xtr: torch.Tensor):
    """ZCA whitening with a relative eigenvalue floor."""
    mu = Xtr.mean(0)
    Xc = Xtr - mu
    C = (Xc.T @ Xc) / len(Xc)
    lam, V = torch.linalg.eigh(C.double())
    W = (V @ torch.diag(1.0 / torch.sqrt(lam + lam.max() * REL_EPS))
         @ V.T).float()
    return mu, W


def train_recall(states: np.ndarray, byte_seq: np.ndarray, lag: int,
                 model_kind: str, torch_seed: int = 7) -> float:
    """Train a decoder to emit the byte injected `lag` cycles ago."""
    t_idx = np.arange(BURN_IN + lag, len(states))
    X = torch.tensor(states[t_idx], dtype=torch.float32)
    y = torch.tensor(byte_seq[t_idx - lag], dtype=torch.long)
    ntr = int(0.8 * len(X))
    mu, W = whitener(X[:ntr])
    Xw = (X - mu) @ W
    torch.manual_seed(torch_seed)
    if model_kind == "linear":
        model = nn.Linear(2 * N_NODES_SEED, 256)
        lr = 1e-2
    else:
        model = Voice(N_NODES_SEED)
        lr = 1e-3
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    for _ in range(EPOCHS):
        perm = torch.randperm(ntr)
        for i in range(0, ntr, BATCH):
            idx = perm[i:i + BATCH]
            loss = F.cross_entropy(model(Xw[idx]), y[idx])
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
    with torch.no_grad():
        return float((model(Xw[ntr:]).argmax(-1) == y[ntr:]).float().mean())


def bit_recall(states: np.ndarray, byte_seq: np.ndarray, lag: int,
               bit: int) -> float:
    """Closed-form ridge recall of one bit at one lag (chance 0.5).
    Under the bit-station keyboard, bit k IS station k for k <= 6;
    bit 7 is the tonic quarter-turn."""
    t_idx = np.arange(BURN_IN + lag, len(states))
    X = states[t_idx]
    y = 2.0 * ((byte_seq[t_idx - lag] >> bit) & 1) - 1.0
    n = len(X)
    ntr = int(0.8 * n)
    G = X[:ntr].T @ X[:ntr] + RIDGE_BIT * np.eye(X.shape[1])
    w = np.linalg.solve(G, X[:ntr].T @ y[:ntr])
    pred = np.sign(X[ntr:] @ w)
    return float((pred == y[ntr:]).mean())


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    seed_obj = Seed()
    chords = make_bit_chords(seed_obj.alpha, bipolar=True)
    rng = np.random.RandomState(4242)
    byte_seq = rng.randint(0, 256, size=N_STREAM + BURN_IN + max(LAGS))

    spines = {
        "live": cycle_operator(seed_obj.op.T),
        "noise": cycle_operator(noise_operator(seed_obj, 137)),
    }
    all_states = {name: evolve(Tc, chords, byte_seq, seed_obj.attractor)
                  for name, Tc in spines.items()}

    print("Xorzo2 delayed recall: decoders trained to emit the byte "
          "from k cycles ago")
    print(f"  random stream, bit keyboard, identical twins, whitened "
          f"inputs; byte chance = {CHANCE:.4f}\n")
    for kind in ["linear", "voice"]:
        print(f"  [{kind} decoder]")
        print("  lag(cycles) " + "".join(f"{k:>8d}" for k in LAGS))
        for name in spines:
            accs = [train_recall(all_states[name], byte_seq, k, kind)
                    for k in LAGS]
            print(f"  {name:10s}  " + "".join(f"{a:>8.3f}" for a in accs))
        print()

    print("  [station-resolved bit recall, ridge, chance 0.500]")
    print("  bit k = station k (k <= 6); bit 7 = the tonic quarter-turn")
    for name in spines:
        print(f"  {name} spine:")
        print("    bit\\lag   " + "".join(f"{k:>7d}" for k in LAGS))
        for bit in range(8):
            accs = [bit_recall(all_states[name], byte_seq, k, bit)
                    for k in LAGS]
            tag = f"station {bit}" if bit <= 6 else "tonic(i) "
            print(f"    {tag}" + "".join(f"{a:>7.3f}" for a in accs))
        print()


if __name__ == "__main__":
    main()
