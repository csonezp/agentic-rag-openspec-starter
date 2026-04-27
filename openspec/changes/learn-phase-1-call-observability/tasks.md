## 1. 启动学习小节

- [x] 1.1 确认该小节尚未完成。
- [x] 1.2 从 `main` 创建学习分支 `codex/learn-phase-1-call-observability`。
- [x] 1.3 创建 OpenSpec change `learn-phase-1-call-observability`。
- [x] 1.4 写明学习目标、不做事项和完成标准。

## 2. 设计与测试

- [x] 2.1 设计 DeepSeek 调用观测信息的最小数据结构和展示格式。
- [x] 2.2 先编写或更新单元测试，覆盖 usage 提取、延迟统计和错误展示。

## 3. 实现

- [x] 3.1 扩展 DeepSeek 客户端，返回或暴露模型名、token 使用量和错误信息。
- [x] 3.2 为流式输出补充延迟和 token 观测摘要。
  - 2026-04-27(task1): 恢复 `stream()` 的真正流式语义，不再先全量缓冲后输出；统一 `complete_with_observation`、`parse_deepseek_stream_events` 和 `stream_with_observation` 在 200 但非法 JSON、畸形 SSE、`payload.error` 场景下抛出携带 `observation` 的 `DeepSeekCallError`；补充 `error_type` 摘要输出，并通过 `tests.test_deepseek_client`、`tests.test_call_observability` 回归验证。
- [ ] 3.3 为 tool calling 链路补充最小观测信息。
- [ ] 3.4 更新 CLI 脚本，输出统一的观测摘要。

## 4. 文档与验证

- [ ] 4.1 新增学习笔记，记录字段来源、统计口径和限制。
- [ ] 4.2 运行单元测试和 OpenSpec 严格校验。
  - 2026-04-27(task1): 已运行 `PYTHONPATH=src:. python3 -m unittest tests.test_deepseek_client tests.test_call_observability -v`，通过；尚未执行 OpenSpec 严格校验，因此该项保持未完成。
- [ ] 4.3 使用真实 DeepSeek 调用验证至少一条非流式链路和一条 tool calling 链路。
- [ ] 4.4 完成后更新 `tasks.md` 和 `docs/agent-learning-todo.md` 勾选状态。
