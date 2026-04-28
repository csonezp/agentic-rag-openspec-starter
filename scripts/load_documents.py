import sys
from argparse import ArgumentParser, Namespace
from typing import Optional, Sequence

from agent_kb.document_loader import load_markdown_documents


def parse_args(argv: Sequence[str]) -> Namespace:
    parser = ArgumentParser(description="加载本地 Markdown 知识库文档。")
    parser.add_argument("source_dir", nargs="?", default="knowledge")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    documents = load_markdown_documents(args.source_dir)

    print(f"source_dir={args.source_dir}")
    print(f"loaded={len(documents)}")
    for document in documents:
        print(
            f"- source_path={document.source_path} "
            f"title={document.title} chars={len(document.content)}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
