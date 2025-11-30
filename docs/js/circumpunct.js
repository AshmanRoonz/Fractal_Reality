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
    let animationId;
    let centerX, centerY;

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        centerX = canvas.width / 2;
        centerY = canvas.height / 2;
        initParticles();
    }

    class Particle {
        constructor() {
            this.reset();
        }

        reset() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.baseSize = Math.random() * 2 + 1;
            this.speedX = (Math.random() - 0.5) * 0.4;
            this.speedY = (Math.random() - 0.5) * 0.4;
            this.baseOpacity = Math.random() * 0.4 + 0.1;
            // Each particle is a mini circumpunct with body/mind/soul colors
            const types = ['body', 'mind', 'soul'];
            this.type = types[Math.floor(Math.random() * types.length)];
        }

        update() {
            this.x += this.speedX;
            this.y += this.speedY;

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

    function drawConnections() {
        const connectionRadius = 150;

        // Connect particles to each other
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < connectionRadius) {
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
        const boundaryRadius = Math.min(canvas.width, canvas.height) * 0.18; // The outer ring
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
        particles.forEach(p => { p.update(); p.draw(); });
        drawConnections();
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
