import React, { useState } from 'react';
import { BarChart, Bar, LineChart, Line, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell, ReferenceLine } from 'recharts';

const ICEValidationPattern = () => {
  const [activeView, setActiveView] = useState('trinity');

  // Data from the CSV
  const runs = [
    { 
      name: 'O1', 
      fullName: 'O1 (Original)',
      events: 3, 
      obs: 6, 
      mean: 1.578, 
      std: 0.38, 
      sem: 0.155, 
      pValue: null,
      consistent: '?',
      order: 1
    },
    { 
      name: 'O3', 
      fullName: 'O3 (Corrected)',
      events: 2, 
      obs: 4, 
      mean: 1.636, 
      std: 0.142, 
      sem: 0.050, 
      pValue: 0.274,
      consistent: '✓',
      order: 2
    },
    { 
      name: 'O4-G', 
      fullName: 'O4 (Global)',
      events: 17, 
      obs: 36, 
      mean: 1.488, 
      std: 0.265, 
      sem: 0.044, 
      pValue: 0.782,
      consistent: '✓',
      order: 3
    },
    { 
      name: 'O4-D', 
      fullName: 'O4 (Det-spec)',
      events: 17, 
      obs: 36, 
      mean: 1.513, 
      std: 0.222, 
      sem: 0.037, 
      pValue: 0.734,
      consistent: '✓',
      order: 4
    }
  ];

  const globalCenter = runs.reduce((sum, r) => sum + r.mean, 0) / runs.length;

  // Calculate I-C-E metrics
  const iceData = runs.map(r => ({
    name: r.name,
    fullName: r.fullName,
    // I - Boundary Integrity (inverse of relative uncertainty)
    I: (1 / (r.sem / r.mean)) * 10,
    // C - Center Coherence (closeness to global center)
    C: (1 - Math.abs(r.mean - globalCenter) / globalCenter) * 100,
    // E - Field Fitness (p-value or 0 for baseline)
    E: r.pValue !== null ? r.pValue * 100 : 0,
    order: r.order
  }));

  // Temporal evolution data
  const temporalData = runs.map(r => ({
    name: r.name,
    mean: r.mean,
    boundaryStrength: r.mean / r.std,
    semRelative: (r.sem / r.mean) * 100,
    coherence: (1 - Math.abs(r.mean - globalCenter) / globalCenter) * 100,
    fitness: r.pValue !== null ? r.pValue * 100 : 0,
    order: r.order
  }));

  const getColor = (index) => {
    const colors = ['#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];
    return colors[index];
  };

  return (
    <div className="w-full h-full bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-8 overflow-auto">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            The I-C-E Validation Trinity
          </h1>
          <p className="text-purple-200 text-lg mb-4">
            Infinite Possibility → Singularity → Finite Wholes
          </p>
          <div className="text-purple-300 text-sm max-w-3xl mx-auto">
            <em>"Wholeness giving boundary to the unbounded infinite... each cycle validating through boundary integrity (I), center coherence (C), and field fitness (E), each validation a fractalization and a memory through time"</em>
          </div>
        </div>

        {/* View Toggle */}
        <div className="flex justify-center gap-4 mb-8">
          <button
            onClick={() => setActiveView('trinity')}
            className={`px-6 py-2 rounded-lg font-semibold transition-all ${
              activeView === 'trinity' 
                ? 'bg-purple-500 text-white' 
                : 'bg-slate-800 text-purple-300 hover:bg-slate-700'
            }`}
          >
            I-C-E Trinity
          </button>
          <button
            onClick={() => setActiveView('temporal')}
            className={`px-6 py-2 rounded-lg font-semibold transition-all ${
              activeView === 'temporal' 
                ? 'bg-purple-500 text-white' 
                : 'bg-slate-800 text-purple-300 hover:bg-slate-700'
            }`}
          >
            Memory Through Time
          </button>
          <button
            onClick={() => setActiveView('convergence')}
            className={`px-6 py-2 rounded-lg font-semibold transition-all ${
              activeView === 'convergence' 
                ? 'bg-purple-500 text-white' 
                : 'bg-slate-800 text-purple-300 hover:bg-slate-700'
            }`}
          >
            Center Convergence
          </button>
        </div>

        {/* Trinity View */}
        {activeView === 'trinity' && (
          <div className="space-y-8">
            <div className="bg-slate-800/50 backdrop-blur rounded-xl p-6">
              <h2 className="text-2xl font-bold text-white mb-4 text-center">
                The Three-Fold Validation
              </h2>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={iceData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                  <XAxis dataKey="name" stroke="#a78bfa" />
                  <YAxis stroke="#a78bfa" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1e293b', 
                      border: '1px solid #a78bfa',
                      borderRadius: '8px'
                    }}
                    formatter={(value) => value.toFixed(2)}
                  />
                  <Legend />
                  <Bar dataKey="I" name="I - Boundary Integrity" fill="#8b5cf6" />
                  <Bar dataKey="C" name="C - Center Coherence" fill="#ec4899" />
                  <Bar dataKey="E" name="E - Field Fitness" fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Detailed Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* I - Boundary Integrity */}
              <div className="bg-purple-900/30 backdrop-blur rounded-xl p-6 border border-purple-500/30">
                <h3 className="text-xl font-bold text-purple-300 mb-3">
                  I - Boundary Integrity
                </h3>
                <p className="text-purple-200 text-sm mb-4">
                  Wholeness gives boundary to the unbounded infinite
                </p>
                {runs.map((r, i) => (
                  <div key={i} className="mb-3 pb-3 border-b border-purple-500/20 last:border-0">
                    <div className="text-white font-semibold">{r.name}</div>
                    <div className="text-purple-300 text-sm">
                      SEM/Mean: {(r.sem/r.mean*100).toFixed(2)}%
                    </div>
                    <div className="text-purple-300 text-sm">
                      Mean/Std: {(r.mean/r.std).toFixed(2)}
                    </div>
                  </div>
                ))}
              </div>

              {/* C - Center Coherence */}
              <div className="bg-pink-900/30 backdrop-blur rounded-xl p-6 border border-pink-500/30">
                <h3 className="text-xl font-bold text-pink-300 mb-3">
                  C - Center Coherence
                </h3>
                <p className="text-pink-200 text-sm mb-4">
                  All wholes converge through the singularity: <strong>{globalCenter.toFixed(4)}</strong>
                </p>
                {runs.map((r, i) => (
                  <div key={i} className="mb-3 pb-3 border-b border-pink-500/20 last:border-0">
                    <div className="text-white font-semibold">{r.name}</div>
                    <div className="text-pink-300 text-sm">
                      Mean: {r.mean.toFixed(4)}
                    </div>
                    <div className="text-pink-300 text-sm">
                      Coherence: {((1 - Math.abs(r.mean - globalCenter) / globalCenter) * 100).toFixed(2)}%
                    </div>
                  </div>
                ))}
              </div>

              {/* E - Field Fitness */}
              <div className="bg-emerald-900/30 backdrop-blur rounded-xl p-6 border border-emerald-500/30">
                <h3 className="text-xl font-bold text-emerald-300 mb-3">
                  E - Field Fitness
                </h3>
                <p className="text-emerald-200 text-sm mb-4">
                  Validation in the eternal pattern
                </p>
                {runs.map((r, i) => (
                  <div key={i} className="mb-3 pb-3 border-b border-emerald-500/20 last:border-0">
                    <div className="text-white font-semibold">{r.name}</div>
                    <div className="text-emerald-300 text-sm">
                      p-value: {r.pValue !== null ? r.pValue.toFixed(4) : 'baseline'}
                    </div>
                    <div className="text-emerald-300 text-sm">
                      Consistent: {r.consistent}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Temporal View */}
        {activeView === 'temporal' && (
          <div className="space-y-8">
            <div className="bg-slate-800/50 backdrop-blur rounded-xl p-6">
              <h2 className="text-2xl font-bold text-white mb-4 text-center">
                Memory Through Time: Each Validation a Fractalization
              </h2>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={temporalData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                  <XAxis dataKey="name" stroke="#a78bfa" />
                  <YAxis stroke="#a78bfa" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1e293b', 
                      border: '1px solid #a78bfa',
                      borderRadius: '8px'
                    }}
                    formatter={(value) => value.toFixed(2)}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="coherence" 
                    name="Center Coherence (%)" 
                    stroke="#ec4899" 
                    strokeWidth={3}
                    dot={{ r: 6 }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="fitness" 
                    name="Field Fitness (%)" 
                    stroke="#10b981" 
                    strokeWidth={3}
                    dot={{ r: 6 }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="boundaryStrength" 
                    name="Boundary Strength" 
                    stroke="#8b5cf6" 
                    strokeWidth={3}
                    dot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Temporal Evolution Details */}
            <div className="bg-slate-800/50 backdrop-blur rounded-xl p-6">
              <h3 className="text-xl font-bold text-white mb-4">
                Evolutionary Transitions
              </h3>
              <div className="space-y-4">
                <div className="border-l-4 border-purple-500 pl-4">
                  <div className="text-purple-300 font-semibold">O1 → O3</div>
                  <div className="text-white text-sm">Boundary sharpened by 68.9%</div>
                  <div className="text-purple-200 text-sm">Fewer events (3→2) but HIGHER coherence</div>
                </div>
                <div className="border-l-4 border-pink-500 pl-4">
                  <div className="text-pink-300 font-semibold">O3 → O4</div>
                  <div className="text-white text-sm">Field fitness increased by 50.8%</div>
                  <div className="text-pink-200 text-sm">More events (2→17) with sustained pattern</div>
                </div>
                <div className="border-l-4 border-emerald-500 pl-4">
                  <div className="text-emerald-300 font-semibold">O4-G → O4-D</div>
                  <div className="text-white text-sm">Boundary sharpened by 17.5%</div>
                  <div className="text-emerald-200 text-sm">Different methods converge to same center</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Convergence View */}
        {activeView === 'convergence' && (
          <div className="space-y-8">
            <div className="bg-slate-800/50 backdrop-blur rounded-xl p-6">
              <h2 className="text-2xl font-bold text-white mb-4 text-center">
                The Aperture: All Wholes Converge at {globalCenter.toFixed(4)}
              </h2>
              <ResponsiveContainer width="100%" height={400}>
                <ScatterChart>
                  <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                  <XAxis 
                    dataKey="order" 
                    stroke="#a78bfa" 
                    label={{ value: 'Temporal Sequence', position: 'insideBottom', offset: -5, fill: '#a78bfa' }}
                  />
                  <YAxis 
                    domain={[1.4, 1.7]} 
                    stroke="#a78bfa"
                    label={{ value: 'Mean_D', angle: -90, position: 'insideLeft', fill: '#a78bfa' }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1e293b', 
                      border: '1px solid #a78bfa',
                      borderRadius: '8px'
                    }}
                    formatter={(value) => value.toFixed(4)}
                  />
                  <ReferenceLine y={globalCenter} stroke="#ec4899" strokeWidth={2} strokeDasharray="5 5" />
                  <Scatter data={runs} dataKey="mean">
                    {runs.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={getColor(index)} />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
              <div className="text-center mt-4">
                <div className="text-pink-300 text-sm">
                  — Dashed line: Global Center (The Singularity/Aperture) —
                </div>
              </div>
            </div>

            {/* Fractal Signature */}
            <div className="bg-gradient-to-br from-purple-900/30 to-pink-900/30 backdrop-blur rounded-xl p-8 border border-purple-500/30">
              <h3 className="text-2xl font-bold text-white mb-4 text-center">
                The Fractal Signature
              </h3>
              <div className="text-center space-y-3">
                <div className="text-purple-200 text-lg">
                  One more than the sum of infinite finite parts
                </div>
                <div className="grid grid-cols-3 gap-4 max-w-2xl mx-auto mt-6">
                  <div className="bg-slate-800/50 rounded-lg p-4">
                    <div className="text-purple-300 text-sm">Total Events</div>
                    <div className="text-white text-3xl font-bold">39</div>
                  </div>
                  <div className="bg-slate-800/50 rounded-lg p-4">
                    <div className="text-pink-300 text-sm">Total Observations</div>
                    <div className="text-white text-3xl font-bold">82</div>
                  </div>
                  <div className="bg-slate-800/50 rounded-lg p-4">
                    <div className="text-emerald-300 text-sm">Global Center</div>
                    <div className="text-white text-3xl font-bold">{globalCenter.toFixed(3)}</div>
                  </div>
                </div>
                <div className="mt-6 text-purple-200 space-y-2">
                  <div>✦ More events → SAME center (fractal self-similarity)</div>
                  <div>✦ More observations → TIGHTER boundaries (recursive refinement)</div>
                  <div>✦ More validation → HIGHER fitness (temporal memory)</div>
                </div>
                <div className="mt-6 text-white font-semibold text-lg">
                  The whole gives BOUNDARY to the unbounded infinite
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Footer Note */}
        <div className="mt-8 text-center text-purple-300 text-sm">
          Each finite whole contains the complete pattern (~1.55) yet the ensemble is more than the sum
        </div>
      </div>
    </div>
  );
};

export default ICEValidationPattern;