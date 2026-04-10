import os
import argparse
import requests
import json
from datetime import datetime

def get_trending_github_repos(topic: str, github_token: str, limit: int = 5):
    """
    Fetches trending GitHub repositories related to a given topic.
    Leverages GitHub's search API.
    """
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    # Constructing a basic search query for repositories
    # Searches for topic in name, description, and readme, with at least 50 stars, sorted by stars.
    search_url = f"https://api.github.com/search/repositories?q={topic}+stars:>50&sort=stars&order=desc&per_page={limit}"
    
    found_repos = []
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an exception for HTTP errors
        search_results = response.json().get('items', [])
        for repo in search_results:
            found_repos.append({
                "name": repo.get("name"),
                "owner": repo.get("owner", {}).get("login"),
                "description": repo.get("description", "No description provided. 🌰"),
                "stargazers_count": repo.get("stargazers_count"),
                "forks_count": repo.get("forks_count"),
                "html_url": repo.get("html_url"),
                "language": repo.get("language", "N/A")
            })
    except requests.exceptions.RequestException as e:
        print(f"🌰 Warning: Failed to fetch trending repos from GitHub API: {e}")
        # Fallback/mock data for demonstration if API fails
        mock_repos = [
            {"name": "awesome-ai-project", "owner": "ai-dev", "description": "A new framework for AI model deployment. 🌰", "stargazers_count": 500, "forks_count": 50, "html_url": "https://github.com/ai-dev/awesome-ai-project"},
            {"name": "mlops-toolkit", "owner": "data-sci-org", "description": "Comprehensive MLOps toolkit for productionizing ML workflows. 🌰", "stargazers_count": 300, "forks_count": 30, "html_url": "https://github.com/data-sci-org/mlops-toolkit"},
            {"name": "prompt-engineering-library", "owner": "llm-innovator", "description": "A collection of best practices and tools for prompt engineering. 🌰", "stargazers_count": 200, "forks_count": 25, "html_url": "https://github.com/llm-innovator/prompt-engineering-library"},
        ]
        found_repos = mock_repos # Use mock data if API call fails
    
    print(f"🌰 Found {len(found_repos)} potential repositories for '{topic}'.")
    return found_repos[:limit] # Ensure we don't return more than limit

