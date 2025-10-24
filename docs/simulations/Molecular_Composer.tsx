import React, { useState, useMemo, useRef, useEffect } from 'react';
import { Music, Trash2, Play, Volume2, Info, Sparkles, Zap, X, Atom, Radio } from 'lucide-react';

const App = () => {
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
  };

  const stats = useMemo(() => {
    const totalE = selectedElements.reduce((sum, el) => sum + el.e, 0);
    const totalZ = selectedElements.reduce((sum, el) => sum + el.z, 0);
    const totalN = selectedElements.reduce((sum, el) => sum + el.n, 0);
    const totalMass = selectedElements.reduce((sum, el) => sum + el.mass, 0);
    return { e: totalE, z: totalZ, n: totalN, mass: totalMass };
  }, [selectedElements]);

  const frequencyMap = useMemo(() => {
    const freqCount = {};
    selectedElements.forEach(el => {
      const freq = (el.z / 10) * 440;
      freqCount[freq] = (freqCount[freq] || 0) + 1;
    });
    return Object.entries(freqCount).map(([freq, count]) => ({
      frequency: parseFloat(freq),
      count: count
    }));
  }, [selectedElements]);

  const stopPlaying = () => {
    stopPlayingRef.current = true;
    setIsPlaying(false);
    oscillatorsRef.current.forEach(osc => {
      try {
        osc.stop();
      } catch (e) {}
    });
    oscillatorsRef.current = [];
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
  };

  const playMoleculeSong = async () => {
    if (!audioContext || selectedElements.length === 0) return;
    
    stopPlaying();
    stopPlayingRef.current = false;
    setIsPlaying(true);
    
    const masterGain = audioContext.createGain();
    masterGain.connect(audioContext.destination);
    masterGain.gain.value = 0.15;
    
    const cycleDuration = 4000 / cycleSpeed;
    const beatsPerCycle = selectedElements.length;
    const beatDuration = cycleDuration / beatsPerCycle;
    
    let currentBeat = 0;
    
    const playNextBeat = () => {
      if (stopPlayingRef.current) {
        stopPlaying();
        return;
      }
      
      const el = selectedElements[currentBeat % selectedElements.length];
      const frequency = (el.z / 10) * 440;
      const duration = beatDuration / 1000;
      
      const osc = audioContext.createOscillator();
      const gain = audioContext.createGain();
      
      osc.type = el.noble ? 'sine' : 'triangle';
      osc.frequency.value = frequency;
      
      osc.connect(gain);
      gain.connect(masterGain);
      
      gain.gain.setValueAtTime(0, audioContext.currentTime);
      gain.gain.linearRampToValueAtTime(0.5, audioContext.currentTime + 0.01);
      gain.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);
      
      osc.start(audioContext.currentTime);
      osc.stop(audioContext.currentTime + duration);
      
      oscillatorsRef.current.push(osc);
      
      currentBeat++;
      
      if (currentBeat < selectedElements.length * 3) {
        setTimeout(playNextBeat, beatDuration);
      } else {
        stopPlaying();
      }
    };
    
    playNextBeat();
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    let animationId;
    let phase = 0;
    
    const animate = () => {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
      ctx.fillRect(0, 0, width, height);
      
      if (selectedElements.length > 0) {
        const centerX = width / 2;
        const centerY = height / 2;
        const radius = Math.min(width, height) * 0.35;
        
        selectedElements.forEach((el, i) => {
          const angle = (i / selectedElements.length) * Math.PI * 2 + phase;
          const x = centerX + Math.cos(angle) * radius;
          const y = centerY + Math.sin(angle) * radius;
          
          const gradient = ctx.createRadialGradient(x, y, 0, x, y, 20);
          gradient.addColorStop(0, el.color);
          gradient.addColorStop(1, 'rgba(0,0,0,0)');
          
          ctx.fillStyle = gradient;
          ctx.beginPath();
          ctx.arc(x, y, 20, 0, Math.PI * 2);
          ctx.fill();
          
          ctx.fillStyle = '#fff';
          ctx.font = 'bold 12px monospace';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(el.symbol, x, y);
        });
        
        for (let i = 0; i < selectedElements.length; i++) {
          const angle1 = (i / selectedElements.length) * Math.PI * 2 + phase;
          const angle2 = ((i + 1) / selectedElements.length) * Math.PI * 2 + phase;
          
          const x1 = centerX + Math.cos(angle1) * radius;
          const y1 = centerY + Math.sin(angle1) * radius;
          const x2 = centerX + Math.cos(angle2) * radius;
          const y2 = centerY + Math.sin(angle2) * radius;
          
          ctx.strokeStyle = 'rgba(168, 85, 247, 0.3)';
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.moveTo(x1, y1);
          ctx.lineTo(x2, y2);
          ctx.stroke();
        }
      }
      
      phase += 0.01 * cycleSpeed;
      setWavePhase(phase);
      animationId = requestAnimationFrame(animate);
    };
    
    animate();
    
    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId);
      }
    };
  }, [selectedElements, cycleSpeed]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-3">
            <Atom className="w-12 h-12 text-purple-400 animate-pulse" />
            <h1 className="text-5xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Molecular Composer
            </h1>
            <Music className="w-12 h-12 text-pink-400 animate-pulse" />
          </div>
          <p className="text-xl text-gray-300 mb-2">
            Turn molecules into music! Each atom plays a note based on its atomic number.
          </p>
          <p className="text-sm text-purple-300">
            🎵 Molecules aren't static - they VIBRATE and CYCLE! 🎵
          </p>
          
          {showInfo && (
            <div className="mt-4 bg-black/30 rounded-lg p-4 border border-purple-500/30 relative">
              <button
                onClick={() => setShowInfo(false)}
                className="absolute top-2 right-2 text-gray-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
              <div className="text-left space-y-2 text-sm">
                <p className="text-cyan-300">
                  <strong>How it works:</strong> Each element plays a note based on its atomic number (Z). 
                  Hydrogen (Z=1) plays low, Copper (Z=29) plays high!
                </p>
                <p className="text-pink-300">
                  <strong>Build molecules:</strong> Add atoms from the periodic table, or load famous molecules like H₂O, O₂, or glucose!
                </p>
                <p className="text-yellow-300">
                  <strong>Listen:</strong> Your molecule cycles through its atoms in a repeating pattern - just like real molecular vibrations!
                </p>
              </div>
            </div>
          )}
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          
          {/* Left: Visualization & Controls */}
          <div className="md:col-span-2 space-y-6">
            {/* Visualization */}
            <div className="bg-black/30 rounded-xl p-6 border border-cyan-500/30">
              <h2 className="text-2xl font-bold text-cyan-300 mb-4">Molecular Visualization</h2>
              <div className="relative">
                <canvas
                  ref={canvasRef}
                  width={600}
                  height={400}
                  className="w-full bg-black/50 rounded-lg border border-purple-500/30"
                />
                {selectedElements.length === 0 && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center text-gray-400">
                      <Sparkles className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p>Add atoms to compose your molecule</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Stats & Controls */}
            {selectedElements.length > 0 && (
              <div className="bg-black/30 rounded-xl p-6 border border-purple-500/30">
                <div className="grid md:grid-cols-2 gap-6">
                  {/* Stats */}
                  <div>
                    <h3 className="text-xl font-bold text-purple-300 mb-3">Molecule Stats</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between bg-slate-800/50 rounded p-2">
                        <span className="text-cyan-300">Total Electrons:</span>
                        <span className="font-bold">{stats.e}e⁻</span>
                      </div>
                      <div className="flex justify-between bg-slate-800/50 rounded p-2">
                        <span className="text-pink-300">Total Protons:</span>
                        <span className="font-bold">{stats.z}p⁺</span>
                      </div>
                      <div className="flex justify-between bg-slate-800/50 rounded p-2">
                        <span className="text-yellow-300">Total Neutrons:</span>
                        <span className="font-bold">{stats.n}n⁰</span>
                      </div>
                      <div className="flex justify-between bg-slate-800/50 rounded p-2">
                        <span className="text-green-300">Molecular Mass:</span>
                        <span className="font-bold">{stats.mass}u</span>
                      </div>
                      <div className="flex justify-between bg-slate-800/50 rounded p-2">
                        <span className="text-purple-300">Atom Count:</span>
                        <span className="font-bold">{selectedElements.length}</span>
                      </div>
                    </div>
                  </div>

                  {/* Controls */}
                  <div>
                    <h3 className="text-xl font-bold text-pink-300 mb-3">Playback Controls</h3>
                    
                    <div className="mb-4">
                      <label className="text-sm text-gray-400 block mb-2">
                        Cycle Speed: {cycleSpeed.toFixed(1)}x
                      </label>
                      <input
                        type="range"
                        min="0.5"
                        max="4"
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
                    <div className="max-h-32 overflow-y-auto space-y-2 mt-4">
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
              </div>
            )}
          </div>

          {/* Famous Molecules */}
          <div className="space-y-6">
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

            {/* Element Palette */}
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
    </div>
  );
};

export default App;
