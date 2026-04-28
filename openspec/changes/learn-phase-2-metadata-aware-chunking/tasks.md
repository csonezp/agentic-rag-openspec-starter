## 1. 启动学习小节

- [x] 1.1 确认该小节尚未完成。
- [x] 1.2 从 `main` 创建学习分支 `codex/learn-phase-2-metadata-aware-chunking`。
- [x] 1.3 创建 OpenSpec change `learn-phase-2-metadata-aware-chunking`。
- [x] 1.4 写明学习目标、不做事项和完成标准。

## 2. 设计与测试

- [x] 2.1 设计 `DocumentChunk` 数据结构和最小元数据集合。
- [x] 2.2 先编写切片测试，覆盖 chunk 大小、overlap 和元数据保留。

## 3. 实现

- [x] 3.1 新增 `DocumentChunk` 数据对象。
- [x] 3.2 新增面向 `NormalizedDocument` 的切片函数。
- [x] 3.3 新增文档级切片函数和演示脚本。

## 4. 文档与验证

- [x] 4.1 新增学习笔记，记录切片规则、元数据设计和后续衔接点。
- [x] 4.2 运行单元测试和 OpenSpec 严格校验。
- [x] 4.3 使用 `knowledge/` 完成本地切片演示验证。
- [x] 4.4 完成后更新 `tasks.md` 和 `docs/agent-learning-todo.md` 勾选状态。
