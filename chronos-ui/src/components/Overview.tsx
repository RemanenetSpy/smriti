"use client";

import { useState, useEffect } from "react";
import { apiCall } from "@/lib/api";
import { Key, Activity, Search, Cpu, Hexagon, ChevronRight, ChevronDown, ArrowRight, Plug } from "lucide-react";

// ── Steps ──────────────────────────────────────────────────────────────────────
const STEPS = [
  {
    id: "keys",
    Icon: Key,
    title: "Get your API Key",
    section: "API Keys",
    description: "Go to API Keys in the sidebar. Generate your first key — attach it as the Authorization header on every request.",
    code: `curl -H "Authorization: Bearer YOUR_KEY" \\
  https://spy9191-chronos-api-backend.hf.space/health`,
  },
  {
    id: "mcp",
    Icon: Plug,
    title: "Connect via MCP (Claude / Cursor)",
    section: "MCP Server",
    description: "Use Model Context Protocol to connect Smriti directly to Claude Desktop or Cursor IDE with zero code.",
    code: `pip install -r mcp/requirements.txt
export SMRITI_API_KEY="chrn_your_key"
python -m smriti.mcp`,
  },
  {
    id: "ingest",
    Icon: Activity,
    title: "Ingest your first event",
    section: "Ingest Events",
    description: "Send raw text. Smriti extracts Subject-Verb-Object tuples and stores them with timestamps automatically.",
    code: `POST /ingest
{ "source_id": "my-app", "events": [{"text": "Acme Corp signed a $50k contract"}] }`,
  },
  {
    id: "query",
    Icon: Search,
    title: "Query your memory",
    section: "Query Memory",
    description: "Ask natural-language questions. Smriti runs hybrid temporal + semantic search and returns ranked results.",
    code: `POST /query
{ "query": "What happened with Acme Corp?" }`,
  },
  {
    id: "agent",
    Icon: Cpu,
    title: "Run an Agent",
    section: "Agent Chat",
    description: "A LangGraph agent with your entire memory as context. Ask complex questions or trigger tools — it reasons across time.",
    code: `POST /agent/run
{ "prompt": "Summarise all Q2 deals and flag any risks" }`,
  },
  {
    id: "connect",
    Icon: Hexagon,
    title: "Connect a tool",
    section: "Connect Tool",
    description: "Register SaaS tools (Stripe, Notion, CRM). The Agent calls them mid-conversation and stores results as new events.",
    code: `POST /connectors/register
{ "name": "Stripe", "base_url": "https://api.stripe.com", "endpoints": [...] }`,
  },
];

const ACTIONS = [
  { id: "ingest", Icon: Activity, label: "Ingest an Event",  sub: "Send text → Smriti stores it as structured memory" },
  { id: "query",  Icon: Search,   label: "Query Memory",     sub: "Ask a question → get ranked results across all events" },
  { id: "agent",  Icon: Cpu,      label: "Run Agent",        sub: "Let the AI reason across your full memory context" },
];

