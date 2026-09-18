# Circumpunct Flow Model v0.1 (incoming document, filed as received)

**Provenance.** Developed by Ashman outside this repository (working revision 5, 17 September 2026) and brought into the corpus on 2026-09-18. Filed **verbatim**; nothing below this banner has been edited, and no claim in it has been promoted into `CLAUDE.md` or `circumpunct_framework.md`.

**Status: incoming source material, pending Ashman's adjudication.** Corpus-side review: `plans/recursive_present_review_2026_09_18.md`. Companion document: `plans/the_recursive_present_2026_09_18.md`.

**Notation warning.** This document uses two symbols in senses that collide with corpus usage, and a reader who does not know that will mis-cite it:

- `Φ` here is the normalized `ℓ²` potential vector, not the 3D field station. Under the §4.8a limit case (`Φ∞ = E`) the intended object is `E`, so read `Φ∞` wherever this document writes `Φ`.
- `κ` here is a coupling *profile* (a vector in `ℓ²`). The corpus already carries two other `κ`s: the cross-station nesting matrix `κ_{p,q}` with `κ_{0,0} = α` (§27.7q), and the two-coordinate bond `κ(f) = (c, a)` from the 2026-08-01 wholeness-plane correction. Three distinct objects now share the letter. See Finding 10 of the review.

**Self-assessed scope, quoted from §11 of the document itself:** "At present, no additional observable law follows from the stated metaphysical premises." The model is observationally equivalent to standard temporal coupled-mode theory for the quantities it treats. This is the document's own finding, stated in its own voice, and the review does not soften it.

---

# Circumpunct flow model: coupling through a point

Working revision 5, 17 September 2026  
Developed from Ashman Roonz's Circumpunct Framework

This revision derives the proposed phase term conditionally from a weak, local optical interaction and constrains its coefficient, state dependence, and observable effects. The derivation identifies a conventional nonlinear mechanism and a test protocol. It does not establish the term as a unique consequence of the metaphysical premises or assign it an experimentally measured magnitude.

The user's current definitions govern the interpretation:

- Energy means infinite, unactualized potential.
- Power means finite physical expression.
- The future has no events. Events arise in the present and leave a past.
- Actualization occurs through convergence into a singular point and emergence from it.
- Finite actualization begins with localization at a point.

These are premises of the proposed framework. The mathematics below supplies one candidate representation and conditional predictions. It does not establish those premises as facts about nature.

## 1. The point and its coupling

Choose a distinguished point \(p\), denoted \(\bullet_p\), as the locus of interaction. The point has no spatial extension.

A point also needs a coupling rule if it is to produce a determinate response. We represent the local interface by a profile \(\kappa_p\). Its coefficients describe how potential is coupled at the point; they are not spatial pieces of the point.

In this construction, "singular point" means a distinguished zero-dimensional locus. The coupling does not require a divergent numerical value. If "singularity" is intended to mean a mathematical divergence, that would be an additional condition.

The two-stage architecture is

\[
\boxed{
\Phi
\xrightarrow{\ \mathcal C_p\ }
c_p
\xrightarrow{\ \mathcal M_p\ }
\{P_{p,j}\}.
}
\tag{1}
\]

The first stage produces a localized amplitude. The second produces finite output powers. These are proposed mathematical operators whose interpretation is convergence and emergence.

## 2. One representation of infinite potential

Represent potential by a complex sequence

\[
\Phi=(\phi_0,\phi_1,\ldots)\in\ell^2,
\qquad
\sum_{n=0}^{\infty}|\phi_n|^2=1.
\tag{2}
\]

This is one normalized state in an infinite-dimensional space. It can have infinitely many nonzero coordinates.

The coordinates label potential modes. They do not label events waiting in the future, or packets of physical energy. Indexing \(\Phi(t)\) below means representing potential at the current interaction.

The normalization is dimensionless. It is a possible mathematical expression of "one by inclusion." It does not equate a physical energy measured in joules with the number one. Infinite dimensionality and infinite physical energy are different properties; equation (2) represents only the former.

## 3. A concrete convergence law

Choose a coupling profile satisfying

\[
\kappa_p=(\kappa_{p,0},\kappa_{p,1},\ldots),
\qquad
\sum_{n=0}^{\infty}|\kappa_{p,n}|^2\leq1.
\tag{3}
\]

Define convergence at the point by

\[
\boxed{
c_p(t)=\mathcal C_p[\Phi(t)]
=\langle\kappa_p,\Phi(t)\rangle
=\sum_{n=0}^{\infty}
\overline{\kappa_{p,n}}\,\phi_n(t).
}
\tag{4}
\]

The bar denotes complex conjugation. This is a weighted combination of potential modes into one local complex amplitude.

The Cauchy–Schwarz inequality gives

\[
\sum_n|\overline{\kappa_{p,n}}\phi_n|
\leq
\left(\sum_n|\kappa_{p,n}|^2\right)^{1/2}
\left(\sum_n|\phi_n|^2\right)^{1/2}
\leq1.
\tag{5}
\]

Thus the series converges absolutely, and

\[
\boxed{|c_p(t)|\leq1.}
\tag{6}
\]

This is the first explicit finite result. Infinitely many mode contributions can produce a bounded value at one locus.

The bound follows from the normalization and the chosen coupling constraint. It is not a property supplied by a bare point alone.

## 4. A concrete emergence law

Introduce a finite physical power scale \(P_{*,p}>0\), measured in watts. For immediate response, define

\[
\boxed{
P_p(t)=\mathcal M_p[c_p(t)]
=P_{*,p}|c_p(t)|^2.
}
\tag{7}
\]

