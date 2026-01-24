#!/usr/bin/env python3
"""
64-State Chemistry: CORRECTED Implementation

This version:
1. Uses d_eff = d - max(0, ℓ-1) to fix d/f orbital ordering
2. Actually uses energy functional to determine filling order
3. Is honest about what's derived vs fitted
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Physical constants
R_INF = 13.6  # Rydberg constant in eV
LAMBDA = 0.5  # Angular penalty coefficient in eV (FITTED, not derived)

@dataclass
class Orbital:
    """Represents a (d, ℓ) orbital state"""
    d: int  # Depth index (from input bits)
    ℓ: int  # Angular momentum (from output bits)
    name: str
    max_electrons: int
    
    @property
    def d_eff(self):
        """Effective depth with d/f channel shift"""
        return self.d - max(0, self.ℓ - 1)
    
    @property
    def m(self):
        """Madelung ordering index (corrected)"""
        return self.d_eff + self.ℓ
    
    def __lt__(self, other):
        """Sort by m, then by d_eff"""
        return (self.m, self.d_eff) < (other.m, other.d_eff)
    
    def __repr__(self):
        return f"{self.name}(d={self.d},ℓ={self.ℓ},m={self.m})"

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
                
                orbitals.append(Orbital(d, ℓ, name, max_e))
    
    return sorted(orbitals)

def slater_screening(config: List[Tuple[Orbital, int]], target: Orbital) -> float:
    """
    Calculate Slater screening for electron in target orbital
    given current configuration
    """
    σ = 0.0
    
    for orb, n_electrons in config:
        if n_electrons == 0:
            continue
            
        # Same orbital: 0.35 per electron (don't count electron itself)
        if orb.d == target.d and orb.ℓ == target.ℓ:
            σ += max(0, n_electrons - 1) * 0.35
        
        # Same n-1 group (roughly same d): 0.85
        elif abs(orb.d - target.d) <= 1 and orb.ℓ < target.ℓ:
            σ += n_electrons * 0.85
        
        # Inner shells (d much lower): 1.00
        elif orb.d < target.d - 1:
            σ += n_electrons * 1.00
        
        # Lower same-ℓ shells: 0.85
        elif orb.d < target.d and orb.ℓ == target.ℓ:
            σ += n_electrons * 0.85
    
    return σ

def orbital_energy(orb: Orbital, Z: int, config: List[Tuple[Orbital, int]]) -> float:
    """
    Calculate energy of adding one electron to orbital
    
    E(d,ℓ;Z) = -R_∞ · Z_eff² / (d+1)² + λ·ℓ(ℓ+1)
    """
    σ = slater_screening(config, orb)
    Z_eff = max(Z - σ, 0.3)  # Prevent negative Z_eff
    
    E_rad = -R_INF * Z_eff**2 / (orb.d + 1)**2
    E_ang = LAMBDA * orb.ℓ * (orb.ℓ + 1)
    
    return E_rad + E_ang

def fill_atom_energy(Z: int, orbitals: List[Orbital], 
                     verbose: bool = False) -> List[Tuple[Orbital, int]]:
    """
    Determine electron configuration for atom Z
    by ACTUALLY USING THE ENERGY FUNCTIONAL
    
    At each step, add electron to lowest-energy available orbital
    """
    config = [(orb, 0) for orb in orbitals]
    
    for electron_num in range(1, Z + 1):
        # Find orbital with lowest marginal energy that's not full
        best_idx = None
        best_energy = float('inf')
        
        for idx, (orb, n_e) in enumerate(config):
            if n_e < orb.max_electrons:
                E = orbital_energy(orb, Z, config)
                if E < best_energy:
                    best_energy = E
                    best_idx = idx
        
        if best_idx is None:
            raise ValueError(f"No available orbital for electron {electron_num}")
        
        # Add electron to best orbital
        orb, n_e = config[best_idx]
        config[best_idx] = (orb, n_e + 1)
        
        if verbose and electron_num <= 10:
            print(f"Electron {electron_num}: {orb.name} (E={best_energy:.2f} eV)")
    
    # Return only occupied orbitals
    return [(orb, n_e) for orb, n_e in config if n_e > 0]

def format_config(config: List[Tuple[Orbital, int]]) -> str:
    """Format electron configuration as string"""
    if not config:
        return "empty"
    
    parts = []
    for orb, n_e in config:
        if n_e > 0:
            parts.append(f"{orb.name}{n_e if n_e > 1 else ''}")
    
    return " ".join(parts)

def noble_gas_core(Z: int, config: List[Tuple[Orbital, int]]) -> Tuple[str, int]:
    """
    Find appropriate noble gas core for configuration
    Returns (core_name, electrons_in_core)
    """
    noble_gases = [
        (2, "He"),
        (10, "Ne"),
        (18, "Ar"),
        (36, "Kr"),
        (54, "Xe"),
        (86, "Rn"),
    ]
    
    for ng_z, ng_name in reversed(noble_gases):
        if Z > ng_z:
            return ng_name, ng_z
    
    return "", 0

def verify_element(Z: int, orbitals: List[Orbital], 
                   known_configs: dict = None) -> Tuple[bool, str]:
    """
    Verify electron configuration for element Z
    Returns (success, config_string)
    """
    config = fill_atom_energy(Z, orbitals)
    result = format_config(config)
    
    # Check against known configuration if provided
    if known_configs and Z in known_configs:
        expected = known_configs[Z]
        # Simple string comparison (could be more sophisticated)
        match = result.replace(" ", "") == expected.replace(" ", "").replace("[", "").replace("]", "")
        return match, result
    
    return True, result  # Assume correct if no expected value

def test_aufbau_order():
    """Test that orbital ordering is correct"""
    print("=" * 80)
    print("AUFBAU ORBITAL SEQUENCE TEST")
    print("=" * 80)
    
    orbitals = generate_orbitals(max_d=7)
    
    print("\nFirst 25 orbitals in corrected order:")
    print(f"{'#':<4} {'Orbital':<8} {'d':<4} {'ℓ':<4} {'d_eff':<6} {'m':<6} {'Expected sequence':<20}")
    print("-" * 80)
    
    expected = [
        "1s", "2s", "2p", "3s", "3p", "4s", "3d", "4p", "5s", "4d",
        "5p", "6s", "4f", "5d", "6p", "7s", "5f", "6d", "7p"
    ]
    
    for i, orb in enumerate(orbitals[:25]):
        exp = expected[i] if i < len(expected) else "?"
        match = "✓" if orb.name == exp else "✗"
        print(f"{i+1:<4} {orb.name:<8} {orb.d:<4} {orb.ℓ:<4} {orb.d_eff:<6} "
              f"{orb.m:<6} {exp:<20} {match}")
    
    print("\nKey tests:")
    print("✓ 4s before 3d?", "4s" in [orbitals[i].name for i in range(6)])
    print("✓ 3d before 4p?", orbitals[6].name == "3d" and orbitals[7].name == "4p")

def test_transition_metals():
    """Test first-row transition metals specifically"""
    print("\n" + "=" * 80)
    print("TRANSITION METAL TEST (Sc through Zn)")
    print("=" * 80)
    
    orbitals = generate_orbitals()
    
    # Known configurations
    known = {
        21: "Ar 3d1 4s2",  # Sc
        22: "Ar 3d2 4s2",  # Ti
        23: "Ar 3d3 4s2",  # V
        24: "Ar 3d5 4s1",  # Cr (exception)
        25: "Ar 3d5 4s2",  # Mn
        26: "Ar 3d6 4s2",  # Fe
        27: "Ar 3d7 4s2",  # Co
        28: "Ar 3d8 4s2",  # Ni
        29: "Ar 3d10 4s1", # Cu (exception)
        30: "Ar 3d10 4s2", # Zn
    }
    
    elements = ["Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn"]
    
    print(f"\n{'Z':<4} {'Element':<8} {'Predicted':<30} {'Expected':<30} {'Status'}")
    print("-" * 90)
    
    for Z, elem in zip(range(21, 31), elements):
        config = fill_atom_energy(Z, orbitals)
        result = format_config(config)
        
        # Extract just the outer shells for comparison
        # (assuming [Ar] core)
        outer = result.split()[-4:]  # Last few orbitals
        outer_str = " ".join(outer)
        
        expected = known[Z]
        # Simple check: does it contain the right d and s counts?
        match = "?" # Can't definitively say without parsing
        
        print(f"{Z:<4} {elem:<8} {result:<30} {expected:<30} {match}")

def test_hydrogen_energies():
    """Test hydrogen energy levels (no screening)"""
    print("\n" + "=" * 80)
    print("HYDROGEN ENERGY LEVELS")
    print("=" * 80)
    
    print("\nWARNING: The ℓ(ℓ+1) term with λ=0.5 eV is NOT physically correct")
    print("for hydrogen. Real fine structure is ~10^-5 eV, not ~1 eV.")
    print("This is a FITTED parameter that makes Aufbau ordering work,")
    print("not a derived prediction of hydrogen spectroscopy.\n")
    
    orbitals = generate_orbitals(max_d=4)
    
    print(f"{'Orbital':<8} {'E (eV)':<12} {'Notes'}")
    print("-" * 50)
    
    for orb in orbitals[:10]:
        E = orbital_energy(orb, Z=1, config=[])
        notes = ""
        if orb.name == "1s":
            notes = "Ground state"
        elif orb.name in ["2s", "2p"]:
            notes = "First excited manifold"
        
        print(f"{orb.name:<8} {E:>11.4f}  {notes}")

def main():
    """Run all tests"""
    
    # Test 1: Orbital ordering
    test_aufbau_order()
    
    # Test 2: Transition metals
    test_transition_metals()
    
    # Test 3: Hydrogen energies
    test_hydrogen_energies()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("""
WHAT WORKS:
✓ d_eff correction fixes orbital ordering
✓ 4s before 3d, 3d before 4p sequence correct
✓ Energy-based filling implemented
✓ Slater screening approximation in place

WHAT'S NOT YET DERIVED:
✗ λ = 0.5 eV is FITTED to match Aufbau, not derived from geometry
✗ Hydrogen fine structure claim is wrong (real ≈ 10^-5 eV, not 1 eV)
✗ Cr/Cu exceptions need explicit exchange energy term (not yet added)
✗ H₂ bond energy needs actual molecular calculation (not hardcoded)

NEXT STEPS:
1. Add exchange term for half-filled/filled subshell stabilization
2. Test against full periodic table with known exceptions
3. Replace spectroscopy claims with actual derivable predictions
4. Implement molecular energy calculation properly
    """)

if __name__ == "__main__":
    main()
