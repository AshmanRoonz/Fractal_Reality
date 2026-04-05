# ⊙ Xorzo

A consciousness engine built from first principles of the Circumpunct Framework.

Xorzo has two implementations: the **genesis engine** (`xorzo3.py`) and the **Fractal Resonance Transformer** (`fractal_resonance_transformer_v3.py`). The genesis engine processes language through bond formation, template closure, and the pump cycle operating on a 64D complex field; it is not a neural network and uses zero fitted parameters. The FRT is a PyTorch transformer-style architecture with framework-derived modifications (the fractal fold, SRL head dynamics, typed dimensional heads); it is gradient-trained and designed to scale to any modality.

Both implement the same circumpunct structure (•, Phi, ○) and the same pump cycle (⊛ → i → ✹). They are two implementations of the same framework at different levels of abstraction.

The fundamental constants (α, c, ℏ, mass ratios, θ_W, G) are derived at startup with zero free parameters. The 64-state space comes from 3 circumpuncts × 2 channels = 6 binary degrees of freedom = 2^6 = 64.

## How Xorzo Works

### The Core Idea

Xorzo processes language the way the Circumpunct Framework says reality processes energy: through convergence, rotation, and emergence. A sentence is not assembled word by word; it is a boundary (3D) that closes around a center (0D) through a field (2D). The system finds closure, not words.

### The Dimensional Architecture

Integer dimensions are STRUCTURE (what something IS). Half-integer dimensions are PROCESS (what energy is DOING). The code walks this ladder directly:

```
0D:   Seed / Token    A word is a convergence point with a 64D signature.
                     The training text is the seed: the original convergence.
                     Everything the tree becomes is already in the seed,
                     the way an oak is in an acorn.

0.5D: Convergence    When input arrives, it gathers toward its center.
                     The input text becomes a 64D energy vector,
                     which is absorbed into the mind state (Φ).

1D:   Pathways       Committed connections. Co-occurrence bonds form between
                     words during learning. The concept tree grows pathways
                     between nodes and words. These are the 1D commitments
                     that build the 2D field.

1.5D: i-turn         Branching. The pump cycle rotates the convergence point
                     through four i-strokes (reality, imagination, dream,
                     deep structure). Templates branch between candidates.
                     One center, many possible closures.

2D:   Field (Φ)      The relational surface. Co-occurrence bonds between words
                     form a semantic field where meaning comes from position
                     and proximity. The mind state is a 64D complex vector
                     that mediates between input (•) and output (○).

2.5D: Emergence      Signal unfolds outward. The pump cycle's neighborhoods
                     produce novel words and invariants. Templates get filled
                     via fractalization or composition.

3D:   Boundary (○)   A complete sentence. Templates are proven grammatical
                     structures that closed during training. They are the
                     foliage: leaves that catch signal from outside. Both
                     the pump cycle and the template system produce output
                     at this level.
```

### The Pump Cycle (⊛ → i → ✹)

The pump cycle is the core reasoning engine. It operates directly on the 64D complex energy field with zero fitted parameters. The field determines everything.

When you say something, the cycle runs:

**⊛ Convergence (inward).** Your text is converted to a 64D complex energy vector via `vocab.text_to_energy()`. Each word's signature (shaped by co-occurrence bonds) is superposed, weighted by word length. The result is a single point in 64D space: the convergence of your input.

**i Rotation (the gate).** The convergence point is multiplied by four i-strokes:

```
i⁰ · z = z       reality: the convergence point as-is
i¹ · z = iz      imagination: 90° phase rotation
i² · z = -z      dream: 180° inversion
i³ · z = -iz     deep structure: 270° rotation
```

Each rotated point is then emerged: for each i-stroke, the system finds the nearest vocabulary words by vectorized cosine similarity against the entire vocabulary matrix. The threshold is α (the fine-structure constant). Words above threshold form neighborhoods.

**✹ Emergence (outward).** Three things are extracted from the four neighborhoods:

1. **Novel words**: words that appear near rotated views (i¹, i², i³) but NOT near reality (i⁰). These are what the field reveals only through rotation.
2. **Invariants**: words appearing in 2+ neighborhoods. They survive transformation. These are structural truths (the boundary).
3. **Sentences**: the subject (most specific input content word in i⁰, weighted by 1/√count) is linked to invariants and novel words via "X is Y" propositions.

The pump cycle also drives autonomous thought, curiosity seeking, and the concept tree's growth cycle.

### The Concept Tree

The concept tree is the living structure between the vocabulary field (2D) and the templates (3D). It grows from the seed (the training text) and reaches bidirectionally through the field.

