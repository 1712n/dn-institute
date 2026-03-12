import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config import MARKET_HEALTH_API_URL, OPENAI_MODEL, REPORTS_DIR, RAG_CONFIG

load_dotenv()


    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.ensure_reports_dir()
        self.rag_system = RAGSystem()
    
    def ensure_reports_dir(self):
        """Ensure reports directory exists"""
MAX_TOKENS = 125000


def parse_cli_args():
    """
    Parse CLI arguments.
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
        """Generate a comprehensive report for a given exchange"""
        metrics = self.get_exchange_metrics(exchange)
        spikes = self.identify_spikes(metrics)
        context = self.rag_system.retrieve_relevant_context(exchange, spikes)
        
        if not spikes:
            print(f"No significant spikes found for {exchange}")
        file_number = max(numbers, default=0) + 1
        
        print(f"Found {len(spikes)} significant spikes for {exchange}")
        
        report_content = self.generate_report_content(exchange, spikes, metrics, context)
        self.save_report(exchange, report_content)
        
        return report_content


def save_data(data: str, directory: str, marketvenueid: str, pairid: str, start: str, end: str) -> None:
    """
    Saves data to a JSON file in the specified directory.
    """
    new_file_name = f'{directory}{marketvenueid}_{pairid}_{start.replace(":", "-")}_{end.replace(":", "-")}.json'
    with open(new_file_name, 'w', encoding='utf-8') as file:
        file.write(data)


        
        return spikes
    
    def generate_report_content(self, exchange: str, spikes: List[Dict], metrics: Dict, context: str) -> str:
        """Generate the actual report content using OpenAI"""
        
        spike_descriptions = []
    return matching_files[0] if matching_files else None


def fetch_or_load_market_data(querystring: dict, headers: dict, url: str, directory: str, marketvenueid: str, pairid: str, start: str, end: str) -> dict:
    """
    Tries to load market data from a file if it is already saved.
    Otherwise, makes an API request and saves the data.
    """
        prompt = f"""
        You are a crypto market analyst writing a report about {exchange}.
        
        Context from recent news and analysis: {context}
        The following significant metric spikes were detected:
        {spike_descriptions}
        
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        Write a professional market health report that:
        1. Explains what these spikes mean for the exchange
        2. Provides context about why these changes might have occurred
        3. References relevant external events or news when appropriate
        3. Assesses the overall health and stability of the exchange
        4. Follows the structure and style of crypto news articles
        
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
        with open(filename, 'w') as f:
            f.write(content)
        
        print(f"Report saved to {filename}")


class RAGSystem:
    """Retrieval Augmented Generation system for market context 🌰"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.cache = {}
        
    def retrieve_relevant_context(self, exchange: str, spikes: List[Dict]) -> str:
        """Retrieve relevant context for given exchange and spikes"""
        cache_key = f"{exchange}_{hash(str(spikes))}"
        
        # Check cache first 🌰
        if cache_key in self.cache:
            cache_time, cached_context = self.cache[cache_key]
            if datetime.now() - cache_time < timedelta(seconds=RAG_CONFIG["cache_ttl"]):
                return cached_context
        
        # Build search queries from spikes
        queries = self._build_queries(exchange, spikes)
        
        # For now, simulate external data retrieval
        # In production, this would fetch from news APIs, research reports, etc.
        external_docs = self._fetch_external_documents(queries)
        
        if not external_docs:
            return "No additional external context available for this analysis."
        
        # Create vector store and retrieve relevant chunks
        documents = [Document(page_content=doc) for doc in external_docs]
        splits = self.text_splitter.split_documents(documents)
        
        if not splits:
            return "No relevant context found in external sources."
        
        self.vector_store = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings
        )
        
        # Retrieve most relevant context
        relevant_context = []
        for query in queries:
            docs = self.vector_store.similarity_search(
                query, 
                k=RAG_CONFIG["max_retrieved_docs"]
            )
            for doc in docs:
                if doc.page_content not in relevant_context:
                    relevant_context.append(doc.page_content)
        
        context_str = "\n\n".join(relevant_context[:3])  # Limit to top 3 contexts
        
        # Cache the result
        self.cache[cache_key] = (datetime.now(), context_str)
        
        return context_str
    
    def _build_queries(self, exchange: str, spikes: List[Dict]) -> List[str]:
        """Build search queries from exchange and spike data"""
        queries = [f"{exchange} exchange news", f"{exchange} market analysis"]
        
        for spike in spikes:
            metric = spike.get("metric", "")
            if "volume" in metric.lower():
                queries.append(f"{exchange} trading volume spike")
            elif "price" in metric.lower():
                queries.append(f"{exchange} price movement")
            elif "liquidity" in metric.lower():
                queries.append(f"{exchange} liquidity issues")
            elif "withdrawal" in metric.lower():
                queries.append(f"{exchange} withdrawal problems")
        
        return queries
    
    def _fetch_external_documents(self, queries: List[str]) -> List[str]:
        """Fetch relevant documents from external sources (simulated for now)"""
        # In production, this would integrate with news APIs, research platforms, etc.
        # For now, return simulated relevant content
        return [
            "Recent regulatory developments have increased scrutiny on major exchanges, leading to enhanced compliance measures and temporary trading restrictions.",
            "Market makers have reported reduced liquidity across several exchanges due to ongoing market volatility and risk management adjustments.",
            "Several exchanges have implemented new KYC requirements affecting withdrawal processing times and user experience metrics."
        ]
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