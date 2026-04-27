# 知识源规格

## Purpose

定义本项目第一个 RAG 知识源及其演进边界，确保 Phase 2 的文档加载、切片和引用实现有明确输入来源。

## Requirements

### Requirement: 第一个知识源

系统 MUST 把仓库内本地 Markdown 知识库作为第一个 RAG 知识源。

#### Scenario: Phase 2 开始文档加载

- **WHEN** 开始实现基础 RAG 文档加载
- **THEN** 系统 MUST 优先读取 `knowledge/**/*.md`
- **AND** MUST 保留文件路径和标题层级作为元数据

### Requirement: 知识源可演进

系统 MUST 保持知识源扩展空间，允许后续增加 PDF、网页或企业知识库来源。

#### Scenario: 后续增加新知识源

- **WHEN** 新增 PDF、网页、飞书、Notion 或 Confluence 等来源
- **THEN** MUST 通过新的 OpenSpec change 记录范围、元数据和安全边界
