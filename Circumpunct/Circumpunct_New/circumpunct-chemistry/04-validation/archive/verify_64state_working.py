#!/usr/bin/env python3
"""
64-State Chemistry: PROPERLY CORRECTED
With the actual missing physics added
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple

# Physical constants
R_INF = 13.6  # Rydberg constant in eV
LAMBDA = 0.1  # Angular penalty coefficient in eV
U_0 = 2.5     # Subshell repulsion parameter (eV) - moderate value
EXCHANGE_BONUS = 0.8  # Bonus for half/full d-shells (eV)

@dataclass
class Orbital:
    """Represents a (d, ℓ, n) orbital state"""
    d: int      # Depth index (from input bits, for sequencing)
    ℓ: int      # Angular momentum (from output bits)
    n: int      # Principal quantum number (for energy)
    name: str
    max_electrons: int
    
    @property
    def d_eff(self):
        """Effective depth with d/f channel shift (for sequencing)"""
        return self.d - max(0, self.ℓ - 1)
    
    @property
    def m(self):
        """Madelung ordering index"""
        return self.d_eff + self.ℓ
    
    def __lt__(self, other):
        """Sort by m, then by d_eff"""
        return (self.m, self.d_eff) < (other.m, other.d_eff)
    
    def __repr__(self):
        return f"{self.name}(n={self.n},ℓ={self.ℓ},d={self.d})"

def generate_orbitals(max_d=7):
    """Generate all valid (d,ℓ) orbitals from 64-state structure"""
    orbitals = []
    ℓ_names = ['s', 'p', 'd', 'f']
    
    for d in range(max_d + 1):
        for ℓ in range(4):  # s, p, d, f
            # Validity rules from 64-state structure
            if ℓ == 0:  # s: always valid
                valid = True
            elif ℓ == 1:  # p: needs d ≥ 1
                valid = d >= 1
            elif ℓ == 2:  # d: needs d ≥ 3 (3d first)
                valid = d >= 3
            elif ℓ == 3:  # f: needs d ≥ 5 (4f first)
                valid = d >= 5
            else:
                valid = False
            
            if valid:
                # Determine n from d and ℓ
                if ℓ <= 1:  # s, p
                    n = d + 1
                elif ℓ == 2:  # d
                    n = d
                elif ℓ == 3:  # f
                    n = d - 1
                
                name = f"{n}{ℓ_names[ℓ]}"
                max_e = 2 * (2 * ℓ + 1)  # 2 for spin, 2ℓ+1 for degeneracy
                
                # NOW STORE n!
                orbitals.append(Orbital(d, ℓ, n, name, max_e))
    
    return sorted(orbitals)

def slater_screening(config: List[Tuple[Orbital, int]], target: Orbital) -> float:
    """
    Proper Slater screening with correct n-grouping
    """
    σ = 0.0
    
    for orb, n_electrons in config:
        if n_electrons == 0:
            continue
        
        # CASE 1: Target is ns or np
        if target.ℓ <= 1:
            if orb.n == target.n and orb.ℓ <= 1:
                # Same n, s/p: 0.35 per electron (excluding self)
                σ += max(0, n_electrons - (1 if orb.name == target.name else 0)) * 0.35
            elif orb.n == target.n - 1:
                # n-1 shell: 0.85
                σ += n_electrons * 0.85
            elif orb.n < target.n - 1:
                # n-2 and lower: 1.00
                σ += n_electrons * 1.00
        
        # CASE 2: Target is nd or nf
        else:
            if orb.n == target.n and orb.ℓ >= 2:
                # Same n, d/f: 0.35 per electron (excluding self)
                σ += max(0, n_electrons - (1 if orb.name == target.name else 0)) * 0.35
            elif orb.n == target.n and orb.ℓ <= 1:
                # Same n, but s/p: 1.00 (d/f see full screening from s/p)
                σ += n_electrons * 1.00
            elif orb.n < target.n:
                # Any lower n: 1.00
                σ += n_electrons * 1.00
    
    return σ

def subshell_repulsion(orb: Orbital, n_electrons: int, Z_eff: float) -> float:
    """
    Electron-electron repulsion within subshell
    
    U(n,ℓ,N) = U_0 * Z_eff / n³ * (N-1)
    
    This is the "don't stuff everything into 3d" term
    """
    if n_electrons <= 1:
        return 0.0
    
    # Repulsion scales with Z_eff (tighter orbitals = stronger repulsion)
    # and inverse n³ (larger orbitals = weaker repulsion)
    U = U_0 * Z_eff / (orb.n ** 3)
    
    # Repulsion increases with each additional electron
    return U * (n_electrons - 1)

def exchange_stabilization(orb: Orbital, n_electrons: int) -> float:
    """
    Exchange stabilization for half-filled and filled d/f subshells
    """
    max_e = orb.max_electrons
    
    # Only for d and f orbitals
    if orb.ℓ < 2:
        return 0.0
    
    # Half-filled or completely filled
    half_filled = (n_electrons == max_e // 2)
    fully_filled = (n_electrons == max_e)
    
    if half_filled or fully_filled:
        return -EXCHANGE_BONUS  # Negative = stabilization
    
    return 0.0

def orbital_energy(orb: Orbital, Z: int, config: List[Tuple[Orbital, int]], 
                   n_electrons_in_orb: int = 0) -> float:
    """
    Complete orbital energy including:
    - Radial (using n, not d!)
    - Angular
    - Screening (proper Slater)
    - Electron-electron repulsion
    - Exchange stabilization
    """
    # Screening
    σ = slater_screening(config, orb)
    Z_eff = max(Z - σ, 0.3)
    
    # RADIAL TERM: Use n, not d!
    E_rad = -R_INF * Z_eff**2 / (orb.n ** 2)
    
    # ANGULAR TERM
    E_ang = LAMBDA * orb.ℓ * (orb.ℓ + 1)
    
    # ELECTRON-ELECTRON REPULSION
    E_rep = subshell_repulsion(orb, n_electrons_in_orb, Z_eff)
    
    # EXCHANGE STABILIZATION
    E_exch = exchange_stabilization(orb, n_electrons_in_orb)
    
    return E_rad + E_ang + E_rep + E_exch

def fill_atom_energy(Z: int, orbitals: List[Orbital], 
                     verbose: bool = False) -> List[Tuple[Orbital, int]]:
    """
    Determine electron configuration using proper many-electron physics
    """
    config = [(orb, 0) for orb in orbitals]
    
    for electron_num in range(1, Z + 1):
        # Find orbital with lowest MARGINAL energy
        best_idx = None
        best_energy = float('inf')
        
        candidates = []
        for idx, (orb, n_e) in enumerate(config):
            if n_e < orb.max_electrons:
                # Energy of adding next electron to this orbital
                E = orbital_energy(orb, Z, config, n_e + 1)
                candidates.append((orb, E))
                
                if E < best_energy:
                    best_energy = E
                    best_idx = idx
        
        if best_idx is None:
            raise ValueError(f"No available orbital for electron {electron_num}")
        
        # Add electron
        orb, n_e = config[best_idx]
        config[best_idx] = (orb, n_e + 1)
        
        # Verbose output for critical electrons
        if verbose:
            if Z == 22 and electron_num >= 19:  # Show all valence for Ti
                print(f"\nElectron {electron_num}:")
                for cand_orb, cand_E in sorted(candidates, key=lambda x: x[1])[:8]:
                    marker = "→" if cand_orb.name == orb.name else " "
                    n_in_cand = next((n for o, n in config if o.name == cand_orb.name), 0)
                    if cand_orb.name == orb.name:
                        n_in_cand += 1  # Show what it WILL be
                    print(f"  {marker} {cand_orb.name:4s}^{n_in_cand}: {cand_E:8.2f} eV")
            elif electron_num in [19, 20, 21, 22, 23, 24, 29]:
                print(f"\nElectron {electron_num}:")
                for cand_orb, cand_E in sorted(candidates, key=lambda x: x[1])[:8]:
                    marker = "→" if cand_orb.name == orb.name else " "
                    n_in_cand = next((n for o, n in config if o.name == cand_orb.name), 0)
                    print(f"  {marker} {cand_orb.name:4s}^{n_in_cand}: {cand_E:8.2f} eV")
    
    return [(orb, n_e) for orb, n_e in config if n_e > 0]

def format_config(config: List[Tuple[Orbital, int]], 
                  use_core: bool = False, Z: int = 0) -> str:
    """Format electron configuration in standard order (by n, then l)"""
    if not config:
        return "empty"
    
    # Sort by (n, ℓ) for standard notation
    sorted_config = sorted([(orb, n_e) for orb, n_e in config if n_e > 0],
                          key=lambda x: (x[0].n, x[0].ℓ))
    
    if use_core and Z > 2:
        cores = [(2, "He"), (10, "Ne"), (18, "Ar"), (36, "Kr"), 
                 (54, "Xe"), (86, "Rn")]
        core_name = ""
        core_electrons = 0
        
        for core_z, name in reversed(cores):
            if Z > core_z:
                core_name = f"[{name}]"
                core_electrons = core_z
                break
        
        parts = []
        electron_count = 0
        for orb, n_e in sorted_config:
            electron_count += n_e
            if electron_count > core_electrons:
                if electron_count - n_e >= core_electrons:
                    parts.append(f"{orb.name}{n_e if n_e > 1 else ''}")
                else:
                    valence_e = electron_count - core_electrons
                    parts.append(f"{orb.name}{valence_e if valence_e > 1 else ''}")
        
        return f"{core_name} {' '.join(parts)}" if core_name else ' '.join(parts)
    else:
        parts = []
        for orb, n_e in sorted_config:
            parts.append(f"{orb.name}{n_e if n_e > 1 else ''}")
        return " ".join(parts)

def test_transition_metals():
    """Test first-row transition metals"""
    print("=" * 80)
    print("TRANSITION METAL TEST (K through Zn)")
    print("=" * 80)
    
    orbitals = generate_orbitals()
    
    known = {
        19: "[Ar] 4s1",     # K
        20: "[Ar] 4s2",     # Ca
        21: "[Ar] 3d1 4s2", # Sc
        22: "[Ar] 3d2 4s2", # Ti
        23: "[Ar] 3d3 4s2", # V
        24: "[Ar] 3d5 4s1", # Cr (exception!)
        25: "[Ar] 3d5 4s2", # Mn
        26: "[Ar] 3d6 4s2", # Fe
        27: "[Ar] 3d7 4s2", # Co
        28: "[Ar] 3d8 4s2", # Ni
        29: "[Ar] 3d10 4s1",# Cu (exception!)
        30: "[Ar] 3d10 4s2",# Zn
    }
    
    elements = {
        19: "K", 20: "Ca", 21: "Sc", 22: "Ti", 23: "V", 24: "Cr",
        25: "Mn", 26: "Fe", 27: "Co", 28: "Ni", 29: "Cu", 30: "Zn"
    }
    
    print(f"\n{'Z':<4} {'El':<4} {'Predicted':<25} {'Expected':<25} {'Match'}")
    print("-" * 80)
    
    correct = 0
    total = 0
    
    for Z in range(19, 31):
        verbose = (Z in [21, 22, 24, 29])  # Debug key atoms including Ti
        config = fill_atom_energy(Z, orbitals, verbose=verbose)
        result = format_config(config, use_core=True, Z=Z)
        expected = known[Z]
        
        # Normalize for comparison
        result_norm = result.replace(" ", "").replace("[", "").replace("]", "")
        expected_norm = expected.replace(" ", "").replace("[", "").replace("]", "")
        
        match = result_norm == expected_norm
        status = "✓" if match else "✗"
        
        if match:
            correct += 1
        total += 1
        
        print(f"{Z:<4} {elements[Z]:<4} {result:<25} {expected:<25} {status}")
    
    print("-" * 80)
    print(f"Success rate: {correct}/{total} = {100*correct/total:.0f}%")
    return correct, total

def test_main_group():
    """Test main group elements"""
    print("\n" + "=" * 80)
    print("MAIN GROUP ELEMENTS (H through Ar)")
    print("=" * 80)
    
    orbitals = generate_orbitals()
    
    known = {
        1: "1s1", 2: "1s2", 3: "[He] 2s1", 4: "[He] 2s2",
        5: "[He] 2s2 2p1", 6: "[He] 2s2 2p2", 7: "[He] 2s2 2p3",
        8: "[He] 2s2 2p4", 9: "[He] 2s2 2p5", 10: "[He] 2s2 2p6",
        11: "[Ne] 3s1", 12: "[Ne] 3s2", 13: "[Ne] 3s2 3p1",
        14: "[Ne] 3s2 3p2", 15: "[Ne] 3s2 3p3", 16: "[Ne] 3s2 3p4",
        17: "[Ne] 3s2 3p5", 18: "[Ne] 3s2 3p6",
    }
    
    correct = 0
    total = 0
    
    for Z in range(1, 19):
        config = fill_atom_energy(Z, orbitals)
        result = format_config(config, use_core=True, Z=Z)
        expected = known.get(Z, "")
        
        if expected:
            result_norm = result.replace(" ", "").replace("[", "").replace("]", "")
            expected_norm = expected.replace(" ", "").replace("[", "").replace("]", "")
            
            match = result_norm == expected_norm
            if match:
                correct += 1
            total += 1
    
    print(f"\nSuccess rate: {correct}/{total} = {100*correct/total:.0f}%")
    return correct, total

def main():
    """Run tests"""
    print("\n" + "=" * 80)
    print("64-STATE CHEMISTRY: PROPERLY CORRECTED")
    print("With n in radial term + proper screening + electron-electron physics")
    print("=" * 80)
    
    mg_correct, mg_total = test_main_group()
    tm_correct, tm_total = test_transition_metals()
    
    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    
    total_correct = mg_correct + tm_correct
    total_tested = mg_total + tm_total
    
    print(f"""
Main group (Z=1-18):       {mg_correct}/{mg_total} = {100*mg_correct/mg_total:.0f}%
Transition metals (K-Zn):  {tm_correct}/{tm_total} = {100*tm_correct/tm_total:.0f}%
Overall:                   {total_correct}/{total_tested} = {100*total_correct/total_tested:.0f}%

PARAMETERS:
- R_∞ = 13.6 eV (exact)
- λ = {LAMBDA} eV (angular penalty)
- U_0 = {U_0} eV (repulsion)
- Exchange = {EXCHANGE_BONUS} eV (d⁵, d¹⁰ bonus)

KEY FIXES APPLIED:
✓ Use n (not d) in radial energy → 3d and 4p have different E_rad
✓ Proper Slater screening by (n, type)
✓ Subshell repulsion U_0·Z_eff/n³·(N-1)
✓ Exchange bonus for half/full d-shells
    """)

if __name__ == "__main__":
    main()
