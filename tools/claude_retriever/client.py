from typing import Optional, Tuple
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from .searcher.types import SearchTool, SearchResult, Tool
import logging
import re
from utils import format_results_full
import json

logger = logging.getLogger(__name__)

EXTRACTING_PROMPT = """
Please extract important statements that appear to be factual from the text provided between <text></text> tags.
Return the extracted statements. Place each statement within <statement></statement> tags.
Also, return the number of extracted statements within <number_of_statements></number_of_statements> tags.
Aim to extract important statements with numbers, dates, and names of organizations. There should not be too many extracted statements.
Skip the preamble; go straight into the result.
"""

RETRIEVAL_PROMPT = """
You are tasked with verifying the accuracy of a series of factual statements using a search engine. Below is the search engine's description: <tool_description>{description}</tool_description>.

For each statement within <statement></statement> tags formulate a query to check its accuracy. You can make a call to the search engine tool by inserting a query within <search_query> tags like so: <search_query>query</search_query>. You'll then get results back within <search_result></search_result> tags.
Results will be provided in <search_result></search_result> tags. Based on these results, determine the accuracy of each statement and categorize it as 'True', 'False', or 'Unverified'.
Include the Web Page URL in <source></source> tags (use 'None' if no URL is available).
If a statement is false, include an explanation in <explanation></explanation> tags.
Focus particularly on verifying numbers, dates, monetary values, and names of people or organizations.
Avoid verifying statements already enclosed in <search_query>query</search_query> tags.
Do not try to answer the query. Your only job is to gather relevant search results that will help to check the accuracy of statements.

Statements to be verified: 
"""

ANSWER_PROMPT = """
Please review the provided tex between <text></text> tags:
<fact_checking_results>%s</fact_checking_results>

<text>%s</text>

Perform the following tasks:
1. Using the information provided within the <fact_checking_results></fact_checking_results> tags, 
please form the desired output with results of fact-checking. There should be required fields "statement", "source", "result". If the result is False, provide an explanation why. If there is no source, put "None" in the "source" field.
Output example:
{"fact_checking":
   [
   {"statement": "In July 2011, BTC-e experienced a security breach.",
   "source": "https://bitcoinmagazine.com/business/btc-e-attacked-1343738085",
   "result": "False",
   "explanation": "BTC-e experienced a security breach in July 2012, not 2011"
   }
   ]}
2. Find all possible spelling mistakes in the text between tags <text></text>. 
For each misspelled word:

- Provide the sentence containing the error
- Provide the incorrect word
- Suggest the correct spelling

Only make corrections for actual spelling errors. Be helpful and point out every spelling error you can find.
Try to look for mistakes only in the text between <text></text> tags. Do not try to correct the preamble.
Output example: 
{"spell_checking": [
   {"context": "The attakers stole my cryptocurrency.", "error": "attakers", "correction": "attackers"}
   ]}
3. Additionally, since the text between <text></text> is a Markdown document for Hugo SSG, ensure it adheres to specific formatting requirements.
Output example:
{"hugo_checking": "False"}

4. Check if the text between <text></text> follows the Markdown format, including appropriate headers.
Confirm if it meets submission guidelines, particularly the file naming convention ("YYYY-MM-DD-entity-that-was-hacked.md"). Extract the name of the file from the text between <text></text> tags and compare it to the correct name.
Verify that the text between <text></text> includes only the allowed headers: "## Summary", "## Attackers", "## Losses", "## Timeline", "## Security Failure Causes".
Check for the presence of specific metadata headers between "---" lines, such as "date", "target-entities", "entity-types", "attack-types", "title", "loss". The text between <text></text> must contain all and only allowed metadata headers.
Present your findings only in a structured JSON format. 
Output example:
{"submission_guidelines": {
       "article_filename": "bla-bla.md",
       "correct_filename": "2012-07-16-BTC-e.md",
       "is_filename_correct": "False",
       "allowed_headers": ["## Summary", "## Attackers", "## Losses", "## Timeline", "## Security Failure Causes"],   
       "headers_from_text": "None",   
       "has_allowed_headers": "False",
       "allowed_metadata_headers": ["date", "target-entities", "entity-types", "attack-types", "title", "loss"],
       "metadata_headers_from_text": "None",
       "has_allowed_metadata_headers": "False"
       }
    }

Combine the results of all steps into a single JSON and return it to me in <answer></answer> tags. 
All quotes in string values must be properly escaped for use with the json.load function in Python. Strictly adhere to the key names.
"""


