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


class DeepSeekCallError(RuntimeError):
    def __init__(self, message: str, observation: CallObservation) -> None:
        super().__init__(message)
        self.observation = observation


class _DeepSeekPayloadError(RuntimeError):
    def __init__(
        self,
        message: str,
        model: Optional[str] = None,
        error_type: str = "api_error",
    ) -> None:
        super().__init__(message)
        self.model = model
        self.error_type = error_type


class DeepSeekChatCompletionsModelClient(ModelClient):
    def __init__(self, config: AppConfig) -> None:
        if not config.deepseek_api_key:
            raise ValueError("真实模式需要配置 DEEPSEEK_API_KEY")
        self._config = config

    def complete(self, prompt: str) -> str:
        return self.complete_with_observation(prompt).text

    def complete_with_observation(self, prompt: str) -> CompletionResult:
        started_at = time.monotonic()
        request = self._build_request(prompt, stream=False)

        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            _raise_call_error(
                config=self._config,
                started_at=started_at,
                error_type="http_error",
                error_message=f"DeepSeek API 请求失败：{exc.code} {detail}",
                cause=exc,
            )
        except urllib.error.URLError as exc:
            _raise_call_error(
                config=self._config,
                started_at=started_at,
                error_type="url_error",
                error_message=f"DeepSeek API 网络请求失败：{exc.reason}",
                cause=exc,
            )
        except json.JSONDecodeError as exc:
            _raise_call_error(
                config=self._config,
                started_at=started_at,
                error_type="invalid_json",
                error_message=f"DeepSeek API 返回了非法 JSON：{exc}",
                cause=exc,
            )

        try:
            text = _extract_message_content(payload)
        except _DeepSeekPayloadError as exc:
            _raise_call_error(
                config=self._config,
                started_at=started_at,
                model=payload.get("model", self._config.deepseek_model),
                error_type=exc.error_type,
                error_message=str(exc),
                cause=exc,
            )
        observation = CallObservation(
            provider="deepseek",
            model=payload.get("model", self._config.deepseek_model),
            latency_ms=_compute_latency_ms(started_at),
            usage=_extract_usage(payload),
            error_type=None,
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
        started_at = time.monotonic()
        request = self._build_request(prompt, stream=True)

        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                yield from parse_deepseek_stream_events(
                    response,
                    default_model=self._config.deepseek_model,
                )
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            _raise_call_error(
                config=self._config,
                started_at=started_at,
                error_type="http_error",
                error_message=f"DeepSeek API 请求失败：{exc.code} {detail}",
                cause=exc,
            )
        except urllib.error.URLError as exc:
            _raise_call_error(
                config=self._config,
                started_at=started_at,
                error_type="url_error",
                error_message=f"DeepSeek API 网络请求失败：{exc.reason}",
                cause=exc,
            )
        except DeepSeekCallError as exc:
            _raise_call_error(
                config=self._config,
                started_at=started_at,
                model=exc.observation.model,
                error_type=exc.observation.error_type or "api_error",
                error_message=str(exc),
                cause=exc,
            )

    def stream_with_observation(self, prompt: str) -> StreamResult:
        started_at = time.monotonic()
        request = self._build_request(prompt, stream=True)
        metadata: dict = {}

        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                chunks = list(
                    parse_deepseek_stream_events(
                        response,
                        default_model=self._config.deepseek_model,
                        metadata=metadata,
                    )
                )
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            _raise_call_error(
                config=self._config,
                started_at=started_at,
                error_type="http_error",
                error_message=f"DeepSeek API 请求失败：{exc.code} {detail}",
                cause=exc,
            )
        except urllib.error.URLError as exc:
            _raise_call_error(
                config=self._config,
                started_at=started_at,
                error_type="url_error",
                error_message=f"DeepSeek API 网络请求失败：{exc.reason}",
                cause=exc,
            )
        except DeepSeekCallError as exc:
            _raise_call_error(
                config=self._config,
                started_at=started_at,
                model=exc.observation.model,
                error_type=exc.observation.error_type or "api_error",
                error_message=str(exc),
                cause=exc,
            )

        observation = CallObservation(
            provider="deepseek",
            model=metadata.get("model") or self._config.deepseek_model,
            latency_ms=_compute_latency_ms(started_at),
            usage=_extract_usage(metadata),
            error_type=None,
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


def parse_deepseek_stream_events(
    lines: Iterable[bytes],
    default_model: str = "deepseek-chat",
    metadata: Optional[dict] = None,
) -> Iterable[str]:
    stream_metadata = metadata if metadata is not None else {}
    try:
        yield from _iter_deepseek_stream_chunks(
            lines,
            default_model=default_model,
            metadata=stream_metadata,
        )
    except _DeepSeekPayloadError as exc:
        _raise_stream_parse_error(default_model=default_model, error=exc)


def _extract_message_content(payload: dict) -> str:
    texts: list[str] = []
    for choice in payload.get("choices", []):
        content = choice.get("message", {}).get("content")
        if content:
            texts.append(content)

    if texts:
        return "\n".join(texts)

    if payload.get("error"):
        raise _DeepSeekPayloadError(
            f"DeepSeek API 返回错误：{payload['error']}",
            model=payload.get("model"),
        )

    raise _DeepSeekPayloadError(
        "DeepSeek API 响应中没有可读取的 message.content",
        model=payload.get("model"),
    )


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


def _iter_deepseek_stream_chunks(
    lines: Iterable[bytes],
    *,
    default_model: str,
    metadata: dict,
) -> Iterable[str]:
    current_model = default_model
    metadata.setdefault("model", current_model)
    for raw_line in lines:
        try:
            line = raw_line.decode("utf-8").strip()
        except UnicodeDecodeError as exc:
            raise _DeepSeekPayloadError(
                "DeepSeek SSE 事件格式非法：无法解码事件数据",
                model=current_model,
                error_type="invalid_sse",
            ) from exc

        if not line:
            continue
        if not line.startswith("data: "):
            raise _DeepSeekPayloadError(
                f"DeepSeek SSE 事件格式非法：{line}",
                model=current_model,
                error_type="invalid_sse",
            )

        data = line.removeprefix("data: ")
        if data == "[DONE]":
            break

        try:
            payload = json.loads(data)
        except json.JSONDecodeError as exc:
            raise _DeepSeekPayloadError(
                f"DeepSeek SSE 事件格式非法：{exc}",
                model=current_model,
                error_type="invalid_sse",
            ) from exc
        if payload.get("model"):
            current_model = payload["model"]
            metadata["model"] = current_model
        if payload.get("error"):
            raise _DeepSeekPayloadError(
                f"DeepSeek API 返回错误：{payload['error']}",
                model=current_model,
            )
        if payload.get("usage"):
            metadata["usage"] = payload["usage"]
        for choice in payload.get("choices", []):
            content = choice.get("delta", {}).get("content")
            if content:
                yield content


def _raise_call_error(
    config: AppConfig,
    started_at: float,
    error_type: str,
    error_message: str,
    cause: Exception,
    model: Optional[str] = None,
) -> None:
    observation = CallObservation(
        provider="deepseek",
        model=model or config.deepseek_model,
        latency_ms=_compute_latency_ms(started_at),
        usage=UsageMetrics(None, None, None),
        error_type=error_type,
        error_message=error_message,
    )
    raise DeepSeekCallError(error_message, observation) from cause


def _raise_stream_parse_error(
    default_model: str,
    error: _DeepSeekPayloadError,
) -> None:
    observation = CallObservation(
        provider="deepseek",
        model=error.model or default_model,
        latency_ms=0,
        usage=UsageMetrics(None, None, None),
        error_type=error.error_type,
        error_message=str(error),
    )
    raise DeepSeekCallError(str(error), observation) from error


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
