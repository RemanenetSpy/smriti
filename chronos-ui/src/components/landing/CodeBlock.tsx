"use client";
import { useState } from "react";
import { Copy, Check } from "lucide-react";

export function CodeBlock() {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(`// Feed an event
httpx.post("/ingest", json={"text": "Acme signed a contract"})

// Query memory
httpx.post("/query", json={
  "query": "What happened with Acme?"
})`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="py-32 bg-white">
      <div className="max-w-4xl mx-auto px-6">
        <h2 className="text-center text-[#666666] mb-8 font-medium">How it looks in code</h2>
        
        <div className="border border-[#eaeaea] rounded-lg overflow-hidden bg-[#fafafa] shadow-sm">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-[#eaeaea] bg-white">
            <div className="flex gap-4 text-sm font-medium">
              <button className="text-black border-b-2 border-black pb-[14px] -mb-[15px]">Python</button>
              <button className="text-[#999999] hover:text-[#666666] transition-colors pb-[14px] -mb-[15px]">JavaScript</button>
              <button className="text-[#999999] hover:text-[#666666] transition-colors pb-[14px] -mb-[15px]">cURL</button>
            </div>
            <button 
              onClick={copyToClipboard}
              className="text-[#999999] hover:text-black transition-colors"
              aria-label="Copy code"
            >
              {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            </button>
          </div>
          
          {/* Code */}
          <div className="p-6 font-mono text-sm overflow-x-auto">
            <pre className="leading-loose">
              <span className="text-[#999999]"># Feed an event</span><br/>
              <span className="text-black font-semibold">httpx.post</span>(
              <span className="text-[#0a8f44]">"/ingest"</span>, json=
              <span className="text-black font-semibold">{"{"}</span>
              <span className="text-[#0a8f44]">"text"</span>: <span className="text-[#0a8f44]">"Acme signed a contract"</span>
              <span className="text-black font-semibold">{"}"}</span>)<br/><br/>
              
              <span className="text-[#999999]"># Query memory</span><br/>
              <span className="text-black font-semibold">httpx.post</span>(
              <span className="text-[#0a8f44]">"/query"</span>, json=
              <span className="text-black font-semibold">{"{"}</span><br/>
              &nbsp;&nbsp;<span className="text-[#0a8f44]">"query"</span>: <span className="text-[#0a8f44]">"What happened with Acme?"</span><br/>
              <span className="text-black font-semibold">{"}"}</span>)<br/><br/>
              
              <span className="text-[#999999]"># → {"{"} subject: "Acme", verb: "signed"... {"}"}</span>
            </pre>
          </div>
        </div>
      </div>
    </section>
  );
}
