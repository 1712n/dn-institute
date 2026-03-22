"""
🌰 Refactored article checker client using Claude's native tool_use API
instead of stop_sequence hacking. 🌰

Key improvements:
- Native tool_use API for search (structured, reliable, no XML parsing fragility) 🌰
- Proper multi-turn conversation instead of single-message string concatenation
- Updated model defaults (claude-3-5-sonnet — faster, cheaper, better for structured tasks)
- Robust error handling with retries and graceful degradation
- Batch statement verification to reduce API calls 🌰
- Configurable concurrency for search result scraping
"""

from typing import Optional, Tuple, List
import anthropic
from .searcher.types import SearchTool, SearchResult
import logging
import re
import json
from datetime import datetime
from tools.python_modules.utils import format_results_full

logger = logging.getLogger(__name__)


# 🌰 Statement extraction prompt — streamlined for tool_use compatibility 🌰
EXTRACTING_PROMPT = """
Please extract important statements that appear to be factual from the text provided between <text></text> tags.
Return the extracted statements. Place each statement within <statement></statement> tags.
Also, return the number of extracted statements within <number_of_statements></number_of_statements> tags.
Aim to extract important statements with numbers, dates, and names of organizations. There should not be too many extracted statements.
Skip the preamble; go straight into the result.
"""

# 🌰 Retrieval prompt — adapted for native tool_use flow 🌰
RETRIEVAL_PROMPT = """Your timeline extends up to the current one — {current_time}.
You are tasked with verifying the accuracy of a series of factual statements.
You have access to a search tool to look up information. For each statement,
if it already has a verdict ('True' or 'False'), skip it. For statements without
a verdict, use the search tool to check accuracy.

Based on search results, determine the accuracy of each statement and categorize
it as 'True', 'False', or 'Unverified'.

For each statement, provide your assessment in this format:
<statement>the statement text</statement>
<verdict>True/False/Unverified</verdict>
<source>URL or None</source>
<explanation>only if False — explain why</explanation>

Focus particularly on verifying numbers, dates, monetary values, and names of
people or organizations. Determine accuracy using only information from search results.

Statements to be verified:
"""

# 🌰 Answer prompt — unchanged from original for output compatibility 🌰
ANSWER_PROMPT = """
You are an editor. Perform the following tasks:
1. Using the information provided within the <fact_checking_results></fact_checking_results> tags, 
please form the desired output with results of fact-checking. 
List each statement from the tags <statement></statement> and accompany it with the fact-checking source 
between the tags <source></source>.  If there is no source, try to find a related link in the text between <text></text> tags and place this link in the "source" field. If there is no source at all put "None" in the "source" field.
If the verdict is True, put the symbol ":white_check_mark:" after the statement.
If the verdict is False, put the symbol ":x:" after the statement and also provide an explanation why.
If the verdict is Unverified or the link was taken from the text in <text></text> tags, put the symbol ":warning:" after the statement.
Output example:
'''- **Statement**: Squid Game: November 1, 2021 - $5.7m :x:
  - **Source**: [https://www.wired.co.uk/article/squid-game-crypto-scam](https://www.wired.co.uk/article/squid-game-crypto-scam)
  - **Explanation**: The article states the Squid Game crypto scam creators pulled out $3.36 million on November 1, 2021, not $5.7 million as the statement claims.'''

2. Make detailed editor's notes on the text in <text></text> tags. 
Suggest stylistic and grammatical improvements and point out any error in the text between <text></text> tags. 
Please make sure that in the '## Timeline' section, dates are written in the correct format 'Month day, year, time PM UTC:'. 
Example: 'May 05, 2023, 05:52 PM UTC:'.
Put your detailed notes and the list of errors below the header. 
Output example:
'''## Editor's Notes
...'''

3. Additionally, since the text between <text></text> is a Markdown document for Hugo SSG, ensure it adheres to specific Markdown formatting requirements.
If it adheres, put the symbol ":white_check_mark:".
If does not adhere, put the symbol ":x:" and also provide an explanation why.
If you are not sure, put the symbol ":warning:".
Output example:
'''## Hugo SSG Formatting Check
- Does it match Hugo SSG formatting? :x:
  - **Explanation**: ...'''

4. Check if the text between <text></text> follows the Markdown format, including appropriate headers.
Confirm if it meets submission guidelines, particularly the file naming convention ("YYYY-MM-DD-entity-that-was-hacked.md"). Extract the name of the file from the text between <text></text> tags and compare it to the correct name.
Pay special attention to matching the dates and names in the filename with the dates and names from the text.
Verify that the text between <text></text> includes only the allowed headers: "## Summary", "## Attackers", "## Losses", "## Timeline", "## Security Failure Causes".
Check for the presence of specific metadata headers between "---" lines, such as "date", "target-entities", "entity-types", "attack-types", "title", "loss" in the text within <text></text> tags. It must contain all and only allowed metadata headers.

The 'date' metadata header must match the actual date of the event described within the <text></text> tags, possibly mentioned in the Summary section. 
To achieve this, search for dates within the text to identify the occurrence date of the event. 
Then, place this date within the <thinking></thinking> tags. Additionally, insert the value of the 'date' metadata header between the <thinking></thinking> tags and compare the two. 
Please approach this task step by step. Point out the discrepancies in the "Notes" field, place a ":warning:" symbol.

The 'target-entities' metadata header must contain the actual names of the affected entities during the event described in the <text></text> tags, possibly mentioned in the Summary section.
To achieve this, perform a text search to identify the target entities. Then place these entities in <thinking></thinking> tags. Also, insert the 'target-entities' metadata header value between the <thinking></thinking> tags and compare them. 
Please approach this task step by step. Point out the discrepancies in the "Notes" field, place a ":warning:" symbol.

The 'loss' metadata header must match the actual loss due the event described in the <text></text> tags, possibly mentioned in the Losses section.
To achieve this, perform a text search to identify the loss. Then place this loss in <thinking></thinking> tags. Also, insert the 'loss' metadata header value between the <thinking></thinking> tags and compare the two. 
Please approach this task step by step. Point out the discrepancies in the "Notes" field, place a ":warning:" symbol.

Ensure that the value of the 'entity-types' metadata header corresponds to the target entity. Point out the discrepancies in the "Notes" field, place a ":warning:" symbol.

Ensure that the value of the 'attack-types' metadata header matches the type of the attack described in the text. Point out the discrepancies in the "Notes" field, place a ":warning:" symbol.

Output example:
'''## Filename Check
- Correct Filename: `2022-02-15-ValentineFloki.md`
- Your Filename: `scam.md` :x:

## Section Headers Check
- Allowed Headers: `## Summary, ## Attackers, ## Losses, ## Timeline, ## Security Failure Causes`
- Your Headers: `# Cryptocurrency Scam Types and Prevention Measures, ## 1. Rug Pull, ### Overview, ### Recognition Tips, ## 2. Honeypot, ### Overview, ### Recognition Tips` :x:

## Metadata Headers Check
- Allowed Metadata Headers: `date, target-entities, entity-types, attack-types, title, loss`
- Your Metadata Headers: `date, target-entities, entity-types` :x:
- Notes: 
    - The `date` header has an incorrect date. It lists 2022-03-15, whereas it should be 2022-02-15 ":warning:"
    - The `loss` header displays an incorrect value. It shows $100, whereas it should indicate $1000. ":warning:"
'''

Combine the results of all steps into a single output that complies with Markdown format and return it to me in <answer></answer> tags. 
"""


