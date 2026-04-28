# Phase 2 学习笔记：文本抽取和标准化

日期：2026-04-28

## 学习目标

本小节把上一节加载到的原始 Markdown 文档转换为后续切片可使用的稳定文本。它位于“文档加载”和“文档切片”之间，是基础 RAG 管线里的清洗层。

## 本小节实现

- 新增 `NormalizedDocument` dataclass。
- 新增 `normalize_markdown_text()`，把 Markdown 原文转换为较干净的纯文本。
- 新增 `normalize_document()` 和 `normalize_documents()`，在标准化后保留 `source_path`、`title` 和 `text`。
- 新增 `scripts/normalize_documents.py`，用于查看标准化摘要。

## 当前标准化规则

- 移除一级到六级标题前缀 `#`，保留标题文本。
- 移除无序列表前缀 `-`、`*`，保留列表内容。
- 移除有序列表前缀 `1.`，保留列表内容。
- 将 Markdown 链接 `[label](url)` 转成 `label`。
- 移除代码围栏 ```，保留代码内容。
- 压缩行内多余空格和 tab。
- 将三个及以上连续换行压缩为一个空行。

## 边界

本小节不做：

- 完整 Markdown AST 解析。
- 标题层级 metadata 抽取。
- chunking。
- embedding。
- 向量库写入。
- 检索和回答生成。

这些会在 Phase 2 后续小节继续推进。

## 关键认知

- 文本标准化会影响 embedding 输入质量，因此规则必须稳定、可测试。
- 标准化不能过度清洗：本小节保留标题文本和代码内容，只移除语法符号。
- `KnowledgeDocument` 和 `NormalizedDocument` 分层后，后续排查问题时可以判断错误来自加载、标准化还是切片。

## 验证记录

- 单元测试覆盖标题、列表、链接、代码围栏、空白归一化、文档元数据保留和演示脚本。
- 本地演示使用 `scripts/normalize_documents.py knowledge`。
- 单元测试验证命令：`PYTHONPATH=src:. python3 -m unittest discover -s tests`，结果为 79 个测试通过。
- OpenSpec 验证命令：`/opt/homebrew/bin/openspec validate --all --strict`，结果为 12 项通过。
- 本地标准化演示命令：`PYTHONPATH=src:. python3 scripts/normalize_documents.py knowledge`，结果为标准化 1 个 Markdown 文档。

## 后续问题

- 下一小节需要决定 chunk 的最小 metadata：`source_path`、`title`、chunk index、字符范围等。
- 是否需要把 Markdown 标题层级提取为 chunk metadata。
- 是否要保留链接 URL 作为引用 metadata，而不是只保留链接文本。
