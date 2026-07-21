# AI Model Comparison — Local vs Free Cloud APIs

> **Purpose**: Choose the right brain for each task in the Marketing Engine.
> Hardware: RTX 3060 · 4GB VRAM · 16GB RAM · Windows

---

## Part 1 — Local Models (Zero Cost, Zero Internet)

Run 100% on your machine via Ollama or LM Studio.

| Model | Maker | Params | VRAM (Q4) | Context |
|---|---|---|---|---|
| **Llama 3.2 3B** | Meta | 3.2B | ~2.2 GB | 128K |
| **Phi-3.5 Mini** | Microsoft | 3.8B | ~2.6 GB | 128K |
| **Gemma 2 2B** | Google | 2.6B | ~3.0 GB (Q8) | 8K |
| **Falcon 3 3B** | TII | 3B | ~2.3 GB | 8K |
| **DeepSeek R1 1.5B** | DeepSeek | 1.5B | ~1.1 GB | 64K |
| **DeepSeek R1 7B** | DeepSeek | 7B | ~4.0 GB (tight) | 64K |
| ~~Mistral 7B~~ | Mistral | 7.3B | ~3.5 GB (tight) | 32K |

### Capability Breakdown — Local Models

| Capability | Llama 3.2 3B | Phi-3.5 Mini | Gemma 2 2B | DS R1 1.5B | DS R1 7B |
|---|---|---|---|---|---|
| **Text Generation** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Math / Reasoning** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Coding / Logic** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Self-correction** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Conversation / Reply** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Summarization** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **SEO / Keyword writing** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Image generation** | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Vision (image input)** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Speed (tok/sec local)** | ~80–100 | ~60–80 | ~70–90 | ~120–150 | ~40–60 |
| **VRAM safe for 4GB** | ✅ Easy | ✅ Easy | ✅ Easy | ✅ Very easy | ⚠️ Tight |

### Local Model Winner Per Task

| Task | Best Local Model | Why |
|---|---|---|
| Writing captions / posts | **Phi-3.5 Mini** | Best text quality at small size |
| Replying to comments | **Gemma 2 2B** | Best conversational fluency |
| Risk scoring / decisions | **DeepSeek R1 1.5B** | Chain-of-thought reasoning, tiny VRAM |
| Code self-repair / logic | **DeepSeek R1 7B** | Built for reasoning + rewriting |
| Fast background tasks | **Llama 3.2 3B** | Fastest + has vision |

---

## Part 2 — DeepSeek R1 — The Reasoning Giant

> [!IMPORTANT]
> DeepSeek R1 is not just a language model. It is a **reasoning model** trained with reinforcement learning, designed to think step-by-step before answering. This makes it fundamentally different from all other models above.

### What Makes R1 Special

| Feature | Normal Models | DeepSeek R1 |
|---|---|---|
| How it answers | Directly outputs text | Thinks out loud first (chain-of-thought), then answers |
| Self-correction | Rare | **Built-in** — it catches and fixes its own errors mid-thought |
| Reasoning depth | Surface level | Explores multiple approaches before committing |
| Code rewriting | Basic edits | Analyzes why code fails, rewrites with explanation |
| Math accuracy | Moderate | Near-perfect on complex problems |

### All DeepSeek R1 Variants

| Variant | Type | Params | VRAM (Q4) | Free API | Best Use |
|---|---|---|---|---|---|
| **R1 1.5B** (Distilled) | Local | 1.5B | ~1.1 GB | Groq | Fast local scoring, logic checks |
| **R1 7B** (Distilled) | Local | 7B | ~4.0 GB | Groq / OpenRouter | Local code reasoning (tight fit) |
| **R1 14B** (Distilled) | Local (needs RAM offload) | 14B | ~8 GB | Groq | Too heavy for 4GB alone |
| **R1 32B** (Distilled) | Cloud only | 32B | 18 GB | Groq / OpenRouter | Best reasoning via free API |
| **R1 70B** (Distilled) | Cloud only | 70B | 40 GB | Groq | Near-full R1 power free |
| **R1 671B** (Full) | Cloud only | 671B | 400 GB | OpenRouter (paid) | Godmode — not needed yet |

### R1 Benchmark vs Other Models

| Benchmark | GPT-4o | Gemini Flash | Llama 70B | **DeepSeek R1** |
|---|---|---|---|---|
| MATH-500 | 76% | 71% | 68% | **97.3%** |
| AIME (hard math) | 9.3% | 7% | 4% | **79.8%** |
| Codeforces (coding) | 46% | 40% | 34% | **96.3%** |
| MMLU (knowledge) | 88% | 85% | 86% | **90.8%** |
| LiveCodeBench | 53% | 48% | 44% | **65.9%** |

> R1 is the **#1 open-source reasoning model** as of early 2026. Free via Groq.

### R1's Role in the Marketing Engine: Self-Improvement

This is the game-changing part. Because R1 reasons step by step and can self-correct, it can:

```
1. Read the engine's own source code
2. Read the memory/pattern data (what's working, what's failing)
3. Reason about WHY something is underperforming
4. Propose and write a rewritten version of that module
5. Validate its own output before returning it
```

**Example auto-improvement loop:**
```
Scorer detects: "video posts on instagram underperforming last 7 days"
   → R1 reads scorer.py + last 50 post results from memory
   → R1 reasons: "The engagement formula weights saves too low vs
                  comments. Instagram algorithm changed — saves now
                  matter 4x more. Rewriting compute_engagement_score..."
   → R1 outputs updated scoring function
   → Engine tests new function on historical data
   → If score improves → auto-apply patch
   → Memory logs: "scorer updated by R1 on [date], reason: [...]"
```

**Other self-improvement tasks R1 can handle:**
- Rewrite the delay engine when ban risk rises
- Adjust hook-style weights when memory shows shift in platform trends
- Detect and fix broken API integrations automatically
- Propose new pattern types the scorer should track
- Review and improve its own generated captions

---

## Part 3 — Free Cloud APIs

No GPU load — runs on their servers. You call an API.

| API | Model | Free/Day | Speed | No Card | Reasoning |
|---|---|---|---|---|---|
| **Google AI Studio** | Gemini 2.0 Flash | 1,500 req | Very fast | ✅ | Moderate |
| **Google AI Studio** | Gemini 2.5 Flash-Lite | 1,000 req | Fast | ✅ | Good |
| **Groq** | Llama 3.3 70B | 14,400 req | Fastest | ✅ | Good |
| **Groq** | **DeepSeek R1 Distill 70B** | ~1,000 req | Fast | ✅ | **Best** |
| **Groq** | **DeepSeek R1 1.5B** | ~10,000 req | Fastest | ✅ | **Strong** |
| **OpenRouter** | DeepSeek R1 32B | ~200 req | Fast | ✅ | **Excellent** |
| **Cloudflare Workers AI** | Llama, Mistral | 10,000 req | Moderate | ✅ | Basic |

### Cloud API Capability Breakdown

| Capability | Gemini 2.0 Flash | Groq Llama 70B | DS R1 70B (Groq) | DS R1 32B (OR) |
|---|---|---|---|---|
| **Text Generation** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Reasoning / Logic** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Coding / Code rewrite** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Self-correction** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **SEO writing** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Conversation / Reply** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Image understanding** | ✅ Multimodal | ❌ | ❌ | ❌ |
| **Long context** | ✅ 1M tokens | ✅ 128K | ✅ 64K | ✅ 64K |
| **Speed** | Very fast | Fastest | Fast | Fast |

---

## Part 4 — Image Generation Options

| Tool | Type | Cost | VRAM | Quality |
|---|---|---|---|---|
| **Stable Diffusion 1.5** | Local | Free | ~3.5 GB | ⭐⭐⭐ |
| **Stable Diffusion 2.1** | Local | Free | ~3.8 GB | ⭐⭐⭐⭐ |
| **Cloudflare Workers AI** | Cloud free | Free | 0 | ⭐⭐⭐ |
| **Hugging Face (FLUX)** | Cloud free | Free (queued) | 0 | ⭐⭐⭐⭐⭐ |
| **Pollinations.ai** | Cloud free | Free | 0 | ⭐⭐⭐⭐ |

> **Best for 4GB**: SD 1.5 locally + Pollinations.ai or HuggingFace FLUX as free cloud backup.

---

## Part 5 — Final Task Assignment (Updated)

### Complete Hybrid Strategy

```
TASK                          → MODEL                    → WHERE
-----------------------------------------------------------------------
Write captions / scripts      → Gemini 2.0 Flash         Cloud (1500/day)
Reply to comments / DMs       → Groq Llama 70B           Cloud (14400/day)
SEO content / keyword copy    → Gemini 2.0 Flash         Cloud
Risk scoring (fast)           → DeepSeek R1 1.5B (local) Local (~1GB VRAM)
Pattern analysis / decisions  → DeepSeek R1 7B (local)   Local (~4GB VRAM)
CODE SELF-REPAIR / REWRITE    → DeepSeek R1 70B (Groq)   Cloud (free)
Generate images / thumbnails  → SD 1.5                   Local (3.5GB VRAM)
Image fallback                → Pollinations.ai           Cloud (free)
```

> [!IMPORTANT]
> R1 for code rewriting runs **on demand only** (not constantly) — triggered when the scorer detects declining performance or an error. This keeps API quota usage minimal and makes the engine genuinely self-improving without burning free limits.

### API Keys Needed (All Free, No Card)

| Service | Get Key At | Used For |
|---|---|---|
| Gemini | [aistudio.google.com](https://aistudio.google.com) | Writing, SEO, vision |
| Groq | [console.groq.com](https://console.groq.com) | Speed + R1 reasoning |
| OpenRouter | [openrouter.ai](https://openrouter.ai) | Fallback / R1 32B |

---

## AirLLM Note

> [!TIP]
> **AirLLM** runs 70B models on 4GB via layer-sharding (~1–5 tok/sec). Not worth it when Groq gives R1 70B free at full speed. Only use if going fully offline.

---

*Last updated: March 2026 · Hardware: RTX 3060 4GB VRAM · 16GB RAM*
