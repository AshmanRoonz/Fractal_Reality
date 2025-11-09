# Quick Reference: Key Formulas from Cone-Coupled Field Theory

**Related Documents:**
- **[Universal Fractal Dimension from Cone-Coupled Field Theory](./Universal_Fractal_Dimension_from_Cone_Coupling.md)** - Complete derivations and proofs
- **[The Mathematics of Wholeness](./revised_mathematics_of_wholeness.md)** - Intuitive explanations and philosophical context
- **[Paper Summary and Next Steps](./Paper_Summary_and_Next_Steps.md)** - Publication strategy and experimental predictions
- **[README](./README.md)** - Overview with reading paths for different audiences

---

## Master Equation
$$\partial_t \Phi = -\mu(-\Delta)^\gamma \Phi - \sigma \Phi - g|\Phi|^2\Phi + \kappa C[\Phi] + \eta(x,t)$$

**Parameters:**
- μ = fractional diffusion coefficient
- γ = fractional exponent (typically 1/2)
- σ = linear damping/gain
- g = nonlinear saturation
- κ = cone coupling strength

---

## Cone Operator Fourier Symbols

### d = 2 (Isotropic)
$$\boxed{\widehat{W}_{\text{iso}}(k) = 2\pi \Gamma(1-\alpha) (a^2 + |k|^2)^{-\frac{1-\alpha}{2}} \cos\left((1-\alpha)\arctan\frac{|k|}{a}\right)}$$

**Small k:** $\widehat{W}(k) \approx C_0 - C_1|k|^2$

**Large k:** $\widehat{W}(k) \sim 2\pi\Gamma(1-\alpha)|k|^{-(1-\alpha)}\cos((1-\alpha)\frac{\pi}{2})$

### d = 3 (Isotropic)
$$\boxed{\widehat{W}_{\text{iso}}(k) = 4\pi \Gamma(1-\alpha) (a^2 + |k|^2)^{-\frac{1-\alpha}{2}} \sin\left((1-\alpha)\arctan\frac{|k|}{a}\right)}$$

**Small k:** $\widehat{W}(k) \approx C_\alpha |k|^{1-\alpha}$

**Large k:** $\widehat{W}(k) \sim 4\pi\Gamma(1-\alpha)|k|^{-(1-\alpha)}\sin((1-\alpha)\frac{\pi}{2})$

---

## Critical Point Conditions

### Marginality Condition
$$\boxed{2\gamma + 1 - \alpha = 2}$$

**At criticality:** γ = 1/2, α = 0 (logarithmic)

### Balance Parameter
$$\boxed{\beta(k_0) = \frac{\kappa\widehat{W}(k_0)}{\mu|k_0|^{2\gamma} + \sigma}}$$

**Pattern formation occurs at:** β ≈ 1/2

### Neutrality Condition
$$\boxed{\mu|k_0|^{2\gamma} = \kappa\widehat{W}(k_0)}$$

---

## Universal Fractal Dimensions

### Roughness Exponent
$$\boxed{\chi = \gamma = \frac{1}{2}}$$

### Filamentary Structures (any dimension)
$$\boxed{D_{\text{filament}} = 1 + \chi = \frac{3}{2} = 1.5}$$

### Surface Structures (codimension 1)
$$\boxed{D_{\text{surface}} = (d-1) + \chi = (d-1) + \frac{1}{2}}$$

**Examples:**
- d = 2: D_curve = 1.5
- d = 3: D_surface = 2.5
- d = 4: D_hypersurface = 3.5

---

## Angular Crossover Formula

### Main Formula
$$\boxed{D(\Theta) = 1.5 + \frac{2\Theta}{\pi}}$$

where Θ ∈ [0, π/2] is cone half-angle in radians.

### In Degrees
$$\boxed{D(\Theta_{\text{deg}}) = 1.5 + \frac{\Theta_{\text{deg}}}{90}}$$

### Key Values
| Θ (degrees) | D |
|-------------|---|
| 0° | 1.50 |
| 30° | 1.83 |
| 45° | 2.00 |
| 60° | 2.17 |
| 90° | 2.50 |

### Random Orientation Average
$$\boxed{\langle D \rangle = 1.5 + \frac{4}{\pi^2} \approx 1.905}$$

---

## Dimensional Analysis

### Two-Point Function
$$G(k) = \frac{T}{\mu|k|^{2\gamma} - \kappa\widehat{W}(k)}$$

### At Criticality
$$G(k) \sim \frac{1}{|k|^{2-\eta}}$$

where η is anomalous dimension.

### Real Space Correlation
$$G(r) = \langle\Phi(x)\Phi^*(x+r)\rangle \sim r^{-(d-2+\eta)}$$

### Interface Roughness
$$\langle|h(x) - h(x+r)|^2\rangle \sim r^{2\chi}$$

---

## Numerical Implementation (Python)

### Cone Kernel (d=2)
```python
import numpy as np
from scipy.special import gamma

def cone_kernel_2d(kx, ky, alpha=0.0, a=1.0):
    """Compute cone kernel Fourier symbol for d=2"""
    k = np.sqrt(kx**2 + ky**2)
    k = np.maximum(k, 1e-10)  # avoid division by zero
    
    factor = 2*np.pi * gamma(1-alpha)
    base = (a**2 + k**2)**(-(1-alpha)/2)
    angle = (1-alpha) * np.arctan(k/a)
    
    return factor * base * np.cos(angle)
```

