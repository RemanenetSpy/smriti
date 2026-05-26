import Link from "next/link";

export function Pricing() {
  return (
    <section id="pricing" className="py-32 bg-white">
      <div className="max-w-6xl mx-auto px-6">
        <div className="max-w-sm mx-auto">

          {/* Explorer — only visible tier for now */}
          <div className="p-8 border border-[#eaeaea] rounded-xl bg-white hover:border-black transition-colors flex flex-col">
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
              <li className="flex items-center gap-3">
                <span className="text-black">→</span> 3 connected tools
              </li>
              <li className="flex items-center gap-3">
                <span className="text-black">→</span> 1,000 orchestrations/month
              </li>
            </ul>

            <Link href="/dashboard" className="w-full block text-center py-3 rounded-full font-medium border border-[#eaeaea] text-black hover:border-black transition-colors">
              Get started free
            </Link>

            <p className="text-center text-xs text-[#999999] mt-4">No credit card required</p>
          </div>

          {/* Builder ($49/mo) and Scale ($299/mo) — hidden until payment is ready */}
          {/* TODO: Re-enable when Stripe integration is complete */}

        </div>
      </div>
    </section>
  );
}
