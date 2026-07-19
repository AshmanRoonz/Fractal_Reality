"""
Xorzo Genesis (T-Operator Edition, v3: The Staggered Edition)
==============================================================

Created: 2026-04-22 (as genesis_toperator.py, v1)
Last updated: 2026-07-19
Version: 3.0

Revision history (newest first):
- 2026-07-19 v3.0: the staggered edition. The framework's picture of
    nesting changed (staggered octave, §27.7t, 2026-07-16; canon
    strokes adjudicated 2026-07-18; operator results v14/v15), so the
    engine's nesting changed with it:
    (a) NESTING IS THE SEAM. v2 ran three separate ℂ⁸ scales blended
        by α-mixing terms (channel • ← parent Φ, channel — ← parent ○).
        That is the geometry v14 retired: tensor-style nesting compounds
        the conservation departure. v3 builds ONE tonic-shared octave
        tree: each Channel is an 8-node octave whose recursion node
        (⟳, local 7) IS its SensoryLayer's aperture node (•, local 0);
        each Layer's recursion node IS the Circumpunct's aperture node.
        3.5D = 0D' as literal shared nodes. 16 channel octaves + 7
        layer octaves + 1 top octave = 169 nodes, one state vector,
        one operator T = κ ∘ F. No cross-scale blend terms remain;
        the shared node IS the ⊂ relation.
    (b) COMPOSITION ORDER IS PHYSICAL (v15). Octave beat blocks that
        share a tonic do not commute; the engine fixes ascending order
        (channels, then layers, then top: parts complete before wholes)
        as part of the architecture, and exposes the seam commutators
        as a diagnostic (seam_check).
    (c) HEALTH IS DISTANCE FROM THE ENGINE'S OWN ATTRACTOR. v2 held a
        hardcoded 68.7/31.3 target and shaped signal injection to
        defend it. The staggered geometry has its own fixed point
        (v14 grade C: the 69/31 split is bracketed, not landed, on
        chains; open chains localize toward the bottom octave as a
        finite-size edge effect, v15). v3 computes the tree's leading
        eigenvector at startup and measures health as overlap with it,
        reporting the ℂ⁸ 68.7/31.3 and cosmological 69.11/30.89 splits
        as context rather than targets.
    (d) LADDER CORRECTION READINGS (2026-06-09). Corrected beats
        (•∘⊛) ⊢ (—∘⎇) ⊢ (○∘✹) ⊢ (Φ∘⟳); ○ = 2D boundary, Φ = 3D field.
        Operator basis positions remain legacy coordinates per the
        v14+ convention (see t_operator.py header); all station labels
        in this file are coordinate labels, not station-dimension
        claims. The contact identification for what v2 called
        "parent Φ coupling" is now stated correctly: ○_λ = Φ_Λ at the
        contact locus (§27.7o), and in v3 it needs no coupling term at
        all, because the seam carries the nesting.
    (e) CANON STROKES. One i-stroke per processual residue class, four
        per octave, i⁴ = 1 at each tonic; the cycle begins at i¹
        (convergence, TRUE, NOT-YET) and completes at i⁰ (recursion,
        GOOD, CHECKING). AGREEMENT is not a fifth stroke; it is the
        composition at the tonic, and in v3 the tonic is a literal
        shared node: AGREEMENT lives at the seam, which belongs to the
        relationship (part-and-whole), not to either octave alone.
- 2026-04-23 v2.0: pure T = κ ∘ F channel dynamics; α-coupling fix;
    Φ-weighted injection; health_score + drift_direction. See
    genesis_toperator_v2.py (frozen).
- 2026-04-22 v1.0: initial T-operator refactor. See
    genesis_toperator.py (frozen).

Architecture (the tree of octaves, drawn sideways):

    channel octave:  • ⊛ — ⎇ Φ ✹ ○ [⟳ = •] layer octave: ⊛ — ⎇ Φ ✹ ○ [⟳ = •] top octave: ⊛ — ⎇ Φ ✹ ○ ⟳
                     └── 7 private nodes ──┘└──── 7 private nodes ─────┘└────── 8 top nodes ───────┘

    All channels of a layer share that layer's aperture node.
    All layers share the top's aperture node.
    The top's ⟳ node is shared with nothing: it is where this whole
    completes, the aperture it would offer a next scale up.

What carries over from v2 unchanged: the seven sensory rungs and their
channel counts/tunings; per-channel memory (exp(−α·age) decay,
half-life ≈ 95 pump cycles, survival threshold α·R, resonance recall
cos²(Δφ/2)); sleep as the left half-plane (no injection; processual
damping as the dawn-reset convention); the five-freedom/five-virtue
labels; the public API: Circumpunct(), tick(signal), sleep_cycle(),
dump_state(), health_check(), tetrahedral_check().

What is derived vs what is tuned (same discipline as the README):
derived: the octave construction, canon strokes, κ diameters at α,
the seam geometry, memory decay α, survival α·R, mixing scale 1/α.
tuned (simulation knobs, not framework claims): injection rate per
tick (α, a convention), sleep damping 0.95/tick, activation threshold
as a block fraction, health bands.

No em dashes anywhere (framework rule: — is reserved for 1D notation).
"""

