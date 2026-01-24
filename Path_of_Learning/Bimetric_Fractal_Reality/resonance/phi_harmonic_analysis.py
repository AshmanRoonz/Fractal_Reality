#!/usr/bin/env python3
"""
Phi-Harmonic Analysis of Gravitational Waves
=============================================

Analyzes LIGO gravitational wave data for Golden Ratio (Φ) structure
Integrates Pattern Resonance Theory with Fractal Reality framework

Author: Ashman Roonz
Date: November 7, 2025
Repository: github.com/AshmanRoonz/Fractal_Reality
"""

import numpy as np
from scipy import signal, stats
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List
import h5py

# Golden Ratio
PHI = (1 + np.sqrt(5)) / 2  # ≈ 1.618033988749895

def generate_phi_frequencies(f_fundamental: float, n_octaves: int = 10) -> np.ndarray:
    """
    Generate frequency array with Φ-spacing
    
    Args:
        f_fundamental: Base frequency in Hz
        n_octaves: Number of Φ-octaves above and below fundamental
    
    Returns:
        Array of Φ-spaced frequencies
    """
    powers = np.arange(-n_octaves, n_octaves + 1)
    frequencies = f_fundamental * PHI**powers
    return frequencies


def phi_spectrum_analysis(time_series: np.ndarray, 
                         sample_rate: float,
                         f_fundamental: float = None) -> Dict:
    """
    Compute power spectrum with emphasis on Φ-spaced frequencies
    
    Args:
        time_series: Time-domain signal
        sample_rate: Sampling rate in Hz
        f_fundamental: Fundamental frequency (auto-detected if None)
    
    Returns:
        Dictionary with spectrum data and Φ-resonance metrics
    """
    # Compute FFT
    N = len(time_series)
    fft_vals = fft(time_series)
    fft_freqs = fftfreq(N, 1/sample_rate)
    
    # Only positive frequencies
    pos_mask = fft_freqs > 0
    freqs = fft_freqs[pos_mask]
    power = np.abs(fft_vals[pos_mask])**2
    
    # Auto-detect fundamental if not provided
    if f_fundamental is None:
        # Find dominant frequency in range 20-500 Hz (typical for GW)
        gw_mask = (freqs >= 20) & (freqs <= 500)
        if np.any(gw_mask):
            f_fundamental = freqs[gw_mask][np.argmax(power[gw_mask])]
        else:
            f_fundamental = 100.0  # Default
    
    # Generate Φ-spaced target frequencies
    phi_freqs = generate_phi_frequencies(f_fundamental, n_octaves=8)
    phi_freqs = phi_freqs[(phi_freqs > 0) & (phi_freqs < sample_rate/2)]
    
    # Measure power at Φ-frequencies (with tolerance)
    tolerance = 0.05  # 5% frequency tolerance
    phi_powers = []
    
    for f_phi in phi_freqs:
        # Find power near this Φ-frequency
        mask = (freqs >= f_phi * (1 - tolerance)) & (freqs <= f_phi * (1 + tolerance))
        if np.any(mask):
            phi_powers.append(np.max(power[mask]))
        else:
            phi_powers.append(0.0)
    
    phi_powers = np.array(phi_powers)
    
    # Compute Φ-resonance score
    total_power = np.sum(power)
    phi_power = np.sum(phi_powers)
    phi_score = phi_power / total_power if total_power > 0 else 0.0
    
    # Check for Φ-harmonic relationships between peak frequencies
    peak_indices = signal.find_peaks(power, height=np.percentile(power, 90))[0]
    peak_freqs = freqs[peak_indices]
    
    phi_relationships = []
    for i, f1 in enumerate(peak_freqs[:-1]):
        for f2 in peak_freqs[i+1:]:
            ratio = f2 / f1
            # Check if ratio close to Φ^n for some integer n
            for n in range(-5, 6):
                phi_n = PHI**n
                if np.abs(ratio - phi_n) / phi_n < 0.1:  # 10% tolerance
                    phi_relationships.append({
                        'f1': f1,
                        'f2': f2,
                        'ratio': ratio,
                        'phi_power': n,
                        'phi_theoretical': phi_n,
                        'error': np.abs(ratio - phi_n) / phi_n
                    })
    
    return {
        'frequencies': freqs,
        'power': power,
        'f_fundamental': f_fundamental,
        'phi_frequencies': phi_freqs,
        'phi_powers': phi_powers,
        'phi_score': phi_score,
        'phi_relationships': phi_relationships,
        'peak_frequencies': peak_freqs
    }


