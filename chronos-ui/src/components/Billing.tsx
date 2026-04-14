"use client";

import { useState, useEffect } from "react";
import { apiCall } from "@/lib/api";

export function Billing({ apiKey }: { apiKey: string }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!apiKey) {
      setError("Please enter your API Key in the sidebar to view usage.");
      setLoading(false);
      return;
    }

    async function fetchUsage() {
      try {
        const usageData = await apiCall("GET", "/billing/usage", apiKey);
        setData(usageData);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchUsage();
  }, [apiKey]);

  return (
    <div className="max-w-4xl mx-auto p-12">
      <h2 className="font-inter text-xs uppercase tracking-[3px] text-[var(--chronos-text-dim)] mb-2">Account</h2>
      <h3 className="font-cormorant text-4xl font-bold text-[var(--chronos-ink)] mb-3">Usage & Billing</h3>

      {loading ? (
        <div className="text-[var(--chronos-text-dim)] animate-pulse mt-8">Fetching quota...</div>
      ) : error ? (
        <div className="mt-8 bg-red-50 text-red-800 p-4 rounded border border-red-200 text-sm">⚠ {error}</div>
      ) : data ? (
        <div className="animate-fade-in mt-8">
          <div className="flex justify-center mb-10">
            <span className="font-inter font-bold uppercase tracking-widest text-[#A93322] bg-[#F0ECD8] px-4 py-1 rounded-full border border-[var(--chronos-border)]">
              {data.tier || 'Explorer'} Tier
            </span>
          </div>

          <div className="grid grid-cols-3 gap-6 mb-12">
            <div className="glass-panel text-center p-6">
              <div className="font-inter text-xs text-[var(--chronos-text-dim)] uppercase tracking-wider mb-2">Events Used</div>
              <div className="font-cormorant text-3xl font-bold text-[var(--chronos-ink)]">
                {data.usage?.events?.used?.toLocaleString() || 0}
              </div>
              <div className="text-xs text-[var(--chronos-text-dim)] mt-2">
                {data.usage?.events?.remaining?.toLocaleString() || 0} remaining
              </div>
            </div>
            <div className="glass-panel text-center p-6">
              <div className="font-inter text-xs text-[var(--chronos-text-dim)] uppercase tracking-wider mb-2">Orchestration</div>
              <div className="font-cormorant text-3xl font-bold text-[var(--chronos-ink)]">
                {data.usage?.orchestration?.used?.toLocaleString() || 0}
              </div>
              <div className="text-xs text-[var(--chronos-text-dim)] mt-2">
                {data.usage?.orchestration?.remaining === -1 ? 'Unlimited' : (data.usage?.orchestration?.remaining?.toLocaleString() || 0) + ' remaining'}
              </div>
            </div>
            <div className="glass-panel text-center p-6">
              <div className="font-inter text-xs text-[var(--chronos-text-dim)] uppercase tracking-wider mb-2">Connected Tools</div>
              <div className="font-cormorant text-3xl font-bold text-[var(--chronos-ink)]">
                {data.usage?.connectors?.used || 0}
              </div>
              <div className="text-xs text-[var(--chronos-text-dim)] mt-2">
                of {data.usage?.connectors?.limit === -1 ? 'Unlimited' : data.usage?.connectors?.limit || 0} slots
              </div>
            </div>
          </div>

          <div className="border-t border-[var(--chronos-border)] pt-10">
            <h3 className="font-inter text-xs uppercase tracking-[3px] text-[var(--chronos-text-dim)] mb-4">Pricing</h3>
            <h4 className="font-cormorant text-2xl font-bold text-[var(--chronos-ink)] mb-6">Temporal Memory Tiers</h4>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse border border-[var(--chronos-border)] bg-white/50 backdrop-blur-sm shadow-sm rounded-lg overflow-hidden">
                <thead>
                  <tr className="bg-[var(--chronos-border)] text-[var(--chronos-ink)] font-semibold text-sm">
                    <th className="p-3">Feature</th>
                    <th className="p-3 bg-[#e8e4d3]">Explorer</th>
                    <th className="p-3 bg-[#e0dacc]">⭐ Builder <br/><span className="text-xs font-normal text-amber-700">Coming Soon</span></th>
                    <th className="p-3 bg-[#d5cebc]">⭐ Scale <br/><span className="text-xs font-normal text-amber-700">Coming Soon</span></th>
                  </tr>
                </thead>
                <tbody className="text-sm font-inter divide-y divide-[var(--chronos-border)] text-[var(--chronos-text)]">
                  <tr><td className="p-3 font-semibold">Price</td><td className="p-3">Free</td><td className="p-3">$49/month</td><td className="p-3">$249/month</td></tr>
                  <tr><td className="p-3 font-semibold">Events/mo</td><td className="p-3">10,000</td><td className="p-3">500,000</td><td className="p-3">5,000,000</td></tr>
                  <tr><td className="p-3 font-semibold">Orchestration</td><td className="p-3">100</td><td className="p-3">10,000</td><td className="p-3">Unlimited</td></tr>
                  <tr><td className="p-3 font-semibold">Connected Tools</td><td className="p-3">3</td><td className="p-3">25</td><td className="p-3">Unlimited</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
