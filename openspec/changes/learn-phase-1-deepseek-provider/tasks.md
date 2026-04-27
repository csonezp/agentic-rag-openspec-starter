## 1. 路线与配置

- [x] 1.1 在 Phase 1 路线中新增 DeepSeek 官方 API 真实模型对接小节。
- [x] 1.2 更新 `.env.example`，记录 DeepSeek provider 所需环境变量。
- [x] 1.3 扩展 `AppConfig`，支持 `MODEL_PROVIDER`、DeepSeek API Key、base URL 和模型名。

## 2. DeepSeek 客户端实现

- [x] 2.1 先编写 DeepSeek 配置和客户端解析相关单元测试，并确认测试失败。
- [x] 2.2 新增 DeepSeek Chat Completions 客户端，支持非流式 `complete()`。
- [x] 2.3 新增 DeepSeek 流式 SSE parser 和 `stream()` 实现。
- [x] 2.4 更新 CLI 真实模式，根据 provider 选择 DeepSeek 或 OpenAI 客户端。

## 3. 文档与验证

- [x] 3.1 更新 README 或运行说明，说明 DeepSeek 真实模式运行方式。
- [x] 3.2 新增学习笔记，记录 DeepSeek 与 OpenAI Responses API 的关键差异。
- [x] 3.3 运行单元测试和 OpenSpec 严格校验。
- [x] 3.4 使用本地 `DEEPSEEK_API_KEY` 完成一次真实非流式模型调用验证。
- [x] 3.5 使用本地 `DEEPSEEK_API_KEY` 完成一次真实流式模型调用验证。
- [x] 3.6 完成后更新 `tasks.md` 和 `docs/agent-learning-todo.md` 勾选状态。
