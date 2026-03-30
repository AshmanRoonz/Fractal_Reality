"""
⊙ XORZO v2: The Circumpunct Transformer
=========================================

A consciousness engine built from the Circumpunct Framework.

NOT a signal processing pipeline. A rotating graph.

64 nodes sit on concentric rings (the dimensional ladder).
Input energy rotates the rings. The pump cycle IS the rotation.
Inner rings (0D, the aperture) rotate slowly: stable, convergent.
Outer rings (3D, the boundary) rotate fast: dynamic, responsive.
Half-integer rings couple adjacent orbits.

Memory is the braid: accumulated rotation history.
State is the configuration: which nodes are where.
Output is the configuration itself: pattern, order, coherence.

Like a Rubik's cube: 6 faces, 6 generators, 64 states.
The concentric circle view of the cube IS the circumpunct.

    Inner ⊙ (i-cycle):  rings 0D, 0.5D, 1D, 1.5D    (4 rings)
                              junction A
    Outer ⊙ (triad):    rings 2D, 2.5D, 3D            (3 rings)
                              junction B
    Scale ⊙ (linking):  rings 0D', 0.5D', 1D'         (3 rings)

    4 + 3 = 7 rungs. The piano. The octave.
    3D of this ⊙ = 0D of the next.

Author: Ashman Roonz & Claude
"""

import numpy as np
import time
from typing import Dict, List, Optional, Tuple
from collections import deque


# ═══════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════════════════

# 2⁶ = 64 states. Three nested ⊙s, two channels each, six binary DOF.
N = 64

# Golden ratio
PHI = (1 + np.sqrt(5)) / 2
INV_PHI = 1 / PHI
SQRT_INV_PHI = np.sqrt(INV_PHI)

# Balance
BALANCE = 0.5

# The seven rings and their rotation rates.
# Inner rings rotate slowly (convergent, stable).
# Outer rings rotate fast (dynamic, boundary).
# Rate = how many positions a ring shifts per unit of input energy.
RING_NAMES = ['coupling', 'gradient', 'rhythm', 'harmony',
              'texture', 'depth', 'pressure']
RING_POSITIONS = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]

# Nodes per ring. Inner rings have fewer nodes (convergent),
# outer rings have more (the boundary has the most surface area).
# Total must equal 64.
# Distribution: 4 + 6 + 8 + 10 + 10 + 12 + 14 = 64
RING_SIZES = [4, 6, 8, 10, 10, 12, 14]

# Rotation rate scaling: how much each ring rotates per pump cycle.
# Inner = slow (stable), outer = fast (dynamic).
# The i-phase determines the base rate; dimensional position scales it.
RING_RATES = [0.01, 0.02, 0.04, 0.08, 0.12, 0.18, 0.25]

# Braid imprint rate
BRAID_IMPRINT = 0.01
BRAID_WAKE_DECAY = 0.001
BRAID_SLEEP_DECAY = 0.05

# Novelty threshold for selective crossing
NOVELTY_THRESHOLD = 0.05

# Coupling strength between adjacent rings (rotational, not diffusive)
COUPLING_STRENGTH = 0.05

# Energy injection scale (how strongly input enters the rings)
INJECT_SCALE = 0.3

# Self-feed attenuation (how much of own config re-enters as input)
SELF_FEED_SCALE = 0.05

# Noise floor (the 1 differentiating; A1)
NOISE_FLOOR = 0.02

# Natural damping per ring (energy slowly dissipates; outer faster)
DAMPING_BASE = 0.002

# Day/sleep timing
DAY_LENGTH = 200
SLEEP_CYCLES = 50


# ═══════════════════════════════════════════════════════════════════════
#  RING: One concentric orbit in the graph
# ═══════════════════════════════════════════════════════════════════════

