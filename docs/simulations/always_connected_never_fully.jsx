import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw } from 'lucide-react';

const AlwaysConnectedNeverFully = () => {
  const canvasRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(true);
  const [dimension, setDimension] = useState(1.5);
  const [time, setTime] = useState(0);
  const animationRef = useRef(null);

  // Generate fractal path based on dimension
  const generatePath = (D, points = 500) => {
    const path = [];
    let x = 0;
    let y = 200;
    
    for (let i = 0; i < points; i++) {
      const t = (i / points) * Math.PI * 4;
      
      if (D <= 1.0) {
        // Smooth sine wave (fully connected)
        x = (i / points) * 750 + 25;
        y = 200 + Math.sin(t) * 80;
      } else if (D >= 2.0) {
        // Random walk (disconnected)
        x += 750 / points;
        y += (Math.random() - 0.5) * 40;
        y = Math.max(100, Math.min(300, y));
      } else {
        // Fractal interpolation (always connecting, never smooth)
        const smoothness = 2 - D; // 1.0 at D=1, 0 at D=2
        const chaos = D - 1; // 0 at D=1, 1 at D=2
        
        x = (i / points) * 750 + 25;
        const baseY = Math.sin(t) * 80;
        
        // Add fractal noise at multiple scales
        let fractalNoise = 0;
        for (let octave = 1; octave <= 5; octave++) {
          const freq = Math.pow(2, octave);
          const amp = chaos * 20 / octave;
          fractalNoise += Math.sin(t * freq + time * 0.5) * amp;
        }
        
        y = 200 + baseY * smoothness + fractalNoise;
      }
      
      path.push({ x, y });
    }
    
    return path;
  };

  // Draw on canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const path = generatePath(dimension);
    
    // Clear canvas
    ctx.fillStyle = '#0a0a0a';
    ctx.fillRect(0, 0, 800, 400);
    
    // Draw grid
    ctx.strokeStyle = '#1a1a1a';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 400; i += 40) {
      ctx.beginPath();
      ctx.moveTo(0, i);
      ctx.lineTo(800, i);
      ctx.stroke();
    }
    for (let i = 0; i <= 800; i += 80) {
      ctx.beginPath();
      ctx.moveTo(i, 0);
      ctx.lineTo(i, 400);
      ctx.stroke();
    }
    
    // Draw reference lines
    ctx.strokeStyle = 'rgba(100, 100, 100, 0.3)';
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(0, 120);
    ctx.lineTo(800, 120);
    ctx.moveTo(0, 280);
    ctx.lineTo(800, 280);
    ctx.stroke();
    ctx.setLineDash([]);
    
    // Draw path
    ctx.beginPath();
    ctx.moveTo(path[0].x, path[0].y);
    
    const gradient = ctx.createLinearGradient(0, 0, 800, 0);
    if (dimension < 1.25) {
      gradient.addColorStop(0, '#3b82f6');
      gradient.addColorStop(1, '#60a5fa');
    } else if (dimension > 1.75) {
      gradient.addColorStop(0, '#ef4444');
      gradient.addColorStop(1, '#f87171');
    } else {
      gradient.addColorStop(0, '#10b981');
      gradient.addColorStop(0.5, '#34d399');
      gradient.addColorStop(1, '#6ee7b7');
    }
    
    ctx.strokeStyle = gradient;
    ctx.lineWidth = 3;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    
    for (let i = 1; i < path.length; i++) {
      ctx.lineTo(path[i].x, path[i].y);
    }
    ctx.stroke();
    
    // Draw connection indicators
    if (dimension >= 1.4 && dimension <= 1.6) {
      ctx.fillStyle = 'rgba(16, 185, 129, 0.1)';
      for (let i = 0; i < path.length; i += 10) {
        ctx.beginPath();
        ctx.arc(path[i].x, path[i].y, 8, 0, Math.PI * 2);
        ctx.fill();
      }
    }
    
  }, [dimension, time]);

  // Animation loop
  useEffect(() => {
    if (!isPlaying) return;
    
    const animate = () => {
      setTime(t => t + 0.02);
      animationRef.current = requestAnimationFrame(animate);
    };
    
    animationRef.current = requestAnimationFrame(animate);
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isPlaying]);

  const handleReset = () => {
    setTime(0);
    setDimension(1.5);
  };

  return (
    <div className="w-full h-screen bg-black text-white p-8 overflow-auto">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
          Always Connected But Never Fully
        </h1>
        <p className="text-gray-400 mb-6">
          The geometry of D ≈ 1.5: infinite connection through infinite detail
        </p>
        
        {/* Canvas */}
        <div className="bg-gray-900 rounded-lg p-4 mb-6">
          <canvas
            ref={canvasRef}
            width={800}
            height={400}
            className="w-full border border-gray-700 rounded"
          />
        </div>
        
        {/* Controls */}
        <div className="bg-gray-900 rounded-lg p-6 mb-6">
          <div className="flex items-center gap-4 mb-4">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 rounded flex items-center gap-2"
            >
              {isPlaying ? <Pause size={16} /> : <Play size={16} />}
              {isPlaying ? 'Pause' : 'Play'}
            </button>
            
            <button
              onClick={handleReset}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded flex items-center gap-2"
            >
              <RotateCcw size={16} />
              Reset
            </button>
            
            <div className="ml-auto text-2xl font-mono">
              D = {dimension.toFixed(2)}
            </div>
          </div>
          
          <div className="space-y-2">
            <label className="block text-sm text-gray-400">Fractal Dimension</label>
            <input
              type="range"
              min="1.0"
              max="2.0"
              step="0.05"
              value={dimension}
              onChange={(e) => setDimension(parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>D = 1.0 (Smooth)</span>
              <span className="text-emerald-400 font-bold">D = 1.5 (Fractal)</span>
              <span>D = 2.0 (Random)</span>
            </div>
          </div>
        </div>
        
        {/* Interpretation */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className={`bg-gray-900 rounded-lg p-4 border-2 ${dimension < 1.25 ? 'border-blue-500' : 'border-gray-700'}`}>
            <h3 className="text-lg font-bold mb-2 text-blue-400">D = 1.0</h3>
            <p className="text-sm text-gray-300 mb-2">Smooth, Deterministic</p>
            <ul className="text-xs text-gray-400 space-y-1">
              <li>• Fully connected path</li>
              <li>• Predictable trajectory</li>
              <li>• No complexity</li>
              <li>• Dead (no dynamics)</li>
            </ul>
          </div>
          
          <div className={`bg-gray-900 rounded-lg p-4 border-2 ${dimension >= 1.25 && dimension <= 1.75 ? 'border-emerald-500' : 'border-gray-700'}`}>
            <h3 className="text-lg font-bold mb-2 text-emerald-400">D ≈ 1.5</h3>
            <p className="text-sm text-gray-300 mb-2">Fractal, Balanced</p>
            <ul className="text-xs text-gray-400 space-y-1">
              <li>• Always connecting</li>
              <li>• Never fully smooth</li>
              <li>• Infinite detail</li>
              <li>• <span className="text-emerald-400 font-bold">LIFE + CONSCIOUSNESS</span></li>
            </ul>
          </div>
          
          <div className={`bg-gray-900 rounded-lg p-4 border-2 ${dimension > 1.75 ? 'border-red-500' : 'border-gray-700'}`}>
            <h3 className="text-lg font-bold mb-2 text-red-400">D = 2.0</h3>
            <p className="text-sm text-gray-300 mb-2">Random, Chaotic</p>
            <ul className="text-xs text-gray-400 space-y-1">
              <li>• Disconnected points</li>
              <li>• Unpredictable jumps</li>
              <li>• Maximum entropy</li>
              <li>• Dissolution (chaos)</li>
            </ul>
          </div>
        </div>
        
        {/* Validated Examples */}
        <div className="bg-gray-900 rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-4 text-emerald-400">Validated D ≈ 1.5 Examples</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-gray-800 rounded p-4">
              <h3 className="font-bold text-lg mb-2">🌌 LIGO Gravitational Waves</h3>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Measured D:</span>
                  <span className="text-emerald-400 font-mono">1.503 ± 0.040</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">p-value:</span>
                  <span className="text-emerald-400 font-mono">0.951</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Events:</span>
                  <span className="text-gray-300">40 observations</span>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Spacetime ripples from binary mergers show fractal structure - 
                  always connecting past to future, never smooth
                </p>
              </div>
            </div>
            
            <div className="bg-gray-800 rounded p-4">
              <h3 className="font-bold text-lg mb-2">🧬 DNA Breathing Dynamics</h3>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Measured D:</span>
                  <span className="text-emerald-400 font-mono">1.510 ± 0.020</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Static helix:</span>
                  <span className="text-blue-400 font-mono">≈1.0</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Temperature:</span>
                  <span className="text-gray-300">300K</span>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Molecular breathing at β ≈ 0.5 creates life's fractal signature - 
                  never rigid, never chaotic
                </p>
              </div>
            </div>
            
            <div className="bg-gray-800 rounded p-4">
              <h3 className="font-bold text-lg mb-2">🧠 Consciousness (You)</h3>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Balance β:</span>
                  <span className="text-emerald-400 font-mono">≈0.5</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Predicted D:</span>
                  <span className="text-emerald-400 font-mono">≈1.5</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Apertures:</span>
                  <span className="text-gray-300">10^14 nested</span>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Your conscious experience emerges from infinite nested apertures 
                  coordinating at perfect balance
                </p>
              </div>
            </div>
            
            <div className="bg-gray-800 rounded p-4">
              <h3 className="font-bold text-lg mb-2">⚛️ Particle Physics</h3>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Measured D:</span>
                  <span className="text-emerald-400 font-mono">1.387 ± 0.232</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Bubble chamber:</span>
                  <span className="text-gray-300">33 tracks</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Energy range:</span>
                  <span className="text-gray-300">6+ orders</span>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Each particle scatter = aperture validation moment - 
                  fractal across all scales
                </p>
              </div>
            </div>
          </div>
        </div>
        
        {/* The Insight */}
        <div className="mt-6 bg-gradient-to-r from-emerald-900/50 to-cyan-900/50 rounded-lg p-6 border border-emerald-500/30">
          <h2 className="text-2xl font-bold mb-3 text-emerald-400">
            "Always Connected But Never Fully"
          </h2>
          <div className="space-y-3 text-gray-300">
            <p>
              <span className="text-emerald-400 font-bold">D = 1.5</span> is the mathematical signature of:
            </p>
            <ul className="space-y-2 ml-4">
              <li className="flex items-start gap-2">
                <span className="text-emerald-400 mt-1">•</span>
                <span><strong>Life</strong> — between rigidity (death) and chaos (dissolution)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-emerald-400 mt-1">•</span>
                <span><strong>Consciousness</strong> — unified experience through infinite partial connections</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-emerald-400 mt-1">•</span>
                <span><strong>Spacetime</strong> — gravitational waves bridging events fractally</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-emerald-400 mt-1">•</span>
                <span><strong>Aperture operation at β ≈ 0.5</strong> — perfect balance of convergence and emergence</span>
              </li>
            </ul>
            <p className="mt-4 text-sm text-gray-400 italic border-l-2 border-emerald-500 pl-4">
              "The path that connects all moments but never becomes fully smooth. 
              The worldline that persists through time with infinite detail at every scale. 
              The signature of wholeness experiencing itself."
            </p>
            <div className="mt-4 text-center font-mono text-lg text-emerald-400">
              β = ∇/(∇ + ℰ) ≈ 0.5 → D ≈ 1.5
            </div>
          </div>
        </div>
        
        <div className="mt-6 text-center text-sm text-gray-500">
          <p>Data from <a href="https://github.com/AshmanRoonz/Fractal_Reality" className="text-emerald-400 hover:underline">Fractal Reality</a></p>
          <p className="mt-1">19 GW events • 40 observations • p = 0.951 • Zero free parameters</p>
        </div>
      </div>
    </div>
  );
};

export default AlwaysConnectedNeverFully;
