"use client";

import { useState } from "react";
import { apiCall } from "@/lib/api";
import { Eye, EyeOff, Check } from "lucide-react";

interface KeysProps {
  onKeySet?: (key: string) => void;
}

export function Keys({ onKeySet }: KeysProps) {
  // ── Enter existing key ────────────────────────────────────────────────────
  const [existingKey, setExistingKey] = useState("");
  const [showKey, setShowKey]         = useState(false);
  const [keySaved, setKeySaved]       = useState(false);

  const saveExistingKey = () => {
    const trimmed = existingKey.trim();
    if (!trimmed) return;
    localStorage.setItem("kaal_api_key", trimmed);
    onKeySet?.(trimmed);
    setKeySaved(true);
    setTimeout(() => setKeySaved(false), 2500);
  };

  // ── Generate new key ──────────────────────────────────────────────────────
  const [email, setEmail]     = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult]   = useState<any>(null);
  const [error, setError]     = useState("");
  const [copied, setCopied]   = useState(false);

  const generateKey = async () => {
    if (!email.trim().includes("@")) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await apiCall("POST", `/billing/keys?tier=explorer&email=${encodeURIComponent(email.trim())}`, "");
      setResult(data);
      localStorage.setItem("kaal_api_key", data.api_key);
      onKeySet?.(data.api_key);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const copyKey = (key: string) => {
    navigator.clipboard.writeText(key).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="max-w-2xl mx-auto px-8 py-8 space-y-8">

      {/* Page header */}
      <div>
        <h1 className="text-xl font-semibold text-black">API Keys</h1>
        <p className="text-sm text-[#999] mt-0.5">Manage your Smriti authentication keys.</p>
      </div>

      {/* ── Section 1: Enter existing key ──────────────────────────────────── */}
      <div className="border border-[#eaeaea] rounded-xl p-5 bg-white">
        <h2 className="text-sm font-semibold text-black mb-1">Use an existing key</h2>
        <p className="text-xs text-[#999] mb-4">
          Switching device? Paste your key here to authenticate this session.
        </p>

        <div className="flex gap-2">
          <div className="relative flex-1">
            <input
              type={showKey ? "text" : "password"}
              value={existingKey}
              onChange={(e) => setExistingKey(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && saveExistingKey()}
              placeholder="kaal_..."
              className="w-full kaal-input pr-9 font-mono text-sm"
            />
            <button
              onClick={() => setShowKey((v) => !v)}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[#aaa] hover:text-black transition-colors"
              tabIndex={-1}
            >
              {showKey ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
            </button>
          </div>

          <button
            onClick={saveExistingKey}
            disabled={!existingKey.trim()}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium transition-all border ${
              keySaved
                ? "bg-[#f0fdf4] border-[#86efac] text-[#166534]"
                : "bg-black text-white border-black hover:opacity-80 disabled:opacity-30 disabled:cursor-not-allowed"
            }`}
          >
            {keySaved ? (
              <><Check className="w-3.5 h-3.5" /> Saved</>
            ) : (
              "Use this key"
            )}
          </button>
        </div>
      </div>

      {/* Divider */}
      <div className="flex items-center gap-3">
        <div className="flex-1 h-px bg-[#f0f0f0]" />
        <span className="text-xs text-[#ccc] font-medium">or generate a new one</span>
        <div className="flex-1 h-px bg-[#f0f0f0]" />
      </div>

      {/* ── Section 2: Generate new key ────────────────────────────────────── */}
      <div className="border border-[#eaeaea] rounded-xl p-5 bg-white">
        <h2 className="text-sm font-semibold text-black mb-1">Generate a new key</h2>
        <p className="text-xs text-[#999] mb-4">
          Free tier · 10,000 events/month. Enter your email so we can associate the key with your account.
        </p>

        {/* Email input */}
        <div className="mb-3">
          <label className="text-xs text-[#666] font-medium mb-1.5 block">Email address</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && generateKey()}
            placeholder="you@company.com"
            className="kaal-input"
          />
        </div>

        {/* Tier */}
        <div className="flex items-center justify-between mb-4 p-3 border border-[#eaeaea] rounded-lg">
          <div>
            <div className="text-sm font-medium text-black">Explorer</div>
            <div className="text-xs text-[#999]">Free · 10k events/month</div>
          </div>
          <div className="w-4 h-4 rounded-full border-[5px] border-black bg-white" />
        </div>

        <button
          onClick={generateKey}
          disabled={loading || !email.trim().includes("@")}
          className="primary-button w-full disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {loading ? "Generating…" : "Generate Key"}
        </button>

        <p className="text-[10px] text-[#bbb] text-center mt-3">
          Rate limited · 1 key per email · IP protected
        </p>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg border border-red-200 text-sm">
          ⚠ {error}
        </div>
      )}

      {/* Generated key result */}
      {result && (
        <div className="border border-[#eaeaea] rounded-xl p-5 bg-white space-y-3">
          <div className="flex items-center gap-2 text-sm text-[#166534] font-medium">
            <Check className="w-4 h-4" /> Key generated · saved to this session
          </div>

          <div
            className="font-mono text-sm bg-[#fafafa] border border-[#eaeaea] rounded-lg px-4 py-3 text-black break-all select-all cursor-text"
            title="Click to select all"
          >
            {result.api_key}
          </div>

          <div className="flex items-center justify-between">
            <span className="text-xs text-[#999]">
              Source ID: <code className="text-black">{result.source_id}</code>
            </span>
            <button
              onClick={() => copyKey(result.api_key)}
              className={`text-xs font-medium px-3 py-1.5 rounded-md border transition-all ${
                copied
                  ? "border-[#86efac] text-[#166534] bg-[#f0fdf4]"
                  : "border-[#eaeaea] text-black hover:border-black"
              }`}
            >
              {copied ? "✓ Copied" : "Copy Key"}
            </button>
          </div>
        </div>
      )}

    </div>
  );
}
