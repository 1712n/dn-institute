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
from github import Github
import openai
from bs4 import BeautifulSoup
import requests

from tools.python_modules.llm_utils import remove_plus, count_tokens, trimming_text
from tools.python_modules.git import get_pull_request, get_diff_by_url, parse_diff
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


def new_text_handler(diff):
    """
    Extracts text and target entity from a new pull request
    """
    new_text = remove_plus(diff[0]['header'] + diff[0]['body'][0]['body'])
    pattern = r'target-entities:\s+(.*?)\n'
    matches = re.search(pattern, new_text)
    target = ''
    if matches:
        target_entities = matches.group(1)
        target = target_entities
    else:
        print("Value 'target-entities' didn't find")

    new_text = re.search(r'## Summary.*', new_text, re.DOTALL)
    new_text = new_text.group(0)
    return new_text, target


def get_list_of_target_entities(url):
    """
    Gets a list of target entities that exist on the crypto wiki
    """
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
    list_of_target_entities = get_list_of_target_entities(target_entities_url)
    href_list = get_same_texts(target, target_entities_url, list_of_target_entities)
    if href_list:
        answer = compare_texts(href_list, main_url, new_text, PROMPT, config)
        print(answer)
        create_comment_on_pr(pr, answer)
    else:
        create_comment_on_pr(pr, ":white_check_mark:")
