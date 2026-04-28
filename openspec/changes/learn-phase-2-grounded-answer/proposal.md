# Proposal: 学习 Phase 2 的「基于检索上下文生成回答」

## 为什么做

前面已经完成了文档加载、切片、embedding、本地向量库写入和 top-k chunks 检索。RAG 的下一步是把检索结果变成模型可用的上下文，让模型基于这些上下文回答用户问题。

本小节要学习的是“检索结果如何进入生成阶段”：上下文如何格式化、prompt 如何约束模型、脚本如何串联检索和生成，以及如何为后续来源引用和拒答留下结构化边界。

## 做什么

- 定义 grounded answer 的 prompt 结构。
- 把 top-k `SearchResult` 转换为模型上下文。
- 新增一个回答生成模块，接收问题、检索结果和模型 client。
- 新增演示脚本，串联问题 embedding、Qdrant top-k 检索和模型回答。
- 支持默认 dry-run，便于无 API Key 时验证上下文组装；支持 `--real` 调用 DeepSeek。

## 不做什么

- 不实现正式来源引用格式。
- 不实现证据弱时拒答策略。
- 不做答案质量评测。
- 不做 streaming 回答。
- 不做 metadata filter、hybrid search 或 rerank。

## 成功标准

- 能把 top-k 检索结果格式化为模型 prompt。
- dry-run 模式能展示完整上下文进入了回答生成链路。
- 真实模式能调用 DeepSeek 基于检索上下文生成回答。
- 单元测试覆盖 prompt 结构、回答模块和演示脚本。
- OpenSpec 严格校验通过。
