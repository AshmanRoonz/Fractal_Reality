"""
O3 Gravitational Wave Fractal Dimension Analysis
FIXED VERSION - Properly extracts event windows from bulk files
================================================

This analyzes the HDF5 files you downloaded from GWOSC.
Uses your proven O1 methodology: Higuchi + fBm calibration.

Requirements:
    pip install numpy scipy matplotlib pandas h5py

Usage:
    python analyze_o3_real_data.py
"""

import numpy as np
from scipy import stats, signal as sp_signal
import matplotlib.pyplot as plt
import pandas as pd
import h5py
import json
import os
from datetime import datetime

# Known event GPS times (from GWOSC)
EVENT_GPS_TIMES = {
    'GW190412': 1239082262.2,
    'GW190425': 1240215503.0,
    'GW190521': 1242442967.4,
    'GW190814': 1249852257.0,
    'GW190915_235702': 1252278640.4,
}

# ============================================================================
# 1. HIGUCHI FRACTAL DIMENSION (Your proven O1 method)
# ============================================================================

def higuchi_fd(signal_data, k_max=20):
    """
    Calculate fractal dimension using Higuchi method.
    Exactly as validated in O1 analysis.
    """
    N = len(signal_data)
    
    if N < 100:  # Need minimum samples
        return np.nan, 0.0
    
    L_k = []
    
    for k in range(1, k_max + 1):
        L_m = []
        for m in range(k):
            indices = np.arange(m, N, k, dtype=int)
            if len(indices) < 2:
                continue
            
            curve_length = 0
            for i in range(1, len(indices)):
                curve_length += abs(signal_data[indices[i]] - signal_data[indices[i-1]])
            
            curve_length *= (N - 1) / ((len(indices) - 1) * k * k)
            L_m.append(curve_length)
        
        if L_m:
            L_k.append(np.mean(L_m))
    
    if len(L_k) < 5:  # Need enough points for regression
        return np.nan, 0.0
    
    # Linear regression on log-log plot
    k_values = np.arange(1, len(L_k) + 1)
    log_k = np.log(k_values)
    log_L = np.log(L_k)
    
    slope, intercept, r_value, _, _ = stats.linregress(log_k, log_L)
    
    fd = -slope
    r_squared = r_value ** 2
    
    return fd, r_squared


def calibrate_fd(higuchi_value):
    """
    Convert Higuchi to canonical FD using O1 calibration.
    
    Calibration from fBm simulations:
        FD_canonical = 1.032 × Higuchi + 0.975
        R² = 0.9943
    """
    if np.isnan(higuchi_value):
        return np.nan
    return 1.032 * higuchi_value + 0.975


# ============================================================================
# 2. LOAD AND EXTRACT EVENT WINDOW FROM BULK FILE
# ============================================================================

def load_strain_from_hdf5(filename):
    """
    Load strain data from downloaded GWOSC HDF5 file.
    """
    with h5py.File(filename, 'r') as f:
        strain = f['strain'][:]
        
        # Get metadata
        sample_rate = 1.0 / f['strain']['Strain'].attrs['Xspacing']
        gps_start = f['strain']['Strain'].attrs['Xstart']
        
        # Try to get event name and detector from attributes
        event_name = f['strain'].attrs.get('event_name', None)
        detector = f['strain'].attrs.get('detector', None)
        
        # If not in attributes, parse from filename
        if event_name is None or detector is None:
            basename = os.path.basename(filename)
            parts = basename.split('_')
            if len(parts) >= 2:
                event_name = parts[0]
                detector = parts[1].replace('.hdf5', '').replace('.hdf', '')
    
    times = gps_start + np.arange(len(strain)) / sample_rate
    
    return {
        'strain': strain,
        'times': times,
        'sample_rate': sample_rate,
        'gps_start': gps_start,
        'event': event_name,
        'detector': detector
    }


