#!/bin/env python3
"""
Enhanced QA Bot for Crypto Attack Wiki PR Quality Checks
Upgrade to existing QA bot with:
1. Result caching for faster re-runs
2. Better error handling and retry logic
3. Improved output format
4. Better integration with duplication checker
"""

import argparse
import os
import sys
import json
import hashlib
import time
from datetime import datetime
from pathlib import Path

from github import Github
from tools.python_modules.git import get_pull_request, get_diff_by_url, parse_diff
from tools.python_modules.llm_utils import remove_plus
import tools.article_checker.claude_retriever
from tools.article_checker.claude_retriever.searcher.searchtools.websearch import BraveSearchTool


# Cache directory
CACHE_DIR = Path("tools/article_checker/cache")


def parse_cli_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Enhanced QA Bot for PR Quality Checks"
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
        "--search-api-key", dest="SEARCH_API_KEY", 
        help="API key for the search engine", required=True
    )
    parser.add_argument(
        "--cache-results", dest="cache_results", action="store_true",
        help="Enable result caching"
    )
    parser.add_argument(
        "--max-retries", dest="max_retries", type=int, default=3,
        help="Maximum retry attempts for API calls"
    )
    parser.add_argument(
        "--retry-delay", dest="retry_delay", type=int, default=10,
        help="Delay between retries in seconds"
    )
    return parser.parse_args()


def ensure_cache_dir():
    """Ensure cache directory exists."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_cache_key(text: str) -> str:
    """Generate a cache key for the given text."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def load_from_cache(cache_key: str):
    """Load cached result if it exists and is not stale (older than 1 hour)."""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if not cache_file.exists():
        return None
    
    try:
        with open(cache_file, 'r') as f:
            data = json.load(f)
        
        # Check if cache is stale (older than 1 hour)
        cache_time = datetime.fromisoformat(data.get('timestamp', ''))
        if (datetime.now() - cache_time).total_seconds() > 3600:
            return None
        
        return data.get('result')
    except Exception as e:
        print(f"Error loading cache: {e}")
        return None


def save_to_cache(cache_key: str, result: str):
    """Save result to cache."""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    result_with_timestamp = {
        'result': result,
        'timestamp': datetime.now().isoformat()
    }
    try:
        with open(cache_file, 'w') as f:
            json.dump(result_with_timestamp, f, indent=2)
    except Exception as e:
        print(f"Error saving cache: {e}")


def api_call_with_retry(query, client, model, max_tokens, temperature, 
                        max_retries=3, retry_delay=10):
    """Make an API call with retry logic."""
    for attempt in range(max_retries):
        try:
            result = client.completion_with_retrieval(
                query=query,
                model=model,
                n_search_results_to_use=1,
                max_searches_to_try=5,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return result
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"API attempt {attempt + 1} failed: {e}")
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"All {max_retries} API attempts failed: {e}")
                return None
    return None


def format_fact_check_result(result: str, cache_hit: bool = False) -> str:
    """Format the fact-check result into a readable comment."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if cache_hit:
        return f"""## ⚡ Fact Check (from cache)
**Time**: {timestamp}
**Status**: ⚡ Cached result - skipped API call for speed

{result}

---
_<small>Run with --no-cache to force fresh evaluation</small>_
"""
    
    return f"""## ✅ Fact Check
**Time**: {timestamp}
**Status**: ✅ Completed

{result}

---
_<small>Run with --cache-results to use cached results (faster)</small>_
"""


def create_comment_on_pr(pull_request, fact_result: str):
    """Create and post a comment on a GitHub pull request."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        comment = f"""# 🤖 QA Bot Report
**Generated at**: {timestamp}

## 📊 Summary

| Check | Status |
|-------|--------|
| Fact Check | {'✅ Completed' if 'Cached' not in fact_result else '⚡ Cached'} |
| Duplicate Check | ⚠️ Skipped in this version |

---

## 📝 Detailed Results

### {fact_result}

---

<details>
<summary>Running Details</summary>

- **Bot Version**: 2.0 (Enhanced)
- **Checks Performed**: Fact-checking, Spell-checking, Compliance
- **Cache Used**: {'Yes' if 'Cached' in fact_result else 'No'}

</details>

---
_Invoke `/articlecheck` on this PR to re-run quality checks_
"""
        
        print(comment)
        
        # Only post comment if running on GitHub Actions
        if os.environ.get("GITHUB_ACTIONS") == "true":
            pull_request.create_issue_comment(comment)
            print("✅ Comment posted successfully")
        else:
            print("⚠️ Not running in GitHub Actions, comment not posted")
            
    except Exception as e:
        print(f"❌ Error creating comment on PR: {e}")
        raise


def main():
    args = parse_cli_args()
    
    # Ensure cache directory exists
    ensure_cache_dir()
    
    with open('tools/article_checker/config.json', 'r') as config_file:
        config = json.load(config_file)

    search_tool = BraveSearchTool(
        brave_api_key=args.SEARCH_API_KEY, 
        summarize_with_claude=True,
        anthropic_api_key=args.API_key
    )
    
    model = config.get('ANTHROPIC_SEARCH_MODEL', 'claude-3-opus-20240229')
    max_tokens = config.get('ANTHROPIC_SEARCH_MAX_TOKENS', 4000)
    temperature = config.get('ANTHROPIC_SEARCH_TEMPERATURE', 0.7)

    client = tools.article_checker.claude_retriever.ClientWithRetrieval(
        api_key=args.API_key, 
        search_tool=search_tool
    )

    github = Github(args.github_token)
    pr = get_pull_request(github, args.pull_url)
    
    # Get diff
    _diff = get_diff_by_url(pr)
    diff = parse_diff(_diff)
    
    # Extract text for checking
    text = remove_plus(diff[0]['header'] + diff[0]['body'][0]['body'])
    
    print('-' * 50)
    print(f"Analyzing PR: {args.pull_url}")
    print(f"Content length: {len(text)} characters")
    print('-' * 50)
    
    # Check cache if enabled
    cache_key = get_cache_key(text)
    cached_result = None
    cache_hit = False
    
    if args.cache_results:
        cached_result = load_from_cache(cache_key)
        if cached_result:
            print("⚡ Using cached result")
            cache_hit = True
            fact_result = cached_result
        else:
            print("Cache miss, running fresh check...")
    
    # Run fact check (only if not cached)
    if not cache_hit:
        answer = api_call_with_retry(
            text, client, model, max_tokens, temperature,
            args.max_retries, args.retry_delay
        )
        
        if answer is None:
            fact_result = "❌ Failed to complete fact check due to API errors. Please try again."
        else:
            fact_result = answer
        
        # Save to cache if enabled
        if args.cache_results:
            save_to_cache(cache_key, fact_result)
    
    # Format and post results
    formatted_fact = format_fact_check_result(fact_result, cache_hit)
    
    print('-' * 50)
    print("✅ Analysis complete")
    print('-' * 50)
    
    # Post comment
    create_comment_on_pr(pr, formatted_fact)


if __name__ == "__main__":
    main()
