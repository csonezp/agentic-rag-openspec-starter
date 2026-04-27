# Phase 1 Call Observability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为当前 DeepSeek 主链补充最小调用观测能力，让真实调用可以输出模型名、延迟、token 使用量和错误信息。

**Architecture:** 新增一个轻量观测模型文件，集中定义 usage、调用摘要和脚本打印格式；`DeepSeekChatCompletionsModelClient` 负责提取 provider 响应中的 usage/model/error，并返回观测结果；`ToolCallingRunner` 在不改变主流程的前提下补充 tool call 过程观测，两个 CLI 脚本只负责打印摘要。

**Tech Stack:** Python 3、标准库 `dataclasses`、`time`、`unittest`、现有 DeepSeek HTTP 客户端

---

## File Map

- Create: `src/agent_kb/call_observability.py`
  - 定义 `UsageMetrics`、`CallObservation`、`ToolCallObservation` 等轻量数据结构。
  - 提供统一的摘要格式化函数，避免脚本重复拼接打印逻辑。
- Modify: `src/agent_kb/deepseek_client.py`
  - 提取 `usage`、`model`、错误信息。
  - 为非流式、流式和 tool calling 提供带观测结果的调用入口。
- Modify: `src/agent_kb/tool_calling.py`
  - 在 runner 中记录是否触发 tool、tool 名、最终成功或失败。
- Modify: `scripts/hello_model.py`
  - 在真实调用完成后打印统一观测摘要。
- Modify: `scripts/tool_calling_demo.py`
  - 在真实 tool calling 完成后打印统一观测摘要。
- Test: `tests/test_deepseek_client.py`
  - 增加 usage 提取、错误展示、流式观测结果测试。
- Test: `tests/test_tool_calling.py`
  - 增加 tool calling 观测和脚本打印测试。
- Create: `docs/learning-notes/phase-1-call-observability.md`
  - 记录字段来源、统计口径、流式限制和真实验证结果。
- Modify: `docs/agent-learning-todo.md`
  - 完成后勾选本小节并写学习记录。
- Modify: `openspec/changes/learn-phase-1-call-observability/tasks.md`
  - 勾选任务状态并补学习结论。

### Task 1: 观测数据结构

**Files:**
- Create: `src/agent_kb/call_observability.py`
- Test: `tests/test_deepseek_client.py`

- [ ] **Step 1: 写失败测试，固定 usage 和摘要格式**

```python
from agent_kb.call_observability import CallObservation, UsageMetrics, format_observation_lines


def test_format_observation_lines_renders_usage_and_error():
    observation = CallObservation(
        provider="deepseek",
        model="deepseek-v4-flash",
        latency_ms=321,
        usage=UsageMetrics(input_tokens=11, output_tokens=7, total_tokens=18),
        error="none",
    )

    lines = format_observation_lines(observation)

    assert lines == [
        "provider=deepseek",
        "model=deepseek-v4-flash",
        "latency_ms=321",
        "input_tokens=11",
        "output_tokens=7",
        "total_tokens=18",
        "error=none",
    ]
```

- [ ] **Step 2: 运行测试确认失败**

Run: `PYTHONPATH=src:. python3 -m unittest tests.test_deepseek_client.DeepSeekClientTest.test_format_observation_lines_renders_usage_and_error`

Expected: FAIL with `ModuleNotFoundError` or `cannot import name 'CallObservation'`

- [ ] **Step 3: 写最小实现**

```python
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UsageMetrics:
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    total_tokens: Optional[int]


@dataclass(frozen=True)
class CallObservation:
    provider: str
    model: str
    latency_ms: int
    usage: UsageMetrics
    error: str


def format_observation_lines(observation: CallObservation) -> list[str]:
    return [
        f"provider={observation.provider}",
        f"model={observation.model}",
        f"latency_ms={observation.latency_ms}",
        f"input_tokens={observation.usage.input_tokens}",
        f"output_tokens={observation.usage.output_tokens}",
        f"total_tokens={observation.usage.total_tokens}",
        f"error={observation.error}",
    ]
```

- [ ] **Step 4: 运行测试确认通过**

