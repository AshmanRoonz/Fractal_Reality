/**
 * Fractal Background Animation
 * Creates an animated fractal pattern representing nested wholeness
 */

class FractalBackground {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.connections = [];
        this.particleCount = 100;
        this.time = 0;

        this.resize();
        this.init();
        this.animate();

        window.addEventListener('resize', () => this.resize());
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.centerX = this.canvas.width / 2;
        this.centerY = this.canvas.height / 2;
    }

    init() {
        this.particles = [];
        for (let i = 0; i < this.particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                radius: Math.random() * 2 + 1,
                opacity: Math.random() * 0.5 + 0.2,
                hue: Math.random() * 60 + 250 // Purple to cyan range
            });
        }
    }

    drawParticle(particle) {
        this.ctx.beginPath();
        this.ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
        this.ctx.fillStyle = `hsla(${particle.hue}, 70%, 70%, ${particle.opacity})`;
        this.ctx.fill();
    }

    drawConnection(p1, p2, distance, maxDistance) {
        const opacity = (1 - distance / maxDistance) * 0.3;
        this.ctx.beginPath();
        this.ctx.moveTo(p1.x, p1.y);
        this.ctx.lineTo(p2.x, p2.y);
        this.ctx.strokeStyle = `hsla(${(p1.hue + p2.hue) / 2}, 70%, 70%, ${opacity})`;
        this.ctx.lineWidth = 0.5;
        this.ctx.stroke();
    }

    update() {
        this.time += 0.01;

        // Update particles with fractal-like behavior
        this.particles.forEach((particle, i) => {
            // Oscillating motion (representing ∇ ⊗ ℰ)
            const angle = this.time + i * 0.1;
            const radius = 50 + Math.sin(this.time * 0.5 + i) * 20;

            particle.vx += Math.cos(angle) * 0.01;
            particle.vy += Math.sin(angle) * 0.01;

            // Damping (β = 0.5 behavior)
            particle.vx *= 0.98;
            particle.vy *= 0.98;

            particle.x += particle.vx;
            particle.y += particle.vy;

            // Wrap around edges
            if (particle.x < 0) particle.x = this.canvas.width;
            if (particle.x > this.canvas.width) particle.x = 0;
            if (particle.y < 0) particle.y = this.canvas.height;
            if (particle.y > this.canvas.height) particle.y = 0;

            // Pulse opacity
            particle.opacity = 0.2 + Math.abs(Math.sin(this.time + i * 0.5)) * 0.3;
        });
    }

    draw() {
        // Clear with fade effect
        this.ctx.fillStyle = 'rgba(10, 14, 26, 0.1)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        const maxDistance = 150;

        // Draw connections (representing ⊗)
        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const dx = this.particles[i].x - this.particles[j].x;
                const dy = this.particles[i].y - this.particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < maxDistance) {
                    this.drawConnection(this.particles[i], this.particles[j], distance, maxDistance);
                }
            }
        }

        // Draw particles (representing ⊙)
        this.particles.forEach(particle => this.drawParticle(particle));

        // Draw central symbol (⊙) with pulsing effect
        const pulseSize = 30 + Math.sin(this.time * 2) * 5;
        this.ctx.save();
        this.ctx.translate(this.centerX, this.centerY);
        this.ctx.font = `${pulseSize}px serif`;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillStyle = `hsla(45, 95%, 55%, ${0.1 + Math.abs(Math.sin(this.time)) * 0.2})`;
        this.ctx.fillText('⊙', 0, 0);
        this.ctx.restore();
    }

    animate() {
        this.update();
        this.draw();
        requestAnimationFrame(() => this.animate());
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new FractalBackground('fractalCanvas');
});
