#!/usr/bin/env python3
"""
Molecular Compiler with Full ≻i⊰ Traces
Compiles molecules from atomic configs using proper circumpunct notation
"""

import sys
from molecular_compiler import (
    MolecularCompiler, Orbital, get_simple_config, ELECTRONEGATIVITY
)
from dataclasses import dataclass
from typing import List, Tuple, Dict

PHI = (1 + 5**0.5) / 2

@dataclass
class CircumpunctTrace:
    """Complete trace of molecular compilation in ≻i⊰ form"""
    molecule_name: str
    
    # Input (atomic states)
    atoms: List[str]
    configs: Dict[str, List[Tuple[Orbital, int]]]
    
    # Convergence phase (≻)
    valence_sigs: Dict
    deficits: Dict
    closure_match: str
    
    # Aperture phase (i)
    bonds: List
    aperture_operations: str
    
    # Emergence phase (⊰)
    pair_structures: Dict
    geometries: Dict
    field: any
    
    def print_full_trace(self):
        """Print complete ≻i⊰ trace"""
        print(f"\n{'='*80}")
        print(f"{self.molecule_name} - COMPLETE ≻i⊰ TRACE")
        print(f"{'='*80}")
        
        # Input
        print(f"\n{'INPUT: ATOMIC STATES (⊙ = • ⊗ ○ ⊗ Φ)':-^80}")
        for atom in set(self.atoms):
            config_str = self._format_config(self.configs[atom])
            print(f"  {atom}⊙ = • ⊗ [{config_str}] ⊗ Φ_atomic")
        
        # Convergence phase (≻)
        print(f"\n{'CONVERGENCE PHASE (≻)':-^80}")
        print("\nValence signatures:")
        for atom, sig in self.valence_sigs.items():
            print(f"  {sig}")
        
        print("\nClosure analysis:")
        for atom, deficit in self.deficits.items():
            print(f"  {deficit}")
        
        print(f"\nClosure matching:")
        print(f"  {self.closure_match}")
        print(f"  → Stoichiometry follows from deficit alignment! ✓")
        
        # Aperture phase (i)
        print(f"\n{'APERTURE PHASE (i_share)':-^80}")
        print(f"\n{self.aperture_operations}")
        
        print("\nBonds formed:")
        for bond in self.bonds:
            print(f"  {bond}")
        
        # Emergence phase (⊰)
        print(f"\n{'EMERGENCE PHASE (⊰)':-^80}")
        
        print("\nPair structures (○ = i_ext ⊕ i_int):")
        for atom in sorted(set(self.atoms)):
            if atom in self.pair_structures and atom != 'H':
                pairs = self.pair_structures[atom]
                print(f"  {pairs}")
                print(f"    → {pairs.i_ext} bonding pairs + {pairs.i_int} lone pairs")
        
        print("\nGeometry:")
        for atom in sorted(set(self.atoms)):
            if atom in self.geometries and atom != 'H':
                geom = self.geometries[atom]
                print(f"  {geom}")
                print(f"    → {geom.domains} electron domains → {geom.shape}")
        
        print(f"\nField (Φ):")
        print(f"  {self.field}")
        if self.field.has_dipole:
            print(f"    → β ≠ 0.5, asymmetric boundary → Φ_dipole emerges via ⊰")
            if self.field.network_potential:
                print(f"    → Network potential: donate({self.field.network_potential[0]}) + accept({self.field.network_potential[1]})")
        else:
            print(f"    → β ≈ 0.5, symmetric → Φ cancels")
        
        # Complete composition
        print(f"\n{'COMPLETE CIRCUMPUNCT COMPOSITION':-^80}")
        print(f"\n{self._format_complete_composition()}")
        
        # Final structure
        print(f"\n{'EMERGENT STRUCTURE (⊙_molecule)':-^80}")
        central_atom = self._get_central_atom()
        print(f"\n{self.molecule_name}⊙ = • ⊗ ○ ⊗ Φ")
        print(f"\nwhere:")
        print(f"  • (center):   {central_atom} nucleus")
        if central_atom in self.pair_structures:
            pairs = self.pair_structures[central_atom]
            print(f"  ○ (boundary): (i_ext)^{pairs.i_ext} ⊕ (i_int)^{pairs.i_int}")
        if self.field.has_dipole:
            print(f"  Φ (field):    Φ_dipole ({self.field.magnitude})")
        else:
            print(f"  Φ (field):    Φ = 0 (symmetric)")
        
        print()
    
    def _format_config(self, config):
        """Format electron config as string"""
        parts = []
        for orb, occ in config:
            if occ > 0:
                parts.append(f"{orb.name}^{occ}" if occ > 1 else orb.name)
        return ' '.join(parts)
    
    def _get_central_atom(self):
        """
        Deterministic 'molecular center' for traces and Φ summaries.
        
        Rule:
          1) If exactly one non-H element appears once → choose it (CO₂→C, H₂O→O)
          2) Else choose max bond-degree among non-H (tie-break alphabetically)
        """
        from collections import Counter
        
        counts = Counter(self.atoms)
        singles = [e for e, c in counts.items() if c == 1 and e != "H"]
        if len(singles) == 1:
            return singles[0]
        
        # Fallback: degree by element symbol
        deg = {e: 0 for e in counts.keys() if e != "H"}
        for b in self.bonds:
            if b.a1 in deg:
                deg[b.a1] += 1
            if b.a2 in deg:
                deg[b.a2] += 1
        
        if deg:
            max_deg = max(deg.values())
            candidates = sorted([e for e, d in deg.items() if d == max_deg])
            return candidates[0]
        
        return next((e for e in self.atoms if e != "H"), self.atoms[0])
    
    def _format_complete_composition(self):
        """Format the complete [A⊙+B⊙] ≻ i ⊰ [AB⊙] equation"""
        # Input atoms
        atom_counts = {}
        for atom in self.atoms:
            atom_counts[atom] = atom_counts.get(atom, 0) + 1
        
        input_parts = []
        for atom in sorted(atom_counts.keys()):
            count = atom_counts[atom]
            if count == 1:
                input_parts.append(f"{atom}⊙")
            else:
                input_parts.append(f"{count}{atom}⊙")
        input_str = " + ".join(input_parts)
        
        # Aperture operation
        n_bonds = len(self.bonds)
        has_double = any(b.order >= 2 for b in self.bonds)
        
        if has_double:
            aperture_str = f"(i_σ ⊕ i_π)^{sum(b.order for b in self.bonds)//2}"
        else:
            aperture_str = f"(i_share)^{n_bonds}" if n_bonds > 1 else "i_share"
        
        # Output structure
        central = self._get_central_atom()
        if central in self.pair_structures:
            pairs = self.pair_structures[central]
            boundary_str = f"(i_ext)^{pairs.i_ext} ⊕ (i_int)^{pairs.i_int}"
        else:
            boundary_str = "structure"
        
        field_str = "Φ_dipole" if self.field.has_dipole else "Φ=0"
        
        output_str = f"[{central}[{boundary_str}] ⊗ {field_str}]"
        
        # Complete equation
        equation = f"[{input_str}] ≻ {aperture_str} ⊰ {output_str}"
        
        # Add interpretation
        interpretation = "\nReading:\n"
        interpretation += f"  ≻: {input_str} converge (deficits align)\n"
        interpretation += f"  i: {aperture_str} (electron sharing apertures)\n"
        interpretation += f"  ⊰: Structure emerges with geometry + field"
        
        return equation + "\n" + interpretation


