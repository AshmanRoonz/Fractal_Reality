import React, { useState } from 'react';

const App = () => {
  const [selectedState, setSelectedState] = useState(null);
  const [hoveredState, setHoveredState] = useState(null);

  // Define particles and their states
  const particles = {
    7: { name: 'Photon (γ)', mass: '0', type: 'boson', color: '#fbbf24', desc: 'Massless EM mediator' },
    11: { name: 'Gluons (g×8)', mass: '0*', type: 'boson', color: '#ef4444', desc: 'Color force mediators' },
    15: { name: 'W±, Z', mass: '80-91 GeV', type: 'boson', color: '#8b5cf6', desc: 'Weak force mediators' },
    31: { name: 'Higgs (H⁰)', mass: '125 GeV', type: 'boson', color: '#ec4899', desc: 'Mass-giving field' },
    43: { name: 'Quarks', mass: '2MeV-173GeV', type: 'fermion', color: '#10b981', desc: 'u,d,s,c,b,t (×3 colors)' },
    44: { name: 'Quarks', mass: '2MeV-173GeV', type: 'fermion', color: '#10b981', desc: 'u,d,s,c,b,t (×3 colors)' },
    45: { name: 'Quarks', mass: '2MeV-173GeV', type: 'fermion', color: '#10b981', desc: 'u,d,s,c,b,t (×3 colors)' },
    46: { name: 'Quarks', mass: '2MeV-173GeV', type: 'fermion', color: '#10b981', desc: 'u,d,s,c,b,t (×3 colors)' },
    47: { name: 'Quarks', mass: '2MeV-173GeV', type: 'fermion', color: '#10b981', desc: 'u,d,s,c,b,t (×3 colors)' },
    54: { name: 'Leptons', mass: '0.5-1777 MeV', type: 'fermion', color: '#3b82f6', desc: 'e, μ, τ' },
    55: { name: 'Leptons', mass: '0.5-1777 MeV', type: 'fermion', color: '#3b82f6', desc: 'e, μ, τ' },
    56: { name: 'Neutrinos', mass: '<1 eV', type: 'fermion', color: '#6366f1', desc: 'νₑ, νμ, ντ' },
    63: { name: 'Stable States', mass: 'Various', type: 'fermion', color: '#14b8a6', desc: 'Maximum validation' }
  };

  const getStateLabel = (state) => {
    const input = Math.floor(state / 8);
    const output = state % 8;
    return `${input.toString(2).padStart(3, '0')}|${output.toString(2).padStart(3, '0')}`;
  };

  const getStateColor = (state) => {
    if (particles[state]) return particles[state].color;
    if (state >= 40 && state <= 42) return '#64748b'; // Dark matter candidates
    if (state >= 57 && state <= 62) return '#71717a'; // Exotic states
    return '#1e293b'; // Empty/virtual
  };

  const getStateOpacity = (state) => {
    if (particles[state]) return 1;
    if (state >= 40 && state <= 42) return 0.6; // Dark matter
    if (state >= 57 && state <= 62) return 0.4; // Exotic
    return 0.15; // Virtual
  };

  const displayState = hoveredState !== null ? hoveredState : selectedState;

  return (
    <div className="w-full h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-8 text-white overflow-auto">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-6">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
            The 64-State Validation Matrix
          </h1>
          <p className="text-lg text-cyan-300 mb-1">Standard Model Particles from Dual-Interface Geometry</p>
          <p className="text-xs text-purple-300">8πG/c⁴ × 2 interfaces = 64 complete states</p>
        </div>

        {/* Main Matrix */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 mb-4 border border-cyan-500/30 max-w-2xl mx-auto">
          <div className="flex items-start gap-2">
            {/* Output label */}
            <div className="flex flex-col items-center pt-6">
              <div className="transform -rotate-90 origin-center whitespace-nowrap text-xs font-mono text-cyan-400 mb-2">
                OUTPUT (I,C,E)
              </div>
            </div>

            {/* Matrix grid */}
            <div className="flex-1">
              <div className="text-center text-xs font-mono text-purple-400 mb-1">
                INPUT (I,C,E) →
              </div>
              <div className="grid grid-cols-8 gap-0.5">
                {Array.from({ length: 64 }, (_, i) => (
                  <div
                    key={i}
                    className="relative aspect-square cursor-pointer transition-all duration-200 rounded border"
                    style={{
                      backgroundColor: getStateColor(i),
                      opacity: getStateOpacity(i),
                      borderColor: particles[i] ? getStateColor(i) : '#334155',
                      transform: hoveredState === i ? 'scale(1.1)' : 'scale(1)',
                      boxShadow: hoveredState === i ? `0 0 20px ${getStateColor(i)}` : 'none',
                      zIndex: hoveredState === i ? 10 : 1
                    }}
                    onMouseEnter={() => setHoveredState(i)}
                    onMouseLeave={() => setHoveredState(null)}
                    onClick={() => setSelectedState(i === selectedState ? null : i)}
                  >
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-[9px] font-mono font-bold" style={{
                        color: particles[i] ? '#fff' : '#64748b',
                        textShadow: particles[i] ? '0 0 4px rgba(0,0,0,0.8)' : 'none'
                      }}>
                        {i}
                      </span>
                    </div>
                    {particles[i] && (
                      <div className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-white animate-pulse" />
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Axis labels */}
          <div className="grid grid-cols-8 gap-0.5 mt-1 ml-6">
            {['000', '001', '010', '011', '100', '101', '110', '111'].map((label, i) => (
              <div key={i} className="text-center text-[10px] font-mono text-cyan-400">
                {label}
              </div>
            ))}
          </div>
        </div>

        {/* Info Panel */}
        {displayState !== null && (
          <div className="bg-slate-800/70 backdrop-blur-sm rounded-xl p-6 border border-purple-500/30 animate-fadeIn">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-2xl font-bold mb-4 text-cyan-400">
                  State {displayState}: {getStateLabel(displayState)}
                </h3>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <span className="text-purple-400 font-mono">Input:</span>
                    <span className="font-mono">{Math.floor(displayState / 8).toString(2).padStart(3, '0')}</span>
                    <span className="text-slate-400">
                      ({Math.floor(displayState / 8) & 4 ? 'I' : ''}
                      {Math.floor(displayState / 8) & 2 ? 'C' : ''}
                      {Math.floor(displayState / 8) & 1 ? 'E' : ''} pass)
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-cyan-400 font-mono">Output:</span>
                    <span className="font-mono">{(displayState % 8).toString(2).padStart(3, '0')}</span>
                    <span className="text-slate-400">
                      ({displayState & 4 ? 'I' : ''}
                      {displayState & 2 ? 'C' : ''}
                      {displayState & 1 ? 'E' : ''} pass)
                    </span>
                  </div>
                </div>
              </div>

              <div>
                {particles[displayState] ? (
                  <div className="space-y-2">
                    <h4 className="text-xl font-bold" style={{ color: particles[displayState].color }}>
                      {particles[displayState].name}
                    </h4>
                    <div className="space-y-1 text-sm">
                      <div><span className="text-slate-400">Type:</span> {particles[displayState].type}</div>
                      <div><span className="text-slate-400">Mass:</span> {particles[displayState].mass}</div>
                      <div className="text-slate-300">{particles[displayState].desc}</div>
                    </div>
                  </div>
                ) : displayState >= 40 && displayState <= 42 ? (
                  <div className="text-yellow-400">
                    <h4 className="text-xl font-bold mb-2">Dark Matter Candidate?</h4>
                    <p className="text-sm">Predicted: Validation-only particle with no EM/weak coupling</p>
                  </div>
                ) : displayState >= 57 && displayState <= 62 ? (
                  <div className="text-orange-400">
                    <h4 className="text-xl font-bold mb-2">Exotic State</h4>
                    <p className="text-sm">Near-threshold configuration (pentaquarks, tetraquarks?)</p>
                  </div>
                ) : (
                  <div className="text-slate-400">
                    <h4 className="text-xl font-bold mb-2">Virtual State</h4>
                    <p className="text-sm">Insufficient validation - appears only as quantum fluctuation</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Legend */}
        <div className="mt-6 bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 border border-cyan-500/30">
          <h3 className="text-lg font-bold mb-3 text-cyan-400">Particle Categories</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: '#fbbf24' }} />
              <span>Photon (γ)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: '#ef4444' }} />
              <span>Gluons (g)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: '#8b5cf6' }} />
              <span>W±, Z</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: '#ec4899' }} />
              <span>Higgs (H)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: '#10b981' }} />
              <span>Quarks</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: '#3b82f6' }} />
              <span>Leptons</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: '#6366f1' }} />
              <span>Neutrinos</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-slate-600" />
              <span>Dark Matter?</span>
            </div>
          </div>
        </div>

        {/* Key Stats */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gradient-to-br from-cyan-500/20 to-purple-500/20 rounded-xl p-4 border border-cyan-500/30">
            <div className="text-3xl font-bold text-cyan-400">61</div>
            <div className="text-sm text-slate-300">Standard Model Particles</div>
          </div>
          <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-xl p-4 border border-purple-500/30">
            <div className="text-3xl font-bold text-purple-400">0</div>
            <div className="text-sm text-slate-300">Free Parameters</div>
          </div>
          <div className="bg-gradient-to-br from-pink-500/20 to-cyan-500/20 rounded-xl p-4 border border-pink-500/30">
            <div className="text-3xl font-bold text-pink-400">1.503</div>
            <div className="text-sm text-slate-300">Fractal Dimension (LIGO)</div>
          </div>
        </div>

        {/* Formula */}
        <div className="mt-6 text-center p-4 bg-slate-800/50 rounded-xl border border-cyan-500/30">
          <div className="text-sm text-slate-400 mb-2">The fundamental structure:</div>
          <div className="text-2xl font-mono text-transparent bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text">
            8πG/c⁴ × (2 interfaces) = 8² = 64 states
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
};

export default App;
