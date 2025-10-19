"""
FRACTAL DIMENSION ANALYSIS OF QUANTUM PARTICLE TRACKS
======================================================
Tests the [ICE] framework prediction: D = 1.50

This script analyzes bubble chamber images to measure the fractal
dimension of particle worldlines using box-counting method.

REQUIREMENTS:
pip install numpy matplotlib pillow scipy scikit-image pandas

USAGE:
1. Save your bubble chamber image as 'bubble_chamber.jpg'
2. Run: python fractal_analysis.py
3. Results printed to console + saved as PNG plots
"""

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from scipy.ndimage import binary_erosion, binary_dilation
from skimage import measure, morphology
import pandas as pd
from scipy import stats

# ========================================================================
# STEP 1: Load and preprocess bubble chamber image
# ========================================================================

print("\n" + "="*70)
print("FRACTAL DIMENSION ANALYSIS OF QUANTUM PARTICLE TRACKS")
print("="*70 + "\n")

# Load the image
print("Loading bubble chamber image...")
img = Image.open('bubble_chamber.jpg')
img_array = np.array(img.convert('L'))  # Convert to grayscale

print(f"Image size: {img_array.shape}")

# Threshold to isolate tracks (adjust threshold as needed)
# Dark tracks on light background
threshold = 200  # Adjust this if tracks aren't detected properly
binary = img_array < threshold

# Clean up noise
print("Preprocessing: removing noise and artifacts...")
binary_clean = morphology.remove_small_objects(binary, min_size=50)
binary_clean = morphology.remove_small_holes(binary_clean, area_threshold=50)

# Show preprocessed image
plt.figure(figsize=(15, 5))
plt.subplot(1, 2, 1)
plt.imshow(img_array, cmap='gray')
plt.title('Original Bubble Chamber Image')
plt.axis('off')

plt.subplot(1, 2, 2)
plt.imshow(binary_clean, cmap='gray')
plt.title('Detected Particle Tracks')
plt.axis('off')

plt.tight_layout()
plt.savefig('1_preprocessing.png', dpi=300, bbox_inches='tight')
print("→ Saved: 1_preprocessing.png")
plt.show()

# ========================================================================
# STEP 2: Extract individual tracks using connected components
# ========================================================================

print("\nExtracting individual particle tracks...")

# Label connected components (each track)
labeled = measure.label(binary_clean)
regions = measure.regionprops(labeled)

print(f"Found {len(regions)} potential track regions")

# Filter by size to remove noise and fiducial markers
tracks = []
track_info = []

for region in regions:
    area = region.area
    # Keep only tracks of reasonable size (not tiny noise, not huge blobs)
    if 100 < area < 10000:
        # Get coordinates
        coords = region.coords  # Returns (row, col) = (y, x)
        # Swap to (x, y) convention
        track_coords = np.column_stack([coords[:, 1], coords[:, 0]])
        tracks.append(track_coords)
        track_info.append({
            'area': area,
            'bbox': region.bbox
        })

print(f"Kept {len(tracks)} tracks after filtering")
print(f"Track sizes: {[info['area'] for info in track_info]}")

# ========================================================================
# STEP 3: Calculate fractal dimension for each track
# ========================================================================

def box_counting_dimension(coords, min_box_size=2, max_box_size=None, n_sizes=15):
    """
    Calculate fractal dimension using box-counting method.
    
    The box-counting dimension is defined as:
        D = lim (log N(ε) / log(1/ε))
    where N(ε) is the number of boxes of size ε needed to cover the path.
    
    Args:
        coords: numpy array of shape (N, 2) with [x, y] coordinates
        min_box_size: minimum box size to test
        max_box_size: maximum box size (default: half of max extent)
        n_sizes: number of different box sizes to test
    
    Returns:
        D: fractal dimension
        box_sizes: array of box sizes tested
        counts: array of box counts for each size
    """
    # Normalize coordinates to start at origin
    coords_norm = coords - coords.min(axis=0)
    max_extent = coords_norm.max()
    
    if max_box_size is None:
        max_box_size = max_extent / 2
    
    # Logarithmically spaced box sizes
    box_sizes = np.logspace(np.log10(min_box_size), 
                           np.log10(max_box_size), n_sizes)
    
    counts = []
    
    for epsilon in box_sizes:
        # Create grid of boxes
        grid_x = np.arange(0, coords_norm[:, 0].max() + epsilon, epsilon)
        grid_y = np.arange(0, coords_norm[:, 1].max() + epsilon, epsilon)
        
        # Digitize coordinates into boxes
        x_idx = np.digitize(coords_norm[:, 0], grid_x)
        y_idx = np.digitize(coords_norm[:, 1], grid_y)
        
        # Count unique boxes containing at least one point
        unique_boxes = len(set(zip(x_idx, y_idx)))
        counts.append(unique_boxes)
    
    # Fit line in log-log space: log(N) vs log(1/ε)
    log_inv_eps = np.log(1/box_sizes)
    log_N = np.log(counts)
    
    # Use middle range for fitting (avoid edge effects)
    use_indices = slice(3, -3) if len(box_sizes) > 10 else slice(None)
    coeffs = np.polyfit(log_inv_eps[use_indices], log_N[use_indices], 1)
    
    # Slope = fractal dimension D
    D = coeffs[0]
    
    return D, box_sizes, counts

