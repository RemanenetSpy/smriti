import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-white selection:bg-black selection:text-white flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-4xl mx-auto px-6 py-24 w-full">
        <h1 className="text-4xl font-bold text-black mb-4">Documentation</h1>
        <p className="text-[#666666] text-lg mb-12">
          Everything you need to integrate and build with Chronos OS.
        </p>

        <div className="p-8 border border-[#eaeaea] rounded-lg bg-[#fafafa]">
          <h2 className="text-xl font-semibold text-black mb-2">Coming Soon</h2>
          <p className="text-[#666666]">
            Our full API reference and SDK documentation is currently being finalized.
            Check back soon for the complete guide!
          </p>
        </div>
      </main>
      <Footer />
    </div>
  );
}
