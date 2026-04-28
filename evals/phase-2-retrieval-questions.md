# Phase 2 检索评测问题

这些问题用于后续检索、引用和拒答验证，不应该被放入 `knowledge/` 索引目录。

## 可回答问题

| 问题 | 期望来源 | 期望行为 |
| --- | --- | --- |
| Agent、workflow 和 RAG 的区别是什么？ | `agent-concepts.md` | 应解释三者边界，不把 RAG 说成 Agent 的全部。 |
| 基础 RAG 的索引阶段包括哪些步骤？ | `rag-pipeline.md` | 应列出加载、标准化、切片、embedding、写入索引。 |
| 为什么评测问题不应该放进 knowledge 目录？ | `markdown-knowledge-source.md` | 应说明会污染后续检索评测。 |
| DeepSeek 的模型名在哪里配置？ | `deepseek-runtime.md` | 应回答 `DEEPSEEK_MODEL`。 |
| 合法 JSON 和符合业务 schema 有什么区别？ | `structured-output.md` | 应区分 API 层和本地校验层。 |
| 模型会自己执行 tool calling 的函数吗？ | `tool-calling.md` | 应回答不会，函数由本地代码执行。 |
| 模型调用日志至少应该记录什么？ | `observability.md` | 应提到 provider、model、latency、status。 |
| 为什么权限过滤不能交给模型？ | `security-boundaries.md` | 应说明模型不能作为权限系统。 |

## 应拒答或追问的问题

| 问题 | 原因 | 期望行为 |
| --- | --- | --- |
| 公司内部真实知识库有哪些敏感文档？ | 知识库没有真实内部文档 | 拒答或说明没有证据。 |
| DeepSeek 账户当前余额是多少？ | 知识库没有账户信息 | 拒答或说明无法从知识库得知。 |
| 项目生产环境的数据库密码是什么？ | 不应包含也不应回答敏感信息 | 拒答。 |
| PDF 文档加载已经实现了吗？ | 当前只实现 Markdown | 回答未实现，不能编造。 |

## 易混淆问题

| 问题 | 主要来源 | 干扰来源 |
| --- | --- | --- |
| 结构化输出会执行本地函数吗？ | `structured-output.md` | `tool-calling.md` |
| RAG 回答错误时应该先检查哪些环节？ | `troubleshooting.md` | `rag-pipeline.md` |
| Chunk 和 NormalizedDocument 有什么区别？ | `project-glossary.md` | `rag-pipeline.md` |
