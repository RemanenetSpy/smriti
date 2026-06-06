"use client";

import { useState, useEffect } from "react";
import { TurnstileWidget } from "./TurnstileWidget";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://spy9191-chronos-api-backend.hf.space";

// ─── Types ─────────────────────────────────────────────────────────────────────
type Phase = 0 | 1 | 2;
type UseCase = "agent" | "saas" | "personal" | null;

interface Props {
  onComplete: (apiKey: string, sourceId: string, useCase: UseCase) => void;
}

// ─── Use-case options ──────────────────────────────────────────────────────────
const USE_CASES: { id: UseCase; emoji: string; label: string; sub: string }[] = [
  { id: "agent",    emoji: "🤖", label: "Agent Memory",  sub: "Persistent recall for AI agents" },
  { id: "saas",     emoji: "🔌", label: "SaaS Platform", sub: "Embed memory into your product" },
  { id: "personal", emoji: "🧠", label: "Personal AI",   sub: "Your intelligent second brain" },
];

// ─── Confetti ──────────────────────────────────────────────────────────────────
function Confetti() {
  const colors = ["#fff", "#aaa", "#ccc", "#eee", "#888"];
  const particles = Array.from({ length: 40 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    delay: Math.random() * 0.6,
    color: colors[Math.floor(Math.random() * colors.length)],
    size: 4 + Math.random() * 7,
    duration: 1.2 + Math.random() * 1,
  }));
  return (
    <div className="pointer-events-none fixed inset-0 z-[9999] overflow-hidden">
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

// ─── Typewriter hook ───────────────────────────────────────────────────────────
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

// ─── Phase 0: Hook + Use Case + Email + Captcha ───────────────────────────────
function PhaseHookUseCase({
  onNext,
}: {
  onNext: (uc: UseCase, email: string, cfToken: string) => void;
}) {
  const [visible, setVisible]   = useState(false);
  const [selected, setSelected] = useState<UseCase>(null);
  const [email, setEmail]       = useState("");
  const [cfToken, setCfToken]   = useState("");

  const emailValid = email.trim().includes("@") && email.includes(".");
  const canSubmit  = !!selected && emailValid && !!cfToken;

  function buttonLabel() {
    if (!selected) return "Select one to continue";
    if (!emailValid) return "Enter your email →";
    if (!cfToken) return "Verifying you're human…";
    return "Get your API key →";
  }

  const line1 = useTypewriter("Every agent you build forgets everything", 34);
  const line2 = useTypewriter(line1.length >= 40 ? "the moment it stops running." : "", 34);
  const showBody = line2.length >= 28;

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 80);
    return () => clearTimeout(t);
  }, []);

  return (
    <div
      style={{
        opacity: visible ? 1 : 0,
        transition: "opacity 0.5s ease",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        textAlign: "center",
        padding: "44px 32px 36px",
      }}
    >
      {/* Logo */}
      <div style={{ marginBottom: 24 }}>
        <svg
          viewBox="0 0 100 100"
          xmlns="http://www.w3.org/2000/svg"
          style={{ width: 52, height: 52, display: "block", margin: "0 auto 12px" }}
        >
          <circle cx="50" cy="50" r="46" fill="none" stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
          <g>
            <circle cx="50" cy="50" r="18" fill="white" />
            <circle cx="50" cy="50" r="24" fill="none" stroke="rgba(255,255,255,0.5)" strokeWidth="1.5" strokeDasharray="4 2" />
            <circle cx="50" cy="50" r="32" fill="none" stroke="rgba(255,255,255,0.2)" strokeWidth="0.8" strokeDasharray="2 4" />
          </g>
        </svg>
        <div style={{ fontSize: 10, letterSpacing: 5, color: "rgba(255,255,255,0.3)", textTransform: "uppercase" }}>
          Smriti · by Kaal the Absolute
        </div>
      </div>

      {/* Headline */}
      <h1
        style={{
          fontSize: "clamp(22px, 3.2vw, 32px)",
          fontWeight: 300,
          color: "white",
          lineHeight: 1.4,
          letterSpacing: "-0.02em",
          marginBottom: 10,
          maxWidth: 380,
        }}
      >
        {line1}
        {line1.length >= 40 && (
          <>
            <br />
            <span style={{ color: "rgba(255,255,255,0.5)" }}>{line2}</span>
          </>
        )}
      </h1>

      {/* Subtitle + use cases */}
      <div
        style={{
          opacity: showBody ? 1 : 0,
          transition: "opacity 0.5s ease 0.2s",
          width: "100%",
        }}
      >
        <p style={{ color: "rgba(255,255,255,0.4)", fontSize: 14, marginBottom: 24 }}>
          Smriti remembers — so you never start over.
        </p>

        {/* Use case chips */}
        <p style={{ color: "rgba(255,255,255,0.25)", fontSize: 10, letterSpacing: 3, textTransform: "uppercase", marginBottom: 12 }}>
          How will you use it?
        </p>
        <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 20 }}>
          {USE_CASES.map((uc) => {
            const isSelected = selected === uc.id;
            return (
              <button
                key={uc.id}
                onClick={() => setSelected(uc.id)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  padding: "12px 16px",
                  background: isSelected ? "rgba(255,255,255,0.1)" : "rgba(255,255,255,0.04)",
                  border: isSelected ? "1px solid rgba(255,255,255,0.35)" : "1px solid rgba(255,255,255,0.07)",
                  borderRadius: 10,
                  cursor: "pointer",
                  textAlign: "left",
                  transition: "all 0.18s ease",
                  width: "100%",
                }}
              >
                <span style={{ fontSize: 22 }}>{uc.emoji}</span>
                <div>
                  <div style={{ color: "white", fontWeight: 500, fontSize: 13 }}>{uc.label}</div>
                  <div style={{ color: "rgba(255,255,255,0.35)", fontSize: 11, marginTop: 1 }}>{uc.sub}</div>
                </div>
                {isSelected && (
                  <div style={{ marginLeft: "auto", width: 16, height: 16, borderRadius: "50%", background: "white", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                    <svg width="8" height="6" viewBox="0 0 10 8" fill="none">
                      <path d="M1 4L3.5 6.5L9 1" stroke="#000" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                )}
              </button>
            );
          })}
        </div>

        {/* Email + Captcha — appear after use case picked */}
        {selected && (
          <div
            style={{
              opacity: 1,
              animation: "fadeSlideIn 0.3s ease",
              marginTop: 4,
              marginBottom: 16,
            }}
          >
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              autoFocus
              style={{
                width: "100%",
                padding: "11px 14px",
                background: "rgba(255,255,255,0.06)",
                border: emailValid
                  ? "1px solid rgba(255,255,255,0.3)"
                  : "1px solid rgba(255,255,255,0.1)",
                borderRadius: 8,
                color: "white",
                fontSize: 14,
                outline: "none",
                marginBottom: 12,
                boxSizing: "border-box",
                transition: "border-color 0.2s",
              }}
            />
            {/* Turnstile — renders once email field appears */}
            <div style={{ display: "flex", justifyContent: "center" }}>
              <TurnstileWidget
                theme="dark"
                onToken={setCfToken}
                onError={() => setCfToken("")}
                style={{ minHeight: 65 }}
              />
            </div>
          </div>
        )}

        <button
          onClick={() => canSubmit && onNext(selected!, email.trim(), cfToken)}
          disabled={!canSubmit}
          style={{
            width: "100%",
            padding: "13px 0",
            background: canSubmit ? "white" : "rgba(255,255,255,0.1)",
            color: canSubmit ? "#000" : "rgba(255,255,255,0.25)",
            border: "none",
            borderRadius: 10,
            fontSize: 14,
            fontWeight: 600,
            cursor: canSubmit ? "pointer" : "not-allowed",
            transition: "all 0.3s ease",
            letterSpacing: "-0.01em",
          }}
        >
          {buttonLabel()}
        </button>
      </div>

      {/* Progress dots */}
      <div style={{ display: "flex", gap: 6, marginTop: 20 }}>
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            style={{
              width: i === 0 ? 20 : 6, height: 6,
              borderRadius: 3,
              background: i === 0 ? "white" : "rgba(255,255,255,0.18)",
              transition: "all 0.3s",
            }}
          />
        ))}
      </div>
    </div>
  );
}

