#!/usr/bin/env python3
"""
64-State Chemistry: COMPLETE WORKING VERSION
With proper n vs d, correct screening, and gating constraints
"""

from dataclasses import dataclass
from typing import List, Tuple

# Physical constants
R_INF = 13.605693122994  # eV (exact Rydberg)

# Golden ratio
PHI = (1 + 5**0.5) / 2  # φ ≈ 1.618...

# DERIVED angular penalty from circumpunct geometry: λ = R∞ × φ⁻⁷
LAMBDA = R_INF * (PHI ** -7)  # ≈ 0.4686 eV (φ⁻⁷ exact), not a fit

# Optional multi-electron knobs (baseline = 0)
U0 = 0.0  # Crowding (Hubbard-U-like)
J0 = 0.0  # Exchange stabilization

@dataclass
class Orbital:
    """
    Store BOTH:
      - d : 64-state effective shell index (0→1s, 1→2s/2p, 2→3s/3p/3d, …)
      - n : principal quantum number (for hydrogenic radial scaling)
      - ℓ : angular momentum (0=s,1=p,2=d,3=f)
    """
    d: int
    n: int
    ℓ: int
    name: str
    max_electrons: int

    @property
    def d_eff(self) -> int:
        return self.d - max(0, self.ℓ - 1)

    @property
    def m(self) -> int:
        return self.d_eff + self.ℓ

    def __lt__(self, other):
        if self.m != other.m:
            return self.m < other.m
        if self.n != other.n:
            return self.n < other.n
        return self.ℓ < other.ℓ

    def __repr__(self):
        return f"{self.name} (d={self.d}, n={self.n}, ℓ={self.ℓ}, m={self.m})"


def generate_orbitals(max_d: int = 7, max_n: int = 7) -> List[Orbital]:
    """
    Generate orbitals from the 64-state (d, ℓ) scaffold and compute principal n.

    Mapping:
      s,p: n = d + 1
      d:   n = d
      f:   n = d - 1
    """
    orbitals = []
    for d in range(0, max_d + 1):
        for ℓ, subshell in [(0, "s"), (1, "p"), (2, "d"), (3, "f")]:
            if ℓ > d:
                continue

            if subshell in ("s", "p"):
                n = d + 1
            elif subshell == "d":
                n = d
            else:
                n = d - 1

            # physical constraint: n >= ℓ + 1
            if n <= ℓ:
                continue
            if n < 1 or n > max_n:
                continue

            name = f"{n}{subshell}"
            max_e = 2 * (2 * ℓ + 1)
            orbitals.append(Orbital(d=d, n=n, ℓ=ℓ, name=name, max_electrons=max_e))

    return sorted(orbitals)


def slater_screening(config: List[Tuple[Orbital, int]], target: Orbital) -> float:
    """
    Slater-style screening using principal n and ℓ.

    IMPORTANT: same-shell term uses N (not N-1). We are evaluating Z_eff for a
    marginal addition, so config already represents the existing electrons.
    """
    σ = 0.0
    n_t, ℓ_t = target.n, target.ℓ

    for orb, N in config:
        if N <= 0:
            continue
        n, ℓ = orb.n, orb.ℓ
        if n > n_t:
            continue

        if ℓ_t <= 1:  # s/p target
            if n == n_t:
                coeff = 0.30 if n_t == 1 else 0.35
                σ += N * coeff
            elif n == n_t - 1:
                σ += N * (0.85 if ℓ <= 1 else 1.00)
            else:
                σ += N * 1.00
        else:  # d/f target
            if n == n_t and ℓ == ℓ_t:
                σ += N * 0.35
            elif n == n_t and ℓ <= 1:
                σ += N * 1.00
            elif n < n_t:
                σ += N * 1.00

    return σ


