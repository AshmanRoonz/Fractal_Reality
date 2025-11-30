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
    // Particle Background
    // =========================================
    const canvas = document.getElementById('particles');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let particles = [];
    let animationId;
    let mouseX = 0, mouseY = 0;

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        initParticles();
    }

    class Particle {
        constructor() {
            this.reset();
        }

        reset() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2 + 0.5;
            this.speedX = (Math.random() - 0.5) * 0.3;
            this.speedY = (Math.random() - 0.5) * 0.3;
            this.opacity = Math.random() * 0.5 + 0.1;
            const colors = [[163, 113, 247], [240, 180, 41], [88, 166, 255]];
            this.color = colors[Math.floor(Math.random() * colors.length)];
        }

        update() {
            this.x += this.speedX;
            this.y += this.speedY;

            const dx = mouseX - this.x;
            const dy = mouseY - this.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 150) {
                const force = (150 - dist) / 150 * 0.02;
                this.x -= dx * force;
                this.y -= dy * force;
            }

            if (this.x < 0) this.x = canvas.width;
            if (this.x > canvas.width) this.x = 0;
            if (this.y < 0) this.y = canvas.height;
            if (this.y > canvas.height) this.y = 0;
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(${this.color[0]}, ${this.color[1]}, ${this.color[2]}, ${this.opacity})`;
            ctx.fill();
        }
    }

    function initParticles() {
        const count = Math.min(80, Math.floor((canvas.width * canvas.height) / 15000));
        particles = [];
        for (let i = 0; i < count; i++) particles.push(new Particle());
    }

    function drawConnections() {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 120) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(255, 255, 255, ${(1 - dist / 120) * 0.15})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
        }
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => { p.update(); p.draw(); });
        drawConnections();
        animationId = requestAnimationFrame(animate);
    }

    function handlePointer(e) {
        const point = e.touches ? e.touches[0] : e;
        mouseX = point.clientX;
        mouseY = point.clientY;
    }

    document.addEventListener('mousemove', handlePointer);
    document.addEventListener('touchmove', handlePointer, { passive: true });

    window.addEventListener('resize', resize);
    resize();
    animate();

    document.addEventListener('visibilitychange', () => {
        if (document.hidden) cancelAnimationFrame(animationId);
        else animate();
    });
})();
