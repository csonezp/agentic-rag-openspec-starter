import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Optional, Sequence

from agent_kb.chunker import chunk_document
from agent_kb.document_loader import KnowledgeDocument, load_markdown_documents
from agent_kb.text_normalizer import normalize_document


def parse_args(argv: Sequence[str]) -> Namespace:
    parser = ArgumentParser(description="加载、标准化并切分单个 Markdown 文档。")
    parser.add_argument("source_dir", nargs="?", default="knowledge")
    parser.add_argument("source_path")
    parser.add_argument("--chunk-size", type=int, default=400)
    parser.add_argument("--overlap", type=int, default=40)
    return parser.parse_args(argv)


def _load_one_markdown_document(source_dir: str, source_path: str) -> KnowledgeDocument:
    documents = load_markdown_documents(source_dir)
    for document in documents:
        if document.source_path == source_path:
            return document
    raise FileNotFoundError(f"未找到文档：{source_path}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    try:
        document = _load_one_markdown_document(args.source_dir, args.source_path)
        normalized = normalize_document(document)
        chunks = chunk_document(
            normalized,
            chunk_size=args.chunk_size,
            overlap=args.overlap,
        )
    except (FileNotFoundError, ValueError) as e:
        print(str(e), file=sys.stderr)
        return 2

    print(f"source_dir={args.source_dir}")
    print(f"source_path={document.source_path}")
    print(f"title={document.title}")

    print("--- RAW MARKDOWN ---")
    print(document.content)

    print(f"--- NORMALIZED TEXT (chars={len(normalized.text)}) ---")
    print(normalized.text)

    print(f"--- CHUNKS (n={len(chunks)}) ---")
    for chunk in chunks:
        print(
            f"--- CHUNK #{chunk.chunk_index} {chunk.chunk_id} "
            f"start={chunk.start_char} end={chunk.end_char} chars={len(chunk.text)} ---"
        )
        print(chunk.text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
