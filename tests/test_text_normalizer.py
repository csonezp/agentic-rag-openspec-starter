import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from agent_kb.document_loader import KnowledgeDocument
from agent_kb.text_normalizer import (
    NormalizedDocument,
    normalize_document,
    normalize_documents,
    normalize_markdown_text,
)
from scripts.normalize_documents import main, parse_args


class TextNormalizerTest(unittest.TestCase):
    def test_normalizes_common_markdown_syntax(self):
        markdown = """# 主标题

这是一段  包含\t多余空白的文字。

- 第一项
* 第二项
1. 第三项

参考 [项目文档](https://example.com)。

```python
print("hello")
```
"""

        text = normalize_markdown_text(markdown)

        self.assertEqual(
            text,
            '主标题\n\n这是一段 包含 多余空白的文字。\n\n第一项\n第二项\n第三项\n\n参考 项目文档。\n\nprint("hello")',
        )

    def test_normalizes_document_and_preserves_metadata(self):
        document = KnowledgeDocument(
            source_path="guide/intro.md",
            title="介绍",
            content="# 介绍\n\n阅读 [指南](https://example.com)。",
        )

        normalized = normalize_document(document)

        self.assertEqual(
            normalized,
            NormalizedDocument(
                source_path="guide/intro.md",
                title="介绍",
                text="介绍\n\n阅读 指南。",
            ),
        )

    def test_normalizes_multiple_documents(self):
        documents = [
            KnowledgeDocument("a.md", "A", "# A"),
            KnowledgeDocument("b.md", "B", "# B"),
        ]

        normalized = normalize_documents(documents)

        self.assertEqual([document.title for document in normalized], ["A", "B"])
        self.assertEqual([document.text for document in normalized], ["A", "B"])

    def test_parse_args_uses_knowledge_by_default(self):
        args = parse_args([])

        self.assertEqual(args.source_dir, "knowledge")

    def test_demo_script_prints_normalized_documents(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "note.md").write_text(
                "# 笔记\n\n请看 [链接](https://example.com)。",
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main([str(root)])

        self.assertEqual(exit_code, 0)
        self.assertIn("normalized=1", stdout.getvalue())
        self.assertIn("note.md", stdout.getvalue())
        self.assertIn("笔记", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
