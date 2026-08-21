# The Balance-Attractor Dynamics

**Status:** derived formal model, 2026-08-20, v1.1. This note answers what additional dynamics would make \(b\equiv\text{◐}=1/2\) a stable attractor rather than only the unique algebraically perfect point. It formalizes Ashman's proposal: stable systems should balance input and output, convergence and emergence. The mathematical implications are proved and computationally verified. The choice of which law, if any, nature instantiates remains open and requires measurement. Framework integration awaits Ashman's countersign.

## 0. Answer in one statement

Complement symmetry makes \(1/2\) a fixed point. Bounded persistence plus negative feedback makes it an attractor.

Let

\[
I(t)>0
\]

be convergence or input throughput, and let

\[
O(t)>0
\]

be emergence or output throughput. Define

\[
b
=
\frac{I}{I+O},
\qquad
2b-1
=
\frac{I-O}{I+O}.
\]

The missing constitutive principle is:

> Excess convergence must increase emergence or suppress convergence; excess emergence must increase convergence or suppress emergence.

At the balance-coordinate level, the condition is

\[
\left(b-\frac12\right)\dot b<0
\qquad
\text{for }b\ne\frac12.
\]

At the stored-state level, with target \(X^*\), it is

\[
(X-X^*)(I-O)<0
\qquad
\text{for }X\ne X^*.
\]

Either inequality supplies a strict Lyapunov decrease and turns balance into an attractor.

## 1. Why Algebra Alone Is Insufficient

The complement transformation is

\[
b\mapsto1-b.
\]

If a balance dynamics

\[
\dot b=f(b)
\]

respects that complement, then

\[
f(1-b)=-f(b).
\]

This forces

\[
f(1/2)=0.
\]

It does not determine stability. All three examples respect the fixed point:

\[
\dot b=-\lambda(b-1/2)
\qquad
\text{stable},
\]

\[
\dot b=0
\qquad
\text{neutral},
\]

\[
\dot b=+\lambda(b-1/2)
\qquad
\text{unstable}.
\]

Therefore the balance-rigidity theorem supplies the distinguished state and several exact defect measures. A dissipative feedback principle is still required to select the direction of motion.

## 2. Bounded-Persistence Balance Theorem

Let \(X(t)\) be the stored amount of the conserved quantity inside a chosen system boundary. Conservation gives

\[
\dot X=I-O.
\]

Define cumulative throughput

\[
Q(T)
=
\int_0^T[I(t)+O(t)]\,dt.
\]

**Theorem 1, bounded-persistence balance.** Suppose \(X(t)\) remains bounded and \(Q(T)\to\infty\). Then the throughput-weighted long-run balance is

\[
\lim_{T\to\infty}
\frac{\int_0^T[I(t)+O(t)]b(t)\,dt}
{Q(T)}
=
\frac12.
\]

Equivalently,

\[
\lim_{T\to\infty}
\frac{\int_0^T[I(t)-O(t)]\,dt}
{Q(T)}
=
0.
\]

**Proof.** Since

\[
I-O=(I+O)(2b-1),
\]

integration of the storage equation gives

\[
\int_0^T(I-O)\,dt=X(T)-X(0).
\]

Boundedness of \(X\) and divergence of \(Q(T)\) imply

\[
\frac{X(T)-X(0)}{Q(T)}\to0.
\]

Substitution and rearrangement give the result. QED.

**Corollary 1.1, steady state.** At any time-independent stable state,

\[
I^*=O^*,
\qquad
b^*=\frac12.
\]

**Corollary 1.2, stable periodic operation.** If \(X(t)\) returns to its starting value after a period \(P\), then

\[
\int_0^P I(t)\,dt
=
\int_0^P O(t)\,dt.
\]

The system can be instantaneously off balance throughout the cycle while being exactly balanced over the complete cycle.

**Precision.** Bounded stability forces average flow balance, not instantaneous equality. Instantaneous attraction requires a feedback law.

## 3. General Attractor Criterion

Let

\[
\delta=b-\frac12
\]

and define

\[
W(b)=\delta^2.
\]

**Theorem 2, one-dimensional balance criterion.** Let \(f\) be continuous. If

\[
\dot b=f(b),
\qquad
f(1/2)=0,
\]

and

\[
\delta f(b)<0
\qquad
\text{for every }b\ne1/2,
\]