def compile_with_trace(molecule_name: str, atoms: List[str],
                       configs: Dict[str, List[Tuple[Orbital, int]]]) -> CircumpunctTrace:
    """
    Compile molecule and return full ≻i⊰ trace
    """
    compiler = MolecularCompiler()
    
    # Parse valence (convergence phase begins)
    valence_sigs = {}
    for atom in set(atoms):
        valence_sigs[atom] = compiler.parse_valence(atom, configs[atom])
    
    # Compute deficits
    deficits = {}
    for atom in set(atoms):
        deficits[atom] = compiler.compute_deficit(valence_sigs[atom])
    
    # Closure matching
    closure_match = _generate_closure_match_description(atoms, deficits)
    
    # Compile full molecule (aperture + emergence phases)
    molecule = compiler.compile(atoms, configs)
    
    # Generate aperture description
    aperture_ops = _generate_aperture_description(molecule.bonds)
    
    # Create trace
    trace = CircumpunctTrace(
        molecule_name=molecule_name,
        atoms=atoms,
        configs=configs,
        valence_sigs=valence_sigs,
        deficits=deficits,
        closure_match=closure_match,
        bonds=molecule.bonds,
        aperture_operations=aperture_ops,
        pair_structures=molecule.pair_structures,
        geometries=molecule.geometries,
        field=molecule.field
    )
    
    return trace


