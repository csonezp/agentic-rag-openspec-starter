## Context

当前 DeepSeek 主链已经覆盖三种典型调用方式：

1. `scripts/hello_model.py --real` 的非流式真实调用。
2. `scripts/hello_model.py --real --stream` 的流式真实调用。
3. `scripts/tool_calling_demo.py --real` 的 tool calling 闭环。

这些链路都能工作，但“调用过程中发生了什么”还不可见。用户只能看到最终文本，不能快速判断一次调用慢在哪里、是否真的使用了目标模型、token 消耗是多少，以及失败时是 HTTP 错误、网络错误还是本地校验错误。

## Goals / Non-Goals

**Goals:**

- 为 DeepSeek 非流式调用提取并展示模型名、延迟、token 使用量和错误。
- 为 DeepSeek 流式调用补充相同维度的观测摘要，并在流式结束后统一输出。
- 为 tool calling 运行过程补充最小观测信息，包括模型是否触发 tool、最终是否成功。
- 保持 dry-run 默认可运行，不依赖真实 API Key 也能学习脚本结构。
- 用单元测试和一次真实 DeepSeek 调用验证观测结果。

**Non-Goals:**

- 不接入 OpenTelemetry、外部 tracing 平台或数据库。
- 不做跨 provider 的统一可观测框架。
- 不实现成本换算、聚合报表或会话级统计。
- 不改变当前核心调用协议，只在现有主链上增加最小观测能力。

## Decisions

### Decision: 先围绕 DeepSeek 主链增加轻量观测结构

本小节先服务当前主用链路，而不是一次性抽象所有 provider。DeepSeek 客户端和 tool calling 入口将优先返回或暴露最小观测信息，保证学习成本低、路径短。

备选方案是先设计一个覆盖 OpenAI 和 DeepSeek 的通用观测层，但这会把本小节从“学习基础观测”扩展成“设计多 provider 框架”，范围过大。

### Decision: 观测结果与模型文本分离

模型文本仍按现有脚本输出；观测信息单独作为摘要输出。这样后续无论是普通文本、流式文本还是 tool calling 最终答案，都可以复用同一套观测展示方式，不会把业务输出和诊断输出混在一起。

### Decision: 错误按来源保留原始语义

HTTP 错误、网络错误、模型响应缺失字段、本地 tool 校验错误应继续区分，不统一抹平成一个“调用失败”。观测摘要只补充结构化错误信息，不替换现有可读错误。

### Decision: token 统计以 provider 响应 `usage` 为准

如果 DeepSeek 响应中包含 `usage`，则优先读取 `prompt_tokens`、`completion_tokens` 和 `total_tokens`。若流式场景无法稳定获取完整 usage，则在学习笔记中明确记录该限制，并在输出中允许为空值。

## Risks / Trade-offs

- [Risk] 流式响应中的 usage 不一定总是可得。→ 允许流式摘要中的 token 字段为空，并在文档说明口径。
- [Risk] 观测输出过多会影响脚本直觉。→ 先控制为固定几行摘要，不引入复杂 debug dump。
- [Risk] tool calling 链路同时包含模型调用和本地执行，边界容易混乱。→ 先记录最关键事件：是否触发 tool、tool 名、最终成功或错误。
- [Risk] 后续接入 OpenAI 时字段命名可能不同。→ 当前命名先围绕通用概念 `input/output/total/error`，为后续兼容留空间，但不提前做重抽象。
