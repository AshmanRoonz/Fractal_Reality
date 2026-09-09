# Navier-Stokes: the cascade-completion argument against the 2026-09 blowup results

**Status:** review record, not an adjudication. Ashman to decide what (if anything) gets retracted.
**Occasion:** Ashman asked how close `clay/navier_stokes_formal_proof.md` came to OpenAI's "Finite Time Blowup for Navier-Stokes" (published 2026-09-08).

**Sourcing caveat, stated first.** `cdn.openai.com` and `openai.com` are blocked by this session's network egress policy, so the PDF and the OpenAI write-up were not read directly. Everything below about the new results is reconstructed from secondary sources reached by search (Tao's blog post of 2026-09-07, Quanta, Nature, Fortune, Buckmaster's public statement, Unite.AI, heise). Direct quotes of the theorem statement are second-hand. Anything here that turns on the exact hypotheses should be re-checked against the PDF from an unblocked network before it is treated as settled.

---

## 1. What the new results prove

Two things happened within a day of each other, and they are being conflated in the press.

**Buckmaster and Alpöge (2026-09-07, three preprints).** Finite-time blowup with a **smooth forcing term** for the incompressible porous medium equation, the 2D Boussinesq system, and the 3D incompressible Euler equations. This extends the program of Córdoba and Martínez-Zoroa, who had the same blowups with **rough** forcing; the new contribution is smoothing the force. Tao's post says these do not quite reach full Navier-Stokes but make it look feasible.

**OpenAI (2026-09-08, "Finite Time Blowup for Navier-Stokes", ~166 pages plus a Lean formalization).** The claim reaches Navier-Stokes itself. Reported statement: for every positive viscosity there exist smooth initial data and smooth forcing for which no global smooth solution with uniformly bounded kinetic energy exists on ℝ³, and likewise on ℝ³/ℤ³. This is Fefferman's statements **(C)** and **(D)**. OpenAI says it will not claim the prize.

**Priority dispute.** Buckmaster alleges the OpenAI effort was triggered by rumors of his unpublished work with Alpöge, that OpenAI misrepresented how independently its model reached the result, and that co-authorship was offered on condition Alpöge be excluded. Tao separately criticized the use of Millennium problems as marketing. This record takes no position on the dispute; it is noted because it bears on how much of the mathematical credit is OpenAI's.

**The mechanism.** Successive amplification of oscillatory layers across geometrically shrinking scales, with larger-scale strain amplifying smaller-scale vorticity, and approximations of increasing order used to keep every spatial derivative of the force uniformly bounded. In the OpenAI construction, oscillatory pulses generate a mean momentum flux that supplies the missing force on a collapsing background vortex. The solution starts **from rest**, develops **unbounded velocity** in finite time, and keeps **kinetic energy uniformly bounded** throughout.

The physical picture reported for the blowup: a vortex core that contracts while spinning faster, with incompressibility forcing axial stretching so the fluid cannot simply pile up, and angular and axial speeds growing as the core narrows.

---

## 2. What the corpus claims

Three documents, two distinct strategies, one conclusion.

| Document | Date | Strategy | Conclusion |
| --- | --- | --- | --- |
| `Path_of_Learning/claymathsolutions/navier_stokes_functional_analysis.md` | 2025-10-29 | 3D turbulence as a projection of smooth high-dimensional flow | global regularity |
| `clay/navier_stokes_cascade_completion.md` | 2026-04-03 | drain-stretch coupling (prose form) | global regularity |
| `clay/navier_stokes_formal_proof.md` | 2026-04-03 | drain-stretch coupling (formalized) | global regularity |

The formal proof's spine: Littlewood-Paley decomposition; Beale-Kato-Majda reduces regularity to control of ‖ω‖_∞; every nonzero strain configuration in 3D incompressible flow is three-dimensionally unstable (Bayly, Waleffe, Pierrehumbert, Crow), so instability growth rate σ ≥ c₀|S| universally (Theorem 3.4); therefore the cascade drain Γ_j is bounded below by c₀ times the enstrophy production 𝒲_j (Theorem 3.5); effective stretching drops to (1 − c₀)𝒲_j; viscosity absorbs the remainder at small scales while Leray's inequality handles large scales; the BKM integral converges.

