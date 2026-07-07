"""
Smriti pSEO Page Generator
Generates hundreds of targeted landing pages from data.json + template.html

Usage:
    python generate_pages.py              # generates all pages
    python generate_pages.py --batch 50   # generates first 50 (for staged publishing)
    python generate_pages.py --type framework  # only framework pages
"""
import json, os, re, sys, argparse
from pathlib import Path

BASE   = Path(__file__).parent
DATA   = json.loads((BASE / "data.json").read_text())
TMPL   = (BASE / "template.html").read_text()
OUT    = BASE / "pages"
OUT.mkdir(exist_ok=True)

def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def fill(template, tokens):
    for k, v in tokens.items():
        template = template.replace("{{" + k + "}}", v)
    return template

# ── PAGE TYPES ────────────────────────────────────────────────────────────────

def framework_page(name):
    s = slug(name)
    t = {
        "PAGE_TITLE":       f"{name} Persistent Memory — Smriti",
        "META_DESCRIPTION": f"Add long-term, causal memory to {name} using Smriti's dual pgvector architecture. S-V-O extraction. Cross-session retention. O(1) recall.",
        "SLUG":             f"memory/{s}",
        "H1_HEADLINE":      f"Add Persistent Memory to <span>{name}</span>",
        "HERO_SUBTEXT":     f"Give your {name} agent a brain. Smriti adds long-term, causal memory — retaining context across every session, understanding why events happened, not just what happened.",
        "PROBLEM_TEXT":     f"{name} agents lose all context when a session ends. Every conversation starts from zero. Users repeat themselves, agents forget preferences, and causal connections between events disappear entirely.",
        "SOLUTION_TEXT":    f"Smriti integrates directly with {name} as a drop-in memory layer. It extracts Subject-Verb-Object triples from every interaction, stores them in a dual semantic and episodic pgvector space, and retrieves causal context in O(1) time — across any number of sessions.",
        "HOW_IT_WORKS":     f"{name} calls Smriti's memory API before generating any response. Smriti checks its timeline, retrieves relevant causal context, and passes it as structured memory to the {name} prompt. The agent responds with full awareness of past events — not just the last message.",
        "TARGET_NAME":      name,
        "TARGET_SLUG":      s,
        "COMPARISON_NAME":  "Standard Vector DB",
        "SEO_H2_1":         f"Why {name} needs long-term memory",
        "SEO_PARA_1":       f"{name} is a powerful AI framework but lacks persistent, cross-session memory by default. Each agent run begins with no knowledge of previous interactions. For production applications — customer support, personal assistants, research tools — this is a critical limitation. Smriti solves this by maintaining a chronological memory timeline that persists indefinitely.",
        "SEO_H2_2":         f"How Smriti's S-V-O architecture improves {name} agents",
        "SEO_PARA_2":       f"Unlike simple vector search that retrieves semantically similar text, Smriti extracts the Subject-Verb-Object structure from every stored memory. This means a {name} agent can answer causal questions: not just 'what happened?' but 'why did it happen?' and 'what was the consequence?' This is the difference between a database and a timeline.",
        "SEO_H2_3":         f"Getting started with Smriti and {name}",
        "SEO_PARA_3":       f"Smriti installs as a Python package and integrates with {name} in under 10 lines of code. It requires a PostgreSQL instance with pgvector enabled. Memory is stored in two parallel vector spaces — one for semantic meaning, one for episodic cause-and-effect — giving {name} agents both broad recall and precise causal reasoning.",
    }
    return s, t

def usecase_page(name):
    s = slug(name)
    t = {
        "PAGE_TITLE":       f"{name} with Long-Term Memory — Smriti",
        "META_DESCRIPTION": f"Build a {name} that actually remembers. Smriti adds persistent, causal memory to any AI system — cross-session, encrypted, O(1) retrieval.",
        "SLUG":             f"use-case/{s}",
        "H1_HEADLINE":      f"Build a <span>{name}</span> That Actually Remembers",
        "HERO_SUBTEXT":     f"Most AI-powered {name.lower()} systems forget everything when the session ends. Smriti gives your {name.lower()} a persistent timeline — so it understands context, cause, and consequence.",
        "PROBLEM_TEXT":     f"A {name.lower()} that forgets its users is not intelligent — it is a search engine with a chat interface. Every session reset destroys trust, increases user friction, and makes the system feel broken.",
        "SOLUTION_TEXT":    f"Smriti gives your {name.lower()} a persistent causal memory. Every interaction is stored as a Subject-Verb-Object triple on a chronological timeline. When a user returns after days or weeks, the system remembers not just what happened — but why.",
        "HOW_IT_WORKS":     f"For a {name.lower()}, Smriti stores the full history of every user interaction in a dual pgvector space. When the user asks a question, Smriti retrieves the most causally relevant memories — not just the most recent ones — and passes them to your language model as structured context.",
        "TARGET_NAME":      name,
        "TARGET_SLUG":      s,
        "COMPARISON_NAME":  "Session-Only Memory",
        "SEO_H2_1":         f"Why {name.lower()} AI systems fail without long-term memory",
        "SEO_PARA_1":       f"The majority of {name.lower()} AI systems today rely on in-session context windows. Once the session ends, all memory is lost. Users are forced to repeat their preferences, history, and background every time they interact. This creates frustration and destroys the value of AI personalization.",
        "SEO_H2_2":         f"Smriti's causal memory model for {name.lower()} applications",
        "SEO_PARA_2":       f"Smriti does not simply store and retrieve text. It extracts the causal structure of every interaction — who did what, when, and why — and organises these events on a chronological timeline. For a {name.lower()}, this means the AI can answer questions like 'why did this user's situation change?' with real contextual evidence.",
        "SEO_H2_3":         f"Technical architecture for {name.lower()} memory with Smriti",
        "SEO_PARA_3":       f"Smriti uses a dual pgvector architecture. The semantic space captures meaning and similarity. The episodic space captures temporal ordering and causal relationships. For a {name.lower()}, this means both fuzzy recall ('something about pricing') and precise recall ('the user asked about pricing after their contract expired') are supported simultaneously.",
    }
    return s, t

