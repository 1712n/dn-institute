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
from tools.python_modules.llm_utils import remove_plus, count_tokens, trimming_text
import tools.article_checker.claude_retriever
from tools.article_checker.claude_retriever.searcher.searchtools.websearch import BraveSearchTool

# 🌰 Maximum token budget per file to avoid exceeding Claude's context window
MAX_TOKENS_PER_FILE = 12000


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
    Make an API call and return the response. 🌰
    Includes retry logic for transient failures.
    """
    for attempt in range(3):
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
            print(f"Error in API call (attempt {attempt + 1}/3): {e}")
            if attempt == 2:
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


def extract_file_text(file_diff):
    """
    Extract and combine all text segments from a single file diff. 🌰
    Handles files with multiple diff segments gracefully.
    """
    parts = [file_diff.get('header', '')]
    for segment in file_diff.get('body', []):
        parts.append(segment.get('body', ''))
    return remove_plus('\n'.join(parts))


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

    if not diff:
        print("No diff content found in the PR.")
        create_comment_on_pr(pr, "⚠️ No article content found in this PR to review.")
        return

    print('-' * 50)
    print(f"Found {len(diff)} file(s) in the PR diff")
    print('-' * 50)

    # 🌰 Process all files in the diff, not just the first one
    all_answers = []
    for i, file_diff in enumerate(diff):
        if not file_diff.get('body'):
            print(f"Skipping file {i + 1}: no body segments")
            continue

        text = extract_file_text(file_diff)
        if not text.strip():
            print(f"Skipping file {i + 1}: empty text after processing")
            continue

        # Trim text if it exceeds token budget to avoid context window issues
        token_count = count_tokens(text)
        if token_count > MAX_TOKENS_PER_FILE:
            print(f"File {i + 1} has {token_count} tokens, trimming to {MAX_TOKENS_PER_FILE}")
            text = trimming_text(text, MAX_TOKENS_PER_FILE)

        print(f"Processing file {i + 1}/{len(diff)} ({count_tokens(text)} tokens)")
        answer = api_call(text, client, model, max_tokens, temperature)

        if answer:
            # Extract filename from the diff header for context
            header_line = file_diff.get('header', 'Unknown file')
            filename = header_line.split('\n')[0].strip() if header_line else 'Unknown file'
            if len(diff) > 1:
                all_answers.append(f"### 📄 Review for `{filename}`\n\n{answer}")
            else:
                all_answers.append(answer)
        else:
            print(f"Warning: API call returned no answer for file {i + 1}")

    if all_answers:
        # 🌰 Combine all file reviews into a single comment
        combined_answer = "\n\n---\n\n".join(all_answers)
        create_comment_on_pr(pr, combined_answer)
    else:
        create_comment_on_pr(pr, "⚠️ The QA bot was unable to generate a review for this PR. Please request a manual review.")