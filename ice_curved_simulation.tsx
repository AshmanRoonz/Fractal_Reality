import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw, Download } from 'lucide-react';

const ICECurvedSimulation = () => {
  const canvasRef = useRef(null);
  const [isRunning, setIsRunning] = useState(false);
  const [metricType, setMetricType] = useState('flat');
  const [energy, setEnergy] = useState(100);
  const [iteration, setIteration] = useState(0);
  const [measuredD, setMeasuredD] = useState(null);
  const [textureAccum, setTextureAccum] = useState(0);
  const animationRef = useRef(null);
  const stateRef = useRef({
    phi: [],
    path: [],
    validations: 0,
    failedValidations: 0
  });

  // Initialize field
  useEffect(() => {
    const N = 200;
    const phi = new Array(N).fill(0).map(() => ({
      re: Math.random() * 0.1 - 0.05,
      im: Math.random() * 0.1 - 0.05
    }));
    
    // Add Gaussian wave packet
    const center = N / 2;
    const sigma = 10;
    for (let i = 0; i < N; i++) {
      const x = i - center;
      const gauss = Math.exp(-x * x / (2 * sigma * sigma));
      phi[i].re += gauss * Math.cos(0.5 * i);
      phi[i].im += gauss * Math.sin(0.5 * i);
    }
    
    stateRef.current = {
      phi,
      path: [[center, 0]],
      validations: 0,
      failedValidations: 0
    };
    
    setIteration(0);
    setTextureAccum(0);
  }, [metricType, energy]);

  // Metric functions
  const getMetric = (position, type) => {
    const r = Math.abs(position - 100) + 30; // Distance from "mass" (increased safety margin)
    
    switch(type) {
      case 'flat':
        return { g_tt: -1.0, g_rr: 1.0 };
      
      case 'weak':
        const rs_weak = 3; // Reduced for stability
        return {
          g_tt: -(1 - rs_weak / r),
          g_rr: 1 / (1 - rs_weak / r)
        };
      
      case 'neutron':
        const rs_ns = 10; // Reduced for stability
        return {
          g_tt: Math.max(-0.6, -(1 - rs_ns / r)),
          g_rr: Math.min(1.67, 1 / Math.max(0.6, 1 - rs_ns / r))
        };
      
      case 'horizon':
        const rs_bh = 20; // Reduced for stability
        return {
          g_tt: Math.max(-0.05, -(1 - rs_bh / r)),
          g_rr: Math.min(20, 1 / Math.max(0.05, 1 - rs_bh / r))
        };
      
      default:
        return { g_tt: -1.0, g_rr: 1.0 };
    }
  };

  // D(E) prediction
  const predictedD = (E) => {
    return 1.50 * (1.08 - 0.12 * Math.pow(E / 100, -0.3));
  };

  // ICE validation - significantly more lenient for flat spacetime
  const iceValidation = (phi, idx, g_tt, g_rr) => {
    const N = phi.length;
    if (idx < 2 || idx >= N - 2) return false;
    
    // Get amplitude at this point
    const amp = Math.sqrt(phi[idx].re ** 2 + phi[idx].im ** 2);
    
    // C: Center - must have non-zero amplitude
    if (amp < 0.0001) return false;
    
    // I: Interface - check that field is not exploding
    const neighbors = [
      Math.sqrt(phi[idx-1].re ** 2 + phi[idx-1].im ** 2),
      Math.sqrt(phi[idx+1].re ** 2 + phi[idx+1].im ** 2)
    ];
    const maxNeighbor = Math.max(...neighbors);
    
    // Field shouldn't change too drastically (but allow some variation)
    const gradientOK = (maxNeighbor < 100 * amp) && (amp < 100 * maxNeighbor);
    
    // E: Evidence - local energy should be reasonable
    let localEnergy = 0;
    for (let i = Math.max(0, idx - 3); i < Math.min(N, idx + 4); i++) {
      localEnergy += phi[i].re ** 2 + phi[i].im ** 2;
    }
    
    const energyOK = localEnergy > 0.001 && localEnergy < 100;
    
    // In flat spacetime, be very lenient
    if (Math.abs(g_tt + 1.0) < 0.01) {
      return amp > 0.001 && amp < 10 && gradientOK;
    }
    
    // In curved spacetime, slightly stricter
    return gradientOK && energyOK;
  };

  // Laplacian with metric
  const laplacian = (phi, idx, g_rr) => {
    const N = phi.length;
    if (idx < 1 || idx >= N - 1) return { re: 0, im: 0 };
    
    const dx = 1.0;
    const factor = Math.min(Math.abs(g_rr), 10); // Cap extreme metric values
    const dx_proper = dx * Math.sqrt(factor);
    
    const lap_re = (phi[idx + 1].re - 2 * phi[idx].re + phi[idx - 1].re) / (dx_proper * dx_proper);
    const lap_im = (phi[idx + 1].im - 2 * phi[idx].im + phi[idx - 1].im) / (dx_proper * dx_proper);
    
    return {
      re: lap_re,
      im: lap_im
    };
  };

  // Simulation step
  const simulationStep = () => {
    const state = stateRef.current;
    const N = state.phi.length;
    const phi = state.phi;
    
    // Find peak (particle position)
    let maxAmp = 0;
    let peakIdx = N / 2;
    for (let i = 5; i < N - 5; i++) {
      const amp = Math.sqrt(phi[i].re ** 2 + phi[i].im ** 2);
      if (amp > maxAmp) {
        maxAmp = amp;
        peakIdx = i;
      }
    }
    
    // Get metric at peak
    const { g_tt, g_rr } = getMetric(peakIdx, metricType);
    
    // Time step modified by metric (cap extreme values)
    const dt_base = 0.1; // Back to reasonable value
    const sqrt_g_tt = Math.sqrt(Math.abs(g_tt));
    const dt_proper = dt_base * Math.min(sqrt_g_tt, 1.0);
    
    // Validate at peak
    const validated = iceValidation(phi, peakIdx, g_tt, g_rr);
    
    if (validated) {
      state.validations++;
      
      // Update field with metric-dependent evolution
      const phi_new = [...phi];
      
      // Add diffusion constant (energy dependent)
      const D_coeff = 0.2 / Math.sqrt(energy / 100);
      
      for (let i = 1; i < N - 1; i++) {
        const lap = laplacian(phi, i, g_rr);
        
        phi_new[i] = {
          re: phi[i].re + dt_proper * D_coeff * lap.re,
          im: phi[i].im + dt_proper * D_coeff * lap.im
        };
      }
      
      // Gentle normalization to prevent drift
      let totalNorm = 0;
      for (let i = 0; i < N; i++) {
        totalNorm += phi_new[i].re ** 2 + phi_new[i].im ** 2;
      }
      
      const targetNorm = N * 0.5; // Target average amplitude
      const normFactor = Math.sqrt(targetNorm / Math.max(totalNorm, 0.01));
      
      // Only normalize if factor is reasonable
      if (normFactor > 0.5 && normFactor < 2.0) {
        for (let i = 0; i < N; i++) {
          phi_new[i].re *= normFactor;
          phi_new[i].im *= normFactor;
        }
      }
      
      // Add texture proportional to sqrt(|g_tt|)
      const texture = sqrt_g_tt;
      setTextureAccum(prev => prev + texture);
      
      state.phi = phi_new;
      state.path.push([peakIdx, iteration]);
    } else {
      state.failedValidations++;
    }
    
    stateRef.current = state;
  };

  // Calculate D from path
  const calculateD = () => {
    const path = stateRef.current.path;
    if (path.length < 20) return null;
    
    // Box-counting method
    const boxSizes = [2, 4, 8, 16];
    const counts = boxSizes.map(epsilon => {
      const boxes = new Set();
      path.forEach(([x, t]) => {
        const boxX = Math.floor(x / epsilon);
        const boxT = Math.floor(t / epsilon);
        boxes.add(`${boxX},${boxT}`);
      });
      return boxes.size;
    });
    
    // Filter out invalid counts
    const validData = boxSizes.map((size, i) => ({ size, count: counts[i] }))
      .filter(d => d.count > 0);
    
    if (validData.length < 3) return null;
    
    // Linear regression log(N) vs log(1/epsilon)
    const logEps = validData.map(d => Math.log(1 / d.size));
    const logN = validData.map(d => Math.log(d.count));
    
    const n = logEps.length;
    const sumX = logEps.reduce((a, b) => a + b, 0);
    const sumY = logN.reduce((a, b) => a + b, 0);
    const sumXY = logEps.reduce((sum, x, i) => sum + x * logN[i], 0);
    const sumX2 = logEps.reduce((sum, x) => sum + x * x, 0);
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    
    // D should be positive and reasonable
    return (slope > 0.5 && slope < 2.5) ? slope : null;
  };

  // Animation loop
  useEffect(() => {
    if (isRunning) {
      animationRef.current = setInterval(() => {
        simulationStep();
        setIteration(prev => prev + 1);
        
        if (iteration % 25 === 0 && iteration > 50) {
          const D = calculateD();
          if (D && !isNaN(D) && D > 0 && D < 3) {
            setMeasuredD(D);
          }
        }
      }, 50);
    } else {
      if (animationRef.current) {
        clearInterval(animationRef.current);
      }
    }
    
    return () => {
      if (animationRef.current) {
        clearInterval(animationRef.current);
      }
    };
  }, [isRunning, iteration]);

  // Draw
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, width, height);
    
    // Draw field amplitude
    const phi = stateRef.current.phi;
    const N = phi.length;
    ctx.strokeStyle = '#0ff';
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (let i = 0; i < N; i++) {
      const x = (i / N) * width;
      const amp = Math.sqrt(phi[i].re ** 2 + phi[i].im ** 2);
      const y = height / 2 - amp * 50;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
    
    // Draw path (trajectory)
    const path = stateRef.current.path;
    if (path.length > 1) {
      ctx.strokeStyle = '#ff0';
      ctx.lineWidth = 1;
      ctx.beginPath();
      const scale = Math.min(iteration / 500, 1);
      path.forEach(([x, t], i) => {
        const px = (x / N) * width;
        const py = height - (t / (iteration + 1)) * height * scale;
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      });
      ctx.stroke();
    }
    
    // Draw metric indicator
    const peakIdx = Math.floor(N / 2);
    const { g_tt, g_rr } = getMetric(peakIdx, metricType);
    ctx.fillStyle = '#fff';
    ctx.font = '12px monospace';
    ctx.fillText(`g_tt = ${g_tt.toFixed(3)}`, 10, 20);
    ctx.fillText(`g_rr = ${g_rr.toFixed(3)}`, 10, 35);
    ctx.fillText(`Texture: ${textureAccum.toFixed(2)}`, 10, 50);
    
  }, [iteration, metricType, textureAccum]);

  const predD = predictedD(energy);
  const validationRate = stateRef.current.validations / (stateRef.current.validations + stateRef.current.failedValidations + 1);

  return (
    <div className="w-full h-screen bg-gray-900 text-white p-6">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">ICE Validation in Curved Spacetime</h1>
        <p className="text-gray-400 mb-6">Interactive simulation of interface validation under metric coupling</p>
        
        <div className="grid grid-cols-2 gap-6 mb-6">
          {/* Canvas */}
          <div className="bg-black rounded-lg p-4">
            <canvas
              ref={canvasRef}
              width={600}
              height={400}
              className="w-full border border-gray-700 rounded"
            />
          </div>
          
          {/* Controls */}
          <div className="space-y-4">
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="font-semibold mb-3">Spacetime Metric</h3>
              <select
                value={metricType}
                onChange={(e) => setMetricType(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                disabled={isRunning}
              >
                <option value="flat">Flat (Minkowski): g_tt = -1</option>
                <option value="weak">Weak Field: g_tt ≈ -0.99</option>
                <option value="neutron">Neutron Star: g_tt ≈ -0.5</option>
                <option value="horizon">Near Horizon: g_tt ≈ -0.01</option>
              </select>
            </div>
            
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="font-semibold mb-3">Particle Energy: {energy} MeV</h3>
              <input
                type="range"
                min="10"
                max="1000"
                value={energy}
                onChange={(e) => setEnergy(Number(e.target.value))}
                className="w-full"
                disabled={isRunning}
              />
            </div>
            
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="font-semibold mb-3">Controls</h3>
              <div className="flex gap-2">
                <button
                  onClick={() => setIsRunning(!isRunning)}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded flex items-center justify-center gap-2"
                >
                  {isRunning ? <Pause size={16} /> : <Play size={16} />}
                  {isRunning ? 'Pause' : 'Start'}
                </button>
                <button
                  onClick={() => {
                    setIsRunning(false);
                    window.location.reload();
                  }}
                  className="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded flex items-center gap-2"
                >
                  <RotateCcw size={16} />
                  Reset
                </button>
              </div>
            </div>
          </div>
        </div>
        
        {/* Results */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Iteration</div>
            <div className="text-2xl font-bold">{iteration}</div>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Predicted D(E)</div>
            <div className="text-2xl font-bold text-blue-400">{predD.toFixed(3)}</div>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Measured D</div>
            <div className="text-2xl font-bold text-green-400">
              {measuredD ? measuredD.toFixed(3) : '---'}
            </div>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Validation Rate</div>
            <div className="text-2xl font-bold">{(validationRate * 100).toFixed(1)}%</div>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Validations</div>
            <div className="text-2xl font-bold text-green-400">{stateRef.current.validations}</div>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Failed</div>
            <div className="text-2xl font-bold text-red-400">{stateRef.current.failedValidations}</div>
          </div>
        </div>
        
        <div className="mt-4 bg-gray-800 rounded-lg p-4">
          <h3 className="font-semibold mb-2">Predictions to Test</h3>
          <ul className="text-sm space-y-1 text-gray-300">
            <li>• <strong>Flat metric:</strong> D → 1.50 (baseline)</li>
            <li>• <strong>Weak field:</strong> D ≈ 1.48 (small correction)</li>
            <li>• <strong>Neutron star:</strong> D ≈ 1.35 (significant suppression)</li>
            <li>• <strong>Near horizon:</strong> D → 1.0-1.2 (strong suppression, approaches null curve)</li>
            <li>• <strong>Energy dependence:</strong> D decreases with increasing E</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ICECurvedSimulation;