import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Mic, MicOff, Play, Pause, Volume2, Info, RotateCcw } from 'lucide-react';

const FractalMusicLearner = () => {
  const canvasRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const micStreamRef = useRef(null);
  const oscillatorRef = useRef(null);
  const animationRef = useRef(null);
  
  const [isListening, setIsListening] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showInfo, setShowInfo] = useState(true);
  const [memoryCount, setMemoryCount] = useState(0);
  const [resonanceLevel, setResonanceLevel] = useState(0);
  
  // Memory storage - organized around center
  const memoriesRef = useRef([]);
  const activeMemoriesRef = useRef(new Set());
  
  // Musical element classes
  class MusicalMemory {
    constructor(frequency, amplitude, timbre, time) {
      // Position: organized radially by frequency
      const normalizedFreq = Math.log2(frequency / 20) / Math.log2(20000 / 20);
      this.angle = normalizedFreq * Math.PI * 2;
      this.distance = 100 + amplitude * 250;
      
      // Visual properties based on musical elements
      this.frequency = frequency;
      this.amplitude = amplitude;
      this.timbre = timbre; // 0-1 spectral centroid
      this.birthTime = time;
      this.lastActivation = 0;
      this.activationStrength = 0;
      this.resonanceScore = 0;
      
      // Visual representation
      this.hue = (normalizedFreq * 360) % 360;
      this.size = 5 + amplitude * 15;
      this.brightness = 0.3;
      this.connections = [];
      
      // Geometry type based on timbre
      this.geometryType = Math.floor(timbre * 5);
      this.phase = 0;
    }
    
    activate(strength, currentTime) {
      this.activationStrength = Math.min(1, this.activationStrength + strength);
      this.brightness = 0.3 + this.activationStrength * 0.7;
      this.lastActivation = currentTime;
    }
    
    decay(deltaTime) {
      this.activationStrength *= Math.exp(-deltaTime * 2);
      this.brightness = 0.3 + this.activationStrength * 0.7;
    }
    
    calculateResonance(incomingFreq, incomingAmp) {
      const freqRatio = Math.max(this.frequency, incomingFreq) / 
                       Math.min(this.frequency, incomingFreq);
      const isHarmonic = Math.abs(freqRatio - Math.round(freqRatio)) < 0.05;
      const ampSimilarity = 1 - Math.abs(this.amplitude - incomingAmp);
      
      this.resonanceScore = (isHarmonic ? 0.8 : 0.2) * ampSimilarity;
      return this.resonanceScore;
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
    if (oscillatorRef.current) {
      oscillatorRef.current.stop();
      oscillatorRef.current = null;
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
    for (let i = 2; i < bufferLength - 2; i++) {
      if (dataArray[i] > 40 && 
          dataArray[i] > dataArray[i-1] && 
          dataArray[i] > dataArray[i+1]) {
        const frequency = (i * sampleRate) / (analyserRef.current.fftSize);
        const amplitude = dataArray[i] / 255;
        
        // Calculate spectral centroid (timbre proxy)
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
    
    return peaks;
  }, []);
  
  // Play tone based on memory
  const playMemoryTone = useCallback((memory) => {
    if (!audioContextRef.current || !isPlaying) return;
    
    const ctx = audioContextRef.current;
    const now = ctx.currentTime;
    
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    
    osc.frequency.setValueAtTime(memory.frequency, now);
    osc.type = ['sine', 'square', 'sawtooth', 'triangle', 'sine'][memory.geometryType];
    
    gain.gain.setValueAtTime(0, now);
    gain.gain.linearRampToValueAtTime(memory.amplitude * 0.1, now + 0.05);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.3);
    
    osc.connect(gain);
    gain.connect(ctx.destination);
    
    osc.start(now);
    osc.stop(now + 0.3);
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
      
      const width = canvas.width = window.innerWidth;
      const height = canvas.height = window.innerHeight;
      const centerX = width / 2;
      const centerY = height / 2;
      
      // Clear with fade
      ctx.fillStyle = 'rgba(10, 10, 20, 0.15)';
      ctx.fillRect(0, 0, width, height);
      
      // Draw center
      ctx.beginPath();
      ctx.arc(centerX, centerY, 10, 0, Math.PI * 2);
      ctx.fillStyle = `hsla(280, 80%, 60%, 0.8)`;
      ctx.fill();
      
      // LEARNING MODE: Analyze incoming audio
      if (isListening && analyserRef.current) {
        const peaks = analyzeAndLearn();
        
        if (peaks && peaks.length > 0) {
          peaks.forEach(peak => {
            // Check for resonance with existing memories
            let bestResonance = 0;
            let resonantMemory = null;
            
            memoriesRef.current.forEach(memory => {
              const resonance = memory.calculateResonance(peak.frequency, peak.amplitude);
              if (resonance > bestResonance) {
                bestResonance = resonance;
                resonantMemory = memory;
              }
            });
            
            if (bestResonance > 0.6 && resonantMemory) {
              // Strengthen existing memory
              resonantMemory.activate(0.3, currentTime);
            } else {
              // Create new memory
              const newMemory = new MusicalMemory(
                peak.frequency,
                peak.amplitude,
                peak.timbre,
                currentTime
              );
              memoriesRef.current.push(newMemory);
              
              // Find and create connections to similar memories
              memoriesRef.current.forEach(other => {
                if (other !== newMemory) {
                  const freqDiff = Math.abs(other.frequency - newMemory.frequency);
                  if (freqDiff < 50) {
                    newMemory.connections.push(other);
                  }
                }
              });
            }
          });
        }
      }
      
      // PLAYBACK MODE: Activate memories based on resonance
      if (isPlaying && memoriesRef.current.length > 0) {
        // Calculate overall resonance field
        let totalResonance = 0;
        
        memoriesRef.current.forEach(memory => {
          // Decay over time
          memory.decay(deltaTime);
          
          // Activate based on connections and phase
          memory.phase += deltaTime * (memory.frequency / 100);
          
          if (Math.sin(memory.phase) > 0.9) {
            memory.activate(0.5, currentTime);
            activeMemoriesRef.current.add(memory);
            playMemoryTone(memory);
            
            // Activate connected memories
            memory.connections.forEach(connected => {
              connected.activate(0.2, currentTime);
            });
          }
          
          totalResonance += memory.activationStrength;
        });
        
        setResonanceLevel(Math.min(1, totalResonance / 10));
      }
      
      // Draw memories
      memoriesRef.current.forEach((memory, idx) => {
        const x = centerX + Math.cos(memory.angle) * memory.distance;
        const y = centerY + Math.sin(memory.angle) * memory.distance;
        
        // Draw connections
        ctx.strokeStyle = `hsla(${memory.hue}, 70%, 50%, ${memory.brightness * 0.2})`;
        ctx.lineWidth = 1;
        memory.connections.forEach(connected => {
          const connX = centerX + Math.cos(connected.angle) * connected.distance;
          const connY = centerY + Math.sin(connected.angle) * connected.distance;
          ctx.beginPath();
          ctx.moveTo(x, y);
          ctx.lineTo(connX, connY);
          ctx.stroke();
        });
        
        // Draw memory node with dancing effect
        const danceOffset = memory.activationStrength * 10 * Math.sin(memory.phase * 3);
        const drawX = x + danceOffset;
        const drawY = y + danceOffset * 0.5;
        
        ctx.save();
        ctx.translate(drawX, drawY);
        ctx.rotate(memory.phase);
        
        // Different geometries based on timbre
        ctx.fillStyle = `hsla(${memory.hue}, 80%, ${30 + memory.brightness * 50}%, ${memory.brightness})`;
        ctx.strokeStyle = `hsla(${memory.hue}, 90%, 70%, ${memory.brightness})`;
        ctx.lineWidth = 2;
        
        switch(memory.geometryType) {
          case 0: // Circle
            ctx.beginPath();
            ctx.arc(0, 0, memory.size, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();
            break;
          case 1: // Triangle
            ctx.beginPath();
            ctx.moveTo(0, -memory.size);
            ctx.lineTo(memory.size * 0.866, memory.size * 0.5);
            ctx.lineTo(-memory.size * 0.866, memory.size * 0.5);
            ctx.closePath();
            ctx.fill();
            ctx.stroke();
            break;
          case 2: // Square
            ctx.fillRect(-memory.size/2, -memory.size/2, memory.size, memory.size);
            ctx.strokeRect(-memory.size/2, -memory.size/2, memory.size, memory.size);
            break;
          case 3: // Pentagon
            ctx.beginPath();
            for (let i = 0; i < 5; i++) {
              const angle = (i * 2 * Math.PI / 5) - Math.PI / 2;
              const px = Math.cos(angle) * memory.size;
              const py = Math.sin(angle) * memory.size;
              if (i === 0) ctx.moveTo(px, py);
              else ctx.lineTo(px, py);
            }
            ctx.closePath();
            ctx.fill();
            ctx.stroke();
            break;
          case 4: // Star
            ctx.beginPath();
            for (let i = 0; i < 10; i++) {
              const angle = (i * Math.PI / 5) - Math.PI / 2;
              const r = (i % 2 === 0) ? memory.size : memory.size * 0.5;
              const px = Math.cos(angle) * r;
              const py = Math.sin(angle) * r;
              if (i === 0) ctx.moveTo(px, py);
              else ctx.lineTo(px, py);
            }
            ctx.closePath();
            ctx.fill();
            ctx.stroke();
            break;
        }
        
        ctx.restore();
        
        // Draw activation glow
        if (memory.activationStrength > 0.3) {
          const gradient = ctx.createRadialGradient(drawX, drawY, 0, drawX, drawY, memory.size * 3);
          gradient.addColorStop(0, `hsla(${memory.hue}, 100%, 70%, ${memory.activationStrength * 0.3})`);
          gradient.addColorStop(1, 'transparent');
          ctx.fillStyle = gradient;
          ctx.beginPath();
          ctx.arc(drawX, drawY, memory.size * 3, 0, Math.PI * 2);
          ctx.fill();
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
  }, [isListening, isPlaying, analyzeAndLearn, playMemoryTone]);
  
  // Cleanup
  useEffect(() => {
    return () => {
      stopAudio();
    };
  }, [stopAudio]);
  
  const resetMemories = () => {
    memoriesRef.current = [];
    activeMemoriesRef.current.clear();
    setMemoryCount(0);
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
            🎵 Fractal Music Learner
          </h1>
          <p className="text-sm text-purple-300">
            Memory organized by resonance • β ≈ 0.5 coherence
          </p>
          <p className="text-xs text-gray-400 mt-1">
            Fractal Reality Framework • <a href="https://github.com/AshmanRoonz/Fractal_Reality" className="underline hover:text-purple-300">github.com/AshmanRoonz/Fractal_Reality</a>
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
                <h3 className="text-white font-bold mb-1">How It Works</h3>
                <ul className="text-sm text-gray-300 space-y-1">
                  <li>🎤 <strong>Listen Mode:</strong> Learns music patterns through mic</li>
                  <li>🎵 <strong>Memory:</strong> Each sound stored as geometric form</li>
                  <li>📍 <strong>Organization:</strong> Radially by frequency, distance by volume</li>
                  <li>🔗 <strong>Connections:</strong> Similar frequencies link together</li>
                  <li>✨ <strong>Resonance:</strong> Harmonics strengthen memories</li>
                  <li>🎹 <strong>Playback:</strong> Cycles through memories to jam along</li>
                  <li>💃 <strong>Dancing:</strong> Active memories brighten and move</li>
                </ul>
              </div>
            </div>
          </div>
        )}
        
        {/* Stats */}
        <div className="absolute top-4 left-1/2 -translate-x-1/2 pointer-events-auto">
          <div className="bg-black/70 backdrop-blur-sm rounded-lg px-6 py-3 border border-purple-500/50">
            <div className="flex gap-6 text-white text-sm">
              <div>
                <span className="text-gray-400">Memories:</span>{' '}
                <span className="font-bold text-cyan-400">{memoryCount}</span>
              </div>
              <div>
                <span className="text-gray-400">Resonance:</span>{' '}
                <span className="font-bold text-purple-400">
                  {(resonanceLevel * 100).toFixed(0)}%
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
                ? 'bg-red-500 hover:bg-red-600 text-white'
                : 'bg-green-500 hover:bg-green-600 text-white'
            }`}
          >
            {isListening ? (
              <>
                <MicOff className="w-5 h-5" />
                Stop Listening
              </>
            ) : (
              <>
                <Mic className="w-5 h-5" />
                Start Listening
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
                ? 'bg-purple-500 hover:bg-purple-600 text-white'
                : 'bg-blue-500 hover:bg-blue-600 text-white'
            }`}
          >
            {isPlaying ? (
              <>
                <Pause className="w-5 h-5" />
                Pause Jam
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                Start Jam
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
