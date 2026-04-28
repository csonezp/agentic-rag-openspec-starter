## ADDED Requirements

### Requirement: Markdown text extraction

项目 MUST 能从 Markdown 文档中抽取可用于后续切片的纯文本。

#### Scenario: 抽取常见 Markdown 语法

- **WHEN** Markdown 内容包含标题、列表、链接和代码围栏
- **THEN** 标准化文本 MUST 移除 Markdown 语法符号
- **AND** MUST 保留可读文本内容

### Requirement: Whitespace normalization

项目 MUST 对抽取后的文本做稳定空白归一化。

#### Scenario: 归一化空白

- **WHEN** 文本包含多余空格、制表符或连续空行
- **THEN** 标准化文本 MUST 压缩行内多余空白
- **AND** MUST 将多个连续空行压缩为一个空行

### Requirement: Normalized document metadata

项目 MUST 在标准化后保留文档来源元数据。

#### Scenario: 标准化已加载文档

- **WHEN** 系统标准化一个 `KnowledgeDocument`
- **THEN** 输出对象 MUST 保留 `source_path`
- **AND** MUST 保留 `title`
- **AND** MUST 包含标准化后的 `text`

### Requirement: Text extraction learning record

本小节完成时 MUST 记录文本抽取和标准化的实现方式、验证结果和后续边界。

#### Scenario: 完成文本抽取和标准化小节

- **WHEN** 文本抽取和标准化小节完成
- **THEN** 对应 OpenSpec change 的 `tasks.md` MUST 全部勾选
- **AND** `docs/agent-learning-todo.md` 中对应小节 MUST 勾选
- **AND** MUST 新增或更新学习总结文档
