import os
from pathlib import Path

BASE = Path(__file__).parent
TMPL = (BASE / "template.html").read_text(encoding="utf-8")
OUT = BASE.parent / "chronos-ui" / "public" / "integration"
OUT.mkdir(exist_ok=True, parents=True)

def fill(template, tokens):
    for k, v in tokens.items():
        template = template.replace("{{" + k + "}}", str(v))
    return template

tokens = {
    "PAGE_TITLE": "Supabase Integration: Event Memory & Audit Logs — Smriti",
    "META_DESCRIPTION": "Integrate Smriti with Supabase using BYODB. Create bi-temporal SVO event memory and enterprise audit logs natively inside your Supabase project with zero data lock-in.",
    "SLUG": "integration/supabase-event-memory",
    "H1_HEADLINE": "Supabase Event Memory & <span>Audit Ledgers</span>",
    "HERO_SUBTEXT": "Smriti’s BYODB (Bring Your Own Database) integration lets you extract structured, bi-temporal SVO events and write them directly into your Supabase project. Zero cloud lock-in. 100% native PostgreSQL queries.",
    "PROBLEM_TEXT": "Standard Supabase audit tables create unstructured JSON sludge. Tracking multi-agent state, CRM updates, or strict chronological event sequencing fails because simple row diffs do not support causal querying.",
    "SOLUTION_TEXT": "Smriti sits as a pipeline before your database. You send unstructured text or raw events, Smriti extracts the precise Subject-Verb-Object (SVO) causal structure, and writes a fully indexed, bi-temporal memory timeline natively into your own Supabase.",
    "HOW_IT_WORKS": "Pass your X-Supabase-Url header in the API call. Smriti runs the language extraction model and instantly pipes the structured records into the Supabase pooler URL. You own the data, the schema, and the vectors.",
    "TARGET_NAME": "Supabase Integration",
    "TARGET_SLUG": "supabase",
    "COMPARISON_NAME": "Standard Row Auditing",
    "SEO_H2_1": "Why standard Supabase audit logs break under scale",
    "SEO_PARA_1": "When building an agentic AI app, CRM, or complex operational system, relying on raw Supabase PostgreSQL row-level audit logs becomes unscalable. These logs typically store before/after JSON blobs. If you need to query 'why did this agent change this state?', you are forced to parse unstructured JSON in real-time. Smriti’s SVO extraction resolves this by creating a highly structured, queryable semantic layer on top of your existing Supabase database.",
    "SEO_H2_2": "The Bring Your Own Database (BYODB) Advantage",
    "SEO_PARA_2": "Data privacy and vendor lock-in are the primary roadblocks for enterprise AI adoption. Smriti’s Supabase BYODB feature eliminates this entirely. Because Smriti writes directly to your PostgreSQL database, your users' temporal memory and vector embeddings never reside in our cloud. You retain full HIPAA, SOC2, and GDPR compliance effortlessly by keeping all event data within your own Supabase infrastructure.",
    "SEO_H2_3": "Setting up the Smriti Supabase Integration",
    "SEO_PARA_3": "Setup takes two minutes. First, run the provided Smriti migration script in your Supabase SQL editor to create the necessary bi-temporal tables and pgvector indexes. Second, add the X-Supabase-Url header (using the Session Pooler connection string) to your Smriti API or MCP Server requests. Instantly, all memory ingestion and temporal querying will utilize your database."
}

html = fill(TMPL, tokens)
path = OUT / "supabase-event-memory.html"
path.write_text(html, encoding='utf-8')
print(f"[OK] Generated {path}")
