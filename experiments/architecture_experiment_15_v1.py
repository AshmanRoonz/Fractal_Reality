"""Architecture of Wholeness, Experiment 15: the line that rings.

Created: 2026-11-08. Last updated: 2026-11-08. Version: 1.0.
History: v1.0 built after the plan's predictions were frozen (plans/architecture_experiment_15_the_line_that_rings_2026_11_08.md);
two indexing slips fixed before any test printed; after the first results Test 5's windows were repaired, Test 0 (noise floor) added
and the tests made selectable (argv: seeds, test ids, noise). Results (100 seeds, noise .002): 3 PASS (two cues at once 1.013/1.003;
lateral transparency .766/.502/.360/.236; hold decay .0094 against gamma/2 .010), 7 MISS, all where the derived signal sits at or
below the measured noise floor (.0174 at part 5; K5 fired); at noise .0005 every derived clause holds (peaks .19/.39/.58/.76; node at
8 gives .111/1.991/1.962; node at 4 gives .056/.073/1.318; on-mode over mid-gap 41 and 25 after the floor is removed, derived 44/28).
Full record in the plan's Results section.

A chain of N = 15 parts between two fixed ends, unit wave speed, damping GAMMA, driven by a point force at part K0 = 5 with
white force noise, integrated by RK4. Tests: 1 the resonance curve; 2 two cues at once; 3 a 0 imposed in the line (a part held
at zero); 4 two chains coupled at their midpoints (lateral transparency); 5 the hold after the cue stops. Everything is
measured from the parts' displacements; the mode shapes sin(n pi k / 16) are used only to read the result.
usage: python architecture_experiment_15_v1.py [seeds]   (default 100; writes CSVs to architecture_experiment_15_results/)
"""
import sys, time
from pathlib import Path
import numpy as np

N, SEG, K0, GAMMA, A = 15, 16, 5, .02, .01
DT, T_END, T0, T1 = .05, 600., 400., 600.          # settle until T0, measure T0..T1
KAPPA = .04
SEEDS = int(sys.argv[1]) if len(sys.argv) > 1 else 100
TESTS = sys.argv[2] if len(sys.argv) > 2 else '012345'   # which tests to run (0 = noise floor)
SIG = float(sys.argv[3]) if len(sys.argv) > 3 else .002   # white force noise per part (.002 is the frozen value)
TAG = '' if SIG == .002 else f'_sig{SIG:g}'               # files from a non-frozen noise level are tagged
OUT = Path(__file__).resolve().parent / 'architecture_experiment_15_results'; OUT.mkdir(exist_ok=True)
k = np.arange(1, N + 1)
PHI = np.sin(np.outer(np.arange(1, N + 1), k) * np.pi / SEG)       # PHI[n-1, k-1]
OMEGA = 2 * np.sin(np.arange(1, N + 1) * np.pi / (2 * SEG))


