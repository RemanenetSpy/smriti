export function HowItWorks() {
  return (
    <section id="how-it-works" className="py-32 bg-white border-t border-b border-[#eaeaea]">
      <div className="max-w-6xl mx-auto px-6">
        <h2 className="text-4xl font-semibold tracking-tight text-black mb-24">
          Three calls. Permanent memory.
        </h2>

        <div className="relative">
          {/* Horizontal connecting line (hidden on mobile) */}
          <div className="hidden md:block absolute top-8 left-0 w-full h-[1px] bg-[#eaeaea] z-0"></div>

          <div className="grid md:grid-cols-3 gap-12 md:gap-8 relative z-10">
            
            {/* Step 1 */}
            <div className="relative bg-white pt-2">
              <div className="text-6xl font-bold text-[#f5f5f5] absolute -top-8 -left-4 z-0 pointer-events-none select-none">
                01
              </div>
              <div className="relative z-10">
                <h3 className="text-xl font-semibold text-black mb-4">Feed any text</h3>
                <div className="font-mono text-sm mb-4">
                  <span className="text-[#666666]">POST</span> <span className="text-black font-semibold">/ingest</span> any text →
                </div>
                <p className="text-[#666666] leading-relaxed">
                  Send raw data from CRMs, chats, emails, or git commits. Smriti accepts completely unstructured text.
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="relative bg-white pt-2">
              <div className="text-6xl font-bold text-[#f5f5f5] absolute -top-8 -left-4 z-0 pointer-events-none select-none">
                02
              </div>
              <div className="relative z-10">
                <h3 className="text-xl font-semibold text-black mb-4">AI extracts structure</h3>
                <div className="font-mono text-sm mb-4">
                  <span className="text-[#666666]">WHO + DID + WHAT + WHEN →</span>
                </div>
                <p className="text-[#666666] leading-relaxed">
                  Our pipeline automatically extracts Subject-Verb-Object (SVO) events and stores them in PostgreSQL with dual pgvector indexing.
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="relative bg-white pt-2">
              <div className="text-6xl font-bold text-[#f5f5f5] absolute -top-8 -left-4 z-0 pointer-events-none select-none">
                03
              </div>
              <div className="relative z-10">
                <h3 className="text-xl font-semibold text-black mb-4">Query anything</h3>
                <div className="font-mono text-sm mb-4">
                  <span className="text-[#666666]">GET</span> <span className="text-black font-semibold">structured results</span>
                </div>
                <p className="text-[#666666] leading-relaxed">
                  Search naturally. Smriti returns exact, structured JSON events in ~80ms, enabling your agents to reason temporally.
                </p>
              </div>
            </div>

          </div>
        </div>
      </div>
    </section>
  );
}