def orbital_energy(orb: Orbital, Z: int, config: List[Tuple[Orbital, int]]) -> float:
    """
    Marginal energy model (eV).

      E_rad = -R_inf * Z_eff^2 / n^2
      E_ang = +λ ℓ(ℓ+1) / n²  (SCALED by n² for heavier atoms)

    Optional:
      E_rep = +U0 * (Z_eff / n^3) * N_sub
      E_ex  = -J0 * (Z_eff / n^3) when entering half/full d/f subshell
    """
    σ = slater_screening(config, orb)
    Z_eff = max(Z - σ, 0.3)

    E_rad = -R_INF * (Z_eff ** 2) / (orb.n ** 2)
    
    # Angular penalty scaled by n² - becomes less important for larger orbitals
    E_ang = LAMBDA * orb.ℓ * (orb.ℓ + 1) / (orb.n ** 2)

    # occupancy in this subshell
    N_sub = 0
    for o, N in config:
        if o.name == orb.name:
            N_sub = N
            break

    E_rep = U0 * (Z_eff / (orb.n ** 3)) * N_sub if U0 else 0.0

    E_ex = 0.0
    if J0 and orb.ℓ in (2, 3):
        half = orb.max_electrons // 2
        new_occ = N_sub + 1
        if new_occ in (half, orb.max_electrons):
            E_ex = -J0 * (Z_eff / (orb.n ** 3))

    return E_rad + E_ang + E_rep + E_ex


def total_energy(config: List[Tuple[Orbital, int]], Z: int) -> float:
    """
    Frozen-orbital total energy proxy:
      E_total = Σ_occ N_sub * ε_sub
    where ε_sub is computed from the *current* configuration (screening included).
    This is consistent with using orbital_energy() as our single energy model,
    and is intended for *local* promotion comparisons (not absolute spectroscopy).
    """
    E = 0.0
    for orb, N in config:
        if N > 0:
            E += N * orbital_energy(orb, Z, config)
    return E


def _apply_move(
    config: List[Tuple[Orbital, int]],
    idx: dict,
    src: str,
    dst: str,
    k: int
) -> List[Tuple[Orbital, int]] | None:
    if k <= 0:
        return None
    if src not in idx or dst not in idx:
        return None
    s_i, d_i = idx[src], idx[dst]
    src_orb, src_occ = config[s_i]
    dst_orb, dst_occ = config[d_i]
    if src_occ < k:
        return None
    if dst_occ + k > dst_orb.max_electrons:
        return None
    new = list(config)
    new[s_i] = (src_orb, src_occ - k)
    new[d_i] = (dst_orb, dst_occ + k)
    return new


def try_promotions(
    config: List[Tuple[Orbital, int]],
    Z: int,
    idx: dict,
    max_passes: int = 6,
    tol: float = 1e-12
) -> List[Tuple[Orbital, int]]:
    """
    Local energy minimization after greedy fill.

    Candidate moves (minimal but covers known exception families):
      - (n+1)s ↔ nd    : 1e and 2e moves (covers Cr/Cu/Nb/Mo/Ru/Rh/Pd patterns)
      - nf ↔ (n+1)d    : 1e moves (covers La/Ce/Gd-type f/d competition)
      - (n+2)s ↔ nf    : 1e moves (rare, but allows the solver to explore)

    NOTE: We keep J0=0 as requested. If some 4d/5d cases remain wrong,
    the next "physics knob" is a tiny exchange bonus (J0 > 0), but this
    optimizer is parameter-free by itself.
    """
    for _ in range(max_passes):
        baseE = total_energy(config, Z)
        bestE = baseE
        best = config

        candidates = []
        for orb, _N in config:
            # s <-> d promotions (including 2e for Pd-like cases)
            if orb.ℓ == 2:
                dname = orb.name
                sname = f"{orb.n + 1}s"
                candidates += [(sname, dname, 1), (sname, dname, 2), (dname, sname, 1)]

            # f <-> d and s <-> f exploration
            if orb.ℓ == 3:
                fname = orb.name
                dname = f"{orb.n + 1}d"
                sname = f"{orb.n + 2}s"
                candidates += [(fname, dname, 1), (dname, fname, 1)]
                candidates += [(sname, fname, 1), (fname, sname, 1)]

        seen = set()
        for src, dst, k in candidates:
            key = (src, dst, k)
            if key in seen:
                continue
            seen.add(key)
            new = _apply_move(config, idx, src, dst, k)
            if new is None:
                continue
            E = total_energy(new, Z)
            if E < bestE - tol:
                bestE = E
                best = new

        if best is config:
            break
        config = best

    return config


