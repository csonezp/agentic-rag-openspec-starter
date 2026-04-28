# Tool Calling 执行闭环

Tool calling 让模型可以请求调用外部函数，但模型不会自己执行函数。它只会返回 tool call，说明想调用哪个函数以及传入什么 arguments。真正的函数执行必须由本地代码完成。

本项目的第一个本地工具是 `get_phase1_progress`。它是只读函数，用于返回 Phase 1 学习进度和下一步事项。这个函数不访问网络、不写文件，也不接受用户传入的参数。

一次完整 tool calling 通常包含两个模型回合。第一回合，本地代码把用户问题和 tools schema 发给模型。模型返回 `tool_calls`。然后本地 runner 校验工具名在 allowlist 中，解析 arguments，执行函数。第二回合，本地代码把工具结果作为 `role=tool` 消息发回模型，模型再生成最终自然语言回答。

所有工具名和 arguments 都必须视为不可信输入。即使工具 schema 声明了参数格式，也不能跳过本地校验。学习阶段只开放只读工具，不开放会修改状态的工具。

## 可验证事实

- 模型不会自己执行函数。
- 当前本地工具是 `get_phase1_progress`。
- 工具必须在 allowlist 中才允许执行。
- 学习阶段只开放只读工具。
