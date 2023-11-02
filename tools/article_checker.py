#!/bin/env python


import argparse, os
from github import Github
from tools.git import get_pull_request, get_diff_by_url, parse_diff
from tools.utils import logging_decorator
import requests
import json
import tiktoken


# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "--github-token", dest="github_token", help="GitHub token", required=True
)
parser.add_argument(
    "--wp-key", dest="wp_key", help="WebPilot API key", required=True
)
parser.add_argument(
    "--pull-url", dest="pull_url", help="GitHub pull URL", required=True
)

args = parser.parse_args()

wp_key = args.wp_key
endpoint = 'https://preview.webpilotai.com/api/v1/watt'
headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {wp_key}'
    }


def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return len(encoding.encode(text))


def trimming_prompt(trimmed_prompt):
    token_count = count_tokens(trimmed_prompt)
    while token_count > 4096:
        sentences = trimmed_prompt.rsplit('.', maxsplit=1)
        if len(sentences) == 2 and sentences[0]:
            trimmed_prompt = sentences[0].strip() + '.'
        else:
            trimmed_prompt = trimmed_prompt.rsplit(' ', maxsplit=1)[0]

        token_count = count_tokens(trimmed_prompt)

    return trimmed_prompt


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True


def extract_json_content(content):
    if is_json(content):
        return json.loads(content)
    else:
        raise ValueError("Content is not a valid JSON-like string")


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


def wp_call(PROMPT, headers=headers, endpoint=endpoint):
    """
    Create an API call
    """
    data = {"Content": PROMPT}
    try:
        response = requests.post(endpoint, headers=headers, json=data)
        response.raise_for_status()  # will raise an HTTPError if the HTTP request returned an unsuccessful status code
        answer = response.text
    except requests.exceptions.RequestException as e:
        print(f"Error making API call: {e}")
        answer = None
    return answer


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
def create_comment(pull_request, answer):
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


def main():
    github = Github(args.github_token)
    pr = get_pull_request(github, args.pull_url)
    _diff = get_diff_by_url(pr)
    diff = parse_diff(_diff)
    content = get_content(diff)

    whole_prompt = PROMPT % content
    print(count_tokens(whole_prompt))

    if count_tokens(whole_prompt) > 4096:
        print("The token limit has been exceeded. Prompt will be trimmed")
        whole_prompt = trimming_prompt(whole_prompt)

    claims = wp_call(whole_prompt)
    claims = json.loads(claims)
    print(claims)
    try:
        # Attempt to extract JSON content
        new_claims = extract_json_content(claims['content'])
        create_comment(pr, new_claims)
    except ValueError as e:
        # Handle the case where the content is not JSON-like
        print(f"Error: {e}")
        # You can raise the exception again if you want to stop the script here
        raise
