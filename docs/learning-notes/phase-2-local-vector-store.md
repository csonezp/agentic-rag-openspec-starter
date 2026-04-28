# Phase 2 学习笔记：把向量存入本地向量库

日期：2026-04-28

## 学习目标

本小节把上一小节生成的 `EmbeddedChunk` 写入本地 Qdrant 向量库，为后续 top-k 检索做准备。

## 选型

本小节使用 Qdrant 本地模式，而不是 ChromaDB 或自己写 JSONL 文件。

选择 Qdrant 的原因：

- Qdrant 的 collection、point、vector、payload 概念更贴近生产向量数据库。
- Python client 支持 `path=...` 的本地磁盘模式，不需要启动额外服务。
- payload 可以保存 chunk 文本、来源路径、标题、chunk 序号和字符范围。
- 后续学习 top-k 检索、metadata filter、服务化部署时可以复用这些概念。

ChromaDB 仍然是合理选择，尤其适合快速 RAG 原型；本项目当前更偏向学习可迁移到生产形态的 RAG 工程边界。

## 本小节实现

- 新增 `VectorStoreConfig`，记录本地路径、collection 名称和向量维度。
- 新增 `LocalQdrantVectorStore`，封装 Qdrant 本地 collection 初始化、批量 upsert、count 和按 `chunk_id` 取回。
- 新增 `chunk_payload()`，把 `DocumentChunk` 转成 Qdrant payload。
- 新增 `stable_point_id()`，使用 `uuid5` 从 `chunk_id` 生成稳定 Qdrant point id。
- 新增 `scripts/index_knowledge_base.py`，串联加载、标准化、切片、embedding 生成和本地向量库写入。

## 数据结构

每个 chunk 写入一个 Qdrant point：

- `id`：由 `chunk_id` 稳定生成的 UUID 字符串。
- `vector`：embedding 向量。
- `payload.chunk_id`
- `payload.source_path`
- `payload.title`
- `payload.chunk_index`
- `payload.start_char`
- `payload.end_char`
- `payload.text`

稳定 point id 的意义是：重复运行索引脚本时，同一个 chunk 会执行 upsert 覆盖，而不是不断追加重复数据。

## 关键认知

- 向量库不只保存向量，还必须保存能支撑回答引用的 payload。
- Qdrant 使用 `Distance.COSINE` 时，读回向量可能是归一化后的值；检索语义不受影响。
- 本地向量库运行数据属于生成产物，应该放入 `data/` 并加入 `.gitignore`。
- 单元测试使用 hashing provider，避免依赖 FastEmbed 模型下载。

## 验证记录

- 向量库测试先失败于 `agent_kb.vector_store` 不存在，随后实现模块后通过。
- 当前系统 Python 为 3.9，`qdrant-client>=1.17` 要求 Python 3.10+，因此依赖锁定为 `qdrant-client>=1.16.1,<1.17`。
- `PYTHONPATH=src:. python3 scripts/index_knowledge_base.py knowledge --vector-store-path data/qdrant-hashing-demo --collection-name knowledge_chunks_hashing --provider hashing --dimensions 64 --chunk-size 400 --overlap 40` 写入 21 个 chunk，对应 21 个 Qdrant point，向量维度为 64。
- `PYTHONPATH=src:. python3 scripts/index_knowledge_base.py knowledge --vector-store-path data/qdrant-fastembed-demo --collection-name knowledge_chunks_fastembed --provider fastembed --chunk-size 400 --overlap 40` 写入 21 个 chunk，对应 21 个 Qdrant point，向量维度为 512。
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` 通过，合计 100 个测试。
- `/opt/homebrew/bin/openspec validate --all --strict` 通过，合计 15 个 OpenSpec 校验项。

## 后续问题

- 下一小节需要用同一个 Qdrant collection 实现问题向量检索 top-k chunks。
- 需要决定检索结果的数据结构：至少包含 chunk、score 和 payload。
- 后续可以加入 metadata filter，例如只检索某个来源或某类文档。
