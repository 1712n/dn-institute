#!/bin/env python

"""
The bot checks if a new article complies with all requirements
"""

import argparse
import os
import sys
import json
from github import Github

# Local imports
from tools.git import get_pull_request, get_diff_by_url, parse_diff
from tools.utils import logging_decorator
from tools.llm_utils import extract_json, remove_plus
import tools.claude_retriever
from tools.claude_retriever.searcher.searchtools.websearch import BraveSearchTool


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


def api_call(query, client, model):
    """
    Make an API call and return the response.
    """
    try:
        return client.completion_with_retrieval(
            query=query,
            model=model,
            n_search_results_to_use=1,
            max_searches_to_try=3,
            max_tokens_to_sample=2000
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
        comment = generate_comment(answer)
        print(comment)
        # only post comment if running on Github Actions
        if os.environ.get("GITHUB_ACTIONS") == "true":
            pull_request.create_issue_comment(comment)
    except Exception as e:
        print(f"Error creating a comment on PR: {e}")


def generate_comment(answer):
    """
    Generate a formatted comment based on the provided answer.
    """
    comment = "## Fact-Checking Results\n\n"
    for claim in answer["fact_checking"]:
        emoji = ":white_check_mark:" if claim["result"].lower() == "true" else ":x:"
        comment += f"- **Claim**: {claim['claim']} {emoji}\n"
        comment += f"  - **Source**: [{claim['source']}]({claim['source']})\n"
        if claim["result"].lower() == "false":
            comment += f"  - **Explanation**: {claim['explanation']}\n"
        comment += "\n"

    comment += "## Spell-Checking Results\n\n"
    for mistake in answer["spell_checking"]:
        comment += f"- **Mistake**: `{mistake['mistake']}`\n"
        comment += f"  - **Correction**: `{mistake['correction']}`\n"
        comment += f"  - **Context**: `{mistake['context']}`\n"
        comment += "\n"

    emoji_hugo = ":white_check_mark:" if answer['hugo_checking'].lower() == "true" else ":x:"
    comment += f"## Hugo SSG Formatting Check\n- Does it match Hugo SSG formatting? {emoji_hugo}\n\n"

    emoji_filename = ":white_check_mark:" if answer['submission_guidelines']['is_filename_correct'].lower() == "true" else ":x:"
    comment += f"## Filename Check\n- Correct Filename: `{answer['submission_guidelines']['correct_filename']}`\n"
    comment += f"- Your Filename: `{answer['submission_guidelines']['article_filename']}` {emoji_filename}\n\n"

    emoji_sections = ":white_check_mark:" if answer['submission_guidelines']['has_allowed_headers'].lower() == "true" else ":x:"
    comment += f"## Section Headers Check\n- Allowed Headers: `{', '.join(answer['submission_guidelines']['allowed_headers'])}`\n"
    comment += f"- Your Headers: `{', '.join(answer['submission_guidelines']['headers_from_text'])}` {emoji_sections}\n\n"

    emoji_headers = ":white_check_mark:" if answer['submission_guidelines']['has_allowed_metadata_headers'].lower() == "true" else ":x:"
    comment += f"## Metadata Headers Check\n- Allowed Metadata Headers: `{', '.join(answer['submission_guidelines']['allowed_metadata_headers'])}`\n"
    comment += f"- Your Metadata Headers: `{', '.join(answer['submission_guidelines']['metadata_headers_from_text'])}` {emoji_headers}\n"

    return comment


PROMPT = """Please review and verify the provided text. This involves two main tasks: fact-checking and spell-checking.

Fact-Checking: Examine each factual statement in the text. Verify these against reliable online sources. Specifically, check the accuracy of numbers, dates, monetary values, and names of people or entities. Report your findings in a structured format, stating whether each claim is true or false, with a source for verification and an explanation if a claim is false.

Spell-Checking: Scan the text for any spelling, grammatical, and punctuation mistakes. List each mistake you find, providing the incorrect and corrected versions.

Additionally, since the text is a Markdown document for Hugo SSG, ensure it adheres to specific formatting requirements:

Check if the document follows the Markdown format, including appropriate headers.
Confirm if it meets submission guidelines, particularly the file naming convention ("YYYY-MM-DD-entity-that-was-hacked.md"). Extract the name of the file from the text and compare it to the correct name.
Verify that the document includes only the allowed headers: "## Summary", "## Attackers", "## Losses", "## Timeline", "## Security Failure Causes".
Check for the presence of specific metadata headers between "---" lines, such as "date", "target-entities", "entity-types", "attack-types", "title", "loss". The document must contain all and only allowed metadata headers.
Example:
Input Text: "bla-bla.md: In July 2011, BTC-e, a cryptocurrency exchange, experienced a security breach that resulted in the loss of around 4,500 BTC."
Present your findings only in a structured JSON format.
Output: {"fact_checking": 
    [
    {"claim": "In July 2011, BTC-e experienced a security breach.",
    "source": "https://bitcoinmagazine.com/business/btc-e-attacked-1343738085",
    "result": "False",
    "explanation": "BTC-e experienced a security breach in July 2012, not 2011"}
    ],
    "spell_checking": [
    {"context": "a cryptocurrency exchange",
    "mistake": "exchange",     
    "correction": "exchange"    
    }  
    ],
    "hugo_checking": "False",
    "submission_guidelines": {
        "article_filename": "bla-bla.md", 
        "correct_filename": "2012-07-16-BTC-e.md",
        "is_filename_correct": "False",
        "allowed_headers": ["## Summary", "## Attackers", "## Losses", "## Timeline", "## Security Failure Causes"],    
        "headers_from_text": "None",    
        "has_allowed_headers": "False",
        "allowed_metadata_headers": ["date", "target-entities", "entity-types", "attack-types", "title", "loss"],
        "metadata_headers_from_text": "None",
        "has_allowed_metadata_headers": "False" 
        }
}

Text for Verification: ```%s```
"""


def main():
    args = parse_cli_args()
    with open('tools/config.json', 'r') as config_file:
        config = json.load(config_file)

    search_tool = BraveSearchTool(brave_api_key=args.SEARCH_API_KEY, summarize_with_claude=True,
                                  anthropic_api_key=args.API_key)
    model = config['ANTHROPIC_SEARCH_MODEL']
    client = tools.claude_retriever.ClientWithRetrieval(api_key=args.API_key, search_tool=search_tool)

    github = Github(args.github_token)
    pr = get_pull_request(github, args.pull_url)
    _diff = get_diff_by_url(pr)
    diff = parse_diff(_diff)

    print('-' * 50)
    print(diff)
    print('-' * 50)


    text = remove_plus(diff[0]['header'] + diff[0]['body'][0]['body'])

    print('-' * 50)
    print(text)
    print('-' * 50)

    query = PROMPT % text

    answer = api_call(query, client, model)
    print('-' * 50)
    print(answer)
    print('-' * 50)

    extracted_answer = extract_json(answer)
    print('-' * 50)
    print(extracted_answer)
    print('-' * 50)
    create_comment_on_pr(pr, extracted_answer)