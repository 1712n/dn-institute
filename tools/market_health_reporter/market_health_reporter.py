import argparse
import glob
import html
import json
import math
import os
import re
from typing import Dict, List, Tuple

import openai
import requests
from github import Github
from tiktoken import encoding_for_model

from tools.python_modules.utils import extract_between_tags, read_file


REPO_NAME = "1712n/dn-institute"
SYSTEM_PROMPT_FILE = 'tools/market_health_reporter/doc/prompts/system_prompt.txt'
HUMAN_PROMPT_FILE = 'tools/market_health_reporter/doc/prompts/prompt1.txt'
ARTICLE_EXAMPLE_FILE = 'content/research/market-health/posts/2023-08-14-huobi/index.md'
OUTPUT_DIR = 'content/research/market-health/posts/'
DATA_DIR = 'tools/market_health_reporter/doc/data/'
MAX_TOKENS = 125000
FIGURE_SHORTCODE_PATTERN = re.compile(r"\{\{<\s*figure\s+([^>]+?)\s*>\}\}")
SHORTCODE_ATTR_PATTERN = re.compile(r'(\w+)="([^"]*)"')
CHART_PLACEHOLDER_ORDER = (
    "volume_hist.png",
    "crypto_metrics.png",
    "benford_law.png",
    "vv_correlation.png",
)
MAX_INLINE_CHART_POINTS = 240


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
    os.makedirs(directory, exist_ok=True)
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


def normalize_market_metrics(data) -> List[dict]:
    """
    Normalizes market metrics response payload into a list of dict records.
    """
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ("data", "metrics", "items", "result"):
            maybe_metrics = data.get(key)
            if isinstance(maybe_metrics, list):
                return [item for item in maybe_metrics if isinstance(item, dict)]
    return []


def _to_float(value):
    """
    Best-effort conversion to float.
    """
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _round_float(value):
    """
    Rounds float values to reduce shortcode payload size.
    """
    if value is None:
        return None
    return round(value, 8)


def _format_timestamp(value) -> str:
    """
    Formats API timestamp values for chart labels.
    """
    if not isinstance(value, str):
        return ""
    normalized = value.replace("T", " ").rstrip("Z")
    return normalized[:16]


def _build_histogram(values: List[float], bins: int = 30) -> Tuple[List[str], List[int]]:
    """
    Builds histogram bins and labels without external plotting dependencies.
    """
    if not values:
        return [], []

    minimum = min(values)
    maximum = max(values)
    if minimum == maximum:
        labels = [f"{minimum:.4f} - {maximum:.4f}"]
        return labels, [len(values)]

    bin_width = (maximum - minimum) / bins
    counts = [0] * bins
    for value in values:
        index = int((value - minimum) / bin_width)
        if index >= bins:
            index = bins - 1
        counts[index] += 1

    labels = []
    for index in range(bins):
        start = minimum + (bin_width * index)
        end = minimum + (bin_width * (index + 1))
        labels.append(f"{start:.4f} - {end:.4f}")
    return labels, counts


def _downsample_metrics(metrics_data: List[dict], max_points: int = MAX_INLINE_CHART_POINTS) -> List[dict]:
    """
    Downsamples dense series so inline shortcode JSON stays reasonably sized.
    """
    if len(metrics_data) <= max_points:
        return metrics_data

    step = max(1, math.ceil(len(metrics_data) / max_points))
    sampled = metrics_data[::step]
    if sampled[-1] is not metrics_data[-1]:
        sampled.append(metrics_data[-1])
    return sampled


