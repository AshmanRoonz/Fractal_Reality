import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Play, Pause, RotateCcw, Mic, MicOff, Zap } from 'lucide-react';

const PHYSICS = {
  ENERGY_DECAY: 0.0002,        
  RESONANCE_GAIN: 0.004,       
  BASELINE_ENERGY: 0.0005,     
  FEED_AMOUNT: 0.4,
  COUPLING_STRENGTH: 1.2,      
  COUPLING_RANGE: 300,         
  DAMPING: 0.85,               
  MIN_SPACING: 30,
  REPULSION: 200,
  MITOSIS_ENERGY: 0.82,        
  MITOSIS_STABILITY: 120,      
  MAX_PARTICLES: 60,
  AGING_RATE: 0.00001,
  ELDERLY_AGE: 10000,          
  LEARNING_RATE: 0.04,         // Even faster learning
  WEIGHT_DECAY: 0.0002,        // Almost no decay!
  PRUNE_THRESHOLD: 0.05,       
  BOND_THRESHOLD: 0.4,        
};

export default function FractalPetCell() {
  const canvasRef = useRef(null);
  const [isRunning, setIsRunning] = useState(true);
  const [micEnabled, setMicEnabled] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(false);
  const [interactionMode, setInteractionMode] = useState('feed'); // feed, excite, calm
  const [stats, setStats] = useState({ 
    particles: 0, bonds: 0, energy: 0, stage: 'Identity', 
    avgAge: 0, fps: 60, coherence: 0 
  });
  
  const audioContextRef = useRef(null);
  const micAnalyserRef = useRef(null);
  const micStreamRef = useRef(null);
  const audioInfluenceRef = useRef(0);
  const oscillatorsRef = useRef(new Map());
  const masterGainRef = useRef(null);
  
  const systemRef = useRef({
    particles: [],
    bonds: [],
    energyFlows: [],
    nextId: 0,
    time: 0,
  });

  // Audio setup
  const initMicrophone = useCallback(async () => {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!audioContextRef.current) {
        audioContextRef.current = new AudioContext();
        
        // Create master gain
        masterGainRef.current = audioContextRef.current.createGain();
        masterGainRef.current.gain.value = 0.1;
        masterGainRef.current.connect(audioContextRef.current.destination);
      }
      
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      micStreamRef.current = stream;
      
      const source = audioContextRef.current.createMediaStreamSource(stream);
      micAnalyserRef.current = audioContextRef.current.createAnalyser();
      micAnalyserRef.current.fftSize = 2048;
      micAnalyserRef.current.smoothingTimeConstant = 0.8;
      
      source.connect(micAnalyserRef.current);
      return true;
    } catch (error) {
      console.error('Microphone access denied:', error);
      return false;
    }
  }, []);

  const stopMicrophone = useCallback(() => {
    if (micStreamRef.current) {
      micStreamRef.current.getTracks().forEach(track => track.stop());
      micStreamRef.current = null;
    }
    micAnalyserRef.current = null;
  }, []);

  const toggleMic = async () => {
    if (micEnabled) {
      stopMicrophone();
      setMicEnabled(false);
    } else {
      const success = await initMicrophone();
      setMicEnabled(success);
    }
  };
  
  const toggleSound = () => {
    if (!soundEnabled) {
      // Only initialize audio context if needed
      if (!audioContextRef.current) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        audioContextRef.current = new AudioContext();
        masterGainRef.current = audioContextRef.current.createGain();
        masterGainRef.current.gain.value = 0.1;
        masterGainRef.current.connect(audioContextRef.current.destination);
      }
    }
    setSoundEnabled(!soundEnabled);
  };
  
  // Particle class with learning
  class Particle {
    constructor(id, x, y, frequency, amplitude, age = 0) {
      this.id = id;
      this.x = x;
      this.y = y;
      this.vx = 0;
      this.vy = 0;
      this.phase = Math.random() * Math.PI * 2;
      this.frequency = frequency;
      this.amplitude = amplitude;
      this.age = age;
      this.stability = 0;
      
      // Learning & memory
      this.resonanceMemory = new Map();
      this.connectionWeights = new Map();
      this.preferredAngles = [];
      this.gravitationalMass = 0;
      
      // Visual
      this.hue = Math.random() * 360;
      this.evolutionStage = Math.random() * 3;
      this.geometryType = Math.floor(Math.random() * 6);
      this.phaseOffset = Math.random() * Math.PI * 2;
      
      // Probability cloud
      this.probabilityCloud = [];
      for (let i = 0; i < 6; i++) {
        this.probabilityCloud.push({
          angle: Math.random() * Math.PI * 2,
          dist: 10 + Math.random() * 15,
          phase: Math.random() * Math.PI * 2,
        });
      }
    }
    
    update(system, dt, canvas, audioInfluence) {
      this.phase += this.frequency * dt;
      this.age += dt;
      
      // Evolution
      this.evolutionStage += 0.003 * dt * (1 + audioInfluence * 0.5);
      this.geometryType = (this.geometryType + Math.sin(this.evolutionStage) * 0.01) % 6;
      
      // Update gravitational mass from connections
      this.gravitationalMass = 0;
      for (let [id, weight] of this.connectionWeights.entries()) {
        this.gravitationalMass += weight;
      }
      this.gravitationalMass = Math.min(2, this.gravitationalMass / 5);
      
      // Learn preferred angles from strong connections
      const strongBonds = system.bonds.filter(b => 
        (b.id1 === this.id || b.id2 === this.id) && b.weight > 0.5
      );
      
      strongBonds.forEach(bond => {
        const partnerId = bond.id1 === this.id ? bond.id2 : bond.id1;
        const partner = system.particles.find(p => p.id === partnerId);
        if (partner) {
          const angle = Math.atan2(partner.y - this.y, partner.x - this.x);
          this.preferredAngles.push(angle);
          if (this.preferredAngles.length > 5) {
            this.preferredAngles.shift();
          }
        }
      });
    }
    
    drawBranch(ctx, x, y, length, angle, depth, time, baseAlpha) {
      if (depth === 0 || length < 2) {
        this.drawBody(ctx, x, y, angle, time, baseAlpha);
        return;
      }
      
      const endX = x + length * Math.cos(angle);
      const endY = y + length * Math.sin(angle);
      const alpha = baseAlpha * (depth / 4);
      
      // Draw branch
      const gradient = ctx.createLinearGradient(x, y, endX, endY);
      gradient.addColorStop(0, `hsla(${this.hue}, 70%, 50%, ${alpha * 0.6})`);
      gradient.addColorStop(1, `hsla(${this.hue + 30}, 70%, 60%, ${alpha})`);
      
      ctx.strokeStyle = gradient;
      ctx.lineWidth = Math.max(0.5, depth * 1.5);
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(endX, endY);
      ctx.stroke();
      
      if (depth > 1) {
        this.drawBody(ctx, endX, endY, angle, time, alpha);
      }
      
      // Branch recursion
      const branchAngle = Math.PI / 5;
      const lengthMult = 0.65 + Math.sin(time * 0.01) * 0.05;
      
      this.drawBranch(ctx, endX, endY, length * lengthMult, angle - branchAngle, depth - 1, time, baseAlpha);
      this.drawBranch(ctx, endX, endY, length * lengthMult, angle + branchAngle, depth - 1, time, baseAlpha);
    }
    
    drawBody(ctx, x, y, angle, time, alpha) {
      const size = 3 + this.amplitude * 5 + this.gravitationalMass * 3;
      const pulse = Math.sin(this.phase) * 0.3 + 0.7;
      const rotation = time * 0.01 * this.evolutionStage + this.phaseOffset;
      
      ctx.save();
      ctx.translate(x, y);
      ctx.rotate(rotation);
      
      // Glow for important nodes
      if (this.gravitationalMass > 0.5) {
        ctx.shadowBlur = 15 * this.gravitationalMass;
        ctx.shadowColor = `hsla(${this.hue}, 80%, 60%, ${this.gravitationalMass * 0.4})`;
      }
      
      // Draw geometry based on evolution
      const stage = Math.floor(this.geometryType);
      ctx.fillStyle = `hsla(${this.hue}, 80%, 60%, ${alpha * pulse})`;
      ctx.strokeStyle = `hsla(${this.hue + 20}, 90%, 70%, ${alpha * pulse * 0.8})`;
      ctx.lineWidth = 1.5;
      
      ctx.beginPath();
      switch (stage) {
        case 0: // Triangle
          for (let i = 0; i <= 3; i++) {
            const a = (i / 3) * Math.PI * 2 - Math.PI / 2;
            const px = Math.cos(a) * size;
            const py = Math.sin(a) * size;
            if (i === 0) ctx.moveTo(px, py);
            else ctx.lineTo(px, py);
          }
          break;
        case 1: // Square
          ctx.rect(-size, -size, size * 2, size * 2);
          break;
        case 2: // Pentagon
          for (let i = 0; i <= 5; i++) {
            const a = (i / 5) * Math.PI * 2 - Math.PI / 2;
            const px = Math.cos(a) * size;
            const py = Math.sin(a) * size;
            if (i === 0) ctx.moveTo(px, py);
            else ctx.lineTo(px, py);
          }
          break;
        case 3: // Hexagon
          for (let i = 0; i <= 6; i++) {
            const a = (i / 6) * Math.PI * 2;
            const px = Math.cos(a) * size;
            const py = Math.sin(a) * size;
            if (i === 0) ctx.moveTo(px, py);
            else ctx.lineTo(px, py);
          }
          break;
        case 4: // Star
          for (let i = 0; i <= 12; i++) {
            const a = (i / 12) * Math.PI * 2 - Math.PI / 2;
            const r = i % 2 === 0 ? size : size * 0.5;
            const px = Math.cos(a) * r;
            const py = Math.sin(a) * r;
            if (i === 0) ctx.moveTo(px, py);
            else ctx.lineTo(px, py);
          }
          break;
        case 5: // Circle
          ctx.arc(0, 0, size, 0, Math.PI * 2);
          break;
      }
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      
      ctx.shadowBlur = 0;
      ctx.restore();
    }
  }

  const initializeSeed = () => {
    const system = systemRef.current;
    system.particles = [];
    system.bonds = [];
    system.energyFlows = [];
    system.nextId = 0;
    system.time = 0;
    
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    
    const seedCount = 4 + Math.floor(Math.random() * 3);
    const baseFreq = 0.045;
    
    for (let i = 0; i < seedCount; i++) {
      const angle = (Math.PI * 2 * i) / seedCount;
      const radius = 40 + Math.random() * 20; // Closer together
      const x = cx + Math.cos(angle) * radius;
      const y = cy + Math.sin(angle) * radius;
      const frequency = baseFreq * (0.9 + Math.random() * 0.2); // More similar frequencies
      
      system.particles.push(new Particle(system.nextId++, x, y, frequency, 0.7));
    }
  };

  const updatePhysics = (dt) => {
    const system = systemRef.current;
    if (system.particles.length === 0) return;
    
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    system.time += dt;
    
    // Get audio influence with pitch detection
    let audioInfluence = 0;
    let dominantFreq = 0;
    let rhythm = 0;
    
    if (micEnabled && micAnalyserRef.current) {
      const bufferLength = micAnalyserRef.current.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      const timeData = new Uint8Array(bufferLength);
      
      micAnalyserRef.current.getByteFrequencyData(dataArray);
      micAnalyserRef.current.getByteTimeDomainData(timeData);
      
      // Overall volume
      const average = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
      audioInfluence = average / 256;
      audioInfluenceRef.current = audioInfluence;
      
      // Find dominant frequency (pitch)
      let maxVal = 0;
      let maxIdx = 0;
      for (let i = 0; i < bufferLength; i++) {
        if (dataArray[i] > maxVal) {
          maxVal = dataArray[i];
          maxIdx = i;
        }
      }
      const nyquist = audioContextRef.current.sampleRate / 2;
      dominantFreq = (maxIdx / bufferLength) * nyquist;
      
      // Detect rhythm (rapid changes in volume)
      let changeSum = 0;
      for (let i = 1; i < timeData.length; i++) {
        changeSum += Math.abs(timeData[i] - timeData[i-1]);
      }
      rhythm = Math.min(1, changeSum / (timeData.length * 50));
      
      // Apply effects based on detected features
      if (audioInfluence > 0.2) {
        // Pitch affects particle frequencies
        const freqInfluence = dominantFreq / 1000; // normalize
        system.particles.forEach(p => {
          if (Math.random() < audioInfluence * 0.1) {
            p.frequency = p.frequency * 0.95 + freqInfluence * 0.05;
          }
        });
        
        // Rhythm creates pulses
        if (rhythm > 0.5) {
          system.particles.forEach(p => {
            p.amplitude = Math.min(1, p.amplitude + rhythm * 0.1);
          });
        }
      }
    }
    
    // Update particle sounds directly (no callback dependency)
    if (soundEnabled && audioContextRef.current && masterGainRef.current) {
      system.particles.forEach(p => {
        if (oscillatorsRef.current.has(p.id)) {
          const sound = oscillatorsRef.current.get(p.id);
          const baseFreq = 200 + p.frequency * 3000;
          const volume = (p.amplitude * 0.15 + p.gravitationalMass * 0.1) * 0.02;
          
          try {
            sound.osc.frequency.setTargetAtTime(baseFreq, audioContextRef.current.currentTime, 0.1);
            sound.gain.gain.setTargetAtTime(volume, audioContextRef.current.currentTime, 0.1);
          } catch (e) {}
        } else if (p.amplitude > 0.4) {
          try {
            const ctx = audioContextRef.current;
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            
            const baseFreq = 200 + p.frequency * 3000;
            osc.frequency.value = baseFreq;
            
            const volume = (p.amplitude * 0.15 + p.gravitationalMass * 0.1) * 0.02;
            gain.gain.value = volume;
            
            const waveforms = ['sine', 'triangle', 'square', 'sawtooth'];
            osc.type = waveforms[Math.floor(p.geometryType) % 4];
            
            osc.connect(gain);
            gain.connect(masterGainRef.current);
            
            osc.start();
            oscillatorsRef.current.set(p.id, { osc, gain, freq: baseFreq });
          } catch (e) {}
        }
      });
      
      // Clean up dead particle sounds
      for (let [id, sound] of oscillatorsRef.current.entries()) {
        if (!system.particles.find(p => p.id === id)) {
          try {
            sound.osc.stop();
            sound.gain.disconnect();
          } catch (e) {}
          oscillatorsRef.current.delete(id);
        }
      }
    }
    
    // Update particles
    system.particles.forEach(p => p.update(system, dt, canvas, audioInfluence));
    
    // Calculate forces and resonance
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
          const dPhase = p1.phase - p2.phase;
          const dFreq = Math.abs(p1.frequency - p2.frequency);
          const resonance = Math.cos(dPhase) * Math.exp(-dFreq / 0.02);
          
          const strength = PHYSICS.COUPLING_STRENGTH * 
            (p1.amplitude * p2.amplitude) / (dist * dist + 1);
          const force = strength * resonance;
          
          fx += force * dx / dist;
          fy += force * dy / dist;
          
          if (resonance > 0.5) {
            resonanceEnergy += PHYSICS.RESONANCE_GAIN * resonance * p2.amplitude;
            
            // Frequency sync - help them lock in
            const sync = 0.015 * Math.sin(dPhase) * (1 + audioInfluence);
            p1.frequency += sync * p2.amplitude;
            p2.frequency -= sync * p1.amplitude;
            
            // Hebbian learning - strengthen bond
            let bond = system.bonds.find(b =>
              (b.id1 === p1.id && b.id2 === p2.id) ||
              (b.id1 === p2.id && b.id2 === p1.id)
            );
            
            if (resonance > PHYSICS.BOND_THRESHOLD) {
              if (!bond) {
                bond = {
                  id1: p1.id,
                  id2: p2.id,
                  weight: 0.4,           // Start much stronger!
                  age: 0,
                  resonanceHistory: [],
                };
                system.bonds.push(bond);
              }
              
              // Accelerated learning - bonds strengthen quickly
              const learningBoost = 1 + (bond.age < 50 ? 1 : 0); // Extra boost for young bonds
              bond.weight = Math.min(1, bond.weight + PHYSICS.LEARNING_RATE * resonance * (1 + audioInfluence) * learningBoost);
              bond.age++;
              bond.resonanceHistory.push(resonance);
              if (bond.resonanceHistory.length > 50) {
                bond.resonanceHistory.shift();
              }
              
              // Update connection weights
              p1.connectionWeights.set(p2.id, bond.weight);
              p2.connectionWeights.set(p1.id, bond.weight);
              
              // Update resonance memory
              const mem1 = p1.resonanceMemory.get(p2.id) || { count: 0, avg: 0 };
              mem1.count++;
              mem1.avg = (mem1.avg * (mem1.count - 1) + resonance) / mem1.count;
              p1.resonanceMemory.set(p2.id, mem1);
              
              const mem2 = p2.resonanceMemory.get(p1.id) || { count: 0, avg: 0 };
              mem2.count++;
              mem2.avg = (mem2.avg * (mem2.count - 1) + resonance) / mem2.count;
              p2.resonanceMemory.set(p1.id, mem2);
            }
          }
        }
        
        // Repulsion
        if (dist < PHYSICS.MIN_SPACING && dist > 0) {
          const repulsion = PHYSICS.REPULSION / Math.pow(dist + 1, 3);
          fx -= repulsion * dx / dist;
          fy -= repulsion * dy / dist;
        }
      }
      
      p1.amplitude += resonanceEnergy;
      
      // Apply forces
      p1.vx += fx * dt;
      p1.vy += fy * dt;
      
      // Gentle attraction toward center to keep colony together
      const dxCenter = (canvas.width / 2) - p1.x;
      const dyCenter = (canvas.height / 2) - p1.y;
      const distCenter = Math.sqrt(dxCenter * dxCenter + dyCenter * dyCenter);
      if (distCenter > 100) {
        const centerPull = 0.02;
        p1.vx += centerPull * dxCenter / distCenter;
        p1.vy += centerPull * dyCenter / distCenter;
      }
      
      p1.vx *= PHYSICS.DAMPING;
      p1.vy *= PHYSICS.DAMPING;
      p1.x += p1.vx * dt;
      p1.y += p1.vy * dt;
      
      // Soft walls
      const margin = 80;
      if (p1.x < margin) p1.vx += 0.5;
      if (p1.x > canvas.width - margin) p1.vx -= 0.5;
      if (p1.y < margin) p1.vy += 0.5;
      if (p1.y > canvas.height - margin) p1.vy -= 0.5;
    }
    
    // Energy dynamics - more forgiving
    system.particles.forEach(p => {
      // Baseline energy + audio boost
      p.amplitude += PHYSICS.BASELINE_ENERGY * dt * (1 + audioInfluence * 3);
      
      // Age-based decay - but gentler
      const ageFactor = 1 + (p.age / PHYSICS.ELDERLY_AGE) * 0.3;
      p.amplitude -= PHYSICS.ENERGY_DECAY * ageFactor * dt;
      
      // Clamp - but never go below 0.15 (no starvation death)
      p.amplitude = Math.max(0.15, Math.min(1.0, p.amplitude));
      
      const vel = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
      if (vel < 0.5 && p.amplitude > 0.7) {
        p.stability++;
      } else {
        p.stability = Math.max(0, p.stability - 1);
      }
    });
    
    // Mitosis
    if (system.particles.length < PHYSICS.MAX_PARTICLES) {
      const toAdd = [];
      system.particles.forEach(p => {
        if (p.amplitude > PHYSICS.MITOSIS_ENERGY && p.stability > PHYSICS.MITOSIS_STABILITY) {
          const angle = Math.random() * Math.PI * 2;
          const offset = 25;
          const x = p.x + Math.cos(angle) * offset;
          const y = p.y + Math.sin(angle) * offset;
          
          toAdd.push(new Particle(
            system.nextId++,
            x, y,
            p.frequency * (0.95 + Math.random() * 0.1),
            p.amplitude * 0.7,
            0
          ));
          
          p.amplitude *= 0.7;
          p.stability = 0;
          p.vx = -Math.cos(angle) * 2;
          p.vy = -Math.sin(angle) * 2;
        }
      });
      system.particles.push(...toAdd);
    }
    
    // Pruning - only remove truly dead particles
    system.particles = system.particles.filter(p => {
      // Only remove if amplitude drops critically low (shouldn't happen now)
      return p.amplitude > 0.05;
    });
    
    // Bond decay and pruning
    system.bonds = system.bonds.filter(bond => {
      bond.weight -= PHYSICS.WEIGHT_DECAY * dt;
      
      const p1Exists = system.particles.find(p => p.id === bond.id1);
      const p2Exists = system.particles.find(p => p.id === bond.id2);
      
      return bond.weight > PHYSICS.PRUNE_THRESHOLD && p1Exists && p2Exists;
    });
    
    // Update energy flows
    system.energyFlows = system.energyFlows.filter(flow => {
      flow.age += dt;
      flow.strength *= 0.95;
      return flow.strength > 0.05 && flow.age < 100;
    });
  };

  const render = () => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!canvas || !ctx) return;
    
    const system = systemRef.current;
    
    // Background with trail effect
    ctx.fillStyle = 'rgba(0, 8, 16, 0.15)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    if (system.particles.length === 0) {
      ctx.fillStyle = 'rgba(100, 150, 200, 0.5)';
      ctx.font = '20px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('Click to awaken...', canvas.width / 2, canvas.height / 2);
      return;
    }
    
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    
    // Draw energy flows
    system.energyFlows.forEach(flow => {
      ctx.strokeStyle = `hsla(180, 70%, 60%, ${flow.strength * 0.5})`;
      ctx.lineWidth = 2 * flow.strength;
      ctx.beginPath();
      ctx.moveTo(flow.x1, flow.y1);
      ctx.lineTo(flow.x2, flow.y2);
      ctx.stroke();
    });
    
    // Draw bonds with learned weights
    system.bonds.forEach(bond => {
      const p1 = system.particles.find(p => p.id === bond.id1);
      const p2 = system.particles.find(p => p.id === bond.id2);
      if (!p1 || !p2) return;
      
      const avgResonance = bond.resonanceHistory.length > 0
        ? bond.resonanceHistory.reduce((a, b) => a + b, 0) / bond.resonanceHistory.length
        : 0;
      
      const gradient = ctx.createLinearGradient(p1.x, p1.y, p2.x, p2.y);
      gradient.addColorStop(0, `hsla(${p1.hue}, 70%, 50%, ${bond.weight * 0.3})`);
      gradient.addColorStop(1, `hsla(${p2.hue}, 70%, 50%, ${bond.weight * 0.3})`);
      
      ctx.strokeStyle = gradient;
      ctx.lineWidth = 1 + bond.weight * 4;
      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.stroke();
      
      // Strong connection nodes
      if (bond.weight > 0.7) {
        const midX = (p1.x + p2.x) / 2;
        const midY = (p1.y + p2.y) / 2;
        const pulse = Math.sin(system.time * 0.05) * 0.3 + 0.7;
        
        ctx.fillStyle = `hsla(${(p1.hue + p2.hue) / 2}, 80%, 70%, ${bond.weight * pulse * 0.6})`;
        ctx.beginPath();
        ctx.arc(midX, midY, 2 + bond.weight * 3, 0, Math.PI * 2);
        ctx.fill();
      }
    });
    
    // Draw particles with fractal branches
    system.particles.forEach(p => {
      // Probability cloud
      p.probabilityCloud.forEach(cloud => {
        const angle = Math.atan2(p.y - centerY, p.x - centerX) + cloud.angle + 
                     Math.sin(system.time * 0.01 + cloud.phase) * 0.5;
        const dist = cloud.dist * (1 + Math.sin(system.time * 0.02 + cloud.phase) * 0.3);
        const cloudX = p.x + Math.cos(angle) * dist;
        const cloudY = p.y + Math.sin(angle) * dist;
        
        ctx.fillStyle = `hsla(${p.hue}, 70%, 60%, 0.08)`;
        ctx.beginPath();
        ctx.arc(cloudX, cloudY, 3, 0, Math.PI * 2);
        ctx.fill();
      });
      
      // Main particle with fractal branches
      const angleToCenter = Math.atan2(p.y - centerY, p.x - centerX);
      const branchLength = 15 + p.amplitude * 25 + p.gravitationalMass * 15;
      const depth = Math.min(3, Math.ceil(2 + p.gravitationalMass * 2));
      const baseAlpha = 0.4 + p.amplitude * 0.5 + p.gravitationalMass * 0.3;
      
      p.drawBranch(ctx, p.x, p.y, branchLength, angleToCenter, depth, system.time, baseAlpha);
    });
  };

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
      
      frameCount++;
      if (currentTime - fpsTime > 1000) {
        const system = systemRef.current;
        const energy = system.particles.reduce((sum, p) => sum + p.amplitude, 0);
        const avgAge = system.particles.length > 0
          ? system.particles.reduce((sum, p) => sum + p.age, 0) / system.particles.length
          : 0;
        
        // Calculate coherence
        let totalWeight = 0;
        let matureBonds = 0;
        system.bonds.forEach(b => { 
          totalWeight += b.weight; 
          if (b.weight > 0.6) matureBonds++;
        });
        const coherence = system.bonds.length > 0 ? totalWeight / system.bonds.length : 0;
        
        // Stage detection with hysteresis (resistance to rapid changes)
        let stage = 'Identity';
        if (system.particles.length === 0) {
          stage = 'Void';
        } else if (system.particles.length === 1 || system.bonds.length === 0) {
          stage = 'Identity';
        } else if (system.bonds.length < 5 || matureBonds < 3) {
          stage = 'Coupling';
        } else if (system.bonds.length < 15 || system.particles.length < 15) {
          stage = 'Field';
        } else if (system.particles.length < 35) {
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
          fps: frameCount,
          coherence: coherence,
        });
        
        frameCount = 0;
        fpsTime = currentTime;
      }
      
      animationId = requestAnimationFrame(loop);
    };
    
    loop();
    
    return () => {
      cancelAnimationFrame(animationId);
      stopMicrophone();
      
      // Clean up all oscillators
      for (let [id, sound] of oscillatorsRef.current.entries()) {
        try {
          sound.osc.stop();
          sound.gain.disconnect();
        } catch (e) {}
      }
      oscillatorsRef.current.clear();
    };
  }, [isRunning, stopMicrophone]);

  const handleCanvasInteraction = (e) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const system = systemRef.current;
    
    // Create energy flow
    if (e.type === 'mousemove' && e.buttons === 1) {
      system.energyFlows.push({
        x1: x - (e.movementX || 0),
        y1: y - (e.movementY || 0),
        x2: x,
        y2: y,
        strength: 1,
        age: 0,
      });
    }
    
    // Apply effects based on interaction mode
    system.particles.forEach(p => {
      const dx = p.x - x;
      const dy = p.y - y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      
      if (dist < 150) {
        const strength = 1 - dist / 150;
        
        switch (interactionMode) {
          case 'feed':
            // Standard feeding
            p.amplitude = Math.min(1, p.amplitude + PHYSICS.FEED_AMOUNT * strength);
            p.hue = (p.hue + Math.random() * 30) % 360;
            break;
            
          case 'excite':
            // Create chaos and movement
            p.vx += (Math.random() - 0.5) * 5 * strength;
            p.vy += (Math.random() - 0.5) * 5 * strength;
            p.frequency *= (1 + (Math.random() - 0.5) * 0.2 * strength);
            p.hue = (p.hue + 120) % 360;
            p.evolutionStage += 0.5 * strength;
            break;
            
          case 'calm':
            // Smooth and stabilize
            p.vx *= (1 - 0.5 * strength);
            p.vy *= (1 - 0.5 * strength);
            p.amplitude = Math.min(1, p.amplitude + 0.1 * strength);
            p.hue = (p.hue * 0.9 + 200 * 0.1); // Shift toward blue
            break;
        }
        
        // Play sound on interaction
        if (soundEnabled && audioContextRef.current && masterGainRef.current && Math.random() < 0.3) {
          try {
            const ctx = audioContextRef.current;
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            
            const baseFreq = 200 + p.frequency * 3000;
            osc.frequency.value = baseFreq;
            gain.gain.value = 0.05;
            
            osc.connect(gain);
            gain.connect(masterGainRef.current);
            
            osc.start();
            setTimeout(() => {
              try {
                osc.stop();
                gain.disconnect();
              } catch (e) {}
            }, 100);
          } catch (e) {}
        }
      }
    });
  };

  return (
    <div className="w-full h-screen bg-slate-950 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-6xl">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-blue-300">
              Fractal Reality Pet Cell
            </h1>
            <p className="text-xs text-slate-500 mt-1">Living • Learning • Evolving</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setIsRunning(!isRunning)}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded flex items-center gap-2 text-white"
            >
              {isRunning ? <Pause size={16} /> : <Play size={16} />}
            </button>
            <button
              onClick={toggleMic}
              className={`px-4 py-2 rounded flex items-center gap-2 text-white ${
                micEnabled ? 'bg-red-600 hover:bg-red-700' : 'bg-slate-600 hover:bg-slate-700'
              }`}
              title="Sing or hum to influence growth"
            >
              {micEnabled ? <MicOff size={16} /> : <Mic size={16} />}
            </button>
            <button
              onClick={toggleSound}
              className={`px-4 py-2 rounded flex items-center gap-2 text-white ${
                soundEnabled ? 'bg-green-600 hover:bg-green-700' : 'bg-slate-600 hover:bg-slate-700'
              }`}
              title="Toggle sound generation"
            >
              <Zap size={16} />
              {soundEnabled ? 'Mute' : 'Sound'}
            </button>
            <button
              onClick={() => initializeSeed()}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded flex items-center gap-2 text-white"
            >
              <RotateCcw size={16} />
              Rebirth
            </button>
          </div>
        </div>
        
        <div className="mb-4 p-4 bg-slate-900 rounded border border-slate-700 text-sm">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-slate-400 text-xs mb-2">
                <strong>Choose interaction mode:</strong>
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => setInteractionMode('feed')}
                  className={`px-3 py-1 rounded text-xs ${
                    interactionMode === 'feed' ? 'bg-green-600 text-white' : 'bg-slate-700 text-slate-300'
                  }`}
                >
                  🍃 Feed (nurture)
                </button>
                <button
                  onClick={() => setInteractionMode('excite')}
                  className={`px-3 py-1 rounded text-xs ${
                    interactionMode === 'excite' ? 'bg-orange-600 text-white' : 'bg-slate-700 text-slate-300'
                  }`}
                >
                  ⚡ Excite (chaos)
                </button>
                <button
                  onClick={() => setInteractionMode('calm')}
                  className={`px-3 py-1 rounded text-xs ${
                    interactionMode === 'calm' ? 'bg-blue-600 text-white' : 'bg-slate-700 text-slate-300'
                  }`}
                >
                  🌊 Calm (harmony)
                </button>
              </div>
            </div>
            {micEnabled && audioInfluenceRef.current > 0.1 && (
              <div className="flex items-center gap-2 text-yellow-400 animate-pulse">
                <Zap size={14} />
                <span className="text-xs">Listening...</span>
              </div>
            )}
          </div>
          <div className="grid grid-cols-7 gap-2 text-slate-300 text-xs">
            <div>Stage: <span className="text-blue-400 font-bold">{stats.stage}</span></div>
            <div>Cells: <span className="text-blue-400">{stats.particles}</span></div>
            <div>Bonds: <span className="text-green-400">{stats.bonds}</span></div>
            <div>Energy: <span className="text-yellow-400">{stats.energy.toFixed(1)}</span></div>
            <div>Age: <span className="text-purple-400">{(stats.avgAge / 60).toFixed(1)}s</span></div>
            <div>FPS: <span className={stats.fps < 50 ? 'text-red-400' : 'text-green-400'}>{stats.fps}</span></div>
            <div>Coherence: <span className="text-cyan-400">{(stats.coherence * 100).toFixed(0)}%</span></div>
          </div>
          <p className="text-slate-500 text-xs mt-2">
            {soundEnabled && '🎵 Making sounds • '}
            {micEnabled && '🎤 Responds to pitch & rhythm • '}
            Click & drag to interact
          </p>
        </div>
        
        <canvas
          ref={canvasRef}
          width={1200}
          height={800}
          onClick={handleCanvasInteraction}
          onMouseMove={handleCanvasInteraction}
          className="w-full border-2 border-blue-500/30 rounded cursor-crosshair bg-slate-950"
          style={{ aspectRatio: '3/2' }}
        />
        
        <div className="mt-4 text-xs text-slate-500 text-center space-y-1">
          <p>Hebbian learning • Resonance memory • Synaptic pruning • Fractal emergence</p>
          <p className="text-slate-600">Based on Fractal Reality Field Equation • ICE: Identity → Coupling → Environment</p>
        </div>
      </div>
    </div>
  );
}
