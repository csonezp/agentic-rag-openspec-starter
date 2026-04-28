## ADDED Requirements

### Requirement: Top-k chunk retrieval

项目 MUST 支持针对用户问题从本地向量库检索 top-k chunks。

#### Scenario: 检索 top-k chunks

- **WHEN** 用户提供一个问题和 `top_k`
- **THEN** 系统 MUST 生成 query embedding
- **AND** MUST 从本地 Qdrant collection 返回最多 `top_k` 个相关 chunks
- **AND** 返回结果 MUST 按相似度 score 排序

#### Scenario: 检索结果包含来源 metadata

- **WHEN** 系统返回检索结果
- **THEN** 每条结果 MUST 包含 `chunk_id`、`source_path`、`title`、`chunk_index` 和 chunk 文本
- **AND** 每条结果 MUST 包含向量检索 score

### Requirement: Top-k retrieval demo script

项目 MUST 提供一个本地演示脚本，用于对问题检索 top-k chunks。

#### Scenario: 运行检索演示

- **WHEN** 用户运行检索演示脚本
- **THEN** 脚本 MUST 输出问题、collection、provider、top_k 和检索结果摘要
- **AND** 每条结果 MUST 输出 score、来源和文本预览

### Requirement: Top-k retrieval learning record

本小节完成时 MUST 记录 top-k 检索流程、验证结果和后续衔接点。

#### Scenario: 完成 top-k 检索小节

- **WHEN** top-k 检索小节完成
- **THEN** 对应 OpenSpec change 的 `tasks.md` MUST 更新勾选状态
- **AND** `docs/agent-learning-todo.md` 中对应小节 MUST 勾选
- **AND** MUST 新增或更新学习总结文档
