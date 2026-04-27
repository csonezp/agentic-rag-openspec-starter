## Why

当前项目的真实模型调用路径只支持 OpenAI Responses API，但用户实际使用的是 DeepSeek 官方 API。为了让学习项目可以调用真实模型并继续推进后续 RAG/Agent 实验，需要在 Phase 1 中补齐 DeepSeek provider 接入。

本小节同时用于学习“同一个 Agent 抽象如何适配不同模型服务商”：保留上层 `ModelClient` 协议，把 provider 差异收敛到独立客户端和配置层。

## What Changes

- 在 Phase 1 路线中新增“接入 DeepSeek 官方 API 并完成真实模型调用”小节。
- 新增 DeepSeek Chat Completions 客户端，实现非流式 `complete()` 和流式 `stream()`。
- 将真实模式从“只支持 OpenAI”调整为“按配置选择 provider”，默认真实 provider 使用 DeepSeek。
- 新增 DeepSeek 相关环境变量约定，并保留 OpenAI Responses API 客户端用于前序学习成果。
- 为 DeepSeek 请求体、响应解析、流式 SSE 解析、缺少 API Key 等行为添加测试。
- 新增学习总结，记录 DeepSeek 官方 API 与 OpenAI Responses API 的关键差异。

不做：

- 不在本小节实现 RAG、embedding、结构化输出或 tool calling。
- 不引入第三方 SDK；继续使用标准库 `urllib`，降低依赖和学习干扰。
- 不把 DeepSeek 的思考模式、reasoning 参数、JSON Output、Tool Calls 一次性铺开；本小节只完成基础真实对话和流式输出。

## Capabilities

### New Capabilities

- `deepseek-provider-learning`: 覆盖 DeepSeek 官方 API provider 接入学习，包括配置、非流式调用、流式调用和基础验证。

### Modified Capabilities

- `learning-roadmap`: Phase 1 路线增加 DeepSeek 官方 API 真实模型对接小节。

## Impact

- 影响配置：`.env.example`、`src/agent_kb/config.py`。
- 影响真实调用入口：`scripts/hello_model.py`。
- 新增或调整模型客户端：`src/agent_kb/deepseek_client.py`，保留 `src/agent_kb/openai_client.py`。
- 影响测试：新增 DeepSeek 客户端测试，调整配置和 CLI 测试。
- 影响文档：更新 `docs/agent-learning-todo.md`，新增学习笔记。
