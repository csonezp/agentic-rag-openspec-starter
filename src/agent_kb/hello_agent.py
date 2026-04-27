from typing import Iterable, Protocol


class ModelClient(Protocol):
    def complete(self, prompt: str) -> str:
        """根据单次提示词返回模型响应。"""

    def stream(self, prompt: str) -> Iterable[str]:
        """根据单次提示词流式返回模型响应片段。"""


class DryRunModelClient:
    def complete(self, prompt: str) -> str:
        return (
            "Dry-run 响应：配置真实模型 API Key 后可调用模型服务。"
            f"收到的提示词：{prompt}"
        )

    def stream(self, prompt: str) -> Iterable[str]:
        response = self.complete(prompt)
        for chunk in response.split("。"):
            if chunk:
                yield f"{chunk}。"


class HelloAgent:
    def __init__(self, model_client: ModelClient) -> None:
        self._model_client = model_client

    def run(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("提示词不能为空")
        return self._model_client.complete(prompt)

    def stream(self, prompt: str) -> Iterable[str]:
        if not prompt.strip():
            raise ValueError("提示词不能为空")
        return self._model_client.stream(prompt)
