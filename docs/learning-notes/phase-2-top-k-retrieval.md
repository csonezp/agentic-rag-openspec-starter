# Phase 2 学习笔记：针对问题检索 top-k chunks

日期：2026-04-28

## 学习目标

本小节把用户问题转换为 query embedding，并从本地 Qdrant collection 中检索最相关的 top-k chunks。

本小节只负责检索，不负责把检索结果交给模型生成回答，也不负责来源引用格式化或拒答判断。

## 本小节实现

- 新增 `SearchResult`，保存 `score`、chunk metadata 和 chunk 文本。
- 在 `LocalQdrantVectorStore` 中新增 `search()`。
- 新增 `scripts/retrieve_top_k.py`，支持输入问题、provider、collection、top-k 和文本预览长度。
- 检索脚本支持 `hashing` 和 `fastembed` 两种 provider。

## 数据流

1. 用户输入问题。
2. 使用和索引阶段兼容的 embedding provider 生成 query embedding。
3. 调用 Qdrant `query_points`。
4. 从返回 point 的 payload 中恢复 chunk metadata 和文本。
5. 输出 score、来源和文本预览。

## 关键认知

- 检索阶段必须使用与索引阶段兼容的 embedding provider 和模型，否则向量空间不一致，结果没有意义。
- query embedding 维度必须等于 collection 维度；当前代码会在维度不一致时报错。
- Qdrant 当前使用 cosine distance，返回的 score 可以用于排序和调试，但是否“足够可信”要等后续拒答小节再处理。
- Hashing provider 只适合验证结构流程；FastEmbed provider 的结果更接近真实语义检索。

## 验证记录

- top-k 检索测试先失败于 `SearchResult` 不存在，随后实现检索对象、`search()` 和检索脚本后通过。
- `PYTHONPATH=src:. python3 -m unittest tests.test_vector_store` 通过，合计 10 个测试。
- `PYTHONPATH=src:. python3 scripts/retrieve_top_k.py "Agent RAG 是什么？" --vector-store-path data/qdrant-hashing-demo --collection-name knowledge_chunks_hashing --provider hashing --dimensions 64 --top-k 3` 返回 3 条结果，第一条为 `agent-concepts.md#0`。
- `PYTHONPATH=src:. python3 scripts/retrieve_top_k.py "如何记录模型调用的延迟和 token？" --vector-store-path data/qdrant-fastembed-demo --collection-name knowledge_chunks_fastembed --provider fastembed --top-k 3` 返回 3 条结果，前两条为 `observability.md#0` 和 `observability.md#1`。
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` 通过，合计 104 个测试。
- `/opt/homebrew/bin/openspec validate --all --strict` 通过，合计 16 个 OpenSpec 校验项。

## 后续问题

- 下一小节需要把检索结果组织成回答上下文。
- 后续来源引用需要复用 `chunk_id`、`source_path`、`title` 和 `chunk_index`。
- 后续拒答需要基于 score、命中数量和问题类型设计证据强弱判断。
