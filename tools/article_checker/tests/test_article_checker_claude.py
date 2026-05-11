import unittest

from tools.article_checker.article_checker_claude import (
    analyze_article_structure,
    build_review_input,
    collect_changed_articles,
    extract_added_lines,
    extract_file_path,
    is_new_file_diff,
)


class ArticleCheckerClaudeTest(unittest.TestCase):
    def test_extract_file_path_prefers_new_diff_path(self):
        header = "a/old.md b/content/research/cyberattacks/incidents/2024-01-02-Test.md\n--- a/old.md\n+++ b/content/research/cyberattacks/incidents/2024-01-02-Test.md"

        self.assertEqual(
            extract_file_path(header),
            "content/research/cyberattacks/incidents/2024-01-02-Test.md",
        )

    def test_extract_added_lines_skips_removed_and_metadata_lines(self):
        hunk = "@@ -1,2 +1,2 @@\n-old\n+new\n+++ b/file.md\n context"

        self.assertEqual(extract_added_lines(hunk), ["new"])

    def test_is_new_file_diff_detects_new_file_headers(self):
        self.assertTrue(is_new_file_diff("new file mode 100644\n--- /dev/null"))
        self.assertFalse(is_new_file_diff("--- a/file.md\n+++ b/file.md"))

    def test_collect_changed_articles_ignores_non_article_markdown(self):
        diff = [
            {
                "header": "a/README.md b/README.md\n--- a/README.md\n+++ b/README.md",
                "body": [{"body": "+Readme"}],
            },
            {
                "header": "a/content/research/cyberattacks/incidents/2024-01-02-Test.md b/content/research/cyberattacks/incidents/2024-01-02-Test.md\n--- a/content/research/cyberattacks/incidents/2024-01-02-Test.md\n+++ b/content/research/cyberattacks/incidents/2024-01-02-Test.md",
                "body": [{"body": "+## Summary\n+Test body"}],
            },
        ]

        articles = collect_changed_articles(diff)

        self.assertEqual(len(articles), 1)
        self.assertEqual(
            articles[0]["path"],
            "content/research/cyberattacks/incidents/2024-01-02-Test.md",
        )

    def test_analyze_article_structure_reports_missing_headers(self):
        text = """---
date: 2024-01-02
target-entities: Example
entity-types: exchange
attack-types: exploit
title: Example Hack
loss: $100
---

## Summary
Short text.
"""

        report = analyze_article_structure(
            "content/research/cyberattacks/incidents/example.md", text
        )

        self.assertIn("Filename shape: fail", report)
        self.assertIn("Section headers: warning", report)

    def test_existing_article_edits_do_not_require_full_front_matter(self):
        report = analyze_article_structure(
            "content/research/cyberattacks/incidents/2024-01-02-Example.md",
            "## Summary\nA changed sentence.",
            is_new_file=False,
        )

        self.assertIn("Full-article structure checks: skipped", report)
        self.assertNotIn("Front matter: fail", report)

    def test_build_review_input_includes_all_article_files(self):
        diff = [
            {
                "header": "a/content/research/cyberattacks/incidents/2024-01-02-First.md b/content/research/cyberattacks/incidents/2024-01-02-First.md\n--- a/content/research/cyberattacks/incidents/2024-01-02-First.md\n+++ b/content/research/cyberattacks/incidents/2024-01-02-First.md",
                "body": [{"body": "+## Summary\n+First"}],
            },
            {
                "header": "a/content/research/cyberattacks/incidents/2024-01-03-Second.md b/content/research/cyberattacks/incidents/2024-01-03-Second.md\n--- a/content/research/cyberattacks/incidents/2024-01-03-Second.md\n+++ b/content/research/cyberattacks/incidents/2024-01-03-Second.md",
                "body": [{"body": "+## Summary\n+Second"}],
            },
        ]

        prompt, paths = build_review_input(diff)

        self.assertEqual(len(paths), 2)
        self.assertIn("2024-01-02-First.md", prompt)
        self.assertIn("2024-01-03-Second.md", prompt)


if __name__ == "__main__":
    unittest.main()