def _generate_closure_match_description(atoms, deficits):
    """Generate human-readable closure matching"""
    # Get non-H atoms
    heavy = [a for a in set(atoms) if a != 'H']
    if heavy:
        central = heavy[0]
        h_count = atoms.count('H')
        
        Δ_central = deficits[central].Δ
        Δ_total_H = h_count * deficits.get('H', deficits.get(atoms[1])).Δ if 'H' in atoms else 0
        
        desc = f"{central}(Δ={Δ_central})"
        if h_count > 0:
            desc += f" + {h_count}H(Δ=1 each = {Δ_total_H} total)"
        
        if Δ_central == Δ_total_H:
            desc += f" → EXACT MATCH ✓"
        else:
            desc += f" → partial match (Δ_central={Δ_central} vs Δ_H={Δ_total_H})"
        
        return desc
    
    return "Closure analysis"


def _generate_aperture_description(bonds):
    """Generate description of aperture operations"""
    n_bonds = len(bonds)
    has_double = any(b.order >= 2 for b in bonds)
    
    if has_double:
        desc = f"Double bonds detected: (i_σ ⊕ i_π) apertures\n"
        desc += f"  Each double bond = σ + π orthogonal apertures"
    else:
        desc = f"{n_bonds} × i_share apertures form\n"
        desc += f"  Each creates one shared electron pair"
    
    return desc


def main():
    """Compile canonical molecules and show full traces"""
    
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "CIRCUMPUNCT MOLECULAR COMPILER" + " "*28 + "║")
    print("║" + " "*20 + "Full ≻i⊰ Trace Generation" + " "*33 + "║")
    print("╚" + "="*78 + "╝")
    
    # Canonical molecules
    molecules = [
        ("H₂O", ['O', 'H', 'H']),
        ("CH₄", ['C', 'H', 'H', 'H', 'H']),
        ("NH₃", ['N', 'H', 'H', 'H']),
        ("CO₂", ['C', 'O', 'O']),
    ]
    
    for name, atoms in molecules:
        # Get configs
        configs = {}
        for atom in set(atoms):
            Z_map = {'H': 1, 'C': 6, 'N': 7, 'O': 8}
            configs[atom] = get_simple_config(Z_map[atom])
        
        # Compile with trace
        trace = compile_with_trace(name, atoms, configs)
        
        # Print full trace
        trace.print_full_trace()
        
        input("\nPress ENTER for next molecule...")
    
    print("\n" + "="*80)
    print("⊙ ALL MOLECULES COMPILED IN PROPER ≻i⊰ NOTATION ⊙")
    print("="*80)
    print("\nKey insights:")
    print("  • Same ≻i⊰ pattern at every scale")
    print("  • Convergence (≻): deficits align")
    print("  • Aperture (i): transformation/sharing")
    print("  • Emergence (⊰): structure + field")
    print("\n  Chemistry IS aperture calculus! ⊙")
    print()


if __name__ == '__main__':
    # Check for auto mode
    if '--auto' in sys.argv:
        import builtins
        builtins.input = lambda *args: None
    
    main()
