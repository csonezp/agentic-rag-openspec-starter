## ADDED Requirements

### Requirement: DeepSeek 真实调用观测信息

系统 MUST 为当前 Phase 1 主用的 DeepSeek 真实调用链路提供可读的最小观测信息。

#### Scenario: 非流式真实调用完成

- **WHEN** 开发者以真实模式运行基础聊天调用
- **THEN** 系统 MUST 输出本次调用使用的 provider 和 model
- **AND** MUST 输出本次调用的 latency
- **AND** SHOULD 输出 `input_tokens`、`output_tokens` 和 `total_tokens`
- **AND** MUST 保留可调试的错误信息

#### Scenario: 流式真实调用完成

- **WHEN** 开发者以真实模式运行流式输出
- **THEN** 系统 MUST 在流式文本结束后输出本次调用的观测摘要
- **AND** MUST 至少包含 provider、model 和 latency
- **AND** MAY 在 provider 可提供时输出 token 使用量

### Requirement: Tool Calling 观测信息

系统 MUST 为当前 Phase 1 的 tool calling 学习链路提供最小过程观测信息。

#### Scenario: tool calling 真实调用完成

- **WHEN** 开发者以真实模式运行 tool calling 演示脚本
- **THEN** 系统 MUST 能区分模型调用成功与失败
- **AND** MUST 能看见是否触发了 tool calling
- **AND** SHOULD 能看见被触发的 tool 名称

### Requirement: Dry-run 兼容性

系统 MUST 保持默认 dry-run 路径可运行。

#### Scenario: 未启用真实模式

- **WHEN** 开发者未显式选择真实模式
- **THEN** 系统 MUST 继续使用 dry-run
- **AND** MUST NOT 因新增观测能力而要求真实 API Key
