"""
Smriti — LongMemEval HTTP Adapter
====================================
Runs the LongMemEval benchmark (ICLR 2025) against any live Smriti-compatible
REST API endpoint. No local library installation of Smriti required.

LongMemEval dataset: https://github.com/xiaowu0162/LongMemEval
  - 500+ QA pairs across multi-session conversations
  - Tests: temporal reasoning, multi-session synthesis, single-session recall

Usage:
  # Against live production API
  python benchmark/adapters/longmemeval_adapter.py \
      --api-url https://smriti-kaal.hf.space \
      --api-key YOUR_SMRITI_API_KEY \
      --data-path ./longmemeval_data/longmemeval_s.json \
      --output-path ./benchmark/results/longmemeval_results.json

  # Against local test server
  python benchmark/adapters/longmemeval_adapter.py \
      --api-url http://127.0.0.1:8976 \
      --data-path ./longmemeval_data/longmemeval_s.json

Requirements:
  pip install requests tqdm openai   # openai SDK used for LLM-as-judge scoring
  Download dataset from: https://github.com/xiaowu0162/LongMemEval/tree/main/data
"""

import argparse
import json
import os
import time
import requests
from typing import Optional

# ──────────────────────────────────────────────
# Smriti HTTP Client
# ──────────────────────────────────────────────
class SmritiClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None, scope: str = "longmemeval"):
        self.base_url = base_url.rstrip("/")
        self.headers  = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        self.scope = scope

    def health(self) -> dict:
        return requests.get(f"{self.base_url}/health", headers=self.headers, timeout=10).json()

    def reset(self):
        requests.get(f"{self.base_url}/reset", headers=self.headers, timeout=10)

    def ingest(self, event_id: str, text: str) -> dict:
        payload = {
            "text": text,
            "scope": self.scope,
            "metadata": {"beliefId": event_id}
        }
        r = requests.post(f"{self.base_url}/ingest", json=payload, headers=self.headers, timeout=30)
        r.raise_for_status()
        return r.json()

    def recall(self, query: str, limit: int = 5) -> list[dict]:
        payload = {"query": query, "limit": limit, "scope": self.scope}
        r = requests.post(f"{self.base_url}/recall", json=payload, headers=self.headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data.get("results", data.get("matched_ids", []))

# ──────────────────────────────────────────────
# Simple exact-match scorer (no LLM needed)
# ──────────────────────────────────────────────
def score_exact(prediction: str, ground_truth: str) -> float:
    """Returns 1.0 if ground truth appears in prediction (case-insensitive), else 0.0"""
    return 1.0 if ground_truth.strip().lower() in prediction.strip().lower() else 0.0

# ──────────────────────────────────────────────
# Main Evaluation Loop
# ──────────────────────────────────────────────
def run_evaluation(client: SmritiClient, data_path: str, output_path: str, max_cases: int = 500):
    with open(data_path, encoding="utf-8") as f:
        dataset = json.load(f)

    results   = []
    total     = min(len(dataset), max_cases)
    correct   = 0
    latencies = []

    print(f"\nRunning LongMemEval on {total} cases against {client.base_url}...\n")

    for i, case in enumerate(dataset[:total]):
        session_id = case.get("session_id", f"session_{i}")
        turns      = case.get("history", case.get("conversation", []))
        question   = case.get("question", "")
        answer     = case.get("answer",   "")

        # Reset per session
        client.reset()

        # Ingest conversation turns
        for j, turn in enumerate(turns):
            text = turn if isinstance(turn, str) else f"{turn.get('role','')}: {turn.get('content','')}"
            client.ingest(event_id=f"{session_id}_turn_{j}", text=text)

        # Query
        t0 = time.perf_counter()
        retrieved = client.recall(question, limit=5)
        latency_ms = (time.perf_counter() - t0) * 1000

        # Build prediction from retrieved context
        context = " ".join([
            r.get("text", r.get("id", "")) if isinstance(r, dict) else str(r)
            for r in retrieved
        ])
        score = score_exact(context, answer)

        correct   += score
        latencies.append(latency_ms)
        results.append({
            "session_id": session_id,
            "question":   question,
            "answer":     answer,
            "score":      score,
            "latency_ms": round(latency_ms, 1),
            "context_retrieved": len(retrieved)
        })

        if (i + 1) % 50 == 0:
            print(f"  [{i+1}/{total}] Running accuracy: {round(correct/(i+1), 3)}")

    # Summary
    accuracy   = round(correct / total, 3)
    p50        = round(sorted(latencies)[int(len(latencies)*0.5)], 1)
    p95        = round(sorted(latencies)[int(len(latencies)*0.95)], 1)

    summary = {
        "benchmark": "LongMemEval",
        "total_cases": total,
        "correct": int(correct),
        "accuracy": accuracy,
        "p50_latency_ms": p50,
        "p95_latency_ms": p95,
        "api_url": client.base_url
    }

    output = {"summary": summary, "cases": results}
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 60)
    print("LONGMEMEVAL RESULTS")
    print(f"  Total Cases  : {total}")
    print(f"  Correct      : {int(correct)}")
    print(f"  Accuracy     : {accuracy}")
    print(f"  p50 Latency  : {p50}ms")
    print(f"  p95 Latency  : {p95}ms")
    print("=" * 60)
    print(f"\nFull results saved to: {output_path}")

    return summary

# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LongMemEval adapter for Smriti REST API")
    parser.add_argument("--api-url",   required=True,  help="Smriti API base URL")
    parser.add_argument("--api-key",   default=None,   help="Smriti API key (optional for local)")
    parser.add_argument("--data-path", required=True,  help="Path to LongMemEval JSON dataset file")
    parser.add_argument("--output-path", default="benchmark/results/longmemeval_results.json")
    parser.add_argument("--max-cases", type=int, default=500)
    parser.add_argument("--scope",     default="longmemeval")
    args = parser.parse_args()

    client = SmritiClient(args.api_url, args.api_key, args.scope)
    print("Health check:", client.health())
    run_evaluation(client, args.data_path, args.output_path, args.max_cases)