**Critically: the corpus documents set f ≡ 0.** Forcing appears nowhere in either April 2026 document. They target Fefferman (A) and (B).

---

## 3. The headline

**Opposite conclusions, and different problems.**

The corpus says 3D Navier-Stokes never blows up. The new results say it does. But the corpus proves (or attempts) the **unforced** case and the new results establish the **forced** case, so the two are not in strict logical contradiction. Both could be true: unforced Navier-Stokes globally regular, forced Navier-Stokes able to blow up. (A) and (B) remain open; the cascade-completion argument is not refuted by the new work.

That is the generous reading, and it is honest as far as it goes. The rest of this record says why it does not go very far.

---

## 4. Where the idea was genuinely close

Five points of real contact, and they are not trivial.

**4.1 The arena is right.** Both treat the whole problem as a competition, between scales, over how much amplification the nonlinearity moves down the ladder per unit time. The dyadic-scale framing, the identification of the strain tensor as the driver, and the reduction to BKM are the standard and correct setting. Nothing here is off-topic.

**4.2 "Compression and transfer are the same mechanism" is correct, and it is the engine of the blowup.** §1.2 of the cascade document says the term (ω·∇)u that drives stretching *is* the term that drives transfer to smaller scales, one mechanism seen twice. The Córdoba-Martínez-Zoroa machinery runs on exactly that identification: larger-scale strain amplifying smaller-scale vorticity. The corpus found the right lever and then assumed it always pulls the safe way.

**4.3 The self-similar cascade architecture is right.** A3 insisting the same engine runs at every scale is the shape of the construction: successive amplification of oscillatory layers, each feeding the next, geometrically. "The energy echoes through scales, each echo weaker, and the process is self-similar" is the correct architecture with the damping assumed rather than derived.

**4.4 "There is no floor" (§1.4) is shared, with the sign flipped.** The corpus takes the absence of a smallest scale as the reason blowup cannot happen (the convergence always has somewhere to go, so it completes instead of accumulating). The construction takes the absence of a floor as the reason blowup *can* happen: the cascade runs through infinitely many scales in finite time and arrives. Same premise; opposite conclusion.

**4.5 The ice skater is the blowup.** The reported physical picture of the singularity (a vortex core contracting while spinning faster, incompressibility forcing axial stretching so the fluid cannot pile up) is the opening image of `navier_stokes_cascade_completion.md`, almost line for line. The corpus described the singularity mechanism accurately and then argued it cannot complete. It completes.

---

## 5. Where the idea was far

**5.1 Wrong target statement.** (A)/(B) versus (C)/(D). Even granting everything, the corpus is not addressing the problem that was just resolved.

**5.2 Bounded energy does not save you, and the construction says so explicitly.** Corollary 5.2 leans on ∫Z_j dt ≤ E₀/ν from Leray to control large scales. The new construction develops **unbounded velocity while kinetic energy stays uniformly bounded**. That is a direct demonstration that the energy budget alone cannot close the argument, in exactly the place the proof leans on it.

**5.3 The load-bearing step (Theorem 3.5) is heuristic, not proved.** Steps 3 and 4 read: "within one eddy turnover time τ_j ~ 1/‖S_j‖_∞, the perturbation enstrophy at scale j+1 reaches O(1) fraction of the base enstrophy at scale j", and "Γ_j ~ c₀ Z_j / τ_j". Those are turbulence-phenomenology scalings written with ~, inside a proof whose conclusion needs ≥. Nothing in Sections 2 to 4 turns the ~ into a ≥.

**5.4 Linear stability theorems are being applied where they do not apply.** Bayly, Pierrehumbert, Waleffe and Crow are linear stability results about **frozen base flows** with scale separation between the base and the perturbation. Approaching a singularity there is no scale separation: base flow and perturbation evolve on the same timescale, and the growth rate the instability needs is comparable to the rate at which the thing it is destabilizing changes. Theorem 3.4 imports these results pointwise into a time-evolving near-singular solution, which is precisely the regime where they lose their justification.

