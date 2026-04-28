# Phase 2 Metadata-Aware Chunking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 `NormalizedDocument` 增加带元数据的固定窗口切片能力，输出可供后续 embedding 使用的 `DocumentChunk`。

**Architecture:** 新增独立的 chunking 模块，定义 `DocumentChunk` 和切片函数；在现有 `document_loader -> text_normalizer` 管线之后增加 `chunk_documents()`；通过一个演示脚本输出 chunk 的基础元数据和文本摘要，帮助学习者检查切片边界。整个实现保持在 Phase 2 基础 RAG 范围内，不扩展到 embedding 或检索。

**Tech Stack:** Python 3、标准库 `dataclasses`、`unittest`、现有 `document_loader` / `text_normalizer`

---

## File Map

- Create: `src/agent_kb/chunker.py`
  - 定义 `DocumentChunk`
  - 实现单文档与多文档切片函数
  - 处理 `chunk_size`、`overlap` 和基础元数据生成
- Create: `scripts/chunk_documents.py`
  - 组合加载、标准化和切片流程
  - 输出 chunk 数量、chunk 元数据和文本摘要
- Create: `tests/test_chunker.py`
  - 覆盖 chunk 大小、overlap、单文档/多文档切片、元数据保留和非法参数
- Modify: `docs/learning-notes/phase-2-metadata-aware-chunking.md`
  - 记录切片规则、元数据设计、验证命令和后续衔接点
- Modify: `docs/agent-learning-todo.md`
  - 勾选本小节并记录学习结论
- Modify: `openspec/changes/learn-phase-2-metadata-aware-chunking/tasks.md`
  - 回写任务勾选状态和验证结果

### Task 1: 定义 `DocumentChunk` 和切片边界

**Files:**
- Create: `src/agent_kb/chunker.py`
- Test: `tests/test_chunker.py`

- [ ] **Step 1: 写失败测试，固定单文档切片元数据**

```python
def test_chunk_document_preserves_metadata_and_ranges(self):
    document = NormalizedDocument(
        source_path="guide/intro.md",
        title="介绍",
        text="abcdefghij",
    )

    chunks = chunk_document(document, chunk_size=4, overlap=1)

    self.assertEqual(
        chunks,
        [
            DocumentChunk(
                chunk_id="guide/intro.md#0",
                source_path="guide/intro.md",
                title="介绍",
                chunk_index=0,
                start_char=0,
                end_char=4,
                text="abcd",
            ),
            DocumentChunk(
                chunk_id="guide/intro.md#1",
                source_path="guide/intro.md",
                title="介绍",
                chunk_index=1,
                start_char=3,
                end_char=7,
                text="defg",
            ),
            DocumentChunk(
                chunk_id="guide/intro.md#2",
                source_path="guide/intro.md",
                title="介绍",
                chunk_index=2,
                start_char=6,
                end_char=10,
                text="ghij",
            ),
        ],
    )
```

- [ ] **Step 2: 运行测试确认失败**

Run: `PYTHONPATH=src:. python3 -m unittest tests.test_chunker.ChunkerTest.test_chunk_document_preserves_metadata_and_ranges`

Expected: FAIL with `ModuleNotFoundError` or missing `chunk_document`

- [ ] **Step 3: 写最小实现**

```python
from dataclasses import dataclass

from agent_kb.text_normalizer import NormalizedDocument


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    source_path: str
    title: str
    chunk_index: int
    start_char: int
    end_char: int
    text: str


def chunk_document(
    document: NormalizedDocument,
    *,
    chunk_size: int,
    overlap: int,
) -> list[DocumentChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size 必须大于 0")
    if overlap < 0:
        raise ValueError("overlap 不能小于 0")
    if overlap >= chunk_size:
        raise ValueError("overlap 必须小于 chunk_size")

    chunks: list[DocumentChunk] = []
    start = 0
    chunk_index = 0
    step = chunk_size - overlap
    while start < len(document.text):
        end = min(start + chunk_size, len(document.text))
        text = document.text[start:end]
        chunks.append(
            DocumentChunk(
                chunk_id=f"{document.source_path}#{chunk_index}",
                source_path=document.source_path,
                title=document.title,
                chunk_index=chunk_index,
                start_char=start,
                end_char=end,
                text=text,
            )
        )
        if end == len(document.text):
            break
        start += step
        chunk_index += 1
    return chunks
```

