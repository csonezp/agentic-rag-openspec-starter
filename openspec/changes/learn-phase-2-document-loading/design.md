## Context

项目的第一个知识源已经确定为本地 Markdown 知识库，路径为 `knowledge/`。当前目录里已有 `knowledge/README.md`，后续 Phase 2 会逐步把这些 Markdown 文档转成 chunks、embeddings 和检索上下文。

文档加载阶段需要保持简单、可测试、可追溯：它只负责把文件系统里的 Markdown 文件变成内存中的文档对象。

## Goals / Non-Goals

**Goals:**

- 递归发现指定目录下的 `*.md` 文件。
- 读取 UTF-8 Markdown 内容。
- 从第一个一级标题 `# ...` 提取文档标题。
- 返回稳定排序的文档对象，便于测试和后续处理。
- 保留相对来源路径，后续引用回答时可以使用。

**Non-Goals:**

- 不解析 Markdown AST。
- 不做文本清洗、标题层级抽取或段落标准化。
- 不做 chunking、embedding 或检索。
- 不支持非 Markdown 文件。

## Decisions

### Decision: 使用标准库实现

本小节不引入第三方 Markdown parser。文件发现使用 `pathlib.Path.rglob()`，读取使用 `Path.read_text(encoding="utf-8")`。这样学习重点集中在加载边界和元数据，而不是 parser 细节。

### Decision: 文档对象使用 dataclass

新增 `KnowledgeDocument` dataclass，包含：

- `source_path`：相对知识库根目录的 POSIX 风格路径。
- `title`：第一个一级标题；如果没有一级标题，则回退为文件 stem。
- `content`：原始 Markdown 文本。

后续小节如果需要更多元数据，再按需要扩展。

### Decision: 加载顺序稳定

加载器按相对路径排序返回文档，避免不同系统文件遍历顺序导致测试或后续索引结果不稳定。

## Risks / Trade-offs

- [Risk] Markdown 文件编码不是 UTF-8。→ 学习阶段约定使用 UTF-8，遇到解码错误直接暴露，后续可加入容错策略。
- [Risk] 标题提取过于简单。→ 当前只提取第一个 `# ` 标题；完整标题层级留到后续“抽取和标准化”小节。
- [Risk] 默认读取真实敏感数据。→ 默认源目录为仓库内 `knowledge/`，并在文档中继续强调不放真实敏感数据。
