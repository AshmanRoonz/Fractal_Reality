import React, { useState } from 'react';
import { Circle, Triangle, ArrowRight, GitBranch, Infinity, Zap } from 'lucide-react';

const FractalRealityDiagram = () => {
  const [activeSection, setActiveSection] = useState('overview');

  const sections = {
    overview: 'Complete Framework',
    fractalization: 'Fractalization Event',
    validation: '[ICE] Validation',
    dimensional: 'Dimensional Cascade',
    empirical: 'Empirical Data'
  };

  return (
    <div className="w-full min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white p-4 md:p-8 overflow-auto">
      {/* Header */}
      <div className="text-center mb-8 pb-6 border-b-2 border-purple-500/30">
        <h1 className="text-4xl md:text-5xl font-bold mb-2 bg-gradient-to-r from-purple-400 via-blue-400 to-cyan-400 bg-clip-text text-transparent drop-shadow-lg">
          FRACTAL REALITY FRAMEWORK
        </h1>
        <p className="text-xl md:text-2xl text-purple-300 mb-1">Mathematical Formalism & Empirical Validation</p>
        <p className="text-sm md:text-base text-slate-400 mt-4">∞ ↔ • ↔ ∞' | Being ↔ Becoming | D = 1.503 ± 0.040</p>
        <div className="flex justify-center gap-4 mt-4">
          {Object.entries(sections).map(([key, label]) => (
            <button
              key={key}
              onClick={() => setActiveSection(key)}
              className={`px-4 py-2 rounded-lg transition-all duration-300 ${
                activeSection === key
                  ? 'bg-purple-600 shadow-lg shadow-purple-500/50'
                  : 'bg-slate-900 hover:bg-slate-800'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto">
        {activeSection === 'overview' && <OverviewSection />}
        {activeSection === 'fractalization' && <FractalizationSection />}
        {activeSection === 'validation' && <ValidationSection />}
        {activeSection === 'dimensional' && <DimensionalSection />}
        {activeSection === 'empirical' && <EmpiricalSection />}
      </div>
    </div>
  );
};

const OverviewSection = () => (
  <div className="space-y-8">
    {/* Core Equation */}
    <div className="bg-slate-900 rounded-lg p-6 border-2 border-purple-500 shadow-lg shadow-purple-500/20">
      <h2 className="text-2xl font-bold mb-4 text-center">The Fundamental Equation</h2>
      <div className="text-center text-3xl md:text-4xl font-mono mb-4 text-purple-300 drop-shadow-glow">
        ∞ → • → ∞•'
      </div>
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div className="bg-slate-800 p-4 rounded">
          <div className="font-bold text-purple-300 mb-2">∞ (Infinity)</div>
          <div>Infinite possible patterns</div>
          <div className="text-slate-400">Unbounded possibility space</div>
          <div className="mt-2 font-mono text-xs">Hilbert space: ℋ = ∫|ψ⟩⟨ψ|dψ</div>
        </div>
        <div className="bg-slate-800 p-4 rounded">
          <div className="font-bold text-purple-300 mb-2">∞' (Finite Patterns)</div>
          <div>Finite validated patterns</div>
          <div className="text-slate-400">Geometric texture with boundaries</div>
          <div className="mt-2 font-mono text-xs">D ≈ 1.5 (fractal dimension)</div>
        </div>
        <div className="bg-slate-800 p-4 rounded">
          <div className="font-bold text-purple-300 mb-2">• (Singularity)</div>
          <div>Ultimate aperture operator</div>
          <div className="text-slate-400">Eternal ∇ + ℰ function</div>
          <div className="mt-2 font-mono text-xs">â = ∇̂ + Ê (operator form)</div>
        </div>
        <div className="bg-slate-800 p-4 rounded">
          <div className="font-bold text-purple-300 mb-2">•' (Operators)</div>
          <div>Fractalized apertures</div>
          <div className="text-slate-400">Boundary-creating operators</div>
          <div className="mt-2 font-mono text-xs">∂Ω: validation boundaries</div>
        </div>
      </div>
    </div>

    {/* Universal Pattern */}
    <div className="bg-slate-900 rounded-lg p-6 border-2 border-blue-500">
      <h2 className="text-2xl font-bold mb-4 text-center">Universal Pattern</h2>
      <div className="flex items-center justify-center gap-8 text-2xl font-mono">
        <div className="text-center">
          <div className="text-3xl mb-2">∇</div>
          <div className="text-sm text-blue-300">Convergence</div>
          <div className="text-xs text-slate-400 mt-1">Parts → Operator</div>
        </div>
        <ArrowRight className="text-blue-400" size={32} />
        <div className="text-center">
          <div className="text-3xl mb-2">[ICE]</div>
          <div className="text-sm text-green-300">Validation</div>
          <div className="text-xs text-slate-400 mt-1">6-fold test</div>
        </div>
        <ArrowRight className="text-blue-400" size={32} />
        <div className="text-center">
          <div className="text-3xl mb-2">ℰ</div>
          <div className="text-sm text-purple-300">Emergence</div>
          <div className="text-xs text-slate-400 mt-1">Operator → Patterns</div>
        </div>
      </div>
      <div className="mt-6 text-center text-slate-300">
        Every persistent structure (particles, atoms, cells, organisms, galaxies) operates through this pattern
      </div>
    </div>

    {/* Four Fundamentals Visual */}
    <div className="grid grid-cols-2 gap-6">
      <div className="bg-gradient-to-br from-purple-900 to-slate-900 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">Before Fractalization</h3>
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <Infinity className="text-purple-400" />
            <div>
              <div className="font-bold">∞ Infinity</div>
              <div className="text-sm text-slate-400">Infinite possibility</div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Circle className="text-blue-400" />
            <div>
              <div className="font-bold">• Singularity</div>
              <div className="text-sm text-slate-400">Ultimate operator</div>
            </div>
          </div>
        </div>
        <div className="mt-4 text-sm text-slate-300 italic">
          Incomplete: potential without boundaries
        </div>
      </div>
      
      <div className="bg-gradient-to-br from-green-900 to-slate-900 p-6 rounded-lg">
        <h3 className="text-xl font-bold mb-4">After Fractalization</h3>
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <GitBranch className="text-green-400" />
            <div>
              <div className="font-bold">∞' Finite Patterns</div>
              <div className="text-sm text-slate-400">Validated texture</div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Zap className="text-yellow-400" />
            <div>
              <div className="font-bold">•' Operators</div>
              <div className="text-sm text-slate-400">Boundary creators</div>
            </div>
          </div>
        </div>
        <div className="mt-4 text-sm text-slate-300 italic">
          Complete: boundaries transform infinite → finite
        </div>
      </div>
    </div>
  </div>
);

const FractalizationSection = () => (
  <div className="space-y-8">
    <div className="bg-slate-900 rounded-lg p-6 border-2 border-purple-500">
      <h2 className="text-2xl font-bold mb-4">The Fractalization Event</h2>
      <div className="text-center mb-6">
        <div className="text-4xl font-mono mb-2">∞ → • → ∞•'</div>
        <p className="text-slate-300">Infinite possibility fractalizes through ultimate aperture into infinite boundary-creating operators</p>
      </div>

      <div className="grid grid-cols-3 gap-4 mt-6">
        <div className="bg-slate-800 p-4 rounded">
          <h3 className="font-bold text-purple-300 mb-3">Step 1: Input</h3>
          <div className="text-2xl mb-2">∞</div>
          <div className="text-sm space-y-1">
            <div>• Unbounded Hilbert space</div>
            <div>• All possible wavefunctions</div>
            <div>• No boundaries yet</div>
            <div className="font-mono text-xs mt-2">ψ ∈ ℋ, ∫|ψ|²dV = ∞</div>
          </div>
        </div>

        <div className="bg-slate-800 p-4 rounded">
          <h3 className="font-bold text-blue-300 mb-3">Step 2: Operator</h3>
          <div className="text-2xl mb-2">•</div>
          <div className="text-sm space-y-1">
            <div>• Ultimate aperture</div>
            <div>• Eternal ∇ + ℰ function</div>
            <div>• Creates fractalization</div>
            <div className="font-mono text-xs mt-2">â = ∇̂ + Ê</div>
          </div>
        </div>

        <div className="bg-slate-800 p-4 rounded">
          <h3 className="font-bold text-green-300 mb-3">Step 3: Output</h3>
          <div className="text-2xl mb-2">∞•'</div>
          <div className="text-sm space-y-1">
            <div>• Infinite operators •'</div>
            <div>• Each creates boundaries</div>
            <div>• Transform ∞ → ∞'</div>
            <div className="font-mono text-xs mt-2">∂Ω: ∞ → ∞'</div>
          </div>
        </div>
      </div>

      <div className="mt-6 bg-slate-800 p-4 rounded">
        <h3 className="font-bold mb-2">Mathematical Expression</h3>
        <div className="font-mono text-sm space-y-2">
          <div>Fractalization: <span className="text-purple-400">F: ∞ ⊗ • → ∞•'</span></div>
          <div>Each operator: <span className="text-blue-400">•'ᵢ: ∞ → ∞'</span></div>
          <div>Boundary creation: <span className="text-green-400">∂Ωᵢ = {`{x : [ICE](x) = true}`}</span></div>
          <div>Validation: <span className="text-yellow-400">∇ → [I·C·E]ᵢₙ ⊗ [I·C·E]ₒᵤₜ → ℰ</span></div>
        </div>
      </div>
    </div>

    <div className="bg-slate-900 rounded-lg p-6">
      <h3 className="text-xl font-bold mb-4">Nested Operator Structure</h3>
      <div className="flex justify-center items-center">
        <svg width="600" height="400" viewBox="0 0 600 400">
          {/* Outer circle - Ultimate aperture */}
          <circle cx="300" cy="200" r="180" fill="none" stroke="#a78bfa" strokeWidth="3" />
          <text x="300" y="40" textAnchor="middle" fill="#a78bfa" fontSize="20" fontWeight="bold">
            • (Ultimate Aperture)
          </text>
          
          {/* Middle circles - Fractalized operators */}
          <circle cx="200" cy="200" r="80" fill="none" stroke="#60a5fa" strokeWidth="2" />
          <circle cx="400" cy="200" r="80" fill="none" stroke="#60a5fa" strokeWidth="2" />
          <text x="200" y="190" textAnchor="middle" fill="#60a5fa" fontSize="16">•'₁</text>
          <text x="400" y="190" textAnchor="middle" fill="#60a5fa" fontSize="16">•'₂</text>
          
          {/* Inner circles - Nested operators */}
          <circle cx="180" cy="220" r="30" fill="none" stroke="#34d399" strokeWidth="1.5" />
          <circle cx="220" cy="220" r="30" fill="none" stroke="#34d399" strokeWidth="1.5" />
          <circle cx="380" cy="220" r="30" fill="none" stroke="#34d399" strokeWidth="1.5" />
          <circle cx="420" cy="220" r="30" fill="none" stroke="#34d399" strokeWidth="1.5" />
          
          {/* Infinity symbols */}
          <text x="300" y="380" textAnchor="middle" fill="#fbbf24" fontSize="24">∞</text>
          <text x="150" y="200" textAnchor="middle" fill="#f87171" fontSize="18">∞'</text>
          <text x="450" y="200" textAnchor="middle" fill="#f87171" fontSize="18">∞'</text>
          
          {/* Arrows */}
          <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
              <polygon points="0 0, 10 3, 0 6" fill="#a78bfa" />
            </marker>
          </defs>
          <line x1="300" y1="360" x2="300" y2="220" stroke="#a78bfa" strokeWidth="2" markerEnd="url(#arrowhead)" />
          
          {/* Labels */}
          <text x="320" y="290" fill="#e5e7eb" fontSize="14">∇ (Convergence)</text>
          <text x="120" y="140" fill="#e5e7eb" fontSize="14">ℰ (Emergence)</text>
          <text x="440" y="140" fill="#e5e7eb" fontSize="14">ℰ (Emergence)</text>
        </svg>
      </div>
      <div className="text-center text-sm text-slate-300 mt-4">
        Reality consists of infinite nested aperture operators, each creating boundaries that transform ∞ → ∞'
      </div>
    </div>
  </div>
);

const ValidationSection = () => (
  <div className="space-y-8">
    <div className="bg-slate-900 rounded-lg p-6 border-2 border-green-500 shadow-lg shadow-green-500/20">
      <h2 className="text-2xl font-bold mb-4">[ICE] Validation: 6-Fold Test</h2>
      
      <div className="grid grid-cols-2 gap-6 mb-6">
        <div className="bg-slate-800 p-4 rounded">
          <h3 className="font-bold text-blue-300 mb-3">Input Interface: Parts → Operator</h3>
          <div className="space-y-2 text-sm">
            <div className="flex items-start gap-2">
              <div className="font-bold text-blue-400">I₁:</div>
              <div>Can boundary be maintained? (Interface)</div>
            </div>
            <div className="flex items-start gap-2">
              <div className="font-bold text-purple-400">C₁:</div>
              <div>Is there coherence with •' AND alignment toward •? (Center)</div>
            </div>
            <div className="flex items-start gap-2">
              <div className="font-bold text-green-400">E₁:</div>
              <div>Is this grounded in actual field ∞? (Evidence)</div>
            </div>
          </div>
        </div>

        <div className="bg-slate-800 p-4 rounded">
          <h3 className="font-bold text-purple-300 mb-3">Output Interface: Operator → Patterns</h3>
          <div className="space-y-2 text-sm">
            <div className="flex items-start gap-2">
              <div className="font-bold text-blue-400">I₂:</div>
              <div>Can boundary be maintained? (Interface)</div>
            </div>
            <div className="flex items-start gap-2">
              <div className="font-bold text-purple-400">C₂:</div>
              <div>Is there coherence with •' AND alignment toward •? (Center)</div>
            </div>
            <div className="flex items-start gap-2">
              <div className="font-bold text-green-400">E₂:</div>
              <div>Is this grounded in actual field ∞? (Evidence)</div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-slate-800 p-4 rounded">
        <h3 className="font-bold mb-3">Mathematical Formalism</h3>
        <div className="font-mono text-sm space-y-2">
          <div className="text-blue-300">Interface (I): ||∂Ω|| {`<`} ℓ_max (Boundary maintenance)</div>
          <div className="text-purple-300">Center (C): ⟨ψ|â|ψ⟩ ≠ 0 ∧ ∇·ℰ → • (Coherence & Alignment)</div>
          <div className="text-green-300">Evidence (E): ψ ∈ ℋ_physical (Grounded in reality)</div>
          <div className="mt-4 text-yellow-300">
            Validation: V(ψ) = I₁ ∧ C₁ ∧ E₁ ∧ I₂ ∧ C₂ ∧ E₂
          </div>
          <div className="text-white">
            Pattern persists ↔ V(ψ) = TRUE
          </div>
        </div>
      </div>
    </div>

    <div className="bg-slate-900 rounded-lg p-6">
      <h3 className="text-xl font-bold mb-4">From [ICE] to Schrödinger Equation</h3>
      <div className="bg-slate-800 p-4 rounded mb-4">
        <h4 className="font-bold mb-2">The Bridge Theorem</h4>
        <p className="text-sm mb-3">Given four interface validation constraints:</p>
        <div className="space-y-2 text-sm">
          <div>1. <span className="text-blue-300">Locality</span>: Validation within finite interface radius ℓ</div>
          <div>2. <span className="text-purple-300">Isotropy</span>: No preferred spatial direction</div>
          <div>3. <span className="text-green-300">Conservation</span>: Total probability preserved</div>
          <div>4. <span className="text-yellow-300">Smoothness</span>: Continuous evolution in limit</div>
        </div>
      </div>

      <div className="bg-slate-800 p-4 rounded">
        <h4 className="font-bold mb-2">Then the ONLY possible continuous evolution is:</h4>
        <div className="text-center text-2xl font-mono my-4 text-purple-400">
          iℏ ∂ψ/∂t = -(ℏ²/2m)∇²ψ + V(x)ψ
        </div>
        <div className="text-sm text-slate-300">
          <div className="mb-2">Where:</div>
          <div>• ℏ = interface validation rate (Planck's constant)</div>
          <div>• m = operator resistance to change (mass)</div>
          <div>• V(x) = external boundary field (potential)</div>
        </div>
      </div>

      <div className="mt-4 bg-blue-900 p-4 rounded">
        <div className="font-bold mb-2">Proven mathematically in Layer 6</div>
        <div className="text-sm">Numerical validation: O(Δx²) convergence confirmed</div>
      </div>
    </div>
  </div>
);

const DimensionalSection = () => (
  <div className="space-y-8">
    <div className="bg-slate-900 rounded-lg p-6 border-2 border-yellow-500">
      <h2 className="text-2xl font-bold mb-4">States and Gates: The Complete Cascade</h2>
      <div className="text-center mb-6 p-4 bg-gradient-to-r from-purple-900 to-blue-900 rounded">
        <div className="text-lg font-bold mb-2">Integer Dimensions = STATES (Being)</div>
        <div className="text-lg font-bold">Half Dimensions = GATES (Becoming)</div>
      </div>
      
      <div className="space-y-4">
        {/* 0D STATE */}
        <div className="bg-gradient-to-r from-purple-900 to-slate-900 p-4 rounded border-2 border-purple-400">
          <div className="flex items-center gap-4 mb-2">
            <div className="text-3xl font-bold">0D</div>
            <div className="text-xl">STATE: Pure Infinity (∞)</div>
          </div>
          <div className="text-sm space-y-1 ml-16">
            <div>• Point of infinite potential - BEING</div>
            <div>• Symmetric, no direction, timeless</div>
            <div>• All possibilities exist</div>
            <div className="font-mono text-purple-300">Hilbert space: ℋ = ∫|ψ⟩⟨ψ|dψ</div>
          </div>
        </div>

        <div className="flex justify-center">
          <ArrowRight className="text-yellow-400" size={32} />
        </div>

        {/* 0.5D GATE */}
        <div className="bg-gradient-to-r from-blue-900 to-slate-900 p-4 rounded border-2 border-blue-400">
          <div className="flex items-center gap-4 mb-2">
            <div className="text-3xl font-bold">[0.5D]</div>
            <div className="text-xl">GATE: Time Creation Validator</div>
          </div>
          <div className="text-sm space-y-1 ml-16">
            <div>• BECOMING: Validates ∞ → 1D transition</div>
            <div>• Asymmetric aperture: ∇ ≠ ℰ breaks time symmetry</div>
            <div>• [ICE] test: "Can sequence exist?"</div>
            <div>• Creates time's arrow</div>
            <div className="font-mono text-blue-300">â = ∇̂ + Ê (∇ ≠ ℰ)</div>
          </div>
          <div className="mt-2 p-2 bg-blue-800 rounded text-xs">
            <span className="font-bold">KEY:</span> This asymmetry is why time flows forward!
          </div>
        </div>

        <div className="flex justify-center">
          <ArrowRight className="text-yellow-400" size={32} />
        </div>

        {/* 1D STATE */}
        <div className="bg-gradient-to-r from-green-900 to-slate-900 p-4 rounded border-2 border-green-400">
          <div className="flex items-center gap-4 mb-2">
            <div className="text-3xl font-bold">1D</div>
            <div className="text-xl">STATE: Linear Flow (Time)</div>
          </div>
          <div className="text-sm space-y-1 ml-16">
            <div>• Temporal sequence - BEING</div>
            <div>• Causality becomes possible</div>
            <div>• Sequential past → present → future</div>
            <div className="font-mono text-green-300">t: validated temporal flow</div>
          </div>
        </div>

        <div className="flex justify-center">
          <ArrowRight className="text-yellow-400" size={32} />
        </div>

        {/* 1.5D GATE - CONSCIOUSNESS */}
        <div className="bg-gradient-to-r from-yellow-900 to-slate-900 p-4 rounded border-4 border-yellow-400 shadow-2xl shadow-yellow-500/50">
          <div className="flex items-center gap-4 mb-2">
            <div className="text-3xl font-bold text-yellow-300">[1.5D]</div>
            <div className="text-xl text-yellow-100">GATE: CONSCIOUSNESS VALIDATOR ⭐</div>
          </div>
          <div className="text-sm space-y-1 ml-16">
            <div className="font-bold text-yellow-200">• BECOMING: Validates 1D → 2D transition</div>
            <div>• [ICE] test: "Which branch?" at β ≈ 0.5</div>
            <div>• Creates validated 90° deflections</div>
            <div>• Fractal dimension D ≈ 1.5</div>
            <div className="font-mono text-yellow-300 font-bold">D = 1.503 ± 0.040 (EMPIRICALLY MEASURED!)</div>
          </div>
          <div className="mt-2 p-2 bg-yellow-800/60 rounded text-xs border border-yellow-400/40">
            <div className="font-bold mb-1 text-yellow-200">YOU ARE HERE!</div>
            <div>• LIGO: D = 1.503 ± 0.040, p = 0.951</div>
            <div>• This is consciousness operating at the gate</div>
            <div>• You ARE the validation process itself</div>
          </div>
        </div>

        <div className="flex justify-center">
          <ArrowRight className="text-yellow-400" size={32} />
        </div>

        {/* 2D STATE */}
        <div className="bg-gradient-to-r from-red-900 to-slate-900 p-4 rounded border-2 border-red-400">
          <div className="flex items-center gap-4 mb-2">
            <div className="text-3xl font-bold">2D</div>
            <div className="text-xl">STATE: Pattern (Geometric Surface)</div>
          </div>
          <div className="text-sm space-y-1 ml-16">
            <div>• Branched structures - BEING</div>
            <div>• Tree of Life forms manifest</div>
            <div>• Sacred geometry appears</div>
            <div className="font-mono text-red-300">Validated choices create surfaces</div>
          </div>
        </div>

        <div className="flex justify-center">
          <ArrowRight className="text-yellow-400" size={32} />
        </div>

        {/* 2.5D GATE */}
        <div className="bg-gradient-to-r from-orange-900 to-slate-900 p-4 rounded border-2 border-orange-400">
          <div className="flex items-center gap-4 mb-2">
            <div className="text-3xl font-bold">[2.5D]</div>
            <div className="text-xl">GATE: Integration Validator</div>
          </div>
          <div className="text-sm space-y-1 ml-16">
            <div>• BECOMING: Validates 2D → 3D transition</div>
            <div>• [ICE] test: "Can surfaces coordinate?"</div>
            <div>• Creates unified volume from patterns</div>
            <div className="font-mono text-orange-300">Integration: 2D → 3D</div>
          </div>
        </div>

        <div className="flex justify-center">
          <ArrowRight className="text-yellow-400" size={32} />
        </div>

        {/* 3D STATE */}
        <div className="bg-gradient-to-r from-purple-900 to-slate-900 p-4 rounded border-2 border-purple-400">
          <div className="flex items-center gap-4 mb-2">
            <div className="text-3xl font-bold">3D</div>
            <div className="text-xl">STATE: Volume (Spatial Experience)</div>
          </div>
          <div className="text-sm space-y-1 ml-16">
            <div>• Integrated wholeness - BEING</div>
            <div>• Full spatial experience</div>
            <div>• Unified reality</div>
            <div className="font-mono text-purple-300">β ≈ 0.5: balanced gates create space</div>
          </div>
        </div>
      </div>
    </div>

    {/* CONTINUATION BEYOND 3D */}
    <div className="bg-slate-900 rounded-lg p-6 border-2 border-cyan-500">
      <h2 className="text-2xl font-bold mb-4">Beyond 3D: The Pattern Continues</h2>
      
      <div className="grid grid-cols-2 gap-6">
        {/* Fractal Nesting */}
        <div className="bg-gradient-to-br from-cyan-900 to-slate-900 p-6 rounded-lg border-2 border-cyan-400">
          <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
            <GitBranch className="text-cyan-400" />
            1. Fractal Nesting (Recursion)
          </h3>
          <div className="space-y-3 text-sm">
            <div className="font-bold text-cyan-300">Same architecture, all scales:</div>
            <div className="space-y-2 ml-4">
              <div>• Quantum gates → Atomic gates</div>
              <div>• Molecular gates → Cellular gates</div>
              <div>• Organismal gates → Social gates</div>
              <div>• Planetary gates → Cosmic gates</div>
            </div>
            <div className="mt-4 p-3 bg-cyan-800 rounded">
              <div className="font-bold mb-2">Infinite nesting:</div>
              <div className="font-mono text-xs">
                You (1.5D gate)
                <br/>├─ Cells (1.5D gates)
                <br/>│  ├─ Molecules (1.5D gates)
                <br/>│  │  ├─ Atoms (1.5D gates)
                <br/>│  │  │  └─ Particles (1.5D gates)
                <br/>│  │  │      └─ ...infinitely nested
              </div>
            </div>
            <div className="mt-3 font-bold text-yellow-300">
              One pattern, infinite scales, nested forever
            </div>
          </div>
        </div>

        {/* Feedback Loop */}
        <div className="bg-gradient-to-br from-purple-900 to-slate-900 p-6 rounded-lg border-2 border-purple-400">
          <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Zap className="text-purple-400" />
            2. Feedback Loop (∞' → ∞)
          </h3>
          <div className="space-y-3 text-sm">
            <div className="font-bold text-purple-300">Manifested reality feeds back:</div>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="text-lg">∞</div>
                <ArrowRight size={16} />
                <div className="text-lg">•'</div>
                <ArrowRight size={16} />
                <div className="text-lg">∞'</div>
              </div>
              <div className="ml-4 text-slate-300">↓</div>
              <div className="bg-slate-800 p-2 rounded ml-4">
                ∞' creates texture (T_μν)
              </div>
              <div className="ml-4 text-slate-300">↓</div>
              <div className="bg-slate-800 p-2 rounded ml-4">
                Texture curves spacetime (g_μν)
              </div>
              <div className="ml-4 text-slate-300">↓</div>
              <div className="bg-slate-800 p-2 rounded ml-4">
                Spacetime affects validation rates
              </div>
              <div className="ml-4 text-slate-300">↓</div>
              <div className="bg-purple-800 p-2 rounded ml-4 font-bold">
                LOOPS BACK TO AFFECT FUTURE ∞
              </div>
            </div>
            <div className="mt-3 font-bold text-yellow-300">
              Self-referential backreaction: Reality creates conditions for future reality
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 bg-gradient-to-r from-cyan-900 to-purple-900 p-6 rounded-lg border-2 border-yellow-400">
        <h3 className="text-xl font-bold mb-3 text-center">The Pattern Completes and Returns</h3>
        <div className="text-center space-y-2">
          <div className="text-lg">After 3D (unified volume/experience)</div>
          <div className="text-2xl font-bold text-yellow-300">↓</div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="bg-slate-800 p-3 rounded">
              <div className="font-bold mb-1">Fractal Recursion:</div>
              <div>Pattern repeats at all scales infinitely nested</div>
            </div>
            <div className="bg-slate-800 p-3 rounded">
              <div className="font-bold mb-1">Causal Feedback:</div>
              <div>Manifested patterns affect future possibility space</div>
            </div>
          </div>
          <div className="text-2xl font-bold text-yellow-300 mt-4">↓</div>
          <div className="text-lg font-bold">∞ ↔ • ↔ ∞'</div>
          <div className="text-slate-300 text-sm">Eternal circulation: Being ↔ Becoming</div>
        </div>
      </div>
    </div>

    <div className="bg-slate-900 rounded-lg p-6">
      <h3 className="text-xl font-bold mb-4">The Critical 1.5D Branching</h3>
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-slate-800 p-4 rounded">
          <h4 className="font-bold text-red-400 mb-2">D = 1 (Pure Determinism)</h4>
          <div className="text-sm space-y-1">
            <div>• No branches, smooth line</div>
            <div>• No choices, purely mechanical</div>
            <div>• β = 0 or β = 1 (unbalanced)</div>
          </div>
        </div>
        <div className="bg-slate-800 p-4 rounded">
          <h4 className="font-bold text-red-400 mb-2">D = 2 (Pure Chaos)</h4>
          <div className="text-sm space-y-1">
            <div>• Too many branches</div>
            <div>• No coherence, randomness</div>
            <div>• No structure persists</div>
          </div>
        </div>
      </div>
      <div className="mt-4 bg-green-900 p-4 rounded">
        <h4 className="font-bold text-green-300 mb-2">D ≈ 1.5 (CONSCIOUSNESS!) ⭐</h4>
        <div className="text-sm space-y-2">
          <div>• Validated branching at β ≈ 0.5</div>
          <div>• Constrained by physics (not pure freedom)</div>
          <div>• Not predetermined (genuine branches)</div>
          <div>• Optimal adaptive complexity</div>
          <div className="mt-2 font-bold text-yellow-300">
            Consciousness exists precisely at the dimension where validated choice becomes geometrically possible
          </div>
        </div>
      </div>
    </div>
  </div>
);

const EmpiricalSection = () => (
  <div className="space-y-8">
    <div className="bg-slate-900 rounded-lg p-6 border-2 border-green-500 shadow-lg shadow-green-500/20">
      <h2 className="text-2xl font-bold mb-4">Empirical Validation: D ≈ 1.5</h2>
      
      <div className="grid grid-cols-2 gap-6 mb-6">
        <div className="bg-gradient-to-br from-green-900 to-slate-900 p-6 rounded-lg border-2 border-green-400">
          <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
            <span>✅</span> LIGO Gravitational Waves
          </h3>
          <div className="space-y-3 text-sm">
            <div>
              <div className="font-bold text-green-300">Dataset:</div>
              <div>19 merger events, 40 observations</div>
              <div>O1/O3/O4 observing runs</div>
            </div>
            <div className="bg-slate-800 p-3 rounded">
              <div className="font-bold text-yellow-300 mb-1">Results:</div>
              <div className="font-mono">Mean D = 1.503 ± 0.040</div>
              <div className="font-mono">SEM = 0.040</div>
              <div className="font-mono">p-value = 0.951</div>
            </div>
            <div>
              <div className="font-bold text-purple-300">Interpretation:</div>
              <div>Worldlines show fractal dimension extremely consistent with 1.5D prediction</div>
            </div>
            <div className="bg-green-800 p-2 rounded">
              <div className="font-bold">High p-value → Not coincidental, it's structural!</div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-900 to-slate-900 p-6 rounded-lg border-2 border-blue-400">
          <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
            <span>✅</span> Bubble Chamber Particles
          </h3>
          <div className="space-y-3 text-sm">
            <div>
              <div className="font-bold text-blue-300">Dataset:</div>
              <div>33 particle tracks</div>
              <div>MeV-GeV energy range</div>
            </div>
            <div className="bg-slate-800 p-3 rounded">
              <div className="font-bold text-yellow-300 mb-1">Results:</div>
              <div className="font-mono">Mean D = 1.387 ± 0.232</div>
              <div className="font-mono">Energy correlation: r = -0.65</div>
            </div>
            <div>
              <div className="font-bold text-purple-300">Interpretation:</div>
              <div>Validates D ≈ 1.5 across 6+ orders of magnitude in energy</div>
            </div>
            <div className="bg-blue-800 p-2 rounded">
              <div className="font-bold">Lower-energy particles show slight suppression (predicted!)</div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-r from-purple-900 to-slate-900 p-6 rounded-lg border-2 border-purple-400">
        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
          <span>✅</span> Metric Coupling Validation
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="font-bold text-purple-300 mb-2">Prediction:</div>
            <div className="text-sm mb-3">Validation rate scales with metric:</div>
            <div className="font-mono text-center text-lg bg-slate-800 p-2 rounded">
              Texture ∝ √|g_tt|
            </div>
          </div>
          <div>
            <div className="font-bold text-green-300 mb-2">Results:</div>
            <div className="text-sm mb-3">Four spacetime geometries tested:</div>
            <div className="space-y-1 text-sm">
              <div>• Flat (Minkowski): g_tt = -1.0</div>
              <div>• Weak field: g_tt ≈ -(1 + 2Φ/c²)</div>
              <div>• Neutron star: g_tt = -(1 - 2GM/rc²)</div>
              <div>• Near horizon: extreme curvature</div>
            </div>
          </div>
        </div>
        <div className="mt-4 bg-purple-800 p-4 rounded">
          <div className="text-center text-2xl font-bold mb-2">R² = 0.9997</div>
          <div className="text-center text-sm">Near-perfect correlation!</div>
          <div className="text-center text-xs text-slate-300 mt-2">
            Black hole horizons suppress fractalization by 77.6%, approaching D → 1 (smooth null curves)
          </div>
        </div>
      </div>
    </div>

    <div className="bg-slate-900 rounded-lg p-6">
      <h3 className="text-xl font-bold mb-4">Complete Validation Summary</h3>
      <div className="space-y-3">
        <div className="flex items-start gap-3">
          <div className="text-2xl">✅</div>
          <div>
            <div className="font-bold">Metric coupling validated</div>
            <div className="text-sm text-slate-300">Texture accumulation scales as √|g_tt| with R² = 0.9997</div>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <div className="text-2xl">✅</div>
          <div>
            <div className="font-bold">Self-consistent backreaction</div>
            <div className="text-sm text-slate-300">3D simulations show texture stress-energy creates emergent cosmological constant WITHOUT fine-tuning</div>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <div className="text-2xl">✅</div>
          <div>
            <div className="font-bold">Quantum uncertainty reproduced</div>
            <div className="text-sm text-slate-300">Stochastic [ICE] validation noise yields hydrogen spectra with &lt;0.4% error</div>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <div className="text-2xl">✅</div>
          <div>
            <div className="font-bold">Fractal geometry confirmed</div>
            <div className="text-sm text-slate-300">Extended path simulations demonstrate texture accumulation and multi-scale structure</div>
          </div>
        </div>
      </div>

      <div className="mt-6 bg-gradient-to-r from-green-900 to-blue-900 p-6 rounded-lg border-2 border-yellow-400 shadow-2xl shadow-yellow-400/30">
        <div className="text-center text-2xl font-bold mb-4 text-yellow-100">
          This is not philosophy. This is falsifiable, testable, validated physics.
        </div>
        <div className="text-center text-lg text-yellow-300 font-semibold">
          Complete unification: QM + GR from single principle (validation at interfaces)
        </div>
      </div>
    </div>

    <div className="bg-slate-900 rounded-lg p-6 border-2 border-blue-500/30">
      <h3 className="text-xl font-bold mb-4 text-blue-300">GitHub Repository</h3>
      <div className="bg-slate-800 p-4 rounded border border-blue-500/20 hover:border-blue-500/50 transition-all">
        <div className="font-mono text-sm mb-2">
          <a href="https://github.com/AshmanRoonz/Fractal_Reality" 
             className="text-blue-400 hover:text-blue-300 hover:underline transition-colors flex items-center gap-2"
             target="_blank" 
             rel="noopener noreferrer">
            📂 github.com/AshmanRoonz/Fractal_Reality
          </a>
        </div>
        <div className="text-sm space-y-1 text-slate-300">
          <div>• Complete 12-layer framework documentation</div>
          <div>• All simulation code (open source)</div>
          <div>• Validation data and analysis</div>
          <div>• Three papers ready for submission</div>
        </div>
      </div>
    </div>
  </div>
);

export default FractalRealityDiagram;
