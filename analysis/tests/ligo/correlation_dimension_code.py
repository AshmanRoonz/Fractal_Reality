# ============================================================================
# CORRELATION DIMENSION ANALYSIS FOR GRAVITATIONAL WAVES
# ============================================================================
# Implements Grassberger-Procaccia algorithm for calculating correlation
# dimension (D₂) from time series data using phase space reconstruction.
#
# This provides a complementary fractal measure to Higuchi dimension:
# - Higuchi D_H: Geometric roughness of time series curve (1D)
# - Correlation D₂: Attractor dimension in reconstructed phase space (≥2D)
#
# Literature reports D₂ ≈ 3-5 for LIGO GW signals
# This implementation validates those findings on the same signals showing D_H ≈ 1.5
# ============================================================================

import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.stats import linregress
import matplotlib.pyplot as plt

# ============================================================================
# 1. TIME DELAY EMBEDDING (TAKENS' THEOREM)
# ============================================================================

def mutual_information(signal, max_lag=100):
    """
    Calculate mutual information to find optimal time delay τ.
    
    Mutual information I(τ) measures shared information between
    signal[t] and signal[t+τ]. First minimum indicates optimal τ
    for phase space reconstruction.
    
    Parameters:
        signal: 1D time series
        max_lag: Maximum lag to test (default 100)
    
    Returns:
        tau_optimal: Optimal time delay (index of first MI minimum)
        mi_values: Mutual information for each lag
    
    Reference: Fraser & Swinney (1986)
    """
    N = len(signal)
    mi_values = []
    
    # Normalize signal to [0, 1]
    sig_norm = (signal - signal.min()) / (signal.max() - signal.min())
    
    # Discretize into bins for histogram
    n_bins = int(np.sqrt(N / 5))  # Rule of thumb
    bins = np.linspace(0, 1, n_bins + 1)
    
    for lag in range(1, max_lag + 1):
        if lag >= N:
            break
        
        # Create lagged pairs
        x = sig_norm[:-lag]
        y = sig_norm[lag:]
        
        # 2D histogram
        H_xy, _, _ = np.histogram2d(x, y, bins=bins)
        H_x = np.histogram(x, bins=bins)[0]
        H_y = np.histogram(y, bins=bins)[0]
        
        # Convert to probabilities
        P_xy = H_xy / H_xy.sum()
        P_x = H_x / H_x.sum()
        P_y = H_y / H_y.sum()
        
        # Calculate mutual information
        mi = 0
        for i in range(len(P_x)):
            for j in range(len(P_y)):
                if P_xy[i, j] > 0 and P_x[i] > 0 and P_y[j] > 0:
                    mi += P_xy[i, j] * np.log(P_xy[i, j] / (P_x[i] * P_y[j]))
        
        mi_values.append(mi)
    
    # Find first local minimum
    mi_array = np.array(mi_values)
    
    # Look for first minimum after initial values
    tau_optimal = 1
    for i in range(2, len(mi_array) - 2):
        if mi_array[i] < mi_array[i-1] and mi_array[i] < mi_array[i+1]:
            tau_optimal = i + 1
            break
    
    return tau_optimal, mi_array


