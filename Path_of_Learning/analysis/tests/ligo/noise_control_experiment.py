#!/usr/bin/env python
"""
LIGO Noise Control Experiment
=============================
Critical test: Does D ≈ 1.5 come from GW signals or detector noise?

This script downloads LIGO data from:
1. Event windows (with GW signal)
2. Non-event windows (pure detector noise - control)

And compares the fractal dimension of both to determine if D ≈ 1.5
is a property of gravitational waves or just detector noise.

If D_noise ≈ D_event ≈ 1.5, then we're just measuring noise.
If D_event ≠ D_noise, then there's a real signal effect.
"""

import numpy as np
from scipy import stats, signal as sp_signal
import json
import io
import os
from datetime import datetime

# Try to import gwosc for real data
try:
    from gwosc.locate import get_event_urls
    import requests
    import h5py
    GWOSC_AVAILABLE = True
except ImportError:
    GWOSC_AVAILABLE = False
    print("WARNING: gwosc not available, will use cached data if present")


# ============================================================================
# 1. HIGUCHI FRACTAL DIMENSION (same algorithm used in main analysis)
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

    fd = -slope
    r_squared = r_value ** 2

    return fd, r_squared


def calibrate_fd(higuchi_value, method='o4_optimal'):
    """Apply calibration to raw Higuchi value."""
    if np.isnan(higuchi_value):
        return np.nan
    if method == 'o4_optimal':
        return higuchi_value - 0.3
    elif method == 'o3_corrected':
        return higuchi_value - 0.5
    else:
        return higuchi_value


# ============================================================================
# 2. SIGNAL PROCESSING
# ============================================================================

def bandpass_filter(data, fs=4096, f_low=30, f_high=400):
    """Apply bandpass filter (same as main analysis)."""
    nyquist = fs / 2
    low = max(f_low / nyquist, 0.001)
    high = min(f_high / nyquist, 0.999)

    b, a = sp_signal.butter(4, [low, high], btype='band')

    try:
        filtered = sp_signal.filtfilt(b, a, data)
        return filtered
    except:
        return data


# ============================================================================
# 3. DATA DOWNLOAD FUNCTIONS
# ============================================================================

def download_gwosc_data(event, detector):
    """Download strain data from GWOSC for a specific event."""
    if not GWOSC_AVAILABLE:
        raise RuntimeError("gwosc library not available")

    urls = get_event_urls(event, detector=detector)
    h5_urls = [u for u in urls if u.lower().endswith(".hdf5")]

    if not h5_urls:
        raise RuntimeError(f"No HDF5 URLs found for {event} {detector}")

    # Sort by length (shorter URLs tend to be simpler)
    h5_urls.sort(key=lambda u: len(u))
    url = h5_urls[0]

    print(f"  Downloading {event} {detector}...")
    print(f"  URL: {url[:80]}...")

    r = requests.get(url, timeout=60)
    r.raise_for_status()

    with h5py.File(io.BytesIO(r.content), "r") as f:
        strain = f["strain"]["Strain"][:]
        fs = float(f["strain"]["Strain"].attrs.get("SampleRate", 4096.0))
        gps_start = float(f["strain"]["Strain"].attrs.get("GPSstart", 0))

    return strain, fs, gps_start


def download_bulk_strain(gps_start, gps_end, detector="H1"):
    """
    Download bulk strain data for arbitrary GPS time range.
    Uses GWOSC timeline API.
    """
    if not GWOSC_AVAILABLE:
        raise RuntimeError("gwosc library not available")

    # GWOSC bulk data URL format
    # Note: This requires the gwosc timeline API
    from gwosc import datasets
    from gwosc.locate import get_urls

    print(f"  Fetching data for GPS {gps_start} to {gps_end}, detector {detector}")

    try:
        urls = get_urls(detector, gps_start, gps_end)
        if not urls:
            raise RuntimeError("No URLs found for time range")

        url = urls[0]
        print(f"  URL: {url[:80]}...")

        r = requests.get(url, timeout=60)
        r.raise_for_status()

        with h5py.File(io.BytesIO(r.content), "r") as f:
            strain = f["strain"]["Strain"][:]
            fs = float(f["strain"]["Strain"].attrs.get("SampleRate", 4096.0))

        return strain, fs
    except Exception as e:
        print(f"  Error: {e}")
        raise


# ============================================================================
# 4. ANALYZE A DATA SEGMENT
# ============================================================================

