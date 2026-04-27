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

## 学习小节工作流

- 用户可以通过“学习 Phase X 的某个小节”启动一个学习单元，例如“学习 Phase 1 的「学习 Responses API 的请求和响应结构」”。
- 正式进入学习或实验前，必须从 `main` 创建独立分支，分支名使用 `codex/learn-phase-<n>-<topic>` 形式；不要直接在 `main` 上提交学习过程变更。
- 收到这类请求后，先检查该小节是否已经完成：
  - 查看 `docs/agent-learning-todo.md` 中对应任务是否已勾选。
  - 查看 `openspec/changes/archive/`、相关学习记录和决策文档中是否已有完成记录。
- 如果该小节已经完成，只回复已完成，不创建 change、不修改文件、不重复实现。
- 如果该小节未完成，先创建独立 OpenSpec change，change id 使用 `learn-phase-<n>-<topic>` 形式。
- 学习小节 change 表示“开始学习和实验这个小节”，不默认代表完整功能交付。
- 创建 change 时必须明确告诉用户：
  - 新增或修改了哪些文件。
  - 每个文件为什么存在。
  - 本次 change 的学习目标、不做什么和完成标准。
- 只有在用户确认继续学习或执行时，才进入实验、代码修改或任务实施。
- 正式学习开始后，学习笔记、实验脚本、任务勾选和验证结果都提交到该学习分支；合并回 `main` 需要用户明确要求。
- 小节完成时至少更新三处上下文：
  - 对应 OpenSpec change 的 `tasks.md`。
  - `docs/agent-learning-todo.md` 中对应小节勾选状态。
  - 学习总结或决策记录，记录学到什么、验证结果、坑点和后续问题。
