## ADDED Requirements

### Requirement: Markdown document discovery

项目 MUST 能从指定知识库目录递归发现 Markdown 文件。

#### Scenario: 发现 Markdown 文件

- **WHEN** 知识库目录包含一个或多个 `*.md` 文件
- **THEN** 文档加载器 MUST 返回这些 Markdown 文件对应的文档对象
- **AND** MUST 忽略非 Markdown 文件

#### Scenario: 空知识库目录

- **WHEN** 知识库目录不存在 Markdown 文件
- **THEN** 文档加载器 MUST 返回空列表

### Requirement: Document metadata

项目 MUST 为每个加载到的 Markdown 文件保留基础来源元数据。

#### Scenario: 加载带标题的 Markdown

- **WHEN** Markdown 文件包含一级标题
- **THEN** 文档对象 MUST 使用第一个一级标题作为 `title`
- **AND** MUST 保留相对来源路径 `source_path`
- **AND** MUST 保留原始 Markdown `content`

#### Scenario: 加载无一级标题的 Markdown

- **WHEN** Markdown 文件不包含一级标题
- **THEN** 文档对象 MUST 使用文件名 stem 作为 `title`

### Requirement: Stable loading order

项目 MUST 以稳定顺序返回加载结果。

#### Scenario: 多文件加载

- **WHEN** 知识库目录包含多个 Markdown 文件
- **THEN** 文档对象 MUST 按相对来源路径升序返回

### Requirement: Document loading learning record

本小节完成时 MUST 记录文档加载的实现方式、验证结果和后续边界。

#### Scenario: 完成文档加载小节

- **WHEN** 文档加载小节完成
- **THEN** 对应 OpenSpec change 的 `tasks.md` MUST 全部勾选
- **AND** `docs/agent-learning-todo.md` 中对应小节 MUST 勾选
- **AND** MUST 新增或更新学习总结文档
