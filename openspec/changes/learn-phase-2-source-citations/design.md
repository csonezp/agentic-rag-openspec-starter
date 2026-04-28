# Design: 回答来源引用

## 背景

当前 grounded answer 链路已经能完成：

用户问题 → top-k chunks → grounded prompt → 模型回答。

本节新增引用链路：

top-k chunks → citations → answer + sources。

## 模块边界

计划扩展 `agent_kb.grounded_answer`：

- `SourceCitation`：结构化来源引用。
- `citations_from_contexts()`：从 `SearchResult` 生成 citations。
- `GroundedAnswerResult.citations`：回答结果显式携带来源。
- `build_grounded_prompt()`：要求模型使用 `[chunk_id]` 形式标记依据。

计划调整 `scripts/answer_with_context.py`：

- 输出 `sources:` 列表。
- 每条来源包含 `chunk_id`、`source_path`、`title`、`chunk_index` 和 score。

## 引用格式

模型回答中的引用建议使用：

```text
...回答内容...[observability.md#0]
```

CLI 的结构化 sources 使用：

```text
sources:
- chunk_id=observability.md#0 source_path=observability.md title=模型调用可观测性 chunk_index=0 score=0.703202
```

模型可能不稳定输出引用标记，因此结构化 citations 仍由代码从检索结果生成。下一阶段评测会再检查“回答中引用是否正确”。

## 验证策略

- 单元测试直接构造 `SearchResult`，验证 citations 字段和 prompt 引用要求。
- CLI 测试使用 hashing provider 和临时 Qdrant。
- 真实演示使用 FastEmbed + DeepSeek，并打开 `--show-prompt`。

## 风险与取舍

- 本小节不强制模型一定输出引用标记，只把引用要求放进 prompt，并由程序稳定输出 sources。
- 不做来源去重，top-k 命中同一文档的多个 chunk 时会逐条展示。
- 不判断是否应该拒答；低质量来源仍会输出，下一小节专门处理证据弱时拒答。
