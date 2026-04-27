## 1. 设计与测试

- [x] 1.1 创建 OpenSpec change，明确 tool calling 学习目标、边界和验收标准。
- [x] 1.2 先编写 DeepSeek tools 请求、tool call 解析和本地函数 runner 测试，并确认测试失败。

## 2. 实现

- [x] 2.1 扩展 DeepSeek 客户端，支持发送 tools 并解析 tool_calls。
- [x] 2.2 新增只读本地函数 `get_phase1_progress` 和 tool schema。
- [x] 2.3 新增 tool calling runner，完成模型 tool call、本地执行、二次模型调用闭环。
- [x] 2.4 新增 tool calling 演示脚本，支持 dry-run 和真实 DeepSeek 调用。

## 3. 文档与验证

- [x] 3.1 新增学习笔记，记录 tool calling 流程和安全边界。
- [x] 3.2 运行单元测试和 OpenSpec 严格校验。
- [x] 3.3 使用真实 DeepSeek Tool Calls 完成一次本地函数调用验证。
- [x] 3.4 完成后更新 `tasks.md` 和 `docs/agent-learning-todo.md` 勾选状态。
