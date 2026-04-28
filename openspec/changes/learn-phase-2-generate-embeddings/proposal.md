## Why

Phase 2 已经完成文档加载、文本标准化和带元数据切片。下一步需要把 chunks 转换为 embeddings，才能进入向量存储和 top-k 检索。

当前真实对话模型使用 DeepSeek，但 DeepSeek 官方文档当前主要提供 Chat Completions、JSON Output 和 Tool Calls，没有将 embeddings 作为本项目已验证的官方能力。因此本小节先实现可重复的本地 deterministic embedding，用于学习向量化接口、数据结构和后续检索流程，后续可替换为真实 embedding provider。

## What Changes

- 在 Phase 2 中推进“生成 embeddings”小节。
- 新增 embedding 模型协议和本地 deterministic embedding 实现。
- 新增 `EmbeddedChunk` 对象，把 chunk metadata 和向量绑定。
- 新增批量生成 chunk embeddings 的函数。
- 新增演示脚本，加载 `knowledge/`、标准化、切片并生成 embeddings 摘要。
- 新增测试和学习笔记，记录为什么本小节不使用 DeepSeek 作为 embedding provider。

不做：

- 不接入向量库；这是下一小节“把向量存入本地向量库”的内容。
- 不实现真实云端 embedding API。
- 不做 top-k 检索。
- 不做 embedding 质量评估。

## Capabilities

### New Capabilities

- `embedding-generation-learning`: 覆盖 chunk embeddings 生成学习，包括 embedding 接口、可重复本地向量、metadata 保留和演示验证。

### Modified Capabilities

- `learning-roadmap`: Phase 2 embeddings 小节完成状态会在本 change 完成后更新。

## Impact

- 新增 embeddings 模块和演示脚本。
- 新增测试：覆盖稳定向量、维度、metadata 保留和脚本输出。
- 更新学习路线、OpenSpec 任务和学习笔记。
