# Phase 2 学习笔记：带元数据的文档切片

日期：2026-04-28

## 学习目标

本小节把上一节的 `NormalizedDocument` 转换为可供后续 embedding 使用的 `DocumentChunk`。它位于“文本标准化”和“embedding 生成”之间，是基础 RAG 管线里的切片层。

## 本小节实现

- 新增 `DocumentChunk` dataclass。
- 新增 `chunk_document()`，把单篇标准化文档切成固定窗口 chunks。
- 新增 `chunk_documents()`，支持按文档顺序批量切片。
- 新增 `scripts/chunk_documents.py`，用于查看本地 `knowledge/` 的 chunk 摘要。

## 当前元数据设计

每个 chunk 当前保留：

- `chunk_id`
- `source_path`
- `title`
- `chunk_index`
- `start_char`
- `end_char`
- `text`

这组字段足够支持：

- 后续 embedding 输入追踪
- 检索命中后的来源回溯
- 引用定位和调试输出

## 当前切片规则

- 先在 `NormalizedDocument.text` 上做固定字符窗口切片。
- `chunk_size` 表示单个 chunk 最多保留多少字符。
- `overlap` 表示下一个 chunk 与前一个 chunk 的重叠字符数。
- 下一块起点 = `上一块终点 - overlap`。
- `overlap` 必须小于 `chunk_size`。
- 空文本不会生成 chunk。

## 边界

本小节不做：

- token 级切片。
- 语义分块。
- 标题层级感知切片。
- embedding。
- 向量库写入。
- 检索和回答生成。

这些会在 Phase 2 后续小节继续推进。

## 关键认知

- `DocumentChunk` 是后续 embedding 和检索的稳定中间层。
- 第一版先用字符窗口切片，优点是规则透明、测试简单、边界清晰。
- 元数据设计不能只关心“能切出来”，还要关心后续引用和调试是否可回溯。
- overlap 会提高上下文连续性，但也会引入重复内容，后续 Phase 3 可以再评估 chunk size 和 overlap 组合。

## 验证记录

- 单元测试覆盖 chunk 元数据、字符范围、非法 overlap、空文本边界和演示脚本输出。
- 全量测试命令：`PYTHONPATH=src python3 -m unittest discover -s tests`
- OpenSpec 校验命令：`openspec validate --all --strict`
- 本地演示命令：`PYTHONPATH=src python3 scripts/chunk_documents.py knowledge --chunk-size 400 --overlap 40`

## 后续问题

- 后续 embedding 阶段是否要把 `chunk_size` 从字符数升级为 token 数。
- 是否需要把标题层级、更新时间等信息进一步加入 chunk metadata。
- 当检索需要更高质量时，是否要从固定窗口切片升级到句子感知或标题感知切片。