class ClientWithRetrieval(Anthropic):

    def __init__(self, search_tool: Optional[SearchTool] = None, verbose: bool = True, *args, **kwargs):
        """
        Initializes the ClientWithRetrieval class.
        
        Parameters:
            search_tool (SearchTool): SearchTool object to handle searching
            verbose (bool): Whether to print verbose logging
            *args, **kwargs: Passed to superclass init
        """
        super().__init__(*args, **kwargs)
        self.search_tool = search_tool
        self.verbose = verbose
    
    def extract_statements(self, text: str, model: str, temperature: float = 0.0, max_tokens_to_sample: int = 1000):
        prompt = f"{EXTRACTING_PROMPT} {HUMAN_PROMPT} <text>{text}</text>{AI_PROMPT}"
        completion = self.completions.create(prompt=prompt, model=model, temperature=temperature, max_tokens_to_sample=max_tokens_to_sample).completion
            
        return completion
    

    def retrieve(self,
                       query: str,
                       model: str,
                       n_search_results_to_use: int = 3,
                       stop_sequences: list[str] = [HUMAN_PROMPT],
                       max_tokens_to_sample: int = 1000,
                       max_searches_to_try: int = 5,
                       temperature: float = 1.0) -> str:
        """
        Main method to retrieve relevant search results for a query with a provided search tool.
        
        Constructs RETRIEVAL prompt with query and search tool description. 
        Keeps sampling Claude completions until stop sequence hit.
        
        Returns string with fact-checking results
        """
        assert self.search_tool is not None, "SearchTool must be provided to use .retrieve()"

        description = self.search_tool.tool_description
        statements = self.extract_statements(query, model=model, max_tokens_to_sample=max_tokens_to_sample, temperature=temperature)
        print("Statements:", statements)
        num_of_statements = int(self.extract_between_tags("number_of_statements", statements, strip=True))
        print("num_of_statements:", num_of_statements)
        prompt = f"{RETRIEVAL_PROMPT.format(description=description)}{HUMAN_PROMPT} {statements} {AI_PROMPT}"
        print("Prompt:", prompt)
        token_budget = max_tokens_to_sample
        all_raw_search_results: list[SearchResult] = []
        completions = ""
        for tries in range(num_of_statements):
            partial_completion = self.completions.create(prompt = prompt,
                                                     stop_sequences=stop_sequences + ['</search_query>'],
                                                     model=model,
                                                     max_tokens_to_sample = token_budget,
                                                     temperature = temperature)
            print("Partial completion:", partial_completion.completion)
            completions += partial_completion.completion
            partial_completion, stop_reason, stop_seq = partial_completion.completion, partial_completion.stop_reason, partial_completion.stop # type: ignore
            logger.info(partial_completion)
            token_budget -= self.count_tokens(partial_completion)
            prompt += partial_completion
            if stop_reason == 'stop_sequence' and stop_seq == '</search_query>':
                logger.info(f'Attempting search number {tries}.')
                raw_search_results, formatted_search_results = self._search_query_stop(partial_completion, n_search_results_to_use)
                print("formatted_search_results", formatted_search_results)
                prompt += '</search_query>' + formatted_search_results
                completions += '</search_query>' + formatted_search_results
                all_raw_search_results += raw_search_results
            else:
                break
        print("all_completions:", completions)
        return completions


    def answer_with_results(self, search_results: str, query: str, model: str, temperature: float):
        """Generates an RAG response based on search results and a query. If format_results is True,
           formats the raw search results first. Set format_results to True if you are using this method standalone without retrieve().

        Returns:
            str: Claude's answer to the query
        """
        
        try:
            prompt = f"{HUMAN_PROMPT} {ANSWER_PROMPT%(search_results, query)} {AI_PROMPT}"
        except Exception as e:
            print(str(e))
        
        print("Prompt:", prompt)
        
        try:
            answer = self.completions.create(
                prompt=prompt, 
                model=model, 
                temperature=temperature, 
                max_tokens_to_sample=4000
            ).completion
        except Exception as e:
            answer = str(e)
        
        return answer
    

    def completion_with_retrieval(self,
                                        query: str,
                                        model: str,
                                        n_search_results_to_use: int = 3,
                                        stop_sequences: list[str] = [HUMAN_PROMPT],
                                        max_tokens_to_sample: int = 1000,
                                        max_searches_to_try: int = 5,
                                        temperature: float = 1.0) -> str:
        """
        Gets a final completion from retrieval results        
        
        Calls retrieve() to get search results.
        Calls answer_with_results() with search results and query.
        
        Returns:
            str: Claude's answer to the query
        """
        search_results = self.retrieve(query, model=model,
                                                 n_search_results_to_use=n_search_results_to_use, stop_sequences=stop_sequences,
                                                 max_tokens_to_sample=max_tokens_to_sample,
                                                 max_searches_to_try=max_searches_to_try,
                                                 temperature=temperature)
        print("Search results:", search_results)
        answer = self.answer_with_results(search_results, query, model, temperature)
        print("Answer:", answer)
        json_answer = self.extract_between_tags("answer", answer)
        return json_answer
    

    # Helper methods
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
        return search_results, formatted_search_results
    

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