#!/bin/env python

"""
Extract and verify statements from text content in a pull request using a LLM model and related search results.
"""

__author__ = "Mikhail Orzhenovskii <orzhan057@gmail.com>, Daniel Souza <me@posix.dev.br>"

# core
import os, sys, argparse
from typing import List, Tuple, Dict

# deps
import re
import time
from github import Github
import subprocess
import json
from duckduckgo_search import ddg
import openai
import tiktoken

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "--repo-url", dest="repo_url", help="GitHub repository URL", required=True
)
parser.add_argument(
    "--pull-request-head",
    dest="pull_request_head",
    help="GitHub pull request head branch",
    required=True,
)
parser.add_argument(
    "--pull-request-base",
    dest="pull_request_base",
    default=False,
    help="GitHub pull request base branch",
    required=True,
)
parser.add_argument(
    "--pull-request-number",
    dest="pull_request_number",
    help="GitHub pull request number",
    type=int,
    required=True,
)
parser.add_argument(
    "--github-token", dest="github_token", help="GitHub token", required=True
)
parser.add_argument(
    "--openai-key", dest="openai_key", help="OpenAI API key", required=True
)
parser.add_argument(
    "--content-path", dest="content_path", help="Content path", required=True
)
args = parser.parse_args()

openai.api_key = args.openai_key

token_usage = {"prompt": 0, "completion": 0}


def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-0301")
    return len(encoding.encode(text))


