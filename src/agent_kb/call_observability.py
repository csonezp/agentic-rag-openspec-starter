from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UsageMetrics:
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    total_tokens: Optional[int]


@dataclass(frozen=True)
class CallObservation:
    provider: str
    model: str
    latency_ms: int
    usage: UsageMetrics
    error_type: Optional[str] = None
    error_message: Optional[str] = None


def _render_metric(value: Optional[int]) -> str:
    if value is None:
        return "unknown"
    return str(value)


def format_observation_lines(observation: CallObservation) -> list[str]:
    return [
        f"provider={observation.provider}",
        f"model={observation.model}",
        f"latency_ms={observation.latency_ms}",
        f"input_tokens={_render_metric(observation.usage.input_tokens)}",
        f"output_tokens={_render_metric(observation.usage.output_tokens)}",
        f"total_tokens={_render_metric(observation.usage.total_tokens)}",
        f"error_type={observation.error_type or ''}",
        f"error_message={observation.error_message or ''}",
    ]
