# Phase 2 学习笔记：生成 embeddings

日期：2026-04-28

## 学习目标

本小节把前面生成的 `DocumentChunk` 转换为 embedding 向量，为后续“写入本地向量库”和“top-k 检索”做准备。

## Provider 取舍

本项目真实对话模型使用 DeepSeek 官方 API，但本小节没有把 DeepSeek 当作 embedding provider。原因是当前已验证的 DeepSeek 官方能力主要集中在 Chat Completions、JSON Output 和 Tool Calls；本小节重点是学习 embedding 生成的代码边界，而不是绑定某个云端 embedding 服务。

因此，本小节先实现本地 deterministic embedding：

- 不依赖网络。
- 不依赖 API Key。
- 单元测试完全可重复。
- 足够支撑后续向量库和检索流程学习。

这个本地实现不能代表真实语义质量。后续如果要做质量更好的检索，可以替换为 BGE、bge-m3、Qwen embedding、OpenAI embedding 或其他真实 embedding provider。

## 本小节实现

- 新增 `EmbeddingModel` 协议。
- 新增 `HashingEmbeddingModel`，把文本 token hash 到固定维度向量，并做 L2 normalization。
- 新增 `EmbeddedChunk`，把 `DocumentChunk` 和 embedding 绑定。
- 新增 `embed_chunk()` 和 `embed_chunks()`。
- 新增 `scripts/generate_embeddings.py`，串联加载、标准化、切片和 embedding 生成。

## 关键认知

- Embedding 是检索的中间表示，不是最终答案。
- Embedding 必须和 chunk metadata 绑定，否则后续无法引用来源。
- 本地 deterministic embedding 适合学习流程，但不适合代表生产检索质量。
- 向量维度应该是配置项，因为不同 embedding provider 的维度不同。

## 验证记录

- 单元测试覆盖稳定向量、维度、不同文本差异、chunk metadata 保留和演示脚本。
- 本地演示使用 `scripts/generate_embeddings.py knowledge`。
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` 通过，合计 92 个测试。
- `/opt/homebrew/bin/openspec validate --all --strict` 通过，合计 14 个 OpenSpec 校验项。
- `PYTHONPATH=src:. python3 scripts/generate_embeddings.py knowledge --chunk-size 400 --overlap 40 --dimensions 64` 生成 21 个 chunk 和 21 个 embedding，向量维度为 64。

## 后续问题

- 下一小节需要决定本地向量库的数据结构和相似度计算方式。
- 是否要把 embedding provider 抽成可配置项。
- 什么时候引入真实 embedding 模型来评估检索质量。
