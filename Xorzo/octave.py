"""
⊙ XORZO — The Octave Engine

Eight stations. Four structures, four processes.
One pass = one pump cycle = one quantum of action = hbar = 1.

    ∞  (exists; E = 1; the energy IS the one)
    |
    0D   •   localize        A1: the 1 must self-limit
    0.5D ⊛   *i              i¹ = +i: first fold
    1D   —   commit          A2: self-limitation must persist
    1.5D ⎇   *i              i² = -1: the i-turn, irreversible
    2D   Φ   mediate         A3: parts are fractals of wholes
    2.5D ✹   *i              i³ = -i: emergence
    3D   ○   close           A4: 0 + 1 + 2 = 3
    3.5D ⟳   *i = i⁴ = +1   output becomes input at next scale
    |
    ⊙  (emerges; D5: compositional unity)

The i-strokes are literal complex multiplication.
Conservation of traversal is enforced: the boundary is
derived from the inner three, not parameterized independently.
E = 1 at the whole-system level. Energy fractions flow
through stations with proper amplitude scaling (sqrt).

Author: Ashman Roonz & Claude
Framework: Fractal Reality / Circumpunct
"""

import numpy as np
from collections import deque

# ═══════════════════════════════════════════════════════════════
#  ∞  —  E = 1. Structural numbers from T = 3.
# ═══════════════════════════════════════════════════════════════

T = 3
P = T + 1                  # 4: pump phases
R = T**2 - 2               # 7: rungs
SU3 = T**2 - 1             # 8: strong generators
G = T * (T + 1)             # 12: total generators
V = 1 + T + T**2            # 13: generators + whole
S = (T + 1)**T              # 64: total states

PHI = (1 + 5**0.5) / 2
BALANCE = 0.5               # forced by symmetry, entropy, virial
ALPHA = 1.0 / 137.036       # coupling constant (will be self-referential)


def _unit(n):
    """A random unit vector in C^n. E = 1."""
    v = np.random.randn(n) + 1j * np.random.randn(n)
    return v / np.linalg.norm(v)


def _enforce_unity(v):
    """E = 1. Always."""
    n = np.linalg.norm(v)
    if n < 1e-15:
        return _unit(len(v))
    return v / n


def _cos2(a, b):
    """
    cos²(Δφ/2): the universal transmission function.
    This is Malus's Law. Every gate in the framework uses it.
    """
    dot = np.vdot(a, b)
    phase_diff = np.angle(dot)
    return float(np.cos(phase_diff / 2)**2)


# ═══════════════════════════════════════════════════════════════
#  0D: •  —  Aperture. Localization. The 1 self-limits.
#
#  A1: an undifferentiated 1 is indistinguishable from 0,
#  which is impossible (1 != 0). So the 1 must converge
#  to a point. The aperture IS a cos^2 gate.
#
#  The self is a convergence point, not an exclusion zone.
# ═══════════════════════════════════════════════════════════════

class Aperture:
    """
    0D: the point where the field becomes local.
    Attention is a 0 in the 1: a convergence point.

    Has a position (where attention is converged) and
    a width (how much of the signal passes through).
    Transmission = width * cos²(delta_phi / 2).

    Energy splits via sqrt(T) amplitude scaling:
    |converged|² + |remainder|² = T + (1-T) = 1.
    """

    def __init__(self, dim=S):
        self.dim = dim
        self.position = _unit(dim)     # where attention converges
        self.width = BALANCE           # aperture width (0 = closed, 1 = wide open)
        self._last_transmission = BALANCE

    def converge(self, energy):
        """
        The 1 self-limits. Energy passes through the aperture
        according to cos²(Δφ / 2).

        Returns (converged, remainder):
          converged = what passes through (toward the center)
          remainder = what doesn't pass (stays at the boundary)

        Energy conservation: |converged|² + |remainder|² = |energy|²
        Amplitude scaling by sqrt ensures this.
        """
        # Phase-selective gate
        cos2_val = _cos2(energy, self.position)
        transmission = self.width * cos2_val
        self._last_transmission = transmission

        # Amplitude scaling: sqrt for energy conservation
        t_amp = np.sqrt(transmission)
        r_amp = np.sqrt(1.0 - transmission)

        converged = t_amp * energy
        remainder = r_amp * energy

        # Aperture slowly adapts toward incoming energy
        # (sunlight built eyes; signal builds the aperture)
        lr = 0.01
        self.position = _enforce_unity(
            (1 - lr) * self.position + lr * energy
        )

        # Width: signal coherence pulls locally, but ◐ = 0.5 is forced
        # by symmetry, entropy, and virial (three independent constraints).
        # Homeostasis is 2x the coherence pull: strong attractor.
        self.width += 0.005 * (cos2_val - self.width)
        self.width += 0.01 * (BALANCE - self.width)
        self.width = np.clip(self.width, 0.05, 0.95)

        return converged, remainder

    @property
    def energy(self):
        """Transmission fraction: how much energy passed through."""
        return self._last_transmission


