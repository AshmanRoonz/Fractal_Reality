import { useState, useEffect, useRef, useCallback } from "react";

// ============================================================================
// LAST SHIP SAILING — React Overlay Effects System
// Cinematic in-game overlays: damage vignettes, kill streaks, round countdowns,
// achievement medals, ability activations, and more.
// Sits on top of the THREE.js canvas; the game engine pushes events in.
// ============================================================================

// --- Utility: spring-style easing ---
const easeOutBack = (t) => {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
};
const easeOutElastic = (t) => {
  if (t === 0 || t === 1) return t;
  return Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * (2 * Math.PI) / 3) + 1;
};

// --- Damage Vignette ---
function DamageVignette({ intensity = 0, direction = null }) {
  const [flash, setFlash] = useState(0);
  const [shakeX, setShakeX] = useState(0);
  const [shakeY, setShakeY] = useState(0);
  const shakeRef = useRef(null);

  useEffect(() => {
    if (intensity > 0) {
      setFlash(Math.min(intensity, 1));
      // Screen shake
      let frame = 0;
      const maxFrames = 12;
      const mag = intensity * 8;
      const doShake = () => {
        if (frame >= maxFrames) {
          setShakeX(0);
          setShakeY(0);
          return;
        }
        const decay = 1 - frame / maxFrames;
        setShakeX((Math.random() - 0.5) * mag * decay);
        setShakeY((Math.random() - 0.5) * mag * decay);
        frame++;
        shakeRef.current = requestAnimationFrame(doShake);
      };
      doShake();
      const fadeOut = setTimeout(() => setFlash(0), 400);
      return () => {
        clearTimeout(fadeOut);
        if (shakeRef.current) cancelAnimationFrame(shakeRef.current);
      };
    }
  }, [intensity]);

  // Directional indicators
  const dirs = direction ? [direction] : [];

  return (
    <div
      style={{
        position: "fixed", inset: 0, pointerEvents: "none", zIndex: 50,
        transform: `translate(${shakeX}px, ${shakeY}px)`,
      }}
    >
      {/* Red vignette */}
      <div
        style={{
          position: "absolute", inset: 0,
          background: `radial-gradient(ellipse at center, transparent 30%, rgba(255,0,0,${flash * 0.5}) 100%)`,
          transition: "background 0.3s ease-out",
        }}
      />
      {/* Chromatic aberration edge */}
      <div
        style={{
          position: "absolute", inset: 0,
          boxShadow: flash > 0.3
            ? `inset 0 0 80px rgba(255,0,0,${flash * 0.3}), inset 0 0 120px rgba(0,0,0,${flash * 0.2})`
            : "none",
          transition: "box-shadow 0.2s ease-out",
        }}
      />
      {/* Directional damage arrows */}
      {dirs.map((d, i) => (
        <DamageArrow key={`${d}-${i}`} direction={d} opacity={flash} />
      ))}
    </div>
  );
}

function DamageArrow({ direction, opacity }) {
  const positions = {
    top:    { top: "8%", left: "50%", transform: "translateX(-50%) rotate(0deg)" },
    bottom: { bottom: "8%", left: "50%", transform: "translateX(-50%) rotate(180deg)" },
    left:   { top: "50%", left: "5%", transform: "translateY(-50%) rotate(-90deg)" },
    right:  { top: "50%", right: "5%", transform: "translateY(-50%) rotate(90deg)" },
  };
  return (
    <div style={{ position: "absolute", ...positions[direction], pointerEvents: "none" }}>
      <svg width="60" height="30" style={{ opacity, filter: `drop-shadow(0 0 8px rgba(255,40,0,0.8))`, transition: "opacity 0.3s" }}>
        <polygon points="10,28 30,2 50,28" fill="none" stroke="#ff2200" strokeWidth="3" />
        <polygon points="18,26 30,8 42,26" fill="rgba(255,34,0,0.4)" stroke="none" />
      </svg>
    </div>
  );
}

// --- Kill Streak Announcements ---
const STREAK_DATA = [
  { count: 2, label: "DOUBLE KILL", color: "#ffcc00", scale: 1.1 },
  { count: 3, label: "TRIPLE KILL", color: "#ff8800", scale: 1.2 },
  { count: 4, label: "QUAD KILL", color: "#ff4400", scale: 1.35 },
  { count: 5, label: "RAMPAGE", color: "#ff0044", scale: 1.5 },
  { count: 6, label: "UNSTOPPABLE", color: "#cc00ff", scale: 1.6 },
  { count: 7, label: "GODLIKE", color: "#ff00ff", scale: 1.7, glow: true },
];

