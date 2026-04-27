# LLM 应用基础规格增量

## ADDED Requirements

### Requirement: Dry-run 模式

系统 MUST 在没有真实模型 API Key 的情况下提供可运行的 dry-run 路径。

#### Scenario: 无 API Key 运行示例

- WHEN 开发者未配置 `OPENAI_API_KEY`
- THEN 示例脚本 MUST 不访问网络
- AND MUST 返回清晰的 dry-run 响应

### Requirement: 真实模型调用入口

系统 SHOULD 提供一个真实模型调用入口，用于学习基础聊天请求。

#### Scenario: 配置 API Key 后调用模型

- WHEN 开发者配置了 `OPENAI_API_KEY`
- AND 运行真实模型调用脚本
- THEN 系统 SHOULD 调用配置的模型
- AND SHOULD 输出模型响应或可理解的错误信息

### Requirement: 结构化输出示例

系统 SHOULD 提供一个小型结构化输出示例，用于学习模型输出约束。

#### Scenario: 请求结构化结果

- WHEN 开发者运行结构化输出示例
- THEN 系统 SHOULD 返回符合预期 schema 的结果
- AND SHOULD 在解析失败时输出可调试信息

### Requirement: 本地工具调用示例

系统 SHOULD 提供一个只读本地工具调用示例。

#### Scenario: 模型需要调用本地工具

- WHEN 示例问题需要工具辅助
- THEN 系统 SHOULD 使用白名单中的只读工具
- AND MUST 校验工具输入
- AND MUST 记录工具调用结果
