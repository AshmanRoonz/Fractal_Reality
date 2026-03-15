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
    // Static Particle Background - decorative dots
    // =========================================
    const canvas = document.getElementById('particles');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let dots = [];

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        initDots();
        drawDots();
    }

    function initDots() {
        const circEl = document.querySelector('.circumpunct-container');
        let cx, cy, br;
        if (circEl) {
            const rect = circEl.getBoundingClientRect();
            cx = rect.left + rect.width / 2;
            cy = rect.top + rect.height / 2;
            br = Math.min(rect.width, rect.height) * 0.45;
        } else {
            cx = canvas.width / 2;
            cy = canvas.height / 2;
            br = Math.min(canvas.width, canvas.height) * 0.2;
        }

        const count = Math.min(40, Math.floor((canvas.width * canvas.height) / 30000));
        dots = [];
        const types = ['body', 'mind', 'soul'];
        for (let i = 0; i < count; i++) {
            let x, y;
            do {
                x = Math.random() * canvas.width;
                y = Math.random() * canvas.height;
            } while (Math.sqrt((x - cx) ** 2 + (y - cy) ** 2) < br + 30);
            dots.push({
                x: x,
                y: y,
                size: Math.random() * 2 + 1,
                opacity: Math.random() * 0.3 + 0.2,
                type: types[Math.floor(Math.random() * types.length)]
            });
        }
    }

    function drawDots() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        dots.forEach(d => {
            let r, g, b;
            if (d.type === 'body') { r = 163; g = 113; b = 247; }
            else if (d.type === 'mind') { r = 240; g = 180; b = 41; }
            else { r = 88; g = 166; b = 255; }

            // Outer ring
            ctx.beginPath();
            ctx.arc(d.x, d.y, d.size * 2, 0, Math.PI * 2);
            ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, ${d.opacity * 0.6})`;
            ctx.lineWidth = d.size * 0.3;
            ctx.stroke();

            // Center dot
            ctx.beginPath();
            ctx.arc(d.x, d.y, d.size * 0.5, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${d.opacity})`;
            ctx.fill();
        });
    }

    window.addEventListener('resize', resize);
    resize();
})();
