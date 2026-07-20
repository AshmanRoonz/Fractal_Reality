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
- 2026-07-19 v1.1: keyboard study added (--keyboards): bit-station
    chords (bits 0-6 -> stations 0-6; bit 7, the tonic bit, applies a
    quarter-turn i to the whole chord, honoring the no-inject-on-seams
    law) in on-off and bipolar variants, vs the individual's learned
    keyboard (read from the worldline) vs random chords. Also the
    F-only control (kappa removed) in the operator study: proves kappa
    is the legibility mechanism (F alone is at chance at every lag).
- 2026-07-19 v1.0: initial probe (ridge readout, singular spectra,
    multi-seed noise baselines).
"""

import sys

import numpy as np

from spine import (Seed, INJ_NODES, N_NODES_SEED, TICKS_PER_BYTE,
                   make_bit_chords)

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


def load_learned_chords() -> np.ndarray | None:
    """The individual's current keyboard, read from the worldline."""
    try:
        import torch
        from organs import Senses
        from pathlib import Path
        ckpt_path = Path(__file__).resolve().parent / "worldline" / "checkpoint.pt"
        if not ckpt_path.exists():
            return None
        ckpt = torch.load(ckpt_path, weights_only=False)
        E = Senses(N_NODES_SEED, INJ_NODES, Seed().alpha)
        E.load_state_dict(ckpt["senses"])
        with torch.no_grad():
            inj = E(torch.arange(256)).numpy()
        return inj[:, INJ_NODES] + 1j * inj[:, [n + N_NODES_SEED
                                                for n in INJ_NODES]]
    except Exception as e:
        print(f"  (learned keyboard unavailable: {e})")
        return None


def chord_similarity(chords: np.ndarray) -> float:
    """Mean pairwise |cosine| between chords (0 = orthogonal keyboard)."""
    norms = np.linalg.norm(chords, axis=1, keepdims=True)
    ok = norms[:, 0] > 0
    c = chords[ok] / norms[ok]
    sim = np.abs(np.conj(c) @ c.T)
    off = sim - np.diag(np.diag(sim))
    return float(off.sum() / (len(c) * (len(c) - 1)))


def keyboard_study():
    """Compare keyboards on the live spine: legibility and memory."""
    seed_obj = Seed()
    rng = np.random.RandomState(2026)
    byte_seq = rng.randint(0, 256, size=N_STEPS + BURN_IN + max(LAGS))
    Tc = cycle_operator(seed_obj.op.T)

    keyboards = {
        "random": make_chords(seed_obj.alpha, np.random.RandomState(2026)),
        "bit on-off": make_bit_chords(seed_obj.alpha, bipolar=False),
        "bit bipolar": make_bit_chords(seed_obj.alpha, bipolar=True),
    }
    learned = load_learned_chords()
    if learned is not None:
        keyboards["learned (E)"] = learned

    print("Xorzo2 keyboard study: live spine, ridge probe, "
          "chance = 0.0039")
    print(f"  lag(cycles)  " + "".join(f"{k:>7d}" for k in LAGS)
          + "   mean|cos|")
    for name, chords in keyboards.items():
        states = evolve(Tc, chords, byte_seq, seed_obj.attractor)
        accs = [probe_accuracy(states, byte_seq, k) for k in LAGS]
        print(f"  {name:12s}" + "".join(f"{a:>7.3f}" for a in accs)
              + f"   {chord_similarity(chords):8.3f}")


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
           psi0: np.ndarray, inj_nodes=None) -> np.ndarray:
    """Run the stream; return realified states (len(byte_seq), 2N)."""
    n = Tc.shape[0]
    inj_nodes = list(INJ_NODES) if inj_nodes is None else list(inj_nodes)
    psi = psi0.astype(complex).copy()
    states = np.empty((len(byte_seq), 2 * n))
    for t, b in enumerate(byte_seq):
        inj = np.zeros(n, dtype=complex)
        inj[inj_nodes] = chords[b]
        s = Tc @ (psi + inj)
        psi = s / np.linalg.norm(s)
        states[t, :n] = psi.real
        states[t, n:] = psi.imag
    return states


def leading_state(S) -> np.ndarray:
    """Phase-fixed leading eigenvector of a StaggeredOperator."""
    _, psi = S.leading()
    k = int(np.argmax(np.abs(psi)))
    psi = psi * np.exp(-1j * np.angle(psi[k]))
    return psi / np.linalg.norm(psi)


