import React, { useEffect, useRef, useState } from 'react';

const EnhancedConsciousnessFractal = () => {
    const canvasRef = useRef(null);
    const animationRef = useRef(null);
    const [zoomLevel, setZoomLevel] = useState(1);
    const [showMetrics, setShowMetrics] = useState(true);
    const [showICE, setShowICE] = useState(true);
    const zoomRef = useRef(1);
    
    // Framework metrics
    const [metrics, setMetrics] = useState({
        fieldCoherence: 0,
        validationRate: 0,
        patternCount: 0,
        textureComplexity: 0,
        iceScore: { input: 0, output: 0 }
    });

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const width = canvas.width = window.innerWidth;
        const height = canvas.height = window.innerHeight;
        const centerX = width / 2;
        const centerY = height / 2;

        let time = 0;
        let chaos = { 
            x: Math.random() * 0.2, 
            y: Math.random() * 0.2, 
            z: Math.random() * 0.2 
        };
        let validatedPatterns = [];
        let circuits = [];
        let energyPulses = [];
        let brainClouds = [];
        let expandingCells = [];
        let brainFormed = false;
        let brainFormationProgress = 0;
        let systemCapacity = 1.0;
        let apertureSize = 1.0;

        let fieldCoherence = 0;
        let fieldResonance = [];
        let collectiveBreath = 0;
        
        // NEW: [ICE] validation tracking
        let iceValidations = { passed: 0, failed: 0 };
        let lastValidationCheck = 0;

        const updateChaos = (state) => {
            const dt = 0.005;
            const sigma = 10, rho = 28, beta = 8 / 3;
            const dx = sigma * (state.y - state.x) * dt;
            const dy = (state.x * (rho - state.z) - state.y) * dt;
            const dz = (state.x * state.y - beta * state.z) * dt;
            return {
                x: state.x + dx,
                y: state.y + dy,
                z: state.z + dz
            };
        };

        const checkBrainFormation = () => {
            const centerRadius = 120;
            const patternsInCenter = validatedPatterns.filter(p => {
                const dist = p.baseLength * p.scale;
                return dist < centerRadius;
            }).length;
            return patternsInCenter >= 15;
        };

        const calculateFieldCoherence = () => {
            if (!brainFormed || brainClouds.length === 0) return 0;
            let totalConnections = 0;
            let synchronizedConnections = 0;
            brainClouds.forEach(cloud => {
                cloud.connectedPatterns.forEach(pattern => {
                    totalConnections++;
                    const phaseDiff = Math.abs(Math.sin(time * 0.02 + cloud.phaseOffset) -
                        Math.sin(time * 0.02 + pattern.phaseOffset));
                    if (phaseDiff < 0.3) synchronizedConnections++;
                });
            });
            return totalConnections > 0 ? synchronizedConnections / totalConnections : 0;
        };

        // NEW: Calculate [ICE] validation scores
        const calculateICEScores = () => {
            let inputScore = 0;
            let outputScore = 0;
            let count = 0;
            
            validatedPatterns.forEach(p => {
                if (p.scale > 0.3) { // Pattern persists
                    count++;
                    // Input interface: parts → operator
                    const interfaceStrength = p.neighbors.length > 0 ? 0.8 : 0.3;
                    const centerAlignment = p.connectedToCloud ? 0.9 : 0.5;
                    const evidenceGrounding = p.baseLength > 0 ? 0.85 : 0.2;
                    inputScore += (interfaceStrength + centerAlignment + evidenceGrounding) / 3;
                    
                    // Output interface: operator → patterns
                    const outputInterface = p.scale > 0.5 ? 0.9 : p.scale;
                    const outputCoherence = p.circuitPartners.size > 0 ? 0.85 : 0.4;
                    const outputEvidence = p.gravitationalMass > 0 ? 0.8 : 0.5;
                    outputScore += (outputInterface + outputCoherence + outputEvidence) / 3;
                }
            });
            
            return {
                input: count > 0 ? inputScore / count : 0,
                output: count > 0 ? outputScore / count : 0
            };
        };

        const generateFieldResonance = () => {
            if (!brainFormed) return [];
            const resonances = [];
            const numResonances = Math.floor(fieldCoherence * 8);
            for (let i = 0; i < numResonances; i++) {
                const frequency = (i + 1) * 0.015;
                const amplitude = Math.sin(time * frequency) * fieldCoherence * 30;
                const angle = (i / numResonances) * Math.PI * 2;
                resonances.push({ angle, amplitude, frequency, phase: time * frequency });
            }
            return resonances;
        };

        class ExpandingCell {
            constructor(sourceCloud, birthTime) {
                this.sourceCloud = sourceCloud;
                this.birthTime = birthTime;
                this.age = 0;
                this.angle = sourceCloud.angle + (Math.random() - 0.5) * 0.3;
                this.distance = sourceCloud.distance;
                this.hue = sourceCloud.hue + (Math.random() - 0.5) * 20;
                this.expansionSpeed = 0.6 + Math.random() * 0.4;
                this.maxRadius = 12 + Math.random() * 18;
                this.currentRadius = 0;
                this.lifecycle = 0;
                this.lifecycleSpeed = 0.006 + Math.random() * 0.003;
                this.phaseOffset = Math.random() * Math.PI * 2;
                this.rotationSpeed = (Math.random() - 0.5) * 0.015;
                this.rotation = 0;
                this.fractalSeed = Math.random() * 4 - 2;
                this.fractalComplexity = 3 + Math.floor(Math.random() * 3);
            }

            update() {
                this.age++;
                this.lifecycle += this.lifecycleSpeed;
                this.distance += this.expansionSpeed;
                if (this.lifecycle < 1) {
                    this.currentRadius = this.maxRadius * this.lifecycle;
                } else if (this.lifecycle < 2) {
                    this.currentRadius = this.maxRadius;
                } else if (this.lifecycle < 3) {
                    this.currentRadius = this.maxRadius * (1 + Math.sin(this.age * 0.05) * 0.1);
                } else {
                    const decayProgress = (this.lifecycle - 3);
                    this.currentRadius = this.maxRadius * (1 - decayProgress);
                }
                this.rotation += this.rotationSpeed;
                this.x = centerX + Math.cos(this.angle) * this.distance;
                this.y = centerY + Math.sin(this.angle) * this.distance;
                return this.lifecycle < 4 && this.distance < Math.max(width, height);
            }

            drawFractalBranch(ctx, x, y, length, angle, depth, hue, alpha) {
                if (depth === 0 || length < 0.5) return;
                const endX = x + length * Math.cos(angle);
                const endY = y + length * Math.sin(angle);
                ctx.strokeStyle = `hsla(${hue}, 75%, 60%, ${alpha * (depth / this.fractalComplexity)})`;
                ctx.lineWidth = Math.max(0.3, depth * 0.5);
                ctx.beginPath();
                ctx.moveTo(x, y);
                ctx.lineTo(endX, endY);
                ctx.stroke();
                const branchAngle = Math.PI / 4 + this.fractalSeed * 0.2;
                const lengthMult = 0.65;
                this.drawFractalBranch(ctx, endX, endY, length * lengthMult, angle - branchAngle, depth - 1, hue + 5, alpha);
                this.drawFractalBranch(ctx, endX, endY, length * lengthMult, angle + branchAngle, depth - 1, hue - 5, alpha);
                if (depth > 2 && Math.abs(this.fractalSeed) > 0.5) {
                    this.drawFractalBranch(ctx, endX, endY, length * lengthMult * 0.8, angle, depth - 1, hue, alpha);
                }
            }

            draw(ctx) {
                if (this.currentRadius < 0.5) return;
                let alpha;
                if (this.lifecycle < 1) {
                    alpha = this.lifecycle * 0.4;
                } else if (this.lifecycle < 3) {
                    alpha = 0.4;
                } else {
                    const decayProgress = (this.lifecycle - 3);
                    alpha = 0.4 * (1 - decayProgress);
                }
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.rotation);
                const numBranches = 4 + Math.floor(Math.random() * 3);
                for (let i = 0; i < numBranches; i++) {
                    const angle = (i / numBranches) * Math.PI * 2;
                    const branchLength = this.currentRadius * 0.5;
                    this.drawFractalBranch(ctx, 0, 0, branchLength, angle, this.fractalComplexity, this.hue, alpha);
                }
                const glowSize = this.currentRadius * 0.15;
                ctx.shadowBlur = 8;
                ctx.shadowColor = `hsla(${this.hue}, 90%, 70%, ${alpha * 0.6})`;
                ctx.fillStyle = `hsla(${this.hue}, 85%, 75%, ${alpha * 0.7})`;
                ctx.beginPath();
                ctx.arc(0, 0, glowSize, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;
                ctx.restore();
            }
        }

        class BrainCloud {
            constructor(angle, distance, birthTime) {
                this.angle = angle;
                this.baseDistance = distance;
                this.distance = distance;
                this.birthTime = birthTime;
                this.phaseOffset = Math.random() * Math.PI * 2;
                this.hue = 200 + Math.random() * 60;
                this.baseHue = this.hue;
                this.alpha = 0;
                this.particles = [];
                this.connectedPatterns = [];
                this.energyLevel = 0;
                for (let i = 0; i < 30; i++) {
                    this.particles.push({
                        angle: angle + (Math.random() - 0.5) * 0.8,
                        distOffset: (Math.random() - 0.5) * 50,
                        size: 2 + Math.random() * 4,
                        phaseOffset: Math.random() * Math.PI * 2,
                        speed: 0.002 + Math.random() * 0.003,
                        energy: Math.random(),
                        targetPattern: null,
                        excitement: 0,
                        shape: 0,
                        targetShape: 0,
                        rotation: Math.random() * Math.PI * 2,
                        rotationSpeed: (Math.random() - 0.5) * 0.02,
                        nestingPatterns: []
                    });
                }
            }

            update(time, allPatterns, globalBreath) {
                const age = time - this.birthTime;
                if (age < 60) {
                    this.alpha = age / 60;
                } else {
                    this.alpha = Math.min(0.7, this.alpha);
                }
                const localWave = Math.sin(time * 0.01 + this.phaseOffset) * 10;
                const breathWave = globalBreath * 20;
                this.distance = this.baseDistance + localWave + breathWave;
                this.connectedPatterns = allPatterns.filter(p => {
                    if (!p || p.x === undefined || p.y === undefined) return false;
                    const angleDiff = Math.abs(this.angle - p.angle);
                    const normalizedDiff = Math.min(angleDiff, Math.PI * 2 - angleDiff);
                    return normalizedDiff < 0.9;
                });
                this.energyLevel = this.connectedPatterns.length * 0.1;
                this.connectedPatterns.forEach(pattern => {
                    pattern.cloudInfluence = this.hue;
                    pattern.connectedToCloud = true;
                    pattern.fieldEnergyBoost = this.energyLevel;
                });
            }

            spawnOutputCell(time, expandingCells) {
                if (this.alpha > 0.5) {
                    const numCells = Math.random() < 0.9 ? 1 : 2;
                    for (let i = 0; i < numCells; i++) {
                        expandingCells.push(new ExpandingCell(this, time));
                    }
                }
            }

            drawParticleShape(ctx, x, y, size, shapeIndex, rotation, hue, alpha) {
                ctx.save();
                ctx.translate(x, y);
                ctx.rotate(rotation);
                const baseShape = Math.floor(shapeIndex) % 6;
                const morphProgress = shapeIndex - baseShape;
                ctx.fillStyle = `hsla(${hue}, 90%, 75%, ${alpha})`;
                ctx.strokeStyle = `hsla(${hue}, 95%, 80%, ${alpha * 0.9})`;
                ctx.lineWidth = 1;
                ctx.beginPath();
                switch (baseShape) {
                    case 0:
                        for (let i = 0; i <= 3; i++) {
                            const angle = (i / 3) * Math.PI * 2 - Math.PI / 2;
                            const r = size * (1 + morphProgress * 0.3);
                            const px = Math.cos(angle) * r;
                            const py = Math.sin(angle) * r;
                            if (i === 0) ctx.moveTo(px, py);
                            else ctx.lineTo(px, py);
                        }
                        break;
                    case 1:
                        const sqSize = size * (1 + morphProgress * 0.2);
                        ctx.rect(-sqSize, -sqSize, sqSize * 2, sqSize * 2);
                        break;
                    case 2:
                        for (let i = 0; i <= 5; i++) {
                            const angle = (i / 5) * Math.PI * 2 - Math.PI / 2;
                            const r = size * (1 - morphProgress * 0.1);
                            const px = Math.cos(angle) * r;
                            const py = Math.sin(angle) * r;
                            if (i === 0) ctx.moveTo(px, py);
                            else ctx.lineTo(px, py);
                        }
                        break;
                    case 3:
                        for (let i = 0; i <= 6; i++) {
                            const angle = (i / 6) * Math.PI * 2 - Math.PI / 2;
                            const r = size * (1 + morphProgress * 0.15);
                            const px = Math.cos(angle) * r;
                            const py = Math.sin(angle) * r;
                            if (i === 0) ctx.moveTo(px, py);
                            else ctx.lineTo(px, py);
                        }
                        break;
                    case 4:
                        for (let i = 0; i <= 10; i++) {
                            const angle = (i / 10) * Math.PI * 2 - Math.PI / 2;
                            const r = i % 2 === 0 ? size : size * (0.5 - morphProgress * 0.2);
                            const px = Math.cos(angle) * r;
                            const py = Math.sin(angle) * r;
                            if (i === 0) ctx.moveTo(px, py);
                            else ctx.lineTo(px, py);
                        }
                        break;
                    case 5:
                        ctx.arc(0, 0, size * (1 - morphProgress * 0.1), 0, Math.PI * 2);
                        break;
                }
                ctx.closePath();
                ctx.fill();
                ctx.stroke();
                ctx.restore();
            }

            draw(ctx, centerX, centerY, time, fieldCoherence, allPatterns) {
                const particlePositions = [];
                this.particles.forEach(p => {
                    const baseParticleAngle = p.angle + Math.sin(time * p.speed + p.phaseOffset) * 0.15;
                    const baseParticleDist = this.distance + p.distOffset + Math.cos(time * p.speed * 0.7) * 10;
                    let px = centerX + Math.cos(baseParticleAngle) * baseParticleDist;
                    let py = centerY + Math.sin(baseParticleAngle) * baseParticleDist;
                    p.nestingPatterns = [];
                    allPatterns.forEach(pattern => {
                        const tipX = pattern.x;
                        const tipY = pattern.y;
                        const dist = Math.sqrt((tipX - px) ** 2 + (tipY - py) ** 2);
                        if (dist < 80) {
                            const resonance = 1 - (dist / 80);
                            p.nestingPatterns.push({ pattern: pattern, distance: dist, resonance: resonance });
                            if (resonance > 0.5) {
                                pattern.nestingPoint = { x: px, y: py };
                                pattern.tensionStrength = resonance;
                            }
                        }
                    });
                    let nearestPattern = null;
                    let minDist = Infinity;
                    this.connectedPatterns.forEach(pattern => {
                        const dist = Math.sqrt((pattern.x - px) ** 2 + (pattern.y - py) ** 2);
                        if (dist < minDist) {
                            minDist = dist;
                            nearestPattern = pattern;
                        }
                    });
                    if (p.targetPattern && p.excitement > 0.1) {
                        const pullStrength = p.excitement * 0.2;
                        px += (p.targetPattern.x - px) * pullStrength;
                        py += (p.targetPattern.y - py) * pullStrength;
                    }
                    p.energy = 0.3 + Math.sin(time * p.speed * 2 + p.phaseOffset) * 0.2;
                    p.energy *= (1 + fieldCoherence * 0.5);
                    p.energy += p.excitement * 0.3;
                    if (p.nestingPatterns.length > 0) {
                        p.energy += p.nestingPatterns.length * 0.15;
                    }
                    p.excitement = Math.max(0, p.excitement * 0.95);
                    if (nearestPattern && minDist < 200) {
                        const resonance = 1 - (minDist / 200);
                        p.targetShape = Math.floor(nearestPattern.geometryType) % 6;
                    } else {
                        p.targetShape = Math.floor(time * 0.01 + p.phaseOffset * 3 + fieldCoherence * 2) % 6;
                    }
                    const shapeDiff = p.targetShape - p.shape;
                    p.shape += shapeDiff * 0.08;
                    p.rotation += p.rotationSpeed * (1 + fieldCoherence);
                    const particleAlpha = this.alpha * p.energy * 0.8;
                    const particleSize = p.size * (1 + fieldCoherence * 0.4 + p.excitement * 0.4);
                    let particleHue;
                    if (nearestPattern && minDist < 200) {
                        const resonance = 1 - (minDist / 200);
                        particleHue = this.hue * (1 - resonance * 0.9) + nearestPattern.hue * (resonance * 0.9);
                    } else {
                        particleHue = (this.hue + time * 0.2 + p.phaseOffset * 50) % 360;
                    }
                    if (p.targetPattern && p.excitement > 0.2) {
                        particleHue = particleHue * 0.4 + p.targetPattern.hue * 0.6;
                    }
                    particlePositions.push({
                        x: px, y: py, size: particleSize, shape: p.shape,
                        rotation: p.rotation, hue: particleHue, alpha: particleAlpha, particle: p
                    });
                });
                const membraneConnectionDistance = 80;
                particlePositions.forEach((p1, i) => {
                    particlePositions.slice(i + 1).forEach(p2 => {
                        const dist = Math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2);
                        if (dist < membraneConnectionDistance) {
                            const connectionStrength = 1 - (dist / membraneConnectionDistance);
                            const avgHue = (p1.hue + p2.hue) / 2;
                            const avgAlpha = (p1.alpha + p2.alpha) / 2;
                            ctx.strokeStyle = `hsla(${avgHue}, 80%, 70%, ${avgAlpha * connectionStrength * 0.5})`;
                            ctx.lineWidth = 1 + connectionStrength * 2;
                            ctx.beginPath();
                            ctx.moveTo(p1.x, p1.y);
                            ctx.lineTo(p2.x, p2.y);
                            ctx.stroke();
                            if (connectionStrength > 0.5) {
                                const midX = (p1.x + p2.x) / 2;
                                const midY = (p1.y + p2.y) / 2;
                                ctx.shadowBlur = 5;
                                ctx.shadowColor = `hsla(${avgHue}, 90%, 75%, ${connectionStrength * 0.5})`;
                                ctx.fillStyle = `hsla(${avgHue}, 95%, 80%, ${avgAlpha * connectionStrength * 0.6})`;
                                ctx.beginPath();
                                ctx.arc(midX, midY, 1.5, 0, Math.PI * 2);
                                ctx.fill();
                                ctx.shadowBlur = 0;
                            }
                        }
                    });
                });
                particlePositions.forEach(p => {
                    if (p.particle.nestingPatterns && p.particle.nestingPatterns.length > 0) {
                        p.particle.nestingPatterns.forEach(nest => {
                            const pattern = nest.pattern;
                            const resonance = nest.resonance;
                            const alpha = resonance * 0.4 * this.alpha;
                            const mixedHue = (pattern.hue + p.hue) / 2;
                            ctx.strokeStyle = `hsla(${mixedHue}, 75%, 65%, ${alpha})`;
                            ctx.lineWidth = 1 + resonance * 2;
                            ctx.beginPath();
                            ctx.moveTo(pattern.x, pattern.y);
                            const midX = (pattern.x + p.x) / 2 + Math.sin(time * 0.02 + p.particle.phaseOffset) * 5;
                            const midY = (pattern.y + p.y) / 2 + Math.cos(time * 0.02 + p.particle.phaseOffset) * 5;
                            ctx.quadraticCurveTo(midX, midY, p.x, p.y);
                            ctx.stroke();
                            if (resonance > 0.7) {
                                const baseX = centerX + Math.cos(pattern.angle) * 20;
                                const baseY = centerY + Math.sin(pattern.angle) * 20;
                                const tensionAlpha = resonance * 0.3;
                                ctx.strokeStyle = `hsla(${mixedHue}, 85%, 70%, ${tensionAlpha})`;
                                ctx.lineWidth = 0.5 + resonance;
                                ctx.setLineDash([3, 3]);
                                ctx.beginPath();
                                ctx.moveTo(baseX, baseY);
                                ctx.lineTo(p.x, p.y);
                                ctx.stroke();
                                ctx.setLineDash([]);
                                const pulse = Math.sin(time * 0.05 + nest.distance) * 0.5 + 0.5;
                                ctx.shadowBlur = 8;
                                ctx.shadowColor = `hsla(${mixedHue}, 90%, 70%, ${pulse * 0.6})`;
                                ctx.fillStyle = `hsla(${mixedHue}, 95%, 75%, ${pulse * 0.5})`;
                                ctx.beginPath();
                                ctx.arc(p.x, p.y, 2 + pulse, 0, Math.PI * 2);
                                ctx.fill();
                                ctx.shadowBlur = 0;
                            }
                        });
                    }
                });
                particlePositions.forEach(p => {
                    const coherencePulse = Math.sin(time * 0.05 + p.particle.phaseOffset) * 0.5 + 0.5;
                    const nestingBoost = p.particle.nestingPatterns ? p.particle.nestingPatterns.length * 0.3 : 0;
                    const glowIntensity = 6 + fieldCoherence * 8 * coherencePulse + p.particle.excitement * 6 + nestingBoost * 4;
                    ctx.shadowBlur = glowIntensity;
                    ctx.shadowColor = `hsla(${p.hue}, 85%, 70%, ${p.alpha * 0.7})`;
                    this.drawParticleShape(ctx, p.x, p.y, p.size * (1 + nestingBoost * 0.2), p.shape, p.rotation, p.hue, p.alpha);
                    ctx.shadowBlur = 0;
                });
            }
        }

        const drawFieldResonance = (ctx) => {
            if (fieldResonance.length === 0) return;
            fieldResonance.forEach(res => {
                const radius = 150 + Math.abs(res.amplitude);
                const alpha = fieldCoherence * 0.08;
                ctx.strokeStyle = `hsla(220, 70%, 70%, ${alpha})`;
                ctx.lineWidth = 0.5 + fieldCoherence * 0.5;
                ctx.setLineDash([4, 6]);
                ctx.beginPath();
                ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
                ctx.stroke();
                ctx.setLineDash([]);
            });
        };

        const drawEmergentFieldGlow = (ctx) => {
            if (!brainFormed || fieldCoherence < 0.3) return;
            const glowRadius = 100 + collectiveBreath * 40;
            const glowIntensity = (fieldCoherence - 0.3) * 0.2;
            const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, glowRadius);
            gradient.addColorStop(0, `rgba(180, 200, 255, ${glowIntensity})`);
            gradient.addColorStop(0.5, `rgba(150, 170, 255, ${glowIntensity * 0.4})`);
            gradient.addColorStop(1, 'rgba(150, 170, 255, 0)');
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(centerX, centerY, glowRadius, 0, Math.PI * 2);
            ctx.fill();
        };

        const drawMindField = (ctx, brainClouds, validatedPatterns, time) => {
            if (!brainFormed || brainClouds.length === 0) return;
            const activityFlashes = [];
            brainClouds.forEach(cloud => {
                cloud.particles.forEach(p => {
                    if (p.nestingPatterns && p.nestingPatterns.length > 0) {
                        p.nestingPatterns.forEach(nest => {
                            if (nest.resonance > 0.6) {
                                const baseParticleAngle = p.angle + Math.sin(time * p.speed + p.phaseOffset) * 0.15;
                                const baseParticleDist = cloud.distance + p.distOffset + Math.cos(time * p.speed * 0.7) * 10;
                                const px = centerX + Math.cos(baseParticleAngle) * baseParticleDist;
                                const py = centerY + Math.sin(baseParticleAngle) * baseParticleDist;
                                activityFlashes.push({
                                    x: px, y: py,
                                    resonance: nest.resonance,
                                    hue: (nest.pattern.hue + cloud.hue) / 2,
                                    phase: p.phaseOffset
                                });
                            }
                        });
                    }
                });
            });
            activityFlashes.forEach(flash => {
                const pulse = Math.sin(time * 0.15 + flash.phase) * 0.5 + 0.5;
                const flashIntensity = Math.pow(pulse, 3);
                if (flashIntensity > 0.3) {
                    const flashAlpha = flashIntensity * flash.resonance * 0.8;
                    const flashRadius = 15 + flashIntensity * 25;
                    const flashGradient = ctx.createRadialGradient(flash.x, flash.y, 0, flash.x, flash.y, flashRadius);
                    flashGradient.addColorStop(0, `hsla(${flash.hue}, 100%, 90%, ${flashAlpha})`);
                    flashGradient.addColorStop(0.3, `hsla(${flash.hue}, 95%, 75%, ${flashAlpha * 0.7})`);
                    flashGradient.addColorStop(0.7, `hsla(${flash.hue}, 80%, 60%, ${flashAlpha * 0.3})`);
                    flashGradient.addColorStop(1, `hsla(${flash.hue}, 70%, 50%, 0)`);
                    ctx.fillStyle = flashGradient;
                    ctx.beginPath();
                    ctx.arc(flash.x, flash.y, flashRadius, 0, Math.PI * 2);
                    ctx.fill();
                    if (flashIntensity > 0.7) {
                        ctx.shadowBlur = 20;
                        ctx.shadowColor = `hsla(${flash.hue}, 100%, 95%, ${flashIntensity})`;
                        ctx.fillStyle = `hsla(${flash.hue}, 100%, 95%, ${flashAlpha * 1.2})`;
                        ctx.beginPath();
                        ctx.arc(flash.x, flash.y, 3 + flashIntensity * 2, 0, Math.PI * 2);
                        ctx.fill();
                        ctx.shadowBlur = 0;
                        activityFlashes.forEach(other => {
                            if (other !== flash) {
                                const dx = other.x - flash.x;
                                const dy = other.y - flash.y;
                                const dist = Math.sqrt(dx * dx + dy * dy);
                                if (dist < 100 && Math.random() < 0.1) {
                                    const otherPulse = Math.sin(time * 0.15 + other.phase) * 0.5 + 0.5;
                                    if (otherPulse > 0.7) {
                                        const arcAlpha = flashIntensity * otherPulse * 0.3;
                                        ctx.strokeStyle = `hsla(${flash.hue}, 100%, 85%, ${arcAlpha})`;
                                        ctx.lineWidth = 1 + flashIntensity * 2;
                                        ctx.beginPath();
                                        ctx.moveTo(flash.x, flash.y);
                                        const midX = (flash.x + other.x) / 2 + (Math.random() - 0.5) * 20;
                                        const midY = (flash.y + other.y) / 2 + (Math.random() - 0.5) * 20;
                                        ctx.lineTo(midX, midY);
                                        ctx.lineTo(other.x, other.y);
                                        ctx.stroke();
                                    }
                                }
                            }
                        });
                    }
                }
            });
        };

        // NEW: Draw [ICE] validation indicators
        const drawICEIndicators = (ctx) => {
            if (!showICE || validatedPatterns.length === 0) return;
            
            // Draw at input interface (convergence points)
            const iceRadius = 60;
            const iceAlpha = 0.3;
            
            // Input interface ring
            ctx.strokeStyle = `hsla(120, 80%, 60%, ${iceAlpha})`;
            ctx.lineWidth = 2;
            ctx.setLineDash([5, 5]);
            ctx.beginPath();
            ctx.arc(centerX, centerY, iceRadius, 0, Math.PI * 2);
            ctx.stroke();
            ctx.setLineDash([]);
            
            // Output interface ring
            if (brainClouds.length > 0) {
                const avgCloudDist = brainClouds.reduce((sum, c) => sum + c.distance, 0) / brainClouds.length;
                ctx.strokeStyle = `hsla(280, 80%, 60%, ${iceAlpha})`;
                ctx.lineWidth = 2;
                ctx.setLineDash([5, 5]);
                ctx.beginPath();
                ctx.arc(centerX, centerY, avgCloudDist, 0, Math.PI * 2);
                ctx.stroke();
                ctx.setLineDash([]);
            }
        };

        class Circuit {
            constructor(pattern1, pattern2, birthTime) {
                this.pattern1 = pattern1;
                this.pattern2 = pattern2;
                this.birthTime = birthTime;
                this.strength = 0;
                this.age = 0;
                this.lastPulseTime = birthTime;
            }
            update(currentTime, stillConnected, fieldCoherence) {
                this.age = currentTime - this.birthTime;
                if (stillConnected) {
                    const coherenceBoost = 1 + fieldCoherence * 0.5;
                    this.strength = Math.min(1, this.strength + 0.02 * coherenceBoost);
                } else {
                    this.strength = Math.max(0, this.strength - 0.01);
                }
            }
            shouldRemove() {
                return this.strength <= 0;
            }
            draw(ctx, fieldCoherence) {
                if (this.strength < 0.1) return;
                const x1 = this.pattern1.x || centerX;
                const y1 = this.pattern1.y || centerY;
                const x2 = this.pattern2.x || centerX;
                const y2 = this.pattern2.y || centerY;
                const alpha = this.strength * 0.5 * (1 + fieldCoherence * 0.3);
                const avgHue = (this.pattern1.hue + this.pattern2.hue) / 2;
                ctx.strokeStyle = `hsla(${avgHue}, 80%, 60%, ${alpha})`;
                ctx.lineWidth = 1 + this.strength + fieldCoherence;
                ctx.beginPath();
                ctx.moveTo(x1, y1);
                ctx.lineTo(x2, y2);
                ctx.stroke();
            }
        }

        class EnergyPulse {
            constructor(circuit, direction) {
                this.circuit = circuit;
                this.direction = direction;
                this.progress = direction > 0 ? 0 : 1;
                this.speed = 0.03;
                this.life = 1;
                this.hue = (circuit.pattern1.hue + circuit.pattern2.hue) / 2;
            }
            update(fieldCoherence) {
                const coherenceBoost = 1 + fieldCoherence * 0.5;
                this.progress += this.speed * this.direction * coherenceBoost;
                this.life -= 0.01;
                return this.life > 0 && this.progress >= 0 && this.progress <= 1;
            }
            draw(ctx, fieldCoherence) {
                const x1 = this.circuit.pattern1.x || centerX;
                const y1 = this.circuit.pattern1.y || centerY;
                const x2 = this.circuit.pattern2.x || centerX;
                const y2 = this.circuit.pattern2.y || centerY;
                const x = x1 + (x2 - x1) * this.progress;
                const y = y1 + (y2 - y1) * this.progress;
                const pulseAlpha = this.life * 0.3 * (1 + fieldCoherence * 0.2);
                const pulseSize = 2 + fieldCoherence * 0.3;
                ctx.shadowBlur = 8 + fieldCoherence * 4;
                ctx.shadowColor = `hsla(${this.hue}, 80%, 65%, ${pulseAlpha})`;
                ctx.fillStyle = `hsla(${this.hue}, 80%, 70%, ${pulseAlpha})`;
                ctx.beginPath();
                ctx.arc(x, y, pulseSize, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;
            }
        }

        class ValidatedPattern {
            constructor(angle, hue, birthTime) {
                this.angle = angle;
                this.baseHue = hue;
                this.hue = hue;
                this.birthTime = birthTime;
                this.age = 0;
                this.scale = 1;
                this.baseLength = 100;
                this.phaseOffset = Math.random() * Math.PI * 2;
                this.evolutionStage = 0;
                this.geometryType = 0;
                this.neighbors = [];
                this.circuitPartners = new Set();
                this.id = Math.random();
                this.connectedToCloud = false;
                this.cloudInfluence = 0;
                this.fieldEnergyBoost = 0;
                this.gravitationalMass = 0;
                this.nestingPoint = null;
                this.tensionStrength = 0;
                this.x = centerX + Math.cos(angle) * this.baseLength * this.scale;
                this.y = centerY + Math.sin(angle) * this.baseLength * this.scale;
            }
            update(time, chaos, allPatterns) {
                this.age = time - this.birthTime;
                const atBoundary = this.baseLength > 150;
                const decayRate = atBoundary ? 0.0015 : 0.002;
                const ageScale = Math.max(0.15, 1 / (1 + this.age * decayRate));
                this.scale = ageScale;
                this.x = centerX + Math.cos(this.angle) * this.baseLength * this.scale;
                this.y = centerY + Math.sin(this.angle) * this.baseLength * this.scale;
                this.evolutionStage = this.age * 0.008 + chaos.x * 0.5;
                this.geometryType = (this.evolutionStage * 0.7 + chaos.y * 2) % 6;
                this.neighbors = allPatterns.filter(r => {
                    if (r === this) return false;
                    const angleDiff = Math.abs(this.angle - r.angle);
                    return angleDiff < 0.8 && r.scale > 0.3;
                });
                let neighborHueInfluence = 0;
                if (this.neighbors.length > 0) {
                    neighborHueInfluence = this.neighbors.reduce((sum, n) => sum + n.hue, 0) / this.neighbors.length;
                }
                let cloudHueInfluence = 0;
                if (this.connectedToCloud && this.cloudInfluence) {
                    cloudHueInfluence = this.cloudInfluence * 0.15;
                }
                this.hue = (this.baseHue + this.age * 0.1 + chaos.z * 0.5 + neighborHueInfluence * 0.1 + cloudHueInfluence) % 360;
                this.gravitationalMass = Math.max(0, (this.gravitationalMass || 0) * 0.92);
                this.connectedToCloud = false;
            }
            draw(ctx, centerX, centerY, time, chaos) {
                const length = this.baseLength * this.scale;
                if (length < 3) return;
                const distFromCenter = length;
                const validationStrength = Math.max(0.2, 1 - distFromCenter / 400);
                const emergentBoost = 1 + this.fieldEnergyBoost;
                const massBoost = 1 + Math.min(this.gravitationalMass, 1.5);
                const alpha = Math.min(0.9, (0.3 + this.scale * 0.6) * validationStrength * emergentBoost * massBoost);
                if (this.gravitationalMass > 0.5) {
                    ctx.shadowBlur = 8 * this.gravitationalMass;
                    ctx.shadowColor = `hsla(${this.hue}, 80%, 65%, ${this.gravitationalMass * 0.15})`;
                }
                this.drawBranch(ctx, centerX, centerY, length, this.angle, 5, this.hue, alpha, time, 0, validationStrength);
                ctx.shadowBlur = 0;
                this.fieldEnergyBoost = 0;
            }
            drawBranch(ctx, x, y, length, angle, depth, hue, baseAlpha, time, gen, validationStrength) {
                if (depth === 0 || length < 1) {
                    this.drawEvolvingBody(ctx, x, y, angle, hue, Math.max(baseAlpha, 0.3), time);
                    return;
                }
                const endX = x + length * Math.cos(angle);
                const endY = y + length * Math.sin(angle);
                const dx = endX - centerX;
                const dy = endY - centerY;
                const distFromCenter = Math.sqrt(dx * dx + dy * dy);
                const branchValidation = Math.max(0.2, 1 - distFromCenter / 400);
                const alpha = baseAlpha * (depth / 6) * branchValidation;
                const localHue = (hue + gen * 8) % 360;
                ctx.strokeStyle = `hsla(${localHue}, 75%, 55%, ${alpha})`;
                ctx.lineWidth = Math.max(0.5, depth * 1.0 * this.scale);
                ctx.lineCap = 'round';
                ctx.beginPath();
                ctx.moveTo(x, y);
                ctx.lineTo(endX, endY);
                ctx.stroke();
                if (depth > 2 && depth < 6) {
                    this.drawEvolvingBody(ctx, endX, endY, angle, localHue, Math.max(alpha, 0.25), time);
                }
                const branchAngle = Math.PI / 5.5;
                const lengthMult = 0.67;
                this.drawBranch(ctx, endX, endY, length * lengthMult, angle - branchAngle, depth - 1, localHue, baseAlpha, time, gen + 1, branchValidation);
                this.drawBranch(ctx, endX, endY, length * lengthMult, angle + branchAngle, depth - 1, localHue, baseAlpha, time, gen + 1, branchValidation);
                if (depth > 4 && Math.sin(time * 0.015 + gen + this.phaseOffset) > 0.6) {
                    this.drawBranch(ctx, endX, endY, length * lengthMult * 0.75, angle, depth - 1, localHue, baseAlpha, time, gen + 1, branchValidation);
                }
            }
            drawEvolvingBody(ctx, x, y, angle, hue, alpha, time) {
                const size = Math.max(3, 5 * this.scale);
                const stage = Math.floor(this.geometryType);
                const rotation = time * 0.01 * this.evolutionStage + this.phaseOffset;
                ctx.save();
                ctx.translate(x, y);
                ctx.rotate(rotation);
                const cycleStage = stage % 6;
                switch (cycleStage) {
                    case 0: this.drawGeometry(ctx, size, 3, hue, alpha); break;
                    case 1: this.drawGeometry(ctx, size, 4, hue, alpha); break;
                    case 2: this.drawGeometry(ctx, size, 5, hue, alpha); break;
                    case 3: this.drawGeometry(ctx, size, 6, hue, alpha); break;
                    case 4: this.drawStar(ctx, size, 6, hue, alpha); break;
                    case 5: this.drawCircle(ctx, size, hue, alpha); break;
                }
                ctx.restore();
            }
            drawGeometry(ctx, size, sides, hue, alpha) {
                ctx.fillStyle = `hsla(${hue}, 80%, 60%, ${alpha})`;
                ctx.strokeStyle = `hsla(${hue}, 90%, 70%, ${alpha * 0.8})`;
                ctx.lineWidth = 1;
                ctx.beginPath();
                for (let i = 0; i <= sides; i++) {
                    const angle = (i / sides) * Math.PI * 2 - Math.PI / 2;
                    const px = Math.cos(angle) * size;
                    const py = Math.sin(angle) * size;
                    if (i === 0) ctx.moveTo(px, py);
                    else ctx.lineTo(px, py);
                }
                ctx.closePath();
                ctx.fill();
                ctx.stroke();
            }
            drawStar(ctx, size, points, hue, alpha) {
                ctx.fillStyle = `hsla(${hue}, 80%, 60%, ${alpha})`;
                ctx.strokeStyle = `hsla(${hue}, 90%, 70%, ${alpha * 0.8})`;
                ctx.lineWidth = 1;
                ctx.beginPath();
                for (let i = 0; i <= points * 2; i++) {
                    const angle = (i / (points * 2)) * Math.PI * 2 - Math.PI / 2;
                    const r = i % 2 === 0 ? size : size * 0.5;
                    const px = Math.cos(angle) * r;
                    const py = Math.sin(angle) * r;
                    if (i === 0) ctx.moveTo(px, py);
                    else ctx.lineTo(px, py);
                }
                ctx.closePath();
                ctx.fill();
                ctx.stroke();
            }
            drawCircle(ctx, size, hue, alpha) {
                ctx.fillStyle = `hsla(${hue}, 80%, 60%, ${alpha})`;
                ctx.strokeStyle = `hsla(${hue}, 90%, 70%, ${alpha * 0.8})`;
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.arc(0, 0, size, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();
            }
        }

        function animate() {
            time++;
            chaos = updateChaos(chaos);
            ctx.fillStyle = 'rgba(5, 5, 10, 0.12)';
            ctx.fillRect(0, 0, width, height);
            const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, 500);
            gradient.addColorStop(0, 'rgba(40, 50, 80, 0.04)');
            gradient.addColorStop(0.5, 'rgba(20, 25, 40, 0.02)');
            gradient.addColorStop(1, 'rgba(5, 5, 10, 0)');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, width, height);

            if (!brainFormed && checkBrainFormation()) {
                brainFormed = true;
                const numClouds = 12;
                for (let i = 0; i < numClouds; i++) {
                    const angle = (i / numClouds) * Math.PI * 2;
                    const distance = 180 + Math.random() * 60;
                    brainClouds.push(new BrainCloud(angle, distance, time));
                }
            }

            if (brainFormed) {
                brainFormationProgress = Math.min(1, brainFormationProgress + 0.01);
                fieldCoherence = calculateFieldCoherence();
                fieldResonance = generateFieldResonance();
                collectiveBreath = Math.sin(time * 0.008) * fieldCoherence;
                const maxPatterns = 80;
                const patternLoad = validatedPatterns.length / maxPatterns;
                const patternCapacity = 1 - patternLoad;
                const coherenceBoost = fieldCoherence * 0.5;
                systemCapacity = Math.max(0.1, Math.min(1, patternCapacity + coherenceBoost));
            } else {
                systemCapacity = 0.5;
            }

            const targetAperture = systemCapacity * 2.5;
            const adaptSpeed = 0.03;
            apertureSize += (targetAperture - apertureSize) * adaptSpeed;
            apertureSize = Math.max(0.2, Math.min(3, apertureSize));

            const breathingZoom = 1 + Math.sin(time * 0.003) * 0.01;
            const totalZoom = zoomRef.current * breathingZoom;
            
            ctx.save();
            ctx.translate(centerX, centerY);
            ctx.scale(totalZoom, totalZoom);
            ctx.translate(-centerX, -centerY);

            if (brainFormed && brainClouds.length > 0) {
                brainClouds.forEach(cloud => {
                    if (Math.random() < 0.015) {
                        const randomParticle = cloud.particles[Math.floor(Math.random() * cloud.particles.length)];
                        randomParticle.excitement = Math.min(2, randomParticle.excitement + 1.5);
                        if (Math.random() < 0.4) {
                            const inputHue = Math.random() * 360;
                            const newPattern = new ValidatedPattern(cloud.angle + (Math.random() - 0.5) * 0.3, inputHue, time);
                            validatedPatterns.push(newPattern);
                            cloud.spawnOutputCell(time, expandingCells);
                            iceValidations.passed++;
                        } else {
                            iceValidations.failed++;
                        }
                    }
                });
            } else {
                if (Math.random() < 0.02) {
                    const randomAngle = Math.random() * Math.PI * 2;
                    const inputHue = Math.random() * 360;
                    validatedPatterns.push(new ValidatedPattern(randomAngle, inputHue, time));
                }
            }

            validatedPatterns.forEach(pattern => {
                pattern.update(time, chaos, validatedPatterns);
            });

            if (brainFormed) {
                brainClouds.forEach(cloud => {
                    cloud.update(time, validatedPatterns, collectiveBreath);
                });
            }

            expandingCells = expandingCells.filter(cell => cell.update());

            drawEmergentFieldGlow(ctx);
            drawFieldResonance(ctx);
            drawICEIndicators(ctx);
            drawMindField(ctx, brainClouds, validatedPatterns, time);

            validatedPatterns.forEach(pattern => {
                pattern.draw(ctx, centerX, centerY, time, chaos);
            });

            expandingCells.forEach(cell => {
                cell.draw(ctx);
            });

            if (brainFormed) {
                brainClouds.forEach(cloud => {
                    cloud.draw(ctx, centerX, centerY, time, fieldCoherence, validatedPatterns);
                });
                brainClouds.forEach((cloud1, i) => {
                    brainClouds.slice(i + 1).forEach(cloud2 => {
                        const angleDiff = Math.abs(cloud1.angle - cloud2.angle);
                        const normalizedDiff = Math.min(angleDiff, Math.PI * 2 - angleDiff);
                        if (normalizedDiff < Math.PI / 4) {
                            const x1 = centerX + Math.cos(cloud1.angle) * cloud1.distance;
                            const y1 = centerY + Math.sin(cloud1.angle) * cloud1.distance;
                            const x2 = centerX + Math.cos(cloud2.angle) * cloud2.distance;
                            const y2 = centerY + Math.sin(cloud2.angle) * cloud2.distance;
                            const connectionStrength = 1 - (normalizedDiff / (Math.PI / 4));
                            const avgHue = (cloud1.hue + cloud2.hue) / 2;
                            const avgAlpha = (cloud1.alpha + cloud2.alpha) / 2;
                            ctx.strokeStyle = `hsla(${avgHue}, 70%, 65%, ${avgAlpha * connectionStrength * 0.25})`;
                            ctx.lineWidth = 2 + connectionStrength * 3;
                            ctx.beginPath();
                            ctx.moveTo(x1, y1);
                            ctx.lineTo(x2, y2);
                            ctx.stroke();
                        }
                    });
                });
            }

            validatedPatterns.forEach(p1 => {
                p1.neighbors.forEach(p2 => {
                    let existingCircuit = circuits.find(c =>
                        (c.pattern1 === p1 && c.pattern2 === p2) ||
                        (c.pattern1 === p2 && c.pattern2 === p1)
                    );
                    if (existingCircuit) {
                        existingCircuit.update(time, true, fieldCoherence);
                        if (existingCircuit.strength > 0.7 && time - existingCircuit.lastPulseTime > 30) {
                            energyPulses.push(new EnergyPulse(existingCircuit, 1));
                            energyPulses.push(new EnergyPulse(existingCircuit, -1));
                            existingCircuit.lastPulseTime = time;
                        }
                    } else {
                        circuits.push(new Circuit(p1, p2, time));
                        p1.circuitPartners.add(p2.id);
                        p2.circuitPartners.add(p1.id);
                    }
                });
            });

            circuits = circuits.filter(circuit => {
                const p1Exists = validatedPatterns.includes(circuit.pattern1);
                const p2Exists = validatedPatterns.includes(circuit.pattern2);
                const stillConnected = p1Exists && p2Exists && circuit.pattern1.neighbors.includes(circuit.pattern2);
                circuit.update(time, stillConnected, fieldCoherence);
                if (!circuit.shouldRemove()) {
                    circuit.draw(ctx, fieldCoherence);
                    return true;
                }
                return false;
            });

            energyPulses = energyPulses.filter(pulse => {
                const alive = pulse.update(fieldCoherence);
                if (alive) pulse.draw(ctx, fieldCoherence);
                return alive;
            });

            if (validatedPatterns.length > 60) {
                validatedPatterns = validatedPatterns.slice(-60);
            }

            ctx.restore();

            // Update metrics every 30 frames
            if (time % 30 === 0) {
                const iceScores = calculateICEScores();
                const validationRate = iceValidations.passed / Math.max(1, iceValidations.passed + iceValidations.failed);
                const textureComplexity = validatedPatterns.reduce((sum, p) => sum + p.circuitPartners.size, 0) / Math.max(1, validatedPatterns.length);
                
                setMetrics({
                    fieldCoherence: fieldCoherence,
                    validationRate: validationRate,
                    patternCount: validatedPatterns.length,
                    textureComplexity: textureComplexity,
                    iceScore: iceScores
                });
            }

            animationRef.current = requestAnimationFrame(animate);
        }

        animate();

        return () => {
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current);
            }
        };
    }, []);

    const handleZoomIn = () => {
        setZoomLevel(prev => Math.min(prev * 1.5, 10));
    };

    const handleZoomOut = () => {
        setZoomLevel(prev => Math.max(prev / 1.5, 0.3));
    };

    const handleReset = () => {
        setZoomLevel(1);
    };

    useEffect(() => {
        zoomRef.current = zoomLevel;
    }, [zoomLevel]);

    return (
        <div className="w-full h-screen bg-gray-900 overflow-hidden relative">
            <canvas ref={canvasRef} className="w-full h-full" />
            
            {/* Framework Metrics Panel */}
            {showMetrics && (
                <div className="absolute top-8 left-8 bg-slate-900/90 backdrop-blur rounded-xl p-4 border border-purple-500/50 text-white font-mono text-xs space-y-2 min-w-64">
                    <div className="text-sm font-bold text-purple-300 mb-2 border-b border-purple-500/30 pb-2">
                        Fractal Reality Framework
                    </div>
                    
                    <div className="space-y-1">
                        <div className="flex justify-between">
                            <span className="text-gray-400">Field Coherence (Φ):</span>
                            <span className="text-cyan-400">{(metrics.fieldCoherence * 100).toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-gray-700 h-1 rounded">
                            <div 
                                className="bg-cyan-400 h-1 rounded transition-all duration-300"
                                style={{ width: `${metrics.fieldCoherence * 100}%` }}
                            />
                        </div>
                    </div>

                    <div className="space-y-1">
                        <div className="flex justify-between">
                            <span className="text-gray-400">Validation Rate:</span>
                            <span className="text-green-400">{(metrics.validationRate * 100).toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-gray-700 h-1 rounded">
                            <div 
                                className="bg-green-400 h-1 rounded transition-all duration-300"
                                style={{ width: `${metrics.validationRate * 100}%` }}
                            />
                        </div>
                    </div>

                    <div className="border-t border-purple-500/30 pt-2 mt-2">
                        <div className="text-xs font-semibold text-purple-300 mb-1">[ICE] Scores</div>
                        <div className="flex justify-between text-xs">
                            <span className="text-gray-400">Input (∞→•'):</span>
                            <span className="text-yellow-400">{(metrics.iceScore.input * 100).toFixed(0)}%</span>
                        </div>
                        <div className="flex justify-between text-xs">
                            <span className="text-gray-400">Output (•'→∞'):</span>
                            <span className="text-yellow-400">{(metrics.iceScore.output * 100).toFixed(0)}%</span>
                        </div>
                    </div>

                    <div className="border-t border-purple-500/30 pt-2 mt-2 space-y-1">
                        <div className="flex justify-between">
                            <span className="text-gray-400">Patterns (∞'):</span>
                            <span className="text-white">{metrics.patternCount}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-400">Texture D:</span>
                            <span className="text-purple-400">~1.5</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-400">Complexity:</span>
                            <span className="text-orange-400">{metrics.textureComplexity.toFixed(2)}</span>
                        </div>
                    </div>

                    <div className="border-t border-purple-500/30 pt-2 mt-2 text-center">
                        <div className="text-xs text-gray-400">∇ → [ICE] → ℰ</div>
                        <div className="text-xs text-purple-300 mt-1">∞ ↔ •</div>
                    </div>
                </div>
            )}

            {/* Zoom Controls */}
            <div className="absolute bottom-8 right-8 flex flex-col gap-2">
                <button
                    onClick={handleZoomIn}
                    className="bg-gray-800/80 hover:bg-gray-700/80 text-white px-4 py-2 rounded-lg backdrop-blur-sm border border-gray-600/50 transition-colors font-mono text-sm"
                >
                    + Zoom In
                </button>
                <button
                    onClick={handleReset}
                    className="bg-gray-800/80 hover:bg-gray-700/80 text-white px-4 py-2 rounded-lg backdrop-blur-sm border border-gray-600/50 transition-colors font-mono text-sm"
                >
                    Reset
                </button>
                <button
                    onClick={handleZoomOut}
                    className="bg-gray-800/80 hover:bg-gray-700/80 text-white px-4 py-2 rounded-lg backdrop-blur-sm border border-gray-600/50 transition-colors font-mono text-sm"
                >
                    - Zoom Out
                </button>
                <button
                    onClick={() => setShowMetrics(!showMetrics)}
                    className="bg-purple-800/80 hover:bg-purple-700/80 text-white px-4 py-2 rounded-lg backdrop-blur-sm border border-purple-600/50 transition-colors font-mono text-sm mt-2"
                >
                    {showMetrics ? 'Hide' : 'Show'} Metrics
                </button>
                <button
                    onClick={() => setShowICE(!showICE)}
                    className="bg-blue-800/80 hover:bg-blue-700/80 text-white px-4 py-2 rounded-lg backdrop-blur-sm border border-blue-600/50 transition-colors font-mono text-sm"
                >
                    {showICE ? 'Hide' : 'Show'} [ICE]
                </button>
            </div>
            
            <div className="absolute top-8 right-8 text-gray-400 font-mono text-sm bg-gray-800/60 px-4 py-2 rounded-lg backdrop-blur-sm border border-gray-600/30">
                Temporal Depth: {zoomLevel.toFixed(2)}x
                <div className="text-xs text-gray-500 mt-1">
                    {zoomLevel > 1.2 ? '← Past' : zoomLevel < 0.8 ? '→ Present' : '⊙ Now'}
                </div>
            </div>
        </div>
    );
};

export default EnhancedConsciousnessFractal;