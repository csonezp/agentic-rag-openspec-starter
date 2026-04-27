# 内部知识库 Agent

这个仓库是一个学习型工作区，用来从零构建一个接近生产标准的知识库 Agent。

当前重点是 [docs/agent-learning-todo.md](docs/agent-learning-todo.md) 中的 Phase 1：学习 LLM 应用基础，并让后续每一步都容易运行和验证。

## 项目约定

- 说明文档、进度文档、学习记录、运行手册等面向人的文本内容统一使用中文。
- 代码标识符、第三方 API 名称、命令、环境变量名保持英文。
- 新增项目级约定时，优先记录到根目录 [AGENTS.md](AGENTS.md)。

## 项目结构

- `src/agent_kb/`：Python 包，后续承载 Agent、检索、配置、评测等代码。
- `scripts/`：本地学习和开发入口脚本。
- `tests/`：每个学习里程碑的回归测试。
- `docs/`：路线图、进度、决策记录和运行手册。
- `openspec/`：OpenSpec 项目说明、能力规格和阶段 change 文档。
- `knowledge/`：第一个本地 Markdown 知识源，Phase 2 会从这里开始实现基础 RAG。

## 本地命令

运行测试：

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

运行 dry-run hello agent：

```bash
PYTHONPATH=src python3 scripts/hello_model.py
```

使用 DeepSeek 官方 API 运行真实模型调用。密钥从本机环境变量读取，不需要写入代码或提交到 Git：

```bash
export MODEL_PROVIDER=deepseek
export DEEPSEEK_API_KEY=你的密钥
PYTHONPATH=src python3 scripts/hello_model.py --real "用一句话介绍这个项目"
```

使用 DeepSeek 官方 API 运行真实流式输出：

```bash
export MODEL_PROVIDER=deepseek
export DEEPSEEK_API_KEY=你的密钥
PYTHONPATH=src python3 scripts/hello_model.py --real --stream "用一句话介绍这个项目"
```

如果需要回看 OpenAI Responses API 学习成果，可以把 `MODEL_PROVIDER` 设置为 `openai`，并配置 `OPENAI_API_KEY`。

## 环境变量

真实模型密钥只从本机运行环境读取，例如当前 shell 的 `export`、`direnv`、系统 Secret 管理工具或 CI Secret。不要把真实密钥写入代码、README、`.env.example` 或任何会提交到 Git 的文件。

`.env`、`.env.local` 等本地密钥文件已被 `.gitignore` 忽略；`.env.example` 只是可提交模板，不能填写真实密钥。

默认真实 provider 是 DeepSeek：

- `MODEL_PROVIDER=deepseek`
- `DEEPSEEK_API_KEY`：DeepSeek 官方 API Key。
- `DEEPSEEK_BASE_URL`：默认 `https://api.deepseek.com`。
- `DEEPSEEK_MODEL`：默认 `deepseek-v4-flash`。

项目默认仍使用 dry-run 模型客户端，这样在没有网络和 API Key 的情况下也能运行。

## 当前学习主线

共享路线图和进度清单见 [docs/agent-learning-todo.md](docs/agent-learning-todo.md)。

每个新的学习阶段或较大功能，使用 `openspec/changes/` 下的独立 change 管理上下文。Phase 1 每个学习小节都使用独立分支和独立 OpenSpec change 推进。
