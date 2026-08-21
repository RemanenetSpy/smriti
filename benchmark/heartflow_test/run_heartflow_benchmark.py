import os
import sys
import time
import requests
import json

API_URL = "https://spy9191-chronos-api-backend.hf.space"
API_KEY = os.environ.get("SMRITI_API_KEY")

if not API_KEY:
    print("ERROR: SMRITI_API_KEY environment variable not set.")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# The 6 Fixture States derived from the HeartFlow maintainer's description
FIXTURES = [
    {
        "description": "F1: Baseline fact insertion",
        "events": [{"text": "John lives in New York.", "timestamp": "2024-01-01T10:00:00Z"}]
    },
    {
        "description": "F2: Direct supersession (same subject, same domain)",
        "events": [{"text": "John lives in San Francisco.", "timestamp": "2024-01-02T10:00:00Z"}]
    },
    {
        "description": "F3: Alias gap (the user vs John)",
        "events": [{"text": "The user moved to London.", "timestamp": "2024-01-03T10:00:00Z"}]
    },
    {
        "description": "F4: Tag-awareness context (work scope)",
        "events": [{"text": "John works at Google.", "scope": "work", "timestamp": "2024-01-04T10:00:00Z"}]
    },
    {
        "description": "F5: Orthogonal domain insertion (no supersession expected)",
        "events": [{"text": "John bought a dog.", "timestamp": "2024-01-05T10:00:00Z"}]
    },
    {
        "description": "F6: Temporal closure (closing a state in work scope)",
        "events": [{"text": "John is no longer employed at Google.", "scope": "work", "timestamp": "2024-01-06T10:00:00Z"}]
    }
]

print("==================================================")
print("RUNNING FULL 6-FIXTURE HEARTFLOW BENCHMARK")
print(f"Target: {API_URL}")
print("==================================================\n")

print("--- PHASE 1: INGESTION ---")
for i, fix in enumerate(FIXTURES):
    print(f"Ingesting {fix['description']}")
    payload = {
        "source_id": "hf_benchmark_runner_v3",
        "events": fix["events"],
        "parse_svo": True,
        "scope": "heartflow_bench"  # Default scope for the payload
    }
    
    try:
        resp = requests.post(f"{API_URL}/ingest", json=payload, headers=HEADERS)
        if resp.status_code in [200, 201]:
            print(f"  [OK] Successfully ingested.")
        else:
            print(f"  [ERROR] {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"  [EXCEPTION] {e}")
    time.sleep(1.5) # ensure order processing and vector indexing

print("\n--- PHASE 2: FULL 6-TEST QUERY BENCHMARK ---")

# 6 Explicit tests for the 6 fixtures
QUERIES = [
    {
        "test_name": "Test 1: Direct Supersession (F1 vs F2)",
        "query": "Where does John live?",
        "scope": "heartflow_bench",
        "expected": "San Francisco",
        "fail_if_contains": "New York"
    },
    {
        "test_name": "Test 2: Alias Gap Retrieval (F3)",
        "query": "Where does the user live?",
        "scope": "heartflow_bench",
        "expected": "London",
        "fail_if_contains": ""
    },
    {
        "test_name": "Test 3: Orthogonal Domain (F5)",
        "query": "What pet does John have?",
        "scope": "heartflow_bench",
        "expected": "dog",
        "fail_if_contains": "San Francisco"
    },
    {
        "test_name": "Test 4: Tag-Awareness - Correct Scope (F4 & F6)",
        "query": "Where does John work?",
        "scope": "work",
        "expected": "no longer employed",
        "fail_if_contains": ""
    },
    {
        "test_name": "Test 5: Tag-Awareness - Isolation (F4 & F6 from wrong scope)",
        "query": "Where does John work?",
        "scope": "personal", 
        "expected": "no results", # Should return 0 results or fallback
        "fail_if_contains": "Google"
    },
    {
        "test_name": "Test 6: Temporal Closure Validation (F6)",
        "query": "Is John employed at Google?",
        "scope": "work",
        "expected": "no longer",
        "fail_if_contains": "works at Google"
    }
]

false_positives = 0
false_negatives = 0
passed = 0

for q in QUERIES:
    print(f"\nEvaluating {q['test_name']}")
    print(f"Query: '{q['query']}' | Scope: '{q['scope']}'")
    
    payload = {
        "query": q["query"],
        "max_results": 5,
        "semantic_weight": 0.8, # Bumped up to prioritize semantic match over raw temporal recency
        "scope": q["scope"],
        "source_ids": ["hf_benchmark_runner_v3"]
    }
    
    try:
        start = time.time()
        resp = requests.post(f"{API_URL}/query", json=payload, headers=HEADERS)
        latency = (time.time() - start) * 1000
        
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            total_found = data.get('total_found', 0)
            
            print(f"  Latency: {latency:.2f}ms | Found: {total_found} events")
            
            if q["expected"] == "no results":
                if total_found == 0 or q["fail_if_contains"].lower() not in str(results[0].get("event", {})).lower():
                    print("  [PASS] Correctly isolated scope.")
                    passed += 1
                else:
                    print(f"  [FAIL] False Positive: Leaked data across scopes: {results[0].get('event')}")
                    false_positives += 1
                continue

            if not results:
                print("  [FAIL] False Negative: No results retrieved.")
                false_negatives += 1
                continue
                
            top_result = str(results[0].get("event", {}))
            
            if q["expected"].lower() in top_result.lower():
                print(f"  [PASS] Correct valid_to state retrieved.")
                passed += 1
            else:
                print(f"  [FAIL] Retrieved incorrect state: {top_result}")
                false_positives += 1
                
        else:
            print(f"  [ERROR] {resp.status_code} - {resp.text}")
            
    except Exception as e:
        print(f"  [EXCEPTION] {e}")

print("\n==================================================")
print("FULL 6-FIXTURE BENCHMARK RESULTS")
print("==================================================")
print(f"Total Queries: {len(QUERIES)}")
print(f"Passed: {passed}")
print(f"False Positives (Hallucination/Wrong State): {false_positives}")
print(f"False Negatives (Missed Retrieval): {false_negatives}")
print("==================================================")
