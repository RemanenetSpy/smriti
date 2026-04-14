"use client";

import { useState } from "react";
import { apiCall } from "@/lib/api";

export function Ingest({ apiKey }: { apiKey: string }) {
  const [sourceId, setSourceId] = useState("my-app");
  const [eventsText, setEventsText] = useState("Acme Corp signed a $50,000 contract for Q2 2026\nJane was promoted to VP of Engineering on March 15\nThe team completed the product demo for TechStart on April 1");
  const [parseSvo, setParseSvo] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const handleIngest = async () => {
    if (!apiKey) {
      setError("Please enter your API Key in the sidebar first.");
      return;
    }
    if (!eventsText.trim()) return;

    setLoading(true);
    setError("");
    setResult(null);

    const lines = eventsText.split("\n").map(l => l.trim()).filter(l => l);
    const payload = {
      source_id: sourceId,
      events: lines.map(text => ({ text })),
      parse_svo: parseSvo,
    };

    try {
      const data = await apiCall("POST", "/ingest", apiKey, payload);
      setResult(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-12">
      <h2 className="font-inter text-xs uppercase tracking-[3px] text-[var(--chronos-text-dim)] mb-2">Memory Ingestion</h2>
      <h3 className="font-cormorant text-4xl font-bold text-[var(--chronos-ink)] mb-3">Feed the Temporal Memory</h3>
      <p className="font-spectral text-lg text-[var(--chronos-text-dim)] italic mb-8">
        Enter events as natural language. The AI extracts the who, what, and when.
      </p>

      <div className="glass-panel mb-8 p-6">
        <div className="mb-6">
          <label className="block text-sm font-semibold text-[var(--chronos-text)] mb-2">Source ID</label>
          <input 
            type="text" 
            value={sourceId}
            onChange={(e) => setSourceId(e.target.value)}
            className="chronos-input w-full md:w-1/2"
          />
          <p className="text-xs text-[var(--chronos-text-dim)] mt-1">Identifies where these events come from</p>
        </div>

        <div className="mb-6">
          <label className="block text-sm font-semibold text-[var(--chronos-text)] mb-2">Events</label>
          <p className="text-xs text-[var(--chronos-text-dim)] mb-2 italic">One event per line — write in plain English:</p>
          <textarea 
            value={eventsText}
            onChange={(e) => setEventsText(e.target.value)}
            rows={5}
            className="chronos-input w-full resize-y min-h-[120px]"
          />
        </div>

        <div className="mb-8 flex items-center gap-2 text-sm text-[var(--chronos-text)]">
          <input 
            type="checkbox" 
            id="parseSvo"
            checked={parseSvo}
            onChange={(e) => setParseSvo(e.target.checked)}
            className="w-4 h-4 accent-[var(--chronos-wax-red)]"
          />
          <label htmlFor="parseSvo">✧ Enable Fast SVO Parsing (Llama 3.1 via Cerebras)</label>
        </div>

        <button 
          onClick={handleIngest} 
          disabled={loading}
          className={`wax-seal-button ${loading ? "opacity-70 cursor-not-allowed" : ""}`}
        >
          {loading ? "⭳ Processing..." : "⭳ Ingest Into Memory"}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-800 p-4 rounded-md border border-red-200 mb-8 font-inter text-sm">
          ⚠ {error}
        </div>
      )}

      {result && !error && (
        <div className="animate-fade-in">
          <div className="bg-green-50 text-green-800 border border-green-200 p-4 rounded-md font-inter text-sm mb-8 flex items-center">
            <span className="font-bold mr-2">✓</span> 
            Ingested <strong>{result.ingested_count} events</strong> into temporal memory
          </div>

          {result.svo_tuples?.length > 0 && (
            <div>
              <h4 className="font-inter text-xs uppercase tracking-[3px] text-[var(--chronos-text-dim)] mb-4 pb-2 border-b border-[var(--chronos-border)]">Extracted SVO Tuples</h4>
              <div className="space-y-2">
                {result.svo_tuples.map((svo: any, idx: number) => (
                  <div key={idx} className="timeline-event bg-white/50 p-4 rounded-r shadow-sm">
                    <div className="font-spectral text-lg mb-2">
                      <strong className="text-[var(--chronos-ink)]">{svo.subject || '?'}</strong>
                      <span className="text-[var(--chronos-text-dim)] mx-2">→</span>
                      <em className="text-[var(--chronos-wax-red)]">{svo.verb || '?'}</em>
                      <span className="text-[var(--chronos-text-dim)] mx-2">→</span>
                      <span className="text-[var(--chronos-text)]">{svo.object || '?'}</span>
                    </div>
                    <div className="text-xs text-[var(--chronos-text-dim)] font-mono">
                      confidence: {(svo.confidence * 100).toFixed(0)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
