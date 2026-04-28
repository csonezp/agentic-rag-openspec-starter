# Design: 本地向量库写入

## 背景

当前项目已经具备文档加载、文本标准化、带 metadata 的 chunking，以及 FastEmbed / hashing 两种 embedding provider。下一步需要把 `EmbeddedChunk` 落到本地向量库中，让后续检索小节可以只关注“查询向量和 top-k 召回”，而不是重复处理索引写入细节。

## 方案选择

本小节推荐使用 Qdrant 的本地模式作为真实向量库学习对象。

选择 Qdrant 的原因：

- 它是生产中常见的向量数据库，概念和后续线上形态接近。
- Python client 支持本地使用，适合学习阶段不启动额外服务。
- payload 可以自然保存 chunk metadata 和文本。
- 后续 top-k 检索可以直接复用 collection、point 和 payload 概念。

不选择“自己写 JSONL 向量文件”作为主方案，是因为那更适合解释向量存储原理，但不够贴近真实 RAG 工程。Hashing provider 仍然用于测试，避免单元测试依赖模型下载。

## 模块边界

计划新增 `agent_kb.vector_store`：

- `VectorStoreConfig`：collection 名称、向量维度、本地存储路径。
- `StoredVector` 或等价结构：描述写入后的 point 信息。
- `LocalQdrantVectorStore`：封装 collection 初始化和批量 upsert。
- metadata 转换函数：把 `DocumentChunk` 转成 payload。

计划新增脚本 `scripts/index_knowledge_base.py`：

- 加载 `knowledge/` Markdown 文档。
- 标准化文本。
- 切片。
- 生成 embeddings。
- 写入本地 Qdrant collection。
- 输出 collection、chunks、points、dimensions、provider 等摘要。

## 数据结构

每个 chunk 写入一个 point：

- `id`：由 `chunk_id` 稳定生成，重复运行可以覆盖同一 point。
- `vector`：embedding 向量。
- `payload.chunk_id`
- `payload.source_path`
- `payload.title`
- `payload.chunk_index`
- `payload.start_char`
- `payload.end_char`
- `payload.text`

## 验证策略

- 单元测试使用 hashing embedding 和临时本地路径，验证 collection 初始化、metadata 保存和重复 upsert。
- 演示验证可以先使用 `--provider hashing` 保持快速稳定，再使用 `--provider fastembed` 做真实本地模型写入。
- OpenSpec 使用严格校验确认 change 文档完整。

## 风险与取舍

- Qdrant client 会增加依赖。这个成本可以接受，因为下一小节检索会直接复用。
- 本地 Qdrant 路径会产生运行数据，因此应写入 `data/` 或 `.local/` 并加入 git ignore。
- FastEmbed 首次运行需要模型下载，因此测试不依赖真实 FastEmbed。
