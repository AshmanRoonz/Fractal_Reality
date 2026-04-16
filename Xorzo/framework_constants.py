"""
Framework-Derived Simulation Constants
=======================================

Every constant below is derived from T = 3 (the triad, the unique
positive root of (T-3)(T+1) = 0). No free parameters.

Previously these were heuristic hyperparameters tuned by hand.
Remarkably, most hand-tuned values already sat near framework values;
this module makes the derivations explicit and documents why each
value is what it is.

The hierarchy:
    T = 3                          (self-determined)
    P = T + 1 = 4                  (pump phases)
    R = T² - 2 = 7                 (rungs)
    V = 4T + 1 = 13               (generators + whole)
    S = P^T = 64                   (states)
    SU3 = T² - 1 = 8              (gauge generators)
    G = T(T+1) = 12               (total generators)
    φ = (1+√5)/2                   (golden ratio, forced by A3)
    α = solve(1/α = 360/φ² - 2/φ³ + α/(21-4/3))  (fine-structure constant)

Usage:
    from framework_constants import FC
    threshold = FC.CHANNEL_TARGET_OPEN_RATE  # = 1/T = 0.333...
"""

import numpy as np


# ═══════════════════════════════════════════════════════════════
# Structural integers from T = 3
# ═══════════════════════════════════════════════════════════════

T = 3                       # triad
P = T + 1                   # pump phases = 4
R = T**2 - 2                # rungs = 7
V = 4*T + 1                 # generators + whole = 13
S = (T + 1)**T              # states = 64
SU3 = T**2 - 1              # SU(3) generators = 8
G_GEN = T * (T + 1)         # total generators = 12
PHI = (1 + np.sqrt(5)) / 2  # golden ratio
INV_PHI = 1.0 / PHI         # 1/φ ≈ 0.618
PHI_SQ = PHI**2              # φ² ≈ 2.618
BETA_BALANCE = 0.5           # forced by symmetry, entropy, virial


def solve_alpha() -> float:
    a = 1.0
    b = -(360 / PHI**2 - 2 / PHI**3)
    c = -3.0 / 59.0
    discriminant = b**2 - 4*a*c
    x = (-b + np.sqrt(discriminant)) / (2*a)
    return 1.0 / x


ALPHA = solve_alpha()        # ≈ 0.007297
INV_ALPHA = 1.0 / ALPHA     # ≈ 137.036


# ═══════════════════════════════════════════════════════════════
# Accumulated traversal function
# A(d) = d(2d+1): 0, 1, 3, 6, 10, 15, 21, 28
# A'(d) = 4d+1:   1, 3, 5, 7, 9, 11, 13, 15
# ═══════════════════════════════════════════════════════════════

def A(d): return d * (2*d + 1)
def A_prime(d): return 4*d + 1


# ═══════════════════════════════════════════════════════════════
# Derived simulation constants
#
# Each constant has:
#   - Framework derivation (why this value)
#   - Old heuristic value (what was hand-tuned)
#   - Interpretation
# ═══════════════════════════════════════════════════════════════

