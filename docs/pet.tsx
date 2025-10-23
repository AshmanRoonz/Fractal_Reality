import React, { useRef, useEffect, useState } from 'react';
import { Play, Pause, RotateCcw, Info } from 'lucide-react';

// Physics constants - tune these through experimentation
const PHYSICS = {
  // Energy dynamics
  ENERGY_DECAY_RATE: 0.002,
  STARVATION_THRESHOLD: 0.15,
  DEATH_GRACE_PERIOD: 300,
  FEED_AMOUNT: 0.3,
  
  // Coupling and resonance
  COUPLING_STRENGTH: 0.5,
  COUPLING_RANGE: 150,
  PHASE_LEARNING_RATE: 0.05,
  FREQUENCY_LEARNING_RATE: 0.01,
  
  // Hebbian learning
  HEBBIAN_LEARNING_RATE: 0.015,
  WEIGHT_DECAY_RATE: 0.008,
  PRUNING_THRESHOLD: 0.15,
  BOND_FORMATION_THRESHOLD: 0.7,
  
  // Growth
  MITOSIS_ENERGY: 0.85,
  MITOSIS_STABILITY: 120,
  STRESS_NUCLEATION_THRESHOLD: 0.75,
  MAX_PARTICLES: 80,
  
  // Movement
  DAMPING: 0.92,
  MIN_SPACING: 25,
  REPULSION_STRENGTH: 200,
  
  // ICE transitions
  COUPLING_THRESHOLD: 0.75,
  FIELD_VARIANCE_THRESHOLD: 0.25,
  BOUNDARY_COHERENCE: 0.65,
  
  // Consciousness
  CONSCIOUSNESS_DECAY: 0.95,
  ATTENTION_SPAN: 60,
};

interface Particle {
  id: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  phase: number;
  frequency: number;
  amplitude: number;
  fieldDensity: number;
  memory: Map<number, { resonance: number, duration: number }>;
  stabilityCounter: number;
  consciousness: number;
  age: number;
}

interface Bond {
  id1: number;
  id2: number;
  weight: number;
  duration: number;
  resonanceHistory: number[];
}

