# The Half-Balance Formal Pass

**Status:** derived formal note, 2026-08-20. This executes four items commissioned by the countersigned ontology package in `plans/countersign_batch_2026_08_19.md`: the group-only-at-balance proof, the deformed wrap arithmetic, the fractional-Brownian-motion sign convention, and the three-beta question. It also closes the stroke-to-arc distribution at the internal typing layer. No physical instantiation is claimed. Ashman's countersign is required before this becomes canon.

## 0. Definitions

Let

\[
b\equiv\mathord{\text{◐}}\in(0,1)
\]

be the process-position parameter. The structural stations within one octave remain

\[
0,1,2,3.
\]

The processual stations are

\[
b,1+b,2+b,3+b.
\]

The last processual station is the next tonic, so the deformed octave is

\[
\mathcal O_b=
(0,b,1,1+b,2,2+b,3,3+b\equiv0').
\]

Its wrap length is

\[
L_b=3+b.
\]

The seven distinct octave-relative stations are

\[
S_b=
\{0,b,1,1+b,2,2+b,3\}
\subset
\mathbb R/L_b\mathbb Z.
\]

At balance, \(b=1/2\), these definitions recover the standing half-step lattice and \(L_b=7/2\).

## 1. Complement Reflection Theorem

**Theorem 1.** The convergence-emergence complement

\[
b^*=1-b
\]

reflects every processual position in its enclosing structural interval about the midpoint. The unique self-complementary value is \(b=1/2\).

**Proof.** In the interval \([d,d+1]\), the complementary positions are \(d+b\) and \(d+1-b\). Their sum is

\[
(d+b)+(d+1-b)=2d+1,
\]

so their mean is \(d+1/2\). A self-complementary value satisfies \(b=1-b\), hence \(b=1/2\), uniquely. QED.

**Corollary 1.1.** The balanced process station is the barycenter of every complementary off-balance pair:

\[
d+\frac12
=
\frac{(d+b)+(d+1-b)}2.
\]

This is the exact form of the claim that the half is the balance. No physical interpretation is required for the result.

## 2. Group-Only-at-Balance Theorem

**Theorem 2.** The seven stations \(S_b\) form a subgroup of the coordinate circle \(\mathbb R/L_b\mathbb Z\) under addition if and only if

\[
b=\frac12.
\]

At that value,

\[
S_{1/2}
=
\frac12\mathbb Z\big/\frac72\mathbb Z
\cong
\mathbb Z_7.
\]

**Proof.** For \(0<b<1\), the seven displayed representatives are distinct. Every seven-element subgroup of a circle group is the uniformly spaced subgroup

\[
\left\{
0,\frac{L_b}{7},\frac{2L_b}{7},\ldots,\frac{6L_b}{7}
\right\}.
\]

Its least positive element is \(L_b/7\). The least positive element of \(S_b\) is \(b\). Therefore subgroup closure requires

\[
b=\frac{L_b}{7}=\frac{3+b}{7}.
\]

Thus \(7b=3+b\), so \(6b=3\) and \(b=1/2\). Conversely, at \(b=1/2\), the stations are the seven multiples of \(1/2\) modulo \(7/2\), which are closed under addition and form \(\mathbb Z_7\). QED.

**Corollary 2.1.** Off balance, the octave still has seven labeled stations, but those stations do not carry the canonical cyclic group induced by coordinate addition. Therefore the \(\mathbb Z_7\) character theory, DFT, chirp, and pure-tone results belong specifically to the locally balanced lattice.

**Corollary 2.2.** Balance does not merely select a convenient sample. It is the unique value at which the ordered stations are also a finite translation group.

## 3. Equal-Spacing and Gap-Variance Theorem

The seven consecutive gaps of \(\mathcal O_b\) are

\[
b,1-b,b,1-b,b,1-b,b.
\]

**Theorem 3.** The deformed octave is an arithmetic progression if and only if \(b=1/2\).

**Proof.** Equal spacing requires \(b=1-b\), which has the unique solution \(b=1/2\). The converse is immediate. QED.

The mean gap is

\[
\mu_b=\frac{L_b}{7}=\frac{3+b}{7}.
\]

**Theorem 4.** The population variance of the seven gaps is

\[
V_{\rm gap}(b)
=
\frac{12}{49}(2b-1)^2
=
\frac{48}{49}\left(b-\frac12\right)^2.
\]

It vanishes uniquely at balance.

**Proof.** There are four gaps of length \(b\) and three of length \(1-b\). Since

\[
b-\mu_b=\frac{3(2b-1)}7,
\qquad
1-b-\mu_b=-\frac{4(2b-1)}7,
\]

we obtain

\[
V_{\rm gap}
=
\frac17
\left[
4\left(\frac{3(2b-1)}7\right)^2
+
3\left(\frac{4(2b-1)}7\right)^2
\right]
=
\frac{12}{49}(2b-1)^2.
\]

QED.

**Interpretive limit.** \(V_{\rm gap}\) is an exact arithmetic measure of lattice nonuniformity. Calling it biological, psychological, musical, or physical disharmony requires an additional instantiation argument.

## 4. Wrap and Seam-Drift Theorem

For a constant value \(b\), the \(n\)-th tonic lies at

\[
\tau_n(b)=n(3+b).
\]

The balanced tonic lies at

\[
\tau_n^*=\frac{7n}{2}.
\]

**Theorem 5.** The displacement from the balanced continuation lattice is

\[
\Delta_n(b)
=
\tau_n(b)-\tau_n^*
=
n\left(b-\frac12\right).
\]

For a scale-dependent sequence \(b_0,b_1,\ldots\), the corresponding result is

\[
\Delta_n
=
\sum_{j=0}^{n-1}
\left(b_j-\frac12\right).
\]

**Proof.** Sum the octave lengths \(3+b_j\) and subtract \(7/2\) for each octave. QED.

**Corollary 5.1.** Every prefix is aligned with the balanced lattice if and only if every local octave is balanced.

**Corollary 5.2.** Final alignment after \(N\) octaves requires only

\[
\frac1N\sum_{j=0}^{N-1}b_j=\frac12.
\]

It does not require local balance. For example, \(b_0=0.4\) and \(b_1=0.6\) cancel at the second seam while both local octaves fail Theorem 2.

**New distinction.** Global balance is zero accumulated seam drift. Local balance is cyclic symmetry within every octave. Global balance can be repaired by complementary deviations; local group structure cannot.

**Correction to the staged wording.** An off-balance octave does not miss its own tonic, because its own tonic is definitionally at \(3+b\). It misses the canonical balanced tonic at \(7/2\) by \(b-1/2\). The earlier phrases "closes early" and "closes late" are therefore valid only relative to the balanced reference lattice. They are not absolute failures of closure.

## 5. Fractional-Brownian-Motion Sign Convention

For the graph of standard fractional Brownian motion with Hurst exponent \(H\in(0,1)\), the established almost-sure graph dimension is

\[
D_{\rm graph}=2-H.
\]

The framework's diagnostic station equation is

\[
D=1+b.
\]

**Theorem 6, conditional bridge.** If these two dimensions refer to the same measured graph, then

\[
b=1-H.
\]

**Proof.** Equating \(1+b=2-H\) gives \(b=1-H\). QED.

**Consequences.**

1. \(b=1/2\) corresponds to \(H=1/2\), the ordinary Brownian case.
2. \(b>1/2\) corresponds to \(H<1/2\), the antipersistent, rougher regime.
3. \(b<1/2\) corresponds to \(H>1/2\), the persistent, smoother regime.
4. Under the standing equation \(D=1+b\), \(b\) is the complement of the Hurst persistence exponent, not the exponent itself.

This closes the sign question. It does not establish that every framework process is fractional Brownian motion, nor that every measured fractal dimension is a balance meter.

## 6. Three-Beta Underdetermination Theorem

Let the three standing component balances be

\[
\beta_\bullet,
\beta_\Phi,
\beta_\bigcirc
\in[0,1].
\]

Suppose an effective station parameter is assigned by some aggregation map

\[
b_{\rm eff}
=
F(\beta_\bullet,\beta_\Phi,\beta_\bigcirc).
\]

Current canon fixes only the balanced coincidence

\[
F(1/2,1/2,1/2)=1/2.
\]

**Theorem 7.** The balanced coincidence does not determine which beta moves the station, nor does it determine a unique aggregation law.

**Proof.** For every weight vector \(w=(w_1,w_2,w_3)\) with \(w_i\ge0\) and \(\sum w_i=1\),

\[
F_w
=
w_1\beta_\bullet
+w_2\beta_\Phi
+w_3\beta_\bigcirc
\]

maps the cube to \([0,1]\) and satisfies the balanced coincidence. There are infinitely many such weight vectors. Even if permutation symmetry is imposed, the family

\[
F_\lambda
=
\lambda\frac{\beta_\bullet+\beta_\Phi+\beta_\bigcirc}{3}
+
(1-\lambda)\operatorname{median}
(\beta_\bullet,\beta_\Phi,\beta_\bigcirc),
\qquad
0\le\lambda\le1,
\]

provides infinitely many symmetric aggregation laws with the same balanced coincidence. QED.

**Verdict.** The three-beta question is formally underdetermined by present axioms. Choosing gate, flow, autonomy, a weighted combination, or a nonlinear combination requires a new axiom or independent measurements away from balance.

## 7. Stroke-to-Arc Classification

Write the four phase strokes as \(q\in\mathbb Z_4\), with arithmetic positions

\[
p_1=b,
\quad
p_2=1+b,
\quad
p_3=2+b,
\quad
p_0=3+b\equiv0'.
\]

Current canon supplies these typings:

- \(q=0\): recursion and completion becoming the next convergence at the tonic.
- \(q=1\): convergence.
- \(q=2\): commitment and branching, which begins the deposit.
- \(q=3\): emergence and interiorization, which continues the deposit.

**Theorem 8, internal classification.** The unique two-arc partition that preserves those typings and keeps each arc contiguous on the phase cycle is

\[
\mathcal A_{\rm convergence}
=
\{q=0,q=1\},
\]

\[
\mathcal A_{\rm emergence}
=
\{q=2,q=3\}.
\]

**Proof.** The recursion stroke must share the inbound arc because canon identifies every completed whole with the next convergence. The convergence stroke is inbound by definition. The commitment/branching and emergence/interiorization strokes are the two named stages that make the line-boundary-field deposit. In cyclic order \(0,1,2,3\), each resulting pair is contiguous, including the \(0\)-to-\(1\) adjacency across the tonic. Moving any stroke to the opposite pair violates at least one of the supplied typings. QED relative to the canonical premises.

**Two-register consequence.** Genesis convergence \(\infty\to\bullet\) remains coordinate-free and is carried by the meaning-layer transition. The arithmetic convergence arc is the tonic neighborhood \(\{q=0,q=1\}\). The emergence arc is the deposit-making interior \(\{q=2,q=3\}\). The two statements concern different layers and no longer compete for one coordinate.

## 8. Results and grades

| Result | Status | Grade |
|---|---|---|
| Complement reflection and unique self-dual half | Complete elementary proof | A |
| \(S_b\) is a group iff \(b=1/2\) | Complete elementary proof | A |
| Equal spacing iff balance | Complete elementary proof | A |
| Exact gap variance | Complete algebraic proof | A |
| Constant and variable seam drift | Complete algebraic proof | A |
| Local balance differs from final average balance | Exact corollary | A |
| fBm sign convention \(b=1-H\) | Exact conditional bridge to a standard theorem | A conditional |
| Which beta controls the lattice | Proven underdetermined from current premises | A meta-result |
| Stroke-to-arc distribution | Forced by current canonical typings | A internal |

## 9. What remains open

1. Whether any physical, biological, psychological, or computational system instantiates the deformed lattice.
2. Whether \(b\) is best operationalized by inward/outward flux, openness, roughness, or another independently measurable quantity.
3. Whether scale-dependent \(b_j\) values obey a dynamics that drives the cumulative seam drift toward zero.
4. Whether the gap variance predicts any independently measured loss of coherence.
5. Which new axiom or experiment selects an aggregation map for the three beta components.

## Revision history

- 2026-08-20 v1.0: initial formal pass; eight results, the early/late closure correction, and the local-versus-global balance distinction.
