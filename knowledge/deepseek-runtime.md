# DeepSeek 运行时接入

本项目的真实模型 provider 是 DeepSeek 官方 API。运行真实模型调用时，需要通过本地环境变量提供 `MODEL_PROVIDER=deepseek` 和 `DEEPSEEK_API_KEY`。密钥不写入代码、不写入 `.env.example`，也不提交到 Git。

DeepSeek 的基础对话接口使用 Chat Completions 形态，请求路径是 `/chat/completions`。普通回答从 `choices[].message.content` 读取。流式输出使用 data-only SSE，文本片段来自 `choices[].delta.content`，并以 `data: [DONE]` 结束。

本项目默认模型由 `DEEPSEEK_MODEL` 指定。如果没有设置，当前代码使用 `deepseek-v4-flash` 作为默认模型。模型名不是写死在业务逻辑里，而是从配置层读取。

DeepSeek 兼容 OpenAI 的部分接口风格，但不能简单理解为 OpenAI Responses API 换一个 base URL。Responses API 使用 `/v1/responses` 和 `input` 字段，而 DeepSeek 当前基础接入使用 Chat Completions 的 `messages` 字段。

## 可验证事实

- 真实 provider 默认是 DeepSeek。
- API Key 来自本地环境变量。
- 默认模型配置项是 `DEEPSEEK_MODEL`。
- DeepSeek 基础对话使用 Chat Completions 形态。
