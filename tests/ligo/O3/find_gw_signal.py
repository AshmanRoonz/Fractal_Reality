import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

filename = 'gwosc_data/GW_GPS1239080960_H1.hdf5'

print("="*70)
print("FINDING ACTUAL GW SIGNAL - GW190412")
print("="*70)

with h5py.File(filename, 'r') as f:
    strain = f['strain'][:]
    gps_start = f['strain'].attrs['gps_start']
    sample_rate = f['strain'].attrs['sample_rate']
    
    # Event location
    event_gps = 1239082262.2
    event_offset = event_gps - gps_start
    event_idx = int(event_offset * sample_rate)
    
    # Extract window around event
    window_duration = 8  # Use shorter window to see signal better
    half_window = int(window_duration * sample_rate / 2)
    
    start_idx = max(0, event_idx - half_window)
    end_idx = min(len(strain), event_idx + half_window)
    
    strain_window = strain[start_idx:end_idx]
    times_window = np.arange(len(strain_window)) / sample_rate
    
    # Apply bandpass filter (30-400 Hz for better signal visibility)
    nyquist = sample_rate / 2
    low = 30 / nyquist
    high = 400 / nyquist
    b, a = signal.butter(4, [low, high], btype='band')
    strain_filtered = signal.filtfilt(b, a, strain_window)
    
    # Whitening for better visibility
    # Compute PSD
    f_psd, psd = signal.welch(strain_window, sample_rate, nperseg=4096)
    
    # Whiten in frequency domain
    fft_strain = np.fft.rfft(strain_filtered)
    freqs = np.fft.rfftfreq(len(strain_filtered), 1/sample_rate)
    
    # Interpolate PSD to match FFT frequencies
    psd_interp = np.interp(freqs, f_psd, psd)
    psd_interp[psd_interp == 0] = 1e-50  # Avoid division by zero
    
    # Whiten
    whitened_fft = fft_strain / np.sqrt(psd_interp)
    strain_whitened = np.fft.irfft(whitened_fft, len(strain_filtered))
    
    # Find peak in whitened, filtered signal
    abs_whitened = np.abs(strain_whitened)
    peak_idx = np.argmax(abs_whitened)
    peak_time = times_window[peak_idx]
    
    print(f"\nSIGNAL DETECTION:")
    print(f"  Window: ±{window_duration/2:.1f}s around catalog time")
    print(f"  Peak found at: {peak_time:.3f}s (from window start)")
    print(f"  Offset from catalog time: {peak_time - window_duration/2:.3f}s")
    print(f"  Peak SNR (whitened): {abs_whitened[peak_idx]:.1f}")
    
    # Calculate SNR in different time segments
    dt = 1/sample_rate
    inspiral_samples = int(0.5 / dt)  # 0.5s before peak
    ringdown_samples = int(0.3 / dt)  # 0.3s after peak
    
    inspiral_start = max(0, peak_idx - inspiral_samples)
    inspiral_end = peak_idx
    ringdown_start = peak_idx
    ringdown_end = min(len(strain_whitened), peak_idx + ringdown_samples)
    
    inspiral = strain_filtered[inspiral_start:inspiral_end]
    ringdown = strain_filtered[ringdown_start:ringdown_end]
    
    print(f"\nPHASE SEGMENTATION:")
    print(f"  Inspiral: {len(inspiral)} samples ({len(inspiral)/sample_rate:.3f}s)")
    print(f"  Ringdown: {len(ringdown)} samples ({len(ringdown)/sample_rate:.3f}s)")
    print(f"  Inspiral RMS: {np.std(inspiral):.3e}")
    print(f"  Ringdown RMS: {np.std(ringdown):.3e}")
    
    # Create detailed plots
    fig, axes = plt.subplots(4, 1, figsize=(16, 12))
    fig.suptitle('GW190412 Signal Detection & Phase Segmentation', fontsize=14, fontweight='bold')
    
    # Raw strain
    ax = axes[0]
    ax.plot(times_window, strain_window, alpha=0.6)
    ax.axvline(window_duration/2, color='red', linestyle='--', linewidth=2, label='Catalog time')
    ax.axvline(peak_time, color='green', linestyle='--', linewidth=2, label='Detected peak')
    ax.set_ylabel('Raw Strain')
    ax.set_title('Raw Data')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Bandpass filtered
    ax = axes[1]
    ax.plot(times_window, strain_filtered, alpha=0.8)
    ax.axvline(window_duration/2, color='red', linestyle='--', linewidth=2, label='Catalog time')
    ax.axvline(peak_time, color='green', linestyle='--', linewidth=2, label='Detected peak')
    ax.set_ylabel('Filtered Strain (30-400 Hz)')
    ax.set_title('Bandpass Filtered')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Whitened
    ax = axes[2]
    ax.plot(times_window, strain_whitened, alpha=0.8, color='purple')
    ax.axvline(window_duration/2, color='red', linestyle='--', linewidth=2, label='Catalog time')
    ax.axvline(peak_time, color='green', linestyle='--', linewidth=2, label='Detected peak')
    ax.set_ylabel('Whitened Strain')
    ax.set_title('Whitened (for SNR enhancement)')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Phase segmentation on filtered data
    ax = axes[3]
    ax.plot(times_window, strain_filtered, alpha=0.8, label='Full signal')
    
    # Mark inspiral phase
    insp_times = times_window[inspiral_start:inspiral_end]
    ax.fill_between(insp_times, 
                    np.min(strain_filtered), np.max(strain_filtered),
                    alpha=0.3, color='blue', label='Inspiral')
    
    # Mark ringdown phase
    ring_times = times_window[ringdown_start:ringdown_end]
    ax.fill_between(ring_times,
                    np.min(strain_filtered), np.max(strain_filtered),
                    alpha=0.3, color='orange', label='Ringdown')
    
    ax.axvline(peak_time, color='green', linestyle='--', linewidth=2, label='Peak (merger)')
    ax.set_xlabel('Time (s from window start)')
    ax.set_ylabel('Filtered Strain')
    ax.set_title('Phase Segmentation: Inspiral → Merger → Ringdown')
    ax.legend()
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('gw190412_signal_detection.png', dpi=150, bbox_inches='tight')
    print(f"\n✓ Saved signal detection plot")
    plt.show()
    
    # Check if we're getting the right peak
    print(f"\n" + "="*70)
    print("DIAGNOSIS:")
    print("="*70)
    
    offset_from_catalog = abs(peak_time - window_duration/2)
    
    if offset_from_catalog < 0.1:  # Within 100ms
        print(f"✓ Peak detection looks good (within {offset_from_catalog*1000:.1f}ms)")
    else:
        print(f"⚠ Peak is {offset_from_catalog:.3f}s from catalog time")
        print(f"  This might be due to:")
        print(f"  - Noise fluctuations")
        print(f"  - Need for better filtering")
        print(f"  - Catalog time is approximate")
    
    # Recommendation for analysis
    print(f"\nRECOMMENDATION:")
    print(f"The analysis code should:")
    print(f"1. Use whitened strain for peak finding")
    print(f"2. Apply 30-400 Hz bandpass before fractal analysis")
    print(f"3. Use ±0.2s window for peak search (not ±2s)")
    print(f"4. Verify peak is within reasonable range of catalog time")
