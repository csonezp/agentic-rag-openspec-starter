## 1. 设计与测试

- [x] 1.1 创建 OpenSpec change，明确来源引用学习目标、边界和验收标准。
- [x] 1.2 先编写 citation、prompt 和脚本测试，并确认测试失败。

## 2. 实现

- [x] 2.1 新增来源引用对象和从检索结果生成 citations 的函数。
- [x] 2.2 让 `GroundedAnswerResult` 携带 citations。
- [x] 2.3 调整 grounded prompt，要求模型使用 `[chunk_id]` 引用依据。
- [x] 2.4 调整回答脚本，输出结构化 sources 列表。

## 3. 文档与验证

- [x] 3.1 新增学习笔记，记录引用格式、结构化 sources 和模型引用不稳定的边界。
- [x] 3.2 使用 hashing provider 和 dry-run 完成来源引用演示。
- [x] 3.3 使用 FastEmbed provider 和 DeepSeek 完成真实来源引用演示。
- [x] 3.4 运行单元测试和 OpenSpec 严格校验。
- [x] 3.5 完成后更新 `tasks.md` 和 `docs/agent-learning-todo.md` 勾选状态。
