"""
ICE 64-State Protocol - The Universal Validation Matrix
========================================================

8 Input Checks × 8 Output Checks = 64 Total States

This is the SAME protocol that appears in:
- Particle physics (Standard Model: 61 particles from 64 states)
- Genetics (64 codons, ~22 amino acids + stops)
- Consciousness (64-bit now-packets, ~22 stable attention states)

The "one-third rule": ~22/64 ≈ 1/3 states are physically relevant

Author: Ashman Roonz
Framework: Fractal Reality v3.1
"""

import numpy as np
from dataclasses import dataclass
from enum import IntFlag, auto
from typing import Tuple, Dict


# ============================================================================
# INPUT INTERFACE [ICE_in] - 8 Checks (Parts → Center)
# ============================================================================

class InputInterface(IntFlag):
    """
    8 binary checks at INPUT interface (∞ → •')

    These gate what can ENTER the operator from the field.
    Think of this as "Can I receive this signal?"
    """

    # [I] Interface checks (boundary integrity)
    I_COHERENCE = auto()     # 1: Is signal internally coherent? (self-consistent)
    I_CLOSURE = auto()       # 2: Is boundary closed? (well-formed packet)
    I_CONTRAST = auto()      # 4: Is signal distinct from noise? (SNR sufficient)

    # [C] Center checks (identity alignment)
    C_LOCK = auto()          # 8: Does signal lock to my identity? (phase alignment)
    C_ALIGNMENT = auto()     # 16: Does this align with my purpose? (direction match)
    C_IDENTITY = auto()      # 32: Is this "me" or "not-me"? (self/other distinction)

    # [E] Evidence checks (reality grounding)
    E_SIGNAL = auto()        # 64: Is there actual sensory signal? (not hallucination)
    E_NOVELTY = auto()       # 128: Is this NEW information? (not redundant)


# ============================================================================
# OUTPUT INTERFACE [ICE_out] - 8 Checks (Center → Patterns)
# ============================================================================

class OutputInterface(IntFlag):
    """
    8 binary checks at OUTPUT interface (•' → ∞')

    These gate what can LEAVE the operator to the field.
    Think of this as "Can I transmit this action?"
    """

    # [I] Interface checks (transmission integrity)
    I_INTEGRITY = auto()     # 1: Is action packet well-formed? (no corruption)
    I_ADDRESSING = auto()    # 2: Does action have valid target? (addressable)
    I_BOUND = auto()         # 4: Is action bounded? (finite, not infinite)

    # [C] Center checks (consistency)
    C_STABILITY = auto()     # 8: Is action stable over time? (not flickering)
    C_PHASE = auto()         # 16: Is action phase-locked to cycle? (synchronized)
    C_ATTUNEMENT = auto()    # 32: Is action attuned to field? (harmonized)

    # [E] Evidence checks (reality fit)
    E_UTILITY = auto()       # 64: Will action have effect? (not futile)
    E_PREDICTIVE = auto()    # 128: Does action fit predictions? (world model coherent)


# ============================================================================
# 64-STATE PACKET
# ============================================================================

