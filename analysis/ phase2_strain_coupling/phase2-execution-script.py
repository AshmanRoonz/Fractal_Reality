"""
PHASE 2 EXECUTION SCRIPT
Ready to run on your existing O3/O4 LIGO data

This script:
1. Loads your existing fractal dimension results
2. Re-analyzes events to extract strain coupling
3. Generates comprehensive Phase 2 report
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from glob import glob
import os

# Import your existing LIGO analysis code
# Assuming ligo_code_package.py is in the same directory
try:
    from ligo_code_package import *
except ImportError:
    print("⚠ ligo_code_package.py not found. Will define minimal functions.")

BASELINE_D = 1.5

# ============================================================================
# STEP 1: LOAD EXISTING RESULTS
# ============================================================================

def load_existing_results():
    """
    Load your existing analysis results.
    """
    print("="*70)
    print("STEP 1: LOADING EXISTING RESULTS")
    print("="*70)
    
    # Try to load from common output files
    possible_files = [
        'fractal_analysis_results.csv',
        'o4_analysis_results.csv',
        'multi_run_comparison.csv'
    ]
    
    for filename in possible_files:
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            print(f"\n✓ Loaded {filename}")
            print(f"  Shape: {df.shape}")
            print(f"  Columns: {list(df.columns)}")
            return df
    
    print("\n✗ No existing results found.")
    print("  Expected files: fractal_analysis_results.csv")
    return None


# ============================================================================
# STEP 2: CALCULATE ΔD FOR ALL EVENTS
# ============================================================================

def calculate_delta_D_column(df):
    """
    Add ΔD columns to existing results dataframe.
    """
    print("\n" + "="*70)
    print("STEP 2: CALCULATING ΔD = D - 1.5")
    print("="*70)
    
    # Find the D column (might be named differently)
    d_columns = [col for col in df.columns if 'D' in col and 'drop' not in col.lower()]
    
    if 'D_inspiral' in df.columns:
        df['delta_D_inspiral'] = df['D_inspiral'] - BASELINE_D
        print("\n✓ Calculated delta_D_inspiral")
    
    if 'D_ringdown' in df.columns:
        df['delta_D_ringdown'] = df['D_ringdown'] - BASELINE_D
        print("✓ Calculated delta_D_ringdown")
    
    if 'D_global' in df.columns:
        df['delta_D'] = df['D_global'] - BASELINE_D
        print("✓ Calculated delta_D (global)")
    elif 'Mean_D' in df.columns:
        df['delta_D'] = df['Mean_D'] - BASELINE_D
        print("✓ Calculated delta_D (mean)")
    
    # Summary statistics
    if 'delta_D' in df.columns:
        print(f"\nΔD Statistics:")
        print(f"  Mean: {df['delta_D'].mean():+.6f}")
        print(f"  Std:  {df['delta_D'].std():.6f}")
        print(f"  Min:  {df['delta_D'].min():+.6f}")
        print(f"  Max:  {df['delta_D'].max():+.6f}")
        
        # Count by sign
        n_positive = (df['delta_D'] > 0).sum()
        n_negative = (df['delta_D'] < 0).sum()
        n_baseline = (np.abs(df['delta_D']) < 0.01).sum()
        
        print(f"\n  Enhanced (ΔD > 0):    {n_positive} events")
        print(f"  Suppressed (ΔD < 0):  {n_negative} events")
        print(f"  Baseline (|ΔD|<0.01): {n_baseline} events")
    
    return df


# ============================================================================
# STEP 3: EXTRACT STRAIN INFORMATION (IF AVAILABLE)
# ============================================================================

def add_strain_coupling_analysis(df, data_directory='./ligo_data'):
    """
    Re-analyze events to extract strain envelopes and fit coupling.
    
    This requires access to the original HDF5 files.
    """
    print("\n" + "="*70)
    print("STEP 3: STRAIN COUPLING ANALYSIS")
    print("="*70)
    
    # Check if we have access to data files
    if not os.path.exists(data_directory):
        print(f"\n⚠ Data directory not found: {data_directory}")
        print("  Skipping strain coupling analysis.")
        print("  Will work with existing D measurements only.")
        return df
    
    # Find all HDF5 files
    h5_files = glob(os.path.join(data_directory, '*.hdf5')) + \
               glob(os.path.join(data_directory, '*.hdf'))
    
    if len(h5_files) == 0:
        print(f"\n⚠ No HDF5 files found in {data_directory}")
        return df
    
    print(f"\n✓ Found {len(h5_files)} HDF5 files")
    
    # For each event in results, try to find and analyze strain
    h_peaks = []
    h_means = []
    
    for idx, row in df.iterrows():
        # Try to find matching file
        event = row.get('event', '')
        detector = row.get('detector', '')
        
        matching_file = None
        for f in h5_files:
            if event in f and detector in f:
                matching_file = f
                break
        
        if matching_file:
            try:
                # Load and extract strain (simplified)
                with h5py.File(matching_file, 'r') as hf:
                    strain = hf['strain']['Strain'][:]
                    
                # Extract envelope (simplified - just use peak)
                h_peak = np.max(np.abs(strain))
                h_mean = np.mean(np.abs(strain))
                
                h_peaks.append(h_peak)
                h_means.append(h_mean)
                
            except Exception as e:
                print(f"  ⚠ Error processing {matching_file}: {e}")
                h_peaks.append(np.nan)
                h_means.append(np.nan)
        else:
            h_peaks.append(np.nan)
            h_means.append(np.nan)
    
    df['h_peak'] = h_peaks
    df['h_mean'] = h_means
    
    n_with_strain = (~df['h_peak'].isna()).sum()
    print(f"\n✓ Extracted strain for {n_with_strain}/{len(df)} events")
    
    return df


# ============================================================================
# STEP 4: FIT COUPLING MODELS
# ============================================================================

def fit_and_compare_models(df):
    """
    Fit ΔD vs |h| for both linear and quadratic models.
    """
    print("\n" + "="*70)
    print("STEP 4: COUPLING MODEL FIT")
    print("="*70)
    
    if 'delta_D' not in df.columns:
        print("\n✗ No delta_D column found. Run Step 2 first.")
        return None
    
    if 'h_peak' not in df.columns:
        print("\n⚠ No strain data available.")
        print("  Using simplified analysis with D values only.")
        return None
    
    # Remove NaN values
    mask = df['delta_D'].notna() & df['h_peak'].notna() & (df['h_peak'] > 0)
    df_clean = df[mask].copy()
    
    if len(df_clean) < 5:
        print(f"\n✗ Insufficient data points: {len(df_clean)}")
        return None
    
    print(f"\n✓ Fitting with {len(df_clean)} events")
    
    x1 = df_clean['h_peak'].values
    x2 = df_clean['h_peak'].values**2
    y = df_clean['delta_D'].values
    
    # Linear fit: ΔD = β₁·|h|
    beta1 = (x1 @ y) / (x1 @ x1)
    y_pred1 = beta1 * x1
    r2_1 = 1 - np.sum((y - y_pred1)**2) / np.sum((y - y.mean())**2)
    
    # Quadratic fit: ΔD = β₂·|h|²
    beta2 = (x2 @ y) / (x2 @ x2)
    y_pred2 = beta2 * x2
    r2_2 = 1 - np.sum((y - y_pred2)**2) / np.sum((y - y.mean())**2)
    
    print(f"\nLINEAR MODEL (p=1): ΔD = β·|h|")
    print(f"  β = {beta1:.3e}")
    print(f"  R² = {r2_1:.4f}")
    
    print(f"\nQUADRATIC MODEL (p=2): ΔD = β·|h|²")
    print(f"  β = {beta2:.3e}")
    print(f"  R² = {r2_2:.4f}")
    
    if r2_1 > r2_2:
        print(f"\n✓ LINEAR model preferred (ΔR² = +{r2_1 - r2_2:.4f})")
        best = 'linear'
    else:
        print(f"\n✓ QUADRATIC model preferred (ΔR² = +{r2_2 - r2_1:.4f})")
        best = 'quadratic'
    
    return {
        'beta_linear': beta1,
        'r2_linear': r2_1,
        'beta_quad': beta2,
        'r2_quad': r2_2,
        'best_model': best,
        'n_points': len(df_clean)
    }


# ============================================================================
# STEP 5: GENERATE VISUALIZATIONS
# ============================================================================

def create_phase2_visualizations(df, coupling_results=None):
    """
    Create comprehensive Phase 2 visualizations.
    """
    print("\n" + "="*70)
    print("STEP 5: CREATING VISUALIZATIONS")
    print("="*70)
    
    fig = plt.figure(figsize=(16, 10))
    
    # Plot 1: ΔD distribution
    ax1 = plt.subplot(2, 3, 1)
    if 'delta_D' in df.columns:
        ax1.hist(df['delta_D'].dropna(), bins=20, alpha=0.7, edgecolor='black')
        ax1.axvline(0, color='red', linestyle='--', linewidth=2, label='Baseline')
        ax1.set_xlabel('ΔD = D - 1.5')
        ax1.set_ylabel('Count')
        ax1.set_title('ΔD Distribution')
        ax1.legend()
        ax1.grid(alpha=0.3)
    
    # Plot 2: ΔD by detector
    ax2 = plt.subplot(2, 3, 2)
    if 'detector' in df.columns and 'delta_D' in df.columns:
        detectors = df['detector'].unique()
        positions = np.arange(len(detectors))
        means = [df[df['detector'] == det]['delta_D'].mean() for det in detectors]
        stds = [df[df['detector'] == det]['delta_D'].std() for det in detectors]
        
        ax2.bar(positions, means, yerr=stds, alpha=0.7, capsize=10, edgecolor='black')
        ax2.axhline(0, color='red', linestyle='--', linewidth=2)
        ax2.set_xticks(positions)
        ax2.set_xticklabels(detectors)
        ax2.set_ylabel('Mean ΔD')
        ax2.set_title('ΔD by Detector')
        ax2.grid(alpha=0.3, axis='y')
    
    # Plot 3: ΔD vs |h| (if available)
    ax3 = plt.subplot(2, 3, 3)
    if 'delta_D' in df.columns and 'h_peak' in df.columns:
        mask = df['delta_D'].notna() & df['h_peak'].notna()
        ax3.scatter(df[mask]['h_peak'], df[mask]['delta_D'], alpha=0.6, s=50)
        ax3.axhline(0, color='red', linestyle='--', alpha=0.5)
        ax3.set_xlabel('Strain Peak |h|')
        ax3.set_ylabel('ΔD')
        ax3.set_title('Strain Coupling')
        ax3.grid(alpha=0.3)
        
        # Add fit line if available
        if coupling_results:
            x_fit = np.linspace(df[mask]['h_peak'].min(), df[mask]['h_peak'].max(), 100)
            if coupling_results['best_model'] == 'linear':
                y_fit = coupling_results['beta_linear'] * x_fit
                label = f"Linear: β={coupling_results['beta_linear']:.2e}"
            else:
                y_fit = coupling_results['beta_quad'] * x_fit**2
                label = f"Quad: β={coupling_results['beta_quad']:.2e}"
            ax3.plot(x_fit, y_fit, 'r-', linewidth=2, label=label)
            ax3.legend()
    
    # Plot 4: D vs ΔD (deviation from baseline)
    ax4 = plt.subplot(2, 3, 4)
    if 'delta_D' in df.columns:
        D_values = df['delta_D'] + BASELINE_D
        ax4.scatter(D_values, df['delta_D'], alpha=0.6, s=50)
        ax4.axhline(0, color='red', linestyle='--', linewidth=2)
        ax4.axvline(BASELINE_D, color='blue', linestyle='--', linewidth=2, label='Baseline D=1.5')
        ax4.set_xlabel('Measured D')
        ax4.set_ylabel('ΔD')
        ax4.set_title('Deviation from Baseline')
        ax4.legend()
        ax4.grid(alpha=0.3)
    
    # Plot 5: Summary statistics
    ax5 = plt.subplot(2, 3, 5)
    ax5.axis('off')
    
    summary_text = "PHASE 2 SUMMARY STATISTICS\n" + "="*40 + "\n\n"
    
    if 'delta_D' in df.columns:
        summary_text += f"ΔD = D - 1.5:\n"
        summary_text += f"  Mean:   {df['delta_D'].mean():+.6f}\n"
        summary_text += f"  Median: {df['delta_D'].median():+.6f}\n"
        summary_text += f"  Std:    {df['delta_D'].std():.6f}\n"
        summary_text += f"  N:      {df['delta_D'].count()}\n\n"
    
    if coupling_results:
        summary_text += f"STRAIN COUPLING:\n"
        summary_text += f"  Best model: {coupling_results['best_model']}\n"
        if coupling_results['best_model'] == 'linear':
            summary_text += f"  β = {coupling_results['beta_linear']:.3e}\n"
            summary_text += f"  R² = {coupling_results['r2_linear']:.4f}\n"
        else:
            summary_text += f"  β = {coupling_results['beta_quad']:.3e}\n"
            summary_text += f"  R² = {coupling_results['r2_quad']:.4f}\n"
        summary_text += f"  N = {coupling_results['n_points']} events\n"
    
    ax5.text(0.1, 0.5, summary_text, fontsize=10, verticalalignment='center',
             family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    # Plot 6: Phase comparison (if available)
    ax6 = plt.subplot(2, 3, 6)
    if 'delta_D_inspiral' in df.columns and 'delta_D_ringdown' in df.columns:
        ax6.scatter(df['delta_D_inspiral'], df['delta_D_ringdown'], alpha=0.6, s=50)
        ax6.plot([-0.5, 0.5], [-0.5, 0.5], 'r--', alpha=0.5, label='Equal')
        ax6.axhline(0, color='gray', linestyle=':', alpha=0.5)
        ax6.axvline(0, color='gray', linestyle=':', alpha=0.5)
        ax6.set_xlabel('ΔD Inspiral')
        ax6.set_ylabel('ΔD Ringdown')
        ax6.set_title('Phase Comparison')
        ax6.legend()
        ax6.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('phase2_analysis_complete.png', dpi=300, bbox_inches='tight')
    print("\n✓ Saved: phase2_analysis_complete.png")
    
    return fig


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_phase2_analysis():
    """
    Complete Phase 2 analysis pipeline.
    """
    print("\n" + "🚀"*35)
    print("PHASE 2: COMPLETE STRAIN COUPLING ANALYSIS")
    print("🚀"*35)
    
    # Step 1: Load existing results
    df = load_existing_results()
    if df is None:
        print("\n✗ Cannot proceed without existing results.")
        print("  Run your O3/O4 analysis first to generate results CSV.")
        return
    
    # Step 2: Calculate ΔD
    df = calculate_delta_D_column(df)
    
    # Step 3: Add strain coupling (if data available)
    df = add_strain_coupling_analysis(df)
    
    # Step 4: Fit coupling models
    coupling_results = fit_and_compare_models(df)
    
    # Step 5: Create visualizations
    fig = create_phase2_visualizations(df, coupling_results)
    
    # Save enhanced results
    output_file = 'phase2_results_with_deltaD.csv'
    df.to_csv(output_file, index=False)
    print(f"\n✓ Saved enhanced results: {output_file}")
    
    # Final summary
    print("\n" + "="*70)
    print("PHASE 2 ANALYSIS COMPLETE!")
    print("="*70)
    print("\nKey Findings:")
    if 'delta_D' in df.columns:
        mean_delta = df['delta_D'].mean()
        print(f"  Mean ΔD = {mean_delta:+.6f}")
        if abs(mean_delta) < 0.01:
            print(f"  → Baseline validated (deviation < 1%)")
        elif mean_delta > 0:
            print(f"  → Enhanced fractalization detected")
        else:
            print(f"  → Suppressed fractalization detected")
    
    if coupling_results:
        print(f"\n  Best coupling model: {coupling_results['best_model']}")
        print(f"  R² = {coupling_results.get('r2_' + coupling_results['best_model'], 0):.4f}")
    
    print("\n📊 Generated: phase2_analysis_complete.png")
    print("📁 Generated: phase2_results_with_deltaD.csv")
    
    plt.show()


# ============================================================================
# RUN IT!
# ============================================================================

if __name__ == "__main__":
    run_phase2_analysis()
