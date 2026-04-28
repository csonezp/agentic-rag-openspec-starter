## ADDED Requirements

### Requirement: Local vector store

项目 MUST 支持把 `EmbeddedChunk` 写入本地向量库，用于后续检索学习。

#### Scenario: 初始化本地 collection

- **WHEN** 系统准备写入 embeddings
- **THEN** 系统 MUST 创建或复用一个本地 collection
- **AND** collection 的向量维度 MUST 与 embedding provider 输出维度一致

#### Scenario: 写入 chunk embedding

- **WHEN** 系统写入一个 `EmbeddedChunk`
- **THEN** 向量库 point MUST 包含 embedding 向量
- **AND** payload MUST 包含 chunk 文本和 metadata

#### Scenario: 重复写入相同 chunk

- **WHEN** 系统重复写入相同 `chunk_id` 的 chunk
- **THEN** 系统 MUST 使用稳定 point id
- **AND** 写入行为 MUST 是可重复执行的 upsert

### Requirement: Knowledge base indexing script

项目 MUST 提供一个本地索引脚本，把知识库 embeddings 写入本地向量库。

#### Scenario: 索引 knowledge 目录

- **WHEN** 用户运行索引脚本
- **THEN** 脚本 MUST 完成文档加载、标准化、切片、embedding 生成和向量库写入
- **AND** 脚本 MUST 输出 collection 名称、chunk 数量、写入 point 数量、向量维度和 provider

### Requirement: Local vector store learning record

本小节完成时 MUST 记录本地向量库的选型、数据结构、验证结果和后续衔接点。

#### Scenario: 完成本地向量库小节

- **WHEN** 本地向量库小节完成
- **THEN** 对应 OpenSpec change 的 `tasks.md` MUST 更新勾选状态
- **AND** `docs/agent-learning-todo.md` 中对应小节 MUST 勾选
- **AND** MUST 新增或更新学习总结文档
