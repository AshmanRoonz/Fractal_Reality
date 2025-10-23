import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Mic, MicOff, Play, Pause, Volume2, Info, RotateCcw, Zap } from 'lucide-react';

const FractalMusicLearner = () => {
  const canvasRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const micStreamRef = useRef(null);
  const animationRef = useRef(null);
  
  const [isListening, setIsListening] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showInfo, setShowInfo] = useState(true);
  const [memoryCount, setMemoryCount] = useState(0);
  const [resonanceLevel, setResonanceLevel] = useState(0);
  const [synapticStrength, setSynapticStrength] = useState(0);
  
  // Memory storage with learning
  const memoriesRef = useRef([]);
  const timeRef = useRef(0);
  
  // Musical memory with Hebbian learning
  class MusicalMemory {
    constructor(frequency, amplitude, timbre, time) {
      // Position: organized radially by frequency
      const normalizedFreq = Math.log2(frequency / 20) / Math.log2(20000 / 20);
      this.angle = normalizedFreq * Math.PI * 2;
      this.distance = 100 + amplitude * 250;
      
      // Core musical properties
      this.frequency = frequency;
      this.amplitude = amplitude;
      this.timbre = timbre;
      this.birthTime = time;
      this.lastActivation = 0;
      this.activationStrength = 0;
      this.age = 0;
      
      // Hebbian learning structures
      this.connectionWeights = new Map(); // Synaptic weights to other memories
      this.resonanceMemory = new Map();   // Remember which memories resonate well
      this.preferredAngles = [];          // Learned preferred positions
      this.activationHistory = [];        // Temporal pattern of activations
      
      // Visual properties
      this.hue = (normalizedFreq * 360) % 360;
      this.size = 5 + amplitude * 15;
      this.brightness = 0.3;
      this.geometryType = Math.floor(timbre * 5);
      this.phase = 0;
      this.rotation = 0;
      
      // Network properties
      this.neighbors = [];
      this.energyLevel = 0;
    }
    
    // Hebbian learning: strengthen connections when both are active
    updateConnectionWeight(other, learningRate = 0.02) {
      const currentWeight = this.connectionWeights.get(other.id) || 0;
      const distance = Math.sqrt(
        (this.x - other.x) ** 2 + (this.y - other.y) ** 2
      );
      const proximityBonus = Math.max(0, 1 - distance / 200);
      
      // "Neurons that fire together, wire together"
      const coActivation = this.activationStrength * other.activationStrength;
      const newWeight = currentWeight + learningRate * coActivation * proximityBonus;
      
      this.connectionWeights.set(other.id, Math.min(1, newWeight));
      
      // Update resonance memory if weight is strong
      if (newWeight > 0.5) {
        const resonance = this.calculateHarmonicResonance(other);
        const memory = this.resonanceMemory.get(other.id) || { count: 0, avgResonance: 0 };
        memory.count++;
        memory.avgResonance = (memory.avgResonance * (memory.count - 1) + resonance) / memory.count;
        this.resonanceMemory.set(other.id, memory);
        
        // Learn preferred angles based on strong connections
        const angleToOther = Math.atan2(other.y - this.y, other.x - this.x);
        this.preferredAngles.push(angleToOther);
        if (this.preferredAngles.length > 5) {
          this.preferredAngles.shift();
        }
      }
    }
    
    // Synaptic pruning: remove weak connections
    pruneWeakConnections(threshold = 0.1) {
      for (let [id, weight] of this.connectionWeights.entries()) {
        if (weight < threshold) {
          this.connectionWeights.delete(id);
          this.resonanceMemory.delete(id);
        } else {
          // Natural decay of unused connections
          this.connectionWeights.set(id, weight * 0.995);
        }
      }
    }
    
    // Calculate harmonic resonance between frequencies
    calculateHarmonicResonance(other) {
      const freqRatio = Math.max(this.frequency, other.frequency) / 
                       Math.min(this.frequency, other.frequency);
      
      // Check for harmonic relationships (octaves, fifths, thirds)
      const harmonics = [1, 2, 3/2, 4/3, 5/4, 3, 4];
      let maxResonance = 0;
      
      harmonics.forEach(harmonic => {
        const deviation = Math.abs(freqRatio - harmonic);
        if (deviation < 0.05) {
          maxResonance = Math.max(maxResonance, 1 - deviation * 10);
        }
      });
      
      // Amplitude similarity bonus
      const ampSimilarity = 1 - Math.abs(this.amplitude - other.amplitude);
      return maxResonance * 0.7 + ampSimilarity * 0.3;
    }
    
    // Restructure position based on learned preferences
    restructure() {
      if (this.preferredAngles.length < 2 || this.age < 100) return;
      
      // Calculate average preferred angle
      let avgAngle = this.preferredAngles.reduce((sum, a) => sum + a, 0) / this.preferredAngles.length;
      
      // Slowly move toward preferred position
      const angleDiff = avgAngle - this.angle;
      this.angle += angleDiff * 0.003;
    }
    
    activate(strength, currentTime) {
      this.activationStrength = Math.min(1, this.activationStrength + strength);
      this.brightness = 0.3 + this.activationStrength * 0.7;
      this.lastActivation = currentTime;
      this.energyLevel = Math.min(2, this.energyLevel + strength);
      
      // Record activation for temporal learning
      this.activationHistory.push({
        time: currentTime,
        strength: this.activationStrength
      });
      if (this.activationHistory.length > 20) {
        this.activationHistory.shift();
      }
    }
    
    decay(deltaTime) {
      this.activationStrength *= Math.exp(-deltaTime * 2);
      this.brightness = 0.3 + this.activationStrength * 0.7;
      this.energyLevel *= 0.98;
    }
    
    update(currentTime, allMemories) {
      this.age = currentTime - this.birthTime;
      this.phase += 0.02;
      this.rotation += 0.01;
      
      // Find neighbors
      this.neighbors = allMemories.filter(m => {
        if (m === this) return false;
        const dx = this.x - m.x;
        const dy = this.y - m.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        return dist < 150;
      });
      
      // Update connection weights with active neighbors
      this.neighbors.forEach(neighbor => {
        if (this.activationStrength > 0.1 || neighbor.activationStrength > 0.1) {
          this.updateConnectionWeight(neighbor);
        }
      });
      
      // Prune weak connections
      this.pruneWeakConnections();
      
      // Restructure based on learned preferences
      this.restructure();
    }
    
    // Calculate network influence (like gravitational mass)
    getNetworkInfluence() {
      let totalWeight = 0;
      for (let weight of this.connectionWeights.values()) {
        totalWeight += weight;
      }
      return Math.min(1, totalWeight / 5);
    }
  }
  
  // Initialize audio
  const initAudio = useCallback(async () => {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      audioContextRef.current = new AudioContext();
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl: false
        }
      });
      
      micStreamRef.current = stream;
      const source = audioContextRef.current.createMediaStreamSource(stream);
      
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 2048;
      analyserRef.current.smoothingTimeConstant = 0.8;
      
      source.connect(analyserRef.current);
      
      return true;
    } catch (error) {
      console.error('Microphone access denied:', error);
      return false;
    }
  }, []);
  
  // Stop audio
  const stopAudio = useCallback(() => {
    if (micStreamRef.current) {
      micStreamRef.current.getTracks().forEach(track => track.stop());
      micStreamRef.current = null;
    }
  }, []);
  
  // Toggle listening
  const toggleListening = async () => {
    if (!isListening) {
      const success = await initAudio();
      if (success) setIsListening(true);
    } else {
      stopAudio();
      setIsListening(false);
      setIsPlaying(false);
    }
  };
  
  // Analyze audio and learn
  const analyzeAndLearn = useCallback(() => {
    if (!analyserRef.current) return null;
    
    const bufferLength = analyserRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyserRef.current.getByteFrequencyData(dataArray);
    
    const sampleRate = audioContextRef.current.sampleRate;
    const peaks = [];
    
    // Find spectral peaks
    for (let i = 3; i < bufferLength - 3; i++) {
      if (dataArray[i] > 50 && 
          dataArray[i] > dataArray[i-1] && 
          dataArray[i] > dataArray[i+1] &&
          dataArray[i] > dataArray[i-2] &&
          dataArray[i] > dataArray[i+2]) {
        const frequency = (i * sampleRate) / (analyserRef.current.fftSize);
        const amplitude = dataArray[i] / 255;
        
        // Calculate spectral centroid for timbre
        let weightedSum = 0;
        let totalWeight = 0;
        for (let j = Math.max(0, i-5); j < Math.min(bufferLength, i+5); j++) {
          weightedSum += j * dataArray[j];
          totalWeight += dataArray[j];
        }
        const timbre = totalWeight > 0 ? (weightedSum / totalWeight) / bufferLength : 0.5;
        
        peaks.push({ frequency, amplitude, timbre });
      }
    }
    
    return peaks.slice(0, 5); // Limit to top 5 peaks
  }, []);
  
  // Play harmonic based on memory (with overtones)
  const playHarmonic = useCallback((memory, volume = 0.08) => {
    if (!audioContextRef.current || !isPlaying) return;
    
    const ctx = audioContextRef.current;
    const now = ctx.currentTime;
    
    // Play fundamental and harmonics
    const harmonics = [1, 2, 3, 4];
    const waveTypes = ['sine', 'square', 'sawtooth', 'triangle'];
    
    harmonics.forEach((harmonic, i) => {
      setTimeout(() => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        
        osc.frequency.setValueAtTime(memory.frequency * harmonic, now);
        osc.type = waveTypes[memory.geometryType] || 'sine';
        
        const harmVolume = (volume / (i + 1)) * memory.amplitude;
        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(harmVolume, now + 0.05);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);
        
        osc.connect(gain);
        gain.connect(ctx.destination);
        
        osc.start(now);
        osc.stop(now + 0.4);
      }, i * 30);
    });
  }, [isPlaying]);
  
  // Main animation loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let lastTime = Date.now();
    
    const animate = () => {
      const currentTime = Date.now();
      const deltaTime = (currentTime - lastTime) / 1000;
      lastTime = currentTime;
      timeRef.current++;
      
      const width = canvas.width = window.innerWidth;
      const height = canvas.height = window.innerHeight;
      const centerX = width / 2;
      const centerY = height / 2;
      
      // Clear with fade
      ctx.fillStyle = 'rgba(10, 10, 20, 0.12)';
      ctx.fillRect(0, 0, width, height);
      
      // Draw center with pulsing based on system energy
      const totalEnergy = memoriesRef.current.reduce((sum, m) => sum + m.energyLevel, 0);
      const centerPulse = 10 + Math.sin(timeRef.current * 0.05) * 3 + totalEnergy * 2;
      ctx.beginPath();
      ctx.arc(centerX, centerY, centerPulse, 0, Math.PI * 2);
      ctx.fillStyle = `hsla(280, 80%, 60%, ${0.6 + totalEnergy * 0.1})`;
      ctx.fill();
      
      // LEARNING MODE: Analyze and store
      if (isListening && analyserRef.current) {
        const peaks = analyzeAndLearn();
        
        if (peaks && peaks.length > 0) {
          peaks.forEach(peak => {
            // Check for resonance with existing memories
            let bestResonance = 0;
            let resonantMemory = null;
            
            memoriesRef.current.forEach(memory => {
              const resonance = memory.calculateHarmonicResonance({
                frequency: peak.frequency,
                amplitude: peak.amplitude
              });
              if (resonance > bestResonance) {
                bestResonance = resonance;
                resonantMemory = memory;
              }
            });
            
            if (bestResonance > 0.65 && resonantMemory) {
              // Strengthen existing memory
              resonantMemory.activate(0.4, timeRef.current);
            } else if (memoriesRef.current.length < 100) {
              // Create new memory
              const newMemory = new MusicalMemory(
                peak.frequency,
                peak.amplitude,
                peak.timbre,
                timeRef.current
              );
              newMemory.id = Math.random();
              memoriesRef.current.push(newMemory);
            }
          });
        }
      }
      
      // Update all memories
      memoriesRef.current.forEach(memory => {
        memory.decay(deltaTime);
        memory.update(timeRef.current, memoriesRef.current);
        
        // Calculate position
        const wobble = Math.sin(timeRef.current * 0.02 + memory.phase) * 5;
        memory.x = centerX + Math.cos(memory.angle) * memory.distance + wobble;
        memory.y = centerY + Math.sin(memory.angle) * memory.distance + wobble;
      });
      
      // PLAYBACK MODE: Resonance-based activation
      if (isPlaying && memoriesRef.current.length > 0) {
        memoriesRef.current.forEach(memory => {
          // Cycle through memories based on phase
          if (Math.sin(memory.phase + timeRef.current * (memory.frequency / 200)) > 0.95) {
            memory.activate(0.6, timeRef.current);
            playHarmonic(memory);
            
            // Activate strongly connected neighbors
            memory.connectionWeights.forEach((weight, otherId) => {
              if (weight > 0.5) {
                const neighbor = memoriesRef.current.find(m => m.id === otherId);
                if (neighbor) {
                  neighbor.activate(weight * 0.3, timeRef.current);
                }
              }
            });
          }
        });
      }
      
      // Calculate metrics
      let totalResonance = 0;
      let totalSynapticStrength = 0;
      memoriesRef.current.forEach(m => {
        totalResonance += m.activationStrength;
        totalSynapticStrength += m.getNetworkInfluence();
      });
      
      setResonanceLevel(Math.min(1, totalResonance / 10));
      setSynapticStrength(Math.min(1, totalSynapticStrength / memoriesRef.current.length));
      
      // Draw connections first (behind nodes)
      ctx.lineWidth = 1;
      memoriesRef.current.forEach(memory => {
        memory.connectionWeights.forEach((weight, otherId) => {
          if (weight > 0.3) {
            const neighbor = memoriesRef.current.find(m => m.id === otherId);
            if (!neighbor) return;
            
            const alpha = weight * 0.4;
            const resonanceMem = memory.resonanceMemory.get(otherId);
            const hueShift = resonanceMem ? resonanceMem.avgResonance * 60 : 0;
            
            ctx.strokeStyle = `hsla(${(memory.hue + hueShift) % 360}, 70%, 50%, ${alpha})`;
            ctx.lineWidth = 1 + weight * 4;
            ctx.beginPath();
            ctx.moveTo(memory.x, memory.y);
            ctx.lineTo(neighbor.x, neighbor.y);
            ctx.stroke();
            
            // Draw synaptic nodes for strong connections
            if (weight > 0.7) {
              const midX = (memory.x + neighbor.x) / 2;
              const midY = (memory.y + neighbor.y) / 2;
              const pulse = Math.sin(timeRef.current * 0.1) * 0.5 + 0.5;
              ctx.fillStyle = `hsla(${(memory.hue + hueShift) % 360}, 90%, 70%, ${weight * pulse})`;
              ctx.beginPath();
              ctx.arc(midX, midY, 2 + weight * 3, 0, Math.PI * 2);
              ctx.fill();
            }
          }
        });
      });
      
      // Draw memory nodes
      memoriesRef.current.forEach(memory => {
        const networkInfluence = memory.getNetworkInfluence();
        const baseSize = memory.size * (1 + networkInfluence * 0.5);
        
        // Activation glow
        if (memory.activationStrength > 0.3) {
          const glowSize = baseSize * 3 * memory.activationStrength;
          const gradient = ctx.createRadialGradient(
            memory.x, memory.y, 0,
            memory.x, memory.y, glowSize
          );
          gradient.addColorStop(0, `hsla(${memory.hue}, 100%, 70%, ${memory.activationStrength * 0.4})`);
          gradient.addColorStop(1, 'transparent');
          ctx.fillStyle = gradient;
          ctx.beginPath();
          ctx.arc(memory.x, memory.y, glowSize, 0, Math.PI * 2);
          ctx.fill();
        }
        
        // Draw shape
        ctx.save();
        ctx.translate(memory.x, memory.y);
        ctx.rotate(memory.rotation);
        
        const brightness = 30 + memory.brightness * 50;
        ctx.fillStyle = `hsla(${memory.hue}, 80%, ${brightness}%, ${memory.brightness})`;
        ctx.strokeStyle = `hsla(${memory.hue}, 90%, ${brightness + 10}%, ${memory.brightness + 0.2})`;
        ctx.lineWidth = 2;
        
        ctx.beginPath();
        switch(memory.geometryType) {
          case 0: // Circle
            ctx.arc(0, 0, baseSize, 0, Math.PI * 2);
            break;
          case 1: // Triangle
            for (let i = 0; i < 3; i++) {
              const angle = (i / 3) * Math.PI * 2 - Math.PI / 2;
              const x = Math.cos(angle) * baseSize;
              const y = Math.sin(angle) * baseSize;
              if (i === 0) ctx.moveTo(x, y);
              else ctx.lineTo(x, y);
            }
            ctx.closePath();
            break;
          case 2: // Square
            ctx.rect(-baseSize * 0.7, -baseSize * 0.7, baseSize * 1.4, baseSize * 1.4);
            break;
          case 3: // Pentagon
            for (let i = 0; i < 5; i++) {
              const angle = (i / 5) * Math.PI * 2 - Math.PI / 2;
              const x = Math.cos(angle) * baseSize;
              const y = Math.sin(angle) * baseSize;
              if (i === 0) ctx.moveTo(x, y);
              else ctx.lineTo(x, y);
            }
            ctx.closePath();
            break;
          case 4: // Star
            for (let i = 0; i < 10; i++) {
              const angle = (i / 10) * Math.PI * 2 - Math.PI / 2;
              const r = (i % 2 === 0) ? baseSize : baseSize * 0.5;
              const x = Math.cos(angle) * r;
              const y = Math.sin(angle) * r;
              if (i === 0) ctx.moveTo(x, y);
              else ctx.lineTo(x, y);
            }
            ctx.closePath();
            break;
        }
        
        ctx.fill();
        ctx.stroke();
        ctx.restore();
        
        // Show network influence with outer ring
        if (networkInfluence > 0.3) {
          ctx.strokeStyle = `hsla(${memory.hue}, 70%, 60%, ${networkInfluence * 0.3})`;
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.arc(memory.x, memory.y, baseSize + 5, 0, Math.PI * 2);
          ctx.stroke();
        }
      });
      
      setMemoryCount(memoriesRef.current.length);
      animationRef.current = requestAnimationFrame(animate);
    };
    
    animate();
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isListening, isPlaying, analyzeAndLearn, playHarmonic]);
  
  // Cleanup
  useEffect(() => {
    return () => {
      stopAudio();
    };
  }, [stopAudio]);
  
  const resetMemories = () => {
    memoriesRef.current = [];
    setMemoryCount(0);
    setSynapticStrength(0);
  };
  
  return (
    <div className="w-full h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 relative overflow-hidden">
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full"
      />
      
      {/* UI Overlay */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Title */}
        <div className="absolute top-4 left-4 pointer-events-auto">
          <h1 className="text-2xl font-bold text-white mb-1">
            🎵 Fractal Music Learner v2
          </h1>
          <p className="text-sm text-purple-300">
            Hebbian learning • Synaptic pruning • Resonance memory
          </p>
          <p className="text-xs text-gray-400 mt-1">
            <a href="https://github.com/AshmanRoonz/Fractal_Reality" className="underline hover:text-purple-300">
              github.com/AshmanRoonz/Fractal_Reality
            </a>
          </p>
        </div>
        
        {/* Info Panel */}
        {showInfo && (
          <div className="absolute top-4 right-4 bg-black/70 backdrop-blur-sm rounded-lg p-4 max-w-md pointer-events-auto border border-purple-500/50">
            <button
              onClick={() => setShowInfo(false)}
              className="absolute top-2 right-2 text-gray-400 hover:text-white"
            >
              ×
            </button>
            <div className="flex items-start gap-2 mb-3">
              <Info className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-white font-bold mb-1">Hebbian Learning</h3>
                <ul className="text-sm text-gray-300 space-y-1">
                  <li>🧠 <strong>Fire together, wire together:</strong> Co-active memories strengthen bonds</li>
                  <li>🔗 <strong>Synaptic weights:</strong> Connection strength shown by line thickness</li>
                  <li>✂️ <strong>Pruning:</strong> Weak connections decay and vanish</li>
                  <li>📍 <strong>Restructuring:</strong> Memories move toward strong connections</li>
                  <li>🎼 <strong>Harmonic memory:</strong> Remembers which frequencies resonate</li>
                  <li>⚡ <strong>Energy levels:</strong> Network influence affects activation</li>
                  <li>🎹 <strong>Playback:</strong> Activation cascades through learned patterns</li>
                </ul>
              </div>
            </div>
          </div>
        )}
        
        {/* Metrics */}
        <div className="absolute top-4 left-1/2 -translate-x-1/2 pointer-events-auto">
          <div className="bg-black/70 backdrop-blur-sm rounded-lg px-6 py-3 border border-purple-500/50">
            <div className="flex gap-6 text-white text-sm">
              <div>
                <span className="text-gray-400">Memories:</span>{' '}
                <span className="font-bold text-cyan-400">{memoryCount}</span>
              </div>
              <div>
                <span className="text-gray-400">Resonance:</span>{' '}
                <div className="inline-block w-20 h-2 bg-gray-700 rounded-full overflow-hidden align-middle ml-2">
                  <div 
                    className="h-full bg-purple-400 transition-all"
                    style={{ width: `${resonanceLevel * 100}%` }}
                  />
                </div>
              </div>
              <div>
                <Zap className="inline w-4 h-4 text-yellow-400 mr-1" />
                <span className="text-gray-400">Synaptic:</span>{' '}
                <span className="font-bold text-yellow-400">
                  {(synapticStrength * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </div>
        </div>
        
        {/* Controls */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-4 pointer-events-auto">
          <button
            onClick={toggleListening}
            className={`px-6 py-3 rounded-lg font-bold transition-all flex items-center gap-2 ${
              isListening
                ? 'bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-500/50'
                : 'bg-green-500 hover:bg-green-600 text-white'
            }`}
          >
            {isListening ? (
              <>
                <MicOff className="w-5 h-5" />
                Stop Learning
              </>
            ) : (
              <>
                <Mic className="w-5 h-5" />
                Start Learning
              </>
            )}
          </button>
          
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            disabled={memoriesRef.current.length === 0}
            className={`px-6 py-3 rounded-lg font-bold transition-all flex items-center gap-2 ${
              memoriesRef.current.length === 0
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : isPlaying
                ? 'bg-purple-500 hover:bg-purple-600 text-white shadow-lg shadow-purple-500/50'
                : 'bg-blue-500 hover:bg-blue-600 text-white'
            }`}
          >
            {isPlaying ? (
              <>
                <Pause className="w-5 h-5" />
                Pause Playback
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                Play Memory
              </>
            )}
          </button>
          
          <button
            onClick={resetMemories}
            className="px-6 py-3 rounded-lg font-bold bg-slate-700 hover:bg-slate-600 text-white transition-all flex items-center gap-2"
          >
            <RotateCcw className="w-5 h-5" />
            Reset
          </button>
          
          <button
            onClick={() => setShowInfo(!showInfo)}
            className="px-4 py-3 rounded-lg font-bold bg-slate-700 hover:bg-slate-600 text-white transition-all"
          >
            <Info className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default FractalMusicLearner;
