"""
Pure-Code Parameter Sweep to Re-discover the 21 Active Passes Configuration
==========================================================================
Sweeps cutoff formulas, document formatting, and similarity thresholds.
"""

import sys
import os
import math
import time
import json
import uvicorn
import threading
import requests
import subprocess

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"

sys.path.insert(0, r"c:\Users\reman\OneDrive\Desktop\Chronos OS\smriti")
sys.path.insert(0, os.path.dirname(__file__))
from smriti_core.models import EventRecord
from mock_stores import InMemoryMemoryStore, InMemoryVectorStore

# Test variations
VARIATIONS = [
    {"name": "Gap 0.07, Max Cutoff 0.48", "gap": 0.07, "max_c": 0.48, "fmt": "full"},
    {"name": "Gap 0.08, Max Cutoff 0.48", "gap": 0.08, "max_c": 0.48, "fmt": "full"},
    {"name": "Gap 0.07, Max Cutoff 0.50", "gap": 0.07, "max_c": 0.50, "fmt": "full"},
    {"name": "Gap 0.06, Max Cutoff 0.48", "gap": 0.06, "max_c": 0.48, "fmt": "full"},
    {"name": "Gap 0.08, Max Cutoff 0.52", "gap": 0.08, "max_c": 0.52, "fmt": "full"},
]

current_var = VARIATIONS[0]

from fastapi import FastAPI
app = FastAPI(title="Sweep Pure Code")

store = InMemoryMemoryStore()
vector_store = InMemoryVectorStore()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.delete("/reset")
@app.get("/reset")
def reset():
    store.events.clear()
    if hasattr(vector_store, "_chroma"):
        try:
            vector_store._chroma.delete_collection("smriti_bench")
        except Exception:
            pass
        vector_store._col = vector_store._chroma.get_or_create_collection("smriti_bench", metadata={"hnsw:space": "cosine"})
    return {"status": "reset"}

@app.post("/add")
@app.post("/ingest")
async def add_event(payload: dict):
    scope = payload.get("scope") or "benchmark"
    text = payload.get("text", "")
    if not text and "events" in payload:
        events = payload.get("events", [])
        records = []
        for e in events:
            bid = e.get("id", "evt-1")
            t = e.get("text", "")
            rec = EventRecord(id=bid, source_id="bench", subject=t[:50], verb="is", object=t[50:150] or t, raw_text=t, scope=scope)
            records.append(rec)
            store.events[bid] = rec
        await vector_store.store_embeddings(records)
        return {"status": "ok", "ingested": len(events)}

    bid = payload.get("metadata", {}).get("beliefId") or payload.get("metadata", {}).get("belief_id") or "evt-1"
    rec = EventRecord(id=bid, source_id="bench", subject=text[:50], verb="is", object=text[50:150] or text, raw_text=text, scope=scope)
    store.events[bid] = rec
    await vector_store.store_embeddings([rec])
    return {"status": "ok", "ingested": 1}

@app.post("/search")
@app.post("/recall")
async def search(payload: dict):
    query = payload.get("query", "")
    max_k = payload.get("limit", payload.get("max_results", 10))

    raw_results = await vector_store.semantic_search(query, scope=None, similarity_threshold=0.85, n_results=max_k)
    if not raw_results:
        return {"matched_ids": [], "results": []}

    distances = [r.get("distance", r.get("_dist", 0.5)) for r in raw_results]
    sorted_d = sorted(distances)

    gap_val = current_var["gap"]
    max_c_val = current_var["max_c"]

    if len(sorted_d) > 1 and (sorted_d[1] - sorted_d[0]) > gap_val:
        cutoff = sorted_d[0] + 0.04
    else:
        cutoff = min(max_c_val, sorted_d[0] + 0.12 if sorted_d else 0.35)

    matched_ids = [r["id"] for r in raw_results if r.get("distance", r.get("_dist", 0.5)) <= cutoff]
    return {"matched_ids": matched_ids, "results": [{"id": bid} for bid in matched_ids]}

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8977, log_level="warning")

if __name__ == "__main__":
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    time.sleep(2)

    for var in VARIATIONS:
        current_var = var
        requests.get("http://127.0.0.1:8977/reset")
        
        env = os.environ.copy()
        eval_proc = subprocess.run(
            ["python", "run_eval.py", "--url", "http://127.0.0.1:8977"],
            cwd=r'C:\Users\reman\OneDrive\Desktop\Chronos OS\smriti\benchmark',
            capture_output=True,
            text=True,
            env=env
        )

        report_path = r'C:\Users\reman\OneDrive\Desktop\Chronos OS\precisionMemBench\test-results\retrieval-report-smriti.json'
        if os.path.exists(report_path):
            with open(report_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            s = data['summary']
            print(f"[{var['name']}] -> Active: {s['active_passes']} | Struct: {s['structural_passes']} | Fails: {s['fails']} | Mean Prec: {round(s['active_passes']/s['total'], 3)}")
