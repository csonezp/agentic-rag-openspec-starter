import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from agent_kb.chunker import DocumentChunk
from agent_kb.embeddings import EmbeddedChunk
from agent_kb.vector_store import (
    LocalQdrantVectorStore,
    SearchResult,
    VectorStoreConfig,
    chunk_payload,
    stable_point_id,
)
from scripts.index_knowledge_base import main, parse_args
from scripts.retrieve_top_k import main as retrieve_main
from scripts.retrieve_top_k import parse_args as parse_retrieve_args


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

    def test_search_returns_top_k_results_with_payload(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = LocalQdrantVectorStore(
                VectorStoreConfig(
                    path=tmpdir,
                    collection_name="test_chunks",
                    dimensions=2,
                )
            )
            chunks = [
                EmbeddedChunk(
                    chunk=DocumentChunk("agent.md#0", "agent.md", "Agent", 0, 0, 5, "Agent RAG"),
                    embedding=[1.0, 0.0],
                ),
                EmbeddedChunk(
                    chunk=DocumentChunk("ops.md#0", "ops.md", "Ops", 0, 0, 5, "Deploy"),
                    embedding=[0.0, 1.0],
                ),
            ]
            store.upsert_chunks(chunks)

            results = store.search(query_embedding=[1.0, 0.0], top_k=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0],
            SearchResult(
                score=results[0].score,
                chunk_id="agent.md#0",
                source_path="agent.md",
                title="Agent",
                chunk_index=0,
                start_char=0,
                end_char=5,
                text="Agent RAG",
            ),
        )
        self.assertGreater(results[0].score, 0.99)

    def test_search_rejects_wrong_query_dimensions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = LocalQdrantVectorStore(
                VectorStoreConfig(
                    path=tmpdir,
                    collection_name="test_chunks",
                    dimensions=2,
                )
            )

            with self.assertRaisesRegex(ValueError, "query embedding 维度不匹配"):
                store.search(query_embedding=[1.0, 0.0, 0.0], top_k=1)

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

    def test_retrieve_parse_args_uses_defaults(self):
        args = parse_retrieve_args(["什么是 Agent？"])

        self.assertEqual(args.question, "什么是 Agent？")
        self.assertEqual(args.vector_store_path, "data/qdrant")
        self.assertEqual(args.collection_name, "knowledge_chunks")
        self.assertEqual(args.provider, "fastembed")
        self.assertEqual(args.top_k, 3)

    def test_retrieve_script_prints_top_k_results_with_hashing_provider(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_dir = root / "knowledge"
            vector_store_path = root / "qdrant"
            source_dir.mkdir()
            (source_dir / "agent.md").write_text("# Agent\n\nAgent RAG", encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                main(
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
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = retrieve_main(
                    [
                        "Agent RAG 是什么？",
                        "--vector-store-path",
                        str(vector_store_path),
                        "--collection-name",
                        "test_chunks",
                        "--provider",
                        "hashing",
                        "--dimensions",
                        "8",
                        "--top-k",
                        "1",
                    ]
                )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("question=Agent RAG 是什么？", output)
        self.assertIn("provider=hashing", output)
        self.assertIn("top_k=1", output)
        self.assertIn("chunk_id=agent.md#0", output)


if __name__ == "__main__":
    unittest.main()
