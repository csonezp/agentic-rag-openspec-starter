## ADDED Requirements

### Requirement: Grounded answer prompt

项目 MUST 能把检索结果转换为用于模型回答的上下文 prompt。

#### Scenario: 构造 grounded prompt

- **WHEN** 系统收到用户问题和 top-k 检索结果
- **THEN** prompt MUST 包含用户问题
- **AND** prompt MUST 包含每个检索 chunk 的 `chunk_id`、来源 metadata 和文本
- **AND** prompt MUST 要求模型基于给定上下文回答

### Requirement: Grounded answer generation

项目 MUST 支持基于检索上下文生成回答。

#### Scenario: 使用检索上下文回答问题

- **WHEN** 系统已获得 top-k chunks
- **THEN** 系统 MUST 把 grounded prompt 发送给模型 client
- **AND** 系统 MUST 返回模型回答和本次使用的检索结果

### Requirement: Grounded answer demo script

项目 MUST 提供一个本地演示脚本，串联 top-k 检索和回答生成。

#### Scenario: 运行 grounded answer 演示

- **WHEN** 用户运行回答演示脚本
- **THEN** 脚本 MUST 输出问题、provider、collection、top_k、检索上下文数量和回答文本

### Requirement: Grounded answer learning record

本小节完成时 MUST 记录 grounded answer 的 prompt 结构、验证结果和后续衔接点。

#### Scenario: 完成 grounded answer 小节

- **WHEN** grounded answer 小节完成
- **THEN** 对应 OpenSpec change 的 `tasks.md` MUST 更新勾选状态
- **AND** `docs/agent-learning-todo.md` 中对应小节 MUST 勾选
- **AND** MUST 新增或更新学习总结文档
