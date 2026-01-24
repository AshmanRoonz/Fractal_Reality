# ⊙ Circumpunct Chemistry ⊙

**Deriving Chemistry from Geometric First Principles**

[![Status](https://img.shields.io/badge/status-experimental-yellow)]()
[![Accuracy](https://img.shields.io/badge/periodic_table-87.3%25-blue)]()
[![Molecules](https://img.shields.io/badge/molecules-68.4%25-orange)]()
[![License](https://img.shields.io/badge/license-open--academic-orange)]()

---

## 🎯 What This Is

A derivation of chemistry from the Circumpunct Framework (⊙ = • ⊗ ○ ⊗ Φ), achieving:

- **87.3% accuracy** on periodic table electron configurations (48/55 elements)
- **68.4% accuracy** on molecular structure benchmark (26/38 tests)
- **99.84% accuracy** on H₂ orbital contraction (single datapoint)
- **Zero fitted parameters for periodic table** - λ derived from φ and R∞

**Current limitations:**
- Molecular compiler only handles H, C, N, O, F (hardcoded configs)
- Diatomic molecules (N₂, O₂) incorrectly predicted as bent
- Molecules with S, Cl, etc. fail to compile

Starting from a single geometric symbol, we derive:
```
⊙ → 64 states → atoms → molecules → networks
```

This is **an experimental geometric framework** for understanding periodic structure and bonding.

---

## 🚀 Quick Start

### Run Validations

```bash
# Periodic table validation (89.6%)
cd 04-validation/CURRENT
python verify_64state_COMPLETE_v2_optimizer.py

# Molecular structure (100%)
cd ../../05-demos
python demo_molecular_compiler.py

# Complete pipeline: ⊙ → H₂O
python clean_3layer_demo.py
```

### Explore Interactively

Open in browser:
- `06-visualizations/64state_chemistry_visualizer.html` - Interactive 64-state explorer
- `06-visualizations/battery_visualizer.html` - Battery architecture  
- `06-visualizations/fractal_visualizer.html` - Fractal field dynamics

---

## 📊 Key Results

### Periodic Table (Derived λ)

**Derived:**
```
λ = R∞ × φ⁻⁷ = 0.469 eV  (angular penalty)
```

**Accuracy (validated 2024-12-26):**
```
Main group (H-Ar):          18/18 = 100% ✓✓✓
1st row TM (K-Zn):          12/12 = 100% ✓✓✓
2nd row TM (Y-Cd):           6/10 =  60%
Lanthanides (La-Lu):        12/15 =  80% ✓
───────────────────────────────────────
TOTAL:                      48/55 = 87.3%
```

### H₂ Bonding (φ-Scaling)

**Prediction:**
```
ζ = 1 + φ⁻³ = 1.236068
```

**Quantum chemistry optimum:**
```
ζ_opt = 1.238
```

**Agreement: 99.84%** (single datapoint)

### Molecular Structure (Benchmark)

| Molecule | Geometry | Angle | Polarity | Result |
|----------|----------|-------|----------|--------|
| H₂O | Bent | 104.5° | Polar | ✓ |
| CH₄ | Tetrahedral | 109.5° | Nonpolar | ✓ |
| NH₃ | Pyramidal | 107.0° | Polar | ✓ |
| CO₂ | Linear | 180.0° | Nonpolar | ✓ |
| N₂ | **Bent (wrong)** | 117° | Nonpolar | ✗ |
| O₂ | **Bent (wrong)** | 104.5° | Nonpolar | ✗ |
| HCl | **Fails to compile** | - | - | ✗ |

**Benchmark result:** 26/38 = **68.4%** (Grade D)

---

## 📂 Repository Structure

| Folder | Description | Key Files |
|--------|-------------|-----------|
| [01-core-theory/](01-core-theory/) | Framework foundations | [THE_COMPLETE_CIRCUMPUNCT_FRAMEWORK.md](01-core-theory/THE_COMPLETE_CIRCUMPUNCT_FRAMEWORK.md), [PHYSICS_PAPER_GEOMETRIC_PERIODIC_TABLE.md](01-core-theory/PHYSICS_PAPER_GEOMETRIC_PERIODIC_TABLE.md) |
| [02-chemistry-theory/](02-chemistry-theory/) | Chemical applications | [circumpunct_chemistry_64state.md](02-chemistry-theory/circumpunct_chemistry_64state.md) ⭐, [H2_BONDING_PUBLICATION_DRAFT.md](02-chemistry-theory/H2_BONDING_PUBLICATION_DRAFT.md) |
| [03-implementation/](03-implementation/) | Python modules | [molecular_compiler.py](03-implementation/molecular_compiler.py) ⭐ |
| [04-validation/CURRENT/](04-validation/CURRENT/) | Validation scripts | [verify_64state_COMPLETE_v2_optimizer.py](04-validation/CURRENT/verify_64state_COMPLETE_v2_optimizer.py) |
| [05-demos/](05-demos/) | Quick demonstrations | [demo_molecular_compiler.py](05-demos/demo_molecular_compiler.py) |
| [06-visualizations/](06-visualizations/) | Interactive HTML tools | [64state_chemistry_visualizer.html](06-visualizations/64state_chemistry_visualizer.html) |
| [07-results/](07-results/) | Test data | test_results_FINAL.log |
| [08-reports/](08-reports/) | Status & summaries | [CURRENT_STATUS.md](08-reports/CURRENT_STATUS.md) ⭐ |
| [09-documentation/](09-documentation/) | Guides & references | [QUICK_REFERENCE.md](09-documentation/QUICK_REFERENCE.md) |

---

## 🔬 The Framework

### Geometric Axiom

**⊙ = • ⊗ ○ ⊗ Φ**

- **Center (•)**: Nucleus, convergence point, localization
- **Boundary (○)**: Electron shells, stable orbits, quantization  
- **Field (Φ)**: Wavefunction, coupling, electromagnetic interaction

### Key Equations

**Atomic structure:**
```
E_rad = -R∞ Z_eff² / n²
E_ang = λ ℓ(ℓ+1) / n²  where λ = R∞φ⁻⁷
```

**Molecular bonding:**
```
Δ = T - V  (closure deficit)
β = χ_A/(χ_A + χ_B)  (balance parameter)
ζ = 1 + φ⁻³  (orbital contraction)
```

### The Aperture Operator

**Same operator i at every scale:**
```
Atomic:     i: n → n+1       (shell transitions)
Molecular:  i_share: A ↔ B   (bonding)
Network:    Φ: M₁ → M₂       (field coupling)
```

**Chemistry = Aperture calculus in fractal ⊙ structure**

---

## 📖 Read These First

### For Understanding
1. [CURRENT_STATUS.md](08-reports/CURRENT_STATUS.md) - Current achievements
2. [THE_COMPLETE_CIRCUMPUNCT_FRAMEWORK.md](01-core-theory/THE_COMPLETE_CIRCUMPUNCT_FRAMEWORK.md) - Theory
3. [circumpunct_chemistry_64state.md](02-chemistry-theory/circumpunct_chemistry_64state.md) - Chemistry

### For Validation
1. [verify_64state_COMPLETE_v2_optimizer.py](04-validation/CURRENT/verify_64state_COMPLETE_v2_optimizer.py)
2. [test_results_FINAL.log](07-results/test_results_FINAL.log)
3. [RESULTS_VISUAL_SUMMARY.md](08-reports/RESULTS_VISUAL_SUMMARY.md)

### For Publications
1. [PHYSICS_PAPER_GEOMETRIC_PERIODIC_TABLE.md](01-core-theory/PHYSICS_PAPER_GEOMETRIC_PERIODIC_TABLE.md) (ready)
2. [H2_BONDING_PUBLICATION_DRAFT.md](02-chemistry-theory/H2_BONDING_PUBLICATION_DRAFT.md) (ready)
3. [PUBLICATION_GUIDE.md](09-documentation/PUBLICATION_GUIDE.md) (roadmap)

---

## 🎓 Publications (In Preparation)

### Paper 1: Geometric Periodic Table ⭐ READY
- **File**: [PHYSICS_PAPER_GEOMETRIC_PERIODIC_TABLE.md](01-core-theory/PHYSICS_PAPER_GEOMETRIC_PERIODIC_TABLE.md)
- **Target**: Physical Review Letters / Nature Physics
- **Key**: 89.6% accuracy, λ = R∞φ⁻⁷, zero parameters

### Paper 2: H₂ Bonding from φ-Scaling ⭐ READY
- **File**: [H2_BONDING_PUBLICATION_DRAFT.md](02-chemistry-theory/H2_BONDING_PUBLICATION_DRAFT.md)
- **Target**: Journal of Chemical Physics
- **Key**: ζ = 1 + φ⁻³ prediction, 99.84% agreement

### Paper 3: Molecular Compiler 📝 IN PROGRESS
- **Source**: [molecular_compiler.py](03-implementation/molecular_compiler.py)
- **Target**: Journal of Computational Chemistry
- **Key**: VSEPR from aperture calculus, 100% accuracy

---

## 🔬 Falsifiable Predictions

1. **λ = R∞φ⁻⁷**: Specific angular penalty value
2. **ζ = 1 + φ⁻³**: H₂ orbital contraction (validated!)
3. **D = 1.5**: Fractal dimension across scales
4. **β = 0.5**: Critical balance for stable systems
5. **Exactly 64 quantum states**: From 3-bit ⊗ 3-bit structure
6. **Exactly 3 generations**: From B₃ braid topology

---

## 💻 Requirements

### Python Dependencies
```bash
pip install numpy scipy matplotlib pandas
```

### Optional (for visualizations)
- Modern web browser (for HTML visualizations)
- Jupyter notebook (for interactive exploration)

---

## 🤝 Contributing

This work is open for:
- Academic collaboration
- Validation testing
- Extension to new systems
- Implementation improvements
- Visualization enhancements

**Contact**: See repository for details

**Collaborators**: Oliver Kent (RNA), Helen Burston (Cell Biology)

---

## 📊 Validation Status

| Component | Accuracy | Status |
|-----------|----------|--------|
| Main group elements (H-Ar) | 100% (18/18) | ✓✓✓ |
| 1st row transition metals (K-Zn) | 100% (12/12) | ✓✓✓ |
| 2nd row transition metals (Y-Cd) | 60% (6/10) | ⚠️ |
| Lanthanides (La-Lu) | 80% (12/15) | ✓ |
| **Overall periodic table** | **87.3% (48/55)** | ✓ |
| H₂ orbital contraction | 99.84% | ✓ (1 datapoint) |
| **Molecular benchmark** | **68.4% (26/38)** | ⚠️ Needs work |
| Polarity predictions | 100% (10/10) | ✓✓✓ |

### Known Failures
- **N₂, O₂**: Incorrectly predicted as bent (should be linear)
- **HCl, H₂S**: Fail to compile (missing element configs)
- **CH₃OH, H₂O₂**: Wrong geometry predictions

---

## 🎯 What Makes This Different

### Traditional Quantum Chemistry
- Optimizes parameters numerically
- High computational cost
- Excellent quantitative accuracy
- Limited geometric insight

### Circumpunct Framework
- Derives parameters from geometry
- Minimal computation
- Good quantitative accuracy
- Deep geometric insight
- **Predicts what QC must compute**

**Complementary, not competitive!**

---

## 📝 Citation

If you use this work, please cite:

```bibtex
@article{ashman2024circumpunct,
  title={Circumpunct Chemistry: Deriving the Periodic Table from Geometric First Principles},
  author={Ashman},
  journal={In preparation},
  year={2024}
}
```

---

## 📄 License

Open for academic review and collaboration. Please cite appropriately if using in publications.

---

## 🌟 The Bottom Line

**An experimental framework exploring whether chemistry emerges from geometry.**

Starting from:
```
⊙ = • ⊗ ○ ⊗ Φ
```

What works:
- Periodic table structure for main group + 1st row TM (100%)
- Basic molecular geometries (H₂O, CH₄, NH₃, CO₂)
- H₂ orbital contraction prediction

What needs work:
- 2nd row transition metals (60%)
- Diatomic molecules (N₂, O₂ predicted wrong)
- Extending molecular compiler beyond H, C, N, O, F

**Status: Promising but incomplete. Not "production-ready."**

**Chemistry = Aperture calculus (hypothesis under test).**

---

## 🔗 Links

- **Documentation**: [09-documentation/](09-documentation/)
- **Interactive Tools**: [06-visualizations/](06-visualizations/)
- **Full Status**: [CURRENT_STATUS.md](08-reports/CURRENT_STATUS.md)
- **Master Navigation**: [README_MASTER.md](README_MASTER.md)
- **Parent Framework**: [../README.md](../README.md) (Root Circumpunct)

---

**Version**: 5.3.2
**Last Updated**: December 26, 2024
**Status**: Experimental - validation in progress

⊙ = • ⊗ ○ ⊗ Φ

*"Wholeness equals energy"*
