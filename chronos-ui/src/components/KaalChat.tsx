"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { MessageCircle, X, Volume2, VolumeX, Send, Loader2, ChevronDown } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://spy9191-chronos-api-backend.hf.space";

// Generate a stable session ID per browser session
function getSessionId() {
  if (typeof window === "undefined") return "ssr";
  let id = sessionStorage.getItem("kaal_session_id");
  if (!id) {
    id = `sess_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
    sessionStorage.setItem("kaal_session_id", id);
  }
  return id;
}

// Feature cards shown inline when AI uses [SHOW:card_name]
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

type Message = {
  role: "user" | "assistant";
  text: string;
  card?: string; // if assistant suggests [SHOW:card_name]
  timestamp: number;
};

type Consent = "accepted" | "declined" | null;

export function KaalChat() {
  const [open, setOpen] = useState(false);
  const [consent, setConsent] = useState<Consent>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [ttsEnabled, setTtsEnabled] = useState(false);
  const [remaining, setRemaining] = useState(5);
  const [greeted, setGreeted] = useState(false);
  const [audioLoading, setAudioLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Load state from localStorage
  useEffect(() => {
    const savedConsent = localStorage.getItem("kaal_chat_consent") as Consent;
    if (savedConsent) setConsent(savedConsent);
    const savedTts = localStorage.getItem("kaal_tts_enabled");
    if (savedTts) setTtsEnabled(savedTts === "true");
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 100);
  }, [open]);

  // Greeting on first open (after consent)
  useEffect(() => {
    if (open && consent && !greeted && messages.length === 0) {
      setGreeted(true);
      const greeting = "Hi there! I'm Kaal — your temporal memory engine. I can show you how to ingest events, run queries, orchestrate agents, and connect tools. What would you like to know?";
      setMessages([{ role: "assistant", text: greeting, timestamp: Date.now() }]);
      if (ttsEnabled) speakText(greeting);
    }
  }, [open, consent, greeted, messages.length, ttsEnabled]);

  const speakText = useCallback(async (text: string) => {
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
      const url = URL.createObjectURL(blob);
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
  }, [ttsEnabled]);

  const sendMessage = useCallback(async () => {
    const text = input.trim();
    if (!text || loading || remaining <= 0) return;

    setInput("");
    setMessages(prev => [...prev, { role: "user", text, timestamp: Date.now() }]);
    setLoading(true);

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
        setMessages(prev => [...prev, {
          role: "assistant",
          text: data.message || "You've used all demo messages. Get an API key for unlimited access!",
          timestamp: Date.now(),
        }]);
        setRemaining(0);
        return;
      }

      const data = await res.json();
      const response = data.response || "I couldn't generate a response right now.";
      setRemaining(data.messages_remaining ?? remaining - 1);

      // Detect [SHOW:card] tags in response
      const cardMatch = response.match(/\[SHOW:(\w+)\]/);
      const cleanResponse = response.replace(/\[SHOW:\w+\]/g, "").trim();
      const cardKey = cardMatch ? cardMatch[1] : undefined;

      // Detect [SPOTLIGHT:id] but just clean for now
      const cleanFinal = cleanResponse.replace(/\[SPOTLIGHT:\w+\]/g, "").trim();

      setMessages(prev => [...prev, {
        role: "assistant",
        text: cleanFinal,
        card: cardKey,
        timestamp: Date.now(),
      }]);

      if (ttsEnabled) speakText(cleanFinal);
    } catch (e: any) {
      setMessages(prev => [...prev, {
        role: "assistant",
        text: "Network error. Make sure you're connected and try again.",
        timestamp: Date.now(),
      }]);
    } finally {
      setLoading(false);
    }
  }, [input, loading, remaining, consent, ttsEnabled, speakText]);

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

  return (
    <>
      {/* Floating bubble button */}
      <button
        onClick={() => setOpen(o => !o)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-black text-white rounded-full flex items-center justify-center shadow-lg hover:scale-105 transition-transform"
        aria-label="Open Kaal Chat"
      >
        {open
          ? <X className="w-5 h-5" />
          : <MessageCircle className="w-5 h-5" />
        }
        {remaining < 5 && remaining > 0 && !open && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-white text-black text-[10px] font-bold rounded-full flex items-center justify-center border border-black">
            {remaining}
          </span>
        )}
      </button>

      {/* Chat panel */}
      {open && (
        <div className="fixed bottom-24 right-6 z-50 w-[380px] max-h-[600px] flex flex-col bg-white border border-[#eaeaea] rounded-2xl shadow-2xl overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-[#eaeaea] bg-white">
            <div className="flex items-center gap-2.5">
              <div className="w-2 h-2 rounded-full bg-black animate-pulse" />
              <span className="text-sm font-semibold text-black">Kaal</span>
              <span className="text-[10px] text-[#999] uppercase tracking-wider font-medium">AI Guide</span>
            </div>
            <div className="flex items-center gap-2">
              {/* Messages remaining badge */}
              <span className="text-[10px] text-[#999] font-medium">
                {remaining}/5 left
              </span>
              {/* TTS toggle */}
              <button
                onClick={toggleTts}
                className={`p-1.5 rounded-md transition-colors ${ttsEnabled ? "bg-black text-white" : "text-[#999] hover:text-black"}`}
                title={ttsEnabled ? "Mute Kaal's voice" : "Enable Kaal's voice"}
              >
                {audioLoading
                  ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  : ttsEnabled
                  ? <Volume2 className="w-3.5 h-3.5" />
                  : <VolumeX className="w-3.5 h-3.5" />
                }
              </button>
              <button onClick={() => setOpen(false)} className="text-[#999] hover:text-black transition-colors p-1">
                <ChevronDown className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Consent modal (first time) */}
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
            <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-[300px]">
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

                  {/* Feature card */}
                  {msg.card && FEATURE_CARDS[msg.card] && (
                    <div className="max-w-[85%] mt-1 border border-[#eaeaea] rounded-xl overflow-hidden bg-white">
                      <div className="px-3 py-2 bg-black text-white text-[10px] font-semibold uppercase tracking-wider">
                        {FEATURE_CARDS[msg.card].title}
                      </div>
                      <div className="px-3 py-2.5 font-mono text-[11px] text-[#333] space-y-1">
                        {FEATURE_CARDS[msg.card].lines.map((line, j) => (
                          <div
                            key={j}
                            className={`${line.startsWith("→") ? "text-[#0a8f44]" : "text-[#333]"}`}
                          >
                            {line}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {/* Typing indicator */}
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

              {/* Rate limit message */}
              {remaining === 0 && (
                <div className="text-center py-2">
                  <a
                    href="#"
                    onClick={(e) => { e.preventDefault(); }}
                    className="text-xs text-black underline underline-offset-2 font-medium"
                  >
                    Get an API key for unlimited access →
                  </a>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}

          {/* Input area */}
          {consent && (
            <div className="border-t border-[#eaeaea] px-3 py-2.5 flex items-center gap-2 bg-white">
              <input
                ref={inputRef}
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKey}
                disabled={loading || remaining <= 0}
                placeholder={remaining <= 0 ? "Get an API key to continue..." : "Ask about Kaal..."}
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
            <div className="px-4 pb-2 text-center">
              <span className="text-[9px] text-[#bbb]">
                {consent === "accepted" ? "📖 Chats saved for AI training · " : ""}
                Powered by GPT OSS 120B
              </span>
            </div>
          )}
        </div>
      )}
    </>
  );
}
