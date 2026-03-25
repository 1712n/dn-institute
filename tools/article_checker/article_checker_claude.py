#!/bin/env python

"""
The bot checks if a new article complies with all requirements
"""

import argparse
import os
import sys
import json
from github import Github
from tools.python_modules.git import get_pull_request, get_diff_by_url, parse_diff
from tools.python_modules.utils import logging_decorator
from tools.python_modules.llm_utils import remove_plus
import tools.article_checker.claude_retriever
from tools.article_checker.claude_retriever.searcher.searchtools.websearch import BraveSearchTool


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


def api_call(query, client, model, max_tokens, temperature):
    """
    Make an API call and return the response.
    """
    try:
        return client.completion_with_retrieval(
            query=query,
            model=model,
            n_search_results_to_use=1,
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
    with open('tools/article_checker/config.json', 'r') as config_file:
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

    # Concatenate all files and segments from the diff, not just the first one
    all_diff_parts = []
    for file_diff in diff:
        for segment in file_diff['body']:
            all_diff_parts.append(file_diff['header'] + segment['body'])
    text = remove_plus('\n'.join(all_diff_parts))

    if not text.strip():
        print("Error: Diff is empty after parsing. Cannot proceed with review.")
        create_comment_on_pr(pr, ":warning: **QA Bot Error**: Could not parse the PR diff. The diff may be empty or in an unexpected format.")
        sys.exit(1)

    answer = api_call(text, client, model, max_tokens, temperature)
    print('-' * 50)
    print('This is an answer', answer)
    print('-' * 50)

    if answer is None:
        print("Error: API call returned None. Skipping PR comment.")
        create_comment_on_pr(pr, ":warning: **QA Bot Error**: The review could not be completed due to an API error. Please try again with `/articlecheck`.")
        sys.exit(1)

    create_comment_on_pr(pr, answer)