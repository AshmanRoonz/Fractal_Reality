# EML-Tree Discovery Results: Depth 4 with Beam Search

Odrzywołek 2026: eml(x,y) = exp(x) - ln(y) + 1

This report extends the depth-3 search to depth-4 using beam search with aggressive pruning.

## Primary Targets (No shallow matches at depth 3)

### Jarlskog

**Target value:** 3.0800000000e-05

#### Candidate 1

**Formula:** eml(alpha^5, 7)

**Value:** 5.4089850965e-02

**Error:** 1.755164e+03 (175516.3992%)

**Depth:** 1

**Consistency:** fits_ladder

**VERDICT:** No signal

---

#### Candidate 2

**Formula:** eml(alpha^4, 7)

**Value:** 5.4089853780e-02

**Error:** 1.755164e+03 (175516.4084%)

**Depth:** 1

**Consistency:** fits_ladder

**VERDICT:** No signal

---

#### Candidate 3

**Formula:** eml(alpha^3, 7)

**Value:** 5.4090239539e-02

**Error:** 1.755177e+03 (175517.6608%)

**Depth:** 1

**Consistency:** fits_ladder

**VERDICT:** No signal

---

#### Candidate 4

**Formula:** eml(alpha^2, 7)

**Value:** 5.4143103717e-02

**Error:** 1.756893e+03 (175689.2978%)

**Depth:** 1

**Consistency:** fits_ladder

**VERDICT:** No signal

---

#### Candidate 5

**Formula:** eml(alpha, 7)

**Value:** 6.1413894070e-02

**Error:** 1.992958e+03 (199295.7600%)

**Depth:** 1

**Consistency:** fits_ladder

**VERDICT:** No signal

---

### V_ub

**Target value:** 3.8200000000e-03

#### Candidate 1

**Formula:** eml(eml(alpha^3, phi^4), 8)

**Value:** -1.3923666517e-03

**Error:** 1.364494e+00 (136.4494%)

**Depth:** 2

**Consistency:** fits_ladder

**VERDICT:** No signal

---

#### Candidate 2

**Formula:** eml(eml(alpha^4, phi^4), 8)

**Value:** -1.3927825180e-03

**Error:** 1.364603e+00 (136.4603%)

**Depth:** 2

**Consistency:** fits_ladder

**VERDICT:** No signal

---

#### Candidate 3

**Formula:** eml(eml(alpha^4, phi^4), 8)

**Value:** -1.3927825180e-03

**Error:** 1.364603e+00 (136.4603%)

**Depth:** 2

**Consistency:** fits_ladder

**VERDICT:** No signal

---

#### Candidate 4

**Formula:** eml(eml(alpha^4, phi^4), 8)

**Value:** -1.3927825180e-03

**Error:** 1.364603e+00 (136.4603%)

**Depth:** 2

**Consistency:** fits_ladder

**VERDICT:** No signal

---

#### Candidate 5

**Formula:** eml(eml(alpha^4, phi^4), 8)

**Value:** -1.3927825180e-03

**Error:** 1.364603e+00 (136.4603%)

**Depth:** 2

**Consistency:** fits_ladder

**VERDICT:** No signal

---

### mass_sq_ratio

**Target value:** 2.9500000000e-02

#### Candidate 1

**Formula:** eml(eml(eml(eml(alpha^3, phi^4), 8), 7), 8)

**Value:** -2.5329808526e-02

**Error:** 1.858638e+00 (185.8638%)

**Depth:** 4

**Consistency:** fits_ladder

**VERDICT:** No signal

---

#### Candidate 2

**Formula:** eml(eml(eml(eml(alpha^4, phi^4), 8), 7), 8)

**Value:** -2.5330246285e-02

**Error:** 1.858652e+00 (185.8652%)

**Depth:** 4

**Consistency:** fits_ladder

**VERDICT:** No signal

---

#### Candidate 3

**Formula:** eml(eml(eml(eml(alpha^4, phi^4), 8), 7), 8)

**Value:** -2.5330246285e-02

**Error:** 1.858652e+00 (185.8652%)

**Depth:** 4

**Consistency:** fits_ladder

**VERDICT:** No signal

---

#### Candidate 4

