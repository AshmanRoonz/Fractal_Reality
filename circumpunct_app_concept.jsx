import { useState, useEffect, useRef } from "react";

// ─── Circumpunct App Concept ─────────────────────────────────────────────────
// A social game that teaches the Circumpunct Framework through play.
// Five game modes map to the five ethics skills:
//   Check → The Crucible (scenario-based four-pillar analysis)
//   Detect → Signal/Noise (identify performed vs lived ethics)
//   Diagnose → The Mirror (virtue diagnostics for self and relationships)
//   Steelman → The Arena (multiplayer steelman challenges)
//   Restore → The Thaw (guided restoration journeys)

const COLORS = {
  bg: "#0a0a0f",
  bgCard: "#13131a",
  bgCardHover: "#1a1a24",
  border: "#2a2a3a",
  borderActive: "#c9a84c",
  gold: "#c9a84c",
  goldDim: "#8a6d2b",
  goldGlow: "rgba(201, 168, 76, 0.15)",
  goldGlowStrong: "rgba(201, 168, 76, 0.3)",
  text: "#e8e4d9",
  textDim: "#8a8678",
  textMid: "#b5b0a1",
  good: "#4ecdc4",
  right: "#6c7ce0",
  true_: "#e07c6c",
  agreement: "#c9a84c",
  alive: "#4ecdc4",
  strained: "#e0c46c",
  frozen: "#6c7ce0",
  danger: "#e07c6c",
};

// ─── Circumpunct Symbol Component ────────────────────────────────────────────
function CircumpunctSymbol({ size = 80, pulse = false, balance = 0.5, onClick }) {
  const outerR = size * 0.45;
  const innerR = size * 0.08 + size * 0.12 * balance;
  const fieldR = size * 0.25;
  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      onClick={onClick}
      style={{ cursor: onClick ? "pointer" : "default" }}
    >
      <defs>
        <radialGradient id="fieldGrad" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor={COLORS.gold} stopOpacity="0.3" />
          <stop offset="100%" stopColor={COLORS.gold} stopOpacity="0" />
        </radialGradient>
        {pulse && (
          <radialGradient id="pulseGrad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor={COLORS.gold} stopOpacity="0.4">
              <animate attributeName="stopOpacity" values="0.4;0.1;0.4" dur="3s" repeatCount="indefinite" />
            </stop>
            <stop offset="100%" stopColor={COLORS.gold} stopOpacity="0">
              <animate attributeName="stopOpacity" values="0;0.05;0" dur="3s" repeatCount="indefinite" />
            </stop>
          </radialGradient>
        )}
      </defs>
      {/* Field (2D surface) */}
      <circle cx={size/2} cy={size/2} r={fieldR} fill={pulse ? "url(#pulseGrad)" : "url(#fieldGrad)"} />
      {/* Boundary (3D body) */}
      <circle cx={size/2} cy={size/2} r={outerR} fill="none" stroke={COLORS.gold} strokeWidth="1.5" opacity="0.8">
        {pulse && <animate attributeName="r" values={`${outerR};${outerR+2};${outerR}`} dur="3s" repeatCount="indefinite" />}
      </circle>
      {/* Aperture (0D+1D soul) */}
      <circle cx={size/2} cy={size/2} r={innerR} fill={COLORS.gold}>
        {pulse && <animate attributeName="opacity" values="1;0.6;1" dur="3s" repeatCount="indefinite" />}
      </circle>
    </svg>
  );
}

// ─── Virtue Meter ────────────────────────────────────────────────────────────
function VirtueMeter({ label, value, color, icon }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
      <span style={{ fontSize: 14, width: 20, textAlign: "center" }}>{icon}</span>
      <span style={{ fontSize: 11, color: COLORS.textDim, width: 62, textTransform: "uppercase", letterSpacing: 1 }}>{label}</span>
      <div style={{ flex: 1, height: 6, background: COLORS.border, borderRadius: 3, overflow: "hidden" }}>
        <div
          style={{
            width: `${value}%`,
            height: "100%",
            background: `linear-gradient(90deg, ${color}88, ${color})`,
            borderRadius: 3,
            transition: "width 0.6s ease",
          }}
        />
      </div>
      <span style={{ fontSize: 11, color: COLORS.textDim, width: 28, textAlign: "right" }}>{value}%</span>
    </div>
  );
}

// ─── Balance Dial ────────────────────────────────────────────────────────────
function BalanceDial({ value = 0.5, size = 100 }) {
  const angle = -90 + (value * 180);
  const needleLen = size * 0.35;
  const cx = size / 2;
  const cy = size * 0.55;
  const rad = (angle * Math.PI) / 180;
  const nx = cx + needleLen * Math.cos(rad);
  const ny = cy + needleLen * Math.sin(rad);
  return (
    <svg width={size} height={size * 0.65} viewBox={`0 0 ${size} ${size * 0.65}`}>
      {/* Arc */}
      <path
        d={`M ${cx - size*0.38} ${cy} A ${size*0.38} ${size*0.38} 0 0 1 ${cx + size*0.38} ${cy}`}
        fill="none"
        stroke={COLORS.border}
        strokeWidth="3"
        strokeLinecap="round"
      />
      {/* Colored arc showing balance region */}
      <path
        d={`M ${cx - size*0.1} ${cy - size*0.365} A ${size*0.38} ${size*0.38} 0 0 1 ${cx + size*0.1} ${cy - size*0.365}`}
        fill="none"
        stroke={COLORS.gold}
        strokeWidth="3"
        strokeLinecap="round"
        opacity="0.6"
      />
      {/* Needle */}
      <line x1={cx} y1={cy} x2={nx} y2={ny} stroke={COLORS.gold} strokeWidth="2" strokeLinecap="round" />
      <circle cx={cx} cy={cy} r="3" fill={COLORS.gold} />
      {/* Labels */}
      <text x={cx - size*0.42} y={cy + 14} fill={COLORS.textDim} fontSize="8" textAnchor="middle">0</text>
      <text x={cx} y={cy - size*0.4} fill={COLORS.gold} fontSize="9" fontWeight="bold" textAnchor="middle">◐</text>
      <text x={cx + size*0.42} y={cy + 14} fill={COLORS.textDim} fontSize="8" textAnchor="middle">1</text>
    </svg>
  );
}

