import json
import unittest
from unittest.mock import patch

from agent_kb.config import AppConfig
from agent_kb.deepseek_client import (
    DeepSeekChatCompletionsModelClient,
    parse_deepseek_stream_events,
)


class FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return json.dumps(self._payload).encode("utf-8")


class DeepSeekClientTest(unittest.TestCase):
    def test_complete_posts_chat_completions_request_and_extracts_content(self):
        config = AppConfig.from_env(
            {
                "DEEPSEEK_API_KEY": "deepseek-key",
                "DEEPSEEK_BASE_URL": "https://deepseek.example",
                "DEEPSEEK_MODEL": "deepseek-test-model",
            }
        )
        captured = {}

        def fake_urlopen(request, timeout):
            captured["url"] = request.full_url
            captured["timeout"] = timeout
            captured["headers"] = dict(request.header_items())
            captured["body"] = json.loads(request.data.decode("utf-8"))
            return FakeResponse(
                {
                    "choices": [
                        {
                            "message": {
                                "content": "DeepSeek 真实响应",
                            }
                        }
                    ]
                }
            )

        with patch("agent_kb.deepseek_client.urllib.request.urlopen", fake_urlopen):
            response = DeepSeekChatCompletionsModelClient(config).complete("你好")

        self.assertEqual(response, "DeepSeek 真实响应")
        self.assertEqual(
            captured["url"], "https://deepseek.example/chat/completions"
        )
        self.assertEqual(captured["timeout"], 60)
        self.assertEqual(captured["body"]["model"], "deepseek-test-model")
        self.assertEqual(captured["body"]["messages"][-1], {"role": "user", "content": "你好"})
        self.assertFalse(captured["body"]["stream"])

    def test_parse_stream_events_reads_delta_content_until_done(self):
        lines = [
            'data: {"choices":[{"delta":{"content":"你"}}]}\n'.encode("utf-8"),
            b"\n",
            'data: {"choices":[{"delta":{"content":"好"}}]}\n'.encode("utf-8"),
            b"\n",
            b"data: [DONE]\n",
        ]

        chunks = list(parse_deepseek_stream_events(lines))

        self.assertEqual(chunks, ["你", "好"])

    def test_stream_posts_streaming_request(self):
        config = AppConfig.from_env({"DEEPSEEK_API_KEY": "deepseek-key"})
        captured = {}

        class StreamingResponse:
            def __enter__(self):
                return [
                    'data: {"choices":[{"delta":{"content":"流"}}]}\n'.encode(
                        "utf-8"
                    ),
                    b"data: [DONE]\n",
                ]

            def __exit__(self, exc_type, exc, traceback):
                return False

        def fake_urlopen(request, timeout):
            captured["body"] = json.loads(request.data.decode("utf-8"))
            return StreamingResponse()

        with patch("agent_kb.deepseek_client.urllib.request.urlopen", fake_urlopen):
            chunks = list(DeepSeekChatCompletionsModelClient(config).stream("流式"))

        self.assertEqual(chunks, ["流"])
        self.assertTrue(captured["body"]["stream"])

    def test_requires_api_key(self):
        config = AppConfig.from_env({})

        with self.assertRaisesRegex(ValueError, "DEEPSEEK_API_KEY"):
            DeepSeekChatCompletionsModelClient(config)


if __name__ == "__main__":
    unittest.main()
