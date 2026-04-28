## 1. 设计与测试

- [x] 1.1 创建 OpenSpec change，明确弱证据拒答学习目标、边界和验收标准。
- [x] 1.2 将“学习过程中的关键交互内容也要总结进学习文档”的规则写入 `AGENTS.md`。
- [x] 1.3 先编写 evidence check、拒答分支和脚本测试，并确认测试失败。

## 2. 实现

- [x] 2.1 新增证据判断结果对象和 `evaluate_evidence()`。
- [x] 2.2 让回答结果支持 `refused` 和 `refusal_reason`。
- [x] 2.3 调整回答脚本，支持 `--min-score` 和弱证据拒答分支。
- [x] 2.4 确保证据弱时不调用真实模型。

## 3. 文档与验证

- [x] 3.1 新增学习笔记，记录拒答策略、阈值取舍和本次交互总结。
- [x] 3.2 使用高阈值完成 dry-run 拒答演示。
- [x] 3.3 使用 FastEmbed + DeepSeek 完成证据足够时的真实回答演示。
- [x] 3.4 运行单元测试和 OpenSpec 严格校验。
- [x] 3.5 完成后更新 `tasks.md` 和 `docs/agent-learning-todo.md` 勾选状态。
