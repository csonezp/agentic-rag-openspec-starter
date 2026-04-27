# 内部知识库 Agent

这个仓库是一个学习型工作区，用来从零构建一个接近生产标准的知识库 Agent。

当前重点是 [docs/agent-learning-todo.md](docs/agent-learning-todo.md) 中的 Phase 0：建立最小项目结构、沉淀协作约定，并让后续每一步都容易运行和验证。

## 项目约定

- 说明文档、进度文档、学习记录、运行手册等面向人的文本内容统一使用中文。
- 代码标识符、第三方 API 名称、命令、环境变量名保持英文。
- 新增项目级约定时，优先记录到根目录 [AGENTS.md](AGENTS.md)。

## 项目结构

- `src/agent_kb/`：Python 包，后续承载 Agent、检索、配置、评测等代码。
- `scripts/`：本地学习和开发入口脚本。
- `tests/`：每个学习里程碑的回归测试。
- `docs/`：路线图、进度、决策记录和运行手册。

## 本地命令

运行测试：

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

运行 Phase 0 的 dry-run hello agent：

```bash
PYTHONPATH=src python3 scripts/hello_model.py
```

## 环境变量

当我们开始接入真实模型服务时，把 `.env.example` 复制为 `.env` 并填写密钥。

Phase 0 故意使用 dry-run 模型客户端，这样项目在没有网络和 API Key 的情况下也能运行。

## 当前学习主线

共享路线图和进度清单见 [docs/agent-learning-todo.md](docs/agent-learning-todo.md)。