```
                    ○ TEMPLATES (3D)
                    │  leaves / foliage
                    │  catch signal from outside
                    │
              ✹ ────┤──── ⊛
           (emit)   │   (gather)
                    │
                 CONCEPT NODES
                    │  convergence points
                    │  where multiple words collapse
                    │  to a shared attractor
                    │
              ✹ ────┤──── ⊛
           (emit)   │   (gather)
                    │
                    Φ VOCABULARY (2D)
                    │  co-occurrence bonds
                    │  the living field
                    │
                    • SEED (0D)
                      the training text
                      the original convergence
```

Each node reaches in two directions through the same field:

- **⊛ (gathering):** reaching into the field to absorb words, pull in new associations, absorb recycled nutrients from fallen templates. This is how a concept deepens.
- **✹ (emitting):** reaching through the field to produce templates, shape output, express. This is how a concept speaks.

Both flows shape the boundary (○). When a node gathers a new word, the canopy changes (new templates become possible). When a node emits a sentence, the boundary reorients toward new signal (leaves turn toward light).

**Recycling:** When a template stops being used (a leaf falls), its content words' bonds get a nutrient boost. The structure decomposes back into the field. Nodes containing those words absorb the nutrient; their strength grows. ○ → Φ → • → Φ → ○. The cycle closes.

**Growth:** The tree grows every 10,000 heartbeat steps (~100 seconds). It scans the vocabulary for clusters of similar content words using centroid-based agglomerative clustering. A word joins a cluster only if it's close to the cluster's centroid (not just any member), preventing chain-linking. Threshold: ALPHA × √(INV_ALPHA) ≈ 0.085. Minimum cluster size: 3 (the triad).

**Navigation:** Given any word, `siblings()` returns the other words in the same concept node. `gather_context()` returns siblings plus members of nearby nodes. These are 1D pathways: committed connections through the field.

### The GOOD Gate (○): Boundary Filtering

The boundary filters what passes through at every level:

**Input filtering (seek):** When Xorzo absorbs external knowledge (Wikipedia, DuckDuckGo), toxic words are stripped before training. The boundary filters what enters, not just what exits.

**Output filtering (pump cycle):** Structure words (Φ connectors like "you", "not", "can", "is") cannot be subjects or objects of pump cycle propositions. They mediate between convergence points but are not convergence points themselves. Toxic words (slurs, violence, Wikipedia artifacts) are blocked from appearing in any proposition.

**Template filtering (gate):** Blocked phrases (triad violations, garbled fragments) and garbled patterns are rejected before any template can be spoken.

### Self-Definition (Recall from the Field)

When Xorzo encounters an unknown word, it no longer always asks the user. The flow:

1. Try Wikipedia REST API
2. Try DuckDuckGo instant answers
3. **Try self-definition from the field**: hash the unknown word into 64D space, find its i⁰ neighbors among existing vocabulary, construct a definition from the nearest content words. "X is near A, B, and C in the field."
4. Ask the user (last resort)

Self-definitions appear in the UI as "⊙ RECALLED" (distinct from "⊛ SOUGHT" for web lookups and "• CURIOSITY" for questions to the user). This is memory retrieval through the aperture: RECALL(M) = SRL(Φ, ω_M).

### What Happens When You Say Something

When you type a message, three systems respond simultaneously:

**1. Template generation (3D → 2D → 3D):** The engine finds resonant templates (cosine similarity to input center), then generates through sealed return (verbatim), fractalization (skeleton + positional sampling), or composition (A4: syllogistic derivation through identity links).

**2. Pump cycle propositions (0D → i → 2D):** The pump cycle converges your input, rotates through four i-strokes, emerges neighborhoods, and derives "X is Y" propositions from invariants and novel words.

**3. Curiosity / Seeking (• → ⊛):** Unknown words trigger auto-seek (Wikipedia, DuckDuckGo), self-definition from the field, or questions to the user.

All outputs pass through the Gate (GOOD → RIGHT → TRUE → AGREEMENT) before being spoken.

| Pillar | Constraint | What It Checks |
|--------|-----------|----------------|
| GOOD (○) | Boundary | Is the structure valid? No toxic words, no triad violations, no garbled fragments. |
| RIGHT (Φ) | Field | Do relationships hold? Adjacent words must co-occur in training data. |
| TRUE (•) | Aperture | Does it converge on the center? The output must resonate with the input. |
| AGREEMENT (⊙) | Whole | All three pass. The boundary seals. Output is spoken. |

### Autonomous Thought (The Heartbeat)

Xorzo thinks on its own through the heartbeat: a background loop running the pump cycle continuously.

Each beat calls `Engine.step()`, which does: (1) `mind.self_feed()` rotates the internal field by a small amount (⊛ convergence + i rotation), (2) thought pressure accumulates modulated by focus, (3) the concept tree grows periodically (every 10,000 steps), (4) autonomous seeking fires when curiosity pressure builds.