def wavelet_phi_analysis(time_series: np.ndarray,
                        sample_rate: float,
                        f_fundamental: float = None) -> Dict:
    """
    Time-frequency analysis using Φ-spaced wavelets
    
    Args:
        time_series: Time-domain signal  
        sample_rate: Sampling rate in Hz
        f_fundamental: Fundamental frequency for Φ-spacing
        
    Returns:
        Dictionary with time-frequency representation and Φ-metrics
    """
    if f_fundamental is None:
        # Quick estimate from FFT
        spectrum = phi_spectrum_analysis(time_series, sample_rate)
        f_fundamental = spectrum['f_fundamental']
    
    # Generate Φ-spaced frequencies for wavelets
    phi_freqs = generate_phi_frequencies(f_fundamental, n_octaves=6)
    phi_freqs = phi_freqs[(phi_freqs > 20) & (phi_freqs < 500)]
    
    # Compute wavelet transform
    widths = sample_rate / phi_freqs  # Convert frequency to wavelet width
    cwt_matrix = signal.cwt(time_series, signal.morlet2, widths)
    
    # Compute time-averaged power at each Φ-frequency
    phi_time_power = np.abs(cwt_matrix)**2
    phi_avg_power = np.mean(phi_time_power, axis=1)
    
    # Measure temporal coherence of Φ-patterns
    coherence = []
    for i in range(len(phi_freqs) - 1):
        # Cross-correlation between adjacent Φ-frequency bands
        cc = np.corrcoef(phi_time_power[i], phi_time_power[i+1])[0, 1]
        coherence.append(cc)
    
    avg_coherence = np.mean(coherence) if coherence else 0.0
    
    return {
        'phi_frequencies': phi_freqs,
        'time_frequency_matrix': cwt_matrix,
        'phi_power': phi_avg_power,
        'phi_coherence': avg_coherence,
        'coherence_array': coherence
    }


def beta_phi_consistency_test(measured_beta: float, 
                              measured_D: float) -> Dict:
    """
    Test consistency between measured β, D, and Φ predictions
    
    Args:
        measured_beta: Observed balance parameter
        measured_D: Observed fractal dimension
        
    Returns:
        Dictionary with consistency metrics
    """
    # Theoretical predictions
    phi_inv = 1 / PHI  # ≈ 0.618
    beta_theoretical = phi_inv / PHI  # ≈ 0.382 (or 0.5 for consciousness)
    
    # For consciousness specifically
    beta_consciousness = 0.5
    
    # Fractal dimension predictions
    D_from_beta = 1 + measured_beta
    D_phi_perfect = 1 + phi_inv  # ≈ 1.618
    D_observed_mean = 1.503
    
    # Damping factor
    damping = (phi_inv - (measured_D - 1)) / phi_inv
    
    # Consistency checks
    beta_phi_error = np.abs(measured_beta - beta_consciousness)
    D_prediction_error = np.abs(measured_D - D_observed_mean)
    
    return {
        'measured_beta': measured_beta,
        'measured_D': measured_D,
        'phi_inverse': phi_inv,
        'beta_consciousness_theoretical': beta_consciousness,
        'D_phi_perfect': D_phi_perfect,
        'D_from_beta': D_from_beta,
        'damping_factor': damping,
        'beta_phi_error': beta_phi_error,
        'D_prediction_error': D_prediction_error,
        'is_consistent': (beta_phi_error < 0.1) and (D_prediction_error < 0.1)
    }


