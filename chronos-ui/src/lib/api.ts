// API helper for Chronos API
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiCall(
  method: "GET" | "POST",
  path: string,
  apiKey: string,
  body?: any
) {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };
  
  if (apiKey) {
    headers["Authorization"] = `Bearer ${apiKey}`;
  }

  const url = `${API_BASE}${path}`;
  
  try {
    const res = await fetch(url, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
    
    if (!res.ok) {
      let errStr = res.statusText;
      try {
        const errJson = await res.json();
        errStr = errJson.detail || errStr;
      } catch (e) {}
      throw new Error(`HTTP ${res.status}: ${errStr}`);
    }
    
    return await res.json();
  } catch (error: any) {
    throw new Error(error.message || "Failed to connect to Chronos API");
  }
}
