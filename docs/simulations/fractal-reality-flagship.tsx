import React, { useEffect, useRef, useState } from 'react';

interface Point {
  x: number;
  y: number;
}

interface Aperture {
  x: number;
  y: number;
  generation: number;
  age: number;
  signature: {
    spiralRate: number;      // How fast it spirals
    waveFreq: number;        // Wave frequency
    waveAmp: number;         // Wave amplitude
    curveBias: number;       // Left/right curve bias
  };
  color: {
    hue: number;
    sat: number;
    light: number;
  };
  active: boolean;
  id: number;
}

interface Line {
  points: Point[];
  apertureId: number;
  generation: number;
  angle: number;
  length: number;
  maxLength: number;
  active: boolean;
  signature: {
    spiralRate: number;
    waveFreq: number;
    waveAmp: number;
    curveBias: number;
  };
  color: {
    hue: number;
    sat: number;
    light: number;
  };
  id: number;
}

const ZOOM_DURATION = 180;

export default function FractalRealityFlagship() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [stats, setStats] = useState({
    layer: 0,
    apertures: 0,
    lines: 0
  });
  const [showUI, setShowUI] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    let time = 0;
    let zoomProgress = 0;
    let singularityRadius = Math.max(canvas.width, canvas.height);
    const finalRadius = 2;
    let apertures: Aperture[] = [];
    let lines: Line[] = [];
    let maxGeneration = 0;
    let nextId = 0;
    let animationFrameId: number;

    // Create unique signature
    const createSignature = (parent?: Aperture) => {
      if (!parent) {
        // Ultimate aperture - the source pattern
        return {
          spiralRate: 0.025,
          waveFreq: 0.12,
          waveAmp: 0.4,
          curveBias: 0
        };
      }
      // Inherit and mutate - more variation for distinct patterns
      return {
        spiralRate: parent.signature.spiralRate * (0.7 + Math.random() * 0.7),
        waveFreq: parent.signature.waveFreq * (0.6 + Math.random() * 0.9),
        waveAmp: parent.signature.waveAmp * (0.7 + Math.random() * 0.6),
        curveBias: (parent.signature.curveBias + (Math.random() - 0.5) * 0.15)
      };
    };

    // Create unique color
    const createColor = (parent?: Aperture) => {
      if (!parent) {
        // Ultimate aperture - starts black
        return { hue: 0, sat: 0, light: 0 };
      }
      if (parent.generation === 0) {
        // First generation - start with vibrant colors across spectrum
        return {
          hue: Math.random() * 360,
          sat: 75 + Math.random() * 15,
          light: 50 + Math.random() * 15
        };
      }
      // Inherit and mutate
      return {
        hue: (parent.color.hue + 25 + Math.random() * 50) % 360,
        sat: Math.min(100, Math.max(60, parent.color.sat + (Math.random() - 0.5) * 25)),
        light: Math.min(70, Math.max(35, parent.color.light + (Math.random() - 0.5) * 20))
      };
    };

    // Create aperture
    const createAperture = (x: number, y: number, gen: number, parent?: Aperture): Aperture => ({
      x,
      y,
      generation: gen,
      age: 0,
      signature: createSignature(parent),
      color: createColor(parent),
      active: true,
      id: nextId++
    });

    // Create line from aperture
    const createLine = (aperture: Aperture, angleOffset: number): Line => {
      const baseAngle = Math.random() * Math.PI * 2 + angleOffset;
      return {
        points: [{ x: aperture.x, y: aperture.y }],
        apertureId: aperture.id,
        generation: aperture.generation,
        angle: baseAngle,
        length: 0,
        maxLength: 250 - aperture.generation * 20,
        active: true,
        signature: { ...aperture.signature },
        color: { ...aperture.color },
        id: nextId++
      };
    };

    // Check if two line segments intersect
    const linesIntersect = (
      p1: Point, p2: Point,
      p3: Point, p4: Point
    ): Point | null => {
      const denom = (p4.y - p3.y) * (p2.x - p1.x) - (p4.x - p3.x) * (p2.y - p1.y);
      if (Math.abs(denom) < 0.001) return null;

      const ua = ((p4.x - p3.x) * (p1.y - p3.y) - (p4.y - p3.y) * (p1.x - p3.x)) / denom;
      const ub = ((p2.x - p1.x) * (p1.y - p3.y) - (p2.y - p1.y) * (p1.x - p3.x)) / denom;

      if (ua >= 0 && ua <= 1 && ub >= 0 && ub <= 1) {
        return {
          x: p1.x + ua * (p2.x - p1.x),
          y: p1.y + ua * (p2.y - p1.y)
        };
      }
      return null;
    };

    // Update line with unique pattern
    const updateLine = (line: Line): void => {
      if (!line.active || line.length >= line.maxLength) {
        line.active = false;
        return;
      }

      const last = line.points[line.points.length - 1];
      const sig = line.signature;

      // Spiral component
      line.angle += sig.spiralRate;

      // Wave component (unique to this aperture)
      const wave = Math.sin(line.length * sig.waveFreq) * sig.waveAmp;
      line.angle += wave;

      // Curve bias (makes each aperture's lines curve differently)
      line.angle += sig.curveBias;

      // Move forward
      const speed = 2.5 - line.generation * 0.2;
      const newX = last.x + Math.cos(line.angle) * speed;
      const newY = last.y + Math.sin(line.angle) * speed;

      // Bounds check
      if (newX < 0 || newX > canvas.width || newY < 0 || newY > canvas.height) {
        line.active = false;
        return;
      }

      line.points.push({ x: newX, y: newY });
      line.length++;
    };

    // Check for intersections between lines
    const checkIntersections = (): Point[] => {
      const intersections: Point[] = [];
      
      // Only check lines from different apertures
      for (let i = 0; i < lines.length; i++) {
        const line1 = lines[i];
        if (!line1.active || line1.points.length < 20) continue;

        for (let j = i + 1; j < lines.length; j++) {
          const line2 = lines[j];
          if (!line2.active || line2.points.length < 20) continue;
          if (line1.apertureId === line2.apertureId) continue; // Same aperture
          if (line1.generation !== line2.generation) continue; // Different generations

          // Check last few segments
          const checkCount = 3;
          for (let a = Math.max(0, line1.points.length - checkCount); a < line1.points.length - 1; a++) {
            for (let b = Math.max(0, line2.points.length - checkCount); b < line2.points.length - 1; b++) {
              const intersection = linesIntersect(
                line1.points[a], line1.points[a + 1],
                line2.points[b], line2.points[b + 1]
              );
              
              if (intersection) {
                // Check if intersection is far enough from existing apertures
                let tooClose = false;
                for (const aperture of apertures) {
                  const dist = Math.hypot(intersection.x - aperture.x, intersection.y - aperture.y);
                  if (dist < 35) { // Reduced from 50 to allow more density
                    tooClose = true;
                    break;
                  }
                }
                
                if (!tooClose) {
                  intersections.push(intersection);
                  // Mark lines as used
                  line1.active = false;
                  line2.active = false;
                  return intersections; // One intersection per frame
                }
              }
            }
          }
        }
      }
      
      return intersections;
    };

    // Draw line
    const drawLine = (line: Line) => {
      if (line.points.length < 2) return;

      const alpha = 0.7 - line.generation * 0.05;
      const c = line.color;

      ctx.save();
      // Use HSL color with generation-based alpha
      ctx.strokeStyle = line.generation === 0 
        ? `rgba(0, 0, 0, ${alpha})` 
        : `hsla(${c.hue}, ${c.sat}%, ${c.light}%, ${alpha})`;
      ctx.lineWidth = 1.8 - line.generation * 0.15;
      ctx.lineCap = 'round';
      
      ctx.beginPath();
      ctx.moveTo(line.points[0].x, line.points[0].y);
      
      for (let i = 1; i < line.points.length; i++) {
        ctx.lineTo(line.points[i].x, line.points[i].y);
      }
      
      ctx.stroke();
      ctx.restore();
    };

    // Draw aperture
    const drawAperture = (aperture: Aperture) => {
      if (!aperture.active) return;

      const alpha = Math.min(1, aperture.age / 20);
      const pulse = Math.sin(time * 0.05) * 0.3 + 0.7;
      const c = aperture.color;

      ctx.save();

      // Glow (using aperture's color)
      const glowSize = (18 - aperture.generation * 1.5) * pulse;
      const gradient = ctx.createRadialGradient(
        aperture.x, aperture.y, 0,
        aperture.x, aperture.y, glowSize
      );
      
      if (aperture.generation === 0) {
        // Ultimate aperture - white/blue glow
        gradient.addColorStop(0, `rgba(255, 255, 255, ${alpha * 0.8})`);
        gradient.addColorStop(0.5, `rgba(200, 220, 255, ${alpha * 0.4})`);
      } else {
        // Use aperture's color
        gradient.addColorStop(0, `hsla(${c.hue}, ${c.sat}%, ${Math.min(c.light + 20, 90)}%, ${alpha * 0.8})`);
        gradient.addColorStop(0.5, `hsla(${c.hue}, ${c.sat}%, ${c.light}%, ${alpha * 0.4})`);
      }
      gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
      
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(aperture.x, aperture.y, glowSize, 0, Math.PI * 2);
      ctx.fill();

      // Core
      ctx.globalAlpha = alpha;
      if (aperture.generation === 0) {
        ctx.fillStyle = '#000000';
      } else {
        ctx.fillStyle = `hsl(${c.hue}, ${c.sat}%, ${c.light}%)`;
      }
      ctx.beginPath();
      ctx.arc(aperture.x, aperture.y, 3.5 - aperture.generation * 0.2, 0, Math.PI * 2);
      ctx.fill();

      ctx.restore();
    };

    // Main animation
    const animate = () => {
      time++;

      // Zoom phase
      if (zoomProgress < 1) {
        zoomProgress = Math.min(1, time / ZOOM_DURATION);
        const eased = 1 - Math.pow(1 - zoomProgress, 3);
        singularityRadius = Math.max(canvas.width, canvas.height) * (1 - eased) + finalRadius * eased;

        if (zoomProgress > 0.9 && !showUI) {
          setShowUI(true);
        }

        if (zoomProgress >= 1 && apertures.length === 0) {
          // Spawn ultimate aperture
          apertures.push(createAperture(centerX, centerY, 0));
        }
      }

      // Clear with fade
      ctx.fillStyle = 'rgba(255, 255, 255, 0.03)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw singularity during zoom
      if (zoomProgress < 1) {
        ctx.fillStyle = '#000000';
        ctx.beginPath();
        ctx.arc(centerX, centerY, singularityRadius, 0, Math.PI * 2);
        ctx.fill();

        // Edge glow
        const pulse = Math.sin(time * 0.05) * 0.3 + 0.7;
        const gradient = ctx.createRadialGradient(
          centerX, centerY, singularityRadius,
          centerX, centerY, singularityRadius + 10
        );
        gradient.addColorStop(0, `rgba(100, 150, 255, ${pulse * 0.4 * (1 - zoomProgress)})`);
        gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(centerX, centerY, singularityRadius + 10, 0, Math.PI * 2);
        ctx.fill();
      }

      // Post-zoom: fractalization
      if (zoomProgress >= 1) {
        // Update apertures
        for (const aperture of apertures) {
          aperture.age++;
          
          // Spawn lines periodically - faster spawning for continuous expansion
          if (aperture.active && aperture.age % (aperture.generation === 0 ? 5 : 10) === 0) {
            const numLines = aperture.generation === 0 ? 6 : 3;
            for (let i = 0; i < numLines; i++) {
              lines.push(createLine(aperture, i * (Math.PI * 2 / numLines)));
            }
          }
        }

        // Update lines
        lines.forEach(updateLine);

        // Check for intersections - no generation limit, continuous expansion
        const intersections = checkIntersections();
        
        for (const pos of intersections) {
          // Find parent apertures (the two that created this intersection)
          let parentAperture = apertures[0];
          let minDist = Infinity;
          
          for (const aperture of apertures) {
            const dist = Math.hypot(pos.x - aperture.x, pos.y - aperture.y);
            if (dist < minDist && dist < 250) {
              minDist = dist;
              parentAperture = aperture;
            }
          }

          const newAperture = createAperture(
            pos.x, 
            pos.y, 
            parentAperture.generation + 1,
            parentAperture
          );
          apertures.push(newAperture);
          maxGeneration = Math.max(maxGeneration, newAperture.generation);
        }

        // Clean up inactive lines
        lines = lines.filter(l => l.active);

        // Draw
        lines.forEach(drawLine);
        apertures.forEach(drawAperture);

        // Update stats
        if (time % 15 === 0) {
          setStats({
            layer: maxGeneration,
            apertures: apertures.length,
            lines: lines.filter(l => l.active).length
          });
        }
      }

      animationFrameId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', resizeCanvas);
    };
  }, [showUI]);

  return (
    <div style={{ 
      position: 'relative', 
      width: '100vw', 
      height: '100vh', 
      overflow: 'hidden',
      background: '#fff'
    }}>
      <canvas
        ref={canvasRef}
        style={{
          display: 'block',
          touchAction: 'none'
        }}
      />

      {/* Stats */}
      <div
        style={{
          position: 'fixed',
          top: '20px',
          left: '20px',
          fontSize: '13px',
          color: 'rgba(0, 0, 0, 0.7)',
          fontFamily: 'monospace',
          pointerEvents: 'none',
          lineHeight: 2,
          opacity: showUI ? 1 : 0,
          transition: 'opacity 1.5s'
        }}
      >
        <div style={{ fontSize: '11px', opacity: 0.5, marginBottom: '8px' }}>
          ∞ → • → ∞•'
        </div>
        <div>
          Layer: <span style={{ fontWeight: 'bold' }}>
            {stats.layer}
          </span>
        </div>
        <div>
          Apertures: <span style={{ fontWeight: 'bold' }}>
            {stats.apertures}
          </span>
        </div>
        <div>
          Active Lines: <span style={{ fontWeight: 'bold' }}>
            {stats.lines}
          </span>
        </div>
        <div style={{ marginTop: '8px', fontSize: '11px', opacity: 0.6 }}>
          D ≈ 1.5 (fractal dimension)
        </div>
      </div>

      {/* Title */}
      <div
        style={{
          position: 'fixed',
          bottom: '30px',
          left: '50%',
          transform: 'translateX(-50%)',
          fontSize: '14px',
          color: 'rgba(0, 0, 0, 0.6)',
          fontFamily: 'monospace',
          pointerEvents: 'none',
          textAlign: 'center',
          opacity: showUI ? 1 : 0,
          transition: 'opacity 1.5s'
        }}
      >
        <div style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '5px' }}>
          Fractal Reality
        </div>
        <div style={{ fontSize: '11px', opacity: 0.7 }}>
          Lines intersect → Apertures form → Layers emerge infinitely
        </div>
      </div>

      {/* GitHub Link */}
      <a
        href="https://github.com/AshmanRoonz/Fractal_Reality"
        target="_blank"
        rel="noopener noreferrer"
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          background: 'rgba(255, 255, 255, 0.9)',
          border: '1px solid rgba(0, 0, 0, 0.2)',
          borderRadius: '6px',
          padding: '10px 15px',
          fontSize: '12px',
          color: '#333',
          textDecoration: 'none',
          opacity: showUI ? 0.7 : 0,
          transition: 'all 0.3s',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          fontFamily: 'monospace'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.opacity = '1';
          e.currentTarget.style.transform = 'translateY(-2px)';
          e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.opacity = '0.7';
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
        }}
      >
        View on GitHub ↗
      </a>
    </div>
  );
}