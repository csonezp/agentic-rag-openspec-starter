import json
from dataclasses import asdict, dataclass
from typing import Protocol


class StructuredOutputClient(Protocol):
    def complete_json(self, prompt: str, max_tokens: int = 512) -> str:
        """返回符合 JSON Output 模式的模型响应文本。"""


@dataclass(frozen=True)
class LearningBrief:
    title: str
    summary: str
    next_action: str

    @classmethod
    def from_json_text(cls, text: str) -> "LearningBrief":
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"结构化输出不是合法 JSON：{exc.msg}") from exc

        if not isinstance(payload, dict):
            raise ValueError("结构化输出必须是 JSON object")

        values = {}
        for field_name in ("title", "summary", "next_action"):
            value = payload.get(field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"结构化输出字段无效：{field_name}")
            values[field_name] = value.strip()

        return cls(**values)

    def to_json_text(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)


class DryRunStructuredOutputClient:
    def complete_json(self, prompt: str, max_tokens: int = 512) -> str:
        brief = LearningBrief(
            title="结构化输出 dry-run",
            summary=f"已收到待结构化文本：{prompt[:40]}",
            next_action="配置 DEEPSEEK_API_KEY 后使用 --real 验证 DeepSeek JSON Output。",
        )
        return brief.to_json_text()


def build_learning_brief_prompt(text: str) -> str:
    return f"""请把下面的学习内容整理成一个 json object。

要求：
- 只输出 json，不要输出 Markdown。
- 字段必须包含 title、summary、next_action。
- 每个字段都必须是非空字符串。

示例 json：
{{
  "title": "学习主题",
  "summary": "一句话总结学到了什么",
  "next_action": "下一步最具体的行动"
}}

待整理文本：
{text}
"""


def generate_learning_brief(
    client: StructuredOutputClient,
    text: str,
) -> LearningBrief:
    prompt = build_learning_brief_prompt(text)
    response = client.complete_json(prompt, max_tokens=512)
    return LearningBrief.from_json_text(response)
