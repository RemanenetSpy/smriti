import Link from "next/link";
import { Logo } from "../Logo";

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 w-full bg-white border-b border-[#eaeaea]">
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href="/">
          <Logo variant="compact" />
        </Link>

        {/* Links */}
        <nav className="hidden md:flex items-center gap-8 text-sm text-[#666666]">
          <Link href="#how-it-works" className="hover:text-black transition-colors">How it works</Link>
          <Link href="#pricing" className="hover:text-black transition-colors">Pricing</Link>
          <Link href="/docs" className="hover:text-black transition-colors">Docs</Link>
        </nav>

        {/* CTA */}
        <div className="flex items-center gap-4">
          <Link 
            href="/dashboard"
            className="text-sm font-medium bg-black text-white px-6 py-2 rounded-full hover:opacity-90 transition-opacity"
          >
            Get API Key →
          </Link>
        </div>
      </div>
    </header>
  );
}