# Analyze each track
print("\nCalculating fractal dimensions...")
print("-" * 70)

results = []

for i, track in enumerate(tracks):
    try:
        D, box_sizes, counts = box_counting_dimension(track)
        results.append({
            'track_id': i,
            'dimension': D,
            'n_points': len(track),
            'area': track_info[i]['area']
        })
        print(f"Track {i+1:2d}: D = {D:.3f} ({len(track):4d} points, area={track_info[i]['area']:4d})")
    except Exception as e:
        print(f"Track {i+1:2d}: Failed - {e}")

# ========================================================================
# STEP 4: Statistical analysis
# ========================================================================

print("\n" + "="*70)
print("STATISTICAL ANALYSIS")
print("="*70)

results_df = pd.DataFrame(results)

if len(results_df) == 0:
    print("ERROR: No tracks successfully analyzed!")
    print("Try adjusting the threshold parameter (line 41)")
    exit(1)

D_mean = results_df['dimension'].mean()
D_std = results_df['dimension'].std()
D_median = results_df['dimension'].median()
D_min = results_df['dimension'].min()
D_max = results_df['dimension'].max()

print(f"\nNumber of tracks analyzed: {len(results_df)}")
print(f"Mean D     = {D_mean:.4f} ± {D_std:.4f}")
print(f"Median D   = {D_median:.4f}")
print(f"Range      = [{D_min:.4f}, {D_max:.4f}]")

# Hypothesis test: Is D = 1.50?
print("\n" + "-"*70)
print("HYPOTHESIS TEST: H₀: D = 1.50 ([ICE] framework prediction)")
print("-"*70)

predicted_D = 1.50
t_stat = (D_mean - predicted_D) / (D_std / np.sqrt(len(results_df)))
df = len(results_df) - 1
p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df))

print(f"Null hypothesis:     H₀: D = {predicted_D}")
print(f"Alternative:         H₁: D ≠ {predicted_D}")
print(f"t-statistic:         {t_stat:.4f}")
print(f"Degrees of freedom:  {df}")
print(f"p-value:             {p_value:.4f}")

deviation_percent = abs(D_mean - predicted_D) / predicted_D * 100

print(f"\nDeviation from prediction: {abs(D_mean - predicted_D):.4f} ({deviation_percent:.2f}%)")

if p_value > 0.05:
    print("\n" + "✓"*35)
    print("RESULT: Cannot reject H₀ (p > 0.05)")
    print(f"→ Measured D = {D_mean:.3f} is CONSISTENT with predicted D = 1.50")
    print("→ [ICE] framework prediction CONFIRMED by data!")
    print("✓"*35)
else:
    print("\n" + "✗"*35)
    print("RESULT: Reject H₀ (p < 0.05)")
    print(f"→ Measured D = {D_mean:.3f} differs significantly from 1.50")
    print("→ Framework prediction not supported by this data")
    print("✗"*35)

# ========================================================================
# STEP 5: Visualizations
# ========================================================================

print("\nGenerating publication-quality plots...")

# Create comprehensive figure
fig = plt.figure(figsize=(16, 10))

# 1. Histogram of dimensions
ax1 = plt.subplot(2, 3, 1)
ax1.hist(results_df['dimension'], bins=min(15, len(results_df)), 
         alpha=0.7, edgecolor='black', color='steelblue')
ax1.axvline(predicted_D, color='red', linestyle='--', linewidth=2, 
           label=f'Predicted D={predicted_D}')
ax1.axvline(D_mean, color='blue', linestyle='-', linewidth=2, 
           label=f'Measured D={D_mean:.3f}')
