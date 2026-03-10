#!/bin/env python

"""
The bot checks if a new article complies with all requirements
"""

import argparse
import os
import sys
import json
import re
from github import Github
from tools.python_modules.git import get_pull_request, get_diff_by_url, parse_diff
from tools.python_modules.utils import logging_decorator
from tools.python_modules.llm_utils import remove_plus
import tools.article_checker.claude_retriever
from tools.article_checker.claude_retriever.searcher.searchtools.websearch import BraveSearchTool


# Pattern to match article files under content/ directory
ARTICLE_FILE_PATTERN = re.compile(r'content/.+\.md')


def parse_cli_args():
    """
    Parse CLI arguments.
    """
    parser = argparse.ArgumentParser()
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


def filter_article_files(diff):
    """
    Filter diff entries to only include article files under content/ directory.
    Returns list of diff entries matching the content/**/*.md pattern.
    """
    article_files = []
    for file_diff in diff:
        header = file_diff.get('header', '')
        if ARTICLE_FILE_PATTERN.search(header):
            article_files.append(file_diff)
    return article_files


def extract_file_text(file_diff):
    """
    Extract the full text content from a single file diff entry.
    Concatenates header and all segment bodies.
    """
    parts = [file_diff['header']]
    for segment in file_diff.get('body', []):
        parts.append(segment.get('body', ''))
    return remove_plus(''.join(parts))


def api_call(query, client, model, max_tokens, temperature):
    """
    Make an API call and return the response.
    """
    try:
        return client.completion_with_retrieval(
            query=query,
            model=model,
            n_search_results_to_use=3,
            max_searches_to_try=5,
            max_tokens=max_tokens,
            temperature=temperature
        )
    except Exception as e:
        print(f"Error in API call: {e}")
        return None


@logging_decorator("Comment on PR")
def create_comment_on_pr(pull_request, answer):
    """
    Create and post a comment on a Github pull request.
    """
    try:
        comment = answer
        print(comment)
        # only post comment if running on Github Actions
        if os.environ.get("GITHUB_ACTIONS") == "true":
            pull_request.create_issue_comment(comment)
    except Exception as e:
        print(f"Error creating a comment on PR: {e}")


def main():
    args = parse_cli_args()
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    search_tool = BraveSearchTool(brave_api_key=args.SEARCH_API_KEY, summarize_with_claude=True,
                                  anthropic_api_key=args.API_key)

    model = config['ANTHROPIC_SEARCH_MODEL']
    max_tokens = config['ANTHROPIC_SEARCH_MAX_TOKENS']
    temperature = config['ANTHROPIC_SEARCH_TEMPERATURE']

    client = tools.article_checker.claude_retriever.ClientWithRetrieval(api_key=args.API_key, search_tool=search_tool)

    github = Github(args.github_token)
    pr = get_pull_request(github, args.pull_url)
    _diff = get_diff_by_url(pr)
    diff = parse_diff(_diff)

    print('-' * 50)
    print(diff)
    print('-' * 50)

    # Filter to only process article files under content/
    article_files = filter_article_files(diff)

    if not article_files:
        print("No article files found in the PR diff. Skipping analysis.")
        create_comment_on_pr(pr, "No article files (content/**/*.md) found in this PR.")
        return

    # Process each article file and collect results
    results = []
    for file_diff in article_files:
        filename = file_diff['header'].split('\n')[0].strip()
        print(f"\nProcessing: {filename}")

        text = extract_file_text(file_diff)
        answer = api_call(text, client, model, max_tokens, temperature)

        if answer is None:
            results.append(f"## {filename}\n\n:warning: Analysis failed due to an API error.\n")
            continue

        print('-' * 50)
        print(f'Answer for {filename}:', answer)
        print('-' * 50)

        results.append(f"## {filename}\n\n{answer}\n")

    # Combine all results into a single comment
    combined_answer = "\n---\n\n".join(results)
    create_comment_on_pr(pr, combined_answer)