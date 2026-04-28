# Phase 2 学习笔记：基于检索上下文生成回答

日期：2026-04-28

## 学习目标

本小节把 top-k 检索结果转换为模型可用的上下文 prompt，并调用模型生成回答。

本小节只负责“让检索上下文进入生成阶段”。正式来源引用和证据弱时拒答会在后续两个小节单独处理。

## 本小节实现

- 新增 `GroundedAnswerResult`，保存问题、回答和使用的检索上下文。
- 新增 `build_grounded_prompt()`，把问题和 `SearchResult` 列表格式化成 grounded prompt。
- 新增 `GroundedAnswerer`，把 grounded prompt 发送给模型 client。
- 新增 `scripts/answer_with_context.py`，串联 query embedding、Qdrant top-k 检索和回答生成。
- 脚本默认 dry-run，显式 `--real` 时调用 DeepSeek。

## Prompt 结构

当前 prompt 包含：

- 助手角色说明。
- “只能基于给定上下文回答”的约束。
- 检索上下文列表，每条包含 `chunk_id`、标题、来源路径、chunk 序号、score 和文本。
- 用户问题。
- 回答位置。

这个 prompt 不是安全边界，只是生成阶段的一层约束。后续仍需要来源引用、拒答策略和评测来提升可信度。

## 关键认知

- RAG 的生成阶段不是简单把所有文档塞给模型，而是把检索到的少量 chunks 组织成清晰上下文。
- 检索结果必须保留 metadata，否则后续无法做来源引用。
- dry-run 可以验证上下文组装是否正确，但不能代表真实模型回答质量。
- 如果检索结果不相关，grounded prompt 也会把错误上下文交给模型，因此后续需要检索评测。

## 验证记录

- grounded answer 测试先失败于 `agent_kb.grounded_answer` 不存在，随后实现模块和脚本后通过。
- `PYTHONPATH=src:. python3 -m unittest tests.test_grounded_answer` 通过，合计 4 个测试。
- `PYTHONPATH=src:. python3 scripts/answer_with_context.py "Agent RAG 是什么？" --vector-store-path data/qdrant-hashing-demo --collection-name knowledge_chunks_hashing --provider hashing --dimensions 64 --top-k 2` 使用 dry-run 完成验证，输出 2 条检索上下文，并把上下文完整放入回答 prompt。
- `PYTHONPATH=src:. python3 scripts/answer_with_context.py "如何记录模型调用的延迟和 token？" --vector-store-path data/qdrant-fastembed-demo --collection-name knowledge_chunks_fastembed --provider fastembed --top-k 2 --real` 使用 FastEmbed + DeepSeek 完成真实验证，返回基于上下文的回答，并输出 `latency_ms` 与 token usage observation。
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` 通过，合计 108 个测试。
- `/opt/homebrew/bin/openspec validate --all --strict` 通过，合计 17 个 OpenSpec 校验项。

## 后续问题

- 下一小节需要把回答中的来源引用格式标准化。
- 再下一小节需要处理证据弱、无命中或低分命中时的拒答策略。
- 后续评测需要同时检查回答是否基于上下文、是否引用正确来源。