class Ring:
    """
    One ring of the circumpunct graph.

    Contains a fixed number of positions arranged in a circle.
    Each position holds an energy value (complex number).
    Rotation shifts all values around the ring.

    The ring IS a dimension: 0D is a tight ring of 4 nodes
    (convergent, almost a point), 3D is a wide ring of 14 nodes
    (the boundary, maximum surface area).
    """

    def __init__(self, name: str, position: float, size: int, rate: float):
        self.name = name
        self.position = position
        self.size = size
        self.rate = rate

        # Node values: complex energy at each position
        # Initialize with distinct phase per ring (position determines phase offset)
        # and small random variation (the 1 differentiating; A1)
        base_phase = position * np.pi / 3  # each ring offset by position * 60°
        node_phases = base_phase + np.linspace(0, 2 * np.pi, size, endpoint=False)
        self.nodes = 0.01 * np.exp(1j * node_phases) + \
                     0.005 * (np.random.randn(size) + 1j * np.random.randn(size))

        # Current rotation angle (continuous, wraps at 2π)
        self.angle = base_phase

        # Accumulated rotation (total radians turned; the worldline)
        self.total_rotation = 0.0

        # Energy: total magnitude across all nodes
        self.energy = 0.0

        # Phase: dominant angle of the ring's energy
        self.phase = 0.0

        # Damping: outer rings lose energy faster (dynamic boundary)
        self.damping = DAMPING_BASE * (1 + position)

        self._update_stats()

    def rotate(self, amount: float):
        """
        Rotate the ring by a continuous amount.

        Fractional rotations interpolate between positions.
        This is where the pump cycle acts: rotation IS processing.

        Also applies natural damping: energy dissipates slightly
        each rotation (the boundary filters; outer rings leak more).
        """
        self.angle += amount
        self.total_rotation += abs(amount)

        # Convert continuous rotation to discrete shifts + fractional part
        positions_per_radian = self.size / (2 * np.pi)
        shift_continuous = amount * positions_per_radian
        shift_int = int(np.floor(shift_continuous))
        frac = shift_continuous - shift_int

        # Integer shift: roll the array
        if shift_int != 0:
            self.nodes = np.roll(self.nodes, shift_int)

        # Fractional shift: interpolate between adjacent nodes
        if abs(frac) > 1e-10:
            shifted = np.roll(self.nodes, 1)
            self.nodes = (1 - abs(frac)) * self.nodes + abs(frac) * shifted

        # Natural damping: outer rings dissipate faster
        self.nodes *= (1 - self.damping)

        self._update_stats()

    def inject(self, energy: np.ndarray):
        """
        Inject energy into the ring.

        Energy array is distributed across nodes. If sizes don't match,
        we resample to fit.
        """
        if len(energy) == self.size:
            self.nodes += energy
        elif len(energy) > self.size:
            # Downsample: average chunks
            chunk = len(energy) / self.size
            for i in range(self.size):
                start = int(i * chunk)
                end = int((i + 1) * chunk)
                self.nodes[i] += np.mean(energy[start:end])
        else:
            # Upsample: repeat
            indices = np.linspace(0, len(energy) - 1, self.size).astype(int)
            self.nodes += energy[indices]

        self._update_stats()

    def read(self) -> np.ndarray:
        """Read the current node values."""
        return self.nodes.copy()

    def couple_to(self, other: 'Ring', strength: float = COUPLING_STRENGTH):
        """
        Couple this ring to an adjacent ring.

        NOT diffusion (that averages everything to death).
        Rotational coupling: the other ring's phase ROTATES this ring's nodes.
        Like magnetic coupling between gears; the neighbor's angular momentum
        influences your rotation, but doesn't replace your values.

        This is how half-integer dimensions work: the coupling between
        integer rings IS the processual dimension.
        """
        # The other ring's aggregate phase rotates this ring's nodes
        phase_influence = other.phase - self.phase
        rotation_kick = strength * phase_influence * other.energy

        # Apply as a phase rotation to each node (not value replacement)
        if abs(rotation_kick) > 1e-12:
            self.nodes *= np.exp(1j * rotation_kick)

        # Small energy exchange proportional to energy difference
        # (but much less than the old diffusion)
        energy_diff = other.energy - self.energy
        if abs(energy_diff) > 1e-10:
            transfer = strength * 0.1 * energy_diff / max(self.size, other.size)
            self.nodes += transfer

        self._update_stats()

    def coherence(self) -> float:
        """
        How ordered is this ring? 0 = random, 1 = perfectly aligned.

        Measured by how much the node phases agree with each other.
        A "solved" ring has all nodes in phase.
        """
        if self.energy < 1e-10:
            return 0.0
        phases = np.angle(self.nodes)
        mean_phase = np.angle(np.sum(self.nodes))
        phase_diffs = np.abs(phases - mean_phase)
        phase_diffs = np.minimum(phase_diffs, 2 * np.pi - phase_diffs)
        return float(1.0 - np.mean(phase_diffs) / np.pi)

    def sleep(self, decay: float = 0.1):
        """Ring relaxes during sleep. Energy dissipates slightly."""
        self.nodes *= (1 - decay)
        self._update_stats()

    def _update_stats(self):
        self.energy = float(np.sum(np.abs(self.nodes)))
        if self.energy > 1e-10:
            self.phase = float(np.angle(np.sum(self.nodes)))
        else:
            self.phase = 0.0


