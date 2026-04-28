## MODIFIED Requirements

### Requirement: Track Phase 2 progress

学习路线 MUST 记录 Phase 2 基础 RAG 的小节进度。

#### Scenario: 完成 grounded answer 小节

- **WHEN** 用户完成 Phase 2 的「基于检索上下文生成回答」
- **THEN** `docs/agent-learning-todo.md` MUST 将该小节标记为已完成
- **AND** 学习记录 MUST 说明检索上下文进入模型回答的流程和验证结果
