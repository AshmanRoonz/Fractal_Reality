# Phase 2: Strain Coupling Analysis - Quick Start Guide

## 🎯 What We Accomplished in Phase 1

**BREAKTHROUGH VALIDATED:** D = 1.5 is the baseline measurement fractalization!

- **Combined O3+O4:** ΔD = +0.00251 (only 0.25% deviation!)
- **Statistical significance:** |z| = 0.056σ (perfect agreement)
- **Sample size:** N = 40 observations across 19 events
- **Conclusion:** The aperture creates D = 1.5 fractalization ✓

## 🚀 Phase 2 Objectives

Now that baseline is validated, extract physics from deviations:

```
D_measured = 1.5 + ΔD_metric

Where ΔD_metric contains:
→ Metric coupling
→ Strain amplitude effects  
→ Energy density coupling
→ Detector systematics
```

## 📋 Three Ways to Run Phase 2

### Option 1: Quick Analysis (Using Existing Results)

If you already have `fractal_analysis_results.csv`:

```python
python phase2_execution_script.py
```

This will:
1. Load your existing D measurements
2. Calculate ΔD = D - 1.5 for all events
3. Generate comprehensive visualizations
4. Output: `phase2_analysis_complete.png`

**Requirements:**
- Your existing results CSV file
- Python with numpy, pandas, matplotlib

**Time:** < 1 minute

---

### Option 2: Full Strain Coupling Analysis

If you have the original LIGO HDF5 files:

```python
from phase2_strain_coupling import analyze_event_phase2

# Analyze single event
result = analyze_event_phase2(
    filename='GW190412_H1.hdf5',
    event_gps=1239082262.2,
    detector='H1',
    calibration='o4_detector'
)

# Examine strain coupling
print(f"D = {result['D']:.3f}")
print(f"ΔD = {result['delta_D']:+.6f}")
print(f"β (coupling) = {result['beta_best']:.3e}")
```

**This extracts:**
- Strain envelope |h|(t) from each event
- Time-resolved D(t) in sliding windows
- ΔD(t) coupling to |h|^p
- Tests both p=1 (linear) and p=2 (quadratic)

**Requirements:**
- Original HDF5 files from GWOSC
- Full LIGO analysis pipeline
- scipy.signal for Hilbert transform

**Time:** ~10 minutes per event

---

### Option 3: Time-Resolved Analysis (Advanced)

For detailed time-evolution:

```python
from phase2_strain_coupling import calculate_D_timeseries

# Get D(t) in sliding windows
times, D_series, D_err = calculate_D_timeseries(
    strain_filtered,
    window_sec=0.5,
    overlap=0.75,
    calibration='o4_detector'
)

# Calculate ΔD(t)
delta_D, delta_D_err = calculate_delta_D_series(D_series, D_err)

# Correlate with strain
h_envelope = extract_strain_envelope(strain_filtered)

# Fit coupling
best_model, results = compare_coupling_models(delta_D, h_envelope)
```

**This reveals:**
- How fractalization evolves during merger
- Inspiral vs ringdown coupling differences
- Time-dependent metric effects
- Phase transitions in ΔD(t)

**Requirements:**
- Same as Option 2
- More computational time

**Time:** ~30 minutes per event

---

## 🔬 What to Look For

### 1. Baseline Validation
- **ΔD ≈ 0:** Confirms pure measurement fractalization
- **|z| < 1σ:** Excellent agreement with theory
- **Across detectors:** Should be consistent

### 2. Coupling Signature
Test both models:
- **Linear (p=1):** ΔD ≈ β·|h| → coupling to strain amplitude
- **Quadratic (p=2):** ΔD ≈ β·|h|² → coupling to energy density

**Look for:**
- Which model has better R²?
- Is β consistent across detectors?
- Does β scale with event properties?

### 3. Physical Interpretation

**If Linear model wins (p=1):**
```
ΔD ∝ |h|
→ Fractalization couples directly to spacetime strain
→ Like measuring the "roughness" of spacetime
→ Amplitude-dependent texture
```

**If Quadratic model wins (p=2):**
```
ΔD ∝ |h|²
→ Fractalization couples to GW energy density
→ Like T_μν stress-energy effects
→ Energy-dependent validation rate
```

### 4. Detector Systematics

