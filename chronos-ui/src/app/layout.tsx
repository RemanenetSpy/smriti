import type { Metadata } from "next";
import { Inter, Spectral, Cormorant_Garamond } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter", display: "swap" });
const spectral = Spectral({ weight: ["400", "600"], style: ["normal", "italic"], subsets: ["latin"], variable: "--font-spectral", display: "swap" });
const cormorant = Cormorant_Garamond({ weight: ["400", "600"], subsets: ["latin"], variable: "--font-cormorant-garamond", display: "swap" });

export const metadata: Metadata = {
  title: "Chronos OS Workspace",
  description: "Temporal AI Agent Ecosystem",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${spectral.variable} ${cormorant.variable} font-inter antialiased`}>
        {children}
      </body>
    </html>
  );
}
