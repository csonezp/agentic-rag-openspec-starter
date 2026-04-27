# 项目治理规格

## Purpose

定义项目协作、文档语言和 OpenSpec 阶段追踪的长期约定，确保后续会话可以恢复上下文并保持文档一致。

## Requirements

### Requirement: 中文文档约定

项目中面向人的说明文档、进度文档、学习笔记、运行手册和任务记录 MUST 使用中文。

#### Scenario: 新增学习记录

- **WHEN** 新增或更新学习进度、任务记录、运行说明
- **THEN** 内容 MUST 使用中文表达
- **AND** 代码标识符、命令、环境变量名、第三方 API 名称 MAY 保持英文

### Requirement: OpenSpec 阶段追踪

每个新的学习阶段或较大功能 MUST 使用独立 OpenSpec change 管理上下文。

#### Scenario: 启动新 Phase

- **WHEN** 准备开始一个新的学习 Phase
- **THEN** MUST 创建 `openspec/changes/<change-id>/`
- **AND** MUST 包含 `proposal.md`、`design.md`、`tasks.md` 和相关 `specs/`
- **AND** MUST 在实现过程中更新 `tasks.md`

### Requirement: 学习小节变更流程

用户通过“学习 Phase X 的某个小节”启动学习单元时，系统 MUST 以学习小节为粒度管理 OpenSpec change。

#### Scenario: 学习小节尚未完成

- **WHEN** 用户请求学习某个未完成的小节
- **THEN** 系统 MUST 创建独立 OpenSpec change
- **AND** change id MUST 使用 `learn-phase-<n>-<topic>` 形式
- **AND** 系统 MUST 告诉用户新增或修改了哪些文件，以及为什么这样改
- **AND** 系统 MUST 在用户确认继续后再进入实验、代码修改或任务实施

#### Scenario: 学习小节已经完成

- **WHEN** 用户请求学习某个已经完成的小节
- **THEN** 系统 MUST 直接说明该小节已完成
- **AND** MUST NOT 创建新的 change
- **AND** MUST NOT 修改文件

#### Scenario: 学习小节完成

- **WHEN** 一个学习小节完成
- **THEN** 系统 MUST 更新对应 change 的 `tasks.md`
- **AND** MUST 更新 `docs/agent-learning-todo.md` 中对应小节勾选状态
- **AND** MUST 记录学习总结、验证结果、坑点或后续问题
