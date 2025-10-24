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
  
  neuroplasticity: {
    pathwayPersistence: 1800,     // Frames a pathway persists without reinforcement (60 seconds at 30fps - 2x longer!)
    usageStrengthening: 0.15,     // How much strength gained when lightning travels near
    maxPathwayStrength: 3.0,      // Maximum strength a pathway can reach (3x stronger than new)
    decayRate: 0.9996,            // Even slower decay - pathways last much longer
    reactivationBonus: 0.5,       // Bonus strength when reusing a faded pathway
    proximityRadius: 60,          // Distance within which lightning strengthens a pathway
    routingPreference: 5.0,       // Strong preference multiplier for using established pathways
    minMaintenanceStrength: 0.15, // Minimum strength to keep pathway visible
    colorInfluenceRadius: 80,     // Distance within which pathways affect soul colors
    colorInfluenceStrength: 0.25, // How much pathways shift soul colors (0-1)
  },
  
  performance: {
    fpsThreshold: 30,             // FPS below this triggers core mode
    fpsCheckInterval: 60,         // Check FPS every N frames
    coreModeSparkReduction: 1.5,  // INCREASE spark emission by 50% in core mode (pathways = efficiency)
    coreModePathwayLimit: 10000,  // No real limit - more pathways = better
  }
};

// ============================================================================
// COLOR RESONANCE SYSTEM - Each soul has a unique color identity
// ============================================================================
class ColorResonance {
  // Generate a unique color signature for a soul based on its cosmic position
  static generateSoulSignature(x, y, width, height) {
    // Normalize position to 0-1
    const normX = x / width;
    const normY = y / height;
    
    // Distance from center influences base color
    const centerX = 0.5;
    const centerY = 0.5;
    const distFromCenter = Math.hypot(normX - centerX, normY - centerY);
    
    // Angle from center determines color family
    const angle = Math.atan2(normY - centerY, normX - centerX);
    const angleHue = ((angle + Math.PI) / (Math.PI * 2)) * 360;
    
    // Create a unique harmonic signature
    const harmonic1 = Math.sin(normX * Math.PI * 3.7) * 0.5 + 0.5;
    const harmonic2 = Math.cos(normY * Math.PI * 4.3) * 0.5 + 0.5;
    const harmonic3 = Math.sin((normX + normY) * Math.PI * 2.1) * 0.5 + 0.5;
    
    // Primary hue based on position and harmonics
    const primaryHue = (angleHue + harmonic1 * 60 + distFromCenter * 120) % 360;
    
    // Secondary and tertiary hues for triadic harmony
    const secondaryHue = (primaryHue + 120 + harmonic2 * 40) % 360;
    const tertiaryHue = (primaryHue + 240 + harmonic3 * 40) % 360;
    
    // Resonance signature - unique pattern of frequencies
    const resonancePattern = [
      harmonic1,
      harmonic2,
      harmonic3,
      Math.sin(normX * normY * Math.PI * 5) * 0.5 + 0.5,
      Math.cos(distFromCenter * Math.PI * 3) * 0.5 + 0.5
    ];
    
    return {
      primaryHue,
      secondaryHue,
      tertiaryHue,
      resonancePattern,
      distFromCenter,
      angle,
      harmonic1,
      harmonic2,
      harmonic3
    };
  }
  
  // Generate sub-soul colors based on parent signature and position in grid
  static generateSubSoulColors(parentSig, ix, iy) {
    // Position in 3x3 grid (0-2 for each)
    const normIx = ix / 2;
    const normIy = iy / 2;
    
    // Each sub-soul position has a unique role in the parent's pattern
    const subSoulAngle = Math.atan2(iy - 1, ix - 1);
    const subSoulDist = Math.hypot(ix - 1, iy - 1) / Math.sqrt(2);
    
    // Mix parent hues based on position
    let baseHue;
    if (subSoulDist < 0.3) {
      // Center: pure primary
      baseHue = parentSig.primaryHue;
    } else if (ix === 1 || iy === 1) {
      // Cross pattern: blend primary and secondary
      baseHue = (parentSig.primaryHue * 0.7 + parentSig.secondaryHue * 0.3) % 360;
    } else {
      // Corners: use triadic colors
      const corner = ix + iy * 3;
      if (corner % 3 === 0) baseHue = parentSig.primaryHue;
      else if (corner % 3 === 1) baseHue = parentSig.secondaryHue;
      else baseHue = parentSig.tertiaryHue;
    }
    
    // Add position-based variation
    const positionShift = (subSoulAngle / Math.PI) * 30 + parentSig.resonancePattern[ix + iy] * 20;
    baseHue = (baseHue + positionShift) % 360;
    
    // Create sub-soul specific resonance
    const subResonance = parentSig.resonancePattern.map((val, i) => {
      return (val + Math.sin((ix + iy + i) * Math.PI * 0.5) * 0.3) % 1;
    });
    
    return {
      baseHue,
      subResonance,
      subSoulAngle,
      subSoulDist
    };
  }
  
  // Generate pixel colors based on sub-soul and pixel position
  static generatePixelColor(subSoulColors, parentSig, px, py, role) {
    const dx = px - 1; // -1, 0, 1
    const dy = py - 1;
    const pixelAngle = Math.atan2(dy, dx);
    const pixelDist = Math.hypot(dx, dy) / Math.sqrt(2);
    
    let hue = subSoulColors.baseHue;
    let saturation = 0.6;
    
    // Role-based color variation
    if (role === 'core') {
      // Core: brightest, most saturated, true to parent color
      saturation = 0.8;
      hue = subSoulColors.baseHue;
    } else if (role === 'inner') {
      // Inner: blend with secondary hue
      const blend = (pixelAngle + Math.PI) / (Math.PI * 2);
      hue = (subSoulColors.baseHue * (1 - blend * 0.3) + parentSig.secondaryHue * blend * 0.3) % 360;
      saturation = 0.65;
    } else {
      // Outer: use triadic harmony, influenced by angle
      const angleSegment = Math.floor(((pixelAngle + Math.PI) / (Math.PI * 2)) * 3);
      if (angleSegment === 0) hue = parentSig.primaryHue;
      else if (angleSegment === 1) hue = parentSig.secondaryHue;
      else hue = parentSig.tertiaryHue;
      
      // Add pixel-specific resonance
      hue = (hue + subSoulColors.subResonance[(px + py) % 5] * 25) % 360;
      saturation = 0.5 + pixelDist * 0.2;
    }
    
    return { hue, saturation };
  }
  
