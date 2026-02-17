"""
🌰 RAG Retriever for Market Health Reporter 🌰

Retrieves relevant external context (wiki articles, news, regulatory info)
to enrich the Market Health Reporter's article generation prompt.
"""

import os
import glob
import re
from duckduckgo_search import DDGS
from tools.python_modules.utils import read_file


# 🌰 Paths to existing wiki content for local RAG retrieval
WIKI_MARKET_HEALTH_DIR = "content/research/market-health/posts/"
WIKI_ATTACKS_DIR = "content/attacks/posts/"

# 🌰 Maximum context tokens to inject
MAX_RAG_CONTEXT_CHARS = 8000


def retrieve_wiki_context(exchange_name: str) -> str:
    """
    🌰 Retrieve relevant context from existing wiki articles in the repository.
    Searches both market-health and attacks directories for articles mentioning
    the target exchange.
    """
    relevant_chunks = []

    for wiki_dir in [WIKI_MARKET_HEALTH_DIR, WIKI_ATTACKS_DIR]:
        if not os.path.isdir(wiki_dir):
            continue
        for md_path in glob.glob(os.path.join(wiki_dir, "**", "*.md"), recursive=True):
            try:
                content = read_file(md_path)
            except Exception:
                continue
            if exchange_name.lower() in content.lower():
                # Extract summary section if present
                summary = _extract_section(content, "Summary")
                if summary:
                    relevant_chunks.append(
                        f"[Wiki: {os.path.basename(os.path.dirname(md_path))}]\n{summary}"
                    )
                elif len(content) < 2000:
                    relevant_chunks.append(
                        f"[Wiki: {os.path.basename(os.path.dirname(md_path))}]\n{content[:1500]}"
                    )

    return "\n\n".join(relevant_chunks)


def retrieve_web_context(exchange_name: str, pair: str) -> str:
    """
    🌰 Search the web for relevant news, regulatory actions, and analysis
    about the target exchange and trading pair using DuckDuckGo.
    """
    queries = [
        f"{exchange_name} wash trading manipulation",
        f"{exchange_name} {pair} regulatory action SEC CFTC",
        f"{exchange_name} trading volume suspicious",
    ]

    results_text = []
    with DDGS() as ddgs:
        for query in queries:
            try:
                results = list(ddgs.text(query, max_results=3))
                for r in results:
                    snippet = f"[{r.get('title', '')}] {r.get('body', '')}"
                    if snippet not in results_text:
                        results_text.append(snippet)
            except Exception:
                continue

    return "\n\n".join(results_text)


def retrieve_context(exchange_name: str, pair: str) -> str:
    """
    🌰 Main RAG retrieval function. Combines wiki and web context,
    truncated to fit within token budget.
    """
    wiki_ctx = retrieve_wiki_context(exchange_name)
    web_ctx = retrieve_web_context(exchange_name, pair)

    combined = ""
    if wiki_ctx:
        combined += f"## Existing Wiki Context 🌰\n{wiki_ctx}\n\n"
    if web_ctx:
        combined += f"## External Sources 🌰\n{web_ctx}\n\n"

    # Truncate to budget
    if len(combined) > MAX_RAG_CONTEXT_CHARS:
        combined = combined[:MAX_RAG_CONTEXT_CHARS] + "\n[...truncated]"

    return combined


def _extract_section(content: str, section_name: str) -> str:
    """Extract content under a markdown heading."""
    pattern = rf"##\s+{re.escape(section_name)}\s*\n(.*?)(?=\n##\s|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    return match.group(1).strip() if match else ""
