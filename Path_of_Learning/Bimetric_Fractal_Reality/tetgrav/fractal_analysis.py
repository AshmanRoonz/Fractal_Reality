#!/usr/bin/env python3
"""
fractal_analysis.py
===================
Advanced analysis tools for fractal tetradic sheets:
- Fractal dimension computation
- Topology analysis (Euler characteristic, genus)
- Phase field coherence metrics
- Cross-sheet validation measures
- Export utilities for further analysis

Repository: https://github.com/AshmanRoonz/Fractal_Reality
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
import json

from fractal_tetradic_toolkit import (
    Triangle, Tetratriangle, FaceRecord, ClosureHit,
    collect_faces, cluster_vertices
)

# ============================================================================
# FRACTAL DIMENSION ANALYSIS
# ============================================================================

@dataclass
class FractalDimension:
    """Results from fractal dimension computation."""
    method: str
    dimension: float
    r_squared: float
    scales: np.ndarray
    counts: np.ndarray

def box_counting_dimension(
    faces: List[FaceRecord],
    n_scales: int = 10,
    scale_range: Tuple[float, float] = (0.01, 1.0)
) -> FractalDimension:
    """
    Compute fractal dimension via box-counting method.
    
    D = -lim_{ε→0} log N(ε) / log ε
    
    Args:
        faces: List of face records
        n_scales: Number of box sizes to test
        scale_range: (min_scale, max_scale) range
    
    Returns:
        FractalDimension result
    """
    # Collect all vertex coordinates
    coords = []
    for f in faces:
        coords.extend(f.tri.V)
    coords = np.array(coords)
    
    if len(coords) == 0:
        return FractalDimension("box-counting", 0.0, 0.0, np.array([]), np.array([]))
    
    # Compute bounding box
    x_min, y_min = coords.min(axis=0)
    x_max, y_max = coords.max(axis=0)
    
    # Test different box sizes
    scales = np.logspace(np.log10(scale_range[0]), np.log10(scale_range[1]), n_scales)
    counts = []
    
    for eps in scales:
        # Grid dimensions
        nx = int(np.ceil((x_max - x_min) / eps))
        ny = int(np.ceil((y_max - y_min) / eps))
        
        # Count occupied boxes
        occupied = set()
        for x, y in coords:
            i = int((x - x_min) / eps)
            j = int((y - y_min) / eps)
            occupied.add((i, j))
        
        counts.append(len(occupied))
    
    counts = np.array(counts)
    
    # Linear regression on log-log plot
    log_scales = np.log(scales)
    log_counts = np.log(counts)
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(log_scales, log_counts)
    dimension = -slope
    r_squared = r_value ** 2
    
    return FractalDimension(
        method="box-counting",
        dimension=dimension,
        r_squared=r_squared,
        scales=scales,
        counts=counts
    )

def correlation_dimension(
    faces: List[FaceRecord],
    n_points: int = 1000,
    n_scales: int = 20
) -> FractalDimension:
    """
    Compute correlation dimension via pair distance distribution.
    
    Args:
        faces: List of face records
        n_points: Number of sample points
        n_scales: Number of distance scales
    
    Returns:
        FractalDimension result
    """
    # Sample points from face centroids (weighted by area)
    centroids = []
    areas = []
    for f in faces:
        centroids.append(f.tri.centroid())
        areas.append(f.tri.area())
    
    if len(centroids) == 0:
        return FractalDimension("correlation", 0.0, 0.0, np.array([]), np.array([]))
    
    centroids = np.array(centroids)
    areas = np.array(areas)
    areas = areas / areas.sum()
    
    # Sample points
    indices = np.random.choice(len(centroids), size=min(n_points, len(centroids)), 
                               replace=True, p=areas)
    points = centroids[indices]
    
    # Compute pairwise distances
    from scipy.spatial.distance import pdist
    distances = pdist(points)
    
    # Test different scales
    d_min, d_max = distances.min(), distances.max()
    scales = np.logspace(np.log10(d_min + 1e-9), np.log10(d_max), n_scales)
    
    counts = []
    for r in scales:
        count = np.sum(distances < r)
        counts.append(count)
    
    counts = np.array(counts, dtype=float)
    
    # Linear regression on log-log plot
    log_scales = np.log(scales)
    log_counts = np.log(counts + 1)  # Avoid log(0)
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(log_scales, log_counts)
    dimension = slope
    r_squared = r_value ** 2
    
    return FractalDimension(
        method="correlation",
        dimension=dimension,
        r_squared=r_squared,
        scales=scales,
        counts=counts
    )

# ============================================================================
# TOPOLOGY ANALYSIS
# ============================================================================

@dataclass
class TopologyMetrics:
    """Topological properties of the mesh."""
    n_vertices: int
    n_edges: int
    n_faces: int
    euler_characteristic: int
    genus: int
    avg_valence: float
    valence_dist: Dict[int, int]

def compute_topology(faces: List[FaceRecord], tol: float = 1e-3) -> TopologyMetrics:
    """
    Compute topological properties of the mesh.
    
    Uses Euler characteristic: χ = V - E + F = 2 - 2g
    where g is the genus (number of holes).
    
    Args:
        faces: List of face records
        tol: Vertex clustering tolerance
    
    Returns:
        TopologyMetrics
    """
    # Cluster vertices
    vertices = cluster_vertices(faces, tol=tol)
    n_vertices = len(vertices)
    
    # Count faces
    n_faces = len(faces)
    
    # Count edges (each edge shared by exactly 2 faces in closed mesh)
    # For now, approximate as 3F/2 (each face has 3 edges, each edge shared by 2 faces)
    n_edges = 3 * n_faces // 2
    
    # Euler characteristic
    chi = n_vertices - n_edges + n_faces
    
    # Genus (assuming orientable surface)
    genus = (2 - chi) // 2
    
    # Valence distribution
    valence_dist = {}
    total_valence = 0
    for v in vertices:
        val = len(set(v.faces))
        valence_dist[val] = valence_dist.get(val, 0) + 1
        total_valence += val
    
    avg_valence = total_valence / n_vertices if n_vertices > 0 else 0
    
    return TopologyMetrics(
        n_vertices=n_vertices,
        n_edges=n_edges,
        n_faces=n_faces,
        euler_characteristic=chi,
        genus=genus,
        avg_valence=avg_valence,
        valence_dist=valence_dist
    )

# ============================================================================
# PHASE COHERENCE ANALYSIS
# ============================================================================

@dataclass
class PhaseCoherence:
    """Phase field coherence metrics."""
    mean_gradient: float
    std_gradient: float
    mean_twist: float
    std_twist: float
    gradient_correlation: float
    twist_phi_correlation: float

def analyze_phase_coherence(faces: List[FaceRecord]) -> PhaseCoherence:
    """
    Analyze phase field coherence across the sheet.
    
    Args:
        faces: List of face records
    
    Returns:
        PhaseCoherence metrics
    """
    if len(faces) == 0:
        return PhaseCoherence(0, 0, 0, 0, 0, 0)
    
    gradients = np.array([f.gnorm for f in faces])
    twists = np.array([f.phi for f in faces])
    
    # Basic statistics
    mean_grad = np.mean(gradients)
    std_grad = np.std(gradients)
    mean_twist = np.mean(twists)
    std_twist = np.std(twists)
    
    # Correlations
    # Spatial gradient correlation (neighboring faces should have similar gradients)
    grad_corr = 0.0  # Placeholder - requires spatial adjacency info
    
    # Twist-phi correlation
    if len(gradients) > 1 and np.std(gradients) > 0 and np.std(twists) > 0:
        twist_phi_corr = np.corrcoef(gradients, twists)[0, 1]
    else:
        twist_phi_corr = 0.0
    
    return PhaseCoherence(
        mean_gradient=float(mean_grad),
        std_gradient=float(std_grad),
        mean_twist=float(mean_twist),
        std_twist=float(std_twist),
        gradient_correlation=float(grad_corr),
        twist_phi_correlation=float(twist_phi_corr)
    )

# ============================================================================
# CROSS-SHEET VALIDATION
# ============================================================================

@dataclass
class ValidationMetrics:
    """Cross-sheet validation measures."""
    closure_density: float
    q3_count: int
    q5_count: int
    mean_residue: float
    std_residue: float
    validation_score: float

def compute_validation(
    hits_plus: List[ClosureHit],
    hits_minus: List[ClosureHit],
    n_faces_total: int
) -> ValidationMetrics:
    """
    Compute validation metrics from closure detection.
    
    Args:
        hits_plus: Closures on + sheet
        hits_minus: Closures on - sheet
        n_faces_total: Total number of faces (both sheets)
    
    Returns:
        ValidationMetrics
    """
    all_hits = hits_plus + hits_minus
    
    if len(all_hits) == 0:
        return ValidationMetrics(0, 0, 0, 0, 0, 0)
    
    # Count by valence
    q3_count = sum(1 for h in all_hits if h.q_valence == 3)
    q5_count = sum(1 for h in all_hits if h.q_valence == 5)
    
    # Closure density (closures per face)
    closure_density = len(all_hits) / n_faces_total if n_faces_total > 0 else 0
    
    # Residue statistics
    residues = [h.residue for h in all_hits]
    mean_residue = np.mean(residues)
    std_residue = np.std(residues)
    
    # Validation score (higher = better closure quality)
    # Score based on: density, small residues, balanced q3/q5 ratio
    ideal_ratio = 12 / 20  # Icosahedron has 12 q5, 20 q3 faces
    actual_ratio = q5_count / (q3_count + 1e-9)
    ratio_score = 1.0 - abs(actual_ratio - ideal_ratio)
    
    residue_score = np.exp(-mean_residue * 10)  # Exponential decay
    density_score = min(closure_density * 10, 1.0)  # Cap at 1.0
    
    validation_score = (ratio_score + residue_score + density_score) / 3.0
    
    return ValidationMetrics(
        closure_density=float(closure_density),
        q3_count=q3_count,
        q5_count=q5_count,
        mean_residue=float(mean_residue),
        std_residue=float(std_residue),
        validation_score=float(validation_score)
    )

# ============================================================================
# COMPREHENSIVE ANALYSIS
# ============================================================================

@dataclass
class ComprehensiveAnalysis:
    """Complete analysis results."""
    fractal_box: FractalDimension
    fractal_corr: FractalDimension
    topology_plus: TopologyMetrics
    topology_minus: TopologyMetrics
    phase_plus: PhaseCoherence
    phase_minus: PhaseCoherence
    validation: ValidationMetrics

def analyze_sheets(
    faces_plus: List[FaceRecord],
    faces_minus: List[FaceRecord],
    hits_plus: List[ClosureHit],
    hits_minus: List[ClosureHit]
) -> ComprehensiveAnalysis:
    """
    Perform comprehensive analysis on both sheets.
    
    Args:
        faces_plus: Faces from + sheet
        faces_minus: Faces from - sheet
        hits_plus: Closures on + sheet
        hits_minus: Closures on - sheet
    
    Returns:
        ComprehensiveAnalysis results
    """
    print("\nPerforming comprehensive analysis...")
    
    # Combine faces for fractal analysis
    all_faces = faces_plus + faces_minus
    
    # Fractal dimensions
    print("  Computing fractal dimensions...")
    fractal_box = box_counting_dimension(all_faces)
    fractal_corr = correlation_dimension(all_faces)
    
    # Topology
    print("  Analyzing topology...")
    topo_plus = compute_topology(faces_plus)
    topo_minus = compute_topology(faces_minus)
    
    # Phase coherence
    print("  Measuring phase coherence...")
    phase_plus = analyze_phase_coherence(faces_plus)
    phase_minus = analyze_phase_coherence(faces_minus)
    
    # Validation
    print("  Computing validation metrics...")
    validation = compute_validation(hits_plus, hits_minus, len(all_faces))
    
    return ComprehensiveAnalysis(
        fractal_box=fractal_box,
        fractal_corr=fractal_corr,
        topology_plus=topo_plus,
        topology_minus=topo_minus,
        phase_plus=phase_plus,
        phase_minus=phase_minus,
        validation=validation
    )

# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_fractal_dimension(fd: FractalDimension, ax=None, title=None):
    """
    Plot fractal dimension analysis.
    
    Args:
        fd: FractalDimension result
        ax: Matplotlib axis
        title: Plot title
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    
    log_scales = np.log(fd.scales)
    log_counts = np.log(fd.counts)
    
    ax.scatter(log_scales, log_counts, alpha=0.6, s=50, label='Data')
    
    # Fit line
    slope = -fd.dimension if fd.method == "box-counting" else fd.dimension
    intercept = log_counts[0] - slope * log_scales[0]
    fit_line = slope * log_scales + intercept
    
    ax.plot(log_scales, fit_line, 'r--', linewidth=2, 
            label=f'Fit: D={fd.dimension:.3f} (R²={fd.r_squared:.3f})')
    
    ax.set_xlabel('log(scale)')
    ax.set_ylabel('log(count)')
    ax.set_title(title or f'Fractal Dimension ({fd.method})')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    return ax

