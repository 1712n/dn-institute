#!/bin/env python


import argparse, os
from github import Github
from tools.git import get_pull_request, get_diff_by_url, parse_diff
from tools.utils import logging_decorator
import requests
import json


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
Task: Identify and verify factual claims from the given text. Use credible web sources to check the accuracy of each claim. Present your findings only in a structured JSON format with each claim, the verification source, and the outcome of the verification.
Output Format: 
[{"claim": "The factual statement extracted from the text", "source": "URL or name of the source used for verification", "result": "The outcome of the fact-check (True, False, or Unverifiable)"}]
Example:
Input Text: "In July 2011, BTC-e, a cryptocurrency exchange, experienced a security breach that resulted in the loss of around 4,500 BTC."
Output: [{"claim": "In July 2011, BTC-e experienced a security breach.", "source": "https://bitcoinmagazine.com/business/btc-e-attacked-1343738085", "result": "False. The breach occurred in July 2012."}]

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

    claims = wp_call(PROMPT % content)
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