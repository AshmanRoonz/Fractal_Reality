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

  // Comprehensive molecules database organized by category
  const famousMolecules = {
    'Breathable Air': [
      {
        name: 'Air (Typical Mix)',
        formula: '78% N₂ + 21% O₂ + 1% Ar',
        elements: ['N','N','N','N','N','N','N','N','N','N','N','N','N','N','N','N','O','O','O','O','O','O','O','O','O','O','Ar'],
        bondType: 'Mixed atmosphere',
        vibrationFreq: 5.5,
        description: 'What we breathe! Mostly nitrogen with life-giving oxygen',
        tempo: 'Vivace'
      },
    ],
    'Simple Diatomics': [
      { 
        name: 'Hydrogen Gas', 
        formula: 'H₂', 
        elements: ['H', 'H'],
        bondType: 'Single Bond',
        vibrationFreq: 12.5,
        description: '2e⁻ 2p⁺ 0n⁰ - Very fast! ~4300 cm⁻¹',
        tempo: 'Prestissimo'
      },
      { 
        name: 'Oxygen Gas', 
        formula: 'O₂', 
        elements: ['O', 'O'],
        bondType: 'Double Bond',
        vibrationFreq: 4.7,
        description: '16e⁻ 16p⁺ 16n⁰ - Strong O=O stretch ~1580 cm⁻¹',
        tempo: 'Vivace'
      },
      { 
        name: 'Nitrogen Gas', 
        formula: 'N₂', 
        elements: ['N', 'N'],
        bondType: 'Triple Bond',
        vibrationFreq: 7.0,
        description: '14e⁻ 14p⁺ 14n⁰ - Very strong N≡N ~2330 cm⁻¹',
        tempo: 'Presto'
      },
      { 
        name: 'Fluorine Gas', 
        formula: 'F₂', 
        elements: ['F', 'F'],
        bondType: 'Single Bond',
        vibrationFreq: 2.7,
        description: '18e⁻ 18p⁺ 20n⁰ - Weak F-F bond ~890 cm⁻¹',
        tempo: 'Andante'
      },
      { 
        name: 'Chlorine Gas', 
        formula: 'Cl₂', 
        elements: ['Cl', 'Cl'],
        bondType: 'Single Bond',
        vibrationFreq: 1.7,
        description: '34e⁻ 34p⁺ 36n⁰ - Heavy Cl-Cl ~560 cm⁻¹',
        tempo: 'Largo'
      },
    ],
    'Water & Oxides': [
      { 
        name: 'Water', 
        formula: 'H₂O', 
        elements: ['H', 'H', 'O'],
        bondType: 'Bent',
        vibrationFreq: 3.7,
        description: '10e⁻ 10p⁺ 8n⁰ - Bending vibration ~1595 cm⁻¹',
        tempo: 'Allegro'
      },
      { 
        name: 'Hydrogen Peroxide', 
        formula: 'H₂O₂', 
        elements: ['H', 'H', 'O', 'O'],
        bondType: 'Non-planar',
        vibrationFreq: 2.8,
        description: '18e⁻ 18p⁺ 16n⁰ - O-O peroxide bond',
        tempo: 'Moderato'
      },
      { 
        name: 'Carbon Dioxide', 
        formula: 'CO₂', 
        elements: ['O', 'C', 'O'],
        bondType: 'Linear',
        vibrationFreq: 4.0,
        description: '22e⁻ 22p⁺ 22n⁰ - Asymmetric stretch ~2349 cm⁻¹',
        tempo: 'Allegro'
      },
      { 
        name: 'Carbon Monoxide', 
        formula: 'CO', 
        elements: ['C', 'O'],
        bondType: 'Triple Bond',
        vibrationFreq: 6.4,
        description: '14e⁻ 14p⁺ 14n⁰ - Strong C≡O ~2143 cm⁻¹',
        tempo: 'Vivace'
      },
      { 
        name: 'Nitric Oxide', 
        formula: 'NO', 
        elements: ['N', 'O'],
        bondType: 'Double Bond',
        vibrationFreq: 5.6,
        description: '15e⁻ 15p⁺ 15n⁰ - Free radical ~1876 cm⁻¹',
        tempo: 'Vivace'
      },
      { 
        name: 'Nitrogen Dioxide', 
        formula: 'NO₂', 
        elements: ['N', 'O', 'O'],
        bondType: 'Bent',
        vibrationFreq: 4.2,
        description: '23e⁻ 23p⁺ 23n⁰ - Brown gas pollutant',
        tempo: 'Allegro'
      },
      { 
        name: 'Sulfur Dioxide', 
        formula: 'SO₂', 
        elements: ['S', 'O', 'O'],
        bondType: 'Bent',
        vibrationFreq: 3.3,
        description: '32e⁻ 32p⁺ 32n⁰ - Acid rain precursor',
        tempo: 'Moderato'
      },
    ],
    'Simple Hydrides': [
      { 
        name: 'Ammonia', 
        formula: 'NH₃', 
        elements: ['N', 'H', 'H', 'H'],
        bondType: 'Pyramidal',
        vibrationFreq: 3.2,
        description: '10e⁻ 10p⁺ 7n⁰ - Umbrella mode ~950 cm⁻¹',
        tempo: 'Moderato'
      },
      { 
        name: 'Methane', 
        formula: 'CH₄', 
        elements: ['C', 'H', 'H', 'H', 'H'],
        bondType: 'Tetrahedral',
        vibrationFreq: 2.9,
        description: '10e⁻ 10p⁺ 6n⁰ - C-H stretch ~3000 cm⁻¹',
        tempo: 'Andante'
      },
      { 
        name: 'Hydrogen Sulfide', 
        formula: 'H₂S', 
        elements: ['H', 'H', 'S'],
        bondType: 'Bent',
        vibrationFreq: 2.4,
        description: '18e⁻ 18p⁺ 16n⁰ - Rotten egg smell',
        tempo: 'Andante'
      },
      { 
        name: 'Hydrogen Chloride', 
        formula: 'HCl', 
        elements: ['H', 'Cl'],
        bondType: 'Diatomic',
        vibrationFreq: 8.7,
        description: '18e⁻ 18p⁺ 18n⁰ - Strong acid ~2886 cm⁻¹',
        tempo: 'Presto'
      },
      { 
        name: 'Hydrogen Fluoride', 
        formula: 'HF', 
        elements: ['H', 'F'],
        bondType: 'Diatomic',
        vibrationFreq: 12.1,
        description: '10e⁻ 10p⁺ 10n⁰ - Very strong bond ~4138 cm⁻¹',
        tempo: 'Prestissimo'
      },
    ],
    'Organic Molecules': [
      { 
        name: 'Ethane', 
        formula: 'C₂H₆', 
        elements: ['C', 'C', 'H', 'H', 'H', 'H', 'H', 'H'],
        bondType: 'Single C-C',
        vibrationFreq: 2.5,
        description: '18e⁻ 18p⁺ 12n⁰ - Simplest alkane',
        tempo: 'Andante'
      },
      { 
        name: 'Ethylene', 
        formula: 'C₂H₄', 
        elements: ['C', 'C', 'H', 'H', 'H', 'H'],
        bondType: 'Double C=C',
        vibrationFreq: 4.8,
        description: '16e⁻ 16p⁺ 12n⁰ - Plant hormone ~1623 cm⁻¹',
        tempo: 'Vivace'
      },
      { 
        name: 'Acetylene', 
        formula: 'C₂H₂', 
        elements: ['C', 'C', 'H', 'H'],
        bondType: 'Triple C≡C',
        vibrationFreq: 6.1,
        description: '14e⁻ 14p⁺ 12n⁰ - Welding fuel ~1974 cm⁻¹',
        tempo: 'Vivace'
      },
      { 
        name: 'Formaldehyde', 
        formula: 'CH₂O', 
        elements: ['C', 'H', 'H', 'O'],
        bondType: 'Planar',
        vibrationFreq: 4.3,
        description: '16e⁻ 16p⁺ 14n⁰ - Preservative',
        tempo: 'Allegro'
      },
      { 
        name: 'Methanol', 
        formula: 'CH₃OH', 
        elements: ['C', 'H', 'H', 'H', 'O', 'H'],
        bondType: 'Tetrahedral',
        vibrationFreq: 2.7,
        description: '18e⁻ 18p⁺ 14n⁰ - Wood alcohol',
        tempo: 'Andante'
      },
      { 
        name: 'Formic Acid', 
        formula: 'HCOOH', 
        elements: ['H', 'C', 'O', 'O', 'H'],
        bondType: 'Carboxylic',
        vibrationFreq: 3.2,
        description: '24e⁻ 24p⁺ 22n⁰ - Ant venom',
        tempo: 'Moderato'
      },
      { 
        name: 'Acetic Acid', 
        formula: 'CH₃COOH', 
        elements: ['C', 'H', 'H', 'H', 'C', 'O', 'O', 'H'],
        bondType: 'Carboxylic',
        vibrationFreq: 2.3,
        description: '32e⁻ 32p⁺ 28n⁰ - Vinegar',
        tempo: 'Andante'
      },
    ],
    'Salts & Ionic': [
      { 
        name: 'Sodium Chloride', 
        formula: 'NaCl', 
        elements: ['Na', 'Cl'],
        bondType: 'Ionic',
        vibrationFreq: 1.1,
        description: '28e⁻ 28p⁺ 30n⁰ - Table salt',
        tempo: 'Largo'
      },
      { 
        name: 'Magnesium Oxide', 
        formula: 'MgO', 
        elements: ['Mg', 'O'],
        bondType: 'Ionic',
        vibrationFreq: 2.0,
        description: '20e⁻ 20p⁺ 20n⁰ - Refractory material',
        tempo: 'Lento'
      },
      { 
        name: 'Calcium Carbonate', 
        formula: 'CaCO₃', 
        elements: ['Ca', 'C', 'O', 'O', 'O'],
        bondType: 'Ionic/Covalent',
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
      { 
        name: 'Acetone', 
        formula: 'C₃H₆O', 
        elements: ['C','H','H','H','C','O','C','H','H','H'],
        bondType: 'Carbonyl',
        vibrationFreq: 2.1,
        description: '32e⁻ 32p⁺ 26n⁰ - Solvent',
        tempo: 'Lento'
      },
      { 
        name: 'Glycine', 
        formula: 'C₂H₅NO₂', 
        elements: ['C','C','H','H','H','H','H','N','O','O'],
        bondType: 'Amino acid',
        vibrationFreq: 2.0,
        description: '34e⁻ 34p⁺ 29n⁰ - Simplest amino acid',
        tempo: 'Lento'
      },
    ],
    'Atmospheric': [
      { 
        name: 'Ozone', 
        formula: 'O₃', 
        elements: ['O', 'O', 'O'],
        bondType: 'Bent',
        vibrationFreq: 3.3,
        description: '24e⁻ 24p⁺ 24n⁰ - UV protection layer',
        tempo: 'Moderato'
      },
      { 
        name: 'Nitrous Oxide', 
        formula: 'N₂O', 
        elements: ['N', 'N', 'O'],
        bondType: 'Linear',
        vibrationFreq: 4.5,
        description: '22e⁻ 22p⁺ 23n⁰ - Laughing gas',
        tempo: 'Allegro'
      },
    ],
    'Industrial': [
      { 
        name: 'Sulfuric Acid', 
        formula: 'H₂SO₄', 
        elements: ['H', 'H', 'S', 'O', 'O', 'O', 'O'],
        bondType: 'Tetrahedral',
        vibrationFreq: 2.5,
        description: '50e⁻ 50p⁺ 48n⁰ - Strong acid',
        tempo: 'Andante'
      },
      { 
        name: 'Nitric Acid', 
        formula: 'HNO₃', 
        elements: ['H', 'N', 'O', 'O', 'O'],
        bondType: 'Planar',
        vibrationFreq: 3.0,
        description: '32e⁻ 32p⁺ 31n⁰ - Oxidizing acid',
        tempo: 'Moderato'
      },
      { 
        name: 'Benzene', 
        formula: 'C₆H₆', 
        elements: ['C','C','C','C','C','C','H','H','H','H','H','H'],
        bondType: 'Aromatic',
        vibrationFreq: 2.8,
        description: '42e⁻ 42p⁺ 36n⁰ - Aromatic hydrocarbon',
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
              Molecular Song Composer
            </h1>
            <Sparkles className="w-10 h-10 text-pink-400" />
          </div>
          <p className="text-lg text-cyan-200">
            Molecules are SONGS! Atoms cycle through vibrations.
          </p>
          <p className="text-sm text-purple-300 mt-1">
            Fractal Reality Framework • Ashman Roonz • github.com/AshmanRoonz/Fractal_Reality
          </p>
        </div>

        {/* Info Banner */}
        {showInfo && (
          <div className="mb-6 bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-xl p-4 border-2 border-pink-500/50 relative">
            <button
              onClick={() => setShowInfo(false)}
              className="absolute top-2 right-2 text-gray-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
            <div className="flex items-start gap-3">
              <Info className="w-6 h-6 text-cyan-400 flex-shrink-0 mt-1" />
              <div className="text-sm">
                <p className="text-cyan-200 font-bold mb-2">🎵 Molecules as Songs:</p>
                <ul className="space-y-1 text-gray-300">
                  <li>• Each <strong>atom</strong> = a 3-part chord (electrons + protons + neutrons)</li>
                  <li>• The <strong>molecule</strong> = a cycling song through all atoms</li>
                  <li>• <strong>Cycle speed</strong> = vibrational frequency (bond oscillations)</li>
                  <li>• This is what <strong>IR spectroscopy</strong> actually measures!</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Controls */}
        <div className="mb-6 space-y-3">
          <div className="flex flex-wrap gap-3 justify-center">
            <button
              onClick={() => {
                if (!soundEnabled) initAudio();
                setSoundEnabled(!soundEnabled);
              }}
              className={`px-4 py-2 rounded-lg font-bold transition-all ${
                soundEnabled ? 'bg-green-500 text-black' : 'bg-slate-700 text-gray-300'
              }`}
            >
              {soundEnabled ? '🔊 Sound ON' : '🔇 Enable Sound'}
            </button>
            {soundEnabled && selectedElements.length > 0 && (
              <>
                {!isPlaying ? (
                  <button
                    onClick={playMoleculeSong}
                    className="px-4 py-2 rounded-lg font-bold bg-purple-500 text-white hover:bg-purple-600 transition-all flex items-center gap-2"
                  >
                    <Play className="w-5 h-5" />
                    Play Molecular Song
                  </button>
                ) : (
                  <button
                    onClick={stopPlaying}
                    className="px-4 py-2 rounded-lg font-bold bg-red-500 text-white hover:bg-red-600 transition-all flex items-center gap-2"
                  >
                    <X className="w-5 h-5" />
                    Stop Playing
                  </button>
                )}
              </>
            )}
            {selectedElements.length > 0 && (
              <button
                onClick={clearMolecule}
                className="px-4 py-2 rounded-lg font-bold bg-slate-600 text-white hover:bg-slate-700 transition-all flex items-center gap-2"
              >
                <Trash2 className="w-5 h-5" />
                Clear
              </button>
            )}
          </div>

          {/* Vibration Speed Control */}
          {selectedElements.length > 0 && (
            <div className="bg-black/30 rounded-lg p-4 border border-cyan-500/30 max-w-2xl mx-auto">
              <div className="flex items-center justify-between mb-2">
                <label className="text-cyan-300 font-bold">Vibration Frequency:</label>
                <span className="text-pink-400 text-xl font-bold">{cycleSpeed.toFixed(1)} Hz</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="60"
                step="0.5"
                value={cycleSpeed}
                onChange={(e) => setCycleSpeed(parseFloat(e.target.value))}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-400 mt-1">
                <span>0.5 Hz (Grave)</span>
                <span>15 Hz (Allegro)</span>
                <span>30 Hz (Vivace)</span>
                <span>60 Hz (Presto)</span>
              </div>
              <div className="text-center text-sm text-yellow-300 mt-2">
                {cycleSpeed < 2 ? '🐌 Very slow vibration' :
                 cycleSpeed < 10 ? '🎵 Moderate vibration' :
                 cycleSpeed < 30 ? '⚡ Fast vibration' :
                 cycleSpeed < 50 ? '🚀 Very fast vibration' :
                 '⭐ Ultra-fast vibration!'}
              </div>
            </div>
          )}
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          
          {/* Left: Molecule Builder */}
          <div className="space-y-6">
            
            {/* Current Molecule Display */}
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
                  {/* Wave Visualization */}
                  <div className="mb-6 bg-slate-900/70 rounded-lg p-4 h-48 relative overflow-hidden border border-cyan-500/30">
                    <svg width="100%" height="100%" className="absolute inset-0">
                      {selectedElements.map((el, idx) => {
                        const yBase = 24 + (idx * (160 / Math.max(selectedElements.length, 1)));
                        const atomPhase = idx / selectedElements.length;
                        const phase = (wavePhase - atomPhase + 1) % 1;
                        
                        return (
                          <g key={el.id}>
                            <text x="10" y={yBase} fill={el.color} fontSize="14" fontWeight="bold">
                              {el.symbol}
                            </text>
                            
                            <path
                              d={Array.from({ length: 100 }, (_, i) => {
                                const x = 50 + (i / 100) * (typeof window !== 'undefined' ? window.innerWidth * 0.4 : 400);
                                const wavePhaseAtX = (phase + i / 20) * Math.PI * 2;
                                const amplitude = 15 * Math.cos(phase * Math.PI * 2);
                                const y = yBase + Math.sin(wavePhaseAtX) * Math.abs(amplitude);
                                return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
                              }).join(' ')}
                              stroke={el.color}
                              strokeWidth="2"
                              fill="none"
                              opacity="0.8"
                            />
                            
                            <circle
                              cx={50 + (typeof window !== 'undefined' ? window.innerWidth * 0.2 : 200)}
                              cy={yBase}
                              r={8 * (1 - Math.abs(phase - 0.5) * 2)}
                              fill={el.color}
                              opacity={0.6 + 0.4 * (1 - Math.abs(phase - 0.5) * 2)}
                            />
                          </g>
                        );
                      })}
                    </svg>
                    <div className="absolute bottom-2 right-2 text-xs text-gray-400">
                      {cycleSpeed.toFixed(1)} Hz • Phase: {(wavePhase * 100).toFixed(0)}%
                    </div>
                  </div>

                  {/* Atom sequence display */}
                  <div className="flex flex-wrap gap-2 mb-6 min-h-[80px] bg-slate-900/50 rounded-lg p-4">
                    {selectedElements.map((el, idx) => (
                      <div
                        key={el.id}
                        onClick={() => removeElement(el.id)}
                        className="relative group cursor-pointer"
                        title={`${el.name}: ${el.e}e⁻ ${el.z}p⁺ ${el.n}n⁰`}
                      >
                        <div
                          className="w-14 h-14 rounded-full flex flex-col items-center justify-center border-4 transition-all hover:scale-110"
                          style={{ 
                            backgroundColor: el.color + '40',
                            borderColor: el.color,
                            opacity: isPlaying && Math.abs(wavePhase - (idx / selectedElements.length)) < 0.15 ? 1 : 0.5
                          }}
                        >
                          <div className="text-lg font-bold">{el.symbol}</div>
                          <div className="text-[7px] text-gray-300">{idx + 1}</div>
                        </div>
                        <div className="absolute inset-0 bg-red-500/80 rounded-full opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-xs font-bold">
                          ×
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Analysis */}
                  {analyzeMolecule && (
                    <div className="space-y-3">
                      <div className="bg-purple-900/30 rounded-lg p-4">
                        <div className="text-3xl font-bold text-center mb-3" style={{ fontFamily: 'monospace' }}>
                          {analyzeMolecule.formula}
                        </div>
                        
                        <div className="grid grid-cols-3 gap-3 mb-4">
                          <div className="text-center bg-cyan-900/30 rounded p-3">
                            <div className="text-xs text-gray-400 mb-1">Electrons</div>
                            <div className="text-2xl font-bold text-cyan-300">{analyzeMolecule.totalElectrons}</div>
                          </div>
                          <div className="text-center bg-red-900/30 rounded p-3">
                            <div className="text-xs text-gray-400 mb-1">Protons</div>
                            <div className="text-2xl font-bold text-red-300">{analyzeMolecule.totalProtons}</div>
                          </div>
                          <div className="text-center bg-yellow-900/30 rounded p-3">
                            <div className="text-xs text-gray-400 mb-1">Neutrons</div>
                            <div className="text-2xl font-bold text-yellow-300">{analyzeMolecule.totalNeutrons}</div>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-3 text-sm">
                          <div>
                            <span className="text-gray-400">Notes in Song:</span>
                            <span className="text-cyan-300 ml-2 font-bold">{analyzeMolecule.elementCount}</span>
                          </div>
                          <div>
                            <span className="text-gray-400">Total Mass:</span>
                            <span className="text-pink-300 ml-2 font-bold">{analyzeMolecule.totalMass} u</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Famous Molecules */}
            <div className="bg-black/30 rounded-xl p-6 border border-purple-500/30">
              <h3 className="text-xl font-bold text-purple-300 mb-4">Molecular Library</h3>
              <div className="space-y-4 max-h-[500px] overflow-y-auto">
                {Object.entries(famousMolecules).map(([category, molecules]) => (
                  <div key={category}>
                    <h4 className="text-lg font-bold text-cyan-400 mb-2 sticky top-0 bg-slate-900/90 py-1">
                      {category}
                    </h4>
                    <div className="space-y-2">
                      {molecules.map((mol, i) => (
                        <button
                          key={i}
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
                className="w-full bg-slate-800 text-white border-2 border-purple-500/50 rounded-lg p-3 text-lg font-bold cursor-pointer hover:border-purple-500 transition-all"
                defaultValue=""
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
