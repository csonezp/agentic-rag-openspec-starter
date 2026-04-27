## ADDED Requirements

### Requirement: Tool schema request

项目 MUST 支持向 DeepSeek Chat Completions 请求传入本地函数的 tool schema。

#### Scenario: 发送工具定义

- **WHEN** 用户以真实模式运行 tool calling 演示
- **THEN** 请求体 MUST 包含 `tools`
- **AND** 工具 MUST 使用 `type=function`
- **AND** 工具名 MUST 为本地 allowlist 中的函数

### Requirement: Tool call execution loop

项目 MUST 能解析模型返回的 tool call，执行本地函数，并把工具结果回传给模型生成最终回答。

#### Scenario: 执行本地函数闭环

- **WHEN** 模型返回 `tool_calls`
- **THEN** 系统 MUST 校验工具名在 allowlist 中
- **AND** MUST 解析并校验 arguments
- **AND** MUST 执行对应本地函数
- **AND** MUST 把 tool 结果作为 `role=tool` 消息回传模型

### Requirement: Tool calling safety

项目 MUST 把模型生成的工具名和参数视为不可信输入。

#### Scenario: 拒绝未知工具

- **WHEN** 模型请求调用未注册工具
- **THEN** 系统 MUST 拒绝执行并返回明确错误

#### Scenario: 拒绝非法参数

- **WHEN** 模型返回无法解析为 JSON object 的 arguments
- **THEN** 系统 MUST 拒绝执行并返回明确错误

### Requirement: Tool calling learning record

本小节完成时 MUST 记录 tool calling 的执行流程、验证结果和安全边界。

#### Scenario: 完成 tool calling 小节

- **WHEN** tool calling 小节完成
- **THEN** 对应 OpenSpec change 的 `tasks.md` MUST 全部勾选
- **AND** `docs/agent-learning-todo.md` 中对应小节 MUST 勾选
- **AND** MUST 新增或更新学习总结文档
