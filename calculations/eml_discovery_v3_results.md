# EML Discovery v3: tight basis, size <= 2, with null test

Basis: {1, alpha, phi, pi, T, P, R, SU3, G, V}  (10 leaves; framework primitives only)

Total trees: 1,540

## Null distribution by range (40 random draws each)

| range | min | p10 | median | p90 |
|---|---|---|---|---|
| near-unity | 0.0078% | 0.0575% | 0.3942% | 1.1539% |
| percent | 0.1658% | 0.7348% | 27.2842% | 48.1454% |
| sub-percent | 0.5508% | 10.4382% | 125.7559% | 491.9103% |
| ppm | 7362.1954% | 12698.1186% | 81671.2380% | 530467.0708% |
| small-sin2 | 1.4693% | 5.1502% | 34.3900% | 47.9305% |
| mid-sin2 | 0.1499% | 0.4584% | 1.5117% | 5.9278% |
| mass-ratio | 1.8339% | 5.6166% | 34.6812% | 49.6796% |
| phase | 0.0116% | 0.0530% | 0.5116% | 1.3701% |

## Real targets

| target | measured | best pred | rel err | size | formula | null p10 | verdict |
|---|---|---|---|---|---|---|---|
| m_n_over_m_p | 1.00138 | 1.00003 | 0.1350% | 2 | `eml(alpha, eml(alpha, 1))` | 0.0575% | noise |
| V_cb | 0.0405 | 0.0209826 | 48.1911% | 2 | `eml(eml(1, V), pi)` | 0.7348% | noise |
| V_ub | 0.00382 | 0.00729735 | 91.0302% | 0 | `alpha` | 10.4382% | noise |
| Jarlskog | 3.08e-05 | 0.00729735 | 23592.7031% | 0 | `alpha` | 12698.1186% | noise |
| sin2_theta_13 | 0.022 | 0.0209826 | 4.6246% | 2 | `eml(eml(1, V), pi)` | 5.1502% | marginal |
| sin2_theta_23 | 0.546 | 0.54761 | 0.2949% | 2 | `eml(eml(alpha, phi), pi)` | 0.4584% | marginal |
| mass_sq_ratio | 0.0295 | 0.0209826 | 28.8726% | 2 | `eml(eml(1, V), pi)` | 5.6166% | noise |
| delta_CP | 4.27 | 4.238 | 0.7494% | 2 | `eml(phi, eml(1, phi))` | 0.0530% | noise |

## Top-5 per target

### m_n_over_m_p (measured 1.00138)

| rank | rel err | size | value | formula |
|---|---|---|---|---|
| 1 | 0.1350% | 2 | 1.00003 | `eml(alpha, eml(alpha, 1))` |
| 2 | 0.1377% | 0 | 1 | `1` |
| 3 | 0.5937% | 1 | 1.00732 | `eml(alpha, 1)` |
| 4 | 1.8760% | 2 | 1.02016 | `eml(eml(1, R), pi)` |
| 5 | 4.1730% | 2 | 1.04317 | `eml(phi, eml(P, 1))` |

### V_cb (measured 0.0405)

| rank | rel err | size | value | formula |
|---|---|---|---|---|
| 1 | 48.1911% | 2 | 0.0209826 | `eml(eml(1, V), pi)` |
| 2 | 65.6795% | 2 | 0.0671002 | `eml(eml(1, V), T)` |
| 3 | 67.8941% | 2 | 0.0679971 | `eml(alpha, eml(phi, G))` |
| 4 | 81.9159% | 2 | 0.00732404 | `eml(alpha, eml(1, 1))` |
| 5 | 81.9818% | 0 | 0.00729735 | `alpha` |

### V_ub (measured 0.00382)

| rank | rel err | size | value | formula |
|---|---|---|---|---|
| 1 | 91.0302% | 0 | 0.00729735 | `alpha` |
| 2 | 91.7289% | 2 | 0.00732404 | `eml(alpha, eml(1, 1))` |
| 3 | 449.2826% | 2 | 0.0209826 | `eml(eml(1, V), pi)` |
| 4 | 1451.5018% | 2 | -0.0516274 | `eml(eml(1, SU3), R)` |
| 5 | 1656.5495% | 2 | 0.0671002 | `eml(eml(1, V), T)` |

### Jarlskog (measured 3.08e-05)

| rank | rel err | size | value | formula |
|---|---|---|---|---|
| 1 | 23592.7031% | 0 | 0.00729735 | `alpha` |
| 2 | 23679.3608% | 2 | 0.00732404 | `eml(alpha, eml(1, 1))` |
| 3 | 68025.3061% | 2 | 0.0209826 | `eml(eml(1, V), pi)` |
| 4 | 167721.3275% | 2 | -0.0516274 | `eml(eml(1, SU3), R)` |
| 5 | 217757.7644% | 2 | 0.0671002 | `eml(eml(1, V), T)` |

### sin2_theta_13 (measured 0.022)

| rank | rel err | size | value | formula |
|---|---|---|---|---|
| 1 | 4.6246% | 2 | 0.0209826 | `eml(eml(1, V), pi)` |
| 2 | 66.7089% | 2 | 0.00732404 | `eml(alpha, eml(1, 1))` |
| 3 | 66.8302% | 0 | 0.00729735 | `alpha` |
| 4 | 205.0009% | 2 | 0.0671002 | `eml(eml(1, V), T)` |
| 5 | 209.0777% | 2 | 0.0679971 | `eml(alpha, eml(phi, G))` |

### sin2_theta_23 (measured 0.546)

| rank | rel err | size | value | formula |
|---|---|---|---|---|
| 1 | 0.2949% | 2 | 0.54761 | `eml(eml(alpha, phi), pi)` |
| 2 | 1.4631% | 2 | 0.553989 | `eml(alpha, eml(1, pi))` |
| 3 | 3.6425% | 1 | 0.526112 | `eml(alpha, phi)` |
| 4 | 3.8275% | 2 | 0.525102 | `eml(alpha, eml(1, T))` |
| 5 | 6.9618% | 2 | 0.507988 | `eml(eml(1, SU3), P)` |

### mass_sq_ratio (measured 0.0295)

| rank | rel err | size | value | formula |
|---|---|---|---|---|
| 1 | 28.8726% | 2 | 0.0209826 | `eml(eml(1, V), pi)` |
| 2 | 75.1727% | 2 | 0.00732404 | `eml(alpha, eml(1, 1))` |
| 3 | 75.2632% | 0 | 0.00729735 | `alpha` |
| 4 | 127.4583% | 2 | 0.0671002 | `eml(eml(1, V), T)` |
| 5 | 130.4986% | 2 | 0.0679971 | `eml(alpha, eml(phi, G))` |

### delta_CP (measured 4.27)

| rank | rel err | size | value | formula |
|---|---|---|---|---|
| 1 | 0.7494% | 2 | 4.238 | `eml(phi, eml(1, phi))` |
| 2 | 1.6988% | 2 | 4.34254 | `eml(eml(1, pi), phi)` |
| 3 | 2.2625% | 2 | 4.17339 | `eml(1, eml(1, G))` |
| 4 | 3.1469% | 2 | 4.13563 | `eml(phi, eml(phi, V))` |
| 5 | 3.8914% | 2 | 4.10384 | `eml(phi, eml(phi, G))` |