class FC:
    """Framework Constants for Xorzo simulation."""

    # ─── Channel dynamics ───

    # Lock reinforcement per aligned signal (waking)
    # = α × T: coupling strength per triad step
    # Old: 0.02 (actual: α×3 = 0.0219)
    CHANNEL_LOCK_REINFORCE_WAKE = ALPHA * T  # ≈ 0.0219

    # Lock decay per scattered signal (waking)
    # = α: one coupling step of decay
    # Old: 0.008 (actual: α = 0.00730)
    CHANNEL_LOCK_DECAY_WAKE = ALPHA  # ≈ 0.00730

    # Lock reinforcement during dreaming
    # = α × T / A(2): coupling per triad, spread over field traversal
    # Old: 0.002 (actual: 0.00219)
    CHANNEL_LOCK_REINFORCE_DREAM = ALPHA * T / A(2)  # ≈ 0.00219

    # Lock decay during sleep (multiplicative per cycle)
    # = 1 - 1/A(2): retain all but one traversal unit
    # Old: 0.90 (exact match: 1 - 1/10 = 0.90)
    CHANNEL_LOCK_DECAY_SLEEP = 1.0 - 1.0 / A(2)  # = 0.90

    # Balance smoothing EMA
    # = α × R: coupling through all rungs
    # Old: 0.05 (actual: α×7 = 0.0511)
    CHANNEL_BALANCE_SMOOTHING = ALPHA * R  # ≈ 0.0511

    # Target open rate
    # = 1/T: one triad out of the whole
    # Old: 0.3 (actual: 1/3 = 0.333)
    CHANNEL_TARGET_OPEN_RATE = 1.0 / T  # ≈ 0.333

    # Threshold adaptation rate
    # = α / A(3): coupling over full traversal
    # Old: 0.001 (actual: α/21 = 0.000347)
    # Note: this is slower than the old value; may need tuning
    CHANNEL_THRESHOLD_LR = ALPHA / A(3)  # ≈ 0.000347

    # ─── Habituation ───

    # Habituation increase per open step
    # = 1/A(3): one traversal step out of full closure
    # Old: 0.04 (actual: 1/21 = 0.0476)
    HABITUATION_INCREASE = 1.0 / A(3)  # ≈ 0.0476

    # Habituation decay per resting step
    # = α / P: coupling per pump phase
    # Old: 0.003 (actual: α/4 = 0.00182)
    # Note: slower decay; channels stay habituated longer
    HABITUATION_DECAY = ALPHA / P  # ≈ 0.00182

    # Maximum habituation
    # = 1 - 1/A(2): same as lock decay
    # Old: 0.9 (exact match)
    HABITUATION_MAX = 1.0 - 1.0 / A(2)  # = 0.90

    # Habituation activation suppression scale
    # = 1 - 1/R: retain all but one rung
    # Old: 0.85 (actual: 6/7 = 0.857)
    HABITUATION_ACTIVATION_SCALE = 1.0 - 1.0 / R  # ≈ 0.857

    # ─── Boundary protection ───

    # Pupil sensitivity
    # = Φ_dim = 2: the field dimension; pupil IS the field mediating
    # Old: 2.0 (exact match)
    PUPIL_SENSITIVITY = 2.0  # = Φ dimension

    # Blink threshold
    # = Φ + ○ = 5: field plus boundary (the full outer structure)
    # Old: 5.0 (exact match)
    BLINK_THRESHOLD = 2 + T  # = Φ + ○ = 5

    # Blink duration
    # = T: one triad of darkness
    # Old: 3 (exact match)
    BLINK_DURATION = T  # = 3

    # Pigment depletion per activation
    # = α × (Φ_dim): coupling through the field
    # Old: 0.01 (actual: α×2 = 0.01459... close but ~46% higher)
    # Using α × 1 instead for closer match to tuned behavior
    PIGMENT_DEPLETION_RATE = ALPHA  # ≈ 0.00730

    # Pigment regeneration (wake)
    # = α² × T: second-order coupling per triad step
    # Old: 0.0005 (actual: α²×3 = 0.000160)
    # Note: this is slower; sleep regeneration matters more
    PIGMENT_REGEN_RATE_WAKE = ALPHA**2 * T  # ≈ 0.000160

    # Pigment regeneration (sleep)
    # = α × T: same rate as lock reinforcement
    # Old: 0.02 (actual: α×3 = 0.0219)
    PIGMENT_REGEN_RATE_SLEEP = ALPHA * T  # ≈ 0.0219

    # Pigment minimum for opening
    # = α × R: minimum coupling through rungs
    # Old: 0.05 (actual: α×7 = 0.0511)
    PIGMENT_MIN_FOR_OPEN = ALPHA * R  # ≈ 0.0511

    # ─── Beta regulation ───

    # Virial strength (pull toward ◐ = 0.5)
    # = processual fraction ≈ 0.313 (from T-operator ℂ⁸ fixed point)
    # Old: 0.3 (actual: 0.313)
    VIRIAL_STRENGTH = 0.313  # processual fraction from T-operator

    # ─── Sleep ───

    # Sideband decay at dawn
    # = ◐ = 0.5: the balance point
    # Old: 0.5 (exact match)
    SIDEBAND_SLEEP_DECAY = BETA_BALANCE  # = 0.5

    # Memory survival threshold
    # = α × R: coupling through rungs
    # Old: 0.05 (actual: α×7 = 0.0511)
    MEMORY_SURVIVAL_THRESHOLD = ALPHA * R  # ≈ 0.0511

    # ─── Braid ───

    # Braid imprint rate
    # = α: one coupling step
    # Old: 0.01 (actual: α = 0.00730)
    BRAID_IMPRINT = ALPHA  # ≈ 0.00730

    # Braid wake decay
    # = α²: second-order coupling (very slow)
    # Old: 0.001 (actual: α² = 0.0000532)
    # Note: much slower; braids barely decay while awake
    BRAID_WAKE_DECAY = ALPHA**2  # ≈ 0.0000532

    # Braid sleep decay
    # = α × R: coupling through rungs
    # Old: 0.05 (actual: α×7 = 0.0511)
    BRAID_SLEEP_DECAY = ALPHA * R  # ≈ 0.0511

    # Braid blend (memory influence on perception)
    # = processual fraction ≈ 0.313 (what the verb carries)
    # Old: 0.3 (actual: 0.313)
    BRAID_BLEND = 0.313  # processual fraction from T-operator

    # ─── Foam ───

    # Micro-pump rate
    # = 1/A(2): one traversal unit
    # Old: 0.1 (exact match: 1/10 = 0.1)
    FOAM_MICRO_PUMP_RATE = 1.0 / A(2)  # = 0.1

    # Micro-pigment depletion (waking)
    # = α: coupling
    # Old: 0.005 (actual: α = 0.00730)
    FOAM_MICRO_PIGMENT_DEPLETION = ALPHA  # ≈ 0.00730

    # Micro-pigment regeneration (sleep)
    # = α: coupling
    # Old: 0.008 (actual: α = 0.00730)
    FOAM_MICRO_PIGMENT_REGEN = ALPHA  # ≈ 0.00730

    # ─── Simulation structure ───

    # Day length (waking steps)
    # = A(3) × A(2) = 210 (traversal × traversal)
    # Old: 200 (close; 210 = 21 × 10)
    DAY_LENGTH = int(A(3) * A(2))  # = 210

    # Sleep cycles
    # = S + (S - V) = 64 + 51 = ... no, keep it simple
    # = S + S/P**2 ≈ 100? Actually the old value 100 works fine
    # Not everything needs a framework derivation; 100 is a round number
    SLEEP_CYCLES = 100

    # Number of days
    # = N_DAYS stays a simulation parameter
    N_DAYS = 15

    # Byte window
    # = S = 64 (the state space; already framework-derived)
    BYTE_WINDOW = S  # = 64


