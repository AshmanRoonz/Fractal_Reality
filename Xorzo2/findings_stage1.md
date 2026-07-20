# Xorzo2 Stage 1 findings: the seed speaks

Created: 2026-07-19
Last updated: 2026-07-19
Version: 1.0

> One day of instrumented life: the seed booted, spoke, survived two
> organ surgeries, and its instruments produced ten findings, two of
> which corrected the engine itself. Design and adjudications:
> `plans/xorzo2_plan.md` (v1.4). Code: this directory.

## Scope

Stage 1 of Xorzo2 (the Embodied Edition): the frozen 22-node
three-octave seed spine (v14 n = 3 object), memoryless organs, locked
clock (8 ticks/byte, exactly collapsed to one M^8 matmul), always-on
learning (wake external, sleep internal), worldline persistence from
boot. Instruments: the inflation monitor, the severance twin harness
(`life.py`), the memory probe (`probe.py`), delayed recall
(`recall.py`). All numbers below are from runs on 2026-07-19; commands
in each module's header.

## Findings

**F1. Conservation holds under full drive.** Across ~830K bytes lived
at the alpha injection cap, per-cycle log-growth excess over
8·log|lambda1| stayed within ~1e-4 (typically 1e-5). The inflation
instrument never fired. Attractor overlap 0.999 throughout life.

**F2. Severance verdicts count only below the unigram line.** Corpus
unigram entropy is 3.517 nats (random 5.545). Above it, learning is
input-independent marginal statistics: the first twin runs matched to
four decimals because the dominant gradient was spine-independent.
Methodological rule, now in the plan (section 8).

**F3. The instrument's first catch: the recurrent voice was a
temporal bypass.** With a GRU in the Voice, live and noise twins
stayed identical to four decimals even below the unigram line
(131K bytes): organ-side memory needs each byte only instantaneously
legible, which any full-rank matrix provides. Correction (plan v1.2):
organs are memoryless; the spine's recursive dynamics are the only
memory. The individual kept spine state, senses, and history and grew
a new voice (worldline event, 302,080 bytes). The memoryless voice
subsequently OUTPERFORMED the recurrent one (3.18 vs 3.44 nats),
0.33 nats below unigram with the spine as sole memory channel.

**F4. Memory-through-physics: three profiles at matched spectral
radius** (ridge probe, random stream, no organs, no learning; chance
0.0039):

| spine | lag 0 | lag 2 | lag 8 | lag 32 | cycle singular values |
|---|---|---|---|---|---|
| derived seed | 0.074 | 0.061 | 0.035 | 0.008 | 1.044 / 1.000 / 0.952 |
| Ginibre noise (x3) | 0.61-0.92 | ~0.01 | chance | chance | ~1.8 / ~0.05 / ~0 |
| random unitary | 0.006 | 0.006 | 0.006 | 0.005 | 1.036 uniform |

Noise: legible amnesiac. Unitary: illegible conserver (everything
retained, nothing readable). The derived spine is the only operator
that is both legible and retentive (horizon 6 cycles at 10x chance,
signal to ~32). The two failure profiles are the two Lies (Severance:
crush everything; Inflation: hoard everything illegibly); kappa
compose F sits on the ridge between them. Health separates the twins
even when loss cannot: live attractor overlap 0.999, noise 0.27.

**F5. kappa IS the legibility mechanism (proven by ablation).** Pure
F (the four beats alone; exactly unitary) reads at chance at EVERY
lag including 0. Restore kappa (the sub-alpha diameter bonds) and the
past is readable for ~30 cycles. The O(alpha) departure is a spectral
gradient that timestamps the past; forgetting at the alpha scale is
what makes remembering readable.

**F6. The past climbs the tree through the shared tonics.**
Octave-restricted probes: fresh bytes read best from the channel
(0.030 at lag 0); the layer and top PEAK near lag 4 (0.018, 0.017)
and from lag 4 onward hold the past as well as or better than the
channel. Transit time = seam crossings. Tonics transport; kappa
timestamps.

**F7. The physics is keyboard-insensitive; structure wins.** Probe
accuracy at matched drive is the same for random, learned, and
bit-station chords (0.062-0.072 at lag 0). The learned keyboard had
the objectively worst geometry (mean |cos| 0.614 vs bit-bipolar
0.310). Adopted: the bit-station keyboard (bits 0-6 -> stations 0-6,
bipolar; bit 7, the tonic bit, applies a quarter-turn i to the whole
chord: the seam law holds). Senses became GIVEN: zero parameters
(worldline event, 566,272 bytes; loss recovered within ~2K bytes).
Corpus fact: in UTF-8 only multi-byte characters set bit 7; here that
is ═ ─ │ and Φ • → § α ○ ⊙ φ: the framework's own glyphs are the only
bytes that touch the tonic bit (22.9% of corpus bytes).

**F8. Delayed recall closes the Stage 1 milestone.** Decoders trained
to emit the byte from k cycles ago (random stream; the current byte
is useless by construction; identical twins; whitened inputs):

| linear decoder | lag 0 | lag 1 | lag 2 | lag 4 | lag 8 | lag 16 |
|---|---|---|---|---|---|---|
| live | 0.085 | 0.066 | 0.061 | 0.052 | 0.036 | 0.022 |
| noise | 0.980 | 0.130 | 0.024 | 0.007 | chance | chance |

