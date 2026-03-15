/**
 * Circumpunct Interactive Demo
 * Tap the ⊙ to explore Body, Mind, Soul
 */

(function() {
    'use strict';

    // Elements - now CSS div zones with data-zone attribute
    const zones = document.querySelectorAll('[data-zone]');
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
        document.body.style.overflow = 'hidden';
        panel.scrollTop = 0;
    }

    // Close all panels
    function closeAllPanels() {
        panels.forEach(panel => panel.classList.remove('open'));
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
    let outwardRipples = [];
    let animationId;
    let centerX, centerY, boundaryRadius, soulRadius;
    let time = 0;

    // Aurora blobs
    const auroraBlobs = [];
    const AURORA_COUNT = 5;

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const circumpunctEl = document.querySelector('.circumpunct-container');
        if (circumpunctEl) {
            const rect = circumpunctEl.getBoundingClientRect();
            centerX = rect.left + rect.width / 2;
            centerY = rect.top + rect.height / 2;
            boundaryRadius = Math.min(rect.width, rect.height) * 0.4;
        } else {
            centerX = canvas.width / 2;
            centerY = canvas.height / 2;
            boundaryRadius = Math.min(canvas.width, canvas.height) * 0.18;
        }
        soulRadius = boundaryRadius * 0.23;
        initParticles();
        initAurora();
    }

    class AuroraBlob {
        constructor() {
            this.reset();
        }

        reset() {
            const angle = Math.random() * Math.PI * 2;
            const dist = canvas.width * 0.3 + Math.random() * canvas.width * 0.4;
            this.x = centerX + Math.cos(angle) * dist;
            this.y = centerY + Math.sin(angle) * dist;
            this.radius = 100 + Math.random() * 200;
            this.vx = (Math.random() - 0.5) * 0.15;
            this.vy = (Math.random() - 0.5) * 0.15;
            const types = ['body', 'mind', 'soul'];
            this.type = types[Math.floor(Math.random() * types.length)];
            this.phase = Math.random() * Math.PI * 2;
            this.pulseSpeed = 0.005 + Math.random() * 0.01;
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;
            const dx = centerX - this.x;
            const dy = centerY - this.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist > canvas.width * 0.5) {
                this.vx += dx * 0.00001;
                this.vy += dy * 0.00001;
            }
            if (this.x < -this.radius) this.x = canvas.width + this.radius;
            if (this.x > canvas.width + this.radius) this.x = -this.radius;
            if (this.y < -this.radius) this.y = canvas.height + this.radius;
            if (this.y > canvas.height + this.radius) this.y = -this.radius;
        }

        draw() {
            const pulse = Math.sin(time * this.pulseSpeed + this.phase) * 0.5 + 0.5;
            const alpha = 0.03 + pulse * 0.02;
            let r, g, b;
            if (this.type === 'body') { r = 163; g = 113; b = 247; }
            else if (this.type === 'mind') { r = 240; g = 180; b = 41; }
            else { r = 88; g = 166; b = 255; }
            const gradient = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.radius * (0.8 + pulse * 0.4));
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

    class Lightning {
        constructor(angle, particleType) {
            this.angle = angle;
            this.life = 1.0;
            this.decay = 0.04;
            this.type = particleType;
            this.hasTriggeredResponse = false;
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
                const jitter = (i > 0 && i < steps) ? (Math.random() - 0.5) * 0.3 : 0;
                const a = this.angle + jitter;
                segments.push({ x: centerX + Math.cos(a) * r, y: centerY + Math.sin(a) * r });
            }
            return segments;
        }

        update() {
            this.life -= this.decay;
            if (!this.hasTriggeredResponse && this.life < 0.5) {
                this.hasTriggeredResponse = true;
                const responseAngle = this.angle + (Math.random() - 0.5) * 0.3;
                outwardRipples.push(new OutwardRipple(responseAngle, this.type));
            }
            return this.life > 0;
        }

        draw() {
            if (this.segments.length < 2) return;
            let color;
            if (this.type === 'body') color = `rgba(163, 113, 247, ${this.life * 0.8})`;
            else if (this.type === 'mind') color = `rgba(240, 180, 41, ${this.life * 0.8})`;
            else color = `rgba(88, 166, 255, ${this.life * 0.8})`;
            ctx.beginPath();
            ctx.moveTo(this.segments[0].x, this.segments[0].y);
            for (let i = 1; i < this.segments.length; i++) ctx.lineTo(this.segments[i].x, this.segments[i].y);
            ctx.strokeStyle = color;
            ctx.lineWidth = 2 * this.life;
            ctx.stroke();
            ctx.strokeStyle = color.replace(this.life * 0.8, this.life * 0.3);
            ctx.lineWidth = 6 * this.life;
            ctx.stroke();
        }
    }

    class Ripple {
        constructor(angle, particleType) {
            this.angle = angle;
            this.radius = boundaryRadius;
            this.speed = 0.8;
            this.life = 1.0;
            this.type = particleType;
            this.hueShift = Math.random() * 20 - 10;
            this.direction = 'inward';
        }
        update() {
            this.radius -= this.speed;
            this.life = Math.max(0, (this.radius - soulRadius) / (boundaryRadius - soulRadius));
            return this.radius > soulRadius;
        }
    }

    class OutwardRipple {
        constructor(angle, sourceType) {
            this.angle = angle;
            this.radius = soulRadius;
            this.speed = 1.2;
            this.life = 1.0;
            this.sourceType = sourceType;
            this.direction = 'outward';
            this.hueBase = 200;
        }
        update() {
            this.radius += this.speed;
            this.life = Math.max(0, (boundaryRadius - this.radius) / (boundaryRadius - soulRadius));
            return this.radius < boundaryRadius;
        }
    }

    function getFieldIntensity(r, angle) {
        let inwardWave = 0;
        let outwardWave = 0;
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
        outwardRipples.forEach(ripple => {
            const rippleDist = Math.abs(r - ripple.radius);
            let angleDiff = Math.abs(angle - ripple.angle);
            if (angleDiff > Math.PI) angleDiff = 2 * Math.PI - angleDiff;
            const spread = Math.PI * 0.5 * (1 - ripple.life) + 0.4;
            if (rippleDist < 25 && angleDiff < spread) {
                const radialWave = Math.cos((rippleDist / 25) * Math.PI) * ripple.life;
                const angularFade = Math.cos((angleDiff / spread) * Math.PI / 2);
                outwardWave += radialWave * angularFade;
            }
        });
        return { inward: inwardWave, outward: outwardWave, total: inwardWave + outwardWave };
    }

    function drawMindField() {
        const fieldInner = soulRadius + 3;
        const fieldOuter = boundaryRadius - 3;
        const rings = isMobile ? 8 : 12;
        const segments = isMobile ? 24 : 36;
        for (let ringIdx = 0; ringIdx < rings; ringIdx++) {
            const r = fieldInner + (fieldOuter - fieldInner) * (ringIdx / rings);
            for (let seg = 0; seg < segments; seg++) {
                const angle = (seg / segments) * Math.PI * 2;
                const nextAngle = ((seg + 1) / segments) * Math.PI * 2;
                const waves = getFieldIntensity(r, angle);
                const inward = waves.inward;
                const outward = waves.outward;
                const total = Math.abs(inward) + Math.abs(outward);
                if (total > 0.05) {
                    const inwardRatio = Math.abs(inward) / (total + 0.01);
                    const outwardRatio = Math.abs(outward) / (total + 0.01);
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
        const hasInterference = ripples.length > 0 && outwardRipples.length > 0;
        if (hasInterference || ripples.length > 1 || outwardRipples.length > 1) {
            for (let r = fieldInner; r < fieldOuter; r += 8) {
                for (let a = 0; a < Math.PI * 2; a += Math.PI / 12) {
                    const waves = getFieldIntensity(r, a);
                    const total = Math.abs(waves.inward) + Math.abs(waves.outward);
                    if (total > 0.5) {
                        const x = centerX + Math.cos(a) * r;
                        const y = centerY + Math.sin(a) * r;
                        const bothPresent = Math.abs(waves.inward) > 0.2 && Math.abs(waves.outward) > 0.2;
                        let hue, saturation;
                        if (bothPresent) { hue = 180; saturation = 50; }
                        else if (Math.abs(waves.outward) > Math.abs(waves.inward)) { hue = 200; saturation = 90; }
                        else { hue = 45; saturation = 90; }
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

    const TRAIL_LENGTH = 20;

    class Particle {
        constructor(forceCollision = false, staggerIndex = 0) {
            this.trail = [];
            this.reset(forceCollision, staggerIndex);
        }

        reset(forceCollision = false, staggerIndex = 0) {
            this.trail = [];
            if (forceCollision) {
                const angle = Math.random() * Math.PI * 2;
                const staggerDist = 80 + staggerIndex * 60;
                const startDist = boundaryRadius + staggerDist + Math.random() * 40;
                this.x = centerX + Math.cos(angle) * startDist;
                this.y = centerY + Math.sin(angle) * startDist;
                const speed = 0.4 + Math.random() * 0.3;
                this.speedX = -Math.cos(angle) * speed;
                this.speedY = -Math.sin(angle) * speed;
            } else {
                do {
                    this.x = Math.random() * canvas.width;
                    this.y = Math.random() * canvas.height;
                } while (this.isInsideBoundary());
                this.speedX = (Math.random() - 0.5) * 0.8;
                this.speedY = (Math.random() - 0.5) * 0.8;
            }
            this.baseSize = Math.random() * 2.5 + 1.5;
            this.baseOpacity = Math.random() * 0.4 + 0.4;
            const types = ['body', 'mind', 'soul'];
            this.type = types[Math.floor(Math.random() * types.length)];
        }

        isInsideBoundary() {
            const dx = this.x - centerX;
            const dy = this.y - centerY;
            return Math.sqrt(dx * dx + dy * dy) < boundaryRadius + 25;
        }

        update() {
            this.trail.unshift({ x: this.x, y: this.y });
            if (this.trail.length > TRAIL_LENGTH) this.trail.pop();
            const dx = centerX - this.x;
            const dy = centerY - this.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist > boundaryRadius) {
                const gravity = 0.003;
                this.speedX += (dx / dist) * gravity;
                this.speedY += (dy / dist) * gravity;
            }
            this.x += this.speedX;
            this.y += this.speedY;
            const bdx = this.x - centerX;
            const bdy = this.y - centerY;
            const bdist = Math.sqrt(bdx * bdx + bdy * bdy);
            const bounceRadius = boundaryRadius + 18;
            if (bdist < bounceRadius) {
                const angle = Math.atan2(bdy, bdx);
                this.x = centerX + Math.cos(angle) * (bounceRadius + 2);
                this.y = centerY + Math.sin(angle) * (bounceRadius + 2);
                const normalX = bdx / bdist;
                const normalY = bdy / bdist;
                const dot = this.speedX * normalX + this.speedY * normalY;
                this.speedX = this.speedX - 2 * dot * normalX;
                this.speedY = this.speedY - 2 * dot * normalY;
                spawnLightningAndRipple(angle, this.type);
                this.trail = [];
            }
            if (this.x < 0) { this.x = canvas.width; this.trail = []; }
            if (this.x > canvas.width) { this.x = 0; this.trail = []; }
            if (this.y < 0) { this.y = canvas.height; this.trail = []; }
            if (this.y > canvas.height) { this.y = 0; this.trail = []; }
        }

        draw() {
            const dx = this.x - centerX;
            const dy = this.y - centerY;
            const distToCenter = Math.sqrt(dx * dx + dy * dy);
            const maxDist = Math.min(canvas.width, canvas.height) * 0.4;
            const proximity = Math.max(0, 1 - distToCenter / maxDist);
            const size = this.baseSize * (1 + proximity * 2);
            const opacity = this.baseOpacity + proximity * 0.5;
            let r, g, b;
            if (this.type === 'body') { r = 163; g = 113; b = 247; }
            else if (this.type === 'mind') { r = 240; g = 180; b = 41; }
            else { r = 88; g = 166; b = 255; }
            if (this.trail.length > 2) {
                ctx.beginPath();
                ctx.moveTo(this.x, this.y);
                for (let i = 0; i < this.trail.length; i++) ctx.lineTo(this.trail[i].x, this.trail[i].y);
                const gradient = ctx.createLinearGradient(this.x, this.y, this.trail[this.trail.length - 1].x, this.trail[this.trail.length - 1].y);
                gradient.addColorStop(0, `rgba(${r}, ${g}, ${b}, ${opacity * 0.6})`);
                gradient.addColorStop(0.5, `rgba(${r}, ${g}, ${b}, ${opacity * 0.3})`);
                gradient.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0)`);
                ctx.strokeStyle = gradient;
                ctx.lineWidth = size * 1.2;
                ctx.lineCap = 'round';
                ctx.lineJoin = 'round';
                ctx.stroke();
            }
            const ringColor = `rgba(${r}, ${g}, ${b}, ${opacity})`;
            const dotColor = `rgba(${r}, ${g}, ${b}, ${opacity * 0.8})`;
            ctx.beginPath();
            ctx.arc(this.x, this.y, size * 2, 0, Math.PI * 2);
            ctx.strokeStyle = ringColor;
            ctx.lineWidth = size * 0.3;
            ctx.stroke();
            ctx.beginPath();
            ctx.arc(this.x, this.y, size * 0.5, 0, Math.PI * 2);
            ctx.fillStyle = dotColor;
            ctx.fill();
        }
    }

    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
                     || window.innerWidth < 768;

    function initParticles() {
        const maxParticles = isMobile ? 25 : 50;
        const count = Math.min(maxParticles, Math.floor((canvas.width * canvas.height) / 25000));
        particles = [];
        const normalCount = Math.floor(count * 0.7);
        for (let i = 0; i < normalCount; i++) particles.push(new Particle(false));
        const collisionCount = count - normalCount;
        for (let i = 0; i < collisionCount; i++) particles.push(new Particle(true, i));
    }

    function lineCrossesBoundary(x1, y1, x2, y2) {
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
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < connectionRadius) {
                    if (lineCrossesBoundary(particles[i].x, particles[i].y, particles[j].x, particles[j].y)) continue;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(255, 255, 255, ${(1 - dist / connectionRadius) * 0.12})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
        }
        const connectionRange = Math.min(canvas.width, canvas.height) * 0.35;
        particles.forEach(p => {
            const dx = p.x - centerX;
            const dy = p.y - centerY;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist > boundaryRadius && dist < connectionRange) {
                const opacity = (1 - (dist - boundaryRadius) / (connectionRange - boundaryRadius)) * 0.4;
                const angle = Math.atan2(dy, dx);
                const boundaryX = centerX + Math.cos(angle) * boundaryRadius;
                const boundaryY = centerY + Math.sin(angle) * boundaryRadius;
                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(boundaryX, boundaryY);
                if (p.type === 'body') ctx.strokeStyle = `rgba(163, 113, 247, ${opacity})`;
                else if (p.type === 'mind') ctx.strokeStyle = `rgba(240, 180, 41, ${opacity})`;
                else ctx.strokeStyle = `rgba(88, 166, 255, ${opacity})`;
                ctx.lineWidth = 1;
                ctx.stroke();
            }
        });
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        time++;
        auroraBlobs.forEach(blob => { blob.update(); blob.draw(); });
        particles.forEach(p => { p.update(); p.draw(); });
        drawConnections();
        ripples = ripples.filter(r => r.update());
        outwardRipples = outwardRipples.filter(r => r.update());
        drawMindField();
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
