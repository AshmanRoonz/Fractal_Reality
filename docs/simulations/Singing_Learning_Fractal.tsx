import React, { useEffect, useRef, useState, useCallback } from 'react';

// ═══════════════════════════════════════════════════════════════
//  CIRCUMPUNCT FRACTAL SIMULATOR v2.0
//  Grounded in the Circumpunct Framework v6.0 Mathematics
//
//  ⊙ = Φ(•, ○)
//  Conservation of Traversal: D_• + D_Φ = D_○ = 3
//  Six Coupled ODEs  |  ⊛ → i → ☀️ flow cycles
//  Phase coherence T(Δφ) = cos²(Δφ/2)
//  ρ criterion regime transitions
// ═══════════════════════════════════════════════════════════════

const CircumpunctFractalSimulator = () => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const audioContextRef = useRef(null);
  const audioAnalyserRef = useRef(null);
  const audioDataRef = useRef(null);
  const micAnalyserRef = useRef(null);
  const micDataRef = useRef(null);
  const micStreamRef = useRef(null);
  const learnedMelody = useRef([]);
  const melodicMemory = useRef(new Map());
  const harmonicResponse = useRef({ active: false, lastTime: 0 });

  const [showMetrics, setShowMetrics] = useState(true);
  const [soundEnabled, setSoundEnabled] = useState(false);
  const [micEnabled, setMicEnabled] = useState(false);
  const [growthSpeed, setGrowthSpeed] = useState(1.0);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [fps, setFps] = useState(60);
  const [drawQuality, setDrawQuality] = useState(1.0);
  const [resetKey, setResetKey] = useState(0);

  const zoomRef = useRef(1);
  const growthSpeedRef = useRef(1.0);
  const drawQualityRef = useRef(1.0);
  const fpsHistory = useRef([]);
  const lastFrameTime = useRef(Date.now());
  const qualityCounter = useRef(0);
  const touchesRef = useRef(new Map());
  const energyFlowsRef = useRef([]);

  const [metrics, setMetrics] = useState({
    beta: 0.5,
    dAperture: 1.5,
    dField: 1.5,
    dBoundary: 3.0,
    rho: 1.0,
    fieldCoherence: 0,
    phaseCoherence: 0,
    patternCount: 0,
    convergenceNorm: 0,
    emergenceNorm: 0,
  });

  // ─── Audio System ──────────────────────────────────────────
  const initAudio = useCallback(() => {
    if (!audioContextRef.current) {
      const AC = window.AudioContext || window.webkitAudioContext;
      audioContextRef.current = new AC();
      audioAnalyserRef.current = audioContextRef.current.createAnalyser();
      audioAnalyserRef.current.fftSize = 256;
      audioAnalyserRef.current.connect(audioContextRef.current.destination);
      audioDataRef.current = new Uint8Array(audioAnalyserRef.current.frequencyBinCount);
    }
    return audioContextRef.current;
  }, []);

  const initMicrophone = useCallback(async () => {
    try {
      const ctx = initAudio();
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      micStreamRef.current = stream;
      const source = ctx.createMediaStreamSource(stream);
      micAnalyserRef.current = ctx.createAnalyser();
      micAnalyserRef.current.fftSize = 512;
      micAnalyserRef.current.smoothingTimeConstant = 0.8;
      micDataRef.current = new Uint8Array(micAnalyserRef.current.frequencyBinCount);
      source.connect(micAnalyserRef.current);
      return true;
    } catch (e) {
      console.error('Mic denied:', e);
      return false;
    }
  }, [initAudio]);

  const stopMicrophone = useCallback(() => {
    if (micStreamRef.current) {
      micStreamRef.current.getTracks().forEach(t => t.stop());
      micStreamRef.current = null;
    }
    micAnalyserRef.current = null;
    micDataRef.current = null;
  }, []);

  const playTone = useCallback((frequency, duration, volume = 0.08) => {
    if (!soundEnabled || !audioContextRef.current) return;
    const ctx = audioContextRef.current;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(frequency, ctx.currentTime);
    gain.gain.setValueAtTime(volume, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
    osc.connect(gain);
    gain.connect(audioAnalyserRef.current || ctx.destination);
    osc.start(ctx.currentTime);
    osc.stop(ctx.currentTime + duration);
  }, [soundEnabled]);

  const playHarmonic = useCallback((baseFreq, resonance, dur = 0.5) => {
    if (!soundEnabled || !audioContextRef.current) return;
    [1, 1.5, 2, 3].forEach((h, i) => {
      setTimeout(() => playTone(baseFreq * h, dur * (1 - i * 0.2), 0.04 * resonance / (i + 1)), i * 40);
    });
  }, [soundEnabled, playTone]);

  // ─── Main Simulation ───────────────────────────────────────
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const W = canvas.width = window.innerWidth;
    const H = canvas.height = window.innerHeight;
    const cx = W / 2;
    const cy = H / 2;
    let time = 0;

    // ════════════════════════════════════════════════════════
    //  CIRCUMPUNCT STATE — The Six Coupled Variables
    //  ∂Φ/∂t = D∇²Φ − γΦ + Vψ          (field evolution)
    //  z = U*Φ                            (convergence)
    //  z̃ = e^{iπβ} z                     (aperture rotation)
    //  ∂ψ/∂t = −αψ + tanh(z̃)            (aperture dynamics)
    //  ∂c/∂t = −λc + f(β)⊙c + g(β)⊙H(z) (memory/boundary)
    //  ∂β/∂t = κ(|z|/(|z|+|ψ|+ε) − β)   (opening feedback)
    // ════════════════════════════════════════════════════════

    // System-level circumpunct state
    let systemState = {
      // Field (Φ) — represented as complex amplitude array
      Phi: Array.from({ length: 64 }, () => ({
        re: (Math.random() - 0.5) * 0.1,
        im: (Math.random() - 0.5) * 0.1,
        x: 0, y: 0
      })),
      // Aperture state (ψ)
      psi: { re: 0.01, im: 0.01 },
      // Convergence result (z)
      z: { re: 0, im: 0 },
      // Rotated convergence (z̃)
      zTilde: { re: 0, im: 0 },
      // Opening parameter β ∈ [0,1]
      beta: 0.5,
      // Memory/boundary state (c)
      c: Array.from({ length: 16 }, () => 0),
      // Derived quantities
      convergenceNorm: 0,   // |⊛|
      emergenceNorm: 0,     // |☀️|
      rho: 1.0,             // ω/α regime parameter
    };

    // Parameters from the coupled system
    const params = {
      D: 0.1,       // diffusion coefficient
      gamma: 0.05,  // field decay
      V: 0.8,       // aperture-field coupling
      alpha: 0.3,   // aperture decay rate
      lambda: 0.1,  // memory decay
      kappa: 0.05,  // β feedback rate
      epsilon: 0.01 // regularization
    };

    // ═══════ Entities ═══════
    let circumpuncts = [];  // Each is a ⊙ = Φ(•, ○) entity
    let circuits = [];      // Connections between entities
    let energyPulses = [];  // Flow pulses along circuits
    let brainClouds = [];   // Emergent field structures
    let expandingCells = [];
    let brainFormed = false;
    let brainFormationProgress = 0;
    let collectiveBreath = 0;
    let audioInfluence = 0;
    let dominantNote = null;
    let noteHistory = [];

    // ═══════════════════════════════════════════════════════
    //  CIRCUMPUNCT ENTITY CLASS — ⊙ = Φ(•, ○)
    //  Each entity has its own aperture, field, and boundary
    // ═══════════════════════════════════════════════════════
    class CircumpunctEntity {
      constructor(angle, hue, birthTime) {
        this.id = Math.random();
        this.angle = angle;
        this.baseHue = hue;
        this.hue = hue;
        this.birthTime = birthTime;
        this.age = 0;
        this.scale = 1;
        this.baseLength = 100;
        this.phaseOffset = Math.random() * Math.PI * 2;

        // ── Aperture (•) state ──
        this.aperture = {
          beta: 0.3 + Math.random() * 0.4, // opening parameter
          psi: { re: Math.random() * 0.1, im: Math.random() * 0.1 },
          phase: Math.random() * Math.PI * 2,
          gateOpenness: 0.5, // β_•
        };

        // ── Field (Φ) state ──
        this.field = {
          amplitude: 0.5 + Math.random() * 0.5,
          phase: Math.random() * Math.PI * 2,
          coherence: 0,
          flowRatio: 0.5, // β_Φ
          convergenceStrength: 0,
          emergenceStrength: 0,
        };

        // ── Boundary (○) state ──
        this.boundary = {
          autonomy: 0.5, // β_○
          radius: 5 + Math.random() * 10,
          stability: 0,
          memoryTrace: [],
        };

        // Derived
        this.geometryType = Math.random() * 6;
        this.evolutionStage = Math.random() * 3;
        this.neighbors = [];
        this.circuitPartners = new Set();
        this.connectionWeights = new Map();
        this.resonanceMemory = new Map();
        this.harmonicStrength = 0;
        this.connectedToCloud = false;
        this.cloudInfluence = 0;
        this.fieldEnergyBoost = 0;
        this.gravitationalMass = 0;
        this.userSpawned = false;
        this.spawnEnergy = 0;
        this.randomOffsetX = (Math.random() - 0.5) * 25;
        this.randomOffsetY = (Math.random() - 0.5) * 25;
        this.probabilityCloud = Array.from({ length: 8 }, () => ({
          angle: Math.random() * Math.PI * 2,
          dist: Math.random() * 18,
          phase: Math.random() * Math.PI * 2
        }));
        this.nestingPoint = null;
        this.tensionStrength = 0;
        this.musicalNote = null;
        this.baseFrequency = 0;

        this.x = cx + Math.cos(angle) * this.baseLength * this.scale + this.randomOffsetX;
        this.y = cy + Math.sin(angle) * this.baseLength * this.scale + this.randomOffsetY;
      }

      // ═══ THE SIX COUPLED ODEs (per-entity) ═══
      updateCircumpunctDynamics(dt, allEntities) {
        const a = this.aperture;
        const f = this.field;
        const b = this.boundary;

        // 1. Convergence: z = U*Φ (gather from neighbors)
        let zRe = 0, zIm = 0;
        this.neighbors.forEach(n => {
          const dx = n.x - this.x;
          const dy = n.y - this.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          const kernel = Math.sqrt(Math.max(0.01, dist / 200)); // √r kernel
          zRe += n.field.amplitude * Math.cos(n.field.phase) * kernel;
          zIm += n.field.amplitude * Math.sin(n.field.phase) * kernel;
        });
        // Include self-field convergence
        zRe += f.amplitude * Math.cos(f.phase) * 0.3;
        zIm += f.amplitude * Math.sin(f.phase) * 0.3;
        const zNorm = Math.sqrt(zRe * zRe + zIm * zIm);

        // 2. Aperture rotation: z̃ = e^{iπβ} z
        const rotAngle = Math.PI * a.beta;
        const cosR = Math.cos(rotAngle);
        const sinR = Math.sin(rotAngle);
        const ztRe = zRe * cosR - zIm * sinR;
        const ztIm = zRe * sinR + zIm * cosR;

        // 3. Aperture dynamics: ∂ψ/∂t = −αψ + tanh(z̃)
        const tanhMag = Math.tanh(Math.sqrt(ztRe * ztRe + ztIm * ztIm));
        const ztPhase = Math.atan2(ztIm, ztRe);
        a.psi.re += (-params.alpha * a.psi.re + tanhMag * Math.cos(ztPhase)) * dt;
        a.psi.im += (-params.alpha * a.psi.im + tanhMag * Math.sin(ztPhase)) * dt;

        // 4. Opening feedback: ∂β/∂t = κ(|z|/(|z|+|ψ|+ε) − β)
        const psiNorm = Math.sqrt(a.psi.re ** 2 + a.psi.im ** 2);
        const betaTarget = zNorm / (zNorm + psiNorm + params.epsilon);
        a.beta += params.kappa * (betaTarget - a.beta) * dt;
        a.beta = Math.max(0.01, Math.min(0.99, a.beta));

        // 5. Field evolution: ∂Φ/∂t = D∇²Φ − γΦ + Vψ
        // Approximate Laplacian from neighbors
        let laplacianRe = 0, laplacianIm = 0;
        if (this.neighbors.length > 0) {
          this.neighbors.forEach(n => {
            laplacianRe += n.field.amplitude * Math.cos(n.field.phase) - f.amplitude * Math.cos(f.phase);
            laplacianIm += n.field.amplitude * Math.sin(n.field.phase) - f.amplitude * Math.sin(f.phase);
          });
          laplacianRe /= this.neighbors.length;
          laplacianIm /= this.neighbors.length;
        }

        let phiRe = f.amplitude * Math.cos(f.phase);
        let phiIm = f.amplitude * Math.sin(f.phase);
        phiRe += (params.D * laplacianRe - params.gamma * phiRe + params.V * a.psi.re) * dt;
        phiIm += (params.D * laplacianIm - params.gamma * phiIm + params.V * a.psi.im) * dt;
        f.amplitude = Math.sqrt(phiRe * phiRe + phiIm * phiIm);
        f.phase = Math.atan2(phiIm, phiRe);
        f.amplitude = Math.min(3, f.amplitude); // Clamp

        // 6. Memory/boundary: ∂c/∂t = −λc + f(β)c + g(β)H(z)
        b.memoryTrace.push(a.beta);
        if (b.memoryTrace.length > 32) b.memoryTrace.shift();
        b.stability = b.memoryTrace.reduce((s, v) => s + Math.abs(v - 0.5), 0) / b.memoryTrace.length;
        b.stability = 1 - Math.min(1, b.stability * 2);

        // Flow balance
        f.convergenceStrength = zNorm;
        f.emergenceStrength = f.amplitude;
        f.flowRatio = f.convergenceStrength / (f.convergenceStrength + f.emergenceStrength + params.epsilon);

        // Coherence from neighbor phase alignment
        if (this.neighbors.length > 0) {
          let coherenceSum = 0;
          this.neighbors.forEach(n => {
            const dPhi = f.phase - n.field.phase;
            coherenceSum += Math.cos(dPhi); // Phase coherence: cos²(Δφ/2) related
          });
          f.coherence = Math.max(0, coherenceSum / this.neighbors.length);
        }

        // ρ criterion: ω/α
        const omega = f.emergenceStrength * 2;
        const alpha_local = f.convergenceStrength * 2 + params.epsilon;

        // Update β decomposition
        a.gateOpenness = a.beta;
        f.flowRatio = f.convergenceStrength / (f.convergenceStrength + f.emergenceStrength + params.epsilon);
        b.autonomy = b.stability;
      }

      update(currentTime, allEntities) {
        this.age = currentTime - this.birthTime;
        const dt = 0.1 * growthSpeedRef.current;

        // Spawned energy decay
        if (this.userSpawned && this.spawnEnergy > 0) {
          this.spawnEnergy *= 0.98;
          this.scale = Math.min(1.5, this.scale + this.spawnEnergy * 0.03);
        }

        // Find neighbors
        this.neighbors = allEntities.filter(e => {
          if (e === this || !e.x) return false;
          const dx = this.x - e.x;
          const dy = this.y - e.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          return dist < 160 && dist > 5;
        });

        // Run the six coupled ODEs
        this.updateCircumpunctDynamics(dt, allEntities);

        // Update connection weights (Hebbian learning)
        this.neighbors.forEach(n => {
          const w = this.connectionWeights.get(n.id) || 0;
          const dist = Math.sqrt((this.x - n.x) ** 2 + (this.y - n.y) ** 2);
          const resonance = 1 - dist / 160;
          // Phase coherence transmission: T(Δφ) = cos²(Δφ/2)
          const dPhi = this.field.phase - n.field.phase;
          const transmission = Math.cos(dPhi / 2) ** 2;
          const newW = w + 0.01 * resonance * transmission * this.harmonicStrength;
          this.connectionWeights.set(n.id, Math.min(1, newW));
        });

        // Prune weak connections
        for (let [id, w] of this.connectionWeights.entries()) {
          if (w < 0.08) {
            this.connectionWeights.delete(id);
          } else {
            this.connectionWeights.set(id, w * 0.995);
          }
        }

        this.gravitationalMass = Array.from(this.connectionWeights.values()).reduce((s, w) => s + w, 0) / 8;

        // Hue influenced by β and field phase
        const betaHueShift = (this.aperture.beta - 0.5) * 60;
        this.hue = (this.baseHue + betaHueShift + currentTime * 0.05 + audioInfluence * 40) % 360;

        // Evolution
        this.evolutionStage += (0.002 + this.field.amplitude * 0.001) * growthSpeedRef.current;
        this.geometryType += Math.sin(this.evolutionStage) * 0.015;

        // Position with β-influenced wobble
        const length = this.baseLength * this.scale;
        const betaWobble = Math.sin(currentTime * 0.02 + this.phaseOffset) * (5 + this.aperture.beta * 10);
        this.x = cx + Math.cos(this.angle) * length + this.randomOffsetX + betaWobble;
        this.y = cy + Math.sin(this.angle) * length + this.randomOffsetY + betaWobble * 0.7;
      }

      // ═══ DRAWING ═══
      draw(ctx, currentTime) {
        const q = drawQualityRef.current;

        // Probability cloud (field uncertainty)
        if (q > 0.7) {
          this.probabilityCloud.forEach(p => {
            const a = this.angle + p.angle + Math.sin(currentTime * 0.01 + p.phase) * 0.4;
            const d = p.dist * (1 + Math.sin(currentTime * 0.015 + p.phase) * 0.3) * this.field.amplitude;
            const px = this.x + Math.cos(a) * d;
            const py = this.y + Math.sin(a) * d;
            ctx.fillStyle = `hsla(${this.hue}, 65%, 60%, ${0.08 * this.field.coherence})`;
            ctx.beginPath();
            ctx.arc(px, py, 2.5, 0, Math.PI * 2);
            ctx.fill();
          });
        }

        // Connection lines with transmission weight
        if (q > 0.5) {
          this.neighbors.forEach(n => {
            const w = this.connectionWeights.get(n.id);
            if (w && w > 0.2) {
              const dPhi = this.field.phase - n.field.phase;
              const T = Math.cos(dPhi / 2) ** 2; // Phase coherence
              const alpha = w * T * 0.35;
              const mixHue = (this.hue + n.hue) / 2;
              ctx.strokeStyle = `hsla(${mixHue}, 70%, 60%, ${alpha})`;
              ctx.lineWidth = 0.8 + w * 2.5;
              ctx.beginPath();
              ctx.moveTo(this.x, this.y);
              ctx.lineTo(n.x, n.y);
              ctx.stroke();
            }
          });
        }

        // Branch structure
        if (q < 0.5) {
          this.drawSimple(ctx);
        } else {
          const length = this.baseLength * this.scale;
          const distFromCenter = Math.sqrt((this.x - cx) ** 2 + (this.y - cy) ** 2);
          const validationStrength = Math.max(0.2, 1 - distFromCenter / 400);
          const boost = 1 + this.fieldEnergyBoost;
          const massBoost = 1 + Math.min(this.gravitationalMass, 1.2);
          const alpha = Math.min(0.85, (0.3 + this.scale * 0.55) * validationStrength * boost * massBoost);

          if (this.gravitationalMass > 0.4) {
            ctx.shadowBlur = 6 * this.gravitationalMass * q;
            ctx.shadowColor = `hsla(${this.hue}, 80%, 65%, ${this.gravitationalMass * 0.12})`;
          }

          const maxDepth = Math.ceil(5 * q);
          this.drawBranch(ctx, cx, cy, length, this.angle, maxDepth, this.hue, alpha, currentTime, 0, validationStrength);
          ctx.shadowBlur = 0;
          this.fieldEnergyBoost = 0;
        }
      }

      drawSimple(ctx) {
        const alpha = 0.4 + this.scale * 0.4;
        ctx.strokeStyle = `hsla(${this.hue}, 70%, 55%, ${alpha})`;
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(this.x, this.y);
        ctx.stroke();
        ctx.fillStyle = `hsla(${this.hue}, 75%, 60%, ${alpha})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, 4 * this.scale, 0, Math.PI * 2);
        ctx.fill();
      }

      drawBranch(ctx, x, y, length, angle, depth, hue, baseAlpha, t, gen, validation) {
        if (depth === 0 || length < 1.5) {
          this.drawBody(ctx, x, y, angle, hue, Math.max(baseAlpha, 0.25), t);
          return;
        }
        const endX = x + length * Math.cos(angle);
        const endY = y + length * Math.sin(angle);
        const distFromCenter = Math.sqrt((endX - cx) ** 2 + (endY - cy) ** 2);
        const branchVal = Math.max(0.2, 1 - distFromCenter / 400);
        const alpha = baseAlpha * (depth / 5.5) * branchVal;
        const localHue = (hue + gen * 7 + t * 0.04) % 360;

        ctx.strokeStyle = `hsla(${localHue}, 72%, 55%, ${alpha})`;
        ctx.lineWidth = Math.max(0.5, depth * 0.9 * this.scale);
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(endX, endY);
        ctx.stroke();

        if (depth > 2 && depth < 6) {
          this.drawBody(ctx, endX, endY, angle, localHue, Math.max(alpha, 0.2), t);
        }

        // Branch angle influenced by β — more open = wider branching
        const betaAngle = Math.PI / (5 + this.aperture.beta * 2);
        const variation = Math.sin(gen * 0.5 + this.phaseOffset) * 0.25;
        const branchAngle = betaAngle + variation;
        const lengthMult = 0.65 + Math.sin(t * 0.008 + gen) * 0.04;

        this.drawBranch(ctx, endX, endY, length * lengthMult, angle - branchAngle, depth - 1, localHue, baseAlpha, t, gen + 1, branchVal);
        this.drawBranch(ctx, endX, endY, length * lengthMult, angle + branchAngle, depth - 1, localHue, baseAlpha, t, gen + 1, branchVal);

        if (depth > 4 && Math.sin(t * 0.012 + gen + this.phaseOffset) > 0.6) {
          this.drawBranch(ctx, endX, endY, length * lengthMult * 0.7, angle, depth - 1, localHue, baseAlpha, t, gen + 1, branchVal);
        }
      }

      drawBody(ctx, x, y, angle, hue, alpha, t) {
        const size = Math.max(2.5, 4.5 * this.scale);
        const rotation = t * 0.008 * this.evolutionStage + this.phaseOffset;
        const stage = Math.floor(this.geometryType) % 6;

        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(rotation);
        ctx.fillStyle = `hsla(${hue}, 78%, 60%, ${alpha})`;
        ctx.strokeStyle = `hsla(${hue}, 88%, 70%, ${alpha * 0.8})`;
        ctx.lineWidth = 0.8;
        ctx.beginPath();

        const sides = [3, 4, 5, 6, 0, 0][stage];
        if (sides > 0 && stage !== 4) {
          for (let i = 0; i <= sides; i++) {
            const a = (i / sides) * Math.PI * 2 - Math.PI / 2;
            const px = Math.cos(a) * size;
            const py = Math.sin(a) * size;
            i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
          }
        } else if (stage === 4) {
          // Star
          for (let i = 0; i <= 10; i++) {
            const a = (i / 10) * Math.PI * 2 - Math.PI / 2;
            const r = i % 2 === 0 ? size : size * 0.45;
            const px = Math.cos(a) * r;
            const py = Math.sin(a) * r;
            i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
          }
        } else {
          // Circle (⊙ resonance)
          ctx.arc(0, 0, size, 0, Math.PI * 2);
        }

        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // Draw aperture indicator (•) at center of circumpunct bodies
        if (stage === 5 && this.scale > 0.5) {
          const betaColor = this.aperture.beta > 0.6 ? '120' : this.aperture.beta < 0.4 ? '0' : '60';
          ctx.fillStyle = `hsla(${betaColor}, 90%, 70%, ${alpha * 0.9})`;
          ctx.beginPath();
          ctx.arc(0, 0, size * 0.25, 0, Math.PI * 2);
          ctx.fill();
        }

        ctx.restore();
      }
    }

    // ═══════════════════════════════════════════════════════
    //  BRAIN CLOUD — Emergent field structure (Φ)
    // ═══════════════════════════════════════════════════════
    class BrainCloud {
      constructor(angle, distance, birthTime) {
        this.angle = angle + (Math.random() - 0.5) * 0.2;
        this.baseDistance = distance + (Math.random() - 0.5) * 50;
        this.distance = this.baseDistance;
        this.birthTime = birthTime;
        this.phaseOffset = Math.random() * Math.PI * 2;
        this.hue = 200 + Math.random() * 60;
        this.alpha = 0;
        this.particles = [];
        this.connectedEntities = [];
        this.energyLevel = 0;
        this.lastResonanceTime = 0;
        this.learningRate = 0.05;
        this.entityAffinities = new Map();

        const count = 18 + Math.floor(Math.random() * 18);
        for (let i = 0; i < count; i++) {
          this.particles.push({
            angle: angle + (Math.random() - 0.5) * 0.7,
            distOffset: (Math.random() - 0.5) * 45,
            size: 2 + Math.random() * 3.5,
            phaseOffset: Math.random() * Math.PI * 2,
            speed: 0.002 + Math.random() * 0.003,
            energy: Math.random(),
            excitement: 0,
            shape: Math.random() * 6,
            targetShape: 0,
            rotation: Math.random() * Math.PI * 2,
            rotationSpeed: (Math.random() - 0.5) * 0.015,
            nestingEntities: [],
            bondStrength: new Map(),
            convergencePhase: Math.random() * Math.PI * 2,
            targetEntity: null, // Fixed: always initialized
          });
        }
      }

      update(t, allEntities, globalBreath) {
        const age = t - this.birthTime;
        this.alpha = age < 60 ? age / 60 : Math.min(0.65, this.alpha);

        const wave = Math.sin(t * 0.01 + this.phaseOffset) * 10;
        const breathWave = globalBreath * 18;
        const audioWave = audioInfluence * 25;
        this.distance = this.baseDistance + wave + breathWave + audioWave;

        // Find connected entities
        this.connectedEntities = allEntities.filter(e => {
          if (!e || e.x === undefined) return false;
          const diff = Math.abs(this.angle - e.angle);
          return Math.min(diff, Math.PI * 2 - diff) < 0.85;
        });

        // Update affinities using phase coherence T(Δφ) = cos²(Δφ/2)
        this.connectedEntities.forEach(entity => {
          const curr = this.entityAffinities.get(entity.id) || 0;
          const phaseCoherence = Math.cos((entity.field.phase - this.phaseOffset) / 2) ** 2;
          const newAffinity = curr + this.learningRate * phaseCoherence * entity.field.amplitude;
          this.entityAffinities.set(entity.id, Math.min(1, newAffinity));
          entity.connectedToCloud = true;
          entity.cloudInfluence = this.hue;
          entity.fieldEnergyBoost = this.energyLevel * (1 + newAffinity * 0.5);
          entity.harmonicStrength = Math.min(1, entity.harmonicStrength + phaseCoherence * 0.08);
        });

        // Restructure toward strongest affinity
        if (this.entityAffinities.size > 0 && age > 200) {
          let maxAffinity = 0;
          let bestEntity = null;
          this.connectedEntities.forEach(e => {
            const aff = this.entityAffinities.get(e.id) || 0;
            if (aff > maxAffinity) { maxAffinity = aff; bestEntity = e; }
          });
          if (bestEntity && maxAffinity > 0.4) {
            const targetAngle = Math.atan2(bestEntity.y - cy, bestEntity.x - cx);
            this.angle += (targetAngle - this.angle) * 0.004 * maxAffinity;
          }
        }

        this.energyLevel = this.connectedEntities.length * 0.1;
      }

      spawnCell(t, cells) {
        if (this.alpha > 0.4 && drawQualityRef.current > 0.4) {
          cells.push(new ExpandingCell(this, t));
        }
      }

      draw(ctx, t, fieldCoherence, allEntities) {
        const q = drawQualityRef.current;
        const particlesToDraw = Math.ceil(this.particles.length * q);
        const positions = [];

        for (let i = 0; i < particlesToDraw; i++) {
          const p = this.particles[i];
          const baseAngle = p.angle + Math.sin(t * p.speed + p.phaseOffset) * 0.12;
          const baseDist = this.distance + p.distOffset + Math.cos(t * p.speed * 0.7) * 8;
          let px = cx + Math.cos(baseAngle) * baseDist;
          let py = cy + Math.sin(baseAngle) * baseDist;

          // Convergence pull toward connected entities
          if (p.targetEntity && p.excitement > 0.1) {
            const pull = p.excitement * 0.15;
            px += (p.targetEntity.x - px) * pull;
            py += (p.targetEntity.y - py) * pull;
          }

          p.energy = 0.3 + Math.sin(t * p.speed * 2 + p.phaseOffset) * 0.15;
          p.energy *= (1 + fieldCoherence * 0.4);
          p.energy += p.excitement * 0.25;
          p.excitement = Math.max(0, p.excitement * 0.95);
          p.rotation += p.rotationSpeed;

          // Shape morphing toward nearest entity
          let nearestEntity = null;
          let minDist = Infinity;
          this.connectedEntities.forEach(e => {
            const d = Math.sqrt((e.x - px) ** 2 + (e.y - py) ** 2);
            if (d < minDist) { minDist = d; nearestEntity = e; }
          });
          p.targetShape = nearestEntity && minDist < 180 ?
            Math.floor(nearestEntity.geometryType) % 6 :
            Math.floor(t * 0.008 + p.phaseOffset * 3) % 6;
          p.shape += (p.targetShape - p.shape) * 0.06;

          const particleHue = (this.hue + p.energy * 30 + fieldCoherence * 20) % 360;
          const particleAlpha = this.alpha * (0.4 + p.energy * 0.5) * q;
          const particleSize = p.size * (1 + p.excitement * 0.3) * (0.7 + fieldCoherence * 0.3);

          positions.push({ x: px, y: py, size: particleSize, shape: p.shape, rotation: p.rotation, hue: particleHue, alpha: particleAlpha, p });
        }

        // Membrane connections
        if (q > 0.6) {
          const memDist = 70;
          positions.forEach((p1, i) => {
            positions.slice(i + 1).forEach(p2 => {
              const dist = Math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2);
              if (dist < memDist) {
                const str = 1 - dist / memDist;
                const avgHue = (p1.hue + p2.hue) / 2;
                ctx.strokeStyle = `hsla(${avgHue}, 75%, 68%, ${(p1.alpha + p2.alpha) / 2 * str * 0.4})`;
                ctx.lineWidth = 0.8 + str * 1.8;
                ctx.beginPath();
                ctx.moveTo(p1.x, p1.y);
                ctx.lineTo(p2.x, p2.y);
                ctx.stroke();
              }
            });
          });
        }

        // Draw particles
        positions.forEach(pos => {
          const glow = (5 + fieldCoherence * 6 + pos.p.excitement * 5) * q;
          ctx.shadowBlur = glow;
          ctx.shadowColor = `hsla(${pos.hue}, 80%, 68%, ${pos.alpha * 0.6})`;
          this.drawShape(ctx, pos.x, pos.y, pos.size, pos.shape, pos.rotation, pos.hue, pos.alpha);
          ctx.shadowBlur = 0;
        });
      }

      drawShape(ctx, x, y, size, shapeIdx, rotation, hue, alpha) {
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(rotation);
        ctx.fillStyle = `hsla(${hue}, 85%, 72%, ${alpha})`;
        ctx.strokeStyle = `hsla(${hue}, 92%, 78%, ${alpha * 0.85})`;
        ctx.lineWidth = 0.8;
        ctx.beginPath();
        const base = Math.floor(shapeIdx) % 6;
        if (base === 5) {
          ctx.arc(0, 0, size, 0, Math.PI * 2);
        } else if (base === 4) {
          for (let i = 0; i <= 10; i++) {
            const a = (i / 10) * Math.PI * 2 - Math.PI / 2;
            const r = i % 2 === 0 ? size : size * 0.4;
            i === 0 ? ctx.moveTo(Math.cos(a) * r, Math.sin(a) * r) : ctx.lineTo(Math.cos(a) * r, Math.sin(a) * r);
          }
        } else {
          const sides = base + 3;
          for (let i = 0; i <= sides; i++) {
            const a = (i / sides) * Math.PI * 2 - Math.PI / 2;
            i === 0 ? ctx.moveTo(Math.cos(a) * size, Math.sin(a) * size) : ctx.lineTo(Math.cos(a) * size, Math.sin(a) * size);
          }
        }
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        ctx.restore();
      }
    }

    // ═══ CIRCUIT (Connection) ═══
    class Circuit {
      constructor(e1, e2, t) {
        this.e1 = e1; this.e2 = e2;
        this.birthTime = t; this.strength = 0; this.age = 0; this.lastPulseTime = t; this.lastSoundTime = 0;
      }
      update(t, connected, coherence) {
        this.age = t - this.birthTime;
        if (connected) {
          this.strength = Math.min(1, this.strength + 0.015 * (1 + coherence * 0.4));
        } else {
          this.strength = Math.max(0, this.strength - 0.008);
        }
      }
      shouldRemove() { return this.strength <= 0; }
      draw(ctx, coherence, t) {
        if (this.strength < 0.08 || drawQualityRef.current < 0.3) return;
        const alpha = this.strength * 0.4 * (1 + coherence * 0.25);
        const hue = (this.e1.hue + this.e2.hue) / 2;
        ctx.strokeStyle = `hsla(${hue}, 75%, 58%, ${alpha})`;
        ctx.lineWidth = 0.8 + this.strength + coherence * 0.8;
        ctx.beginPath(); ctx.moveTo(this.e1.x, this.e1.y); ctx.lineTo(this.e2.x, this.e2.y); ctx.stroke();
      }
    }

    // ═══ ENERGY PULSE ═══
    class EnergyPulse {
      constructor(circuit, dir) {
        this.circuit = circuit; this.dir = dir;
        this.progress = dir > 0 ? 0 : 1;
        this.speed = 0.025; this.life = 1;
        this.hue = (circuit.e1.hue + circuit.e2.hue) / 2;
      }
      update(coherence) {
        this.progress += this.speed * this.dir * (1 + coherence * 0.4) * growthSpeedRef.current;
        this.life -= 0.008;
        return this.life > 0 && this.progress >= 0 && this.progress <= 1;
      }
      draw(ctx, coherence) {
        if (drawQualityRef.current < 0.4) return;
        const x = this.circuit.e1.x + (this.circuit.e2.x - this.circuit.e1.x) * this.progress;
        const y = this.circuit.e1.y + (this.circuit.e2.y - this.circuit.e1.y) * this.progress;
        const alpha = this.life * 0.25 * (1 + coherence * 0.15);
        ctx.shadowBlur = (6 + coherence * 3) * drawQualityRef.current;
        ctx.shadowColor = `hsla(${this.hue}, 78%, 63%, ${alpha})`;
        ctx.fillStyle = `hsla(${this.hue}, 78%, 68%, ${alpha})`;
        ctx.beginPath(); ctx.arc(x, y, 2 + coherence * 0.3, 0, Math.PI * 2); ctx.fill();
        ctx.shadowBlur = 0;
      }
    }

    // ═══ EXPANDING CELL ═══
    class ExpandingCell {
      constructor(cloud, t) {
        this.cloud = cloud; this.birthTime = t; this.age = 0;
        this.angle = cloud.angle + (Math.random() - 0.5) * 0.25;
        this.distance = cloud.distance; this.hue = cloud.hue + (Math.random() - 0.5) * 18;
        this.expansionSpeed = (0.5 + Math.random() * 0.4) * growthSpeedRef.current;
        this.maxRadius = 10 + Math.random() * 15; this.currentRadius = 0;
        this.lifecycle = 0; this.lifecycleSpeed = (0.005 + Math.random() * 0.003) * growthSpeedRef.current;
        this.rotation = 0; this.rotationSpeed = (Math.random() - 0.5) * 0.012;
        this.fractalSeed = Math.random() * 3 - 1.5; this.fractalComplexity = 3 + Math.floor(Math.random() * 2);
      }
      update() {
        this.age++; this.lifecycle += this.lifecycleSpeed; this.distance += this.expansionSpeed;
        if (this.lifecycle < 1) this.currentRadius = this.maxRadius * this.lifecycle;
        else if (this.lifecycle < 2) this.currentRadius = this.maxRadius;
        else if (this.lifecycle < 3) this.currentRadius = this.maxRadius * (1 + Math.sin(this.age * 0.04) * 0.08);
        else this.currentRadius = this.maxRadius * (1 - (this.lifecycle - 3));
        this.rotation += this.rotationSpeed;
        this.x = cx + Math.cos(this.angle) * this.distance;
        this.y = cy + Math.sin(this.angle) * this.distance;
        return this.lifecycle < 4 && this.distance < Math.max(W, H);
      }
      draw(ctx) {
        if (this.currentRadius < 0.5 || drawQualityRef.current < 0.5) return;
        let alpha = this.lifecycle < 1 ? this.lifecycle * 0.35 : this.lifecycle < 3 ? 0.35 : 0.35 * (1 - (this.lifecycle - 3));
        ctx.save(); ctx.translate(this.x, this.y); ctx.rotate(this.rotation);
        const branches = Math.ceil(4 * drawQualityRef.current);
        for (let i = 0; i < branches; i++) {
          const a = (i / branches) * Math.PI * 2;
          this.drawFractalBranch(ctx, 0, 0, this.currentRadius * 0.4, a, Math.ceil(this.fractalComplexity * drawQualityRef.current), this.hue, alpha);
        }
        ctx.shadowBlur = 6 * drawQualityRef.current;
        ctx.shadowColor = `hsla(${this.hue}, 88%, 68%, ${alpha * 0.5})`;
        ctx.fillStyle = `hsla(${this.hue}, 82%, 72%, ${alpha * 0.6})`;
        ctx.beginPath(); ctx.arc(0, 0, this.currentRadius * 0.12, 0, Math.PI * 2); ctx.fill();
        ctx.shadowBlur = 0; ctx.restore();
      }
      drawFractalBranch(ctx, x, y, len, angle, depth, hue, alpha) {
        if (depth === 0 || len < 0.5) return;
        const ex = x + len * Math.cos(angle);
        const ey = y + len * Math.sin(angle);
        ctx.strokeStyle = `hsla(${hue}, 72%, 58%, ${alpha * (depth / this.fractalComplexity)})`;
        ctx.lineWidth = Math.max(0.3, depth * 0.4);
        ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(ex, ey); ctx.stroke();
        const ba = Math.PI / 4 + this.fractalSeed * 0.15;
        this.drawFractalBranch(ctx, ex, ey, len * 0.62, angle - ba, depth - 1, hue + 4, alpha);
        this.drawFractalBranch(ctx, ex, ey, len * 0.62, angle + ba, depth - 1, hue - 4, alpha);
      }
    }

    // ═══ AUDIO ANALYSIS ═══
    const frequencyToNote = (freq) => {
      const names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
      const halfSteps = 12 * Math.log2(freq / 440);
      const idx = Math.round(halfSteps) + 9;
      return `${names[((idx % 12) + 12) % 12]}${Math.floor(idx / 12) + 4}`;
    };

    const analyzeAudio = () => {
      if (micAnalyserRef.current && micDataRef.current) {
        micAnalyserRef.current.getByteFrequencyData(micDataRef.current);
        let maxAmp = 0, domFreq = 0;
        const sr = audioContextRef.current?.sampleRate || 44100;
        for (let i = 0; i < micDataRef.current.length; i++) {
          const amp = micDataRef.current[i];
          const freq = (i * sr) / micAnalyserRef.current.fftSize;
          if (amp > 45 && freq > 80 && freq < 2000 && amp > maxAmp) {
            maxAmp = amp; domFreq = freq;
          }
        }
        if (domFreq > 0 && maxAmp > 50) {
          const note = frequencyToNote(domFreq);
          dominantNote = { frequency: domFreq, note, amplitude: maxAmp / 255 };
          noteHistory.push({ note, frequency: domFreq, time: time, amplitude: maxAmp / 255 });
          if (noteHistory.length > 32) noteHistory.shift();
          if (noteHistory.length >= 4) {
            const pattern = noteHistory.slice(-4).map(n => n.note).join('-');
            const mem = melodicMemory.current.get(pattern) || { count: 0, frequencies: [] };
            mem.count++; mem.frequencies = noteHistory.slice(-4).map(n => n.frequency);
            melodicMemory.current.set(pattern, mem);
          }
          learnedMelody.current.push(dominantNote);
          if (learnedMelody.current.length > 64) learnedMelody.current.shift();
        }
        audioInfluence = micDataRef.current.reduce((a, b) => a + b, 0) / micDataRef.current.length / 255;
      } else if (audioAnalyserRef.current && audioDataRef.current) {
        audioAnalyserRef.current.getByteFrequencyData(audioDataRef.current);
        audioInfluence = audioDataRef.current.reduce((a, b) => a + b, 0) / audioDataRef.current.length / 255;
      }
    };

    // ═══ DRAWING HELPERS ═══
    const drawFieldGlow = () => {
      if (!brainFormed || systemState.beta < 0.2 || drawQualityRef.current < 0.6) return;
      const radius = 100 + collectiveBreath * 35;
      const intensity = Math.abs(systemState.beta - 0.5) < 0.2 ? 0.15 : 0.06;
      // Hue based on β: balanced (0.5) = blue-white, skewed = warm/cool
      const gH = systemState.beta > 0.5 ? 180 : 30;
      const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius);
      grad.addColorStop(0, `hsla(${gH}, 50%, 80%, ${intensity})`);
      grad.addColorStop(0.5, `hsla(${gH}, 40%, 70%, ${intensity * 0.35})`);
      grad.addColorStop(1, `hsla(${gH}, 40%, 70%, 0)`);
      ctx.fillStyle = grad;
      ctx.beginPath(); ctx.arc(cx, cy, radius, 0, Math.PI * 2); ctx.fill();
    };

    const drawConservationRings = () => {
      if (!brainFormed || drawQualityRef.current < 0.5) return;
      const beta = systemState.beta;
      const dA = 1 + beta;
      const dF = 2 - beta;
      // Draw three concentric rings representing D_•, D_Φ, D_○
      [[dA / 3, '50, 220, 255', '•'], [dF / 3, '180, 120, 255', 'Φ'], [1, '255, 180, 100', '○']].forEach(([frac, color, label], i) => {
        const r = 60 + i * 40 + collectiveBreath * 8;
        const alpha = 0.06 + systemState.beta * 0.04;
        ctx.strokeStyle = `rgba(${color}, ${alpha})`;
        ctx.lineWidth = 0.6 + frac * 0.4;
        ctx.setLineDash([3, 5]);
        ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2 * frac); ctx.stroke();
        ctx.setLineDash([]);
      });
    };

    const drawEnergyFlows = () => {
      energyFlowsRef.current = energyFlowsRef.current.filter(flow => {
        flow.age++; flow.strength *= 0.94;
        if (flow.strength < 0.08 || flow.age > 80) return false;
        const alpha = flow.strength * 0.35;
        const grad = ctx.createLinearGradient(flow.x1, flow.y1, flow.x2, flow.y2);
        grad.addColorStop(0, `rgba(100, 200, 255, ${alpha})`);
        grad.addColorStop(1, `rgba(200, 100, 255, ${alpha * 0.5})`);
        ctx.strokeStyle = grad; ctx.lineWidth = 2.5 * flow.strength; ctx.lineCap = 'round';
        ctx.beginPath(); ctx.moveTo(flow.x1, flow.y1); ctx.lineTo(flow.x2, flow.y2); ctx.stroke();
        circumpuncts.forEach(e => {
          const dx = e.x - flow.x2;
          const dy = e.y - flow.y2;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 90) {
            const force = (1 - dist / 90) * flow.strength * 0.08;
            e.angle += Math.sin(Math.atan2(flow.y2 - flow.y1, flow.x2 - flow.x1) - e.angle) * force;
          }
        });
        return true;
      });
    };

    const updateFPS = () => {
      const now = Date.now();
      const delta = now - lastFrameTime.current;
      const currentFPS = 1000 / delta;
      lastFrameTime.current = now;
      fpsHistory.current.push(currentFPS);
      if (fpsHistory.current.length > 60) fpsHistory.current.shift();
      const avg = fpsHistory.current.reduce((a, b) => a + b, 0) / fpsHistory.current.length;
      setFps(Math.round(avg));
      if (avg < 25) {
        qualityCounter.current--;
        if (qualityCounter.current < -10) { drawQualityRef.current = Math.max(0.2, drawQualityRef.current - 0.08); qualityCounter.current = 0; }
      } else if (avg > 40) {
        qualityCounter.current++;
        if (qualityCounter.current > 25) { drawQualityRef.current = Math.min(1.0, drawQualityRef.current + 0.04); qualityCounter.current = 0; }
      } else { qualityCounter.current = Math.max(-5, Math.min(5, qualityCounter.current)); }
      setDrawQuality(drawQualityRef.current);
    };

    // ═══ EVENT HANDLERS ═══
    let isDragging = false;
    let dragStart = null;

    const handleMouseDown = (e) => {
      const rect = canvas.getBoundingClientRect();
      dragStart = { x: (e.clientX - rect.left) / zoomRef.current, y: (e.clientY - rect.top) / zoomRef.current };
      isDragging = true;
    };
    const handleMouseMove = (e) => {
      if (!isDragging || !dragStart) return;
      const rect = canvas.getBoundingClientRect();
      const x = (e.clientX - rect.left) / zoomRef.current;
      const y = (e.clientY - rect.top) / zoomRef.current;
      energyFlowsRef.current.push({ x1: dragStart.x, y1: dragStart.y, x2: x, y2: y, strength: 1, age: 0 });
      dragStart = { x, y };
    };
    const handleMouseUp = (e) => {
      if (!isDragging) {
        const rect = canvas.getBoundingClientRect();
        const clickX = (e.clientX - rect.left) / zoomRef.current;
        const clickY = (e.clientY - rect.top) / zoomRef.current;
        const angle = Math.atan2(clickY - cy, clickX - cx);
        let hue = Math.random() * 360;
        let geom = Math.random() * 6;
        if (dominantNote) {
          hue = ((dominantNote.frequency - 80) / 1920) * 360;
          geom = dominantNote.amplitude * 6;
        }
        const newEntity = new CircumpunctEntity(angle, hue, time);
        newEntity.baseLength = Math.min(Math.sqrt((clickX - cx) ** 2 + (clickY - cy) ** 2), 250);
        newEntity.geometryType = geom;
        newEntity.userSpawned = true;
        newEntity.spawnEnergy = 1.8;
        circumpuncts.push(newEntity);
        playTone(200 + (hue / 360) * 400, 0.2, 0.12);

        if (brainFormed && brainClouds.length > 0) {
          const nearest = brainClouds.reduce((best, cloud) => {
            const diff = Math.abs(cloud.angle - angle);
            const d = Math.min(diff, Math.PI * 2 - diff) * 100;
            return d < best.dist ? { cloud, dist: d } : best;
          }, { cloud: null, dist: Infinity });
          if (nearest.cloud) {
            nearest.cloud.particles.forEach(p => {
              p.excitement = Math.min(2, p.excitement + 0.7);
              p.targetEntity = newEntity;
            });
            nearest.cloud.spawnCell(time, expandingCells);
          }
        }
      }
      isDragging = false; dragStart = null;
    };

    const handleTouchStart = (e) => {
      e.preventDefault();
      const rect = canvas.getBoundingClientRect();
      for (let t of e.touches) {
        touchesRef.current.set(t.identifier, { x: (t.clientX - rect.left) / zoomRef.current, y: (t.clientY - rect.top) / zoomRef.current });
      }
      if (e.touches.length >= 2) {
        for (let t of e.touches) {
          const x = (t.clientX - rect.left) / zoomRef.current;
          const y = (t.clientY - rect.top) / zoomRef.current;
          const angle = Math.atan2(y - cy, x - cx);
          const newEntity = new CircumpunctEntity(angle, Math.random() * 360, time);
          newEntity.userSpawned = true;
          circumpuncts.push(newEntity);
        }
      }
    };
    const handleTouchMove = (e) => {
      e.preventDefault();
      const rect = canvas.getBoundingClientRect();
      for (let t of e.touches) {
        const x = (t.clientX - rect.left) / zoomRef.current;
        const y = (t.clientY - rect.top) / zoomRef.current;
        const prev = touchesRef.current.get(t.identifier);
        if (prev) energyFlowsRef.current.push({ x1: prev.x, y1: prev.y, x2: x, y2: y, strength: 1, age: 0 });
        touchesRef.current.set(t.identifier, { x, y });
      }
    };
    const handleTouchEnd = (e) => {
      e.preventDefault();
      for (let t of e.changedTouches) touchesRef.current.delete(t.identifier);
    };

    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseup', handleMouseUp);
    canvas.addEventListener('touchstart', handleTouchStart, { passive: false });
    canvas.addEventListener('touchmove', handleTouchMove, { passive: false });
    canvas.addEventListener('touchend', handleTouchEnd, { passive: false });

    // ═══════════════════════════════════════════════════════
    //  MAIN ANIMATION LOOP — ⊛ → i → ☀️ per frame
    // ═══════════════════════════════════════════════════════
    const animate = () => {
      time++;
      collectiveBreath = Math.sin(time * 0.004) * 0.5 + 0.5;
      updateFPS();
      analyzeAudio();

      ctx.fillStyle = 'rgba(8, 8, 14, 0.14)';
      ctx.fillRect(0, 0, W, H);

      // ─── System-level β update from all entities ───
      if (circumpuncts.length > 0) {
        let betaSum = 0, convSum = 0, emergSum = 0;
        circumpuncts.forEach(e => {
          betaSum += e.aperture.beta;
          convSum += e.field.convergenceStrength;
          emergSum += e.field.emergenceStrength;
        });
        systemState.beta = betaSum / circumpuncts.length;
        systemState.convergenceNorm = convSum / circumpuncts.length;
        systemState.emergenceNorm = emergSum / circumpuncts.length;
        systemState.rho = systemState.emergenceNorm / (systemState.convergenceNorm + params.epsilon);
      }

      // ─── Brain formation ───
      if (circumpuncts.length > 12 && !brainFormed) {
        brainFormationProgress += 0.008;
        if (brainFormationProgress >= 1) {
          brainFormed = true;
          const num = 5 + Math.floor(Math.random() * 4);
          for (let i = 0; i < num; i++) {
            const angle = (i / num) * Math.PI * 2 + (Math.random() - 0.5) * 0.3;
            brainClouds.push(new BrainCloud(angle, 190 + Math.random() * 90, time));
          }
        }
      }

      // ─── Field coherence from brain ───
      let fieldCoherence = 0;
      if (brainFormed && brainClouds.length > 0) {
        fieldCoherence = Math.min(0.85, brainClouds.reduce((s, c) => s + c.energyLevel, 0) / brainClouds.length);
      }

      // ─── Zoom ───
      const breathZoom = 1 + Math.sin(time * 0.003) * 0.008;
      ctx.save();
      ctx.translate(cx, cy);
      ctx.scale(zoomRef.current * breathZoom, zoomRef.current * breathZoom);
      ctx.translate(-cx, -cy);

      // ─── Spawn new entities ───
      if (brainFormed) {
        brainClouds.forEach(cloud => {
          if (Math.random() < 0.012 * drawQualityRef.current * growthSpeedRef.current) {
            const rp = cloud.particles[Math.floor(Math.random() * cloud.particles.length)];
            rp.excitement = Math.min(2, rp.excitement + 1.3);
            if (Math.random() < 0.35) {
              let hue = Math.random() * 360;
              let geom = Math.random() * 6;
              if (dominantNote) {
                hue = ((dominantNote.frequency - 80) / 1920) * 360;
                geom = dominantNote.amplitude * 6;
              }
              const ne = new CircumpunctEntity(cloud.angle + (Math.random() - 0.5) * 0.3, hue, time);
              ne.geometryType = geom;
              if (dominantNote) { ne.musicalNote = dominantNote.note; ne.baseFrequency = dominantNote.frequency; }
              circumpuncts.push(ne);
              cloud.spawnCell(time, expandingCells);
            }
          }
        });

        // Harmonic response
        if (dominantNote && soundEnabled && time - harmonicResponse.current.lastTime > 55) {
          if (learnedMelody.current.length > 4 && Math.random() < 0.25) {
            const recent = learnedMelody.current.slice(-6);
            const rn = recent[Math.floor(Math.random() * recent.length)];
            [1, 1.5, 2].forEach((h, i) => {
              setTimeout(() => playTone(rn.frequency * h, 0.3, 0.04 / (i + 1)), i * 35);
            });
            harmonicResponse.current.lastTime = time;
          }
        }
      } else {
        if (Math.random() < 0.018 * drawQualityRef.current * growthSpeedRef.current) {
          let hue = Math.random() * 360;
          if (dominantNote) hue = ((dominantNote.frequency - 80) / 1920) * 360;
          const ne = new CircumpunctEntity(Math.random() * Math.PI * 2, hue, time);
          if (dominantNote) { ne.musicalNote = dominantNote.note; ne.baseFrequency = dominantNote.frequency; }
          circumpuncts.push(ne);
        }
      }

      // ─── Update all entities ───
      circumpuncts.forEach(e => e.update(time, circumpuncts));
      if (brainFormed) brainClouds.forEach(c => c.update(time, circumpuncts, collectiveBreath));
      expandingCells = expandingCells.filter(c => c.update());

      // ─── Draw ───
      drawFieldGlow();
      drawConservationRings();
      drawEnergyFlows();

      circumpuncts.forEach(e => e.draw(ctx, time));
      expandingCells.forEach(c => c.draw(ctx));

      if (brainFormed) {
        brainClouds.forEach(c => c.draw(ctx, time, fieldCoherence, circumpuncts));
        // Inter-cloud connections
        if (drawQualityRef.current > 0.5) {
          brainClouds.forEach((c1, i) => {
            brainClouds.slice(i + 1).forEach(c2 => {
              const diff = Math.abs(c1.angle - c2.angle);
              const nd = Math.min(diff, Math.PI * 2 - diff);
              if (nd < Math.PI / 4) {
                const x1 = cx + Math.cos(c1.angle) * c1.distance;
                const y1 = cy + Math.sin(c1.angle) * c1.distance;
                const x2 = cx + Math.cos(c2.angle) * c2.distance;
                const y2 = cy + Math.sin(c2.angle) * c2.distance;
                const str = 1 - nd / (Math.PI / 4);
                ctx.strokeStyle = `hsla(${(c1.hue + c2.hue) / 2}, 65%, 62%, ${(c1.alpha + c2.alpha) / 2 * str * 0.2})`;
                ctx.lineWidth = 1.5 + str * 2.5;
                ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
              }
            });
          });
        }
      }

      // ─── Circuits ───
      if (drawQualityRef.current > 0.4) {
        circumpuncts.forEach(e1 => {
          e1.neighbors.forEach(e2 => {
            let existing = circuits.find(c => (c.e1 === e1 && c.e2 === e2) || (c.e1 === e2 && c.e2 === e1));
            if (existing) {
              existing.update(time, true, fieldCoherence);
              if (existing.strength > 0.65 && time - existing.lastPulseTime > 25) {
                energyPulses.push(new EnergyPulse(existing, 1));
                energyPulses.push(new EnergyPulse(existing, -1));
                existing.lastPulseTime = time;
              }
            } else {
              circuits.push(new Circuit(e1, e2, time));
              e1.circuitPartners.add(e2.id);
              e2.circuitPartners.add(e1.id);
            }
          });
        });
      }

      circuits = circuits.filter(c => {
        const e1ok = circumpuncts.includes(c.e1);
        const e2ok = circumpuncts.includes(c.e2);
        c.update(time, e1ok && e2ok && c.e1.neighbors.includes(c.e2), fieldCoherence);
        if (!c.shouldRemove()) { c.draw(ctx, fieldCoherence, time); return true; }
        return false;
      });

      energyPulses = energyPulses.filter(p => {
        const alive = p.update(fieldCoherence);
        if (alive) p.draw(ctx, fieldCoherence);
        return alive;
      });

      // Cap entities
      if (circumpuncts.length > 55) circumpuncts = circumpuncts.slice(-55);

      ctx.restore();

      // ─── Draw center ⊙ symbol ───
      const centerAlpha = 0.15 + systemState.beta * 0.2 + collectiveBreath * 0.08;
      const centerSize = 12 + collectiveBreath * 4;
      ctx.strokeStyle = `rgba(200, 200, 255, ${centerAlpha})`;
      ctx.lineWidth = 1.2;
      ctx.beginPath(); ctx.arc(cx, cy, centerSize, 0, Math.PI * 2); ctx.stroke();
      ctx.fillStyle = `rgba(255, 255, 255, ${centerAlpha * 1.2})`;
      ctx.beginPath(); ctx.arc(cx, cy, 2, 0, Math.PI * 2); ctx.fill();

      // ─── Update metrics ───
      if (time % 20 === 0) {
        const beta = systemState.beta;
        let phaseCoherence = 0;
        if (circumpuncts.length > 1) {
          let pcSum = 0;
          circumpuncts.forEach(e => { pcSum += e.field.coherence; });
          phaseCoherence = pcSum / circumpuncts.length;
        }
        setMetrics({
          beta: beta,
          dAperture: 1 + beta,
          dField: 2 - beta,
          dBoundary: 3.0,
          rho: systemState.rho,
          fieldCoherence: fieldCoherence,
          phaseCoherence: phaseCoherence,
          patternCount: circumpuncts.length,
          convergenceNorm: systemState.convergenceNorm,
          emergenceNorm: systemState.emergenceNorm,
        });
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      canvas.removeEventListener('mousedown', handleMouseDown);
      canvas.removeEventListener('mousemove', handleMouseMove);
      canvas.removeEventListener('mouseup', handleMouseUp);
      canvas.removeEventListener('touchstart', handleTouchStart);
      canvas.removeEventListener('touchmove', handleTouchMove);
      canvas.removeEventListener('touchend', handleTouchEnd);
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, [playTone, playHarmonic, resetKey]);

  // ─── Handlers ───
  useEffect(() => { zoomRef.current = zoomLevel; }, [zoomLevel]);
  useEffect(() => { growthSpeedRef.current = growthSpeed; }, [growthSpeed]);

  const handleReset = () => {
    setZoomLevel(1); setGrowthSpeed(1.0); setDrawQuality(1.0); setFps(60);
    zoomRef.current = 1; growthSpeedRef.current = 1.0; drawQualityRef.current = 1.0;
    qualityCounter.current = 0; fpsHistory.current = []; lastFrameTime.current = Date.now();
    energyFlowsRef.current = []; touchesRef.current.clear();
    setResetKey(p => p + 1);
  };

  const toggleSound = () => {
    if (!soundEnabled) {
      const ctx = initAudio();
      if (ctx.state === 'suspended') ctx.resume();
    }
    setSoundEnabled(!soundEnabled);
  };

  const toggleMic = async () => {
    if (!micEnabled) {
      if (await initMicrophone()) setMicEnabled(true);
    } else {
      stopMicrophone(); setMicEnabled(false);
    }
  };

  const betaColor = metrics.beta > 0.55 ? 'text-blue-300' : metrics.beta < 0.45 ? 'text-red-300' : 'text-green-300';
  const rhoLabel = metrics.rho < 0.5 ? 'Overdamped' : metrics.rho > 2 ? 'Overdriven' : 'Critical';
  const rhoColor = metrics.rho < 0.5 ? 'text-blue-400' : metrics.rho > 2 ? 'text-red-400' : 'text-green-400';

  return (
    <div className="w-full h-screen bg-gray-950 overflow-hidden relative" style={{ fontFamily: "'JetBrains Mono', 'Fira Code', monospace" }}>
      <canvas ref={canvasRef} className="w-full h-full cursor-crosshair" />

      {showMetrics && (
        <div className="absolute top-6 left-6 bg-slate-950/92 backdrop-blur-md rounded-xl p-4 border border-indigo-500/40 text-white text-xs space-y-1.5" style={{ minWidth: '280px' }}>
          <div className="text-sm font-bold text-indigo-300 mb-2 pb-2 border-b border-indigo-500/30 flex items-center gap-2">
            <span style={{ fontSize: '1.1rem' }}>⊙</span> Circumpunct Framework v6.0
          </div>

          <div className="text-xs text-gray-500 mb-2">Conservation of Traversal: D• + DΦ = D○</div>

          <div className="space-y-1">
            <div className="flex justify-between">
              <span className="text-gray-400">β (opening):</span>
              <span className={betaColor}>{metrics.beta.toFixed(3)}</span>
            </div>
            <div className="w-full bg-gray-800 h-1.5 rounded overflow-hidden">
              <div className="h-full rounded transition-all" style={{
                width: `${metrics.beta * 100}%`,
                background: `linear-gradient(90deg, hsl(0,70%,55%), hsl(60,70%,55%) 50%, hsl(140,70%,55%))`
              }}></div>
            </div>

            <div className="grid grid-cols-3 gap-2 pt-1">
              <div className="text-center">
                <div className="text-gray-500 text-xs">D•</div>
                <div className="text-cyan-300 text-sm">{metrics.dAperture.toFixed(2)}</div>
              </div>
              <div className="text-center">
                <div className="text-gray-500 text-xs">DΦ</div>
                <div className="text-purple-300 text-sm">{metrics.dField.toFixed(2)}</div>
              </div>
              <div className="text-center">
                <div className="text-gray-500 text-xs">D○</div>
                <div className="text-amber-300 text-sm">{metrics.dBoundary.toFixed(1)}</div>
              </div>
            </div>

            <div className="flex justify-between pt-1">
              <span className="text-gray-400">ρ (ω/α):</span>
              <span className={rhoColor}>{metrics.rho.toFixed(2)} — {rhoLabel}</span>
            </div>

            <div className="flex justify-between">
              <span className="text-gray-400">⊛ convergence:</span>
              <span className="text-blue-400">{metrics.convergenceNorm.toFixed(3)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">☀️ emergence:</span>
              <span className="text-orange-400">{metrics.emergenceNorm.toFixed(3)}</span>
            </div>

            <div className="flex justify-between">
              <span className="text-gray-400">Φ coherence:</span>
              <span className="text-teal-400">{(metrics.fieldCoherence * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">T(Δφ) phase:</span>
              <span className="text-pink-400">{(metrics.phaseCoherence * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Entity count:</span>
              <span className="text-yellow-400">{metrics.patternCount}</span>
            </div>

            <div className="border-t border-gray-800 pt-1.5 mt-1.5">
              <div className="flex justify-between">
                <span className="text-gray-500">FPS:</span>
                <span className={fps >= 30 ? 'text-green-400' : fps >= 20 ? 'text-yellow-400' : 'text-red-400'}>{fps}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Quality:</span>
                <span className={drawQuality > 0.7 ? 'text-green-400' : 'text-yellow-400'}>{(drawQuality * 100).toFixed(0)}%</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="absolute top-6 right-6 bg-slate-950/92 backdrop-blur-md rounded-xl p-4 border border-indigo-500/40 text-white space-y-3" style={{ minWidth: '200px' }}>
        <div className="text-xs text-gray-400">
          <label className="block mb-1">Growth: {growthSpeed.toFixed(1)}×</label>
          <input type="range" min="0.1" max="3" step="0.1" value={growthSpeed}
            onChange={e => setGrowthSpeed(parseFloat(e.target.value))} className="w-full" />
        </div>
        <div className="flex gap-2 pt-2 border-t border-gray-800">
          <button onClick={toggleMic}
            className={`flex-1 py-2 rounded-lg text-lg transition ${micEnabled ? 'bg-red-600/70 hover:bg-red-500' : 'bg-gray-700/70 hover:bg-gray-600'}`}
            title={micEnabled ? 'Stop Listening' : 'Listen'}>
            {micEnabled ? '🎤' : '🎙️'}
          </button>
          <button onClick={toggleSound}
            className={`flex-1 py-2 rounded-lg text-lg transition ${soundEnabled ? 'bg-indigo-600/70 hover:bg-indigo-500' : 'bg-gray-700/70 hover:bg-gray-600'}`}
            title={soundEnabled ? 'Mute' : 'Sound'}>
            {soundEnabled ? '🔊' : '🔇'}
          </button>
        </div>
      </div>

      {/* Bottom Controls */}
      <div className="absolute bottom-6 left-6 flex gap-2 flex-wrap max-w-lg">
        {[
          ['Zoom +', () => setZoomLevel(z => Math.min(z * 1.4, 8))],
          ['Zoom −', () => setZoomLevel(z => Math.max(z / 1.4, 0.3))],
          ['Reset', handleReset],
          [showMetrics ? 'Hide ⊙' : 'Show ⊙', () => setShowMetrics(!showMetrics)],
        ].map(([label, fn]) => (
          <button key={label} onClick={fn}
            className="px-3.5 py-1.5 bg-indigo-700/70 hover:bg-indigo-500 text-white text-xs rounded-lg backdrop-blur-sm transition border border-indigo-500/30">
            {label}
          </button>
        ))}
      </div>

      <div className="absolute bottom-6 right-6 text-gray-500 text-xs bg-gray-900/50 px-3 py-1.5 rounded-lg backdrop-blur-sm border border-gray-700/30">
        Depth: {zoomLevel.toFixed(2)}× • {zoomLevel > 1.1 ? '← Past' : zoomLevel < 0.9 ? '→ Present' : '⊙ Now'}
      </div>
    </div>
  );
};

export default CircumpunctFractalSimulator;
