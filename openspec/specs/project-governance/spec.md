# 项目治理规格

## Requirements

### Requirement: 中文文档约定

项目中面向人的说明文档、进度文档、学习笔记、运行手册和任务记录 MUST 使用中文。

#### Scenario: 新增学习记录

- WHEN 新增或更新学习进度、任务记录、运行说明
- THEN 内容 MUST 使用中文表达
- AND 代码标识符、命令、环境变量名、第三方 API 名称 MAY 保持英文

### Requirement: OpenSpec 阶段追踪

每个新的学习阶段或较大功能 SHOULD 使用独立 OpenSpec change 管理上下文。

#### Scenario: 启动新 Phase

- WHEN 准备开始一个新的学习 Phase
- THEN SHOULD 创建 `openspec/changes/<change-id>/`
- AND SHOULD 包含 `proposal.md`、`design.md`、`tasks.md` 和相关 `specs/`
- AND SHOULD 在实现过程中更新 `tasks.md`
