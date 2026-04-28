# Agent 开发学习 Todo

创建日期：2026-04-27

这份文档是本项目学习 Agent 开发的共享路线图。后续我们会把它作为推进依据：勾选任务、补充笔记、记录决策，并把每个里程碑拆成可执行任务。

## 总目标

构建一个“内部知识库 Agent”，它不只是一个简单聊天机器人：

- 能基于私有知识库回答问题。
- 能引用来源，并在证据不足时拒答。
- 能判断什么时候检索、什么时候追问、什么时候调用工具。
- 具备评测、追踪、日志和回归检查。
- 后续可以通过安全工具或 MCP 接入内部服务。

## 推荐的第一个项目

项目名称：内部知识库 Agent

MVP 形态：

- 支持 Markdown、PDF、HTML 或某一个选定工作区来源的文档导入。
- 切片时保留来源、标题层级、位置和更新时间。
- 先做向量检索，再逐步加入混合检索和 rerank。
- 提供支持流式输出的聊天 API。
- 所有有依据的回答都带来源引用。
- 检索证据不足时能够拒答。
- 支持反馈按钮和对话日志。
- 准备一个小型评测集和可重复运行的评测命令。
- 记录模型调用、检索命中、工具调用、延迟和成本等基础追踪信息。

## 技术方向

初始技术栈：

- Python 用于 RAG、评测和 Agent 实验。
- 如果后续需要前端，Node.js 用于 Web 服务、UI、流式输出和管理流程。
- Go 暂时后置，适合之后做高并发网关、内部服务或 MCP server。

候选库与服务：

- OpenAI Responses API 和 Agents SDK：用于 Agent 运行、托管工具、追踪和 file search 实验。
- LlamaIndex 或 LangChain：用于 RAG 实验。
- LangGraph：当基础 RAG 循环稳定后，用于有状态、偏生产级的编排。
- pgvector 或 Qdrant：用于本地向量存储。
- Qdrant、Weaviate、Pinecone 或托管 pgvector：用于生产化方案对比。
- Ragas、OpenAI Evals 或 trace grading：用于评测。
- OpenTelemetry、OpenAI tracing、LangSmith 或同类工具：用于可观测性。
- MCP：当核心系统足够可信后，用于工具和数据源集成。

## 项目文本约定

- 说明文档、进度文档、学习笔记、运行手册等面向人的文本内容统一使用中文。
- 代码标识符、包名、命令、环境变量、第三方 API 名称保持英文。
- 如果未来新增 README、设计文档、任务文档或 session log，默认使用中文。
- 这个约定同时记录在根目录 `AGENTS.md`，方便后续代理继续遵守。

## OpenSpec 管理约定

- 总学习路线继续由本文档维护。
- 每个学习阶段或较大功能使用 `openspec/changes/<change-id>/` 管理详细上下文。
- 从正式启动 Phase 1 开始，每个 Phase 默认创建独立 change，包含 `proposal.md`、`design.md`、`tasks.md` 和能力规格增量。
- 实现前读取对应 change，推进中更新任务勾选，完成后记录关键决策和验证结果。
- 如果后续安装了 OpenSpec CLI，再补充执行 `openspec validate` 和 `openspec archive`。

## 学习小节启动约定

- 用户通过“学习 Phase X 的某个小节”启动学习单元。
- 每个学习小节优先创建独立 OpenSpec change，而不是一次性推进整个 Phase。
- 正式进入学习或实验前，必须从 `main` 创建独立学习分支，分支名使用 `codex/learn-phase-<n>-<topic>` 形式。
- 不直接在 `main` 上提交学习过程变更；合并回 `main` 需要用户明确要求。
- 如果小节已完成，则不创建 change、不修改文件，只说明已完成。
- 如果小节未完成，change id 使用 `learn-phase-<n>-<topic>` 形式。
- 创建 change 后，先说明本次改了哪些文件、为什么这样改，再等待用户确认是否进入学习和实验。
- 小节完成时，必须更新 change 任务、本文档勾选状态，以及学习总结或决策记录。

## Phase 0：搭建与定位

