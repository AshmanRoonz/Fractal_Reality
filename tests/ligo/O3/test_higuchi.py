"""
Test Higuchi FD calculation to see if there's a systematic 2× error
"""

import numpy as np
from scipy import stats

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
    """Convert Higuchi to canonical FD using O1 calibration."""
    if np.isnan(higuchi_value):
        return np.nan
    return 1.032 * higuchi_value + 0.975


# Test with known signals
print("="*70)
print("TESTING HIGUCHI FD WITH KNOWN SIGNALS")
print("="*70)

# 1. White noise (should give D ≈ 1.5 for fBm H=0.5)
np.random.seed(42)
white_noise = np.random.randn(4096)

D_wn_raw, r2_wn = higuchi_fd(white_noise, k_max=25)
D_wn_cal = calibrate_fd(D_wn_raw)

print(f"\n1. WHITE NOISE (expected D ≈ 1.5):")
print(f"   Higuchi raw: {D_wn_raw:.3f}")
print(f"   Calibrated:  {D_wn_cal:.3f}")
print(f"   R²: {r2_wn:.4f}")

# 2. Smooth sine wave (should give D ≈ 1.0)
t = np.linspace(0, 10, 4096)
sine = np.sin(2 * np.pi * t)

D_sin_raw, r2_sin = higuchi_fd(sine, k_max=25)
D_sin_cal = calibrate_fd(D_sin_raw)

print(f"\n2. SINE WAVE (expected D ≈ 1.0):")
print(f"   Higuchi raw: {D_sin_raw:.3f}")
print(f"   Calibrated:  {D_sin_cal:.3f}")
print(f"   R²: {r2_sin:.4f}")

# 3. Brownian motion (should give D ≈ 1.5)
brownian = np.cumsum(np.random.randn(4096))

D_bm_raw, r2_bm = higuchi_fd(brownian, k_max=25)
D_bm_cal = calibrate_fd(D_bm_raw)

print(f"\n3. BROWNIAN MOTION (expected D ≈ 1.5):")
print(f"   Higuchi raw: {D_bm_raw:.3f}")
print(f"   Calibrated:  {D_bm_cal:.3f}")
print(f"   R²: {r2_bm:.4f}")

# 4. Very rough noise (should give D > 1.5)
rough_noise = np.diff(np.random.randn(4097))

D_rn_raw, r2_rn = higuchi_fd(rough_noise, k_max=25)
D_rn_cal = calibrate_fd(D_rn_raw)

print(f"\n4. ROUGH NOISE (expected D > 1.5):")
print(f"   Higuchi raw: {D_rn_raw:.3f}")
print(f"   Calibrated:  {D_rn_cal:.3f}")
print(f"   R²: {r2_rn:.4f}")

# 5. Test with actual LIGO noise-like signal
# Simulate 1/f noise (pink noise) which is more realistic
freqs = np.fft.rfftfreq(4096, 1/4096)
psd = 1 / np.sqrt(freqs + 1)  # 1/f^0.5 spectrum
phases = np.random.uniform(0, 2*np.pi, len(freqs))
fft_vals = psd * np.exp(1j * phases)
ligo_like = np.fft.irfft(fft_vals)

D_ligo_raw, r2_ligo = higuchi_fd(ligo_like, k_max=25)
D_ligo_cal = calibrate_fd(D_ligo_raw)

print(f"\n5. LIGO-LIKE NOISE (1/f spectrum):")
print(f"   Higuchi raw: {D_ligo_raw:.3f}")
print(f"   Calibrated:  {D_ligo_cal:.3f}")
print(f"   R²: {r2_ligo:.4f}")

print(f"\n" + "="*70)
print("ANALYSIS:")
print("="*70)

if D_wn_cal > 2.5:
    print("\n⚠ WHITE NOISE GIVING D ≈ 3.0 INSTEAD OF 1.5!")
    print("   This confirms a systematic 2× error in the implementation.")
    print("\n   Possible causes:")
    print("   1. Higuchi normalization is wrong")
    print("   2. Calibration curve is from different methodology")
    print("   3. Missing a factor in curve_length calculation")
elif D_wn_cal < 1.0:
    print("\n⚠ WHITE NOISE GIVING D < 1.0!")
    print("   FD is too low - different systematic error")
else:
    print("\n✓ WHITE NOISE GIVING REASONABLE D ≈ 1.5")
    print("   Implementation looks correct.")
    print("\n   Your O3 data D ≈ 3.0 suggests:")
    print("   - The real data is rougher than white noise")
    print("   - OR there's something specific about the LIGO data")

# Check if calibration is the issue
print(f"\n" + "="*70)
print("CALIBRATION CHECK:")
print("="*70)
print(f"\nWithout calibration:")
print(f"  White noise Higuchi: {D_wn_raw:.3f}")
print(f"\nWith calibration (1.032×H + 0.975):")
print(f"  White noise: {D_wn_cal:.3f}")
print(f"\nYour O3 results: D ≈ 2.97")
print(f"Reverse engineering: H = (2.97 - 0.975) / 1.032 = {(2.97 - 0.975) / 1.032:.3f}")
print(f"\nThis means raw Higuchi is giving ~1.93 on your O3 data")