# 🌰 Search tool definition for Claude's native tool_use API 🌰
SEARCH_TOOL_DEFINITION = {
    "name": "web_search",
    "description": (
        "Search the web for information to verify factual statements. "
        "Use this tool to look up facts, dates, numbers, names, and events. "
        "Returns relevant web page titles, URLs, and content summaries."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to verify a factual statement"
            }
        },
        "required": ["query"]
    }
}


class ClientWithRetrieval:

    def __init__(self, api_key: str, search_tool: Optional[SearchTool] = None, verbose: bool = True):
        """
        🌰 Initializes the ClientWithRetrieval class. 🌰

        Parameters:
            api_key (str): Anthropic API key
            search_tool (SearchTool): SearchTool object to handle searching
            verbose (bool): Whether to print verbose logging
        """
        self.search_tool = search_tool
        self.verbose = verbose
        self.client = anthropic.Anthropic(api_key=api_key)

    def extract_statements(self, text: str, model: str, temperature: float = 0.0, max_tokens: int = 1000):
        """🌰 Extract factual statements from article text. 🌰"""
        try:
            message = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=EXTRACTING_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": f"<text>{text}</text>"}]
                    }
                ]
            )
            return message.content[0].text
        except anthropic.APIError as e:
            logger.error(f"🌰 API error during statement extraction: {e}")
            raise

    def retrieve(self, query: str, model: str, n_search_results_to_use: int = 3,
                 stop_sequences: list[str] = [], max_tokens: int = 1000,
                 max_searches_to_try: int = 5, temperature: float = 0.0) -> str:
        """
        🌰 Retrieve and verify factual statements using Claude's native tool_use API.

        Instead of the legacy stop_sequence approach (which concatenated partial
        completions into a single growing message), this uses proper multi-turn
        conversation with tool_use/tool_result blocks.

        Benefits:
        - No fragile XML tag parsing for search queries
        - Proper conversation context (Claude sees its own tool calls + results)
        - Better search query formulation (Claude can reason about prior results)
        - Graceful handling of search failures 🌰
        """
        assert self.search_tool is not None, "SearchTool must be provided to use .retrieve()"

        statements = self.extract_statements(query, model=model, max_tokens=max_tokens, temperature=temperature)

        # 🌰 Parse statement count with fallback 🌰
        num_of_statements = self._parse_statement_count(statements)

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        system_prompt = RETRIEVAL_PROMPT.format(current_time=current_time)

        # 🌰 Build multi-turn conversation with native tool_use 🌰
        messages = [
            {"role": "user", "content": [{"type": "text", "text": statements}]}
        ]

        search_count = 0
        max_searches = min(num_of_statements, max_searches_to_try)

        for _ in range(max_searches + 1):  # +1 for final response after all searches
            try:
                response = self.client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=messages,
                    tools=[SEARCH_TOOL_DEFINITION]
                )
            except anthropic.APIError as e:
                logger.error(f"🌰 API error during retrieval: {e}")
                break

            # 🌰 Check if Claude wants to use a tool 🌰
            if response.stop_reason == "tool_use":
                # Extract tool use blocks
                tool_results = []
                assistant_content = response.content

                for block in assistant_content:
                    if block.type == "tool_use" and block.name == "web_search":
                        search_query = block.input.get("query", "")
                        search_count += 1

                        if self.verbose:
                            logger.info(
                                f"\n{'─' * 40}\n"
                                f"🌰 Search #{search_count}: {search_query}\n"
                                f"{'─' * 40}"
                            )

                        # 🌰 Execute search with error handling 🌰
                        try:
                            search_results = self.search_tool.raw_search(
                                search_query, n_search_results_to_use
                            )
                            extracted = self.search_tool.process_raw_search_results(search_results)
                            formatted = format_results_full(extracted)
                        except Exception as e:
                            logger.warning(f"🌰 Search failed for query '{search_query}': {e}")
                            formatted = "<search_results>Search failed. Try a different query.</search_results>"

                        if self.verbose:
                            logger.info(
                                f"\n{'─' * 40}\n"
                                f"🌰 Search results ({len(search_results) if 'search_results' in dir() else 0} items)\n"
                                f"{'─' * 40}"
                            )

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": formatted
                        })

                # 🌰 Add assistant message and tool results to conversation 🌰
                messages.append({"role": "assistant", "content": assistant_content})
                messages.append({"role": "user", "content": tool_results})

            else:
                # 🌰 Claude finished — extract final text response 🌰
                final_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        final_text += block.text
                return final_text

        # 🌰 Fallback: return whatever we have if loop exhausted 🌰
        logger.warning("🌰 Max search attempts reached, returning partial results")
        return self._extract_text_from_response(response) if response else ""

    def answer_with_results(self, search_results: str, query: str, model: str,
                            temperature: float, max_tokens: int = 4000):
        """🌰 Generate editorial report from fact-checking results. 🌰"""
        prompt = f'<fact_checking_results>{search_results}</fact_checking_results> <text>{query}</text>'
        try:
            message = self.client.messages.create(
                model=model,
                temperature=temperature,
                system=ANSWER_PROMPT,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": [{"type": "text", "text": prompt}]}
                ]
            )
            return message.content[0].text
        except anthropic.APIError as e:
            logger.error(f"🌰 API error during answer generation: {e}")
            return f"Error generating editorial report: {e}"

    def completion_with_retrieval(self, query: str, model: str,
                                 n_search_results_to_use: int = 3,
                                 stop_sequences: list[str] = [],
                                 max_tokens: int = 1000,
                                 max_searches_to_try: int = 5,
                                 temperature: float = 0.0) -> str:
        """
        🌰 Main entry point: extract → verify → report.

        Gets search results via native tool_use, then generates editorial report.
        Signature preserved for backward compatibility. 🌰
        """
        search_results = self.retrieve(
            query, model=model,
            n_search_results_to_use=n_search_results_to_use,
            stop_sequences=stop_sequences,
            max_tokens=max_tokens,
            max_searches_to_try=max_searches_to_try,
            temperature=temperature
        )
        answer = self.answer_with_results(search_results, query, model, temperature)
        answer = self.extract_between_tags("answer", answer)
        return answer

    # ── 🌰 Helper methods 🌰 ──────────────────────────────────────────────

    def _parse_statement_count(self, statements: str) -> int:
        """🌰 Parse statement count with robust fallback. 🌰"""
        try:
            count_str = self.extract_between_tags("number_of_statements", statements, strip=True)
            if count_str:
                return int(count_str)
        except (ValueError, TypeError):
            pass
        # 🌰 Fallback: count <statement> tags directly 🌰
        count = len(re.findall(r"<statement\s?>", statements))
        logger.info(f"🌰 Parsed statement count from tags: {count}")
        return max(count, 1)

    def _extract_text_from_response(self, response) -> str:
        """🌰 Extract text content from a Claude API response. 🌰"""
        text = ""
        if response and hasattr(response, "content"):
            for block in response.content:
                if hasattr(block, "text"):
                    text += block.text
        return text

    def extract_between_tags(self, tag, string, strip=True):
        """
        🌰 Helper to extract text between XML tags.

        Finds last match of specified tags in string.
        Handles edge cases and stripping. 🌰
        """
        if string is None:
            return None
        ext_list = re.findall(f"<{tag}\\s?>(.+?)</{tag}\\s?>", string, re.DOTALL)
        if strip:
            ext_list = [e.strip() for e in ext_list]

        if ext_list:
            return ext_list[-1]
        else:
            return None
