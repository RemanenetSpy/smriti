export function StatsRow() {
  return (
    <section className="py-32 border-t border-b border-[#eaeaea] bg-white">
      <div className="max-w-6xl mx-auto px-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-y-16">
          
          <div className="flex flex-col items-center text-center md:border-r border-[#eaeaea]">
            <span className="text-5xl font-semibold text-black mb-4">2,100+</span>
            <span className="text-[#666666]">tokens/sec</span>
          </div>

          <div className="flex flex-col items-center text-center md:border-r border-[#eaeaea]">
            <span className="text-5xl font-semibold text-black mb-4">~80ms</span>
            <span className="text-[#666666]">query time</span>
          </div>

          <div className="flex flex-col items-center text-center md:border-r border-[#eaeaea]">
            <span className="text-5xl font-semibold text-black mb-4">3</span>
            <span className="text-[#666666]">API calls</span>
          </div>

          <div className="flex flex-col items-center text-center">
            <span className="text-5xl font-semibold text-black mb-4">Free</span>
            <span className="text-[#666666]">to start</span>
          </div>

        </div>
      </div>
    </section>
  );
}
