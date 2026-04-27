## ADDED Requirements

### Requirement: DeepSeek provider configuration

项目 MUST 支持通过环境变量配置 DeepSeek 官方 API 真实调用所需的 provider、API Key、base URL 和模型名。

#### Scenario: 使用 DeepSeek 默认配置

- **WHEN** 环境变量未显式设置 `MODEL_PROVIDER`、`DEEPSEEK_BASE_URL` 和 `DEEPSEEK_MODEL`
- **THEN** 配置 MUST 默认使用 `deepseek` provider
- **AND** DeepSeek base URL MUST 默认为 `https://api.deepseek.com`
- **AND** DeepSeek 模型 MUST 使用项目记录的默认模型

#### Scenario: 缺少 DeepSeek API Key

- **WHEN** `MODEL_PROVIDER` 为 `deepseek` 且用户以真实模式运行脚本
- **THEN** 系统 MUST 在调用网络前返回中文错误提示
- **AND** 进程 MUST 使用非零退出码

### Requirement: DeepSeek non-stream chat call

项目 MUST 能通过 DeepSeek 官方 Chat Completions API 完成一次真实非流式模型调用。

#### Scenario: 发送非流式请求

- **WHEN** 用户运行真实模式且未启用流式输出
- **THEN** DeepSeek 客户端 MUST 向 `/chat/completions` 发送 `messages` 格式请求
- **AND** 请求体 MUST 包含配置中的 DeepSeek 模型名
- **AND** 系统 MUST 从 `choices[].message.content` 中提取回答文本

### Requirement: DeepSeek streaming chat call

项目 MUST 能通过 DeepSeek 官方 Chat Completions API 完成一次真实流式模型调用。

#### Scenario: 解析流式响应片段

- **WHEN** DeepSeek 流式响应返回 data-only SSE
- **THEN** 系统 MUST 从每个 JSON chunk 的 `choices[].delta.content` 中提取文本片段
- **AND** 系统 MUST 在收到 `data: [DONE]` 后结束流式解析

### Requirement: DeepSeek learning record

本小节完成时 MUST 记录 DeepSeek 官方 API 与 OpenAI Responses API 的关键差异、验证结果和后续问题。

#### Scenario: 完成 DeepSeek 学习小节

- **WHEN** DeepSeek provider 接入完成并验证
- **THEN** 对应 OpenSpec change 的 `tasks.md` MUST 全部勾选
- **AND** `docs/agent-learning-todo.md` 中对应 Phase 1 小节 MUST 勾选
- **AND** MUST 新增或更新学习总结文档
