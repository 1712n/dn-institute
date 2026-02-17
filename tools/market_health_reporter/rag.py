"""
RAG (Retrieval-Augmented Generation) module for the Market Health Reporter.

This module provides functionality to:
1. Collect and chunk past market health reports and metric documentation
2. Generate embeddings for document chunks using OpenAI's embeddings API
3. Build an in-memory vector store for similarity search
4. Retrieve relevant context to augment LLM prompts for report generation

The RAG pipeline improves report quality by grounding generated content
in historical analysis patterns, metric interpretations, and established
reporting conventions from the existing corpus of market health articles.
"""

import os
import json
import hashlib
import numpy as np
import openai
from typing import Optional


# Directories containing source documents for the RAG corpus
REPORTS_DIR = "content/research/market-health/posts"
DOCS_DIR = "content/research/market-health/docs"

# Embedding model configuration
EMBEDDING_MODEL = "text-embedding-ada-002"
EMBEDDING_DIMENSION = 1536

# Chunking parameters
MAX_CHUNK_SIZE = 1000  # approximate max characters per chunk
CHUNK_OVERLAP = 200    # character overlap between chunks

# Retrieval parameters
DEFAULT_TOP_K = 3
SIMILARITY_THRESHOLD = 0.5

# Cache directory for persisted embeddings
CACHE_DIR = "tools/market_health_reporter/doc/data/rag_cache"


