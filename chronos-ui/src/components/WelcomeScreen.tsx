"use client";

import { useState, useEffect, useRef } from "react";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://spy9191-chronos-api-backend.hf.space";

// ─── Types ────────────────────────────────────────────────────────────────────
type Phase = 0 | 1 | 2 | 3 | 4;
type UseCase = "agent" | "saas" | "personal" | null;

interface Props {
  onComplete: (apiKey: string, sourceId: string, useCase: UseCase) => void;
}

// ─── Demo lines shown in the terminal animation (Phase 1) ────────────────────
const DEMO_LINES = [
  { delay: 0,    text: '$ POST /ingest', type: "cmd" },
  { delay: 600,  text: '  "Reman closed the Acme deal for $50k on May 12th"', type: "input" },
  { delay: 1400, text: "→ Subject: Reman  |  Verb: closed  |  Object: Acme deal ($50k)", type: "parse" },
  { delay: 2100, text: "→ Stored in 18ms  ✓", type: "ok" },
  { delay: 3000, text: "", type: "gap" },
  { delay: 3200, text: '$ POST /query  "What did Reman close?"', type: "cmd" },
  { delay: 4000, text: "→ Vector + temporal search…", type: "parse" },
  { delay: 4800, text: '→ "Reman closed the Acme deal for $50k on May 12th"', type: "ok" },
  { delay: 5400, text: "→ Retrieved in 11ms  ✓", type: "ok" },
];

// ─── Use-case options ─────────────────────────────────────────────────────────
const USE_CASES: { id: UseCase; emoji: string; label: string; sub: string }[] = [
  { id: "agent",    emoji: "🤖", label: "Agent Memory",   sub: "Give your AI agents persistent recall" },
  { id: "saas",     emoji: "🔌", label: "SaaS Platform",  sub: "Embed memory into your product" },
  { id: "personal", emoji: "🧠", label: "Personal AI",    sub: "Your own intelligent second brain" },
];

// ─── Confetti particle ────────────────────────────────────────────────────────
function Confetti() {
  const colors = ["#000", "#444", "#888", "#ccc", "#f0f0f0"];
  const particles = Array.from({ length: 48 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    delay: Math.random() * 0.8,
    color: colors[Math.floor(Math.random() * colors.length)],
    size: 5 + Math.random() * 8,
    duration: 1.4 + Math.random() * 1.2,
  }));

  return (
    <div className="pointer-events-none fixed inset-0 z-[999] overflow-hidden">
      {particles.map((p) => (
        <div
          key={p.id}
          style={{
            position: "absolute",
            left: `${p.x}%`,
            top: "-10px",
            width: p.size,
            height: p.size,
            background: p.color,
            borderRadius: Math.random() > 0.5 ? "50%" : "2px",
            animation: `confettiFall ${p.duration}s ${p.delay}s ease-in forwards`,
          }}
        />
      ))}
      <style>{`
        @keyframes confettiFall {
          0%   { transform: translateY(0) rotate(0deg); opacity: 1; }
          100% { transform: translateY(110vh) rotate(720deg); opacity: 0; }
        }
      `}</style>
    </div>
  );
}

// ─── Typewriter hook ──────────────────────────────────────────────────────────
function useTypewriter(text: string, speed = 28) {
  const [displayed, setDisplayed] = useState("");
  useEffect(() => {
    setDisplayed("");
    if (!text) return;
    let i = 0;
    const iv = setInterval(() => {
      i++;
      setDisplayed(text.slice(0, i));
      if (i >= text.length) clearInterval(iv);
    }, speed);
    return () => clearInterval(iv);
  }, [text, speed]);
  return displayed;
}

