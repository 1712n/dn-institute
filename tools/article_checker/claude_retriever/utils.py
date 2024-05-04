import os
import aiohttp
import json
from typing import Optional
from bs4 import BeautifulSoup
import anthropic
from anthropic import AsyncAnthropic
import logging
import bleach
from urllib.parse import urlparse


logger = logging.getLogger(__name__)

with open('tools/article_checker/config.json', 'r') as config_file:
    config = json.load(config_file)

model = config['ANTHROPIC_SUMMARIZE_MODEL']
temperature = config['ANTHROPIC_SUMMARIZE_TEMPERATURE']
max_tokens = config['ANTHROPIC_SUMMARIZE_MAX_TOKENS']


def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

        
def format_results(extracted: list[str]) -> str:
    result = "\n".join(
        f'<item index="{i+1}">\n<page_content>\n{r}\n</page_content>\n</item>'
        for i, r in enumerate(extracted)
    )
    return result


def format_results_full(extracted: list[str]) -> str:
    return f"\n<search_results>\n{format_results(extracted)}\n</search_results>"


async def scrape_url(url: str, summarize_with_claude: bool = False,
                     query: Optional[str] = None,
                     anthropic_api_key: Optional[str] = None,
                     missing_content_placeholder: str = "CONTENT NOT AVAILABLE") -> str:
    content = await get_url_content(url)
    if content:
        if summarize_with_claude:
            if anthropic_api_key is None:
                raise ValueError("anthropic_api_key must be provided if summarize_with_claude is True")
            try:
                content = await claude_extract_article(content, query, anthropic_api_key)
            except Exception as e:
                logger.warning(f"Failed to extract with Claude. Falling back to raw content. Error: {e}")
    else:
        content = missing_content_placeholder
    return content


async def get_url_content(url: str, timeout: int = 10) -> Optional[str]:
    try:
        if not is_valid_url(url):
            logger.warning(f"Invalid URL: {url}")
            return None

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout, headers={'User-Agent': 'Mozilla/5.0'}) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    text = soup.get_text(strip=True, separator='\n')
                    
                    # Sanitize the extracted text using bleach
                    sanitized_text = bleach.clean(text, tags=[], attributes={}, strip=True)
                    
                    return sanitized_text
                else:
                    logger.warning(f"HTTP error {response.status} for URL: {url}")
    except Exception as e:
        logger.exception(f"Error fetching URL: {url}")
    return None


async def claude_extract_article(content: str, query: Optional[str], anthropic_api_key: str, max_tokens_to_read: int = 20_000) -> str:
    client = anthropic.Anthropic(api_key=anthropic_api_key)
    tokenizer = client.get_tokenizer()
    tokenized_content = tokenizer.encode(content).ids
    if len(tokenized_content) > max_tokens_to_read:
        logger.info(f"Truncating content from {len(tokenized_content)} tokens to {max_tokens_to_read} tokens")
        content = tokenizer.decode(tokenized_content[:max_tokens_to_read]).strip()
    
    prompt_text = f"Here is the content from a web page. Please extract only the article from this content:\n{content}"
    if query:
        prompt_text += f"\nThis extraction is in response to the following user query:\n{query}"
    instructions = """
    Extract the main article content from this web page, excluding site navigation, advertisements, sidebars, and other non-essential elements. Ensure the extracted text is clean and contains only the relevant information focusing solely on the primary article.
    """
    prompt = f"{prompt_text} {instructions}"
    client = AsyncAnthropic(api_key=anthropic_api_key)
    response = await client.messages.create(
        model=model,
        stop_sequences=["</article>"],
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    )

    extracted_article = response.content[0].text  
    if not extracted_article.endswith("</article>"):
        extracted_article += "</article>"

    return f"<article>{extracted_article}"


async def claude_extract(content: str, query: Optional[str], anthropic_api_key: str, max_tokens_to_read: int = 20_000) -> str:
    client = anthropic.Anthropic(api_key=anthropic_api_key)
    tokenizer = client.get_tokenizer()
    tokenized_content = tokenizer.encode(content).ids
    if len(tokenized_content) > max_tokens_to_read:
        logger.info(f"Truncating content from {len(tokenized_content)} tokens to {max_tokens_to_read} tokens")
        content = tokenizer.decode(tokenized_content[:max_tokens_to_read]).strip()
    
    prompt_text = f"Here is the content of a web page:\n<content>{content}</content>"
    if query:
        prompt_text += f"\nHere is a search query a user made which resulted in this page:\n<query>{query}</query>"

    instructions = """
    Please provide a summary of the web page that is relevant to the query.
    Please make the summary as concise as possible, in bullet points, and include all the information that might be relevant to the query.
    Do not introduce any additional information beyond what's in the web page.
    Do not make any guesses about the contents of the web page. Simply summarize based on the given information content of the web page.
    If the content of the web page is not meaningful, relevant, or understandable then don't write anything.
    """
    prompt = f"{prompt_text} {instructions}"
    client = AsyncAnthropic(api_key=anthropic_api_key)
    response = await client.messages.create(
        model=model,
        stop_sequences=["</summary>"],
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    )

    summary = response.content[0].text  
    if not summary.endswith("</summary>"):
        summary += "</summary>"

    return f"<summary>{summary}"