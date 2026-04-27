# 学习路线规格

## Purpose

定义学习路线和阶段上下文的恢复方式，确保项目即使跨会话推进也能知道当前目标、已完成事项和下一步工作。

## Requirements

### Requirement: 总路线持续可追踪

项目 MUST 保留一个总学习路线入口，用于追踪 Phase 级别的目标、任务和学习记录。

#### Scenario: 查看当前学习进度

- **WHEN** 需要恢复上下文或继续推进项目
- **THEN** MUST 先查看 `docs/agent-learning-todo.md`
- **AND** MUST 再查看当前活跃的 OpenSpec change

### Requirement: 阶段上下文可恢复

每个 Phase 的详细计划和实施上下文 MUST 能从对应 OpenSpec change 中恢复。

#### Scenario: 上下文丢失后恢复 Phase 工作

- **WHEN** 会话上下文丢失或切换到新会话
- **THEN** MUST 读取当前 Phase 的 `proposal.md`
- **AND** MUST 读取 `design.md` 和 `tasks.md`
- **AND** MUST 按任务清单继续推进
