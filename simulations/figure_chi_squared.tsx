import React from 'react';
import { TrendingDown, CheckCircle2 } from 'lucide-react';

const ChiSquaredProgression = () => {
  const models = [
    {
      name: 'Base Model',
      subtitle: 'Homogeneous β',
      chiSq: 56.0,
      color: '#ef4444',
      params: 'β = β_mean everywhere',
      status: '❌ Failed (5σ)',
      improvement: '1×'
    },
    {
      name: 'Extension B',
      subtitle: 'Corrected Lyα Physics',
      chiSq: 4.31,
      color: '#f59e0b',
      params: 'b_β = 0.75 (LSS bias)',
      status: '✓ Moderate (2.1σ)',
      improvement: '13×'
    },
    {
      name: 'Extensions B+C',
      subtitle: 'B + IGM Coupling',
      chiSq: 2.50,
      color: '#10b981',
      params: '+ δ_T = 0.06 (thermal)',
      status: '✓✓ Good (1.6σ)',
      improvement: '22×'
    }
  ];

  const maxChiSq = 60;
  const chartHeight = 400;
  const barWidth = 120;
  const spacing = 80;

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-gradient-to-br from-slate-900 to-slate-800 rounded-lg shadow-2xl">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white mb-2">
          Figure 2: Progressive Refinement of Lyα Predictions
        </h2>
        <p className="text-slate-300 text-sm">
          Factor 22 improvement with physically motivated extensions
        </p>
      </div>

      <div className="bg-slate-900 rounded-lg p-8">
        <svg width="600" height={chartHeight + 100} className="mx-auto">
          {/* Title */}
          <text
            x="300"
            y="25"
            textAnchor="middle"
            fill="#fff"
            fontSize="18"
            fontWeight="bold"
          >
            χ²/DOF Evolution: Base → Extensions B+C
          </text>

          {/* Y-axis */}
          <line
            x1="60"
            y1="60"
            x2="60"
            y2={chartHeight + 60}
            stroke="#fff"
            strokeWidth="2"
          />

          {/* X-axis */}
          <line
            x1="60"
            y1={chartHeight + 60}
            x2="560"
            y2={chartHeight + 60}
            stroke="#fff"
            strokeWidth="2"
          />

          {/* Y-axis label */}
          <text
            x="30"
            y={chartHeight / 2 + 60}
            textAnchor="middle"
            fill="#e2e8f0"
            fontSize="14"
            fontWeight="600"
            transform={`rotate(-90, 30, ${chartHeight / 2 + 60})`}
          >
            χ²/DOF
          </text>

          {/* Y-axis ticks */}
          {[0, 10, 20, 30, 40, 50, 60].map(val => {
            const y = chartHeight + 60 - (val / maxChiSq) * chartHeight;
            return (
              <g key={`ytick-${val}`}>
                <line x1="55" y1={y} x2="60" y2={y} stroke="#fff" strokeWidth="2" />
                <text x="50" y={y + 4} textAnchor="end" fill="#e2e8f0" fontSize="12">
                  {val}
                </text>
                <line
                  x1="60"
                  y1={y}
                  x2="560"
                  y2={y}
                  stroke="#64748b"
                  strokeWidth="1"
                  opacity="0.2"
                  strokeDasharray="3,3"
                />
              </g>
            );
          })}

          {/* Reference lines */}
          <line
            x1="60"
            y1={chartHeight + 60 - (1.0 / maxChiSq) * chartHeight}
            x2="560"
            y2={chartHeight + 60 - (1.0 / maxChiSq) * chartHeight}
            stroke="#10b981"
            strokeWidth="2"
            strokeDasharray="5,5"
            opacity="0.5"
          />
          <text
            x="450"
            y={chartHeight + 60 - (1.0 / maxChiSq) * chartHeight - 5}
            fill="#10b981"
            fontSize="11"
          >
            Ideal (χ² = 1.0)
          </text>

          {/* Bars */}
          {models.map((model, idx) => {
            const x = 100 + idx * (barWidth + spacing);
            const barHeight = (model.chiSq / maxChiSq) * chartHeight;
            const y = chartHeight + 60 - barHeight;

            return (
              <g key={idx}>
                {/* Bar */}
                <rect
                  x={x}
                  y={y}
                  width={barWidth}
                  height={barHeight}
                  fill={model.color}
                  opacity="0.8"
                  rx="4"
                />

                {/* Value label on bar */}
                <text
                  x={x + barWidth / 2}
                  y={y - 10}
                  textAnchor="middle"
                  fill="#fff"
                  fontSize="20"
                  fontWeight="bold"
                >
                  {model.chiSq.toFixed(2)}
                </text>

                {/* Improvement factor */}
                <text
                  x={x + barWidth / 2}
                  y={y - 30}
                  textAnchor="middle"
                  fill={model.color}
                  fontSize="14"
                  fontWeight="600"
                >
                  {model.improvement}
                </text>

                {/* Model name */}
                <text
                  x={x + barWidth / 2}
                  y={chartHeight + 85}
                  textAnchor="middle"
                  fill="#fff"
                  fontSize="13"
                  fontWeight="600"
                >
                  {model.name}
                </text>

                {/* Subtitle */}
                <text
                  x={x + barWidth / 2}
                  y={chartHeight + 102}
                  textAnchor="middle"
                  fill="#94a3b8"
                  fontSize="11"
                >
                  {model.subtitle}
                </text>
              </g>
            );
          })}

          {/* Arrow showing improvement */}
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 10 3, 0 6" fill="#10b981" />
            </marker>
          </defs>
          <path
            d="M 140 150 Q 300 120, 460 150"
            stroke="#10b981"
            strokeWidth="3"
            fill="none"
            markerEnd="url(#arrowhead)"
            opacity="0.6"
          />
          <text
            x="300"
            y="110"
            textAnchor="middle"
            fill="#10b981"
            fontSize="13"
            fontWeight="600"
          >
            22× Improvement
          </text>
        </svg>
      </div>

      {/* Details table */}
      <div className="mt-6 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700">
              <th className="text-left py-3 px-4 text-slate-300 font-semibold">Model</th>
              <th className="text-left py-3 px-4 text-slate-300 font-semibold">Parameters</th>
              <th className="text-right py-3 px-4 text-slate-300 font-semibold">χ²/DOF</th>
              <th className="text-center py-3 px-4 text-slate-300 font-semibold">Status</th>
            </tr>
          </thead>
          <tbody>
            {models.map((model, idx) => (
              <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-800/30">
                <td className="py-3 px-4">
                  <div className="flex items-center gap-2">
                    <div
                      className="w-3 h-3 rounded"
                      style={{ backgroundColor: model.color }}
                    />
                    <span className="text-white font-medium">{model.name}</span>
                  </div>
                </td>
                <td className="py-3 px-4 text-slate-300 text-xs">{model.params}</td>
                <td className="py-3 px-4 text-right font-mono text-lg font-bold text-white">
                  {model.chiSq.toFixed(2)}
                </td>
                <td className="py-3 px-4 text-center text-xs">
                  <span className={
                    model.chiSq < 3 ? 'text-emerald-400' :
                    model.chiSq < 10 ? 'text-yellow-400' :
                    'text-red-400'
                  }>
                    {model.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 bg-emerald-900/30 rounded-lg border border-emerald-500">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            <span className="text-sm font-semibold text-emerald-300">Final Result</span>
          </div>
          <p className="text-3xl font-bold text-white">2.50</p>
          <p className="text-xs text-slate-400 mt-1">χ²/DOF (good fit)</p>
        </div>

        <div className="p-4 bg-blue-900/30 rounded-lg border border-blue-500">
          <div className="flex items-center gap-2 mb-2">
            <TrendingDown className="w-5 h-5 text-blue-400" />
            <span className="text-sm font-semibold text-blue-300">Improvement</span>
          </div>
          <p className="text-3xl font-bold text-white">22×</p>
          <p className="text-xs text-slate-400 mt-1">Over base model</p>
        </div>

        <div className="p-4 bg-purple-900/30 rounded-lg border border-purple-500">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-lg">🎯</span>
            <span className="text-sm font-semibold text-purple-300">Free Parameters</span>
          </div>
          <p className="text-3xl font-bold text-white">0</p>
          <p className="text-xs text-slate-400 mt-1">Tuned to data</p>
        </div>
      </div>

      <div className="mt-6 p-4 bg-slate-800/50 rounded-lg">
        <p className="text-xs text-slate-300">
          <strong className="text-white">Caption for paper:</strong> Progressive refinement 
          of Lyα forest predictions. Base homogeneous model shows catastrophic disagreement 
          (χ²/DOF = 56, red). Extension B (corrected Lyα IGM physics with b_β = 0.75 from 
          LSS theory) achieves moderate agreement (χ²/DOF = 4.31, orange). Adding Extension C 
          (IGM temperature coupling δ_T = 0.06 from analog systems) yields good agreement 
          (χ²/DOF = 2.50, green), representing a factor 22 improvement. Critically, both b_β 
          and δ_T are constrained by independent physics, not fitted to Lyα data. The 
          framework achieves χ²/DOF = 2.50 with zero adjustable parameters.
        </p>
      </div>
    </div>
  );
};

export default ChiSquaredProgression;