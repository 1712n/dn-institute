import os
from typing import Optional, Tuple
import anthropic
from searcher.types import SearchTool, SearchResult, Tool
import logging
import re
from utils import format_results_full
import json
import glob
import requests
from tools.python_modules.utils import read_file
from tools.python_modules.report_graphics_tool import Visualization


ARTICLE_EXAMPLE_FILE = 'content/market-health/posts/2023-08-14-huobi/index.md'
OUTPUT_DIR = 'content/market-health/posts/'
DATA_DIR = 'tools/market_health_reporter/doc/data/'
SYSTEM_PROMPT_FILE = 'tools/market_health_reporter/doc/prompts/system_prompt.txt'
HUMAN_PROMPT_FILE = 'tools/market_health_reporter/doc/prompts/prompt1.txt'
MAX_TOKENS = 125000
SYSTEM_PROMPT = read_file(SYSTEM_PROMPT_FILE)
ANSWER_PROMPT = read_file(HUMAN_PROMPT_FILE)
article_example = read_file(ARTICLE_EXAMPLE_FILE)
logger = logging.getLogger(__name__)

RETRIEVAL_PROMPT = """

Your task is to collect information from an external knowledge base that is relevant to the state of a particular pair of cryptocurrencies on a particular market for a defined period of time.
Below is the search engine's description: <tool_description>{description}</tool_description>.

Here's how to proceed:
1. Formulate a query to search for information about the state of the specified market and cryptocurrency pair, including significant events that occurred during the specified period which could have influenced the market status. 
2. Execute the search using the search engine tool by placing your query inside <search_query> tags: <search_query>your query here</search_query>.
3. Tag the information found with <description>information</description> and include the source web page URL in <source>url</source> tags. If there is no URL, insert 'None' in the <source></source> tags.
4. If a new search is necessary, place the new query within {search_query}{/search_query}.

Your role is to compile the relevant information that will assist the user in analyzing the market data, not to analyze the data yourself. The information that you put in the <description> tags will be utilized in the subsequent prompt for market surveillance analysis. Ensure that the collected data is concise and relevant to enable effective integration into the analysis process.

Information to be retrieved: <market_data>marketvenueid: {marketvenueid}, pairid: {pairid}, start: {start}, end: {end}</market_data>"""

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

    def extract_data_from_comment(self, comment: str) -> tuple:
        """
        Extract data from the comment.
        """
        parts = comment.split(',')
        marketvenueid = parts[1].strip().lower()
        pairid = parts[0].split(':')[1].strip().lower()  
        start, end = parts[2].strip(), parts[3].strip()
        return marketvenueid, pairid, start, end
    
    def save_data(data: str, directory: str, marketvenueid: str, pairid: str, start: str, end: str) -> None:
        """
        Saves data to a JSON file in the specified directory.
        """
        new_file_name = f'{directory}{marketvenueid}_{pairid}_{start.replace(":", "-")}_{end.replace(":", "-")}.json'
        with open(new_file_name, 'w', encoding='utf-8') as file:
            file.write(data)


    def file_exists(self, directory: str, marketvenueid: str, pairid: str, start: str, end: str) -> str:
        """
        Checks if a file with the specified parameters exists.
        Returns the path to the file if found, otherwise returns None.
        """
        pattern = f"{directory}/{marketvenueid}_{pairid}_{start.replace(':', '-')}_{end.replace(':', '-')}.json"
        matching_files = glob.glob(pattern)
        return matching_files[0] if matching_files else None

    def fetch_or_load_market_data(self, querystring: dict, headers: dict, url: str, directory: str, marketvenueid: str, pairid: str, start: str, end: str) -> dict:
        """
        Tries to load market data from a file if it is already saved.
        Otherwise, makes an API request and saves the data.
        """
        existing_file = self.file_exists(directory, marketvenueid, pairid, start, end)
        if existing_file:
            print(f"Loading data from existing file: {existing_file}")
            with open(existing_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        else:
            response = requests.get(url, headers=headers, params=querystring)
            response.raise_for_status()
            data = response.json()
            self.save_data(json.dumps(data), directory, marketvenueid, pairid, start, end)
            return data

    def save_output(self, output: str, directory: str, marketvenueid: str, pairid: str, start: str, end: str) -> None:
        """
        Saves the output to a markdown file in the specified directory, creating a subdirectory for it.
        """
        safe_start = start.replace(":", "-")
        safe_end = end.replace(":", "-")
        output_subdir = os.path.join(directory, f"{safe_start}-{safe_end}-{marketvenueid}-{pairid}")
        os.makedirs(output_subdir, exist_ok=True)
        safe_start = start.replace(":", "-")
        safe_end = end.replace(":", "-")
        base_file_name = "index"
        file_path = os.path.join(output_subdir, base_file_name)  
        
        existing_files = glob.glob(f"{file_path}*.md")
        if existing_files:
            numbers = [int(file_name.split('-')[-1].split('.md')[0]) for file_name in existing_files if file_name.split('-')[-1].split('.md')[0].isdigit()]
            file_number = max(numbers, default=0) + 1
            full_path = f"{file_path}-{file_number}.md"
        else:
            full_path = f"{file_path}.md"
        
        with open(full_path, 'w', encoding='utf-8') as file:
            file.write(output)
        print(f"Output saved to: {full_path}")


    def create_prompt(self, article_example: str, data: dict, human_prompt_content: str, search_results: str) -> str:
        """
        Creates a prompt string using article example, data, and search results.
        """
        return f"<example> {article_example} </example>\n<search_results> {search_results} </search_results>\n{human_prompt_content}\n<data> {json.dumps(data)} </data>"

    def retrieve(self, model: str, marketvenueid: str, pairid: str, start: str, end: str,
                 n_search_results_to_use: int = 3, stop_sequences: list[str] = [], max_tokens: int = 1000,
                 max_searches_to_try: int = 5, temperature: float = 0.0) -> str:
        """
        Retrieves relevant market data for the given marketvenueid and pairid over the specified time period.

        Returns a string with the search results.
        """
        assert self.search_tool is not None, "SearchTool must be provided to use retrieve()"
        completions = ""
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"marketvenueid: {marketvenueid}, pairid: {pairid}, start: {start}, end: {end}"
                    }
                ]
            }
        ]

        for tries in range(max_searches_to_try):
            message = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=RETRIEVAL_PROMPT,
                messages=messages,
                stop_sequences=stop_sequences
            )

            partial_completion, stop_reason, stop_seq = message.content[
                0].text, message.stop_reason, message.stop_sequence
            completions += partial_completion
            messages[0]['content'][0]['text'] += partial_completion
            
            if stop_reason == 'stop_sequence' and stop_seq in stop_sequences:
                logger.info(f'Attempting search number {tries}.')
                search_query = partial_completion.strip('<search_query>').strip('</search_query>')
                formatted_search_results = self.search_tool.search(search_query, n_search_results_to_use)
                completions += formatted_search_results
                messages[0]['content'][0]['text'] += formatted_search_results
            else:
                break

        return completions

    def answer_with_results(self, prompt: str, model: str, temperature: float, max_tokens: int = 4000):
        """
        Generates an article using all the data provided
        """
        try:
            message = self.client.messages.create(
                model=model,
                temperature=temperature,
                system=SYSTEM_PROMPT,
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
            answer = str(e)
        return answer

    def completion_with_retrieval(self,
                                  model: str,
                                  comment_body: str,
                                  headers: dict,
                                  n_search_results_to_use: int = 3,
                                  stop_sequences: list[str] = [],
                                  max_tokens: int = 1000,
                                  max_searches_to_try: int = 5,
                                  temperature: float = 0.0) -> str:
        """
        Gets a final completion from market data retrieval results.

        Calls retrieve() to get search results.
        Uses the retrieved data to write an article analyzing the input data.

        Returns:
            str: The final article.
        """

        marketvenueid, pairid, start, end = self.extract_data_from_comment(comment_body)
        print(f"Marketvenueid: {marketvenueid}, Pairid: {pairid}, Start: {start}, End: {end}")
        querystring = {
            "marketvenueid": marketvenueid,
            "pairid": pairid,
            "start": f"{start}T00:00:00",
            "end": f"{end}T00:00:00",
            "gran": "1h",
            "sort": "asc",
            "limit": "1000"
        }

        url = "https://cross-market-surveillance.p.rapidapi.com/metrics/wt/market"
        try:
            data = self.fetch_or_load_market_data(querystring, headers, url, DATA_DIR, marketvenueid, pairid, start,
                                                  end)
        except Exception as e:
            print(f"Error occurred while loading market data: {e}")
        search_results = self.retrieve(model=model,
                                       marketvenueid=marketvenueid,
                                       pairid=pairid,
                                       start=start,
                                       end=end,
                                       n_search_results_to_use=n_search_results_to_use,
                                       stop_sequences=stop_sequences,
                                       max_tokens=max_tokens,
                                       max_searches_to_try=max_searches_to_try,
                                       temperature=temperature)

        combined_prompt = self.create_prompt(article_example, data, ANSWER_PROMPT, search_results)
        answer = self.answer_with_results(combined_prompt, model, temperature)
        answer = self.extract_between_tags("article", answer)
        self.save_output(answer, OUTPUT_DIR, marketvenueid, pairid, start, end)
        vis = Visualization()
        safe_start = start.replace(":", "-")
        safe_end = end.replace(":", "-")
        output_subdir = os.path.join(OUTPUT_DIR, f"{safe_start}-{safe_end}-{marketvenueid}-{pairid}")
        vis.generate_report(data, output_subdir)

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