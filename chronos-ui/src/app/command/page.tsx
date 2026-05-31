"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search, Zap, Hexagon, Settings, Key, BarChart2,
  Clock, Link, ChevronRight, Database,
  Terminal, X, Command, MessageSquare,
  Grid3X3, List, User, Bot, Brain, Cpu
} from "lucide-react";

/* ─── Types ──────────────────────────────────────────────── */
type View = "list" | "grid" | "ai";

interface Action {
  id: string;
  icon: React.ElementType;
  label: string;
  description: string;
  shortcut?: string;
  category: string;
  view?: View;
}

interface MemoryCard {
  id: string;
  subject: string;
  verb: string;
  object: string;
  time: string;
  tag: string;
}

/* ─── Data ──────────────────────────────────────────────── */
const ACTIONS: Action[] = [
  { id: "query",      icon: Search,    label: "Query Memory",      description: "Semantic + temporal search across all events",      shortcut: "Q", category: "Memory"    },
  { id: "ingest",     icon: Zap,       label: "Ingest Event",       description: "Write a new memory event into Kaal",             shortcut: "I", category: "Memory"    },
  { id: "timeline",   icon: Clock,     label: "View Timeline",      description: "Browse all events in a chronological grid",         shortcut: "T", category: "Memory",   view: "grid" },
  { id: "agent",      icon: Cpu,       label: "Run Agent",          description: "Reason over your memory with GPT OSS 120B",         shortcut: "A", category: "Agent",    view: "ai"   },
  { id: "connect",    icon: Link,      label: "Connect Tool",       description: "Register a SaaS API for the agent to call",                        category: "Agent"    },
  { id: "connectors", icon: Database,  label: "View Connectors",    description: "List all registered agent tools",                                    category: "Agent"    },
  { id: "overview",   icon: Hexagon,   label: "Overview",           description: "System health, stats, and getting started",         shortcut: "O", category: "Navigate"  },
  { id: "usage",      icon: BarChart2, label: "Usage & Billing",    description: "Track event and orchestration usage",                               category: "Navigate"  },
  { id: "keys",       icon: Key,       label: "API Keys",           description: "Generate and manage API keys",                      shortcut: "K", category: "Navigate"  },
  { id: "docs",       icon: Terminal,  label: "Documentation",      description: "API reference and integration guides",                              category: "Developer" },
  { id: "settings",   icon: Settings,  label: "Settings",           description: "Configure your workspace and preferences",                          category: "Developer" },
];

const MEMORY_CARDS: MemoryCard[] = [
  { id: "1", subject: "Ali",    verb: "closed",    object: "deal with Acme Corp",        time: "2h ago",  tag: "Sales"       },
  { id: "2", subject: "Team",   verb: "shipped",   object: "v2.0 of the API",            time: "5h ago",  tag: "Engineering" },
  { id: "3", subject: "Sarah",  verb: "called",    object: "3 enterprise prospects",     time: "1d ago",  tag: "Sales"       },
  { id: "4", subject: "System", verb: "ingested",  object: "1,240 events this week",     time: "1d ago",  tag: "Memory"      },
  { id: "5", subject: "Agent",  verb: "predicted", object: "Q2 revenue at ₹85k",         time: "2d ago",  tag: "AI"          },
  { id: "6", subject: "Reman",  verb: "connected", object: "Google Sheets tool",         time: "3d ago",  tag: "Tools"       },
];

const AI_RESPONSE = `Based on your Kaal memory context:

**Recent Activity Summary**
Ali closed a deal with Acme Corp 2 hours ago.
Sarah reached 3 enterprise prospects yesterday.
12 total interactions were logged this month.

**Revenue Forecast**
Q2 trajectory suggests ₹85,000 based on current deal velocity — a 23% increase over Q1.

**Recommended Actions**
→ Follow up with Acme Corp for an upsell opportunity
→ Sarah's pipeline has 2 warm leads — schedule callbacks
→ Ingest this week's call notes to improve accuracy

Powered by GPT OSS 120B · Cerebras`;

const PROVIDERS = ["GPT OSS 120B", "Llama 3.3 70B", "Groq Fallback"];

