# 任务清单

## 1. 启动学习小节

- [x] 确认该小节尚未完成。
- [x] 从 `main` 创建学习分支 `codex/learn-phase-1-streaming-output`。
- [x] 创建 OpenSpec change `learn-phase-1-streaming-output`。
- [x] 写明学习目标、不做事项和完成标准。

## 2. 官方文档研读

- [x] 阅读 OpenAI streaming responses guide。
- [x] 确认 Responses API 通过 `stream=true` 开启 SSE。
- [x] 记录常见事件：`response.created`、`response.output_text.delta`、`response.completed`、`error`。

## 3. 测试先行

- [x] 为 dry-run 流式输出写测试。
- [x] 为 CLI `--stream` 写测试。
- [x] 为 SSE delta 解析写测试。
- [x] 为非流式路径保持兼容写测试。

## 4. 实现流式输出

- [x] 在模型客户端协议中增加流式输出能力。
- [x] 实现 dry-run stream。
- [x] 实现 Responses API streaming 的最小 SSE 解析。
- [x] 在脚本中增加 `--stream` 开关。
- [x] 保持 `--real` 缺少 API Key 时不发送请求。

## 5. 学习笔记

- [x] 创建流式输出中文学习笔记。
- [x] 记录 SSE 事件模型和 chunk/delta 心智差异。
- [x] 记录生产 moderation 风险。

## 6. 收尾

- [x] 更新 `docs/agent-learning-todo.md` 中对应小节状态。
- [x] 更新本 change 的任务状态和学习结论。
- [x] 运行 OpenSpec 严格校验。
- [x] 运行现有测试。
- [ ] 推送学习分支，不直接合并 `main`。

## 学习结论

- Responses API streaming 通过 `stream: true` 启用 HTTP SSE。
- 文本流式输出的关键事件是 `response.output_text.delta`，其中 `delta` 是本次增量文本。
- `response.completed` 表示生命周期完成；本项目当前只需要读取文本 delta 和 error。
- dry-run streaming 可以让学习和测试不依赖网络。
- 流式输出增加了生产审核难度，因为用户会看到部分输出；当前只作为学习样例。
