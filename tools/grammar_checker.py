#!/bin/env python

"""
Check Grammar mistakes in a Github PR and comment on the PR.
"""

__author__ = "Daniel Souza <me@posix.dev.br>"

import os, argparse
import yaml
from github import Github, GithubException
from tools.utils import logging_decorator
from tools.git import get_pull_request, get_diff_by_url, parse_diff
from pylanguagetool import api
from pylanguagetool import converters

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

    return parser.parse_args()


args = parse_cli_args()

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

def grammar_check(content):
    html_content = converters.markdown2html(content)
    text = converters.html2text(html_content)

    result = api.check(
        text,
        api_url="https://languagetool.org/api/v2/",
        lang="en-US",
    )

    matches = []

    for item in result['matches']:
        context = item['context']
        word = '`' + context['text'][context['offset']:context['offset']+context['length']] + '`'
        replacements = ' | '.join([ '`' + i['value'] + '`' for i in item['replacements'] ])
        issue = item['shortMessage'] if item['shortMessage'] != '' else item['message'] 
        fix = 'Fix: ' + word
        if replacements.strip() != '':
            fix += ' to ' + replacements

        matches.append(
            {
                'context': '`' + context['text'] + '`',
                'issue': 'Issue: '+ issue,
                'fix': fix
            }
        )

    return matches

@logging_decorator("Comment on PR")
def create_comment(
    pull_request,
    matches: list,
    count: int 
) -> None:
    """
    Create a comment on a Github PR.
    """

    url = pull_request.diff_url

    comment = f"{count} grammar issues were found in this [PR]({url}).\n\n"
    for i in matches:
        comment += i['context'] + "\n" + i['issue'] + "\n" + i['fix'] + "\n\n"

    print(comment)

    # only post comment if running on Github
    if os.environ.get("GITHUB_ACTIONS") == "true":
        pull_request.create_issue_comment(comment)


def main():
    github = Github(args.github_token)
    pr = get_pull_request(github, args.pull_url)

    _diff = get_diff_by_url(pr)
    diff = parse_diff(_diff)
    content = get_content(diff)

    data["matches"] = grammar_check(content)
    data["count"] = len(data["matches"])

    # Creating actual comment with Grammar mistakes
    create_comment(pr, **data)