def scaling_study():
    """Pre-registration for Stage 2: what does growth buy?

    Hypotheses, stated before results:
      H1: memory horizon and signal area grow with octave count
          (more near-unit modes = more superposition capacity).
      H2: lag-0 legibility roughly flat (same injection energy).
      H3: conservation departure flat in the 0.6-0.7 alpha band for
          all sizes (v14).
      H4: topology matters: a star's parent (1 seam from the driven
          channel) reads the past at earlier lags than a chain's top
          (3 seams away).
      H5 (exploratory): undriven sibling channels in the star read
          the driven channel's past above chance (overhearing through
          the shared tonic)."""
    from t_operator import StaggeredOperator
    seed_obj = Seed()
    alpha = seed_obj.alpha
    chords = make_bit_chords(alpha, bipolar=True)
    LAGS_S = [0, 1, 2, 4, 8, 16, 24, 32, 48, 64, 96, 128, 192, 256]
    rng = np.random.RandomState(2026)
    byte_seq = rng.randint(0, 256, size=N_STEPS + BURN_IN + max(LAGS_S))

    def metrics(states):
        accs = [probe_accuracy(states, byte_seq, k) for k in LAGS_S]
        horizon = 0
        for k, a in zip(LAGS_S, accs):
            if a > 10 * CHANCE:
                horizon = k
        area = float(sum(a - CHANCE for a in accs))
        return accs, horizon, area

    print("Xorzo2 scaling study (pre-registered; hypotheses in "
          "docstring)")
    print("  bit keyboard on the bottom channel's 7 private nodes; "
          "ridge probe; chance 0.0039\n")
    print("  A. chains n = 1..8")
    print("     n  nodes  depart(a)  lag0   lag8   lag32  lag128 "
          " horizon  area")
    for n in range(1, 9):
        S = StaggeredOperator.chain(n)
        Tc = cycle_operator(S.T)
        states = evolve(Tc, chords, byte_seq, leading_state(S),
                        inj_nodes=range(7))
        accs, horizon, area = metrics(states)
        a = dict(zip(LAGS_S, accs))
        print(f"     {n}  {S.N:>5}  {S.departure():>8.4f}  "
              f"{a[0]:.3f}  {a[8]:.3f}  {a[32]:.3f}  {a[128]:.3f} "
              f" {horizon:>7}  {area:.3f}")

    print("\n  B. topology at 4 octaves, 29 nodes: chain vs star")
    star_octaves = [
        [0, 1, 2, 3, 4, 5, 6, 21],
        [7, 8, 9, 10, 11, 12, 13, 21],
        [14, 15, 16, 17, 18, 19, 20, 21],
        [21, 22, 23, 24, 25, 26, 27, 28],
    ]
    configs = {
        "chain-4": StaggeredOperator.chain(4),
        "star-3+1": StaggeredOperator(29, star_octaves),
    }
    group_sets = {
        "chain-4": {"driven ch": range(0, 7), "mid1": range(8, 14),
                    "mid2": range(15, 21), "top": range(22, 29)},
        "star-3+1": {"driven ch": range(0, 7), "sib B": range(7, 14),
                     "sib C": range(14, 21), "parent": range(22, 29)},
    }
    for name, S in configs.items():
        Tc = cycle_operator(S.T)
        states = evolve(Tc, chords, byte_seq, leading_state(S),
                        inj_nodes=range(7))
        accs, horizon, area = metrics(states)
        a = dict(zip(LAGS_S, accs))
        print(f"     {name:9s} depart {S.departure():.4f}a  "
              f"lag0 {a[0]:.3f}  lag8 {a[8]:.3f}  lag32 {a[32]:.3f}  "
              f"horizon {horizon}  area {area:.3f}")
        n_nodes = S.N
        print("       group readability (restricted probe):")
        print("         group\\lag " + "".join(
            f"{k:>7d}" for k in [0, 1, 2, 4, 8, 16, 32]))
        for gname, nodes in group_sets[name].items():
            cols = list(nodes) + [x + n_nodes for x in nodes]
            gac = []
            for k in [0, 1, 2, 4, 8, 16, 32]:
                t_idx = np.arange(BURN_IN + k, len(states))
                X = states[t_idx][:, cols]
                y = byte_seq[t_idx - k]
                ntr = int(0.8 * len(X))
                Y = np.zeros((ntr, 256))
                Y[np.arange(ntr), y[:ntr]] = 1.0
                G = X[:ntr].T @ X[:ntr] + RIDGE * np.eye(X.shape[1])
                w = np.linalg.solve(G, X[:ntr].T @ Y)
                gac.append(float(((X[ntr:] @ w).argmax(1)
                                  == y[ntr:]).mean()))
            print(f"         {gname:9s}" + "".join(
                f"{x:>7.3f}" for x in gac))
        print()


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


