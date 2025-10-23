import React, { useEffect, useRef, useState, useCallback } from 'react';

const EnhancedConsciousnessFractal = () => {
    const canvasRef = useRef(null);
    const animationRef = useRef(null);
    const audioContextRef = useRef(null);
    const oscillatorsRef = useRef(new Map());
    const [zoomLevel, setZoomLevel] = useState(1);
    const [showMetrics, setShowMetrics] = useState(true);
    const [showICE, setShowICE] = useState(true);
    const [selectedShape, setSelectedShape] = useState(0);
    const [fps, setFps] = useState(60);
    const [drawQuality, setDrawQuality] = useState(1.0);
    const [soundEnabled, setSoundEnabled] = useState(false);
    const [growthSpeed, setGrowthSpeed] = useState(1.0);
    const [isDragging, setIsDragging] = useState(false);
    const [dragStart, setDragStart] = useState(null);
    const [energyFlows, setEnergyFlows] = useState([]);
    const [resetKey, setResetKey] = useState(0);
    const zoomRef = useRef(1);
    const fpsHistory = useRef([]);
    const lastFrameTime = useRef(Date.now());
    const drawQualityRef = useRef(1.0);
    const qualityStabilityCounter = useRef(0);
    const growthSpeedRef = useRef(1.0);
    const energyFlowsRef = useRef([]);
    const lastShakeTime = useRef(0);
    const shakeVelocity = useRef({ x: 0, y: 0 });
    const audioAnalyser = useRef(null);
    const audioDataArray = useRef(null);
    const touchesRef = useRef(new Map());
    const showICERef = useRef(true);
    
    const [metrics, setMetrics] = useState({
        fieldCoherence: 0,
        validationRate: 0,
        patternCount: 0,
        textureComplexity: 0,
        iceScore: { input: 0, output: 0 }
    });

    const shapes = [
        { icon: '⭕', name: 'Circle', value: 5 },
        { icon: '▲', name: 'Triangle', value: 0 },
        { icon: '■', name: 'Square', value: 1 },
        { icon: '⬟', name: 'Pentagon', value: 2 },
        { icon: '⬢', name: 'Hexagon', value: 3 },
        { icon: '✦', name: 'Star', value: 4 }
    ];

    // Initialize audio context
    const initAudio = useCallback(() => {
        if (!audioContextRef.current) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            audioContextRef.current = new AudioContext();
            
            // Create analyser for audio visualization
            audioAnalyser.current = audioContextRef.current.createAnalyser();
            audioAnalyser.current.fftSize = 256;
            audioAnalyser.current.connect(audioContextRef.current.destination);
            audioDataArray.current = new Uint8Array(audioAnalyser.current.frequencyBinCount);
        }
        return audioContextRef.current;
    }, []);

    // Play tone based on particle properties
    const playTone = useCallback((frequency, duration, volume = 0.1) => {
        if (!soundEnabled || !audioContextRef.current) return;
        
        const ctx = audioContextRef.current;
        const oscillator = ctx.createOscillator();
        const gainNode = ctx.createGain();
        
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(frequency, ctx.currentTime);
        
        gainNode.gain.setValueAtTime(volume, ctx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
        
        oscillator.connect(gainNode);
        gainNode.connect(audioAnalyser.current || ctx.destination);
        
        oscillator.start(ctx.currentTime);
        oscillator.stop(ctx.currentTime + duration);
        
        return oscillator;
    }, [soundEnabled]);

    // Create harmonic based on resonance
    const playHarmonic = useCallback((baseFreq, resonance, duration = 0.5) => {
        if (!soundEnabled || !audioContextRef.current) return;
        
        const harmonics = [1, 2, 3, 4];
        const volume = 0.05 * resonance;
        
        harmonics.forEach((harmonic, i) => {
            setTimeout(() => {
                playTone(baseFreq * harmonic, duration * (1 - i * 0.2), volume / (i + 1));
            }, i * 50);
        });
    }, [soundEnabled, playTone]);

    // Export organism state
    const exportOrganism = useCallback(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        
        const state = {
            timestamp: Date.now(),
            growthSpeed: growthSpeed,
            zoomLevel: zoomLevel,
            metrics: metrics
        };
        
        const blob = new Blob([JSON.stringify(state, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `consciousness-fractal-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }, [growthSpeed, zoomLevel, metrics]);

    // Import organism state
    const importOrganism = useCallback((event) => {
        const file = event.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const state = JSON.parse(e.target.result);
                setGrowthSpeed(state.growthSpeed || 1.0);
                setZoomLevel(state.zoomLevel || 1);
                growthSpeedRef.current = state.growthSpeed || 1.0;
            } catch (error) {
                console.error('Failed to import organism:', error);
            }
        };
        reader.readAsText(file);
    }, []);

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
            z: Math.random() * 0.2,
            seed: Math.random() * 1000
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
        let iceValidations = { passed: 0, failed: 0 };
        let audioInfluence = 0;

        const updateChaos = (state) => {
            const dt = 0.005 * growthSpeedRef.current;
            const sigma = 10 + Math.sin(state.seed * 0.1) * 2;
            const rho = 28 + Math.cos(state.seed * 0.13) * 5;
            const beta = 8 / 3 + Math.sin(state.seed * 0.07) * 0.5;
            const dx = sigma * (state.y - state.x) * dt;
            const dy = (state.x * (rho - state.z) - state.y) * dt;
            const dz = (state.x * state.y - beta * state.z) * dt;
            return { 
                x: state.x + dx, 
                y: state.y + dy, 
                z: state.z + dz,
                seed: state.seed 
            };
        };

        // Audio analysis for background music influence
        const analyzeAudio = () => {
            if (audioAnalyser.current && audioDataArray.current) {
                audioAnalyser.current.getByteFrequencyData(audioDataArray.current);
                const average = audioDataArray.current.reduce((a, b) => a + b, 0) / audioDataArray.current.length;
                audioInfluence = average / 255;
            }
        };

        const handleCanvasDown = (e) => {
            const rect = canvas.getBoundingClientRect();
            const x = (e.clientX - rect.left) / zoomRef.current;
            const y = (e.clientY - rect.top) / zoomRef.current;
            
            setIsDragging(true);
            setDragStart({ x, y });
        };

        const handleCanvasMove = (e) => {
            if (!isDragging || !dragStart) return;
            
            const rect = canvas.getBoundingClientRect();
            const x = (e.clientX - rect.left) / zoomRef.current;
            const y = (e.clientY - rect.top) / zoomRef.current;
            
            energyFlowsRef.current.push({
                x1: dragStart.x,
                y1: dragStart.y,
                x2: x,
                y2: y,
                strength: 1,
                age: 0
            });
            
            setDragStart({ x, y });
        };

        const handleCanvasUp = (e) => {
            if (!isDragging) {
                // Click to spawn
                const rect = canvas.getBoundingClientRect();
                const clickX = (e.clientX - rect.left) / zoomRef.current;
                const clickY = (e.clientY - rect.top) / zoomRef.current;
                
                const angle = Math.atan2(clickY - centerY, clickX - centerX);
                const dist = Math.sqrt((clickX - centerX) ** 2 + (clickY - centerY) ** 2);
                
                const newPattern = new ValidatedPattern(angle, Math.random() * 360, time);
                newPattern.baseLength = Math.min(dist, 250);
                newPattern.geometryType = selectedShape + Math.random() * 0.5;
                newPattern.userSpawned = true;
                newPattern.spawnEnergy = 2.0;
                validatedPatterns.push(newPattern);
                iceValidations.passed++;
                
                // Play spawn sound
                const frequency = 200 + (newPattern.hue / 360) * 400;
                playTone(frequency, 0.2, 0.15);
                
                if (brainFormed && brainClouds.length > 0) {
                    const nearestCloud = brainClouds.reduce((nearest, cloud) => {
                        const cloudAngleDiff = Math.abs(cloud.angle - angle);
                        const normalizedDiff = Math.min(cloudAngleDiff, Math.PI * 2 - cloudAngleDiff);
                        const cloudDist = Math.abs(cloud.distance - dist);
                        const totalDist = normalizedDiff * 100 + cloudDist;
                        return totalDist < nearest.dist ? { cloud, dist: totalDist } : nearest;
                    }, { cloud: null, dist: Infinity });
                    
                    if (nearestCloud.cloud) {
                        nearestCloud.cloud.particles.forEach(p => {
                            p.excitement = Math.min(2, p.excitement + 0.8);
                            p.targetPattern = newPattern;
                        });
                        nearestCloud.cloud.spawnOutputCell(time, expandingCells);
                    }
                }
            }
            setIsDragging(false);
            setDragStart(null);
        };

        // Touch handling for multi-touch and gestures
        const handleTouchStart = (e) => {
            e.preventDefault();
            const rect = canvas.getBoundingClientRect();
            
            for (let touch of e.touches) {
                const x = (touch.clientX - rect.left) / zoomRef.current;
                const y = (touch.clientY - rect.top) / zoomRef.current;
                touchesRef.current.set(touch.identifier, { x, y, time: Date.now() });
            }
            
            // Multi-touch spawn
            if (e.touches.length >= 2) {
                for (let touch of e.touches) {
                    const x = (touch.clientX - rect.left) / zoomRef.current;
                    const y = (touch.clientY - rect.top) / zoomRef.current;
                    const angle = Math.atan2(y - centerY, x - centerX);
                    const dist = Math.sqrt((x - centerX) ** 2 + (y - centerY) ** 2);
                    
                    const newPattern = new ValidatedPattern(angle, Math.random() * 360, time);
                    newPattern.baseLength = Math.min(dist, 250);
                    newPattern.geometryType = Math.random() * 6;
                    newPattern.userSpawned = true;
                    validatedPatterns.push(newPattern);
                }
            }
        };

        const handleTouchMove = (e) => {
            e.preventDefault();
            const rect = canvas.getBoundingClientRect();
            
            if (e.touches.length === 2) {
                // Pinch to affect field coherence
                const touch1 = e.touches[0];
                const touch2 = e.touches[1];
                const dist = Math.hypot(
                    touch2.clientX - touch1.clientX,
                    touch2.clientY - touch1.clientY
                );
                
                const prevTouch1 = touchesRef.current.get(touch1.identifier);
                const prevTouch2 = touchesRef.current.get(touch2.identifier);
                
                if (prevTouch1 && prevTouch2) {
                    const prevDist = Math.hypot(
                        prevTouch2.x - prevTouch1.x,
                        prevTouch2.y - prevTouch1.y
                    );
                    const scale = dist / prevDist;
                    fieldCoherence = Math.max(0, Math.min(1, fieldCoherence * scale));
                }
            }
            
            for (let touch of e.touches) {
                const x = (touch.clientX - rect.left) / zoomRef.current;
                const y = (touch.clientY - rect.top) / zoomRef.current;
                const prev = touchesRef.current.get(touch.identifier);
                
                if (prev) {
                    energyFlowsRef.current.push({
                        x1: prev.x, y1: prev.y,
                        x2: x, y2: y,
                        strength: 1, age: 0
                    });
                }
                
                touchesRef.current.set(touch.identifier, { x, y, time: Date.now() });
            }
        };

        const handleTouchEnd = (e) => {
            e.preventDefault();
            for (let touch of e.changedTouches) {
                touchesRef.current.delete(touch.identifier);
            }
        };

        // Shake detection
        const handleDeviceMotion = (e) => {
            const acceleration = e.accelerationIncludingGravity;
            if (!acceleration) return;
            
            const magnitude = Math.sqrt(
                acceleration.x ** 2 + 
                acceleration.y ** 2 + 
                acceleration.z ** 2
            );
            
            if (magnitude > 20 && Date.now() - lastShakeTime.current > 500) {
                // Shake detected - introduce chaos
                chaos.x += (Math.random() - 0.5) * 0.5;
                chaos.y += (Math.random() - 0.5) * 0.5;
                chaos.z += (Math.random() - 0.5) * 0.5;
                lastShakeTime.current = Date.now();
                
                // Create explosion of patterns
                for (let i = 0; i < 5; i++) {
                    const angle = Math.random() * Math.PI * 2;
                    const newPattern = new ValidatedPattern(angle, Math.random() * 360, time);
                    validatedPatterns.push(newPattern);
                }
            }
        };

        canvas.addEventListener('mousedown', handleCanvasDown);
        canvas.addEventListener('mousemove', handleCanvasMove);
        canvas.addEventListener('mouseup', handleCanvasUp);
        canvas.addEventListener('touchstart', handleTouchStart, { passive: false });
        canvas.addEventListener('touchmove', handleTouchMove, { passive: false });
        canvas.addEventListener('touchend', handleTouchEnd, { passive: false });
        window.addEventListener('devicemotion', handleDeviceMotion);

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
                this.evolutionStage = Math.random() * 3;
                this.geometryType = Math.random() * 6;
                this.neighbors = [];
                this.circuitPartners = new Set();
                this.id = Math.random();
                this.connectedToCloud = false;
                this.cloudInfluence = 0;
                this.fieldEnergyBoost = 0;
                this.gravitationalMass = 0;
                this.nestingPoint = null;
                this.tensionStrength = 0;
                this.userSpawned = false;
                this.spawnEnergy = 0;
                this.randomOffsetX = (Math.random() - 0.5) * 30;
                this.randomOffsetY = (Math.random() - 0.5) * 30;
                this.probabilityCloud = [];
                this.resonanceMemory = new Map(); // Learning: remember which patterns resonate well
                this.harmonicStrength = 0;
                this.connectionWeights = new Map(); // Synaptic weights to other patterns
                this.activationHistory = [];
                this.preferredAngles = []; // Learned preferred growth directions
                
                // Create probability cloud
                for (let i = 0; i < 8; i++) {
                    this.probabilityCloud.push({
                        angle: Math.random() * Math.PI * 2,
                        dist: Math.random() * 20,
                        phase: Math.random() * Math.PI * 2
                    });
                }
                
                this.x = centerX + Math.cos(angle) * this.baseLength * this.scale + this.randomOffsetX;
                this.y = centerY + Math.sin(angle) * this.baseLength * this.scale + this.randomOffsetY;
            }

            update(time, chaos, allPatterns) {
                this.age = time - this.birthTime;
                const atBoundary = this.baseLength > 150;
                const decayRate = atBoundary ? 0.002 : 0;
                this.scale = Math.max(0, this.scale - decayRate);
                
                if (this.userSpawned && this.spawnEnergy > 0) {
                    this.spawnEnergy *= 0.98;
                    this.scale = Math.min(1.5, this.scale + this.spawnEnergy * 0.05);
                }
                
                const evolutionSpeed = (0.002 + chaos.x * 0.001) * growthSpeedRef.current * (1 + audioInfluence * 0.5);
                this.evolutionStage += evolutionSpeed;
                this.geometryType += Math.sin(this.evolutionStage + chaos.y) * 0.02;
                
                // Learning: Find neighbors and update connection strengths
                this.neighbors = allPatterns.filter(p => {
                    if (p === this || !p.x) return false;
                    const dx = this.x - p.x;
                    const dy = this.y - p.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    return dist < 150 && dist > 10;
                });

                // Update connection weights based on sustained proximity
                this.neighbors.forEach(neighbor => {
                    const currentWeight = this.connectionWeights.get(neighbor.id) || 0;
                    const resonance = 1 - (Math.sqrt((this.x - neighbor.x) ** 2 + (this.y - neighbor.y) ** 2) / 150);
                    
                    // Hebbian learning: "neurons that fire together, wire together"
                    const learningRate = 0.01;
                    const newWeight = currentWeight + learningRate * resonance * this.harmonicStrength;
                    this.connectionWeights.set(neighbor.id, Math.min(1, newWeight));
                    
                    // Remember resonance patterns
                    const memorizedResonance = this.resonanceMemory.get(neighbor.id) || { count: 0, avgResonance: 0 };
                    memorizedResonance.count++;
                    memorizedResonance.avgResonance = (memorizedResonance.avgResonance * (memorizedResonance.count - 1) + resonance) / memorizedResonance.count;
                    this.resonanceMemory.set(neighbor.id, memorizedResonance);
                    
                    // Learn preferred angles based on strong connections
                    if (newWeight > 0.5) {
                        const angleToNeighbor = Math.atan2(neighbor.y - this.y, neighbor.x - this.x);
                        this.preferredAngles.push(angleToNeighbor);
                        if (this.preferredAngles.length > 5) {
                            this.preferredAngles.shift(); // Keep only recent preferences
                        }
                    }
                });
                
                // Prune weak connections (synaptic pruning)
                for (let [id, weight] of this.connectionWeights.entries()) {
                    if (weight < 0.1) {
                        this.connectionWeights.delete(id);
                        this.resonanceMemory.delete(id);
                    }
                }

                // Calculate gravitational mass based on learned connection strengths
                this.gravitationalMass = Array.from(this.connectionWeights.values()).reduce((sum, w) => sum + w, 0) / 10;
                
                // Update activation history for temporal learning
                this.activationHistory.push(this.scale * this.gravitationalMass);
                if (this.activationHistory.length > 20) {
                    this.activationHistory.shift();
                }
                
                // Adjust angle based on learned preferences (restructuring)
                if (this.preferredAngles.length > 2 && this.age > 100) {
                    const avgPreferredAngle = this.preferredAngles.reduce((sum, a) => sum + a, 0) / this.preferredAngles.length;
                    const angleDiff = avgPreferredAngle - this.angle;
                    this.angle += angleDiff * 0.002; // Slowly restructure toward preferred connections
                }
                
                const chaosInfluence = (chaos.x + chaos.y + chaos.z) / 3;
                const cloudHueInfluence = this.connectedToCloud ? this.cloudInfluence : this.baseHue;
                this.hue = (cloudHueInfluence + chaosInfluence * 30 + time * 0.1 + audioInfluence * 60) % 360;
                
                const length = this.baseLength * this.scale;
                const wobble = Math.sin(time * 0.02 + this.phaseOffset) * 5;
                this.x = centerX + Math.cos(this.angle) * length + this.randomOffsetX + wobble;
                this.y = centerY + Math.sin(this.angle) * length + this.randomOffsetY + wobble;
            }

            draw(ctx, centerX, centerY, time, chaos) {
                // Draw probability cloud
                if (drawQualityRef.current > 0.7) {
                    this.probabilityCloud.forEach(p => {
                        const cloudAngle = this.angle + p.angle + Math.sin(time * 0.01 + p.phase) * 0.5;
                        const cloudDist = p.dist * (1 + Math.sin(time * 0.02 + p.phase) * 0.3);
                        const cloudX = this.x + Math.cos(cloudAngle) * cloudDist;
                        const cloudY = this.y + Math.sin(cloudAngle) * cloudDist;
                        
                        ctx.fillStyle = `hsla(${this.hue}, 70%, 60%, 0.1)`;
                        ctx.beginPath();
                        ctx.arc(cloudX, cloudY, 3, 0, Math.PI * 2);
                        ctx.fill();
                    });
                }
                
                // Draw learned connections with variable thickness
                if (drawQualityRef.current > 0.6 && this.connectionWeights.size > 0) {
                    this.neighbors.forEach(neighbor => {
                        const weight = this.connectionWeights.get(neighbor.id);
                        if (weight && weight > 0.3) {
                            const memory = this.resonanceMemory.get(neighbor.id);
                            const alpha = weight * 0.3;
                            const hueShift = memory ? memory.avgResonance * 60 : 0;
                            
                            ctx.strokeStyle = `hsla(${(this.hue + hueShift) % 360}, 70%, 60%, ${alpha})`;
                            ctx.lineWidth = 1 + weight * 3;
                            ctx.beginPath();
                            ctx.moveTo(this.x, this.y);
                            ctx.lineTo(neighbor.x, neighbor.y);
                            ctx.stroke();
                            
                            // Draw synapse nodes at strong connections
                            if (weight > 0.7) {
                                const midX = (this.x + neighbor.x) / 2;
                                const midY = (this.y + neighbor.y) / 2;
                                ctx.fillStyle = `hsla(${(this.hue + hueShift) % 360}, 80%, 70%, ${weight * 0.6})`;
                                ctx.beginPath();
                                ctx.arc(midX, midY, 2 + weight * 2, 0, Math.PI * 2);
                                ctx.fill();
                            }
                        }
                    });
                }
                
                if (drawQualityRef.current < 0.5) {
                    this.drawSimple(ctx, centerX, centerY, time);
                    return;
                }
                
                const length = this.baseLength * this.scale;
                const dx = this.x - centerX;
                const dy = this.y - centerY;
                const distFromCenter = Math.sqrt(dx * dx + dy * dy);
                const validationStrength = Math.max(0.2, 1 - distFromCenter / 400);
                const emergentBoost = 1 + this.fieldEnergyBoost;
                const massBoost = 1 + Math.min(this.gravitationalMass, 1.5);
                const spawnBoost = this.userSpawned ? 1 + this.spawnEnergy : 1;
                const alpha = Math.min(0.9, (0.3 + this.scale * 0.6) * validationStrength * emergentBoost * massBoost * spawnBoost);
                
                if (this.gravitationalMass > 0.5) {
                    ctx.shadowBlur = 8 * this.gravitationalMass * drawQualityRef.current;
                    ctx.shadowColor = `hsla(${this.hue}, 80%, 65%, ${this.gravitationalMass * 0.15})`;
                }
                
                const maxDepth = Math.ceil(5 * drawQualityRef.current);
                this.drawBranch(ctx, centerX, centerY, length, this.angle, maxDepth, this.hue, alpha, time, 0, validationStrength);
                ctx.shadowBlur = 0;
                this.fieldEnergyBoost = 0;
            }

            drawSimple(ctx, centerX, centerY, time) {
                const length = this.baseLength * this.scale;
                const alpha = 0.5 + this.scale * 0.5;
                
                ctx.strokeStyle = `hsla(${this.hue}, 75%, 55%, ${alpha})`;
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(centerX, centerY);
                ctx.lineTo(this.x, this.y);
                ctx.stroke();
                
                const size = 5 * this.scale;
                ctx.fillStyle = `hsla(${this.hue}, 80%, 60%, ${alpha})`;
                ctx.beginPath();
                ctx.arc(this.x, this.y, size, 0, Math.PI * 2);
                ctx.fill();
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
                const localHue = (hue + gen * 8 + time * 0.05) % 360;
                
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
                
                const branchAngleBase = Math.PI / 5.5;
                const branchAngleVariation = Math.sin(gen * 0.5 + this.phaseOffset) * 0.3;
                const branchAngle = branchAngleBase + branchAngleVariation;
                const lengthMult = 0.67 + Math.sin(time * 0.01 + gen) * 0.05;
                
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
                ctx.closePath();
                ctx.fill();
                ctx.stroke();
            }
        }

        class Circuit {
            constructor(pattern1, pattern2, birthTime) {
                this.pattern1 = pattern1;
                this.pattern2 = pattern2;
                this.birthTime = birthTime;
                this.strength = 0;
                this.age = 0;
                this.lastPulseTime = birthTime;
                this.lastSoundTime = 0;
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

            draw(ctx, fieldCoherence, time) {
                if (this.strength < 0.1 || drawQualityRef.current < 0.3) return;
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
                
                // Play sound on strong connection formation
                if (this.strength > 0.8 && time - this.lastSoundTime > 100) {
                    const frequency = 150 + (avgHue / 360) * 200;
                    playTone(frequency, 0.1, 0.03);
                    this.lastSoundTime = time;
                }
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
                this.progress += this.speed * this.direction * coherenceBoost * growthSpeedRef.current;
                this.life -= 0.01;
                return this.life > 0 && this.progress >= 0 && this.progress <= 1;
            }

            draw(ctx, fieldCoherence) {
                if (drawQualityRef.current < 0.4) return;
                const x1 = this.circuit.pattern1.x || centerX;
                const y1 = this.circuit.pattern1.y || centerY;
                const x2 = this.circuit.pattern2.x || centerX;
                const y2 = this.circuit.pattern2.y || centerY;
                const x = x1 + (x2 - x1) * this.progress;
                const y = y1 + (y2 - y1) * this.progress;
                const pulseAlpha = this.life * 0.3 * (1 + fieldCoherence * 0.2);
                const pulseSize = 2 + fieldCoherence * 0.3;
                
                ctx.shadowBlur = (8 + fieldCoherence * 4) * drawQualityRef.current;
                ctx.shadowColor = `hsla(${this.hue}, 80%, 65%, ${pulseAlpha})`;
                ctx.fillStyle = `hsla(${this.hue}, 80%, 70%, ${pulseAlpha})`;
                ctx.beginPath();
                ctx.arc(x, y, pulseSize, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;
            }
        }

        class BrainCloud {
            constructor(angle, distance, birthTime) {
                this.angle = angle + (Math.random() - 0.5) * 0.2;
                this.baseDistance = distance + (Math.random() - 0.5) * 50;
                this.distance = this.baseDistance;
                this.birthTime = birthTime;
                this.phaseOffset = Math.random() * Math.PI * 2;
                this.hue = 200 + Math.random() * 60;
                this.baseHue = this.hue;
                this.alpha = 0;
                this.particles = [];
                this.connectedPatterns = [];
                this.energyLevel = 0;
                this.particleCount = 20 + Math.floor(Math.random() * 20);
                this.lastResonanceTime = 0;
                this.learningRate = 0.05;
                this.patternAffinities = new Map(); // Learn which patterns this cloud connects to best
                
                for (let i = 0; i < this.particleCount; i++) {
                    this.particles.push({
                        angle: angle + (Math.random() - 0.5) * 0.8,
                        distOffset: (Math.random() - 0.5) * 50,
                        size: 2 + Math.random() * 4,
                        phaseOffset: Math.random() * Math.PI * 2,
                        speed: 0.002 + Math.random() * 0.003,
                        energy: Math.random(),
                        targetPattern: null,
                        excitement: 0,
                        shape: Math.random() * 6,
                        targetShape: 0,
                        rotation: Math.random() * Math.PI * 2,
                        rotationSpeed: (Math.random() - 0.5) * 0.02,
                        nestingPatterns: [],
                        bondStrength: new Map() // Remember bond strengths to patterns
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
                const audioWave = audioInfluence * 30;
                this.distance = this.baseDistance + localWave + breathWave + audioWave;
                
                // Learn from connection patterns
                this.connectedPatterns = allPatterns.filter(p => {
                    if (!p || p.x === undefined || p.y === undefined) return false;
                    const angleDiff = Math.abs(this.angle - p.angle);
                    const normalizedDiff = Math.min(angleDiff, Math.PI * 2 - angleDiff);
                    return normalizedDiff < 0.9;
                });
                
                // Update pattern affinities based on resonance
                this.connectedPatterns.forEach(pattern => {
                    const currentAffinity = this.patternAffinities.get(pattern.id) || 0;
                    const resonance = pattern.harmonicStrength || 0;
                    const newAffinity = currentAffinity + this.learningRate * resonance;
                    this.patternAffinities.set(pattern.id, Math.min(1, newAffinity));
                    
                    // Strengthen the relationship
                    const affinityBoost = newAffinity * 0.5;
                    pattern.cloudInfluence = this.hue;
                    pattern.connectedToCloud = true;
                    pattern.fieldEnergyBoost = this.energyLevel * (1 + affinityBoost);
                    pattern.harmonicStrength = Math.min(1, pattern.harmonicStrength + resonance * 0.1);
                });
                
                // Restructure: Move toward patterns with highest affinity
                if (this.patternAffinities.size > 0 && age > 200) {
                    let maxAffinity = 0;
                    let targetPattern = null;
                    
                    this.connectedPatterns.forEach(pattern => {
                        const affinity = this.patternAffinities.get(pattern.id) || 0;
                        if (affinity > maxAffinity) {
                            maxAffinity = affinity;
                            targetPattern = pattern;
                        }
                    });
                    
                    if (targetPattern && maxAffinity > 0.5) {
                        const targetAngle = Math.atan2(targetPattern.y - centerY, targetPattern.x - centerX);
                        const angleDiff = targetAngle - this.angle;
                        this.angle += angleDiff * 0.005 * maxAffinity; // Restructure toward strong connections
                    }
                }
                
                this.energyLevel = this.connectedPatterns.length * 0.1;
            }

            spawnOutputCell(time, expandingCells) {
                if (this.alpha > 0.5 && drawQualityRef.current > 0.4) {
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
                const particlesToDraw = Math.ceil(this.particles.length * drawQualityRef.current);
                const particlePositions = [];
                
                for (let i = 0; i < particlesToDraw; i++) {
                    const p = this.particles[i];
                    const baseParticleAngle = p.angle + Math.sin(time * p.speed + p.phaseOffset) * 0.15;
                    const baseParticleDist = this.distance + p.distOffset + Math.cos(time * p.speed * 0.7) * 10;
                    let px = centerX + Math.cos(baseParticleAngle) * baseParticleDist;
                    let py = centerY + Math.sin(baseParticleAngle) * baseParticleDist;
                    
                    if (drawQualityRef.current > 0.5) {
                        p.nestingPatterns = [];
                        allPatterns.forEach(pattern => {
                            const tipX = pattern.x;
                            const tipY = pattern.y;
                            const dist = Math.sqrt((tipX - px) ** 2 + (tipY - py) ** 2);
                            if (dist < 80) {
                                const resonance = 1 - (dist / 80);
                                p.nestingPatterns.push({ pattern: pattern, distance: dist, resonance: resonance });
                                
                                // Learn bond strength between particle and pattern
                                const currentBond = p.bondStrength.get(pattern.id) || 0;
                                const bondGrowth = resonance * 0.02;
                                p.bondStrength.set(pattern.id, Math.min(1, currentBond + bondGrowth));
                                
                                if (resonance > 0.5) {
                                    pattern.nestingPoint = { x: px, y: py };
                                    pattern.tensionStrength = resonance;
                                    
                                    // Increase harmonic strength based on nesting
                                    pattern.harmonicStrength = Math.min(1, (pattern.harmonicStrength || 0) + resonance * 0.05);
                                }
                                
                                // Play harmonic on high resonance
                                if (resonance > 0.7 && time - this.lastResonanceTime > 200) {
                                    const baseFreq = 200 + (pattern.hue / 360) * 300;
                                    playHarmonic(baseFreq, resonance, 0.3);
                                    this.lastResonanceTime = time;
                                }
                            }
                        });
                        
                        // Prune weak bonds (synaptic pruning at particle level)
                        for (let [id, strength] of p.bondStrength.entries()) {
                            if (strength < 0.1) {
                                p.bondStrength.delete(id);
                            } else {
                                p.bondStrength.set(id, strength * 0.99); // Decay over time
                            }
                        }
                    }
                    
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
                    if (p.nestingPatterns && p.nestingPatterns.length > 0) {
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
                }
                
                if (drawQualityRef.current > 0.6) {
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
                                
                                if (connectionStrength > 0.5 && drawQualityRef.current > 0.8) {
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
                }
                
                if (drawQualityRef.current > 0.7) {
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
                }
                
                particlePositions.forEach(p => {
                    const coherencePulse = Math.sin(time * 0.05 + p.particle.phaseOffset) * 0.5 + 0.5;
                    const nestingBoost = p.particle.nestingPatterns ? p.particle.nestingPatterns.length * 0.3 : 0;
                    const glowIntensity = (6 + fieldCoherence * 8 * coherencePulse + p.particle.excitement * 6 + nestingBoost * 4) * drawQualityRef.current;
                    
                    ctx.shadowBlur = glowIntensity;
                    ctx.shadowColor = `hsla(${p.hue}, 85%, 70%, ${p.alpha * 0.7})`;
                    this.drawParticleShape(ctx, p.x, p.y, p.size * (1 + nestingBoost * 0.2), p.shape, p.rotation, p.hue, p.alpha);
                    ctx.shadowBlur = 0;
                });
            }
        }

        class ExpandingCell {
            constructor(sourceCloud, birthTime) {
                this.sourceCloud = sourceCloud;
                this.birthTime = birthTime;
                this.age = 0;
                this.angle = sourceCloud.angle + (Math.random() - 0.5) * 0.3;
                this.distance = sourceCloud.distance;
                this.hue = sourceCloud.hue + (Math.random() - 0.5) * 20;
                this.expansionSpeed = (0.6 + Math.random() * 0.4) * growthSpeedRef.current;
                this.maxRadius = 12 + Math.random() * 18;
                this.currentRadius = 0;
                this.lifecycle = 0;
                this.lifecycleSpeed = (0.006 + Math.random() * 0.003) * growthSpeedRef.current;
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
                if (this.currentRadius < 0.5 || drawQualityRef.current < 0.5) return;
                
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
                
                const branchesToDraw = Math.ceil((4 + Math.floor(Math.random() * 3)) * drawQualityRef.current);
                for (let i = 0; i < branchesToDraw; i++) {
                    const angle = (i / branchesToDraw) * Math.PI * 2;
                    const branchLength = this.currentRadius * 0.5;
                    const maxDepth = Math.ceil(this.fractalComplexity * drawQualityRef.current);
                    this.drawFractalBranch(ctx, 0, 0, branchLength, angle, maxDepth, this.hue, alpha);
                }
                
                const glowSize = this.currentRadius * 0.15;
                ctx.shadowBlur = 8 * drawQualityRef.current;
                ctx.shadowColor = `hsla(${this.hue}, 90%, 70%, ${alpha * 0.6})`;
                ctx.fillStyle = `hsla(${this.hue}, 85%, 75%, ${alpha * 0.7})`;
                ctx.beginPath();
                ctx.arc(0, 0, glowSize, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;
                ctx.restore();
            }
        }

        const drawICEIndicators = (ctx) => {
            if (!showICERef.current) return;
            
            const indicatorY = 100;
            const indicatorSpacing = 120;
            const baseX = 80;
            
            ctx.font = '12px monospace';
            ctx.textAlign = 'left';
            
            const iceScores = calculateICEScores();
            
            [[iceScores.input, 'Input'], [iceScores.output, 'Output']].forEach(([score, label], idx) => {
                const x = baseX + idx * indicatorSpacing;
                const barHeight = 60;
                const barWidth = 40;
                
                ctx.fillStyle = 'rgba(30, 30, 40, 0.8)';
                ctx.fillRect(x - 5, indicatorY - 5, barWidth + 10, barHeight + 35);
                
                ctx.fillStyle = `hsl(${score * 120}, 70%, 50%)`;
                ctx.fillRect(x, indicatorY + barHeight - score * barHeight, barWidth, score * barHeight);
                
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
                ctx.strokeRect(x, indicatorY, barWidth, barHeight);
                
                ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
                ctx.fillText(`[ICE] ${label}`, x, indicatorY + barHeight + 15);
                ctx.fillText(`${(score * 100).toFixed(0)}%`, x + 5, indicatorY + barHeight + 28);
            });
        };

        const calculateICEScores = () => {
            let inputScore = 0, outputScore = 0, count = 0;
            
            validatedPatterns.forEach(p => {
                count++;
                if (p.scale > 0.3) {
                    const inputInterface = p.age > 10 ? 0.9 : p.scale;
                    const inputCoherence = p.neighbors.length > 0 ? 0.85 : 0.5;
                    const inputEvidence = p.connectedToCloud ? 0.9 : 0.6;
                    inputScore += (inputInterface + inputCoherence + inputEvidence) / 3;
                    
                    const outputInterface = p.age > 20 ? 0.9 : p.scale;
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

        const drawFieldResonance = (ctx) => {
            if (fieldResonance.length === 0 || drawQualityRef.current < 0.5) return;
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
            if (!brainFormed || fieldCoherence < 0.3 || drawQualityRef.current < 0.6) return;
            
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
            if (!brainFormed || brainClouds.length === 0 || drawQualityRef.current < 0.5) return;
            
            const activityFlashes = [];
            brainClouds.forEach(cloud => {
                cloud.particles.slice(0, Math.ceil(cloud.particles.length * drawQualityRef.current)).forEach(p => {
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
                    flashGradient.addColorStop(0, `hsla(${flash.hue}, 90%, 75%, ${flashAlpha})`);
                    flashGradient.addColorStop(1, `hsla(${flash.hue}, 90%, 75%, 0)`);
                    ctx.fillStyle = flashGradient;
                    ctx.beginPath();
                    ctx.arc(flash.x, flash.y, flashRadius, 0, Math.PI * 2);
                    ctx.fill();
                }
            });
        };

        const drawEnergyFlows = (ctx) => {
            energyFlowsRef.current = energyFlowsRef.current.filter(flow => {
                flow.age++;
                flow.strength *= 0.95;
                
                if (flow.strength < 0.1 || flow.age > 100) return false;
                
                const alpha = flow.strength * 0.4;
                const gradient = ctx.createLinearGradient(flow.x1, flow.y1, flow.x2, flow.y2);
                gradient.addColorStop(0, `rgba(100, 200, 255, ${alpha})`);
                gradient.addColorStop(1, `rgba(200, 100, 255, ${alpha * 0.5})`);
                
                ctx.strokeStyle = gradient;
                ctx.lineWidth = 3 * flow.strength;
                ctx.lineCap = 'round';
                ctx.beginPath();
                ctx.moveTo(flow.x1, flow.y1);
                ctx.lineTo(flow.x2, flow.y2);
                ctx.stroke();
                
                // Apply force to nearby patterns
                validatedPatterns.forEach(pattern => {
                    const dx = pattern.x - flow.x2;
                    const dy = pattern.y - flow.y2;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 100) {
                        const force = (1 - dist / 100) * flow.strength * 0.1;
                        const flowAngle = Math.atan2(flow.y2 - flow.y1, flow.x2 - flow.x1);
                        pattern.angle += Math.sin(flowAngle - pattern.angle) * force;
                    }
                });
                
                return true;
            });
        };

        const updateFPS = () => {
            const now = Date.now();
            const delta = now - lastFrameTime.current;
            const currentFPS = 1000 / delta;
            lastFrameTime.current = now;
            
            fpsHistory.current.push(currentFPS);
            if (fpsHistory.current.length > 60) {
                fpsHistory.current.shift();
            }
            
            const avgFPS = fpsHistory.current.reduce((a, b) => a + b, 0) / fpsHistory.current.length;
            setFps(Math.round(avgFPS));
            
            const targetFPS = 30;
            const fpsMargin = 5;
            
            if (avgFPS < targetFPS - fpsMargin) {
                qualityStabilityCounter.current--;
                if (qualityStabilityCounter.current < -10) {
                    drawQualityRef.current = Math.max(0.2, drawQualityRef.current - 0.1);
                    qualityStabilityCounter.current = 0;
                }
            } else if (avgFPS > targetFPS + 10) {
                qualityStabilityCounter.current++;
                if (qualityStabilityCounter.current > 30) {
                    drawQualityRef.current = Math.min(1.0, drawQualityRef.current + 0.05);
                    qualityStabilityCounter.current = 0;
                }
            } else {
                qualityStabilityCounter.current = Math.max(-5, Math.min(5, qualityStabilityCounter.current));
            }
            
            setDrawQuality(drawQualityRef.current);
        };

        const animate = () => {
            time++;
            chaos = updateChaos(chaos);
            collectiveBreath = Math.sin(time * 0.005) * 0.5 + 0.5;
            
            updateFPS();
            analyzeAudio();
            
            ctx.fillStyle = 'rgba(10, 10, 15, 0.15)';
            ctx.fillRect(0, 0, width, height);
            
            if (validatedPatterns.length > 15 && !brainFormed) {
                brainFormationProgress += 0.01;
                if (brainFormationProgress >= 1) {
                    brainFormed = true;
                    const numClouds = 6 + Math.floor(Math.random() * 4);
                    for (let i = 0; i < numClouds; i++) {
                        const angle = (i / numClouds) * Math.PI * 2 + (Math.random() - 0.5) * 0.3;
                        const distance = 200 + Math.random() * 100;
                        brainClouds.push(new BrainCloud(angle, distance, time));
                    }
                }
            }
            
            if (brainFormed && brainClouds.length > 0) {
                const avgEnergyLevel = brainClouds.reduce((sum, cloud) => sum + cloud.energyLevel, 0) / brainClouds.length;
                fieldCoherence = Math.min(0.9, avgEnergyLevel);
                fieldResonance = generateFieldResonance();
            }
            
            let patternCapacity, coherenceBoost;
            if (brainFormed && brainClouds.length > 0) {
                patternCapacity = Math.max(0, Math.min(1, (60 - validatedPatterns.length) / 60));
                coherenceBoost = fieldCoherence * 0.5;
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
                    if (Math.random() < 0.015 * drawQualityRef.current * growthSpeedRef.current) {
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
                if (Math.random() < 0.02 * drawQualityRef.current * growthSpeedRef.current) {
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
            drawEnergyFlows(ctx);
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
                
                if (drawQualityRef.current > 0.5) {
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
            }
            
            if (drawQualityRef.current > 0.4) {
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
            }
            
            circuits = circuits.filter(circuit => {
                const p1Exists = validatedPatterns.includes(circuit.pattern1);
                const p2Exists = validatedPatterns.includes(circuit.pattern2);
                const stillConnected = p1Exists && p2Exists && circuit.pattern1.neighbors.includes(circuit.pattern2);
                circuit.update(time, stillConnected, fieldCoherence);
                if (!circuit.shouldRemove()) {
                    circuit.draw(ctx, fieldCoherence, time);
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
        };

        animate();

        return () => {
            canvas.removeEventListener('mousedown', handleCanvasDown);
            canvas.removeEventListener('mousemove', handleCanvasMove);
            canvas.removeEventListener('mouseup', handleCanvasUp);
            canvas.removeEventListener('touchstart', handleTouchStart);
            canvas.removeEventListener('touchmove', handleTouchMove);
            canvas.removeEventListener('touchend', handleTouchEnd);
            window.removeEventListener('devicemotion', handleDeviceMotion);
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current);
            }
        };
    }, [playTone, playHarmonic, resetKey]);

    const handleZoomIn = () => {
        setZoomLevel(prev => Math.min(prev * 1.5, 10));
    };

    const handleZoomOut = () => {
        setZoomLevel(prev => Math.max(prev / 1.5, 0.3));
    };

    const handleReset = () => {
        // Reset all state
        setZoomLevel(1);
        setGrowthSpeed(1.0);
        setDrawQuality(1.0);
        setFps(60);
        setIsDragging(false);
        setDragStart(null);
        
        // Reset refs
        zoomRef.current = 1;
        growthSpeedRef.current = 1.0;
        drawQualityRef.current = 1.0;
        qualityStabilityCounter.current = 0;
        fpsHistory.current = [];
        lastFrameTime.current = Date.now();
        energyFlowsRef.current = [];
        touchesRef.current.clear();
        
        // Trigger re-render by changing key
        setResetKey(prev => prev + 1);
    };

    const toggleSound = () => {
        if (!soundEnabled) {
            const ctx = initAudio();
            // Resume audio context (required by browsers)
            if (ctx.state === 'suspended') {
                ctx.resume();
            }
        }
        setSoundEnabled(!soundEnabled);
    };

    const toggleICE = () => {
        setShowICE(prev => {
            showICERef.current = !prev;
            return !prev;
        });
    };

    useEffect(() => {
        zoomRef.current = zoomLevel;
    }, [zoomLevel]);

    useEffect(() => {
        growthSpeedRef.current = growthSpeed;
    }, [growthSpeed]);

    useEffect(() => {
        showICERef.current = showICE;
    }, [showICE]);

    const getQualityColor = () => {
        if (drawQuality > 0.8) return 'text-green-400';
        if (drawQuality > 0.5) return 'text-yellow-400';
        return 'text-red-400';
    };

    const getQualityLabel = () => {
        if (drawQuality > 0.8) return 'Ultra';
        if (drawQuality > 0.6) return 'High';
        if (drawQuality > 0.4) return 'Medium';
        if (drawQuality > 0.2) return 'Low';
        return 'Minimal';
    };

    return (
        <div className="w-full h-screen bg-gray-900 overflow-hidden relative">
            <canvas ref={canvasRef} className="w-full h-full cursor-crosshair" />
            
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
                            <div className="bg-cyan-400 h-1 rounded transition-all" style={{ width: `${metrics.fieldCoherence * 100}%` }}></div>
                        </div>
                        
                        <div className="flex justify-between">
                            <span className="text-gray-400">Validation Rate:</span>
                            <span className="text-green-400">{(metrics.validationRate * 100).toFixed(1)}%</span>
                        </div>
                        
                        <div className="flex justify-between">
                            <span className="text-gray-400">Pattern Count (∞'):</span>
                            <span className="text-yellow-400">{metrics.patternCount}</span>
                        </div>
                        
                        <div className="flex justify-between">
                            <span className="text-gray-400">Texture D:</span>
                            <span className="text-orange-400">{(1 + metrics.textureComplexity * 0.5).toFixed(2)}</span>
                        </div>
                        
                        <div className="border-t border-gray-700 pt-2 mt-2">
                            <div className="flex justify-between">
                                <span className="text-gray-400">FPS:</span>
                                <span className={fps >= 30 ? 'text-green-400' : fps >= 20 ? 'text-yellow-400' : 'text-red-400'}>
                                    {fps}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-400">Draw Quality:</span>
                                <span className={getQualityColor()}>
                                    {getQualityLabel()} ({(drawQuality * 100).toFixed(0)}%)
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            )}
            
            <div className="absolute top-8 right-8 bg-slate-900/90 backdrop-blur rounded-xl p-4 border border-purple-500/50 text-white space-y-3">
                <div className="text-sm font-bold text-purple-300 mb-3">Feed the Organism</div>
                <div className="grid grid-cols-3 gap-2">
                    {shapes.map((shape, idx) => {
                        return (
                            <button
                                key={idx}
                                onClick={() => setSelectedShape(shape.value)}
                                className={`p-3 rounded-lg transition-all text-2xl ${
                                    selectedShape === shape.value
                                        ? 'bg-purple-600 ring-2 ring-purple-400 scale-110'
                                        : 'bg-gray-700 hover:bg-gray-600'
                                }`}
                                title={shape.name}
                            >
                                {shape.icon}
                            </button>
                        );
                    })}
                </div>
                <div className="text-xs text-gray-400 text-center pt-2 border-t border-gray-700">
                    Click/Drag to interact
                </div>
                
                <div className="pt-3 border-t border-gray-700 space-y-2">
                    <div>
                        <label className="text-xs text-gray-400 block mb-1">Growth Speed: {growthSpeed.toFixed(1)}x</label>
                        <input 
                            type="range" 
                            min="0.1" 
                            max="3" 
                            step="0.1" 
                            value={growthSpeed}
                            onChange={(e) => setGrowthSpeed(parseFloat(e.target.value))}
                            className="w-full"
                        />
                    </div>
                </div>
                
                <div className="flex gap-2 pt-3 border-t border-gray-700">
                    <button
                        onClick={exportOrganism}
                        className="flex-1 px-3 py-2 bg-blue-600/80 hover:bg-blue-500 rounded-lg transition flex items-center justify-center gap-2 text-xl"
                        title="Export organism state"
                    >
                        💾
                    </button>
                    <label className="flex-1 px-3 py-2 bg-green-600/80 hover:bg-green-500 rounded-lg transition flex items-center justify-center gap-2 cursor-pointer text-xl">
                        📤
                        <input 
                            type="file" 
                            accept=".json" 
                            onChange={importOrganism}
                            className="hidden"
                        />
                    </label>
                    <button
                        onClick={toggleSound}
                        className={`flex-1 px-3 py-2 rounded-lg transition flex items-center justify-center gap-2 text-xl ${
                            soundEnabled ? 'bg-purple-600/80 hover:bg-purple-500' : 'bg-gray-600/80 hover:bg-gray-500'
                        }`}
                        title={soundEnabled ? 'Mute' : 'Enable Sound'}
                    >
                        {soundEnabled ? '🔊' : '🔇'}
                    </button>
                </div>
            </div>
            
            <div className="absolute bottom-8 left-8 flex gap-2 flex-wrap max-w-md">
                <button onClick={handleZoomIn} className="px-4 py-2 bg-purple-600/80 hover:bg-purple-500 text-white rounded-lg backdrop-blur transition">
                    Zoom In
                </button>
                <button onClick={handleZoomOut} className="px-4 py-2 bg-purple-600/80 hover:bg-purple-500 text-white rounded-lg backdrop-blur transition">
                    Zoom Out
                </button>
                <button onClick={handleReset} className="px-4 py-2 bg-purple-600/80 hover:bg-purple-500 text-white rounded-lg backdrop-blur transition">
                    Reset
                </button>
                <button onClick={() => setShowMetrics(!showMetrics)} className="px-4 py-2 bg-purple-600/80 hover:bg-purple-500 text-white rounded-lg backdrop-blur transition">
                    {showMetrics ? 'Hide' : 'Show'} Metrics
                </button>
                <button onClick={toggleICE} className="px-4 py-2 bg-purple-600/80 hover:bg-purple-500 text-white rounded-lg backdrop-blur transition">
                    {showICE ? 'Hide' : 'Show'} [ICE]
                </button>
            </div>
            
            <div className="absolute bottom-8 right-8 text-gray-400 font-mono text-sm bg-gray-800/60 px-4 py-2 rounded-lg backdrop-blur-sm border border-gray-600/30">
                Temporal Depth: {zoomLevel.toFixed(2)}x
                <div className="text-xs text-gray-500 mt-1">
                    {zoomLevel > 1.2 ? '← Past' : zoomLevel < 0.8 ? '→ Present' : '⊙ Now'}
                </div>
            </div>
        </div>
    );
};

export default EnhancedConsciousnessFractal;