def analyze_segment(strain, fs, window_seconds=1.0, label="unknown"):
    """
    Analyze a segment of strain data.
    Returns fractal dimension statistics.
    """
    # Apply bandpass filter
    strain_filtered = bandpass_filter(strain, fs)

    # Calculate Higuchi FD on full segment
    D_raw, r2 = higuchi_fd(strain_filtered, k_max=25)
    D_calibrated = calibrate_fd(D_raw)

    # Also calculate on multiple sub-windows for statistics
    samples_per_window = int(window_seconds * fs)
    n_windows = len(strain_filtered) // samples_per_window

    D_values = []
    for i in range(n_windows):
        start = i * samples_per_window
        end = start + samples_per_window
        segment = strain_filtered[start:end]

        if len(segment) >= 100:
            D_raw_seg, r2_seg = higuchi_fd(segment, k_max=25)
            D_cal_seg = calibrate_fd(D_raw_seg)
            if not np.isnan(D_cal_seg):
                D_values.append(D_cal_seg)

    return {
        'label': label,
        'n_samples': len(strain),
        'duration_s': len(strain) / fs,
        'D_full': D_calibrated,
        'D_raw_full': D_raw,
        'r2_full': r2,
        'n_windows': len(D_values),
        'D_mean': np.mean(D_values) if D_values else np.nan,
        'D_std': np.std(D_values) if D_values else np.nan,
        'D_min': np.min(D_values) if D_values else np.nan,
        'D_max': np.max(D_values) if D_values else np.nan,
    }


# ============================================================================
# 5. MAIN EXPERIMENT
# ============================================================================