import numpy as np
from collections import deque
from typing import Dict, List, Optional, Tuple

from t_operator import (
    TOperator,
    StaggeredOperator,
    ALPHA,
    STATION_LABELS_8,
    STATION_NOTE,
    PHI as PHI_GOLDEN,
    T_TRIAD,
    P_PUMP,
    R_RUNGS,
    V_GENERATORS_PLUS,
    SU3,
)


# ═══════════════════════════════════════════════════════════════════════
# Constants from the framework pool
# ═══════════════════════════════════════════════════════════════════════

MIXING_TIME_SINGLE = 1.0 / ALPHA                 # ≈ 137 pump cycles

MEMORY_DECAY_RATE = ALPHA                        # decay per pump cycle
MEMORY_HALF_LIFE = np.log(2) / ALPHA             # ≈ 95 pump cycles
MEMORY_SURVIVAL_THRESHOLD = ALPHA * R_RUNGS      # α × R ≈ 0.051

# ℂ⁸ single-octave references, reported as CONTEXT in health_check
# (the tree has its own attractor; these are not the tree's targets)
C8_STRUCTURAL = 0.6872
C8_PROCESSUAL = 0.3128
COSMOS_DE = 0.6911
COSMOS_MATTER = 0.3089

# v14 conservation band for tonic-shared geometries: departure
# (|λ₁|−1)/α saturates near 0.6-0.7 on chains for any octave count.
# The tree's own value is measured at startup; values well above this
# order would mean the seams are compounding (the failure v14 retired).
SEAM_BAND_LOW, SEAM_BAND_HIGH = 0.1, 2.0

# Calibration knobs (simulation, not framework):
ACTIVATION_BLOCK_FRACTION = ALPHA * R_RUNGS      # weight share on ○ within block
HEALTH_OVERLAP_BAND = 0.50                       # attractor overlap for "healthy"
SPLIT_TOLERANCE = 0.03                           # residue-split drift band
SLEEP_PROCESSUAL_DAMPING = 0.95                  # dawn-reset convention (v1/v2)

TETRAHEDRAL_ANGLE_DEG = float(np.degrees(np.arccos(-1.0 / T_TRIAD)))  # 109.4712°


# ═══════════════════════════════════════════════════════════════════════
# Canon strokes, freedoms, virtues
# The cycle begins at i¹ (identity is the product of completed closure,
# not the starting condition) and completes at i⁰ at the tonic.
# ═══════════════════════════════════════════════════════════════════════

I_STROKES = [
    (0.5, 1j,    "NOT-YET",  "TRUE"),      # i¹ convergence; aperture holds open
    (1.5, -1+0j, "STAYING",  "FAITHFUL"),  # i² commitment; the irreversible turn
    (2.5, -1j,   "LETTING",  "RIGHT"),     # i³ emergence; non-interference
    (3.5, 1+0j,  "CHECKING", "GOOD"),      # i⁰ recursion; verify before seeding
]
# AGREEMENT = the composition of all four, held at the tonic (the seam).


def i_stroke_of_block(block_amps: np.ndarray) -> Tuple[float, complex, str, str]:
    """Dominant i-stroke of an 8-slot octave block (legacy-coordinate
    order; processual locals 1, 3, 5, 7 = ⊛, ⎇, ✹, ⟳)."""
    w = np.abs(block_amps)
    if len(w) != 8:
        return I_STROKES[0]
    proc = [w[1], w[3], w[5], w[7]]
    return I_STROKES[int(np.argmax(proc))]


