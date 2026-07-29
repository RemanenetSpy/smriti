# Smriti Benchmark Suite

All benchmark harnesses, evaluation adapters, results, and research docs for Smriti.
Production code (`smriti_core/`) is never modified by anything here.

## Structure

```
benchmark/
├── README.md
├── harness/
│   ├── run_precision_bench.py    # Best config: Gap 0.08 / Max 0.52 → 23 Active / 0.299 Precision
│   ├── sweep_pure_code.py        # Parameter sweep to find optimal configs
│   └── mock_stores.py            # In-memory ChromaDB + EventRecord for isolated testing
├── adapters/
│   └── longmemeval_adapter.py    # LongMemEval (ICLR 2025) via HTTP REST
└── results/
    ├── algorithm_comparison.md   # All algorithms, results, production implications
    └── precision_mem_bench.md    # Raw run-by-run log of every test
```

## Quick Start

```bash
cd smriti/
python benchmark/harness/run_precision_bench.py
```

Best result: **23 Active Passes / 77 cases — Precision 0.299 — p50 ~24ms — 0 query LLM calls**

## Run LongMemEval (ICLR 2025)

```bash
# Download dataset first: github.com/xiaowu0162/LongMemEval
python benchmark/adapters/longmemeval_adapter.py \
    --api-url https://smriti-kaal.hf.space \
    --api-key YOUR_KEY \
    --data-path ./longmemeval_data/longmemeval_s.json
```

## Algorithm Results Summary

| Algorithm                         | Active | Precision |
|:----------------------------------|:------:|:---------:|
| Baseline Static Cutoff            |   9    |   0.117   |
| Pure Bayesian Gap Cutoff          |  17    |   0.221   |
| Stateful Kalman Filter (v2)       |  18    |   0.234   |
| Neuron Forge Oppose Strong/Weak   |  16    |   0.208   |
| Dual-Stage Entity SVO + Bayesian  |  17    |   0.221   |
| **Sweep: Gap 0.08 / Max 0.52**    | **23** | **0.299** |

Full details: `results/algorithm_comparison.md`

## Requirements

```bash
pip install sentence-transformers chromadb fastapi uvicorn requests
```
