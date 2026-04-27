# 项目说明

## 项目目标

本项目用于学习并构建一个接近生产标准的内部知识库 Agent。学习路线从 LLM 应用基础开始，逐步进入 RAG、检索优化、评测、工具调用、MCP 集成和生产化能力。

## 协作约定

- 面向人的文档统一使用中文。
- 代码标识符、包名、环境变量、命令和第三方 API 名称保持英文。
- `docs/agent-learning-todo.md` 是总路线图和阶段进度入口。
- `openspec/changes/` 中的每个 change 是某一阶段或较大功能的详细上下文。
- 实现前先读取对应 change 的 proposal、design、tasks 和 specs。
- 推进过程中及时更新 `tasks.md` 的勾选状态和必要的学习记录。

## 技术方向

- Phase 0 到 Phase 2 优先使用 Python-only 原型，降低学习噪音。
- 需要 UI 或管理后台时再引入 Node.js。
- 真实模型调用优先围绕 OpenAI Responses API 学习。
- RAG 与评测能力先用本地、可验证的方式实现，再引入更复杂的编排。

## OpenSpec 使用方式

当前环境未安装 OpenSpec CLI，因此先使用兼容的目录结构和文档约定：

- `openspec/specs/`：长期有效的能力规格。
- `openspec/changes/<change-id>/`：阶段性变更上下文。
- `openspec/changes/archive/`：后续归档完成的 change。

后续安装 CLI 后，再执行官方的 validate/archive 流程。