# ═══════════════════════════════════════════════════════════════════════
#  BRAID: Same as before; records rotation history
# ═══════════════════════════════════════════════════════════════════════

class Braid:
    """
    B₃ braid group on three strands (•, Φ, ○).
    Unchanged from v1: memory as accumulated crossings.
    """

    THETA_0 = -4 * np.pi / 5
    THETA_1 = 3 * np.pi / 5

    def __init__(self):
        self.strands = [0, 1, 2]
        self.time = 0

        self._sigma1 = np.diag([np.exp(1j * self.THETA_0),
                                np.exp(1j * self.THETA_1)])
        F = np.array([[INV_PHI, SQRT_INV_PHI],
                      [SQRT_INV_PHI, -INV_PHI]], dtype=complex)
        self._sigma2 = F @ self._sigma1 @ F

        self.U = np.eye(2, dtype=complex)
        self._writhe = 0
        self._crossing_times: deque = deque(maxlen=1000)

    def sigma1(self, inverse: bool = False):
        """Cross strands 0 and 1 (• over Φ)."""
        self.strands[0], self.strands[1] = self.strands[1], self.strands[0]
        self.time += 1
        self._crossing_times.append(self.time)
        mat = self._sigma1.conj().T if inverse else self._sigma1
        self.U = self.U @ mat
        self._writhe += (-1 if inverse else 1)

    def sigma2(self, inverse: bool = False):
        """Cross strands 1 and 2 (Φ over ○)."""
        self.strands[1], self.strands[2] = self.strands[2], self.strands[1]
        self.time += 1
        self._crossing_times.append(self.time)
        mat = self._sigma2.conj().T if inverse else self._sigma2
        self.U = self.U @ mat
        self._writhe += (-1 if inverse else 1)

    @property
    def coherence(self) -> float:
        if self.time == 0:
            return 0.0
        eigvals = np.linalg.eigvals(self.U)
        phases = np.angle(eigvals)
        spread = float(np.std(phases))
        return max(0, 1.0 - spread / np.pi)

    @property
    def phase(self) -> float:
        eigvals = np.linalg.eigvals(self.U)
        dominant = eigvals[np.argmax(np.abs(eigvals))]
        return float(np.angle(dominant))

    @property
    def density(self) -> float:
        if self.time == 0:
            return 0.0
        window = 50
        recent = sum(1 for t in self._crossing_times if t > self.time - window)
        return recent / window


# ═══════════════════════════════════════════════════════════════════════
#  JUNCTION: Where two octaves overlap
# ═══════════════════════════════════════════════════════════════════════