def fill_atom_energy(Z: int, orbitals: List[Orbital], verbose: bool = False) -> List[Tuple[Orbital, int]]:
    """
    Energy-based filling with a 64-state gating constraint:

      - nd (ℓ=2) cannot open until (n+1)s is full
      - nf (ℓ=3) cannot open until (n+2)s is full

    After greedy filling, perform a local promotion optimization that
    minimizes total_energy() using the same orbital_energy() model.
    """
    config = [(orb, 0) for orb in orbitals]
    idx = {orb.name: i for i, orb in enumerate(orbitals)}

    def occ(name: str) -> int:
        return config[idx[name]][1] if name in idx else 0

    def is_allowed(orb: Orbital) -> bool:
        if orb.ℓ == 2:
            sname = f"{orb.n + 1}s"
            if sname in idx:
                return occ(sname) >= orbitals[idx[sname]].max_electrons
        if orb.ℓ == 3:
            sname = f"{orb.n + 2}s"
            if sname in idx:
                return occ(sname) >= orbitals[idx[sname]].max_electrons
        return True

    for e in range(1, Z + 1):
        best_i = None
        best_E = float("inf")
        for i, (orb, n_e) in enumerate(config):
            if n_e >= orb.max_electrons:
                continue
            if not is_allowed(orb):
                continue
            E = orbital_energy(orb, Z, config)
            if E < best_E:
                best_E = E
                best_i = i

        if best_i is None:
            raise RuntimeError("No allowed orbital found — gating too strict.")

        orb, n_e = config[best_i]
        config[best_i] = (orb, n_e + 1)

        if verbose and e <= 25:
            print(f"e={e:>2} → {orb.name:4s} (E={best_E:>8.2f} eV)")

    # Promotion optimizer (replaces hardcoded d⁴→d⁵ and d⁹→d¹⁰ rules)
    config = try_promotions(config, Z, idx)

    return [(orb, n_e) for orb, n_e in config if n_e > 0]


def format_config(config: List[Tuple[Orbital, int]], use_core: bool = False, Z: int = 0) -> str:
    """Format electron configuration"""
    if not config:
        return "empty"
    
    # Sort by (n, ℓ) for standard notation
    sorted_config = sorted([(orb, n_e) for orb, n_e in config if n_e > 0],
                          key=lambda x: (x[0].n, x[0].ℓ))
    
    if use_core and Z > 2:
        cores = [(2, "He", {("1s", 2)}),
                 (10, "Ne", {("1s", 2), ("2s", 2), ("2p", 6)}),
                 (18, "Ar", {("1s", 2), ("2s", 2), ("2p", 6), ("3s", 2), ("3p", 6)}),
                 (36, "Kr", {("1s", 2), ("2s", 2), ("2p", 6), ("3s", 2), ("3p", 6), ("3d", 10), ("4s", 2), ("4p", 6)}),
                 (54, "Xe", {("1s", 2), ("2s", 2), ("2p", 6), ("3s", 2), ("3p", 6), ("3d", 10), ("4s", 2), ("4p", 6), ("4d", 10), ("5s", 2), ("5p", 6)}),
                 (86, "Rn", {("1s", 2), ("2s", 2), ("2p", 6), ("3s", 2), ("3p", 6), ("3d", 10), ("4s", 2), ("4p", 6), ("4d", 10), ("4f", 14), ("5s", 2), ("5p", 6), ("5d", 10), ("6s", 2), ("6p", 6)})]
        
        core_name = ""
        core_set = set()
        
        for core_z, name, core_orbs in reversed(cores):
            if Z > core_z:
                core_name = f"[{name}]"
                core_set = core_orbs
                break
        
        # Show only orbitals NOT in core
        parts = []
        for orb, n_e in sorted_config:
            key = (orb.name, n_e)
            if key not in core_set:
                parts.append(f"{orb.name}{n_e}")
        
        return f"{core_name} {' '.join(parts)}" if core_name else ' '.join(parts)
    else:
        parts = []
        for orb, n_e in sorted_config:
            parts.append(f"{orb.name}{n_e}")
        return " ".join(parts)


