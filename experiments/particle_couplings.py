"""
Particle Coupling Calculator
============================

Companion to unified_expression.py.  Asks: given the framework's §27.7
closed forms (α as input), what is |•_X| for any particle X?  That is,
what does X's entry in κ look like, across each field it couples to?

The §27.7a reframe says α = |•_electron|; the primary measurable
coupling of the electron's 0D aperture to the 0D aperture of the greater
whole, with 2D Φ (photon) as mediator.  Other particles have their own
|•| at κ_{0,0}.  For each (particle, field) pair the coupling strength
is what κ records; this file computes that strength where the framework
already has a closed form, and flags what remains measurement-input.

Structure of output:

    Particle  |  γ (EM)  |  H (Yukawa)  |  G (gravity)  |  W/Z (weak)  |  g (strong)
    -------  | -------  | -----------  | ------------  | -----------  | ----------
    electron |  α       |  m_e/v       |  α_G · m_e²   |  g·sin θ_W   |  -
    muon     |  α       |  m_μ/v       |  α_G · m_μ²   |  g·sin θ_W   |  -
    ...

Columns marked with a framework formula are derived from α alone.
Columns marked "measured" ship with their measurement value because the
framework does not yet pin them from first principles.

Run:  python3 particle_couplings.py
"""

import numpy as np
from math import pi
from dataclasses import dataclass, field
from typing import Optional, Dict

# Reuse the framework constants from unified_expression.py
from unified_expression import (
    ALPHA, ALPHA_G, SIN_THETA_C, SIN_THETA_W, SIN2_THETA_W, LAMBDA_HIGGS,
    PHI_GOLDEN, T_TRIAD, P_PUMP,
)


# ═══════════════════════════════════════════════════════════════
# Framework mass ladder  (§27.7j; all take α as input, return m/m_e)
# ═══════════════════════════════════════════════════════════════

def mass_ratio_lepton(generation: int) -> float:
    """m_ℓ / m_e from §27.7j, three generations."""
    if generation == 1: return 1.0
    if generation == 2: return (1.0 / ALPHA) ** (13.0/12.0 + ALPHA / 27.0)
    if generation == 3: return (1.0 / ALPHA) ** (58.0/35.0 + ALPHA / 81.0)
    raise ValueError(f"no lepton formula for generation {generation}")


def proton_to_electron() -> float:
    """m_p / m_e from §27.7j baryon composite formula."""
    return (1.0 / ALPHA) ** (1.5 + (11.0/3.0) * ALPHA + 13.0 * ALPHA**2)


def higgs_vev_over_electron() -> float:
    """v / m_e from §27.7k:  T³/α² · (1 - R·α)."""
    return (T_TRIAD ** 3) / (ALPHA ** 2) * (1.0 - 7.0 * ALPHA)


# Electron mass in MeV; framework takes this as measurement input
# (the framework pins m_p/m_e etc. as RATIOS; the overall scale is set
# by measurement).  Using CODATA 2022: m_e c² = 0.51099895 MeV.
M_E_MEV = 0.51099895

V_HIGGS_MEV = higgs_vev_over_electron() * M_E_MEV   # ≈ 245.9 GeV (§27.7k)


# ═══════════════════════════════════════════════════════════════
# Particle registry
# ═══════════════════════════════════════════════════════════════

@dataclass
class Particle:
    name: str
    symbol: str
    gen: int                         # generation 1, 2, 3 (leptons, quarks)
    electric_charge: float            # in units of |e|
    color: bool                      # True for quarks (SU(3) charged)
    weak_isospin: Optional[float]    # +1/2, -1/2, 0 (approx; for leptons/quarks)
    mass_mev: float                  # pole mass in MeV (framework or measured)
    mass_source: str                 # "framework" or "measured"

    def yukawa(self) -> float:
        """Higgs Yukawa coupling y_f = m_f · √2 / v."""
        return self.mass_mev * np.sqrt(2.0) / V_HIGGS_MEV

    def kappa_photon(self) -> float:
        """EM coupling entry at κ_{•,•}: Q² · α."""
        return (self.electric_charge ** 2) * ALPHA

    def kappa_gravity(self) -> float:
        """Gravitational coupling: α_G · (m/m_Planck)²; framework reports
           α_G as the fundamental rate; mass weighting sets per-particle
           strength."""
        # Planck mass in MeV: framework-side M_Pl/m_e = (1/α)^(21/2) · √2/φ
        m_pl_over_me = (1.0 / ALPHA) ** (21.0/2.0) * np.sqrt(2.0) / PHI_GOLDEN
        m_pl_mev = m_pl_over_me * M_E_MEV
        return ALPHA_G * (self.mass_mev / m_pl_mev) ** 2

    def kappa_weak(self) -> Optional[float]:
        """Weak coupling: g · I_3 where g = e/sin θ_W.
           Framework provides sin θ_W (§27.7k); g = √(4πα)/sin θ_W."""
        if self.weak_isospin is None: return None
        g = np.sqrt(4 * pi * ALPHA) / SIN_THETA_W
        return g * abs(self.weak_isospin)

    def kappa_strong(self) -> Optional[float]:
        """Strong coupling α_s; NOT framework-derived (measurement input).
           Using α_s(m_Z) ≈ 0.1179 (PDG 2022) for colored particles."""
        if not self.color: return None
        return 0.1179    # measured; flagged below