/* ─── Subtle animated background ────────────────────────── */
function Background() {
  return (
    <div className="fixed inset-0 z-0 bg-black">
      {/* Very subtle noise grain via CSS */}
      <div className="absolute inset-0 opacity-[0.4]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.05'/%3E%3C/svg%3E")`,
        }}
      />
      {/* Barely-there radial vignette */}
      <div className="absolute inset-0"
        style={{
          background: "radial-gradient(ellipse 70% 60% at 50% 40%, rgba(255,255,255,0.015) 0%, transparent 70%)",
        }}
      />
      {/* Faint grid lines */}
      <div className="absolute inset-0 opacity-[0.025]"
        style={{
          backgroundImage: "linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)",
          backgroundSize: "80px 80px",
        }}
      />
    </div>
  );
}

/* ─── Typewriter ─────────────────────────────────────────── */
function Typewriter({ text }: { text: string }) {
  const [displayed, setDisplayed] = useState("");
  useEffect(() => {
    setDisplayed("");
    let i = 0;
    const timer = setInterval(() => {
      if (i < text.length) { setDisplayed(text.slice(0, i + 1)); i++; }
      else clearInterval(timer);
    }, 10);
    return () => clearInterval(timer);
  }, [text]);

  return (
    <div className="text-[13px] leading-6 text-white/60 font-mono whitespace-pre-wrap">
      {displayed.split("\n").map((line, i) => {
        const html = line.replace(/\*\*(.*?)\*\*/g, "<span class='text-white/90 font-semibold'>$1</span>").replace(/^→ /, '<span class="text-white/30">→ </span>');
        return <p key={i} className="min-h-[1.5rem]" dangerouslySetInnerHTML={{ __html: html }} />;
      })}
      <span className="inline-block w-[6px] h-[13px] bg-white/50 ml-px animate-pulse" />
    </div>
  );
}

/* ─── Single action row ──────────────────────────────────── */
function ActionRow({ action, isSelected, onClick }: {
  action: Action; isSelected: boolean; onClick: () => void;
}) {
  const Icon = action.icon;
  return (
    <motion.div
      onClick={onClick}
      className="relative flex items-center gap-3 px-3 py-2 cursor-pointer mx-2 rounded-lg"
    >
      {isSelected && (
        <motion.div
          layoutId="highlight"
          className="absolute inset-0 rounded-lg bg-white/[0.07]"
          transition={{ type: "spring", stiffness: 500, damping: 40 }}
        />
      )}
      <div className="relative w-7 h-7 rounded-md bg-white/[0.06] border border-white/[0.08] flex items-center justify-center flex-shrink-0">
        <Icon size={13} className="text-white/50" />
      </div>
      <div className="relative flex-1 min-w-0">
        <span className="text-[13px] font-medium text-white/80">{action.label}</span>
        <span className="text-[11px] text-white/30 ml-2 hidden sm:inline">{action.description}</span>
      </div>
      {action.shortcut && (
        <kbd className="relative text-[10px] text-white/20 bg-white/[0.04] border border-white/[0.08] rounded px-1.5 py-0.5 font-mono flex-shrink-0">
          {action.shortcut}
        </kbd>
      )}
      <ChevronRight size={11} className="relative text-white/[0.15] flex-shrink-0" />
    </motion.div>
  );
}

/* ─── Main ───────────────────────────────────────────────── */
export default function CommandInterface() {
  const [open, setOpen]                 = useState(true);
  const [query, setQuery]               = useState("");
  const [view, setView]                 = useState<View>("list");
  const [selected, setSelected]         = useState(0);
  const [aiQuery, setAiQuery]           = useState("");
  const [showAi, setShowAi]             = useState(false);
  const [provider, setProvider]         = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const filtered = ACTIONS.filter(a =>
    !query || a.label.toLowerCase().includes(query.toLowerCase()) || a.description.toLowerCase().includes(query.toLowerCase())
  );
  const grouped  = filtered.reduce((acc, a) => { (acc[a.category] = acc[a.category] || []).push(a); return acc; }, {} as Record<string, Action[]>);
  const flat     = Object.values(grouped).flat();

  const pick = useCallback((action: Action) => {
    if (action.view === "grid") { setView("grid"); }
    else if (action.view === "ai") {
      setAiQuery(query || "Summarize recent memory and forecast revenue");
      setShowAi(true); setView("ai");
    }
  }, [query]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") { e.preventDefault(); setOpen(o => !o); setQuery(""); setView("list"); setShowAi(false); setSelected(0); }
      if (!open) return;
      if (e.key === "Escape") { if (showAi || view !== "list") { setView("list"); setShowAi(false); } else setOpen(false); }
      if (view === "list" && !showAi) {
        if (e.key === "ArrowDown") { e.preventDefault(); setSelected(i => Math.min(i + 1, flat.length - 1)); }
        if (e.key === "ArrowUp")   { e.preventDefault(); setSelected(i => Math.max(i - 1, 0)); }
        if (e.key === "Enter")     { e.preventDefault(); if (flat[selected]) pick(flat[selected]); }
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, view, showAi, flat, selected, pick]);

  useEffect(() => { if (open) setTimeout(() => inputRef.current?.focus(), 40); }, [open]);
  useEffect(() => { setSelected(0); }, [query]);

  return (
    <>
      <Background />

      {/* Collapsed hint */}
      <AnimatePresence>
        {!open && (
          <motion.button
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2.5 px-4 py-2 rounded-xl"
            style={{ background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.08)", backdropFilter: "blur(16px)" }}
            onClick={() => setOpen(true)}
          >
            <Hexagon size={12} className="text-white/40" strokeWidth={1.5} />
            <span className="text-xs text-white/40 font-medium">Kaal Command</span>
            <div className="flex gap-1 ml-1">
              {["⌘","K"].map(k => <kbd key={k} className="text-[10px] text-white/20 bg-white/[0.04] border border-white/[0.07] rounded px-1 py-0.5 font-mono">{k}</kbd>)}
            </div>
          </motion.button>
        )}
      </AnimatePresence>

      {/* Modal */}
      <AnimatePresence>
        {open && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center p-6"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          >
            <div className="absolute inset-0" onClick={() => setOpen(false)} />

            <motion.div
              initial={{ opacity: 0, scale: 0.97, y: -6 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.97, y: -6 }}
              transition={{ type: "spring", stiffness: 600, damping: 40 }}
              className="relative w-full max-w-xl overflow-hidden rounded-2xl"
              style={{
                background: "rgba(12,12,12,0.92)",
                border: "1px solid rgba(255,255,255,0.09)",
                backdropFilter: "blur(48px)",
                boxShadow: "0 0 0 1px rgba(255,255,255,0.03) inset, 0 24px 80px rgba(0,0,0,0.9), 0 2px 0 rgba(255,255,255,0.05) inset",
              }}
            >
              {/* Top shine line */}
              <div className="absolute top-0 left-6 right-6 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

              {/* ── Search bar ── */}
              <div className="flex items-center gap-3 px-4 py-3.5 border-b border-white/[0.06]">
                {showAi
                  ? <Brain size={15} className="text-white/30 flex-shrink-0" strokeWidth={1.5} />
                  : <Search size={15} className="text-white/25 flex-shrink-0" strokeWidth={1.5} />
                }
                {showAi ? (
                  <div className="flex-1 text-[13px] text-white/50 font-medium truncate">{aiQuery}</div>
                ) : (
                  <input
                    ref={inputRef}
                    value={query}
                    onChange={e => setQuery(e.target.value)}
                    placeholder={view === "grid" ? "Browse memory events..." : "Query memory, run agent, connect tools..."}
                    className="flex-1 bg-transparent text-[13px] text-white/80 placeholder-white/20 outline-none font-medium"
                  />
                )}
                <div className="flex items-center gap-1.5 flex-shrink-0">
                  {/* View toggles */}
                  {[
                    { v: "list" as View, Icon: List,     label: "List"  },
                    { v: "grid" as View, Icon: Grid3X3,  label: "Grid"  },
                    { v: "ai"   as View, Icon: Brain,    label: "Agent" },
                  ].map(({ v, Icon: I }) => (
                    <button key={v}
                      onClick={() => { setView(v); if (v === "ai") { setAiQuery(query || "Summarize recent activity"); setShowAi(true); } else setShowAi(false); }}
                      className={`p-1.5 rounded-md transition-all ${(view === v && (v !== "ai" || showAi)) || (v === "ai" && showAi) ? "text-white/70 bg-white/[0.07]" : "text-white/20 hover:text-white/40"}`}
                    >
                      <I size={12} strokeWidth={1.5} />
                    </button>
                  ))}
                  <div className="w-px h-3.5 bg-white/[0.08] mx-1" />
                  <button onClick={() => setOpen(false)} className="p-1.5 text-white/15 hover:text-white/40 transition-colors rounded-md">
                    <X size={12} strokeWidth={1.5} />
                  </button>
                </div>
              </div>

              {/* ── Body ── */}
              <div style={{ maxHeight: 420 }} className="overflow-hidden">
                <AnimatePresence mode="wait">

                  {/* LIST */}
                  {view === "list" && !showAi && (
                    <motion.div key="list"
                      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                      transition={{ duration: 0.12 }}
                      className="overflow-y-auto py-2"
                      style={{ maxHeight: 420 }}
                    >
                      {Object.entries(grouped).map(([cat, actions]) => (
                        <div key={cat}>
                          <p className="px-5 pt-3 pb-1 text-[10px] font-semibold text-white/20 uppercase tracking-[0.12em]">{cat}</p>
                          {actions.map(a => {
                            const idx = flat.indexOf(a);
                            return (
                              <ActionRow key={a.id} action={a} isSelected={selected === idx}
                                onClick={() => { setSelected(idx); pick(a); }}
                              />
                            );
                          })}
                        </div>
                      ))}
                      {flat.length === 0 && (
                        <div className="flex flex-col items-center justify-center py-16 gap-3">
                          <Search size={20} className="text-white/10" />
                          <p className="text-xs text-white/20">No results for "{query}"</p>
                        </div>
                      )}
                    </motion.div>
                  )}

                  {/* GRID */}
                  {view === "grid" && (
                    <motion.div key="grid"
                      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                      transition={{ duration: 0.12 }}
                      className="p-4 overflow-y-auto"
                      style={{ maxHeight: 420 }}
                    >
                      <div className="grid grid-cols-2 gap-2">
                        {MEMORY_CARDS.map((card, i) => (
                          <motion.div key={card.id}
                            initial={{ opacity: 0, y: 8 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.035 }}
                            whileHover={{ scale: 1.015 }}
                            className="p-3.5 rounded-xl cursor-pointer"
                            style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.07)" }}
                          >
                            <div className="flex items-center justify-between mb-2.5">
                              <span className="text-[9px] font-semibold uppercase tracking-wider text-white/30 bg-white/[0.05] px-2 py-0.5 rounded-full border border-white/[0.07]">
                                {card.tag}
                              </span>
                              <span className="text-[10px] text-white/20">{card.time}</span>
                            </div>
                            <p className="text-xs text-white/60 leading-5">
                              <span className="text-white/80 font-medium">{card.subject}</span>
                              {" "}{card.verb}{" "}
                              {card.object}
                            </p>
                          </motion.div>
                        ))}
                      </div>
                    </motion.div>
                  )}

                  {/* AI */}
                  {(view === "ai" || showAi) && (
                    <motion.div key="ai"
                      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                      transition={{ duration: 0.12 }}
                      className="flex flex-col"
                      style={{ maxHeight: 420 }}
                    >
                      {/* User turn */}
                      <div className="px-5 pt-4 pb-3.5 border-b border-white/[0.05]">
                        <div className="flex items-start gap-3">
                          <div className="w-6 h-6 rounded-full bg-white/[0.07] border border-white/[0.09] flex items-center justify-center flex-shrink-0 mt-0.5">
                            <User size={11} className="text-white/40" />
                          </div>
                          <p className="text-[13px] text-white/50 font-medium leading-5 pt-0.5">
                            {aiQuery}
                          </p>
                        </div>
                      </div>

                      {/* Agent turn */}
                      <div className="px-5 pt-4 pb-2 overflow-y-auto flex-1">
                        <div className="flex items-start gap-3">
                          <div className="w-6 h-6 rounded-full bg-white/[0.05] border border-white/[0.08] flex items-center justify-center flex-shrink-0 mt-0.5">
                            <Hexagon size={11} className="text-white/40" strokeWidth={1.5} />
                          </div>
                          <Typewriter text={AI_RESPONSE} />
                        </div>
                      </div>

                      {/* Provider pills */}
                      <div className="px-5 py-3 border-t border-white/[0.05] flex items-center gap-2">
                        <span className="text-[9px] text-white/20 uppercase tracking-widest mr-1">Model</span>
                        {PROVIDERS.map((p, i) => (
                          <button key={p} onClick={() => setProvider(i)}
                            className="px-2.5 py-1 rounded-full text-[11px] transition-all"
                            style={{
                              background: provider === i ? "rgba(255,255,255,0.08)" : "transparent",
                              border: `1px solid ${provider === i ? "rgba(255,255,255,0.15)" : "rgba(255,255,255,0.06)"}`,
                              color: provider === i ? "rgba(255,255,255,0.65)" : "rgba(255,255,255,0.2)",
                            }}
                          >
                            {p}
                          </button>
                        ))}
                        <div className="flex-1" />
                        <div className="flex items-center gap-1.5 text-[10px] text-white/20">
                          <span className="w-1.5 h-1.5 rounded-full bg-white/40 animate-pulse" />
                          Streaming
                        </div>
                      </div>
                    </motion.div>
                  )}

                </AnimatePresence>
              </div>

              {/* ── Footer ── */}
              <div className="px-5 py-2.5 border-t border-white/[0.06] flex items-center justify-between">
                <div className="flex items-center gap-4 text-[10px] text-white/15">
                  {[["↑↓","navigate"],["↵","select"],["esc","close"]].map(([k,l]) => (
                    <span key={l} className="flex items-center gap-1">
                      <kbd className="bg-white/[0.04] border border-white/[0.07] rounded px-1 py-0.5 font-mono">{k}</kbd>
                      {l}
                    </span>
                  ))}
                </div>
                <div className="flex items-center gap-1.5 text-[10px] text-white/15">
                  <Hexagon size={9} strokeWidth={1.5} />
                  <span>Kaal</span>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
