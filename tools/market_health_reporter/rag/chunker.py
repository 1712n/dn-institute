"""
Text chunking utilities for the RAG pipeline.

Splits article text into overlapping chunks suitable for embedding and
semantic retrieval.  Uses a simple sliding-window approach over sentences
to preserve context across chunk boundaries.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    """A chunk of text with its source metadata."""
    text: str
    source_url: str
    source_title: str
    chunk_index: int


# Approximate sentence boundary pattern
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")

# Default chunk parameters (in characters, not tokens)
DEFAULT_CHUNK_SIZE = 1500
DEFAULT_CHUNK_OVERLAP = 200


def chunk_text(
    text: str,
    source_url: str = "",
    source_title: str = "",
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[TextChunk]:
    """
    Split text into overlapping chunks, respecting sentence boundaries.

    Args:
        text: The full article text to chunk.
        source_url: URL of the source article (stored in metadata).
        source_title: Title of the source article.
        chunk_size: Target chunk size in characters.
        chunk_overlap: Overlap between consecutive chunks in characters.

    Returns:
        List of TextChunk objects.
    """
    if not text or len(text.strip()) < 50:
        return []

    sentences = _SENTENCE_SPLIT.split(text.strip())
    if not sentences:
        return []

    chunks: list[TextChunk] = []
    current_chunk: list[str] = []
    current_len = 0
    chunk_idx = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        sent_len = len(sentence)

        if current_len + sent_len > chunk_size and current_chunk:
            # Emit current chunk
            chunk_text_str = " ".join(current_chunk)
            chunks.append(TextChunk(
                text=chunk_text_str,
                source_url=source_url,
                source_title=source_title,
                chunk_index=chunk_idx,
            ))
            chunk_idx += 1

            # Keep overlap: walk backwards to find sentences within overlap window
            overlap_len = 0
            overlap_start = len(current_chunk)
            for i in range(len(current_chunk) - 1, -1, -1):
                overlap_len += len(current_chunk[i])
                if overlap_len >= chunk_overlap:
                    overlap_start = i
                    break
            current_chunk = current_chunk[overlap_start:]
            current_len = sum(len(s) for s in current_chunk)

        current_chunk.append(sentence)
        current_len += sent_len

    # Emit final chunk
    if current_chunk:
        chunk_text_str = " ".join(current_chunk)
        if len(chunk_text_str.strip()) > 50:
            chunks.append(TextChunk(
                text=chunk_text_str,
                source_url=source_url,
                source_title=source_title,
                chunk_index=chunk_idx,
            ))

    return chunks
