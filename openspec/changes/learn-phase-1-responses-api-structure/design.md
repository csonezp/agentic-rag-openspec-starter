## Overview

本 change 采用“先学习结构，再写实验”的方式推进。第一步只创建可追溯上下文，明确学习范围、材料来源和完成标准；等用户确认后，再进入具体学习笔记、示例请求和代码实验。

## 学习范围

本小节关注 Responses API 的结构认知：

- 请求入口：`POST /v1/responses`。
- 请求核心字段：`model`、`input`、`instructions`、`previous_response_id`、`tools`、`include`、`max_output_tokens`、`metadata` 等。
- 输入形态：简单字符串输入，以及带 `role`、`content`、`input_text` 的结构化输入项。
- 响应核心字段：`id`、`status`、`output`、`usage`、`error`、`incomplete_details`、`created_at` 等。
- 输出形态：输出项列表、消息内容、文本输出，以及后续工具调用输出的扩展位置。
- 辅助接口：按 `response_id` 查看 input items，以及 input token count。

## 不在本小节处理

- 不实现完整 OpenAI SDK client。
- 不做 streaming。
- 不做 structured output。
- 不做 function/tool calling。
- 不接入 RAG 或知识库检索。
- 不设计生产级错误处理和重试。

这些会在 Phase 1 后续小节中分别创建独立 change。

## 学习产出设计

用户确认继续后，建议产出：

- `docs/learning-notes/phase-1-responses-api-structure.md`：中文学习笔记。
- 一个最小请求/响应结构对照表。
- 一个 dry-run JSON 示例，用于理解字段层级，不访问真实 API。
- 如果用户提供 API Key 并确认真实调用，再补一个最小真实请求脚本；否则不做真实调用。

## 官方依据

OpenAI 官方 API reference 说明 Responses API 用于生成模型响应，支持文本/图像输入、文本或 JSON 输出、会话状态和工具扩展；创建响应的端点是 `POST /v1/responses`。官方文档还说明 `input` 可以是文本或结构化输入项，`instructions` 用于插入系统或开发者消息，response object 中包含响应 id、状态、输出、错误和用量等信息。

参考：

- [Responses API reference](https://platform.openai.com/docs/api-reference/responses)
- [Responses API guide](https://developers.openai.com/api/docs/guides/responses)
