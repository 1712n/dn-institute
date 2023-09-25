#!/bin/env python

"""
Extract and verify statements from text content in a pull request using a LLM model and related search results.
Also, the bot checks if a text is written in an informational style.

"""

import os, sys, argparse, time
from typing import List, Tuple, Dict
import json
from tools.utils import logging_decorator
from tools.git import get_pull_request, get_diff_by_url
from github import Github
from duckduckgo_search import ddg
import openai
import tiktoken


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
    "max_tokens": 500,
    "search_size": 10,
}

if args.mode == "development":
    config["retry"] = 1
    config["search_size"] = 1


def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-0301")
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


def web_search(query):
    size = config["search_size"]
    return "\n\n----".join([x["title"] + "\n" + x["body"] for x in ddg(query)[:size]])


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

STYLE_CHECKER_STATEMENT = """
Determine what style the text is written in.

The text is: ```%s```

Is the text written in the informational style? If it is not true, return false in an informational field.

Output should be machine-readable, for example:
```{
    "text": "",
    "informational": true|false
}```"""


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
        if f == "":
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
            meta = [
                x.replace("date: ", "")
                .replace("title: ", "")
                .removeprefix('"')
                .removesuffix('"')
                for x in meta
                if "date: " in x or "title: " in x
            ]
            meta_str = " ".join(meta)
        else:
            meta_str = ""
        final = [
            x for x in final if not x.startswith("---") and not x.endswith("---\n")
        ]
        results.append((final, meta_str))
    return results


@logging_decorator("Verify claim")
def verify_claim(claim: Dict, meta: str) -> Tuple[bool, str]:
    print(f"\nQuery: {meta} {claim['query']}")
    summary = web_search(f"{meta} {claim['query']}")
    print("Summary: " + summary)

    print("Verify Statement Prompt: " + VERIFY_STATEMENT % (claim["claim"], summary))
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
    return (
        is_false,
        (f"`" + obj["claim"] + "` " + emoji + "\n" + obj["explanation"] + "\n\n"),
    )


@logging_decorator("Check text's style")
def check_style(text: str) -> Tuple[bool, str]:
    print("Statement Prompt: " + STYLE_CHECKER_STATEMENT % text)
    ans = openai_call(STYLE_CHECKER_STATEMENT % text)
    ans = ans.strip().strip("`").strip()
    ans = ans[ans.find("{") :]
    print("Answer: " + ans)

    obj = json.loads(ans)
    print("Parsed:", obj)

    is_informational = False
    if obj["informational"]:
        is_informational = True
    emoji = ":x:" if is_informational else ":white_check_mark:"
    return (
        is_informational,
        (f"`" + obj["text"] + "` " + emoji + "\n\n"),
    )


@logging_decorator("Verify file")
def verify_file(parts: List[str], meta: str) -> tuple[int, bool, bool, str]:
    print(f"\n\nProcessing: {meta} | {len(parts)} splits")
    # Filter out empty parts
    parts = list(filter(lambda x: (len(x.strip()) > 1), parts))
    exceptions = 0
    had_false_claim = False
    had_no_informational = False
    file_comment = ""

    for p in parts:
        try:
            print("\nPrompt: " + EXTRACT_STATEMENTS % p)
            ans = openai_call(EXTRACT_STATEMENTS % p)
        except Exception as ex:
            print(ex)
            exceptions += 1
            continue
        ans = ans.strip().strip("`").strip()
        ans = ans[ans.find("[") :]
        print("Answer: " + ans)
        try:
            if ans[-1] != "]":
                ans = fix_uncompleted_json(ans)
            claims = json.loads(ans)
            claims = list(
                filter(
                    lambda x: (
                        x
                        and "query" in x
                        and "claim" in x
                        and x["query"] != ""
                        and x["claim"] != ""
                    ),
                    claims,
                )
            )
        except Exception as ex:
            print(ex)
            exceptions += 1
            continue
        for claim in claims:
            try:
                (is_false, comment) = verify_claim(claim, meta)
                file_comment += comment
                if is_false:
                    had_false_claim = True
            except Exception as ex:
                print(ex)
                exceptions += 1
                continue
        try:
            (is_informational, style_comment) = check_style(p)
            file_comment += style_comment
            if not is_informational:
                had_no_informational = True
        except Exception as ex:
            print(ex)
            exceptions += 1
            continue

    return exceptions, had_false_claim, had_no_informational, file_comment


@logging_decorator("Verify statements")
def verify_statements(diff: str) -> tuple[str, int, bool, bool]:
    files = split_content(diff)
    comment = ""
    exceptions = 0
    had_false_claim = False
    had_no_informational = False
    for parts, meta in files:
        file_exceptions, false_claim, style_check, file_comment = verify_file(parts, meta)
        if file_exceptions != 0:
            print(f"File processing contains {file_exceptions} exceptions")
        exceptions += file_exceptions
        if false_claim:
            had_false_claim = True
        if style_check:
            had_no_informational = True
        comment += file_comment

    return comment, exceptions, had_false_claim, had_no_informational


@logging_decorator("Compile Report")
def compile_report(comment: str, exceptions: int) -> str:
    if exceptions > 0:
        comment += f":warning: Checking failed due to {exceptions} errors"

    print(comment)
    return comment


def main():
    # initialize GitHub object
    github = Github(args.github_token)

    is_github_env = True if os.environ.get("GITHUB_ACTIONS") == "true" else False

    pr = get_pull_request(github, args.pull_url)
    diff = get_diff_by_url(pr)

    if len(diff.strip()) < 1:
        print("No diff - exit")
        pass

    else:
        _comment, exceptions, had_false_claim, had_no_informational = verify_statements(diff)

        had_error = exceptions > 0 or had_false_claim or had_no_informational

        comment = compile_report(_comment, exceptions)

        if len(comment) > 0 and is_github_env:
            pr.create_issue_comment(comment)
            print("comment", comment)

        print("token_usage", token_usage)

        if had_error:
            sys.exit(1)