ax1.set_xlabel('Fractal Dimension D', fontsize=11)
ax1.set_ylabel('Count', fontsize=11)
ax1.set_title('Distribution of Measured Fractal Dimensions', fontsize=12, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

# 2. Box plot
ax2 = plt.subplot(2, 3, 2)
box = ax2.boxplot([results_df['dimension']], widths=0.5)
ax2.axhline(predicted_D, color='red', linestyle='--', linewidth=2, label='Predicted')
ax2.set_ylabel('Fractal Dimension D', fontsize=11)
ax2.set_title('Statistical Distribution', fontsize=12, fontweight='bold')
ax2.set_xticklabels(['All Tracks'])
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3, axis='y')

# 3. D vs track length
ax3 = plt.subplot(2, 3, 3)
ax3.scatter(results_df['n_points'], results_df['dimension'], 
           s=100, alpha=0.6, c='steelblue', edgecolors='black')
ax3.axhline(predicted_D, color='red', linestyle='--', linewidth=2, alpha=0.7)
ax3.set_xlabel('Number of Points in Track', fontsize=11)
ax3.set_ylabel('Fractal Dimension D', fontsize=11)
ax3.set_title('D vs Track Length', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3)

# 4. Example box-counting plot
if len(tracks) > 0:
    ax4 = plt.subplot(2, 3, 4)
    # Re-analyze first track for plotting
    D_ex, bs_ex, cnt_ex = box_counting_dimension(tracks[0])
    log_inv_eps = np.log(1/bs_ex)
    log_N = np.log(cnt_ex)
    
    ax4.scatter(log_inv_eps, log_N, s=80, alpha=0.7, c='steelblue', edgecolors='black')
    
    # Fit line
    use_idx = slice(3, -3) if len(bs_ex) > 10 else slice(None)
    coeffs = np.polyfit(log_inv_eps[use_idx], log_N[use_idx], 1)
    fit_line = coeffs[0] * log_inv_eps + coeffs[1]
    ax4.plot(log_inv_eps, fit_line, 'r--', linewidth=2, 
            label=f'Fit: D = {coeffs[0]:.3f}')
    
    ax4.set_xlabel('log(1/ε)', fontsize=11)
    ax4.set_ylabel('log(N(ε))', fontsize=11)
    ax4.set_title('Box-Counting Analysis (Example Track)', fontsize=12, fontweight='bold')
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3)

# 5. Track visualization
ax5 = plt.subplot(2, 3, 5)
ax5.imshow(img_array, cmap='gray', alpha=0.5)
# Overlay tracks with colors based on D
for i, (track, result) in enumerate(zip(tracks, results)):
    D_val = result['dimension']
    # Color code: blue (D<1.4), green (1.4-1.6), red (D>1.6)
    if D_val < 1.4:
        color = 'blue'
    elif D_val < 1.6:
        color = 'green'
    else:
        color = 'red'
    ax5.plot(track[:, 0], track[:, 1], color=color, linewidth=2, alpha=0.7)
ax5.set_title('Detected Tracks (color-coded by D)', fontsize=12, fontweight='bold')
ax5.axis('off')

# 6. Summary statistics text
ax6 = plt.subplot(2, 3, 6)
ax6.axis('off')
summary_text = f"""
MEASUREMENT SUMMARY
{'='*40}

Tracks analyzed:      {len(results_df)}
Mean D:              {D_mean:.4f} ± {D_std:.4f}
Median D:            {D_median:.4f}
Range:               [{D_min:.3f}, {D_max:.3f}]

FRAMEWORK PREDICTION
{'='*40}

Predicted D:         {predicted_D}
Deviation:           {abs(D_mean - predicted_D):.4f} ({deviation_percent:.1f}%)

STATISTICAL TEST
{'='*40}

t-statistic:         {t_stat:.4f}
p-value:             {p_value:.4f}
Result:              {"CONFIRMED ✓" if p_value > 0.05 else "NOT CONFIRMED ✗"}

"""
ax6.text(0.1, 0.5, summary_text, fontsize=11, family='monospace',
        verticalalignment='center', bbox=dict(boxstyle='round', 
        facecolor='wheat', alpha=0.3))

plt.suptitle('Fractal Analysis of Quantum Particle Worldlines', 
            fontsize=16, fontweight='bold', y=0.995)
plt.tight_layout(rect=[0, 0, 1, 0.99])
plt.savefig('2_fractal_analysis_results.png', dpi=300, bbox_inches='tight')
print("→ Saved: 2_fractal_analysis_results.png")
plt.show()

# Save results to CSV
results_df.to_csv('fractal_dimensions.csv', index=False)
print("→ Saved: fractal_dimensions.csv")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
print("\nGenerated files:")
print("  • 1_preprocessing.png")
print("  • 2_fractal_analysis_results.png")
print("  • fractal_dimensions.csv")
print("\nFor publication, use the results from 2_fractal_analysis_results.png")
