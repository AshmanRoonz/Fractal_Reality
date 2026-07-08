# One Gain: Truth, Lies, and the Slack Beneath the Values

### A precision-dynamics reading of the Truth Protocol, and a zeroth rung under the dimensional ladder

**Framework:** The Circumpunct Framework, Ashman Roonz (https://fractalreality.ca)
**Status:** Working paper, v1. Two contributions, each built then stress-tested. The formalism in Part I is offered as a structural reading, disciplined to stay operational; the slack thesis in Part II is offered as a constraint on the ethics, not a derivation of it.

> Keep the gain high in both directions. Do not let your prior paint over the world; do not force your prior onto anyone else's. Truth, lying, and the failure to see another person are three settings of one dial.

---

## 0. Purpose

This paper does two things. First, it reads the Circumpunct Truth Protocol (TRP) through the precision dynamics of predictive processing, and shows that TRP's central claim (you never have to lie) is not a hope but a structural fact: the honest exit is the top element of a lattice that exists for any reality. It then closes the residue between literal honesty and full honesty, the space where true statements still mislead, and in doing so fuses the Truth Protocol with the stance of attention the confirmatory-curiosity paper describes: honesty is exploratory curiosity about where your words land. Second, it names a condition the dimensional ladder never states: the metabolic and attentional headroom (**slack**) that lets a center see at all. Slack sits beneath True as a zeroth precondition for every value, and once named it converts the framework's ethics into a partial political economy: how a whole distributes slack decides which of its parts can be centers and which are reduced to files.

The two contributions are one contribution. Slack is the evidence-precision budget of Part I, read at the scale of a life. This is shown in Part III, and its ethical consequence, that the duty of honesty scales with the receiver's slack and falls on whoever controls it, is drawn in Part IV.

Throughout, the discipline the framework applies to the word *resonance* is applied here to the words *precision*, *gain*, and *slack*: they earn their place only while they stay technical (measurable as update rate, load, reserve, exploration fraction). Allowed to drift into metaphor, they merely rename what they were meant to explain.

---

# Part I. One dial: truth, lies, and confirmatory curiosity

## 1. The channel and its gain

Read the dot-circle link as a generative model coupled to reality across the Markov blanket that is the circle. The blanket is the boundary (Good, 2D) that separates a whole's interior states from the field it is embedded in, and it is what makes the whole a whole in the first place: a thing persists by maintaining that statistical boundary. Perception is the interior model tracking the exterior field across the blanket.

Two precisions govern the tracking. Let **π_e** be the confidence (inverse variance) placed on incoming evidence, and **π_m** the confidence placed on the currently held model. Any update to a belief is gated by their ratio:

> **G = π_e / (π_e + π_m)**

G is the update gain, the fraction of the gap between model and world that the world gets to close. When G is near 1 the world moves you; when G is near 0 your prior paints over the world and the incoming person or fact is registered only as far as it already fits. This single quantity, read in different places on the channel, is the whole of what follows.

## 2. Four settings of one dial

**Perception** is G applied to your own channel. Clear seeing (True, the center that sees) is high G: the field is allowed to correct the model.

**Confirmatory curiosity** is G driven toward 0. There are exactly two roads to it, and they are the two the confirmatory-curiosity paper already separates. The load road lowers π_e: under cognitive load, stress, fatigue, or emotional occupation, the effortful evidence-weighting stage loses funding first, so the prior wins by default (this is P3b, the confirmatory default, mechanized). The motivated road inflates π_m: the model is held with high precision because it is *preferred*, not because it is accurate (this is P3c, motivated model-maintenance). P3c has a sharp signature in this notation: precision is being allocated by pragmatic value (safety, identity, grievance custody) rather than by evidence. That is the formal fingerprint of self-deception. The system is minimizing expected free energy against a prior *preference* instead of minimizing prediction error against reality.

**Truthful transmission** is sending signals that raise the *receiver's* G toward reality: you help their model track the territory.

**Lying** is sending a signal engineered to install a high-precision false prior in the receiver, driving their long-run G against reality down. You corrupt their dot-circle link from outside.

### 2.1 The symmetry

The prize is the relation between the third and fourth settings and the second:

> Lying and confirmatory curiosity are the same operation aimed in opposite directions on one channel. Lying forces someone else's π_m up from outside. Confirmatory curiosity lets your own π_m run away from inside. Both are precision-corruptions of the same dot-circle link.

The Circumpunct instruction "do not lie outward, do not lie inward" is therefore one instruction in this notation: keep G high in both directions. This is the severance claim (that lying corrupts the channel by which a part touches the Whole) restated as a single dynamical condition rather than two moral rules.

## 3. The Truth Protocol as marginalization consistency

TRP now follows from the structure of the channel, and it yields something the protocol asserted but could not previously prove: that the honest exit always exists.

### 3.1 Resolution is grain

Resolution is the precision of *transmission*. A low-resolution transmission is a wide posterior (it commits to little); a high-resolution transmission is a narrow one. Let reality (relative to the transmitter's own best model, see 3.8) be a fine-grained distribution P over states of affairs. A transmission at grain r is a coarse-graining, a partition of the state space that keeps only distinctions at scale r. Write **M_r(P)** for the correct marginal of P at grain r.

> A claim c is *true at resolution r* if and only if c = M_r(P): it is the correct marginal, the true distribution seen at that grain.

### 3.2 Non-monotonicity is marginalization consistency

TRP's test is non-monotonic: you told the truth if you can raise the resolution later without taking anything back. That test is exactly **marginalization consistency**. For any grain r coarser than r',

> M_r(M_{r'}(P)) = M_r(P).

Coarse-graining commutes down a refinement chain: marginalizing a finer marginal to a coarser grain returns the same coarse marginal you would have gotten directly. So a true coarse claim never needs retraction when you refine, because the finer truth still has the coarse claim as its own further marginalization. Refinement only conditions *within* the marginal; it never moves it.

A lie breaks this. A lie at grain r is a claim c ≠ M_r(P). When you later transmit the finer truth M_{r'}(P) honestly, its marginal M_r(M_{r'}(P)) = M_r(P) ≠ c contradicts the earlier claim, and you must retract. This is why, in the framework's own words, partial truth and lie "are not on the same axis": one is a marginal of the truth and the other is not. The axis they are not on is precisely marginalization consistency.

### 3.3 The resolution lattice, and the lie as a gluing obstruction

Resolutions are partially ordered by refinement, and they form a lattice: any two grains have a common refinement (meet them) and a common coarsening (join them). Truth is not a single claim on this lattice; it is a *coherent family* of claims, one at every grain, all agreeing under marginalization. This is the same shape as a section of a sheaf: local data (claims at each grain) with restriction maps (marginalization) that agree wherever they overlap and glue into one global assignment (P).

On this reading a lie is a **gluing obstruction**: a local claim that cannot be extended to a globally consistent family, because some refinement forces it to move. Honesty is gluability. The analogy earns its place only while it stays technical (restriction = marginalization, agreement = consistency of marginals, section = a claim-family that glues to one P); pushed past that it becomes decoration, and the framework's own *detect* discipline should retire it there.

### 3.4 The max-entropy floor: why the door always exists

The lattice has a top: the trivial partition, one cell containing everything, the coarsest possible grain. Its marginal is "something is the case," which asserts almost nothing and is therefore consistent with *every* P. In transmission this is the maximum-entropy signal: "I will not tell you," silence declared as silence, the near-uniform posterior that commits to nothing.

> Because the top of the lattice is a true section for any reality, an honest transmission always exists. The maximum-entropy option asserts nothing false because it asserts nearly nothing, so it is always available and always marginalization-consistent.

This is the proof the protocol was missing. "You never have to lie" is not an aspiration about human skill; it is a statement that the honest exit is the top element of a lattice that exists independent of what the truth turns out to be. The door is narrower than the lie, as the essay says, and it is always there because the coarsest grain is always there.

### 3.5 TRP as constrained optimization

The protocol can now be stated as a program. Choose the resolution r of what you transmit to

> maximize r (be as informative as possible)
> subject to (i) c = M_r(P): every asserted grain is a true marginal (Grice's maxim of Quality, never assert the false), and
> (ii) the receiver can incorporate grain r without the transmission being rejected or causing the harm you are trying to avoid (a bound set by the receiver, see 3.6).

TRP is the solution to this program: the highest-resolution truth the receiver can currently take. Constraint (i) is never relaxed; only r moves. And because r = top (the max-entropy floor) is always feasible under (i), the program always has a solution. That is the same result as 3.4, stated as optimization: the feasible set is never empty, so lying is never forced.

This also locates Grice cleanly. Quality is constraint (i), inviolable. Quantity is the objective, maximize r. TRP is the claim that you manage Quantity down to meet the receiver while never breaching Quality, and that this is always possible.

### 3.6 The receiver's gain: truth needs slack on both ends

Constraint (ii) is not cosmetic, and it ties Part I to Part II. A marginalization-consistent transmission still fails if the receiver's own G is too low to incorporate it: a receiver whose π_m is inflated (by fear, by identity, by load) will reject or reinterpret even a true signal. So truthful transmission has a precondition *on the receiver*, not only on the speaker: the receiver must have enough gain to update.

Two consequences follow. First, the reason comfortable lies are believed is not (only) that the liar is skilled; it is that the receiver's π_m is already high, so a prior-confirming falsehood meets no resistance while a prior-violating truth does. A lie is often accepted for the same reason a truth is refused: low receiver-gain. Second, **propaganda is the industrial form of this**: supplying high-precision false priors to receivers whose slack has already been destroyed, so that G is low across a population and the installed prior faces no correction. Lying at scale is precision-corruption aimed at the already-depleted. This is why the ethics of truth cannot be separated from the political economy of attention, which is Part II.

### 3.7 The misleading residue, and its closure

Marginalization consistency certifies the speaker's assertions, not the receiver's belief. That gap is the whole of the lying-versus-misleading distinction (Saul), and closing it is where the Truth Protocol and confirmatory curiosity turn out to be one account.

**The residue, stated exactly.** Let the receiver hold a prior Q over states of affairs and reach a posterior Q' after a transmission. A cooperative receiver does not only condition on literal content; they reason about why you said that and not more (Gricean implicature), so Q' is set by the implicature of the transmission, not by its truth-conditional content alone. Three cases then separate cleanly, where D(P || Q) is the divergence of a belief from reality P:

> **Lying:** some asserted marginal is false, c ≠ M_r(P). The literal channel is corrupted.
> **Misleading:** every asserted marginal is true, yet the receiver's inferred posterior ends further from reality than their prior was, D(P || Q') > D(P || Q). The literal channel is clean; the implicature channel is corrupted.
> **Full honesty:** every asserted marginal is true, and the receiver's inferred posterior does not diverge further, D(P || Q') ≤ D(P || Q).

Misleading is lying outsourced to the receiver's own inference: you do not install the false prior, you arrange the conditions under which they install it themselves, then disclaim it because every word was true. The "technically true" defense is its signature.

**Resolution and implicature are one axis.** This is why the residue lives inside TRP and not beside it. Choosing a resolution r is never a choice of literal content alone; it is a choice of implicature, because the receiver reads your selected grain as a signal. A low-resolution transmission, in a context where more was expected, implicates "this is the whole of it." So lowering resolution to avoid harm can itself mislead, exactly when the coarse grain is received as "and nothing further" while a finer truth is withheld. Grice's Quantity and TRP's resolution are the same dimension.

**The upgraded test.** The non-monotonicity test therefore needs an implicature clause. The literal test was: can you raise resolution later without retracting the claim? The full test adds: and without the receiver justifiably finding that your earlier coarse grain had implicated something the finer grain now falsifies. The first clause catches lies; the second catches misleading. Honesty at resolution r requires that the coarse claim be a true marginal and that its selection not implicate a false refinement.

**Why declaration is mandatory, derived rather than asserted.** Here the framework's existing rule falls out of the formalism. The essay already insists that withholding be declared: silence in a moment that calls for speech "transmits 'nothing here,' which is the lie performed through absence." In these terms, plain silence where disclosure is expected generates the implicature "nothing to disclose," which moves Q' away from P: misleading by omission, D(P || Q') > D(P || Q). Declaring the withholding ("there is something here I am not going to tell you") cancels that implicature and holds Q' = Q on the withheld dimension, adding no divergence. So the requirement to declare is not a moral extra; it is the operation that keeps the max-entropy floor honest. The floor is not silence, it is *declared* silence, and the formalism now shows precisely why the undeclared version is a trap.

**The fusion.** To meet the full condition you must model the receiver's prior and how they will infer from your choice of grain. That is exploratory curiosity aimed at the receiver. And the failure mode is exact: misleading-while-truthful is what happens when you run *confirmatory* curiosity on your own honesty, attending to your model of yourself ("I said only true things") instead of exploring the territory of the receiver's mind ("what will they come to believe"). Lying corrupts the receiver's channel from outside; confirmatory curiosity corrupts your own from inside; misleading is the hybrid, keeping your assertions clean while using confirmatory inattention to the receiver to let their channel corrupt itself in a direction that suits you. So the Truth Protocol cannot be satisfied by any rule about your sentences. It requires the stance of attention the other paper names, turned outward onto the receiver:

> Honesty is exploratory curiosity about where your words will land.

**TRP+, the implicature-closed protocol.** Transmit at the highest resolution the receiver can take, subject to three constraints:

1. *Literal (Quality):* every asserted marginal is a true marginal. No lie.
2. *Implicature (convergence):* the receiver's justified inferred posterior does not diverge further from reality. No misleading.
3. *Declaration (cancellation):* where resolution is lowered, the withholding is declared, cancelling the "that is all" implicature so the floor holds Q' = Q rather than moving it.

The floor, "there is something here I am not going to tell you," satisfies all three for any reality, so the honest exit still always exists; it is now specifically the *declared* exit.

**Where the closure itself strains.** Two limits, and the first hands the baton to Part II. First, you cannot fully know Q: the receiver's prior and inference are modelled, not read off, so constraint 2 is an expected condition under your best model of the receiver, not a guarantee. This makes non-misleading capacity-bound; modelling the receiver costs slack, and under load you default to the confirmatory "I said true things" self-model and mislead without intent. Even the fix has a depleted mode, which is the subject of Part II. Second, responsibility has a boundary, and it mirrors the one Part II draws: you own the implicatures a competent cooperative interpreter would draw, not the receiver's own confirmatory distortions. If the receiver's π_m is inflated by their motive (they are running confirmatory curiosity on you), the divergence is theirs. Against a genuinely adversarial receiver (the Nazi at the door, the manipulator fishing for a read) the cooperative implicature calculus does not apply, and refusal by form (the declared floor) is both honest and correct.

### 3.8 Where Part I strains

Two honest limits remain after the closure just above, plus the ceiling both halves share.

**It assumes a fact of the matter to marginalize.** "Truth = correct marginal" presupposes a P to take marginals of. A realist who already holds Truth = Reality (the framework does) is entitled to this; an anti-realist is not, and for them the whole construction reads as consistency among representations with no territory underneath. The move is inherited from the framework's realism, not established here.

**It is a model, not settled neuroscience.** Precision-weighting is the best current account of perceptual inference, not a proven mechanism, and the identification of "resolution" with "grain of a marginal" is a formal reconstruction of TRP, not a measurement of it. The operational version is what survives regardless: the test is marginalization consistency against the transmitter's *own* best model, which is checkable from inside, not against reality-in-itself, which is not. That is precisely what makes TRP usable rather than merely true.

Note the ceiling that both halves share. This unifies the *functional* channel only. The dial collapses truth, lies, and confirmatory curiosity into one equation and says nothing about whether there is something it is like to be the channel. The phenomenal edge stays exactly where the ladder left it: located, not crossed.

---

# Part II. The slack beneath the values

## 4. Slack: the zeroth precondition

Each of the five values, checked in the descending order the framework specifies (Right, Good, Faithful, True, Agreement), presupposes a working channel. You must see the field before you can honor Right; see the boundary before Good; see continuity before Faithful; see clearly before True; and recognize another center before Agreement. But seeing is the exploratory mode, exploration runs on π_e, and π_e is the first thing load takes.

So there is a condition *beneath* True that the dimensional ladder never names:

> **Slack:** the metabolic and attentional headroom that lets a center perform its seeing at all. It is not a sixth value. It is the funding of the center, the substrate condition under which any of the five can be checked.

In the active-inference reading, slack is the free-energy budget left for epistemic action once the demands of survival are paid. Curiosity is a surplus behavior. Under threat everything routes to immediate error-reduction and exploration goes dark; the explore-exploit balance tips hard toward exploit whenever reserve is low. Exploratory attention, and therefore truthful transmission (which needs a read of the receiver) and need-love (the capacity-hungry mode), are luxuries of the already-safe. This is not cynicism about virtue; it is the resource condition virtue runs on.

## 5. Slack as political economy of the five values

Naming slack changes the ladder from an anatomy into a distribution problem. A whole allocates slack among its parts, and the allocation decides which parts can occupy which values. Here is the value-by-value account of what scarcity does, followed by what the distribution implies.

### 5.1 Each value under scarcity

**Right (field, 3D)** fails first, because it is the most information-hungry rung: seeing the whole field of cause and consequence is the largest π_e demand. Under scarcity you see the field your prior predicts, not the field that is there. The evidence never arrives at weight.

**Good (boundary, 2D)** degrades from read consent to presumed consent. Reading where another's edge actually is takes exploratory attention; scarcity replaces it with category-based boundaries (the file, the risk profile, the type). Consent requires seeing the specific person; depletion substitutes the class.

**Faithful (line, 1D)** shortens. Stress collapses the time-horizon: the worldline you can hold contracts toward the immediate, and commitments that require a long horizon cannot be maintained, not from bad faith but from a foreshortened window. Faithfulness is a temporal reach that scarcity amputates.

**True (center, 0D)** is G itself. Scarcity is low G by definition. This is the rung slack sits directly beneath.

**Agreement (whole)** is the most capacity-hungry of all, because mutual recognition is recursive: to co-hold a center I must model you modeling me, and resonance requires that each center have enough gain to actually be *moved* by the other. A depleted center cannot be moved; it can only drive (if it has power) or be driven (if it does not). Either way the joint mode collapses into forced oscillation, which the framework already names as the false whole.

### 5.2 Performed agreement is the low-slack attractor

That last result deserves its own statement, because it makes a moral category mechanical.

> Genuine agreement (resonance, a joint in-phase mode built by mutual recognition) is metabolically expensive. Performed agreement (forced oscillation, one center driving, the rest complying) is cheap. Under scarcity a system settles into the cheap equilibrium.

Tyranny is therefore not only a moral failure; it is the thermodynamically favored state when slack is low. A false whole is what a true whole decays into when its parts are depleted below the point where they can be moved. This upgrades the framework's forced-oscillation claim from a description of counterfeit unity to a prediction: destroy slack and you will get performed agreement, reliably, from people of ordinary good will. Compliance is what resonance looks like when no one can afford to resonate.

### 5.3 Slack distribution is centerhood distribution

The framework's anti-tyranny claim (claim 11) says a whole is ethical only when its parts can remain centered within it. Slack gives "remain centered" a concrete criterion.

> To remain a center is to stay above the exploratory-slack threshold: the level of headroom at which a part can still perceive, revise, and be moved. Below it, a part is perceived-only, a file that cannot itself perceive back. It has been reduced from a center to an object without anyone deciding to do so.

So the concrete content of claim 11 is a distribution rule:

> A false whole concentrates slack: a few centers, many objects. A true whole distributes slack so that every part clears the exploratory threshold. Slack inequality is centerhood inequality.

This is claim 12's "a good society is one where the whole strengthens the wholeness of its parts" made mechanical. The primary thing a whole owes its parts, the operational meaning of strengthening their wholeness, is enough slack to be a center. A whole that eats its parts' slack does not merely harm them; it forecloses their virtue, converting them into confirmatory, projecting, need-blind agents who then run confirmatory attention on one another, at which point the injustice self-seals because frozen models manufacture the evidence that freezes them. Exploitation is doubly corrosive: it depletes the part and disables the part's capacity to see, which is the very capacity the whole needs to stay honest.

### 5.4 Reciprocity is slack-flow balance

The framework treats reciprocity (β = give / (give + receive) ≈ 0.5) as the condition under which resonance stays stable. Slack says what is being balanced. Part of what flows between centers is headroom: attention given, load absorbed, error-correction supplied. An extractive relationship is a one-way slack transfer, one center's reserve consumed to fund another's, which is exactly the forced oscillation of a false whole seen as an energy budget rather than a phase relation. β ≈ 0.5 is the balance point at which neither center is drained below the exploratory threshold. This ties the ethics of reciprocity to the thermodynamics of sharing: balanced slack-flow sustains the joint mode; one-way drain breaks it.

### 5.5 The blindness of concentrated slack

An objection: if those with more slack see more truly, does this not license an epistemic aristocracy, the leisured class as the seers of truth? It does not, and the reason sharpens the critique.

Concentrated slack does not produce a class that sees truly. It produces a class that sees *itself* truly and everyone below it confirmatorily. The powerful have gain, but they point it inward and at their peers, and they run maximally confirmatory attention on the depleted, who appear to them only as low-resolution files, precisely because the depleted lack the standing to force a revision (the status-inverted epistemic access of the track-and-room case: the persons with the most person-level evidence had no input channel; the persons with the least held revision authority). Slack-hoarding therefore yields a characteristic blindness of power, not an aristocracy of insight. The administration that could not see the child was not short on slack; it had reorganized its slack away from the child and toward the model. Concentration produces sight for the few and a specific, motivated blindness toward the many.

### 5.6 Where Part II strains

**Slack owns only the depleted mode.** This is the essential scoping limit. The confirmatory-curiosity paper separates three deficits: charity, effort, and faith. Slack is the *effort* axis. It is necessary-not-sufficient, and the other two run at full slack: prosecutorial attention (charity deficit) is often highly effortful and intensely engaged, and archival attention (faith deficit) can be perfectly rested. The well-rested cruelty is real and slack will not touch it. So the political economy of slack strictly governs the depleted mode (P3b, and the load-path of resentment's occlusion in P6). It does not govern prosecutorial or archival attention, nor the motivated custody of P3c, which yield only to charity practice, faith repair, and ledger-closing respectively. Overclaiming slack as the master key would wrongly absorb charity and faith; the thesis is deliberately narrower, and stronger for it.

**Slack is optimized, not maximized.** Infinite slack removes the pressure to differentiate, and the framework holds that the capacity for love is potential requiring cultivation, which needs some load. Too little slack is confirmatory collapse; too much is a system with no forcing function. The ethical failure is scarcity *below the exploratory threshold*, not the absence of comfort. This hands the apoptosis clause of claim 12 a mechanism: legitimate cost is asking a whole-and-recoverable part to spend slack it can regenerate; exploitation is driving a part below the threshold where it can still see and recover. The framework's existing test ("can all involved still function and grow after?") now has teeth, because functioning and growing are exactly what fall off a cliff when slack drops under the line that funds exploratory attention. The threshold between cost and exploitation *is* the slack line.

**Slack is under-measured.** The word is doing real work and is not yet operationalized. Free-energy budget, cognitive load, attentional reserve, and metabolic headroom are related but not identical, and until the construct is pinned to a measure (exploration fraction under load, revision rate, recovery time) it risks becoming a comfortable name for "resources." It is admitted here as a construct-in-progress under the same discipline the framework imposes on resonance: technical or nothing.

---

# Part III. The seam

## 6. A and B are one dial

The two contributions are the same quantity read at two scales.

> Slack is the evidence-precision budget π_e, read at the scale of a life rather than a moment.

Part II is Part I applied to the act of ethical perception itself. Load lowers π_e, which lowers G on your seeing, which is why the descending check of the five values cannot even begin: you cannot weigh the field, the boundary, the worldline, or the center against reality when the world is not being given enough gain to correct you. The whole ethics runs on the same dial as truth and lying. Keep G high and you see reality, tell the truth at the resolution the receiver can take, and see other people as centers. Let π_m win, whether from fatigue (Part II) or from motive or because someone lied you into it (Part I), and all three fail together, in the same motion, for the same reason.

The fusion runs both ways. Section 3.7 showed that honest transmission itself requires exploratory curiosity about the receiver, so the confirmatory-or-exploratory stance is not only how a center takes reality in, it is how it gives reality out. One stance governs both directions of the channel: reception and transmission, seeing and saying.

This is why the framework's deepest instruction and its politics are one instruction. "Do not lie inward or outward" and "a true whole keeps its parts centered" are both the demand to keep the gain high: in yourself, toward others, and in the conditions a whole sets for its parts. Truth is a property of a channel. Ethics is the maintenance of that channel across relation, time, and scale. Slack is what the maintenance costs.

---

# Part IV. The truth-duty scales with slack

## 7. Who owns the misleading

Part I's responsibility boundary and Part II's slack thesis collide, and the collision is not a flaw; it is where the framework says something neither half could say alone.

The boundary (3.7): you own the implicatures a *competent cooperative interpreter* would draw, not the receiver's own confirmatory distortions. The slack thesis (Part II): interpretive competence is itself slack-bound. Under load a receiver's π_e falls, they run confirmatory, they miss or over-read implicatures. So "competent cooperative interpreter" is not a fixed standard; it is a slack-dependent capacity, and a depleted receiver is a degraded interpreter. The boundary was defined against a constant that Part II shows is a variable.

**The loophole this opens.** If competence is idealized, you can mislead by pitching to a competence the receiver does not have. Every marginal true, the disclosure "complete," and yet the actual receiver reliably ends with a false model, because decoding it required a slack they lacked. This is misleading laundered through the competence standard: the fine print that was technically sufficient for a rested expert and useless to the exhausted person in front of you. The "it was all disclosed" defense is this loophole worn as a virtue.

**The closure: index competence to the actual receiver, then route the residue by who caused the depletion.** The competence standard for non-misleading is the receiver's *actual* interpretive capacity as far as you can read it, not an idealized one. This is not a new demand; it is TRP's original one returning with force, because TRP already held that you cannot find the right resolution "without attending to where the other person actually is." The idealized interpreter was a placeholder, and the slack thesis forces it back into the read standard: transmit at the resolution *this* receiver can actually incorporate. The residual responsibility for any competence shortfall then tracks its cause. Three cases:

1. **Exogenous depletion** (grief, illness, poverty, load you did not create). You did not cause it, but you encounter it, and the duty is indexed to the actual receiver: if you can see they are depleted, pitching above their visible competence misleads even though a rested person would decode it. You owe accommodation.
2. **Self-inflicted distortion** (the receiver's own π_m inflated by a motive you did not induce and are not exploiting). Here the 3.7 boundary holds and the divergence is theirs: you spoke to their actual reachable competence and they refused to update for reasons internal to them.
3. **Engineered depletion** (you, or the whole you speak for, consumed the receiver's slack, then spoke at a resolution only an un-depleted interpreter could decode). This is the culpable case, and responsibility is doubled: Part II makes you answerable for foreclosing their competence, Part I for exploiting the competence you removed. You built the low-gain interpreter you then held to a high-gain standard.

**The strong form.** Put the three cases together and the boundary stops being a line and becomes a slope:

> Non-misleading is not a fixed duty. Its stringency scales inversely with the receiver's interpretive slack, and it concentrates on whoever controls that slack.

A rested peer is owed less accommodation, and the standard approaches the idealized interpreter. A depleted receiver is owed more: lower resolution, more declaration, more checking. And a whole that depletes its parts thereby *raises its own truth-duty toward them*, because it lowered their competence; it cannot deplete them and then hold them to the rested standard. Power over someone's attentional conditions is duty toward their comprehension. The party who can starve a receiver of slack inherits the burden of not misleading them, in proportion to that power.

This is where the framework's clinical work becomes a special case. The abuser who installs a fear and then speaks truths the fear predictably misreads is running case 3 through case 2: the distortion is proximately the victim's own π_m, but its cause is the abuser's, so its exploitation is the abuser's. Where the whole authored the prior, the whole authors the misreading. Manufactured consent, predatory disclosure, and the overwhelm-then-sign pattern are the same structure at institutional scale: deplete, disclose above the depleted receiver's competence, then point to the disclosure.

**Where Part IV strains.** Four limits.

First, causation of depletion is usually diffuse. Who starved this receiver of slack (this speaker, prior relationships, an economic order, their own choices) is rarely cleanly traceable, so the principle yields a gradient (more control over the receiver's slack means more duty) rather than a ledger with a verdict. It is directional, and honest only as a direction.

Second, it can slide into paternalism, the exact posture TRP was built to kill. Deciding a receiver is "too depleted for the truth" and feeding them a comfortable picture is the Noble Lie again. The guardrail is TRP's own: accommodation means *lowering resolution with declaration*, never substituting content. You simplify and you flag that you are simplifying; you never decide for them what they cannot handle and hand them a false marginal. The duty to accommodate the depleted is bounded by the duty not to patronize them.

Third, timing becomes an ethical variable, which lands on the Faithful rung. Sometimes the honest move is neither to transmit into a depleted state nor to withhold, but to *defer*: "this is a large decision and you are exhausted; I will not walk you through it tonight." Honest communication has a *when*, and pushing a heavy truth into a receiver with no slack to hold it can discharge your duty on paper while ensuring it fails in fact.

Fourth, the collision applies inward, by the symmetry that has run through the paper. Your own depleted state degrades you as an interpreter of the world and of others, so "do not lie inward" now includes: do not make large interpretive commitments while depleted, because your low-slack self is a degraded reader you should not fully trust. Defer the reading, not only the telling.

---

## 8. Strongest form

The system stated at full strength, each claim in its sharpest line.

**1. One quantity governs truth, lying, and seeing.** The update gain G = π_e / (π_e + π_m) is the fraction of the model-world gap the world is allowed to close.
> *Truth, lying, and confirmatory curiosity are three settings of one dial.*

**2. Lying and confirmatory curiosity are mirror operations.** One forces another's model-precision up from outside; the other lets your own run away from inside.
> *To lie outward and to lie inward are the same corruption, aimed in opposite directions on one channel.*

**3. Truth is marginalization consistency.** A true claim at any grain is the correct marginal of reality at that grain, and true marginals never require retraction under refinement.
> *Partial truth and lie are not on one axis because a partial truth is a marginal of the truth and a lie is not.*

**4. The honest exit always exists.** The coarsest grain (the maximum-entropy transmission, "I will not tell you") is a true section for any reality, because it asserts nearly nothing.
> *You never have to lie because the top of the resolution lattice is always there.*

**5. TRP is a constrained optimization with a nonempty feasible set.** Maximize resolution subject to truth and receiver-uptake; the max-entropy floor keeps the feasible set nonempty.
> *Honesty is always solvable; only its resolution is in question.*

**6. Truth needs gain on both ends.** A true signal fails on a receiver whose precision is inflated; comfortable lies are believed for the same reason true things are refused.
> *Propaganda is precision-corruption aimed at the already-depleted.*

**7. Honesty is non-misleading, not merely non-lying.** True marginals can still be arranged to move a cooperative receiver away from reality; ruling that out requires modelling where your words will land, which turns the outbound protocol into an act of exploratory curiosity.
> *You are answerable for what a reasonable hearer will infer, not only for what you assert.*

**8. Slack is the zeroth precondition.** Every value presupposes a channel with enough evidence-precision to see; slack is the funding of that seeing, beneath True.
> *Before a center can be true, it must be able to afford to look.*

**9. Scarcity has a signature on every rung.** Right fails first, Good defaults to category, Faithful foreshortens, True goes to low gain, Agreement collapses into forced oscillation.
> *Performed agreement is the thermodynamically favored state when slack is low.*

**10. Slack distribution is centerhood distribution.** To remain a center is to stay above the exploratory-slack threshold; below it a part is perceived-only.
> *A false whole concentrates slack; a true whole distributes enough that every part can be a center.*

**11. Concentrated slack blinds rather than ennobles.** The slack-rich see themselves truly and the slack-poor confirmatorily.
> *Slack-hoarding produces the characteristic blindness of power, not an aristocracy of insight.*

**12. The two theses are one.** Slack is π_e at life-scale; the politics of attention and the ethics of truth are the same maintenance of one channel.
> *Ethics is keeping the gain high, in yourself, toward others, and in the conditions a whole sets for its parts.*

**13. The truth-duty scales with slack.** Interpretive competence is itself slack-bound, so non-misleading is indexed to the receiver's actual capacity, and the burden concentrates on whoever controls that capacity.
> *Power over another's attention is duty toward their comprehension; deplete a hearer and you inherit the burden of not misleading them.*

**14. The scope is honest.** Slack governs the depleted mode only; charity and faith deficits run at full rest and need their own repairs; the phenomenal edge is untouched.
> *One dial explains the epistemics of wholeness and leaves the hard problem exactly where it was.*

---

## 9. Summary table

| Phenomenon | Setting of the dial | Circumpunct reading |
|------------|--------------------|---------------------|
| Clear perception | G high on own channel | Center sees; True is funded |
| Confirmatory curiosity (load) | π_e low | Depleted mode; P3b |
| Confirmatory curiosity (motive) | π_m inflated by preference | Self-deception; P3c |
| Truthful transmission | raises receiver G | Helping a part touch the Whole |
| Lie | installs high-precision false prior | Severs another's dot-circle link |
| Misleading | all true marginals, receiver's inferred posterior diverges | Lying outsourced to the receiver's own inference |
| Engineered misleading | deplete the receiver, then disclose above their competence | Doubled culpability; the slack-holder owns the truth-duty |
| TRP resolution | choose grain r; assert only true marginals | Appropriate-level truth |
| Full honesty (TRP+) | true marginals and receiver's posterior converges | No lie and no mislead |
| Max-entropy floor (declared) | r = top of lattice, implicature cancelled | The declared door that is always there |
| Slack | π_e budget at life-scale | Zeroth precondition beneath True |
| False whole | forced oscillation under low slack | Concentrated slack; parts made objects |
| True whole | resonance sustained by balanced slack-flow | Distributed slack; parts kept centers |

---

## Coda

> Truth is a property of a channel, not a possession of a speaker. To be honest is to keep the gain high enough that reality can correct you and that your word can help reality correct someone else. To be just is to keep that gain affordable for every part of every whole you belong to. The lie, the self-deception, and the tyranny are one failure at three scales: a prior defended past the point where the world was still allowed to speak.