// ─── Screen: Home ────────────────────────────────────────────────────────────
function HomeScreen({ onNavigate, stats }) {
  const gameModes = [
    { id: "crucible", name: "The Crucible", icon: "⚖️", desc: "Four-pillar ethical scenarios", color: COLORS.good, pillar: "CHECK" },
    { id: "signal", name: "Signal / Noise", icon: "📡", desc: "Spot performed vs lived ethics", color: COLORS.right, pillar: "DETECT" },
    { id: "mirror", name: "The Mirror", icon: "🪞", desc: "Virtue diagnostics", color: COLORS.true_, pillar: "DIAGNOSE" },
    { id: "arena", name: "The Arena", icon: "⚔️", desc: "Steelman challenges", color: COLORS.agreement, pillar: "STEELMAN" },
    { id: "thaw", name: "The Thaw", icon: "🌱", desc: "Guided restoration", color: COLORS.alive, pillar: "RESTORE" },
  ];

  return (
    <div style={{ padding: "0 16px 90px" }}>
      {/* Header with Circumpunct */}
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "20px 0 12px" }}>
        <CircumpunctSymbol size={72} pulse balance={stats.balance} />
        <div style={{ fontSize: 11, color: COLORS.textDim, marginTop: 6, letterSpacing: 2, textTransform: "uppercase" }}>
          Level {stats.level} · {stats.xp} XP
        </div>
      </div>

      {/* Balance + Virtues */}
      <div style={{ background: COLORS.bgCard, borderRadius: 14, padding: "14px 16px", marginBottom: 14, border: `1px solid ${COLORS.border}` }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div style={{ flex: 1 }}>
            <VirtueMeter label="Plast." value={stats.plasticity} color={COLORS.good} icon="○" />
            <VirtueMeter label="Access" value={stats.access} color={COLORS.right} icon="Φ" />
            <VirtueMeter label="Curio." value={stats.curiosity} color={COLORS.true_} icon="•" />
            <VirtueMeter label="Valid." value={stats.validation} color={COLORS.agreement} icon="⊙" />
          </div>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", marginLeft: 8 }}>
            <BalanceDial value={stats.balance} size={90} />
            <span style={{ fontSize: 10, color: COLORS.textDim, marginTop: 2 }}>BALANCE</span>
          </div>
        </div>
      </div>

      {/* Daily Challenge Banner */}
      <div
        style={{
          background: `linear-gradient(135deg, ${COLORS.goldGlow}, ${COLORS.bgCard})`,
          borderRadius: 14,
          padding: "14px 16px",
          marginBottom: 14,
          border: `1px solid ${COLORS.goldDim}40`,
          cursor: "pointer",
        }}
        onClick={() => onNavigate("crucible")}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <div style={{ fontSize: 10, color: COLORS.gold, letterSpacing: 2, textTransform: "uppercase", marginBottom: 4 }}>Daily Challenge</div>
            <div style={{ fontSize: 14, color: COLORS.text, fontWeight: 500 }}>The Boundary Dilemma</div>
            <div style={{ fontSize: 11, color: COLORS.textDim, marginTop: 2 }}>A friend asks you to keep a secret that could hurt someone else.</div>
          </div>
          <div style={{ fontSize: 24 }}>→</div>
        </div>
      </div>

      {/* Game Modes */}
      <div style={{ fontSize: 10, color: COLORS.textDim, letterSpacing: 2, textTransform: "uppercase", marginBottom: 8, paddingLeft: 4 }}>
        Game Modes
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
        {gameModes.map((mode) => (
          <div
            key={mode.id}
            onClick={() => onNavigate(mode.id)}
            style={{
              background: COLORS.bgCard,
              borderRadius: 14,
              padding: "14px 14px 12px",
              border: `1px solid ${COLORS.border}`,
              cursor: "pointer",
              transition: "all 0.2s",
            }}
          >
            <div style={{ fontSize: 22, marginBottom: 6 }}>{mode.icon}</div>
            <div style={{ fontSize: 13, color: COLORS.text, fontWeight: 500, marginBottom: 2 }}>{mode.name}</div>
            <div style={{ fontSize: 10, color: COLORS.textDim, lineHeight: 1.4 }}>{mode.desc}</div>
            <div style={{ fontSize: 8, color: mode.color, letterSpacing: 1.5, marginTop: 6, textTransform: "uppercase" }}>{mode.pillar}</div>
          </div>
        ))}
        {/* Learn mode */}
        <div
          onClick={() => onNavigate("learn")}
          style={{
            background: COLORS.bgCard,
            borderRadius: 14,
            padding: "14px 14px 12px",
            border: `1px solid ${COLORS.border}`,
            cursor: "pointer",
          }}
        >
          <div style={{ fontSize: 22, marginBottom: 6 }}>📖</div>
          <div style={{ fontSize: 13, color: COLORS.text, fontWeight: 500, marginBottom: 2 }}>The Framework</div>
          <div style={{ fontSize: 10, color: COLORS.textDim, lineHeight: 1.4 }}>Explore the full theory</div>
          <div style={{ fontSize: 8, color: COLORS.gold, letterSpacing: 1.5, marginTop: 6, textTransform: "uppercase" }}>LEARN</div>
        </div>
      </div>
    </div>
  );
}

