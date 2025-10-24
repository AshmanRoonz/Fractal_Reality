import React, { useEffect, useRef, useState } from 'react';

// Types
interface Particle {
  x: number;
  y: number;
  angle: number;
  speed: number;
  generation: number;
  age: number;
  maxAge: number;
  size: number;
  hue: number;
  trail: Array<{ x: number; y: number; age: number }>;
  branchCooldown: number;
  hasBranched: boolean;
  curvature: number;
  spiral: number;
  wobble: number;
}

// Constants
const PHI = (1 + Math.sqrt(5)) / 2;
const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5));
const ZOOM_DURATION = 900;

export default function FractalFountain() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [stats, setStats] = useState({
    particleCount: 0,
    branchCount: 0,
    fractalDim: 1.5
  });
  const [showUI, setShowUI] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    // Animation state
    let time = 0;
    let zoomProgress = 0;
    let singularityRadius = Math.max(canvas.width, canvas.height);
    const finalRadius = 0.5;
    let particles: Particle[] = [];
    let spawnIndex = 0;
    let branchCount = 0;
    let animationFrameId: number;

    // Create particle
    const createParticle = (
      x: number,
      y: number,
      angle: number,
      speed: number,
      generation: number,
      hue: number
    ): Particle => ({
      x,
      y,
      angle,
      speed,
      generation,
      age: 0,
      maxAge: 200 - generation * 20,
      size: Math.max(1, 3 - generation * 0.3),
      hue,
      trail: [],
      branchCooldown: 20 + Math.random() * 30,
      hasBranched: false,
      curvature: (Math.random() - 0.5) * 0.05,
      spiral: Math.random() * 0.02,
      wobble: Math.random() * 0.1
    });

    // Update particle
    const updateParticle = (p: Particle): boolean => {
      p.age++;

      // Complex curved motion
      p.angle += p.curvature + Math.sin(p.age * p.wobble) * 0.03;

      // Spiral outward
      const spiralFactor = 1 + p.age * p.spiral;

      // Move
      p.x += Math.cos(p.angle) * p.speed * spiralFactor;
      p.y += Math.sin(p.angle) * p.speed * spiralFactor;

      // Add to trail
      if (p.age % 2 === 0) {
        p.trail.push({ x: p.x, y: p.y, age: 0 });
        if (p.trail.length > 30) p.trail.shift();
      }

      // Age trail points
      p.trail.forEach(t => t.age++);

      // Branch recursively
      if (
        !p.hasBranched &&
        p.age > p.branchCooldown &&
        p.generation < 4 &&
        Math.random() < 0.03
      ) {
        p.hasBranched = true;
        branchCount++;

        // Create 2-3 child particles
        const numChildren = 2 + Math.floor(Math.random() * 2);
        const angleSpread = Math.PI / 3;

        for (let i = 0; i < numChildren; i++) {
          const childAngle = p.angle + (Math.random() - 0.5) * angleSpread;
          const childSpeed = p.speed * (0.8 + Math.random() * 0.4);
          const childHue = (p.hue + (Math.random() - 0.5) * 30) % 360;

          particles.push(
            createParticle(p.x, p.y, childAngle, childSpeed, p.generation + 1, childHue)
          );
        }
      }

      return p.age < p.maxAge;
    };

    // Draw particle
    const drawParticle = (p: Particle) => {
      const alpha = 1 - p.age / p.maxAge;

      // Draw trail
      if (p.trail.length > 1) {
        ctx.strokeStyle = `hsla(${p.hue}, 80%, 60%, ${alpha * 0.3})`;
        ctx.lineWidth = p.size * 0.8;
        ctx.beginPath();
        p.trail.forEach((point, i) => {
          if (i === 0) ctx.moveTo(point.x, point.y);
          else ctx.lineTo(point.x, point.y);
        });
        ctx.stroke();
      }

      // Draw particle with glow
      const glowSize = p.size * 3;
      const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, glowSize);
      gradient.addColorStop(0, `hsla(${p.hue}, 90%, 70%, ${alpha})`);
      gradient.addColorStop(0.5, `hsla(${p.hue}, 80%, 60%, ${alpha * 0.5})`);
      gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(p.x, p.y, glowSize, 0, Math.PI * 2);
      ctx.fill();
    };

    // Spawn particles
    const spawnParticles = () => {
      if (zoomProgress < 0.3) return;

      const spawnRate = Math.floor(5 + zoomProgress * 15);

      for (let i = 0; i < spawnRate; i++) {
        const angle = spawnIndex * GOLDEN_ANGLE;
        const speed = 1 + Math.random() * 2;
        const hue = (spawnIndex * 137.5) % 360;

        particles.push(createParticle(centerX, centerY, angle, speed, 0, hue));
        spawnIndex++;
      }
    };

    // Calculate fractal dimension
    const calculateFractalDimension = (): number => {
      let totalD = 0;
      let count = 0;

      particles.forEach(p => {
        if (p.trail.length > 15) {
          const first = p.trail[0];
          const last = p.trail[p.trail.length - 1];
          const disp = Math.hypot(last.x - first.x, last.y - first.y);
          let pathLen = 0;

          for (let i = 1; i < p.trail.length; i++) {
            pathLen += Math.hypot(
              p.trail[i].x - p.trail[i - 1].x,
              p.trail[i].y - p.trail[i - 1].y
            );
          }

          if (disp > 20 && pathLen > 0) {
            const D = Math.log(pathLen) / Math.log(disp);
            if (D > 1.2 && D < 2) {
              totalD += D;
              count++;
            }
          }
        }
      });

      return count > 0 ? totalD / count : 1.5;
    };

    // Main animation loop
    const animate = () => {
      time++;

      // Zoom phase
      if (zoomProgress < 1) {
        zoomProgress = Math.min(1, time / ZOOM_DURATION);
        const eased = 1 - Math.pow(1 - zoomProgress, 3);
        singularityRadius =
          Math.max(canvas.width, canvas.height) * (1 - eased) + finalRadius * eased;

        // Show UI after zoom
        if (zoomProgress > 0.95 && !showUI) {
          setShowUI(true);
        }
      }

      // Spawn and update particles
      spawnParticles();
      particles = particles.filter(updateParticle);

      // Update stats (throttled)
      if (time % 10 === 0) {
        setStats({
          particleCount: particles.length,
          branchCount,
          fractalDim: calculateFractalDimension()
        });
      }

      // Clear with fade
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw particles
      particles.forEach(drawParticle);

      // Draw singularity
      if (zoomProgress < 1) {
        // Black circle
        ctx.fillStyle = '#000000';
        ctx.beginPath();
        ctx.arc(centerX, centerY, singularityRadius, 0, Math.PI * 2);
        ctx.fill();

        // Edge glow
        const pulse = Math.sin(time * 0.05) * 0.2 + 0.8;
        const glowRadius = singularityRadius + 5;
        const gradient = ctx.createRadialGradient(
          centerX,
          centerY,
          singularityRadius,
          centerX,
          centerY,
          glowRadius
        );
        gradient.addColorStop(0, `rgba(100, 200, 255, ${pulse * 0.6 * (1 - zoomProgress)})`);
        gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(centerX, centerY, glowRadius, 0, Math.PI * 2);
        ctx.fill();
      } else {
        // After zoom: 1px singularity with accretion disk
        const pulse = Math.sin(time * 0.05) * 0.3 + 1;

        // Accretion disk
        for (let r = 2; r < 30; r += 2) {
          const alpha = 1 - r / 30;
          ctx.strokeStyle = `hsla(${200 + r * 3}, 90%, 70%, ${alpha * 0.4 * pulse})`;
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.arc(centerX, centerY, r, 0, Math.PI * 2);
          ctx.stroke();
        }

        // Bright glow
        const gradient = ctx.createRadialGradient(
          centerX,
          centerY,
          0,
          centerX,
          centerY,
          20 * pulse
        );
        gradient.addColorStop(0, 'rgba(255, 255, 255, 0.9)');
        gradient.addColorStop(0.5, 'rgba(200, 220, 255, 0.5)');
        gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(centerX, centerY, 20 * pulse, 0, Math.PI * 2);
        ctx.fill();

        // The singularity (1px)
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(centerX - 0.5, centerY - 0.5, 1, 1);
      }

      animationFrameId = requestAnimationFrame(animate);
    };

    animate();

    // Cleanup
    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', resizeCanvas);
    };
  }, [showUI]);

  return (
    <div style={{ position: 'relative', width: '100vw', height: '100vh', overflow: 'hidden' }}>
      <canvas
        ref={canvasRef}
        style={{
          display: 'block',
          background: '#000',
          touchAction: 'none'
        }}
      />

      {/* Stats */}
      <div
        style={{
          position: 'fixed',
          top: '15px',
          left: '15px',
          fontSize: '11px',
          color: 'rgba(100, 200, 255, 0.7)',
          fontFamily: 'monospace',
          pointerEvents: 'none',
          lineHeight: 1.8,
          textShadow: '0 0 10px rgba(0, 0, 0, 0.8)',
          opacity: showUI ? 1 : 0,
          transition: 'opacity 1s'
        }}
      >
        <span style={{ opacity: 0.5 }}>∞ → • → ∞'</span>
        <br />
        <br />
        Particles: <span style={{ color: 'rgba(255, 255, 255, 0.9)', fontWeight: 'bold' }}>
          {stats.particleCount}
        </span>
        <br />
        Branches: <span style={{ color: 'rgba(255, 255, 255, 0.9)', fontWeight: 'bold' }}>
          {stats.branchCount}
        </span>
        <br />
        D = <span style={{ color: 'rgba(255, 255, 255, 0.9)', fontWeight: 'bold' }}>
          {stats.fractalDim.toFixed(3)}
        </span>
      </div>

      {/* GitHub Link */}
      <a
        href="https://github.com/AshmanRoonz/Fractal_Reality"
        target="_blank"
        rel="noopener noreferrer"
        style={{
          position: 'fixed',
          bottom: '15px',
          right: '15px',
          background: 'rgba(10, 10, 30, 0.7)',
          border: '1px solid rgba(100, 200, 255, 0.3)',
          borderRadius: '5px',
          padding: '8px 12px',
          fontSize: '11px',
          color: '#64c8ff',
          textDecoration: 'none',
          opacity: showUI ? 0.6 : 0,
          transition: 'opacity 0.3s',
          backdropFilter: 'blur(5px)'
        }}
        onMouseEnter={(e) => (e.currentTarget.style.opacity = '1')}
        onMouseLeave={(e) => (e.currentTarget.style.opacity = '0.6')}
      >
        GitHub ↗
      </a>
    </div>
  );
}