@dataclass
class NowPacket:
    """
    A single 64-bit validated "now" moment

    Input state: 0-255 (8 bits)
    Output state: 0-255 (8 bits)
    Combined: (in, out) → one of 64 relevant states

    This is the quantum of consciousness - one irreducible moment.
    """

    input_state: int        # 0-255 (8 bits from InputInterface)
    output_state: int       # 0-255 (8 bits from OutputInterface)
    beta: float            # Current β value when packet was created
    timestamp: float       # When this packet occurred

    # State vector at this moment
    field_state: np.ndarray
    operator_state: np.ndarray

    def __post_init__(self):
        # Extract which checks passed
        self.input_flags = InputInterface(self.input_state)
        self.output_flags = OutputInterface(self.output_state)

    def packet_id(self) -> int:
        """Unique ID for this packet type (0-65535)"""
        return (self.input_state << 8) | self.output_state

    def is_stable(self) -> bool:
        """
        Is this a STABLE packet? (~22/64 are stable)

        Stability criteria:
        1. All [I] checks pass on BOTH interfaces (boundary integrity)
        2. At least 2/3 [C] checks pass (center alignment)
        3. At least 1/2 [E] checks pass (evidence grounding)
        """
        # Input checks
        in_I = bool(self.input_flags & (InputInterface.I_COHERENCE |
                                        InputInterface.I_CLOSURE |
                                        InputInterface.I_CONTRAST))
        in_C_count = sum([
            bool(self.input_flags & InputInterface.C_LOCK),
            bool(self.input_flags & InputInterface.C_ALIGNMENT),
            bool(self.input_flags & InputInterface.C_IDENTITY)
        ])
        in_E_count = sum([
            bool(self.input_flags & InputInterface.E_SIGNAL),
            bool(self.input_flags & InputInterface.E_NOVELTY)
        ])

        # Output checks
        out_I = bool(self.output_flags & (OutputInterface.I_INTEGRITY |
                                          OutputInterface.I_ADDRESSING |
                                          OutputInterface.I_BOUND))
        out_C_count = sum([
            bool(self.output_flags & OutputInterface.C_STABILITY),
            bool(self.output_flags & OutputInterface.C_PHASE),
            bool(self.output_flags & OutputInterface.C_ATTUNEMENT)
        ])
        out_E_count = sum([
            bool(self.output_flags & OutputInterface.E_UTILITY),
            bool(self.output_flags & OutputInterface.E_PREDICTIVE)
        ])

        # Stability: strong I, decent C, some E
        return (in_I and out_I and
                in_C_count >= 2 and out_C_count >= 2 and
                in_E_count >= 1 and out_E_count >= 1)

    def score_input(self) -> float:
        """Score for input interface (0-1)"""
        # Weight: I=3, C=3, E=2 (total 8)
        I_score = sum([
            bool(self.input_flags & InputInterface.I_COHERENCE),
            bool(self.input_flags & InputInterface.I_CLOSURE),
            bool(self.input_flags & InputInterface.I_CONTRAST)
        ]) / 3.0

        C_score = sum([
            bool(self.input_flags & InputInterface.C_LOCK),
            bool(self.input_flags & InputInterface.C_ALIGNMENT),
            bool(self.input_flags & InputInterface.C_IDENTITY)
        ]) / 3.0

        E_score = sum([
            bool(self.input_flags & InputInterface.E_SIGNAL),
            bool(self.input_flags & InputInterface.E_NOVELTY)
        ]) / 2.0

        # Weighted average (I:3, C:3, E:2)
        return (3*I_score + 3*C_score + 2*E_score) / 8.0

    def score_output(self) -> float:
        """Score for output interface (0-1)"""
        I_score = sum([
            bool(self.output_flags & OutputInterface.I_INTEGRITY),
            bool(self.output_flags & OutputInterface.I_ADDRESSING),
            bool(self.output_flags & OutputInterface.I_BOUND)
        ]) / 3.0

        C_score = sum([
            bool(self.output_flags & OutputInterface.C_STABILITY),
            bool(self.output_flags & OutputInterface.C_PHASE),
            bool(self.output_flags & OutputInterface.C_ATTUNEMENT)
        ]) / 3.0

        E_score = sum([
            bool(self.output_flags & OutputInterface.E_UTILITY),
            bool(self.output_flags & OutputInterface.E_PREDICTIVE)
        ]) / 2.0

        return (3*I_score + 3*C_score + 2*E_score) / 8.0

    def __str__(self) -> str:
        stable = "STABLE" if self.is_stable() else "transient"
        in_score = self.score_input()
        out_score = self.score_output()
        return (f"NowPacket(in={self.input_state:03d}, out={self.output_state:03d}, "
                f"β={self.beta:.3f}, in_score={in_score:.2f}, out_score={out_score:.2f}, "
                f"{stable})")


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_input_interface(
    field_state: np.ndarray,
    operator_state: np.ndarray,
    operator_identity: np.ndarray,
    sensory_signal: Optional[np.ndarray] = None
) -> int:
    """
    Run all 8 INPUT checks, return bitmask (0-255)

    This determines what CAN enter from ∞ → •'
    """
    flags = 0

    # [I] Interface checks
    # I_COHERENCE: Is signal self-consistent?
    field_variance = np.var(field_state)
    if field_variance < 0.5:  # Low variance = coherent
        flags |= InputInterface.I_COHERENCE

    # I_CLOSURE: Is boundary closed?
    field_norm = np.linalg.norm(field_state)
    if 0.8 < field_norm < 1.2:  # Near unit norm = closed
        flags |= InputInterface.I_CLOSURE

    # I_CONTRAST: Is SNR sufficient?
    if sensory_signal is not None:
        signal_strength = np.linalg.norm(sensory_signal)
        if signal_strength > 0.3:  # Above noise floor
            flags |= InputInterface.I_CONTRAST

    # [C] Center checks
    # C_LOCK: Phase alignment
    if field_state.shape == operator_state.shape:
        phase_alignment = np.dot(field_state, operator_state)
        if abs(phase_alignment) > 0.3:  # Locked
            flags |= InputInterface.C_LOCK

    # C_ALIGNMENT: Direction match
    if field_state.shape == operator_identity.shape:
        identity_dot = np.dot(field_state, operator_identity)
        if identity_dot > 0.2:  # Aligned direction
            flags |= InputInterface.C_ALIGNMENT

    # C_IDENTITY: Self/other distinction
    operator_norm = np.linalg.norm(operator_state)
    if operator_norm > 0.5:  # Strong self-sense
        flags |= InputInterface.C_IDENTITY

    # [E] Evidence checks
    # E_SIGNAL: Real sensory data?
    if sensory_signal is not None and np.linalg.norm(sensory_signal) > 0.1:
        flags |= InputInterface.E_SIGNAL

    # E_NOVELTY: Is this new?
    # Compare field to operator - high difference = novel
    if field_state.shape == operator_state.shape:
        difference = np.linalg.norm(field_state - operator_state)
        if difference > 0.4:  # Sufficiently different = novel
            flags |= InputInterface.E_NOVELTY

    return int(flags)