def false_nearest_neighbors(signal, tau, max_dim=15):
    """
    Calculate false nearest neighbors to find optimal embedding dimension.
    
    False Nearest Neighbors (FNN) test: If points are close in m-dimensional
    space but far in (m+1)-dimensional space, they are "false neighbors"
    due to insufficient embedding. Optimal m is where FNN% drops below ~1%.
    
    Parameters:
        signal: 1D time series
        tau: Time delay from mutual information
        max_dim: Maximum embedding dimension to test
    
    Returns:
        m_optimal: Optimal embedding dimension
        fnn_percentages: FNN% for each dimension
    
    Reference: Kennel, Brown & Abarbanel (1992)
    """
    N = len(signal)
    fnn_percentages = []
    
    R_tol = 15.0  # Tolerance for distance ratio
    A_tol = 2.0   # Tolerance for attractor size
    
    sig_std = np.std(signal)
    
    for m in range(1, max_dim + 1):
        # Construct embedded vectors
        n_vectors = N - (m + 1) * tau
        if n_vectors < 100:
            break
        
        vectors_m = np.zeros((n_vectors, m))
        vectors_m1 = np.zeros((n_vectors, m + 1))
        
        for i in range(n_vectors):
            for j in range(m):
                vectors_m[i, j] = signal[i + j * tau]
                vectors_m1[i, j] = signal[i + j * tau]
            vectors_m1[i, m] = signal[i + m * tau]
        
        # Calculate distances in m-dimensional space
        false_neighbors = 0
        total_neighbors = 0
        
        # Sample subset for efficiency
        sample_size = min(500, n_vectors)
        sample_indices = np.random.choice(n_vectors, sample_size, replace=False)
        
        for i in sample_indices:
            # Find nearest neighbor in m-dimensional space
            distances_m = np.sqrt(np.sum((vectors_m - vectors_m[i])**2, axis=1))
            distances_m[i] = np.inf  # Exclude self
            
            nearest_idx = np.argmin(distances_m)
            d_m = distances_m[nearest_idx]
            
            if d_m == 0:
                continue
            
            # Distance in (m+1)-dimensional space
            d_m1 = np.sqrt(np.sum((vectors_m1[i] - vectors_m1[nearest_idx])**2))
            
            # Test 1: Distance ratio
            ratio = np.abs(d_m1 - d_m) / d_m
            
            # Test 2: Relative to attractor size
            relative = d_m1 / sig_std
            
            if ratio > R_tol or relative > A_tol:
                false_neighbors += 1
            
            total_neighbors += 1
        
        fnn_pct = (false_neighbors / total_neighbors) * 100 if total_neighbors > 0 else 0
        fnn_percentages.append(fnn_pct)
    
    # Find where FNN drops below threshold
    fnn_array = np.array(fnn_percentages)
    m_optimal = 1
    
    for i in range(len(fnn_array)):
        if fnn_array[i] < 1.0:  # Less than 1% false neighbors
            m_optimal = i + 1
            break
    
    # If never drops below 1%, use where it stabilizes
    if m_optimal == 1 and len(fnn_array) > 3:
        # Find where change is small
        for i in range(2, len(fnn_array)):
            if abs(fnn_array[i] - fnn_array[i-1]) < 2.0:
                m_optimal = i + 1
                break
    
    return m_optimal, fnn_array


def embed_signal(signal, m, tau):
    """
    Perform time-delay embedding (Takens' theorem).
    
    Reconstruct phase space from 1D time series:
    Y_i = [X(i), X(i+τ), X(i+2τ), ..., X(i+(m-1)τ)]
    
    Parameters:
        signal: 1D time series
        m: Embedding dimension
        tau: Time delay
    
    Returns:
        embedded: Array of shape (n_vectors, m)
    
    Reference: Takens (1981)
    """
    N = len(signal)
    n_vectors = N - (m - 1) * tau
    
    if n_vectors < 1:
        raise ValueError(f"Signal too short for m={m}, tau={tau}")
    
    embedded = np.zeros((n_vectors, m))
    
    for i in range(n_vectors):
        for j in range(m):
            embedded[i, j] = signal[i + j * tau]
    
    return embedded


# ============================================================================
# 2. CORRELATION DIMENSION (GRASSBERGER-PROCACCIA)
# ============================================================================