def openai_call(
    prompt: str,
    model: str = "gpt-3.5-turbo",
    retry: int = 3,
    temperature: float = 0.5,
    max_tokens: int = 500,
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
        if retry == 0: raise(ex)
        print(ex)
        print(f"Retry - {retry}, waiting 15 seconds")
        time.sleep(15)
        return openai_call(prompt, model, retry-1)

    ret = response.choices[0].message.content.strip()
    token_usage["prompt"] += count_tokens(prompt)
    token_usage["completion"] += count_tokens(ret)
    return ret


def google_search(query):
    return "\n\n----".join([x["title"] + "\n" + x["body"] for x in ddg(query)[:10]])


EXTRACT_STATEMENTS = """```%s```
Extract all claims that can be fact-checked from the text section above. Make sure to keep associated URLs found in the claims. Then, for each "claim", copy the claim and add synopsys of the whole text section above to make the corresponding "query". Make sure to add associated URLs found in the claims to the corresponding queries. Important: Respond only with an array of valid JSONs in the following format: ```[{"claim": "", "query": ""}, {"claim": "", "query": ""}]```."""

VERIFY_STATEMENT = """
Given a claim and a set of search results from a search engine API, determine whether the claim is true or false, or if there is not enough evidence to verify it. Use the search results to provide evidence for your determination.

The claim to be verified is: ```%s```

The search results are as follows: ```%s```

Based on the search results, is the claim true or false? If the claim is false, provide a brief explanation and reference your sources. If the claim can't be verified, verdict should also be false.

Output should be machine-readable, for example:
```{
    "claim": "",
    "verdict": true|false,
    "explanation": ""
}```"""


def get_pull_request():
    # Initialize the Github object
    g = Github(args.github_token)

    repo_name = "/".join(args.repo_url.split("/")[-2:]).replace(".git", "")

    # Get the repository object for the pull request
    repo = g.get_repo(repo_name)

    # Get the pull request object
    pull_request = repo.get_pull(args.pull_request_number)
    return pull_request


def get_diff(pull_request) -> str:
    subpath = args.content_path

    # Get the repository path on the runner
    repo_path = os.environ["GITHUB_WORKSPACE"]
    print("repo_path", repo_path)
    tmp_branch_name = "tmp_pull_branch"

    # Check out the base branch and head branch
    print(
        "git0",
        subprocess.run(
            ["git", "fetch", "--prune", "--unshallow"],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        ),
    )
    print(
        "git1",
        subprocess.run(
            ["git", "checkout", args.pull_request_base],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        ),
    )
    print(
        "git2",
        subprocess.run(
            ["git", "fetch", "origin", f"pull/{args.pull_request_number}/head:{tmp_branch_name}"],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        ),
    )
    print(
        "git3",
        subprocess.run(
            ["git", "checkout", tmp_branch_name],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        ),
    )

    # Get the diff for the pull request
    diff_output = subprocess.check_output(
        [
            "git",
            "diff",
            "--no-prefix",
            "--unified=0",
            f"{args.pull_request_base}...{tmp_branch_name}",
            "--",
            subpath
        ],
        cwd=repo_path,
    )

    # Convert the bytes to a string
    diff_str = diff_output.decode("utf-8")

    # Print the diff
    return diff_str

def fix_uncompleted_json(json_string: str) -> str:
    # if start not presented, just make it empty list
    if "[" not in json_string:
        json_string = "["
    while True:
        if not json_string:
            raise ValueError("Couldn't fix JSON")
        try:
            data = json.loads(json_string + "]")
        except json.decoder.JSONDecodeError:
            json_string = json_string[:-1]
            continue
        break
    return json_string + "]"

def split_content(diff: str) -> List[Tuple[List[str], str]]:
    files = diff.split("diff --git")
    results = []
    for f in files:
        if f == '':
            continue
        # remove all tech info and stay only changed and append
        parts = f.split("\n")
        parts = [x for x in parts if x.startswith("+")]
        # remove file names
        parts = [x for x in parts if not x.startswith("+++")]
        # remove '+' sign from start
        parts = [x.lstrip("+") for x in parts]

        # Join string between # symbol
        final = []
        buff = []
        for p in parts:
            if p.startswith("#"):
                final.append("\n".join(buff))
                buff = []
            buff.append(p)
        final.append("\n".join(buff))

        if "---" in final[0] and "date:" in final[0] and "title:" in final[0]:
            meta = final[0].split("\n")
            meta = [x.replace("date: ", "").replace("title: ", "").removeprefix('"').removesuffix('"') for x in meta if "date: " in x or "title: " in x]
            meta_str = " ".join(meta)
        else:
            meta_str = ""
        final = [x for x in final if not x.startswith("---") and not x.endswith("---\n")]
        results.append((final, meta_str))
    return results

def verify_claim(claim: Dict, meta: str) -> Tuple[bool, str]:
    print(f"\nQuery: {meta} {claim['query']}")
    summary = google_search(f"{meta} {claim['query']}")
    print("Summary: " + summary)

    print("Veryfy Statement Prompt: " + VERIFY_STATEMENT % (claim["claim"], summary))
    ans = openai_call(VERIFY_STATEMENT % (claim["claim"], summary))
    ans = ans.strip().strip("`").strip()
    ans = ans[ans.find("{") :]
    print("Answer: " + ans)

    obj = json.loads(ans)
    print("Parsed:", obj)

    is_false = False
    if obj["verdict"] != "true" and obj["verdict"] != True:
        is_false = True
    emoji = ":x:" if is_false else ":white_check_mark:"
    return (is_false, (
        f"`" + obj["claim"] + "` " + emoji
        + "\n"
        + obj["explanation"]
        + "\n\n"
    ))

def verify_file(parts: List[str], meta: str) -> tuple[int, bool, str]:
    print(f"\n\nProcessing: {meta} | {len(parts)} splits")
    # Filter out empty parts
    parts = list(filter(lambda x: (len(x.strip()) > 1), parts))
    exceptions = 0
    had_false_claim = False
    file_comment = ""

    for p in parts:
        try:
            print("\nPrompt: " + EXTRACT_STATEMENTS % p)
            ans = openai_call(EXTRACT_STATEMENTS % p)
        except Exception as ex:
            print(ex)
            exceptions+=1
            continue
        ans = ans.strip().strip("`").strip()
        ans = ans[ans.find("[") :]
        print("Answer: " + ans)
        try:
            if ans[-1] != "]": ans = fix_uncompleted_json(ans)
            claims = json.loads(ans)
            claims = list(filter(lambda x: (x and "query" in x and "claim" in x and x["query"] != "" and x["claim"] != ""), claims))
        except Exception as ex:
            print(ex)
            exceptions+=1
            continue
        for claim in claims:
            try:
                (is_false, comment) = verify_claim(claim, meta)
                file_comment += comment
                if is_false: had_false_claim = True
            except Exception as ex:
                print(ex)
                exceptions+=1
                continue

    return exceptions, had_false_claim, file_comment

def verify_statements(diff: str) -> tuple[bool, bool, str]:
    files = split_content(diff)
    comment = ""
    exceptions = 0
    had_false_claim = False
    for (parts, meta) in files:
        file_exceptions, false_claim, file_comment = verify_file(parts, meta)
        if file_exceptions!= 0: print(f"File processing contains {file_exceptions} exceptions")
        exceptions+=file_exceptions
        if false_claim: had_false_claim = True
        comment+=file_comment
    if exceptions > 0:
        comment += f"Fact-check failed due to {exceptions} errors"

    return exceptions > 0, had_false_claim, comment


def main():
    pull_request = get_pull_request()
    diff = get_diff(pull_request)

    if len(diff.strip()) < 1:
        print("No diff - exit")
        pass

    else:
        print(diff)
        had_error, had_false_claim, comment = verify_statements(diff)

        if comment != "":
            print("comment", comment)
            pull_request.create_issue_comment(comment)

        print("token_usage", token_usage)

        if had_error or had_false_claim:
            sys.exit(1)


main()
