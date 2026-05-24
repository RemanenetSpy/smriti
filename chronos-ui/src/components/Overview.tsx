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
            <div className="text-sm font-medium text-black">
              DeepSeek V3.2 + Llama 3.1
            </div>
            <div className="text-[0.65rem] font-medium uppercase tracking-wider text-[#666666] mt-4">AI Engine</div>
          </div>
        </div>
      ) : (
        <div className="text-[#999999] mb-16 animate-pulse">Connecting to temporal core...</div>
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
