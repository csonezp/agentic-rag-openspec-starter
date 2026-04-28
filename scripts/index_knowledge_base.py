import sys
from argparse import ArgumentParser, Namespace
from typing import Optional, Sequence

from agent_kb.chunker import chunk_documents
from agent_kb.document_loader import load_markdown_documents
from agent_kb.embeddings import (
    DEFAULT_FASTEMBED_DIMENSIONS,
    DEFAULT_FASTEMBED_MODEL_NAME,
    FastEmbedEmbeddingModel,
    HashingEmbeddingModel,
    embed_chunks,
)
from agent_kb.text_normalizer import normalize_documents
from agent_kb.vector_store import LocalQdrantVectorStore, VectorStoreConfig


def parse_args(argv: Sequence[str]) -> Namespace:
    parser = ArgumentParser(description="把本地 Markdown 知识库索引到 Qdrant 本地向量库。")
    parser.add_argument("source_dir", nargs="?", default="knowledge")
    parser.add_argument("--vector-store-path", default="data/qdrant")
    parser.add_argument("--collection-name", default="knowledge_chunks")
    parser.add_argument("--chunk-size", type=int, default=400)
    parser.add_argument("--overlap", type=int, default=40)
    parser.add_argument("--provider", choices=["fastembed", "hashing"], default="fastembed")
    parser.add_argument("--model-name", default=DEFAULT_FASTEMBED_MODEL_NAME)
    parser.add_argument("--dimensions", type=int, default=DEFAULT_FASTEMBED_DIMENSIONS)
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    documents = load_markdown_documents(args.source_dir)
    normalized_documents = normalize_documents(documents)
    chunks = chunk_documents(
        normalized_documents,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
    )
    model = _create_embedding_model(args)
    embedded_chunks = embed_chunks(chunks, model)

    store = LocalQdrantVectorStore(
        VectorStoreConfig(
            path=args.vector_store_path,
            collection_name=args.collection_name,
            dimensions=model.dimensions,
        )
    )
    result = store.upsert_chunks(embedded_chunks)

    print(f"source_dir={args.source_dir}")
    print(f"vector_store_path={args.vector_store_path}")
    print(f"collection_name={result.collection_name}")
    print(f"provider={args.provider}")
    if args.provider == "fastembed":
        print(f"model_name={args.model_name}")
    print(f"chunks={len(chunks)}")
    print(f"points_written={result.points_written}")
    print(f"total_points={result.total_points}")
    print(f"dimensions={model.dimensions}")
    return 0


def _create_embedding_model(args: Namespace):
    if args.provider == "fastembed":
        return FastEmbedEmbeddingModel(
            model_name=args.model_name,
            dimensions=args.dimensions,
        )
    return HashingEmbeddingModel(dimensions=args.dimensions)


if __name__ == "__main__":
    sys.exit(main())