// ─── Phase 0: Hook ────────────────────────────────────────────────────────────
function PhaseHook({ onNext }: { onNext: () => void }) {
  const [visible, setVisible] = useState(false);
  const line1 = useTypewriter("Every agent you build forgets everything", 36);
  const line2 = useTypewriter(line1.length >= 40 ? "the moment it stops running." : "", 36);
  const showCta = line2.length >= 28;

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 80);
    return () => clearTimeout(t);
  }, []);

  return (
    <div
      style={{
        opacity: visible ? 1 : 0,
        transition: "opacity 0.6s ease",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        textAlign: "center",
        padding: "48px 32px 36px",
      }}
    >
      {/* Real Kaal logo — orbital SVG adapted for dark background */}
      <div style={{ marginBottom: 28 }}>
        <svg
          viewBox="0 0 100 100"
          xmlns="http://www.w3.org/2000/svg"
          style={{ width: 64, height: 64, display: "block", margin: "0 auto 14px" }}
        >
          <circle cx="50" cy="50" r="46" fill="none" stroke="rgba(255,255,255,0.25)" strokeWidth="1" />
          <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,0.12)" strokeWidth="0.5" strokeDasharray="1 2" />
          <g>
            <circle cx="50" cy="50" r="18" fill="white" />
            <circle cx="50" cy="50" r="24" fill="none" stroke="rgba(255,255,255,0.55)" strokeWidth="1.5" strokeDasharray="4 2" />
            <circle cx="50" cy="50" r="32" fill="none" stroke="rgba(255,255,255,0.25)" strokeWidth="0.8" strokeDasharray="2 4" />
          </g>
        </svg>
        <div style={{ fontSize: 11, letterSpacing: 6, color: "rgba(255,255,255,0.35)", textTransform: "uppercase" }}>
          Smriti · by Kaal
        </div>
      </div>

      {/* Headline */}
      <div style={{ maxWidth: 400, marginBottom: 32 }}>
        <h1
          style={{
            fontSize: "clamp(24px, 3.5vw, 36px)",
            fontWeight: 300,
            color: "white",
            lineHeight: 1.4,
            letterSpacing: "-0.02em",
            marginBottom: 14,
          }}
        >
          {line1}
          {line1.length >= 40 && (
            <>
              <br />
              <span style={{ color: "rgba(255,255,255,0.55)" }}>{line2}</span>
            </>
          )}
        </h1>

        <p
          style={{
            color: "rgba(255,255,255,0.4)",
            fontSize: 15,
            marginBottom: 32,
            opacity: showCta ? 1 : 0,
            transition: "opacity 0.6s ease 0.3s",
          }}
        >
          Smriti remembers. So you never have to start over.
        </p>

        <button
          onClick={onNext}
          style={{
            background: "white",
            color: "#000",
            border: "none",
            borderRadius: 10,
            padding: "14px 40px",
            fontSize: 15,
            fontWeight: 600,
            cursor: "pointer",
            opacity: showCta ? 1 : 0,
            transition: "opacity 0.5s ease 0.5s, transform 0.2s",
            letterSpacing: "-0.01em",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.transform = "scale(1.03)")}
          onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
        >
          Show me how →
        </button>
      </div>

      {/* Progress dots — in normal flow, no absolute positioning */}
      <div style={{ display: "flex", gap: 6, marginTop: 8 }}>
        {[0, 1, 2, 3].map((i) => (
          <div
            key={i}
            style={{
              width: i === 0 ? 20 : 6, height: 6,
              borderRadius: 3,
              background: i === 0 ? "white" : "rgba(255,255,255,0.2)",
              transition: "all 0.3s",
            }}
          />
        ))}
      </div>
    </div>
  );
}

