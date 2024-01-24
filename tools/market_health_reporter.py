from openai import OpenAI
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import argparse
import json
import os
from github import Github
from tools.claude_retriever.client.py import extract_between_tags


def parse_cli_args():
    """
    Parse CLI arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--llm-api-key", dest="API_key", help="LLM API key", required=True
    )
    parser.add_argument(
        "--issue", dest="issue", help="Issue number", required=True
    )
    parser.add_argument(
        "--comment-body", dest="comment_body", help="Comment body", required=True
    )
    parser.add_argument(
        "--github-token", dest="github_token", help="Github token", required=True
    )
    return parser.parse_args()


def post_comment_to_issue(github_token, issue_number, repo_name, comment):
    """
    Post a comment to a GitHub issue.
    """
    g = Github(github_token)
    repo = g.get_repo(repo_name)
    issue = repo.get_issue(number=issue_number)
        # only post comment if running on Github Actions
    if os.environ.get("GITHUB_ACTIONS") == "true":
        issue.create_comment(comment)


def main():
    args = parse_cli_args()
    repo_name = "1712n/dn-institute"

    if "openai:" in args.comment_body:
        with open('tools/market_health_reporter_doc/data/data1.json', 'r') as data_file:
            data = json.load(data_file)

        with open('tools/market_health_reporter_doc/openai/prompts/system_prompt.txt', 'r') as file:
            SYSTEM_PROMPT = file.read()

        with open('tools/market_health_reporter_doc/openai/prompts/prompt1.txt', 'r') as file:
            HUMAN_PROMPT_CONTENT = file.read()

        with open('content/market-health/posts/2023-08-14-huobi/index.md', 'r') as file:
            article_example = file.read()


        HUMAN_PROMPT_CONTENT = f"""
        <example> %s </example>
        {HUMAN_PROMPT_CONTENT}
        <data> %s </data>
        """
        
        prompt = f"{HUMAN_PROMPT_CONTENT%(article_example, data)}"
        print('This is a prompt: ', prompt)

        client = OpenAI(api_key=args.API_key)

        completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"{SYSTEM_PROMPT}"},
            {"role": "user", "content": f"{prompt}"}
        ]
        )

        output = completion.choices[0].message.content
        
        output = extract_between_tags("article", output)

        print("This is an answer: ", output)

        #with open('tools/market_health_reporter_doc/openai/outputs/output1.md', 'w', encoding='utf-8') as file:
            #file.write(output)   

        post_comment_to_issue(args.github_token, int(args.issue), repo_name, output)
    
    elif "claude:" in args.comment_body:
        with open('tools/market_health_reporter_doc/data/data1.json', 'r') as data_file:
            data = json.load(data_file)

        with open('tools/market_health_reporter_doc/claude/prompts/system_prompt.txt', 'r') as file:
            SYSTEM_PROMPT = file.read()

        with open('tools/market_health_reporter_doc/claude/prompts/prompt1.txt', 'r') as file:
            HUMAN_PROMPT_CONTENT = file.read()

        with open('content/market-health/posts/2023-08-14-huobi/index.md', 'r') as file:
            article_example = file.read()


        HUMAN_PROMPT_CONTENT = f"""
        <example> %s </example>
        {HUMAN_PROMPT_CONTENT}
        <data> %s </data>
        """
        
        prompt = f"{SYSTEM_PROMPT}{HUMAN_PROMPT}{HUMAN_PROMPT_CONTENT%(article_example, data)}{AI_PROMPT}"
        print('This is a prompt: ', prompt)

        completion = anthropic.completions.create(
            model="claude-2.1",
            max_tokens_to_sample=4000,
            temperature=0,
            prompt=prompt,
        )
        
        output = extract_between_tags("article", completion.completion)

        print("This is an answer: ", completion.completion)

        #with open('tools/market_health_reporter_doc/claude/outputs/output1.md', 'w') as file:
            #file.write(output)   

        post_comment_to_issue(args.github_token, int(args.issue), repo_name, output)