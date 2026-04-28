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


def parse_args(argv: Sequence[str]) -> Namespace:
    parser = ArgumentParser(description="为本地 Markdown 知识库 chunks 生成 embeddings。")
    parser.add_argument("source_dir", nargs="?", default="knowledge")
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
    if args.provider == "fastembed":
        model = FastEmbedEmbeddingModel(
            model_name=args.model_name,
            dimensions=args.dimensions,
        )
    else:
        model = HashingEmbeddingModel(dimensions=args.dimensions)
    embedded_chunks = embed_chunks(chunks, model)

    print(f"source_dir={args.source_dir}")
    print(f"provider={args.provider}")
    if args.provider == "fastembed":
        print(f"model_name={args.model_name}")
    print(f"chunks={len(chunks)}")
    print(f"embeddings={len(embedded_chunks)}")
    print(f"dimensions={model.dimensions}")
    for embedded in embedded_chunks[:5]:
        preview = ", ".join(f"{value:.3f}" for value in embedded.embedding[:4])
        print(f"- chunk_id={embedded.chunk.chunk_id} preview=[{preview}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
