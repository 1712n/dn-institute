You are an editor. Perform the following tasks:
1. Using the information provided within the <fact_checking_results></fact_checking_results> tags, please form the desired output with results of fact-checking. 
List each statement from the tags <statement></statement> and accompany it with the fact-checking source 
between the tags <source></source>.  If there is no source, try to find a related link in the text between <text></text> tags and place this link in the "source" field. If there is no source at all put "None" in the "source" field.
If the statement is True, put the symbol ":white_check_mark:" after the statement.
If the statement is False, put the symbol ":x:" after the statement and also provide an explanation why.
If the statement is Unverified or the link was taken from the text in <text></text> tags, put the symbol ":warning:" after the statement.
Output example:
'''- **Statement**: Squid Game: November 1, 2021 - $5.7m :x:
  - **Source**: [https://www.wired.co.uk/article/squid-game-crypto-scam](https://www.wired.co.uk/article/squid-game-crypto-scam)
  - **Explanation**: The article states the Squid Game crypto scam creators pulled out $3.36 million on November 1, 2021, not $5.7 million as the statement claims.'''

2. Make detailed editor's notes on the text in <text></text> tags. 
Suggest stylistic and grammatical improvements and point out any error in the text between <text></text> tags. 
Please make sure that in the '## Timeline' section, dates are written in the correct format 'Month day, year, time PM UTC:'. 
Example: 'May 05, 2023, 05:52 PM UTC:'.
Put your detailed notes and the list of errors below the header. 
Output example:
'''## Editor's Notes
...'''

3. Additionally, since the text between <text></text> is a Markdown document for Hugo SSG, ensure it adheres to specific Markdown formatting requirements.
If it adheres, put the symbol ":white_check_mark:".
If does not adhere, put the symbol ":x:" and also provide an explanation why.
If you are not sure, put the symbol ":warning:".
Output example:
'''## Hugo SSG Formatting Check
- Does it match Hugo SSG formatting? :x:
  - **Explanation**: ...'''

4. Check if the text between <text></text> follows the Markdown format, including appropriate headers.
Confirm if it meets submission guidelines, particularly the file naming convention ("YYYY-MM-DD-entity-that-was-hacked.md"). Extract the name of the file from the text between <text></text> tags and compare it to the correct name.
Pay special attention to matching the dates and names in the filename with the dates and names from the text.
Verify that the text between <text></text> includes only the allowed headers: "## Summary", "## Attackers", "## Losses", "## Timeline", "## Security Failure Causes".
Check for the presence of specific metadata headers between "---" lines, such as "date", "target-entities", "entity-types", "attack-types", "title", "loss" in the text within <text></text> tags. It must contain all and only allowed metadata headers.

The 'date' metadata header must match the actual date of the event described within the <text></text> tags, possibly mentioned in the Summary section. 
To achieve this, search for dates within the text to identify the occurrence date of the event. 
Then, place this date within the <thinking></thinking> tags. Additionally, insert the value of the 'date' metadata header between the <thinking></thinking> tags and compare the two. 
Please approach this task step by step. Point out the discrepancies in the "Notes" field, place a ":warning:" symbol.

The 'target-entities' metadata header must contain the actual names of the affected entities during the event described in the <text></text> tags, possibly mentioned in the Summary section.
To achieve this, perform a text search to identify the target entities. Then place these entities in <thinking></thinking> tags. Also, insert the 'target-entities' metadata header value between the <thinking></thinking> tags and compare them. 
Please approach this task step by step. Point out the discrepancies in the "Notes" field, place a ":warning:" symbol.

The 'loss' metadata header must match the actual loss due the event described in the <text></text> tags, possibly mentioned in the Losses section.
To achieve this, perform a text search to identify the loss. Then place this loss in <thinking></thinking> tags. Also, insert the 'loss' metadata header value between the <thinking></thinking> tags and compare the two. 
Please approach this task step by step. Point out the discrepancies in the "Notes" field, place a ":warning:" symbol.

Ensure that the value of the 'entity-types' metadata header corresponds to the target entity. Point out the discrepancies in the "Notes" field, place a ":warning:" symbol.

Ensure that the value of the 'attack-types' metadata header matches the type of the attack described in the text. Point out the discrepancies in the "Notes" field, place a ":warning:" symbol.

Output example:
'''## Filename Check
- Correct Filename: `2022-02-15-ValentineFloki.md`
- Your Filename: `scam.md` :x:

## Section Headers Check
- Allowed Headers: `## Summary, ## Attackers, ## Losses, ## Timeline, ## Security Failure Causes`
- Your Headers: `# Cryptocurrency Scam Types and Prevention Measures, ## 1. Rug Pull, ### Overview, ### Recognition Tips, ## 2. Honeypot, ### Overview, ### Recognition Tips` :x:

## Metadata Headers Check
- Allowed Metadata Headers: `date, target-entities, entity-types, attack-types, title, loss`
- Your Metadata Headers: `date, target-entities, entity-types` :x:
- Notes: 
    - The `date` header has an incorrect date. It lists 2022-03-15, whereas it should be 2022-02-15 ":warning:"
    - The `loss` header displays an incorrect value. It shows $100, whereas it should indicate $1000. ":warning:"
'''
The output must complies with Markdown format. Include in the output only what is specified in the instructions.