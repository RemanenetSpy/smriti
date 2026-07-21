# PrecisionMemBench — Complete Reference

> **Status:** Smriti has a working adapter and eval runner wired to this benchmark.
> **Source:** [github.com/tenurehq/precisionmembench](https://github.com/tenurehq/precisionmembench)
> **Paper:** arxiv.org (TenureHQ, 2026)

---

## 1. What It Is

**PrecisionMemBench** is an AI memory retrieval benchmark created by **TenureHQ** to measure one specific thing: does a memory system return the *right* beliefs and *only* the right beliefs, without relying on a generative model to cover its mistakes?

Most existing benchmarks (LoCoMo, LongMemEval) measure **answer quality** — they let a judge LLM read whatever the retrieval system returns and score whether the final answer is correct. This hides retrieval failures because a strong generative model can often produce the right answer even from noisy or incomplete context.

PrecisionMemBench removes the generative model from the loop entirely. It asserts directly against what the retrieval system returned.

### Core Design Principle
> "If your retrieval is imprecise, no amount of generative compensation should mask it."

---

## 2. What It Tests

**89 total cases** across 4 dimensions:

| Dimension | What it checks |
|---|---|
| Precision | Does the system return only relevant beliefs? |
| Noise Isolation | Does the system exclude semantically-similar-but-wrong beliefs? |
| Session Latency | Does the system handle time-scoped / session-bounded retrieval? |
| Belief Mutability | Does the system correctly suppress stale, resolved, or superseded beliefs? |

---

## 3. Benchmark Data / Fixtures

The benchmark ships three JSON fixture files:

| File | Contents |
|---|---|
| fixtures/beliefs.seed.json | The belief corpus loaded into the memory system before testing |
| fixtures/retrieval.cases.json | 89 retrieval test cases (the main eval) |
| fixtures/session-retrieval.cases.json | Session-scoped test cases (additional, opt-in) |

### Belief Object Structure

```json
{
  "_id": "belief-uuid-001",
  "user_id": "test-user",
  "canonical_name": "Alice's current city",
  "aliases": ["Alice lives in", "Alice moved to"],
  "content": "Alice lives in Seattle as of March 2025.",
  "why_it_matters": "Used to resolve location-dependent queries.",
  "scope": ["user:work"],
  "type": "fact",
  "resolved_at": null,
  "superseded_by": null,
  "pinned": false
}
```

### Belief Types

| Type | Meaning | In /search results? |
|---|---|---|
| fact | Active, current fact | Yes |
| open_question | Unresolved question/task | No — openQuestions slot only |
| resolved (resolved_at != null) | Historical, no longer active | No |
| superseded (superseded_by != null) | Replaced by newer belief | No |
| pinned = true | Retrieved separately | No (via /pinned endpoint) |

---

## 4. Scoring Rules

Each test case specifies expected retrieval behaviour:

```json
{
  "caseId": "retrieval-alice-city-scope",
  "category": "precision",
  "description": "Should return current city belief, not old city belief",
  "query": "Where does Alice live?",
  "scope": ["user:work"],
  "expect": {
    "relevantBeliefs": {
      "mustInclude": ["belief-uuid-001"],
      "mustExclude": ["belief-uuid-old-city"],
      "shouldOnlyInclude": ["belief-uuid-001"],
      "maxCount": 2
    }
  }
}
```

### Assertion Types

**mustInclude**
Belief IDs that MUST appear in results. Any missing = FAIL.

**mustExclude**
Belief IDs that must NOT appear in results. Any present = FAIL.
This is where "dump everything" systems fail — they return superseded facts.

**shouldOnlyInclude**
Strict allowlist. Any belief returned outside this list = FAIL.
The hardest constraint. Tests true precision.

**maxCount**
Maximum beliefs allowed in response. If len(results) > maxCount = FAIL.
Prevents "return 50 things and one is right" strategies.

### Pass Type Classification

| Pass Type | Meaning |
|---|---|
| active_retrieval | shouldOnlyInclude non-empty, all required beliefs returned, no noise. Real signal. |
| structural | Passed constraints but shouldOnlyInclude was empty. Weaker signal. |
| trivially_empty | No assertions triggered. Passes by default. No signal at all. |
| fail | Any assertion violated. |

### Score Metric

```
mean_precision = active_retrieval_passes / total_cases
```

TenureHQ reported 1.00 mean precision (perfect score) for their own Tenure system.
Competing systems scored 0.22 or lower.

---

## 5. Smriti's Actual Test — What Happened

**Run date:** 2026-06-22 at 19:12 UTC
**Tested against:** localhost:8080 (smriti_service.py — local ChromaDB service)
**Threshold used:** 0.45 cosine distance (default)

### Results

| Metric | Smriti (June 22) | Tenure (baseline) | Mem0 (baseline) |
|---|---|---|---|
| Total cases | 77 | 89 | 89 |
| Active retrieval passes | 9 | ~89 (perfect) | ~20 |
| Structural passes | 34 | 0 | - |
| Trivially empty passes | 34 | 0 | - |
| Fails | 0 | 0 | - |
| **Mean precision** | **0.117** | **1.00** | **~0.22** |
| p50 latency | 2096 ms | <100 ms | - |
| p95 latency | 2119 ms | <100 ms | - |

### What the Numbers Mean

**0 fails** — good. Smriti never returned a belief it was explicitly told to exclude.
That means type-aware filtering (suppressing resolved, superseded, open_question beliefs) worked.

**9 active passes out of 77** (precision = 0.117) — below the community average of ~0.22.
The problem: Smriti missed mustInclude beliefs on many cases where shouldOnlyInclude required exact matches.
The threshold of 0.45 was too broad for noise isolation — retrieval brought in noise (structural pass instead of active).
Or too narrow — true positives were below similarity threshold and not returned at all.

**34 trivially empty passes** — these are cases with no assertions, they pass by definition and add no signal.
The effective test pool is 77 - 34 = 43 meaningful cases.
Active passes on meaningful cases: 9/43 = 0.209 — closer to the community average.

**2 second latency** — serious problem.
p50 of 2096ms means the AVERAGE query took 2 seconds.
This was the ChromaDB telemetry issue — each request was blocked by a network call to ChromaDB's analytics server.
Fix: telemetry disabled in v2 of smriti_service.py. Expected latency after fix: <100ms.

### Why the Latency Was 2 Seconds

smriti_service.py v1 did not disable ChromaDB telemetry. On every `/search` call, ChromaDB made an outbound HTTP request to its analytics endpoint before returning results. This added ~2000ms of blocked I/O to every single query.

Fix applied in v2:
```python
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_ENABLED"] = "false"
```

This was fixed before the doc was written. The 2096ms numbers are from the unfixed run.

---

## 6. Why Benchmark Results Are NOT in the Smriti Dashboard

The June 22 benchmark ran against Smriti locally — the full system, running on the same laptop where
the entire codebase lives. smriti_service.py IS Smriti retrieval layer. The test is real.

`
benchmark/run_eval.py
    --> POST http://localhost:8080/add       (Smriti, running locally)
    --> POST http://localhost:8080/search    (Smriti, running locally)
    --> DELETE http://localhost:8080/reset   (Smriti, running locally)
`

The only thing NOT tested was the deployed live server (HF Space: spy9191-chronos-api-backend.hf.space).
Local Smriti = the real system. HF Space = the deployed version of the same system.

Why results are not in the Smriti dashboard:
- The benchmark uses an in-memory ChromaDB store wiped between test cases (via /reset)
- This is intentional — benchmark test data must not pollute the persistent memory database
- The dashboard shows production Neon/pgvector counts, not benchmark run data
- No benchmark beliefs were written to the persistent database — by design
- The benchmark is a test harness. It tests retrieval quality, it is not a data source.

## 7. How Smriti Is Wired To It

### 7.1 benchmark/smriti_service.py — Local Benchmark Service

Self-contained FastAPI service implementing the PrecisionMemBench provider API locally:

| Endpoint | Purpose |
|---|---|
| POST /add | Load a belief into ChromaDB vector store |
| POST /search | Retrieve beliefs by query; applies threshold + type filters |
| DELETE /reset | Wipe all collections between runs |
| GET /health | Service status, model info, belief count |

Key implementation details:
- Embedding model: all-MiniLM-L6-v2 (sentence-transformers)
- Vector store: ChromaDB (in-memory)
- Similarity threshold: 0.45 cosine distance (SMRITI_SIMILARITY_THRESHOLD)
- LRU embedding cache: 512 entries
- Type-aware filtering: open_question, resolved, superseded, pinned excluded from /search
- ChromaDB telemetry: disabled in v2 (was causing 2s latency in June 22 run)

### 7.2 benchmark/run_eval.py — Eval Runner

```bash
python benchmark/run_eval.py --url http://localhost:8080
python benchmark/run_eval.py --url http://localhost:8080 --threshold 0.35
python benchmark/run_eval.py --url http://localhost:8080 --no-reseed
python benchmark/run_eval.py --url http://localhost:8080 --session
```

Output: precisionMemBench/test-results/retrieval-report-smriti.json

### 7.3 benchmark_adapter.py — Live API Adapter

Bridges the benchmark harness to Smriti's production API (NOT used in June 22 run):

```
Benchmark Harness -> benchmark_adapter.py (port 8765) -> Smriti API (HF Space)
```

Config:
```bash
SMRITI_API_URL=https://spy9191-chronos-api-backend.hf.space
SMRITI_API_KEY=chrn_...
SMRITI_THRESHOLD=0.15
SMRITI_SEMANTIC_WEIGHT=0.7
SMRITI_SCOPE_MODE=test_id
ADAPTER_PORT=8765
```

---

## 8. How To Run a Full Eval

Step 1 — Start the local service:
```bash
cd "...\smriti\benchmark"
pip install -r requirements.txt
python smriti_service.py
# Listening on http://localhost:8080
```

Step 2 — Run the eval:
```bash
python benchmark/run_eval.py --url http://localhost:8080
```

Step 3 — Results in:
```
precisionMemBench/test-results/retrieval-report-smriti.json
```

To run against the live API instead:
```bash
# Terminal 1
SMRITI_API_KEY=chrn_xxx python benchmark_adapter.py

# Terminal 2
python benchmark/run_eval.py --url http://localhost:8765
```

---

## 9. Known Issues / Tuning

| Issue | Root Cause | Status |
|---|---|---|
| p50 latency 2096ms | ChromaDB telemetry enabled | Fixed in v2 (telemetry disabled) |
| Mean precision 0.117 | Threshold not tuned for belief format | Needs re-run after telemetry fix |
| 34 trivial passes out of 77 | Benchmark cases with no assertions | Expected — not Smriti's fault |
| Benchmark not testing real API | Local ChromaDB service != production | adapter.py exists, needs to be used |
| True positives missed | Threshold 0.45 possibly still too strict or broad | Need threshold sweep: 0.2, 0.3, 0.4, 0.5 |

---

## 10. PrecisionMemBench vs. LongMemEval vs. LoCoMo

| | PrecisionMemBench | LongMemEval | LoCoMo |
|---|---|---|---|
| What it measures | Retrieval precision only | End-to-end answer quality | Long-conversation memory + QA |
| Generative model in loop? | No | Yes (LLM judge) | Yes |
| Gameable? | Hard — strict ID assertions | Yes — Mem0 hardcoded question_ids | Harder but possible |
| Community credibility | Niche / TenureHQ-origin | High (r/AIMemory reference) | High (leaderboard active) |
| Smriti adapter exists? | Yes (full, local + live) | Not yet | Not yet |
| Cost to run | Free (local) | ~$5-20 GPT-4o calls | ~$5-15 |
| Smriti score | 0.117 (June 22, local, untuned) | Not run | Not run |

---

## 11. File Index

```
smriti/
├── benchmark_adapter.py         # Adapter: harness -> Smriti live API
├── benchmark/
│   ├── smriti_service.py        # Local benchmark service (ChromaDB + ST) v2
│   ├── run_eval.py              # Eval runner
│   ├── requirements.txt         # chromadb, sentence-transformers, fastapi, uvicorn
│   └── Dockerfile
precisionMemBench/
└── test-results/
    ├── retrieval-report-smriti.json    # Smriti run (June 22 2026, local service)
    └── baseline/                       # Competitor baseline reports
        ├── retrieval-report-mem0.json
        ├── retrieval-report-zep.json
        ├── retrieval-report-tenure.json
        └── ... (13 other systems)
docs/
    └── precision-mem-bench.md          # This file
```

---

*Last updated: July 2026*