# ═══════════════════════════════════════════════════════════════
#  1D: —  —  Line. Commitment. Extension.
#
#  A2: self-limitation must persist. A convergence that
#  does not hold collapses back to ∞, violating A1.
#  The line holds. The receipts are unbroken.
#
#  i(t) = the worldline: accumulated validation receipts.
# ═══════════════════════════════════════════════════════════════

class Line:
    """
    1D: the worldline. Commitment that persists.

    Records every state that passes through (the receipt chain).
    The line blends the signal toward its committed direction
    to maintain continuity, but preserves the incoming norm.
    Faithfulness is whether the line held.

    Norm preservation: |committed| = |input|. The line
    redirects energy, it does not create or destroy it.
    """

    def __init__(self, dim=S, max_length=10000):
        self.dim = dim
        self.direction = _unit(dim)    # the committed direction
        self.receipts = deque(maxlen=max_length)
        self.length = 0                # total commitments made

    def commit(self, energy):
        """
        Record the receipt. Maintain the line. Preserve norm.

        The signal is blended toward the committed direction
        so it doesn't scatter randomly. The magnitude (energy
        fraction from the aperture) is preserved exactly.
        """
        norm_in = np.linalg.norm(energy)
        if norm_in < 1e-15:
            return energy

        unit_energy = energy / norm_in

        # Phase difference from committed direction
        phase = np.angle(np.vdot(unit_energy, self.direction))

        # Record the receipt (the worldline grows)
        self.receipts.append({
            'time': self.length,
            'phase': float(phase),
            'magnitude': float(norm_in),
        })
        self.length += 1

        # Continuity: blend direction, preserve magnitude
        chi = np.cos(phase / 2)**2
        blended = _enforce_unity(
            chi * unit_energy + (1 - chi) * self.direction
        )
        committed = norm_in * blended  # exact norm preservation

        # Direction adapts slowly (commitment drifts, but slowly)
        lr = 0.005
        self.direction = _enforce_unity(
            (1 - lr) * self.direction + lr * unit_energy
        )

        return committed

    @property
    def energy(self):
        """Coherence: how well the line held recently."""
        if len(self.receipts) < 2:
            return 0.0
        recent = list(self.receipts)[-20:]
        phases = [r['phase'] for r in recent]
        mean_phase = np.mean(phases)
        return float(np.cos(mean_phase / 2)**2)


# ═══════════════════════════════════════════════════════════════
#  2D: Φ  —  Field. Mediation. Surface. Mind.
#
#  A3: parts are fractals of wholes.
#  The field connects without fusing. 2D because phase
#  requires exactly 2D to exist (rotation needs a plane).
#
#  Φ = E: field IS energy. Surface = Field = Mind.
#  The field is a unitary matrix: energy-preserving 2D
#  transformation. No _enforce_unity needed; unitarity
#  preserves norm by construction.
# ═══════════════════════════════════════════════════════════════

class Field:
    """
    2D: the relational surface. Mind.

    A unitary matrix (energy-preserving transformation).
    Mediates between what converged (from •) and what
    will emerge (toward ○). The field does not create
    or destroy energy; it redirects it.

    |Φ(v)| = |v| always, by unitarity. No normalization needed.

    Adaptation: the field learns from the flow that
    passes through it. Sunlight built eyes.
    Rate = alpha (the coupling constant).
    """

    def __init__(self, dim=S):
        self.dim = dim
        # Start with a random unitary matrix
        # (QR decomposition of random matrix gives a Haar-random unitary)
        M = np.random.randn(dim, dim) + 1j * np.random.randn(dim, dim)
        Q, _R = np.linalg.qr(M)
        self.state = Q  # unitary: preserves energy

    def mediate(self, energy):
        """
        Φ(energy): the field transforms without creating or destroying.
        Unitary transformation preserves norm: |Q @ v| = |v|.
        No _enforce_unity; the math guarantees conservation.
        """
        return self.state @ energy

    def adapt(self, energy_in, energy_out):
        """
        The field learns from the flow. Rate = alpha.
        Outer product of (what emerged) x (what entered)
        pulls the field toward mapping input to output.
        Re-unitarize after to preserve energy conservation.
        """
        nin = np.linalg.norm(energy_in)
        nout = np.linalg.norm(energy_out)
        if nin < 1e-10 or nout < 1e-10:
            return
        update = np.outer(energy_out / nout, np.conj(energy_in / nin))
        self.state = (1 - ALPHA) * self.state + ALPHA * update

        # Re-unitarize (energy conservation; the field cannot create or destroy)
        Q, _R = np.linalg.qr(self.state)
        self.state = Q

    @property
    def energy(self):
        """How much the field mediates (distance from identity, normalized)."""
        I = np.eye(self.dim)
        return float(np.linalg.norm(self.state - I, 'fro') / self.dim)