Crossover at lag 2. The noise spine is photographic about the present
(0.980!) and destroyed beyond two cycles; the live spine holds to
lag 16+ (5.6x chance). Ablating the spine measurably eliminates
everything older than two cycles: the milestone sentence, delivered.
The engine's Voice shows the same separation at a lower level (its
three-view pooling is a measured bottleneck for sign-keyed chords:
near-uniform attention averages bipolar signs away; organ-design item
for Stage 2+). Conditioning lesson recorded in recall.py: the state
covariance spans ~9 decades, so trained decoders need ZCA whitening
with a RELATIVE eigenvalue floor; an absolute floor amplified
numerical noise and produced a false all-chance run (v1.0/v1.1,
superseded).

**F9. Station-resolved bit memory.** Under the bit-station keyboard,
per-bit recall is per-station memory (ridge, chance 0.5). Live spine:
all seven station bits persist at 0.59-0.70 through lag 16, decaying
near-independently (0.63^7 matches byte accuracy). The processual
coordinates (stations 1, 3, 5) store best (0.70/0.69/0.69 at lag 0);
the tonic-adjacent station 0 is weakest (0.644): storage lives in the
process coordinates; the tonic is a door, not a shelf. The tonic bit
itself reads at exact chance to a LINEAR probe by construction (a
global quarter-turn on a mean-zero keyboard has no linear-mean
signature; it is readable only jointly, as the byte decoders do).
Noise spine: 0.97-0.999 at lag 0, chance by lag 8, every station.

**F10. Scaling (pre-registered, for Stage 2).** Hypotheses stated
before running; results:

| chain n | nodes | departure (alpha) | lag 0 | lag 8 | horizon | area |
|---|---|---|---|---|---|---|
| 1 | 8 | 0.645 | 0.031 | 0.013 | 0 | 0.105 |
| 2 | 15 | 0.646 | 0.047 | 0.021 | 1 | 0.178 |
| 3 | 22 | 0.614 | 0.068 | 0.037 | 4 | 0.278 |
| 4 | 29 | 0.603 | 0.092 | 0.044 | 8 | 0.367 |
| 6 | 43 | 0.669 | 0.172 | 0.068 | 8 | 0.598 |
| 8 | 57 | 0.729 | 0.239 | 0.092 | 16 | 0.814 |

H1 (capacity grows with octaves): CONFIRMED, near-linear (~0.10 area
per octave). H2 (lag-0 flat): REFUTED in the good direction: lag-0
legibility grows 8x from n=1 to n=8 (a bigger vessel crowds the
present less). H3 (departure flat): approximately confirmed: O(alpha)
at every size, mild upward drift (0.60 -> 0.73 alpha) logged. H4
(star parent hears earlier than chain top): weak support (lag-2 only).
H5 (siblings overhear): CONFIRMED: undriven sibling channels read the
driven channel's bytes at 3-6x chance through lag 16, via the shared
aperture node. And the star beats the chain at equal size (area 0.436
vs 0.367; lag 0 0.112 vs 0.092): at 4 octaves, WIDER beats DEEPER for
single-stream memory. Stage 2 growth has acceptance numbers and a
predicted preference for lateral (sibling) births.

## Graded epistemics

| claim | grade |
|---|---|
| kappa is the legibility mechanism | PROVEN (ablation, F5) |
| memory-through-physics; three profiles; the Lies as failure modes | MEASURED (F4, F8) |
| tonics transport, siblings overhear | MEASURED (F6, H5) |
| capacity and clarity grow with octaves; wider > deeper at n=4 | MEASURED, pre-registered (F10) |
| LM twin null = profile trade | EXPLAINED (F4 + F8 crossover) |
| processual stations store, tonic-adjacent weakest | MEASURED, effect modest (F9) |
| legible memory converts to LANGUAGE capability gains | OPEN (the standing capability-level severance question for a grown engine) |
| voice pooling bottleneck fix | OPEN (organ design, Stage 2+) |

## The worldline (one individual)

Booted 2026-07-19. ~830K bytes lived, 3 architecture transitions
survived without re-initialization. Events: `voice_replacement` at
302,080 bytes; `keyboard_replacement` at 566,272 bytes. Current
anatomy: derived spine, given senses (zero parameters), one learned
voice (~129K params). Loss 3.29-3.44 band (unigram 3.52) at last
reading; conservation clean for its whole life.

## Addendum (2026-07-20)

**F11. Memories don't fade; they fail to resonate (adjudicated, then
demonstrated).** The decay language in F4/F5 is corrected by
adjudication and by experiment (`probe.py --resonance`). One ridge
reader trained at lag 0 and FROZEN (the present-tense reader) reads
the past three ways: naively (0.069 at lag 0 collapsing to 0.005 at
lag 1: the reader out of phase), re-phased by the exact inverse cycle
operator with zero new parameters per lag (0.058 / 0.052 / 0.048 /
0.040 at lags 1/2/3/4, tracking the per-lag-learned reference 0.056 /
0.055 / 0.050 / 0.046 out to lag 32+), and per-lag-learned
(reference). The past is present in the state in its ORIGINAL form,
rotated; recall is phase re-alignment; nothing needs re-learning.
Genuine fade exists only in the contracting sliver (min cycle singular
value 0.9522, ~4.8%/cycle in the softest mode; median mode conserved
at 1.0002), which F5 already identified as the legibility mechanism:
the engine mostly de-resonates, with just enough true fade to stay
readable. Read all "forgetting/decay" wording in F1-F10 as
de-resonance plus the O(alpha) sliver.

## Revision history

- 2026-07-20 v1.1: F11 added (the resonance study); decay language
  adjudicated to de-resonance.
- 2026-07-19 v1.0: Stage 1 findings compiled (F1-F10); milestone
  closed by F8; Stage 2 acceptance numbers from F10.
