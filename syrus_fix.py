```python
#!/usr/bin/env python3
"""
PD-Hunter Intelligence: ProjectDiscovery Bounty Intelligence Platform
Persona: The Strategic Bounty Hunter
Description: Automates triage across 15+ ProjectDiscovery repositories.
             Filters out high-friction "War Zones" and identifies high-ROI
             "S-Tier" bugs and "Hidden Gems" for maximum bounty efficiency.
"""

import os
import json
import urllib.request
from urllib.error import HTTPError
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict

# --- Configuration ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
PD_REPOS = [
    "projectdiscovery/nuclei",
    "projectdiscovery/nuclei-templates",
    "projectdiscovery/subfinder",
    "projectdiscovery/httpx",
    "projectdiscovery/naabu",
    "projectdiscovery/interactsh",
    "projectdiscovery/katana",
    "projectdiscovery/notify",
    "projectdiscovery/dnsx",
    "projectdiscovery/tlsx",
    "projectdiscovery/uncover",
    "projectdiscovery/alterx",
    "projectdiscovery/asnmap",
    "projectdiscovery/cvemap",
    "projectdiscovery/chaos-client"
]

# --- ANSI Colors ---
class Colors:
    S_TIER = '\033[95m'      # Magenta
    HIDDEN_GEM = '\033[96m'  # Cyan
    WAR_ZONE = '\033[91m'    # Red
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

class PDHunterIntel:
    def __init__(self, token: str):
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable is required.")
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.intel_data: Dict[str, List[Dict]] = {
            "S_TIER": [],
            "HIDDEN_GEM": [],
            "WAR_ZONE": []
        }

    def fetch_open_issues(self, repo: str) -> List[Dict]:
        """Fetch open issues (excluding PRs) for a specific repository."""
        url = f"https://api.github.com/repos/{repo}/issues?state=open&per_page=100"
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req) as response:
                issues = json.loads(response.read())
                # Filter out Pull Requests
                return [i for i in issues if "pull_request" not in i]
        except HTTPError as e:
            print(f"Error fetching {repo}: {e}")
            return []

    def evaluate_roi(self, issue: Dict, repo: str) -> None:
        """
        The Strategic Bounty Hunter Algorithm.
        Evaluates an issue's ROI based on friction, age, and label semantics.
        """
        comments = issue.get("comments", 0)
        labels = [l.get("name", "").lower() for l in issue.get("labels", [])]
        created_at = datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        age_days = (datetime.utcnow() - created_at).days

        # Feature Extractors
        is_bug_or_sec = any(l in labels for l in ["security", "bug", "critical", "p1", "bounty"])
        is_assigned = bool(issue.get("assignee"))
        is_stale_or_locked = issue.get("locked", False) or "wontfix" in labels or "duplicate" in labels

        intel_packet = {
            "repo": repo,
            "title": issue["title"],
            "url": issue["html_url"],
            "comments": comments,
            "age": age_days,
            "labels": labels
        }

        # 1. WAR ZONE (High Friction / Low ROI)
        # Highly contested, already assigned, or locked.
        if comments >= 5 or is_assigned or is_stale_or_locked:
            self.intel_data["WAR_ZONE"].append(intel_packet)
            return

        # 2. S-TIER (High ROI / Immediate Action Required)
        # Confirmed bugs/security issues with minimal competition.
        if is_bug_or_sec and comments <= 2 and age_days < 30:
            self.intel_data["S_TIER"].append(intel_packet)
            return

        # 3. HIDDEN GEM (Medium-High ROI / Stealth Exploitation)
        # Unnoticed bugs, older but unresolved, zero noise.
        if comments == 0 and age_days >= 7 and age_days <= 120 and not is_assigned:
            self.intel_data["HIDDEN_GEM"].append(intel_packet)
            return

    def run_recon(self) -> None:
        print(f"{Colors.BOLD}[*] Initiating PD-Hunter Intelligence Recon across {len(PD_REPOS)} targets...{Colors.RESET}")

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self.fetch_open_issues, repo): repo for repo in PD_REPOS}

            for future in futures:
                repo = futures[future]
                issues = future.result()
                for issue in issues:
                    self.evaluate_roi(issue, repo)

        self.generate_report()

    def generate_report(self) -> None:
        """Output the actionable intelligence."""
        print(f"\n{Colors.BOLD}=== STRATEGIC BOUNTY HUNTER INTELLIGENCE REPORT ==={Colors.RESET}")

        # Sort S-Tier by newest
        self.intel_data["S_TIER"].sort(key=lambda x: x["age"])
        # Sort Hidden Gems by least comments, then age
        self.intel_data["HIDDEN_GEM"].sort(key=lambda x: (x["comments"], x["age"]))

        print(f"\n{Colors.S_TIER}{Colors.BOLD}🏆 S-TIER BUGS (High ROI | Low Friction | Action: IMMEDIATE){Colors.RESET}")
        if not self.intel_data["S_TIER"]:
            print("  No S-Tier targets currently available.")
        for item in self.intel_data["S_TIER"][:10]: # Top 10
            print(f"  [ {item['repo']} ] {item['title'][:60].ljust(60)} | Age: {item['age']}d | Comments: {item['comments']}")
            print(f"  {Colors.DIM}↳ {item['url']}{Colors.RESET}")

        print(f"\n{Colors.HIDDEN_GEM}{Colors.BOLD}💎 HIDDEN GEMS (Zero Noise | Stealth Exploitation | Action: INVESTIGATE){Colors.RESET}")
        if not self.intel_data["HIDDEN_GEM"]:
            print("  No Hidden Gems currently available.")
        for item in self.intel_data["HIDDEN_GEM"][:10]: # Top 10
            print(f"  [ {item['repo']} ] {item['title'][:60].ljust(60)} | Age: {item['age']}d | Comments: {item['comments']}")
            print(f"  {Colors.DIM}↳ {item['url']}{Colors.RESET}")

        print(f"\n{Colors.WAR_ZONE}{Colors.BOLD}⚠️  WAR ZONES FILTERED: {len(self.intel_data['WAR_ZONE'])} (Time-Sinks Avoided){Colors.RESET}")
        print(f"{Colors.DIM}* Focus your energy on the S-Tier and Hidden Gems listed above.{Colors.RESET}\n")


if __name__ == "__main__":
    try:
        hunter = PDHunterIntel(GITHUB_TOKEN)
        hunter.run_recon()
    except ValueError as e:
        print(f"{Colors.WAR_ZONE}Error: {e}{Colors.RESET}")
        print("Please run: export GITHUB_TOKEN='your_personal_access_token'")
    except Exception as e:
        print(f"{Colors.WAR_ZONE}Critical Failure during execution: {e}{Colors.RESET}")
```