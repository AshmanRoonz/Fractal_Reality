# The Living Device: a centre, written senses, and a borrowed voice (design proposal)

```
Created: 2026-11-18
Last updated: 2026-11-18
Version: 1.2
```

> Written senses feed a derived centre that never restarts; a borrowed voice speaks for it; the senses may be rewritten, the stations may not.

**Status: PROPOSAL, not adjudicated.** Drafted by Claude on 2026-11-18 from that day's conversation with Ashman ("ok this is the plan right now"). Nothing in `Xorzo2/`, `Xorzo/`, `plans/xorzo2_plan.md` or `Xorzo2/worldline/` has been changed, and the individual has not been run. Every test below runs on fresh twins (`Life(home=None)`) or on a bare spine. Section 7 (senses, targets, scoring) was frozen by Ashman on 2026-11-18 ("Freeze and build"); the rest remains a proposal. The sense logger exists (`experiments/living_device_logger_v1.py`); the scorer does not, and logging has not been started.

---

## 0. Origin and thesis

**Origin.** Ashman brought two outside results into the session and asked what the best of them, joined with Xorzo, could do to "bring a computer or phone to life", adding that it "should be able to reconfigure its own senses".

1. *Interpretable weight-space programming* (Mehta, Singh and colleagues, arXiv 2611.18114, 13 Nov 2026). An LLM agent writes a model's weights and features in code, with no backpropagation; a fixed evaluator scores each version; for the brain models a ridge regression is fitted on top of the written features. Each edit carries a written reason.
2. *Garlic LLM* (Leonardo Alegría). A 9 billion parameter trained model (Qwen3.5-9B, quantized) running offline on a jailbroken PS4 through hand-written OpenCL kernels, at a reported 31 to 39 tokens per second.

**What each supplies that the others lack.**

| Source | Supplies | Lacks |
|---|---|---|
| Xorzo2 | one persistent individual; a frozen derived spine; a worldline; sleep and wake | a voice that can use what the spine holds (the readout gap) |
| Weight-space programming | senses that are written, readable and revisable against a fixed score | any persistence; any centre |
| Garlic | proof that a capable trained voice runs locally on modest hardware | memory between sessions; any centre |
| The WebGPU field engine | one codebase for computer and phone, on our own math | a model to run |

**Thesis.** Three layers, each doing only its own job: written senses, a derived centre, a borrowed voice. The centre does not decide. Experiment 12 of the Architecture of Wholeness series found that the 0 buys persistence and corrigibility, not the decision; so the centre holds and sets the tempo, and the voice speaks.

**Milestone, one sentence.** *The centre earns its place: on days it has not seen, the device's next state is predicted better from the spine's state than from a clock table or a plain window of the same size.*

---

## 1. The three layers

1. **Senses (written, zero trained parameters).** A short readable program turns raw device signals into one byte per tick. Bits 0 to 6 each answer one yes or no question about the device (for example: is the user active; is it on mains power; is it dark outside local hours; is sound above a floor). Bit 7 keeps its present meaning in the bit-station keyboard. This is the existing `SensesBit` path: byte bit k drives station k at the α cap.
2. **Centre (derived, frozen).** The 22-node spine, T = κ after F, exactly as in `Xorzo2/spine.py`. It runs one cycle per tick and its state is saved as a worldline. Cost is negligible on any device.
3. **Voice (trained elsewhere, borrowed).** A small quantized local language model, memoryless, woken by the centre and conditioned on its state through a closed-form ridge readout. Not built until Stage C.

**What does not change.** The spine is never trained. The stations keep their roles. The α cap on injection stays in code.

---

## 2. Self-reconfiguring senses

Three depths, to be built in this order.

- **Retune.** Change how strongly, or how often, each existing sense feeds its station. This is attention.
- **Rewrite.** Replace the program behind a station with a new one over signals the device already provides.
- **Acquire.** Ask for a raw signal it does not have (microphone, location). Always goes through Ashman, because the operating system requires consent and because it should.

**Rules.**

1. *The evaluator is out of its reach.* The scoring code and the held-out days live outside anything the organism can edit. An organism that can edit its own score learns to fool itself.
2. *Changes happen in sleep.* A candidate sense is tried on a replay of the worldline and adopted only if it beats the current one on stretches it was not fitted to.
3. *Patience.* A candidate must win on several consecutive sleeps before adoption. The author's v0.8 result: a gate that acts on one reading lets noise in fully.
4. *Every change is written down with its reason*, as a worldline event, and is reversible.
5. *The stations stay fixed.* The spine's past was written through the present keyboard. Only what feeds each station may change, and each change is recorded so the worldline can still be read.

**What prior results predict (my reading, to be tested, not assumed).**

