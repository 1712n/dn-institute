# GitHub Copilot Instructions

## General

- Deliver concise, BLUF-driven (bottom line up front) feedback. Strip filler and decorative formatting; prioritize actionable, substantive points over cosmetic ones.
- Flag any divergence from the requirements of the associated issue.
- For prose, watch for plagiarism or derivative content. When you suspect it, provide the exact quote and a link to the source.
- Every factual, quantitative, or temporal claim should be backed by a primary source. Fact-check named entities, figures, dates, and technical claims; flag anything unverifiable, misattributed, conflated, mislabeled, overstated, or future-dated.

## `content/research/cyberattacks/wiki/**` — Attack-vector explainers

- Require a substantive, original explainer of a distinct attack vector that matches sibling pages in depth, structure, and conventions, including a mitigations section.
- Reject draft, stub, thin, derivative, or duplicate submissions that overlap existing wiki pages or open PRs.
- Require an inline primary-source link for every factual or quantitative claim.
- Enforce consistency with siblings across frontmatter, headings, naming, file layout, and internal cross-linking. Flag any divergence.
- Require illustrative exploit code to be labelled as such.

## `content/research/cyberattacks/incidents/**` — Incident reports

- Require accurate, verifiable, well-sourced write-ups consistent with sibling files: on-chain evidence (transaction hashes, addresses), dates, attribution, and root cause.
- Flag thin narrative recaps, unverifiable or future-dated claims, and duplicates of existing incidents or other open PRs adding the same file.

## `content/research/market-health/posts/**` — Market-manipulation analysis

- Scope is limited to sophisticated market manipulation: wash trading, spoofing, pump-and-dump, oracle/price manipulation, volume fabrication, supply concentration, etc. Reject as out of scope: security exploits, hacks, custody breaches, Ponzi/exit-scams, insolvency post-mortems, etc.
- Conclusions must be derived from primary market data the author worked with — orderbook/trade feeds, statistically significant metric datasets, or computed DN Institute crypto-market-health API metrics — not figures lifted from news, filings, or papers.
- Require a committed dataset and/or author-generated charts. Qualitative tables or round-number tables are not datasets. If the prose cites figures, images, or statistics, verify the underlying files are committed and reproducible, and flag any that are not.
- Baseline against accepted siblings (e.g. Huobi, Senso). Output a strict, BLUF list of substantive improvements.

## `content/research/market-health/docs/**` — Metric and technique documentation

- Reject literature or regulatory summaries that lack data, visuals, or API-response documentation.

## `**/posts/*.md` — General post quality

- Baseline quality against sibling files on the `main` branch.
- Fact-check contentious claims with targeted research, and verify temporal accuracy by checking recent developments for the mentioned entities and events.
- Prefer statistically significant metric datasets that support claims over narrative-driven data presented as if it were a structured dataset.
- If the submission falls short, output a strict list of actionable, substantive improvements requiring rigorous research; ignore minor cosmetic fixes.
