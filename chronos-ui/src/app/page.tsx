import { Navbar } from "@/components/landing/Navbar";
import { Hero } from "@/components/landing/Hero";
import { LogoStrip } from "@/components/landing/LogoStrip";
import { ProblemCards } from "@/components/landing/ProblemCards";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { CodeBlock } from "@/components/landing/CodeBlock";
import { StatsRow } from "@/components/landing/StatsRow";
import { Pricing } from "@/components/landing/Pricing";
import { FinalCTA } from "@/components/landing/FinalCTA";
import { Footer } from "@/components/landing/Footer";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white selection:bg-black selection:text-white">
      <Navbar />
      <main>
        <Hero />
        <LogoStrip />
        <ProblemCards />
        <HowItWorks />
        <CodeBlock />
        <StatsRow />
        <Pricing />
        <FinalCTA />
      </main>
      <Footer />
    </div>
  );
}
