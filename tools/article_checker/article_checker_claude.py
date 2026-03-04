#!/bin/env python

"""
Improved QA Bot for PR Article Quality Checks

Enhancements:
- Multi-file support: Process ALL article files in PR, not just the first one
- Model upgrades: claude-3-opus → claude-3-5-sonnet, claude-3-haiku → claude-3-5-haiku
- Better fact-checking: Increased search results from 1 to 3
- Retry logic with exponential backoff for API calls
- Better error handling for parsing and API failures
- Configurable parameters via config.json
- Structure validation for submission guidelines compliance
"""

import argparse
import os
import sys
import json
import time
import re
from typing import Optional, List, Dict, Any
from github import Github
from tools.python_modules.git import get_pull_request, get_diff_by_url, parse_diff
from tools.python_modules.utils import logging_decorator
from tools.python_modules.llm_utils import remove_plus
import tools.article_checker.claude_retriever
from tools.article_checker.claude_retriever.searcher.searchtools.websearch import BraveSearchTool


def parse_cli_args():
    """Parse CLI arguments."""
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


def load_config() -> Dict[str, Any]:
    """Load configuration from config.json."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as config_file:
        return json.load(config_file)


def api_call_with_retry(
    query: str, 
    client, 
    model: str, 
    max_tokens: int, 
    temperature: float,
    n_search_results: int = 3,
    max_retries: int = 3
) -> Optional[str]:
    """
    Make an API call with retry logic and improved search coverage.
    
    Args:
        query: The query to send to the LLM
        client: The API client
        model: Model name to use
        max_tokens: Maximum tokens in response
        temperature: Temperature for generation
        n_search_results: Number of search results to use (increased for better fact-checking)
        max_retries: Maximum number of retry attempts
    
    Returns:
        API response or None if all retries failed
    """
    for attempt in range(max_retries):
        try:
            response = client.completion_with_retrieval(
                query=query,
                model=model,
                n_search_results_to_use=n_search_results,
                max_searches_to_try=5,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response
        except Exception as e:
            wait_time = (2 ** attempt)
            print(f"API call attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"All {max_retries} attempts failed")
                return None
    return None


def is_article_file(filename: str) -> bool:
    """
    Check if a file is an article file (content/**/*.md).
    
    Args:
        filename: The file path from the diff
    
    Returns:
        True if it's an article file, False otherwise
    """
    return filename.startswith('content/') and filename.endswith('.md')


def extract_added_content(diff_files: List[Dict]) -> List[Dict[str, str]]:
    """
    Extract added content from all article files in the diff.
    
    Args:
        diff_files: Parsed diff structure
    
    Returns:
        List of dicts with filename and content
    """
    articles = []
    
    for file_diff in diff_files:
        header = file_diff.get('header', '')
        match = re.search(r'b/(.+)', header)
        if not match:
            continue
            
        filename = match.group(1).strip()
        
        if not is_article_file(filename):
            print(f"Skipping non-article file: {filename}")
            continue
        
        added_content = []
        for segment in file_diff.get('body', []):
            body = segment.get('body', '')
            for line in body.split('\n'):
                if line.startswith('+') and not line.startswith('+++'):
                    added_content.append(line[1:])
        
        if added_content:
            full_content = '\n'.join(added_content)
            articles.append({
                'filename': filename,
                'content': remove_plus(full_content)
            })
            print(f"Found article: {filename} ({len(full_content)} chars)")
    
    return articles


def validate_article_structure(content: str, filename: str) -> List[str]:
    """
    Validate article structure against submission guidelines.
    
    Required headers: date, entities, title
    
    Args:
        content: Article content
        filename: Source filename
    
    Returns:
        List of validation issues (empty if valid)
    """
    issues = []
    
    if 'date:' not in content:
        issues.append(f"Missing required 'date' header in {filename}")
    if 'entities:' not in content:
        issues.append(f"Missing required 'entities' header in {filename}")
    if 'title:' not in content:
        issues.append(f"Missing required 'title' header in {filename}")
    
    return issues


@logging_decorator("Comment on PR")
def create_comment_on_pr(pull_request, answer: str):
    """
    Create and post a comment on a Github pull request.
    
    Args:
        pull_request: GitHub PR object
        answer: The comment content
    """
    try:
        print("=" * 60)
        print("QA BOT REVIEW RESULTS")
        print("=" * 60)
        print(answer)
        print("=" * 60)
        
        if os.environ.get("GITHUB_ACTIONS") == "true":
            pull_request.create_issue_comment(answer)
            print("Comment posted to PR successfully")
        else:
            print("Not running on GitHub Actions - comment not posted")
    except Exception as e:
        print(f"Error creating a comment on PR: {e}")


def format_review_results(results: List[Dict[str, Any]]) -> str:
    """
    Format review results into a readable comment.
    
    Args:
        results: List of review results for each article
    
    Returns:
        Formatted markdown comment
    """
    output = ["## 🤖 QA Bot Review Results\n"]
    
    if not results:
        output.append("⚠️ **No article files found in this PR.**\n")
        output.append("Please ensure your PR contains markdown files in the `content/` directory.")
        return '\n'.join(output)
    
    total_articles = len(results)
    passed = sum(1 for r in results if r['status'] == 'passed')
    failed = sum(1 for r in results if r['status'] == 'failed')
    
    output.append(f"**Reviewed {total_articles} article(s):** ✅ {passed} passed, ❌ {failed} need attention\n")
    output.append("---\n")
    
    for result in results:
        filename = result['filename']
        status = result['status']
        status_icon = "✅" if status == 'passed' else "❌"
        
        output.append(f"### {status_icon} {filename}\n")
        
        if result.get('validation_issues'):
            output.append("**Structure Issues:**")
            for issue in result['validation_issues']:
                output.append(f"- ⚠️ {issue}")
            output.append("")
        
        if result.get('analysis'):
            output.append("**Quality Analysis:**")
            output.append(result['analysis'])
            output.append("")
        
        output.append("---\n")
    
    if failed == 0:
        output.append("## ✅ Overall: All articles meet submission guidelines!\n")
        output.append("Great work! The articles appear to follow the required structure and quality standards.")
    else:
        output.append(f"## ⚠️ Overall: {failed} article(s) need attention\n")
        output.append("Please address the issues above before merging.")
    
    return '\n'.join(output)


def main():
    """Main entry point."""
    args = parse_cli_args()
    config = load_config()

    search_tool = BraveSearchTool(
        brave_api_key=args.SEARCH_API_KEY, 
        summarize_with_claude=True,
        anthropic_api_key=args.API_key
    )
    
    model = config.get('ANTHROPIC_SEARCH_MODEL', 'claude-3-5-sonnet-20241022')
    max_tokens = config.get('ANTHROPIC_SEARCH_MAX_TOKENS', 4000)
    temperature = config.get('ANTHROPIC_SEARCH_TEMPERATURE', 0.0)

    client = tools.article_checker.claude_retriever.ClientWithRetrieval(
        api_key=args.API_key, 
        search_tool=search_tool
    )

    github = Github(args.github_token)
    pr = get_pull_request(github, args.pull_url)
    _diff = get_diff_by_url(pr)
    diff = parse_diff(_diff)

    print('-' * 50)
    print(f"Found {len(diff)} file(s) in diff")
    print('-' * 50)

    articles = extract_added_content(diff)
    
    if not articles:
        comment = "## ⚠️ QA Bot Review\n\nNo article files (content/**/*.md) found in this PR. Please ensure your submission contains markdown files in the `content/` directory following the [submission guidelines](https://github.com/1712n/dn-institute/issues/277)."
        create_comment_on_pr(pr, comment)
        return

    results = []
    for article in articles:
        filename = article['filename']
        content = article['content']
        
        print(f"\n{'='*60}")
        print(f"Reviewing: {filename}")
        print(f"{'='*60}")
        
        validation_issues = validate_article_structure(content, filename)
        
        n_search_results = config.get('N_SEARCH_RESULTS_TO_USE', 3)
        max_retries = config.get('GPT_retry', 3)
        
        analysis = api_call_with_retry(
            query=content,
            client=client,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            n_search_results=n_search_results,
            max_retries=max_retries
        )
        
        results.append({
            'filename': filename,
            'status': 'passed' if not validation_issues and analysis else 'failed',
            'validation_issues': validation_issues,
            'analysis': analysis
        })
    
    comment = format_review_results(results)
    create_comment_on_pr(pr, comment)


if __name__ == "__main__":
    main()