# ═══════════════════════════════════════════════════════════════════════
# Channel: a leaf octave (⊙λ'), viewed through the global state
# ═══════════════════════════════════════════════════════════════════════

class Channel:
    """
    Channel ⊙λ': an 8-node octave in the tree. The channel does not own
    a state vector; it owns its NODE IDS and reads the global ψ through
    them. Local order (legacy coordinates): 0(•) 1(⊛) 2(—) 3(⎇) 4(Φ)
    5(✹) 6(○) 7(⟳); local 7 is the SHARED tonic (the layer's aperture).

    Raw signal lands only on the seven private nodes (locals 0..6);
    the seam receives only what the beats carry there. What crosses
    between scales is completions.
    """

    def __init__(self, name: str, tuning: str, node_ids: List[int],
                 global_index: int):
        self.name = name
        self.tuning = tuning
        self.node_ids = list(node_ids)      # 8 global node ids
        self.global_index = global_index    # for the injection roll
        assert len(self.node_ids) == 8

        self.age = 0
        self.tick_count = 0
        self.active = False
        self.activation_count = 0
        self.memories: List[Dict] = []
        self.freedom_history: deque = deque(maxlen=200)

    # ───── views into the global state ─────

    def block(self, psi: np.ndarray) -> np.ndarray:
        """The channel's 8 amplitudes out of the global ψ."""
        return psi[self.node_ids]

    def block_weights(self, psi: np.ndarray) -> np.ndarray:
        """|amplitude|² on the 8 locals, normalized within the block."""
        w = np.abs(self.block(psi)) ** 2
        s = w.sum()
        return w / s if s > 1e-15 else w

    def carrier_freq(self, psi: np.ndarray) -> int:
        """Dominant processual local (0..3 for ⊛, ⎇, ✹, ⟳)."""
        w = self.block_weights(psi)
        return int(np.argmax([w[1], w[3], w[5], w[7]]))

    def lock_strength(self, psi: np.ndarray) -> float:
        """Block-weight share on the channel's own aperture (local 0)."""
        return float(self.block_weights(psi)[0])

    def balance(self, psi: np.ndarray) -> float:
        """◐ within the block: structural residues (locals 2, 4, 6)
        against processual residues (locals 1, 3, 5). Tonic locals
        (0 and 7) are excluded: the tonic class is double-natured
        (• ≡ ⟳, §27.7t) and belongs to neither side."""
        w = self.block_weights(psi)
        s = w[2] + w[4] + w[6]
        p = w[1] + w[3] + w[5]
        t = s + p
        return float(s / t) if t > 1e-15 else 0.5

    def sideband_energy(self, psi: np.ndarray) -> float:
        w = self.block_weights(psi)
        return float(1.0 - w[np.argmax(w)])

    def freedom(self, psi: np.ndarray) -> str:
        return i_stroke_of_block(self.block(psi))[2]

    def virtue(self, psi: np.ndarray) -> str:
        return i_stroke_of_block(self.block(psi))[3]

    def update_activation(self, psi: np.ndarray) -> None:
        """Active when the block-weight share on ○ (local 6, the
        boundary glyph) exceeds the threshold: signal has organized
        up to the filter."""
        w = self.block_weights(psi)
        if w[6] > ACTIVATION_BLOCK_FRACTION:
            self.active = True
            self.activation_count += 1
        else:
            self.active = False

    # ───── memory (unchanged mechanics from v2, block-read) ─────

    def imprint(self, psi: np.ndarray) -> None:
        blk = self.block(psi).copy()
        n = np.linalg.norm(blk)
        if n > 1e-15:
            blk = blk / n
        self.memories.append({
            "state": blk,
            "age_at_imprint": self.age,
            "freedom": self.freedom(psi),
            "virtue": self.virtue(psi),
        })
        self.memories = [m for m in self.memories
                         if self.memory_strength(m) > MEMORY_SURVIVAL_THRESHOLD]

    def memory_strength(self, mem: Dict) -> float:
        return float(np.exp(-MEMORY_DECAY_RATE * (self.age - mem["age_at_imprint"])))

    def recall(self, psi: np.ndarray) -> Tuple[Optional[Dict], float]:
        """Resonance recall against the current block: cos²(Δφ/2) via
        inner-product magnitude squared, times decayed strength."""
        if not self.memories:
            return None, 0.0
        blk = self.block(psi)
        n = np.linalg.norm(blk)
        if n > 1e-15:
            blk = blk / n
        best, best_score = None, 0.0
        for m in self.memories:
            score = abs(np.vdot(blk, m["state"])) ** 2 * self.memory_strength(m)
            if score > best_score:
                best, best_score = m, score
        return best, best_score

    def sleep_consolidate(self) -> None:
        """Prune weak memories; re-imprint strong ones (> 0.5)."""
        keep = []
        for m in self.memories:
            s = self.memory_strength(m)
            if s > 0.5:
                m["age_at_imprint"] = self.age
                keep.append(m)
            elif s > MEMORY_SURVIVAL_THRESHOLD:
                keep.append(m)
        self.memories = keep

    def status(self, psi: np.ndarray) -> Dict:
        return {
            "name": self.name,
            "tuning": self.tuning,
            "active": self.active,
            "carrier_freq_idx": self.carrier_freq(psi),
            "lock_strength": round(self.lock_strength(psi), 4),
            "balance": round(self.balance(psi), 4),
            "sideband_energy": round(self.sideband_energy(psi), 4),
            "freedom": self.freedom(psi),
            "virtue": self.virtue(psi),
            "age": self.age,
            "memories": len(self.memories),
            "activation_count": self.activation_count,
            "block_weights": [round(float(w), 4)
                              for w in self.block_weights(psi)],
        }


