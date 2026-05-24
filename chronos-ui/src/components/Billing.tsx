"use client";

import { useState, useEffect } from "react";
import { apiCall } from "@/lib/api";
import { Lock } from "lucide-react";

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
      <div className="mb-12">
        <h2 className="text-3xl font-semibold text-black mb-2">Usage & Billing</h2>
        <p className="text-[#666666]">
          Monitor your temporal memory usage and account limits.
        </p>
      </div>

      {loading ? (
        <div className="text-[#999999] animate-pulse mt-8">Fetching quota...</div>
      ) : error ? (
        <div className="mt-8 bg-red-50 text-red-800 p-4 rounded-md border border-red-200 text-sm">⚠ {error}</div>
      ) : data ? (
        <div className="animate-fade-in mt-8">
          <div className="flex justify-start mb-10">
            <span className="text-xs font-medium uppercase tracking-wider text-black bg-[#fafafa] px-3 py-1.5 rounded border border-[#eaeaea]">
              {data.tier || 'Explorer'} Tier
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
            <div className="glass-panel text-left p-6">
              <div className="text-xs font-medium text-[#666666] uppercase tracking-wider mb-3">Events Used</div>
              <div className="text-4xl font-semibold text-black tracking-tight">
                {data.usage?.events?.used?.toLocaleString() || 0}
              </div>
              <div className="text-sm text-[#999999] mt-3">
                {data.usage?.events?.remaining?.toLocaleString() || 0} remaining
              </div>
            </div>
            <div className="glass-panel text-left p-6">
              <div className="text-xs font-medium text-[#666666] uppercase tracking-wider mb-3">Orchestration</div>
              <div className="text-4xl font-semibold text-black tracking-tight">
                {data.usage?.orchestration?.used?.toLocaleString() || 0}
              </div>
              <div className="text-sm text-[#999999] mt-3">
                {data.usage?.orchestration?.remaining === -1 ? 'Unlimited' : (data.usage?.orchestration?.remaining?.toLocaleString() || 0) + ' remaining'}
              </div>
            </div>
            <div className="glass-panel text-left p-6">
              <div className="text-xs font-medium text-[#666666] uppercase tracking-wider mb-3">Connected Tools</div>
              <div className="text-4xl font-semibold text-black tracking-tight">
                {data.usage?.connectors?.used || 0}
              </div>
              <div className="text-sm text-[#999999] mt-3">
                of {data.usage?.connectors?.limit === -1 ? 'Unlimited' : data.usage?.connectors?.limit || 0} slots
              </div>
            </div>
          </div>

          <div className="border-t border-[#eaeaea] pt-12">
            <h3 className="text-2xl font-semibold text-black mb-8">Temporal Memory Tiers</h3>
            
            <div className="overflow-hidden rounded-lg border border-[#eaeaea]">
              <table className="w-full text-left border-collapse bg-white">
                <thead>
                  <tr className="bg-[#fafafa] text-black text-sm border-b border-[#eaeaea]">
                    <th className="p-4 font-medium">Feature</th>
                    <th className="p-4 font-medium">Explorer</th>
                    <th className="p-4 font-medium border-l border-[#eaeaea]">
                      <div className="flex flex-col gap-1">
                        <div className="flex items-center gap-1.5 text-[#999999]">
                          <Lock className="w-3.5 h-3.5" />
                          BUILDER
                        </div>
                        <div className="text-[10px] font-medium text-[#999999] uppercase tracking-wider">Coming Soon</div>
                      </div>
                    </th>
                    <th className="p-4 font-medium border-l border-[#eaeaea]">
                      <div className="flex flex-col gap-1">
                        <div className="flex items-center gap-1.5 text-[#999999]">
                          <Lock className="w-3.5 h-3.5" />
                          SCALE
                        </div>
                        <div className="text-[10px] font-medium text-[#999999] uppercase tracking-wider">Coming Soon</div>
                      </div>
                    </th>
                  </tr>
                </thead>
                <tbody className="text-sm divide-y divide-[#eaeaea] text-black">
                  <tr className="hover:bg-[#fafafa] transition-colors"><td className="p-4 font-medium text-[#666666]">Price</td><td className="p-4">Free</td><td className="p-4 border-l border-[#eaeaea] text-[#999999]">$49/month</td><td className="p-4 border-l border-[#eaeaea] text-[#999999]">$249/month</td></tr>
                  <tr className="hover:bg-[#fafafa] transition-colors"><td className="p-4 font-medium text-[#666666]">Events/mo</td><td className="p-4">10,000</td><td className="p-4 border-l border-[#eaeaea] text-[#999999]">500,000</td><td className="p-4 border-l border-[#eaeaea] text-[#999999]">5,000,000</td></tr>
                  <tr className="hover:bg-[#fafafa] transition-colors"><td className="p-4 font-medium text-[#666666]">Orchestration</td><td className="p-4">100</td><td className="p-4 border-l border-[#eaeaea] text-[#999999]">10,000</td><td className="p-4 border-l border-[#eaeaea] text-[#999999]">Unlimited</td></tr>
                  <tr className="hover:bg-[#fafafa] transition-colors"><td className="p-4 font-medium text-[#666666]">Connected Tools</td><td className="p-4">3</td><td className="p-4 border-l border-[#eaeaea] text-[#999999]">25</td><td className="p-4 border-l border-[#eaeaea] text-[#999999]">Unlimited</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
