import unittest

from agent_kb.call_observability import (
    CallObservation,
    UsageMetrics,
    format_observation_lines,
    format_tool_call_observation_lines,
)


class CallObservabilityTest(unittest.TestCase):
    def test_format_observation_lines_renders_usage_and_no_error_message(self):
        observation = CallObservation(
            provider="deepseek",
            model="deepseek-v4-flash",
            latency_ms=321,
            usage=UsageMetrics(input_tokens=11, output_tokens=7, total_tokens=18),
            error_type=None,
            error_message=None,
        )

        lines = format_observation_lines(observation)

        self.assertEqual(
            lines,
            [
                "provider=deepseek",
                "model=deepseek-v4-flash",
                "latency_ms=321",
                "input_tokens=11",
                "output_tokens=7",
                "total_tokens=18",
                "error_type=",
                "error_message=",
            ],
        )

    def test_format_observation_lines_renders_missing_usage_stably(self):
        observation = CallObservation(
            provider="deepseek",
            model="deepseek-v4-flash",
            latency_ms=321,
            usage=UsageMetrics(input_tokens=None, output_tokens=None, total_tokens=None),
            error_type=None,
            error_message=None,
        )

        lines = format_observation_lines(observation)

        self.assertEqual(
            lines,
            [
                "provider=deepseek",
                "model=deepseek-v4-flash",
                "latency_ms=321",
                "input_tokens=unknown",
                "output_tokens=unknown",
                "total_tokens=unknown",
                "error_type=",
                "error_message=",
            ],
        )

    def test_format_observation_lines_renders_error_type_and_error_message(self):
        observation = CallObservation(
            provider="deepseek",
            model="deepseek-v4-flash",
            latency_ms=321,
            usage=UsageMetrics(input_tokens=11, output_tokens=7, total_tokens=18),
            error_type="invalid_json",
            error_message="HTTP 429",
        )

        lines = format_observation_lines(observation)

        self.assertEqual(lines[-2], "error_type=invalid_json")
        self.assertEqual(lines[-1], "error_message=HTTP 429")

    def test_format_tool_call_observation_lines_renders_summary(self):
        lines = format_tool_call_observation_lines(
            {
                "tool_triggered": True,
                "tool_names": ["get_phase1_progress"],
                "success": True,
                "error_type": None,
                "error_message": None,
            }
        )

        self.assertEqual(
            lines,
            [
                "tool_triggered=true",
                "tool_names=get_phase1_progress",
                "success=true",
                "error_type=",
                "error_message=",
            ],
        )


if __name__ == "__main__":
    unittest.main()
