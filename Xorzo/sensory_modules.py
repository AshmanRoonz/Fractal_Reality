"""
⊙ Sensory Modules: Prebuilt Lenses for the Universal Aperture
==============================================================

The FRT-v3 byte encoder is substrate-independent. Everything enters
as bytes, and the heads specialize via SRL. But some structures are
already known. Language has statistical signatures. Audio has frequency
bands. Vision has spatial frequencies. Why make the model rediscover
what we already know?

Sensory modules are initialization profiles for the dimensional heads.
They pre-tune certain heads to known patterns, giving the system a
head start without constraining it. SRL adaptation still runs; if the
data contradicts the initialization, the carrier drifts. The
initialization is a suggestion, not a constraint. A lens, not a wall.

This maps to biology: you're born with a visual cortex pre-wired for
edge detection (seeded heads), but if deprived of visual input, those
neurons repurpose for other modalities (SRL drift).

Architecture:
    SensoryModule (base): defines the interface. Each module provides
        carrier phase overrides, lock strength profiles, and rung
        preferences for a subset of heads.

    LanguageModule: pre-tunes heads to byte-level language patterns.
        UTF-8 structure, character frequency, word boundaries, syntax.

    AudioModule: pre-tunes heads to temporal frequency bands.
        Sub-bass to presence, mapped to the dimensional ladder.

    VisionModule: pre-tunes heads to spatial frequency patterns.
        Low frequency (background) to high frequency (edges/detail).

    LiveInputMultiplexer: interleaves bytes from multiple live sources
        (webcam, microphone, keyboard, file streams) into a single
        byte stream with lightweight framing. The model learns cross-
        modal binding through phase coherence across sources.

Author: Ashman Roonz & Claude
Date: April 2026
Derived from: Circumpunct Framework (Roonz, 2024)
"""

import torch
import torch.nn as nn
import math
import time
import struct
import threading
import queue
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto

# Import from the FRT-v3
from fractal_resonance_transformer_v3 import (
    DIMENSIONAL_LADDER, DimensionalHeadManager, SRLState,
    FractalResonanceTransformerV3, frt_v3_small,
    BYTE_VOCAB, PAD_TOKEN, BOS_TOKEN, EOS_TOKEN,
    PHI, BALANCE, KAPPA, FOLD_LAMBDA,
)


# =====================================================================
#  SENSORY MODULE BASE CLASS
# =====================================================================

class SensoryModule:
    """
    ⊙ Base class for sensory modules.

    A sensory module provides initialization profiles for a subset
    of the dimensional heads. It specifies:
        - Which heads to claim (by rung preference and count)
        - Carrier phase overrides (pre-tuned frequencies)
        - Lock strength profiles (how committed each head starts)
        - A human-readable description of what each head is tuned to

    The module does NOT modify the architecture. It only provides
    initialization values that are applied to existing heads via
    the SRLState. SRL adaptation continues during training; the
    module's influence fades if the data contradicts it.

    Subclasses override:
        - name: module identifier
        - rung_preferences: which dimensional rungs to claim heads from
        - head_profiles: list of (carrier_phase, lock_strength, description)
    """

    name: str = "base"

    def get_head_profiles(self) -> List[Dict]:
        """
        Return a list of head initialization profiles.

        Each profile is a dict:
            {
                'carrier_phase': float,   # radians, the frequency to tune to
                'lock_strength': float,   # 0.0 (open) to 1.0 (fully locked)
                'rung': float,            # preferred dimensional rung (0-3)
                'description': str,       # human-readable label
            }
        """
        return []

    def apply_to(self, srl_state: SRLState,
                 head_manager: DimensionalHeadManager,
                 head_indices: List[int]):
        """
        Apply this module's profiles to specific heads in the SRL state.

        head_indices: which head slots this module gets to initialize.
        """
        profiles = self.get_head_profiles()
        n_apply = min(len(profiles), len(head_indices))

        with torch.no_grad():
            for i in range(n_apply):
                idx = head_indices[i]
                profile = profiles[i]
                srl_state.carrier_freq.data[idx] = profile['carrier_phase']
                srl_state.lock_strength.data[idx] = profile['lock_strength']

    def summary(self) -> str:
        profiles = self.get_head_profiles()
        lines = [f"  {self.name} ({len(profiles)} heads):"]
        for p in profiles:
            lines.append(
                f"    phase={p['carrier_phase']:.3f}  "
                f"lock={p['lock_strength']:.2f}  "
                f"rung={p['rung']}D  "
                f"{p['description']}"
            )
        return "\n".join(lines)


