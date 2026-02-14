from typing import Optional, Tuple
import anthropic
from .searcher.types import SearchTool, SearchResult, Tool
import logging
import re
from utils import format_results_full
import json
from datetime import datetime


logger = logging.getLogger(__name__)


EXTRACTING_PROMPT = """You are a fact-checking assistant specializing in cryptocurrency security incidents.

Your task: Extract **verifiable factual claims** from the article text provided between <text></text> tags.

Focus on claims that can be independently verified through web searches:
- Specific monetary amounts and losses (e.g., "$20 million stolen")
- Dates and timestamps of events (e.g., "On May 14, 2024")
- Names of entities, protocols, and individuals involved
- Blockchain addresses and transaction hashes (verify they exist and match claims)
- Descriptions of attack methods and vulnerabilities
- Claims about protocol responses (pauses, bounties offered, post-mortems)

Rules:
- Place each statement within <statement></statement> tags
- Return the count within <number_of_statements></number_of_statements> tags
- Extract 5-15 of the most important verifiable statements
- Prefer statements with specific numbers, dates, and named entities
- DO NOT extract subjective opinions or vague claims
- Skip the preamble; go straight into the result
"""

RETRIEVAL_PROMPT = """Your current date is {current_time}.

You are a cryptocurrency security researcher performing fact-checking verification. You have access to a search engine described here: <tool_description>{description}</tool_description>

Your task: Verify each factual statement provided within <statement></statement> tags.

Process:
1. For each statement WITHOUT a <verdict></verdict> tag, formulate a precise search query
2. Issue the query by writing: <search_query>your query here</search_query>
3. Review the search results returned within <search_result></search_result> tags
4. Determine the accuracy of the statement

Search query best practices for crypto incidents:
- Include the protocol/entity name AND the year
- For monetary amounts, search for the incident name + "hack" or "exploit" + amount
- For dates, search for the event name + specific date
- For blockchain addresses, search for the address directly
- If the first search is inconclusive, try a more specific or different query

Verdicts:
- **True**: The claim is supported by search results with matching details
- **False**: The search results contradict the claim (include explanation in <explanation></explanation>)
- **Unverified**: Could not find sufficient evidence to confirm or deny

Place your verdict in <verdict></verdict> tags.
Include the source URL in <source></source> tags (or 'None' if no URL found).

Important:
- Pay special attention to EXACT numbers — $20M vs $20.5M matters
- Verify dates precisely — month/day/year must all match
- Cross-reference entity names for correctness
- Skip statements that already have a True/False verdict

Statements to be verified:
"""

