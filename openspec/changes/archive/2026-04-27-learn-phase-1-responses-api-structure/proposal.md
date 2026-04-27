## Why

Phase 1 的第一个学习小节是理解 Responses API 的请求和响应结构。这个小节需要先把官方概念、字段边界和最小示例沉淀下来，再决定后续如何接入真实模型调用，避免一上来就把 SDK、网络调用、工具调用和 RAG 混在一起。

## What Changes

- 创建一个学习型 OpenSpec change，用来追踪“Responses API 请求和响应结构”这个小节。
- 明确本小节只学习请求/响应结构，不实现完整模型客户端、不消耗 API token、不接入 RAG。
- 后续学习时会基于官方文档整理最小请求、响应对象、输入项、输出项和用量信息。
- 后续如果进入实验，会优先新增只读学习笔记或 dry-run 对照脚本。

## Capabilities

### New Capabilities

- `responses-api-structure-learning`: 记录 Responses API 请求/响应结构学习目标、验收标准和上下文恢复方式。

### Modified Capabilities

- 无。

## Impact

- 影响 `openspec/changes/learn-phase-1-responses-api-structure/` 下的学习 change 文档。
- 当前不修改生产代码、不安装依赖、不调用真实 OpenAI API。
- 官方参考文档：
  - [Responses API reference](https://platform.openai.com/docs/api-reference/responses)
  - [Responses API guide](https://developers.openai.com/api/docs/guides/responses)
