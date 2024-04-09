import os
import aiohttp
from typing import Optional
from bs4 import BeautifulSoup
import anthropic
from anthropic import Anthropic, AsyncAnthropic
import logging

logger = logging.getLogger(__name__)

# Formatting search results
def format_results(extracted: list[str]) -> str:
    """
    Joins and formats the extracted search results as a string.

    :param extracted: The extracted search results to format.
    """
    result = "\n".join(
        [
            f'<item index="{i+1}">\n<page_content>\n{r}\n</page_content>\n</item>'
            for i, r in enumerate(extracted)
        ]
    )
    return result

def format_results_full(extracted: list[str]) -> str:
    """
    Formats the extracted search results as a string, including the <search_results> tags.

    :param extracted: The extracted search results to format.
    """
    return f"\n<search_results>\n{format_results(extracted)}\n</search_results>"

# Extract content, potentially using language models

async def scrape_url(url: str, summarize_with_claude: bool = False,
                     query: Optional[str] = None,
                     anthropic_api_key: Optional[str] = None,
                     missing_content_placeholder: str = "CONTENT NOT AVAILABLE") -> str:
    content = await get_url_content(url)
    if content:
        if summarize_with_claude:
            if anthropic_api_key is None:
                try:
                    anthropic_api_key = os.environ["ANTHROPIC_API_KEY"]
                except KeyError:
                    raise ValueError("anthropic_api_key must be provided if llm_extract is True")
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
    
    # Get first max_tokens_to_read words tokens of content

    client = Anthropic(api_key=anthropic_api_key)
    tokenizer = client.get_tokenizer()
    tokenized_content = tokenizer.encode(content).ids
    if len(tokenized_content) > max_tokens_to_read:
        logger.info(f"Truncating content from {len(tokenized_content)} tokens to {max_tokens_to_read} tokens")
        content = tokenizer.decode(tokenized_content[:max_tokens_to_read]).strip()

    # Generate prompt

    prompt = f"""{anthropic.HUMAN_PROMPT} Here is the content of a web page:
<content>
{content}
</content>"""

    if query:
        prompt += f"""
Here is a search query a user made which resulted in this page:

<query>
{query}
</query>

<instructions>
* Please provide a summary of the web page that is relevant to the query.
* Please made the summary as concise as possible, in bullet points, and include all the information that might be relevant to the query.
"""

    else:

        prompt += f"""

<instructions>
* Please provide a summary of the web page, as concisely as possible, in bullet points."""

    prompt += f"""
* Please do not introduce any additional information beyond what's in the web page.
* Please do not make any guesses about the contents of the web page. Simply summarize based on the given information content of the web page.
* If the content of the web page is not meaningful, relevant, or understandable then don't write anything.
* IMPORTANT: You are going to simulate the output of a web page. Therefore your response should look indistinguishable from what one might read on a web page. This means you should neither refer to yourself in any way in the response nor make it apparent that you are providing a summary. You should not explicitly mention in any way that you are providing a simulated output of a web page.
* IMPORTANT: Please do not ask for feedback on your summary in any way at the end of your response.
* IMPORTANT: Please do not mention that you are providing a summary, or mention "summary" in any other way.
</instructions>{anthropic.AI_PROMPT} Based on the given content{' and query' if query else ''}, the summary of the page would be:
<summary>"""

    logger.info(f"Triggering a Claude extract for a {len(tokenizer.encode(content).ids)} token document")

    client = AsyncAnthropic(api_key=anthropic_api_key)
    response = await client.completions.create(
        prompt=prompt,
        max_tokens_to_sample=512,
        temperature=0.0,
        model="claude-3-opus-20240229",
        stop_sequences=["</summary>", anthropic.HUMAN_PROMPT]
    )

    # Extract summary

    completion = response.completion
    if not completion.endswith("</summary>"):
        completion += "</summary>"
    return '<summary>'+completion