# ─── The known particles, with framework-sourced masses where available ───

def build_registry() -> Dict[str, Particle]:
    reg: Dict[str, Particle] = {}

    # ─────── Leptons ────────────────────────────────────
    reg["e"]  = Particle("electron",  "e⁻",  gen=1, electric_charge=-1.0,
                         color=False, weak_isospin=-0.5,
                         mass_mev=M_E_MEV, mass_source="input scale")
    reg["mu"] = Particle("muon",      "μ⁻",  gen=2, electric_charge=-1.0,
                         color=False, weak_isospin=-0.5,
                         mass_mev=mass_ratio_lepton(2) * M_E_MEV,
                         mass_source="framework (§27.7j)")
    reg["tau"]= Particle("tau",       "τ⁻",  gen=3, electric_charge=-1.0,
                         color=False, weak_isospin=-0.5,
                         mass_mev=mass_ratio_lepton(3) * M_E_MEV,
                         mass_source="framework (§27.7j)")
    reg["nu_e"]  = Particle("electron-neutrino", "νₑ",  gen=1, electric_charge=0.0,
                            color=False, weak_isospin=+0.5,
                            mass_mev=0.0, mass_source="unaddressed")

    # ─────── Quarks ─────────────────────────────────────
    # Framework doesn't yet have clean closed forms for individual quark
    # masses (mesons have them, quarks don't); using PDG 2022 current
    # masses and flagging as measured.  Constituent masses differ.
    reg["u"] = Particle("up",        "u",   gen=1, electric_charge=+2.0/3.0,
                        color=True, weak_isospin=+0.5,
                        mass_mev=2.16,  mass_source="measured (PDG)")
    reg["d"] = Particle("down",      "d",   gen=1, electric_charge=-1.0/3.0,
                        color=True, weak_isospin=-0.5,
                        mass_mev=4.67,  mass_source="measured (PDG)")
    reg["c"] = Particle("charm",     "c",   gen=2, electric_charge=+2.0/3.0,
                        color=True, weak_isospin=+0.5,
                        mass_mev=1.273e3, mass_source="measured (PDG)")
    reg["s"] = Particle("strange",   "s",   gen=2, electric_charge=-1.0/3.0,
                        color=True, weak_isospin=-0.5,
                        mass_mev=93.4,    mass_source="measured (PDG)")
    reg["t"] = Particle("top",       "t",   gen=3, electric_charge=+2.0/3.0,
                        color=True, weak_isospin=+0.5,
                        mass_mev=172.69e3, mass_source="measured (PDG)")
    reg["b"] = Particle("bottom",    "b",   gen=3, electric_charge=-1.0/3.0,
                        color=True, weak_isospin=-0.5,
                        mass_mev=4.18e3,  mass_source="measured (PDG)")

    # ─────── Gauge / Higgs bosons ───────────────────────
    # Masses from §27.7k
    W_OVER_E = (1.0 / ALPHA) ** (95.0/39.0 - ALPHA / 2.0)
    W_MEV    = W_OVER_E * M_E_MEV
    Z_MEV    = W_MEV / np.sqrt(1.0 - SIN2_THETA_W)
    H_MEV    = np.sqrt(2.0 * LAMBDA_HIGGS) * V_HIGGS_MEV

    reg["W"] = Particle("W-boson",   "W±",  gen=0, electric_charge=+1.0,
                        color=False, weak_isospin=+1.0,
                        mass_mev=W_MEV, mass_source="framework (§27.7k)")
    reg["Z"] = Particle("Z-boson",   "Z⁰",  gen=0, electric_charge=0.0,
                        color=False, weak_isospin=0.0,
                        mass_mev=Z_MEV, mass_source="framework (§27.7k)")
    reg["H"] = Particle("Higgs",     "H⁰",  gen=0, electric_charge=0.0,
                        color=False, weak_isospin=0.0,
                        mass_mev=H_MEV, mass_source="framework (§27.7k)")
    reg["gamma"] = Particle("photon", "γ",  gen=0, electric_charge=0.0,
                            color=False, weak_isospin=None,
                            mass_mev=0.0, mass_source="massless (A4)")
    reg["g"] = Particle("gluon",      "g",  gen=0, electric_charge=0.0,
                        color=True,  weak_isospin=None,
                        mass_mev=0.0, mass_source="massless (SU(3) closed)")

    return reg


