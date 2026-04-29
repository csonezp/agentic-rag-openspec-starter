# Phase 2 学习笔记：当检索证据较弱时拒答

日期：2026-04-28

## 学习目标

本小节在生成回答前增加 evidence check，避免模型在检索证据不足时继续生成看似合理但缺乏依据的回答。

本小节采用最小可解释策略：根据检索结果数量和最高 score 判断是否拒答。

## 本次做了什么

- 新增 `EvidenceCheckResult`，记录证据是否足够、原因、最高 score 和上下文数量。
- 新增 `evaluate_evidence()`：
  - 无检索结果时拒答，原因是 `no_contexts`。
  - 最高 score 低于 `min_score` 时拒答，原因是 `best_score_below_threshold`。
  - 最高 score 达到阈值时允许继续生成回答。
- `GroundedAnswerResult` 新增 `refused` 和 `refusal_reason` 字段。
- `scripts/answer_with_context.py` 新增 `--min-score` 参数，默认 `0.45`。
- 回答脚本会先做 evidence check；证据弱时输出拒答和 sources，不调用真实模型。
- 补充测试覆盖证据足够、无上下文、低分上下文、本地拒答和正常模型调用分支。
- 把“学习交互内容也要沉淀到学习文档”的规则写入 `AGENTS.md`，并从本小节开始执行。

## 原理/流程

本小节解决的是“检索到了来源，但来源是否足够支撑回答”的问题。来源引用负责可追溯，弱证据拒答负责判断是否应该回答。

整体流程如下：

```text
用户问题
-> 生成 query embedding
-> Qdrant top-k 检索候选 chunk
-> evaluate_evidence() 检查上下文数量和最高 score
-> 证据不足：本地输出拒答，不调用 DeepSeek
-> 证据足够：构造 grounded prompt，调用 DeepSeek 或 dry-run
-> 输出回答、refused 状态、拒答原因和 sources
```

当前判断逻辑是最小版本：

- 没有检索结果，说明知识库没有可用上下文，直接拒答。
- 有检索结果但最高 score 低于 `min_score`，说明最相关内容仍然不够相似，拒答。
- 最高 score 达到阈值时，才把检索上下文放进 prompt，并允许模型生成回答。

这个判断发生在模型调用之前，因此证据不足时不会消耗真实模型调用，也不会把弱相关上下文交给模型“硬答”。

## 拒答输出

证据弱时输出：

```text
mode=refusal
answer:
当前知识库没有提供足够证据回答这个问题。
refused=true
refusal_reason=best_score_below_threshold
sources:
...
```

证据足够时输出：

```text
mode=real 或 mode=dry-run
answer:
...
refused=false
sources:
...
```

## 阈值取舍

默认 `min_score=0.45` 是学习阶段的保守起点，不是生产最终阈值。

需要注意：

- 不同 embedding provider 的 score 分布不同，阈值不能跨 provider 盲目复用。
- hashing provider 只适合流程测试，score 语义不可靠。
- FastEmbed 的 score 更接近真实语义检索，但仍需要后续评测集来校准阈值。

## 验证记录

- evidence check 测试先失败于 `EvidenceCheckResult` 不存在，随后实现证据判断和拒答分支后通过。
- `PYTHONPATH=src:. python3 -m unittest tests.test_grounded_answer` 通过，合计 10 个测试。
- `PYTHONPATH=src:. python3 scripts/answer_with_context.py "如何记录模型调用的延迟和 token？" --vector-store-path data/qdrant-fastembed-demo --collection-name knowledge_chunks_fastembed --provider fastembed --top-k 2 --min-score 0.99` 使用高阈值完成 dry-run 拒答演示，`best_score=0.703202` 低于阈值。
- `PYTHONPATH=src:. python3 scripts/answer_with_context.py "如何记录模型调用的延迟和 token？" --vector-store-path data/qdrant-fastembed-demo --collection-name knowledge_chunks_fastembed --provider fastembed --top-k 2 --min-score 0.99 --real` 本地拒答，`best_score=0.703202` 低于阈值，且没有调用 DeepSeek。
- `PYTHONPATH=src:. python3 scripts/answer_with_context.py "如何记录模型调用的延迟和 token？" --vector-store-path data/qdrant-fastembed-demo --collection-name knowledge_chunks_fastembed --provider fastembed --top-k 2 --min-score 0.45 --real` 证据足够，调用 DeepSeek 成功，输出 `refused=false`，并保留 sources 和 observation。
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` 通过，合计 114 个测试。
- `/opt/homebrew/bin/openspec validate --all --strict` 通过，合计 19 个 OpenSpec 校验项。

## 本次交互总结

- 用户要求从本小节开始新增规则：学习过程中的交互内容也要总结并更新到学习文档中。
- 该规则已写入 `AGENTS.md`，以后学习文档不仅记录代码改动，也要记录用户追问、概念澄清、验证方式、实现取舍和临时新增的协作规则。
- 本小节讨论并落实了“有来源不等于证据足够”的边界：来源引用解决可追溯，弱证据拒答解决是否应该回答。
- 实现过程中测试暴露了 hashing provider 在小样本下可能出现 score 为 0 的情况，因此正常回答测试显式设置 `--min-score 0`，拒答测试使用高阈值；这再次说明阈值必须结合 provider 和评测集校准。

## 后续问题

- Phase 3 需要用评测集量化不同阈值下的误答率和误拒率。
- 后续可以增加 query rewriting、二次检索、metadata filter 或 rerank 来减少误拒。
- 拒答策略最终应该结合 score、top-k 分布、问题类型和评测结果，而不只看单一最高 score。
