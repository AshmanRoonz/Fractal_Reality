import React, { useEffect, useRef, useState } from 'react';

// ============================================================================
// CONFIGURATION
// ============================================================================
const CONFIG = {
  canvas: {
    width: 1200,
    height: 800,
  },
  
  souls: {
    spacing: 60,              // Distance between main souls
    subSoulSpacing: 12,       // Distance between sub-souls within a soul (3×3 grid)
    pixelSpacing: 3,          // Distance between pixels within a sub-soul (3×3 grid)
  },
  
  packet: {
    speed: 8.0,               // Movement speed
    acceleration: 0.3,        // Acceleration toward target
    maxSpeed: 12.0,           // Maximum speed
    lightningSegments: 8,     // Number of segments in lightning bolt
    branchProbability: 0.4,   // Chance of branching
    maxBranches: 3,           // Max branches per segment
    jumpDistance: 200,        // Max distance to jump to next soul
    activationRadius: 25,     // Activation distance
    trailLength: 35,          // Length of lightning trail
    dwellTime: 2,             // Frames to pause at soul before jumping
    lightningFadeFrames: 20,  // How long lightning bolts persist
    lengthVariation: 1.0,     // Can be up to 100% longer (2x)
  },
  
  sparks: {
    emissionThreshold: 0.9,   // Activation level needed to emit sparks (higher = less frequent)
    emissionCooldown: 90,     // Frames between spark emissions (longer cooldown)
    count: [2, 4],            // Min/max sparks per emission (fewer sparks)
    speed: 3.0,               // Spark movement speed (not used in fractal version)
    maxAge: 50,               // Frames before spark fades out
    maxRange: 53,             // Max length of fractal sparks (33% shorter)
    waveStrength: 0.6,        // Strength of waves created by sparks (subtler)
    branchProbability: 0.55,  // Increased chance of branching for more fractal look
  },
  
  waves: {
    speed: 5.0,               // Wave propagation speed
    maxRadius: 120,           // Max wave radius
    colorInfluence: 0.5,      // How much waves affect colors
    decay: 0.012,             // Wave strength decay per frame
    wakeSpacing: 3,           // Distance between wake rings
    wakeWidth: 20,            // Width of wake ring effect
  },
  
  resonance: {
    frequencyWeight: 0.4,     // Importance of frequency match
    phaseWeight: 0.3,         // Importance of phase alignment
    distanceWeight: 0.3,      // Importance of proximity
  },
  
  zoom: {
    enabled: true,
    maxFrames: 90,
    startScale: 20,
    endScale: 1,
  },
  
  physics: {
    fieldDecay: 0.96,
    fieldInfluence: 0.25,
    pulseSpeed: 0.08,
    environmentInfluence: 0.2,
    parentInfluence: 0.15,     // How much parent soul affects sub-souls
    childInfluence: 0.05,      // How much sub-souls affect parent
  },
  
  visuals: {
    fadeAlpha: 0.12,
    glowRadius: 15,
    envGlowRadius: 22,
    backgroundAlpha: 0.03,
  },
  
  axions: {
    activationThreshold: 0.6,     // 60% of souls must be active
    maxDistance: 250,             // Maximum distance for spark path recording (increased)
    visibilityThreshold: 0.08,    // Strength needed to become visible (lowered for faster formation)
    growthPerSpark: 0.05,         // How much strength each spark adds (2-3 sparks makes visible)
    decayRate: 0.9995,            // Very slow decay - pathways persist
  },
  
  performance: {
    fpsThreshold: 30,             // FPS below this triggers core mode
    fpsCheckInterval: 60,         // Check FPS every N frames
    coreModeSparkReduction: 0.4,  // Reduce spark emission by 60% in core mode
    coreModePathwayLimit: 500,    // Max pathways in core mode
  }
};

// ============================================================================
// WAVE SYSTEM - Smooth trailing wake
// ============================================================================
class WaveSystem {
  constructor() {
    this.waves = [];
    this.lastEmitX = 0;
    this.lastEmitY = 0;
  }
  
  emitWake(x, y, strength = 1.0, hue = 200) {
    // Only emit if moved enough distance
    const dist = Math.hypot(x - this.lastEmitX, y - this.lastEmitY);
    if (dist > CONFIG.waves.wakeSpacing) {
      this.waves.push({
        x, y,
        radius: 0,
        strength,
        hue,
        age: 0
      });
      this.lastEmitX = x;
      this.lastEmitY = y;
    }
  }
  
  emitBurst(x, y, strength = 1.5, hue = 200) {
    // Larger burst when hitting a soul
    this.waves.push({
      x, y,
      radius: 0,
      strength,
      hue,
      age: 0
    });
  }
  
  update() {
    for (let i = this.waves.length - 1; i >= 0; i--) {
      const wave = this.waves[i];
      wave.radius += CONFIG.waves.speed;
      wave.strength -= CONFIG.waves.decay;
      wave.age++;
      
      if (wave.radius > CONFIG.waves.maxRadius || wave.strength <= 0) {
        this.waves.splice(i, 1);
      }
    }
  }
  
  getInterferenceAt(x, y) {
    let totalStrength = 0;
    let totalHue = 0;
    let count = 0;
    
    for (const wave of this.waves) {
      const dist = Math.hypot(x - wave.x, y - wave.y);
      const distFromRing = Math.abs(dist - wave.radius);
      
      if (distFromRing < CONFIG.waves.wakeWidth) {
        const influence = (1 - distFromRing / CONFIG.waves.wakeWidth) * wave.strength;
        totalStrength += influence;
        totalHue += wave.hue * influence;
        count++;
      }
    }
    
    return count > 0 ? {
      strength: totalStrength,
      hue: totalHue / count
    } : null;
  }
}

// ============================================================================
// SPARK SYSTEM - Fractal 1px sparks emitted by charged souls
// ============================================================================
class SparkSystem {
  constructor() {
    this.sparks = [];
  }
  
