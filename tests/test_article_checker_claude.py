import sys
import types
import unittest


github_module = types.ModuleType("github")
github_module.Github = object
sys.modules.setdefault("github", github_module)

llm_utils_module = types.ModuleType("tools.python_modules.llm_utils")
llm_utils_module.remove_plus = lambda text: "\n".join(
    line[1:] if line.startswith("+") else line
    for line in text.split("\n")
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

    def test_handles_attack_article_in_subdirectory(self):
        diff = [
            {
                "header": "a/content/attacks/subdir/example.md b/content/attacks/subdir/example.md\n+++ b/content/attacks/subdir/example.md\n",
                "body": [{"body": "+Nested article text\n"}],
            }
        ]

        review_text = build_article_review_text(diff)

        self.assertIn("File: content/attacks/subdir/example.md", review_text)
        self.assertIn("Nested article text", review_text)

    def test_ignores_deleted_only_attack_article(self):
        diff = [
            {
                "header": "a/content/attacks/example.md b/content/attacks/example.md\n+++ b/content/attacks/example.md\n",
                "body": [{"body": "-Deleted claim\n context\n"}],
            }
        ]

        self.assertEqual(build_article_review_text(diff), "")

    def test_handles_empty_diff(self):
        self.assertEqual(build_article_review_text([]), "")

    def test_preserves_literal_leading_plus_in_added_line(self):
        diff = [
            {
                "header": "a/content/attacks/example.md b/content/attacks/example.md\n+++ b/content/attacks/example.md\n",
                "body": [{"body": "++C compiler note\n"}],
            }
        ]

        review_text = build_article_review_text(diff)

        self.assertIn("+C compiler note", review_text)

    def test_preserves_added_markdown_line_starting_with_plus_markers(self):
        diff = [
            {
                "header": "a/content/attacks/example.md b/content/attacks/example.md\n+++ b/content/attacks/example.md\n",
                "body": [{"body": "++++ front matter delimiter example\n"}],
            }
        ]

        review_text = build_article_review_text(diff)

        self.assertIn("+++ front matter delimiter example", review_text)


if __name__ == "__main__":
    unittest.main()