def plot_valence_distribution(topo: TopologyMetrics, ax=None, title=None):
    """Plot vertex valence distribution."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    
    valences = sorted(topo.valence_dist.keys())
    counts = [topo.valence_dist[v] for v in valences]
    
    colors = ['royalblue' if v == 3 else 'crimson' if v == 5 else 'gray' 
              for v in valences]
    
    ax.bar(valences, counts, color=colors, alpha=0.7, edgecolor='black')
    ax.set_xlabel('Valence')
    ax.set_ylabel('Count')
    ax.set_title(title or 'Vertex Valence Distribution')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='royalblue', edgecolor='black', label='q=3'),
        Patch(facecolor='crimson', edgecolor='black', label='q=5'),
        Patch(facecolor='gray', edgecolor='black', label='other')
    ]
    ax.legend(handles=legend_elements)
    
    return ax

def create_analysis_report(analysis: ComprehensiveAnalysis, filename: str = None):
    """
    Create comprehensive analysis report with visualizations.
    
    Args:
        analysis: ComprehensiveAnalysis results
        filename: Output filename (optional)
    """
    fig = plt.figure(figsize=(16, 12))
    
    # Fractal dimensions
    ax1 = plt.subplot(3, 3, 1)
    plot_fractal_dimension(analysis.fractal_box, ax=ax1, 
                           title='Box-Counting Dimension')
    
    ax2 = plt.subplot(3, 3, 2)
    plot_fractal_dimension(analysis.fractal_corr, ax=ax2,
                           title='Correlation Dimension')
    
    # Valence distributions
    ax3 = plt.subplot(3, 3, 3)
    plot_valence_distribution(analysis.topology_plus, ax=ax3,
                              title='Valence Dist (+)')
    
    ax4 = plt.subplot(3, 3, 4)
    plot_valence_distribution(analysis.topology_minus, ax=ax4,
                              title='Valence Dist (-)')
    
    # Summary text
    ax5 = plt.subplot(3, 3, 5)
    ax5.axis('off')
    summary_text = f"""
