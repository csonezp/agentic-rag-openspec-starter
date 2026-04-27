# Phase 1 学习笔记：接入 DeepSeek 官方 API

日期：2026-04-27

## 学习目标

本小节目标是把项目的真实模型调用从“只支持 OpenAI Responses API”扩展为“可按 provider 选择模型服务”，并完成 DeepSeek 官方 API 的真实非流式和流式调用验证。

## 官方 API 观察

DeepSeek 官方文档说明其 API 使用与 OpenAI/Anthropic 兼容的格式。OpenAI 兼容入口的 `base_url` 是 `https://api.deepseek.com`，基础对话接口是 `POST /chat/completions`。

本小节只接入 Chat Completions 的基础能力：

- 非流式请求使用 `messages` 数组。
- 响应文本来自 `choices[].message.content`。
- 流式请求设置 `stream: true`。
- 流式响应是 data-only SSE，文本片段来自 `choices[].delta.content`。
- 流式响应通过 `data: [DONE]` 结束。

## 与 OpenAI Responses API 的差异

- OpenAI Responses API 使用 `/v1/responses`，DeepSeek 使用 `/chat/completions`。
- OpenAI Responses API 最小请求可以使用 `input`，DeepSeek Chat Completions 使用 `messages`。
- OpenAI Responses API 的普通文本输出来自 `output[].content[].text`，DeepSeek 来自 `choices[].message.content`。
- OpenAI Responses API 的流式文本事件类型是 `response.output_text.delta`，DeepSeek 流式文本来自 `choices[].delta.content`。
- 因此不能把 DeepSeek 简单理解为“换一个 base URL 的 Responses API”，它兼容的是 Chat Completions 形态。

## 实现记录

- 保留 `ModelClient` 抽象，`HelloAgent` 不感知 provider。
- 新增 `DeepSeekChatCompletionsModelClient`，负责 DeepSeek 请求体、响应解析和流式 SSE 解析。
- 新增 `MODEL_PROVIDER`，默认真实 provider 使用 `deepseek`。
- 真实密钥只通过本机环境变量读取，不写入代码，也不写入可提交文件。
- 保留 `ResponsesApiModelClient`，用于回看前序 OpenAI Responses API 学习小节。
- CLI 的 `--real` 根据 `MODEL_PROVIDER` 选择 DeepSeek 或 OpenAI。

## 验证记录

- 单元测试覆盖配置读取、DeepSeek 非流式请求、DeepSeek 流式解析、CLI 缺少 API Key 错误。
- OpenSpec 严格校验用于确认 change 和 specs 格式正确。
- 单元测试验证命令：`PYTHONPATH=src:. python3 -m unittest discover -s tests`，结果为 16 个测试通过。
- OpenSpec 验证命令：`/opt/homebrew/bin/openspec validate --all --strict`，结果为 7 项通过。
- 真实非流式调用验证通过，命令使用 `--real`，DeepSeek 返回了正常回答。
- 真实流式调用验证通过，命令使用 `--real --stream`，DeepSeek 返回了流式文本片段。

## 后续问题

- 是否要在后续小节学习 DeepSeek thinking/reasoning 参数。
- 是否要为 provider 增加统一的调用元数据返回值，例如模型名、token 使用量和延迟。
- 是否要在结构化输出和 tool calling 小节中同时验证 DeepSeek 与 OpenAI 的差异。
