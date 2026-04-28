import os
import sys
from argparse import ArgumentParser, Namespace
from typing import Mapping, Optional, Sequence

from agent_kb.call_observability import format_tool_call_observation_lines
from agent_kb.config import AppConfig
from agent_kb.deepseek_client import DeepSeekChatCompletionsModelClient
from agent_kb.tool_calling import (
    DryRunToolCallingClient,
    ToolCallingRunner,
    ToolDefinition,
    get_phase1_progress,
    get_phase1_progress_tool,
)


DEFAULT_PROMPT = "请调用工具查询当前 Phase 1 学习进度，并用一句话告诉我下一步。"


def _print_observation_summary(lines: Sequence[str]) -> None:
    print("observation:")
    for line in lines:
        print(line)


def parse_args(argv: Sequence[str]) -> Namespace:
    parser = ArgumentParser(description="运行 tool calling 学习脚本。")
    parser.add_argument("prompt", nargs="?", default=DEFAULT_PROMPT)
    parser.add_argument(
        "--real",
        action="store_true",
        help="显式调用真实 DeepSeek Tool Calls；默认使用 dry-run。",
    )
    return parser.parse_args(argv)


def main(
    argv: Optional[Sequence[str]] = None,
    env: Optional[Mapping[str, str]] = None,
) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    config = AppConfig.from_env(os.environ if env is None else env)

    if args.real:
        if not config.has_deepseek_api_key:
            print("真实模式需要先配置 DEEPSEEK_API_KEY。", file=sys.stderr)
            return 2
        client = DeepSeekChatCompletionsModelClient(config)
        mode = "real"
    else:
        client = DryRunToolCallingClient()
        mode = "dry-run"

    runner = ToolCallingRunner(
        client=client,
        tools=[
            ToolDefinition(
                schema=get_phase1_progress_tool(),
                handler=get_phase1_progress,
            )
        ],
    )
    print(f"mode={mode}")
    print(f"provider={config.model_provider}")
    print(f"model={config.deepseek_model}")

    if args.real:
        result = runner.run_with_observation(args.prompt)
        if not result.observation["success"]:
            _print_observation_summary(
                format_tool_call_observation_lines(result.observation)
            )
            print(
                result.observation["error_message"] or "tool calling 运行失败",
                file=sys.stderr,
            )
            return 1
        answer = result.answer
    else:
        answer = runner.run(args.prompt)

    print(answer)
    if args.real:
        _print_observation_summary(
            format_tool_call_observation_lines(result.observation)
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
