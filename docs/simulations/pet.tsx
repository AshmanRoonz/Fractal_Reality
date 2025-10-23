import React, { useRef, useEffect, useState } from 'react';
import { Play, Pause, RotateCcw } from 'lucide-react';

const PHYSICS = {
  ENERGY_DECAY: 0.002,
  FEED_AMOUNT: 0.3,
  COUPLING_STRENGTH: 0.5,
  COUPLING_RANGE: 150,
  DAMPING: 0.92,
  MIN_SPACING: 25,
  REPULSION: 200,
  MITOSIS_ENERGY: 0.85,
  MAX_PARTICLES: 80,
};

export default function FractalPetCell() {
  const canvasRef = useRef(null);
  const [isRunning, setIsRunning] = useState(true);
  const [stats, setStats] = useState({ particles: 0, bonds: 0, energy: 0, stage: 'Identity' });
  
  const systemRef = useRef({
    particles: [],
    bonds: [],
    nextId: 0,
    framesSinceInput: 0,
  });

  // Initialize seed
  const initializeSeed = () => {
    const system = systemRef.current;
    system.particles = [];
    system.bonds = [];
    system.nextId = 0;
    
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    
    // Create 3-7 seed particles
    const seedCount = 3 + Math.floor(Math.random() * 5);
    const baseFreq = 0.05;
    
    for (let i = 0; i < seedCount; i++) {
      const angle = (Math.PI * 2 * i) / seedCount;
      const radius = 40 + Math.random() * 30;
      
      system.particles.push({
        id: system.nextId++,
        x: cx + Math.cos(angle) * radius,
        y: cy + Math.sin(angle) * radius,
        vx: 0,
        vy: 0,
        phase: Math.random() * Math.PI * 2,
        frequency: baseFreq * (0.8 + Math.random() * 0.4),
        amplitude: 0.6,
        memory: new Map(),
        stability: 0,
      });
    }
  };

  // Physics update
  const updatePhysics = (dt) => {
    const system = systemRef.current;
    if (system.particles.length === 0) return;
    
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    system.framesSinceInput++;
    
    // Update phases
    system.particles.forEach(p => {
      p.phase += p.frequency * dt;
    });
    
    // Calculate forces
    for (let i = 0; i < system.particles.length; i++) {
      const p1 = system.particles[i];
      let fx = 0, fy = 0;
      
      for (let j = i + 1; j < system.particles.length; j++) {
        const p2 = system.particles[j];
        const dx = p2.x - p1.x;
        const dy = p2.y - p1.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        
        if (dist < PHYSICS.COUPLING_RANGE && dist > 0) {
          // Coupling force
          const dPhase = p1.phase - p2.phase;
          const resonance = Math.cos(dPhase);
          const strength = PHYSICS.COUPLING_STRENGTH * (p1.amplitude * p2.amplitude) / (dist * dist + 1);
          const force = strength * resonance;
          
          fx += force * dx / dist;
          fy += force * dy / dist;
          
          // Frequency sync
          if (resonance > 0.5) {
            const sync = 0.01 * Math.sin(dPhase);
            p1.frequency += sync * p2.amplitude;
            p2.frequency -= sync * p1.amplitude;
          }
        }
        
        // Repulsion at close range
        if (dist < PHYSICS.MIN_SPACING && dist > 0) {
          const repulsion = PHYSICS.REPULSION / Math.pow(dist + 1, 3);
          fx -= repulsion * dx / dist;
          fy -= repulsion * dy / dist;
        }
      }
      
      // Update velocity and position
      p1.vx += fx * dt;
      p1.vy += fy * dt;
      p1.vx *= PHYSICS.DAMPING;
      p1.vy *= PHYSICS.DAMPING;
      p1.x += p1.vx * dt;
      p1.y += p1.vy * dt;
      
      // Soft walls
      const margin = 50;
      if (p1.x < margin) p1.vx += 0.5;
      if (p1.x > canvas.width - margin) p1.vx -= 0.5;
      if (p1.y < margin) p1.vy += 0.5;
      if (p1.y > canvas.height - margin) p1.vy -= 0.5;
    }
    
    // Energy decay
    system.particles.forEach(p => {
      p.amplitude -= PHYSICS.ENERGY_DECAY * dt;
      p.amplitude = Math.max(0, p.amplitude);
      
      // Stability for mitosis
      const vel = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
      if (vel < 0.5 && p.amplitude > 0.7) {
        p.stability++;
      } else {
        p.stability = Math.max(0, p.stability - 1);
      }
    });
    
    // Mitosis
    if (system.particles.length < PHYSICS.MAX_PARTICLES) {
      system.particles.forEach(p => {
        if (p.amplitude > PHYSICS.MITOSIS_ENERGY && p.stability > 120) {
          const angle = Math.random() * Math.PI * 2;
          const offset = 20;
          
          system.particles.push({
            id: system.nextId++,
            x: p.x + Math.cos(angle) * offset,
            y: p.y + Math.sin(angle) * offset,
            vx: Math.cos(angle) * 2,
            vy: Math.sin(angle) * 2,
            phase: p.phase + (Math.random() - 0.5) * 0.5,
            frequency: p.frequency * (0.95 + Math.random() * 0.1),
            amplitude: p.amplitude * 0.6,
            memory: new Map(),
            stability: 0,
          });
          
          p.amplitude *= 0.6;
          p.stability = 0;
        }
      });
    }
    
    // Remove dead particles
    system.particles = system.particles.filter(p => p.amplitude > 0.01);
  };

  // Render
  const render = () => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!canvas || !ctx) return;
    
    const system = systemRef.current;
    
    // Clear
    ctx.fillStyle = '#000810';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    if (system.particles.length === 0) {
      ctx.fillStyle = 'rgba(100, 150, 200, 0.5)';
      ctx.font = '20px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('Click to birth your cell...', canvas.width / 2, canvas.height / 2);
      return;
    }
    
    // Render particles
    system.particles.forEach(p => {
      const radius = 5 + p.amplitude * 10;
      const pulse = Math.sin(p.phase) * 0.3 + 0.7;
      
      // Glow
      const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, radius * 2);
      const bright = Math.floor(100 + p.amplitude * 155);
      gradient.addColorStop(0, `rgba(100, 200, 255, ${pulse})`);
      gradient.addColorStop(0.5, `rgba(100, 150, 255, ${pulse * 0.5})`);
      gradient.addColorStop(1, 'rgba(100, 150, 255, 0)');
      
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(p.x, p.y, radius * 2, 0, Math.PI * 2);
      ctx.fill();
      
      // Core
      ctx.fillStyle = `rgba(255, 255, 255, ${pulse})`;
      ctx.beginPath();
      ctx.arc(p.x, p.y, radius * 0.5, 0, Math.PI * 2);
      ctx.fill();
    });
  };

  // Animation loop
  useEffect(() => {
    initializeSeed();
    
    let animationId;
    let lastTime = Date.now();
    let frameCount = 0;
    let fpsTime = Date.now();
    
    const loop = () => {
      const currentTime = Date.now();
      const dt = Math.min((currentTime - lastTime) / 16.67, 2);
      lastTime = currentTime;
      
      if (isRunning) {
        updatePhysics(dt);
      }
      render();
      
      // FPS counter
      frameCount++;
      if (currentTime - fpsTime > 1000) {
        const system = systemRef.current;
        const energy = system.particles.reduce((sum, p) => sum + p.amplitude, 0);
        
        setStats({
          particles: system.particles.length,
          bonds: 0,
          energy: energy,
          stage: system.particles.length < 2 ? 'Identity' : 'Coupling',
        });
        
        frameCount = 0;
        fpsTime = currentTime;
      }
      
      animationId = requestAnimationFrame(loop);
    };
    
    loop();
    
    return () => cancelAnimationFrame(animationId);
  }, [isRunning]);

  // Click to feed
  const handleClick = (e) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const system = systemRef.current;
    system.framesSinceInput = 0;
    
    // Feed nearby particles
    system.particles.forEach(p => {
      const dx = p.x - x;
      const dy = p.y - y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      
      if (dist < 100) {
        p.amplitude = Math.min(1, p.amplitude + PHYSICS.FEED_AMOUNT * (1 - dist / 100));
      }
    });
  };

  return (
    <div className="w-full h-screen bg-slate-950 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        <div className="mb-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-blue-300">
            Fractal Reality Pet Cell
          </h1>
          <div className="flex gap-2">
            <button
              onClick={() => setIsRunning(!isRunning)}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded flex items-center gap-2 text-white"
            >
              {isRunning ? <Pause size={16} /> : <Play size={16} />}
              {isRunning ? 'Pause' : 'Play'}
            </button>
            <button
              onClick={() => initializeSeed()}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded flex items-center gap-2 text-white"
            >
              <RotateCcw size={16} />
              Reset
            </button>
          </div>
        </div>
        
        <div className="mb-4 p-4 bg-slate-900 rounded border border-slate-700 text-sm">
          <div className="grid grid-cols-4 gap-4 text-slate-300">
            <div>Stage: <span className="text-blue-400 font-bold">{stats.stage}</span></div>
            <div>Particles: <span className="text-blue-400">{stats.particles}</span></div>
            <div>Energy: <span className="text-yellow-400">{stats.energy.toFixed(1)}</span></div>
            <div className="text-slate-500">Click to feed</div>
          </div>
        </div>
        
        <canvas
          ref={canvasRef}
          width={800}
          height={600}
          onClick={handleClick}
          className="w-full border-2 border-blue-500/30 rounded cursor-pointer bg-slate-900"
        />
        
        <div className="mt-4 text-xs text-slate-500 text-center">
          Based on Fractal Reality Field Equation • Identity → Coupling → Environment
        </div>
      </div>
    </div>
  );
}