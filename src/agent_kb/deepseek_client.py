import json
import urllib.error
import urllib.request
from typing import Iterable, Optional

from agent_kb.config import AppConfig
from agent_kb.hello_agent import ModelClient


class DeepSeekChatCompletionsModelClient(ModelClient):
    def __init__(self, config: AppConfig) -> None:
        if not config.deepseek_api_key:
            raise ValueError("真实模式需要配置 DEEPSEEK_API_KEY")
        self._config = config

    def complete(self, prompt: str) -> str:
        request = self._build_request(prompt, stream=False)

        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"DeepSeek API 请求失败：{exc.code} {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"DeepSeek API 网络请求失败：{exc.reason}") from exc

        return _extract_message_content(payload)

    def complete_json(self, prompt: str, max_tokens: int = 512) -> str:
        request = self._build_request(
            prompt,
            stream=False,
            response_format={"type": "json_object"},
            max_tokens=max_tokens,
        )

        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"DeepSeek API 请求失败：{exc.code} {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"DeepSeek API 网络请求失败：{exc.reason}") from exc

        return _extract_message_content(payload)

    def create_chat_completion(
        self,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
    ) -> dict:
        body = {
            "model": self._config.deepseek_model,
            "messages": messages,
            "stream": False,
        }
        if tools:
            body["tools"] = tools

        request = self._build_raw_request(body)

        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"DeepSeek API 请求失败：{exc.code} {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"DeepSeek API 网络请求失败：{exc.reason}") from exc

        return _extract_message(payload)

    def stream(self, prompt: str) -> Iterable[str]:
        request = self._build_request(prompt, stream=True)

        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                yield from parse_deepseek_stream_events(response)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"DeepSeek API 请求失败：{exc.code} {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"DeepSeek API 网络请求失败：{exc.reason}") from exc

    def _build_request(
        self,
        prompt: str,
        stream: bool,
        response_format: Optional[dict] = None,
        max_tokens: Optional[int] = None,
    ) -> urllib.request.Request:
        body = {
            "model": self._config.deepseek_model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个帮助学习 Agent 开发的助手。",
                },
                {"role": "user", "content": prompt},
            ],
            "stream": stream,
        }
        if response_format:
            body["response_format"] = response_format
        if max_tokens:
            body["max_tokens"] = max_tokens

        return self._build_raw_request(body)

    def _build_raw_request(self, body: dict) -> urllib.request.Request:
        return urllib.request.Request(
            f"{self._config.deepseek_base_url}/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._config.deepseek_api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )


def parse_deepseek_stream_events(lines: Iterable[bytes]) -> Iterable[str]:
    for raw_line in lines:
        line = raw_line.decode("utf-8").strip()
        if not line.startswith("data: "):
            continue

        data = line.removeprefix("data: ")
        if data == "[DONE]":
            break

        payload = json.loads(data)
        for choice in payload.get("choices", []):
            content = choice.get("delta", {}).get("content")
            if content:
                yield content


def _extract_message_content(payload: dict) -> str:
    texts: list[str] = []
    for choice in payload.get("choices", []):
        content = choice.get("message", {}).get("content")
        if content:
            texts.append(content)

    if texts:
        return "\n".join(texts)

    if payload.get("error"):
        raise RuntimeError(f"DeepSeek API 返回错误：{payload['error']}")

    raise RuntimeError("DeepSeek API 响应中没有可读取的 message.content")


def extract_tool_calls(payload: dict) -> list[dict]:
    message = _extract_message(payload)
    return message.get("tool_calls", [])


def _extract_message(payload: dict) -> dict:
    choices = payload.get("choices", [])
    if not choices:
        if payload.get("error"):
            raise RuntimeError(f"DeepSeek API 返回错误：{payload['error']}")
        raise RuntimeError("DeepSeek API 响应中没有 choices")
    message = choices[0].get("message")
    if not isinstance(message, dict):
        raise RuntimeError("DeepSeek API 响应中没有可读取的 message")
    return message
