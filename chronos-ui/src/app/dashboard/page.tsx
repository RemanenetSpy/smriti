"use client";

import { useState, useEffect } from "react";
import { Sidebar } from "@/components/Sidebar";
import { Overview } from "@/components/Overview";
import { Ingest } from "@/components/Ingest";
import { Query } from "@/components/Query";
import { Agent } from "@/components/Agent";
import { Connect } from "@/components/Connect";
import { Billing } from "@/components/Billing";
import { Keys } from "@/components/Keys";

export default function App() {
  const [apiKey, setApiKey] = useState("");
  const [activePage, setActivePage] = useState("overview");

  // Load API key from local storage on mount
  useEffect(() => {
    const saved = localStorage.getItem("chronos_api_key");
    if (saved) setApiKey(saved);
  }, []);

  // Save API key on change
  useEffect(() => {
    if (apiKey) {
      localStorage.setItem("chronos_api_key", apiKey);
    } else {
      localStorage.removeItem("chronos_api_key");
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
