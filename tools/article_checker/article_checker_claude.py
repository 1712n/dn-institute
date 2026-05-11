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
import tools.article_checker.claude_retriever
from tools.article_checker.claude_retriever.searcher.searchtools.websearch import BraveSearchTool

ARTICLE_PATH_PREFIXES = (
    "content/attacks/",
    "content/research/cyberattacks/incidents/",
)
ALLOWED_METADATA_HEADERS = {
    "date",
    "target-entities",
    "entity-types",
    "attack-types",
    "title",
    "loss",
}
REQUIRED_SECTION_HEADERS = {
    "## Summary",
    "## Attackers",
    "## Losses",
    "## Timeline",
    "## Security Failure Causes",
}


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
            n_search_results_to_use=3,
            max_searches_to_try=8,
            max_tokens=max_tokens,
            temperature=temperature
        )
    except Exception as e:
        print(f"Error in API call: {e}")
        return None


def extract_file_path(diff_header: str) -> str:
    """
    Extract the new file path from a unified diff file header.
    """
    for line in diff_header.splitlines():
        if line.startswith("+++ b/"):
            return line.removeprefix("+++ b/").strip()
        if line.startswith("+++ "):
            return line.removeprefix("+++ ").strip()
    match = re.search(r" b/([^\s]+)", diff_header)
    return match.group(1) if match else ""


def is_article_path(path: str) -> bool:
    """
    Check whether a file path is a Markdown article managed by the QA bot.
    """
    return path.endswith(".md") and any(
        path.startswith(prefix) for prefix in ARTICLE_PATH_PREFIXES
    )


def is_new_file_diff(diff_header: str) -> bool:
    """
    Check whether a diff header represents a newly added file.
    """
    return "new file mode" in diff_header or "--- /dev/null" in diff_header


def extract_added_lines(hunk_body: str) -> list[str]:
    """
    Return only added content lines from a diff hunk, excluding diff metadata.
    """
    return [
        line[1:]
        for line in hunk_body.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]


def collect_changed_articles(diff: list[dict]) -> list[dict]:
    """
    Collect all changed article Markdown files from a parsed PR diff.
    """
    articles = []
    for file_diff in diff:
        path = extract_file_path(file_diff["header"])
        if not is_article_path(path):
            continue

        added_lines = []
        for hunk in file_diff["body"]:
            added_lines.extend(extract_added_lines(hunk["body"]))

        if added_lines:
            articles.append({
                "path": path,
                "text": "\n".join(added_lines),
                "is_new_file": is_new_file_diff(file_diff["header"]),
            })
    return articles


def parse_front_matter(text: str) -> dict[str, str]:
    """
    Parse simple Hugo YAML front matter keys without adding a YAML dependency.
    """
    if not text.startswith("---"):
        return {}

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}

    front_matter = {}
    for raw_line in parts[1].splitlines():
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        front_matter[key.strip()] = value.strip()
    return front_matter


def extract_markdown_headers(text: str) -> list[str]:
    """
    Extract level-two-or-deeper Markdown headers from an article body.
    """
    return [
        line.strip()
        for line in text.splitlines()
        if line.startswith("##")
    ]


def analyze_article_structure(path: str, text: str, is_new_file: bool = True) -> str:
    """
    Produce deterministic review notes before the LLM fact-checking pass.
    """
    notes = [f"### Preflight: `{path}`"]
    file_name = os.path.basename(path)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}-.+\.md", file_name):
        notes.append("- Filename shape: pass")
    else:
        notes.append(
            "- Filename shape: fail. Expected `YYYY-MM-DD-entity-that-was-hacked.md`."
        )

    headers = extract_markdown_headers(text)
    if is_new_file:
        metadata = parse_front_matter(text)
        metadata_keys = set(metadata.keys())
        missing_keys = sorted(ALLOWED_METADATA_HEADERS - metadata_keys)
        extra_keys = sorted(metadata_keys - ALLOWED_METADATA_HEADERS)
        if not metadata:
            notes.append("- Front matter: fail. Missing opening and closing `---` block.")
        elif missing_keys or extra_keys:
            notes.append(
                "- Front matter keys: warning. "
                f"Missing: {missing_keys or 'none'}; unexpected: {extra_keys or 'none'}."
            )
        else:
            notes.append("- Front matter keys: pass")

        header_set = set(headers)
        missing_headers = sorted(REQUIRED_SECTION_HEADERS - header_set)
        extra_headers = sorted(header_set - REQUIRED_SECTION_HEADERS)
        if missing_headers or extra_headers:
            notes.append(
                "- Section headers: warning. "
                f"Missing: {missing_headers or 'none'}; unexpected: {extra_headers or 'none'}."
            )
        else:
            notes.append("- Section headers: pass")
    else:
        added_unexpected_headers = sorted(
            set(headers) - REQUIRED_SECTION_HEADERS
        )
        if added_unexpected_headers:
            notes.append(
                "- Added section headers: warning. "
                f"Unexpected headers in changed lines: {added_unexpected_headers}."
            )
        else:
            notes.append(
                "- Full-article structure checks: skipped because this is an edit to an existing article diff, not a full new-file diff."
            )

    if len(text.strip()) < 500:
        notes.append("- Article length: warning. Added article text is very short.")
    else:
        notes.append("- Article length: pass")

    return "\n".join(notes)


def build_review_input(diff: list[dict]) -> tuple[str, list[str]]:
    """
    Build the LLM input from every changed article file, not just the first diff.
    """
    articles = collect_changed_articles(diff)
    if not articles:
        return (
            "No changed attack article Markdown files were found in this pull request.",
            [],
        )

    preflight_blocks = []
    article_blocks = []
    for article in articles:
        preflight_blocks.append(
            analyze_article_structure(
                article["path"],
                article["text"],
                is_new_file=article["is_new_file"],
            )
        )
        article_blocks.append(
            f"<article_file path=\"{article['path']}\">\n{article['text']}\n</article_file>"
        )

    prompt = "\n\n".join(
        [
            "Review every changed attack article below. Start with the deterministic preflight notes, then perform fact-checking, source review, style review, Hugo formatting checks, and submission-guideline checks.",
            "<deterministic_preflight>",
            "\n\n".join(preflight_blocks),
            "</deterministic_preflight>",
            "<changed_articles>",
            "\n\n".join(article_blocks),
            "</changed_articles>",
        ]
    )
    return prompt, [article["path"] for article in articles]


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

    text, article_paths = build_review_input(diff)
    if not article_paths:
        answer = (
            "## Article Check\n\n"
            "No changed attack article Markdown files were found in this pull request. "
            "Expected a Markdown file under `content/attacks/` or "
            "`content/research/cyberattacks/incidents/`."
        )
    else:
        answer = api_call(text, client, model, max_tokens, temperature)
        if answer is None:
            answer = (
                "## Article Check\n\n"
                "The deterministic preflight ran, but the Claude retrieval pass failed. "
                "Please rerun `/articlecheck` or inspect the action logs.\n\n"
                f"{text}"
            )
    print('-' * 50)
    print('This is an answer', answer)
    print('-' * 50)

    create_comment_on_pr(pr, answer)