then \(b=1/2\) is globally asymptotically stable on every invariant subinterval of \((0,1)\).

**Proof.**

\[
\dot W
=
2\delta\dot b
=
2\delta f(b)
<
0
\]

away from balance. Thus \(W\) decreases strictly and is bounded below by zero. In one dimension, \(b(t)\) moves monotonically toward \(1/2\). If its limit were not \(1/2\), continuity would leave \(f\) bounded away from zero near that limit, contradicting convergence. QED.

The local version is

\[
f(1/2)=0,
\qquad
f'(1/2)<0.
\]

This theorem says exactly what a proposed physical dynamics must demonstrate.

## 4. Minimal Conservative Exchange Dynamics

The simplest symmetric law transfers capacity from the excessive channel to the deficient one:

\[
\dot I=-\kappa(I-O),
\]

\[
\dot O=+\kappa(I-O),
\qquad
\kappa>0.
\]

**Theorem 3.** This law conserves total throughput

\[
T=I+O
\]

and makes \(b=1/2\) globally exponentially stable:

\[
b(t)-\frac12
=
\left(b(0)-\frac12\right)e^{-2\kappa t}.
\]

**Proof.** The total derivative is zero. The mismatch \(D=I-O\) obeys

\[
\dot D=-2\kappa D.
\]

Since

\[
b-\frac12=\frac{D}{2T},
\]

the result follows. QED.

This is the minimal direct answer to the user's question. Excess input is converted into increased output capacity, and excess output is converted into increased input capacity.

## 5. Storage-Mediated Homeostasis

Direct exchange between input and output rates is an abstraction. A more physical mechanism uses the stored interior state:

\[
\dot X=I-O.
\]

Let \(X^*\) be the stable storage level and assume

\[
I-O=-k(X-X^*),
\qquad
k>0.
\]

**Theorem 4.** The storage error and flow mismatch decay exponentially:

\[
X(t)-X^*
=
[X(0)-X^*]e^{-kt},
\]

\[
I(t)-O(t)
=
-k[X(0)-X^*]e^{-kt}.
\]

If \(I+O\) stays bounded away from zero, then

\[
b(t)\to\frac12.
\]

**Proof.** Substitute the feedback law into \(\dot X=I-O\). The result is the scalar stable equation

\[
\frac{d}{dt}(X-X^*)=-k(X-X^*).
\]

The balance conclusion follows from

\[
2b-1=\frac{I-O}{I+O}.
\]

QED.

The physical mechanism is ordinary homeostasis:

1. Excess input raises storage.
2. Raised storage increases output or suppresses input.
3. Excess output lowers storage.
4. Lowered storage increases input or suppresses output.

## 6. Boundary-Preserving Relative-Growth Dynamics

If a channel with exactly zero activity cannot be recreated spontaneously, the boundaries \(b=0\) and \(b=1\) should remain invariant. Let the relative per-capita response obey

\[
r_I-r_O=-\gamma(2b-1),
\qquad
\gamma>0.
\]

The ratio identity

\[
\dot b=b(1-b)(r_I-r_O)
\]

then gives

\[
\dot b
=
\gamma b(1-b)(1-2b).
\]

**Theorem 5.** Every initial state \(b(0)\in(0,1)\) converges to \(1/2\). The endpoints are invariant and repelling from the interior.

**Proof.** For \(0<b<1/2\), every factor on the right is positive. For \(1/2<b<1\), the right side is negative. Theorem 2 applies. QED.

An exact solution can be written for

\[
y(t)=\left(b(t)-\frac12\right)^2.
\]

It obeys

\[
\dot y=-\gamma y(1-4y),
\]

so

\[
y(t)
=
\frac{y_0e^{-\gamma t}}
{1-4y_0+4y_0e^{-\gamma t}}.
\]

This is negative frequency-dependent feedback: whichever channel dominates receives a relative disadvantage.

## 7. Dynamics Generated by the Rigidity Defect

The odd-cycle theorem gives the exact gap defect

\[
V_{\rm gap}(m,b)
=
\frac{m(m+1)}{(2m+1)^2}(2b-1)^2.
\]

Let \(M(b)>0\) be a mobility and impose gradient descent:

\[
\dot b
=
-M(b)\frac{dV_{\rm gap}}{db}.
\]

**Theorem 6.** Balance is globally asymptotically stable in the interior, and

