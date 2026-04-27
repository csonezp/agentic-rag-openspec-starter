## Overview

本小节目标是实现“基础聊天调用”的最小闭环：用户输入 prompt，系统选择一个模型客户端，返回文本响应。

设计上继续沿用 Phase 0 的 `ModelClient` 协议，让 `HelloAgent` 不直接依赖 OpenAI SDK。真实 API 调用被隔离在新的 client 中，dry-run 继续作为默认和测试路径。

## 设计要点

- `HelloAgent` 只负责 prompt 校验和调用 `ModelClient.complete()`。
- `DryRunModelClient` 保持无网络、无 API Key 可运行。
- 新增真实 Responses API client 时，只做最小 `model + input` 请求。
- 脚本支持从命令行读取 prompt，未传入时使用默认 prompt。
- 脚本默认使用 dry-run；只有显式选择真实模式时才调用 OpenAI。

## 运行模式

建议使用环境变量或命令行参数控制：

- 默认：dry-run。
- `--real`：尝试真实 Responses API 调用。
- 无 `OPENAI_API_KEY` 且选择 `--real` 时，给出中文错误提示并退出。

## 测试策略

- 单元测试覆盖配置读取、prompt 输入、dry-run 行为和错误处理。
- 不在单元测试中调用真实网络。
- 真实调用通过手动脚本验证，且只在用户显式提供 API Key 和选择真实模式时发生。

## 不做事项

- 不做 streaming。
- 不做 structured output。
- 不做 tool calling。
- 不做 RAG。
- 不做复杂重试、限流或成本追踪。
