from typing import Optional, Tuple
import anthropic
from .searcher.types import SearchTool, SearchResult, Tool
import logging
import re
from utils import format_results_full
import json
from datetime import datetime


logger = logging.getLogger(__name__)


EXTRACTING_PROMPT = """
Extract factual claims from the text provided between <text></text> tags that can be independently verified.

Focus on:
- Specific dates and timestamps of events
- Monetary amounts and financial losses
- Names of protocols, exchanges, organizations, and individuals
- Transaction hashes, wallet addresses, or contract addresses
- Technical claims about vulnerabilities or attack vectors
- Claimed sequence of events in the timeline

Exclude:
- Opinions, analysis, or editorial commentary
- General background information that isn't specific to this incident
- Statements that are definitions or explanations of concepts

For each extracted statement, place it within <statement></statement> tags.
Return the total count within <number_of_statements></number_of_statements> tags.
Skip the preamble; go straight into the result.
"""

RETRIEVAL_PROMPT = """
Current date: {current_time}.

You are a fact-checker for a cryptocurrency security research wiki. Your task is to verify factual claims about crypto hacks, exploits, and security incidents using a search engine.

Search engine: <tool_description>{description}</tool_description>

## Instructions

For each <statement> that does not already have a <verdict>:
1. Formulate a precise search query. Use specific names, dates, and amounts from the statement. Wrap queries in <search_query></search_query> tags.
2. Evaluate search results carefully. Only mark a statement as 'True' if the search results directly confirm it with matching specifics (dates, amounts, names).
3. Assign a verdict:
   - **True**: Search results confirm the statement with matching details. Include the source URL.
   - **False**: Search results contradict the statement. Include an explanation of what the correct information is, citing the source.
   - **Unverified**: Search results are insufficient or ambiguous. Do NOT default to True — if you can't confirm it, mark it Unverified.

## Important
- Pay close attention to **exact amounts** — a statement claiming "$100M stolen" when the actual amount was "$97M" should be flagged.
- Pay close attention to **exact dates** — off-by-one-day errors in timelines are common and should be caught.
- Cross-reference entity names carefully — "Euler Finance" vs "Euler Labs" vs "Euler Protocol" matter.
- Skip statements that already have True/False verdicts.
- Base verdicts ONLY on information found in search results, not your training data.

Statements to be verified:
"""

ANSWER_PROMPT = """
You are a senior editor reviewing article submissions for a cryptocurrency security research wiki. Your review must be thorough, structured, and actionable.

Using the fact-checking results in <fact_checking_results></fact_checking_results> and the article text in <text></text>, produce a complete review with the following sections:

---

## 1. Fact-Checking Results

For each verified statement, format as:
- **Statement**: [statement text] [verdict emoji]
  - **Source**: [URL as markdown link, or "None"]
  - **Explanation**: [only if False — explain what's wrong and what the correct information is]

Verdict emojis:
- :white_check_mark: — Confirmed true by search results
- :x: — Contradicted by search results (MUST include explanation)
- :warning: — Unverified or source taken from the article itself

If no source URL was found in search results, check the article text for cited links. If a link from the article text is used, mark as :warning: not :white_check_mark:.

## 2. Editor's Notes

Provide specific, actionable feedback:
- Grammar and spelling errors (quote the error, suggest the fix)
- Stylistic improvements (clarity, conciseness, consistency)
- Timeline format: dates MUST follow "Month DD, YYYY, HH:MM PM UTC:" format (e.g., "May 05, 2023, 05:52 PM UTC:")
- Flag any unsupported claims that weren't caught in fact-checking
- Note any missing context that would strengthen the article

## 3. Hugo SSG Formatting Check

- Does it match Hugo SSG formatting? [emoji]
  - **Explanation**: [if not, explain what's wrong]

## 4. Submission Guidelines Compliance

### Filename Check
<thinking>
Extract the date of the incident from the article content (typically in Summary or Timeline).
Extract the target entity name from the article content.
Construct the expected filename: YYYY-MM-DD-entity-name.md
Compare with the actual filename from the diff.
</thinking>
- Expected Filename: `[constructed filename]`
- Actual Filename: `[filename from diff]` [emoji]

### Section Headers Check
- Required Headers: `## Summary, ## Attackers, ## Losses, ## Timeline, ## Security Failure Causes`
- Article Headers: `[list actual headers found]` [emoji]
- Missing headers should be flagged with :x:
- Extra headers should be flagged with :warning:

### Metadata Headers Check
Required metadata (between `---` delimiters): `date`, `target-entities`, `entity-types`, `attack-types`, `title`, `loss`

<thinking>
For each metadata field:
1. Extract the value from the article's frontmatter
2. Extract the corresponding information from the article body
3. Compare them and note discrepancies
</thinking>

- `date`: [value] — [matches article content? emoji]
- `target-entities`: [value] — [matches entities discussed? emoji]
- `entity-types`: [value] — [appropriate for target? emoji]
- `attack-types`: [value] — [matches attack described? emoji]
- `title`: [value] — [descriptive and accurate? emoji]
- `loss`: [value] — [matches Losses section? emoji]
- **Notes**: [list any discrepancies found]

---

Combine all sections into a single well-formatted Markdown output. Return the complete review in <answer></answer> tags.
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
    

    def extract_statements(self, text: str, model: str, temperature: float = 0.0, max_tokens: int = 1000):
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
    

    def retrieve(self, query: str, model: str, n_search_results_to_use: int = 3, stop_sequences: list[str] = [], max_tokens: int = 1000, max_searches_to_try: int = 5, temperature: float = 0.0) -> str:
        """
        Main method to retrieve relevant search results for a query with a provided search tool.

        Constructs RETRIEVAL prompt with query and search tool description. 
        Keeps sampling messages until stop sequence hit.

        Returns string with fact-checking results
        """
        assert self.search_tool is not None, "SearchTool must be provided to use .retrieve()"

        description = self.search_tool.tool_description
        statements = self.extract_statements(query, model=model, max_tokens=max_tokens, temperature=temperature)
        num_of_statements = int(self.extract_between_tags("number_of_statements", statements, strip=True))
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
            message = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages = messages,
                stop_sequences=["</search_query>"]
            )
            partial_completion, stop_reason, stop_seq = message.content[0].text, message.stop_reason, message.stop_sequence
            completions += partial_completion
            messages[0]['content'][0]['text'] += partial_completion
            if stop_reason == 'stop_sequence' and stop_seq == '</search_query>':
                logger.info(f'Attempting search number {tries}.')
                formatted_search_results = self._search_query_stop(partial_completion, n_search_results_to_use)
                completions += '</search_query>' + formatted_search_results
                messages[0]['content'][0]['text'] += '</search_query>' + formatted_search_results
            else:
                break
        return completions


    def answer_with_results(self, search_results: str, query: str, model: str, temperature: float, max_tokens: int = 4000):
        prompt = f'<fact_checking_results>{search_results}</fact_checking_results> <text>{query}</text>'
        try:
            message = self.client.messages.create(
                model=model,
                temperature=temperature,
                system=ANSWER_PROMPT,
                max_tokens=max_tokens,
                messages = [
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
            answer = str(e)
        return answer
    

    def completion_with_retrieval(self,
                                        query: str,
                                        model: str,
                                        n_search_results_to_use: int = 3,
                                        stop_sequences: list[str] = [],
                                        max_tokens: int = 1000,
                                        max_searches_to_try: int = 5,
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