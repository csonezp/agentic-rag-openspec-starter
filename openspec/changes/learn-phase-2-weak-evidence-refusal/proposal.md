# Proposal: 学习 Phase 2 的「当检索证据较弱时拒答」

## 为什么做

当前 RAG 链路已经能检索 top-k chunks、基于上下文回答，并输出来源引用。但“有检索结果”不等于“证据足够”。如果检索命中弱、score 很低、上下文数量不足，模型仍然可能组织出看似合理但缺乏依据的回答。

本小节要学习的是拒答边界：如何在生成回答前先判断检索证据是否足够，什么时候继续回答，什么时候明确说明当前知识库没有足够证据。

## 做什么

- 定义 evidence check 结果对象。
- 基于检索结果数量和最高 score 实现最小证据强弱判断。
- 在回答脚本中加入拒答分支，证据弱时不调用真实模型。
- 输出拒答原因和当前可用 sources。
- 记录本次学习过程中的关键交互内容和实现取舍。

## 不做什么

- 不做复杂语义评估。
- 不做 LLM-as-judge。
- 不做 query rewriting 或二次检索。
- 不做 metadata filter、hybrid search 或 rerank。
- 不保证拒答策略就是生产最终策略。

## 成功标准

- 检索结果为空或最高 score 低于阈值时，脚本能拒答。
- 拒答时不调用模型生成回答。
- 命中足够强时，仍可走 grounded answer 链路。
- CLI 能输出 refusal reason、evidence score 和 sources。
- 单元测试、真实演示和 OpenSpec 严格校验通过。