def simulate(cues, seeds, node=None, speed=None, coupled=None, cue_off=None, record=False):
    """cues: array (C,) of drive frequencies, or (C, 2) for two cues at once (sum of two cosines).
    node: part index (1-based) held at zero, or None. speed: wave speed per condition (C,) or None (1).
    coupled: if not None, a second chain B with speeds `coupled` (C,), coupled to A by a spring KAPPA between parts 8; returns both.
    cue_off: time after which the drive stops. Returns dict with windowed modal RMS and displacement RMS at K0 (and traces if record)."""
    cues = np.asarray(cues, float)
    if cues.ndim == 1: cues = cues[:, None]            # (C, 1) single cues; (C, 2) two cues at once, a 0 entry meaning none
    C = cues.shape[0]
    rng = np.random.default_rng(15_2026)
    c2 = (np.ones(C) if speed is None else np.asarray(speed, float)) ** 2
    nchain = 2 if coupled is not None else 1
    x = np.zeros((nchain, C, seeds, N)); v = np.zeros_like(x)
    cB2 = None if coupled is None else np.asarray(coupled, float) ** 2
    steps = int(round(T_END / DT)); n_rec = int(round((T1 - T0) / DT))
    sumsq_x = np.zeros((nchain, C, seeds)); sumsq_a = np.zeros((nchain, C, seeds, N)); count = 0
    trace = [] if record else None
    hold_env = [] if cue_off is not None else None

    def force(t):
        f = np.zeros((C, 1, N))
        drive = A * (np.cos(cues * t) * (cues > 0)).sum(1)
        if cue_off is not None and t >= cue_off: drive = drive * 0
        f[:, 0, K0 - 1] = drive
        return f

    def acc(x, v, t):
        xp = np.pad(x, ((0, 0), (0, 0), (0, 0), (1, 1)))
        lap = xp[..., 2:] - 2 * xp[..., 1:-1] + xp[..., :-2]
        a = np.empty_like(x)
        a[0] = c2[:, None, None] * lap[0] - GAMMA * v[0] + force(t)
        if nchain == 2:
            a[1] = cB2[:, None, None] * lap[1] - GAMMA * v[1]
            s = KAPPA * (x[1][..., 7] - x[0][..., 7])      # spring between the parts 8
            a[0][..., 7] += s; a[1][..., 7] -= s
        if node is not None: a[..., node - 1] = 0
        return a

    t = 0.
    for i in range(steps):
        noise = SIG * rng.standard_normal(x.shape) / np.sqrt(DT)
        k1v = acc(x, v, t) + noise; k1x = v
        k2v = acc(x + .5 * DT * k1x, v + .5 * DT * k1v, t + .5 * DT) + noise; k2x = v + .5 * DT * k1v
        k3v = acc(x + .5 * DT * k2x, v + .5 * DT * k2v, t + .5 * DT) + noise; k3x = v + .5 * DT * k2v
        k4v = acc(x + DT * k3x, v + DT * k3v, t + DT) + noise; k4x = v + DT * k3v
        x = x + DT / 6 * (k1x + 2 * k2x + 2 * k3x + k4x); v = v + DT / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
        if node is not None: x[..., node - 1] = 0; v[..., node - 1] = 0
        t += DT
        if t >= T0:
            a = (2 / SEG) * np.einsum('mcsk,nk->mcsn', x, PHI)
            sumsq_x += x[..., K0 - 1] ** 2; sumsq_a += a ** 2; count += 1
            if hold_env is not None and i % 20 == 0: hold_env.append((t, np.sqrt((a[0, :, :, 0] ** 2).mean(1))))
        if record and i % 4 == 0: trace.append((t, x[0, 0, 0].copy()))
    x_rms, a_rms = np.sqrt(sumsq_x / count), np.sqrt(sumsq_a / count)
    if nchain == 1: x_rms, a_rms = x_rms[0], a_rms[0]          # drop the chain axis for a single chain
    out = dict(x_rms=x_rms, a_rms=a_rms)
    if record: out['trace'] = trace
    if hold_env is not None: out['hold'] = hold_env
    return out


def write(name, header, rows):
    name = name.replace('.csv', TAG + '.csv')
    with (OUT / name).open('w', encoding='utf-8') as f:
        f.write(','.join(header) + '\n')
        for r in rows: f.write(','.join(f'{v:.6g}' if isinstance(v, (float, np.floating)) else str(v) for v in r) + '\n')


def ms(a): return f'{a.mean():.4f} ± {a.std(ddof=1) / np.sqrt(len(a)):.4f}' if len(a) > 1 else f'{a.mean():.4f}'


t_start = time.time()
print(f'Experiment 15, {SEEDS} seeds, tests {TESTS}, noise {SIG}. omega_1..4 = ' + ', '.join(f'{w:.4f}' for w in OMEGA[:4]))
grid = np.round(np.arange(.05, .86, .01), 4)
mid = (OMEGA[0] + OMEGA[1]) / 2

