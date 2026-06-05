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
      <div className="mb-12">
        <h2 className="text-3xl font-semibold text-black mb-2">Query the Memory</h2>
        <p className="text-[#666666]">
          Ask in natural language. Kaal searches across time and meaning.
        </p>
      </div>

      <div className="glass-panel mb-12">
        <div className="mb-6">
          <input 
            type="text" 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="What happened with contracts this quarter?"
            className="w-full bg-[#fafafa] border border-[#eaeaea] rounded-md px-4 py-3 text-base text-black focus:outline-none focus:border-black transition-colors"
            onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div>
            <label className="block text-xs font-medium text-[#666666] uppercase tracking-wider mb-2">From Date</label>
            <input 
              type="date" 
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="kaal-input w-full"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-[#666666] uppercase tracking-wider mb-2">To Date</label>
            <input 
              type="date" 
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="kaal-input w-full"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-[#666666] uppercase tracking-wider mb-2">Results: {maxResults}</label>
            <input 
              type="range" 
              min="1" 
              max="50" 
              value={maxResults}
              onChange={(e) => setMaxResults(parseInt(e.target.value))}
              className="w-full accent-black h-2 bg-[#eaeaea] rounded-lg appearance-none cursor-pointer mt-2"
            />
          </div>
        </div>

        <button 
          onClick={handleQuery} 
          disabled={loading}
          className={`primary-button ${loading ? "opacity-70 cursor-not-allowed" : ""}`}
        >
          {loading ? "Searching..." : "Search Temporal Memory"}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-800 p-4 rounded-md border border-red-200 mb-8 text-sm">
          ⚠ {error}
        </div>
      )}

      {result && !error && (
        <div className="animate-fade-in relative min-h-[400px]">
          <div className="text-xs font-medium uppercase tracking-wider text-[#666666] mb-8 pb-4 border-b border-[#eaeaea] flex justify-between">
            <span>Search Results</span>
            <span>{result.total_found} events found · {result.query_time_ms.toFixed(0)}ms</span>
          </div>

          <div className="space-y-4">
            {result.results?.length === 0 ? (
              <div className="text-center text-[#999999] py-12">
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
                  <div key={idx} className="timeline-event group hover:bg-[#fafafa] p-4 rounded-md transition-colors -ml-4 pl-8 border border-transparent hover:border-[#eaeaea]">
                    <div className="font-mono text-xs text-[#666666] mb-2">
                      {formatter.format(date)}
                    </div>
                    <div className="text-lg mb-2">
                      <strong className="text-black">{event.subject}</strong>
                      <span className="text-[#666666] mx-1.5">{event.verb}</span>
                      <span className="text-black">{event.object}</span>
                    </div>
                    <div className="text-[10px] uppercase tracking-wider text-[#999999] font-mono mt-3 bg-white inline-block px-2 py-1 rounded border border-[#eaeaea]">
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
