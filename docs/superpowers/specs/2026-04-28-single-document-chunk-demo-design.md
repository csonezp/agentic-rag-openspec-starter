# 单文档 Chunk Demo Design

日期：2026-04-28

## 背景

当前 `scripts/chunk_documents.py` 主要输出“多文档汇总视角”的 chunk 列表（chunk_id、start/end、chars）。它对快速确认“是否能切片”有帮助，但不够直观：很难从输出中看清楚“某个单文档的完整输入（原文/标准化）是怎样的，以及每个 chunk 的完整文本内容是什么”。

## 目标

- 提供一个只针对“单个文档”的 demo 脚本，能把完整输入与输出按固定格式打印出来，便于肉眼检查切片边界与内容连续性。
- 输出包含：
  - `KnowledgeDocument`：`source_path/title` + 原始 Markdown（完整）
  - `NormalizedDocument`：标准化后的 `text`（完整）+ 字符数
  - `DocumentChunk[]`：逐块打印 chunk 元数据与 `chunk.text`（完整）

## 不做

- 不修改 `chunker` 的核心切片逻辑。
- 不引入 embedding、向量库、检索等后续功能。
- 不把 `scripts/chunk_documents.py` 做成“大而全”的 verbose 输出模式（避免多文档情况下输出过吵）。

## 方案

### 新增脚本

新增 `scripts/chunk_one_document.py`，CLI 形态：

```bash
PYTHONPATH=src python3 scripts/chunk_one_document.py knowledge tool-calling.md --chunk-size 400 --overlap 40
```

- `source_dir`：默认 `knowledge`
- `source_path`：必填，表示相对 `source_dir` 的单个 Markdown 路径
- `--chunk-size` / `--overlap`：与现有切片一致

### 输出格式（稳定、可 grep）

输出按块分隔，且每块都有固定 header：

1. 基本信息
   - `source_dir=...`
   - `source_path=...`
   - `title=...`
2. 原始输入
   - `--- RAW MARKDOWN ---`
   - 原始 Markdown（完整）
3. 标准化输入
   - `--- NORMALIZED TEXT (chars=...) ---`
   - 标准化文本（完整）
4. 切片输出
   - `--- CHUNKS (n=...) ---`
   - 对每个 chunk：
     - `--- CHUNK #<idx> <chunk_id> start=<s> end=<e> chars=<n> ---`
     - chunk 文本（完整）

### 错误处理

- `source_path` 不存在：打印中文错误到 stderr，返回非 0。
- 参数非法（如 overlap >= chunk_size）：让底层 `chunk_document` 抛 `ValueError`，脚本捕获后打印中文错误到 stderr，返回非 0。

## 测试

新增 `tests/test_chunk_one_document_script.py`：

- 用临时目录创建一个 `note.md`（含标题/正文），运行 `main([...])` 捕获 stdout。
- 断言输出包含：
  - `--- RAW MARKDOWN ---`
  - `--- NORMALIZED TEXT`
  - `--- CHUNKS (n=`
  - `--- CHUNK #0 note.md#0`
  - 以及正文中的一段片段（证明 chunk 内容被完整打印）

## 验收标准

- demo 脚本能对单个文档打印“原始 Markdown + 标准化文本 + 每个 chunk 完整内容”。
- 单测通过：
  - `PYTHONPATH=src:. python3 -m unittest tests.test_chunk_one_document_script -v`
  - `PYTHONPATH=src:. python3 -m unittest discover -s tests`
*** End Patch}"}}
