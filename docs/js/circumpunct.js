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
    const circumpunctLink = document.querySelector('.circumpunct-link');
    const panelLinks = document.querySelectorAll('.panel-links a[data-zone]');

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
        // Highlight the corresponding zone if it exists (not for circumpunct)
        const zoneEl = document.querySelector(`.zone-${zoneName}`);
        if (zoneEl) zoneEl.classList.add('active');
        document.body.style.overflow = 'hidden';
        // Scroll panel to top when opening
        panel.scrollTop = 0;
    }

    // Close all panels
    function closeAllPanels() {
        panels.forEach(panel => panel.classList.remove('open'));
        zones.forEach(zone => zone.classList.remove('active'));
        backdrop.classList.remove('show');
        openPanel = null;
        document.body.style.overflow = '';
    }

    // Zone click handlers (for the SVG zones)
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

    // "You ARE ⊙" link handler
    if (circumpunctLink) {
        circumpunctLink.addEventListener('click', (e) => {
            e.preventDefault();
            openPanelByZone('circumpunct');
        });
    }

    // Panel navigation links (cross-links between panels)
    panelLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const zoneName = link.dataset.zone;
            if (zoneName) openPanelByZone(zoneName);
        });
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
    let outwardRipples = []; // Emergence from soul
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
            this.hasTriggeredResponse = false; // Only trigger soul response once
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

            // When lightning "arrives" at soul (life around 0.5), trigger emergence
            // Soul receives input, then responds with output
            if (!this.hasTriggeredResponse && this.life < 0.5) {
                this.hasTriggeredResponse = true;
                // Soul responds! Spawn outward ripple after brief "processing"
                // Angle may shift slightly - soul transforms, doesn't just reflect
                const responseAngle = this.angle + (Math.random() - 0.5) * 0.3;
                outwardRipples.push(new OutwardRipple(responseAngle, this.type));
            }

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

    // Ripple that propagates through the field (mind) - INWARD
    class Ripple {
        constructor(angle, particleType) {
            this.angle = angle;
            this.radius = boundaryRadius; // Start at boundary
            this.speed = 0.8; // Slower - patterns persist longer
            this.life = 1.0;
            this.type = particleType;
            this.hueShift = Math.random() * 20 - 10;
            this.direction = 'inward';
        }

        update() {
            this.radius -= this.speed; // Move inward
            // Slower decay - hold patterns longer
            this.life = Math.max(0, (this.radius - soulRadius) / (boundaryRadius - soulRadius));
            return this.radius > soulRadius;
        }
    }

    // Outward ripple - EMERGENCE from soul
    // The soul responds to input with transformed output
    class OutwardRipple {
        constructor(angle, sourceType) {
            this.angle = angle;
            this.radius = soulRadius; // Start at soul
            this.speed = 1.2; // Slightly faster - soul's response is energized
            this.life = 1.0;
            this.sourceType = sourceType; // What triggered it
            this.direction = 'outward';
            // Soul transforms input - response is always soul-colored (cyan)
            // but carries a hint of what triggered it
            this.hueBase = 200; // Cyan base
        }

        update() {
            this.radius += this.speed; // Move OUTWARD
            this.life = Math.max(0, (boundaryRadius - this.radius) / (boundaryRadius - soulRadius));
            return this.radius < boundaryRadius;
        }
    }

    // Calculate wave intensity at a point in the field
    // Returns { inward: number, outward: number } for interference patterns
    function getFieldIntensity(r, angle) {
        let inwardWave = 0;
        let outwardWave = 0;

        // Inward ripples (from boundary toward soul)
        ripples.forEach(ripple => {
            const rippleDist = Math.abs(r - ripple.radius);
            let angleDiff = Math.abs(angle - ripple.angle);
            if (angleDiff > Math.PI) angleDiff = 2 * Math.PI - angleDiff;
            const spread = Math.PI * (1 - ripple.life) + 0.3;

            if (rippleDist < 20 && angleDiff < spread) {
                const radialWave = Math.cos((rippleDist / 20) * Math.PI) * ripple.life;
                const angularFade = Math.cos((angleDiff / spread) * Math.PI / 2);
                inwardWave += radialWave * angularFade;
            }
        });

        // Outward ripples (from soul toward boundary) - EMERGENCE
        outwardRipples.forEach(ripple => {
            const rippleDist = Math.abs(r - ripple.radius);
            let angleDiff = Math.abs(angle - ripple.angle);
            if (angleDiff > Math.PI) angleDiff = 2 * Math.PI - angleDiff;
            // Outward ripples spread more as they travel
            const spread = Math.PI * 0.5 * (1 - ripple.life) + 0.4;

            if (rippleDist < 25 && angleDiff < spread) {
                const radialWave = Math.cos((rippleDist / 25) * Math.PI) * ripple.life;
                const angularFade = Math.cos((angleDiff / spread) * Math.PI / 2);
                outwardWave += radialWave * angularFade;
            }
        });

        return { inward: inwardWave, outward: outwardWave, total: inwardWave + outwardWave };
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
                const waves = getFieldIntensity(r, angle);
                const inward = waves.inward;
                const outward = waves.outward;
                const total = Math.abs(inward) + Math.abs(outward);

                if (total > 0.05) {
                    // Blend between gold (inward/input) and cyan (outward/output)
                    // Inward = gold (45), Outward = cyan (190)
                    const inwardRatio = Math.abs(inward) / (total + 0.01);
                    const outwardRatio = Math.abs(outward) / (total + 0.01);

                    // Hue blends from gold to cyan based on direction
                    const hue = 45 * inwardRatio + 190 * outwardRatio + waves.total * 20;
                    const saturation = 70 + total * 30;
                    const lightness = 45 + waves.total * 20;
                    const alpha = 0.15 + total * 0.4;

                    ctx.beginPath();
                    ctx.arc(centerX, centerY, r, angle, nextAngle);
                    ctx.strokeStyle = `hsla(${hue}, ${saturation}%, ${lightness}%, ${alpha})`;
                    ctx.lineWidth = (fieldOuter - fieldInner) / rings + total * 4;
                    ctx.stroke();
                }
            }
        }

        // Draw bright interference nodes where inward and outward waves meet
        const hasInterference = ripples.length > 0 && outwardRipples.length > 0;
        if (hasInterference || ripples.length > 1 || outwardRipples.length > 1) {
            for (let r = fieldInner; r < fieldOuter; r += 8) {
                for (let a = 0; a < Math.PI * 2; a += Math.PI / 12) {
                    const waves = getFieldIntensity(r, a);
                    const total = Math.abs(waves.inward) + Math.abs(waves.outward);

                    if (total > 0.5) {
                        const x = centerX + Math.cos(a) * r;
                        const y = centerY + Math.sin(a) * r;

                        // When inward and outward meet - special interference!
                        const bothPresent = Math.abs(waves.inward) > 0.2 && Math.abs(waves.outward) > 0.2;
                        let hue, saturation;

                        if (bothPresent) {
                            // Input meets output - white/bright interference
                            hue = 180; // Teal - meeting point
                            saturation = 50;
                        } else if (Math.abs(waves.outward) > Math.abs(waves.inward)) {
                            // Soul's response - cyan
                            hue = 200;
                            saturation = 90;
                        } else {
                            // External input - gold
                            hue = 45;
                            saturation = 90;
                        }

                        const size = 2 + total * 4;
                        ctx.beginPath();
                        ctx.arc(x, y, size, 0, Math.PI * 2);
                        ctx.fillStyle = `hsla(${hue}, ${saturation}%, 65%, ${total * 0.6})`;
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

        // Update ripples (inward - convergence)
        ripples = ripples.filter(r => r.update());

        // Update outward ripples (emergence from soul)
        outwardRipples = outwardRipples.filter(r => r.update());

        // Draw the mind field (Φ) with both inward and outward ripple distortions
        drawMindField();

        // Update and draw lightning bolts (which trigger soul responses)
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