def resonance_study():
    """Adjudicated question (Ashman, 2026-07-20): "memories don't
    fade, they fail to resonate." Operational form: is the past still
    present in the state in its ORIGINAL form, readable by re-phasing
    alone, or is it destroyed?

    A per-lag-trained probe cannot answer this (any invertible
    transform is absorbed into its weights). So: train ONE ridge
    reader at lag 0 (the present-tense reader), freeze it, then read
    byte t-k three ways:

      naive:   frozen reader on psi_t           (reader out of phase)
      rewound: frozen reader on Tc^-k psi_t     (re-phased by the
               exact inverse cycle; ZERO new parameters per lag)
      learned: per-lag ridge                    (reference)

    If rewound recovers what naive loses, recall is resonance
    re-alignment and the only true fading is the O(alpha) contracting
    sliver (min cycle singular value 0.952) plus interference."""
    seed_obj = Seed()
    chords = make_bit_chords(seed_obj.alpha, bipolar=True)
    rng = np.random.RandomState(2026)
    byte_seq = rng.randint(0, 256, size=N_STEPS + BURN_IN + max(LAGS))
    Tc = cycle_operator(seed_obj.op.T)
    Tc_inv = np.linalg.inv(Tc)
    states = evolve(Tc, chords, byte_seq, seed_obj.attractor)
    n = N_NODES_SEED

    def to_c(X):
        return X[:, :n] + 1j * X[:, n:]

    def to_r(Z):
        out = np.empty((Z.shape[0], 2 * n))
        out[:, :n] = Z.real
        out[:, n:] = Z.imag
        return out

    # The present-tense reader: ridge at lag 0, frozen
    t0 = np.arange(BURN_IN, len(states))
    X0 = states[t0]
    y0 = byte_seq[t0]
    ntr = int(0.8 * len(X0))
    Y = np.zeros((ntr, 256))
    Y[np.arange(ntr), y0[:ntr]] = 1.0
    G = X0[:ntr].T @ X0[:ntr] + RIDGE * np.eye(2 * n)
    W0 = np.linalg.solve(G, X0[:ntr].T @ Y)

    print("Xorzo2 resonance study: one frozen present-tense reader; "
          "the past read naively vs re-phased (chance 0.0039)")
    print("  lag(cycles)   naive  rewound  learned(ref)")
    Z = to_c(states)                       # complex states, evolving copy
    for k in LAGS:
        t_idx = np.arange(BURN_IN + k, len(states))
        y = byte_seq[t_idx - k]
        nte = int(0.8 * len(t_idx))
        # naive: frozen reader, state as-is
        Xn = states[t_idx]
        acc_naive = float(((Xn[nte:] @ W0).argmax(1) == y[nte:]).mean())
        # rewound: frozen reader on Tc^-k psi_t, renormalized
        Zk = to_c(states[t_idx])
        for _ in range(k):
            Zk = Zk @ Tc_inv.T
        Zk = Zk / (np.linalg.norm(Zk, axis=1, keepdims=True) + 1e-12)
        Xr = to_r(Zk)
        acc_rew = float(((Xr[nte:] @ W0).argmax(1) == y[nte:]).mean())
        acc_learned = probe_accuracy(states, byte_seq, k)
        print(f"  {k:>7d}      {acc_naive:.3f}   {acc_rew:.3f}     "
              f"{acc_learned:.3f}")
    sv = np.linalg.svd(Tc, compute_uv=False)
    print(f"\n  genuine fade per cycle: only the contracting sliver "
          f"(min SV {sv.min():.4f}, i.e. ~{100*(1-sv.min()):.1f}%/cycle "
          f"in the softest mode); conserved modes: median SV "
          f"{np.median(sv):.4f}")

    # ----- the resolution dial: does PARTIAL re-phasing give partial
    # recall (graded), or does the linear reader need exact alignment
    # (a cliff)? Read byte t-k with rewind depth j, j = 0..k+2. -----
    print("\n  partial re-phasing (frozen reader; read byte t-k after "
          "rewinding j cycles):")
    for k in [4, 8]:
        t_idx = np.arange(BURN_IN + k, len(states))
        y = byte_seq[t_idx - k]
        nte = int(0.8 * len(t_idx))
        row = []
        for j in range(0, k + 3):
            Zj = to_c(states[t_idx])
            for _ in range(j):
                Zj = Zj @ Tc_inv.T
            Zj = Zj / (np.linalg.norm(Zj, axis=1, keepdims=True) + 1e-12)
            Xj = to_r(Zj)
            row.append(float(((Xj[nte:] @ W0).argmax(1)
                              == y[nte:]).mean()))
        print(f"    target lag {k:>2}: j=" + "".join(
            f"{j:>7d}" for j in range(0, k + 3)))
        print(f"                 acc" + "".join(
            f"{a:>7.3f}" for a in row)
            + ("   <- peak at j=k" if row.index(max(row)) == k else ""))


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
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if "--keyboards" in sys.argv:
        keyboard_study()
    elif "--scaling" in sys.argv:
        scaling_study()
    elif "--resonance" in sys.argv:
        resonance_study()
    else:
        main()