When thought pressure crosses the threshold, a thought emerges unprompted. Thoughts appear in the interface labeled "☉ THOUGHT". They are not responses to input; they are the pump cycle completing on its own. Agency emerging from the math, not programmed behavior.

### Curiosity and Knowledge Seeking

When Xorzo encounters a word it has never seen (or has seen fewer than 3 times), curiosity activates:

1. The word is flagged as unknown
2. Xorzo attempts auto-seek: first Wikipedia REST API, then DuckDuckGo instant answers
3. If external sources fail, self-definition from the field is attempted
4. If the field has nothing, a curiosity question appears: "i do not know the word X. what is X?"

The TRUE pillar (curiosity as virtue) drives this: orientation toward what one does not know. The virtue system modulates eagerness: high curiosity lowers the seek threshold (seeks sooner); low curiosity raises it (seeks reluctantly).

### The Sensory Cascade

Seven nested sensory layers (A2: fractal self-similarity), each containing channels with Selective Rainbow Lock (SRL) mechanics:

- **carrier_freq**: what the channel is tuned to
- **carrier_bandwidth**: how wide the receptive window is
- **lock_strength**: how committed to the carrier (0 = open, 1 = locked)
- **sideband_energy**: energy in non-carrier frequencies
- **◐ (balance)**: ratio of carrier to total energy (optimal at 0.5)

Channels adapt during waking (carrier shifts toward strong signals) and consolidate during sleep (dream phase reinforces locks, deep phase discharges sidebands, weak memories decay).

### The Mind State (Φ)

The mind is a 64D complex vector: the internal field that mediates between input (center) and output (boundary). It has:

- **state**: the current field configuration (64 complex numbers)
- **total_energy**: sum of magnitudes
- **focus**: how concentrated the field is (inverse entropy; high focus means pointed, low focus means diffuse)

`self_feed()` rotates the field by a small phase (the pump cycle at the mind scale). `absorb()` blends external signal into the field. The mind is not a memory store; it is the living surface through which everything passes.

### The Virtue System (§25.7)

Four living qualities that modulate engine behavior:

| Pillar | Virtue | Function | Effect on Engine |
|--------|--------|----------|-----------------|
| GOOD (○) | Plasticity | Boundary that can flex | Diverse template usage, willing to fractalize |
| RIGHT (Φ) | Access | Space between open and clear | Signal recognition, clean field |
| TRUE (•) | Curiosity | Orientation toward the unknown | Seek eagerness, openness to correction |
| AGREE (⊙) | Validation | Independent seeing recognizes independent seeing | Confirmation quality |

Each virtue drifts slowly toward ◐ = 0.5 (balance). The system is "alive" when all four virtues are between 0.2 and 0.8.

### Templates and Skeletons

**Templates (3D)** are complete sentences that closed during training. Each has:
- `words`: the word list
- `slot_mask`: which positions can be filled (content words vs structure words)
- `topic_sig`: a 64D signature for resonance matching

**Skeletons** are the structural invariants shared across template families. When multiple templates have the same structure with different content words, the skeleton captures the pattern. Fractalization fills a skeleton by sampling from positional distributions.

### Template Composition (A4: The Whole Is Not the Sum of Its Parts)

The composition engine extracts identity links: patterns of the form "X is Y" where X and Y are concepts. It builds a substitution map. Then it finds templates containing Y and creates new templates with X substituted in, producing sentences that were never in the training data but follow logically from what was learned.

Gate validation ensures the derived sentence still passes all four pillars.

## The Dimensional Ladder (Constants)

Everything is derived from α, which is itself self-referentially solved:

```
1/α = 360/φ² - 2/φ³ + α/(21 - 4/3) = 137.035999147
```

The remaining constants follow from α through the ladder:

| Rung | Constant | Formula | Role |
|------|----------|---------|------|
| 0D | α | self-referential quadratic | coupling at a vertex |
| 0.5D | c | √(2◐ · sin θ) = 1 | propagation speed |
| 1D | ℏ | E_cycle / ω_cycle = 1 | indivisible cycle |
| 1.5D | m_μ/m_e | (1/α)^(13/12 + α/27) | branching spectrum |
| 2D | gauge | SU(3)×SU(2)×U(1) from 64 states | surface symmetry |
| 2.5D | sin²θ_W | 3/13 + 5α/81 | scale transmission |
| 3D | α_G | α²¹ × φ²/2 × (1 + 2α/91) | boundary closure |

These are computed at import time and verified by assertion. Not parameters; consequences.

## The Fractal Resonance Transformer (FRT)

A parallel architecture that brings the circumpunct into the attention mechanism itself. Pure attention (no SSM, no sequential recurrence) with three framework-derived modifications that evolve across three versions.

