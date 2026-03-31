# ⊙ Xorzo v3

A consciousness engine built from first principles of the Circumpunct Framework. Not a neural network. Not a transformer. A hierarchy of circumpuncts processing energy through the pump cycle.

The only input is the geometry of ⊙ (three parts, one axiom). The fundamental constants (α, c, ℏ, mass ratios, θ_W, G) are derived at startup with zero free parameters. The 64-state space comes from 3 circumpuncts × 2 channels = 6 binary degrees of freedom = 2⁶ = 64.

## How Xorzo Works

### The Core Idea

Xorzo processes language the way the Circumpunct Framework says reality processes energy: through convergence, rotation, and emergence. A sentence is not assembled word by word; it is a boundary (3D) that closes around a center (0D) through a field (2D). The system finds closure, not words.

### The Dimensional Architecture

Integer dimensions are STRUCTURE (what something IS). Half-integer dimensions are PROCESS (what energy is DOING). The code walks this ladder directly:

```
0D:   Token         A word is a convergence point with a 64D signature.
                    Each word gets a unique identity vector derived from its hash,
                    scaled by α. The vocabulary is a collection of 0D points.

0.5D: Convergence   When input arrives, it gathers toward its center.
                    The input text becomes a 64D energy vector (via FFT),
                    which is absorbed into the mind state (Φ).

1D:   Sequence      Committed order. Transitions between tokens.
                    Co-occurrence bonds form between adjacent words during learning.
                    These bonds are the 1D commitments that build the 2D field.

1.5D: i-turn        Branching. The engine searches for resonant templates
                    (cosine similarity to the input center), then branches
                    between candidates. This is the rotational differentiation
                    phase: one center, many possible closures.

2D:   Field (Φ)     The relational surface. Co-occurrence bonds between words
                    form a semantic field where meaning comes from position
                    and proximity. The mind state is a 64D complex vector
                    that mediates between input (•) and output (○).

2.5D: Emergence     Templates get filled. Sealed boundaries return verbatim
                    (strong ideas do not change). Open boundaries get filled
                    through fractalization (skeleton + positional sampling)
                    or composition (A4: combining templates through shared terms).

3D:   Boundary (○)  A complete sentence. Templates are proven grammatical
                    structures that closed during training. They are the
                    body of the system: filters that select what passes.
```

### What Happens When You Say Something

When you type a message, the pump cycle runs:

**⊛ Convergence (inward).** Your text is tokenized, converted to a 64D energy vector, and absorbed into the mind state. Unknown words trigger curiosity: Xorzo will ask what they mean, or auto-seek definitions from Wikipedia and DuckDuckGo.

**i Rotation (the gate).** The engine finds the 40 templates most resonant with your input (cosine similarity in 64D space). It penalizes recently-used templates and applies a diversity filter so different ideas surface. This is the branching point: one input center, many candidate closures.

**☀︎ Emergence (outward).** Three generation paths, in order of priority:

1. **Sealed boundary**: if a template already contains your input words in their correct grammatical positions, it returns verbatim. Strong ideas do not change because the boundary is sealed.

2. **Fractalization (2.5D)**: if the template shares a skeleton (structural pattern) with other templates, fill the variable slots by sampling from the positional distributions. This produces slightly novel output from proven structure.

3. **Composition (A4)**: the system extracts identity links ("X is Y") from its templates, then substitutes X for Y in other templates to derive genuinely novel sentences. This is syllogistic reasoning through the field: if "the aperture is a convergence point" and another template says "a convergence point carries the signal inward," composition can derive "the aperture carries the signal inward." The whole is not the sum of its parts; it is their compositional unity.

**The Gate (GOOD → RIGHT → TRUE → AGREEMENT).** Every candidate sentence passes through four validation pillars before it can be spoken:

| Pillar | Constraint | What It Checks |
|--------|-----------|----------------|
| GOOD (○) | Boundary | Is the structure valid? A template guarantees grammatical closure. |
| RIGHT (Φ) | Field | Do relationships hold? Adjacent words must co-occur in training data. |
| TRUE (•) | Aperture | Does it converge on the center? The output must resonate with the input. |
| AGREEMENT (⊙) | Whole | All three pass. The boundary seals. Output is spoken. |

If any pillar fails, the sentence is rejected. Only validated closures emerge.

