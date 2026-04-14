"use client";

import { useState } from "react";
import { apiCall } from "@/lib/api";

export function Keys() {
  const [tier, setTier] = useState("explorer");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const generateKey = async () => {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await apiCall("POST", `/billing/keys?tier=${tier}`, "");
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-12">
      <h2 className="font-inter text-xs uppercase tracking-[3px] text-[var(--chronos-text-dim)] mb-2">Authentication</h2>
      <h3 className="font-cormorant text-4xl font-bold text-[var(--chronos-ink)] mb-3">Generate API Key</h3>
      <p className="font-spectral text-lg text-[var(--chronos-text-dim)] italic mb-8">
        Create a new key to authenticate with Chronos OS. Store it safely — it's shown only once.
      </p>

      <div className="glass-panel p-6 mb-8 max-w-md">
        <label className="block text-sm font-semibold text-[var(--chronos-text)] mb-3">Select Tier</label>
        <select 
          value={tier} 
          onChange={e => setTier(e.target.value)} 
          className="chronos-input mb-6 bg-white"
        >
          <option value="explorer">Explorer (Free - 10k Events)</option>
          <option value="builder" disabled>⭐ Builder ($49 - 500k Events) — Coming Soon</option>
          <option value="scale" disabled>⭐ Scale ($249 - 5M Events) — Coming Soon</option>
        </select>

        <button 
          onClick={generateKey} 
          disabled={loading} 
          className={`wax-seal-button w-full ${loading ? 'opacity-70' : ''}`}
        >
          {loading ? "⚷ Generating..." : "⚷ Generate Key"}
        </button>
      </div>

      {error && <div className="bg-red-50 text-red-800 p-4 rounded border border-red-200 text-sm mb-6 max-w-md">⚠ {error}</div>}

      {result && (
        <div className="animate-fade-in">
          <div className="bg-green-50 text-green-800 p-4 rounded border border-green-200 text-sm mb-6 max-w-2xl font-bold">
            ✓ Key generated. Store it in a safe place — it cannot be retrieved again.
          </div>
          
          <div className="p-6 bg-white border-2 border-[var(--chronos-border)] border-dashed rounded-lg max-w-2xl text-center">
            <h4 className="font-inter text-xs uppercase tracking-[2px] text-[var(--chronos-text-dim)] mb-2">Your API Key</h4>
            <div className="font-mono text-xl bg-[var(--chronos-bg)] py-3 px-4 rounded text-[var(--chronos-wax-red)] select-all break-all shadow-inner">
              {result.api_key}
            </div>
            <div className="mt-4 flex justify-between items-center text-sm font-inter text-[var(--chronos-text-dim)] pt-4 border-t border-[var(--chronos-border)]">
              <span><strong>Source ID:</strong> {result.source_id}</span>
              <span className="uppercase tracking-wider font-bold">Tier: {result.tier}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
