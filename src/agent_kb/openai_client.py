import json
import urllib.error
import urllib.request

from agent_kb.config import AppConfig
from agent_kb.hello_agent import ModelClient


class ResponsesApiModelClient(ModelClient):
    def __init__(self, config: AppConfig) -> None:
        if not config.openai_api_key:
            raise ValueError("真实模式需要配置 OPENAI_API_KEY")
        self._config = config

    def complete(self, prompt: str) -> str:
        request = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(
                {
                    "model": self._config.model,
                    "input": prompt,
                }
            ).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._config.openai_api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Responses API 请求失败：{exc.code} {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Responses API 网络请求失败：{exc.reason}") from exc

        return _extract_output_text(payload)


def _extract_output_text(payload: dict) -> str:
    texts: list[str] = []
    for item in payload.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text" and content.get("text"):
                texts.append(content["text"])

    if texts:
        return "\n".join(texts)

    if payload.get("error"):
        raise RuntimeError(f"Responses API 返回错误：{payload['error']}")

    raise RuntimeError("Responses API 响应中没有可读取的 output_text")