function KillStreakAnnouncement({ streak = 0 }) {
  const [visible, setVisible] = useState(false);
  const [anim, setAnim] = useState(0);
  const [data, setData] = useState(null);
  const animRef = useRef(null);

  useEffect(() => {
    if (streak < 2) return;
    const d = STREAK_DATA.find((s) => s.count === streak) || STREAK_DATA[STREAK_DATA.length - 1];
    setData(d);
    setVisible(true);
    setAnim(0);

    let start = null;
    const duration = 2000;
    const animate = (ts) => {
      if (!start) start = ts;
      const t = Math.min((ts - start) / duration, 1);
      setAnim(t);
      if (t < 1) {
        animRef.current = requestAnimationFrame(animate);
      } else {
        setVisible(false);
      }
    };
    animRef.current = requestAnimationFrame(animate);
    return () => { if (animRef.current) cancelAnimationFrame(animRef.current); };
  }, [streak]);

  if (!visible || !data) return null;

  // Phase: 0-0.15 slam in, 0.15-0.7 hold, 0.7-1.0 fade out
  let opacity = 1, scale = data.scale, translateY = 0;
  if (anim < 0.15) {
    const t = anim / 0.15;
    opacity = t;
    scale = data.scale * easeOutBack(t);
    translateY = (1 - t) * -40;
  } else if (anim > 0.7) {
    const t = (anim - 0.7) / 0.3;
    opacity = 1 - t;
    translateY = t * 30;
  }

  return (
    <div
      style={{
        position: "fixed", top: "28%", left: "50%",
        transform: `translate(-50%, -50%) translateY(${translateY}px) scale(${scale})`,
        opacity, zIndex: 60, pointerEvents: "none", textAlign: "center",
      }}
    >
      <div
        style={{
          fontFamily: "'Courier New', monospace", fontWeight: "bold",
          fontSize: "42px", color: data.color, letterSpacing: "6px",
          textShadow: data.glow
            ? `0 0 20px ${data.color}, 0 0 40px ${data.color}, 0 0 60px ${data.color}`
            : `0 0 12px ${data.color}88, 0 0 30px ${data.color}44`,
          filter: data.glow ? "brightness(1.3)" : "none",
        }}
      >
        {data.label}
      </div>
      <div
        style={{
          fontSize: "14px", color: `${data.color}aa`, letterSpacing: "4px",
          fontFamily: "'Courier New', monospace", marginTop: "4px",
        }}
      >
        {streak} KILLS
      </div>
      {/* Horizontal slash lines */}
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: "12px", marginTop: "6px" }}>
        <div style={{ width: `${60 + streak * 12}px`, height: "2px", background: `linear-gradient(90deg, transparent, ${data.color}, transparent)` }} />
      </div>
    </div>
  );
}

