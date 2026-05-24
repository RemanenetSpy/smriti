import type { Metadata } from "next";
import "@fontsource/geist-sans";
import "@fontsource/geist-mono";
import "./globals.css";

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
      <body className="font-sans antialiased text-black bg-white">
        {children}
      </body>
    </html>
  );
}