Run: `PYTHONPATH=src:. python3 -m unittest tests.test_deepseek_client.DeepSeekClientTest.test_format_observation_lines_renders_usage_and_error`

Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add src/agent_kb/call_observability.py tests/test_deepseek_client.py
git commit -m "feat: add call observation primitives"
```

### Task 2: DeepSeek 客户端提取 usage、model 和延迟

**Files:**
- Modify: `src/agent_kb/deepseek_client.py`
- Test: `tests/test_deepseek_client.py`

- [ ] **Step 1: 写失败测试，固定非流式 usage 提取**

```python
def test_complete_with_observation_extracts_usage_and_model(self):
    config = AppConfig.from_env({"DEEPSEEK_API_KEY": "deepseek-key"})

    def fake_urlopen(request, timeout):
        return FakeResponse(
            {
                "model": "deepseek-v4-flash",
                "usage": {
                    "prompt_tokens": 8,
                    "completion_tokens": 5,
                    "total_tokens": 13,
                },
                "choices": [{"message": {"content": "你好"}}],
            }
        )

    with patch("agent_kb.deepseek_client.urllib.request.urlopen", fake_urlopen):
        result = DeepSeekChatCompletionsModelClient(config).complete_with_observation("你好")

    self.assertEqual(result.text, "你好")
    self.assertEqual(result.observation.model, "deepseek-v4-flash")
    self.assertEqual(result.observation.usage.input_tokens, 8)
    self.assertEqual(result.observation.usage.output_tokens, 5)
    self.assertEqual(result.observation.usage.total_tokens, 13)
```

- [ ] **Step 2: 运行测试确认失败**

Run: `PYTHONPATH=src:. python3 -m unittest tests.test_deepseek_client.DeepSeekClientTest.test_complete_with_observation_extracts_usage_and_model`

Expected: FAIL with `AttributeError: 'DeepSeekChatCompletionsModelClient' object has no attribute 'complete_with_observation'`

- [ ] **Step 3: 写最小实现**

```python
@dataclass(frozen=True)
class CompletionResult:
    text: str
    observation: CallObservation


def _extract_usage(payload: dict) -> UsageMetrics:
    usage = payload.get("usage", {})
    return UsageMetrics(
        input_tokens=usage.get("prompt_tokens"),
        output_tokens=usage.get("completion_tokens"),
        total_tokens=usage.get("total_tokens"),
    )


def complete_with_observation(self, prompt: str) -> CompletionResult:
    started_at = time.monotonic()
    payload = self._post_json(self._build_request(prompt, stream=False))
    observation = CallObservation(
        provider="deepseek",
        model=payload.get("model", self._config.deepseek_model),
        latency_ms=int((time.monotonic() - started_at) * 1000),
        usage=_extract_usage(payload),
        error="none",
    )
    return CompletionResult(
        text=_extract_message_content(payload),
        observation=observation,
    )
```

- [ ] **Step 4: 写失败测试，固定流式结束后摘要**

```python
def test_stream_with_observation_returns_chunks_and_summary(self):
    config = AppConfig.from_env({"DEEPSEEK_API_KEY": "deepseek-key"})

    stream_lines = [
        'data: {"model":"deepseek-v4-flash","choices":[{"delta":{"content":"流"}}]}\n'.encode("utf-8"),
        'data: {"usage":{"prompt_tokens":3,"completion_tokens":1,"total_tokens":4},"choices":[{"delta":{}}]}\n'.encode("utf-8"),
        b"data: [DONE]\n",
    ]

    class StreamingResponse:
        def __enter__(self):
            return stream_lines
        def __exit__(self, exc_type, exc, traceback):
            return False

    with patch("agent_kb.deepseek_client.urllib.request.urlopen", lambda request, timeout: StreamingResponse()):
        chunks, observation = DeepSeekChatCompletionsModelClient(config).stream_with_observation("流式")

    self.assertEqual(list(chunks), ["流"])
    self.assertEqual(observation.usage.total_tokens, 4)
```

- [ ] **Step 5: 实现流式观测和错误保留**

```python
def parse_deepseek_stream_events(lines: Iterable[bytes]) -> tuple[list[str], dict]:
    chunks: list[str] = []
    meta: dict = {"model": None, "usage": {}}
    for raw_line in lines:
        line = raw_line.decode("utf-8").strip()
        if not line.startswith("data: "):
            continue
        data = line.removeprefix("data: ")
        if data == "[DONE]":
            break
        payload = json.loads(data)
        meta["model"] = payload.get("model") or meta["model"]
        if payload.get("usage"):
            meta["usage"] = payload["usage"]
        for choice in payload.get("choices", []):
            content = choice.get("delta", {}).get("content")
            if content:
                chunks.append(content)
    return chunks, meta
