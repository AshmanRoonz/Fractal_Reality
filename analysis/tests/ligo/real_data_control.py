#!/usr/bin/env python
"""
LIGO Real Data Noise Control Experiment
========================================

Downloads REAL LIGO data from:
1. Event windows (with GW signal)
2. Non-event windows (pure detector noise)

Compares fractal dimension to determine if D≈1.5 is signal or noise.

Uses GWOSC API v2 for data access.
"""

import numpy as np
from scipy import stats, signal as sp_signal
import h5py
import requests
import os
from datetime import datetime
from pathlib import Path
import json

# ============================================================================
# GWOSC DATA ACCESS (from o4_pipeline_v2.py)
# ============================================================================

GWOSC_BASE_URL = "https://gwosc.org/api/v2"

def download_strain_for_gps(gps_time, detector, duration=32, output_dir='control_data'):
    """
    Download strain data for ANY GPS time (not just events).
    Uses bulk strain files endpoint.
    """
    Path(output_dir).mkdir(exist_ok=True)

    start_time = int(gps_time - duration/2)
    filename = f"{output_dir}/{detector}_{start_time}_{duration}s.hdf5"

    if os.path.exists(filename):
        print(f"  Using cached: {filename}")
        return filename

    print(f"  Downloading {detector} data for GPS {gps_time}...")

    # Use bulk strain files endpoint
    url = f"{GWOSC_BASE_URL}/strain-files"
    params = {
        'detector': detector,
        'gps-time': int(gps_time),
        'sample-rate': 4,
        'file-format': 'hdf5'
    }

    try:
        response = requests.get(url, params=params, timeout=30)

        if response.status_code != 200:
            print(f"  API error: {response.status_code}")
            return None

        data = response.json()

        if 'results' not in data or len(data['results']) == 0:
            print(f"  No files found for GPS {gps_time}")
            return None

        # Get download URL
        file_info = data['results'][0]
        download_url = file_info.get('download_url') or file_info.get('hdf5_url')

        if not download_url:
            print(f"  No download URL found")
            return None

        print(f"  Downloading from: {download_url[:60]}...")
        file_response = requests.get(download_url, timeout=120)

        if file_response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(file_response.content)
            print(f"  ✓ Saved to {filename}")
            return filename
        else:
            print(f"  Download failed: {file_response.status_code}")
            return None

    except Exception as e:
        print(f"  Error: {e}")
        return None


def download_event_data(event_name, detector, output_dir='control_data'):
    """Download data for a specific event using event endpoint."""
    Path(output_dir).mkdir(exist_ok=True)

    filename = f"{output_dir}/{event_name}_{detector}.hdf5"

    if os.path.exists(filename):
        print(f"  Using cached: {filename}")
        return filename

    print(f"  Downloading {event_name} {detector}...")

    url = f"{GWOSC_BASE_URL}/event-versions/{event_name}/strain-files"
    params = {
        'detector': detector,
        'sample-rate': 4,
        'file-format': 'hdf5'
    }

    try:
        response = requests.get(url, params=params, timeout=30)

        if response.status_code != 200:
            print(f"  API error: {response.status_code}")
            return None

        data = response.json()
        results = data.get('results', data if isinstance(data, list) else [])

        if len(results) == 0:
            print(f"  No files found")
            return None

        download_url = results[0].get('download_url')

        if not download_url:
            print(f"  No download URL")
            return None

        print(f"  Downloading...")
        file_response = requests.get(download_url, timeout=120)

        if file_response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(file_response.content)
            print(f"  ✓ Saved to {filename}")
            return filename
        else:
            print(f"  Download failed: {file_response.status_code}")
            return None

    except Exception as e:
        print(f"  Error: {e}")
        return None


# ============================================================================
# HIGUCHI FRACTAL DIMENSION
# ============================================================================

def higuchi_fd(signal_data, k_max=25):
    """Calculate Higuchi fractal dimension."""
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

    return -slope, r_value ** 2


def calibrate_fd(higuchi_value, method='o4'):
    """Apply calibration."""
    if np.isnan(higuchi_value):
        return np.nan
    if method == 'o4':
        return higuchi_value - 0.3
    elif method == 'o3':
        return higuchi_value - 0.5
    return higuchi_value


# ============================================================================
# SIGNAL PROCESSING
# ============================================================================

def load_strain(filename):
    """Load strain data from HDF5 file."""
    with h5py.File(filename, 'r') as f:
        # Try different HDF5 structures
        if 'strain' in f and 'Strain' in f['strain']:
            strain = f['strain']['Strain'][:]
        elif 'strain' in f:
            strain = f['strain'][:]
        else:
            raise ValueError("Cannot find strain data in file")

        # Get GPS start time
        try:
            if 'meta' in f and 'GPSstart' in f['meta']:
                gps_start = f['meta']['GPSstart'][()]
            elif 'strain' in f and 'Strain' in f['strain']:
                gps_start = f['strain']['Strain'].attrs.get('GPSstart', 0)
            else:
                gps_start = 0
        except:
            gps_start = 0

        sample_rate = 4096

    return strain, gps_start, sample_rate