def run_control_experiment():
    """
    Run the noise control experiment.

    Strategy:
    1. Download GW150914 data (event with clear signal)
    2. Analyze event window (around merger)
    3. Analyze off-source windows (before/after event = pure noise)
    4. Compare fractal dimensions
    """
    print("=" * 70)
    print("LIGO NOISE CONTROL EXPERIMENT")
    print("=" * 70)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nQuestion: Is D ≈ 1.5 a property of GW signals or detector noise?")
    print("\nMethod:")
    print("  1. Download LIGO data containing GW150914")
    print("  2. Analyze ON-SOURCE window (around merger)")
    print("  3. Analyze OFF-SOURCE windows (pure detector noise)")
    print("  4. Compare fractal dimensions")
    print()

    results = []

    # Known event parameters
    EVENT = "GW150914"
    DETECTOR = "H1"
    MERGER_GPS = 1126259462.4  # GW150914 merger time

    try:
        # Download event data
        print(f"\n1. DOWNLOADING {EVENT} {DETECTOR} DATA")
        print("-" * 50)
        strain, fs, gps_start = download_gwosc_data(EVENT, DETECTOR)

        print(f"  Sample rate: {fs} Hz")
        print(f"  Duration: {len(strain)/fs:.1f} seconds")
        print(f"  GPS start: {gps_start}")

        # Create time array
        times = gps_start + np.arange(len(strain)) / fs

        # Find merger in data
        merger_idx = np.argmin(np.abs(times - MERGER_GPS))
        print(f"  Merger at sample index: {merger_idx}")

        # Define windows
        window_samples = int(2.0 * fs)  # 2 second windows

        # 2. ON-SOURCE: Window centered on merger
        print(f"\n2. ANALYZING ON-SOURCE (EVENT WINDOW)")
        print("-" * 50)

        on_start = max(0, merger_idx - window_samples // 2)
        on_end = min(len(strain), merger_idx + window_samples // 2)
        on_source = strain[on_start:on_end]

        result_on = analyze_segment(on_source, fs, window_seconds=0.5, label="ON-SOURCE (GW event)")
        results.append(result_on)

        print(f"  Samples: {result_on['n_samples']}")
        print(f"  Duration: {result_on['duration_s']:.2f}s")
        print(f"  D (full): {result_on['D_full']:.3f}")
        print(f"  D (mean of windows): {result_on['D_mean']:.3f} +/- {result_on['D_std']:.3f}")

        # 3. OFF-SOURCE: Windows BEFORE the event (pure noise)
        print(f"\n3. ANALYZING OFF-SOURCE (NOISE - BEFORE EVENT)")
        print("-" * 50)

        # Take data 10-12 seconds before merger (well before inspiral)
        off_start_1 = max(0, merger_idx - int(12 * fs))
        off_end_1 = merger_idx - int(10 * fs)
        off_source_before = strain[off_start_1:off_end_1]

        result_off_before = analyze_segment(off_source_before, fs, window_seconds=0.5,
                                            label="OFF-SOURCE (before event)")
        results.append(result_off_before)

        print(f"  Samples: {result_off_before['n_samples']}")
        print(f"  Duration: {result_off_before['duration_s']:.2f}s")
        print(f"  D (full): {result_off_before['D_full']:.3f}")
        print(f"  D (mean of windows): {result_off_before['D_mean']:.3f} +/- {result_off_before['D_std']:.3f}")

        # 4. OFF-SOURCE: Windows AFTER the event (pure noise)
        print(f"\n4. ANALYZING OFF-SOURCE (NOISE - AFTER EVENT)")
        print("-" * 50)

        # Take data 10-12 seconds after merger (well after ringdown)
        off_start_2 = min(len(strain), merger_idx + int(10 * fs))
        off_end_2 = min(len(strain), merger_idx + int(12 * fs))
        off_source_after = strain[off_start_2:off_end_2]

        result_off_after = analyze_segment(off_source_after, fs, window_seconds=0.5,
                                           label="OFF-SOURCE (after event)")
        results.append(result_off_after)

        print(f"  Samples: {result_off_after['n_samples']}")
        print(f"  Duration: {result_off_after['duration_s']:.2f}s")
        print(f"  D (full): {result_off_after['D_full']:.3f}")
        print(f"  D (mean of windows): {result_off_after['D_mean']:.3f} +/- {result_off_after['D_std']:.3f}")

        # 5. Additional: Random segment far from event
        print(f"\n5. ANALYZING RANDOM NOISE SEGMENT (FAR FROM EVENT)")
        print("-" * 50)

        # Take data 100 seconds before (definitely no signal)
        far_start = max(0, merger_idx - int(102 * fs))
        far_end = max(0, merger_idx - int(100 * fs))
        far_noise = strain[far_start:far_end]

        result_far = analyze_segment(far_noise, fs, window_seconds=0.5,
                                     label="FAR OFF-SOURCE (100s before)")
        results.append(result_far)

        print(f"  Samples: {result_far['n_samples']}")
        print(f"  Duration: {result_far['duration_s']:.2f}s")
        print(f"  D (full): {result_far['D_full']:.3f}")
        print(f"  D (mean of windows): {result_far['D_mean']:.3f} +/- {result_far['D_std']:.3f}")

        # 6. STATISTICAL COMPARISON
        print(f"\n" + "=" * 70)
        print("RESULTS COMPARISON")
        print("=" * 70)

        print(f"\n{'Window':<35} {'D (full)':<12} {'D (mean)':<12} {'D (std)':<10}")
        print("-" * 70)
        for r in results:
            print(f"{r['label']:<35} {r['D_full']:<12.3f} {r['D_mean']:<12.3f} {r['D_std']:<10.3f}")

        # Calculate differences
        D_event = result_on['D_mean']
        D_noise_before = result_off_before['D_mean']
        D_noise_after = result_off_after['D_mean']
        D_noise_far = result_far['D_mean']
        D_noise_avg = np.mean([D_noise_before, D_noise_after, D_noise_far])

        print(f"\n" + "=" * 70)
        print("CRITICAL COMPARISON")
        print("=" * 70)
        print(f"\n  D (event window):     {D_event:.3f}")
        print(f"  D (noise average):    {D_noise_avg:.3f}")
        print(f"  Difference:           {D_event - D_noise_avg:.3f}")
        print(f"  Difference (%):       {100*(D_event - D_noise_avg)/D_noise_avg:.1f}%")

        # Statistical test
        noise_values = []
        for r in [result_off_before, result_off_after, result_far]:
            if r['n_windows'] > 0:
                # We'd need the actual values, but we can estimate
                noise_values.extend([r['D_mean']] * r['n_windows'])

        print(f"\n" + "=" * 70)
        print("CONCLUSION")
        print("=" * 70)

        if abs(D_event - D_noise_avg) < 0.1:
            print(f"""
  RESULT: D_event ≈ D_noise (difference < 0.1)

  The fractal dimension during the GW event is essentially
  IDENTICAL to the detector noise fractal dimension.

  This suggests that D ≈ 1.5 is a property of LIGO detector noise,
  NOT a unique signature of gravitational waves.

  The 90-degree arms hypothesis appears SUPPORTED:
  The detector noise characteristics (which dominate the signal)
  inherently produce D ≈ 1.5.
            """)
        else:
            print(f"""
  RESULT: D_event ≠ D_noise (difference = {D_event - D_noise_avg:.3f})

  There IS a measurable difference in fractal dimension between
  the GW event window and pure noise windows.

  This suggests that gravitational waves DO have distinct
  fractal properties that differ from detector noise.
            """)

        # Save results
        output_file = "noise_control_results.json"
        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'event': EVENT,
                'detector': DETECTOR,
                'results': results,
                'summary': {
                    'D_event': D_event,
                    'D_noise_avg': D_noise_avg,
                    'difference': D_event - D_noise_avg,
                    'conclusion': 'noise_dominated' if abs(D_event - D_noise_avg) < 0.1 else 'signal_present'
                }
            }, f, indent=2, default=str)

        print(f"\nResults saved to: {output_file}")

        return results

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

        print("\n" + "=" * 70)
        print("FALLBACK: Testing with synthetic data")
        print("=" * 70)

        return run_synthetic_control()


