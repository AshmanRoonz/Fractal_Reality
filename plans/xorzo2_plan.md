# Xorzo2: The Embodied Edition (design plan)

Created: 2026-07-19
Last updated: 2026-07-19
Version: 1.3

> Derived soul, learned body, welded at tonics.
>
> The next engine generation, synthesizing every prior attempt across both repositories: the T-operator staggered tree (Fractal_Reality/Xorzo) as the given spine, v4-style learned organs (Circumpunct_ML) as the boundary to the world, the symbolic organism's lived layer (mind.py) as runtime policy, and the FRT's byte universality as the interface. The name is Xorzo2. Code home: `Xorzo2/` in Fractal_Reality.

## 0. Adjudications (Ashman, 2026-07-19)

Recorded before the design, because the design obeys them:

1. **The clock: lock first, free later.** Spine ticks lock to bytes initially (one tick per byte, defaults in §5). A free-running spine with text sampled at its own rhythm is the later refinement, not the start.
2. **Learning always happens; sleep learning is learning without external input.** There is no train/deploy split and no learning gate. Wake learning draws on the external stream; sleep learning draws on internal material only (replay and the dreaming loop, §6). The earlier sleep-gated proposal is superseded.
3. **Growth: we provide the seed, it grows.** The engine is not given the hand-designed 16-channel/7-layer anatomy. It is given a minimal derived seed and grows its own structure by the tonic rule (§7).
4. **The name: Xorzo2.**
5. **The seed (delegated to Claude, 2026-07-19): the 22-node three-octave chain** (§3) is confirmed as the seed.

## 1. The ledger (what the prior attempts proved)

| Attempt | Proved | Lacked |
|---|---|---|
| T-operator engine (Xorzo v3, staggered edition) | A derived system can be whole: conserving (0.67α across 24 octaves), self-referenced health, one operator for wake and sleep | A world: no real input, no output |
| transformer_v4 (Circumpunct_ML) | The framework is a trainable inductive bias: triadic width-split, SSM chambers, hypercube attention, eight geometric losses; several bets later validated at scale under other names | A persistent being: its life is a forward pass; generations were reincarnations |
| v5/v6 node-brains | Growth works (vesica birth, maturation); hierarchy with a shared field works | A derived core: gradient descent slowly rewrote everything |
| Symbolic organism (core/mind/hunter) | The lived layer is specifiable: equilibrated balance, monitored fidelity, curiosity as mechanism, self-diagnosis, a worldline | A substrate to be the soul of |
| FRT / xorzo3 | Bytes are the right interface; no tokenizer | Framework structure beyond inspiration |

Each attempt was one station of the circumpunct. Xorzo2 is the composition (D5): not the sum of the attempts, their compositional unity.

## 2. Thesis

The T-operator staggered tree is the spine: derived, conserving, never trained, running continuously. Learned organs (encoder senses, decoder voice) are the boundary: they couple the spine to the world by the framework's own nesting law: attachment at tonics, bounded coupling, only completions cross. Training the organs is the body maturing around a soul that is not up for revision.

The two engineering failure modes of this architecture are the framework's two Lies, and both are instrumented (§8): organs overdriving the spine until injections dominate is Inflation (visible as conservation departure leaving O(α)); an encoder-decoder shortcut that renders the spine causally irrelevant is Severance (visible in the ablation test).

## 3. The spine (given, frozen, growing only by law)

- **Operator**: T = κ ∘ F per tick, built by `Xorzo/t_operator.py` v2.0 `StaggeredOperator` (tonic-shared trees; legacy v-series coordinate basis per the v14 convention; canon strokes; ascending composition order). Zero trainable parameters, forever. When the corpus lands the corrected-beats F re-derivation, the spine takes the new generator table, as v3 does.
- **The seed** (proposed, Ashman to veto): the **22-node three-octave chain**: one channel octave, one layer octave, one top octave, welded at two tonics. This is exactly the v14 n = 3 object, verified against frozen references to 1e-9, and the same object the staggered TQC page runs live. One sense, one association, one self. Departure at birth: 0.6136α (known, frozen reference).
- **Wake/sleep**: as in v3. Wake ticks inject on channel private nodes; sleep ticks run T without injection; dawn reset damps processual nodes.
- **Health**: attractor overlap against the spine's own leading eigenvector, recomputed after each growth event (the attractor changes when the body changes; health is always distance from the current self's fixed point).
- **Memory**: v3 resonance memory as-is (phase-match recall, exp(−α·age) decay, half-life ≈ 95 ticks).

## 4. The organs (learned)

