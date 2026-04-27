import os
import sys

from agent_kb.config import AppConfig
from agent_kb.hello_agent import DryRunModelClient, HelloAgent


def main() -> int:
    config = AppConfig.from_env(os.environ)
    prompt = "用一句简短的话介绍 Agent 开发学习项目。"

    # Phase 0 保持项目在没有网络和 API Key 的情况下也能运行。
    # Phase 1 学习模型调用时，再接入真实 OpenAI client。
    agent = HelloAgent(model_client=DryRunModelClient())
    response = agent.run(prompt)

    print(f"model={config.model}")
    print(response)
    return 0


if __name__ == "__main__":
    sys.exit(main())