\[
\frac{dV_{\rm gap}}{dt}
=
-M(b)
\left(\frac{dV_{\rm gap}}{db}\right)^2
\le0.
\]

Equality holds in the interior only at \(b=1/2\).

**Proof.** The chain rule gives

\[
\frac{dV_{\rm gap}}{dt}
=
\frac{dV_{\rm gap}}{db}\dot b
=
-M(b)
\left(\frac{dV_{\rm gap}}{db}\right)^2.
\]

The derivative of \(V_{\rm gap}\) has its unique interior zero at \(b=1/2\), so the Lyapunov argument of Theorem 2 applies. QED.

For constant mobility \(M(b)=\eta\),

\[
b(t)-\frac12
=
\left(b(0)-\frac12\right)
\exp\left[
-\frac{8\eta m(m+1)}{(2m+1)^2}t
\right].
\]

For \(m=3\), the decay rate is

\[
\frac{96\eta}{49}.
\]

Choosing

\[
M(b)\propto b(1-b)
\]

recovers the boundary-preserving dynamics of Section 6 up to time scaling.

This law is mathematically natural because it dissipates the exact nonuniformity derived by the rigidity theorem. It becomes a physical claim only if a real system can be shown to respond to that defect.

## 8. Local Balance Does Not Erase Seam Error

Let octave \(n\) have

\[
\delta_n=b_n-\frac12
\]

and cumulative seam displacement

\[
\Delta_n
=
\Delta_0+\sum_{j=0}^{n-1}\delta_j.
\]

Suppose local balance contracts by

\[
\delta_{n+1}=\rho\delta_n,
\qquad
|\rho|<1.
\]

Then

\[
\delta_n\to0,
\]

but

\[
\Delta_\infty
=
\Delta_0+\frac{\delta_0}{1-\rho}.
\]

The residual is generally nonzero.

**Conclusion.** A dynamics that attracts \(b\) to \(1/2\) stops future drift but does not necessarily repair accumulated global displacement.

## 9. Seam-Restoring Feedback

To restore both local balance and global alignment, the dynamics must respond to accumulated error. In continuous form:

\[
\dot\Delta=\delta,
\]

\[
\dot\delta=-k_p\delta-k_i\Delta,
\qquad
k_p>0,
\quad
k_i>0.
\]

**Theorem 7.** The equilibrium

\[
(\delta,\Delta)=(0,0)
\]

is globally asymptotically stable.

**Proof.** Define

\[
\mathcal L
=
\frac12\delta^2
+
\frac{k_i}{2}\Delta^2.
\]

Then

\[
\dot{\mathcal L}
=
\delta(-k_p\delta-k_i\Delta)
+
k_i\Delta\delta
=
-k_p\delta^2
\le0.
\]

The only invariant subset of \(\delta=0\) also requires

\[
\dot\delta=-k_i\Delta=0,
\]

so \(\Delta=0\). QED.

Equivalently,

\[
\ddot\Delta+k_p\dot\Delta+k_i\Delta=0.
\]

The regimes are:

\[
k_p^2>4k_i
\qquad
\text{overdamped},
\]

\[
k_p^2=4k_i
\qquad
\text{critically damped},
\]

\[
k_p^2<4k_i
\qquad
\text{damped oscillation}.
\]

Critical damping gives the fastest return without overshoot in this linear model.

### Discrete octave controller

A direct per-octave version is

\[
\begin{pmatrix}
\Delta_{n+1}\\
\delta_{n+1}
\end{pmatrix}
=
\begin{pmatrix}
1&1\\
-k_i&1-k_p
\end{pmatrix}
\begin{pmatrix}
\Delta_n\\
\delta_n
\end{pmatrix}.
\]

**Theorem 8.** Both eigenvalues lie strictly inside the unit circle exactly when

\[
k_i>0,
\]

\[
k_p>k_i,
\]

and

\[
2k_p-k_i<4.
\]

**Proof.** The characteristic polynomial is

\[
z^2-(2-k_p)z+(1-k_p+k_i).
\]

Applying the quadratic Jury conditions gives the three displayed inequalities. QED.

The integral term \(k_i\Delta\) is the exact addition required to eliminate the residual left by local relaxation alone.

## 10. Delay, Gain, and Oscillation

Negative feedback can fail if it acts too late. The simplest delayed linear model is