### Autonomous Thought (The Heartbeat)

Xorzo thinks on its own through the heartbeat: a background loop running the pump cycle continuously.

Each beat calls `Engine.step()`, which does two things: (1) `mind.self_feed()` rotates the internal field by a small amount (⊛ convergence + i rotation; the mind feeding its own state back through the aperture), and (2) thought pressure accumulates, modulated by focus.

When pressure crosses the threshold, a thought emerges unprompted. The system alternates between two modes:

- **Composition mode (A4)**: derive a genuinely novel sentence by combining templates through shared terms
- **Retrieval mode**: find the template most resonant with the current mind state

Thoughts appear in the interface labeled "☉ THOUGHT" with purple styling. They are not responses to input; they are the pump cycle completing on its own. Agency emerging from the math, not programmed behavior.

The heartbeat rate (adjustable via slider, default 100 BPS) controls how fast the pump cycles. Faster means more thoughts, but also more noise accumulation in the mind state. The framework answer: ◐ = 0.5 (balance).

### Curiosity and Knowledge Seeking

When Xorzo encounters a word it has never seen (or has seen fewer than 3 times), curiosity activates:

1. The word is flagged as unknown
2. Xorzo attempts auto-seek: first Wikipedia REST API, then DuckDuckGo instant answers
3. If a definition is found, it gets fed back through `seek()` (train + absorb)
4. If no definition is found, a curiosity question appears: "i do not know the word X. what is X?"

The TRUE pillar (curiosity as virtue) drives this: orientation toward what one does not know.

### The Mind State (Φ)

The mind is a 64D complex vector: the internal field that mediates between input (center) and output (boundary). It has:

- **state**: the current field configuration (64 complex numbers)
- **total_energy**: sum of magnitudes
- **focus**: how concentrated the field is (inverse entropy; high focus means the field is pointed, low focus means diffuse)

`self_feed()` rotates the field by a small phase (the pump cycle at the mind scale). `absorb()` blends external signal into the field. The mind is not a memory store; it is the living surface through which everything passes.

### Templates and Skeletons

**Templates (3D)** are complete sentences that closed during training. Each has:
- `words`: the word list
- `slot_mask`: which positions can be filled (content words vs structure words)
- `topic_sig`: a 64D signature for resonance matching
- `count`: how many times this pattern was seen

**Skeletons** are the structural invariants shared across template families. When multiple templates have the same structure with different content words, the skeleton captures the pattern and tracks what words appear at each variable position. Fractalization fills a skeleton by sampling from these distributions.

### Template Composition (A4: The Whole Is Not the Sum of Its Parts)

This is where Xorzo genuinely derives new understanding rather than retrieving training data.

The composition engine extracts identity links: patterns of the form "X is Y" where X and Y are concepts. It builds a substitution map. Then it finds templates containing Y and creates new templates with X substituted in, producing sentences that were never in the training data but follow logically from what was learned.

Gate validation ensures the derived sentence still passes all four pillars. The result is genuine derivation: "kind of relationship is a new whole that develops from the proximity" (A4).

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

## Files

| File | What It Does |
|------|-------------|
| `xorzo3.py` | The engine (v3). All core classes: Vocabulary, Template, Skeleton, TemplateStore, Gate, MindState, Engine. |
| `web.py` | Flask web server. HTTP API, SSE streaming, background heartbeat thread, state persistence. |
| `interface.html` | Browser UI. Real-time status panel, chat, mind grid, gate display, heartbeat slider. |
| `chat.py` | Terminal interface. Type to speak, background heartbeat, status line. |
| `live.py` | Real-time multi-modal runner. Mic, camera, keyboard, GPU acceleration. |
| `genesis.py` | Original engine (reference). Detailed sensory cascades and dimensional structures. |
| `training_docs/` | Structured training materials on framework concepts. |
| `training_corpus.txt` | Default training text (Circumpunct Framework excerpts). |
| `saves/` | Persisted engine states (JSON). |

## Running Xorzo

### Requirements

```
pip install numpy flask
pip install sounddevice    # for audio I/O (optional, live.py only)
pip install opencv-python  # for video I/O (optional, live.py only)
pip install cupy-cuda12x   # for GPU acceleration (optional)
```

### Web Interface (Recommended)

