"use client";

import { Disc3, Search, Activity, Cpu, Hexagon, Banknote, Key } from "lucide-react";
import Link from "next/link";

interface SidebarProps {
  apiKey: string;
  setApiKey: (val: string) => void;
  activePage: string;
  setActivePage: (val: string) => void;
}

const PAGES = [
  { id: "overview", label: "Overview", icon: Disc3 },
  { id: "ingest", label: "Ingest Events", icon: Activity },
  { id: "query", label: "Query Memory", icon: Search },
  { id: "agent", label: "Agent Chat", icon: Cpu },
  { id: "connect", label: "Connect Tool", icon: Hexagon },
  { id: "billing", label: "Usage & Billing", icon: Banknote },
  { id: "keys", label: "API Keys", icon: Key },
];

export function Sidebar({ apiKey, setApiKey, activePage, setActivePage }: SidebarProps) {
  return (
    <div className="w-64 border-r border-[#eaeaea] h-screen flex flex-col bg-[#fafafa]">
      {/* Logo Area */}
      <div className="p-6 border-b border-[#eaeaea]">
        <Link href="/" className="flex items-center gap-2">
          <Hexagon className="w-5 h-5 fill-black text-black" strokeWidth={1.5} />
          <span className="font-medium text-black">Chronos OS</span>
        </Link>
      </div>

      <div className="p-4 flex flex-col h-full">
        {/* API Key Input */}
        <div className="mb-8">
          <label className="text-xs text-[#666666] mb-2 block uppercase tracking-wider font-medium">Auth Token</label>
          <input 
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="chrn_..."
            className="w-full bg-white border border-[#eaeaea] rounded-md px-3 py-2 text-sm font-mono focus:outline-none focus:border-black transition-colors"
          />
        </div>

        {/* Navigation */}
        <div className="flex-1 space-y-1">
          {PAGES.map((page) => {
            const isActive = activePage === page.id;
            const Icon = page.icon;
            return (
              <button
                key={page.id}
                onClick={() => setActivePage(page.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 text-sm rounded-md transition-colors ${
                  isActive 
                    ? "bg-[#eaeaea] text-black font-medium" 
                    : "text-[#666666] hover:bg-white hover:text-black"
                }`}
              >
                <Icon className="w-4 h-4" />
                {page.label}
              </button>
            )
          })}
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-[#eaeaea] text-left">
          <span className="text-xs text-[#999999]">
            v0.2.0 · Workspace
          </span>
        </div>
      </div>
    </div>
  );
}