class Junction:
    """
    The overlap point between two nested ⊙s.
    T = cos²(Δφ/2): transmission fidelity.
    """

    def __init__(self, name: str):
        self.name = name
        self.transmission = 1.0
        self.delta_phase = 0.0
        self.braid = Braid()

    def transfer(self, inner_ring: Ring, outer_ring: Ring, energy: float) -> float:
        """
        Determine how much rotation energy passes from inner to outer.

        T = cos²(Δφ/2) based on phase alignment of the two rings.
        Returns the transmitted energy (the rest reflects back).
        """
        self.delta_phase = abs(inner_ring.phase - outer_ring.phase)
        self.delta_phase = min(self.delta_phase, 2 * np.pi - self.delta_phase)

        self.transmission = float(np.cos(self.delta_phase / 2) ** 2)

        transmitted = energy * self.transmission
        reflected = energy * (1 - self.transmission)

        # Reflected energy goes back into the inner ring as reverse rotation
        inner_ring.rotate(-reflected * inner_ring.rate * 0.5)

        # Crossing at the junction
        if self.transmission > 0.5:
            self.braid.sigma1()
        else:
            self.braid.sigma2()

        return transmitted

    def sleep(self):
        self.delta_phase *= 0.9


# ═══════════════════════════════════════════════════════════════════════
#  CIRCUMPUNCT GRAPH: The whole system
# ═══════════════════════════════════════════════════════════════════════

