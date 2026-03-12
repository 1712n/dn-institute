"""
rag_context.py — RAG context retrieval for Market Health Reporter 🌰

Fetches relevant articles from the dn-institute knowledge base to provide
contextual grounding for report generation. Uses the dn-institute GitHub
repository (market-health posts) as the knowledge base.

This improves report quality by giving the LLM examples of well-structured
analysis articles that follow the dn-institute contribution guidelines.
"""
import json
import re
import requests
from typing import List, Optional


GITHUB_RAW_BASE = "https://raw.githubusercontent.com/1712n/dn-institute/main"
GITHUB_API_BASE = "https://api.github.com"
MARKET_HEALTH_POSTS_PATH = "content/research/market-health/posts"
REPO = "1712n/dn-institute"

# 🌰 Maximum characters to use for RAG context (leave room for data + prompts)
MAX_CONTEXT_CHARS = 8000
MAX_ARTICLES = 3

# Common exchange alias mapping (normalised_key -> list of known names)
_VENUE_ALIASES: dict = {
    "huobi": ["huobi", "htx"],
    "htx": ["htx", "huobi"],
    "okx": ["okx", "okex"],
    "okex": ["okex", "okx"],
    "gateio": ["gateio", "gate-io", "gate.io"],
    "gate": ["gate", "gateio", "gate-io"],
    "kucoin": ["kucoin", "ku coin"],
    "binance": ["binance"],
    "coinbase": ["coinbase", "coinbase pro"],
}


def _normalise(s: str) -> str:
    """Lowercase and strip common separators for fuzzy matching."""
    return re.sub(r"[-_.\s]", "", s.lower())


def _venue_names(marketvenueid: str) -> List[str]:
    """Return all known aliases for a venue id (normalised)."""
    key = _normalise(marketvenueid)
    aliases = _VENUE_ALIASES.get(key, [marketvenueid])
    return [_normalise(a) for a in aliases]


def _pair_tokens(pairid: str) -> List[str]:
    """Split a pair id like 'btcusdt' or 'btc-usdt' into base tokens."""
    normalised = _normalise(pairid)
    # Try to split common quote currencies
    for quote in ["usdt", "usdc", "busd", "btc", "eth", "usd"]:
        if normalised.endswith(quote) and len(normalised) > len(quote):
            base = normalised[: -len(quote)]
            return [base, quote, normalised]
    return [normalised]


def _fetch_raw(path: str, github_token: Optional[str] = None) -> Optional[str]:
    """Fetch raw file content from dn-institute GitHub repo."""
    url = f"{GITHUB_RAW_BASE}/{path}"
    headers: dict = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            return resp.text
    except requests.RequestException:
        pass
    return None


def _list_market_health_posts(github_token: Optional[str] = None) -> List[str]:
    """List all market-health post directories via GitHub API."""
    url = f"{GITHUB_API_BASE}/repos/{REPO}/contents/{MARKET_HEALTH_POSTS_PATH}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            try:
                items = resp.json()
                return [
                    item["name"] for item in items
                    if item["type"] == "dir" and item["name"] != "_index"
                ]
            except (ValueError, KeyError):
                pass
    except requests.RequestException:
        pass
    return []


def _score_article_relevance(
    article_name: str,
    content: str,
    marketvenueid: str,
    pairid: str,
) -> int:
    """
    Score how relevant an article is to the target exchange and pair.

    Rules:
    - Articles with NO venue/pair signal score 0 (will be excluded later).
    - Year recency is used ONLY as a tie-breaker, not to promote unrelated articles.
    """
    venue_aliases = _venue_names(marketvenueid)
    pair_tokens = _pair_tokens(pairid)
    name_lower = _normalise(article_name)
    content_lower = _normalise(content) if content else ""

    venue_hit = False
    pair_hit = False
    score = 0

    # Venue matching (name in directory OR content)
    for alias in venue_aliases:
        if alias in name_lower:
            score += 10
            venue_hit = True
        if alias in content_lower:
            score += 5
            venue_hit = True

    # Pair matching (any token in content)
    for token in pair_tokens:
        if token in content_lower:
            score += 3
            pair_hit = True

    # Only add recency bonus if the article is actually relevant
    if venue_hit or pair_hit:
        year_match = re.search(r"(\d{4})", article_name)
        if year_match:
            year = int(year_match.group(1))
            score += max(0, year - 2020)  # Newer = slightly higher score, tie-breaker only

    return score


