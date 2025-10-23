<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Fractal Music Learner – v0.1</title>
<style>
  html, body { margin:0; height:100%; background:#0b0f14; color:#e5f1ff; font-family:Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji"; }
  #ui { position:fixed; inset:16px auto auto 16px; z-index:10; display:flex; gap:8px; flex-wrap:wrap; }
  button, .pill { background:#12202f; color:#e5f1ff; border:1px solid #2a3a4a; padding:10px 14px; border-radius:12px; cursor:pointer; font-weight:600; letter-spacing:.2px; }
  button:hover { background:#16273a; }
  .pill { user-select:none; }
  #stats { position:fixed; right:16px; top:16px; background:#0e1621aa; border:1px solid #28405a; padding:10px 12px; border-radius:12px; font-size:12px; line-height:1.35; }
  canvas { display:block; width:100vw; height:100vh; }
  a { color:#8fd3ff; }
</style>
</head>
<body>
  <div id="ui">
    <button id="start">🎙️ Start Mic</button>
    <button id="stop" disabled>⏹ Stop</button>
    <button id="clear">🧹 Clear Memory</button>
    <button id="mute">🔇 Mute Synth</button>
    <span class="pill" id="status">idle</span>
  </div>
  <div id="stats">tempo: <span id="tempo">--</span> bpm<br/>key: <span id="key">--</span><br/>rms: <span id="rms">--</span><br/>centroid: <span id="cent">--</span> Hz<br/>mem: <span id="mem">0</span> motifs</div>
  <canvas id="viz"></canvas>

<script>
// Fractal Music Learner – v0.1
// Core idea (aligned with your framework):
// Center (•') = the circular hub on canvas. Memory (∞') = orbiting motifs.
// ∇ Convergence: audio features flow in; [ICE] validation here is a simple thresholding/consistency test;
// ℰ Emergence: validated motifs are written into the memory-graph.
// Resonance: cosine similarity activates past motifs; coherence lights them up; jam-synth plays along accordingly.

const canvas = document.getElementById('viz');
const ctx = canvas.getContext('2d');
let W = canvas.width = window.innerWidth; let H = canvas.height = window.innerHeight;
window.addEventListener('resize', ()=>{ W = canvas.width = innerWidth; H = canvas.height = innerHeight; });

const $tempo = document.getElementById('tempo');
const $key = document.getElementById('key');
const $rms = document.getElementById('rms');
const $cent = document.getElementById('cent');
const $mem = document.getElementById('mem');
const $status = document.getElementById('status');

const btnStart = document.getElementById('start');
const btnStop  = document.getElementById('stop');
const btnClear = document.getElementById('clear');
const btnMute  = document.getElementById('mute');

let audioCtx, analyser, fft, timeData, micNode, running=false;
let synthMuted = false;

// Audio feature state
let feature = {
  rms: 0,
  centroidHz: 0,
  rolloffHz: 0,
  pitchHz: 0,
  pitchClass: null,
  tempoBPM: 0,
  beatNow: false
};

// Memory graph of motifs (validated snapshots)
const memory = []; // { t, vec:[rms,cent,roll,pclass,tempo], act, angle, radius }

// Jam synth
let masterGain, osc, env = null; // ADSR envelope
let lastBeatTime = 0, beatInterval = 0; // seconds

function hzToPitchClass(hz){
  if(!hz || !isFinite(hz) || hz <= 0) return null;
  const A4 = 440;
  const n = Math.round(12 * Math.log2(hz / A4));
  const pc = ((n % 12) + 12) % 12; // 0..11
  return pc;
}

function pitchClassName(pc){
  const names = ['A','A#','B','C','C#','D','D#','E','F','F#','G','G#'];
  return pc==null? '--' : names[pc];
}

function cosine(a,b){
  let s=0,sa=0,sb=0; for(let i=0;i<a.length;i++){ s+=a[i]*b[i]; sa+=a[i]*a[i]; sb+=b[i]*b[i]; }
  return (sa>0 && sb>0)? s/Math.sqrt(sa*sb) : 0;
}

function smooth(prev, next, k=0.2){ return prev + k*(next - prev); }

async function start(){
  if(running) return;
  audioCtx = new (window.AudioContext||window.webkitAudioContext)();
  const stream = await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:false, noiseSuppression:false, autoGainControl:false}});
  micNode = audioCtx.createMediaStreamSource(stream);
  analyser = audioCtx.createAnalyser();
  analyser.fftSize = 2048;
  analyser.smoothingTimeConstant = 0.8;
  fft = new Uint8Array(analyser.frequencyBinCount);
  timeData = new Float32Array(analyser.fftSize);
  micNode.connect(analyser);

  // Synth chain
  masterGain = audioCtx.createGain(); masterGain.gain.value = 0.15; masterGain.connect(audioCtx.destination);
  running = true; $status.textContent = 'listening'; btnStart.disabled = true; btnStop.disabled = false;
  loop();
}

function stop(){
  if(!running) return;
  running=false; $status.textContent = 'stopped'; btnStart.disabled=false; btnStop.disabled=true;
  if(audioCtx){ audioCtx.close(); }
}

btnStart.onclick = start;
btnStop.onclick = stop;
btnClear.onclick = ()=>{ memory.length = 0; };
btnMute.onclick = ()=>{ synthMuted = !synthMuted; btnMute.textContent = synthMuted? '🔈 Unmute Synth' : '🔇 Mute Synth'; };

// --- Feature Extraction --- //
function computeFeatures(dt){
  analyser.getFloatTimeDomainData(timeData);
  analyser.getByteFrequencyData(fft);

  // RMS energy
  let sum=0; for(let i=0;i<timeData.length;i++){ const x=timeData[i]; sum += x*x; }
  const rms = Math.sqrt(sum/timeData.length);

  // Spectral centroid & rolloff
  let num=0, den=0; let cumulative=0; let total=0; for(let i=0;i<fft.length;i++){ const mag = fft[i]; const f = i * audioCtx.sampleRate / (2*fft.length); num += f*mag; den += mag; total += mag; }
  const centroidHz = den>0? num/den : 0;
  const target = total*0.85; cumulative=0; let rolloffHz=0; for(let i=0;i<fft.length;i++){ cumulative += fft[i]; if(cumulative>=target){ rolloffHz = i * audioCtx.sampleRate / (2*fft.length); break; } }

  // Autocorrelation for pitch
  const pitchHz = autoCorrelate(timeData, audioCtx.sampleRate);
  const pClass = hzToPitchClass(pitchHz);

  // Beat (simple onset/energy threshold with adaptive avg)
  beatNow = beatTracker(rms, dt);

  feature.rms = smooth(feature.rms, rms, 0.3);
  feature.centroidHz = smooth(feature.centroidHz, centroidHz, 0.3);
  feature.rolloffHz = smooth(feature.rolloffHz, rolloffHz, 0.3);
  feature.pitchHz = isFinite(pitchHz)? smooth(feature.pitchHz||pitchHz, pitchHz, 0.2) : feature.pitchHz*0.98;
  feature.pitchClass = pClass ?? feature.pitchClass ?? null;
  feature.tempoBPM = beatDetector.tempoBPM || feature.tempoBPM;
  feature.beatNow = beatNow;
}

// Autocorrelation-based pitch (returns Hz or 0)
function autoCorrelate(buf, sampleRate){
  let SIZE = buf.length;
  let rms=0; for(let i=0;i<SIZE;i++){ const v=buf[i]; rms += v*v; }
  rms = Math.sqrt(rms/SIZE); if(rms<0.008) return 0;
  let r1=0, r2=SIZE-1, th=0.2;
  for(let i=0;i<SIZE/2;i++){ if(Math.abs(buf[i])<th){ r1=i; break; } }
  for(let i=1;i<SIZE/2;i++){ if(Math.abs(buf[SIZE-i])<th){ r2=SIZE-i; break; } }
  buf = buf.slice(r1, r2);
  SIZE = buf.length;
  const c = new Array(SIZE).fill(0);
  for(let i=0;i<SIZE;i++) for(let j=0;j<SIZE-i;j++) c[i] += buf[j]*buf[j+i];
  let d=0; while(d<SIZE-1 && c[d]>c[d+1]) d++;
  let maxval=-1, maxpos=-1; for(let i=d;i<SIZE;i++){ if(c[i]>maxval){ maxval=c[i]; maxpos=i; } }
  if(maxpos<=0) return 0; // no pitch
  const T0 = maxpos; return sampleRate/T0;
}

// Simple beat tracker (energy-based)
const beatDetector = { avg:0, env:0, t:0, lastBeat:0, tempoBPM:0, intervals:[] };
function beatTracker(rms, dt){
  beatDetector.t += dt;
  beatDetector.env = smooth(beatDetector.env, rms, 0.15);
  beatDetector.avg = smooth(beatDetector.avg, rms, 0.01);
  const isBeat = beatDetector.env > beatDetector.avg*1.25 && (beatDetector.t - beatDetector.lastBeat) > 0.2; // >300 BPM guard
  if(isBeat){
    const now = beatDetector.t;
    const interval = now - beatDetector.lastBeat;
    beatDetector.lastBeat = now;
    if(interval>0.25 && interval<1.2){ // 50–240 BPM window
      beatDetector.intervals.push(interval); if(beatDetector.intervals.length>12) beatDetector.intervals.shift();
      const med = median(beatDetector.intervals);
      beatDetector.tempoBPM = Math.round(60/med);
      beatInterval = med; lastBeatTime = performance.now()/1000;
    }
  }
  return isBeat;
}
function median(a){ const b=[...a].sort((x,y)=>x-y); const m=Math.floor(b.length/2); return b.length? (b.length%2? b[m] : (b[m-1]+b[m])/2) : 0.5; }

// --- Memory & Resonance --- //
function validateAndStore(){
  // [ICE] (very simple): ensure stable energy & centroid; avoid spam
  const t = performance.now()/1000;
  const vec = [feature.rms, normHz(feature.centroidHz), normHz(feature.rolloffHz), (feature.pitchClass??-1)/12, (feature.tempoBPM||0)/240];
  if(!isFinite(vec[0])||vec.some(v=>v==null)) return;

  // Only write on beats for clarity
  if(feature.beatNow){
    // Distinctness test: don’t store if too similar to last motif
    const last = memory[memory.length-1];
    const sim = last? cosine(vec, last.vec) : 0;
    if(sim < 0.96){
      const angle = hashToAngle(vec);
      const radius = Math.min(W,H)*0.33 + Math.random()*40;
      memory.push({ t, vec, act:0, angle, radius });
      if(memory.length>512) memory.shift();
    }
  }
}

function hashToAngle(vec){
  // Map feature vector to [0,2π)
  let h=0; for(let i=0;i<vec.length;i++){ h = (h*1.37 + (vec[i]*997.3))%1; }
  return h * Math.PI*2;
}

function normHz(hz){ return Math.log2(Math.max(hz, 1))/12; }

function resonateAndJam(){
  if(memory.length===0) return;
  // Current feature vector
  const v = [feature.rms, normHz(feature.centroidHz), normHz(feature.rolloffHz), (feature.pitchClass??-1)/12, (feature.tempoBPM||0)/240];
  // Activate top-K similar motifs
  const scored = memory.map((m,i)=>({i, s: cosine(v, m.vec)}));
  scored.sort((a,b)=>b.s-a.s);
  const top = scored.slice(0, 12);
  top.forEach(({i,s})=>{ memory[i].act = Math.max(memory[i].act, s); });

  // Jam: on beats, pick a pitch from dominant PC and top memory
  const now = performance.now()/1000;
  if(beatInterval>0 && (now - lastBeatTime) < 0.15){ // near-beat edge
    const pc = chooseScalePC(feature.pitchClass);
    const noteHz = pcToHz(pc, 4); // around A4 region
    if(!synthMuted) trigSynth(noteHz, 0.12);
  }
}

function chooseScalePC(rootPC){
  // Minor pentatonic relative to detected root (fallback A)
  const root = (rootPC==null)? 0 : rootPC; // A as 0 in our mapping
  const scale = [0,3,5,7,10]; // A minor pentatonic offsets
  const pick = scale[Math.floor(Math.random()*scale.length)];
  return (root + pick) % 12;
}
function pcToHz(pc, octave=4){ const A4=440; const semis = pc; return A4 * Math.pow(2, semis/12 + (octave-4)); }

function trigSynth(freq, dur=0.1){
  const t0 = audioCtx.currentTime;
  const g = audioCtx.createGain(); g.gain.setValueAtTime(0, t0);
  const o = audioCtx.createOscillator(); o.type='triangle'; o.frequency.setValueAtTime(freq, t0);
  o.connect(g).connect(masterGain);
  const a=0.005, d=0.06, s=0.4, r=0.12;
  g.gain.linearRampToValueAtTime(1.0, t0+a);
  g.gain.linearRampToValueAtTime(s, t0+a+d);
  g.gain.linearRampToValueAtTime(0.0, t0+dur+r);
  o.start(t0); o.stop(t0+dur+r+0.02);
}

// --- Render --- //
function draw(){
  ctx.clearRect(0,0,W,H);
  const cx=W/2, cy=H/2;

  // Background subtle grid
  ctx.save();
  ctx.globalAlpha = 0.08;
  for(let x=0;x<W;x+=40){ ctx.fillStyle = (x%200===0?'#173149':'#0f1b29'); ctx.fillRect(x,0,1,H); }
  for(let y=0;y<H;y+=40){ ctx.fillStyle = (y%200===0?'#173149':'#0f1b29'); ctx.fillRect(0,y,W,1); }
  ctx.restore();

  // Center (•')
  const beta = 0.5; // balance
  const centerR = 26 + 10*Math.min(1, feature.rms*18);
  const glow = 0.3 + 0.7*Math.min(1, feature.rms*14);
  ctx.save();
  ctx.shadowBlur = 30; ctx.shadowColor = `rgba(120,220,255,${glow})`;
  ctx.beginPath(); ctx.arc(cx, cy, centerR, 0, Math.PI*2); ctx.fillStyle = '#1b3a52'; ctx.fill();
  ctx.shadowBlur = 0;
  ctx.lineWidth = 2; ctx.strokeStyle = '#4fb4ff'; ctx.stroke();
  ctx.restore();

  // Memory ring & motifs
  const R0 = Math.min(W,H)*0.34;

  // Animate activation decay and draw connections from center (resonance)
  for(const m of memory){ m.act = Math.max(0, m.act - 0.01); }

  // Draw connections for strongly resonant motifs
  memory.forEach(m=>{
    if(m.act>0.6){
      const x = cx + Math.cos(m.angle)*m.radius;
      const y = cy + Math.sin(m.angle)*m.radius;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(x,y);
      ctx.strokeStyle = `rgba(79,180,255,${(m.act-0.5)*1.2})`;
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }
  });

  // Draw motifs
  memory.forEach(m=>{
    const pulse = 1 + 0.12*Math.sin((performance.now()/130)+m.angle*3.0);
    const r = 4 + 6*m.act*pulse;
    const x = cx + Math.cos(m.angle)*m.radius;
    const y = cy + Math.sin(m.angle)*m.radius;
    ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2);
    const hue = 190 + (m.vec[3]*360); // mapped by pitch class
    ctx.fillStyle = `hsla(${hue}, 80%, ${45+30*m.act}%, ${0.6+0.4*m.act})`;
    ctx.fill();
    ctx.lineWidth=1; ctx.strokeStyle = `rgba(180,230,255,${0.5+0.5*m.act})`; ctx.stroke();
  });

  // Ring
  ctx.beginPath(); ctx.arc(cx, cy, R0, 0, Math.PI*2);
  ctx.strokeStyle = '#16324a'; ctx.lineWidth = 1; ctx.stroke();

  // HUD text at bottom
  ctx.font = '12px Inter, system-ui, sans-serif';
  ctx.fillStyle = '#7fbfff';
  ctx.fillText('Fractal Music Learner – v0.1  •  memory nodes brighten when resonating  •  center pulses with input energy', 16, H-20);
}

// Main loop
let prevT = performance.now();
function loop(){
  if(!running){ draw(); return; }
  const now = performance.now(); const dt = (now - prevT)/1000; prevT = now;
  computeFeatures(dt);
  validateAndStore();
  resonateAndJam();
  draw();
  // Stats UI
  $tempo.textContent = feature.tempoBPM? String(feature.tempoBPM) : '--';
  $key.textContent = pitchClassName(feature.pitchClass);
  $rms.textContent = feature.rms.toFixed(3);
  $cent.textContent = Math.round(feature.centroidHz);
  $mem.textContent = memory.length;
  requestAnimationFrame(loop);
}

// Kick an initial frame
draw();
</script>
</body>
</html>
