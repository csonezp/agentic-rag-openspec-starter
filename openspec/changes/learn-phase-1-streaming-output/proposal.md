## Why

基础聊天调用已经可以通过 dry-run 或真实 Responses API 返回完整文本。下一步需要学习流式输出，让模型生成过程中产生的文本增量可以被逐步处理，为后续 CLI 体验、Web SSE、工具调用进度和 RAG 调试输出打基础。

## What Changes

- 创建学习小节 change `learn-phase-1-streaming-output`。
- 学习 Responses API 的 `stream=true` 和 SSE 事件模型。
- 为现有模型客户端增加最小流式输出能力。
- 在 dry-run 模式下提供可测试的流式 token/chunk 输出。
- 在真实模式下解析 Responses API streaming 事件中的 `response.output_text.delta`。
- 脚本增加显式 `--stream` 开关；默认仍保持非流式 dry-run。

## Capabilities

### New Capabilities

- `streaming-output-learning`: 记录 Phase 1 流式输出小节的学习目标、最小行为和验证方式。

### Modified Capabilities

- 无。

## Impact

- 影响 `src/agent_kb/hello_agent.py`、`src/agent_kb/openai_client.py` 和 `scripts/hello_model.py`。
- 新增或更新测试与中文学习笔记。
- 不做 WebSocket，不做 streaming tool calls，不做 streaming structured output，不接入 RAG。
