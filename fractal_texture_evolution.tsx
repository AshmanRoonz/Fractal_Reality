import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw, Info } from 'lucide-react';

const FractalTextureEvolution = () => {
  const canvasRef = useRef(null);
  const [isRunning, setIsRunning] = useState(false);
  const [time, setTime] = useState(0);
  const [showInfo, setShowInfo] = useState(true);
  
  // Physical constants (Planck units, c=G=ℏ=1)
  const l_P = 1.0;  // Planck length
  const t_P = 1.0;  // Planck time
  const rho_P = 1.0; // Planck density
  
  // Simulation parameters
  const numScales = 7; // From Planck to cosmic
  const scaleFactors = [1, 10, 100, 1000, 10000, 100000, 1000000];
  
  // State for each fractal level
  const [scales, setScales] = useState(() => 
    scaleFactors.map((L, i) => ({
      L: L * l_P,
      rho_texture: 0,
      Lambda: 0,
      validationRate: 0,
      quantumNoise: 0,
      operators: [],
      label: ['Planck', 'Quantum', 'Atomic', 'Molecular', 'Macro', 'Astro', 'Cosmic'][i]
    }))
  );
  
  // Initialize operators at each scale
  useEffect(() => {
    setScales(prevScales => prevScales.map((scale, idx) => {
      const numOps = Math.max(3, Math.floor(20 / (idx + 1)));
      const ops = Array.from({ length: numOps }, (_, i) => ({
        id: i,
        phase: Math.random() * 2 * Math.PI,
        amplitude: 0.5 + Math.random() * 0.5,
        validated: false,
        textureLocal: 0
      }));
      return { ...scale, operators: ops };
    }));
  }, []);
  
  // Self-consistent evolution step
  const evolveStep = (dt) => {
    setScales(prevScales => {
      const newScales = [...prevScales];
      
      // Step 1: Evolve operators and validate patterns
      newScales.forEach((scale, idx) => {
        const L = scale.L;
        const rho = scale.rho_texture;
        
        // Validation rate scales with √|g_tt| ≈ √(1 + 8πG·rho)
        const g_tt = 1 + 8 * Math.PI * rho / L;
        const valRate = Math.sqrt(Math.abs(g_tt));
        
        // Quantum noise: σ ∝ √ρ (from file)
        const sigma = Math.sqrt(rho + 1e-10);
        const xi = (Math.random() - 0.5) * 2; // Noise [-1,1]
        const quantumNoise = sigma * xi;
        
        // Update each operator
        scale.operators.forEach(op => {
          // Phase evolution affected by texture density and quantum noise
          const omega = 1.0 + 0.1 * rho / rho_P + 0.05 * quantumNoise;
          op.phase += omega * dt;
          
          // Validation check: passes [ICE] if phase crosses threshold
          const prevValidated = op.validated;
          op.validated = Math.sin(op.phase) > 0.8;
          
          // If newly validated, create texture
          if (op.validated && !prevValidated) {
            op.textureLocal += op.amplitude * valRate * dt;
          }
        });
        
        scale.validationRate = valRate;
        scale.quantumNoise = quantumNoise;
      });
      
      // Step 2: Accumulate texture density from all operators
      newScales.forEach((scale, idx) => {
        const L = scale.L;
        const volume = L * L * L;
        
        // Sum texture from operators at this scale
        let textureSum = 0;
        scale.operators.forEach(op => {
          textureSum += op.textureLocal;
        });
        
        // Average over volume + contributions from nested scales below
        let totalTexture = textureSum;
        
        // Add contribution from all finer scales (fractal nesting)
        for (let j = 0; j < idx; j++) {
          const finerScale = newScales[j];
          const nestingFactor = Math.pow(L / finerScale.L, 3);
          totalTexture += finerScale.rho_texture * volume / nestingFactor;
        }
        
        // Update density
        scale.rho_texture = totalTexture / volume;
      });
      
      // Step 3: Calculate effective Λ at each scale
      newScales.forEach(scale => {
        const L = scale.L;
        const rho = scale.rho_texture;
        
        // From file: Λ ∝ ρ/L² with quantum enhancement β~5
        const beta = 5.0;
        const Lambda_base = (8 * Math.PI * rho) / (L * L);
        
        // Quantum enhancement
        const sigma = Math.sqrt(rho + 1e-10);
        const enhancement = 1 + beta * sigma / Math.sqrt(rho_P);
        
        scale.Lambda = Lambda_base * enhancement;
      });
      
      return newScales;
    });
    
    setTime(t => t + dt);
  };
  
  // Animation loop
  useEffect(() => {
    if (!isRunning) return;
    
    const interval = setInterval(() => {
      evolveStep(0.1);
    }, 50);
    
    return () => clearInterval(interval);
  }, [isRunning]);
  
  // Visualization
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear
    ctx.fillStyle = '#0a0a0a';
    ctx.fillRect(0, 0, width, height);
    
    // Draw each scale level
    const levelHeight = height / numScales;
    
    scales.forEach((scale, idx) => {
      const y = idx * levelHeight;
      
      // Background for this scale
      const alpha = Math.min(0.3, scale.rho_texture / rho_P);
      ctx.fillStyle = `rgba(100, 50, 200, ${alpha})`;
      ctx.fillRect(0, y, width, levelHeight);
      
      // Draw operators
      const opWidth = width / (scale.operators.length + 1);
      scale.operators.forEach((op, i) => {
        const x = (i + 1) * opWidth;
        const cy = y + levelHeight / 2;
        
        // Operator circle
        const radius = 8 + op.textureLocal * 5;
        const hue = op.validated ? 120 : 200;
        ctx.fillStyle = `hsl(${hue}, 70%, 50%)`;
        ctx.beginPath();
        ctx.arc(x, cy, radius, 0, 2 * Math.PI);
        ctx.fill();
        
        // Phase indicator
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.6)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(x, cy);
        ctx.lineTo(
          x + Math.cos(op.phase) * radius,
          cy + Math.sin(op.phase) * radius
        );
        ctx.stroke();
      });
      
      // Scale label and metrics
      ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
      ctx.font = '12px monospace';
      ctx.fillText(scale.label, 10, y + 20);
      
      ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
      ctx.font = '10px monospace';
      ctx.fillText(`ρ: ${scale.rho_texture.toExponential(2)}`, 10, y + 35);
      ctx.fillText(`Λ: ${scale.Lambda.toExponential(2)}`, 10, y + 50);
      
      // Quantum noise indicator
      const noiseX = width - 60;
      const noiseBar = Math.abs(scale.quantumNoise) * 20;
      ctx.fillStyle = scale.quantumNoise > 0 ? 
        'rgba(255, 100, 100, 0.6)' : 'rgba(100, 100, 255, 0.6)';
      ctx.fillRect(noiseX, y + levelHeight/2 - noiseBar/2, 5, noiseBar);
      
      // Divider line
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(0, y + levelHeight);
      ctx.lineTo(width, y + levelHeight);
      ctx.stroke();
    });
    
    // Time display
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
    ctx.font = '14px monospace';
    ctx.fillText(`Time: ${time.toFixed(1)} t_P`, width - 150, 20);
    
  }, [scales, time]);
  
  const reset = () => {
    setTime(0);
    setIsRunning(false);
    setScales(prevScales => prevScales.map(scale => ({
      ...scale,
      rho_texture: 0,
      Lambda: 0,
      validationRate: 0,
      quantumNoise: 0,
      operators: scale.operators.map(op => ({
        ...op,
        phase: Math.random() * 2 * Math.PI,
        textureLocal: 0,
        validated: false
      }))
    })));
  };
  
  return (
    <div className="w-full h-full bg-gray-900 text-white p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold">
            Fractal Texture Self-Consistent Evolution
          </h1>
          <button
            onClick={() => setShowInfo(!showInfo)}
            className="p-2 bg-gray-800 rounded hover:bg-gray-700"
          >
            <Info size={20} />
          </button>
        </div>
        
        {showInfo && (
          <div className="mb-4 p-4 bg-gray-800 rounded text-sm space-y-2">
            <p><strong>Self-Consistent Loop:</strong></p>
            <p>1. Operators validate → create texture ∞'</p>
            <p>2. Texture density ρ accumulates fractally</p>
            <p>3. ρ affects validation rate ∝ √|g_tt|</p>
            <p>4. ρ creates Λ ∝ ρ/L² with quantum enhancement β~5</p>
            <p>5. Quantum noise σ ∝ √ρ feeds back to operator evolution</p>
            <p className="text-yellow-400 mt-2">
              Green circles = validated (creating texture) | Blue = unvalidated
            </p>
            <p className="text-purple-400">
              Background intensity = texture density | Side bars = quantum noise
            </p>
          </div>
        )}
        
        <div className="mb-4 flex gap-4">
          <button
            onClick={() => setIsRunning(!isRunning)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 rounded hover:bg-blue-700"
          >
            {isRunning ? <Pause size={20} /> : <Play size={20} />}
            {isRunning ? 'Pause' : 'Start'}
          </button>
          <button
            onClick={reset}
            className="flex items-center gap-2 px-4 py-2 bg-gray-700 rounded hover:bg-gray-600"
          >
            <RotateCcw size={20} />
            Reset
          </button>
        </div>
        
        <canvas
          ref={canvasRef}
          width={1000}
          height={700}
          className="w-full border border-gray-700 rounded"
        />
        
        <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
          <div className="p-3 bg-gray-800 rounded">
            <div className="font-bold mb-2">Cosmic Scale</div>
            <div>Λ = {scales[6]?.Lambda.toExponential(3)} m⁻²</div>
            <div className="text-gray-400">Observed: ~10⁻⁵² m⁻²</div>
          </div>
          <div className="p-3 bg-gray-800 rounded">
            <div className="font-bold mb-2">Planck Scale</div>
            <div>ρ = {scales[0]?.rho_texture.toExponential(3)}</div>
            <div className="text-gray-400">Max fractal depth</div>
          </div>
          <div className="p-3 bg-gray-800 rounded">
            <div className="font-bold mb-2">Total Validations</div>
            <div>
              {scales.reduce((sum, s) => 
                sum + s.operators.filter(o => o.validated).length, 0
              )} active
            </div>
            <div className="text-gray-400">Creating texture now</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FractalTextureEvolution;