import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from agent_kb.chunker import DocumentChunk
from agent_kb.embeddings import (
    EmbeddedChunk,
    HashingEmbeddingModel,
    embed_chunk,
    embed_chunks,
)
from scripts.generate_embeddings import main, parse_args


class EmbeddingsTest(unittest.TestCase):
    def test_hashing_embedding_is_deterministic(self):
        model = HashingEmbeddingModel(dimensions=8)

        first = model.embed("Agent RAG Agent")
        second = model.embed("Agent RAG Agent")

        self.assertEqual(first, second)
        self.assertEqual(len(first), 8)
        self.assertAlmostEqual(sum(value * value for value in first), 1.0)

    def test_hashing_embedding_changes_for_different_text(self):
        model = HashingEmbeddingModel(dimensions=8)

        self.assertNotEqual(model.embed("Agent"), model.embed("RAG"))

    def test_embed_chunk_preserves_chunk_metadata(self):
        chunk = DocumentChunk(
            chunk_id="doc.md#0",
            source_path="doc.md",
            title="Doc",
            chunk_index=0,
            start_char=0,
            end_char=5,
            text="Agent",
        )
        model = HashingEmbeddingModel(dimensions=8)

        embedded = embed_chunk(chunk, model)

        self.assertEqual(
            embedded,
            EmbeddedChunk(
                chunk=chunk,
                embedding=model.embed("Agent"),
            ),
        )

    def test_embed_chunks_preserves_order(self):
        chunks = [
            DocumentChunk("a.md#0", "a.md", "A", 0, 0, 1, "A"),
            DocumentChunk("b.md#0", "b.md", "B", 0, 0, 1, "B"),
        ]
        model = HashingEmbeddingModel(dimensions=4)

        embedded = embed_chunks(chunks, model)

        self.assertEqual([item.chunk.chunk_id for item in embedded], ["a.md#0", "b.md#0"])
        self.assertEqual([len(item.embedding) for item in embedded], [4, 4])

    def test_parse_args_uses_defaults(self):
        args = parse_args([])

        self.assertEqual(args.source_dir, "knowledge")
        self.assertEqual(args.dimensions, 64)

    def test_demo_script_prints_embedding_summary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "note.md").write_text("# 笔记\n\nAgent RAG", encoding="utf-8")
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        str(root),
                        "--chunk-size",
                        "20",
                        "--overlap",
                        "0",
                        "--dimensions",
                        "8",
                    ]
                )

        self.assertEqual(exit_code, 0)
        self.assertIn("chunks=1", stdout.getvalue())
        self.assertIn("embeddings=1", stdout.getvalue())
        self.assertIn("dimensions=8", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
