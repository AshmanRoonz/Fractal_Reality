import React, { useState } from 'react';
import { Info, TrendingUp, Database } from 'lucide-react';

const EnvironmentalCorrelationPlot = () => {
  const [showInfo, setShowInfo] = useState(true);
  const [highlightEnv, setHighlightEnv] = useState(null);

  // Physical parameters
  const BETA_MEAN = 4.823;
  const B_BETA = 0.75;
  
  // Environmental data
  const environments = [
    { 
      name: 'Deep Voids',
      delta_m: -0.8,
      beta: BETA_MEAN * (1 + B_BETA * (-0.8)),
      volume_frac: 0.15,
      lya_weight: 0.40,
      color: '#3b82f6',
      x: 15
    },
    { 
      name: 'Voids',
      delta_m: -0.5,
      beta: BETA_MEAN * (1 + B_BETA * (-0.5)),
      volume_frac: 0.35,
      lya_weight: 0.35,
      color: '#60a5fa',
      x: 30
    },
    { 
      name: 'Sheets',
      delta_m: -0.2,
      beta: BETA_MEAN * (1 + B_BETA * (-0.2)),
      volume_frac: 0.25,
      lya_weight: 0.18,
      color: '#93c5fd',
      x: 45
    },
    { 
      name: 'Mean',
      delta_m: 0.0,
      beta: BETA_MEAN,
      volume_frac: 0.15,
      lya_weight: 0.05,
      color: '#a5f3fc',
      x: 60
    },
    { 
      name: 'Filaments',
      delta_m: 0.5,
      beta: BETA_MEAN * (1 + B_BETA * 0.5),
      volume_frac: 0.08,
      lya_weight: 0.02,
      color: '#fcd34d',
      x: 75
    },
    { 
      name: 'Nodes',
      delta_m: 1.5,
      beta: BETA_MEAN * (1 + B_BETA * 1.5),
      volume_frac: 0.02,
      lya_weight: 0.00,
      color: '#fbbf24',
      x: 90
    }
  ];

  // Calculate tau_eff relative to mean
  const tauEffData = environments.map(env => {
    const beta_ratio = env.beta / BETA_MEAN;
    const tau_ratio = beta_ratio; // Simplified: tau_eff ∝ β
    const delta_tau_percent = (tau_ratio - 1) * 100;
    
    // Expected detection significance with DESI DR2
    const observational_error = 5; // 5% per environment bin
    const sigma_detection = Math.abs(delta_tau_percent) / observational_error;
    
    return {
      ...env,
      tau_ratio,
      delta_tau_percent,
      sigma_detection
    };
  });

  // Plotting parameters
  const plotWidth = 600;
  const plotHeight = 400;
  const margin = { top: 40, right: 120, bottom: 60, left: 80 };
  const innerWidth = plotWidth - margin.left - margin.right;
  const innerHeight = plotHeight - margin.top - margin.bottom;

  // Scales
  const xScale = (delta_m) => {
    const xMin = -1.0;
    const xMax = 2.0;
    return margin.left + ((delta_m - xMin) / (xMax - xMin)) * innerWidth;
  };

  const yScale = (delta_tau) => {
    const yMin = -60;
    const yMax = 80;
    return margin.top + ((yMax - delta_tau) / (yMax - yMin)) * innerHeight;
  };

  return (
    <div className="w-full max-w-5xl mx-auto p-6 bg-gradient-to-br from-slate-900 to-slate-800 rounded-lg shadow-2xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">
            Environmental Correlation Forecast
          </h1>
          <p className="text-slate-300">
            Predicted τ_eff vs local density • SDSS-V × DESI (2026)
          </p>
        </div>
        <button
          onClick={() => setShowInfo(!showInfo)}
          className="p-2 text-slate-400 hover:text-white transition-colors"
        >
          <Info className="w-6 h-6" />
        </button>
      </div>

      {showInfo && (
        <div className="mb-6 p-4 bg-slate-800/50 rounded-lg border border-slate-700">
          <h3 className="text-lg font-semibold text-white mb-2">Test Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-slate-300">
            <div>
              <p className="font-semibold text-emerald-400 mb-1">Prediction:</p>
              <p>τ_eff varies with local matter density δ_m</p>
              <p className="mt-2">β(x) = β_mean × [1 + b_β × δ_m]</p>
              <p>b_β = 0.75 (texture bias)</p>
            </div>
            <div>
              <p className="font-semibold text-blue-400 mb-1">Observable:</p>
              <p>Cross-correlate DESI Lyα with SDSS-V galaxies</p>
              <p className="mt-2">Expected: 6-12σ total signal</p>
              <p>Timeline: DR2 (2026)</p>
            </div>
          </div>
        </div>
      )}

      <div className="bg-slate-900 rounded-lg p-6 mb-6">
        <svg width={plotWidth} height={plotHeight} className="mx-auto">
          {/* Grid lines */}
          <g opacity="0.2">
            {[-0.5, 0, 0.5, 1.0, 1.5].map(x => (
              <line
                key={`vline-${x}`}
                x1={xScale(x)}
                y1={margin.top}
                x2={xScale(x)}
                y2={plotHeight - margin.bottom}
                stroke="#94a3b8"
                strokeWidth="1"
                strokeDasharray="2,2"
              />
            ))}
            {[-40, -20, 0, 20, 40, 60].map(y => (
              <line
                key={`hline-${y}`}
                x1={margin.left}
                y1={yScale(y)}
                x2={plotWidth - margin.right}
                y2={yScale(y)}
                stroke="#94a3b8"
                strokeWidth="1"
                strokeDasharray="2,2"
              />
            ))}
          </g>

          {/* Axes */}
          <line
            x1={margin.left}
            y1={yScale(0)}
            x2={plotWidth - margin.right}
            y2={yScale(0)}
            stroke="#fff"
            strokeWidth="2"
          />
          <line
            x1={xScale(0)}
            y1={margin.top}
            x2={xScale(0)}
            y2={plotHeight - margin.bottom}
            stroke="#fff"
            strokeWidth="2"
          />

          {/* Theory line */}
          <path
            d={`M ${xScale(-1)} ${yScale(-1 * B_BETA * BETA_MEAN / BETA_MEAN * 100)} 
                L ${xScale(2)} ${yScale(2 * B_BETA * BETA_MEAN / BETA_MEAN * 100)}`}
            stroke="#10b981"
            strokeWidth="3"
            fill="none"
            strokeDasharray="5,5"
          />

          {/* Data points with error bars */}
          {tauEffData.map((env, idx) => {
            const cx = xScale(env.delta_m);
            const cy = yScale(env.delta_tau_percent);
            const errorBar = 5; // 5% observational uncertainty
            const isHighlighted = highlightEnv === env.name;

            return (
              <g key={idx}>
                {/* Error bar */}
                <line
                  x1={cx}
                  y1={yScale(env.delta_tau_percent - errorBar)}
                  x2={cx}
                  y2={yScale(env.delta_tau_percent + errorBar)}
                  stroke={env.color}
                  strokeWidth="2"
                  opacity={isHighlighted ? 1 : 0.6}
                />
                <line
                  x1={cx - 5}
                  y1={yScale(env.delta_tau_percent - errorBar)}
                  x2={cx + 5}
                  y2={yScale(env.delta_tau_percent - errorBar)}
                  stroke={env.color}
                  strokeWidth="2"
                  opacity={isHighlighted ? 1 : 0.6}
                />
                <line
                  x1={cx - 5}
                  y1={yScale(env.delta_tau_percent + errorBar)}
                  x2={cx + 5}
                  y2={yScale(env.delta_tau_percent + errorBar)}
                  stroke={env.color}
                  strokeWidth="2"
                  opacity={isHighlighted ? 1 : 0.6}
                />

                {/* Data point */}
                <circle
                  cx={cx}
                  cy={cy}
                  r={isHighlighted ? 8 : 6}
                  fill={env.color}
                  stroke="#fff"
                  strokeWidth={isHighlighted ? 3 : 2}
                  opacity={isHighlighted ? 1 : 0.8}
                  style={{ cursor: 'pointer' }}
                  onMouseEnter={() => setHighlightEnv(env.name)}
                  onMouseLeave={() => setHighlightEnv(null)}
                />

                {/* Sigma detection label */}
                {env.sigma_detection > 3 && (
                  <text
                    x={cx}
                    y={cy - 15}
                    textAnchor="middle"
                    fill={env.color}
                    fontSize="11"
                    fontWeight="bold"
                    opacity={isHighlighted ? 1 : 0.7}
                  >
                    {env.sigma_detection.toFixed(1)}σ
                  </text>
                )}
              </g>
            );
          })}

          {/* Axis labels */}
          <text
            x={plotWidth / 2}
            y={plotHeight - 10}
            textAnchor="middle"
            fill="#e2e8f0"
            fontSize="14"
            fontWeight="600"
          >
            Local Matter Overdensity δ_m = ρ/⟨ρ⟩ - 1
          </text>

          <text
            x={margin.left - 60}
            y={plotHeight / 2}
            textAnchor="middle"
            fill="#e2e8f0"
            fontSize="14"
            fontWeight="600"
            transform={`rotate(-90, ${margin.left - 60}, ${plotHeight / 2})`}
          >
            Δτ_eff / τ_mean (%)
          </text>

          {/* Title */}
          <text
            x={plotWidth / 2}
            y={25}
            textAnchor="middle"
            fill="#fff"
            fontSize="16"
            fontWeight="bold"
          >
            Texture Framework: τ_eff vs Environment
          </text>

          {/* Legend */}
          <g transform={`translate(${plotWidth - margin.right + 20}, ${margin.top})`}>
            <text fill="#fff" fontSize="12" fontWeight="600" y="0">
              Legend
            </text>
            <line
              x1="0"
              y1="15"
              x2="30"
              y2="15"
              stroke="#10b981"
              strokeWidth="3"
              strokeDasharray="5,5"
            />
            <text fill="#e2e8f0" fontSize="11" x="35" y="19">
              Theory
            </text>
            <circle cx="15" cy="35" r="5" fill="#60a5fa" />
            <text fill="#e2e8f0" fontSize="11" x="25" y="39">
              Forecast
            </text>
          </g>

          {/* Axis ticks */}
          {[-1, -0.5, 0, 0.5, 1.0, 1.5, 2.0].map(x => (
            <g key={`xtick-${x}`}>
              <line
                x1={xScale(x)}
                y1={plotHeight - margin.bottom}
                x2={xScale(x)}
                y2={plotHeight - margin.bottom + 5}
                stroke="#fff"
                strokeWidth="2"
              />
              <text
                x={xScale(x)}
                y={plotHeight - margin.bottom + 20}
                textAnchor="middle"
                fill="#e2e8f0"
                fontSize="11"
              >
                {x.toFixed(1)}
              </text>
            </g>
          ))}

          {[-60, -40, -20, 0, 20, 40, 60, 80].map(y => (
            <g key={`ytick-${y}`}>
              <line
                x1={margin.left - 5}
                y1={yScale(y)}
                x2={margin.left}
                y2={yScale(y)}
                stroke="#fff"
                strokeWidth="2"
              />
              <text
                x={margin.left - 10}
                y={yScale(y) + 4}
                textAnchor="end"
                fill="#e2e8f0"
                fontSize="11"
              >
                {y > 0 ? '+' : ''}{y}
              </text>
            </g>
          ))}
        </svg>
      </div>

      {/* Environment Details Table */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-800 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
            <Database className="w-5 h-5 text-blue-400" />
            Environment Properties
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-2 text-slate-300">Region</th>
                  <th className="text-right py-2 text-slate-300">δ_m</th>
                  <th className="text-right py-2 text-slate-300">β</th>
                  <th className="text-right py-2 text-slate-300">Vol%</th>
                </tr>
              </thead>
              <tbody>
                {tauEffData.map((env, idx) => (
                  <tr
                    key={idx}
                    className={`border-b border-slate-700/50 cursor-pointer transition-colors ${
                      highlightEnv === env.name ? 'bg-slate-700' : 'hover:bg-slate-700/30'
                    }`}
                    onMouseEnter={() => setHighlightEnv(env.name)}
                    onMouseLeave={() => setHighlightEnv(null)}
                  >
                    <td className="py-2">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: env.color }}
                        />
                        <span className="text-white">{env.name}</span>
                      </div>
                    </td>
                    <td className="text-right font-mono text-slate-300">
                      {env.delta_m.toFixed(1)}
                    </td>
                    <td className="text-right font-mono text-slate-300">
                      {env.beta.toFixed(2)}
                    </td>
                    <td className="text-right font-mono text-slate-300">
                      {(env.volume_frac * 100).toFixed(0)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-slate-800 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-emerald-400" />
            Detection Forecast
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-2 text-slate-300">Region</th>
                  <th className="text-right py-2 text-slate-300">Δτ_eff</th>
                  <th className="text-right py-2 text-slate-300">Signal</th>
                  <th className="text-center py-2 text-slate-300">Status</th>
                </tr>
              </thead>
              <tbody>
                {tauEffData.map((env, idx) => (
                  <tr
                    key={idx}
                    className={`border-b border-slate-700/50 cursor-pointer transition-colors ${
                      highlightEnv === env.name ? 'bg-slate-700' : 'hover:bg-slate-700/30'
                    }`}
                    onMouseEnter={() => setHighlightEnv(env.name)}
                    onMouseLeave={() => setHighlightEnv(null)}
                  >
                    <td className="py-2">
                      <span className="text-white">{env.name}</span>
                    </td>
                    <td className="text-right font-mono">
                      <span className={env.delta_tau_percent < 0 ? 'text-blue-400' : 'text-orange-400'}>
                        {env.delta_tau_percent > 0 ? '+' : ''}{env.delta_tau_percent.toFixed(1)}%
                      </span>
                    </td>
                    <td className="text-right font-mono">
                      <span className={
                        env.sigma_detection > 5 ? 'text-emerald-400' :
                        env.sigma_detection > 3 ? 'text-yellow-400' :
                        'text-slate-400'
                      }>
                        {env.sigma_detection.toFixed(1)}σ
                      </span>
                    </td>
                    <td className="text-center">
                      {env.sigma_detection > 5 ? '✓✓' :
                       env.sigma_detection > 3 ? '✓' : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="mt-6 p-4 bg-emerald-900/30 rounded-lg border border-emerald-500">
        <h3 className="text-lg font-semibold text-emerald-400 mb-2">
          Combined Detection Significance
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-slate-300 mb-1">Total χ² for correlation:</p>
            <p className="text-2xl font-bold text-white">
              {tauEffData.reduce((sum, env) => sum + env.sigma_detection**2, 0).toFixed(1)}
            </p>
          </div>
          <div>
            <p className="text-slate-300 mb-1">Combined significance:</p>
            <p className="text-2xl font-bold text-emerald-400">
              {Math.sqrt(tauEffData.reduce((sum, env) => sum + env.sigma_detection**2, 0)).toFixed(1)}σ
            </p>
          </div>
          <div>
            <p className="text-slate-300 mb-1">Expected by:</p>
            <p className="text-2xl font-bold text-white">
              2026
            </p>
          </div>
        </div>
        <p className="text-xs text-slate-400 mt-3">
          Assumes DESI DR2 + SDSS-V with 5% per-bin measurement precision on τ_eff × density
        </p>
      </div>

      <div className="mt-4 p-4 bg-slate-800/50 rounded-lg">
        <h3 className="text-sm font-semibold text-slate-400 mb-2">Key Points:</h3>
        <ul className="text-xs text-slate-300 space-y-1">
          <li>• <strong className="text-blue-400">Voids</strong>: β low → τ_eff reduced by 35-60% (6-12σ detectable)</li>
          <li>• <strong className="text-orange-400">Filaments</strong>: β high → τ_eff enhanced by 35-80% (6-10σ detectable)</li>
          <li>• <strong className="text-emerald-400">Linear correlation</strong>: τ_eff ∝ [1 + b_β × δ_m] validates texture bias</li>
          <li>• <strong className="text-white">Independent test</strong>: Does not depend on global τ_eff fit quality</li>
          <li>• <strong className="text-purple-400">Falsifiable</strong>: If correlation absent or wrong sign → model rejected</li>
        </ul>
      </div>
    </div>
  );
};

export default EnvironmentalCorrelationPlot;