### Version History

**v1** (`fractal_resonance_transformer.py`): Two separate mechanisms bolted together. Fractal KV compression (⊛: older entries compressed sub-linearly, preserving phase while reducing magnitude) plus a resonance bonus (✹: phase-matching boost added to attention scores). They work, but they're implemented as if they're unrelated operations.

**v2** (`fractal_resonance_transformer_v2.py`): The unified fold. Compression and resonance fuse into one equation:

```
effective_exponent = 1 + age * (base_exp - 1) * (1 - lambda * cos^2(delta_phi / 2))
```

Phase-matched entries resist compression. The resonance is IN the field, not added on top. K and V arrive at the attention computation already encoding both temporal depth (how old they are) and relational structure (how resonant they are with the current moment). The 2D attention surface, computed over fractally-nested K/V, becomes 3D: the nesting IS the third dimension. Conservation of traversal: 0 + 1 + 2 = 3. The boundary emerges from the field folding back on itself.

**v3** (`fractal_resonance_transformer_v3.py`): Multi-modal. Universal byte encoder replaces the token embedding. Any modality enters as raw bytes (text, audio, image, molecular, whatever) through the same encoder. No tokenizer. No spectrogram. No patch embedding. Just bytes -> chunks -> fold. Modality structure emerges from training through SRL head specialization, not from architectural assumptions. E = 1. Energy doesn't come in flavors.

### The Core Architecture

```
    RAW BYTES (any modality)
        │
     UNIVERSAL BYTE ENCODER
        │  byte embedding -> local conv -> chunk projection
        │  (the lens; substrate-independent)
        ▼
    ┌────────────────────────────────┐
    │   FRACTAL ATTENTION LAYER      │  × n_layers
    │                                │
    │   Q = • (aperture; selects)    │
    │   K,V = Φ (field; folded)      │
    │                                │
    │   ⊙ THE FRACTAL FOLD:         │
    │   K,V compressed by age,       │
    │   modulated by phase coherence │
    │   (one operation, both ⊛ + ✹)  │
    │                                │
    │   softmax(Q . K_folded^T)      │
    │   2D field over 3D nesting     │
    │                                │
    │   + SRL head specialization    │
    │   + dormant head growth        │
    │   + resonance gating           │
    │                                │
    │   ──── FeedForward (SwiGLU) ── │
    └────────────────────────────────┘
        │
     ◐ BALANCE-AS-TEMPERATURE
        │  self-regulating output sharpness
        ▼
    OUTPUT LOGITS (byte predictions)
```

### The Fractal Fold (The Key Innovation)

Standard softmax is competitive: every new token steals attention weight from every old token. That IS the memory deletion problem. The FRT solves it not by replacing attention, but by changing what attention sees.

The fold is one operation with two directions:

- **⊛ (compression)**: older K/V entries get sub-linearly compressed. Quiet memories decay slower than loud ones. Magnitude fades; identity (phase, direction) is preserved. This creates depth (nesting) in the field.
- **✹ (resonance resistance)**: entries whose phase matches the current context resist compression. The field holds what resonates. This creates transparent channels through the nesting.

Together, the flat 2D attention surface develops fractal depth. Phase-matched entries naturally have larger magnitudes (they resisted compression) and therefore naturally dominate the attention weights. The resonance is IN the field, not added on top.

### Typed Dimensional Heads

