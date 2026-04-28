# Phase 2 学习笔记：为第一个来源类型实现文档加载

日期：2026-04-28

## 学习目标

本小节进入基础 RAG 的第一步：把第一个知识源类型加载为程序可处理的文档对象。当前项目的第一个知识源是仓库内 `knowledge/` 目录下的本地 Markdown 文件。

## 本小节实现

- 新增 `KnowledgeDocument` dataclass。
- 新增 `load_markdown_documents()`，递归读取指定目录下的 `*.md` 文件。
- 新增 `extract_markdown_title()`，从第一个一级标题 `# ...` 提取文档标题。
- 文档对象保留：
  - `source_path`：相对知识库根目录的 POSIX 风格路径。
  - `title`：第一个一级标题；没有一级标题时使用文件名 stem。
  - `content`：原始 Markdown 内容。
- 新增 `scripts/load_documents.py`，用于查看加载摘要。

## 边界

文档加载阶段只做三件事：

- 找到文件。
- 读取内容。
- 保留最小来源元数据。

它不做：

- Markdown 正文标准化。
- 标题层级和段落结构抽取。
- 文档切片。
- embedding。
- 向量库写入。
- 检索或回答生成。

这些会在 Phase 2 后续小节继续推进。

## 关键认知

- 文档加载不是 RAG 的全部，它只是把外部知识源带入系统的第一层边界。
- 加载结果要稳定排序，否则后续索引、测试和调试容易出现不可重复行为。
- 早期保留 `source_path` 很重要，后续引用来源、定位问题和回放评测都会用到。
- 当前标题提取故意简单，只找第一个一级标题；更完整的 Markdown 结构处理留给“文本抽取和标准化”小节。

## 验证记录

- 单元测试覆盖标题提取、递归加载、忽略非 Markdown、无标题回退、空目录和演示脚本输出。
- 本地演示使用 `scripts/load_documents.py knowledge`。
- 单元测试验证命令：`PYTHONPATH=src:. python3 -m unittest discover -s tests`，结果为 74 个测试通过。
- OpenSpec 验证命令：`/opt/homebrew/bin/openspec validate --all --strict`，结果为 11 项通过。
- 本地文档加载演示命令：`PYTHONPATH=src:. python3 scripts/load_documents.py knowledge`，结果为加载 1 个 Markdown 文档。

## 后续问题

- 下一小节需要定义“抽取和标准化”后的文本形态。
- 是否要保留 Markdown 标题层级为 metadata。
- 是否要记录文件更新时间、文件大小和内容 hash，方便后续增量索引。
