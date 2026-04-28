## 1. 设计与测试

- [x] 1.1 创建 OpenSpec change，明确 top-k 检索学习目标、边界和验收标准。
- [x] 1.2 先编写 top-k 检索测试，并确认测试失败。

## 2. 实现

- [x] 2.1 新增检索结果对象，包含 score、chunk metadata 和文本。
- [x] 2.2 在 `LocalQdrantVectorStore` 中实现 top-k search。
- [x] 2.3 新增检索演示脚本，支持问题输入、provider、collection 和 top-k 参数。
- [x] 2.4 确保 query embedding 维度与 collection 维度一致时可以检索。

## 3. 文档与验证

- [x] 3.1 新增学习笔记，记录 top-k 检索流程、score 含义和 provider 一致性约束。
- [x] 3.2 使用 hashing provider 完成 top-k 检索演示。
- [x] 3.3 使用 FastEmbed provider 完成真实本地 top-k 检索演示。
- [x] 3.4 运行单元测试和 OpenSpec 严格校验。
- [x] 3.5 完成后更新 `tasks.md` 和 `docs/agent-learning-todo.md` 勾选状态。
