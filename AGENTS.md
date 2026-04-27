# 项目协作约定

## 文档语言

- 本项目的说明文档、进度文档、学习笔记、运行手册、任务记录等面向人的文本内容统一使用中文。
- 代码标识符、包名、命令、环境变量名、第三方 API 名称保持英文，不强行翻译。
- 后续新增或更新 `README.md`、`docs/` 下的文档、session log、todo/task 文档时，默认使用中文。

## 当前学习主线

- 以 [docs/agent-learning-todo.md](docs/agent-learning-todo.md) 作为 Agent 开发学习路线和进度追踪依据。
- 每次推进后，把完成项、关键决策和下一步问题记录回该文档。

## OpenSpec 工作流

- 本项目使用 `openspec/` 目录沉淀可追溯上下文。
- 每个新的学习阶段或较大功能，都应创建一个独立 change；Phase 1 的 change 只在用户明确启动 Phase 1 时创建。
- 每个 change 至少包含：
  - `proposal.md`：为什么做、做什么、不做什么、成功标准。
  - `design.md`：技术方案、边界、风险和取舍。
  - `tasks.md`：可验证的实施清单，推进时逐项勾选。
  - `specs/<capability>/spec.md`：能力级别的需求增量。
- 开始实现前，先读取对应 change 的 `proposal.md`、`design.md`、`tasks.md` 和相关 `specs/`。
- 完成并验证后，把任务勾选状态、学习记录和关键决策写回 change 文档；如果后续安装了 OpenSpec CLI，再执行 validate/archive。
- `docs/agent-learning-todo.md` 负责总路线和阶段状态，OpenSpec change 负责每个阶段的详细上下文。
