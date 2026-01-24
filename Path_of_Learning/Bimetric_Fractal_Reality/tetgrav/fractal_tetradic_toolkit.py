#!/usr/bin/env python3
"""
fractal_tetradic_toolkit.py
===========================
Production-ready toolkit for holofractal tetradic sheets with:
- Bimetric dual-sheet evolution
- Phase-field coupling and cross-sheet validation
- Closure detection (q=3, q=5 valences)
- Visualization and analysis utilities

Based on: Foundational Geometry to Tetradic Gravitation framework
Repository: https://github.com/AshmanRoonz/Fractal_Reality
"""

from __future__ import annotations
import math
import numpy as np
from dataclasses import dataclass, field
from typing import Callable, List, Tuple, Optional
import matplotlib.pyplot as plt
from collections import defaultdict

# ============================================================================
# CONSTANTS
# ============================================================================

PHI = (1.0 + 5.0 ** 0.5) / 2.0  # Golden ratio
GOLDEN_ANGLE = 2.0 * math.pi / (PHI ** 2)  # ~137.5°

# ============================================================================
# UTILITIES
# ============================================================================

def rot2(theta: float) -> np.ndarray:
    """2D rotation matrix."""
    c, s = math.cos(theta), math.sin(theta)
    return np.array([[c, -s], [s, c]], dtype=float)

def triangle_area(p: np.ndarray) -> float:
    """Compute triangle area from vertices p (3,2)."""
    return 0.5 * abs(
        p[0,0]*(p[1,1]-p[2,1]) + p[1,0]*(p[2,1]-p[0,1]) + p[2,0]*(p[0,1]-p[1,1])
    )

def signed_triangle_area(p: np.ndarray) -> float:
    """Signed triangle area for orientation detection."""
    return 0.5 * (
        p[0,0]*(p[1,1]-p[2,1]) + p[1,0]*(p[2,1]-p[0,1]) + p[2,0]*(p[0,1]-p[1,1])
    )

def barycentric_grad(pts: np.ndarray, vals: np.ndarray) -> np.ndarray:
    """
    Approximate constant ∇θ on triangle by planar fit.
    Find a,b,c s.t. a*x + b*y + c ≈ θ, then return [a,b].
    
    Args:
        pts: (3,2) array of triangle vertices
        vals: (3,) array of phase values at vertices
    Returns:
        (2,) gradient vector [∂θ/∂x, ∂θ/∂y]
    """
    A = np.c_[pts, np.ones(3)]
    sol, *_ = np.linalg.lstsq(A, vals, rcond=None)
    return sol[:2]

