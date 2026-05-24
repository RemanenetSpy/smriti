"use client";

import { useState } from "react";
import { apiCall } from "@/lib/api";

export function Connect({ apiKey }: { apiKey: string }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [baseUrl, setBaseUrl] = useState("");
  const [authHeader, setAuthHeader] = useState("Authorization");
  const [endpointsJson, setEndpointsJson] = useState('[\n  {\n    "method": "GET",\n    "path": "/api/data",\n    "description": "Fetch data"\n  }\n]');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleConnect = async () => {
    if (!apiKey) {
      setError("Please enter your API Key in the sidebar first.");
      return;
    }
    setLoading(true);
    setError("");
    setMessage("");

    try {
      let parsedEndpoints = [];
      try {
        parsedEndpoints = JSON.parse(endpointsJson);
      } catch (err) {
        throw new Error("Invalid JSON format in the Endpoints field.");
      }

      const payload = {
        name,
        description,
        base_url: baseUrl,
        auth_header: authHeader,
        endpoints: parsedEndpoints
      };

      const result = await apiCall("POST", "/connect", apiKey, payload);
      setMessage(result.message || "Connected seamlessly.");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-12">
      <div className="mb-12">
        <h2 className="text-3xl font-semibold text-black mb-2">Connect a Tool</h2>
        <p className="text-[#666666]">
          Register any SaaS API — agents will discover and use it automatically.
        </p>
      </div>

      <div className="glass-panel p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm font-medium text-black mb-2">Tool Name</label>
            <input type="text" value={name} onChange={e => setName(e.target.value)} placeholder="Stripe, Notion, Slack..." className="chronos-input" />
          </div>
          <div>
            <label className="block text-sm font-medium text-black mb-2">Auth Header</label>
            <input type="text" value={authHeader} onChange={e => setAuthHeader(e.target.value)} placeholder="Authorization" className="chronos-input" />
          </div>
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium text-black mb-2">Base API URL</label>
          <input type="text" value={baseUrl} onChange={e => setBaseUrl(e.target.value)} placeholder="https://api.myproduct.com" className="chronos-input" />
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium text-black mb-2">Description</label>
          <textarea value={description} onChange={e => setDescription(e.target.value)} placeholder="What does this tool do?" rows={2} className="chronos-input resize-y"></textarea>
        </div>

        <div className="mb-8">
          <label className="block text-sm font-medium text-black mb-2">Endpoints <span className="font-normal text-[#999999] text-xs">(JSON format)</span></label>
          <textarea value={endpointsJson} onChange={e => setEndpointsJson(e.target.value)} rows={6} className="chronos-input font-mono text-xs text-[#666666]"></textarea>
        </div>

        <button onClick={handleConnect} disabled={loading} className={`primary-button ${loading ? 'opacity-70' : ''}`}>
          {loading ? "Processing..." : "Connect Tool"}
        </button>

        {error && <div className="mt-6 bg-red-50 text-red-800 p-4 rounded-md border border-red-200 text-sm">⚠ {error}</div>}
        {message && <div className="mt-6 bg-[#fafafa] text-black p-4 rounded-md border border-[#eaeaea] text-sm"><span className="font-bold text-[#0a8f44] mr-2">✓</span> {message}</div>}
      </div>
    </div>
  );
}
