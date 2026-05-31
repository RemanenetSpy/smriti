import type { Metadata } from "next";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";
import "./globals.css";

export const metadata: Metadata = {
  title: "Kaal | Temporal Memory API for AI",
  description: "Give any AI agent structured, persistent, queryable memory in 3 API calls. Never start from zero again.",
  openGraph: {
    title: "Kaal | Temporal Memory API for AI",
    description: "Give any AI agent structured, persistent, queryable memory in 3 API calls.",
    url: "https://kaal.ai", // Replace with your actual domain when ready
    siteName: "Kaal",
    images: [
      {
        url: "/og.png",
        width: 1200,
        height: 630,
        alt: "Kaal — Temporal memory API for AI agents",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Kaal | Temporal Memory API for AI",
    description: "Give any AI agent structured, persistent, queryable memory in 3 API calls.",
    images: ["/og.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${GeistSans.variable} ${GeistMono.variable}`}>
      <body className="font-sans antialiased text-black bg-white">
        {children}
      </body>
    </html>
  );
}