  emitFromSoul(soul) {
    // Sparks follow recursive pattern - emit from active sub-souls!
    // Find the most active sub-souls
    const activeSubSouls = soul.subSouls
      .filter(ss => ss.activation > 0.3)
      .sort((a, b) => b.activation - a.activation);
    
    if (activeSubSouls.length === 0) return;
    
    // Emit from top 3-5 active sub-souls
    const numSparks = Math.min(activeSubSouls.length, 2 + Math.floor(Math.random() * 3));
    
    for (let i = 0; i < numSparks; i++) {
      const subSoul = activeSubSouls[i];
      
      // Direction based on sub-soul position in parent grid
      const dx = subSoul.ix - 1; // -1, 0, 1
      const dy = subSoul.iy - 1;
      let angle = Math.atan2(dy, dx);
      
      // If center sub-soul, use random angle
      if (Math.abs(dx) < 0.1 && Math.abs(dy) < 0.1) {
        angle = Math.random() * Math.PI * 2;
      }
      
      // Add some variation
      angle += (Math.random() - 0.5) * 0.4;
      
      // Emit from sub-soul position
      this.createFractalSpark(subSoul.x, subSoul.y, angle, subSoul.hue, 0, soul, subSoul);
    }
  }
  
  
  createFractalSpark(x, y, angle, baseHue, depth, soul, subSoul = null) {
    // Length influenced by subSoul's activation if available, else soul's
    const lengthFactor = subSoul ? subSoul.activation : (soul ? soul.activationLevel : 1.0);
    const length = CONFIG.sparks.maxRange * (0.3 + Math.random() * 0.3) * lengthFactor * Math.pow(0.7, depth);
    const segments = [];
    const numSegments = Math.floor(length / 8) + 3;
    
    // Use subSoul properties for pattern if available
    const patternPhase = subSoul ? subSoul.phase : (soul ? soul.phase : 0);
    const patternFreq = subSoul ? subSoul.frequency : (soul ? soul.frequency : 0.02);
    
    // Create main spark path - pattern influenced by subSoul
    for (let i = 0; i <= numSegments; i++) {
      const t = i / numSegments;
      const dist = length * t;
      
      // Increased jitter influenced by subSoul's phase for more fractal look
      const phaseInfluence = Math.sin(patternPhase + t * Math.PI * 2);
      const jitter = (Math.random() - 0.5 + phaseInfluence * 0.5) * 10 * (1 - t * 0.7);
      const jitterAngle = angle + Math.PI / 2;
      
      // Add extra wiggle for fractal appearance
      const wiggle = Math.sin(t * Math.PI * 6 + patternPhase) * 3;
      
      segments.push({
        x: x + Math.cos(angle) * dist + Math.cos(jitterAngle) * jitter + Math.cos(angle + Math.PI / 3) * wiggle,
        y: y + Math.sin(angle) * dist + Math.sin(jitterAngle) * jitter + Math.sin(angle + Math.PI / 3) * wiggle
      });
    }
    
    // Create branches recursively
    const branches = [];
    
    const createBranch = (parentSegs, fromIndex, branchAngle, branchLength, branchDepth) => {
      if (branchDepth > 2 || branchLength < 5) return;
      
      const startSeg = parentSegs[fromIndex];
      const branchSegments = [];
      const branchSteps = Math.floor(branchLength / 6) + 2;
      
      for (let i = 0; i <= branchSteps; i++) {
        const t = i / branchSteps;
        const dist = branchLength * t;
        
        // SubSoul-influenced wiggle with extra fractal variation
        const freqInfluence = Math.cos(patternFreq * 200 + t * Math.PI * 4);
        const wiggle = freqInfluence * branchLength * 0.15;
        const wiggleAngle = branchAngle + Math.PI / 2;
        
        // Additional high-frequency jitter for more fractal appearance
        const jitter = (Math.random() - 0.5) * 2 * (1 - t * 0.5);
        
        branchSegments.push({
          x: startSeg.x + Math.cos(branchAngle) * dist + Math.cos(wiggleAngle) * wiggle + jitter,
          y: startSeg.y + Math.sin(branchAngle) * dist + Math.sin(wiggleAngle) * wiggle + jitter
        });
      }
      
      branches.push({
        segments: branchSegments,
        depth: branchDepth
      });
      
      // Recursive sub-branches - probability influenced by subSoul frequency
      const branchChance = 0.45 + patternFreq * 10;
      if (branchDepth < 2 && branchSteps > 2) {
        const subPoint = Math.floor(branchSteps * (0.4 + Math.random() * 0.4));
        const subLength = branchLength * (0.4 + Math.random() * 0.35);
        
        if (Math.random() < branchChance) {
          const leftAngle = branchAngle - Math.PI / 5 - Math.random() * Math.PI / 8;
          createBranch(branchSegments, subPoint, leftAngle, subLength, branchDepth + 1);
        }
        
        if (Math.random() < branchChance) {
          const rightAngle = branchAngle + Math.PI / 5 + Math.random() * Math.PI / 8;
          createBranch(branchSegments, subPoint, rightAngle, subLength, branchDepth + 1);
        }
      }
    };
    
    // Add initial branches - pattern based on subSoul's frequency
    const branchFrequency = Math.max(2, Math.floor(patternFreq * 150));
    for (let i = 2; i < segments.length - 1; i += branchFrequency) {
      if (Math.random() < CONFIG.sparks.branchProbability) {
        const side = Math.random() < 0.5 ? 1 : -1;
        const perpAngle = angle + (Math.PI / 2) * side + (Math.random() - 0.5) * 0.5;
        const branchLength = length * (0.2 + Math.random() * 0.25);
        createBranch(segments, i, perpAngle, branchLength, 0);
      }
    }
    
    this.sparks.push({
      segments,
      branches,
      hue: baseHue + (Math.random() - 0.5) * 40,
      alpha: 1.0,
      age: 0,
      maxAge: CONFIG.sparks.maxAge,
      originX: x,
      originY: y
    });
  }
  
  update(waveSystem, axionSystem = null, soulSystem = null) {
    for (let i = this.sparks.length - 1; i >= 0; i--) {
      const spark = this.sparks[i];
      
      spark.age++;
      spark.alpha = 1.0 - (spark.age / spark.maxAge);
      
      // Emit wave at origin periodically
      if (spark.age % 8 === 0 && spark.age < spark.maxAge * 0.7) {
        waveSystem.emitWake(spark.originX, spark.originY, CONFIG.sparks.waveStrength, spark.hue);
      }
      
      // Record spark path for axion system at multiple points in its life
      if (axionSystem && soulSystem) {
        // Record at 30%, 50%, and 70% of spark lifetime
        const lifePercent = spark.age / spark.maxAge;
        if (lifePercent >= 0.3 && lifePercent <= 0.31 ||
            lifePercent >= 0.5 && lifePercent <= 0.51 ||
            lifePercent >= 0.7 && lifePercent <= 0.71) {
          axionSystem.recordSparkPath(spark, soulSystem);
        }
      }
      
      // Remove if expired
      if (spark.age > spark.maxAge) {
        waveSystem.emitBurst(spark.originX, spark.originY, CONFIG.sparks.waveStrength * 1.2, spark.hue);
        this.sparks.splice(i, 1);
      }
    }
  }
}

// ============================================================================
// AXION SYSTEM - Neural connections that grow from repeated spark paths
// ============================================================================
class AxionSystem {
  constructor() {
    this.pathTraces = new Map(); // Map of path keys to trace strength
    this.connections = []; // Array of visible axion connections
    this.enabled = false;
    this.coreMode = false; // Performance optimization mode
    this.connectedSouls = new Set(); // Souls that are part of the network
  }
  
  updateActivationStatus(soulSystem) {
    // Enable axions when 60% of souls are active
    const activeRatio = soulSystem.getActiveSoulCount() / soulSystem.souls.length;
    this.enabled = activeRatio >= CONFIG.axions.activationThreshold;
  }
  
  checkPerformance(fps) {
    // Activate core mode if FPS is low and we have many pathways
    if (fps < CONFIG.performance.fpsThreshold && this.connections.length > 100) {
      this.coreMode = true;
    } else if (fps > CONFIG.performance.fpsThreshold + 10 && this.connections.length < 50) {
      // Deactivate core mode if performance recovers and network is smaller
      this.coreMode = false;
    }
  }
  
  isSoulConnected(soul, soulSystem) {
    // Check if this soul is part of the axion network
    if (!this.coreMode) return true; // In normal mode, all souls can be active
    
    const soulIdx = soulSystem.souls.indexOf(soul);
    return this.connectedSouls.has(soulIdx);
  }
  