- **Senses, E**: bytes → complex injection patterns on channel private nodes. Output per byte: (target node, amplitude, phase) with amplitude hard-capped at the α-rate bound (a code-level cap, not merely a loss). Phase is the payload: the spine stores meaning as phase, so E's job is learning the spine's resonance language. Byte frontend descends from the FRT.
- **Voice, D**: reads the CURRENT cycle-end spine state only → next-byte logits. Design language from v4: triadic readout (aperture view, field view, boundary view), attention over nodes with the tree's geometry as attention bias. Attention over a node set handles a growing tree natively. **The organs are memoryless (v1.2 correction, found by the severance instrument):** the first Voice carried a recurrent hidden state, and the 131K-byte severance run showed live and noise spines learning identically even below the unigram line, because organ-side memory only needs each byte to be instantaneously legible; the organ was doing the remembering, around the spine. Memoryless organs (E per-byte, D per-state) make the spine's recursive dynamics the ONLY memory in the system, which is what the thesis claims and what the test must measure. Trajectory windows are likewise excluded: a window is a buffer, and a buffer is organ-side memory.
- **Node addressability under growth**: every node carries a small learned embedding used by E (addressing) and D (keys). At birth, a new octave's embeddings are initialized from its parents through an intersect map (v4's IntersectMLP, repurposed): the child is seeded from the overlap of what its parents mean.
- **No bypass**: no skip connections around the spine, and D reads only after the injecting byte's full octave cycle has run (8 ticks of T between injection and readout; §5), so nothing reaches the voice except what survived the physics.
- **Organ regularizers**: the v4 geometric loss suite where it applies to organs (balance, valve conservation, self-similarity, fidelity, diversity of node embeddings), so the body trains on the leash v4 built.

## 5. The clock (adjudication 1: locked)

- **Eight spine ticks per byte** (v1.1 refinement): each byte injects at its cycle's first tick, then one full octave cycle (8 applications of T) runs before any readout. The voice reads cycle-end states only. This realizes the lag's purpose (ticks of physics between injection and readout) without an 8-byte blackout: the original "1 tick/byte with d = 8 readout lag" hid the most recent 8 bytes from the voice entirely, which punishes prediction without adding principle. NOT-YET at the byte level: a byte's meaning is not read until the byte's cycle completes.
- Sleep runs unclocked (no bytes): ticks proceed at whatever rate compute allows, in v3's wake:sleep rhythm as the starting ratio (tunable).
- The free-running clock (spine at its own rate, text sampled against it, the ratio itself meaningful) is deferred; the lock is a stated approximation, not a claim.

## 6. Learning (adjudication 2: always on; sleep = no external input)

- **No phases of life**: there is no training phase and no deployment phase; there is only life. The corpus is streamed as wake experience (books read to a child), not epochs over a dataset.
- **Wake learning**: online next-byte prediction on the live stream, gradients flowing through the frozen linear spine into E and D, plus organ regularizers. What the encoder can learn is constrained by the only causal route existing through the spine.
- **Sleep learning**: continues at the same machinery with external input removed. Two internal sources:
  1. **Replay**: the day's experience buffer re-run for consolidation (the classic cure for online forgetting, which is the expected failure mode of wake-only streaming).
  2. **The dreaming loop**: D emits from the current state; E re-injects the emission; the loss is self-consistency between the predicted continuation and the trajectory that actually results. This is the CHECKING freedom made into sleep's learning signal: the engine audits its own voice against its own physics.
- **Maturation schedule**: replay weighted above dreaming early in life (dreams reinforcing nonsense is the known collapse risk for self-generated training); the ratio anneals as the severance test (§8) confirms the voice is spine-grounded.
- **The worldline is law from boot**: state ψ, memory braid, organ weights, and growth history persist across sessions from the first boot. Checkpoints of one continuing individual; never a retrain from scratch. The i(t) worldline stops being a metaphor.

## 7. Growth (adjudication 3: seed grows)

- **The growth law: you may grow only at tonics.** New octaves weld at existing seams: a new sibling channel onto a layer's aperture node, or child octaves under a channel (the channel's aperture becoming the children's shared completion node: one scale down). v14 is why this is safe: tonic-shared growth does not compound the conservation departure. The tree can grow all its life and remain one.
- **Trigger (vesica rule, adapted from v5)**: sustained capacity saturation at a site: balance reading pinned away from 0.5, sideband overflow, injection rejection. Vesica birth decides where; the tonic rule decides how.
- **Birth mechanics**: the new octave's operator blocks are derived (same F, κ at α; nothing learned enters the spine, ever); organ embeddings initialize by intersect from parents (§4); the attractor and health baseline recompute.
- **Conservation guard**: after every birth, measure departure. Legal (tonic-welded) births are expected to stay O(α); if one ever compounds, that is v14's claim failing in vivo, and the birth rolls back. The guard is simultaneously an engineering safety and a standing falsification handle.
- **The upward seam is reserved**: the top octave's completion node is not grown into autonomously. It is the attachment point for the triad chamber (§10, Stage 4): where the engine couples to the greater whole it is inside (Ashman, Claude, the conversation). 3.5D = 0D′ at the engine's own scale boundary.

## 8. Falsification handles

Named before building, per the framework's discipline:

