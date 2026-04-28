#!/bin/env python

"""
The bot checks if a new article complies with all requirements.
Enhanced with: multi-file parallel processing, duplicate detection,
structured submission guidelines compliance, and actionable markdown feedback.

Addresses Issue #408 - Improve QA Bot
"""

import argparse
import os
import sys
import json
import re
import time
import concurrent.futures
from typing import Dict, List, Optional, Tuple

from github import Github
from tools.python_modules.git import get_pull_request, get_diff_by_url, parse_diff
from tools.python_modules.utils import logging_decorator
from tools.python_modules.llm_utils import remove_plus, count_tokens, trimming_text
import tools.article_checker.claude_retriever
from tools.article_checker.claude_retriever.searcher.searchtools.websearch import BraveSearchTool

# Import duplication checker utilities
try:
    import openai
    from bs4 import BeautifulSoup
    import requests
    DUPLICATION_AVAILABLE = True
except ImportError:
    DUPLICATION_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────
# Submission Guidelines Checklist (Issue #277)
# Each item maps to a checklist the LLM evaluates
# ─────────────────────────────────────────────────────────────────
SUBMISSION_GUIDELINES = """
## Submission Guidelines Compliance Check

Review the PR diff against ALL of the following requirements. For each item,
respond with PASS or FAIL and cite specific evidence from the diff.

### 1. Structure Requirements
- [ ] Article has ## Summary section at the top
- [ ] Article has ## Attack Vector / ## Methodology section (for attack reports)
- [ ] Article has ## Timeline of Events
- [ ] Article has ## Warning Signs / Red Flags section
- [ ] Article has ## Affected Parties section
- [ ] Article has ## References section with at least 3 sources
- [ ] All headers follow "## " Markdown format (not "# " or "### ")

### 2. Content Quality
- [ ] Article is at least 500 words of body text (excluding headers)
- [ ] Contains specific dates, figures, and named entities (no vague language)
- [ ] Describes the mechanism of harm, not just the outcome
- [ ] No first-person ("I", "we") or editorial language
- [ ] Claims are verifiable with cited sources

### 3. Source Requirements
- [ ] At least 3 unique source URLs in ## References
- [ ] Sources are credible (official reports, court documents, news >1 year old)
- [ ] No dead links or placeholder URLs

### 4. Formatting
- [ ] No excessive emoji (max 2-3 per article)
- [ ] No all-caps headers except acronyms
- [ ] Code blocks use triple backticks
- [ ] Tables are properly formatted Markdown

### 5. Wiki-Specific
- [ ] Front matter includes: title, summary, tags, date, author
- [ ] File is placed in correct directory: content/attacks/posts/ or content/research/market-health/posts/
- [ ] Filename is slug-formatted (lowercase-hyphenated.md)
- [ ] No duplicate article on the same topic (check existing wiki)

### 6. Completeness
- [ ] All "TODO" or "TBD" placeholders removed
- [ ] All external resources (images, PDFs) are accessible
- [ ] No Lorem Ipsum or template text remaining

Respond in this exact JSON format:
{
  "checks": {
    "structure": {"pass": true/false, "details": "..."},
    "content": {"pass": true/false, "details": "..."},
    "sources": {"pass": true/false, "details": "..."},
    "formatting": {"pass": true/false, "details": "..."},
    "wiki": {"pass": true/false, "details": "..."},
    "completeness": {"pass": true/false, "details": "..."}
  },
  "overall_pass": true/false,
  "actionable_feedback": ["specific line references and fix suggestions"]
}
"""


def parse_cli_args():
    parser = argparse.ArgumentParser(
        description="Article compliance checker with multi-file support"
    )
    parser.add_argument(
        "--github-token", dest="github_token", help="GitHub token", required=True
    )
    parser.add_argument(
        "--llm-api-key", dest="API_key", help="API key for LLM", required=True
    )
    parser.add_argument(
        "--pull-url", dest="pull_url", help="GitHub pull URL", required=True
    )
    parser.add_argument(
        "--search-api-key", dest="SEARCH_API_KEY",
        help="API key for search engine", required=True
    )
    parser.add_argument(
        "--max-files", dest="max_files", type=int, default=10,
        help="Max files to process in parallel (default: 10)"
    )
    parser.add_argument(
        "--skip-duplicate", dest="skip_duplicate", action="store_true",
        help="Skip duplicate detection check"
    )
    return parser.parse_args()


