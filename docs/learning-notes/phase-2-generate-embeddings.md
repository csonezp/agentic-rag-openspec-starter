# Phase 2 学习笔记：生成 embeddings

日期：2026-04-28

## 学习目标

本小节把前面生成的 `DocumentChunk` 转换为 embedding 向量，为后续“写入本地向量库”和“top-k 检索”做准备。

## Provider 取舍

本项目真实对话模型使用 DeepSeek 官方 API，但本小节没有把 DeepSeek 当作 embedding provider。原因是当前已验证的 DeepSeek 官方能力主要集中在 Chat Completions、JSON Output 和 Tool Calls；本小节重点是学习 embedding 生成的代码边界，而不是绑定某个云端 embedding 服务。

因此，本小节保留本地 deterministic embedding：

- 不依赖网络。
- 不依赖 API Key。
- 单元测试完全可重复。
- 适合作为测试和离线演示兜底。

这个本地实现不能代表真实语义质量。为了在本小节完成真实本地模型对接，项目新增 FastEmbed provider，默认模型为 `BAAI/bge-small-zh-v1.5`。它不需要云端 API Key，适合中文知识库的本地语义向量生成。

## 本小节实现

- 新增 `EmbeddingModel` 协议。
- 新增 `HashingEmbeddingModel`，把文本 token hash 到固定维度向量，并做 L2 normalization。
- 新增 `FastEmbedEmbeddingModel`，包装 FastEmbed 的 `TextEmbedding`，默认使用 `BAAI/bge-small-zh-v1.5`。
- 新增 `EmbeddedChunk`，把 `DocumentChunk` 和 embedding 绑定。
- 新增 `embed_chunk()` 和 `embed_chunks()`。
- 新增 `scripts/generate_embeddings.py`，串联加载、标准化、切片和 embedding 生成；默认使用 `fastembed`，也可以通过 `--provider hashing` 使用 deterministic provider。

## 关键认知

- Embedding 是检索的中间表示，不是最终答案。
- Embedding 必须和 chunk metadata 绑定，否则后续无法引用来源。
- 本地 deterministic embedding 适合学习流程，但不适合代表生产检索质量。
- 真实本地 embedding provider 首次运行通常需要下载模型，因此不要让单元测试依赖真实模型下载。
- 向量维度应该是配置项，因为不同 embedding provider 的维度不同。

## 验证记录

- 单元测试覆盖稳定向量、维度、不同文本差异、chunk metadata 保留和演示脚本。
- 本地演示使用 `scripts/generate_embeddings.py knowledge`。
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` 通过，合计 92 个测试。
- `/opt/homebrew/bin/openspec validate --all --strict` 通过，合计 14 个 OpenSpec 校验项。
- `PYTHONPATH=src:. python3 scripts/generate_embeddings.py knowledge --chunk-size 400 --overlap 40 --dimensions 64` 生成 21 个 chunk 和 21 个 embedding，向量维度为 64。
- FastEmbed provider 补充测试先失败于 `FastEmbedEmbeddingModel` 不存在，随后实现 provider 后通过。
- 安装 `fastembed` 后，`PYTHONPATH=src:. python3 scripts/generate_embeddings.py knowledge --chunk-size 400 --overlap 40` 使用 `BAAI/bge-small-zh-v1.5` 生成 21 个 chunk 和 21 个 embedding，向量维度为 512。
- 首次运行 FastEmbed 需要下载模型；当前环境需要联网权限。运行时还出现 `urllib3` 关于系统 LibreSSL 版本的提示，但不影响本次模型下载和 embedding 生成。
- 补充 FastEmbed provider 后，`PYTHONPATH=src:. python3 -m unittest discover -s tests` 通过，合计 94 个测试；`/opt/homebrew/bin/openspec validate --all --strict` 仍为 14 个校验项全部通过。

## 后续问题

- 下一小节需要决定本地向量库的数据结构和相似度计算方式。
- 后续需要决定是否引入 reranker 来提升检索质量。
- 后续需要补充检索评估集，用真实问题衡量 embedding 效果。
