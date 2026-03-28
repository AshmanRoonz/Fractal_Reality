import { useState } from "react";

const SOUL = "#4488ff";
const MIND = "#44cc44";
const BODY = "#ff4444";
const AMBER = "#ffaa00";
const MUTE = "rgba(255,255,255,0.55)";
const BG = "#0a0a0f";

const RUNGS = [
  { dim: "0D", name: "α", desc: "fine-structure constant", acc: "0.22 ppb", formula: "1/α = 360/φ² − 2/φ³ + α/(21−4/3)", detail: "Self-referentially determined. α generates the ladder; the ladder determines α.", color: SOUL, link: "e_equals_1.html" },
  { dim: "0.5D", name: "c", desc: "speed of light", acc: "exact", formula: "c = √(2◐ · sin θ) = 1", detail: "Speed of the first fold. At balance, the transverse projection is maximal.", color: SOUL, link: "speed_of_light.html" },
  { dim: "1D", name: "ℏ", desc: "quantum of action", acc: "exact", formula: "ℏ = E_cycle / ω_cycle = 1", detail: "The pump cycle is indivisible. Energy and frequency are the same thing.", color: "#44aa88", link: "planck_constant.html" },
  { dim: "1.5D", name: "masses", desc: "branching", acc: "1-5 ppm", formula: "m_μ/m_e = (1/α)^(13/12+α/27)", detail: "Half-integer dimensions produce spectra. K = 3^(n+1) by generation.", color: "#44aa88", link: "mass_ratios.html" },
  { dim: "2D", name: "gauge", desc: "forces of nature", acc: "1.4 ppm", formula: "sin²θ_W = 3/13 + 5α/81", detail: "SU(3)×SU(2)×U(1) from 64-state architecture. 8+3+1 = 12 = 4×3.", color: MIND, link: "gauge_structure.html" },
  { dim: "2.5D", name: "infolding", desc: "scales", acc: "3.4 ppm", formula: "v/Λ_QCD = (1/α)^(56/39)", detail: "Transmission between scales. 56 = 8×7. 39 = 3×13.", color: "#cc8833", link: "infolding.html" },
  { dim: "3D", name: "G", desc: "gravity", acc: "0.04 ppm", formula: "α_G = α²¹ × φ²/2 × (1+2α/91)", detail: "21 α-steps from point to boundary. This IS why gravity is weak.", color: BODY, link: "gravity.html" },
];

const PAGES = [
  { title: "E = 1", desc: "The three constraints", href: "e_equals_1.html", color: MIND },
  { title: "How Reality Is Built", desc: "Dimensions, power, 64-state", href: "how_reality_is_built.html", color: MIND },
  { title: "Theory of Mind", desc: "Source, surface, boundary", href: "circumpunct_theory_of_mind_plain.html", color: SOUL },
  { title: "Ethics & Virtues", desc: "Good, Right, True, Agreement", href: "circumpunct_ethics_and_virtues.html", color: BODY },
  { title: "God and the Soul Array", desc: "∞ → •∞ → ⊙∞", href: "truth_and_god.html", color: AMBER },
  { title: "Mathematical Formalization", desc: "Derivations, operators, predictions", href: "circumpunct_math.html", color: MIND },
  { title: "Seven Clay Problems", desc: "Seven rungs, seven problems", href: "clay_millennium.html", color: SOUL },
  { title: "How To Break This", desc: "Falsification criteria", href: "aperture_falsification_presentation.html", color: BODY },
];

