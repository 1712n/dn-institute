## Cryptocurrency Ecosystem Threat Modeling

We are looking for talent to join our efforts to model attacks on critical infrastructure in the crypto space. Multiple [research grants](https://github.com/1712n/challenge/issues/97) and [code bounties](https://github.com/1712n/challenge/issues/100) are available for the following tasks:

1. Modeling current tactics, techniques and procedures (TTP) of crypto attacks
1. Building a taxonomy of current harms, risks and vulnerabilities.
1. Threat modeling of the technical, social, regulatory and political vectors of attack to the financial ecosystem.
1. Identifying critical points of failure common to the cyberinfrastructure of cryptocurrency and traditional finance.

To participate and find out more, submit a pull request to this repository that meets the criteria outlined below.

## Attack Wiki PR Approval Criteria

 Submit a pull request that adds or modifies files in the [`attacks` directory](https://github.com/1712n/dn-institute/tree/main/content/attacks). All submissions will be reviewed by the wiki maintainers, and additional changes to your pull request may be asked of you to bring your submission to the quality level of the rest of the wiki.

### Submission ideas

- New pages
- Page placeholders with metadata
- Additions to existing pages
- Meaningful edits to existing content that fix typos, grammar, factual and stylistic errors, etc.

Before committing to the wikis, please ensure your submission meets the following criteria:

- The attack is not already covered by existing posts and pending PRs
- File name - YYYY-MM-DD-entity-that-was-hacked.md
- Headers:

| Header name | Required | Description | Example |
|--|--|--|--|
| `date` | yes | YYYY-MM-DD | 2012-07-16 |
`target-entities` | yes  | Entities that were targeted by the attackers. Multiple values allowed | `Binance`, `Localbitcoins`, `Ethereum`|
`entity-types`| yes | General category describing targeted entity. Check existing ones in the examples and suggest yours if not present. Multiple values allowed | `Custodian`, `DeFi`, `GameFi`, `Exchange`, `Wallet`, `Blockchain`, `Bridge`, `Yield Aggregator`, `Lending Platform`, `Stablecoin`, `Token`, `NFT` |
`attack-types` | yes  | Common hacking technique, check existing ones in the examples and suggest yours if not present. Multiple values allowed | `51%`, `Wallet Hack`,`Private Key Leak`, `Infrastructure Attack`, `Smart Contract Exploit`, `Flash Loan Attack`, `Phishing`, `Signature Verification Issue`, `Brute Force`, `Race Condition Exploit`|
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