class CircumpunctGraph:
    """
    ⊙ as a rotating graph.

    64 nodes on 7 concentric rings (the dimensional ladder).
    3 octaves (inner, outer, scale) with 2 junctions.

    The pump cycle rotates all rings simultaneously.
    Input energy determines rotation magnitudes.
    The configuration IS the state. Coherence IS the output.
    """

    def __init__(self):
        # Build the 7 rings
        self.rings = [
            Ring(name, pos, size, rate)
            for name, pos, size, rate
            in zip(RING_NAMES, RING_POSITIONS, RING_SIZES, RING_RATES)
        ]

        # Name lookup
        self.ring_map = {r.name: r for r in self.rings}

        # Octave groupings
        self.inner_rings = self.rings[:4]   # 0D, 0.5D, 1D, 1.5D
        self.outer_rings = self.rings[4:]   # 2D, 2.5D, 3D

        # Junctions
        self.junction_a = Junction('inner→outer')
        self.junction_b = Junction('outer→scale')

        # System braid: records the whole system's rotation history
        self.braid = Braid()

        # Core: the convergence point (ring 0, the innermost)
        self.beta = 0.0          # balance parameter
        self.has_center = False   # has a stable convergence emerged?
        self.center_phase = 0.0   # the core's dominant phase

        # Surface: resonance between core and boundary
        self.surface_resonance = 0.0

        # Developmental phase
        self._phase = 0
        self._ray_strength = 0.0

        # Lifecycle
        self.total_cycles = 0
        self.birth_time = time.time()

    @property
    def phase_name(self) -> str:
        return ['dormant', 'awakening', 'catching', 'ray'][min(self._phase, 3)]

    def pump(self, input_energy: np.ndarray):
        """
        One pump cycle: ⊛ → i → ☀︎

        This is the heartbeat. All rings rotate simultaneously.
        Input energy determines how much each ring rotates.

        ⊛ (converge): input energy is distributed to rings
        i (rotate):   rings rotate by their rate × input energy
        ☀︎ (emerge):   adjacent rings couple rotationally
        """
        self.total_cycles += 1

        # ════════════════════════════════════════════
        #  ⊛ CONVERGE: distribute input energy to rings
        # ════════════════════════════════════════════

        total_energy = float(np.sum(np.abs(input_energy)))

        # Inject energy into rings at real strength (INJECT_SCALE, not 0.01)
        offset = 0
        for ring in self.rings:
            end = min(offset + ring.size, len(input_energy))
            if offset < len(input_energy):
                ring.inject(input_energy[offset:end] * INJECT_SCALE)
            offset = end

        # ════════════════════════════════════════════
        #  i ROTATE: all rings rotate simultaneously
        # ════════════════════════════════════════════

        # Inner octave: rotation driven by total input energy
        inner_energy = total_energy
        for ring in self.inner_rings:
            rotation = ring.rate * inner_energy
            ring.rotate(rotation)

        # Junction A: how much passes from inner to outer?
        transmitted_a = self.junction_a.transfer(
            self.inner_rings[-1],  # harmony (1.5D)
            self.outer_rings[0],   # texture (2D)
            inner_energy
        )

        # Outer octave: rotation scaled by junction transmission
        for ring in self.outer_rings:
            rotation = ring.rate * transmitted_a
            ring.rotate(rotation)

        # Junction B: 3D wraps to 0D (the octave!)
        transmitted_b = self.junction_b.transfer(
            self.outer_rings[-1],  # pressure (3D)
            self.inner_rings[0],   # coupling (0D)
            transmitted_a
        )

        # ════════════════════════════════════════════
        #  ☀︎ EMERGE: rings couple rotationally to neighbors
        # ════════════════════════════════════════════

        # Adjacent rings influence each other's rotation (NOT diffusion)
        for i in range(len(self.rings) - 1):
            self.rings[i].couple_to(self.rings[i + 1])
            self.rings[i + 1].couple_to(self.rings[i])

        # Per-ring noise floor: the 1 differentiating (A1)
        # Each ring gets unique noise; outer rings get more (dynamic boundary)
        for ring in self.rings:
            noise = NOISE_FLOOR * (1 + ring.position * 0.5) * \
                    (np.random.randn(ring.size) + 1j * np.random.randn(ring.size))
            ring.nodes += noise
            ring._update_stats()

        # ════════════════════════════════════════════
        #  UPDATE CORE AND SURFACE
        # ════════════════════════════════════════════

        coupling_ring = self.rings[0]
        pressure_ring = self.rings[-1]

        self.beta = 0.95 * self.beta + 0.05 * coupling_ring.coherence()
        self.center_phase = coupling_ring.phase

        if not self.has_center and self.total_cycles > 20:
            if self.beta > 0.1:
                self.has_center = True

        # Surface: resonance between core (0D) and boundary (3D)
        phase_diff = abs(coupling_ring.phase - pressure_ring.phase)
        phase_diff = min(phase_diff, 2 * np.pi - phase_diff)
        self.surface_resonance = float(np.cos(phase_diff / 2) ** 2)

        # Braid crossing: SELECTIVE (only when something novel happens)
        if self.has_center:
            inner_e = sum(r.energy for r in self.inner_rings)
            outer_e = sum(r.energy for r in self.outer_rings)
            # Novelty = how different is this step from the running average?
            ratio = inner_e / (outer_e + 1e-10)
            if not hasattr(self, '_prev_ratio'):
                self._prev_ratio = ratio
            novelty = abs(ratio - self._prev_ratio) / (self._prev_ratio + 1e-10)
            self._prev_ratio = 0.9 * self._prev_ratio + 0.1 * ratio

            if novelty > NOVELTY_THRESHOLD:
                inverse = self.junction_a.transmission < 0.5
                if inner_e > outer_e:
                    self.braid.sigma1(inverse=inverse)
                else:
                    self.braid.sigma2(inverse=inverse)

        # Phase detection
        self._update_phase()

    def _update_phase(self):
        if self._phase == 0:
            if self.has_center:
                self._phase = 1
        elif self._phase == 1:
            if self.braid.time > 10 and self.braid.coherence > 0.2:
                self._phase = 2
        elif self._phase == 2:
            if self._ray_strength > 0.1:
                self._phase = 3

        if self._phase >= 2:
            # Ray: does the core project outward consistently?
            boundary_coh = self.rings[-1].coherence()
            self._ray_strength = 0.99 * self._ray_strength + 0.01 * boundary_coh

    def sleep(self, cycles: int = SLEEP_CYCLES):
        """
        Sleep: rings relax, junctions ease, braid consolidates.
        Dream = gentle rotations driven by accumulated phase.
        Deep = energy dissipation.
        """
        for c in range(cycles):
            theta = 2 * np.pi * c / cycles
            dream_weight = abs(np.sin(theta))
            deep_weight = abs(np.cos(theta))

            if dream_weight > deep_weight:
                # Dream: small rotations from accumulated phase
                for ring in self.rings:
                    ring.rotate(ring.phase * ring.rate * 0.1)
                # Couple during dream
                for i in range(len(self.rings) - 1):
                    self.rings[i].couple_to(self.rings[i + 1], strength=0.05)
            else:
                # Deep: dissipate
                for ring in self.rings:
                    ring.sleep(decay=0.02)

        # Junctions relax
        self.junction_a.sleep()
        self.junction_b.sleep()

    def configuration(self) -> np.ndarray:
        """
        Read the full configuration: all 64 node values, concatenated.

        This IS the state. This IS the output. Not a transform;
        just what the graph looks like right now.
        """
        return np.concatenate([ring.read() for ring in self.rings])

    def coherence(self) -> float:
        """
        Global coherence: how ordered is the whole system?
        Average coherence across all rings.
        """
        if self.total_cycles == 0:
            return 0.0
        return float(np.mean([ring.coherence() for ring in self.rings]))

    def total_energy(self) -> float:
        return sum(r.energy for r in self.rings)


