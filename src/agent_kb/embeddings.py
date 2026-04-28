import hashlib
import math
import re
from dataclasses import dataclass
from typing import Any, Optional, Protocol

from agent_kb.chunker import DocumentChunk

DEFAULT_FASTEMBED_MODEL_NAME = "BAAI/bge-small-zh-v1.5"
DEFAULT_FASTEMBED_DIMENSIONS = 512


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


class FastEmbedEmbeddingModel:
    def __init__(
        self,
        model_name: str = DEFAULT_FASTEMBED_MODEL_NAME,
        dimensions: int = DEFAULT_FASTEMBED_DIMENSIONS,
        embedding_client: Optional[Any] = None,
    ) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions 必须大于 0")
        self.model_name = model_name
        self.dimensions = dimensions
        self._client = embedding_client or _create_fastembed_client(model_name)

    def embed(self, text: str) -> list[float]:
        vectors = list(self._client.embed([text]))
        if not vectors:
            raise RuntimeError("fastembed 没有返回 embedding")

        embedding = _vector_to_float_list(vectors[0])
        if len(embedding) != self.dimensions:
            raise ValueError(
                f"embedding 维度不匹配：期望 {self.dimensions}，实际 {len(embedding)}"
            )
        return embedding


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


def _create_fastembed_client(model_name: str) -> Any:
    try:
        from fastembed import TextEmbedding
    except ImportError as error:
        raise RuntimeError(
            "未安装 fastembed。请先运行 `pip install -e .` 或 `pip install fastembed`。"
        ) from error

    return TextEmbedding(model_name=model_name)


def _vector_to_float_list(vector: Any) -> list[float]:
    if hasattr(vector, "tolist"):
        vector = vector.tolist()
    return [float(value) for value in vector]