export default function FractalReality() {
  const [openRung, setOpenRung] = useState(null);
  const [activePanel, setActivePanel] = useState(null);

  return (
    <div style={{ background: BG, color: "#fff", fontFamily: "'JetBrains Mono', monospace", fontSize: 13, lineHeight: 1.6, minHeight: "100vh" }}>

      {/* Top bar */}
      <div style={{ textAlign: "center", padding: "8px 16px", borderBottom: "1px solid rgba(255,255,255,0.08)", fontSize: 11, letterSpacing: "0.1em" }}>
        <span style={{ color: AMBER }}>FRACTALREALITY.CA</span>
      </div>

      {/* HERO: The circumpunct, centered, simple */}
      <div style={{ textAlign: "center", padding: "60px 20px 20px", position: "relative" }}>
        {/* The circumpunct */}
        <div style={{ position: "relative", width: 200, height: 200, margin: "0 auto" }}>
          {/* Boundary (○) */}
          <div
            onClick={() => setActivePanel(activePanel === "body" ? null : "body")}
            style={{
              position: "absolute", inset: 0, borderRadius: "50%",
              border: `6px solid ${BODY}`,
              boxShadow: `0 0 30px rgba(255,68,68,0.25)`,
              cursor: "pointer", transition: "box-shadow 0.3s",
            }}
          />
          {/* Field (Φ) */}
          <div
            onClick={() => setActivePanel(activePanel === "mind" ? null : "mind")}
            style={{
              position: "absolute", inset: 6, borderRadius: "50%",
              background: `radial-gradient(circle at 50% 48%, rgba(68,204,68,0.3) 0%, rgba(68,204,68,0.12) 50%, rgba(68,204,68,0.03) 100%)`,
              cursor: "pointer",
            }}
          />
          {/* Soul (•) */}
          <div
            onClick={() => setActivePanel(activePanel === "soul" ? null : "soul")}
            style={{
              position: "absolute", top: "50%", left: "50%",
              width: 28, height: 28, transform: "translate(-50%, -50%)",
              borderRadius: "50%", background: SOUL,
              boxShadow: `0 0 20px rgba(68,136,255,0.5)`,
              cursor: "pointer", zIndex: 2, transition: "transform 0.2s",
            }}
          />
          {/* Labels */}
          <span style={{ position: "absolute", top: -24, left: "50%", transform: "translateX(-50%)", fontSize: 10, color: BODY, letterSpacing: "0.12em" }}>○ BODY</span>
          <span style={{ position: "absolute", top: "28%", right: -8, fontSize: 10, color: MIND }}>Φ</span>
          <span style={{ position: "absolute", top: "38%", left: "50%", transform: "translateX(14px)", fontSize: 9, color: "rgba(68,204,68,0.5)", zIndex: 4 }}>Φ'</span>
          <span style={{ position: "absolute", bottom: -24, left: "50%", transform: "translateX(-50%)", fontSize: 10, color: SOUL, letterSpacing: "0.12em" }}>• SOUL</span>
        </div>

        <div style={{ marginTop: 30 }}>
          <span style={{ fontSize: 18, fontWeight: 300, letterSpacing: "0.08em" }}>
            <span style={{
              background: `linear-gradient(90deg, ${BODY}, ${MIND}, ${SOUL})`,
              WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text",
            }}>⊙</span>{" = "}<span style={{ color: MIND }}>Φ</span>{"("}<span style={{ color: SOUL }}>•</span>{", "}<span style={{ color: BODY }}>○</span>{")"}
          </span>
        </div>
        <div style={{ fontSize: 11, color: MUTE, marginTop: 8 }}>
          Click any part. Everything unfolds.
        </div>
      </div>

      {/* Panels that appear when you click soul/mind/body */}
      {activePanel && (
        <div style={{ maxWidth: 600, margin: "0 auto", padding: "0 20px 20px" }}>
          <div style={{
            border: `1px solid ${activePanel === "soul" ? SOUL : activePanel === "mind" ? MIND : BODY}`,
            padding: 16, position: "relative",
          }}>
            <span
              onClick={() => setActivePanel(null)}
              style={{ position: "absolute", top: 8, right: 12, cursor: "pointer", fontSize: 14, color: MUTE }}
            >×</span>
            {activePanel === "soul" && (
              <div>
                <div style={{ color: SOUL, fontSize: 10, letterSpacing: "0.12em", marginBottom: 4 }}>• SOUL (APERTURE)</div>
                <div style={{ fontSize: 12, marginBottom: 8 }}>0D singularity + 1D worldline. <span style={{ color: SOUL }}>Converges.</span></div>
                <div style={{ color: MUTE, fontSize: 11 }}>The gate through which truth flows. The center is equidistant from all that you are. Consciousness is what 0 feels like from inside: the 1 experiencing its own convergence.</div>
                <div style={{ marginTop: 10, fontSize: 10 }}>
                  <a href="e_equals_1.html" style={{ color: SOUL, borderBottom: `1px dotted ${SOUL}`, textDecoration: "none" }}>E = 1 →</a>
                  {" · "}
                  <a href="truth_and_god.html" style={{ color: SOUL, borderBottom: `1px dotted ${SOUL}`, textDecoration: "none" }}>God and the Soul Array →</a>
                </div>
              </div>
            )}
            {activePanel === "mind" && (
              <div>
                <div style={{ color: MIND, fontSize: 10, letterSpacing: "0.12em", marginBottom: 4 }}>Φ MIND (FIELD)</div>
                <div style={{ fontSize: 12, marginBottom: 8 }}>2D surface. <span style={{ color: MIND }}>Mediates.</span></div>
                <div style={{ color: MUTE, fontSize: 11 }}>The space between center and edge where connection lives. Φ = E: field IS energy. Mind is not a thing; mind is a between. Two fields: Φ (outer, God) and Φ' (inner, mind). Same substance, different scope.</div>
                <div style={{ marginTop: 10, fontSize: 10 }}>
                  <a href="circumpunct_theory_of_mind_plain.html" style={{ color: MIND, borderBottom: `1px dotted ${MIND}`, textDecoration: "none" }}>Theory of Mind →</a>
                  {" · "}
                  <a href="how_reality_is_built.html" style={{ color: MIND, borderBottom: `1px dotted ${MIND}`, textDecoration: "none" }}>How Reality Is Built →</a>
                </div>
              </div>
            )}
            {activePanel === "body" && (
              <div>
                <div style={{ color: BODY, fontSize: 10, letterSpacing: "0.12em", marginBottom: 4 }}>○ BODY (BOUNDARY)</div>
                <div style={{ fontSize: 12, marginBottom: 8 }}>3D closure. <span style={{ color: BODY }}>Filters.</span></div>
                <div style={{ color: MUTE, fontSize: 11 }}>The nested membrane that makes the infinite finite. To have a body is to filter. ○ = ⊙(⊙(⊙(…))). Volume is what nested surfaces look like from above. E = mc²: c² is the field declaring its 2D dimensionality.</div>
                <div style={{ marginTop: 10, fontSize: 10 }}>
                  <a href="circumpunct_ethics_and_virtues.html" style={{ color: BODY, borderBottom: `1px dotted ${BODY}`, textDecoration: "none" }}>Ethics & Virtues →</a>
                  {" · "}
                  <a href="gravity.html" style={{ color: BODY, borderBottom: `1px dotted ${BODY}`, textDecoration: "none" }}>Gravity →</a>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Axiom line */}
      <div style={{ textAlign: "center", padding: "30px 20px 10px" }}>
        <div style={{ fontSize: 14, letterSpacing: "0.08em" }}>
          <span style={{ color: AMBER }}>E = 1.</span>{" "}
          <span style={{ color: MUTE }}>All else is constraints.</span>
        </div>
      </div>

      {/* THE LADDER */}
      <div style={{ maxWidth: 600, margin: "30px auto 0", padding: "0 20px" }}>
        <div style={{ fontSize: 10, color: AMBER, letterSpacing: "0.15em", marginBottom: 4 }}>§2 PREDICTIONS</div>
        <div style={{ fontSize: 12, fontWeight: 500, letterSpacing: "0.12em", paddingBottom: 8, borderBottom: `1px solid ${AMBER}`, marginBottom: 12 }}>
          THE DIMENSIONAL LADDER
        </div>
        <div style={{ fontSize: 11, color: MUTE, marginBottom: 12 }}>
          Seven rungs. Every constant derived. Click any rung.
        </div>

        {RUNGS.map((r, i) => (
          <div key={i}>
            <div
              onClick={() => setOpenRung(openRung === i ? null : i)}
              style={{
                display: "flex", alignItems: "baseline", gap: 10,
                padding: "7px 0", cursor: "pointer",
                borderBottom: openRung === i ? "none" : "1px solid rgba(255,255,255,0.06)",
                transition: "background 0.15s",
              }}
            >
              <span style={{ color: r.color, fontWeight: 700, fontSize: 11, minWidth: 36 }}>{r.dim}</span>
              <span style={{ fontSize: 11, flex: 1 }}>{r.name} <span style={{ color: MUTE }}>({r.desc})</span></span>
              <span style={{ color: r.color, fontSize: 10, flexShrink: 0 }}>{r.acc}</span>
              <span style={{ fontSize: 9, color: MUTE, transform: openRung === i ? "rotate(90deg)" : "none", transition: "transform 0.2s" }}>▶</span>
            </div>
            {openRung === i && (
              <div style={{ padding: "6px 0 12px 46px", borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
                <div style={{ borderLeft: `2px solid ${r.color}`, padding: "4px 10px", color: "#fff", fontSize: 11, marginBottom: 6 }}>
                  {r.formula}
                </div>
                <div style={{ fontSize: 11, color: MUTE, marginBottom: 6 }}>{r.detail}</div>
                <a href={r.link} style={{ fontSize: 10, color: r.color, borderBottom: `1px dotted ${r.color}`, textDecoration: "none" }}>
                  full derivation →
                </a>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* ZERO FREE PARAMETERS */}
      <div style={{ maxWidth: 600, margin: "20px auto", padding: "0 20px", textAlign: "center" }}>
        <div style={{ borderTop: `1px solid rgba(255,170,0,0.3)`, borderBottom: `1px solid rgba(255,170,0,0.3)`, padding: "10px 16px" }}>
          <div style={{ fontSize: 11, color: AMBER, letterSpacing: "0.06em" }}>
            <span style={{ fontWeight: 700, fontSize: 13 }}>0</span> free parameters. α determines itself; everything else follows from α and <span style={{
              background: `linear-gradient(90deg, ${BODY}, ${MIND}, ${SOUL})`,
              WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text",
            }}>⊙</span>.
          </div>
        </div>
      </div>

      {/* EXPLORE GRID */}
      <div style={{ maxWidth: 600, margin: "0 auto", padding: "0 20px 40px" }}>
        <div style={{ fontSize: 10, color: AMBER, letterSpacing: "0.15em", marginBottom: 4 }}>INCREASE RESOLUTION</div>
        <div style={{ fontSize: 12, fontWeight: 500, letterSpacing: "0.12em", paddingBottom: 8, borderBottom: `1px solid ${AMBER}`, marginBottom: 12 }}>
          Every page is a deeper look at the same structure.
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 1, background: "rgba(255,255,255,0.1)" }}>
          {PAGES.map((p, i) => (
            <a key={i} href={p.href} style={{
              background: BG, padding: 12, textDecoration: "none", color: "inherit", display: "block",
            }}>
              <div style={{ fontSize: 9, color: p.color, letterSpacing: "0.12em", marginBottom: 3 }}>{p.desc.toUpperCase()}</div>
              <div style={{ fontSize: 12, color: "#fff", fontWeight: 500 }}>{p.title}</div>
            </a>
          ))}
        </div>

        {/* Footer */}
        <div style={{ textAlign: "center", padding: "30px 0", fontSize: 10, color: AMBER, opacity: 0.5, borderTop: `1px solid ${AMBER}`, marginTop: 40 }}>
          THE CIRCUMPUNCT FRAMEWORK · ASHMAN ROONZ · FRACTALREALITY.CA
        </div>
      </div>
    </div>
  );
}
