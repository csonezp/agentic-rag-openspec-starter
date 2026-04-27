# Phase 1 设计

## 技术方案

在现有 `ModelClient` 协议的基础上扩展真实模型客户端，而不是把 OpenAI SDK 调用散落在脚本里。这样后续 RAG、评测和工具调用都可以复用同一层抽象。

建议新增或演进以下模块：

- `agent_kb.config`：继续负责模型名、API Key、运行模式等配置。
- `agent_kb.hello_agent`：保持教学入口和 dry-run 示例。
- `agent_kb.model_client`：封装真实模型调用、结构化输出、流式输出和工具调用示例。
- `scripts/`：提供可手动运行的学习脚本。
- `tests/`：优先测试配置、协议、无网络路径和本地工具逻辑。

## 运行模式

- dry-run：默认可运行，不需要 API Key。
- real：检测到 `OPENAI_API_KEY` 或显式参数后调用真实模型。

## 测试策略

- 单元测试不依赖真实网络。
- 真实模型调用通过脚本手动验证，避免 CI 或本地测试消耗 token。
- 对工具调用示例，优先测试本地函数和参数校验。

## 风险与取舍

- OpenAI SDK 版本会变化，因此模型客户端需要尽量薄，避免过早抽象。
- 本阶段先学 Responses API 的基本能力，不急着接 LangGraph。
- 如果本地没有包管理工具或网络，先保留 dry-run 和文档任务，真实 SDK 安装留到有环境时执行。