  recordSparkPath(spark, soulSystem) {
    // Record the path a spark takes - find which souls it's near
    const originSoul = this.findNearestSoul(spark.originX, spark.originY, soulSystem);
    if (!originSoul) return;
    
    // Check multiple points along the spark path, not just the end
    const checkPoints = [
      Math.floor(spark.segments.length * 0.5),  // midpoint
      spark.segments.length - 1                  // endpoint
    ];
    
    for (const idx of checkPoints) {
      if (idx < 0 || idx >= spark.segments.length) continue;
      
      const seg = spark.segments[idx];
      const endSoul = this.findNearestSoul(seg.x, seg.y, soulSystem);
      
      if (!endSoul || endSoul === originSoul) continue;
      
      // Create a key for this path (sorted so direction doesn't matter)
      const soul1Idx = soulSystem.souls.indexOf(originSoul);
      const soul2Idx = soulSystem.souls.indexOf(endSoul);
      
      if (soul1Idx === -1 || soul2Idx === -1) continue;
      
      const key = soul1Idx < soul2Idx ? `${soul1Idx}-${soul2Idx}` : `${soul2Idx}-${soul1Idx}`;
      
      // Record this path and store the actual spark segments for organic shape
      const existing = this.pathTraces.get(key);
      if (existing) {
        existing.strength = Math.min(1.5, existing.strength + CONFIG.axions.growthPerSpark);
        existing.lastTravel = Date.now();
        // Keep updating the path shape with latest spark
        existing.recentPaths.push({
          segments: [...spark.segments],
          age: 0
        });
        if (existing.recentPaths.length > 8) {
          existing.recentPaths.shift();
        }
      } else {
        this.pathTraces.set(key, {
          soul1: originSoul,
          soul2: endSoul,
          strength: CONFIG.axions.growthPerSpark,
          lastTravel: Date.now(),
          recentPaths: [{
            segments: [...spark.segments],
            age: 0
          }]
        });
      }
    }
  }
  
  findNearestSoul(x, y, soulSystem) {
    let nearest = null;
    let minDist = CONFIG.axions.maxDistance;
    
    for (const soul of soulSystem.souls) {
      if (!soul.activated) continue;
      const dist = Math.hypot(soul.x - x, soul.y - y);
      if (dist < minDist) {
        minDist = dist;
        nearest = soul;
      }
    }
    return nearest;
  }
  
  update(soulSystem, frameCount) {
    if (!this.enabled) return;
    
    // Decay path traces over time
    for (const [key, trace] of this.pathTraces.entries()) {
      const timeSinceTravel = Date.now() - trace.lastTravel;
      
      // Very slow decay - only after significant time
      if (timeSinceTravel > 500) {
        trace.strength *= CONFIG.axions.decayRate;
      }
      
      // Age recent paths
      for (const path of trace.recentPaths) {
        path.age++;
      }
      
      // Remove very weak traces
      if (trace.strength < 0.005) {
        this.pathTraces.delete(key);
      }
    }
    
    // Convert strong traces into visible connections
    this.connections = [];
    this.connectedSouls.clear();
    
    // In core mode, limit the number of pathways
    const maxPathways = this.coreMode ? 500 : 10000;
    
    for (const [key, trace] of this.pathTraces.entries()) {
      if (trace.strength > CONFIG.axions.visibilityThreshold) {
        // Average the recent paths for organic shape
        const avgPath = this.averageSparkPaths(trace.recentPaths);
        
        this.connections.push({
          soul1: trace.soul1,
          soul2: trace.soul2,
          strength: Math.min(1, trace.strength / 1.5), // Normalize to 0-1 range
          segments: avgPath
        });
        
        // Track connected souls
        const soul1Idx = this.pathTraces.get(key) ? soulSystem.souls.indexOf(trace.soul1) : -1;
        const soul2Idx = this.pathTraces.get(key) ? soulSystem.souls.indexOf(trace.soul2) : -1;
        if (soul1Idx !== -1) this.connectedSouls.add(soul1Idx);
        if (soul2Idx !== -1) this.connectedSouls.add(soul2Idx);
        
        // Stop if we hit the limit
        if (this.connections.length >= maxPathways) break;
      }
    }
    
    // In core mode, aggressively prune weak traces
    if (this.coreMode && this.pathTraces.size > maxPathways) {
      // Remove weakest traces
      const sortedTraces = Array.from(this.pathTraces.entries())
        .sort((a, b) => a[1].strength - b[1].strength);
      
      for (let i = 0; i < sortedTraces.length - maxPathways; i++) {
        this.pathTraces.delete(sortedTraces[i][0]);
      }
    }
  }
  
  averageSparkPaths(recentPaths) {
    if (!recentPaths || recentPaths.length === 0) return [];
    
    // Find the path with most segments as base
    const basePath = recentPaths.reduce((max, p) => 
      p.segments.length > max.segments.length ? p : max
    , recentPaths[0]);
    
    const numSegments = basePath.segments.length;
    const avgSegments = [];
    
    // Average positions across all paths
    for (let i = 0; i < numSegments; i++) {
      let sumX = 0, sumY = 0, count = 0;
      
      for (const path of recentPaths) {
        if (path.segments[i]) {
          const weight = 1 / (1 + path.age * 0.1); // Newer paths weighted more
          sumX += path.segments[i].x * weight;
          sumY += path.segments[i].y * weight;
          count += weight;
        }
      }
      
      avgSegments.push({
        x: sumX / count,
        y: sumY / count
      });
    }
    
    return avgSegments;
  }
  
  getConnections() {
    return this.connections;
  }
}

// ============================================================================
// PACKET SYSTEM - Single fractal lightning packet with smooth motion
// ============================================================================
class PacketSystem {
  constructor(width, height) {
    this.width = width;
    this.height = height;
    this.packet = null;
    this.lightningBolts = []; // Persistent lightning bolts from jumps
    this.initializePacket();
  }
  
  initializePacket() {
    // Start from outside, aimed at center
    const angle = Math.random() * Math.PI * 2;
    const distance = Math.max(this.width, this.height);
    
    this.packet = {
      x: this.width / 2 + Math.cos(angle) * distance,
      y: this.height / 2 + Math.sin(angle) * distance,
      targetX: this.width / 2,
      targetY: this.height / 2,
      vx: 0,
      vy: 0,
      speed: 0, // Current speed
      trail: [],
      hue: 180 + Math.random() * 60,
      phase: 0,
      frequency: 0.015,
      targetSoul: null,
      dwellCounter: 0,
      mode: 'traveling', // 'traveling' or 'dwelling'
      visible: true, // Visible during zoom phase
      frameCount: 0
    };
    
    this.updateAcceleration();
  }
  
  updateAcceleration() {
    const dx = this.packet.targetX - this.packet.x;
    const dy = this.packet.targetY - this.packet.y;
    const dist = Math.hypot(dx, dy);
    
    if (dist > 0) {
      // Accelerate toward target
      const targetVx = (dx / dist) * CONFIG.packet.maxSpeed;
      const targetVy = (dy / dist) * CONFIG.packet.maxSpeed;
      
      this.packet.vx += (targetVx - this.packet.vx) * CONFIG.packet.acceleration;
      this.packet.vy += (targetVy - this.packet.vy) * CONFIG.packet.acceleration;
      
      // Clamp to max speed
      this.packet.speed = Math.hypot(this.packet.vx, this.packet.vy);
      if (this.packet.speed > CONFIG.packet.maxSpeed) {
        this.packet.vx = (this.packet.vx / this.packet.speed) * CONFIG.packet.maxSpeed;
        this.packet.vy = (this.packet.vy / this.packet.speed) * CONFIG.packet.maxSpeed;
        this.packet.speed = CONFIG.packet.maxSpeed;
      }
    }
  }
  
