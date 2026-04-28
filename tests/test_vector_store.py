import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from agent_kb.chunker import DocumentChunk
from agent_kb.embeddings import EmbeddedChunk
from agent_kb.vector_store import (
    LocalQdrantVectorStore,
    VectorStoreConfig,
    chunk_payload,
    stable_point_id,
)
from scripts.index_knowledge_base import main, parse_args


class VectorStoreTest(unittest.TestCase):
    def test_chunk_payload_preserves_text_and_metadata(self):
        chunk = DocumentChunk(
            chunk_id="doc.md#0",
            source_path="doc.md",
            title="Doc",
            chunk_index=0,
            start_char=3,
            end_char=15,
            text="Agent RAG",
        )

        payload = chunk_payload(chunk)

        self.assertEqual(
            payload,
            {
                "chunk_id": "doc.md#0",
                "source_path": "doc.md",
                "title": "Doc",
                "chunk_index": 0,
                "start_char": 3,
                "end_char": 15,
                "text": "Agent RAG",
            },
        )

    def test_stable_point_id_is_repeatable_uuid(self):
        first = stable_point_id("doc.md#0")
        second = stable_point_id("doc.md#0")

        self.assertEqual(first, second)
        self.assertRegex(first, r"^[0-9a-f-]{36}$")

    def test_upsert_embedded_chunks_writes_payload_and_vector(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = LocalQdrantVectorStore(
                VectorStoreConfig(
                    path=tmpdir,
                    collection_name="test_chunks",
                    dimensions=3,
                )
            )
            chunk = DocumentChunk("doc.md#0", "doc.md", "Doc", 0, 0, 5, "Agent")
            embedded = EmbeddedChunk(chunk=chunk, embedding=[0.1, 0.2, 0.3])

            result = store.upsert_chunks([embedded])
            stored = store.retrieve_by_chunk_id("doc.md#0")

        self.assertEqual(result.points_written, 1)
        self.assertIsNotNone(stored)
        self.assertEqual(stored.payload["chunk_id"], "doc.md#0")
        self.assertEqual(stored.payload["text"], "Agent")
        self.assertEqual(len(stored.vector), 3)
        self.assertAlmostEqual(stored.vector[0], 0.267261, places=5)

    def test_upsert_is_idempotent_for_same_chunk_id(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = LocalQdrantVectorStore(
                VectorStoreConfig(
                    path=tmpdir,
                    collection_name="test_chunks",
                    dimensions=2,
                )
            )
            chunk = DocumentChunk("doc.md#0", "doc.md", "Doc", 0, 0, 5, "Agent")
            embedded = EmbeddedChunk(chunk=chunk, embedding=[0.1, 0.2])

            store.upsert_chunks([embedded])
            store.upsert_chunks([embedded])

            count = store.count()

        self.assertEqual(count, 1)

    def test_parse_args_uses_local_qdrant_defaults(self):
        args = parse_args([])

        self.assertEqual(args.source_dir, "knowledge")
        self.assertEqual(args.vector_store_path, "data/qdrant")
        self.assertEqual(args.collection_name, "knowledge_chunks")
        self.assertEqual(args.provider, "fastembed")

    def test_index_script_writes_chunks_with_hashing_provider(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_dir = root / "knowledge"
            vector_store_path = root / "qdrant"
            source_dir.mkdir()
            (source_dir / "note.md").write_text("# 笔记\n\nAgent RAG", encoding="utf-8")
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        str(source_dir),
                        "--vector-store-path",
                        str(vector_store_path),
                        "--collection-name",
                        "test_chunks",
                        "--provider",
                        "hashing",
                        "--dimensions",
                        "8",
                        "--chunk-size",
                        "20",
                        "--overlap",
                        "0",
                    ]
                )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("collection_name=test_chunks", output)
        self.assertIn("provider=hashing", output)
        self.assertIn("chunks=1", output)
        self.assertIn("points_written=1", output)


if __name__ == "__main__":
    unittest.main()
