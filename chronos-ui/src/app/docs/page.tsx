import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-white selection:bg-black selection:text-white flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-4xl mx-auto px-6 py-24 w-full">
        <h1 className="text-4xl font-bold text-black mb-4">Documentation</h1>
        <p className="text-[#666666] text-lg mb-12">
          Everything you need to integrate and build with KAAL.
        </p>

        <div className="space-y-12">
          {/* Authentication */}
          <section>
            <h2 className="text-2xl font-semibold text-black mb-4 pb-2 border-b border-[#eaeaea]">Authentication</h2>
            <p className="text-[#666666] mb-4">
              All API requests must be authenticated using a Bearer token in the <code className="bg-[#f5f5f5] text-black px-1.5 py-0.5 rounded text-sm font-mono">Authorization</code> header.
            </p>
            <div className="bg-[#fafafa] border border-[#eaeaea] p-4 rounded-md overflow-x-auto">
              <pre className="text-sm font-mono text-black">
                Authorization: Bearer chrn_...
              </pre>
            </div>
          </section>

          {/* Ingest Endpoint */}
          <section>
            <h2 className="text-2xl font-semibold text-black mb-4 pb-2 border-b border-[#eaeaea]">Ingest Event</h2>
            <p className="text-[#666666] mb-4">
              Feed unstructured text to your agent's memory. KAAL automatically extracts the relationships, entities, and temporal data.
            </p>
            <div className="mb-4">
              <span className="inline-block bg-[#f5f5f5] text-black border border-[#eaeaea] px-2 py-1 rounded font-mono text-sm font-medium mr-3">POST</span>
              <code className="text-black font-mono">/ingest</code>
            </div>
            
            <div className="bg-[#fafafa] border border-[#eaeaea] p-4 rounded-md overflow-x-auto">
              <pre className="text-sm font-mono text-black">
{`curl -X POST https://your-api.hf.space/ingest \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "source_id": "my-app",
    "events": [{"text": "Acme Corp signed a new $50k contract today"}]
  }'`}
              </pre>
            </div>
          </section>

          {/* Query Endpoint */}
          <section>
            <h2 className="text-2xl font-semibold text-black mb-4 pb-2 border-b border-[#eaeaea]">Query Memory</h2>
            <p className="text-[#666666] mb-4">
              Search your agent's memory using natural language. Returns fully structured JSON objects representing the events.
            </p>
            <div className="mb-4">
              <span className="inline-block bg-[#f5f5f5] text-black border border-[#eaeaea] px-2 py-1 rounded font-mono text-sm font-medium mr-3">POST</span>
              <code className="text-black font-mono">/query</code>
            </div>
            
            <div className="bg-[#fafafa] border border-[#eaeaea] p-4 rounded-md overflow-x-auto">
              <pre className="text-sm font-mono text-black">
{`curl -X POST https://your-api.hf.space/query \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "What did Acme Corp do?"}'`}
              </pre>
            </div>
          </section>
        </div>
      </main>
      <Footer />
    </div>
  );
}
