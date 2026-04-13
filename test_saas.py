"""Test SaaS Connector integration with the Agent."""
import httpx
import json

API = "http://localhost:8000"

# Step 1: Generate key
print("=== Setting up ===")
key_data = httpx.post(f"{API}/billing/keys?tier=builder").json()
KEY = key_data["api_key"]
H = {"X-API-Key": KEY}
print(f"Key generated: {KEY[:15]}...")

# Step 2: Register a SaaS connector (Mock API)
print("\n=== Connecting SaaS Tool ===")
connect_req = {
    "name": "UserDirectory SaaS",
    "description": "A REST API to fetch user profiles and directory information.",
    "base_url": "https://jsonplaceholder.typicode.com",
    "endpoints": [
        {
            "method": "GET",
            "path": "/users/1",
            "description": "Fetch the profile data for Leanne Graham (User 1)"
        }
    ]
}

conn = httpx.post(f"{API}/connect", headers=H, json=connect_req).json()
print("SaaS Connected!")
print(f"Data: {json.dumps(conn, indent=2)}")

# Step 3: Run the Agent to use the tool
print("\n=== Calling Agent ===")
prompt = "Use the connected 'UserDirectory SaaS' tool to fetch information for User 1. Tell me their name and email."
print(f"Prompt: {prompt}")

chat = httpx.post(f"{API}/agent/run", headers=H, json={
    "prompt": prompt,
}, timeout=60).json()

print("\n=== Agent Response ===")
print(chat.get("response", "No response text found."))

print("\n=== Execution Steps ===")
for i, step in enumerate(chat.get("steps", [])):
    print(f"\nStep {i+1} Type: {step.get('type')}")
    if step.get('type') == 'ai':
        print(f"Content: {step.get('content', '')[:100]}...")
        if step.get('tool_calls'):
            print(f"Tool Calls: {json.dumps(step.get('tool_calls'), indent=2)}")
