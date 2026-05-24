import Link from "next/link";

export function FinalCTA() {
  return (
    <section className="py-32 bg-white text-center">
      <div className="max-w-4xl mx-auto px-6">
        <h2 className="text-5xl md:text-6xl font-semibold tracking-tight text-black mb-6">
          Give your agents memory.
        </h2>
        <p className="text-xl text-[#666666] mb-12">
          Start free. Integrate in 5 minutes.
        </p>
        
        <Link 
          href="/dashboard"
          className="inline-block bg-black text-white px-8 py-3 rounded-full font-medium hover:opacity-90 transition-opacity mb-6"
        >
          Get Free API Key →
        </Link>
        
        <p className="text-sm text-[#999999]">
          Free tier · 10,000 events/month · No card required
        </p>
      </div>
    </section>
  );
}
