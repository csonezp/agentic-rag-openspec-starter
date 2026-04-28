## 1. 设计与测试

- [x] 1.1 创建 OpenSpec change，明确本地向量库学习目标、边界和验收标准。
- [x] 1.2 先编写向量库写入测试，并确认测试失败。

## 2. 实现

- [x] 2.1 新增本地向量库模块，封装 Qdrant collection 初始化。
- [x] 2.2 实现 `EmbeddedChunk` 到 Qdrant point payload 的转换。
- [x] 2.3 实现批量 upsert，保证相同 chunk 重复写入时使用稳定 point id。
- [x] 2.4 新增索引脚本，串联加载、标准化、切片、embedding 和向量库写入。
- [x] 2.5 更新依赖和 git ignore，避免本地向量库数据进入仓库。

## 3. 文档与验证

- [x] 3.1 新增学习笔记，记录 Qdrant 本地模式、payload 设计和重复写入策略。
- [x] 3.2 使用 hashing provider 完成本地向量库写入演示。
- [x] 3.3 使用 FastEmbed provider 完成真实本地模型写入演示。
- [x] 3.4 运行单元测试和 OpenSpec 严格校验。
- [x] 3.5 完成后更新 `tasks.md` 和 `docs/agent-learning-todo.md` 勾选状态。
