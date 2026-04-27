## Why

上一小节已经建立了 Responses API 请求和响应结构的心智模型。现在需要把这个结构落到一个最小“基础聊天调用”入口上，让项目从固定 dry-run 演示，演进到可输入 prompt、可选择 dry-run 或真实调用的学习样例。

## What Changes

- 创建学习小节 change `learn-phase-1-basic-chat-call`。
- 在现有 `ModelClient` 抽象基础上，扩展一个面向基础聊天调用的最小接口。
- 保留 dry-run 作为默认路径，确保无 API Key、无网络时仍可学习和测试。
- 增加命令行 prompt 输入能力，不再只依赖脚本内写死的 prompt。
- 增加真实 Responses API 调用的最小实现边界，但真实调用只在配置 API Key 且显式选择时发生。
- 更新中文学习笔记、任务状态和测试。

## Capabilities

### New Capabilities

- `basic-chat-call-learning`: 记录 Phase 1 基础聊天调用小节的学习目标、最小行为和验证方式。

### Modified Capabilities

- 无。

## Impact

- 可能影响 `src/agent_kb/` 下的模型客户端和 Agent 入口代码。
- 可能影响 `scripts/hello_model.py`，让它支持命令行 prompt 和运行模式。
- 可能新增测试和学习笔记。
- 不接入 streaming、structured output、tool calling 或 RAG。