# ═══════════════════════════════════════════════════════════════
# Coupling table printout
# ═══════════════════════════════════════════════════════════════

def print_coupling_table(reg: Dict[str, Particle]) -> None:
    print()
    print("═" * 98)
    print(f"  PARTICLE COUPLINGS FROM THE §27.7 COUPLING FAMILY")
    print(f"  (α = {ALPHA:.8f} as sole input; v = {V_HIGGS_MEV/1000:.2f} GeV; "
          f"α_G = {ALPHA_G:.2e})")
    print("═" * 98)
    print(f"  {'particle':<10} {'mass':>11} {'γ (Q²α)':>12} {'Yukawa':>10} "
          f"{'α_G·(m/M_Pl)²':>15} {'weak g·I₃':>11} {'α_s':>8}  mass-src")
    print(f"  {'-'*10} {'-'*11} {'-'*12} {'-'*10} {'-'*15} {'-'*11} {'-'*8}  {'-'*22}")

    order = ["e", "mu", "tau", "nu_e",
             "u", "d", "c", "s", "t", "b",
             "gamma", "g", "W", "Z", "H"]
    for key in order:
        p = reg[key]
        mass_str = _format_mass(p.mass_mev)
        em = f"{p.kappa_photon():.3e}" if p.electric_charge != 0 else "0"
        yuk = f"{p.yukawa():.3e}" if p.mass_mev > 0 else "0"
        grav = f"{p.kappa_gravity():.2e}" if p.mass_mev > 0 else "0"
        weak = f"{p.kappa_weak():.3f}" if p.kappa_weak() is not None else "-"
        strong = f"{p.kappa_strong():.3f}" if p.kappa_strong() is not None else "-"
        print(f"  {p.symbol:<10} {mass_str:>11} {em:>12} {yuk:>10} "
              f"{grav:>15} {weak:>11} {strong:>8}  {p.mass_source}")
    print()


def _format_mass(m_mev: float) -> str:
    if m_mev == 0: return "0"
    if m_mev < 1: return f"{m_mev*1000:.3f} keV"
    if m_mev < 1000: return f"{m_mev:.3f} MeV"
    return f"{m_mev/1000:.3f} GeV"


# ═══════════════════════════════════════════════════════════════
# Drill-down: which κ entry is which coupling?
# ═══════════════════════════════════════════════════════════════

def print_kappa_interpretation() -> None:
    print("═" * 98)
    print("  WHICH κ ENTRY CARRIES WHICH COUPLING?")
    print("═" * 98)
    rows = [
        ("γ  (photon)",      "κ[•,Φ] = Q² · α",
         "0D aperture coupled to 2D mediator; fine-structure; per-particle by Q"),
        ("H  (Higgs)",       "κ[—,Φ] = λ_H; weighted by y_f = m_f√2/v",
         "1D committed mass coupled to 2D field; §27.7i, §27.7k"),
        ("W,Z (weak)",       "κ[Φ,○] = sin θ_W; weighted by I₃",
         "2D field to 3D boundary; electroweak; §13.15"),
        ("G  (graviton)",    "κ[○,○] = α_G; weighted by (m/M_Pl)²",
         "3D boundary to 3D boundary across scales; §27.7g; universal"),
        ("g  (gluon)",       "κ[•,—] slot candidate?; α_s not derived",
         "Color SU(3) mediator; framework has SU(3)=8 structurally but "
         "α_s value is measurement-input"),
        ("CKM (quark mix)",  "κ[•,—] = sin θ_C · α",
         "Inter-generation •↔— mixing; §27.7h; Cabibbo only (θ_13, θ_23, δ "
         "still open)"),
        ("PMNS (ν mix)",     "not yet mapped",
         "Neutrino mixing; framework does not yet address"),
    ]
    for field_name, formula, interp in rows:
        print(f"  {field_name:<18} {formula}")
        print(f"                     {interp}")
        print()