- [x] 创建最小项目结构。
- [x] 选择初始语言拆分：Python-only 原型，或 Python 后端加 Node 前端。
- [x] 建立依赖管理。
- [x] 添加 API Key 和模型选择的环境变量约定。
- [x] 在仓库中添加简单运行手册。
- [x] 决定第一个知识源。

验收标准：

- 开发者可以在本地运行一个 hello-world 级别的模型调用入口。
- 仓库中有清晰的位置承载导入、检索、Agent 逻辑、评测和文档。

## Phase 1：LLM 应用基础

- [x] 学习 Responses API 的请求和响应结构。
- [x] 实现一个基础聊天调用。
- [x] 添加流式输出。
- [x] 接入 DeepSeek 官方 API 并完成真实模型调用。
- [x] 为一个小 schema 添加结构化输出。
- [x] 添加 function/tool calling，并接入一个本地函数。
- [x] 记录延迟、token 使用量、模型名和错误。

验收标准：

- 我们可以调用模型、流式输出、调用一个函数，并检查调用过程中发生了什么。

## Phase 2：基础 RAG

- [x] 为第一个来源类型实现文档加载。
- [x] 实现文本抽取和标准化。
- [x] 实现带元数据的文档切片。
- [x] 生成 embeddings。
- [x] 把向量存入本地向量库。
- [ ] 针对问题检索 top-k chunks。
- [ ] 基于检索上下文生成回答。
- [ ] 在回答中包含来源引用。
- [ ] 当检索证据较弱时拒答。

验收标准：

- 系统可以基于一个小型文档集合回答问题，并引用证据。

## Phase 3：检索质量提升

- [ ] 实验 chunk size 和 overlap。
- [ ] 添加元数据过滤。
- [ ] 添加关键词检索或 BM25。
- [ ] 添加混合检索。
- [ ] 添加 reranking。
- [ ] 为模糊问题或复合问题添加 query rewriting。
- [ ] 添加来源去重。
- [ ] 为每个回答添加检索调试输出。

验收标准：

- 在评测集上，检索质量可以被量化地提升。

## Phase 4：评测体系

- [ ] 创建 50 到 100 个代表性测试问题。
- [ ] 标注期望回答行为：可回答、不可回答、需要追问、需要工具。
- [ ] 为可回答问题记录期望来源文档。
- [ ] 构建可重复运行的评测命令。
- [ ] 评估回答正确性。
- [ ] 评估引用正确性。
- [ ] 评估拒答正确性。
- [ ] 保存实验结果。
- [ ] 对比至少两种检索配置。

验收标准：

- 我们修改 RAG 策略后，可以判断质量是提升还是回退。

## Phase 5：Agent 工具调用

- [ ] 定义工具接口约定。
- [ ] 添加一个只读知识库搜索工具。
- [ ] 添加一个非 RAG 的只读工具，例如服务状态、数据库 schema 查询或配置查询。
- [ ] 添加工具输入校验。
- [ ] 添加工具输出标准化。
- [ ] 添加工具调用追踪。
- [ ] 为可能修改状态的工具添加审批边界。

验收标准：

- Agent 可以在直接回答、搜索知识库、追问用户、调用只读工具之间做选择。

## Phase 6：Agent 工作流与 LangGraph

- [ ] 学习 workflow 与 agent pattern 的区别。
- [ ] 把当前流程建模成显式状态。
- [ ] 添加路由：检索、追问、回答、拒答或调用工具。
- [ ] 为对话添加持久状态。
- [ ] 为高风险动作添加 human-in-the-loop 检查点。
- [ ] 添加重试和 fallback。
- [ ] 向客户端流式输出状态更新。

验收标准：

- Agent 流程是显式、可检查、并且比单一 prompt loop 更容易调试的。

## Phase 7：MCP 集成

- [ ] 学习 MCP 概念：tools、resources、prompts、transports 和 authorization。
- [ ] 为知识库搜索工具构建一个本地只读 MCP server。
- [ ] 只开放 allowlist 中的工具。
- [ ] 校验所有工具参数。
- [ ] 把模型生成的工具输入视为不可信输入。
- [ ] 为 MCP 调用添加审计日志。
- [ ] 对比直接工具集成与 MCP 集成。

