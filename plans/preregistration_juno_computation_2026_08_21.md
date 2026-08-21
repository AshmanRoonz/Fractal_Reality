# Pre-Registered Computation: The JUNO Pair

**Status: computation record under the binding protocol of `plans/preregistration_targets_2026_08_21.md`. Part I (this commit) freezes the rules, the targets, the candidate space, and the decision procedure BEFORE any search runs; Part II (a separate later commit) carries the search and its outcome. The git history is the timestamp separating the two. Drafted by Claude, executing Ashman's pick of 2026-08-21; the outcome, whatever it is, will be reported under clauses 5 through 7 (no revision, no silent drops, null is an outcome).**

---

## Part I: rules first (frozen before the search)

### 1. The pick, registered

Ashman picked, by structured answer on 2026-08-21: **the JUNO pair**, meaning the two dimensionless quantities

- **Target 1: sin²θ₁₂**, the solar mixing parameter, as measured by JUNO.
- **Target 2: Δm²₂₁ / |Δm²₃₁|**, the neutrino mass-square ratio, dimensionless, from JUNO's Δm²₂₁ and the global |Δm²₃₁|.

Jointly adjudicated: both outcomes are reported; the headline claim requires both to survive; partial outcomes are reported as partial. In the same structured answer Ashman commissioned the Λ-constancy audit (separate record) and folded the α band restatement into this record (§7 below).

### 2. Blindness status and disclosures

