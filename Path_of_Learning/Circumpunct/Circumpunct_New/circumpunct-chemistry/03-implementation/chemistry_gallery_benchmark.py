#!/usr/bin/env python3
"""
Chemistry Gallery Benchmark
Tests molecular compiler predictions against textbook expectations
"""

from molecular_compiler import MolecularCompiler, get_simple_config
from collections import namedtuple

# Expected molecular properties
Expected = namedtuple('Expected', [
    'shape', 'angle', 'polar', 'h_bond_donor', 'h_bond_acceptor', 'bond_orders'
])

# Benchmark database: molecule specifications with expected properties
BENCHMARK = {
    # Simple hydrides
    'H2O': {
        'atoms': ['O', 'H', 'H'],
        'expected': Expected(
            shape='bent',
            angle=104.5,
            polar=True,
            h_bond_donor=2,
            h_bond_acceptor=2,
            bond_orders={'O-H': 1}
        )
    },
    'NH3': {
        'atoms': ['N', 'H', 'H', 'H'],
        'expected': Expected(
            shape='trigonal_pyramidal',
            angle=107.0,
            polar=True,
            h_bond_donor=3,
            h_bond_acceptor=1,
            bond_orders={'N-H': 1}
        )
    },
    'CH4': {
        'atoms': ['C', 'H', 'H', 'H', 'H'],
        'expected': Expected(
            shape='tetrahedral',
            angle=109.5,
            polar=False,
            h_bond_donor=0,
            h_bond_acceptor=0,
            bond_orders={'C-H': 1}
        )
    },
    'H2S': {
        'atoms': ['S', 'H', 'H'],
        'expected': Expected(
            shape='bent',
            angle=92.0,  # Smaller than H2O due to weaker lp repulsion
            polar=True,
            h_bond_donor=0,  # Weak H-bonding
            h_bond_acceptor=0,
            bond_orders={'S-H': 1}
        )
    },
    
    # Small molecules with multiple bonds
    'CO2': {
        'atoms': ['C', 'O', 'O'],
        'expected': Expected(
            shape='linear',
            angle=180.0,
            polar=False,  # Symmetric cancellation
            h_bond_donor=0,
            h_bond_acceptor=0,
            bond_orders={'C=O': 2}
        )
    },
    'HCN': {
        'atoms': ['H', 'C', 'N'],
        'expected': Expected(
            shape='linear',
            angle=180.0,
            polar=True,
            h_bond_donor=0,
            h_bond_acceptor=1,
            bond_orders={'H-C': 1, 'C≡N': 3}
        )
    },
    
    # Halogens
    'HF': {
        'atoms': ['H', 'F'],
        'expected': Expected(
            shape='linear',
            angle=180.0,
            polar=True,
            h_bond_donor=1,
            h_bond_acceptor=3,  # F has 3 lone pairs
            bond_orders={'H-F': 1}
        )
    },
    'HCl': {
        'atoms': ['H', 'Cl'],
        'expected': Expected(
            shape='linear',
            angle=180.0,
            polar=True,
            h_bond_donor=0,  # Weak H-bonding
            h_bond_acceptor=0,
            bond_orders={'H-Cl': 1}
        )
    },
    
    # Two-heavy-atom molecules
    'N2': {
        'atoms': ['N', 'N'],
        'expected': Expected(
            shape='linear',
            angle=180.0,
            polar=False,
            h_bond_donor=0,
            h_bond_acceptor=0,
            bond_orders={'N≡N': 3}
        )
    },
    'O2': {
        'atoms': ['O', 'O'],
        'expected': Expected(
            shape='linear',
            angle=180.0,
            polar=False,
            h_bond_donor=0,
            h_bond_acceptor=0,
            bond_orders={'O=O': 2}
        )
    },
    
    # More complex
    'H2O2': {
        'atoms': ['H', 'O', 'O', 'H'],
        'expected': Expected(
            shape='bent',  # At each O
            angle=104.0,   # O-O-H angle
            polar=True,
            h_bond_donor=2,
            h_bond_acceptor=2,
            bond_orders={'H-O': 1, 'O-O': 1}
        )
    },
    'CH3OH': {
        'atoms': ['C', 'H', 'H', 'H', 'O', 'H'],
        'expected': Expected(
            shape='tetrahedral',  # At C
            angle=109.5,
            polar=True,
            h_bond_donor=1,  # OH hydrogen
            h_bond_acceptor=2,  # O lone pairs
            bond_orders={'C-H': 1, 'C-O': 1, 'O-H': 1}
        )
    },
}


