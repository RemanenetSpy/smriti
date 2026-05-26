"use client";

import { useState, useEffect } from "react";
import { apiCall } from "@/lib/api";
import { Key, Activity, Search, Cpu, Hexagon } from "lucide-react";

// ---------------------------------------------------------------------------
// Getting Started Steps — using same Lucide icons as the sidebar
// ---------------------------------------------------------------------------
const STEPS = [
  {
    id: "keys",
    Icon: Key,
    title: "Get your API Key",
    section: "API Keys",
    description:
      "Head to the API Keys section in the sidebar. Generate your first key and keep it safe — you will attach it to every request as the Authorization header.",
    code: `curl -H "Authorization: Bearer YOUR_KEY" \\
  https://chronos-api-backend.hf.space/health`,
  },
  {
    id: "ingest",
    Icon: Activity,
    title: "Ingest your first event",
    section: "Ingest Events",
    description:
      "The Ingest section lets you send raw text into Chronos. The AI automatically decomposes it into Subject-Verb-Object tuples and stores them with timestamps.",
    code: `POST /ingest
{
  "source_id": "my-app",
  "events": [{"text": "Acme Corp signed a $50k contract"}]
}`,
  },
  {
    id: "query",
    Icon: Search,
    title: "Query your memory",
    section: "Query Memory",
    description:
      "Use the Query section to ask natural-language questions. Chronos runs hybrid temporal + semantic search across all stored events and returns ranked results.",
    code: `POST /query
{ "query": "What happened with Acme Corp?" }`,
  },
  {
    id: "agent",
    Icon: Cpu,
    title: "Run an Agent",
    section: "Agent Chat",
    description:
      "The Agent section gives you a full LangGraph-powered agent that has your entire memory as context. Ask it complex questions, schedule tasks, or trigger tools — it reasons across time.",
    code: `POST /agent/run
{ "prompt": "Summarise all Q2 deals and flag any risks" }`,
  },
  {
    id: "connect",
    Icon: Hexagon,
    title: "Connect a tool",
    section: "Connect Tool",
    description:
      "Register your SaaS tools (Stripe, Notion, CRM) via the Connect section. Once connected, the Agent can call them mid-conversation and store the results as new events in memory.",
    code: `POST /connectors/register
{
  "name": "Stripe", "base_url": "https://api.stripe.com",
  "endpoints": [{"method":"GET","path":"/v1/charges"}]
}`,
  },
];

