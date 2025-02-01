# Test Articles for Article Checker

This directory contains test articles for validating the DNI Article Checker functionality.

## Articles

### 1. Good Article (`good-article.md`)
A well-formatted article that should pass all checks:
- Valid target entities (SolarWinds, Kaseya, NotPetya)
- Proper formatting and structure
- Factual content with verifiable claims
- Good language and grammar
- No duplication issues

### 2. Bad Article (`bad-article.md`)
An article with intentional issues to test validation:
- Invalid target entities (NonExistentCompany, InvalidTarget)
- Poor formatting and informal language
- Unverifiable claims and vague statements
- Grammar and spelling issues
- Lack of proper citations

## Testing Process
1. Create a new pull request with these articles
2. Comment `/articlecheck` on the PR
3. Verify that the article checker:
   - Correctly identifies valid/invalid target entities
   - Flags language and grammar issues
   - Detects factual accuracy problems
   - Provides appropriate feedback in GitHub comments

## Expected Results

### Good Article
- Should pass target entity validation
- Should pass factual accuracy check
- May have minor language suggestions
- Should be approved overall

### Bad Article
- Should fail target entity validation
- Should fail factual accuracy check
- Should have multiple language issues
- Should be rejected overall 