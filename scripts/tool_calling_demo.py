import os
import sys
from argparse import ArgumentParser, Namespace
from typing import Mapping, Optional, Sequence

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
    answer = runner.run(args.prompt)

    print(f"mode={mode}")
    print(f"provider={config.model_provider}")
    print(f"model={config.deepseek_model}")
    print(answer)
    return 0


if __name__ == "__main__":
    sys.exit(main())
