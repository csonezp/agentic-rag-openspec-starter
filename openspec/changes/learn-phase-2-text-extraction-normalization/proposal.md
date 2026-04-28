## Why

上一小节已经能把本地 Markdown 文件加载为 `KnowledgeDocument`，但原始 Markdown 内容仍包含标题标记、代码围栏、链接语法和多余空白。进入切片和 embedding 之前，需要先把文档抽取并标准化为更稳定的纯文本形态。

本小节用于学习“文本抽取和标准化”的边界：它负责把 Markdown 原文变成干净文本，并保留最小来源元数据；不做文档切片或向量化。

## What Changes

- 在 Phase 2 中推进“实现文本抽取和标准化”小节。
- 新增标准化文档对象，保存 `source_path`、`title` 和标准化后的 `text`。
- 新增 Markdown 文本抽取逻辑，处理标题、列表、链接、代码围栏和多余空白。
- 新增演示脚本，用于查看加载后再标准化的文本摘要。
- 新增测试和学习笔记，记录标准化规则、边界和后续衔接点。

不做：

- 不做 chunking；这是下一小节“实现带元数据的文档切片”的内容。
- 不做 embedding、向量库写入或检索。
- 不实现完整 Markdown AST 解析。
- 不从 PDF、HTML 或其他格式抽取文本。

## Capabilities

### New Capabilities

- `text-extraction-normalization-learning`: 覆盖 Markdown 文本抽取和标准化学习，包括纯文本转换、空白归一化和来源元数据保留。

### Modified Capabilities

- `learning-roadmap`: Phase 2 文本抽取和标准化小节完成状态会在本 change 完成后更新。

## Impact

- 新增文本标准化模块和演示脚本。
- 新增测试：覆盖 Markdown 标题、链接、列表、代码围栏、空白归一化和文档元数据保留。
- 更新学习路线、OpenSpec 任务和学习笔记。