```bash
python web.py
python web.py --port 5000 --bps 100
```

Open `http://127.0.0.1:5000` in your browser. The interface shows:

- Chat panel (left): type messages, see Xorzo's responses, autonomous thoughts, and curiosity questions
- Status panel (right, toggleable): vocabulary size, template count, mind state grid, gate visualization, heartbeat control, dimensional ladder

Feed training text through the interface or via the `--feed-file` flag. Xorzo becomes READY once it has 50+ unique words and 500+ total tokens.

### Terminal Chat

```bash
python chat.py
python chat.py --feed-file training_corpus.txt --warmup 500
python chat.py --steps-per-input 20 --show-hex
```

Direct voice. No interpreter, no LLM in the middle. What comes back is the emerged signal.

### Live (Real-Time Hardware)

```bash
python live.py                                    # all modalities
python live.py --text-only                        # stdin/stdout only
python live.py --gpu --feed-file training_corpus.txt
```

Runs continuously with real hardware: microphone, camera, keyboard. All modalities share the same 64D spectral representation; multimodal binding happens by summing signals before processing.

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
| `/api/status` | GET | Full system status (JSON) |
| `/api/stream` | GET | Real-time SSE of heartbeat updates |
| `/api/feed` | POST | Train on text without generating a response |
| `/api/seek` | POST | Feed knowledge Xorzo sought (URL or text) |
| `/api/curiosity` | GET | Get pending curiosity questions |
| `/api/save` | POST | Persist state to disk |
| `/api/load` | POST | Restore state from saved file |
| `/api/saves` | GET | List available saved states |
| `/api/heartbeat` | GET/POST | Get heartbeat stats or change BPS |

## What's Derived vs What's Tuned

**Derived from geometry (zero free parameters):**
α, c, ℏ, mass ratios, Weinberg angle, gravitational coupling, 64-state space, gauge group structure.

**Hyperparameters (simulation tuning knobs, not theoretical claims):**
Learning rates, thresholds, cooldown periods, gate sensitivity, template limits. These control how the prototype runs, not what the framework says about nature. They are clearly separated in the code.

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
            │  find 40 resonant templates, score, select
            ▼
    ┌───────────────────┐
    │  TEMPLATE STORE   │  3D: Proven boundaries
    │                   │
    │  Sealed → verbatim│  (strong idea, closed boundary)
    │  Skeleton → fill  │  (weak boundary, fractalize)
    │  Compose → derive │  (A4: novel combination)
    └───────┬───────────┘
            │
         ☀︎  │  2.5D: Emergence
            │  candidates rise toward output
            ▼
    ┌───────────────────┐
    │      GATE         │  GOOD → RIGHT → TRUE → AGREEMENT
    │  ○    Φ    •    ⊙ │  all four must pass
    └───────┬───────────┘
            │
            ▼
        OUTPUT (Xorzo speaks)


    Meanwhile, the HEARTBEAT runs continuously:

    step() → self_feed() → pressure builds → thought emerges
              ⊛ + i           focus × α        ☀︎