const FractalPetCell: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isRunning, setIsRunning] = useState(true);
  const [showInfo, setShowInfo] = useState(true);
  const [stats, setStats] = useState({
    particles: 0,
    bonds: 0,
    energy: 0,
    fps: 60,
    stage: 'Identity'
  });
  
  // System state
  const systemRef = useRef({
    particles: [] as Particle[],
    bonds: [] as Bond[],
    nextId: 0,
    framesSinceInput: 0,
    deathTimer: 0,
    isDead: false,
    fieldGrid: [] as number[][],
    consciousnessThreshold: 0.3,
    targetFPS: 60,
    lastFrameTime: Date.now(),
    frameCount: 0,
  });

  // Initialize with random seed
  const initializeSeed = () => {
    const system = systemRef.current;
    system.particles = [];
    system.bonds = [];
    system.nextId = 0;
    system.deathTimer = 0;
    system.isDead = false;
    system.framesSinceInput = 0;
    
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    
    // Random seed: 3-7 particles
    const seedCount = 3 + Math.floor(Math.random() * 5);
    const baseFreq = 0.05 + Math.random() * 0.05;
    
    for (let i = 0; i < seedCount; i++) {
      const angle = (Math.PI * 2 * i) / seedCount;
      const radius = 30 + Math.random() * 40;
      
      system.particles.push({
        id: system.nextId++,
        x: cx + Math.cos(angle) * radius,
        y: cy + Math.sin(angle) * radius,
        vx: 0,
        vy: 0,
        phase: Math.random() * Math.PI * 2,
        frequency: baseFreq * (0.8 + Math.random() * 0.4),
        amplitude: 0.5 + Math.random() * 0.2,
        fieldDensity: 1.0 + (Math.random() - 0.5) * 0.2,
        memory: new Map(),
        stabilityCounter: 0,
        consciousness: 0.5,
        age: 0,
      });
    }
    
    // Initialize field grid
    const gridSize = 20;
    system.fieldGrid = Array(gridSize).fill(0).map(() => 
      Array(gridSize).fill(1.0)
    );
  };

  // Physics update
  const updatePhysics = (dt: number) => {
    const system = systemRef.current;
    if (system.isDead || system.particles.length === 0) return;
    
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    system.framesSinceInput++;
    const neglectMultiplier = 1 + (system.framesSinceInput / 10000);
    
    // Update particle phases and consciousness
    system.particles.forEach(p => {
      p.phase += p.frequency * dt;
      p.age++;
      p.consciousness *= PHYSICS.CONSCIOUSNESS_DECAY;
    });
    
    // Calculate coupling forces and resonance
    for (let i = 0; i < system.particles.length; i++) {
      const p1 = system.particles[i];
      let fx = 0, fy = 0;
      
      for (let j = i + 1; j < system.particles.length; j++) {
        const p2 = system.particles[j];
        const dx = p2.x - p1.x;
        const dy = p2.y - p1.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        
        if (dist < PHYSICS.COUPLING_RANGE && dist > 0) {
          // Phase difference and resonance quality
          const dPhase = p1.phase - p2.phase;
          const dFreq = Math.abs(p1.frequency - p2.frequency);
          const resonance = Math.cos(dPhase) * Math.exp(-dFreq / 0.02);
          
          // Coupling force (in phase attracts, out of phase repels)
          const couplingStrength = PHYSICS.COUPLING_STRENGTH * 
            (p1.amplitude * p2.amplitude) / (dist * dist + 1);
          const force = couplingStrength * resonance;
          
          fx += force * dx / dist;
          fy += force * dy / dist;
          
          // Frequency synchronization (Hebbian at physics level)
          if (resonance > 0.5) {
            const freqPull = PHYSICS.FREQUENCY_LEARNING_RATE * 
              Math.sin(dPhase) * (1 / (dist + 10));
            p1.frequency += freqPull * p2.amplitude;
            p2.frequency -= freqPull * p1.amplitude;
            
            // Boost consciousness for resonant particles
            p1.consciousness = Math.min(1, p1.consciousness + 0.02 * resonance);
            p2.consciousness = Math.min(1, p2.consciousness + 0.02 * resonance);
          }
          
          // Update or create bond
          const bondKey = `${Math.min(p1.id, p2.id)}-${Math.max(p1.id, p2.id)}`;
          let bond = system.bonds.find(b => 
            (b.id1 === p1.id && b.id2 === p2.id) || 
            (b.id1 === p2.id && b.id2 === p1.id)
          );
          
          if (resonance > PHYSICS.BOND_FORMATION_THRESHOLD) {
            if (!bond) {
              bond = {
                id1: p1.id,
                id2: p2.id,
                weight: 0.1,
                duration: 0,
                resonanceHistory: []
              };
              system.bonds.push(bond);
            }
            
            // Hebbian learning
            bond.weight = Math.min(1, bond.weight + 
              PHYSICS.HEBBIAN_LEARNING_RATE * resonance * 
              (p1.amplitude * p2.amplitude));
            bond.duration++;
            bond.resonanceHistory.push(resonance);
            if (bond.resonanceHistory.length > 100) {
              bond.resonanceHistory.shift();
            }
            
            // Update memory
            if (!p1.memory.has(p2.id)) {
              p1.memory.set(p2.id, { resonance: 0, duration: 0 });
            }
            const mem1 = p1.memory.get(p2.id)!;
            mem1.resonance = mem1.resonance * 0.95 + resonance * 0.05;
            mem1.duration++;
            
            if (!p2.memory.has(p1.id)) {
              p2.memory.set(p1.id, { resonance: 0, duration: 0 });
            }
            const mem2 = p2.memory.get(p1.id)!;
            mem2.resonance = mem2.resonance * 0.95 + resonance * 0.05;
            mem2.duration++;
          }
        }
        
        // Repulsion at close range (collision avoidance)
        if (dist < PHYSICS.MIN_SPACING && dist > 0) {
          const repulsion = PHYSICS.REPULSION_STRENGTH / 
            Math.pow(dist - PHYSICS.MIN_SPACING + 1, 3);
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
      
      // Boundary conditions (soft walls)
      const margin = 50;
      if (p1.x < margin) p1.vx += 0.5;
      if (p1.x > canvas.width - margin) p1.vx -= 0.5;
      if (p1.y < margin) p1.vy += 0.5;
      if (p1.y > canvas.height - margin) p1.vy -= 0.5;
    }
    
    // Energy decay
    system.particles.forEach(p => {
      p.amplitude -= PHYSICS.ENERGY_DECAY_RATE * neglectMultiplier * dt;
      p.amplitude = Math.max(0, p.amplitude);
      
      // Stability counter for mitosis
      const avgVelocity = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
      if (avgVelocity < 0.5 && p.amplitude > 0.7) {
        p.stabilityCounter++;
      } else {
        p.stabilityCounter = Math.max(0, p.stabilityCounter - 1);
      }
    });
    
    // Synaptic pruning
    system.bonds = system.bonds.filter(bond => {
      bond.weight -= PHYSICS.WEIGHT_DECAY_RATE * dt;
      return bond.weight > PHYSICS.PRUNING_THRESHOLD;
    });
    
    // Check for mitosis
    if (system.particles.length < PHYSICS.MAX_PARTICLES) {
      system.particles.forEach(p => {
        if (p.amplitude > PHYSICS.MITOSIS_ENERGY && 
            p.stabilityCounter > PHYSICS.MITOSIS_STABILITY) {
          // Divide
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
            fieldDensity: p.fieldDensity,
            memory: new Map(),
            stabilityCounter: 0,
            consciousness: p.consciousness * 0.5,
            age: 0,
          });
          
          p.amplitude *= 0.6;
          p.stabilityCounter = 0;
          p.vx = -Math.cos(angle) * 2;
          p.vy = -Math.sin(angle) * 2;
        }
      });
    }
    
    // Check for death
    const totalEnergy = system.particles.reduce((sum, p) => sum + p.amplitude, 0);
    if (totalEnergy < PHYSICS.STARVATION_THRESHOLD * system.particles.length) {
      system.deathTimer++;
      if (system.deathTimer > PHYSICS.DEATH_GRACE_PERIOD) {
        system.isDead = true;
      }
    } else {
      system.deathTimer = Math.max(0, system.deathTimer - 2);
    }
    
    // Remove dead particles
    system.particles = system.particles.filter(p => p.amplitude > 0.01);
    
    // Self-regulate based on FPS
    const currentFPS = stats.fps;
    if (currentFPS < 45 && system.particles.length > 5) {
      system.consciousnessThreshold += 0.01;
    } else if (currentFPS > 55 && system.consciousnessThreshold > 0.1) {
      system.consciousnessThreshold -= 0.005;
    }
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
    
    if (system.isDead) {
      ctx.fillStyle = 'rgba(100, 100, 150, 0.5)';
      ctx.font = '24px monospace';
      ctx.textAlign = 'center';
      ctx.fillText('Cell has dissolved...', canvas.width / 2, canvas.height / 2);
      ctx.font = '16px monospace';
      ctx.fillText('Click Reset to birth a new cell', canvas.width / 2, canvas.height / 2 + 30);
      return;
    }
    
    // Calculate field density (simple version)
    const gridSize = 30;
    const cellSize = canvas.width / gridSize;
    const field: number[][] = Array(gridSize).fill(0).map(() => Array(gridSize).fill(0));
    
    system.particles.forEach(p => {
      const gx = Math.floor(p.x / cellSize);
      const gy = Math.floor(p.y / cellSize);
      if (gx >= 0 && gx < gridSize && gy >= 0 && gy < gridSize) {
        field[gx][gy] += p.amplitude * p.fieldDensity;
      }
    });
    
    // Render field (E stage visualization)
    for (let x = 0; x < gridSize; x++) {
      for (let y = 0; y < gridSize; y++) {
        if (field[x][y] > 0.1) {
          const alpha = Math.min(0.15, field[x][y] * 0.1);
          ctx.fillStyle = `rgba(100, 150, 255, ${alpha})`;
          ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
        }
      }
    }
    
    // Render bonds (C stage visualization)
    system.bonds.forEach(bond => {
      const p1 = system.particles.find(p => p.id === bond.id1);
      const p2 = system.particles.find(p => p.id === bond.id2);
      if (!p1 || !p2) return;
      
      // Only render if both particles are "conscious"
      if (p1.consciousness < system.consciousnessThreshold && 
          p2.consciousness < system.consciousnessThreshold) return;
      
      const avgResonance = bond.resonanceHistory.length > 0 ?
        bond.resonanceHistory.reduce((a, b) => a + b, 0) / bond.resonanceHistory.length : 0;
      
      // Color based on phase relationship
      const dPhase = p1.phase - p2.phase;
      const resonance = Math.cos(dPhase);
      const hue = resonance > 0 ? 120 : 0; // Green for in-phase, red for out-of-phase
      const alpha = bond.weight * 0.6;
      
      ctx.strokeStyle = `hsla(${hue}, 70%, 50%, ${alpha})`;
      ctx.lineWidth = bond.weight * 3;
      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.stroke();
    });
    
    // Render particles (I stage visualization)
    system.particles.forEach(p => {
      // Only render conscious particles (adaptive complexity)
      if (p.consciousness < system.consciousnessThreshold) return;
      
      const radius = 5 + p.amplitude * 10;
      const pulse = Math.sin(p.phase) * 0.3 + 0.7;
      
      // Glow effect
      const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, radius * 2);
      const energyColor = p.amplitude > 0.7 ? [100, 200, 255] : 
                          p.amplitude > 0.3 ? [150, 150, 255] :
                          [200, 100, 100];
      
      gradient.addColorStop(0, `rgba(${energyColor[0]}, ${energyColor[1]}, ${energyColor[2]}, ${pulse})`);
      gradient.addColorStop(0.5, `rgba(${energyColor[0]}, ${energyColor[1]}, ${energyColor[2]}, ${pulse * 0.5})`);
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
    
    // Death fade effect
    if (system.deathTimer > 0) {
      const fadeAlpha = system.deathTimer / PHYSICS.DEATH_GRACE_PERIOD * 0.5;
      ctx.fillStyle = `rgba(0, 0, 0, ${fadeAlpha})`;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
  };

  // Determine ICE stage
  const determineStage = () => {
    const system = systemRef.current;
    if (system.particles.length === 0) return 'Void';
    if (system.particles.length === 1) return 'Identity';
    
    const strongBonds = system.bonds.filter(b => b.weight > PHYSICS.COUPLING_THRESHOLD);
    if (strongBonds.length === 0) return 'Identity';
    if (strongBonds.length < 3) return 'Coupling';
    
    // Calculate field variance
    let fieldSum = 0;
    let fieldSqSum = 0;
    system.particles.forEach(p => {
      fieldSum += p.fieldDensity;
      fieldSqSum += p.fieldDensity * p.fieldDensity;
    });
    const fieldMean = fieldSum / system.particles.length;
    const fieldVariance = (fieldSqSum / system.particles.length) - fieldMean * fieldMean;
    
    if (fieldVariance > PHYSICS.FIELD_VARIANCE_THRESHOLD) {
      // Check for boundary coherence
      const avgCoupling = strongBonds.reduce((sum, b) => sum + b.weight, 0) / strongBonds.length;
      if (avgCoupling > PHYSICS.BOUNDARY_COHERENCE) {
        return system.particles.length > 20 ? 'Organism' : 'Boundary';
      }
      return 'Field';
    }
    
    return 'Coupling';
  };

  // Animation loop
  useEffect(() => {
    initializeSeed();
    
    let animationId: number;
    let lastTime = Date.now();
    let frameCount = 0;
    let fpsTime = Date.now();
    
    const loop = () => {
      const currentTime = Date.now();
      const dt = Math.min((currentTime - lastTime) / 16.67, 2); // Cap dt for stability
      lastTime = currentTime;
      
      if (isRunning) {
        updatePhysics(dt);
      }
      render();
      
      // Update FPS counter
      frameCount++;
      if (currentTime - fpsTime > 1000) {
        const fps = frameCount / ((currentTime - fpsTime) / 1000);
        const system = systemRef.current;
        const totalEnergy = system.particles.reduce((sum, p) => sum + p.amplitude, 0);
        
        setStats({
          particles: system.particles.length,
          bonds: system.bonds.length,
          energy: totalEnergy,
          fps: Math.round(fps),
          stage: determineStage(),
        });
        
        frameCount = 0;
        fpsTime = currentTime;
      }
      
      animationId = requestAnimationFrame(loop);
    };
    
    loop();
    
    return () => cancelAnimationFrame(animationId);
  }, [isRunning]);

  // User interaction
  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
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
        p.consciousness = Math.min(1, p.consciousness + 0.3);
      }
    });
  };

  const handleReset = () => {
    initializeSeed();
    systemRef.current.isDead = false;
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
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded flex items-center gap-2"
            >
              {isRunning ? <Pause size={16} /> : <Play size={16} />}
              {isRunning ? 'Pause' : 'Play'}
            </button>
            <button
              onClick={handleReset}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded flex items-center gap-2"
            >
              <RotateCcw size={16} />
              Reset
            </button>
            <button
              onClick={() => setShowInfo(!showInfo)}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded flex items-center gap-2"
            >
              <Info size={16} />
            </button>
          </div>
        </div>
        
        {showInfo && (
          <div className="mb-4 p-4 bg-slate-900 rounded border border-slate-700 text-sm">
            <p className="text-blue-300 mb-2">
              <strong>Click/tap</strong> to feed energy • Watch your cell grow and learn
            </p>
            <div className="grid grid-cols-2 gap-2 text-slate-300">
              <div>Stage: <span className="text-blue-400 font-bold">{stats.stage}</span></div>
              <div>Particles: <span className="text-blue-400">{stats.particles}</span></div>
              <div>Bonds: <span className="text-green-400">{stats.bonds}</span></div>
              <div>Energy: <span className="text-yellow-400">{stats.energy.toFixed(1)}</span></div>
              <div>FPS: <span className={stats.fps < 50 ? 'text-red-400' : 'text-green-400'}>{stats.fps}</span></div>
              <div>Conscious: <span className="text-purple-400">
                {system.particles.filter(p => p.consciousness > systemRef.current.consciousnessThreshold).length}
              </span></div>
            </div>
          </div>
        )}
        
        <canvas
          ref={canvasRef}
          width={800}
          height={600}
          onClick={handleCanvasClick}
          className="w-full border-2 border-blue-500/30 rounded cursor-pointer"
          style={{ aspectRatio: '4/3' }}
        />
        
        <div className="mt-4 text-xs text-slate-500 text-center">
          Based on Fractal Reality Field Equation theory • ICE developmental stages: Identity → Coupling → Environment
        </div>
      </div>
    </div>
  );
};

export default FractalPetCell;
