# Phase 1：添加流式输出

日期：2026-04-27

对应 OpenSpec change：`learn-phase-1-streaming-output`

官方参考：

- [Streaming API responses](https://developers.openai.com/api/docs/guides/streaming-responses)

## 这一小节学什么

这一小节学习 Responses API 的流式输出模型，并把它接到当前基础聊天脚本中。

目标不是做完整 Web SSE 服务，而是建立最小工程闭环：

- 脚本支持 `--stream`。
- 默认 dry-run 可以流式输出，不访问网络、不消耗 token。
- 真实模式使用 Responses API 的 `stream: true`。
- 只解析文本增量事件 `response.output_text.delta`。
- 保持原有非流式 `complete()` 路径可用。

## 官方心智模型

OpenAI 官方文档说明，普通请求会等模型完整生成后一次性返回；streaming 可以在模型继续生成时，先处理已经生成的开头部分。

Responses API 的 streaming 使用 HTTP SSE。常见文本流事件包括：

- `response.created`
- `response.output_text.delta`
- `response.completed`
- `error`

本项目当前只处理：

- `response.output_text.delta`：提取 `delta` 文本片段。
- `error`：转换为中文可调试错误。

## 当前运行方式

dry-run streaming：

```bash
PYTHONPATH=src python3 scripts/hello_model.py --stream "你好，流式输出"
```

输出示例：

```text
mode=dry-run
stream=true
model=gpt-4.1-mini
Dry-run 响应：配置 OPENAI_API_KEY 后可调用真实模型。收到的提示词：你好，流式输出。
```

真实 streaming：

```bash
PYTHONPATH=src python3 scripts/hello_model.py --real --stream "你好，Responses API streaming"
```

真实模式需要配置：

```bash
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4.1-mini
```

## 代码结构变化

- `HelloAgent.stream(prompt)`
  - 校验 prompt。
  - 委托给模型客户端的 `stream()`。

- `DryRunModelClient.stream(prompt)`
  - 使用本地字符串切分模拟 chunk。
  - 用于学习和测试，不访问网络。

- `ResponsesApiModelClient.stream(prompt)`
  - 发送 `{"model": ..., "input": ..., "stream": true}`。
  - 读取 SSE `data:` 行。
  - 从 `response.output_text.delta` 事件中 yield `delta`。

- `scripts/hello_model.py`
  - 新增 `--stream` 参数。
  - 非流式时走 `agent.run()`。
  - 流式时走 `agent.stream()` 并边收到边打印。

## 和非流式的区别

非流式：

```text
请求 -> 等完整响应 -> 解析 output_text -> 打印完整文本
```

流式：

```text
请求 stream=true -> 接收多个 SSE event -> 提取 delta -> 增量打印
```

这意味着调用方不能只关心“最终字符串”，还要能处理事件顺序、增量片段、完成事件和错误事件。

## 生产风险

流式输出会让用户更早看到模型的部分输出，内容审核更难，因为 partial completion 可能还没有完整上下文。本项目当前只是学习样例，不处理生产级 moderation。

## 当前结论

流式输出应该是模型客户端能力，而不是写死在脚本里。脚本只负责选择是否 `--stream`，Agent 只负责委托，真实 SSE 细节封装在 `ResponsesApiModelClient` 里。

这个边界能让后续 Web SSE、RAG 检索进度、工具调用进度都复用同样的“逐步 yield chunk”心智模型。
