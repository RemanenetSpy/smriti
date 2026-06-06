"use client";

import { Disc3, Search, Activity, Cpu, Banknote, Key, Info, Hexagon } from "lucide-react";
import { Logo } from "./Logo";
import Link from "next/link";
import { useState } from "react";

interface SidebarProps {
  apiKey: string;
  setApiKey: (val: string) => void;
  activePage: string;
  setActivePage: (val: string) => void;
}

const PAGES = [
  {
    id: "overview",
    label: "Overview",
    icon: Disc3,
    tip: "System health, stats, and your getting started guide.",
  },
  {
    id: "ingest",
    label: "Ingest Events",
    icon: Activity,
    tip: "Send raw text into Smriti. The AI extracts Subject-Verb-Object tuples and stores them with timestamps.",
  },
  {
    id: "query",
    label: "Query Memory",
    icon: Search,
    tip: "Ask natural-language questions. Smriti runs hybrid temporal + semantic search across all your stored events.",
  },
  {
    id: "agent",
    label: "Agent Chat",
    icon: Cpu,
    tip: "A LangGraph agent with your full memory as context. Ask complex questions, trigger tools, and reason across time.",
  },
  {
    id: "connect",
    label: "Connect Tool",
    icon: Hexagon,
    tip: "Register SaaS tools (Stripe, Notion, CRM). Once connected, the Agent can call them mid-conversation.",
  },
  {
    id: "billing",
    label: "Usage & Billing",
    icon: Banknote,
    tip: "Track your monthly event and orchestration usage against your plan limits.",
  },
  {
    id: "keys",
    label: "API Keys",
    icon: Key,
    tip: "Generate and manage API keys. Pass them as the Authorization: Bearer header on every request.",
  },
];

export function Sidebar({ apiKey, setApiKey, activePage, setActivePage }: SidebarProps) {
  const [tooltip, setTooltip] = useState<string | null>(null);

  return (
    <div className="w-64 border-r border-[#eaeaea] h-screen flex flex-col bg-[#fafafa]">
      {/* Logo Area */}
      <div className="p-6 border-b border-[#eaeaea]">
        <Link href="/">
          <Logo variant="compact" />
        </Link>
      </div>

      <div className="p-4 flex flex-col h-full">

        {/* Navigation */}
        <div className="flex-1 space-y-0.5">
          {PAGES.map((page) => {
            const isActive = activePage === page.id;
            const Icon = page.icon;
            const showTip = tooltip === page.id;
            return (
              <div key={page.id} className="relative group">
                <button
                  onClick={() => setActivePage(page.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2 text-sm rounded-md transition-colors ${
                    isActive
                      ? "bg-[#eaeaea] text-black font-medium"
                      : "text-[#666666] hover:bg-white hover:text-black"
                  }`}
                >
                  <Icon className="w-4 h-4 flex-shrink-0" strokeWidth={1.5} />
                  <span className="flex-1 text-left">{page.label}</span>

                  {/* ⓘ Info button */}
                  <span
                    role="button"
                    tabIndex={0}
                    onClick={(e) => {
                      e.stopPropagation();
                      setTooltip(showTip ? null : page.id);
                    }}
                    onKeyDown={(e) => e.key === "Enter" && setTooltip(showTip ? null : page.id)}
                    className={`flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity rounded-sm p-0.5 ${
                      showTip ? "opacity-100 text-black" : "text-[#aaaaaa] hover:text-black"
                    }`}
                  >
                    <Info className="w-3 h-3" strokeWidth={1.5} />
                  </span>
                </button>

                {/* Tooltip */}
                {showTip && (
                  <div className="absolute left-full top-0 ml-2 z-50 w-56 bg-white border border-[#eaeaea] rounded-lg shadow-md p-3">
                    <p className="text-xs text-[#444444] leading-relaxed">{page.tip}</p>
                    {/* small arrow */}
                    <div className="absolute -left-1.5 top-3 w-2.5 h-2.5 bg-white border-l border-b border-[#eaeaea] rotate-45" />
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Close tooltip on outside click */}
        {tooltip && (
          <div
            className="fixed inset-0 z-40"
            onClick={() => setTooltip(null)}
          />
        )}

        {/* Footer */}
        <div className="pt-4 border-t border-[#eaeaea] text-left">
          <span className="text-xs text-[#999999]">v0.2.0 · Workspace</span>
        </div>
      </div>
    </div>
  );
}