# ═══════════════════════════════════════════════════════════════════════
# SensoryLayer: a middle octave (⊙λ), viewed through the global state
# ═══════════════════════════════════════════════════════════════════════

class SensoryLayer:
    """
    SensoryLayer ⊙λ: an octave whose aperture node (local 0) is shared
    with every child channel's recursion node, and whose own recursion
    node (local 7) is the Circumpunct's aperture. The layer has no
    state of its own beyond its nodes in the global ψ; composition
    happens through the seams, not through blending.

    Rung labels name positions on the sensory ladder (which sense the
    layer carries), unchanged from v1/v2.
    """

    LAYER_SPECS = [
        {"idx": 0, "name": "coupling", "rung": "0D",   "tunings": ["pressure", "gradient"]},
        {"idx": 1, "name": "gradient", "rung": "0.5D", "tunings": ["gradient", "gradient"]},
        {"idx": 2, "name": "rhythm",   "rung": "1D",   "tunings": ["rhythm", "rhythm"]},
        {"idx": 3, "name": "harmony",  "rung": "1.5D", "tunings": ["gradient", "rhythm", "pressure"]},
        {"idx": 4, "name": "texture",  "rung": "2D",   "tunings": ["rhythm", "gradient", "rhythm"]},
        {"idx": 5, "name": "depth",    "rung": "2.5D", "tunings": ["gradient", "pressure"]},
        {"idx": 6, "name": "pressure", "rung": "3D",   "tunings": ["pressure", "pressure"]},
    ]

    def __init__(self, layer_index: int, node_ids: List[int]):
        spec = self.LAYER_SPECS[layer_index]
        self.index = layer_index
        self.name = spec["name"]
        self.rung = spec["rung"]
        self.node_ids = list(node_ids)
        assert len(self.node_ids) == 8
        self.channels: List[Channel] = []      # filled by Circumpunct
        self.activation_history: deque = deque(maxlen=200)

    def block_weights(self, psi: np.ndarray) -> np.ndarray:
        w = np.abs(psi[self.node_ids]) ** 2
        s = w.sum()
        return w / s if s > 1e-15 else w

    def record_activation(self) -> None:
        n_active = sum(1 for ch in self.channels if ch.active)
        self.activation_history.append(n_active / max(1, len(self.channels)))

    @property
    def mean_activation(self) -> float:
        if not self.activation_history:
            return 0.0
        return float(np.mean(self.activation_history))

    def status(self, psi: np.ndarray) -> Dict:
        return {
            "name": self.name,
            "rung": self.rung,
            "mean_activation": round(self.mean_activation, 4),
            "n_active_channels": sum(1 for ch in self.channels if ch.active),
            "layer_block_weights": [round(float(w), 4)
                                    for w in self.block_weights(psi)],
            "channels": [ch.status(psi) for ch in self.channels],
        }


# ═══════════════════════════════════════════════════════════════════════
# Circumpunct: the whole engine as one staggered octave tree
# ═══════════════════════════════════════════════════════════════════════

