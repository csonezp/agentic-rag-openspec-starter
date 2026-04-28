## ADDED Requirements

### Requirement: Source citation objects

项目 MUST 能从检索结果生成结构化来源引用。

#### Scenario: 从检索结果生成 citations

- **WHEN** 系统已获得 top-k 检索结果
- **THEN** 系统 MUST 生成 citations
- **AND** 每条 citation MUST 包含 `chunk_id`、`source_path`、`title`、`chunk_index` 和 score

### Requirement: Grounded answer with citations

项目 MUST 在基于检索上下文生成回答时携带来源引用。

#### Scenario: 生成带来源的回答

- **WHEN** 系统基于检索上下文生成回答
- **THEN** 结果对象 MUST 包含 answer
- **AND** 结果对象 MUST 包含 citations
- **AND** prompt SHOULD 要求模型使用 `[chunk_id]` 标记依据

### Requirement: Source citation demo output

回答演示脚本 MUST 输出结构化 sources 列表。

#### Scenario: 运行带来源的回答演示

- **WHEN** 用户运行回答演示脚本
- **THEN** 脚本 MUST 输出 answer
- **AND** 脚本 MUST 输出 sources 列表
- **AND** 每条 source MUST 包含 chunk id 和来源 metadata

### Requirement: Source citation learning record

本小节完成时 MUST 记录来源引用格式、验证结果和后续衔接点。

#### Scenario: 完成来源引用小节

- **WHEN** 来源引用小节完成
- **THEN** 对应 OpenSpec change 的 `tasks.md` MUST 更新勾选状态
- **AND** `docs/agent-learning-todo.md` 中对应小节 MUST 勾选
- **AND** MUST 新增或更新学习总结文档
