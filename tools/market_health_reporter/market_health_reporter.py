import openai
from tiktoken import encoding_for_model
import argparse
import json
import os
import requests
import glob
import numpy as np
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
RAG_MAX_ARTICLES = 5
RAG_MAX_CHARS_PER_ARTICLE = 1500


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
        "--cryptopanic-api-key", dest="cryptopanic_api_key", help="CryptoPanic API key", required=False, default=None
    )
    parser.add_argument(
        "--newsapi-key", dest="newsapi_key", help="NewsAPI key", required=False, default=None
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


def fetch_cryptopanic_articles(query: str, api_key: str) -> list:
    """
    Fetch relevant crypto news articles from CryptoPanic API.
    Returns a list of dicts with 'title' and 'body' keys.
    """
    articles = []
    try:
        url = "https://cryptopanic.com/api/v1/posts/"
        params = {
            "auth_token": api_key,
            "kind": "news",
            "filter": "important",
            "public": "true",
        }
        # CryptoPanic doesn't support free-text search, so we filter by currency symbol
        currency = query.split("-")[0].upper() if "-" in query else query.upper()
        params["currencies"] = currency

        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for post in data.get("results", []):
                title = post.get("title", "")
                body = post.get("body") or ""
                if title:
                    articles.append({"title": title, "body": body})
        else:
            print(f"CryptoPanic API returned status {response.status_code}")
    except Exception as e:
        print(f"Error fetching CryptoPanic articles: {e}")
    return articles


def fetch_newsapi_articles(query: str, api_key: str, from_date: str, to_date: str) -> list:
    """
    Fetch relevant news articles from NewsAPI.
    Returns a list of dicts with 'title' and 'body' keys.
    """
    articles = []
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "from": from_date,
            "to": to_date,
            "language": "en",
            "sortBy": "relevancy",
            "pageSize": 20,
            "apiKey": api_key,
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for article in data.get("articles", []):
                title = article.get("title") or ""
                body = article.get("description") or article.get("content") or ""
                if title:
                    articles.append({"title": title, "body": body})
        else:
            print(f"NewsAPI returned status {response.status_code}")
    except Exception as e:
        print(f"Error fetching NewsAPI articles: {e}")
    return articles


def get_embedding(text: str, api_key: str) -> list:
    """
    Get an embedding vector for the given text using OpenAI embeddings.
    """
    openai.api_key = api_key
    text = text.replace("\n", " ").strip()[:8000]
    response = openai.Embedding.create(
        input=[text],
        model="text-embedding-ada-002"
    )
    return response["data"][0]["embedding"]


def cosine_similarity(vec_a: list, vec_b: list) -> float:
    """
    Compute cosine similarity between two vectors.
    """
    a = np.array(vec_a)
    b = np.array(vec_b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def retrieve_relevant_articles(
    marketvenueid: str,
    pairid: str,
    start: str,
    end: str,
    api_key: str,
    cryptopanic_api_key: str = None,
    newsapi_key: str = None,
    top_k: int = RAG_MAX_ARTICLES,
) -> str:
    """
    Fetches articles from available news sources, embeds them alongside a
    query derived from the market context, and returns the top-k most
    relevant articles as a formatted string for RAG augmentation.
    """
    # Build a descriptive query from the market context
    base_currency = pairid.split("-")[0].upper() if "-" in pairid else pairid.upper()
    query_text = (
        f"{base_currency} {marketvenueid} cryptocurrency market trading volume "
        f"price anomaly spike {start} {end}"
    )

    all_articles = []

    if cryptopanic_api_key:
        cp_articles = fetch_cryptopanic_articles(pairid, cryptopanic_api_key)
        print(f"Fetched {len(cp_articles)} articles from CryptoPanic")
        all_articles.extend(cp_articles)

    if newsapi_key:
        newsapi_articles = fetch_newsapi_articles(
            f"{base_currency} {marketvenueid}", newsapi_key, start, end
        )
        print(f"Fetched {len(newsapi_articles)} articles from NewsAPI")
        all_articles.extend(newsapi_articles)

    if not all_articles:
        print("No external articles fetched for RAG context.")
        return ""

    print(f"Computing embeddings for {len(all_articles)} articles...")
    query_embedding = get_embedding(query_text, api_key)

    scored = []
    for article in all_articles:
        combined_text = f"{article['title']}. {article['body']}"
        try:
            article_embedding = get_embedding(combined_text, api_key)
            score = cosine_similarity(query_embedding, article_embedding)
            scored.append((score, article))
        except Exception as e:
            print(f"Error embedding article '{article['title']}': {e}")

    scored.sort(key=lambda x: x[0], reverse=True)
    top_articles = scored[:top_k]

    if not top_articles:
        return ""

    formatted_parts = []
    for rank, (score, article) in enumerate(top_articles, start=1):
        title = article["title"]
        body = article["body"][:RAG_MAX_CHARS_PER_ARTICLE]
        formatted_parts.append(f"[Article {rank}] {title}\n{body}")

    rag_context = "\n\n".join(formatted_parts)
    print(f"RAG context built from {len(top_articles)} articles.")
    return rag_context


def create_prompt(article_example: str, data: dict, human_prompt_content: str, rag_context: str = "") -> str:
    """
    Creates a prompt string using article example, data, and optional RAG context.
    """
    rag_section = ""
    if rag_context:
        rag_section = f"\n<context>\n{rag_context}\n</context>\n"
    return f"<example> {article_example} </example>\n{human_prompt_content}{rag_section}\n<data> {json.dumps(data)} </data>"


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

        # RAG: retrieve relevant articles to augment the prompt with external context
        rag_context = retrieve_relevant_articles(
            marketvenueid=marketvenueid,
            pairid=pairid,
            start=start,
            end=end,
            api_key=args.API_key,
            cryptopanic_api_key=args.cryptopanic_api_key,
            newsapi_key=args.newsapi_key,
        )

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
