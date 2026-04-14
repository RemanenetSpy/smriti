"use client";

import { useState, useEffect } from "react";
import { apiCall } from "@/lib/api";

export function Overview({ apiKey }: { apiKey: string }) {
  const [health, setHealth] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
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

  return (
    <div className="max-w-5xl mx-auto p-12">
      <div className="text-center mb-16">
        <svg className="mx-auto mb-6" width="64" height="64" viewBox="0 0 100 100" fill="none">
            <path d="M50 5 L95 25 L95 75 L50 95 L5 75 L5 25 Z" fill="#A93322" />
            <path d="M50 15 L85 30 L85 70 L50 85 L15 70 L15 30 Z" fill="#F7F5F0"/>
            <path d="M50 35 L65 42 L65 58 L50 65 L35 58 L35 42 Z" fill="#A93322" opacity="0.8"/>
        </svg>
        <h1 className="font-cormorant text-5xl font-bold text-[var(--chronos-ink)] mb-3">Chronos OS</h1>
        <p className="font-spectral text-xl text-[var(--chronos-text-dim)] italic">Capturing the fragments of today for the clarity of tomorrow.</p>
        <p className="font-inter text-xs text-[var(--chronos-text-dim)] uppercase tracking-widest mt-4">Temporal AI Agent Ecosystem · v0.2.0</p>
      </div>

      {error ? (
        <div className="bg-red-50 text-red-800 p-4 rounded-md border border-red-200 mb-8 font-inter text-sm">
          ⚠ {error}
        </div>
      ) : health ? (
        <div className="grid grid-cols-4 gap-6 mb-16">
          <div className="glass-panel text-center">
            <div className="font-cormorant text-4xl font-bold text-[var(--chronos-ink)]">
              {(health.stores?.postgres_events || 0).toLocaleString()}
            </div>
            <div className="font-inter text-[0.65rem] uppercase tracking-wider text-[var(--chronos-text-dim)] mt-2">Events Stored</div>
          </div>
          <div className="glass-panel text-center">
            <div className="font-cormorant text-4xl font-bold text-[var(--chronos-ink)]">
              {(health.stores?.pgvector_embeddings || 0).toLocaleString()}
            </div>
            <div className="font-inter text-[0.65rem] uppercase tracking-wider text-[var(--chronos-text-dim)] mt-2">Embeddings</div>
          </div>
          <div className="glass-panel text-center flex flex-col items-center justify-center">
            <div className="bg-green-100 text-green-800 text-xs font-semibold px-3 py-1 rounded-full flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
              Operational
            </div>
            <div className="font-inter text-[0.65rem] uppercase tracking-wider text-[var(--chronos-text-dim)] mt-3">System Status</div>
          </div>
          <div className="glass-panel text-center flex flex-col items-center justify-center">
            <div className="font-inter text-sm font-semibold text-[var(--chronos-wax-red)]">
              Qwen 3 + Llama 3.1
            </div>
            <div className="font-inter text-[0.65rem] uppercase tracking-wider text-[var(--chronos-text-dim)] mt-3">AI Engine</div>
          </div>
        </div>
      ) : (
        <div className="text-center text-[var(--chronos-text-dim)] mb-16 animate-pulse">Connecting to temporal core...</div>
      )}

      <div className="border-t border-[var(--chronos-border)] pt-8">
        <h2 className="font-inter text-xs uppercase tracking-[3px] text-[var(--chronos-text-dim)] mb-6">Architecture</h2>
        <h3 className="font-cormorant text-2xl font-bold text-[var(--chronos-ink)] mb-4">The Dual Calendar System</h3>
        <p className="font-spectral text-lg text-[var(--chronos-text)] leading-relaxed mb-6">
          Chronos decomposes every piece of text into <strong>Subject-Verb-Object</strong> event tuples,
          stores them in a dual calendar (structured events + raw conversation turns),
          and indexes them for both <strong>semantic</strong> and <strong>temporal</strong> retrieval.
        </p>

        <div className="bg-[#2C3048] rounded-lg p-6 font-mono text-sm text-[var(--background)] overflow-x-auto shadow-inner">
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