def run_synthetic_control():
    """
    Comprehensive control experiment with synthetic data.
    Tests what fractal dimension we get from various signal types.
    """
    print("\n" + "=" * 70)
    print("COMPREHENSIVE SYNTHETIC CONTROL EXPERIMENT")
    print("=" * 70)
    print("\nGenerating synthetic control data to understand D measurements...")

    fs = 4096
    duration = 32  # seconds
    n_samples = int(fs * duration)
    t = np.arange(n_samples) / fs

    results = []

    # 1. Pure white noise
    print("\n1. WHITE NOISE (Gaussian)")
    white_noise = np.random.randn(n_samples)
    result_white = analyze_segment(white_noise, fs, window_seconds=1.0, label="White noise")
    results.append(result_white)
    print(f"  D = {result_white['D_mean']:.3f} +/- {result_white['D_std']:.3f}")

    # 2. LIGO-like noise (colored, 1/f characteristic)
    print("\n2. LIGO-LIKE COLORED NOISE")
    # LIGO noise has roughly 1/f^2 at low freq, flat at mid, rising at high
    freqs = np.fft.rfftfreq(n_samples, 1/fs)
    freqs[0] = 1e-10
    # Approximate LIGO noise PSD shape
    ligo_psd = np.ones_like(freqs)
    ligo_psd[freqs < 30] = (30/freqs[freqs < 30])**2  # Low freq seismic
    ligo_psd[freqs > 500] = (freqs[freqs > 500]/500)**0.5  # High freq shot noise
    ligo_noise = np.fft.irfft(np.sqrt(ligo_psd) * np.exp(2j * np.pi * np.random.rand(len(freqs))))
    ligo_noise = ligo_noise[:n_samples]
    result_ligo_noise = analyze_segment(ligo_noise, fs, window_seconds=1.0, label="LIGO-like noise")
    results.append(result_ligo_noise)
    print(f"  D = {result_ligo_noise['D_mean']:.3f} +/- {result_ligo_noise['D_std']:.3f}")

    # 3. Bandpass filtered white noise (like LIGO analysis does)
    print("\n3. BANDPASS FILTERED WHITE NOISE (30-400 Hz)")
    bp_white = bandpass_filter(white_noise, fs, 30, 400)
    result_bp_white = analyze_segment(bp_white, fs, window_seconds=1.0, label="Bandpass white noise")
    results.append(result_bp_white)
    print(f"  D = {result_bp_white['D_mean']:.3f} +/- {result_bp_white['D_std']:.3f}")

    # 4. Sine wave (smooth signal)
    print("\n4. PURE SINE WAVE (100 Hz)")
    sine_wave = np.sin(2 * np.pi * 100 * t)
    result_sine = analyze_segment(sine_wave, fs, window_seconds=1.0, label="Sine wave")
    results.append(result_sine)
    print(f"  D = {result_sine['D_mean']:.3f} +/- {result_sine['D_std']:.3f}")

    # 5. Pure chirp (no noise) - the actual GW signal shape
    print("\n5. PURE CHIRP (GW signal shape, NO noise)")
    f0, f1 = 30, 200
    chirp_pure = np.sin(2 * np.pi * (f0 * t + (f1 - f0) / (2 * duration) * t**2))
    result_chirp_pure = analyze_segment(chirp_pure, fs, window_seconds=1.0, label="Pure chirp (no noise)")
    results.append(result_chirp_pure)
    print(f"  D = {result_chirp_pure['D_mean']:.3f} +/- {result_chirp_pure['D_std']:.3f}")

    # 6. Chirp with SNR=10 noise
    print("\n6. CHIRP + NOISE (SNR ≈ 10)")
    snr = 10
    noise_level = np.std(chirp_pure) / snr
    chirp_snr10 = chirp_pure + noise_level * np.random.randn(n_samples)
    result_snr10 = analyze_segment(chirp_snr10, fs, window_seconds=1.0, label="Chirp SNR=10")
    results.append(result_snr10)
    print(f"  D = {result_snr10['D_mean']:.3f} +/- {result_snr10['D_std']:.3f}")

    # 7. Chirp with SNR=1 noise (signal buried in noise)
    print("\n7. CHIRP + NOISE (SNR ≈ 1, noise dominated)")
    noise_level = np.std(chirp_pure) / 1.0
    chirp_snr1 = chirp_pure + noise_level * np.random.randn(n_samples)
    result_snr1 = analyze_segment(chirp_snr1, fs, window_seconds=1.0, label="Chirp SNR=1")
    results.append(result_snr1)
    print(f"  D = {result_snr1['D_mean']:.3f} +/- {result_snr1['D_std']:.3f}")

    # 8. Chirp with SNR=0.1 noise (signal invisible)
    print("\n8. CHIRP + NOISE (SNR ≈ 0.1, noise overwhelms signal)")
    noise_level = np.std(chirp_pure) / 0.1
    chirp_snr01 = chirp_pure + noise_level * np.random.randn(n_samples)
    result_snr01 = analyze_segment(chirp_snr01, fs, window_seconds=1.0, label="Chirp SNR=0.1")
    results.append(result_snr01)
    print(f"  D = {result_snr01['D_mean']:.3f} +/- {result_snr01['D_std']:.3f}")

    # Summary table
    print(f"\n" + "=" * 70)
    print("SYNTHETIC CONTROL RESULTS")
    print("=" * 70)
    print(f"\n{'Signal Type':<30} {'D (mean)':<12} {'D (std)':<10} {'Note':<20}")
    print("-" * 75)
    for r in results:
        note = ""
        if "white" in r['label'].lower() and "bandpass" not in r['label'].lower():
            note = "Expected ≈1.5"
        elif "sine" in r['label'].lower() or "pure chirp" in r['label'].lower():
            note = "Expected ≈1.0"
        elif "SNR=0.1" in r['label']:
            note = "Noise dominated"
        print(f"{r['label']:<30} {r['D_mean']:<12.3f} {r['D_std']:<10.3f} {note:<20}")

    # Critical analysis
    D_white = result_white['D_mean']
    D_bp_white = result_bp_white['D_mean']
    D_pure_signal = result_chirp_pure['D_mean']
    D_snr10 = result_snr10['D_mean']
    D_snr1 = result_snr1['D_mean']
    D_snr01 = result_snr01['D_mean']

    print(f"\n" + "=" * 70)
    print("CRITICAL ANALYSIS")
    print("=" * 70)

    print(f"""
KEY FINDINGS:

1. PURE SIGNALS (no noise):
   - Sine wave:    D = {result_sine['D_mean']:.3f}  (smooth → D ≈ 1.0)
   - Pure chirp:   D = {D_pure_signal:.3f}  (smooth FM signal → D ≈ 1.0)

2. PURE NOISE:
   - White noise:           D = {D_white:.3f}
   - Bandpass white noise:  D = {D_bp_white:.3f}
   - LIGO-like colored:     D = {result_ligo_noise['D_mean']:.3f}

3. SIGNAL + NOISE (varying SNR):
   - SNR = 10:    D = {D_snr10:.3f}  (signal visible)
   - SNR = 1:     D = {D_snr1:.3f}  (signal/noise equal)
   - SNR = 0.1:   D = {D_snr01:.3f}  (noise overwhelms)

INTERPRETATION:
""")

    # The key insight
    if abs(D_snr01 - D_white) < 0.1:
        print(f"""
  As SNR decreases, D approaches the NOISE value, not the signal value.

  This means: if LIGO measurements show D ≈ {D_white:.1f} regardless of
  whether a GW event is present, the measurement is dominated by
  detector noise characteristics, NOT the gravitational wave signal.

  The published D ≈ 1.5 result likely reflects:
  → Detector noise fractal properties
  → NOT intrinsic GW signal properties

  To prove D ≈ 1.5 is a GW property (not noise), you need to show:
  1. D differs significantly between event and non-event windows
  2. D correlates with SNR (higher SNR → more signal → different D)
  3. D for pure simulated waveforms differs from noise
""")
    else:
        print(f"""
  The signal does affect D even at low SNR.
  Further investigation needed with real LIGO data.
""")

    # Save comprehensive results
    output_file = "noise_control_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'experiment': 'synthetic_control',
            'results': results,
            'analysis': {
                'D_white_noise': D_white,
                'D_bandpass_white': D_bp_white,
                'D_pure_chirp': D_pure_signal,
                'D_chirp_snr10': D_snr10,
                'D_chirp_snr1': D_snr1,
                'D_chirp_snr01': D_snr01,
                'conclusion': 'noise_dominated' if abs(D_snr01 - D_white) < 0.1 else 'signal_detectable'
            }
        }, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")

    return results


if __name__ == "__main__":
    run_control_experiment()
