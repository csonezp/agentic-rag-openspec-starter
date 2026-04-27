## ADDED Requirements

### Requirement: Phase 1 structured output completion

Phase 1 MUST 包含一个小 schema 结构化输出学习小节，用于验证模型输出可以被程序稳定解析和校验。

#### Scenario: 完成结构化输出小节

- **WHEN** 用户要求学习 Phase 1 的结构化输出小节
- **THEN** 路线图 MUST 记录该小节完成状态
- **AND** 小节完成标准 MUST 包含单元测试和一次真实 DeepSeek JSON Output 验证