\[
\dot\delta(t)=-\lambda\delta(t-\tau).
\]

Its first stability boundary occurs at

\[
\lambda\tau=\frac\pi2.
\]

Below this boundary the restoring feedback is stable. At the boundary a conjugate pair reaches the imaginary axis; beyond it the feedback produces growing oscillation.

This gives a concrete interpretation of unstable overcorrection: balance requires not only the correct sign of feedback, but sufficient response speed relative to gain.

## 11. Noisy Stable Balance

A measured balance parameter will fluctuate. The local stochastic model is

\[
d\delta
=
-\lambda\delta\,dt
+
\sqrt{2D}\,dW_t.
\]

Away from boundary effects, its stationary signatures are

\[
\mathbb E[\delta]=0,
\]

\[
\operatorname{Var}(\delta)=\frac D\lambda,
\]

\[
\operatorname{Corr}[\delta(t),\delta(t+s)]
=
e^{-\lambda|s|}.
\]

Thus a stable attractor does not predict that every observation equals \(1/2\). It predicts a restoring conditional drift toward \(1/2\), with fluctuations whose width is set by noise divided by restoration strength.

## 12. Empirical Test

Measure input and output independently and define

\[
b(t)=\frac{I(t)}{I(t)+O(t)}.
\]

Estimate the conditional drift

\[
A(b)
=
\lim_{\Delta t\to0}
\frac{\mathbb E[b(t+\Delta t)-b(t)\mid b(t)=b]}
{\Delta t}.
\]

The stable-balance prediction is

\[
A(1/2)=0,
\]

\[
A(b)>0
\quad
\text{for }b<1/2,
\]

\[
A(b)<0
\quad
\text{for }b>1/2.
\]

Near balance,

\[
A(b)\approx-\lambda(b-1/2),
\qquad
\lambda>0.
\]

The stronger bounded-persistence prediction is that the throughput-weighted long-run mean of \(b\) approaches \(1/2\).

### Disconfirming outcomes

1. Conditional drift consistently points away from \(1/2\).
2. Stable bounded regimes possess a reproducible biased mean after all relevant sources, sinks, and storage terms are included.
3. Apparent balance occurs without any restoring response to perturbation.
4. A different value predicts recovery and bounded persistence better than \(1/2\).

## 13. Accounting Boundary Protection

The conservation statement is only as good as the accounting boundary. If the stored quantity obeys

\[
\dot X=I-O+G-L,
\]

with internal generation \(G\) and loss \(L\), then stable operation requires

\[
\langle I+G\rangle
=
\langle O+L\rangle,
\]

not necessarily \(\langle I\rangle=\langle O\rangle\).

Likewise, a growing system can remain dynamically organized while \(X\) increases, so it need not be flow-balanced during growth. The half-balance theorem applies to bounded persistence, steady operation, or a complete periodic cycle after all relevant channels have been counted.

This protection prevents the framework from declaring every unequal pair of superficially chosen flows pathological.

## 14. Result

The strongest justified framework principle is:

> A bounded persistent whole must balance total convergence and emergence over its complete cycle. It becomes dynamically stable when accumulated excess in either direction changes the next flow in the opposite direction.

The first sentence follows from conservation and boundedness. The second is the negative-feedback law that makes \(\text{◐}=1/2\) an attractor. Integral feedback is required if the system must also erase accumulated seam displacement.

## 15. Verification Record

Companion script: experiments/balance_attractor_dynamics_v1.py.

Verified:

1. Conservative input-output exchange matches its exact exponential solution.
2. Boundary-preserving homeostasis matches its exact nonlinear solution for six initial balances.
3. Exact gap variance decreases monotonically under its gradient flow.
4. Local balance convergence leaves the predicted nonzero seam residual.
5. Continuous seam-restoring feedback decreases its Lyapunov function to numerical zero.
6. The discrete Jury conditions agree with spectral-radius calculations across 7,900 parameter pairs.
7. A periodic bounded-storage example returns to exactly throughput-weighted \(b=1/2\).

## Revision History

- 2026-08-20 v1.1: completed the continuity argument and the defect-gradient Lyapunov proof.
- 2026-08-20 v1.0: bounded-persistence theorem, general attractor criterion, conservative exchange, storage homeostasis, boundary-preserving flow, defect-gradient dynamics, seam-restoring control, delay and noise predictions, and verification record.
