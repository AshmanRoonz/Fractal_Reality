#!/usr/bin/env python3
"""
fractal_demo_complete.py
=========================
Comprehensive demonstration of fractal tetradic sheet toolkit with analysis.

This script demonstrates the complete workflow:
1. Sheet evolution with configurable parameters
2. Closure detection
3. Comprehensive geometric analysis
4. Multi-panel visualization
5. Data export for further research

Repository: https://github.com/AshmanRoonz/Fractal_Reality
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Import toolkit modules
from fractal_tetradic_toolkit import (
    Triangle, SheetParams, FractalConfig, PhaseField,
    run_two_sheets, collect_faces, scan_closures,
    annotate_hits, print_closure_roster, default_phase,
    vortex_phase, spiral_phase, PHI, GOLDEN_ANGLE
)

from fractal_analysis import (
    analyze_sheets, create_analysis_report,
    export_to_json, export_faces_to_csv
)

# ============================================================================
# CONFIGURATIONS
# ============================================================================

class PresetConfig:
    """Preset configurations for different experiments."""
    
    @staticmethod
    def standard_icosahedral():
        """Standard icosahedral symmetry (pentagonal)."""
        return {
            'name': 'Icosahedral',
            'description': 'Pentagonal symmetry with golden deflation',
            'cfg': FractalConfig(
                max_depth=3,
                tri_prune_min_area=1e-5,
                closure_tolerance=5e-2,
                use_golden_angle=False
            ),
            'params': SheetParams(
                chi=+1,  # Will be set appropriately for each sheet
                phi_step=2.0*np.pi/5.0,
                scale_deflate=1.0/PHI,
                kappa_pitch=2.0*np.pi/5.0,
                ds_per_step=1.0,
                eta_twist=0.10,
                beta_aniso=0.35,
                gamma_cross=0.10
            ),
            'phase': default_phase
        }
    
    @staticmethod
    def golden_spiral():
        """Golden angle spiral configuration."""
        return {
            'name': 'Golden Spiral',
            'description': 'Golden angle rotation with spiral phase',
            'cfg': FractalConfig(
                max_depth=4,
                tri_prune_min_area=1e-6,
                closure_tolerance=3e-2,
                use_golden_angle=True
            ),
            'params': SheetParams(
                chi=+1,
                phi_step=GOLDEN_ANGLE,
                scale_deflate=1.0/PHI,
                kappa_pitch=GOLDEN_ANGLE,
                ds_per_step=0.8,
                eta_twist=0.15,
                beta_aniso=0.40,
                gamma_cross=0.15
            ),
            'phase': spiral_phase
        }
    
    @staticmethod
    def high_symmetry():
        """High symmetry with strong coupling."""
        return {
            'name': 'High Symmetry',
            'description': 'Hexagonal symmetry with strong phase coupling',
            'cfg': FractalConfig(
                max_depth=3,
                tri_prune_min_area=1e-5,
                closure_tolerance=4e-2,
                use_golden_angle=False
            ),
            'params': SheetParams(
                chi=+1,
                phi_step=2.0*np.pi/6.0,  # Hexagonal
                scale_deflate=0.707,      # √2/2
                kappa_pitch=2.0*np.pi/6.0,
                ds_per_step=1.0,
                eta_twist=0.20,
                beta_aniso=0.45,
                gamma_cross=0.20
            ),
            'phase': lambda x,y,s: vortex_phase(x,y,s, n=3)
        }

# ============================================================================
# MAIN WORKFLOW
# ============================================================================

def run_complete_analysis(preset_name: str = 'standard_icosahedral', output_dir: str = '/mnt/user-data/outputs'):
    """
    Run complete fractal sheet analysis workflow.
    
    Args:
        preset_name: Name of preset configuration
        output_dir: Output directory for results
    """
    # Setup
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("="*80)
    print("FRACTAL TETRADIC SHEET - COMPLETE ANALYSIS")
    print("="*80)
    
    # Load configuration
    preset_func = getattr(PresetConfig, preset_name, PresetConfig.standard_icosahedral)
    config = preset_func()
    
    print(f"\nConfiguration: {config['name']}")
    print(f"Description: {config['description']}")
    print(f"Max depth: {config['cfg'].max_depth}")
    print(f"Rotation: {config['params'].phi_step:.4f} rad ({np.degrees(config['params'].phi_step):.2f}°)")
    print(f"Deflation: {config['params'].scale_deflate:.6f}")
    
    # Create seed triangle (equilateral)
    R0 = 1.0
    seed_base = Triangle(
        V=np.array([
            [ R0, 0.0],
            [-0.5*R0,  (np.sqrt(3)/2.0)*R0],
            [-0.5*R0, -(np.sqrt(3)/2.0)*R0]
        ], dtype=float)
    )
    
    # Setup sheet parameters
    params_plus = config['params']
    params_plus.chi = +1
    
    params_minus = SheetParams(
        chi=-1,
        phi_step=config['params'].phi_step,
        scale_deflate=config['params'].scale_deflate,
        kappa_pitch=config['params'].kappa_pitch,
        ds_per_step=config['params'].ds_per_step,
        eta_twist=config['params'].eta_twist,
        beta_aniso=config['params'].beta_aniso,
        gamma_cross=config['params'].gamma_cross
    )
    
    # Evolve sheets
    print(f"\nEvolving bimetric sheets...")
    sheet_plus, sheet_minus = run_two_sheets(
        seed_base=seed_base,
        s0=0.0,
        params_plus=params_plus,
        params_minus=params_minus,
        theta_plus=config['phase'],
        theta_minus=lambda x,y,s: config['phase'](x,y,-s),  # Mirror
        cfg=config['cfg']
    )
    
    print(f"  Generated: {len(sheet_plus)} (+) + {len(sheet_minus)} (-) tetratriangles")
    
    # Collect face data
    print(f"\nCollecting face data...")
    faces_plus = collect_faces(
        sheet_plus, s=0.0, params=params_plus,
        theta_fn=config['phase'],
        theta_fn_other=lambda x,y,s: config['phase'](x,y,-s)
    )
    faces_minus = collect_faces(
        sheet_minus, s=0.0, params=params_minus,
        theta_fn=lambda x,y,s: config['phase'](x,y,-s),
        theta_fn_other=config['phase']
    )
    
    print(f"  Total faces: {len(faces_plus)} (+) + {len(faces_minus)} (-)")
    
    # Detect closures
    print(f"\nScanning for closures...")
    hits_plus = scan_closures(faces_plus, tol_vertex=1e-3, 
                               tol_closure=config['cfg'].closure_tolerance)
    hits_minus = scan_closures(faces_minus, tol_vertex=1e-3,
                                tol_closure=config['cfg'].closure_tolerance)
    
    print_closure_roster(hits_plus, "PLUS (+)")
    print_closure_roster(hits_minus, "MINUS (-)")
    
    # Comprehensive analysis
    analysis = analyze_sheets(faces_plus, faces_minus, hits_plus, hits_minus)
    
    # Display key results
    print("\n" + "="*80)
    print("KEY RESULTS")
    print("="*80)
    print(f"\nFractal Dimension:")
    print(f"  Box-counting:  D = {analysis.fractal_box.dimension:.4f} (R² = {analysis.fractal_box.r_squared:.4f})")
    print(f"  Correlation:   D = {analysis.fractal_corr.dimension:.4f} (R² = {analysis.fractal_corr.r_squared:.4f})")
    
    print(f"\nTopology (+/-):")
    print(f"  Vertices:      {analysis.topology_plus.n_vertices} / {analysis.topology_minus.n_vertices}")
    print(f"  Faces:         {analysis.topology_plus.n_faces} / {analysis.topology_minus.n_faces}")
    print(f"  Euler χ:       {analysis.topology_plus.euler_characteristic} / {analysis.topology_minus.euler_characteristic}")
    print(f"  Genus:         {analysis.topology_plus.genus} / {analysis.topology_minus.genus}")
    
    print(f"\nValidation:")
    print(f"  q=3 closures:  {analysis.validation.q3_count}")
    print(f"  q=5 closures:  {analysis.validation.q5_count}")
    print(f"  Density:       {analysis.validation.closure_density:.4f}")
    print(f"  Score:         {analysis.validation.validation_score:.3f}")
    
    # Create visualizations
    print(f"\nGenerating visualizations...")
    
    # 1. Main sheet visualization
    fig_sheets, axs = plt.subplots(1, 2, figsize=(14, 7))
    
    from fractal_tetradic_toolkit import plot_sheet
    plot_sheet(faces_plus, ax=axs[0], color_by="gnorm", label="+", cmap="plasma")
    plot_sheet(faces_minus, ax=axs[1], color_by="gnorm", label="-", cmap="viridis")
    
    annotate_hits(axs[0], hits_plus)
    annotate_hits(axs[1], hits_minus)
    
    plt.tight_layout()
    sheet_file = output_path / f'sheets_{preset_name}.png'
    plt.savefig(sheet_file, dpi=300, bbox_inches='tight')
    print(f"  Saved: {sheet_file}")
    
    # 2. Analysis report
    fig_analysis = create_analysis_report(analysis)
    analysis_file = output_path / f'analysis_{preset_name}.png'
    plt.savefig(analysis_file, dpi=300, bbox_inches='tight')
    print(f"  Saved: {analysis_file}")
    
    # Export data
    print(f"\nExporting data...")
    json_file = output_path / f'analysis_{preset_name}.json'
    export_to_json(analysis, str(json_file))
    
    csv_plus = output_path / f'faces_plus_{preset_name}.csv'
    csv_minus = output_path / f'faces_minus_{preset_name}.csv'
    export_faces_to_csv(faces_plus, str(csv_plus))
    export_faces_to_csv(faces_minus, str(csv_minus))
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nOutput directory: {output_path}")
    print(f"Files generated:")
    print(f"  - {sheet_file.name}")
    print(f"  - {analysis_file.name}")
    print(f"  - {json_file.name}")
    print(f"  - {csv_plus.name}")
    print(f"  - {csv_minus.name}")
    
    return analysis

# ============================================================================
# BATCH ANALYSIS
# ============================================================================

def run_batch_analysis(presets: list = None, output_dir: str = '/mnt/user-data/outputs'):
    """
    Run analysis on multiple configurations.
    
    Args:
        presets: List of preset names (None = all)
        output_dir: Output directory
    """
    if presets is None:
        presets = ['standard_icosahedral', 'golden_spiral', 'high_symmetry']
    
    results = {}
    
    for preset in presets:
        print(f"\n{'='*80}")
        print(f"Running: {preset}")
        print(f"{'='*80}\n")
        
        try:
            analysis = run_complete_analysis(preset, output_dir)
            results[preset] = analysis
        except Exception as e:
            print(f"ERROR in {preset}: {e}")
            import traceback
            traceback.print_exc()
    
    # Create comparison plot
    if len(results) > 1:
        print(f"\nCreating comparison plot...")
        fig, axs = plt.subplots(2, 2, figsize=(14, 12))
        
        preset_names = list(results.keys())
        colors = plt.cm.tab10(np.linspace(0, 1, len(preset_names)))
        
        # Fractal dimensions
        ax = axs[0, 0]
        for i, (name, analysis) in enumerate(results.items()):
            ax.scatter(1, analysis.fractal_box.dimension, s=100, c=[colors[i]], 
                      label=f'{name} (box)', marker='o')
            ax.scatter(2, analysis.fractal_corr.dimension, s=100, c=[colors[i]],
                      label=f'{name} (corr)', marker='s')
        ax.set_ylabel('Fractal Dimension')
        ax.set_xticks([1, 2])
        ax.set_xticklabels(['Box-counting', 'Correlation'])
        ax.set_title('Fractal Dimensions Comparison')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        
        # Topology
        ax = axs[0, 1]
        x = np.arange(len(preset_names))
        v_plus = [results[p].topology_plus.n_vertices for p in preset_names]
        v_minus = [results[p].topology_minus.n_vertices for p in preset_names]
        ax.bar(x - 0.2, v_plus, 0.4, label='+', color='crimson', alpha=0.7)
        ax.bar(x + 0.2, v_minus, 0.4, label='-', color='royalblue', alpha=0.7)
        ax.set_ylabel('Vertices')
        ax.set_xlabel('Configuration')
        ax.set_xticks(x)
        ax.set_xticklabels(preset_names, rotation=45, ha='right')
        ax.set_title('Topology Comparison')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        # Validation scores
        ax = axs[1, 0]
        scores = [results[p].validation.validation_score for p in preset_names]
        ax.bar(preset_names, scores, color=colors, alpha=0.7, edgecolor='black')
        ax.set_ylabel('Validation Score')
        ax.set_xlabel('Configuration')
        ax.set_xticklabels(preset_names, rotation=45, ha='right')
        ax.set_title('Validation Scores')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Closure counts
        ax = axs[1, 1]
        q3_counts = [results[p].validation.q3_count for p in preset_names]
        q5_counts = [results[p].validation.q5_count for p in preset_names]
        x = np.arange(len(preset_names))
        ax.bar(x - 0.2, q3_counts, 0.4, label='q=3', color='royalblue', alpha=0.7)
        ax.bar(x + 0.2, q5_counts, 0.4, label='q=5', color='crimson', alpha=0.7)
        ax.set_ylabel('Closure Count')
        ax.set_xlabel('Configuration')
        ax.set_xticks(x)
        ax.set_xticklabels(preset_names, rotation=45, ha='right')
        ax.set_title('Closure Counts')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        comparison_file = Path(output_dir) / 'comparison_all_presets.png'
        plt.savefig(comparison_file, dpi=300, bbox_inches='tight')
        print(f"Saved comparison: {comparison_file}")
    
    return results

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Run specific preset
        preset = sys.argv[1]
        run_complete_analysis(preset)
    else:
        # Run batch analysis
        run_batch_analysis()
