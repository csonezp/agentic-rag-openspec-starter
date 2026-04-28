import sys
from argparse import ArgumentParser, Namespace
from typing import Optional, Sequence

from agent_kb.embeddings import (
    DEFAULT_FASTEMBED_DIMENSIONS,
    DEFAULT_FASTEMBED_MODEL_NAME,
    FastEmbedEmbeddingModel,
    HashingEmbeddingModel,
)
from agent_kb.vector_store import LocalQdrantVectorStore, VectorStoreConfig


def parse_args(argv: Sequence[str]) -> Namespace:
    parser = ArgumentParser(description="从本地 Qdrant 向量库检索 top-k chunks。")
    parser.add_argument("question")
    parser.add_argument("--vector-store-path", default="data/qdrant")
    parser.add_argument("--collection-name", default="knowledge_chunks")
    parser.add_argument("--provider", choices=["fastembed", "hashing"], default="fastembed")
    parser.add_argument("--model-name", default=DEFAULT_FASTEMBED_MODEL_NAME)
    parser.add_argument("--dimensions", type=int, default=DEFAULT_FASTEMBED_DIMENSIONS)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--preview-chars", type=int, default=160)
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    model = _create_embedding_model(args)
    query_embedding = model.embed(args.question)
    store = LocalQdrantVectorStore(
        VectorStoreConfig(
            path=args.vector_store_path,
            collection_name=args.collection_name,
            dimensions=model.dimensions,
        )
    )
    results = store.search(query_embedding=query_embedding, top_k=args.top_k)

    print(f"question={args.question}")
    print(f"vector_store_path={args.vector_store_path}")
    print(f"collection_name={args.collection_name}")
    print(f"provider={args.provider}")
    if args.provider == "fastembed":
        print(f"model_name={args.model_name}")
    print(f"top_k={args.top_k}")
    print(f"results={len(results)}")
    for index, result in enumerate(results, start=1):
        preview = result.text[: args.preview_chars].replace("\n", " ")
        print("---")
        print(f"rank={index}")
        print(f"score={result.score:.6f}")
        print(f"chunk_id={result.chunk_id}")
        print(f"source_path={result.source_path}")
        print(f"title={result.title}")
        print(f"chunk_index={result.chunk_index}")
        print(f"text_preview={preview}")
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
