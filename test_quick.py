"""Quick integration test for Chronos OS API."""
import httpx
import json

client = httpx.Client(base_url="http://localhost:8000", timeout=300)  # 5min for first-time embedding model download

# 1. Generate API key
print("=== GENERATING API KEY ===")
resp = client.post("/billing/keys?tier=explorer")
key_data = resp.json()
api_key = key_data["api_key"]
source_id = key_data["source_id"]
print(f"Key: {api_key[:20]}...")
print(f"Source: {source_id}")

# 2. Ingest events
print("\n=== INGESTING EVENTS ===")
headers = {"X-API-Key": api_key}
events = {
    "source_id": source_id,
    "events": [
        {"text": "Acme Corp signed a 50000 dollar contract for Q2 2026"},
        {"text": "Jane promoted to VP of Engineering on March 15 2026"},
        {"text": "Server migration completed from AWS to Railway on April 1"},
        {"text": "Customer satisfaction score reached 94 percent in Q1 report"},
    ],
}
resp = client.post("/ingest", headers=headers, json=events)
ingest_data = resp.json()
print(f"Ingested: {ingest_data['ingested_count']} events")
print(f"SVO tuples found: {len(ingest_data.get('svo_tuples', []))}")
for svo in ingest_data.get("svo_tuples", []):
    print(f"  SVO: {svo['subject']} | {svo['verb']} | {svo['object']}")

# 3. Query memory
print("\n=== QUERYING MEMORY ===")
query = {"query": "What happened with contracts?", "max_results": 5}
resp = client.post("/query", headers=headers, json=query)
query_data = resp.json()
print(f"Found: {query_data['total_found']} results in {query_data['query_time_ms']}ms")
for r in query_data.get("results", []):
    e = r["event"]
    print(f"  [{e['timestamp'][:10]}] {e['subject']} {e['verb']} {e['object'][:60]}")

# 4. Health check
print("\n=== HEALTH CHECK ===")
resp = client.get("/health")
print(json.dumps(resp.json(), indent=2))

# 5. Usage stats
print("\n=== USAGE STATS ===")
resp = client.get("/billing/usage", headers=headers)
print(json.dumps(resp.json(), indent=2))

print("\n=== ALL TESTS PASSED ===")
