import os
import sys
from argparse import ArgumentParser, Namespace
from typing import Mapping, Optional, Sequence

from agent_kb.config import AppConfig
from agent_kb.hello_agent import DryRunModelClient, HelloAgent
from agent_kb.openai_client import ResponsesApiModelClient


DEFAULT_PROMPT = "用一句简短的话介绍 Agent 开发学习项目。"


def parse_args(argv: Sequence[str]) -> Namespace:
    parser = ArgumentParser(description="运行基础聊天调用学习脚本。")
    parser.add_argument("prompt", nargs="?", default=DEFAULT_PROMPT)
    parser.add_argument(
        "--real",
        action="store_true",
        help="显式调用真实 OpenAI Responses API；默认使用 dry-run。",
    )
    return parser.parse_args(argv)


def main(
    argv: Optional[Sequence[str]] = None,
    env: Optional[Mapping[str, str]] = None,
) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    config = AppConfig.from_env(os.environ if env is None else env)

    if args.real:
        if not config.has_openai_api_key:
            print("真实模式需要先配置 OPENAI_API_KEY。", file=sys.stderr)
            return 2
        model_client = ResponsesApiModelClient(config)
        mode = "real"
    else:
        # 默认 dry-run 保持项目在没有网络和 API Key 的情况下也能运行。
        model_client = DryRunModelClient()
        mode = "dry-run"

    agent = HelloAgent(model_client=model_client)
    response = agent.run(args.prompt)

    print(f"mode={mode}")
    print(f"model={config.model}")
    print(response)
    return 0


if __name__ == "__main__":
    sys.exit(main())
