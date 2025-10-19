"""
O3 Gravitational Wave Fractal Dimension Analysis
ONLY VALID EVENTS - GW190412 and GW190425
================================================

Analyzes ONLY the 2 events that are actually in the downloaded files.
GW190521 and GW190814 are NOT in the files and are excluded.

Requirements:
    pip install numpy scipy matplotlib pandas h5py

Usage:
    python analyze_valid_events_only.py
"""

import numpy as np
from scipy import stats, signal as sp_signal
import matplotlib.pyplot as plt
import pandas as pd
import h5py
import json
import os
from datetime import datetime

# ONLY events that are in the files
EVENT_GPS_TIMES_CATALOG = {
    'GW190412': 1239082262.2,
    'GW190425': 1240215503.0,
}

# Map file GPS times to events
FILE_GPS_TO_EVENT = {
    1239080960: 'GW190412',
    1240213455: 'GW190425',
}

# ============================================================================
# 1. HIGUCHI FRACTAL DIMENSION
# ============================================================================

def higuchi_fd(signal_data, k_max=20):
    """Calculate fractal dimension using Higuchi method."""
    N = len(signal_data)
    
    if N < 100:
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
    
    if len(L_k) < 5:
        return np.nan, 0.0
    
    k_values = np.arange(1, len(L_k) + 1)
    log_k = np.log(k_values)
    log_L = np.log(L_k)
    
    slope, intercept, r_value, _, _ = stats.linregress(log_k, log_L)
    
    fd = -slope
    r_squared = r_value ** 2
    
    return fd, r_squared


def calibrate_fd(higuchi_value):
    """
    Convert Higuchi to canonical FD.
    CORRECTED: The old calibration (1.032×H + 0.975) was wrong!
    
    Based on test data:
    - White noise: Higuchi=2.00 → should be D=1.5
    - Sine wave: Higuchi=1.00 → should be D=1.0
    - Brownian: Higuchi=1.52 → should be D=1.5
    
    Correct relationship: D = Higuchi - 0.5
    """
    if np.isnan(higuchi_value):
        return np.nan
    return higuchi_value - 0.5


# ============================================================================
# 2. LOAD AND PROCESS DATA
# ============================================================================

def load_strain_from_hdf5(filename):
    """Load strain data from GWOSC HDF5 file."""
    with h5py.File(filename, 'r') as f:
        strain = f['strain'][:]
        
        sample_rate = f['strain'].attrs.get('sample_rate', 4096.0)
        gps_start = f['strain'].attrs.get('gps_start', 0)
        duration = f['strain'].attrs.get('duration', len(strain) / sample_rate)
        detector = f['strain'].attrs.get('detector', None)
        
        basename = os.path.basename(filename)
        parts = basename.replace('.hdf5', '').split('_')
        
        file_gps = None
        for part in parts:
            if part.startswith('GPS'):
                file_gps = int(part.replace('GPS', ''))
                break
        
        event_name = FILE_GPS_TO_EVENT.get(file_gps, f'GW_GPS{file_gps}')
        
        if detector is None:
            for part in parts:
                if part in ['H1', 'L1', 'V1']:
                    detector = part
                    break
        
        if 'times' in f:
            times_relative = f['times'][:]
            times = gps_start + times_relative
        else:
            times = gps_start + np.arange(len(strain)) / sample_rate
    
    return {
        'strain': strain,
        'times': times,
        'sample_rate': sample_rate,
        'gps_start': gps_start,
        'duration': duration,
        'event': event_name,
        'detector': detector,
        'file_gps': file_gps
    }


def extract_event_window(strain, times, event_gps, window_duration=32):
    """Extract window around event GPS time."""
    half_window = window_duration / 2
    
    mask = (times >= event_gps - half_window) & (times <= event_gps + half_window)
    
    if np.sum(mask) < 100:
        print(f"    ⚠ Warning: Only {np.sum(mask)} samples in window")
        return None, None
    
    strain_window = strain[mask]
    times_window = times[mask]
    
    return strain_window, times_window


def preprocess_strain(strain, sample_rate, f_low=30, f_high=400):
    """Bandpass filter strain data."""
    nyquist = sample_rate / 2
    low = f_low / nyquist
    high = f_high / nyquist
    
    low = max(low, 0.001)
    high = min(high, 0.999)
    
    b, a = sp_signal.butter(4, [low, high], btype='band')
    
    if np.any(np.isnan(strain)) or np.any(np.isinf(strain)):
        print(f"    ⚠ Warning: Input strain contains NaN or Inf values")
        strain = np.nan_to_num(strain, nan=0.0, posinf=0.0, neginf=0.0)
    
    try:
        strain_filtered = sp_signal.filtfilt(b, a, strain)
        
        if np.any(np.isnan(strain_filtered)) or np.any(np.isinf(strain_filtered)):
            print(f"    ⚠ Warning: Filtering produced NaN or Inf values")
            return strain
            
        return strain_filtered
    except Exception as e:
        print(f"    ⚠ Warning: Filtering failed: {e}")
        return strain


def segment_phases(strain, times, event_gps):
    """Segment into inspiral and ringdown using catalog GPS time."""
    peak_idx = np.argmin(np.abs(times - event_gps))
    
    dt = times[1] - times[0] if len(times) > 1 else 1/4096
    
    inspiral_start = max(0, peak_idx - int(0.5 / dt))
    inspiral_end = peak_idx
    
    ringdown_start = peak_idx
    ringdown_end = min(len(strain), peak_idx + int(0.3 / dt))
    
    inspiral = strain[inspiral_start:inspiral_end]
    ringdown = strain[ringdown_start:ringdown_end]
    
    return inspiral, ringdown