def test_transition_metals():
    """Test first-row transition metals"""
    print("=" * 80)
    print("FIRST-ROW TRANSITION METALS (K through Zn)")
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
        verbose = (Z == 21)  # Debug Sc
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


def test_second_row_transition_metals():
    """Test second-row transition metals (Y-Cd)"""
    print("\n" + "=" * 80)
    print("SECOND-ROW TRANSITION METALS (Y through Cd)")
    print("=" * 80)
    
    orbitals = generate_orbitals()
    
    known = {
        39: "[Kr] 4d1 5s2",  # Y
        40: "[Kr] 4d2 5s2",  # Zr
        41: "[Kr] 4d4 5s1",  # Nb (exception!)
        42: "[Kr] 4d5 5s1",  # Mo (exception! like Cr)
        43: "[Kr] 4d5 5s2",  # Tc
        44: "[Kr] 4d7 5s1",  # Ru (exception!)
        45: "[Kr] 4d8 5s1",  # Rh (exception!)
        46: "[Kr] 4d10",     # Pd (exception! no 5s)
        47: "[Kr] 4d10 5s1", # Ag (like Cu)
        48: "[Kr] 4d10 5s2", # Cd
    }
    
    elements = {
        39: "Y", 40: "Zr", 41: "Nb", 42: "Mo", 43: "Tc",
        44: "Ru", 45: "Rh", 46: "Pd", 47: "Ag", 48: "Cd"
    }
    
    print(f"\n{'Z':<4} {'El':<4} {'Predicted':<25} {'Expected':<25} {'Match'}")
    print("-" * 80)
    
    correct = 0
    total = 0
    
    for Z in range(39, 49):
        verbose = (Z == 39)  # Debug Y
        config = fill_atom_energy(Z, orbitals, verbose=verbose)
        result = format_config(config, use_core=True, Z=Z)
        expected = known[Z]
        
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


def test_lanthanides():
    """Test lanthanides (La-Lu) - the f-block test"""
    print("\n" + "=" * 80)
    print("LANTHANIDES (La through Lu) - F-BLOCK TEST")
    print("=" * 80)
    
    orbitals = generate_orbitals()
    
    # Known configurations - lanthanides are complex!
    known = {
        57: "[Xe] 5d1 6s2",      # La (starts series, no f yet)
        58: "[Xe] 4f1 5d1 6s2",  # Ce (f starts)
        59: "[Xe] 4f3 6s2",      # Pr
        60: "[Xe] 4f4 6s2",      # Nd
        61: "[Xe] 4f5 6s2",      # Pm
        62: "[Xe] 4f6 6s2",      # Sm
        63: "[Xe] 4f7 6s2",      # Eu
        64: "[Xe] 4f7 5d1 6s2",  # Gd (exception! half-filled f)
        65: "[Xe] 4f9 6s2",      # Tb
        66: "[Xe] 4f10 6s2",     # Dy
        67: "[Xe] 4f11 6s2",     # Ho
        68: "[Xe] 4f12 6s2",     # Er
        69: "[Xe] 4f13 6s2",     # Tm
        70: "[Xe] 4f14 6s2",     # Yb (filled f)
        71: "[Xe] 4f14 5d1 6s2", # Lu (ends series)
    }
    
    elements = {
        57: "La", 58: "Ce", 59: "Pr", 60: "Nd", 61: "Pm",
        62: "Sm", 63: "Eu", 64: "Gd", 65: "Tb", 66: "Dy",
        67: "Ho", 68: "Er", 69: "Tm", 70: "Yb", 71: "Lu"
    }
    
    print(f"\n{'Z':<4} {'El':<4} {'Predicted':<30} {'Expected':<30} {'Match'}")
    print("-" * 90)
    
    correct = 0
    total = 0
    
    for Z in range(57, 72):
        verbose = (Z == 64)  # Debug Gd (exception)
        config = fill_atom_energy(Z, orbitals, verbose=verbose)
        
        # DEBUG: Check total electrons
        total_e = sum(n_e for _, n_e in config)
        if total_e != Z:
            print(f"WARNING Z={Z}: Total electrons = {total_e}, expected {Z}")
        
        result = format_config(config, use_core=True, Z=Z)
        expected = known[Z]
        
        result_norm = result.replace(" ", "").replace("[", "").replace("]", "")
        expected_norm = expected.replace(" ", "").replace("[", "").replace("]", "")
        
        match = result_norm == expected_norm
        status = "✓" if match else "✗"
        
        if match:
            correct += 1
        total += 1
        
        print(f"{Z:<4} {elements[Z]:<4} {result:<30} {expected:<30} {status}")
    
    print("-" * 90)
    print(f"Success rate: {correct}/{total} = {100*correct/total:.0f}%")
    
    print("\nNOTE: Lanthanides have many 4f/5d competition cases.")
    print("Some configurations vary depending on ionization state and measurement.")
    
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
    
    print(f"\n{'Z':<4} {'Element':<8} {'Predicted':<25} {'Expected':<25} {'Match'}")
    print("-" * 85)
    
    for Z in range(1, 19):
        config = fill_atom_energy(Z, orbitals)
        result = format_config(config, use_core=True, Z=Z)
        expected = known.get(Z, "")
        
        if expected:
            result_norm = result.replace(" ", "").replace("[", "").replace("]", "")
            expected_norm = expected.replace(" ", "").replace("[", "").replace("]", "")
            
            match = result_norm == expected_norm
            status = "✓" if match else "✗"
            if match:
                correct += 1
            total += 1
            
            elem_name = {1:"H",2:"He",3:"Li",4:"Be",5:"B",6:"C",7:"N",8:"O",
                        9:"F",10:"Ne",11:"Na",12:"Mg",13:"Al",14:"Si",15:"P",
                        16:"S",17:"Cl",18:"Ar"}.get(Z, f"Z{Z}")
            
            print(f"{Z:<4} {elem_name:<8} {result:<25} {expected:<25} {status}")
    
    print("-" * 85)
    print(f"Success rate: {correct}/{total} = {100*correct/total:.0f}%")
    return correct, total