  findNextTarget(soulSystem, axionSystem = null) {
    let bestSoul = null;
    let bestScore = -Infinity;
    
    for (const soul of soulSystem.souls) {
      const dist = Math.hypot(soul.x - this.packet.x, soul.y - this.packet.y);
      if (dist > CONFIG.packet.jumpDistance) continue;
      if (dist < 5) continue;
      
      // Skip if this was the last target (avoid ping-pong)
      if (soul === this.packet.targetSoul) continue;
      
      // In core mode, strongly prefer connected souls
      let connectionBonus = 0;
      if (axionSystem && axionSystem.coreMode) {
        const isConnected = axionSystem.isSoulConnected(soul, soulSystem);
        if (isConnected) {
          connectionBonus = 0.8; // Huge bonus for connected souls
        } else {
          connectionBonus = -0.5; // Penalty for non-connected souls
        }
      }
      
      // Calculate resonance score with gravity-like attraction
      const freqDiff = Math.abs(soul.frequency - this.packet.frequency);
      const freqScore = (1 - freqDiff / 0.03) * CONFIG.resonance.frequencyWeight;
      
      const phaseDiff = Math.abs(soul.phase - this.packet.phase);
      const normalizedPhaseDiff = Math.min(phaseDiff, Math.PI * 2 - phaseDiff) / Math.PI;
      const phaseScore = (1 - normalizedPhaseDiff) * CONFIG.resonance.phaseWeight;
      
      // Stronger distance attraction
      const distScore = (1 - dist / CONFIG.packet.jumpDistance) * CONFIG.resonance.distanceWeight;
      
      // Strongly prefer unactivated souls
      const activationBonus = soul.activated ? 0.05 : 0.4;
      
      // Penalize recently hit souls
      const timeSinceHit = this.packet.frameCount - (soul.lastHitTime || 0);
      const recencyPenalty = timeSinceHit < 50 ? -0.3 : 0;
      
      const totalScore = freqScore + phaseScore + distScore + activationBonus + recencyPenalty + connectionBonus + Math.random() * 0.3;
      
      if (totalScore > bestScore) {
        bestScore = totalScore;
        bestSoul = soul;
      }
    }
    
    return bestSoul;
  }
  
  createLightningBolt(fromX, fromY, toX, toY) {
    // Create a lightning bolt with fractal branching
    const segments = [];
    const numSegments = CONFIG.packet.lightningSegments;
    
    const dx = toX - fromX;
    const dy = toY - fromY;
    
    for (let i = 0; i <= numSegments; i++) {
      const t = i / numSegments;
      const x = fromX + dx * t;
      const y = fromY + dy * t;
      
      // Add jitter perpendicular to direction
      const perpX = -dy;
      const perpY = dx;
      const len = Math.hypot(perpX, perpY);
      
      const jitter = (Math.random() - 0.5) * 12 * (1 - Math.abs(t - 0.5) * 2);
      
      segments.push({
        x: x + (perpX / len) * jitter,
        y: y + (perpY / len) * jitter
      });
    }
    
    // Create fractal branches recursively
    const branches = [];
    
    const createFractalBranch = (parentSegments, fromIndex, baseAngle, length, depth) => {
      if (depth > 3 || length < 3) return;
      
      const startSeg = parentSegments[fromIndex];
      
      // Create branch outward
      const angleVariation = (Math.random() - 0.5) * Math.PI / 6;
      const branchAngle = baseAngle + angleVariation;
      
      const branchSegments = [];
      const branchSteps = Math.floor(length / 5) + 2;
      
      for (let i = 0; i <= branchSteps; i++) {
        const t = i / branchSteps;
        const dist = length * t;
        
        // Add fractal wiggle
        const wiggle = Math.sin(t * Math.PI * 3) * length * 0.12;
        const wiggleAngle = branchAngle + Math.PI / 2;
        
        branchSegments.push({
          x: startSeg.x + Math.cos(branchAngle) * dist + Math.cos(wiggleAngle) * wiggle,
          y: startSeg.y + Math.sin(branchAngle) * dist + Math.sin(wiggleAngle) * wiggle
        });
      }
      
      branches.push({
        segments: branchSegments,
        depth,
        alpha: 1.0
      });
      
      // Recursively create sub-branches from THIS branch
      if (depth < 3 && branchSteps > 2) {
        const subBranchPoint = Math.floor(branchSteps * (0.5 + Math.random() * 0.3));
        
        // Chance to branch left
        if (Math.random() < 0.5) {
          const leftAngle = branchAngle - Math.PI / 4 - Math.random() * Math.PI / 12;
          const subLength = length * (0.4 + Math.random() * 0.3);
          createFractalBranch(branchSegments, subBranchPoint, leftAngle, subLength, depth + 1);
        }
        
        // Chance to branch right  
        if (Math.random() < 0.5) {
          const rightAngle = branchAngle + Math.PI / 4 + Math.random() * Math.PI / 12;
          const subLength = length * (0.4 + Math.random() * 0.3);
          createFractalBranch(branchSegments, subBranchPoint, rightAngle, subLength, depth + 1);
        }
      }
    };
    
    // Create initial branches from main bolt perpendicular
    const mainAngle = Math.atan2(dy, dx);
    for (let i = 2; i < segments.length - 2; i += 2) {
      if (Math.random() < 0.35) {
        const side = Math.random() < 0.5 ? 1 : -1;
        const perpAngle = mainAngle + (Math.PI / 2) * side;
        const branchLength = 10 + Math.random() * 15;
        createFractalBranch(segments, i, perpAngle, branchLength, 0);
      }
    }
    
    this.lightningBolts.push({
      segments,
      branches,
      hue: this.packet.hue,
      alpha: 1.0,
      age: 0
    });
  }
  
  update(soulSystem, waveSystem, frameCount, axionSystem = null) {
    this.packet.phase += this.packet.frequency;
    this.packet.frameCount = frameCount;
    
    // Update persistent lightning bolts
    for (let i = this.lightningBolts.length - 1; i >= 0; i--) {
      const bolt = this.lightningBolts[i];
      bolt.age++;
      bolt.alpha = 1.0 - (bolt.age / CONFIG.packet.lightningFadeFrames);
      
      if (bolt.alpha <= 0) {
        this.lightningBolts.splice(i, 1);
      }
    }
    
    if (this.packet.mode === 'traveling') {
      // Emit wake continuously while moving
      if (this.packet.speed > 1) {
        waveSystem.emitWake(this.packet.x, this.packet.y, 0.8, this.packet.hue);
      }
      
      // Smooth acceleration toward target
      this.updateAcceleration();
      
      // Move packet
      this.packet.trail.push({ x: this.packet.x, y: this.packet.y });
      if (this.packet.trail.length > CONFIG.packet.trailLength) {
        this.packet.trail.shift();
      }
      
      this.packet.x += this.packet.vx;
      this.packet.y += this.packet.vy;
      
      // Check if reached target
      const distToTarget = Math.hypot(
        this.packet.x - this.packet.targetX,
        this.packet.y - this.packet.targetY
      );
      
      if (distToTarget < CONFIG.packet.activationRadius) {
        // Hit a soul!
        const soul = this.packet.targetSoul;
        if (soul) {
          if (soul.activated) {
            this.lightUpSoul(soul, frameCount);
          } else {
            soulSystem.activate(soul, frameCount);
          }
          
          // Emit burst wave
          waveSystem.emitBurst(soul.x, soul.y, 1.5, this.packet.hue);
        }
        
        // Find next target immediately (no dwelling)
        const nextSoul = this.findNextTarget(soulSystem, axionSystem);
        if (nextSoul) {
          // Create lightning bolt from current position to next soul
          this.createLightningBolt(this.packet.x, this.packet.y, nextSoul.x, nextSoul.y);
          
          this.packet.targetSoul = nextSoul;
          this.packet.targetX = nextSoul.x;
          this.packet.targetY = nextSoul.y;
          this.packet.trail = [];
          
          // Slight hue shift
          this.packet.hue = (this.packet.hue + Math.random() * 20 - 10 + 360) % 360;
        }
      }
    }
  }
  