**Formula:** eml(eml(eml(eml(alpha^4, phi^4), 8), 7), 8)

**Value:** -2.5330246285e-02

**Error:** 1.858652e+00 (185.8652%)

**Depth:** 4

**Consistency:** fits_ladder

**VERDICT:** No signal

---

#### Candidate 5

**Formula:** eml(eml(eml(eml(alpha^4, phi^4), 8), 7), 8)

**Value:** -2.5330246285e-02

**Error:** 1.858652e+00 (185.8652%)

**Depth:** 4

**Consistency:** fits_ladder

**VERDICT:** No signal

---

## Secondary Targets (Depth-3 Candidates Re-Tested at Depth-4)

### sin2_theta_13

**Target value:** 2.2000000000e-02

#### Candidate 1

**Formula:** eml(eml(eml(alpha, 7), 8), 7)

**Value:** 3.8116195978e-02

**Error:** 7.325544e-01 (73.2554%)

**Depth:** 3

**Consistency:** fits_ladder

**VERDICT:** No signal

---

#### Candidate 2

**Formula:** eml(eml(eml(alpha^1, 7), 8), 7)

**Value:** 3.8116195978e-02

**Error:** 7.325544e-01 (73.2554%)

**Depth:** 3

**Consistency:** fits_ladder

**VERDICT:** No signal

---

#### Candidate 3

**Formula:** eml(eml(eml(alpha^1, 7), 8), 7)

**Value:** 3.8116195978e-02

**Error:** 7.325544e-01 (73.2554%)

**Depth:** 3

**Consistency:** fits_ladder

**VERDICT:** No signal

---

### sin2_theta_23

**Target value:** 5.4600000000e-01

#### Candidate 1

**Formula:** eml(eml(eml(eml(alpha^2, phi^3), 10), 7), 10)

**Value:** 5.3717829363e-01

**Error:** 1.615697e-02 (1.6157%)

**Depth:** 4

**Consistency:** fits_ladder

**VERDICT:** Weak (< 10% error; monitor for pattern)

---

#### Candidate 2

**Formula:** eml(eml(eml(eml(alpha^2, phi^3), 10), 7), 10)

**Value:** 5.3717829363e-01

**Error:** 1.615697e-02 (1.6157%)

**Depth:** 4

**Consistency:** fits_ladder

**VERDICT:** Weak (< 10% error; monitor for pattern)

---

#### Candidate 3

**Formula:** eml(eml(eml(eml(alpha^2, phi^3), 10), 7), 10)

**Value:** 5.3717829363e-01

**Error:** 1.615697e-02 (1.6157%)

**Depth:** 4

**Consistency:** fits_ladder

**VERDICT:** Weak (< 10% error; monitor for pattern)

---

#### Candidate 4

**Formula:** eml(eml(eml(eml(alpha^2, phi^3), 10), 7), 10)

**Value:** 5.3717829363e-01

**Error:** 1.615697e-02 (1.6157%)

**Depth:** 4

**Consistency:** fits_ladder

**VERDICT:** Weak (< 10% error; monitor for pattern)

---

#### Candidate 5

**Formula:** eml(eml(eml(eml(alpha^3, phi^3), 10), 7), 10)

**Value:** 5.3691442172e-01

**Error:** 1.664025e-02 (1.6640%)

**Depth:** 4

**Consistency:** fits_ladder

**VERDICT:** Weak (< 10% error; monitor for pattern)

---

### delta_CP

**Target value:** 4.2700000000e+00

#### Candidate 1

**Formula:** eml(phi, eml(phi, eml(phi, eml(phi, phi^3))))

**Value:** 4.5312808552e+00

**Error:** 6.118990e-02 (6.1190%)

**Depth:** 4

**Consistency:** fits_ladder

**VERDICT:** Weak (< 10% error; monitor for pattern)

---

#### Candidate 2

**Formula:** eml(phi, eml(phi, eml(phi, eml(phi, phi^3))))

**Value:** 4.5312808552e+00

**Error:** 6.118990e-02 (6.1190%)

**Depth:** 4

**Consistency:** fits_ladder

**VERDICT:** Weak (< 10% error; monitor for pattern)

---

#### Candidate 3

**Formula:** eml(phi, eml(phi, eml(phi, eml(phi, 5))))

