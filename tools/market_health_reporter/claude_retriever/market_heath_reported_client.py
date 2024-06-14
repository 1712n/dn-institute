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
from tools.python_modules.utils import read_file, extract_between_tags
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



EXTRACTING_INDICATORS_PROMPT = """
Identify and extract key performance indicators (KPIs) analyzed in the text provided.
Return the extracted KPIs. Place each KPI within <kpi></kpi> tags.
Also, return the number of extracted KPIs within <number_of_kpis></number_of_kpis> tags.
Focus on extracting KPIs that involve numerical data, statistical analysis, and named metrics. Limit the number of extracted KPIs to the most significant ones.
Skip any introductory text; proceed directly to the results.
"""

RETRIEVAL_PROMPT = """
You are tasked with collecting information from an external knowledge base that is pertinent to a list of terms related to the cryptocurrency market. 
Below is the search engine's description: <tool_description>{description}</tool_description>.

Here's how to proceed:
1. Within <thinking></thinking> tags, consider the type of information necessary to understand each term.
2. Use the search engine tool by placing your query inside <search_query> tags: <search_query>your specific query here</search_query>.
3. Review the results returned within <search_result></search_result> tags.
4. Reflect on the completeness of the information using <search_quality></search_quality> tags.

Your role is not to analyze the terms but to compile relevant information that will enable the user to conduct the analysis.

For each term, provide a description of the gathered information within <description></description> tags to emphasize its relevance to the analysis of that particular cryptocurrency market term.

Here is the list of terms: <kpi>{list of terms}</kpi>
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
        output_subdir = os.path.join(directory, f"{start}-{end}-{marketvenueid}-{pairid}")  
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


    def extract_kpis(self, text: str, model: str, temperature: float = 0.0, max_tokens: int = 1000):
        
        """
        Extracts indicators from the example article that may be important for analysis
        """
        
        message = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=EXTRACTING_INDICATORS_PROMPT,
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
        kpis = self.extract_between_tags("kpi", message.content[0].text)
        number_of_kpis = self.extract_between_tags("number_of_kpis", message.content[0].text)
        return kpis, number_of_kpis

    def retrieve(self, example_article: str, model: str, n_search_results_to_use: int = 3, stop_sequences: list[str] = [], max_tokens: int = 1000, max_searches_to_try: int = 5, temperature: float = 0.0) -> str:
        """
        Main method to retrieve relevant search results for indicators with a provided search tool.

        Extracts KPIs from the provided article and retrieves information relevant to these KPIs using a search tool.

        Returns string with fact-checking results.
        """
        assert self.search_tool is not None, "SearchTool must be provided to use .retrieve()"

        kpis, number_of_kpis = self.extract_kpis(example_article, model=model, max_tokens=max_tokens, temperature=temperature)
        completions = ""
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": kpis
                    }
                ]
            }
        ]
        

        for tries in range(min(number_of_kpis, max_searches_to_try)):
            message = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=RETRIEVAL_PROMPT,
                messages=messages,
                stop_sequences=stop_sequences
            )

            partial_completion, stop_reason, stop_seq = message.content[0].text, message.stop_reason, message.stop_sequence
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
                                  model: str,
                                  comment_body: str,
                                  headers: dict,
                                  n_search_results_to_use: int = 3,
                                  stop_sequences: list[str] = [],
                                  max_tokens: int = 1000,
                                  max_searches_to_try: int = 5,
                                  temperature: float = 0.0) -> str:
        """
        Gets a final completion from retrieval results        
        
        Calls retrieve() to get search results.
        Calls answer_with_results() with search results, article example, human_prompt and json data.
        
        Returns:
            str: Claude's answer to the query
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
            data = self.fetch_or_load_market_data(querystring, headers, url, DATA_DIR, marketvenueid, pairid, start, end)
        except Exception as e:
            print(f"Error occurred: {e}")

        search_results = self.retrieve(article_example, model=model,
                                       n_search_results_to_use=n_search_results_to_use, stop_sequences=stop_sequences,
                                       max_tokens=max_tokens,
                                       max_searches_to_try=max_searches_to_try,
                                       temperature=temperature)


        combined_prompt = self.create_prompt(article_example, data, ANSWER_PROMPT, search_results)
        answer = self.answer_with_results(combined_prompt, model, temperature)
        answer='<article>this is answer, wow</article>'
        answer = self.extract_between_tags("article", answer)
        self.save_output(answer, OUTPUT_DIR, marketvenueid, pairid, start, end)
        vis = Visualization()
        output_subdir = os.path.join(OUTPUT_DIR, f"{start}-{end}-{marketvenueid}-{pairid}") 
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