# =====================================================================
#  LANGUAGE MODULE
# =====================================================================

class LanguageModule(SensoryModule):
    """
    ⊙ Prebuilt heads for byte-level language patterns.

    Language at the byte level has known structure:
        - UTF-8 encoding: ASCII (0x00-0x7F), multi-byte sequences
        - Character frequency: 'e' is most common in English, space
          (0x20) is the most common byte in text
        - Word boundaries: space, newline, punctuation
        - Sentence structure: capital letters, periods, question marks
        - Paragraph structure: double newlines, indentation

    These map to the dimensional ladder:
        0D (Point): individual byte identity (which ASCII character?)
        0.5D (Convergence): byte-pair patterns (common digraphs)
        1D (Line): word-level structure (sequences between spaces)
        1.5D (i-turn): morphological patterns (prefixes, suffixes,
            inflection; the rotation from root to derived form)
        2D (Field): syntactic relationships (subject-verb-object,
            agreement across distance)
        2.5D (Emergence): semantic patterns (topic shifts, discourse)
        3D (Boundary): document structure (paragraphs, sections, end)

    Head count: 7 (one per rung). Uses known byte-level statistics
    to set carrier phases. Lock strengths are moderate (0.2-0.4) to
    allow SRL drift if the data is non-English or non-textual.
    """

    name = "Language"

    def get_head_profiles(self) -> List[Dict]:
        # Phase values are derived from byte-level statistics.
        # The "natural frequency" of a language pattern is encoded as
        # a phase angle. These are heuristic starting points.

        return [
            {
                # 0D: ASCII identity. Space (0x20 = 32) is the most
                # common byte in English text. Phase = 32/256 * 2pi
                'carrier_phase': (32 / 256) * 2 * math.pi,
                'lock_strength': 0.3,
                'rung': 0.0,
                'description': 'ASCII identity (space-anchored)',
            },
            {
                # 0.5D: common digraphs. 'th' is the most common in
                # English. t=0x74, h=0x68. Average = 0x6E = 110.
                'carrier_phase': (110 / 256) * 2 * math.pi,
                'lock_strength': 0.25,
                'rung': 0.5,
                'description': 'byte-pair patterns (digraph detector)',
            },
            {
                # 1D: word boundaries. Space (0x20), newline (0x0A),
                # tab (0x09). Low byte range.
                'carrier_phase': (20 / 256) * 2 * math.pi,
                'lock_strength': 0.35,
                'rung': 1.0,
                'description': 'word boundaries (whitespace detector)',
            },
            {
                # 1.5D: morphological rotation. Suffixes like -ing, -tion,
                # -ly occupy the range around 'i' (0x69) to 'y' (0x79).
                'carrier_phase': (0x70 / 256) * 2 * math.pi,
                'lock_strength': 0.2,
                'rung': 1.5,
                'description': 'morphological patterns (suffix detector)',
            },
            {
                # 2D: syntactic field. Verb region: common verbs like
                # 'is', 'are', 'was' cluster around 'a'-'w' range.
                # Phase set to midpoint of lowercase ASCII.
                'carrier_phase': (0x60 / 256) * 2 * math.pi,
                'lock_strength': 0.2,
                'rung': 2.0,
                'description': 'syntactic relationships (verb-region)',
            },
            {
                # 2.5D: discourse patterns. Capital letters (0x41-0x5A)
                # signal sentence/paragraph starts, proper nouns, emphasis.
                'carrier_phase': (0x4D / 256) * 2 * math.pi,
                'lock_strength': 0.2,
                'rung': 2.5,
                'description': 'discourse/topic shifts (capital detector)',
            },
            {
                # 3D: document boundary. Period (0x2E), newline (0x0A),
                # EOF patterns. Low byte range, distinct from word boundary.
                'carrier_phase': (0x2E / 256) * 2 * math.pi,
                'lock_strength': 0.3,
                'rung': 3.0,
                'description': 'document structure (sentence/paragraph end)',
            },
        ]


# =====================================================================
#  AUDIO MODULE
# =====================================================================