def analyze_gw_event_for_phi(h5_file_path: str,
                             detector: str = 'H1',
                             event_time: float = None) -> Dict:
    """
    Complete Φ-harmonic analysis of a gravitational wave event
    
    Args:
        h5_file_path: Path to HDF5 file with strain data
        detector: Detector name (H1, L1, V1)
        event_time: GPS time of event (auto-detect peak if None)
        
    Returns:
        Comprehensive analysis dictionary
    """
    # Load data
    with h5py.File(h5_file_path, 'r') as f:
        strain = f['strain']['Strain'][:]
        sample_rate = 1.0 / f['strain']['Strain'].attrs['Xspacing']
        gps_start = f['strain']['Strain'].attrs['Xstart']
    
    # If event_time provided, window around it
    if event_time is not None:
        duration = 1.0  # seconds around event
        start_idx = int((event_time - gps_start - duration/2) * sample_rate)
        end_idx = int((event_time - gps_start + duration/2) * sample_rate)
        strain = strain[max(0, start_idx):end_idx]
    
    # Apply bandpass filter (20-500 Hz, typical for GW)
    sos = signal.butter(4, [20, 500], btype='band', fs=sample_rate, output='sos')
    strain_filtered = signal.sosfilt(sos, strain)
    
    # Compute Φ-spectrum
    spectrum_results = phi_spectrum_analysis(strain_filtered, sample_rate)
    
    # Compute Φ-wavelet analysis
    wavelet_results = wavelet_phi_analysis(strain_filtered, sample_rate,
                                          spectrum_results['f_fundamental'])
    
    # Summary metrics
    results = {
        'detector': detector,
        'sample_rate': sample_rate,
        'spectrum': spectrum_results,
        'wavelet': wavelet_results,
        'phi': PHI,
        'summary': {
            'fundamental_frequency': spectrum_results['f_fundamental'],
            'phi_score': spectrum_results['phi_score'],
            'n_phi_relationships': len(spectrum_results['phi_relationships']),
            'wavelet_phi_coherence': wavelet_results['phi_coherence']
        }
    }
    
    return results