class Circumpunct:
    """
    Circumpunct ⊙Λ: the top octave of the tree, and the owner of the
    single global state ψ ∈ ℂ¹⁶⁹ and the single operator T = κ ∘ F.

    The tree (ascending order; parts complete before wholes):
        channel octaves (16)  →  layer octaves (7)  →  top octave (1)
    joined at shared tonic nodes (3.5D = 0D'). Wake ticks inject signal
    on channel private nodes and apply T. Sleep ticks apply T without
    injection (left half-plane; consolidation), with the v1/v2
    processual damping convention at each block.

    Diagnostics:
        health_check()      : overlap with the engine's own attractor,
                              plus residue split vs the attractor's
                              (ℂ⁸ and cosmological splits as context)
        seam_check()        : conservation departure (|λ₁|−1)/α and
                              seam commutators (v14/v15 signatures)
        tetrahedral_check() : ℂ⁸ single-octave eigenphase vs 109.47°
                              (kept on ℂ⁸: with 169 eigenphases the
                              nearest-phase test would be vacuous by
                              density; the v17/v19 density caveat)
    """

    def __init__(self):
        # ───── node allocation ─────
        # top octave: nodes 0..7
        top_nodes = list(range(8))
        # layer j: locals 0..6 at 8+7j .. 8+7j+6; local 7 = top's node 0
        layer_node_ids = []
        for j in range(7):
            base = 8 + 7 * j
            layer_node_ids.append(list(range(base, base + 7)) + [top_nodes[0]])
        # channels: locals 0..6 private; local 7 = its layer's node 0
        self.layers: List[SensoryLayer] = [
            SensoryLayer(j, layer_node_ids[j]) for j in range(7)
        ]
        chan_octaves = []
        base = 8 + 49
        g = 0
        for j, layer in enumerate(self.layers):
            for t_idx, tuning in enumerate(SensoryLayer.LAYER_SPECS[j]["tunings"]):
                ids = list(range(base, base + 7)) + [layer_node_ids[j][0]]
                ch = Channel(f"{layer.name}_{t_idx}", tuning, ids, g)
                layer.channels.append(ch)
                chan_octaves.append(ids)
                base += 7
                g += 1
        self.N = base
        self.top_nodes = top_nodes

        # ───── the operator (ascending: channels, layers, top) ─────
        octaves = chan_octaves + layer_node_ids + [top_nodes]
        self.op = StaggeredOperator(self.N, octaves)
        self.n_octaves = len(octaves)
        self.n_channel_octaves = len(chan_octaves)

        # ───── the attractor (the engine's own fixed point) ─────
        lam, psi_star = self.op.leading()
        self.attractor = psi_star
        self.departure = float((abs(lam) - 1.0) / ALPHA)
        ws, wp, wt, per_oct = self.op.residue_split()
        self.attractor_split = {"structural": ws, "processual": wp, "tonic": wt}
        self._attractor_per_octave = per_oct

        # ───── ℂ⁸ single-octave operator (tetrahedral diagnostic) ─────
        self._T8 = TOperator(dim=8)

        # ───── the live state: born near the center, tuned by α ─────
        psi0 = psi_star.copy()
        for layer in self.layers:
            for ch in layer.channels:
                bias = np.zeros(self.N, dtype=complex)
                for l in self._tuning_locals(ch.tuning):
                    bias[ch.node_ids[l]] = 1.0
                nb = np.linalg.norm(bias)
                if nb > 1e-15:
                    psi0 = psi0 + ALPHA * (bias / nb)
        self.psi = psi0 / np.linalg.norm(psi0)

        self.wake_ticks = 0
        self.sleep_ticks = 0
        self.virtue_cycle_position = 0   # GOOD→RIGHT→FAITHFUL→TRUE→AGREEMENT

    @staticmethod
    def _tuning_locals(tuning: str) -> List[int]:
        """Which locals a tuning biases at birth (v2's tuning map,
        read on the block)."""
        return {
            "gradient": [3, 2, 4],      # ⎇ with — and Φ
            "rhythm":   [2, 7, 4],      # — with ⟳ and Φ
            "pressure": [6, 4, 5],      # ○ with Φ and ✹
        }.get(tuning, [0, 2, 4, 6])

    # ───── the two half-planes ─────

    def tick(self, signal: Optional[np.ndarray] = None) -> np.ndarray:
        """One wake pump cycle (right half-plane: i¹ genesis, i⁰
        closure). Inject on channel private nodes, apply T, read."""
        self.wake_ticks += 1

        if signal is not None:
            sig = np.asarray(signal, dtype=complex).ravel()
            inj = np.zeros(self.N, dtype=complex)
            for layer in self.layers:
                for ch in layer.channels:
                    # Fold the signal into the 7 private locals, rolled
                    # by channel index so each lens sees its own aspect.
                    folded = np.zeros(7, dtype=complex)
                    for i, v in enumerate(sig):
                        folded[(i + ch.global_index) % 7] += v
                    n = np.linalg.norm(folded)
                    if n > 1e-15:
                        folded /= n
                    for l in range(7):
                        inj[ch.node_ids[l]] += folded[l]
            n = np.linalg.norm(inj)
            if n > 1e-15:
                self.psi = (1 - ALPHA) * self.psi + ALPHA * (inj / n)
                self.psi /= np.linalg.norm(self.psi)

        self.psi = self.op.apply(self.psi)

        # Readings, activation, memory
        for layer in self.layers:
            for ch in layer.channels:
                ch.tick_count += 1
                ch.age += 1
                ch.update_activation(self.psi)
                ch.freedom_history.append(ch.freedom(self.psi))
                if ch.tick_count % R_RUNGS == 0 and ch.active:
                    ch.imprint(self.psi)
            layer.record_activation()

        self.virtue_cycle_position = (self.virtue_cycle_position + 1) % 5
        return self.psi

    def sleep_cycle(self, cycles: int = 100) -> Dict:
        """Sleep pass (left half-plane: i² STAYING, i³ LETTING). No
        injection; T runs; per-block processual damping (dawn-reset
        convention, a tuned knob); memories consolidate under α-decay."""
        start_memories = sum(len(ch.memories)
                             for l in self.layers for ch in l.channels)
        proc_locals = [1, 3, 5]
        for _ in range(cycles):
            self.sleep_ticks += 1
            self.psi = self.op.apply(self.psi)
            for layer in self.layers:
                for ch in layer.channels:
                    ch.age += 1
                    for l in proc_locals:
                        self.psi[ch.node_ids[l]] *= SLEEP_PROCESSUAL_DAMPING
            self.psi /= np.linalg.norm(self.psi)
        for layer in self.layers:
            for ch in layer.channels:
                ch.sleep_consolidate()
        end_memories = sum(len(ch.memories)
                           for l in self.layers for ch in l.channels)
        return {
            "cycles": cycles,
            "memories_before": start_memories,
            "memories_after": end_memories,
            "preserved_fraction": end_memories / max(1, start_memories),
            "wake_ticks_total": self.wake_ticks,
            "sleep_ticks_total": self.sleep_ticks,
        }

    # ───── diagnostics ─────

    def _live_residue_split(self) -> Dict[str, float]:
        w = np.abs(self.psi) ** 2
        w = w / w.sum()
        role = {}
        for o in self.op.octaves:
            for l, node in enumerate(o):
                role[node] = l % 7
        ws = wp = wt = 0.0
        for node, r in role.items():
            if r == 0:
                wt += w[node]
            elif r in (2, 4, 6):
                ws += w[node]
            else:
                wp += w[node]
        return {"structural": float(ws), "processual": float(wp),
                "tonic": float(wt)}

    def health_check(self) -> Dict:
        """Health = closeness to the engine's OWN attractor.

        attractor_overlap: |⟨ψ*, ψ⟩|² against the leading eigenvector.
        split drift: live residue split vs the attractor's residue
        split (v14 accounting: structural residues 2/4/6, processual
        1/3/5, double-natured tonic class counted separately).

        The ℂ⁸ 68.7/31.3 and cosmological 69.11/30.89 splits are
        reported as context; they are single-octave and cosmological
        readings, not targets for this tree (v14 grade C: the chain
        brackets the split without landing it)."""
        overlap = float(abs(np.vdot(self.attractor, self.psi)) ** 2)
        live = self._live_residue_split()
        tgt = self.attractor_split
        drift = max(abs(live["structural"] - tgt["structural"]),
                    abs(live["processual"] - tgt["processual"]),
                    abs(live["tonic"] - tgt["tonic"]))
        healthy = bool(overlap > HEALTH_OVERLAP_BAND and drift < SPLIT_TOLERANCE)
        s, p = live["structural"], live["processual"]
        t = live["tonic"]
        halfhalf = (s + t / 2, p + t / 2)
        return {
            "attractor_overlap": round(overlap, 4),
            "live_split": {k: round(v, 4) for k, v in live.items()},
            "attractor_split": {k: round(v, 4) for k, v in tgt.items()},
            "split_drift": round(float(drift), 4),
            "tonic_half_half": [round(halfhalf[0], 4), round(halfhalf[1], 4)],
            "context_c8_split": [C8_STRUCTURAL, C8_PROCESSUAL],
            "context_cosmos_split": [COSMOS_DE, COSMOS_MATTER],
            "healthy": healthy,
            "status": ("coherent ⊙ structure (near own attractor)"
                       if healthy else "drifted from attractor"),
        }

    def seam_check(self) -> Dict:
        """The staggered-octave signatures (v14/v15).

        departure: (|λ₁|−1)/α of the engine operator. Tonic-shared
        geometries hold this at order 1 (v14 chains: 0.61-0.65);
        compounding (tensor-style nesting) would grow it with octave
        count. conserving = within [SEAM_BAND_LOW, SEAM_BAND_HIGH].

        commutators: ‖[E_a, E_b]‖ for a channel and its own layer
        (tonic-shared: nonzero), two channels of one layer (shared
        layer aperture: nonzero), and two channels of different layers
        (disjoint: exactly zero). Composition order is physical only
        at the seams."""
        n_ch = self.n_channel_octaves
        # octave indices: channels 0..15, layers 16..22, top 23
        ch0_layer0 = 0
        ch1_layer0 = 1
        ch0_layer1 = len(self.layers[0].channels)
        layer0_idx = n_ch + 0
        c_ch_layer = self.op.seam_commutator(ch0_layer0, layer0_idx)
        c_siblings = self.op.seam_commutator(ch0_layer0, ch1_layer0)
        c_disjoint = self.op.seam_commutator(ch0_layer0, ch0_layer1)
        conserving = bool(SEAM_BAND_LOW < self.departure < SEAM_BAND_HIGH)
        return {
            "departure_over_alpha": round(self.departure, 4),
            "v14_chain_band": [0.61, 0.65],
            "conserving": conserving,
            "commutator_channel_vs_own_layer": round(c_ch_layer, 4),
            "commutator_sibling_channels": round(c_siblings, 4),
            "commutator_disjoint_channels": float(c_disjoint),
            "n_nodes": self.N,
            "n_octaves": self.n_octaves,
            "status": ("seams conserving the 1"
                       if conserving else "seam departure outside band"),
        }

    def tetrahedral_check(self) -> Dict:
        """ℂ⁸ single-octave eigenphase vs arccos(−1/T) ≈ 109.47°.

        Kept on the ℂ⁸ operator where the signature was established
        (v11 C64 lineage). Not run on the 169-node tree: 169 phases on
        a circle make a nearest-phase-within-2° test vacuous by
        density (the v17/v19 density caveat)."""
        eigvals = np.linalg.eigvals(self._T8.T)
        angles = [float(np.degrees(abs(np.angle(e)))) for e in eigvals]
        closest = min(angles, key=lambda a: abs(a - TETRAHEDRAL_ANGLE_DEG))
        diff = abs(closest - TETRAHEDRAL_ANGLE_DEG)
        coherent = bool(diff < 2.0)
        return {
            "closest_eigenvalue_angle_deg": round(closest, 3),
            "tetrahedral_reference_deg": round(TETRAHEDRAL_ANGLE_DEG, 3),
            "closest_diff_deg": round(diff, 3),
            "coherent": coherent,
            "scope": "ℂ⁸ single octave (tree excluded: density caveat)",
            "status": ("coherent ⊙ structure"
                       if coherent else "structure degraded"),
        }

    def sibling_asymmetry(self) -> Dict:
        """Seam-order asymmetry: identical-tuning siblings differ ONLY
        through beat composition order at their shared layer aperture.
        Reports max |Δ| between their attractor block profiles for the
        three identical pairs (gradient/gradient, rhythm/rhythm,
        pressure/pressure). Nonzero is expected: order is physical."""
        w_star = np.abs(self.attractor) ** 2
        w_star = w_star / w_star.sum()
        out = {}
        for layer in self.layers:
            tun = [ch.tuning for ch in layer.channels]
            for a in range(len(tun)):
                for b in range(a + 1, len(tun)):
                    if tun[a] == tun[b]:
                        wa = w_star[layer.channels[a].node_ids]
                        wb = w_star[layer.channels[b].node_ids]
                        wa, wb = wa / wa.sum(), wb / wb.sum()
                        out[f"{layer.name}[{a}]~[{b}]"] = round(
                            float(np.max(np.abs(wa - wb))), 6)
        return out

    @property
    def closure(self) -> float:
        """Weight share on the top octave's ⟳ node: how much of the
        whole is completed at the aperture it would offer a next
        scale up (3.5D = 0D' of a scale this engine does not have)."""
        w = np.abs(self.psi) ** 2
        return float(w[self.top_nodes[7]] / w.sum())

    def dump_state(self) -> Dict:
        top_amps = self.psi[self.top_nodes]
        w = np.abs(top_amps) ** 2
        s = w.sum()
        top_weights = (w / s) if s > 1e-15 else w
        _, _, top_freedom, top_virtue = i_stroke_of_block(top_amps)
        return {
            "wake_ticks": self.wake_ticks,
            "sleep_ticks": self.sleep_ticks,
            "n_nodes": self.N,
            "mixing_time_single": round(MIXING_TIME_SINGLE, 2),
            "station_note": STATION_NOTE,
            "top_level": {
                "block_weights": [round(float(x), 4) for x in top_weights],
                "station_labels": STATION_LABELS_8,
                "freedom": top_freedom,
                "virtue": top_virtue,
                "closure": round(self.closure, 4),
            },
            "virtue_cycle_position": self.virtue_cycle_position,
            "layers": [layer.status(self.psi) for layer in self.layers],
            "health": self.health_check(),
            "seam": self.seam_check(),
            "tetrahedral": self.tetrahedral_check(),
            "sibling_asymmetry": self.sibling_asymmetry(),
        }