def test_molecule(name, spec, compiler):
    """Test a single molecule"""
    print(f"\n{'='*80}")
    print(f"{name}")
    print(f"{'='*80}")
    
    # Get configs
    configs = {}
    for atom in set(spec['atoms']):
        Z_map = {'H': 1, 'C': 6, 'N': 7, 'O': 8, 'F': 9, 'S': 16, 'Cl': 17}
        if atom in Z_map:
            configs[atom] = get_simple_config(Z_map[atom])
        else:
            print(f"  ⚠ Skipping {name}: {atom} not in simple config")
            return None
    
    # Compile
    try:
        molecule = compiler.compile(spec['atoms'], configs)
    except Exception as e:
        print(f"  ✗ Compilation failed: {e}")
        return None
    
    expected = spec['expected']
    results = {}
    
    # Get central atom using deterministic rule
    # Rule: 1) If exactly one non-H appears once → pick it (CO₂→C)
    #       2) Else pick by max bond degree (tie-break alphabetically)
    from collections import Counter
    
    counts = Counter(spec['atoms'])
    singles = [e for e, c in counts.items() if c == 1 and e != "H"]
    
    if len(singles) == 1:
        central = singles[0]
    else:
        # Fallback: pick alphabetically first non-H with geometry
        central_atoms = sorted([a for a in set(spec['atoms']) if a != 'H' and a in molecule.geometries])
        if not central_atoms:
            print(f"  ⚠ No central atom found")
            return None
        central = central_atoms[0]
    
    # Get geometry for central atom
    geom = molecule.geometries.get(central)
    if geom is None:
        # Fallback: pick any geometry deterministically
        if molecule.geometries:
            central = sorted(molecule.geometries.keys())[0]
            geom = molecule.geometries[central]
        else:
            print(f"  ⚠ No geometry found")
            return None
    
    # Test 1: Shape
    shape_match = geom.shape == expected.shape
    shape_status = "✓" if shape_match else "✗"
    print(f"  Shape:     {geom.shape:20s} vs {expected.shape:20s} {shape_status}")
    results['shape'] = shape_match
    
    # Test 2: Angle (within tolerance)
    if expected.angle:
        angle_diff = abs(geom.actual_angle - expected.angle)
        angle_match = angle_diff < 5.0  # 5° tolerance
        angle_status = "✓" if angle_match else "✗"
        print(f"  Angle:     {geom.actual_angle:6.1f}° vs {expected.angle:6.1f}° (Δ={angle_diff:.1f}°) {angle_status}")
        results['angle'] = angle_match
    
    # Test 3: Polarity
    polar_match = molecule.field.has_dipole == expected.polar
    polar_status = "✓" if polar_match else "✗"
    polar_pred = "polar" if molecule.field.has_dipole else "nonpolar"
    polar_exp = "polar" if expected.polar else "nonpolar"
    print(f"  Polarity:  {polar_pred:20s} vs {polar_exp:20s} {polar_status}")
    results['polar'] = polar_match
    
    # Test 4: H-bonding (if applicable)
    if expected.h_bond_donor or expected.h_bond_acceptor:
        if molecule.field.network_potential:
            donor_pred, acceptor_pred = molecule.field.network_potential
            donor_match = donor_pred == expected.h_bond_donor
            acceptor_match = acceptor_pred == expected.h_bond_acceptor
            hbond_status = "✓" if (donor_match and acceptor_match) else "✗"
            print(f"  H-bond:    donate({donor_pred}), accept({acceptor_pred}) vs " +
                  f"donate({expected.h_bond_donor}), accept({expected.h_bond_acceptor}) {hbond_status}")
            results['h_bond'] = donor_match and acceptor_match
        else:
            print(f"  H-bond:    none predicted vs donate({expected.h_bond_donor}), accept({expected.h_bond_acceptor}) ✗")
            results['h_bond'] = False
    
    # Test 5: Bond orders (simplified - just check if double bonds exist)
    if any('=' in key for key in expected.bond_orders.keys()):
        has_double = any(b.order >= 2 for b in molecule.bonds)
        bond_status = "✓" if has_double else "?"
        print(f"  Bonds:     double bonds {'present' if has_double else 'absent'} {bond_status}")
        results['bonds'] = has_double
    
    return results


def run_benchmark():
    """Run full chemistry gallery benchmark"""
    compiler = MolecularCompiler()
    
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*25 + "CHEMISTRY GALLERY BENCHMARK" + " "*26 + "║")
    print("║" + " "*20 + "Molecular Compiler vs Textbook" + " "*27 + "║")
    print("╚" + "="*78 + "╝")
    
    all_results = {}
    for name, spec in BENCHMARK.items():
        results = test_molecule(name, spec, compiler)
        if results:
            all_results[name] = results
    
    # Summary
    print(f"\n{'='*80}")
    print("BENCHMARK SUMMARY")
    print(f"{'='*80}")
    
    total_tests = 0
    total_pass = 0
    
    categories = ['shape', 'angle', 'polar', 'h_bond', 'bonds']
    category_stats = {cat: {'pass': 0, 'total': 0} for cat in categories}
    
    for name, results in all_results.items():
        for cat, result in results.items():
            category_stats[cat]['total'] += 1
            if result:
                category_stats[cat]['pass'] += 1
            total_tests += 1
            if result:
                total_pass += 1
    
    print()
    print("Category Performance:")
    for cat in categories:
        if category_stats[cat]['total'] > 0:
            pct = 100 * category_stats[cat]['pass'] / category_stats[cat]['total']
            print(f"  {cat:15s}: {category_stats[cat]['pass']:2d}/{category_stats[cat]['total']:2d} = {pct:5.1f}%")
    
    print()
    overall_pct = 100 * total_pass / total_tests if total_tests > 0 else 0
    print(f"Overall: {total_pass}/{total_tests} = {overall_pct:.1f}% tests passed")
    print()
    
    print("Molecules tested:")
    print(f"  ✓ Successfully compiled: {len(all_results)}/{len(BENCHMARK)}")
    print()
    
    # Grade the system
    if overall_pct >= 90:
        grade = "A (Excellent)"
    elif overall_pct >= 80:
        grade = "B (Good)"
    elif overall_pct >= 70:
        grade = "C (Acceptable)"
    elif overall_pct >= 60:
        grade = "D (Needs work)"
    else:
        grade = "F (Failed)"
    
    print(f"Benchmark Grade: {grade}")
    print()
    print("⊙ Chemistry Gallery Benchmark Complete ⊙")
    print()


if __name__ == '__main__':
    run_benchmark()
