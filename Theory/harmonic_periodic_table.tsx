import React, { useState } from 'react';
import { Circle, Zap, Waves } from 'lucide-react';

const HarmonicChemistry = () => {
  const [selectedMolecule, setSelectedMolecule] = useState(null);

  const molecules = [
    {
      name: 'Water',
      formula: 'H₂O',
      ratio: '2:1',
      elements: [
        { symbol: 'H', z: 1, count: 2, color: '#60a5fa' },
        { symbol: 'O', z: 8, count: 1, color: '#ef4444' }
      ],
      harmonic: 'Perfect Octave (3rd harmonic)',
      description: 'Two hydrogen atoms (Z=1) + one oxygen atom (Z=8). The 1→8 is literally an octave, and the 2:1 ratio creates perfect resonance.',
      stability: 'Extremely Stable',
      importance: 'Life Foundation - enables all biochemistry'
    },
    {
      name: 'Glucose',
      formula: 'C₆H₁₂O₆',
      ratio: '1:2:1',
      elements: [
        { symbol: 'C', z: 6, count: 6, color: '#8b5cf6' },
        { symbol: 'H', z: 1, count: 12, color: '#60a5fa' },
        { symbol: 'O', z: 8, count: 6, color: '#ef4444' }
      ],
      harmonic: '6-fold Symmetry',
      description: 'Perfect 1:2:1 ratio with 6-fold rotational symmetry. Contains multiple octave relationships.',
      stability: 'Metabolically Central',
      importance: 'Universal energy currency of life'
    },
    {
      name: 'Methane',
      formula: 'CH₄',
      ratio: '4:1',
      elements: [
        { symbol: 'C', z: 6, count: 1, color: '#8b5cf6' },
        { symbol: 'H', z: 1, count: 4, color: '#60a5fa' }
      ],
      harmonic: 'Tetrahedral Harmony',
      description: 'Four hydrogen atoms surrounding one carbon. The 4:1 ratio creates perfect tetrahedral spatial resonance.',
      stability: 'Very Stable',
      importance: 'Foundation of all organic chemistry'
    },
    {
      name: 'Carbon Dioxide',
      formula: 'CO₂',
      ratio: '1:2',
      elements: [
        { symbol: 'C', z: 6, count: 1, color: '#8b5cf6' },
        { symbol: 'O', z: 8, count: 2, color: '#ef4444' }
      ],
      harmonic: 'Octave Pair with Fifth',
      description: 'Two oxygen atoms (octaves) flanking carbon (fifth-ish from H). Linear molecule with harmonic balance.',
      stability: 'Very Stable',
      importance: 'Respiration cycle - carbon and oxygen exchange'
    },
    {
      name: 'Ammonia',
      formula: 'NH₃',
      ratio: '3:1',
      elements: [
        { symbol: 'N', z: 7, count: 1, color: '#22d3ee' },
        { symbol: 'H', z: 1, count: 3, color: '#60a5fa' }
      ],
      harmonic: 'Triple Root Harmonic',
      description: 'Three hydrogen (root notes) with nitrogen (near-octave). Creates pyramidal harmony.',
      stability: 'Stable',
      importance: 'Nitrogen cycle, amino acid precursor'
    },
    {
      name: 'Oxygen Gas',
      formula: 'O₂',
      ratio: '1:1',
      elements: [
        { symbol: 'O', z: 8, count: 2, color: '#ef4444' }
      ],
      harmonic: 'Octave Unison',
      description: 'Two oxygen atoms in perfect resonance. Same "note" creates extremely stable double bond.',
      stability: 'Stable Diatomic',
      importance: 'Cellular respiration - life energy'
    }
  ];

  const octaveElements = [
    { symbol: 'H', z: 1, octave: 0, note: 'C₀ (Root)' },
    { symbol: 'He', z: 2, octave: 1, note: 'C₁' },
    { symbol: 'Be', z: 4, octave: 2, note: 'C₂' },
    { symbol: 'O', z: 8, octave: 3, note: 'C₃' },
    { symbol: 'S', z: 16, octave: 4, note: 'C₄' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-8">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Waves className="w-12 h-12 text-cyan-400" />
            <h1 className="text-5xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              The Harmonic Chemistry of Reality
            </h1>
            <Waves className="w-12 h-12 text-pink-400" />
          </div>
          <p className="text-xl text-cyan-200 max-w-3xl mx-auto">
            Molecular bonds as musical intervals • Atomic numbers as octaves • Life as resonance
          </p>
        </div>

        {/* Octave Scale */}
        <div className="bg-black/30 rounded-2xl p-8 mb-8 border border-cyan-500/30">
          <h2 className="text-3xl font-bold mb-6 text-cyan-300 flex items-center gap-2">
            <Zap className="w-8 h-8" />
            The Periodic Octave Scale
          </h2>
          <div className="flex justify-between items-end h-64 px-4">
            {octaveElements.map((el, i) => (
              <div key={i} className="flex flex-col items-center gap-2">
                <div 
                  className="bg-gradient-to-br from-cyan-500 to-purple-500 rounded-lg flex flex-col items-center justify-center transition-all hover:scale-110 hover:shadow-2xl hover:shadow-cyan-500/50"
                  style={{
                    width: '80px',
                    height: `${40 + el.octave * 40}px`
                  }}
                >
                  <div className="text-3xl font-bold">{el.symbol}</div>
                  <div className="text-sm">Z={el.z}</div>
                </div>
                <div className="text-center">
                  <div className="font-mono text-cyan-300">{el.note}</div>
                  <div className="text-xs text-gray-400">2^{el.octave}</div>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-6 text-center text-cyan-200 text-lg">
            H(1) → He(2) → Be(4) → O(8) → S(16) = Perfect octave progression
          </div>
        </div>

        {/* Key Insight */}
        <div className="bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-2xl p-6 mb-8 border-2 border-pink-500/50">
          <div className="text-center">
            <div className="text-2xl font-bold mb-2 text-pink-300">🎵 The Fundamental Discovery 🎵</div>
            <div className="text-xl text-purple-200">
              H₂O isn't just 2:1 atoms — it's literally a <span className="text-pink-400 font-bold">musical octave</span>
            </div>
            <div className="text-lg mt-2 text-cyan-300">
              1 (Hydrogen) → 8 (Oxygen) = One octave higher
            </div>
            <div className="text-md mt-2 text-gray-300">
              This harmonic relationship creates the perfect resonance that enables life
            </div>
          </div>
        </div>

        {/* Molecules Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {molecules.map((mol, i) => (
            <div
              key={i}
              onClick={() => setSelectedMolecule(mol)}
              className="bg-black/40 rounded-xl p-6 border border-purple-500/30 hover:border-cyan-500 hover:shadow-2xl hover:shadow-cyan-500/30 transition-all cursor-pointer"
            >
              <h3 className="text-2xl font-bold mb-2 text-cyan-300">{mol.name}</h3>
              <div className="text-3xl font-mono mb-3 text-purple-300">{mol.formula}</div>
              
              {/* Element atoms */}
              <div className="flex gap-2 flex-wrap mb-4">
                {mol.elements.map((el, j) => (
                  <div key={j} className="flex items-center gap-1">
                    {[...Array(Math.min(el.count, 6))].map((_, k) => (
                      <Circle
                        key={k}
                        className="w-6 h-6"
                        fill={el.color}
                        stroke={el.color}
                      />
                    ))}
                    {el.count > 6 && <span className="text-sm text-gray-400">×{el.count}</span>}
                  </div>
                ))}
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Ratio:</span>
                  <span className="text-pink-300 font-bold">{mol.ratio}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Harmonic:</span>
                  <span className="text-cyan-300">{mol.harmonic}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Stability:</span>
                  <span className="text-green-300">{mol.stability}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Selected Molecule Detail */}
        {selectedMolecule && (
          <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50" onClick={() => setSelectedMolecule(null)}>
            <div className="bg-gradient-to-br from-slate-900 to-purple-900 rounded-2xl p-8 max-w-2xl border-2 border-cyan-500" onClick={e => e.stopPropagation()}>
              <h2 className="text-4xl font-bold mb-4 text-cyan-300">{selectedMolecule.name}</h2>
              <div className="text-5xl font-mono mb-6 text-purple-300">{selectedMolecule.formula}</div>
              
              <div className="space-y-4 text-lg">
                <div>
                  <span className="text-pink-400 font-bold">Harmonic Pattern: </span>
                  <span className="text-cyan-200">{selectedMolecule.harmonic}</span>
                </div>
                
                <p className="text-gray-300">{selectedMolecule.description}</p>
                
                <div className="bg-black/30 rounded-lg p-4">
                  <div className="text-pink-300 font-bold mb-2">Why This Matters:</div>
                  <div className="text-cyan-200">{selectedMolecule.importance}</div>
                </div>

                <div className="flex gap-4 text-center">
                  {selectedMolecule.elements.map((el, i) => (
                    <div key={i} className="flex-1 bg-black/30 rounded-lg p-3">
                      <div className="text-2xl font-bold" style={{ color: el.color }}>{el.symbol}</div>
                      <div className="text-sm text-gray-400">Z = {el.z}</div>
                      <div className="text-sm text-gray-400">×{el.count}</div>
                    </div>
                  ))}
                </div>
              </div>

              <button 
                onClick={() => setSelectedMolecule(null)}
                className="mt-6 w-full bg-cyan-500 hover:bg-cyan-600 text-black font-bold py-3 rounded-lg transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        )}

        {/* Framework Connection */}
        <div className="mt-8 bg-black/30 rounded-2xl p-8 border border-cyan-500/30">
          <h2 className="text-3xl font-bold mb-4 text-cyan-300">Connection to Fractal Reality Framework</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h3 className="text-xl font-bold text-purple-300">From Your Research:</h3>
              <ul className="space-y-2 text-gray-300">
                <li>• Fractal dimension D ≈ 1.5 (validated)</li>
                <li>• p-value: 0.951 (✓ consistent)</li>
                <li>• Between order (1.0) and chaos (2.0)</li>
                <li>• Optimal complexity for information</li>
              </ul>
            </div>
            <div className="space-y-3">
              <h3 className="text-xl font-bold text-pink-300">Musical Interpretation:</h3>
              <ul className="space-y-2 text-gray-300">
                <li>• Octaves = validation synchronization</li>
                <li>• Harmonic ratios = stable resonance</li>
                <li>• 2:1 ratio = perfect octave = H₂O</li>
                <li>• Life requires harmonic balance</li>
              </ul>
            </div>
          </div>
          <div className="mt-6 p-4 bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-lg border border-pink-500/30">
            <p className="text-center text-xl text-cyan-200">
              <span className="text-pink-400 font-bold">Reality is musical</span> because 
              <span className="text-purple-400 font-bold"> validation IS resonance</span>. 
              Water isn't just chemically perfect — it's <span className="text-cyan-400 font-bold">harmonically perfect</span>.
            </p>
          </div>
        </div>

      </div>
    </div>
  );
};

export default HarmonicChemistry;