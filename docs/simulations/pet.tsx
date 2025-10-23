import React, { useRef, useEffect, useState } from 'react';
import { Play, Pause, RotateCcw } from 'lucide-react';

const PHYSICS = {
  ENERGY_DECAY: 0.0005,        // Much slower decay
  RESONANCE_GAIN: 0.001,       // Gain energy from resonance
  BASELINE_ENERGY: 0.0002,     // Ambient energy intake
  FEED_AMOUNT: 0.2,            // Click bonus
  COUPLING_STRENGTH: 0.5,
  COUPLING_RANGE: 150,
  DAMPING: 0.92,
  MIN_SPACING: 25,
  REPULSION: 200,
  MITOSIS_ENERGY: 0.75,        // Lower threshold
  MITOSIS_STABILITY: 80,       // Faster mitosis
  MAX_PARTICLES: 100,
  AGING_RATE: 0.00001,         // Very slow aging
  ELDERLY_AGE: 5000,           // Frames until considered old
};

export default function FractalPetCell() {
  const canvasRef = useRef(null);
  const [isRunning, setIsRunning] = useState(true);
  const [stats, setStats] = useState({ particles: 0, bonds: 0, energy: 0, stage: 'Identity', avgAge: 0 });
  
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
        age: 0,
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
    
    // Update phases and aging
    system.particles.forEach(p => {
      p.phase += p.frequency * dt;
      p.age += dt;
    });
    
    // Calculate forces and energy gains
    for (let i = 0; i < system.particles.length; i++) {
      const p1 = system.particles[i];
      let fx = 0, fy = 0;
      let resonanceEnergy = 0;
      
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
          
          // Gain energy from good resonance
          if (resonance > 0.5) {
            resonanceEnergy += PHYSICS.RESONANCE_GAIN * resonance * (p2.amplitude);
            
            // Frequency sync
            const sync = 0.01 * Math.sin(dPhase);
            p1.frequency += sync * p2.amplitude;
            p2.frequency -= sync * p1.amplitude;
            
            // Track strong bonds
            const bondKey = `${Math.min(p1.id, p2.id)}-${Math.max(p1.id, p2.id)}`;
            let bond = system.bonds.find(b => 
              (b.id1 === p1.id && b.id2 === p2.id) || (b.id1 === p2.id && b.id2 === p1.id)
            );
            
            if (resonance > 0.7) {
              if (!bond) {
                system.bonds.push({
                  id1: p1.id,
                  id2: p2.id,
                  strength: resonance,
                  age: 0,
                });
              } else {
                bond.strength = bond.strength * 0.95 + resonance * 0.05;
                bond.age++;
              }
            }
          }
        }
        
        // Repulsion at close range
        if (dist < PHYSICS.MIN_SPACING && dist > 0) {
          const repulsion = PHYSICS.REPULSION / Math.pow(dist + 1, 3);
          fx -= repulsion * dx / dist;
          fy -= repulsion * dy / dist;
        }
      }
      
      // Apply resonance energy gain
      p1.amplitude += resonanceEnergy;
      
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
    
    // Energy dynamics - baseline intake, decay with age
    system.particles.forEach(p => {
      // Ambient energy
      p.amplitude += PHYSICS.BASELINE_ENERGY * dt;
      
      // Aging increases decay rate
      const ageFactor = 1 + (p.age / PHYSICS.ELDERLY_AGE) * 0.5;
      p.amplitude -= PHYSICS.ENERGY_DECAY * ageFactor * dt;
      
      // Clamp amplitude
      p.amplitude = Math.max(0.1, Math.min(1.0, p.amplitude));
      
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
        if (p.amplitude > PHYSICS.MITOSIS_ENERGY && p.stability > PHYSICS.MITOSIS_STABILITY) {
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
            amplitude: p.amplitude * 0.7,
            memory: new Map(),
            stability: 0,
            age: 0, // New particle is young
          });
          
          p.amplitude *= 0.7;
          p.stability = 0;
        }
      });
    }
    
    // Natural pruning - very old, low energy particles fade
    system.particles = system.particles.filter(p => {
      if (p.age > PHYSICS.ELDERLY_AGE && p.amplitude < 0.2) {
        return false; // Let elderly low-energy particles go
      }
      return true;
    });
    
    // Prune weak bonds
    system.bonds = system.bonds.filter(bond => {
      bond.strength *= 0.99; // Decay
      return bond.strength > 0.3 && 
             system.particles.find(p => p.id === bond.id1) && 
             system.particles.find(p => p.id === bond.id2);
    });
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
    
    // Render bonds (Coupling visualization)
    system.bonds.forEach(bond => {
      const p1 = system.particles.find(p => p.id === bond.id1);
      const p2 = system.particles.find(p => p.id === bond.id2);
      if (!p1 || !p2) return;
      
      ctx.strokeStyle = `rgba(100, 255, 150, ${bond.strength * 0.4})`;
      ctx.lineWidth = 1 + bond.strength * 2;
      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.stroke();
    });
    
    // Render particles
    system.particles.forEach(p => {
      const radius = 5 + p.amplitude * 10;
      const pulse = Math.sin(p.phase) * 0.3 + 0.7;
      
      // Color shifts with age: young = blue, old = purple/red
      const ageFactor = Math.min(1, p.age / PHYSICS.ELDERLY_AGE);
      const hue = 200 - ageFactor * 80; // 200 (cyan-blue) to 120 (purple) to 40 (orange)
      const saturation = 70 + ageFactor * 20;
      
      // Glow
      const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, radius * 2);
      gradient.addColorStop(0, `hsla(${hue}, ${saturation}%, 60%, ${pulse})`);
      gradient.addColorStop(0.5, `hsla(${hue}, ${saturation}%, 50%, ${pulse * 0.5})`);
      gradient.addColorStop(1, `hsla(${hue}, ${saturation}%, 40%, 0)`);
      
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
        const avgAge = system.particles.length > 0 
          ? system.particles.reduce((sum, p) => sum + p.age, 0) / system.particles.length 
          : 0;
        
        // ICE stage detection
        let stage = 'Identity';
        if (system.particles.length === 0) {
          stage = 'Void';
        } else if (system.particles.length === 1 || system.bonds.length === 0) {
          stage = 'Identity';
        } else if (system.bonds.length < 10) {
          stage = 'Coupling';
        } else if (system.bonds.length < 30 || system.particles.length < 20) {
          stage = 'Field';
        } else if (system.particles.length < 60) {
          stage = 'Boundary';
        } else {
          stage = 'Organism';
        }
        
        setStats({
          particles: system.particles.length,
          bonds: system.bonds.length,
          energy: energy,
          stage: stage,
          avgAge: avgAge,
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
          <p className="text-slate-400 mb-2 text-xs">
            Your cell is self-sustaining! It gains energy from resonance. <strong>Click to give bonus energy</strong> and encourage growth.
          </p>
          <div className="grid grid-cols-5 gap-3 text-slate-300">
            <div>Stage: <span className="text-blue-400 font-bold">{stats.stage}</span></div>
            <div>Particles: <span className="text-blue-400">{stats.particles}</span></div>
            <div>Bonds: <span className="text-green-400">{stats.bonds}</span></div>
            <div>Energy: <span className="text-yellow-400">{stats.energy.toFixed(1)}</span></div>
            <div>Avg Age: <span className="text-purple-400">{stats.avgAge.toFixed(0)}</span></div>
          </div>
          <div className="mt-2 text-xs text-slate-500">
            Young = blue • Aging = purple • Elderly = orange • Green lines = bonds
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
