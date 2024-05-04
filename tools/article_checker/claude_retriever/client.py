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
Please extract important statements that appear to be factual from the text provided between <text></text> tags.
Return the extracted statements. Place each statement within <statement></statement> tags.
Also, return the number of extracted statements within <number_of_statements></number_of_statements> tags.
Aim to extract important statements with numbers, dates, and names of organizations. There should not be too many extracted statements.
Skip the preamble; go straight into the result.
"""

RETRIEVAL_PROMPT = """
Your timeline extends up to the current one — {current_time}.
You are tasked with verifying the accuracy of a series of factual statements using a search engine. Below is the search engine's description: <tool_description>{description}</tool_description>.
For each statement within <statement></statement> tags, if the statement already has a verdict in the <verdict></verdict> tags (either 'True' or 'False'), skip it and move to the next statement. For statements without a verdict, formulate a query to check its accuracy. You can make a call to the search engine tool by inserting a query within <search_query> tags like so: <search_query>query</search_query>. You'll then get results back within <search_result></search_result> tags.
Based on these results, determine the accuracy of each statement and categorize it as 'True', 'False', or 'Unverified'.
Put your verdict in <verdict></verdict> tags. If a statement is true, put 'True' in the <verdict></verdict> tags.
Include the Web Page URL in <source></source> tags. If there is no URL at all, put 'None' in the <source></source> tags.
If a statement is false, include an explanation in <explanation></explanation> tags.
Focus particularly on verifying numbers, dates, monetary values, and names of people or organizations.
Avoid verifying statements that already have a True/False verdict in the <verdict></verdict> tags.
Determine the accuracy of each statement using only information that is contained in the search_result.
If you need to search again, put the new query in <search_query></search_query>.

Statements to be verified: 
"""

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