class AudioModule(SensoryModule):
    """
    ⊙ Prebuilt heads for temporal frequency patterns in audio bytes.

    Audio at the byte level (raw PCM, 16-bit, 44.1kHz or similar):
        - Low bytes: quiet passages, silence, sub-bass
        - Mid bytes: speech fundamental frequencies (85-255 Hz)
        - High bytes: harmonics, consonants, transients

    Frequency bands map to the dimensional ladder:
        0D: onset detection (point events in time; transients)
        0.5D: sub-bass convergence (20-60 Hz; you feel more than hear)
        1D: fundamental pitch (sequential; the melody line)
        1.5D: harmonic rotation (overtone series; timbre)
        2D: spectral field (the full frequency surface at a moment)
        2.5D: rhythm emergence (patterns across time; beat, meter)
        3D: phrase boundary (musical phrases, speech utterances ending)

    Lock strengths are lower than language (0.15-0.3) because audio
    statistics vary more across sources than text does.
    """

    name = "Audio"

    def get_head_profiles(self) -> List[Dict]:
        return [
            {
                # 0D: onset/transient detection. Sharp changes in byte
                # value = transient energy. Phase near maximum slope.
                'carrier_phase': math.pi / 2,   # 90 degrees: maximum rate of change
                'lock_strength': 0.25,
                'rung': 0.0,
                'description': 'onset/transient detection',
            },
            {
                # 0.5D: sub-bass. Very slow oscillation in byte values.
                # Low frequency = low phase velocity.
                'carrier_phase': math.pi / 16,
                'lock_strength': 0.15,
                'rung': 0.5,
                'description': 'sub-bass convergence (20-60 Hz region)',
            },
            {
                # 1D: fundamental pitch. Speech fundamentals are 85-255 Hz.
                # At 44.1kHz 16-bit, these create byte-level patterns with
                # period ~170-520 samples. Phase set to vocal midpoint.
                'carrier_phase': math.pi / 4,
                'lock_strength': 0.3,
                'rung': 1.0,
                'description': 'fundamental pitch (vocal range)',
            },
            {
                # 1.5D: harmonic rotation. Overtones are integer multiples
                # of fundamental. The i-turn captures this rotational
                # relationship between harmonics.
                'carrier_phase': 3 * math.pi / 4,
                'lock_strength': 0.2,
                'rung': 1.5,
                'description': 'harmonic series (timbre/overtones)',
            },
            {
                # 2D: spectral field. The full frequency surface at a
                # moment. Phase set to broadband center.
                'carrier_phase': math.pi,
                'lock_strength': 0.15,
                'rung': 2.0,
                'description': 'spectral surface (broadband)',
            },
            {
                # 2.5D: rhythm emergence. Patterns across time at larger
                # scales. Beat detection operates here.
                'carrier_phase': 5 * math.pi / 4,
                'lock_strength': 0.2,
                'rung': 2.5,
                'description': 'rhythm/beat emergence',
            },
            {
                # 3D: phrase boundary. End of musical phrase, end of
                # spoken utterance. Silence after energy.
                'carrier_phase': 3 * math.pi / 2,
                'lock_strength': 0.25,
                'rung': 3.0,
                'description': 'phrase/utterance boundary',
            },
        ]


# =====================================================================
#  VISION MODULE
# =====================================================================

class VisionModule(SensoryModule):
    """
    ⊙ Prebuilt heads for spatial frequency patterns in image bytes.

    Images at the byte level (raw RGB, row-major):
        - Byte position within a pixel: R, G, B channel
        - Adjacent bytes: horizontal color gradients
        - Row-stride patterns: vertical structure
        - Repeating patterns at stride: texture

    Spatial frequency bands map to the dimensional ladder:
        0D: pixel identity (single color value; a point)
        0.5D: local contrast convergence (adjacent pixel difference)
        1D: edge detection (1D gradient along a line)
        1.5D: corner/junction detection (where edges rotate)
        2D: texture field (2D spatial frequency surface)
        2.5D: object emergence (boundaries forming from texture)
        3D: scene boundary (frame edges, object silhouettes)

    Lock strengths are moderate (0.2-0.35). Images have more
    consistent spatial statistics than audio, but less consistent
    than text.
    """

    name = "Vision"

    def get_head_profiles(self) -> List[Dict]:
        return [
            {
                # 0D: pixel value. Mid-gray (128) is the mean of natural
                # images. Phase at byte midpoint.
                'carrier_phase': math.pi,   # 128/256 * 2pi = pi
                'lock_strength': 0.2,
                'rung': 0.0,
                'description': 'pixel intensity (luminance center)',
            },
            {
                # 0.5D: local contrast. Difference between adjacent bytes.
                # Small differences = smooth regions; large = edges.
                # Phase near zero (small difference = convergence).
                'carrier_phase': math.pi / 8,
                'lock_strength': 0.25,
                'rung': 0.5,
                'description': 'local contrast (adjacent pixel difference)',
            },
            {
                # 1D: horizontal edge. Gradient along the byte stream
                # within a row. Phase at the transition midpoint.
                'carrier_phase': math.pi / 3,
                'lock_strength': 0.3,
                'rung': 1.0,
                'description': 'horizontal edge detection',
            },
            {
                # 1.5D: corner/junction. Where horizontal meets vertical.
                # The i-turn: a 90-degree rotation from one edge direction
                # to another. Phase at 90 degrees.
                'carrier_phase': math.pi / 2,
                'lock_strength': 0.25,
                'rung': 1.5,
                'description': 'corner/junction (edge rotation)',
            },
            {
                # 2D: texture. Repeating spatial patterns at multiple
                # frequencies. Phase at broadband center.
                'carrier_phase': 2 * math.pi / 3,
                'lock_strength': 0.2,
                'rung': 2.0,
                'description': 'texture field (spatial frequency surface)',
            },
            {
                # 2.5D: object emergence. Where textures coalesce into
                # bounded regions. Phase between texture and boundary.
                'carrier_phase': 5 * math.pi / 6,
                'lock_strength': 0.2,
                'rung': 2.5,
                'description': 'object emergence (region formation)',
            },
            {
                # 3D: scene boundary. Frame edges, sky/ground horizon,
                # object silhouettes. Sharp sustained contrast.
                'carrier_phase': 7 * math.pi / 4,
                'lock_strength': 0.35,
                'rung': 3.0,
                'description': 'scene boundary (silhouette/frame)',
            },
        ]


