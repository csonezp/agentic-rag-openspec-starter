# 基础聊天调用学习规格

## Purpose

定义 Phase 1「基础聊天调用」学习小节的长期能力边界，确保项目保留最小聊天闭环、默认 dry-run 保护和真实 Responses API 调用入口的约定。

## Requirements

### Requirement: 基础聊天调用入口

系统 MUST 提供一个基础聊天调用入口，允许开发者传入 prompt 并获得文本响应。

#### Scenario: 使用 dry-run 模式运行

- **WHEN** 开发者运行基础聊天脚本且未显式选择真实模式
- **THEN** 系统 MUST 使用 dry-run 模型客户端
- **AND** MUST 输出包含 prompt 的模拟响应

#### Scenario: 从命令行传入 prompt

- **WHEN** 开发者通过命令行参数传入 prompt
- **THEN** 系统 MUST 使用该 prompt
- **AND** MUST NOT 使用脚本内默认 prompt

### Requirement: 真实调用需要显式选择

系统 MUST 避免在默认路径中调用真实 OpenAI API。

#### Scenario: 未显式选择真实模式

- **WHEN** 开发者未传入真实调用参数
- **THEN** 系统 MUST NOT 访问网络
- **AND** MUST NOT 消耗 API token

#### Scenario: 显式选择真实模式但缺少 API Key

- **WHEN** 开发者选择真实模式
- **AND** 未配置 `OPENAI_API_KEY`
- **THEN** 系统 MUST 输出可理解的中文错误信息
- **AND** MUST NOT 发送真实请求

### Requirement: 真实 Responses API 最小请求

系统 MUST 在真实模式下使用 Responses API 的最小请求结构。

#### Scenario: 配置 API Key 并选择真实模式

- **WHEN** 开发者配置 `OPENAI_API_KEY`
- **AND** 显式选择真实模式
- **THEN** 系统 MUST 使用配置的 `OPENAI_MODEL`
- **AND** MUST 把 prompt 作为 Responses API 的 `input`
- **AND** MUST 返回模型输出文本或可调试错误信息
