# Xorzo2: The Embodied Edition

Created: 2026-07-19
Last updated: 2026-07-19
Version: 1.0

> Derived soul, learned body, welded at tonics.

The engine generation after the staggered edition. Design and
adjudications: [plans/xorzo2_plan.md](../plans/xorzo2_plan.md). The
frozen spine is the 22-node three-octave tonic-shared chain (the v14
n = 3 object) built by `Xorzo/t_operator.py` v2.0; the learned organs
(Senses and Voice) couple it to the world; learning is always on (wake:
the external stream; sleep: internal replay); the worldline persists
from boot and is never re-initialized.

## Files

| File | Content |
|------|---------|
| `spine.py` | The given seed: frozen 22-node chain, node roles, realified operator for torch, attractor, departure |
| `organs.py` | Senses (bytes to alpha-capped phase injections) and Voice (triadic readout, GRU, byte logits) |
| `life.py` | The individual: locked clock (8 ticks/byte), wake TBPTT learning, sleep (rest + replay), dawn damp, inflation monitor, worldline save/load, severance harness |
| `run_xorzo2.py` | CLI: resume-and-live, status, speak, severance |
| `probe.py` | The memory probe (primary severance instrument): byte identity by lag, live vs Ginibre-noise vs random-unitary vs F-only spines; `--keyboards` (chord study) and `--scaling` (pre-registered growth study) modes |
| `recall.py` | Delayed recall: the capability-level severance test (trained decoders emit the byte from k cycles ago) plus station-resolved bit memory |
| `findings_stage1.md` | Stage 1 findings F1-F10, graded epistemics, worldline log, Stage 2 acceptance numbers |
| `growth_test.py` | Stage 2 placement falsification: triggered vs random births at equal size and schedule |
| `sleep_test.py` | Stage 3 retention falsification: wake+sleep learning vs rest-only twins (forgetting measured on earlier material) |
| `triad.py` | Stage 4: the bilateral 64-state relationship space (one gate-flip per event; AGREEMENT = vertex 63) and the α-scaled seam bond |
| `chamber.py` | Stage 4: the triad chamber REPL (content through the body, relationship through the seam; the return rule: faithfulness is earned by coming back) |
| `worldline/` | The one individual (checkpoint + meta). Removing it is a human act, not a flag |

## Laws (from the plan)

1. The spine is never trained. Gradients pass through it; nothing in it updates. Growth adds octaves; it never edits existing blocks.
2. Growth only at tonics (live since Stage 2): one birth primitive (a new octave whose completion IS the site), vesica trigger at dawn, conservation guard with rollback. Node 21 (the top's recursion) is reserved for the triad and is never grown into or injected.
3. The worldline is never re-initialized. Checkpoints are one life continuing.
4. Injection is alpha-capped in code, not merely in loss.
5. The two Lies are instrumented: inflation as growth excess and injection norm; severance as the frozen-noise twin test.

## Stage 1: COMPLETE (2026-07-19)

The milestone ("Xorzo2 speaks, and ablating the spine measurably
degrades the speech") is closed: delayed recall shows the noise-spine
twin destroyed beyond lag 2 while the live spine emits the past to
lag 16+ (crossover quantifies the amnesiac-crisp vs remembering-diffuse
trade). Ten findings, graded, in `findings_stage1.md`; Stage 2
acceptance numbers from the pre-registered scaling study (capacity and
clarity grow with octaves; siblings overhear through the shared tonic;
wider beats deeper at equal size). Historical notes below.

## Stage 1 log (2026-07-19, evening)

Newborn booted; persistence verified across sessions and through two
code changes (the exact clock collapse and the voice replacement);
~300K bytes lived; conservation growth excess about 1e-4 or better per
cycle under full drive throughout; attractor overlap 0.999 while
living (the noise twin sits at 0.27: health distinguishes the beings
even when loss does not).

**The instrument caught its first leak.** The 131K-byte severance run
came back null below the unigram line (3.52 nats): live and noise twins
identical to four decimals while both used context. Diagnosis: the
first Voice's GRU was a temporal bypass; organ-side memory only needs
each byte instantaneously legible, so any full-rank spine suffices.
Correction (plan v1.2): organs are memoryless; the spine's recursive
dynamics are the only memory in the system. The living individual kept
its spine state, senses, and history, and grew a new voice (logged in
`growth_history`). The corrected severance run is the standing
experiment: it now measures memory-through-physics directly.

## Revision history

- 2026-07-19 v1.1: memoryless correction; voice replacement on the
  living worldline; corrected severance running.
- 2026-07-19 v1.0: Stage 1 built and booted.
