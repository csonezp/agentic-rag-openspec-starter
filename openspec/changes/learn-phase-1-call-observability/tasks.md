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
- [x] 3.3 为 tool calling 链路补充最小观测信息。
  - 2026-04-27(task1): 为 `ToolCallingRunner` 新增 `run_with_observation()`，返回独立的结构化观测结果；最小字段覆盖 `tool_triggered`、`tool_names`、`success`、`error_type` 和 `error_message`，并保持现有 `run()`/CLI 输出契约不变；已通过 `tests.test_tool_calling` 和 `tests.test_call_observability` 回归验证。
  - 2026-04-27(task3-review): 修复进入 `tool_calls` 分支后在 `parse_tool_request` 失败、handler 抛错、第二次 `create_chat_completion` 失败、最终 `content` 为空等路径下观测字段丢失的问题；补充 `parse_tool_request` 对缺失 `id`/`name` 的清晰校验，以及 `run_with_observation()` 失败路径测试；已通过 `tests.test_tool_calling` 和 `tests.test_call_observability` 回归验证。
- [x] 3.4 更新 CLI 脚本，输出统一的观测摘要。
  - 2026-04-27(task4): `scripts/hello_model.py` 在 DeepSeek 真实非流式与流式路径接入 `call_observability.format_observation_lines()`，统一输出 `observation:` 摘要块；`scripts/tool_calling_demo.py` 在真实模式接入 `format_tool_call_observation_lines()` 输出 tool calling 观测摘要，同时保留 dry-run 默认路径与真实模式缺少 API Key 时的现有语义；对应补充 `tests.test_hello_model_script`、`tests.test_tool_calling` 和 `tests.test_call_observability` 回归验证。
  - 2026-04-27(task4-review): 修复两个 CLI 在真实失败路径丢失结构化观测的问题：`scripts/hello_model.py` 捕获 `DeepSeekCallError` 后先打印 `observation:` 摘要，再向 stderr 输出错误并以非零退出；`scripts/tool_calling_demo.py` 在 `run_with_observation()` 返回 `success=false` 时先打印 tool calling 观测摘要，再向 stderr 输出错误并返回非零；补充对应失败路径测试，覆盖非流式、流式和 tool calling 三类 CLI 失败场景。

## 4. 文档与验证

- [ ] 4.1 新增学习笔记，记录字段来源、统计口径和限制。
- [ ] 4.2 运行单元测试和 OpenSpec 严格校验。
  - 2026-04-27(task1): 已运行 `PYTHONPATH=src:. python3 -m unittest tests.test_deepseek_client tests.test_call_observability -v`，通过；尚未执行 OpenSpec 严格校验，因此该项保持未完成。
  - 2026-04-27(task4-review): 已运行 `PYTHONPATH=src:. python3 -m unittest tests.test_hello_model_script tests.test_tool_calling tests.test_call_observability -v`，通过；尚未执行 OpenSpec 严格校验，因此该项保持未完成。
- [ ] 4.3 使用真实 DeepSeek 调用验证至少一条非流式链路和一条 tool calling 链路。
- [ ] 4.4 完成后更新 `tasks.md` 和 `docs/agent-learning-todo.md` 勾选状态。