**Value:** 4.5330672628e+00

**Error:** 6.160826e-02 (6.1608%)

**Depth:** 4

**Consistency:** unclear

**VERDICT:** Weak (< 10% error; monitor for pattern)

---

#### Candidate 4

**Formula:** eml(phi, eml(phi, eml(phi, eml(phi^1, 5))))

**Value:** 4.5330672628e+00

**Error:** 6.160826e-02 (6.1608%)

**Depth:** 4

**Consistency:** fits_ladder

**VERDICT:** Weak (< 10% error; monitor for pattern)

---

#### Candidate 5

**Formula:** eml(phi, eml(phi, eml(phi, eml(phi^1, 5))))

**Value:** 4.5330672628e+00

**Error:** 6.160826e-02 (6.1608%)

**Depth:** 4

**Consistency:** fits_ladder

**VERDICT:** Weak (< 10% error; monitor for pattern)

---

### m_n_m_p

**Target value:** 1.0013784193e+00

#### Candidate 1

**Formula:** eml(eml(eml(eml(alpha^3, phi^2), 20), 12), 10)

**Value:** 9.2454290203e-01

**Error:** 7.672975e-02 (7.6730%)

**Depth:** 4

**Consistency:** fits_ladder

**VERDICT:** Weak (< 10% error; monitor for pattern)

---

#### Candidate 2

**Formula:** eml(eml(eml(eml(alpha^4, phi^2), 20), 12), 10)

**Value:** 9.2453735989e-01

**Error:** 7.673529e-02 (7.6735%)

**Depth:** 4

**Consistency:** fits_ladder

**VERDICT:** Weak (< 10% error; monitor for pattern)

---

#### Candidate 3

**Formula:** eml(eml(eml(eml(alpha^4, phi^2), 20), 12), 10)

**Value:** 9.2453735989e-01

**Error:** 7.673529e-02 (7.6735%)

**Depth:** 4

**Consistency:** fits_ladder

**VERDICT:** Weak (< 10% error; monitor for pattern)

---

#### Candidate 4

**Formula:** eml(eml(eml(eml(alpha^5, phi^2), 20), 10), 13)

**Value:** 1.1075975375e+00

**Error:** 1.060729e-01 (10.6073%)

**Depth:** 4

**Consistency:** fits_ladder

**VERDICT:** No signal

---

#### Candidate 5

**Formula:** eml(eml(eml(eml(alpha^5, phi^2), 20), 10), 13)

**Value:** 1.1075975375e+00

**Error:** 1.060729e-01 (10.6073%)

**Depth:** 4

**Consistency:** fits_ladder

**VERDICT:** No signal

---

### V_cb

**Target value:** 4.0500000000e-02

#### Candidate 1

**Formula:** eml(eml(eml(eml(alpha^5, 7), 8), 7), 7)

**Value:** 8.5070257772e-02

**Error:** 1.100500e+00 (110.0500%)

**Depth:** 4

**Consistency:** fits_ladder

**VERDICT:** No signal

---

#### Candidate 2

**Formula:** eml(eml(eml(eml(alpha^5, 7), 8), 7), 7)

**Value:** 8.5070257772e-02

**Error:** 1.100500e+00 (110.0500%)

**Depth:** 4

**Consistency:** fits_ladder

**VERDICT:** No signal

---

#### Candidate 3

**Formula:** eml(eml(eml(eml(alpha^4, 7), 8), 7), 7)

**Value:** 8.5070260763e-02

**Error:** 1.100500e+00 (110.0500%)

**Depth:** 4

**Consistency:** fits_ladder

**VERDICT:** No signal

---

#### Candidate 4

**Formula:** eml(eml(eml(eml(alpha^4, 7), 8), 7), 7)

**Value:** 8.5070260763e-02

**Error:** 1.100500e+00 (110.0500%)

**Depth:** 4

**Consistency:** fits_ladder

**VERDICT:** No signal

---

#### Candidate 5

**Formula:** eml(eml(eml(eml(alpha^3, 7), 8), 7), 7)

**Value:** 8.5070670678e-02

**Error:** 1.100510e+00 (110.0510%)

**Depth:** 4

**Consistency:** fits_ladder

**VERDICT:** No signal

---

