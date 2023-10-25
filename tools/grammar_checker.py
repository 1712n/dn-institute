#!/bin/env python

"""
Check Grammar mistakes in a Github PR and comment on the PR.
"""

__author__ = "Daniel Souza <me@posix.dev.br>"

import os, argparse, time
from github import Github, GithubException
from tools.utils import logging_decorator
from tools.git import get_pull_request, get_diff_by_url, parse_diff
from pylanguagetool import api
from pylanguagetool import converters
import openai
import tiktoken

data = {}


def parse_cli_args():
    """
    Parse CLI arguments.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pull-url", dest="pull_url", help="GitHub pull URL", required=True
    )
    parser.add_argument(
        "--github-token", dest="github_token", help="GitHub token", required=True
    )

    parser.add_argument(
        "--openai-key", dest="openai_key", help="OpenAI API key", required=True
    )

    return parser.parse_args()


args = parse_cli_args()

openai.api_key = args.openai_key

token_usage = {"prompt": 0, "completion": 0}

config = {
    "model": "gpt-4-0613",
    "retry": 3,
    "temperature": 0,
    "max_tokens": 4000,
    "search_size": 10,
}

def get_content(diff: list[dict]) -> int:
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

def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-4-0613")
    return len(encoding.encode(text))


def openai_call(
    prompt: str,
    model: str = config["model"],
    retry: int = config["retry"],
    temperature: float = config["temperature"],
    max_tokens: int = config["max_tokens"],
):
    messages = [{"role": "user", "content": prompt}]
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            n=1,
            stop=None,
        )
    except Exception as ex:
        if retry == 0:
            raise (ex)
        print(ex)
        print(f"Retry - {retry}, waiting 15 seconds")
        time.sleep(15)
        return openai_call(prompt, model, retry - 1)

    ret = response.choices[0].message.content.strip()
    token_usage["prompt"] += count_tokens(prompt)
    token_usage["completion"] += count_tokens(ret)
    return ret

def grammar_check(content):
    # call OpenAI

    issues = ""

    return issues

@logging_decorator("Comment on PR")
def create_comment(
    pull_request,
    issues
) -> None:
    """
    Create a comment on a Github PR.
    """

    url = pull_request.diff_url

    comment = f"Grammar issues found in this [PR]({url}):\n\n"
    comment += issues

    print(comment)

    # only post comment if running on Github
    if os.environ.get("GITHUB_ACTIONS") == "true":
        pull_request.create_issue_comment(comment)


GRAMMAR_CHECKER = """

"""


def main():
    github = Github(args.github_token)
    pr = get_pull_request(github, args.pull_url)

    _diff = get_diff_by_url(pr)
    diff = parse_diff(_diff)
    content = get_content(diff)

    issues = grammar_check(content)

    # Creating actual comment with Grammar mistakes
    create_comment(pr, issues)
