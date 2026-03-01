import React, { useEffect, useRef, useState, useCallback } from 'react';

// ═══════════════════════════════════════════════════════════════
//  CIRCUMPUNCT FRACTAL SIMULATOR v3.0
//  "The Tree That Dreams"
//
//       ☀ branches (emergence → outward → objective → real → finite)
//       │
//  ═════●═════  aperture: rotation through i
//       │
//       ⊛ roots (convergence → inward → subjective → imaginary → infinite)
//
//  ⊙ = Φ(•, ○)  —  Parts are fractals of their wholes
//  Conservation of Traversal: D_• + D_Φ = D_○ = 3
//  Six Coupled ODEs  |  Bidirectional trunk flow
//  Phase coherence T(Δφ) = cos²(Δφ/2)
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
    beta: 0.5, dAperture: 1.5, dField: 1.5, dBoundary: 3.0,
    rho: 1.0, fieldCoherence: 0, phaseCoherence: 0,
    patternCount: 0, convergenceNorm: 0, emergenceNorm: 0,
    rootCount: 0, rootDepth: 0, trunkFlow: 0, imaginationStrength: 0,
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
    } catch (e) { console.error('Mic denied:', e); return false; }
  }, [initAudio]);

  const stopMicrophone = useCallback(() => {
    if (micStreamRef.current) { micStreamRef.current.getTracks().forEach(t => t.stop()); micStreamRef.current = null; }
    micAnalyserRef.current = null; micDataRef.current = null;
  }, []);

  const playTone = useCallback((frequency, duration, volume = 0.08) => {
    if (!soundEnabled || !audioContextRef.current) return;
    const ctx = audioContextRef.current;
    const osc = ctx.createOscillator(); const gain = ctx.createGain();
    osc.type = 'sine'; osc.frequency.setValueAtTime(frequency, ctx.currentTime);
    gain.gain.setValueAtTime(volume, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
    osc.connect(gain); gain.connect(audioAnalyserRef.current || ctx.destination);
    osc.start(ctx.currentTime); osc.stop(ctx.currentTime + duration);
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
    //  SYSTEM STATE — The Six Coupled Variables
    // ════════════════════════════════════════════════════════
    let systemState = {
      beta: 0.5,
      convergenceNorm: 0,
      emergenceNorm: 0,
      rho: 1.0,
    };

    const params = {
      D: 0.1, gamma: 0.05, V: 0.8, alpha: 0.3,
      lambda: 0.1, kappa: 0.05, epsilon: 0.01
    };

    // ════════════════════════════════════════════════════════
    //  ENTITY ARRAYS — Outer (☀️) and Inner (⊛) worlds
    // ════════════════════════════════════════════════════════
    let branches = [];       // ☀️ Outer entities — emergence, objective, real
    let roots = [];          // ⊛ Inner entities — convergence, subjective, imaginary
    let circuits = [];
    let energyPulses = [];
    let brainClouds = [];    // Outer field structures
    let rootClouds = [];     // Inner field structures — the dreaming layer
    let expandingCells = [];
    let trunkFlows = [];     // Bidirectional energy along aperture axis
    let ghostBranches = [];  // Imagination — what roots dream before it emerges
    let brainFormed = false;
    let rootsFormed = false;
    let brainFormationProgress = 0;
    let rootFormationProgress = 0;
    let collectiveBreath = 0;
    let audioInfluence = 0;
    let dominantNote = null;
    let noteHistory = [];
    let memoryBraid = [];    // Accumulated history patterns

    // ═══════════════════════════════════════════════════════
    //  BRANCH ENTITY — ☀️ Emergence into the outer world
    //  Grows OUTWARD from center toward boundary
    // ═══════════════════════════════════════════════════════
    class BranchEntity {
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

        // Aperture (•)
        this.aperture = {
          beta: 0.3 + Math.random() * 0.4,
          psi: { re: Math.random() * 0.1, im: Math.random() * 0.1 },
          phase: Math.random() * Math.PI * 2,
          gateOpenness: 0.5,
        };
        // Field (Φ)
        this.field = {
          amplitude: 0.5 + Math.random() * 0.5,
          phase: Math.random() * Math.PI * 2,
          coherence: 0, flowRatio: 0.5,
          convergenceStrength: 0, emergenceStrength: 0,
        };
        // Boundary (○)
        this.boundary = {
          autonomy: 0.5, radius: 5 + Math.random() * 10,
          stability: 0, memoryTrace: [],
        };

        this.geometryType = Math.random() * 6;
        this.evolutionStage = Math.random() * 3;
        this.neighbors = [];
        this.circuitPartners = new Set();
        this.connectionWeights = new Map();
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
        this.musicalNote = null;
        this.baseFrequency = 0;
        this.maturity = 0; // When >=1, branch can become root
        this.rootSpawned = false;

        this.x = cx + Math.cos(angle) * this.baseLength * this.scale + this.randomOffsetX;
        this.y = cy + Math.sin(angle) * this.baseLength * this.scale + this.randomOffsetY;
      }

      updateCircumpunctDynamics(dt) {
        const a = this.aperture; const f = this.field; const b = this.boundary;

        // 1. Convergence: z = U*Φ (with √r kernel)
        let zRe = 0, zIm = 0;
        this.neighbors.forEach(n => {
          const dist = Math.sqrt((n.x - this.x) ** 2 + (n.y - this.y) ** 2);
          const kernel = Math.sqrt(Math.max(0.01, dist / 200));
          zRe += n.field.amplitude * Math.cos(n.field.phase) * kernel;
          zIm += n.field.amplitude * Math.sin(n.field.phase) * kernel;
        });
        zRe += f.amplitude * Math.cos(f.phase) * 0.3;
        zIm += f.amplitude * Math.sin(f.phase) * 0.3;
        const zNorm = Math.sqrt(zRe * zRe + zIm * zIm);

        // 2. Aperture rotation: z̃ = e^{iπβ} z
        const rotAngle = Math.PI * a.beta;
        const ztRe = zRe * Math.cos(rotAngle) - zIm * Math.sin(rotAngle);
        const ztIm = zRe * Math.sin(rotAngle) + zIm * Math.cos(rotAngle);

        // 3. ∂ψ/∂t = −αψ + tanh(z̃)
        const tanhMag = Math.tanh(Math.sqrt(ztRe * ztRe + ztIm * ztIm));
        const ztPhase = Math.atan2(ztIm, ztRe);
        a.psi.re += (-params.alpha * a.psi.re + tanhMag * Math.cos(ztPhase)) * dt;
        a.psi.im += (-params.alpha * a.psi.im + tanhMag * Math.sin(ztPhase)) * dt;

        // 4. ∂β/∂t = κ(|z|/(|z|+|ψ|+ε) − β)
        const psiNorm = Math.sqrt(a.psi.re ** 2 + a.psi.im ** 2);
        a.beta += params.kappa * (zNorm / (zNorm + psiNorm + params.epsilon) - a.beta) * dt;
        a.beta = Math.max(0.01, Math.min(0.99, a.beta));

        // 5. Field evolution: ∂Φ/∂t = D∇²Φ − γΦ + Vψ
        let lapRe = 0, lapIm = 0;
        if (this.neighbors.length > 0) {
          this.neighbors.forEach(n => {
            lapRe += n.field.amplitude * Math.cos(n.field.phase) - f.amplitude * Math.cos(f.phase);
            lapIm += n.field.amplitude * Math.sin(n.field.phase) - f.amplitude * Math.sin(f.phase);
          });
          lapRe /= this.neighbors.length; lapIm /= this.neighbors.length;
        }
        let phiRe = f.amplitude * Math.cos(f.phase);
        let phiIm = f.amplitude * Math.sin(f.phase);
        phiRe += (params.D * lapRe - params.gamma * phiRe + params.V * a.psi.re) * dt;
        phiIm += (params.D * lapIm - params.gamma * phiIm + params.V * a.psi.im) * dt;
        f.amplitude = Math.min(3, Math.sqrt(phiRe * phiRe + phiIm * phiIm));
        f.phase = Math.atan2(phiIm, phiRe);

        // 6. Boundary memory trace
        b.memoryTrace.push(a.beta);
        if (b.memoryTrace.length > 32) b.memoryTrace.shift();
        b.stability = 1 - Math.min(1, b.memoryTrace.reduce((s, v) => s + Math.abs(v - 0.5), 0) / b.memoryTrace.length * 2);

        f.convergenceStrength = zNorm;
        f.emergenceStrength = f.amplitude;
        f.flowRatio = f.convergenceStrength / (f.convergenceStrength + f.emergenceStrength + params.epsilon);

        if (this.neighbors.length > 0) {
          let cs = 0;
          this.neighbors.forEach(n => { cs += Math.cos(f.phase - n.field.phase); });
          f.coherence = Math.max(0, cs / this.neighbors.length);
        }
      }

      update(t, allBranches) {
        this.age = t - this.birthTime;
        const dt = 0.1 * growthSpeedRef.current;

        if (this.userSpawned && this.spawnEnergy > 0) {
          this.spawnEnergy *= 0.98;
          this.scale = Math.min(1.5, this.scale + this.spawnEnergy * 0.03);
        }

        this.neighbors = allBranches.filter(e => {
          if (e === this || !e.x) return false;
          const d = Math.sqrt((this.x - e.x) ** 2 + (this.y - e.y) ** 2);
          return d < 160 && d > 5;
        });

        this.updateCircumpunctDynamics(dt);

        // Hebbian learning with T(Δφ) = cos²(Δφ/2)
        this.neighbors.forEach(n => {
          const w = this.connectionWeights.get(n.id) || 0;
          const d = Math.sqrt((this.x - n.x) ** 2 + (this.y - n.y) ** 2);
          const T = Math.cos((this.field.phase - n.field.phase) / 2) ** 2;
          this.connectionWeights.set(n.id, Math.min(1, w + 0.01 * (1 - d / 160) * T * Math.max(0.1, this.harmonicStrength)));
        });
        for (let [id, w] of this.connectionWeights.entries()) {
          if (w < 0.08) this.connectionWeights.delete(id);
          else this.connectionWeights.set(id, w * 0.995);
        }
        this.gravitationalMass = Array.from(this.connectionWeights.values()).reduce((s, w) => s + w, 0) / 8;

        // Maturity — branches ripen toward becoming roots
        this.maturity = Math.min(1, this.maturity + 0.0003 * growthSpeedRef.current * (1 + this.boundary.stability));

        const betaShift = (this.aperture.beta - 0.5) * 60;
        this.hue = (this.baseHue + betaShift + t * 0.05 + audioInfluence * 40) % 360;
        this.evolutionStage += (0.002 + this.field.amplitude * 0.001) * growthSpeedRef.current;
        this.geometryType += Math.sin(this.evolutionStage) * 0.015;

        const length = this.baseLength * this.scale;
        const wobble = Math.sin(t * 0.02 + this.phaseOffset) * (5 + this.aperture.beta * 10);
        this.x = cx + Math.cos(this.angle) * length + this.randomOffsetX + wobble;
        this.y = cy + Math.sin(this.angle) * length + this.randomOffsetY + wobble * 0.7;
      }

      draw(ctx, t) {
        const q = drawQualityRef.current;

        // Probability cloud
        if (q > 0.7) {
          this.probabilityCloud.forEach(p => {
            const a = this.angle + p.angle + Math.sin(t * 0.01 + p.phase) * 0.4;
            const d = p.dist * (1 + Math.sin(t * 0.015 + p.phase) * 0.3) * this.field.amplitude;
            ctx.fillStyle = `hsla(${this.hue}, 65%, 60%, ${0.08 * this.field.coherence})`;
            ctx.beginPath(); ctx.arc(this.x + Math.cos(a) * d, this.y + Math.sin(a) * d, 2.5, 0, Math.PI * 2); ctx.fill();
          });
        }

        // Connections
        if (q > 0.5) {
          this.neighbors.forEach(n => {
            const w = this.connectionWeights.get(n.id);
            if (w && w > 0.2) {
              const T = Math.cos((this.field.phase - n.field.phase) / 2) ** 2;
              ctx.strokeStyle = `hsla(${(this.hue + n.hue) / 2}, 70%, 60%, ${w * T * 0.35})`;
              ctx.lineWidth = 0.8 + w * 2.5;
              ctx.beginPath(); ctx.moveTo(this.x, this.y); ctx.lineTo(n.x, n.y); ctx.stroke();
            }
          });
        }

        if (q < 0.5) {
          const alpha = 0.4 + this.scale * 0.4;
          ctx.strokeStyle = `hsla(${this.hue}, 70%, 55%, ${alpha})`;
          ctx.lineWidth = 1.5;
          ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(this.x, this.y); ctx.stroke();
          ctx.fillStyle = `hsla(${this.hue}, 75%, 60%, ${alpha})`;
          ctx.beginPath(); ctx.arc(this.x, this.y, 4 * this.scale, 0, Math.PI * 2); ctx.fill();
        } else {
          const length = this.baseLength * this.scale;
          const dFC = Math.sqrt((this.x - cx) ** 2 + (this.y - cy) ** 2);
          const val = Math.max(0.2, 1 - dFC / 400);
          const alpha = Math.min(0.85, (0.3 + this.scale * 0.55) * val * (1 + this.fieldEnergyBoost) * (1 + Math.min(this.gravitationalMass, 1.2)));

          if (this.gravitationalMass > 0.4) {
            ctx.shadowBlur = 6 * this.gravitationalMass * q;
            ctx.shadowColor = `hsla(${this.hue}, 80%, 65%, ${this.gravitationalMass * 0.12})`;
          }
          this.drawBranch(ctx, cx, cy, length, this.angle, Math.ceil(5 * q), this.hue, alpha, t, 0, val);
          ctx.shadowBlur = 0;
          this.fieldEnergyBoost = 0;
        }

        // Maturity glow — approaching transformation to root
        if (this.maturity > 0.6) {
          const pulse = Math.sin(t * 0.03 + this.phaseOffset) * 0.5 + 0.5;
          const mAlpha = (this.maturity - 0.6) * 2.5 * pulse * 0.15;
          ctx.fillStyle = `hsla(250, 60%, 70%, ${mAlpha})`;
          ctx.beginPath(); ctx.arc(this.x, this.y, 8 + pulse * 4, 0, Math.PI * 2); ctx.fill();
        }
      }

      drawBranch(ctx, x, y, length, angle, depth, hue, baseAlpha, t, gen, validation) {
        if (depth === 0 || length < 1.5) { this.drawBody(ctx, x, y, hue, Math.max(baseAlpha, 0.25), t); return; }
        const endX = x + length * Math.cos(angle);
        const endY = y + length * Math.sin(angle);
        const dFC = Math.sqrt((endX - cx) ** 2 + (endY - cy) ** 2);
        const bVal = Math.max(0.2, 1 - dFC / 400);
        const alpha = baseAlpha * (depth / 5.5) * bVal;
        const lHue = (hue + gen * 7 + t * 0.04) % 360;

        ctx.strokeStyle = `hsla(${lHue}, 72%, 55%, ${alpha})`;
        ctx.lineWidth = Math.max(0.5, depth * 0.9 * this.scale);
        ctx.lineCap = 'round';
        ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(endX, endY); ctx.stroke();

        if (depth > 2 && depth < 6) this.drawBody(ctx, endX, endY, lHue, Math.max(alpha, 0.2), t);

        const betaAngle = Math.PI / (5 + this.aperture.beta * 2);
        const variation = Math.sin(gen * 0.5 + this.phaseOffset) * 0.25;
        const ba = betaAngle + variation;
        const lm = 0.65 + Math.sin(t * 0.008 + gen) * 0.04;
        this.drawBranch(ctx, endX, endY, length * lm, angle - ba, depth - 1, lHue, baseAlpha, t, gen + 1, bVal);
        this.drawBranch(ctx, endX, endY, length * lm, angle + ba, depth - 1, lHue, baseAlpha, t, gen + 1, bVal);
        if (depth > 4 && Math.sin(t * 0.012 + gen + this.phaseOffset) > 0.6)
          this.drawBranch(ctx, endX, endY, length * lm * 0.7, angle, depth - 1, lHue, baseAlpha, t, gen + 1, bVal);
      }

      drawBody(ctx, x, y, hue, alpha, t) {
        const size = Math.max(2.5, 4.5 * this.scale);
        const rot = t * 0.008 * this.evolutionStage + this.phaseOffset;
        const stage = Math.floor(this.geometryType) % 6;
        ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
        ctx.fillStyle = `hsla(${hue}, 78%, 60%, ${alpha})`;
        ctx.strokeStyle = `hsla(${hue}, 88%, 70%, ${alpha * 0.8})`;
        ctx.lineWidth = 0.8; ctx.beginPath();
        if (stage === 5) ctx.arc(0, 0, size, 0, Math.PI * 2);
        else if (stage === 4) {
          for (let i = 0; i <= 10; i++) { const a = (i / 10) * Math.PI * 2 - Math.PI / 2; const r = i % 2 === 0 ? size : size * 0.45; i === 0 ? ctx.moveTo(Math.cos(a) * r, Math.sin(a) * r) : ctx.lineTo(Math.cos(a) * r, Math.sin(a) * r); }
        } else {
          const sides = stage + 3;
          for (let i = 0; i <= sides; i++) { const a = (i / sides) * Math.PI * 2 - Math.PI / 2; i === 0 ? ctx.moveTo(Math.cos(a) * size, Math.sin(a) * size) : ctx.lineTo(Math.cos(a) * size, Math.sin(a) * size); }
        }
        ctx.closePath(); ctx.fill(); ctx.stroke(); ctx.restore();
      }
    }

    // ═══════════════════════════════════════════════════════
    //  ROOT ENTITY — ⊛ Convergence into the inner world
    //  Grows INWARD — memory of what once emerged
    //  Phase rotated π/2 (through i) from parent branch
    //  "The past isn't gone — it's below. Still connected."
    // ═══════════════════════════════════════════════════════
    class RootEntity {
      constructor(parentBranch, birthTime) {
        this.id = Math.random();
        this.parentAngle = parentBranch.angle;
        this.baseHue = (parentBranch.baseHue + 180) % 360; // Complement
        this.hue = this.baseHue;
        this.birthTime = birthTime;
        this.age = 0;

        // Root depth — how far inward
        this.depth = 30 + Math.random() * 40;
        this.maxDepth = 80 + parentBranch.gravitationalMass * 40;
        this.growthRate = 0.1 + Math.random() * 0.15;

        // Inherited field — the memory of what this branch was
        // Phase rotated by π/2 — the i rotation from real to imaginary
        this.field = {
          amplitude: parentBranch.field.amplitude * 0.7,
          phase: parentBranch.field.phase + Math.PI / 2,
          coherence: parentBranch.field.coherence,
        };

        // Memory content
        this.memory = {
          originalHue: parentBranch.baseHue,
          originalBeta: parentBranch.aperture.beta,
          connectionStrength: parentBranch.gravitationalMass,
          musicalNote: parentBranch.musicalNote,
          braidPattern: [...parentBranch.boundary.memoryTrace],
        };

        this.alpha = 0;
        this.phaseOffset = parentBranch.phaseOffset;
        this.wobblePhase = Math.random() * Math.PI * 2;
        this.neighbors = [];
        this.imaginationStrength = 0;
        this.resonanceWithPresent = 0;

        this.x = cx; this.y = cy;
      }

      update(t, allRoots, allBranches, fieldCoherence) {
        this.age = t - this.birthTime;
        this.alpha = Math.min(0.55, this.age / 80);

        // Grow inward
        if (this.depth < this.maxDepth) this.depth += this.growthRate * growthSpeedRef.current * 0.3;

        // Organic wobble — roots flow more than branches
        const wobble = Math.sin(t * 0.008 + this.wobblePhase) * 8 * (1 + fieldCoherence * 0.5);
        const breathPull = Math.sin(t * 0.004) * 5;

        // Position: opposite side of center from parent branch
        this.x = cx - Math.cos(this.parentAngle) * this.depth + Math.sin(t * 0.006 + this.wobblePhase) * wobble * 0.5;
        this.y = cy - Math.sin(this.parentAngle) * this.depth + Math.cos(t * 0.006 + this.wobblePhase) * wobble * 0.5 + breathPull;

        // Find root neighbors
        this.neighbors = allRoots.filter(r => {
          if (r === this) return false;
          const d = Math.sqrt((r.x - this.x) ** 2 + (r.y - this.y) ** 2);
          return d < 120 && d > 3;
        });

        // Imagination: roots dream when present input resonates with memory
        this.resonanceWithPresent = 0;
        if (allBranches.length > 0) {
          allBranches.forEach(b => {
            const hueDiff = Math.abs(this.memory.originalHue - b.baseHue);
            const hueRes = 1 - Math.min(hueDiff, 360 - hueDiff) / 180;
            const betaRes = 1 - Math.abs(this.memory.originalBeta - b.aperture.beta);
            const phaseRes = Math.cos((this.field.phase - b.field.phase) / 2) ** 2;
            const total = hueRes * 0.4 + betaRes * 0.3 + phaseRes * 0.3;
            if (total > this.resonanceWithPresent) this.resonanceWithPresent = total;
          });
        }
        this.imaginationStrength = this.resonanceWithPresent * this.field.amplitude * this.alpha;

        // Shift toward imaginary spectrum — blues, violets, cyans
        this.hue = (this.baseHue + Math.sin(t * 0.003 + this.phaseOffset) * 20 + 200) % 360;
      }

      draw(ctx, t, fieldCoherence) {
        if (this.alpha < 0.02) return;
        const q = drawQualityRef.current;

        // Root tendrils — organic flowing lines from center outward (into the depths)
        if (q > 0.4) {
          const numTendrils = q > 0.6 ? 3 : 1;
          for (let i = 0; i < numTendrils; i++) this.drawTendril(ctx, t, i, numTendrils);
        }

        // Imagination glow — root dreaming
        const pulse = Math.sin(t * 0.015 + this.phaseOffset) * 0.3 + 0.7;
        const size = 3 + this.field.amplitude * 2 + this.imaginationStrength * 3;

        if (this.imaginationStrength > 0.2 && q > 0.5) {
          const igAlpha = this.imaginationStrength * this.alpha * 0.4 * pulse;
          const igR = size * 3 + this.imaginationStrength * 8;
          const grad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, igR);
          grad.addColorStop(0, `hsla(${(this.hue + 60) % 360}, 70%, 70%, ${igAlpha})`);
          grad.addColorStop(1, `hsla(${this.hue}, 70%, 70%, 0)`);
          ctx.fillStyle = grad;
          ctx.beginPath(); ctx.arc(this.x, this.y, igR, 0, Math.PI * 2); ctx.fill();
        }

        // Root node
        ctx.shadowBlur = (4 + this.imaginationStrength * 8) * q;
        ctx.shadowColor = `hsla(${this.hue}, 65%, 55%, ${this.alpha * 0.4})`;
        ctx.fillStyle = `hsla(${this.hue}, 55%, 50%, ${this.alpha * pulse * 0.7})`;
        ctx.beginPath(); ctx.arc(this.x, this.y, size * pulse, 0, Math.PI * 2); ctx.fill();
        ctx.shadowBlur = 0;

        // Root web — curved organic connections
        if (q > 0.5) {
          this.neighbors.forEach(n => {
            const d = Math.sqrt((n.x - this.x) ** 2 + (n.y - this.y) ** 2);
            const str = (1 - d / 120) * 0.2;
            if (str > 0.03) {
              ctx.strokeStyle = `hsla(${(this.hue + n.hue) / 2}, 50%, 50%, ${str * this.alpha})`;
              ctx.lineWidth = 0.5 + str * 2;
              const midX = (this.x + n.x) / 2 + Math.sin(t * 0.01 + this.phaseOffset) * 8;
              const midY = (this.y + n.y) / 2 + Math.cos(t * 0.01 + n.phaseOffset) * 8;
              ctx.beginPath(); ctx.moveTo(this.x, this.y);
              ctx.quadraticCurveTo(midX, midY, n.x, n.y); ctx.stroke();
            }
          });
        }
      }

      drawTendril(ctx, t, index, total) {
        const spreadAngle = (index - (total - 1) / 2) * 0.15;
        const angle = this.parentAngle + Math.PI + spreadAngle;
        const segments = Math.ceil(6 * drawQualityRef.current);
        const segLen = this.depth * 0.6 / segments;
        let x = cx; let y = cy;

        ctx.beginPath(); ctx.moveTo(x, y);
        for (let i = 0; i < segments; i++) {
          const progress = i / segments;
          const wobble = Math.sin(t * 0.01 + this.phaseOffset + i * 0.5 + index) * (5 + progress * 10);
          const perpAngle = angle + Math.PI / 2;
          x += Math.cos(angle) * segLen + Math.cos(perpAngle) * wobble * 0.3;
          y += Math.sin(angle) * segLen + Math.sin(perpAngle) * wobble * 0.3;
          ctx.lineTo(x, y);
        }

        const alpha = this.alpha * 0.3 * (1 - this.depth / this.maxDepth * 0.3);
        ctx.strokeStyle = `hsla(${this.hue}, 45%, 45%, ${alpha})`;
        ctx.lineWidth = 1.5 - index * 0.3;
        ctx.stroke();
      }
    }

    // ═══════════════════════════════════════════════════════
    //  GHOST BRANCH — Imagination made visible
    //  When roots dream strongly, translucent previews
    //  appear in the outer world — what might emerge
    // ═══════════════════════════════════════════════════════
    class GhostBranch {
      constructor(root, t) {
        this.root = root;
        this.birthTime = t;
        this.life = 1.0;
        this.angle = root.parentAngle; // Points outward — the dream of emergence
        this.hue = root.memory.originalHue;
        this.length = 40 + root.memory.connectionStrength * 60;
        this.phaseOffset = root.phaseOffset;
      }
      update() { this.life -= 0.006 * growthSpeedRef.current; return this.life > 0; }
      draw(ctx, t) {
        if (this.life < 0.05 || drawQualityRef.current < 0.5) return;
        const alpha = this.life * this.root.imaginationStrength * 0.2;
        const length = this.length * this.life;
        const endX = cx + Math.cos(this.angle) * length;
        const endY = cy + Math.sin(this.angle) * length;

        ctx.setLineDash([3, 6]);
        ctx.strokeStyle = `hsla(${this.hue}, 50%, 65%, ${alpha})`;
        ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(endX, endY); ctx.stroke();
        ctx.setLineDash([]);

        // Ghost node
        ctx.fillStyle = `hsla(${this.hue}, 50%, 65%, ${alpha * 0.7})`;
        ctx.beginPath(); ctx.arc(endX, endY, 3 * this.life, 0, Math.PI * 2); ctx.fill();
      }
    }

    // ═══════════════════════════════════════════════════════
    //  TRUNK FLOW — Bidirectional energy along aperture
    //  "The power line runs both ways."
    //  Up: imagination → reality  |  Down: experience → memory
    // ═══════════════════════════════════════════════════════
    class TrunkFlow {
      constructor(angle, t, direction, hue) {
        this.birthTime = t;
        this.direction = direction; // 1=upward (root→branch), -1=downward (branch→root)
        this.angle = angle;
        this.progress = direction > 0 ? -0.1 : 1.1;
        this.life = 1;
        this.hue = hue;
        this.speed = 0.02 + Math.random() * 0.01;
      }
      update() {
        this.progress += this.speed * this.direction * growthSpeedRef.current;
        this.life -= 0.008;
        return this.life > 0 && this.progress > -0.5 && this.progress < 1.5;
      }
      draw(ctx, t) {
        if (drawQualityRef.current < 0.4 || this.life < 0.05) return;
        const alpha = this.life * 0.35;
        // Map progress 0→1 from root-depth to branch-length through center
        const maxDist = 120;
        const dist = (this.progress - 0.5) * maxDist * 2;
        const x = cx + Math.cos(this.angle) * dist;
        const y = cy + Math.sin(this.angle) * dist;
        const size = 2 + this.life * 2;

        // Trail
        const trailLen = 3;
        for (let i = 0; i < trailLen; i++) {
          const tDist = dist - this.direction * i * 6;
          const tx = cx + Math.cos(this.angle) * tDist;
          const ty = cy + Math.sin(this.angle) * tDist;
          const ta = alpha * (1 - i / trailLen) * 0.5;
          ctx.fillStyle = `hsla(${this.hue}, 70%, 65%, ${ta})`;
          ctx.beginPath(); ctx.arc(tx, ty, size * (1 - i * 0.2), 0, Math.PI * 2); ctx.fill();
        }

        ctx.shadowBlur = 6 * drawQualityRef.current;
        ctx.shadowColor = `hsla(${this.hue}, 70%, 65%, ${alpha * 0.5})`;
        ctx.fillStyle = `hsla(${this.hue}, 75%, 70%, ${alpha})`;
        ctx.beginPath(); ctx.arc(x, y, size, 0, Math.PI * 2); ctx.fill();
        ctx.shadowBlur = 0;
      }
    }

    // ═══ BRAIN CLOUD — Outer field structures ═══
    class BrainCloud {
      constructor(angle, distance, birthTime) {
        this.angle = angle + (Math.random() - 0.5) * 0.2;
        this.baseDistance = distance + (Math.random() - 0.5) * 50;
        this.distance = this.baseDistance;
        this.birthTime = birthTime;
        this.phaseOffset = Math.random() * Math.PI * 2;
        this.hue = 200 + Math.random() * 60; this.alpha = 0;
        this.particles = []; this.connectedEntities = [];
        this.energyLevel = 0;
        this.learningRate = 0.05; this.entityAffinities = new Map();
        const count = 16 + Math.floor(Math.random() * 14);
        for (let i = 0; i < count; i++) {
          this.particles.push({
            angle: angle + (Math.random() - 0.5) * 0.7,
            distOffset: (Math.random() - 0.5) * 40,
            size: 2 + Math.random() * 3, phaseOffset: Math.random() * Math.PI * 2,
            speed: 0.002 + Math.random() * 0.003, energy: Math.random(),
            excitement: 0, targetEntity: null,
            rotation: Math.random() * Math.PI * 2,
            rotationSpeed: (Math.random() - 0.5) * 0.015,
          });
        }
      }
      update(t, allBranches, globalBreath) {
        const age = t - this.birthTime;
        this.alpha = age < 60 ? age / 60 : Math.min(0.6, this.alpha);
        this.distance = this.baseDistance + Math.sin(t * 0.01 + this.phaseOffset) * 10 + globalBreath * 18 + audioInfluence * 22;
        this.connectedEntities = allBranches.filter(e => {
          if (!e || e.x === undefined) return false;
          const diff = Math.abs(this.angle - e.angle);
          return Math.min(diff, Math.PI * 2 - diff) < 0.85;
        });
        this.connectedEntities.forEach(entity => {
          const curr = this.entityAffinities.get(entity.id) || 0;
          const pc = Math.cos((entity.field.phase - this.phaseOffset) / 2) ** 2;
          const na = curr + this.learningRate * pc * entity.field.amplitude;
          this.entityAffinities.set(entity.id, Math.min(1, na));
          entity.connectedToCloud = true; entity.cloudInfluence = this.hue;
          entity.fieldEnergyBoost = this.energyLevel * (1 + na * 0.5);
          entity.harmonicStrength = Math.min(1, entity.harmonicStrength + pc * 0.08);
        });
        this.energyLevel = this.connectedEntities.length * 0.1;
      }
      spawnCell(t, cells) { if (this.alpha > 0.4 && drawQualityRef.current > 0.4) cells.push(new ExpandingCell(this, t)); }
      draw(ctx, t, fieldCoherence) {
        const q = drawQualityRef.current;
        const positions = [];
        const count = Math.ceil(this.particles.length * q);
        for (let i = 0; i < count; i++) {
          const p = this.particles[i];
          const ba = p.angle + Math.sin(t * p.speed + p.phaseOffset) * 0.12;
          const bd = this.distance + p.distOffset + Math.cos(t * p.speed * 0.7) * 8;
          let px = cx + Math.cos(ba) * bd; let py = cy + Math.sin(ba) * bd;
          if (p.targetEntity && p.excitement > 0.1) {
            px += (p.targetEntity.x - px) * p.excitement * 0.15;
            py += (p.targetEntity.y - py) * p.excitement * 0.15;
          }
          p.energy = (0.3 + Math.sin(t * p.speed * 2 + p.phaseOffset) * 0.15) * (1 + fieldCoherence * 0.4) + p.excitement * 0.25;
          p.excitement = Math.max(0, p.excitement * 0.95);
          p.rotation += p.rotationSpeed;
          const h = (this.hue + p.energy * 30 + fieldCoherence * 20) % 360;
          const a = this.alpha * (0.4 + p.energy * 0.5) * q;
          const s = p.size * (1 + p.excitement * 0.3) * (0.7 + fieldCoherence * 0.3);
          positions.push({ x: px, y: py, size: s, hue: h, alpha: a });
        }
        if (q > 0.6) {
          positions.forEach((p1, i) => {
            positions.slice(i + 1).forEach(p2 => {
              const d = Math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2);
              if (d < 65) {
                const str = 1 - d / 65;
                ctx.strokeStyle = `hsla(${(p1.hue + p2.hue) / 2}, 70%, 65%, ${(p1.alpha + p2.alpha) / 2 * str * 0.35})`;
                ctx.lineWidth = 0.7 + str * 1.5;
                ctx.beginPath(); ctx.moveTo(p1.x, p1.y); ctx.lineTo(p2.x, p2.y); ctx.stroke();
              }
            });
          });
        }
        positions.forEach(pos => {
          ctx.shadowBlur = (4 + fieldCoherence * 5) * q;
          ctx.shadowColor = `hsla(${pos.hue}, 80%, 65%, ${pos.alpha * 0.5})`;
          ctx.fillStyle = `hsla(${pos.hue}, 82%, 70%, ${pos.alpha})`;
          ctx.beginPath(); ctx.arc(pos.x, pos.y, pos.size, 0, Math.PI * 2); ctx.fill();
          ctx.shadowBlur = 0;
        });
      }
    }

    // ═══ ROOT CLOUD — Inner dreaming layer ═══
    class RootCloud {
      constructor(angle, distance, birthTime) {
        this.angle = angle + Math.PI;
        this.baseDistance = distance * 0.5;
        this.distance = this.baseDistance;
        this.birthTime = birthTime;
        this.phaseOffset = Math.random() * Math.PI * 2;
        this.hue = 240 + Math.random() * 40;
        this.alpha = 0;
        this.particles = Array.from({ length: 10 + Math.floor(Math.random() * 8) }, () => ({
          angle: this.angle + (Math.random() - 0.5) * 0.8,
          distOffset: (Math.random() - 0.5) * 30,
          size: 1.5 + Math.random() * 2.5,
          phaseOffset: Math.random() * Math.PI * 2,
          speed: 0.001 + Math.random() * 0.002,
        }));
        this.dreamIntensity = 0;
      }
      update(t, allRoots, breath) {
        const age = t - this.birthTime;
        this.alpha = Math.min(0.35, age / 120);
        this.distance = this.baseDistance + Math.sin(t * 0.007 + this.phaseOffset) * 8 + breath * 12;
        this.dreamIntensity = allRoots.length > 0 ? allRoots.reduce((max, r) => Math.max(max, r.imaginationStrength), 0) : 0;
      }
      draw(ctx, t) {
        if (this.alpha < 0.02 || drawQualityRef.current < 0.5) return;
        this.particles.forEach(p => {
          const a = p.angle + Math.sin(t * p.speed + p.phaseOffset) * 0.2;
          const d = this.distance + p.distOffset + Math.cos(t * p.speed * 0.5) * 6;
          const px = cx + Math.cos(a) * d;
          const py = cy + Math.sin(a) * d;
          const pulse = Math.sin(t * 0.012 + p.phaseOffset) * 0.3 + 0.7;
          const dreamGlow = this.dreamIntensity * 0.5;
          ctx.fillStyle = `hsla(${this.hue}, 45%, 50%, ${this.alpha * pulse * (0.5 + dreamGlow)})`;
          ctx.beginPath(); ctx.arc(px, py, p.size * pulse, 0, Math.PI * 2); ctx.fill();
        });
      }
    }

    // ═══ UTILITY CLASSES ═══
    class Circuit {
      constructor(e1, e2, t) { this.e1 = e1; this.e2 = e2; this.birthTime = t; this.strength = 0; this.age = 0; this.lastPulseTime = t; }
      update(t, conn, coh) { this.age = t - this.birthTime; this.strength = conn ? Math.min(1, this.strength + 0.015 * (1 + coh * 0.4)) : Math.max(0, this.strength - 0.008); }
      shouldRemove() { return this.strength <= 0; }
      draw(ctx, coh, t) { if (this.strength < 0.08 || drawQualityRef.current < 0.3) return; ctx.strokeStyle = `hsla(${(this.e1.hue + this.e2.hue) / 2}, 75%, 58%, ${this.strength * 0.4 * (1 + coh * 0.25)})`; ctx.lineWidth = 0.8 + this.strength + coh * 0.8; ctx.beginPath(); ctx.moveTo(this.e1.x, this.e1.y); ctx.lineTo(this.e2.x, this.e2.y); ctx.stroke(); }
    }
    class EnergyPulse {
      constructor(circuit, dir) { this.circuit = circuit; this.dir = dir; this.progress = dir > 0 ? 0 : 1; this.speed = 0.025; this.life = 1; this.hue = (circuit.e1.hue + circuit.e2.hue) / 2; }
      update(coh) { this.progress += this.speed * this.dir * (1 + coh * 0.4) * growthSpeedRef.current; this.life -= 0.008; return this.life > 0 && this.progress >= 0 && this.progress <= 1; }
      draw(ctx, coh) { if (drawQualityRef.current < 0.4) return; const x = this.circuit.e1.x + (this.circuit.e2.x - this.circuit.e1.x) * this.progress; const y = this.circuit.e1.y + (this.circuit.e2.y - this.circuit.e1.y) * this.progress; ctx.shadowBlur = 5 * drawQualityRef.current; ctx.shadowColor = `hsla(${this.hue}, 75%, 63%, ${this.life * 0.2})`; ctx.fillStyle = `hsla(${this.hue}, 75%, 68%, ${this.life * 0.2})`; ctx.beginPath(); ctx.arc(x, y, 2, 0, Math.PI * 2); ctx.fill(); ctx.shadowBlur = 0; }
    }
    class ExpandingCell {
      constructor(cloud, t) { this.angle = cloud.angle + (Math.random() - 0.5) * 0.25; this.distance = cloud.distance; this.hue = cloud.hue + (Math.random() - 0.5) * 18; this.speed = (0.5 + Math.random() * 0.4) * growthSpeedRef.current; this.maxR = 10 + Math.random() * 12; this.r = 0; this.lc = 0; this.lcSpeed = (0.005 + Math.random() * 0.003) * growthSpeedRef.current; this.rot = 0; this.rotSpeed = (Math.random() - 0.5) * 0.01; this.x = 0; this.y = 0; }
      update() { this.lc += this.lcSpeed; this.distance += this.speed; this.r = this.lc < 1 ? this.maxR * this.lc : this.lc < 3 ? this.maxR : this.maxR * (1 - (this.lc - 3)); this.rot += this.rotSpeed; this.x = cx + Math.cos(this.angle) * this.distance; this.y = cy + Math.sin(this.angle) * this.distance; return this.lc < 4 && this.distance < Math.max(W, H); }
      draw(ctx) { if (this.r < 0.5 || drawQualityRef.current < 0.5) return; const a = this.lc < 1 ? this.lc * 0.3 : this.lc < 3 ? 0.3 : 0.3 * (1 - (this.lc - 3)); ctx.save(); ctx.translate(this.x, this.y); ctx.rotate(this.rot); ctx.fillStyle = `hsla(${this.hue}, 80%, 70%, ${a * 0.5})`; ctx.beginPath(); ctx.arc(0, 0, this.r * 0.15, 0, Math.PI * 2); ctx.fill(); ctx.restore(); }
    }

    // ═══ AUDIO ═══
    const frequencyToNote = (freq) => {
      const names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
      const idx = Math.round(12 * Math.log2(freq / 440)) + 9;
      return `${names[((idx % 12) + 12) % 12]}${Math.floor(idx / 12) + 4}`;
    };
    const analyzeAudio = () => {
      if (micAnalyserRef.current && micDataRef.current) {
        micAnalyserRef.current.getByteFrequencyData(micDataRef.current);
        let maxAmp = 0, domFreq = 0;
        const sr = audioContextRef.current?.sampleRate || 44100;
        for (let i = 0; i < micDataRef.current.length; i++) {
          const amp = micDataRef.current[i]; const freq = (i * sr) / micAnalyserRef.current.fftSize;
          if (amp > 45 && freq > 80 && freq < 2000 && amp > maxAmp) { maxAmp = amp; domFreq = freq; }
        }
        if (domFreq > 0 && maxAmp > 50) {
          dominantNote = { frequency: domFreq, note: frequencyToNote(domFreq), amplitude: maxAmp / 255 };
          noteHistory.push({ ...dominantNote, time }); if (noteHistory.length > 32) noteHistory.shift();
          if (noteHistory.length >= 4) { const pat = noteHistory.slice(-4).map(n => n.note).join('-'); const m = melodicMemory.current.get(pat) || { count: 0 }; m.count++; melodicMemory.current.set(pat, m); }
          learnedMelody.current.push(dominantNote); if (learnedMelody.current.length > 64) learnedMelody.current.shift();
        }
        audioInfluence = micDataRef.current.reduce((a, b) => a + b, 0) / micDataRef.current.length / 255;
      } else if (audioAnalyserRef.current && audioDataRef.current) {
        audioAnalyserRef.current.getByteFrequencyData(audioDataRef.current);
        audioInfluence = audioDataRef.current.reduce((a, b) => a + b, 0) / audioDataRef.current.length / 255;
      }
    };

    // ═══ DRAWING HELPERS ═══
    const drawInnerGlow = () => {
      if (roots.length < 1 || drawQualityRef.current < 0.5) return;
      const avgIm = roots.reduce((s, r) => s + r.imaginationStrength, 0) / Math.max(1, roots.length);
      const radius = 70 + collectiveBreath * 25 + avgIm * 30;
      const intensity = 0.03 + avgIm * 0.1 + roots.length * 0.003;
      const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius);
      grad.addColorStop(0, `hsla(250, 50%, 60%, ${intensity})`);
      grad.addColorStop(0.4, `hsla(270, 40%, 50%, ${intensity * 0.4})`);
      grad.addColorStop(1, `hsla(270, 40%, 50%, 0)`);
      ctx.fillStyle = grad; ctx.beginPath(); ctx.arc(cx, cy, radius, 0, Math.PI * 2); ctx.fill();
    };
    const drawOuterGlow = () => {
      if (!brainFormed || drawQualityRef.current < 0.6) return;
      const radius = 100 + collectiveBreath * 35;
      const intensity = Math.abs(systemState.beta - 0.5) < 0.2 ? 0.12 : 0.05;
      const gH = systemState.beta > 0.5 ? 180 : 30;
      const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius);
      grad.addColorStop(0, `hsla(${gH}, 50%, 80%, ${intensity})`);
      grad.addColorStop(0.5, `hsla(${gH}, 40%, 70%, ${intensity * 0.3})`);
      grad.addColorStop(1, `hsla(${gH}, 40%, 70%, 0)`);
      ctx.fillStyle = grad; ctx.beginPath(); ctx.arc(cx, cy, radius, 0, Math.PI * 2); ctx.fill();
    };
    const drawConservationRings = () => {
      if (drawQualityRef.current < 0.6 || branches.length < 3) return;
      const beta = systemState.beta;
      const ringR = 25 + collectiveBreath * 3;
      // D_• ring (aperture dimension)
      const dArc = (1 + beta) / 3 * Math.PI * 2;
      ctx.strokeStyle = `rgba(100, 200, 255, 0.12)`;
      ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(cx, cy, ringR, -Math.PI / 2, -Math.PI / 2 + dArc); ctx.stroke();
      // D_Φ ring (field dimension)
      ctx.strokeStyle = `rgba(200, 100, 255, 0.12)`;
      ctx.beginPath(); ctx.arc(cx, cy, ringR, -Math.PI / 2 + dArc, -Math.PI / 2 + dArc + (2 - beta) / 3 * Math.PI * 2); ctx.stroke();
    };
    const drawEnergyFlows = () => {
      energyFlowsRef.current = energyFlowsRef.current.filter(flow => {
        flow.age++; flow.strength *= 0.94;
        if (flow.strength < 0.08 || flow.age > 80) return false;
        const alpha = flow.strength * 0.3;
        const grad = ctx.createLinearGradient(flow.x1, flow.y1, flow.x2, flow.y2);
        grad.addColorStop(0, `rgba(100, 200, 255, ${alpha})`); grad.addColorStop(1, `rgba(200, 100, 255, ${alpha * 0.5})`);
        ctx.strokeStyle = grad; ctx.lineWidth = 2.5 * flow.strength; ctx.lineCap = 'round';
        ctx.beginPath(); ctx.moveTo(flow.x1, flow.y1); ctx.lineTo(flow.x2, flow.y2); ctx.stroke();
        branches.forEach(e => {
          const dx = e.x - flow.x2; const dy = e.y - flow.y2;
          const d = Math.sqrt(dx * dx + dy * dy);
          if (d < 90) e.angle += Math.sin(Math.atan2(flow.y2 - flow.y1, flow.x2 - flow.x1) - e.angle) * (1 - d / 90) * flow.strength * 0.08;
        });
        return true;
      });
    };
    const updateFPS = () => {
      const now = Date.now(); const delta = now - lastFrameTime.current;
      lastFrameTime.current = now; fpsHistory.current.push(1000 / delta);
      if (fpsHistory.current.length > 60) fpsHistory.current.shift();
      const avg = fpsHistory.current.reduce((a, b) => a + b, 0) / fpsHistory.current.length;
      setFps(Math.round(avg));
      if (avg < 25) { qualityCounter.current--; if (qualityCounter.current < -10) { drawQualityRef.current = Math.max(0.2, drawQualityRef.current - 0.08); qualityCounter.current = 0; } }
      else if (avg > 40) { qualityCounter.current++; if (qualityCounter.current > 25) { drawQualityRef.current = Math.min(1.0, drawQualityRef.current + 0.04); qualityCounter.current = 0; } }
      else { qualityCounter.current = Math.max(-5, Math.min(5, qualityCounter.current)); }
      setDrawQuality(drawQualityRef.current);
    };

    // ═══ EVENTS ═══
    let isDragging = false; let dragStart = null;
    const handleMouseDown = (e) => { const r = canvas.getBoundingClientRect(); dragStart = { x: (e.clientX - r.left) / zoomRef.current, y: (e.clientY - r.top) / zoomRef.current }; isDragging = true; };
    const handleMouseMove = (e) => { if (!isDragging || !dragStart) return; const r = canvas.getBoundingClientRect(); const x = (e.clientX - r.left) / zoomRef.current; const y = (e.clientY - r.top) / zoomRef.current; energyFlowsRef.current.push({ x1: dragStart.x, y1: dragStart.y, x2: x, y2: y, strength: 1, age: 0 }); dragStart = { x, y }; };
    const handleMouseUp = (e) => {
      if (!isDragging) {
        const r = canvas.getBoundingClientRect();
        const clickX = (e.clientX - r.left) / zoomRef.current;
        const clickY = (e.clientY - r.top) / zoomRef.current;
        const angle = Math.atan2(clickY - cy, clickX - cx);
        let hue = Math.random() * 360; let geom = Math.random() * 6;
        if (dominantNote) { hue = ((dominantNote.frequency - 80) / 1920) * 360; geom = dominantNote.amplitude * 6; }
        const ne = new BranchEntity(angle, hue, time);
        ne.baseLength = Math.min(Math.sqrt((clickX - cx) ** 2 + (clickY - cy) ** 2), 250);
        ne.geometryType = geom; ne.userSpawned = true; ne.spawnEnergy = 1.8;
        branches.push(ne);
        playTone(200 + (hue / 360) * 400, 0.2, 0.12);
        if (brainFormed && brainClouds.length > 0) {
          const nearest = brainClouds.reduce((best, c) => { const d = Math.min(Math.abs(c.angle - angle), Math.PI * 2 - Math.abs(c.angle - angle)) * 100; return d < best.dist ? { cloud: c, dist: d } : best; }, { cloud: null, dist: Infinity });
          if (nearest.cloud) { nearest.cloud.particles.forEach(p => { p.excitement = Math.min(2, p.excitement + 0.7); p.targetEntity = ne; }); nearest.cloud.spawnCell(time, expandingCells); }
        }
      }
      isDragging = false; dragStart = null;
    };
    const handleTouchStart = (e) => { e.preventDefault(); const r = canvas.getBoundingClientRect(); for (let t of e.touches) touchesRef.current.set(t.identifier, { x: (t.clientX - r.left) / zoomRef.current, y: (t.clientY - r.top) / zoomRef.current }); };
    const handleTouchMove = (e) => { e.preventDefault(); const r = canvas.getBoundingClientRect(); for (let t of e.touches) { const x = (t.clientX - r.left) / zoomRef.current; const y = (t.clientY - r.top) / zoomRef.current; const p = touchesRef.current.get(t.identifier); if (p) energyFlowsRef.current.push({ x1: p.x, y1: p.y, x2: x, y2: y, strength: 1, age: 0 }); touchesRef.current.set(t.identifier, { x, y }); } };
    const handleTouchEnd = (e) => { e.preventDefault(); for (let t of e.changedTouches) touchesRef.current.delete(t.identifier); };

    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseup', handleMouseUp);
    canvas.addEventListener('touchstart', handleTouchStart, { passive: false });
    canvas.addEventListener('touchmove', handleTouchMove, { passive: false });
    canvas.addEventListener('touchend', handleTouchEnd, { passive: false });

    // ═══════════════════════════════════════════════════════
    //  ANIMATION LOOP — The full ⊛ → i → ☀️ cycle
    //  Bidirectional: branches grow outward, roots grow inward
    //  The trunk carries energy both ways
    // ═══════════════════════════════════════════════════════
    const animate = () => {
      time++;
      collectiveBreath = Math.sin(time * 0.004) * 0.5 + 0.5;
      updateFPS(); analyzeAudio();

      ctx.fillStyle = 'rgba(8, 8, 14, 0.14)';
      ctx.fillRect(0, 0, W, H);

      // ─── System β from branches ───
      if (branches.length > 0) {
        let bS = 0, cS = 0, eS = 0;
        branches.forEach(e => { bS += e.aperture.beta; cS += e.field.convergenceStrength; eS += e.field.emergenceStrength; });
        systemState.beta = bS / branches.length;
        systemState.convergenceNorm = cS / branches.length;
        systemState.emergenceNorm = eS / branches.length;
        systemState.rho = systemState.emergenceNorm / (systemState.convergenceNorm + params.epsilon);
      }

      // ─── Brain formation (outer) ───
      if (branches.length > 12 && !brainFormed) {
        brainFormationProgress += 0.008;
        if (brainFormationProgress >= 1) {
          brainFormed = true;
          const num = 5 + Math.floor(Math.random() * 3);
          for (let i = 0; i < num; i++) brainClouds.push(new BrainCloud((i / num) * Math.PI * 2 + (Math.random() - 0.5) * 0.3, 190 + Math.random() * 90, time));
        }
      }

      // ─── Root cloud formation (inner) ───
      if (roots.length > 4 && !rootsFormed) {
        rootFormationProgress += 0.006;
        if (rootFormationProgress >= 1) {
          rootsFormed = true;
          const num = 3 + Math.floor(Math.random() * 3);
          for (let i = 0; i < num; i++) rootClouds.push(new RootCloud((i / num) * Math.PI * 2, 80 + Math.random() * 40, time));
        }
      }

      let fieldCoherence = 0;
      if (brainFormed && brainClouds.length > 0) fieldCoherence = Math.min(0.85, brainClouds.reduce((s, c) => s + c.energyLevel, 0) / brainClouds.length);

      // ─── Zoom ───
      const bz = 1 + Math.sin(time * 0.003) * 0.008;
      ctx.save(); ctx.translate(cx, cy); ctx.scale(zoomRef.current * bz, zoomRef.current * bz); ctx.translate(-cx, -cy);

      // ─── Spawn branches ───
      if (brainFormed) {
        brainClouds.forEach(cloud => {
          if (Math.random() < 0.012 * drawQualityRef.current * growthSpeedRef.current) {
            const rp = cloud.particles[Math.floor(Math.random() * cloud.particles.length)];
            rp.excitement = Math.min(2, rp.excitement + 1.3);
            if (Math.random() < 0.35) {
              let hue = Math.random() * 360; let geom = Math.random() * 6;
              if (dominantNote) { hue = ((dominantNote.frequency - 80) / 1920) * 360; geom = dominantNote.amplitude * 6; }
              const ne = new BranchEntity(cloud.angle + (Math.random() - 0.5) * 0.3, hue, time);
              ne.geometryType = geom;
              if (dominantNote) { ne.musicalNote = dominantNote.note; ne.baseFrequency = dominantNote.frequency; }
              branches.push(ne); cloud.spawnCell(time, expandingCells);
            }
          }
        });
        if (dominantNote && soundEnabled && time - harmonicResponse.current.lastTime > 55 && learnedMelody.current.length > 4 && Math.random() < 0.25) {
          const rn = learnedMelody.current[Math.floor(Math.random() * Math.min(6, learnedMelody.current.length))];
          if (rn) { [1, 1.5, 2].forEach((h, i) => { setTimeout(() => playTone(rn.frequency * h, 0.3, 0.04 / (i + 1)), i * 35); }); }
          harmonicResponse.current.lastTime = time;
        }
      } else {
        if (Math.random() < 0.018 * drawQualityRef.current * growthSpeedRef.current) {
          let hue = Math.random() * 360;
          if (dominantNote) hue = ((dominantNote.frequency - 80) / 1920) * 360;
          const ne = new BranchEntity(Math.random() * Math.PI * 2, hue, time);
          if (dominantNote) { ne.musicalNote = dominantNote.note; ne.baseFrequency = dominantNote.frequency; }
          branches.push(ne);
        }
      }

      // ═══ BRANCH → ROOT CONVERSION ═══
      // "What emerged becomes memory. Branches become trunk become roots."
      branches.forEach(branch => {
        if (branch.maturity >= 1 && !branch.rootSpawned && roots.length < 35) {
          const newRoot = new RootEntity(branch, time);
          roots.push(newRoot);
          branch.rootSpawned = true;
          // Trunk flow downward — experience → memory
          trunkFlows.push(new TrunkFlow(branch.angle, time, -1, branch.hue));
          playTone(100 + newRoot.memory.originalBeta * 80, 0.4, 0.04);
          memoryBraid.push({ hue: branch.baseHue, beta: branch.aperture.beta, time: time });
          if (memoryBraid.length > 64) memoryBraid.shift();
        }
      });

      // ═══ IMAGINATION — Roots dream ghost branches ═══
      roots.forEach(root => {
        if (root.imaginationStrength > 0.4 && Math.random() < 0.006 * root.imaginationStrength * growthSpeedRef.current) {
          ghostBranches.push(new GhostBranch(root, time));
          // Trunk flow upward — imagination → reality
          trunkFlows.push(new TrunkFlow(root.parentAngle, time, 1, (root.hue + 180) % 360));
        }
      });

      // ─── Update everything ───
      branches.forEach(e => e.update(time, branches));
      roots.forEach(r => r.update(time, roots, branches, fieldCoherence));
      if (brainFormed) brainClouds.forEach(c => c.update(time, branches, collectiveBreath));
      if (rootsFormed) rootClouds.forEach(c => c.update(time, roots, collectiveBreath));
      expandingCells = expandingCells.filter(c => c.update());
      ghostBranches = ghostBranches.filter(g => g.update());
      trunkFlows = trunkFlows.filter(f => f.update());

      // ═══════════════════════════════════════════════════
      //  DRAW ORDER: Inner → Trunk → Outer
      //  "Roots behind, branches in front"
      // ═══════════════════════════════════════════════════

      drawInnerGlow();
      if (rootsFormed) rootClouds.forEach(c => c.draw(ctx, time));
      roots.forEach(r => r.draw(ctx, time, fieldCoherence));
      ghostBranches.forEach(g => g.draw(ctx, time));
      trunkFlows.forEach(f => f.draw(ctx, time));
      drawConservationRings();
      drawOuterGlow();
      drawEnergyFlows();
      branches.forEach(e => e.draw(ctx, time));
      expandingCells.forEach(c => c.draw(ctx));

      if (brainFormed) {
        brainClouds.forEach(c => c.draw(ctx, time, fieldCoherence));
        if (drawQualityRef.current > 0.5) {
          brainClouds.forEach((c1, i) => {
            brainClouds.slice(i + 1).forEach(c2 => {
              const nd = Math.min(Math.abs(c1.angle - c2.angle), Math.PI * 2 - Math.abs(c1.angle - c2.angle));
              if (nd < Math.PI / 4) {
                const str = 1 - nd / (Math.PI / 4);
                ctx.strokeStyle = `hsla(${(c1.hue + c2.hue) / 2}, 65%, 62%, ${(c1.alpha + c2.alpha) / 2 * str * 0.2})`;
                ctx.lineWidth = 1.5 + str * 2.5;
                ctx.beginPath(); ctx.moveTo(cx + Math.cos(c1.angle) * c1.distance, cy + Math.sin(c1.angle) * c1.distance);
                ctx.lineTo(cx + Math.cos(c2.angle) * c2.distance, cy + Math.sin(c2.angle) * c2.distance); ctx.stroke();
              }
            });
          });
        }
      }

      // Circuits
      if (drawQualityRef.current > 0.4) {
        branches.forEach(e1 => {
          e1.neighbors.forEach(e2 => {
            let ex = circuits.find(c => (c.e1 === e1 && c.e2 === e2) || (c.e1 === e2 && c.e2 === e1));
            if (ex) { ex.update(time, true, fieldCoherence); if (ex.strength > 0.65 && time - ex.lastPulseTime > 25) { energyPulses.push(new EnergyPulse(ex, 1)); energyPulses.push(new EnergyPulse(ex, -1)); ex.lastPulseTime = time; } }
            else { circuits.push(new Circuit(e1, e2, time)); e1.circuitPartners.add(e2.id); e2.circuitPartners.add(e1.id); }
          });
        });
      }
      circuits = circuits.filter(c => { c.update(time, branches.includes(c.e1) && branches.includes(c.e2) && c.e1.neighbors.includes(c.e2), fieldCoherence); if (!c.shouldRemove()) { c.draw(ctx, fieldCoherence, time); return true; } return false; });
      energyPulses = energyPulses.filter(p => { const alive = p.update(fieldCoherence); if (alive) p.draw(ctx, fieldCoherence); return alive; });

      // Cap
      if (branches.length > 50) branches = branches.slice(-50);
      if (roots.length > 35) roots = roots.slice(-35);

      ctx.restore();

      // ─── Center ⊙ — THE TRUNK ───
      const centerAlpha = 0.15 + systemState.beta * 0.2 + collectiveBreath * 0.08;
      const centerSize = 14 + collectiveBreath * 5;
      ctx.strokeStyle = `rgba(200, 200, 255, ${centerAlpha})`;
      ctx.lineWidth = 1.5; ctx.beginPath(); ctx.arc(cx, cy, centerSize, 0, Math.PI * 2); ctx.stroke();
      if (roots.length > 0) {
        const rootAlpha = Math.min(0.3, roots.length * 0.02);
        ctx.strokeStyle = `rgba(160, 140, 255, ${rootAlpha})`;
        ctx.lineWidth = 0.8; ctx.setLineDash([2, 4]);
        ctx.beginPath(); ctx.arc(cx, cy, centerSize * 0.6, 0, Math.PI * 2); ctx.stroke();
        ctx.setLineDash([]);
      }
      ctx.fillStyle = `rgba(255, 255, 255, ${centerAlpha * 1.3})`;
      ctx.beginPath(); ctx.arc(cx, cy, 2.5, 0, Math.PI * 2); ctx.fill();

      // ─── Metrics ───
      if (time % 20 === 0) {
        const beta = systemState.beta;
        let phaseCoherence = 0;
        if (branches.length > 1) { let ps = 0; branches.forEach(e => { ps += e.field.coherence; }); phaseCoherence = ps / branches.length; }
        const avgIm = roots.length > 0 ? roots.reduce((s, r) => s + r.imaginationStrength, 0) / roots.length : 0;
        const avgDepth = roots.length > 0 ? roots.reduce((s, r) => s + r.depth, 0) / roots.length : 0;
        setMetrics({
          beta, dAperture: 1 + beta, dField: 2 - beta, dBoundary: 3.0,
          rho: systemState.rho, fieldCoherence, phaseCoherence,
          patternCount: branches.length, convergenceNorm: systemState.convergenceNorm,
          emergenceNorm: systemState.emergenceNorm,
          rootCount: roots.length, rootDepth: avgDepth,
          trunkFlow: trunkFlows.length, imaginationStrength: avgIm,
        });
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();
    return () => {
      canvas.removeEventListener('mousedown', handleMouseDown); canvas.removeEventListener('mousemove', handleMouseMove);
      canvas.removeEventListener('mouseup', handleMouseUp); canvas.removeEventListener('touchstart', handleTouchStart);
      canvas.removeEventListener('touchmove', handleTouchMove); canvas.removeEventListener('touchend', handleTouchEnd);
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, [playTone, playHarmonic, resetKey]);

  useEffect(() => { zoomRef.current = zoomLevel; }, [zoomLevel]);
  useEffect(() => { growthSpeedRef.current = growthSpeed; }, [growthSpeed]);

  const handleReset = () => {
    setZoomLevel(1); setGrowthSpeed(1.0); setDrawQuality(1.0); setFps(60);
    zoomRef.current = 1; growthSpeedRef.current = 1.0; drawQualityRef.current = 1.0;
    qualityCounter.current = 0; fpsHistory.current = []; lastFrameTime.current = Date.now();
    energyFlowsRef.current = []; touchesRef.current.clear(); setResetKey(p => p + 1);
  };
  const toggleSound = () => { if (!soundEnabled) { const c = initAudio(); if (c.state === 'suspended') c.resume(); } setSoundEnabled(!soundEnabled); };
  const toggleMic = async () => { if (!micEnabled) { if (await initMicrophone()) setMicEnabled(true); } else { stopMicrophone(); setMicEnabled(false); } };

  const betaColor = metrics.beta > 0.55 ? 'text-blue-300' : metrics.beta < 0.45 ? 'text-red-300' : 'text-green-300';
  const rhoLabel = metrics.rho < 0.5 ? 'Overdamped' : metrics.rho > 2 ? 'Overdriven' : 'Critical';
  const rhoColor = metrics.rho < 0.5 ? 'text-blue-400' : metrics.rho > 2 ? 'text-red-400' : 'text-green-400';

  return (
    <div className="w-full h-screen bg-gray-950 overflow-hidden relative" style={{ fontFamily: "'JetBrains Mono', 'Fira Code', monospace" }}>
      <canvas ref={canvasRef} className="w-full h-full cursor-crosshair" />

      {showMetrics && (
        <div className="absolute top-3 left-3 bg-slate-950 rounded-xl p-3 border border-indigo-500/40 text-white text-xs space-y-1" style={{ minWidth: '260px', backgroundColor: 'rgba(5,5,20,0.92)', backdropFilter: 'blur(12px)' }}>
          <div className="text-sm font-bold text-indigo-300 mb-1.5 pb-1.5 border-b border-indigo-500/30 flex items-center gap-2">
            <span style={{ fontSize: '1rem' }}>⊙</span> The Tree That Dreams
          </div>
          <div className="text-xs text-gray-600 mb-1">D• + DΦ = D○ = 3 &nbsp;|&nbsp; ☀️↕⊛</div>

          <div className="flex justify-between">
            <span className="text-gray-400">β (opening):</span>
            <span className={betaColor}>{metrics.beta.toFixed(3)}</span>
          </div>
          <div className="w-full bg-gray-800 h-1 rounded overflow-hidden">
            <div className="h-full rounded transition-all" style={{ width: `${metrics.beta * 100}%`, background: 'linear-gradient(90deg, hsl(0,70%,55%), hsl(60,70%,55%) 50%, hsl(140,70%,55%))' }}></div>
          </div>

          <div className="grid grid-cols-3 gap-1.5 pt-0.5">
            <div className="text-center"><div className="text-gray-600 text-xs">D•</div><div className="text-cyan-300">{metrics.dAperture.toFixed(2)}</div></div>
            <div className="text-center"><div className="text-gray-600 text-xs">DΦ</div><div className="text-purple-300">{metrics.dField.toFixed(2)}</div></div>
            <div className="text-center"><div className="text-gray-600 text-xs">D○</div><div className="text-amber-300">{metrics.dBoundary.toFixed(1)}</div></div>
          </div>

          <div className="flex justify-between"><span className="text-gray-400">ρ:</span><span className={rhoColor}>{metrics.rho.toFixed(2)} — {rhoLabel}</span></div>

          <div className="border-t border-gray-800/60 pt-1 mt-1">
            <div className="text-xs text-gray-500 mb-0.5">☀️ Branches (outer · objective)</div>
            <div className="flex justify-between"><span className="text-gray-600">count:</span><span className="text-yellow-400">{metrics.patternCount}</span></div>
            <div className="flex justify-between"><span className="text-gray-600">Φ coherence:</span><span className="text-teal-400">{(metrics.fieldCoherence * 100).toFixed(0)}%</span></div>
          </div>

          <div className="border-t border-gray-800/60 pt-1 mt-1">
            <div className="text-xs text-gray-500 mb-0.5">⊛ Roots (inner · subjective)</div>
            <div className="flex justify-between"><span className="text-gray-600">count:</span><span className="text-violet-400">{metrics.rootCount}</span></div>
            <div className="flex justify-between"><span className="text-gray-600">depth:</span><span className="text-violet-300">{metrics.rootDepth.toFixed(1)}</span></div>
            <div className="flex justify-between"><span className="text-gray-600">imagination:</span><span className="text-pink-400">{(metrics.imaginationStrength * 100).toFixed(0)}%</span></div>
            <div className="flex justify-between"><span className="text-gray-600">trunk flows:</span><span className="text-blue-300">{metrics.trunkFlow}</span></div>
          </div>

          <div className="border-t border-gray-800/60 pt-1 mt-1 flex justify-between">
            <span className="text-gray-600">FPS:</span>
            <span className={fps >= 30 ? 'text-green-400' : 'text-yellow-400'}>{fps} ({(drawQuality * 100).toFixed(0)}%)</span>
          </div>
        </div>
      )}

      <div className="absolute top-3 right-3 bg-slate-950 rounded-xl p-3 border border-indigo-500/40 text-white space-y-2" style={{ minWidth: '170px', backgroundColor: 'rgba(5,5,20,0.92)', backdropFilter: 'blur(12px)' }}>
        <div className="text-xs text-gray-400">
          <label className="block mb-1">Growth: {growthSpeed.toFixed(1)}×</label>
          <input type="range" min="0.1" max="3" step="0.1" value={growthSpeed} onChange={e => setGrowthSpeed(parseFloat(e.target.value))} className="w-full" />
        </div>
        <div className="flex gap-2 pt-2 border-t border-gray-800">
          <button onClick={toggleMic} className={`flex-1 py-1.5 rounded-lg text-lg transition ${micEnabled ? 'bg-red-600/70 hover:bg-red-500' : 'bg-gray-700/70 hover:bg-gray-600'}`}>{micEnabled ? '🎤' : '🎙️'}</button>
          <button onClick={toggleSound} className={`flex-1 py-1.5 rounded-lg text-lg transition ${soundEnabled ? 'bg-indigo-600/70 hover:bg-indigo-500' : 'bg-gray-700/70 hover:bg-gray-600'}`}>{soundEnabled ? '🔊' : '🔇'}</button>
        </div>
      </div>

      <div className="absolute bottom-4 left-4 flex gap-2 flex-wrap max-w-lg">
        {[['Zoom +', () => setZoomLevel(z => Math.min(z * 1.4, 8))], ['Zoom −', () => setZoomLevel(z => Math.max(z / 1.4, 0.3))], ['Reset', handleReset], [showMetrics ? 'Hide ⊙' : 'Show ⊙', () => setShowMetrics(!showMetrics)]].map(([label, fn]) => (
          <button key={label} onClick={fn} className="px-3 py-1.5 bg-indigo-700/70 hover:bg-indigo-500 text-white text-xs rounded-lg transition border border-indigo-500/30" style={{ backdropFilter: 'blur(8px)' }}>{label}</button>
        ))}
      </div>

      <div className="absolute bottom-4 right-4 text-gray-600 text-xs px-3 py-1.5 rounded-lg border border-gray-700/30" style={{ backgroundColor: 'rgba(10,10,20,0.5)', backdropFilter: 'blur(8px)' }}>
        {zoomLevel.toFixed(2)}× • {zoomLevel > 1.1 ? '☀️ canopy' : zoomLevel < 0.9 ? '⊛ roots' : '⊙ trunk'}
      </div>
    </div>
  );
};

export default CircumpunctFractalSimulator;
