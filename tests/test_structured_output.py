import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from agent_kb.structured_output import (
    DryRunStructuredOutputClient,
    LearningBrief,
    build_learning_brief_prompt,
    generate_learning_brief,
)
from scripts.structured_output_demo import main, parse_args


class FakeStructuredClient:
    def __init__(self, response: str):
        self.response = response
        self.prompt = None
        self.max_tokens = None

    def complete_json(self, prompt: str, max_tokens: int = 512) -> str:
        self.prompt = prompt
        self.max_tokens = max_tokens
        return self.response


class StructuredOutputTest(unittest.TestCase):
    def test_parses_valid_learning_brief(self):
        brief = LearningBrief.from_json_text(
            '{"title":"结构化输出","summary":"学习 JSON Output","next_action":"加入校验"}'
        )

        self.assertEqual(brief.title, "结构化输出")
        self.assertEqual(brief.summary, "学习 JSON Output")
        self.assertEqual(brief.next_action, "加入校验")

    def test_rejects_missing_required_field(self):
        with self.assertRaisesRegex(ValueError, "next_action"):
            LearningBrief.from_json_text('{"title":"标题","summary":"摘要"}')

    def test_rejects_non_string_field(self):
        with self.assertRaisesRegex(ValueError, "summary"):
            LearningBrief.from_json_text(
                '{"title":"标题","summary":["摘要"],"next_action":"下一步"}'
            )

    def test_build_prompt_contains_json_and_example_schema(self):
        prompt = build_learning_brief_prompt("学习结构化输出")

        self.assertIn("json", prompt.lower())
        self.assertIn('"title"', prompt)
        self.assertIn('"summary"', prompt)
        self.assertIn('"next_action"', prompt)

    def test_generate_learning_brief_uses_json_client(self):
        client = FakeStructuredClient(
            '{"title":"标题","summary":"摘要","next_action":"下一步"}'
        )

        brief = generate_learning_brief(client, "学习文本")

        self.assertEqual(brief.title, "标题")
        self.assertIn("学习文本", client.prompt)
        self.assertEqual(client.max_tokens, 512)

    def test_dry_run_structured_client_returns_valid_json(self):
        response = DryRunStructuredOutputClient().complete_json("请总结")
        payload = json.loads(response)

        self.assertEqual(set(payload), {"title", "summary", "next_action"})


class StructuredOutputDemoScriptTest(unittest.TestCase):
    def test_parse_args_defaults_to_dry_run(self):
        args = parse_args([])

        self.assertFalse(args.real)

    def test_main_outputs_structured_json_in_dry_run_mode(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = main(["学习 JSON Output"], env={})

        self.assertEqual(exit_code, 0)
        self.assertIn("mode=dry-run", stdout.getvalue())
        self.assertIn('"title"', stdout.getvalue())

    def test_real_mode_requires_deepseek_api_key(self):
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            exit_code = main(["--real", "学习 JSON Output"], env={})

        self.assertEqual(exit_code, 2)
        self.assertIn("DEEPSEEK_API_KEY", stderr.getvalue())

    def test_real_mode_uses_deepseek_json_client(self):
        stdout = io.StringIO()

        with patch(
            "scripts.structured_output_demo.DeepSeekChatCompletionsModelClient"
        ) as client_class:
            client_class.return_value.complete_json.return_value = (
                '{"title":"标题","summary":"摘要","next_action":"下一步"}'
            )
            with redirect_stdout(stdout):
                exit_code = main(
                    ["--real", "学习 JSON Output"],
                    env={"DEEPSEEK_API_KEY": "deepseek-key"},
                )

        self.assertEqual(exit_code, 0)
        self.assertIn("mode=real", stdout.getvalue())
        self.assertIn('"next_action"', stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
