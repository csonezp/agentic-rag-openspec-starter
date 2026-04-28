# Design: 基于检索上下文生成回答

## 背景

当前查询链路已经能完成：

用户问题 → query embedding → Qdrant top-k chunks。

本小节新增生成链路：

top-k chunks → grounded prompt → 模型回答。

## 模块边界

计划新增 `agent_kb.grounded_answer`：

- `GroundedAnswerResult`：保存问题、回答和使用的检索结果。
- `build_grounded_prompt()`：把问题和检索结果格式化为 prompt。
- `GroundedAnswerer`：接收 `ModelClient`，根据检索结果生成回答。

计划新增脚本 `scripts/answer_with_context.py`：

- 接收问题。
- 使用 provider 生成 query embedding。
- 从本地 Qdrant 检索 top-k chunks。
- 将检索结果组装成 grounded prompt。
- 默认 dry-run，显式 `--real` 时调用 DeepSeek。

## Prompt 结构

prompt 包含三段：

- 任务说明：只能基于上下文回答，不要编造。
- 检索上下文：按 `[chunk_id] title / source_path` 组织文本。
- 用户问题：原始问题。

本小节不会要求模型输出正式来源引用；下一小节会专门处理引用格式。

## 验证策略

- 单元测试直接构造 `SearchResult`，验证 prompt 包含问题、chunk metadata 和文本。
- 用 fake model client 验证 `GroundedAnswerer` 传入的是 grounded prompt。
- CLI 测试使用 hashing provider 和临时 Qdrant 路径，避免真实模型和网络依赖。
- 真实演示使用 FastEmbed collection 和 DeepSeek。

## 风险与取舍

- prompt 中要求“只基于上下文回答”是一层软约束，不能替代后续拒答策略。
- dry-run 只能验证上下文组装，不代表真实回答质量。
- 如果检索结果质量差，生成回答也会受影响；这会在后续评测和检索质量提升阶段继续处理。
