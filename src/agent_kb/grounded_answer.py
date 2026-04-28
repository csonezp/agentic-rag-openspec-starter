from dataclasses import dataclass
from typing import Optional

from agent_kb.hello_agent import ModelClient
from agent_kb.vector_store import SearchResult


@dataclass(frozen=True)
class EvidenceCheckResult:
    is_sufficient: bool
    reason: str
    best_score: Optional[float]
    contexts_count: int


@dataclass(frozen=True)
class SourceCitation:
    chunk_id: str
    source_path: str
    title: str
    chunk_index: int
    score: float


@dataclass(frozen=True)
class GroundedAnswerResult:
    question: str
    answer: str
    contexts: list[SearchResult]
    citations: list[SourceCitation]
    refused: bool = False
    refusal_reason: Optional[str] = None


class GroundedAnswerer:
    def __init__(self, model_client: ModelClient) -> None:
        self._model_client = model_client

    def answer(
        self,
        question: str,
        contexts: list[SearchResult],
    ) -> GroundedAnswerResult:
        prompt = build_grounded_prompt(question, contexts)
        return GroundedAnswerResult(
            question=question,
            answer=self._model_client.complete(prompt),
            contexts=contexts,
            citations=citations_from_contexts(contexts),
        )


def citations_from_contexts(contexts: list[SearchResult]) -> list[SourceCitation]:
    return [
        SourceCitation(
            chunk_id=context.chunk_id,
            source_path=context.source_path,
            title=context.title,
            chunk_index=context.chunk_index,
            score=context.score,
        )
        for context in contexts
    ]


def evaluate_evidence(
    contexts: list[SearchResult],
    min_score: float = 0.45,
) -> EvidenceCheckResult:
    if not contexts:
        return EvidenceCheckResult(
            is_sufficient=False,
            reason="no_contexts",
            best_score=None,
            contexts_count=0,
        )

    best_score = max(context.score for context in contexts)
    if best_score < min_score:
        return EvidenceCheckResult(
            is_sufficient=False,
            reason="best_score_below_threshold",
            best_score=best_score,
            contexts_count=len(contexts),
        )

    return EvidenceCheckResult(
        is_sufficient=True,
        reason="sufficient",
        best_score=best_score,
        contexts_count=len(contexts),
    )


def build_grounded_prompt(question: str, contexts: list[SearchResult]) -> str:
    if not question.strip():
        raise ValueError("问题不能为空")

    context_blocks = []
    for index, context in enumerate(contexts, start=1):
        context_blocks.append(
            "\n".join(
                [
                    f"### 上下文 {index}",
                    f"[{context.chunk_id}] {context.title} / {context.source_path}",
                    f"chunk_index={context.chunk_index}",
                    f"score={context.score:.6f}",
                    context.text,
                ]
            )
        )

    context_text = "\n\n".join(context_blocks) if context_blocks else "无检索上下文。"
    return "\n\n".join(
        [
            "你是一个基于本地知识库回答问题的助手。",
            "只能基于给定上下文回答；不要编造上下文之外的事实。",
            "回答中尽量使用 [chunk_id] 标记依据，例如 [observability.md#0]。",
            "如果上下文没有提供足够信息，请说明当前上下文没有提供足够信息。",
            "## 检索上下文",
            context_text,
            "## 用户问题",
            question,
            "## 回答",
        ]
    )
