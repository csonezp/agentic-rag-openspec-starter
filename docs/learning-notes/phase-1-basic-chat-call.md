# Phase 1：实现一个基础聊天调用

日期：2026-04-27

对应 OpenSpec change：`learn-phase-1-basic-chat-call`

## 这一小节学什么

这一小节把上一节学到的 Responses API 请求/响应结构落到一个最小聊天入口上。

目标不是做完整聊天产品，而是建立最小工程闭环：

- 用户可以从命令行输入 prompt。
- 默认使用 dry-run，不访问网络、不消耗 token。
- 显式传入 `--real` 时才尝试真实 Responses API 调用。
- 真实模式缺少 `OPENAI_API_KEY` 时，直接给中文错误提示。
- 代码中保留 `ModelClient` 抽象，让 Agent 不直接依赖 OpenAI SDK 或 HTTP 细节。

## 当前运行方式

默认 dry-run：

```bash
PYTHONPATH=src python3 scripts/hello_model.py "你好，基础聊天调用"
```

输出结构：

```text
mode=dry-run
model=gpt-4.1-mini
Dry-run 响应：配置 OPENAI_API_KEY 后可调用真实模型。收到的提示词：你好，基础聊天调用
```

真实模式：

```bash
PYTHONPATH=src python3 scripts/hello_model.py --real "你好，Responses API"
```

真实模式要求配置：

```bash
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4.1-mini
```

## 代码结构

- `scripts/hello_model.py`
  - 负责命令行参数解析。
  - 支持默认 prompt 和命令行 prompt。
  - 支持默认 dry-run 和显式 `--real`。
  - 根据模式选择模型客户端。

- `src/agent_kb/hello_agent.py`
  - 保持简单，只校验 prompt 并调用 `ModelClient.complete()`。
  - 不关心模型来自 dry-run、HTTP 还是未来 SDK。

- `src/agent_kb/openai_client.py`
  - 新增 `ResponsesApiModelClient`。
  - 使用 Responses API 最小请求：`model + input`。
  - 从 response object 的 `output[].content[]` 中提取 `output_text`。
  - 把 HTTP 错误和网络错误转换成中文可调试错误。

## 为什么默认 dry-run

学习阶段默认 dry-run 有三个好处：

- 没有 API Key 也能运行项目。
- 单元测试不会访问网络或消耗 token。
- 可以先验证脚本参数、配置读取、Agent 调用链路，再引入真实模型的不确定性。

真实调用必须显式 `--real`，这让“会消耗 token 的行为”变得清楚。

## 当前结论

最小聊天调用不应该直接写成“脚本里请求 OpenAI 然后 print 文本”。更好的结构是：

```text
命令行脚本 -> AppConfig -> ModelClient -> HelloAgent -> 文本响应
```

这样后续学习 streaming、structured output、tool calling 时，可以继续扩展 `ModelClient` 或新增更具体的 client，而不是重写 Agent 主流程。
