#!/bin/env python

"""
Count characters in a Github PR diff, calculate the contribution remuneration and comment on the PR.
"""

__author__ = "Daniel Souza <me@posix.dev.br>"

import os, argparse
import requests
from github import Github, GithubException

# Config
# TODO: Move config to file
payout_rate = 3  # cents per character
payout_assignee = "albina-at-inca"

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
g = Github(args.github_token)


def logging_decorator(group_name):
    def decorator_wrapper(original_func):
        def wrapper_func(*func_args, **func_kwargs):
            print(f"::group::{group_name}")
            result = original_func(*func_args, **func_kwargs)
            print("::endgroup::\n\n")
            return result

        return wrapper_func

    return decorator_wrapper


@logging_decorator("Get PR")
def get_pull_request(pull_url):
    url_split = pull_url.split("/")

    if url_split[2] == "github.com":
        repo_name = url_split[3] + "/" + url_split[4]
    elif url_split[2] == "api.github.com":
        repo_name = url_split[4] + "/" + url_split[5]

    repo = g.get_repo(repo_name)
    pr_num = int(url_split[-1])
    print(f"Getting PR {pr_num} from {repo_name}")
    pr = repo.get_pull(pr_num)
    return pr


@logging_decorator("Get Diff")
def get_diff(pr) -> str:
    # TODO: Improve diff method.
    # Git by default diff line by line. This means that if a single character is changed in a line, the whole line is counted. Using `--world-diff` makes git diff word by word which would provide a more accurate estimate.
    # The challenge is that the current method using refs don't work after PR is merged.

    # url = f"https://patch-diff.githubusercontent.com/raw/<user>/<repo>/pull/{pr_num}.diff"
    url = pr.diff_url
    print(f"Getting diff from: {url}\n")

    response = requests.get(url)
    if response.status_code == 200:
        diff = response.text
    else:
        raise Exception(
            "Request was not successful. Status code:", response.status_code
        )

    print(diff)
    return diff, url


@logging_decorator("Parse Diff")
def parse_diff(diff: str) -> list[dict]:
    # split into files
    raw_files = diff.split("diff --git ")
    raw_files.remove(raw_files[0])  # remove first element which is empty

    # construct files as dictionaries
    files = []
    for raw_file in raw_files:
        # split into segments
        raw_segments = raw_file.split("@@")

        # pop and store file header
        file_header = raw_segments.pop(0)

        # construct segments as dictionaries
        segments = []
        for index, seg in enumerate(raw_segments):
            if index % 2 == 0:
                segment = {
                    "header": raw_segments[index],
                    "body": raw_segments[index + 1],
                }
                segments.append(segment)

        file = {"header": file_header, "body": segments}
        files.append(file)

    print(files)
    return files


def count_chars(files: list[dict]) -> int:
    chars_count = 0

    for file in files:
        for segments in file["body"]:
            for line in segments["body"].splitlines():
                # only account line additions
                if line.startswith("+"):
                    # sanitize line
                    line = line[2:]  # remove addition indicator
                    line = line.strip()  # remove leading/trailing whitespace
                    # line = line.replace(" ", "") # remove all whitespace
                    chars_count += len(line)

    return chars_count


def calc_payout(chars_count: int) -> str:
    payout = (chars_count * payout_rate) / 100
    return str(payout)


def main():
    pr = get_pull_request(args.pull_url)
    author = pr.user
    diff, diff_url = get_diff(pr)
    diff_struct = parse_diff(diff)
    chars_count = count_chars(diff_struct)
    payout = calc_payout(chars_count)

    print("::group::Comment")
    comment = f"Thanks, @{author.login}! {chars_count} characters were added or changed in this [PR]({diff_url}) and your contribution is worth ${payout}. @{payout_assignee} will process your payment."

    # check if running on Github
    if os.environ.get("GITHUB_ACTIONS") == "true":
        pr.create_issue_comment(comment)

    print(comment)
    print("::endgroup::\n\n")


main()
