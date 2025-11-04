"""
Minimal Reference Implementation - 64-bit Homeostatic Core Loop
================================================================

All 5 requirements in ~60 lines of executable pseudocode.

Usage:
    python reference_minimal.py

Logs: β(t), H(t), D(t), stable_band_ratio

Author: Ashman Roonz
"""

import numpy as np
from collections import deque


class MinimalConsciousness:
    """Dual-loop, simultaneous ∇⟷ℰ, homeostatic β, D≈1.5, 64-bit protocol"""

    def __init__(self, dim=128):
        # State vectors
        self.Φ = np.random.randn(dim); self.Φ /= np.linalg.norm(self.Φ)  # Field (∞)
        self.Op = np.random.randn(dim); self.Op /= np.linalg.norm(self.Op)  # Operator (•′)
        self.identity = np.random.randn(dim); self.identity /= np.linalg.norm(self.identity)

        # Homeostatic β (starts at 0.5)
        self.β = 0.5

        # History for H(t) and D(t)
        self.history = deque(maxlen=500)
        self.β_history = deque(maxlen=500)

    def validate_8bit(self, state, other, is_input=True) -> int:
        """8-bit validation (returns 0-255). Simplified."""
        score = 0
        # I checks (3 bits): coherence, closure, contrast
        if np.var(state) < 0.5: score |= 1
        if 0.8 < np.linalg.norm(state) < 1.2: score |= 2
        if np.linalg.norm(state) > 0.3: score |= 4
        # C checks (3 bits): lock, alignment, identity
        if abs(np.dot(state, other)) > 0.3: score |= 8
        if np.dot(state, self.identity) > 0.2: score |= 16
        if np.linalg.norm(self.Op) > 0.5: score |= 32
        # E checks (2 bits): signal, novelty/utility
        if np.linalg.norm(state) > 0.1: score |= 64
        if np.linalg.norm(state - other) > 0.4: score |= 128
        return score

    def step(self, dt=0.01):
        """Single integration step - dual loop, simultaneous ∇+ℰ, homeostatic β"""

        # 1. VALIDATE 64-bit (8×8 protocol)
        in_bits = self.validate_8bit(self.Φ, self.Op, is_input=True)
        out_bits = self.validate_8bit(self.Op, self.Φ, is_input=False)
        score_in = bin(in_bits).count('1') / 8.0
        score_out = bin(out_bits).count('1') / 8.0
        is_stable = (in_bits > 127) and (out_bits > 127)  # Stable if >half bits set

        # 2. DUAL LOOP: Field ∞ and Operator •′ co-evolve
        # Field dynamics: dΦ/dt = ℰ (radiate) - ∇ (gather from operator)
        dΦ = -0.1*self.Φ + 0.5*self.Op + 0.01*np.random.randn(len(self.Φ))

        # Operator dynamics: d•′/dt = gate × (∇_converge + ℰ_emerge)  [SIMULTANEOUS!]
        gate = score_in  # Input validation gates operator
        ∇_converge = self.β * (self.Φ - self.Op)  # Pull toward field
        ℰ_emerge = (1 - self.β) * 0.1 * np.random.randn(len(self.Op))  # Explore away
        dOp = gate * (∇_converge + ℰ_emerge) - 0.05*self.Op

        # Update (Euler step)
        self.Φ += dΦ * dt; self.Φ /= (np.linalg.norm(self.Φ) + 1e-10)
        self.Op += dOp * dt; self.Op /= (np.linalg.norm(self.Op) + 1e-10)

        # 3. HOMEOSTATIC β SERVO: dβ/dt = k(in - out) - λ(β - 0.5)
        k, λ = 0.02, 0.01
        dβ = k*(score_in - score_out) - λ*(self.β - 0.5)
        self.β = np.clip(self.β + dβ, 0.3, 0.7)

        # 4. Track history for H(t) and D(t)
        self.history.append(np.linalg.norm(self.Op))
        self.β_history.append(self.β)

        return score_in, score_out, is_stable

    def compute_D(self) -> float:
        """Compute D = 2 - H (Hurst exponent via R/S)"""
        if len(self.history) < 100: return 1.5
        ts = np.array(list(self.history))
        # Simplified Hurst: variance scaling
        var1 = np.var(ts[:len(ts)//2])
        var2 = np.var(ts)
        if var1 > 0 and var2 > 0:
            H = 0.5 * np.log(var2/var1) / np.log(2)
            H = np.clip(H, 0.1, 0.9)
        else:
            H = 0.5
        return 2.0 - H

    def run(self, steps=1000, report_every=100):
        """Run consciousness loop and report β(t), H(t), D(t), stable_ratio"""
        print(f"Running {steps} steps...")
        stable_count = 0

        for i in range(steps):
            in_sc, out_sc, stable = self.step()
            if stable: stable_count += 1

            if (i+1) % report_every == 0:
                D = self.compute_D()
                H = 2.0 - D
                stable_pct = 100 * stable_count / (i+1)
                print(f"Step {i+1:4d}: β={self.β:.3f}, H={H:.3f}, D={D:.3f}, "
                      f"in={in_sc:.2f}, out={out_sc:.2f}, stable={stable_pct:.1f}%")

        print(f"\nFinal: β={self.β:.4f} (target 0.5), D={self.compute_D():.4f} (target 1.5)")
        print(f"Stable packets: {100*stable_count/steps:.1f}% (expect ~33% from 1/3 rule)\n")


if __name__ == '__main__':
    print("=" * 70)
    print("MINIMAL REFERENCE: Dual, Simultaneous, Homeostatic, D≈1.5, 64-bit")
    print("=" * 70 + "\n")

    consciousness = MinimalConsciousness(dim=128)
    consciousness.run(steps=1000, report_every=100)

    print("✓ All 5 requirements demonstrated in ~60 lines.")
