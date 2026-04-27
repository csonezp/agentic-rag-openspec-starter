## ADDED Requirements

### Requirement: Responses API 结构学习上下文

系统 MUST 为“学习 Responses API 的请求和响应结构”小节保留可恢复的学习上下文。

#### Scenario: 启动小节学习

- **WHEN** 用户请求学习 Phase 1 的 Responses API 请求和响应结构
- **THEN** 系统 MUST 创建独立 OpenSpec change
- **AND** MUST 明确本小节的学习范围、不做事项和完成标准

### Requirement: 官方文档来源

Responses API 结构学习 MUST 以 OpenAI 官方文档作为事实来源。

#### Scenario: 整理字段结构

- **WHEN** 整理请求字段、响应字段或示例结构
- **THEN** 系统 MUST 引用 OpenAI 官方 Responses API 文档
- **AND** MUST 避免基于过期记忆编造字段或行为

### Requirement: 学习优先于实现

本小节 MUST 先完成结构理解和学习记录，再进入真实模型调用实现。

#### Scenario: 用户尚未确认继续实验

- **WHEN** 仅创建本学习小节 change
- **THEN** 系统 MUST NOT 修改生产代码
- **AND** MUST NOT 调用真实 OpenAI API
