#!/bin/env python

"""
The bot checks if a new article complies with all requirements. 🌰
"""

import argparse
import os
import json
import time
from github import Github
from tools.python_modules.git import get_pull_request, get_diff_by_url, parse_diff
from tools.python_modules.utils import logging_decorator
from tools.python_modules.llm_utils import remove_plus
import tools.article_checker.claude_retriever
from tools.article_checker.claude_retriever.searcher.searchtools.websearch import BraveSearchTool

# Maximum number of retries for transient API failures
MAX_RETRIES = 3
# Base delay in seconds for exponential backoff
BASE_RETRY_DELAY = 5


def parse_cli_args():
    """
    Parse CLI arguments.
    """
    parser = argparse.ArgumentParser(
        description="QA bot that fact-checks and validates new Crypto Attack Wiki articles. 🌰"
    )
    parser.add_argument(
        "--github-token", dest="github_token", help="GitHub token", required=True
    )
    parser.add_argument(
        "--llm-api-key", dest="API_key", help="API key", required=True
    )
    parser.add_argument(
        "--pull-url", dest="pull_url", help="GitHub pull URL", required=True
    )
    parser.add_argument(
        "--search-api-key", dest="SEARCH_API_KEY", help="API key for the search engine", required=True
    )
    return parser.parse_args()


def api_call(query, client, model, max_tokens, temperature, retries=MAX_RETRIES):
    """
    Make an API call with exponential backoff retry logic.

    Retries up to `retries` times on transient failures, with exponential
    backoff starting at BASE_RETRY_DELAY seconds.

    Returns the API response string, or None if all attempts fail.
    """
    for attempt in range(1, retries + 1):
        try:
            start = time.time()
            result = client.completion_with_retrieval(
                query=query,
                model=model,
                n_search_results_to_use=1,
                max_searches_to_try=5,
                max_tokens=max_tokens,
                temperature=temperature
            )
            elapsed = time.time() - start
            print(f"API call succeeded (attempt {attempt}/{retries}, {elapsed:.1f}s)")
            return result
        except Exception as e:
            print(f"API call failed (attempt {attempt}/{retries}): {e}")
            if attempt < retries:
                delay = BASE_RETRY_DELAY * (2 ** (attempt - 1))
                print(f"Retrying in {delay}s...")
                time.sleep(delay)
    print("All API call attempts exhausted.")
    return None


def extract_article_text(diff):
    """
    Extract article text from parsed diff, combining all modified attack articles.

    Only processes files under `content/attacks/` with a `.md` extension to
    avoid feeding unrelated files (READMEs, configs, etc.) to the LLM.
    Returns None if no matching article files are found.
    """
    texts = []
    for file_diff in diff:
        header = file_diff.get('header', '')
        is_attack_article = 'content/attacks/' in header and '.md' in header
        if not is_attack_article:
            print(f"Skipping non-article file: {header[:80]}")
            continue
        body_segments = file_diff.get('body', [])
        file_text_parts = [file_diff['header']]
        for segment in body_segments:
            segment_body = segment.get('body', '') if isinstance(segment, dict) else str(segment)
            file_text_parts.append(segment_body)
        texts.append(remove_plus(''.join(file_text_parts)))
    if not texts:
        print("No attack article (.md) files found in diff.")
        return None
    return '\n\n'.join(texts)


@logging_decorator("Comment on PR")
def create_comment_on_pr(pull_request, answer):
    """
    Create and post a comment on a Github pull request.

    Posts a user-friendly error message if `answer` is None or empty,
    so contributors always receive actionable feedback.
    """
    try:
        if not answer:
            comment = (
                "## 🌰 QA Bot\n\n"
                "The automated check could not complete due to a temporary error. "
                "Please re-run by commenting `/articlecheck` or contact a maintainer."
            )
        else:
            comment = answer
        print(comment)
        # only post comment if running on Github Actions
        if os.environ.get("GITHUB_ACTIONS") == "true":
            pull_request.create_issue_comment(comment)
    except Exception as e:
        print(f"Error creating a comment on PR: {e}")


def main():
    start_time = time.time()
    args = parse_cli_args()

    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'config.json'
    )
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    search_tool = BraveSearchTool(
        brave_api_key=args.SEARCH_API_KEY,
        summarize_with_claude=True,
        anthropic_api_key=args.API_key
    )

    model = config['ANTHROPIC_SEARCH_MODEL']
    max_tokens = config['ANTHROPIC_SEARCH_MAX_TOKENS']
    temperature = config['ANTHROPIC_SEARCH_TEMPERATURE']

    client = tools.article_checker.claude_retriever.ClientWithRetrieval(
        api_key=args.API_key, search_tool=search_tool
    )

    github = Github(args.github_token)
    pr = get_pull_request(github, args.pull_url)
    _diff = get_diff_by_url(pr)
    diff = parse_diff(_diff)

    print('-' * 50)
    print(f"Parsed {len(diff)} file(s) from diff.")
    print('-' * 50)

    text = extract_article_text(diff)
    if text is None:
        create_comment_on_pr(pr, (
            "## 🌰 QA Bot\n\n"
            "No attack article files (`content/attacks/*.md`) were found in this PR's diff. "
            "Nothing to check."
        ))
        return

    print('-' * 50)
    print("Article text extracted, sending to LLM for review...")
    print('-' * 50)

    answer = api_call(text, client, model, max_tokens, temperature)

    elapsed = time.time() - start_time
    print('-' * 50)
    print(f"Total run time: {elapsed:.1f}s")
    print('Answer:', answer)
    print('-' * 50)

    create_comment_on_pr(pr, answer)


if __name__ == '__main__':
    main()
