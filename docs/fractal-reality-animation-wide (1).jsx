import React, { useEffect, useRef, useState } from 'react';

/**
 * Fractal Reality Animation - High Performance Edition (Wide Format)
 * 
 * Visualizes the journey: ∞ → • → ∞•'
 * 
 * Each fractalized dot generates its own unique fractal branching pattern.
 * The branching rules (angles, ratios) are determined by c-values
 * derived from its position, creating 64 unique fractal "signatures".
 * 
 * This represents how the infinite field (∞) fractalizes through the singularity (•)
 * into infinite unique patterns (∞•'), each with its own mathematical signature.
 * 
 * Features:
 * - 16×4 grid layout (64 dots) optimized for wide aspect ratio
 * - Recursive fractal branching (binary trees, depth 3)
 * - Vine-like connections between nearby fractals (12s-18s)
 * - Organic tendrils reaching and curling between fields
 * - Each vine connection has animated tendrils with curls at the tips
 * 
 * Performance optimizations:
 * - NO glow effects (shadowBlur) - major performance gain!
 * - NO expensive gradients - simple fills and strokes only
 * - Fractal branching: 4 initial directions, binary branching, depth 3
 * - Each dot: ~28 cached lines (4 * 2^3 = 32 branches total)
 * - Total: 64 dots × 28 lines = ~1,800 lines (very reasonable!)
 * - Patterns absorbed quickly (no bouncing)
 * - Extended viewing: 2 seconds of full fractal display (16s-18s)
 * - Logo appears at 18s, text at 22s
 * - Total loop: 37 seconds
 * - Smooth 60fps on most hardware
 */