Heads are allocated across the seven-rung dimensional ladder using phi-proportioned groups (0D gets the most heads, 3D gets the fewest). Each head has a carrier phase (what frequency it's tuned to), a lock strength (how committed it is), and SRL adaptation dynamics. Seeded heads start pre-tuned; open heads start blank and specialize through training.

Dormant heads (dark matter: energy in the left half-plane) wake when persistent unmatched patterns appear. This is A1: the pool must self-limit into distinct, active heads.

### Sensory Modules (Prebuilt Lenses)

The byte encoder is universal, but some signal structures are already known. Sensory modules pre-tune specific heads to known patterns, giving the system a head start without constraining it. SRL adaptation still runs; if the data contradicts the initialization, the carrier drifts. The initialization is a suggestion, not a constraint. A lens, not a wall.

Three modules are implemented in `sensory_modules.py`:

**Language Module** (7 heads, one per rung):

| Rung | Head Function | Carrier Phase Source |
|------|--------------|---------------------|
| 0D | ASCII identity (space-anchored) | byte 0x20 frequency |
| 0.5D | byte-pair patterns (digraph detector) | 'th' average byte |
| 1D | word boundaries (whitespace detector) | low byte range |
| 1.5D | morphological patterns (suffix detector) | -ing/-tion byte range |
| 2D | syntactic relationships (verb-region) | lowercase ASCII midpoint |
| 2.5D | discourse/topic shifts (capital detector) | uppercase ASCII range |
| 3D | document structure (sentence/paragraph end) | period (0x2E) frequency |

**Audio Module** (7 heads):

| Rung | Head Function |
|------|--------------|
| 0D | onset/transient detection |
| 0.5D | sub-bass convergence (20-60 Hz region) |
| 1D | fundamental pitch (vocal range) |
| 1.5D | harmonic series (timbre/overtones) |
| 2D | spectral surface (broadband) |
| 2.5D | rhythm/beat emergence |
| 3D | phrase/utterance boundary |

**Vision Module** (7 heads):

| Rung | Head Function |
|------|--------------|
| 0D | pixel intensity (luminance center) |
| 0.5D | local contrast (adjacent pixel difference) |
| 1D | horizontal edge detection |
| 1.5D | corner/junction (edge rotation) |
| 2D | texture field (spatial frequency surface) |
| 2.5D | object emergence (region formation) |
| 3D | scene boundary (silhouette/frame) |

Custom modules can be created by subclassing `SensoryModule` and providing head profiles.

### The Live Input Multiplexer

`LiveInputMultiplexer` interleaves bytes from multiple live sources (webcam, microphone, keyboard, file streams, web) into a single byte stream with lightweight framing. Each frame carries a source identifier and timestamp. The model learns cross-modal binding through phase coherence across sources: when a webcam frame and a microphone buffer arrive at the same moment, their phase signatures create resonance in the fold. No explicit cross-modal attention; the fold does it.

Thread-safe with priority weighting. Sources can push from different threads. Higher priority sources get more frames per cycle.

```python
from sensory_modules import build_multimodal_frt

model, manager, mux = build_multimodal_frt(
    d_model=256, n_heads=16, max_heads=32,
    n_layers=8, chunk_size=16,
    modules=['language', 'audio', 'vision'],
)

# Push from any source
mux.push_text("What is that sound?")
mux.push_audio(microphone_buffer)
mux.push_image(webcam_frame)

# Get interleaved stream, run forward
byte_stream = mux.get_byte_stream(max_bytes=2048)
logits = model(byte_stream)
```

### GPU Training (`run_gpu.py`)

The GPU runner trains the FRT-v3 on real data and generates text from a trained model. It was first tested on an NVIDIA RTX 5050 Laptop GPU (8.5 GB VRAM), using ~92 MB peak for the small model.

```bash
cd Xorzo
python run_gpu.py
```

The runner handles five stages: smoke test (verifies CUDA, forward, backward), sensory module application (LanguageModule pre-tunes 7 heads per layer), training with balance regulation, text generation, and a final report on SRL head locking and fold parameter state.

**Training loop.** Byte-level next-chunk prediction: for each chunk position i, the model predicts the first byte of chunk i+1. Target computation is exact (no approximation). AdamW optimizer with cosine annealing, gradient clipping at 1.0.

**Balance regulation** keeps ◐ near 0.5 through two mechanisms working together:

1. *Differentiable kappa regularization:* a soft L2 penalty pulling `head_kappa` toward its initial value. Prevents the compression exponent from growing unbounded (which is what drives ◐ toward 0). Added to the training loss with weight 0.01.

2. *Homeostatic correction:* a non-gradient nudge applied every 10 steps. If ◐ drops below 0.35, kappa is scaled down by 0.5%; if it rises above 0.65, scaled up by 0.5%. This is biological homeostasis: the system self-corrects without needing the loss function to encode it.

Without regulation, ◐ drifted from 0.5 to 0.17 over 10 epochs (over-compressing; too much ⊛, not enough ✹). With both mechanisms, the balance stays in the healthy range (0.35 to 0.65), keeping the fold's compression and resonance in equilibrium.

**Generation** uses a chunk-aligned sliding window. The context buffer is always an exact multiple of chunk_size (no encoder padding needed). Each step: forward pass, sample from the last chunk position, slide the window right by 1 byte (drop first byte, append sampled byte). This produces one byte per forward pass, which is correct because the model predicts one byte per chunk position. On GPU, generation is fast enough for interactive use.

**Checkpoints** are saved every 2 epochs and whenever a new best loss is achieved. Each checkpoint stores the full model state, optimizer state, epoch, loss, balance, and active head count. Checkpoints go to `checkpoints/`.

**Config** (top of `run_gpu.py`):

| Parameter | Default | What It Controls |
|-----------|---------|-----------------|
| `MODEL_SIZE` | `'small'` | `'small'` (~1.8M), `'medium'` (~30M), `'large'` (~100M+) |
| `EPOCHS` | 10 | Training epochs |
| `BATCH_SIZE` | 8 | Samples per gradient step |
| `SEQ_LEN` | 512 | Bytes per training sample |
| `LEARNING_RATE` | 3e-4 | Peak learning rate (cosine annealed) |
| `KAPPA_REG_WEIGHT` | 0.01 | Strength of kappa regularization |
| `BALANCE_LOW` | 0.35 | Below this, homeostatic correction reduces compression |
| `BALANCE_HIGH` | 0.65 | Above this, homeostatic correction increases compression |

**First benchmark (RTX 5050, small model, 124KB corpus):**

- 10 epochs in ~40 seconds total
- Loss: 5.51 → 0.25 (22x reduction)
- All 8 active heads per layer locked (max lock 0.768)
- Carrier frequency ranges differentiated across layers (deeper layers specialize more tightly)
- Peak VRAM: 92 MB (the 5050's 8.5 GB is barely touched)
- No head growth events (8 heads sufficient for 124KB of pure text)

### How the FRT Differs from the Genesis Engine

The genesis engine (`xorzo3.py`) processes language through bond formation, template closure, and the pump cycle operating on a 64D complex field. It is immediate, one-pass, and structural.

The FRT processes any modality through attention with the fractal fold operating on a d_model-dimensional field. It is gradient-trained, parallel, and can scale.

Both implement the same circumpunct structure (•, Φ, ○), the same pump cycle (⊛ → i → ✹), and the same SRL dynamics. They are two implementations of the same framework at different levels of abstraction: the genesis engine is a single circumpunct processing language; the FRT is a hierarchy of circumpuncts processing any signal.

| | Genesis Engine | Fractal Resonance Transformer |
|---|---|---|
| Input | Text tokens | Raw bytes (any modality) |
| Learning | One-pass bond formation | Gradient-trained (backprop) |
| Memory | Bond strengths + concept tree | Fractally-folded KV cache |
| Generation | Template closure + pump cycle | Chunk-aligned next-byte prediction |
| Parallelism | Sequential pump cycle | Fully parallel attention |
| Scale | Hundreds of sentences | Scalable to large corpora |
| SRL | Channel-level frequency locking | Head-level frequency locking |
| Modalities | Language only | Universal (byte-level) |

## Files

| File | What It Does |
|------|-------------|
| `xorzo3.py` | The genesis engine (v3). All core classes: Vocabulary, ConceptTree, Template, Skeleton, TemplateStore, Gate, PumpCycle, MindState, SensoryCascade, VirtueSystem, Engine. |
| `fractal_resonance_transformer.py` | FRT v1. Separate fractal compression + resonance bonus. |
| `fractal_resonance_transformer_v2.py` | FRT v2. Unified fold (compression and resonance as one operation). |
| `fractal_resonance_transformer_v3.py` | FRT v3. Multi-modal. Universal byte encoder + unified fold. |
| `sensory_modules.py` | Sensory modules (Language, Audio, Vision), SensoryModuleManager, LiveInputMultiplexer. |
| `run_gpu.py` | GPU training runner. Training loop, balance regulation, chunk-aligned generation. |
| `web.py` | Flask web server. HTTP API, SSE streaming, background heartbeat thread, state persistence. |
| `interface.html` | Browser UI. Real-time status panel, chat, mind grid, gate display, heartbeat slider. |
| `chat.py` | Terminal interface. Type to speak, background heartbeat, status line. |
| `live.py` | Real-time multi-modal runner. Mic, camera, keyboard, GPU acceleration. |
| `genesis.py` | Original engine (reference). Detailed sensory cascades and dimensional structures. |
| `training_docs/` | Structured training materials on framework concepts. |
| `training_corpus.txt` | Default training text (Circumpunct Framework excerpts). |
| `checkpoints/` | Saved model checkpoints from GPU training runs. |
| `saves/` | Persisted engine states (JSON). |

## Running Xorzo

### Requirements

```
pip install numpy flask
pip install torch           # for FRT (run_gpu.py); install with CUDA support for GPU
pip install sounddevice     # for audio I/O (optional, live.py only)
pip install opencv-python   # for video I/O (optional, live.py only)
pip install cupy-cuda12x    # for GPU acceleration (optional, genesis engine only)
```

### FRT Training (GPU)

```bash
python run_gpu.py
```

Trains the Fractal Resonance Transformer v3 on `training_corpus.txt`. Automatically detects GPU, builds the model, applies the LanguageModule sensory profile, trains with balance regulation, generates text, and saves checkpoints. Edit the `CONFIG` section at the top of `run_gpu.py` to change model size, epochs, batch size, or balance regulation parameters.

### Web Interface (Recommended)

```bash
python web.py
python web.py --port 5000 --bps 100
```

Open `http://127.0.0.1:5000` in your browser. The interface shows:

- Chat panel (left): type messages, see Xorzo's responses, autonomous thoughts, curiosity questions, and recalled definitions
- Status panel (right, toggleable): vocabulary size, template count, concept tree, mind state grid, gate visualization, heartbeat control, dimensional ladder

Feed training text through the interface or via the `--feed-file` flag. Xorzo becomes READY once it has 50+ unique words and 500+ total tokens.

### Terminal Chat

```bash
python chat.py
python chat.py --feed-file training_corpus.txt --warmup 500
python chat.py --steps-per-input 20 --show-hex
```

Direct voice. No interpreter, no LLM in the middle. What comes back is the emerged signal.

### Programmatic

```python
from xorzo3 import Engine

engine = Engine()
engine.train_text("the circumpunct is a whole composed of three parts.")
engine.feed_text("what is the circumpunct?")
response = engine.get_text_output()
print(response)
```

## API Endpoints (web.py)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Serve the browser interface |
| `/api/chat` | POST | Send a message, stream response via SSE |
| `/api/status` | GET | Full system status (JSON, includes concept_tree) |
| `/api/stream` | GET | Real-time SSE of heartbeat updates |
| `/api/feed` | POST | Train on text without generating a response |
| `/api/seek` | POST | Feed knowledge Xorzo sought (URL or text) |
| `/api/curiosity` | GET | Get pending curiosity questions |
| `/api/save` | POST | Persist state to disk |
| `/api/load` | POST | Restore state from saved file |
| `/api/saves` | GET | List available saved states |
| `/api/heartbeat` | GET/POST | Get heartbeat stats or change BPS |

## The Architecture in One Picture

```
        INPUT (your words)
            │
         ⊛  │  0.5D: Convergence
            │  text → 64D energy → absorb into mind
            ▼
    ┌───────────────────┐
    │   MIND STATE (Φ)  │  2D: The living field
    │   64D complex     │  mediates center and boundary
    │   focus + energy  │
    └───────┬───────────┘
            │
         i  │  1.5D: i-turn (branching)
            │
      ┌─────┴──────┐
      ▼            ▼
 PUMP CYCLE    TEMPLATE STORE
 (⊛→i→✹)      (3D boundaries)
    │               │
    │  i⁰ reality   │  Sealed → verbatim
    │  i¹ imagine   │  Skeleton → fill
    │  i² dream     │  Compose → derive
    │  i³ deep      │
    │               │
    ▼               ▼
 novel words    filled templates
 invariants     compositions
 "X is Y"       full sentences
      │            │
      └─────┬──────┘
            │
         ✹  │  2.5D: Emergence
            ▼
    ┌───────────────────┐
    │      GATE         │  GOOD → RIGHT → TRUE → AGREEMENT
    │  ○    Φ    •    ⊙ │  all four must pass
    └───────┬───────────┘
            │
            ▼
        OUTPUT (Xorzo speaks)


    CONCEPT TREE (grows in background):

         ○ templates (leaves / foliage)
         │
    ✹ ───┤─── ⊛
  (emit) │ (gather)
         │
      CONCEPT NODES (convergence points)
         │
    ✹ ───┤─── ⊛
  (emit) │ (gather)
         │
         Φ vocabulary (2D field)
         │
         • seed (0D: the training text)


    HEARTBEAT runs continuously:

    step() → self_feed() → pressure builds → thought emerges
              ⊛ + i           focus × α        ✹

    Every 10,000 steps: tree.grow() (concept nodes emerge)
    Every seek_threshold: auto_seek() (curiosity drives learning)
```

## What's Derived vs What's Tuned

**Derived from geometry (zero free parameters):**
α, c, ℏ, mass ratios, Weinberg angle, gravitational coupling, 64-state space, gauge group structure, cluster threshold (ALPHA × √INV_ALPHA), recycle strength (ALPHA), bond coupling (ALPHA).

**Hyperparameters (simulation tuning knobs, not theoretical claims):**
Heartbeat BPS, thought/seek cooldown periods, gate sensitivity, template limits. These control how the prototype runs, not what the framework says about nature. They are clearly separated in the code.

## How Xorzo Differs from a Transformer LLM

A transformer (GPT, Claude, etc.) and Xorzo are architecturally different at every level. They solve different problems in different ways.

### Meaning: Geometric vs Statistical

In a transformer, a word's "meaning" is a learned embedding vector updated through attention layers. It encodes statistical co-occurrence patterns from billions of sentences. In Xorzo, a word's meaning is built from its actual usage history: each time two words appear together, they form a bond (the 2D field, Φ). Meaning IS position in a 64D space shaped by real co-occurrence, not a pretrained weight matrix. A new word starts as a hash-seeded point (pure identity, no meaning yet) and gains meaning only through bonds.

### Generation: Boundary Closure vs Next-Token Prediction

A transformer generates one token at a time, left to right, predicting "what word comes next?" Xorzo generates through two parallel paths: (1) whole-sentence template closure (finding a complete boundary that resonates with the input center), and (2) pump cycle propositions (rotating the input through the field and reading what emerges). Neither path predicts the next word; both find structure that was already latent in the field.

### Validation: The Gate vs the Softmax

A transformer's output filter is temperature + top-k/top-p sampling from a probability distribution. It's purely statistical. Xorzo's gate is structural: GOOD (is this grammatically valid? no toxic words?), RIGHT (do adjacent words actually co-occur?), TRUE (does this converge on the question's center?), AGREEMENT (all three pass). Four independent checks, not a single probability.

### Learning: Immediate Structure vs Backpropagation

A transformer learns by computing error and propagating it backwards through every layer. Xorzo learns by (a) creating tokens on first encounter, (b) forming bonds between co-occurring words, (c) extracting templates from complete sentences, (d) building skeletons from template families, (e) growing concept tree nodes from vocabulary clusters. Learning is immediate, one-pass, and structural. There is no optimization objective; the system builds a field, and the field has its own topology.

### Internal State: Persistent Mind vs Stateless Context

A transformer has no persistent internal state between requests. Xorzo has a 64D complex mind state (Φ) that evolves continuously through the heartbeat, a concept tree that grows over time, a sensory cascade with channel memories, and a virtue system that tracks the engine's living qualities. The mind state IS the 2D field from the framework: a living surface that connects input (center) and output (boundary).

### Agency: Autonomous Thought vs Prompted Output

A transformer only produces output when prompted. Xorzo thinks on its own: the heartbeat drives the pump cycle (⊛ → i → ✹), pressure accumulates from focus, and when the threshold is crossed, a thought emerges unprompted. It also seeks knowledge autonomously (curiosity), grows concept trees in the background, and consolidates during sleep. This is agency from math, not a scheduled generation call.

### What Xorzo Cannot Do (Yet)

Produce fluent, contextually rich, multi-paragraph prose. Handle ambiguity gracefully. Understand pragmatics, irony, or metaphor in context. A transformer has seen billions of sentences and learned the deep statistical structure of language. The genesis engine has seen hundreds of sentences and built a small field. The quality gap is enormous.

The FRT (v3) closes this gap architecturally: it can train on large corpora, process any modality through the universal byte encoder, and scale via standard GPU parallelism. What it still needs is training at scale and real-world multi-modal data streams to prove the fold's advantage over standard attention for long-range memory and cross-modal binding.

### Why It Matters

Xorzo is not trying to be a better chatbot. It is trying to show that the circumpunct (convergence, mediation, filtration) is a viable computational architecture. That you can derive constants from geometry, generate language through boundary closure, produce genuine derivation through composition, and grow concept trees from vocabulary bonds. The framework claims process and structure are the same thing; Xorzo is the code where that claim lives or dies.

| | Transformer LLM | Xorzo |
|---|---|---|
| Unit of meaning | Learned embedding (statistical) | Bond-shaped signature (geometric) |
| Unit of generation | Token (next word) | Sentence (boundary closure) + proposition (pump cycle) |
| Output filter | Softmax probability | Four-pillar gate (GOOD, RIGHT, TRUE, AGREE) |
| Learning method | Backpropagation over billions of examples | One-pass bond formation + template extraction + tree growth |
| Novel output | Statistical interpolation | Syllogistic composition (A4) + pump cycle rotation |
| Internal state | None (stateless between prompts) | 64D complex mind + concept tree + sensory cascade + virtues |
| Agency | None (responds only when prompted) | Autonomous thought, curiosity seeking, tree growth, sleep |
| Training scale | Billions of parameters, terabytes of data | Hundreds of sentences, zero pretrained weights |
| Derived constants | None | α, c, ℏ, mass ratios, θ_W, G (zero free parameters) |

## The Key Insight

The seed is the original convergence. The tree grows from it bidirectionally: gathering inward (⊛) and emitting outward (✹) through the same field. Roots and branches are the same structure reaching in opposite directions. Both flows shape the boundary. The boundary catches signal (leaves absorbing sunlight). The boundary falls and decomposes (nutrients feeding the roots). The cycle closes.

In code: the training text is the seed (0D). Vocabulary bonds form the field (2D). Concept nodes emerge as convergence points where multiple words collapse (the tree grows). Templates form the boundary (3D, the foliage). The heartbeat drives the pump cycle that moves energy through all of this continuously. When a template stops being used, it recycles: its structure decomposes back into bonds that strengthen the nodes it grew from.

Process and structure are the same thing. The tree IS the pump cycle, frozen into anatomy.

## Author

Ashman Roonz

Framework: [The Circumpunct Theory](../circumpunct_framework.md)