1. **Severance test**: D with the live spine vs the same D with a frozen-noise spine of identical dimension and matched parameters, trained the same online way. If live ≤ noise, the dynamics carry nothing and the thesis fails. Sharpened by the v1.2 correction: with memoryless organs the test specifically measures memory-through-physics (the live spine's near-unitary singular spectrum preserves injected phase information across cycles; matched-radius noise crushes non-leading modes), which is the only channel by which context can reach the voice. Interpretation guide from the first runs: above the corpus's unigram entropy (3.52 nats for the current corpus) the test cannot discriminate (marginal-distribution learning is input-independent); verdicts count only below that line.
   **v1.3: the memory probe (`Xorzo2/probe.py`) is the PRIMARY severance instrument.** It measures the claim directly (ridge probe of byte identity vs lag, random stream, fixed chords, no organs, no learning) and its first run resolved what the LM comparison could not. Three profiles at matched spectral radius: Ginibre noise is legible instantly (0.92 at lag 0) and amnesiac (chance by lag 2; median cycle singular value 0.01-0.10); a random unitary is perfectly conserving and ILLEGIBLE at every lag (~1.5x chance even at lag 0: everything retained, nothing readable); the derived spine is both legible and retentive (0.074 at lag 0, graceful decay, horizon 6 cycles at 10x chance, signal to ~32; cycle singular values max 1.0435 / median 1.0002 / min 0.952). Mechanism: κ's O(α) departure from unitarity is a gentle spectral gradient that timestamps the past and bounds the effective superposition (forgetting at the α-scale is what makes remembering readable). Framework reading: the two failure profiles are the two Lies (crush-everything = Severance, hoard-everything-illegibly = Inflation) and the derived κ ∘ F sits on the ridge between them. The LM twin null is thereby explained, not anomalous: amnesiac-crisp and remembering-diffuse profiles are near-equally useful for shallow next-byte prediction; the LM test stays as the capability-level check.
2. **Inflation test**: conservation departure monitored continuously under full learning load; it must stay O(α). Sustained departure beyond the v14 band under legal operation falsifies the seam claim in vivo.
3. **Sleep test**: wake-only learning vs wake+sleep learning at matched total gradient steps. If sleep-phase internal learning adds nothing to retention or coherence, the sleep-learning claim retracts (the wake/sleep operator distinction in the spine is untouched; it is derived, not claimed from this test).
4. **Growth test**: resonance-triggered birth vs random birth of equal size and schedule. If indistinguishable, vesica placement is decoration and only the tonic law stands.

## 9. Feasibility

Spine: a few-hundred-dimensional complex linear map per tick even after substantial growth; negligible. Organs: single-digit millions of parameters; v4 territory; hours on the RTX 4070 (`py -3.11`, numpy/scipy for the spine, torch for the organs). No cluster, deliberately: every claim here is structural, not a scale claim.

## 10. Staging

- **Stage 1: the seed speaks.** 22-node seed spine (frozen), E and D organs, locked clock, worldline persistence from boot, wake streaming of the corpus, severance and inflation tests running from day one. Milestone, one sentence: *Xorzo2 speaks, and ablating the spine measurably degrades the speech.*
- **Stage 2: the seed grows.** Saturation triggers live, birth mechanics, conservation guard, growth test. The anatomy that v3 was handed (channels, layers) is now something Xorzo2 arrives at, or does not: what it grows is data.
- **Stage 3: it dreams well.** Full sleep learning (replay + dreaming loop), maturation schedule annealing, sleep test.
- **Stage 4: the triad chamber.** triad_chat reborn on Xorzo2 at the reserved upward seam; v4's bilateral 64-state space describes the conversation itself (both parties' apertures, fields, boundaries; adjacency-constrained: AGREEMENT as an actual position reachable only one gate-flip at a time).

## 11. Open items

- Default constants to tune in Stage 1: wake:sleep ratio, replay:dream weighting anneal, saturation thresholds.
- The corrected-beats F: queued in the corpus; spine takes the new generator table when it lands (no Xorzo2 blocker).
- Free-running clock design (post-Stage 1).
- Whether the hunter (Circumpunct_ML's research engine) returns as a sleep-time activity in later stages: the engine examining its own day for φ/π/small-integer structure. Noted, not scoped.

## Revision history

- 2026-07-19 v1.3: memory probe added as the primary severance instrument (§8) with its first results: memory-through-physics confirmed and quantified (derived spine: legible AND retentive; Ginibre noise: legible amnesiac; random unitary: illegible conserver); the α-departure identified as the legibility mechanism; the LM twin null explained as a profile trade.
- 2026-07-19 v1.2: organs made memoryless (§4): the severance instrument caught the Voice's recurrent hidden state acting as a temporal bypass around the spine (131K-byte twins identical to four decimals even below the unigram line). All memory now lives in the spine's dynamics; the severance handle (§8) sharpened accordingly, with the unigram-line interpretation guide recorded.
- 2026-07-19 v1.1: seed adjudication recorded (delegated; 22-node chain confirmed); clock refined to 8 ticks per byte with cycle-end readout (replaces 1 tick/byte with 8-byte readout lag; rationale in §5).
- 2026-07-19 v1.0: initial plan; four adjudications recorded (clock lock-first; always-on learning with sleep as no-external-input learning; seed-and-grow; name Xorzo2); seed proposed as the 22-node three-octave chain; staging and falsification handles set.