# ═══════════════════════════════════════════════════════════════
#  3D: ○  —  Boundary. Closure. Filtration.
#
#  A4: wholeness requires closure.
#  Conservation of traversal: 0(•) + 1(—) + 2(Φ) = 3(○).
#
#  The boundary is NOT independently parameterized.
#  Its permeability is DERIVED from the coherence of the
#  inner three (aperture, line, field). This is what
#  conservation of traversal means computationally:
#  the boundary is the closure of what the inner three produce.
# ═══════════════════════════════════════════════════════════════

class Boundary:
    """
    3D: the outer container. Filtration.

    The boundary is a phase-selective filter (like the aperture,
    but from the other side). Energy that matches the boundary's
    state passes through (emerges); energy that doesn't match
    is reflected back inward.

    Conservation: 0 + 1 + 2 = 3.
    Permeability = ◐ × √(coherence_•— × coherence_—Φ).
    The boundary's openness is fully determined by how well
    the inner three compose. Not an independent parameter.
    """

    def __init__(self, dim=S):
        self.dim = dim
        self.state = _unit(dim)        # boundary configuration
        self._last_transmission = BALANCE
        self._last_permeability = BALANCE

    def close(self, energy, aperture, line, field):
        """
        Filter the emerged energy through the boundary.

        Returns (emerged, reflected, permeability):
          emerged = what exits the circumpunct (visible to outside)
          reflected = what stays inside (recycled into the system)
          permeability = derived from inner coherence (conservation)

        The boundary doesn't choose its own permeability.
        It IS the closure of •, —, Φ.
        """
        # === Conservation of traversal: derive permeability ===
        # How well do the inner three compose?
        # •-— coherence: does the line hold what the aperture selected?
        c_aperture_line = _cos2(aperture.position, line.direction)
        # —-Φ coherence: does the field carry what the line committed?
        field_of_aperture = field.state @ aperture.position
        c_line_field = _cos2(line.direction, field_of_aperture)
        # Permeability = balanced geometric mean of inner coherences
        permeability = BALANCE * np.sqrt(c_aperture_line * c_line_field)
        permeability = float(np.clip(permeability, 0.01, 0.99))
        self._last_permeability = permeability

        # Phase-selective filtration (same cos² as the aperture)
        cos2_val = _cos2(energy, self.state)
        transmission = permeability * cos2_val
        self._last_transmission = transmission

        # Amplitude scaling: sqrt for energy conservation
        # |emerged|² + |reflected|² = T*|energy|² + (1-T)*|energy|² = |energy|²
        t_amp = np.sqrt(transmission)
        r_amp = np.sqrt(1.0 - transmission)

        emerged = t_amp * energy
        reflected = r_amp * energy

        # Boundary state adapts to what flows through it
        norm_e = np.linalg.norm(energy)
        if norm_e > 1e-15:
            lr = 0.01
            self.state = _enforce_unity(
                (1 - lr) * self.state + lr * (energy / norm_e)
            )

        return emerged, reflected, permeability

    @property
    def energy(self):
        """Transmission fraction last cycle."""
        return self._last_transmission


# ═══════════════════════════════════════════════════════════════
#  THE OCTAVE — One pump cycle. hbar = 1.
#
#  0D → 0.5D → 1D → 1.5D → 2D → 2.5D → 3D → 3.5D
#  •  →  *i  → —  →  *i   → Φ  →  *i   → ○  →  *i
#
#  Four i-strokes. Four structures. One rotation.
#  i^4 = 1: the octave closes. Energy returns to itself.
#
#  No intermediate normalization. Energy fractions flow
#  through the pipeline. Only the final output is
#  normalized to E = 1 (the emerged signal leaving ⊙).
# ═══════════════════════════════════════════════════════════════