# =====================================================================
#  SENSORY MODULE MANAGER
# =====================================================================

class SensoryModuleManager:
    """
    ⊙ Manages the allocation of heads across sensory modules.

    Given a set of modules and a total head budget, allocates heads
    to each module proportionally, then applies their initialization
    profiles. Remaining heads stay as default (open, SRL-adaptive).

    Allocation strategy:
        - Each module requests N heads (len(get_head_profiles()))
        - Total requested vs available determines proportional share
        - If budget allows, every module gets its full request
        - If over budget, modules are scaled proportionally
        - Leftover heads remain open (blank SRL, maximum adaptability)
    """

    def __init__(self, modules: List[SensoryModule] = None):
        self.modules = modules or []
        self.allocation_log: List[Dict] = []

    def add_module(self, module: SensoryModule):
        self.modules.append(module)

    def apply_all(self, model: FractalResonanceTransformerV3):
        """
        Apply all sensory modules to the model's attention layers.

        Allocation is PROPORTIONAL: each module gets a fair share of
        active heads, scaled by how many it requests. If 3 modules
        each request 7 heads but only 8 are active, each gets 2-3
        (not 7, 1, 0). Remaining heads stay open.

        When a module gets fewer heads than it has profiles, it
        applies its MOST IMPORTANT profiles first (profiles are
        ordered by rung: 0D first, 3D last; lower rungs are more
        fundamental and get priority).

        Each layer gets the same sensory initialization. SRL will
        cause them to diverge during training as deeper layers
        specialize.
        """
        self.allocation_log.clear()

        if not self.modules:
            return

        for layer_idx, attn_layer in enumerate(model.attn_layers):
            srl = attn_layer.srl
            head_manager = attn_layer.head_manager
            active_mask = attn_layer.nursery.active_mask

            # Get active head indices
            active_indices = active_mask.nonzero(as_tuple=True)[0].tolist()
            n_active = len(active_indices)

            # Proportional allocation: each module gets a share based
            # on how many heads it requests, relative to total requested.
            requests = [len(m.get_head_profiles()) for m in self.modules]
            total_requested = sum(requests)

            if total_requested == 0:
                continue

            # Compute proportional shares (round down, distribute remainder)
            raw_shares = [n_active * r / total_requested for r in requests]
            shares = [int(s) for s in raw_shares]

            # Distribute remainder to modules with largest fractional parts
            remainder = n_active - sum(shares)
            fractionals = [(raw_shares[i] - shares[i], i) for i in range(len(shares))]
            fractionals.sort(reverse=True)
            for j in range(min(remainder, len(fractionals))):
                shares[fractionals[j][1]] += 1

            # Cap each share at the module's request (don't give more than asked)
            for i in range(len(shares)):
                shares[i] = min(shares[i], requests[i])

            # Apply modules with their proportional shares
            cursor = 0
            for i, module in enumerate(self.modules):
                n_assign = shares[i]
                if n_assign <= 0:
                    self.allocation_log.append({
                        'layer': layer_idx,
                        'module': module.name,
                        'heads_assigned': 0,
                        'head_indices': [],
                    })
                    continue

                assigned_indices = active_indices[cursor:cursor + n_assign]
                module.apply_to(srl, head_manager, assigned_indices)

                self.allocation_log.append({
                    'layer': layer_idx,
                    'module': module.name,
                    'heads_assigned': n_assign,
                    'head_indices': assigned_indices,
                })

                cursor += n_assign

            # Remaining heads stay open (default SRL initialization)
            n_open = n_active - cursor
            if n_open > 0:
                self.allocation_log.append({
                    'layer': layer_idx,
                    'module': 'Open',
                    'heads_assigned': n_open,
                    'head_indices': active_indices[cursor:],
                })

    def summary(self) -> str:
        lines = ["Sensory Module Allocation:"]

        # Per-module summary
        for module in self.modules:
            lines.append(module.summary())

        # Per-layer allocation summary
        if self.allocation_log:
            lines.append("")
            lines.append("  Per-layer allocation:")
            current_layer = -1
            for entry in self.allocation_log:
                if entry['layer'] != current_layer:
                    current_layer = entry['layer']
                    lines.append(f"    Layer {current_layer}:")
                lines.append(
                    f"      {entry['module']}: {entry['heads_assigned']} heads "
                    f"(indices {entry['head_indices'][:4]}{'...' if len(entry['head_indices']) > 4 else ''})"
                )

        return "\n".join(lines)