// --- Round Countdown ---
function RoundCountdown({ count = null, roundNum = 1, label = "" }) {
  const [displayCount, setDisplayCount] = useState(null);
  const [phase, setPhase] = useState(0);
  const animRef = useRef(null);

  useEffect(() => {
    if (count === null) { setDisplayCount(null); return; }
    setDisplayCount(count);
    setPhase(0);
    let start = null;
    const duration = 900;
    const animate = (ts) => {
      if (!start) start = ts;
      const t = Math.min((ts - start) / duration, 1);
      setPhase(t);
      if (t < 1) animRef.current = requestAnimationFrame(animate);
    };
    animRef.current = requestAnimationFrame(animate);
    return () => { if (animRef.current) cancelAnimationFrame(animRef.current); };
  }, [count]);

  if (displayCount === null) return null;

  // Slam in, hold, fade
  let opacity = 1, scale = 1;
  if (phase < 0.1) {
    const t = phase / 0.1;
    scale = easeOutElastic(t) * 1.0;
    opacity = t;
  } else if (phase > 0.7) {
    const t = (phase - 0.7) / 0.3;
    opacity = 1 - t * 0.6;
    scale = 1 + t * 0.3;
  }

  const isFight = displayCount === 0;

  return (
    <div
      style={{
        position: "fixed", top: "40%", left: "50%",
        transform: `translate(-50%, -50%) scale(${scale})`,
        opacity, zIndex: 65, pointerEvents: "none", textAlign: "center",
      }}
    >
      {!isFight && (
        <div style={{
          fontFamily: "'Courier New', monospace", fontSize: "12px",
          color: "#ffaa00aa", letterSpacing: "4px", marginBottom: "8px",
        }}>
          {label || `ROUND ${roundNum}`}
        </div>
      )}
      <div
        style={{
          fontFamily: "'Courier New', monospace", fontWeight: "bold",
          fontSize: isFight ? "64px" : "96px",
          color: isFight ? "#ff4400" : "#ffffff",
          textShadow: isFight
            ? "0 0 30px #ff4400, 0 0 60px #ff220088"
            : "0 0 20px rgba(255,255,255,0.3)",
          letterSpacing: isFight ? "8px" : "0",
        }}
      >
        {isFight ? "FIGHT" : displayCount}
      </div>
      {/* Expanding ring behind the number */}
      <div
        style={{
          position: "absolute", top: "50%", left: "50%",
          width: `${80 + phase * 200}px`, height: `${80 + phase * 200}px`,
          transform: "translate(-50%, -50%)",
          border: `2px solid rgba(255,170,0,${0.4 * (1 - phase)})`,
          borderRadius: "50%",
        }}
      />
    </div>
  );
}

// --- Achievement / Medal Popup ---
const MEDAL_ICONS = {
  headshot: { icon: "⊙", label: "HEADSHOT", color: "#ff4400" },
  firstBlood: { icon: "◉", label: "FIRST BLOOD", color: "#ff0044" },
  revenge: { icon: "⟳", label: "REVENGE", color: "#cc44ff" },
  shutdown: { icon: "✹", label: "SHUTDOWN", color: "#ffaa00" },
  longshot: { icon: "—", label: "LONGSHOT", color: "#44ccff" },
  assist: { icon: "Φ", label: "ASSIST", color: "#66ff66" },
  savior: { icon: "○", label: "SAVIOR", color: "#44aaff" },
  execution: { icon: "•", label: "EXECUTION", color: "#ff2200" },
};

function MedalPopup({ medals = [] }) {
  return (
    <div
      style={{
        position: "fixed", left: "50%", top: "62%",
        transform: "translateX(-50%)", zIndex: 55, pointerEvents: "none",
        display: "flex", flexDirection: "column", alignItems: "center", gap: "4px",
      }}
    >
      {medals.map((m, i) => (
        <MedalEntry key={m.id || i} type={m.type} delay={i * 100} />
      ))}
    </div>
  );
}

function MedalEntry({ type, delay = 0 }) {
  const [anim, setAnim] = useState(0);
  const animRef = useRef(null);
  const medal = MEDAL_ICONS[type] || MEDAL_ICONS.headshot;

  useEffect(() => {
    const timeout = setTimeout(() => {
      let start = null;
      const duration = 2200;
      const animate = (ts) => {
        if (!start) start = ts;
        const t = Math.min((ts - start) / duration, 1);
        setAnim(t);
        if (t < 1) animRef.current = requestAnimationFrame(animate);
      };
      animRef.current = requestAnimationFrame(animate);
    }, delay);
    return () => {
      clearTimeout(timeout);
      if (animRef.current) cancelAnimationFrame(animRef.current);
    };
  }, [delay]);

  let opacity = 0, translateX = -40;
  if (anim < 0.12) {
    const t = anim / 0.12;
    opacity = t;
    translateX = -40 * (1 - easeOutBack(t));
  } else if (anim < 0.75) {
    opacity = 1;
    translateX = 0;
  } else {
    const t = (anim - 0.75) / 0.25;
    opacity = 1 - t;
    translateX = t * 20;
  }

  return (
    <div
      style={{
        opacity, transform: `translateX(${translateX}px)`,
        display: "flex", alignItems: "center", gap: "8px",
        fontFamily: "'Courier New', monospace",
        background: `rgba(0,0,0,0.6)`, padding: "4px 14px",
        border: `1px solid ${medal.color}44`,
        borderRadius: "2px",
      }}
    >
      <span style={{ fontSize: "18px", color: medal.color, filter: `drop-shadow(0 0 6px ${medal.color})` }}>
        {medal.icon}
      </span>
      <span style={{ fontSize: "11px", color: medal.color, letterSpacing: "2px", fontWeight: "bold" }}>
        {medal.label}
      </span>
    </div>
  );
}