验收标准：

- 我们理解什么时候值得使用 MCP，并且拥有一个安全的本地只读 MCP 集成。

## Phase 8：生产化准备

- [ ] 添加认证。
- [ ] 添加按用户或租户隔离的文档权限。
- [ ] 防止跨租户检索。
- [ ] 添加速率限制和成本预算。
- [ ] 添加后台导入任务。
- [ ] 添加索引状态和重试处理。
- [ ] 添加 prompt injection 防护。
- [ ] 添加监控面板或结构化日志。
- [ ] 添加反馈 review 流程。
- [ ] 把回归评测接入 CI。

验收标准：

- 系统具备真实内部工具所需的最低安全、质量和运维控制。

## 安全注意事项

- 把检索到的文档、用户输入和工具输出都视为不可信。
- 不允许检索文本覆盖 system 或 developer 指令。
- 在审批和审计流程建立前，不开放会修改状态的工具。
- 学习阶段优先使用只读工具。
- 使用 schema 校验工具参数。
- 日志要足够支持调试，但不能泄露密钥或敏感文档内容。
- 使用真实私有数据前，先加入文档级权限控制。

## 后续需要反复确认的问题

- 第一个原型应该使用 OpenAI 托管 file search，还是自管理向量数据库？
- 第一个 UI 应该是简单聊天页、开发者控制台，还是两者都做？
- 第一个知识源应该导入什么？
- 哪个评测框架最适合我们的工作流？
- LangGraph 到什么时候才是帮助，而不是额外复杂度？
- 哪个内部工具能让 Agent 超越问答，真正变得有用？

## 学习记录

每次学习结束后，在这里留下简短记录。

### 2026-04-28 Phase 2 学习记录

- 启动并完成学习小节 `learn-phase-2-document-loading`，在独立分支 `codex/learn-phase-2-document-loading` 实现本地 Markdown 文档加载。
- 文档加载支持递归读取 `knowledge/**/*.md`，生成包含 `source_path`、`title`、`content` 的 `KnowledgeDocument`。
- 本小节只负责文件发现、读取和最小元数据保留，不做标准化、切片、embedding 或检索。
- 启动并完成学习小节 `learn-phase-2-text-extraction-normalization`，在独立分支 `codex/learn-phase-2-text-extraction-normalization` 实现 Markdown 文本抽取和标准化。
- 文本标准化支持标题、列表、链接、代码围栏和空白归一化，输出包含 `source_path`、`title`、`text` 的 `NormalizedDocument`。
- 启动并完成学习小节 `learn-phase-2-metadata-aware-chunking`，在独立分支 `codex/learn-phase-2-metadata-aware-chunking` 实现带元数据的固定窗口切片。
- 切片小节新增 `DocumentChunk`，保留 `chunk_id`、`source_path`、`title`、`chunk_index`、`start_char`、`end_char` 和 `text`，并支持 `chunk_size` 与 `overlap`。
- 启动并完成学习小节 `learn-phase-2-generate-embeddings`，在独立分支 `codex/learn-phase-2-generate-embeddings` 实现本地 deterministic embeddings。
- Embeddings 小节将 `DocumentChunk` 转换为 `EmbeddedChunk`，保留 chunk metadata，并使用可配置维度的 `HashingEmbeddingModel` 支撑后续向量库学习。
- 后续在 embeddings 小节补充 FastEmbed provider，默认使用 `BAAI/bge-small-zh-v1.5` 生成 512 维中文语义向量，同时保留 hashing provider 作为测试兜底。
- 启动并完成学习小节 `learn-phase-2-local-vector-store`，在独立分支 `codex/learn-phase-2-local-vector-store` 使用 Qdrant 本地模式写入向量。
- 本地向量库小节新增 `LocalQdrantVectorStore` 和 `scripts/index_knowledge_base.py`，把 chunk embedding、文本和 metadata 写入 Qdrant point，并用稳定 UUID point id 支持重复 upsert。

### 2026-04-27

