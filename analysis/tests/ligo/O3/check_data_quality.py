import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

filename = 'gwosc_data/GW_GPS1239080960_H1.hdf5'

print("="*70)
print("DATA QUALITY CHECK - GW190412")
print("="*70)

with h5py.File(filename, 'r') as f:
    strain = f['strain'][:]
    gps_start = f['strain'].attrs['gps_start']
    sample_rate = f['strain'].attrs['sample_rate']
    
    # Event location
    event_gps = 1239082262.2
    event_offset = event_gps - gps_start
    event_idx = int(event_offset * sample_rate)
    
    print(f"\nEvent at index: {event_idx:,} ({event_offset:.1f}s from start)")
    
    # Extract window around event
    window_duration = 32  # seconds
    half_window = int(window_duration * sample_rate / 2)
    
    start_idx = max(0, event_idx - half_window)
    end_idx = min(len(strain), event_idx + half_window)
    
    strain_window = strain[start_idx:end_idx]
    times_window = np.arange(len(strain_window)) / sample_rate
    
    print(f"\nExtracted {len(strain_window):,} samples ({len(strain_window)/sample_rate:.1f}s)")
    print(f"\nSTRAIN STATISTICS (32s window):")
    print(f"  Min: {np.nanmin(strain_window):.3e}")
    print(f"  Max: {np.nanmax(strain_window):.3e}")
    print(f"  Mean: {np.nanmean(strain_window):.3e}")
    print(f"  Std: {np.nanstd(strain_window):.3e}")
    print(f"  Contains NaN: {np.any(np.isnan(strain_window))}")
    print(f"  Contains Inf: {np.any(np.isinf(strain_window))}")
    
    # Check for typical GW signal characteristics
    print(f"\nSIGNAL QUALITY CHECKS:")
    
    # 1. Amplitude range (should be ~1e-21 to 1e-20 for real strain)
    typical_gw_amplitude = 1e-21
    if np.nanmax(np.abs(strain_window)) < 1e-17:
        print(f"  ✓ Amplitude range looks reasonable for strain data")
        print(f"    Max |strain|: {np.nanmax(np.abs(strain_window)):.3e}")
    else:
        print(f"  ✗ Amplitude seems too large!")
        print(f"    Max |strain|: {np.nanmax(np.abs(strain_window)):.3e}")
        print(f"    Expected: ~1e-21 to 1e-19")
    
    # 2. Apply bandpass filter (20-400 Hz, typical for GW analysis)
    nyquist = sample_rate / 2
    low = 20 / nyquist
    high = 400 / nyquist
    b, a = signal.butter(4, [low, high], btype='band')
    
    # Remove NaNs before filtering
    valid_mask = ~np.isnan(strain_window)
    if np.sum(valid_mask) > 0:
        strain_clean = np.copy(strain_window)
        strain_clean[~valid_mask] = 0  # Replace NaNs with zeros
        strain_filtered = signal.filtfilt(b, a, strain_clean)
    else:
        print("  ✗ All data is NaN!")
        strain_filtered = strain_window
    
    print(f"\nFILTERED STRAIN (20-400 Hz):")
    print(f"  Max: {np.nanmax(np.abs(strain_filtered)):.3e}")
    
    # 3. Create plots
    fig, axes = plt.subplots(3, 2, figsize=(16, 12))
    fig.suptitle('GW190412 Data Quality Assessment', fontsize=14, fontweight='bold')
    
    # Raw strain - full window
    ax = axes[0, 0]
    ax.plot(times_window, strain_window, alpha=0.8)
    ax.axvline(window_duration/2, color='red', linestyle='--', label='Event time')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Strain')
    ax.set_title('Raw Strain (32s window)')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Raw strain - zoom to ±2s around event
    ax = axes[0, 1]
    center_idx = len(strain_window) // 2
    zoom_samples = int(4 * sample_rate)  # ±2 seconds
    zoom_start = max(0, center_idx - zoom_samples)
    zoom_end = min(len(strain_window), center_idx + zoom_samples)
    ax.plot(times_window[zoom_start:zoom_end], strain_window[zoom_start:zoom_end])
    ax.axvline(window_duration/2, color='red', linestyle='--', label='Event')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Strain')
    ax.set_title('Raw Strain (±2s zoom)')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Filtered strain - full window
    ax = axes[1, 0]
    ax.plot(times_window, strain_filtered, alpha=0.8)
    ax.axvline(window_duration/2, color='red', linestyle='--', label='Event time')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Strain')
    ax.set_title('Bandpass Filtered Strain (20-400 Hz)')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Filtered strain - zoom
    ax = axes[1, 1]
    ax.plot(times_window[zoom_start:zoom_end], strain_filtered[zoom_start:zoom_end])
    ax.axvline(window_duration/2, color='red', linestyle='--', label='Event')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Strain')
    ax.set_title('Filtered Strain (±2s zoom)')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Power spectral density
    ax = axes[2, 0]
    # Use only valid data
    if np.sum(valid_mask) > 1000:
        f, psd = signal.welch(strain_window[valid_mask], sample_rate, nperseg=4096)
        ax.loglog(f, np.sqrt(psd))
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('ASD (1/√Hz)')
        ax.set_title('Amplitude Spectral Density')
        ax.set_xlim([10, 2000])
        ax.grid(alpha=0.3)
    
    # Spectrogram
    ax = axes[2, 1]
    if np.sum(valid_mask) > 1000:
        f, t, Sxx = signal.spectrogram(strain_filtered, sample_rate, nperseg=512)
        im = ax.pcolormesh(t, f, np.log10(Sxx + 1e-30), shading='gouraud', cmap='viridis')
        ax.axvline(window_duration/2, color='red', linestyle='--', linewidth=2)
        ax.set_ylabel('Frequency (Hz)')
        ax.set_xlabel('Time (s)')
        ax.set_title('Spectrogram (filtered)')
        ax.set_ylim([20, 500])
        plt.colorbar(im, ax=ax, label='log10(Power)')
    
    plt.tight_layout()
    plt.savefig('gw190412_data_quality.png', dpi=150, bbox_inches='tight')
    print(f"\n✓ Saved quality assessment to gw190412_data_quality.png")
    plt.show()
    
    # Recommendation
    print(f"\n" + "="*70)
    print("RECOMMENDATION:")
    print("="*70)
    
    if np.any(np.isnan(strain_window)):
        print("\n⚠ DATA CONTAINS NaN VALUES!")
        print("  This might be:")
        print("  - Bad data quality flags")
        print("  - Missing detector calibration")
        print("  - Wrong data product")
        print("\n  You may need to download:")
        print("  - Cleaned/filtered strain data")
        print("  - Or apply proper data conditioning")
    
    if np.nanmax(np.abs(strain_window)) > 1e-17:
        print("\n⚠ AMPLITUDE TOO LARGE FOR STRAIN DATA!")
        print("  Your data might be:")
        print("  - Uncalibrated (raw ADC counts)")
        print("  - In wrong units")
        print("  - Contaminated by glitches")