def normalize(v: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """Normalize vector with numerical stability."""
    n = np.linalg.norm(v)
    return v / (n + eps)

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Triangle:
    """Triangle with 3 vertices in 2D."""
    V: np.ndarray  # shape (3,2): [[x1,y1], [x2,y2], [x3,y3]]
    
    def centroid(self) -> np.ndarray:
        """Compute centroid."""
        return self.V.mean(axis=0)
    
    def area(self) -> float:
        """Compute unsigned area."""
        return triangle_area(self.V)
    
    def signed_area(self) -> float:
        """Compute signed area (orientation)."""
        return signed_triangle_area(self.V)

@dataclass
class Tetratriangle:
    """
    Tetrahedron-like structure with:
    - base: lens patch triangle (soldered interface)
    - laterals: 3 lateral triangular faces
    """
    base: Triangle
    laterals: List[Triangle]  # length 3

@dataclass
class SheetParams:
    """Parameters governing sheet evolution."""
    chi: int                     # ±1 chirality (left/right)
    phi_step: float              # base rotation per step (rad)
    scale_deflate: float         # deflation factor (typically 1/PHI)
    kappa_pitch: float           # φ-axis coupling (rad per unit s)
    ds_per_step: float           # axial increment per generation
    eta_twist: float             # twist from cross-Σ phase difference
    beta_aniso: float            # anisotropic stretch from |∇θ|
    gamma_cross: float = 0.0     # cross-sheet gradient mismatch coupling

@dataclass
class FractalConfig:
    """Configuration for fractal iteration."""
    max_depth: int = 4
    tri_prune_min_area: float = 1e-6
    closure_tolerance: float = 1e-3
    use_golden_angle: bool = False

# ============================================================================
# PHASE FIELDS
# ============================================================================

PhaseField = Callable[[float, float, float], float]

def default_phase(x: float, y: float, s: float) -> float:
    """
    Default phase field with vortex structure.
    
    Args:
        x, y: spatial coordinates
        s: φ-axis coordinate
    Returns:
        Phase value θ(x,y,s)
    """
    r = math.hypot(x, y) + 1e-9
    ang = math.atan2(y, x)
    return ang + 0.2 * math.sin(3.0 * ang) + 0.05 * math.log(r) + 0.1 * s

def vortex_phase(x: float, y: float, s: float, n: int = 2) -> float:
    """n-fold vortex phase field."""
    ang = math.atan2(y, x)
    r = math.hypot(x, y) + 1e-9
    return n * ang + 0.1 * s * math.sin(ang)

def spiral_phase(x: float, y: float, s: float, k: float = 0.5) -> float:
    """Logarithmic spiral phase field."""
    r = math.hypot(x, y) + 1e-9
    ang = math.atan2(y, x)
    return ang + k * math.log(r) + 0.15 * s

# ============================================================================
# CORE EVOLUTION
# ============================================================================

def face_update(
    tri: Triangle,
    s: float,
    params: SheetParams,
    theta_fn: PhaseField,
    theta_fn_other: Optional[PhaseField] = None
) -> Triangle:
    """
    Apply one inflation-rotation-anisotropy step to a lateral triangle.
    
    Process:
    1. Sample phase field at vertices → compute ∇θ
    2. Compute twist angle from: base rotation + pitch + cross-sheet coupling
    3. Apply transformation around centroid: deflate → rotate → anisotropic stretch
    
    Args:
        tri: Input triangle
        s: Current φ-axis position
        params: Sheet evolution parameters
        theta_fn: Phase field for this sheet
        theta_fn_other: Phase field for twin sheet (for cross-coupling)
    
    Returns:
        Transformed triangle
    """
    V = tri.V.copy()
    c = tri.centroid()
    
    # Sample phase on vertices (active sheet)
    th = np.array([theta_fn(V[i,0], V[i,1], s) for i in range(3)], dtype=float)
    g = barycentric_grad(V, th)  # ∇θ
    g_hat = normalize(g)
    
    # Cross-Σ mean phase difference (validation coupling)
    dtheta_bar = 0.0
    if theta_fn_other is not None:
        th_other = np.array([theta_fn_other(V[i,0], V[i,1], s) for i in range(3)], dtype=float)
        dtheta_bar = float(th.mean() - th_other.mean())
    
    # Compute total twist angle
    phi_geom = params.phi_step
    if params.kappa_pitch != 0.0:
        phi_geom += params.kappa_pitch * params.ds_per_step
    phi_geom += params.eta_twist * dtheta_bar
    phi_geom *= params.chi  # Chirality sign
    
    R = rot2(phi_geom)
    
    # Anisotropic stretch tensor: S = I + σ∥ t⊗t + σ⊥ n⊗n
    # Use traceless stretch (pure shear) for stability
    t_hat = g_hat  # Stretch direction parallel to ∇θ
    n_hat = np.array([-t_hat[1], t_hat[0]], dtype=float)  # Perpendicular
    
    sigma_mag = params.beta_aniso * np.linalg.norm(g)
    sigma_par = 0.5 * sigma_mag
    sigma_perp = -0.5 * sigma_mag
    
    S = np.eye(2) + sigma_par * np.outer(t_hat, t_hat) + sigma_perp * np.outer(n_hat, n_hat)
    
    # Optional: Cross-sheet gradient mismatch
    if theta_fn_other is not None and params.gamma_cross != 0.0:
        g_other = barycentric_grad(V, np.array([theta_fn_other(V[i,0], V[i,1], s) for i in range(3)]))
        mismatch = np.linalg.norm(g - g_other)
        S += params.gamma_cross * mismatch * (np.outer(t_hat, t_hat) - np.outer(n_hat, n_hat))
    
    # Apply composite transformation around centroid
    X = (V - c) * params.scale_deflate  # Deflate
    X = (R @ X.T).T                      # Rotate
    X = (S @ X.T).T                      # Stretch
    V_new = X + c
    
    return Triangle(V=V_new)

def spawn_children(
    tet: Tetratriangle,
    s: float,
    params: SheetParams,
    theta_fn: PhaseField,
    theta_fn_other: Optional[PhaseField],
    cfg: FractalConfig
) -> List[Tetratriangle]:
    """
    Generate child tetratriangles from parent's lateral faces.
    
    For each lateral face:
    1. Apply face_update to get child base
    2. Construct 3 new lateral faces via geometric hinging
    
    Args:
        tet: Parent tetratriangle
        s: Current φ-axis position
        params: Evolution parameters
        theta_fn: Phase field
        theta_fn_other: Twin sheet phase field
        cfg: Fractal configuration
    
    Returns:
        List of child tetratriangles
    """
    children: List[Tetratriangle] = []
    
    for lat in tet.laterals:
        # Prune tiny faces
        if lat.area() < cfg.tri_prune_min_area:
            continue
        
        # Evolve lateral face to become child base
        base_child = face_update(lat, s, params, theta_fn, theta_fn_other)
        B = base_child.V
        
        # Generate 3 lateral faces via simple hinging
        laterals = []
        for i in range(3):
            j = (i + 1) % 3
            # Edge midpoint and outward normal
            mid = 0.5 * (B[i] + B[j])
            e = B[j] - B[i]
            n_out = normalize(np.array([-e[1], e[0]]))
            
            # Apex displacement proportional to edge length
            h = 0.25 * np.linalg.norm(e)
            apex = mid + h * n_out
            
            tri_side = Triangle(V=np.vstack([B[i], B[j], apex]))
            laterals.append(tri_side)
        
        child = Tetratriangle(base=base_child, laterals=laterals)
        children.append(child)
    
    return children

def iterate_sheet(
    seed: Tetratriangle,
    s0: float,
    params: SheetParams,
    theta_fn: PhaseField,
    theta_fn_other: Optional[PhaseField],
    cfg: FractalConfig
) -> List[Tetratriangle]:
    """
    Evolve a single sheet through fractal iteration.
    
    Args:
        seed: Initial tetratriangle
        s0: Starting φ-axis position
        params: Evolution parameters
        theta_fn: Phase field for this sheet
        theta_fn_other: Twin sheet phase field
        cfg: Fractal configuration
    
    Returns:
        Final population of tetratriangles
    """
    pop: List[Tetratriangle] = [seed]
    s = s0
    
    for depth in range(cfg.max_depth):
        next_pop: List[Tetratriangle] = []
        for tet in pop:
            kids = spawn_children(tet, s, params, theta_fn, theta_fn_other, cfg)
            next_pop.extend(kids)
        pop = next_pop
        s += params.ds_per_step
    
    return pop

# ============================================================================
# TWO-SHEET BIMETRIC EVOLUTION
# ============================================================================

def run_two_sheets(
    seed_base: Triangle,
    s0: float,
    params_plus: SheetParams,
    params_minus: SheetParams,
    theta_plus: PhaseField,
    theta_minus: PhaseField,
    cfg: FractalConfig
) -> Tuple[List[Tetratriangle], List[Tetratriangle]]:
    """
    Evolve twin sheets with soldered base (bimetric structure).
    
    The sheets share the same base triangle but evolve with opposite
    chiralities and coupled phase fields.
    
    Args:
        seed_base: Shared base triangle (lens interface)
        s0: Starting φ-axis position
        params_plus: Parameters for + chirality sheet
        params_minus: Parameters for - chirality sheet
        theta_plus: Phase field for + sheet
        theta_minus: Phase field for - sheet
        cfg: Fractal configuration
    
    Returns:
        (sheet_plus, sheet_minus) tuple of tetratriangle populations
    """
    def seed_tetratriangle(B: Triangle) -> Tetratriangle:
        """Create initial tetratriangle from base triangle."""
        Bv = B.V
        laterals = []
        for i in range(3):
            j = (i + 1) % 3
            mid = 0.5 * (Bv[i] + Bv[j])
            e = Bv[j] - Bv[i]
            n_out = normalize(np.array([-e[1], e[0]]))
            apex = mid + 0.5 * np.linalg.norm(e) * n_out
            laterals.append(Triangle(V=np.vstack([Bv[i], Bv[j], apex])))
        return Tetratriangle(base=B, laterals=laterals)
    
    # Create soldered seeds (same base)
    seed_plus = seed_tetratriangle(seed_base)
    seed_minus = seed_tetratriangle(seed_base)
    
    # Evolve both sheets with cross-coupling
    sheet_plus = iterate_sheet(
        seed_plus, s0, params_plus, theta_plus, theta_minus, cfg
    )
    sheet_minus = iterate_sheet(
        seed_minus, s0, params_minus, theta_minus, theta_plus, cfg
    )
    
    return sheet_plus, sheet_minus

# ============================================================================
# VISUALIZATION
# ============================================================================

@dataclass
class FaceRecord:
    """Record of a triangular face with computed properties."""
    tri: Triangle
    phi: float      # Applied twist angle
    gnorm: float    # |∇θ| magnitude

def collect_faces(
    pop: List[Tetratriangle],
    s: float,
    params: SheetParams,
    theta_fn: PhaseField,
    theta_fn_other: Optional[PhaseField]
) -> List[FaceRecord]:
    """
    Extract all lateral faces from population and compute properties.
    
    Args:
        pop: Population of tetratriangles
        s: Current φ-axis position
        params: Sheet parameters
        theta_fn: Phase field
        theta_fn_other: Twin sheet phase field
    
    Returns:
        List of face records with computed properties
    """
    faces: List[FaceRecord] = []
    
    for tet in pop:
        for lat in tet.laterals:
            V = lat.V
            
            # Compute gradient
            th = np.array([theta_fn(V[i,0], V[i,1], s) for i in range(3)], dtype=float)
            g = barycentric_grad(V, th)
            gnorm = float(np.linalg.norm(g))
            
            # Compute cross-sheet coupling
            dtheta_bar = 0.0
            if theta_fn_other is not None:
                th_other = np.array([theta_fn_other(V[i,0], V[i,1], s) for i in range(3)], dtype=float)
                dtheta_bar = float(th.mean() - th_other.mean())
            
            # Reconstruct twist angle
            phi_geom = params.phi_step
            if params.kappa_pitch != 0.0:
                phi_geom += params.kappa_pitch * params.ds_per_step
            phi_geom += params.eta_twist * dtheta_bar
            phi_geom *= params.chi
            
            faces.append(FaceRecord(tri=lat, phi=float(phi_geom), gnorm=gnorm))
    
    return faces

def plot_sheet(
    faces: List[FaceRecord],
    ax=None,
    cmap="viridis",
    color_by="gnorm",
    alpha=0.65,
    lw=0.8,
    label=None
):
    """
    Plot triangular mesh colored by face properties.
    
    Args:
        faces: List of face records
        ax: Matplotlib axis (creates new if None)
        cmap: Colormap name
        color_by: Property to color by ("gnorm" or "phi")
        alpha: Face transparency
        lw: Line width
        label: Plot label
    
    Returns:
        Matplotlib axis
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(7,7))
    
    vals = np.array([getattr(f, color_by) for f in faces], float)
    vmin, vmax = float(vals.min()), float(vals.max())
    
    # Use updated matplotlib API
    try:
        cm = plt.colormaps.get_cmap(cmap)
    except AttributeError:
        cm = plt.cm.get_cmap(cmap)  # Fallback for older matplotlib
    
    for f in faces:
        V = f.tri.V
        val = getattr(f, color_by)
        norm_val = (val - vmin) / (vmax - vmin + 1e-12)
        
        poly = plt.Polygon(
            V, closed=True, fill=True,
            facecolor=cm(norm_val),
            edgecolor="k", linewidth=lw, alpha=alpha
        )
        ax.add_patch(poly)
    
    ax.set_aspect("equal", adjustable="box")
    ax.set_title(f"Sheet ({label}) colored by {color_by}")
    ax.autoscale(enable=True, axis='both', tight=True)
    
    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap=cm, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    plt.colorbar(sm, ax=ax, label=color_by)
    
    return ax

# ============================================================================
# CLOSURE DETECTION
# ============================================================================

@dataclass
class VertexIndex:
    """Clustered vertex with incident faces."""
    coord: np.ndarray
    faces: List[int] = field(default_factory=list)

@dataclass
class ClosureHit:
    """Detected closure candidate."""
    v_coord: np.ndarray
    q_valence: int
    sum_phi: float
    residue: float
    incident_faces: List[int]

def cluster_vertices(faces: List[FaceRecord], tol: float = 1e-3) -> List[VertexIndex]:
    """
    Cluster nearby vertices within tolerance.
    
    Args:
        faces: List of face records
        tol: Distance tolerance for clustering
    
    Returns:
        List of clustered vertices
    """
    verts: List[VertexIndex] = []
    
    def find_match(p: np.ndarray) -> int:
        for idx, v in enumerate(verts):
            if np.linalg.norm(v.coord - p) <= tol:
                return idx
        return -1
    
    for fi, f in enumerate(faces):
        V = f.tri.V
        for k in range(3):
            p = V[k]
            j = find_match(p)
            if j < 0:
                verts.append(VertexIndex(coord=p.copy(), faces=[fi]))
            else:
                verts[j].faces.append(fi)
    
    return verts

def sigma_orientation(face: FaceRecord, v_coord: np.ndarray) -> int:
    """
    Compute orientation σ_{vf} = ±1 for vertex-face incidence.
    
    Args:
        face: Face record
        v_coord: Vertex coordinate
    
    Returns:
        +1 for CCW orientation, -1 for CW
    """
    sa = face.tri.signed_area()
    return +1 if sa >= 0.0 else -1

def scan_closures(
    faces: List[FaceRecord],
    tol_vertex: float = 1e-3,
    tol_closure: float = 5e-2
) -> List[ClosureHit]:
    """
    Scan for closure conditions: Σ σ_{vf} φ_f ≈ 0 (mod 2π).
    
    Detects vertices where the oriented twist sum closes, indicating
    topological features (q=3 or q=5 valences correspond to icosahedral geometry).
    
    Args:
        faces: List of face records
        tol_vertex: Vertex clustering tolerance
        tol_closure: Maximum residue for closure detection
    
    Returns:
        List of closure candidates
    """
    verts = cluster_vertices(faces, tol=tol_vertex)
    hits: List[ClosureHit] = []
    two_pi = 2.0 * math.pi
    
    for v in verts:
        qv = len(set(v.faces))  # Valence
        
        # Accumulate oriented twist
        sphi = 0.0
        for fi in set(v.faces):
            sig = sigma_orientation(faces[fi], v.coord)
            sphi += sig * faces[fi].phi
        
        # Reduce mod 2π and check closure
        residue = abs((sphi + math.pi) % two_pi - math.pi)
        
        if residue <= tol_closure and qv in (3, 5):
            hits.append(ClosureHit(
                v_coord=v.coord,
                q_valence=qv,
                sum_phi=sphi,
                residue=residue,
                incident_faces=list(set(v.faces))
            ))
    
    return hits

def annotate_hits(ax, hits: List[ClosureHit]):
    """
    Annotate closure hits on plot.
    
    Args:
        ax: Matplotlib axis
        hits: List of closure hits
    """
    for h in hits:
        color = 'crimson' if h.q_valence == 5 else 'royalblue'
        ax.plot(h.v_coord[0], h.v_coord[1], 'o', ms=8, color=color, 
                markeredgecolor='white', markeredgewidth=1.5, zorder=100)
        ax.text(
            h.v_coord[0], h.v_coord[1],
            f" q={h.q_valence}\nΔ={h.residue:.3f}",
            fontsize=8, ha='left', va='bottom',
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=color, alpha=0.9, linewidth=2),
            zorder=101
        )

def print_closure_roster(hits: List[ClosureHit], tag: str):
    """Print summary of detected closures."""
    print(f"\n[{tag}] Candidate closures (tolerance={hits[0].residue if hits else 0:.2e}):")
    if not hits:
        print("  None detected")
        return
    
    for i, h in enumerate(hits, 1):
        print(f"  {i:02d}) q={h.q_valence}, residue={h.residue:.4f}, "
              f"sum_phi={h.sum_phi:.4f}, faces={len(h.incident_faces)}")

# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

def main():
    """Run demonstration of fractal tetradic sheets."""
    print("="*80)
    print("FRACTAL TETRADIC SHEET TOOLKIT")
    print("Bimetric holofractal evolution with closure detection")
    print("="*80)
    
    # Create equilateral seed triangle
    R0 = 1.0
    base = Triangle(
        V=np.array([
            [ R0, 0.0],
            [-0.5*R0,  (3**0.5/2.0)*R0],
            [-0.5*R0, -(3**0.5/2.0)*R0]
        ], dtype=float)
    )
    
    # Configuration
    cfg = FractalConfig(
        max_depth=3,
        tri_prune_min_area=1e-5,
        closure_tolerance=5e-2,
        use_golden_angle=False
    )
    
    # Sheet parameters (+ chirality)
    params_plus = SheetParams(
        chi=+1,
        phi_step=2.0*math.pi/5.0,      # Pentagonal symmetry
        scale_deflate=1.0/PHI,          # Golden deflation
        kappa_pitch=2.0*math.pi/5.0,    # Pitch-lock condition
        ds_per_step=1.0,
        eta_twist=0.10,                 # Cross-sheet coupling
        beta_aniso=0.35,                # Gradient-driven anisotropy
        gamma_cross=0.10                # Gradient mismatch
    )
    
    # Sheet parameters (- chirality)
    params_minus = SheetParams(
        chi=-1,
        phi_step=2.0*math.pi/5.0,
        scale_deflate=1.0/PHI,
        kappa_pitch=2.0*math.pi/5.0,
        ds_per_step=1.0,
        eta_twist=0.10,
        beta_aniso=0.35,
        gamma_cross=0.10
    )
    
    print(f"\nConfiguration:")
    print(f"  Max depth: {cfg.max_depth}")
    print(f"  Deflation: 1/φ = {params_plus.scale_deflate:.6f}")
    print(f"  Rotation: 2π/5 = {params_plus.phi_step:.6f} rad = {math.degrees(params_plus.phi_step):.2f}°")
    print(f"  Chirality: ±{params_plus.chi}")
    
    # Evolve twin sheets
    print(f"\nEvolving bimetric sheets...")
    sheet_plus, sheet_minus = run_two_sheets(
        seed_base=base,
        s0=0.0,
        params_plus=params_plus,
        params_minus=params_minus,
        theta_plus=default_phase,
        theta_minus=lambda x,y,s: default_phase(x,y,-s),  # Mirror phase
        cfg=cfg
    )
    
    print(f"  Generated: {len(sheet_plus)} (+) + {len(sheet_minus)} (-) tetratriangles")
    
    # Collect faces for visualization
    print(f"\nCollecting face data...")
    faces_plus = collect_faces(
        sheet_plus, s=0.0, params=params_plus,
        theta_fn=default_phase,
        theta_fn_other=lambda x,y,s: default_phase(x,y,-s)
    )
    faces_minus = collect_faces(
        sheet_minus, s=0.0, params=params_minus,
        theta_fn=lambda x,y,s: default_phase(x,y,-s),
        theta_fn_other=default_phase
    )
    
    print(f"  Faces: {len(faces_plus)} (+) + {len(faces_minus)} (-)")
    
    # Detect closures
    print(f"\nScanning for closures...")
    hits_plus = scan_closures(faces_plus, tol_vertex=1e-3, tol_closure=5e-2)
    hits_minus = scan_closures(faces_minus, tol_vertex=1e-3, tol_closure=5e-2)
    
    print_closure_roster(hits_plus, "PLUS (+)")
    print_closure_roster(hits_minus, "MINUS (-)")
    
    # Visualization
    print(f"\nGenerating visualization...")
    fig, axs = plt.subplots(1, 2, figsize=(14, 7))
    
    plot_sheet(faces_plus, ax=axs[0], color_by="gnorm", label="+", cmap="plasma")
    plot_sheet(faces_minus, ax=axs[1], color_by="gnorm", label="-", cmap="viridis")
    
    annotate_hits(axs[0], hits_plus)
    annotate_hits(axs[1], hits_minus)
    
    plt.tight_layout()
    plt.savefig('/mnt/user-data/outputs/fractal_tetradic_sheets.png', dpi=300, bbox_inches='tight')
    print(f"\nVisualization saved to outputs/")
    
    plt.show()
    
    print("\n" + "="*80)
    print("COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
