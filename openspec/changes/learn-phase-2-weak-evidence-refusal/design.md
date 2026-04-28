# Design: 弱证据拒答

## 背景

当前链路：

问题 → query embedding → Qdrant top-k → grounded prompt → 模型回答 → sources。

本节在“模型回答”之前增加证据判断：

问题 → query embedding → Qdrant top-k → evidence check → 回答或拒答。

## 策略

本小节采用最小可解释策略：

- 如果检索结果数量为 0：拒答。
- 如果最高 score 低于 `min_score`：拒答。
- 否则继续生成回答。

默认 `min_score` 计划先使用 `0.45`，并允许 CLI 通过 `--min-score` 调整。

## 模块边界

计划扩展 `agent_kb.grounded_answer`：

- `EvidenceCheckResult`：记录 `is_sufficient`、`reason`、`best_score` 和 `contexts_count`。
- `evaluate_evidence()`：根据 contexts 和阈值判断证据是否足够。
- `GroundedAnswerResult` 增加 `refused` 和 `refusal_reason`。

计划调整 `scripts/answer_with_context.py`：

- 增加 `--min-score`。
- 检索后先执行 evidence check。
- 如果证据弱，输出拒答文本、reason、sources，不调用 DeepSeek。
- 如果证据足够，保持现有回答生成流程。

## 输出格式

证据弱时：

```text
answer:
当前知识库没有提供足够证据回答这个问题。
refused=true
refusal_reason=best_score_below_threshold
best_score=0.123456
sources:
...
```

证据足够时：

```text
answer:
...
refused=false
sources:
...
```

## 风险与取舍

- 单纯 score 阈值是粗糙策略，但适合本阶段学习拒答边界。
- 不同 embedding provider 的 score 分布不同，阈值不能跨 provider 盲目复用。
- 后续评测集会帮助选择更合理阈值。
- 本节先保证“不确定时不编造”的基本安全行为。
