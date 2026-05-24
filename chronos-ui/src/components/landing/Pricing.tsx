import Link from "next/link";

export function Pricing() {
  return (
    <section id="pricing" className="py-32 bg-white">
      <div className="max-w-6xl mx-auto px-6">
        <div className="grid md:grid-cols-3 gap-8 items-start">
          
          {/* Explorer */}
          <div className="p-8 border border-[#eaeaea] rounded-xl bg-white hover:border-black transition-colors h-full flex flex-col">
            <h3 className="text-xl font-semibold text-black mb-2">Explorer</h3>
            <div className="text-4xl font-semibold text-black mb-8">Free</div>
            
            <ul className="space-y-4 mb-12 flex-1 text-[#666666]">
              <li className="flex items-center gap-3">
                <span className="text-black">→</span> 10,000 events/month
              </li>
              <li className="flex items-center gap-3">
                <span className="text-black">→</span> Standard query speed
              </li>
              <li className="flex items-center gap-3">
                <span className="text-black">→</span> Community support
              </li>
            </ul>

            <Link href="/dashboard" className="w-full block text-center py-3 rounded-full font-medium border border-[#eaeaea] text-black hover:border-black transition-colors">
              Get started
            </Link>
          </div>

          {/* Builder */}
          <div className="p-8 border-2 border-black rounded-xl bg-white shadow-sm relative h-full flex flex-col transform md:-translate-y-4">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-black text-white text-[11px] font-medium px-3 py-1 rounded-full tracking-wide">
              MOST POPULAR
            </div>
            
            <h3 className="text-xl font-semibold text-black mb-2">Builder</h3>
            <div className="text-4xl font-semibold text-black mb-8">$49<span className="text-lg text-[#666666] font-normal">/mo</span></div>
            
            <ul className="space-y-4 mb-12 flex-1 text-[#666666]">
              <li className="flex items-center gap-3">
                <span className="text-black">→</span> 100,000 events/month
              </li>
              <li className="flex items-center gap-3">
                <span className="text-black">→</span> Priority query speed (~80ms)
              </li>
              <li className="flex items-center gap-3">
                <span className="text-black">→</span> Priority support
              </li>
            </ul>

            <Link href="/dashboard" className="w-full block text-center py-3 rounded-full font-medium bg-black text-white hover:opacity-90 transition-opacity">
              Start building
            </Link>
          </div>

          {/* Scale */}
          <div className="p-8 border border-[#eaeaea] rounded-xl bg-white hover:border-black transition-colors h-full flex flex-col">
            <h3 className="text-xl font-semibold text-black mb-2">Scale</h3>
            <div className="text-4xl font-semibold text-black mb-8">$249<span className="text-lg text-[#666666] font-normal">/mo</span></div>
            
            <ul className="space-y-4 mb-12 flex-1 text-[#666666]">
              <li className="flex items-center gap-3">
                <span className="text-black">→</span> Unlimited events
              </li>
              <li className="flex items-center gap-3">
                <span className="text-black">→</span> Dedicated infrastructure
              </li>
              <li className="flex items-center gap-3">
                <span className="text-black">→</span> 24/7 Phone support
              </li>
            </ul>

            <Link href="mailto:sales@chronosos.com" className="w-full block text-center py-3 rounded-full font-medium border border-[#eaeaea] text-black hover:border-black transition-colors">
              Contact us
            </Link>
          </div>

        </div>
      </div>
    </section>
  );
}
