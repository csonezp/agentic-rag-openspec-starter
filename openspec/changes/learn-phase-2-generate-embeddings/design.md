## Context

RAG 的检索阶段通常需要把文本 chunk 转成向量。向量不是最终答案，而是用于相似度检索的中间表示。当前项目已经有 `DocumentChunk`，它包含 `chunk_id`、`source_path`、`title`、字符范围和文本。

本小节的重点是建立 embedding 生成的代码边界，并补充一个可在本地运行的真实 embedding provider。

## Goals / Non-Goals

**Goals:**

- 定义 embedding 模型协议。
- 为每个 `DocumentChunk` 生成固定维度向量。
- 保留 chunk metadata，形成 `EmbeddedChunk`。
- 使用 deterministic 本地实现保证测试稳定。
- 使用 FastEmbed 接入真实本地 embedding 模型。
- 提供演示脚本串联加载、标准化、切片和 embedding。

**Non-Goals:**

- 不接入云端 embedding API。
- 不存储向量。
- 不实现检索。
- 不系统评估语义相似度质量。

## Decisions

### Decision: 使用本地 deterministic embedding

本小节保留 `HashingEmbeddingModel`。它把文本按 token 简单拆分，用 hash 将 token 映射到固定维度，并做 L2 normalization。优点是：

- 不依赖网络和 API Key。
- 单元测试完全可重复。
- 可以作为测试和离线演示兜底。

缺点是语义质量不如真实 embedding 模型。这个缺点会在学习笔记中明确记录。

### Decision: 使用 FastEmbed 作为真实本地 provider

本小节新增 `FastEmbedEmbeddingModel`，默认使用 `BAAI/bge-small-zh-v1.5`。选择它的原因是：

- 本地运行，不需要云端 API Key。
- 依赖相对轻量，适合当前学习项目。
- 默认模型对中文知识库更友好。
- 后续接入 Qdrant 或其他向量库时迁移成本低。

CLI 默认 provider 使用 `fastembed`；单元测试和无网络演示可以显式选择 `--provider hashing`。

### Decision: embedding 与 chunk metadata 绑定

`EmbeddedChunk` 保留原始 `DocumentChunk` 和 `embedding`。后续写入向量库时，可以直接取 chunk metadata 作为 payload。

### Decision: 向量维度可配置

FastEmbed 默认维度使用 512，匹配 `BAAI/bge-small-zh-v1.5`。Hashing provider 可以通过 `--dimensions` 使用更小维度，便于本地演示和测试。

## Risks / Trade-offs

- [Risk] 本地 hash embedding 不能代表真实语义质量。→ 明确作为学习和流程验证用，后续 provider 可替换。
- [Risk] FastEmbed 首次运行需要下载模型。→ 单元测试不依赖真实下载，真实演示单独执行。
- [Risk] tokenization 简单。→ 当前只做轻量拆分，后续检索质量提升阶段再优化。
- [Risk] 用户误以为 DeepSeek 已提供 embeddings。→ 文档明确记录本小节未使用 DeepSeek embedding provider。
