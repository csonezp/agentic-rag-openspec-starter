# Proposal: 学习 Phase 2 的「针对问题检索 top-k chunks」

## 为什么做

上一小节已经能把知识库 chunks 和 embeddings 写入本地 Qdrant。RAG 的下一步是把用户问题转换为 query embedding，并从向量库中召回最相关的 top-k chunks。

本小节要学习的是检索边界：query 如何 embedding、如何调用向量库搜索、检索结果包含什么信息、score 如何展示，以及如何为后续“基于检索上下文生成回答”和“来源引用”留下结构化输入。

## 做什么

- 定义检索结果对象，包含 chunk metadata、文本和相似度 score。
- 在本地 Qdrant 向量库上实现 top-k 检索。
- 提供一个演示脚本，对问题生成 embedding 并检索 top-k chunks。
- 支持 hashing provider 的快速测试路径和 FastEmbed provider 的真实本地检索路径。
- 记录检索结果结构、验证命令和后续衔接点。

## 不做什么

- 不调用大模型生成最终回答。
- 不做来源引用格式化。
- 不做证据强弱判断或拒答。
- 不做 metadata filter、hybrid search、BM25 或 rerank。
- 不引入远程向量数据库服务。

## 成功标准

- 能对一个自然语言问题从本地 Qdrant collection 中检索 top-k chunks。
- 检索结果包含 `chunk_id`、`source_path`、`title`、`chunk_index`、文本预览和 score。
- 单元测试覆盖检索结果结构和 top-k 行为。
- hashing provider 和 FastEmbed provider 都能完成演示验证。
- OpenSpec 严格校验通过。
