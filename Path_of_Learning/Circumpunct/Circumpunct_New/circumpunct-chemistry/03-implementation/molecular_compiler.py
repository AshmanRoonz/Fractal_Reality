#!/usr/bin/env python3
"""
Molecular Compiler: 64-State → Molecular Structure
Derives bonding, geometry, and fields from circumpunct principles

Architecture:
  Pass 0: Parse (atomic configs → valence signatures)
  Pass 1: Closure (deficits → pair budgets)
  Pass 2: Bonding (i_share aperture matching)
  Pass 3: Allocation (i_ext vs i_int pairs)
  Pass 4: Geometry (domains → 3D structure)
  Pass 5: Field (β asymmetry → Φ properties)
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
from collections import defaultdict
import math

PHI = (1 + 5**0.5) / 2

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Orbital:
    """Orbital specification (n, ℓ)"""
    n: int  # principal quantum number
    ℓ: int  # angular momentum (0=s, 1=p, 2=d, 3=f)
    
    @property
    def name(self) -> str:
        ℓ_names = {0: 's', 1: 'p', 2: 'd', 3: 'f'}
        return f"{self.n}{ℓ_names[self.ℓ]}"
    
    @property
    def max_electrons(self) -> int:
        return 2 * (2 * self.ℓ + 1)

@dataclass
class ValenceSignature:
    """Valence electron signature for an atom"""
    atom: str
    d_v: int           # valence depth
    N_s: int           # s electrons in valence
    N_p: int           # p electrons in valence
    V: int             # total valence electrons
    χ: float           # electronegativity (Pauling scale)
    
    def __repr__(self):
        return f"{self.atom}(d={self.d_v}, {self.N_s}s{self.N_p}p, V={self.V}, χ={self.χ:.2f})"

@dataclass
class Deficit:
    """Closure deficit for an atom"""
    atom: str
    Δ: int             # electrons needed for closure
    P: int             # pair budget (V/2)
    T: int             # target electrons (2 for H, 8 for main group)
    
    def __repr__(self):
        return f"{self.atom}(Δ={self.Δ}, pairs={self.P}, target={self.T})"

@dataclass
class Bond:
    """Chemical bond between atoms"""
    a1: str
    a2: str
    order: int = 1     # 1=single, 2=double, 3=triple
    β: float = 0.5     # asymmetry parameter (0.5=symmetric)
    
    @property
    def is_polar(self) -> bool:
        return abs(self.β - 0.5) > 0.05
    
    def __repr__(self):
        bond_symbol = {1: '−', 2: '=', 3: '≡'}[self.order]
        polar = f" (β={self.β:.3f})" if self.is_polar else ""
        return f"{self.a1}{bond_symbol}{self.a2}{polar}"

@dataclass
class PairStructure:
    """Electron pair structure around an atom"""
    atom: str
    i_ext: int         # external (bonding) pairs
    i_int: int         # internal (lone) pairs
    
    @property
    def total_pairs(self) -> int:
        return self.i_ext + self.i_int
    
    def __repr__(self):
        return f"{self.atom}[(i_ext)^{self.i_ext} ⊕ (i_int)^{self.i_int}]"

@dataclass
class Geometry:
    """3D geometry around an atom"""
    atom: str
    domains: int       # electron domains (bonds + lone pairs)
    shape: str         # molecular shape
    ideal_angle: float # ideal bond angle
    actual_angle: Optional[float] = None  # with lone pair compression
    
    def __repr__(self):
        angle = self.actual_angle if self.actual_angle else self.ideal_angle
        return f"{self.atom}: {self.shape} ({angle:.1f}°, D={self.domains})"

@dataclass
class MolecularField:
    """Field properties of molecule"""
    has_dipole: bool
    magnitude: str     # 'none', 'weak', 'moderate', 'strong'
    network_potential: Optional[Tuple[int, int]] = None  # (donate, accept)
    
    def __repr__(self):
        dipole = f"Φ_dipole ({self.magnitude})" if self.has_dipole else "no dipole"
        network = f", network({self.network_potential[0]},{self.network_potential[1]})" if self.network_potential else ""
        return dipole + network

@dataclass
class Molecule:
    """Complete molecular structure"""
    atoms: List[str]
    bonds: List[Bond]
    pair_structures: Dict[str, PairStructure]
    geometries: Dict[str, Geometry]
    field: MolecularField
    
    def __repr__(self):
        formula = self._generate_formula()
        bond_list = ', '.join(str(b) for b in self.bonds)
        return f"Molecule: {formula}\nBonds: {bond_list}\n{self.field}"
    
    def _generate_formula(self) -> str:
        """Generate molecular formula like H₂O, CH₄"""
        from collections import Counter
        counts = Counter(self.atoms)
        
        # Standard order: C, H, then alphabetical
        priority = {'C': 0, 'H': 1}
        sorted_atoms = sorted(counts.items(), 
                            key=lambda x: (priority.get(x[0], 10), x[0]))
        
        formula = ''
        for atom, count in sorted_atoms:
            formula += atom
            if count > 1:
                # Unicode subscripts
                subscript = str(count).translate(str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉'))
                formula += subscript
        
        return formula

# ============================================================================
# ELECTRONEGATIVITY TABLE (Pauling scale)
# ============================================================================

ELECTRONEGATIVITY = {
    'H':  2.20,
    'C':  2.55,
    'N':  3.04,
    'O':  3.44,
    'F':  3.98,
    'Si': 1.90,
    'P':  2.19,
    'S':  2.58,
    'Cl': 3.16,
    'Br': 2.96,
    'I':  2.66,
}

# ============================================================================
# MOLECULAR COMPILER
# ============================================================================

class MolecularCompiler:
    """Compiles molecules from atomic configurations using circumpunct principles"""
    
    def __init__(self, electronegativity: Dict[str, float] = None):
        """Initialize compiler with electronegativity table"""
        self.χ_table = electronegativity or ELECTRONEGATIVITY
    
    # ========================================================================
    # PASS 0: PARSE - Atomic configs → valence signatures
    # ========================================================================
    
    def parse_valence(self, atom: str, config: List[Tuple[Orbital, int]]) -> ValenceSignature:
        """
        Extract valence signature from atomic configuration.
        
        For main group elements, valence = outermost shell.
        """
        # Find valence shell (highest n with electrons)
        max_n = max(orb.n for orb, occ in config if occ > 0)
        
        # Extract valence electrons
        N_s = 0
        N_p = 0
        
        for orb, occ in config:
            if orb.n == max_n:
                if orb.ℓ == 0:  # s
                    N_s = occ
                elif orb.ℓ == 1:  # p
                    N_p = occ
        
        V = N_s + N_p
        χ = self.χ_table.get(atom, 2.5)  # default electronegativity
        
        return ValenceSignature(atom, max_n, N_s, N_p, V, χ)
    
    # ========================================================================
    # PASS 1: CLOSURE - Deficits → pair budgets
    # ========================================================================
    
    def compute_deficit(self, sig: ValenceSignature) -> Deficit:
        """
        Compute closure deficit for an atom.
        
        H aims for duet (T=2)
        Main group aims for octet (T=8)
        """
        if sig.atom == 'H':
            T = 2  # duet rule
        else:
            T = 8  # octet rule
        
        Δ = T - sig.V
        P = sig.V // 2
        
        return Deficit(sig.atom, Δ, P, T)
    
    # ========================================================================
    # PASS 2: BONDING - i_share aperture matching
    # ========================================================================
    
    def match_bonds(self, atoms: List[str], deficits: Dict[str, Deficit]) -> List[Bond]:
        """
        Create bonds by matching deficits.
        
        Simple algorithm: pair heavy atoms first, then add hydrogens.
        This works for simple molecules; more complex molecules need
        graph matching.
        """
        bonds = []
        atom_list = list(atoms)
        bonded_count = defaultdict(int)
        
        # Separate heavy atoms and hydrogens
        heavy = [a for a in atom_list if a != 'H']
        hydrogens = [a for a in atom_list if a == 'H']
        
        # Strategy depends on molecule type
        if len(heavy) == 1:
            # Single heavy atom: bind all hydrogens/other atoms to it
            center = heavy[0]
            for other in atom_list:
                if other != center:
                    # Determine bond order from deficits
                    order = self._determine_bond_order(
                        center, other, 
                        deficits[center], deficits[other],
                        bonded_count[center]
                    )
                    
                    β = self._compute_beta(center, other)
                    bonds.append(Bond(center, other, order, β))
                    bonded_count[center] += order
                    bonded_count[other] += order
        
        elif len(heavy) == 2:
            # Two heavy atoms: bond them, then add hydrogens
            a1, a2 = heavy[0], heavy[1]
            
            # Determine bond order between heavy atoms
            order = self._determine_bond_order(
                a1, a2,
                deficits[a1], deficits[a2],
                0
            )
            
            β = self._compute_beta(a1, a2)
            bonds.append(Bond(a1, a2, order, β))
            bonded_count[a1] += order
            bonded_count[a2] += order
            
            # Add hydrogens to each heavy atom
            for h in hydrogens:
                # Prefer less saturated atom
                if bonded_count[a1] < bonded_count[a2]:
                    target = a1
                else:
                    target = a2
                
                β = self._compute_beta(target, h)
                bonds.append(Bond(target, h, 1, β))
                bonded_count[target] += 1
                bonded_count[h] += 1
        
        elif len(heavy) == 3 and len(hydrogens) == 0:
            # Three heavy atoms, no H: likely CO₂ (O-C-O)
            # Determine central atom (lowest electronegativity usually)
            χ_values = [(a, self.χ_table.get(a, 2.5)) for a in heavy]
            center = min(χ_values, key=lambda x: x[1])[0]
            others = [a for a in heavy if a != center]
            
            # Bond center to each other atom
            for other in others:
                order = self._determine_bond_order(
                    center, other,
                    deficits[center], deficits[other],
                    bonded_count[center]
                )
                
                β = self._compute_beta(center, other)
                bonds.append(Bond(center, other, order, β))
                bonded_count[center] += order
                bonded_count[other] += order
        
        elif len(heavy) >= 3:
            # Multiple heavy atoms: use ring detection for benzene-like
            if len(heavy) == 6 and len(hydrogens) == 6:
                # Benzene special case
                bonds = self._make_benzene(heavy, hydrogens)
            else:
                # General case: chain them
                bonds = self._make_chain(heavy, hydrogens, deficits)
        
        return bonds
    
    def _determine_bond_order(self, a1: str, a2: str, 
                               def1: Deficit, def2: Deficit,
                               current_bonds: int) -> int:
        """
        Determine bond order based on deficits.
        
        Simple rules:
        - C-O in CO₂: double bond (C needs 4, each O needs 2)
        - C=C in ethene: double bond
        - Default: single bond
        """
        # CO₂ special case: C=O double bonds
        if {a1, a2} == {'C', 'O'}:
            # C needs 4 electrons, will form 2 double bonds
            # Each O needs 2 electrons, will form 1 double bond
            return 2
        
        # C=C double bond in ethene-like
        if a1 == 'C' and a2 == 'C':
            # If both carbons need multiple bonds
            remaining1 = def1.Δ - current_bonds
            remaining2 = def2.Δ
            if remaining1 >= 2 and remaining2 >= 2:
                return 2
        
        return 1
    
    def _compute_beta(self, a1: str, a2: str) -> float:
        """
        Compute bond asymmetry from electronegativity.
        
        β = max(χ) / (χ₁ + χ₂)  [order-invariant, always ≥ 0.5]
        
        β = 0.5:  symmetric (C-C, H-H)
        β > 0.5:  asymmetric/polar (O-H, N-H)
        """
        χ1 = self.χ_table.get(a1, 2.5)
        χ2 = self.χ_table.get(a2, 2.5)
        
        # Use max to make order-invariant
        return max(χ1, χ2) / (χ1 + χ2)
    
    def _make_benzene(self, carbons: List[str], hydrogens: List[str]) -> List[Bond]:
        """Special case: benzene ring with resonance"""
        bonds = []
        
        # Ring bonds (C-C)
        for i in range(6):
            c1 = f"C{i+1}"
            c2 = f"C{(i+1)%6+1}"
            β = self._compute_beta('C', 'C')
            bonds.append(Bond(c1, c2, 1, β))  # Single bonds (resonance delocalization)
        
        # C-H bonds
        for i in range(6):
            c = f"C{i+1}"
            h = f"H{i+1}"
            β = self._compute_beta('C', 'H')
            bonds.append(Bond(c, h, 1, β))
        
        return bonds
    
    def _make_chain(self, heavy: List[str], hydrogens: List[str], 
                    deficits: Dict[str, Deficit]) -> List[Bond]:
        """Make a chain of heavy atoms with hydrogens"""
        bonds = []
        bonded_count = defaultdict(int)
        
        # Chain heavy atoms
        for i in range(len(heavy) - 1):
            a1, a2 = heavy[i], heavy[i+1]
            order = 1  # default single bond
            β = self._compute_beta(a1, a2)
            bonds.append(Bond(a1, a2, order, β))
            bonded_count[a1] += order
            bonded_count[a2] += order
        
        # Add hydrogens
        for h in hydrogens:
            # Find least saturated heavy atom
            target = min(heavy, key=lambda a: bonded_count[a])
            β = self._compute_beta(target, h)
            bonds.append(Bond(target, h, 1, β))
            bonded_count[target] += 1
        
        return bonds
    
    # ========================================================================
    # PASS 3: ALLOCATION - External vs internal apertures
    # ========================================================================
    
    def allocate_pairs(self, atoms: List[str], bonds: List[Bond], 
                       signatures: Dict[str, ValenceSignature]) -> Dict[str, PairStructure]:
        """
        Allocate electron pairs: external (bonds) vs internal (lone pairs).
        
        For each atom:
        - External pairs = total bond ORDER (counts double bonds as 2)
        - Lone pairs = (valence electrons - electrons in bonds) / 2
        
        Note: Each bond uses 1 electron from each atom (not 2!)
              A double bond uses 2 electrons from each atom
        """
        pair_structures = {}
        
        # Count TOTAL bond order per atom (for electron accounting)
        bond_order_total = defaultdict(int)
        for bond in bonds:
            bond_order_total[bond.a1] += bond.order
            bond_order_total[bond.a2] += bond.order
        
        # Unique atoms
        unique_atoms = list(set(atoms))
        
        for atom in unique_atoms:
            sig = signatures[atom]
            
            # External pairs = total bond order
            # (a double bond = 2 pairs, triple = 3 pairs)
            i_ext = bond_order_total[atom]
            
            # Each bond uses electrons from this atom
            # Single bond: 1 electron contributed
            # Double bond: 2 electrons contributed
            # So electrons_contributed = total bond order
            electrons_contributed = i_ext
            remaining_electrons = sig.V - electrons_contributed
            i_int = remaining_electrons // 2
            
            pair_structures[atom] = PairStructure(atom, i_ext, i_int)
        
        return pair_structures
    
    # ========================================================================
    # PASS 4: GEOMETRY - Domains → 3D structure
    # ========================================================================
    
    def emit_geometry(self, bonds: List[Bond], 
                      pair_structures: Dict[str, PairStructure]) -> Dict[str, Geometry]:
        """
        Determine 3D geometry from electron domain count.
        
        Uses VSEPR-like rules with lone pair compression.
        
        KEY: For geometry, count NUMBER of bonds (bonding groups),
             not bond ORDER. A double bond = 1 group, not 2!
        """
        geometries = {}
        
        # Count number of bonds per atom (not bond order!)
        bond_count = defaultdict(int)
        for bond in bonds:
            bond_count[bond.a1] += 1  # Count bonds, not order
            bond_count[bond.a2] += 1
        
        for atom, pairs in pair_structures.items():
            # Skip hydrogens (terminal atoms)
            if atom == 'H':
                geometries[atom] = Geometry(atom, 1, 'terminal', 180.0)
                continue
            
            # Electron domains = NUMBER of bonds + lone pairs
            # (double bond still counts as 1 domain for geometry!)
            bonding_domains = bond_count[atom]
            lone_pair_domains = pairs.i_int
            D = bonding_domains + lone_pair_domains
            
            # Ideal geometry from domains
            if D == 1:
                shape = 'linear'
                ideal = 180.0
                actual = 180.0
            
            elif D == 2:
                shape = 'linear'
                ideal = 180.0
                actual = 180.0
            
            elif D == 3:
                if lone_pair_domains == 0:
                    shape = 'trigonal_planar'
                    ideal = 120.0
                    actual = 120.0
                elif lone_pair_domains == 1:
                    shape = 'bent'
                    ideal = 120.0
                    actual = 117.0  # lone pair compression
                else:
                    shape = 'linear'
                    ideal = 180.0
                    actual = 180.0
            
            elif D == 4:
                if lone_pair_domains == 0:
                    shape = 'tetrahedral'
                    ideal = 109.5
                    actual = 109.5
                elif lone_pair_domains == 1:
                    shape = 'trigonal_pyramidal'
                    ideal = 109.5
                    actual = 107.0  # lone pair compression (NH₃)
                elif lone_pair_domains == 2:
                    shape = 'bent'
                    ideal = 109.5
                    actual = 104.5  # lone pair compression (H₂O)
                else:
                    shape = 'linear'
                    ideal = 180.0
                    actual = 180.0
            
            elif D == 5:
                shape = 'trigonal_bipyramidal'
                ideal = 90.0  # axial-equatorial
                actual = ideal
            
            elif D == 6:
                shape = 'octahedral'
                ideal = 90.0
                actual = 90.0
            
            else:
                shape = 'unknown'
                ideal = 0.0
                actual = 0.0
            
            geometries[atom] = Geometry(atom, D, shape, ideal, actual)
        
        return geometries
    
    # ========================================================================
    # PASS 5: FIELD - β asymmetry → Φ properties
    # ========================================================================
    
    def emit_field(self, atoms: List[str], bonds: List[Bond], geometries: Dict[str, Geometry],
                   pair_structures: Dict[str, PairStructure]) -> MolecularField:
        """
        Determine molecular field from bond polarities and geometry.
        
        Considers vector addition of bond dipoles.
        """
        # Check if any bonds are polar
        polar_bonds = [b for b in bonds if b.is_polar]
        
        if not polar_bonds:
            return MolecularField(False, 'none')
        
        # Determine if dipoles cancel based on symmetry
        # This is simplified; real version needs 3D vectors
        
        # Check for symmetric cancellation (like CO₂, CH₄)
        centers = set()
        for bond in bonds:
            if bond.a1 != 'H':
                centers.add(bond.a1)
            if bond.a2 != 'H':
                centers.add(bond.a2)
        
        # Special case: symmetric linear molecules (e.g., O=C=O)
        # Check for pattern: [A, B, B] with 2 bonds where A is linear
        if len(bonds) == 2 and len(atoms) == 3:
            from collections import Counter
            atom_counts = Counter(atoms)
            
            # Find which atoms appear once vs twice
            singles = [a for a, c in atom_counts.items() if c == 1]
            doubles = [a for a, c in atom_counts.items() if c == 2]
            
            # Pattern: one unique atom (center), one that appears twice (terminals)
            if len(singles) == 1 and len(doubles) == 1:
                center = singles[0]
                
                # Check if center has linear geometry
                if center in geometries and geometries[center].shape == 'linear':
                    # Check if both bonds have same order
                    if bonds[0].order == bonds[1].order:
                        # Symmetric linear molecule - dipoles cancel
                        return MolecularField(False, 'none')
        
        # If single center with symmetric geometry, check for cancellation
        if len(centers) == 1:
            center = list(centers)[0]
            geom = geometries.get(center)
            
            if geom and geom.shape in ['tetrahedral', 'linear'] and pair_structures[center].i_int == 0:
                # Symmetric, dipoles cancel
                return MolecularField(False, 'none')
        
        # Has dipole - estimate magnitude from β values
        avg_asymmetry = sum(abs(b.β - 0.5) for b in polar_bonds) / len(polar_bonds)
        
        if avg_asymmetry < 0.05:
            magnitude = 'weak'
        elif avg_asymmetry < 0.15:
            magnitude = 'moderate'
        else:
            magnitude = 'strong'
        
        # Check for hydrogen bonding potential (H₂O, NH₃)
        network = None
        for atom, pairs in pair_structures.items():
            if atom in ['O', 'N', 'F'] and pairs.i_int > 0:
                # Count H atoms bonded
                h_bonds = sum(1 for b in bonds if (b.a1 == atom and b.a2 == 'H') or
                                                   (b.a2 == atom and b.a1 == 'H'))
                lone_pairs = pairs.i_int
                network = (h_bonds, lone_pairs)  # (donate, accept)
                break
        
        return MolecularField(True, magnitude, network)
    
    # ========================================================================
    # MAIN COMPILE FUNCTION
    # ========================================================================
    
    def compile(self, atoms: List[str], 
                configs: Dict[str, List[Tuple[Orbital, int]]]) -> Molecule:
        """
        Full pipeline: atoms → molecule
        
        Args:
            atoms: List of atom symbols (can have duplicates)
            configs: Atomic electron configurations from periodic table
        
        Returns:
            Molecule with bonds, geometry, field
        """
        # Pass 0: Parse valence
        unique_atoms = list(set(atoms))
        signatures = {}
        for atom in unique_atoms:
            signatures[atom] = self.parse_valence(atom, configs[atom])
        
        # Pass 1: Compute deficits
        deficits = {}
        for atom in unique_atoms:
            deficits[atom] = self.compute_deficit(signatures[atom])
        
        # Pass 2: Match bonds
        bonds = self.match_bonds(atoms, deficits)
        
        # Pass 3: Allocate pairs
        pair_structures = self.allocate_pairs(atoms, bonds, signatures)
        
        # Pass 4: Emit geometry
        geometries = self.emit_geometry(bonds, pair_structures)
        
        # Pass 5: Emit field
        field = self.emit_field(atoms, bonds, geometries, pair_structures)
        
        return Molecule(atoms, bonds, pair_structures, geometries, field)


# ============================================================================
# HELPER: Get config from periodic table model
# ============================================================================

def get_simple_config(Z: int) -> List[Tuple[Orbital, int]]:
    """
    Simple electron configurations for testing.
    For full integration, use validate_with_optimizer_v4.py
    """
    configs = {
        1:  [(Orbital(1, 0), 1)],  # H: 1s¹
        6:  [(Orbital(1, 0), 2), (Orbital(2, 0), 2), (Orbital(2, 1), 2)],  # C: 1s² 2s² 2p²
        7:  [(Orbital(1, 0), 2), (Orbital(2, 0), 2), (Orbital(2, 1), 3)],  # N: 1s² 2s² 2p³
        8:  [(Orbital(1, 0), 2), (Orbital(2, 0), 2), (Orbital(2, 1), 4)],  # O: 1s² 2s² 2p⁴
        9:  [(Orbital(1, 0), 2), (Orbital(2, 0), 2), (Orbital(2, 1), 5)],  # F: 1s² 2s² 2p⁵
    }
    return configs.get(Z, [])


if __name__ == '__main__':
    # Quick test
    compiler = MolecularCompiler()
    
    # Test water
    H_config = get_simple_config(1)
    O_config = get_simple_config(8)
    
    water = compiler.compile(
        atoms=['O', 'H', 'H'],
        configs={'O': O_config, 'H': H_config}
    )
    
    print("="*80)
    print("WATER (H₂O)")
    print("="*80)
    print(water)
    print("\nPair structures:")
    for atom, pairs in water.pair_structures.items():
        print(f"  {pairs}")
    print("\nGeometries:")
    for atom, geom in water.geometries.items():
        print(f"  {geom}")