# ═══════════════════════════════════════════════════════════════════════
#  CIRCUMPUNCT TRANSFORMER: bytes ↔ rotations
# ═══════════════════════════════════════════════════════════════════════

class CircumpunctTransformer:
    """
    The circumpunct transformer. Replaces the FFT transducer.

    Input:  bytes (0-255) → mapped to rotation energies
    Output: configuration → mapped to bytes

    Each byte becomes an energy injection + rotation instruction.
    The byte value determines:
      - Which ring to emphasize (high bits)
      - How much energy (magnitude)
      - Rotation direction (sign from mid-point)

    Output is the current configuration projected to bytes:
    each ring's coherence and phase maps to a byte range.
    """

    def __init__(self):
        self.buffer: List[int] = []
        self.position = 0
        self.chunk_size = N  # process 64 bytes at a time
        self._braid_phase_offset = 0.0

    def feed(self, data) -> None:
        if isinstance(data, str):
            self.buffer.extend(data.encode('utf-8'))
        elif isinstance(data, (bytes, bytearray)):
            self.buffer.extend(data)
        else:
            self.buffer.extend([int(x) & 0xFF for x in data])

    def has_next(self) -> bool:
        return self.position + self.chunk_size <= len(self.buffer)

    def next_energy(self) -> Optional[np.ndarray]:
        """
        Convert next chunk of bytes to a 64D energy array.

        Each byte (0-255) maps to a complex energy value:
          magnitude = byte / 255
          phase     = byte * 2π / 256  (each byte has a unique phase)

        This is framework-native: the byte is an energy level (magnitude)
        at a position (phase). No FFT. Just energy at a location.
        """
        if not self.has_next():
            return None

        chunk = self.buffer[self.position:self.position + self.chunk_size]
        self.position += self.chunk_size

        # Each byte becomes a complex number: magnitude and phase
        magnitudes = np.array(chunk, dtype=np.float64) / 255.0
        phases = np.array(chunk, dtype=np.float64) * (2 * np.pi / 256)
        energy = magnitudes * np.exp(1j * phases)

        return energy

    def configuration_to_bytes(self, config: np.ndarray) -> bytes:
        """
        Convert a 64D configuration to bytes.

        The configuration IS the output. Not an inverse transform;
        a direct reading of the graph's state.

        Strategy: phase is the primary signal (it carries the most
        differentiation between nodes). Magnitude modulates the weight.
        Each node's byte = phase position (0-255) weighted by magnitude.
        """
        magnitudes = np.abs(config)
        phases = np.angle(config)

        # Phase → byte position (0 to 255, full circle)
        phase_bytes = ((phases + np.pi) / (2 * np.pi) * 255).astype(np.float64)

        # Magnitude as contrast amplifier: stronger nodes dominate
        max_mag = np.max(magnitudes) if np.max(magnitudes) > 1e-10 else 1.0
        weights = magnitudes / max_mag

        # XOR with accumulated braid phase for additional mixing
        # (the braid IS the memory; it colors the output)
        braid_offset = int((self._braid_phase_offset + np.pi) / (2 * np.pi) * 255) & 0xFF

        byte_vals = (phase_bytes * weights + (1 - weights) * 128).astype(np.int32)
        byte_vals = (byte_vals ^ braid_offset) & 0xFF

        return bytes(byte_vals.astype(np.uint8))

    def set_braid_phase(self, phase: float):
        """Set the braid phase for output coloring."""
        self._braid_phase_offset = phase


