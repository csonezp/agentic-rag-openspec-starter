import io
import unittest
from contextlib import redirect_stderr, redirect_stdout

from scripts.hello_model import DEFAULT_PROMPT, main, parse_args


class HelloModelScriptTest(unittest.TestCase):
    def test_parse_args_uses_default_prompt_when_no_prompt_is_given(self):
        args = parse_args([])

        self.assertEqual(args.prompt, DEFAULT_PROMPT)
        self.assertFalse(args.real)

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

    def test_real_mode_without_api_key_returns_error(self):
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            exit_code = main(["--real", "真实调用"], env={})

        self.assertEqual(exit_code, 2)
        self.assertIn("OPENAI_API_KEY", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
