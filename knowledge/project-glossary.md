# 项目术语表

KnowledgeDocument 指加载阶段得到的原始文档对象。它包含来源路径、标题和原始内容。这个对象还没有经过标准化，也没有被切片。

NormalizedDocument 指标准化阶段得到的文本对象。它包含来源路径、标题和标准化后的纯文本。它是后续 chunking 的输入。

Chunk 指从标准化文档中切出的文本片段。一个 chunk 应该带有来源路径、标题、chunk 序号和位置范围等 metadata。chunk 是后续 embedding 和检索的基本单位。

Embedding 指把文本转换成向量表示。向量可以用于相似度检索，但不能单独保证答案正确。检索出的 chunk 仍然需要模型基于证据生成回答。

Top-k 指检索时返回最相关的前 k 个结果。k 太小可能漏召回，k 太大可能把噪声带进模型上下文。

Refusal 指证据不足时拒答。拒答不是失败，而是防止模型编造答案的重要能力。

## 可验证事实

- `KnowledgeDocument` 是原始加载结果。
- `NormalizedDocument` 是标准化后的文本结果。
- Chunk 是 embedding 和检索的基本单位。
- Refusal 用于证据不足的场景。
