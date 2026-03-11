import openai
from tiktoken import encoding_for_model
import argparse
import json
import os
import requests
import glob
import re
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
RAG_MAX_TOKENS = 4000  # 🌰 max tokens reserved for RAG context
RAG_TOP_K = 3         # 🌰 number of top articles to retrieve


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
        "--cohere-api-key", dest="cohere_api_key", help="Cohere API key for RAG embeddings", required=False, default=None
    )
    parser.add_argument(
        "--cryptopanic-api-key", dest="cryptopanic_api_key", help="CryptoPanic API key for news fetching", required=False, default=None
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


def create_prompt(article_example: str, data: dict, human_prompt_content: str, rag_context: str = "") -> str:
    """
    Creates a prompt string using article example, data, and optional RAG context. 🌰
    """
    if rag_context:
        return (
            f"<example> {article_example} </example>\n"
            f"{human_prompt_content}\n"
            f"<context> {rag_context} </context>\n"
            f"<data> {json.dumps(data)} </data>"
        )
    return f"<example> {article_example} </example>\n{human_prompt_content}\n<data> {json.dumps(data)} </data>"


# ---------------------------------------------------------------------------
# 🌰 RAG helpers
# ---------------------------------------------------------------------------

def _clean_text(raw: str) -> str:
    """Strip HTML tags and collapse whitespace from article text. 🌰"""
    no_html = re.sub(r'<[^>]+>', ' ', raw)
    return re.sub(r'\s+', ' ', no_html).strip()


def fetch_cryptopanic_articles(marketvenueid: str, pairid: str, cryptopanic_api_key: str) -> list:
    """
    Fetch recent crypto news articles from CryptoPanic relevant to the
    market venue and trading pair. Returns a list of dicts with keys
    'title', 'url', 'text'. 🌰
    """
    # Derive a base currency symbol from the pair (e.g. 'btc-usdt' -> 'BTC')
    base_currency = pairid.split('-')[0].upper() if '-' in pairid else pairid.upper()
    currencies = base_currency

    articles = []
    try:
        url = "https://cryptopanic.com/api/v1/posts/"
        params = {
            "auth_token": cryptopanic_api_key,
            "currencies": currencies,
            "kind": "news",
            "public": "true",
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json().get("results", [])
        for item in results[:20]:  # 🌰 cap at 20 candidates before re-ranking
            title = item.get("title", "")
            source_url = item.get("url", "")
            # CryptoPanic free tier does not provide full body; use title as text
            body = item.get("metadata", {}).get("description") or title
            articles.append({"title": title, "url": source_url, "text": _clean_text(body)})
    except Exception as e:
        print(f"[RAG] CryptoPanic fetch error: {e}")
    return articles


def fetch_newsapi_articles(marketvenueid: str, pairid: str, newsapi_key: str) -> list:
    """
    Fetch recent crypto news articles from NewsAPI relevant to the
    market venue and trading pair. Returns a list of dicts with keys
    'title', 'url', 'text'. 🌰
    """
    base_currency = pairid.split('-')[0].upper() if '-' in pairid else pairid.upper()
    query = f"{base_currency} {marketvenueid} cryptocurrency"

    articles = []
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 20,
            "apiKey": newsapi_key,
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json().get("articles", [])
        for item in results:
            title = item.get("title") or ""
            source_url = item.get("url") or ""
            description = item.get("description") or ""
            content = item.get("content") or ""
            body = content if content else description
            articles.append({"title": title, "url": source_url, "text": _clean_text(body)})
    except Exception as e:
        print(f"[RAG] NewsAPI fetch error: {e}")
    return articles


def embed_texts_cohere(texts: list, cohere_api_key: str) -> list:
    """
    Embed a list of strings using the Cohere embed API.
    Returns a list of float vectors. 🌰
    """
    url = "https://api.cohere.ai/v1/embed"
    headers = {
        "Authorization": f"Bearer {cohere_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "texts": texts,
        "model": "embed-english-v3.0",
        "input_type": "search_document",
    }
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()["embeddings"]


def cosine_similarity(vec_a: list, vec_b: list) -> float:
    """Compute cosine similarity between two vectors. 🌰"""
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = sum(a * a for a in vec_a) ** 0.5
    norm_b = sum(b * b for b in vec_b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def retrieve_relevant_articles(
    marketvenueid: str,
    pairid: str,
    cohere_api_key: str,
    cryptopanic_api_key: str = None,
    newsapi_key: str = None,
    top_k: int = RAG_TOP_K,
) -> list:
    """
    Fetch articles from available news sources, embed them alongside a
    query built from the market venue and pair, then return the top_k
    most relevant article dicts (keys: title, url, text). 🌰
    """
    articles = []
    if cryptopanic_api_key:
        articles += fetch_cryptopanic_articles(marketvenueid, pairid, cryptopanic_api_key)
    if newsapi_key:
        articles += fetch_newsapi_articles(marketvenueid, pairid, newsapi_key)

    if not articles:
        print("[RAG] No articles fetched from any source.")
        return []

    # Deduplicate by URL 🌰
    seen_urls = set()
    unique_articles = []
    for a in articles:
        if a["url"] not in seen_urls:
            seen_urls.add(a["url"])
            unique_articles.append(a)
    articles = unique_articles

    base_currency = pairid.split('-')[0].upper() if '-' in pairid else pairid.upper()
    query = f"{marketvenueid} {base_currency} cryptocurrency market trading volume price spike"

    try:
        doc_texts = [f"{a['title']} {a['text']}" for a in articles]
        all_texts = [query] + doc_texts
        all_embeddings = embed_texts_cohere(all_texts, cohere_api_key)
        query_embedding = all_embeddings[0]
        doc_embeddings = all_embeddings[1:]

        scored = [
            (cosine_similarity(query_embedding, doc_emb), article)
            for doc_emb, article in zip(doc_embeddings, articles)
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [article for _, article in scored[:top_k]]
    except Exception as e:
        print(f"[RAG] Embedding/similarity error: {e}")
        # Fallback: return first top_k articles without re-ranking 🌰
        return articles[:top_k]


def build_rag_context(articles: list, encoding, max_tokens: int = RAG_MAX_TOKENS) -> str:
    """
    Concatenate retrieved article snippets into a context string that
    fits within max_tokens. 🌰
    """
    context_parts = []
    total_tokens = 0
    for article in articles:
        snippet = f"Title: {article['title']}\nSource: {article['url']}\n{article['text']}"
        snippet_tokens = len(encoding.encode(snippet))
        if total_tokens + snippet_tokens > max_tokens:
            break
        context_parts.append(snippet)
        total_tokens += snippet_tokens
    return "\n\n---\n\n".join(context_parts)


# ---------------------------------------------------------------------------


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

        # 🌰 RAG: retrieve contextual articles when Cohere key is provided
        rag_context = ""
        if args.cohere_api_key:
            print("[RAG] Fetching and ranking relevant articles... 🌰")
            relevant_articles = retrieve_relevant_articles(
                marketvenueid=marketvenueid,
                pairid=pairid,
                cohere_api_key=args.cohere_api_key,
                cryptopanic_api_key=args.cryptopanic_api_key,
                newsapi_key=None,  # 🌰 pass newsapi key here if available
                top_k=RAG_TOP_K,
            )
            if relevant_articles:
                rag_context = build_rag_context(relevant_articles, encoding, RAG_MAX_TOKENS)
                print(f"[RAG] Retrieved {len(relevant_articles)} article(s), "
                      f"{len(encoding.encode(rag_context))} tokens of context. 🌰")
            else:
                print("[RAG] No relevant articles found, proceeding without RAG context.")
        else:
            print("[RAG] Cohere API key not provided, skipping RAG. 🌰")

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
