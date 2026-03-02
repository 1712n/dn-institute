#!/usr/bin/env python3
# 🌰 ChestnutAI ingestion pipeline

import os
import json
import datetime as dt
from typing import List
import httpx
import openai

openai.api_key = os.environ["OPENAI_API_KEY"]

TWITTER_URL = "https://api.twitter.com/2/tweets/search/recent"
HEADERS = {"Authorization": f"Bearer {os.environ['TWITTER_BEARER_TOKEN']}"}
QUERY = "bitcoin OR ethereum OR solana hack OR exploit OR rug -is:retweet lang:en"


class Tweet:
    def __init__(self, id_str: str, text: str):
        self.id_str = id_str
        self.text = text


def fetch_tweets() -> List[Tweet]:
    params = {
        "query": QUERY,
        "max_results": 100,
        "tweet.fields": "created_at,author_id",
    }
    r = httpx.get(TWITTER_URL, headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    return [Tweet(t["id"], t["text"]) for t in data.get("data", [])]


def score_risk(tweets: List[Tweet]) -> List[dict]:
    scored = []
    prompt_template = open(".github/prompts/risk-scorer.txt").read()
    for tw in tweets:
        prompt = prompt_template.replace("{{TWEET}}", tw.text)
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=60,
        )
        answer = resp.choices[0].message.content.strip()
        # Expected format: "score:0.87 label:hack"
        try:
            score = float(answer.split("score:")[1].split()[0])
            label = answer.split("label:")[1].split()[0]
        except Exception:
            score, label = 0.0, "unknown"
        scored.append(
            {
                "id": tw.id_str,
                "text": tw.text,
                "score": score,
                "label": label,
                "timestamp": dt.datetime.utcnow().isoformat(),
            }
        )
    return scored


if __name__ == "__main__":
    tweets = fetch_tweets()
    results = score_risk(tweets)
    out_path = "data/risk_events.jsonl"
    os.makedirs("data", exist_ok=True)
    with open(out_path, "a") as f:
