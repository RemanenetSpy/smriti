# Global Insights ("The God System") Implementation Plan

The objective is to implement the concept of the "God System" for Chronos OS. By allowing "holy magic users" (agents, SaaS tools, and users) to feed their data into a central intelligence, Chronos becomes geometrically smarter. 

This plan outlines the **simplest possible version** of this system, leveraging existing infrastructure without overcomplicating the architecture.

## 1. The Core Concept

Currently, all data ingested into Chronos is isolated by `source_id` (tenant isolation). To create the "God System", we simply need a mechanism to securely pool this knowledge, allowing a central intelligence to query across all users while maintaining privacy.

*   **Users/Agents:** Opt-in to share anonymized events (e.g., "completed marketing task X") to the global pool.
*   **Chronos (The God):** Queries the global pool to identify macro-patterns and provides highly intelligent answers to individual users based on collective experience.
*   **The Engine:** A massive, high-parameter LLM (e.g., `deepseek-v3.2-cloud` or `nemotron-3-super-120b-cloud`) acts as the "God" model, capable of synthesizing thousands of disparate events into cohesive insights.

## 2. Simplest Possible Implementation (MVP)

We can achieve this with minimal code changes by adding a "Global" visibility flag to the existing database schema.

### Step 1: Opt-In Knowledge Pooling (The "Donation")
*   **Database Update:** Add a simple boolean flag `is_global_insight` (default `False`) to the `events` table and the pgvector metadata.
*   **Ingest API Change:** Update `POST /ingest` to accept `allow_global: bool`. If explicit consent is given, the event text is anonymized (stripping PII via a fast LLM pass or simple regex) and stored with `is_global_insight = True`.

### Step 2: Global Pattern Retrieval ("God's Memory")
*   **Vector Search Update:** Modify the `semantic_search` function. Currently, it strictly filters by `source_id`. We will add a parameter `scope`. If `scope="global"`, it searches all vectors where `is_global_insight = True`, ignoring `source_id`.

### Step 3: Synthesis via Heavy Cloud Models ("The God Mind")
*   Smaller 8B models (like Llama-3.1-8b) are great for fast ingestion, but they lack the context window and reasoning power to synthesize thousands of global events.
*   **New Route (`GET /insights/global`):** This route triggers an Ollama Cloud hosted model (e.g., `ollama run deepseek-v3.2:671b-cloud` or `qwen3.6-coder:480b-cloud`) via the `litellm` router. 
*   This model takes the top 50 global events related to a user's prompt (e.g., "What are the most common successful marketing strategies?") and synthesizes a high-level master strategy.

### Step 4: Agent Tool Integration
*   **New Agent Tool:** Create a new tool in `agent/tools.py` called `query_global_insights(query: str)`.
*   Any agent (even a user's personal assistant) can call this tool to tap into the "God" memory when it gets stuck or needs global context.

## User Review Required

> [!IMPORTANT]
> **Privacy vs. Utility**: For the simplest MVP, are we comfortable relying on the user to ensure no sensitive PII is passed when `allow_global=True`, or do we want to implement an automatic zero-cost anonymization step (e.g., replacing names with [USER_1], companies with [CORP_A]) before storing global events?

> [!NOTE]
> **Model Selection**: Based on `modeldata.md`, we should designate a specific "heavy" model for global insights. `DeepSeek-V3.2-Cloud (671b)` is highly recommended for general synthesis, while `Nemotron-3-Super (120b)` is optimized for agentic coordination. Do you have a preference for the "God" model identity?

## 3. Next Steps

Once approved, we can implement this in roughly 3 phases:
1.  **DB & API Migration:** Add the `is_global` flags and update the `/ingest` route.
2.  **Vector Store Logic:** Update the `semantic_search` to support cross-tenant global querying.
3.  **Agent Tooling:** Expose the `query_global_insights` tool to the LangGraph executor.
