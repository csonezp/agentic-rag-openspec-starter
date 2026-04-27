import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Iterable, Optional

from agent_kb.call_observability import CallObservation, UsageMetrics
from agent_kb.config import AppConfig
from agent_kb.hello_agent import ModelClient


@dataclass(frozen=True)
class CompletionResult:
    text: str
    observation: CallObservation


@dataclass(frozen=True)
class StreamResult:
    chunks: list[str]
    observation: CallObservation


class DeepSeekChatCompletionsModelClient(ModelClient):
    def __init__(self, config: AppConfig) -> None:
        if not config.deepseek_api_key:
            raise ValueError("真实模式需要配置 DEEPSEEK_API_KEY")
        self._config = config

    def complete(self, prompt: str) -> str:
        return self.complete_with_observation(prompt).text

    def complete_with_observation(self, prompt: str) -> CompletionResult:
        started_at = time.monotonic()
        payload = self._post_json(self._build_request(prompt, stream=False))
        text = _extract_message_content(payload)
        observation = CallObservation(
            provider="deepseek",
            model=payload.get("model", self._config.deepseek_model),
            latency_ms=_compute_latency_ms(started_at),
            usage=_extract_usage(payload),
            error_message=None,
        )
        return CompletionResult(text=text, observation=observation)

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

        return _extract_message(self._post_json(request))

    def stream(self, prompt: str) -> Iterable[str]:
        yield from self.stream_with_observation(prompt).chunks

    def stream_with_observation(self, prompt: str) -> StreamResult:
        started_at = time.monotonic()
        request = self._build_request(prompt, stream=True)

        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                chunks, metadata = _collect_deepseek_stream_payload(response)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"DeepSeek API 请求失败：{exc.code} {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"DeepSeek API 网络请求失败：{exc.reason}") from exc

        observation = CallObservation(
            provider="deepseek",
            model=metadata.get("model") or self._config.deepseek_model,
            latency_ms=_compute_latency_ms(started_at),
            usage=_extract_usage(metadata),
            error_message=None,
        )
        return StreamResult(chunks=chunks, observation=observation)

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

    def _post_json(self, request: urllib.request.Request) -> dict:
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"DeepSeek API 请求失败：{exc.code} {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"DeepSeek API 网络请求失败：{exc.reason}") from exc


def parse_deepseek_stream_events(lines: Iterable[bytes]) -> Iterable[str]:
    chunks, _ = _collect_deepseek_stream_payload(lines)
    yield from chunks


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


def _extract_usage(payload: dict) -> UsageMetrics:
    usage = payload.get("usage")
    if not isinstance(usage, dict):
        usage = {}
    return UsageMetrics(
        input_tokens=usage.get("prompt_tokens"),
        output_tokens=usage.get("completion_tokens"),
        total_tokens=usage.get("total_tokens"),
    )


def _compute_latency_ms(started_at: float) -> int:
    return round((time.monotonic() - started_at) * 1000)


def _collect_deepseek_stream_payload(lines: Iterable[bytes]) -> tuple[list[str], dict]:
    chunks: list[str] = []
    metadata: dict = {}
    for raw_line in lines:
        line = raw_line.decode("utf-8").strip()
        if not line.startswith("data: "):
            continue

        data = line.removeprefix("data: ")
        if data == "[DONE]":
            break

        payload = json.loads(data)
        if payload.get("model"):
            metadata["model"] = payload["model"]
        if payload.get("usage"):
            metadata["usage"] = payload["usage"]
        for choice in payload.get("choices", []):
            content = choice.get("delta", {}).get("content")
            if content:
                chunks.append(content)
    return chunks, metadata


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
