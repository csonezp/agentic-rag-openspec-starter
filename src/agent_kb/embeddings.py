import hashlib
import math
import re
from dataclasses import dataclass
from typing import Protocol

from agent_kb.chunker import DocumentChunk


class EmbeddingModel(Protocol):
    dimensions: int

    def embed(self, text: str) -> list[float]:
        """把文本转换为固定维度向量。"""


@dataclass(frozen=True)
class EmbeddedChunk:
    chunk: DocumentChunk
    embedding: list[float]


class HashingEmbeddingModel:
    def __init__(self, dimensions: int = 64) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions 必须大于 0")
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in _tokenize(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


def embed_chunk(chunk: DocumentChunk, model: EmbeddingModel) -> EmbeddedChunk:
    return EmbeddedChunk(
        chunk=chunk,
        embedding=model.embed(chunk.text),
    )


def embed_chunks(
    chunks: list[DocumentChunk],
    model: EmbeddingModel,
) -> list[EmbeddedChunk]:
    return [embed_chunk(chunk, model) for chunk in chunks]


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[\w\u4e00-\u9fff]+", text.lower())