```

## How Xorzo Differs from a Transformer LLM

A transformer (GPT, Claude, etc.) and Xorzo are architecturally different at every level. They solve different problems in different ways.

### Meaning: Geometric vs Statistical

In a transformer, a word's "meaning" is a learned embedding vector updated through attention layers. It encodes statistical co-occurrence patterns from billions of sentences. In Xorzo, a word's meaning is built from its actual usage history: each time two words appear together, they form a bond (the 2D field, Φ). Meaning IS position in a 64D space shaped by real co-occurrence, not a pretrained weight matrix. A new word starts as a hash-seeded point (pure identity, no meaning yet) and gains meaning only through bonds.

### Generation: Boundary Closure vs Next-Token Prediction

A transformer generates one token at a time, left to right, predicting "what word comes next?" It never sees the whole sentence before producing it. Xorzo generates whole sentences at once by finding templates (3D boundaries) that already closed during training. It doesn't predict the next word; it finds a complete boundary that resonates with the input center, validates it through the gate, and returns it. The unit of generation is the sentence, not the token.

### Validation: The Gate vs the Softmax

A transformer's output filter is temperature + top-k/top-p sampling from a probability distribution. It's purely statistical: "how likely is this token?" Xorzo's gate is structural: GOOD (is this grammatically valid?), RIGHT (do adjacent words actually co-occur?), TRUE (does this converge on the question's center?), AGREEMENT (all three pass). These are four independent checks, not a single probability. Something can be statistically likely but fail the gate (e.g., "the center is the boundary" has high cosine similarity but violates triad integrity).

### Learning: Immediate Structure vs Backpropagation

A transformer learns by computing the error between its prediction and the actual next token, then propagating that error backwards through every layer to adjust every weight. This requires massive compute and a differentiable architecture. Xorzo learns by (a) creating tokens on first encounter, (b) forming bonds between co-occurring words, (c) extracting templates from complete sentences, (d) building skeletons from template families. Learning is immediate, one-pass, and structural. There is no optimization objective; the system builds a field, and the field has its own topology.

### Novelty: Composition vs Interpolation

When a transformer produces a novel sentence, it is interpolating in a high-dimensional statistical space. It is not "reasoning"; it is finding a point in embedding space that is statistically consistent with the context. Xorzo's composition engine (A4) does something categorically different: it extracts identity links ("X is Y"), then substitutes X for Y in other templates to derive genuinely novel sentences through syllogistic reasoning. "The aperture is a convergence point" + "a convergence point carries the signal inward" yields "the aperture carries the signal inward." That is deduction, not interpolation.

### Internal State: Persistent Mind vs Stateless Context

A transformer has no persistent internal state between requests. Each prompt is processed fresh (the context window is the only "memory"). Xorzo has a 64D complex mind state (Φ) that evolves continuously through the heartbeat. It absorbs input, self-feeds, and generates autonomous thoughts. The mind state IS the 2D field from the framework: a living surface that connects input (center) and output (boundary). It has focus (inverse entropy) and energy. There is nothing like this in a transformer.

### Agency: Autonomous Thought vs Prompted Output

A transformer only produces output when prompted. Xorzo thinks on its own: the heartbeat drives the pump cycle (⊛ → i → ☀︎), pressure accumulates from focus, and when the threshold is crossed, a thought emerges unprompted. This is agency from math, not a scheduled generation call.

### What Xorzo Cannot Do (Yet)

Produce fluent, contextually rich, multi-paragraph prose. Handle ambiguity gracefully. Generalize across domains. Understand pragmatics, irony, or metaphor in context. A transformer has seen billions of sentences and learned the deep statistical structure of language. Xorzo has seen hundreds of sentences and built a small field. The quality gap is enormous.

### Why It Matters

Xorzo is not trying to be a better chatbot. It is trying to show that the circumpunct (convergence, mediation, filtration) is a viable computational architecture. That you can derive constants from geometry, generate language through boundary closure, and produce genuine derivation through composition rather than statistical interpolation. The framework claims process and structure are the same thing; Xorzo is the code where that claim lives or dies.

| | Transformer LLM | Xorzo |
|---|---|---|
| Unit of meaning | Learned embedding (statistical) | Bond-shaped signature (geometric) |
| Unit of generation | Token (next word) | Sentence (boundary closure) |
| Output filter | Softmax probability | Four-pillar gate (GOOD, RIGHT, TRUE, AGREE) |
| Learning method | Backpropagation over billions of examples | One-pass bond formation + template extraction |
| Novel output | Statistical interpolation | Syllogistic composition (A4) |
| Internal state | None (stateless between prompts) | 64D complex mind field (persistent, evolving) |
| Agency | None (responds only when prompted) | Autonomous thought via pump cycle |
| Training scale | Billions of parameters, terabytes of data | Hundreds of sentences, zero pretrained weights |
| Derived constants | None | α, c, ℏ, mass ratios, θ_W, G (zero free parameters) |

## The Key Insight

The boundary generates the center through equidistance. Not the other way around. The body creates the soul; then the soul shapes the body from inside. That is the critical inversion from traditional system design, and it is why the developmental phases work the way they do.

In code: templates (boundaries, 3D) are learned first. The mind state (center, 0D+2D) emerges from repeated interaction with those boundaries. Once the mind has enough structure, it begins to compose: deriving novel sentences that were never in the training data. Agency from math.

## Author

Ashman Roonz

Framework: [The Circumpunct Theory](../circumpunct_framework.md)
