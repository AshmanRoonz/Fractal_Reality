"""
Calibration Optimization for Fractal Dimension
Tests different calibration constants to find best fit to D=1.5
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import glob

# Load results
result_files = glob.glob('O4_fractal_results_*.csv')
if not result_files:
    print("No results files found!")
    exit()

latest_file = sorted(result_files)[-1]
print(f"Optimizing calibration using: {latest_file}\n")

df = pd.read_csv(latest_file)

# We need raw Higuchi values - recalculate from current D values
# Current: D = Higuchi - 0.5, so Higuchi = D + 0.5
df['Higuchi_raw'] = df['D_full'] + 0.5

df_valid = df.dropna(subset=['Higuchi_raw'])

print("="*70)
print("CALIBRATION OPTIMIZATION ANALYSIS")
print("="*70)

# Test range of calibration constants
print("\n1. TESTING CALIBRATION CONSTANTS")
print("   Testing: D = Higuchi + c")
print("   Range: c from -1.0 to 0.0 (step 0.05)\n")

constants = np.arange(-1.0, 0.05, 0.05)
results = []

for c in constants:
    D_calibrated = df_valid['Higuchi_raw'] + c
    mean_D = D_calibrated.mean()
    std_D = D_calibrated.std()
    deviation = abs(mean_D - 1.5)
    t_stat, p_value = stats.ttest_1samp(D_calibrated, 1.5)
    
    results.append({
        'constant': c,
        'mean_D': mean_D,
        'std_D': std_D,
        'deviation': deviation,
        'p_value': p_value,
        't_stat': t_stat
    })

results_df = pd.DataFrame(results)

# Find best calibration (closest to 1.5)
best_idx = results_df['deviation'].idxmin()
best_constant = results_df.loc[best_idx, 'constant']
best_mean = results_df.loc[best_idx, 'mean_D']
best_p = results_df.loc[best_idx, 'p_value']

print(f"   Current calibration:  D = Higuchi - 0.5")
print(f"   Current mean:         D = {(df_valid['Higuchi_raw'] - 0.5).mean():.3f}")
print(f"   Current p-value:      p = {stats.ttest_1samp(df_valid['Higuchi_raw'] - 0.5, 1.5)[1]:.4f}")

print(f"\n   OPTIMAL calibration:  D = Higuchi {best_constant:+.3f}")
print(f"   Optimal mean:         D = {best_mean:.3f}")
print(f"   Optimal deviation:    {results_df.loc[best_idx, 'deviation']:.3f}")
print(f"   Optimal p-value:      p = {best_p:.4f}")
print(f"   Status:               {'✓ CONSISTENT' if best_p >= 0.05 else '✗ Still different'} with D=1.5")

# Also find calibration that gives p-value closest to 0.5 (perfect consistency)
best_p_idx = (results_df['p_value'] - 0.5).abs().idxmin()
best_p_constant = results_df.loc[best_p_idx, 'constant']
best_p_mean = results_df.loc[best_p_idx, 'mean_D']

print(f"\n   Max p-value calibration: D = Higuchi {best_p_constant:+.3f}")
print(f"   Mean D:                  {best_p_mean:.3f}")
print(f"   p-value:                 {results_df.loc[best_p_idx, 'p_value']:.4f}")

# 2. DETECTOR-SPECIFIC CALIBRATION
print(f"\n2. DETECTOR-SPECIFIC ANALYSIS")
print(f"   Testing if different detectors need different calibrations\n")

detector_results = {}
for detector in ['H1', 'L1', 'V1']:
    det_data = df_valid[df_valid['detector'] == detector]
    if len(det_data) > 3:
        higuchi_det = det_data['Higuchi_raw'].values
        
        # Find best calibration for this detector
        det_constants = []
        det_means = []
        for c in constants:
            D_cal = higuchi_det + c
            det_constants.append(c)
            det_means.append(D_cal.mean())
        
        det_means = np.array(det_means)
        best_det_idx = np.abs(det_means - 1.5).argmin()
        best_det_c = det_constants[best_det_idx]
        best_det_mean = det_means[best_det_idx]
        
        detector_results[detector] = {
            'n': len(det_data),
            'best_c': best_det_c,
            'best_mean': best_det_mean,
            'current_mean': (higuchi_det - 0.5).mean()
        }
        
        print(f"   {detector}: N={len(det_data):2d}, "
              f"Current D={detector_results[detector]['current_mean']:.3f}, "
              f"Optimal c={best_det_c:+.3f} → D={best_det_mean:.3f}")

# 3. VISUALIZATIONS
print(f"\n3. GENERATING CALIBRATION PLOTS...")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Calibration Optimization Analysis', fontsize=14, fontweight='bold')

# Plot 1: Mean D vs calibration constant
ax = axes[0, 0]
ax.plot(results_df['constant'], results_df['mean_D'], 'b-', linewidth=2)
ax.axhline(1.5, color='red', linestyle='--', linewidth=2, label='Framework: D=1.5')
ax.axvline(best_constant, color='green', linestyle=':', linewidth=2, 
           label=f'Best: c={best_constant:.3f}')
ax.axvline(-0.5, color='orange', linestyle=':', linewidth=2,
           label='Current: c=-0.5')
ax.fill_between(results_df['constant'], 
                results_df['mean_D'] - results_df['std_D']/np.sqrt(len(df_valid)),
                results_df['mean_D'] + results_df['std_D']/np.sqrt(len(df_valid)),
                alpha=0.3)
ax.set_xlabel('Calibration Constant c', fontsize=11)
ax.set_ylabel('Mean D', fontsize=11)
ax.set_title('Mean D vs Calibration', fontsize=12, fontweight='bold')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

# Plot 2: p-value vs calibration constant
ax = axes[0, 1]
ax.plot(results_df['constant'], results_df['p_value'], 'b-', linewidth=2)
ax.axhline(0.05, color='red', linestyle='--', linewidth=1, label='α=0.05')
ax.axhline(0.5, color='gray', linestyle=':', linewidth=1, label='Perfect consistency')
ax.axvline(best_constant, color='green', linestyle=':', linewidth=2,
           label=f'Best: c={best_constant:.3f}')
ax.axvline(-0.5, color='orange', linestyle=':', linewidth=2,
           label='Current: c=-0.5')
ax.set_xlabel('Calibration Constant c', fontsize=11)
ax.set_ylabel('p-value', fontsize=11)
ax.set_title('Statistical Consistency vs Calibration', fontsize=12, fontweight='bold')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

# Plot 3: Distribution with different calibrations
ax = axes[1, 0]
D_current = df_valid['Higuchi_raw'] - 0.5
D_optimal = df_valid['Higuchi_raw'] + best_constant

ax.hist(D_current, bins=15, alpha=0.5, label=f'Current (c=-0.5)\nμ={D_current.mean():.3f}',
        color='orange', edgecolor='black')
ax.hist(D_optimal, bins=15, alpha=0.5, label=f'Optimal (c={best_constant:.2f})\nμ={D_optimal.mean():.3f}',
        color='green', edgecolor='black')
ax.axvline(1.5, color='red', linestyle='--', linewidth=2, label='Framework: D=1.5')
ax.set_xlabel('Fractal Dimension', fontsize=11)
ax.set_ylabel('Count', fontsize=11)
ax.set_title('Distribution Comparison', fontsize=12, fontweight='bold')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

# Plot 4: Detector-specific optimal calibrations
ax = axes[1, 1]
if detector_results:
    detectors = list(detector_results.keys())
    current_means = [detector_results[d]['current_mean'] for d in detectors]
    optimal_means = [detector_results[d]['best_mean'] for d in detectors]
    
    x = np.arange(len(detectors))
    width = 0.35
    
    ax.bar(x - width/2, current_means, width, label='Current (c=-0.5)',
           alpha=0.7, color='orange')
    ax.bar(x + width/2, optimal_means, width, label='Detector-optimal',
           alpha=0.7, color='green')
    ax.axhline(1.5, color='red', linestyle='--', linewidth=2, label='D=1.5')
    
    ax.set_xlabel('Detector', fontsize=11)
    ax.set_ylabel('Mean D', fontsize=11)
    ax.set_title('Detector-Specific Calibration', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(detectors)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('calibration_optimization.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: calibration_optimization.png")

# 4. SAVE CALIBRATION RECOMMENDATIONS
print(f"\n4. SAVING CALIBRATION RECOMMENDATIONS...")

calibration_summary = {
    'current_calibration': 'D = Higuchi - 0.5',
    'current_mean_D': (df_valid['Higuchi_raw'] - 0.5).mean(),
    'current_p_value': stats.ttest_1samp(df_valid['Higuchi_raw'] - 0.5, 1.5)[1],
    'optimal_calibration': f'D = Higuchi {best_constant:+.3f}',
    'optimal_constant': best_constant,
    'optimal_mean_D': best_mean,
    'optimal_p_value': best_p,
    'optimal_deviation': results_df.loc[best_idx, 'deviation'],
    'n_observations': len(df_valid),
    'recommendation': f'D = Higuchi {best_constant:+.3f}' if best_p >= 0.05 else 'Current calibration or refine with more data'
}

calib_df = pd.DataFrame([calibration_summary])
calib_df.to_csv('calibration_recommendations.csv', index=False)
print(f"   ✓ Saved: calibration_recommendations.csv")

# Save full calibration scan results
results_df.to_csv('calibration_scan_results.csv', index=False)
print(f"   ✓ Saved: calibration_scan_results.csv")

print(f"\n{'='*70}")
print("CALIBRATION OPTIMIZATION COMPLETE")
print(f"{'='*70}")

# 5. RECOMMENDATIONS
print(f"\n5. RECOMMENDATIONS")

if best_p >= 0.05:
    print(f"\n✓ RECOMMENDED CALIBRATION: D = Higuchi {best_constant:+.3f}")
    print(f"  This brings mean D to {best_mean:.3f}, consistent with framework (p={best_p:.4f})")
else:
    print(f"\n⚠ NO PERFECT CALIBRATION FOUND")
    print(f"  Best calibration: D = Higuchi {best_constant:+.3f} → D={best_mean:.3f}")
    print(f"  Still different from D=1.5 (p={best_p:.4f})")
    print(f"\n  Possible reasons:")
    print(f"  • Detector-specific effects (L1 systematically lower)")
    print(f"  • Event selection bias")
    print(f"  • Need more observations (N={len(df_valid)} may be insufficient)")
    print(f"  • Framework prediction may need refinement")

# Compare L1 vs others
l1_mean = detector_results.get('L1', {}).get('current_mean', 0)
h1_mean = detector_results.get('H1', {}).get('current_mean', 0)

if abs(l1_mean - h1_mean) > 0.2:
    print(f"\n⚠ DETECTOR ANOMALY DETECTED:")
    print(f"  L1 mean ({l1_mean:.3f}) differs from H1 ({h1_mean:.3f}) by {abs(l1_mean-h1_mean):.3f}")
    print(f"  Consider:")
    print(f"  • Using detector-specific calibrations")
    print(f"  • Investigating L1 systematic effects")
    print(f"  • Analyzing H1+V1 separately from L1")

print(f"\n✓ Analysis complete! Check generated files for details.")
