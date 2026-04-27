import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout

from agent_kb.tool_calling import (
    ToolCallingRunner,
    ToolDefinition,
    ToolRunResult,
    ToolRequest,
    get_phase1_progress,
    get_phase1_progress_tool,
    parse_tool_request,
)
from scripts.tool_calling_demo import main, parse_args


class FakeToolClient:
    def __init__(self):
        self.messages_seen = []
        self.tools_seen = []

    def create_chat_completion(self, messages, tools=None):
        self.messages_seen.append(messages)
        self.tools_seen.append(tools)
        if len(messages) == 1:
            return {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {
                            "name": "get_phase1_progress",
                            "arguments": "{}",
                        },
                    }
                ],
            }
        return {"role": "assistant", "content": "Phase 1 已调用工具并生成回答。"}


class NoToolClient:
    def create_chat_completion(self, messages, tools=None):
        return {"role": "assistant", "content": "无需调用工具，直接回答。"}


class ToolCallingTest(unittest.TestCase):
    def test_local_phase1_progress_function_returns_json(self):
        payload = json.loads(get_phase1_progress())

        self.assertIn("completed", payload)
        self.assertIn("next", payload)
        self.assertIn("function/tool calling", payload["completed"][-1])
        self.assertEqual(payload["next"], "记录延迟、token 使用量、模型名和错误")

    def test_tool_schema_defines_local_function(self):
        tool = get_phase1_progress_tool()

        self.assertEqual(tool["type"], "function")
        self.assertEqual(tool["function"]["name"], "get_phase1_progress")
        self.assertEqual(tool["function"]["parameters"]["type"], "object")

    def test_parse_tool_request_accepts_valid_call(self):
        request = parse_tool_request(
            {
                "id": "call_1",
                "type": "function",
                "function": {
                    "name": "get_phase1_progress",
                    "arguments": "{}",
                },
            }
        )

        self.assertEqual(
            request,
            ToolRequest(
                call_id="call_1",
                name="get_phase1_progress",
                arguments={},
            ),
        )

    def test_parse_tool_request_rejects_invalid_arguments(self):
        with self.assertRaisesRegex(ValueError, "arguments"):
            parse_tool_request(
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "get_phase1_progress",
                        "arguments": "not-json",
                    },
                }
            )

    def test_runner_executes_tool_and_gets_final_answer(self):
        client = FakeToolClient()
        runner = ToolCallingRunner(
            client=client,
            tools=[
                ToolDefinition(
                    schema=get_phase1_progress_tool(),
                    handler=get_phase1_progress,
                )
            ],
        )

        answer = runner.run("请查询 Phase 1 进度")

        self.assertEqual(answer, "Phase 1 已调用工具并生成回答。")
        self.assertEqual(client.tools_seen[0][0]["function"]["name"], "get_phase1_progress")
        second_messages = client.messages_seen[1]
        self.assertEqual(second_messages[-1]["role"], "tool")
        self.assertEqual(second_messages[-1]["tool_call_id"], "call_1")

    def test_runner_returns_structured_observation_when_tool_called(self):
        runner = ToolCallingRunner(
            client=FakeToolClient(),
            tools=[
                ToolDefinition(
                    schema=get_phase1_progress_tool(),
                    handler=get_phase1_progress,
                )
            ],
        )

        result = runner.run_with_observation("请查询 Phase 1 进度")

        self.assertEqual(
            result,
            ToolRunResult(
                answer="Phase 1 已调用工具并生成回答。",
                observation={
                    "tool_triggered": True,
                    "tool_names": ["get_phase1_progress"],
                    "success": True,
                    "error_type": None,
                    "error_message": None,
                },
            ),
        )

    def test_runner_returns_structured_observation_when_no_tool_called(self):
        runner = ToolCallingRunner(
            client=NoToolClient(),
            tools=[
                ToolDefinition(
                    schema=get_phase1_progress_tool(),
                    handler=get_phase1_progress,
                )
            ],
        )

        result = runner.run_with_observation("请直接回答")

        self.assertEqual(
            result,
            ToolRunResult(
                answer="无需调用工具，直接回答。",
                observation={
                    "tool_triggered": False,
                    "tool_names": [],
                    "success": True,
                    "error_type": None,
                    "error_message": None,
                },
            ),
        )

    def test_runner_rejects_unknown_tool(self):
        class UnknownToolClient(FakeToolClient):
            def create_chat_completion(self, messages, tools=None):
                return {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": "call_1",
                            "type": "function",
                            "function": {"name": "unknown", "arguments": "{}"},
                        }
                    ],
                }

        runner = ToolCallingRunner(
            client=UnknownToolClient(),
            tools=[
                ToolDefinition(
                    schema=get_phase1_progress_tool(),
                    handler=get_phase1_progress,
                )
            ],
        )

        with self.assertRaisesRegex(ValueError, "未注册工具"):
            runner.run("请查询 Phase 1 进度")

    def test_runner_returns_structured_observation_when_tool_call_fails(self):
        class UnknownToolClient(FakeToolClient):
            def create_chat_completion(self, messages, tools=None):
                return {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": "call_1",
                            "type": "function",
                            "function": {"name": "unknown", "arguments": "{}"},
                        }
                    ],
                }

        runner = ToolCallingRunner(
            client=UnknownToolClient(),
            tools=[
                ToolDefinition(
                    schema=get_phase1_progress_tool(),
                    handler=get_phase1_progress,
                )
            ],
        )

        result = runner.run_with_observation("请查询 Phase 1 进度")

        self.assertEqual(result.answer, "")
        self.assertEqual(
            result.observation,
            {
                "tool_triggered": True,
                "tool_names": ["unknown"],
                "success": False,
                "error_type": "ValueError",
                "error_message": "未注册工具：unknown",
            },
        )


class ToolCallingDemoScriptTest(unittest.TestCase):
    def test_parse_args_defaults_to_dry_run(self):
        args = parse_args([])

        self.assertFalse(args.real)

    def test_main_outputs_answer_in_dry_run_mode(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = main(["请查询 Phase 1 进度"], env={})

        self.assertEqual(exit_code, 0)
        self.assertIn("mode=dry-run", stdout.getvalue())
        self.assertIn("Phase 1", stdout.getvalue())

    def test_real_mode_requires_deepseek_api_key(self):
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            exit_code = main(["--real", "请查询 Phase 1 进度"], env={})

        self.assertEqual(exit_code, 2)
        self.assertIn("DEEPSEEK_API_KEY", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
