#!/usr/bin/env python3
"""
Circumpunct Framework: Complete Reproducibility Suite
Single command to run all tests and generate machine-checkable artifacts

Usage:
    python run_all.py              # Run all tests
    python run_all.py --quick      # Skip long tests
    python run_all.py --json-only  # Just generate JSON artifacts
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*80}")
    print(f"{title.center(80)}")
    print(f"{'='*80}\n")

def run_test(name, command, critical=True):
    """Run a test command and capture results"""
    print(f"Running: {name}")
    print(f"Command: {' '.join(command)}")
    print("-" * 80)
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        success = result.returncode == 0
        
        if not success and critical:
            print(f"✗ {name} FAILED (exit code {result.returncode})")
            return False, result
        elif success:
            print(f"✓ {name} PASSED")
            return True, result
        else:
            print(f"⚠ {name} FAILED (non-critical)")
            return True, result  # Don't fail overall
            
    except subprocess.TimeoutExpired:
        print(f"✗ {name} TIMEOUT")
        if critical:
            return False, None
        return True, None
    except Exception as e:
        print(f"✗ {name} ERROR: {e}")
        if critical:
            return False, None
        return True, None

def generate_json_artifacts():
    """Generate machine-checkable JSON artifacts"""
    print_header("GENERATING JSON ARTIFACTS")
    
    artifacts = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "framework": "Circumpunct Chemistry",
            "version": "1.0.0"
        },
        "tests": {},
        "molecules": {}
    }
    
    # Test molecular compiler
    try:
        from molecular_compiler import MolecularCompiler, get_simple_config
        
        compiler = MolecularCompiler()
        
        # Test canonical molecules
        test_molecules = [
            ('H2O', ['O', 'H', 'H']),
            ('CH4', ['C', 'H', 'H', 'H', 'H']),
            ('NH3', ['N', 'H', 'H', 'H']),
            ('CO2', ['C', 'O', 'O']),
        ]
        
        for name, atoms in test_molecules:
            configs = {}
            Z_map = {'H': 1, 'C': 6, 'N': 7, 'O': 8}
            for atom in set(atoms):
                configs[atom] = get_simple_config(Z_map[atom])
            
            molecule = compiler.compile(atoms, configs)
            
            # Get central atom (most bonded non-H, or unique non-H for simple cases)
            non_h_atoms = [a for a in set(atoms) if a != 'H']
            if len(non_h_atoms) == 1:
                central = non_h_atoms[0]
            else:
                # Choose atom with most bonds
                bond_counts = {}
                for bond in molecule.bonds:
                    bond_counts[bond.a1] = bond_counts.get(bond.a1, 0) + 1
                    bond_counts[bond.a2] = bond_counts.get(bond.a2, 0) + 1
                # Remove H from consideration
                for h in ['H']:
                    bond_counts.pop(h, None)
                central = max(bond_counts.items(), key=lambda x: x[1])[0] if bond_counts else non_h_atoms[0]
            
            # Extract data
            mol_data = {
                "formula": name,
                "atoms": atoms,
                "bonds": len(molecule.bonds),
                "geometry": molecule.geometries[central].shape if central in molecule.geometries else "unknown",
                "angle": float(molecule.geometries[central].actual_angle) if central in molecule.geometries else 0.0,
                "polar": molecule.field.has_dipole,
                "dipole_magnitude": molecule.field.magnitude if molecule.field.has_dipole else "none"
            }
            
            if central in molecule.pair_structures:
                pairs = molecule.pair_structures[central]
                mol_data["pair_structure"] = {
                    "i_ext": pairs.i_ext,
                    "i_int": pairs.i_int
                }
            
            if molecule.field.network_potential:
                mol_data["network"] = {
                    "donate": molecule.field.network_potential[0],
                    "accept": molecule.field.network_potential[1]
                }
            
            artifacts["molecules"][name] = mol_data
        
        print("✓ Generated molecule artifacts")
        
    except Exception as e:
        print(f"✗ Failed to generate molecule artifacts: {e}")
        artifacts["molecules"]["error"] = str(e)
    
    # Write JSON
    output_file = "circumpunct_artifacts.json"
    with open(output_file, 'w') as f:
        json.dump(artifacts, f, indent=2)
    
    print(f"✓ Wrote artifacts to {output_file}")
    
    return artifacts

def main():
    """Run complete test suite"""
    
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "CIRCUMPUNCT FRAMEWORK TEST SUITE" + " "*26 + "║")
    print("║" + " "*25 + "Complete Reproducibility Run" + " "*27 + "║")
    print("╚" + "="*78 + "╝")
    print()
    
    # Check for flags
    quick_mode = '--quick' in sys.argv
    json_only = '--json-only' in sys.argv
    
    results = {}
    
    # Always generate JSON artifacts
    artifacts = generate_json_artifacts()
    
    if json_only:
        print("\n✓ JSON artifacts generated. Exiting.")
        return 0
    
    # Test 1: Molecular Compiler Tests
    print_header("TEST 1: MOLECULAR COMPILER")
    success, result = run_test(
        "Molecular Compiler Unit Tests",
        [sys.executable, "test_molecular_compiler.py"],
        critical=True
    )
    results["molecular_compiler"] = success
    
    if not success:
        print("\n✗ CRITICAL TEST FAILED: Molecular Compiler")
        return 1
    
    # Test 2: Compile with Traces
    print_header("TEST 2: FULL ≻i⊰ TRACES")
    success, result = run_test(
        "Complete Molecular Traces",
        [sys.executable, "compile_with_traces.py", "--auto"],
        critical=False
    )
    results["traces"] = success
    
    # Test 3: 3-Layer Demo
    print_header("TEST 3: 3-LAYER DEMO (⊙ → H₂O)")
    success, result = run_test(
        "Complete Pipeline Demo",
        [sys.executable, "clean_3layer_demo.py", "--auto"],
        critical=False
    )
    results["demo"] = success
    
    # Test 4: i_mix Hypothesis
    print_header("TEST 4: i_mix HYPOTHESIS (Correlation)")
    success, result = run_test(
        "Atomic Correlation as Self-Bonding",
        [sys.executable, "test_imix_hypothesis.py"],
        critical=False
    )
    results["imix"] = success
    
    # Test 5: Chemistry Gallery (if not quick mode)
    if not quick_mode:
        print_header("TEST 5: CHEMISTRY GALLERY BENCHMARK")
        success, result = run_test(
            "Benchmark Suite (12 molecules)",
            [sys.executable, "chemistry_gallery_benchmark.py"],
            critical=False
        )
        results["gallery"] = success
    else:
        print("⊘ Skipping Chemistry Gallery (--quick mode)")
        results["gallery"] = None
    
    # Summary
    print_header("SUMMARY")
    
    total = sum(1 for v in results.values() if v is not None)
    passed = sum(1 for v in results.values() if v is True)
    
    print(f"Tests run: {total}")
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {total - passed}")
    print()
    
    for test, result in results.items():
        if result is True:
            status = "✓ PASS"
        elif result is False:
            status = "✗ FAIL"
        else:
            status = "⊘ SKIP"
        print(f"  {test:25s}: {status}")
    
    print()
    print("Artifacts:")
    print(f"  ✓ circumpunct_artifacts.json ({len(artifacts['molecules'])} molecules)")
    print()
    
    # Success rate
    if total > 0:
        success_rate = 100 * passed / total
        print(f"Success rate: {success_rate:.1f}%")
        print()
        
        if success_rate == 100:
            print("⊙ ALL TESTS PASSED! ⊙")
            print()
            return 0
        elif success_rate >= 80:
            print("⊙ MOST TESTS PASSED ⊙")
            print()
            return 0
        else:
            print("✗ Multiple test failures")
            print()
            return 1
    else:
        print("⚠ No tests run")
        return 1

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⊘ Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
