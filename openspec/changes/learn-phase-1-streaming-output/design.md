## Overview

本小节实现最小流式输出闭环：用户传入 prompt，脚本启用 `--stream`，模型客户端逐步产出文本 chunk，脚本边收到边打印。

官方文档说明 Responses API 通过 `stream=True` 开启 HTTP SSE，常见文本流事件包括 `response.created`、`response.output_text.delta`、`response.completed` 和 `error`。本项目只处理文本 delta 和 error。

## 设计要点

- 保留 `complete(prompt) -> str`，不破坏基础聊天调用。
- 增加可选 `stream(prompt) -> Iterable[str]` 能力。
- `HelloAgent` 增加 `stream()`，只负责 prompt 校验和委托。
- `DryRunModelClient.stream()` 使用本地字符串切分模拟流式输出，方便测试。
- `ResponsesApiModelClient.stream()` 使用 `stream: true` 请求 Responses API，并解析 SSE 的 `data:` 行。
- 只从事件 `response.output_text.delta` 中提取 `delta` 文本。
- 遇到 `error` 事件时抛出中文可调试错误。

## CLI 行为

- 默认：非流式 dry-run。
- `--stream`：启用流式输出。
- `--real --stream`：真实 Responses API streaming，要求 `OPENAI_API_KEY`。
- 缺少 API Key 时仍然不发送真实请求。

## 不做事项

- 不做 WebSocket mode。
- 不做浏览器 SSE endpoint。
- 不做工具调用参数流式解析。
- 不做 structured output streaming。
- 不做复杂重连、重试和 moderation 管线。

## 风险

生产环境中流式输出更难做完整内容审核，因为用户会看到部分输出。本小节只做学习样例，不用于生产审核策略。