- 确立学习方向：构建一个偏生产标准的知识库问答 Agent。
- 决定第一个项目重点关注 RAG 质量、引用、拒答、评测、追踪和安全工具调用。
- 创建本 todo 文档作为后续追踪基础。
- 在分支 `codex/agent-learning-phase-0` 开始 Phase 0。
- 为第一轮学习选择 Python-only 原型。
- 添加最小 Python 包、unittest 测试、环境变量模板、dry-run hello agent 脚本和 README 运行手册。
- 第一个知识源留到下一次继续决策。
- 根据用户要求，把项目说明文档、进度文档等面向人的文本统一改为中文，并在 `AGENTS.md` 记录为项目级约定。
- 接入 OpenSpec 目录结构，后续每个 Phase 默认通过独立 change 管理；Phase 1 change 会在正式启动 Phase 1 时再创建。
- 完成 Phase 0 最后一项：第一个知识源确定为仓库内本地 Markdown 知识库，路径为 `knowledge/`。
- 新增决策记录 `docs/decisions/0001-first-knowledge-source.md` 和 OpenSpec 知识源规格 `openspec/specs/knowledge-source/spec.md`。

### 2026-04-27 Phase 1 学习记录

- 启动学习小节 `learn-phase-1-responses-api-structure`，并在独立分支 `codex/learn-phase-1-responses-api-structure` 推进。
- 固化规则：正式学习或实验必须从 `main` 创建独立学习分支，不直接在 `main` 上提交学习过程变更。
- 完成 Responses API 请求和响应结构学习笔记，记录官方字段结构、最小请求/响应示例、input items、input token count，以及与 Chat Completions 的心智差异。
- 启动并完成学习小节 `learn-phase-1-basic-chat-call`，在独立分支 `codex/learn-phase-1-basic-chat-call` 实现基础聊天调用。
- 基础聊天调用支持命令行 prompt、默认 dry-run、显式 `--real` 真实模式，以及缺少 API Key 时的中文错误提示。
- 启动并完成学习小节 `learn-phase-1-streaming-output`，在独立分支 `codex/learn-phase-1-streaming-output` 添加流式输出。
- 流式输出支持 dry-run `--stream`、真实模式 `--real --stream`，并解析 Responses API streaming 的 `response.output_text.delta` 事件。
- 启动并完成学习小节 `learn-phase-1-deepseek-provider`，在独立分支 `codex/learn-phase-1-deepseek-provider` 接入 DeepSeek 官方 API。
- DeepSeek 接入支持 `MODEL_PROVIDER=deepseek`、非流式真实调用和流式真实调用，并保留 OpenAI Responses API 客户端用于前序学习成果回看。
- 启动并完成学习小节 `learn-phase-1-structured-output-schema`，在独立分支 `codex/learn-phase-1-structured-output-schema` 学习 DeepSeek JSON Output。
- 结构化输出小节实现 `LearningBrief` 小 schema、本地字段校验、dry-run 演示和真实 DeepSeek JSON Output 验证。
- 启动并完成学习小节 `learn-phase-1-tool-calling-local-function`，在独立分支 `codex/learn-phase-1-tool-calling-local-function` 学习 DeepSeek Tool Calls。
- Tool calling 小节实现 `get_phase1_progress` 本地只读函数、工具 allowlist、参数校验、模型 tool call 到本地执行再到最终回答的闭环。
- 启动并完成学习小节 `learn-phase-1-call-observability`，在独立分支 `codex/learn-phase-1-call-observability` 为 DeepSeek 非流式、流式和 tool calling 链路补齐最小调用观测。
- 调用观测小节统一输出 `observation:` 摘要块，覆盖 `model`、`latency_ms`、`input_tokens`、`output_tokens`、`total_tokens`、`error_type`、`error_message` 以及 tool calling 的 `tool_triggered`、`tool_names`、`success`。
- 已通过 `PYTHONPATH=src python3 -m unittest discover -s tests` 和 `openspec validate --all --strict` 验证当前实现，并已完成真实 DeepSeek 非流式调用与真实 tool calling 复核。
- 调用观测真实验证显示：CLI 能输出统一的 `observation:` 摘要，非流式链路可读到 `model / latency_ms / token`，tool calling 链路可读到 `tool_triggered / tool_names / success`。
