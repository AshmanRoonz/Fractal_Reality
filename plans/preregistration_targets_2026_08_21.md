# Pre-Registration Targets for the Blind-Prediction Test

**Status: staging record, 2026-08-21. Scouted and drafted by Claude on Ashman's commission ("Do it," 2026-08-21), executing the offers card's Tier 2 item 1 and its open decision 2 (`plans/what_it_offers_math_and_physics_2026_08_21.md`). The pick is Ashman's. Nothing in this record is a prediction; the grammar's value for any blind target is computed only after the pick, in a separate dated record. UPDATE, same date: the pick was made (the JUNO pair), the computation ran under the frozen protocol, and the outcomes were countersigned; see `plans/preregistration_juno_computation_2026_08_21.md` and `plans/countersign_batch_2026_08_21.md`.** Experimental facts below were verified by web search on 2026-08-21; sources are listed at the bottom; timeline claims are the experiments' own and inherit their slippage.

## What this record is

The offers card names one decisive test: choose a not-yet-measured or soon-to-be-remeasured quantity before looking; publish the grammar's value; let the measurement arrive. This record is the "before": a scouted menu of quantities that experiment will measure or sharpen on known clocks, staged so a target can be chosen while the grammar's answer for it does not yet exist. Git history is the timestamp for every step.

## The binding protocol (in force from this commit)

1. **Pick before looking.** A target is chosen from this menu (or added to it) before any grammar-side computation for that target exists, anywhere in the corpus or in session work.
2. **One dated computation record per pick.** After the pick, a dedicated session produces the grammar's value. That record must open by quoting, verbatim and before any search begins, the selection rules and the integer pool it will use (§27.7j's selection rule, the glyph-integer dictionary, the pool inventory from §27.7b). No vocabulary added mid-search.
3. **Acceptance vs adjudication.** For a quantity with a current public value, the computed expression must land within the current public uncertainty to count as "the grammar speaks." The future, sharpened measurement then adjudicates. For a quantity with no current value, the expression is stated with its tolerance and simply waits.
4. **Kill stated with the value.** The computation record states, alongside the value, exactly what future measured range falsifies it.
5. **No revision.** Once committed, the value does not move. Corrections of record errors happen by addendum with the original visible, per the corpus's no-silent-retraction law.
6. **No silent drops.** Every target that is ever picked gets its outcome reported in the ledger: hit, miss, or null. Pre-registering several targets and reporting only the hits would be the file-drawer effect wearing framework clothes.
7. **Null is an outcome.** "The vocabulary offers no expression for this quantity under its own rules" is a reportable result. It is evidence about the grammar's restrictiveness, and it is the honest alternative to stretching the pool until something fits.

## Contamination statement

This record carries experiment-side facts only: what will be measured, by whom, on what clock, at what precision. No grammar-side computation, candidate expression, or integer-combination reasoning was performed for any Class A target during this scouting, and none appears below. The only grammar content named here is Class B material already published in the corpus, cited as-is.

## Three blindness grades

- **Grade i, from nothing:** the quantity has no meaningful current value. The grammar's statement is a prediction in the fullest sense. Rarest and slowest.
- **Grade ii, sharpening survival:** the quantity has a public value at coarse precision and a large precision jump is scheduled. The grammar's expression is chosen knowing the coarse value; the blind content is surviving the jump. This is the corpus's existing fit-then-survive pattern made prospective, dated, and unrevisable.
- **Grade iii, band restatement:** the corpus already carries a formula and an accuracy band; the pre-registration is to restate the band and its kill semantics now, dated, before named incoming data adjudicates.

The grades are ordered by strength. A grade-ii hit is real but weaker than a grade-i hit; the record of which grade a result belongs to travels with it.

## Class A: blind targets (no corpus formula exists)

### A1. The JUNO solar pair: sin²θ₁₂ and the mass-square ratio (grade ii) [RECOMMENDED PRIMARY]

