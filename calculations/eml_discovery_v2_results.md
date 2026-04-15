# EML Discovery v2 Results (CORRECTED eml = exp(x) - ln(y))

Max tree size: 3 internal nodes
Total trees enumerated: 358,458
Leaf basis: 1, alpha, phi, pi, e, 2, 3, 4, 5, 7, 8, 10, 12, 13, 20, 21, 27, 28, 56, 64, 81, 91, 147, 247


## m_n_over_m_p
Measured: 1.00137841931

Top 5 candidates:

| Rank | Rel Err | Size | Value | Formula |
|------|---------|------|-------|---------|
| 1 | 0.0154% | 3 | 1.00122 | `eml(phi, eml(eml(2, 27), 20))` |
| 2 | 0.0213% | 3 | 1.00117 | `eml(2, eml(eml(2, e), 2))` |
| 3 | 0.0257% | 3 | 1.00112 | `eml(eml(2, eml(7, 147)), phi)` |
| 4 | 0.0302% | 3 | 1.00168 | `eml(2, eml(eml(2, e), e))` |
| 5 | 0.0447% | 3 | 1.00183 | `eml(eml(2, eml(7, 247)), phi)` |

Verdict: **STRONG** (best error 0.0154%)

## V_cb
Measured: 0.0405

Top 5 candidates:

| Rank | Rel Err | Size | Value | Formula |
|------|---------|------|-------|---------|
| 1 | 0.0027% | 3 | 0.0405011 | `eml(eml(eml(1, 10), 1), 91)` |
| 2 | 0.0243% | 3 | 0.0405098 | `eml(eml(1, eml(pi, 12)), 2)` |
| 3 | 0.3583% | 3 | 0.0406451 | `eml(eml(eml(alpha, 64), 2), phi)` |
| 4 | 0.4057% | 3 | 0.0406643 | `eml(eml(eml(alpha, 21), 1), 3)` |
| 5 | 0.4653% | 3 | 0.0406885 | `eml(eml(eml(alpha, 21), 28), 1)` |

Verdict: **STRONG** (best error 0.0027%)

## V_ub
Measured: 0.00382

Top 5 candidates:

| Rank | Rel Err | Size | Value | Formula |
|------|---------|------|-------|---------|
| 1 | 0.0744% | 3 | 0.00382284 | `eml(1, eml(3, eml(5, 5)))` |
| 2 | 0.8184% | 3 | 0.00378874 | `eml(eml(alpha, 247), eml(alpha, 1))` |
| 3 | 2.3914% | 2 | 0.00391135 | `eml(1, eml(3, 147))` |
| 4 | 2.5920% | 3 | 0.00391901 | `eml(eml(1, eml(3, 147)), e)` |
| 5 | 2.7084% | 3 | 0.00392346 | `eml(1, eml(3, eml(5, 4)))` |

Verdict: **STRONG** (best error 0.0744%)

## Jarlskog
Measured: 3.08e-05

Top 5 candidates:

| Rank | Rel Err | Size | Value | Formula |
|------|---------|------|-------|---------|
| 1 | 11.2118% | 3 | 3.42532e-05 | `eml(eml(1, eml(13, alpha)), 1)` |
| 2 | 11.2131% | 3 | 3.42536e-05 | `eml(eml(1, eml(13, 1)), 1)` |
| 3 | 11.2132% | 3 | 3.42537e-05 | `eml(eml(1, eml(13, phi)), 1)` |
| 4 | 11.2132% | 3 | 3.42537e-05 | `eml(eml(1, eml(13, 2)), 1)` |
| 5 | 11.2133% | 3 | 3.42537e-05 | `eml(eml(1, eml(13, e)), 1)` |

Verdict: **no-signal** (best error 11.2118%)

## sin2_theta_13
Measured: 0.022

Top 5 candidates:

| Rank | Rel Err | Size | Value | Formula |
|------|---------|------|-------|---------|
| 1 | 0.0113% | 3 | 0.0220025 | `eml(eml(eml(alpha, 8), 64), 1)` |
| 2 | 0.0335% | 3 | 0.0219926 | `eml(eml(eml(alpha, phi), 247), 1)` |
| 3 | 0.1999% | 3 | 0.022044 | `eml(eml(eml(alpha, 13), 56), 1)` |
| 4 | 0.5399% | 3 | 0.0221188 | `eml(eml(1, eml(e, 81)), 4)` |
| 5 | 0.6166% | 3 | 0.0218643 | `eml(eml(eml(alpha, 8), 1), 4)` |

Verdict: **STRONG** (best error 0.0113%)

## sin2_theta_23
Measured: 0.546

Top 5 candidates:

| Rank | Rel Err | Size | Value | Formula |
|------|---------|------|-------|---------|
| 1 | 0.0022% | 3 | 0.546012 | `eml(eml(eml(alpha, 1), 10), e)` |
| 2 | 0.0032% | 3 | 0.545983 | `eml(eml(1, eml(phi, 3)), 27)` |
| 3 | 0.0099% | 2 | 0.545946 | `eml(eml(1, 5), 12)` |
| 4 | 0.0156% | 3 | 0.546085 | `eml(eml(eml(phi, 81), e), 7)` |
| 5 | 0.0181% | 3 | 0.545901 | `eml(eml(alpha, eml(1, 3)), pi)` |

Verdict: **STRONG** (best error 0.0022%)

## mass_sq_ratio
Measured: 0.0295

Top 5 candidates:

| Rank | Rel Err | Size | Value | Formula |
|------|---------|------|-------|---------|
| 1 | 0.0532% | 3 | 0.0295157 | `eml(eml(eml(alpha, pi), 81), 1)` |
| 2 | 0.1423% | 3 | 0.029542 | `eml(phi, eml(eml(phi, 1), 91))` |
| 3 | 0.8117% | 3 | 0.0292605 | `eml(eml(eml(phi, 247), 64), 1)` |
| 4 | 0.9874% | 3 | 0.0292087 | `eml(eml(1, 12), eml(phi, 5))` |
| 5 | 1.1424% | 3 | 0.029163 | `eml(eml(1, 21), eml(phi, 21))` |

Verdict: **STRONG** (best error 0.0532%)

## delta_CP
Measured: 4.27

Top 5 candidates:

| Rank | Rel Err | Size | Value | Formula |
|------|---------|------|-------|---------|
| 1 | 0.0078% | 3 | 4.27033 | `eml(eml(phi, 27), eml(2, 21))` |
| 2 | 0.0161% | 3 | 4.27069 | `eml(phi, eml(alpha, eml(alpha, 2)))` |
| 3 | 0.0183% | 3 | 4.27078 | `eml(phi, eml(phi, eml(3, 10)))` |
| 4 | 0.0186% | 3 | 4.27079 | `eml(phi, eml(eml(1, 7), 1))` |
| 5 | 0.0218% | 3 | 4.26907 | `eml(eml(phi, 27), eml(phi, 2))` |

Verdict: **STRONG** (best error 0.0078%)