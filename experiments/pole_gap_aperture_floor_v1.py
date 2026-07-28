"""Is the measured aperture floor the analytic one?

Created: 2026-07-28
Last updated: 2026-07-28
Version: 1.0
History:
- 2026-07-28 v1.0: initial. The three-term experiment measures
  H(Y|O) = 0.46709 while the analytic floor is h2(0.1) = 0.46900. The 0.0019
  gap is too large for plug-in bias at n = 400,000. This checks the realised
  noise rate: p = 0.09940 gives h2 = 0.46710, matching to 1e-5. Sampling
  variation in the source, not estimator bias.

See plans/pole_gap_and_the_octave.md section 7.
Run: py -3.11 experiments/pole_gap_aperture_floor_v1.py
"""
import numpy as np, math
rng = np.random.default_rng(11)          # same seed as the experiment
N = 400_000
a, b = 0, 1
flips = 0
for t in range(N+4):
    na = a ^ b
    f = 1 if rng.random() < 0.10 else 0
    flips += f
    nb = a ^ f
    a, b = na, nb
p_emp = flips/(N+4)
h2 = lambda p: -(p*math.log2(p) + (1-p)*math.log2(1-p))
print(f"  nominal p = 0.10        h2 = {h2(0.10):.5f}")
print(f"  realised  p = {p_emp:.5f}   h2 = {h2(p_emp):.5f}")
print(f"  measured H(Y|O)         = 0.46709")
print(f"\n  |h2(realised) - measured| = {abs(h2(p_emp)-0.46709):.5f}")
print(f"  |h2(nominal)  - measured| = {abs(h2(0.10)-0.46709):.5f}")
print("\n  -> the 0.0019 gap is sampling variation in the REALISED noise rate,")
print("     not estimator bias. dh2/dp = log2(9) = 3.17, so a 6e-4 shift in p")
print("     moves the floor by ~0.002 bits.")
