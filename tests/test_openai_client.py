import unittest

from agent_kb.openai_client import parse_response_stream_events


class OpenAIClientTest(unittest.TestCase):
    def test_parses_response_output_text_delta_events(self):
        lines = [
            b"event: response.output_text.delta\n",
            b"data: "
            + '{"type":"response.output_text.delta","delta":"你"}\n'.encode("utf-8"),
            b"\n",
            b"event: response.output_text.delta\n",
            b"data: "
            + '{"type":"response.output_text.delta","delta":"好"}\n'.encode("utf-8"),
            b"\n",
            b"event: response.completed\n",
            b'data: {"type":"response.completed"}\n',
            b"\n",
        ]

        chunks = list(parse_response_stream_events(lines))

        self.assertEqual(chunks, ["你", "好"])

    def test_raises_on_stream_error_event(self):
        lines = [
            b"event: error\n",
            b'data: {"type":"error","message":"bad request"}\n',
            b"\n",
        ]

        with self.assertRaisesRegex(RuntimeError, "bad request"):
            list(parse_response_stream_events(lines))


if __name__ == "__main__":
    unittest.main()
