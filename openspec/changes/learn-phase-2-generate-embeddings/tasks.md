## 1. 设计与测试

- [x] 1.1 创建 OpenSpec change，明确 embeddings 学习目标、边界和验收标准。
- [x] 1.2 先编写 embedding 模型、chunk embedding 和演示脚本测试，并确认测试失败。

## 2. 实现

- [x] 2.1 新增 embedding 模型协议和本地 deterministic embedding 实现。
- [x] 2.2 新增 `EmbeddedChunk` 对象，绑定 chunk metadata 和向量。
- [x] 2.3 新增批量生成 chunk embeddings 的函数。
- [x] 2.4 新增 embeddings 演示脚本，串联加载、标准化、切片和向量生成。

## 3. 文档与验证

- [x] 3.1 新增学习笔记，记录 embedding provider 取舍和后续衔接点。
- [x] 3.2 运行单元测试和 OpenSpec 严格校验。
- [x] 3.3 使用 `knowledge/` 完成本地 embeddings 演示验证。
- [x] 3.4 完成后更新 `tasks.md` 和 `docs/agent-learning-todo.md` 勾选状态。
