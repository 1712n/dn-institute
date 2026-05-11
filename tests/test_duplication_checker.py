import unittest

from tools.article_checker.duplication_checker import (
    build_new_article_texts,
    generate_comment,
    new_text_handler,
)

ARTICLE_DIR = "content/research/cyberattacks/incidents"


def article_header(filename):
    path = f"{ARTICLE_DIR}/{filename}"
    return f"a/{path} b/{path}\n"


def make_file(header, body):
    return {
        "header": header,
        "body": [
            {
                "header": " -1,1 +1,1 ",
                "body": body,
            }
        ],
    }


class DuplicationCheckerTextTests(unittest.TestCase):
    def test_extracts_added_incident_article_text(self):
        diff = [
            make_file(
                article_header("2026-01-01-Test.md"),
                "+---\n"
                "+target-entities: Test Exchange\n"
                "+---\n"
                "+## Summary\n"
                "+New incident details\n"
                " context line\n"
                "-removed line\n",
            )
        ]

        articles = new_text_handler(diff)

        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]["path"], f"{ARTICLE_DIR}/2026-01-01-Test.md")
        self.assertEqual(articles[0]["target"], "Test Exchange")
        self.assertEqual(articles[0]["text"], "## Summary\nNew incident details")

    def test_uses_article_when_unrelated_file_is_first(self):
        diff = [
            make_file(
                "a/tools/script.py b/tools/script.py\n",
                "+print('not an article')\n",
            ),
            make_file(
                article_header("2026-01-02-Second.md"),
                "+target-entities: Second Target\n+## Summary\n+Relevant text\n",
            ),
        ]

        articles = new_text_handler(diff)

        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]["target"], "Second Target")
        self.assertIn("Relevant text", articles[0]["text"])
        self.assertNotIn("not an article", articles[0]["text"])

    def test_handles_multiple_articles_independently(self):
        diff = [
            make_file(
                article_header("2026-01-04-First.md"),
                "+target-entities: First Target\n+## Summary\n+First text\n",
            ),
            make_file(
                article_header("2026-01-05-Second.md"),
                "+target-entities: Second Target\n+## Summary\n+Second text\n",
            ),
        ]

        articles = new_text_handler(diff)

        self.assertEqual(
            [article["target"] for article in articles],
            ["First Target", "Second Target"],
        )
        self.assertEqual(
            [article["text"] for article in articles],
            ["## Summary\nFirst text", "## Summary\nSecond text"],
        )

    def test_ignores_non_article_markdown(self):
        diff = [
            make_file(
                "a/README.md b/README.md\n",
                "+target-entities: Readme\n+## Summary\n+No review\n",
            )
        ]

        self.assertEqual(build_new_article_texts(diff), [])
        self.assertEqual(new_text_handler(diff), [])

    def test_ignores_deleted_only_article_hunks(self):
        diff = [
            make_file(
                article_header("2026-01-03-Delete.md"),
                "-target-entities: Removed\n-## Summary\n-Removed text\n",
            )
        ]

        self.assertEqual(build_new_article_texts(diff), [])
        self.assertEqual(new_text_handler(diff), [])

    def test_generate_comment_keeps_per_file_results(self):
        answer = (
            f"- `{ARTICLE_DIR}/2026-01-04-First.md`: :white_check_mark:\n"
            f"- `{ARTICLE_DIR}/2026-01-05-Second.md`: :x:"
        )

        comment = generate_comment(answer)

        self.assertIn(answer, comment)
        self.assertNotIn("Is this a new article", comment)


if __name__ == "__main__":
    unittest.main()