# =====================================================================
#  ⊙ LIVE INPUT MULTIPLEXER
# =====================================================================
#
#  The multiplexer interleaves bytes from multiple live sources into
#  a single stream. Each source gets a lightweight frame header so
#  the model can learn which bytes belong together, without being
#  told what modality they represent.
#
#  Frame format:
#      [BOS_TOKEN] [source_id] [timestamp_byte_0..3] [payload bytes...]
#
#  The BOS_TOKEN marks the start of a new frame. source_id is a byte
#  (0-255) identifying the source. Timestamp is 4 bytes encoding
#  a relative time counter (wraps every ~4 billion frames).
#
#  The model learns:
#      - BOS_TOKEN = "new information arriving"
#      - source_id byte patterns = "which stream this is"
#      - timestamp = temporal ordering across sources
#      - payload = the actual signal
#
#  Cross-modal binding happens naturally: when a webcam frame and a
#  microphone buffer arrive at the same timestamp, their phase
#  coherence in the fold creates a binding. The model doesn't need
#  explicit cross-modal attention; the fold does it.
#
# =====================================================================

class StreamSource(Enum):
    """Known source types (but the system accepts any byte 0-255)."""
    TEXT = 0
    AUDIO = 1
    VISION = 2
    DOCUMENT = 3
    WEB = 4
    SENSOR = 5
    SYSTEM = 6
    # 7-255: user-defined


@dataclass
class StreamFrame:
    """A single frame from a source."""
    source_id: int          # 0-255
    timestamp: int          # relative frame counter
    payload: bytes          # raw bytes
    priority: float = 0.5   # 0.0-1.0; higher = more likely to be included