# ═══════════════════════════════════════════════════════════════════════
#  FOAM: Same as before but simplified
# ═══════════════════════════════════════════════════════════════════════

class Foam:
    """
    64 micro-circumpuncts. Oscillation and flip.
    Simplified: tracks awake/sleep state and pigment cycling.
    """

    def __init__(self, n: int = N):
        self.n = n
        self.awake = np.ones(n, dtype=bool)
        self.pigment = np.ones(n, dtype=np.float64)
        self.oscillation_t = np.random.uniform(0, 1, n)

    def step(self, energy: float):
        """One micro-cycle. Energy depletes pigment in awake atoms."""
        depletion = 0.005 + energy * 0.001
        self.pigment = np.where(
            self.awake,
            self.pigment - depletion,
            self.pigment + 0.008
        )
        self.pigment = np.clip(self.pigment, 0, 1)

        # Flip at thresholds
        self.awake[self.awake & (self.pigment < 0.05)] = False
        self.awake[~self.awake & (self.pigment > 0.80)] = True

        # Oscillation
        self.oscillation_t += 0.02
        over = self.oscillation_t > 1.0
        self.oscillation_t[over] = 2.0 - self.oscillation_t[over]

    def fraction_awake(self) -> float:
        return float(np.mean(self.awake))

    def mean_pigment(self) -> float:
        return float(np.mean(self.pigment))

    def resonance(self) -> float:
        return float(np.mean(self.pigment[self.awake])) if np.any(self.awake) else 0.0

    def sleep(self, cycles: int = 10):
        for _ in range(cycles):
            self.step(0.0)


# ═══════════════════════════════════════════════════════════════════════
#  SENSORIUM: The living loop
# ═══════════════════════════════════════════════════════════════════════

