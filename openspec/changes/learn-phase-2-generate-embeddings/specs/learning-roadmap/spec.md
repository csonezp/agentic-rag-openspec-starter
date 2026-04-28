## ADDED Requirements

### Requirement: Phase 2 embeddings completion

Phase 2 MUST 包含一个 embeddings 生成学习小节，用于把带元数据的 chunks 转换为后续向量存储可使用的向量对象。

#### Scenario: 完成 embeddings 小节

- **WHEN** 用户要求学习 Phase 2 的生成 embeddings 小节
- **THEN** 路线图 MUST 记录该小节完成状态
- **AND** 小节完成标准 MUST 包含单元测试和本地演示脚本验证
