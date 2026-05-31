"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { Sidebar } from "@/components/Sidebar";

const Overview = dynamic(() => import("@/components/Overview").then(mod => mod.Overview));
const Ingest = dynamic(() => import("@/components/Ingest").then(mod => mod.Ingest));
const Query = dynamic(() => import("@/components/Query").then(mod => mod.Query));
const Agent = dynamic(() => import("@/components/Agent").then(mod => mod.Agent));
const Connect = dynamic(() => import("@/components/Connect").then(mod => mod.Connect));
const Billing = dynamic(() => import("@/components/Billing").then(mod => mod.Billing));
const Keys = dynamic(() => import("@/components/Keys").then(mod => mod.Keys));

export default function App() {
  const [apiKey, setApiKey] = useState("");
  const [activePage, setActivePage] = useState("overview");

  // Load API key from local storage on mount
  useEffect(() => {
    const saved = localStorage.getItem("kaal_api_key");
    if (saved) setApiKey(saved);
  }, []);

  // Save API key on change (but don't delete on initial render when it's empty)
  useEffect(() => {
    if (apiKey) {
      localStorage.setItem("kaal_api_key", apiKey);
    }
  }, [apiKey]);

  const renderPage = () => {
    switch (activePage) {
      case "overview": return <Overview apiKey={apiKey} />;
      case "ingest": return <Ingest apiKey={apiKey} />;
      case "query": return <Query apiKey={apiKey} />;
      case "agent": return <Agent apiKey={apiKey} />;
      case "connect": return <Connect apiKey={apiKey} />;
      case "billing": return <Billing apiKey={apiKey} />;
      case "keys": return <Keys />;
      default: return null;
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
      <main className="flex-1 overflow-y-auto bg-white">
        {renderPage()}
      </main>
    </div>
  );
}