- **What:** the solar mixing parameter sin²θ₁₂ and the dimensionless mass-square ratio Δm²₂₁/|Δm²₃₁|. Both are dimensionless, which is the grammar's native register.
- **Current state (public):** JUNO began operation in August 2025 and published first results in Nature on 2026-06-11, from 59 days of data: sin²θ₁₂ = 0.3092 ± 0.0087 (2.8%) and Δm²₂₁ = (7.50 ± 0.12) × 10⁻⁵ eV² (1.6%), already 1.6× more precise than all previous experiments combined. |Δm²₃₁| is known at the percent level from the global program.
- **The clock:** JUNO's design reach over about six years is a few tenths of a percent on all three quantities (roughly 0.5% on sin²θ₁₂, 0.3% on Δm²₂₁, 0.2% on |Δm²₃₁|), with further releases expected on a one-to-two-year cadence. Every release narrows the remaining blind window; the value of picking now decays with each JUNO paper.
- **Test content:** an expression chosen at today's 2.8% must survive a roughly five-fold sharpening. Pre-registering the pair jointly (both reported, jointly adjudicated) guards against the one-number lucky hit.
- **Why recommended:** soonest adjudication, cleanest dimensionless form, no corpus formula anywhere, and a collaboration whose only job for the next five years is to shrink these error bars.
- **Watch item, not a target:** JUNO confirmed the mild solar-vs-reactor tension (about 1.5σ) in Δm²₂₁; if it grows, the "measured value" becomes two values, and the adjudication rule will need an addendum naming which channel binds.

### A2. δ_CP, the leptonic CP phase (grade i, the long game)

