## 1. 设计与测试

- [x] 1.1 创建 OpenSpec change，明确结构化输出学习目标、边界和验收标准。
- [x] 1.2 先编写 DeepSeek JSON Output 请求和本地 schema 校验测试，并确认测试失败。

## 2. 实现

- [x] 2.1 扩展 DeepSeek 客户端，支持非流式 JSON Output 请求。
- [x] 2.2 新增小 schema 结构化输出模块，支持解析和校验 `title`、`summary`、`next_action`。
- [x] 2.3 新增结构化输出演示脚本，支持 dry-run 和真实 DeepSeek 调用。

## 3. 文档与验证

- [x] 3.1 新增学习笔记，记录 DeepSeek JSON Output 的请求方式和边界。
- [x] 3.2 运行单元测试和 OpenSpec 严格校验。
- [x] 3.3 使用真实 DeepSeek JSON Output 完成一次结构化输出验证。
- [x] 3.4 完成后更新 `tasks.md` 和 `docs/agent-learning-todo.md` 勾选状态。
