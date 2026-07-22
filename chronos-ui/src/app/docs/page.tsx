import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-white selection:bg-black selection:text-white flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-4xl mx-auto px-6 py-24 w-full">
        <h1 className="text-4xl font-bold text-black mb-4">Documentation</h1>
        <p className="text-[#666666] text-lg mb-12">
          Everything you need to integrate, connect MCP, and build with KAAL & Smriti.
        </p>

        <div className="space-y-16">
          {/* Quick Links Nav */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <a href="#auth" className="p-3 border border-[#eaeaea] rounded-lg bg-[#fafafa] hover:border-black text-xs font-medium text-black transition-colors">
              🔑 Authentication
            </a>
            <a href="#mcp" className="p-3 border border-[#eaeaea] rounded-lg bg-[#fafafa] hover:border-black text-xs font-medium text-black transition-colors">
              🔌 MCP Server (Claude/Cursor)
            </a>
            <a href="#ingest" className="p-3 border border-[#eaeaea] rounded-lg bg-[#fafafa] hover:border-black text-xs font-medium text-black transition-colors">
              ⚡ Ingest API
            </a>
            <a href="#query" className="p-3 border border-[#eaeaea] rounded-lg bg-[#fafafa] hover:border-black text-xs font-medium text-black transition-colors">
              🔍 Query API
            </a>
          </div>

          {/* Authentication */}
          <section id="auth" className="scroll-mt-24">
            <h2 className="text-2xl font-semibold text-black mb-4 pb-2 border-b border-[#eaeaea]">Authentication</h2>
            <p className="text-[#666666] mb-4">
              All API requests must be authenticated using a Bearer token or <code className="bg-[#f5f5f5] text-black px-1.5 py-0.5 rounded text-sm font-mono">X-API-Key</code> header.
            </p>
            <div className="bg-[#fafafa] border border-[#eaeaea] p-4 rounded-md overflow-x-auto">
              <pre className="text-sm font-mono text-black">
{`Authorization: Bearer chrn_...
# OR
X-API-Key: chrn_...`}
              </pre>
            </div>
          </section>

          {/* Model Context Protocol (MCP) Section */}
          <section id="mcp" className="scroll-mt-24">
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-2xl font-semibold text-black">Model Context Protocol (MCP) Server</h2>
              <span className="bg-black text-white text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full">New</span>
            </div>
            <p className="text-[#666666] mb-6 leading-relaxed">
              Connect Smriti directly to <strong>Claude Desktop</strong>, <strong>Cursor IDE</strong>, <strong>VS Code</strong>, or <strong>Windsurf</strong> using the official Model Context Protocol (MCP) server. Give your AI persistent temporal memory with zero glue code.
            </p>

            {/* MCP Setup Steps */}
            <div className="space-y-6 mb-8">
              <h3 className="text-lg font-medium text-black">1. Quick 3-Step Setup</h3>
              <div className="bg-[#fafafa] border border-[#eaeaea] p-4 rounded-md overflow-x-auto">
                <pre className="text-sm font-mono text-black">
{`# 1. Install dependencies
pip install -r mcp/requirements.txt

# 2. Set your API Key
export SMRITI_API_KEY="chrn_your_api_key_here"

# 3. Run stdio server (or test with MCP Inspector)
python -m smriti.mcp
# npx @modelcontextprotocol/inspector python -m smriti.mcp`}
                </pre>
              </div>

              <h3 className="text-lg font-medium text-black">2. Claude Desktop Integration</h3>
              <p className="text-sm text-[#666666] mb-2">
                Add this snippet to your <code className="bg-[#f5f5f5] text-black px-1.5 py-0.5 rounded text-xs font-mono">claude_desktop_config.json</code> file:
              </p>
              <div className="bg-[#fafafa] border border-[#eaeaea] p-4 rounded-md overflow-x-auto">
                <pre className="text-sm font-mono text-black">
{`{
  "mcpServers": {
    "smriti": {
      "command": "python",
      "args": ["-m", "smriti.mcp"],
      "cwd": "/path/to/smriti",
      "env": {
        "SMRITI_API_KEY": "chrn_your_api_key_here",
        "SMRITI_SOURCE_ID": "claude-desktop"
      }
    }
  }
}`}
                </pre>
              </div>

              <h3 className="text-lg font-medium text-black">3. Cursor IDE Integration</h3>
              <p className="text-sm text-[#666666] mb-2">
                Add to your project's <code className="bg-[#f5f5f5] text-black px-1.5 py-0.5 rounded text-xs font-mono">.cursor/mcp.json</code> or global Cursor settings:
              </p>
              <div className="bg-[#fafafa] border border-[#eaeaea] p-4 rounded-md overflow-x-auto">
                <pre className="text-sm font-mono text-black">
{`{
  "mcpServers": {
    "smriti": {
      "command": "python",
      "args": ["-m", "smriti.mcp"],
      "cwd": "/path/to/smriti",
      "env": {
        "SMRITI_API_KEY": "chrn_your_api_key_here",
        "SMRITI_SOURCE_ID": "cursor-workspace",
        "SMRITI_SCOPE": "code"
      }
    }
  }
}`}
                </pre>
              </div>
            </div>

            {/* MCP Tools Table */}
            <h3 className="text-lg font-medium text-black mb-3">Exposed MCP Tools</h3>
            <div className="border border-[#eaeaea] rounded-lg overflow-hidden mb-8">
              <table className="w-full text-left text-sm">
                <thead className="bg-[#fafafa] border-b border-[#eaeaea] text-black font-medium">
                  <tr>
                    <th className="p-3">Tool Name</th>
                    <th className="p-3">Description</th>
                    <th className="p-3">Parameters</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#eaeaea] text-[#444]">
                  <tr>
                    <td className="p-3 font-mono text-xs font-bold text-black">smriti_remember</td>
                    <td className="p-3">Stores text memory; auto-extracts Subject-Verb-Object causal tuples</td>
                    <td className="p-3 font-mono text-xs text-[#666]">text, source_id, scope, timestamp</td>
                  </tr>
                  <tr>
                    <td className="p-3 font-mono text-xs font-bold text-black">smriti_recall</td>
                    <td className="p-3">Hybrid search across semantic, temporal, and entity indexes</td>
                    <td className="p-3 font-mono text-xs text-[#666]">query, max_results, source_id, scope</td>
                  </tr>
                  <tr>
                    <td className="p-3 font-mono text-xs font-bold text-black">smriti_timeline</td>
                    <td className="p-3">Retrieves chronological event timeline for a specified time range</td>
                    <td className="p-3 font-mono text-xs text-[#666]">time_range_start, time_range_end, scope</td>
                  </tr>
                  <tr>
                    <td className="p-3 font-mono text-xs font-bold text-black">smriti_forget</td>
                    <td className="p-3">Finds memories to mark as superseded (preserving bi-temporal history)</td>
                    <td className="p-3 font-mono text-xs text-[#666]">query, scope, max_to_forget</td>
                  </tr>
                  <tr>
                    <td className="p-3 font-mono text-xs font-bold text-black">smriti_health</td>
                    <td className="p-3">Checks memory engine status, event count & embedding statistics</td>
                    <td className="p-3 font-mono text-xs text-[#666]">none</td>
                  </tr>
                  <tr>
                    <td className="p-3 font-mono text-xs font-bold text-black">smriti_usage</td>
                    <td className="p-3">Fetches current monthly usage statistics and plan tier limits</td>
                    <td className="p-3 font-mono text-xs text-[#666]">none</td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* MCP Environment Config Table */}
            <h3 className="text-lg font-medium text-black mb-3">MCP Environment Variables</h3>
            <div className="border border-[#eaeaea] rounded-lg overflow-hidden">
              <table className="w-full text-left text-sm">
                <thead className="bg-[#fafafa] border-b border-[#eaeaea] text-black font-medium">
                  <tr>
                    <th className="p-3">Variable</th>
                    <th className="p-3">Default</th>
                    <th className="p-3">Description</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#eaeaea] text-[#444]">
                  <tr>
                    <td className="p-3 font-mono text-xs font-semibold text-black">SMRITI_API_KEY</td>
                    <td className="p-3 text-xs text-red-600 font-mono">(required)</td>
                    <td className="p-3">Your Smriti API key (<code className="font-mono">chrn_...</code>)</td>
                  </tr>
                  <tr>
                    <td className="p-3 font-mono text-xs font-semibold text-black">SMRITI_BASE_URL</td>
                    <td className="p-3 font-mono text-xs text-[#666]">https://spy9191-chronos-api-backend.hf.space</td>
                    <td className="p-3">Base URL of your deployed Smriti API backend</td>
                  </tr>
                  <tr>
                    <td className="p-3 font-mono text-xs font-semibold text-black">SMRITI_SOURCE_ID</td>
                    <td className="p-3 font-mono text-xs text-[#666]">mcp-client</td>
                    <td className="p-3">Default source identifier for memory operations</td>
                  </tr>
                  <tr>
                    <td className="p-3 font-mono text-xs font-semibold text-black">SMRITI_SCOPE</td>
                    <td className="p-3 font-mono text-xs text-[#666]">default</td>
                    <td className="p-3">Logical namespace scope for memory partitioning</td>
                  </tr>
                  <tr>
                    <td className="p-3 font-mono text-xs font-semibold text-black">SMRITI_MAX_RESULTS</td>
                    <td className="p-3 font-mono text-xs text-[#666]">20</td>
                    <td className="p-3">Default max search results for recall & timeline</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          {/* Ingest Endpoint */}
          <section id="ingest" className="scroll-mt-24">
            <h2 className="text-2xl font-semibold text-black mb-4 pb-2 border-b border-[#eaeaea]">Ingest Event</h2>
            <p className="text-[#666666] mb-4">
              Feed unstructured text to your agent's memory. KAAL automatically extracts S-V-O relationships, entities, and temporal data.
            </p>
            <div className="mb-4">
              <span className="inline-block bg-[#f5f5f5] text-black border border-[#eaeaea] px-2 py-1 rounded font-mono text-sm font-medium mr-3">POST</span>
              <code className="text-black font-mono">/ingest</code>
            </div>
            
            <div className="bg-[#fafafa] border border-[#eaeaea] p-4 rounded-md overflow-x-auto">
              <pre className="text-sm font-mono text-black">
{`curl -X POST https://spy9191-chronos-api-backend.hf.space/ingest \\
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
          <section id="query" className="scroll-mt-24">
            <h2 className="text-2xl font-semibold text-black mb-4 pb-2 border-b border-[#eaeaea]">Query Memory</h2>
            <p className="text-[#666666] mb-4">
              Search your agent's memory using natural language. Performs hybrid semantic + temporal + entity retrieval.
            </p>
            <div className="mb-4">
              <span className="inline-block bg-[#f5f5f5] text-black border border-[#eaeaea] px-2 py-1 rounded font-mono text-sm font-medium mr-3">POST</span>
              <code className="text-black font-mono">/query</code>
            </div>
            
            <div className="bg-[#fafafa] border border-[#eaeaea] p-4 rounded-md overflow-x-auto">
              <pre className="text-sm font-mono text-black">
{`curl -X POST https://spy9191-chronos-api-backend.hf.space/query \\
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
