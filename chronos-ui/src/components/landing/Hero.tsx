import Link from "next/link";

export function Hero() {
  return (
    <section className="pt-32 pb-32 px-6 flex flex-col items-center text-center max-w-6xl mx-auto">
      {/* Badge */}
      <div className="border border-black rounded-full px-3 py-1 text-[11px] font-medium mb-12">
        Free tier · No credit card
      </div>

      {/* Heading */}
      <h1 className="text-6xl md:text-7xl font-semibold tracking-tight text-black max-w-3xl leading-[1.1] mb-8">
        Your AI agents have <br className="hidden md:block" />
        no memory.
        <span className="block mt-4 text-[#666666]">We fix that.</span>
      </h1>

      {/* Subheading */}
      <p className="text-lg md:text-xl text-[#666666] max-w-2xl mb-12 leading-relaxed">
        Chronos OS gives any agent structured, persistent, queryable memory in 3 API calls. Never start from zero again.
      </p>

      {/* CTAs */}
      <div className="flex flex-col sm:flex-row items-center gap-4 mb-24">
        <Link 
          href="/dashboard"
          className="bg-black text-white px-8 py-3 rounded-full font-medium hover:opacity-90 transition-opacity"
        >
          Get Free API Key →
        </Link>
        <Link 
          href="/docs"
          className="bg-white text-black px-8 py-3 rounded-full font-medium border border-[#eaeaea] hover:border-black transition-colors"
        >
          Read the docs
        </Link>
      </div>

      {/* Demo Box */}
      <div className="w-full max-w-3xl border border-[#eaeaea] bg-[#fafafa] rounded-lg text-left overflow-hidden shadow-sm">
        <div className="border-b border-[#eaeaea] px-6 py-4 font-mono text-sm text-black">
          Input: "Acme Corp signed a $50K contract"
        </div>
        <div className="px-6 py-4 font-mono text-sm text-[#0a8f44] bg-white flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
          <span>WHO: Acme Corp</span>
          <span className="hidden sm:inline text-[#eaeaea]">|</span>
          <span>DID: signed</span>
          <span className="hidden sm:inline text-[#eaeaea]">|</span>
          <span>WHAT: $50K contract</span>
          <span className="hidden sm:inline text-[#eaeaea]">|</span>
          <span>WHEN: Q2 2026</span>
        </div>
      </div>
    </section>
  );
}
