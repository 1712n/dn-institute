import re
from pathlib import Path
from typing import Dict, List


ARTICLE_DIR_CANDIDATES = (
    "content/market-health/posts",
    "content/research/market-health/posts",
)
MAX_EXCERPT_CHARS = 480


def _repo_root() -> Path:
    """
    Resolve repository root from this module path.
    """
    return Path(__file__).resolve().parents[2]


def _discover_article_paths(repo_root: Path) -> List[Path]:
    """
    Discover historical market-health article markdown files.
    """
    article_paths: List[Path] = []
    for rel_dir in ARTICLE_DIR_CANDIDATES:
        base_dir = repo_root / rel_dir
        if not base_dir.exists():
            continue

        for path in sorted(base_dir.rglob("index.md")):
            # Skip section index files directly under the posts root.
            if path.parent == base_dir:
                continue
            article_paths.append(path)

    return article_paths


def _split_front_matter(content: str) -> tuple:
    """
    Split markdown into front matter and body.
    """
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", content, flags=re.DOTALL)
    if not match:
        return "", content
    return match.group(1), match.group(2)


def _extract_title(front_matter: str, fallback_slug: str) -> str:
    """
    Extract title from front matter; fallback to directory slug.
    """
    title_match = re.search(r'^title:\s*"?(.+?)"?\s*$', front_matter, flags=re.MULTILINE)
    if title_match:
        return title_match.group(1).strip()
    return fallback_slug


def _to_plain_text(markdown: str) -> str:
    """
    Convert markdown to lightweight plain text for retrieval.
    """
    text = re.sub(r"\{\{<\s*figure.*?>\}\}", " ", markdown)
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _build_excerpt(markdown_body: str) -> str:
    """
    Build a short excerpt from early narrative paragraphs.
    """
    cleaned_body = re.sub(r"\{\{<\s*figure.*?>\}\}", "", markdown_body)
    paragraphs = [p.strip() for p in cleaned_body.split("\n\n") if p.strip()]
    filtered = [p for p in paragraphs if not p.startswith("{{<")]
    excerpt = " ".join(filtered[:2]) if filtered else cleaned_body.strip()
    excerpt = _to_plain_text(excerpt)

    if len(excerpt) > MAX_EXCERPT_CHARS:
        excerpt = excerpt[: MAX_EXCERPT_CHARS - 3].rsplit(" ", 1)[0] + "..."
    return excerpt


def _normalize_marketvenue(marketvenueid: str) -> str:
    """
    Normalize venue id and enrich common exchange aliases.
    """
    raw = marketvenueid.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", " ", raw).strip()

    aliases = {
        "gateio": "gate io gate.io",
        "okex": "okex okx",
    }

    parts = [raw, normalized]
    if raw in aliases:
        parts.append(aliases[raw])
    if normalized in aliases:
        parts.append(aliases[normalized])

    return " ".join(p for p in parts if p)


def _load_articles(repo_root: Path) -> List[Dict[str, str]]:
    """
    Load historical articles and retrieval fields.
    """
    articles: List[Dict[str, str]] = []
    for path in _discover_article_paths(repo_root):
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            continue

        front_matter, body = _split_front_matter(content)
        slug = path.parent.name
        title = _extract_title(front_matter, slug)
        plain_text = _to_plain_text(body)
        excerpt = _build_excerpt(body)

        articles.append(
            {
                "title": title,
                "slug": slug,
                "path": str(path.relative_to(repo_root)),
                "search_text": f"{slug} {title} {plain_text}",
                "excerpt": excerpt,
            }
        )

    return articles


def get_context(marketvenueid: str, top_k: int = 3) -> str:
    """
    Retrieve context snippets from the most relevant historical market-health articles.
    """
    if not marketvenueid:
        return ""

    repo_root = _repo_root()
    articles = _load_articles(repo_root)
    if not articles:
        return ""

    # Lazy import to avoid changing default behavior if sklearn is unavailable.
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError:
        return ""

    query = _normalize_marketvenue(marketvenueid)
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    doc_matrix = vectorizer.fit_transform([article["search_text"] for article in articles])
    query_vector = vectorizer.transform([query])
    similarity_scores = cosine_similarity(query_vector, doc_matrix).flatten()

    ranked_indices = sorted(
        range(len(articles)),
        key=lambda idx: similarity_scores[idx],
        reverse=True,
    )

    max_items = min(top_k, len(articles))
    selected_indices: List[int] = []
    for idx in ranked_indices:
        if len(selected_indices) >= max_items:
            break
        if similarity_scores[idx] <= 0 and len(selected_indices) >= 2:
            break
        selected_indices.append(idx)

    if not selected_indices:
        return ""
    if len(selected_indices) == 1 and len(ranked_indices) > 1:
        selected_indices = ranked_indices[:2]

    lines = [
        "Historical context from previous dn-institute market-health investigations (TF-IDF retrieved):",
        "Use this as comparative background only; prioritize current-period evidence and avoid copying prior wording.",
    ]

    for rank, idx in enumerate(selected_indices, start=1):
        article = articles[idx]
        score = similarity_scores[idx]
        lines.append(
            f"{rank}. {article['title']} ({article['path']}; relevance={score:.3f})"
        )
        lines.append(f"Excerpt: {article['excerpt']}")

    return "\n".join(lines)
