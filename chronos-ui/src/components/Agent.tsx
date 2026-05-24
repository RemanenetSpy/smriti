"use client";

import { useState } from "react";
import { apiCall } from "@/lib/api";
import { Send } from "lucide-react";

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
      <div className="shrink-0 mb-8 border-b border-[#eaeaea] pb-8">
        <h2 className="text-3xl font-semibold text-black mb-2">Converse with Memory</h2>
        <p className="text-[#666666]">
          An agent that remembers. Ask anything — it searches your temporal memory first.
        </p>
      </div>

      <div className="flex-1 overflow-y-auto mb-6 pr-4 space-y-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-[#999999]">
            <p className="text-base font-medium">Ready for your query.</p>
          </div>
        ) : (
          messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-lg p-5 ${
                m.role === 'user' 
                  ? 'bg-[#f5f5f5] text-black text-sm border border-[#eaeaea]' 
                  : 'bg-white border border-[#eaeaea] text-sm text-black shadow-sm leading-relaxed'
              }`}>
                {m.content}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-[#eaeaea] rounded-lg p-5 flex items-center space-x-2">
               <div className="w-1.5 h-1.5 rounded-full bg-black animate-bounce" style={{animationDelay: "0ms"}}></div>
               <div className="w-1.5 h-1.5 rounded-full bg-black animate-bounce" style={{animationDelay: "150ms"}}></div>
               <div className="w-1.5 h-1.5 rounded-full bg-black animate-bounce" style={{animationDelay: "300ms"}}></div>
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
          className="w-full bg-white border border-[#eaeaea] rounded-full py-4 pl-6 pr-16 focus:outline-none focus:border-black text-sm transition-colors text-black placeholder-[#999999]"
        />
        <button 
          onClick={sendMessage}
          disabled={loading || !apiKey || !input.trim()}
          className="absolute right-2 top-2 bottom-2 w-12 bg-black text-white rounded-full hover:opacity-80 transition-opacity flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
