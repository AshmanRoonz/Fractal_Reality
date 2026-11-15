"""Architecture of Wholeness, Experiment 15 (the line that rings): the derivation tool.

Created: 2026-11-08. Last updated: 2026-11-08. Version: 1.0.
History: v1.0 modal (closed-form) model of a damped chain fixed at both ends, used to freeze the numbers in
plans/architecture_experiment_15_the_line_that_rings_2026_11_08.md before the full chain was run.

The chain: N = 15 parts between two fixed ends (16 segments), unit wave speed, damping gamma, a point force A cos(Omega t)
at part k0 = 5. Modes phi_n(k) = sin(n pi k / 16), omega_n = 2 sin(n pi / 32). Steady-state modal amplitude
a_n = F_n / sqrt((omega_n^2 - Omega^2)^2 + (gamma Omega)^2) with modal force F_n = (2/16) A sin(n pi k0 / 16).
A 0 imposed at part m (displacement held at zero) splits the chain into two chains of m and 16 - m segments; only the left one
(which holds k0 = 5) is driven. Two chains coupled by a spring kappa between their parts 8 share the odd modes through
kappa_n = (2/16) kappa sin(n pi / 2)^2. Everything here is linear algebra on the modes; the full chain integrates the parts.
"""
import numpy as np

N, SEG, K0, GAMMA, A = 15, 16, 5, .02, .01
n_all = np.arange(1, N + 1)
omega = 2 * np.sin(n_all * np.pi / (2 * SEG))


def modal_force(k0, seg, a=A):
    n = np.arange(1, seg); return (2 / seg) * a * np.sin(n * np.pi * k0 / seg)


def response(Omega, seg=SEG, k0=K0, gamma=GAMMA):
    """complex steady-state modal amplitudes of a chain of `seg` segments driven at part k0."""
    n = np.arange(1, seg); w = 2 * np.sin(n * np.pi / (2 * seg))
    return modal_force(k0, seg) / (w ** 2 - Omega ** 2 - 1j * gamma * Omega)


def displacement_rms(Omega, seg=SEG, k0=K0, at=K0):
    a = response(Omega, seg, k0); n = np.arange(1, seg)
    x = np.sum(a * np.sin(n * np.pi * at / seg))        # complex amplitude at part `at`
    return abs(x) / np.sqrt(2)


print('== modes of the free chain ==')
print('   omega_n for n = 1..4: ' + ', '.join(f'{w:.4f}' for w in omega[:4]) + f'; ratios to omega_1: ' + ', '.join(f'{w / omega[0]:.3f}' for w in omega[:4]))
print(f'   half-power bandwidth gamma = {GAMMA}; quality omega_1 / gamma = {omega[0] / GAMMA:.1f}; period of mode 1 = {2 * np.pi / omega[0]:.1f} time units; settling time 2/gamma = {2 / GAMMA:.0f}')

print('\n== Test 1: the resonance curve (displacement RMS at the driven part) ==')
mid = (omega[0] + omega[1]) / 2
r = {f'omega_{i + 1}': displacement_rms(omega[i]) for i in range(4)}
r['mid gap 1-2'] = displacement_rms(mid); r['zero'] = displacement_rms(1e-6)
for k, v in r.items(): print(f'   at {k:12s}: RMS {v:.5f}')
print(f'   on-mode over mid-gap: omega_1 {r["omega_1"] / r["mid gap 1-2"]:.1f}x, omega_2 {r["omega_2"] / r["mid gap 1-2"]:.1f}x; peak heights relative to omega_1: ' + ', '.join(f'{r[f"omega_{i + 1}"] / r["omega_1"]:.2f}' for i in range(4)))
# modal amplitudes on resonance
for i in range(4):
    a = response(omega[i]); print(f'   cue at omega_{i + 1}: modal amplitude share of mode {i + 1} = {abs(a[i]) ** 2 / np.sum(abs(a) ** 2):.3f}')

