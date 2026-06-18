import { Metadata } from "next";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

export const metadata: Metadata = {
  title: "How to Give Any AI Agent Long-Term Memory in 3 API Calls | Smriti",
  description:
    "Step-by-step guide to adding persistent, queryable temporal memory to any AI agent using Smriti's API. Works with OpenAI, LangChain, CrewAI, or any LLM stack.",
  openGraph: {
    title: "How to Give Any AI Agent Long-Term Memory in 3 API Calls",
    description:
      "Your AI agent forgets everything on restart. Here's the exact code to fix that — without a PhD in graph databases.",
    url: "https://smriti-kaal.vercel.app/blog/how-to-give-ai-agents-long-term-memory",
    type: "article",
    publishedTime: "2026-06-18T00:00:00Z",
    authors: ["Kaal the Absolute"],
  },
  twitter: {
    card: "summary_large_image",
    title: "How to Give Any AI Agent Long-Term Memory in 3 API Calls",
    description:
      "Step-by-step: add persistent memory to any LLM agent in minutes. No vector DB setup. No graph theory. Just 3 curl commands.",
  },
};

const CodeBlock = ({
  language,
  code,
}: {
  language: string;
  code: string;
}) => (
  <div className="my-6 rounded-xl overflow-hidden border border-[#e0e0e0] shadow-sm">
    <div className="bg-[#1e1e2e] flex items-center justify-between px-4 py-2">
      <span className="text-xs text-[#6c7086] font-mono uppercase tracking-wider">
        {language}
      </span>
      <div className="flex gap-1.5">
        <div className="w-3 h-3 rounded-full bg-[#ff5f57]" />
        <div className="w-3 h-3 rounded-full bg-[#febc2e]" />
        <div className="w-3 h-3 rounded-full bg-[#28c840]" />
      </div>
    </div>
    <div className="bg-[#181825] p-5 overflow-x-auto">
      <pre className="text-sm font-mono text-[#cdd6f4] leading-relaxed whitespace-pre">
        <code>{code}</code>
      </pre>
    </div>
  </div>
);

const callout = (
  icon: string,
  text: string,
  bg = "bg-[#f0f7ff]",
  border = "border-[#bfdbfe]"
) => (
  <div className={`${bg} border ${border} rounded-xl p-4 flex gap-3 my-6`}>
    <span className="text-xl shrink-0">{icon}</span>
    <p className="text-sm text-[#334155] leading-relaxed">{text}</p>
  </div>
);

