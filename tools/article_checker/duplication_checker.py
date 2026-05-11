#!/bin/env python

"""
Searches for similar texts on the wiki and checks whether a text from a pull request contains new information
"""

import argparse
import os
import sys
import time
import json
import re

from tools.python_modules.utils import logging_decorator


def parse_cli_args():
    """
    Parse CLI arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--github-token", dest="github_token", help="GitHub token", required=True
    )
    parser.add_argument(
        "--llm-api-key", dest="API_key", help="API key", required=True
    )
    parser.add_argument(
        "--pull-url", dest="pull_url", help="GitHub pull URL", required=True
    )
    return parser.parse_args()


def openai_call(prompt: str, config, retry: int = None):
    import openai

    model = config["GPT_MODEL"]
    temperature = config["GPT_temperature"]
    max_tokens = config["GPT_max_tokens"]
    if retry is None:
        retry = config["GPT_retry"]

    messages = [
        {"role": "system", "content": "Return output as JSON."},
        {"role": "user", "content": prompt}
    ]
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            n=1,
            stop=None,
            response_format={"type": "json_object"}
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as ex:
        if retry == 0:
            raise ex
        print(ex)
        print(f"Retry - {retry}, waiting 15 seconds")
        time.sleep(15)
        return openai_call(prompt, config, retry - 1)


ARTICLE_PATH_PREFIX = "content/research/cyberattacks/incidents/"


def get_new_file_path(file_header):
    """
    Extract the new-side path from a unified diff file header.
    """
    matches = re.findall(r"(?:^|\s)b/([^\s]+)", file_header)
    if not matches:
        return ""
    path = matches[-1]
    return "" if path == "/dev/null" else path


def is_attack_article_path(path):
    """
    Return true for Markdown incident articles that should be duplicate-checked.
    """
    return path.startswith(ARTICLE_PATH_PREFIX) and path.endswith(".md")


def added_lines(segment_body):
    """
    Return only added content lines from a unified diff hunk body.
    """
    lines = []
    for line in segment_body.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            lines.append(line[1:])
    return lines


def build_new_article_text(diff):
    """
    Extract added text from changed incident article Markdown files.
    """
    article_lines = []
    for file in diff:
        path = get_new_file_path(file["header"])
        if not is_attack_article_path(path):
            continue

        for segment in file["body"]:
            article_lines.extend(added_lines(segment["body"]))

    return "\n".join(article_lines).strip()


def new_text_handler(diff):
    """
    Extracts text and target entity from a new pull request
    """
    new_text = build_new_article_text(diff)
    if not new_text:
        return "", ""

    pattern = r'^target-entities:\s*(.*?)$'
    matches = re.search(pattern, new_text, re.MULTILINE)
    target = ''
    if matches:
        target_entities = matches.group(1)
        target = target_entities
    else:
        print("Value 'target-entities' didn't find")

    summary = re.search(r'^## Summary.*', new_text, re.DOTALL | re.MULTILINE)
    if summary:
        new_text = summary.group(0)
    return new_text.strip(), target


def get_list_of_target_entities(url):
    """
    Gets a list of target entities that exist on the crypto wiki
    """
    import requests
    from bs4 import BeautifulSoup

    result_list = []
    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        li_elements = soup.find_all('li', class_='section-item')
        for li in li_elements:
            a_element = li.find('a')
            if a_element:
                result_list.append(a_element.text)
    else:
        print("Failed to retrieve page content")
    return result_list
    

def get_same_texts(target, url, list_of_target_entities):
    """
    Searching urls of same texts in the crypto wiki
    """
    import requests
    from bs4 import BeautifulSoup

    href_list = []
    if target in list_of_target_entities:
        target_url_component = target.replace(' ', '-')
        url = url + target_url_component
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


def get_old_text(url):
    """
    Gets an old text from the crypto wiki
    """
    import requests
    from bs4 import BeautifulSoup

    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        old_text = soup.get_text()
        old_text = re.search(r'Summary\n#.*', old_text, re.DOTALL)
        old_text = old_text.group(0)
        return old_text
    else:
        print("Failed to retrieve page content")


def compare_texts(href_list, url, new_text, prompt, config):
    """
    Compares a new text from a pull request with old texts
    """
    from tools.python_modules.llm_utils import count_tokens, trimming_text

    for href in href_list:
        url = url + href
        old_text = get_old_text(url)
        amount_of_tokens = count_tokens(prompt % (new_text, old_text))
        if amount_of_tokens > config["max_tokens"]:
            threshold = amount_of_tokens / 2
            new_text = trimming_text(new_text, threshold)
            old_text = trimming_text(old_text, threshold)
        query = prompt % (new_text, old_text)
        ans = openai_call(query, config)
        obj = json.loads(ans)
        if obj["have_same_article"]:
            return ":x:"
    return ":white_check_mark:"


@logging_decorator("Comment on PR")
def create_comment_on_pr(pull_request, answer):
    """
    Create and post a comment on a Github pull request.
    """
    try:
        comment = generate_comment(answer)
        print(comment)
        # only post comment if running on Github Actions
        if os.environ.get("GITHUB_ACTIONS") == "true":
            pull_request.create_issue_comment(comment)
    except Exception as e:
        print(f"Error creating a comment on PR: {e}")


def generate_comment(answer):
    """
    Generate a formatted comment based on the provided answer
    """
    comment = "## Duplicate checker\n\n"
    comment += f"Is this a new article for Crypto wiki? {answer}\n\n"
    return comment


PROMPT = """Compare two texts and say if they are the same.
First: ```%s```

Second: ```%s```

If the texts say the same thing, return True.  Output should be machine-readable, for example:
```{
  "have_same_article": True|False
}```"""


def main():
    import openai
    from github import Github

    from tools.python_modules.git import get_pull_request, get_diff_by_url, parse_diff

    args = parse_cli_args()
    openai.api_key = args.API_key
    
    with open('tools/article_checker/config.json', 'r') as config_file:
        config = json.load(config_file)

    main_url = 'https://dn.institute'
    target_entities_url = 'https://dn.institute/attacks/posts/target-entities/'

    github = Github(args.github_token)
    pr = get_pull_request(github, args.pull_url)
    _diff = get_diff_by_url(pr)
    diff = parse_diff(_diff)
    new_text, target = new_text_handler(diff)
    if not new_text:
        create_comment_on_pr(
            pr,
            ":information_source: No changed cyberattack article content found to compare.",
        )
        return

    if not target:
        create_comment_on_pr(
            pr,
            ":information_source: Duplicate check skipped because no target-entities "
            "value was found in the changed article content.",
        )
        return

    list_of_target_entities = get_list_of_target_entities(target_entities_url)
    href_list = get_same_texts(target, target_entities_url, list_of_target_entities)
    if href_list:
        answer = compare_texts(href_list, main_url, new_text, PROMPT, config)
        print(answer)
        create_comment_on_pr(pr, answer)
    else:
        create_comment_on_pr(pr, ":white_check_mark:")
