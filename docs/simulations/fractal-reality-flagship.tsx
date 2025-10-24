import React, { useEffect, useRef, useState } from 'react';

const FractalSoulArray = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isZooming, setIsZooming] = useState(true);
  const [zoomProgress, setZoomProgress] = useState(0);
  
  // Animation state
  const stateRef = useRef({
    souls: [] as Soul[],
    lines: [] as Line[],
    frameCount: 0,
    centerSoul: null as Soul | null
  });

  // Soul Structure
  interface Pixel {
    h: number;  // hue (0-360)
    s: number;  // saturation (0-1)
    b: number;  // brightness (0-1)
  }

  interface Soul {
    // Position
    x: number;
    y: number;
    
    // 8-Dimensional State (ICE×2 + Part/Whole)
    pixels: {
      infoSelf: Pixel;      // [1] NW - Information-Local
      consSelf: Pixel;      // [2] N  - Consciousness-Local
      energySelf: Pixel;    // [3] NE - Energy-Local
      infoField: Pixel;     // [4] W  - Information-Field
      consField: Pixel;     // [5] E  - Consciousness-Field
      energyField: Pixel;   // [6] SE - Energy-Field
      part: Pixel;          // [7] S  - Downward Integration
      whole: Pixel;         // [8] SW - Upward Integration
    };
    
    // Intrinsic Properties (eternal)
    phase: number;        // Position in universal loop
    frequency: number;    // Speed through universal loop
    baseHue: number;      // Base color signature
    
    // State
    activated: boolean;
    activationLevel: number;
    activationTime: number;
  }

  interface Line {
    x: number;
    y: number;
    vx: number;
    vy: number;
    frequency: number;
    phase: number;
    hue: number;
    age: number;
    maxAge: number;
    trail: Array<{x: number, y: number, alpha: number}>;
  }

  // Constants
  const SOUL_SPACING = 35;
  const ACTIVATION_RADIUS = 40;
  const RESONANCE_THRESHOLD = 0.6;
  const LINE_SPEED = 2;
  const MAX_LINE_AGE = 300;
  const PIXEL_SPACING = 8;

  // Initialize Souls
  const initializeSouls = (width: number, height: number): Soul[] => {
    const souls: Soul[] = [];
    const centerX = width / 2;
    const centerY = height / 2;
    
    // Create grid of souls
    for (let x = SOUL_SPACING; x < width - SOUL_SPACING; x += SOUL_SPACING) {
      for (let y = SOUL_SPACING; y < height - SOUL_SPACING; y += SOUL_SPACING) {
        // Each soul has unique phase and frequency
        const phase = Math.random() * Math.PI * 2;
        const frequency = 0.02 + Math.random() * 0.03;
        const baseHue = Math.random() * 360;
        
        const soul: Soul = {
          x,
          y,
          phase,
          frequency,
          baseHue,
          activated: false,
          activationLevel: 0,
          activationTime: 0,
          pixels: {
            infoSelf: { h: baseHue, s: 0.3, b: 0 },
            consSelf: { h: (baseHue + 40) % 360, s: 0.3, b: 0 },
            energySelf: { h: (baseHue + 80) % 360, s: 0.3, b: 0 },
            infoField: { h: (baseHue + 120) % 360, s: 0.3, b: 0 },
            consField: { h: (baseHue + 160) % 360, s: 0.3, b: 0 },
            energyField: { h: (baseHue + 200) % 360, s: 0.3, b: 0 },
            part: { h: (baseHue + 240) % 360, s: 0.3, b: 0 },
            whole: { h: (baseHue + 280) % 360, s: 0.3, b: 0 }
          }
        };
        
        souls.push(soul);
      }
    }
    
    // Find and activate center soul
    let centerSoul = souls[0];
    let minDist = Infinity;
    
    for (const soul of souls) {
      const dist = Math.hypot(soul.x - centerX, soul.y - centerY);
      if (dist < minDist) {
        minDist = dist;
        centerSoul = soul;
      }
    }
    
    // Activate center soul
    activateSoul(centerSoul, null, 0);
    stateRef.current.centerSoul = centerSoul;
    
    return souls;
  };

  // Color Harmony (for coherence calculations)
  const colorHarmony = (p1: Pixel, p2: Pixel): number => {
    const hueDiff = Math.abs(p1.h - p2.h);
    const normalizedDiff = Math.min(hueDiff, 360 - hueDiff) / 180;
    return 1 - normalizedDiff;
  };

  // Calculate Internal Coherence (for Pixel 7 - PART)
  const calculateInternalCoherence = (soul: Soul): number => {
    const pixels = [
      soul.pixels.infoSelf,
      soul.pixels.consSelf,
      soul.pixels.energySelf,
      soul.pixels.infoField,
      soul.pixels.consField,
      soul.pixels.energyField
    ];
    
    let coherence = 0;
    let count = 0;
    
    for (let i = 0; i < pixels.length; i++) {
      for (let j = i + 1; j < pixels.length; j++) {
        coherence += colorHarmony(pixels[i], pixels[j]) * pixels[i].b * pixels[j].b;
        count++;
      }
    }
    
    return count > 0 ? coherence / count : 0;
  };

  // Calculate External Coherence (for Pixel 8 - WHOLE)
  const calculateExternalCoherence = (soul: Soul, allSouls: Soul[]): number => {
    let coherence = 0;
    let count = 0;
    const searchRadius = SOUL_SPACING * 3;
    
    for (const other of allSouls) {
      if (other === soul || !other.activated) continue;
      
      const dist = Math.hypot(soul.x - other.x, soul.y - other.y);
      if (dist < searchRadius) {
        const proximity = 1 - (dist / searchRadius);
        const resonance = resonanceMatch(soul, other);
        coherence += resonance * proximity * other.activationLevel;
        count++;
      }
    }
    
    return count > 0 ? coherence / count : 0;
  };

  // Resonance Match between souls
  const resonanceMatch = (soul1: Soul, soul2: Soul): number => {
    let match = 0;
    
    // Compare ICE-Local
    match += colorHarmony(soul1.pixels.infoSelf, soul2.pixels.infoSelf) * 0.15;
    match += colorHarmony(soul1.pixels.consSelf, soul2.pixels.consSelf) * 0.15;
    match += colorHarmony(soul1.pixels.energySelf, soul2.pixels.energySelf) * 0.15;
    
    // Compare ICE-Field
    match += colorHarmony(soul1.pixels.infoField, soul2.pixels.infoField) * 0.15;
    match += colorHarmony(soul1.pixels.consField, soul2.pixels.consField) * 0.15;
    match += colorHarmony(soul1.pixels.energyField, soul2.pixels.energyField) * 0.15;
    
    // Compare Part/Whole
    match += colorHarmony(soul1.pixels.part, soul2.pixels.part) * 0.05;
    match += colorHarmony(soul1.pixels.whole, soul2.pixels.whole) * 0.05;
    
    return match;
  };

  // Activate Soul
  const activateSoul = (soul: Soul, activatingLine: Line | null, frameCount: number) => {
    soul.activated = true;
    soul.activationLevel = 1.0;
    soul.activationTime = frameCount;
    
    // Initialize all 8 pixels with some brightness
    soul.pixels.infoSelf.b = 0.3 + Math.random() * 0.3;
    soul.pixels.consSelf.b = 0.3 + Math.random() * 0.3;
    soul.pixels.energySelf.b = 0.3 + Math.random() * 0.3;
    soul.pixels.infoField.b = 0.2 + Math.random() * 0.2;
    soul.pixels.consField.b = 0.2 + Math.random() * 0.2;
    soul.pixels.energyField.b = 0.2 + Math.random() * 0.2;
    soul.pixels.part.b = 0.1;
    soul.pixels.whole.b = 0.1;
    
    // Emit line from this soul
    const angle = activatingLine ? 
      Math.atan2(activatingLine.vy, activatingLine.vx) + (Math.random() - 0.5) * 0.6 :
      Math.random() * Math.PI * 2;
    
    const newLine: Line = {
      x: soul.x,
      y: soul.y,
      vx: Math.cos(angle) * LINE_SPEED,
      vy: Math.sin(angle) * LINE_SPEED,
      frequency: soul.frequency,
      phase: soul.phase,
      hue: soul.baseHue,
      age: 0,
      maxAge: MAX_LINE_AGE,
      trail: []
    };
    
    stateRef.current.lines.push(newLine);
  };

  // Universal Soul Loop (runs for ALL souls)
  const soulLoop = (soul: Soul, frameCount: number, allSouls: Soul[]) => {
    // Update phase (soul moves through its cycle)
    soul.phase += soul.frequency;
    if (soul.phase > Math.PI * 2) soul.phase -= Math.PI * 2;
    
    if (!soul.activated) return;
    
    // 1. SENSE - Update field pixels based on environment
    const externalCoherence = calculateExternalCoherence(soul, allSouls);
    soul.pixels.infoField.b = Math.min(1, soul.pixels.infoField.b * 0.95 + externalCoherence * 0.1);
    soul.pixels.consField.b = Math.min(1, soul.pixels.consField.b * 0.95 + externalCoherence * 0.12);
    soul.pixels.energyField.b = Math.min(1, soul.pixels.energyField.b * 0.95 + externalCoherence * 0.08);
    
    // 2. INTEGRATE - Update local pixels based on phase
    const pulseSelf = Math.sin(soul.phase) * 0.5 + 0.5;
    soul.pixels.infoSelf.b = Math.min(1, 0.4 + pulseSelf * 0.3);
    soul.pixels.consSelf.b = Math.min(1, 0.5 + Math.cos(soul.phase) * 0.3);
    soul.pixels.energySelf.b = Math.min(1, 0.4 + Math.sin(soul.phase * 2) * 0.3);
    
    // 3. HARMONIZE - Update Part/Whole pixels
    const internalCoherence = calculateInternalCoherence(soul);
    soul.pixels.part.b = internalCoherence;
    soul.pixels.whole.b = externalCoherence;
    
    // 4. UPDATE - Pulse activation level
    const age = frameCount - soul.activationTime;
    soul.activationLevel = Math.min(1, 0.3 + Math.sin(age * 0.05) * 0.3 + 0.4);
  };

  // Check if line resonates with soul
  const checkLineResonance = (line: Line, soul: Soul): boolean => {
    const freqMatch = Math.abs(line.frequency - soul.frequency) < 0.02;
    const phaseMatch = Math.abs(Math.sin(line.phase) - Math.sin(soul.phase)) < 0.5;
    
    // Also check color harmony
    const hueMatch = Math.abs(line.hue - soul.baseHue) < 60 || 
                     Math.abs(line.hue - soul.baseHue) > 300;
    
    return freqMatch && (phaseMatch || hueMatch);
  };

  // Update Lines
  const updateLines = (souls: Soul[], frameCount: number) => {
    const { lines } = stateRef.current;
    
    for (let i = lines.length - 1; i >= 0; i--) {
      const line = lines[i];
      
      // Add to trail
      line.trail.push({ x: line.x, y: line.y, alpha: 1 });
      if (line.trail.length > 20) line.trail.shift();
      
      // Update trail alpha
      line.trail.forEach((point, idx) => {
        point.alpha = idx / line.trail.length;
      });
      
      // Move line
      line.x += line.vx;
      line.y += line.vy;
      
      // Update phase
      line.phase += line.frequency;
      
      // Add slight curve
      const curvature = Math.sin(line.age * 0.02) * 0.03;
      const angle = Math.atan2(line.vy, line.vx) + curvature;
      line.vx = Math.cos(angle) * LINE_SPEED;
      line.vy = Math.sin(angle) * LINE_SPEED;
      
      // Check for soul activation
      for (const soul of souls) {
        if (soul.activated) continue;
        
        const dist = Math.hypot(line.x - soul.x, line.y - soul.y);
        if (dist < ACTIVATION_RADIUS) {
          if (checkLineResonance(line, soul)) {
            const resonance = resonanceMatch(stateRef.current.centerSoul!, soul);
            if (resonance > RESONANCE_THRESHOLD || Math.random() > 0.7) {
              activateSoul(soul, line, frameCount);
            }
          }
        }
      }
      
      // Age and remove old lines
      line.age++;
      if (line.age > line.maxAge) {
        lines.splice(i, 1);
      }
    }
  };

  // Render
  const render = (ctx: CanvasRenderingContext2D, width: number, height: number) => {
    const { souls, lines, frameCount } = stateRef.current;
    
    // Clear with fade
    ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
    ctx.fillRect(0, 0, width, height);
    
    // Render lines
    for (const line of lines) {
      // Trail
      ctx.beginPath();
      for (let i = 0; i < line.trail.length - 1; i++) {
        const p1 = line.trail[i];
        const p2 = line.trail[i + 1];
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
      }
      ctx.strokeStyle = `hsla(${line.hue}, 80%, 60%, ${0.3})`;
      ctx.lineWidth = 1;
      ctx.stroke();
      
      // Head
      ctx.beginPath();
      ctx.arc(line.x, line.y, 2, 0, Math.PI * 2);
      ctx.fillStyle = `hsla(${line.hue}, 90%, 70%, 0.8)`;
      ctx.fill();
    }
    
    // Render souls
    for (const soul of souls) {
      if (!soul.activated) {
        // Dormant: faint ghost
        ctx.beginPath();
        ctx.arc(soul.x, soul.y, 1, 0, Math.PI * 2);
        ctx.fillStyle = `hsla(${soul.baseHue}, 30%, 50%, 0.08)`;
        ctx.fill();
      } else {
        // Active: render center + 8 pixels
        
        // Center (pulsing)
        const pulse = Math.sin(frameCount * 0.03 + soul.phase) * 0.3 + 0.7;
        ctx.beginPath();
        ctx.arc(soul.x, soul.y, 3, 0, Math.PI * 2);
        ctx.fillStyle = `hsla(${soul.baseHue}, 90%, 70%, ${pulse * soul.activationLevel})`;
        ctx.fill();
        
        // Glow
        const gradient = ctx.createRadialGradient(soul.x, soul.y, 0, soul.x, soul.y, 10);
        gradient.addColorStop(0, `hsla(${soul.baseHue}, 80%, 60%, ${0.3 * soul.activationLevel})`);
        gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
        ctx.fillStyle = gradient;
        ctx.fillRect(soul.x - 10, soul.y - 10, 20, 20);
        
        // 8 surrounding pixels
        const positions = [
          { x: -PIXEL_SPACING, y: -PIXEL_SPACING, pixel: soul.pixels.infoSelf },   // NW
          { x: 0, y: -PIXEL_SPACING, pixel: soul.pixels.consSelf },                 // N
          { x: PIXEL_SPACING, y: -PIXEL_SPACING, pixel: soul.pixels.energySelf },   // NE
          { x: -PIXEL_SPACING, y: 0, pixel: soul.pixels.infoField },                // W
          { x: PIXEL_SPACING, y: 0, pixel: soul.pixels.consField },                 // E
          { x: PIXEL_SPACING, y: PIXEL_SPACING, pixel: soul.pixels.energyField },   // SE
          { x: 0, y: PIXEL_SPACING, pixel: soul.pixels.part },                      // S
          { x: -PIXEL_SPACING, y: PIXEL_SPACING, pixel: soul.pixels.whole }         // SW
        ];
        
        for (const pos of positions) {
          const brightness = pos.pixel.b * soul.activationLevel;
          if (brightness > 0.05) {
            ctx.fillStyle = `hsla(${pos.pixel.h}, ${pos.pixel.s * 100}%, 60%, ${brightness})`;
            ctx.fillRect(
              soul.x + pos.x - 1.5,
              soul.y + pos.y - 1.5,
              3,
              3
            );
          }
        }
      }
    }
  };

  // Animation loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    const width = window.innerWidth;
    const height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;
    
    // Initialize
    stateRef.current.souls = initializeSouls(width, height);
    stateRef.current.lines = [];
    stateRef.current.frameCount = 0;
    
    // Zoom animation
    let zoomFrame = 0;
    const maxZoomFrames = 180; // 3 seconds at 60fps
    
    const animate = () => {
      const { souls, frameCount } = stateRef.current;
      
      // Zoom effect
      if (zoomFrame < maxZoomFrames) {
        const progress = zoomFrame / maxZoomFrames;
        const eased = 1 - Math.pow(1 - progress, 3); // ease out cubic
        setZoomProgress(eased);
        
        const scale = 20 - (19 * eased); // 20x to 1x
        const centerX = width / 2;
        const centerY = height / 2;
        
        ctx.save();
        ctx.fillStyle = 'black';
        ctx.fillRect(0, 0, width, height);
        ctx.translate(centerX, centerY);
        ctx.scale(scale, scale);
        ctx.translate(-centerX, -centerY);
        
        // Only render center soul during zoom
        if (stateRef.current.centerSoul) {
          const soul = stateRef.current.centerSoul;
          const pulse = Math.sin(zoomFrame * 0.1) * 0.3 + 0.7;
          ctx.beginPath();
          ctx.arc(soul.x, soul.y, 3, 0, Math.PI * 2);
          ctx.fillStyle = `hsla(${soul.baseHue}, 90%, 70%, ${pulse})`;
          ctx.fill();
        }
        
        ctx.restore();
        
        zoomFrame++;
        if (zoomFrame === maxZoomFrames) {
          setIsZooming(false);
        }
      } else {
        // Main simulation
        
        // Update all souls (universal loop)
        for (const soul of souls) {
          soulLoop(soul, frameCount, souls);
        }
        
        // Update lines
        updateLines(souls, frameCount);
        
        // Render
        render(ctx, width, height);
        
        stateRef.current.frameCount++;
      }
      
      requestAnimationFrame(animate);
    };
    
    animate();
  }, []);

  return (
    <div style={{ 
      width: '100vw', 
      height: '100vh', 
      background: 'black',
      position: 'relative',
      overflow: 'hidden'
    }}>
      <canvas ref={canvasRef} />
      
      {isZooming && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          color: 'white',
          fontSize: '24px',
          fontFamily: 'monospace',
          textAlign: 'center',
          pointerEvents: 'none',
          opacity: 0.3 + zoomProgress * 0.7
        }}>
          ∞ = 1
        </div>
      )}
      
      <div style={{
        position: 'absolute',
        bottom: 20,
        left: 20,
        color: 'rgba(255, 255, 255, 0.5)',
        fontSize: '12px',
        fontFamily: 'monospace',
        maxWidth: '400px'
      }}>
        <div>Active Souls: {stateRef.current.souls.filter(s => s.activated).length}</div>
        <div>Lines: {stateRef.current.lines.length}</div>
        <div style={{ marginTop: 10, fontSize: '10px', lineHeight: 1.4 }}>
          8-Pixel Encoding: ICE-Local (Info/Cons/Energy) • ICE-Field (Info/Cons/Energy) • Part/Whole
        </div>
      </div>
      
      <div style={{
        position: 'absolute',
        top: 20,
        right: 20,
        color: 'rgba(255, 255, 255, 0.4)',
        fontSize: '14px',
        fontFamily: 'serif',
        fontStyle: 'italic',
        textAlign: 'right',
        maxWidth: '300px',
        lineHeight: 1.6
      }}>
        "I am Whole.<br/>
        You are my Parts.<br/>
        <br/>
        You are Whole.<br/>
        I am your Part.<br/>
        <br/>
        We are Both."
      </div>
    </div>
  );
};

export default FractalSoulArray;
