import React, { useState, useMemo, useRef, useEffect } from 'react';
import { Music, Trash2, Play, Volume2, Info, Sparkles, Zap, X, Atom, Radio } from 'lucide-react';

const MolecularComposer = () => {
  const [selectedElements, setSelectedElements] = useState([]);
  const [audioContext, setAudioContext] = useState(null);
  const [soundEnabled, setSoundEnabled] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showInfo, setShowInfo] = useState(true);
  const [cycleSpeed, setCycleSpeed] = useState(2);
  const [wavePhase, setWavePhase] = useState(0);
  const canvasRef = useRef(null);
  const stopPlayingRef = useRef(false);
  const animationRef = useRef(null);
  const oscillatorsRef = useRef([]);

  // Element library with full particle counts
  const elements = [
    { symbol: 'H', name: 'Hydrogen', z: 1, n: 0, e: 1, color: '#60a5fa', mass: 1 },
    { symbol: 'He', name: 'Helium', z: 2, n: 2, e: 2, color: '#a78bfa', mass: 4, noble: true },
    { symbol: 'C', name: 'Carbon', z: 6, n: 6, e: 6, color: '#8b5cf6', mass: 12 },
    { symbol: 'N', name: 'Nitrogen', z: 7, n: 7, e: 7, color: '#22d3ee', mass: 14 },
    { symbol: 'O', name: 'Oxygen', z: 8, n: 8, e: 8, color: '#ef4444', mass: 16 },
    { symbol: 'F', name: 'Fluorine', z: 9, n: 10, e: 9, color: '#f59e0b', mass: 19 },
    { symbol: 'Ne', name: 'Neon', z: 10, n: 10, e: 10, color: '#a78bfa', mass: 20, noble: true },
    { symbol: 'Na', name: 'Sodium', z: 11, n: 12, e: 11, color: '#fbbf24', mass: 23 },
    { symbol: 'Mg', name: 'Magnesium', z: 12, n: 12, e: 12, color: '#10b981', mass: 24 },
    { symbol: 'P', name: 'Phosphorus', z: 15, n: 16, e: 15, color: '#f97316', mass: 31 },
    { symbol: 'S', name: 'Sulfur', z: 16, n: 16, e: 16, color: '#eab308', mass: 32 },
    { symbol: 'Cl', name: 'Chlorine', z: 17, n: 18, e: 17, color: '#84cc16', mass: 35 },
    { symbol: 'Ar', name: 'Argon', z: 18, n: 22, e: 18, color: '#a78bfa', mass: 40, noble: true },
    { symbol: 'K', name: 'Potassium', z: 19, n: 20, e: 19, color: '#fbbf24', mass: 39 },
    { symbol: 'Ca', name: 'Calcium', z: 20, n: 20, e: 20, color: '#10b981', mass: 40 },
    { symbol: 'Fe', name: 'Iron', z: 26, n: 30, e: 26, color: '#ec4899', mass: 56 },
    { symbol: 'Cu', name: 'Copper', z: 29, n: 34, e: 29, color: '#ec4899', mass: 63 },
  ];

  // Famous molecules database
  const famousMolecules = {
    'Breathable Air': [
      {
        name: 'Air (Typical Mix)',
        formula: '78% N₂ + 21% O₂ + 1% Ar',
        elements: ['N','N','N','N','N','N','N','N','N','N','N','N','N','N','N','N','O','O','O','O','O','O','O','O','O','O','Ar'],
        bondType: 'Mixed atmosphere',
        vibrationFreq: 5.5,
        description: 'What we breathe! 280e⁻ 280p⁺ 296n⁰',
        tempo: 'Allegro'
      },
      {
        name: 'Oxygen',
        formula: 'O₂',
        elements: ['O', 'O'],
        bondType: 'Double',
        vibrationFreq: 7.5,
        description: '16e⁻ 16p⁺ 16n⁰ - Life-giving molecule',
        tempo: 'Vivace'
      },
      {
        name: 'Nitrogen',
        formula: 'N₂',
        elements: ['N', 'N'],
        bondType: 'Triple',
        vibrationFreq: 9.0,
        description: '14e⁻ 14p⁺ 14n⁰ - 78% of atmosphere',
        tempo: 'Presto'
      },
      {
        name: 'Carbon Dioxide',
        formula: 'CO₂',
        elements: ['C', 'O', 'O'],
        bondType: 'Linear',
        vibrationFreq: 4.2,
        description: '22e⁻ 22p⁺ 22n⁰ - What we exhale',
        tempo: 'Moderato'
      },
    ],
    'Water & Life': [
      {
        name: 'Water',
        formula: 'H₂O',
        elements: ['H', 'H', 'O'],
        bondType: 'Bent',
        vibrationFreq: 3.5,
        description: '10e⁻ 10p⁺ 8n⁰ - Universal solvent',
        tempo: 'Andante'
      },
      {
        name: 'Hydrogen Peroxide',
        formula: 'H₂O₂',
        elements: ['H', 'H', 'O', 'O'],
        bondType: 'Bent-bent',
        vibrationFreq: 4.0,
        description: '18e⁻ 18p⁺ 16n⁰ - Disinfectant',
        tempo: 'Moderato'
      },
      {
        name: 'Ammonia',
        formula: 'NH₃',
        elements: ['N', 'H', 'H', 'H'],
        bondType: 'Pyramidal',
        vibrationFreq: 4.8,
        description: '10e⁻ 10p⁺ 7n⁰ - Pungent gas',
        tempo: 'Allegro'
      },
      {
        name: 'Methane',
        formula: 'CH₄',
        elements: ['C', 'H', 'H', 'H', 'H'],
        bondType: 'Tetrahedral',
        vibrationFreq: 5.2,
        description: '10e⁻ 10p⁺ 6n⁰ - Natural gas',
        tempo: 'Allegro'
      },
    ],
    'Common Compounds': [
      {
        name: 'Table Salt',
        formula: 'NaCl',
        elements: ['Na', 'Cl'],
        bondType: 'Ionic',
        vibrationFreq: 3.0,
        description: '28e⁻ 28p⁺ 30n⁰ - Sodium chloride',
        tempo: 'Moderato'
      },
      {
        name: 'Hydrochloric Acid',
        formula: 'HCl',
        elements: ['H', 'Cl'],
        bondType: 'Polar covalent',
        vibrationFreq: 8.0,
        description: '18e⁻ 18p⁺ 18n⁰ - Stomach acid',
        tempo: 'Vivace'
      },
      {
        name: 'Calcium Carbonate',
        formula: 'CaCO₃',
        elements: ['Ca', 'C', 'O', 'O', 'O'],
        bondType: 'Ionic/covalent',
        vibrationFreq: 2.6,
        description: '50e⁻ 50p⁺ 50n⁰ - Limestone, chalk',
        tempo: 'Andante'
      },
    ],
    'Biochemical': [
      {
        name: 'Glucose',
        formula: 'C₆H₁₂O₆',
        elements: ['C','C','C','C','C','C','H','H','H','H','H','H','H','H','H','H','H','H','O','O','O','O','O','O'],
        bondType: 'Ring',
        vibrationFreq: 1.8,
        description: '72e⁻ 72p⁺ 66n⁰ - Blood sugar, energy',
        tempo: 'Lento'
      },
      {
        name: 'Ethanol',
        formula: 'C₂H₅OH',
        elements: ['C', 'C', 'H', 'H', 'H', 'H', 'H', 'O', 'H'],
        bondType: 'Hydroxyl',
        vibrationFreq: 2.4,
        description: '26e⁻ 26p⁺ 20n⁰ - Alcohol',
        tempo: 'Andante'
      },
    ],
  };

  const initAudio = () => {
    if (!audioContext) {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      setAudioContext(ctx);
      setSoundEnabled(true);
    }
  };

  const addElement = (element) => {
    setSelectedElements([...selectedElements, { ...element, id: Date.now() + Math.random() }]);
  };

  const addElementBySymbol = (symbol) => {
    const element = elements.find(e => e.symbol === symbol);
    if (element) {
      addElement(element);
    }
  };

  const removeElement = (id) => {
    setSelectedElements(selectedElements.filter(el => el.id !== id));
  };

  const clearMolecule = () => {
    setSelectedElements([]);
    stopPlaying();
  };

  const loadMolecule = (molecule) => {
    const elementList = molecule.elements.map((symbol, idx) => {
      const el = elements.find(e => e.symbol === symbol);
      return { ...el, id: Date.now() + idx };
    });
    setSelectedElements(elementList);
    setCycleSpeed(molecule.vibrationFreq);
  };

  // Calculate frequency for particles
  const getParticleFrequency = (count, particleType) => {
    const baseFreq = 261.63;
    const baseOctaves = {
      electron: 0,
      proton: 1,
      neutron: 0.5
    };
    
    if (count === 0) return null;
    const octave = Math.log2(count) + baseOctaves[particleType];
    return baseFreq * Math.pow(2, octave);
  };

  const stopPlaying = () => {
    stopPlayingRef.current = true;
    setIsPlaying(false);
    oscillatorsRef.current.forEach(({ oscillator }) => {
      try {
        oscillator.stop();
      } catch (e) {}
    });
    oscillatorsRef.current = [];
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
  };

  // Continuous play
  const playMoleculeSong = () => {
    if (!audioContext || !soundEnabled || selectedElements.length === 0 || isPlaying) return;

    setIsPlaying(true);
    stopPlayingRef.current = false;
    oscillatorsRef.current = [];

    selectedElements.forEach((el, atomIndex) => {
      const particles = [
        { type: 'electron', count: el.e, wave: 'sine', baseVol: 0.08 },
        { type: 'proton', count: el.z, wave: 'triangle', baseVol: 0.10 },
        { type: 'neutron', count: el.n, wave: 'square', baseVol: 0.06 }
      ];

      particles.forEach(({ type, count, wave, baseVol }) => {
        if (count === 0) return;
        
        const freq = getParticleFrequency(count, type);
        if (!freq) return;

        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.type = wave;
        oscillator.frequency.setValueAtTime(freq, audioContext.currentTime);
        gainNode.gain.setValueAtTime(0, audioContext.currentTime);

        oscillator.start(audioContext.currentTime);
        
        oscillatorsRef.current.push({ 
          oscillator, 
          gainNode, 
          atomIndex, 
          baseVol,
          type 
        });
      });
    });

    const modulateVolumes = () => {
      if (stopPlayingRef.current) {
        stopPlaying();
        return;
      }

      const time = audioContext.currentTime;

      oscillatorsRef.current.forEach(({ gainNode, atomIndex, baseVol }) => {
        const atomPhase = atomIndex / selectedElements.length;
        const distance = Math.abs(wavePhase - atomPhase);
        const normalizedDist = Math.min(distance, 1 - distance) * 2;
        
        const envelope = Math.pow(Math.cos(normalizedDist * Math.PI / 2), 2);
        const targetGain = baseVol * envelope;

        gainNode.gain.setTargetAtTime(targetGain, time, 0.01);
      });

      setTimeout(modulateVolumes, 20);
    };

    modulateVolumes();
  };

  // Canvas drawing effect - SUPERIMPOSED waves showing emergent pattern
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || selectedElements.length === 0) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    const draw = () => {
      // Clear canvas with dark background
      ctx.fillStyle = 'rgba(15, 23, 42, 0.95)';
      ctx.fillRect(0, 0, width, height);

      const centerY = height / 2;
      const elementCount = selectedElements.length;

      // Draw center line
      ctx.strokeStyle = 'rgba(148, 163, 184, 0.2)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(60, centerY);
      ctx.lineTo(width - 20, centerY);
      ctx.stroke();

      // Draw each atom's waveform SUPERIMPOSED on the same baseline
      selectedElements.forEach((el, idx) => {
        const atomPhase = idx / elementCount;
        const phase = (wavePhase - atomPhase + 1) % 1;

        // Draw waveform
        ctx.beginPath();
        ctx.strokeStyle = el.color;
        ctx.lineWidth = 2;
        ctx.globalAlpha = 0.6; // Semi-transparent so we can see overlaps

        for (let i = 0; i < width - 80; i++) {
          const x = 60 + i;
          const wavePhaseAtX = (phase + i / 50) * Math.PI * 2;
          const amplitude = 40 * Math.cos(phase * Math.PI * 2); // Larger amplitude
          const y = centerY + Math.sin(wavePhaseAtX) * Math.abs(amplitude);
          
          if (i === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        }
        ctx.stroke();
        ctx.globalAlpha = 1;
      });

      // Now draw the EMERGENT PATTERN - sum of all waves
      ctx.beginPath();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 3;
      ctx.globalAlpha = 1;
      ctx.shadowColor = '#ffffff';
      ctx.shadowBlur = 10;

      for (let i = 0; i < width - 80; i++) {
        const x = 60 + i;
        let sumY = 0;
        
        // Sum all waves at this x position
        selectedElements.forEach((el, idx) => {
          const atomPhase = idx / elementCount;
          const phase = (wavePhase - atomPhase + 1) % 1;
          const wavePhaseAtX = (phase + i / 50) * Math.PI * 2;
          const amplitude = 40 * Math.cos(phase * Math.PI * 2);
          sumY += Math.sin(wavePhaseAtX) * Math.abs(amplitude);
        });
        
        const y = centerY + sumY / elementCount; // Average the sum
        
        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
      ctx.stroke();
      ctx.shadowBlur = 0;

      // Draw legend on the left
      const legendX = 10;
      let legendY = 30;
      
      selectedElements.forEach((el, idx) => {
        // Color swatch
        ctx.fillStyle = el.color;
        ctx.fillRect(legendX, legendY - 10, 20, 12);
        
        // Element info
        ctx.fillStyle = el.color;
        ctx.font = 'bold 12px sans-serif';
        ctx.fillText(el.symbol, legendX + 25, legendY);
        
        ctx.fillStyle = '#94a3b8';
        ctx.font = '9px monospace';
        ctx.fillText(`${el.e}e⁻ ${el.z}p⁺ ${el.n}n⁰`, legendX + 25, legendY + 10);
        
        legendY += 35;
      });

      // Label for emergent pattern
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 14px sans-serif';
      ctx.fillText('EMERGENT PATTERN', width - 180, 30);
      ctx.fillRect(width - 200, 35, 30, 3);
    };

    draw();
  }, [selectedElements, wavePhase]);

  // Animate wave phase
  useEffect(() => {
    if (!isPlaying) return;

    let lastTime = Date.now();
    const animate = () => {
      const now = Date.now();
      const dt = (now - lastTime) / 1000;
      lastTime = now;

      setWavePhase(prev => (prev + dt * cycleSpeed) % 1);

      if (isPlaying) {
        animationRef.current = requestAnimationFrame(animate);
      }
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isPlaying, cycleSpeed]);

  // Analyze molecule
  const analyzeMolecule = useMemo(() => {
    if (selectedElements.length === 0) return null;

    const totalElectrons = selectedElements.reduce((sum, el) => sum + el.e, 0);
    const totalProtons = selectedElements.reduce((sum, el) => sum + el.z, 0);
    const totalNeutrons = selectedElements.reduce((sum, el) => sum + el.n, 0);

    const elementCounts = {};
    selectedElements.forEach(el => {
      elementCounts[el.symbol] = (elementCounts[el.symbol] || 0) + 1;
    });

    const formula = Object.entries(elementCounts)
      .map(([sym, count]) => {
        if (count === 1) return sym;
        const subscripts = '₀₁₂₃₄₅₆₇₈₉';
        return sym + count.toString().split('').map(d => subscripts[parseInt(d)]).join('');
      })
      .join('');

    const epRatio = totalElectrons === totalProtons;
    const pnRatio = totalProtons === totalNeutrons;
    const allEqual = epRatio && totalElectrons === totalNeutrons;

    return {
      formula,
      totalElectrons,
      totalProtons,
      totalNeutrons,
      elementCount: selectedElements.length,
      totalMass: selectedElements.reduce((sum, el) => sum + el.mass, 0),
      epRatio,
      pnRatio,
      allEqual,
      elementCounts
    };
  }, [selectedElements]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white p-4">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="text-center mb-6">
          <div className="flex items-center justify-center gap-3 mb-3">
            <Radio className="w-10 h-10 text-cyan-400" />
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Molecular Song Composer (Canvas)
            </h1>
            <Sparkles className="w-10 h-10 text-pink-400" />
          </div>
          <p className="text-lg text-cyan-200">
            Molecules are SONGS! Atoms cycle through vibrations.
          </p>
        </div>

        {/* Info Panel */}
        {showInfo && (
          <div className="mb-6 bg-gradient-to-r from-purple-900/50 via-pink-900/50 to-purple-900/50 rounded-xl p-6 border border-purple-500/50 relative">
            <button
              onClick={() => setShowInfo(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
            <div className="flex items-start gap-4">
              <Info className="w-6 h-6 text-cyan-400 flex-shrink-0 mt-1" />
              <div>
                <h3 className="text-xl font-bold text-pink-300 mb-2">How it works</h3>
                <p className="text-gray-300 mb-2">
                  Each atom vibrates with 3 frequencies: electrons (sine), protons (triangle), neutrons (square).
                  The wave cycles through atoms in sequence—this is molecular breathing!
                </p>
                <p className="text-sm text-cyan-300">
                  Based on real molecular vibrations measured by IR spectroscopy. Reference: <a href="https://github.com/AshmanRoonz/Fractal_Reality" target="_blank" rel="noopener noreferrer" className="underline">Fractal Reality Framework</a>
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Analysis Panel */}
        {analyzeMolecule && (
          <div className="mb-6 bg-black/40 rounded-xl p-4 border border-yellow-500/30">
            <div className="grid md:grid-cols-3 gap-4">
              <div>
                <div className="text-2xl font-bold text-yellow-400">{analyzeMolecule.formula}</div>
                <div className="text-sm text-gray-400">{analyzeMolecule.elementCount} atoms • {analyzeMolecule.totalMass}u</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-mono">
                  <span className="text-cyan-400">{analyzeMolecule.totalElectrons}e⁻</span>
                  {' • '}
                  <span className="text-pink-400">{analyzeMolecule.totalProtons}p⁺</span>
                  {' • '}
                  <span className="text-yellow-400">{analyzeMolecule.totalNeutrons}n⁰</span>
                </div>
              </div>
              <div className="text-right text-sm">
                {analyzeMolecule.allEqual && (
                  <div className="text-green-400">✨ Perfect Balance!</div>
                )}
                {!analyzeMolecule.allEqual && analyzeMolecule.epRatio && (
                  <div className="text-blue-400">⚡ Neutral Charge</div>
                )}
                <div className="text-gray-400">
                  Vibration: {cycleSpeed.toFixed(1)} Hz •{' '}
                  {cycleSpeed < 2 ? '🐌 Very slow' :
                   cycleSpeed < 4 ? '🎵 Slow' :
                   cycleSpeed < 6 ? '⚡ Moderate' :
                   cycleSpeed < 8 ? '🚀 Fast' : '⭐ Very fast'}
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="grid lg:grid-cols-2 gap-6">
          
          {/* Left: Molecule Builder */}
          <div className="space-y-6">
            
            {/* Current Molecule Display - Canvas Version */}
            <div className="bg-black/30 rounded-xl p-6 border border-cyan-500/30">
              <h2 className="text-2xl font-bold text-cyan-300 mb-4 flex items-center gap-2">
                <Music className="w-6 h-6" />
                Your Molecular Song
              </h2>
              
              {selectedElements.length === 0 ? (
                <div className="text-center py-12 text-gray-400">
                  <Atom className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p className="text-lg">No atoms selected yet</p>
                  <p className="text-sm mt-2">Load a molecule below or use dropdown to add atoms</p>
                </div>
              ) : (
                <div>
                  {/* Canvas Visualization */}
                  <div className="mb-6 bg-slate-900/70 rounded-lg overflow-hidden border border-cyan-500/30">
                    <canvas
                      ref={canvasRef}
                      width={800}
                      height={300}
                      className="w-full"
                      style={{ display: 'block' }}
                    />
                  </div>

                  {/* Controls */}
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">
                        Vibration Speed: {cycleSpeed.toFixed(1)} Hz
                      </label>
                      <input
                        type="range"
                        min="0.5"
                        max="10"
                        step="0.1"
                        value={cycleSpeed}
                        onChange={(e) => setCycleSpeed(parseFloat(e.target.value))}
                        className="w-full"
                      />
                    </div>

                    <div className="flex gap-2">
                      <button
                        onClick={soundEnabled ? playMoleculeSong : initAudio}
                        disabled={selectedElements.length === 0}
                        className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 disabled:from-gray-700 disabled:to-gray-800 text-white font-bold py-3 px-6 rounded-lg flex items-center justify-center gap-2 transition-all"
                      >
                        {!soundEnabled ? (
                          <>
                            <Volume2 className="w-5 h-5" />
                            Enable Sound
                          </>
                        ) : isPlaying ? (
                          <>
                            <Zap className="w-5 h-5 animate-pulse" />
                            Playing...
                          </>
                        ) : (
                          <>
                            <Play className="w-5 h-5" />
                            Play Song
                          </>
                        )}
                      </button>
                      
                      {isPlaying && (
                        <button
                          onClick={stopPlaying}
                          className="bg-red-600 hover:bg-red-500 text-white font-bold py-3 px-6 rounded-lg transition-all"
                        >
                          Stop
                        </button>
                      )}
                      
                      <button
                        onClick={clearMolecule}
                        disabled={selectedElements.length === 0}
                        className="bg-red-900/50 hover:bg-red-900/70 disabled:bg-gray-800 text-white p-3 rounded-lg transition-all"
                        title="Clear all atoms"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>

                    {/* Atom list */}
                    <div className="max-h-32 overflow-y-auto space-y-2">
                      {selectedElements.map((el) => (
                        <div
                          key={el.id}
                          className="flex items-center justify-between bg-slate-800/50 rounded p-2 border"
                          style={{ borderColor: el.color + '40' }}
                        >
                          <div className="flex items-center gap-2">
                            <div
                              className="w-8 h-8 rounded-full flex items-center justify-center font-bold"
                              style={{ backgroundColor: el.color + '30', color: el.color }}
                            >
                              {el.symbol}
                            </div>
                            <div>
                              <div className="text-sm font-bold">{el.name}</div>
                              <div className="text-xs text-gray-400">{el.e}e⁻ {el.z}p⁺ {el.n}n⁰</div>
                            </div>
                          </div>
                          <button
                            onClick={() => removeElement(el.id)}
                            className="text-red-400 hover:text-red-300"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Famous Molecules */}
            <div className="bg-black/30 rounded-xl p-6 border border-purple-500/30">
              <h2 className="text-2xl font-bold text-purple-300 mb-4">Load Famous Molecules</h2>
              <div className="space-y-4">
                {Object.entries(famousMolecules).map(([category, molecules]) => (
                  <div key={category}>
                    <h3 className="text-lg font-bold text-pink-400 mb-2">{category}</h3>
                    <div className="grid gap-2">
                      {molecules.map((mol, idx) => (
                        <button
                          key={idx}
                          onClick={() => loadMolecule(mol)}
                          className="w-full bg-purple-900/20 hover:bg-purple-900/40 rounded-lg p-3 border border-purple-500/30 transition-all text-left"
                        >
                          <div className="flex justify-between items-start mb-1">
                            <div className="font-bold text-cyan-300">{mol.name}</div>
                            <div className="text-sm text-purple-300 font-mono">{mol.formula}</div>
                          </div>
                          <div className="text-xs text-yellow-400 mb-1">
                            {mol.vibrationFreq.toFixed(1)} Hz • {mol.tempo}
                          </div>
                          <div className="text-xs text-gray-400">{mol.bondType}</div>
                          <div className="text-xs text-gray-500 mt-1">{mol.description}</div>
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>

          {/* Right: Element Palette */}
          <div className="bg-black/30 rounded-xl p-6 border border-pink-500/30">
            <h2 className="text-2xl font-bold text-pink-300 mb-4">Add Atoms</h2>
            
            {/* Dropdown */}
            <div className="mb-6">
              <label className="block text-sm text-gray-400 mb-2">Select element to add:</label>
              <select
                onChange={(e) => {
                  if (e.target.value) {
                    addElementBySymbol(e.target.value);
                    e.target.value = '';
                  }
                }}
                defaultValue=""
                className="w-full bg-slate-800 text-white border-2 border-purple-500/50 rounded-lg p-3 text-lg font-bold cursor-pointer hover:border-purple-500 transition-all"
              >
                <option value="" disabled>Choose an element...</option>
                {elements.map((el) => (
                  <option key={el.symbol} value={el.symbol}>
                    {el.symbol} - {el.name} ({el.e}e⁻ {el.z}p⁺ {el.n}n⁰)
                  </option>
                ))}
              </select>
            </div>

            {/* Quick add */}
            <div className="mb-6">
              <p className="text-sm text-gray-400 mb-3">Quick add common atoms:</p>
              <div className="grid grid-cols-4 gap-2">
                {elements.slice(0, 12).map((el) => (
                  <button
                    key={el.symbol}
                    onClick={() => addElement(el)}
                    className="p-3 rounded-lg border-2 transition-all hover:scale-105"
                    style={{ 
                      backgroundColor: el.color + '20',
                      borderColor: el.color
                    }}
                    title={el.name}
                  >
                    <div className="text-xl font-bold" style={{ color: el.color }}>
                      {el.symbol}
                    </div>
                    <div className="text-[8px] text-gray-400">{el.mass}u</div>
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-4">
              <div className="bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-lg p-4 border border-pink-500/30">
                <div className="text-center">
                  <div className="text-lg font-bold text-pink-300 mb-2">🎵 The Molecular Symphony 🎵</div>
                  <p className="text-sm text-gray-300 mb-2">
                    A molecule isn't a static chord - it's a SONG that cycles!
                  </p>
                  <p className="text-sm text-cyan-300">
                    Bonds vibrate, atoms oscillate, molecules breathe.
                  </p>
                </div>
              </div>

              <div className="bg-gradient-to-r from-cyan-900/50 to-blue-900/50 rounded-lg p-4 border border-cyan-500/30">
                <div className="text-center">
                  <div className="text-lg font-bold text-cyan-300 mb-2">⚛️ Real Science!</div>
                  <p className="text-sm text-gray-300">
                    This is what <strong>IR spectroscopy</strong> measures - molecular vibrations!
                  </p>
                  <p className="text-xs text-gray-400 mt-2">
                    Framework: <a href="https://github.com/AshmanRoonz/Fractal_Reality" target="_blank" rel="noopener noreferrer" className="text-cyan-400 underline">Fractal Reality</a>
                  </p>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default MolecularComposer;