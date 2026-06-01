"use client";

import { useState } from "react";
import { apiCall } from "@/lib/api";
import { Lock } from "lucide-react";

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
      <div className="mb-12">
        <h2 className="text-3xl font-semibold text-black mb-2">Generate API Key</h2>
        <p className="text-[#666666]">
          Create a new key to authenticate with KAAL. Store it safely — it's shown only once.
        </p>
      </div>

      <div className="glass-panel mb-8 max-w-md">
        <label className="block text-sm font-medium text-black mb-4">Select Tier</label>
        
        <div className="space-y-3 mb-8">
          {/* Explorer - Active */}
          <div className="border-2 border-black bg-white rounded-lg p-4 cursor-pointer flex justify-between items-center shadow-sm transition-colors">
            <div>
              <div className="font-semibold text-black">Explorer</div>
              <div className="text-xs text-[#666666]">Free - 10k Events</div>
            </div>
            <div className="w-5 h-5 rounded-full border-[6px] border-black bg-white"></div>
          </div>
        </div>

        <button 
          onClick={generateKey} 
          disabled={loading} 
          className={`primary-button w-full ${loading ? 'opacity-70' : ''}`}
        >
          {loading ? "Generating..." : "Generate Key"}
        </button>
      </div>

      {error && <div className="bg-red-50 text-red-800 p-4 rounded-md border border-red-200 text-sm mb-6 max-w-md">⚠ {error}</div>}

      {result && (
        <div className="animate-fade-in">
          <div className="bg-[#fafafa] border border-[#eaeaea] text-black p-4 rounded-md text-sm mb-6 max-w-2xl">
            <span className="font-bold text-[#0a8f44] mr-2">✓</span> Key generated. Store it in a safe place — it cannot be retrieved again.
          </div>
          
          <div className="p-6 bg-white border border-[#eaeaea] rounded-lg max-w-2xl shadow-sm">
            <h4 className="text-xs font-medium uppercase tracking-wider text-[#666666] mb-3">Your API Key</h4>
            <div className="font-mono text-lg bg-[#fafafa] border border-[#eaeaea] py-4 px-4 rounded-md text-black select-all break-all">
              {result.api_key}
            </div>
            <div className="mt-4 flex justify-between items-center text-sm text-[#666666] pt-4 border-t border-[#eaeaea]">
              <span><strong>Source ID:</strong> {result.source_id}</span>
              <span className="uppercase tracking-wider font-medium text-black">Tier: {result.tier}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
