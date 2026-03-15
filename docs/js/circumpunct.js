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
    // Floating Circumpuncts - bounce off boundary
    // with field ripples on impact
    // =========================================
    const canvas = document.getElementById('particles');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let particles = [];
    let ripples = [];
    let bolts = [];
    let centerX, centerY, boundaryRadius, soulRadius;
    let animId;

    const isMobile = window.innerWidth < 768;
    const PARTICLE_COUNT = isMobile ? 15 : 30;

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const el = document.querySelector('.circumpunct-container');
        if (el) {
            const r = el.getBoundingClientRect();
            centerX = r.left + r.width / 2;
            centerY = r.top + r.height / 2 + window.scrollY;
            boundaryRadius = Math.min(r.width, r.height) * 0.42;
        } else {
            centerX = canvas.width / 2;
            centerY = canvas.height / 2;
            boundaryRadius = Math.min(canvas.width, canvas.height) * 0.18;
        }
        soulRadius = boundaryRadius * 0.22;

        if (particles.length === 0) initParticles();
    }

    function initParticles() {
        particles = [];
        const types = ['body', 'mind', 'soul'];
        for (let i = 0; i < PARTICLE_COUNT; i++) {
            let x, y;
            do {
                x = Math.random() * canvas.width;
                y = Math.random() * canvas.height;
            } while (Math.sqrt((x - centerX) ** 2 + (y - centerY) ** 2) < boundaryRadius + 20);

            particles.push({
                x, y,
                vx: (Math.random() - 0.5) * 0.6,
                vy: (Math.random() - 0.5) * 0.6,
                size: Math.random() * 2 + 1.5,
                opacity: Math.random() * 0.3 + 0.3,
                type: types[Math.floor(Math.random() * 3)]
            });
        }
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const sy = window.scrollY;
        const cyScreen = centerY - sy;

        // Draw field ripples
        for (let i = ripples.length - 1; i >= 0; i--) {
            const rip = ripples[i];
            rip.radius -= rip.speed;
            rip.life = (rip.radius - soulRadius) / (boundaryRadius - soulRadius);
            if (rip.life <= 0) { ripples.splice(i, 1); continue; }

            ctx.beginPath();
            ctx.arc(centerX, cyScreen, rip.radius, rip.angle - rip.spread, rip.angle + rip.spread);
            ctx.strokeStyle = `rgba(240,180,41,${rip.life * 0.3})`;
            ctx.lineWidth = 2;
            ctx.stroke();

            rip.spread += 0.01;
        }

        // Draw lightning bolts
        for (let i = bolts.length - 1; i >= 0; i--) {
            const bolt = bolts[i];
            bolt.life -= 0.04;
            if (bolt.life <= 0) { bolts.splice(i, 1); continue; }

            ctx.beginPath();
            ctx.moveTo(bolt.segs[0].x, bolt.segs[0].y);
            for (let s = 1; s < bolt.segs.length; s++) ctx.lineTo(bolt.segs[s].x, bolt.segs[s].y);
            ctx.strokeStyle = `rgba(${bolt.r},${bolt.g},${bolt.b},${bolt.life * 0.7})`;
            ctx.lineWidth = 2 * bolt.life;
            ctx.stroke();
            // Glow pass
            ctx.strokeStyle = `rgba(${bolt.r},${bolt.g},${bolt.b},${bolt.life * 0.25})`;
            ctx.lineWidth = 6 * bolt.life;
            ctx.stroke();
        }

        // Update and draw particles
        for (let i = 0; i < particles.length; i++) {
            const p = particles[i];

            // Gentle gravity toward center
            const dx = centerX - p.x;
            const dy = cyScreen - p.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist > boundaryRadius) {
                p.vx += (dx / dist) * 0.002;
                p.vy += (dy / dist) * 0.002;
            }

            p.x += p.vx;
            p.y += p.vy;

            // Bounce off boundary
            const bx = p.x - centerX;
            const by = p.y - cyScreen;
            const bdist = Math.sqrt(bx * bx + by * by);
            if (bdist < boundaryRadius + 12) {
                const nx = bx / bdist;
                const ny = by / bdist;
                const dot = p.vx * nx + p.vy * ny;
                p.vx -= 2 * dot * nx;
                p.vy -= 2 * dot * ny;
                p.x = centerX + nx * (boundaryRadius + 14);
                p.y = cyScreen + ny * (boundaryRadius + 14);

                // Spawn inward ripple + lightning at impact point
                const hitAngle = Math.atan2(by, bx);
                if (ripples.length < 8) {
                    ripples.push({
                        radius: boundaryRadius,
                        angle: hitAngle,
                        spread: 0.3,
                        speed: 0.8,
                        life: 1
                    });
                }
                if (bolts.length < 5) {
                    // Build jagged path from boundary to soul
                    const segs = [];
                    const steps = 8;
                    for (let s = 0; s <= steps; s++) {
                        const t = s / steps;
                        const rad = boundaryRadius - (boundaryRadius - soulRadius) * t;
                        const jit = (s > 0 && s < steps) ? (Math.random() - 0.5) * 0.3 : 0;
                        const a = hitAngle + jit;
                        segs.push({ x: centerX + Math.cos(a) * rad, y: cyScreen + Math.sin(a) * rad });
                    }
                    let br, bg, bb;
                    if (p.type === 'body') { br = 163; bg = 113; bb = 247; }
                    else if (p.type === 'mind') { br = 240; bg = 180; bb = 41; }
                    else { br = 88; bg = 166; bb = 255; }
                    bolts.push({ segs, life: 1, r: br, g: bg, b: bb });
                }
            }

            // Wrap edges
            if (p.x < -10) p.x = canvas.width + 10;
            if (p.x > canvas.width + 10) p.x = -10;
            if (p.y < -10) p.y = canvas.height + 10;
            if (p.y > canvas.height + 10) p.y = -10;

            // Draw as mini circumpunct: ring + dot
            let r, g, b;
            if (p.type === 'body') { r = 163; g = 113; b = 247; }
            else if (p.type === 'mind') { r = 240; g = 180; b = 41; }
            else { r = 88; g = 166; b = 255; }

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size * 2, 0, Math.PI * 2);
            ctx.strokeStyle = `rgba(${r},${g},${b},${p.opacity * 0.5})`;
            ctx.lineWidth = 0.8;
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size * 0.5, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(${r},${g},${b},${p.opacity})`;
            ctx.fill();
        }

        animId = requestAnimationFrame(animate);
    }

    window.addEventListener('resize', resize);
    resize();
    animate();

    document.addEventListener('visibilitychange', () => {
        if (document.hidden) cancelAnimationFrame(animId);
        else animate();
    });

})();
