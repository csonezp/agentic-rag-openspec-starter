import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from agent_kb.call_observability import CallObservation, UsageMetrics
from agent_kb.deepseek_client import (
    CompletionResult,
    DeepSeekCallError,
    StreamResult,
)
from scripts.hello_model import DEFAULT_PROMPT, main, parse_args


class HelloModelScriptTest(unittest.TestCase):
    def test_parse_args_uses_default_prompt_when_no_prompt_is_given(self):
        args = parse_args([])

        self.assertEqual(args.prompt, DEFAULT_PROMPT)
        self.assertFalse(args.real)
        self.assertFalse(args.stream)

    def test_parse_args_uses_prompt_from_command_line(self):
        args = parse_args(["请解释 Responses API"])

        self.assertEqual(args.prompt, "请解释 Responses API")

    def test_main_uses_dry_run_by_default(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = main(["来自命令行的提示词"], env={})

        self.assertEqual(exit_code, 0)
        self.assertIn("mode=dry-run", stdout.getvalue())
        self.assertIn("来自命令行的提示词", stdout.getvalue())

    def test_main_streams_in_dry_run_mode(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = main(["--stream", "流式提示词"], env={})

        self.assertEqual(exit_code, 0)
        self.assertIn("mode=dry-run", stdout.getvalue())
        self.assertIn("stream=true", stdout.getvalue())
        self.assertIn("流式提示词", stdout.getvalue())

    def test_real_mode_without_api_key_returns_error(self):
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            exit_code = main(["--real", "真实调用"], env={})

        self.assertEqual(exit_code, 2)
        self.assertIn("DEEPSEEK_API_KEY", stderr.getvalue())

    def test_real_openai_mode_without_api_key_returns_openai_error(self):
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            exit_code = main(
                ["--real", "真实调用"],
                env={"MODEL_PROVIDER": "openai"},
            )

        self.assertEqual(exit_code, 2)
        self.assertIn("OPENAI_API_KEY", stderr.getvalue())

    def test_real_deepseek_mode_outputs_observation_summary(self):
        class FakeDeepSeekClient:
            def __init__(self, config):
                self.config = config

            def complete(self, prompt):
                return "真实模式回答"

            def complete_with_observation(self, prompt):
                return CompletionResult(
                    text="真实模式回答",
                    observation=CallObservation(
                        provider="deepseek",
                        model="deepseek-chat",
                        latency_ms=321,
                        usage=UsageMetrics(
                            input_tokens=11,
                            output_tokens=7,
                            total_tokens=18,
                        ),
                        error_type=None,
                        error_message=None,
                    ),
                )

        stdout = io.StringIO()
        with patch(
            "scripts.hello_model.DeepSeekChatCompletionsModelClient",
            FakeDeepSeekClient,
        ):
            with redirect_stdout(stdout):
                exit_code = main(
                    ["--real", "真实调用"],
                    env={"DEEPSEEK_API_KEY": "deepseek-key"},
                )

        self.assertEqual(exit_code, 0)
        self.assertIn("真实模式回答", stdout.getvalue())
        self.assertIn("observation:", stdout.getvalue())
        self.assertIn("provider=deepseek", stdout.getvalue())
        self.assertIn("latency_ms=321", stdout.getvalue())
        self.assertIn("total_tokens=18", stdout.getvalue())

    def test_real_deepseek_mode_prints_observation_before_non_zero_exit_on_error(self):
        class FakeDeepSeekClient:
            def __init__(self, config):
                self.config = config

            def complete_with_observation(self, prompt):
                raise DeepSeekCallError(
                    "DeepSeek API 请求失败：429 rate limit",
                    CallObservation(
                        provider="deepseek",
                        model="deepseek-chat",
                        latency_ms=789,
                        usage=UsageMetrics(
                            input_tokens=None,
                            output_tokens=None,
                            total_tokens=None,
                        ),
                        error_type="http_error",
                        error_message="DeepSeek API 请求失败：429 rate limit",
                    ),
                )

        stdout = io.StringIO()
        stderr = io.StringIO()
        with patch(
            "scripts.hello_model.DeepSeekChatCompletionsModelClient",
            FakeDeepSeekClient,
        ):
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = main(
                    ["--real", "真实调用失败"],
                    env={"DEEPSEEK_API_KEY": "deepseek-key"},
                )

        self.assertEqual(exit_code, 1)
        self.assertIn("observation:", stdout.getvalue())
        self.assertIn("provider=deepseek", stdout.getvalue())
        self.assertIn("latency_ms=789", stdout.getvalue())
        self.assertIn("error_type=http_error", stdout.getvalue())
        self.assertIn("429 rate limit", stdout.getvalue())
        self.assertIn("429 rate limit", stderr.getvalue())

    def test_real_deepseek_stream_mode_outputs_observation_summary(self):
        class FakeDeepSeekClient:
            def __init__(self, config):
                self.config = config

            def stream(self, prompt):
                return iter(["第一段", "第二段"])

            def stream_with_observation(self, prompt):
                return StreamResult(
                    chunks=["第一段", "第二段"],
                    observation=CallObservation(
                        provider="deepseek",
                        model="deepseek-chat",
                        latency_ms=456,
                        usage=UsageMetrics(
                            input_tokens=None,
                            output_tokens=None,
                            total_tokens=None,
                        ),
                        error_type=None,
                        error_message=None,
                    ),
                )

        stdout = io.StringIO()
        with patch(
            "scripts.hello_model.DeepSeekChatCompletionsModelClient",
            FakeDeepSeekClient,
        ):
            with redirect_stdout(stdout):
                exit_code = main(
                    ["--real", "--stream", "流式真实调用"],
                    env={"DEEPSEEK_API_KEY": "deepseek-key"},
                )

        self.assertEqual(exit_code, 0)
        self.assertIn("第一段第二段", stdout.getvalue())
        self.assertIn("observation:", stdout.getvalue())
        self.assertIn("latency_ms=456", stdout.getvalue())
        self.assertIn("input_tokens=unknown", stdout.getvalue())
        self.assertIn("total_tokens=unknown", stdout.getvalue())

    def test_real_deepseek_stream_mode_supports_lazy_observation_result(self):
        class FakeDeepSeekClient:
            def __init__(self, config):
                self.config = config

            def stream_with_observation(self, prompt):
                result = StreamResult(chunks=())

                def iter_chunks():
                    yield "第一段"
                    yield "第二段"
                    result.observation = CallObservation(
                        provider="deepseek",
                        model="deepseek-chat",
                        latency_ms=654,
                        usage=UsageMetrics(
                            input_tokens=9,
                            output_tokens=4,
                            total_tokens=13,
                        ),
                        error_type=None,
                        error_message=None,
                    )

                result.chunks = iter_chunks()
                return result

        stdout = io.StringIO()
        with patch(
            "scripts.hello_model.DeepSeekChatCompletionsModelClient",
            FakeDeepSeekClient,
        ):
            with redirect_stdout(stdout):
                exit_code = main(
                    ["--real", "--stream", "流式真实调用"],
                    env={"DEEPSEEK_API_KEY": "deepseek-key"},
                )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("第一段第二段", output)
        self.assertIn("observation:", output)
        self.assertIn("latency_ms=654", output)
        self.assertLess(output.index("第一段第二段"), output.index("observation:"))

    def test_real_deepseek_stream_mode_prints_observation_before_non_zero_exit_on_error(
        self,
    ):
        class FakeDeepSeekClient:
            def __init__(self, config):
                self.config = config

            def stream_with_observation(self, prompt):
                raise DeepSeekCallError(
                    "DeepSeek SSE 事件格式非法",
                    CallObservation(
                        provider="deepseek",
                        model="deepseek-chat",
                        latency_ms=12,
                        usage=UsageMetrics(
                            input_tokens=None,
                            output_tokens=None,
                            total_tokens=None,
                        ),
                        error_type="invalid_sse",
                        error_message="DeepSeek SSE 事件格式非法",
                    ),
                )

        stdout = io.StringIO()
        stderr = io.StringIO()
        with patch(
            "scripts.hello_model.DeepSeekChatCompletionsModelClient",
            FakeDeepSeekClient,
        ):
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = main(
                    ["--real", "--stream", "流式真实调用失败"],
                    env={"DEEPSEEK_API_KEY": "deepseek-key"},
                )

        self.assertEqual(exit_code, 1)
        self.assertIn("observation:", stdout.getvalue())
        self.assertIn("error_type=invalid_sse", stdout.getvalue())
        self.assertIn("latency_ms=12", stdout.getvalue())
        self.assertIn("DeepSeek SSE 事件格式非法", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
