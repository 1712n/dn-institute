#!/bin/env python

"""
Search for duplicates in the crypto wiki
Check for the presence of mandatory headers
Evaluate the style and readability
Extract and verify statements from text content in a pull request using a LLM model and related search results.
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
import requests
from bs4 import BeautifulSoup
import re
import textstat


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


"""
Below is a block with style and readability checker
"""


STYLE_AND_READABILITY_STATEMENT = """ 
Indicate whether the text below is written in an informational style. 
In the 'informational' field, provide the answer.
Also, I know that the text has a Flesch Reading Ease Score equals ```%s```. In the 'flesch_explanation' field, write a detailed explanation of the Flesch Reading Ease score.

Output should be machine-readable, for example:
```{
    "informational": true|false,
    "flesch_explanation": ""
}```

text: ```%s```
"""


@logging_decorator("Check style and readability")
def check_style_and_readability(content):
    # check if an article is written in an informational style and determine its readability score
    f_index = textstat.flesch_reading_ease(content)

    ans = openai_call(STYLE_AND_READABILITY_STATEMENT % (f_index, content))
    ans = ans.strip().strip("`").strip()
    ans = ans[ans.find("{"):]

    obj = json.loads(ans)
    print("Parsed:", obj)

    is_informational = False
    if obj["informational"]:
        is_informational = True
    emoji_inf = ":x:" if not is_informational else ":white_check_mark:"

    return (f"`" + "Is this article written in the informational style?" + "` " + emoji_inf + "\n",
            "The readability score: <b>" + str(f_index) + "</b>\n" + obj["flesch_explanation"])


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


"""
Below is a block with duplication checker
"""


def get_list_of_target_entities(url):
    # gets a list of target entities that exist on the crypto wiki
    target_entities = []
    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        li_elements = soup.find_all('li', class_='section-item')
        for li in li_elements:
            a_element = li.find('a')
            if a_element:
                target_entities.append(a_element.text)
    else:
        print("Failed to retrieve page content")
    return target_entities


def get_target_and_date(diff):
    # get the target name and date of the attack from the pr
    error_comment = ''
    target = ''
    date = ''
    pattern_target = r'target-entities:\s+(.*?)\n'
    pattern_date = r'date:\s+(.*?)\n'
    matches_target = re.search(pattern_target, diff)
    matches_date = re.search(pattern_date, diff)
    if matches_target:
        target = matches_target.group(1)
    else:
        error_comment += "Value 'target-entities' didn't find" + "\n" + "Please, pay attention to mandatory headers. Check the Submission Guidelines" + "\n"
    if matches_date:
        date = matches_date.group(1)
    else:
        error_comment += "Value 'date' didn't find" + "\n" + "Please, pay attention to mandatory headers. Check the Submission Guidelines" + "\n"

    return error_comment, target, date


def check_dupl_in_wiki(target, url, list_of_target_entities):
    # searching urls of same texts in the crypto wiki for the target
    href_list = []
    if target in list_of_target_entities:
        url = url + target.replace(" ", "-")
        print(url)
        response = requests.get(url)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            posts = soup.find_all('article', class_='markdown book-post')
            if posts:
                for post in posts:
                    post_head = post.find('h2')
                    href = post_head.find('a')
                    href = href['href']
                    href_list.append(href)
    return href_list


def get_user_answer_from_comments(pr):
    # get an answer from the pr comments to decide whether to continue the check or not
    while True:
        comments = pr.get_issue_comments()
        for comment in comments:
            if comment.body == "No" or comment.body == "no":
                return "No"
            elif comment.body == "Yes" or comment.body == "yes":
                return "Yes"


@logging_decorator("Search duplicates in the crypto wiki")
def check_wiki_duplicates(href_list, target, date):
    # compares the metadata of the new text with the metadata of the texts in the crypto wiki
    have_same_article = False
    for href in href_list:
        pattern = r'/(\d{4}-\d{2}-\d{2})-(.*?)/'

        match = re.search(pattern, href)

        if match:
            old_date = match.group(1)
            old_target = match.group(2)
            print(old_target)
            print(old_date)

            if target == old_target.replace("-", " ") and date == old_date:
                have_same_article = True

    emoji = ":x:" if have_same_article else ":white_check_mark:"
    return (have_same_article,
        f"`" + "Is this article new for our wiki?" + "` " + emoji + "\n\n")


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


@logging_decorator("Verify file")
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

    return exceptions, had_false_claim, file_comment


@logging_decorator("Verify statements")
def verify_statements(diff: str) -> tuple[str, int, bool]:
    files = split_content(diff)
    comment = ""
    exceptions = 0
    had_false_claim = False
    for parts, meta in files:
        file_exceptions, false_claim, file_comment = verify_file(parts, meta)
        if file_exceptions != 0:
            print(f"File processing contains {file_exceptions} exceptions")
        exceptions += file_exceptions
        if false_claim:
            had_false_claim = True
        comment += file_comment

    return comment, exceptions, had_false_claim


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
        error_comment, target, date = get_target_and_date(diff)

        if len(error_comment) > 0 and is_github_env:
            pr.create_issue_comment(error_comment)

        else:
            list_of_target_entities = get_list_of_target_entities('https://dn.institute/attacks/posts/target-entities/')
            href_list = check_dupl_in_wiki(target, 'https://dn.institute/attacks/posts/target-entities/', list_of_target_entities)
            have_same_article, comment_wiki_duplicate = check_wiki_duplicates(href_list, target, date)

            if len(comment_wiki_duplicate) > 0 and is_github_env:
                pr.create_issue_comment(comment_wiki_duplicate)
                print(comment_wiki_duplicate)

            if have_same_article and is_github_env:
                question = "Continue the check? (Answer 'Yes' or 'No' in a comment)"
                pr.create_issue_comment(question)
                user_answer = get_user_answer_from_comments(pr)
                if user_answer.lower() == "no":
                    sys.exit(1)

        comment_sections = ""
        are_allowed_sections, res = are_there_standard_sections("".join(split_content(diff)[0][0]))

        if not are_allowed_sections:
            if res["missing_sections"]:
                comment_sections += f'There are missing sections: <b>{", ".join(res["missing_sections"])}</b> here. You should add them' + "\n"
            if res["extra_sections"]:
                comment_sections += f'There are extra sections: <b>{", ".join(res["extra_sections"])}</b> here. You should delete them' + "\n"

        emoji_sections = ":white_check_mark:" if are_allowed_sections else ":x:"
        comment_sections_full = f"Does this article have only allowed sections? {emoji_sections}" + "\n" + comment_sections + "\n\n"

        if len(comment_sections_full) > 0 and is_github_env:
            pr.create_issue_comment(comment_sections_full)
            print(comment_sections_full)

        comment_style, comment_readability = check_style_and_readability("".join(split_content(diff)[0][0]))

        if len(comment_style) > 0 and is_github_env:
            pr.create_issue_comment(comment_style)
            print(comment_style)

        if len(comment_readability) > 0 and is_github_env:
            pr.create_issue_comment(comment_readability)
            print(comment_readability)

        _comment, exceptions, had_false_claim = verify_statements(diff)

        had_error = exceptions > 0 or had_false_claim

        comment = compile_report(_comment, exceptions)

        if len(comment) > 0 and is_github_env:
            pr.create_issue_comment(comment)
            print("comment", comment)

        print("token_usage", token_usage)

        if had_error:
            sys.exit(1)