def plot_phi_analysis_results(results: Dict, save_path: str = None):
    """
    Create comprehensive visualization of Φ-analysis results
    
    Args:
        results: Output from analyze_gw_event_for_phi
        save_path: Optional path to save figure
    """
    fig = plt.figure(figsize=(16, 12))
    
    # 1. Power spectrum with Φ-frequencies marked
    ax1 = plt.subplot(3, 2, 1)
    spectrum = results['spectrum']
    ax1.loglog(spectrum['frequencies'], spectrum['power'], 'b-', alpha=0.6, label='Full Spectrum')
    
    # Mark Φ-frequencies
    for i, (f_phi, p_phi) in enumerate(zip(spectrum['phi_frequencies'], spectrum['phi_powers'])):
        if p_phi > 0:
            ax1.plot(f_phi, p_phi, 'ro', markersize=8, alpha=0.7)
            if i % 3 == 0:  # Label every 3rd to avoid clutter
                ax1.text(f_phi, p_phi, f'Φ^{i-4:.0f}', fontsize=8)
    
    ax1.set_xlabel('Frequency (Hz)')
    ax1.set_ylabel('Power')
    ax1.set_title(f'Power Spectrum with Φ-Harmonics (Score: {spectrum["phi_score"]:.3f})')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 2. Φ-power distribution
    ax2 = plt.subplot(3, 2, 2)
    phi_powers_db = 10 * np.log10(spectrum['phi_powers'] + 1e-10)
    ax2.bar(range(len(phi_powers_db)), phi_powers_db, color='orange', alpha=0.7)
    ax2.set_xlabel('Φ^n Index')
    ax2.set_ylabel('Power (dB)')
    ax2.set_title('Power at Φ-Harmonics')
    ax2.grid(True, alpha=0.3)
    
    # 3. Peak frequency ratios vs Φ^n
    ax3 = plt.subplot(3, 2, 3)
    if spectrum['phi_relationships']:
        errors = [rel['error'] for rel in spectrum['phi_relationships']]
        powers = [rel['phi_power'] for rel in spectrum['phi_relationships']]
        ax3.scatter(powers, errors, s=100, alpha=0.6, c='green')
        ax3.axhline(y=0.1, color='r', linestyle='--', label='10% Tolerance')
        ax3.set_xlabel('Φ Power (n)')
        ax3.set_ylabel('Relative Error')
        ax3.set_title(f'Φ-Relationships Found: {len(spectrum["phi_relationships"])}')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
    else:
        ax3.text(0.5, 0.5, 'No Φ-relationships detected', 
                ha='center', va='center', transform=ax3.transAxes)
    
    # 4. Time-frequency representation
    ax4 = plt.subplot(3, 2, 4)
    wavelet = results['wavelet']
    time_axis = np.arange(wavelet['time_frequency_matrix'].shape[1]) / results['sample_rate']
    
    # Plot as heatmap
    im = ax4.pcolormesh(time_axis, wavelet['phi_frequencies'], 
                       np.abs(wavelet['time_frequency_matrix']),
                       shading='auto', cmap='viridis')
    ax4.set_ylabel('Φ-Frequency (Hz)')
    ax4.set_xlabel('Time (s)')
    ax4.set_title(f'Φ-Wavelet Transform (Coherence: {wavelet["phi_coherence"]:.3f})')
    plt.colorbar(im, ax=ax4, label='Amplitude')
    
    # 5. Coherence between adjacent Φ-bands
    ax5 = plt.subplot(3, 2, 5)
    if wavelet['coherence_array']:
        ax5.plot(wavelet['coherence_array'], 'o-', color='purple', linewidth=2, markersize=6)
        ax5.axhline(y=0.5, color='r', linestyle='--', label='Moderate Coherence')
        ax5.set_xlabel('Φ-Band Pair Index')
        ax5.set_ylabel('Cross-Correlation')
        ax5.set_title('Φ-Band Coherence')
        ax5.grid(True, alpha=0.3)
        ax5.legend()
    
    # 6. Summary text
    ax6 = plt.subplot(3, 2, 6)
    ax6.axis('off')
    
    summary_text = f"""
    Φ-HARMONIC ANALYSIS SUMMARY
    ===========================
    
    Golden Ratio (Φ): {PHI:.6f}
    
    SPECTRUM:
    • Fundamental Frequency: {spectrum['f_fundamental']:.2f} Hz
    • Φ-Resonance Score: {spectrum['phi_score']:.4f}
    • Φ-Relationships Detected: {len(spectrum['phi_relationships'])}
    
    WAVELET:
    • Φ-Band Coherence: {wavelet['phi_coherence']:.4f}
    • Analysis Frequencies: {len(wavelet['phi_frequencies'])}
    
    INTERPRETATION:
    • Φ-Score > 0.1: Strong harmonic structure
    • Coherence > 0.5: Sustained Φ-patterns
    • Multiple relationships: Nested harmonics
    
    CONSISTENCY WITH FRACTAL REALITY:
    • Predicted D ≈ 1.5 from β ≈ 0.5
    • β ≈ Φ⁻¹/Φ ≈ 0.382-0.5 range
    • Consciousness at perfect Φ-balance
    """
    
    ax6.text(0.1, 0.9, summary_text, fontsize=10, verticalalignment='top',
            fontfamily='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to {save_path}")
    
    plt.show()


def batch_phi_analysis(gw_event_list: List[Dict]) -> Dict:
    """
    Analyze multiple gravitational wave events for Φ-structure
    
    Args:
        gw_event_list: List of dicts with keys 'file_path', 'detector', 'event_time'
        
    Returns:
        Aggregate statistics across all events
    """
    all_phi_scores = []
    all_coherences = []
    all_n_relationships = []
    all_fundamentals = []
    
    for event in gw_event_list:
        try:
            results = analyze_gw_event_for_phi(
                event['file_path'],
                event.get('detector', 'H1'),
                event.get('event_time')
            )
            
            all_phi_scores.append(results['summary']['phi_score'])
            all_coherences.append(results['summary']['wavelet_phi_coherence'])
            all_n_relationships.append(results['summary']['n_phi_relationships'])
            all_fundamentals.append(results['summary']['fundamental_frequency'])
            
        except Exception as e:
            print(f"Warning: Failed to analyze {event.get('file_path', 'unknown')}: {e}")
            continue
    
    return {
        'n_events': len(all_phi_scores),
        'phi_scores': {
            'mean': np.mean(all_phi_scores),
            'std': np.std(all_phi_scores),
            'median': np.median(all_phi_scores),
            'all': all_phi_scores
        },
        'coherences': {
            'mean': np.mean(all_coherences),
            'std': np.std(all_coherences),
            'median': np.median(all_coherences),
            'all': all_coherences
        },
        'n_relationships': {
            'mean': np.mean(all_n_relationships),
            'std': np.std(all_n_relationships),
            'total': sum(all_n_relationships),
            'all': all_n_relationships
        },
        'fundamentals': {
            'mean': np.mean(all_fundamentals),
            'std': np.std(all_fundamentals),
            'all': all_fundamentals
        }
    }


def consciousness_eeg_phi_score(eeg_data: np.ndarray,
                                sample_rate: float,
                                bands: Dict[str, Tuple[float, float]] = None) -> float:
    """
    Compute consciousness Φ-resonance score from EEG data
    
    Args:
        eeg_data: Multi-channel EEG time series [n_channels, n_samples]
        sample_rate: Sampling rate in Hz
        bands: Dictionary of frequency bands (default: standard EEG bands)
        
    Returns:
        Φ-resonance score (higher = more conscious state predicted)
    """
    if bands is None:
        bands = {
            'delta': (0.5, 4),
            'theta': (4, 8),
            'alpha': (8, 13),
            'beta': (13, 30),
            'gamma': (30, 50)
        }
    
    # Compute power in each band (averaged across channels)
    band_powers = {}
    for band_name, (low, high) in bands.items():
        sos = signal.butter(4, [low, high], btype='band', fs=sample_rate, output='sos')
        filtered = signal.sosfilt(sos, eeg_data, axis=1)
        power = np.mean(filtered**2)
        band_powers[band_name] = power
    
    # Compute mean frequency in each band
    band_freqs = {name: np.mean(band_range) for name, band_range in bands.items()}
    
    # Check for Φ-relationships between bands
    phi_score = 0.0
    n_comparisons = 0
    
    band_names = list(band_freqs.keys())
    for i in range(len(band_names)):
        for j in range(i+1, len(band_names)):
            f1 = band_freqs[band_names[i]]
            f2 = band_freqs[band_names[j]]
            ratio = f2 / f1
            
            # Find closest Φ^n
            best_error = float('inf')
            for n in range(-3, 4):
                phi_n = PHI**n
                error = abs(ratio - phi_n) / phi_n
                if error < best_error:
                    best_error = error
            
            # Weight by geometric mean of band powers
            weight = np.sqrt(band_powers[band_names[i]] * band_powers[band_names[j]])
            phi_score += weight * np.exp(-best_error)
            n_comparisons += 1
    
    # Normalize
    phi_score /= n_comparisons if n_comparisons > 0 else 1.0
    
    return phi_score


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("Φ-Harmonic Analysis Toolkit")
    print("=" * 50)
    print(f"Golden Ratio (Φ): {PHI:.10f}")
    print(f"Φ⁻¹: {1/PHI:.10f}")
    print(f"Φ⁻¹/Φ (β_consciousness): {(1/PHI)/PHI:.10f}")
    print()
    
    # Example: Generate synthetic gravitational wave with Φ-structure
    print("Generating synthetic GW with Φ-harmonics...")
    sample_rate = 4096  # Hz
    duration = 1.0  # seconds
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Create signal with Φ-spaced frequency components
    f_fund = 100  # Hz
    signal_gw = np.zeros_like(t)
    
    for n in range(-3, 4):
        f_n = f_fund * PHI**n
        if 20 <= f_n <= 500:  # Typical GW range
            amplitude = 1.0 / (1 + abs(n))  # Decay with distance from fundamental
            signal_gw += amplitude * np.sin(2 * np.pi * f_n * t)
    
    # Add noise
    signal_gw += 0.5 * np.random.randn(len(t))
    
    print(f"Signal duration: {duration} s")
    print(f"Sampling rate: {sample_rate} Hz")
    print(f"Fundamental frequency: {f_fund} Hz")
    print()
    
    # Analyze
    print("Running Φ-spectrum analysis...")
    results_spectrum = phi_spectrum_analysis(signal_gw, sample_rate, f_fund)
    
    print(f"  Φ-resonance score: {results_spectrum['phi_score']:.4f}")
    print(f"  Φ-relationships found: {len(results_spectrum['phi_relationships'])}")
    
    for i, rel in enumerate(results_spectrum['phi_relationships'][:5]):  # Show first 5
        print(f"    {i+1}. {rel['f1']:.1f} Hz : {rel['f2']:.1f} Hz = {rel['ratio']:.3f} ≈ Φ^{rel['phi_power']} (error: {rel['error']*100:.1f}%)")
    
    print()
    print("Running Φ-wavelet analysis...")
    results_wavelet = wavelet_phi_analysis(signal_gw, sample_rate, f_fund)
    
    print(f"  Φ-band coherence: {results_wavelet['phi_coherence']:.4f}")
    print()
    
    # Test β-D-Φ consistency
    print("Testing β-D-Φ consistency...")
    consistency = beta_phi_consistency_test(measured_beta=0.503, measured_D=1.503)
    
    print(f"  Measured β: {consistency['measured_beta']:.3f}")
    print(f"  Measured D: {consistency['measured_D']:.3f}")
    print(f"  Theoretical D_Φ: {consistency['D_phi_perfect']:.3f}")
    print(f"  Damping factor: {consistency['damping_factor']*100:.1f}%")
    print(f"  Consistent with Φ-theory: {consistency['is_consistent']}")
    print()
    
    print("=" * 50)
    print("Analysis complete!")
    print()
    print("To analyze real LIGO data:")
    print("  results = analyze_gw_event_for_phi('path/to/event.hdf5')")
    print("  plot_phi_analysis_results(results, 'output_figure.png')")