# ═══════════════════════════════════════════════════════════════
# The coupling ladder:  every dimensionless constant as α at its rung
# ═══════════════════════════════════════════════════════════════

def print_coupling_ladder() -> None:
    """Every dimensionless physical constant as α-compounded at its
    ladder rung (§27.7o field fineness principle)."""
    m_mu_me  = mass_ratio_lepton(2)
    m_tau_me = mass_ratio_lepton(3)
    m_p_me   = proton_to_electron()
    v_over_lambda_QCD = (1.0 / ALPHA) ** (56.0 / 39.0)

    SU3 = 8
    Lam = (ALPHA ** 56) * (1.0 - 6.0 * ALPHA + 4.0 * ALPHA * ALPHA) / (SU3 * T_TRIAD * T_TRIAD)
    m_pl_over_me = (1.0 / ALPHA) ** (21.0 / 2.0) * np.sqrt(2.0) / PHI_GOLDEN

    v_me = higgs_vev_over_electron()
    a_f  = f"{ALPHA:.6e}"
    mu_f = f"{m_mu_me:.4f}"
    ta_f = f"{m_tau_me:.2f}"
    pp_f = f"{m_p_me:.4f}"
    pi_f = f"{pi:.9f}"
    w2_f = f"{SIN2_THETA_W:.6f}"
    cb_f = f"{SIN_THETA_C:.6f}"
    lH_f = f"{LAMBDA_HIGGS:.6f}"
    vL_f = f"{v_over_lambda_QCD:.2f}"
    vm_f = f"{v_me:.2f}"
    mp_f = f"{m_pl_over_me:.3e}"
    aG_f = f"{ALPHA_G:.3e}"
    La_f = f"{Lam:.3e}"

    bar_big  = "=" * 112
    bar_mid  = "-" * 112

    print()
    print(bar_big)
    print("  THE COUPLING LADDER:  EVERY DIMENSIONLESS CONSTANT AS ALPHA AT ITS RUNG  (§27.7o)")
    print(bar_big)
    print(f"  alpha-input = {ALPHA:.9f}    phi = {PHI_GOLDEN:.9f}    T = {T_TRIAD}    "
          f"P = {P_PUMP}    SU(3) = 8    R = 7    V = 13")
    print(bar_mid)
    print(f"  {'rung':<6} {'stn':<4} {'constant':<14} {'formula':<38} "
          f"{'a-exp':>8} {'value':>18}   physics")
    print(f"  {'-'*6} {'-'*4} {'-'*14} {'-'*38} {'-'*8} {'-'*18}   {'-'*26}")

    rows = [
        ("0D",   "•", "alpha",      "alpha",                                       "1",     a_f,          "fine structure (§27.7a)"),
        ("0.5D", "*", "c",          "sin(i) at balance 1/2",                       "-",     "1 (c=1)",    "speed of light"),
        ("1D",   "—", "hbar",       "one pump cycle",                              "-",     "1 (hbar=1)", "indivisible action"),
        ("1.5D", "Y", "m_mu/m_e",   "(1/a)^(13/12 + a/27)",                        "13/12", mu_f,         "muon/electron (§27.7j)"),
        ("1.5D", "Y", "m_tau/m_e",  "(1/a)^(58/35 + a/81)",                        "58/35", ta_f,         "tau/electron (§27.7j)"),
        ("1.5D", "Y", "m_p/m_e",    "(1/a)^(3/2 + (11/3)a + 13 a^2)",              "3/2",   pp_f,         "proton/electron (§27.7j)"),
        ("2D",   "Φ", "pi",         "closure round a centre",                      "0",     pi_f,         "mediation (§27.7l)"),
        ("2D",   "Φ", "sin^2 th_W", "3/13 + 5a/81",                                "0",     w2_f,         "Weinberg angle (§13.15)"),
        ("2D",   "Φ", "sin th_C",   "a^(1/2 + 3a/7) * 8/3",                        "1/2",   cb_f,         "Cabibbo angle (§27.7h)"),
        ("2D",   "Φ", "lambda_H",   "(1/8)(1 + 5a - 8 a^2)",                       "0",     lH_f,         "Higgs quartic (§27.7i)"),
        ("2.5D", "*", "v/Lam_QCD",  "(1/a)^(56/39)",                               "56/39", vL_f,         "EW-to-QCD"),
        ("2.5D", "*", "v/m_e",      "T^3/a^2 * (1 - 7 a)",                         "-2",    vm_f,         "Higgs VEV (§27.7k)"),
        ("3D",   "○", "M_Pl/m_e",   "(1/a)^(21/2) * sqrt(2)/phi",                  "21/2",  mp_f,         "Planck mass (§27.7j)"),
        ("3D",   "○", "alpha_G",    "a^21 * phi^2/2 * (1 + 2a/91)",                "21",    aG_f,         "gravity (§27.7g)"),
        ("Lam",  "Λ", "Lam/M_Pl^4", "a^56 * (1 - 6a + 4 a^2) / (SU3 * T^2)",       "56",    La_f,         "cosmological constant (§12.2)"),
    ]

    for rung, glyph, name, formula, aexp, value, physics in rows:
        print(f"  {rung:<6} {glyph:<4} {name:<14} {formula:<38} "
              f"{aexp:>8} {value:>18}   {physics}")

    print(bar_mid)
    print("  Reading:  every dimensionless constant is alpha at a specific ladder rung.")
    print("            Exponent = A(d) = d(2d+1) at structural rungs: 0, 1, 3, 6, 10, 15, 21, 28.")
    print("            alpha itself is a^1 at 0D (§27.7a).  Gravity is a^21 at 3D (§27.7g).")
    print("            Cosmological Lambda sits at a^56 = SU(3)*R, one level beyond closure.")
    print("            Field Fineness Principle (§27.7o): every coupling is a nesting-tightness reading.")
    print()


