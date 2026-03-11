import openai
from tiktoken import encoding_for_model
import argparse
import json
import os
import requests
import glob
from bs4 import BeautifulSoup
from github import Github
from tools.python_modules.utils import read_file, extract_between_tags
from tools.python_modules.report_graphics_tool import Visualization


REPO_NAME = "1712n/dn-institute"
SYSTEM_PROMPT_FILE = 'tools/market_health_reporter/doc/prompts/system_prompt.txt'
HUMAN_PROMPT_FILE = 'tools/market_health_reporter/doc/prompts/prompt1.txt'
ARTICLE_EXAMPLE_FILE = 'content/market-health/posts/2023-08-14-huobi/index.md'
OUTPUT_DIR = 'content/market-health/posts/'
DATA_DIR = 'tools/market_health_reporter/doc/data/'
MAX_TOKENS = 125000
MAX_CONTEXT_TOKENS = 8000  # max tokens reserved for RAG context
CRYPTOPANIC_API_URL = "https://cryptopanic.com/api/v1/posts/"
NEWSAPI_URL = "https://newsapi.org/v2/everything"


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
    parser.add_argument(
        "--cryptopanic-api-key", dest="cryptopanic_api_key", help="CryptoPanic API key", required=False, default=""
    )
    parser.add_argument(
        "--newsapi-key", dest="newsapi_key", help="NewsAPI key", required=False, default=""
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


def save_data(data: str, directory: str, marketvenueid: str, pairid: str, start: str, end: str) -> None:
    """
    Saves data to a JSON file in the specified directory.
    """
    new_file_name = f'{directory}{marketvenueid}_{pairid}_{start.replace(":", "-")}_{end.replace(":", "-")}.json'
    with open(new_file_name, 'w', encoding='utf-8') as file:
        file.write(data)


def file_exists(directory: str, marketvenueid: str, pairid: str, start: str, end: str) -> str:
    """
    Checks if a file with the specified parameters exists.
    Returns the path to the file if found, otherwise returns None.
    """
    pattern = f"{directory}/{marketvenueid}_{pairid}_{start.replace(':', '-')}_{end.replace(':', '-')}.json"
    matching_files = glob.glob(pattern)
    return matching_files[0] if matching_files else None


def fetch_or_load_market_data(querystring: dict, headers: dict, url: str, directory: str, marketvenueid: str, pairid: str, start: str, end: str) -> dict:
    """
    Tries to load market data from a file if it is already saved.
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


def extract_text_from_html(html_content: str) -> str:
    """
    Extracts plain text from HTML content using BeautifulSoup.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    # Remove script and style elements
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator=' ', strip=True)
    # Collapse whitespace
    text = ' '.join(text.split())
    return text


def fetch_article_text(url: str, max_chars: int = 2000) -> str:
    """
    Fetches and extracts plain text from an article URL.
    Returns up to max_chars characters of content.
    """
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        text = extract_text_from_html(response.text)
        return text[:max_chars]
    except Exception as e:
        print(f"Could not fetch article text from {url}: {e}")
        return ""


def fetch_cryptopanic_news(marketvenueid: str, pairid: str, api_key: str, max_articles: int = 5) -> list:
    """
    Fetches relevant news articles from CryptoPanic API for a given market venue and pair.
    Returns a list of dicts with title, url, and body.
    """
    if not api_key:
        print("No CryptoPanic API key provided, skipping.")
        return []

    # Build a search query from the venue and pair
    currency = pairid.split('-')[0].upper() if '-' in pairid else pairid.upper()
    params = {
        "auth_token": api_key,
        "currencies": currency,
        "public": "true",
        "kind": "news",
    }
    try:
        response = requests.get(CRYPTOPANIC_API_URL, params=params, timeout=10)
        response.raise_for_status()
        results = response.json().get("results", [])
        articles = []
        for item in results[:max_articles]:
            article = {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "body": ""
            }
            if article["url"]:
                article["body"] = fetch_article_text(article["url"])
            articles.append(article)
        print(f"Fetched {len(articles)} articles from CryptoPanic for {currency}.")
        return articles
    except Exception as e:
        print(f"CryptoPanic fetch error: {e}")
        return []


