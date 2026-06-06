"use client";

import { useEffect, useRef } from "react";

declare global {
  interface Window {
    turnstile?: {
      render: (el: HTMLElement, opts: Record<string, unknown>) => string;
      remove: (id: string) => void;
      reset: (id: string) => void;
    };
  }
}

const SITE_KEY =
  process.env.NEXT_PUBLIC_CF_TURNSTILE_SITE_KEY ||
  "1x00000000000000000000AA"; // CF test key — always passes in dev

interface Props {
  onToken: (token: string) => void;
  onError?: () => void;
  theme?: "light" | "dark" | "auto";
  size?: "normal" | "compact" | "flexible" | "invisible";
  style?: React.CSSProperties;
}

export function TurnstileWidget({
  onToken,
  onError,
  theme = "auto",
  size = "normal",
  style,
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const widgetIdRef  = useRef<string | null>(null);

  useEffect(() => {
    let mounted = true;

    function renderWidget() {
      if (!mounted || !containerRef.current || widgetIdRef.current) return;
      widgetIdRef.current =
        window.turnstile?.render(containerRef.current, {
          sitekey: SITE_KEY,
          callback: (token: string) => onToken(token),
          "error-callback": () => {
            onToken("");
            onError?.();
          },
          "expired-callback": () => onToken(""),
          theme,
          size,
        }) ?? null;
    }

    // Turnstile already loaded
    if (window.turnstile) {
      renderWidget();
      return () => { mounted = false; };
    }

    // Check if script tag already exists (another component loaded it)
    const existing = document.querySelector<HTMLScriptElement>(
      'script[src*="challenges.cloudflare.com/turnstile"]'
    );
    if (existing) {
      existing.addEventListener("load", renderWidget);
      return () => {
        mounted = false;
        existing.removeEventListener("load", renderWidget);
      };
    }

    // Load for the first time
    const script = document.createElement("script");
    script.src =
      "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
    script.async = true;
    script.defer = true;
    script.addEventListener("load", renderWidget);
    document.head.appendChild(script);

    return () => {
      mounted = false;
      script.removeEventListener("load", renderWidget);
      if (widgetIdRef.current) {
        window.turnstile?.remove(widgetIdRef.current);
        widgetIdRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return <div ref={containerRef} style={style} />;
}