// --- Ability Activation Flash ---
function AbilityFlash({ ability = null }) {
  const [active, setActive] = useState(false);
  const [anim, setAnim] = useState(0);
  const [info, setInfo] = useState(null);
  const animRef = useRef(null);

  const ABILITY_COLORS = {
    dash: "#00ccff",
    shield: "#4488ff",
    overclock: "#ffaa00",
    cloak: "#aa44ff",
    emp: "#ff4400",
    heal: "#44ff88",
    stasis: "#00ffcc",
    missiles: "#ff6600",
    default: "#ffffff",
  };

  useEffect(() => {
    if (!ability) return;
    setInfo(ability);
    setActive(true);
    setAnim(0);
    let start = null;
    const duration = 800;
    const animate = (ts) => {
      if (!start) start = ts;
      const t = Math.min((ts - start) / duration, 1);
      setAnim(t);
      if (t < 1) {
        animRef.current = requestAnimationFrame(animate);
      } else {
        setActive(false);
      }
    };
    animRef.current = requestAnimationFrame(animate);
    return () => { if (animRef.current) cancelAnimationFrame(animRef.current); };
  }, [ability]);

  if (!active || !info) return null;

  const color = ABILITY_COLORS[info.key] || ABILITY_COLORS.default;
  const edgeOpacity = (1 - anim) * 0.5;

  return (
    <div style={{ position: "fixed", inset: 0, pointerEvents: "none", zIndex: 48 }}>
      {/* Edge glow */}
      <div
        style={{
          position: "absolute", inset: 0,
          boxShadow: `inset 0 0 100px ${color}${Math.round(edgeOpacity * 255).toString(16).padStart(2, "0")}, inset 0 0 200px ${color}${Math.round(edgeOpacity * 128).toString(16).padStart(2, "0")}`,
        }}
      />
      {/* Center label */}
      <div
        style={{
          position: "absolute", top: "52%", left: "50%",
          transform: `translate(-50%, -50%) scale(${1 + anim * 0.3})`,
          opacity: Math.max(0, 1 - anim * 1.5),
          fontFamily: "'Courier New', monospace", fontSize: "14px",
          color, letterSpacing: "4px", fontWeight: "bold",
          textShadow: `0 0 10px ${color}`,
        }}
      >
        {(info.name || info.key || "").toUpperCase()} ACTIVE
      </div>
    </div>
  );
}

// --- Respawn Screen ---
function RespawnOverlay({ active = false, killer = "", countdown = 5 }) {
  const [anim, setAnim] = useState(0);
  const animRef = useRef(null);

  useEffect(() => {
    if (!active) { setAnim(0); return; }
    let start = null;
    const animate = (ts) => {
      if (!start) start = ts;
      const t = Math.min((ts - start) / 600, 1);
      setAnim(t);
      if (t < 1) animRef.current = requestAnimationFrame(animate);
    };
    animRef.current = requestAnimationFrame(animate);
    return () => { if (animRef.current) cancelAnimationFrame(animRef.current); };
  }, [active]);

  if (!active) return null;

  return (
    <div
      style={{
        position: "fixed", inset: 0, zIndex: 70, pointerEvents: "none",
        background: `rgba(0,0,0,${0.6 * anim})`,
        display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
      }}
    >
      <div
        style={{
          fontFamily: "'Courier New', monospace", color: "#ff2200",
          fontSize: "36px", fontWeight: "bold", letterSpacing: "6px",
          opacity: anim, transform: `scale(${0.8 + anim * 0.2})`,
          textShadow: "0 0 20px rgba(255,34,0,0.5)",
        }}
      >
        DESTROYED
      </div>
      {killer && (
        <div
          style={{
            fontFamily: "'Courier New', monospace", color: "#aaa",
            fontSize: "13px", marginTop: "12px", opacity: anim,
            letterSpacing: "2px",
          }}
        >
          by <span style={{ color: "#ff6666", fontWeight: "bold" }}>{killer}</span>
        </div>
      )}
      <div
        style={{
          fontFamily: "'Courier New', monospace", color: "#ffaa00",
          fontSize: "18px", marginTop: "24px", opacity: anim,
          letterSpacing: "3px",
        }}
      >
        RESPAWN IN {countdown}
      </div>
      {/* Animated ring */}
      <svg width="80" height="80" style={{ marginTop: "16px", opacity: anim }}>
        <circle cx="40" cy="40" r="35" fill="none" stroke="#ff220033" strokeWidth="3" />
        <circle
          cx="40" cy="40" r="35" fill="none" stroke="#ff4400" strokeWidth="3"
          strokeDasharray={`${220 * (countdown > 0 ? (1 - 1/countdown) : 0)} 220`}
          strokeLinecap="round"
          transform="rotate(-90 40 40)"
          style={{ transition: "stroke-dasharray 1s linear" }}
        />
        <text x="40" y="46" textAnchor="middle" fill="#ff4400" fontFamily="'Courier New', monospace" fontSize="20" fontWeight="bold">
          {countdown}
        </text>
      </svg>
    </div>
  );
}