export default function ArticlePage() {
  return (
    <div className="min-h-screen bg-white selection:bg-black selection:text-white flex flex-col">
      <Navbar />

      <main className="flex-1 w-full max-w-3xl mx-auto px-6 py-24 mt-12">
        {/* ── Header ── */}
        <header className="mb-14">
          <div className="flex items-center gap-2 mb-5">
            <span className="text-xs font-mono text-[#888] uppercase tracking-widest">
              Tutorial
            </span>
            <span className="text-[#ddd]">·</span>
            <span className="text-xs font-mono text-[#888]">June 18, 2026</span>
            <span className="text-[#ddd]">·</span>
            <span className="text-xs font-mono text-[#888]">6 min read</span>
          </div>

          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-black mb-6 leading-[1.12]">
            How to Give Any AI Agent Long-Term Memory in{" "}
            <span className="underline decoration-wavy decoration-black/20">
              3 API Calls
            </span>
          </h1>

          <p className="text-xl text-[#555] leading-relaxed mb-8">
            Your AI agent has a working memory of a goldfish. Here is the
            exact code to permanently fix that — no PhD in graph databases
            required.
          </p>

          <div className="flex items-center gap-3 pt-6 border-t border-[#f0f0f0]">
            <div className="w-9 h-9 rounded-full bg-black flex items-center justify-center text-white text-sm font-bold shrink-0">
              K
            </div>
            <div>
              <p className="text-sm font-semibold text-black leading-none mb-0.5">
                Kaal the Absolute
              </p>
              <p className="text-xs text-[#999]">Building Smriti</p>
            </div>
          </div>
        </header>

        {/* ── Body ── */}
        <div className="space-y-7 text-[#333] text-lg leading-[1.8]">

          <p>
            If you've ever built an AI chatbot or agent and hit the moment where
            a user says <em>"remember when I told you last week that my budget
            was $10k?"</em> — and your agent stares back blankly — this
            tutorial is for you.
          </p>

          <p>
            Most developers patch this with larger context windows or in-memory
            dictionaries. Both approaches collapse at scale. Context windows are
            expensive. In-memory dicts evaporate on restart. And neither gives
            you the ability to ask temporal questions like <em>"what changed
            about this project in the last 30 days?"</em>
          </p>

          <p>
            Today, I'll show you how to add real, persistent, queryable memory
            to any AI agent in under 10 minutes using{" "}
            <strong>Smriti</strong> — a temporal memory API built for exactly
            this.
          </p>

          {/* ── Prerequisites ── */}
          <h2 className="text-2xl font-bold text-black mt-12 mb-1 pt-6 border-t border-[#f0f0f0]">
            Prerequisites
          </h2>
          <ul className="list-disc pl-6 space-y-1.5 text-[#444]">
            <li>Any AI project (Python, JavaScript, or just curl)</li>
            <li>
              A free Smriti API key —{" "}
              <a href="/" className="underline text-black font-medium">
                get one here in 30 seconds
              </a>
            </li>
            <li>5 minutes</li>
          </ul>

          {/* ── Call 1 ── */}
          <h2 className="text-2xl font-bold text-black mt-12 mb-2 pt-6 border-t border-[#f0f0f0]">
            API Call 1 — Ingest: Feed your agent&apos;s memories
          </h2>
          <p>
            Any time something important happens — a user makes a decision, a
            contract is signed, a preference is stated — you fire one{" "}
            <code className="bg-[#f5f5f5] text-black px-1.5 py-0.5 rounded text-sm font-mono">
              POST /ingest
            </code>{" "}
            call. Smriti handles the rest: it extracts the entities, maps the
            relationships, and timestamps everything automatically.
          </p>

          <CodeBlock
            language="bash — curl"
            code={`curl -X POST https://spy9191-chronos-api-backend.hf.space/ingest \\
  -H "X-API-Key: YOUR_SMRITI_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "source_id": "my-agent",
    "events": [
      {"text": "User said their monthly budget is $10,000"},
      {"text": "User prefers async communication over meetings"},
      {"text": "Project deadline moved to August 15th"}
    ]
  }'`}
          />

          <p>
            That's it. Three facts are now permanently stored. Even if your
            server crashes, restarts, or your agent is replaced by a newer
            model tomorrow — those facts survive.
          </p>

          {/* ── Call 2 ── */}
          <h2 className="text-2xl font-bold text-black mt-12 mb-2 pt-6 border-t border-[#f0f0f0]">
            API Call 2 — Query: Retrieve the right memory at the right time
          </h2>
          <p>
            Before your agent responds to any user message, inject relevant
            memory from Smriti into the system prompt. The query is plain
            English — no SQL, no embeddings API, no configuration required.
          </p>

          <CodeBlock
            language="python — before calling your LLM"
            code={`import httpx

SMRITI = "https://spy9191-chronos-api-backend.hf.space"
KEY    = "YOUR_SMRITI_KEY"

def get_context(user_message: str) -> str:
    res = httpx.post(
        f"{SMRITI}/query",
        headers={"X-API-Key": KEY},
        json={"query": user_message, "max_results": 5},
    )
    results = res.json()["results"]
    if not results:
        return ""
    lines = [f"- {r['event']['object']}" for r in results]
    return "Relevant memory:\\n" + "\\n".join(lines)

# Use it in your system prompt
context = get_context("What is the user's budget?")
system_prompt = f"""You are a helpful assistant.

{context}

Answer based on the above memory when relevant."""`}
          />

          <div className="bg-[#f0fdf4] border border-[#86efac] rounded-xl p-4 flex gap-3 my-6">
            <span className="text-xl shrink-0">✅</span>
            <p className="text-sm text-[#14532d] leading-relaxed">
              <strong>Pro tip:</strong> Always inject the memory context before
              the conversation history in your prompt. Memory is ground truth;
              the conversation is context. Ground truth wins.
            </p>
          </div>

          {/* ── Call 3 ── */}
          <h2 className="text-2xl font-bold text-black mt-12 mb-2 pt-6 border-t border-[#f0f0f0]">
            API Call 3 — Agent Run: Let the AI reason with its memory
          </h2>
          <p>
            For power users, Smriti has a built-in{" "}
            <code className="bg-[#f5f5f5] text-black px-1.5 py-0.5 rounded text-sm font-mono">
              /agent/run
            </code>{" "}
            endpoint. Instead of managing the query-inject-prompt loop yourself,
            you send a message and Smriti's LangGraph-powered agent retrieves
            the relevant memory, injects it, calls the model, and returns a
            coherent response — all in one call.
          </p>

          <CodeBlock
            language="javascript — full agent with memory"
            code={`const res = await fetch(
  "https://spy9191-chronos-api-backend.hf.space/agent/run",
  {
    method: "POST",
    headers: {
      "X-API-Key": "YOUR_SMRITI_KEY",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      prompt: "What is the user's budget and when is their deadline?",
      thread_id: "user-session-42",
    }),
  }
);

const { response, events_retrieved } = await res.json();
console.log(response);
// → "Based on your memory: the user's budget is $10,000/month
//    and their project deadline is August 15th."
console.log(\`Retrieved \${events_retrieved} memory events.\`);`}
          />

          <p>
            Notice the <code className="bg-[#f5f5f5] text-black px-1.5 py-0.5 rounded text-sm font-mono">thread_id</code>.
            This lets Smriti maintain conversational continuity across sessions —
            every message in the thread builds on the last, and memory persists
            across all of them indefinitely.
          </p>

          {/* ── Why not vector DB ── */}
          <h2 className="text-2xl font-bold text-black mt-12 mb-2 pt-6 border-t border-[#f0f0f0]">
            &ldquo;Can&apos;t I just use Pinecone or Weaviate?&rdquo;
          </h2>
          <p>
            Yes — and for pure semantic similarity, they're excellent. But
            Smriti solves a fundamentally different problem:{" "}
            <strong>temporal reasoning</strong>.
          </p>

          <div className="overflow-x-auto my-6">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="bg-[#fafafa] border border-[#eaeaea]">
                  <th className="text-left p-3 font-semibold text-black border-b border-[#eaeaea]">Capability</th>
                  <th className="text-center p-3 font-semibold text-black border-b border-[#eaeaea]">Vector DB</th>
                  <th className="text-center p-3 font-semibold text-black border-b border-[#eaeaea]">Smriti</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["Semantic similarity search", "✅", "✅"],
                  ["\"What changed last month?\"", "❌", "✅"],
                  ["Automatic entity extraction (SVO)", "❌", "✅"],
                  ["Structured event timeline", "❌", "✅"],
                  ["Time-range filtering", "❌", "✅"],
                  ["3-call integration", "❌", "✅"],
                ].map(([feat, vdb, sm], i) => (
                  <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-[#fafafa]"}>
                    <td className="p-3 border border-[#eaeaea] text-[#333]">{feat}</td>
                    <td className="p-3 border border-[#eaeaea] text-center">{vdb}</td>
                    <td className="p-3 border border-[#eaeaea] text-center font-medium">{sm}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* ── Wrap up ── */}
          <h2 className="text-2xl font-bold text-black mt-12 mb-2 pt-6 border-t border-[#f0f0f0]">
            Your agent doesn&apos;t have to be a goldfish
          </h2>
          <p>
            The three calls above — ingest, query, run — are the complete loop.
            You can drop them into any existing LLM stack: OpenAI, LangChain,
            CrewAI, LlamaIndex, or a raw{" "}
            <code className="bg-[#f5f5f5] text-black px-1.5 py-0.5 rounded text-sm font-mono">
              fetch()
            </code>{" "}
            call. No infrastructure to manage. No vector database to provision.
            No embedding pipeline to maintain.
          </p>
          <p>
            Smriti handles the memory layer so you can focus on building the
            agent behavior that actually matters to your users.
          </p>

          {/* ── CTA ── */}
          <div className="mt-10 pt-8 border-t border-[#eaeaea] flex flex-col sm:flex-row gap-4 items-start sm:items-center">
            <a
              href="/"
              className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-semibold rounded-lg text-white bg-black hover:bg-[#111] transition-colors"
            >
              Get your free API key →
            </a>
            <a
              href="/docs"
              className="inline-flex items-center justify-center px-6 py-3 border border-[#e0e0e0] text-base font-medium rounded-lg text-black bg-white hover:bg-[#fafafa] transition-colors"
            >
              Full API docs
            </a>
          </div>

          <p className="text-sm text-[#aaa] mt-6">
            Explorer tier is free · 10,000 events/month · No credit card required.
          </p>
        </div>
      </main>

      <Footer />
    </div>
  );
}