def collect_documents(reports_dir: str = REPORTS_DIR, docs_dir: str = DOCS_DIR) -> list[dict]:
    """
    Collect markdown documents from past reports and metric documentation.

    Scans the reports and docs directories for .md files, reads their content,
    and returns a list of document dictionaries with metadata.

    Args:
        reports_dir: Path to the directory containing past report posts.
        docs_dir: Path to the directory containing metric documentation.

    Returns:
        A list of dicts, each containing 'text', 'source', and 'doc_type' keys.
    """
    documents = []

    # Collect past reports
    if os.path.isdir(reports_dir):
        for entry in sorted(os.listdir(reports_dir)):
            entry_path = os.path.join(reports_dir, entry)
            if os.path.isdir(entry_path):
                index_file = os.path.join(entry_path, "index.md")
                if os.path.isfile(index_file):
                    with open(index_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    documents.append({
                        "text": content,
                        "source": index_file,
                        "doc_type": "past_report",
                    })

    # Collect metric documentation
    if os.path.isdir(docs_dir):
        for entry in sorted(os.listdir(docs_dir)):
            entry_path = os.path.join(docs_dir, entry)
            # Check for index.md inside subdirectories
            if os.path.isdir(entry_path):
                index_file = os.path.join(entry_path, "index.md")
                if os.path.isfile(index_file):
                    with open(index_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    documents.append({
                        "text": content,
                        "source": index_file,
                        "doc_type": "metric_documentation",
                    })
            # Check for standalone .md files (excluding _index.md)
            elif entry.endswith(".md") and not entry.startswith("_"):
                with open(entry_path, "r", encoding="utf-8") as f:
                    content = f.read()
                documents.append({
                    "text": content,
                    "source": entry_path,
                    "doc_type": "metric_documentation",
                })

    return documents


def chunk_text(text: str, max_size: int = MAX_CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Split text into overlapping chunks based on section boundaries.

    The chunking strategy prioritizes splitting at markdown section headers (##),
    then paragraph boundaries, falling back to character-level splits when
    sections exceed the maximum chunk size.

    Args:
        text: The full text to split into chunks.
        max_size: Maximum number of characters per chunk.
        overlap: Number of characters to overlap between consecutive chunks.

    Returns:
        A list of text chunks.
    """
    # Remove frontmatter (content between --- delimiters)
    if text.startswith("---"):
        end_idx = text.find("---", 3)
        if end_idx != -1:
            text = text[end_idx + 3:].strip()

    chunks = []

    # First, try to split by markdown sections (## headers)
    sections = []
    current_section = ""
    for line in text.split("\n"):
        if line.startswith("## ") and current_section.strip():
            sections.append(current_section.strip())
            current_section = line + "\n"
        else:
            current_section += line + "\n"
    if current_section.strip():
        sections.append(current_section.strip())

    # Process each section
    for section in sections:
        if len(section) <= max_size:
            chunks.append(section)
        else:
            # Split large sections by paragraphs
            paragraphs = section.split("\n\n")
            current_chunk = ""
            for paragraph in paragraphs:
                if len(current_chunk) + len(paragraph) + 2 <= max_size:
                    current_chunk += paragraph + "\n\n"
                else:
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                    # If a single paragraph is too large, split by characters
                    if len(paragraph) > max_size:
                        start = 0
                        while start < len(paragraph):
                            end = min(start + max_size, len(paragraph))
                            chunks.append(paragraph[start:end].strip())
                            start = end - overlap
                    else:
                        current_chunk = paragraph + "\n\n"
            if current_chunk.strip():
                chunks.append(current_chunk.strip())

    # Filter out empty or trivially small chunks
    chunks = [c for c in chunks if len(c.strip()) > 50]

    return chunks


def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    Split a list of documents into chunks, preserving metadata.

    Each document is chunked using chunk_text(), and the resulting chunks
    inherit the source and doc_type metadata from the parent document.

    Args:
        documents: List of document dicts with 'text', 'source', 'doc_type'.

    Returns:
        A list of chunk dicts with 'text', 'source', 'doc_type', and 'chunk_index'.
    """
    all_chunks = []
    for doc in documents:
        text_chunks = chunk_text(doc["text"])
        for i, chunk in enumerate(text_chunks):
            all_chunks.append({
                "text": chunk,
                "source": doc["source"],
                "doc_type": doc["doc_type"],
                "chunk_index": i,
            })
    return all_chunks


def _compute_corpus_hash(chunks: list[dict]) -> str:
    """
    Compute a hash of the corpus content for cache invalidation.

    Args:
        chunks: List of chunk dicts.

    Returns:
        A hex digest string representing the corpus content hash.
    """
    hasher = hashlib.sha256()
    for chunk in chunks:
        hasher.update(chunk["text"].encode("utf-8"))
    return hasher.hexdigest()


def generate_embeddings(texts: list[str], api_key: str) -> np.ndarray:
    """
    Generate embeddings for a list of texts using the OpenAI embeddings API.

    Args:
        texts: A list of text strings to embed.
        api_key: The OpenAI API key.

    Returns:
        A numpy array of shape (len(texts), EMBEDDING_DIMENSION).
    """
    openai.api_key = api_key

    # Process in batches to respect API limits
    batch_size = 100
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = openai.Embedding.create(
            model=EMBEDDING_MODEL,
            input=batch,
        )
        batch_embeddings = [item["embedding"] for item in response["data"]]
        all_embeddings.extend(batch_embeddings)

    return np.array(all_embeddings, dtype=np.float32)


def cosine_similarity(query_embedding: np.ndarray, corpus_embeddings: np.ndarray) -> np.ndarray:
    """
    Compute cosine similarity between a query embedding and a corpus of embeddings.

    Args:
        query_embedding: A 1D numpy array of the query embedding.
        corpus_embeddings: A 2D numpy array of corpus embeddings (n_docs x dim).

    Returns:
        A 1D numpy array of cosine similarity scores.
    """
    # Normalize query
    query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-10)
    # Normalize corpus
    corpus_norms = np.linalg.norm(corpus_embeddings, axis=1, keepdims=True) + 1e-10
    corpus_normalized = corpus_embeddings / corpus_norms
    # Dot product gives cosine similarity when vectors are normalized
    return np.dot(corpus_normalized, query_norm)


class VectorStore:
    """
    In-memory vector store for document chunks and their embeddings.

    Provides methods to build the store from document chunks, persist to disk
    for caching, and perform similarity search for retrieval.

    Attributes:
        chunks: List of chunk dicts with text and metadata.
        embeddings: Numpy array of embeddings for each chunk.
        corpus_hash: Hash of the corpus for cache invalidation.
    """

    def __init__(self):
        self.chunks: list[dict] = []
        self.embeddings: Optional[np.ndarray] = None
        self.corpus_hash: str = ""

    def build(self, chunks: list[dict], api_key: str, cache_dir: str = CACHE_DIR) -> None:
        """
        Build the vector store from document chunks.

        Generates embeddings for all chunks, or loads from cache if the
        corpus hasn't changed since the last build.

        Args:
            chunks: List of chunk dicts with 'text' and metadata.
            api_key: OpenAI API key for embedding generation.
            cache_dir: Directory for persisting the embedding cache.
        """
        self.chunks = chunks
        self.corpus_hash = _compute_corpus_hash(chunks)

        # Try to load from cache
        if self._load_cache(cache_dir):
            print(f"RAG: Loaded {len(self.chunks)} chunk embeddings from cache.")
            return

        # Generate embeddings
        texts = [chunk["text"] for chunk in chunks]
        print(f"RAG: Generating embeddings for {len(texts)} chunks...")
        self.embeddings = generate_embeddings(texts, api_key)
        print(f"RAG: Generated embeddings with shape {self.embeddings.shape}.")

        # Save to cache
        self._save_cache(cache_dir)

    def _save_cache(self, cache_dir: str) -> None:
        """
        Persist embeddings and metadata to disk for future reuse.

        Args:
            cache_dir: Directory to store cache files.
        """
        os.makedirs(cache_dir, exist_ok=True)
        cache_meta = {
            "corpus_hash": self.corpus_hash,
            "chunks": [
                {
                    "source": c["source"],
                    "doc_type": c["doc_type"],
                    "chunk_index": c["chunk_index"],
                }
                for c in self.chunks
            ],
        }
        with open(os.path.join(cache_dir, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(cache_meta, f)
        np.save(os.path.join(cache_dir, "embeddings.npy"), self.embeddings)
        print(f"RAG: Saved embedding cache to {cache_dir}.")

    def _load_cache(self, cache_dir: str) -> bool:
        """
        Attempt to load cached embeddings if the corpus hash matches.

        Args:
            cache_dir: Directory containing cache files.

        Returns:
            True if cache was loaded successfully, False otherwise.
        """
        meta_path = os.path.join(cache_dir, "meta.json")
        embeddings_path = os.path.join(cache_dir, "embeddings.npy")

        if not os.path.isfile(meta_path) or not os.path.isfile(embeddings_path):
            return False

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                cache_meta = json.load(f)

            if cache_meta.get("corpus_hash") != self.corpus_hash:
                print("RAG: Corpus has changed, rebuilding embeddings.")
                return False

            self.embeddings = np.load(embeddings_path)

            if self.embeddings.shape[0] != len(self.chunks):
                print("RAG: Cache size mismatch, rebuilding embeddings.")
                return False

            return True
        except (json.JSONDecodeError, ValueError, OSError) as e:
            print(f"RAG: Cache load failed ({e}), rebuilding embeddings.")
            return False

    def search(self, query: str, api_key: str, top_k: int = DEFAULT_TOP_K,
               threshold: float = SIMILARITY_THRESHOLD) -> list[dict]:
        """
        Search for chunks most similar to the query.

        Generates an embedding for the query text and computes cosine similarity
        against all stored chunk embeddings to find the most relevant ones.

        Args:
            query: The query text to search for.
            api_key: OpenAI API key for embedding the query.
            top_k: Number of top results to return.
            threshold: Minimum cosine similarity score to include a result.

        Returns:
            A list of dicts, each with 'text', 'source', 'doc_type', 'score'.
        """
        if self.embeddings is None or len(self.chunks) == 0:
            print("RAG: Vector store is empty, no results to return.")
            return []

        # Generate query embedding
        query_embedding = generate_embeddings([query], api_key)[0]

        # Compute similarities
        similarities = cosine_similarity(query_embedding, self.embeddings)

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score >= threshold:
                results.append({
                    "text": self.chunks[idx]["text"],
                    "source": self.chunks[idx]["source"],
                    "doc_type": self.chunks[idx]["doc_type"],
                    "score": score,
                })

        return results


def build_rag_context(query: str, api_key: str, top_k: int = DEFAULT_TOP_K,
                      reports_dir: str = REPORTS_DIR, docs_dir: str = DOCS_DIR) -> str:
    """
    Build RAG context by retrieving relevant past reports and documentation.

    This is the main entry point for the RAG pipeline. It collects documents,
    chunks them, builds a vector store, and retrieves the most relevant chunks
    for the given query.

    Args:
        query: The query text describing what context is needed (typically
               derived from the market data and analysis parameters).
        api_key: OpenAI API key for embeddings.
        top_k: Number of top relevant chunks to retrieve.
        reports_dir: Path to past report posts directory.
        docs_dir: Path to metric documentation directory.

    Returns:
        A formatted string of retrieved context, ready to be inserted into
        the LLM prompt.
    """
    # Step 1: Collect documents
    documents = collect_documents(reports_dir, docs_dir)
    if not documents:
        print("RAG: No documents found for the RAG corpus.")
        return ""

    print(f"RAG: Collected {len(documents)} documents from the corpus.")

    # Step 2: Chunk documents
    chunks = chunk_documents(documents)
    print(f"RAG: Created {len(chunks)} chunks from {len(documents)} documents.")

    # Step 3: Build vector store
    store = VectorStore()
    store.build(chunks, api_key)

    # Step 4: Search for relevant context
    results = store.search(query, api_key, top_k=top_k)
    print(f"RAG: Retrieved {len(results)} relevant chunks.")

    if not results:
        return ""

    # Step 5: Format retrieved context
    context_parts = []
    for i, result in enumerate(results, 1):
        source_label = os.path.basename(os.path.dirname(result["source"]))
        context_parts.append(
            f"--- Retrieved Context {i} (source: {source_label}, "
            f"type: {result['doc_type']}, relevance: {result['score']:.3f}) ---\n"
            f"{result['text']}"
        )

    context_str = "\n\n".join(context_parts)
    return context_str


def build_rag_query(marketvenueid: str, pairid: str, data: dict) -> str:
    """
    Build a search query for RAG retrieval from the analysis parameters.

    Constructs a descriptive query that captures the key aspects of the
    current analysis, enabling effective similarity search against the
    corpus of past reports and documentation.

    Args:
        marketvenueid: The market venue identifier (e.g., 'huobi', 'binance').
        pairid: The trading pair identifier (e.g., 'btc-usdt').
        data: The market data dict from the API response.

    Returns:
        A query string for similarity search.
    """
    # Extract key metric names present in the data for a targeted query
    metric_keywords = []
    sample_record = data[0] if isinstance(data, list) and len(data) > 0 else {}

    metric_map = {
        "vvcorrelation": "volume-volatility correlation",
        "firstdigitdist": "first-digit distribution Benford's law",
        "benfordlawtest": "Kolmogorov-Smirnov test Benford's law",
        "volumedist": "volume distribution power law",
        "timeoftrade": "time-of-trade distribution bot activity",
        "buysellratio": "buy-sell ratio market sentiment",
        "buysellratioabs": "buy-sell ratio absolute volume",
        "vwap": "VWAP volume weighted average price",
    }

    for key, description in metric_map.items():
        if key in sample_record:
            metric_keywords.append(description)

    metrics_str = ", ".join(metric_keywords) if metric_keywords else "market health metrics"

    query = (
        f"Market health analysis for {pairid} on {marketvenueid} exchange. "
        f"Analysis of {metrics_str}. "
        f"Detecting wash trading, market manipulation, anomalous trading patterns, "
        f"and suspicious activity on cryptocurrency exchanges."
    )

    return query
