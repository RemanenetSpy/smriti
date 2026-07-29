import type { Metadata } from "next";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";
import Script from "next/script";
import "./globals.css";

export const metadata: Metadata = {
  title: "Smriti | Temporal Memory API for AI",
  description: "Give any AI agent structured, persistent, queryable memory in 3 API calls. Never start from zero again.",
  openGraph: {
    title: "Smriti | Temporal Memory API for AI",
    description: "Give any AI agent structured, persistent, queryable memory in 3 API calls.",
    url: "https://smriti-kaal.vercel.app",
    siteName: "Smriti",
    images: [
      {
        url: "/og.png",
        width: 1200,
        height: 630,
        alt: "Smriti — Temporal memory API for AI agents",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Smriti | Temporal Memory API for AI",
    description: "Give any AI agent structured, persistent, queryable memory in 3 API calls.",
    images: ["/og.png"],
  },
  verification: {
    google: "LcpqtTeE5e5DzzsqX8lIU8UCePd6v1-WaDjgDS6xIh0",
  },
};

const GA_ID = "G-7G3JG5WTW5";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${GeistSans.variable} ${GeistMono.variable}`}>
      <body className="font-sans antialiased text-black bg-white">
        {/* Google Analytics */}
        <Script
          src={`https://www.googletagmanager.com/gtag/js?id=${GA_ID}`}
          strategy="afterInteractive"
        />
        <Script id="google-analytics" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', '${GA_ID}');
          `}
        </Script>
        {children}
      </body>
    </html>
  );
}
