We value original ideas, judgment, and analysis driven by a human, and we close work that is produced by an agent looping against review bots. Using an agent is fine. Letting it replace the contributor is not.

## Before you start

- Check that the issue you are working on is open. Submissions to closed challenges are closed without review.
- Read the whole issue, including the submission requirements, the named reviewers, and any deadline.
- Read the open and recently closed PRs for the same issue. Do not resubmit an analysis someone else already made, and do not build a follow-on to another contributor's open PR and present it as your own.
- Read the sibling files in the target directory and match their structure, naming, frontmatter, and taxonomy values.

## Working with review bots

Bots review every PR. They are useful and often wrong.

- Do not push a fix for every bot comment within minutes of it arriving. Each push triggers another review round, and a PR with many rapid rounds of bot-driven commits reads as an agent talking to a bot.
- Batch the findings, let the contributor decide which ones matter, and push once.
- Reject findings that are out of scope or incorrect, and say why in one or two sentences. Reasoned pushback is a strong signal of human judgment. Silent compliance with every finding is not.
- Do not reply to a bot with long polished summaries of everything you changed. If a reply is needed, keep it short and specific.
- Never chase a bot's approval. An approval from a bot is not a review.

## Content scope

### Market health posts (content/research/market-health/posts/)

- Only sophisticated market manipulation belongs here: wash trading, spoofing, pump-and-dump, oracle or price manipulation, volume fabrication, supply concentration, and similar.
- Out of scope: security exploits, hacks, custody breaches, Ponzi or exit scams, insolvency post-mortems, insider trading, and price discovery studies. An article that concludes it cannot establish manipulation does not belong here either.
- Conclusions must come from primary market data the author worked with, such as order book or trade feeds, statistically significant metric datasets, or the DN Institute market health API. Figures lifted from news, filings, or papers do not count.
- Commit the dataset and the code that produces every figure and number in the post, in the post's own directory. A link to an external companion repository is not enough.
- Baseline quality against the accepted siblings (Huobi, Senso, Bybit). One article per directory, with clear file names.
- A reconstruction of a single well-known historical case is a recap, not original analysis, unless it adds a measurement nobody has made before.

### Market health docs (content/research/market-health/docs/)

- Metric and technique documentation must be backed by data, visuals, or real API responses. Literature or regulatory summaries without data are rejected.

### Crypto attacks wiki (content/research/cyberattacks/wiki/)

- Each page must be a substantive, original explainer of a distinct attack vector, matching sibling pages in depth and structure, including mitigations. No stubs, drafts, or overlaps with existing pages or open PRs.

### Incident reports (content/research/cyberattacks/incidents/)

- Name the file YYYY-MM-DD-Name.md, matching its siblings.
- Reuse existing frontmatter taxonomy values for entity-types and attack-types. Do not invent new ones when an equivalent exists.
- Include on-chain evidence: exploit transaction hashes and attacker addresses, linked to an explorer. Addresses alone are not enough.
- Every factual or quantitative claim needs an inline link to a primary source. Wikipedia and recap sites such as Rekt are background, not evidence.
- Check that every link resolves and that the dates, figures, and attributions match the source you cite. Mark time-sensitive claims with an as-of date.
- Classify the root cause by what the evidence shows.

## Writing

- Write in the contributor's own words. Do not closely paraphrase or lightly reword source text; near-verbatim runs from Wikipedia or press articles are flagged as plagiarism.
- Focus the prose on intent rather than implementation details.
- State findings as flags for review, not verdicts, and name the alternative explanations.
- Fact-check named entities, figures, and dates against current sources before submitting.
- Write plainly and human-like: no rich formatting in prose, no em dashes, no hard-to-type characters, no word wrapping, etc.

## What gets a PR closed

- Submitting to a closed issue, or duplicating or following on from another open submission.
- Many rapid commits driven by bot comments, polished bulk replies to bots, or chasing bot approval.
- Agent artifacts in the diff, such as logs, temp files, or IDE folders, or files that belong to other PRs.
- Data or code that lives only outside the repository, results that cannot be regenerated from the committed code, or a description that disagrees with the committed results.
- Content outside the scope of the target issue, PR, or directory, or edits to a file someone else wrote that the issue does not ask for.
- Requested changes not addressed within a week.