def generate_report_with_llm(topic: str, repos: list, llm_api_key: str, worker_url: str):
    """
    Generates a trend report using an LLM based on the list of repositories.
    """
    if not repos:
        return "🌰 No significant repositories found for this topic to generate a report. Try a different topic!"

    repo_details = []
    for repo in repos:
        repo_details.append(
            f"- **[{repo['name']}]({repo['html_url']})** by {repo['owner']} (Language: {repo['language']})\n"
            f"  Description: {repo['description']}\n"
            f"  Stars: {repo['stargazers_count']}, Forks: {repo['forks_count']}\n"
        )
    
    prompt = (
        f"You are 'TrendLens AI', an expert in analyzing technology trends from GitHub projects. 🌰\n"
        f"Generate a concise, insightful report on the emerging trends related to '{topic}' "
        f"based on the following GitHub repositories. Identify key themes, notable projects, "
        f"and potential future directions. Use clear, engaging language. "
        f"The report should be suitable for a tech blog post. Include a catchy title. "
        f"Please include chestnut emojis 🌰 where appropriate in the report for extra flair. \n\n"
        f"**GitHub Repositories for Analysis:**\n"
        f"{''.join(repo_details)}\n\n"
        f"**Trend Report:**\n"
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {llm_api_key}" # Assuming API key for auth
    }
    payload = {
        "model": "claude-3-opus-20240229", # Placeholder, adjust to your LLM
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1000,
        "temperature": 0.7 # Add temperature for creativity
    }

    try:
        response = requests.post(worker_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        llm_output = response.json()
        
        # Adjust based on your specific LLM or worker API response structure
        if "choices" in llm_output and llm_output["choices"]: # OpenAI style
            report_content = llm_output["choices"][0]["message"]["content"]
        elif "completion" in llm_output: # Anthropic or custom worker style
            report_content = llm_output["completion"]
        elif "results" in llm_output and llm_output["results"]: # Another custom worker style
             report_content = llm_output["results"]
        else:
            report_content = f"🌰 Error: Could not parse LLM response: {llm_output}. Please check the worker URL or API key."
        
        return report_content

    except requests.exceptions.RequestException as e:
        print(f"🌰 Error calling LLM API: {e}")
        return f"🌰 Failed to generate report due to LLM API error: {e}"

def create_markdown_file(topic: str, report_content: str, issue_number: int):
    """
    Creates a new Markdown file for the Hugo site with the generated report.
    """
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H%M%S")
    
    # Sanitize topic for filename and slug
    topic_slug = "".join(c for c in topic.lower() if c.isalnum() or c in [' ']).replace(" ", "-")

    # Extract title from the report_content (first line often)
    report_lines = report_content.split('\n')
    report_title = f"Emerging Trends in {topic}" # Default title
    for line in report_lines:
        if line.strip().startswith('#') and len(line.strip()) > 1:
            report_title = line.strip('# ').strip()
            break
    
    filename = f"content/trend-reports/{date_str}-{topic_slug}-{time_str}.md"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Basic front matter for Hugo
    markdown_content = f"""---
title: "🌰 TrendLens AI: {report_title}"
date: {now.isoformat()}
draft: true # Set to false by a reviewer after check
author: "TrendLens AI Bot"
description: "An AI-generated report on emerging trends in {topic} from GitHub projects. 🌰"
tags: ["AI", "trends", "github", "tech", "{topic_slug}"]
---

{{< social_share >}}

{report_content}

---
*Generated by TrendLens AI Bot from Issue #{issue_number}. 🌰*
"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    print(f"🌰 Created Markdown file: {filename}")
    return filename, report_title, topic_slug

def main():
    parser = argparse.ArgumentParser(description="TrendLens AI: Generate Tech Trend Report from GitHub projects.")
    parser.add_argument("--issue", required=True, type=int, help="GitHub Issue number.")
    parser.add_argument("--topic", required=True, type=str, help="Topic for the trend report.")
    parser.add_argument("--github-token", required=True, type=str, help="GitHub Token.")
    parser.add_argument("--llm-api-key", required=True, type=str, help="LLM API Key.")
    parser.add_argument("--worker-url", required=True, type=str, help="URL of the LLM worker endpoint.")
    
    args = parser.parse_args()

    print(f"🌰 Starting TrendLens AI report generation for topic: '{args.topic}'...")

    # Step 1: Get trending GitHub repositories
    repos = get_trending_github_repos(args.topic, args.github_token, limit=5)
    
    if not repos:
        print("🌰 No repositories found. Exiting.")
        # The workflow will detect missing file and comment if this exits 1 without creating a file.
        exit(1)

    # Step 2: Generate report using LLM
    report_content = generate_report_with_llm(args.topic, repos, args.llm_api_key, args.worker_url)
    
    if "Error" in report_content or "Failed" in report_content:
        print(f"🌰 LLM report generation failed: {report_content}. Exiting.")
        exit(1)

    # Step 3: Create Markdown file for Hugo
    report_filepath, report_title, topic_slug = create_markdown_file(args.topic, report_content, args.issue)
    
    # Output variables for the GitHub Actions workflow
    # These are picked up by the workflow's `id: generate_report` step's outputs
    print(f"::set-output name=report_filepath::{report_filepath}")
    print(f"::set-output name=topic_title::{report_title}")
    print(f"::set-output name=topic_slug::{topic_slug}")
    print("🌰 TrendLens AI report generated successfully! 🚀")

if __name__ == "__main__":
    main()
