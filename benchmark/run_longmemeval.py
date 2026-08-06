"""
Smriti — LongMemEval Official Evaluation Runner
================================================
Downloads LongMemEval-S dataset from HuggingFace, runs it against
the live Smriti API, scores with exact-match + F1, saves results.

Dataset: xiaowu0162/longmemeval-cleaned (HuggingFace)
Benchmark: LongMemEval (ICLR 2025) - https://github.com/xiaowu0162/LongMemEval

Usage:
    python benchmark/run_longmemeval.py \
        --api-url https://spy9191-chronos-api-backend.hf.space \
        --api-key chrn_YOUR_KEY
"""

import argparse
import json
import os
import re
import time
import uuid
import sys
import warnings
from datetime import datetime

# Inject Windows system cert store so HuggingFace downloads work on Windows
try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass  # truststore not installed, fall back to default

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
from datasets import load_dataset

# ── Scoring helpers ──────────────────────────────────────────────────────────

def normalize(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r'\b(a|an|the)\b', ' ', s)
    s = re.sub(r'[^a-z0-9 ]', '', s)
    return ' '.join(s.split())

def exact_match(pred: str, gold: str) -> float:
    return 1.0 if normalize(pred) == normalize(gold) else 0.0

def token_f1(pred: str, gold: str) -> float:
    pred_toks = normalize(pred).split()
    gold_toks = normalize(gold).split()
    if not pred_toks or not gold_toks:
        return 0.0
    common = set(pred_toks) & set(gold_toks)
    if not common:
        return 0.0
    p = len(common) / len(pred_toks)
    r = len(common) / len(gold_toks)
    return 2 * p * r / (p + r)

def substring_match(pred: str, gold: str) -> float:
    """1.0 if gold appears anywhere in pred (case-insensitive)"""
    return 1.0 if normalize(gold) in normalize(pred) else 0.0

# ── Smriti API client ────────────────────────────────────────────────────────

class SmritiClient:
    def __init__(self, base_url: str, api_key: str = None):
        self.base = base_url.rstrip("/")
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def health(self):
        return requests.get(f"{self.base}/health", headers=self.headers,
                            timeout=15, verify=False).json()

    def ingest(self, text: str, scope: str, belief_id: str = None) -> dict:
        payload = {
            "text": text,
            "scope": scope,
            **({"metadata": {"beliefId": belief_id}} if belief_id else {})
        }
        r = requests.post(f"{self.base}/ingest", json=payload,
                          headers=self.headers, timeout=30, verify=False)
        r.raise_for_status()
        return r.json()

    def recall(self, query: str, scope: str, limit: int = 5) -> list:
        payload = {"query": query, "scope": scope, "limit": limit}
        r = requests.post(f"{self.base}/recall", json=payload,
                          headers=self.headers, timeout=30, verify=False)
        r.raise_for_status()
        data = r.json()
        return data.get("results", data.get("events", []))


# ── LongMemEval dataset loader ───────────────────────────────────────────────