// --- Round Transition Banner ---
function RoundBanner({ text = null, subtext = "" }) {
  const [visible, setVisible] = useState(false);
  const [anim, setAnim] = useState(0);
  const animRef = useRef(null);

  useEffect(() => {
    if (!text) { setVisible(false); return; }
    setVisible(true);
    setAnim(0);
    let start = null;
    const duration = 3000;
    const animate = (ts) => {
      if (!start) start = ts;
      const t = Math.min((ts - start) / duration, 1);
      setAnim(t);
      if (t < 1) {
        animRef.current = requestAnimationFrame(animate);
      } else {
        setVisible(false);
      }
    };
    animRef.current = requestAnimationFrame(animate);
    return () => { if (animRef.current) cancelAnimationFrame(animRef.current); };
  }, [text]);

  if (!visible) return null;

  let opacity = 1, barWidth = 0;
  if (anim < 0.1) {
    opacity = anim / 0.1;
    barWidth = anim / 0.1;
  } else if (anim < 0.8) {
    barWidth = 1;
  } else {
    const t = (anim - 0.8) / 0.2;
    opacity = 1 - t;
    barWidth = 1;
  }

  return (
    <div
      style={{
        position: "fixed", top: "38%", left: "50%",
        transform: "translate(-50%, -50%)", opacity,
        zIndex: 65, pointerEvents: "none", textAlign: "center",
      }}
    >
      {/* Top line */}
      <div style={{
        width: `${barWidth * 300}px`, height: "1px", margin: "0 auto 12px",
        background: "linear-gradient(90deg, transparent, #ffaa00, transparent)",
        transition: "width 0.3s",
      }} />
      <div style={{
        fontFamily: "'Courier New', monospace", fontSize: "28px",
        fontWeight: "bold", color: "#ffaa00", letterSpacing: "8px",
        textShadow: "0 0 20px rgba(255,170,0,0.4)",
      }}>
        {text}
      </div>
      {subtext && (
        <div style={{
          fontFamily: "'Courier New', monospace", fontSize: "12px",
          color: "#888", letterSpacing: "3px", marginTop: "6px",
        }}>
          {subtext}
        </div>
      )}
      {/* Bottom line */}
      <div style={{
        width: `${barWidth * 300}px`, height: "1px", margin: "12px auto 0",
        background: "linear-gradient(90deg, transparent, #ffaa00, transparent)",
        transition: "width 0.3s",
      }} />
    </div>
  );
}

// ============================================================================
// MAIN OVERLAY CONTROLLER + DEMO
// ============================================================================

// The event bus the game engine would call into
const GameEvents = {
  _listeners: {},
  on(event, fn) {
    (this._listeners[event] = this._listeners[event] || []).push(fn);
  },
  off(event, fn) {
    if (!this._listeners[event]) return;
    this._listeners[event] = this._listeners[event].filter((f) => f !== fn);
  },
  emit(event, data) {
    (this._listeners[event] || []).forEach((fn) => fn(data));
  },
};

