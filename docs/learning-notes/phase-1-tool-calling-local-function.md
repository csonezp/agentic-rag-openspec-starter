# Phase 1 学习笔记：function/tool calling 与本地函数

日期：2026-04-27

## 学习目标

本小节学习模型如何通过 Tool Calls 请求调用外部函数，并由本地代码完成函数执行。我们接入了一个只读本地函数 `get_phase1_progress`，用于返回当前 Phase 1 学习进度。

## DeepSeek Tool Calls 观察

DeepSeek Tool Calls 的关键流程是：

1. 本地代码把 `tools` 定义随用户消息一起发给模型。
2. 模型返回 `tool_calls`，其中包含函数名和 arguments。
3. 本地代码校验函数名和 arguments。
4. 本地代码执行函数，并把结果作为 `role=tool` 消息回传给模型。
5. 模型基于工具结果生成最终自然语言回答。

重要认知：模型不会执行函数。模型只是提出“我想调用哪个函数、参数是什么”。真正执行函数的是我们的代码。

## 本小节实现

- 新增 `get_phase1_progress()` 只读本地函数。
- 新增 `get_phase1_progress_tool()`，描述函数 schema。
- 新增 `ToolCallingRunner`，负责工具 allowlist、参数解析、本地函数执行和二次模型调用。
- 扩展 `DeepSeekChatCompletionsModelClient.create_chat_completion()`，支持发送 `tools` 并返回 assistant message。
- 新增 `scripts/tool_calling_demo.py`，默认 dry-run，`--real` 时调用 DeepSeek Tool Calls。

## 安全边界

- 模型生成的工具名和 arguments 都是不可信输入。
- 只允许调用 allowlist 中注册的工具。
- arguments 必须能解析为 JSON object。
- 当前工具不接受任何参数；如果模型生成了参数，本地 runner 会拒绝。
- 本小节只接入只读函数，不开放写操作。

## 验证记录

- 单元测试覆盖 tools 请求体、tool call 解析、未知工具拒绝、非法 arguments 拒绝、runner 闭环和演示脚本。
- 单元测试验证命令：`PYTHONPATH=src:. python3 -m unittest discover -s tests`，结果为 38 个测试通过。
- OpenSpec 验证命令：`/opt/homebrew/bin/openspec validate --all --strict`，结果为 9 项通过。
- 真实 DeepSeek Tool Calls 验证使用 `scripts/tool_calling_demo.py --real`，模型返回 tool call，本地执行 `get_phase1_progress`，再由模型基于工具结果生成最终回答。

## 后续问题

- 后续是否启用 DeepSeek strict mode beta。
- 多工具场景下如何做权限、审计和错误恢复。
- 何时把本地函数升级为 MCP tool。