# ═══════════════════════════════════════════════════════════════
# Spot-check a specific particle
# ═══════════════════════════════════════════════════════════════

def describe(particle_key: str) -> None:
    reg = build_registry()
    if particle_key not in reg:
        print(f"Unknown particle: {particle_key}.  Known: {list(reg.keys())}")
        return
    p = reg[particle_key]
    print()
    print("-" * 72)
    print(f"  PARTICLE:  {p.name}  ({p.symbol})    generation {p.gen}")
    print("-" * 72)
    print(f"    electric charge Q  = {p.electric_charge:+.4f} e")
    print(f"    color              = {'yes (SU(3))' if p.color else 'no'}")
    print(f"    weak isospin I3    = {p.weak_isospin}")
    print(f"    mass               = {_format_mass(p.mass_mev)}  ({p.mass_source})")
    print()
    print(f"  kappa entries for this particle:")
    print(f"    photon  k[.,F]    = Q^2 * a    = {p.kappa_photon():.6e}")
    if p.mass_mev > 0:
        y = p.yukawa()
        print(f"    Higgs   k[-,F] y   = m sqrt(2)/v  = {y:.6e}")
        grav = p.kappa_gravity()
        print(f"    gravity k[O,O] g   = a_G*(m/M_Pl)^2 = {grav:.3e}")
    if p.kappa_weak() is not None:
        print(f"    weak    k[F,O] g*I3 = {p.kappa_weak():.6f}")
    if p.kappa_strong() is not None:
        print(f"    strong  a_s        = {p.kappa_strong():.4f}   (measurement input)")
    print()


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Particle coupling calculator")
    parser.add_argument('--particle', type=str, default=None,
                        help="Describe one particle (e, mu, tau, u, d, c, s, t, b, "
                             "gamma, g, W, Z, H, nu_e)")
    parser.add_argument('--interpret', action='store_true',
                        help="Explain which kappa entry carries which coupling")
    parser.add_argument('--ladder', action='store_true',
                        help="Print the coupling ladder: every dimensionless "
                             "constant as alpha at its rung (§27.7o)")
    args = parser.parse_args()

    reg = build_registry()

    if args.ladder:
        print_coupling_ladder()
    elif args.particle:
        describe(args.particle)
    else:
        print_coupling_table(reg)
        if args.interpret:
            print_kappa_interpretation()