// ---------------------------------------------------------------------------
// Getting Started Panel
// ---------------------------------------------------------------------------
function GettingStarted({ onDismiss }: { onDismiss: () => void }) {
  const [openStep, setOpenStep] = useState<string | null>("keys");
  const [done, setDone] = useState<Set<string>>(new Set());

  const toggleDone = (id: string) => {
    setDone((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  return (
    <div className="border border-[#eaeaea] rounded-xl bg-white mb-12 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-5 border-b border-[#eaeaea]">
        <div className="flex items-center gap-3">
          <div className="w-1.5 h-1.5 rounded-full bg-black" />
          <span className="font-semibold text-black text-sm">Getting Started</span>
          <span className="text-[#999999] text-xs">
            {done.size} / {STEPS.length} completed
          </span>
        </div>
        <button
          onClick={onDismiss}
          className="text-[#999999] hover:text-black transition-colors text-xs"
        >
          Dismiss
        </button>
      </div>

      {/* Progress bar */}
      <div className="h-0.5 bg-[#f0f0f0]">
        <div
          className="h-full bg-black transition-all duration-500"
          style={{ width: `${(done.size / STEPS.length) * 100}%` }}
        />
      </div>

      {/* Steps */}
      <div className="divide-y divide-[#f5f5f5]">
        {STEPS.map((step) => {
          const isOpen = openStep === step.id;
          const isDone = done.has(step.id);
          const { Icon } = step;
          return (
            <div key={step.id}>
              <button
                onClick={() => setOpenStep(isOpen ? null : step.id)}
                className="w-full flex items-center gap-4 px-6 py-4 hover:bg-[#fafafa] transition-colors text-left"
              >
                {/* Checkbox */}
                <button
                  onClick={(e) => { e.stopPropagation(); toggleDone(step.id); }}
                  className={`flex-shrink-0 w-5 h-5 rounded border flex items-center justify-center transition-colors ${
                    isDone ? "bg-black border-black" : "border-[#d0d0d0] hover:border-black"
                  }`}
                >
                  {isDone && (
                    <svg width="10" height="8" viewBox="0 0 10 8" fill="none">
                      <path d="M1 4L3.5 6.5L9 1" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  )}
                </button>

                {/* Lucide icon matching the sidebar */}
                <Icon className={`w-4 h-4 flex-shrink-0 ${isDone ? "text-[#cccccc]" : "text-black"}`} strokeWidth={1.5} />

                <div className="flex-1">
                  <span className={`text-sm font-medium ${isDone ? "text-[#999999] line-through" : "text-black"}`}>
                    {step.title}
                  </span>
                  <span className="ml-2 text-[0.65rem] uppercase tracking-wider text-[#999999]">
                    → {step.section}
                  </span>
                </div>
                <span className="text-[#cccccc] text-[10px]">{isOpen ? "▲" : "▼"}</span>
              </button>

              {/* Expanded content */}
              {isOpen && (
                <div className="px-6 pb-5 ml-[60px] space-y-3">
                  <p className="text-sm text-[#666666] leading-relaxed">{step.description}</p>
                  <div className="bg-[#fafafa] border border-[#eaeaea] rounded-lg p-4 font-mono text-xs text-black overflow-x-auto">
                    <pre>{step.code}</pre>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Overview
// ---------------------------------------------------------------------------
export function Overview({ apiKey }: { apiKey: string }) {
  const [health, setHealth] = useState<any>(null);
  const [error, setError] = useState("");
  const [showGuide, setShowGuide] = useState(false);

  useEffect(() => {
    const dismissed = localStorage.getItem("chronos_guide_dismissed");
    if (!dismissed) setShowGuide(true);

    async function fetchHealth() {
      try {
        const data = await apiCall("GET", "/health", apiKey);
        setHealth(data);
      } catch (e: any) {
        setError(e.message);
      }
    }
    fetchHealth();
  }, [apiKey]);

  const dismissGuide = () => {
    localStorage.setItem("chronos_guide_dismissed", "1");
    setShowGuide(false);
  };

  return (
    <div className="max-w-5xl mx-auto p-12">
      <div className="mb-16">
        <h1 className="text-3xl font-semibold text-black mb-3">Overview</h1>
        <p className="text-[#666666]">System health and temporal storage statistics.</p>
      </div>

      {error ? (
        <div className="bg-red-50 text-red-800 p-4 rounded-md border border-red-200 mb-8 text-sm">
          ⚠ {error}
        </div>
      ) : health ? (
        <div className="grid grid-cols-4 gap-6 mb-16">
          <div className="glass-panel text-center">
            <div className="text-4xl font-semibold text-black">
              {(health.stores?.postgres_events || 0).toLocaleString()}
            </div>
            <div className="text-[0.65rem] font-medium uppercase tracking-wider text-[#666666] mt-3">Events Stored</div>
          </div>
          <div className="glass-panel text-center">
            <div className="text-4xl font-semibold text-black">
              {(health.stores?.pgvector_embeddings || 0).toLocaleString()}
            </div>
            <div className="text-[0.65rem] font-medium uppercase tracking-wider text-[#666666] mt-3">Embeddings</div>
          </div>
          <div className="glass-panel flex flex-col items-center justify-center">
            <div className="bg-[#fafafa] border border-[#eaeaea] text-black text-xs font-medium px-3 py-1 rounded-full flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-[#0a8f44]"></div>
              Operational
            </div>
            <div className="text-[0.65rem] font-medium uppercase tracking-wider text-[#666666] mt-4">System Status</div>
          </div>
          <div className="glass-panel flex flex-col items-center justify-center">
            <div className="text-sm font-medium text-black">GLM 4.7 + Llama 3.1</div>
            <div className="text-[0.65rem] font-medium uppercase tracking-wider text-[#666666] mt-4">AI Engine</div>
          </div>
        </div>
      ) : (
        <div className="text-[#999999] mb-16 animate-pulse">Connecting to temporal core...</div>
      )}

      {/* Getting Started Guide */}
      {showGuide && <GettingStarted onDismiss={dismissGuide} />}

      {!showGuide && (
        <div className="mb-12">
          <button
            onClick={() => setShowGuide(true)}
            className="text-xs text-[#999999] hover:text-black transition-colors underline underline-offset-2"
          >
            Show getting started guide
          </button>
        </div>
      )}

      <div className="border-t border-[#eaeaea] pt-8">
        <h2 className="text-xs font-medium uppercase tracking-wider text-[#666666] mb-6">Architecture</h2>
        <h3 className="text-xl font-semibold text-black mb-4">The Dual Calendar System</h3>
        <p className="text-[#666666] leading-relaxed mb-6 max-w-3xl">
          Chronos decomposes every piece of text into Subject-Verb-Object event tuples,
          stores them in a dual calendar (structured events + raw conversation turns),
          and indexes them for both semantic and temporal retrieval.
        </p>
        <div className="border border-[#eaeaea] bg-[#fafafa] rounded-lg p-6 font-mono text-sm text-black overflow-x-auto shadow-sm">
          <pre>
{`# Feed any text → AI extracts structured events
POST /ingest
{
  "source_id": "your-saas-app",
  "events": [{"text": "Acme Corp signed a $50k contract for Q2 2026"}]
}

# Ask any question → hybrid search finds answers
POST /query
{
  "query": "What happened with Acme Corp?"
}

# Response: [{subject: "Acme Corp", verb: "signed", object: "$50k contract", when: "Q2 2026"}]`}
          </pre>
        </div>
      </div>
    </div>
  );
}
