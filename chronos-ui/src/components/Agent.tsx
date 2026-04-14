"use client";

import { useState } from "react";
import { apiCall } from "@/lib/api";

export function Agent({ apiKey }: { apiKey: string }) {
  const [messages, setMessages] = useState<{role: string, content: string}[]>([]);
  const [input, setInput] = useState("");
  const [threadId, setThreadId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() || !apiKey) return;
    
    const userMsg = input;
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const payload = { prompt: userMsg, thread_id: threadId };
      const response = await apiCall("POST", "/agent/run", apiKey, payload);
      
      setMessages(prev => [...prev, { role: "assistant", content: response.response }]);
      setThreadId(response.thread_id);
    } catch (e: any) {
      setMessages(prev => [...prev, { role: "assistant", content: `⚠ Error: ${e.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-12 h-screen flex flex-col pt-12 pb-8">
      <div className="shrink-0 mb-6 border-b border-[var(--chronos-border)] pb-6">
        <h2 className="font-inter text-xs uppercase tracking-[3px] text-[var(--chronos-text-dim)] mb-2">Temporal Agent</h2>
        <h3 className="font-cormorant text-4xl font-bold text-[var(--chronos-ink)] mb-2">Converse with Memory</h3>
        <p className="font-spectral text-lg text-[var(--chronos-text-dim)] italic">
          An agent that remembers. Ask anything — it searches your temporal memory first.
        </p>
      </div>

      <div className="flex-1 overflow-y-auto mb-6 pr-4 space-y-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-[var(--chronos-text-dim)] opacity-50">
            <svg width="48" height="48" viewBox="0 0 100 100" fill="none" className="mb-4">
               <path d="M50 15 L85 30 L85 70 L50 85 L15 70 L15 30 Z" fill="currentColor"/>
               <circle cx="50" cy="50" r="15" fill="none" stroke="var(--background)" strokeWidth="4" strokeDasharray="6 4"/>
            </svg>
            <p className="font-spectral text-xl">The temporal span is recording.</p>
          </div>
        ) : (
          messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-lg p-5 ${
                m.role === 'user' 
                  ? 'bg-[var(--chronos-ink)] text-[var(--background)] font-inter text-sm shadow-md' 
                  : 'bg-white border border-[var(--chronos-border)] font-spectral text-lg text-[var(--chronos-text)] shadow-sm'
              }`}>
                {m.content}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-[var(--chronos-border)] rounded-lg p-5 flex items-center space-x-2">
               <div className="w-2 h-2 rounded-full bg-[var(--chronos-wax-red)] animate-bounce text-[var(--chronos-wax-red)]" style={{animationDelay: "0ms"}}></div>
               <div className="w-2 h-2 rounded-full bg-[var(--chronos-wax-red)] animate-bounce text-[var(--chronos-wax-red)]" style={{animationDelay: "150ms"}}></div>
               <div className="w-2 h-2 rounded-full bg-[var(--chronos-wax-red)] animate-bounce text-[var(--chronos-wax-red)]" style={{animationDelay: "300ms"}}></div>
            </div>
          </div>
        )}
      </div>

      <div className="shrink-0 relative">
        <input 
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          placeholder="Ask your temporally-aware agent..."
          disabled={loading || !apiKey}
          className="w-full bg-white border border-[var(--chronos-border)] rounded-full py-4 pl-6 pr-16 shadow-inner focus:outline-none focus:border-[var(--chronos-wax-red)] font-inter text-sm transition-colors"
        />
        <button 
          onClick={sendMessage}
          disabled={loading || !apiKey || !input.trim()}
          className="absolute right-2 top-2 bottom-2 w-12 bg-[#F0ECD8] rounded-full hover:bg-[var(--chronos-wax-red)] hover:text-white transition-colors flex items-center justify-center disabled:opacity-50"
        >
          ↵
        </button>
      </div>
    </div>
  );
}