def api_call(query: str, client, model: str, max_tokens: int, temperature: float) -> Optional[str]:
    """Make an API call with retry logic."""
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
            print(f"API call attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                return None


# ─────────────────────────────────────────────────────────────────
# Duplicate Detection (inline from duplication_checker.py)
# ─────────────────────────────────────────────────────────────────

def get_target_entities(url: str) -> List[str]:
    """Fetch list of target entities from the wiki."""
    if not DUPLICATION_AVAILABLE:
        return []
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            return [li.find('a').text for li in soup.find_all('li', class_='section-item')
                    if li.find('a')]
    except Exception as e:
        print(f"Failed to fetch target entities: {e}")
    return []


def find_existing_articles(target: str, base_url: str) -> List[str]:
    """Find existing articles for a target entity."""
    if not DUPLICATION_AVAILABLE:
        return []
    target_entities_url = f"{base_url}/attacks/posts/target-entities/"
    entities = get_target_entities(target_entities_url)
    if target not in entities:
        return []
    href_list = []
    try:
        resp = requests.get(target_entities_url + target.replace(' ', '-'), timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            for article in soup.find_all('article', class_='markdown book-post'):
                h2 = article.find('h2')
                if h2 and h2.find('a'):
                    href_list.append(h2.find('a')['href'])
    except Exception as e:
        print(f"Failed to find existing articles: {e}")
    return href_list


def check_duplicate(new_text: str, target: str, config: dict, api_key: str) -> Tuple[bool, str]:
    """Check if article is duplicate of existing wiki content."""
    if not DUPLICATION_AVAILABLE or not target:
        return False, ":white_check_mark:"

    main_url = "https://dn.institute"
    target_entities_url = f"{main_url}/attacks/posts/target-entities/"
    existing = find_existing_articles(target, main_url)

    if not existing:
        return False, ":white_check_mark:"

    prompt = (
        "Compare two texts and determine if they cover the SAME incident/event. "
        "Return True only if both texts describe the same specific event with similar details.\n\n"
        f"NEW ARTICLE:\n```{new_text[:2000]}```\n\n"
        f"EXISTING WIKI ARTICLE:\n```{new_text[:2000]}```\n\n"
        'Output JSON: {"is_duplicate": true/false, "reason": "..."}'
    )

    try:
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model=config.get("GPT_MODEL", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": "Return output as JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=float(config.get("GPT_temperature", 0)),
            max_tokens=int(config.get("GPT_max_tokens", 500)),
            response_format={"type": "json_object"}
        )
        result = json.loads(response['choices'][0]['message']['content'].strip())
        if result.get("is_duplicate"):
            return True, f":x: **Possible duplicate detected**: {result.get('reason', '')}"
        return False, ":white_check_mark:"
    except Exception as e:
        print(f"Duplicate check failed: {e}")
        return False, ":white_check_mark:"


def extract_target_entity(text: str) -> str:
    """Extract target-entities from article front matter."""
    match = re.search(r'target-entities:\s+(.*?)\n', text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Try to infer from title
    title_match = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    if title_match:
        return title_match.group(1).strip()
    return ""


# ─────────────────────────────────────────────────────────────────
# Fact-Check + Guidelines Compliance
# ─────────────────────────────────────────────────────────────────

def analyze_file(diff_entry: dict, client, model: str, max_tokens: int, temperature: float) -> dict:
    """
    Analyze a single file's diff for both fact-checking and guidelines compliance.
    Returns structured results.
    """
    header = diff_entry.get('header', '')
    body_segments = diff_entry.get('body', [])

    # Combine all body segments
    text = remove_plus(header)
    for seg in body_segments:
        if isinstance(seg, dict):
            text += "\n" + remove_plus(seg.get('body', ''))
        elif isinstance(seg, str):
            text += "\n" + remove_plus(seg)

    # Token budget check — trim if too long
    token_count = count_tokens(text) if 'count_tokens' in dir() else len(text) // 4
    if token_count > max_tokens:
        text = trimming_text(text, max_tokens * 0.8) if 'trimming_text' in dir() else text[:int(max_tokens * 3.5)]

    # Step 1: Guidelines compliance check
    guidelines_query = (
        f"Article content:\n{text[:3000]}\n\n{SUBMISSION_GUIDELINES}"
    )
    guidelines_result = api_call(guidelines_query, client, model, max_tokens, temperature)

    # Step 2: Fact-checking (original behavior)
    fact_query = (
        "You are a financial crime investigator. Review the following article for accuracy. "
        "Identify any factual errors, unsubstantiated claims, or missing critical information. "
        "Be specific — cite line numbers or content when possible.\n\n"
        f"Article:\n{text[:3000]}"
    )
    fact_result = api_call(fact_query, client, model, max_tokens, temperature)

    return {
        'header': header,
        'guidelines_result': guidelines_result,
        'fact_result': fact_result,
        'text_length': len(text),
    }


def process_diff_files(
    diff: List[dict],
    client,
    model: str,
    max_tokens: int,
    temperature: float,
    max_workers: int = 5
) -> List[dict]:
    """
    Process multiple files in parallel using ThreadPoolExecutor.
    Falls back to sequential if parallel fails.
    """
    if len(diff) == 1:
        return [analyze_file(diff[0], client, model, max_tokens, temperature)]

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(analyze_file, f, client, model, max_tokens, temperature): i
            for i, f in enumerate(diff)
        }
        for future in concurrent.futures.as_completed(future_to_file):
            idx = future_to_file[future]
            try:
                result = future.result(timeout=120)
                results.append((idx, result))
            except Exception as e:
                print(f"Error processing file {idx}: {e}")
                results.append((idx, {'error': str(e)}))

    # Sort by original index to maintain order
    results.sort(key=lambda x: x[0])
    return [r for _, r in results]


# ─────────────────────────────────────────────────────────────────
# PR Comment Generation
# ─────────────────────────────────────────────────────────────────

def parse_guidelines_result(result: dict) -> dict:
    """Parse the guidelines compliance JSON from LLM response."""
    try:
        if isinstance(result, str):
            # Try to extract JSON from the string
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        return {'overall_pass': False, 'actionable_feedback': [str(result)[:500]]}
    except (json.JSONDecodeError, AttributeError):
        return {'overall_pass': False, 'actionable_feedback': [str(result)[:500] if result else 'No result']}


def generate_pr_comment(
    file_results: List[dict],
    duplicate_status: str,
    model: str
) -> str:
    """Generate an actionable, well-formatted PR comment."""

    # Parse all guidelines results
    all_checks = []
    all_feedback = []
    overall_pass = True

    for fr in file_results:
        if 'error' in fr:
            all_feedback.append(f"  - File analysis error: {fr['error']}")
            continue

        gl_result = fr.get('guidelines_result', '')
        parsed = parse_guidelines_result(gl_result)
        checks = parsed.get('checks', {})
        all_checks.append({
            'file': fr.get('header', 'unknown')[:80],
            'checks': checks,
            'fact': fr.get('fact_result', '')[:500]
        })
        if not parsed.get('overall_pass', True):
            overall_pass = False
        all_feedback.extend(parsed.get('actionable_feedback', []))

    # Header
    status_emoji = ":white_check_mark:" if overall_pass else ":warning:"
    comment = f"""## QA Bot Check Results {status_emoji}

**Model:** {model}  
**Files reviewed:** {len(file_results)}

"""

    # Duplicate status
    comment += f"**Duplicate Check:** {duplicate_status}\n\n"

    # Per-file guidelines checklist
    comment += "### Submission Guidelines Compliance\n\n"
    comment += "| File | Structure | Content | Sources | Formatting | Wiki | Complete | Overall |\n"
    comment += "|------|-----------|---------|---------|-----------|-----|----------|---------|\n"

    for fc in all_checks:
        checks = fc.get('checks', {})
        def check_cell(v):
            if isinstance(v, dict):
                return ":white_check_mark:" if v.get('pass') else ":x:"
            return ":grey_question:"
        comment += f"| {fc['file'][:40]} | "
        comment += f"{check_cell(checks.get('structure'))} | "
        comment += f"{check_cell(checks.get('content'))} | "
        comment += f"{check_cell(checks.get('sources'))} | "
        comment += f"{check_cell(checks.get('formatting'))} | "
        comment += f"{check_cell(checks.get('wiki'))} | "
        comment += f"{check_cell(checks.get('completeness'))} | "
        comment += f"{':white_check_mark:' if checks and all(v.get('pass', True) for v in checks.values()) else ':x:'} |\n"

    # Actionable feedback
    if all_feedback:
        comment += "\n### Actionable Feedback\n\n"
        for i, fb in enumerate(all_feedback[:15], 1):  # Limit to 15 items
            comment += f"{i}. {fb}\n"
        if len(all_feedback) > 15:
            comment += f"\n_... and {len(all_feedback) - 15} more items_\n"

    # Summary
    if overall_pass:
        comment += "\n---\n:white_check_mark: **All checks passed!** Ready for review."
    else:
        comment += "\n---\n:x: **Some requirements not met.** Please address the items above before re-submitting."

    comment += "\n\n*This check was performed automatically by the QA Bot. "
    comment += "If you believe a check is incorrect, please explain and re-request with `/articlecheck`.*"

    return comment


@logging_decorator("Comment on PR")
def create_comment_on_pr(pull_request, answer: str):
    """Create and post a comment on a GitHub pull request."""
    try:
        print(f"Comment preview:\n{answer[:500]}")
        if os.environ.get("GITHUB_ACTIONS") == "true":
            pull_request.create_issue_comment(answer)
    except Exception as e:
        print(f"Error creating comment on PR: {e}")


# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────

def main():
    args = parse_cli_args()

    with open('tools/article_checker/config.json', 'r') as config_file:
        config = json.load(config_file)

    # Initialize search tool and client
    search_tool = BraveSearchTool(
        brave_api_key=args.SEARCH_API_KEY,
        summarize_with_claude=True,
        anthropic_api_key=args.API_key
    )
    client = tools.article_checker.claude_retriever.ClientWithRetrieval(
        api_key=args.API_key,
        search_tool=search_tool
    )

    model = config['ANTHROPIC_SEARCH_MODEL']
    max_tokens = config['ANTHROPIC_SEARCH_MAX_TOKENS']
    temperature = config['ANTHROPIC_SEARCH_TEMPERATURE']

    # Get PR and diff
    github = Github(args.github_token)
    pr = get_pull_request(github, args.pull_url)
    _diff = get_diff_by_url(pr)
    diff = parse_diff(_diff)

    print(f"Processing {len(diff)} file(s)...")

    # 1. Duplicate detection
    if not args.skip_duplicate and diff:
        combined_text = remove_plus(diff[0]['header'] + diff[0]['body'][0]['body'])
        target = extract_target_entity(combined_text)
        is_dup, dup_status = check_duplicate(combined_text, target, config, args.API_key)
        print(f"Duplicate check: {dup_status}")
    else:
        dup_status = ":white_check_mark: (skipped)"
        is_dup = False

    # 2. Multi-file analysis (parallel)
    file_results = process_diff_files(
        diff,
        client,
        model,
        max_tokens,
        temperature,
        max_workers=args.max_files
    )

    # 3. Generate and post comment
    comment = generate_pr_comment(file_results, dup_status, model)
    create_comment_on_pr(pr, comment)


if __name__ == "__main__":
    main()
