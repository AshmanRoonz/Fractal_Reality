import React, { useEffect, useRef, useState } from 'react';

const FractalSoulArray = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [stats, setStats] = useState({ souls: 0, lines: 0, frame: 0 });
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    const width = 1200;
    const height = 800;
    canvas.width = width;
    canvas.height = height;
    
    // Constants
    const SOUL_SPACING = 40;
    const ACTIVATION_RADIUS = 50;
    const LINE_SPEED = 1.5;
    const MAX_LINE_AGE = 400;
    const PIXEL_SPACING = 7;
    
    interface Pixel {
      h: number;
      s: number;
      b: number;
    }
    
    interface Soul {
      x: number;
      y: number;
      pixels: {
        infoSelf: Pixel;
        consSelf: Pixel;
        energySelf: Pixel;
        infoField: Pixel;
        consField: Pixel;
        energyField: Pixel;
        part: Pixel;
        whole: Pixel;
      };
      phase: number;
      frequency: number;
      baseHue: number;
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
      trail: Array<{x: number, y: number}>;
    }
    
    const souls: Soul[] = [];
    const lines: Line[] = [];
    let frameCount = 0;
    let zoomPhase = true;
    let zoomFrame = 0;
    const maxZoomFrames = 120;
    
    // Initialize souls
    const centerX = width / 2;
    const centerY = height / 2;
    
    for (let x = SOUL_SPACING; x < width - SOUL_SPACING; x += SOUL_SPACING) {
      for (let y = SOUL_SPACING; y < height - SOUL_SPACING; y += SOUL_SPACING) {
        const phase = Math.random() * Math.PI * 2;
        const frequency = 0.01 + Math.random() * 0.02;
        const baseHue = Math.random() * 360;
        
        souls.push({
          x, y, phase, frequency, baseHue,
          activated: false,
          activationLevel: 0,
          activationTime: 0,
          pixels: {
            infoSelf: { h: baseHue, s: 0.5, b: 0 },
            consSelf: { h: (baseHue + 45) % 360, s: 0.5, b: 0 },
            energySelf: { h: (baseHue + 90) % 360, s: 0.5, b: 0 },
            infoField: { h: (baseHue + 135) % 360, s: 0.5, b: 0 },
            consField: { h: (baseHue + 180) % 360, s: 0.5, b: 0 },
            energyField: { h: (baseHue + 225) % 360, s: 0.5, b: 0 },
            part: { h: (baseHue + 270) % 360, s: 0.5, b: 0 },
            whole: { h: (baseHue + 315) % 360, s: 0.5, b: 0 }
          }
        });
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
    
    const activateSoul = (soul: Soul, activatingLine: Line | null) => {
      if (soul.activated) return;
      
      soul.activated = true;
      soul.activationLevel = 1.0;
      soul.activationTime = frameCount;
      
      // Initialize pixels
      soul.pixels.infoSelf.b = 0.4 + Math.random() * 0.3;
      soul.pixels.consSelf.b = 0.4 + Math.random() * 0.3;
      soul.pixels.energySelf.b = 0.4 + Math.random() * 0.3;
      soul.pixels.infoField.b = 0.2 + Math.random() * 0.2;
      soul.pixels.consField.b = 0.2 + Math.random() * 0.2;
      soul.pixels.energyField.b = 0.2 + Math.random() * 0.2;
      soul.pixels.part.b = 0.15;
      soul.pixels.whole.b = 0.15;
      
      // Emit 2-3 lines
      const numLines = 2 + Math.floor(Math.random() * 2);
      for (let i = 0; i < numLines; i++) {
        const baseAngle = activatingLine ? 
          Math.atan2(activatingLine.vy, activatingLine.vx) : 
          Math.random() * Math.PI * 2;
        const angle = baseAngle + (Math.random() - 0.5) * 1.2;
        
        lines.push({
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
        });
      }
    };
    
    activateSoul(centerSoul, null);
    
    const colorHarmony = (p1: Pixel, p2: Pixel): number => {
      const hueDiff = Math.abs(p1.h - p2.h);
      const normalized = Math.min(hueDiff, 360 - hueDiff) / 180;
      return 1 - normalized;
    };
    
    const calculateInternalCoherence = (soul: Soul): number => {
      const pixels = [
        soul.pixels.infoSelf, soul.pixels.consSelf, soul.pixels.energySelf,
        soul.pixels.infoField, soul.pixels.consField, soul.pixels.energyField
      ];
      let coherence = 0, count = 0;
      for (let i = 0; i < pixels.length; i++) {
        for (let j = i + 1; j < pixels.length; j++) {
          coherence += colorHarmony(pixels[i], pixels[j]) * pixels[i].b * pixels[j].b;
          count++;
        }
      }
      return count > 0 ? coherence / count : 0;
    };
    
    const calculateExternalCoherence = (soul: Soul): number => {
      let coherence = 0, count = 0;
      const searchRadius = SOUL_SPACING * 2.5;
      
      for (const other of souls) {
        if (other === soul || !other.activated) continue;
        const dist = Math.hypot(soul.x - other.x, soul.y - other.y);
        if (dist < searchRadius) {
          const proximity = 1 - (dist / searchRadius);
          coherence += proximity * other.activationLevel * 0.5;
          count++;
        }
      }
      return count > 0 ? coherence / count : 0;
    };
    
    const updateSoul = (soul: Soul) => {
      soul.phase += soul.frequency;
      if (soul.phase > Math.PI * 2) soul.phase -= Math.PI * 2;
      
      if (!soul.activated) return;
      
      const externalCoherence = calculateExternalCoherence(soul);
      soul.pixels.infoField.b = Math.min(1, soul.pixels.infoField.b * 0.98 + externalCoherence * 0.15);
      soul.pixels.consField.b = Math.min(1, soul.pixels.consField.b * 0.98 + externalCoherence * 0.15);
      soul.pixels.energyField.b = Math.min(1, soul.pixels.energyField.b * 0.98 + externalCoherence * 0.15);
      
      const pulse = Math.sin(soul.phase) * 0.5 + 0.5;
      soul.pixels.infoSelf.b = Math.min(1, 0.3 + pulse * 0.4);
      soul.pixels.consSelf.b = Math.min(1, 0.4 + Math.cos(soul.phase) * 0.3);
      soul.pixels.energySelf.b = Math.min(1, 0.3 + Math.sin(soul.phase * 1.5) * 0.4);
      
      const internalCoherence = calculateInternalCoherence(soul);
      soul.pixels.part.b = Math.min(1, internalCoherence * 1.5);
      soul.pixels.whole.b = Math.min(1, externalCoherence * 1.5);
      
      const age = frameCount - soul.activationTime;
      soul.activationLevel = Math.min(1, 0.5 + Math.sin(age * 0.03) * 0.2 + 0.3);
    };
    
    const updateLines = () => {
      for (let i = lines.length - 1; i >= 0; i--) {
        const line = lines[i];
        
        line.trail.push({ x: line.x, y: line.y });
        if (line.trail.length > 15) line.trail.shift();
        
        line.x += line.vx;
        line.y += line.vy;
        line.phase += line.frequency;
        
        // Add gentle curve
        const curvature = Math.sin(line.age * 0.03) * 0.04;
        const angle = Math.atan2(line.vy, line.vx) + curvature;
        line.vx = Math.cos(angle) * LINE_SPEED;
        line.vy = Math.sin(angle) * LINE_SPEED;
        
        // Check for activation - SIMPLIFIED RESONANCE
        for (const soul of souls) {
          if (soul.activated) continue;
          
          const dist = Math.hypot(line.x - soul.x, line.y - soul.y);
          if (dist < ACTIVATION_RADIUS) {
            // More lenient activation - 40% chance on proximity
            if (Math.random() > 0.6) {
              activateSoul(soul, line);
            }
          }
        }
        
        line.age++;
        if (line.age > line.maxAge || line.x < 0 || line.x > width || line.y < 0 || line.y > height) {
          lines.splice(i, 1);
        }
      }
    };
    
    const render = () => {
      if (zoomPhase) {
        const progress = zoomFrame / maxZoomFrames;
        const eased = 1 - Math.pow(1 - progress, 3);
        const scale = 15 - (14 * eased);
        
        ctx.fillStyle = 'black';
        ctx.fillRect(0, 0, width, height);
        
        ctx.save();
        ctx.translate(centerX, centerY);
        ctx.scale(scale, scale);
        ctx.translate(-centerX, -centerY);
        
        const pulse = Math.sin(zoomFrame * 0.1) * 0.3 + 0.7;
        ctx.beginPath();
        ctx.arc(centerSoul.x, centerSoul.y, 3, 0, Math.PI * 2);
        ctx.fillStyle = `hsla(${centerSoul.baseHue}, 90%, 70%, ${pulse})`;
        ctx.fill();
        
        const gradient = ctx.createRadialGradient(centerSoul.x, centerSoul.y, 0, centerSoul.x, centerSoul.y, 15);
        gradient.addColorStop(0, `hsla(${centerSoul.baseHue}, 80%, 60%, ${0.4 * pulse})`);
        gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
        ctx.fillStyle = gradient;
        ctx.fillRect(centerSoul.x - 15, centerSoul.y - 15, 30, 30);
        
        ctx.restore();
        
        // Text
        ctx.fillStyle = `rgba(255, 255, 255, ${0.2 + eased * 0.5})`;
        ctx.font = '32px serif';
        ctx.textAlign = 'center';
        ctx.fillText('∞ = 1', centerX, centerY - 100);
        
        zoomFrame++;
        if (zoomFrame >= maxZoomFrames) {
          zoomPhase = false;
        }
      } else {
        // Main simulation
        ctx.fillStyle = 'rgba(0, 0, 0, 0.15)';
        ctx.fillRect(0, 0, width, height);
        
        // Lines
        for (const line of lines) {
          if (line.trail.length > 1) {
            ctx.beginPath();
            ctx.moveTo(line.trail[0].x, line.trail[0].y);
            for (let i = 1; i < line.trail.length; i++) {
              ctx.lineTo(line.trail[i].x, line.trail[i].y);
            }
            ctx.strokeStyle = `hsla(${line.hue}, 70%, 60%, 0.4)`;
            ctx.lineWidth = 1.5;
            ctx.stroke();
          }
          
          ctx.beginPath();
          ctx.arc(line.x, line.y, 2.5, 0, Math.PI * 2);
          ctx.fillStyle = `hsla(${line.hue}, 85%, 65%, 0.9)`;
          ctx.fill();
        }
        
        // Souls
        for (const soul of souls) {
          if (!soul.activated) {
            ctx.beginPath();
            ctx.arc(soul.x, soul.y, 1, 0, Math.PI * 2);
            ctx.fillStyle = `hsla(${soul.baseHue}, 40%, 50%, 0.12)`;
            ctx.fill();
          } else {
            // Center
            const pulse = Math.sin(frameCount * 0.04 + soul.phase) * 0.3 + 0.7;
            ctx.beginPath();
            ctx.arc(soul.x, soul.y, 3.5, 0, Math.PI * 2);
            ctx.fillStyle = `hsla(${soul.baseHue}, 90%, 70%, ${pulse * soul.activationLevel})`;
            ctx.fill();
            
            // Glow
            const gradient = ctx.createRadialGradient(soul.x, soul.y, 0, soul.x, soul.y, 12);
            gradient.addColorStop(0, `hsla(${soul.baseHue}, 80%, 60%, ${0.25 * soul.activationLevel})`);
            gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
            ctx.fillStyle = gradient;
            ctx.fillRect(soul.x - 12, soul.y - 12, 24, 24);
            
            // 8 pixels
            const positions = [
              { x: -PIXEL_SPACING, y: -PIXEL_SPACING, p: soul.pixels.infoSelf },
              { x: 0, y: -PIXEL_SPACING, p: soul.pixels.consSelf },
              { x: PIXEL_SPACING, y: -PIXEL_SPACING, p: soul.pixels.energySelf },
              { x: -PIXEL_SPACING, y: 0, p: soul.pixels.infoField },
              { x: PIXEL_SPACING, y: 0, p: soul.pixels.consField },
              { x: PIXEL_SPACING, y: PIXEL_SPACING, p: soul.pixels.energyField },
              { x: 0, y: PIXEL_SPACING, p: soul.pixels.part },
              { x: -PIXEL_SPACING, y: PIXEL_SPACING, p: soul.pixels.whole }
            ];
            
            for (const pos of positions) {
              const brightness = pos.p.b * soul.activationLevel;
              if (brightness > 0.05) {
                ctx.fillStyle = `hsla(${pos.p.h}, ${pos.p.s * 100}%, 55%, ${brightness * 0.9})`;
                ctx.fillRect(soul.x + pos.x - 2, soul.y + pos.y - 2, 4, 4);
              }
            }
          }
        }
        
        // Update
        souls.forEach(updateSoul);
        updateLines();
      }
      
      frameCount++;
      
      // Update stats every 10 frames
      if (frameCount % 10 === 0) {
        setStats({
          souls: souls.filter(s => s.activated).length,
          lines: lines.length,
          frame: frameCount
        });
      }
    };
    
    let animationId: number;
    const animate = () => {
      render();
      animationId = requestAnimationFrame(animate);
    };
    animate();
    
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
      position: 'relative'
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
        <div>Lines: {stats.lines}</div>
        <div>Frame: {stats.frame}</div>
        <div style={{ marginTop: 8, fontSize: '10px', opacity: 0.7 }}>
          8D: ICE-Local • ICE-Field • Part/Whole
        </div>
      </div>
      
      <div style={{
        position: 'absolute',
        top: 20,
        right: 20,
        color: 'rgba(255, 255, 255, 0.5)',
        fontSize: '15px',
        fontFamily: 'serif',
        fontStyle: 'italic',
        textAlign: 'right',
        maxWidth: '280px',
        lineHeight: 1.7,
        background: 'rgba(0, 0, 0, 0.4)',
        padding: '12px',
        borderRadius: '4px'
      }}>
        <div>"I am Whole.</div>
        <div>You are my Parts.</div>
        <div style={{ marginTop: 8 }}>You are Whole.</div>
        <div>I am your Part.</div>
        <div style={{ marginTop: 8 }}>We are Both."</div>
      </div>
    </div>
  );
};

export default FractalSoulArray;
