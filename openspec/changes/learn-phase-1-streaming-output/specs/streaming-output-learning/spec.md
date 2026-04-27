## ADDED Requirements

### Requirement: Dry-run 流式输出

系统 MUST 在 dry-run 模式下支持可测试的流式文本输出。

#### Scenario: 使用 dry-run streaming

- **WHEN** 开发者运行脚本并传入 `--stream`
- **AND** 未显式选择真实模式
- **THEN** 系统 MUST 不访问网络
- **AND** MUST 逐步输出 prompt 对应的模拟文本 chunk

### Requirement: 真实 Responses API streaming

系统 MUST 在真实模式下使用 Responses API 的 streaming 事件模型。

#### Scenario: 使用真实 streaming

- **WHEN** 开发者配置 `OPENAI_API_KEY`
- **AND** 传入 `--real --stream`
- **THEN** 系统 MUST 在请求体中设置 `stream: true`
- **AND** MUST 解析 `response.output_text.delta` 事件中的文本增量
- **AND** MUST 在收到 `error` 事件时输出可调试错误

### Requirement: 非流式兼容

系统 MUST 保持现有非流式基础聊天调用可用。

#### Scenario: 不传入 stream 参数

- **WHEN** 开发者未传入 `--stream`
- **THEN** 系统 MUST 沿用现有 `complete()` 路径
- **AND** MUST 保持原有测试通过
