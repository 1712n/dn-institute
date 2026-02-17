import openai
from tiktoken import encoding_for_model
import argparse
import json
import os
import requests
import glob
from github import Github
from tools.python_modules.utils import read_file, extract_between_tags
from tools.python_modules.report_graphics_tool import Visualization
from tools.chart_generator.chart_generator import (
    generate_charts_for_report,
    charts_to_shortcodes,
    replace_static_images_in_markdown,
)


REPO_NAME = "1712n/dn-institute"
SYSTEM_PROMPT_FILE = 'tools/market_health_reporter/doc/prompts/system_prompt.txt'
HUMAN_PROMPT_FILE = 'tools/market_health_reporter/doc/prompts/prompt1.txt'
DYNAMIC_CHART_INSTRUCTIONS_FILE = 'tools/market_health_reporter/doc/prompts/dynamic_chart_instructions.txt'
ARTICLE_EXAMPLE_FILE = 'content/market-health/posts/2023-08-14-huobi/index.md'
OUTPUT_DIR = 'content/market-health/posts/'
DATA_DIR = 'tools/market_health_reporter/doc/data/'
MAX_TOKENS = 125000
RAG_TOP_K = 3


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
        "--use-dynamic-charts",
        dest="use_dynamic_charts",
        help="Use dynamic Chart.js charts instead of static matplotlib images",
        action="store_true",
        default=False,
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


def create_prompt(article_example: str, data: dict, human_prompt_content: str,
                  rag_context: str = "", use_dynamic_charts: bool = False) -> str:
    """
    Creates a prompt string using article example, data, and optional RAG context.

    When use_dynamic_charts is True, additional instructions are appended to
    guide the LLM to use dynamic chart placeholders instead of static image
    references.
    """
    prompt = f"<example> {article_example} </example>\n"

    if rag_context:
        prompt += (
            "<retrieved_context>\n"
            "The following excerpts from past market health reports and metric documentation "
            "are provided as additional reference. Use these to inform your analysis style, "
            "metric interpretations, and report structure. Do not copy them verbatim, but "
            "leverage the analytical patterns and domain knowledge they contain.\n\n"
            f"{rag_context}\n"
            "</retrieved_context>\n"
        )

    prompt += f"{human_prompt_content}\n"

    if use_dynamic_charts:
        try:
            dynamic_chart_instructions = read_file(DYNAMIC_CHART_INSTRUCTIONS_FILE)
            prompt += f"\n{dynamic_chart_instructions}\n"
        except FileNotFoundError:
            print("Warning: Dynamic chart instructions file not found, using default prompt.")

    prompt += f"<data> {json.dumps(data)} </data>"
    return prompt


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

        # Build RAG context from past reports and metric documentation
        rag_context = ""
        try:
            from tools.market_health_reporter.rag import build_rag_context, build_rag_query
            rag_query = build_rag_query(marketvenueid, pairid, data)
            print(f"RAG query: {rag_query}")
            rag_context = build_rag_context(
                query=rag_query,
                api_key=args.API_key,
                top_k=RAG_TOP_K,
            )
            if rag_context:
                print(f"RAG context retrieved ({len(rag_context)} characters).")
            else:
                print("RAG: No relevant context retrieved, proceeding without RAG.")
        except Exception as rag_error:
            print(f"RAG retrieval failed ({rag_error}), proceeding without RAG context.")

        prompt = create_prompt(article_example, data, human_prompt_content, rag_context,
                               use_dynamic_charts=args.use_dynamic_charts)
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

            output_subdir = os.path.join(OUTPUT_DIR, f"{start}-{end}-{marketvenueid}-{pairid}")

            if args.use_dynamic_charts:
                # Generate dynamic Chart.js charts using LLM-driven selection
                print("Generating dynamic charts...")
                charts, chart_reasoning = generate_charts_for_report(
                    data, api_key=args.API_key
                )
                if chart_reasoning:
                    print(f"Chart selection reasoning: {chart_reasoning}")

                # Replace static figure shortcodes with dynamic chart shortcodes
                output = replace_static_images_in_markdown(output, charts)

                # Append any charts not already referenced in the article
                chart_shortcodes = charts_to_shortcodes(charts)
                referenced_ids = set()
                for chart in charts:
                    if chart['id'] in output:
                        referenced_ids.add(chart['id'])

                # Add unreferenced charts at the end of the article
                extra_charts = []
                for i, chart in enumerate(charts):
                    if chart['id'] not in referenced_ids:
                        extra_charts.append(chart_shortcodes[i])

                if extra_charts:
                    output += "\n\n## Additional Charts\n\n"
                    output += "\n\n".join(extra_charts)

                print(f"Generated {len(charts)} dynamic charts for the report.")
            else:
                # Fall back to static matplotlib image generation
                vis = Visualization()
                vis.generate_report(data, output_subdir)

            save_output(output, OUTPUT_DIR, marketvenueid, pairid, start, end)

            post_comment_to_issue(args.github_token, int(args.issue), REPO_NAME, output)

    except Exception as e:
        print(f"Error occurred: {e}")