def problem_page(problem):
    s = slug(problem)
    t = {
        "PAGE_TITLE":       f"Fix: {problem.capitalize()} — Smriti Memory",
        "META_DESCRIPTION": f"Solving the problem: {problem}. Smriti's S-V-O timeline architecture gives AI systems persistent causal memory across sessions.",
        "SLUG":             f"problem/{s}",
        "H1_HEADLINE":      f"Why <span>{problem.capitalize()}</span> — And How to Fix It",
        "HERO_SUBTEXT":     f"This is not a bug in your AI. It is a fundamental architectural gap. Smriti fills it with a persistent causal memory layer built on dual pgvector and S-V-O extraction.",
        "PROBLEM_TEXT":     f"The root cause of '{problem}' is that most AI systems store context in a session-scoped token window — not in a persistent, structured timeline. When the session ends, the context is gone. There is no mechanism for causal recall across time.",
        "SOLUTION_TEXT":    f"Smriti replaces the ephemeral context window with a persistent S-V-O timeline. Every interaction is extracted into a Subject-Verb-Object triple and stored in a dual semantic/episodic pgvector space. Sessions end — memory does not.",
        "HOW_IT_WORKS":     f"When your AI encounters the situation '{problem}', Smriti's memory layer already has the relevant context indexed. It retrieves it in O(1) time and injects it into the prompt as structured causal memory — no session required.",
        "TARGET_NAME":      problem.capitalize(),
        "TARGET_SLUG":      s,
        "COMPARISON_NAME":  "Session Context Window",
        "SEO_H2_1":         f"Root cause: why '{problem}' happens in AI systems",
        "SEO_PARA_1":       f"The problem of '{problem}' is endemic to LLM-based systems that store state in the prompt context window rather than in a persistent external memory store. Context windows have hard token limits, are session-scoped, and provide no mechanism for causal reasoning across time. The result is an AI that cannot remember, cannot reason about the past, and cannot maintain continuity.",
        "SEO_H2_2":         "The S-V-O timeline: a structural solution",
        "SEO_PARA_2":       f"Smriti addresses '{problem}' at the architectural level by replacing the context window as the primary memory store. Instead, every interaction is parsed into a Subject-Verb-Object triple — capturing who did what to whom — and placed on a persistent chronological timeline stored in PostgreSQL with pgvector indexing. This structure enables causal queries that a flat vector store cannot answer.",
        "SEO_H2_3":         "Implementation: integrating Smriti to solve this problem",
        "SEO_PARA_3":       f"Integrating Smriti to fix '{problem}' requires three steps. First, install the Smriti Python package and configure a pgvector-enabled PostgreSQL database. Second, replace your in-session context injection with Smriti's memory.recall() call, which returns causally-relevant context from the full timeline. Third, use memory.store() after every interaction to keep the timeline current. The fix is additive — no existing code needs to be removed.",
    }
    return s, t

# ── GENERATE ──────────────────────────────────────────────────────────────────

def generate_all(page_type=None, batch=None):
    pages = []

    if page_type in (None, 'framework'):
        for name in DATA['frameworks']:
            s, t = framework_page(name)
            pages.append(('framework', s, t))

    if page_type in (None, 'usecase'):
        for name in DATA['use_cases']:
            s, t = usecase_page(name)
            pages.append(('usecase', s, t))

    if page_type in (None, 'problem'):
        for prob in DATA['problems']:
            s, t = problem_page(prob)
            pages.append(('problem', s, t))

    if batch:
        pages = pages[:batch]

    total = 0
    for ptype, s, tokens in pages:
        folder = OUT / ptype
        folder.mkdir(exist_ok=True)
        html = fill(TMPL, tokens)
        path = folder / f"{s}.html"
        path.write_text(html, encoding='utf-8')
        print(f"[OK] {ptype}/{s}.html")
        total += 1

    print(f"\n[DONE] Generated {total} pages -> {OUT}")
    print(f"       Frameworks : {len(DATA['frameworks'])}")
    print(f"       Use cases  : {len(DATA['use_cases'])}")
    print(f"       Problems   : {len(DATA['problems'])}")
    print(f"       TOTAL POSSIBLE : {len(DATA['frameworks'])+len(DATA['use_cases'])+len(DATA['problems'])}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('--batch', type=int, default=None, help='Only generate first N pages')
    ap.add_argument('--type', choices=['framework','usecase','problem'], default=None)
    args = ap.parse_args()
    generate_all(page_type=args.type, batch=args.batch)