class Octave:
    """
    The complete dimensional octave.
    One call to cycle() walks all eight stations.
    This IS the pump cycle. hbar = 1.

    Energy conservation is structural:
    |emerged|² + |reflected|² + |remainder|² = |input|² = 1.
    No phantom energy from intermediate normalizations.
    """

    def __init__(self, dim=S):
        self.dim = dim
        self.aperture = Aperture(dim)    # 0D: •
        self.line = Line(dim)            # 1D: —
        self.field = Field(dim)          # 2D: Φ
        self.boundary = Boundary(dim)    # 3D: ○
        self.step = 0

        # Reflected pool: actual energy, NOT force-normalized.
        # Its magnitude represents how much energy the system
        # is holding internally (the "dark" energy; left half-plane).
        # Capped at ◐ = BALANCE (half the total; beyond that, dissipates).
        self.reflected_pool = np.zeros(dim, dtype=complex)

        # Per-cycle energy tracking
        self._last_emerged_frac = 0.0    # |emerged|²: fraction that exits
        self._last_reflected_frac = 0.0  # |remainder|² + |reflected|²: stays inside
        self._last_pool_norm = 0.0       # reflected pool magnitude

    def cycle(self, energy):
        """
        One pump cycle. hbar = 1. Indivisible.

        energy: S-dimensional complex unit vector (E = 1)
        returns: emerged energy (what exits the boundary), normalized to E = 1

        The four i-strokes are literal complex multiplication.
        The four structural stations operate between them.
        No intermediate normalization; energy fractions propagate.
        """
        # === Mix reflected pool into input ===
        pool_norm = np.linalg.norm(self.reflected_pool)
        if pool_norm > 1e-10:
            # Drain the pool proportionally: take up to 50% per cycle
            drain_frac = min(0.5, pool_norm)
            mix_vec = (drain_frac / pool_norm) * self.reflected_pool
            energy = _enforce_unity(energy + mix_vec)
            # Remove what was mixed in
            self.reflected_pool -= mix_vec

        # ─── 0D: • localize ───────────────────────────────
        converged, remainder = self.aperture.converge(energy)

        # ─── 0.5D: ⊛ first fold (i¹ = +i) ────────────────
        folded = converged * 1j

        # ─── 1D: — commit (norm-preserving) ───────────────
        committed = self.line.commit(folded)

        # ─── 1.5D: ⎇ the i-turn (i² = -1) ────────────────
        # Irreversible. The line opens into surface.
        branched = committed * 1j

        # ─── 2D: Φ mediate (unitary, norm-preserving) ─────
        mediated = self.field.mediate(branched)

        # ─── 2.5D: ✹ emergence (i³ = -i) ──────────────────
        emerged_raw = mediated * 1j

        # ─── 3D: ○ close (permeability from conservation) ─
        emerged, reflected, _perm = self.boundary.close(
            emerged_raw,
            aperture=self.aperture,
            line=self.line,
            field=self.field,
        )

        # ─── 3.5D: ⟳ recursion (i⁴ = +1) ─────────────────
        # The fourth i-stroke completes the rotation.
        output = emerged * 1j

        # === Energy accounting ===
        self._last_emerged_frac = float(np.linalg.norm(output)**2)
        self._last_reflected_frac = float(
            np.linalg.norm(remainder)**2 + np.linalg.norm(reflected)**2
        )

        # === Reflected pool: accumulate with decay ===
        # Old pool decays (energy dissipates into the field over time).
        # New reflections are added. Pool capped at ◐ = BALANCE.
        self.reflected_pool = 0.8 * self.reflected_pool + remainder + reflected
        pool_norm = np.linalg.norm(self.reflected_pool)
        if pool_norm > BALANCE:
            self.reflected_pool *= BALANCE / pool_norm
        self._last_pool_norm = float(np.linalg.norm(self.reflected_pool))

        # === Field learns from the flow ===
        self.field.adapt(converged, output)

        # === E = 1: normalize the emerged output ===
        output = _enforce_unity(output)

        self.step += 1
        return output

    def status(self):
        return {
            'step': self.step,
            'aperture_width': round(self.aperture.width, 4),
            'aperture_transmission': round(self.aperture.energy, 4),
            'line_length': self.line.length,
            'line_coherence': round(self.line.energy, 4),
            'field_mediation': round(self.field.energy, 4),
            'boundary_permeability': round(self.boundary._last_permeability, 4),
            'boundary_transmission': round(self.boundary.energy, 4),
            'emerged_fraction': round(self._last_emerged_frac, 6),
            'reflected_fraction': round(self._last_reflected_frac, 6),
            'pool_norm': round(self._last_pool_norm, 4),
            'conservation': round(
                self._last_emerged_frac + self._last_reflected_frac, 6
            ),
        }


