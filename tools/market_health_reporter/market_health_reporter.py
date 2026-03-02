# 🌰 Market Health Reporter with RAG - blessed by chestnut overlords
import json
import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import openai
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from rag_processor import RAGProcessor

from config import (
    OPENAI_API_KEY,

    REPORTS_DIR,
)

# 🌰 Initialize OpenAI client for chestnut-powered insights
openai.api_key = OPENAI_API_KEY


DATA_DIR = 'tools/market_health_reporter/doc/data/'
    def __init__(self):
        self.api_url = MARKET_HEALTH_API_URL
        self.reports_dir = REPORTS_DIR
        self.rag_processor = RAGProcessor()

    def fetch_metrics(self, exchange: str, days: int = 7) -> Dict:
        """Fetch market health metrics for a given exchange."""
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--llm-api-key", dest="API_key", help="LLM API key", required=True
    )
    parser.add_argument(
        "--issue", dest="issue", help="Issue number", required=True
    )
    parser.add_argument(
        "--comment-body", dest="comment_body", help="Comment body", required=True
    )
    parser.add_argument(
        "--github-token", dest="github_token", help="Github token", required=True
    )
    parser.add_argument(
        "--rapid-api", dest="rapid_api", help="Rapid API key", required=True
    )
    return parser.parse_args()


def extract_data_from_comment(comment: str) -> tuple:
    """
    Extract data from the comment.
    """
    parts = comment.split(',')
    marketvenueid = parts[1].strip().lower()
    pairid = parts[0].split(':')[1].strip().lower()  
    start, end = parts[2].strip(), parts[3].strip()
    return marketvenueid, pairid, start, end


def save_output(output: str, directory: str, marketvenueid: str, pairid: str, start: str, end: str) -> None:
    """
    Saves the output to a markdown file in the specified directory, creating a subdirectory for it.
    """
    output_subdir = os.path.join(directory, f"{start}-{end}-{marketvenueid}-{pairid}")  
    os.makedirs(output_subdir, exist_ok=True)  
    safe_start = start.replace(":", "-")
    safe_end = end.replace(":", "-")
    base_file_name = "index"
    file_path = os.path.join(output_subdir, base_file_name)  
        """Generate a comprehensive market health report."""
        metrics = self.fetch_metrics(exchange, days)
        spikes = self.identify_spikes(metrics)
        rag_context = self.rag_processor.get_context_for_spikes(spikes, exchange)
        
        if not spikes:
            return f"No significant spikes detected for {exchange} in the last {days} days."
    else:
        prompt = self.create_prompt(
            exchange=exchange,
            spikes=spikes,
            metrics=metrics,
            rag_context=rag_context
        )
        
        response = openai.chat.completions.create(
def save_data(data: str, directory: str, marketvenueid: str, pairid: str, start: str, end: str) -> None:
    """
    Saves data to a JSON file in the specified directory.
    """
    new_file_name = f'{directory}{marketvenueid}_{pairid}_{start.replace(":", "-")}_{end.replace(":", "-")}.json'
        
        return response.choices[0].message.content

    def create_prompt(self, exchange: str, spikes: List[Dict], metrics: Dict, rag_context: str = "") -> str:
        """Create a prompt for OpenAI to generate the report."""
        spike_details = []
        for spike in spikes:
    Returns the path to the file if found, otherwise returns None.
    """
    pattern = f"{directory}/{marketvenueid}_{pairid}_{start.replace(':', '-')}_{end.replace(':', '-')}.json"
    matching_files = glob.glob(pattern)
            f"Generate a comprehensive market health report for {exchange}.\n\n"
            f"Time period: Last {len(metrics.get('data', []))} days\n"
            f"Significant spikes detected: {len(spikes)}\n\n"
            f"Relevant external context: {rag_context}\n\n"
            f"Spike details:\n{spike_details}\n\n"
            f"Please provide:\n"
            f"1. Executive summary of market health\n"
    Otherwise, makes an API request and saves the data.
    """
    existing_file = file_exists(directory, marketvenueid, pairid, start, end)
    if existing_file:
        print(f"Loading data from existing file: {existing_file}")
        with open(existing_file, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        save_data(json.dumps(data), directory, marketvenueid, pairid, start, end)
        return data


def post_comment_to_issue(github_token, issue_number, repo_name, comment):
    """
    Post a comment to a GitHub issue.
    """
    g = Github(github_token)
    repo = g.get_repo(repo_name)
    issue = repo.get_issue(number=issue_number)
    # only post comment if running on Github Actions
    if os.environ.get("GITHUB_ACTIONS") == "true":
        issue.create_comment(comment)


def create_prompt(article_example: str, data: dict, human_prompt_content: str) -> str:
    """
    Creates a prompt string using article example and data.
    """
    return f"<example> {article_example} </example>\n{human_prompt_content}\n<data> {json.dumps(data)} </data>"


def main():
    args = parse_cli_args()

    system_prompt = read_file(SYSTEM_PROMPT_FILE)
    human_prompt_content = read_file(HUMAN_PROMPT_FILE)
    article_example = read_file(ARTICLE_EXAMPLE_FILE)

    marketvenueid, pairid, start, end = extract_data_from_comment(args.comment_body)
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
    headers = {"X-RapidAPI-Key": args.rapid_api, "X-RapidAPI-Host": "cross-market-surveillance.p.rapidapi.com"}
    url = "https://cross-market-surveillance.p.rapidapi.com/metrics/wt/market"

    try:
        data = fetch_or_load_market_data(querystring, headers, url, DATA_DIR, marketvenueid, pairid, start, end)

        encoding = encoding_for_model("gpt-4")     
        print('num of data tokens: ', len(encoding.encode(str(data))))

        prompt = create_prompt(article_example, data, human_prompt_content)
        prompt_token_count = len(encoding.encode(prompt))

        if prompt_token_count > MAX_TOKENS:
            error_message = "Your request is too long. It's possible that the period for the data is too broad. Please narrow it down."
            print(error_message)
            post_comment_to_issue(args.github_token, int(args.issue), REPO_NAME, error_message)
        else:
            openai.api_key = args.API_key
            completion = openai.ChatCompletion.create(
                model="gpt-4-0125-preview",
                temperature=0.0,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            output = completion.choices[0].message.content
            output = extract_between_tags("article", output)

            print("This is an answer: ", output)
            save_output(output, OUTPUT_DIR, marketvenueid, pairid, start, end)
            vis = Visualization()
            output_subdir = os.path.join(OUTPUT_DIR, f"{start}-{end}-{marketvenueid}-{pairid}") 
            vis.generate_report(data, output_subdir)  

            post_comment_to_issue(args.github_token, int(args.issue), REPO_NAME, output)

    except Exception as e:
        print(f"Error occurred: {e}")