def extract_event_window(strain, times, event_gps, window_duration=32):
    """
    Extract a window around the event GPS time from bulk data.
    
    Parameters:
        strain: Full strain timeseries
        times: GPS times for each sample
        event_gps: Event GPS time
        window_duration: Duration in seconds (default 32s, like O1)
    
    Returns:
        strain_window: Extracted strain data
        times_window: Corresponding times
    """
    # Find indices within window
    half_window = window_duration / 2
    
    mask = (times >= event_gps - half_window) & (times <= event_gps + half_window)
    
    if np.sum(mask) < 100:
        print(f"    ⚠ Warning: Only {np.sum(mask)} samples in window")
        return None, None
    
    strain_window = strain[mask]
    times_window = times[mask]
    
    return strain_window, times_window


def preprocess_strain(strain, sample_rate, f_low=20, f_high=400):
    """
    Standard LIGO preprocessing: bandpass filter.
    """
    nyquist = sample_rate / 2
    low = f_low / nyquist
    high = f_high / nyquist
    
    # Ensure values are in valid range
    low = max(low, 0.001)
    high = min(high, 0.999)
    
    b, a = sp_signal.butter(4, [low, high], btype='band')
    strain_filtered = sp_signal.filtfilt(b, a, strain)
    
    return strain_filtered


def segment_phases(strain, times, event_gps):
    """
    Segment into inspiral and ringdown phases.
    Uses event GPS time as reference.
    """
    # Find peak near event time
    center_idx = np.argmin(np.abs(times - event_gps))
    
    # Search for peak within ±2 seconds of event GPS
    search_window = int(2 * (times[1] - times[0]))  # 2 seconds
    start_search = max(0, center_idx - search_window)
    end_search = min(len(strain), center_idx + search_window)
    
    peak_idx_local = np.argmax(np.abs(strain[start_search:end_search]))
    peak_idx = start_search + peak_idx_local
    
    # Define windows
    # Inspiral: -0.5s to peak
    # Ringdown: peak to +0.3s
    dt = times[1] - times[0]
    
    inspiral_start = max(0, peak_idx - int(0.5 / dt))
    inspiral_end = peak_idx
    
    ringdown_start = peak_idx
    ringdown_end = min(len(strain), peak_idx + int(0.3 / dt))
    
    inspiral = strain[inspiral_start:inspiral_end]
    ringdown = strain[ringdown_start:ringdown_end]
    
    return inspiral, ringdown


# ============================================================================
# 3. ANALYZE SINGLE EVENT (Real GWOSC data with proper windowing)
# ============================================================================

def analyze_event_real(filename):
    """
    Full analysis pipeline for real GWOSC data.
    FIXED: Properly extracts event window from bulk files.
    """
    # Load data
    data = load_strain_from_hdf5(filename)
    
    event = data['event']
    detector = data['detector']
    
    print(f"  Analyzing {event} {detector}...")
    
    # Get event GPS time
    event_gps = EVENT_GPS_TIMES.get(event, None)
    
    if event_gps is None:
        print(f"    ✗ Unknown event GPS time for {event}")
        return None
    
    print(f"    Event GPS: {event_gps}")
    
    # Extract 32-second window around event
    strain_window, times_window = extract_event_window(
        data['strain'], 
        data['times'], 
        event_gps, 
        window_duration=32
    )
    
    if strain_window is None:
        print(f"    ✗ Could not extract event window")
        return None
    
    print(f"    Extracted window: {len(strain_window)} samples ({len(strain_window)/data['sample_rate']:.1f}s)")
    
    # Preprocess
    strain = preprocess_strain(strain_window, data['sample_rate'])
    
    # Segment phases
    inspiral, ringdown = segment_phases(strain, times_window, event_gps)
    
    print(f"    Inspiral: {len(inspiral)} samples, Ringdown: {len(ringdown)} samples")
    
    # Calculate Higuchi FD
    D_insp_raw, r2_insp = higuchi_fd(inspiral, k_max=25)
    D_ring_raw, r2_ring = higuchi_fd(ringdown, k_max=25)
    
    # Calibrate to canonical FD
    D_inspiral = calibrate_fd(D_insp_raw)
    D_ringdown = calibrate_fd(D_ring_raw)
    
    # Calculate metrics
    if not np.isnan(D_inspiral) and not np.isnan(D_ringdown):
        FD_drop = D_inspiral - D_ringdown
        FD_drop_pct = (FD_drop / D_inspiral) * 100
    else:
        FD_drop = np.nan
        FD_drop_pct = np.nan
    
    # Quality check
    passed = (FD_drop_pct >= 5.0) or (abs(FD_drop_pct) >= 20.0) if not np.isnan(FD_drop_pct) else False
    
    print(f"    D_insp = {D_inspiral:.3f}, D_ring = {D_ringdown:.3f}, Drop = {FD_drop_pct:.1f}%")
    print(f"    QC: {'PASS' if passed else 'FAIL'}")
    
    return {
        'event': event,
        'detector': detector,
        'D_inspiral': D_inspiral,
        'D_ringdown': D_ringdown,
        'FD_drop': FD_drop,
        'FD_drop_pct': FD_drop_pct,
        'r2_inspiral': r2_insp,
        'r2_ringdown': r2_ring,
        'passed_QC': passed,
        'n_inspiral': len(inspiral),
        'n_ringdown': len(ringdown)
    }


