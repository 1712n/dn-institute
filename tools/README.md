# Repo Tools 

The scripts are invoked when commenting on a pull request. It only runs if the comment contains a command and the comment author is listed in the `WIKI_REVIEWERS` secret. Only the line containing the command will be interpreted so the comment can have multiple lines and normal content. 

## Payout Calculation

`/payout`

User parameters are:

- `--rate` (`-r`)
- `--multiplier` (`-x`)

*e.g.* `/payout -r 1 -x 2`

## Fact Check

`/qualitycheck`

No special parameters.
