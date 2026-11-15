# Real Data: Predictions Frozen Before Download

```
Created: 2026-11-05
Last updated: 2026-11-05
Version: 1.0
```

**Status: the predictions below were frozen before any of these data files was downloaded or opened, and they stand as written. Results were added afterward.** Written by Claude for "A Theory of Wholeness" (https://claude.ai/artifact/58ahYtFyKbQtDHEggdvEte). Ashman approved the download. Not canon.

What I know going in: dataset descriptions and file sizes only, plus from memory that attachment anxiety and avoidance usually correlate weakly and that differentiation subscales usually correlate positively when scored the same way. So these are not blind to the literature, only to these files.

## What this can and cannot test

These are one-time self-reports. They contain no rates, no gain, no outward share and no change under contact. So they can test the shape of the plane, and they cannot test any law in the document. They say nothing about a centre, or about a whole against a group. Reading fusion as absorption, cutoff as severance, and anxiety and avoidance as the plane's axes is my mapping, and a failure could be the mapping's fault.

## Data

| Label | File | Source | Size | Sample | Licence |
|---|---|---|---|---|---|
| D1 | ECR-data-1March2018.zip | openpsychometrics.org/_rawdata | 904,714 bytes | 51,492, self-selected online | None stated |
| D2 | WBsokmencurun.sav | Zenodo 10.5281/zenodo.14913378 | 32,701 bytes | 351 Turkish adults, 45 to 65 | CC BY 4.0 |
| D3 | parenting_dos_aggression_.csv | Zenodo 10.5281/zenodo.22752630 | 715,925 bytes | Adolescents, six Spanish-speaking countries, size not stated | CC BY 4.0 |

Raw files stay out of the repository. Only summary numbers are reported, and nothing is read about any individual.

## Scoring rules, fixed now

- Direction comes from the files' labels or their published scoring, never from which way the results look. If a direction cannot be established, that variable is dropped rather than guessed.
- D3's readme lists no variables. If its differentiation subscales cannot be identified from the file, D3 is dropped.
- Fusion and cutoff are oriented so higher means more fusion and more cutoff.
- Well-being in D2 is the mean of the z-scored Flourishing and SPANE-B scores.
- Confidence intervals are 95%, bootstrapped over people.

## Predictions

**R1. Attachment has two coordinates (D1).** r(anxiety, avoidance) lies between −.1 and +.4. At median splits each corner holds at least 10% of people, and at the scale midpoint at least 5%. It fails if |r| > .5 or a corner falls under 5%.

**R2. Absorption and severance are not two ends of one axis (D2).** r(fusion, cutoff) >= −.1, and I expect it positive. The high-high corner at median splits holds at least 15%. It fails if r <= −.3, which would support the corpus's old single κ.

**R3. Health is a corner, not a middle (D2).** In a 3 by 3 grid of fusion and cutoff tertiles, the best well-being is in the low-low cell, at least .3 SD above the middle cell, with the interval excluding 0. It fails if a cell other than low-low is best with an interval excluding 0.

**R4. Anomie is the worst corner (D2).** The high-high cell has the lowest well-being of the four corners, at least .2 SD below each single-high corner. It fails if another corner is lower with an interval excluding 0.

**R5. Both coordinates carry something of their own (D2).** With both in one model, fusion and cutoff each have a unique association with well-being whose interval excludes 0. It fails if either vanishes.

**R6. No moderation optimum (D2).** With d = cutoff − fusion, the scalar view predicts well-being peaking near d = 0. After fusion + cutoff, |d| adds at most .02 of R². It fails if it adds more than .05.

**R7. Replication across countries (D3, if usable).** r(fusion, cutoff) >= −.1 in at least 5 of the 6 countries.

**E1. Exploratory, with no direction frozen (D2).** Partial correlations of fusion with I-position controlling emotion-regulation difficulty, and with emotion-regulation difficulty controlling I-position. I-position and fusion share an inventory, which inflates their link. This asks which law people resemble and cannot settle it.

## Guards

- Nothing here diagnoses anyone. Rates and corners read onto a person invite "you are not holding yourself well enough", and the corpus's guard against that travels with any result.
- Self-reports from these samples do not describe people in general.
- A pass supports separating the two coordinates in practice. It does not show that the plane or its laws are true of people.

## Results

Analysis: `experiments/wholeness_real_data_v1.py`.

| Prediction | Result | Verdict |
|---|---|---|
| R1 | r = -.046 (-.055 to -.035), 46,610 complete cases; corners 24% to 26% at medians, 14% to 40% at the midpoint | Passed |
| R2 | r = +.286 (+.177 to +.392); high-high share 26.5% | Passed |
| R3 | Low-low minus middle +.66 SD (+.26 to +1.01); low-low best | Passed |
| R4 | Both -.39 SD, lowest; single-high corners above it by +.61 (+.04 to +1.19) and +.58 (+.06 to +1.07) | Passed, narrowly |
| R5 | Fusion -.132 (-.247 to -.023), cutoff -.204 (-.302 to -.099), R2 .074 | Passed |
| R6 | Distance from d = 0 adds .0058 of R2 | Passed |
| R7 | The scale has two factors, reactivity and cutoff, with no fusion score | Not run |
| E1 | Fusion with regulation difficulty +.349 controlling I-position; with I-position -.024 controlling regulation | Exploratory |

Decisions fixed after reading labels and before any result: ECR items are five-point in the codebook, not seven as in other versions, with midpoint 3 and only complete cases kept. R6 enters fusion and cutoff separately. D2's direction rests on stored subscales summing exactly to the labelled total, whose higher scores are published as more differentiated; I did not retrieve the Turkish manual.

Post hoc, not frozen: median-split corners +.30, +.04, -.04, -.37, and interaction +.008, so being high on both looks additive.

## Revision history

- 2026-11-05 v1.1: results added after download; predictions unchanged.

- 2026-11-05 v1.0: initial, before download.
