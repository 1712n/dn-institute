import openai
from tiktoken import encoding_for_model
import argparse
import json
import os
import requests
import glob
from github import Github
from tools.python_modules.utils import read_file, extract_between_tags


REPO_NAME = "1712n/dn-institute"
SYSTEM_PROMPT_FILE = 'tools/market_health_reporter/doc/prompts/system_prompt.txt'
HUMAN_PROMPT_FILE = 'tools/market_health_reporter/doc/prompts/prompt1.txt'
ARTICLE_EXAMPLE_FILE = 'content/market-health/posts/2023-08-14-huobi/index.md'
OUTPUT_DIR = 'content/market-health/posts/'
DATA_DIR = 'tools/market_health_reporter/doc/data/'
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


def build_chart_shortcode(data: dict, metric: str, label: str, color: str = "rgba(75,192,192,1)") -> str:
    """
    Build a Hugo metric_chart shortcode string from API data for a given metric.
    Returns an empty string if the metric has no data.
    """
    timestamps = []
    values = []

    for entry in data:
        ts = entry.get("time") or entry.get("timestamp") or entry.get("date", "")
        val = entry.get(metric)
        if ts and val is not None:
            timestamps.append(ts)
            try:
                values.append(float(val))
            except (TypeError, ValueError):
                values.append(None)

    if not timestamps or all(v is None for v in values):
        return ""

    chart_data = {
        "labels": timestamps,
        "datasets": [
            {
                "label": label,
                "data": values,
                "borderColor": color,
                "backgroundColor": color.replace("1)", "0.15)"),
                "fill": True,
                "tension": 0.3,
                "pointRadius": 2
            }
        ]
    }

    json_str = json.dumps(chart_data)
    return f'{{{{< metric_chart type="line" title="{label}" >}}}}\n{json_str}\n{{{{< /metric_chart >}}}}\n'


def generate_charts_markdown(data: dict, output_subdir: str) -> None:
    """
    Generate a markdown file containing dynamic Chart.js shortcodes
    for each metric found in the API data, replacing static image generation.
    """
    if not data:
        return

    # Determine the list of records (API may return a list or a dict with a key)
    records = []
    if isinstance(data, list):
        records = data
    elif isinstance(data, dict):
        for key in ("data", "results", "metrics"):
            if key in data and isinstance(data[key], list):
                records = data[key]
                break
        if not records:
            # Fallback: treat top-level dict as a single record
            records = [data]

    if not records:
        return

    # Discover numeric metric keys (excluding time/identifier fields)
    skip_keys = {"time", "timestamp", "date", "marketvenueid", "pairid", "pair", "market"}
    metric_keys = []
    for rec in records:
        for k, v in rec.items():
            if k not in skip_keys and k not in metric_keys:
                try:
                    float(v)
                    metric_keys.append(k)
                except (TypeError, ValueError):
                    pass

    if not metric_keys:
        return

    # Color palette for multiple metrics
    colors = [
        "rgba(75,192,192,1)",
        "rgba(255,99,132,1)",
        "rgba(54,162,235,1)",
        "rgba(255,206,86,1)",
        "rgba(153,102,255,1)",
        "rgba(255,159,64,1)",
    ]

    charts_md_path = os.path.join(output_subdir, "charts.md")
    with open(charts_md_path, "w", encoding="utf-8") as f:
        f.write("---\ntitle: Market Health Charts\n---\n\n")
        for idx, metric in enumerate(metric_keys):
            color = colors[idx % len(colors)]
            label = metric.replace("_", " ").title()
            shortcode = build_chart_shortcode(records, metric, label, color)
            if shortcode:
                f.write(shortcode)
                f.write("\n")

    print(f"Charts markdown saved to: {charts_md_path}")


def inject_charts_into_article(article_path: str, data: dict) -> None:
    """
    Inject metric_chart shortcodes directly into the generated article markdown.
    """
    if not os.path.exists(article_path):
        return

    records = []
    if isinstance(data, list):
        records = data
    elif isinstance(data, dict):
        for key in ("data", "results", "metrics"):
            if key in data and isinstance(data[key], list):
                records = data[key]
                break

    if not records:
        return

    skip_keys = {"time", "timestamp", "date", "marketvenueid", "pairid", "pair", "market"}
    metric_keys = []
    for rec in records:
        for k, v in rec.items():
            if k not in skip_keys and k not in metric_keys:
                try:
                    float(v)
                    metric_keys.append(k)
                except (TypeError, ValueError):
                    pass

    if not metric_keys:
        return

    colors = [
        "rgba(75,192,192,1)",
        "rgba(255,99,132,1)",
        "rgba(54,162,235,1)",
        "rgba(255,206,86,1)",
        "rgba(153,102,255,1)",
        "rgba(255,159,64,1)",
    ]

    charts_block = "\n\n## Market Health Charts \U0001f330\n\n"
    for idx, metric in enumerate(metric_keys):
        color = colors[idx % len(colors)]
        label = metric.replace("_", " ").title()
        shortcode = build_chart_shortcode(records, metric, label, color)
        if shortcode:
            charts_block += shortcode + "\n"

    with open(article_path, "r", encoding="utf-8") as f:
        content = f.read()

    with open(article_path, "w", encoding="utf-8") as f:
        f.write(content + charts_block)

    print(f"Charts injected into article: {article_path}")


def save_output(output: str, directory: str, marketvenueid: str, pairid: str, start: str, end: str) -> str:
    """
    Saves the output to a markdown file in the specified directory, creating a subdirectory for it.
    Returns the full path of the saved file.
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
    return full_path


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
            article_path = save_output(output, OUTPUT_DIR, marketvenueid, pairid, start, end)
            output_subdir = os.path.join(OUTPUT_DIR, f"{start}-{end}-{marketvenueid}-{pairid}")

            # Inject dynamic Chart.js shortcodes into the generated article
            inject_charts_into_article(article_path, data)
            # Also generate a standalone charts.md for reference
            generate_charts_markdown(data, output_subdir)

            post_comment_to_issue(args.github_token, int(args.issue), REPO_NAME, output)

    except Exception as e:
        print(f"Error occurred: {e}")
