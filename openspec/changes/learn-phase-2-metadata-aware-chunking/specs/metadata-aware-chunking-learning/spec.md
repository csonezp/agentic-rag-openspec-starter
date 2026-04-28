## ADDED Requirements

### Requirement: 带元数据的文档切片

系统 MUST 能把标准化文档切分为多个可检索的小块，并为每个 chunk 保留最小元数据。

#### Scenario: 标准化文档被切片

- **WHEN** 开发者传入一个 `NormalizedDocument`
- **THEN** 系统 MUST 生成一个或多个 `DocumentChunk`
- **AND** 每个 chunk MUST 保留 `source_path`、`title`、`chunk_id`、`chunk_index`、`start_char`、`end_char` 和 `text`

### Requirement: 固定 chunk size 与 overlap

系统 MUST 支持最小固定窗口切片策略。

#### Scenario: 使用固定窗口切片

- **WHEN** 开发者提供 `chunk_size` 和 `overlap`
- **THEN** 系统 MUST 按固定窗口生成 chunks
- **AND** MUST 保证 `overlap < chunk_size`
- **AND** MUST 保持 chunk 顺序稳定

### Requirement: 本地演示验证

系统 MUST 提供一个最小演示入口，帮助学习者检查 chunk 结果。

#### Scenario: 对 `knowledge/` 运行切片演示

- **WHEN** 开发者运行本地演示脚本
- **THEN** 系统 MUST 输出每个 chunk 的基础元数据和文本摘要
- **AND** MUST 能看见 chunk 顺序和边界
