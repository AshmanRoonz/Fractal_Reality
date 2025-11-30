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
            this.speed = 0.8; // Slower - patterns persist longer
            this.life = 1.0;
            this.type = particleType;
            this.hueShift = Math.random() * 20 - 10;
        }

        update() {
            this.radius -= this.speed; // Move inward
            // Slower decay - hold patterns longer
            this.life = Math.max(0, (this.radius - soulRadius) / (boundaryRadius - soulRadius));
            return this.radius > soulRadius;
        }
    }

    // Calculate wave intensity at a point in the field
    function getFieldIntensity(r, angle) {
        let totalWave = 0;
        ripples.forEach(ripple => {
            // Distance from this point to the ripple wavefront
            const rippleDist = Math.abs(r - ripple.radius);
            // Angular proximity to ripple origin
            let angleDiff = Math.abs(angle - ripple.angle);
            if (angleDiff > Math.PI) angleDiff = 2 * Math.PI - angleDiff;
            // Ripple spreads as it moves inward
            const spread = Math.PI * (1 - ripple.life) + 0.3;

            if (rippleDist < 20 && angleDiff < spread) {
                const radialWave = Math.cos((rippleDist / 20) * Math.PI) * ripple.life;
                const angularFade = Math.cos((angleDiff / spread) * Math.PI / 2);
                totalWave += radialWave * angularFade;
            }
        });
        return totalWave;
    }

    // Draw the golden mind field with ripple distortions
    function drawMindField() {
        const fieldInner = soulRadius + 3;
        const fieldOuter = boundaryRadius - 3;
        const rings = 12;
        const segments = 36;

        for (let ringIdx = 0; ringIdx < rings; ringIdx++) {
            const r = fieldInner + (fieldOuter - fieldInner) * (ringIdx / rings);

            for (let seg = 0; seg < segments; seg++) {
                const angle = (seg / segments) * Math.PI * 2;
                const nextAngle = ((seg + 1) / segments) * Math.PI * 2;

                // Get wave intensity at this point
                const intensity = getFieldIntensity(r, angle);

                if (Math.abs(intensity) > 0.05) {
                    // Base gold color, shifted by interference
                    const hue = 45 + intensity * 40; // Gold shifts toward orange or yellow-green
                    const saturation = 70 + Math.abs(intensity) * 30;
                    const lightness = 45 + intensity * 25;
                    const alpha = 0.15 + Math.abs(intensity) * 0.4;

                    ctx.beginPath();
                    ctx.arc(centerX, centerY, r, angle, nextAngle);
                    ctx.strokeStyle = `hsla(${hue}, ${saturation}%, ${lightness}%, ${alpha})`;
                    ctx.lineWidth = (fieldOuter - fieldInner) / rings + Math.abs(intensity) * 4;
                    ctx.stroke();
                }
            }
        }

        // Draw bright interference nodes where multiple ripples overlap
        if (ripples.length > 1) {
            for (let r = fieldInner; r < fieldOuter; r += 8) {
                for (let a = 0; a < Math.PI * 2; a += Math.PI / 12) {
                    const intensity = getFieldIntensity(r, a);

                    if (Math.abs(intensity) > 0.6) {
                        const x = centerX + Math.cos(a) * r;
                        const y = centerY + Math.sin(a) * r;

                        // Bright interference points
                        const hue = 45 + intensity * 60;
                        const size = 2 + Math.abs(intensity) * 4;

                        ctx.beginPath();
                        ctx.arc(x, y, size, 0, Math.PI * 2);
                        ctx.fillStyle = `hsla(${hue}, 90%, 65%, ${Math.abs(intensity) * 0.7})`;
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

            this.baseSize = Math.random() * 2.5 + 1.5;
            this.speedX = (Math.random() - 0.5) * 0.4;
            this.speedY = (Math.random() - 0.5) * 0.4;
            this.baseOpacity = Math.random() * 0.4 + 0.4; // Brighter particles
            // Each particle is a mini circumpunct with body/mind/soul colors
            const types = ['body', 'mind', 'soul'];
            this.type = types[Math.floor(Math.random() * types.length)];
        }

        isInsideBoundary() {
            const dx = this.x - centerX;
            const dy = this.y - centerY;
            return Math.sqrt(dx * dx + dy * dy) < boundaryRadius + 25; // Match bounce radius
        }

        update() {
            this.x += this.speedX;
            this.y += this.speedY;

            // Bounce off the boundary (○) - particles cannot cross it
            // Bounce BEFORE entering the purple ring visually
            const dx = this.x - centerX;
            const dy = this.y - centerY;
            const dist = Math.sqrt(dx * dx + dy * dy);
            const bounceRadius = boundaryRadius + 18; // Stay outside the purple ring

            if (dist < bounceRadius) {
                // Push particle back outside and reflect velocity
                const angle = Math.atan2(dy, dx);
                this.x = centerX + Math.cos(angle) * (bounceRadius + 2);
                this.y = centerY + Math.sin(angle) * (bounceRadius + 2);

                // Reflect velocity away from center
                const normalX = dx / dist;
                const normalY = dy / dist;
                const dot = this.speedX * normalX + this.speedY * normalY;
                this.speedX = this.speedX - 2 * dot * normalX;
                this.speedY = this.speedY - 2 * dot * normalY;

                // ⚡ Spawn lightning bolt and ripple on impact!
                // Lightning shoots inward from the impact point (same side)
                spawnLightningAndRipple(angle, this.type);
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

        // Update ripples
        ripples = ripples.filter(r => r.update());

        // Draw the golden mind field (Φ) with ripple distortions
        drawMindField();

        // Update and draw lightning bolts
        lightningBolts = lightningBolts.filter(l => l.update());
        lightningBolts.forEach(l => l.draw());

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