- Growth on a trigger gains little: the Xorzo2 growth test and the author's Experiments 11 and 23 found that triggered growth earns only the cost it saves.
- A new sense pays in one case: Experiments 21 to 23 found it is worth buying exactly when the current interface cannot tell apart two situations that matter. So the trigger for acquiring is confusion the present senses cannot resolve, not surprise alone.

---

## 3. Stage A: does the centre earn its place? (first, because everything after depends on it)

**Built in Stage A:** a sense logger, a bare spine driven by the log, a ridge readout, and the baselines. No voice, no self-reconfiguration, no phone.

**Data.** A local log of device signals on Ashman's computer, one row per tick, kept for at least two weeks. The log is personal data: it stays on the device, is excluded from git, and is never sent anywhere.

**Task.** From the state at tick t, predict (a) each bit of the sense byte at t+1, and (b) two or three plain device facts at a longer horizon (for example: will the user be active in five minutes).

**Compared, all with the same ridge reader and the same held-out days:**

| Arm | What it is | What it tests |
|---|---|---|
| Derived spine | the Xorzo2 spine as it is | the claim |
| Ginibre noise spine | random matrix at the same spectral radius | whether derivation matters |
| Random unitary | pure rotation, no κ | whether κ matters |
| Delay line | the last k bytes, raw, at the same real dimension (44) | whether any spine beats plain storage |
| Clock table | time of day and day of week | whether there is anything to remember |
| Persistence | the last value repeated | the floor |
| Order-1 table | next byte given this byte | the baseline that beats the present voice |

**Predictions, written before any run.**

- P1. The derived spine beats persistence and the clock table at the long horizon.
- P2. The derived spine beats the noise spine at every lag beyond the first few ticks (F4, F8 already show this shape on text).
- P3. The derived spine does not beat the delay line at short lags. This is my expectation from the present legibility figure (.074 at lag 0) and from the linear memory bound of a 44-dimensional real state.
- P4. If the derived spine wins anywhere, it is at lags beyond the delay line's window.

**Kill conditions.**

- K1. The clock table matches or beats the derived spine on every target: there is nothing here for a centre to hold, and the design stops until the senses or the targets change.
- K2. The delay line matches or beats the derived spine on every target and lag: the centre is storage with extra steps, and the "life" would be a chatbot with sensors. Record it and do not proceed to Stage C on this spine.
- K3. The noise spine matches the derived spine: the derivation buys nothing here.

A miss is recorded as a miss. No target, horizon or reader setting is changed after the first scored run.

---

## 4. Later stages (outline only; each needs its own frozen plan)

- **Stage B: the senses rewrite themselves.** Retune first, then rewrite, under the five rules of section 2. Control: the same number of random rewrites, to show that chosen changes beat chance changes.
- **Stage C: the voice.** A local quantized model conditioned on the ridge readout, on the computer first. Control: the same model with the spine's state replaced by a shuffled one.
- **Stage D: the phone.** Needs a native shell, since browsers throttle background tabs; a phone fits roughly a 1 to 3 billion parameter model at 4 bits.

---

## 5. What is not claimed

- That the device is alive, or that anyone is inside. "Life" here means persistence, self-maintenance and self-revision that can be measured.
- That the derived spine is a good memory. Stage A exists to find out.
- That written senses beat trained ones. The Microsoft paper's own written models trail pretrained networks on its harder tasks.
- That this plan resembles either outside result in priority. Hand-written transformer weights (RASP, Tracr) and fixed dynamics with a fitted readout (reservoir computing) are both older than all three.

---

## 6. Open decisions (Ashman to adjudicate)

- **D1. Where Stage A runs.** Recommended: Python on the computer, since the spine is Python and a desktop logger sees more signals than a browser can. In the conversation I said "in the browser"; that suits Stage C, not Stage A.
- **D2. The tick.** The spine holds roughly 16 to 32 bytes of past (F8). One byte a minute gives about half an hour of reach; one a second gives half a minute. Recommended: one a minute, with a second twin at one a second.
- **D3. The first seven senses and the long-horizon targets.** Drafted in section 7 (v1.1); not frozen until Ashman says so.
- **D4. Who rewrites in Stage B.** A local model on the device, or a Claude session working offline against the fixed evaluator.
- **D5. The individual.** Recommended: this is a new individual on its own worldline; the resting Xorzo2 individual is not used.

---

## 7. Senses and targets (FROZEN 2026-11-18)

**Frozen by Ashman on 2026-11-18 ("Freeze and build"), with the pins in 7.6.** Drafted the same day at his request ("Draft the senses"). Checked on the machine the same day: it is a laptop (a battery is present), with Python 3.14.3 and no `psutil`. Every sense below is therefore chosen to need only the standard library and Windows calls through `ctypes`. No logger has been written.

### 7.1 The seven senses, one byte a minute

