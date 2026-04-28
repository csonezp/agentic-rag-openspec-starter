# Proposal: 学习 Phase 2 的「在回答中包含来源引用」

## 为什么做

上一小节已经能把检索上下文交给模型生成回答，但回答本身还没有稳定的来源引用格式。知识库问答 Agent 如果不能说明依据来自哪里，用户很难判断答案是否可信，也无法回到原始文档复核。

本小节要学习的是“引用边界”：引用应该来自检索结果 metadata，而不是让模型自由编造；回答输出如何携带引用；CLI 如何展示答案和来源；后续拒答和评测如何复用这些结构。

## 做什么

- 定义来源引用对象，包含 `chunk_id`、`source_path`、`title`、`chunk_index` 和 score。
- 让 grounded answer 结果携带 citations。
- 调整 prompt，要求模型在可用时使用 `[chunk_id]` 标记引用。
- 调整回答脚本，输出 answer 后再输出 sources 列表。
- 支持 dry-run 和 DeepSeek 真实模式验证。

## 不做什么

- 不判断证据是否足够。
- 不在低分或无命中时拒答。
- 不实现引用正确性自动评测。
- 不做来源去重、metadata filter 或 rerank。

## 成功标准

- 回答结果对象包含 answer、contexts 和 citations。
- citations 从检索结果结构化生成，不依赖模型自由输出。
- CLI 输出中包含 sources 列表。
- 真实 DeepSeek 调用能看到 prompt 中的引用要求，并返回带引用标记或可对照 sources 的回答。
- 单元测试和 OpenSpec 严格校验通过。