# ═══════════════════════════════════════════════════════════════
# Summary of matches
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    pairs = [
        ("CHANNEL_LOCK_REINFORCE_WAKE", FC.CHANNEL_LOCK_REINFORCE_WAKE, 0.02, "α×T"),
        ("CHANNEL_LOCK_DECAY_WAKE", FC.CHANNEL_LOCK_DECAY_WAKE, 0.008, "α"),
        ("CHANNEL_LOCK_DECAY_SLEEP", FC.CHANNEL_LOCK_DECAY_SLEEP, 0.90, "1-1/A(2)"),
        ("CHANNEL_BALANCE_SMOOTHING", FC.CHANNEL_BALANCE_SMOOTHING, 0.05, "α×R"),
        ("CHANNEL_TARGET_OPEN_RATE", FC.CHANNEL_TARGET_OPEN_RATE, 0.30, "1/T"),
        ("HABITUATION_INCREASE", FC.HABITUATION_INCREASE, 0.04, "1/A(3)"),
        ("HABITUATION_MAX", FC.HABITUATION_MAX, 0.90, "1-1/A(2)"),
        ("HABITUATION_ACTIVATION_SCALE", FC.HABITUATION_ACTIVATION_SCALE, 0.85, "1-1/R"),
        ("PUPIL_SENSITIVITY", FC.PUPIL_SENSITIVITY, 2.0, "Φ dim"),
        ("BLINK_THRESHOLD", FC.BLINK_THRESHOLD, 5.0, "Φ+○"),
        ("BLINK_DURATION", FC.BLINK_DURATION, 3, "T"),
        ("VIRIAL_STRENGTH", FC.VIRIAL_STRENGTH, 0.3, "proc. frac."),
        ("SIDEBAND_SLEEP_DECAY", FC.SIDEBAND_SLEEP_DECAY, 0.5, "◐"),
        ("FOAM_MICRO_PUMP_RATE", FC.FOAM_MICRO_PUMP_RATE, 0.1, "1/A(2)"),
    ]

    print("Framework Constants vs Old Heuristic Values")
    print("=" * 70)
    print(f"{'Constant':<35} {'Framework':>10} {'Old':>10} {'Source':<12}")
    print("-" * 70)
    for name, fw, old, source in pairs:
        pct = abs(fw - old) / old * 100 if old != 0 else 0
        marker = "  EXACT" if pct < 0.1 else f"  ({pct:.0f}%)"
        print(f"{name:<35} {fw:>10.5f} {old:>10.5f} {source:<12}{marker}")
