# 任务清单

## 1. 启动学习小节

- [x] 确认该小节尚未完成。
- [x] 从 `main` 创建学习分支 `codex/learn-phase-1-basic-chat-call`。
- [x] 创建 OpenSpec change `learn-phase-1-basic-chat-call`。
- [x] 写明学习目标、不做事项和完成标准。

## 2. 测试先行

- [x] 为命令行 prompt 解析写测试。
- [x] 为 dry-run 默认路径写测试。
- [x] 为真实模式缺少 API Key 的错误路径写测试。

## 3. 实现基础聊天调用

- [x] 调整脚本，让 prompt 可以从命令行传入。
- [x] 保留默认 prompt。
- [x] 增加 `--real` 显式真实调用开关。
- [x] 新增最小 Responses API client。
- [x] 真实模式缺少 API Key 时输出中文错误。

## 4. 学习笔记

- [x] 创建基础聊天调用中文学习笔记。
- [x] 记录 dry-run 和真实调用的边界。
- [x] 记录为什么默认不调用真实 API。

## 5. 收尾

- [x] 更新 `docs/agent-learning-todo.md` 中对应小节状态。
- [x] 更新本 change 的任务状态和学习结论。
- [x] 运行 OpenSpec 严格校验。
- [x] 运行现有测试。
- [x] 推送学习分支，不直接合并 `main`。

## 学习结论

- 基础聊天调用的最小闭环是“命令行 prompt -> 配置 -> 模型客户端 -> Agent -> 文本响应”。
- 默认 dry-run 可以保护学习流程，不依赖 API Key、不访问网络、不消耗 token。
- 真实模式必须显式 `--real`，这样会消耗 token 的行为是可见的。
- 真实 Responses API client 只做最小 `model + input` 请求，并从 response object 的 `output_text` 提取文本。
- 单元测试覆盖 dry-run 和错误路径，不调用真实网络。
