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
        
        <div className="space-y-3 mb-6">
          {/* Explorer - Active */}
          <div className="border-2 border-[#A93322] bg-[#A93322]/5 rounded-lg p-4 cursor-pointer flex justify-between items-center shadow-sm">
            <div>
              <div className="font-semibold text-[#A93322]">Explorer</div>
              <div className="text-xs text-[var(--chronos-text-dim)]">Free - 10k Events</div>
            </div>
            <div className="w-5 h-5 rounded-full border-[5px] border-[#A93322] bg-white"></div>
          </div>

          {/* Builder - Disabled */}
          <div className="border border-[var(--chronos-border)] bg-[#fdfdfc] rounded-lg p-4 opacity-80 flex justify-between items-center">
            <div>
              <div className="font-semibold text-[var(--chronos-text-dim)] flex items-center gap-2">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="#cfab78" className="mb-[1px]">
                  <path d="M18 10h-1V7A5 5 0 0 0 7 7v3H6a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V12a2 2 0 0 0-2-2zm-6 9a2 2 0 1 1 0-4 2 2 0 0 1 0 4zm3-9H9V7a3 3 0 0 1 6 0v3z" />
                </svg>
                Builder
              </div>
              <div className="text-xs text-[var(--chronos-text-dim)] ml-5">$49/mo - 500k Events</div>
            </div>
            <div className="text-[10px] font-bold text-amber-800/80 uppercase tracking-wider bg-[#f8f1e3] px-2 py-1 rounded">Coming Soon</div>
          </div>

          {/* Scale - Disabled */}
          <div className="border border-[var(--chronos-border)] bg-[#fdfdfc] rounded-lg p-4 opacity-80 flex justify-between items-center">
            <div>
              <div className="font-semibold text-[var(--chronos-text-dim)] flex items-center gap-2">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="#c39d67" className="mb-[1px]">
                  <path d="M18 10h-1V7A5 5 0 0 0 7 7v3H6a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V12a2 2 0 0 0-2-2zm-6 9a2 2 0 1 1 0-4 2 2 0 0 1 0 4zm3-9H9V7a3 3 0 0 1 6 0v3z" />
                </svg>
                Scale
              </div>
              <div className="text-xs text-[var(--chronos-text-dim)] ml-5">$249/mo - 5M Events</div>
            </div>
            <div className="text-[10px] font-bold text-amber-800/80 uppercase tracking-wider bg-[#f8f1e3] px-2 py-1 rounded">Coming Soon</div>
          </div>
        </div>

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
