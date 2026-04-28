import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from agent_kb.text_normalizer import NormalizedDocument

from agent_kb.chunker import DocumentChunk, chunk_document, chunk_documents
from scripts.chunk_documents import main, parse_args


class ChunkerTest(unittest.TestCase):
    def test_chunk_document_preserves_metadata_and_ranges(self):
        document = NormalizedDocument(
            source_path="guide/intro.md",
            title="介绍",
            text="abcdefghij",
        )

        chunks = chunk_document(document, chunk_size=4, overlap=1)

        self.assertEqual(
            chunks,
            [
                DocumentChunk(
                    chunk_id="guide/intro.md#0",
                    source_path="guide/intro.md",
                    title="介绍",
                    chunk_index=0,
                    start_char=0,
                    end_char=4,
                    text="abcd",
                ),
                DocumentChunk(
                    chunk_id="guide/intro.md#1",
                    source_path="guide/intro.md",
                    title="介绍",
                    chunk_index=1,
                    start_char=3,
                    end_char=7,
                    text="defg",
                ),
                DocumentChunk(
                    chunk_id="guide/intro.md#2",
                    source_path="guide/intro.md",
                    title="介绍",
                    chunk_index=2,
                    start_char=6,
                    end_char=10,
                    text="ghij",
                ),
            ],
        )

    def test_chunk_document_rejects_invalid_overlap(self):
        document = NormalizedDocument(
            source_path="a.md",
            title="A",
            text="abcdef",
        )

        with self.assertRaisesRegex(ValueError, "overlap 必须小于 chunk_size"):
            chunk_document(document, chunk_size=4, overlap=4)

    def test_chunk_documents_preserves_document_order(self):
        documents = [
            NormalizedDocument("a.md", "A", "abcdef"),
            NormalizedDocument("b.md", "B", "uvwxyz"),
        ]

        chunks = chunk_documents(documents, chunk_size=4, overlap=0)

        self.assertEqual(
            [chunk.chunk_id for chunk in chunks],
            ["a.md#0", "a.md#1", "b.md#0", "b.md#1"],
        )

    def test_chunk_document_returns_empty_when_text_is_empty(self):
        document = NormalizedDocument("empty.md", "Empty", "")

        chunks = chunk_document(document, chunk_size=4, overlap=1)

        self.assertEqual(chunks, [])


class ChunkerScriptTest(unittest.TestCase):
    def test_parse_args_uses_defaults(self):
        args = parse_args([])

        self.assertEqual(args.source_dir, "knowledge")
        self.assertEqual(args.chunk_size, 400)
        self.assertEqual(args.overlap, 40)

    def test_demo_script_prints_chunk_summary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "note.md").write_text("abcdefghi", encoding="utf-8")
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main([str(root), "--chunk-size", "4", "--overlap", "1"])

        self.assertEqual(exit_code, 0)
        self.assertIn("chunks=3", stdout.getvalue())
        self.assertIn("chunk_id=note.md#0", stdout.getvalue())
        self.assertIn("start=0", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
