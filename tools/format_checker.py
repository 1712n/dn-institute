#!/bin/env python

"""
Check a format of a new article from a Github PR and comment on the PR.
"""


import os, argparse, time
from github import Github
import openai
from tools.git import get_pull_request, get_diff_by_url, parse_diff
import tiktoken
import json
from tools.utils import logging_decorator


# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "--github-token", dest="github_token", help="GitHub token", required=True
)
parser.add_argument(
    "--openai-key", dest="openai_key", help="OpenAI API key", required=True
)
parser.add_argument(
    "--pull-url", dest="pull_url", help="GitHub pull URL", required=True
)

parser.add_argument("--content-path", dest="content_path", help="Content path")
parser.add_argument("--mode", dest="mode", help="Run mode")
args = parser.parse_args()

openai.api_key = args.openai_key

token_usage = {"prompt": 0, "completion": 0}

config = {
    "model": "gpt-3.5-turbo",
    "retry": 3,
    "temperature": 0.5,
    "max_tokens": 1000,
    "search_size": 10,
}

if args.mode == "development":
    config["retry"] = 1
    config["search_size"] = 1


def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
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


def get_filename(_diff):
    """
    gets a filename from a raw diff
    """
    lines = _diff.splitlines()
    filename = lines[0].split("/")[-1]
    return filename


def get_content(diff: list[dict]) -> str:
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


STATEMENT = """To comply with the Hugo SSG format, a text must have a certain structure — all fields below are required: 
```
---
date: YYYY-MM-DD
target-entities: name_of_entity
entity-types:
  - entity_type
attack-types:
  - attack_type
title: "title"
---
```
 Check if a new text matches the correct Hugo SSG format, taking into account the information given above and general information about Hugo SSG. 
  Your output should be machine-readable, for example:
```{
    "hugo_ssg": true|false,
    "hugo_explanation": ""
}```
If the new text doesn't match the correct Hugo SSG format, set the hugo_ssg flag to false. Explain what specifically doesn't match the format in the field "explanation".

new text: ```%s```
"""


FILENAME_STATEMENT = """Check if a filename matches this format: "YYYY-MM-DD-entity-that-was-hacked.md".

Filename: ```%s```

Give me just an output. Output should be machine-readable, for example:
```{
    "correct_filename": true|false
}```"""


def check_filename(filename):
    """
    Checks if the filename matches the pattern "YYYY-MM-DD-entity-that-was-hacked.md"
    """
    ans = openai_call(FILENAME_STATEMENT % filename)
    ans = ans.strip().strip("`").strip()
    ans = ans[ans.find("{"):]
    print("Answer: " + ans)

    obj = json.loads(ans)
    print("Parsed:", obj)

    correct_filename = False
    if obj["correct_filename"]:
        correct_filename = True
    emoji_filename = ":white_check_mark:" if correct_filename else ":x:"

    return emoji_filename


def are_there_standard_sections(content):
    """
    Checks if there are sections: Summary, Attackers, Ls, Timeline, Security Failure Causes
    """
    # list of allowed sections
    allowed_sections = ['Summary', 'Attackers', 'Losses', 'Timeline', 'Security Failure Causes']

    lines = content.split('\n')
    found_sections = []

    for line in lines:
        if line.startswith("## "):
            section_name = line[3:]  # extracts the name of a section
            if section_name in allowed_sections:
                found_sections.append(section_name)

    if sorted(found_sections) == sorted(allowed_sections):
        return (True, {})
    else:
        # Calculate the difference between found_sections and allowed_sections
        missing_sections = set(allowed_sections) - set(found_sections)
        extra_sections = set(found_sections) - set(allowed_sections)
        return (False, {
            "missing_sections": list(missing_sections),
            "extra_sections": list(extra_sections)
        })


def check_format(content):
    """
    Checks if an article follows the Hygo SSG format
    """
    ans = openai_call(STATEMENT % content)
    ans = ans.strip().strip("`").strip()
    ans = ans[ans.find("{"):]
    print("Answer: " + ans)

    obj = json.loads(ans)
    print("Parsed:", obj)

    comment_hugo = ""
    is_hugo_ssg = False
    if obj["hugo_ssg"]:
        is_hugo_ssg = True
    emoji_hugo = ":white_check_mark:" if is_hugo_ssg else ":x:"
    if obj["hugo_explanation"]:
        comment_hugo += obj["hugo_explanation"]

    comment_sections = ""
    are_allowed_sections, res = are_there_standard_sections(content)
    if not are_allowed_sections:
        if res["missing_sections"]:
            comment_sections += f'There are missing sections: <b>{", ".join(res["missing_sections"])}</b> here. You should add them'
        if res["extra_sections"]:
            comment_sections += f'There are extra sections: <b>{", ".join(res["extra_sections"])}</b> here. You should delete them'
    emoji_sections = ":white_check_mark:" if are_allowed_sections else ":x:"

    return (
        emoji_hugo,
        emoji_sections,
        comment_hugo,
        comment_sections
    )


@logging_decorator("Comment on PR")
def create_comment(
    pr,
    emoji_filename,
    emoji_hugo,
    emoji_sections,
    comment_hugo,
    comment_sections
):
    """
    Create a comment on a Github PR.
    """

    comment_filename = f"Is the filename correct? {emoji_filename}\n\n"
    comment_hugo = f"Does this article match Hugo SSG format? {emoji_hugo}\n\n" + comment_hugo + "\n\n"
    comment_sections = f"Does this article have only allowed sections? {emoji_sections}" + comment_sections + "\n\n"

    print(comment_filename)
    print(comment_hugo)
    print(comment_sections)

    # only post comment if running on Github
    if os.environ.get("GITHUB_ACTIONS") == "true":
        pr.create_issue_comment(comment_filename + comment_hugo + comment_sections)


def main():
    github = Github(args.github_token)
    pr = get_pull_request(github, args.pull_url)

    _diff = get_diff_by_url(pr)

    filename = get_filename(_diff)  # get a filename from a raw diff
    emoji_filename = check_filename(filename)  # get the check result for the filename

    diff = parse_diff(_diff)
    content = get_content(diff)  # get an article from the diff

    emoji_hugo, emoji_sections, comment_hugo, comment_sections = check_format(content)
    # get the result of the formatting check

    create_comment(pr, emoji_filename, emoji_hugo, emoji_sections, comment_hugo, comment_sections)
    # create comments in pr

    print("token_usage", token_usage)