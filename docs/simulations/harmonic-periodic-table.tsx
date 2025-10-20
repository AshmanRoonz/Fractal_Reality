import React, { useState, useMemo } from 'react';
import { Waves, Music, Zap, Info, X, Atom, Layers } from 'lucide-react';

const HarmonicPeriodicTable = () => {
  const [selectedElement, setSelectedElement] = useState(null);
  const [compareElement, setCompareElement] = useState(null);
  const [showOctaves, setShowOctaves] = useState(true);
  const [showElectronShells, setShowElectronShells] = useState(false);
  const [showNeutronHarmonics, setShowNeutronHarmonics] = useState(false);
  const [showMusicalRatios, setShowMusicalRatios] = useState(true);
  const [viewMode, setViewMode] = useState('table'); // 'table', 'shells', 'nucleus'
  const [audioContext, setAudioContext] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(false);

  // Initialize Web Audio API
  const initAudio = () => {
    if (!audioContext) {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      setAudioContext(ctx);
      setSoundEnabled(true);
    }
  };

  // Play element tone
  const playElementTone = (element, duration = 0.5) => {
    if (!audioContext || !soundEnabled) return;

    // Base frequency: A4 = 440 Hz, C4 = 261.63 Hz
    const baseFreq = 261.63; // C4
    const frequency = baseFreq * Math.pow(2, element.octave);

    // Create oscillator for main tone
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.type = element.noble ? 'sine' : 
                       element.transition ? 'triangle' : 'sine';
    oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime);

    // Envelope
    gainNode.gain.setValueAtTime(0, audioContext.currentTime);
    gainNode.gain.linearRampToValueAtTime(0.3, audioContext.currentTime + 0.01);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);

    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + duration);

    // Add nuclear harmonic overtone if element has neutrons
    if (element.n > 0) {
      const nuclear = calculateNuclearHarmonic(element);
      if (nuclear?.isPerfectMusical) {
        const npRatio = element.z / element.n;
        const harmonicFreq = frequency * (1 + npRatio) / 2; // Blend frequency

        const harmonic = audioContext.createOscillator();
        const harmonicGain = audioContext.createGain();
        
        harmonic.connect(harmonicGain);
        harmonicGain.connect(audioContext.destination);

        harmonic.type = 'sine';
        harmonic.frequency.setValueAtTime(harmonicFreq, audioContext.currentTime);

        harmonicGain.gain.setValueAtTime(0, audioContext.currentTime);
        harmonicGain.gain.linearRampToValueAtTime(0.15, audioContext.currentTime + 0.01);
        harmonicGain.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);

        harmonic.start(audioContext.currentTime);
        harmonic.stop(audioContext.currentTime + duration);
      }
    }
  };

  // Play chord for comparison
  const playChord = (el1, el2) => {
    if (!audioContext || !soundEnabled) return;

    const baseFreq = 261.63;
    const freq1 = baseFreq * Math.pow(2, el1.octave);
    const freq2 = baseFreq * Math.pow(2, el2.octave);

    [freq1, freq2].forEach((freq, i) => {
      const osc = audioContext.createOscillator();
      const gain = audioContext.createGain();
      
      osc.connect(gain);
      gain.connect(audioContext.destination);

      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, audioContext.currentTime);

      gain.gain.setValueAtTime(0, audioContext.currentTime);
      gain.gain.linearRampToValueAtTime(0.2, audioContext.currentTime + 0.01);
      gain.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 1.5);

      osc.start(audioContext.currentTime);
      osc.stop(audioContext.currentTime + 1.5);
    });
  };

  // Play arpeggio through octave elements
  const playOctaveSequence = () => {
    if (!audioContext || !soundEnabled || isPlaying) return;
    
    setIsPlaying(true);
    const octaveElements = elements.filter(e => Math.log2(e.z) % 1 === 0).slice(0, 7);
    
    octaveElements.forEach((el, i) => {
      setTimeout(() => {
        playElementTone(el, 0.4);
        if (i === octaveElements.length - 1) {
          setTimeout(() => setIsPlaying(false), 500);
        }
      }, i * 400);
    });
  };

  // Complete periodic table data with FULL configurations
  const elements = [
    // Period 1
    { symbol: 'H', name: 'Hydrogen', z: 1, n: 0, period: 1, group: 1, octave: 0, note: 'C₀', interval: 'Root', harmonic: 1, color: '#60a5fa', config: '1s¹', shells: [1], shellHarmonic: '1:0', np_ratio: 'Pure proton', mass: 1 },
    { symbol: 'He', name: 'Helium', z: 2, n: 2, period: 1, group: 18, octave: 1, note: 'C₁', interval: 'Octave', harmonic: 2, color: '#a78bfa', noble: true, config: '1s²', shells: [2], shellHarmonic: '2:2 (1:1)', np_ratio: '1:1 Perfect', mass: 4 },
    
    // Period 2
    { symbol: 'Li', name: 'Lithium', z: 3, n: 4, period: 2, group: 1, octave: 1.58, note: 'G₁', interval: 'Fifth + Octave', harmonic: 3, color: '#fbbf24', config: '1s² 2s¹', shells: [2,1], shellHarmonic: '3:4', np_ratio: '3:4 (4th)', mass: 7 },
    { symbol: 'Be', name: 'Beryllium', z: 4, n: 5, period: 2, group: 2, octave: 2, note: 'C₂', interval: '2nd Octave', harmonic: 4, color: '#60a5fa', config: '1s² 2s²', shells: [2,2], shellHarmonic: '4:5', np_ratio: '4:5 (maj 3rd)', mass: 9 },
    { symbol: 'B', name: 'Boron', z: 5, n: 6, period: 2, group: 13, octave: 2.32, note: 'E₂', interval: 'Major 3rd + 2oct', harmonic: 5, color: '#34d399', config: '1s² 2s² 2p¹', shells: [2,3], shellHarmonic: '5:6', np_ratio: '5:6 (min 3rd)', mass: 11 },
    { symbol: 'C', name: 'Carbon', z: 6, n: 6, period: 2, group: 14, octave: 2.58, note: 'G₂', interval: 'Fifth + 2oct', harmonic: 6, color: '#8b5cf6', config: '1s² 2s² 2p²', shells: [2,4], shellHarmonic: '6:6 (1:1)', np_ratio: '1:1 Perfect', mass: 12 },
    { symbol: 'N', name: 'Nitrogen', z: 7, n: 7, period: 2, group: 15, octave: 2.81, note: 'B♭₂', interval: 'Min 7th + 2oct', harmonic: 7, color: '#22d3ee', config: '1s² 2s² 2p³', shells: [2,5], shellHarmonic: '7:7 (1:1)', np_ratio: '1:1 Perfect', mass: 14 },
    { symbol: 'O', name: 'Oxygen', z: 8, n: 8, period: 2, group: 16, octave: 3, note: 'C₃', interval: '3rd Octave', harmonic: 8, color: '#ef4444', config: '1s² 2s² 2p⁴', shells: [2,6], shellHarmonic: '8:8 (1:1)', np_ratio: '1:1 Perfect', mass: 16 },
    { symbol: 'F', name: 'Fluorine', z: 9, n: 10, period: 2, group: 17, octave: 3.17, note: 'D₃', interval: 'Major 2nd + 3oct', harmonic: 9, color: '#f59e0b', config: '1s² 2s² 2p⁵', shells: [2,7], shellHarmonic: '9:10', np_ratio: '9:10 (maj 2nd)', mass: 19 },
    { symbol: 'Ne', name: 'Neon', z: 10, n: 10, period: 2, group: 18, octave: 3.32, note: 'E₃', interval: 'Major 3rd + 3oct', harmonic: 10, color: '#a78bfa', noble: true, config: '1s² 2s² 2p⁶', shells: [2,8], shellHarmonic: '10:10 (1:1)', np_ratio: '1:1 Perfect', mass: 20 },
    
    // Period 3
    { symbol: 'Na', name: 'Sodium', z: 11, n: 12, period: 3, group: 1, octave: 3.46, note: 'F₃', interval: 'Perfect 4th + 3oct', harmonic: 11, color: '#fbbf24', config: '[Ne] 3s¹', shells: [2,8,1], shellHarmonic: '11:12', np_ratio: '11:12 (semitone)', mass: 23 },
    { symbol: 'Mg', name: 'Magnesium', z: 12, n: 12, period: 3, group: 2, octave: 3.58, note: 'G₃', interval: 'Perfect 5th + 3oct', harmonic: 12, color: '#10b981', config: '[Ne] 3s²', shells: [2,8,2], shellHarmonic: '12:12 (1:1)', np_ratio: '1:1 Perfect', mass: 24 },
    { symbol: 'Al', name: 'Aluminum', z: 13, n: 14, period: 3, group: 13, octave: 3.70, note: 'A♭₃', interval: 'Minor 6th + 3oct', harmonic: 13, color: '#94a3b8', config: '[Ne] 3s² 3p¹', shells: [2,8,3], shellHarmonic: '13:14', np_ratio: '13:14', mass: 27 },
    { symbol: 'Si', name: 'Silicon', z: 14, n: 14, period: 3, group: 14, octave: 3.81, note: 'B♭₃', interval: 'Minor 7th + 3oct', harmonic: 14, color: '#64748b', config: '[Ne] 3s² 3p²', shells: [2,8,4], shellHarmonic: '14:14 (1:1)', np_ratio: '1:1 Perfect', mass: 28 },
    { symbol: 'P', name: 'Phosphorus', z: 15, n: 16, period: 3, group: 15, octave: 3.91, note: 'B₃', interval: 'Major 7th + 3oct', harmonic: 15, color: '#f97316', config: '[Ne] 3s² 3p³', shells: [2,8,5], shellHarmonic: '15:16', np_ratio: '15:16 (semitone)', mass: 31 },
    { symbol: 'S', name: 'Sulfur', z: 16, n: 16, period: 3, group: 16, octave: 4, note: 'C₄', interval: '4th Octave', harmonic: 16, color: '#eab308', config: '[Ne] 3s² 3p⁴', shells: [2,8,6], shellHarmonic: '16:16 (1:1)', np_ratio: '1:1 Perfect', mass: 32 },
    { symbol: 'Cl', name: 'Chlorine', z: 17, n: 18, period: 3, group: 17, octave: 4.09, note: 'C♯₄', interval: 'Minor 2nd + 4oct', harmonic: 17, color: '#84cc16', config: '[Ne] 3s² 3p⁵', shells: [2,8,7], shellHarmonic: '17:18', np_ratio: '17:18 (semitone)', mass: 35 },
    { symbol: 'Ar', name: 'Argon', z: 18, n: 22, period: 3, group: 18, octave: 4.17, note: 'D₄', interval: 'Major 2nd + 4oct', harmonic: 18, color: '#a78bfa', noble: true, config: '[Ne] 3s² 3p⁶', shells: [2,8,8], shellHarmonic: '18:22', np_ratio: '9:11', mass: 40 },
    
    // Period 4 (complete)
    { symbol: 'K', name: 'Potassium', z: 19, n: 20, period: 4, group: 1, octave: 4.25, note: 'E♭₄', harmonic: 19, color: '#fbbf24', config: '[Ar] 4s¹', shells: [2,8,8,1], shellHarmonic: '19:20', mass: 39 },
    { symbol: 'Ca', name: 'Calcium', z: 20, n: 20, period: 4, group: 2, octave: 4.32, note: 'E₄', harmonic: 20, color: '#10b981', config: '[Ar] 4s²', shells: [2,8,8,2], shellHarmonic: '20:20 (1:1)', np_ratio: '1:1 Perfect', mass: 40 },
    { symbol: 'Sc', name: 'Scandium', z: 21, n: 24, period: 4, group: 3, octave: 4.39, note: 'F₄', harmonic: 21, color: '#ec4899', transition: true, config: '[Ar] 3d¹ 4s²', shells: [2,8,9,2], shellHarmonic: '21:24', np_ratio: '7:8', mass: 45 },
    { symbol: 'Ti', name: 'Titanium', z: 22, n: 26, period: 4, group: 4, octave: 4.46, note: 'F♯₄', harmonic: 22, color: '#ec4899', transition: true, config: '[Ar] 3d² 4s²', shells: [2,8,10,2], shellHarmonic: '22:26', np_ratio: '11:13', mass: 48 },
    { symbol: 'V', name: 'Vanadium', z: 23, n: 28, period: 4, group: 5, octave: 4.52, note: 'G₄', harmonic: 23, color: '#ec4899', transition: true, config: '[Ar] 3d³ 4s²', shells: [2,8,11,2], shellHarmonic: '23:28', mass: 51 },
    { symbol: 'Cr', name: 'Chromium', z: 24, n: 28, period: 4, group: 6, octave: 4.58, note: 'A♭₄', harmonic: 24, color: '#ec4899', transition: true, config: '[Ar] 3d⁵ 4s¹', shells: [2,8,13,1], shellHarmonic: '24:28', np_ratio: '6:7', mass: 52 },
    { symbol: 'Mn', name: 'Manganese', z: 25, n: 30, period: 4, group: 7, octave: 4.64, note: 'A₄', harmonic: 25, color: '#ec4899', transition: true, config: '[Ar] 3d⁵ 4s²', shells: [2,8,13,2], shellHarmonic: '25:30', np_ratio: '5:6', mass: 55 },
    { symbol: 'Fe', name: 'Iron', z: 26, n: 30, period: 4, group: 8, octave: 4.70, note: 'B♭₄', harmonic: 26, color: '#ec4899', transition: true, config: '[Ar] 3d⁶ 4s²', shells: [2,8,14,2], shellHarmonic: '26:30', np_ratio: '13:15', mass: 56 },
    { symbol: 'Co', name: 'Cobalt', z: 27, n: 32, period: 4, group: 9, octave: 4.75, note: 'B₄', harmonic: 27, color: '#ec4899', transition: true, config: '[Ar] 3d⁷ 4s²', shells: [2,8,15,2], shellHarmonic: '27:32', mass: 59 },
    { symbol: 'Ni', name: 'Nickel', z: 28, n: 31, period: 4, group: 10, octave: 4.81, note: 'C₅', harmonic: 28, color: '#ec4899', transition: true, config: '[Ar] 3d⁸ 4s²', shells: [2,8,16,2], shellHarmonic: '28:31', mass: 59 },
    { symbol: 'Cu', name: 'Copper', z: 29, n: 34, period: 4, group: 11, octave: 4.86, note: 'C♯₅', harmonic: 29, color: '#ec4899', transition: true, config: '[Ar] 3d¹⁰ 4s¹', shells: [2,8,18,1], shellHarmonic: '29:34', mass: 63 },
    { symbol: 'Zn', name: 'Zinc', z: 30, n: 35, period: 4, group: 12, octave: 4.91, note: 'D₅', harmonic: 30, color: '#ec4899', transition: true, config: '[Ar] 3d¹⁰ 4s²', shells: [2,8,18,2], shellHarmonic: '30:35', np_ratio: '6:7 (submin 3rd)', mass: 65 },
    { symbol: 'Ga', name: 'Gallium', z: 31, n: 39, period: 4, group: 13, octave: 4.95, note: 'E♭₅', harmonic: 31, color: '#94a3b8', config: '[Ar] 3d¹⁰ 4s² 4p¹', shells: [2,8,18,3], shellHarmonic: '31:39', mass: 70 },
    { symbol: 'Ge', name: 'Germanium', z: 32, n: 41, period: 4, group: 14, octave: 5, note: 'E₅', harmonic: 32, color: '#64748b', config: '[Ar] 3d¹⁰ 4s² 4p²', shells: [2,8,18,4], shellHarmonic: '32:41', mass: 73 },
    { symbol: 'As', name: 'Arsenic', z: 33, n: 42, period: 4, group: 15, octave: 5.04, note: 'F₅', harmonic: 33, color: '#f97316', config: '[Ar] 3d¹⁰ 4s² 4p³', shells: [2,8,18,5], shellHarmonic: '33:42', mass: 75 },
    { symbol: 'Se', name: 'Selenium', z: 34, n: 45, period: 4, group: 16, octave: 5.09, note: 'F♯₅', harmonic: 34, color: '#eab308', config: '[Ar] 3d¹⁰ 4s² 4p⁴', shells: [2,8,18,6], shellHarmonic: '34:45', mass: 79 },
    { symbol: 'Br', name: 'Bromine', z: 35, n: 45, period: 4, group: 17, octave: 5.13, note: 'G₅', harmonic: 35, color: '#84cc16', config: '[Ar] 3d¹⁰ 4s² 4p⁵', shells: [2,8,18,7], shellHarmonic: '35:45', np_ratio: '7:9', mass: 80 },
    { symbol: 'Kr', name: 'Krypton', z: 36, n: 48, period: 4, group: 18, octave: 5.17, note: 'A♭₅', harmonic: 36, color: '#a78bfa', noble: true, config: '[Ar] 3d¹⁰ 4s² 4p⁶', shells: [2,8,18,8], shellHarmonic: '36:48', np_ratio: '3:4 (4th)', mass: 84 },
    
    // Period 5 (key elements)
    { symbol: 'Ag', name: 'Silver', z: 47, n: 60, period: 5, group: 11, octave: 5.55, note: 'G₆', harmonic: 47, color: '#ec4899', transition: true, config: '[Kr] 4d¹⁰ 5s¹', shells: [2,8,18,18,1], shellHarmonic: '47:60', mass: 107 },
    { symbol: 'I', name: 'Iodine', z: 53, n: 74, period: 5, group: 17, octave: 5.73, note: 'B₆', harmonic: 53, color: '#84cc16', config: '[Kr] 4d¹⁰ 5s² 5p⁵', shells: [2,8,18,18,7], shellHarmonic: '53:74', mass: 127 },
    { symbol: 'Xe', name: 'Xenon', z: 54, n: 77, period: 5, group: 18, octave: 5.75, note: 'C₇', harmonic: 54, color: '#a78bfa', noble: true, config: '[Kr] 4d¹⁰ 5s² 5p⁶', shells: [2,8,18,18,8], shellHarmonic: '54:77', mass: 131 },
    
    // Period 6 (key elements)
    { symbol: 'Au', name: 'Gold', z: 79, n: 118, period: 6, group: 11, octave: 6.30, note: 'E₈', harmonic: 79, color: '#ec4899', transition: true, config: '[Xe] 4f¹⁴ 5d¹⁰ 6s¹', shells: [2,8,18,32,18,1], shellHarmonic: '79:118', mass: 197 },
    { symbol: 'U', name: 'Uranium', z: 92, n: 146, period: 7, group: 3, octave: 6.52, note: 'G♯₈', harmonic: 92, color: '#10b981', config: '[Rn] 5f³ 6d¹ 7s²', shells: [2,8,18,32,21,9,2], shellHarmonic: '92:146', np_ratio: '46:73', mass: 238 },
  ];

  // Calculate harmonic relationship
  const calculateHarmonicRelationship = (z1, z2) => {
    const ratio = z2 / z1;
    const octaves = Math.log2(ratio);
    const semitones = Math.round(octaves * 12);
    
    const intervalNames = [
      'Unison', 'Minor 2nd', 'Major 2nd', 'Minor 3rd', 'Major 3rd',
      'Perfect 4th', 'Tritone', 'Perfect 5th', 'Minor 6th', 'Major 6th',
      'Minor 7th', 'Major 7th', 'Octave'
    ];
    
    const reducedSemitones = ((semitones % 12) + 12) % 12;
    const octaveCount = Math.floor(semitones / 12);
    const intervalName = intervalNames[reducedSemitones];
    
    const consonance = [0, 12, 7, 5, 4, 9, 3].includes(reducedSemitones) ? 'Consonant' : 
                       [2, 10].includes(reducedSemitones) ? 'Mild Dissonance' : 'Dissonant';
    
    return {
      ratio: ratio.toFixed(3),
      octaves: octaves.toFixed(2),
      semitones,
      interval: octaveCount > 0 ? `${intervalName} + ${octaveCount} octave(s)` : intervalName,
      consonance
    };
  };

  // Calculate nuclear harmonic and check if it's a perfect musical ratio
  const calculateNuclearHarmonic = (element) => {
    if (!element.n) return null;
    const npRatio = element.z / element.n;
    
    // Perfect musical ratios with tolerance
    const perfectRatios = [
      { ratio: 1.0, name: 'Unison (1:1)', semitones: 0, perfect: true },
      { ratio: 0.9375, name: 'Minor 2nd (15:16)', semitones: 1, perfect: false },
      { ratio: 0.8889, name: 'Major 2nd (8:9)', semitones: 2, perfect: false },
      { ratio: 0.8333, name: 'Minor 3rd (5:6)', semitones: 3, perfect: false },
      { ratio: 0.8, name: 'Major 3rd (4:5)', semitones: 4, perfect: false },
      { ratio: 0.75, name: 'Perfect 4th (3:4)', semitones: 5, perfect: true },
      { ratio: 0.7071, name: 'Tritone (1:√2)', semitones: 6, perfect: false },
      { ratio: 0.6667, name: 'Perfect 5th (2:3)', semitones: 7, perfect: true },
      { ratio: 0.625, name: 'Minor 6th (5:8)', semitones: 8, perfect: false },
      { ratio: 0.6, name: 'Major 6th (3:5)', semitones: 9, perfect: false },
      { ratio: 0.5625, name: 'Minor 7th (9:16)', semitones: 10, perfect: false },
      { ratio: 0.5333, name: 'Major 7th (8:15)', semitones: 11, perfect: false },
      { ratio: 0.5, name: 'Octave (1:2)', semitones: 12, perfect: true },
    ];
    
    let closestRatio = null;
    let minDiff = 1;
    let isPerfectMusical = false;
    
    perfectRatios.forEach(({ ratio, name, perfect }) => {
      const diff = Math.abs(npRatio - ratio);
      if (diff < minDiff && diff < 0.04) { // 4% tolerance
        minDiff = diff;
        closestRatio = name;
        isPerfectMusical = perfect && diff < 0.02; // Perfect intervals need tighter tolerance
      }
    });
    
    // Stability assessment
    let stability;
    if (npRatio > 0.95) stability = 'Highly unstable';
    else if (npRatio > 0.7) stability = 'Unstable (heavy)';
    else if (npRatio > 0.55) stability = 'Stable zone';
    else if (npRatio > 0.45) stability = 'Very stable';
    else stability = 'Light nucleus';
    
    // Check for magic numbers
    const magicNumbers = [2, 8, 20, 28, 50, 82, 126];
    const hasMagicProtons = magicNumbers.includes(element.z);
    const hasMagicNeutrons = magicNumbers.includes(element.n);
    const isDoubleMagic = hasMagicProtons && hasMagicNeutrons;
    
    if (isDoubleMagic) stability = '✨ DOUBLE MAGIC ✨';
    else if (hasMagicProtons || hasMagicNeutrons) stability += ' (Magic)';
    
    return {
      ratio: npRatio.toFixed(3),
      interpretation: closestRatio || 'Complex ratio',
      stability,
      isPerfectMusical,
      isDoubleMagic,
      hasMagic: hasMagicProtons || hasMagicNeutrons
    };
  };

  const harmonicRelationship = useMemo(() => {
    if (selectedElement && compareElement) {
      return calculateHarmonicRelationship(selectedElement.z, compareElement.z);
    }
    return null;
  }, [selectedElement, compareElement]);

  const getElementPosition = (element) => {
    const { period, group } = element;
    if (element.z >= 57 && element.z <= 71) return null;
    if (element.z >= 89 && element.z <= 103) return null;
    return { row: period, col: group };
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white p-4">
      <div className="max-w-[1800px] mx-auto">
        
        {/* Header */}
        <div className="text-center mb-4">
          <div className="flex items-center justify-center gap-3 mb-2">
            <Music className="w-8 h-8 text-cyan-400" />
            <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Harmonic Periodic Table: Nuclear & Electronic Resonance
            </h1>
            <Atom className="w-8 h-8 text-pink-400" />
          </div>
          <p className="text-sm text-cyan-200">
            Protons/Neutrons as Intervals • Electron Shells as Harmonics • Nuclear Stability as Consonance
          </p>
          <p className="text-xs text-purple-300 mt-1">
            Fractal Reality Framework • Ashman Roonz • github.com/AshmanRoonz/Fractal_Reality
          </p>
        </div>

        {/* View Mode Toggle */}
        <div className="flex flex-wrap gap-2 justify-center mb-4">
          <button
            onClick={() => {
              if (!soundEnabled) initAudio();
              setSoundEnabled(!soundEnabled);
            }}
            className={`px-4 py-2 rounded-lg font-bold text-sm transition-all ${
              soundEnabled ? 'bg-green-500 text-black' : 'bg-slate-700 text-gray-300'
            }`}
          >
            {soundEnabled ? '🔊 Sound ON' : '🔇 Sound OFF'}
          </button>
          {soundEnabled && (
            <button
              onClick={playOctaveSequence}
              disabled={isPlaying}
              className={`px-4 py-2 rounded-lg font-bold text-sm transition-all ${
                isPlaying ? 'bg-slate-600 text-gray-400' : 'bg-purple-500 text-white hover:bg-purple-600'
              }`}
            >
              {isPlaying ? '♪ Playing...' : '♪ Play Octave Scale'}
            </button>
          )}
          <button
            onClick={() => setViewMode('table')}
            className={`px-3 py-1 rounded-lg font-bold text-sm transition-all ${
              viewMode === 'table' ? 'bg-cyan-500 text-black' : 'bg-slate-700 text-gray-300'
            }`}
          >
            Periodic Table
          </button>
          <button
            onClick={() => setViewMode('shells')}
            className={`px-3 py-1 rounded-lg font-bold text-sm transition-all ${
              viewMode === 'shells' ? 'bg-purple-500 text-black' : 'bg-slate-700 text-gray-300'
            }`}
          >
            Electron Shell Harmonics
          </button>
          <button
            onClick={() => setViewMode('nucleus')}
            className={`px-3 py-1 rounded-lg font-bold text-sm transition-all ${
              viewMode === 'nucleus' ? 'bg-pink-500 text-black' : 'bg-slate-700 text-gray-300'
            }`}
          >
            Nuclear Harmonics
          </button>
        </div>

        {/* Controls */}
        <div className="flex flex-wrap gap-2 justify-center mb-4">
          <button
            onClick={() => setShowOctaves(!showOctaves)}
            className={`px-3 py-1 rounded-lg font-bold text-sm transition-all ${
              showOctaves ? 'bg-cyan-500 text-black' : 'bg-slate-700 text-gray-300'
            }`}
          >
            {showOctaves ? '✓' : ''} Octave Elements
          </button>
          <button
            onClick={() => setShowElectronShells(!showElectronShells)}
            className={`px-3 py-1 rounded-lg font-bold text-sm transition-all ${
              showElectronShells ? 'bg-purple-500 text-black' : 'bg-slate-700 text-gray-300'
            }`}
          >
            {showElectronShells ? '✓' : ''} Shell Config
          </button>
          <button
            onClick={() => setShowNeutronHarmonics(!showNeutronHarmonics)}
            className={`px-3 py-1 rounded-lg font-bold text-sm transition-all ${
              showNeutronHarmonics ? 'bg-pink-500 text-black' : 'bg-slate-700 text-gray-300'
            }`}
          >
            {showNeutronHarmonics ? '✓' : ''} N/P Ratio
          </button>
          <button
            onClick={() => setShowMusicalRatios(!showMusicalRatios)}
            className={`px-3 py-1 rounded-lg font-bold text-sm transition-all ${
              showMusicalRatios ? 'bg-pink-500 text-black' : 'bg-slate-700 text-gray-300'
            }`}
          >
            {showMusicalRatios ? '✓' : ''} Perfect Musical Ratios
          </button>
          {(selectedElement || compareElement) && (
            <button
              onClick={() => {
                setSelectedElement(null);
                setCompareElement(null);
              }}
              className="px-3 py-1 rounded-lg font-bold text-sm bg-red-500 text-white hover:bg-red-600"
            >
              Clear
            </button>
          )}
        </div>

        {/* Detail Panel */}
        {selectedElement && (
          <div className="mb-4 bg-gradient-to-r from-purple-900/80 to-pink-900/80 rounded-xl p-4 border-2 border-cyan-500/50">
            <div className="grid md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-5xl font-bold mb-2" style={{ color: selectedElement.color }}>
                  {selectedElement.symbol}
                </div>
                <div className="text-xl">{selectedElement.name}</div>
                <div className="text-cyan-300">Z = {selectedElement.z}, N = {selectedElement.n}, Mass = {selectedElement.mass}</div>
                <div className="text-purple-300 text-sm mt-1">{selectedElement.note} • {selectedElement.interval}</div>
              </div>
              
              <div className="space-y-2 text-sm">
                <div className="font-bold text-pink-300">Electronic Structure:</div>
                <div className="text-cyan-200">Config: {selectedElement.config}</div>
                <div className="text-purple-200">Shells: {selectedElement.shells.join('-')}</div>
                {selectedElement.shellHarmonic && (
                  <div className="text-yellow-300">Shell Ratio: {selectedElement.shellHarmonic}</div>
                )}
              </div>
              
              <div className="space-y-2 text-sm">
                <div className="font-bold text-pink-300">Nuclear Structure:</div>
                {selectedElement.n > 0 && (
                  <>
                    <div className="text-cyan-200">Protons: {selectedElement.z}</div>
                    <div className="text-purple-200">Neutrons: {selectedElement.n}</div>
                    <div className="text-yellow-300">N/P Ratio: {(selectedElement.n/selectedElement.z).toFixed(3)}</div>
                    <div className="text-green-300">{selectedElement.np_ratio}</div>
                    {(() => {
                      const nuclear = calculateNuclearHarmonic(selectedElement);
                      return nuclear && (
                        <div className={`font-bold ${
                          nuclear.stability.includes('stable') ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {nuclear.stability}
                        </div>
                      );
                    })()}
                  </>
                )}
              </div>
            </div>
            
            {compareElement && harmonicRelationship && (
              <div className="mt-4 pt-4 border-t border-cyan-500/30">
                <div className="text-center">
                  <div className="text-xl font-bold text-pink-400 mb-2">
                    Harmonic Relationship: {selectedElement.symbol} ↔ {compareElement.symbol}
                  </div>
                  <div className="grid grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="text-gray-400">Ratio</div>
                      <div className="text-cyan-300 font-bold">{harmonicRelationship.ratio}:1</div>
                    </div>
                    <div>
                      <div className="text-gray-400">Interval</div>
                      <div className="text-purple-300 font-bold">{harmonicRelationship.interval}</div>
                    </div>
                    <div>
                      <div className="text-gray-400">Semitones</div>
                      <div className="text-yellow-300 font-bold">{harmonicRelationship.semitones}</div>
                    </div>
                    <div>
                      <div className="text-gray-400">Consonance</div>
                      <div className={`font-bold ${
                        harmonicRelationship.consonance === 'Consonant' ? 'text-green-400' :
                        harmonicRelationship.consonance === 'Mild Dissonance' ? 'text-yellow-400' :
                        'text-red-400'
                      }`}>
                        {harmonicRelationship.consonance}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Main Content */}
        {viewMode === 'table' && (
          <div className="bg-black/30 rounded-xl p-4 border border-cyan-500/30 overflow-x-auto">
            <div className="min-w-[1200px]">
              <div className="grid gap-1" style={{ 
                gridTemplateColumns: 'repeat(18, 1fr)',
                gridTemplateRows: 'repeat(7, auto)'
              }}>
                {elements.map((element) => {
                  const pos = getElementPosition(element);
                  if (!pos) return null;
                  
                  const isOctave = Math.log2(element.z) % 1 === 0;
                  const isSelected = selectedElement?.z === element.z;
                  const isCompare = compareElement?.z === element.z;
                  
                  // Check if has perfect musical N/P ratio
                  const nuclear = calculateNuclearHarmonic(element);
                  const hasMusicalRatio = nuclear?.isPerfectMusical;
                  const hasMagic = nuclear?.hasMagic;
                  const isDoubleMagic = nuclear?.isDoubleMagic;
                  
                  return (
                    <div
                      key={element.z}
                      onClick={() => {
                        if (soundEnabled) playElementTone(element, 0.5);
                        if (!selectedElement) {
                          setSelectedElement(element);
                        } else if (!compareElement && element.z !== selectedElement.z) {
                          setCompareElement(element);
                          setTimeout(() => {
                            if (soundEnabled) playChord(selectedElement, element);
                          }, 100);
                        } else {
                          setSelectedElement(element);
                          setCompareElement(null);
                        }
                      }}
                      style={{
                        gridColumn: pos.col,
                        gridRow: pos.row,
                        backgroundColor: element.color + '40',
                        borderColor: element.color,
                      }}
                      className={`
                        relative p-2 rounded border-2 cursor-pointer transition-all text-center
                        hover:scale-110 hover:shadow-lg hover:z-10
                        ${isOctave && showOctaves ? 'ring-2 ring-yellow-400' : ''}
                        ${isSelected ? 'ring-2 ring-cyan-400 scale-110 z-20' : ''}
                        ${isCompare ? 'ring-2 ring-pink-400 scale-110 z-20' : ''}
                        ${element.noble ? 'border-4' : ''}
                        ${hasMusicalRatio && showMusicalRatios ? 'ring-2 ring-green-400 shadow-lg shadow-green-500/50' : ''}
                        ${isDoubleMagic && showMusicalRatios ? 'ring-4 ring-purple-400 shadow-xl shadow-purple-500/70' : ''}
                      `}
                    >
                      {showNeutronHarmonics && element.n > 0 && (
                        <div className="absolute top-0 left-0 text-[7px] bg-black/50 px-1 rounded">
                          N/P:{(element.n/element.z).toFixed(2)}
                        </div>
                      )}
                      {isDoubleMagic && showMusicalRatios && (
                        <div className="absolute top-0 right-0 text-[10px]">✨</div>
                      )}
                      {hasMagic && !isDoubleMagic && showMusicalRatios && (
                        <div className="absolute top-0 right-0 text-[10px]">⭐</div>
                      )}
                      {hasMusicalRatio && showMusicalRatios && (
                        <div className="absolute bottom-0 right-0 text-[10px]">🎵</div>
                      )}
                      <div className="text-[9px] text-gray-400">{element.z}</div>
                      <div className="text-lg font-bold">{element.symbol}</div>
                      {showElectronShells && (
                        <div className="text-[7px] text-cyan-300">{element.shells.join('-')}</div>
                      )}
                      <div className="text-[7px] text-gray-300">{element.note}</div>
                      {isOctave && showOctaves && (
                        <div className="absolute bottom-0 left-0 right-0 text-[7px] bg-yellow-400/20 text-yellow-300">
                          2^{Math.log2(element.z)}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {viewMode === 'shells' && (
          <div className="grid gap-4">
            <div className="bg-black/30 rounded-xl p-6 border border-purple-500/30">
              <h2 className="text-2xl font-bold text-purple-300 mb-4 flex items-center gap-2">
                <Layers className="w-6 h-6" />
                Electron Shell Harmonics
              </h2>
              <div className="space-y-6">
                {[
                  { name: 'K Shell (n=1)', max: 2, note: 'Foundation octave - 1s²', elements: elements.filter(e => e.shells && e.shells[0] === 2).slice(0, 5) },
                  { name: 'L Shell (n=2)', max: 8, note: 'Second harmonic - 2s² 2p⁶', elements: elements.filter(e => e.shells && e.shells[1] === 8).slice(0, 5) },
                  { name: 'M Shell (n=3)', max: 18, note: 'Third harmonic - 3s² 3p⁶ 3d¹⁰', elements: elements.filter(e => e.shells && e.shells[2] >= 8).slice(0, 5) },
                  { name: 'N Shell (n=4)', max: 32, note: 'Fourth harmonic - adds 4f orbitals', elements: elements.filter(e => e.shells && e.shells.length >= 4).slice(0, 5) },
                ].map((shell, i) => (
                  <div key={i} className="bg-purple-900/20 rounded-lg p-4">
                    <div className="font-bold text-xl text-cyan-300 mb-2">{shell.name}</div>
                    <div className="text-sm text-gray-400 mb-3">{shell.note}</div>
                    <div className="text-lg text-purple-300 mb-3">
                      Max electrons: {shell.max} = 2n² (harmonic series)
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {shell.elements.map(el => (
                        <div
                          key={el.z}
                          onClick={() => setSelectedElement(el)}
                          className="px-3 py-2 bg-purple-800/40 rounded border-2 cursor-pointer hover:scale-105 transition-all"
                          style={{ borderColor: el.color }}
                        >
                          <div className="text-lg font-bold">{el.symbol}</div>
                          <div className="text-xs text-gray-400">{el.shells?.join('-')}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
                
                <div className="bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-lg p-4 border border-pink-500/30">
                  <div className="text-center">
                    <div className="text-xl font-bold text-pink-300 mb-2">🎵 The Shell Harmonic Pattern 🎵</div>
                    <div className="text-lg text-cyan-200">
                      2, 8, 18, 32... = 2n² where n = shell number
                    </div>
                    <div className="text-md text-purple-300 mt-2">
                      This is the harmonic series! Each shell is a perfect square relationship.
                    </div>
                    <div className="text-md text-yellow-300 mt-2">
                      Noble gases complete shells → Perfect harmonic closure → Maximum stability
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {viewMode === 'nucleus' && (
          <div className="grid gap-4">
            <div className="bg-black/30 rounded-xl p-6 border border-pink-500/30">
              <h2 className="text-2xl font-bold text-pink-300 mb-4 flex items-center gap-2">
                <Atom className="w-6 h-6" />
                Nuclear Harmonics: Proton/Neutron Ratios
              </h2>
              
              <div className="grid md:grid-cols-2 gap-6 mb-6">
                <div className="bg-pink-900/20 rounded-lg p-4">
                  <div className="text-xl font-bold text-cyan-300 mb-3">Perfect 1:1 Ratio Elements</div>
                  <div className="text-sm text-gray-300 mb-3">
                    Elements where N = Z (perfect unison) are maximally stable for light nuclei
                  </div>
                  <div className="space-y-2">
                    {elements.filter(e => e.n > 0 && Math.abs(e.n/e.z - 1) < 0.05).slice(0, 8).map(el => {
                      const nuclear = calculateNuclearHarmonic(el);
                      return (
                        <div
                          key={el.z}
                          onClick={() => setSelectedElement(el)}
                          className="flex justify-between items-center p-2 bg-green-900/20 rounded border border-green-500/30 cursor-pointer hover:bg-green-900/30"
                        >
                          <div className="flex items-center gap-2">
                            <div className="text-xl font-bold" style={{ color: el.color }}>{el.symbol}</div>
                            <div className="text-sm text-gray-400">(Z={el.z})</div>
                          </div>
                          <div className="text-sm">
                            <div className="text-cyan-300">{el.z}p : {el.n}n</div>
                            <div className="text-green-400 text-xs">{nuclear?.interpretation}</div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div className="bg-pink-900/20 rounded-lg p-4">
                  <div className="text-xl font-bold text-cyan-300 mb-3">Musical Ratio Elements</div>
                  <div className="text-sm text-gray-300 mb-3">
                    Elements with N/P ratios matching musical intervals
                  </div>
                  <div className="space-y-2">
                    {elements.filter(e => {
                      if (!e.n) return false;
                      const ratio = e.n / e.z;
                      return Math.abs(ratio - 0.667) < 0.05 || // 2:3 fifth
                             Math.abs(ratio - 0.75) < 0.05 ||  // 3:4 fourth
                             Math.abs(ratio - 0.8) < 0.05 ||   // 4:5 major third
                             Math.abs(ratio - 0.833) < 0.05;  // 5:6 minor third
                    }).slice(0, 8).map(el => {
                      const nuclear = calculateNuclearHarmonic(el);
                      return (
                        <div
                          key={el.z}
                          onClick={() => setSelectedElement(el)}
                          className="flex justify-between items-center p-2 bg-purple-900/20 rounded border border-purple-500/30 cursor-pointer hover:bg-purple-900/30"
                        >
                          <div className="flex items-center gap-2">
                            <div className="text-xl font-bold" style={{ color: el.color }}>{el.symbol}</div>
                            <div className="text-sm text-gray-400">(Z={el.z})</div>
                          </div>
                          <div className="text-sm">
                            <div className="text-cyan-300">{el.z}p : {el.n}n</div>
                            <div className="text-purple-400 text-xs">{nuclear?.interpretation}</div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-r from-pink-900/50 to-purple-900/50 rounded-lg p-4 border border-pink-500/30">
                <div className="text-center">
                  <div className="text-xl font-bold text-pink-300 mb-2">⚛️ The Nuclear Stability Pattern ⚛️</div>
                  <div className="grid md:grid-cols-3 gap-4 mt-4 text-sm">
                    <div>
                      <div className="text-green-400 font-bold mb-1">Light Nuclei (Z &lt; 20)</div>
                      <div className="text-gray-300">N ≈ Z (1:1 ratio)</div>
                      <div className="text-cyan-300">Perfect unison = stable</div>
                    </div>
                    <div>
                      <div className="text-yellow-400 font-bold mb-1">Medium Nuclei (Z = 20-50)</div>
                      <div className="text-gray-300">N ≈ 1.3Z (4:5 ratio)</div>
                      <div className="text-cyan-300">Major third interval</div>
                    </div>
                    <div>
                      <div className="text-red-400 font-bold mb-1">Heavy Nuclei (Z &gt; 50)</div>
                      <div className="text-gray-300">N ≈ 1.5Z (2:3 ratio)</div>
                      <div className="text-cyan-300">Perfect fifth needed</div>
                    </div>
                  </div>
                  <div className="mt-4 text-lg text-purple-200">
                    As nuclei get heavier, they need MORE neutrons (higher intervals) to maintain stability!
                  </div>
                  <div className="mt-2 text-md text-yellow-300">
                    Magic numbers (2, 8, 20, 28, 50, 82, 126) = harmonic completion points
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Theory Section */}
        <div className="mt-4 bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-xl p-4 border-2 border-pink-500/50">
          <h2 className="text-2xl font-bold mb-3 text-center text-cyan-300">
            The Complete Harmonic Structure of Matter
          </h2>
          <div className="grid md:grid-cols-3 gap-4 text-sm">
            <div className="text-center">
              <div className="text-4xl mb-2">🎵</div>
              <h3 className="text-lg font-bold text-purple-300 mb-2">Atomic Numbers</h3>
              <p className="text-gray-300">
                Proton count = harmonic frequency. Powers of 2 (H, He, Be, O, S...) = perfect octaves.
              </p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-2">⚛️</div>
              <h3 className="text-lg font-bold text-cyan-300 mb-2">Electron Shells</h3>
              <p className="text-gray-300">
                2n² pattern = harmonic series. Noble gases = complete octaves. Valence electrons = active harmonics.
              </p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-2">🔬</div>
              <h3 className="text-lg font-bold text-pink-300 mb-2">Nuclear Ratios</h3>
              <p className="text-gray-300">
                N/P ratio = musical interval. 1:1 for light, increases to 3:2 for heavy. Stability = consonance!
              </p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default HarmonicPeriodicTable;