## Why

上一小节已经能把 Markdown 文档加载并标准化为稳定纯文本，但后续 embedding 和检索仍不能直接对整篇文档操作。进入基础 RAG 之前，需要把标准化文本切成更小的 chunks，并为每个 chunk 保留足够的来源元数据，方便后续引用、调试和检索过滤。

本小节用于学习“带元数据的文档切片”的最小边界：围绕本地 Markdown 知识源，把 `NormalizedDocument` 切分为可检索的 `DocumentChunk`，同时保留来源、标题、顺序和字符范围等基础元数据；不做 embedding 或向量库写入。

## What Changes

- 在 Phase 2 中推进“实现带元数据的文档切片”小节。
- 新增 chunk 数据结构，至少保留 `source_path`、`title`、`chunk_id`、`chunk_index`、`start_char`、`end_char` 和 `text`。
- 新增面向标准化文本的切片逻辑，支持固定 `chunk_size` 和 `overlap`。
- 新增文档级切片函数和演示脚本，用于查看 `knowledge/` 中样例文档的 chunk 结果。
- 新增测试和学习笔记，记录切片边界、元数据设计和后续与 embedding 的衔接点。

不做：

- 不生成 embeddings。
- 不写入向量数据库。
- 不做检索、rerank 或引用拼装。
- 不引入复杂的语义分块或基于标题树的高级切片策略。

## Capabilities

### New Capabilities

- `metadata-aware-chunking-learning`: 覆盖 Phase 2 带元数据的文档切片学习，包括 chunk 生成、chunk 元数据和切片边界规则。

### Modified Capabilities

- `learning-roadmap`: Phase 2 带元数据的文档切片小节完成状态会在本 change 完成后更新。

## Impact

- 可能新增 `DocumentChunk` 模块和切片演示脚本。
- 新增测试：覆盖 chunk 大小、overlap、顺序编号和元数据保留。
- 更新学习路线、OpenSpec 任务和学习笔记。