FRACTAL ANALYSIS
Box-counting D: {analysis.fractal_box.dimension:.3f} (R²={analysis.fractal_box.r_squared:.3f})
Correlation D: {analysis.fractal_corr.dimension:.3f} (R²={analysis.fractal_corr.r_squared:.3f})

TOPOLOGY (+/-)
Vertices: {analysis.topology_plus.n_vertices} / {analysis.topology_minus.n_vertices}
Faces: {analysis.topology_plus.n_faces} / {analysis.topology_minus.n_faces}
Euler χ: {analysis.topology_plus.euler_characteristic} / {analysis.topology_minus.euler_characteristic}
Genus: {analysis.topology_plus.genus} / {analysis.topology_minus.genus}
Avg valence: {analysis.topology_plus.avg_valence:.2f} / {analysis.topology_minus.avg_valence:.2f}

PHASE COHERENCE (+/-)
Mean |∇θ|: {analysis.phase_plus.mean_gradient:.3f} / {analysis.phase_minus.mean_gradient:.3f}
Mean φ: {analysis.phase_plus.mean_twist:.3f} / {analysis.phase_minus.mean_twist:.3f}

VALIDATION
Closures: q3={analysis.validation.q3_count}, q5={analysis.validation.q5_count}
Density: {analysis.validation.closure_density:.4f}
Score: {analysis.validation.validation_score:.3f}
    """.strip()
    ax5.text(0.1, 0.5, summary_text, transform=ax5.transAxes,
             fontsize=10, verticalalignment='center', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    if filename:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"\nAnalysis report saved to: {filename}")
    
    return fig

# ============================================================================
# EXPORT UTILITIES
# ============================================================================

def export_to_json(analysis: ComprehensiveAnalysis, filename: str):
    """Export analysis results to JSON."""
    data = {
        'fractal_box': {
            'method': analysis.fractal_box.method,
            'dimension': analysis.fractal_box.dimension,
            'r_squared': analysis.fractal_box.r_squared
        },
        'fractal_corr': {
            'method': analysis.fractal_corr.method,
            'dimension': analysis.fractal_corr.dimension,
            'r_squared': analysis.fractal_corr.r_squared
        },
        'topology_plus': asdict(analysis.topology_plus),
        'topology_minus': asdict(analysis.topology_minus),
        'phase_plus': asdict(analysis.phase_plus),
        'phase_minus': asdict(analysis.phase_minus),
        'validation': asdict(analysis.validation)
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Results exported to: {filename}")

def export_faces_to_csv(faces: List[FaceRecord], filename: str):
    """Export face data to CSV for external analysis."""
    import csv
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['face_id', 'centroid_x', 'centroid_y', 'area', 
                         'phi', 'gnorm'])
        
        for i, face in enumerate(faces):
            c = face.tri.centroid()
            writer.writerow([
                i,
                c[0], c[1],
                face.tri.area(),
                face.phi,
                face.gnorm
            ])
    
    print(f"Face data exported to: {filename}")

if __name__ == "__main__":
    print("Analysis module loaded. Import and use with fractal_tetradic_toolkit.")
