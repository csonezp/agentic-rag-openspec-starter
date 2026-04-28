from dataclasses import dataclass

from agent_kb.hello_agent import ModelClient
from agent_kb.vector_store import SearchResult


@dataclass(frozen=True)
class GroundedAnswerResult:
    question: str
    answer: str
    contexts: list[SearchResult]


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
            "如果上下文没有提供足够信息，请说明当前上下文没有提供足够信息。",
            "本小节暂不要求输出正式来源引用，后续小节会单独处理引用格式。",
            "## 检索上下文",
            context_text,
            "## 用户问题",
            question,
            "## 回答",
        ]
    )