- **Corpus cleanliness** (established by grep across all eras before this record was drafted; receipts in the staging record's addendum): sin²θ₁₂ has no expression anywhere in the corpus, any era. The mass-square ratio has none in the current grammar; the eml program searched it at depths ≤ 4 and returned null both times (disclosed prior nulls in a non-primary family; nothing to steer toward).
- **Sector archaeology**: an archived braid-era table carries θ₁₃ and V_us entries; eml-era candidates for θ₂₃/θ₁₃/δ_CP exist and are downgraded by the corpus's own §27.7n caveat. None touches the picked targets.
- **Contamination disclosure (Claude, required by this record's own discipline):** while drafting filter B of §6 below, and after the station argument for it was already fixed, Claude mentally noted that a Cabibbo-family base α^◐ for sin θ₁₂ implies a pre-correction prefactor of order six. That fragment is disclosed rather than hidden. It selected nothing: no pool decomposition of any prefactor was examined, and the enumeration of §6 is exhaustive within its pre-stated caps, so the candidate set cannot be steered by an in-head fragment; the only thing it could have biased is the filter ordering, which was fixed by the §27.7p flavor-mixing precedent before the fragment occurred. No other grammar-side computation for either target has been performed by anyone, anywhere in the corpus or this session, as of this commit.

### 3. The rules, quoted verbatim (per protocol clause 2)

**The form rule** (framework §27.7p, "Falsifiable prediction," quoted):

> "Every dimensionless coupling in physics, discovered or yet-to-be-discovered, must decompose as α^k · (framework prefactor) · (1 + α · framework ratio), where k is an integer or rational number assembled from the ladder-position pool {T, R, P, G, V, SU(3), Φ, ○} (or sums/differences/products of these). The α-exponent is diagnostic of which ⊂ relation the coupling encodes; the prefactor is diagnostic of the station shared (or not) between part and whole; the α-correction is diagnostic of the channel structure at the coupling's station. A newly measured coupling that cannot be fit into this decomposition within measurement precision would falsify §27.7p."

**The address precedent** (framework §27.7p table, row for flavor mixing, quoted): "Cabibbo | flavor mixing | 0.5D | 2.5D | 1 (half-rung base) | α^(½ + αT/R) · SU(3)/T; §27.7h". And §27.7q names the empty κ-matrix cells, with "neutrino mixing angles" listed among the measurements that "either fill the remaining cells consistently or break the architecture. The matrix is not a postdiction device; it is the framework's main channel of falsification for the next decade of precision physics."

**The pool** (CLAUDE.md canonical, §27.7b, quoted): "Every structural number on the ladder derives from T = 3 ... R = T² - 2 = 7 (rungs). G = T(T+1) = 12 (generators). G+1 = 1 + T + T² = 13 ... S = (T+1)^T = 64 (states). SU(3) gen = T² - 1 = 8. P = T + 1 = 4 (pump phases). K_gen = T^(n+T-1) (corrections)." Plus the glyph-integer rule (binding): "in every constants formula, Φ denotes the integer 2 and ○ denotes the integer 3." Plus the traversal functions (§27.7j): A(d) = d(2d+1) giving 0, 1, 3, 6, 10, 15, 21, 28 at the stations, and A'(d) = 4d + 1 giving 1, 3, 5, 7, 9, 11, 13, 15.

**The selection rule** (CLAUDE.md canonical, §27.7j, quoted): "The accumulated traversal function A(d) = d(2d+1) IS the selection rule; the framework does not choose exponents, the ladder computes them ... Elementary particles use A' (derivative; point-like), composites use A (function; accumulated) ... Corrections: first-order = closure count at home scale, second-order = process count, ratio = dimensional balance."

**The null-bar caveat** (CLAUDE.md canonical, §27.7n, quoted, binding on this search): "blind symbolic regression over eml/pump-gate trees at typical depths overfits. Size-3 search over the rich framework basis produces a null-target median error near 0.05%; only hits that beat a matched-magnitude null by roughly 3x count as signal. Flavor-physics constants at size 3 do not reliably pass this bar."

**Precedent formula families** (the corpus's published mixing/fraction forms, which define the candidate families below): Weinberg: sin²θ_W = SU(2)/V + (Φ+○)α/T⁴ = 3/13 + 5α/81. Cabibbo: sin θ_C = α^(1/2 + α·T/R) · SU(3)/T. Budget style: DE = T²/V = 9/13 (pure structural fraction, no α).

### 4. Targets and acceptance bands

Experiment-side inputs (quoted from the staging record's verified sources):

- JUNO (Nature, 2026-06-11, 59 days): **sin²θ₁₂ = 0.3092 ± 0.0087** (2.8%); **Δm²₂₁ = (7.50 ± 0.12) × 10⁻⁵ eV²** (1.6%).
- NuFIT 6.0 (2024, normal ordering): sin²θ₁₂ = 0.307 +0.012/−0.011 (consistent with JUNO); **|Δm²₃₁| = (2.534 +0.025/−0.023) × 10⁻³ eV²** (symmetrized ±0.024 for the band arithmetic).

**Acceptance** (protocol clause 3): a candidate expression counts as "the grammar speaks" only if it lands inside the 1σ band of the current values: for Target 1, inside 0.3092 ± 0.0087; for Target 2, inside the ratio band computed in the script from the quoted inputs (central value 7.50 × 10⁻⁵ / 2.534 × 10⁻³ with uncertainties combined in quadrature; the script prints the band and this record's Part II quotes it).

**Adjudication**: future JUNO reactor-channel releases bind (pinned now, per the staging record's watch item on the solar-vs-reactor tension). JUNO design reach is a few tenths of a percent on all three underlying quantities over about six years. Normal ordering is assumed for |Δm²₃₁| (NuFIT 6.0 preference and JUNO's own reporting); if inverted ordering is established, an addendum re-pins the target's definition before comparing.

**Kill semantics** (protocol clause 4): a pre-registered value is **dead** when a future JUNO (or successor global) determination excludes it at more than 3σ of that future measurement; **in tension** (reported, not dead) between 2σ and 3σ; **standing** inside 2σ. A pre-registered SET (see §6, verdict rules) is dead when every member is dead.

### 5. The candidate space (frozen; no vocabulary added mid-search)

**Atom list** (the named integers of the current grammar, from CLAUDE.md's constants entries; frozen):

1 (•), 2 (Φ), 3 (T = ○), 4 (P), 5 (Φ+○), 6 (T!), 7 (R), 8 (SU(3)), 9 (T²), 10 (A(2)), 11 (A'(2.5)), 12 (G), 13 (V), 15 (A(2.5)), 16 (P²), 20 (P(P+1)), 21 (A(3)), 24 (P!), 27 (T³), 28 (A(3.5)), 32 (2P²), 35 (C(R,T)), 39 (T·V), 56 (SU(3)·R), 58 (ΣA+2), 59 (P·V+R), 64 (S), 72 (SU(3)·T²), 81 (T⁴), 84 (G·R), 91 (R·V), 126 (C(9,4)), 169 (V²), 247 (V(P²+T)).

Irrational carriers: α (CODATA 2022, 1/α = 137.035999177) and φ (golden ratio), exactly as the current grammar's formulas use them. π is excluded: no current-grammar constants formula uses a bare π (the braid-era stratum did; it is archived).

**Families** (each candidate must instantiate the §27.7p decomposition):

- **F1 (Weinberg family, for sin² form):** value = p/q + n·α/K, with p/q a Tier 1 fraction (below), n an atom ≤ 13, K an atom, and the base p/q required to sit within 2% of target before correction (the Weinberg precedent's own shape: base within 2%, correction well under 1%). The no-correction case n = 0 is included (and is then also F3).
- **F2 (Cabibbo family, for sin form):** sin θ = α^(◐ + c·α) · (p/q), with ◐ = 1/2 fixed as the base exponent (the precedent's "balanced aperture state for a mixing angle"), c ∈ {0} ∪ {atom/atom ratios with value ≤ 13}, and p/q a Tier 1 fraction. Evaluated against the target as (sin θ)² for Target 1. For Target 2 (not an angle), F2 is evaluated directly as a value form α^(◐ + cα)·(p/q) with the same caps, since the §27.7p form does not restrict k = ◐ to angles.
- **F3 (budget family, pure fraction):** value = p/q, Tier 1.

**Tier 1 fraction** = (single atom) / (single atom). This matches the corpus's own uniqueness-claim practice (3/13, 9/13, 8/3, 7/9, 13/20, 64/247 are all single-atom over single-atom on this list). A Tier 2 sensitivity sweep (products of ≤ 2 atoms over products of ≤ 2 atoms) is computed and reported for the multiplicity picture only; Tier 2 hits cannot be pre-registered (pre-stated now: the corpus has no Tier 2 precedent for a base fraction).

**Null calibration** (binding, per §27.7n): for each family and each target, the same enumeration is run against 2,000 random windows of the same relative width, placed uniformly over a magnitude-matched range (sin²θ₁₂: [0.15, 0.50]; the ratio: [0.010, 0.090]). Reported: the actual in-band count, the null median and the null 90th percentile of in-band counts. A family's result at a target counts as signal only if its in-band count is at or below the null median (i.e., the window is not unusually crowded) AND the filtered survivor count (below) is 1, or if the survivor set is small (≤ 5) and beats the null by the 3x standard of §27.7n applied to filtered survivors.

### 6. The decision procedure (frozen)

Applied per target, in this order, to the union of in-band candidates from F1, F2, F3:

- **Filter A (form):** the candidate must instantiate §27.7p's decomposition with every constant pool-native. (Guaranteed by construction; stated for completeness.)
- **Filter B (address):** Target 1 is inter-generation flavor mixing (lepton generations 1 and 2), which is the Cabibbo analogue, not the Weinberg analogue (θ_W mixes gauge groups, not generations). The §27.7p table's flavor-mixing row is the precedented address. Therefore F2 candidates outrank F1/F3 candidates for Target 1; an F1/F3 candidate can win only if F2 is empty in band. Target 2 is a ratio of spectral splittings, not a mixing amplitude; the corpus has no direct address precedent for it (mass ratios at 1.5D use exponential forms that cannot reach a value of this magnitude with pool exponents; stated in advance), so for Target 2 the three families compete on equal footing and multiplicity risk is higher; this asymmetry is pre-declared.
- **Filter C (economy):** among survivors, fewest distinct pool objects wins; exact ties are reported as ties.

**Verdict rules** (frozen): exactly one survivor: that is the pre-registered value. Two to five survivors: the pre-registered SET (a weaker, explicitly graded claim: the sharpened measurement must land on a member). More than five survivors: null-by-multiplicity (the family space cannot claim this target; reported as such). Zero in band: null (clause 7). Every outcome is reported (clause 6).

### 7. Folded restatement: the α closed form vs CODATA 2026 (B1)

Already-published commitment, restated and dated here before the adjudicating data exists: the closed form **1/α = 360/φ² − 2/φ³ + α/(59/3) = 137.035999147** is frozen in `docs/alpha_derivation.html` with every factor pinned; its distance from CODATA 2022 (1/α = 137.035999177(21)) is 0.22 ppb, about 1.4σ of that adjustment. The CODATA 2026 adjustment (data cutoff 2026-12-31, publication early 2027) must digest the standing >5σ rubidium-vs-cesium interferometry discrepancy and the electron magnetic-moment route. **Proposed graded semantics, pending Ashman's countersign:** the auxiliary claim **survives** if the closed form lies within 3σ of the CODATA 2026 recommended value; **critical tension** (reported, with the discrepancy's treatment examined before any verdict, since CODATA's stated σ depends on how the discrepant inputs are weighted) between 3σ and 5σ; **dead** beyond 5σ. Either way the representation layer (α as measured input to κ_{0,0}) is untouched, per the corpus's separability clause.

**End of Part I. Nothing below this line exists at the Part I commit; the search script and its results follow in a separate commit, and the git hashes are the receipt that the rules preceded the search.**
