import Link from "next/link";
import { Hexagon } from "lucide-react";

export function Footer() {
  return (
    <footer className="py-12 border-t border-[#eaeaea] bg-white">
      <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
        
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2">
            <Hexagon className="w-4 h-4 fill-black text-black" strokeWidth={1.5} />
            <span className="font-medium text-black text-sm">Chronos OS</span>
          </Link>
          
          <div className="flex items-center gap-6 text-sm text-[#666666]">
            <Link href="#how-it-works" className="hover:text-black transition-colors">How it works</Link>
            <Link href="#pricing" className="hover:text-black transition-colors">Pricing</Link>
            <Link href="/docs" className="hover:text-black transition-colors">Docs</Link>
            <Link href="https://github.com" className="hover:text-black transition-colors">GitHub</Link>
          </div>
        </div>

        <div className="text-sm text-[#999999]">
          © 2026 Chronos OS · v0.2.0
        </div>
        
      </div>
    </footer>
  );
}
