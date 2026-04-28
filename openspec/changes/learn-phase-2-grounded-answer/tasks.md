## 1. 设计与测试

- [x] 1.1 创建 OpenSpec change，明确 grounded answer 学习目标、边界和验收标准。
- [x] 1.2 先编写 prompt 组装、回答模块和脚本测试，并确认测试失败。

## 2. 实现

- [x] 2.1 新增 grounded answer 模块，定义结果对象和 prompt 构造函数。
- [x] 2.2 实现 `GroundedAnswerer`，把检索结果交给模型 client 生成回答。
- [x] 2.3 新增回答演示脚本，串联检索和生成。
- [x] 2.4 支持 dry-run 和 DeepSeek 真实模式。

## 3. 文档与验证

- [x] 3.1 新增学习笔记，记录上下文 prompt 结构、边界和后续衔接点。
- [x] 3.2 使用 hashing provider 和 dry-run 完成 grounded answer 演示。
- [x] 3.3 使用 FastEmbed provider 和 DeepSeek 完成真实 grounded answer 演示。
- [x] 3.4 运行单元测试和 OpenSpec 严格校验。
- [x] 3.5 完成后更新 `tasks.md` 和 `docs/agent-learning-todo.md` 勾选状态。