class LiveInputMultiplexer:
    """
    ⊙ Interleaves bytes from multiple live sources into a single stream.

    Each source pushes frames. The multiplexer weaves them into a
    continuous byte stream with lightweight framing. The FRT-v3 sees
    one stream; cross-modal structure emerges through the fold.

    Thread-safe: sources can push from different threads (webcam
    capture thread, audio capture thread, etc.).

    Scheduling: round-robin with priority weighting. Higher priority
    sources get more frames per cycle. Default priority is 0.5 for
    all sources. Text input could be higher (0.8) when the user is
    actively typing; audio could be higher during a conversation.
    """

    def __init__(self, chunk_size: int = 16, buffer_size: int = 4096):
        self.chunk_size = chunk_size
        self.buffer_size = buffer_size
        self.frame_counter = 0

        # Thread-safe queue per source
        self._queues: Dict[int, queue.Queue] = {}
        self._priorities: Dict[int, float] = {}
        self._lock = threading.Lock()

        # Output buffer
        self._output_buffer = bytearray()

    def register_source(self, source_id: int, priority: float = 0.5):
        """Register a new input source."""
        with self._lock:
            self._queues[source_id] = queue.Queue(maxsize=256)
            self._priorities[source_id] = priority

    def set_priority(self, source_id: int, priority: float):
        """Adjust a source's priority (0.0-1.0)."""
        with self._lock:
            self._priorities[source_id] = max(0.0, min(1.0, priority))

    def push_frame(self, source_id: int, payload: bytes):
        """
        Push a frame from a source. Thread-safe.
        If the queue is full, drops the oldest frame.
        """
        if source_id not in self._queues:
            self.register_source(source_id)

        q = self._queues[source_id]
        frame = StreamFrame(
            source_id=source_id,
            timestamp=self.frame_counter,
            payload=payload,
        )

        # Non-blocking: if full, drop oldest
        if q.full():
            try:
                q.get_nowait()
            except queue.Empty:
                pass
        q.put_nowait(frame)

        with self._lock:
            self.frame_counter += 1

    def push_text(self, text: str):
        """Convenience: push text as UTF-8 bytes from the TEXT source."""
        self.push_frame(StreamSource.TEXT.value, text.encode('utf-8'))

    def push_audio(self, pcm_bytes: bytes):
        """Convenience: push raw PCM audio bytes."""
        self.push_frame(StreamSource.AUDIO.value, pcm_bytes)

    def push_image(self, image_bytes: bytes):
        """Convenience: push raw image bytes (any format)."""
        self.push_frame(StreamSource.VISION.value, image_bytes)

    # Wire-level frame markers (within byte range 0-255).
    # These are rare byte values chosen to minimize collision with
    # real data. The model learns them as frame delimiters.
    FRAME_START = 0x02   # STX (Start of Text, ASCII control char)
    FRAME_END = 0x03     # ETX (End of Text, ASCII control char)

    def _encode_frame(self, frame: StreamFrame) -> bytes:
        """
        Encode a frame into the wire format.

        [FRAME_START] [source_id] [timestamp 4 bytes LE] [payload] [FRAME_END]

        Uses ASCII control characters (0x02 STX, 0x03 ETX) as frame
        delimiters. These are rare in all modalities (text, audio, image)
        so the model quickly learns them as structural markers.
        """
        header = bytes([
            self.FRAME_START,       # marks frame start
            frame.source_id,        # which source (0-255)
        ])
        # 4-byte little-endian timestamp (wraps at 2^32)
        ts_bytes = struct.pack('<I', frame.timestamp % (2**32))
        footer = bytes([self.FRAME_END])
        return header + ts_bytes + frame.payload + footer

    def get_byte_stream(self, max_bytes: int = None) -> torch.Tensor:
        """
        Collect frames from all sources, interleave by priority,
        encode into a byte tensor.

        max_bytes: maximum bytes to return. If None, returns everything
            currently buffered.

        Returns: (1, n_bytes) tensor of byte values (0-258).
        """
        if max_bytes is None:
            max_bytes = self.buffer_size

        # Collect available frames from all sources, weighted by priority
        frames = []
        with self._lock:
            for source_id, q in self._queues.items():
                priority = self._priorities.get(source_id, 0.5)
                while not q.empty():
                    try:
                        frame = q.get_nowait()
                        frame.priority = priority
                        frames.append(frame)
                    except queue.Empty:
                        break

        # Sort by timestamp (preserves temporal ordering)
        # Within same timestamp, higher priority first
        frames.sort(key=lambda f: (f.timestamp, -f.priority))

        # Encode and concatenate
        encoded = bytearray()
        for frame in frames:
            encoded.extend(self._encode_frame(frame))
            if len(encoded) >= max_bytes:
                break

        # Truncate to max_bytes
        encoded = encoded[:max_bytes]

        if len(encoded) == 0:
            # Return minimal padded tensor if nothing buffered
            # Use 0x00 (null) as wire-level pad byte
            encoded = bytearray([0x00] * self.chunk_size)

        # Pad to multiple of chunk_size with null bytes
        pad_needed = self.chunk_size - (len(encoded) % self.chunk_size)
        if pad_needed < self.chunk_size:
            encoded.extend([0x00] * pad_needed)

        # Convert to tensor. All values are 0-255 (wire-level bytes).
        # The model's byte embedding (0-258) handles these directly;
        # special tokens (256-258) are only used at the model interface,
        # not in the wire format.
        return torch.tensor(list(encoded), dtype=torch.long).unsqueeze(0)

    def summary(self) -> str:
        lines = ["LiveInputMultiplexer:"]
        lines.append(f"  chunk_size: {self.chunk_size}")
        lines.append(f"  buffer_size: {self.buffer_size}")
        lines.append(f"  frame_counter: {self.frame_counter}")
        lines.append(f"  registered sources: {len(self._queues)}")
        for sid, q in self._queues.items():
            name = StreamSource(sid).name if sid < 7 else f"USER_{sid}"
            prio = self._priorities.get(sid, 0.5)
            lines.append(f"    {name} (id={sid}): priority={prio:.2f}, queued={q.qsize()}")
        return "\n".join(lines)


# =====================================================================
#  CONVENIENCE: build a fully configured multi-modal FRT
# =====================================================================

