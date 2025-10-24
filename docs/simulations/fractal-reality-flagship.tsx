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
    decayRate: 0.99992,           // Nearly permanent - extremely slow decay
    decayStartTime: 5000,         // Wait 5 seconds before any decay starts
    minStrength: 0.001,           // Very low threshold before deletion
    neuroplasticityBonus: 0.08,   // Bonus strength when pathway is reused (neuroplasticity!)
    lightningReinforcement: 0.15, // How much lightning strengthens pathways
    lightningAttractionMultiplier: 1.5, // How much pathways attract lightning (1.5 = 50% more)
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
  
  // NEW: Find nearby sparks for braiding
  findNeighborSparks(spark, maxDistance = 120) {
    const neighbors = [];
    const sparkMid = spark.segments[Math.floor(spark.segments.length / 2)];
    
    for (const other of this.sparks) {
      if (other === spark) continue;
      
      const otherMid = other.segments[Math.floor(other.segments.length / 2)];
      const dist = Math.hypot(otherMid.x - sparkMid.x, otherMid.y - sparkMid.y);
      
      if (dist < maxDistance) {
        neighbors.push({ spark: other, distance: dist, midpoint: otherMid });
      }
    }
    
    return neighbors.sort((a, b) => a.distance - b.distance);
  }
  
  // NEW: Apply attraction to bend sparks toward neighbors (braiding)
  applyNeighborAttraction(spark) {
    if (!spark.neighbors || spark.neighbors.length === 0) return;
    
    // Attract toward closest 2-3 neighbors
    for (let i = 0; i < Math.min(3, spark.neighbors.length); i++) {
      const neighbor = spark.neighbors[i];
      const attractionStrength = 0.2 * (1 - neighbor.distance / 120);
      
      // Bend middle and later segments toward neighbor (creates braiding effect)
      for (let j = Math.floor(spark.segments.length * 0.3); j < spark.segments.length; j++) {
        const seg = spark.segments[j];
        const t = j / spark.segments.length;
        const bendStrength = attractionStrength * Math.sin(t * Math.PI) * 1.5;
        
        const dx = neighbor.midpoint.x - seg.x;
        const dy = neighbor.midpoint.y - seg.y;
        const dist = Math.hypot(dx, dy);
        
        if (dist > 0) {
          seg.x += (dx / dist) * bendStrength;
          seg.y += (dy / dist) * bendStrength;
        }
      }
    }
  }
  
  // NEW: Share colors through braided connections
  shareColorsAlongBraid(spark1, spark2, strength) {
    const shareRate = 0.12 * strength;
    const targetHue = (spark1.hue + spark2.hue) / 2;
    spark1.hue += (targetHue - spark1.hue) * shareRate;
    spark2.hue += (targetHue - spark2.hue) * shareRate;
    spark1.hue = (spark1.hue + 360) % 360;
    spark2.hue = (spark2.hue + 360) % 360;
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
            
            this.sparkBonds.push({
              point1,
              point2,
              strength: resonance,
              hue: avgHue,
              alpha: bondAlpha,
              spark1,
              spark2,
              distance: minDist
            });
            
            // NEW: Share colors through the bond
            this.shareColorsAlongBraid(spark1, spark2, resonance);
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
      originY: y,
      neighbors: [] // NEW: For braiding
    });
  }
  
  update(waveSystem, axionSystem = null, soulSystem = null) {
    // NEW: First pass - find neighbors for all sparks
    for (const spark of this.sparks) {
      spark.neighbors = this.findNeighborSparks(spark);
    }
    
    // Second pass - update sparks and apply braiding
    for (let i = this.sparks.length - 1; i >= 0; i--) {
      const spark = this.sparks[i];
      
      spark.age++;
      spark.alpha = 1.0 - (spark.age / spark.maxAge);
      
      // NEW: Apply neighbor attraction to create braiding (after age 5, before 80% of life)
      if (spark.age > 5 && spark.age < spark.maxAge * 0.8) {
        this.applyNeighborAttraction(spark);
      }
      
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
  
  // NEW: Get the strength of the pathway between two souls
  getPathwayStrength(soul1, soul2, soulSystem) {
    if (!soul1 || !soul2) return 0;
    
    const soul1Idx = soulSystem.souls.indexOf(soul1);
    const soul2Idx = soulSystem.souls.indexOf(soul2);
    
    if (soul1Idx === -1 || soul2Idx === -1) return 0;
    
    const key = soul1Idx < soul2Idx ? `${soul1Idx}-${soul2Idx}` : `${soul2Idx}-${soul1Idx}`;
    const trace = this.pathTraces.get(key);
    
    return trace ? trace.strength : 0;
  }
  
  // NEW: Strengthen a pathway when lightning travels it (reinforcement learning!)
  strengthenPathway(soul1, soul2, soulSystem) {
    if (!soul1 || !soul2 || !this.enabled) return;
    
    const soul1Idx = soulSystem.souls.indexOf(soul1);
    const soul2Idx = soulSystem.souls.indexOf(soul2);
    
    if (soul1Idx === -1 || soul2Idx === -1) return;
    
    const key = soul1Idx < soul2Idx ? `${soul1Idx}-${soul2Idx}` : `${soul2Idx}-${soul1Idx}`;
    const trace = this.pathTraces.get(key);
    
    if (trace) {
      // LIGHTNING REINFORCEMENT: Pathways strengthen significantly when lightning travels them!
      // This creates a powerful feedback loop: strong paths attract lightning, lightning makes them stronger!
      trace.strength = Math.min(3.0, trace.strength + CONFIG.axions.lightningReinforcement);
      trace.lastTravel = Date.now();
    }
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
        // NEUROPLASTICITY: Reused pathways strengthen more!
        // Sparks can push to 2.0, Lightning can push to 2.5 (super-highways!)
        const baseGrowth = CONFIG.axions.growthPerSpark;
        const neuroplasticityGrowth = CONFIG.axions.neuroplasticityBonus;
        existing.strength = Math.min(3.0, existing.strength + baseGrowth + neuroplasticityGrowth);
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
    
    // Decay path traces over time (but very slowly - nearly permanent)
    for (const [key, trace] of this.pathTraces.entries()) {
      const timeSinceTravel = Date.now() - trace.lastTravel;
      
      // Only decay after significant time (5 seconds), and very slowly
      if (timeSinceTravel > CONFIG.axions.decayStartTime) {
        trace.strength *= CONFIG.axions.decayRate;
      }
      
      // Age recent paths
      for (const path of trace.recentPaths) {
        path.age++;
      }
      
      // Only remove extremely weak traces (pathways are nearly permanent)
      if (trace.strength < CONFIG.axions.minStrength) {
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
      frameCount: 0,
      stuckCounter: 0, // Anti-stuck mechanism
      lastX: 0,
      lastY: 0
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
      
      // STRONGLY prefer pathways when they exist (neural routing with strength-based attraction)
      let connectionBonus = 0;
      if (axionSystem && axionSystem.enabled && this.packet.targetSoul) {
        const pathwayStrength = axionSystem.getPathwayStrength(this.packet.targetSoul, soul, soulSystem);
        if (pathwayStrength > 0) {
          // Bonus scales with pathway strength: stronger pathways = more attraction
          // Base 2.0 + (strength * multiplier): creates powerful feedback loop!
          connectionBonus = 2.0 + (pathwayStrength * CONFIG.axions.lightningAttractionMultiplier);
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
      
      // STUCK DETECTION: If packet hasn't moved much, increment counter
      const moveDist = Math.hypot(this.packet.x - this.packet.lastX, this.packet.y - this.packet.lastY);
      if (moveDist < 0.5) {
        this.packet.stuckCounter++;
        
        // If stuck for 60 frames, force a reset
        if (this.packet.stuckCounter > 60) {
          const randomSoul = soulSystem.souls[Math.floor(Math.random() * soulSystem.souls.length)];
          this.packet.x = randomSoul.x;
          this.packet.y = randomSoul.y;
          this.packet.targetSoul = randomSoul;
          this.packet.targetX = randomSoul.x;
          this.packet.targetY = randomSoul.y;
          this.packet.vx = 0;
          this.packet.vy = 0;
          this.packet.stuckCounter = 0;
          this.packet.trail = [];
        }
      } else {
        this.packet.stuckCounter = 0;
      }
      
      // Update last position for stuck detection
      this.packet.lastX = this.packet.x;
      this.packet.lastY = this.packet.y;
      
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
        const previousSoul = soul; // Store current soul
        let nextSoul = this.findNextTarget(soulSystem, axionSystem);
        
        // ANTI-STUCK: If no target found, find ANY activated soul as fallback
        if (!nextSoul) {
          const fallbackSouls = soulSystem.souls.filter(s => 
            s.activated && 
            s !== previousSoul && 
            Math.hypot(s.x - this.packet.x, s.y - this.packet.y) < CONFIG.packet.jumpDistance * 1.5
          );
          if (fallbackSouls.length > 0) {
            nextSoul = fallbackSouls[Math.floor(Math.random() * fallbackSouls.length)];
          }
        }
        
        // LAST RESORT: If still no target, pick ANY soul within extended range
        if (!nextSoul) {
          const anySouls = soulSystem.souls.filter(s => 
            s !== previousSoul && 
            Math.hypot(s.x - this.packet.x, s.y - this.packet.y) < CONFIG.packet.jumpDistance * 2
          );
          if (anySouls.length > 0) {
            nextSoul = anySouls[Math.floor(Math.random() * anySouls.length)];
          }
        }
        
        if (nextSoul) {
          // REINFORCE THE PATHWAY: Lightning traveling a pathway strengthens it!
          if (axionSystem && previousSoul) {
            axionSystem.strengthenPathway(previousSoul, nextSoul, soulSystem);
          }
          
          // Create lightning bolt from current position to next soul
          this.createLightningBolt(this.packet.x, this.packet.y, nextSoul.x, nextSoul.y);
          
          this.packet.targetSoul = nextSoul;
          this.packet.targetX = nextSoul.x;
          this.packet.targetY = nextSoul.y;
          this.packet.trail = [];
          this.packet.stuckCounter = 0; // Reset stuck counter
          
          // Slight hue shift
          this.packet.hue = (this.packet.hue + Math.random() * 20 - 10 + 360) % 360;
        } else {
          // Truly stuck - teleport to a random soul (emergency reset)
          const randomSoul = soulSystem.souls[Math.floor(Math.random() * soulSystem.souls.length)];
          this.packet.x = randomSoul.x;
          this.packet.y = randomSoul.y;
          this.packet.targetSoul = randomSoul;
          this.packet.targetX = randomSoul.x;
          this.packet.targetY = randomSoul.y;
          this.packet.stuckCounter = 0;
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
      
      // Subtle glow - scales with strength (lightning-reinforced paths glow more)
      const glowIntensity = Math.min(1, strength / 2.0); // Normalize 0-2.0 to 0-1
      this.ctx.shadowBlur = 8 + glowIntensity * 12; // 8-20px blur for super-highways
      this.ctx.shadowColor = `hsla(${avgHue}, 75%, 65%, ${glowIntensity * 0.6})`;
      
      // Main line - thickness increases with strength (shows reinforcement!)
      // Base 1.5px, up to 5px for heavily lightning-traveled pathways
      const lineThickness = 1.5 + (glowIntensity * 3.5);
      this.ctx.strokeStyle = `hsla(${avgHue}, 85%, 70%, ${Math.min(1, glowIntensity * 1.1)})`;
      this.ctx.lineWidth = lineThickness;
      this.ctx.stroke();
      
      // Brighter core for stronger connections - these are the neural super-highways!
      if (strength > 0.3) {
        const coreIntensity = Math.min(1, (strength - 0.3) / 2.0); // 0.3-2.3 → 0-1
        this.ctx.strokeStyle = `hsla(${avgHue}, 95%, 85%, ${Math.min(1, coreIntensity * 1.1)})`;
        this.ctx.lineWidth = lineThickness * 0.6; // Core is thinner
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
    
    // Render bonds between resonant sparks
    for (const bond of sparkSystem.sparkBonds) {
      // Validate bond data before rendering
      if (!bond.point1 || !bond.point2 || 
          !isFinite(bond.point1.x) || !isFinite(bond.point1.y) ||
          !isFinite(bond.point2.x) || !isFinite(bond.point2.y) ||
          !isFinite(bond.hue) || !isFinite(bond.alpha) || !isFinite(bond.strength)) {
        continue;
      }
      
      this.ctx.save();
      
      // Create a subtle, pulsing connection line
      const pulsePhase = (Date.now() * 0.003) % (Math.PI * 2);
      const pulse = Math.sin(pulsePhase) * 0.2 + 0.8;
      
      // Ensure hue is in valid range
      const hue = Math.max(0, Math.min(360, bond.hue));
      const alpha = Math.max(0, Math.min(1, bond.alpha * pulse * 0.6));
      
      // Draw bond connection with gradient
      const gradient = this.ctx.createLinearGradient(
        bond.point1.x, bond.point1.y,
        bond.point2.x, bond.point2.y
      );
      
      gradient.addColorStop(0, `hsla(${hue}, 80%, 60%, ${alpha})`);
      gradient.addColorStop(0.5, `hsla(${hue}, 90%, 70%, ${Math.max(0, Math.min(1, bond.alpha * pulse * 0.9))})`);
      gradient.addColorStop(1, `hsla(${hue}, 80%, 60%, ${alpha})`);
      
      // Draw main bond line
      this.ctx.beginPath();
      this.ctx.moveTo(bond.point1.x, bond.point1.y);
      this.ctx.lineTo(bond.point2.x, bond.point2.y);
      this.ctx.strokeStyle = gradient;
      this.ctx.lineWidth = Math.max(0.5, 1.5 * bond.strength);
      this.ctx.stroke();
      
      // Add glow for stronger bonds
      if (bond.strength > 0.7) {
        this.ctx.shadowBlur = 8;
        this.ctx.shadowColor = `hsla(${hue}, 90%, 70%, ${Math.max(0, Math.min(1, bond.alpha * 0.5))})`;
        this.ctx.strokeStyle = `hsla(${hue}, 100%, 80%, ${Math.max(0, Math.min(1, bond.alpha * bond.strength * 0.4))})`;
        this.ctx.lineWidth = 3;
        this.ctx.stroke();
      }
      
      // Draw energy particles flowing along the bond
      const particleCount = Math.floor(bond.strength * 3);
      for (let i = 0; i < particleCount; i++) {
        const t = ((Date.now() * 0.001 + i * 0.3) % 1);
        const px = bond.point1.x + (bond.point2.x - bond.point1.x) * t;
        const py = bond.point1.y + (bond.point2.y - bond.point1.y) * t;
        
        this.ctx.shadowBlur = 0;
        this.ctx.beginPath();
        this.ctx.arc(px, py, 1.5, 0, Math.PI * 2);
        this.ctx.fillStyle = `hsla(${hue}, 100%, 80%, ${Math.max(0, Math.min(1, bond.alpha * bond.strength))})`;
        this.ctx.fill();
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
  const [stats, setStats] = useState({ souls: 0, sparks: 0, bonds: 0, frame: 0, axions: 0, traces: 0, axionsEnabled: false, fps: 60, coreMode: false });
  
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
        soulSystem.updateSoul(soulSystem.centerSoul, zoomFrame, waveSystem, sparkSystem, axionSystem);
        
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
          bonds: sparkSystem.sparkBonds.length,
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
