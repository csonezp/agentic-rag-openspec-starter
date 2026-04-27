## ADDED Requirements

### Requirement: Phase 1 tool calling completion

Phase 1 MUST 包含一个 function/tool calling 学习小节，用于验证模型可以请求调用本地函数并基于工具结果生成回答。

#### Scenario: 完成 tool calling 小节

- **WHEN** 用户要求学习 Phase 1 的 tool calling 小节
- **THEN** 路线图 MUST 记录该小节完成状态
- **AND** 小节完成标准 MUST 包含单元测试和一次真实 DeepSeek Tool Calls 验证
