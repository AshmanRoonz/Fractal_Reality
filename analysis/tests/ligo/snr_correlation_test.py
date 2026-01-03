#!/usr/bin/env python
"""
SNR vs Fractal Dimension Correlation Test
==========================================

If D≈1.5 is a GW signal property:
- Higher SNR → more signal → D should differ from noise
- Lower SNR → more noise → D should approach noise value

If D≈1.5 is a noise property:
- D should be constant regardless of SNR

This uses existing O4 analysis results.
"""

import pandas as pd
import numpy as np
from scipy import stats

# Load the O4 results
df = pd.read_csv('/home/user/Fractal_Reality/analysis/tests/ligo/O4/O4_fractal_results_20251019_203311.csv')

print("=" * 70)
print("SNR vs FRACTAL DIMENSION CORRELATION ANALYSIS")
print("=" * 70)
print(f"\nLoaded {len(df)} observations")

# Clean data
df_clean = df.dropna(subset=['network_snr', 'D_full'])
print(f"Valid observations: {len(df_clean)}")

# Basic stats
print(f"\nSNR range: {df_clean['network_snr'].min():.1f} - {df_clean['network_snr'].max():.1f}")
print(f"D range: {df_clean['D_full'].min():.3f} - {df_clean['D_full'].max():.3f}")
print(f"D mean: {df_clean['D_full'].mean():.3f} ± {df_clean['D_full'].std():.3f}")

# Correlation analysis
print(f"\n" + "=" * 70)
print("CORRELATION TESTS")
print("=" * 70)

# Pearson correlation
r_pearson, p_pearson = stats.pearsonr(df_clean['network_snr'], df_clean['D_full'])
print(f"\n1. Pearson Correlation (SNR vs D_full):")
print(f"   r = {r_pearson:.3f}")
print(f"   p = {p_pearson:.4f}")

if p_pearson < 0.05:
    print(f"   → SIGNIFICANT correlation (p < 0.05)")
else:
    print(f"   → NO significant correlation (p >= 0.05)")

# Spearman correlation (rank-based, more robust)
r_spearman, p_spearman = stats.spearmanr(df_clean['network_snr'], df_clean['D_full'])
print(f"\n2. Spearman Correlation (rank-based):")
print(f"   rho = {r_spearman:.3f}")
print(f"   p = {p_spearman:.4f}")

# Split by SNR
high_snr = df_clean[df_clean['network_snr'] >= 20]
low_snr = df_clean[df_clean['network_snr'] < 20]

print(f"\n3. SNR Group Comparison:")
print(f"   High SNR (≥20): N={len(high_snr)}, D = {high_snr['D_full'].mean():.3f} ± {high_snr['D_full'].std():.3f}")
print(f"   Low SNR (<20):  N={len(low_snr)}, D = {low_snr['D_full'].mean():.3f} ± {low_snr['D_full'].std():.3f}")

if len(high_snr) > 1 and len(low_snr) > 1:
    t_stat, p_ttest = stats.ttest_ind(high_snr['D_full'], low_snr['D_full'])
    print(f"   t-test: t = {t_stat:.3f}, p = {p_ttest:.4f}")

# Check by detector
print(f"\n4. By Detector:")
for det in ['H1', 'L1', 'V1']:
    det_data = df_clean[df_clean['detector'] == det]
    if len(det_data) > 2:
        r, p = stats.pearsonr(det_data['network_snr'], det_data['D_full'])
        print(f"   {det}: N={len(det_data)}, D={det_data['D_full'].mean():.3f}, r(SNR)={r:.3f}, p={p:.4f}")

# Key interpretation
print(f"\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)

if abs(r_pearson) < 0.3 and p_pearson > 0.05:
    print(f"""
NO CORRELATION between SNR and fractal dimension.

If D≈1.5 were a gravitational wave signal property:
  → Higher SNR (more signal) should give different D than low SNR (more noise)
  → We should see D change systematically with SNR

But D is approximately constant regardless of SNR:
  → High SNR events: D ≈ {high_snr['D_full'].mean():.2f}
  → Low SNR events:  D ≈ {low_snr['D_full'].mean():.2f}
  → Difference: {abs(high_snr['D_full'].mean() - low_snr['D_full'].mean()):.2f}

CONCLUSION: D≈1.5 appears to be a NOISE property, not affected by
the presence or strength of the gravitational wave signal.
""")
else:
    print(f"""
CORRELATION DETECTED: r = {r_pearson:.3f}

This suggests D does change with SNR, which could indicate
the measurement is sensitive to the signal strength.

Further investigation needed.
""")

# Save results
results = {
    'n_observations': len(df_clean),
    'snr_range': [float(df_clean['network_snr'].min()), float(df_clean['network_snr'].max())],
    'D_mean': float(df_clean['D_full'].mean()),
    'D_std': float(df_clean['D_full'].std()),
    'pearson_r': float(r_pearson),
    'pearson_p': float(p_pearson),
    'spearman_rho': float(r_spearman),
    'spearman_p': float(p_spearman),
    'high_snr_D_mean': float(high_snr['D_full'].mean()),
    'low_snr_D_mean': float(low_snr['D_full'].mean()),
    'conclusion': 'noise_dominated' if abs(r_pearson) < 0.3 and p_pearson > 0.05 else 'snr_dependent'
}

import json
with open('snr_correlation_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: snr_correlation_results.json")