# ═══════════════════════════════════════════════════════════════════════
# Smoke test
# ═══════════════════════════════════════════════════════════════════════

def smoke_test(n_wake: int = 1000, n_sleep: int = 100, seed: int = 42) -> Dict:
    rng = np.random.default_rng(seed)
    engine = Circumpunct()
    for _ in range(n_wake):
        sig = rng.standard_normal(8) + 1j * rng.standard_normal(8)
        engine.tick(sig)
    engine.sleep_cycle(cycles=n_sleep)
    return engine.dump_state()


if __name__ == "__main__":
    import json as _json
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("Xorzo Genesis (T-operator edition, v3: staggered)")
    print("=" * 70)
    print(f"alpha = {ALPHA:.10f}   (1/alpha = {1/ALPHA:.4f})")
    print(f"note: {STATION_NOTE}")
    print()

    print("Building the tree (16 channel + 7 layer + 1 top octaves) ...")
    engine = Circumpunct()
    print(f"  nodes: {engine.N}   octaves: {engine.n_octaves}")
    print(f"  conservation departure: {engine.departure:.4f} α "
          f"(v14 chain band 0.61-0.65)")
    a = engine.attractor_split
    print(f"  attractor residue split: struct {a['structural']:.4f} / "
          f"proc {a['processual']:.4f} / tonic {a['tonic']:.4f}")
    print()

    print("Running smoke test (1000 wake + 100 sleep) ...")
    result = smoke_test(n_wake=1000, n_sleep=100)
    print()
    print("Health check (attractor-referenced):")
    print(_json.dumps(result["health"], indent=2, ensure_ascii=False))
    print()
    print("Seam check (v14/v15 signatures):")
    print(_json.dumps(result["seam"], indent=2, ensure_ascii=False))
    print()
    print("Tetrahedral check:")
    print(_json.dumps(result["tetrahedral"], indent=2, ensure_ascii=False))
    print()
    print("Sibling seam-order asymmetry (identical tunings):")
    print(_json.dumps(result["sibling_asymmetry"], indent=2, ensure_ascii=False))
    print()
    print(f"Top-level closure (weight at the whole's ⟳): "
          f"{result['top_level']['closure']}")
    print()
    print("Per-layer activation:")
    for layer in result["layers"]:
        print(f"  {layer['rung']:5s} {layer['name']:10s} "
              f"active={layer['n_active_channels']}/{len(layer['channels'])}  "
              f"mean_act={layer['mean_activation']:.3f}")