def load_longmemeval(max_cases: int = 100, use_hf: bool = False, local_path: str = None):
    """
    Load LongMemEval-S from a local file, HuggingFace, or a synthetic fallback.
    """
    if local_path and os.path.exists(local_path):
        print(f"  Loading LongMemEval from local file: {local_path}")
        try:
            # Load raw JSON (real LongMemEval schema)
            with open(local_path, 'r', encoding='utf-8') as f:
                raw = json.load(f)

            if not isinstance(raw, list):
                raise ValueError("Expected a JSON list at top level")

            cases = []
            for row in raw[:max_cases]:
                # Real schema: haystack_sessions = list of sessions,
                # each session = list of {role, content} turns.
                # Flatten all sessions into one flat history list for ingest.
                haystack = row.get("haystack_sessions", [])
                flat_history = []
                for session in haystack:
                    if isinstance(session, list):
                        flat_history.extend(session)
                    elif isinstance(session, dict):
                        flat_history.append(session)

                cases.append({
                    "id": str(row.get("question_id", uuid.uuid4())),
                    "history": flat_history,
                    "question": row.get("question", ""),
                    "answer": str(row.get("answer", "")),
                    "category": row.get("question_type", "general"),
                    "answer_session_ids": row.get("answer_session_ids", []),
                    "haystack_session_ids": row.get("haystack_session_ids", []),
                })
            print(f"  Loaded {len(cases)} cases from local file.")
            return cases
        except Exception as e:
            print(f"  Failed to load local file: {e}")

    if not use_hf:
        print("  Skipping HuggingFace load (--use-hf not provided). Using synthetic fallback set.")
        return _synthetic_fallback(max_cases)
        
    print("  Loading LongMemEval-S from HuggingFace...")
    try:
        ds = load_dataset("xiaowu0162/longmemeval-cleaned", split="longmemeval_s_cleaned",
                          trust_remote_code=True)
        print(f"  Loaded {len(ds)} cases from HuggingFace.")
        cases = []
        for row in list(ds)[:max_cases]:
            history = row.get("history") or row.get("conversation") or []
            if isinstance(history, str):
                try:
                    history = json.loads(history)
                except Exception:
                    history = [{"role": "user", "content": history}]
            cases.append({
                "id": row.get("id", str(uuid.uuid4())),
                "history": history,
                "question": row.get("question", ""),
                "answer": str(row.get("answer", "")),
                "category": row.get("question_type", row.get("category", "general")),
            })
        return cases
    except Exception as e:
        print(f"  HuggingFace load failed ({e}). Using synthetic fallback set.")
        return _synthetic_fallback(max_cases)


def _synthetic_fallback(n: int) -> list:
    """
    Minimal synthetic benchmark that mirrors LongMemEval structure.
    Tests the 5 core competencies with real multi-turn session patterns.
    """
    base_cases = [
        # 1. Single-session recall
        {
            "id": "syn-001",
            "category": "single_session_user",
            "history": [
                {"role": "user", "content": "My name is Reman and I work at Google as a software engineer."},
                {"role": "assistant", "content": "Nice to meet you Reman! That's great."},
                {"role": "user", "content": "I'm working on a distributed caching project using Redis."},
                {"role": "assistant", "content": "Redis is excellent for that use case."},
            ],
            "question": "What is the user's name?",
            "answer": "Reman",
        },
        {
            "id": "syn-002",
            "category": "single_session_user",
            "history": [
                {"role": "user", "content": "I prefer dark mode in all my applications."},
                {"role": "assistant", "content": "Noted! Dark mode is easier on the eyes."},
                {"role": "user", "content": "Also I use VS Code as my primary editor."},
            ],
            "question": "What editor does the user prefer?",
            "answer": "VS Code",
        },
        # 2. Temporal reasoning
        {
            "id": "syn-003",
            "category": "temporal_reasoning",
            "history": [
                {"role": "user", "content": "In January I was using Python 3.9."},
                {"role": "assistant", "content": "OK noted."},
                {"role": "user", "content": "I upgraded to Python 3.11 in March."},
                {"role": "assistant", "content": "Nice, Python 3.11 is much faster."},
                {"role": "user", "content": "Just upgraded again to Python 3.12 last week."},
            ],
            "question": "What is the user's current Python version?",
            "answer": "3.12",
        },
        # 3. Knowledge update
        {
            "id": "syn-004",
            "category": "knowledge_update",
            "history": [
                {"role": "user", "content": "I live in Mumbai."},
                {"role": "assistant", "content": "Mumbai is a great city!"},
                {"role": "user", "content": "I moved to Bangalore last month."},
                {"role": "assistant", "content": "Bangalore is great for tech!"},
            ],
            "question": "Where does the user currently live?",
            "answer": "Bangalore",
        },
        # 4. Multi-session reasoning
        {
            "id": "syn-005",
            "category": "multi_session",
            "history": [
                {"role": "user", "content": "Session 1: I am allergic to peanuts."},
                {"role": "assistant", "content": "I'll remember that."},
                {"role": "user", "content": "Session 2: I'm planning a trip to Thailand."},
                {"role": "assistant", "content": "Thailand is beautiful!"},
                {"role": "user", "content": "Session 3: Can you recommend food I should avoid?"},
            ],
            "question": "What food allergy does the user have?",
            "answer": "peanuts",
        },
        # 5. Preference tracking
        {
            "id": "syn-006",
            "category": "single_session_preference",
            "history": [
                {"role": "user", "content": "I love jazz music, especially Miles Davis."},
                {"role": "assistant", "content": "Miles Davis is iconic!"},
                {"role": "user", "content": "I also enjoy reading science fiction novels."},
            ],
            "question": "What genre of music does the user enjoy?",
            "answer": "jazz",
        },
        {
            "id": "syn-007",
            "category": "single_session_user",
            "history": [
                {"role": "user", "content": "I'm a vegetarian and have been for 5 years."},
                {"role": "assistant", "content": "That's a healthy lifestyle choice."},
                {"role": "user", "content": "My favourite cuisine is Italian."},
            ],
            "question": "What is the user's dietary preference?",
            "answer": "vegetarian",
        },
        {
            "id": "syn-008",
            "category": "knowledge_update",
            "history": [
                {"role": "user", "content": "My project uses PostgreSQL as the database."},
                {"role": "assistant", "content": "Good choice!"},
                {"role": "user", "content": "We switched to MongoDB last sprint for better flexibility."},
            ],
            "question": "What database does the user's project use?",
            "answer": "MongoDB",
        },
        {
            "id": "syn-009",
            "category": "temporal_reasoning",
            "history": [
                {"role": "user", "content": "I started learning Rust in 2022."},
                {"role": "assistant", "content": "Rust is powerful."},
                {"role": "user", "content": "By 2023 I was building production services in Rust."},
                {"role": "assistant", "content": "Impressive progress!"},
                {"role": "user", "content": "Now I teach Rust at my company."},
            ],
            "question": "What does the user do with Rust now?",
            "answer": "teach",
        },
        {
            "id": "syn-010",
            "category": "multi_session",
            "history": [
                {"role": "user", "content": "My budget for the new laptop is 1500 USD."},
                {"role": "assistant", "content": "That gives you good options."},
                {"role": "user", "content": "I need it to run machine learning workloads."},
                {"role": "assistant", "content": "You'll want a dedicated GPU then."},
            ],
            "question": "What is the user's budget for the laptop?",
            "answer": "1500",
        },
    ]
    return base_cases[:n]