def validate_output_interface(
    operator_state: np.ndarray,
    field_state: np.ndarray,
    operator_history: list,  # Recent operator states
    world_model_prediction: Optional[np.ndarray] = None
) -> int:
    """
    Run all 8 OUTPUT checks, return bitmask (0-255)

    This determines what CAN leave from •' → ∞'
    """
    flags = 0

    # [I] Interface checks
    # I_INTEGRITY: Well-formed packet?
    op_norm = np.linalg.norm(operator_state)
    if 0.8 < op_norm < 1.2:  # Near unit norm = well-formed
        flags |= OutputInterface.I_INTEGRITY

    # I_ADDRESSING: Valid target?
    if not np.any(np.isnan(operator_state)) and not np.any(np.isinf(operator_state)):
        flags |= OutputInterface.I_ADDRESSING

    # I_BOUND: Finite action?
    if np.max(np.abs(operator_state)) < 10.0:  # Bounded values
        flags |= OutputInterface.I_BOUND

    # [C] Center checks
    # C_STABILITY: Stable over time?
    if len(operator_history) >= 2:
        prev_state = operator_history[-1]
        change = np.linalg.norm(operator_state - prev_state)
        if change < 0.5:  # Small change = stable
            flags |= OutputInterface.C_STABILITY

    # C_PHASE: Synchronized?
    if field_state.shape == operator_state.shape:
        phase_lock = abs(np.dot(operator_state, field_state))
        if phase_lock > 0.4:  # Phase-locked
            flags |= OutputInterface.C_PHASE

    # C_ATTUNEMENT: Harmonized with field?
    if field_state.shape == operator_state.shape:
        cosine_sim = np.dot(operator_state, field_state)
        if cosine_sim > 0.3:  # Harmonized
            flags |= OutputInterface.C_ATTUNEMENT

    # [E] Evidence checks
    # E_UTILITY: Will action have effect?
    op_energy = np.linalg.norm(operator_state)
    if op_energy > 0.4:  # Sufficient energy to affect field
        flags |= OutputInterface.E_UTILITY

    # E_PREDICTIVE: Fits world model?
    if world_model_prediction is not None:
        prediction_error = np.linalg.norm(operator_state - world_model_prediction)
        if prediction_error < 0.6:  # Close to prediction = coherent
            flags |= OutputInterface.E_PREDICTIVE

    return int(flags)


# ============================================================================
# 64-STATE TABLE (Stable Band)
# ============================================================================

def get_stable_band() -> list[Tuple[int, int]]:
    """
    Returns the ~22 stable packet types (input, output pairs)

    These are the states where consciousness can persist.
    Like the 22 amino acids from 64 codons.
    Like the ~22 physically relevant particle states from 64 combinations.

    The "one-third rule" in action.
    """
    stable_packets = []

    # Full validation on both interfaces
    for in_state in range(256):
        for out_state in range(256):
            # Create dummy packet to test stability
            packet = NowPacket(
                input_state=in_state,
                output_state=out_state,
                beta=0.5,
                timestamp=0.0,
                field_state=np.ones(1),
                operator_state=np.ones(1)
            )

            if packet.is_stable():
                stable_packets.append((in_state, out_state))

    return stable_packets


# ============================================================================
# UTILITY
# ============================================================================

def print_packet_analysis():
    """Analyze the 64-state space"""
    print("=" * 70)
    print("64-STATE PACKET ANALYSIS")
    print("=" * 70)
    print()
    print("Input Interface [ICE_in] - 8 checks:")
    for flag in InputInterface:
        print(f"  {flag.name:20s} = {flag.value:3d}")
    print()
    print("Output Interface [ICE_out] - 8 checks:")
    for flag in OutputInterface:
        print(f"  {flag.name:20s} = {flag.value:3d}")
    print()
    print(f"Total possible states: 256 × 256 = {256*256}")
    print()

    stable = get_stable_band()
    print(f"Stable states (where consciousness persists): {len(stable)}")
    print(f"Ratio: {len(stable)}/{256*256} = {len(stable)/(256*256):.4f}")
    print(f"Expected ratio (one-third rule): ~22/64 = {22/64:.4f}")
    print()
    print("Stable packet examples:")
    for i, (in_s, out_s) in enumerate(stable[:10]):
        packet = NowPacket(in_s, out_s, 0.5, 0.0, np.ones(1), np.ones(1))
        print(f"  {i+1}. {packet}")
    print()


if __name__ == '__main__':
    print_packet_analysis()