```

- [ ] **Step 6: 运行 DeepSeek 客户端测试**

Run: `PYTHONPATH=src:. python3 -m unittest tests.test_deepseek_client -v`

Expected: PASS

- [ ] **Step 7: 提交**

```bash
git add src/agent_kb/deepseek_client.py src/agent_kb/call_observability.py tests/test_deepseek_client.py
git commit -m "feat: add DeepSeek call observations"
```

### Task 3: Tool calling 过程观测

**Files:**
- Modify: `src/agent_kb/tool_calling.py`
- Test: `tests/test_tool_calling.py`

- [ ] **Step 1: 写失败测试，固定 tool 调用摘要**

```python
def test_runner_records_triggered_tool_name(self):
    client = FakeToolClient()
    runner = ToolCallingRunner(
        client=client,
        tools=[ToolDefinition(schema=get_phase1_progress_tool(), handler=get_phase1_progress)],
    )

    result = runner.run_with_observation("请查询 Phase 1 进度")

    self.assertEqual(result.answer, "Phase 1 已调用工具并生成回答。")
    self.assertTrue(result.observation.tool_called)
    self.assertEqual(result.observation.tool_name, "get_phase1_progress")
    self.assertEqual(result.observation.error, "none")
```

- [ ] **Step 2: 运行测试确认失败**

Run: `PYTHONPATH=src:. python3 -m unittest tests.test_tool_calling.ToolCallingTest.test_runner_records_triggered_tool_name`

Expected: FAIL with `AttributeError: 'ToolCallingRunner' object has no attribute 'run_with_observation'`

- [ ] **Step 3: 写最小实现**

```python
@dataclass(frozen=True)
class ToolCallObservation:
    tool_called: bool
    tool_name: str
    error: str


@dataclass(frozen=True)
class ToolCallRunResult:
    answer: str
    observation: ToolCallObservation


def run_with_observation(self, prompt: str) -> ToolCallRunResult:
    tool_name = ""
    try:
        messages = [{"role": "user", "content": prompt}]
        assistant_message = self._client.create_chat_completion(messages, tools=[tool.schema for tool in self._tools.values()])
        tool_calls = assistant_message.get("tool_calls", [])
        if tool_calls:
            request = parse_tool_request(tool_calls[0])
            tool_name = request.name
            result = self._tools[request.name].handler()
            messages.append(assistant_message)
            messages.append({"role": "tool", "tool_call_id": request.call_id, "content": result})
            final_message = self._client.create_chat_completion(messages)
            return ToolCallRunResult(
                answer=final_message["content"],
                observation=ToolCallObservation(tool_called=True, tool_name=tool_name, error="none"),
            )
        return ToolCallRunResult(
            answer=assistant_message["content"],
            observation=ToolCallObservation(tool_called=False, tool_name="", error="none"),
        )
    except Exception as exc:
        return ToolCallRunResult(
            answer="",
            observation=ToolCallObservation(tool_called=bool(tool_name), tool_name=tool_name, error=str(exc)),
        )
```

- [ ] **Step 4: 写失败测试，固定脚本输出**

```python
def test_tool_calling_demo_prints_observation_lines(self):
    stdout = io.StringIO()

    with redirect_stdout(stdout):
        exit_code = main(["请查询 Phase 1 进度"], env={})

    self.assertEqual(exit_code, 0)
    self.assertIn("tool_called=true", stdout.getvalue())
    self.assertIn("tool_name=get_phase1_progress", stdout.getvalue())
```

- [ ] **Step 5: 运行测试并补齐通过**

Run: `PYTHONPATH=src:. python3 -m unittest tests.test_tool_calling -v`

Expected: PASS

- [ ] **Step 6: 提交**

```bash
git add src/agent_kb/tool_calling.py tests/test_tool_calling.py
git commit -m "feat: add tool calling observations"
```

### Task 4: CLI 摘要输出

**Files:**
- Modify: `scripts/hello_model.py`
- Modify: `scripts/tool_calling_demo.py`
- Test: `tests/test_hello_model_script.py`
- Test: `tests/test_tool_calling.py`

- [ ] **Step 1: 写失败测试，固定 `hello_model.py` 真实模式摘要打印**

```python
def test_main_real_mode_prints_observation_summary(self):
    stdout = io.StringIO()

    class FakeObservedClient:
        def complete_with_observation(self, prompt):
            return CompletionResult(
                text="真实响应",
                observation=CallObservation(
                    provider="deepseek",
                    model="deepseek-v4-flash",
                    latency_ms=123,
                    usage=UsageMetrics(input_tokens=9, output_tokens=4, total_tokens=13),
                    error="none",
                ),
            )

    with patch("scripts.hello_model.DeepSeekChatCompletionsModelClient", return_value=FakeObservedClient()):
        with redirect_stdout(stdout):
            exit_code = main(["--real", "你好"], env={"DEEPSEEK_API_KEY": "deepseek-key"})

    self.assertEqual(exit_code, 0)
    self.assertIn("latency_ms=123", stdout.getvalue())
    self.assertIn("total_tokens=13", stdout.getvalue())