# ============================================================================
# 4. BATCH PROCESS ALL DOWNLOADED FILES
# ============================================================================

def analyze_all_o3_events():
    """
    Process all downloaded O3 events.
    """
    print("="*70)
    print("O3 GRAVITATIONAL WAVE FRACTAL DIMENSION ANALYSIS")
    print("Real GWOSC Data - FIXED VERSION")
    print("="*70)
    
    # Load manifest
    manifest_file = 'gwosc_data/manifest.json'
    
    if not os.path.exists(manifest_file):
        print("✗ No manifest.json found. Run process_downloaded_files.py first.")
        return None
    
    with open(manifest_file, 'r') as f:
        manifest = json.load(f)
    
    print(f"\nFound {len(manifest)} files in manifest")
    print(f"Framework Prediction: D ≈ 1.5\n")
    
    results = []
    
    for entry in manifest:
        filename = entry['filename']
        
        if os.path.exists(filename):
            try:
                result = analyze_event_real(filename)
                if result is not None:
                    results.append(result)
            except Exception as e:
                print(f"  ✗ Error processing {filename}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"  ✗ File not found: {filename}")
    
    if not results:
        print("\n✗ No results generated")
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Remove rows with NaN values for statistical analysis
    df_valid = df.dropna(subset=['D_inspiral', 'D_ringdown'])
    
    print(f"\n✓ Successfully analyzed: {len(df_valid)}/{len(df)} observations")
    
    # Save results
    df.to_csv('O3_real_fractal_analysis_FIXED.csv', index=False)
    print(f"✓ Results saved to O3_real_fractal_analysis_FIXED.csv")
    
    return df_valid if len(df_valid) > 0 else None


# ============================================================================
# 5. STATISTICAL ANALYSIS
# ============================================================================

def analyze_results(df):
    """
    Statistical analysis comparing O3 with O1 baseline.
    """
    print("\n" + "="*70)
    print("STATISTICAL SUMMARY")
    print("="*70)
    
    D_all = np.concatenate([df['D_inspiral'].values, df['D_ringdown'].values])
    
    print(f"\n1. OVERALL FRACTAL DIMENSION")
    print(f"   N = {len(df)} detector observations")
    print(f"   Mean D = {D_all.mean():.3f} ± {D_all.std():.3f}")
    print(f"   Median D = {np.median(D_all):.3f}")
    print(f"   Range: [{D_all.min():.3f}, {D_all.max():.3f}]")
    print(f"   SEM = {D_all.std()/np.sqrt(len(D_all)):.3f}")
    print(f"\n   Framework prediction: D ≈ 1.50")
    print(f"   Deviation: {abs(D_all.mean() - 1.5):.3f}")
    
    print(f"\n2. PHASE COMPARISON")
    print(f"   Inspiral: {df['D_inspiral'].mean():.3f} ± {df['D_inspiral'].std():.3f}")
    print(f"   Ringdown: {df['D_ringdown'].mean():.3f} ± {df['D_ringdown'].std():.3f}")
    print(f"   Expected: Inspiral > Ringdown (rougher → smoother)")
    
    print(f"\n3. DETECTOR COMPARISON")
    for det in df['detector'].unique():
        det_data = df[df['detector'] == det]
        det_D = np.concatenate([det_data['D_inspiral'].values, det_data['D_ringdown'].values])
        print(f"   {det}: D = {det_D.mean():.3f} ± {det_D.std():.3f} (N={len(det_data)})")
    
    print(f"\n4. QUALITY CONTROL")
    pass_rate = df['passed_QC'].sum() / len(df) * 100
    print(f"   Pass rate: {pass_rate:.1f}% ({df['passed_QC'].sum()}/{len(df)})")
    print(f"   O1 comparison: 83.3% (5/6)")
    
    print(f"\n5. HYPOTHESIS TEST: H₀: μ = 1.5")
    t_stat, p_value = stats.ttest_1samp(D_all, 1.5)
    print(f"   t-statistic = {t_stat:.3f}")
    print(f"   p-value = {p_value:.4f}")
    result = 'REJECT H₀' if p_value < 0.05 else 'FAIL TO REJECT H₀'
    print(f"   Result: {result} at α=0.05")
    
    if p_value >= 0.05:
        print(f"   ✓ Data consistent with D = 1.5 (framework prediction)")
    else:
        print(f"   ✗ Data significantly different from D = 1.5")
    
    print(f"\n6. COMPARISON WITH O1 BASELINE")
    print(f"   O1 (N=6):  Mean = 1.578 ± 0.380, SEM = 0.155")
    print(f"   O3 (N={len(df)}): Mean = {D_all.mean():.3f} ± {D_all.std():.3f}, SEM = {D_all.std()/np.sqrt(len(D_all)):.3f}")
    
    if len(df) > 6:
        improvement = 0.155 / (D_all.std()/np.sqrt(len(D_all)))
        print(f"   SEM improvement: {improvement:.1f}×")
    
    return df


# ============================================================================
# 6. VISUALIZATION
# ============================================================================

def create_plots(df):
    """
    Generate publication-quality plots.
    """
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('LIGO O3 Fractal Dimension Analysis (Real GWOSC Data - FIXED)', 
                 fontsize=16, fontweight='bold')
    
    D_all = np.concatenate([df['D_inspiral'].values, df['D_ringdown'].values])
    
    # 1. Distribution
    ax = axes[0, 0]
    ax.hist(D_all, bins=20, alpha=0.7, edgecolor='black', color='steelblue')
    ax.axvline(1.5, color='red', linestyle='--', linewidth=2, label='Prediction: D=1.5')
    ax.axvline(D_all.mean(), color='blue', linestyle='-', linewidth=2, 
               label=f'Measured: {D_all.mean():.3f}')
    ax.set_xlabel('Fractal Dimension D', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title('Distribution (All Phases)', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # 2. Phase comparison
    ax = axes[0, 1]
    ax.scatter(df['D_inspiral'], df['D_ringdown'], alpha=0.6, s=50)
    ax.plot([0.5, 3], [0.5, 3], 'r--', label='D_insp = D_ring')
    ax.axhline(1.5, color='red', linestyle=':', alpha=0.5)
    ax.axvline(1.5, color='red', linestyle=':', alpha=0.5)
    ax.set_xlabel('D (Inspiral)', fontsize=12)
    ax.set_ylabel('D (Ringdown)', fontsize=12)
    ax.set_title('Phase Comparison', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # 3. Event progression
    ax = axes[0, 2]
    x = np.arange(len(df))
    ax.scatter(x, df['D_inspiral'], label='Inspiral', alpha=0.6, s=30)
    ax.scatter(x, df['D_ringdown'], label='Ringdown', alpha=0.6, s=30)
    ax.axhline(1.5, color='red', linestyle='--', label='D=1.5')
    ax.set_xlabel('Observation Index', fontsize=12)
    ax.set_ylabel('Fractal Dimension D', fontsize=12)
    ax.set_title('Event-by-Event Results', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # 4. Detector comparison
    ax = axes[1, 0]
    detectors = sorted(df['detector'].unique())
    detector_means = []
    detector_stds = []
    for det in detectors:
        det_data = df[df['detector'] == det]
        det_D = np.concatenate([det_data['D_inspiral'].values, det_data['D_ringdown'].values])
        detector_means.append(det_D.mean())
        detector_stds.append(det_D.std())
    
    ax.bar(detectors, detector_means, yerr=detector_stds, capsize=10, 
           alpha=0.7, edgecolor='black')
    ax.axhline(1.5, color='red', linestyle='--', linewidth=2, label='D=1.5')
    ax.set_ylabel('Mean Fractal Dimension', fontsize=12)
    ax.set_title('Detector Systematics', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3, axis='y')
    
    # 5. FD drop distribution
    ax = axes[1, 1]
    ax.hist(df['FD_drop_pct'].dropna(), bins=15, alpha=0.7, edgecolor='black', color='coral')
    ax.axvline(5.0, color='red', linestyle='--', label='QC Threshold (5%)')
    ax.set_xlabel('FD Drop (%)', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title('Inspiral → Ringdown Transition', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # 6. Summary statistics
    ax = axes[1, 2]
    ax.axis('off')
    
    t_stat, p_value = stats.ttest_1samp(D_all, 1.5)
    
    summary_text = f"""
O3 ANALYSIS SUMMARY (FIXED)

Sample Size: N = {len(df)} observations

Fractal Dimension:
  Mean:   {D_all.mean():.3f} ± {D_all.std():.3f}
  Median: {np.median(D_all):.3f}
  SEM:    {D_all.std()/np.sqrt(len(D_all)):.3f}

Framework Prediction: 1.500
Deviation: {abs(D_all.mean() - 1.5):.3f}

Phase Analysis:
  Inspiral:  {df['D_inspiral'].mean():.3f} ± {df['D_inspiral'].std():.3f}
  Ringdown:  {df['D_ringdown'].mean():.3f} ± {df['D_ringdown'].std():.3f}

QC Pass Rate: {df['passed_QC'].sum()/len(df)*100:.1f}%

Hypothesis Test (H₀: μ = 1.5):
  t = {t_stat:.3f}
  p = {p_value:.4f}
  {'✓ Consistent' if p_value >= 0.05 else '✗ Different'}

Comparison with O1:
  O1:  1.578 ± 0.380 (N=6)
  O3:  {D_all.mean():.3f} ± {D_all.std():.3f} (N={len(df)})
    """
    
    ax.text(0.1, 0.5, summary_text, fontsize=11, verticalalignment='center',
            family='monospace', 
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    plt.savefig('O3_real_fractal_analysis_FIXED_plots.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Plots saved to O3_real_fractal_analysis_FIXED_plots.png")
    plt.show()


# ============================================================================
# 7. MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Analyzing REAL GWOSC O3 data - FIXED VERSION\n")
    
    # Run analysis
    df = analyze_all_o3_events()
    
    if df is not None and len(df) > 0:
        # Statistical analysis
        df = analyze_results(df)
        
        # Create plots
        create_plots(df)
        
        print("\n" + "="*70)
        print("ANALYSIS COMPLETE")
        print("="*70)
        print("\nOutput files:")
        print("  1. O3_real_fractal_analysis_FIXED.csv (raw data)")
        print("  2. O3_real_fractal_analysis_FIXED_plots.png (visualizations)")
        print("\nNext steps:")
        print("  - Compare O3 vs O1 results")
        print("  - If D ≈ 1.5: Framework validated!")
        print("  - If D ≠ 1.5: Investigate systematic differences")
    else:
        print("\n✗ No valid data analyzed")
        print("   Check that event GPS times are correct in EVENT_GPS_TIMES")
