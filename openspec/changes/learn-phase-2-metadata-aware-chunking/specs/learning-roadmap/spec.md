## MODIFIED Requirements

### Requirement: 总路线持续可追踪

项目 MUST 保留一个总学习路线入口，用于追踪 Phase 级别的目标、任务和学习记录。

#### Scenario: Phase 2 带元数据的文档切片小节完成

- **WHEN** “实现带元数据的文档切片”小节完成
- **THEN** MUST 更新 `docs/agent-learning-todo.md` 中对应任务为已完成
- **AND** MUST 记录本次学习的验证结果和关键结论