# ============================================================================
# 3. ANALYZE SINGLE EVENT
# ============================================================================

def analyze_event_real(filename):
    """Full analysis pipeline for real GWOSC data."""
    data = load_strain_from_hdf5(filename)
    
    event = data['event']
    detector = data['detector']
    
    # Skip if event not in our valid list
    if event not in EVENT_GPS_TIMES_CATALOG:
        print(f"  Skipping {event} {detector} - not in valid event list")
        return None
    
    print(f"  Analyzing {event} {detector}...")
    
    event_gps = EVENT_GPS_TIMES_CATALOG.get(event, None)
    
    if event_gps is None:
        print(f"    ✗ Unknown event in catalog: {event}")
        return None
    
    print(f"    Catalog GPS: {event_gps}")
    print(f"    File GPS: {data['file_gps']}")
    print(f"    File duration: {data['duration']:.1f}s")
    
    # Check if event GPS is within the data range
    data_start = data['times'][0]
    data_end = data['times'][-1]
    
    if not (data_start <= event_gps <= data_end):
        print(f"    ✗ Event GPS {event_gps} not in data range [{data_start}, {data_end}]")
        print(f"    Skipping - event not in file!")
        return None
    
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
    
    if np.all(np.isnan(strain)) or np.all(strain == 0):
        print(f"    ✗ Preprocessing failed - all NaN or zeros")
        return None
    
    # Segment phases
    inspiral, ringdown = segment_phases(strain, times_window, event_gps)
    
    print(f"    Inspiral: {len(inspiral)} samples, Ringdown: {len(ringdown)} samples")
    
    if len(inspiral) < 100 or len(ringdown) < 100:
        print(f"    ⚠ Warning: Phases too short for reliable FD calculation")
    
    if np.all(np.isnan(inspiral)) or np.all(np.isnan(ringdown)):
        print(f"    ✗ Phase data contains all NaN")
        return None
    
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
# 4. BATCH PROCESS
# ============================================================================

def analyze_all_o3_events():
    """Process all downloaded O3 events."""
    print("="*70)
    print("O3 GRAVITATIONAL WAVE FRACTAL DIMENSION ANALYSIS")
    print("Valid Events Only: GW190412 & GW190425")
    print("="*70)
    
    manifest_file = 'gwosc_data/manifest.json'
    
    if not os.path.exists(manifest_file):
        print("✗ No manifest.json found.")
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
    
    df = pd.DataFrame(results)
    df_valid = df.dropna(subset=['D_inspiral', 'D_ringdown'])
    
    print(f"\n✓ Successfully analyzed: {len(df_valid)} observations")
    print(f"  Events: {df_valid['event'].unique()}")
    print(f"  Detectors: {df_valid['detector'].unique()}")
    
    # Save results
    df.to_csv('O3_VALID_events_fractal_analysis.csv', index=False)
    print(f"✓ Results saved to O3_VALID_events_fractal_analysis.csv")
    
    return df_valid if len(df_valid) > 0 else None


# ============================================================================
# 5. STATISTICAL ANALYSIS
# ============================================================================

def analyze_results(df):
    """Statistical analysis."""
    print("\n" + "="*70)
    print("STATISTICAL SUMMARY - VALID EVENTS ONLY")
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
    
    print(f"\n3. BY EVENT")
    for evt in df['event'].unique():
        evt_data = df[df['event'] == evt]
        evt_D = np.concatenate([evt_data['D_inspiral'].values, evt_data['D_ringdown'].values])
        print(f"   {evt}: D = {evt_D.mean():.3f} ± {evt_D.std():.3f} (N={len(evt_data)})")
    
    print(f"\n4. BY DETECTOR")
    for det in df['detector'].unique():
        det_data = df[df['detector'] == det]
        det_D = np.concatenate([det_data['D_inspiral'].values, det_data['D_ringdown'].values])
        print(f"   {det}: D = {det_D.mean():.3f} ± {det_D.std():.3f} (N={len(det_data)})")
    
    print(f"\n5. QUALITY CONTROL")
    pass_rate = df['passed_QC'].sum() / len(df) * 100
    print(f"   Pass rate: {pass_rate:.1f}% ({df['passed_QC'].sum()}/{len(df)})")
    
    print(f"\n6. HYPOTHESIS TEST: H₀: μ = 1.5")
    t_stat, p_value = stats.ttest_1samp(D_all, 1.5)
    print(f"   t-statistic = {t_stat:.3f}")
    print(f"   p-value = {p_value:.4f}")
    result = 'REJECT H₀' if p_value < 0.05 else 'FAIL TO REJECT H₀'
    print(f"   Result: {result} at α=0.05")
    
    if p_value >= 0.05:
        print(f"   ✓ Data consistent with D = 1.5")
    else:
        print(f"   ✗ Data significantly different from D = 1.5")
    
    return df


# ============================================================================
# 7. MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Analyzing VALID O3 events only\n")
    
    df = analyze_all_o3_events()
    
    if df is not None and len(df) > 0:
        df = analyze_results(df)
        
        print("\n" + "="*70)
        print("ANALYSIS COMPLETE")
        print("="*70)
        print("\nOutput: O3_VALID_events_fractal_analysis.csv")
        print("\nNote: Only analyzed events that are actually in the files.")
        print("GW190521 and GW190814 were skipped (not in downloaded data).")
    else:
        print("\n✗ No valid data analyzed")
