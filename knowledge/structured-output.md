# 结构化输出

结构化输出用于让模型返回可被程序解析的数据，而不只是自然语言。当前项目使用一个小 schema：`title`、`summary`、`next_action`，把学习内容整理成结构化学习摘要。

DeepSeek JSON Output 通过 `response_format={"type":"json_object"}` 要求模型返回合法 JSON。提示词中也必须明确包含 json 字样，并给出目标 JSON 示例。这个机制能提高输出可解析性，但不等于完整业务 schema 校验。

因此，本项目把结构化输出拆成两层。第一层是模型/API 层，要求返回合法 JSON。第二层是本地应用层，使用代码检查 required fields、字段类型和非空字符串。即使模型返回合法 JSON，如果缺少 `next_action` 或字段类型错误，也应该被拒绝。

结构化输出和 tool calling 容易混淆。结构化输出是“让模型生成 JSON”；tool calling 是“模型请求本地代码调用函数”。前者不执行外部能力，后者必须由本地 runner 控制工具执行。

## 可验证事实

- 当前小 schema 包含 `title`、`summary`、`next_action`。
- DeepSeek JSON Output 要求 `response_format` 为 `json_object`。
- 合法 JSON 不等于符合业务 schema。
- 结构化输出不会自动执行本地函数。
