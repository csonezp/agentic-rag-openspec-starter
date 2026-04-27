## Why

当前项目已经能调用 DeepSeek 官方 API，但模型输出仍然是自由文本。为了让后续 Agent 能稳定地把模型结果交给程序逻辑处理，需要学习并实现一个小 schema 的结构化输出。

本小节重点学习 DeepSeek JSON Output 的真实用法：通过 `response_format={"type":"json_object"}` 约束模型输出合法 JSON，再由本地代码做 schema 校验。

## What Changes

- 在 Phase 1 中推进“为一个小 schema 添加结构化输出”小节。
- 新增一个小型结构化输出 schema，用于把学习文本提炼为固定字段。
- 扩展 DeepSeek 客户端，支持 JSON Output 请求参数。
- 新增结构化输出解析和校验逻辑，避免把“合法 JSON”误认为“符合业务 schema”。
- 新增演示脚本，支持 dry-run 和真实 DeepSeek 调用。
- 新增单元测试和学习笔记，记录 DeepSeek JSON Output 与 OpenAI Structured Outputs 的差异。

不做：

- 不在本小节实现复杂 JSON Schema、嵌套结构或数组 schema。
- 不引入 Pydantic、jsonschema 等第三方依赖。
- 不实现 tool calling；function/tool calling 是后续独立小节。
- 不要求流式结构化输出；本小节只验证非流式结构化输出。

## Capabilities

### New Capabilities

- `structured-output-schema-learning`: 覆盖小 schema 结构化输出学习，包括 JSON Output 请求、解析、校验和验证。

### Modified Capabilities

- `learning-roadmap`: Phase 1 结构化输出小节完成状态会在本 change 完成后更新。

## Impact

- 影响 DeepSeek 客户端：增加 JSON Output 请求能力。
- 新增结构化输出模块和演示脚本。
- 新增测试：覆盖 JSON Output 请求体、schema 解析和 CLI 行为。
- 更新文档：路线图、学习笔记和 OpenSpec 任务记录。