- **What:** the CP-violating phase of the lepton mixing matrix. Essentially unmeasured: current T2K and NOvA data give broad, ordering-dependent hints only.
- **The clock:** Hyper-Kamiokande begins data-taking around 2028; a slimmed DUNE around 2029; discovery-level statements arrive in the 2030s (Hyper-K's most favorable scenario claims CP-violation discovery after about three years of running).
- **Test content:** the only true from-nothing continuous target on the menu. A value committed now sits in the record for years before anything can adjudicate it, which is exactly what makes it the strongest possible test and the least gratifying one.

### A3. The neutrino mass ordering (grade i, discrete)

- **What:** normal vs inverted ordering; one bit. JUNO alone reaches about 3σ on a multi-year horizon; combined analyses may speak sooner.
- **Test content:** a single-bit pre-registration is weak alone (a coin lands it half the time) but costs nothing alongside A1 or A2 and compounds a joint record.

### A4. The low-energy weak mixing angle at MOLLER (grade ii, with a mapping caveat)

- **What:** sin²θ_W at low momentum transfer, from parity-violating Møller scattering at Jefferson Lab; data-taking begins in 2026, with precision matching the best single collider determination; results expected late in the decade.
- **Caveat:** the corpus's existing Weinberg-angle formula lives at the Z pole; the low-energy value differs by Standard Model running. A MOLLER pre-registration therefore needs its own adjudication first: whether the grammar addresses the low-energy value directly or only through the Z-pole formula plus standard running, in which case the test is of the running, not the grammar. Staged as secondary until that is decided.

### A5. Considered and not staged (with reasons)

- **Neutron lifetime (BL3):** BL3 completes commissioning at NIST in 2026 and aims at 0.1 s on a 10 s beam-vs-bottle discrepancy. Not staged: the lifetime is dimensionful (seconds), which the grammar does not address without a contrived ratio, and the discrepancy makes "the measured value" ambiguous until resolved.
- **W boson mass:** the live dispute (CDF 80,433.5 ± 9.4 MeV vs the CMS-anchored world picture near 80,360, PDG average 80,369.2 ± 13.3 MeV excluding CDF) plays out at the 10 MeV scale; the corpus's W formula carries 0.15% (about 120 MeV) accuracy. The measurement war will resolve far below the formula's resolving power either way; no test content.
- **Muon g-2:** the experimental value is final (Fermilab, June 2025); what moves next is the Standard Model theory side (lattice vs data-driven hadronic vacuum polarization), and J-PARC E34 commissions around 2028. A theory consensus is not a measurement arriving; not staged.
- **KATRIN:** final analysis (toward 0.3 eV sensitivity) is in progress via parallel blind analyses, but the output is an upper limit, not a value; nothing for a numeric pre-registration unless a signal appears.
- **Proton charge radius:** largely converged since the muonic-hydrogen resolution, and dimensionful; no clean target.

## Class B: standing corpus bands meeting incoming data (grade iii)

These require no new computation; the formulas and bands are already published. The pre-registration move is to restate each band and its kill semantics in a dated record before the named data arrives, so that no future reading of the corpus can suspect post-hoc adjustment.

### B1. The α closed form vs CODATA 2026 [NEAREST CLOCK]

- **Standing claim (published):** 1/α = 360/φ² − 2/φ³ + α/(59/3) = 137.035999147, at 0.22 ppb from CODATA 2022 (`docs/alpha_derivation.html`; the separability clause: the representation layer survives the auxiliary claim's death).
- **Incoming data:** the CODATA 2026 adjustment has a hard data cutoff of 2026-12-31 and publishes in early 2027 (task-group meeting at the BIPM, September 2026). Its α will have to digest the standing >5σ rubidium-vs-cesium interferometry discrepancy plus the electron magnetic-moment route; an improved Berkeley measurement targeting 2 × 10⁻¹¹ is underway and may or may not land before the cutoff.
- **The restatement to sign:** the closed-form value is already frozen in the corpus; the 2026 recommended value will be compared against it and the distance reported whatever it is, with the exact kill band semantics (how far is dead) pinned in the restatement record before the CODATA release.

### B2. The Λ-constancy commitment vs Euclid DR1 and DESI DR3 [MOST EXPOSED]

- **Standing position (published):** the corpus reads dark energy as Φ at 3D, "constant energy per unit volume," and computes Λ as a constant (§27.7g at 0.004%). That reading implies an equation of state w = −1, constant.
- **Incoming data:** DESI DR2 (March 2025) already shows a 3.1σ preference for evolving dark energy, rising to about 4.2σ with supernova data. Euclid DR1 is expected in October 2026; DESI DR3 follows. This is the corpus's most exposed implicit commitment, and current data leans against it.
- **The move to sign (two steps):** first an adjudication, not a restatement: does the framework commit to w = −1 exactly, or does the nesting picture (Λ as the Φ of the scale above, which is itself a whole with its own dynamics) leave room the corpus has not needed to use? Whichever way Ashman adjudicates, the answer gets dated BEFORE Euclid DR1. Committing to w = −1 in August 2026 against a 3σ headwind would be the framework at its gutsiest; discovering that the framework genuinely permits evolution would be equally worth having on record before the data speaks, and indistinguishable from a dodge if recorded after.

### B3. The cosmological budget vs sharpening surveys

- **Standing claim (published):** DE = T²/V = 9/13 = 69.23%, with the three-way split at 0.03 to 0.17% against the 2018-era values. DESI, Euclid, and successors sharpen Ω_Λ within ΛCDM, entangled with the Hubble tension and with B2 (if w drifts, the constant-budget frame itself shifts). Worth a dated restatement alongside B2; adjudication data accumulates continuously rather than on one clock.

### B4. The Cabibbo formula vs the Cabibbo-angle anomaly

- **Standing claim (published):** sin θ_C = 0.22432 against the 2022-era 0.2243 ± 0.0005. The first-row CKM unitarity test currently shows a 2-3σ deficit, with V_us determinations split by channel; lattice and radiative-correction work is converging on it over the next few years. A dated restatement would name which experimental channel the formula binds to before the resolution picks a side. Diffuse clock; secondary.

### B5. Scalar-sector minimality (listed for the ledger)

- Already fully stated in the corpus with no restatement needed: any charged Higgs or CP-odd scalar falsifies the 64-state architecture. Standing LHC searches adjudicate continuously. Listed so the ledger of live stakes is complete in one place.

## Recommendation

**Pick A1 now** (the JUNO pair, jointly), because its clock is the fastest and its window is actively closing; **sign B1 and B2 in the same dated record** (B1 is pure restatement before a December cutoff; B2's adjudication must precede October to mean anything); **stage A2** (δ_CP) as the from-nothing flagship whenever Ashman wants the strongest test on the slowest clock. A3 rides along free with any pick. A4 and B3/B4 wait.

## Open decisions (Ashman to adjudicate)

1. **The pick** (A1 recommended; A2 and A3 compatible additions; any combination is valid under the protocol).
2. **The computation-session procedure** for the picked target(s): protocol clause 2 as written (selection rules and pool quoted verbatim before any search), or amended.
3. **The B2 adjudication**: does the framework commit to w = −1 exactly? To be answered and dated before 2026-10 regardless of the Class A pick.
4. **Landing**: whether this staging record and the eventual computation record get a public-facing page beside the claims card, and when (at commitment, or at adjudication).

## Addendum (2026-08-21, same day, after the pick): correction to the Class A blindness claim

The Class A header above says "no corpus formula exists." A deeper corpus search (grep across all eras, run after Ashman's pick and before any computation) shows that claim was too broad as a sector statement, though it holds for the two picked targets. The original text stands above per the no-silent-revision discipline; the corrected state is:

- **sin²θ₁₂: clean everywhere.** No expression for it exists in the current grammar, in the archived braid-era Ch13 table (which carries sin²θ₁₃ = 1/45 and |V_us| = 1/φ³ − 0.01 but not θ₁₂), in the eml discovery program (its eight flavor targets did not include θ₁₂), or in the v10 operator-predictions run (θ₁₂ appears there only as a reference-table entry; no match was claimed in the findings).
- **Δm²₂₁/|Δm²₃₁|: clean in the current grammar, with two disclosed prior nulls in a non-primary family.** The eml program searched this ratio at tree depths up to 3 and again at depth 4 and found no signal both times (`calculations/eml_discovery_results.md`, `calculations/eml_discovery_depth4_summary.md`). A prior null contaminates nothing (there is no candidate to steer toward); it is disclosed because clause 6 requires the full search history of a target to be visible.
- **Sector archaeology, disclosed:** an archived exploratory stratum of `circumpunct_framework.md` (the braid-era 25-prediction table, whose 1/α = 4π³ + 13 contradicts the canonical closed form) contains PMNS θ₁₃ and CKM V_us entries; the eml program recorded candidates for sin²θ₂₃, sin²θ₁₃, and δ_CP that the corpus's own §27.7n caveat later downgraded (flavor-physics constants at size 3 do not reliably pass the matched-null bar). Consequence for A2: δ_CP's grade-i status carries a footnote; an eml-era candidate exists in `calculations/`, and any future δ_CP pre-registration must disclose and supersede it rather than ignore it.
- **A strengthening found in the same search:** framework §27.7p and §27.7q already pre-commit the functional form for any future coupling (α^k · framework prefactor · (1 + α · framework ratio), k assembled from the pool) and name neutrino mixing angles among the empty κ-matrix cells that "either fill the remaining cells consistently or break the architecture," adding: "The matrix is not a postdiction device; it is the framework's main channel of falsification for the next decade of precision physics." The pre-registration therefore executes a commitment the corpus made in advance of the pick, not a procedure invented for the occasion.

The pick stands: both picked targets are clean for the primary families, and the computation record (`plans/preregistration_juno_computation_2026_08_21.md`) carries the full disclosures.

## Addendum 2 (2026-08-21, same day): B2's premise corrected by the commissioned audit

B2 above says the corpus's Λ reading "implies an equation of state w = −1, constant." The commissioned audit (`plans/lambda_constancy_audit_2026_08_21.md`) found that sentence describes one voice of a two-voiced corpus: §12.2/§27.7g and the Ladder Correction Notice carry constancy, while §12.1, the public predictions page, and the unique-predictions essay carry a dated evolution prediction (w(z) ≈ −1.033 + 0.017/(1+z), "falsified cleanly if w converges to exactly −1 ± 0.005"). B2's move is therefore not "state the commitment or find the freedom" but "adjudicate between two dated strata," and the audit stages that adjudication with a pre-assigned futures table. The original B2 text stands above per the no-silent-revision discipline; the audit record is the current state.

## Sources (verified by web search, 2026-08-21)

- JUNO first results: [Phys.org](https://phys.org/news/2025-11-juno-physics-results-months.html), [EurekAlert](https://www.eurekalert.org/news-releases/1106885), [JINR](https://www.jinr.ru/posts/juno-experiment-first-physics-results-obtained/), [JUNO physics program (arXiv:2104.02565)](https://arxiv.org/pdf/2104.02565)
- CODATA 2026 schedule: [BIPM CODATA-TGFC](https://www.bipm.org/en/hosting/codata-tgfc), [CODATA fundamental constants](https://codata.org/initiatives/data-science-and-stewardship/fundamental-physical-constants/)
- α interferometry status: [Fine-structure constant review (ResearchGate)](https://www.researchgate.net/publication/395531806_The_fine-structure_constant_a_review_of_measurement_results_and_possible_space-time_variations), [LKB/SPIE rubidium recoil](https://spie.org/photonics-west/presentation/Recent-advances-in-measuring-rubidium-recoil-with-atom-interferometry/13920-1)
- Dark energy: [DESI DR2 dynamical dark energy (Nature Astronomy)](https://www.nature.com/articles/s41550-025-02669-6), [DESI](https://www.desi.lbl.gov/)
- KATRIN: [Physics World](https://physicsworld.com/a/katrin-sets-tighter-limit-on-neutrino-mass/), [MPIK](https://www.mpi-hd.mpg.de/mpi/en/public-relations/news/news-item/katrin-sets-new-limit-for-neutrino-mass)
- MOLLER: [MOLLER at JLab](https://moller.jlab.org/), [arXiv:1411.4088](https://arxiv.org/abs/1411.4088)
- W mass: [PDG 2025 W review](https://pdg.lbl.gov/2025/reviews/rpp2025-rev-w-mass.pdf), [CMS measurement (Nature)](https://www.nature.com/articles/s41586-026-10168-5), [CERN Courier on CDF](https://cerncourier.com/a/cdf-addresses-w-mass-doubt/)
- Hyper-K/DUNE: [Science (AAAS) on LBNF/DUNE](https://www.science.org/content/article/trying-stay-ahead-competition-u-s-pares-down-troubled-3-billion-neutrino-experiment), [Hyper-K (arXiv:1904.10206)](https://arxiv.org/pdf/1904.10206)
- Muon g-2 at J-PARC: [E34 status (JPS Conf. Proc.)](https://journals.jps.jp/doi/10.7566/JPSCP.8.025008)
- Cabibbo-angle anomaly: [PDG 2025 Vud/Vus review](https://pdg.lbl.gov/2025/reviews/rpp2024-rev-vud-vus.pdf)
- Neutron lifetime / BL3: [BL3 at Illinois](https://npl.illinois.edu/research/bl3)

## Files consulted

`plans/what_it_offers_math_and_physics_2026_08_21.md` (the commission); `CLAUDE.md` (the published formulas and bands cited in Class B; the selection-rule and pool citations for protocol clause 2); `docs/alpha_derivation.html` and framework §27.7g/h/j via CLAUDE.md summaries (Class B standing claims). No grammar-side files were opened for Class A purposes.