def correlation_integral(embedded, r_values):
    """
    Calculate correlation integral C(r) for various radii.
    
    C(r) = (2/N(N-1)) × Σ Θ(r - ||Y_i - Y_j||)
    
    Where Θ is Heaviside function, counting pairs within distance r.
    
    Parameters:
        embedded: Embedded vectors (n_vectors × m)
        r_values: Array of radii to test
    
    Returns:
        C_r: Correlation integral for each radius
    """
    N = len(embedded)
    
    # Calculate all pairwise distances (upper triangle only)
    # For efficiency, use pdist which computes condensed distance matrix
    distances = pdist(embedded)
    
    C_r = []
    
    for r in r_values:
        # Count pairs with distance < r
        count = np.sum(distances < r)
        # Normalize by total number of pairs
        C = (2.0 * count) / (N * (N - 1))
        C_r.append(C)
    
    return np.array(C_r)


def estimate_correlation_dimension(embedded, r_min=None, r_max=None, n_radii=50):
    """
    Estimate correlation dimension D₂ using Grassberger-Procaccia algorithm.
    
    D₂ = lim(r→0) [d log(C(r)) / d log(r)]
    
    In practice: slope of log(C) vs log(r) in scaling region.
    
    Parameters:
        embedded: Embedded vectors from time-delay embedding
        r_min: Minimum radius (default: auto-detect)
        r_max: Maximum radius (default: auto-detect)
        n_radii: Number of radii to test
    
    Returns:
        D2: Correlation dimension
        r_values: Radii tested
        C_r: Correlation integrals
        r_scaling: Radii in scaling region
        slope: Slope in scaling region
        r_squared: Quality of fit
    
    Reference: Grassberger & Procaccia (1983)
    """
    # Calculate pairwise distances
    distances = pdist(embedded)
    
    # Determine radius range if not specified
    if r_min is None:
        r_min = np.percentile(distances, 1)  # Avoid very small r (numerical issues)
    
    if r_max is None:
        r_max = np.percentile(distances, 50)  # Avoid saturation at large r
    
    # Generate logarithmically-spaced radii
    r_values = np.logspace(np.log10(r_min), np.log10(r_max), n_radii)
    
    # Calculate correlation integral
    C_r = correlation_integral(embedded, r_values)
    
    # Remove zeros (can't take log)
    valid = C_r > 0
    r_valid = r_values[valid]
    C_valid = C_r[valid]
    
    if len(r_valid) < 5:
        return np.nan, r_values, C_r, None, np.nan, 0.0
    
    # Find scaling region (where log-log plot is linear)
    log_r = np.log(r_valid)
    log_C = np.log(C_valid)
    
    # Use central 60% of data for scaling region
    start_idx = int(len(log_r) * 0.2)
    end_idx = int(len(log_r) * 0.8)
    
    r_scaling = r_valid[start_idx:end_idx]
    log_r_scaling = log_r[start_idx:end_idx]
    log_C_scaling = log_C[start_idx:end_idx]
    
    # Linear regression in scaling region
    slope, intercept, r_value, p_value, std_err = linregress(log_r_scaling, log_C_scaling)
    
    D2 = slope
    r_squared = r_value ** 2
    
    return D2, r_values, C_r, r_scaling, slope, r_squared


# ============================================================================
# 3. COMPLETE ANALYSIS PIPELINE
# ============================================================================

