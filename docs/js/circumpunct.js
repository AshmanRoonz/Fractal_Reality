/**
 * Circumpunct Interactive Demo
 * Tap the ⊙ to explore Body, Mind, Soul
 */

(function() {
    'use strict';

    // Elements
    const zones = document.querySelectorAll('.zone');
    const panels = document.querySelectorAll('.panel');
    const closeButtons = document.querySelectorAll('.panel-close');

    // Create backdrop
    const backdrop = document.createElement('div');
    backdrop.className = 'backdrop';
    document.body.appendChild(backdrop);

    let openPanel = null;

    // Open panel
    function openPanelByZone(zoneName) {
        const panel = document.getElementById(`panel-${zoneName}`);
        if (!panel) return;

        closeAllPanels();
        panel.classList.add('open');
        backdrop.classList.add('show');
        openPanel = panel;
        document.querySelector(`.zone-${zoneName}`)?.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    // Close all panels
    function closeAllPanels() {
        panels.forEach(panel => panel.classList.remove('open'));
        zones.forEach(zone => zone.classList.remove('active'));
        backdrop.classList.remove('show');
        openPanel = null;
        document.body.style.overflow = '';
    }

    // Zone click handlers
    zones.forEach(zone => {
        zone.addEventListener('click', (e) => {
            e.stopPropagation();
            const zoneName = zone.dataset.zone;
            if (zoneName) openPanelByZone(zoneName);
        });

        zone.addEventListener('touchstart', () => {
            zone.classList.add('active');
        }, { passive: true });

        zone.addEventListener('touchend', () => {
            setTimeout(() => {
                if (!openPanel) zone.classList.remove('active');
            }, 100);
        }, { passive: true });
    });

    // Close handlers
    closeButtons.forEach(btn => btn.addEventListener('click', closeAllPanels));
    backdrop.addEventListener('click', closeAllPanels);
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && openPanel) closeAllPanels();
    });

    // Swipe to close
    let touchStartY = 0;
    panels.forEach(panel => {
        panel.addEventListener('touchstart', (e) => {
            touchStartY = e.touches[0].clientY;
        }, { passive: true });

        panel.addEventListener('touchmove', (e) => {
            const diff = e.touches[0].clientY - touchStartY;
            if (diff > 80 && panel.scrollTop === 0) closeAllPanels();
        }, { passive: true });
    });

    // =========================================
    // Particle Background - Mini Circumpuncts
    // =========================================
    const canvas = document.getElementById('particles');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let particles = [];
    let lightningBolts = [];
    let ripples = [];
    let animationId;
    let centerX, centerY, boundaryRadius, soulRadius;

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        centerX = canvas.width / 2;
        centerY = canvas.height / 2;
        boundaryRadius = Math.min(canvas.width, canvas.height) * 0.18; // The ○ boundary
        soulRadius = boundaryRadius * 0.23; // The • soul
        initParticles();
    }

    // Lightning bolt that shoots inward when boundary is hit
    class Lightning {
        constructor(angle, particleType) {
            this.angle = angle;
            this.life = 1.0;
            this.decay = 0.04;
            this.type = particleType;
            // Generate jagged path from boundary to soul
            this.segments = this.generatePath();
        }

        generatePath() {
            const segments = [];
            const startR = boundaryRadius;
            const endR = soulRadius;
            const steps = 8;

            for (let i = 0; i <= steps; i++) {
                const t = i / steps;
                const r = startR - (startR - endR) * t;
                // Add jitter for lightning effect (less at start and end)
                const jitter = (i > 0 && i < steps) ? (Math.random() - 0.5) * 0.3 : 0;
                const a = this.angle + jitter;
                segments.push({
                    x: centerX + Math.cos(a) * r,
                    y: centerY + Math.sin(a) * r
                });
            }
            return segments;
        }

        update() {
            this.life -= this.decay;
            return this.life > 0;
        }

        draw() {
            if (this.segments.length < 2) return;

            // Color based on particle type that triggered it
            let color;
            if (this.type === 'body') {
                color = `rgba(163, 113, 247, ${this.life * 0.8})`;
            } else if (this.type === 'mind') {
                color = `rgba(240, 180, 41, ${this.life * 0.8})`;
            } else {
                color = `rgba(88, 166, 255, ${this.life * 0.8})`;
            }

            ctx.beginPath();
            ctx.moveTo(this.segments[0].x, this.segments[0].y);
            for (let i = 1; i < this.segments.length; i++) {
                ctx.lineTo(this.segments[i].x, this.segments[i].y);
            }
            ctx.strokeStyle = color;
            ctx.lineWidth = 2 * this.life;
            ctx.stroke();

            // Glow effect
            ctx.strokeStyle = color.replace(this.life * 0.8, this.life * 0.3);
            ctx.lineWidth = 6 * this.life;
            ctx.stroke();
        }
    }

    // Ripple that propagates through the field (mind)
    class Ripple {
        constructor(angle, particleType) {
            this.angle = angle;
            this.radius = boundaryRadius; // Start at boundary
            this.speed = 1.5;
            this.life = 1.0;
            this.type = particleType;
            this.hueShift = Math.random() * 30 - 15; // Slight color variation
        }

        update() {
            this.radius -= this.speed; // Move inward
            this.life = (this.radius - soulRadius) / (boundaryRadius - soulRadius);
            return this.radius > soulRadius && this.life > 0;
        }

        getColor(interference = 0) {
            // Base colors shifted by interference
            let h, s, l;
            if (this.type === 'body') {
                h = 270 + this.hueShift + interference * 60; // Purple
            } else if (this.type === 'mind') {
                h = 40 + this.hueShift + interference * 60; // Gold
            } else {
                h = 210 + this.hueShift + interference * 60; // Cyan
            }
            s = 70 + interference * 20;
            l = 50 + interference * 20;
            return `hsla(${h}, ${s}%, ${l}%, ${this.life * 0.4})`;
        }
    }

    // Calculate interference between ripples
    function calculateInterference(x, y) {
        let totalWave = 0;
        ripples.forEach(ripple => {
            const dx = x - centerX;
            const dy = y - centerY;
            const pointRadius = Math.sqrt(dx * dx + dy * dy);
            const diff = Math.abs(pointRadius - ripple.radius);
            if (diff < 15) {
                // Wave contribution based on proximity to ripple
                const wave = Math.cos((diff / 15) * Math.PI) * ripple.life;
                totalWave += wave;
            }
        });
        return totalWave;
    }

    function drawRipples() {
        // Draw ripples as arcs in the field
        ripples.forEach(ripple => {
            const arcSpan = Math.PI / 3; // 60 degree arc
            ctx.beginPath();
            ctx.arc(centerX, centerY, ripple.radius,
                    ripple.angle - arcSpan / 2,
                    ripple.angle + arcSpan / 2);

            // Calculate interference at this ripple's position
            const interference = calculateInterference(
                centerX + Math.cos(ripple.angle) * ripple.radius,
                centerY + Math.sin(ripple.angle) * ripple.radius
            );

            ctx.strokeStyle = ripple.getColor(Math.abs(interference));
            ctx.lineWidth = 3 + Math.abs(interference) * 4;
            ctx.stroke();
        });

        // Draw interference pattern overlay in the field
        if (ripples.length > 1) {
            const fieldSteps = 20;
            for (let r = soulRadius + 5; r < boundaryRadius - 5; r += (boundaryRadius - soulRadius) / fieldSteps) {
                for (let a = 0; a < Math.PI * 2; a += Math.PI / 16) {
                    const x = centerX + Math.cos(a) * r;
                    const y = centerY + Math.sin(a) * r;
                    const interference = calculateInterference(x, y);

                    if (Math.abs(interference) > 0.3) {
                        // Interference creates color shifts
                        const hue = 200 + interference * 120; // Shifts between colors
                        const brightness = 50 + interference * 30;
                        ctx.beginPath();
                        ctx.arc(x, y, 2 + Math.abs(interference) * 2, 0, Math.PI * 2);
                        ctx.fillStyle = `hsla(${hue}, 80%, ${brightness}%, ${Math.abs(interference) * 0.5})`;
                        ctx.fill();
                    }
                }
            }
        }
    }

    function spawnLightningAndRipple(angle, particleType) {
        lightningBolts.push(new Lightning(angle, particleType));
        ripples.push(new Ripple(angle, particleType));
    }

    class Particle {
        constructor() {
            this.reset();
        }

        reset() {
            // Spawn particles outside the boundary
            do {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
            } while (this.isInsideBoundary());

            this.baseSize = Math.random() * 2 + 1;
            this.speedX = (Math.random() - 0.5) * 0.4;
            this.speedY = (Math.random() - 0.5) * 0.4;
            this.baseOpacity = Math.random() * 0.4 + 0.1;
            // Each particle is a mini circumpunct with body/mind/soul colors
            const types = ['body', 'mind', 'soul'];
            this.type = types[Math.floor(Math.random() * types.length)];
        }

        isInsideBoundary() {
            const dx = this.x - centerX;
            const dy = this.y - centerY;
            return Math.sqrt(dx * dx + dy * dy) < boundaryRadius + 10;
        }

        update() {
            this.x += this.speedX;
            this.y += this.speedY;

            // Bounce off the boundary (○) - particles cannot cross it
            const dx = this.x - centerX;
            const dy = this.y - centerY;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist < boundaryRadius + 5) {
                // Push particle back outside and reflect velocity
                const angle = Math.atan2(dy, dx);
                this.x = centerX + Math.cos(angle) * (boundaryRadius + 6);
                this.y = centerY + Math.sin(angle) * (boundaryRadius + 6);

                // Reflect velocity away from center
                const normalX = dx / dist;
                const normalY = dy / dist;
                const dot = this.speedX * normalX + this.speedY * normalY;
                this.speedX = this.speedX - 2 * dot * normalX;
                this.speedY = this.speedY - 2 * dot * normalY;

                // ⚡ Spawn lightning bolt and ripple on impact!
                spawnLightningAndRipple(angle + Math.PI, this.type); // Inward angle
            }

            // Wrap around edges
            if (this.x < 0) this.x = canvas.width;
            if (this.x > canvas.width) this.x = 0;
            if (this.y < 0) this.y = canvas.height;
            if (this.y > canvas.height) this.y = 0;
        }

        draw() {
            // Distance to center (main circumpunct)
            const dx = this.x - centerX;
            const dy = this.y - centerY;
            const distToCenter = Math.sqrt(dx * dx + dy * dy);

            // Particles grow and brighten as they approach center
            const maxDist = Math.min(canvas.width, canvas.height) * 0.4;
            const proximity = Math.max(0, 1 - distToCenter / maxDist);

            const size = this.baseSize * (1 + proximity * 2);
            const opacity = this.baseOpacity + proximity * 0.5;

            // Colors based on type
            let ringColor, dotColor;
            if (this.type === 'body') {
                ringColor = `rgba(163, 113, 247, ${opacity})`;
                dotColor = `rgba(163, 113, 247, ${opacity * 0.8})`;
            } else if (this.type === 'mind') {
                ringColor = `rgba(240, 180, 41, ${opacity})`;
                dotColor = `rgba(240, 180, 41, ${opacity * 0.8})`;
            } else {
                ringColor = `rgba(88, 166, 255, ${opacity})`;
                dotColor = `rgba(88, 166, 255, ${opacity * 0.8})`;
            }

            // Draw as mini circumpunct: ring + dot
            // Outer ring (○)
            ctx.beginPath();
            ctx.arc(this.x, this.y, size * 2, 0, Math.PI * 2);
            ctx.strokeStyle = ringColor;
            ctx.lineWidth = size * 0.3;
            ctx.stroke();

            // Inner dot (•)
            ctx.beginPath();
            ctx.arc(this.x, this.y, size * 0.5, 0, Math.PI * 2);
            ctx.fillStyle = dotColor;
            ctx.fill();
        }
    }

    function initParticles() {
        const count = Math.min(50, Math.floor((canvas.width * canvas.height) / 25000));
        particles = [];
        for (let i = 0; i < count; i++) particles.push(new Particle());
    }

    // Check if a line segment crosses through the circumpunct
    function lineCrossesBoundary(x1, y1, x2, y2) {
        // Find closest point on line segment to center
        const dx = x2 - x1;
        const dy = y2 - y1;
        const t = Math.max(0, Math.min(1, ((centerX - x1) * dx + (centerY - y1) * dy) / (dx * dx + dy * dy)));
        const closestX = x1 + t * dx;
        const closestY = y1 + t * dy;
        const distToCenter = Math.sqrt((closestX - centerX) ** 2 + (closestY - centerY) ** 2);
        return distToCenter < boundaryRadius;
    }

    function drawConnections() {
        const connectionRadius = 150;

        // Connect particles to each other (but not through the circumpunct!)
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < connectionRadius) {
                    // Don't draw if line would cross the boundary
                    if (lineCrossesBoundary(particles[i].x, particles[i].y, particles[j].x, particles[j].y)) {
                        continue;
                    }
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(255, 255, 255, ${(1 - dist / connectionRadius) * 0.12})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
        }

        // Connect particles to the main circumpunct's BOUNDARY (not center!)
        // ○ = boundary, Φ = field connects boundary to center, • = soul/center
        // External connections only reach the boundary
        const connectionRange = Math.min(canvas.width, canvas.height) * 0.35;

        particles.forEach(p => {
            const dx = p.x - centerX;
            const dy = p.y - centerY;
            const dist = Math.sqrt(dx * dx + dy * dy);

            // Only connect if particle is outside the boundary but within range
            if (dist > boundaryRadius && dist < connectionRange) {
                const opacity = (1 - (dist - boundaryRadius) / (connectionRange - boundaryRadius)) * 0.4;

                // Calculate the point on the boundary where line should end
                const angle = Math.atan2(dy, dx);
                const boundaryX = centerX + Math.cos(angle) * boundaryRadius;
                const boundaryY = centerY + Math.sin(angle) * boundaryRadius;

                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(boundaryX, boundaryY); // Connect to boundary, not center!

                // Color based on particle type
                if (p.type === 'body') {
                    ctx.strokeStyle = `rgba(163, 113, 247, ${opacity})`;
                } else if (p.type === 'mind') {
                    ctx.strokeStyle = `rgba(240, 180, 41, ${opacity})`;
                } else {
                    ctx.strokeStyle = `rgba(88, 166, 255, ${opacity})`;
                }
                ctx.lineWidth = 1;
                ctx.stroke();
            }
        });
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Update and draw particles
        particles.forEach(p => { p.update(); p.draw(); });
        drawConnections();

        // Update and draw lightning bolts
        lightningBolts = lightningBolts.filter(l => l.update());
        lightningBolts.forEach(l => l.draw());

        // Update and draw ripples in the field
        ripples = ripples.filter(r => r.update());
        drawRipples();

        animationId = requestAnimationFrame(animate);
    }

    window.addEventListener('resize', resize);
    resize();
    animate();

    document.addEventListener('visibilitychange', () => {
        if (document.hidden) cancelAnimationFrame(animationId);
        else animate();
    });
})();