# ---------------------------------------------------------------- Test 0: the noise floor (no drive)
if '0' in TESTS:
    r0 = simulate(np.array([OMEGA[0]]), SEEDS, cue_off=0.)
    print(f'\nTest 0. noise floor without drive: RMS at part 5 {ms(r0["x_rms"][0])}; modal RMS of modes 1 to 4: ' + ', '.join(f'{v:.4f}' for v in r0['a_rms'][0].mean(0)[:4]))
    write('t0_noise_floor.csv', ['x_rms_at_5', 'a1', 'a2', 'a3', 'a4'], [(r0['x_rms'][0].mean(),) + tuple(r0['a_rms'][0].mean(0)[:4])])

# ---------------------------------------------------------------- Test 1: resonance curve
if '1' in TESTS:
  cues1 = np.concatenate([grid, OMEGA[:4], [mid]])
  r1 = simulate(cues1, SEEDS)
  xr = r1['x_rms'].mean(1); rows = []
  for i, w in enumerate(cues1): rows.append((w, xr[i], r1['x_rms'][i].std(ddof=1) / np.sqrt(SEEDS)) + tuple(r1['a_rms'][i].mean(0)[:4]))
  write('t1_resonance.csv', ['Omega', 'x_rms_at_5', 'se', 'a1', 'a2', 'a3', 'a4'], rows)
  peaks = []
  for n in range(4):
      sel = np.abs(grid - OMEGA[n]) <= .035; j = np.flatnonzero(sel)[np.argmax(xr[:len(grid)][sel])]; peaks.append(grid[j])
  on = {n: r1['x_rms'][len(grid) + n] for n in range(4)}; midr = r1['x_rms'][-1]
  print('\nTest 1. peaks of the sweep (grid step .01) at ' + ', '.join(f'{p:.2f}' for p in peaks) + ' against modes ' + ', '.join(f'{w:.4f}' for w in OMEGA[:4]))
  print('   RMS at part 5 on the modes: ' + '; '.join(f'omega_{n + 1} {ms(on[n])}' for n in range(4)) + f'; mid gap {ms(midr)}')
  print(f'   on-mode over mid-gap: omega_1 {(on[0] / midr).mean():.1f}x, omega_2 {(on[1] / midr).mean():.1f}x; heights relative to omega_1: ' + ', '.join(f'{(on[n] / on[0]).mean():.2f}' for n in range(4)))
  share = [(r1['a_rms'][len(grid) + n] ** 2)[:, n].sum() / (r1['a_rms'][len(grid) + n] ** 2).sum() for n in range(4)]
  print('   modal energy share of the cued mode: ' + ', '.join(f'{s:.3f}' for s in share))

# ---------------------------------------------------------------- Test 2: two cues at once
if '2' in TESTS:
  r2 = simulate(np.array([[OMEGA[0], 0.], [OMEGA[1], 0.], [OMEGA[0], OMEGA[1]]]), SEEDS)
  a = r2['a_rms']
  print(f'\nTest 2. mode 1: alone {ms(a[0, :, 0])}, with both cues {ms(a[2, :, 0])}, ratio {(a[2, :, 0] / a[0, :, 0]).mean():.3f}; mode 2: alone {ms(a[1, :, 1])}, with both {ms(a[2, :, 1])}, ratio {(a[2, :, 1] / a[1, :, 1]).mean():.3f}')
  print(f'   cross-talk: mode 2 under the omega_1 cue over mode 2 under its own: {(a[0, :, 1] / a[1, :, 1]).mean():.3f}; mode 1 under the omega_2 cue: {(a[1, :, 0] / a[0, :, 0]).mean():.3f}')
  write('t2_superposition.csv', ['condition', 'a1', 'a2', 'a3', 'a4'], [(c,) + tuple(a[i].mean(0)[:4]) for i, c in enumerate(('omega_1 alone', 'omega_2 alone', 'both'))])

