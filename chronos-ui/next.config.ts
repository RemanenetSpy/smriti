import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    optimizePackageImports: ["lucide-react"],
  },

  async headers() {
    return [
      {
        // Apply to every route
        source: "/(.*)",
        headers: [
          // Prevent the app from being embedded in iframes on other origins
          // — this is what stops the chrome-error://chromewebdata/ frame warning
          { key: "X-Frame-Options",          value: "SAMEORIGIN" },
          // Prevent MIME-type sniffing
          { key: "X-Content-Type-Options",   value: "nosniff" },
          // Restrict referrer info sent to third parties
          { key: "Referrer-Policy",          value: "strict-origin-when-cross-origin" },
          // Disable unused browser features
          { key: "Permissions-Policy",       value: "camera=(), microphone=(), geolocation=()" },
          // CSP: allow self + the HF Space API + Vercel analytics
          // connect-src must include the backend domain so fetch() calls work
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline' 'unsafe-eval'",   // Next.js requires unsafe-eval in dev
              "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
              "font-src 'self' https://fonts.gstatic.com",
              "img-src 'self' data: blob:",
              "connect-src 'self' https://spy9191-chronos-api-backend.hf.space https://*.vercel.app",
              "frame-ancestors 'self'",                             // Only allow framing from same origin
            ].join("; "),
          },
        ],
      },
    ];
  },
};

export default nextConfig;
