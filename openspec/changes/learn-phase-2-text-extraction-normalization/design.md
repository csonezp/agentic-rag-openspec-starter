## Context

当前 `load_markdown_documents()` 返回的是原始 Markdown 文本。后续做 chunking 时，如果直接切原始 Markdown，会把链接语法、围栏符号和不稳定空白带入 embeddings，影响检索质量和可读性。

本小节先实现一个轻量标准化层，输出可供后续切片使用的 `NormalizedDocument`。

## Goals / Non-Goals

**Goals:**

- 把 Markdown 原文转换为稳定纯文本。
- 保留 `source_path` 和 `title`。
- 归一化换行和多余空白。
- 保留代码块内容，但移除 ``` 围栏。
- 将 Markdown 链接 `[text](url)` 转为 `text`。
- 为后续切片提供稳定输入。

**Non-Goals:**

- 不做完整 Markdown 语法解析。
- 不做标题层级 metadata 抽取。
- 不做 chunking 或 overlap。
- 不做 embedding。

## Decisions

### Decision: 使用标准库正则做轻量规则

本小节不引入 Markdown parser。先用标准库 `re` 实现可读、可测试的最小规则：

- 移除一级到六级标题前缀 `#`，保留标题文本。
- 移除列表前缀 `-`、`*`、`1.`，保留列表内容。
- 将 `[label](url)` 转换为 `label`。
- 移除代码围栏行，保留代码内容。
- 多个空行压缩为一个空行，行内多空白压缩为单空格。

### Decision: 标准化对象独立于加载对象

`KnowledgeDocument` 表示“从来源加载到的原始文档”；`NormalizedDocument` 表示“进入切片前的文本”。分层后便于调试：如果检索质量有问题，可以判断是加载、标准化还是切片阶段引入的。

## Risks / Trade-offs

- [Risk] 轻量正则无法覆盖完整 Markdown。→ 学习阶段先覆盖常见文档形态，复杂结构后续按需要引入 parser。
- [Risk] 标准化过度导致丢失上下文。→ 保留标题文本和代码内容，只移除语法符号。
- [Risk] 链接 URL 被移除后丢失引用信息。→ 当前先保留链接文本；如后续需要 URL 引用，可扩展 metadata。