// ─── Phase 1: Live Demo ───────────────────────────────────────────────────────
function PhaseDemo({ onNext }: { onNext: () => void }) {
  const [visibleLines, setVisibleLines] = useState<number[]>([]);
  const [done, setDone] = useState(false);

  useEffect(() => {
    const timers: ReturnType<typeof setTimeout>[] = [];
    DEMO_LINES.forEach((line, idx) => {
      timers.push(setTimeout(() => setVisibleLines((p) => [...p, idx]), line.delay));
    });
    timers.push(setTimeout(() => setDone(true), 6200));
    return () => timers.forEach(clearTimeout);
  }, []);

  const lineColor = (type: string) => {
    if (type === "cmd") return "rgba(255,255,255,0.9)";
    if (type === "input") return "rgba(255,255,255,0.55)";
    if (type === "parse") return "#a8d8ff";
    if (type === "ok") return "#7dffb3";
    return "transparent";
  };

  return (
    <div className="flex flex-col h-full px-10 py-10">
      <div style={{ marginBottom: 28 }}>
        <div style={{ fontSize: 11, letterSpacing: 4, color: "rgba(255,255,255,0.3)", textTransform: "uppercase", marginBottom: 10 }}>
          Step 1 of 3 · Live demo
        </div>
        <h2 style={{ color: "white", fontSize: 22, fontWeight: 500, letterSpacing: "-0.02em" }}>
          Watch Smriti remember something.
        </h2>
        <p style={{ color: "rgba(255,255,255,0.35)", fontSize: 13, marginTop: 6 }}>
          Kaal, the Absolute, forgets nothing. Neither will your agents.
        </p>
      </div>

      {/* Terminal */}
      <div
        style={{
          flex: 1,
          background: "rgba(255,255,255,0.04)",
          border: "1px solid rgba(255,255,255,0.08)",
          borderRadius: 12,
          padding: "20px 24px",
          fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
          fontSize: 13,
          lineHeight: 1.7,
          overflowY: "auto",
          marginBottom: 24,
        }}
      >
        {DEMO_LINES.map((line, idx) =>
          visibleLines.includes(idx) && line.type !== "gap" ? (
            <div
              key={idx}
              style={{
                color: lineColor(line.type),
                animation: "fadeSlideIn 0.25s ease",
                whiteSpace: "pre-wrap",
                wordBreak: "break-all",
              }}
            >
              {line.text}
            </div>
          ) : visibleLines.includes(idx) && line.type === "gap" ? (
            <br key={idx} />
          ) : null
        )}
        {!done && (
          <span style={{ color: "rgba(255,255,255,0.3)", animation: "blink 1s infinite" }}>▋</span>
        )}
      </div>

      <button
        onClick={onNext}
        disabled={!done}
        style={{
          background: done ? "white" : "rgba(255,255,255,0.12)",
          color: done ? "#000" : "rgba(255,255,255,0.3)",
          border: "none",
          borderRadius: 10,
          padding: "13px 0",
          width: "100%",
          fontSize: 14,
          fontWeight: 600,
          cursor: done ? "pointer" : "not-allowed",
          transition: "all 0.4s ease",
          letterSpacing: "-0.01em",
        }}
      >
        {done ? "That's Smriti. Ready to bind it to your agent? →" : "Initialising Smriti…"}
      </button>

      {/* Progress dots */}
      <div style={{ display: "flex", justifyContent: "center", gap: 6, marginTop: 20 }}>
        {[0, 1, 2, 3].map((i) => (
          <div key={i} style={{ width: i === 1 ? 20 : 6, height: 6, borderRadius: 3, background: i === 1 ? "white" : "rgba(255,255,255,0.2)" }} />
        ))}
      </div>

      <style>{`
        @keyframes fadeSlideIn { from { opacity:0; transform:translateY(4px); } to { opacity:1; transform:translateY(0); } }
        @keyframes blink { 0%,100% { opacity:1; } 50% { opacity:0; } }
      `}</style>
    </div>
  );
}

