from dataclasses import dataclass
from typing import Optional, TypedDict


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


class ToolCallObservation(TypedDict):
    tool_triggered: bool
    tool_names: list[str]
    success: bool
    error_type: Optional[str]
    error_message: Optional[str]


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


def build_tool_call_observation(
    *,
    tool_triggered: bool,
    tool_names: list[str],
    success: bool,
    error_type: Optional[str] = None,
    error_message: Optional[str] = None,
) -> ToolCallObservation:
    return {
        "tool_triggered": tool_triggered,
        "tool_names": tool_names,
        "success": success,
        "error_type": error_type,
        "error_message": error_message,
    }
