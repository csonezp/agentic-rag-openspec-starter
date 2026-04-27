## Context

DeepSeek 官方 JSON Output 能保证模型返回合法 JSON 字符串，但不等价于完整 schema enforcement。官方文档要求：

- 设置 `response_format` 为 `{"type":"json_object"}`。
- system 或 user prompt 中必须包含 `json` 字样。
- prompt 中需要给出目标 JSON 格式样例。
- 合理设置 `max_tokens`，避免 JSON 被截断。

因此本小节采用“两层约束”：API 层要求合法 JSON，本地代码层校验业务字段。

## Goals / Non-Goals

**Goals:**

- 学习 DeepSeek JSON Output 的请求结构和注意事项。
- 定义一个小 schema：`title`、`summary`、`next_action`。
- 真实调用 DeepSeek，把一段学习文本转为结构化 JSON。
- 本地解析并校验 required fields 和字段类型。
- 通过 dry-run、单元测试和真实调用完成验证。

**Non-Goals:**

- 不实现 OpenAI `json_schema` 形态。
- 不引入第三方 schema 校验库。
- 不实现流式 JSON 拼接和增量解析。
- 不处理复杂嵌套 schema。

## Decisions

### Decision: 使用 DeepSeek JSON Output 而不是 OpenAI json_schema

用户真实 provider 是 DeepSeek。DeepSeek 当前文档明确支持 `json_object`，而不是 OpenAI 新式 `json_schema` strict structured outputs。本小节用 DeepSeek 官方能力，并在学习笔记中记录这种差异。

### Decision: 本地 schema 校验用 dataclass 和标准库

新增 `LearningBrief` dataclass，字段为：

- `title`
- `summary`
- `next_action`

解析时使用 `json.loads`，再检查 required fields、字段类型和空字符串。这样能清楚地区分：

- API 约束：返回合法 JSON。
- 应用约束：JSON 必须符合业务 schema。

### Decision: 新增独立演示脚本

新增 `scripts/structured_output_demo.py`，避免把 `hello_model.py` 变成过多学习点混杂的入口。脚本默认 dry-run，显式 `--real` 时调用 DeepSeek JSON Output。

## Risks / Trade-offs

- [Risk] JSON Output 可能返回合法 JSON 但字段不符合预期。→ 本地 schema 校验失败时抛出明确错误。
- [Risk] 模型输出可能为空或被截断。→ prompt 中给出 JSON 样例，并设置 `max_tokens`。
- [Risk] 结构化输出与 tool calling 容易混淆。→ 本小节只做“模型生成 JSON”，不触发工具调用。