  lightUpSoul(soul, frameCount) {
    // Recursively boost all sub-souls and their pixels
    const boost = 0.3;
    
    for (const subSoul of soul.subSouls) {
      subSoul.activation = Math.min(1, subSoul.activation + boost);
      
      for (const pixel of subSoul.pixels) {
        if (pixel.active) {
          const pixelBoost = boost * (pixel.role === 'core' ? 1.2 : 
                                      pixel.role === 'inner' ? 1.0 : 0.8);
          pixel.b = Math.min(1, pixel.b + pixelBoost);
        }
      }
    }
    
    soul.activationLevel = Math.min(1, soul.activationLevel + 0.3);
    soul.lastHitTime = frameCount;
  }
}

// ============================================================================
// SOUL SYSTEM - Now with environment layer (12D)
// ============================================================================
class SoulSystem {
  constructor(width, height, spacing) {
    this.souls = [];
    this.centerSoul = null;
    this.initializeSouls(width, height, spacing);
  }
  
  initializeSouls(width, height, spacing) {
    for (let x = spacing; x < width - spacing; x += spacing) {
      for (let y = spacing; y < height - spacing; y += spacing) {
        this.souls.push(this.createSoul(x, y));
      }
    }
    
    // Find center soul
    const centerX = width / 2;
    const centerY = height / 2;
    let minDist = Infinity;
    
    for (const soul of this.souls) {
      const dist = Math.hypot(soul.x - centerX, soul.y - centerY);
      if (dist < minDist) {
        minDist = dist;
        this.centerSoul = soul;
      }
    }
  }
  
  createSoul(x, y) {
    const baseHue = Math.random() * 360;
    
    // Create 3×3 grid of sub-souls (9 total) - RECURSIVE STRUCTURE
    const subSouls = [];
    for (let iy = 0; iy < 3; iy++) {
      for (let ix = 0; ix < 3; ix++) {
        subSouls.push(this.createSubSoul(x, y, ix, iy, baseHue));
      }
    }
    
    return {
      x, y,
      phase: Math.random() * Math.PI * 2,
      frequency: 0.01 + Math.random() * 0.02,
      baseHue,
      activated: false,
      activationLevel: 0,
      activationTime: 0,
      lastHitTime: -1000,
      lastSparkEmission: -1000,
      subSouls, // 9 sub-souls, each with 9 pixels = 81 total
    };
  }
  
  createSubSoul(baseX, baseY, ix, iy, soulHue) {
    // Each sub-soul is offset within the parent soul (3×3 grid)
    const spacing = CONFIG.souls.subSoulSpacing;
    const offset = spacing * (3 - 1) / 2;
    
    const x = baseX + ix * spacing - offset;
    const y = baseY + iy * spacing - offset;
    
    // Sub-soul properties influenced by position
    const positionInfluence = (ix + iy * 3);
    const hue = (soulHue + positionInfluence * 40) % 360;
    
    return {
      x, y,
      ix, iy, // Grid position (0-2)
      phase: Math.random() * Math.PI * 2,
      frequency: 0.015 + Math.random() * 0.01,
      hue,
      activation: 0,
      pixels: this.createPixelsForSubSoul(hue) // 3×3 = 9 pixels
    };
  }
  
  createPixelsForSubSoul(baseHue) {
    // Create 3×3 grid of pixels for a sub-soul (9 pixels)
    const pixels = [];
    
    for (let y = 0; y < 3; y++) {
      for (let x = 0; x < 3; x++) {
        const dx = x - 1; // -1, 0, 1
        const dy = y - 1;
        const distFromCenter = Math.hypot(dx, dy);
        
        // Role based on distance from center
        let role;
        if (distFromCenter < 0.5) {
          role = 'core';
        } else if (distFromCenter < 1.5) {
          role = 'inner';
        } else {
          role = 'outer';
        }
        
        const angle = Math.atan2(dy, dx);
        const hueOffset = angle * 57.3; // Angle in degrees
        
        pixels.push({
          x, y,
          h: (baseHue + hueOffset) % 360,
          s: 0.6,
          b: 0,
          role,
          active: false
        });
      }
    }
    
    return pixels;
  }
  
  activate(soul, frameCount) {
    if (soul.activated) return;
    
    soul.activated = true;
    soul.activationLevel = 1.0;
    soul.activationTime = frameCount;
    soul.lastHitTime = frameCount;
    
    // Recursively activate sub-souls and their pixels
    for (const subSoul of soul.subSouls) {
      // Activation pattern based on sub-soul position
      const dx = subSoul.ix - 1;
      const dy = subSoul.iy - 1;
      const distFromCenter = Math.hypot(dx, dy);
      const angle = Math.atan2(dy, dx);
      
      // Activation strength decreases with distance
      const activationStrength = 1.0 - (distFromCenter / 2);
      subSoul.activation = Math.random() * 0.3 + activationStrength * 0.7;
      
      // Activate pixels within sub-soul
      for (const pixel of subSoul.pixels) {
        const pdx = pixel.x - 1;
        const pdy = pixel.y - 1;
        const pAngle = Math.atan2(pdy, pdx);
        
        // Pattern based on angles
        const phaseMatch = Math.cos(angle - pAngle + soul.phase);
        pixel.b = (0.3 + Math.random() * 0.4) * (0.5 + phaseMatch * 0.5);
        pixel.active = pixel.b > 0.1;
      }
    }
  }
  
  update(frameCount, waveSystem, sparkSystem, axionSystem = null) {
    for (const soul of this.souls) {
      this.updateSoul(soul, frameCount, waveSystem, sparkSystem, axionSystem);
    }
  }
  
  updateSoul(soul, frameCount, waveSystem, sparkSystem, axionSystem = null) {
    soul.phase += soul.frequency;
    if (soul.phase > Math.PI * 2) soul.phase -= Math.PI * 2;
    
    if (!soul.activated) return;
    
    // Check if soul is charged up enough to emit sparks
    if (soul.activationLevel > CONFIG.sparks.emissionThreshold) {
      // In core mode, only connected souls emit sparks
      const canEmit = !axionSystem || !axionSystem.coreMode || 
                      axionSystem.isSoulConnected(soul, this);
      
      if (canEmit) {
        const timeSinceLastSpark = frameCount - (soul.lastSparkEmission || 0);
        const emissionCooldown = axionSystem && axionSystem.coreMode 
          ? CONFIG.sparks.emissionCooldown / CONFIG.performance.coreModeSparkReduction
          : CONFIG.sparks.emissionCooldown;
          
        if (timeSinceLastSpark > emissionCooldown) {
          sparkSystem.emitFromSoul(soul);
          soul.lastSparkEmission = frameCount;
          soul.activationLevel = Math.max(0.6, soul.activationLevel - 0.15);
        }
      }
    }
    
    // Decay from last packet hit
    const timeSinceHit = frameCount - soul.lastHitTime;
    const hitRecency = Math.max(0, 1 - timeSinceHit / 100);
    
    // Check wave interference
    const interference = waveSystem.getInterferenceAt(soul.x, soul.y);
    const waveBoost = interference ? interference.strength * 0.4 : 0;
    
    // RECURSIVE UPDATE: Update each sub-soul
    for (const subSoul of soul.subSouls) {
      // Sub-soul phase progression
      subSoul.phase += subSoul.frequency;
      if (subSoul.phase > Math.PI * 2) subSoul.phase -= Math.PI * 2;
      
      // Parent influences sub-soul
      subSoul.activation += soul.activationLevel * CONFIG.physics.parentInfluence;
      
      // Update pixels within sub-soul
      for (const pixel of subSoul.pixels) {
        const dx = pixel.x - 1;
        const dy = pixel.y - 1;
        const angle = Math.atan2(dy, dx);
        
        let baseBrightness = 0;
        
        if (pixel.role === 'core') {
          // Core pulses with sub-soul's phase
          const pulse = Math.sin(subSoul.phase) * 0.4 + 0.6;
          baseBrightness = pulse * subSoul.activation * 0.9;
        } else if (pixel.role === 'inner') {
          // Inner ring pulses with harmonics
          const harmonic = Math.sin(subSoul.phase * 2 + angle * 2) * 0.3 + 0.5;
          baseBrightness = harmonic * subSoul.activation * 0.7;
        } else if (pixel.role === 'outer') {
          // Outer responds to waves
          const envPulse = Math.sin(frameCount * 0.03 + angle * 3) * 0.3 + 0.5;
          baseBrightness = (envPulse * 0.5 + waveBoost) * subSoul.activation * 0.6;
        }
        
        // Apply wave interference to colors
        if (interference && interference.strength > 0.1) {
          const waveInfluence = interference.strength * CONFIG.waves.colorInfluence;
          pixel.h = (pixel.h * (1 - waveInfluence) + interference.hue * waveInfluence) % 360;
        }
        
        // Add hit boost
        baseBrightness = Math.min(1, baseBrightness + hitRecency * 0.3);
        
        // Smooth transition
        pixel.b = pixel.b * 0.9 + baseBrightness * 0.1;
        pixel.active = pixel.b > 0.05;
      }
      
      // Decay sub-soul activation
      subSoul.activation *= 0.98;
    }
    
    // BIDIRECTIONAL INFLUENCE: Sub-souls influence parent
    const avgSubSoulActivation = soul.subSouls.reduce((sum, ss) => sum + ss.activation, 0) / soul.subSouls.length;
    soul.activationLevel = soul.activationLevel * 0.95 + avgSubSoulActivation * 0.05;
    
    // Update main activation level
    const age = frameCount - soul.activationTime;
    const activationPulse = Math.sin(age * 0.03) * 0.2;
    soul.activationLevel = Math.min(1, soul.activationLevel + activationPulse * 0.1 + hitRecency * 0.2);
  }
  
