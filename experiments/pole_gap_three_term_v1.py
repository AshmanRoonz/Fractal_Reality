"""Three-term decomposition of the Pole Gap: aperture, integration, learning.

Created: 2026-07-28
Last updated: 2026-07-28
Version: 1.0
History:
- 2026-07-28 v1.0: initial. Verifies that Gamma_rep = I(Y;X|M) splits into
  I(Y;X|O) + I(Y;O|M), separating loss no observer of O can recover from loss
  a better-memoried observer can. Checks the screening condition rather than
  assuming it.

See plans/pole_gap_and_the_octave.md section 7.
Run: py -3.11 experiments/pole_gap_three_term_v1.py
"""
"""Does Gamma_rep split into aperture loss + integration loss?

Claim:  I(Y;X|M) = I(Y;O|M) + I(Y;X|O)   when M = f(O) and the full state
screens off the past.  The algebra is telescoping; the NON-trivial part is
the screening condition H(Y|X,O) = H(Y|X), which must be checked.

  I(Y;X|O)  = destroyed at the aperture   -> NO observer of O recovers it
  I(Y;O|M)  = discarded in integration    -> a better-memoried observer does
  E[KL]     = not yet learned             -> more data does
"""
import numpy as np, math
from collections import Counter

rng = np.random.default_rng(11)
N = 400_000
# X = (a,b). a' = a xor b ; b' = a with 10% flip noise (so it is genuinely
# stochastic and the screening condition is not vacuous).
a, b = 0, 1
X, O, Y = [], [], []
for t in range(N+4):
    X.append((a, b)); O.append(a)
    na = a ^ b
    nb = a ^ (1 if rng.random() < 0.10 else 0)
    a, b = na, nb
    Y.append(a)                       # Y_t = a_{t+1}, the next observable

def Hc(pairs):
    """H(target | cond) from a list of (cond, target)."""
    byc = {}
    for c, y in pairs:
        byc.setdefault(c, Counter())[y] += 1
    tot = len(pairs); H = 0.0
    for c, cnt in byc.items():
        n = sum(cnt.values())
        H += (n/tot)*sum(-(v/n)*math.log2(v/n) for v in cnt.values() if v)
    return H

W = 3                                  # O_<=t proxy: last 3 observations
idx = range(W, N)
Ohist = [tuple(O[t-W+1:t+1]) for t in idx]
Mmem  = [O[t] for t in idx]            # limited observer: memory depth 1
Xs    = [X[t] for t in idx]
Ys    = [Y[t] for t in idx]

H_Y_M  = Hc(list(zip(Mmem, Ys)))
H_Y_O  = Hc(list(zip(Ohist, Ys)))
H_Y_X  = Hc(list(zip(Xs, Ys)))
H_Y_XO = Hc(list(zip([(x, o) for x, o in zip(Xs, Ohist)], Ys)))

print(f"  H(Y|M)   = {H_Y_M:.5f}   (memory depth 1)")
print(f"  H(Y|O)   = {H_Y_O:.5f}   (full observation window)")
print(f"  H(Y|X)   = {H_Y_X:.5f}   (full state)")
print(f"  H(Y|X,O) = {H_Y_XO:.5f}")
print(f"\n  screening check  H(Y|X,O) == H(Y|X) ?  "
      f"|diff| = {abs(H_Y_XO-H_Y_X):.2e}")

gamma_rep = H_Y_M - H_Y_X
integ     = H_Y_M - H_Y_O              # I(Y;O|M)
aperture  = H_Y_O - H_Y_X              # I(Y;X|O)
print(f"\n  Gamma_rep = I(Y;X|M)          = {gamma_rep:.5f}")
print(f"    integration loss I(Y;O|M)   = {integ:.5f}   (recoverable: more memory)")
print(f"    aperture loss    I(Y;X|O)   = {aperture:.5f}   (irrecoverable by any observer of O)")
print(f"    sum                          = {integ+aperture:.5f}"
      f"   |residual| = {abs(gamma_rep-(integ+aperture)):.2e}")