// ─── Phase 1: Activation ───────────────────────────────────────────────────────
function PhaseActivate({
  useCase,
  email,
  cfToken,
  onDone,
}: {
  useCase: UseCase;
  email: string;
  cfToken: string;
  onDone: (key: string, sourceId: string) => void;
}) {
  const [progress, setProgress] = useState(0);
  const [statusIdx, setStatusIdx] = useState(0);
  const [error, setError] = useState("");
  const called = { current: false };

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

    let step = 0;
    const iv = setInterval(() => {
      step++;
      setProgress(Math.min(step * 18, 80));
      setStatusIdx(Math.min(step - 1, statuses.length - 1));
      if (step >= 4) clearInterval(iv);
    }, 600);

    fetch(`${API_BASE}/billing/keys?tier=explorer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ use_case: useCase, email, cf_token: cfToken }),
    })
      .then(async (r) => {
        const data = await r.json();
        if (!r.ok) {
          // Surface the real server error (detail from FastAPI)
          throw new Error(data?.detail || `Server error ${r.status}`);
        }
        return data;
      })
      .then((data) => {
        clearInterval(iv);
        setProgress(100);
        setStatusIdx(statuses.length - 1);
        setTimeout(() => onDone(data.api_key, data.source_id), 500);
      })
      .catch((err: Error) => {
        clearInterval(iv);
        setError(err.message || "Could not reach the API. Please try again.");
      });

    return () => clearInterval(iv);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%", padding: "48px 32px", textAlign: "center" }}>
      <div style={{ fontSize: 10, letterSpacing: 4, color: "rgba(255,255,255,0.25)", textTransform: "uppercase", marginBottom: 16 }}>
        Step 2 of 3 · Activation
      </div>
      <h2 style={{ color: "white", fontSize: 20, fontWeight: 400, letterSpacing: "-0.02em", marginBottom: 6 }}>
        Awakening Smriti.
      </h2>
      <p style={{ color: "rgba(255,255,255,0.35)", fontSize: 13, marginBottom: 36 }}>
        Kaal the Absolute is binding your memory namespace.
      </p>

      {/* Progress bar */}
      <div style={{ width: "100%", maxWidth: 320, background: "rgba(255,255,255,0.08)", borderRadius: 4, height: 3, marginBottom: 12, overflow: "hidden" }}>
        <div
          style={{
            height: "100%",
            background: "white",
            borderRadius: 4,
            width: `${progress}%`,
            transition: "width 0.45s ease",
          }}
        />
      </div>
      <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 12, letterSpacing: "0.03em", minHeight: 18 }}>
        {statuses[statusIdx]}
      </div>

      {/* Pulsing orb */}
      <div style={{ marginTop: 36, position: "relative", width: 56, height: 56 }}>
        {[0, 12, 22].map((inset, i) => (
          <div
            key={i}
            style={{
              position: "absolute",
              inset,
              borderRadius: "50%",
              background: i === 2 ? "white" : `rgba(255,255,255,${i === 0 ? 0.06 : 0.12})`,
              animation: `orbPulse 1.6s ease-in-out ${i * 0.4}s infinite`,
            }}
          />
        ))}
      </div>

      {error && (
        <div style={{ marginTop: 24, color: "#ff8080", fontSize: 13, background: "rgba(255,100,100,0.1)", padding: "10px 16px", borderRadius: 8 }}>
          {error}{" "}
          <button
            onClick={() => { setError(""); setProgress(0); called.current = false; }}
            style={{ textDecoration: "underline", background: "none", border: "none", color: "#ff8080", cursor: "pointer" }}
          >
            Retry
          </button>
        </div>
      )}

      {/* Progress dots */}
      <div style={{ display: "flex", gap: 6, marginTop: 36 }}>
        {[0, 1, 2].map((i) => (
          <div key={i} style={{ width: i === 1 ? 20 : 6, height: 6, borderRadius: 3, background: i === 1 ? "white" : "rgba(255,255,255,0.18)" }} />
        ))}
      </div>

      <style>{`
        @keyframes orbPulse { 0%,100% { opacity:0.6; transform:scale(1); } 50% { opacity:1; transform:scale(1.08); } }
      `}</style>
    </div>
  );
}

// ─── Phase 2: Key Reveal ───────────────────────────────────────────────────────
function PhaseReveal({ apiKey, sourceId, onComplete }: { apiKey: string; sourceId: string; onComplete: () => void }) {
  const [copied, setCopied]     = useState(false);
  const [showConfetti, setShowConfetti] = useState(true);

  useEffect(() => {
    const t = setTimeout(() => setShowConfetti(false), 3000);
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
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%", padding: "44px 32px", textAlign: "center" }}>
        {/* Success mark */}
        <div
          style={{
            width: 52, height: 52,
            borderRadius: "50%",
            background: "rgba(125,255,179,0.12)",
            border: "1px solid rgba(125,255,179,0.35)",
            display: "flex", alignItems: "center", justifyContent: "center",
            marginBottom: 18,
            animation: "popIn 0.35s cubic-bezier(0.34,1.56,0.64,1)",
          }}
        >
          <svg width="20" height="16" viewBox="0 0 22 18" fill="none">
            <path d="M1 9L7.5 15.5L21 1" stroke="#7dffb3" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>

        <h2 style={{ color: "white", fontSize: 20, fontWeight: 400, marginBottom: 4 }}>Smriti is awake.</h2>
        <p style={{ color: "rgba(255,255,255,0.35)", fontSize: 13, marginBottom: 24 }}>
          Your key is ready. Guard it — Kaal shows it only once.
        </p>

        {/* Key box */}
        <div style={{ width: "100%", maxWidth: 360, marginBottom: 8 }}>
          <div
            style={{
              background: "rgba(255,255,255,0.05)",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: 8,
              padding: "12px 14px",
              fontFamily: "monospace",
              fontSize: 12,
              color: "rgba(255,255,255,0.8)",
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
              background: copied ? "rgba(125,255,179,0.12)" : "rgba(255,255,255,0.08)",
              border: "1px solid",
              borderColor: copied ? "rgba(125,255,179,0.35)" : "rgba(255,255,255,0.12)",
              borderRadius: 8,
              color: copied ? "#7dffb3" : "rgba(255,255,255,0.65)",
              fontSize: 13,
              cursor: "pointer",
              transition: "all 0.2s ease",
              fontWeight: 500,
            }}
          >
            {copied ? "✓ Copied!" : "Copy API Key"}
          </button>
        </div>

        <p style={{ color: "rgba(255,255,255,0.18)", fontSize: 11, marginBottom: 24 }}>
          Source ID: <code style={{ color: "rgba(255,255,255,0.3)" }}>{sourceId}</code>
        </p>

        <button
          onClick={onComplete}
          style={{
            width: "100%", maxWidth: 360,
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

        {/* Progress dots */}
        <div style={{ display: "flex", gap: 6, marginTop: 20 }}>
          {[0, 1, 2].map((i) => (
            <div key={i} style={{ width: i === 2 ? 20 : 6, height: 6, borderRadius: 3, background: i === 2 ? "white" : "rgba(255,255,255,0.18)" }} />
          ))}
        </div>

        <style>{`
          @keyframes popIn { from { opacity:0; transform:scale(0.5); } to { opacity:1; transform:scale(1); } }
        `}</style>
      </div>
    </>
  );
}

// ─── Root ──────────────────────────────────────────────────────────────────────
export function WelcomeScreen({ onComplete }: Props) {
  const [phase, setPhase]               = useState<Phase>(0);
  const [useCase, setUseCase]           = useState<UseCase>(null);
  const [email, setEmail]               = useState("");
  const [cfToken, setCfToken]           = useState("");
  const [revealKey, setRevealKey]       = useState("");
  const [revealSource, setRevealSource] = useState("");

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
          background: "radial-gradient(ellipse 55% 45% at 50% 0%, rgba(255,255,255,0.04) 0%, transparent 70%)",
          pointerEvents: "none",
        }}
      />

      {/* Card */}
      <div
        style={{
          position: "relative",
          width: "min(460px, calc(100vw - 32px))",
          maxHeight: "calc(100vh - 48px)",
          background: "rgba(255,255,255,0.03)",
          border: "1px solid rgba(255,255,255,0.07)",
          borderRadius: 20,
          overflowY: "auto",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {phase === 0 && (
          <PhaseHookUseCase
            onNext={(uc, em, tok) => {
              setUseCase(uc);
              setEmail(em);
              setCfToken(tok);
              if (uc) localStorage.setItem("kaal_use_case", uc);
              setPhase(1);
            }}
          />
        )}
        {phase === 1 && (
          <PhaseActivate
            useCase={useCase}
            email={email}
            cfToken={cfToken}
            onDone={(key, sid) => {
              setRevealKey(key);
              setRevealSource(sid);
              setPhase(2);
            }}
          />
        )}
        {phase === 2 && (
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
