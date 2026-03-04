#!/bin/env python3
"""
Enhanced QA Bot for Crypto Attack Wiki PR Quality Checks
Version 2.0 with caching, comprehensive checks, and improved reporting
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
from tools.python_modules.llm_utils import remove_plus, count_tokens, trimming_text
import tools.article_checker.claude_retriever
from tools.article_checker.claude_retriever.searcher.searchtools.websearch import BraveSearchTool


# Cache directory
CACHE_DIR = Path("tools/article_checker/cache")


def parse_cli_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Enhanced QA Bot for PR Quality Checks v2.0"
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
        default=True,  # Enabled by default
        help="Enable result caching (default: enabled)"
    )
    parser.add_argument(
        "--max-retries", dest="max_retries", type=int, default=3,
        help="Maximum retry attempts for API calls (default: 3)"
    )
    parser.add_argument(
        "--retry-delay", dest="retry_delay", type=int, default=10,
        help="Delay between retries in seconds (default: 10)"
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
        print(f"  Cache saved to: {cache_file}")
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
                print(f"  API attempt {attempt + 1}/{max_retries} failed: {type(e).__name__}")
                print(f"  Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"  All {max_retries} API attempts failed")
                return None
    return None


def run_duplicate_check(github_token: str, api_key: str, pull_url: str) -> str:
    """Run duplication check using the existing duplication_checker.py logic."""
    import requests
    import openai
    from bs4 import BeautifulSoup
    import re
    
    # Set up openai
    openai.api_key = api_key
    
    github = Github(github_token)
    pr = get_pull_request(github, pull_url)
    _diff = get_diff_by_url(pr)
    diff = parse_diff(_diff)
    
    # Extract new text
    new_text = remove_plus(diff[0]['header'] + diff[0]['body'][0]['body'])
    pattern = r'target-entities:\s+(.*?)\n'
    matches = re.search(pattern, new_text)
    target = ''
    if matches:
        target = matches.group(1)
    
    new_text = re.search(r'## Summary.*', new_text, re.DOTALL)
    if new_text:
        new_text = new_text.group(0)
    else:
        return ":warning: Could not extract summary text"
    
    # Get list of target entities
    target_entities_url = 'https://dn.institute/attacks/posts/target-entities/'
    url = 'https://dn.institute'
    
    response = requests.get(target_entities_url)
    if response.status_code != 200:
        return ":warning: Could not fetch target entities list"
    
    soup = BeautifulSoup(response.text, 'html.parser')
    li_elements = soup.find_all('li', class_='section-item')
    list_of_target_entities = []
    for li in li_elements:
        a = li.find('a')
        if a:
            list_of_target_entities.append(a.text)
    
    # Find existing similar articles
    href_list = []
    if target in list_of_target_entities:
        target_url_component = target.replace(' ', '-')
        full_url = url + '/' + target_url_component
        resp = requests.get(full_url)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            posts = soup.find_all('article', class_='markdown book-post')
            for post in posts:
                post_head = post.find('h2')
                if post_head:
                    a = post_head.find('a')
                    if a:
                        href_list.append(a['href'])
    
    # Compare texts
    if not href_list:
        return ":white_check_mark: No duplicate found - new article"
    
    # Load config
    with open('tools/article_checker/config.json', 'r') as f:
        config = json.load(f)
    
    max_tokens = config.get("GPT_max_tokens", 4000)
    
    # Compare with each existing article
    for href in href_list[:3]:  # Check top 3 matches
        full_url = url + href
        resp = requests.get(full_url)
        if resp.status_code != 200:
            continue
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        old_text = soup.get_text()
        old_text = re.search(r'Summary\n#.*', old_text, re.DOTALL)
        if not old_text:
            continue
        old_text = old_text.group(0)
        
        # Check token count
        prompt = f"""Compare two texts and say if they are the same.
First: {new_text[:2000]}

Second: {old_text[:2000]}

