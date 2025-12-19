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
    let time = 0; // For aurora animation

    // Aurora blobs - soft moving color clouds
    const auroraBlobs = [];
    const AURORA_COUNT = 5;

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        // Get the actual position of the circumpunct SVG element
        const circumpunctEl = document.querySelector('.circumpunct-container');
        if (circumpunctEl) {
            const rect = circumpunctEl.getBoundingClientRect();
            centerX = rect.left + rect.width / 2;
            centerY = rect.top + rect.height / 2;
            // Scale boundary radius based on the actual circumpunct size
            boundaryRadius = Math.min(rect.width, rect.height) * 0.4; // Match SVG proportions
        } else {
            // Fallback to canvas center
            centerX = canvas.width / 2;
            centerY = canvas.height / 2;
            boundaryRadius = Math.min(canvas.width, canvas.height) * 0.18;
        }
        soulRadius = boundaryRadius * 0.23; // The • soul
        initParticles();
        initAurora();
    }

    // Aurora/Nebula effect - soft flowing color clouds
    class AuroraBlob {
        constructor() {
            this.reset();
        }

        reset() {
            // Position anywhere on canvas, preferring edges
            const angle = Math.random() * Math.PI * 2;
            const dist = canvas.width * 0.3 + Math.random() * canvas.width * 0.4;
            this.x = centerX + Math.cos(angle) * dist;
            this.y = centerY + Math.sin(angle) * dist;

            // Size varies significantly
            this.radius = 100 + Math.random() * 200;

            // Very slow drift
            this.vx = (Math.random() - 0.5) * 0.15;
            this.vy = (Math.random() - 0.5) * 0.15;

            // Color type cycles through body/mind/soul
            const types = ['body', 'mind', 'soul'];
            this.type = types[Math.floor(Math.random() * types.length)];

            // Phase offset for pulsing
            this.phase = Math.random() * Math.PI * 2;
            this.pulseSpeed = 0.005 + Math.random() * 0.01;
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;

            // Gentle attraction toward center
            const dx = centerX - this.x;
            const dy = centerY - this.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist > canvas.width * 0.5) {
                this.vx += dx * 0.00001;
                this.vy += dy * 0.00001;
            }

            // Wrap around if too far
            if (this.x < -this.radius) this.x = canvas.width + this.radius;
            if (this.x > canvas.width + this.radius) this.x = -this.radius;
            if (this.y < -this.radius) this.y = canvas.height + this.radius;
            if (this.y > canvas.height + this.radius) this.y = -this.radius;
        }

        draw() {
            const pulse = Math.sin(time * this.pulseSpeed + this.phase) * 0.5 + 0.5;
            const alpha = 0.03 + pulse * 0.02;

            let r, g, b;
            if (this.type === 'body') {
                r = 163; g = 113; b = 247; // Purple
            } else if (this.type === 'mind') {
                r = 240; g = 180; b = 41; // Gold
            } else {
                r = 88; g = 166; b = 255; // Cyan
            }

            // Radial gradient for soft cloud effect
            const gradient = ctx.createRadialGradient(
                this.x, this.y, 0,
                this.x, this.y, this.radius * (0.8 + pulse * 0.4)
            );
            gradient.addColorStop(0, `rgba(${r}, ${g}, ${b}, ${alpha})`);
            gradient.addColorStop(0.5, `rgba(${r}, ${g}, ${b}, ${alpha * 0.5})`);
            gradient.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0)`);

            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius * (0.8 + pulse * 0.4), 0, Math.PI * 2);
            ctx.fill();
        }
    }

    function initAurora() {
        auroraBlobs.length = 0;
        for (let i = 0; i < AURORA_COUNT; i++) {
            auroraBlobs.push(new AuroraBlob());
        }
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

    const TRAIL_LENGTH = 20; // Number of trail segments - longer for more visible trails

    class Particle {
        constructor(forceCollision = false, staggerIndex = 0) {
            this.trail = [];
            this.reset(forceCollision, staggerIndex);
        }

        reset(forceCollision = false, staggerIndex = 0) {
            // Clear trail on reset
            this.trail = [];

            if (forceCollision) {
                // Spawn aimed at the circumpunct for guaranteed collision
                // Stagger distances so they don't all arrive at once
                const angle = Math.random() * Math.PI * 2;
                const staggerDist = 100 + staggerIndex * 80; // Each one starts further out
                const startDist = boundaryRadius + staggerDist + Math.random() * 50;
                this.x = centerX + Math.cos(angle) * startDist;
                this.y = centerY + Math.sin(angle) * startDist;

                // Use SAME speed as normal particles - no speedup
                const speed = 0.15 + Math.random() * 0.15; // 0.15 to 0.3 toward center
                this.speedX = -Math.cos(angle) * speed;
                this.speedY = -Math.sin(angle) * speed;
            } else {
                // Spawn particles outside the boundary
                do {
                    this.x = Math.random() * canvas.width;
                    this.y = Math.random() * canvas.height;
                } while (this.isInsideBoundary());

                this.speedX = (Math.random() - 0.5) * 0.4;
                this.speedY = (Math.random() - 0.5) * 0.4;
            }

            this.baseSize = Math.random() * 2.5 + 1.5;
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
            // Store current position in trail before moving
            this.trail.unshift({ x: this.x, y: this.y });
            if (this.trail.length > TRAIL_LENGTH) {
                this.trail.pop();
            }

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

                // Clear trail on bounce to avoid visual artifacts through boundary
                this.trail = [];
            }

            // Wrap around edges
            if (this.x < 0) { this.x = canvas.width; this.trail = []; }
            if (this.x > canvas.width) { this.x = 0; this.trail = []; }
            if (this.y < 0) { this.y = canvas.height; this.trail = []; }
            if (this.y > canvas.height) { this.y = 0; this.trail = []; }
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
            let r, g, b;
            if (this.type === 'body') {
                r = 163; g = 113; b = 247; // Purple
            } else if (this.type === 'mind') {
                r = 240; g = 180; b = 41; // Gold
            } else {
                r = 88; g = 166; b = 255; // Cyan
            }

            // Draw ethereal trail
            if (this.trail.length > 2) {
                ctx.beginPath();
                ctx.moveTo(this.x, this.y);
                for (let i = 0; i < this.trail.length; i++) {
                    const t = this.trail[i];
                    ctx.lineTo(t.x, t.y);
                }

                // Gradient stroke for trail - more visible
                const gradient = ctx.createLinearGradient(
                    this.x, this.y,
                    this.trail[this.trail.length - 1].x,
                    this.trail[this.trail.length - 1].y
                );
                gradient.addColorStop(0, `rgba(${r}, ${g}, ${b}, ${opacity * 0.6})`);
                gradient.addColorStop(0.5, `rgba(${r}, ${g}, ${b}, ${opacity * 0.3})`);
                gradient.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0)`);

                ctx.strokeStyle = gradient;
                ctx.lineWidth = size * 1.2;
                ctx.lineCap = 'round';
                ctx.lineJoin = 'round';
                ctx.stroke();
            }

            // Draw as mini circumpunct: ring + dot
            const ringColor = `rgba(${r}, ${g}, ${b}, ${opacity})`;
            const dotColor = `rgba(${r}, ${g}, ${b}, ${opacity * 0.8})`;

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

        // Spawn most particles normally
        const normalCount = Math.floor(count * 0.85);
        for (let i = 0; i < normalCount; i++) {
            particles.push(new Particle(false));
        }

        // Spawn just a few particles aimed at the circumpunct for initial collisions
        // Staggered distances so they arrive one at a time over ~10 seconds
        const collisionCount = Math.min(5, count - normalCount);
        for (let i = 0; i < collisionCount; i++) {
            particles.push(new Particle(true, i));
        }
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

        // Increment time for aurora pulsing
        time++;

        // Draw aurora/nebula background first (behind everything)
        auroraBlobs.forEach(blob => {
            blob.update();
            blob.draw();
        });

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

    // =========================================
    // Soul Movement System
    // The soul (center dot) follows cursor + wanders when idle
    // =========================================
    const soulMoving = document.getElementById('eye-moving');
    const circumpunctContainer = document.querySelector('.circumpunct-container');

    if (soulMoving && circumpunctContainer) {
        // Get pupil and highlight elements for parallax effect
        const soulPupil = soulMoving.querySelector('.soul-pupil');
        const soulHighlight = soulMoving.querySelector('.soul-highlight');

        // Movement constraints (how far soul can move from center)
        // Soul iris r=32, mind zone at r=60, keep soul inside mind area
        const MAX_OFFSET = 25; // Stay mostly within the mind field
        const PUPIL_PARALLAX = 0.25; // Pupil moves 25% extra for depth illusion

        // Current position (offset from center)
        let currentX = 0;
        let currentY = 0;
        let targetX = 0;
        let targetY = 0;

        // Idle wandering state
        let isIdle = true;
        let idleTimeout = null;
        let wanderAngle = Math.random() * Math.PI * 2;
        let wanderSpeed = 0.0025; // Slower wandering
        let lastWanderTime = 0;
        const IDLE_DELAY = 2000; // ms before starting idle wander

        // Convert page coordinates to soul offset
        function getSoulOffset(pageX, pageY) {
            const rect = circumpunctContainer.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;

            // Direction from center to cursor
            const dx = pageX - centerX;
            const dy = pageY - centerY;
            const distance = Math.sqrt(dx * dx + dy * dy);

            // Scale factor - moves more when cursor is closer
            const maxDistance = Math.max(window.innerWidth, window.innerHeight);
            const normalizedDist = Math.min(distance / (maxDistance * 0.3), 1);
            const offsetScale = MAX_OFFSET * (0.3 + normalizedDist * 0.7);

            if (distance > 0) {
                return {
                    x: (dx / distance) * Math.min(offsetScale, MAX_OFFSET),
                    y: (dy / distance) * Math.min(offsetScale, MAX_OFFSET)
                };
            }
            return { x: 0, y: 0 };
        }

        // Idle wandering - gentle random movement (slower, less frequent)
        function updateWander(timestamp) {
            if (!isIdle) return;

            // Change direction occasionally (doubled interval = half as frequent)
            if (timestamp - lastWanderTime > 4000 + Math.random() * 6000) {
                wanderAngle += (Math.random() - 0.5) * Math.PI * 0.5;
                wanderSpeed = 0.0015 + Math.random() * 0.002; // Half speed
                lastWanderTime = timestamp;
            }

            // Gentle circular/random motion
            const wanderRadius = MAX_OFFSET * 0.4;
            targetX = Math.cos(wanderAngle + timestamp * wanderSpeed) * wanderRadius;
            targetY = Math.sin(wanderAngle + timestamp * wanderSpeed * 0.7) * wanderRadius;
        }

        // Smooth lerp toward target
        function updateSoulPosition() {
            const lerp = 0.08; // Smoothing factor
            currentX += (targetX - currentX) * lerp;
            currentY += (targetY - currentY) * lerp;

            // Apply transform to soul group
            soulMoving.style.transform = `translate(${currentX}px, ${currentY}px)`;

            // Apply parallax offset to pupil for spherical depth illusion
            if (soulPupil) {
                const pupilOffsetX = currentX * PUPIL_PARALLAX;
                const pupilOffsetY = currentY * PUPIL_PARALLAX;
                soulPupil.setAttribute('cx', 150 + pupilOffsetX);
                soulPupil.setAttribute('cy', 150 + pupilOffsetY);
            }

            // Move highlight opposite direction slightly (stays on light source side)
            if (soulHighlight) {
                const highlightOffsetX = currentX * PUPIL_PARALLAX * 0.5;
                const highlightOffsetY = currentY * PUPIL_PARALLAX * 0.5;
                soulHighlight.setAttribute('cx', 140 + highlightOffsetX);
                soulHighlight.setAttribute('cy', 142 + highlightOffsetY);
            }
        }

        // Mouse/touch move handler
        function handlePointerMove(e) {
            const pageX = e.touches ? e.touches[0].pageX : e.pageX;
            const pageY = e.touches ? e.touches[0].pageY : e.pageY;

            const offset = getSoulOffset(pageX, pageY);
            targetX = offset.x;
            targetY = offset.y;

            // Reset idle state
            isIdle = false;
            clearTimeout(idleTimeout);
            idleTimeout = setTimeout(() => {
                isIdle = true;
                lastWanderTime = performance.now();
            }, IDLE_DELAY);
        }

        // Mouse leave - return to idle
        function handlePointerLeave() {
            clearTimeout(idleTimeout);
            idleTimeout = setTimeout(() => {
                isIdle = true;
                lastWanderTime = performance.now();
            }, 500);
        }

        // Animation loop for soul
        function animateSoul(timestamp) {
            if (isIdle) {
                updateWander(timestamp);
            }
            updateSoulPosition();
            requestAnimationFrame(animateSoul);
        }

        // Event listeners
        document.addEventListener('mousemove', handlePointerMove);
        document.addEventListener('touchmove', handlePointerMove, { passive: true });
        document.addEventListener('mouseleave', handlePointerLeave);

        // Start animation
        requestAnimationFrame(animateSoul);

        // Start in idle mode
        lastWanderTime = performance.now();
    }
})();
