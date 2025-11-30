/**
 * Subtle animated background & Circumpunct animation
 */

(function() {
    // =========================================
    // Animated Circumpunct (⊙)
    // =========================================
    const circCanvas = document.getElementById('circumpunct');
    if (circCanvas) {
        const cCtx = circCanvas.getContext('2d');
        const size = 360;
        circCanvas.width = size;
        circCanvas.height = size;

        const center = size / 2;
        let time = 0;

        // Field particles orbiting in mind zone
        const fieldParticles = [];
        for (let i = 0; i < 8; i++) {
            fieldParticles.push({
                angle: (Math.PI * 2 * i) / 8,
                radius: 45 + Math.random() * 20,
                speed: 0.003 + Math.random() * 0.002,
                size: 2 + Math.random() * 2,
                opacity: 0.4 + Math.random() * 0.3
            });
        }

        function drawCircumpunct() {
            cCtx.clearRect(0, 0, size, size);
            time += 0.008;

            // ○ Body - outer ring (purple)
            const ringRadius = 65;
            const ringPulse = Math.sin(time * 0.4) * 2;

            // Ring glow
            const ringGlow = cCtx.createRadialGradient(
                center, center, ringRadius - 8,
                center, center, ringRadius + 25
            );
            ringGlow.addColorStop(0, 'rgba(163, 113, 247, 0)');
            ringGlow.addColorStop(0.5, 'rgba(163, 113, 247, 0.15)');
            ringGlow.addColorStop(1, 'rgba(163, 113, 247, 0)');
            cCtx.beginPath();
            cCtx.arc(center, center, ringRadius + 15, 0, Math.PI * 2);
            cCtx.fillStyle = ringGlow;
            cCtx.fill();

            // Ring stroke
            cCtx.beginPath();
            cCtx.arc(center, center, ringRadius + ringPulse, 0, Math.PI * 2);
            cCtx.strokeStyle = `rgba(163, 113, 247, ${0.5 + Math.sin(time * 0.4) * 0.15})`;
            cCtx.lineWidth = 3;
            cCtx.stroke();

            // Φ Mind - field particles (gold)
            fieldParticles.forEach(p => {
                p.angle += p.speed;
                const wobble = Math.sin(time * 1.5 + p.angle * 2) * 6;
                const x = center + Math.cos(p.angle) * (p.radius + wobble);
                const y = center + Math.sin(p.angle) * (p.radius + wobble);

                cCtx.beginPath();
                cCtx.arc(x, y, p.size, 0, Math.PI * 2);
                const pulse = 0.6 + Math.sin(time * 2 + p.angle) * 0.4;
                cCtx.fillStyle = `rgba(240, 180, 41, ${p.opacity * pulse})`;
                cCtx.fill();
            });

            // • Soul - center dot (cyan)
            const corePulse = Math.sin(time * 0.6) * 3;
            const coreRadius = 18 + corePulse;

            // Core glow
            const coreGlow = cCtx.createRadialGradient(
                center, center, 0,
                center, center, coreRadius + 20
            );
            coreGlow.addColorStop(0, 'rgba(88, 166, 255, 0.9)');
            coreGlow.addColorStop(0.4, 'rgba(88, 166, 255, 0.3)');
            coreGlow.addColorStop(0.8, 'rgba(88, 166, 255, 0.1)');
            coreGlow.addColorStop(1, 'rgba(88, 166, 255, 0)');
            cCtx.beginPath();
            cCtx.arc(center, center, coreRadius + 20, 0, Math.PI * 2);
            cCtx.fillStyle = coreGlow;
            cCtx.fill();

            // Core
            cCtx.beginPath();
            cCtx.arc(center, center, coreRadius, 0, Math.PI * 2);
            cCtx.fillStyle = `rgba(88, 166, 255, ${0.85 + Math.sin(time * 0.6) * 0.15})`;
            cCtx.fill();

            requestAnimationFrame(drawCircumpunct);
        }

        drawCircumpunct();
    }

    // =========================================
    // Background Particles
    // =========================================
    const canvas = document.getElementById('bg');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let particles = [];

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        init();
    }

    function init() {
        const count = Math.floor((canvas.width * canvas.height) / 20000);
        particles = [];
        for (let i = 0; i < count; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                r: Math.random() * 1.5 + 0.5,
                dx: (Math.random() - 0.5) * 0.2,
                dy: (Math.random() - 0.5) * 0.2,
                opacity: Math.random() * 0.3 + 0.1
            });
        }
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        particles.forEach(p => {
            // Move
            p.x += p.dx;
            p.y += p.dy;

            // Wrap
            if (p.x < 0) p.x = canvas.width;
            if (p.x > canvas.width) p.x = 0;
            if (p.y < 0) p.y = canvas.height;
            if (p.y > canvas.height) p.y = 0;

            // Draw
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(88, 166, 255, ${p.opacity})`;
            ctx.fill();
        });

        requestAnimationFrame(draw);
    }

    // Scroll reveal for sections
    const sections = document.querySelectorAll('.section');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });

    sections.forEach(s => observer.observe(s));

    window.addEventListener('resize', resize);
    resize();
    draw();
})();
