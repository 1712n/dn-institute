"""
Check if the statements from text content in a pull request are written in an informational style.
"""

import os, sys, argparse, time
from typing import List, Tuple
import json
from tools.utils import logging_decorator
from tools.git import get_pull_request, get_diff_by_url
from github import Github
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


STATEMENT = """
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


@logging_decorator("Check text")
def check_text(text: str) -> Tuple[bool, str]:

    print("Statement Prompt: " + STATEMENT % text)
    ans = openai_call(STATEMENT % text)
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
        (f"`" + obj["text"] + "` " + emoji + "\n" + "\n\n"),
    )


@logging_decorator("Check file")
def check_file(parts: List[str], meta: str) -> tuple[int, bool, str]:
    print(f"\n\nProcessing: {meta} | {len(parts)} splits")
    # Filter out empty parts
    parts = list(filter(lambda x: (len(x.strip()) > 1), parts))
    exceptions = 0
    had_no_informational = False
    file_comment = ""

    for p in parts:
        try:
            (is_informational, comment) = check_text(p)
            file_comment += comment
            if not is_informational:
                had_no_informational = True
        except Exception as ex:
            print(ex)
            exceptions += 1
            continue

    return exceptions, had_no_informational, file_comment


@logging_decorator("Check all diff")
def check_diff(diff: str) -> tuple[int, bool, str]:
    files = split_content(diff)
    comment = ""
    exceptions = 0
    had_no_informational = False
    for parts, meta in files:
        file_exceptions, is_not_informational, file_comment = check_file(parts, meta)
        if file_exceptions != 0:
            print(f"File processing contains {file_exceptions} exceptions")
        exceptions += file_exceptions
        if is_not_informational:
            had_no_informational = True
        comment += file_comment

    return exceptions, had_no_informational, comment


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
        exceptions, had_no_informational, _comment = check_diff(diff)

        had_error = exceptions > 0 or had_no_informational

        comment = compile_report(_comment, exceptions)

        if len(comment) > 0 and is_github_env:
            pr.create_issue_comment(comment)
            print("comment", comment)

        print("token_usage", token_usage)

        if had_error:
            sys.exit(1)