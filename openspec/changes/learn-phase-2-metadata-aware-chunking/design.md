## Context

当前 `load_markdown_documents()` 已经能输出 `KnowledgeDocument`，`normalize_documents()` 已经能把 Markdown 标准化为 `NormalizedDocument`。下一步做 embedding 前，需要先把长文本切分为更稳定、可追踪的小块，否则后续检索会面临上下文过大、来源难以定位和引用难以回溯的问题。

本小节先实现“最小、可验证”的 chunking：对标准化文本做长度切片，并给每个 chunk 加上最基础的来源元数据。

## Goals / Non-Goals

**Goals:**

- 从 `NormalizedDocument` 生成 `DocumentChunk`。
- 保留最小可追溯元数据：`source_path`、`title`、`chunk_id`、`chunk_index`、`start_char`、`end_char`。
- 支持固定 `chunk_size` 和 `overlap`。
- 为后续 embedding 和引用提供稳定输入。
- 用本地 `knowledge/` 数据完成切片演示验证。

**Non-Goals:**

- 不做语义分块。
- 不做标题层级感知切片。
- 不做 embedding、向量库存储或检索。
- 不做多来源格式支持，先只面向现有 Markdown 标准化结果。

## Decisions

### Decision: 先用字符窗口切片

本小节先不用 token 级切片，也不引入外部 tokenizer。直接在标准化文本上实现固定字符窗口切片，优点是简单、可预测、测试成本低，足够支撑当前学习目标。

后续如果检索质量受影响，再在 Phase 3 或之后引入 token-aware / sentence-aware 的改进策略。

### Decision: chunk 元数据最小但可回溯

每个 chunk 至少保留：

- `source_path`
- `title`
- `chunk_id`
- `chunk_index`
- `start_char`
- `end_char`
- `text`

这样后续回答引用、调试输出和检索日志都能定位“这个 chunk 来自哪篇文档、是第几个 chunk、覆盖原文哪个字符范围”。

### Decision: overlap 先做固定步长

先用固定 overlap 实现最小版本，不做自适应 overlap。规则保持透明：

- 下一块起点 = `上一块终点 - overlap`
- overlap 必须小于 `chunk_size`

这样易于推导、也容易被测试锁住。

## Risks / Trade-offs

- [Risk] 字符切片可能把句子截断。→ 学习阶段先接受这个代价，后续再引入更高级切片策略。
- [Risk] 元数据过少导致后续引用能力不足。→ 当前先保留最小集合，后续如需要再加标题路径、更新时间或文档 id。
- [Risk] overlap 过大会制造重复上下文。→ 在演示脚本和测试里显式展示 chunk 边界，帮助观察实际效果。
