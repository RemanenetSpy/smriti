"use client";

import { Disc3, Search, Activity, Cpu, Hexagon, Banknote, Key } from "lucide-react";

interface SidebarProps {
  apiKey: string;
  setApiKey: (val: string) => void;
  activePage: string;
  setActivePage: (val: string) => void;
}

const PAGES = [
  { id: "overview", label: "⟡ Overview", icon: Disc3 },
  { id: "ingest", label: "⭳ Ingest Events", icon: Activity },
  { id: "query", label: "⚲ Query Memory", icon: Search },
  { id: "agent", label: "✦ Agent Chat", icon: Cpu },
  { id: "connect", label: "⚙ Connect Tool", icon: Hexagon },
  { id: "billing", label: "▤ Usage & Billing", icon: Banknote },
  { id: "keys", label: "⚷ API Keys", icon: Key },
];

export function Sidebar({ apiKey, setApiKey, activePage, setActivePage }: SidebarProps) {
  return (
    <div className="w-64 border-r border-[var(--chronos-border)] h-screen flex flex-col p-4 bg-[#F2F0E6]">
      {/* Logo Area */}
      <div className="flex flex-col items-center justify-center py-6 mb-4 border-b border-[var(--chronos-border)]">
        <svg width="48" height="48" viewBox="0 0 100 100" fill="none">
            <path d="M50 5 L95 25 L95 75 L50 95 L5 75 L5 25 Z" fill="#A93322" opacity="0.1"/>
            <path d="M50 15 L85 30 L85 70 L50 85 L15 70 L15 30 Z" fill="#A93322"/>
            <path d="M50 35 L65 42 L65 58 L50 65 L35 58 L35 42 Z" fill="#F7F5F0"/>
            <circle cx="50" cy="50" r="15" fill="none" stroke="#2C3048" strokeWidth="2" strokeDasharray="4 2"/>
            <circle cx="50" cy="50" r="2" fill="#2C3048"/>
        </svg>
        <div className="font-cormorant font-semibold text-xl text-[var(--chronos-ink)] mt-3">Chronos OS</div>
        <div className="font-inter text-[0.5rem] uppercase tracking-[4px] text-[var(--chronos-text-dim)] mt-1">Temporal AI Agent Ecosystem</div>
      </div>

      {/* API Key Input */}
      <div className="mb-6">
        <label className="text-xs font-inter text-[var(--chronos-text-dim)] mb-1 block uppercase tracking-wider">⚷ Auth Token</label>
        <input 
          type="password"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          placeholder="chrn_..."
          className="chronos-input w-full text-xs font-mono"
        />
      </div>

      {/* Navigation */}
      <div className="flex-1 space-y-1">
        {PAGES.map((page) => {
          const isActive = activePage === page.id;
          return (
            <button
              key={page.id}
              onClick={() => setActivePage(page.id)}
              className={`w-full flex items-center px-3 py-2 text-sm font-inter rounded-md transition-colors ${
                isActive 
                  ? "bg-[var(--chronos-border)] text-[var(--chronos-ink)] font-semibold" 
                  : "text-[var(--chronos-text-dim)] hover:bg-[var(--chronos-hover)] hover:text-[var(--chronos-text)]"
              }`}
            >
              {page.label}
            </button>
          )
        })}
      </div>

      {/* Footer */}
      <div className="pt-4 border-t border-[var(--chronos-border)] text-center">
        <span className="font-spectral text-xs italic text-[var(--chronos-text-dim)]">
          Letters to the Future, for agents.
        </span>
      </div>
    </div>
  );
}
