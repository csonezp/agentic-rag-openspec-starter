from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union


@dataclass(frozen=True)
class KnowledgeDocument:
    source_path: str
    title: str
    content: str


def extract_markdown_title(content: str) -> Optional[str]:
    for line in content.splitlines():
        if line.startswith("# ") and line[2:].strip():
            return line[2:].strip()
    return None


def load_markdown_documents(source_dir: Union[Path, str]) -> list[KnowledgeDocument]:
    root = Path(source_dir)
    if not root.exists():
        return []

    documents = []
    for path in sorted(root.rglob("*.md")):
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        source_path = path.relative_to(root).as_posix()
        title = extract_markdown_title(content) or path.stem
        documents.append(
            KnowledgeDocument(
                source_path=source_path,
                title=title,
                content=content,
            )
        )
    return documents