A square-amplitude response is a modeling choice. Such relationships are familiar in wave physics, where intensity depends on amplitude squared, but that analogy is not evidence that metaphysical potential is a physical wave. [OpenStax, Sound Intensity](https://openstax.org/books/university-physics-volume-1/pages/17-3-sound-intensity)

Combining the two operations gives

\[
\boxed{
P_p(t)=P_{*,p}
\left|
\sum_{n=0}^{\infty}
\overline{\kappa_{p,n}}\phi_n(t)
\right|^2.
}
\tag{8}
\]

By equation (6),

\[
\boxed{0\leq P_p(t)\leq P_{*,p}<\infty.}
\tag{9}
\]

For finitely many output channels \(j=1,\ldots,m\), choose weights

\[
w_{p,j}\geq0,\qquad \sum_{j=1}^m w_{p,j}=1,
\]

and set

\[
\boxed{
P_{p,j}(t)=w_{p,j}P_p(t).
}
\tag{10}
\]

The output may be distributed across many physical effects while its total stays finite.

Here \(P_{*,p}\) is an explicit physical postulate. Dimensionless potential coordinates and a zero-dimensional point do not determine a value in watts. Deriving or measuring this scale is a remaining task.

## 5. An exactly solvable example

Choose

\[
\phi_n=\frac{\sqrt3}{2^{n+1}},
\qquad
\kappa_{p,n}(\theta)=\phi_n e^{in\theta},
\qquad n=0,1,2,\ldots.
\tag{11}
\]

Both sequences have norm one because

\[
\sum_{n=0}^{\infty}|\phi_n|^2
=\frac34\sum_{n=0}^{\infty}\frac1{4^n}
=1.
\]

The parameter \(\theta\) changes the relative phase profile of the coupling. It has no assigned psychological, quantum, or cosmological meaning.

The converged amplitude can be summed exactly:

\[
\begin{aligned}
c_p(\theta)
&=\frac34\sum_{n=0}^{\infty}
\left(\frac{e^{-i\theta}}4\right)^n\\
&=\frac3{4-e^{-i\theta}}.
\end{aligned}
\tag{12}
\]

Therefore the immediate-response power is

\[
\boxed{
P_p(\theta)
=P_{*,p}\frac9{17-8\cos\theta}.
}
\tag{13}
\]

The same formula gives the steady output of the response-time extension below.

For an illustrative \(P_{*,p}=10\) W:

| Coupling phase \(\theta\) | \(P_p/P_{*,p}\) | Output power |
| --- | --- | --- |
| \(0\) | \(1\) | \(10\) W |
| \(\pi/2\) | \(9/17\) | \(5.29412\) W |
| \(\pi\) | \(9/25\) | \(3.6\) W |

Infinitely many nonzero contributions are present in every row. Their coupling changes the finite resulting power.

The lower limit \(0.36P_{*,p}\) belongs to this particular example. General normalized profiles can be orthogonal and yield zero overlap and zero output.

The geometric coefficient choice is illustrative. It is not a derived universal pattern.

## 6. Adding a response time

An optional local response law introduces an amplitude \(z_p(t)\) associated with the interface at the point:

\[
\boxed{
\tau_p\frac{dz_p}{dt}+z_p=c_p(t),
\qquad
\tau_p>0,\quad |z_p(0)|\leq1.
}
\tag{14}
\]

The point remains a location. The response state describes the interaction associated with it; any physical storage or memory would require an implementation in the local system.

The solution is

\[
z_p(t)=e^{-t/\tau_p}z_p(0)
+\frac1{\tau_p}\int_0^t
e^{-(t-s)/\tau_p}c_p(s)\,ds.
\tag{15}
\]

Since \(|c_p|\leq1\),

\[
|z_p(t)|
\leq e^{-t/\tau_p}|z_p(0)|+
1-e^{-t/\tau_p}
\leq1.
\tag{16}
\]

Replace \(c_p\) by \(z_p\) in the emergence law:

\[
\boxed{
P_{p,j}(t)=P_{*,p}w_{p,j}|z_p(t)|^2,
\qquad
\sum_jP_{p,j}(t)\leq P_{*,p}.
}
\tag{17}
\]

For a constant aligned drive \(c_p=1\), starting from \(z_p(0)=0\),

\[
\boxed{
P_p(t)=P_{*,p}(1-e^{-t/\tau_p})^2.
}
\tag{18}
\]

At one response time the output is approximately \(0.39958P_{*,p}\); at three response times it is approximately \(0.90290P_{*,p}\).

If the drive becomes zero at \(T\),

\[
P_p(t)=P_p(T)e^{-2(t-T)/\tau_p},\qquad t>T.
\tag{19}
\]

This makes a distinct prediction: the amplitude decays on time scale \(\tau_p\), while the power decays on time scale \(\tau_p/2\).

This amplitude-response model differs from the earlier reservoir model, in which power itself followed a first-order exponential. Measurements could distinguish the response shapes. The present law is a chosen extension, not a consequence of the point's geometry.

## 7. Emergence into extended effects

A simple extension distributes the designated emitted power isotropically into a physical space. For distance \(r>0\) from \(p\), transport speed \(v>0\), and no intervening absorption,

\[
\boxed{
I_{\rm out}(r,t)
=\frac{P_p(t-r/v)}{4\pi r^2}.
}
\tag{20}
\]

The power crossing a sphere of radius \(r\) is

\[
4\pi r^2 I_{\rm out}(r,t)=P_p(t-r/v).
\]

Prescribe the output history before the initial time, or set it to zero when there was no earlier emission. The delay ensures that an actual output takes time to reach a more distant location.

Equation (20) assumes a spatial geometry and propagation law. It describes effects extending from a point within space; it does not derive space from the point.

Flux density may diverge as \(r\to0\) in the ideal point representation while every surrounding sphere carries finite total power. A physical description near a source would generally need its detailed interface. No value of \(0\times\infty\) is used.

## 8. Events arise in the present and leave a past

The potential modes carry no future-event timestamps. An actualization episode produces concrete transfers.

Over the current interval \([t_n,t_{n+1}]\), define

\[
\Delta W_{p,j,n}
=\int_{t_n}^{t_{n+1}}P_{p,j}(s)\,ds.
\tag{21}
\]

Because the total power is bounded,

\[
\sum_j\Delta W_{p,j,n}
\leq P_{*,p}(t_{n+1}-t_n)<\infty.
\tag{22}
\]

The event produced over that interval is

\[
e_n=
\left(t_{n+1},
\Delta W_{p,1,n},\ldots,\Delta W_{p,m,n}\right).
\]

The past record grows by appending this actual event:

\[
\boxed{H_{n+1}=H_n\Vert e_n.}
\tag{23}
\]

Here \(\Vert\) means append.

| Framework term | Proposed mathematical role |
| --- | --- |
| Future | Unactualized potential represented by \(\Phi\), without a stock of timestamped events |
| Present | Convergence and emergence through the coupling at \(p\) |
| Past | Actual transfers already produced and recorded in \(H\) |

The variable \(t\) is already present in these equations. This construction models event production in time; it does not derive the existence or direction of time. Forecasts computed from the equations remain present descriptions rather than events assigned an already-actual existence.

The record is ideal bookkeeping. A physical recorder would need finite storage, an encoding, and its own physical accounting.

## 9. Supply supporting the output

We can complete the physical account by specifying a source, storage, and all outgoing channels. Conservation relates changes of stored physical energy to incoming and outgoing transfers. [Feynman Lectures, Field Energy and Field Momentum](https://www.feynmanlectures.caltech.edu/II_27.html)

The following is one proposed passive interface, chosen to preserve the amplitude response in section 6. Its return channel and storage law are additional modeling assumptions, not consequences of a point alone. We suppress the point index \(p\) in this section.

### 9.1 Supply availability and actual drive

Introduce a real supply availability amplitude \(q(t)\), with \(0\leq q\leq1\), and define

\[
\boxed{
u(t)=q(t)c(t),
\qquad
\tau\dot z+z=u(t).
}
\tag{24}
\]

The power capacity made available to this coupling is \(P_*q^2\). The actual incoming power is \(P_*q^2|c|^2\). Available capacity need not all be drawn from the source.

Full availability, \(q=1\), recovers equation (14). Setting \(q=0\) disconnects the incoming supply even if the potential representation and its overlap \(c\) remain unchanged. Because \(|u|\leq1\), the earlier bound \(|z|\leq1\) still holds for the same initial condition.

Choose the physical quantities

\[
\boxed{
\begin{aligned}
P_{\rm in}&=P_*|u|^2,\\
P_{\rm out}&=P_*|z|^2,\\
P_{\rm back}&=P_*|u-z|^2,\\
U&=P_*\tau|z|^2.
\end{aligned}
}
\tag{25}
\]

All three powers are nonnegative and measured in watts. \(U\) is stored physical energy in joules, distinct from the user's metaphysical Energy. It represents storage in the local system associated with the point, not a claim that a bare geometric point contains a finite physical volume.

\(P_{\rm out}\) is the designated output \(P_p\) used in earlier sections. \(P_{\rm back}\) is a separate return toward the source. The weights \(w_{p,j}\) distribute only the designated output. A complete record of every physical transfer would also include the return.

### 9.2 Deriving the balance

Differentiate the storage rule and use equation (24):

\[
\begin{aligned}
\dot U
&=2P_*\tau\operatorname{Re}(\bar z\dot z)\\
&=2P_*\bigl(\operatorname{Re}(\bar z u)-|z|^2\bigr)\\
&=P_*\bigl(|u|^2-|u-z|^2-|z|^2\bigr).
\end{aligned}
\tag{26}
\]

Consequently,

\[
\boxed{
P_{\rm in}=\dot U+P_{\rm out}+P_{\rm back}.
}
\tag{27}
\]

This identity holds for time-varying complex inputs as well as constant inputs. It explicitly accounts for the source supplying storage and output. There is no internal dissipative channel in this chosen model; any physical loss would need its own term and a consistent response law.

For constant \(u\), the steady state is \(z=u\), so

\[
P_{\rm out}=P_{\rm in}=P_*q^2|c|^2,
\qquad P_{\rm back}=0,
\qquad \dot U=0.
\tag{28}
\]

If the supply is disconnected at \(T\), then \(u=0\) and

\[
U(t)=U(T)e^{-2(t-T)/\tau},
\qquad
P_{\rm out}(t)=P_{\rm back}(t)=U(t)/\tau.
\tag{29}
\]

Half of the remaining storage eventually exits through each channel. Counting only \(P_{\rm out}\) as all outgoing power would miss the other half in this particular completion of the model.

### 9.3 Accounting for the source itself

Let \(R(t)\geq0\) be the upstream source's remaining physical energy, in joules. Let \(P_{\rm refill}\geq0\) describe replenishment from outside the chosen system. Assuming perfect recovery of returned power and negligible propagation delay,

\[
\dot R=P_{\rm refill}-P_{\rm in}+P_{\rm back}.
\tag{30}
\]

With accumulated designated output

\[
W(t)=\int_0^tP_{\rm out}(s)\,ds,
\]

equations (27) and (30) give

\[
\boxed{
R(t)+U(t)+W(t)
=R(0)+U(0)+\int_0^tP_{\rm refill}(s)\,ds.
}
\tag{31}
\]

Returned power is counted once: it leaves the interface and replenishes the source. If it is dissipated elsewhere instead, that destination needs a separate account.

To make supply availability respond to depletion, one possible explicit law is

\[
\boxed{
q(R)=\frac{R}{R+R_c},\qquad R_c>0.
}
\tag{32}
\]

Here \(R_c\), in joules, sets the scale over which supply availability falls. This is an illustrative constitutive law, not a universal relation. Along with equations (24), (25), and (30), it defines the source and interface dynamics once \(c(t)\) and replenishment are specified. At \(R=0\), \(q=0\) and \(\dot R=P_{\rm refill}+P_{\rm back}\geq0\), so the source cannot be driven below zero by this law.

With no replenishment,

\[
0\leq W(t)\leq R(0)+U(0).
\tag{33}
\]

A finite initial supply can therefore support only a finite accumulated output. Sustaining a positive constant output indefinitely requires an unbounded cumulative supply. Infinite metaphysical potential does not, by normalization alone, specify that physical supply or its transfer rate.

### 9.4 An exactly calculable supply pulse

Choose \(P_*=10\) W, \(\tau=1\) s, \(z(0)=0\), and an initially charged source with \(R(0)=100\) J. For this example, prescribe full availability \(q=1\) for four seconds and then disconnect it; use \(c=1\). This pulse replaces the depletion law (32), and the source budget stays positive throughout.

During the pulse,

\[
P_{\rm in}=10,\qquad
P_{\rm out}=10(1-e^{-t/\tau})^2,\qquad
P_{\rm back}=10e^{-2t/\tau},
\]

with powers in watts. At switch-off, the interface holds approximately \(9.63704\) J. It subsequently releases half through each outgoing channel.

For a pulse of duration \(T\), including all subsequent decay,

\[
\begin{aligned}
W_{\rm out}(\infty)&=P_*\bigl[T-\tau(1-e^{-T/\tau})\bigr],\\
W_{\rm back}(\infty)&=P_*\tau(1-e^{-T/\tau}).
\end{aligned}
\tag{34}
\]

| Transfer, integrated over the pulse and subsequent decay | Joules |
| --- | ---: |
| Gross incoming supply | 40.00000 |
| Designated output | 30.18316 |
| Return to source | 9.81684 |

The two outgoing transfers add to the gross incoming supply. With perfect return recovery and no replenishment, the source ends with approximately \(69.81684\) J, the interface storage tends to zero, and \(30.18316\) J has reached the designated output.

This accounts for the output of a specified physical supply. Identifying an actual source, or establishing metaphysical potential as its ultimate origin, remains a separate question. The new equations describe the proposed transfer mechanism and its limits.

## 10. A physical system matching the interface equations

### 10.1 A driven optical cavity

A concrete realization is a resonator driven through one of two ports, such as light confined between two partially transmitting mirrors. Temporal coupled-mode theory describes an isolated optical resonance using a driven amplitude and outgoing waves. [Fan, Suh, and Joannopoulos, 2003](https://opg.optica.org/josaa/abstract.cfm?URI=josaa-20-3-569)

Use an amplitude \(a\) with \(|a|^2\) measured in joules and incoming amplitude \(s\) with \(|s|^2\) measured in watts. Write the more general interface as

\[
\begin{aligned}
\dot a&=(i\Delta-\Gamma/2)a+\sqrt{\gamma_1}\,s,\\
s_{\rm back}&=s-\sqrt{\gamma_1}\,a,\\
s_{\rm out}&=\sqrt{\gamma_2}\,a,\\
\Gamma&=\gamma_1+\gamma_2+\gamma_{\rm loss}.
\end{aligned}
\tag{35}
\]

Here \(\gamma_1,\gamma_2\) are energy leakage rates through the two ports, \(\gamma_{\rm loss}\) is an internal loss rate, and \(\Delta\) is drive detuning, all in inverse seconds. Port phase conventions can change amplitude signs without changing powers. The normalization and input-output structure are standard; the following substitution establishes the correspondence to our variables. [Kristensen et al., coupled-mode derivation](https://arxiv.org/html/1701.02929v1)

Set

\[
\boxed{
\gamma_1=\gamma_2=1/\tau,\quad
\gamma_{\rm loss}=0,\quad \Delta=0,\quad
a=\sqrt{P_*\tau}\,z,\quad s=\sqrt{P_*}\,qc.
}
\tag{36}
\]

Equation (35) then becomes exactly equation (24), while its incident, transmitted, reflected, and stored quantities become equation (25). This is algebraic equivalence between the two effective models. Applying either model to hardware assumes an isolated mode, linear response, negligible relevant propagation delay, and a slowly varying envelope. Equal coupling, resonant driving, and negligible internal loss are the additional restrictions for our original special case.

| Model quantity | Optical realization |
| --- | --- |
| \(z\) | Normalized field amplitude of the selected cavity mode |
| \(\tau\) | Field-amplitude decay time; twice the energy decay time |
| \(P_{\rm in}\) | Power entering in the selected input mode |
| \(P_{\rm out}\) | Transmitted power at the second port |
| \(P_{\rm back}\) | Reflected power in the first port |
| \(U\) | Energy stored in the cavity field |
| Point \(p\) | Effective location assigned to a spatially extended resonator |

The last row is a limit on the analogy: a single amplitude is not evidence of a literally zero-sized physical object. A real cavity has a spatial field and boundaries.

For a resonant step of mode-matched input power \(P_0\), starting empty, the symmetric ideal model predicts

\[
\frac{P_{\rm out}(t)}{P_0}=(1-e^{-t/\tau})^2,
\qquad
\frac{P_{\rm back}(t)}{P_0}=e^{-2t/\tau}.
\tag{37}
\]

After switch-off, the emitted power decays as \(e^{-2(t-T)/\tau}\). These are testable physical predictions, shared with the established cavity model. Internal loss or unequal mirrors require equation (35), rather than an unexplained failure of equation (37).

### 10.2 What the overlap can represent physically

In an optical realization, a normalized incident field profile can be expanded in an orthonormal mode basis. Its overlap with a normalized accepted mode plays the role of \(c=\langle\kappa,\Phi\rangle\). Here the coordinates describe a measurable field profile, not a measurement of metaphysical potential.

If an actual incident beam has total power \(P_{\rm beam}=P_*q^2\), the single-mode approximation gives

\[
P_{\rm in}=P_{\rm beam}|c|^2,
\qquad
P_{\rm unmatched}=P_{\rm beam}(1-|c|^2).
\tag{38}
\]

The unmatched portion must be included in the complete physical account. For nonresonant orthogonal modes treated as directly reflected, the reflected power summed over modes is \(P_{\rm back}+P_{\rm unmatched}\). The return in equation (25) refers only to the selected mode. A physical beam's total supplied power is therefore different from unused source capacity in section 9.1.

An infinite basis can represent a finite-power field. Observing the field does not establish metaphysical infinity. Likewise, reflected light does not automatically recharge a laser's power supply: the perfect recovery assumption in equation (30) requires an additional implementation. A detector or absorber receiving the return needs its own energy account instead.

### 10.3 Comparison with a published experiment

The same overlap structure also appears in temporal pulse capture. For an initially empty cavity on resonance, define the normalized incident waveform \(\varphi(t)=s(t)/\sqrt{W_{\rm in}}\) over times \(t\leq T\), and

\[
h_T(t)=\sqrt{\Gamma}\,e^{-\Gamma(T-t)/2}\,\mathbf 1_{t\leq T}.
\]

Both waveforms have unit squared integral. Integrating equation (35) gives

\[
\boxed{
\frac{U(T)}{W_{\rm in}}
=\frac{\gamma_1}{\Gamma}
\left|\langle h_T,\varphi\rangle\right|^2.
}
\tag{39}
\]

The integral concerns the input already delivered by time \(T\). It does not assign an actual existence to future events. This is our derivation from the cavity equation: geometry limits capture, while temporal overlap determines how closely a supplied pulse approaches that limit.

Bader and colleagues reported an asymmetric cavity with a geometric capture factor of approximately \(0.97\), temporal amplitude overlap \(0.986\), and spatial power overlap \(0.94\). Their measured maximum stored fraction was \(94^{+3}_{-5}\%\) of the spatially matched input, or \(88^{+3}_{-5}\%\) of the total input. [Bader et al., 2013, experiment and Table 1](https://arxiv.org/html/1309.6167v1)

Using those reported parameters in the overlap account gives

\[
0.97(0.986)^2=0.94303012,
\qquad
0.94\times0.94303012=0.88644831.
\]

Thus the calculated fractions are approximately 94.3% and 88.6%, within the reported measurement intervals. This is a consistency calculation using parameters from that experiment, not an independent fit to its raw data. The experiment has unequal mirror couplings; its 94% storage result belongs to the generalized model (35), not the symmetric specialization (36).

### 10.4 A direct validation protocol

1. Measure the input waveform and detector response independently. Characterize mirror asymmetry, internal loss, detuning, and spatial mode matching.
2. Estimate the energy decay time from a switch-off trace and convert it to the amplitude time \(\tau\). Reserve different pulse shapes and durations for prediction.
3. Predict both transmission and reflection for those held-out pulses using the measured input and fixed parameters. Include unmatched modes and known losses.
4. Compare residuals with measurement uncertainty and test ordinary explanations for systematic deviations, including additional modes and intensity-dependent responses.

Agreement would validate the applicable physical response model. It would not distinguish between metaphysical interpretations that assign the same equations and observations.

## 11. Does the metaphysical interpretation add a distinct prediction?

At present, no additional observable law follows from the stated metaphysical premises. The existing equations constrain responses, but attaching the meanings infinite potential, present convergence, and past record does not change their predicted signals.

There is a precise identification problem. Set \(\kappa=(1,0,\ldots)\), choose any unit vector \(\chi\) in the remaining modes, and define

\[
\Phi_c=\left(c,\sqrt{1-|c|^2}\,\chi\right),
\qquad |c|\leq1.
\tag{40}
\]

Then \(\|\Phi_c\|=1\) and \(\langle\kappa,\Phi_c\rangle=c\). Every allowed input amplitude has such a representation, with many possible unseen mode configurations. Consequently, measuring the output alone cannot establish that the underlying potential has infinitely many modes, much less that it is metaphysical. Independent rules for preparing or measuring the state and coupling are needed to make their particular structure testable.

The statement that the future contains no actual events likewise has no competing probability assignment or timing prediction in the present equations. A test of that statement would require a defined alternative observable consequence.

### 11.1 A possible additional hypothesis, explicitly not derived

One question suggested by the framework is whether the broader field configuration changes the response even when its projection onto the selected coupling is held fixed. The current model predicts that it does not, for the same supply, parameters, and initial state.

To illustrate what a distinguishable extension would require, take a physically specified basis of three input modes and

\[
\kappa=(1,0,0),\qquad
\Phi_+=\left(\frac1{\sqrt2},\frac12,\frac12\right),\qquad
\Phi_-=\left(\frac1{\sqrt2},\frac12,-\frac12\right).
\tag{41}
\]

Both profiles are normalized, have the same power in each mode, and give the same coupling \(c=1/\sqrt2\). They differ only in the relative phase of the last two modes. Define the independently controlled quantity

\[
X=2\operatorname{Re}(\bar\phi_1\phi_2),
\qquad X_+=\frac12,\quad X_-=-\frac12.
\tag{42}
\]

An illustrative extra postulate would be

\[
\boxed{\tau\dot z+(1+i\lambda X)z=qc,\qquad \lambda\in\mathbb R.}
\tag{43}
\]

This posits a phase response to the specified mode context. It is not implied by the current metaphysical axioms, and no nonzero value of \(\lambda\) has been established. Sections 12 and 13 supply a conditional physical derivation and bounds. Take \(X\) constant within each run. The extra term is purely imaginary and preserves equation (27) algebraically with the existing effective storage and power definitions.

At \(q=1\) and zero baseline detuning, the steady states predict

\[
\boxed{
\arg z_+-\arg z_-=-2\arctan(\lambda/2),
\qquad
P_{{\rm out},+}=P_{{\rm out},-}
=\frac{P_*}{2[1+(\lambda/2)^2]}.
}
\tag{44}
\]

The equal intensities make phase measurement essential for this particular comparison. The current model, \(\lambda=0\), predicts no phase difference. The proposed extension predicts a specified difference for a specified nonzero \(\lambda\).

Randomize the two input settings, verify their identical projection and supply, and measure the phase of only the selected output mode relative to a stable reference. Independently monitor detuning, temperature, unwanted mode mixing, detector effects, and known nonlinear couplings. Conventional optical nonlinearities can also shift resonance, so an unexplained shift is not sufficient to attribute an effect to metaphysical potential. [Kristensen et al., discussion of nonlinear and thermal responses](https://arxiv.org/html/1701.02929v1)

If the absolute phase contrast is bounded by \(\delta\), with its uncertainty and confidence level specified, this candidate law implies

\[
|\lambda|\leq2\tan(\delta/2)
\tag{45}
\]

for the relevant principal phase interval. A null result constrains this added law; it does not refute the original ontology, which never required a nonzero \(\lambda\). A reproducible nonzero result would first support an additional physical coupling after ordinary alternatives have been tested.

### 11.2 What would make it a prediction of the framework

The framework would need to justify a particular extra law from its premises, identify its measurable variables, and constrain its sign, size, or dependence on independently varied conditions. A chosen functional form can be tested on new data after its parameters are calibrated. Allowing an arbitrary function or silently adjusting parameters for every outcome would remove that predictive constraint.

The interface has an established physical counterpart, and the current metaphysical interpretation is observationally equivalent for the quantities modeled. The phase extension can be justified under the additional physical assumptions below. Establishing a distinct prediction of the metaphysical interpretation still requires a further result that those conventional assumptions do not already supply.

## 12. Conditional derivation of the phase law

### 12.1 The additional assumptions

The proposed term can follow from a weak, local, reactive interaction: the context changes the selected mode's resonance frequency while leaving its decay rates approximately unchanged. Assume that the response is smooth in weak context fields, insensitive to their common absolute phase, and evaluated with fixed material boundaries. The two context components are mutually coherent at the same carrier frequency; otherwise their cross term can oscillate or average away and requires a dynamical treatment. Their phase reference must be defined physically.

For an optical realization, take a weak probe, negligible absorption, weak material dispersion, and a high-quality isolated cavity mode. Retain the frequency-shifting interaction and neglect significant frequency conversion, pump depletion, and probe-induced changes of the context. These are physical assumptions in addition to the Circumpunct premises. Nonlinear coupled-mode treatments derive frequency shifts from material and field-overlap coefficients under such perturbative conditions. [Ramirez et al., nonlinear coupled-mode derivation, Sec. II](https://arxiv.org/pdf/1011.5845)

### 12.2 Why the leading dependence is quadratic

Let the physical amplitudes of the two context components be

\[
\mathbf b=\begin{pmatrix}b_1\\b_2\end{pmatrix}
=\sqrt S\begin{pmatrix}\phi_1\\\phi_2\end{pmatrix},
\qquad S\geq0.
\tag{46}
\]

Here \(S\) is a calibrated reference power in watts, and \(|b_j|^2\) is the power of component \(j\). With the normalization used in section 11, the two context components together carry \(S(|\phi_1|^2+|\phi_2|^2)\). \(S\) is an actual physical field scale, separate from dimensionless metaphysical normalization. If these components belong to the same supplied beam as the original input, its normalization gives \(S=P_*q^2\); an independently supplied context requires its own power account.

A common phase transformation \(\mathbf b\mapsto e^{i\vartheta}\mathbf b\) leaves a phase-insensitive material response unchanged. Smoothness at zero field then permits a quadratic term as the lowest nonconstant order. A real frequency shift has the general leading form

\[
\begin{aligned}
\delta\omega&=\mathbf b^\dagger G\mathbf b,\qquad G=G^\dagger,\\
&=S\left[G_{11}|\phi_1|^2+G_{22}|\phi_2|^2
+2\operatorname{Re}(G_{12}\bar\phi_1\phi_2)\right].
\end{aligned}
\tag{47}
\]

The coefficients of \(G\) have units of inverse seconds per watt. Higher field orders are neglected. The symmetry permits this form but does not require any coefficient to be nonzero.

The diagonal terms are real frequency shifts caused by the individual components. They cannot simply be omitted. Measure them separately and include their sum, \(\delta\omega_{\rm diag}\), in the baseline detuning. Set the relative phase origin by calibration so that the off-diagonal coefficient can be written as a real \(g\). Without this phase calibration, both real and imaginary parts of \(\bar\phi_1\phi_2\) enter.

The remaining coherent shift is then

\[
\delta\omega_{\rm coh}=SgX,
\qquad X=2\operatorname{Re}(\bar\phi_1\phi_2).
\tag{48}
\]

With \(\Delta_{\rm cal}=\omega_{\rm drive}-\omega_0-\delta\omega_{\rm diag}\), the probe response becomes

\[
\boxed{
\tau\dot z+
\left[1-i\tau\Delta_{\rm cal}+i\lambda(S)X\right]z=qc,
\qquad \lambda(S)=\tau Sg.
}
\tag{49}
\]

At zero calibrated detuning this recovers equation (43). Thus the original constant \(\lambda\) is a coefficient at a specified context power, response time, material, and geometry. It is not a universal number supplied by \(E=1\). In this leading-order mechanism, it vanishes with the interacting field strength and grows linearly with \(S\) while the perturbative assumptions hold.

### 12.3 A physical expression for the coefficient

One scalar realization is an intensity-dependent, real dielectric perturbation,

\[
\delta\epsilon(\mathbf r)=\alpha(\mathbf r)
\left|b_1 f_1(\mathbf r)+b_2 f_2(\mathbf r)\right|^2.
\]

The context mode profiles \(f_j\) are normalized consistently with the power amplitudes \(b_j\). \(\alpha\) is an effective material coefficient for the chosen polarizations and frequencies. For an unperturbed probe field \(f_a\), first-order eigenfrequency perturbation gives

\[
\delta\omega\simeq
-\frac{\omega_0}{2}
\frac{\int\delta\epsilon\,|f_a|^2\,dV}
{\int\epsilon\,|f_a|^2\,dV}.
\tag{50}
\]

This follows by varying the fixed-boundary Maxwell eigenproblem and taking its inner product with the unperturbed mode. It uses a real, nondispersive dielectric and the approximately Hermitian high-quality-mode limit; strongly leaky or dispersive cavities need a different normalization. A derivation and its limits are given in [Christopoulos et al., material perturbation theory, Eq. 20 and Appendix A](https://arxiv.org/html/2312.03539v2).

Expanding the local intensity yields

\[
\boxed{
G_{ij}=-\frac{\omega_0}{2D}
\int\alpha(\mathbf r)|f_a(\mathbf r)|^2
f_i^*(\mathbf r)f_j(\mathbf r)\,dV,
\qquad D=\int\epsilon|f_a|^2\,dV.
}
\tag{51}
\]

This makes \(g\) calculable from material response, field normalization, and geometry. Modes that are orthogonal in the input power inner product need not be orthogonal with this local interaction weight. If the weighted overlap vanishes, then \(g=0\) for this mechanism.

For a fully calculable overlap illustration, take dimensionless \(x\in[0,2\pi]\), globally orthogonal profiles \(f_1=e^{ix}/\sqrt{2\pi}\), \(f_2=e^{-ix}/\sqrt{2\pi}\), and a nonnegative interaction weight \(w=1+v\cos2x\), \(|v|\leq1\). The corresponding matrix, up to a signed material scale \(\sigma g_0\), is

\[
G=\sigma g_0
\begin{pmatrix}1&v/2\\v/2&1\end{pmatrix},
\qquad g_0>0,\quad \sigma=\pm1.
\tag{52}
\]

The overlap \(g=\sigma g_0v/2\) is fixed once that weight and material scale are specified. This illustrates the geometry calculation; it is not a measured device or a claim that every orthogonal optical mode pair has this overlap.

### 12.4 Physical accounting and validity

The imaginary term in equation (49) contributes zero to \(d|z|^2/dt\) directly. With constant context and the effective mode normalization, the probe's input-storage-output identity remains intact. It redirects the steady probe transfer by changing detuning; it introduces no probe gain in this approximation.

A full implementation must also account for the context beams, the material interaction, and any controller. Changing the material or context in time can involve modulation work and interaction energy. The algebraic cancellation in a reduced probe equation alone does not establish a complete physical budget for those components.

The derivation requires small material perturbations and frequency shifts relative to the carrier, isolation from other resonances, and approximately fixed decay rates. A small shift compared with the optical carrier need not be small compared with the cavity linewidth. Changes of linewidth, absorption, or conversion into other frequencies would require extending this phase-only law.

## 13. Constraints on the effect

### 13.1 The state and geometry impose bounds

For the normalized states with \(\kappa=(1,0,\ldots)\),

\[
\boxed{
|X|\leq2|\phi_1||\phi_2|
\leq|\phi_1|^2+|\phi_2|^2
\leq1-|c|^2.
}
\tag{53}
\]

Therefore \(|\delta\omega_{\rm coh}|\leq S|g|(1-|c|^2)\). The phase-dependent contribution vanishes when either context component is absent or their calibrated relative phase makes \(X=0\). Individual-component baseline shifts can remain.

For the scalar realization (51), additionally assume \(\alpha\) has one sign throughout the interaction region. Then \(G\), up to its overall sign, is a Gram matrix with nonnegative weight. Cauchy-Schwarz gives

\[
\boxed{
|G_{12}|^2\leq|G_{11}G_{22}|,
\qquad
|\delta\omega_{\rm coh}|
\leq S\left(|G_{11}||\phi_1|^2+|G_{22}||\phi_2|^2\right)
=|\delta\omega_{\rm diag}|.
}
\tag{54}
\]

These bounds do not follow from Hermiticity alone; the one-sign interaction weight is essential. Within that realization, a nonzero coherent term cannot coexist with two exactly zero individual-component coefficients. Separate frequency-shift measurements therefore constrain the size of the coherent effect before fitting the phase comparison.

### 13.2 Phase and power cannot be fitted independently

At zero calibrated detuning with constant context and nonzero probe input \(u=qc\), write \(y=\lambda X\). The steady solution is

\[
\boxed{
\frac{z}{u}=\frac1{1+iy},\qquad
\theta=\arg(z/u)=-\arctan y,\qquad
\mathcal T=\frac{P_{\rm out}}{P_*|u|^2}
=\frac1{1+y^2}=\cos^2\theta.
}
\tag{55}
\]

For the two states in equation (41), \(X_\pm=\pm1/2\). Let \(D_\theta=\theta_+-\theta_-\). Then

\[
\boxed{
D_\theta=-2\arctan(\lambda/2),
\qquad \mathcal T_+=\mathcal T_-
=\cos^2(D_\theta/2).
}
\tag{56}
\]

The model consequently ties the phase contrast to a specific reduction of transmission from the calibrated resonant baseline. It also predicts an unchanged intensity decay time after probe switch-off with the context held fixed. At small \(|\lambda|\), phase contrast is first order, \(D_\theta\simeq-\lambda\), while the fractional transmission reduction is second order, \(1-\mathcal T\simeq\lambda^2/4\).

### 13.3 Turning a measured null into an upper bound

For the balanced two-state comparison, an upper confidence bound \(|D_\theta|\leq\delta<\pi\) gives

\[
\boxed{
|\lambda|\leq2\tan(\delta/2),\qquad
|g|\leq\frac{2\tan(\delta/2)}{\tau S},\qquad
1-\mathcal T\leq\sin^2(\delta/2).
}
\tag{57}
\]

The coefficient bound requires calibrated nonzero \(S\) and \(\tau\); their uncertainties must be included. The formula assumes the single phase-only mechanism with the calibrated baseline, so unbounded cancelling mechanisms would invalidate an interpretation as a bound on one component of the total effect.

For illustration only, a future experiment establishing a 1-milliradian upper bound on the phase contrast would imply

\[
|\lambda|\lesssim0.00100000008,
\qquad
1-\mathcal T\lesssim2.5\times10^{-7}
\quad\text{(approximately 0.25 parts per million).}
\]

This is a conditional sensitivity calculation, not a bound already measured for our proposed system.

### 13.4 A constrained experiment

Use several independently measured context powers and a continuous relative-phase sweep at fixed component powers. In the model,

\[
X=2|\phi_1||\phi_2|\cos\vartheta,
\qquad
\boxed{\frac{-\tan\theta}{\tau S X}=g}
\quad(SX\ne0).
\tag{58}
\]

After phase-origin and baseline calibration, one common \(g\) must predict all held-out powers and phases. Near \(X=0\), compare the un-divided phase relation to avoid magnifying measurement noise.

| Measurement | Required behavior within this approximation |
| --- | --- |
| Context power sweep | Coherent frequency shift proportional to \(S\) |
| Relative phase reversal | Coherent frequency shift changes sign |
| One context component removed | Coherent term disappears; its diagonal contribution is accounted separately |
| Two equal-power opposite-phase states | Opposite phase offsets and equal transmission |
| Phase and transmission measured together | Equation (55) or (56) holds |
| Probe ring-down at fixed context | Intensity lifetime remains unchanged |
| Context weighted overlap eliminated | This coupling coefficient becomes zero |

Measure the individual-component shifts first, calibrate the interaction coefficient or calculate it from independently characterized material and mode profiles, then reserve other settings for prediction. Stabilize the probe's supplied overlap and baseline detuning, randomize measurement order, and quantify thermal, absorptive, and mode-mixing alternatives.

If these relationships fail beyond the assessed uncertainty, this particular phase-only mechanism fails in that regime. If they hold, they support the specified physical coupling. The derivation uses conventional field interaction and therefore supplies no exclusive evidence for a metaphysical origin. A distinct Circumpunct prediction would need an additional, independently justified constraint beyond this conventional model.

## 14. What is now specified

Given:

1. A distinguished point \(p\).
2. A normalized potential representation \(\Phi(t)\).
3. A bounded coupling profile \(\kappa_p\).
4. A finite power scale \(P_{*,p}\).
5. A normalized output distribution \(w_{p,j}\).
6. Optionally a response time \(\tau_p\) and initial amplitude.
7. For the supply extension, incoming availability or a source state \(R\), its availability law, and any replenishment.

The model gives explicit convergence, response, emergence, supply, storage, finite-transfer, and record equations. A static potential and fixed coupling give a calculable baseline when the supply is specified. Time-varying inputs or changing couplings must be specified to calculate their consequences.

What remains to be explained physically:

- Why a particular center has a particular coupling profile.
- What sets its power scale, response time, and output geometry.
- Which real source could implement the proposed depletion law and perfect return recovery.
- How accurately the interface model predicts new experimental data once its parameters are fixed.
- Whether a specific additional law can be derived from the metaphysical premises and tested against conventional alternatives.

The response and power account match a standard optical-cavity model under stated assumptions. A published experiment is consistent with the generalized overlap account. The additional phase law now has a conditional physical derivation, a coefficient determined by power and overlap, and linked phase, transmission, and decay predictions. The metaphysical premises still do not specify a distinct measurable correction to that conventional description.

## Numerical verification

The infinite geometric sum was compared with 128-term numerical sums over 2,001 phase values. Maximum amplitude discrepancy was below \(4.5\times10^{-16}\). For \(P_*=10\) W, the output ranged from \(3.6\) to \(10\) W up to floating-point rounding.

The overlap bound was additionally checked on 100 independently generated pairs of normalized complex vectors. The response-time solution was checked against independent numerical integration for \(\tau=0.1,\ 1,\ 10\) s; maximum amplitude discrepancy was below \(2.2\times10^{-12}\).

For the supply extension, equation (27) was checked on 10,000 independently generated complex input and response pairs within the unit disk. The largest balance residual was below \(2.2\times10^{-14}\) W at \(P_*=10\) W. Independent quadrature of the four-second pulse reproduced the input, storage, and outgoing transfers with a balance residual below \(2\times10^{-15}\) J before rounding.

The finite-source dynamics were integrated with \(P_*=10\) W, \(\tau=1\) s, \(R_c=10\) J, \(R(0)=100\) J, \(z(0)=0\), no replenishment, and \(c(t)=\exp[0.4i\sin(t/(1\,\mathrm{s}))]\). Over 100 seconds, the maximum sampled discrepancy in \(R+U+W=100\) J was below \(10^{-11}\) J. The source remained nonnegative, and the response amplitude stayed below one. At 100 seconds, approximately \(0.138678\) J remained in the source, \(0.001873\) J in interface storage, and \(99.859449\) J had reached the designated output.

For the physical correspondence, the dimensional cavity equation and normalized response equation were integrated independently with a time-varying complex drive. Their normalized amplitudes agreed to within \(1.4\times10^{-11}\) over the sampled interval. Quadrature of temporal overlaps for six pairs of normalized exponential waveforms agreed with the analytic expression to within \(5.7\times10^{-15}\).

For the optional extension only, the two states in equation (41) were checked to have unit norm, equal coupling, and \(X=\pm1/2\). An illustrative \(\lambda=0.1\) gives a phase contrast of approximately \(-0.0999168\) radians, with identical output intensities. This value is a calculation for an assumed parameter, not an observed effect. The additional phase term preserved the normalized energy identity on 10,000 random complex states to within \(1.8\times10^{-15}\).

For the conditional derivation, direct spatial integration of the example (52) at \(v=0.8\) reproduced the analytic matrix to within \(2.3\times10^{-16}\). Direct integration of the full local intensity over 101 relative phases agreed with the diagonal-plus-coherent expression to within \(2.3\times10^{-16}\). The normalized frequency-shift factor ranged from 0.3 to 0.7 for the fixed-amplitude context pair, as predicted. Random checks on 10,000 Gram matrices and normalized states found no violations of the state and geometry bounds. Across 10,001 trial values of \(\lambda\), the phase-transmission identity (56) agreed to within \(9\times10^{-16}\).

The numerical checks establish algebraic and computational consistency. The comparison in section 10.3 uses published experimental parameters; no new laboratory measurement or raw-data fit has been performed. No empirical value or upper bound for the proposed \(g\) or \(\lambda\) has been obtained, and none of these checks validates the metaphysical interpretation.
