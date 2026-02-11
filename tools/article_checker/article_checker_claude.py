#!/bin/env python

"""
The bot checks if a new article complies with all requirements.

Improvements over original:
- Processes all article files in PR (not just the first)
- Filters out non-article files (only checks .md files in content/ directories)
- Uses configurable search parameters from config.json
- Better error handling and reporting
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


# Pattern to match article files in the wiki content directories
ARTICLE_PATH_PATTERN = re.compile(r'content/.*\.md')


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


def extract_filename(header: str) -> str:
    """
    Extract the filename from a diff header.
    The header typically starts with 'a/path/to/file b/path/to/file'
    """
    lines = header.strip().split('\n')
    if lines:
        parts = lines[0].split()
        if len(parts) >= 2:
            # Remove the 'a/' or 'b/' prefix
            return parts[1].lstrip('b/')
    return ""


def is_article_file(filename: str) -> bool:
    """
    Check if a file is an article markdown file (in the content/ directory).
    Filters out config files, code changes, and non-content files.
    """
    return bool(ARTICLE_PATH_PATTERN.search(filename))


def extract_article_text(diff_file: dict) -> str:
    """
    Extract the full article text from a parsed diff file entry,
    combining all body segments.
    """
    parts = [diff_file['header']]
    for segment in diff_file['body']:
        parts.append(segment['body'])
    return remove_plus('\n'.join(parts))


def api_call(query, client, model, max_tokens, temperature, n_search_results, max_searches):
    """
    Make an API call and return the response.
    """
    try:
        return client.completion_with_retrieval(
            query=query,
            model=model,
            n_search_results_to_use=n_search_results,
            max_searches_to_try=max_searches,
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
    n_search_results = config.get('N_SEARCH_RESULTS_TO_USE', 3)
    max_searches = config.get('MAX_SEARCHES_TO_TRY', 5)

    client = tools.article_checker.claude_retriever.ClientWithRetrieval(api_key=args.API_key, search_tool=search_tool)

    github = Github(args.github_token)
    pr = get_pull_request(github, args.pull_url)
    _diff = get_diff_by_url(pr)
    diff = parse_diff(_diff)

    print('-' * 50)
    print(f"Found {len(diff)} file(s) in PR diff")
    print('-' * 50)

    # Filter to only article files and collect results
    article_files = []
    skipped_files = []
    for diff_file in diff:
        filename = extract_filename(diff_file['header'])
        if is_article_file(filename):
            article_files.append((filename, diff_file))
        else:
            skipped_files.append(filename)

    if skipped_files:
        print(f"Skipping non-article files: {', '.join(skipped_files)}")

    if not article_files:
        print("No article files found in PR diff.")
        create_comment_on_pr(pr, "No article files (content/**/*.md) were found in this PR. The QA bot only checks article submissions.")
        return

    # Process each article file
    all_results = []
    for filename, diff_file in article_files:
        print(f"\n{'=' * 50}")
        print(f"Checking article: {filename}")
        print(f"{'=' * 50}")

        text = extract_article_text(diff_file)
        if not text.strip():
            all_results.append(f"## {filename}\n\n⚠️ Empty or whitespace-only content detected.\n")
            continue

        answer = api_call(text, client, model, max_tokens, temperature, n_search_results, max_searches)
        if answer:
            if len(article_files) > 1:
                all_results.append(f"## File: `{filename}`\n\n{answer}")
            else:
                all_results.append(answer)
        else:
            all_results.append(f"## {filename}\n\n⚠️ Failed to analyze this file. Please check manually.\n")

    # Combine results and post
    final_answer = "\n\n---\n\n".join(all_results)
    print('-' * 50)
    print('Final answer:', final_answer)
    print('-' * 50)

    create_comment_on_pr(pr, final_answer)
