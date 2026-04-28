## Why

Phase 2 的目标是实现基础 RAG，而 RAG 的第一步是把知识源加载成程序可处理的文档对象。当前项目已经确定第一个知识源为仓库内 `knowledge/` 目录下的本地 Markdown 文件，因此需要先实现 Markdown 文档加载能力。

本小节用于学习“文档加载”和后续“文本抽取、切片、embedding、检索”的边界：加载阶段只负责发现文件、读取内容和保留来源元数据，不提前做切片或向量化。

## What Changes

- 在 Phase 2 中推进“为第一个来源类型实现文档加载”小节。
- 新增 Markdown 文档加载模块，递归读取指定目录下的 `*.md` 文件。
- 定义文档对象，保留 `source_path`、`title`、`content` 等基础元数据。
- 新增演示脚本，用于查看加载到的文档摘要。
- 新增测试和学习笔记，记录加载边界、异常处理和后续衔接点。

不做：

- 不做 Markdown 正文标准化；这是下一小节“实现文本抽取和标准化”的内容。
- 不做文档切片、embedding、向量库写入或检索。
- 不加载 PDF、HTML、Word 等其他来源类型。
- 不读取 `knowledge/` 之外的任意路径作为默认数据源。

## Capabilities

### New Capabilities

- `document-loading-learning`: 覆盖本地 Markdown 文档加载学习，包括文件发现、读取、标题提取和基础元数据保留。

### Modified Capabilities

- `learning-roadmap`: Phase 2 文档加载小节完成状态会在本 change 完成后更新。

## Impact

- 新增文档加载模块和演示脚本。
- 新增测试：覆盖 Markdown 文件发现、标题提取、空目录、非 Markdown 文件忽略和排序稳定性。
- 更新学习路线、OpenSpec 任务和学习笔记。
