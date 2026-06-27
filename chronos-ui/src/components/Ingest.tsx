"use client";

import { useState } from "react";
import { apiCall } from "@/lib/api";

export function Ingest({ apiKey }: { apiKey: string }) {
  const [sourceId, setSourceId] = useState("my-app");
  const [eventsText, setEventsText] = useState(
    "Acme Corp signed a $50,000 contract for Q2 2026\nJane was promoted to VP of Engineering on March 15\nThe team completed the product demo for TechStart on April 1"
  );
  const [parseSvo, setParseSvo] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const handleIngest = async () => {
    if (!apiKey) { setError("Please enter your API Key in API Keys first."); return; }
    if (!eventsText.trim()) return;
    setLoading(true); setError(""); setResult(null);
    const lines = eventsText.split("\n").map(l => l.trim()).filter(l => l);
    const payload = { source_id: sourceId, events: lines.map(text => ({ text })), parse_svo: parseSvo };
    try {
      const data = await apiCall("POST", "/ingest", apiKey, payload);
      setResult(data);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 md:px-10 py-6 md:py-10">

      {/* Header */}
      <div className="mb-6 md:mb-10">
        <h2 className="text-2xl md:text-3xl font-semibold text-black">Memory Ingestion</h2>
        <p className="text-sm text-[#666666] mt-1">Enter events as natural language. The AI extracts the who, what, and when.</p>
      </div>

      <div className="border border-[#eaeaea] rounded-xl p-4 md:p-6 bg-white mb-6">

        {/* Source ID */}
        <div className="mb-5">
          <label className="block text-sm font-medium text-black mb-1.5">Source ID</label>
          <input
            type="text" value={sourceId}
            onChange={(e) => setSourceId(e.target.value)}
            className="w-full md:w-1/2 border border-[#eaeaea] rounded-lg px-3 py-2.5 text-sm text-black focus:outline-none focus:border-black transition-colors bg-[#fafafa]"
          />
          <p className="text-xs text-[#999] mt-1.5">Identifies where these events come from</p>
        </div>

        {/* Events */}
        <div className="mb-5">
          <label className="block text-sm font-medium text-black mb-1">Events</label>
          <p className="text-xs text-[#999] mb-2">One event per line — write in plain English:</p>
          <textarea
            value={eventsText}
            onChange={(e) => setEventsText(e.target.value)}
            rows={5}
            className="w-full border border-[#eaeaea] rounded-lg px-3 py-2.5 text-sm text-black focus:outline-none focus:border-black transition-colors bg-[#fafafa] resize-y min-h-[100px]"
          />
        </div>

        {/* SVO toggle */}
        <div className="mb-6 flex items-center gap-3">
          <input
            type="checkbox" id="parseSvo" checked={parseSvo}
            onChange={(e) => setParseSvo(e.target.checked)}
            className="w-4 h-4 accent-black flex-shrink-0"
          />
          <label htmlFor="parseSvo" className="text-sm text-black cursor-pointer select-none leading-tight">
            Enable Fast SVO Parsing (Llama 3.1 via Groq)
          </label>
        </div>

        <button
          onClick={handleIngest} disabled={loading}
          className={`w-full md:w-auto px-6 py-2.5 bg-black text-white text-sm font-medium rounded-lg transition-opacity ${
            loading ? "opacity-60 cursor-not-allowed" : "hover:opacity-80"
          }`}
        >
          {loading ? "Processing..." : "Ingest Into Memory"}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-800 p-4 rounded-lg border border-red-200 mb-5 text-sm">⚠ {error}</div>
      )}

      {result && !error && (
        <div>
          <div className="bg-[#f0fdf4] border border-[#86efac] p-4 rounded-lg text-sm mb-5 flex items-center gap-2 text-[#166534]">
            <span className="font-bold">✓</span>
            Ingested <strong className="mx-1">{result.ingested_count} events</strong> into temporal memory
          </div>
          {result.svo_tuples?.length > 0 && (
            <div>
              <h4 className="text-xs font-medium uppercase tracking-wider text-[#666] mb-3 pb-2 border-b border-[#eaeaea]">Extracted SVO Tuples</h4>
              <div className="space-y-3">
                {result.svo_tuples.map((svo: any, idx: number) => (
                  <div key={idx} className="font-mono text-sm text-black bg-[#fafafa] border border-[#eaeaea] p-3 rounded-lg overflow-x-auto">
                    <strong>{svo.subject || '?'}</strong>
                    <span className="text-[#999] mx-2">→</span>
                    <em className="text-[#0a8f44] not-italic">{svo.verb || '?'}</em>
                    <span className="text-[#999] mx-2">→</span>
                    <span>{svo.object || '?'}</span>
                    <span className="text-xs text-[#999] ml-3">({(svo.confidence * 100).toFixed(0)}%)</span>
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
