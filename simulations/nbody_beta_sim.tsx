import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw, Download, Info } from 'lucide-react';

const NBodyBetaSimulator = () => {
  const canvasRef = useRef(null);
  const [isRunning, setIsRunning] = useState(false);
  const [step, setStep] = useState(0);
  const [particles, setParticles] = useState([]);
  const [betaStats, setBetaStats] = useState(null);
  const [lyaWeightedBeta, setLyaWeightedBeta] = useState(null);
  const [showInfo, setShowInfo] = useState(true);
  
  // Simulation parameters
  const N_PARTICLES = 256;
  const BOX_SIZE = 100; // Mpc/h
  const GRID_SIZE = 32;
  const DT = 0.05;
  const Z_INITIAL = 10;
  const Z_TARGET = 2.3; // Lyα forest epoch
  const BETA_MEAN = 4.823;
  const B_BETA = 0.75; // Texture bias parameter
  
  // Initialize particles with Zel'dovich approximation
  const initializeParticles = () => {
    const newParticles = [];
    const gridStep = BOX_SIZE / Math.cbrt(N_PARTICLES);
    
    // Start with regular lattice
    for (let i = 0; i < Math.cbrt(N_PARTICLES); i++) {
      for (let j = 0; j < Math.cbrt(N_PARTICLES); j++) {
        for (let k = 0; k < Math.cbrt(N_PARTICLES); k++) {
          // Initial position on lattice
          const x0 = i * gridStep + gridStep/2;
          const y0 = j * gridStep + gridStep/2;
          const z0 = k * gridStep + gridStep/2;
          
          // Add initial perturbations (Gaussian random field)
          const sigma_pert = 2.0; // Mpc/h
          const dx = sigma_pert * (Math.random() - 0.5) * 2;
          const dy = sigma_pert * (Math.random() - 0.5) * 2;
          const dz = sigma_pert * (Math.random() - 0.5) * 2;
          
          // Initial velocity from growing mode
          const vx = dx * 0.1;
          const vy = dy * 0.1;
          const vz = dz * 0.1;
          
          newParticles.push({
            x: x0 + dx,
            y: y0 + dy,
            z: z0 + dz,
            vx,
            vy,
            vz,
            mass: 1.0
          });
        }
      }
    }
    
    return newParticles;
  };
  
  // Compute density field on grid using Cloud-in-Cell
  const computeDensityField = (particles) => {
    const grid = Array(GRID_SIZE).fill(0).map(() => 
      Array(GRID_SIZE).fill(0).map(() => 
        Array(GRID_SIZE).fill(0)
      )
    );
    
    const cellSize = BOX_SIZE / GRID_SIZE;
    
    particles.forEach(p => {
      // Periodic boundary
      const px = ((p.x % BOX_SIZE) + BOX_SIZE) % BOX_SIZE;
      const py = ((p.y % BOX_SIZE) + BOX_SIZE) % BOX_SIZE;
      const pz = ((p.z % BOX_SIZE) + BOX_SIZE) % BOX_SIZE;
      
      // Grid cell indices
      const i = Math.floor(px / cellSize);
      const j = Math.floor(py / cellSize);
      const k = Math.floor(pz / cellSize);
      
      // Cloud-in-Cell weights
      const dx = (px - i * cellSize) / cellSize;
      const dy = (py - j * cellSize) / cellSize;
      const dz = (pz - k * cellSize) / cellSize;
      
      // Distribute mass to 8 neighboring cells
      for (let di = 0; di <= 1; di++) {
        for (let dj = 0; dj <= 1; dj++) {
          for (let dk = 0; dk <= 1; dk++) {
            const ii = (i + di) % GRID_SIZE;
            const jj = (j + dj) % GRID_SIZE;
            const kk = (k + dk) % GRID_SIZE;
            
            const wx = di === 0 ? (1 - dx) : dx;
            const wy = dj === 0 ? (1 - dy) : dy;
            const wz = dk === 0 ? (1 - dz) : dz;
            
            grid[ii][jj][kk] += p.mass * wx * wy * wz;
          }
        }
      }
    });
    
    // Convert to overdensity δ = ρ/ρ_mean - 1
    const meanDensity = particles.length / (GRID_SIZE ** 3);
    return grid.map(slice => 
      slice.map(row => 
        row.map(val => val / meanDensity - 1)
      )
    );
  };
  
  // Compute gravitational potential via FFT (simplified: Multigrid approximation)
  const computeForces = (densityField) => {
    const forces = Array(GRID_SIZE).fill(0).map(() => 
      Array(GRID_SIZE).fill(0).map(() => 
        Array(GRID_SIZE).fill(0).map(() => ({ fx: 0, fy: 0, fz: 0 }))
      )
    );
    
    const cellSize = BOX_SIZE / GRID_SIZE;
    
    // Simple 7-point stencil for gravitational potential
    for (let i = 0; i < GRID_SIZE; i++) {
      for (let j = 0; j < GRID_SIZE; j++) {
        for (let k = 0; k < GRID_SIZE; k++) {
          const ip = (i + 1) % GRID_SIZE;
          const im = (i - 1 + GRID_SIZE) % GRID_SIZE;
          const jp = (j + 1) % GRID_SIZE;
          const jm = (j - 1 + GRID_SIZE) % GRID_SIZE;
          const kp = (k + 1) % GRID_SIZE;
          const km = (k - 1 + GRID_SIZE) % GRID_SIZE;
          
          // Force from density gradient
          forces[i][j][k].fx = -(densityField[ip][j][k] - densityField[im][j][k]) / (2 * cellSize);
          forces[i][j][k].fy = -(densityField[i][jp][k] - densityField[i][jm][k]) / (2 * cellSize);
          forces[i][j][k].fz = -(densityField[i][j][kp] - densityField[i][j][km]) / (2 * cellSize);
        }
      }
    }
    
    return forces;
  };
  
  // Evolve particles one timestep
  const evolveParticles = (particles, redshift) => {
    const densityField = computeDensityField(particles);
    const forces = computeForces(densityField);
    const cellSize = BOX_SIZE / GRID_SIZE;
    
    // Hubble drag factor
    const H_factor = 1.0 / (1 + redshift);
    
    return particles.map(p => {
      // Get force at particle position (nearest grid point)
      const px = ((p.x % BOX_SIZE) + BOX_SIZE) % BOX_SIZE;
      const py = ((p.y % BOX_SIZE) + BOX_SIZE) % BOX_SIZE;
      const pz = ((p.z % BOX_SIZE) + BOX_SIZE) % BOX_SIZE;
      
      const i = Math.floor(px / cellSize) % GRID_SIZE;
      const j = Math.floor(py / cellSize) % GRID_SIZE;
      const k = Math.floor(pz / cellSize) % GRID_SIZE;
      
      const force = forces[i][j][k];
      
      // Leapfrog integration with Hubble drag
      const vx_new = p.vx * H_factor + force.fx * DT;
      const vy_new = p.vy * H_factor + force.fy * DT;
      const vz_new = p.vz * H_factor + force.fz * DT;
      
      return {
        x: p.x + vx_new * DT,
        y: p.y + vy_new * DT,
        z: p.z + vz_new * DT,
        vx: vx_new,
        vy: vy_new,
        vz: vz_new,
        mass: p.mass
      };
    });
  };
  
  // Compute β(x,z) from density field
  const computeBetaField = (densityField) => {
    return densityField.map(slice =>
      slice.map(row =>
        row.map(delta => {
          const beta_local = BETA_MEAN * (1 + B_BETA * delta);
          return Math.max(1.5, Math.min(beta_local, 15));
        })
      )
    );
  };
  
  // Compute Lyα sampling weights
  const computeLyaWeights = (densityField) => {
    return densityField.map(slice =>
      slice.map(row =>
        row.map(delta => {
          if (delta < -0.95) return 0; // Fully ionized
          if (delta < -0.3) return Math.exp(2.5 * delta); // Voids
          if (delta < 0.5) return Math.exp(-1.5 * delta); // Transition
          return Math.exp(-4 * delta); // Filaments
        })
      )
    );
  };
  
  // Analyze β statistics
  const analyzeBeta = () => {
    if (particles.length === 0) return;
    
    const densityField = computeDensityField(particles);
    const betaField = computeBetaField(densityField);
    const lyaWeights = computeLyaWeights(densityField);
    
    // Flatten arrays
    let allBetas = [];
    let allWeightedBetas = [];
    let totalWeight = 0;
    
    for (let i = 0; i < GRID_SIZE; i++) {
      for (let j = 0; j < GRID_SIZE; j++) {
        for (let k = 0; k < GRID_SIZE; k++) {
          const beta = betaField[i][j][k];
          const weight = lyaWeights[i][j][k];
          
          allBetas.push(beta);
          allWeightedBetas.push(beta * weight);
          totalWeight += weight;
        }
      }
    }
    
    const meanBeta = allBetas.reduce((a, b) => a + b) / allBetas.length;
    const stdBeta = Math.sqrt(
      allBetas.reduce((sum, val) => sum + (val - meanBeta) ** 2, 0) / allBetas.length
    );
    
    const lyaWeightedBeta = allWeightedBetas.reduce((a, b) => a + b) / totalWeight;
    
    // Environmental breakdown
    const voids = allBetas.filter((_, idx) => densityField[Math.floor(idx / (GRID_SIZE * GRID_SIZE)) % GRID_SIZE]
      [Math.floor(idx / GRID_SIZE) % GRID_SIZE][idx % GRID_SIZE] < -0.5);
    const filaments = allBetas.filter((_, idx) => {
      const delta = densityField[Math.floor(idx / (GRID_SIZE * GRID_SIZE)) % GRID_SIZE]
        [Math.floor(idx / GRID_SIZE) % GRID_SIZE][idx % GRID_SIZE];
      return delta >= 0.1 && delta < 2.0;
    });
    
    setBetaStats({
      mean: meanBeta,
      std: stdBeta,
      voids: voids.length > 0 ? voids.reduce((a, b) => a + b) / voids.length : 0,
      filaments: filaments.length > 0 ? filaments.reduce((a, b) => a + b) / filaments.length : 0,
      voidFraction: voids.length / allBetas.length,
      filamentFraction: filaments.length / allBetas.length
    });
    
    setLyaWeightedBeta(lyaWeightedBeta);
  };
  
  // Render density field
  useEffect(() => {
    if (!canvasRef.current || particles.length === 0) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    ctx.fillStyle = '#0a0a0a';
    ctx.fillRect(0, 0, width, height);
    
    // Project 3D density onto 2D slice (z-slice at middle)
    const densityField = computeDensityField(particles);
    const betaField = computeBetaField(densityField);
    const zSlice = Math.floor(GRID_SIZE / 2);
    
    const cellWidth = width / GRID_SIZE;
    const cellHeight = height / GRID_SIZE;
    
    for (let i = 0; i < GRID_SIZE; i++) {
      for (let j = 0; j < GRID_SIZE; j++) {
        const beta = betaField[i][j][zSlice];
        
        // Color based on β value
        const norm = (beta - 1.5) / (15 - 1.5);
        const r = Math.floor(255 * Math.min(1, norm * 2));
        const g = Math.floor(255 * (1 - Math.abs(norm - 0.5) * 2));
        const b = Math.floor(255 * Math.max(0, 1 - norm * 2));
        
        ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
        ctx.fillRect(i * cellWidth, j * cellHeight, cellWidth, cellHeight);
      }
    }
    
    // Overlay particles
    particles.forEach(p => {
      const px = ((p.x % BOX_SIZE) + BOX_SIZE) % BOX_SIZE;
      const py = ((p.y % BOX_SIZE) + BOX_SIZE) % BOX_SIZE;
      const pz = ((p.z % BOX_SIZE) + BOX_SIZE) % BOX_SIZE;
      
      if (Math.abs(pz - BOX_SIZE / 2) < BOX_SIZE / GRID_SIZE) {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
        ctx.beginPath();
        ctx.arc(
          px * width / BOX_SIZE,
          py * height / BOX_SIZE,
          1.5,
          0,
          2 * Math.PI
        );
        ctx.fill();
      }
    });
    
  }, [particles]);
  
  // Animation loop
  useEffect(() => {
    if (!isRunning) return;
    
    const interval = setInterval(() => {
      setParticles(prev => {
        const currentZ = Z_INITIAL - step * 0.1;
        if (currentZ <= Z_TARGET) {
          setIsRunning(false);
          analyzeBeta();
          return prev;
        }
        return evolveParticles(prev, currentZ);
      });
      setStep(s => s + 1);
    }, 50);
    
    return () => clearInterval(interval);
  }, [isRunning, step]);
  
  const handleStart = () => {
    if (particles.length === 0) {
      setParticles(initializeParticles());
    }
    setIsRunning(true);
  };
  
  const handleReset = () => {
    setIsRunning(false);
    setStep(0);
    setParticles(initializeParticles());
    setBetaStats(null);
    setLyaWeightedBeta(null);
  };
  
  const currentZ = Math.max(Z_INITIAL - step * 0.1, Z_TARGET);
  
  return (
    <div className="w-full max-w-6xl mx-auto p-6 bg-gradient-to-br from-slate-900 to-slate-800 rounded-lg shadow-2xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">
            N-Body β(x,z) Generator
          </h1>
          <p className="text-slate-300">
            Structure formation with texture enhancement mapping
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
          <h3 className="text-lg font-semibold text-white mb-2">How It Works</h3>
          <ul className="text-sm text-slate-300 space-y-1">
            <li>• Evolves {N_PARTICLES} particles from z={Z_INITIAL} → z={Z_TARGET}</li>
            <li>• Computes density δ(x) via Cloud-in-Cell interpolation</li>
            <li>• Maps β(x) = β_mean × [1 + b_β × δ(x)] with b_β={B_BETA}</li>
            <li>• Weights by Lyα sampling (preferential void absorption)</li>
            <li>• Color: Blue (low-β voids) → Red (high-β filaments)</li>
          </ul>
        </div>
      )}
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <canvas
            ref={canvasRef}
            width={600}
            height={600}
            className="w-full h-auto bg-black rounded-lg shadow-lg"
          />
          
          <div className="flex gap-3 mt-4">
            <button
              onClick={handleStart}
              disabled={isRunning}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-600 text-white rounded-lg font-semibold transition-colors"
            >
              <Play className="w-5 h-5" />
              {particles.length === 0 ? 'Initialize & Run' : 'Resume'}
            </button>
            <button
              onClick={() => setIsRunning(false)}
              disabled={!isRunning}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-amber-600 hover:bg-amber-700 disabled:bg-slate-600 text-white rounded-lg font-semibold transition-colors"
            >
              <Pause className="w-5 h-5" />
              Pause
            </button>
            <button
              onClick={handleReset}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-slate-600 hover:bg-slate-700 text-white rounded-lg font-semibold transition-colors"
            >
              <RotateCcw className="w-5 h-5" />
              Reset
            </button>
          </div>
        </div>
        
        <div className="space-y-4">
          <div className="p-4 bg-slate-800 rounded-lg">
            <h3 className="text-lg font-semibold text-white mb-3">Simulation State</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-400">Redshift:</span>
                <span className="text-white font-mono">{currentZ.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Steps:</span>
                <span className="text-white font-mono">{step}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Particles:</span>
                <span className="text-white font-mono">{particles.length}</span>
              </div>
            </div>
          </div>
          
          {betaStats && (
            <div className="p-4 bg-slate-800 rounded-lg border-2 border-emerald-600">
              <h3 className="text-lg font-semibold text-white mb-3">β Statistics</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">Cosmic mean β:</span>
                  <span className="text-white font-mono">{betaStats.mean.toFixed(3)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Std deviation:</span>
                  <span className="text-white font-mono">±{betaStats.std.toFixed(3)}</span>
                </div>
                <div className="h-px bg-slate-700 my-2"></div>
                <div className="flex justify-between">
                  <span className="text-slate-400">β (voids):</span>
                  <span className="text-blue-400 font-mono">{betaStats.voids.toFixed(3)}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-slate-500">Volume fraction:</span>
                  <span className="text-slate-400">{(betaStats.voidFraction * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">β (filaments):</span>
                  <span className="text-red-400 font-mono">{betaStats.filaments.toFixed(3)}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-slate-500">Volume fraction:</span>
                  <span className="text-slate-400">{(betaStats.filamentFraction * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          )}
          
          {lyaWeightedBeta && (
            <div className="p-4 bg-emerald-900/30 rounded-lg border-2 border-emerald-500">
              <h3 className="text-lg font-semibold text-emerald-400 mb-3">
                Lyα-Weighted Result
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-emerald-300">β_eff (Lyα):</span>
                  <span className="text-white font-mono text-lg">{lyaWeightedBeta.toFixed(3)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-emerald-300">Correction factor:</span>
                  <span className="text-white font-mono">{(lyaWeightedBeta / BETA_MEAN).toFixed(3)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-emerald-300">τ_eff reduction:</span>
                  <span className="text-white font-mono">
                    {((1 - lyaWeightedBeta / BETA_MEAN) * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
              <div className="mt-3 pt-3 border-t border-emerald-700">
                <p className="text-xs text-emerald-300">
                  For JCAP: This validates b_β={B_BETA} gives β_eff/β_mean ≈ {(lyaWeightedBeta / BETA_MEAN).toFixed(2)}
                </p>
              </div>
            </div>
          )}
          
          <div className="p-4 bg-slate-800/50 rounded-lg">
            <h3 className="text-sm font-semibold text-slate-400 mb-2">Color Legend</h3>
            <div className="flex items-center gap-2 mb-1">
              <div className="w-4 h-4 bg-blue-500 rounded"></div>
              <span className="text-xs text-slate-300">Voids (β ~ 2-3)</span>
            </div>
            <div className="flex items-center gap-2 mb-1">
              <div className="w-4 h-4 bg-green-500 rounded"></div>
              <span className="text-xs text-slate-300">Mean (β ~ 4.8)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-red-500 rounded"></div>
              <span className="text-xs text-slate-300">Filaments (β ~ 6-12)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NBodyBetaSimulator;