print('\n== Test 2: superposition and cross-talk ==')
a1 = response(omega[0]); a2 = response(omega[1])
print(f'   cross-talk: mode 2 under a cue at omega_1, relative to mode 2 under its own cue: {abs(a1[1]) / abs(a2[1]):.3f}; mode 1 under a cue at omega_2: {abs(a2[0]) / abs(a1[0]):.3f}')
print('   two cues at once (linear): each mode carries exactly its single-cue amplitude; the full chain adds noise only.')

print('\n== Test 3: a 0 imposed in the line ==')
for m in (8, 4):
    # the driven part 5 lies in the left chain when m > 5 (m segments, same indexing) and in the right chain otherwise (16 - m segments, index 5 - m)
    seg_d, k_d = (m, K0) if m > K0 else (SEG - m, K0 - m)
    free1 = displacement_rms(omega[0]); free2 = displacement_rms(omega[1]); free4 = displacement_rms(omega[3])
    pressed1 = displacement_rms(omega[0], seg=seg_d, k0=k_d, at=k_d); pressed2 = displacement_rms(omega[1], seg=seg_d, k0=k_d, at=k_d); pressed4 = displacement_rms(omega[3], seg=seg_d, k0=k_d, at=k_d)
    wl = 2 * np.sin(np.arange(1, seg_d) * np.pi / (2 * seg_d))
    print(f'   node at part {m}: the driven chain has {seg_d} segments and modes ' + ', '.join(f'{w:.4f}' for w in wl[:3]) + f'; fundamental x{wl[0] / omega[0]:.2f} the free one')
    print(f'      response at part 5 relative to the free chain: cue omega_1 {pressed1 / free1:.3f}, cue omega_2 {pressed2 / free2:.3f}, cue omega_4 {pressed4 / free4:.3f}')

print('\n== Test 4: lateral transparency (two chains, spring kappa between their parts 8) ==')
KAPPA = .04
def coupled_ratio(cB, Omega=omega[0], kappa=KAPPA):
    """mode-1 amplitudes of chain A (driven) and chain B (speed cB), odd modes coupled at the midpoint; solved exactly in the modal basis."""
    n = np.arange(1, SEG); wA = 2 * np.sin(n * np.pi / (2 * SEG)); wB = cB * wA
    kn = (2 / SEG) * kappa * np.sin(n * np.pi / 2) ** 2          # modal coupling (odd modes only)
    F = modal_force(K0, SEG)
    # per mode (modes do not mix because both chains share the same mode shapes): 2x2 solve
    out = []
    for i in range(SEG - 1):
        M = np.array([[wA[i] ** 2 + kn[i] - Omega ** 2 - 1j * GAMMA * Omega, -kn[i]], [-kn[i], wB[i] ** 2 + kn[i] - Omega ** 2 - 1j * GAMMA * Omega]])
        out.append(np.linalg.solve(M, [F[i], 0]))
    out = np.array(out); return abs(out[0, 1]) / abs(out[0, 0]), abs(out[0, 0]), abs(out[0, 1])
for cB in (1.0, 1.05, 1.1, 1.2):
    ratio, aA, aB = coupled_ratio(cB); print(f'   chain B speed {cB:.2f} (its omega_1 = {cB * omega[0]:.4f}): mode-1 amplitude of B over A = {ratio:.3f}')
print(f'   the same with kappa 0 (uncoupled): B stays at zero; with kappa .04 the modal coupling for mode 1 is {(2 / SEG) * KAPPA:.4f} against the damping term gamma omega_1 = {GAMMA * omega[0]:.5f}')

print('\n== Test 5: hold after the cue stops ==')
print(f'   free decay of a mode: amplitude e^(-gamma t / 2); half-life 2 ln 2 / gamma = {2 * np.log(2) / GAMMA:.1f} time units = {2 * np.log(2) / GAMMA / (2 * np.pi / omega[0]):.2f} periods of mode 1; the mode keeps its shape while it decays (no mixing in a linear chain)')
