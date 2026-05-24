export function LogoStrip() {
  return (
    <section className="py-16 border-t border-[#eaeaea]">
      <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row items-center justify-center gap-8 md:gap-16 opacity-50 grayscale transition-all hover:grayscale-0 hover:opacity-100 duration-500">
        <span className="text-xs uppercase tracking-widest text-[#666666] font-medium">Works with</span>
        <div className="flex items-center gap-8 md:gap-16 font-semibold text-lg">
          {/* Using text as placeholders for logos to maintain the minimal look */}
          <span>LangChain</span>
          <span>LangGraph</span>
          <span>FastAPI</span>
          <span>any framework</span>
        </div>
      </div>
    </section>
  );
}
