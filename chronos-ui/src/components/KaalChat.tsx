"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import {
  MessageCircle, X, Volume2, VolumeX, Send, Loader2, ChevronDown,
} from "lucide-react";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://spy9191-chronos-api-backend.hf.space";

// ── Session ID ─────────────────────────────────────────────────────────────
function getSessionId() {
  if (typeof window === "undefined") return "ssr";
  let id = sessionStorage.getItem("kaal_session_id");
  if (!id) {
    id = `sess_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
    sessionStorage.setItem("kaal_session_id", id);
  }
  return id;
}

// ── Feature cards ──────────────────────────────────────────────────────────
const FEATURE_CARDS: Record<string, { title: string; lines: string[] }> = {
  ingest: {
    title: "Event Ingestion",
    lines: [
      "POST /ingest",
      '{ "text": "Ali closed Acme deal for $50k", "source_id": "YOUR_KEY" }',
      "→ SVO parsed: subject=Ali, verb=closed, object=Acme deal",
      "→ Stored in Neon PostgreSQL + pgvector",
    ],
  },
  query: {
    title: "Temporal Query",
    lines: [
      "POST /query",
      '{ "query": "What deals did Ali close last week?", "source_id": "YOUR_KEY" }',
      "→ Vector search + temporal filter fused",
      "→ Returns ranked events with timestamps",
    ],
  },
  agent: {
    title: "Agent Orchestration",
    lines: [
      "POST /agent/run",
      '{ "task": "Summarise Q2 deals", "source_id": "YOUR_KEY" }',
      "→ GPT OSS 120B @ 2,100 tok/s on Cerebras",
      "→ memory_inject → call_model → tool_execute → memory_store",
    ],
  },
  connect: {
    title: "Tool Connector",
    lines: [
      "POST /connect",
      '{ "tool_name": "Stripe", "base_url": "https://api.stripe.com", ... }',
      "→ Agent discovers tool automatically",
      "→ Calls it when context requires — no code changes",
    ],
  },
  apikey: {
    title: "API Key",
    lines: [
      "POST /billing/keys?tier=explorer",
      "→ Returns your unique source_id + api_key",
      "→ Use as X-API-Key header on all requests",
      "→ Free tier: 10k events / month",
    ],
  },
};

// ── Types ──────────────────────────────────────────────────────────────────
type Message = {
  role: "user" | "assistant";
  text: string;
  card?: string;
  timestamp: number;
};
type Consent = "accepted" | "declined" | null;

// ── Personalised greeting based on stored use-case ─────────────────────────
function buildGreeting(): string {
  const uc =
    typeof window !== "undefined"
      ? localStorage.getItem("kaal_use_case")
      : null;

  if (uc === "agent")
    return "I am Smriti — temporal memory by Kaal the Absolute. I see you're building agent memory. Want me to show you how to bind your first event? It takes 30 seconds.";
  if (uc === "saas")
    return "I am Smriti — memory that persists across all time. Ready to embed Kaal's recall into your product? Let me show you where to start.";
  if (uc === "personal")
    return "I am Smriti — I remember what time would otherwise erase. Ready to give your assistant a mind that never forgets? Let's begin.";
  return "I am Smriti — temporal memory by Kaal. I can show you how to ingest events, run queries, orchestrate agents, and connect tools. What would you like to explore?";
}

// ── KaalChat ────────────────────────────────────────────────────────────────
export function KaalChat({
  forceOpen = false,
  onFirstVisitDone,
}: {
  forceOpen?: boolean;
  onFirstVisitDone?: () => void;
}) {
  const [open, setOpen]       = useState(forceOpen);
  const [centered, setCentered] = useState(forceOpen); // true = modal, false = corner
  const [consent, setConsent]   = useState<Consent>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput]       = useState("");
  const [loading, setLoading]   = useState(false);
  const [ttsEnabled, setTtsEnabled] = useState(false);
  const [remaining, setRemaining]   = useState(5);
  const [greeted, setGreeted]       = useState(false);
  const [audioLoading, setAudioLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef       = useRef<HTMLInputElement>(null);
  const audioRef       = useRef<HTMLAudioElement | null>(null);

  // Load persisted state
  useEffect(() => {
    const savedConsent = localStorage.getItem("kaal_chat_consent") as Consent;
    if (savedConsent) setConsent(savedConsent);
    const savedTts = localStorage.getItem("kaal_tts_enabled");
    if (savedTts) setTtsEnabled(savedTts === "true");
  }, []);

  // Sync forceOpen prop → open + centered
  useEffect(() => {
    if (forceOpen) {
      setOpen(true);
      setCentered(true);
    }
  }, [forceOpen]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input when open
  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 120);
  }, [open]);

  // Greeting on first open (after consent)
  useEffect(() => {
    if (open && consent && !greeted && messages.length === 0) {
      setGreeted(true);
      const greeting = buildGreeting();
      setMessages([{ role: "assistant", text: greeting, timestamp: Date.now() }]);
      if (ttsEnabled) speakText(greeting);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, consent, greeted, messages.length]);

  // ── TTS ──────────────────────────────────────────────────────────────────
  const speakText = useCallback(
    async (text: string) => {
      if (!ttsEnabled) return;
      setAudioLoading(true);
      try {
        const res = await fetch(`${API_BASE}/tts`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: text.slice(0, 300), language: "en" }),
        });
        if (!res.ok) throw new Error("TTS failed");
        const blob = await res.blob();
        const url  = URL.createObjectURL(blob);
        if (audioRef.current) {
          audioRef.current.pause();
          URL.revokeObjectURL(audioRef.current.src);
        }
        const audio = new Audio(url);
        audioRef.current = audio;
        audio.play();
      } catch (e) {
        console.warn("[KaalChat] TTS failed:", e);
      } finally {
        setAudioLoading(false);
      }
    },
    [ttsEnabled]
  );

  // ── Send message ──────────────────────────────────────────────────────────
  const sendMessage = useCallback(async () => {
    const text = input.trim();
    if (!text || loading || remaining <= 0) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", text, timestamp: Date.now() }]);
    setLoading(true);

    // After user sends first message, collapse from centered to corner
    if (centered) {
      setCentered(false);
      onFirstVisitDone?.();
    }

    try {
      const res = await fetch(`${API_BASE}/chat/demo`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          session_id: getSessionId(),
          consent: consent === "accepted",
        }),
      });

      if (res.status === 429) {
        const data = await res.json();
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            text:
              data.message ||
              "You've used all demo messages. Get an API key for unlimited access!",
            timestamp: Date.now(),
          },
        ]);
        setRemaining(0);
        return;
      }

      const data     = await res.json();
      const response = data.response || "I couldn't generate a response right now.";
      setRemaining(data.messages_remaining ?? remaining - 1);

      const cardMatch   = response.match(/\[SHOW:(\w+)\]/);
      const cleanedCard = response.replace(/\[SHOW:\w+\]/g, "").trim();
      const cleanFinal  = cleanedCard.replace(/\[SPOTLIGHT:\w+\]/g, "").trim();
      const cardKey     = cardMatch ? cardMatch[1] : undefined;

      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: cleanFinal, card: cardKey, timestamp: Date.now() },
      ]);
      if (ttsEnabled) speakText(cleanFinal);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "Network error. Make sure you're connected and try again.",
          timestamp: Date.now(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  }, [input, loading, remaining, consent, ttsEnabled, speakText, centered, onFirstVisitDone]);

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const toggleTts = () => {
    const next = !ttsEnabled;
    setTtsEnabled(next);
    localStorage.setItem("kaal_tts_enabled", String(next));
    if (!next && audioRef.current) audioRef.current.pause();
  };

  const handleConsent = (accepted: boolean) => {
    const choice = accepted ? "accepted" : "declined";
    setConsent(choice);
    localStorage.setItem("kaal_chat_consent", choice);
  };

  // Collapse from centered to corner when user clicks minimize
  const handleClose = () => {
    if (centered) {
      setCentered(false);
      onFirstVisitDone?.();
    }
    setOpen(false);
  };

  // ── Panel position classes ────────────────────────────────────────────────
  // centered = full-screen backdrop + centered card
  // corner   = fixed bottom-right bubble

  return (
    <>
      {/* ── Centered greeting overlay (first visit) ──────────────────── */}
      {open && centered && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 9998,
            background: "rgba(0,0,0,0.45)",
            backdropFilter: "blur(4px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            animation: "fadeIn 0.3s ease",
          }}
          onClick={(e) => { if (e.target === e.currentTarget) handleClose(); }}
        >
          <div
            style={{
              width: "100%",
              maxWidth: 460,
              maxHeight: 600,
              display: "flex",
              flexDirection: "column",
              background: "#fff",
              border: "1px solid #eaeaea",
              borderRadius: 20,
              boxShadow: "0 32px 80px rgba(0,0,0,0.18)",
              overflow: "hidden",
              animation: "slideUp 0.35s cubic-bezier(0.34,1.56,0.64,1)",
            }}
          >
            {renderChatContent()}
          </div>
        </div>
      )}

      {/* ── Corner bubble (normal mode) ───────────────────────────────── */}
      {!centered && (
        <>
          <button
            onClick={() => setOpen((o) => !o)}
            className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-black text-white rounded-full flex items-center justify-center shadow-lg hover:scale-105 transition-transform"
            aria-label="Open Kaal Chat"
          >
            {open ? <X className="w-5 h-5" /> : <MessageCircle className="w-5 h-5" />}
            {remaining < 5 && remaining > 0 && !open && (
              <span className="absolute -top-1 -right-1 w-5 h-5 bg-white text-black text-[10px] font-bold rounded-full flex items-center justify-center border border-black">
                {remaining}
              </span>
            )}
          </button>

          {open && (
            <div className="fixed bottom-24 right-6 z-50 w-[380px] max-h-[580px] flex flex-col bg-white border border-[#eaeaea] rounded-2xl shadow-2xl overflow-hidden">
              {renderChatContent()}
            </div>
          )}
        </>
      )}

      <style>{`
        @keyframes fadeIn  { from { opacity:0 } to { opacity:1 } }
        @keyframes slideUp { from { opacity:0; transform:translateY(20px) scale(0.97) } to { opacity:1; transform:translateY(0) scale(1) } }
      `}</style>
    </>
  );

  // ── Shared chat content ────────────────────────────────────────────────
  function renderChatContent() {
    return (
      <>
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-[#eaeaea] bg-white flex-shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-2 h-2 rounded-full bg-black animate-pulse" />
            <span className="text-sm font-semibold text-black">Kaal</span>
            <span className="text-[10px] text-[#999] uppercase tracking-wider font-medium">
              {centered ? "Smriti · Memory by Kaal" : "Smriti · by Kaal"}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-[#999] font-medium">{remaining}/5 left</span>
            <button
              onClick={toggleTts}
              className={`p-1.5 rounded-md transition-colors ${ttsEnabled ? "bg-black text-white" : "text-[#999] hover:text-black"}`}
              title={ttsEnabled ? "Mute Kaal" : "Enable Kaal voice"}
            >
              {audioLoading
                ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                : ttsEnabled
                ? <Volume2 className="w-3.5 h-3.5" />
                : <VolumeX className="w-3.5 h-3.5" />}
            </button>
            <button onClick={handleClose} className="text-[#999] hover:text-black transition-colors p-1">
              <ChevronDown className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Consent */}
        {!consent && (
          <div className="flex-1 flex flex-col items-center justify-center p-6 text-center gap-4">
            <div className="text-2xl">🧠</div>
            <h3 className="text-sm font-semibold text-black">Before we chat</h3>
            <p className="text-xs text-[#666] leading-relaxed">
              May Kaal save this conversation anonymously to improve its AI? Your data is never shared.
            </p>
            <div className="flex gap-2 w-full">
              <button
                onClick={() => handleConsent(true)}
                className="flex-1 py-2 bg-black text-white text-xs font-medium rounded-lg hover:opacity-80 transition-opacity"
              >
                Accept & Chat
              </button>
              <button
                onClick={() => handleConsent(false)}
                className="flex-1 py-2 border border-[#eaeaea] text-[#666] text-xs font-medium rounded-lg hover:border-black hover:text-black transition-colors"
              >
                Chat without saving
              </button>
            </div>
          </div>
        )}

        {/* Messages */}
        {consent && (
          <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-[280px]">
            {messages.map((msg, i) => (
              <div key={i} className={`flex flex-col gap-1 ${msg.role === "user" ? "items-end" : "items-start"}`}>
                <div
                  className={`max-w-[85%] px-3.5 py-2.5 rounded-2xl text-sm leading-relaxed ${
                    msg.role === "user"
                      ? "bg-black text-white rounded-br-sm"
                      : "bg-[#fafafa] border border-[#eaeaea] text-black rounded-bl-sm"
                  }`}
                >
                  {msg.text}
                </div>
                {msg.card && FEATURE_CARDS[msg.card] && (
                  <div className="max-w-[85%] mt-1 border border-[#eaeaea] rounded-xl overflow-hidden bg-white">
                    <div className="px-3 py-2 bg-black text-white text-[10px] font-semibold uppercase tracking-wider">
                      {FEATURE_CARDS[msg.card].title}
                    </div>
                    <div className="px-3 py-2.5 font-mono text-[11px] text-[#333] space-y-1">
                      {FEATURE_CARDS[msg.card].lines.map((line, j) => (
                        <div key={j} className={line.startsWith("→") ? "text-[#0a8f44]" : "text-[#333]"}>
                          {line}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex items-start">
                <div className="bg-[#fafafa] border border-[#eaeaea] rounded-2xl rounded-bl-sm px-4 py-3">
                  <div className="flex gap-1 items-center">
                    <div className="w-1.5 h-1.5 bg-[#999] rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                    <div className="w-1.5 h-1.5 bg-[#999] rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                    <div className="w-1.5 h-1.5 bg-[#999] rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                </div>
              </div>
            )}

            {remaining === 0 && (
              <div className="text-center py-2">
                <span className="text-xs text-black underline underline-offset-2 font-medium">
                  Get an API key for unlimited access →
                </span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Input */}
        {consent && (
          <div className="border-t border-[#eaeaea] px-3 py-2.5 flex items-center gap-2 bg-white flex-shrink-0">
            <input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKey}
              disabled={loading || remaining <= 0}
              placeholder={remaining <= 0 ? "Get an API key to continue..." : "Ask about Kaal…"}
              className="flex-1 text-sm bg-[#fafafa] border border-[#eaeaea] rounded-lg px-3 py-2 outline-none focus:border-black focus:bg-white transition-all disabled:opacity-40 disabled:cursor-not-allowed"
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim() || remaining <= 0}
              className="w-8 h-8 bg-black text-white rounded-lg flex items-center justify-center disabled:opacity-30 hover:opacity-80 transition-opacity flex-shrink-0"
            >
              {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
            </button>
          </div>
        )}

        {/* Footer */}
        {consent && (
          <div className="px-4 pb-2 text-center flex-shrink-0">
              <span className="text-[9px] text-[#bbb]">
                {consent === "accepted" ? "📖 Chats saved for AI training · " : ""}
                Smriti · Temporal Memory by Kaal
              </span>
          </div>
        )}
      </>
    );
  }
}
