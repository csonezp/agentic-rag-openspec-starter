## Why

当前项目已经能调用模型、流式输出和生成结构化 JSON，但 Agent 仍然只能“说话”，不能调用外部能力。为了理解 Agent 与普通聊天机器人的关键差异，需要学习 function/tool calling，并接入一个本地只读函数。

本小节重点学习 DeepSeek Tool Calls 的基本执行闭环：模型提出 tool call，本地代码校验参数并执行函数，再把 tool 结果回传给模型生成最终回答。

## What Changes

- 在 Phase 1 中推进“添加 function/tool calling，并接入一个本地函数”小节。
- 新增一个只读本地函数，用于返回当前学习项目的 Phase 1 进度摘要。
- 扩展 DeepSeek 客户端，支持发送 `tools` 并解析模型返回的 `tool_calls`。
- 新增 tool calling 运行器，负责参数解析、工具 allowlist、执行本地函数和二次模型调用。
- 新增演示脚本，支持 dry-run 和真实 DeepSeek Tool Calls。
- 新增单元测试和学习笔记，记录模型不会执行函数、工具参数必须视为不可信输入。

不做：

- 不接入会修改状态的工具。
- 不接入外部服务、数据库或 MCP。
- 不实现多工具复杂规划；本小节只验证一个本地函数闭环。
- 不使用 DeepSeek strict mode beta；先学习基础非 strict tool calling。

## Capabilities

### New Capabilities

- `tool-calling-local-function-learning`: 覆盖本地函数 tool calling 学习，包括 tool schema、tool call 解析、本地函数执行和最终回答生成。

### Modified Capabilities

- `learning-roadmap`: Phase 1 tool calling 小节完成状态会在本 change 完成后更新。

## Impact

- 影响 DeepSeek 客户端：增加 tool calling 请求和响应解析能力。
- 新增本地工具模块和 tool calling runner。
- 新增演示脚本和测试。
- 更新学习路线、OpenSpec 任务和学习笔记。
