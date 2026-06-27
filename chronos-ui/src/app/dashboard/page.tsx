"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { Sidebar } from "@/components/Sidebar";
import { KaalChat } from "@/components/KaalChat";
import { WelcomeScreen } from "@/components/WelcomeScreen";

const Overview = dynamic(() => import("@/components/Overview").then(mod => mod.Overview));
const Ingest   = dynamic(() => import("@/components/Ingest").then(mod => mod.Ingest));
const Query    = dynamic(() => import("@/components/Query").then(mod => mod.Query));
const Agent    = dynamic(() => import("@/components/Agent").then(mod => mod.Agent));
const Connect  = dynamic(() => import("@/components/Connect").then(mod => mod.Connect));
const Billing  = dynamic(() => import("@/components/Billing").then(mod => mod.Billing));
const Keys     = dynamic(() => import("@/components/Keys").then(mod => mod.Keys));

export default function App() {
  const [apiKey, setApiKey]         = useState("");
  const [activePage, setActivePage] = useState("overview");
  const [showWelcome, setShowWelcome] = useState(false);

  useEffect(() => {
    const saved     = localStorage.getItem("kaal_api_key");
    const onboarded = localStorage.getItem("kaal_onboarded");
    const chatSeen  = localStorage.getItem("kaal_chat_seen");

    if (saved) setApiKey(saved);
    if (!onboarded) setShowWelcome(true);
  }, []);

  useEffect(() => {
    if (apiKey) localStorage.setItem("kaal_api_key", apiKey);
  }, [apiKey]);

  const handleOnboardingComplete = (
    key: string,
    _sourceId: string,
    _useCase: string | null
  ) => {
    setApiKey(key);
    localStorage.setItem("kaal_api_key", key);
    localStorage.setItem("kaal_onboarded", "true");
    setShowWelcome(false);
  };

  const renderPage = () => {
    switch (activePage) {
      case "overview": return <Overview apiKey={apiKey} onNavigate={setActivePage} />;
      case "ingest":   return <Ingest   apiKey={apiKey} />;
      case "query":    return <Query    apiKey={apiKey} />;
      case "agent":    return <Agent    apiKey={apiKey} />;
      case "connect":  return <Connect  apiKey={apiKey} />;
      case "billing":  return <Billing  apiKey={apiKey} />;
      case "keys":     return <Keys onKeySet={setApiKey} />;
      default:         return null;
    }
  };

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        apiKey={apiKey}
        setApiKey={setApiKey}
        activePage={activePage}
        setActivePage={setActivePage}
      />
      {/* pt-14 on mobile gives room for the hamburger button */}
      <main className="flex-1 overflow-y-auto bg-white pt-14 md:pt-0">
        {renderPage()}
      </main>

      {/* AI chat — always available as corner widget */}
      <KaalChat />

      {/* Onboarding overlay */}
      {showWelcome && <WelcomeScreen onComplete={handleOnboardingComplete} />}
    </div>
  );
}