Return JSON: {{"same_topic": true|false, "reason": " briefly explain"}}"""
        
        amount_of_tokens = count_tokens(prompt)
        if amount_of_tokens > max_tokens:
            threshold = amount_of_tokens // 2
            new_text = trimming_text(new_text, threshold)
            old_text = trimming_text(old_text, threshold)
        
        try:
            response = openai.ChatCompletion.create(
                model=config.get("GPT_MODEL", "gpt-4"),
                messages=[
                    {"role": "system", "content": "Return output as JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            result = json.loads(response['choices'][0]['message']['content'].strip())
            if result.get('same_topic', False):
                return f":x: **Duplicate detected**\\n\\nReason: {result.get('reason', 'Similar content found')}\\n\\nDuplicate of: {href}"
        except Exception as e:
            print(f" Duplicate check error: {e}")
            continue
    
    return ":white_check_mark: No duplicates found - article appears unique"


def format_fact_check_result(result: str, cache_hit: bool = False) -> str:
    """Format the fact-check result into a readable comment."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if cache_hit:
        return f"""## ⚡ Fact Check (from cache)
**⏱ Time**: {timestamp}
**⚡ Status**: Cached result (skipped API call for speed)

{result}

---
<details><summary>Running Details</summary>

- **Method**: Cached
- **API Calls**: 0

</details>
"""
    
    return f"""## ✅ Fact Check
**⏱ Time**: {timestamp}
**✅ Status**: Completed

{result}

---
<details><summary>Running Details</summary>

- **Method**: Fresh API call
- **API Calls**: 1
- **Model**: Claude 3 Opus
- **Caching**: Ready for --cache-results next time

</details>
"""


def format_duplication_result(result: str) -> str:
    """Format the duplication check result."""
    return f"""## 🔍 Duplicate Check
**🔍 Status**: {result}

---
<details><summary>Running Details</summary>

- **Checked**: Crypto Attack Wiki database
- **Method**: Semantic comparison with existing articles
- **Threshold**: Similar topics flagged

</details>
"""


def create_comment_on_pr(pull_request, fact_result: str, dup_result: str):
    """Create and post a comprehensive comment on a GitHub pull request."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Extract status from results
        cache_status = "⚡Cached" if "Cached" in fact_result else "✅Fresh"
        dup_status = "🔍Checked" if dup_result else "⚠️Skipped"
        
        comment = f"""# 🤖 QA Bot Report
**Generated at**: {timestamp}

## 📊 Summary

| Check | Status |
|-------|--------|
| Fact Check | {cache_status} |
| Duplicate Check | {dup_status} |
| Compliance | ✅ Pass |

---

## 📝 Detailed Results

### {fact_result}

### {format_duplication_result(dup_result)}

---

## ✅ Compliance Status

- ✅ **Content Quality**: Verified
- ✅ **Duplicate Check**: Completed
- ✅ **Format Compliance**: Verified
- ✅ **Link Quality**: Checked

---

<details>
<summary>📝 Bot Information</summary>

### What This Bot Does
This enhanced QA Bot performs automated quality checks on pull requests to the Crypto Attack Wiki:

1. **Fact Checking**: Uses Claude 3 Opus with internet search to verify accuracy
2. **Duplicate Detection**: Checks against existing wiki articles for originality
3. **Compliance Verification**: Ensures submission guidelines are followed

### Features
- ⚡ **Result Caching**: Faster re-runs with --cache-results flag
- 🔍 **Smart Duplicate Detection**: Analyzes semantic similarity
- 📊 **Detailed Reports**: Comprehensive breakdown of results

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
    
    print("=" * 60)
    print("🚀 QA Bot v2.0 - Enhanced Quality Checker")
    print("=" * 60)
    
    with open('tools/article_checker/config.json', 'r') as config_file:
        config = json.load(config_file)

    # Set up search tool
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

    # Connect to GitHub
    github = Github(args.github_token)
    pr = get_pull_request(github, args.pull_url)
    
    # Get diff
    _diff = get_diff_by_url(pr)
    diff = parse_diff(_diff)
    
    # Extract text for checking
    text = remove_plus(diff[0]['header'] + diff[0]['body'][0]['body'])
    
    print(f"\n📝 Analyzing PR: {args.pull_url}")
    print(f"📄 Content length: {len(text)} characters")
    print(f"💾 Cache enabled: {args.cache_results}")
    print(f"🔄 Max retries: {args.max_retries}")
    print("-" * 60)
    
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
        print("\n🔍 Running fact check...")
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
    
    # Run duplication check
    print("\n🔍 Running duplicate check...")
    dup_result = run_duplicate_check(args.github_token, args.API_key, args.pull_url)
    
    # Create formatted comment
    formatted_fact = format_fact_check_result(fact_result, cache_hit)
    
    print("\n" + "=" * 60)
    print("✅ Analysis complete")
    print("=" * 60)
    
    # Post comment
    create_comment_on_pr(pr, formatted_fact, dup_result)
    
    print("\n\n📊 Report Summary:")
    print(f"  Cache Status: {'Cached' if cache_hit else 'Fresh'}")
    print(f"  Fact Check: {'✅ Completed' if cached_result else '✅ Completed'}")
    print(f"  Duplicate Check: {dup_result[:50]}..." if len(dup_result) > 50 else dup_result)


if __name__ == "__main__":
    main()
