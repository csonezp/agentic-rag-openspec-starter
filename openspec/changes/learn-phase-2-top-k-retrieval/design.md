# Design: top-k chunks 检索

## 背景

当前项目已经具备完整的索引链路：

文档加载 → 标准化 → 切片 → embedding → 写入本地 Qdrant。

本小节在这个基础上新增查询链路：

用户问题 → query embedding → Qdrant search → top-k chunks。

## 模块边界

计划扩展 `agent_kb.vector_store`：

- `SearchResult`：检索结果对象，包含 score、chunk metadata 和文本。
- `LocalQdrantVectorStore.search()`：接收 query embedding 和 `top_k`，返回按 score 排序的结果。

计划新增 `scripts/retrieve_top_k.py`：

- 接收用户问题。
- 创建 embedding provider。
- 连接本地 Qdrant collection。
- 对问题生成 query embedding。
- 检索 top-k chunks。
- 打印 score、来源和文本预览。

## 数据流

1. 用户输入问题。
2. 使用与索引时相同的 embedding provider 生成 query embedding。
3. 调用 Qdrant collection 做向量搜索。
4. 从 point payload 还原 chunk metadata 和文本。
5. 输出 top-k 检索结果。

## 关键约束

- query embedding 维度必须和 collection 维度一致。
- 检索时必须使用与索引时兼容的 provider 和模型。
- 本小节只返回检索结果，不把结果塞进 prompt，也不生成回答。

## 验证策略

- 单元测试使用 hashing provider 和临时 Qdrant 本地路径。
- 先写入几个测试 chunks，再用 query embedding 搜索 top-k。
- 演示验证使用上一小节的本地数据，分别跑 hashing 和 FastEmbed collection。

## 风险与取舍

- Hashing provider 的检索语义不可靠，只用于结构和流程验证。
- FastEmbed 检索结果更接近真实语义，但仍然需要后续评测集量化质量。
- Qdrant 的 score 含义和 distance 配置相关，本项目当前使用 cosine score。
