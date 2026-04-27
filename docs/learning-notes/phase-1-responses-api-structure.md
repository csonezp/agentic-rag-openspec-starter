# Phase 1：Responses API 请求和响应结构

日期：2026-04-27

对应 OpenSpec change：`learn-phase-1-responses-api-structure`

官方参考：

- [Responses API reference](https://platform.openai.com/docs/api-reference/responses)
- [Create a model response](https://platform.openai.com/docs/api-reference/responses/create)
- [Migrate to the Responses API](https://platform.openai.com/docs/guides/responses-vs-chat-completions)

## 这一小节学什么

本小节只学习 Responses API 的请求和响应结构，不做真实 API 调用，不实现完整 client，不做 streaming、structured output、tool calling 或 RAG。

要建立的心智模型是：

- `responses.create` 是生成模型响应的核心入口。
- 请求的中心是 `model` 和 `input`。
- 响应的中心是 `id`、`status`、`output`、`usage`、`error`。
- 多轮上下文可以通过显式传入前一次 `output`，或通过 `previous_response_id` 串联。

## 最小请求结构

最小请求可以理解为：

```json
{
  "model": "gpt-4.1-mini",
  "input": "用一句话解释什么是 RAG。"
}
```

其中：

- `model`：使用的模型 ID。
- `input`：传给模型的输入。可以是简单字符串，也可以是结构化 input item list。

简单字符串输入等价于一个 user 角色的文本输入。学习阶段可以先从字符串输入理解整体链路，再过渡到结构化输入。

## 结构化 input item

结构化输入更接近后续 Agent 和 RAG 会用到的形式：

```json
{
  "model": "gpt-4.1-mini",
  "input": [
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "用一句话解释什么是 RAG。"
        }
      ]
    }
  ]
}
```

关键点：

- 每个 message item 通常有 `role`、`content`、`type`。
- `content` 可以是字符串，也可以是内容数组。
- 文本内容项的类型是 `input_text`。
- 结构化输入给后续图像、文件、工具输出和多轮上下文留下扩展空间。

## 常见请求字段

| 字段 | 用途 | 当前学习阶段是否需要 |
| --- | --- | --- |
| `model` | 指定模型 | 需要 |
| `input` | 用户输入、上下文、工具输出等 | 需要 |
| `instructions` | 注入 system/developer 指令 | 先理解，后续 prompt 小节再深入 |
| `previous_response_id` | 基于前一个 response 继续对话 | 先理解概念 |
| `tools` | 给模型可调用工具 | 后续 tool calling 小节再做 |
| `include` | 要求响应包含额外字段，如检索结果或 logprobs | 后续工具/RAG 阶段再用 |
| `max_output_tokens` | 限制输出 token | 后续真实调用时使用 |
| `metadata` | 附加业务元数据 | 后续日志和追踪阶段再用 |

## 典型响应结构

典型 response object 可以先按这个层级理解：

```json
{
  "id": "resp_xxx",
  "object": "response",
  "created_at": 1730000000,
  "status": "completed",
  "model": "gpt-4.1-mini",
  "output": [
    {
      "id": "msg_xxx",
      "type": "message",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "RAG 是让模型在回答前检索外部知识，并基于检索结果生成答案的方法。"
        }
      ]
    }
  ],
  "usage": {
    "input_tokens": 20,
    "output_tokens": 30,
    "total_tokens": 50
  }
}
```

关键点：

- `id` 是后续 retrieve、input items 查询、多轮串联的重要锚点。
- `status` 表示响应是否完成，也可能出现进行中、未完成或失败相关状态。
- `output` 是数组，不只是单个字符串；后续可能包含 message、reasoning、tool call 等不同 item。
- 文本输出通常在 `output[].content[]` 中，以 `output_text` 表示。
- `usage` 记录 token 使用情况，是后续成本、延迟和评测分析的基础。
- `error` 和 `incomplete_details` 用来理解失败或未完成原因。

## input items 和 token count

Responses API 还有两个和结构理解相关的辅助入口：

- `GET /v1/responses/{response_id}/input_items`：查看某次 response 实际使用的 input items。
- `POST /v1/responses/input_tokens`：在不生成响应的情况下估算请求输入 token 数。

它们对后续学习很有用：

- 调试上下文是否真的进入模型。
- 检查多轮对话传入了哪些历史信息。
- 在真实调用前估算成本。
- 为 RAG 阶段判断检索上下文是否过长做准备。

## 和 Chat Completions 的心智差异

Chat Completions 的核心输入通常是 `messages`，响应文本常从 `choices[0].message` 读取。

Responses API 的核心输入是 `input`，响应结果主要看 `output`。它更像一个统一的“响应对象”系统：

- 输入可以是字符串，也可以是结构化 item list。
- 输出是 item list，不只是 assistant message。
- 工具调用、reasoning、文件、图像等能力都可以通过 item 结构扩展。
- 多轮可以手动把前一次 `output` 加回上下文，也可以用 `previous_response_id`。

对 Agent 开发来说，Responses API 更贴近后续要做的工具调用、状态追踪和可观测性。

## 当前结论

本项目后续接真实模型时，不应该让业务代码直接依赖某个返回字符串的简单函数。更好的方式是保留 Phase 0 已经建立的 `ModelClient` 抽象，并在真实 client 中显式处理：

- 请求结构构造。
- response id 和 status。
- output item 解析。
- usage 和错误信息。
- 后续工具调用输出。

这样 Phase 1 的基础聊天、streaming、structured output、tool calling 都可以在同一个结构心智上逐步扩展。