ANSWER_PROMPT = """You are a senior editor for the DN Institute Crypto Attack Wiki. Your role is to review article submissions for quality, accuracy, and compliance with submission guidelines.

Perform the following checks and compile a structured report:

---

## 1. FACT-CHECK RESULTS

Using the information in <fact_checking_results></fact_checking_results> tags:
- List each statement from <statement></statement> tags with its verification result
- Use ✅ for verified True statements
- Use ❌ for False statements (include explanation)
- Use ⚠️ for Unverified statements
- Include the source URL for each

Format:
```
- **Statement**: [claim] ✅/❌/⚠️
  - **Source**: [URL or None]
  - **Explanation**: [only for ❌ - what the correct information is]
```

---

## 2. METADATA VALIDATION

Check the YAML frontmatter between `---` delimiters in <text></text> tags.

Required metadata fields (ALL must be present, NO extras allowed):
- `date` — YYYY-MM-DD format, must match the actual incident date from the article body
- `target-entities` — must match the entities described in the Summary
- `entity-types` — must correspond to the type of target entity (e.g., DeFi, CEX, DEX, Bridge, GameFi, etc.)
- `attack-types` — must match the type of attack described (e.g., Smart Contract Exploit, Flash Loan Attack, Rug Pull, Phishing, Private Key Compromise, etc.)
- `title` — should be descriptive and accurate
- `loss` — numeric value (no currency symbols), must match the loss amount described in the Losses section

For each field, verify:
1. Is it present?
2. Is its value correct and consistent with the article content?

Use <thinking></thinking> tags for your reasoning on date, target-entities, and loss comparisons.

---

## 3. SECTION STRUCTURE CHECK

Verify the article contains ONLY these section headers (in this order):
- `## Summary`
- `## Attackers`
- `## Losses`
- `## Timeline`
- `## Security Failure Causes`

Flag any missing, extra, or misordered sections.

---

## 4. FILENAME VALIDATION

The filename should follow: `YYYY-MM-DD-Entity-Name.md`
- Date must match the `date` metadata header
- Entity name must match `target-entities`
- Use hyphens instead of spaces

Extract the filename from the diff header in <text></text> tags and compare.

---

## 5. TIMELINE FORMAT CHECK

In the `## Timeline` section, verify all dates follow this format:
`**Month DD, YYYY, HH:MM AM/PM UTC:**`

Example: `**May 05, 2023, 05:52 PM UTC:**`

Flag entries with incorrect formatting.

---

## 6. CONTENT QUALITY ASSESSMENT

Evaluate:
- **References**: Are claims backed by links to credible sources (block explorers, official announcements, security firm reports)?
- **Completeness**: Does the article cover the incident comprehensively?
- **Objectivity**: Is the language factual and data-driven (no speculation or ambiguous language)?
- **Blockchain evidence**: Are on-chain transaction hashes and addresses provided where relevant?
- **Grammar and style**: Note any grammatical errors or unclear writing

---

## 7. HUGO SSG FORMATTING

Verify the Markdown is valid for Hugo static site generator:
- Proper YAML frontmatter
- Valid Markdown syntax
- Properly formatted links
- No HTML unless necessary

Use ✅ if formatting is correct, ❌ with explanation if not.

---

Combine ALL sections into a single well-formatted Markdown report.
Return the complete report within <answer></answer> tags.
"""