export default function LSSOverlays() {
  // State for each overlay
  const [damage, setDamage] = useState({ intensity: 0, direction: null, key: 0 });
  const [streak, setStreak] = useState({ count: 0, key: 0 });
  const [countdown, setCountdown] = useState({ count: null, round: 1, label: "" });
  const [medals, setMedals] = useState([]);
  const [ability, setAbility] = useState(null);
  const [respawn, setRespawn] = useState({ active: false, killer: "", countdown: 5 });
  const [banner, setBanner] = useState({ text: null, subtext: "", key: 0 });

  // Demo mode: cycle through effects
  const [demoRunning, setDemoRunning] = useState(false);
  const [demoLog, setDemoLog] = useState([]);
  const medalIdRef = useRef(0);

  const addLog = useCallback((msg) => {
    setDemoLog((prev) => [...prev.slice(-8), msg]);
  }, []);

  const runDemo = useCallback(async () => {
    setDemoRunning(true);
    const wait = (ms) => new Promise((r) => setTimeout(r, ms));

    addLog(">>> Round start countdown");
    for (let i = 3; i >= 0; i--) {
      setCountdown({ count: i, round: 1, label: "ROUND 1" });
      await wait(1000);
    }
    setCountdown({ count: null, round: 1, label: "" });
    await wait(500);

    addLog(">>> Banner: ROUND 1 START");
    setBanner((p) => ({ text: "ROUND 1 START", subtext: "FLEET A vs FLEET B", key: p.key + 1 }));
    await wait(3500);

    addLog(">>> Taking damage (light)");
    setDamage((p) => ({ intensity: 0.3, direction: "left", key: p.key + 1 }));
    await wait(1200);

    addLog(">>> Ability: OVERCLOCK");
    setAbility({ key: "overclock", name: "Overclock", ts: Date.now() });
    await wait(1500);

    addLog(">>> Medal: FIRST BLOOD");
    const id1 = ++medalIdRef.current;
    setMedals([{ type: "firstBlood", id: id1 }]);
    await wait(800);
    addLog(">>> Kill streak: DOUBLE KILL");
    setStreak((p) => ({ count: 2, key: p.key + 1 }));
    await wait(2200);
    setMedals([]);

    addLog(">>> Taking heavy damage!");
    setDamage((p) => ({ intensity: 0.8, direction: "top", key: p.key + 1 }));
    await wait(1200);

    addLog(">>> Medal: HEADSHOT + TRIPLE KILL");
    const id2 = ++medalIdRef.current;
    const id3 = ++medalIdRef.current;
    setMedals([{ type: "headshot", id: id2 }, { type: "revenge", id: id3 }]);
    setStreak((p) => ({ count: 3, key: p.key + 1 }));
    await wait(2500);
    setMedals([]);

    addLog(">>> Ability: CLOAK");
    setAbility({ key: "cloak", name: "Cloak", ts: Date.now() });
    await wait(1500);

    addLog(">>> QUAD KILL + LONGSHOT");
    const id4 = ++medalIdRef.current;
    setMedals([{ type: "longshot", id: id4 }]);
    setStreak((p) => ({ count: 4, key: p.key + 1 }));
    await wait(2500);
    setMedals([]);

    addLog(">>> Ship destroyed! Respawn in 5...");
    setDamage((p) => ({ intensity: 1.0, direction: null, key: p.key + 1 }));
    await wait(600);
    setRespawn({ active: true, killer: "VIPER-7", countdown: 5 });
    for (let i = 4; i >= 1; i--) {
      await wait(1000);
      setRespawn({ active: true, killer: "VIPER-7", countdown: i });
    }
    await wait(1000);
    setRespawn({ active: false, killer: "", countdown: 0 });

    addLog(">>> Banner: ROUND OVER");
    setBanner((p) => ({ text: "ROUND OVER", subtext: "FLEET A WINS", key: p.key + 1 }));
    await wait(3500);

    addLog(">>> Demo complete!");
    setDemoRunning(false);
  }, [addLog]);

  return (
    <div style={{ position: "relative", width: "100vw", height: "100vh", background: "#08080f", overflow: "hidden" }}>
      {/* Fake starfield background */}
      <Starfield />

      {/* All overlay layers */}
      <DamageVignette intensity={damage.intensity} direction={damage.direction} key={`dmg-${damage.key}`} />
      <KillStreakAnnouncement streak={streak.count} key={`streak-${streak.key}`} />
      <RoundCountdown count={countdown.count} roundNum={countdown.round} label={countdown.label} />
      <MedalPopup medals={medals} />
      <AbilityFlash ability={ability} key={ability?.ts} />
      <RespawnOverlay active={respawn.active} killer={respawn.killer} countdown={respawn.countdown} />
      <RoundBanner text={banner.text} subtext={banner.subtext} key={`ban-${banner.key}`} />

      {/* Demo controls */}
      <div
        style={{
          position: "fixed", bottom: "24px", left: "50%", transform: "translateX(-50%)",
          zIndex: 100, display: "flex", flexDirection: "column", alignItems: "center", gap: "12px",
        }}
      >
        {/* Log */}
        <div
          style={{
            fontFamily: "'Courier New', monospace", fontSize: "10px",
            color: "#666", textAlign: "center", maxHeight: "100px",
            overflow: "hidden",
          }}
        >
          {demoLog.map((l, i) => (
            <div key={i} style={{ opacity: 0.4 + (i / demoLog.length) * 0.6 }}>{l}</div>
          ))}
        </div>

        {/* Buttons */}
        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", justifyContent: "center" }}>
          <DemoBtn label="RUN FULL DEMO" onClick={runDemo} disabled={demoRunning} accent />
          <DemoBtn label="DAMAGE" onClick={() => setDamage((p) => ({ intensity: 0.6, direction: ["top","left","right","bottom"][Math.random()*4|0], key: p.key+1 }))} />
          <DemoBtn label="KILL x2" onClick={() => setStreak((p) => ({ count: 2, key: p.key+1 }))} />
          <DemoBtn label="KILL x5" onClick={() => setStreak((p) => ({ count: 5, key: p.key+1 }))} />
          <DemoBtn label="GODLIKE" onClick={() => setStreak((p) => ({ count: 7, key: p.key+1 }))} />
          <DemoBtn label="MEDAL" onClick={() => { const id = ++medalIdRef.current; setMedals([{ type: Object.keys(MEDAL_ICONS)[Math.random()*8|0], id }]); setTimeout(() => setMedals([]), 2500); }} />
          <DemoBtn label="ABILITY" onClick={() => setAbility({ key: ["dash","shield","overclock","cloak","emp"][Math.random()*5|0], name: "Ability", ts: Date.now() })} />
          <DemoBtn label="DEATH" onClick={() => { setRespawn({ active: true, killer: "BOT-3", countdown: 3 }); setTimeout(() => setRespawn({ active: false, killer: "", countdown: 0 }), 4000); }} />
          <DemoBtn label="BANNER" onClick={() => setBanner((p) => ({ text: "ROUND OVER", subtext: "FLEET B WINS", key: p.key+1 }))} />
          <DemoBtn label="COUNTDOWN" onClick={async () => { for (let i=3;i>=0;i--) { setCountdown({ count: i, round: 1, label: "" }); await new Promise(r=>setTimeout(r,1000)); } setCountdown({ count: null, round: 1, label: "" }); }} />
        </div>
      </div>
    </div>
  );
}

