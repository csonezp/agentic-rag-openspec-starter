## Context

当前 `HelloAgent` 已经通过 `ModelClient` 协议与具体模型服务解耦，支持 `complete()` 和 `stream()` 两种调用方式。但真实模式仍然固定使用 `ResponsesApiModelClient`，并且配置、错误提示和 CLI 文案都以 OpenAI Responses API 为中心。

用户真实使用 DeepSeek 官方 API。根据 DeepSeek 官方文档，DeepSeek 支持 OpenAI 兼容格式，但基础对话接口是 `POST /chat/completions`，请求使用 `messages`，流式输出使用 data-only SSE，并以 `data: [DONE]` 结束。这与 OpenAI Responses API 的 `/v1/responses`、`input` 和 `response.output_text.delta` 事件结构不同。

## Goals / Non-Goals

**Goals:**

- 在 Phase 1 增加 DeepSeek 官方 API 真实模型对接小节。
- 新增 DeepSeek Chat Completions 客户端，适配现有 `ModelClient` 协议。
- 让 `scripts/hello_model.py --real` 可以按配置选择 DeepSeek 或 OpenAI。
- 完成 DeepSeek 非流式与流式输出的单元测试。
- 用真实 `DEEPSEEK_API_KEY` 验证至少一次真实模型调用。

**Non-Goals:**

- 不在本小节实现 RAG、embedding、结构化输出或工具调用。
- 不引入 OpenAI SDK 或 DeepSeek SDK，继续保持标准库实现。
- 不在配置层一次性抽象所有模型厂商能力，只支持当前学习所需的 `deepseek` 与 `openai`。
- 不默认开启 DeepSeek thinking/reasoning 参数；后续需要时单独学习和记录。

## Decisions

### Decision: 保留 `ModelClient`，新增 provider 客户端

`HelloAgent` 不感知 OpenAI 或 DeepSeek，只依赖 `ModelClient`。DeepSeek 差异放到 `DeepSeekChatCompletionsModelClient` 内部，包括 URL、请求体、响应解析和流式事件解析。

备选方案是直接改造 `ResponsesApiModelClient`，但这会混淆 Responses API 与 Chat Completions 两种不同协议，不利于学习和后续维护。

### Decision: 配置层使用 `MODEL_PROVIDER`

新增 `MODEL_PROVIDER`，默认值为 `deepseek`。当用户运行 `--real` 时，CLI 根据 provider 构造对应客户端。OpenAI 相关配置继续保留，便于回看前序 Responses API 学习成果。

备选方案是用 `--provider` CLI 参数，但环境变量更适合后续 Web 服务和部署场景；CLI 参数可以后续再补。

### Decision: DeepSeek 默认模型使用官方当前推荐模型

DeepSeek 配置默认使用 `deepseek-v4-flash`，并允许通过 `DEEPSEEK_MODEL` 覆盖。这样避免继续默认使用官方已标记未来弃用的 `deepseek-chat`，同时保持用户可以自行选择模型。

### Decision: 先支持基础 message 结构

当前 `HelloAgent` 的输入是单轮 prompt，DeepSeek 客户端会转为：

- `system`: 简短说明模型是学习项目助手。
- `user`: 用户输入的 prompt。

多轮对话历史、thinking 参数、JSON Output 和 Tool Calls 后续以独立小节推进。

## Risks / Trade-offs

- [Risk] DeepSeek API 字段或默认模型可能变化。→ 实现时把 `base_url` 和 `model` 放入环境变量，并在学习笔记记录官方文档查询日期。
- [Risk] OpenAI Responses API 与 DeepSeek Chat Completions 的响应结构不同，容易误用同一个 parser。→ 为 DeepSeek 单独实现并测试 `choices[].message.content` 和 `choices[].delta.content` 解析。
- [Risk] 真实 API 验证依赖本地 `DEEPSEEK_API_KEY`。→ 单元测试不依赖真实网络；真实调用作为手动验证步骤记录结果。
- [Risk] provider 配置增加后，CLI 文案可能让初学者困惑。→ README 和 `.env.example` 明确默认真实 provider 是 DeepSeek，OpenAI 作为可选 provider 保留。