**5.5 Proposition 2.2 assumes statistical steady state.** "In statistical steady state, d/dt Σ_{k≤j} E_k ≈ 0" is a turbulence-modeling hypothesis about ensembles. A specific smooth solution that is about to blow up is the opposite of a steady state.

**5.6 Double counting in Theorem 5.1.** Γ_j is inserted into the enstrophy identity as a separate negative term alongside ⟨ω_j, 𝒮_j⟩ and ⟨ω_j, ℛ_j⟩. But the inter-scale transfer out of band j is not a term the vorticity equation has in addition to the stretching and remainder terms; it is already inside them. Subtracting Γ_j on top is subtracting the same drain twice.

**5.7 The α step is an analogy, not a derivation.** §4.2 and Proposition 2.4 argue that the 2/φ³ term in the closed form for 1/α, read as a "bidirectional valve correction", forces the drain rate to match the stretch rate in a fluid. Two formalisms are being identified by the shape of a factor of two. Nothing licenses transporting a coefficient in a number-theoretic expression for a coupling constant into an inequality between two functionals on Sobolev space. This is the step that fixes c₀, and it is the weakest link in the chain.

**5.8 Method gap.** The new result is an explicit construction with a Lean formalization and a public repository. The corpus documents are prose arguments citing physical literature, with the decisive estimate acknowledged as unfinished.

---

## 6. A concrete error in `clay/navier_stokes_formal_proof.md`

Independent of anything OpenAI did, the critical-scale argument in §5.2 has its inequality reversed.

Equation (5.2b) reads

    dZ_j/dt ≤ 2 Z_j [ (1−c₀) C · 2^(5j/2) · √(2E₀) − c ν · 2^(2j) ]

and (5.2c) defines j_* by setting the two terms equal, giving 2^(j_*/2) = cν / ((1−c₀) C √(2E₀)).

Factor the bracket:

    bracket = 2^(2j) · [ (1−c₀) C √(2E₀) · 2^(j/2) − cν ]

The bracket is **positive exactly when j > j_***, because 5j/2 exceeds 2j for j > 0; the stretching bound grows like 2^(5j/2) and the viscous term only like 2^(2j), so their ratio grows like 2^(j/2) without bound. Under the proof's own bound, viscosity **loses** at scales finer than j_*, not wins. Equation (5.3), "dZ_j/dt ≤ −cν 2^(2j) Z_j for j > j_*", asserts the opposite of what (5.2b) and (5.2c) give, and Corollary 5.1's exponential decay, Step 2 of §5.3, and Step 6's uniform Sobolev bound all rest on it.

Numerically (c₀ = 0.3, C = c = ν = E₀ = 1, so j_* ≈ 0.029):

| j | stretching rate | viscous rate | bracket |
| --- | --- | --- | --- |
| −3.97 | 0.00102 | 0.00407 | negative (decay) |
| 0.03 | 1.041 | 1.041 | zero |
| 2.03 | 33.3 | 16.7 | **positive (growth)** |
| 8.03 | 1.09e6 | 6.82e4 | **positive (growth)** |

This is not a slip in bookkeeping; it is the scaling-supercriticality of 3D Navier-Stokes reappearing where the proof needed it to be absent. Any argument that controls ‖S_j‖_∞ through Bernstein plus the energy bound alone will meet this wall, because that is the wall the problem is famous for.

---

## 7. Tao's barrier

Tao's 2016 finite-time blowup for an **averaged** 3D Navier-Stokes is the standing obstruction to arguments of this shape, and it is the acknowledged conceptual stepping stone for the new work. The averaged equation satisfies the same energy identity, the same cancellation structure in the nonlinearity, and the same scaling, and it blows up. So no proof of global regularity can succeed using only the energy identity plus standard harmonic-analysis estimates; it must use finer structure specific to the true nonlinearity.

Section 5 of the formal proof, after Theorem 3.5 is granted, uses only the energy bound, Bernstein, and Leray. All of the barrier-passing content is inside Theorem 3.5, which is the step derived heuristically. That is the shape a proof takes when it has not yet met the barrier rather than passed it.

---

## 8. What this does and does not settle