```

- [ ] **Step 2: 运行测试确认失败**

Run: `PYTHONPATH=src:. python3 -m unittest tests.test_hello_model_script.HelloModelScriptTest.test_main_real_mode_prints_observation_summary`

Expected: FAIL with missing `complete_with_observation` or missing observation output

- [ ] **Step 3: 写最小实现**

```python
if args.stream:
    chunks, observation = model_client.stream_with_observation(args.prompt)
    for chunk in chunks:
        print(chunk, end="", flush=True)
    print()
    for line in format_observation_lines(observation):
        print(line)
else:
    result = model_client.complete_with_observation(args.prompt)
    print(result.text)
    for line in format_observation_lines(result.observation):
        print(line)
```

- [ ] **Step 4: 更新 tool calling demo 使用 `run_with_observation()`**

```python
result = runner.run_with_observation(args.prompt)
print(result.answer)
for line in format_tool_call_observation_lines(result.observation):
    print(line)
```

- [ ] **Step 5: 运行脚本相关测试**

Run: `PYTHONPATH=src:. python3 -m unittest tests.test_hello_model_script tests.test_tool_calling -v`

Expected: PASS

- [ ] **Step 6: 提交**

```bash
git add scripts/hello_model.py scripts/tool_calling_demo.py tests/test_hello_model_script.py tests/test_tool_calling.py
git commit -m "feat: print call observation summaries"
```

### Task 5: 文档、验证与回写

**Files:**
- Create: `docs/learning-notes/phase-1-call-observability.md`
- Modify: `docs/agent-learning-todo.md`
- Modify: `openspec/changes/learn-phase-1-call-observability/tasks.md`

- [ ] **Step 1: 写学习笔记**

```md
# Phase 1 学习笔记：记录延迟、token 使用量、模型名和错误

日期：2026-04-27

## 本节学到什么

- DeepSeek 非流式响应中的 `usage.prompt_tokens`、`usage.completion_tokens`、`usage.total_tokens` 可直接读取。
- 延迟使用本地 `time.monotonic()` 包裹单次请求计算。
- 流式场景优先从事件中的 `usage` 读取；若 provider 未返回，则允许为空。
- tool calling 需要单独记录是否触发 tool 和触发的 tool 名。
```

- [ ] **Step 2: 更新任务清单和路线图**

```md
- [x] 4.1 新增学习笔记，记录字段来源、统计口径和限制。
- [x] 4.2 运行单元测试和 OpenSpec 严格校验。
- [x] 4.3 使用真实 DeepSeek 调用验证至少一条非流式链路和一条 tool calling 链路。
- [x] 4.4 完成后更新 `tasks.md` 和 `docs/agent-learning-todo.md` 勾选状态。
```

- [ ] **Step 3: 运行完整验证**

Run: `PYTHONPATH=src:. python3 -m unittest discover -s tests`

Expected: PASS with all tests green

Run: `/opt/homebrew/bin/openspec validate --all --strict`

Expected: PASS with no spec validation errors

- [ ] **Step 4: 手动真实验证**

Run: `PYTHONPATH=src python3 scripts/hello_model.py --real "用一句话介绍这个项目"`

Expected: 输出文本答案，并附带 `provider/model/latency_ms/.../error`

Run: `PYTHONPATH=src python3 scripts/tool_calling_demo.py --real "请调用工具查询当前 Phase 1 进度，并告诉我下一步"`

Expected: 输出最终答案，并附带 `tool_called=true`、`tool_name=get_phase1_progress`

- [ ] **Step 5: 提交**

```bash
git add docs/learning-notes/phase-1-call-observability.md docs/agent-learning-todo.md openspec/changes/learn-phase-1-call-observability/tasks.md
git commit -m "docs: record call observability learning results"
```

## Self-Review

- 规格覆盖：
  - `call-observability-learning/spec.md` 的三项要求分别由 Task 2、Task 3、Task 4 和 Task 5 覆盖。
  - `learning-roadmap/spec.md` 的回写要求由 Task 5 覆盖。
- 占位符检查：
  - 计划内没有 `TBD`、`TODO`、`implement later` 之类的占位内容。
- 类型一致性：
  - 全文统一使用 `UsageMetrics`、`CallObservation`、`CompletionResult`、`ToolCallObservation`、`ToolCallRunResult` 这几个类型名。
