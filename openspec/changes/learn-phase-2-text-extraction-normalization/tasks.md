## 1. 设计与测试

- [x] 1.1 创建 OpenSpec change，明确文本抽取和标准化目标、边界和验收标准。
- [x] 1.2 先编写文本抽取和标准化测试，并确认测试失败。

## 2. 实现

- [x] 2.1 新增 `NormalizedDocument` 文档对象。
- [x] 2.2 新增 Markdown 文本抽取和标准化函数。
- [x] 2.3 新增文档级标准化函数，保留 `source_path`、`title` 和 `text`。
- [x] 2.4 新增标准化演示脚本，输出标准化摘要。

## 3. 文档与验证

- [x] 3.1 新增学习笔记，记录标准化规则和后续衔接点。
- [x] 3.2 运行单元测试和 OpenSpec 严格校验。
- [x] 3.3 使用 `knowledge/` 完成本地标准化演示验证。
- [x] 3.4 完成后更新 `tasks.md` 和 `docs/agent-learning-todo.md` 勾选状态。
