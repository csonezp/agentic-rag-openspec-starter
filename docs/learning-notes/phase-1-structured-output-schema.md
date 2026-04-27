# Phase 1 学习笔记：小 schema 结构化输出

日期：2026-04-27

## 学习目标

本小节学习如何让模型输出可被程序稳定解析的数据，而不是只返回自由文本。我们选择一个很小的 schema：`title`、`summary`、`next_action`，用于把一段学习内容整理成结构化学习摘要。

## DeepSeek JSON Output 观察

DeepSeek 官方 JSON Output 不是 OpenAI 新式 `json_schema` strict structured outputs。它的核心约束是：

- 请求体设置 `response_format` 为 `{"type": "json_object"}`。
- system 或 user prompt 中必须包含 `json` 字样。
- prompt 中需要给出希望输出的 JSON 示例。
- 需要设置合理的 `max_tokens`，避免 JSON 中途截断。

这意味着 DeepSeek 可以帮助我们得到“合法 JSON”，但业务 schema 仍然需要本地代码校验。

## 本小节实现

- 新增 `LearningBrief` dataclass，字段为 `title`、`summary`、`next_action`。
- 新增 `build_learning_brief_prompt()`，在 prompt 中明确要求输出 json object，并给出示例。
- 新增 `generate_learning_brief()`，调用支持 JSON Output 的模型客户端并解析结果。
- 扩展 `DeepSeekChatCompletionsModelClient.complete_json()`，向 `/chat/completions` 发送 `response_format={"type":"json_object"}`。
- 新增 `scripts/structured_output_demo.py`，默认 dry-run，`--real` 时调用 DeepSeek。

## 关键认知

- “结构化输出”至少有两层含义：
  - 模型/API 层：尽量返回合法 JSON。
  - 应用层：校验 JSON 是否符合业务字段、类型和非空约束。
- 不能因为 API 返回了合法 JSON，就默认它满足业务 schema。
- 这个能力会成为后续 tool calling、评测打分、拒答分类和路由决策的基础。

## 验证记录

- 单元测试覆盖 DeepSeek JSON Output 请求体、本地 schema 解析、无效字段拒绝和演示脚本。
- 单元测试验证命令：`PYTHONPATH=src:. python3 -m unittest discover -s tests`，结果为 27 个测试通过。
- OpenSpec 验证命令：`/opt/homebrew/bin/openspec validate --all --strict`，结果为 8 项通过。
- 真实 DeepSeek JSON Output 验证使用 `scripts/structured_output_demo.py --real`，返回了包含 `title`、`summary`、`next_action` 的 JSON，并通过本地 schema 校验。

## 后续问题

- 后续是否需要引入 `jsonschema` 或 Pydantic 做复杂 schema 校验。
- 结构化输出失败时是否需要自动重试或让模型自修复。
- 后续 tool calling 小节需要区分“模型输出 JSON”和“模型请求调用工具”。
