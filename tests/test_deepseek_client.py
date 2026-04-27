import json
import unittest
from unittest.mock import patch

import agent_kb.deepseek_client as deepseek_client_module
from agent_kb.config import AppConfig
from agent_kb.deepseek_client import (
    DeepSeekChatCompletionsModelClient,
    extract_tool_calls,
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

    def test_complete_json_sets_response_format_and_max_tokens(self):
        config = AppConfig.from_env({"DEEPSEEK_API_KEY": "deepseek-key"})
        captured = {}

        def fake_urlopen(request, timeout):
            captured["body"] = json.loads(request.data.decode("utf-8"))
            return FakeResponse(
                {
                    "choices": [
                        {
                            "message": {
                                "content": '{"title":"标题","summary":"摘要","next_action":"下一步"}',
                            }
                        }
                    ]
                }
            )

        with patch("agent_kb.deepseek_client.urllib.request.urlopen", fake_urlopen):
            response = DeepSeekChatCompletionsModelClient(config).complete_json(
                "请输出 json", max_tokens=256
            )

        self.assertEqual(
            response, '{"title":"标题","summary":"摘要","next_action":"下一步"}'
        )
        self.assertEqual(captured["body"]["response_format"], {"type": "json_object"})
        self.assertEqual(captured["body"]["max_tokens"], 256)
        self.assertFalse(captured["body"]["stream"])

    def test_complete_with_observation_extracts_usage_model_and_latency(self):
        config = AppConfig.from_env({"DEEPSEEK_API_KEY": "deepseek-key"})

        def fake_urlopen(request, timeout):
            return FakeResponse(
                {
                    "model": "deepseek-observed-model",
                    "usage": {
                        "prompt_tokens": 8,
                        "completion_tokens": 5,
                        "total_tokens": 13,
                    },
                    "choices": [
                        {
                            "message": {
                                "content": "带观测的响应",
                            }
                        }
                    ],
                }
            )

        with patch("agent_kb.deepseek_client.urllib.request.urlopen", fake_urlopen):
            with patch.object(
                deepseek_client_module,
                "time",
                create=True,
            ) as fake_time:
                fake_time.monotonic.side_effect = [10.0, 10.321]
                result = DeepSeekChatCompletionsModelClient(
                    config
                ).complete_with_observation("你好")

        self.assertEqual(result.text, "带观测的响应")
        self.assertEqual(result.observation.provider, "deepseek")
        self.assertEqual(result.observation.model, "deepseek-observed-model")
        self.assertEqual(result.observation.latency_ms, 321)
        self.assertEqual(result.observation.usage.input_tokens, 8)
        self.assertEqual(result.observation.usage.output_tokens, 5)
        self.assertEqual(result.observation.usage.total_tokens, 13)
        self.assertIsNone(result.observation.error_message)

    def test_create_tool_call_request_sends_tools(self):
        config = AppConfig.from_env({"DEEPSEEK_API_KEY": "deepseek-key"})
        captured = {}
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_phase1_progress",
                    "description": "获取 Phase 1 学习进度。",
                    "parameters": {"type": "object", "properties": {}},
                },
            }
        ]

        def fake_urlopen(request, timeout):
            captured["body"] = json.loads(request.data.decode("utf-8"))
            return FakeResponse(
                {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "tool_calls": [
                                    {
                                        "id": "call_1",
                                        "type": "function",
                                        "function": {
                                            "name": "get_phase1_progress",
                                            "arguments": "{}",
                                        },
                                    }
                                ],
                            }
                        }
                    ]
                }
            )

        with patch("agent_kb.deepseek_client.urllib.request.urlopen", fake_urlopen):
            message = DeepSeekChatCompletionsModelClient(config).create_chat_completion(
                [{"role": "user", "content": "查询进度"}],
                tools=tools,
            )

        self.assertEqual(captured["body"]["tools"], tools)
        self.assertEqual(message["tool_calls"][0]["function"]["name"], "get_phase1_progress")

    def test_extract_tool_calls_reads_assistant_tool_calls(self):
        payload = {
            "choices": [
                {
                    "message": {
                        "tool_calls": [
                            {
                                "id": "call_1",
                                "type": "function",
                                "function": {
                                    "name": "get_phase1_progress",
                                    "arguments": "{}",
                                },
                            }
                        ]
                    }
                }
            ]
        }

        tool_calls = extract_tool_calls(payload)

        self.assertEqual(tool_calls[0]["id"], "call_1")
        self.assertEqual(tool_calls[0]["function"]["name"], "get_phase1_progress")

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

    def test_stream_with_observation_returns_chunks_and_usage_summary(self):
        config = AppConfig.from_env({"DEEPSEEK_API_KEY": "deepseek-key"})
        captured = {}

        class StreamingResponse:
            def __enter__(self):
                return [
                    (
                        'data: {"model":"deepseek-stream-model","choices":[{"delta":{"content":"流"}}]}\n'
                    ).encode("utf-8"),
                    (
                        'data: {"choices":[{"delta":{"content":"式"}}],"usage":{"prompt_tokens":3,"completion_tokens":2,"total_tokens":5}}\n'
                    ).encode("utf-8"),
                    b"data: [DONE]\n",
                ]

            def __exit__(self, exc_type, exc, traceback):
                return False

        def fake_urlopen(request, timeout):
            captured["body"] = json.loads(request.data.decode("utf-8"))
            return StreamingResponse()

        with patch("agent_kb.deepseek_client.urllib.request.urlopen", fake_urlopen):
            with patch.object(
                deepseek_client_module,
                "time",
                create=True,
            ) as fake_time:
                fake_time.monotonic.side_effect = [100.0, 100.045]
                result = DeepSeekChatCompletionsModelClient(
                    config
                ).stream_with_observation("流式")

        self.assertEqual(result.chunks, ["流", "式"])
        self.assertEqual(result.observation.provider, "deepseek")
        self.assertEqual(result.observation.model, "deepseek-stream-model")
        self.assertEqual(result.observation.latency_ms, 45)
        self.assertEqual(result.observation.usage.input_tokens, 3)
        self.assertEqual(result.observation.usage.output_tokens, 2)
        self.assertEqual(result.observation.usage.total_tokens, 5)
        self.assertIsNone(result.observation.error_message)
        self.assertTrue(captured["body"]["stream"])

    def test_requires_api_key(self):
        config = AppConfig.from_env({})

        with self.assertRaisesRegex(ValueError, "DEEPSEEK_API_KEY"):
            DeepSeekChatCompletionsModelClient(config)


if __name__ == "__main__":
    unittest.main()
