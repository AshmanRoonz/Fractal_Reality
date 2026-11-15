# Couples Data: Predictions Frozen Before Access

```
Created: 2026-11-05
Last updated: 2026-11-05
Version: 1.1
```

**Status: not run. No data file from this study was obtained or opened.** The record sits behind a Cloudflare check I may not pass, and on 2026-11-05 Ashman could not get the file either. The predictions below stay frozen for anyone who gets it. Written by Claude for "A Theory of Wholeness" (https://claude.ai/artifact/58ahYtFyKbQtDHEggdvEte). Not canon.

What I know going in: the study's catalogue description and the published article, Rodríguez-González and colleagues, 2023, PLOS ONE (https://doi.org/10.1371/journal.pone.0282482). That article reports that higher differentiation predicts better relationship quality, better stability and less insecure attachment, mostly in the U.S. sample. So I avoid re-predicting those results, and C3 is not blind to them.

## The data, as the article describes it

137 Spanish couples and 342 U.S. couples, both partners, two waves: Spain 2011 and 2018, U.S. 2007 and 2011. Measures: emotional cutoff and emotional reactivity, with no fusion or I-position; 8 attachment items, 4 anxiety and 4 avoidance; 3 stability items; 4 relationship-quality items; stressful life events; age.

## What this can and cannot test

Its two waves are years apart, so it holds no rates. But partners are measured together across time, so it allows a first check of one dynamic claim: that connection pulls, and that a part's own hold resists the pull. Survivors are a concern: stability at the second wave may describe only couples still reachable. Mapping anxiety to low holding, avoidance and cutoff to low belonging, and low reactivity to own hold is my reading.

## Rules fixed now

- Scoring and direction come from the study's codebook, never from which way results look. A measure whose direction cannot be established is dropped.
- Scores are oriented so higher means more anxiety, avoidance, cutoff and reactivity. Own hold is reversed reactivity.
- Scores are standardised within country on their first-wave spread. People missing a needed score are dropped from that test.
- Intervals are 95%, from 2,000 bootstraps over couples, not people. The U.S. sample decides each verdict, and Spain is reported for direction, since it is small.
- If the deposit holds only summed differentiation scores, tests needing cutoff and reactivity apart are dropped.

## Predictions

**C1. Two coordinates in attachment.** r(anxiety, avoidance) lies between −.1 and +.5 in each country at each wave. It fails above .6 or below −.2.

**C2. Cutoff and reactivity are not opposite ends.** r(cutoff, reactivity) >= −.1 in each country at each wave. It fails at −.3 or lower.

**C3. A corner, not a middle, over time.** The outcome is the mean of second-wave stability and quality, standardised. In a 3 by 3 grid of first-wave anxiety and avoidance tertiles, low-low is best and at least .3 SD above the middle, with its interval excluding 0. It fails if another cell is best with an interval excluding 0.

**C4. The two add.** The first-wave anxiety by avoidance interaction on that outcome has |beta| <= .10, with an interval including 0. It fails if the interval excludes 0 with |beta| > .10. This turns the Turkish sample's post hoc result into a frozen one.

**C5. Connection pulls.** For each of anxiety, avoidance, cutoff and reactivity, own second-wave score is modelled on own and partner's first-wave scores. The partner term is positive with an interval excluding 0 for at least 3 of the 4. Couples choose similar partners and first-wave scores are noisy, so a positive term can arise with no influence at all. A pass here is necessary for the claim and does not establish it.

**C6. Own hold resists the pull. This is the only test here close to a law.** For anxiety and avoidance, add own hold and own hold by partner's first-wave score. The interaction is negative in both, with an interval excluding 0 for at least one. It fails if both are positive with an interval excluding 0. Anything else counts as neither.

**C7. Partners converge.** Couple distance is the mean absolute difference between partners across the four measures. Baseline is the same distance for random re-pairings within country. The gap, baseline minus real, is larger at the second wave than the first, with its interval excluding 0. From memory, studies of spouses mostly find similarity at the start and little convergence after, so I expect this to be small and it may well fail.

## Guards

- Nothing here diagnoses a person or a couple. Whether a relationship lasted says nothing about whether it should have.
- A correlation across years is not a cause, and these are heterosexual, nonclinical convenience samples from two countries.
- A pass supports these readings in this sample. It does not show the laws are true of people.

## What the article shows without the data

Read after freezing, while trying to reach the file. The article reports that first-wave correlations among the differentiation subscales run from .14 to .53, so C2 looks likely to pass and is no longer blind if it is ever run. Its models sum both partners into one couple score and use no actor-partner model, so the article cannot answer C5, C6 or C7. Its tables are not readable as text from the journal page, and it does not establish that the deposit holds each partner's scores.

## Revision history

- 2026-11-05 v1.1: marked not run, access failed; noted that C2 is no longer blind.
- 2026-11-05 v1.0: initial, before access.