function QuickStart() {
  const [open, setOpen] = useState(false);
  const [openStep, setOpenStep] = useState<string | null>(null);
  const [done, setDone] = useState<Set<string>>(new Set());

  const toggleDone = (id: string, e: React.MouseEvent | React.KeyboardEvent) => {
    e.stopPropagation();
    setDone((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const pct = Math.round((done.size / STEPS.length) * 100);

  return (
    <div className="border border-[#eaeaea] rounded-xl bg-white overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center gap-3 px-4 py-3 hover:bg-[#fafafa] transition-colors text-left"
      >
        <div className="flex items-center gap-2 flex-1 min-w-0">
          {open
            ? <ChevronDown className="w-3.5 h-3.5 text-[#999] flex-shrink-0" />
            : <ChevronRight className="w-3.5 h-3.5 text-[#999] flex-shrink-0" />
          }
          <span className="text-sm font-medium text-black">Quick Start</span>
          <span className="text-xs text-[#aaa]">{done.size}/{STEPS.length} steps</span>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <div className="w-16 md:w-20 h-1.5 bg-[#e8e8e8] rounded-full overflow-hidden">
            <div className="h-full bg-black rounded-full transition-all duration-500" style={{ width: `${pct}%` }} />
          </div>
          <span className="text-[10px] text-[#999] font-medium w-6 text-right">{pct}%</span>
        </div>
      </button>

      {open && (
        <div className="border-t border-[#f0f0f0] divide-y divide-[#f5f5f5]">
          {STEPS.map((step) => {
            const isOpen = openStep === step.id;
            const isDone = done.has(step.id);
            const { Icon } = step;
            return (
              <div key={step.id}>
                <button
                  onClick={() => setOpenStep(isOpen ? null : step.id)}
                  className="w-full flex items-center gap-3 px-4 py-3 hover:bg-[#fafafa] transition-colors text-left"
                >
                  <div
                    role="checkbox" aria-checked={isDone} tabIndex={0}
                    onClick={(e) => toggleDone(step.id, e)}
                    onKeyDown={(e) => { if (e.key === " " || e.key === "Enter") toggleDone(step.id, e as any); }}
                    className={`flex-shrink-0 w-4 h-4 rounded border flex items-center justify-center transition-colors cursor-pointer ${
                      isDone ? "bg-black border-black" : "border-[#d0d0d0] hover:border-black"
                    }`}
                  >
                    {isDone && (
                      <svg width="8" height="6" viewBox="0 0 10 8" fill="none">
                        <path d="M1 4L3.5 6.5L9 1" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    )}
                  </div>
                  <Icon className={`w-3.5 h-3.5 flex-shrink-0 ${isDone ? "text-[#ccc]" : "text-black"}`} strokeWidth={1.5} />
                  <span className={`text-sm flex-1 ${isDone ? "text-[#bbb] line-through" : "text-black"}`}>{step.title}</span>
                  <span className="text-[10px] text-[#ccc] uppercase tracking-wider hidden sm:block">{step.section}</span>
                  <ChevronDown className={`w-3 h-3 text-[#ccc] transition-transform flex-shrink-0 ${isOpen ? "rotate-180" : ""}`} />
                </button>
                {isOpen && (
                  <div className="px-4 pb-4 ml-10 space-y-2">
                    <p className="text-xs text-[#666] leading-relaxed">{step.description}</p>
                    <div className="bg-[#fafafa] border border-[#eaeaea] rounded-md p-3 font-mono text-[11px] text-black overflow-x-auto">
                      <pre>{step.code}</pre>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export function Overview({ apiKey, onNavigate }: { apiKey: string; onNavigate?: (page: string) => void }) {
  const [health, setHealth] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchHealth() {
      try { const data = await apiCall("GET", "/health", apiKey); setHealth(data); }
      catch (e: any) { setError(e.message); }
    }
    fetchHealth();
  }, [apiKey]);

  return (
    <div className="max-w-4xl mx-auto px-4 md:px-8 py-6 md:py-8 space-y-5">

      {/* Header */}
      <div>
        <h1 className="text-xl font-semibold text-black">Overview</h1>
        <p className="text-sm text-[#999] mt-0.5">Smriti by Kaal the Absolute.</p>
      </div>

      {/* No API key */}
      {!apiKey && (
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 px-4 py-3 bg-[#fafafa] border border-[#e0e0e0] rounded-lg">
          <div className="flex items-center gap-2.5">
            <div className="w-1.5 h-1.5 rounded-full bg-[#f59e0b] flex-shrink-0" />
            <span className="text-sm text-black font-medium">No API key set</span>
            <span className="text-sm text-[#999] hidden sm:inline">— enter yours to connect Smriti</span>
          </div>
          <button
            onClick={() => onNavigate?.("keys")}
            className="text-xs font-medium text-black underline underline-offset-2 hover:opacity-60 transition-opacity self-start sm:self-auto"
          >
            Go to API Keys →
          </button>
        </div>
      )}

      {/* Stats — 2-col on mobile, 4-col on desktop */}
      {error ? (
        <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg border border-red-200 text-sm">⚠ {error}</div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="border border-[#eaeaea] rounded-lg p-4 bg-white hover:border-black transition-colors">
            <div className="text-2xl font-semibold text-black">
              {health ? (health.stores?.postgres_events || 0).toLocaleString() : <span className="text-[#ddd]">—</span>}
            </div>
            <div className="text-[10px] uppercase tracking-wider text-[#999] mt-1.5 font-medium">Events</div>
          </div>
          <div className="border border-[#eaeaea] rounded-lg p-4 bg-white hover:border-black transition-colors">
            <div className="text-2xl font-semibold text-black">
              {health ? (health.stores?.pgvector_embeddings || 0).toLocaleString() : <span className="text-[#ddd]">—</span>}
            </div>
            <div className="text-[10px] uppercase tracking-wider text-[#999] mt-1.5 font-medium">Embeddings</div>
          </div>
          <div className="border border-[#eaeaea] rounded-lg p-4 bg-white hover:border-black transition-colors">
            <div className="flex items-center gap-1.5">
              <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${health ? "bg-[#0a8f44]" : "bg-[#ddd] animate-pulse"}`} />
              <span className="text-sm font-medium text-black">{health ? "Online" : "…"}</span>
            </div>
            <div className="text-[10px] uppercase tracking-wider text-[#999] mt-1.5 font-medium">Status</div>
          </div>
          <div className="border border-[#eaeaea] rounded-lg p-4 bg-white hover:border-black transition-colors">
            <div className="text-sm font-medium text-black">120B</div>
            <div className="text-[10px] uppercase tracking-wider text-[#999] mt-1.5 font-medium">AI Engine</div>
          </div>
        </div>
      )}

      {/* Quick Start */}
      <QuickStart />

      {/* Quick Actions — 1-col on mobile, 3-col on desktop */}
      <div>
        <p className="text-[10px] uppercase tracking-wider text-[#bbb] font-medium mb-3">Jump to</p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {ACTIONS.map(({ id, Icon, label, sub }) => (
            <button
              key={id}
              onClick={() => onNavigate?.(id)}
              className="border border-[#eaeaea] rounded-lg p-4 bg-white hover:border-black hover:shadow-sm transition-all text-left group flex sm:block items-center gap-3"
            >
              <div className="flex items-start justify-between mb-0 sm:mb-3">
                <div className="w-8 h-8 rounded-md border border-[#eaeaea] flex items-center justify-center group-hover:border-black transition-colors flex-shrink-0">
                  <Icon className="w-3.5 h-3.5 text-black" strokeWidth={1.5} />
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-[#ccc] group-hover:text-black transition-colors mt-0.5 hidden sm:block" />
              </div>
              <div>
                <div className="text-sm font-medium text-black">{label}</div>
                <div className="text-xs text-[#999] mt-0.5 leading-relaxed">{sub}</div>
              </div>
            </button>
          ))}
        </div>
      </div>

    </div>
  );
}