  getActiveSoulCount() {
    return this.souls.filter(s => s.activated).length;
  }
}

// ============================================================================
// RENDERER
// ============================================================================
class Renderer {
  constructor(ctx, width, height) {
    this.ctx = ctx;
    this.width = width;
    this.height = height;
  }
  
  renderZoomPhase(centerSoul, zoomFrame) {
    const progress = zoomFrame / CONFIG.zoom.maxFrames;
    const eased = 1 - Math.pow(1 - progress, 3);
    const scale = CONFIG.zoom.startScale - ((CONFIG.zoom.startScale - CONFIG.zoom.endScale) * eased);
    
    this.ctx.fillStyle = 'black';
    this.ctx.fillRect(0, 0, this.width, this.height);
    
    this.ctx.save();
    this.ctx.translate(this.width / 2, this.height / 2);
    this.ctx.scale(scale, scale);
    this.ctx.translate(-this.width / 2, -this.height / 2);
    
    const pulse = Math.sin(zoomFrame * 0.1) * 0.3 + 0.7;
    this.ctx.beginPath();
    this.ctx.arc(centerSoul.x, centerSoul.y, 3, 0, Math.PI * 2);
    this.ctx.fillStyle = `hsla(${centerSoul.baseHue}, 90%, 70%, ${pulse})`;
    this.ctx.fill();
    
    const gradient = this.ctx.createRadialGradient(
      centerSoul.x, centerSoul.y, 0, 
      centerSoul.x, centerSoul.y, 15
    );
    gradient.addColorStop(0, `hsla(${centerSoul.baseHue}, 80%, 60%, ${0.4 * pulse})`);
    gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
    this.ctx.fillStyle = gradient;
    this.ctx.fillRect(centerSoul.x - 15, centerSoul.y - 15, 30, 30);
    
    this.ctx.restore();
    
    this.ctx.fillStyle = `rgba(255, 255, 255, ${0.2 + eased * 0.5})`;
    this.ctx.font = '32px serif';
    this.ctx.textAlign = 'center';
    this.ctx.fillText('∞ = 1', this.width / 2, this.height / 2 - 100);
  }
  
  renderMainPhase(soulSystem, packetSystem, waveSystem, sparkSystem, axionSystem, frameCount, isZoomPhase = false) {
    // Subtle fade
    this.ctx.fillStyle = `rgba(0, 0, 0, ${CONFIG.visuals.fadeAlpha})`;
    this.ctx.fillRect(0, 0, this.width, this.height);
    
    // Render axion connections first (behind everything)
    this.renderAxions(axionSystem);
    
    // Render waves (wake) - invisible now
    this.renderWaves(waveSystem);
    
    // Render packet (lightning bolts and optionally the packet during zoom)
    this.renderPacket(packetSystem, isZoomPhase);
    
    // Render sparks
    this.renderSparks(sparkSystem);
    
    // Render souls
    this.renderSouls(soulSystem, frameCount);
  }
  
  renderAxions(axionSystem) {
    if (!axionSystem || !axionSystem.enabled) return;
    
    const connections = axionSystem.getConnections();
    
    for (const conn of connections) {
      if (!conn.segments || conn.segments.length < 2) continue;
      
      const { segments, strength } = conn;
      
      // Calculate hue from souls
      const avgHue = (conn.soul1.baseHue + conn.soul2.baseHue) / 2;
      
      this.ctx.save();
      
      // Draw as thin organic line following the spark path
      this.ctx.beginPath();
      this.ctx.moveTo(segments[0].x, segments[0].y);
      
      for (let i = 1; i < segments.length; i++) {
        this.ctx.lineTo(segments[i].x, segments[i].y);
      }
      
      // Subtle glow
      this.ctx.shadowBlur = 5;
      this.ctx.shadowColor = `hsla(${avgHue}, 75%, 65%, ${strength * 0.25})`;
      
      // Main thin line - 1px like sparks
      this.ctx.strokeStyle = `hsla(${avgHue}, 85%, 70%, ${strength * 0.6})`;
      this.ctx.lineWidth = 1;
      this.ctx.stroke();
      
      // Slightly brighter core for stronger connections
      if (strength > 0.3) {
        this.ctx.strokeStyle = `hsla(${avgHue}, 90%, 80%, ${(strength - 0.3) * 0.5})`;
        this.ctx.lineWidth = 0.5;
        this.ctx.stroke();
      }
      
      this.ctx.restore();
    }
  }
  
  renderWaves(waveSystem) {
    // Waves are now invisible - they only influence pixel colors
    // No rendering needed
  }
  
