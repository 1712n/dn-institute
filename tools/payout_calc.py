#!/bin/env python

"""
Count characters in a Github PR diff, calculate the contribution remuneration and comment on the PR.
"""

__author__ = "Daniel Souza <me@posix.dev.br>"

import os, argparse
from github import Github, GithubException
from tools.utils import logging_decorator
from tools.git import get_pull_request, get_diff_by_url, parse_diff

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "--pull-url", dest="pull_url", help="GitHub pull URL", required=True
)
parser.add_argument(
    "--github-token", dest="github_token", help="GitHub token", required=True
)
args = parser.parse_args()

# Initialize Github API
github = Github(args.github_token)

# TODO: Read config from file
config = {"rate": 5, "payeer": "albina-at-inca"}  # cents per character
data = {}


def count_chars(diff: list[dict]) -> int:
    chars = 0

    for file in diff:
        for segments in file["body"]:
            for line in segments["body"].splitlines():
                # only count line additions
                if line.startswith("+"):
                    # sanitize line
                    line = line[2:]  # rm addition indicator
                    line = line.strip()  # rm leading/trailing whitespace
                    # line = line.replace(" ", "") # rm all whitespace
                    chars += len(line)

    return chars


@logging_decorator("Comment on PR")
def create_comment(
    pull_request,
    payeer: str,
    rate: str,
    chars: int,
    value: str,
) -> None:
    author = pull_request.user.login
    url = pull_request.diff_url
    comment = f"Thanks, @{author}! {chars} characters were added/changed in this [PR]({url}). At a rate of {rate}¢/char your contribution is worth ${value}. @{payeer} will process your payment."

    print(comment)

    # only post comment if running on Github
    if os.environ.get("GITHUB_ACTIONS") == "true":
        pull_request.create_issue_comment(comment)


def main():
    pr = get_pull_request(github, args.pull_url)

    # TODO: Improve Diff method. Get diff by words instead of lines.
    _diff = get_diff_by_url(pr)
    diff = parse_diff(_diff)
    data["chars"] = count_chars(diff)
    _value = (data["chars"] * config["rate"]) / 100
    data["value"] = str(_value)

    create_comment(pr, **config, **data)