const FractalRealityAnimation = () => {
  const canvasRef = useRef(null);
  const [phase, setPhase] = useState(0);
  const animationRef = useRef(null);
  const startTimeRef = useRef(Date.now());

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const width = canvas.width = 1200;
    const height = canvas.height = 267;

    // Animation state
    let infinityX = 150;
    let singularityX = width - 150;
    let singularityY = height / 2;
    let dots = [];
    let patterns = [];
    let waveAmplitude = 0;
    let logoAlpha = 0;
    let textAlpha = 0;
    let bounceCount = 0;

    // Generate fractal dots in 16x4 grid
    const generateDots = () => {
      dots = [];
      const gridX = 16; // Wide grid
      const gridY = 4;  // Short grid
      const spacingX = width / (gridX + 1);
      const spacingY = height / (gridY + 1);
      
      for (let i = 0; i < gridX; i++) {
        for (let j = 0; j < gridY; j++) {
          // Unique c value for each dot's Mandelbrot set
          // Spread around interesting regions of parameter space
          const angle = (i * gridY + j) * Math.PI * 2 / (gridX * gridY);
          const radius = 0.3 + (Math.sin(i * 0.5) * 0.4);
          const cReal = -0.4 + Math.cos(angle) * radius;
          const cImag = Math.sin(angle) * radius;
          
          dots.push({
            x: spacingX * (i + 1),
            y: spacingY * (j + 1),
            targetX: spacingX * (i + 1),
            targetY: spacingY * (j + 1),
            currentX: singularityX,
            currentY: singularityY,
            color: `hsl(${(i * 360 / gridX + j * 30)}, 80%, 60%)`,
            phase: 0,
            fieldRadius: 0,
            hasPattern: false,
            patternAlpha: 0,
            cReal: cReal,
            cImag: cImag,
            fractalBranches: null // Will store pre-computed branching pattern
          });
        }
      }
    };

    // Draw infinity symbol (no glow)
    const drawInfinity = (x, y, size, alpha = 1) => {
      ctx.save();
      ctx.strokeStyle = `rgba(100, 200, 255, ${alpha})`;
      ctx.lineWidth = 3;
      
      ctx.beginPath();
      for (let t = 0; t < Math.PI * 2; t += 0.01) {
        const scale = size / (3 - Math.cos(2 * t));
        const px = x + scale * Math.cos(t);
        const py = y + scale * Math.sin(2 * t) / 2;
        if (t === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      }
      ctx.stroke();
      ctx.restore();
    };

    // Draw singularity dot (no glow)
    const drawSingularity = (x, y, radius, alpha = 1, pulse = 0) => {
      ctx.save();
      
      // Simple filled circle
      ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
      ctx.beginPath();
      ctx.arc(x, y, radius + pulse * 10, 0, Math.PI * 2);
      ctx.fill();
      
      // Thin colored ring
      ctx.strokeStyle = `rgba(200, 100, 255, ${alpha})`;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(x, y, (radius + pulse * 10) * 1.5, 0, Math.PI * 2);
      ctx.stroke();
      
      ctx.restore();
    };

    // Generate fractal branching pattern for a dot (REDUCED complexity)
    const generateFractalBranches = (dot) => {
      const branches = [];
      const maxDepth = 3; // Reduced from 5
      const initialLength = 20; // Smaller
      
      // Use c-values to determine branching characteristics
      const branchAngle = Math.PI / 4 + dot.cReal * 0.3; // Simpler angles
      const lengthRatio = 0.65 + Math.abs(dot.cImag) * 0.15;
      const branchCount = 2; // Fixed at 2 (binary branching)
      
      // Recursive fractal branching
      const createBranch = (x, y, angle, length, depth) => {
        if (depth > maxDepth || length < 3) return;
        
        const endX = x + Math.cos(angle) * length;
        const endY = y + Math.sin(angle) * length;
        
        branches.push({
          x1: x, y1: y,
          x2: endX, y2: endY,
          depth: depth,
          length: length
        });
        
        // Create exactly 2 sub-branches
        const newLength = length * lengthRatio;
        createBranch(endX, endY, angle - branchAngle, newLength, depth + 1);
        createBranch(endX, endY, angle + branchAngle, newLength, depth + 1);
      };
      
      // Start with only 4 directions from center (reduced from 6+)
      const directions = 4;
      for (let i = 0; i < directions; i++) {
        const angle = (i / directions) * Math.PI * 2;
        createBranch(0, 0, angle, initialLength, 0);
      }
      
      return branches;
    };

    // Draw fractal field using fine lines (SIMPLIFIED)
    const drawFractalField = (dot, time) => {
      if (!dot.hasPattern || dot.fieldRadius < 10) return;
      
      // Lazy generate branches
      if (!dot.fractalBranches) {
        dot.fractalBranches = generateFractalBranches(dot);
      }
      
      ctx.save();
      ctx.translate(dot.currentX, dot.currentY);
      
      const scale = dot.fieldRadius / 80; // Adjusted scale
      const rotation = time * 0.0003 * (1 + dot.cReal);
      ctx.rotate(rotation);
      
      // Draw all branches
      dot.fractalBranches.forEach(branch => {
        const alpha = dot.patternAlpha * (1 - branch.depth / 4) * 0.6;
        
        ctx.strokeStyle = dot.color.replace('60%)', `${60 - branch.depth * 8}%, ${alpha})`);
        ctx.lineWidth = Math.max(0.5, 1.5 - branch.depth * 0.4);
        
        ctx.beginPath();
        ctx.moveTo(branch.x1 * scale, branch.y1 * scale);
        ctx.lineTo(branch.x2 * scale, branch.y2 * scale);
        ctx.stroke();
      });
      
      // Simplified rings - only 2 instead of 4
      const rings = [0.5, 0.85];
      rings.forEach((ratio, idx) => {
        const r = dot.fieldRadius * ratio;
        const alpha = dot.patternAlpha * 0.25;
        const points = 16; // Reduced from 24
        
        ctx.strokeStyle = dot.color.replace('60%)', `50%, ${alpha})`);
        ctx.lineWidth = 0.5;
        
        ctx.beginPath();
        for (let i = 0; i <= points; i++) {
          const angle = (i / points) * Math.PI * 2;
          const wave = Math.sin(time * 0.001 + i * 0.3 + idx) * 1.5;
          const currentR = r + wave;
          const x = Math.cos(angle) * currentR;
          const y = Math.sin(angle) * currentR;
          
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.stroke();
      });
      
      ctx.restore();
    };

    // Draw fractalized dots (no glow)
    const drawDots = () => {
      dots.forEach(dot => {
        // Interpolate position
        dot.currentX += (dot.targetX - dot.currentX) * 0.05;
        dot.currentY += (dot.targetY - dot.currentY) * 0.05;

        // Draw fractal field
        drawFractalField(dot, Date.now());

        // Draw the dot itself (smaller, simpler)
        ctx.fillStyle = dot.color;
        ctx.beginPath();
        ctx.arc(dot.currentX, dot.currentY, 4, 0, Math.PI * 2);
        ctx.fill();

        // Simple ring
        ctx.strokeStyle = dot.color.replace('60%', '70%');
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(dot.currentX, dot.currentY, 6, 0, Math.PI * 2);
        ctx.stroke();
      });
    };

    // Draw breaking patterns (simplified)
    const drawBreakingPatterns = () => {
      patterns.forEach((p, idx) => {
        if (p.absorbed) return;

        const dx = p.targetDot.currentX - p.x;
        const dy = p.targetDot.currentY - p.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 30) {
          p.absorbed = true;
          p.targetDot.hasPattern = true;
          return;
        }

        p.x += p.vx;
        p.y += p.vy;

        const attractionForce = 0.15;
        p.vx += (dx / dist) * attractionForce;
        p.vy += (dy / dist) * attractionForce;

        p.alpha = Math.max(0, p.alpha - 0.008);

        if (p.alpha > 0) {
          ctx.save();
          ctx.globalAlpha = p.alpha;
          ctx.strokeStyle = `rgba(100, 200, 255, 1)`;
          ctx.lineWidth = 1.5;

          ctx.beginPath();
          p.points.forEach((point, i) => {
            const px = p.x + point.x * p.size;
            const py = p.y + point.y * p.size;
            if (i === 0) ctx.moveTo(px, py);
            else ctx.lineTo(px, py);
          });
          ctx.closePath();
          ctx.stroke();

          ctx.restore();
        }
      });
    };

    // Draw interference patterns (simplified)
    const drawInterferencePatterns = (time) => {
      ctx.save();
      
      for (let i = 0; i < dots.length; i++) {
        for (let j = i + 1; j < dots.length; j++) {
          const dot1 = dots[i];
          const dot2 = dots[j];
          
          if (!dot1.hasPattern || !dot2.hasPattern) continue;
          
          const dx = dot2.currentX - dot1.currentX;
          const dy = dot2.currentY - dot1.currentY;
          const dist = Math.sqrt(dx * dx + dy * dy);
          
          if (dist < 120) {
            const phase = Math.sin(time * 0.002 + i * 0.5 + j * 0.7);
            const alpha = (1 - dist / 120) * 0.15 * Math.abs(phase);
            
            ctx.strokeStyle = `rgba(150, 200, 255, ${alpha})`;
            ctx.lineWidth = 0.5;
            
            ctx.beginPath();
            ctx.moveTo(dot1.currentX, dot1.currentY);
            ctx.lineTo(dot2.currentX, dot2.currentY);
            ctx.stroke();
          }
        }
      }
      
      ctx.restore();
    };

    // Draw vine connections (organic tendrils between fractals)
    const drawVineConnections = (time) => {
      ctx.save();
      
      for (let i = 0; i < dots.length; i++) {
        for (let j = i + 1; j < dots.length; j++) {
          const dot1 = dots[i];
          const dot2 = dots[j];
          
          if (!dot1.hasPattern || !dot2.hasPattern) continue;
          
          const dx = dot2.currentX - dot1.currentX;
          const dy = dot2.currentY - dot1.currentY;
          const dist = Math.sqrt(dx * dx + dy * dy);
          
          if (dist < 100 && dist > 40) {
            const tendrils = 2;
            for (let t = 0; t < tendrils; t++) {
              const seed = i * 1000 + j * 100 + t;
              const phase = Math.sin(time * 0.0005 + seed * 0.1);
              const alpha = (1 - dist / 100) * 0.2 * (0.5 + phase * 0.5);
              
              ctx.strokeStyle = `rgba(120, 180, 255, ${alpha})`;
              ctx.lineWidth = 1;
              
              ctx.beginPath();
              const steps = 8;
              for (let s = 0; s <= steps; s++) {
                const progress = s / steps;
                const baseX = dot1.currentX + dx * progress;
                const baseY = dot1.currentY + dy * progress;
                
                const perpX = -dy / dist;
                const perpY = dx / dist;
                const wave = Math.sin(progress * Math.PI * 3 + time * 0.001 + seed) * 8;
                const curl = Math.sin(progress * Math.PI * 2 + time * 0.0015 + seed * 0.5) * 4;
                
                const px = baseX + perpX * (wave + curl);
                const py = baseY + perpY * (wave + curl);
                
                if (s === 0) ctx.moveTo(px, py);
                else ctx.lineTo(px, py);
              }
              ctx.stroke();
              
              const tipX = dot2.currentX + Math.cos(time * 0.001 + seed) * 5;
              const tipY = dot2.currentY + Math.sin(time * 0.001 + seed) * 5;
              
              ctx.beginPath();
              ctx.arc(tipX, tipY, 2, 0, Math.PI * 2);
              ctx.fillStyle = `rgba(120, 180, 255, ${alpha * 0.6})`;
              ctx.fill();
            }
          }
        }
      }
      
      ctx.restore();
    };

    // Draw Celtic trinity knot logo (Mathematics of Wholeness) - no glow
    const drawLogo = (alpha) => {
      const centerX = width / 2;
      const centerY = height / 2;
      const size = 180;

      ctx.save();
      ctx.globalAlpha = alpha;

      // Dashed boundary circle (Boundary - I)
      ctx.strokeStyle = `rgba(100, 200, 255, ${alpha})`;
      ctx.lineWidth = 2;
      ctx.setLineDash([10, 10]);
      ctx.beginPath();
      ctx.arc(centerX, centerY, size * 1.1, 0, Math.PI * 2);
      ctx.stroke();
      ctx.setLineDash([]);

      // Trinity Knot (Triquetra) - Field (∞)
      ctx.strokeStyle = `rgba(100, 220, 255, ${alpha})`;
      ctx.lineWidth = 8;
      ctx.lineCap = 'round';
      
      const R = size * 0.45;
      const h = R / Math.sqrt(3); 
      
      // Three circle centers forming equilateral triangle
      const centers = [
        { x: centerX, y: centerY - h },
        { x: centerX + R/2, y: centerY + h/2 },
        { x: centerX - R/2, y: centerY + h/2 }
      ];
      
      // Draw the three lens shapes (vesica piscis)
      
      // Lens 1: between circles 0 (top) and 1 (bottom-right)
      const a01_from0 = Math.atan2(centers[1].y - centers[0].y, centers[1].x - centers[0].x);
      const a01_from1 = Math.atan2(centers[0].y - centers[1].y, centers[0].x - centers[1].x);
      ctx.beginPath();
      ctx.arc(centers[0].x, centers[0].y, R, a01_from0 - Math.PI/3, a01_from0 + Math.PI/3);
      ctx.arc(centers[1].x, centers[1].y, R, a01_from1 - Math.PI/3, a01_from1 + Math.PI/3);
      ctx.closePath();
      ctx.stroke();
      
      // Lens 2: between circles 1 (bottom-right) and 2 (bottom-left)
      const a12_from1 = Math.atan2(centers[2].y - centers[1].y, centers[2].x - centers[1].x);
      const a12_from2 = Math.atan2(centers[1].y - centers[2].y, centers[1].x - centers[2].x);
      ctx.beginPath();
      ctx.arc(centers[1].x, centers[1].y, R, a12_from1 - Math.PI/3, a12_from1 + Math.PI/3);
      ctx.arc(centers[2].x, centers[2].y, R, a12_from2 - Math.PI/3, a12_from2 + Math.PI/3);
      ctx.closePath();
      ctx.stroke();
      
      // Lens 3: between circles 2 (bottom-left) and 0 (top)
      const a20_from2 = Math.atan2(centers[0].y - centers[2].y, centers[0].x - centers[2].x);
      const a20_from0 = Math.atan2(centers[2].y - centers[0].y, centers[2].x - centers[0].x);
      ctx.beginPath();
      ctx.arc(centers[2].x, centers[2].y, R, a20_from2 - Math.PI/3, a20_from2 + Math.PI/3);
      ctx.arc(centers[0].x, centers[0].y, R, a20_from0 - Math.PI/3, a20_from0 + Math.PI/3);
      ctx.closePath();
      ctx.stroke();

      // Center dot (Center - C) - simple bright circle
      ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
      ctx.beginPath();
      ctx.arc(centerX, centerY, 12, 0, Math.PI * 2);
      ctx.fill();
      
      // Center dot outline
      ctx.strokeStyle = `rgba(150, 220, 255, ${alpha})`;
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.restore();
    };

    // Draw final text (no glow, positioned left and right of logo)
    const drawText = (alpha) => {
      ctx.save();
      ctx.globalAlpha = alpha;
      
      // Main title - positioned to the left of logo
      ctx.font = 'bold 36px Arial';
      ctx.fillStyle = 'rgba(100, 220, 255, 1)';
      ctx.textAlign = 'right';
      ctx.textBaseline = 'middle';
      ctx.fillText('FractalReality.ca', width / 2 - 220, height / 2);
      
      // Subtitle - positioned to the right of logo
      ctx.font = 'italic 24px Arial';
      ctx.fillStyle = 'rgba(100, 200, 255, 0.8)';
      ctx.textAlign = 'left';
      ctx.fillText('by Ashman Roonz', width / 2 + 220, height / 2);
      
      ctx.restore();
    };

    // Main animation loop
    const animate = () => {
      const elapsed = (Date.now() - startTimeRef.current) / 1000;

      // Clear canvas with fade effect
      ctx.fillStyle = 'rgba(10, 10, 20, 0.15)';
      ctx.fillRect(0, 0, width, height);

      // Phase 0: Initial state (0-2s)
      if (elapsed < 2) {
        drawInfinity(infinityX, height / 2, 60);
        drawSingularity(singularityX, singularityY, 20);
      }
      // Phase 1: Infinity flies toward singularity (2-4s)
      else if (elapsed < 4) {
        const t = (elapsed - 2) / 2;
        infinityX = 150 + (singularityX - 150 - 100) * t;
        drawInfinity(infinityX, height / 2, 60);
        drawSingularity(singularityX, singularityY, 20, 1, Math.sin(t * Math.PI * 4) * 0.5 + 0.5);
      }
      // Phase 2: Bounce back (4-5s)
      else if (elapsed < 5) {
        const t = (elapsed - 4);
        bounceCount++;
        if (bounceCount < 3) {
          infinityX = singularityX - 100 - Math.abs(Math.sin(t * Math.PI * 3)) * 50;
        } else {
          infinityX = singularityX - 100 + t * 100;
        }
        drawInfinity(infinityX, height / 2, 60, 1 - t * 0.3);
        drawSingularity(singularityX, singularityY, 20, 1, Math.sin(t * Math.PI * 8));
      }
      // Phase 3: Singularity fractalizes (5-7s)
      else if (elapsed < 7) {
        if (dots.length === 0) generateDots();
        const t = (elapsed - 5) / 2;
        drawSingularity(singularityX, singularityY, 20, 1 - t);
        drawDots();
      }
      // Phase 4: Infinity breaks into patterns (7-8.5s) - SHORTENED
      else if (elapsed < 8.5) {
        if (patterns.length === 0) {
          for (let i = 0; i < 100; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = Math.random() * 5 + 2;
            patterns.push({
              x: infinityX,
              y: height / 2,
              vx: Math.cos(angle) * speed,
              vy: Math.sin(angle) * speed,
              alpha: 1,
              size: Math.random() * 8 + 4,
              targetDot: dots[Math.floor(Math.random() * dots.length)],
              points: Array.from({ length: 3 }, () => ({
                x: Math.cos(Math.random() * Math.PI * 2),
                y: Math.sin(Math.random() * Math.PI * 2)
              }))
            });
          }
        }
        drawDots();
        drawBreakingPatterns();
      }
      // Phase 5: Patterns absorbed, fields emerge (8.5-16s) - ADJUSTED
      else if (elapsed < 16) {
        const t = (elapsed - 8.5) / 7.5;
        dots.forEach(dot => {
          if (!dot.hasPattern && Math.random() < 0.02) {
            dot.hasPattern = true;
          }
          if (dot.hasPattern) {
            dot.fieldRadius = Math.min(dot.fieldRadius + 1.5, 100);
            dot.patternAlpha = Math.min(dot.patternAlpha + 0.015, 1);
          }
        });
        drawDots();
        drawBreakingPatterns();
        drawInterferencePatterns(Date.now());
        
        if (elapsed > 12) {
          drawVineConnections(Date.now());
        }
      }
      // Phase 6: Interference patterns fully harmonized (16-18s) - SHORTENED
      else if (elapsed < 18) {
        dots.forEach(dot => {
          dot.hasPattern = true;
          dot.fieldRadius = Math.min(dot.fieldRadius + 0.5, 100);
          dot.patternAlpha = 1;
        });
        drawDots();
        drawInterferencePatterns(Date.now());
        drawVineConnections(Date.now());
      }
      // Phase 7: Logo starts to emerge (18-22s) - 5s EARLIER
      else if (elapsed < 22) {
        const t = (elapsed - 18) / 4;
        logoAlpha = t;
        dots.forEach(dot => {
          dot.hasPattern = true;
          dot.fieldRadius = 100;
          dot.patternAlpha = 1 - t * 0.3;
        });
        drawDots();
        drawInterferencePatterns(Date.now());
        drawLogo(logoAlpha);
      }
      // Phase 8: Text appears (22-26s) - 5s EARLIER
      else if (elapsed < 26) {
        const t = (elapsed - 22) / 4;
        textAlpha = t;
        dots.forEach(dot => {
          dot.patternAlpha = 0.7 - t * 0.5;
        });
        drawDots();
        drawInterferencePatterns(Date.now());
        drawLogo(logoAlpha);
        drawText(textAlpha);
      }
      // Phase 9: Hold final state (26-37s) - EXTENDED
      else if (elapsed < 37) {
        dots.forEach(dot => {
          dot.patternAlpha = 0.2;
        });
        drawDots();
        drawInterferencePatterns(Date.now());
        drawLogo(logoAlpha);
        drawText(textAlpha);
      }
      // Loop restart
      else {
        startTimeRef.current = Date.now();
        dots = [];
        patterns = [];
        infinityX = 150;
        logoAlpha = 0;
        textAlpha = 0;
        bounceCount = 0;
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
        animationRef.current = null;
      }
    };
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <canvas
        ref={canvasRef}
        width={1200}
        height={267}
        className="border-2 border-purple-500 rounded-lg shadow-2xl"
      />
      <div className="mt-4 text-sm text-slate-400 italic">
        ∞ → • → ∞•' | Mathematics of Wholeness
      </div>
      <div className="mt-2 text-xs text-slate-500">
        64 fractal trees (16×4 grid) with vine connections
      </div>
    </div>
  );
};

export default FractalRealityAnimation;