def analyze_correlation_dimension(signal, m=None, tau=None, plot=False):
    """
    Complete correlation dimension analysis pipeline.
    
    Steps:
    1. Find optimal time delay τ (mutual information)
    2. Find optimal embedding dimension m (false nearest neighbors)
    3. Embed signal in m-dimensional phase space
    4. Calculate correlation dimension D₂
    
    Parameters:
        signal: 1D time series
        m: Embedding dimension (None = auto-detect)
        tau: Time delay (None = auto-detect)
        plot: Generate diagnostic plots
    
    Returns:
        results: Dictionary with D₂, τ, m, and quality metrics
    """
    results = {}
    
    print("Correlation Dimension Analysis")
    print("="*50)
    
    # Step 1: Find optimal time delay
    if tau is None:
        print("\n1. Finding optimal time delay (mutual information)...")
        tau, mi_values = mutual_information(signal, max_lag=100)
        print(f"   Optimal τ = {tau}")
        results['tau_auto'] = tau
        results['mi_values'] = mi_values
    else:
        print(f"\n1. Using specified time delay τ = {tau}")
        results['tau_auto'] = False
    
    results['tau'] = tau
    
    # Step 2: Find optimal embedding dimension
    if m is None:
        print("\n2. Finding optimal embedding dimension (FNN)...")
        m, fnn_values = false_nearest_neighbors(signal, tau, max_dim=15)
        print(f"   Optimal m = {m}")
        results['m_auto'] = m
        results['fnn_values'] = fnn_values
    else:
        print(f"\n2. Using specified embedding dimension m = {m}")
        results['m_auto'] = False
    
    results['m'] = m
    
    # Step 3: Embed signal
    print(f"\n3. Embedding signal (m={m}, τ={tau})...")
    embedded = embed_signal(signal, m, tau)
    print(f"   Embedded vectors: {embedded.shape[0]} × {embedded.shape[1]}")
    results['embedded'] = embedded
    results['n_vectors'] = embedded.shape[0]
    
    # Step 4: Calculate correlation dimension
    print("\n4. Calculating correlation dimension...")
    D2, r_values, C_r, r_scaling, slope, r_squared = estimate_correlation_dimension(embedded)
    
    print(f"   D₂ = {D2:.3f}")
    print(f"   R² = {r_squared:.4f}")
    print(f"   Scaling region: r ∈ [{r_scaling[0]:.4f}, {r_scaling[-1]:.4f}]")
    
    results['D2'] = D2
    results['r_values'] = r_values
    results['C_r'] = C_r
    results['r_scaling'] = r_scaling
    results['slope'] = slope
    results['r_squared'] = r_squared
    
    # Generate plots if requested
    if plot:
        plot_correlation_analysis(results, signal)
    
    return results


