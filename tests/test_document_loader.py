import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from agent_kb.document_loader import (
    KnowledgeDocument,
    extract_markdown_title,
    load_markdown_documents,
)
from scripts.load_documents import main, parse_args


class DocumentLoaderTest(unittest.TestCase):
    def test_extracts_first_level_one_markdown_title(self):
        title = extract_markdown_title("intro\n# 主标题\n## 二级标题\n# 另一个标题\n")

        self.assertEqual(title, "主标题")

    def test_loads_markdown_documents_with_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "b.md").write_text("# B 标题\nB 内容", encoding="utf-8")
            (root / "nested").mkdir()
            (root / "nested" / "a.md").write_text("无标题内容", encoding="utf-8")
            (root / "ignored.txt").write_text("# 忽略", encoding="utf-8")

            documents = load_markdown_documents(root)

        self.assertEqual(
            documents,
            [
                KnowledgeDocument(
                    source_path="b.md",
                    title="B 标题",
                    content="# B 标题\nB 内容",
                ),
                KnowledgeDocument(
                    source_path="nested/a.md",
                    title="a",
                    content="无标题内容",
                ),
            ],
        )

    def test_returns_empty_list_when_no_markdown_files_exist(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            documents = load_markdown_documents(Path(tmpdir))

        self.assertEqual(documents, [])

    def test_parse_args_uses_knowledge_by_default(self):
        args = parse_args([])

        self.assertEqual(args.source_dir, "knowledge")

    def test_demo_script_prints_loaded_documents(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "note.md").write_text("# 笔记\n内容", encoding="utf-8")
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main([str(root)])

        self.assertEqual(exit_code, 0)
        self.assertIn("loaded=1", stdout.getvalue())
        self.assertIn("note.md", stdout.getvalue())
        self.assertIn("笔记", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
