# 学习路线规格

## Requirements

### Requirement: 总路线持续可追踪

项目 MUST 保留一个总学习路线入口，用于追踪 Phase 级别的目标、任务和学习记录。

#### Scenario: 查看当前学习进度

- WHEN 需要恢复上下文或继续推进项目
- THEN SHOULD 先查看 `docs/agent-learning-todo.md`
- AND SHOULD 再查看当前活跃的 OpenSpec change

### Requirement: 阶段上下文可恢复

每个 Phase 的详细计划和实施上下文 SHOULD 能从对应 OpenSpec change 中恢复。

#### Scenario: 上下文丢失后恢复 Phase 工作

- WHEN 会话上下文丢失或切换到新会话
- THEN SHOULD 读取当前 Phase 的 `proposal.md`
- AND SHOULD 读取 `design.md` 和 `tasks.md`
- AND SHOULD 按任务清单继续推进
