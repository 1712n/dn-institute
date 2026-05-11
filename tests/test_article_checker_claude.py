import sys
import types
import unittest


github_module = types.ModuleType("github")
github_module.Github = object
sys.modules.setdefault("github", github_module)

llm_utils_module = types.ModuleType("tools.python_modules.llm_utils")
llm_utils_module.remove_plus = lambda text: "\n".join(
    line[1:] if line.startswith("+") else line
    for line in text.splitlines()
    if line.startswith("+") and not line.startswith("+++")
)
sys.modules.setdefault("tools.python_modules.llm_utils", llm_utils_module)

retriever_module = types.ModuleType("tools.article_checker.claude_retriever")
retriever_module.ClientWithRetrieval = object
sys.modules.setdefault("tools.article_checker.claude_retriever", retriever_module)

websearch_module = types.ModuleType(
    "tools.article_checker.claude_retriever.searcher.searchtools.websearch"
)
websearch_module.BraveSearchTool = object
sys.modules.setdefault(
    "tools.article_checker.claude_retriever.searcher.searchtools.websearch",
    websearch_module,
)

from tools.article_checker.article_checker_claude import build_article_review_text


class ArticleReviewTextTests(unittest.TestCase):
    def test_builds_text_from_attack_article_markdown_only(self):
        diff = [
            {
                "header": "a/content/attacks/example.md b/content/attacks/example.md\n+++ b/content/attacks/example.md\n",
                "body": [
                    {"body": "+# Example\n+Added claim\n-context\n"},
                    {"body": "+Second addition\n"},
                ],
            },
            {
                "header": "a/tools/script.py b/tools/script.py\n+++ b/tools/script.py\n",
                "body": [{"body": "+print('skip')\n"}],
            },
        ]

        review_text = build_article_review_text(diff)

        self.assertIn("File: content/attacks/example.md", review_text)
        self.assertIn("# Example", review_text)
        self.assertIn("Added claim", review_text)
        self.assertIn("Second addition", review_text)
        self.assertNotIn("script.py", review_text)
        self.assertNotIn("print('skip')", review_text)

    def test_returns_empty_text_when_no_attack_articles_changed(self):
        diff = [
            {
                "header": "a/README.md b/README.md\n+++ b/README.md\n",
                "body": [{"body": "+Unrelated docs\n"}],
            }
        ]

        self.assertEqual(build_article_review_text(diff), "")


if __name__ == "__main__":
    unittest.main()