def _extract_article_body(content: str) -> str:
    """
    Extract the body of a Hugo markdown article, stripping YAML front matter.

    Handles both LF and CRLF line endings.
    """
    # Match front matter anchored to the start of the file
    match = re.match(r"^---\r?\n.*?\r?\n---\r?\n(.*)", content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return content.strip()


def fetch_rag_context(
    marketvenueid: str,
    pairid: str,
    github_token: Optional[str] = None,
) -> str:
    """
    Fetch RAG context articles relevant to the target exchange and trading pair.

    Returns a formatted string with relevant article excerpts to inject into
    the LLM prompt as additional context. Returns empty string on any failure
    or when no relevant articles are found.

    🌰 Uses dn-institute's own market-health knowledge base for grounding.
    """
    print(f"[RAG] Fetching context for exchange={marketvenueid}, pair={pairid}")

    # 1. List available market-health posts
    post_dirs = _list_market_health_posts(github_token)
    if not post_dirs:
        print("[RAG] Could not fetch article list, skipping RAG context")
        return ""

    # 2. Score each article for relevance
    scored_articles = []
    for post_dir in post_dirs:
        path = f"{MARKET_HEALTH_POSTS_PATH}/{post_dir}/index.md"
        content = _fetch_raw(path, github_token)
        if content:
            score = _score_article_relevance(post_dir, content, marketvenueid, pairid)
            if score > 0:  # Only keep articles with at least one relevance signal
                scored_articles.append((score, post_dir, content))

    if not scored_articles:
        print("[RAG] No relevant articles found, skipping RAG context")
        return ""

    # 3. Sort by relevance, take top N
    scored_articles.sort(key=lambda x: x[0], reverse=True)
    top_articles = scored_articles[:MAX_ARTICLES]
    print(f"[RAG] Found {len(scored_articles)} relevant articles, using top {len(top_articles)}")
    for score, name, _ in top_articles:
        print(f"[RAG]   {name} (score={score})")

    # 4. Build context string, respecting character limit
    context_parts: List[str] = []
    total_chars = 0

    for _score, post_dir, content in top_articles:
        article_body = _extract_article_body(content)
        header = f"### Reference Article: {post_dir}\n"
        separator = "\n\n"

        # Account for header, separator, and leave 200 char buffer
        overhead = len(header) + len(separator)
        remaining = MAX_CONTEXT_CHARS - total_chars - overhead - 200
        if remaining <= 0:
            break

        excerpt = article_body[:remaining]
        chunk = header + excerpt
        context_parts.append(chunk)
        total_chars += len(chunk) + len(separator)

    if not context_parts:
        return ""

    context = "\n\n".join(context_parts)
    print(f"[RAG] Context prepared: {len(context)} chars from {len(context_parts)} articles")
    return context


def build_rag_enhanced_prompt(
    article_example: str,
    data: dict,
    human_prompt_content: str,
    rag_context: str,
) -> str:
    """
    Build the LLM prompt with RAG context injected.

    Adds retrieved articles between the example and the data, so the LLM
    can use them as style/structure reference alongside the primary example.
    Falls back to the original prompt format when rag_context is empty. 🌰
    """
    if rag_context:
        return (
            f"<example> {article_example} </example>\n"
            f"<additional_context>\n"
            f"The following are additional reference articles from the dn-institute "
            f"market surveillance knowledge base. Use them to match the writing style, "
            f"structure, and analytical depth expected in the final report:\n\n"
            f"{rag_context}\n"
            f"</additional_context>\n"
            f"{human_prompt_content}\n"
            f"<data> {json.dumps(data)} </data>"
        )
    else:
        # Fallback: same as original prompt without RAG
        return (
            f"<example> {article_example} </example>\n"
            f"{human_prompt_content}\n"
            f"<data> {json.dumps(data)} </data>"
        )
