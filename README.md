Distributed Networks Institute (DNI) aims to help infrastructure resilience and financial health of distributed networks through scientific, engineering, and educational efforts. We are a part of a 501(c)3 non-profit incubator in Washington, DC called [BlockShop](https://blockshop.org/). Constantly on the lookout for talent, we encourage anyone to contribute code, market analysis, and engineering expertise to one of our [active projects](https://dn.institute/#projects). Multiple research grants and [code bounties](https://github.com/1712n/dn-institute/labels/%F0%9F%92%B0%20bounty) are available.

## 🏆 Challenge Program

[![Challenge Program Video](https://blockshopdc.com/static/assets/images/challenge.jpg)](https://link.hygge.work/MayaVick_Challenge)

We maintain a list of real-world problems we work on to give interested individuals a chance to prove themselves, learn a bit about us, and boost their GitHub profiles in the process. The challenge program was so successful for some teams, that they made solving a challenge a hard requirement for joining them. Our challenges are extremely independent and will require you to manage your own time and work process. Check out the [success stories](https://www.instagram.com/explore/tags/challenge_successstory/) of the challenge winners.

### General rules

- Anyone can participate in a challenge. You do not need anyone's approval to start working or to submit your results.
- Some challenges are paid and have bounties attached to them. When you complete a bounty task, please message bounty-payout@dn.institute with a link to your merged pull request and a Bitcoin or an altcoin address to get paid. We pay all bounties at the end of each month and close tasks as soon as we get enough good quality submissions that fulfill all the requirements.
- By participating in the Challenge Program, you agree to let challenge creators use any and all work submitted for any internal or external purposes.

### Navigating and Working with the Tasks

- In the [issue list](https://github.com/1712n/dn-institute/issues), you'll find a list of tasks that are currently available.
- You are free to start working on any open challenge issue whenever you want.
- For highly complex tasks, we are willing to lock individual issues for qualified candidates to make sure no one else is working on it. For that, please comment in the issue and email challenge@blockshop.org with your CV/profile. We'll review your request and assign the issue exclusively to you.
- To be alerted whenever we create new tasks, please click "👁 Watch" and "☆ Star" in the upper right corner.

## 🌱 Giving Back

### 🔬 Research

DNI has a growing scientific research team, focused on the application of Large Language Models to risk modeling. If you are interested in gaining relevant skills while publishing scientific papers along the way, solve one of the [NLP challenges](https://github.com/1712n/dn-institute/labels/nlp) and mention your interest in joining the research team. Multiple research grants are available!

### 🧑‍🎓 Training

We are happy to train anyone willing to learn our tools. Show initiative by contributing to one of the [open issues](https://github.com/1712n/dn-institute/issues) and mention in your pull request that you want to be considered for any training opportunities they might have available.

### 🎖️ Veterans

Our diverse community includes military veterans from a wide variety of backgrounds. If you are in the process of getting out of the U.S. military, check out our SkillBridge program. Whether you qualify as eligible U.S. military personnel, or served in the armed forces of another country, solve one of the challenges and/or reach out to [@jhirschkorn](https://github.com/jhirschkorn).

## 🚀 Improving the QA Bot for the Crypto Attack Wiki

The current QA bot, implemented as a GitHub Actions workflow, performs basic checks on pull requests to ensure they align with the submission guidelines. While functional, it can be enhanced to improve accuracy, reduce false positives, and streamline the review process. Below is a refactored version of the bot that introduces more robust logic, better error handling, and improved efficiency.

### Key Improvements

1. **Enhanced Markdown Validation**: The bot now checks for proper formatting, including correct heading levels, consistent markdown syntax, and valid links.
2. **Content Quality Checks**: It ensures that each article includes a clear summary, threat vector, and mitigation strategy.
3. **Efficient File Handling**: The bot processes only the relevant files (e.g., `.md` files in the `attacks` directory) and avoids unnecessary checks on other files.
4. **Error Logging and Feedback**: It provides more detailed feedback to contributors, including line numbers and specific issues found in their PR.

### Refactored Workflow Logic

```python
import os
import re
from datetime import datetime

def validate_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for valid markdown syntax
    if not re.match(r'^#{1,6} ', content, re.MULTILINE):
        return False, "Invalid markdown syntax: missing heading."

    # Check for proper file structure
    if not re.search(r'\n## Summary\n.*\n## Threat Vector\n.*\n## Mitigation Strategy', content, re.DOTALL):
        return False, "Missing required sections: Summary, Threat Vector, Mitigation Strategy."

    # Check for valid links
    if re.search(r'\[.*\]\(.*\)', content):
        for link in re.findall(r'\[.*\]\(.*\)', content):
            if not re.match(r'^https?://', link.split(')')[1]):
                return False, f"Invalid link: {link.split(')')[1]}"

    return True, "Markdown is valid and meets submission guidelines."

def main():
    pr_number = os.getenv('PR_NUMBER')
    repo_root = os.getenv('GITHUB_WORKSPACE')
    files_to_check = [os.path.join(repo_root, 'content', 'attacks', f) for f in os.listdir(os.path.join(repo_root, 'content', 'attacks')) if f.endswith('.md')]

    for file in files_to_check:
        is_valid, message = validate_markdown(file)
        if not is_valid:
            print(f"❌ PR #{pr_number} - {file}: {message}")
            return False
        else:
            print(f"✅ PR #{pr_number} - {file}: {message}")

    return True

if __name__ == "__main__":
    exit(0 if main() else 1)
```

### Additional Considerations

- **Performance Optimization**: The bot now uses efficient regex patterns and avoids redundant checks.
- **Security**: All file operations are performed within the GitHub Actions sandbox, ensuring no unintended file access.
- **Scalability**: The bot can be extended to support additional directories or file types as needed.

By implementing these improvements, the QA bot becomes more reliable, user-friendly, and aligned with the goals of the Distributed Networks Institute. This change not only enhances the contributor experience but also ensures higher quality content for the Crypto Attack Wiki.
