# Phase 1 学习笔记：记录延迟、token 使用量、模型名和错误

日期：2026-04-27

## 本节学到什么

- 当前观测能力聚焦 DeepSeek 主链，覆盖非流式调用、流式调用和 tool calling 三条路径。
- 非流式和流式调用的观测结果统一使用 `CallObservation` 表示，tool calling 使用 `ToolCallObservation` 表示。
- CLI 不把观测字段混进模型正文，而是在正文后输出固定的 `observation:` 摘要块，便于人工查看和后续脚本解析。

## 字段来源

### DeepSeek 非流式调用

- `provider`：固定写为 `deepseek`。
- `model`：优先读取 DeepSeek 响应体中的 `model`，缺失时回退到 `DEEPSEEK_MODEL` 配置值。
- `latency_ms`：在 `complete_with_observation()` 中用本地 `time.monotonic()` 包裹整次 HTTP 请求与响应解析过程后计算。
- `input_tokens`：读取响应 `usage.prompt_tokens`。
- `output_tokens`：读取响应 `usage.completion_tokens`。
- `total_tokens`：读取响应 `usage.total_tokens`。
- `error_type` / `error_message`：成功时为空；失败时按异常来源记录，例如 `http_error`、`url_error`、`invalid_json`、`api_error`。

### DeepSeek 流式调用

- `provider`：固定写为 `deepseek`。
- `model`：优先读取 SSE 事件里的 `model`，缺失时回退到 `DEEPSEEK_MODEL`。
- `latency_ms`：在 `stream_with_observation()` 中从发起请求开始计时，到消费完流并生成最终 observation 时结束。
- `input_tokens` / `output_tokens` / `total_tokens`：优先读取流式事件中最后一次出现的 `usage`。
- `error_type` / `error_message`：在 HTTP 错误、网络错误、非法 JSON、畸形 SSE、事件体 `payload.error` 等场景下记录。

### Tool Calling 调用

- `tool_triggered`：首轮模型回复是否包含 `tool_calls`。
- `tool_names`：从 `tool_calls[].function.name` 提取，保留模型实际请求的工具名列表。
- `success`：只有工具解析、本地 handler 执行、第二次模型调用和最终 `content` 都成功时为 `true`。
- `error_type` / `error_message`：失败时保留 Python 异常类型和消息，例如未知工具、参数非法、handler 异常、第二次模型调用失败、最终回答为空。

## 统计口径

- 延迟是“本地可见时延”，不是服务端处理时延；它包含 Python 侧发起请求、等待响应、解析 JSON 或 SSE 事件的耗时。
- 非流式 token 统计完全以 provider 返回的 `usage` 为准，本地不做二次估算。
- 流式 token 统计也只认 provider 事件里的 `usage`；若 provider 没有返回，CLI 会输出 `unknown`，而不是猜测值。
- tool calling 观测只统计当前最小闭环，不聚合两次模型调用的 token，也不记录单个工具执行耗时。
- 错误口径强调“保留来源语义”，不把所有失败都抹平成同一种错误。

## 限制

- 当前没有接入 OpenTelemetry、LangSmith 或持久化日志，观测结果只在本次 CLI 运行时打印。
- tool calling 观测暂不包含模型名、token 使用量和端到端延迟，只覆盖是否触发工具、工具名和最终成功/失败。
- 流式场景是否能拿到 `usage` 依赖 DeepSeek 实际返回；代码允许为空并以 `unknown` 展示。
- `error_message` 直接暴露底层错误文本，适合学习和调试，但如果后续进入生产化阶段需要再评估脱敏策略。

## 自动化验证结果

- `PYTHONPATH=src python3 -m unittest discover -s tests`
  - 结果：通过，`Ran 69 tests in 0.009s`，`OK`。
- `openspec validate --all --strict`
  - 结果：通过，`10 passed, 0 failed (10 items)`。

## 本地真实验证结果

- 已运行 `MODEL_PROVIDER=deepseek PYTHONPATH=src python3 scripts/hello_model.py --real "用一句话介绍这个项目"`。
  - 结果：成功，退出码 `0`。
  - 观测摘要示例：`model=deepseek-v4-flash`、`latency_ms=2208`、`input_tokens=18`、`output_tokens=104`、`total_tokens=122`。
- 已运行 `MODEL_PROVIDER=deepseek PYTHONPATH=src python3 scripts/tool_calling_demo.py --real "请调用工具查询当前 Phase 1 进度，并告诉我下一步"`。
  - 结果：成功，退出码 `0`。
  - 模型先触发 `get_phase1_progress` 本地函数，再基于工具结果生成最终回答。
  - 观测摘要示例：`tool_triggered=true`、`tool_names=get_phase1_progress`、`success=true`。

## 结论

- 代码、单测、OpenSpec 校验和本地真实 DeepSeek 调用都已经证明最小观测链路可工作。
- 当前项目已经能够在 CLI 中稳定输出非流式、流式和 tool calling 的统一观测摘要。
- 下一步可以把这些最小观测结果继续接到更长期的 tracing、结构化日志或评测体系中。