- [ ] **Step 4: 增加非法参数失败测试**

```python
def test_chunk_document_rejects_invalid_overlap(self):
    document = NormalizedDocument("a.md", "A", "abcdef")

    with self.assertRaisesRegex(ValueError, "overlap 必须小于 chunk_size"):
        chunk_document(document, chunk_size=4, overlap=4)
```

- [ ] **Step 5: 运行测试确认通过**

Run: `PYTHONPATH=src:. python3 -m unittest tests.test_chunker -v`

Expected: PASS

- [ ] **Step 6: 提交**

```bash
git add src/agent_kb/chunker.py tests/test_chunker.py
git commit -m "feat: add metadata-aware chunk primitives"
```

### Task 2: 文档级切片函数

**Files:**
- Modify: `src/agent_kb/chunker.py`
- Test: `tests/test_chunker.py`

- [ ] **Step 1: 写失败测试，固定多文档切片顺序**

```python
def test_chunk_documents_preserves_document_order(self):
    documents = [
        NormalizedDocument("a.md", "A", "abcdef"),
        NormalizedDocument("b.md", "B", "uvwxyz"),
    ]

    chunks = chunk_documents(documents, chunk_size=4, overlap=0)

    self.assertEqual(
        [chunk.chunk_id for chunk in chunks],
        ["a.md#0", "a.md#1", "b.md#0", "b.md#1"],
    )
```

- [ ] **Step 2: 运行测试确认失败**

Run: `PYTHONPATH=src:. python3 -m unittest tests.test_chunker.ChunkerTest.test_chunk_documents_preserves_document_order`

Expected: FAIL with missing `chunk_documents`

- [ ] **Step 3: 写最小实现**

```python
def chunk_documents(
    documents: list[NormalizedDocument],
    *,
    chunk_size: int,
    overlap: int,
) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for document in documents:
        chunks.extend(
            chunk_document(document, chunk_size=chunk_size, overlap=overlap)
        )
    return chunks
```

- [ ] **Step 4: 增加空文本边界测试**

```python
def test_chunk_document_returns_empty_when_text_is_empty(self):
    document = NormalizedDocument("empty.md", "Empty", "")

    chunks = chunk_document(document, chunk_size=4, overlap=1)

    self.assertEqual(chunks, [])
```

- [ ] **Step 5: 运行测试确认通过**

Run: `PYTHONPATH=src:. python3 -m unittest tests.test_chunker -v`

Expected: PASS

- [ ] **Step 6: 提交**

```bash
git add src/agent_kb/chunker.py tests/test_chunker.py
git commit -m "feat: add document chunking pipeline"
```

### Task 3: 切片演示脚本

**Files:**
- Create: `scripts/chunk_documents.py`
- Test: `tests/test_chunker.py`

- [ ] **Step 1: 写失败测试，固定演示脚本输出**

```python
def test_demo_script_prints_chunk_summary(self):
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "note.md").write_text("# 标题\n\nabcdefghi", encoding="utf-8")
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = main([str(root), "--chunk-size", "4", "--overlap", "1"])

    self.assertEqual(exit_code, 0)
    self.assertIn("chunks=3", stdout.getvalue())
    self.assertIn("chunk_id=note.md#0", stdout.getvalue())
    self.assertIn("start=0", stdout.getvalue())
```

- [ ] **Step 2: 运行测试确认失败**

Run: `PYTHONPATH=src:. python3 -m unittest tests.test_chunker.ChunkerScriptTest.test_demo_script_prints_chunk_summary`

Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.chunk_documents'`