def fetch_newsapi_articles(marketvenueid: str, pairid: str, api_key: str, start: str, end: str, max_articles: int = 5) -> list:
    """
    Fetches relevant news articles from NewsAPI for a given market venue and pair.
    Returns a list of dicts with title, url, and body.
    """
    if not api_key:
        print("No NewsAPI key provided, skipping.")
        return []

    currency = pairid.split('-')[0].upper() if '-' in pairid else pairid.upper()
    query = f"{marketvenueid} {currency}"
    params = {
        "q": query,
        "from": start,
        "to": end,
        "language": "en",
        "sortBy": "relevancy",
        "apiKey": api_key,
        "pageSize": max_articles,
    }
    try:
        response = requests.get(NEWSAPI_URL, params=params, timeout=10)
        response.raise_for_status()
        results = response.json().get("articles", [])
        articles = []
        for item in results[:max_articles]:
            article = {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "body": item.get("description", "") or ""
            }
            # Fetch full article text if body is short
            if article["url"] and len(article["body"]) < 300:
                article["body"] = fetch_article_text(article["url"])
            articles.append(article)
        print(f"Fetched {len(articles)} articles from NewsAPI for '{query}'.")
        return articles
    except Exception as e:
        print(f"NewsAPI fetch error: {e}")
        return []


def compute_keyword_score(text: str, keywords: list) -> int:
    """
    Simple keyword-based relevance scoring: counts how many keywords appear in the text.
    """
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw.lower() in text_lower)


def retrieve_relevant_articles(articles: list, keywords: list, top_k: int = 3) -> list:
    """
    Ranks articles by keyword relevance and returns the top_k most relevant ones.
    This acts as a lightweight semantic search / retrieval step.
    """
    scored = []
    for article in articles:
        combined_text = f"{article.get('title', '')} {article.get('body', '')}"
        score = compute_keyword_score(combined_text, keywords)
        scored.append((score, article))
    scored.sort(key=lambda x: x[0], reverse=True)
    # Return only articles with at least one keyword match
    return [article for score, article in scored[:top_k] if score > 0]


def build_rag_context(articles: list, encoding, max_tokens: int = MAX_CONTEXT_TOKENS) -> str:
    """
    Builds a RAG context string from retrieved articles, truncated to max_tokens.
    """
    if not articles:
        return ""
    context_parts = []
    total_tokens = 0
    for article in articles:
        title = article.get("title", "")
        body = article.get("body", "")
        url = article.get("url", "")
        snippet = f"Title: {title}\nSource: {url}\nContent: {body}"
        snippet_tokens = len(encoding.encode(snippet))
        if total_tokens + snippet_tokens > max_tokens:
            # Truncate the snippet to fit
            remaining = max_tokens - total_tokens
            if remaining > 50:
                tokens = encoding.encode(snippet)[:remaining]
                snippet = encoding.decode(tokens)
            else:
                break
        context_parts.append(snippet)
        total_tokens += snippet_tokens
    return "\n\n---\n\n".join(context_parts)


def create_prompt(article_example: str, data: dict, human_prompt_content: str, rag_context: str = "") -> str:
    """
    Creates a prompt string using article example, data, and optional RAG context.
    """
    base_prompt = f"<example> {article_example} </example>\n{human_prompt_content}\n<data> {json.dumps(data)} </data>"
    if rag_context:
        base_prompt += f"\n<context>\nThe following recent news articles provide additional context about the market venue and trading pair. Use this information to enrich your analysis where relevant:\n\n{rag_context}\n</context>"
    return base_prompt


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

        # RAG: fetch news articles from CryptoPanic and NewsAPI
        cryptopanic_articles = fetch_cryptopanic_news(
            marketvenueid, pairid, args.cryptopanic_api_key, max_articles=5
        )
        newsapi_articles = fetch_newsapi_articles(
            marketvenueid, pairid, args.newsapi_key, start, end, max_articles=5
        )
        all_articles = cryptopanic_articles + newsapi_articles

        # Build keywords for retrieval from venue and pair
        currency = pairid.split('-')[0].upper() if '-' in pairid else pairid.upper()
        keywords = [marketvenueid, currency, pairid, "market", "trading", "volume", "liquidity"]
        relevant_articles = retrieve_relevant_articles(all_articles, keywords, top_k=3)
        print(f"Retrieved {len(relevant_articles)} relevant articles for RAG context.")

        rag_context = build_rag_context(relevant_articles, encoding, max_tokens=MAX_CONTEXT_TOKENS)

        prompt = create_prompt(article_example, data, human_prompt_content, rag_context)
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