// ─── Phase 2: Use Case ────────────────────────────────────────────────────────
function PhaseUseCase({ onNext }: { onNext: (uc: UseCase) => void }) {
  const [selected, setSelected] = useState<UseCase>(null);

  return (
    <div className="flex flex-col h-full px-10 py-10">
      <div style={{ marginBottom: 28 }}>
        <div style={{ fontSize: 11, letterSpacing: 4, color: "rgba(255,255,255,0.3)", textTransform: "uppercase", marginBottom: 10 }}>
          Step 2 of 3 · Personalise
        </div>
        <h2 style={{ color: "white", fontSize: 22, fontWeight: 500, letterSpacing: "-0.02em" }}>
          How will you use Smriti?
        </h2>
        <p style={{ color: "rgba(255,255,255,0.35)", fontSize: 13, marginTop: 6 }}>
          Kaal's memory adapts to your world from day one.
        </p>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 12, flex: 1 }}>
        {USE_CASES.map((uc) => {
          const isSelected = selected === uc.id;
          return (
            <button
              key={uc.id}
              onClick={() => setSelected(uc.id)}
              style={{
                display: "flex", alignItems: "center", gap: 16,
                padding: "16px 20px",
                background: isSelected ? "rgba(255,255,255,0.1)" : "rgba(255,255,255,0.04)",
                border: isSelected ? "1px solid rgba(255,255,255,0.4)" : "1px solid rgba(255,255,255,0.08)",
                borderRadius: 12,
                cursor: "pointer",
                textAlign: "left",
                transition: "all 0.2s ease",
              }}
              onMouseEnter={(e) => { if (!isSelected) e.currentTarget.style.background = "rgba(255,255,255,0.07)"; }}
              onMouseLeave={(e) => { if (!isSelected) e.currentTarget.style.background = "rgba(255,255,255,0.04)"; }}
            >
              <span style={{ fontSize: 28 }}>{uc.emoji}</span>
              <div>
                <div style={{ color: "white", fontWeight: 500, fontSize: 14 }}>{uc.label}</div>
                <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 12, marginTop: 2 }}>{uc.sub}</div>
              </div>
              {isSelected && (
                <div style={{ marginLeft: "auto", width: 18, height: 18, borderRadius: "50%", background: "white", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <svg width="10" height="8" viewBox="0 0 10 8" fill="none">
                    <path d="M1 4L3.5 6.5L9 1" stroke="#000" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
              )}
            </button>
          );
        })}
      </div>

      <button
        onClick={() => selected && onNext(selected)}
        disabled={!selected}
        style={{
          marginTop: 24,
          background: selected ? "white" : "rgba(255,255,255,0.1)",
          color: selected ? "#000" : "rgba(255,255,255,0.3)",
          border: "none",
          borderRadius: 10,
          padding: "13px 0",
          width: "100%",
          fontSize: 14,
          fontWeight: 600,
          cursor: selected ? "pointer" : "not-allowed",
          transition: "all 0.3s ease",
          letterSpacing: "-0.01em",
        }}
      >
        Continue →
      </button>

      <div style={{ display: "flex", justifyContent: "center", gap: 6, marginTop: 20 }}>
        {[0, 1, 2, 3].map((i) => (
          <div key={i} style={{ width: i === 2 ? 20 : 6, height: 6, borderRadius: 3, background: i === 2 ? "white" : "rgba(255,255,255,0.2)" }} />
        ))}
      </div>
    </div>
  );
}

