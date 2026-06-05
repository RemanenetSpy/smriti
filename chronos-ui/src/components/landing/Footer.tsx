import Link from "next/link";
import { Logo } from "../Logo";

export function Footer() {
  return (
    <footer className="py-12 border-t border-[#eaeaea] bg-white">
      <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
        
        <div className="flex items-center gap-8">
          <Link href="/">
            <Logo variant="compact" />
          </Link>
          
          <div className="flex items-center gap-6 text-sm text-[#666666]">
            <Link href="#how-it-works" className="hover:text-black transition-colors">How it works</Link>
            <Link href="#pricing" className="hover:text-black transition-colors">Pricing</Link>
            <Link href="/docs" className="hover:text-black transition-colors">Docs</Link>
            <Link href="https://github.com" className="hover:text-black transition-colors">GitHub</Link>
          </div>
        </div>

        <div className="text-sm text-[#999999]">
          © 2026 Smriti by Kaal the Absolute · v0.2.0
        </div>
        
      </div>
    </footer>
  );
}
