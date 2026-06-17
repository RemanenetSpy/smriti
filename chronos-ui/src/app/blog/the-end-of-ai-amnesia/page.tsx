import { Metadata } from "next";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

export const metadata: Metadata = {
  title: "The End of AI Amnesia: Introducing Smriti | Kaal the Absolute",
  description: "Every AI agent you build forgets everything the moment it stops running. Smriti by Kaal the Absolute provides persistent, structured, temporal memory for your AI models.",
  openGraph: {
    title: "The End of AI Amnesia: Introducing Smriti",
    description: "Every AI agent you build forgets everything the moment it stops running. We fixed it.",
    url: "https://smriti-kaal.vercel.app/blog/the-end-of-ai-amnesia",
    type: "article",
    publishedTime: new Date().toISOString(),
    authors: ["Kaal the Absolute"],
  },
  twitter: {
    card: "summary_large_image",
    title: "The End of AI Amnesia: Introducing Smriti",
    description: "Your AI agents are goldfish. We built Smriti to give them permanent, queryable memory in 3 simple API calls.",
  }
};

export default function ArticlePage() {
  return (
    <div className="min-h-screen bg-white selection:bg-black selection:text-white flex flex-col">
      <Navbar />
      
      <main className="flex-1 w-full max-w-3xl mx-auto px-6 py-24 mt-12">
        <article className="prose prose-lg prose-neutral max-w-none">
          {/* Article Header */}
          <header className="mb-12">
            <div className="text-sm text-[#666] font-mono mb-4 uppercase tracking-wider">
              Product Announcement • Kaal the Absolute
            </div>
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-black mb-6 leading-[1.15]">
              The End of AI Amnesia: Introducing Smriti
            </h1>
            <p className="text-xl text-[#666] leading-relaxed">
              Every AI agent you build forgets everything the moment it stops running. Today, we're fixing that permanently.
            </p>
          </header>

          {/* Body Content */}
          <div className="space-y-8 text-[#333] leading-relaxed text-lg">
            <p>
              The current landscape of Artificial Intelligence has a terminal flaw: <strong>Amnesia</strong>.
            </p>
            <p>
              You spend hours meticulously crafting the perfect prompt, giving your AI context, and having a productive, nuanced conversation. But the second you close the window or restart the server, the AI becomes a blank slate. It's like working with a genius colleague who suffers from severe short-term memory loss every time they blink.
            </p>

            <h2 className="text-2xl font-bold text-black mt-12 mb-4">The Context Window Trap</h2>
            <p>
              Until now, developers have tried to solve this by stuffing more and more tokens into the context window. "Just dump the entire history in the prompt," they say. But context windows are expensive, slow, and eventually, they run out of space. You aren't giving your AI memory; you're just reading its diary back to it every morning.
            </p>
            
            <p>
              Vector databases promised to fix this, but they fundamentally misunderstand how memory works. Humans don't store memories as floating mathematical embeddings in a void. We store memories as <strong>relationships, events, and timelines</strong>.
            </p>

            <h2 className="text-2xl font-bold text-black mt-12 mb-4">Enter Smriti by Kaal the Absolute</h2>
            <p>
              <strong>Smriti</strong> (Sanskrit for "that which is remembered") is a temporal memory engine designed specifically for AI agents. It doesn't just store what was said; it understands <em>who</em> said it, <em>when</em> it happened, and how it <em>relates</em> to everything else the AI knows.
            </p>

            <div className="bg-[#fafafa] border border-[#eaeaea] p-6 rounded-xl my-8">
              <h3 className="text-lg font-bold text-black mb-2">How it works in 3 steps:</h3>
              <ul className="list-decimal pl-5 space-y-2 text-[#444]">
                <li><strong>Ingest:</strong> You pass raw, unstructured text to our API.</li>
                <li><strong>Process:</strong> Smriti automatically extracts entities, maps relationships, and timestamps the events.</li>
                <li><strong>Recall:</strong> Your agent queries Smriti using natural language to retrieve exactly the context it needs, when it needs it.</li>
              </ul>
            </div>

            <h2 className="text-2xl font-bold text-black mt-12 mb-4">Built for Builders</h2>
            <p>
              We designed Smriti with a developer-first approach. You don't need to learn a new query language or manage a complex graph database infrastructure. With a single API key, you can give your application persistent memory in minutes.
            </p>
            
            <p>
              Whether you are building an AI companion that remembers users over years, a customer support agent that knows the history of every ticket, or a personal assistant that actually acts like one, Smriti is the missing infrastructure layer.
            </p>

            <h2 className="text-2xl font-bold text-black mt-12 mb-4">Ready to cure your AI's amnesia?</h2>
            <p>
              The era of the goldfish AI is over. It's time to build agents that learn, grow, and remember.
            </p>
            
            <div className="mt-8 pt-8 border-t border-[#eaeaea]">
              <a 
                href="/" 
                className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-black hover:bg-gray-800 transition-colors"
              >
                Get your free API Key today →
              </a>
            </div>
          </div>
        </article>
      </main>
      
      <Footer />
    </div>
  );
}
