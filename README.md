## Attack Wiki PR Approval Criteria

Before committing to the wikis, please ensure your submission meets the following criteria:

- The attack is not already covered by existing posts and pending PRs
- File name - YYYY-MM-DD-entity-that-was-hacked.md
- Headers:

| Header name | Required | Description | Example |
|--|--|--|--|
| `date` | yes | YYYY-MM-DD | 2012-07-16 |
`target-entities` | yes  | Entities that were targeted by the attackers. Multiple values allowed | `Binance`, `Localbitcoins`, `ETH`|
`entity-types`| yes | General category describing targeted entity. Multiple values allowed | `Exchange`, `Wallet`, `Blockchain`
`attack-types` | yes  | Common hacking technique, check existing ones and suggest yours if not present. Multiple values allowed | `51%`, `Custodian`, `Flash Loan Attack`|
`title` | yes | Article Title | `BitGrail Hack Results in $170 Million Loss` |

- Focus on **facts and numbers** instead of vague phrases and value judgments (such as "huge losses", "important lesson"). Facts mostly include named entities (people, companies, places, addresses, etc.) Simply repeating what the attacked entity had to say is not enough. Try finding messages from those who spotted anomalies before any official announcements, 3rd party audits, statements from other entities, sources of structured data that show the impact of the attack on prices, volumes, hashrates, etc.
- Add [markdown links](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet#links) directly to your text - they count towards the total bounty amount and help our fact-checking bot to verify claims found in your article.
- The timeline should use bullet points with dates; no significant events should be missing
- Default to **bullet point structure with titles** - this helps to keep the content concise and focused, and is essential for future attack modeling
- Only **standard sections** are allowed. The attack wiki requires the following sections:
  - Summary
  - Attackers (focus on the attackers, not what they did)
  - Losses
  - Timeline
  - Security Failure Causes

If the changes requested by reviewers are not addressed within a week, the PR will be considered stale and will be closed.
