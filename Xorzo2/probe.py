"""
Xorzo2 memory probe: does the physics remember?
===============================================

Created: 2026-07-19
Last updated: 2026-07-19
Version: 1.0

The severance test compares twins through language-modeling loss, which
confounds the spine's memory with decoder capacity and training
dynamics. This probe measures the claim directly, with no learning in
the loop:

    Inject a RANDOM byte stream through fixed random alpha-capped
    chords (one complex 7-vector per byte value, same chords for every
    spine). Evolve the state with the per-byte cycle operator
    (T_cycle = T^8, normalized). Then, for each lag k, fit a ridge
    linear probe from the state at time t to the identity of the byte
    injected at time t-k, and report held-out top-1 accuracy.

    Memory-through-physics is the claim that the live spine's
    near-unitary spectrum preserves injected phase information across
    cycles while a matched-spectral-radius noise matrix crushes its
    non-leading modes. If true: the live accuracy-vs-lag curve decays
    slowly; noise curves die within a few cycles. If the curves match,
    the seed spine's memory claim fails at this drive level.

No organs, no gradient descent, no corpus: chords are random, probes
are closed-form. What is being measured is the operator, alone.

Revision history:
- 2026-07-19 v1.0: initial probe (ridge readout, singular spectra,
    multi-seed noise baselines).
"""

import sys

import numpy as np

from spine import Seed, INJ_NODES, N_NODES_SEED, TICKS_PER_BYTE

BURN_IN = 200
N_STEPS = 30000
LAGS = [0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128]
RIDGE = 1e-3
CHANCE = 1.0 / 256.0


def make_chords(alpha: float, rng: np.random.RandomState) -> np.ndarray:
    """One fixed alpha-capped complex chord per byte value."""
    c = rng.randn(256, len(INJ_NODES)) + 1j * rng.randn(256, len(INJ_NODES))
    c *= (alpha / np.linalg.norm(c, axis=1, keepdims=True))
    return c


def cycle_operator(T: np.ndarray) -> np.ndarray:
    """The per-byte cycle: T^(ticks_per_byte)."""
    return np.linalg.matrix_power(T, TICKS_PER_BYTE)


def noise_operator(seed_obj: Seed, rs: int) -> np.ndarray:
    """Matched-radius Ginibre noise, same construction as life.py."""
    rng = np.random.RandomState(rs)
    Z = (rng.randn(N_NODES_SEED, N_NODES_SEED)
         + 1j * rng.randn(N_NODES_SEED, N_NODES_SEED))
    Z *= seed_obj.lambda1_abs / max(np.abs(np.linalg.eigvals(Z)))
    return Z


def evolve(Tc: np.ndarray, chords: np.ndarray, byte_seq: np.ndarray,
           psi0: np.ndarray) -> np.ndarray:
    """Run the stream; return realified states (N_STEPS, 44)."""
    psi = psi0.astype(complex).copy()
    states = np.empty((len(byte_seq), 2 * N_NODES_SEED))
    for t, b in enumerate(byte_seq):
        inj = np.zeros(N_NODES_SEED, dtype=complex)
        inj[INJ_NODES] = chords[b]
        s = Tc @ (psi + inj)
        psi = s / np.linalg.norm(s)
        states[t, :N_NODES_SEED] = psi.real
        states[t, N_NODES_SEED:] = psi.imag
    return states


def probe_accuracy(states: np.ndarray, byte_seq: np.ndarray,
                   lag: int) -> float:
    """Held-out top-1 accuracy of a ridge probe state_t -> byte_{t-lag}."""
    t_idx = np.arange(BURN_IN + lag, len(states))
    X = states[t_idx]
    y = byte_seq[t_idx - lag]
    n = len(X)
    n_train = int(0.8 * n)
    Xtr, Xte = X[:n_train], X[n_train:]
    ytr, yte = y[:n_train], y[n_train:]
    # One-hot ridge regression, closed form
    Y = np.zeros((n_train, 256))
    Y[np.arange(n_train), ytr] = 1.0
    G = Xtr.T @ Xtr + RIDGE * np.eye(X.shape[1])
    W = np.linalg.solve(G, Xtr.T @ Y)
    pred = (Xte @ W).argmax(axis=1)
    return float((pred == yte).mean())


def spectrum_line(name: str, Tc: np.ndarray) -> str:
    sv = np.linalg.svd(Tc, compute_uv=False)
    return (f"  {name:14s} cycle singular values: max {sv.max():.4f}  "
            f"median {np.median(sv):.4f}  min {sv.min():.6f}")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    seed_obj = Seed()
    rng = np.random.RandomState(2026)
    chords = make_chords(seed_obj.alpha, rng)
    byte_seq = rng.randint(0, 256, size=N_STEPS + BURN_IN + max(LAGS))

    ops = {"live": cycle_operator(seed_obj.op.T)}
    for i, rs in enumerate([137, 138, 139]):
        ops[f"noise{i + 1}"] = cycle_operator(noise_operator(seed_obj, rs))
    # Control: conserving but structureless (random unitary at the same
    # spectral radius). Separates memory-from-conservation (generic)
    # from memory-from-the-derived-structure (specific).
    rngu = np.random.RandomState(555)
    Zu = (rngu.randn(N_NODES_SEED, N_NODES_SEED)
          + 1j * rngu.randn(N_NODES_SEED, N_NODES_SEED))
    Q, _ = np.linalg.qr(Zu)
    ops["unitary"] = cycle_operator(seed_obj.lambda1_abs * Q)

    print("Xorzo2 memory probe: byte identity recoverable from state, "
          "by lag (chance = 1/256 = 0.0039)")
    print(f"  stream {len(byte_seq):,} random bytes, ridge probe, "
          f"80/20 split, drive = alpha, no organs, no learning")
    for name, Tc in ops.items():
        print(spectrum_line(name, Tc))
    print()

    curves = {}
    for name, Tc in ops.items():
        psi0 = seed_obj.attractor
        states = evolve(Tc, chords, byte_seq, psi0)
        curves[name] = [probe_accuracy(states, byte_seq, k) for k in LAGS]

    hdr = "  lag(cycles) " + "".join(f"{k:>7d}" for k in LAGS)
    print(hdr)
    for name, accs in curves.items():
        print(f"  {name:12s}" + "".join(f"{a:>7.3f}" for a in accs))

    # Memory horizon: last lag with accuracy > 10x chance
    print()
    for name, accs in curves.items():
        horizon = 0
        for k, a in zip(LAGS, accs):
            if a > 10 * CHANCE:
                horizon = k
        print(f"  {name:12s} memory horizon (acc > 10x chance): "
              f"{horizon} cycles")


if __name__ == "__main__":
    main()