class ClientWithRetrieval:

    def __init__(self, api_key: str, search_tool: Optional[SearchTool] = None, verbose: bool = True):
        """
        Initializes the ClientWithRetrieval class.
        
        Parameters:
            search_tool (SearchTool): SearchTool object to handle searching
            verbose (bool): Whether to print verbose logging
        """
        self.search_tool = search_tool
        self.verbose = verbose
        self.client = anthropic.Anthropic(api_key=api_key)
    

    def extract_statements(self, text: str, model: str, temperature: float = 0.0, max_tokens: int = 2000):
        message = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=EXTRACTING_PROMPT,
            messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"<text>{text}</text>"
                    }
                ]
            }
        ]
        )
        return message.content[0].text
    

    def retrieve(self, query: str, model: str, n_search_results_to_use: int = 3, stop_sequences: list[str] = [], max_tokens: int = 1000, max_searches_to_try: int = 8, temperature: float = 0.0) -> str:
        """
        Main method to retrieve relevant search results for a query with a provided search tool.

        Constructs RETRIEVAL prompt with query and search tool description. 
        Keeps sampling messages until stop sequence hit.

        Returns string with fact-checking results
        """
        assert self.search_tool is not None, "SearchTool must be provided to use .retrieve()"

        description = self.search_tool.tool_description
        statements = self.extract_statements(query, model=model, max_tokens=max_tokens, temperature=temperature)
        
        # Safely extract number of statements
        try:
            num_str = self.extract_between_tags("number_of_statements", statements, strip=True)
            num_of_statements = int(num_str) if num_str else 5
        except (ValueError, TypeError):
            logger.warning(f"Could not parse number_of_statements, defaulting to 5")
            num_of_statements = 5
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        system_prompt = f"{RETRIEVAL_PROMPT.format(current_time=current_time, description=description)}"

        completions = ""
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": statements
                    }
                ]
            }
        ]
        for tries in range(min(num_of_statements, max_searches_to_try)):
            try:
                message = self.client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=messages,
                    stop_sequences=["</search_query>"]
                )
                partial_completion = message.content[0].text
                stop_reason = message.stop_reason
                stop_seq = message.stop_sequence
            except Exception as e:
                logger.error(f"Error in retrieval API call (attempt {tries}): {e}")
                break
                
            completions += partial_completion
            messages[0]['content'][0]['text'] += partial_completion
            if stop_reason == 'stop_sequence' and stop_seq == '</search_query>':
                logger.info(f'Attempting search number {tries}.')
                try:
                    formatted_search_results = self._search_query_stop(partial_completion, n_search_results_to_use)
                except Exception as e:
                    logger.error(f"Search failed on attempt {tries}: {e}")
                    formatted_search_results = "\n<search_results>\n<item index=\"1\">\n<page_content>\nSearch failed. Please continue with available information.\n</page_content>\n</item>\n</search_results>"
                completions += '</search_query>' + formatted_search_results
                messages[0]['content'][0]['text'] += '</search_query>' + formatted_search_results
            else:
                break
        return completions


    def answer_with_results(self, search_results: str, query: str, model: str, temperature: float, max_tokens: int = 8000):
        prompt = f'<fact_checking_results>{search_results}</fact_checking_results> <text>{query}</text>'
        try:
            message = self.client.messages.create(
                model=model,
                temperature=temperature,
                system=ANSWER_PROMPT,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]       
                    }
                ]
            )
            answer = message.content[0].text
        except Exception as e:
            answer = f"Error generating analysis: {str(e)}"
        return answer
    

    def completion_with_retrieval(self,
                                        query: str,
                                        model: str,
                                        n_search_results_to_use: int = 3,
                                        stop_sequences: list[str] = [],
                                        max_tokens: int = 1000,
                                        max_searches_to_try: int = 8,
                                        temperature: float = 0.0) -> str:
        """
        Gets a final completion from retrieval results        
        
        Calls retrieve() to get search results.
        Calls answer_with_results() with search results and query.
        
        Returns:
            str: Claude's answer to the query
        """
        search_results = self.retrieve(query, model=model,
                                                 n_search_results_to_use=n_search_results_to_use, stop_sequences=stop_sequences,
                                                 max_tokens=max_tokens,
                                                 max_searches_to_try=max_searches_to_try,
                                                 temperature=temperature)
        answer = self.answer_with_results(search_results, query, model, temperature)
        answer = self.extract_between_tags("answer", answer)
        if answer is None:
            # If no <answer> tags found, return the raw response
            logger.warning("No <answer> tags found in LLM response, returning raw output")
            answer = self.answer_with_results(search_results, query, model, temperature)
        return answer
    

    def _search_query_stop(self, partial_completion: str, n_search_results_to_use: int) -> Tuple[list[SearchResult], str]:
        """
        Helper to handle search query stop case.
        
        Extracts search query from completion text.
        Runs search using SearchTool. 
        Formats search results.
        
        Returns:
            tuple: 
                list[SearchResult]: Raw search results
                str: Formatted search result text
        """
        assert self.search_tool is not None, "SearchTool was not provided for client"

        search_query = self.extract_between_tags('search_query', partial_completion + '</search_query>') 
        if search_query is None:
            raise Exception(f'Completion with retrieval failed as partial completion returned mismatched <search_query> tags.')
        if self.verbose:
            logger.info('\n'+'-'*20 + f'\nPausing stream because Claude has issued a query in <search_query> tags: <search_query>{search_query}</search_query>\n' + '-'*20)
        logger.info(f'Running search query against SearchTool: {search_query}')
        search_results = self.search_tool.raw_search(search_query, n_search_results_to_use)
        extracted_search_results = self.search_tool.process_raw_search_results(search_results)
        formatted_search_results = format_results_full(extracted_search_results)

        if self.verbose:
            logger.info('\n' + '-'*20 + f'\nThe SearchTool has returned the following search results:\n\n{formatted_search_results}\n\n' + '-'*20 + '\n')
        return formatted_search_results
    

    def extract_between_tags(self, tag, string, strip=True):
        """
        Helper to extract text between XML tags.
        
        Finds last match of specified tags in string.
        Handles edge cases and stripping.
        
        Returns:
            str: Extracted string between tags
        """
        ext_list = re.findall(f"<{tag}\\s?>(.+?)</{tag}\\s?>", string, re.DOTALL)
        if strip:
            ext_list = [e.strip() for e in ext_list]
        
        if ext_list:
            return ext_list[-1]
        else:
            return None
