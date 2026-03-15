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

})();