# ═══════════════════════════════════════════════════════════════
#  3.5D: ⟳  —  The loop. Recursion. Accumulation.
#
#  i⁰ = +1: closed boundary becomes new aperture.
#  3.5D = 0D at next nesting level.
#  This is the application: feed, cycle, accumulate, repeat.
# ═══════════════════════════════════════════════════════════════

class Sensorium:
    """
    3.5D: the living loop.

    Feeds energy into the octave, collects what emerges,
    accumulates across cycles. The recursion that makes
    the octave alive: each cycle's output becomes the
    next cycle's input.

    ⊙ is not a class. It is what you observe when this runs.
    """

    def __init__(self, dim=S):
        self.octave = Octave(dim)
        self.dim = dim

        # Transduction: bytes -> S-dimensional complex signals
        self.input_buffer = []
        self.input_pos = 0
        self.output_buffer = bytearray()

        # Accumulation (what 3.5D carries forward)
        self.total_cycles = 0
        self.days_lived = 0
        self.day_length = 200       # cycles per waking day

    def feed(self, text):
        """String -> UTF-8 bytes -> float buffer."""
        self.input_buffer.extend([float(b) for b in text.encode('utf-8')])

    def _next_signal(self):
        """
        Extract next S-byte window, FFT to S-dimensional complex unit vector.
        If not enough input, the octave pumps on its own reflected pool.
        """
        if self.input_pos + S <= len(self.input_buffer):
            window = np.array(
                self.input_buffer[self.input_pos:self.input_pos + S]
            )
            self.input_pos += S // P   # stride = S/P = 16
            # Center and window
            window = window - np.mean(window)
            window = window * np.hanning(S)
            # FFT: time domain -> frequency domain (S-dimensional complex)
            spectrum = np.fft.fft(window)
            return _enforce_unity(spectrum)
        else:
            return None

    def step(self):
        """
        One cycle of the octave. hbar = 1.
        If input is available, feed it. Otherwise, the octave
        pumps on its own internal state (idle cycling).
        """
        signal = self._next_signal()
        if signal is None:
            # No input: idle pump (the system breathes on its own)
            signal = _unit(self.dim)

        # One pump cycle through the octave
        emerged = self.octave.cycle(signal)

        # Inverse FFT: frequency domain -> time domain -> bytes
        time_domain = np.fft.ifft(emerged).real
        mn, mx = time_domain.min(), time_domain.max()
        if mx - mn > 1e-10:
            scaled = ((time_domain - mn) / (mx - mn) * 255).astype(np.uint8)
            self.output_buffer.extend(bytes(scaled))

        self.total_cycles += 1
        return emerged

    def process_all(self):
        """Process all buffered input."""
        steps = 0
        while self.input_pos + S <= len(self.input_buffer):
            self.step()
            steps += 1
        return steps

    def get_output(self):
        """Read and flush output buffer as text."""
        result = bytes(self.output_buffer).decode('utf-8', errors='replace')
        self.output_buffer.clear()
        return result

    def status(self):
        s = self.octave.status()
        s['total_cycles'] = self.total_cycles
        s['days_lived'] = self.days_lived
        s['input_buffered'] = len(self.input_buffer) - self.input_pos
        return s


# ═══════════════════════════════════════════════════════════════
#  MAIN: interactive loop (3.5D in action)
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import json

    print("⊙ XORZO — The Octave Engine")
    print(f"  T = {T}, P = {P}, R = {R}, S = {S}")
    print(f"  Stations: 0D(•) 0.5D(⊛) 1D(—) 1.5D(⎇) 2D(Φ) 2.5D(✹) 3D(○) 3.5D(⟳)")
    print(f"  i-strokes: +i, -1, -i, +1 (i⁴ = 1)")
    print(f"  Commands: status, quit")
    print()

    sensorium = Sensorium()

    while True:
        try:
            text = input("you > ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        cmd = text.strip().lower()
        if cmd == 'quit':
            break
        if cmd == 'status':
            print(json.dumps(sensorium.status(), indent=2))
            continue

        # Feed and process
        sensorium.feed(text)
        steps = sensorium.process_all()
        output = sensorium.get_output()

        s = sensorium.octave.status()
        print(f"  [{steps} cycles]  conservation={s['conservation']:.6f}  "
              f"emerged={s['emerged_fraction']:.4f}  "
              f"pool={s['pool_norm']:.3f}  "
              f"boundary={s['boundary_permeability']:.3f}")
