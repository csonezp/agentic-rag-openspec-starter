## ADDED Requirements

### Requirement: Structured output request

项目 MUST 支持通过 DeepSeek JSON Output 请求生成结构化 JSON。

#### Scenario: 发送 JSON Output 请求

- **WHEN** 用户以真实模式运行结构化输出演示
- **THEN** DeepSeek 请求体 MUST 包含 `response_format` 为 `{"type":"json_object"}`
- **AND** 请求 prompt MUST 包含 `json` 字样和目标 JSON 示例

### Requirement: Small schema validation

项目 MUST 对模型返回的 JSON 做本地 schema 校验。

#### Scenario: 解析有效结构化输出

- **WHEN** 模型返回包含 `title`、`summary`、`next_action` 的 JSON 字符串
- **THEN** 系统 MUST 解析为结构化对象
- **AND** 每个字段 MUST 是非空字符串

#### Scenario: 拒绝无效结构化输出

- **WHEN** 模型返回的 JSON 缺少 required fields 或字段类型错误
- **THEN** 系统 MUST 返回明确错误

### Requirement: Structured output learning record

本小节完成时 MUST 记录结构化输出的实现方式、验证结果和 DeepSeek JSON Output 的边界。

#### Scenario: 完成结构化输出学习小节

- **WHEN** 结构化输出小节完成
- **THEN** 对应 OpenSpec change 的 `tasks.md` MUST 全部勾选
- **AND** `docs/agent-learning-todo.md` 中对应小节 MUST 勾选
- **AND** MUST 新增或更新学习总结文档