# ---------------------------------------------------------------- Test 3: a 0 imposed in the line
if '3' in TESTS:
  cues3 = np.array([OMEGA[0], OMEGA[1], OMEGA[3]])
  free = simulate(cues3, SEEDS)['x_rms']
  rows = []
  print('\nTest 3. a part held at zero; RMS at part 5 relative to the free chain')
  for m in (8, 4):
      pressed = simulate(cues3, SEEDS, node=m)['x_rms']
      rel = pressed / free
      print(f'   node at part {m}: cue omega_1 {ms(rel[0])}, cue omega_2 {ms(rel[1])}, cue omega_4 {ms(rel[2])}')
      for i, w in enumerate(cues3): rows.append((m, w, rel[i].mean(), rel[i].std(ddof=1) / np.sqrt(SEEDS)))
  # sweep with the node at 8 to find the pressed fundamental
  rp = simulate(grid, SEEDS, node=8)['x_rms'].mean(1)
  jp = np.argmax(rp[grid < .5]); print(f'   with the node at 8 the first peak of the sweep sits at {grid[jp]:.2f} (free fundamental {OMEGA[0]:.4f}, free second mode {OMEGA[1]:.4f})')
  write('t3_node.csv', ['node', 'Omega', 'rel_rms', 'se'], rows)

# ---------------------------------------------------------------- Test 4: lateral transparency
if '4' in TESTS:
  speeds = np.array([1.0, 1.05, 1.1, 1.2])
  r4 = simulate(np.full(4, OMEGA[0]), SEEDS, coupled=speeds)
  ratio = r4['a_rms'][1][:, :, 0] / r4['a_rms'][0][:, :, 0]
  print('\nTest 4. two chains, spring between the parts 8, A driven at omega_1; mode-1 amplitude of B over A: ' + '; '.join(f'speed {s:.2f} {ms(ratio[i])}' for i, s in enumerate(speeds)))
  write('t4_transparency.csv', ['speed_B', 'ratio', 'se'], [(s, ratio[i].mean(), ratio[i].std(ddof=1) / np.sqrt(SEEDS)) for i, s in enumerate(speeds)])

# ---------------------------------------------------------------- Test 5: hold
if '5' in TESTS:
  r5 = simulate(np.array([OMEGA[0]]), SEEDS, cue_off=T0, record=True)
  tt = np.array([h[0] for h in r5['hold']]); env = np.array([h[1] for h in r5['hold']])[:, 0]    # seed-mean RMS of mode 1, every 20 steps
  per = int(round(2 * np.pi / OMEGA[0] / (20 * DT)))                                                # samples per period of mode 1
  idx = list(range(0, len(env) - per, per))
  e = np.array([np.sqrt((env[i:i + per] ** 2).mean()) for i in idx]); te = np.array([tt[i + per // 2] for i in idx])
  e0 = e[0]; half = te[np.flatnonzero(e <= e0 / 2)[0]] - T0 if (e <= e0 / 2).any() else np.nan
  floor = e[-3:].mean()                                                                              # late envelope = the noise floor
  mask = e > max(.05 * e0, 3 * floor); slope = np.polyfit(te[mask] - T0, np.log(e[mask]), 1)[0] if mask.sum() > 2 else np.nan
  # modal shape while decaying: which mode is largest in the first and the later periods
  A = np.array([h[1] for h in r5['hold']])  # only mode 1 was stored; use the recorded trace of seed 0 for the modal shape
  print(f'\nTest 5. cue off at t = {T0:.0f}: mode-1 envelope halves after {half:.1f} time units (derived 2 ln 2 / gamma = {2 * np.log(2) / GAMMA:.1f}); fitted decay rate {-slope:.4f} over the points above 3 times the late floor (derived gamma / 2 = {GAMMA / 2:.3f}); envelope at the cue\'s end {e0:.4f}, late floor {floor:.4f}')
  print('   envelope by period after the cue stops: ' + ', '.join(f'{v:.4f}' for v in e[:8]))
  write('t5_hold.csv', ['t_after_off', 'mode1_envelope'], [(t - T0, v) for t, v in zip(te, e)])
print(f'\n{time.time() - t_start:.0f} s')
