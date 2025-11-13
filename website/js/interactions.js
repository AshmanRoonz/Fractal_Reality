/**
 * Interactive Elements
 * Handles scale explorer and other dynamic interactions
 */

// Scale Explorer Data
const scaleData = {
    cosmic: {
        title: 'Cosmic Scale',
        description: 'At the cosmic scale, you are a finite part (X) within the universal whole',
        formula: '⊙_universe = ∞_universe ⊗ X_universe (you are part of X_universe)'
    },
    planetary: {
        title: 'Planetary Scale',
        description: 'You are part of Earth\'s wholeness - a node in Gaia\'s network',
        formula: '⊙_Earth = ∞_Earth ⊗ X_Earth (you are part of X_Earth)'
    },
    human: {
        title: 'Your Scale',
        description: 'At this scale, you are a complete whole (⊙) - both ∞ and X unified',
        formula: '⊙_you = ∞_you ⊗ X_you'
    },
    cellular: {
        title: 'Cellular Scale',
        description: 'To your cells, you are the infinite encompassing field (∞)',
        formula: '⊙_cell = ∞_you ⊗ X_cell (you are the ∞ for your cells)'
    },
    quantum: {
        title: 'Quantum Scale',
        description: 'You contain quantum wholes - atoms, molecules, all conscious at their scale',
        formula: '⊙_quantum = ∞_you ⊗ X_quantum (you encompass quantum ⊙s)'
    }
};

// Initialize interactions when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initScaleExplorer();
    initIdentityCards();
    initSmoothScroll();
    initPathHoverEffects();
});

/**
 * Scale Explorer Interactions
 */
function initScaleExplorer() {
    const markers = document.querySelectorAll('.scale-marker');
    const vizTitle = document.getElementById('vizTitle');
    const vizDescription = document.getElementById('vizDescription');
    const vizFormula = document.getElementById('vizFormula');

    markers.forEach(marker => {
        marker.addEventListener('click', () => {
            // Remove active class from all markers
            markers.forEach(m => m.classList.remove('active'));

            // Add active class to clicked marker
            marker.classList.add('active');

            // Get scale data
            const scale = marker.dataset.scale;
            const data = scaleData[scale];

            // Update visualization with animation
            updateVisualization(vizTitle, vizDescription, vizFormula, data);
        });

        // Add hover effect
        marker.addEventListener('mouseenter', () => {
            if (!marker.classList.contains('active')) {
                marker.style.opacity = '0.8';
            }
        });

        marker.addEventListener('mouseleave', () => {
            marker.style.opacity = '1';
        });
    });
}

function updateVisualization(titleEl, descEl, formulaEl, data) {
    // Fade out
    titleEl.style.opacity = '0';
    descEl.style.opacity = '0';
    formulaEl.style.opacity = '0';

    setTimeout(() => {
        titleEl.textContent = data.title;
        descEl.textContent = data.description;
        formulaEl.textContent = data.formula;

        // Fade in
        titleEl.style.transition = 'opacity 0.5s ease';
        descEl.style.transition = 'opacity 0.5s ease';
        formulaEl.style.transition = 'opacity 0.5s ease';

        titleEl.style.opacity = '1';
        descEl.style.opacity = '1';
        formulaEl.style.opacity = '1';
    }, 300);
}

/**
 * Identity Cards Interaction
 */
function initIdentityCards() {
    const cards = document.querySelectorAll('.identity-card');

    cards.forEach(card => {
        card.addEventListener('click', () => {
            // Pulse animation
            card.style.transform = 'scale(1.05)';
            setTimeout(() => {
                card.style.transform = '';
            }, 200);
        });
    });
}

/**
 * Smooth Scroll for Internal Links
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Path Cards Hover Effects
 */
function initPathHoverEffects() {
    const pathCards = document.querySelectorAll('.path-card');

    pathCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            // Add glow effect
            card.style.transition = 'all 0.4s ease';
        });

        card.addEventListener('mousemove', (e) => {
            // Subtle 3D tilt effect based on mouse position
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = (y - centerY) / 20;
            const rotateY = (centerX - x) / 20;

            card.style.transform = `
                perspective(1000px)
                rotateX(${rotateX}deg)
                rotateY(${rotateY}deg)
                translateY(-15px)
                scale(1.02)
            `;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
        });
    });
}

/**
 * Parallax Effect for Sections (optional enhancement)
 */
function initParallax() {
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.hero-content, .core-equation');

        parallaxElements.forEach(el => {
            const speed = 0.5;
            el.style.transform = `translateY(${scrolled * speed}px)`;
        });
    });
}

/**
 * Intersection Observer for Fade-in Animations
 */
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe all sections
    document.querySelectorAll('section').forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(50px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(section);
    });
}

// Initialize scroll animations
initScrollAnimations();

/**
 * Typing Effect for Hero Text (Optional Enhancement)
 */
function typeWriterEffect(element, text, speed = 100) {
    let i = 0;
    element.textContent = '';

    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }

    type();
}

/**
 * Dynamic Background Color Based on Scroll
 */
function initDynamicBackground() {
    window.addEventListener('scroll', () => {
        const scrollPercent = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;

        // Shift hue based on scroll position (representing ∇ ⊗ ℰ cycle)
        const hue = 250 + (scrollPercent / 100) * 60; // Purple to cyan
        document.body.style.backgroundColor = `hsl(${hue}, 20%, 8%)`;
    });
}

// Optional: Initialize dynamic background
// initDynamicBackground();
