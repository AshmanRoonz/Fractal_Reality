"""
Deep analysis of O4 fractal dimension results
Compares with O3 findings and investigates systematic effects
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import glob

# Load most recent results
result_files = glob.glob('O4_fractal_results_*.csv')
if not result_files:
    print("No results files found!")
    exit()

latest_file = sorted(result_files)[-1]
print(f"Analyzing: {latest_file}\n")

df = pd.read_csv(latest_file)

# Remove invalid data
df_valid = df.dropna(subset=['D_full'])

print("="*70)
print("COMPREHENSIVE O4 ANALYSIS")
print("="*70)

# 1. Overall Statistics
print(f"\n1. OVERALL STATISTICS (N={len(df_valid)})")
D_all = df_valid['D_full'].values
print(f"   Mean D:     {D_all.mean():.3f} ± {D_all.std():.3f}")
print(f"   Median D:   {np.median(D_all):.3f}")
print(f"   Mode:       {stats.mode(np.round(D_all, 1), keepdims=True)[0][0]:.1f}")
print(f"   Range:      [{D_all.min():.3f}, {D_all.max():.3f}]")
print(f"   IQR:        [{np.percentile(D_all, 25):.3f}, {np.percentile(D_all, 75):.3f}]")

# 2. Comparison with Framework
print(f"\n2. FRAMEWORK COMPARISON")
print(f"   Prediction:     D = 1.500")
print(f"   Observed:       D = {D_all.mean():.3f}")
print(f"   Deviation:      {D_all.mean() - 1.5:.3f} ({(D_all.mean() - 1.5)/1.5 * 100:.1f}%)")
t_stat, p_value = stats.ttest_1samp(D_all, 1.5)
print(f"   t-test:         t = {t_stat:.3f}, p = {p_value:.4f}")
print(f"   Result:         {'CONSISTENT' if p_value >= 0.05 else 'DIFFERENT'} at α=0.05")

# Test against D=1.3 (observed mean rounded)
t_stat2, p_value2 = stats.ttest_1samp(D_all, 1.3)
print(f"\n   Test vs D=1.3:  p = {p_value2:.4f} ({'consistent' if p_value2 >= 0.05 else 'different'})")

# 3. Detector Analysis
print(f"\n3. DETECTOR COMPARISON")
for detector in ['H1', 'L1', 'V1']:
    det_data = df_valid[df_valid['detector'] == detector]['D_full']
    if len(det_data) > 0:
        print(f"   {detector}: N={len(det_data):2d}, "
              f"Mean={det_data.mean():.3f}±{det_data.std():.3f}, "
              f"Median={det_data.median():.3f}")

# Test if detectors are significantly different
h1_data = df_valid[df_valid['detector'] == 'H1']['D_full'].values
l1_data = df_valid[df_valid['detector'] == 'L1']['D_full'].values
if len(h1_data) > 0 and len(l1_data) > 0:
    t_det, p_det = stats.ttest_ind(h1_data, l1_data)
    print(f"\n   H1 vs L1 t-test: p = {p_det:.4f} ({'same' if p_det >= 0.05 else 'DIFFERENT'})")

# 4. SNR Correlation
print(f"\n4. SNR CORRELATION")
corr_data = df_valid[['network_snr', 'D_full']].dropna()
if len(corr_data) > 1:
    r, p = stats.pearsonr(corr_data['network_snr'], corr_data['D_full'])
    print(f"   Pearson r:      {r:.3f} (p = {p:.4f})")
    print(f"   Interpretation: {'Significant' if p < 0.05 else 'No significant'} correlation")

# 5. Phase Transition Analysis
print(f"\n5. PHASE TRANSITION ANALYSIS")
df_phase = df_valid.dropna(subset=['D_inspiral', 'D_ringdown'])
print(f"   N with phases:  {len(df_phase)}")
print(f"   Inspiral:       {df_phase['D_inspiral'].mean():.3f} ± {df_phase['D_inspiral'].std():.3f}")
print(f"   Ringdown:       {df_phase['D_ringdown'].mean():.3f} ± {df_phase['D_ringdown'].std():.3f}")
print(f"   Mean ΔD:        {df_phase['FD_drop_pct'].mean():.2f}%")
print(f"   QC Pass Rate:   {df_phase['passed_QC'].sum()}/{len(df_phase)} ({df_phase['passed_QC'].mean()*100:.1f}%)")

# Paired t-test for inspiral vs ringdown
if len(df_phase) > 1:
    t_phase, p_phase = stats.ttest_rel(df_phase['D_inspiral'], df_phase['D_ringdown'])
    print(f"   Paired t-test:  p = {p_phase:.4f} ({'different' if p_phase < 0.05 else 'NOT different'})")

# 6. Event-by-event
print(f"\n6. TOP EVENTS BY SNR")
event_summary = df_valid.groupby('event').agg({
    'D_full': ['mean', 'std', 'count'],
    'network_snr': 'first'
}).round(3)
event_summary.columns = ['D_mean', 'D_std', 'N_det', 'SNR']
event_summary = event_summary.sort_values('SNR', ascending=False)
print(event_summary.head(10).to_string())

# 7. Outlier Analysis
print(f"\n7. OUTLIER ANALYSIS")
q1, q3 = np.percentile(D_all, [25, 75])
iqr = q3 - q1
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr
outliers = df_valid[(df_valid['D_full'] < lower_bound) | (df_valid['D_full'] > upper_bound)]
print(f"   IQR bounds:     [{lower_bound:.3f}, {upper_bound:.3f}]")
print(f"   Outliers:       {len(outliers)}/{len(df_valid)} ({len(outliers)/len(df_valid)*100:.1f}%)")
if len(outliers) > 0:
    print(f"\n   Outlier events:")
    for _, row in outliers.iterrows():
        print(f"     {row['event']} {row['detector']}: D={row['D_full']:.3f}, SNR={row['network_snr']:.1f}")

# 8. Create visualizations
print(f"\n8. GENERATING PLOTS...")

fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle('O4 Gravitational Wave Fractal Dimension Analysis\n' +
             f'N={len(df_valid)} observations, Mean D={D_all.mean():.3f}±{D_all.std():.3f}',
             fontsize=14, fontweight='bold')

# Plot 1: Distribution
ax = axes[0, 0]
ax.hist(D_all, bins=20, alpha=0.7, edgecolor='black', color='steelblue')
ax.axvline(1.5, color='red', linestyle='--', linewidth=2, label='Framework: D=1.5')
ax.axvline(D_all.mean(), color='green', linestyle='-', linewidth=2, 
           label=f'Observed: D={D_all.mean():.3f}')
ax.axvline(np.median(D_all), color='orange', linestyle=':', linewidth=2,
           label=f'Median: D={np.median(D_all):.3f}')
ax.set_xlabel('Fractal Dimension', fontsize=11)
ax.set_ylabel('Count', fontsize=11)
ax.set_title('D Distribution', fontsize=12, fontweight='bold')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

# Plot 2: D vs SNR
ax = axes[0, 1]
colors = {'H1': 'red', 'L1': 'blue', 'V1': 'green'}
for detector in ['H1', 'L1', 'V1']:
    det_df = df_valid[df_valid['detector'] == detector]
    if len(det_df) > 0:
        ax.scatter(det_df['network_snr'], det_df['D_full'], 
                  alpha=0.6, s=50, label=detector, color=colors[detector])
ax.axhline(1.5, color='red', linestyle='--', alpha=0.5, label='D=1.5')
ax.set_xlabel('Network SNR', fontsize=11)
ax.set_ylabel('Fractal Dimension', fontsize=11)
ax.set_title('D vs Signal Strength', fontsize=12, fontweight='bold')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

# Plot 3: By Detector (boxplot)
ax = axes[0, 2]
detector_data = []
detector_labels = []
for det in ['H1', 'L1', 'V1']:
    data = df_valid[df_valid['detector'] == det]['D_full'].values
    if len(data) > 0:
        detector_data.append(data)
        detector_labels.append(f"{det}\n(N={len(data)})")

ax.boxplot(detector_data, labels=detector_labels)
ax.axhline(1.5, color='red', linestyle='--', alpha=0.5, label='D=1.5')
ax.set_ylabel('Fractal Dimension', fontsize=11)
ax.set_title('By Detector', fontsize=12, fontweight='bold')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

# Plot 4: Inspiral vs Ringdown
ax = axes[1, 0]
if len(df_phase) > 0:
    x = np.arange(min(len(df_phase), 15))
    width = 0.35
    ax.bar(x - width/2, df_phase['D_inspiral'].iloc[:15], width, 
           label='Inspiral', alpha=0.7, color='skyblue')
    ax.bar(x + width/2, df_phase['D_ringdown'].iloc[:15], width,
           label='Ringdown', alpha=0.7, color='coral')
    ax.axhline(1.5, color='red', linestyle='--', alpha=0.5)
    ax.set_xlabel('Observation', fontsize=11)
    ax.set_ylabel('Fractal Dimension', fontsize=11)
    ax.set_title('Phase Evolution (First 15)', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

# Plot 5: ΔD Distribution
ax = axes[1, 1]
if len(df_phase) > 0:
    ax.hist(df_phase['FD_drop_pct'].dropna(), bins=15, alpha=0.7,
            edgecolor='black', color='coral')
    ax.axvline(5.0, color='red', linestyle='--', label='QC: 5%')
    ax.axvline(df_phase['FD_drop_pct'].mean(), color='green', linestyle='-',
               label=f"Mean: {df_phase['FD_drop_pct'].mean():.1f}%")
    ax.set_xlabel('FD Drop (%)', fontsize=11)
    ax.set_ylabel('Count', fontsize=11)
    ax.set_title('Phase Transition Magnitude', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

# Plot 6: Q-Q Plot (test normality)
ax = axes[1, 2]
stats.probplot(D_all, dist="norm", plot=ax)
ax.set_title('Q-Q Plot (Normality Test)', fontsize=12, fontweight='bold')
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('O4_comprehensive_analysis.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: O4_comprehensive_analysis.png")

# 9. Save summary statistics
summary_stats = {
    'N_observations': len(df_valid),
    'N_events': len(df_valid['event'].unique()),
    'Mean_D': D_all.mean(),
    'Std_D': D_all.std(),
    'Median_D': np.median(D_all),
    'SEM': D_all.std() / np.sqrt(len(D_all)),
    'CI_95_lower': D_all.mean() - 1.96 * D_all.std() / np.sqrt(len(D_all)),
    'CI_95_upper': D_all.mean() + 1.96 * D_all.std() / np.sqrt(len(D_all)),
    'Framework_prediction': 1.5,
    'Deviation': D_all.mean() - 1.5,
    't_statistic': t_stat,
    'p_value': p_value,
    'QC_pass_rate': df_phase['passed_QC'].sum() / len(df_phase) if len(df_phase) > 0 else 0
}

summary_df = pd.DataFrame([summary_stats])
summary_df.to_csv('O4_summary_statistics.csv', index=False)
print(f"   ✓ Saved: O4_summary_statistics.csv")

print(f"\n{'='*70}")
print("ANALYSIS COMPLETE")
print(f"{'='*70}")

# 10. Interpretation
print(f"\n10. INTERPRETATION")
print(f"\nKey Findings:")
print(f"  1. Mean D = {D_all.mean():.3f} is {abs(D_all.mean()-1.5):.3f} below framework prediction")
print(f"  2. Statistical test shows {'significant' if p_value < 0.05 else 'no'} difference from D=1.5")
print(f"  3. Detector variability suggests systematic effects or noise characteristics")
print(f"  4. Phase transitions remain muted (ΔD={df_phase['FD_drop_pct'].mean():.1f}%)")
print(f"\nPossible Explanations:")
print(f"  • Calibration: D = Higuchi - 0.5 may need refinement")
print(f"  • Detector effects: L1 shows consistently lower D values")
print(f"  • Event selection: High-SNR bias toward certain waveform types")
print(f"  • SNR effects: Lower SNR events have noisier measurements")
print(f"\nNext Steps:")
print(f"  • Compare with O1 high-SNR events (GW150914)")
print(f"  • Investigate L1 detector systematic offset")
print(f"  • Test calibration refinement: D = Higuchi - 0.7?")
print(f"  • Expand to N>50 for better statistics")
