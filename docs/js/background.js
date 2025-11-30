/**
 * Subtle animated background
 * Simple particles that drift slowly
 */

(function() {
    // =========================================
    // Animated Circumpunct (⊙)
    // =========================================
    const circumpunctCanvas = document.getElementById('circumpunct');
    if (circumpunctCanvas) {
        const cCtx = circumpunctCanvas.getContext('2d');
        const size = 400; // High res for crisp rendering
        circumpunctCanvas.width = size;
        circumpunctCanvas.height = size;

        const center = size / 2;
        let time = 0;

        // Field particles (Φ Mind)
        const fieldParticles = [];
        for (let i = 0; i < 12; i++) {
            fieldParticles.push({
                angle: (Math.PI * 2 * i) / 12,
                radius: 50 + Math.random() * 30,
                speed: 0.002 + Math.random() * 0.003,
                size: 1.5 + Math.random() * 1.5,
                opacity: 0.3 + Math.random() * 0.3
            });
        }

        function drawCircumpunct() {
            cCtx.clearRect(0, 0, size, size);
            time += 0.01;

            // Outer ring glow (○ Body) - purple
            const ringRadius = 70;
            const ringPulse = Math.sin(time * 0.5) * 3;

            // Outer glow
            const ringGradient = cCtx.createRadialGradient(
                center, center, ringRadius - 10 + ringPulse,
                center, center, ringRadius + 20 + ringPulse
            );
            ringGradient.addColorStop(0, 'rgba(163, 113, 247, 0)');
            ringGradient.addColorStop(0.5, 'rgba(163, 113, 247, 0.15)');
            ringGradient.addColorStop(1, 'rgba(163, 113, 247, 0)');

            cCtx.beginPath();
            cCtx.arc(center, center, ringRadius + 10 + ringPulse, 0, Math.PI * 2);
            cCtx.fillStyle = ringGradient;
            cCtx.fill();

            // Ring stroke
            cCtx.beginPath();
            cCtx.arc(center, center, ringRadius + ringPulse, 0, Math.PI * 2);
            cCtx.strokeStyle = `rgba(163, 113, 247, ${0.4 + Math.sin(time * 0.5) * 0.1})`;
            cCtx.lineWidth = 2;
            cCtx.stroke();

            // Field particles (Φ Mind) - gold
            fieldParticles.forEach(p => {
                p.angle += p.speed;
                const wobble = Math.sin(time * 2 + p.angle * 3) * 8;
                const x = center + Math.cos(p.angle) * (p.radius + wobble);
                const y = center + Math.sin(p.angle) * (p.radius + wobble);

                cCtx.beginPath();
                cCtx.arc(x, y, p.size, 0, Math.PI * 2);
                cCtx.fillStyle = `rgba(240, 180, 41, ${p.opacity * (0.7 + Math.sin(time + p.angle) * 0.3)})`;
                cCtx.fill();
            });

            // Draw subtle connections between nearby particles
            for (let i = 0; i < fieldParticles.length; i++) {
                const p1 = fieldParticles[i];
                const p2 = fieldParticles[(i + 1) % fieldParticles.length];
                const wobble1 = Math.sin(time * 2 + p1.angle * 3) * 8;
                const wobble2 = Math.sin(time * 2 + p2.angle * 3) * 8;
                const x1 = center + Math.cos(p1.angle) * (p1.radius + wobble1);
                const y1 = center + Math.sin(p1.angle) * (p1.radius + wobble1);
                const x2 = center + Math.cos(p2.angle) * (p2.radius + wobble2);
                const y2 = center + Math.sin(p2.angle) * (p2.radius + wobble2);

                cCtx.beginPath();
                cCtx.moveTo(x1, y1);
                cCtx.lineTo(x2, y2);
                cCtx.strokeStyle = 'rgba(240, 180, 41, 0.1)';
                cCtx.lineWidth = 0.5;
                cCtx.stroke();
            }

            // Center dot glow (• Soul) - cyan
            const corePulse = Math.sin(time * 0.8) * 2;
            const coreRadius = 12 + corePulse;

            // Inner glow
            const coreGradient = cCtx.createRadialGradient(
                center, center, 0,
                center, center, coreRadius + 15
            );
            coreGradient.addColorStop(0, 'rgba(88, 166, 255, 0.9)');
            coreGradient.addColorStop(0.3, 'rgba(88, 166, 255, 0.4)');
            coreGradient.addColorStop(0.7, 'rgba(88, 166, 255, 0.1)');
            coreGradient.addColorStop(1, 'rgba(88, 166, 255, 0)');

            cCtx.beginPath();
            cCtx.arc(center, center, coreRadius + 15, 0, Math.PI * 2);
            cCtx.fillStyle = coreGradient;
            cCtx.fill();

            // Core
            cCtx.beginPath();
            cCtx.arc(center, center, coreRadius, 0, Math.PI * 2);
            cCtx.fillStyle = `rgba(88, 166, 255, ${0.8 + Math.sin(time * 0.8) * 0.2})`;
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
