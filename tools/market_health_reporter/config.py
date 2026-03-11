# RAG configuration for Market Health Reporter

# Maximum number of articles to fetch per source
MAX_ARTICLES_PER_SOURCE = 5

# Maximum number of top relevant articles to include in RAG context
RAG_TOP_K = 3

# Maximum tokens reserved for RAG context within the prompt
RAG_MAX_CONTEXT_TOKENS = 8000

# Maximum characters to extract from each article body
ARTICLE_MAX_CHARS = 2000

# Keywords always included in retrieval scoring
DEFAULT_KEYWORDS = ["market", "trading", "volume", "liquidity", "exchange", "crypto"]
