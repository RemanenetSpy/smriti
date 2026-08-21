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
          // ─── Content Security Policy ─────────────────────────────────────────
          // Cloudflare Turnstile requires:
          //   • script-src-elem  → to load the challenges.cloudflare.com JS
          //   • frame-src        → Turnstile renders inside an iframe
          //   • worker-src / child-src → Turnstile's internal web workers
          //   • connect-src      → token verification XHR
          // Without script-src-elem, browsers that support it will IGNORE
          // script-src for inline/external scripts and block Turnstile silently.
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",

              // script-src: broad fallback for browsers that don't support script-src-elem
              "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://challenges.cloudflare.com https://www.googletagmanager.com",

              // script-src-elem: what modern browsers actually check for <script> tags
              // This is the directive that was missing and causing Turnstile to be blocked
              "script-src-elem 'self' 'unsafe-inline' https://challenges.cloudflare.com https://www.googletagmanager.com",

              "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
              "font-src 'self' https://fonts.gstatic.com",
              "img-src 'self' data: blob:",

              // connect-src: fetch() / XHR destinations
              "connect-src 'self' https://spy9191-chronos-api-backend.hf.space https://*.vercel.app https://challenges.cloudflare.com https://www.google-analytics.com",

              // frame-src: Turnstile renders its challenge inside an iframe
              "frame-src 'self' https://challenges.cloudflare.com",

              // worker-src + child-src: Turnstile uses web workers internally
              "worker-src 'self' blob: https://challenges.cloudflare.com",
              "child-src 'self' blob: https://challenges.cloudflare.com",

              "frame-ancestors 'self'",   // Only allow framing from same origin
            ].join("; "),
          },
        ],
      },
    ];
  },
};

export default nextConfig;
