# Phase 2 学习笔记：在回答中包含来源引用

日期：2026-04-28

## 学习目标

本小节让 grounded answer 输出结构化来源引用，使回答可以回到检索到的 chunk 进行复核。

本小节只处理“来源引用”，不处理证据弱时拒答，也不做引用正确性自动评测。

## 本小节实现

- 新增 `SourceCitation`，保存 `chunk_id`、`source_path`、`title`、`chunk_index` 和 score。
- 新增 `citations_from_contexts()`，从 `SearchResult` 稳定生成 citations。
- `GroundedAnswerResult` 新增 `citations` 字段。
- `build_grounded_prompt()` 要求模型尽量使用 `[chunk_id]` 标记依据。
- `scripts/answer_with_context.py` 在 answer 后输出结构化 `sources:` 列表。

## 引用边界

模型回答里的 `[chunk_id]` 是 prompt 约束，可能不稳定；结构化 `sources:` 是程序根据检索结果生成的，更可靠。

当前策略是两层并存：

- prompt 中要求模型在回答中尽量标注 `[chunk_id]`。
- CLI 稳定输出 `sources:`，方便用户看到本次回答用到了哪些检索上下文。

## 关键认知

- 来源引用不应该让模型自由编造，必须来自检索结果 metadata。
- 引用和拒答是两个不同问题：有来源不代表证据足够。
- top-k 命中同一文档的多个 chunk 时，本小节会逐条展示，暂不做来源去重。
- 后续评测需要检查回答内容是否真的由 sources 支撑。

## 验证记录

- citation 测试先失败于 `SourceCitation` 不存在，随后实现 citation 对象和 sources 输出后通过。
- `PYTHONPATH=src:. python3 -m unittest tests.test_grounded_answer` 通过，合计 6 个测试。
- `PYTHONPATH=src:. python3 scripts/answer_with_context.py "Agent RAG 是什么？" --vector-store-path data/qdrant-hashing-demo --collection-name knowledge_chunks_hashing --provider hashing --dimensions 64 --top-k 2 --show-prompt` 使用 dry-run 完成验证，输出 `sources:` 列表。
- `PYTHONPATH=src:. python3 scripts/answer_with_context.py "如何记录模型调用的延迟和 token？" --vector-store-path data/qdrant-fastembed-demo --collection-name knowledge_chunks_fastembed --provider fastembed --top-k 2 --show-prompt --real` 使用 FastEmbed + DeepSeek 完成真实验证，模型回答中包含 `[observability.md#0]` 和 `[observability.md#1]` 引用标记，脚本输出结构化 `sources:`。
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` 通过，合计 110 个测试。
- `/opt/homebrew/bin/openspec validate --all --strict` 通过，合计 18 个 OpenSpec 校验项。

## 后续问题

- 下一小节需要在检索证据较弱时拒答。
- 后续需要评估回答中的引用标记是否和结构化 sources 一致。
- 后续可以考虑来源去重和更友好的引用展示格式。
