import unittest

from agent_kb.call_observability import (
    CallObservation,
    UsageMetrics,
    format_observation_lines,
)


class CallObservabilityTest(unittest.TestCase):
    def test_format_observation_lines_renders_usage_and_no_error_message(self):
        observation = CallObservation(
            provider="deepseek",
            model="deepseek-v4-flash",
            latency_ms=321,
            usage=UsageMetrics(input_tokens=11, output_tokens=7, total_tokens=18),
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
                "error_message=",
            ],
        )

    def test_format_observation_lines_renders_missing_usage_stably(self):
        observation = CallObservation(
            provider="deepseek",
            model="deepseek-v4-flash",
            latency_ms=321,
            usage=UsageMetrics(input_tokens=None, output_tokens=None, total_tokens=None),
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
                "error_message=",
            ],
        )

    def test_format_observation_lines_renders_error_message(self):
        observation = CallObservation(
            provider="deepseek",
            model="deepseek-v4-flash",
            latency_ms=321,
            usage=UsageMetrics(input_tokens=11, output_tokens=7, total_tokens=18),
            error_message="HTTP 429",
        )

        lines = format_observation_lines(observation)

        self.assertEqual(lines[-1], "error_message=HTTP 429")


if __name__ == "__main__":
    unittest.main()