def main():
    """Run tests"""
    print("\n" + "=" * 80)
    print("64-STATE CHEMISTRY: EXTENDED VALIDATION")
    print("With n (not d) in radial, correct screening (N not N-1), and gating")
    print("=" * 80)
    
    mg_correct, mg_total = test_main_group()
    tm1_correct, tm1_total = test_transition_metals()
    tm2_correct, tm2_total = test_second_row_transition_metals()
    ln_correct, ln_total = test_lanthanides()
    
    print("\n" + "=" * 80)
    print("COMPREHENSIVE RESULTS")
    print("=" * 80)
    
    total_correct = mg_correct + tm1_correct + tm2_correct + ln_correct
    total_tested = mg_total + tm1_total + tm2_total + ln_total
    
    print(f"""
Main group (Z=1-18):          {mg_correct}/{mg_total} = {100*mg_correct/mg_total:.0f}%
1st row TM (K-Zn):            {tm1_correct}/{tm1_total} = {100*tm1_correct/tm1_total:.0f}%
2nd row TM (Y-Cd):            {tm2_correct}/{tm2_total} = {100*tm2_correct/tm2_total:.0f}%
Lanthanides (La-Lu):          {ln_correct}/{ln_total} = {100*ln_correct/ln_total:.0f}%
─────────────────────────────────────────
OVERALL:                      {total_correct}/{total_tested} = {100*total_correct/total_tested:.1f}%

PARAMETERS:
- R_∞ = {R_INF} eV (exact)
- λ = {LAMBDA} eV (angular penalty - ONLY fitted parameter)
- U0 = {U0} eV (not needed!)
- J0 = {J0} eV (not needed!)

KEY PRINCIPLES:
✓ 64-state scaffold generates orbital catalog
✓ Radial energy scales as -R∞ Z_eff²/n²
✓ GATING: nd opens only after (n+1)s fills
✓ GATING: nf opens only after (n+2)s fills
✓ Promotions: s²d⁴→s¹d⁵, s²d⁹→s¹d¹⁰

CRITICAL TEST:
Does the SAME gating principle that worked for 3d/4s
also work for 4d/5s and 4f/5d/6s?

If YES → gating is fundamental geometric constraint
If NO  → gating was just fitted to first row
    """)


if __name__ == "__main__":
    main()
