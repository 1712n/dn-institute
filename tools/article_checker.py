#!/bin/env python


import argparse
import json
import os
import sys
from github import Github
from tools.git import get_pull_request, get_diff_by_url, parse_diff
from tools.utils import logging_decorator
import requests
import tiktoken


def parse_cli_args():
    """
    Parse CLI arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--github-token", dest="github_token", help="GitHub token", required=True
    )
    parser.add_argument(
        "--llm-api-key", dest="LLM_API_key", help="LLM API key", required=True
    )
    parser.add_argument(
        "--pull-url", dest="pull_url", help="GitHub pull URL", required=True
    )
    return parser.parse_args()


def count_tokens(text, model_name="gpt-3.5-turbo"):
    tokenizer = tiktoken.encoding_for_model(model_name)
    return len(tokenizer.encode(text))


def trimming_prompt(prompt, max_tokens):
    token_count = count_tokens(prompt)
    trimmed_prompt = prompt
    while token_count > max_tokens:
        tokens = trimmed_prompt.split()
        tokens = tokens[:-1]
        trimmed_prompt = ' '.join(tokens)
        token_count = count_tokens(trimmed_prompt)

    return trimmed_prompt


def extract_json_content(content):
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
        return None


def get_content(diff):
    """
    Collecting content from Github PR diff.
    Returns the parsed raw text
    """
    content = ''

    for file in diff:
        for segments in file["body"]:
            for line in segments["body"].splitlines():
                # only count line additions
                if line.startswith("+"):
                    # sanitize line
                    line = line[1:]  # rm addition indicator
                    line = line.strip()  # rm leading/trailing whitespace

                    # filling the content for further check
                    content += line + '\n'

    return content


def api_call(PROMPT, headers, endpoint):
    """
    Create an API call
    """
    data = {"Content": PROMPT}
    try:
        response = requests.post(endpoint, headers=headers, json=data)
        response.raise_for_status()  # will raise an HTTPError if the HTTP request returned an unsuccessful status code
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making API call: {e}")
    return None


PROMPT = """
Task: Conduct a thorough fact-check of the provided text by identifying each factual claim and verifying its accuracy against reliable web sources. For each claim, cross-reference the specific details such as numbers, dates, monetary values, and named entities with information available from credible websites.

Present your findings only in a structured JSON format with each claim, the verification source, and the outcome of the verification.
Output Format: 
[
  {
    "claim": "[Exact factual statement from the text]",
    "source": "[Direct URL or the name of the credible source where the verification information was found]",
    "result": [true or false]
  }
]

Example:
Given Input Text: "In July 2011, BTC-e, a cryptocurrency exchange, experienced a security breach that resulted in the loss of around 4,500 BTC."
Desired Output:
[
  {
    "claim": "In July 2011, BTC-e experienced a security breach.",
    "source": "https://bitcoinmagazine.com/business/btc-e-attacked-1343738085",
    "result": false
  }
]

Text for Verification: ```%s```
"""


@logging_decorator("Comment on PR")
def create_beautiful_comment(pull_request, answer):
    """
    Create a comment on a Github PR.
    """
    try:
        comment = "Here is a result of fact-checking:\n\n"
        for claim in answer:
            emoji = ":white_check_mark:" if claim["result"] else ":x:"
            comment += f"`{claim['claim']}` {emoji}\n{claim['source']}\n\n"

        print(comment)
        # only post comment if running on Github Actions
        if os.environ.get("GITHUB_ACTIONS") == "true":
            pull_request.create_issue_comment(comment)
    except Exception as e:
        print(f"Error creating a comment on PR: {e}")


def create_ugly_comment(pull_request, answer):
    """
    Create a comment on a Github PR.
    """
    comment = "Here is a result of fact-checking:\n\n"
    comment += answer
    print(comment)
    # only post comment if running on Github Actions
    if os.environ.get("GITHUB_ACTIONS") == "true":
        pull_request.create_issue_comment(comment)


def main():
    """
    The bot parses command-line arguments, such as the GitHub key, LLM API key, and pull request url,
    then retrieves the endpoint and max_tokens from the config file.
    It creates the github-object and extracts a diff.
    Then it obtains clean content from the diff and adds this content to the prompt.
    If the combined prompt and content do not exceed the max_tokens limit, the bot sends the prompt to an AI-service.
    This service provides the answer. The bot then checks if it can extract a JSON segment from the answer.
    If it can, it creates a beautiful comment to the pull request, if it can't, it creates an ugly comment.
    """
    args = parse_cli_args()

    with open('tools/config.json', 'r') as config_file:
        config = json.load(config_file)

    endpoint = config['endpoint']
    max_tokens = config['max_tokens']

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {args.LLM_API_key}'
    }

    github = Github(args.github_token)
    pr = get_pull_request(github, args.pull_url)
    _diff = get_diff_by_url(pr)
    diff = parse_diff(_diff)
    content = get_content(diff)

    whole_prompt = PROMPT % content

    if count_tokens(whole_prompt) > max_tokens:
        print("The token limit has been exceeded. Prompt will be trimmed")
        whole_prompt = trimming_prompt(whole_prompt, max_tokens)

    claims = api_call(whole_prompt, headers, endpoint)
    if claims:
        new_claims = extract_json_content(claims['content'])
        if new_claims:
            create_beautiful_comment(pr, new_claims)
            print("Created beautiful comment")
        else:
            create_ugly_comment(pr, claims)
            print("Created ugly comment")
    else:
        sys.exit(1)
