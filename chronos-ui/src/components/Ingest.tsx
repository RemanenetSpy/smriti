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
      <div className="mb-12">
        <h2 className="text-3xl font-semibold text-black mb-2">Memory Ingestion</h2>
        <p className="text-[#666666]">
          Enter events as natural language. The AI extracts the who, what, and when.
        </p>
      </div>

      <div className="glass-panel mb-8">
        <div className="mb-6">
          <label className="block text-sm font-medium text-black mb-2">Source ID</label>
          <input 
            type="text" 
            value={sourceId}
            onChange={(e) => setSourceId(e.target.value)}
            className="kaal-input w-full md:w-1/2"
          />
          <p className="text-xs text-[#666666] mt-2">Identifies where these events come from</p>
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium text-black mb-2">Events</label>
          <p className="text-xs text-[#666666] mb-3">One event per line — write in plain English:</p>
          <textarea 
            value={eventsText}
            onChange={(e) => setEventsText(e.target.value)}
            rows={5}
            className="kaal-input w-full resize-y min-h-[120px]"
          />
        </div>

        <div className="mb-8 flex items-center gap-3 text-sm text-black">
          <input 
            type="checkbox" 
            id="parseSvo"
            checked={parseSvo}
            onChange={(e) => setParseSvo(e.target.checked)}
            className="w-4 h-4 accent-black"
          />
          <label htmlFor="parseSvo" className="cursor-pointer select-none">Enable Fast SVO Parsing (Llama 3.1 via Groq)</label>
        </div>

        <button 
          onClick={handleIngest} 
          disabled={loading}
          className={`primary-button ${loading ? "opacity-70 cursor-not-allowed" : ""}`}
        >
          {loading ? "Processing..." : "Ingest Into Memory"}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-800 p-4 rounded-md border border-red-200 mb-8 text-sm">
          ⚠ {error}
        </div>
      )}

      {result && !error && (
        <div className="animate-fade-in">
          <div className="bg-[#fafafa] border border-[#eaeaea] p-4 rounded-md text-sm mb-8 flex items-center text-black">
            <span className="font-bold text-[#0a8f44] mr-2">✓</span> 
            Ingested <strong className="mx-1">{result.ingested_count} events</strong> into temporal memory
          </div>

          {result.svo_tuples?.length > 0 && (
            <div>
              <h4 className="text-xs font-medium uppercase tracking-wider text-[#666666] mb-4 pb-2 border-b border-[#eaeaea]">Extracted SVO Tuples</h4>
              <div className="space-y-4">
                {result.svo_tuples.map((svo: any, idx: number) => (
                  <div key={idx} className="timeline-event">
                    <div className="text-sm mb-1 font-mono text-black bg-[#fafafa] border border-[#eaeaea] p-3 rounded-md">
                      <strong className="text-black">{svo.subject || '?'}</strong>
                      <span className="text-[#999999] mx-2">→</span>
                      <em className="text-[#0a8f44] not-italic">{svo.verb || '?'}</em>
                      <span className="text-[#999999] mx-2">→</span>
                      <span className="text-black">{svo.object || '?'}</span>
                    </div>
                    <div className="text-xs text-[#999999] font-mono">
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