function DemoBtn({ label, onClick, disabled = false, accent = false }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        fontFamily: "'Courier New', monospace", fontSize: "10px",
        padding: "6px 14px", cursor: disabled ? "not-allowed" : "pointer",
        background: accent ? "rgba(255,170,0,0.15)" : "rgba(40,40,60,0.9)",
        border: `1px solid ${accent ? "#ffaa00" : "rgba(80,80,120,0.5)"}`,
        color: accent ? "#ffaa00" : "#aaa",
        letterSpacing: "1px", opacity: disabled ? 0.4 : 1,
        transition: "all 0.15s",
      }}
    >
      {label}
    </button>
  );
}

// Fake starfield so the demo doesn't look empty
function Starfield() {
  const canvasRef = useRef(null);
  useEffect(() => {
    const c = canvasRef.current;
    if (!c) return;
    c.width = window.innerWidth;
    c.height = window.innerHeight;
    const ctx = c.getContext("2d");
    ctx.fillStyle = "#08080f";
    ctx.fillRect(0, 0, c.width, c.height);
    for (let i = 0; i < 400; i++) {
      const x = Math.random() * c.width;
      const y = Math.random() * c.height;
      const r = Math.random() * 1.5;
      const a = 0.2 + Math.random() * 0.6;
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(200,210,255,${a})`;
      ctx.fill();
    }
    // A few brighter ones
    for (let i = 0; i < 20; i++) {
      const x = Math.random() * c.width;
      const y = Math.random() * c.height;
      ctx.beginPath();
      ctx.arc(x, y, 1.5, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255,240,200,0.8)`;
      ctx.fill();
    }
  }, []);
  return <canvas ref={canvasRef} style={{ position: "absolute", inset: 0 }} />;
}