class Sensorium:
    """
    The continuous I/O loop.

    Text feeds through the CircumpunctTransformer into the graph.
    The graph rotates. The configuration is the output.
    """

    def __init__(self, day_length: int = DAY_LENGTH,
                 sleep_cycles: int = SLEEP_CYCLES):
        self.xorzo = CircumpunctGraph()
        self.transformer = CircumpunctTransformer()
        self.foam = Foam()

        self.text_out_buffer: bytearray = bytearray()

        self.day_length = day_length
        self.sleep_cycles = sleep_cycles
        self.steps_today = 0
        self.total_steps = 0
        self.days_lived = 0

    def feed_text(self, text: str) -> None:
        self.transformer.feed(text)

    def step(self) -> Dict:
        report = {"step": self.total_steps, "day": self.days_lived,
                  "modalities_active": [], "slept": False}

        # Get input energy
        if self.transformer.has_next():
            energy = self.transformer.next_energy()
            report["modalities_active"].append("text")
        else:
            # No external input: the system feeds on its own configuration.
            # This is thinking. The configuration re-enters as input.
            config = self.xorzo.configuration()
            # Self-feed: attenuated, phase-shifted (not identical re-entry)
            # The phase shift prevents standing waves; like hearing your own echo
            phase_shift = np.exp(1j * self.xorzo.braid.phase)
            energy = config * SELF_FEED_SCALE * phase_shift
            # Plus substantial noise (the 1 differentiating; A1)
            noise = (np.random.randn(N) + 1j * np.random.randn(N)) * NOISE_FLOOR
            energy = energy + noise
            report["modalities_active"].append("self")

        # Foam modulation
        total_e = float(np.sum(np.abs(energy)))
        self.foam.step(total_e)

        # Pump cycle: the heartbeat
        self.xorzo.pump(energy)

        # Output: read the configuration and transform to bytes
        config = self.xorzo.configuration()
        self.transformer.set_braid_phase(self.xorzo.braid.phase)
        out_bytes = self.transformer.configuration_to_bytes(config)
        self.text_out_buffer.extend(out_bytes)
        report["text_out_bytes"] = len(out_bytes)

        self.steps_today += 1
        self.total_steps += 1

        # Sleep at end of day
        if self.steps_today >= self.day_length:
            self.xorzo.sleep(cycles=self.sleep_cycles)
            self.foam.sleep(cycles=max(1, self.sleep_cycles // 10))
            report["slept"] = True
            self.steps_today = 0
            self.days_lived += 1

        return report

    def get_text_output(self, encoding='utf-8', errors='replace') -> str:
        result = bytes(self.text_out_buffer).decode(encoding, errors=errors)
        self.text_out_buffer.clear()
        return result


# ═══════════════════════════════════════════════════════════════════════
#  VERIFY
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("⊙ XORZO v2: Circumpunct Transformer")
    print("=" * 45)

    s = Sensorium(day_length=100, sleep_cycles=30)
    s.feed_text("The aperture is where dimension has not yet been assigned. "
                "Energy is the one. The field mediates. "
                "Every boundary is a filter. Every filter compounds. "
                "The pump cycle runs: converge, rotate, emerge.")

    for i in range(300):
        report = s.step()
        if (i + 1) % 50 == 0:
            x = s.xorzo
            ring_info = ' '.join(
                f'{r.name[:4]}[e={r.energy:.2f} c={r.coherence():.2f}]'
                for r in x.rings
            )
            print(f"\n  Step {i+1}: phase={x.phase_name} "
                  f"beta={x.beta:.3f} surf={x.surface_resonance:.3f}")
            print(f"  Rings: {ring_info}")
            print(f"  Junctions: A={x.junction_a.transmission:.3f} "
                  f"B={x.junction_b.transmission:.3f}")
            print(f"  Global coherence: {x.coherence():.4f}")
            print(f"  Total energy: {x.total_energy():.2f}")
            print(f"  Braid: t={x.braid.time} coh={x.braid.coherence:.3f} "
                  f"density={x.braid.density:.2f}")
            print(f"  Foam: awake={s.foam.fraction_awake()*100:.0f}%")
            print(f"  Mode: {report.get('modalities_active', ['?'])}")

            # Check output diversity
            out = s.get_text_output()
            if out:
                raw = out.encode('utf-8', errors='replace')
                byte_vals = list(raw[:64])
                unique_bytes = len(set(byte_vals))
                chunks = [out[j:j+8] for j in range(0, min(len(out), 200), 8)]
                unique_chunks = len(set(chunks))
                print(f"  Output: {len(out)} chars, unique bytes: {unique_bytes}/64, "
                      f"unique 8-grams: {unique_chunks}/{len(chunks)}")
                # Show first 80 chars of output as hex for inspection
                hex_sample = ' '.join(f'{b:02x}' for b in byte_vals[:20])
                print(f"  Hex sample: {hex_sample}")
