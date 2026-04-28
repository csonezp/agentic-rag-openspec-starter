import uuid
from dataclasses import dataclass
from typing import Optional

from agent_kb.chunker import DocumentChunk
from agent_kb.embeddings import EmbeddedChunk


@dataclass(frozen=True)
class VectorStoreConfig:
    path: str = "data/qdrant"
    collection_name: str = "knowledge_chunks"
    dimensions: int = 512


@dataclass(frozen=True)
class UpsertResult:
    collection_name: str
    points_written: int
    total_points: int


@dataclass(frozen=True)
class StoredVector:
    point_id: str
    payload: dict
    vector: list[float]


@dataclass(frozen=True)
class SearchResult:
    score: float
    chunk_id: str
    source_path: str
    title: str
    chunk_index: int
    start_char: int
    end_char: int
    text: str


class LocalQdrantVectorStore:
    def __init__(self, config: VectorStoreConfig) -> None:
        if config.dimensions <= 0:
            raise ValueError("dimensions 必须大于 0")
        self.config = config
        self._client = _create_qdrant_client(config.path)
        self._ensure_collection()

    def upsert_chunks(self, embedded_chunks: list[EmbeddedChunk]) -> UpsertResult:
        if not embedded_chunks:
            return UpsertResult(
                collection_name=self.config.collection_name,
                points_written=0,
                total_points=self.count(),
            )

        from qdrant_client.http import models

        points = []
        for embedded in embedded_chunks:
            if len(embedded.embedding) != self.config.dimensions:
                raise ValueError(
                    "embedding 维度不匹配："
                    f"collection={self.config.dimensions}, embedding={len(embedded.embedding)}"
                )
            points.append(
                models.PointStruct(
                    id=stable_point_id(embedded.chunk.chunk_id),
                    vector=embedded.embedding,
                    payload=chunk_payload(embedded.chunk),
                )
            )

        self._client.upsert(
            collection_name=self.config.collection_name,
            points=points,
            wait=True,
        )
        return UpsertResult(
            collection_name=self.config.collection_name,
            points_written=len(points),
            total_points=self.count(),
        )

    def retrieve_by_chunk_id(self, chunk_id: str) -> Optional[StoredVector]:
        point_id = stable_point_id(chunk_id)
        points = self._client.retrieve(
            collection_name=self.config.collection_name,
            ids=[point_id],
            with_payload=True,
            with_vectors=True,
        )
        if not points:
            return None

        point = points[0]
        vector = point.vector or []
        if isinstance(vector, dict):
            vector = next(iter(vector.values()), [])
        return StoredVector(
            point_id=str(point.id),
            payload=point.payload or {},
            vector=[float(value) for value in vector],
        )

    def search(self, query_embedding: list[float], top_k: int = 3) -> list[SearchResult]:
        if len(query_embedding) != self.config.dimensions:
            raise ValueError(
                "query embedding 维度不匹配："
                f"collection={self.config.dimensions}, query={len(query_embedding)}"
            )
        if top_k <= 0:
            raise ValueError("top_k 必须大于 0")

        response = self._client.query_points(
            collection_name=self.config.collection_name,
            query=query_embedding,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )
        return [_search_result_from_point(point) for point in response.points]

    def count(self) -> int:
        result = self._client.count(
            collection_name=self.config.collection_name,
            exact=True,
        )
        return int(result.count)

    def _ensure_collection(self) -> None:
        from qdrant_client.http import models

        if self._client.collection_exists(self.config.collection_name):
            return

        self._client.create_collection(
            collection_name=self.config.collection_name,
            vectors_config=models.VectorParams(
                size=self.config.dimensions,
                distance=models.Distance.COSINE,
            ),
        )


def chunk_payload(chunk: DocumentChunk) -> dict:
    return {
        "chunk_id": chunk.chunk_id,
        "source_path": chunk.source_path,
        "title": chunk.title,
        "chunk_index": chunk.chunk_index,
        "start_char": chunk.start_char,
        "end_char": chunk.end_char,
        "text": chunk.text,
    }


def stable_point_id(chunk_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id))


def _search_result_from_point(point) -> SearchResult:
    payload = point.payload or {}
    return SearchResult(
        score=float(point.score),
        chunk_id=str(payload.get("chunk_id", "")),
        source_path=str(payload.get("source_path", "")),
        title=str(payload.get("title", "")),
        chunk_index=int(payload.get("chunk_index", 0)),
        start_char=int(payload.get("start_char", 0)),
        end_char=int(payload.get("end_char", 0)),
        text=str(payload.get("text", "")),
    )


def _create_qdrant_client(path: str):
    try:
        from qdrant_client import QdrantClient
    except ImportError as error:
        raise RuntimeError(
            "未安装 qdrant-client。请先运行 `pip install -e .` 或 `pip install qdrant-client`。"
        ) from error

    return QdrantClient(path=path)
