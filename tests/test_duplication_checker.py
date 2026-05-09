import sys
import types
import unittest


sys.modules.setdefault("github", types.SimpleNamespace(Github=object))
sys.modules.setdefault("openai", types.SimpleNamespace(ChatCompletion=None))
sys.modules.setdefault("requests", types.SimpleNamespace(get=lambda *args, **kwargs: None))
sys.modules.setdefault("bs4", types.SimpleNamespace(BeautifulSoup=object))
sys.modules.setdefault(
    "tiktoken",
    types.SimpleNamespace(
        encoding_for_model=lambda _model: types.SimpleNamespace(encode=lambda text: text.split())
    ),
)

from tools.article_checker.duplication_checker import (  # noqa: E402
    build_target_urls,
    extract_article_summary,
    extract_target_entities,
    new_text_handler,
    normalize_target_entities,
)


class DuplicationCheckerTests(unittest.TestCase):
    def test_normalize_target_entities_handles_multiple_formats(self):
        self.assertEqual(
            normalize_target_entities("[Foo Finance, 'Bar DAO'; Baz Labs]"),
            ["Foo Finance", "Bar DAO", "Baz Labs"],
        )

    def test_extract_target_entities_reads_front_matter_line(self):
        text = "---\ntarget-entities: Foo Finance, Bar DAO\n---\n## Summary\nBody"
        self.assertEqual(extract_target_entities(text), ["Foo Finance", "Bar DAO"])

    def test_extract_article_summary_falls_back_to_full_text(self):
        text = "---\ntarget-entities: Foo Finance\n---\nNo summary heading yet"
        self.assertEqual(extract_article_summary(text), text)

    def test_new_text_handler_combines_files_and_deduplicates_targets(self):
        diff = [
            {
                "header": "a/file-one.md b/file-one.md\n",
                "body": [
                    {
                        "body": (
                            "+---\n"
                            "+target-entities: Foo Finance, Bar DAO\n"
                            "+---\n"
                            "+## Summary\n"
                            "+First body"
                        )
                    }
                ],
            },
            {
                "header": "a/file-two.md b/file-two.md\n",
                "body": [
                    {
                        "body": (
                            "+---\n"
                            "+target-entities: Foo Finance\n"
                            "+---\n"
                            "+## Summary\n"
                            "+Second body"
                        )
                    }
                ],
            },
        ]

        text, targets = new_text_handler(diff)

        self.assertIn("First body", text)
        self.assertIn("Second body", text)
        self.assertEqual(targets, ["Foo Finance", "Bar DAO"])

    def test_build_target_urls_does_not_mutate_base_url(self):
        urls = build_target_urls(
            ["Foo Finance", "Missing", "Bar DAO"],
            "https://dn.institute/attacks/posts/target-entities/",
            ["Foo Finance", "Bar DAO"],
        )

        self.assertEqual(
            urls,
            [
                "https://dn.institute/attacks/posts/target-entities/Foo-Finance",
                "https://dn.institute/attacks/posts/target-entities/Bar-DAO",
            ],
        )


if __name__ == "__main__":
    unittest.main()
