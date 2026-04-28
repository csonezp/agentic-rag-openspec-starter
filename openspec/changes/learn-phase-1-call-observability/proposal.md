## Why

当前项目已经具备 DeepSeek 真实调用、流式输出、结构化输出和 tool calling 能力，但每次运行后仍缺少最基础的可观察信息。学习者只能看到“模型回答了什么”，却看不到“用了哪个模型、耗时多久、消耗了多少 token、失败时具体错在哪”。

本小节重点学习最小调用观测闭环：围绕当前主用的 DeepSeek 调用链，记录延迟、token 使用量、模型名和错误信息，让每次真实调用都能被检查和解释。

## What Changes

- 在 Phase 1 中推进“记录延迟、token 使用量、模型名和错误”小节。
- 为 DeepSeek 非流式调用补充最小观测结果，包括 `provider`、`model`、`latency_ms`、`input_tokens`、`output_tokens`、`total_tokens` 和 `error`。
- 为 DeepSeek 流式输出补充最小观测结果，并在流式结束后汇总打印。
- 为 tool calling 主链补充最小观测信息，至少能看见模型调用结果、是否触发 tool 和失败信息。
- 新增单元测试和学习笔记，记录 DeepSeek `usage` 字段的读取口径、延迟统计方式和错误展示边界。

不做：

- 不接入 OpenTelemetry、LangSmith、Tracing 平台或持久化日志。
- 不做成本换算、预算控制或监控面板。
- 不把 OpenAI 一起纳入统一观测抽象；本小节先覆盖 DeepSeek 主链。
- 不在本小节处理多轮会话级聚合指标。

## Capabilities

### New Capabilities

- `call-observability-learning`: 覆盖 Phase 1 调用观测学习，包括延迟、token 使用量、模型名和错误信息的采集与展示。

### Modified Capabilities

- `learning-roadmap`: Phase 1 调用观测小节完成状态会在本 change 完成后更新。

## Impact

- 影响 `src/agent_kb/deepseek_client.py`：增加 DeepSeek 调用观测信息提取。
- 可能影响 `src/agent_kb/tool_calling.py`：增加 tool calling 过程的最小观测输出。
- 可能影响 `scripts/hello_model.py` 和 `scripts/tool_calling_demo.py`：展示观测摘要。
- 新增或更新测试、学习笔记与 OpenSpec 文档。
