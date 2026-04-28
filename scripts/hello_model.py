import os
import sys
from argparse import ArgumentParser, Namespace
from typing import Mapping, Optional, Sequence

from agent_kb.call_observability import format_observation_lines
from agent_kb.config import AppConfig
from agent_kb.deepseek_client import (
    DeepSeekCallError,
    DeepSeekChatCompletionsModelClient,
)
from agent_kb.hello_agent import DryRunModelClient, HelloAgent
from agent_kb.openai_client import ResponsesApiModelClient


DEFAULT_PROMPT = "用一句简短的话介绍 Agent 开发学习项目。"


def _print_observation_summary(lines: Sequence[str]) -> None:
    print("observation:")
    for line in lines:
        print(line)


def _require_observation(result) -> object:
    observation = getattr(result, "observation", None)
    if observation is None:
        raise RuntimeError("DeepSeek 流式调用结束后未生成 observation")
    return observation


def parse_args(argv: Sequence[str]) -> Namespace:
    parser = ArgumentParser(description="运行基础聊天调用学习脚本。")
    parser.add_argument("prompt", nargs="?", default=DEFAULT_PROMPT)
    parser.add_argument(
        "--real",
        action="store_true",
        help="显式调用真实模型 API；默认使用 dry-run。",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="流式输出响应片段。",
    )
    return parser.parse_args(argv)


def main(
    argv: Optional[Sequence[str]] = None,
    env: Optional[Mapping[str, str]] = None,
) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    config = AppConfig.from_env(os.environ if env is None else env)

    if args.real:
        if config.model_provider == "deepseek":
            if not config.has_deepseek_api_key:
                print("真实模式需要先配置 DEEPSEEK_API_KEY。", file=sys.stderr)
                return 2
            model_client = DeepSeekChatCompletionsModelClient(config)
        elif config.model_provider == "openai":
            if not config.has_openai_api_key:
                print("真实模式需要先配置 OPENAI_API_KEY。", file=sys.stderr)
                return 2
            model_client = ResponsesApiModelClient(config)
        else:
            print(f"不支持的 MODEL_PROVIDER：{config.model_provider}", file=sys.stderr)
            return 2
        mode = "real"
    else:
        # 默认 dry-run 保持项目在没有网络和 API Key 的情况下也能运行。
        model_client = DryRunModelClient()
        mode = "dry-run"

    print(f"mode={mode}")
    print(f"provider={config.model_provider}")
    print(f"stream={str(args.stream).lower()}")
    if config.model_provider == "deepseek":
        print(f"model={config.deepseek_model}")
    else:
        print(f"model={config.model}")

    if args.real and config.model_provider == "deepseek":
        try:
            if args.stream:
                result = model_client.stream_with_observation(args.prompt)
                for chunk in result.chunks:
                    print(chunk, end="", flush=True)
                print()
            else:
                result = model_client.complete_with_observation(args.prompt)
                print(result.text)
        except DeepSeekCallError as exc:
            _print_observation_summary(format_observation_lines(exc.observation))
            print(str(exc), file=sys.stderr)
            return 1

        _print_observation_summary(
            format_observation_lines(_require_observation(result))
        )
        return 0

    agent = HelloAgent(model_client=model_client)
    if args.stream:
        for chunk in agent.stream(args.prompt):
            print(chunk, end="", flush=True)
        print()
    else:
        print(agent.run(args.prompt))
    return 0


if __name__ == "__main__":
    sys.exit(main())