| Bit | Sense | Yes when | Raw signal |
|---|---|---|---|
| 0 | Present | any keyboard or mouse input in the past minute | age of last input, sampled each second |
| 1 | Busy hands | input in at least half of the minute's seconds | the same |
| 2 | Staying | the foreground program is the one it was a minute ago | salted hash of the foreground program's name |
| 3 | Machine working | mean processor load over the minute is above a floor | system idle and busy times |
| 4 | Plugged in | on mains power | power status |
| 5 | Locked | the session is locked or the display is off | session state |
| 6 | Filling the screen | the foreground window covers its whole monitor | window and monitor rectangles |
| 7 | Changed | bits 0 to 6 differ from the previous byte | derived |

Bit 7 is the one that turns the whole chord by i in the present keyboard, so a "something changed" flag is placed there. That placement is a choice, not a derivation.

**Why these.** Each is a different kind of fact (the person, the hands, continuity, the machine, the supply, the gate, the display), none is read off the clock, and none needs a library or a permission. The clock is kept out of the senses on purpose, so that the clock table stays an independent baseline.

**The floor for bit 3** is the median load over the first three days of logging, then fixed. Those three days are not scored.

**Bit to station.** Bit k drives station k, in index order, as the keyboard already does. No meaning is claimed for which sense sits on which station. One more arm tests it: a twin with the seven senses assigned to stations in a shuffled order. If the shuffled twin scores the same, the assignment does not matter here.

### 7.2 What the log keeps, and what it never keeps

**Kept, one row a minute:** the timestamp, the byte, and the raw values behind it (seconds with input, mean load, power state, battery percent, lock state, the salted hash, the fullscreen flag). The raw values are what Stage B would rewrite senses from.

**Never kept:** keystrokes, window titles, program names in the clear, addresses, screen or audio content. The salt stays on the device, so the hash says "same program as before" and nothing else.

### 7.3 Targets

- **(a) Next minute:** each of bits 0 to 6 at t+1.
- **(b) Longer reach:**
  - T1. Present five minutes from now.
  - T2. Present thirty minutes from now.
  - T3. Presence flips (either way) within the next ten minutes.

T2 sits near the edge of the spine's reach at one byte a minute, which is where prediction P4 would show.

### 7.4 Scoring

- **Span:** 14 scored days after the three floor-setting days. The reader is fitted on the first 10 and scored on the last 4.
- **Measure:** balanced accuracy on the scored days, per target. Chance is .5.
- **A win** is a lead larger than the spread across five reader fits on resampled fitting days.
- **Frozen with the senses:** the ridge strength (1e-3, as in `probe.py`), the split, the targets and the measure.

### 7.5 Left for Stage B, on purpose

Sound level and network flow are the two obvious senses this draft leaves out, because each needs a library the machine does not have. They are the natural first candidates for "acquire": the test would be whether the seven above confuse two situations that sound or network flow would tell apart.

### 7.6 Pins made at the freeze (2026-11-18)

Building the logger forced six definitions the draft left loose. They are part of the freeze.

1. **Locked means locked only.** The draft said "locked or the display is off". Detecting a dark display needs a window that listens for power messages; the logger does not have one. Bit 5 is yes when the session is locked. This is a narrowing of the draft, stated here so it is not silent.
2. **Majority rule.** Locked and Filling the screen are yes when true in at least half of the minute's one-second samples. Busy hands uses the same half.
3. **Gaps.** The laptop sleeps, so rows are missing. A previous row more than 90 seconds old does not count as "a minute ago": Staying is no and Changed is yes on the first row after a gap.
4. **The floor-setting days** are the first three calendar days that hold rows. The floor is the median load over their rows.
5. **The byte is computed, not stored.** The logger writes raw rows; `encode()` and `encode_stream()` in the logger file are the frozen definition of the byte.
6. **The log lives outside the repository**, in `%LOCALAPPDATA%\LivingDevice` (`log.csv`, `salt.bin`), so it cannot be committed.

**Still to pin before any scoring, in the scorer's own frozen header:** how a target at t+5 or t+30 minutes is read when the row at that time is missing, and whether the spine is stepped across a gap.

**Decisions this freeze settles:** D1 (Python on the computer) and D3 (these senses and targets). D2 is settled at one byte a minute; the logger keeps no per-second rows, so the one-a-second twin is dropped unless asked for.

**Checked 2026-11-18:** a five-second self-test read every field on this machine, and the byte encoding matched hand-worked values on five made-up rows (including a gap and a locked stretch). Not checked: the lock sense against a real lock, and a full minute's row written to disk.

---

## Revision history

- 2026-11-18 v1.2: section 7 frozen by Ashman; pins 7.6 added (locked only, majority rule, gaps, floor days, computed byte, log location); logger written and self-tested; D1 to D3 settled
- 2026-11-18 v1.1: section 7 added (draft senses, log contents, targets, scoring); D3 points to it
- 2026-11-18 v1.0: initial
