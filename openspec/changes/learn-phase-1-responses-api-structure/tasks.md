# 任务清单

## 1. 启动学习小节

- [x] 确认该小节尚未完成。
- [x] 创建 OpenSpec change `learn-phase-1-responses-api-structure`。
- [x] 写明学习目标、不做事项和完成标准。

## 2. 官方文档研读

- [x] 阅读 Responses API reference 中 create response 的请求字段。
- [x] 阅读 response object 的核心字段。
- [x] 阅读 input item list 和 input token count 的用途。
- [x] 整理请求结构和响应结构的最小字段表。

## 3. 学习笔记

- [x] 创建中文学习笔记。
- [x] 写出最小请求 JSON 示例。
- [x] 写出典型 response object 层级说明。
- [x] 标注和 Chat Completions 心智模型的差异。

## 4. 可选实验

- [x] 如用户确认，只添加 dry-run JSON 对照示例。
- [x] 确认本小节不添加真实 API 最小调用脚本，真实调用留到后续小节或用户明确要求时再做。

## 5. 完成收尾

- [x] 更新 `docs/agent-learning-todo.md` 中对应小节状态。
- [x] 更新本 change 的任务状态和学习结论。
- [x] 运行 OpenSpec 严格校验。
- [x] 运行现有测试，确认项目基础链路未受影响。

## 学习结论

- Responses API 的请求核心是 `model` 和 `input`，`input` 可以从简单字符串逐步演进为结构化 input item list。
- 响应核心不应只看“文本字符串”，而应理解为 response object，其中 `output` 是 item list，`usage`、`status`、`error`、`incomplete_details` 都是后续工程化需要关注的字段。
- `input_items` 和 `input_tokens` 是后续调试上下文和估算成本的重要辅助接口。
- 与 Chat Completions 相比，Responses API 更适合 Agent 场景，因为它天然围绕 response object、output items、工具扩展和会话状态组织。
- 本小节不做真实 API 调用；真实调用脚本留到下一个小节或用户明确要求时再做。
