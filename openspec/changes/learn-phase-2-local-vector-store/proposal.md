# Proposal: 学习 Phase 2 的「把向量存入本地向量库」

## 为什么做

上一小节已经能把知识库文档转换为 `EmbeddedChunk`，但这些向量目前只存在于脚本运行过程里。真正的 RAG 检索需要把 embedding 和 chunk metadata 写入可查询的向量库，否则后续无法稳定执行 top-k 检索、来源引用和拒答判断。

本小节要学习的是“向量库边界”本身：向量如何组织、metadata 如何保存、collection 如何初始化、重复写入如何处理，以及如何为下一小节的 top-k 检索留下清晰接口。

## 做什么

- 选择一个本地向量库方案作为学习实现。
- 定义向量库写入接口，接收 `EmbeddedChunk`。
- 把 embedding、chunk 文本和 chunk metadata 一起写入本地向量库。
- 提供一个演示脚本，从 `knowledge/` 生成 embeddings 并写入本地向量库。
- 为写入行为补充单元测试和学习笔记。

## 不做什么

- 不实现问题检索 top-k chunks。
- 不生成最终回答。
- 不做 hybrid search、rerank 或检索质量评估。
- 不引入远程向量数据库服务。
- 不处理多租户、权限隔离或后台索引任务。

## 成功标准

- 能运行一个本地命令，把 `knowledge/` 的 chunks 和 embeddings 写入本地向量库。
- 写入结果包含向量、chunk 文本、`chunk_id`、`source_path`、`title`、`chunk_index`、字符范围等 metadata。
- 重复运行命令不会因为相同 chunk 反复写入而产生不可控重复数据。
- 单元测试通过。
- OpenSpec 严格校验通过。
- 学习笔记记录本小节的向量库选型、数据结构、验证命令和后续衔接点。