  renderPacket(packetSystem, isZoomPhase) {
    const packet = packetSystem.packet;
    
    // Render persistent lightning bolts from jumps
    for (const bolt of packetSystem.lightningBolts) {
      this.ctx.save();
      this.ctx.shadowBlur = 6;
      this.ctx.shadowColor = `hsla(${bolt.hue}, 90%, 70%, ${bolt.alpha * 0.3})`;
      
      // Draw main bolt segments
      this.ctx.beginPath();
      this.ctx.moveTo(bolt.segments[0].x, bolt.segments[0].y);
      for (let i = 1; i < bolt.segments.length; i++) {
        this.ctx.lineTo(bolt.segments[i].x, bolt.segments[i].y);
      }
      this.ctx.strokeStyle = `hsla(${bolt.hue}, 95%, 75%, ${bolt.alpha * 0.8})`;
      this.ctx.lineWidth = 1.5;
      this.ctx.stroke();
      
      // Draw glow
      this.ctx.strokeStyle = `hsla(${bolt.hue}, 100%, 85%, ${bolt.alpha * 0.25})`;
      this.ctx.lineWidth = 3;
      this.ctx.stroke();
      
      // Draw fractal branches (new structure with segments)
      for (const branch of bolt.branches) {
        if (branch.segments && branch.segments.length > 1) {
          // Calculate alpha based on depth (deeper branches are dimmer)
          const depthAlpha = Math.pow(0.75, branch.depth || 0);
          
          this.ctx.beginPath();
          this.ctx.moveTo(branch.segments[0].x, branch.segments[0].y);
          for (let i = 1; i < branch.segments.length; i++) {
            this.ctx.lineTo(branch.segments[i].x, branch.segments[i].y);
          }
          this.ctx.strokeStyle = `hsla(${bolt.hue}, 90%, 70%, ${bolt.alpha * depthAlpha * 0.7})`;
          this.ctx.lineWidth = 1.0; // 1px as requested
          this.ctx.stroke();
        }
      }
      
      this.ctx.restore();
    }
    
    // Only show packet itself during zoom phase
    if (isZoomPhase && packet.trail.length > 1) {
      this.ctx.shadowBlur = 15;
      this.ctx.shadowColor = `hsla(${packet.hue}, 90%, 70%, 0.8)`;
      
      for (let i = 1; i < packet.trail.length; i++) {
        const alpha = i / packet.trail.length;
        this.ctx.beginPath();
        this.ctx.moveTo(packet.trail[i - 1].x, packet.trail[i - 1].y);
        this.ctx.lineTo(packet.trail[i].x, packet.trail[i].y);
        this.ctx.strokeStyle = `hsla(${packet.hue}, 90%, 70%, ${alpha * 0.9})`;
        this.ctx.lineWidth = 3;
        this.ctx.stroke();
      }
      
      this.ctx.shadowBlur = 0;
      
      // Draw packet head
      this.ctx.shadowBlur = 20;
      this.ctx.shadowColor = `hsla(${packet.hue}, 100%, 80%, 1)`;
      this.ctx.beginPath();
      this.ctx.arc(packet.x, packet.y, 4, 0, Math.PI * 2);
      this.ctx.fillStyle = `hsla(${packet.hue}, 100%, 90%, 1)`;
      this.ctx.fill();
      this.ctx.shadowBlur = 0;
    }
  }
  
  renderSparks(sparkSystem) {
    for (const spark of sparkSystem.sparks) {
      this.ctx.save();
      
      // Main spark path - 1px
      this.ctx.beginPath();
      this.ctx.moveTo(spark.segments[0].x, spark.segments[0].y);
      for (let i = 1; i < spark.segments.length; i++) {
        this.ctx.lineTo(spark.segments[i].x, spark.segments[i].y);
      }
      this.ctx.strokeStyle = `hsla(${spark.hue}, 90%, 70%, ${spark.alpha * 0.8})`;
      this.ctx.lineWidth = 1.0; // 1px
      this.ctx.stroke();
      
      // Draw fractal branches - 1px
      for (const branch of spark.branches) {
        if (branch.segments && branch.segments.length > 1) {
          const depthAlpha = Math.pow(0.7, branch.depth || 0);
          
          this.ctx.beginPath();
          this.ctx.moveTo(branch.segments[0].x, branch.segments[0].y);
          for (let i = 1; i < branch.segments.length; i++) {
            this.ctx.lineTo(branch.segments[i].x, branch.segments[i].y);
          }
          this.ctx.strokeStyle = `hsla(${spark.hue}, 85%, 65%, ${spark.alpha * depthAlpha * 0.7})`;
          this.ctx.lineWidth = 1.0; // 1px
          this.ctx.stroke();
        }
      }
      
      this.ctx.restore();
    }
  }
  
  renderSouls(soulSystem, frameCount) {
    for (const soul of soulSystem.souls) {
      if (!soul.activated) {
        this.renderInactiveSoul(soul);
      } else {
        this.renderActiveSoul(soul, frameCount);
      }
    }
  }
  
  renderInactiveSoul(soul) {
    this.ctx.beginPath();
    this.ctx.arc(soul.x, soul.y, 1.5, 0, Math.PI * 2);
    this.ctx.fillStyle = `hsla(${soul.baseHue}, 40%, 50%, 0.15)`;
    this.ctx.fill();
  }
  
  renderActiveSoul(soul, frameCount) {
    // Environment glow (larger, dimmer)
    const envGradient = this.ctx.createRadialGradient(
      soul.x, soul.y, 0, 
      soul.x, soul.y, CONFIG.visuals.envGlowRadius
    );
    envGradient.addColorStop(0, `hsla(${soul.baseHue}, 60%, 50%, ${0.08 * soul.activationLevel})`);
    envGradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
    this.ctx.fillStyle = envGradient;
    this.ctx.fillRect(
      soul.x - CONFIG.visuals.envGlowRadius, 
      soul.y - CONFIG.visuals.envGlowRadius, 
      CONFIG.visuals.envGlowRadius * 2, 
      CONFIG.visuals.envGlowRadius * 2
    );
    
    // Center core
    const pulse = Math.sin(frameCount * CONFIG.physics.pulseSpeed + soul.phase) * 0.3 + 0.7;
    this.ctx.beginPath();
    this.ctx.arc(soul.x, soul.y, 3.5, 0, Math.PI * 2);
    this.ctx.fillStyle = `hsla(${soul.baseHue}, 90%, 70%, ${pulse * soul.activationLevel})`;
    this.ctx.fill();
    
    // Inner glow
    const gradient = this.ctx.createRadialGradient(
      soul.x, soul.y, 0, 
      soul.x, soul.y, CONFIG.visuals.glowRadius
    );
    gradient.addColorStop(0, `hsla(${soul.baseHue}, 80%, 60%, ${0.25 * soul.activationLevel})`);
    gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
    this.ctx.fillStyle = gradient;
    this.ctx.fillRect(
      soul.x - CONFIG.visuals.glowRadius, 
      soul.y - CONFIG.visuals.glowRadius, 
      CONFIG.visuals.glowRadius * 2, 
      CONFIG.visuals.glowRadius * 2
    );
    
    // 81-pixel grid (9x9)
    this.render81PixelGrid(soul);
  }
  