  // Update colors based on activation and life experience
  static evolveColors(pixel, soul, subSoul, frameCount, waveInfluence) {
    // Colors shift subtly based on activation history
    const activationInfluence = subSoul.activation * 15;
    const lifeInfluence = (frameCount - soul.activationTime) * 0.001;
    
    // Wave interference creates temporary color shifts
    let hueShift = activationInfluence + lifeInfluence;
    if (waveInfluence) {
      hueShift += (waveInfluence.hue - pixel.h) * waveInfluence.strength * 0.3;
    }
    
    pixel.h = (pixel.baseHue + hueShift) % 360;
    
    // Saturation pulses with activation
    const satPulse = Math.sin(frameCount * 0.05) * 0.1;
    pixel.s = Math.min(0.9, pixel.baseSaturation + subSoul.activation * 0.2 + satPulse);
  }
}

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
    this.sparkBonds = []; // Bonds between resonant sparks
  }
  
  // Create a braided/woven path between two spark points
  createBraidedSparkPath(point1, point2, hue1, hue2) {
    const dx = point2.x - point1.x;
    const dy = point2.y - point1.y;
    const dist = Math.hypot(dx, dy);
    const angle = Math.atan2(dy, dx);
    
    const numStrands = 3; // Three strands braiding together
    const segments = [];
    const steps = Math.floor(dist / 5) + 3;
    
    for (let strand = 0; strand < numStrands; strand++) {
      const strandSegments = [];
      const phaseOffset = (strand / numStrands) * Math.PI * 2;
      
      for (let i = 0; i <= steps; i++) {
        const t = i / steps;
        
        // Base position along line
        const baseX = point1.x + dx * t;
        const baseY = point1.y + dy * t;
        
        // Braiding wave pattern - smooth taper
        const braidAmplitude = 8 * Math.sin(t * Math.PI);
        const braidFreq = 6;
        const braidPhase = Math.sin(t * Math.PI * braidFreq + phaseOffset) * braidAmplitude;
        
        // Secondary harmonic for richness
        const harmonic = Math.sin(t * Math.PI * 4 + phaseOffset * 1.5) * 3;
        
        // Perpendicular offset
        const perpX = -Math.sin(angle) * (braidPhase + harmonic);
        const perpY = Math.cos(angle) * (braidPhase + harmonic);
        
        strandSegments.push({
          x: baseX + perpX,
          y: baseY + perpY
        });
      }
      
      segments.push(strandSegments);
    }
    
    return segments;
  }
  
  // Calculate resonance between two sparks
  calculateSparkResonance(spark1, spark2) {
    // Distance between sparks (use midpoints)
    const mid1 = spark1.segments[Math.floor(spark1.segments.length / 2)];
    const mid2 = spark2.segments[Math.floor(spark2.segments.length / 2)];
    const dist = Math.hypot(mid2.x - mid1.x, mid2.y - mid1.y);
    
    // Only resonate if close enough
    if (dist > 100) return 0;
    
    // Color similarity - sparks with similar hues resonate
    const hueDiff = Math.min(
      Math.abs(spark1.hue - spark2.hue),
      360 - Math.abs(spark1.hue - spark2.hue)
    );
    const colorMatch = 1 - (hueDiff / 60); // Within 60° is good
    
    // Also check for complementary colors (opposite on color wheel)
    const isComplementary = Math.abs(hueDiff - 180) < 30;
    const colorResonance = isComplementary ? 0.9 : Math.max(0, colorMatch);
    
    // Age/phase alignment - sparks at similar life stages resonate
    const ageDiff = Math.abs(spark1.age - spark2.age);
    const ageMatch = 1 - Math.min(1, ageDiff / 15);
    
    // Lifetime phase - sparks in similar phases of their life cycle resonate more
    const phase1 = spark1.age / spark1.maxAge;
    const phase2 = spark2.age / spark2.maxAge;
    const phaseDiff = Math.abs(phase1 - phase2);
    const phaseMatch = 1 - phaseDiff;
    
    // Shape similarity - compare branch patterns
    const branch1Count = spark1.branches.length;
    const branch2Count = spark2.branches.length;
    const branchMatch = 1 - Math.min(1, Math.abs(branch1Count - branch2Count) / 5);
    
    // Combined resonance with distance falloff
    const distFactor = 1 - (dist / 100);
    const resonance = (
      colorResonance * 0.45 + 
      ageMatch * 0.20 + 
      phaseMatch * 0.20 + 
      branchMatch * 0.15
    ) * distFactor;
    
    return Math.max(0, resonance);
  }
  
  // Find and create bonds between resonant sparks
  updateSparkBonds() {
    this.sparkBonds = [];
    
    // Check all pairs of sparks
    for (let i = 0; i < this.sparks.length; i++) {
      for (let j = i + 1; j < this.sparks.length; j++) {
        const spark1 = this.sparks[i];
        const spark2 = this.sparks[j];
        
        const resonance = this.calculateSparkResonance(spark1, spark2);
        
        // Form bond if resonance is strong enough (lowered threshold for more connections)
        if (resonance > 0.4) {
          // Find closest points between the sparks
          let minDist = Infinity;
          let point1 = null;
          let point2 = null;
          
          for (const seg1 of spark1.segments) {
            for (const seg2 of spark2.segments) {
              const d = Math.hypot(seg2.x - seg1.x, seg2.y - seg1.y);
              if (d < minDist) {
                minDist = d;
                point1 = seg1;
                point2 = seg2;
              }
            }
          }
          
          if (point1 && point2 && minDist < 100) {
            // Blend hues for bond color - weighted by spark alpha
            const totalAlpha = spark1.alpha + spark2.alpha;
            let avgHue;
            
            // Ensure valid hue values
            if (!isFinite(spark1.hue) || !isFinite(spark2.hue) || totalAlpha === 0) {
              avgHue = 180; // Default to cyan if invalid
            } else {
              avgHue = (spark1.hue * spark1.alpha + spark2.hue * spark2.alpha) / totalAlpha;
            }
            
            // Ensure hue is in valid range
            avgHue = Math.max(0, Math.min(360, avgHue));
            
            // Calculate bond brightness based on resonance strength
            const bondAlpha = Math.min(spark1.alpha, spark2.alpha) * Math.pow(resonance, 0.7);
            
            // Create braided pathway between sparks
            const braidSegments = this.createBraidedSparkPath(point1, point2, spark1.hue, spark2.hue);
            
            this.sparkBonds.push({
              point1,
              point2,
              braidSegments,
              strength: resonance,
              hue: avgHue,
              alpha: bondAlpha,
              spark1,
              spark2,
              distance: minDist
            });
          }
        }
      }
    }
  }
  
  // Calculate harmonic resonance between two souls
  calculateResonance(soul1, soul2) {
    // HARMONIC COMMUNICATION: Sparks seek souls that resonate harmonically
    // - Similar frequencies (like tuning forks)
    // - Phase alignment (synchronized oscillation)
    // - Color harmony (triadic/complementary relationships)
    // - Spatial proximity (distance matters)
    
    // Frequency matching - souls with similar frequencies resonate
    const freqDiff = Math.abs(soul1.frequency - soul2.frequency);
    const freqMatch = 1 - Math.min(1, freqDiff / 0.03); // 0.03 is max frequency range
    
    // Phase alignment - souls in phase resonate more
    const phaseDiff = Math.abs(Math.sin(soul1.phase - soul2.phase));
    const phaseMatch = 1 - phaseDiff;
    
    // Color harmony - souls with harmonic color relationships resonate
    const hue1 = soul1.colorSignature.primaryHue;
    const hue2 = soul2.colorSignature.primaryHue;
    const hueDiff = Math.min(
      Math.abs(hue1 - hue2),
      360 - Math.abs(hue1 - hue2)
    );
    // Triadic (120°), complementary (180°), or similar (0°) colors resonate
    const isTriadic = Math.abs(hueDiff - 120) < 30 || Math.abs(hueDiff - 240) < 30;
    const isComplementary = Math.abs(hueDiff - 180) < 30;
    const isSimilar = hueDiff < 30;
    const colorMatch = isTriadic ? 1.0 : (isComplementary ? 0.8 : (isSimilar ? 0.9 : 0.3));
    
    // Distance factor - closer souls have stronger potential
    const dist = Math.hypot(soul2.x - soul1.x, soul2.y - soul1.y);
    const distFactor = Math.max(0, 1 - dist / 200); // Max range 200px
    
    // Combined resonance score
    return (
      freqMatch * CONFIG.resonance.frequencyWeight +
      phaseMatch * CONFIG.resonance.phaseWeight +
      colorMatch * 0.3 // Color harmony weight
    ) * distFactor * soul2.activationLevel; // Only seek active souls
  }
  
  // Find the most harmonically resonant target for a spark
  findResonantTarget(originSoul, soulSystem) {
    let bestTarget = null;
    let bestResonance = 0.3; // Minimum threshold
    
    for (const soul of soulSystem.souls) {
      if (soul === originSoul || !soul.activated) continue;
      
      const resonance = this.calculateResonance(originSoul, soul);
      if (resonance > bestResonance) {
        bestResonance = resonance;
        bestTarget = soul;
      }
    }
    
    return bestTarget;
  }
  
  emitFromSoul(soul, soulSystem) {
    // Find harmonically resonant target
    const targetSoul = this.findResonantTarget(soul, soulSystem);
    if (!targetSoul) return; // No resonant target found
    
    // Sparks follow recursive pattern - emit from active sub-souls!
    // Find the most active sub-souls
    const activeSubSouls = soul.subSouls
      .filter(ss => ss.activation > 0.3)
      .sort((a, b) => b.activation - a.activation);
    
    if (activeSubSouls.length === 0) return;
    
    // Emit from top 2-4 active sub-souls toward the resonant target
    const numSparks = Math.min(activeSubSouls.length, 2 + Math.floor(Math.random() * 3));
    
    for (let i = 0; i < numSparks; i++) {
      const subSoul = activeSubSouls[i];
      
      // Calculate angle toward resonant target
      const dx = targetSoul.x - subSoul.x;
      const dy = targetSoul.y - subSoul.y;
      let angle = Math.atan2(dy, dx);
      
      // Add some variation so not all sparks follow exact same path
      angle += (Math.random() - 0.5) * 0.6;
      
      // Emit from sub-soul position toward target
      this.createFractalSpark(subSoul.x, subSoul.y, angle, subSoul.hue, 0, soul, subSoul, targetSoul);
    }
  }
  
  
  createFractalSpark(x, y, angle, baseHue, depth, soul, subSoul = null, targetSoul = null) {
    // Length influenced by subSoul's activation if available, else soul's
    const lengthFactor = subSoul ? subSoul.activation : (soul ? soul.activationLevel : 1.0);
    
    // If we have a target, aim toward it and adjust length based on distance
    let targetDistance = CONFIG.sparks.maxRange;
    if (targetSoul) {
      targetDistance = Math.hypot(targetSoul.x - x, targetSoul.y - y);
      targetDistance = Math.min(targetDistance * 0.8, CONFIG.sparks.maxRange); // 80% of distance
    }
    
    const length = targetDistance * (0.3 + Math.random() * 0.3) * lengthFactor * Math.pow(0.7, depth);
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
    
    // Ensure hue is valid
    const sparkHue = isFinite(baseHue) ? 
      (baseHue + (Math.random() - 0.5) * 40) % 360 : 
      Math.random() * 360;
    
    this.sparks.push({
      segments,
      branches,
      hue: sparkHue,
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
    
    // Update bonds between resonant sparks
    this.updateSparkBonds();
    
    // Emit waves from strong spark bonds to show their interaction
    for (const bond of this.sparkBonds) {
      if (bond.strength > 0.7 && Math.random() < 0.15) {
        // Emit wave at the midpoint of the bond
        const midX = (bond.point1.x + bond.point2.x) / 2;
        const midY = (bond.point1.y + bond.point2.y) / 2;
        waveSystem.emitWake(midX, midY, CONFIG.sparks.waveStrength * bond.strength * 0.6, bond.hue);
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
    // Activate core mode when we have a strong network (efficiency mode)
    if (this.connections.length > 300) {
      this.coreMode = true;  // Network is strong - use it!
    } else if (this.connections.length < 150) {
      this.coreMode = false; // Network too weak - explore freely
    }
    // FPS is irrelevant - pathways ARE the optimization
  }
  
  isSoulConnected(soul, soulSystem) {
    // Check if this soul is part of the axion network
    if (!this.coreMode) return true; // In normal mode, all souls can be active
    
    const soulIdx = soulSystem.souls.indexOf(soul);
    return this.connectedSouls.has(soulIdx);
  }
  
  recordSparkPath(spark, soulSystem) {
    // PATHWAY FORMATION: When sparks repeatedly travel between the same souls,
    // they "carve" neural pathways that become permanent communication routes.
    // The more sparks travel a path, the stronger and more visible it becomes.
    // This creates an efficient network where harmonic connections strengthen over time.
    
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
    
    // In network mode, focus on strongest pathways
    const maxPathways = this.coreMode ? CONFIG.performance.coreModePathwayLimit : 10000;
    
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
    this.lightningPathways = []; // Braided pathways formed by connected bolts
    this.pathwayConnections = []; // Active connections between nearby bolts
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
  
  findNextTarget(soulSystem, axionSystem = null, isEmergency = false) {
    let bestSoul = null;
    let bestScore = -Infinity;
    
    // ANTI-STUCK: Track how many times we've failed to find a target
    if (!this.packet.stuckCounter) this.packet.stuckCounter = 0;
    if (!this.packet.lastPositions) this.packet.lastPositions = [];
    
    // Emergency mode: if we haven't moved much in the last 10 frames, we're stuck
    this.packet.lastPositions.push({ x: this.packet.x, y: this.packet.y, frame: this.packet.frameCount });
    if (this.packet.lastPositions.length > 10) {
      this.packet.lastPositions.shift();
      
      // Check if we've barely moved
      const firstPos = this.packet.lastPositions[0];
      const lastPos = this.packet.lastPositions[this.packet.lastPositions.length - 1];
      const totalMovement = Math.hypot(lastPos.x - firstPos.x, lastPos.y - firstPos.y);
      
      if (totalMovement < 20 && !isEmergency) {
        // We're stuck! Force emergency mode
        isEmergency = true;
        this.packet.stuckCounter++;
      }
    }
    
    // Expand search radius if stuck or in emergency mode
    const searchRadius = isEmergency ? CONFIG.packet.jumpDistance * 2 : CONFIG.packet.jumpDistance;
    
    // Disable recency penalty if in emergency mode
    const useRecencyPenalty = !isEmergency;
    
    for (const soul of soulSystem.souls) {
      const dist = Math.hypot(soul.x - this.packet.x, soul.y - this.packet.y);
      if (dist > searchRadius) continue;
      if (dist < 5) continue;
      
      // Skip if this was the last target (avoid ping-pong) - but not in emergency mode
      if (!isEmergency && soul === this.packet.targetSoul) continue;
      
      // NEUROPLASTICITY: Check for established pathways to this soul
      // ONLY after axions are enabled (60% threshold)
      // Reduce pathway influence if we're stuck
      let pathwayBonus = 0;
      let strongestPathway = null;
      
      if (axionSystem && axionSystem.enabled && !isEmergency) {
        // Check all persistent pathways to see if any lead to this soul
        for (const pathway of this.lightningPathways) {
          // Check if pathway connects to this soul's region
          const distToPathway = this.getDistanceToPathway(pathway, soul);
          if (distToPathway < CONFIG.neuroplasticity.proximityRadius) {
            // Found a pathway near this soul - give bonus based on pathway strength
            const pathwayStrength = pathway.strength * pathway.usageCount;
            const proximityFactor = 1 - (distToPathway / CONFIG.neuroplasticity.proximityRadius);
            const bonus = pathwayStrength * proximityFactor * CONFIG.neuroplasticity.routingPreference;
            
            if (bonus > pathwayBonus) {
              pathwayBonus = bonus;
              strongestPathway = pathway;
            }
          }
        }
      }
      
      // Axion connections also provide routing bonus (reduced in emergency)
      let connectionBonus = 0;
      if (axionSystem && axionSystem.enabled) {
        const isConnected = axionSystem.isSoulConnected(soul, soulSystem);
        if (isConnected) {
          connectionBonus = isEmergency ? 1.0 : 2.0; // Reduced in emergency
        }
      }
      
      // Calculate resonance score with gravity-like attraction
      const freqDiff = Math.abs(soul.frequency - this.packet.frequency);
      const freqScore = (1 - freqDiff / 0.03) * CONFIG.resonance.frequencyWeight;
      
      const phaseDiff = Math.abs(soul.phase - this.packet.phase);
      const normalizedPhaseDiff = Math.min(phaseDiff, Math.PI * 2 - phaseDiff) / Math.PI;
      const phaseScore = (1 - normalizedPhaseDiff) * CONFIG.resonance.phaseWeight;
      
      // Stronger distance attraction
      const distScore = (1 - dist / searchRadius) * CONFIG.resonance.distanceWeight;
      
      // In emergency mode, STRONGLY prefer unactivated souls
      const activationBonus = soul.activated ? 0.05 : (isEmergency ? 1.0 : 0.4);
      
      // Penalize recently hit souls (disabled in emergency)
      const timeSinceHit = this.packet.frameCount - (soul.lastHitTime || 0);
      const recencyPenalty = (useRecencyPenalty && timeSinceHit < 50) ? -0.3 : 0;
      
      const totalScore = freqScore + phaseScore + distScore + activationBonus + recencyPenalty + connectionBonus + pathwayBonus + Math.random() * 0.3;
      
      if (totalScore > bestScore) {
        bestScore = totalScore;
        bestSoul = soul;
      }
    }
    
    // ANTI-STUCK FAILSAFE 1: If still no target, find ANY unactivated soul anywhere
    if (!bestSoul) {
      const unactivatedSouls = soulSystem.souls.filter(s => !s.activated);
      if (unactivatedSouls.length > 0) {
        bestSoul = unactivatedSouls[Math.floor(Math.random() * unactivatedSouls.length)];
        this.packet.stuckCounter++;
      }
    }
    
    // ANTI-STUCK FAILSAFE 2: If ALL souls activated, pick any random soul far away
    if (!bestSoul) {
      const farSouls = soulSystem.souls.filter(s => {
        const dist = Math.hypot(s.x - this.packet.x, s.y - this.packet.y);
        return dist > 100; // Must be far away
      });
      if (farSouls.length > 0) {
        bestSoul = farSouls[Math.floor(Math.random() * farSouls.length)];
        this.packet.stuckCounter++;
      }
    }
    
    // ANTI-STUCK FAILSAFE 3: Last resort - pick any random soul
    if (!bestSoul && soulSystem.souls.length > 0) {
      bestSoul = soulSystem.souls[Math.floor(Math.random() * soulSystem.souls.length)];
      this.packet.stuckCounter++;
    }
    
    // Reset stuck counter if we found a good target
    if (bestSoul && bestScore > 0) {
      this.packet.stuckCounter = 0;
    }
    
    return bestSoul;
  }
  
  // Helper function to calculate distance from a point to a pathway
  getDistanceToPathway(pathway, soul) {
    let minDist = Infinity;
    
    // Check distance to main pathway segments
    if (pathway.braidSegments && pathway.braidSegments.length > 0) {
      for (const strand of pathway.braidSegments) {
        for (const segment of strand) {
          const dist = Math.hypot(segment.x - soul.x, segment.y - soul.y);
          minDist = Math.min(minDist, dist);
        }
      }
    }
    
    return minDist;
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
    
    // ANTI-STUCK: Check if stuck counter is too high and force reset
    if (this.packet.stuckCounter > 5) {
      // We've been stuck for too long - emergency reset!
      const unactivatedSouls = soulSystem.souls.filter(s => !s.activated);
      const targetSoul = unactivatedSouls.length > 0 
        ? unactivatedSouls[Math.floor(Math.random() * unactivatedSouls.length)]
        : soulSystem.souls[Math.floor(Math.random() * soulSystem.souls.length)];
      
      if (targetSoul) {
        // Teleport to new location
        this.packet.x = targetSoul.x + (Math.random() - 0.5) * 50;
        this.packet.y = targetSoul.y + (Math.random() - 0.5) * 50;
        this.packet.targetSoul = targetSoul;
        this.packet.targetX = targetSoul.x;
        this.packet.targetY = targetSoul.y;
        this.packet.vx = 0;
        this.packet.vy = 0;
        this.packet.trail = [];
        this.packet.stuckCounter = 0;
        this.packet.lastPositions = [];
        this.packet.mode = 'traveling';
        
        // Visual feedback for teleport
        waveSystem.emitBurst(this.packet.x, this.packet.y, 2.5, this.packet.hue);
        this.createLightningBolt(this.packet.x, this.packet.y, targetSoul.x, targetSoul.y);
      }
    }
    
    // Update persistent lightning bolts
    for (let i = this.lightningBolts.length - 1; i >= 0; i--) {
      const bolt = this.lightningBolts[i];
      bolt.age++;
      bolt.alpha = 1.0 - (bolt.age / (CONFIG.packet.lightningFadeFrames * 3)); // Last 3x longer
      
      if (bolt.alpha <= 0) {
        this.lightningBolts.splice(i, 1);
      }
    }
    
    // Find and create connections between nearby lightning bolts
    this.updateLightningConnections(axionSystem);
    
    // Update pathways (strengthen or fade)
    this.updatePathways(axionSystem);
    
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
      
      // ANTI-STUCK: If speed is too low, give it a random boost
      if (this.packet.speed < 1 && Math.random() < 0.1) {
        const randomAngle = Math.random() * Math.PI * 2;
        this.packet.vx += Math.cos(randomAngle) * 2;
        this.packet.vy += Math.sin(randomAngle) * 2;
      }
      
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
        } else {
          // EMERGENCY: No target found! This should never happen with our failsafes,
          // but if it does, teleport to a random location
          const randomSoul = soulSystem.souls[Math.floor(Math.random() * soulSystem.souls.length)];
          if (randomSoul) {
            this.packet.x = randomSoul.x;
            this.packet.y = randomSoul.y;
            this.packet.targetSoul = randomSoul;
            this.packet.targetX = randomSoul.x;
            this.packet.targetY = randomSoul.y;
            this.packet.vx = 0;
            this.packet.vy = 0;
            this.packet.trail = [];
            this.packet.stuckCounter = 0;
            this.packet.lastPositions = [];
            
            // Emit burst to show teleport
            waveSystem.emitBurst(randomSoul.x, randomSoul.y, 2.0, this.packet.hue);
          }
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
  
  // Find and create connections between nearby lightning bolts
  // ONLY after axions are enabled (60% threshold reached)
  updateLightningConnections(axionSystem = null) {
    this.pathwayConnections = [];
    
    // CRITICAL: Only form pathways after 60% of souls are activated
    if (!axionSystem || !axionSystem.enabled) {
      return; // No braiding until axions activate!
    }
    
    // Check all pairs of lightning bolts
    for (let i = 0; i < this.lightningBolts.length; i++) {
      for (let j = i + 1; j < this.lightningBolts.length; j++) {
        const bolt1 = this.lightningBolts[i];
        const bolt2 = this.lightningBolts[j];
        
        // Find closest points between the two bolts
        let minDist = Infinity;
        let point1 = null;
        let point2 = null;
        let index1 = -1;
        let index2 = -1;
        
        for (let s1 = 0; s1 < bolt1.segments.length; s1++) {
          for (let s2 = 0; s2 < bolt2.segments.length; s2++) {
            const seg1 = bolt1.segments[s1];
            const seg2 = bolt2.segments[s2];
            const dist = Math.hypot(seg2.x - seg1.x, seg2.y - seg1.y);
            
            if (dist < minDist) {
              minDist = dist;
              point1 = seg1;
              point2 = seg2;
              index1 = s1;
              index2 = s2;
            }
          }
        }
        
        // If bolts are close enough, create a connection
        if (minDist < 150 && point1 && point2) {
          // Create a braided pathway between them
          const braidSegments = this.createBraidedPath(point1, point2, bolt1.hue, bolt2.hue);
          
          // Calculate connection strength based on bolt ages and distance
          const ageStrength = Math.min(bolt1.alpha, bolt2.alpha);
          const distStrength = 1 - (minDist / 150);
          const strength = ageStrength * distStrength;
          
          this.pathwayConnections.push({
            bolt1,
            bolt2,
            point1,
            point2,
            braidSegments,
            strength,
            age: 0,
            hue: (bolt1.hue + bolt2.hue) / 2
          });
          
          // Add to persistent pathways if strong enough
          if (strength > 0.6) {
            this.strengthenPathway(bolt1, bolt2, braidSegments, point1, point2);
          }
        }
      }
    }
  }
  
  // Create a braided/woven path between two points
  createBraidedPath(point1, point2, hue1, hue2) {
    const dx = point2.x - point1.x;
    const dy = point2.y - point1.y;
    const dist = Math.hypot(dx, dy);
    const angle = Math.atan2(dy, dx);
    
    const numStrands = 3; // Three strands for richer braiding
    const segments = [];
    const steps = Math.floor(dist / 6) + 3; // More segments for smoother curves
    
    for (let strand = 0; strand < numStrands; strand++) {
      const strandSegments = [];
      const phaseOffset = (strand / numStrands) * Math.PI * 2;
      
      for (let i = 0; i <= steps; i++) {
        const t = i / steps;
        
        // Base position along line
        const baseX = point1.x + dx * t;
        const baseY = point1.y + dy * t;
        
        // Enhanced braiding wave pattern
        const braidAmplitude = 12 * Math.sin(t * Math.PI); // Smooth taper using sine
        const braidFreq = 5; // More oscillations
        const braidPhase = Math.sin(t * Math.PI * braidFreq + phaseOffset) * braidAmplitude;
        
        // Add secondary wave for more organic look
        const secondaryWave = Math.sin(t * Math.PI * 3 + phaseOffset * 1.5) * 4;
        
        // Perpendicular offset
        const perpX = -Math.sin(angle) * (braidPhase + secondaryWave);
        const perpY = Math.cos(angle) * (braidPhase + secondaryWave);
        
        strandSegments.push({
          x: baseX + perpX,
          y: baseY + perpY
        });
      }
      
      segments.push(strandSegments);
    }
    
    return segments;
  }
  
  // Strengthen or create persistent pathways
  strengthenPathway(bolt1, bolt2, braidSegments, point1, point2) {
    // Find if pathway already exists between these bolts
    let pathway = this.lightningPathways.find(p => 
      (p.bolt1 === bolt1 && p.bolt2 === bolt2) ||
      (p.bolt1 === bolt2 && p.bolt2 === bolt1)
    );
    
    if (pathway) {
      // NEUROPLASTICITY: Strengthen existing pathway with usage
      const previousStrength = pathway.strength;
      pathway.strength = Math.min(
        CONFIG.neuroplasticity.maxPathwayStrength, 
        pathway.strength + CONFIG.neuroplasticity.usageStrengthening
      );
      pathway.usageCount = (pathway.usageCount || 0) + 1;
      pathway.lastUsed = this.packet.frameCount;
      pathway.age = 0; // Reset age
      pathway.braidSegments = braidSegments; // Update shape
      
      // Reactivation bonus for pathways that were fading
      if (previousStrength < CONFIG.neuroplasticity.minMaintenanceStrength) {
        pathway.strength += CONFIG.neuroplasticity.reactivationBonus;
      }
    } else {
      // Create new pathway with neuroplastic properties
      this.lightningPathways.push({
        bolt1,
        bolt2,
        point1,
        point2,
        braidSegments,
        strength: 0.3,
        age: 0,
        hue: (bolt1.hue + bolt2.hue) / 2,
        persistent: true,
        usageCount: 1,              // Track how many times this pathway is used
        lastUsed: this.packet.frameCount,
        formed: this.packet.frameCount
      });
    }
  }
  
  // Update persistent pathways with neuroplasticity
  updatePathways(axionSystem = null) {
    // NEUROPLASTICITY: Only strengthen pathways after axions are enabled (60% threshold)
    if (axionSystem && axionSystem.enabled) {
      // Check if lightning is near any pathways and strengthen them
      for (const pathway of this.lightningPathways) {
        // Check distance from current packet position to pathway
        const distToPathway = this.getDistanceToPathwayFromPoint(pathway, this.packet.x, this.packet.y);
        
        if (distToPathway < CONFIG.neuroplasticity.proximityRadius) {
          // Lightning is traveling near this pathway - strengthen it!
          const proximityFactor = 1 - (distToPathway / CONFIG.neuroplasticity.proximityRadius);
          const reinforcement = CONFIG.neuroplasticity.usageStrengthening * proximityFactor;
          
          pathway.strength = Math.min(
            CONFIG.neuroplasticity.maxPathwayStrength,
            pathway.strength + reinforcement
          );
          pathway.lastUsed = this.packet.frameCount;
          pathway.usageCount = (pathway.usageCount || 0) + 0.1; // Partial usage count for proximity
        }
      }
    }
    
    // Now update each pathway's lifecycle
    for (let i = this.lightningPathways.length - 1; i >= 0; i--) {
      const pathway = this.lightningPathways[i];
      pathway.age++;
      
      // Check if connected bolts still exist
      const bolt1Exists = this.lightningBolts.includes(pathway.bolt1);
      const bolt2Exists = this.lightningBolts.includes(pathway.bolt2);
      
      // Calculate time since last use
      const timeSinceUse = this.packet.frameCount - (pathway.lastUsed || pathway.formed || 0);
      
      if (!bolt1Exists && !bolt2Exists) {
        // NEUROPLASTICITY: Bolts gone, but pathway persists based on usage
        // Pathways decay slowly (synaptic pruning) but persist for a long time
        pathway.strength *= CONFIG.neuroplasticity.decayRate;
        
        // Remove pathway if it's been unused for too long OR strength too low
        if (timeSinceUse > CONFIG.neuroplasticity.pathwayPersistence || 
            pathway.strength < CONFIG.neuroplasticity.minMaintenanceStrength) {
          this.lightningPathways.splice(i, 1);
        }
      } else if (!bolt1Exists || !bolt2Exists) {
        // One bolt gone - slower decay, pathways maintain longer
        pathway.strength *= 0.9985; // Even slower decay than before
        
        // Keep pathway alive longer if it's been used frequently
        const usageBonus = Math.min(pathway.usageCount || 1, 10) * 50;
        if (timeSinceUse > CONFIG.neuroplasticity.pathwayPersistence + usageBonus || 
            pathway.strength < CONFIG.neuroplasticity.minMaintenanceStrength) {
          this.lightningPathways.splice(i, 1);
        }
      } else {
        // Both bolts still exist - maintain strength very well
        // High usage pathways maintain strength better
        const usageFactor = Math.min(pathway.usageCount || 1, 20) / 20;
        const maintainRate = 0.985 + (usageFactor * 0.012); // Up to 0.997 for heavily used pathways
        pathway.strength = Math.max(0.4, pathway.strength * maintainRate); // Higher minimum maintenance
      }
    }
  }
  
  // Helper function to calculate distance from a point to a pathway
  getDistanceToPathwayFromPoint(pathway, x, y) {
    let minDist = Infinity;
    
    // Check distance to pathway segments
    if (pathway.braidSegments && pathway.braidSegments.length > 0) {
      for (const strand of pathway.braidSegments) {
        for (const segment of strand) {
          const dist = Math.hypot(segment.x - x, segment.y - y);
          minDist = Math.min(minDist, dist);
        }
      }
    }
    
    return minDist;
  }
}

// ============================================================================
// SOUL SYSTEM - Now with environment layer (12D)
// ============================================================================
class SoulSystem {
  constructor(width, height, spacing) {
    this.souls = [];
    this.centerSoul = null;
    this.width = width;
    this.height = height;
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
    // Generate unique color signature for this soul based on cosmic position
    const colorSig = ColorResonance.generateSoulSignature(x, y, this.width, this.height);
    
    // Create 3×3 grid of sub-souls (9 total) - RECURSIVE STRUCTURE
    const subSouls = [];
    for (let iy = 0; iy < 3; iy++) {
      for (let ix = 0; ix < 3; ix++) {
        subSouls.push(this.createSubSoul(x, y, ix, iy, colorSig));
      }
    }
    
    return {
      x, y,
      phase: Math.random() * Math.PI * 2,
      frequency: 0.01 + Math.random() * 0.02,
      colorSignature: colorSig,
      activated: false,
      activationLevel: 0,
      activationTime: 0,
      lastHitTime: -1000,
      lastSparkEmission: -1000,
      subSouls, // 9 sub-souls, each with 9 pixels = 81 total
    };
  }
  
  createSubSoul(baseX, baseY, ix, iy, parentColorSig) {
    // Each sub-soul is offset within the parent soul (3×3 grid)
    const spacing = CONFIG.souls.subSoulSpacing;
    const offset = spacing * (3 - 1) / 2;
    
    const x = baseX + ix * spacing - offset;
    const y = baseY + iy * spacing - offset;
    
    // Generate sub-soul colors based on parent signature and grid position
    const colors = ColorResonance.generateSubSoulColors(parentColorSig, ix, iy);
    
    return {
      x, y,
      ix, iy, // Grid position (0-2)
      phase: Math.random() * Math.PI * 2,
      frequency: 0.015 + Math.random() * 0.01,
      colors,
      hue: colors.baseHue, // Keep for spark system compatibility
      activation: 0,
      pixels: this.createPixelsForSubSoul(colors, parentColorSig) // 3×3 = 9 pixels
    };
  }
  
  createPixelsForSubSoul(subSoulColors, parentColorSig) {
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
        
        // Generate unique color for this pixel
        const pixelColor = ColorResonance.generatePixelColor(
          subSoulColors, 
          parentColorSig, 
          x, y, 
          role
        );
        
        pixels.push({
          x, y,
          h: pixelColor.hue,
          baseHue: pixelColor.hue, // Store original for evolution
          s: pixelColor.saturation,
          baseSaturation: pixelColor.saturation,
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
        
        // Pattern based on angles and role
        const phaseMatch = Math.cos(angle - pAngle + soul.phase);
        let baseBrightness = (0.3 + Math.random() * 0.4) * (0.5 + phaseMatch * 0.5);
        
        // Roles have different brightness characteristics
        if (pixel.role === 'core') {
          baseBrightness *= 1.2;
        } else if (pixel.role === 'outer') {
          baseBrightness *= 0.8;
        }
        
        pixel.b = baseBrightness;
        pixel.active = pixel.b > 0.1;
      }
    }
  }
  
  update(frameCount, waveSystem, sparkSystem, axionSystem = null, packetSystem = null) {
    for (const soul of this.souls) {
      this.updateSoul(soul, frameCount, waveSystem, sparkSystem, axionSystem, packetSystem);
    }
  }
  
  updateSoul(soul, frameCount, waveSystem, sparkSystem, axionSystem = null, packetSystem = null) {
    soul.phase += soul.frequency;
    if (soul.phase > Math.PI * 2) soul.phase -= Math.PI * 2;
    
    if (!soul.activated) return;
    
    // NEUROPLASTICITY: Calculate pathway color influence on this soul
    let pathwayInfluence = null;
    if (packetSystem && axionSystem && axionSystem.enabled) {
      pathwayInfluence = this.calculatePathwayInfluence(soul, packetSystem);
    }
    
    // Check if soul is charged up enough to emit sparks
    if (soul.activationLevel > CONFIG.sparks.emissionThreshold) {
      // In core mode, connected souls emit MORE sparks (efficiency!)
      const canEmit = !axionSystem || !axionSystem.coreMode || 
                      axionSystem.isSoulConnected(soul, this);
      
      if (canEmit) {
        const timeSinceLastSpark = frameCount - (soul.lastSparkEmission || 0);
        const emissionCooldown = axionSystem && axionSystem.coreMode 
          ? CONFIG.sparks.emissionCooldown / CONFIG.performance.coreModeSparkReduction  // Shorter cooldown = MORE sparks
          : CONFIG.sparks.emissionCooldown;
          
        if (timeSinceLastSpark > emissionCooldown) {
          sparkSystem.emitFromSoul(soul, this);
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
        
        // NEUROPLASTICITY: Apply pathway color influence
        // Pathways near this soul will shift its colors, creating visual memory
        if (pathwayInfluence && pathwayInfluence.strength > 0.05) {
          const pathInfluence = pathwayInfluence.strength * CONFIG.neuroplasticity.colorInfluenceStrength;
          // Blend pixel hue towards the pathway's hue
          pixel.h = (pixel.h * (1 - pathInfluence) + pathwayInfluence.hue * pathInfluence) % 360;
          // Also slightly increase saturation for pathway-influenced pixels
          pixel.s = Math.min(1.0, pixel.s + pathInfluence * 0.15);
        }
        
        // Evolve pixel colors based on life and activation
        ColorResonance.evolveColors(pixel, soul, subSoul, frameCount, interference);
        
        // Add hit boost
        baseBrightness = Math.min(1, baseBrightness + hitRecency * 0.3);
        
        // Smooth transition
        pixel.b = pixel.b * 0.9 + baseBrightness * 0.1;
        pixel.active = pixel.b > 0.05;
      }
      
      // Decay sub-soul activation
      subSoul.activation *= 0.98;
      
      // Clamp to reasonable range
      subSoul.activation = Math.min(1.0, subSoul.activation);
      
      // Waves can reactivate sub-souls
      if (waveBoost > 0.2) {
        subSoul.activation = Math.min(0.9, subSoul.activation + waveBoost * 0.1);
      }
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
  
  // Calculate the color influence of nearby pathways on a soul
  calculatePathwayInfluence(soul, packetSystem) {
    if (!packetSystem || !packetSystem.lightningPathways || packetSystem.lightningPathways.length === 0) {
      return null;
    }
    
    let totalInfluence = 0;
    let weightedHue = 0;
    let maxStrength = 0;
    
    // Check all pathways
    for (const pathway of packetSystem.lightningPathways) {
      // Calculate minimum distance from soul to this pathway
      let minDist = Infinity;
      
      if (pathway.braidSegments && pathway.braidSegments.length > 0) {
        for (const strand of pathway.braidSegments) {
          for (const segment of strand) {
            const dist = Math.hypot(segment.x - soul.x, segment.y - soul.y);
            minDist = Math.min(minDist, dist);
          }
        }
      }
      
      // If pathway is within influence radius, calculate its effect
      if (minDist < CONFIG.neuroplasticity.colorInfluenceRadius) {
        const proximityFactor = 1 - (minDist / CONFIG.neuroplasticity.colorInfluenceRadius);
        // Stronger pathways have more influence
        const usageFactor = Math.min(pathway.usageCount || 1, 20) / 20;
        const influence = proximityFactor * pathway.strength * (0.5 + usageFactor * 0.5);
        
        totalInfluence += influence;
        weightedHue += pathway.hue * influence;
        maxStrength = Math.max(maxStrength, pathway.strength);
      }
    }
    
    // Return averaged influence
    if (totalInfluence > 0) {
      return {
        strength: Math.min(totalInfluence, 1.0),
        hue: (weightedHue / totalInfluence) % 360,
        maxStrength
      };
    }
    
    return null;
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
  
  hslToRgb(h, s, l) {
    const c = (1 - Math.abs(2 * l - 1)) * s;
    const x = c * (1 - Math.abs((h / 60) % 2 - 1));
    const m = l - c / 2;
    
    let r, g, b;
    if (h < 60) { r = c; g = x; b = 0; }
    else if (h < 120) { r = x; g = c; b = 0; }
    else if (h < 180) { r = 0; g = c; b = x; }
    else if (h < 240) { r = 0; g = x; b = c; }
    else if (h < 300) { r = x; g = 0; b = c; }
    else { r = c; g = 0; b = x; }
    
    return {
      r: Math.round((r + m) * 255),
      g: Math.round((g + m) * 255),
      b: Math.round((b + m) * 255)
    };
  }
  
  renderZoomPhase(centerSoul, zoomFrame) {
    // Black background
    this.ctx.fillStyle = 'rgb(0, 0, 0)';
    this.ctx.fillRect(0, 0, this.width, this.height);
    
    // Calculate zoom scale
    const progress = zoomFrame / CONFIG.zoom.maxFrames;
    const scale = CONFIG.zoom.startScale - (CONFIG.zoom.startScale - CONFIG.zoom.endScale) * progress;
    
    // Center on the center soul
    const centerX = this.width / 2;
    const centerY = this.height / 2;
    
    // Render center soul's sub-souls
    for (const subSoul of centerSoul.subSouls) {
      const screenX = centerX + (subSoul.x - centerSoul.x) * scale;
      const screenY = centerY + (subSoul.y - centerSoul.y) * scale;
      const pixelSize = Math.max(2, scale * CONFIG.souls.pixelSpacing);
      
      for (const pixel of subSoul.pixels) {
        // Render with lower threshold during zoom to ensure visibility
        if (pixel.b < 0.02) continue;
        
        const px = screenX + (pixel.x - 1) * pixelSize;
        const py = screenY + (pixel.y - 1) * pixelSize;
        
        const rgb = this.hslToRgb(pixel.h, pixel.s, pixel.b);
        this.ctx.fillStyle = `rgb(${rgb.r}, ${rgb.g}, ${rgb.b})`;
        this.ctx.fillRect(px, py, pixelSize, pixelSize);
        
        // Glow for activated pixels
        if (pixel.b > 0.3) {
          const glowSize = pixelSize * (1 + pixel.b * 0.5);
          this.ctx.fillStyle = `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${pixel.b * 0.3})`;
          this.ctx.fillRect(px - (glowSize - pixelSize) / 2, py - (glowSize - pixelSize) / 2, glowSize, glowSize);
        }
      }
    }
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
      const avgHue = (conn.soul1.colorSignature.primaryHue + conn.soul2.colorSignature.primaryHue) / 2;
      
      this.ctx.save();
      
      // Draw as thin organic line following the spark path
      this.ctx.beginPath();
      this.ctx.moveTo(segments[0].x, segments[0].y);
      
      for (let i = 1; i < segments.length; i++) {
        this.ctx.lineTo(segments[i].x, segments[i].y);
      }
      
      // Subtle glow - ENHANCED for visibility of carved pathways
      this.ctx.shadowBlur = 8;
      this.ctx.shadowColor = `hsla(${avgHue}, 75%, 65%, ${strength * 0.4})`;
      
      // Main line - slightly thicker and brighter to show well-traveled paths
      this.ctx.strokeStyle = `hsla(${avgHue}, 85%, 70%, ${strength * 0.8})`;
      this.ctx.lineWidth = 1.5;
      this.ctx.stroke();
      
      // Brighter core for stronger connections - these are the highways!
      if (strength > 0.3) {
        this.ctx.strokeStyle = `hsla(${avgHue}, 90%, 80%, ${(strength - 0.3) * 0.8})`;
        this.ctx.lineWidth = 1;
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
    
    // Render pathway connections (braided connections between bolts)
    for (const connection of packetSystem.pathwayConnections) {
      this.ctx.save();
      
      const pulse = Math.sin(Date.now() * 0.003) * 0.15 + 0.85;
      
      // Draw each strand of the braid
      for (let s = 0; s < connection.braidSegments.length; s++) {
        const strand = connection.braidSegments[s];
        const strandHue = connection.hue + (s * 10 - 5); // Slight hue variation per strand
        
        this.ctx.beginPath();
        this.ctx.moveTo(strand[0].x, strand[0].y);
        for (let i = 1; i < strand.length; i++) {
          this.ctx.lineTo(strand[i].x, strand[i].y);
        }
        
        // Brighter, more prominent connection
        this.ctx.strokeStyle = `hsla(${strandHue}, 95%, 70%, ${connection.strength * pulse * 0.7})`;
        this.ctx.lineWidth = 1.5;
        this.ctx.shadowBlur = 6;
        this.ctx.shadowColor = `hsla(${strandHue}, 100%, 80%, ${connection.strength * 0.4})`;
        this.ctx.stroke();
      }
      
      this.ctx.restore();
    }
    
    // Render persistent pathways (strengthened connections with neuroplasticity)
    for (const pathway of packetSystem.lightningPathways) {
      this.ctx.save();
      
      // Neuroplasticity visual indicators
      const usageIntensity = Math.min(pathway.usageCount || 1, 20) / 20; // Cap at 20 uses
      const strengthFactor = Math.min(pathway.strength / CONFIG.neuroplasticity.maxPathwayStrength, 1);
      
      // Pulse stronger for heavily used pathways
      const pulsePeriod = 0.002 - (usageIntensity * 0.001); // Faster pulse for more used paths
      const pulseAmplitude = 0.2 + (usageIntensity * 0.3); // Stronger pulse
      const pulse = Math.sin(Date.now() * pulsePeriod + pathway.age * 0.1) * pulseAmplitude + 0.8;
      
      // Draw each strand with strength-based properties
      for (let s = 0; s < pathway.braidSegments.length; s++) {
        const strand = pathway.braidSegments[s];
        const strandHue = pathway.hue + (s * 15 - 7.5);
        
        this.ctx.beginPath();
        this.ctx.moveTo(strand[0].x, strand[0].y);
        for (let i = 1; i < strand.length; i++) {
          this.ctx.lineTo(strand[i].x, strand[i].y);
        }
        
        // Neuroplastic pathways: thickness and brightness scale with strength and usage
        const baseLineWidth = 1.5 + (strengthFactor * 2.5); // Up to 4px for strongest paths
        const baseAlpha = 0.6 + (strengthFactor * 0.3);
        
        // Strong persistent pathways glow more prominently
        this.ctx.strokeStyle = `hsla(${strandHue}, 100%, ${70 + usageIntensity * 15}%, ${pathway.strength * pulse * baseAlpha})`;
        this.ctx.lineWidth = baseLineWidth;
        this.ctx.shadowBlur = 8 + (strengthFactor * 12); // Up to 20px blur for strongest
        this.ctx.shadowColor = `hsla(${strandHue}, 100%, 85%, ${pathway.strength * (0.4 + usageIntensity * 0.3)})`;
        this.ctx.stroke();
        
        // Add inner bright core for well-established pathways
        if (strengthFactor > 0.5) {
          this.ctx.strokeStyle = `hsla(${strandHue}, 100%, 90%, ${(strengthFactor - 0.5) * 2 * pulse})`;
          this.ctx.lineWidth = baseLineWidth * 0.5;
          this.ctx.shadowBlur = 4;
          this.ctx.stroke();
        }
        
        // Add flowing energy particles along pathways (more for heavily used paths)
        if (pathway.strength > 0.3) {
          const particleCount = Math.floor(pathway.strength * 3 + usageIntensity * 5); // More particles for used paths
          for (let p = 0; p < particleCount; p++) {
            const t = ((Date.now() * (0.0015 + usageIntensity * 0.001) + p * 0.25 + s * 0.1) % 1);
            const idx = Math.floor(t * (strand.length - 1));
            if (idx >= 0 && idx < strand.length) {
              const point = strand[idx];
              
              this.ctx.shadowBlur = 0;
              this.ctx.beginPath();
              const particleSize = 1.5 + (strengthFactor * 1.5);
              this.ctx.arc(point.x, point.y, particleSize, 0, Math.PI * 2);
              this.ctx.fillStyle = `hsla(${strandHue}, 100%, 90%, ${pathway.strength * 0.8})`;
              this.ctx.fill();
              
              // Glow for strong pathways
              if (strengthFactor > 0.6) {
                this.ctx.shadowBlur = 6;
                this.ctx.shadowColor = `hsla(${strandHue}, 100%, 95%, ${strengthFactor})`;
                this.ctx.fill();
              }
            }
          }
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
    
    // Render braided bonds between resonant sparks
    for (const bond of sparkSystem.sparkBonds) {
      // Validate bond data before rendering
      if (!bond.point1 || !bond.point2 || !bond.braidSegments ||
          !isFinite(bond.point1.x) || !isFinite(bond.point1.y) ||
          !isFinite(bond.point2.x) || !isFinite(bond.point2.y) ||
          !isFinite(bond.hue) || !isFinite(bond.alpha) || !isFinite(bond.strength)) {
        continue;
      }
      
      this.ctx.save();
      
      // Create a pulsing animation
      const pulsePhase = (Date.now() * 0.003) % (Math.PI * 2);
      const pulse = Math.sin(pulsePhase) * 0.25 + 0.75;
      
      // Ensure hue is in valid range
      const hue = Math.max(0, Math.min(360, bond.hue));
      const alpha = Math.max(0, Math.min(1, bond.alpha));
      
      // Draw each strand of the braided bond
      for (let s = 0; s < bond.braidSegments.length; s++) {
        const strand = bond.braidSegments[s];
        const strandHue = (hue + (s * 20 - 20)) % 360; // Color variation per strand
        
        this.ctx.beginPath();
        this.ctx.moveTo(strand[0].x, strand[0].y);
        for (let i = 1; i < strand.length; i++) {
          this.ctx.lineTo(strand[i].x, strand[i].y);
        }
        
        // Outer glow
        this.ctx.shadowBlur = 10;
        this.ctx.shadowColor = `hsla(${strandHue}, 100%, 80%, ${alpha * bond.strength * 0.6})`;
        
        // Main strand
        this.ctx.strokeStyle = `hsla(${strandHue}, 95%, 75%, ${alpha * pulse * bond.strength * 0.9})`;
        this.ctx.lineWidth = 2 * bond.strength;
        this.ctx.stroke();
        
        // Bright inner core for stronger bonds
        if (bond.strength > 0.6) {
          this.ctx.shadowBlur = 0;
          this.ctx.strokeStyle = `hsla(${strandHue}, 100%, 90%, ${alpha * pulse * bond.strength})`;
          this.ctx.lineWidth = 1.2 * bond.strength;
          this.ctx.stroke();
        }
        
        // Energy particles flowing along the braid
        const particleCount = Math.floor(bond.strength * 4);
        for (let p = 0; p < particleCount; p++) {
          const t = ((Date.now() * 0.0012 + p * 0.25 + s * 0.15) % 1);
          const idx = Math.floor(t * (strand.length - 1));
          if (idx >= 0 && idx < strand.length) {
            const point = strand[idx];
            
            this.ctx.shadowBlur = 6;
            this.ctx.shadowColor = `hsla(${strandHue}, 100%, 90%, ${alpha * bond.strength * 0.8})`;
            this.ctx.beginPath();
            this.ctx.arc(point.x, point.y, 2 * bond.strength, 0, Math.PI * 2);
            this.ctx.fillStyle = `hsla(${strandHue}, 100%, 95%, ${alpha * bond.strength})`;
            this.ctx.fill();
          }
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
    this.ctx.fillStyle = `hsla(${soul.colorSignature.primaryHue}, 40%, 50%, 0.15)`;
    this.ctx.fill();
  }
  
  renderActiveSoul(soul, frameCount) {
    // Environment glow (larger, dimmer)
    const envGradient = this.ctx.createRadialGradient(
      soul.x, soul.y, 0, 
      soul.x, soul.y, CONFIG.visuals.envGlowRadius
    );
    envGradient.addColorStop(0, `hsla(${soul.colorSignature.primaryHue}, 60%, 50%, ${0.08 * soul.activationLevel})`);
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
    this.ctx.fillStyle = `hsla(${soul.colorSignature.primaryHue}, 90%, 70%, ${pulse * soul.activationLevel})`;
    this.ctx.fill();
    
    // Inner glow
    const gradient = this.ctx.createRadialGradient(
      soul.x, soul.y, 0, 
      soul.x, soul.y, CONFIG.visuals.glowRadius
    );
    gradient.addColorStop(0, `hsla(${soul.colorSignature.primaryHue}, 80%, 60%, ${0.25 * soul.activationLevel})`);
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
  const [stats, setStats] = useState({ souls: 0, sparks: 0, bonds: 0, pathways: 0, persistentPathways: 0, frame: 0, axions: 0, traces: 0, axionsEnabled: false, fps: 60, coreMode: false });
  
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
    
    // Activate center soul for zoom phase
    soulSystem.activate(soulSystem.centerSoul, 0);
    
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
        // Keep center soul fully activated during zoom
        soulSystem.centerSoul.activationLevel = 1.0;
        soulSystem.centerSoul.lastHitTime = zoomFrame;
        
        // Update center soul during zoom to maintain colors
        soulSystem.updateSoul(soulSystem.centerSoul, zoomFrame, waveSystem, sparkSystem, axionSystem, packetSystem);
        
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
        soulSystem.update(frameCount, waveSystem, sparkSystem, axionSystem, packetSystem);
        packetSystem.update(soulSystem, waveSystem, frameCount, axionSystem);
        waveSystem.update();
        sparkSystem.update(waveSystem, axionSystem, soulSystem);
        axionSystem.updateActivationStatus(soulSystem);
        axionSystem.update(soulSystem, frameCount);
      }
      
      frameCount++;
      
      if (frameCount % 10 === 0) {
        // Calculate neuroplastic pathway statistics
        const pathways = packetSystem.lightningPathways;
        let avgStrength = 0;
        let maxStrength = 0;
        let totalUsage = 0;
        
        if (pathways.length > 0) {
          for (const pathway of pathways) {
            avgStrength += pathway.strength;
            maxStrength = Math.max(maxStrength, pathway.strength);
            totalUsage += (pathway.usageCount || 0);
          }
          avgStrength /= pathways.length;
        }
        
        setStats({
          souls: soulSystem.getActiveSoulCount(),
          sparks: sparkSystem.sparks.length,
          bonds: sparkSystem.sparkBonds.length,
          pathways: packetSystem.pathwayConnections.length,
          persistentPathways: packetSystem.lightningPathways.length,
          avgPathwayStrength: avgStrength,
          maxPathwayStrength: maxStrength,
          totalPathwayUsage: totalUsage,
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
        {stats.bonds > 0 && (
          <div style={{ color: 'rgba(255, 200, 100, 0.8)', fontSize: '12px' }}>
            🔗 Bonds: {stats.bonds}
          </div>
        )}
        {stats.pathways > 0 && (
          <div style={{ color: 'rgba(150, 255, 200, 0.9)', fontSize: '12px', fontWeight: 'bold' }}>
            🤝 Pathways: {stats.pathways}
          </div>
        )}
        {stats.persistentPathways > 0 && (
          <>
            <div style={{ color: 'rgba(200, 150, 255, 0.95)', fontSize: '12px', fontWeight: 'bold' }}>
              ✨ Braided: {stats.persistentPathways}
            </div>
            {stats.avgPathwayStrength > 0 && (
              <div style={{ 
                color: 'rgba(200, 150, 255, 0.75)', 
                fontSize: '10px',
                marginLeft: 8,
                fontStyle: 'italic'
              }}>
                🧠 Avg Strength: {stats.avgPathwayStrength.toFixed(2)}
              </div>
            )}
            {stats.maxPathwayStrength > 1.0 && (
              <div style={{ 
                color: 'rgba(255, 150, 255, 0.95)', 
                fontSize: '10px',
                marginLeft: 8,
                fontWeight: 'bold'
              }}>
                ⚡ Max: {stats.maxPathwayStrength.toFixed(2)}x
              </div>
            )}
            {stats.totalPathwayUsage > 0 && (
              <div style={{ 
                color: 'rgba(180, 150, 255, 0.7)', 
                fontSize: '10px',
                marginLeft: 8
              }}>
                📊 Total Usage: {Math.round(stats.totalPathwayUsage)}
              </div>
            )}
          </>
        )}
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
            color: 'rgba(100, 255, 150, 0.95)',
            fontWeight: 'bold'
          }}>
            🧠 NETWORK MODE: Pathways optimized
          </div>
        )}
        <div style={{ marginTop: 8, fontSize: '11px', opacity: 0.6 }}>
          Recursive: 9 sub-souls × 9 pixels = 81
        </div>
        <div style={{ marginTop: 4, fontSize: '10px', opacity: 0.5, color: 'rgba(200, 150, 255, 0.7)' }}>
          ✨ Resonant Color Signatures
        </div>
        <div style={{ marginTop: 2, fontSize: '10px', opacity: 0.5, color: 'rgba(150, 255, 200, 0.7)' }}>
          🎵 Harmonic Communication
        </div>
        <div style={{ marginTop: 2, fontSize: '10px', opacity: 0.5, color: 'rgba(255, 150, 255, 0.7)' }}>
          🧠 Neuroplastic Pathways: Strengthen with use
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
