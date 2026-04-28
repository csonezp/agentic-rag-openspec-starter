import sys
from argparse import ArgumentParser, Namespace
from typing import Optional, Sequence

from agent_kb.document_loader import load_markdown_documents
from agent_kb.text_normalizer import normalize_documents


def parse_args(argv: Sequence[str]) -> Namespace:
    parser = ArgumentParser(description="加载并标准化本地 Markdown 知识库文档。")
    parser.add_argument("source_dir", nargs="?", default="knowledge")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    documents = load_markdown_documents(args.source_dir)
    normalized_documents = normalize_documents(documents)

    print(f"source_dir={args.source_dir}")
    print(f"normalized={len(normalized_documents)}")
    for document in normalized_documents:
        print(
            f"- source_path={document.source_path} "
            f"title={document.title} chars={len(document.text)}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