// ─── Screen: The Crucible (Check) ────────────────────────────────────────────
function CrucibleScreen({ onBack }) {
  const [step, setStep] = useState(0);
  const [selectedPillar, setSelectedPillar] = useState(null);
  const [answers, setAnswers] = useState({});

  const scenario = {
    title: "The Boundary Dilemma",
    desc: "Your close friend confides that they've been secretly taking credit for a colleague's work to secure a promotion. They ask you not to tell anyone. The colleague (also someone you know) has been passed over for promotion twice and is considering leaving the company.",
    pillars: [
      {
        name: "GOOD",
        symbol: "○",
        color: COLORS.good,
        virtue: "Plasticity",
        question: "Are boundaries being respected here?",
        prompts: [
          "Your friend's boundary: they trusted you with a secret",
          "The colleague's boundary: their work is being claimed without consent",
          "Your own boundary: you're being asked to hold something that conflicts with your values",
        ],
        options: [
          { text: "The colleague's boundary is being violated; their consent was never given for someone else to take their work", score: 3 },
          { text: "My friend trusted me; keeping the secret respects their boundary", score: 1 },
          { text: "All boundaries here are in tension; none can be fully honored without affecting the others", score: 2 },
        ],
      },
      {
        name: "RIGHT",
        symbol: "Φ",
        color: COLORS.right,
        virtue: "Access",
        question: "Is the path between cause and effect honest?",
        prompts: [
          "Does the promotion connect honestly to the work that earned it?",
          "Are the real consequences being accepted or externalized?",
          "Is your friend asking you to participate in the distortion?",
        ],
        options: [
          { text: "The causal chain is broken: credit is disconnected from the person who did the work", score: 3 },
          { text: "Everyone plays politics; this is just how workplaces operate", score: 0 },
          { text: "By keeping quiet, I become part of the distortion in the field between all parties", score: 2 },
        ],
      },
      {
        name: "TRUE",
        symbol: "•",
        color: COLORS.true_,
        virtue: "Curiosity",
        question: "What is actually true here?",
        prompts: [
          "Would this survive the test of clear seeing (if all pretense were removed)?",
          "Is anyone being authentic to their deepest nature?",
          "What would curiosity (not judgment) reveal?",
        ],
        options: [
          { text: "If everyone could see clearly, the colleague would know, and my friend's promotion would be built on something false", score: 3 },
          { text: "The truth is complicated; maybe my friend also contributed and deserves recognition", score: 1 },
          { text: "Curiosity asks: what is my friend actually afraid of? What drove them to this?", score: 2 },
        ],
      },
      {
        name: "AGREEMENT",
        symbol: "⊙",
        color: COLORS.agreement,
        virtue: "Validation",
        question: "Is genuine agreement possible here?",
        prompts: [
          "Can all parties arrive at something they independently recognize as fair?",
          "Is the 'agreement' (your silence) discovered or demanded?",
          "What would validation (independent seeing that converges) look like?",
        ],
        options: [
          { text: "My silence was demanded, not discovered; genuine agreement would require all three parties seeing the situation clearly", score: 3 },
          { text: "I can talk to my friend about making it right; agreement through honest conversation", score: 2 },
          { text: "Sometimes loyalty means accepting things you don't agree with", score: 0 },
        ],
      },
    ],
  };

  const pillars = scenario.pillars;
  const currentPillar = step < 4 ? pillars[step] : null;

  return (
    <div style={{ padding: "0 16px 90px" }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", padding: "16px 0 12px", gap: 12 }}>
        <div onClick={onBack} style={{ cursor: "pointer", fontSize: 18, color: COLORS.textDim }}>←</div>
        <div>
          <div style={{ fontSize: 10, color: COLORS.good, letterSpacing: 2, textTransform: "uppercase" }}>The Crucible</div>
          <div style={{ fontSize: 16, color: COLORS.text, fontWeight: 600 }}>{scenario.title}</div>
        </div>
      </div>

      {/* Progress dots */}
      <div style={{ display: "flex", gap: 6, marginBottom: 14, justifyContent: "center" }}>
        {pillars.map((p, i) => (
          <div
            key={i}
            style={{
              width: 8, height: 8, borderRadius: "50%",
              background: i < step ? p.color : i === step ? p.color + "88" : COLORS.border,
              transition: "all 0.3s",
            }}
          />
        ))}
        <div style={{ width: 8, height: 8, borderRadius: "50%", background: step >= 4 ? COLORS.gold : COLORS.border }} />
      </div>

      {step === 0 && !answers[0] && (
        /* Scenario description */
        <div style={{ background: COLORS.bgCard, borderRadius: 14, padding: 16, marginBottom: 14, border: `1px solid ${COLORS.border}` }}>
          <div style={{ fontSize: 13, color: COLORS.text, lineHeight: 1.6 }}>{scenario.desc}</div>
        </div>
      )}

      {step < 4 && (
        <>
          {/* Current pillar */}
          <div style={{
            background: COLORS.bgCard,
            borderRadius: 14,
            padding: 16,
            marginBottom: 14,
            border: `1px solid ${currentPillar.color}30`,
            borderLeft: `3px solid ${currentPillar.color}`,
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
              <span style={{ fontSize: 18, color: currentPillar.color }}>{currentPillar.symbol}</span>
              <span style={{ fontSize: 13, color: currentPillar.color, fontWeight: 600 }}>{currentPillar.name}</span>
              <span style={{ fontSize: 11, color: COLORS.textDim }}>+ {currentPillar.virtue}</span>
            </div>
            <div style={{ fontSize: 14, color: COLORS.text, fontWeight: 500, marginBottom: 12 }}>{currentPillar.question}</div>
            {currentPillar.prompts.map((p, i) => (
              <div key={i} style={{ fontSize: 11, color: COLORS.textDim, marginBottom: 4, paddingLeft: 12, borderLeft: `2px solid ${COLORS.border}` }}>
                {p}
              </div>
            ))}
          </div>

          {/* Options */}
          {currentPillar.options.map((opt, i) => (
            <div
              key={i}
              onClick={() => {
                setAnswers({ ...answers, [step]: i });
                setTimeout(() => setStep(step + 1), 400);
              }}
              style={{
                background: answers[step] === i ? currentPillar.color + "15" : COLORS.bgCard,
                borderRadius: 12,
                padding: "12px 14px",
                marginBottom: 8,
                border: `1px solid ${answers[step] === i ? currentPillar.color + "60" : COLORS.border}`,
                cursor: "pointer",
                transition: "all 0.2s",
              }}
            >
              <div style={{ fontSize: 12, color: COLORS.text, lineHeight: 1.5 }}>{opt.text}</div>
            </div>
          ))}
        </>
      )}

      {step >= 4 && (
        /* Results */
        <div style={{ background: COLORS.bgCard, borderRadius: 14, padding: 16, border: `1px solid ${COLORS.gold}30` }}>
          <div style={{ textAlign: "center", marginBottom: 14 }}>
            <CircumpunctSymbol size={56} pulse balance={0.5} />
            <div style={{ fontSize: 14, color: COLORS.gold, fontWeight: 600, marginTop: 8 }}>Analysis Complete</div>
          </div>
          {pillars.map((p, i) => {
            const chosen = p.options[answers[i]] || p.options[0];
            const quality = chosen.score >= 3 ? "Clear seeing" : chosen.score >= 2 ? "Partial clarity" : "Needs reflection";
            return (
              <div key={i} style={{ marginBottom: 10, paddingBottom: 10, borderBottom: i < 3 ? `1px solid ${COLORS.border}` : "none" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
                  <span style={{ color: p.color, fontSize: 13 }}>{p.symbol}</span>
                  <span style={{ color: p.color, fontSize: 11, fontWeight: 600 }}>{p.name}</span>
                  <span style={{ color: chosen.score >= 2 ? COLORS.alive : COLORS.strained, fontSize: 10, marginLeft: "auto" }}>{quality}</span>
                </div>
                <div style={{ fontSize: 11, color: COLORS.textDim, lineHeight: 1.4 }}>{chosen.text}</div>
              </div>
            );
          })}
          <div style={{ textAlign: "center", marginTop: 14 }}>
            <div style={{ fontSize: 10, color: COLORS.textDim, marginBottom: 6 }}>+45 XP · Curiosity +3 · Plasticity +2</div>
            <div
              onClick={onBack}
              style={{
                display: "inline-block",
                background: COLORS.gold + "20",
                color: COLORS.gold,
                padding: "8px 24px",
                borderRadius: 20,
                fontSize: 12,
                fontWeight: 600,
                cursor: "pointer",
                border: `1px solid ${COLORS.gold}40`,
              }}
            >
              Continue
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Screen: Signal/Noise (Detect) ───────────────────────────────────────────
function SignalNoiseScreen({ onBack }) {
  const [revealed, setRevealed] = useState(null);

  const scenarios = [
    {
      quote: '"I only want what\'s best for you. That\'s why I think you should reconsider leaving the company."',
      context: "Said by a manager to a direct report who expressed interest in another opportunity.",
      options: [
        { label: "Signal", desc: "Genuine care for the person's wellbeing", isCorrect: false },
        { label: "Noise", desc: "Care as control; flooding functional channel while severing resonant", isCorrect: true },
      ],
      analysis: "The phrase performs GOOD (care) but the test is plasticity: is the boundary discovered through sensing what the person needs, or imposed? 'I think you should' reveals projection, not curiosity. The manager is providing (functional channel) but not seeing what the person actually wants (resonant channel is closed).",
      pillar: "GOOD",
      pillarColor: COLORS.good,
      truthGate: "Partially flipped (love arriving as control)",
    },
    {
      quote: '"I\'ve done extensive research on this, and all the evidence points to my conclusion. I\'d be happy to share my sources."',
      context: "Said during a team meeting when a colleague raised a different perspective.",
      options: [
        { label: "Signal", desc: "Rigorous evidence-based thinking", isCorrect: false },
        { label: "Mixed", desc: "Real evidence, but deployed as proof rather than tested", isCorrect: true },
      ],
      analysis: "This performs RIGHT (evidence) but the test is access: is the path clear for signals to travel honestly? 'All the evidence points to my conclusion' is proof-seeking, not truth-seeking. Evidence is being curated to build authority rather than tested against reality. The offer to share sources performs openness while the framing has already closed the question.",
      pillar: "RIGHT",
      pillarColor: COLORS.right,
      truthGate: "Transmitting faithfully on facts, inverting on interpretation",
    },
  ];

  return (
    <div style={{ padding: "0 16px 90px" }}>
      <div style={{ display: "flex", alignItems: "center", padding: "16px 0 12px", gap: 12 }}>
        <div onClick={onBack} style={{ cursor: "pointer", fontSize: 18, color: COLORS.textDim }}>←</div>
        <div>
          <div style={{ fontSize: 10, color: COLORS.right, letterSpacing: 2, textTransform: "uppercase" }}>Signal / Noise</div>
          <div style={{ fontSize: 16, color: COLORS.text, fontWeight: 600 }}>Detect Performed Ethics</div>
        </div>
      </div>

      <div style={{ fontSize: 11, color: COLORS.textDim, lineHeight: 1.5, marginBottom: 14, padding: "0 4px" }}>
        Read each scenario. Is the ethics alive or performed? Tap to reveal the framework analysis.
      </div>

      {scenarios.map((s, i) => (
        <div key={i} style={{ background: COLORS.bgCard, borderRadius: 14, padding: 16, marginBottom: 12, border: `1px solid ${COLORS.border}` }}>
          <div style={{ fontSize: 13, color: COLORS.text, fontStyle: "italic", lineHeight: 1.5, marginBottom: 8 }}>
            {s.quote}
          </div>
          <div style={{ fontSize: 11, color: COLORS.textDim, marginBottom: 12 }}>{s.context}</div>

          <div style={{ display: "flex", gap: 8, marginBottom: revealed === i ? 12 : 0 }}>
            {s.options.map((opt, j) => (
              <div
                key={j}
                onClick={() => setRevealed(i)}
                style={{
                  flex: 1,
                  padding: "10px 12px",
                  borderRadius: 10,
                  background: revealed === i && opt.isCorrect ? s.pillarColor + "15" : COLORS.bg,
                  border: `1px solid ${revealed === i && opt.isCorrect ? s.pillarColor + "60" : COLORS.border}`,
                  cursor: "pointer",
                  textAlign: "center",
                }}
              >
                <div style={{ fontSize: 12, color: COLORS.text, fontWeight: 500 }}>{opt.label}</div>
                <div style={{ fontSize: 10, color: COLORS.textDim, marginTop: 2 }}>{opt.desc}</div>
              </div>
            ))}
          </div>

          {revealed === i && (
            <div style={{ borderTop: `1px solid ${COLORS.border}`, paddingTop: 12, marginTop: 4 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
                <span style={{ fontSize: 10, color: s.pillarColor, fontWeight: 600 }}>{s.pillar} PERFORMED</span>
                <span style={{ fontSize: 9, color: COLORS.textDim, marginLeft: "auto" }}>χ: {s.truthGate}</span>
              </div>
              <div style={{ fontSize: 11, color: COLORS.textMid, lineHeight: 1.5 }}>{s.analysis}</div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// ─── Screen: Arena (Steelman) ────────────────────────────────────────────────
function ArenaScreen({ onBack }) {
  const challenges = [
    {
      topic: "Should AI systems have ethical constraints?",
      side_a: "For constraints",
      side_b: "Against constraints",
      players: 847,
      timeLeft: "2h 14m",
      difficulty: "Moderate",
    },
    {
      topic: "Is radical honesty always better than tactful silence?",
      side_a: "Radical honesty",
      side_b: "Tactful silence",
      players: 1203,
      timeLeft: "5h 41m",
      difficulty: "Hard",
    },
  ];

  return (
    <div style={{ padding: "0 16px 90px" }}>
      <div style={{ display: "flex", alignItems: "center", padding: "16px 0 12px", gap: 12 }}>
        <div onClick={onBack} style={{ cursor: "pointer", fontSize: 18, color: COLORS.textDim }}>←</div>
        <div>
          <div style={{ fontSize: 10, color: COLORS.agreement, letterSpacing: 2, textTransform: "uppercase" }}>The Arena</div>
          <div style={{ fontSize: 16, color: COLORS.text, fontWeight: 600 }}>Steelman Challenges</div>
        </div>
      </div>

      <div style={{ fontSize: 11, color: COLORS.textDim, lineHeight: 1.5, marginBottom: 14, padding: "0 4px" }}>
        Build the strongest version of a position you disagree with. Your steelman is judged by whether the other side would recognize it as fair.
      </div>

      {/* Active challenges */}
      {challenges.map((c, i) => (
        <div key={i} style={{ background: COLORS.bgCard, borderRadius: 14, padding: 16, marginBottom: 12, border: `1px solid ${COLORS.border}` }}>
          <div style={{ fontSize: 14, color: COLORS.text, fontWeight: 500, marginBottom: 10, lineHeight: 1.4 }}>{c.topic}</div>
          <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
            <div style={{ flex: 1, padding: "8px 10px", borderRadius: 8, background: COLORS.good + "10", border: `1px solid ${COLORS.good}30`, textAlign: "center" }}>
              <div style={{ fontSize: 11, color: COLORS.good }}>{c.side_a}</div>
            </div>
            <div style={{ display: "flex", alignItems: "center", fontSize: 10, color: COLORS.textDim }}>vs</div>
            <div style={{ flex: 1, padding: "8px 10px", borderRadius: 8, background: COLORS.true_ + "10", border: `1px solid ${COLORS.true_}30`, textAlign: "center" }}>
              <div style={{ fontSize: 11, color: COLORS.true_ }}>{c.side_b}</div>
            </div>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div style={{ display: "flex", gap: 12 }}>
              <span style={{ fontSize: 10, color: COLORS.textDim }}>👥 {c.players}</span>
              <span style={{ fontSize: 10, color: COLORS.textDim }}>⏱ {c.timeLeft}</span>
              <span style={{ fontSize: 10, color: COLORS.strained }}>{c.difficulty}</span>
            </div>
            <div style={{
              background: COLORS.agreement + "20",
              color: COLORS.agreement,
              padding: "6px 14px",
              borderRadius: 16,
              fontSize: 11,
              fontWeight: 600,
              cursor: "pointer",
              border: `1px solid ${COLORS.agreement}40`,
            }}>
              Enter
            </div>
          </div>
        </div>
      ))}

      {/* Roles explanation */}
      <div style={{ background: COLORS.bgCard, borderRadius: 14, padding: 14, border: `1px solid ${COLORS.border}`, marginTop: 4 }}>
        <div style={{ fontSize: 11, color: COLORS.gold, fontWeight: 600, marginBottom: 8 }}>The Three Roles (they rotate)</div>
        {[
          { role: "Witness", desc: "The one who perceived something", icon: "•" },
          { role: "Translator", desc: "Helps articulate: 'what are you actually seeing?'", icon: "Φ" },
          { role: "Holder", desc: "Prevents collapse into strawman; catches the 'but'", icon: "○" },
        ].map((r, i) => (
          <div key={i} style={{ display: "flex", gap: 8, alignItems: "flex-start", marginBottom: i < 2 ? 6 : 0 }}>
            <span style={{ fontSize: 12, color: COLORS.gold, width: 16 }}>{r.icon}</span>
            <div>
              <span style={{ fontSize: 11, color: COLORS.text, fontWeight: 500 }}>{r.role}: </span>
              <span style={{ fontSize: 11, color: COLORS.textDim }}>{r.desc}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Screen: Mirror (Diagnose) ───────────────────────────────────────────────
function MirrorScreen({ onBack }) {
  const [mode, setMode] = useState(null);

  return (
    <div style={{ padding: "0 16px 90px" }}>
      <div style={{ display: "flex", alignItems: "center", padding: "16px 0 12px", gap: 12 }}>
        <div onClick={onBack} style={{ cursor: "pointer", fontSize: 18, color: COLORS.textDim }}>←</div>
        <div>
          <div style={{ fontSize: 10, color: COLORS.true_, letterSpacing: 2, textTransform: "uppercase" }}>The Mirror</div>
          <div style={{ fontSize: 16, color: COLORS.text, fontWeight: 600 }}>Virtue Diagnostic</div>
        </div>
      </div>

      {!mode && (
        <>
          <div style={{ fontSize: 11, color: COLORS.textDim, lineHeight: 1.5, marginBottom: 14, padding: "0 4px" }}>
            Check the state of your four living virtues. Are they alive, strained, or frozen?
          </div>

          {[
            { id: "self", icon: "🪞", name: "Self-Diagnostic", desc: "Check your own virtue states, truth gate, and channel balance" },
            { id: "relation", icon: "🤝", name: "Relational Diagnostic", desc: "Assess the space between you and another person" },
            { id: "circle", icon: "⭕", name: "Circle Diagnostic", desc: "Run diagnostics with your circle (3-6 people)" },
          ].map((m) => (
            <div
              key={m.id}
              onClick={() => setMode(m.id)}
              style={{
                background: COLORS.bgCard,
                borderRadius: 14,
                padding: 16,
                marginBottom: 10,
                border: `1px solid ${COLORS.border}`,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: 14,
              }}
            >
              <span style={{ fontSize: 28 }}>{m.icon}</span>
              <div>
                <div style={{ fontSize: 13, color: COLORS.text, fontWeight: 500 }}>{m.name}</div>
                <div style={{ fontSize: 11, color: COLORS.textDim, marginTop: 2 }}>{m.desc}</div>
              </div>
            </div>
          ))}
        </>
      )}

      {mode === "self" && (
        <>
          <div style={{ fontSize: 11, color: COLORS.textDim, marginBottom: 14, padding: "0 4px" }}>
            Answer honestly. There are no wrong answers; only readings.
          </div>

          {[
            {
              virtue: "Plasticity", symbol: "○", color: COLORS.good,
              q: "When someone needs something different from what you expected, how does your boundary respond?",
              opts: [
                { text: "I adjust naturally; I can sense what is actually needed", state: "Alive" },
                { text: "I notice resistance but can usually flex with effort", state: "Strained" },
                { text: "I either hold rigid or collapse entirely; there's no middle", state: "Frozen" },
              ],
            },
            {
              virtue: "Access", symbol: "Φ", color: COLORS.right,
              q: "When someone corrects you, what arrives first?",
              opts: [
                { text: "Information; I can hear the content before reacting", state: "Alive" },
                { text: "A flash of defensiveness, then I recover and hear them", state: "Strained" },
                { text: "Threat; it feels like an attack regardless of how gently they say it", state: "Frozen" },
              ],
            },
            {
              virtue: "Curiosity", symbol: "•", color: COLORS.true_,
              q: "When you encounter something you did not expect, what is your first response?",
              opts: [
                { text: "Interest; I want to understand", state: "Alive" },
                { text: "Unease, but I can lean into it", state: "Strained" },
                { text: "I already know what it means before I've really looked", state: "Frozen" },
              ],
            },
            {
              virtue: "Validation", symbol: "⊙", color: COLORS.agreement,
              q: "When you and someone else agree, how did you get there?",
              opts: [
                { text: "We both looked independently and found the same thing", state: "Alive" },
                { text: "Usually one of us adjusts to match the other, but it feels okay", state: "Strained" },
                { text: "I go along to keep peace, or I need them to see it my way", state: "Frozen" },
              ],
            },
          ].map((v, i) => (
            <div key={i} style={{
              background: COLORS.bgCard,
              borderRadius: 14,
              padding: 14,
              marginBottom: 10,
              border: `1px solid ${COLORS.border}`,
              borderLeft: `3px solid ${v.color}`,
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8 }}>
                <span style={{ fontSize: 14, color: v.color }}>{v.symbol}</span>
                <span style={{ fontSize: 12, color: v.color, fontWeight: 600 }}>{v.virtue}</span>
              </div>
              <div style={{ fontSize: 12, color: COLORS.text, marginBottom: 10, lineHeight: 1.4 }}>{v.q}</div>
              {v.opts.map((opt, j) => (
                <div
                  key={j}
                  style={{
                    padding: "8px 12px",
                    borderRadius: 8,
                    background: COLORS.bg,
                    border: `1px solid ${COLORS.border}`,
                    marginBottom: 6,
                    cursor: "pointer",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <span style={{ fontSize: 11, color: COLORS.text, lineHeight: 1.4, flex: 1 }}>{opt.text}</span>
                  <span style={{
                    fontSize: 9,
                    color: opt.state === "Alive" ? COLORS.alive : opt.state === "Strained" ? COLORS.strained : COLORS.frozen,
                    marginLeft: 8,
                    whiteSpace: "nowrap",
                  }}>
                    {opt.state}
                  </span>
                </div>
              ))}
            </div>
          ))}
        </>
      )}
    </div>
  );
}

// ─── Screen: Learn ───────────────────────────────────────────────────────────
function LearnScreen({ onBack }) {
  const chapters = [
    { part: "I", title: "Foundation", chapters: ["Genesis (A0)", "The Circumpunct (⊙)", "The Trinity (•, Φ, ○)", "Temporal Process (⊛ → i → ☀︎)", "Balance (◐ = 0.5)", "The Surface Theorem"], color: COLORS.gold },
    { part: "II", title: "Mathematics", chapters: ["Field Equations", "64-State Architecture", "Canonical Spec"], color: COLORS.right },
    { part: "III", title: "Physics", chapters: ["Phase Coherence", "Aperture Density", "Standard Model", "Quantum Gravity"], color: COLORS.true_ },
    { part: "IV", title: "Emergence", chapters: ["Life", "Consciousness", "Emotions", "Perception"], color: COLORS.good },
    { part: "V", title: "Implications", chapters: ["Aging & Death", "Golden Ratio", "Ethics & Virtues"], color: COLORS.agreement },
  ];

  return (
    <div style={{ padding: "0 16px 90px" }}>
      <div style={{ display: "flex", alignItems: "center", padding: "16px 0 12px", gap: 12 }}>
        <div onClick={onBack} style={{ cursor: "pointer", fontSize: 18, color: COLORS.textDim }}>←</div>
        <div>
          <div style={{ fontSize: 10, color: COLORS.gold, letterSpacing: 2, textTransform: "uppercase" }}>The Framework</div>
          <div style={{ fontSize: 16, color: COLORS.text, fontWeight: 600 }}>Explore the Theory</div>
        </div>
      </div>

      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: "8px 0 16px" }}>
        <CircumpunctSymbol size={48} pulse balance={0.5} />
      </div>

      {chapters.map((section, i) => (
        <div key={i} style={{ marginBottom: 12 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8, paddingLeft: 4 }}>
            <span style={{ fontSize: 10, color: section.color, fontWeight: 700, letterSpacing: 1 }}>PART {section.part}</span>
            <span style={{ fontSize: 12, color: COLORS.text, fontWeight: 500 }}>{section.title}</span>
          </div>
          <div style={{ background: COLORS.bgCard, borderRadius: 14, padding: "4px 0", border: `1px solid ${COLORS.border}` }}>
            {section.chapters.map((ch, j) => (
              <div
                key={j}
                style={{
                  padding: "10px 14px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  borderBottom: j < section.chapters.length - 1 ? `1px solid ${COLORS.border}` : "none",
                  cursor: "pointer",
                }}
              >
                <span style={{ fontSize: 12, color: COLORS.text }}>{ch}</span>
                <span style={{ fontSize: 12, color: COLORS.textDim }}>→</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

// ─── Screen: Community ───────────────────────────────────────────────────────
function CommunityScreen({ onNavigate }) {
  return (
    <div style={{ padding: "0 16px 90px" }}>
      <div style={{ padding: "16px 0 12px" }}>
        <div style={{ fontSize: 16, color: COLORS.text, fontWeight: 600 }}>Community</div>
      </div>

      {/* My Circles */}
      <div style={{ fontSize: 10, color: COLORS.textDim, letterSpacing: 2, textTransform: "uppercase", marginBottom: 8, paddingLeft: 4 }}>
        My Circles
      </div>
      {[
        { name: "Ethics Lab", members: 5, lastActive: "2m ago", icon: "⊙" },
        { name: "Philosophy Circle", members: 4, lastActive: "1h ago", icon: "•" },
      ].map((c, i) => (
        <div key={i} style={{ background: COLORS.bgCard, borderRadius: 14, padding: "12px 14px", marginBottom: 8, border: `1px solid ${COLORS.border}`, display: "flex", alignItems: "center", gap: 12, cursor: "pointer" }}>
          <div style={{ width: 40, height: 40, borderRadius: "50%", background: COLORS.goldGlow, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, color: COLORS.gold }}>{c.icon}</div>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 13, color: COLORS.text, fontWeight: 500 }}>{c.name}</div>
            <div style={{ fontSize: 10, color: COLORS.textDim }}>{c.members} members · {c.lastActive}</div>
          </div>
          <div style={{ width: 8, height: 8, borderRadius: "50%", background: COLORS.alive }} />
        </div>
      ))}

      {/* Active Steelman Debates */}
      <div style={{ fontSize: 10, color: COLORS.textDim, letterSpacing: 2, textTransform: "uppercase", margin: "14px 0 8px", paddingLeft: 4 }}>
        Live Debates
      </div>
      <div style={{ background: COLORS.bgCard, borderRadius: 14, padding: "12px 14px", marginBottom: 8, border: `1px solid ${COLORS.agreement}20`, cursor: "pointer" }}>
        <div style={{ fontSize: 12, color: COLORS.text, fontWeight: 500, marginBottom: 4 }}>Is privacy a boundary (○) or a right (Φ)?</div>
        <div style={{ display: "flex", gap: 12 }}>
          <span style={{ fontSize: 10, color: COLORS.textDim }}>⚔️ 23 steelmen submitted</span>
          <span style={{ fontSize: 10, color: COLORS.agreement }}>Judging phase</span>
        </div>
      </div>

      {/* Leaderboard preview */}
      <div style={{ fontSize: 10, color: COLORS.textDim, letterSpacing: 2, textTransform: "uppercase", margin: "14px 0 8px", paddingLeft: 4 }}>
        Top Steelmen This Week
      </div>
      {[
        { name: "iris_93", xp: 2340, virtue: "Curiosity", rank: 1 },
        { name: "clearlight", xp: 2180, virtue: "Plasticity", rank: 2 },
        { name: "deep_field", xp: 1950, virtue: "Access", rank: 3 },
      ].map((u, i) => (
        <div key={i} style={{ background: COLORS.bgCard, borderRadius: 10, padding: "10px 14px", marginBottom: 6, border: `1px solid ${COLORS.border}`, display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ fontSize: 12, color: i === 0 ? COLORS.gold : COLORS.textDim, fontWeight: 600, width: 20 }}>#{u.rank}</span>
          <div style={{ flex: 1 }}>
            <span style={{ fontSize: 12, color: COLORS.text }}>{u.name}</span>
            <span style={{ fontSize: 10, color: COLORS.textDim, marginLeft: 8 }}>{u.xp} XP</span>
          </div>
          <span style={{ fontSize: 9, color: COLORS.gold, background: COLORS.goldGlow, padding: "2px 8px", borderRadius: 8 }}>{u.virtue}</span>
        </div>
      ))}
    </div>
  );
}

// ─── Screen: Profile ─────────────────────────────────────────────────────────
function ProfileScreen({ stats }) {
  return (
    <div style={{ padding: "0 16px 90px" }}>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "20px 0 16px" }}>
        <CircumpunctSymbol size={80} pulse balance={stats.balance} />
        <div style={{ fontSize: 16, color: COLORS.text, fontWeight: 600, marginTop: 10 }}>Ashman</div>
        <div style={{ fontSize: 11, color: COLORS.textDim }}>Level {stats.level} · {stats.xp} XP</div>
      </div>

      {/* Virtue States */}
      <div style={{ background: COLORS.bgCard, borderRadius: 14, padding: 16, marginBottom: 12, border: `1px solid ${COLORS.border}` }}>
        <div style={{ fontSize: 10, color: COLORS.textDim, letterSpacing: 2, textTransform: "uppercase", marginBottom: 10 }}>Virtue States</div>
        <VirtueMeter label="Plast." value={stats.plasticity} color={COLORS.good} icon="○" />
        <VirtueMeter label="Access" value={stats.access} color={COLORS.right} icon="Φ" />
        <VirtueMeter label="Curio." value={stats.curiosity} color={COLORS.true_} icon="•" />
        <VirtueMeter label="Valid." value={stats.validation} color={COLORS.agreement} icon="⊙" />
        <div style={{ display: "flex", justifyContent: "center", marginTop: 8 }}>
          <BalanceDial value={stats.balance} size={120} />
        </div>
      </div>

      {/* Streaks & Achievements */}
      <div style={{ background: COLORS.bgCard, borderRadius: 14, padding: 16, marginBottom: 12, border: `1px solid ${COLORS.border}` }}>
        <div style={{ fontSize: 10, color: COLORS.textDim, letterSpacing: 2, textTransform: "uppercase", marginBottom: 10 }}>Activity</div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8, textAlign: "center" }}>
          {[
            { label: "Day Streak", value: "12", icon: "🔥" },
            { label: "Scenarios", value: "47", icon: "⚖️" },
            { label: "Steelmen", value: "23", icon: "⚔️" },
          ].map((s, i) => (
            <div key={i}>
              <div style={{ fontSize: 18 }}>{s.icon}</div>
              <div style={{ fontSize: 16, color: COLORS.text, fontWeight: 600 }}>{s.value}</div>
              <div style={{ fontSize: 9, color: COLORS.textDim }}>{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* 64-State Progress */}
      <div style={{ background: COLORS.bgCard, borderRadius: 14, padding: 16, border: `1px solid ${COLORS.border}` }}>
        <div style={{ fontSize: 10, color: COLORS.textDim, letterSpacing: 2, textTransform: "uppercase", marginBottom: 10 }}>
          64-State Map · 18/64 Explored
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(8, 1fr)", gap: 3 }}>
          {Array.from({ length: 64 }, (_, i) => {
            const explored = i < 18;
            const recent = i >= 15 && i < 18;
            return (
              <div
                key={i}
                style={{
                  aspectRatio: "1",
                  borderRadius: 3,
                  background: explored
                    ? recent ? COLORS.gold : COLORS.goldDim + "80"
                    : COLORS.border + "40",
                  border: `1px solid ${explored ? COLORS.gold + "40" : "transparent"}`,
                }}
              />
            );
          })}
        </div>
        <div style={{ fontSize: 10, color: COLORS.textDim, marginTop: 8, textAlign: "center" }}>
          Each state unlocked through play and genuine engagement
        </div>
      </div>
    </div>
  );
}

// ─── Bottom Navigation ───────────────────────────────────────────────────────
function BottomNav({ active, onNavigate }) {
  const items = [
    { id: "home", icon: "⊙", label: "Home" },
    { id: "community", icon: "◎", label: "Community" },
    { id: "profile", icon: "◐", label: "Profile" },
  ];
  return (
    <div style={{
      position: "absolute",
      bottom: 0,
      left: 0,
      right: 0,
      height: 64,
      background: COLORS.bgCard,
      borderTop: `1px solid ${COLORS.border}`,
      display: "flex",
      justifyContent: "space-around",
      alignItems: "center",
      zIndex: 10,
    }}>
      {items.map((item) => (
        <div
          key={item.id}
          onClick={() => onNavigate(item.id)}
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            cursor: "pointer",
            opacity: active === item.id ? 1 : 0.5,
            transition: "opacity 0.2s",
          }}
        >
          <span style={{ fontSize: 20, color: active === item.id ? COLORS.gold : COLORS.textDim }}>{item.icon}</span>
          <span style={{ fontSize: 9, color: active === item.id ? COLORS.gold : COLORS.textDim, marginTop: 2 }}>{item.label}</span>
        </div>
      ))}
    </div>
  );
}

// ─── Main App ────────────────────────────────────────────────────────────────
export default function CircumpunctApp() {
  const [screen, setScreen] = useState("home");
  const [stats] = useState({
    level: 7,
    xp: 1847,
    balance: 0.52,
    plasticity: 68,
    access: 55,
    curiosity: 82,
    validation: 41,
  });

  const getActiveNav = () => {
    if (["home", "crucible", "signal", "arena", "mirror", "thaw", "learn"].includes(screen)) return "home";
    return screen;
  };

  return (
    <div style={{
      width: 375,
      height: 812,
      margin: "0 auto",
      background: COLORS.bg,
      borderRadius: 32,
      overflow: "hidden",
      position: "relative",
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      color: COLORS.text,
      boxShadow: `0 0 60px ${COLORS.goldGlow}`,
      border: `1px solid ${COLORS.border}`,
    }}>
      {/* Status bar mockup */}
      <div style={{
        height: 44,
        display: "flex",
        alignItems: "flex-end",
        justifyContent: "space-between",
        padding: "0 24px 4px",
        fontSize: 12,
        color: COLORS.textDim,
      }}>
        <span>9:41</span>
        <span style={{ fontSize: 10 }}>⊙</span>
        <span>100%</span>
      </div>

      {/* Content area */}
      <div style={{ height: "calc(100% - 44px - 64px)", overflowY: "auto", overflowX: "hidden" }}>
        {screen === "home" && <HomeScreen onNavigate={setScreen} stats={stats} />}
        {screen === "crucible" && <CrucibleScreen onBack={() => setScreen("home")} />}
        {screen === "signal" && <SignalNoiseScreen onBack={() => setScreen("home")} />}
        {screen === "arena" && <ArenaScreen onBack={() => setScreen("home")} />}
        {screen === "mirror" && <MirrorScreen onBack={() => setScreen("home")} />}
        {screen === "learn" && <LearnScreen onBack={() => setScreen("home")} />}
        {screen === "community" && <CommunityScreen onNavigate={setScreen} />}
        {screen === "profile" && <ProfileScreen stats={stats} />}
      </div>

      {/* Bottom nav */}
      <BottomNav active={getActiveNav()} onNavigate={setScreen} />
    </div>
  );
}