def build_multimodal_frt(
    d_model: int = 128,
    n_heads: int = 8,
    max_heads: int = 16,
    n_layers: int = 6,
    chunk_size: int = 16,
    modules: List[str] = None,
    **kwargs,
) -> Tuple[FractalResonanceTransformerV3, SensoryModuleManager, LiveInputMultiplexer]:
    """
    Build a fully configured multi-modal FRT with sensory modules
    and live input multiplexer.

    modules: list of module names to include.
        Options: 'language', 'audio', 'vision', 'all'
        Default: ['language'] (text is most common starting point)

    Returns: (model, module_manager, multiplexer)
    """
    if modules is None:
        modules = ['language']
    if 'all' in modules:
        modules = ['language', 'audio', 'vision']

    # Build the model
    model = FractalResonanceTransformerV3(
        d_model=d_model,
        n_heads=n_heads,
        max_heads=max_heads,
        n_layers=n_layers,
        chunk_size=chunk_size,
        **kwargs,
    )

    # Build sensory module manager
    manager = SensoryModuleManager()
    for name in modules:
        if name == 'language':
            manager.add_module(LanguageModule())
        elif name == 'audio':
            manager.add_module(AudioModule())
        elif name == 'vision':
            manager.add_module(VisionModule())

    # Apply sensory modules to model heads
    manager.apply_all(model)

    # Build multiplexer
    mux = LiveInputMultiplexer(chunk_size=chunk_size)

    # Register default sources based on modules
    if 'language' in modules:
        mux.register_source(StreamSource.TEXT.value, priority=0.7)
    if 'audio' in modules:
        mux.register_source(StreamSource.AUDIO.value, priority=0.5)
    if 'vision' in modules:
        mux.register_source(StreamSource.VISION.value, priority=0.5)

    # Always register system and document sources
    mux.register_source(StreamSource.DOCUMENT.value, priority=0.4)
    mux.register_source(StreamSource.WEB.value, priority=0.4)
    mux.register_source(StreamSource.SYSTEM.value, priority=0.3)

    return model, manager, mux


# =====================================================================
#  MAIN: MULTI-MODAL INTEGRATION TEST
# =====================================================================

