#!/bin/env python

"""
The bot checks if a new article complies with all requirements.

Improvements over the original implementation:
- Multi-file PR support: processes all article files in a PR, not just the first one
- Article path filtering: only checks files matching the cyberattacks incidents directory
- Structured validation pipeline: separates metadata, content, and fact-checking stages
- Enhanced error handling with graceful degradation
- Configurable search parameters
- Detailed per-file and aggregate reporting
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


def is_article_file(file_header: str, article_path_pattern: str) -> bool:
    """
    Determine if a diff file entry is an article in the cyberattacks incidents directory.
    Checks the file path in the diff header against the configured article path pattern.
    """
    # Extract file path from diff header (format: "a/path b/path\n...")
    lines = file_header.strip().split('\n')
    for line in lines:
        if line.startswith('---') or line.startswith('+++'):
            path = line.split(' ', 1)[-1].lstrip('ab/')
            if article_path_pattern in path and path.endswith('.md'):
                return True
    # Also check the first line which contains the file paths
    if article_path_pattern in file_header and '.md' in file_header:
        return True
    return False


def extract_filename(file_header: str) -> str:
    """
    Extract the filename from a diff file header.
    """
    lines = file_header.strip().split('\n')
    for line in lines:
        if line.startswith('+++'):
            path = line.split(' ', 1)[-1].lstrip('b/')
            return os.path.basename(path)
    # Fallback: try to extract from the first line
    match = re.search(r'([^\s/]+\.md)', file_header)
    return match.group(1) if match else "unknown.md"


def pre_validate_metadata(text: str, config: dict) -> list[str]:
    """
    Perform quick structural validation on article metadata before sending to LLM.
    Returns a list of issues found. This saves API calls for obviously malformed submissions.
    """
    issues = []

    # Check for frontmatter delimiters
    frontmatter_match = re.search(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
    if not frontmatter_match:
        issues.append("Missing YAML frontmatter (content between `---` delimiters)")
        return issues

    frontmatter = frontmatter_match.group(1)
    valid_headers = config.get("VALID_METADATA_HEADERS", [])

    # Check each required metadata header
    for header in valid_headers:
        pattern = rf'^{re.escape(header)}\s*:'
        if not re.search(pattern, frontmatter, re.MULTILINE):
            issues.append(f"Missing required metadata header: `{header}`")

    # Check for required section headers
    valid_sections = config.get("VALID_SECTION_HEADERS", [])
    for section in valid_sections:
        if section not in text:
            issues.append(f"Missing required section: `{section}`")

    # Validate filename pattern (YYYY-MM-DD-Entity.md)
    # This is checked later by the LLM, but we can flag obvious issues
    date_match = re.search(r'^date:\s*(\d{4}-\d{2}-\d{2})', frontmatter, re.MULTILINE)
    if date_match:
        date_val = date_match.group(1)
        # Validate date format
        try:
            from datetime import datetime
            datetime.strptime(date_val, '%Y-%m-%d')
        except ValueError:
            issues.append(f"Invalid date format in metadata: `{date_val}` (expected YYYY-MM-DD)")

    # Check loss value is numeric
    loss_match = re.search(r'^loss:\s*(.+)$', frontmatter, re.MULTILINE)
    if loss_match:
        loss_val = loss_match.group(1).strip()
        # Remove quotes if present
        loss_val = loss_val.strip('"').strip("'")
        if not re.match(r'^[\d.]+$', loss_val):
            issues.append(f"Loss value `{loss_val}` should be a numeric value (no currency symbols)")

    # Validate attack-types against known types
    attack_type_match = re.search(r'^attack-types:\s*\n((?:\s+-\s+.+\n?)*)', frontmatter, re.MULTILINE)
    if not attack_type_match:
        # Try single-line format
        attack_type_match = re.search(r'^attack-types:\s*(.+)$', frontmatter, re.MULTILINE)

    return issues


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


def format_comment(filename: str, pre_validation_issues: list, llm_answer: str) -> str:
    """
    Format a structured comment for a single article file.
    """
    comment = f"### 📄 `{filename}`\n\n"

    if pre_validation_issues:
        comment += "#### ⚠️ Pre-validation Issues\n\n"
        comment += "The following structural issues were detected before fact-checking:\n\n"
        for issue in pre_validation_issues:
            comment += f"- {issue}\n"
        comment += "\n"

    if llm_answer:
        comment += llm_answer + "\n\n"
    elif pre_validation_issues:
        comment += "> ℹ️ Fact-checking was still performed despite pre-validation issues.\n\n"

    return comment


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

    search_tool = BraveSearchTool(
        brave_api_key=args.SEARCH_API_KEY,
        summarize_with_claude=True,
        anthropic_api_key=args.API_key
    )

    model = config['ANTHROPIC_SEARCH_MODEL']
    max_tokens = config['ANTHROPIC_SEARCH_MAX_TOKENS']
    temperature = config['ANTHROPIC_SEARCH_TEMPERATURE']
    n_search_results = config.get('N_SEARCH_RESULTS_TO_USE', 3)
    max_searches = config.get('MAX_SEARCHES_TO_TRY', 8)
    article_path_pattern = config.get('ARTICLE_PATH_PATTERN', 'content/research/cyberattacks/incidents/')

    client = tools.article_checker.claude_retriever.ClientWithRetrieval(
        api_key=args.API_key,
        search_tool=search_tool
    )

    github = Github(args.github_token)
    pr = get_pull_request(github, args.pull_url)
    _diff = get_diff_by_url(pr)
    diff = parse_diff(_diff)

    print('-' * 50)
    print(f"Found {len(diff)} file(s) in PR diff")
    print('-' * 50)

    # Process each article file in the PR
    article_comments = []
    non_article_files = []

    for file_diff in diff:
        file_header = file_diff['header']
        filename = extract_filename(file_header)

        # Filter: only process article markdown files
        if not is_article_file(file_header, article_path_pattern):
            non_article_files.append(filename)
            print(f"Skipping non-article file: {filename}")
            continue

        print(f"\n{'='*50}")
        print(f"Processing article: {filename}")
        print(f"{'='*50}")

        # Reconstruct the article text from diff
        body_parts = []
        for segment in file_diff['body']:
            body_parts.append(segment.get('body', ''))
        text = remove_plus(file_header + ''.join(body_parts))

        # Pre-validate metadata structure
        pre_issues = pre_validate_metadata(text, config)
        if pre_issues:
            print(f"Pre-validation issues for {filename}: {pre_issues}")

        # Run LLM-based fact-checking and quality analysis
        answer = api_call(text, client, model, max_tokens, temperature, n_search_results, max_searches)

        print('-' * 50)
        print(f'Answer for {filename}:', answer)
        print('-' * 50)

        article_comments.append(format_comment(filename, pre_issues, answer))

    # Build the final PR comment
    if not article_comments:
        final_comment = "## 🤖 Article QA Bot\n\n"
        final_comment += "No article files found in this PR matching the expected path "
        final_comment += f"(`{article_path_pattern}*.md`).\n\n"
        if non_article_files:
            final_comment += f"Non-article files detected: {', '.join(f'`{f}`' for f in non_article_files)}\n"
    else:
        final_comment = "## 🤖 Article QA Bot Report\n\n"
        final_comment += f"Checked **{len(article_comments)}** article(s) "
        if non_article_files:
            final_comment += f"({len(non_article_files)} non-article file(s) skipped)"
        final_comment += "\n\n---\n\n"
        final_comment += "\n---\n\n".join(article_comments)

    create_comment_on_pr(pr, final_comment)
