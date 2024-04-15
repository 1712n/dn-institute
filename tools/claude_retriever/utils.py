import os
import aiohttp
import json
from typing import Optional
from bs4 import BeautifulSoup
import anthropic
from anthropic import AsyncAnthropic
import logging


logger = logging.getLogger(__name__)

with open('tools/config.json', 'r') as config_file:
    config = json.load(config_file)

model = config['ANTHROPIC_SUMMARIZE_MODEL']


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
                content = await claude_extract(content, query, anthropic_api_key)
            except Exception as e:
                logger.warning(f"Failed to extract with Claude. Falling back to raw content. Error: {e}")
    else:
        content = missing_content_placeholder
    return content


async def get_url_content(url: str) -> Optional[str]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                text = soup.get_text(strip=True, separator='\n')
                return text
    return None


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
        max_tokens=512,
        temperature=0.0,
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    )

    summary = response.content[0].text  
    if not summary.endswith("</summary>"):
        summary += "</summary>"

    return f"<summary>{summary}"