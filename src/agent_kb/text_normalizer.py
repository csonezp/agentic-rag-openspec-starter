import re
from dataclasses import dataclass

from agent_kb.document_loader import KnowledgeDocument


@dataclass(frozen=True)
class NormalizedDocument:
    source_path: str
    title: str
    text: str


def normalize_markdown_text(markdown: str) -> str:
    lines = []
    in_code_block = False

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        if not in_code_block:
            line = re.sub(r"^\s{0,3}#{1,6}\s+", "", line)
            line = re.sub(r"^\s*[-*]\s+", "", line)
            line = re.sub(r"^\s*\d+\.\s+", "", line)
            line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)

        line = re.sub(r"[ \t]+", " ", line).strip()
        lines.append(line)

    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_document(document: KnowledgeDocument) -> NormalizedDocument:
    return NormalizedDocument(
        source_path=document.source_path,
        title=document.title,
        text=normalize_markdown_text(document.content),
    )


def normalize_documents(
    documents: list[KnowledgeDocument],
) -> list[NormalizedDocument]:
    return [normalize_document(document) for document in documents]