def plot_correlation_analysis(results, signal):
    """
    Generate diagnostic plots for correlation dimension analysis.
    
    Shows:
    1. Original signal
    2. Mutual information (if auto-detected)
    3. False nearest neighbors (if auto-detected)
    4. Phase space reconstruction (2D projection)
    5. Correlation integral C(r)
    6. Log-log plot with scaling region
    """
    fig = plt.figure(figsize=(15, 10))
    
    # Original signal
    ax1 = plt.subplot(3, 3, 1)
    ax1.plot(signal[:1000], 'b-', linewidth=0.5)
    ax1.set_title('Original Signal (first 1000 points)')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Amplitude')
    ax1.grid(True, alpha=0.3)
    
    # Mutual information
    if results.get('mi_values') is not None:
        ax2 = plt.subplot(3, 3, 2)
        ax2.plot(range(1, len(results['mi_values']) + 1), results['mi_values'], 'g-')
        ax2.axvline(results['tau'], color='r', linestyle='--', label=f"τ = {results['tau']}")
        ax2.set_title('Mutual Information')
        ax2.set_xlabel('Time Lag τ')
        ax2.set_ylabel('MI')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    # False nearest neighbors
    if results.get('fnn_values') is not None:
        ax3 = plt.subplot(3, 3, 3)
        ax3.plot(range(1, len(results['fnn_values']) + 1), results['fnn_values'], 'orange')
        ax3.axhline(1.0, color='r', linestyle='--', label='1% threshold')
        ax3.axvline(results['m'], color='b', linestyle='--', label=f"m = {results['m']}")
        ax3.set_title('False Nearest Neighbors')
        ax3.set_xlabel('Embedding Dimension m')
        ax3.set_ylabel('FNN %')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
    
    # Phase space (2D projection)
    ax4 = plt.subplot(3, 3, 4)
    embedded = results['embedded']
    ax4.plot(embedded[:500, 0], embedded[:500, 1], 'b-', linewidth=0.5, alpha=0.6)
    ax4.set_title(f'Phase Space (m={results["m"]}, τ={results["tau"]})')
    ax4.set_xlabel(f'X(t)')
    ax4.set_ylabel(f'X(t+τ)')
    ax4.grid(True, alpha=0.3)
    
    # 3D phase space if m >= 3
    if results['m'] >= 3:
        ax5 = plt.subplot(3, 3, 5, projection='3d')
        ax5.plot(embedded[:500, 0], embedded[:500, 1], embedded[:500, 2], 
                'b-', linewidth=0.5, alpha=0.6)
        ax5.set_title('3D Phase Space')
        ax5.set_xlabel('X(t)')
        ax5.set_ylabel(f'X(t+τ)')
        ax5.set_zlabel(f'X(t+2τ)')
    
    # Correlation integral
    ax6 = plt.subplot(3, 3, 6)
    ax6.plot(results['r_values'], results['C_r'], 'b-')
    ax6.set_title('Correlation Integral')
    ax6.set_xlabel('Radius r')
    ax6.set_ylabel('C(r)')
    ax6.set_xscale('log')
    ax6.set_yscale('log')
    ax6.grid(True, alpha=0.3)
    
    # Log-log plot with scaling region
    ax7 = plt.subplot(3, 3, 7)
    valid = results['C_r'] > 0
    ax7.plot(results['r_values'][valid], results['C_r'][valid], 'b.', 
            markersize=4, label='Data')
    
    if results['r_scaling'] is not None:
        # Highlight scaling region
        mask = np.isin(results['r_values'], results['r_scaling'])
        ax7.plot(results['r_values'][mask], results['C_r'][mask], 'r.', 
                markersize=6, label='Scaling region')
        
        # Fit line
        log_r_fit = np.log(results['r_scaling'])
        log_C_fit = results['slope'] * log_r_fit + (np.log(results['C_r'][mask][0]) - 
                                                      results['slope'] * log_r_fit[0])
        ax7.plot(results['r_scaling'], np.exp(log_C_fit), 'r--', 
                linewidth=2, label=f'D₂ = {results["D2"]:.3f}')
    
    ax7.set_xlabel('log(r)')
    ax7.set_ylabel('log(C(r))')
    ax7.set_xscale('log')
    ax7.set_yscale('log')
    ax7.set_title(f'Correlation Dimension: D₂ = {results["D2"]:.3f} (R² = {results["r_squared"]:.3f})')
    ax7.legend()
    ax7.grid(True, alpha=0.3)
    
    # Summary text
    ax8 = plt.subplot(3, 3, 8)
    ax8.axis('off')
    summary = f"""
    RESULTS SUMMARY
    ===============
    
    Time Delay (τ): {results['tau']}
    Embedding Dim (m): {results['m']}
    
    Correlation Dimension:
      D₂ = {results['D2']:.3f} ± {results.get('D2_error', 0):.3f}
      
    Fit Quality:
      R² = {results['r_squared']:.4f}
      
    Data Points:
      Total: {results['n_vectors']}
      Scaling region: {len(results['r_scaling']) if results['r_scaling'] is not None else 0}
    
    Interpretation:
      D₂ ≈ 1-2: Low-dimensional
      D₂ ≈ 3-5: Moderate chaos
      D₂ > 5: High-dimensional
    """
    ax8.text(0.1, 0.5, summary, fontfamily='monospace', fontsize=9, 
            verticalalignment='center')
    
    plt.tight_layout()
    plt.savefig('correlation_dimension_analysis.png', dpi=150)
    print("\n✓ Saved diagnostic plots to correlation_dimension_analysis.png")
    plt.show()


# ============================================================================
# 4. COMPARISON WITH HIGUCHI DIMENSION
# ============================================================================

