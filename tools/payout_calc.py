#!/bin/env python

"""
Count characters in a Github PR diff, calculate the contribution remuneration and comment on the PR.
"""

__author__ = "Daniel Souza <me@posix.dev.br>"

import os, argparse
import yaml
from github import Github, GithubException
from tools.utils import logging_decorator
from tools.git import get_pull_request, get_diff_by_url, parse_diff

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
        "--rate", dest="rate", help="Payout rate", type=int, required=False
    )
    return parser.parse_args()


args = parse_cli_args()


def load_config() -> dict:
    """
    Read configuration from default values, config file and CLI arguments in this order of precedence.
    Returns config as a dictionary.
    """

    # default values
    config = {
        "rate": 0,  # cents per character
        "payeer": "",  # GitHub username of the person responsible for processing payments
    }

    # merge with values from config file
    config_file = "tools/payout_calc.yml"
    if os.path.isfile(config_file):
        with open(config_file) as file:
            config_from_file = yaml.load(file, Loader=yaml.FullLoader)
            config = {**config, **config_from_file}

    # merge with values from arguments
    for key, value in config.items():
        # if args.__dict__[key]:
        if key in args.__dict__ and args.__dict__[key] is not None:
            config[key] = args.__dict__[key]

    return config


config = load_config()


def count_chars(diff: list[dict]) -> int:
    """
    Count characters in a Github PR diff.
    Returns the number of characters.
    """

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
    rate: int,
    chars: int,
    value: int,
) -> None:
    """
    Create a comment on a Github PR.
    """

    author = pull_request.user.login
    url = pull_request.diff_url
    comment = f"Thanks, @{author}! {chars} characters were added/changed in this [PR]({url}). At a rate of {rate}¢/char your contribution is worth ${value}. @{payeer} will process your payment."

    print(comment)

    # only post comment if running on Github
    if os.environ.get("GITHUB_ACTIONS") == "true":
        pull_request.create_issue_comment(comment)


def main():
    github = Github(args.github_token)
    pr = get_pull_request(github, args.pull_url)

    # TODO: Improve Diff method. Get diff by words instead of lines.
    _diff = get_diff_by_url(pr)
    diff = parse_diff(_diff)
    data["chars"] = count_chars(diff)
    _value = (data["chars"] * config["rate"]) / 100
    data["value"] = str(_value)

    create_comment(pr, **config, **data)
