import sys
from argparse import ArgumentParser, Namespace
from typing import Optional, Sequence

from agent_kb.chunker import chunk_documents
from agent_kb.document_loader import load_markdown_documents
from agent_kb.text_normalizer import normalize_documents


def parse_args(argv: Sequence[str]) -> Namespace:
    parser = ArgumentParser(description="加载、标准化并切分本地 Markdown 文档。")
    parser.add_argument("source_dir", nargs="?", default="knowledge")
    parser.add_argument("--chunk-size", type=int, default=400)
    parser.add_argument("--overlap", type=int, default=40)
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

    print(f"source_dir={args.source_dir}")
    print(f"chunks={len(chunks)}")
    for chunk in chunks:
        print(
            f"- chunk_id={chunk.chunk_id} source_path={chunk.source_path} "
            f"start={chunk.start_char} end={chunk.end_char} chars={len(chunk.text)}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
