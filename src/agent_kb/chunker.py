from dataclasses import dataclass

from agent_kb.text_normalizer import NormalizedDocument


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    source_path: str
    title: str
    chunk_index: int
    start_char: int
    end_char: int
    text: str


def chunk_document(
    document: NormalizedDocument,
    *,
    chunk_size: int,
    overlap: int,
) -> list[DocumentChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size 必须大于 0")
    if overlap < 0:
        raise ValueError("overlap 不能小于 0")
    if overlap >= chunk_size:
        raise ValueError("overlap 必须小于 chunk_size")

    chunks: list[DocumentChunk] = []
    start = 0
    chunk_index = 0
    step = chunk_size - overlap

    while start < len(document.text):
        end = min(start + chunk_size, len(document.text))
        chunks.append(
            DocumentChunk(
                chunk_id=f"{document.source_path}#{chunk_index}",
                source_path=document.source_path,
                title=document.title,
                chunk_index=chunk_index,
                start_char=start,
                end_char=end,
                text=document.text[start:end],
            )
        )
        if end == len(document.text):
            break
        start += step
        chunk_index += 1

    return chunks


def chunk_documents(
    documents: list[NormalizedDocument],
    *,
    chunk_size: int,
    overlap: int,
) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for document in documents:
        chunks.extend(
            chunk_document(document, chunk_size=chunk_size, overlap=overlap)
        )
    return chunks