def bandpass_filter(data, fs=4096, f_low=30, f_high=400):
    """Apply bandpass filter."""
    sos = sp_signal.butter(4, [f_low, f_high], btype='band', fs=fs, output='sos')
    return sp_signal.sosfilt(sos, data)


def analyze_strain_segment(strain, fs=4096, label=""):
    """
    Analyze a segment of strain data.
    Returns fractal dimension and statistics.
    """
    # Apply bandpass filter
    strain_filtered = bandpass_filter(strain, fs)

    # Calculate on full segment
    D_raw, r2 = higuchi_fd(strain_filtered, k_max=25)
    D_cal = calibrate_fd(D_raw)

    # Also calculate on 1-second windows for variance
    window_samples = fs  # 1 second
    n_windows = len(strain_filtered) // window_samples

    D_values = []
    for i in range(n_windows):
        start = i * window_samples
        end = start + window_samples
        segment = strain_filtered[start:end]

        if len(segment) >= 100:
            d_raw, _ = higuchi_fd(segment, k_max=25)
            d_cal = calibrate_fd(d_raw)
            if not np.isnan(d_cal):
                D_values.append(d_cal)

    return {
        'label': label,
        'n_samples': len(strain),
        'duration_s': len(strain) / fs,
        'D_full': D_cal,
        'D_raw': D_raw,
        'r2': r2,
        'n_windows': len(D_values),
        'D_mean': np.mean(D_values) if D_values else np.nan,
        'D_std': np.std(D_values) if D_values else np.nan,
        'D_values': D_values
    }


# ============================================================================
# MAIN CONTROL EXPERIMENT
# ============================================================================