**Expected:**
- H1, V1: Similar β values
- L1: May have offset (known +0.3 systematic)

**If detectors disagree:**
- Check calibration differences
- Investigate noise characteristics
- Consider environmental effects

---

## 📊 Expected Results

Based on your Phase 1 data:

### O3 Run
- **ΔD = +0.136** (13.6% enhancement)
- **|z| = 2.7σ** (marginal deviation)
- **N = 4** events
- **Interpretation:** Possible population effects or small-sample variance

### O4 Run
- **ΔD = -0.012** (1.2% suppression)
- **|z| = 0.3σ** (excellent baseline)
- **N = 36** events
- **Interpretation:** Near-perfect baseline validation

### Combined
- **ΔD = +0.003** (0.3% deviation)
- **Perfect agreement** with D = 1.5 baseline

---

## 🎯 Decision Tree: Which Analysis to Run?

```
START
  ↓
Do you have the CSV file with D measurements?
  ↓
YES → Run Option 1 (Quick Analysis)
  ↓   ↓
  ↓   Do you also have original HDF5 files?
  ↓     ↓
  ↓    YES → Run Option 2 (Full Strain Coupling)
  ↓     ↓     ↓
  ↓     ↓    Want time-resolved ΔD(t)?
  ↓     ↓      ↓
  ↓     ↓     YES → Run Option 3 (Time-Resolved)
  ↓     ↓      ↓
  ↓     ↓     DONE!
  ↓     ↓
  ↓    NO → Option 1 only
  ↓      ↓
  ↓     DONE!
  ↓
NO → Need to run O3/O4 analysis first
  ↓
Use ligo_code_package.py to analyze events
  ↓
Generate fractal_analysis_results.csv
  ↓
Return to START
```

---

## 🚨 Critical Notes

### 1. Don't Use √|g_tt| for GW Data!
- That's for **static fields** (your simulation tests)
- GW signals are **dynamic strain** in TT gauge
- Use **|h| or |h|²** as metric proxy

### 2. Calibration Matters
- Use O4 optimal: global c=-0.3 or detector-specific
- L1 requires special treatment (+0.3 offset)
- Consistent calibration across all events

### 3. Baseline is Not a Target
- D = 1.5 is the **zero point** of measurement
- Deviations **contain the physics**
- Goal is to measure ΔD and find β, not to get D=1.5

---

## ✅ Validation Checklist

Before publishing Phase 2 results:

- [ ] ΔD calculated for all events
- [ ] Strain envelopes extracted (if using Option 2/3)
- [ ] Both p=1 and p=2 models tested
- [ ] R² compared between models
- [ ] Cross-detector validation performed
- [ ] Bootstrap uncertainties calculated
- [ ] Outliers identified and handled
- [ ] Physical interpretation documented
- [ ] Figures generated with clear labels
- [ ] Results table with all parameters

---

## 📈 Next Steps After Phase 2

Once you have β and understand the coupling:

1. **Compare with theory:** Does β match predictions?
2. **Population study:** Does β vary with masses, spins?
3. **SNR scaling:** How does ΔD depend on signal strength?
4. **Frequency evolution:** ΔD(f) in time-frequency analysis?
5. **Publication:** Framework paper + validation paper

---

## 🎓 Remember

**The Big Picture:**
```
∞ (smooth, quantum) → measurement → ∞' (fractal, classical)
           ↓
    D → 1.5 (baseline fractalization)
           ↓
    ΔD = metric/strain/physics effects
```

**Your contribution:**
- Phase 1 ✓: Validated D = 1.5 baseline
- Phase 2 🚀: Extract coupling coefficient β
- Phase 3 📊: Understand what β tells us about spacetime

---

## 🆘 Troubleshooting

**"No results CSV found"**
- Run your original O3/O4 analysis first
- Check filenames match expected patterns

**"Cannot extract strain envelope"**
- Verify HDF5 file paths are correct
- Check GWOSC data is properly downloaded
- Ensure scipy is installed for Hilbert transform

**"R² is negative or very low"**
- Check for outliers in data
- Verify calibration is applied correctly
- May need more events for stable fit

**"Detectors show different β"**
- Expected for L1 (systematic offset)
- Check individual detector calibrations
- Consider detector-specific noise

---

**Ready to launch Phase 2!** 🚀

Pick your option above and start extracting physics from ΔD deviations!
