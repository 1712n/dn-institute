"""
Article text extraction and cleaning.

Downloads article HTML and extracts the main textual content, stripping
navigation, ads, scripts, and boilerplate.
"""

from __future__ import annotations

import logging
import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_HTTP_TIMEOUT = 10
_MAX_CONTENT_CHARS = 10_000

_USER_AGENT = (
    "Mozilla/5.0 (compatible; MarketHealthReporter/1.0; "
    "+https://github.com/1712n/dn-institute)"
)

# Tags that typically contain article body text
_CONTENT_TAGS = ["article", "main", "[role='main']"]

# Tags to remove before text extraction
_REMOVE_TAGS = [
    "script", "style", "nav", "header", "footer", "aside",
    "iframe", "noscript", "svg", "form", "button",
]


def extract_article_text(url: str) -> Optional[str]:
    """
    Fetch a URL and return cleaned plain-text article content.

    Returns None if fetch or extraction fails.
    """
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": _USER_AGENT},
            timeout=_HTTP_TIMEOUT,
            allow_redirects=True,
        )
        resp.raise_for_status()

        # Only process HTML responses
        content_type = resp.headers.get("Content-Type", "")
        if "html" not in content_type.lower():
            return None

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove noise tags
        for tag_name in _REMOVE_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        # Try to find the main content container
        content = None
        for selector in _CONTENT_TAGS:
            if selector.startswith("["):
                content = soup.select_one(selector)
            else:
                content = soup.find(selector)
            if content:
                break

        # Fall back to body
        if not content:
            content = soup.find("body")
        if not content:
            return None

        # Extract text and clean up whitespace
        text = content.get_text(separator="\n", strip=True)
        # Collapse multiple blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Collapse excessive spaces
        text = re.sub(r"[ \t]{2,}", " ", text)

        text = text[:_MAX_CONTENT_CHARS]

        return text if len(text) > 100 else None

    except Exception as exc:
        logger.debug("Failed to extract text from %s: %s", url, exc)
        return None