**Not refuted.** The unforced problem is still open. Nothing published on 2026-09-08 shows that unforced 3D Navier-Stokes blows up.

**Made harder to believe.** §4.1 of the cascade document states that what remains is "a translation problem, not a conceptual one": the drain-stretch coupling is taken as established and only in need of expression in Sobolev norms. That is the specific claim the new work most directly undercuts. The coupling was asserted to be a universal geometric fact about incompressible 3D flow, following from the strain eigenvalue constraint λ₁ + λ₂ + λ₃ = 0 and from the pump's bidirectional symmetry, neither of which mentions forcing. Forcing is an additive linear term; it changes no part of the nonlinear geometry the argument invokes. If the coupling really were a structural identity of that geometry, adding a smooth force should not be able to reverse it into a machine that drives collapse. That it does suggests the coupling is not a structural identity but a statistical regularity of ordinary turbulence, true of typical flows and defeasible by adversarially arranged ones.

**Confirmed as the right arena, and as an honest document.** §3 and §4 of the cascade file name their own gaps (the projection argument's Assumptions 4.1 to 4.2; the missing rigorous lower bound on c₀; the uniformity-across-configurations problem). The corpus's own editorial law was followed. The error in §6 above is new information, and per "no silent retraction" it should get a dated notice in the file itself if Ashman agrees with the reading.

---

## 9. Verdict

Close on **arena and architecture**; not close on **conclusion, target statement, or method**.

The corpus identified the correct battleground (cross-scale transfer of the strain tensor's amplification), described the actual singularity mechanism accurately (the contracting, axially stretched, faster-spinning vortex core), and correctly saw that stretching and cascade are one mechanism rather than two. It then assumed the mechanism's sign, and staked the proof on that assumption via a coefficient imported from an unrelated formalism. The published work runs the same mechanism with the opposite sign and constructs the singularity out of it.

Compact form: the ice skater was right, the pump was the wrong reason to think she stops.

---

## 10. Open items for Ashman

1. Adjudicate whether §6's reversed inequality warrants a retraction notice on `clay/navier_stokes_formal_proof.md` §5.2 and its dependents (Cor. 5.1, §5.3 Steps 2 and 6).
2. Decide the status of Proposition 2.4 and §4.2 (the α-to-c₀ transport). This record grades it as an analogy; the framework's own type discipline (§27.7t, ill-typed decompositions retired) is the natural instrument if it is to be retired.
3. Decide whether the corpus wants a claim about the **forced** problem at all. As written, both April documents are silent on f, so neither is touched by (C)/(D).
4. Re-read the actual PDF from an unblocked network and correct anything in §1 that this record got second-hand.

---

## References

- OpenAI, "Finite Time Blowup for Navier-Stokes" (2026-09-08). https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf ; write-up at https://openai.com/index/navier-stokes-solution/ ; Lean at https://github.com/openai/NavierStokesAndEuler
- T. Tao, "Finite time blowup with smooth forcing term for the incompressible porous medium, Boussinesq, and incompressible Euler equations", 2026-09-07. https://terrytao.wordpress.com/2026/09/07/finite-time-blowup-with-smooth-forcing-term-for-the-incompressible-porous-medium-boussinesq-and-incompressible-euler-equations/
- T. Buckmaster, public statement, 2026-09-08. https://cims.nyu.edu/~tristanb/statement.pdf
- Quanta Magazine, "AI Has Solved One of Math's $1 Million Millennium Prize Problems", 2026-09-08.
- Nature, "OpenAI claims huge maths breakthrough on a famed 'Millennium Problem'", 2026.
- Fortune, 2026-09-08 (priority dispute).
- T. Tao, "Finite time blowup for an averaged three-dimensional Navier-Stokes equation", J. Amer. Math. Soc. 29 (2016).
- D. Córdoba, L. Martínez-Zoroa, and collaborators, blowup with rough forcing (IPM, Boussinesq, Euler).
- Corpus: `clay/navier_stokes_formal_proof.md`, `clay/navier_stokes_cascade_completion.md`, `Path_of_Learning/claymathsolutions/navier_stokes_functional_analysis.md`.
