## Context

DeepSeek Tool Calls 与 OpenAI Chat Completions 风格兼容。一次完整工具调用通常包含两个模型回合：

1. 用户提问并提供 `tools`。
2. 模型返回 `tool_calls`，说明要调用哪个函数以及参数。
3. 本地代码执行函数，把结果作为 `role=tool` 消息回传。
4. 模型基于工具结果生成最终自然语言回答。

关键点是：模型本身不会执行函数，函数执行和参数校验必须由本地代码负责。

## Goals / Non-Goals

**Goals:**

- 定义一个只读本地函数 `get_phase1_progress`。
- 向 DeepSeek 请求中传入 tool schema。
- 解析模型返回的 `tool_calls`。
- 执行 allowlist 中的本地函数，并把结果回传模型。
- 完成 dry-run、单元测试和一次真实 DeepSeek Tool Calls 验证。

**Non-Goals:**

- 不实现写操作工具。
- 不做 MCP 集成。
- 不实现多轮复杂 planner。
- 不启用 DeepSeek strict mode beta。

## Decisions

### Decision: 本地函数只读且无外部依赖

本小节使用 `get_phase1_progress`，返回当前 Phase 1 已完成和下一步学习项。它不访问网络、不写文件、不依赖用户输入中的路径，便于专注学习 tool calling 流程。

### Decision: 工具调用 runner 与 DeepSeek 客户端分离

DeepSeek 客户端只负责 HTTP 请求和响应解析；tool runner 负责 allowlist、参数解析、函数执行和二次模型调用。这样后续迁移到 MCP 或增加更多工具时，边界更清楚。

### Decision: 工具参数必须本地校验

即使 tool schema 描述了参数，模型生成的 arguments 仍然视为不可信。当前工具参数为空对象，runner 会拒绝未知工具和非法 JSON arguments。

## Risks / Trade-offs

- [Risk] 模型可能不调用工具，直接回答。→ prompt 明确要求必须调用工具；测试覆盖无 tool call 时的错误。
- [Risk] 模型生成非法 arguments。→ 本地 JSON 解析失败时抛出明确错误。
- [Risk] 用户误解 tool calling 为模型自动执行函数。→ 学习笔记明确记录：模型只提出调用请求，本地代码负责执行。