- [ ] **Step 3: 写最小实现**

```python
import sys
from argparse import ArgumentParser, Namespace
from typing import Optional, Sequence

from agent_kb.document_loader import load_markdown_documents
from agent_kb.text_normalizer import normalize_documents
from agent_kb.chunker import chunk_documents


def parse_args(argv: Sequence[str]) -> Namespace:
    parser = ArgumentParser(description="加载、标准化并切分本地 Markdown 文档。")
    parser.add_argument("source_dir", nargs="?", default="knowledge")
    parser.add_argument("--chunk-size", type=int, default=400)
    parser.add_argument("--overlap", type=int, default=40)
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    documents = load_markdown_documents(args.source_dir)
    normalized_documents = normalize_documents(documents)
    chunks = chunk_documents(
        normalized_documents,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
    )

    print(f"source_dir={args.source_dir}")
    print(f"chunks={len(chunks)}")
    for chunk in chunks:
        print(
            f"- chunk_id={chunk.chunk_id} source_path={chunk.source_path} "
            f"start={chunk.start_char} end={chunk.end_char} chars={len(chunk.text)}"
        )
    return 0
```

- [ ] **Step 4: 运行测试确认通过**

Run: `PYTHONPATH=src:. python3 -m unittest tests.test_chunker -v`

Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add scripts/chunk_documents.py tests/test_chunker.py
git commit -m "feat: add chunking demo script"
```

### Task 4: 文档、验证与回写

**Files:**
- Create: `docs/learning-notes/phase-2-metadata-aware-chunking.md`
- Modify: `docs/agent-learning-todo.md`
- Modify: `openspec/changes/learn-phase-2-metadata-aware-chunking/tasks.md`

- [ ] **Step 1: 写学习笔记**

```md
# Phase 2 学习笔记：带元数据的文档切片

日期：2026-04-28

## 本节学到什么

- `DocumentChunk` 是标准化文本进入 embedding 之前的稳定中间层。
- 最小 chunk 元数据至少要能支持来源回溯、顺序定位和字符范围定位。
- 固定字符窗口切片简单透明，适合作为第一版学习实现。
```

- [ ] **Step 2: 更新任务清单和路线图**

```md
- [x] 4.1 新增学习笔记，记录切片规则、元数据设计和后续衔接点。
- [x] 4.2 运行单元测试和 OpenSpec 严格校验。
- [x] 4.3 使用 `knowledge/` 完成本地切片演示验证。
- [x] 4.4 完成后更新 `tasks.md` 和 `docs/agent-learning-todo.md` 勾选状态。
```

- [ ] **Step 3: 运行完整验证**

Run: `PYTHONPATH=src python3 -m unittest discover -s tests`

Expected: PASS with all tests green

Run: `openspec validate --all --strict`

Expected: PASS with no spec validation errors

- [ ] **Step 4: 运行本地演示**

Run: `PYTHONPATH=src python3 scripts/chunk_documents.py knowledge --chunk-size 400 --overlap 40`

Expected: 输出 chunk 数量，以及每个 chunk 的 `chunk_id/source_path/start/end/chars`

- [ ] **Step 5: 提交**

```bash
git add docs/learning-notes/phase-2-metadata-aware-chunking.md docs/agent-learning-todo.md openspec/changes/learn-phase-2-metadata-aware-chunking/tasks.md
git commit -m "docs: record metadata-aware chunking learning results"
```

## Self-Review

- 规格覆盖：
  - `metadata-aware-chunking-learning/spec.md` 的 chunk 元数据、固定窗口切片和本地演示要求分别由 Task 1、Task 2、Task 3 和 Task 4 覆盖。
  - `learning-roadmap/spec.md` 的路线回写要求由 Task 4 覆盖。
- 占位符检查：
  - 计划内没有 `TBD`、`TODO`、`implement later` 之类的占位内容。
- 类型一致性：
  - 全文统一使用 `DocumentChunk`、`chunk_document()`、`chunk_documents()` 这几个类型和函数名。