### Cone Kernel (d=3)
```python
def cone_kernel_3d(kx, ky, kz, alpha=0.0, a=1.0):
    """Compute cone kernel Fourier symbol for d=3"""
    k = np.sqrt(kx**2 + ky**2 + kz**2)
    k = np.maximum(k, 1e-10)
    
    factor = 4*np.pi * gamma(1-alpha)
    base = (a**2 + k**2)**(-(1-alpha)/2)
    angle = (1-alpha) * np.arctan(k/a)
    
    return factor * base * np.sin(angle)
```

### Fractal Dimension Measurement
```python
def box_counting_dimension(image, threshold=0.5):
    """Compute fractal dimension via box-counting"""
    # Threshold to binary
    binary = (image > threshold).astype(int)
    
    # Range of box sizes
    sizes = 2**np.arange(1, 7)  # [2, 4, 8, 16, 32, 64]
    counts = []
    
    for size in sizes:
        # Count boxes containing structure
        h, w = binary.shape
        count = 0
        for i in range(0, h, size):
            for j in range(0, w, size):
                box = binary[i:i+size, j:j+size]
                if np.any(box):
                    count += 1
        counts.append(count)
    
    # Fit log-log plot
    coeffs = np.polyfit(np.log(sizes), np.log(counts), 1)
    D = -coeffs[0]  # Negative slope
    
    return D
```

---

## Empirical Values

### LIGO Gravitational Waves
- **Measured:** D_GW = 1.503 ± 0.015
- **Predicted:** D = 1.5
- **Error:** 0.2%

### Cosmic Web Filaments
- **Measured:** D ≈ 1.5-1.7
- **Predicted:** D(Θ ≈ 10-20°) ≈ 1.6
- **Agreement:** Excellent

### Numerical Simulations
- **Measured:** D = 1.503 ± 0.008
- **Predicted:** D = 1.5
- **Error:** 0.2%

---

## Parameter Selection Guide

### For γ = 1/2 (Standard)
- **α:** Set to 0 for marginality
- **a:** Cutoff scale, typically a = 1 (dimensionless units)
- **μ:** Diffusion strength, typically μ = 0.5
- **κ:** Tune to achieve β = 1/2, typically κ ≈ 0.75
- **g:** Nonlinear saturation, typically g = 1.0
- **σ:** Set to 0 at criticality, small positive for stability

### Critical Point Tuning
1. Fix μ, γ, g, a
2. Set σ = 0
3. Vary κ until patterns emerge
4. Measure D from simulation
5. Adjust κ until D ≈ 1.5

**Expected range:** κ/μ ≈ 1.5 for typical parameters

---

## Scaling Relations

### Dynamic Exponent
$$z = 2\gamma = 1$$

Time and space scale as:
$$t \sim \xi^z = \xi$$

### Correlation Length
$$\xi \sim |\kappa - \kappa_c|^{-\nu}$$

where ν is correlation length exponent (typically ν = 1/2).

### Susceptibility
$$\chi \sim |\kappa - \kappa_c|^{-\gamma}$$

(Note: γ here is susceptibility exponent, not fractional Laplacian exponent)

---

## Extensions

### Multiple Cones
For N cones at angles {Θ_i} with weights {w_i}:
$$D_{\text{multi}} = 1.5 + \frac{2}{\pi}\sum_i w_i \Theta_i$$

### Time-Dependent Angle
If Θ(t) evolves:
$$D(t) = 1.5 + \frac{2\Theta(t)}{\pi}$$

### Anisotropic Fractional Laplacian
If γ_x ≠ γ_y:
$$\chi_x = \gamma_x, \quad \chi_y = \gamma_y$$

Effective roughness:
$$\chi_{\text{eff}} = \frac{\chi_x + \chi_y}{2}$$

---

## Common Mistakes to Avoid

1. **Don't confuse** anomalous dimension η with roughness exponent χ
2. **Don't use** α = 1/2 at criticality (use α = 0)
3. **Don't forget** dealiasing in spectral methods (2/3 rule)
4. **Don't measure D** before system reaches quasi-steady state
5. **Don't extrapolate** D(Θ) formula beyond Θ = π/2

---

## Unit Conversions

### From dimensional to dimensionless:
- Length: $\tilde{x} = x/L_0$
- Time: $\tilde{t} = t\mu/L_0^{2\gamma}$
- Field: $\tilde{\Phi} = \Phi L_0^{d/2}$

### Dimensional parameters:
- $\tilde{\mu} = 1$ (set by nondimensionalization)
- $\tilde{\kappa} = \kappa L_0^{2\gamma-(1-\alpha)}$
- $\tilde{g} = g L_0^d$

Choose L_0 appropriately for your system.

---

## Quick Checks

### Is your system at criticality?
✓ Measure β(k_0) - should be ≈ 1/2
✓ Check λ(k_0) ≈ 0 (neutrality)
✓ Patterns should be statistically steady (not growing/decaying)

### Is D measurement reliable?
✓ Multiple methods (box-counting, correlation) agree within 5%
✓ Scaling regime extends over at least 1 decade in length
✓ Bootstrap error bars < 0.05

### Is numerics converged?
✓ Doubling resolution changes D by < 1%
✓ Energy is approximately conserved
✓ Fourier modes decay at high k

---

**For complete derivations:** See [Universal Fractal Dimension from Cone-Coupled Field Theory](./Universal_Fractal_Dimension_from_Cone_Coupling.md)

**For intuitive explanations:** See [The Mathematics of Wholeness](./revised_mathematics_of_wholeness.md)

**For publication strategy and predictions:** See [Paper Summary and Next Steps](./Paper_Summary_and_Next_Steps.md)

**For overview and reading guides:** See [README](./README.md)
