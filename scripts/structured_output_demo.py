import os
import sys
from argparse import ArgumentParser, Namespace
from typing import Mapping, Optional, Sequence

from agent_kb.config import AppConfig
from agent_kb.deepseek_client import DeepSeekChatCompletionsModelClient
from agent_kb.structured_output import (
    DryRunStructuredOutputClient,
    generate_learning_brief,
)


DEFAULT_TEXT = "今天学习了如何让模型输出 JSON，并在本地代码中校验字段。"


def parse_args(argv: Sequence[str]) -> Namespace:
    parser = ArgumentParser(description="运行结构化输出学习脚本。")
    parser.add_argument("text", nargs="?", default=DEFAULT_TEXT)
    parser.add_argument(
        "--real",
        action="store_true",
        help="显式调用真实 DeepSeek JSON Output；默认使用 dry-run。",
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
        client = DryRunStructuredOutputClient()
        mode = "dry-run"

    brief = generate_learning_brief(client, args.text)

    print(f"mode={mode}")
    print(f"provider={config.model_provider}")
    print(f"model={config.deepseek_model}")
    print(brief.to_json_text())
    return 0


if __name__ == "__main__":
    sys.exit(main())
