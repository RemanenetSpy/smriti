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
    if (!apiKey) { setError("Please enter your API Key in API Keys first."); return; }
    if (!query.trim()) return;
    setLoading(true); setError(""); setResult(null);
    const payload: any = { query, max_results: maxResults };
    if (startDate || endDate) {
      payload.time_range = {};
      if (startDate) payload.time_range.start = new Date(startDate).toISOString();
      if (endDate) payload.time_range.end = new Date(endDate).toISOString();
    }
    try {
      const data = await apiCall("POST", "/query", apiKey, payload);
      setResult(data);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 md:px-10 py-6 md:py-10">

      {/* Header */}
      <div className="mb-6 md:mb-10">
        <h2 className="text-2xl md:text-3xl font-semibold text-black">Query the Memory</h2>
        <p className="text-sm text-[#666] mt-1">Ask in natural language. Kaal searches across time and meaning.</p>
      </div>

      <div className="border border-[#eaeaea] rounded-xl p-4 md:p-6 bg-white mb-6">
        {/* Main query input */}
        <div className="mb-5">
          <input
            type="text" value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="What happened with contracts this quarter?"
            className="w-full border border-[#eaeaea] rounded-lg px-4 py-3 text-sm text-black bg-[#fafafa] focus:outline-none focus:border-black transition-colors"
            onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
          />
        </div>

        {/* Filters — stack on mobile, row on desktop */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-xs font-medium text-[#666] uppercase tracking-wider mb-1.5">From Date</label>
            <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)}
              className="w-full border border-[#eaeaea] rounded-lg px-3 py-2.5 text-sm text-black bg-[#fafafa] focus:outline-none focus:border-black transition-colors"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-[#666] uppercase tracking-wider mb-1.5">To Date</label>
            <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)}
              className="w-full border border-[#eaeaea] rounded-lg px-3 py-2.5 text-sm text-black bg-[#fafafa] focus:outline-none focus:border-black transition-colors"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-[#666] uppercase tracking-wider mb-1.5">Results: {maxResults}</label>
            <input type="range" min="1" max="50" value={maxResults}
              onChange={(e) => setMaxResults(parseInt(e.target.value))}
              className="w-full accent-black h-2 bg-[#eaeaea] rounded-lg appearance-none cursor-pointer mt-3"
            />
          </div>
        </div>

        <button
          onClick={handleQuery} disabled={loading}
          className={`w-full md:w-auto px-6 py-2.5 bg-black text-white text-sm font-medium rounded-lg transition-opacity ${
            loading ? "opacity-60 cursor-not-allowed" : "hover:opacity-80"
          }`}
        >
          {loading ? "Searching..." : "Search Temporal Memory"}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-800 p-4 rounded-lg border border-red-200 mb-5 text-sm">⚠ {error}</div>
      )}

      {result && !error && (
        <div>
          <div className="flex flex-col sm:flex-row sm:justify-between gap-1 text-xs font-medium uppercase tracking-wider text-[#666] mb-4 pb-3 border-b border-[#eaeaea]">
            <span>Search Results</span>
            <span>{result.total_found} events found · {result.query_time_ms.toFixed(0)}ms</span>
          </div>
          <div className="space-y-3">
            {result.results?.length === 0 ? (
              <div className="text-center text-[#999] py-10">No events found matching your query.</div>
            ) : (
              result.results?.map((item: any, idx: number) => {
                const event = item.event;
                const date = new Date(event.timestamp);
                const fmt = new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
                return (
                  <div key={idx} className="border border-[#eaeaea] rounded-lg p-4 bg-white hover:border-black transition-colors">
                    <div className="font-mono text-xs text-[#999] mb-2">{fmt.format(date)}</div>
                    <div className="text-sm text-black mb-2">
                      <strong>{event.subject}</strong>
                      <span className="text-[#666] mx-1.5">{event.verb}</span>
                      <span>{event.object}</span>
                    </div>
                    {event.raw_text && (
                      <div className="text-xs text-[#999] mb-2 break-words">{event.raw_text.slice(0, 120)}{event.raw_text.length > 120 ? '…' : ''}</div>
                    )}
                    <div className="text-[10px] uppercase tracking-wider text-[#aaa] font-mono">
                      Relevance: {(item.relevance_score * 100).toFixed(0)}% · {item.provenance?.replace('_', ' ')}
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