  render81PixelGrid(soul) {
    // Render 9 sub-souls, each with 9 pixels (81 total)
    const pixelSpacing = CONFIG.souls.pixelSpacing;
    
    for (const subSoul of soul.subSouls) {
      // Render all 9 pixels in this sub-soul
      for (const pixel of subSoul.pixels) {
        if (!pixel.active) continue;
        
        const brightness = pixel.b * soul.activationLevel * subSoul.activation;
        if (brightness < 0.05) continue;
        
        // Calculate screen position relative to sub-soul center
        const pixelX = subSoul.x + (pixel.x - 1) * pixelSpacing;
        const pixelY = subSoul.y + (pixel.y - 1) * pixelSpacing;
        
        // Pixel size based on role
        let size = 2;
        let alpha = brightness * 0.8;
        
        if (pixel.role === 'core') {
          size = 3;
          alpha = brightness * 1.0;
        } else if (pixel.role === 'inner') {
          size = 2.5;
          alpha = brightness * 0.9;
        } else if (pixel.role === 'outer') {
          size = 2;
          alpha = brightness * 0.7;
        }
        
        this.ctx.fillStyle = `hsla(${pixel.h}, ${pixel.s * 100}%, 55%, ${alpha})`;
        this.ctx.fillRect(pixelX - size/2, pixelY - size/2, size, size);
      }
    }
  }
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================
const FractalSoulArray = () => {
  const canvasRef = useRef(null);
  const [stats, setStats] = useState({ souls: 0, sparks: 0, frame: 0, axions: 0, traces: 0, axionsEnabled: false, fps: 60, coreMode: false });
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    canvas.width = CONFIG.canvas.width;
    canvas.height = CONFIG.canvas.height;
    
    // Initialize systems
    const soulSystem = new SoulSystem(
      CONFIG.canvas.width, 
      CONFIG.canvas.height, 
      CONFIG.souls.spacing
    );
    const packetSystem = new PacketSystem(CONFIG.canvas.width, CONFIG.canvas.height);
    const waveSystem = new WaveSystem();
    const sparkSystem = new SparkSystem();
    const axionSystem = new AxionSystem();
    const renderer = new Renderer(ctx, CONFIG.canvas.width, CONFIG.canvas.height);
    
    // Set initial target to center soul
    packetSystem.packet.targetSoul = soulSystem.centerSoul;
    packetSystem.packet.targetX = soulSystem.centerSoul.x;
    packetSystem.packet.targetY = soulSystem.centerSoul.y;
    packetSystem.updateAcceleration();
    
    let frameCount = 0;
    let zoomPhase = CONFIG.zoom.enabled;
    let zoomFrame = 0;
    
    // FPS tracking
    let lastTime = performance.now();
    let frameTimeSum = 0;
    let frameTimeCount = 0;
    let currentFPS = 60;
    
    const animate = () => {
      // Calculate FPS
      const currentTime = performance.now();
      const deltaTime = currentTime - lastTime;
      lastTime = currentTime;
      
      frameTimeSum += deltaTime;
      frameTimeCount++;
      
      // Update FPS every 60 frames
      if (frameCount % CONFIG.performance.fpsCheckInterval === 0 && frameTimeCount > 0) {
        const avgFrameTime = frameTimeSum / frameTimeCount;
        currentFPS = Math.round(1000 / avgFrameTime);
        frameTimeSum = 0;
        frameTimeCount = 0;
        
        // Check performance and potentially activate core mode
        axionSystem.checkPerformance(currentFPS);
      }
      
      if (zoomPhase) {
        renderer.renderZoomPhase(soulSystem.centerSoul, zoomFrame);
        
        // Animate packet during zoom phase too
        packetSystem.updateAcceleration();
        packetSystem.packet.trail.push({ x: packetSystem.packet.x, y: packetSystem.packet.y });
        if (packetSystem.packet.trail.length > CONFIG.packet.trailLength) {
          packetSystem.packet.trail.shift();
        }
        packetSystem.packet.x += packetSystem.packet.vx;
        packetSystem.packet.y += packetSystem.packet.vy;
        
        // Show packet in zoom phase
        renderer.renderPacket(packetSystem, true);
        
        zoomFrame++;
        if (zoomFrame >= CONFIG.zoom.maxFrames) {
          zoomPhase = false;
          // Make packet invisible after zoom
          packetSystem.packet.visible = false;
        }
      } else {
        renderer.renderMainPhase(soulSystem, packetSystem, waveSystem, sparkSystem, axionSystem, frameCount, false);
        soulSystem.update(frameCount, waveSystem, sparkSystem, axionSystem);
        packetSystem.update(soulSystem, waveSystem, frameCount, axionSystem);
        waveSystem.update();
        sparkSystem.update(waveSystem, axionSystem, soulSystem);
        axionSystem.updateActivationStatus(soulSystem);
        axionSystem.update(soulSystem, frameCount);
      }
      
      frameCount++;
      
      if (frameCount % 10 === 0) {
        setStats({
          souls: soulSystem.getActiveSoulCount(),
          sparks: sparkSystem.sparks.length,
          frame: frameCount,
          axions: axionSystem.connections.length,
          traces: axionSystem.pathTraces.size,
          axionsEnabled: axionSystem.enabled,
          fps: currentFPS,
          coreMode: axionSystem.coreMode
        });
      }
      
      animationId = requestAnimationFrame(animate);
    };
    
    let animationId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationId);
  }, []);
  
  return (
    <div style={{ 
      width: '100%',
      height: '100vh',
      background: 'black',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative',
      overflow: 'hidden'
    }}>
      <canvas 
        ref={canvasRef} 
        style={{ 
          maxWidth: '100%',
          maxHeight: '100%',
          imageRendering: 'crisp-edges'
        }}
      />
      
      <div style={{
        position: 'absolute',
        bottom: 20,
        left: 20,
        color: 'rgba(255, 255, 255, 0.6)',
        fontSize: '13px',
        fontFamily: 'monospace',
        background: 'rgba(0, 0, 0, 0.5)',
        padding: '10px',
        borderRadius: '4px'
      }}>
        <div>Active Souls: {stats.souls}</div>
        <div>Sparks: {stats.sparks}</div>
        <div style={{ color: stats.fps < 30 ? 'rgba(255, 150, 100, 0.9)' : 'rgba(255, 255, 255, 0.6)' }}>
          FPS: {stats.fps}
        </div>
        {stats.axionsEnabled && (
          <>
            <div style={{ color: 'rgba(150, 200, 255, 0.7)', marginTop: 4, fontSize: '11px' }}>
              Traces: {stats.traces}
            </div>
            {stats.axions > 0 && (
              <div style={{ color: 'rgba(100, 255, 150, 0.95)', fontWeight: 'bold' }}>
                ⚡ Pathways: {stats.axions}
              </div>
            )}
          </>
        )}
        {stats.coreMode && (
          <div style={{ 
            marginTop: 4, 
            fontSize: '11px', 
            color: 'rgba(255, 200, 50, 0.95)',
            fontWeight: 'bold'
          }}>
            🧠 CORE MODE: Network focused
          </div>
        )}
        <div style={{ marginTop: 8, fontSize: '11px', opacity: 0.6 }}>
          Recursive: 9 sub-souls × 9 pixels = 81
        </div>
        {!stats.axionsEnabled && stats.souls > 0 && (
          <div style={{ marginTop: 4, fontSize: '11px', opacity: 0.5 }}>
            Progress: {Math.round((stats.souls / (200 * 0.6)) * 100)}% → Axions at 100%
          </div>
        )}
        {stats.axionsEnabled && stats.traces > 0 && stats.axions === 0 && (
          <div style={{ marginTop: 4, fontSize: '11px', color: 'rgba(255, 200, 100, 0.8)' }}>
            Building neural traces...
          </div>
        )}
        {stats.axionsEnabled && stats.axions > 0 && !stats.coreMode && (
          <div style={{ marginTop: 4, fontSize: '10px', color: 'rgba(100, 255, 150, 0.6)' }}>
            Neural network active
          </div>
        )}
      </div>
      
      <a 
        href="https://github.com/AshmanRoonz/Fractal_Reality"
        target="_blank"
        rel="noopener noreferrer"
        style={{
          position: 'absolute',
          top: 20,
          right: 20,
          color: 'rgba(255, 255, 255, 0.4)',
          fontSize: '12px',
          fontFamily: 'monospace',
          textDecoration: 'none',
          padding: '8px 12px',
          background: 'rgba(0, 0, 0, 0.4)',
          borderRadius: '4px',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          transition: 'all 0.3s ease'
        }}
        onMouseEnter={(e) => {
          e.target.style.color = 'rgba(255, 255, 255, 0.8)';
          e.target.style.borderColor = 'rgba(255, 255, 255, 0.3)';
        }}
        onMouseLeave={(e) => {
          e.target.style.color = 'rgba(255, 255, 255, 0.4)';
          e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)';
        }}
      >
        github.com/AshmanRoonz/Fractal_Reality
      </a>
    </div>
  );
};

export default FractalSoulArray;