def _build_market_chart_configs(metrics_data: List[dict]) -> Dict[str, dict]:
    """
    Builds chart configurations keyed by legacy figure placeholder names.
    """
    chart_metrics = _downsample_metrics(metrics_data)
    labels = [_format_timestamp(item.get("timestamp")) for item in chart_metrics]

    volume_values = [_to_float(item.get("volume")) for item in metrics_data]
    histogram_labels, histogram_counts = _build_histogram(
        [value for value in volume_values if value is not None]
    )

    trade_count_values = [_to_float(item.get("tradecount")) for item in chart_metrics]
    critical_values = []
    for trade_count in trade_count_values:
        if trade_count and trade_count > 0:
            critical_values.append(_round_float(1.36 / math.sqrt(trade_count)))
        else:
            critical_values.append(None)

    return {
        "volume_hist.png": {
            "type": "bar",
            "title": "Transaction Volume Distribution",
            "caption": "Histogram of transaction volume across the selected period.",
            "data": {
                "labels": histogram_labels,
                "datasets": [
                    {
                        "label": "Transaction volume frequency",
                        "data": histogram_counts,
                        "backgroundColor": "rgba(56, 139, 253, 0.45)",
                        "borderColor": "rgba(56, 139, 253, 1)",
                        "borderWidth": 1,
                    }
                ],
            },
        },
        "crypto_metrics.png": {
            "type": "line",
            "title": "Market Metrics Over Time",
            "caption": "Volume, trade count, average transaction size, and buy/sell ratio over time.",
            "data": {
                "labels": labels,
                "datasets": [
                    {
                        "label": "Volume",
                        "data": [_round_float(_to_float(item.get("volume"))) for item in chart_metrics],
                        "borderColor": "rgba(56, 139, 253, 1)",
                        "backgroundColor": "rgba(56, 139, 253, 0.2)",
                        "pointRadius": 0,
                        "tension": 0.2,
                    },
                    {
                        "label": "Trade Count",
                        "data": [_round_float(_to_float(item.get("tradecount"))) for item in chart_metrics],
                        "borderColor": "rgba(46, 160, 67, 1)",
                        "backgroundColor": "rgba(46, 160, 67, 0.2)",
                        "pointRadius": 0,
                        "tension": 0.2,
                    },
                    {
                        "label": "Avg Transaction Size",
                        "data": [_round_float(_to_float(item.get("avgtransactionsize"))) for item in chart_metrics],
                        "borderColor": "rgba(251, 188, 4, 1)",
                        "backgroundColor": "rgba(251, 188, 4, 0.2)",
                        "pointRadius": 0,
                        "tension": 0.2,
                    },
                    {
                        "label": "Buy/Sell Ratio",
                        "data": [_round_float(_to_float(item.get("buysellratio"))) for item in chart_metrics],
                        "borderColor": "rgba(214, 90, 49, 1)",
                        "backgroundColor": "rgba(214, 90, 49, 0.2)",
                        "pointRadius": 0,
                        "tension": 0.2,
                    },
                ],
            },
        },
        "benford_law.png": {
            "type": "line",
            "title": "Benford Law Test vs Critical Value",
            "caption": "K-S Benford test against the 1.36/sqrt(trade count) critical threshold.",
            "data": {
                "labels": labels,
                "datasets": [
                    {
                        "label": "Benford Law Test Score",
                        "data": [_round_float(_to_float(item.get("benfordlawtest"))) for item in chart_metrics],
                        "borderColor": "rgba(56, 139, 253, 1)",
                        "backgroundColor": "rgba(56, 139, 253, 0.2)",
                        "pointRadius": 0,
                        "tension": 0.2,
                    },
                    {
                        "label": "Critical Value",
                        "data": critical_values,
                        "borderColor": "rgba(46, 160, 67, 1)",
                        "backgroundColor": "rgba(46, 160, 67, 0.2)",
                        "borderDash": [6, 4],
                        "pointRadius": 0,
                        "tension": 0.2,
                    },
                ],
            },
        },
        "vv_correlation.png": {
            "type": "line",
            "title": "Volume-Volatility Correlation",
            "caption": "Volume-volatility correlation trend across the selected analysis window.",
            "data": {
                "labels": labels,
                "datasets": [
                    {
                        "label": "VV Correlation",
                        "data": [_round_float(_to_float(item.get("vvcorrelation"))) for item in chart_metrics],
                        "borderColor": "rgba(130, 80, 223, 1)",
                        "backgroundColor": "rgba(130, 80, 223, 0.2)",
                        "pointRadius": 0,
                        "tension": 0.2,
                    }
                ],
            },
        },
    }


def _render_market_chart_shortcode(chart_type: str, title: str, caption: str, data: dict) -> str:
    """
    Renders a Hugo market-chart shortcode line with escaped inline JSON payload.
    """
    # 🌰 Keep chart payload inline so Hugo can render dynamic, client-side visuals.
    escaped_data = html.escape(json.dumps(data, separators=(",", ":")), quote=True)
    escaped_type = html.escape(chart_type, quote=True)
    escaped_title = html.escape(title, quote=True)
    escaped_caption = html.escape(caption, quote=True)
    return (
        "{{< market-chart "
        f'type="{escaped_type}" '
        f'title="{escaped_title}" '
        f'caption="{escaped_caption}" '
        f'data="{escaped_data}" >}}'
    )


def replace_figure_placeholders_with_market_charts(article: str, data) -> str:
    """
    Replaces static figure placeholders with market-chart shortcodes.
    """
    metrics_data = normalize_market_metrics(data)
    chart_configs = _build_market_chart_configs(metrics_data)
    replaced_counter = [0]

    # 🌰 Figure placeholders are a legacy format; map them to dynamic charts here.
    def replacement(match):
        attrs = {
            key.lower(): value for key, value in SHORTCODE_ATTR_PATTERN.findall(match.group(1))
        }
        src = attrs.get("src", "")
        chart_config = chart_configs.get(src)
        if chart_config is None:
            return match.group(0)

        caption = attrs.get("caption") or chart_config["caption"]
        replaced_counter[0] += 1
        return _render_market_chart_shortcode(
            chart_type=chart_config["type"],
            title=chart_config["title"],
            caption=caption,
            data=chart_config["data"],
        )

    updated_article = FIGURE_SHORTCODE_PATTERN.sub(replacement, article)
    if replaced_counter[0] > 0:
        return updated_article

    # 🌰 Fallback for model outputs that omit figure placeholders entirely.
    fallback_shortcodes = []
    for chart_name in CHART_PLACEHOLDER_ORDER:
        chart_config = chart_configs[chart_name]
        fallback_shortcodes.append(
            _render_market_chart_shortcode(
                chart_type=chart_config["type"],
                title=chart_config["title"],
                caption=chart_config["caption"],
                data=chart_config["data"],
            )
        )
    return f"{updated_article.rstrip()}\n\n## Metric Charts\n\n" + "\n\n".join(fallback_shortcodes) + "\n"


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
            output = replace_figure_placeholders_with_market_charts(output, data)

            print("This is an answer: ", output)
            save_output(output, OUTPUT_DIR, marketvenueid, pairid, start, end)

            post_comment_to_issue(args.github_token, int(args.issue), REPO_NAME, output)

    except Exception as e:
        print(f"Error occurred: {e}")