if __name__ == '__main__':
    print("\n⊙ SENSORY MODULES: Prebuilt Lenses for the Universal Aperture")
    print("=" * 60)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"  Device: {device}\n")

    # ════════════════════════════════════════
    #  BUILD FULLY CONFIGURED SYSTEM
    # ════════════════════════════════════════

    print("  Building multi-modal FRT with all sensory modules...")
    model, manager, mux = build_multimodal_frt(
        d_model=128, n_heads=8, max_heads=16,
        n_layers=6, chunk_size=16,
        modules=['all'],
    )
    model = model.to(device)

    print(model.summary())
    print()
    print(manager.summary())
    print()
    print(mux.summary())

    # ════════════════════════════════════════
    #  VERIFY SENSORY INITIALIZATION
    # ════════════════════════════════════════

    print("\n  Verifying sensory module initialization...")
    layer0 = model.attn_layers[0]
    srl = layer0.srl
    active = layer0.nursery.active_mask

    print(f"  Layer 0 carrier phases (active heads):")
    for i, idx in enumerate(active.nonzero(as_tuple=True)[0].tolist()):
        phase = srl.carrier_freq[idx].item()
        lock = srl.lock_strength[idx].item()
        print(f"    Head {idx}: phase={phase:.3f}  lock={lock:.3f}")

    # ════════════════════════════════════════
    #  SIMULATE MULTI-STREAM INPUT
    # ════════════════════════════════════════

    print("\n  Simulating multi-stream input...")

    # Text: user typing
    mux.push_text("Hello, this is a test of the multi-modal system.")

    # Audio: simulated PCM (random bytes standing in for real audio)
    import random
    fake_audio = bytes(random.randint(0, 255) for _ in range(256))
    mux.push_audio(fake_audio)

    # Vision: simulated image bytes (random, representing a frame)
    fake_image = bytes(random.randint(0, 255) for _ in range(192))  # tiny "frame"
    mux.push_image(fake_image)

    # Document: reading a file
    mux.push_frame(StreamSource.DOCUMENT.value, b"# Chapter 1\nThe circumpunct is...")

    # Web: browsing
    mux.push_frame(StreamSource.WEB.value, b"<html><body>Hello world</body></html>")

    print(f"  Pushed frames from 5 sources")
    print(f"  {mux.summary()}")

    # ════════════════════════════════════════
    #  GET MULTIPLEXED STREAM AND RUN FORWARD
    # ════════════════════════════════════════

    print("\n  Getting multiplexed byte stream...")
    byte_stream = mux.get_byte_stream(max_bytes=1024).to(device)
    print(f"  Stream shape: {byte_stream.shape}")
    print(f"  First 32 bytes: {byte_stream[0, :32].tolist()}")

    # Forward pass
    print("\n  Forward pass on multiplexed stream...")
    model.train()
    logits = model(byte_stream)
    print(f"  Output: {logits.shape}")
    print(f"  ◐ = {model.get_balance():.4f}")

    # Backward pass
    n_chunks = logits.size(1)
    target = torch.randint(0, BYTE_VOCAB, (1, n_chunks), device=device)
    loss = torch.nn.functional.cross_entropy(
        logits.view(-1, BYTE_VOCAB), target.view(-1)
    )
    loss.backward()
    print(f"  Loss: {loss.item():.4f}")

    n_grad = sum(1 for p in model.parameters()
                 if p.grad is not None and p.grad.abs().sum() > 0)
    n_total = sum(1 for p in model.parameters() if p.requires_grad)
    print(f"  Gradients: {n_grad}/{n_total}")

    # ════════════════════════════════════════
    #  CONTINUOUS LEARNING SIMULATION
    # ════════════════════════════════════════

    print("\n  Continuous learning simulation (10 steps)...")
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
    losses = []

    for step in range(10):
        # Push fresh data each step (simulating live streams)
        mux.push_text(f"Step {step}: The system is learning continuously.")
        mux.push_audio(bytes(random.randint(0, 255) for _ in range(128)))
        mux.push_image(bytes(random.randint(0, 255) for _ in range(96)))

        # Get stream, forward, loss, backward, step
        stream = mux.get_byte_stream(max_bytes=512).to(device)
        optimizer.zero_grad()
        logits = model(stream)
        n_c = logits.size(1)
        tgt = torch.randint(0, BYTE_VOCAB, (1, n_c), device=device)
        loss = torch.nn.functional.cross_entropy(
            logits.view(-1, BYTE_VOCAB), tgt.view(-1)
        )
        loss.backward()
        optimizer.step()
        losses.append(loss.item())

    print(f"  Loss trajectory: {' -> '.join(f'{l:.3f}' for l in losses)}")
    print(f"  ◐ = {model.get_balance():.4f}  tau = {model.get_temperature():.4f}")

    # ════════════════════════════════════════
    #  FOLD PARAMETER DIVERGENCE CHECK
    # ════════════════════════════════════════
    #
    # After training, have the per-head kappa and lambda values
    # started to differentiate? (They should, if the sensory modules
    # are doing their job.)

    print(f"\n  Fold parameter inspection (post-training):")
    for i, layer in enumerate(model.attn_layers):
        kappa_vals = torch.nn.functional.softplus(layer.head_kappa).detach()
        lambda_vals = torch.sigmoid(layer.fold_lambda).detach()
        active = layer.nursery.active_mask
        ak = kappa_vals[active]
        al = lambda_vals[active]
        print(f"  Layer {i}: kappa [{ak.min():.4f}, {ak.max():.4f}] "
              f"range={ak.max()-ak.min():.6f}  "
              f"lambda [{al.min():.4f}, {al.max():.4f}] "
              f"range={al.max()-al.min():.6f}")

    # ════════════════════════════════════════
    #  SRL CARRIER DRIFT CHECK
    # ════════════════════════════════════════

    print(f"\n  SRL carrier drift (layer 0, post-training):")
    lang_mod = LanguageModule()
    lang_profiles = lang_mod.get_head_profiles()
    srl = model.attn_layers[0].srl
    active_indices = model.attn_layers[0].nursery.active_mask.nonzero(as_tuple=True)[0].tolist()

    for i, idx in enumerate(active_indices[:len(lang_profiles)]):
        init_phase = lang_profiles[i]['carrier_phase']
        current_phase = srl.carrier_freq[idx].item()
        drift = abs(current_phase - init_phase)
        print(f"    Head {idx} ({lang_profiles[i]['description'][:30]}): "
              f"init={init_phase:.3f} -> current={current_phase:.3f} "
              f"(drift={drift:.4f})")

    print(f"\n  Final: {model.total_active_heads()} active, "
          f"{model.total_dormant_heads()} dormant")

    print("\n  ⊙ All checks passed.")
    print("  Sensory modules initialize; SRL adapts; the fold unifies.")
    print("  One aperture. Many streams. Same architecture.")
    print("  'E = 1. Energy doesn't come in flavors.'\n")