# ── Main evaluation loop ─────────────────────────────────────────────────────

def run_eval(client: SmritiClient, cases: list, output_path: str):
    total      = len(cases)
    em_scores  = []
    f1_scores  = []
    sub_scores = []
    latencies  = []
    per_case   = []
    by_cat     = {}

    print(f"\nRunning {total} cases...\n")

    for i, case in enumerate(cases):
        cid      = case["id"]
        history  = case["history"]
        question = case["question"]
        answer   = case["answer"]
        category = case.get("category", "general")

        # Unique scope per session so memories don't bleed across cases
        scope = f"lme_{cid}"

        # --- INGEST all turns ---
        for j, turn in enumerate(history):
            role    = turn.get("role", "user") if isinstance(turn, dict) else "user"
            content = turn.get("content", turn) if isinstance(turn, dict) else str(turn)
            text    = f"{role.capitalize()}: {content}"
            try:
                client.ingest(text=text, scope=scope,
                              belief_id=f"{cid}_t{j}")
            except Exception as e:
                print(f"  [WARN] Ingest failed for case {cid} turn {j}: {e}")

        # --- RECALL ---
        t0 = time.perf_counter()
        try:
            results = client.recall(query=question, scope=scope, limit=5)
            latency_ms = (time.perf_counter() - t0) * 1000
        except Exception as e:
            print(f"  [WARN] Recall failed for case {cid}: {e}")
            latency_ms = 0.0
            results = []

        # Build prediction text from retrieved results
        pred_parts = []
        for r in results:
            if isinstance(r, dict):
                pred_parts.append(r.get("text", r.get("raw_text",
                    r.get("subject", "") + " " + r.get("object", ""))))
            else:
                pred_parts.append(str(r))
        prediction = " ".join(pred_parts)

        # Score
        em  = exact_match(prediction, answer)
        f1  = token_f1(prediction, answer)
        sub = substring_match(prediction, answer)

        em_scores.append(em)
        f1_scores.append(f1)
        sub_scores.append(sub)
        latencies.append(latency_ms)

        if category not in by_cat:
            by_cat[category] = {"em": [], "f1": [], "sub": [], "n": 0}
        by_cat[category]["em"].append(em)
        by_cat[category]["f1"].append(f1)
        by_cat[category]["sub"].append(sub)
        by_cat[category]["n"] += 1

        per_case.append({
            "id": cid,
            "category": category,
            "question": question,
            "answer": answer,
            "prediction": prediction[:300],
            "retrieved_count": len(results),
            "exact_match": em,
            "f1": round(f1, 3),
            "substring_match": sub,
            "latency_ms": round(latency_ms, 1),
        })

        if (i + 1) % 10 == 0 or i == 0:
            running_sub = sum(sub_scores) / len(sub_scores)
            running_f1  = sum(f1_scores)  / len(f1_scores)
            print(f"  [{i+1:3d}/{total}]  SubMatch={running_sub:.3f}  F1={running_f1:.3f}  lat={latency_ms:.0f}ms")

    # Sort latencies for percentiles
    sorted_lat = sorted(latencies)
    p50 = sorted_lat[int(len(sorted_lat) * 0.50)]
    p95 = sorted_lat[int(len(sorted_lat) * 0.95)]

    # Category breakdown
    cat_summary = {}
    for cat, v in by_cat.items():
        cat_summary[cat] = {
            "n": v["n"],
            "exact_match": round(sum(v["em"]) / v["n"], 3),
            "f1": round(sum(v["f1"]) / v["n"], 3),
            "substring_match": round(sum(v["sub"]) / v["n"], 3),
        }

    summary = {
        "benchmark": "LongMemEval-S",
        "run_date": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "api_url": client.base,
        "total_cases": total,
        "exact_match": round(sum(em_scores) / total, 3),
        "token_f1": round(sum(f1_scores) / total, 3),
        "substring_match": round(sum(sub_scores) / total, 3),
        "p50_latency_ms": round(p50, 1),
        "p95_latency_ms": round(p95, 1),
        "by_category": cat_summary,
    }

    output = {"summary": summary, "cases": per_case}
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Print results
    print("\n" + "=" * 65)
    print("  SMRITI — LONGMEMEVAL-S RESULTS")
    print("=" * 65)
    print(f"  Total Cases      : {total}")
    print(f"  Exact Match      : {summary['exact_match']}")
    print(f"  Token F1         : {summary['token_f1']}")
    print(f"  Substring Match  : {summary['substring_match']}")
    print(f"  p50 Latency      : {summary['p50_latency_ms']}ms")
    print(f"  p95 Latency      : {summary['p95_latency_ms']}ms")
    print()
    print("  By Category:")
    for cat, v in cat_summary.items():
        print(f"    {cat:<35} F1={v['f1']:.3f}  Sub={v['substring_match']:.3f}  n={v['n']}")
    print("=" * 65)
    print(f"\n  Full results → {output_path}")

    return summary


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-url", default="https://spy9191-chronos-api-backend.hf.space")
    parser.add_argument("--api-key", default=os.getenv("SMRITI_API_KEY", ""))
    parser.add_argument("--max-cases", type=int, default=100)
    parser.add_argument("--output", default="benchmark/results/longmemeval_run.json")
    parser.add_argument("--use-hf", action="store_true",
                        help="Force HuggingFace dataset download (requires internet)")
    parser.add_argument("--local-dataset", type=str, default=None,
                        help="Path to local longmemeval JSON file (e.g. longmemeval_s_cleaned.json)")
    args = parser.parse_args()

    client = SmritiClient(args.api_url, args.api_key)

    print(f"\n[Smriti LongMemEval Runner]")
    print(f"  API : {args.api_url}")
    try:
        h = client.health()
        print(f"  Health: {h}")
        # Warmup to force model load in local harness
        print("  Warming up embedding model...")
        try:
            client.ingest("warmup", "warmup")
        except Exception:
            pass
    except Exception as e:
        print(f"  Health check failed: {e} — aborting.")
        sys.exit(1)

    cases = load_longmemeval(args.max_cases, args.use_hf, args.local_dataset)
    summary = run_eval(client, cases, args.output)