def run_real_data_control():
    """
    Run control experiment with REAL LIGO data.

    Strategy:
    1. Download GW150914 event data (strong signal, SNR~24)
    2. Extract on-source window (around merger)
    3. Extract off-source windows (before event = pure noise)
    4. Compare fractal dimensions
    """
    print("=" * 70)
    print("LIGO REAL DATA NOISE CONTROL EXPERIMENT")
    print("=" * 70)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nObjective: Determine if D≈1.5 is signal or noise property")

    results = []

    # Event parameters
    EVENT = "GW150914"
    DETECTOR = "H1"
    MERGER_GPS = 1126259462.4

    print(f"\n1. DOWNLOADING EVENT DATA: {EVENT} {DETECTOR}")
    print("-" * 50)

    # Try to download event data
    event_file = download_event_data(EVENT, DETECTOR)

    if event_file is None:
        print("\nFailed to download event data. Trying bulk strain...")
        event_file = download_strain_for_gps(MERGER_GPS, DETECTOR)

    if event_file is None:
        print("\n✗ Could not download LIGO data")
        print("  Network may be blocked or GWOSC unavailable")
        return None

    # Load the data
    print(f"\n2. LOADING AND ANALYZING DATA")
    print("-" * 50)

    strain, gps_start, fs = load_strain(event_file)
    print(f"  Loaded {len(strain)} samples ({len(strain)/fs:.1f}s)")
    print(f"  GPS start: {gps_start}")

    # Create time array
    times = gps_start + np.arange(len(strain)) / fs

    # Find merger index
    merger_idx = np.argmin(np.abs(times - MERGER_GPS))
    print(f"  Merger at index: {merger_idx}")

    # Define analysis windows
    window_duration = 2.0  # seconds
    window_samples = int(window_duration * fs)

    # ON-SOURCE: Window centered on merger
    print(f"\n3. ON-SOURCE ANALYSIS (event window)")
    print("-" * 50)

    on_start = max(0, merger_idx - window_samples // 2)
    on_end = min(len(strain), merger_idx + window_samples // 2)
    on_source = strain[on_start:on_end]

    result_on = analyze_strain_segment(on_source, fs, "ON-SOURCE (GW event)")
    results.append(result_on)
    print(f"  Duration: {result_on['duration_s']:.2f}s")
    print(f"  D (full):     {result_on['D_full']:.3f}")
    print(f"  D (windows):  {result_on['D_mean']:.3f} ± {result_on['D_std']:.3f}")

    # OFF-SOURCE: Before event (10-12 seconds before)
    print(f"\n4. OFF-SOURCE ANALYSIS (noise - before event)")
    print("-" * 50)

    off_start = max(0, merger_idx - int(12 * fs))
    off_end = merger_idx - int(10 * fs)
    off_source_before = strain[off_start:off_end]

    result_off_before = analyze_strain_segment(off_source_before, fs,
                                               "OFF-SOURCE (before)")
    results.append(result_off_before)
    print(f"  Duration: {result_off_before['duration_s']:.2f}s")
    print(f"  D (full):     {result_off_before['D_full']:.3f}")
    print(f"  D (windows):  {result_off_before['D_mean']:.3f} ± {result_off_before['D_std']:.3f}")

    # OFF-SOURCE: After event (10-12 seconds after)
    print(f"\n5. OFF-SOURCE ANALYSIS (noise - after event)")
    print("-" * 50)

    off_start_2 = merger_idx + int(10 * fs)
    off_end_2 = min(len(strain), merger_idx + int(12 * fs))
    off_source_after = strain[off_start_2:off_end_2]

    result_off_after = analyze_strain_segment(off_source_after, fs,
                                              "OFF-SOURCE (after)")
    results.append(result_off_after)
    print(f"  Duration: {result_off_after['duration_s']:.2f}s")
    print(f"  D (full):     {result_off_after['D_full']:.3f}")
    print(f"  D (windows):  {result_off_after['D_mean']:.3f} ± {result_off_after['D_std']:.3f}")

    # FAR OFF-SOURCE: 100 seconds before
    print(f"\n6. FAR OFF-SOURCE ANALYSIS (100s before event)")
    print("-" * 50)

    far_start = max(0, merger_idx - int(102 * fs))
    far_end = max(0, merger_idx - int(100 * fs))

    if far_end > far_start and far_end - far_start >= fs:
        far_noise = strain[far_start:far_end]
        result_far = analyze_strain_segment(far_noise, fs,
                                           "FAR OFF-SOURCE (100s before)")
        results.append(result_far)
        print(f"  Duration: {result_far['duration_s']:.2f}s")
        print(f"  D (full):     {result_far['D_full']:.3f}")
        print(f"  D (windows):  {result_far['D_mean']:.3f} ± {result_far['D_std']:.3f}")
    else:
        print("  Not enough data before event")
        result_far = None

    # COMPARISON
    print(f"\n" + "=" * 70)
    print("COMPARISON: EVENT vs NOISE")
    print("=" * 70)

    print(f"\n{'Window':<30} {'D (full)':<12} {'D (mean)':<12} {'D (std)':<10}")
    print("-" * 65)
    for r in results:
        print(f"{r['label']:<30} {r['D_full']:<12.3f} {r['D_mean']:<12.3f} {r['D_std']:<10.3f}")

    # Calculate key metrics
    D_event = result_on['D_mean']
    noise_Ds = [r['D_mean'] for r in results[1:] if not np.isnan(r['D_mean'])]
    D_noise_avg = np.mean(noise_Ds) if noise_Ds else np.nan

    print(f"\n" + "=" * 70)
    print("CRITICAL RESULT")
    print("=" * 70)

    if not np.isnan(D_event) and not np.isnan(D_noise_avg):
        diff = D_event - D_noise_avg
        diff_pct = 100 * diff / D_noise_avg

        print(f"\n  D (event window):   {D_event:.3f}")
        print(f"  D (noise average):  {D_noise_avg:.3f}")
        print(f"  Difference:         {diff:.3f} ({diff_pct:+.1f}%)")

        # Statistical test
        event_values = result_on['D_values']
        noise_values = []
        for r in results[1:]:
            noise_values.extend(r['D_values'])

        if len(event_values) > 2 and len(noise_values) > 2:
            t_stat, p_value = stats.ttest_ind(event_values, noise_values)
            print(f"\n  t-test: t={t_stat:.3f}, p={p_value:.4f}")

            if p_value < 0.05:
                print(f"  ✓ SIGNIFICANT difference (p < 0.05)")
            else:
                print(f"  ✗ NOT significant (p >= 0.05)")

        print(f"\n" + "=" * 70)
        print("CONCLUSION")
        print("=" * 70)

        if abs(diff) < 0.1 and (not 'p_value' in dir() or p_value >= 0.05):
            print(f"""
  RESULT: D(event) ≈ D(noise)

  The fractal dimension during the GW event is NOT significantly
  different from the detector noise.

  D ≈ 1.5 appears to be a NOISE property, not a GW signal property.

  The original LIGO fractal analysis was measuring detector noise
  characteristics, not gravitational wave properties.
""")
            conclusion = "noise_dominated"
        else:
            print(f"""
  RESULT: D(event) ≠ D(noise)

  There IS a measurable difference in fractal dimension between
  the GW event window and pure noise.

  This suggests gravitational waves may have distinct fractal
  properties that differ from detector noise.
""")
            conclusion = "signal_detected"
    else:
        print("\n  Could not complete comparison (missing data)")
        conclusion = "incomplete"

    # Save results
    output = {
        'timestamp': datetime.now().isoformat(),
        'event': EVENT,
        'detector': DETECTOR,
        'merger_gps': MERGER_GPS,
        'results': [{k: v for k, v in r.items() if k != 'D_values'} for r in results],
        'comparison': {
            'D_event': D_event,
            'D_noise_avg': D_noise_avg,
            'difference': diff if not np.isnan(D_event) else None,
            'conclusion': conclusion
        }
    }

    output_file = "real_data_control_results.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")

    return results


if __name__ == "__main__":
    run_real_data_control()
