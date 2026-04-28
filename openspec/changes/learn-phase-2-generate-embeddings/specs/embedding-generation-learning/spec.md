## ADDED Requirements

### Requirement: Deterministic embedding model

项目 MUST 提供一个本地可重复的 embedding 模型实现，用于学习和测试 embedding 生成流程。

#### Scenario: 同一文本生成稳定向量

- **WHEN** 使用相同 embedding 模型对同一文本生成向量
- **THEN** 返回向量 MUST 完全一致
- **AND** 向量维度 MUST 等于模型配置维度

#### Scenario: 不同文本生成不同向量

- **WHEN** 使用相同 embedding 模型对不同文本生成向量
- **THEN** 返回向量 SHOULD 不完全相同

### Requirement: Chunk embedding metadata

项目 MUST 能为 `DocumentChunk` 生成 embedding，并保留 chunk metadata。

#### Scenario: 生成 chunk embedding

- **WHEN** 系统为一个 chunk 生成 embedding
- **THEN** 输出对象 MUST 保留原始 `DocumentChunk`
- **AND** MUST 包含固定维度 embedding 向量

### Requirement: Embedding demo pipeline

项目 MUST 提供一个本地演示脚本，串联文档加载、标准化、切片和 embedding 生成。

#### Scenario: 对 knowledge 生成 embeddings

- **WHEN** 用户运行 embeddings 演示脚本
- **THEN** 脚本 MUST 输出 chunk 数量、embedding 数量和向量维度

### Requirement: Local real embedding provider

项目 MUST 支持一个真实本地 embedding provider，用于在不调用云端 API 的情况下生成语义向量。

#### Scenario: 使用 FastEmbed 生成 embedding

- **WHEN** 用户选择 `fastembed` provider
- **THEN** 系统 MUST 使用 FastEmbed 客户端生成 embedding
- **AND** 向量维度 MUST 与 provider 配置一致

#### Scenario: 使用 hashing provider 作为测试兜底

- **WHEN** 用户选择 `hashing` provider
- **THEN** 系统 MUST 使用 deterministic hashing embedding
- **AND** 单元测试 MUST 不依赖模型下载或网络访问

### Requirement: Embedding learning record

本小节完成时 MUST 记录 embedding 生成的实现方式、验证结果和 provider 取舍。

#### Scenario: 完成 embeddings 小节

- **WHEN** embeddings 小节完成
- **THEN** 对应 OpenSpec change 的 `tasks.md` MUST 全部勾选
- **AND** `docs/agent-learning-todo.md` 中对应小节 MUST 勾选
- **AND** MUST 新增或更新学习总结文档
