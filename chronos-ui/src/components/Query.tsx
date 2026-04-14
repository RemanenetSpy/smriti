"use client";

import { useState } from "react";
import { apiCall } from "@/lib/api";

export function Query({ apiKey }: { apiKey: string }) {
  const [query, setQuery] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [maxResults, setMaxResults] = useState(20);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const handleQuery = async () => {
    if (!apiKey) {
      setError("Please enter your API Key in the sidebar first.");
      return;
    }
    if (!query.trim()) return;

    setLoading(true);
    setError("");
    setResult(null);

    const payload: any = {
      query,
      max_results: maxResults,
    };

    if (startDate || endDate) {
      payload.time_range = {};
      if (startDate) payload.time_range.start = new Date(startDate).toISOString();
      if (endDate) payload.time_range.end = new Date(endDate).toISOString();
    }

    try {
      const data = await apiCall("POST", "/query", apiKey, payload);
      setResult(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-12">
      <h2 className="font-inter text-xs uppercase tracking-[3px] text-[var(--chronos-text-dim)] mb-2">Temporal Retrieval</h2>
      <h3 className="font-cormorant text-4xl font-bold text-[var(--chronos-ink)] mb-3">Query the Memory</h3>
      <p className="font-spectral text-lg text-[var(--chronos-text-dim)] italic mb-8">
        Ask in natural language. Chronos searches across time and meaning.
      </p>

      <div className="glass-panel mb-12 p-6">
        <div className="mb-6">
          <input 
            type="text" 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="What happened with contracts this quarter?"
            className="chronos-input w-full text-lg py-3 px-4 shadow-inner"
            onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div>
            <label className="block text-xs font-semibold text-[var(--chronos-text-dim)] uppercase tracking-wider mb-2">From Date</label>
            <input 
              type="date" 
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="chronos-input w-full"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-[var(--chronos-text-dim)] uppercase tracking-wider mb-2">To Date</label>
            <input 
              type="date" 
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="chronos-input w-full"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-[var(--chronos-text-dim)] uppercase tracking-wider mb-2">Results: {maxResults}</label>
            <input 
              type="range" 
              min="1" 
              max="50" 
              value={maxResults}
              onChange={(e) => setMaxResults(parseInt(e.target.value))}
              className="w-full accent-[var(--chronos-wax-red)] h-2 bg-[var(--chronos-border)] rounded-lg appearance-none cursor-pointer mt-2"
            />
          </div>
        </div>

        <button 
          onClick={handleQuery} 
          disabled={loading}
          className={`wax-seal-button ${loading ? "opacity-70 cursor-not-allowed" : ""}`}
        >
          {loading ? "⚲ Searching..." : "⚲ Search Temporal Memory"}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-800 p-4 rounded-md border border-red-200 mb-8 font-inter text-sm">
          ⚠ {error}
        </div>
      )}

      {result && !error && (
        <div className="animate-fade-in relative min-h-[400px]">
          <div className="font-inter text-[0.75rem] uppercase tracking-[2px] text-[var(--chronos-text-dim)] mb-8 pb-4 border-b border-[var(--chronos-border)] flex justify-between">
            <span>Search Results</span>
            <span>{result.total_found} events found · {result.query_time_ms.toFixed(0)}ms</span>
          </div>

          <div className="space-y-0">
            {result.results?.length === 0 ? (
              <div className="text-center text-[var(--chronos-text-dim)] py-12 italic font-spectral">
                No events found matching your temporal query.
              </div>
            ) : (
              result.results?.map((item: any, idx: number) => {
                const event = item.event;
                const date = new Date(event.timestamp);
                const formatter = new Intl.DateTimeFormat('en-US', { 
                  month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit'
                });
                
                return (
                  <div key={idx} className="timeline-event group hover:bg-white/40 p-4 rounded-md transition-colors -ml-4 pl-8">
                    <div className="font-mono text-xs text-[var(--chronos-wax-red)] mb-1 opacity-80 decoration-dotted underline-offset-4 decoration-[var(--chronos-border)]">
                      {formatter.format(date)}
                    </div>
                    <div className="font-spectral text-xl mb-1 mt-1">
                      <strong className="text-[var(--chronos-ink)]">{event.subject}</strong>
                      <span className="text-[var(--chronos-text-dim)] mx-1">{event.verb}</span>
                      <span className="text-[var(--chronos-ink)]">{event.object}</span>
                    </div>
                    <div className="text-[0.65rem] uppercase tracking-wider text-[var(--chronos-text-dim)] font-inter mt-3 bg-white/60 inline-block px-2 py-1 rounded border border-[var(--chronos-border)]">
                      Relevance: {(item.relevance_score * 100).toFixed(0)}% · via {item.provenance.replace('_', ' ')}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
}