// ─── Phase 3: Activation ──────────────────────────────────────────────────────
function PhaseActivate({ useCase, onDone }: { useCase: UseCase; onDone: (key: string, sourceId: string) => void }) {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState("Initialising temporal core…");
  const [error, setError] = useState("");
  const called = useRef(false);

  const statuses = [
    "Initialising temporal core…",
    "Allocating vector space…",
    "Configuring SVO parser…",
    "Securing your namespace…",
    "Memory engine ready.",
  ];

  useEffect(() => {
    if (called.current) return;
    called.current = true;

    // Animate progress bar while calling API
    let step = 0;
    const iv = setInterval(() => {
      step++;
      setProgress(Math.min(step * 18, 80));
      setStatus(statuses[Math.min(step - 1, statuses.length - 1)]);
      if (step >= 4) clearInterval(iv);
    }, 700);

    fetch(`${API_BASE}/billing/keys?tier=explorer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ use_case: useCase }),
    })
      .then((r) => r.json())
      .then((data) => {
        clearInterval(iv);
        setProgress(100);
        setStatus("Memory engine ready.");
        setTimeout(() => onDone(data.api_key, data.source_id), 600);
      })
      .catch((e) => {
        clearInterval(iv);
        setError("Could not reach the API. Please try again.");
      });

    return () => clearInterval(iv);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="flex flex-col items-center justify-center h-full px-10 text-center">
      <div style={{ marginBottom: 40 }}>
        <div style={{ fontSize: 11, letterSpacing: 4, color: "rgba(255,255,255,0.3)", textTransform: "uppercase", marginBottom: 12 }}>
          Step 3 of 3 · Activation
        </div>
        <h2 style={{ color: "white", fontSize: 22, fontWeight: 500, letterSpacing: "-0.02em", marginBottom: 8 }}>
          Awakening Smriti.
        </h2>
        <p style={{ color: "rgba(255,255,255,0.4)", fontSize: 13 }}>
          Kaal the Absolute is binding your memory namespace.
        </p>
      </div>

      {/* Progress bar */}
      <div style={{ width: "100%", maxWidth: 360, background: "rgba(255,255,255,0.08)", borderRadius: 4, height: 4, marginBottom: 16, overflow: "hidden" }}>
        <div
          style={{
            height: "100%",
            background: "white",
            borderRadius: 4,
            width: `${progress}%`,
            transition: "width 0.5s ease",
          }}
        />
      </div>

      <div style={{ color: "rgba(255,255,255,0.45)", fontSize: 12, letterSpacing: "0.03em", minHeight: 20 }}>
        {status}
      </div>

      {/* Pulsing orb */}
      <div style={{ marginTop: 40, position: "relative", width: 64, height: 64 }}>
        <div style={{
          position: "absolute", inset: 0,
          borderRadius: "50%",
          background: "rgba(255,255,255,0.06)",
          animation: "orbPulse 1.6s ease-in-out infinite",
        }} />
        <div style={{
          position: "absolute", inset: 12,
          borderRadius: "50%",
          background: "rgba(255,255,255,0.12)",
          animation: "orbPulse 1.6s ease-in-out 0.4s infinite",
        }} />
        <div style={{
          position: "absolute", inset: 22,
          borderRadius: "50%",
          background: "white",
          animation: "orbPulse 1.6s ease-in-out 0.8s infinite",
        }} />
      </div>

      {/* Social proof */}
      <p style={{ color: "rgba(255,255,255,0.2)", fontSize: 11, marginTop: 36, letterSpacing: "0.02em" }}>
        1,200+ agents already remember through Smriti
      </p>

      {error && (
        <div style={{ marginTop: 20, color: "#ff8080", fontSize: 13, background: "rgba(255,100,100,0.1)", padding: "10px 16px", borderRadius: 8 }}>
          {error}{" "}
          <button
            onClick={() => { called.current = false; setError(""); setProgress(0); }}
            style={{ textDecoration: "underline", background: "none", border: "none", color: "#ff8080", cursor: "pointer" }}
          >
            Retry
          </button>
        </div>
      )}

      <style>{`
        @keyframes orbPulse { 0%,100% { opacity:0.6; transform:scale(1); } 50% { opacity:1; transform:scale(1.1); } }
      `}</style>
    </div>
  );
}

// ─── Phase 4: Key Reveal ─────────────────────────────────────────────────────
function PhaseReveal({ apiKey, sourceId, onComplete }: { apiKey: string; sourceId: string; onComplete: () => void }) {
  const [copied, setCopied] = useState(false);
  const [showConfetti, setShowConfetti] = useState(true);

  useEffect(() => {
    const t = setTimeout(() => setShowConfetti(false), 3500);
    return () => clearTimeout(t);
  }, []);

  const copy = () => {
    navigator.clipboard.writeText(apiKey).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <>
      {showConfetti && <Confetti />}
      <div className="flex flex-col items-center justify-center h-full px-10 text-center">
        {/* Success mark */}
        <div
          style={{
            width: 56, height: 56,
            borderRadius: "50%",
            background: "rgba(125,255,179,0.15)",
            border: "1px solid rgba(125,255,179,0.4)",
            display: "flex", alignItems: "center", justifyContent: "center",
            marginBottom: 20,
            animation: "popIn 0.4s cubic-bezier(0.34,1.56,0.64,1)",
          }}
        >
          <svg width="22" height="18" viewBox="0 0 22 18" fill="none">
            <path d="M1 9L7.5 15.5L21 1" stroke="#7dffb3" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>

        <h2 style={{ color: "white", fontSize: 22, fontWeight: 500, marginBottom: 6 }}>Smriti is awake.</h2>
        <p style={{ color: "rgba(255,255,255,0.35)", fontSize: 13, marginBottom: 28 }}>
          Your memory key is ready. Guard it — Kaal shows it only once.
        </p>

        {/* Key box */}
        <div style={{ width: "100%", maxWidth: 380, marginBottom: 12 }}>
          <div
            style={{
              background: "rgba(255,255,255,0.06)",
              border: "1px solid rgba(255,255,255,0.12)",
              borderRadius: 10,
              padding: "14px 16px",
              fontFamily: "monospace",
              fontSize: 12,
              color: "rgba(255,255,255,0.85)",
              wordBreak: "break-all",
              textAlign: "left",
              letterSpacing: "0.04em",
              marginBottom: 8,
              userSelect: "all",
            }}
          >
            {apiKey}
          </div>
          <button
            onClick={copy}
            style={{
              width: "100%",
              padding: "10px 0",
              background: copied ? "rgba(125,255,179,0.15)" : "rgba(255,255,255,0.1)",
              border: "1px solid",
              borderColor: copied ? "rgba(125,255,179,0.4)" : "rgba(255,255,255,0.15)",
              borderRadius: 8,
              color: copied ? "#7dffb3" : "rgba(255,255,255,0.7)",
              fontSize: 13,
              cursor: "pointer",
              transition: "all 0.25s ease",
              fontWeight: 500,
            }}
          >
            {copied ? "✓ Copied!" : "Copy API Key"}
          </button>
        </div>

        {/* Source ID */}
        <p style={{ color: "rgba(255,255,255,0.2)", fontSize: 11, marginBottom: 28 }}>
          Source ID: <code style={{ color: "rgba(255,255,255,0.35)" }}>{sourceId}</code>
        </p>

        {/* Social proof */}
        <p style={{ color: "rgba(255,255,255,0.2)", fontSize: 11, marginBottom: 28 }}>
          1,200+ agents already remember through Smriti · by Kaal the Absolute.
        </p>

        <button
          onClick={onComplete}
          style={{
            width: "100%", maxWidth: 380,
            padding: "13px 0",
            background: "white",
            border: "none",
            borderRadius: 10,
            color: "#000",
            fontSize: 14,
            fontWeight: 600,
            cursor: "pointer",
            letterSpacing: "-0.01em",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.opacity = "0.88")}
          onMouseLeave={(e) => (e.currentTarget.style.opacity = "1")}
        >
          Go to Dashboard →
        </button>

        <style>{`
          @keyframes popIn { from { opacity:0; transform:scale(0.5); } to { opacity:1; transform:scale(1); } }
        `}</style>
      </div>
    </>
  );
}

// ─── Root WelcomeScreen ───────────────────────────────────────────────────────
export function WelcomeScreen({ onComplete }: Props) {
  const [phase, setPhase] = useState<Phase>(0);
  const [useCase, setUseCase] = useState<UseCase>(null);
  const [revealKey, setRevealKey] = useState("");
  const [revealSource, setRevealSource] = useState("");

  const handleUseCaseNext = (uc: UseCase) => {
    setUseCase(uc);
    if (uc) localStorage.setItem("kaal_use_case", uc);
    setPhase(3);
  };

  const handleActivateDone = (key: string, sid: string) => {
    setRevealKey(key);
    setRevealSource(sid);
    setPhase(4);
  };

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 9999,
        background: "#0a0a0a",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "'Inter', 'Geist', system-ui, sans-serif",
      }}
    >
      {/* Subtle radial glow */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "radial-gradient(ellipse 60% 50% at 50% 0%, rgba(255,255,255,0.04) 0%, transparent 70%)",
          pointerEvents: "none",
        }}
      />

      {/* Card — height driven by content; capped at 90vh with scroll */}
      <div
        style={{
          position: "relative",
          width: "min(480px, calc(100vw - 40px))",
          maxHeight: "calc(100vh - 64px)",
          background: "rgba(255,255,255,0.03)",
          border: "1px solid rgba(255,255,255,0.08)",
          borderRadius: 20,
          overflowY: "auto",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {phase === 0 && <PhaseHook onNext={() => setPhase(1)} />}
        {phase === 1 && <PhaseDemo onNext={() => setPhase(2)} />}
        {phase === 2 && <PhaseUseCase onNext={handleUseCaseNext} />}
        {phase === 3 && <PhaseActivate useCase={useCase} onDone={handleActivateDone} />}
        {phase === 4 && (
          <PhaseReveal
            apiKey={revealKey}
            sourceId={revealSource}
            onComplete={() => onComplete(revealKey, revealSource, useCase)}
          />
        )}
      </div>
    </div>
  );
}
