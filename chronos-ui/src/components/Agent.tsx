"use client";

import { useState, useRef, useEffect } from "react";
import { apiCall } from "@/lib/api";
import { Send } from "lucide-react";

export function Agent({ apiKey }: { apiKey: string }) {
  const [messages, setMessages] = useState<{role: string, content: string}[]>([]);
  const [input, setInput] = useState("");
  const [threadId, setThreadId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

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
    /* Full viewport height minus the mobile top-bar padding (pt-14 from page.tsx) */
    <div className="flex flex-col h-[calc(100vh-56px)] md:h-screen">

      {/* Header */}
      <div className="shrink-0 px-4 md:px-10 py-5 border-b border-[#eaeaea]">
        <h2 className="text-xl md:text-3xl font-semibold text-black">Converse with Memory</h2>
        <p className="text-sm text-[#666666] mt-0.5">
          An agent that remembers. Ask anything — it searches your temporal memory first.
        </p>
      </div>

      {/* Message list */}
      <div className="flex-1 overflow-y-auto px-4 md:px-10 py-4 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-[#999999]">
            <p className="text-base font-medium">Ready for your query.</p>
          </div>
        ) : (
          messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[88%] md:max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                m.role === 'user'
                  ? 'bg-black text-white'
                  : 'bg-white border border-[#eaeaea] text-black shadow-sm'
              }`}>
                {m.content}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-[#eaeaea] rounded-2xl px-4 py-3 flex items-center space-x-1.5">
              <div className="w-1.5 h-1.5 rounded-full bg-black animate-bounce" style={{animationDelay: "0ms"}} />
              <div className="w-1.5 h-1.5 rounded-full bg-black animate-bounce" style={{animationDelay: "150ms"}} />
              <div className="w-1.5 h-1.5 rounded-full bg-black animate-bounce" style={{animationDelay: "300ms"}} />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input bar — sticks to bottom */}
      <div className="shrink-0 px-3 md:px-8 py-3 border-t border-[#eaeaea] bg-white">
        {!apiKey && (
          <p className="text-xs text-[#f59e0b] mb-2 text-center">⚠ Set your API key in API Keys to start chatting.</p>
        )}
        <div className="relative">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
            placeholder={apiKey ? "Ask your temporally-aware agent..." : "Add API key first"}
            disabled={loading || !apiKey}
            className="w-full bg-[#f5f5f5] border border-[#eaeaea] rounded-full py-3.5 pl-5 pr-14 text-sm focus:outline-none focus:border-black transition-colors text-black placeholder-[#aaa] disabled:opacity-50"
          />
          <button
            onClick={sendMessage}
            disabled={loading || !apiKey || !input.trim()}
            className="absolute right-1.5 top-1/2 -translate-y-1/2 w-10 h-10 bg-black text-white rounded-full flex items-center justify-center disabled:opacity-40 disabled:cursor-not-allowed transition-opacity hover:opacity-80"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