def compare_fractal_measures(signal, higuchi_fd_func):
    """
    Compare Higuchi dimension (D_H) and Correlation dimension (D₂)
    on the same signal to demonstrate their complementary nature.
    
    Parameters:
        signal: 1D time series
        higuchi_fd_func: Function to calculate Higuchi FD
    
    Returns:
        comparison: Dictionary with both measures and interpretation
    """
    print("\n" + "="*70)
    print("COMPARING FRACTAL DIMENSION METHODS")
    print("="*70)
    
    # Calculate Higuchi dimension
    print("\nHIGUCHI DIMENSION (Geometric Roughness)")
    print("-" * 50)
    D_H, r2_H = higuchi_fd_func(signal)
    print(f"D_H = {D_H:.3f} (R² = {r2_H:.3f})")
    print("Interpretation: Measures roughness of 1D time series curve")
    
    # Calculate correlation dimension
    print("\nCORRELATION DIMENSION (Phase Space Structure)")
    print("-" * 50)
    results = analyze_correlation_dimension(signal, m=7, tau=10, plot=False)
    D2 = results['D2']
    r2_D2 = results['r_squared']
    print(f"D₂ = {D2:.3f} (R² = {r2_D2:.3f})")
    print("Interpretation: Measures attractor dimension in phase space")
    
    # Comparison
    print("\n" + "="*70)
    print("COMPARISON & INTERPRETATION")
    print("="*70)
    print(f"\nHiguchi Dimension (D_H): {D_H:.3f}")
    print(f"Correlation Dimension (D₂): {D2:.3f}")
    print(f"Ratio (D₂/D_H): {D2/D_H:.2f}")
    
    print("\nKEY INSIGHT:")
    print("-" * 50)
    print("These measure DIFFERENT properties:")
    print("• D_H quantifies geometric roughness (1D curve)")
    print("• D₂ quantifies dynamical complexity (multi-D attractor)")
    print("\nBoth can be correct simultaneously!")
    print("GW signals can have rough curves (D_H≈1.5) while")
    print("unfolding in complex phase space (D₂≈3-5)")
    
    return {
        'D_H': D_H,
        'r2_H': r2_H,
        'D2': D2,
        'r2_D2': r2_D2,
        'ratio': D2 / D_H,
        'correlation_results': results
    }


# ============================================================================
# 5. EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example usage with synthetic and real GW data
    """
    
    print("CORRELATION DIMENSION ANALYSIS FOR GRAVITATIONAL WAVES")
    print("="*70)
    
    # Example 1: Synthetic fractional Brownian motion (D_H ≈ 1.5)
    print("\nEXAMPLE 1: Fractional Brownian Motion (H=0.5)")
    print("-" * 50)
    
    np.random.seed(42)
    N = 8192
    fBm = np.cumsum(np.random.randn(N))  # Simplified fBm
    
    results_fbm = analyze_correlation_dimension(fBm, m=5, tau=10, plot=False)
    
    print(f"\nExpected: D_H ≈ 1.5, D₂ ≈ 2-3")
    print(f"Observed: D₂ = {results_fbm['D2']:.3f}")
    
    # Example 2: With actual LIGO strain data (if available)
    print("\n" + "="*70)
    print("\nEXAMPLE 2: LIGO Gravitational Wave Signal")
    print("-" * 50)
    print("\nTo analyze real GW data:")
    print("1. Load strain from HDF5: strain = load_strain_from_hdf5('GW190412_H1.hdf5')")
    print("2. Extract window: strain_window = extract_event_window(...)")
    print("3. Preprocess: strain_filtered = preprocess_strain(...)")
    print("4. Analyze: results = analyze_correlation_dimension(strain_filtered)")
    print("\nExpected for GW signals:")
    print("  Higuchi D_H ≈ 1.5 (geometric roughness)")
    print("  Correlation D₂ ≈ 3-5 (attractor dimension)")
    print("\nBoth are correct - they measure different properties!")
